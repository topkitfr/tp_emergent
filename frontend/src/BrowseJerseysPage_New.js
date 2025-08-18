// Enhanced Browse Jerseys Page with Dark Theme - Same style as Marketplace
const BrowseJerseysPage = ({ jerseys, loading, onFilter, onAddToCollection, onJerseyClick, onCreatorClick, onViewUserProfile }) => {
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState('grid'); // Changed to grid like Marketplace
  const [sortBy, setSortBy] = useState('newest');
  const [searchQuery, setSearchQuery] = useState('');
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [activeTab, setActiveTab] = useState('jerseys');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  const [filters, setFilters] = useState({
    league: '',
    team: '',
    season: '',
    size: '',
    condition: '',
    manufacturer: ''
  });

  // Get unique values for filters
  const getUniqueValues = (field) => {
    const values = jerseys.map(jersey => jersey[field]).filter(v => v && v.trim());
    return [...new Set(values)].sort();
  };

  // Filter and search jerseys
  const getFilteredJerseys = () => {
    let filtered = jerseys;

    if (searchQuery) {
      filtered = filtered.filter(jersey => 
        jersey.team?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.player?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.league?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.season?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        filtered = filtered.filter(jersey => 
          jersey[key]?.toLowerCase().includes(value.toLowerCase())
        );
      }
    });

    switch (sortBy) {
      case 'team':
        filtered.sort((a, b) => (a.team || '').localeCompare(b.team || ''));
        break;
      case 'season':
        filtered.sort((a, b) => (b.season || '').localeCompare(a.season || ''));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      default:
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    return filtered;
  };

  // Handle user search
  const handleUserSearch = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.length >= 2) {
      setSearchLoading(true);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API}/api/users/search?query=${encodeURIComponent(query)}`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (response.ok) {
          const users = await response.json();
          setSearchResults(users);
        } else {
          setSearchResults([]);
        }
      } catch (error) {
        console.error('Failed to search users:', error);
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    } else {
      setSearchResults([]);
      setSearchLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const DarkJerseyCard = ({ jersey, isListView }) => (
    <div 
      className={`bg-gray-900 border border-gray-700 hover:border-gray-600 transition-all duration-200 cursor-pointer group relative ${
        isListView ? 'flex items-center p-4 rounded-lg mb-2' : 'rounded-lg overflow-hidden'
      }`}
      onClick={() => onJerseyClick && onJerseyClick(jersey)}
    >
      {isListView ? (
        <>
          <div className="w-16 h-16 md:w-20 md:h-20 bg-gray-800 rounded flex items-center justify-center overflow-hidden mr-4 flex-shrink-0">
            {jersey.images && jersey.images.length > 0 ? (
              <img
                src={jersey.images[0]}
                alt={`${jersey.team} ${jersey.season}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://dummyimage.com/80x80/333/fff.png&text=Jersey';
                }}
              />
            ) : (
              <span className="text-gray-500 text-2xl">👕</span>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold text-sm md:text-base mb-1 truncate">
              {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
            </h3>
            <div className="text-gray-400 text-xs md:text-sm mb-2">
              {jersey.league} • {jersey.season} • {jersey.home_away}
            </div>
            <div className="text-xs text-gray-500">
              TK{jersey.reference_number} • Taille: {jersey.size}
            </div>
          </div>

          {user && (
            <div className="flex flex-col sm:flex-row gap-2 ml-4">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAddToCollection && onAddToCollection(jersey.id, 'owned');
                }}
                className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                title="Ajouter à ma collection"
              >
                ❤️ Own
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAddToCollection && onAddToCollection(jersey.id, 'wanted');
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                title="Ajouter à ma wishlist"
              >
                ⭐ Want
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="aspect-square bg-gray-800 flex items-center justify-center overflow-hidden">
            {jersey.images && jersey.images.length > 0 ? (
              <img
                src={jersey.images[0]}
                alt={`${jersey.team} ${jersey.season}`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                onError={(e) => {
                  e.target.src = 'https://dummyimage.com/200x200/333/fff.png&text=Jersey';
                }}
              />
            ) : (
              <div className="text-gray-500 text-center">
                <div className="text-4xl mb-2">👕</div>
                <div className="text-sm">No Image</div>
              </div>
            )}
          </div>
          
          <div className="p-4">
            <h3 className="text-white font-semibold text-sm mb-1 truncate">
              {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
            </h3>
            <p className="text-gray-400 text-xs mb-2">
              {jersey.league} • {jersey.season}
            </p>
            <p className="text-gray-500 text-xs mb-3">
              TK{jersey.reference_number}
            </p>
            
            {user && (
              <div className="space-y-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onAddToCollection && onAddToCollection(jersey.id, 'owned');
                  }}
                  className="w-full bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                >
                  ❤️ Own
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onAddToCollection && onAddToCollection(jersey.id, 'wanted');
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                >
                  ⭐ Want
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Explorez</h1>
          <p className="text-gray-400 mb-4">Découvrez et explorez la collection complète de maillots de football</p>
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-3 text-blue-300 text-sm">
            💡 <strong>Astuce :</strong> Utilisez les filtres pour affiner votre recherche et trouvez le maillot parfait
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Rechercher par équipe, joueur, championnat..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-white focus:border-transparent"
              />
            </div>
            
            {/* View Toggle Buttons */}
            <div className="flex bg-gray-800 rounded-lg border border-gray-700 p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z"/>
                </svg>
                <span className="hidden sm:inline">Grille</span>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z"/>
                </svg>
                <span className="hidden sm:inline">Liste</span>
              </button>
            </div>
            
            <button
              onClick={() => setShowMobileFilters(!showMobileFilters)}
              className="lg:hidden bg-gray-800 text-white px-4 py-3 rounded-lg border border-gray-700"
            >
              Filtres {showMobileFilters ? '▲' : '▼'}
            </button>
          </div>

          {/* Filters */}
          <div className={`grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 ${showMobileFilters ? 'block' : 'hidden lg:grid'}`}>
            <select
              value={filters.league}
              onChange={(e) => handleFilterChange('league', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Tous les championnats</option>
              {getUniqueValues('league').map(league => (
                <option key={league} value={league}>{league}</option>
              ))}
            </select>
            
            <select
              value={filters.team}
              onChange={(e) => handleFilterChange('team', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Toutes les équipes</option>
              {getUniqueValues('team').slice(0, 50).map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
            
            <select
              value={filters.season}
              onChange={(e) => handleFilterChange('season', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Toutes les saisons</option>
              {getUniqueValues('season').map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </select>
            
            <select
              value={filters.size}
              onChange={(e) => handleFilterChange('size', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Toutes les tailles</option>
              {getUniqueValues('size').map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
            
            <select
              value={filters.condition}
              onChange={(e) => handleFilterChange('condition', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Tous les états</option>
              {getUniqueValues('condition').map(condition => (
                <option key={condition} value={condition}>{condition}</option>
              ))}
            </select>
            
            <select
              value={filters.manufacturer}
              onChange={(e) => handleFilterChange('manufacturer', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Tous les fabricants</option>
              {getUniqueValues('manufacturer').map(manufacturer => (
                <option key={manufacturer} value={manufacturer}>{manufacturer}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Jerseys Results */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Résultats ({getFilteredJerseys().length})
            </h2>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white"
            >
              <option value="newest">Plus récent</option>
              <option value="oldest">Plus ancien</option>
              <option value="team">Par équipe</option>
              <option value="season">Par saison</option>
            </select>
          </div>
        </div>

        {/* Jersey Display */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">Chargement...</div>
        ) : getFilteredJerseys().length > 0 ? (
          <div className={`${
            viewMode === 'grid' 
              ? 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4' 
              : 'space-y-4'
          }`}>
            {getFilteredJerseys().map((jersey) => (
              <DarkJerseyCard 
                key={jersey.id} 
                jersey={jersey} 
                isListView={viewMode === 'list'} 
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">Aucun maillot trouvé</div>
            <p className="text-gray-500">Essayez de modifier vos critères de recherche ou filtres.</p>
          </div>
        )}
      </div>
    </div>
  );
};