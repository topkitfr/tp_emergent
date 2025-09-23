import React, { useState, useEffect } from 'react';
import { X, Upload, AlertCircle } from 'lucide-react';

const MasterKitForm = ({ isOpen, onClose, onSuccess, API }) => {
  const [formData, setFormData] = useState({
    kit_type: '',
    club_id: '',
    kit_style: '',
    brand_id: '',
    primary_sponsor_id: '',
    secondary_sponsor_ids: [],
    season: '',
    front_photo: null,
    back_photo: null,
    other_photos: []
  });
  
  const [formOptions, setFormOptions] = useState({
    clubs: [],
    brands: [],
    sponsors: []  // Add sponsors array
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const [previewImages, setPreviewImages] = useState({
    front_photo: null,
    back_photo: null,
    other_photos: []
  });

  // Kit Type options with base prices
  const kitTypeOptions = [
    { value: 'replica', label: 'Replica (€90)', basePrice: 90 },
    { value: 'authentic', label: 'Authentic (€140)', basePrice: 140 }
  ];

  // Kit Style options
  const kitStyleOptions = [
    { value: 'home', label: 'Home' },
    { value: 'away', label: 'Away' },
    { value: 'third', label: 'Third' },
    { value: 'fourth', label: 'Fourth' },
    { value: 'goalkeeper', label: 'Goalkeeper' },
    { value: 'special', label: 'Special' }
  ];

  const resetForm = () => {
    setFormData({
      kit_type: '',
      club_id: '',
      kit_style: '',
      brand_id: '',
      primary_sponsor_id: '',
      secondary_sponsor_ids: [],
      season: '',
      front_photo: null,
      back_photo: null,
      other_photos: []
    });
    setErrors({});
    setPreviewImages({
      front_photo: null,
      back_photo: null,
      other_photos: []
    });
  };

  useEffect(() => {
    if (isOpen) {
      resetForm();
      loadFormData();
    }
  }, [isOpen]);

  const loadFormData = async () => {
    try {
      const [clubsRes, brandsRes] = await Promise.all([
        fetch(`${API}/api/form-data/clubs`),
        fetch(`${API}/api/form-data/brands`)
      ]);

      if (clubsRes.ok && brandsRes.ok) {
        const [clubs, brands] = await Promise.all([
          clubsRes.json(),
          brandsRes.json()
        ]);

        setFormOptions({ clubs, brands });
      }
    } catch (error) {
      console.error('Error loading form data:', error);
    }
  };

  const handleInputChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
    // Clear error when field is updated
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: null
      }));
    }
  };

  const handleMultiSelectChange = (key, value) => {
    setFormData(prev => {
      const currentValues = prev[key] || [];
      if (currentValues.includes(value)) {
        return {
          ...prev,
          [key]: currentValues.filter(v => v !== value)
        };
      } else {
        return {
          ...prev,
          [key]: [...currentValues, value]
        };
      }
    });
  };

  const handleFileChange = (key, files, isMultiple = false) => {
    if (isMultiple) {
      // Handle multiple files (other_photos)
      const fileArray = Array.from(files);
      if (formData.other_photos.length + fileArray.length > 3) {
        alert('Maximum 3 additional photos allowed');
        return;
      }
      
      setFormData(prev => ({
        ...prev,
        [key]: [...prev[key], ...fileArray]
      }));
      
      // Generate previews
      const newPreviews = fileArray.map(file => URL.createObjectURL(file));
      setPreviewImages(prev => ({
        ...prev,
        [key]: [...prev[key], ...newPreviews]
      }));
    } else {
      // Handle single file
      const file = files[0];
      if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          setErrors(prev => ({
            ...prev,
            [key]: 'Please select an image file'
          }));
          return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          setErrors(prev => ({
            ...prev,
            [key]: 'Image must be smaller than 10MB'
          }));
          return;
        }

        setFormData(prev => ({
          ...prev,
          [key]: file
        }));
        
        setPreviewImages(prev => ({
          ...prev,
          [key]: URL.createObjectURL(file)
        }));
      }
    }
    
    // Clear error
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: null
      }));
    }
  };

  const removeOtherPhoto = (index) => {
    setFormData(prev => ({
      ...prev,
      other_photos: prev.other_photos.filter((_, i) => i !== index)
    }));
    
    setPreviewImages(prev => ({
      ...prev,
      other_photos: prev.other_photos.filter((_, i) => i !== index)
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Required field validation
    if (!formData.kit_type) newErrors.kit_type = 'Kit Type is required';
    if (!formData.club_id) newErrors.club_id = 'Team/Club is required';
    if (!formData.kit_style) newErrors.kit_style = 'Kit Style is required';
    if (!formData.season) newErrors.season = 'Season/Year is required';
    if (!formData.front_photo) newErrors.front_photo = 'Front photo is required';
    if (!formData.back_photo) newErrors.back_photo = 'Back photo is required';

    // Season format validation (YYYY/YYYY)
    if (formData.season && !/^\d{4}\/\d{4}$/.test(formData.season)) {
      newErrors.season = 'Season must be in YYYY/YYYY format (e.g., 2023/2024)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please log in to create a Master Kit');
        return;
      }

      // Create FormData for file upload
      const submitData = new FormData();
      
      // Add form fields
      submitData.append('kit_type', formData.kit_type);
      submitData.append('club_id', formData.club_id);
      submitData.append('kit_style', formData.kit_style);
      submitData.append('season', formData.season);
      
      // Optional fields
      if (formData.brand_id) submitData.append('brand_id', formData.brand_id);
      if (formData.primary_sponsor_id) submitData.append('primary_sponsor_id', formData.primary_sponsor_id);
      if (formData.secondary_sponsor_ids.length > 0) {
        submitData.append('secondary_sponsor_ids', JSON.stringify(formData.secondary_sponsor_ids));
      }
      
      // Add photos
      submitData.append('front_photo', formData.front_photo);
      submitData.append('back_photo', formData.back_photo);
      
      // Add other photos
      formData.other_photos.forEach((photo, index) => {
        submitData.append(`other_photo_${index}`, photo);
      });

      const response = await fetch(`${API}/api/master-kits`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: submitData
      });

      if (response.ok) {
        const result = await response.json();
        alert('Master Kit created successfully!');
        resetForm();
        onSuccess && onSuccess(result);
        onClose();
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to create Master Kit'}`);
      }
    } catch (error) {
      console.error('Error creating Master Kit:', error);
      alert('Error creating Master Kit. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" style={{ zIndex: 10001 }}>
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">
            Create New Master Kit
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Kit Type (Required) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Kit Type *
            </label>
            <select
              value={formData.kit_type}
              onChange={(e) => handleInputChange('kit_type', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.kit_type ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Kit Type</option>
              {kitTypeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.kit_type && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.kit_type}
              </p>
            )}
          </div>

          {/* Team/Club (Required) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Team/Club *
            </label>
            <select
              value={formData.club_id}
              onChange={(e) => handleInputChange('club_id', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.club_id ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Team/Club</option>
              {formOptions.clubs.map(team => (
                <option key={team.id} value={team.id}>
                  {team.name} ({team.country})
                </option>
              ))}
            </select>
            {errors.club_id && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.club_id}
              </p>
            )}
          </div>

          {/* Kit Style (Required) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Kit Style *
            </label>
            <select
              value={formData.kit_style}
              onChange={(e) => handleInputChange('kit_style', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.kit_style ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Kit Style</option>
              {kitStyleOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.kit_style && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.kit_style}
              </p>
            )}
          </div>

          {/* Brand (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Brand
            </label>
            <select
              value={formData.brand_id}
              onChange={(e) => handleInputChange('brand_id', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Brand</option>
              {formOptions.brands.map(brand => (
                <option key={brand.id} value={brand.id}>
                  {brand.name} {brand.country && `(${brand.country})`}
                </option>
              ))}
            </select>
          </div>

          {/* Primary Sponsor (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Sponsor
            </label>
            <select
              value={formData.primary_sponsor_id}
              onChange={(e) => handleInputChange('primary_sponsor_id', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Primary Sponsor</option>
              {formOptions.brands.map(brand => (
                <option key={brand.id} value={brand.id}>
                  {brand.name} {brand.country && `(${brand.country})`}
                </option>
              ))}
            </select>
          </div>

          {/* Secondary Sponsor (Multiple Selection) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Secondary Sponsors (Multiple Selection)
            </label>
            <div className="border border-gray-300 rounded-lg p-3 max-h-40 overflow-y-auto">
              {formOptions.brands.map(brand => (
                <label key={brand.id} className="flex items-center mb-2">
                  <input
                    type="checkbox"
                    checked={formData.secondary_sponsor_ids.includes(brand.id)}
                    onChange={() => handleMultiSelectChange('secondary_sponsor_ids', brand.id)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mr-3"
                  />
                  <span className="text-sm text-gray-700">
                    {brand.name} {brand.country && `(${brand.country})`}
                  </span>
                </label>
              ))}
              {formOptions.brands.length === 0 && (
                <p className="text-gray-500 text-sm">No brands available</p>
              )}
            </div>
            {formData.secondary_sponsor_ids.length > 0 && (
              <p className="text-sm text-gray-600 mt-1">
                Selected: {formData.secondary_sponsor_ids.length} sponsors
              </p>
            )}
          </div>

          {/* Season/Year (Required) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Season/Year *
            </label>
            <input
              type="text"
              value={formData.season}
              onChange={(e) => handleInputChange('season', e.target.value)}
              placeholder="2023/2024"
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.season ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            <p className="text-xs text-gray-500 mt-1">Format: YYYY/YYYY (e.g., 2023/2024)</p>
            {errors.season && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.season}
              </p>
            )}
          </div>

          {/* Photos Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Photos</h3>
            
            {/* Front Photo (Required) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Front Photo *
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange('front_photo', e.target.files)}
                className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                  errors.front_photo ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {previewImages.front_photo && (
                <div className="mt-2">
                  <img
                    src={previewImages.front_photo}
                    alt="Front preview"
                    className="w-32 h-32 object-cover rounded-lg border"
                  />
                </div>
              )}
              {errors.front_photo && (
                <p className="text-red-500 text-sm mt-1 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  {errors.front_photo}
                </p>
              )}
            </div>

            {/* Back Photo (Required) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Back Photo *
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange('back_photo', e.target.files)}
                className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                  errors.back_photo ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {previewImages.back_photo && (
                <div className="mt-2">
                  <img
                    src={previewImages.back_photo}
                    alt="Back preview"
                    className="w-32 h-32 object-cover rounded-lg border"
                  />
                </div>
              )}
              {errors.back_photo && (
                <p className="text-red-500 text-sm mt-1 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  {errors.back_photo}
                </p>
              )}
            </div>

            {/* Other Photos (Max 3) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Other Photos (Max 3)
              </label>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={(e) => handleFileChange('other_photos', e.target.files, true)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
              {previewImages.other_photos.length > 0 && (
                <div className="mt-2 grid grid-cols-3 gap-2">
                  {previewImages.other_photos.map((preview, index) => (
                    <div key={index} className="relative">
                      <img
                        src={preview}
                        alt={`Other preview ${index + 1}`}
                        className="w-full h-24 object-cover rounded-lg border"
                      />
                      <button
                        type="button"
                        onClick={() => removeOtherPhoto(index)}
                        className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
              <p className="text-xs text-gray-500 mt-1">
                {formData.other_photos.length}/3 photos added
              </p>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Creating...' : 'Create Master Kit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MasterKitForm;