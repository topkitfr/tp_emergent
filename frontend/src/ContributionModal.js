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
  
  // Image management is now handled by UnifiedFieldRenderer
  
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
      
      // Image states no longer needed - handled by UnifiedFieldRenderer
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
      
      // Image changes are now detected through form data changes
      
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
  }, [formData, originalData, entity, title]);

  // Image management functions removed - now handled by UnifiedFieldRenderer

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

    if (changes.length === 0) {
      alert('No changes detected. Please modify at least one field.');
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
      
      // Image changes are now handled through regular form data
      
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
        
        // Image uploads are now handled by UnifiedFieldRenderer
        
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
                  // Image uploads are now handled by UnifiedFieldRenderer through form data
                  // No separate image upload logic needed
                  API={API}
                  formData={formData}
                />
              </div>
            ))}
          </div>

          {/* Images Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Images</h3>
            <div className="text-sm text-gray-600 mb-4">
              Use the image fields below to upload photos. The changes will be tracked automatically.
            </div>
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