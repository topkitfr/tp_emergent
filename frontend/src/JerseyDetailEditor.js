import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { JERSEY_DETAIL_CRITERIA, PRICE_FACTORS, BASE_PRICES } from './JerseyDetailCriteria';
import tokenManager from './utils/tokenManager';

const JerseyDetailEditor = ({ jersey, isOpen, onClose, onSave }) => {
  const [detailData, setDetailData] = useState({
    // Jersey reference info (read-only)
    team: jersey?.team || '',
    league: jersey?.league || '',
    season: jersey?.season || '',
    jersey_type: jersey?.jersey_type || '',
    player: jersey?.player || '',
    
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
    
    // Auto-calculated
    estimated_value: 0
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (jersey && isOpen) {
      // Reset to default values first
      setDetailData({
        // Jersey reference info (read-only)
        team: jersey?.team || '',
        league: jersey?.league || '',
        season: jersey?.season || '',
        jersey_type: jersey?.jersey_type || '',
        player: jersey?.player || '',
        
        // Editable collection details - defaults
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
        
        // Auto-calculated
        estimated_value: 0
      });
      
      // Load existing detail data if available
      loadJerseyDetails();
      // Calculate initial estimated value
      calculateEstimatedValue();
    }
  }, [jersey?.id, isOpen]); // Changed dependency to jersey.id for better tracking

  useEffect(() => {
    // Recalculate estimated value when relevant fields change
    calculateEstimatedValue();
  }, [detailData.model_type, detailData.condition, detailData.special_features, detailData.rarity]);

  const loadJerseyDetails = async () => {
    try {
      console.log('Loading jersey details for jersey ID:', jersey?.id);
      const response = await tokenManager.makeAuthenticatedRequest(
        'get',
        `/api/collections/owned/${jersey.id}/details`
      );
      
      if (response.data) {
        console.log('Jersey details loaded:', response.data);
        setDetailData(prev => ({
          ...prev,
          ...response.data
        }));
      } else {
        console.log('No existing jersey details found');
      }
    } catch (error) {
      // Details don't exist yet, use defaults
      console.log('No existing details found, using defaults:', error.message);
    }
  };

  const calculateEstimatedValue = () => {
    let basePrice = BASE_PRICES[detailData.league] || 70;
    
    // Apply model type factor
    const modelFactor = PRICE_FACTORS.model_type[detailData.model_type] || 1.0;
    
    // Apply condition factor
    const conditionFactor = PRICE_FACTORS.condition[detailData.condition] || 1.0;
    
    // Apply special features factor (additive for multiple features)
    let featuresFactor = 1.0;
    if (detailData.special_features?.length > 0) {
      detailData.special_features.forEach(feature => {
        const factor = PRICE_FACTORS.special_features[feature] || 1.0;
        featuresFactor *= factor;
      });
    }
    
    // Apply rarity factor
    const rarityFactor = PRICE_FACTORS.rarity[detailData.rarity] || 1.0;
    
    // Calculate final estimated value
    const estimatedValue = Math.round(basePrice * modelFactor * conditionFactor * featuresFactor * rarityFactor);
    
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

  const handleSpecialFeaturesChange = (feature, checked) => {
    setDetailData(prev => ({
      ...prev,
      special_features: checked
        ? [...(prev.special_features || []), feature]
        : (prev.special_features || []).filter(f => f !== feature)
    }));
  };

  const handleSave = async () => {
    // Validation de base avant de sauvegarder
    if (!jersey || !jersey.id) {
      setError('Erreur: Informations du maillot manquantes');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      console.log('Saving jersey details for jersey ID:', jersey.id, 'Data:', detailData);
      
      const response = await tokenManager.makeAuthenticatedRequest(
        'put',
        `/api/collections/owned/${jersey.id}/details`,
        detailData
      );
      
      console.log('Jersey details saved successfully:', response.data);
      
      if (onSave) {
        onSave(detailData);
      }
      
      onClose();
      
    } catch (error) {
      console.error('Error saving jersey details:', error);
      let errorMessage = 'Failed to save jersey details';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      // Ne pas fermer le modal en cas d'erreur pour que l'utilisateur puisse voir l'erreur
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-black">Éditer les détails du maillot</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-black text-xl font-bold"
            >
              ×
            </button>
          </div>

          {error && (
            <div className="bg-red-500 text-white px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Jersey Reference Info (Read-only) */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-black mb-3">Référence du maillot</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Équipe:</span>
                <span className="text-black ml-2 font-medium">{detailData.team}</span>
              </div>
              <div>
                <span className="text-gray-600">Championnat:</span>
                <span className="text-black ml-2 font-medium">{detailData.league}</span>
              </div>
              <div>
                <span className="text-gray-600">Saison:</span>
                <span className="text-black ml-2 font-medium">{detailData.season}</span>
              </div>
              {detailData.player && (
                <div>
                  <span className="text-gray-600">Joueur:</span>
                  <span className="text-black ml-2 font-medium">{detailData.player}</span>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left Column */}
            <div className="space-y-6">
              
              {/* Model Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {JERSEY_DETAIL_CRITERIA.model_type.label}
                </label>
                <select
                  value={detailData.model_type}
                  onChange={(e) => handleInputChange('model_type', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.model_type.options.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Condition */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {JERSEY_DETAIL_CRITERIA.condition.label}
                </label>
                <select
                  value={detailData.condition}
                  onChange={(e) => handleInputChange('condition', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.condition.options.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {JERSEY_DETAIL_CRITERIA.size.label}
                </label>
                <select
                  value={detailData.size}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.size.options.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Rarity */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {JERSEY_DETAIL_CRITERIA.rarity.label}
                </label>
                <select
                  value={detailData.rarity}
                  onChange={(e) => handleInputChange('rarity', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.rarity.options.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Purchase Information */}
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="text-md font-semibold text-black mb-3">Informations d'achat</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Prix d'achat (€)</label>
                    <input
                      type="number"
                      value={detailData.purchase_price}
                      onChange={(e) => handleInputChange('purchase_price', e.target.value)}
                      className="w-full p-2 bg-white text-black border border-gray-300 rounded focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date d'achat</label>
                    <input
                      type="date"
                      value={detailData.purchase_date}
                      onChange={(e) => handleInputChange('purchase_date', e.target.value)}
                      className="w-full p-2 bg-white text-black border border-gray-300 rounded focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Lieu d'achat</label>
                    <input
                      type="text"
                      value={detailData.purchase_location}
                      onChange={(e) => handleInputChange('purchase_location', e.target.value)}
                      className="w-full p-2 bg-white text-black border border-gray-300 rounded focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                      placeholder="Magasin, site web, marketplace..."
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={detailData.certificate_authenticity}
                      onChange={(e) => handleInputChange('certificate_authenticity', e.target.checked)}
                      className="w-4 h-4 text-black bg-white border-gray-300 rounded focus:ring-black"
                    />
                    <label className="ml-2 text-sm font-medium text-gray-700">Certificat d'authenticité</label>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              
              {/* Special Features */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  {JERSEY_DETAIL_CRITERIA.special_features.label}
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto bg-gray-50 p-3 rounded-lg border border-gray-200">
                  {JERSEY_DETAIL_CRITERIA.special_features.options.map(option => (
                    <div key={option.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={(detailData.special_features || []).includes(option.value)}
                        onChange={(e) => handleSpecialFeaturesChange(option.value, e.target.checked)}
                        className="w-4 h-4 text-black bg-white border-gray-300 rounded focus:ring-black"
                      />
                      <label className="ml-2 text-sm text-gray-700">{option.label}</label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Customization */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {JERSEY_DETAIL_CRITERIA.customization.label}
                </label>
                <select
                  value={detailData.customization}
                  onChange={(e) => handleInputChange('customization', e.target.value)}
                  className="w-full p-3 bg-white text-black border border-gray-300 rounded-lg focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                >
                  {JERSEY_DETAIL_CRITERIA.customization.options.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Storage Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
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
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="text-md font-semibold text-green-800 mb-2">💰 Valeur estimée</h4>
                <div className="text-2xl font-bold text-green-800">
                  €{detailData.estimated_value}
                </div>
                <p className="text-xs text-green-600 mt-1">
                  Basée sur le type, l'état, les caractéristiques et la rareté
                </p>
              </div>
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
              {loading ? 'Sauvegarde...' : 'Sauvegarder'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JerseyDetailEditor;