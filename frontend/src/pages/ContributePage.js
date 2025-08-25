import React, { useState } from 'react';
import ContributionModal from '../ContributionModal';

const ContributePage = ({ 
  user, 
  API, 
  teams, 
  brands, 
  players, 
  competitions, 
  masterJerseys, 
  onDataUpdate 
}) => {
  const [selectedContributionType, setSelectedContributionType] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const contributionTypes = [
    {
      id: 'team',
      title: 'Équipes',
      icon: '⚽',
      description: 'Ajouter ou améliorer une fiche d\'équipe',
      color: 'bg-blue-50 border-blue-200 hover:bg-blue-100',
      textColor: 'text-blue-700',
      fields: 'Nom, ville, pays, couleurs, année de fondation...'
    },
    {
      id: 'brand',
      title: 'Marques',
      icon: '👕',
      description: 'Documenter un fabricant de maillots',
      color: 'bg-green-50 border-green-200 hover:bg-green-100',
      textColor: 'text-green-700',
      fields: 'Nom, pays d\'origine, site web, logo...'
    },
    {
      id: 'player',
      title: 'Joueurs',
      icon: '👤',
      description: 'Ajouter ou corriger les informations d\'un joueur',
      color: 'bg-purple-50 border-purple-200 hover:bg-purple-100',
      textColor: 'text-purple-700',
      fields: 'Nom, nationalité, poste, date de naissance...'
    },
    {
      id: 'competition',
      title: 'Ligues',
      icon: '🏆',
      description: 'Référencer un championnat ou une coupe',
      color: 'bg-yellow-50 border-yellow-200 hover:bg-yellow-100',
      textColor: 'text-yellow-700',
      fields: 'Nom, pays, type, niveau, saison actuelle...'
    },
    {
      id: 'master_jersey',
      title: 'Master Jerseys',
      icon: '📋',
      description: 'Documenter un design de maillot',
      color: 'bg-red-50 border-red-200 hover:bg-red-100',
      textColor: 'text-red-700',
      fields: 'Équipe, marque, saison, couleurs, sponsors...'
    }
  ];

  const handleEntitySelect = (entity, type) => {
    setSelectedEntity(entity);
    setSelectedContributionType(type);
    setShowContributionModal(true);
  };

  const getEntitiesForType = (type) => {
    switch (type) {
      case 'team':
        return teams || [];
      case 'brand':
        return brands || [];
      case 'player':
        return players || [];
      case 'competition':
        return competitions || [];
      case 'master_jersey':
        return masterJerseys || [];
      default:
        return [];
    }
  };

  const filteredEntities = selectedContributionType 
    ? getEntitiesForType(selectedContributionType).filter(entity =>
        entity.name?.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 20)
    : [];

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-6xl mb-4">✏️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Contribuer à TopKit</h2>
          <p className="text-gray-600 mb-6">
            Connectez-vous pour contribuer à notre base de données collaborative
          </p>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
            Se connecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ✏️ Contribuer à TopKit
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Aidez-nous à enrichir la base de données collaborative la plus complète 
              sur le football en ajoutant ou améliorant des informations
            </p>
          </div>

          {/* User contribution stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">12</div>
              <div className="text-sm text-blue-700">Contributions soumises</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">8</div>
              <div className="text-sm text-green-700">Contributions approuvées</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">⭐ Expert</div>
              <div className="text-sm text-purple-700">Niveau contributeur</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {!selectedContributionType ? (
          /* Step 1: Choose contribution type */
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Que souhaitez-vous documenter ?
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contributionTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedContributionType(type.id)}
                  className={`p-6 rounded-lg border-2 transition-all text-left ${type.color}`}
                >
                  <div className="flex items-start space-x-4">
                    <div className="text-3xl">{type.icon}</div>
                    <div className="flex-1">
                      <h3 className={`font-bold text-lg mb-2 ${type.textColor}`}>
                        {type.title}
                      </h3>
                      <p className="text-gray-700 mb-3">{type.description}</p>
                      <p className="text-sm text-gray-600">
                        <strong>Champs :</strong> {type.fields}
                      </p>
                      <div className="mt-4 flex justify-between items-center">
                        <span className={`text-sm font-medium ${type.textColor}`}>
                          Commencer →
                        </span>
                        <div className="text-xs text-gray-500">
                          {getEntitiesForType(type.id).length} entrées
                        </div>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Recent contributions */}
            <div className="mt-12">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Dernières contributions de la communauté 🔥
              </h3>
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="space-y-4">
                  {[
                    { type: 'team', name: 'FC Barcelona', action: 'Logo mis à jour', user: 'Marie_K', time: '2h' },
                    { type: 'player', name: 'Kylian Mbappé', action: 'Informations mises à jour', user: 'FootData', time: '4h' },
                    { type: 'brand', name: 'Nike', action: 'Site web ajouté', user: 'Alex_89', time: '6h' }
                  ].map((contrib, index) => (
                    <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl">
                        {contributionTypes.find(t => t.id === contrib.type)?.icon}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{contrib.name}</div>
                        <div className="text-sm text-gray-600">{contrib.action}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-blue-600">{contrib.user}</div>
                        <div className="text-xs text-gray-500">Il y a {contrib.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Step 2: Choose entity to improve or create new */
          <div>
            <div className="flex items-center space-x-4 mb-6">
              <button
                onClick={() => {
                  setSelectedContributionType(null);
                  setSearchQuery('');
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ← Retour
              </button>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">
                  {contributionTypes.find(t => t.id === selectedContributionType)?.icon}
                </span>
                <h2 className="text-2xl font-bold text-gray-900">
                  {contributionTypes.find(t => t.id === selectedContributionType)?.title}
                </h2>
              </div>
            </div>

            {/* Create new entity button */}
            <div className="mb-6">
              <button
                onClick={() => handleEntitySelect(null, selectedContributionType)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg font-medium transition-all"
              >
                + Ajouter une nouvelle entrée
              </button>
            </div>

            {/* Search existing entities */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Ou améliorer une fiche existante
              </h3>
              <input
                type="text"
                placeholder="Rechercher pour améliorer..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Entities list */}
            {searchQuery && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredEntities.map((entity) => (
                  <button
                    key={entity.id}
                    onClick={() => handleEntitySelect(entity, selectedContributionType)}
                    className="bg-white border border-gray-200 p-4 rounded-lg hover:shadow-md transition-shadow text-left"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-xl">
                          {contributionTypes.find(t => t.id === selectedContributionType)?.icon}
                        </span>
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{entity.name}</h4>
                        <p className="text-sm text-gray-600">
                          {entity.country || entity.nationality || 'Informations limitées'}
                        </p>
                        <div className="text-xs text-blue-600 mt-1">
                          {entity.topkit_reference}
                        </div>
                      </div>
                      <div className="text-yellow-600">
                        ✏️
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Contribution Modal */}
      {showContributionModal && (
        <ContributionModal
          isOpen={showContributionModal}
          onClose={() => {
            setShowContributionModal(false);
            setSelectedEntity(null);
          }}
          entity={selectedEntity}
          entityType={selectedContributionType}
          onContributionCreated={(newContribution) => {
            console.log('Contribution créée:', newContribution);
            setShowContributionModal(false);
            setSelectedEntity(null);
            if (onDataUpdate) {
              onDataUpdate();
            }
          }}
        />
      )}

    </div>
  );
};

export default ContributePage;