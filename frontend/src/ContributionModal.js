import React, { useState, useEffect } from 'react';
import { getUnifiedFieldsForEntityType } from './components/UnifiedFieldDefinitions';
import UnifiedFieldRenderer from './components/UnifiedFieldRenderer';

const ContributionModal = ({ 
  isOpen, 
  onClose, 
  entity, 
  entityType, 
  onContributionCreated,
  teams = [],
  brands = [],
  competitions = [],
  masterKits = [],
  referenceKits = [],
  players = []
}) => {
  const [formData, setFormData] = useState({});
  const [originalData, setOriginalData] = useState({});
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [sourceUrls, setSourceUrls] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [changes, setChanges] = useState([]);
  
  // Image management states
  const [imageFiles, setImageFiles] = useState({
    logo: null,
    primary_photo: null,
    secondary_photos: []
  });
  const [imagePreviews, setImagePreviews] = useState({
    logo: '',
    primary_photo: '',
    secondary_photos: []
  });
  
  // State for new field types
  const [newColor, setNewColor] = useState('');
  const [newName, setNewName] = useState('');

  const API = process.env.REACT_APP_BACKEND_URL;

  // Initialize form data when entity or entityType changes
  useEffect(() => {
    if (isOpen && entity && entityType) {
      const fields = getUnifiedFieldsForEntityType(entityType);
      const initialFormData = {};
      
      // Initialize form data based on entity data and field types
      fields.forEach(field => {
        if (field.type === 'color_list' || field.type === 'name_list') {
          // Initialize array fields as arrays
          initialFormData[field.key] = entity[field.key] || [];
        } else {
          // Initialize other fields normally
          initialFormData[field.key] = entity[field.key] || '';
        }
      });
      
      setOriginalData(initialFormData);
      setFormData(initialFormData);
      setDescription('');
      setSourceUrls(['']);
      setChanges([]);
      setNewColor('');
      setNewName('');
      
      // Reset image states
      setImageFiles({
        logo: null,
        primary_photo: null,
        secondary_photos: []
      });
      setImagePreviews({
        logo: '',
        primary_photo: '',
        secondary_photos: []
      });
    }
  }, [isOpen, entity, entityType]);

  // Detect changes between original and current form data
  useEffect(() => {
    if (Object.keys(originalData).length > 0) {
      const detectedChanges = [];
      
      Object.keys(formData).forEach(key => {
        if (formData[key] !== originalData[key] && formData[key] !== '') {
          detectedChanges.push({
            field: key,
            from: originalData[key] || 'Not set',
            to: formData[key],
            type: originalData[key] ? 'update' : 'add'
          });
        }
      });
      
      // Check for new images
      if (imageFiles.logo) {
        detectedChanges.push({
          field: 'logo',
          from: 'Current photo',
          to: 'New photo',
          type: 'update'
        });
      }
      
      if (imageFiles.primary_photo) {
        detectedChanges.push({
          field: 'primary_photo',
          from: 'Current photo',
          to: 'New photo',
          type: 'update'
        });
      }
      
      if (imageFiles.secondary_photos.length > 0) {
        detectedChanges.push({
          field: 'secondary_photos',
          from: 'Current photos',
          to: `${imageFiles.secondary_photos.length} new photo(s)`,
          type: 'add'
        });
      }
      
      setChanges(detectedChanges);
      
      // Generate automatic title if no custom title
      if (detectedChanges.length > 0 && !title) {
        if (detectedChanges.length === 1) {
          const change = detectedChanges[0];
          const actionText = change.type === 'add' ? 'Addition' : 'Update';
          setTitle(`${actionText} ${getFieldDisplayName(change.field)} - ${entity.name}`);
        } else {
          setTitle(`Profile improvement - ${entity.name}`);
        }
      }
    }
  }, [formData, originalData, imageFiles, entity, title]);

  // Image management functions
  const handleImageUpload = (imageType, file) => {
    if (!file) return;
    
    // Check file type
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file');
      return;
    }
    
    // Check size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must not exceed 5MB');
      return;
    }
    
    // Update files
    setImageFiles(prev => ({
      ...prev,
      [imageType]: imageType === 'secondary_photos' 
        ? [...prev.secondary_photos, file]
        : file
    }));
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreviews(prev => ({
        ...prev,
        [imageType]: imageType === 'secondary_photos'
          ? [...prev.secondary_photos, e.target.result]
          : e.target.result
      }));
    };
    reader.readAsDataURL(file);
  };

  const removeSecondaryPhoto = (index) => {
    setImageFiles(prev => ({
      ...prev,
      secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
    }));
    setImagePreviews(prev => ({
      ...prev,
      secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
    }));
  };

  const convertFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const getFieldDisplayName = (field) => {
    const fieldNames = {
      name: 'name',
      short_name: 'short name',
      city: 'city',
      country: 'country',
      founded_year: 'founding year',
      colors: 'colors',
      logo_url: 'logo',
      logo: 'logo',
      primary_photo: 'main photo',
      secondary_photos: 'additional photos',
      official_name: 'official name',
      competition_type: 'competition type',
      level: 'level',
      website: 'website'
    };
    return fieldNames[field] || field;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title.trim() || !description.trim()) {
      alert('Please provide a title and description for your contribution');
      return;
    }

    if (changes.length === 0 && Object.values(imageFiles).every(f => !f || (Array.isArray(f) && f.length === 0))) {
      alert('No changes detected. Please modify at least one field or add an image.');
      return;
    }

    setLoading(true);

    try {
      // Prepare only the changed fields for contribution data
      const changedFieldsData = {};
      
      // Only include fields that actually changed
      changes.forEach(change => {
        if (change.field && formData[change.field] !== undefined) {
          changedFieldsData[change.field] = formData[change.field];
        }
      });
      
      // Handle image changes specially since they're tracked differently
      if (imageFiles.logo) {
        // Map logo upload to correct field based on entity type
        if (entityType === 'master_kit') {
          changedFieldsData.front_photo_url = `image_uploaded_${Date.now()}`;
        } else {
          changedFieldsData.logo_url = `image_uploaded_${Date.now()}`;
        }
      }
      if (imageFiles.primary_photo) {
        changedFieldsData.primary_photo_url = `image_uploaded_${Date.now()}`;
      }
      if (imageFiles.secondary_photos.length > 0) {
        changedFieldsData.secondary_photos = `${imageFiles.secondary_photos.length} new photos`;
      }
      
      console.log('Changed fields only:', changedFieldsData);
      console.log('All detected changes:', changes);

      // Prepare contribution data with only changed fields
      const contributionData = {
        title: title.trim(),
        description: description.trim(),
        entity_type: entityType,
        entity_id: entity.id, // Include the entity ID for updates
        data: changedFieldsData, // Send only changed fields instead of all formData
        source_urls: sourceUrls.filter(url => url.trim() !== '')
      };

      console.log('Submitting contribution:', contributionData);

      // Submit contribution
      const response = await fetch(`${API}/api/contributions-v2/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(contributionData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Contribution submitted successfully:', result);
        
        // Upload images if any exist
        const allImages = [];
        if (imageFiles.logo) allImages.push({ file: imageFiles.logo, fieldKey: 'logo' });
        if (imageFiles.primary_photo) allImages.push({ file: imageFiles.primary_photo, fieldKey: 'primary_photo' });
        if (imageFiles.secondary_photos.length > 0) {
          imageFiles.secondary_photos.forEach((file, index) => {
            allImages.push({ file, fieldKey: `secondary_photo_${index}` });
          });
        }

        // Upload images if any
        if (allImages.length > 0) {
          for (let i = 0; i < allImages.length; i++) {
            const { file, fieldKey } = allImages[i];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('is_primary', i === 0 ? 'true' : 'false');
            formData.append('caption', fieldKey || '');

            const imageResponse = await fetch(
              `${API}/api/contributions-v2/${result.id}/images`,
              {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
              }
            );

            if (!imageResponse.ok) {
              console.warn(`Failed to upload image ${i + 1}`);
            }
          }
        }
        
        alert('Contribution submitted successfully! It will be reviewed by the community.');
        
        if (onContributionCreated) {
          onContributionCreated(result);
        }
        
        onClose();
      } else {
        const errorData = await response.json();
        console.error('Contribution submission error:', errorData);
        alert(`Error: ${errorData.detail || 'Failed to submit contribution'}`);
      }
    } catch (error) {
      console.error('Error submitting contribution:', error);
      alert('Error submitting contribution. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const fields = getUnifiedFieldsForEntityType(entityType);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            Improve {entityType === 'master_jersey' ? 'Kit' : entityType.charAt(0).toUpperCase() + entityType.slice(1)} Profile
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Entity Information */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Current {entityType === 'master_jersey' ? 'Kit' : entityType.charAt(0).toUpperCase() + entityType.slice(1)}</h3>
            <p className="text-blue-800">{entity.name}</p>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fields.map((field) => (
              <div key={field.key} className="space-y-1">
                <UnifiedFieldRenderer
                  field={field}
                  value={formData[field.key]}
                  onChange={(key, value) => setFormData(prev => ({ ...prev, [key]: value }))}
                  teams={teams}
                  brands={brands}
                  competitions={competitions}
                  masterKits={masterKits}
                  referenceKits={referenceKits}
                  players={players}
                  onImageUpload={(event, fieldKey) => {
                    // Handle image upload for edit forms
                    const files = Array.from(event.target.files);
                    if (files.length > 0) {
                      setFormData(prev => ({ ...prev, [fieldKey]: `image_uploaded_${Date.now()}` }));
                    }
                  }}
                  API={API}
                  formData={formData}
                />
              </div>
            ))}
          </div>

          {/* Image Upload Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Images</h3>
            
            {/* Main Photo Upload */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                {entityType === 'master_jersey' ? 'Photo principale (face uniquement)' : 'Logo/Main Photo'}
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImageUpload('logo', e.target.files[0])}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
              {imagePreviews.logo && (
                <div className="mt-2">
                  <img src={imagePreviews.logo} alt="Logo preview" className="w-24 h-24 object-cover rounded-lg border" />
                </div>
              )}
              {entityType === 'master_jersey' && (
                <p className="text-xs text-gray-500 mt-1">
                  Image de face du maillot uniquement. Les photos secondaires ne sont pas autorisées pour les Master Kits.
                </p>
              )}
            </div>

            {/* Secondary Photos Upload - Only for non-master jersey entities */}
            {entityType !== 'master_jersey' && (
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Additional Photos</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => {
                    Array.from(e.target.files).forEach(file => {
                      handleImageUpload('secondary_photos', file);
                    });
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                {imagePreviews.secondary_photos.length > 0 && (
                  <div className="mt-2 grid grid-cols-4 gap-2">
                    {imagePreviews.secondary_photos.map((preview, index) => (
                      <div key={index} className="relative">
                        <img src={preview} alt={`Preview ${index + 1}`} className="w-full h-16 object-cover rounded-lg border" />
                        <button
                          type="button"
                          onClick={() => removeSecondaryPhoto(index)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Contribution Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Contribution Details</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                placeholder="Brief title for your contribution"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows="3"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                placeholder="Describe the changes you're making and why"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Source URLs</label>
              {sourceUrls.map((url, index) => (
                <div key={index} className="flex space-x-2 mb-2">
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => {
                      const newUrls = [...sourceUrls];
                      newUrls[index] = e.target.value;
                      setSourceUrls(newUrls);
                    }}
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="https://..."
                  />
                  {index === sourceUrls.length - 1 && (
                    <button
                      type="button"
                      onClick={() => setSourceUrls([...sourceUrls, ''])}
                      className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700"
                    >
                      +
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Changes Summary */}
          {changes.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">Detected Changes ({changes.length})</h4>
              <ul className="space-y-1 text-sm text-green-800">
                {changes.map((change, index) => (
                  <li key={index}>
                    <span className="font-medium">{getFieldDisplayName(change.field)}:</span> {change.from} → {change.to}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || changes.length === 0}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit Contribution'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContributionModal;