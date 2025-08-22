import React, { useState, useEffect } from 'react';
import ContributionModal from '../ContributionModal';

const CollaborativeExplorePage = ({ 
  user, 
  API, 
  teams, 
  brands, 
  players, 
  competitions, 
  masterJerseys, 
  searchQuery 
}) => {
  const [searchResults, setSearchResults] = useState({
    teams: [],
    brands: [],
    players: [],
    competitions: [],
    master_jerseys: []
  });
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(false);
  
  // États pour les modales de détails
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedCompetition, setSelectedCompetition] = useState(null);
  const [selectedMasterJersey, setSelectedMasterJersey] = useState(null);
  
  // États pour les contributions
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedEntityForContribution, setSelectedEntityForContribution] = useState(null);
  const [contributionEntityType, setContributionEntityType] = useState('');

  // Perform search when searchQuery changes
  useEffect(() => {
    if (searchQuery && searchQuery.length > 2) {
      performSearch(searchQuery);
    } else {
      // Show recent data when no search
      setSearchResults({
        teams: teams.slice(0, 8),
        brands: brands.slice(0, 6),
        players: players.slice(0, 8),
        competitions: competitions.slice(0, 6),
        master_jerseys: masterJerseys.slice(0, 12)
      });
    }
  }, [searchQuery, teams, brands, players, competitions, masterJerseys]);

  const performSearch = async (query) => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/search/collaborative?q=${encodeURIComponent(query)}&limit=50`);
      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
      }
    } catch (error) {
      console.error('Search error:', error);
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'all', label: 'Tout', icon: '🔍' },
    { id: 'teams', label: 'Équipes', icon: '⚽' },
    { id: 'brands', label: 'Marques', icon: '👕' },
    { id: 'players', label: 'Joueurs', icon: '👤' },
    { id: 'competitions', label: 'Compétitions', icon: '🏆' },
    { id: 'master_jerseys', label: 'Maillots', icon: '📋' }
  ];

  const getTotalResults = () => {
    return Object.values(searchResults).reduce((total, results) => total + (results?.length || 0), 0);
  };

  const TeamCard = ({ team }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all cursor-pointer group"
      onClick={() => setSelectedTeam(team)}
    >
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-lg">⚽</span>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{team.name}</h3>
          {team.short_name && <p className="text-sm text-gray-500">{team.short_name}</p>}
        </div>
      </div>
      <div className="text-sm space-y-1">
        <div className="flex items-center text-gray-600">
          <span className="mr-2">🌍</span>
          <span>{team.country}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-blue-600 font-mono text-xs">{team.topkit_reference}</span>
          {team.verified_level !== 'unverified' && (
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">✓</span>
          )}
        </div>
      </div>
    </div>
  );

  const BrandCard = ({ brand }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all">
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
          <span className="text-lg">👕</span>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{brand.name}</h3>
          {brand.country && <p className="text-sm text-gray-500">{brand.country}</p>}
        </div>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-blue-600 font-mono text-xs">{brand.topkit_reference}</span>
        {brand.verified_level !== 'unverified' && (
          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">✓</span>
        )}
      </div>
    </div>
  );

  const PlayerCard = ({ player }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all">
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
          <span className="text-lg">👤</span>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{player.name}</h3>
          {player.nationality && <p className="text-sm text-gray-500">{player.nationality}</p>}
        </div>
      </div>
      <div className="text-sm space-y-1">
        {player.position && (
          <div className="flex items-center text-gray-600">
            <span className="mr-2">⚽</span>
            <span>{player.position}</span>
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-blue-600 font-mono text-xs">{player.topkit_reference}</span>
          {player.verified_level !== 'unverified' && (
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">✓</span>
          )}
        </div>
      </div>
    </div>
  );

  const CompetitionCard = ({ competition }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all">
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
          <span className="text-lg">🏆</span>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{competition.name}</h3>
          {competition.country && <p className="text-sm text-gray-500">{competition.country}</p>}
        </div>
      </div>
      <div className="text-sm space-y-1">
        <div className="flex items-center text-gray-600">
          <span className="mr-2">📋</span>
          <span className="capitalize">{competition.competition_type?.replace('_', ' ')}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-blue-600 font-mono text-xs">{competition.topkit_reference}</span>
          {competition.verified_level !== 'unverified' && (
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">✓</span>
          )}
        </div>
      </div>
    </div>
  );

  const MasterJerseyCard = ({ jersey }) => (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-all">
      <div className="aspect-square bg-gray-100 flex items-center justify-center">
        <span className="text-4xl">👕</span>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-sm text-gray-900 mb-2">
          {jersey.team_info?.name || 'Équipe inconnue'}
        </h3>
        <div className="text-xs space-y-1 mb-3">
          <div className="flex items-center text-gray-600">
            <span className="mr-1">⚽</span>
            <span>{jersey.season}</span>
            <span className="ml-2 capitalize">{jersey.jersey_type}</span>
          </div>
          <div className="flex items-center text-gray-600">
            <span className="mr-1">👕</span>
            <span>{jersey.brand_info?.name || 'Marque inconnue'}</span>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-blue-600 font-mono text-xs">{jersey.topkit_reference}</span>
          <div className="text-xs text-gray-500">
            {jersey.releases_count || 0} versions
          </div>
        </div>
      </div>
    </div>
  );

  const renderResults = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Recherche en cours...</span>
        </div>
      );
    }

    if (activeTab === 'all') {
      return (
        <div className="space-y-8">
          {/* Teams */}
          {searchResults.teams && searchResults.teams.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">⚽</span>
                Équipes ({searchResults.teams.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {searchResults.teams.map(team => (
                  <TeamCard key={team.id} team={team} />
                ))}
              </div>
            </div>
          )}

          {/* Brands */}
          {searchResults.brands && searchResults.brands.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">👕</span>
                Marques ({searchResults.brands.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {searchResults.brands.map(brand => (
                  <BrandCard key={brand.id} brand={brand} />
                ))}
              </div>
            </div>
          )}

          {/* Players */}
          {searchResults.players && searchResults.players.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">👤</span>
                Joueurs ({searchResults.players.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {searchResults.players.map(player => (
                  <PlayerCard key={player.id} player={player} />
                ))}
              </div>
            </div>
          )}

          {/* Competitions */}
          {searchResults.competitions && searchResults.competitions.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">🏆</span>
                Compétitions ({searchResults.competitions.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {searchResults.competitions.map(competition => (
                  <CompetitionCard key={competition.id} competition={competition} />
                ))}
              </div>
            </div>
          )}

          {/* Master Jerseys */}
          {searchResults.master_jerseys && searchResults.master_jerseys.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">📋</span>
                Maillots ({searchResults.master_jerseys.length})
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {searchResults.master_jerseys.map(jersey => (
                  <MasterJerseyCard key={jersey.id} jersey={jersey} />
                ))}
              </div>
            </div>
          )}
        </div>
      );
    } else {
      // Single category view
      const categoryResults = searchResults[activeTab] || [];
      const renderCard = {
        teams: (item) => <TeamCard key={item.id} team={item} />,
        brands: (item) => <BrandCard key={item.id} brand={item} />,
        players: (item) => <PlayerCard key={item.id} player={item} />,
        competitions: (item) => <CompetitionCard key={item.id} competition={item} />,
        master_jerseys: (item) => <MasterJerseyCard key={item.id} jersey={item} />
      };

      const gridCols = {
        teams: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
        brands: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
        players: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
        competitions: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
        master_jerseys: 'grid-cols-2 md:grid-cols-4 lg:grid-cols-6'
      };

      return (
        <div className={`grid ${gridCols[activeTab]} gap-4`}>
          {categoryResults.map(renderCard[activeTab])}
        </div>
      );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {searchQuery ? `Résultats pour "${searchQuery}"` : 'Explorer la base de données'}
        </h1>
        <p className="text-gray-600">
          {searchQuery 
            ? `${getTotalResults()} résultat${getTotalResults() > 1 ? 's' : ''} trouvé${getTotalResults() > 1 ? 's' : ''}`
            : 'Découvrez les équipes, marques, joueurs et maillots de la communauté TopKit'
          }
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-gray-200 p-1 mb-8">
        <div className="flex flex-wrap gap-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
              {activeTab !== 'all' && tab.id !== 'all' && searchResults[tab.id] && (
                <span className="ml-2 bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs">
                  {searchResults[tab.id].length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="min-h-[400px]">
        {getTotalResults() > 0 ? (
          renderResults()
        ) : (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchQuery ? 'Aucun résultat trouvé' : 'Commencez votre exploration'}
            </h3>
            <p className="text-gray-600">
              {searchQuery 
                ? `Aucun résultat pour "${searchQuery}". Essayez avec d'autres mots-clés.`
                : 'Utilisez la barre de recherche pour explorer la base de données collaborative.'
              }
            </p>
          </div>
        )}
      </div>

    </div>
  );
};

export default CollaborativeExplorePage;