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
    brands: []
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

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      resetForm();
      loadFormData();
    }
  }, [isOpen]);

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
    
    // Clear error when user starts typing
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: null
      }));
    }
  };

  const handlePhotoUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setErrors(prev => ({
        ...prev,
        front_photo: 'Please select an image file'
      }));
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setErrors(prev => ({
        ...prev,
        front_photo: 'Image must be smaller than 10MB'
      }));
      return;
    }

    // Create image to check dimensions
    const img = new Image();
    img.onload = () => {
      // Check minimum dimensions (800x600px as specified)
      if (img.width < 800 || img.height < 600) {
        setErrors(prev => ({
          ...prev,
          front_photo: `Image must be at least 800x600px. Your image is ${img.width}x${img.height}px`
        }));
        return;
      }

      // All validations passed
      setFrontPhoto(file);
      setFrontPhotoPreview(URL.createObjectURL(file));
      setErrors(prev => ({
        ...prev,
        front_photo: null
      }));
    };

    img.onerror = () => {
      setErrors(prev => ({
        ...prev,
        front_photo: 'Invalid image file'
      }));
    };

    img.src = URL.createObjectURL(file);
  };

  const addSecondaryColor = () => {
    if (newSecondaryColor.trim() && !formData.secondary_colors.includes(newSecondaryColor.trim())) {
      handleInputChange('secondary_colors', [...formData.secondary_colors, newSecondaryColor.trim()]);
      setNewSecondaryColor('');
    }
  };

  const removeSecondaryColor = (colorToRemove) => {
    handleInputChange('secondary_colors', formData.secondary_colors.filter(color => color !== colorToRemove));
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Required fields validation (fields with asterisk)
    const requiredFields = [
      { key: 'club_id', label: 'Club' },
      { key: 'season', label: 'Season' },
      { key: 'kit_type', label: 'Type' },
      { key: 'competition_id', label: 'Competition' },
      { key: 'model', label: 'Model' },
      { key: 'brand_id', label: 'Brand' },
      { key: 'gender', label: 'Gender' },
      { key: 'primary_color', label: 'Primary Color' }
    ];

    requiredFields.forEach(({ key, label }) => {
      if (!formData[key] || formData[key].trim() === '') {
        newErrors[key] = `${label} is required *`;
      }
    });

    // Season format validation (YEAR-YEAR)
    if (formData.season && !/^\d{4}-\d{4}$/.test(formData.season)) {
      newErrors.season = 'Season must be in YEAR-YEAR format (e.g., 2024-2025)';
    }

    // Front photo is required
    if (!frontPhoto) {
      newErrors.front_photo = 'Front photo is required * (minimum 800x600px)';
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
      // First upload the photo
      let frontPhotoUrl = null;
      if (frontPhoto) {
        const photoFormData = new FormData();
        photoFormData.append('file', frontPhoto);

        const photoResponse = await fetch(`${API}/api/upload/master-kit-photo`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: photoFormData
        });

        if (!photoResponse.ok) {
          const errorData = await photoResponse.json();
          throw new Error(errorData.detail || 'Failed to upload photo');
        }

        const photoResult = await photoResponse.json();
        frontPhotoUrl = photoResult.file_url;
      }

      // Prepare Master Kit data
      const masterKitData = {
        ...formData,
        front_photo_url: frontPhotoUrl
      };

      // Get club name from loaded clubs data
      const selectedClub = formOptions.clubs.find(club => club.id === formData.club_id);
      const clubName = selectedClub ? selectedClub.name : 'Unknown Club';

      // Create Master Kit Contribution (instead of direct master kit)
      const contributionData = {
        entity_type: "master_kit",
        title: `${clubName} ${formData.season} ${formData.kit_type} Kit`,
        description: `Master kit contribution for ${clubName} ${formData.season} ${formData.kit_type} jersey${formData.pattern_description ? ` - ${formData.pattern_description}` : ''}`,
        data: {
          ...masterKitData
        },
        source_urls: []
      };

      const response = await fetch(`${API}/api/contributions-v2/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(contributionData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create Master Kit contribution');
      }

      const createdContribution = await response.json();
      
      // Success! The contribution was created and is pending approval
      alert('Master Kit contribution created successfully! Your submission is pending approval. Once approved, it will appear in the Kit Area.');
      onSuccess && onSuccess(createdContribution);
      onClose();

    } catch (error) {
      console.error('Error creating Master Kit contribution:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">
            Add a Kit
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isSubmitting}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Important Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900">Master Kit = Official Jersey Reference</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Create once per jersey design. Contains standard info shared by all users.
                  Fields marked with * are required.
                </p>
              </div>
            </div>
          </div>

          {/* Club Field - Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Club <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.club_id}
              onChange={(e) => handleInputChange('club_id', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.club_id ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Club</option>
              {formOptions.clubs.map(club => (
                <option key={club.id} value={club.id}>
                  {club.name} ({club.country})
                </option>
              ))}
            </select>
            {errors.club_id && <p className="text-red-500 text-xs mt-1">{errors.club_id}</p>}
          </div>

          {/* Season Field - YEAR-YEAR format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Season <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.season}
              onChange={(e) => handleInputChange('season', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.season ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="2024-2025"
              pattern="\d{4}-\d{4}"
            />
            <p className="text-xs text-gray-500 mt-1">Format: YEAR-YEAR (e.g., 2024-2025)</p>
            {errors.season && <p className="text-red-500 text-xs mt-1">{errors.season}</p>}
          </div>

          {/* Type Field - Updated options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.kit_type}
              onChange={(e) => handleInputChange('kit_type', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.kit_type ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Type</option>
              <option value="home">Home</option>
              <option value="away">Away</option>
              <option value="third">Third</option>
              <option value="fourth">Fourth</option>
              <option value="gk">GK</option>
              <option value="special">Special</option>
            </select>
            {errors.kit_type && <p className="text-red-500 text-xs mt-1">{errors.kit_type}</p>}
          </div>

          {/* Competition Field - Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Competition <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.competition_id}
              onChange={(e) => handleInputChange('competition_id', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.competition_id ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Competition</option>
              {formOptions.competitions.map(comp => (
                <option key={comp.id} value={comp.id}>
                  {comp.name} ({comp.country})
                </option>
              ))}
            </select>
            {errors.competition_id && <p className="text-red-500 text-xs mt-1">{errors.competition_id}</p>}
          </div>

          {/* Model Field - Updated options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Model <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.model}
              onChange={(e) => handleInputChange('model', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.model ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Model</option>
              <option value="authentic">Authentic</option>
              <option value="replica">Replica</option>
            </select>
            {errors.model && <p className="text-red-500 text-xs mt-1">{errors.model}</p>}
          </div>

          {/* Brand Field - Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Brand <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.brand_id}
              onChange={(e) => handleInputChange('brand_id', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.brand_id ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Brand</option>
              {formOptions.brands.map(brand => (
                <option key={brand.id} value={brand.id}>
                  {brand.name} ({brand.country})
                </option>
              ))}
            </select>
            {errors.brand_id && <p className="text-red-500 text-xs mt-1">{errors.brand_id}</p>}
          </div>

          {/* SKU Code Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              SKU Code
            </label>
            <input
              type="text"
              value={formData.sku_code}
              onChange={(e) => handleInputChange('sku_code', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., NI-PSG-HOME-24-25"
            />
            <p className="text-xs text-gray-500 mt-1">Product SKU or catalog code (optional)</p>
          </div>

          {/* Main Sponsor Field - Dropdown (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Main Sponsor
            </label>
            <select
              value={formData.main_sponsor_id}
              onChange={(e) => handleInputChange('main_sponsor_id', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">No Sponsor</option>
              {formOptions.brands.map(brand => (
                <option key={brand.id} value={brand.id}>
                  {brand.name} ({brand.country})
                </option>
              ))}
            </select>
          </div>

          {/* Gender Field - Updated options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Gender <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.gender}
              onChange={(e) => handleInputChange('gender', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.gender ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select Gender</option>
              <option value="man">Man</option>
              <option value="woman">Woman</option>
              <option value="child">Child</option>
            </select>
            {errors.gender && <p className="text-red-500 text-xs mt-1">{errors.gender}</p>}
          </div>

          {/* Colors Section - Primary and Secondary on the same line */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Primary Color Field - Required */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary Color <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.primary_color}
                onChange={(e) => handleInputChange('primary_color', e.target.value)}
                className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                  errors.primary_color ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="e.g., Navy Blue, Red, White"
              />
              {errors.primary_color && <p className="text-red-500 text-xs mt-1">{errors.primary_color}</p>}
            </div>

            {/* Secondary Colors with + button */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Secondary Colors
              </label>
              <div className="flex flex-wrap gap-1 mb-2 min-h-[24px]">
                {formData.secondary_colors.map((color, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {color}
                    <button
                      type="button"
                      onClick={() => removeSecondaryColor(color)}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newSecondaryColor}
                  onChange={(e) => setNewSecondaryColor(e.target.value)}
                  placeholder="Add secondary color"
                  className="flex-1 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addSecondaryColor();
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={addSecondaryColor}
                  className="px-2 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
                >
                  <Plus className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>

          {/* Front Photo Upload - Required */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Front Photo <span className="text-red-500">*</span>
              <span className="text-xs text-gray-500 ml-2">(minimum 800x600px)</span>
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
              {frontPhotoPreview ? (
                <div className="text-center">
                  <img
                    src={frontPhotoPreview}
                    alt="Front photo preview"
                    className="mx-auto max-h-32 rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setFrontPhoto(null);
                      setFrontPhotoPreview(null);
                    }}
                    className="mt-2 text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove Photo
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-2">
                    <label htmlFor="front-photo" className="cursor-pointer">
                      <span className="mt-2 block text-sm font-medium text-gray-900">
                        Upload front photo
                      </span>
                      <span className="mt-1 block text-xs text-gray-500">
                        PNG, JPG, GIF up to 10MB. Minimum 800x600px required.
                      </span>
                    </label>
                    <input
                      id="front-photo"
                      type="file"
                      accept="image/*"
                      onChange={handlePhotoUpload}
                      className="hidden"
                    />
                  </div>
                </div>
              )}
            </div>
            {errors.front_photo && <p className="text-red-500 text-xs mt-1">{errors.front_photo}</p>}
          </div>

          {/* Pattern Description - Optional */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pattern Description
            </label>
            <textarea
              value={formData.pattern_description}
              onChange={(e) => handleInputChange('pattern_description', e.target.value)}
              rows="2"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="Describe any patterns, designs, or special elements"
            />
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
              {isSubmitting ? 'Creating...' : 'Add Kit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MasterKitForm;