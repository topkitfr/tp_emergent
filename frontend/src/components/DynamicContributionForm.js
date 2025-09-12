import React, { useState, useEffect } from 'react';
import { X, Upload, ThumbsUp, ThumbsDown, Image as ImageIcon } from 'lucide-react';
import { getUnifiedFieldsForEntityType, validateEntityData } from './UnifiedFieldDefinitions';
import UnifiedFieldRenderer from './UnifiedFieldRenderer';

const DynamicContributionForm = ({ 
  isOpen, 
  onClose, 
  selectedType = null, 
  teams = [], 
  brands = [], 
  competitions = [], 
  masterJerseys = [], 
  referenceKits = [], 
  players = [], 
  API 
}) => {
  const [contributionType, setContributionType] = useState(() => {
    // Ensure we don't default to removed entity types
    const validTypes = ['team', 'brand', 'player', 'competition'];
    return validTypes.includes(selectedType) ? selectedType : 'team';
  });
  const [formData, setFormData] = useState({});
  const [images, setImages] = useState([]);
  const [sourceUrls, setSourceUrls] = useState(['']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [previewImages, setPreviewImages] = useState([]);

  // Dynamic form configuration based on entity type (Unified version)
  const getFieldsForEntityType = (type) => {
    return getUnifiedFieldsForEntityType(type);
  };

  const requiresImages = (type) => {
    return ['master_kit', 'reference_kit'].includes(type);
  };

  const resetForm = () => {
    setFormData({});
    setImages([]);
    setPreviewImages([]);
    setSourceUrls(['']);
  };

  useEffect(() => {
    if (selectedType) {
      setContributionType(selectedType);
    }
    resetForm();
  }, [selectedType, isOpen]);

  const handleTypeChange = (type) => {
    setContributionType(type);
    resetForm();
  };

  const handleInputChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleImageUpload = async (event, fieldKey) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    const newPreviews = [];
    const newImages = [];

    for (const file of files) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        alert('File size must be less than 5MB');
        continue;
      }

      const preview = URL.createObjectURL(file);
      newPreviews.push({ file, preview, fieldKey });
      newImages.push({ file, fieldKey });
    }

    setPreviewImages(prev => [...prev, ...newPreviews]);
    setImages(prev => [...prev, ...newImages]);
    
    // Also update formData to indicate that this required image field has a value
    // This ensures validation passes for required image fields
    if (fieldKey) {
      setFormData(prev => ({
        ...prev,
        [fieldKey]: `image_uploaded_${Date.now()}` // Placeholder value to satisfy validation
      }));
    }
  };

  const removeImage = (index) => {
    const removedImage = previewImages[index];
    setPreviewImages(prev => prev.filter((_, i) => i !== index));
    setImages(prev => prev.filter((_, i) => i !== index));
    
    // If we removed an image, check if there are still images for this field
    // If not, remove the placeholder value from formData
    if (removedImage && removedImage.fieldKey) {
      const remainingImagesForField = images.filter((img, i) => i !== index && img.fieldKey === removedImage.fieldKey);
      if (remainingImagesForField.length === 0) {
        setFormData(prev => {
          const newFormData = { ...prev };
          delete newFormData[removedImage.fieldKey];
          return newFormData;
        });
      }
    }
  };

  const handleSourceUrlChange = (index, value) => {
    const newUrls = [...sourceUrls];
    newUrls[index] = value;
    setSourceUrls(newUrls);
  };

  const addSourceUrl = () => {
    setSourceUrls([...sourceUrls, '']);
  };

  const removeSourceUrl = (index) => {
    setSourceUrls(sourceUrls.filter((_, i) => i !== index));
  };

  const validateForm = () => {
    const errors = validateEntityData(contributionType, formData);
    
    if (errors.length > 0) {
      return errors[0]; // Return first error
    }

    if (requiresImages(contributionType) && images.length === 0) {
      return 'At least one image is required for this entity type';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      alert(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      // Generate title automatically based on entity data
      const generateTitle = () => {
        switch (contributionType) {
          case 'team':
            return `New Team: ${formData.name || 'Unnamed Team'}`;
          case 'brand':
            return `New Brand: ${formData.name || 'Unnamed Brand'}`;
          case 'player':
            return `New Player: ${formData.name || 'Unnamed Player'}`;
          case 'competition':
            return `New Competition: ${formData.competition_name || formData.name || 'Unnamed Competition'}`;
          case 'master_kit':
            return `New Master Kit: ${formData.season || 'Unknown Season'} ${formData.jersey_type || 'Kit'}`;
          case 'reference_kit':
            return `New Reference Kit: ${formData.model_name || 'Unknown Model'}`;
          default:
            return `New ${contributionType.replace('_', ' ')} Contribution`;
        }
      };

      // First, create the contribution
      const contributionData = {
        entity_type: contributionType,
        title: generateTitle(),
        description: '',
        data: formData,
        source_urls: sourceUrls.filter(url => url.trim() !== '')
      };

      const token = localStorage.getItem('token');
      console.log('🔑 Token check:', token ? `Found token (${token.length} chars)` : 'No token found');

      if (!token) {
        alert('Please log in to create contributions');
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contributions-v2/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(contributionData)
      });

      console.log('📡 Contribution response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Contribution creation failed:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        
        if (response.status === 401) {
          alert('Your session has expired. Please log in again.');
          return;
        }
        
        let errorMessage = 'Failed to create contribution';
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          errorMessage = errorText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const contribution = await response.json();

      // Then, upload images if any
      if (images.length > 0) {
        for (let i = 0; i < images.length; i++) {
          const { file, fieldKey } = images[i];
          const formData = new FormData();
          formData.append('file', file);
          formData.append('is_primary', i === 0 ? 'true' : 'false');
          formData.append('caption', fieldKey || '');

          const imageResponse = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}/api/contributions-v2/${contribution.id}/images`,
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
      resetForm();
      onClose();

    } catch (error) {
      console.error('Error submitting contribution:', error);
      alert('Error submitting contribution. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderFields = (fields) => {
    const groupedFields = {};
    const regularFields = [];

    // Group fields that should be on the same line
    fields.forEach(field => {
      if (field.grouped) {
        if (!groupedFields[field.grouped]) {
          groupedFields[field.grouped] = [];
        }
        groupedFields[field.grouped].push(field);
      } else {
        regularFields.push(field);
      }
    });

    const allRenderedFields = [];

    // Render regular fields
    regularFields.forEach(field => {
      allRenderedFields.push(
        <div key={field.key}>
          <UnifiedFieldRenderer
            field={field}
            value={formData[field.key]}
            onChange={handleInputChange}
            teams={teams}
            brands={brands}
            competitions={competitions}
            masterKits={masterJerseys}
            referenceKits={referenceKits || []}
            players={players || []}
            onImageUpload={handleImageUpload}
            API={process.env.REACT_APP_BACKEND_URL}
            formData={formData}
          />
        </div>
      );
    });

    // Render grouped fields
    Object.entries(groupedFields).forEach(([groupName, groupFields]) => {
      allRenderedFields.push(
        <div key={groupName} className="md:col-span-2">
          <div className="grid grid-cols-2 gap-4">
            {groupFields.map(field => (
              <div key={field.key}>
                <UnifiedFieldRenderer
                  field={field}
                  value={formData[field.key]}
                  onChange={handleInputChange}
                  teams={teams}
                  brands={brands}
                  competitions={competitions}
                  masterKits={masterJerseys}
                  referenceKits={referenceKits || []}
                  players={players || []}
                  onImageUpload={handleImageUpload}
                  API={process.env.REACT_APP_BACKEND_URL}
                  formData={formData}
                />
              </div>
            ))}
          </div>
        </div>
      );
    });

    return allRenderedFields;
  };

  const renderField = (field) => {
    return (
      <div key={field.key} className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          {field.label} {field.required && <span className="text-red-500">*</span>}
        </label>
        <UnifiedFieldRenderer
          field={field}
          value={formData[field.key]}
          onChange={handleInputChange}
          teams={teams}
          brands={brands}
          competitions={competitions}
          masterKits={masterJerseys}
          referenceKits={referenceKits || []}
          players={players || []}
          onImageUpload={handleImageUpload}
          API={process.env.REACT_APP_BACKEND_URL}
          formData={formData}
        />
      </div>
    );
  };

  if (!isOpen) return null;

  const fields = getFieldsForEntityType(contributionType);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" style={{ zIndex: 10001 }}>
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">
            New Contribution - {contributionType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Entity Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Entity Type *
            </label>
            <select
              value={contributionType}
              onChange={(e) => {
                setContributionType(e.target.value);
                resetForm();
              }}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="team">Team</option>
              <option value="brand">Brand</option>
              <option value="player">Player</option>
              <option value="competition">Competition</option>
            </select>
          </div>

          {/* Dynamic Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderFields(fields)}
          </div>

          {/* Image Previews */}
          {previewImages.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Image Previews
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {previewImages.map((preview, index) => (
                  <div key={index} className="relative">
                    <img
                      src={preview.preview}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-32 object-cover rounded-lg border"
                    />
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                    >
                      ×
                    </button>
                    <p className="text-xs text-gray-500 mt-1 truncate">
                      {preview.fieldKey || 'General'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Source URLs */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source URLs (Optional)
            </label>
            {sourceUrls.map((url, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => handleSourceUrlChange(index, e.target.value)}
                  placeholder="https://example.com"
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                {sourceUrls.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeSourceUrl(index)}
                    className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={addSourceUrl}
              className="text-blue-600 hover:bg-blue-50 px-3 py-1 rounded-lg text-sm"
            >
              + Add Source URL
            </button>
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
              {isSubmitting ? 'Submitting...' : 'Submit Contribution'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DynamicContributionForm;