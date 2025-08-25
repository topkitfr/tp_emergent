import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ContributionModal from '../ContributionModal';

const CompetitionDetailPage = ({ user, API, competitions, onDataUpdate }) => {
  const { competitionId } = useParams();
  const navigate = useNavigate();
  const [competition, setCompetition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [secondaryImages, setSecondaryImages] = useState([]);

  useEffect(() => {
    if (competitions && competitionId) {
      const foundCompetition = competitions.find(c => c.id === competitionId);
      setCompetition(foundCompetition);
      setLoading(false);
      
      // Charger les images secondaires depuis le champ secondary_images
      if (foundCompetition && foundCompetition.secondary_images) {
        setSecondaryImages(foundCompetition.secondary_images.filter(Boolean));
      }
    }
  }, [competitions, competitionId]);

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

  if (!competition) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Ligue non trouvée</h2>
        <button 
          onClick={() => navigate('/competitions')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
        >
          Retour aux ligues
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header avec boutons */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{competition.name}</h1>
          {competition.official_name && competition.official_name !== competition.name && (
            <p className="text-xl text-gray-600 mb-2">{competition.official_name}</p>
          )}
          <p className="text-blue-600 font-mono">{competition.topkit_reference}</p>
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
            onClick={() => navigate('/competitions')}
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
            {competition.logo_url ? (
              <img 
                src={competition.logo_url.startsWith('data:') || competition.logo_url.startsWith('http') ? competition.logo_url : `${API}/${competition.logo_url}`}
                alt={`${competition.name} logo`}
                className="w-full h-full object-contain p-8"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div className="text-6xl flex items-center justify-center w-full h-full" style={{display: competition.logo_url ? 'none' : 'flex'}}>
              🏆
            </div>
          </div>
        </div>

        {/* Informations à droite */}
        <div className="space-y-6">
          <div>
            <div className="grid grid-cols-1 gap-4 text-lg">
              <div>
                <span className="font-semibold text-gray-700">Pays :</span>
                <span className="ml-2 text-gray-900">{competition.country || 'International'}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Type :</span>
                <span className="ml-2 text-gray-900 capitalize">{competition.competition_type || 'Non spécifié'}</span>
              </div>
              
              {competition.founded_year && (
                <div>
                  <span className="font-semibold text-gray-700">Fondation :</span>
                  <span className="ml-2 text-gray-900">{competition.founded_year}</span>
                </div>
              )}
              
              {competition.current_season && (
                <div>
                  <span className="font-semibold text-gray-700">Saison actuelle :</span>
                  <span className="ml-2 text-gray-900">{competition.current_season}</span>
                </div>
              )}
              
              <div>
                <span className="font-semibold text-gray-700">Maillots référencés :</span>
                <span className="ml-2 text-gray-900">{competition.jerseys_count || 0}</span>
              </div>
              
              <div>
                <span className="font-semibold text-gray-700">Collectionneurs :</span>
                <span className="ml-2 text-gray-900">{competition.collectors_count || 0}</span>
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
                  alt={`${competition.name} - Image ${index + 1}`}
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

      {/* Description */}
      {competition.description && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-3">Description</h3>
          <p className="text-gray-700 leading-relaxed">{competition.description}</p>
        </div>
      )}

      {/* Informations complémentaires */}
      {(competition.participating_countries && competition.participating_countries.length > 0) && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-3">Pays participants</h3>
          <div className="flex flex-wrap gap-2">
            {competition.participating_countries.map((country, index) => (
              <span key={index} className="bg-white text-gray-700 px-3 py-1 rounded-full text-sm border">
                🌍 {country}
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
                competition.verified_level !== 'unverified' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {competition.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
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
          entity={competition}
          entityType="competition"
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

export default CompetitionDetailPage;