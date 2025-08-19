import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { JERSEY_DETAIL_CRITERIA, PRICE_FACTORS, BASE_PRICES } from './JerseyDetailCriteria';
import tokenManager from './utils/tokenManager';

const JerseyDetailEditor = ({ jersey, isOpen, onClose, onSave, onUpdateSuccess, mode }) => {
  const [detailData, setDetailData] = useState({
    // Jersey basic info (editable for new submissions, read-only for existing)
    team: '',
    league: '',
    season: '',
    jersey_type: '',
    manufacturer: '',
    sku_code: '', // Changed from reference to sku_code
    model: 'authentic', // New field: authentic/replica
    description: '',
    
    // Editable collection details
    model_type: 'authentic',
    condition: 'mint',
    size: 'm',
    special_features: [],
    material_details: '',
    tags: 'tags_on',
    packaging: 'no_packaging',
    customization: 'blank',
    competition_badges: '',
    rarity: 'common',
    purchase_price: '',
    purchase_date: '',
    purchase_location: '',
    certificate_authenticity: false,
    storage_notes: '',
    
    // Photo uploads
    front_photo: null,
    back_photo: null,
    
    // Auto-calculated
    estimated_value: 0
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [photoPreview, setPhotoPreview] = useState({
    front: null,
    back: null
  });

  // Add suggestions state and constants for smart form
  const [suggestions, setSuggestions] = useState({});

  // Predefined options
  const SEASONS = [
    '25/26', '24/25', '23/24', '22/23', '21/22', '20/21', '19/20', '18/19', '17/18', '16/17'
  ];

  const JERSEY_TYPES = [
    { value: 'home', label: 'Domicile' },
    { value: 'away', label: 'Extérieur' },
    { value: 'third', label: 'Troisième' },
    { value: 'goalkeeper', label: 'Gardien' },
    { value: 'training', label: 'Entraînement' },
    { value: 'special', label: 'Édition spéciale' }
  ];

  const MANUFACTURERS = [
    'Nike', 'Adidas', 'Puma', 'Jordan', 'Umbro', 'Kappa', 'New Balance', 'Under Armour', 'Hummel', 'Autre'
  ];

  const MODEL_TYPES = [
    { value: 'authentic', label: 'Authentic' },
    { value: 'replica', label: 'Replica' }
  ];

  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Check if this is a new submission
  const isNewSubmission = jersey?.isNewSubmission || mode === 'submission' || false;
  const isAdminEdit = jersey?.isAdminEdit || mode === 'admin-modify' || false;
  const isCollectionEdit = mode === 'collection-edit' || (!isNewSubmission && !isAdminEdit);

  useEffect(() => {
    if (jersey && isOpen) {
      // Reset to jersey data or defaults
      setDetailData({
        // Jersey basic info
        team: jersey?.team || '',
        league: jersey?.league || '',
        season: jersey?.season || '',
        jersey_type: jersey?.jersey_type || '',
        manufacturer: jersey?.manufacturer || '',
        sku_code: jersey?.sku_code || jersey?.reference_code || '', // Handle both names
        model: jersey?.model || 'authentic',
        description: jersey?.description || '',
        
        // Collection details from existing data or defaults
        model_type: jersey?.model_type || 'authentic',
        condition: jersey?.condition || 'mint',
        size: jersey?.size || 'm',
        special_features: jersey?.special_features || [],
        material_details: jersey?.material_details || '',
        tags: jersey?.tags || 'tags_on',
        packaging: jersey?.packaging || 'no_packaging',
        customization: jersey?.customization || 'blank',
        competition_badges: jersey?.competition_badges || '',
        rarity: jersey?.rarity || 'common',
        purchase_price: jersey?.purchase_price || '',
        purchase_date: jersey?.purchase_date || '',
        purchase_location: jersey?.purchase_location || '',
        certificate_authenticity: jersey?.certificate_authenticity || false,
        storage_notes: jersey?.storage_notes || '',
        
        // Photos
        front_photo: null,
        back_photo: null,
        
        estimated_value: 0
      });
      
      // Clear photo previews and suggestions
      setPhotoPreview({
        front: null,
        back: null
      });
      setSuggestions({});
      
      setError('');
    }
  }, [jersey, isOpen]);

  useEffect(() => {
    // Calculate estimated value when relevant fields change
    calculateEstimatedValue();
  }, [detailData.model_type, detailData.condition, detailData.rarity, detailData.special_features]);

  const calculateEstimatedValue = () => {
    // Basic calculation logic
    let baseValue = BASE_PRICES[detailData.model_type] || 50;
    let conditionMultiplier = PRICE_FACTORS.condition[detailData.condition] || 1;
    let rarityMultiplier = PRICE_FACTORS.rarity[detailData.rarity] || 1;
    let featuresBonus = (detailData.special_features || []).length * 10;

    const estimatedValue = Math.round((baseValue * conditionMultiplier * rarityMultiplier) + featuresBonus);
    
    setDetailData(prev => ({
      ...prev,
      estimated_value: estimatedValue
    }));
  };

  const handleInputChange = (field, value) => {
    setDetailData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSpecialFeatureToggle = (feature) => {
    setDetailData(prev => ({
      ...prev,
      special_features: prev.special_features?.includes(feature)
        ? (prev.special_features || []).filter(f => f !== feature)
        : [...(prev.special_features || []), feature]
    }));
  };

  const handlePhotoUpload = (type, file) => {
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/webp')) {
      setDetailData(prev => ({
        ...prev,
        [`${type}_photo`]: file
      }));
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(prev => ({
          ...prev,
          [type]: e.target.result
        }));
      };
      reader.readAsDataURL(file);
    } else {
      setError('Veuillez sélectionner une image au format JPEG, PNG ou WebP');
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError('');
      
      if (isNewSubmission || isAdminEdit) {
        // Validation for new submissions and admin edits (basic info)
        if (!detailData.team || !detailData.league || !detailData.season || !detailData.model) {
          setError('Veuillez remplir les champs obligatoires: Club/Équipe, Ligue, Saison, et Modèle');
          return;
        }
      } else if (isCollectionEdit) {
        // Validation for collection edits (collection details)
        if (!detailData.model_type || !detailData.condition || !detailData.size) {
          setError('Veuillez remplir les champs obligatoires: Modèle, État, et Taille');
          return;
        }
      }
      
      if (isNewSubmission) {
        // Create FormData for photo upload
        const formData = new FormData();
        
        // Add all jersey data
        Object.keys(detailData).forEach(key => {
          if (key !== 'front_photo' && key !== 'back_photo' && detailData[key] !== null && detailData[key] !== undefined) {
            if (Array.isArray(detailData[key])) {
              formData.append(key, JSON.stringify(detailData[key]));
            } else {
              formData.append(key, detailData[key]);
            }
          }
        });
        
        // Add photos if they exist
        if (detailData.front_photo) {
          formData.append('front_photo', detailData.front_photo);
        }
        if (detailData.back_photo) {
          formData.append('back_photo', detailData.back_photo);
        }
        
        console.log('Submitting new jersey with data:', detailData);
        
        // Submit new jersey
        const response = await tokenManager.makeAuthenticatedRequest(
          'post',
          '/api/jerseys',
          formData,
          {
            'Content-Type': 'multipart/form-data'
          }
        );
        
        console.log('Jersey submitted successfully:', response.data);
        
        if (onUpdateSuccess) {
          onUpdateSuccess();
        }
        
      } else {
        // Existing logic for updating collection details or admin edits
        if (isAdminEdit) {
          // Admin is editing a pending jersey
          if (!jersey || !jersey.id) {
            setError('Erreur: Informations du maillot manquantes');
            return;
          }
          
          const response = await tokenManager.makeAuthenticatedRequest(
            'put',
            `/api/admin/jerseys/${jersey.id}`,
            detailData
          );
          
          console.log('Admin jersey update successful:', response.data);
          
        } else {
          // Regular collection update
          if (!jersey || !jersey.id) {
            setError('Erreur: Informations du maillot manquantes');
            return;
          }
          
          console.log('Saving jersey details for jersey ID:', jersey.id, 'Data:', detailData);
          
          const response = await tokenManager.makeAuthenticatedRequest(
            'put',
            `/api/collections/owned/${jersey.id}/details`,
            detailData
          );
          
          console.log('Jersey details saved successfully:', response.data);
        }
        
        if (onSave) {
          onSave(detailData);
        }
        if (onUpdateSuccess) {
          onUpdateSuccess();
        }
      }
      
      onClose();
      
    } catch (error) {
      console.error('Error saving jersey:', error);
      let errorMessage = 'Erreur lors de la sauvegarde';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-black">
              {isNewSubmission ? '📝 Soumettre un maillot' : 
               (isAdminEdit ? '✏️ Corriger le maillot' : 
               (isCollectionEdit ? '🔍 Modifier les détails de collection' : '✏️ Modifier les détails'))}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-black text-2xl font-bold"
            >
              ×
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
              <strong>Erreur:</strong> {error}
            </div>
          )}

          <div className="grid gap-6 grid-cols-1">
            {/* Left Column - Basic Info - Only show for submission and admin-modify */}
            {(isNewSubmission || isAdminEdit) && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-black border-b border-gray-200 pb-2">
                📋 Informations de base
              </h3>

              {/* League */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Ligue/Championnat *
                </label>
                <input
                  type="text"
                  value={detailData.league}
                  onChange={(e) => handleInputChange('league', e.target.value)}
                  disabled={!(isNewSubmission || isAdminEdit)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: Ligue 1, Premier League, La Liga..."
                  required
                />
              </div>

              {/* Club/National Team */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Club/Équipe nationale *
                </label>
                <input
                  type="text"
                  value={detailData.team}
                  onChange={(e) => handleInputChange('team', e.target.value)}
                  disabled={!(isNewSubmission || isAdminEdit)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: Paris Saint-Germain, France..."
                  required
                />
              </div>

              {/* Season */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Saison *
                </label>
                <select
                  value={detailData.season}
                  onChange={(e) => handleInputChange('season', e.target.value)}
                  disabled={!(isNewSubmission || isAdminEdit)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  required
                >
                  <option value="">Sélectionner une saison...</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              {/* Brand/Manufacturer */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Marque/Fabricant
                </label>
                <select
                  value={detailData.manufacturer}
                  onChange={(e) => handleInputChange('manufacturer', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                >
                  <option value="">Sélectionner une marque...</option>
                  {MANUFACTURERS.map(manufacturer => (
                    <option key={manufacturer} value={manufacturer}>{manufacturer}</option>
                  ))}
                </select>
              </div>

              {/* Code SKU (instead of Reference) */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Code SKU
                </label>
                <input
                  type="text"
                  value={detailData.sku_code}
                  onChange={(e) => handleInputChange('sku_code', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: DH2987-100, FB7894-411..."
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Type de maillot
                </label>
                <select
                  value={detailData.jersey_type}
                  onChange={(e) => handleInputChange('jersey_type', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                >
                  <option value="">Sélectionner un type...</option>
                  {JERSEY_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              {/* Model (New field: Authentic/Replica) */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Modèle *
                </label>
                <select
                  value={detailData.model}
                  onChange={(e) => handleInputChange('model', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  required
                >
                  {MODEL_TYPES.map(model => (
                    <option key={model.value} value={model.value}>{model.label}</option>
                  ))}
                </select>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Description
                </label>
                <textarea
                  value={detailData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black h-24 disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Détails supplémentaires sur ce maillot..."
                />
              </div>

              {/* Photo Uploads */}
              <div className="space-y-4">
                <h4 className="text-md font-semibold text-black">📸 Photos du maillot</h4>
                
                {/* Front Photo */}
                <div>
                  <label className="block text-sm font-medium text-black mb-2">
                    Photo de face
                  </label>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={(e) => handlePhotoUpload('front', e.target.files[0])}
                    className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
                  />
                  {photoPreview.front && (
                    <div className="mt-2">
                      <img 
                        src={photoPreview.front} 
                        alt="Preview front" 
                        className="w-32 h-32 object-cover rounded-lg border border-gray-300"
                      />
                    </div>
                  )}
                </div>

                {/* Back Photo */}
                <div>
                  <label className="block text-sm font-medium text-black mb-2">
                    Photo de dos
                  </label>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={(e) => handlePhotoUpload('back', e.target.files[0])}
                    className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
                  />
                  {photoPreview.back && (
                    <div className="mt-2">
                      <img 
                        src={photoPreview.back} 
                        alt="Preview back" 
                        className="w-32 h-32 object-cover rounded-lg border border-gray-300"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
            )}

            {/* Right Column - Detail Info - Only show for collection-edit */}
            {isCollectionEdit && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-black border-b border-gray-200 pb-2">
                🔍 Détails de la collection
              </h3>

              {/* Model Type */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.model_type?.label || "Model Type"}
                </label>
                <select
                  value={detailData.model_type}
                  onChange={(e) => handleInputChange('model_type', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.model_type?.options ? 
                    JERSEY_DETAIL_CRITERIA.model_type.options.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    )) : (
                      <>
                        <option value="authentic">Authentic</option>
                        <option value="replica">Replica</option>
                      </>
                    )
                  }
                </select>
              </div>

              {/* Condition */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.condition?.label || "Condition"}
                </label>
                <select
                  value={detailData.condition}
                  onChange={(e) => handleInputChange('condition', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.condition?.options ? 
                    JERSEY_DETAIL_CRITERIA.condition.options.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    )) : (
                      <>
                        <option value="mint">Mint</option>
                        <option value="near_mint">Near Mint</option>
                        <option value="very_good">Very Good</option>
                        <option value="good">Good</option>
                      </>
                    )
                  }
                </select>
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.size?.label || "Size"}
                </label>
                <select
                  value={detailData.size}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.size?.options ? 
                    JERSEY_DETAIL_CRITERIA.size.options.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    )) : (
                      <>
                        <option value="xs">XS</option>
                        <option value="s">S</option>
                        <option value="m">M</option>
                        <option value="l">L</option>
                        <option value="xl">XL</option>
                        <option value="xxl">XXL</option>
                      </>
                    )
                  }
                </select>
              </div>

              {/* Special Features */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.special_features?.label || "Special Features"}
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {(JERSEY_DETAIL_CRITERIA.special_features?.options || []).map((feature) => (
                    <label key={feature.value} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={(detailData.special_features || []).includes(feature.value)}
                        onChange={() => handleSpecialFeatureToggle(feature.value)}
                        className="w-4 h-4 text-black bg-white border-gray-300 rounded focus:ring-black focus:ring-2"
                      />
                      <span className="text-sm text-black">{feature.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Rarity */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.rarity?.label || "Rarity"}
                </label>
                <select
                  value={detailData.rarity}
                  onChange={(e) => handleInputChange('rarity', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.rarity?.options ? 
                    JERSEY_DETAIL_CRITERIA.rarity.options.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    )) : (
                      <>
                        <option value="common">Common</option>
                        <option value="uncommon">Uncommon</option>
                        <option value="rare">Rare</option>
                        <option value="very_rare">Very Rare</option>
                      </>
                    )
                  }
                </select>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.tags?.label || "Tags"}
                </label>
                <select
                  value={detailData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.tags?.options ? 
                    JERSEY_DETAIL_CRITERIA.tags.options.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    )) : (
                      <>
                        <option value="tags_on">Tags On</option>
                        <option value="tags_off">Tags Off</option>
                        <option value="no_tags">No Tags</option>
                      </>
                    )
                  }
                </select>
              </div>

              {/* Purchase Price */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.purchase_price?.label || "Purchase Price"}
                </label>
                <input
                  type="number"
                  value={detailData.purchase_price}
                  onChange={(e) => handleInputChange('purchase_price', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                  placeholder={JERSEY_DETAIL_CRITERIA.purchase_price?.placeholder || "Prix d'achat en €"}
                />
              </div>

              {/* Purchase Date */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.purchase_date?.label || "Purchase Date"}
                </label>
                <input
                  type="date"
                  value={detailData.purchase_date}
                  onChange={(e) => handleInputChange('purchase_date', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                />
              </div>

              {/* Storage Notes */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.storage_notes?.label || "Storage Notes"}
                </label>
                <textarea
                  value={detailData.storage_notes}
                  onChange={(e) => handleInputChange('storage_notes', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black h-24"
                  placeholder={JERSEY_DETAIL_CRITERIA.storage_notes?.placeholder || "Notes sur le stockage et l'entretien"}
                />
              </div>

              {/* Estimated Value */}
              {!isNewSubmission && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="text-md font-semibold text-green-800 mb-2">💰 Valeur estimée</h4>
                  <div className="text-2xl font-bold text-green-800">
                    €{detailData.estimated_value}
                  </div>
                  <p className="text-xs text-green-600 mt-1">
                    Basée sur le type, l'état, les caractéristiques et la rareté
                  </p>
                </div>
              )}
            </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-black rounded-lg transition-colors font-medium"
            >
              Annuler
            </button>
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-6 py-2 bg-black hover:bg-gray-800 disabled:opacity-50 text-white rounded-lg transition-colors font-medium"
            >
              {loading ? 'Sauvegarde...' : (isNewSubmission ? 'Soumettre' : 'Sauvegarder')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JerseyDetailEditor;