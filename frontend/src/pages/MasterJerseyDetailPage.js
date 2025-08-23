import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ContributionModal from '../ContributionModal';

const MasterJerseyDetailPage = ({ user, API, masterJerseys, onDataUpdate }) => {
  const { jerseyId } = useParams();
  const navigate = useNavigate();
  const [jersey, setJersey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [secondaryImages, setSecondaryImages] = useState([]);

  useEffect(() => {
    if (masterJerseys && jerseyId) {
      const foundJersey = masterJerseys.find(j => j.id === jerseyId);
      setJersey(foundJersey);
      setLoading(false);
      
      // Charger les images secondaires depuis le champ secondary_images
      if (foundJersey && foundJersey.secondary_images) {
        setSecondaryImages(foundJersey.secondary_images.filter(Boolean));
      }
    }
  }, [masterJerseys, jerseyId]);

  const getJerseyTypeLabel = (type) => {
    const labels = {
      'home': 'Domicile',
      'away': 'Extérieur',
      'third': 'Troisième',
      'goalkeeper': 'Gardien',
      'training': 'Entraînement',
      'special': 'Spécial'
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/4 mb-8"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="aspect-square bg-gray-300 rounded-lg"></div>
            <div className="space-y-4">
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              <div className="h-4 bg-gray-300 rounded w-1/2"></div>
              <div className="h-4 bg-gray-300 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!jersey) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Master Jersey non trouvé</h2>
        <button 
          onClick={() => navigate('/master-jerseys')}
          className="bg-blue-600 hover:blue-blue-700 text-white px-6 py-2 rounded-lg"
        >
          Retour aux Master Jerseys
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header avec boutons */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {jersey.team_info?.name || 'Équipe inconnue'} {jersey.season}
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            {getJerseyTypeLabel(jersey.jersey_type)} - {jersey.brand_info?.name || 'Marque inconnue'}
          </p>
          <p className="text-blue-600 font-mono">{jersey.topkit_reference}</p>
        </div>
        
        <div className="flex gap-3">
          {user && (
            <button
              onClick={() => setShowContributionModal(true)}
              className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
            >
              ✏️ Améliorer cette fiche
            </button>
          )}
          <button
            onClick={() => navigate('/master-jerseys')}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Image principale à gauche */}
        <div>
          <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center border border-gray-200">
            {jersey.main_image_url ? (
              <img 
                src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `${API}/${jersey.main_image_url}`}
                alt={`${jersey.team_info?.name} ${jersey.season}`}
                className="w-full h-full object-contain p-8"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div className="text-6xl flex items-center justify-center w-full h-full" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>
              👕
            </div>
          </div>
        </div>

        {/* Informations à droite */}
        <div className="space-y-6">
          <div>
            <div className="grid grid-cols-1 gap-4 text-lg">
              <div>
                <span className="font-semibold text-gray-700">Équipe :</span>
                <span className="ml-2 text-gray-900">{jersey.team_info?.name || 'Non spécifié'}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Marque :</span>
                <span className="ml-2 text-gray-900">{jersey.brand_info?.name || 'Non spécifié'}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Saison :</span>
                <span className="ml-2 text-gray-900">{jersey.season}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Type :</span>
                <span className="ml-2 text-gray-900">{getJerseyTypeLabel(jersey.jersey_type)}</span>
              </div>
              
              {jersey.design_name && (
                <div>
                  <span className="font-semibold text-gray-700">Design :</span>
                  <span className="ml-2 text-gray-900">{jersey.design_name}</span>
                </div>
              )}
              
              {jersey.main_sponsor && (
                <div>
                  <span className="font-semibold text-gray-700">Sponsor :</span>
                  <span className="ml-2 text-gray-900">{jersey.main_sponsor}</span>
                </div>
              )}
              
              <div>
                <span className="font-semibold text-gray-700">Couleur :</span>
                <div className="ml-2 flex items-center gap-2">
                  {jersey.primary_color ? (
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-5 h-5 rounded-full border border-gray-300"
                        style={{ backgroundColor: jersey.primary_color }}
                        title={jersey.primary_color}
                      ></div>
                      <span className="capitalize text-gray-900">{jersey.primary_color}</span>
                      {jersey.secondary_colors && jersey.secondary_colors.length > 0 && (
                        <>
                          {jersey.secondary_colors.slice(0, 2).map((color, index) => (
                            <div key={index} className="flex items-center space-x-1">
                              <div
                                className="w-4 h-4 rounded-full border border-gray-300"
                                style={{ backgroundColor: color }}
                                title={color}
                              ></div>
                              <span className="text-sm capitalize text-gray-600">{color}</span>
                            </div>
                          ))}
                          {jersey.secondary_colors.length > 2 && (
                            <span className="text-sm text-gray-500">+{jersey.secondary_colors.length - 2}</span>
                          )}
                        </>
                      )}
                    </div>
                  ) : (
                    <span className="text-gray-900">Non spécifié</span>
                  )}
                </div>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Maillots référencés :</span>
                <span className="ml-2 text-gray-900">{jersey.releases_count || 0}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Collectionneurs :</span>
                <span className="ml-2 text-gray-900">{jersey.collectors_count || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section Images secondaires */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Images secondaires</h3>
        {secondaryImages.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {secondaryImages.slice(0, 3).map((image, index) => (
              <div key={index} className="aspect-video bg-gray-100 rounded-lg border border-gray-200 overflow-hidden">
                <img 
                  src={image.startsWith('data:') || image.startsWith('http') ? image : `${API}/${image}`}
                  alt={`${jersey.team_info?.name} ${jersey.season} - Image ${index + 1}`}
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="flex items-center justify-center w-full h-full text-2xl text-gray-400" style={{display: 'none'}}>
                  🖼️
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🖼️</div>
            <p>Aucune image secondaire disponible</p>
          </div>
        )}
      </div>

      {/* Description du motif */}
      {jersey.pattern_description && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-3">Description du motif</h3>
          <p className="text-gray-700 leading-relaxed">{jersey.pattern_description}</p>
        </div>
      )}

      {/* Caractéristiques spéciales */}
      {(jersey.special_features && jersey.special_features.length > 0) && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-3">Caractéristiques spéciales</h3>
          <div className="flex flex-wrap gap-2">
            {jersey.special_features.map((feature, index) => (
              <span key={index} className="bg-white text-gray-700 px-3 py-1 rounded-full text-sm border">
                ⭐ {feature}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Statut de vérification */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Statut de vérification</h3>
            <div className="flex items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                jersey.verified_level !== 'unverified' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {jersey.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Contribution Modal */}
      {showContributionModal && (
        <ContributionModal
          isOpen={showContributionModal}
          onClose={() => setShowContributionModal(false)}
          entity={jersey}
          entityType="master_jersey"
          onContributionCreated={(newContribution) => {
            console.log('Contribution créée:', newContribution);
            if (onDataUpdate) {
              onDataUpdate();
            }
          }}
        />
      )}
    </div>
  );
};

export default MasterJerseyDetailPage;