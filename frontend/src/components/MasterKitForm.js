import React, { useState, useEffect } from 'react';
import { X, Upload, AlertCircle } from 'lucide-react';

const MasterKitForm = ({ isOpen, onClose, onSuccess, API }) => {
  const [formData, setFormData] = useState({
    club: '',
    season: '',
    kit_type: '',
    competition: '',
    model: '',
    brand: '',
    gender: '',
    primary_color: '',
    secondary_colors: [],
    pattern_description: '',
    main_sponsor: ''
  });
  
  const [frontPhoto, setFrontPhoto] = useState(null);
  const [frontPhotoPreview, setFrontPhotoPreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      resetForm();
    }
  }, [isOpen]);

  const resetForm = () => {
    setFormData({
      club: '',
      season: '',
      kit_type: '',
      competition: '',
      model: '',
      brand: '',
      gender: '',
      primary_color: '',
      secondary_colors: [],
      pattern_description: '',
      main_sponsor: ''
    });
    setFrontPhoto(null);
    setFrontPhotoPreview(null);
    setErrors({});
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
    const newColor = document.getElementById('new-secondary-color').value.trim();
    if (newColor && !formData.secondary_colors.includes(newColor)) {
      handleInputChange('secondary_colors', [...formData.secondary_colors, newColor]);
      document.getElementById('new-secondary-color').value = '';
    }
  };

  const removeSecondaryColor = (colorToRemove) => {
    handleInputChange('secondary_colors', formData.secondary_colors.filter(color => color !== colorToRemove));
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Required fields validation
    const requiredFields = [
      { key: 'club', label: 'Club' },
      { key: 'season', label: 'Season' },
      { key: 'kit_type', label: 'Type' },
      { key: 'competition', label: 'Competition' },
      { key: 'model', label: 'Model' },
      { key: 'brand', label: 'Brand' },
      { key: 'gender', label: 'Gender' }
    ];

    requiredFields.forEach(({ key, label }) => {
      if (!formData[key] || formData[key].trim() === '') {
        newErrors[key] = `${label} is required`;
      }
    });

    // Front photo is required
    if (!frontPhoto) {
      newErrors.front_photo = 'Front photo is required (minimum 800x600px)';
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

      // Create Master Kit
      const masterKitData = {
        ...formData,
        front_photo_url: frontPhotoUrl
      };

      const response = await fetch(`${API}/api/master-kits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(masterKitData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create Master Kit');
      }

      const createdMasterKit = await response.json();
      
      alert('Master Kit created successfully!');
      onSuccess && onSuccess(createdMasterKit);
      onClose();

    } catch (error) {
      console.error('Error creating Master Kit:', error);
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
            Create New Master Kit
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
                  All fields marked with * are required.
                </p>
              </div>
            </div>
          </div>

          {/* Club Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Club <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.club}
              onChange={(e) => handleInputChange('club', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.club ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., PSG, Manchester United, AC Milan"
            />
            {errors.club && <p className="text-red-500 text-xs mt-1">{errors.club}</p>}
          </div>

          {/* Season Field */}
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
              placeholder="e.g., 2024/2025, 2023-24"
            />
            {errors.season && <p className="text-red-500 text-xs mt-1">{errors.season}</p>}
          </div>

          {/* Type Field */}
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
              <option value="training">Training</option>
            </select>
            {errors.kit_type && <p className="text-red-500 text-xs mt-1">{errors.kit_type}</p>}
          </div>

          {/* Competition Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Competition <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.competition}
              onChange={(e) => handleInputChange('competition', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.competition ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., Ligue 1, Champions League, Premier League"
            />
            {errors.competition && <p className="text-red-500 text-xs mt-1">{errors.competition}</p>}
          </div>

          {/* Model Field */}
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
              <option value="player_issue">Player Issue</option>
            </select>
            {errors.model && <p className="text-red-500 text-xs mt-1">{errors.model}</p>}
          </div>

          {/* Brand Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Brand <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.brand}
              onChange={(e) => handleInputChange('brand', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                errors.brand ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., Nike, Adidas, Puma"
            />
            {errors.brand && <p className="text-red-500 text-xs mt-1">{errors.brand}</p>}
          </div>

          {/* Gender Field */}
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
              <option value="men">Men</option>
              <option value="women">Women</option>
              <option value="youth">Youth</option>
              <option value="unisex">Unisex</option>
            </select>
            {errors.gender && <p className="text-red-500 text-xs mt-1">{errors.gender}</p>}
          </div>

          {/* Front Photo Upload */}
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

          {/* Optional Fields Section */}
          <div className="border-t pt-4">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Optional Details</h3>
            
            {/* Primary Color */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary Color
              </label>
              <input
                type="text"
                value={formData.primary_color}
                onChange={(e) => handleInputChange('primary_color', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Navy Blue, Red, White"
              />
            </div>

            {/* Secondary Colors */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Secondary Colors
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
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
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  id="new-secondary-color"
                  type="text"
                  placeholder="Add secondary color"
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
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
                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
            </div>

            {/* Pattern Description */}
            <div className="mb-4">
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

            {/* Main Sponsor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Main Sponsor
              </label>
              <input
                type="text"
                value={formData.main_sponsor}
                onChange={(e) => handleInputChange('main_sponsor', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Qatar Airways, Emirates, Jeep"
              />
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