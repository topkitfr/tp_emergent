import React, { useState, useEffect } from 'react';
import { X, Upload, ThumbsUp, ThumbsDown, Image as ImageIcon } from 'lucide-react';
import { getUnifiedFieldsForEntityType, validateEntityData } from './UnifiedFieldDefinitions';
import UnifiedFieldRenderer from './UnifiedFieldRenderer';

const DynamicContributionForm = ({ isOpen, onClose, selectedType = null, teams = [], brands = [], competitions = [], masterJerseys = [], API }) => {
  const [contributionType, setContributionType] = useState(selectedType || 'team');
  const [formData, setFormData] = useState({});
  const [images, setImages] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
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
    setTitle('');
    setDescription('');
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
  };

  const removeImage = (index) => {
    setPreviewImages(prev => prev.filter((_, i) => i !== index));
    setImages(prev => prev.filter((_, i) => i !== index));
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

    if (!title.trim()) {
      return 'Title is required';
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
      // First, create the contribution
      const contributionData = {
        entity_type: contributionType,
        title,
        description: description || '',
        data: formData,
        source_urls: sourceUrls.filter(url => url.trim() !== '')
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contributions-v2/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(contributionData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create contribution: ${response.statusText}`);
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

  const renderField = (field) => {
    return (
      <UnifiedFieldRenderer
        key={field.key}
        field={field}
        value={formData[field.key]}
        onChange={handleInputChange}
        teams={teams}
        brands={brands}
        competitions={competitions}
        masterKits={masterJerseys}
        onImageUpload={handleImageUpload}
        API={process.env.REACT_APP_BACKEND_URL}
      />
    );
  };

  if (!isOpen) return null;

  const fields = getFieldsForEntityType(contributionType);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
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
              Contribution Type
            </label>
            <select
              value={contributionType}
              onChange={(e) => handleTypeChange(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="team">Team</option>
              <option value="brand">Brand</option>
              <option value="player">Player</option>
              <option value="competition">Competition</option>
              <option value="master_kit">Master Kit</option>
              <option value="reference_kit">Reference Kit</option>
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={`Add new ${contributionType.replace('_', ' ')}`}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Additional information about this contribution..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Dynamic Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fields.map(field => renderField(field))}
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