import React, { useState, useEffect } from 'react';

const ContributionModal = ({ isOpen, onClose, entity, entityType, onContributionCreated }) => {
  const [formData, setFormData] = useState({});
  const [originalData, setOriginalData] = useState({});
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [sourceUrls, setSourceUrls] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [changes, setChanges] = useState([]);
  
  // États pour la gestion des images
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
      // Initialiser le formulaire avec les données actuelles
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
        // Autres champs selon le type d'entité...
      };
      
      setOriginalData(initialData);
      setFormData(initialData);
      setTitle('');
      setDescription('');
      setSourceUrls(['']);
      setChanges([]);
      
      // Réinitialiser les images
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

  useEffect(() => {
    // Calculer les changements en temps réel
    if (Object.keys(originalData).length > 0) {
      const detectedChanges = [];
      
      Object.keys(formData).forEach(field => {
        const originalValue = originalData[field];
        const newValue = formData[field];
        
        // Normaliser les valeurs pour la comparaison
        const normalizedOriginal = originalValue === null || originalValue === undefined ? '' : String(originalValue);
        const normalizedNew = newValue === null || newValue === undefined ? '' : String(newValue);
        
        if (normalizedOriginal !== normalizedNew && normalizedNew.trim() !== '') {
          detectedChanges.push({
            field,
            from: originalValue,
            to: field === 'colors' ? newValue.split(',').map(c => c.trim()).filter(c => c) : newValue,
            type: normalizedOriginal === '' ? 'add' : 'update'
          });
        }
      });
      
      setChanges(detectedChanges);
      
      // Générer un titre automatique si pas de titre personnalisé
      if (detectedChanges.length > 0 && !title) {
        if (detectedChanges.length === 1) {
          const change = detectedChanges[0];
          const actionText = change.type === 'add' ? 'Ajout' : 'Mise à jour';
          setTitle(`${actionText} ${getFieldDisplayName(change.field)} - ${entity.name}`);
        } else {
          setTitle(`Amélioration de la fiche - ${entity.name}`);
        }
      }
    }
  }, [formData, originalData, entity, title]);

  // Fonctions de gestion des images
  const handleImageUpload = (imageType, file) => {
    if (!file) return;
    
    // Vérifier le type de fichier
    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner un fichier image valide');
      return;
    }
    
    // Vérifier la taille (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('La taille de l\'image ne doit pas dépasser 5MB');
      return;
    }
    
    // Mettre à jour les fichiers
    setImageFiles(prev => ({
      ...prev,
      [imageType]: file
    }));
    
    // Créer l'aperçu
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreviews(prev => ({
        ...prev,
        [imageType]: e.target.result
      }));
    };
    reader.readAsDataURL(file);
  };

  const handleMultipleImagesUpload = (files) => {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
      if (!file.type.startsWith('image/')) {
        alert(`${file.name} n'est pas un fichier image valide`);
        return false;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert(`${file.name} dépasse la taille maximale de 5MB`);
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) return;

    setImageFiles(prev => ({
      ...prev,
      secondary_photos: [...prev.secondary_photos, ...validFiles]
    }));

    // Créer les aperçus
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreviews(prev => ({
          ...prev,
          secondary_photos: [...prev.secondary_photos, e.target.result]
        }));
      };
      reader.readAsDataURL(file);
    });
  };

  const removeSecondaryImage = (index) => {
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
      name: 'du nom',
      short_name: 'du nom court',
      city: 'de la ville',
      country: 'du pays',
      founded_year: 'de l\'année de fondation',
      colors: 'des couleurs',
      logo_url: 'du logo',
      official_name: 'du nom officiel',
      competition_type: 'du type de compétition',
      level: 'du niveau',
      website: 'du site web'
    };
    return fieldNames[field] || `de ${field}`;
  };

  const getFieldsForEntityType = () => {
    switch (entityType) {
      case 'team':
        return [
          { key: 'name', label: 'Nom de l\'équipe', type: 'text', required: true },
          { key: 'short_name', label: 'Nom court', type: 'text' },
          { key: 'city', label: 'Ville', type: 'text' },
          { key: 'country', label: 'Pays', type: 'text' },
          { key: 'founded_year', label: 'Année de fondation', type: 'number' },
          { key: 'colors', label: 'Couleurs (séparées par des virgules)', type: 'text' },
          { key: 'logo_url', label: 'URL du logo', type: 'url' }
        ];
      case 'competition':
        return [
          { key: 'name', label: 'Nom de la compétition', type: 'text', required: true },
          { key: 'official_name', label: 'Nom officiel', type: 'text' },
          { key: 'country', label: 'Pays', type: 'text' },
          { key: 'competition_type', label: 'Type', type: 'select', options: ['domestic_league', 'cup', 'international'] },
          { key: 'level', label: 'Niveau', type: 'number' },
          { key: 'logo_url', label: 'URL du logo', type: 'url' }
        ];
      case 'brand':
        return [
          { key: 'name', label: 'Nom de la marque', type: 'text', required: true },
          { key: 'country', label: 'Pays d\'origine', type: 'text' },
          { key: 'website', label: 'Site web', type: 'url' },
          { key: 'logo_url', label: 'URL du logo', type: 'url' }
        ];
      default:
        return [
          { key: 'name', label: 'Nom', type: 'text', required: true }
        ];
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addSourceUrl = () => {
    setSourceUrls(prev => [...prev, '']);
  };

  const removeSourceUrl = (index) => {
    setSourceUrls(prev => prev.filter((_, i) => i !== index));
  };

  const updateSourceUrl = (index, value) => {
    setSourceUrls(prev => prev.map((url, i) => i === index ? value : url));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (changes.length === 0) {
      alert('Aucun changement détecté. Veuillez modifier au moins un champ.');
      return;
    }
    
    if (!title.trim()) {
      alert('Veuillez saisir un titre pour votre contribution.');
      return;
    }

    setLoading(true);
    
    try {
      const token = localStorage.getItem('auth_token');
      
      // Préparer les données proposées
      const proposedData = {};
      changes.forEach(change => {
        proposedData[change.field] = change.to;
      });
      
      // Traitement des images
      const images = {};
      
      // Logo principal
      if (imageFiles.logo) {
        images.logo = await convertFileToBase64(imageFiles.logo);
      }
      
      // Photo principale
      if (imageFiles.primary_photo) {
        images.primary_photo = await convertFileToBase64(imageFiles.primary_photo);
      }
      
      // Photos secondaires
      if (imageFiles.secondary_photos.length > 0) {
        images.secondary_photos = await Promise.all(
          imageFiles.secondary_photos.map(file => convertFileToBase64(file))
        );
      }

      const contributionData = {
        entity_type: entityType,
        entity_id: entity.id,
        proposed_data: proposedData,
        title: title.trim(),
        description: description.trim() || null,
        source_urls: sourceUrls.filter(url => url.trim()),
        images: Object.keys(images).length > 0 ? images : null
      };
      
      const response = await fetch(`${API}/api/contributions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(contributionData)
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Contribution créée avec succès ! Référence: ${result.topkit_reference}`);
        onContributionCreated && onContributionCreated(result);
        onClose();
      } else {
        const error = await response.json();
        alert(`Erreur: ${error.detail || 'Une erreur est survenue'}`);
      }
    } catch (error) {
      console.error('Erreur lors de la création de la contribution:', error);
      alert('Une erreur est survenue lors de la création de la contribution');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const fields = getFieldsForEntityType();

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>
        
        {/* Modal */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <form onSubmit={handleSubmit}>
            {/* Header */}
            <div className="bg-blue-600 px-6 py-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-white">
                  ✏️ Améliorer la fiche : {entity?.name}
                </h3>
                <button
                  type="button"
                  onClick={onClose}
                  className="text-white hover:text-gray-200"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Body */}
            <div className="px-6 py-4 max-h-96 overflow-y-auto">
              
              {/* Informations actuelles */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Informations actuelles :</h4>
                <div className="text-sm text-gray-600">
                  <p><strong>Référence :</strong> {entity?.topkit_reference}</p>
                  <p><strong>Type :</strong> {entityType}</p>
                </div>
              </div>
              
              {/* Formulaire d'édition */}
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {fields.map((field) => (
                  <div key={field.key} className="flex flex-col">
                    <label className="text-sm font-medium text-gray-700 mb-1">
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.key] || ''}
                        onChange={(e) => handleInputChange(field.key, e.target.value)}
                        className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Sélectionner...</option>
                        {field.options?.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={field.type}
                        value={formData[field.key] || ''}
                        onChange={(e) => handleInputChange(field.key, e.target.value)}
                        className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder={`Saisir ${field.label.toLowerCase()}`}
                        required={field.required}
                      />
                    )}
                  </div>
                ))}
              </div>
              
              {/* Section Upload d'Images */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
                  📸 Images à ajouter/modifier
                  <span className="text-xs text-gray-500 font-normal">(optionnel, max 5MB par image)</span>
                </h4>
                
                <div className="space-y-4">
                  {/* Logo/Image principale */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {entityType === 'team' ? 'Logo de l\'équipe' : 
                       entityType === 'competition' ? 'Logo de la compétition' :
                       entityType === 'brand' ? 'Logo de la marque' :
                       entityType === 'player' ? 'Photo du joueur' : 'Image principale'}
                    </label>
                    <div className="flex items-center gap-4">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleImageUpload('logo', e.target.files[0])}
                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                      />
                      {imagePreviews.logo && (
                        <div className="relative">
                          <img src={imagePreviews.logo} alt="Aperçu logo" className="w-16 h-16 object-cover rounded-lg border" />
                          <button
                            type="button"
                            onClick={() => {
                              setImageFiles(prev => ({ ...prev, logo: null }));
                              setImagePreviews(prev => ({ ...prev, logo: '' }));
                            }}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                          >
                            ×
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Photo principale (pour maillots) */}
                  {(entityType === 'master-jersey' || entityType === 'jersey') && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Photo principale du maillot
                      </label>
                      <div className="flex items-center gap-4">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => handleImageUpload('primary_photo', e.target.files[0])}
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                        />
                        {imagePreviews.primary_photo && (
                          <div className="relative">
                            <img src={imagePreviews.primary_photo} alt="Aperçu photo principale" className="w-16 h-16 object-cover rounded-lg border" />
                            <button
                              type="button"
                              onClick={() => {
                                setImageFiles(prev => ({ ...prev, primary_photo: null }));
                                setImagePreviews(prev => ({ ...prev, primary_photo: '' }));
                              }}
                              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                            >
                              ×
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Photos secondaires */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Photos supplémentaires
                      <span className="text-xs text-gray-500 font-normal ml-2">(détails, autres angles...)</span>
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={(e) => handleMultipleImagesUpload(e.target.files)}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                    />
                    {imagePreviews.secondary_photos.length > 0 && (
                      <div className="flex gap-2 mt-3 flex-wrap">
                        {imagePreviews.secondary_photos.map((preview, index) => (
                          <div key={index} className="relative">
                            <img src={preview} alt={`Aperçu ${index + 1}`} className="w-16 h-16 object-cover rounded-lg border" />
                            <button
                              type="button"
                              onClick={() => removeSecondaryImage(index)}
                              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Prévisualisation des changements */}
              {changes.length > 0 && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                  <h4 className="font-medium text-blue-900 mb-3">Aperçu des changements :</h4>
                  <div className="space-y-2">
                    {changes.map((change, index) => (
                      <div key={index} className="flex items-center gap-4 text-sm">
                        <span className="font-medium text-blue-900 min-w-0 flex-shrink-0">
                          {getFieldDisplayName(change.field)}:
                        </span>
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          <span className="text-red-600 truncate">
                            {change.from || 'Non défini'}
                          </span>
                          <span className="text-gray-400">→</span>
                          <span className="text-green-600 truncate font-medium">
                            {Array.isArray(change.to) ? change.to.join(', ') : change.to}
                          </span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          change.type === 'add' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                        }`}>
                          {change.type === 'add' ? 'Ajout' : 'Modification'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Titre de la contribution */}
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Titre de la contribution <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Décrivez brièvement votre contribution..."
                  required
                />
              </div>
              
              {/* Description */}
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Justification (optionnelle)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Expliquez pourquoi cette modification est nécessaire..."
                />
              </div>
              
              {/* Sources */}
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Sources (optionnelles)
                </label>
                {sourceUrls.map((url, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => updateSourceUrl(index, e.target.value)}
                      className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://exemple.com/source"
                    />
                    {sourceUrls.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeSourceUrl(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        ❌
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addSourceUrl}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  + Ajouter une source
                </button>
              </div>
            </div>
            
            {/* Footer */}
            <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
              <div className="text-sm text-gray-600">
                {changes.length === 0 ? (
                  "Aucun changement détecté"
                ) : (
                  `${changes.length} changement${changes.length > 1 ? 's' : ''} détecté${changes.length > 1 ? 's' : ''}`
                )}
              </div>
              
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  disabled={loading}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  disabled={loading || changes.length === 0}
                >
                  {loading ? 'Soumission...' : '📝 Soumettre pour validation'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ContributionModal;