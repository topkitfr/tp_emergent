import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ContributionModal from '../ContributionModal';

const BrandDetailPage = ({ user, API, brands, masterJerseys, onDataUpdate }) => {
  const { brandId } = useParams();
  const navigate = useNavigate();
  const [brand, setBrand] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [secondaryImages, setSecondaryImages] = useState([]);
  const [relatedMasterKits, setRelatedMasterKits] = useState([]);

  useEffect(() => {
    if (brands && brandId) {
      const foundBrand = brands.find(b => b.id === brandId);
      setBrand(foundBrand);
      setLoading(false);
      
      // Charger les images secondaires depuis le champ secondary_images
      if (foundBrand && foundBrand.secondary_images) {
        setSecondaryImages(foundBrand.secondary_images.filter(Boolean));
      }

      // Find related Master Kits for this brand
      if (foundBrand && masterJerseys) {
        const brandRelatedKits = masterJerseys.filter(kit => 
          kit.brand_id === foundBrand.id || 
          kit.brand === foundBrand.name ||
          kit.brand_name === foundBrand.name
        ).slice(0, 5); // Limit to 5 kits
        setRelatedMasterKits(brandRelatedKits);
      }
    }
  }, [brands, brandId, masterJerseys]);

  const handleSeeMoreClick = () => {
    if (brand) {
      // Navigate to Kit Area with brand filter
      navigate(`/kit-area?brand=${encodeURIComponent(brand.name)}`);
    }
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

  if (!brand) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Marque non trouvée</h2>
        <button 
          onClick={() => navigate('/catalogue')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
        >
          Retour au catalogue
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header avec boutons */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{brand.name}</h1>
          {brand.official_name && brand.official_name !== brand.name && (
            <p className="text-xl text-gray-600 mb-2">{brand.official_name}</p>
          )}
          <p className="text-blue-600 font-mono">{brand.topkit_reference}</p>
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
            onClick={() => navigate('/catalogue')}
            className="text-gray-400 hover:text-gray-600 text-2xl"
            title="Retour au catalogue"
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
            {brand.logo_url ? (
              <img 
                src={brand.logo_url.startsWith('image_uploaded_') 
                  ? `${API}/api/legacy-image/${brand.logo_url}` 
                  : brand.logo_url.startsWith('data:') || brand.logo_url.startsWith('http') 
                    ? brand.logo_url 
                    : `${API}/api/${brand.logo_url}`}
                alt={`${brand.name} logo`}
                className="w-full h-full object-contain p-8"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div className="text-6xl flex items-center justify-center w-full h-full" style={{display: brand.logo_url ? 'none' : 'flex'}}>
              👕
            </div>
          </div>
        </div>

        {/* Informations à droite */}
        <div className="space-y-6">
          <div>
            <div className="grid grid-cols-1 gap-4 text-lg">
              <div>
                <span className="font-semibold text-gray-700">Pays :</span>
                <span className="ml-2 text-gray-900">{brand.country || 'Non spécifié'}</span>
              </div>
              
              {brand.founded_year && (
                <div>
                  <span className="font-semibold text-gray-700">Fondation :</span>
                  <span className="ml-2 text-gray-900">{brand.founded_year}</span>
                </div>
              )}
              
              {brand.website && (
                <div>
                  <span className="font-semibold text-gray-700">Site web :</span>
                  <a href={brand.website} target="_blank" rel="noopener noreferrer" className="ml-2 text-blue-600 hover:text-blue-800">
                    {brand.website}
                  </a>
                </div>
              )}
              
              <div>
                <span className="font-semibold text-gray-700">Maillots référencés :</span>
                <span className="ml-2 text-gray-900">{relatedMasterKits.length}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Collectionneurs :</span>
                <span className="ml-2 text-gray-900">{brand.collectors_count || 0}</span>
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
                  src={image.startsWith('image_uploaded_') 
                    ? `${API}/api/legacy-image/${image}` 
                    : image.startsWith('data:') || image.startsWith('http') 
                      ? image 
                      : `${API}/api/${image}`}
                  alt={`${brand.name} - Image ${index + 1}`}
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

      {/* Section Maillots associés */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Maillots associés</h3>
          {relatedMasterKits.length > 0 && (
            <button
              onClick={handleSeeMoreClick}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Voir tout ({relatedMasterKits.length}) →
            </button>
          )}
        </div>
        
        {relatedMasterKits.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {relatedMasterKits.map((kit) => (
              <div 
                key={kit.id}
                onClick={() => navigate(`/master-kits/${kit.id}`)}
                className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-200 cursor-pointer group"
              >
                <div className="relative w-full h-32 bg-gray-100 rounded-t-lg overflow-hidden flex items-center justify-center">
                  {kit.front_photo_url ? (
                    <img 
                      src={kit.front_photo_url.startsWith('http') 
                        ? kit.front_photo_url 
                        : `${API}/api/${kit.front_photo_url}`}
                      alt={`${kit.club} ${kit.season} ${kit.kit_type}`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: kit.front_photo_url ? 'none' : 'flex'}}>
                    👕
                  </div>
                </div>
                
                <div className="p-3">
                  <h4 className="font-bold text-sm text-gray-900 mb-1 group-hover:text-blue-600 line-clamp-2">
                    {kit.club} {kit.season}
                  </h4>
                  <div className="text-xs text-gray-600 mb-2">
                    <div className="capitalize">{kit.kit_type}</div>
                    <div>{kit.brand}</div>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-blue-600 font-mono truncate">{kit.topkit_reference}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">👕</div>
            <p>Aucun maillot associé à cette marque</p>
            <p className="text-sm mt-1">Les maillots apparaîtront ici une fois référencés</p>
          </div>
        )}
      </div>

      {/* Informations complémentaires */}
      {(brand.common_names && brand.common_names.length > 0) && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-3">Noms alternatifs</h3>
          <div className="flex flex-wrap gap-2">
            {brand.common_names.map((name, index) => (
              <span key={index} className="bg-white text-gray-700 px-3 py-1 rounded-full text-sm border">
                {name}
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
                brand.verified_level !== 'unverified' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {brand.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
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
          entity={brand}
          entityType="brand"
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

export default BrandDetailPage;