import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { JERSEY_DETAIL_CRITERIA, PRICE_FACTORS, BASE_PRICES } from './JerseyDetailCriteria';
import tokenManager from './utils/tokenManager';

const JerseyDetailEditor = ({ jersey, isOpen, onClose, onSave, onUpdateSuccess }) => {
  const [detailData, setDetailData] = useState({
    // Jersey basic info (editable for new submissions, read-only for existing)
    team: '',
    league: '',
    season: '',
    jersey_type: '',
    player: '',
    manufacturer: '',
    home_away: 'home',
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

  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Check if this is a new submission
  const isNewSubmission = jersey?.isNewSubmission || false;
  const isAdminEdit = jersey?.isAdminEdit || false;

  useEffect(() => {
    if (jersey && isOpen) {
      // Reset to jersey data or defaults
      setDetailData({
        // Jersey basic info
        team: jersey?.team || '',
        league: jersey?.league || '',
        season: jersey?.season || '',
        jersey_type: jersey?.jersey_type || '',
        player: jersey?.player || '',
        manufacturer: jersey?.manufacturer || '',
        home_away: jersey?.home_away || 'home',
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
      
      // Clear photo previews
      setPhotoPreview({
        front: null,
        back: null
      });
      
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
      
      if (isNewSubmission) {
        // Validation for new submissions
        if (!detailData.team || !detailData.league || !detailData.season) {
          setError('Veuillez remplir les champs obligatoires: Équipe, Ligue, et Saison');
          return;
        }
        
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
              {isNewSubmission ? '📝 Soumettre un maillot' : (isAdminEdit ? '✏️ Modifier le maillot' : '✏️ Modifier les détails')}
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

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Basic Info */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-black border-b border-gray-200 pb-2">
                📋 Informations de base
              </h3>

              {/* Team */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Équipe *
                </label>
                <input
                  type="text"
                  value={detailData.team}
                  onChange={(e) => handleInputChange('team', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: Paris Saint-Germain"
                />
              </div>

              {/* League */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Ligue/Championnat *
                </label>
                <input
                  type="text"
                  value={detailData.league}
                  onChange={(e) => handleInputChange('league', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: Ligue 1"
                />
              </div>

              {/* Season */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Saison *
                </label>
                <input
                  type="text"
                  value={detailData.season}
                  onChange={(e) => handleInputChange('season', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: 2023-24"
                />
              </div>

              {/* Jersey Type */}
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
                  <option value="">Sélectionner...</option>
                  <option value="home">Domicile</option>
                  <option value="away">Extérieur</option>
                  <option value="third">Troisième</option>
                  <option value="goalkeeper">Gardien</option>
                  <option value="training">Entraînement</option>
                  <option value="special">Édition spéciale</option>
                </select>
              </div>

              {/* Player */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Joueur (optionnel)
                </label>
                <input
                  type="text"
                  value={detailData.player}
                  onChange={(e) => handleInputChange('player', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                  placeholder="Ex: Mbappé"
                />
              </div>

              {/* Manufacturer */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Fabricant
                </label>
                <select
                  value={detailData.manufacturer}
                  onChange={(e) => handleInputChange('manufacturer', e.target.value)}
                  disabled={!isNewSubmission}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-100 disabled:text-gray-600"
                >
                  <option value="">Sélectionner...</option>
                  <option value="nike">Nike</option>
                  <option value="adidas">Adidas</option>
                  <option value="puma">Puma</option>
                  <option value="jordan">Jordan</option>
                  <option value="umbro">Umbro</option>
                  <option value="kappa">Kappa</option>
                  <option value="new_balance">New Balance</option>
                  <option value="other">Autre</option>
                </select>
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

            {/* Right Column - Detail Info */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-black border-b border-gray-200 pb-2">
                🔍 Détails de la collection
              </h3>

              {/* Model Type */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.model_type.label}
                </label>
                <select
                  value={detailData.model_type}
                  onChange={(e) => handleInputChange('model_type', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {Object.entries(JERSEY_DETAIL_CRITERIA.model_type.options).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Condition */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.condition.label}
                </label>
                <select
                  value={detailData.condition}
                  onChange={(e) => handleInputChange('condition', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {Object.entries(JERSEY_DETAIL_CRITERIA.condition.options).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.size.label}
                </label>
                <select
                  value={detailData.size}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {Object.entries(JERSEY_DETAIL_CRITERIA.size.options).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Special Features */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.special_features.label}
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {JERSEY_DETAIL_CRITERIA.special_features.options.map((feature) => (
                    <label key={feature} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={(detailData.special_features || []).includes(feature)}
                        onChange={() => handleSpecialFeatureToggle(feature)}
                        className="w-4 h-4 text-black bg-white border-gray-300 rounded focus:ring-black focus:ring-2"
                      />
                      <span className="text-sm text-black">{feature}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Rarity */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.rarity.label}
                </label>
                <select
                  value={detailData.rarity}
                  onChange={(e) => handleInputChange('rarity', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {Object.entries(JERSEY_DETAIL_CRITERIA.rarity.options).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.tags.label}
                </label>
                <select
                  value={detailData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {Object.entries(JERSEY_DETAIL_CRITERIA.tags.options).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Purchase Price */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.purchase_price.label}
                </label>
                <input
                  type="number"
                  value={detailData.purchase_price}
                  onChange={(e) => handleInputChange('purchase_price', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                  placeholder={JERSEY_DETAIL_CRITERIA.purchase_price.placeholder}
                />
              </div>

              {/* Purchase Date */}
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  {JERSEY_DETAIL_CRITERIA.purchase_date.label}
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
                  {JERSEY_DETAIL_CRITERIA.storage_notes.label}
                </label>
                <textarea
                  value={detailData.storage_notes}
                  onChange={(e) => handleInputChange('storage_notes', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black h-24"
                  placeholder={JERSEY_DETAIL_CRITERIA.storage_notes.placeholder}
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