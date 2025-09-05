import React, { useState, useEffect } from 'react';

const ContributionModal = ({ isOpen, onClose, entity, entityType, onContributionCreated }) => {
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

  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    if (isOpen && entity) {
      // Initialize form with current data
      const initialData = {
        name: entity.name || '',
        short_name: entity.short_name || '',
        city: entity.city || '',
        country: entity.country || '',
        founded_year: entity.founded_year || '',
        colors: Array.isArray(entity.colors) ? entity.colors.join(', ') : '',
        logo_url: entity.logo_url || '',
        official_name: entity.official_name || '',
        competition_type: entity.competition_type || '',
        level: entity.level || '',
        website: entity.website || '',
        // Other fields based on entity type...
      };
      
      setOriginalData(initialData);
      setFormData(initialData);
      setTitle('');
      setDescription('');
      setSourceUrls(['']);
      setChanges([]);
      
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
  }, [isOpen, entity]);

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

  const getFieldsForEntityType = () => {
    switch (entityType) {
      case 'team':
        return [
          { key: 'name', label: 'Team Name', type: 'text', required: true },
          { key: 'short_name', label: 'Short Name', type: 'text' },
          { key: 'country', label: 'Country', type: 'text', required: true },
          { key: 'city', label: 'City', type: 'text' },
          { key: 'founded_year', label: 'Founded Year', type: 'number' },
          { key: 'colors', label: 'Team Colors', type: 'color_list', placeholder: 'Enter colors one by one' }
        ];

      case 'brand':
        return [
          { key: 'name', label: 'Nom de la marque', type: 'text', required: true, placeholder: 'Ex: Nike' },
          { key: 'official_name', label: 'Nom officiel', type: 'text', placeholder: 'Ex: Nike Inc.' },
          { key: 'country', label: 'Pays', type: 'text', placeholder: 'Ex: United States' },
          { key: 'founded_year', label: 'Année de fondation', type: 'number', placeholder: 'Ex: 1964', min: 1800, max: 2030 },
          { key: 'website', label: 'Site web', type: 'url', placeholder: 'Ex: https://www.nike.com' },
          { key: 'common_names', label: 'Noms alternatifs', type: 'name_list', placeholder: 'Ex: Nike Football, Swoosh' }
        ];

      case 'player':
        return [
          { key: 'name', label: 'Nom du joueur', type: 'text', required: true, placeholder: 'Ex: Kylian Mbappé' },
          { key: 'full_name', label: 'Nom complet', type: 'text', placeholder: 'Ex: Kylian Mbappé Lottin' },
          { key: 'nationality', label: 'Nationalité', type: 'text', placeholder: 'Ex: France' },
          { key: 'position', label: 'Position', type: 'select', options: ['Goalkeeper', 'Defender', 'Midfielder', 'Forward'] },
          { key: 'birth_date', label: 'Date de naissance', type: 'date', max: new Date().toISOString().split('T')[0] },
          { key: 'common_names', label: 'Noms alternatifs', type: 'name_list', placeholder: 'Ex: Mbappé, K. Mbappé' }
        ];

      case 'competition':
        return [
          { key: 'name', label: 'Nom de la ligue', type: 'text', required: true, placeholder: 'Ex: Ligue 1' },
          { key: 'official_name', label: 'Nom officiel', type: 'text', placeholder: 'Ex: Ligue 1 Uber Eats' },
          { key: 'competition_type', label: 'Type de ligue', type: 'select', required: true, options: [
            { value: 'domestic_league', label: 'Championnat national' },
            { value: 'cup', label: 'Coupe' },
            { value: 'international', label: 'Compétition internationale' },
            { value: 'friendly', label: 'Match amical' }
          ]},
          { key: 'country', label: 'Pays', type: 'text', placeholder: 'Ex: France' },
          { key: 'level', label: 'Niveau', type: 'number', placeholder: 'Ex: 1 (première division)' },
          { key: 'common_names', label: 'Noms alternatifs', type: 'name_list', placeholder: 'Ex: L1, French Championship' }
        ];

      case 'master_jersey':
        return [
          { key: 'team_id', label: 'Équipe', type: 'select', required: true, options: 'teams' },
          { key: 'brand_id', label: 'Marque', type: 'select', required: true, options: 'brands' },
          { key: 'season', label: 'Saison', type: 'text', required: true, placeholder: '2024-25' },
          { key: 'jersey_type', label: 'Type', type: 'select', required: true, options: [
            { value: 'home', label: 'Home' },
            { value: 'away', label: 'Away' },
            { value: 'third', label: 'Third' },
            { value: 'fourth', label: 'Fourth' },
            { value: 'goalkeeper', label: 'GK' },
            { value: 'special', label: 'Special' },
            { value: 'other', label: 'Other' }
          ]},
          { key: 'model', label: 'Modèle', type: 'select', required: true, options: [
            { value: 'authentic', label: 'Authentique' },
            { value: 'replica', label: 'Réplique' }
          ]},
          { key: 'colors', label: 'Couleurs', type: 'text', required: true, placeholder: 'Ex: Blue, White, Red' },
          { key: 'pattern', label: 'Pattern', type: 'textarea', placeholder: 'Description du motif, design, rayures...' }
        ];
        
      default:
        return [];
    }
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
      // Prepare contribution data
      const contributionData = {
        title: title.trim(),
        description: description.trim(),
        entity_type: entityType,
        entity_id: entity.id,
        proposed_data: formData,
        source_urls: sourceUrls.filter(url => url.trim() !== ''),
        changes: changes
      };

      // Convert images to base64 if present
      if (imageFiles.logo) {
        const logoBase64 = await convertFileToBase64(imageFiles.logo);
        contributionData.images = { logo: logoBase64 };
      }

      if (imageFiles.primary_photo) {
        const photoBase64 = await convertFileToBase64(imageFiles.primary_photo);
        contributionData.images = {
          ...(contributionData.images || {}),
          primary_photo: photoBase64
        };
      }

      if (imageFiles.secondary_photos.length > 0) {
        const secondaryPhotos = await Promise.all(
          imageFiles.secondary_photos.map(file => convertFileToBase64(file))
        );
        contributionData.images = {
          ...(contributionData.images || {}),
          secondary_photos: secondaryPhotos
        };
      }

      console.log('Submitting contribution:', contributionData);

      // Submit contribution
      const response = await fetch(`${API}/api/contributions`, {
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

  const fields = getFieldsForEntityType();

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
              <div key={field.key} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                
                {field.type === 'select' ? (
                  <select
                    value={formData[field.key] || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      [field.key]: e.target.value
                    }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    required={field.required}
                  >
                    <option value="">Select {field.label.toLowerCase()}</option>
                    {Array.isArray(field.options) ? field.options.map(option => (
                      <option key={typeof option === 'object' ? option.value : option} value={typeof option === 'object' ? option.value : option}>
                        {typeof option === 'object' ? option.label : option}
                      </option>
                    )) : null}
                  </select>
                ) : field.type === 'color_list' ? (
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newColor || ''}
                        onChange={(e) => setNewColor(e.target.value)}
                        placeholder={field.placeholder || "Enter color (e.g., Red, Blue, #FF0000)"}
                        className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          if (newColor && !(formData[field.key] || []).includes(newColor)) {
                            setFormData(prev => ({
                              ...prev,
                              [field.key]: [...(prev[field.key] || []), newColor]
                            }));
                            setNewColor('');
                          }
                        }}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                      >
                        +
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData[field.key] || []).map((color, index) => (
                        <span
                          key={index}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm flex items-center"
                        >
                          {color}
                          <button
                            type="button"
                            onClick={() => setFormData(prev => ({
                              ...prev,
                              [field.key]: prev[field.key].filter(c => c !== color)
                            }))}
                            className="ml-2 text-red-500 hover:text-red-700"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                ) : field.type === 'name_list' ? (
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newName || ''}
                        onChange={(e) => setNewName(e.target.value)}
                        placeholder={field.placeholder || "Enter name"}
                        className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          if (newName && !(formData[field.key] || []).includes(newName)) {
                            setFormData(prev => ({
                              ...prev,
                              [field.key]: [...(prev[field.key] || []), newName]
                            }));
                            setNewName('');
                          }
                        }}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                      >
                        +
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData[field.key] || []).map((name, index) => (
                        <span
                          key={index}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm flex items-center"
                        >
                          {name}
                          <button
                            type="button"
                            onClick={() => setFormData(prev => ({
                              ...prev,
                              [field.key]: prev[field.key].filter(n => n !== name)
                            }))}
                            className="ml-2 text-red-500 hover:text-red-700"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                ) : field.type === 'textarea' ? (
                  <textarea
                    value={formData[field.key] || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      [field.key]: e.target.value
                    }))}
                    rows="3"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                    required={field.required}
                  />
                ) : (
                  <input
                    type={field.type}
                    value={formData[field.key] || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      [field.key]: e.target.value
                    }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                    required={field.required}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Image Upload Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Images</h3>
            
            {/* Logo Upload */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Logo/Main Photo</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImageUpload('logo', e.target.files[0])}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {imagePreviews.logo && (
                <div className="mt-2">
                  <img src={imagePreviews.logo} alt="Logo preview" className="w-24 h-24 object-cover rounded-lg border" />
                </div>
              )}
            </div>

            {/* Secondary Photos Upload */}
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
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
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