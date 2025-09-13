import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, List, LayoutGrid } from 'lucide-react';
import { AuthContext } from '../App';
import ContributionModal from '../ContributionModal';
import { uploadOptimizedImage, ImageUploadProgress, OptimizedImage } from '../utils/imageUpload';

const CollaborativeTeamsPage = ({ user, API, teams, onDataUpdate }) => {
  const navigate = useNavigate();
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    country: '',
    verified_only: false
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid', // 'grid', 'thumbnail', 'list'
    itemsPerPage: 20,
    currentPage: 1
  });
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedTeamForContribution, setSelectedTeamForContribution] = useState(null);
  
  // Get unique countries for filter
  const countries = [...new Set(teams.map(team => team.country).filter(Boolean))];

  // Apply filters
  useEffect(() => {
    let filtered = [...teams];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(team =>
        team.name.toLowerCase().includes(searchLower) ||
        team.short_name?.toLowerCase().includes(searchLower) ||
        team.common_names?.some(name => name.toLowerCase().includes(searchLower))
      );
    }

    if (filters.country) {
      filtered = filtered.filter(team => team.country === filters.country);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(team => team.verified_level !== 'unverified');
    }

    setFilteredTeams(filtered);
  }, [teams, filters]);

  const handleTeamClick = (team) => {
    navigate(`/teams/${team.id}`);
  };

  const handleContributeClick = (team, e) => {
    e.stopPropagation();
    setSelectedTeamForContribution(team);
    setShowContributionModal(true);
  };

  // Team Card Component
  const TeamCard = ({ team }) => {
    return (
      <div 
        onClick={() => handleTeamClick(team)}
        className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-200 cursor-pointer group"
      >
        {/* Image section - same structure as Master Jersey */}
        <div className="relative w-full h-32 bg-gray-100 rounded-t-lg overflow-hidden flex items-center justify-center">
          {team.logo_url ? (
            <img 
              src={`${API}/api/${team.logo_url}`}
              alt={team.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: team.logo_url ? 'none' : 'flex'}}>
            ⚽
          </div>
          
          {team.verified_level !== 'unverified' && (
            <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
              ✓
            </div>
          )}
          
          <div className="absolute top-2 left-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
            🌍 {team.country}
          </div>
        </div>
        
        {/* Content section - same structure as Master Jersey */}
        <div className="p-4">
          <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
            {team.name}
          </h3>
          
          <div className="space-y-1 text-xs text-gray-600 mb-3">
            {team.short_name && (
              <div className="flex items-center">
                <span className="mr-1">🏷️</span>
                <span>{team.short_name}</span>
              </div>
            )}
            
            {team.city && (
              <div className="flex items-center">
                <span className="mr-1">🏙️</span>
                <span>{team.city}</span>
              </div>
            )}
            
            {team.founded_year && (
              <div className="flex items-center">
                <span className="mr-1">📅</span>
                <span>Founded in {team.founded_year}</span>
              </div>
            )}
            
            {(team.colors || team.primary_colors) && (team.colors?.length > 0 || team.primary_colors?.length > 0) && (
              <div className="flex items-center">
                <span className="mr-1">🎨</span>
                <div className="flex space-x-1">
                  {(team.colors || team.primary_colors || []).slice(0, 3).map((color, index) => (
                    <div
                      key={index}
                      className="w-3 h-3 rounded-full border border-gray-300"
                      style={{ backgroundColor: color.toLowerCase() }}
                      title={color}
                    ></div>
                  ))}
                  {(team.colors || team.primary_colors || []).length > 3 && (
                    <span className="text-xs text-gray-400">+{(team.colors || team.primary_colors || []).length - 3}</span>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Bottom section - same structure as Master Jersey */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-blue-600 font-mono">{team.topkit_reference}</span>
            <div className="flex items-center space-x-2 text-gray-500">
              <span>{team.jerseys_count || 0} kits</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Thumbnail version - smaller cards
  const TeamThumbnail = ({ team }) => (
    <div 
      onClick={() => handleTeamClick(team)}
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
    >
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {team.logo_url ? (
          <img 
            src={`${API}/api/${team.logo_url}`}
            alt={team.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-2xl flex items-center justify-center w-full h-full" style={{display: team.logo_url ? 'none' : 'flex'}}>
          ⚽
        </div>
        
        {team.verified_level !== 'unverified' && (
          <div className="absolute top-1 right-1 bg-green-100 text-green-800 px-1 py-0.5 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
      </div>
      
      <div className="p-2">
        <h3 className="font-bold text-xs text-gray-900 mb-1 group-hover:text-blue-600 line-clamp-1">
          {team.name}
        </h3>
        <div className="text-xs text-gray-600 mb-1">
          {team.country && <span>{team.country}</span>}
        </div>
        <div className="text-xs text-blue-600 font-mono truncate">{team.topkit_reference}</div>
      </div>
    </div>
  );

  // List version - horizontal layout
  const TeamListItem = ({ team }) => (
    <div 
      onClick={() => handleTeamClick(team)}
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all cursor-pointer group flex items-center space-x-4"
    >
      <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-gray-200 transition-colors">
        {team.logo_url ? (
          <img 
            src={`${API}/${team.logo_url}`}
            alt={team.name}
            className="w-full h-full object-cover rounded-lg"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-2xl flex items-center justify-center w-full h-full" style={{display: team.logo_url ? 'none' : 'flex'}}>
          ⚽
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 truncate">
            {team.name}
          </h3>
          {team.verified_level !== 'unverified' && (
            <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium ml-2">
              ✓
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
          {team.country && (
            <span className="flex items-center">
              <span className="mr-1">🌍</span>
              {team.country}
            </span>
          )}
          {team.city && (
            <span className="flex items-center">
              <span className="mr-1">🏙️</span>
              {team.city}
            </span>
          )}
          {team.founded_year && (
            <span className="flex items-center">
              <span className="mr-1">📅</span>
              Founded in {team.founded_year}
            </span>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <span className="text-blue-600 font-mono text-sm">{team.topkit_reference}</span>
          <span className="text-gray-500 text-sm">{team.jerseys_count || 0} kits</span>
        </div>
      </div>
    </div>
  );



  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ⚽ Teams
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explore our collaborative database of teams. To add a new team, use the Community DB.
            </p>
          </div>
        </div>
      </div>

      {/* Filters and Statistics */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                placeholder="Team name..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({...prev, search: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
              <select
                value={filters.country}
                onChange={(e) => setFilters(prev => ({...prev, country: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All countries</option>
                {countries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.verified_only}
                  onChange={(e) => setFilters(prev => ({...prev, verified_only: e.target.checked}))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Verified teams only</span>
              </label>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => setFilters({ search: '', country: '', verified_only: false })}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium px-4 py-2"
              >
                Reset filters
              </button>
            </div>
            
            {/* Display Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">View</label>
              <div className="flex border border-gray-300 rounded">
                <button
                  onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'grid' }))}
                  className={`px-3 py-2 text-sm flex items-center ${displayOptions.viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                  <Grid className="w-4 h-4 mr-1" />
                  Grid
                </button>
                <button
                  onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'thumbnail' }))}
                  className={`px-3 py-2 text-sm border-x border-gray-300 flex items-center ${displayOptions.viewMode === 'thumbnail' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                  <LayoutGrid className="w-4 h-4 mr-1" />
                  Thumb
                </button>
                <button
                  onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'list' }))}
                  className={`px-3 py-2 text-sm flex items-center ${displayOptions.viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                  <List className="w-4 h-4 mr-1" />
                  List
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Per Page</label>
              <select
                value={displayOptions.itemsPerPage}
                onChange={(e) => setDisplayOptions(prev => ({ ...prev, itemsPerPage: parseInt(e.target.value), currentPage: 1 }))}
                className="border border-gray-300 rounded px-3 py-1 text-sm"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{filteredTeams.length}</div>
              <div className="text-sm text-blue-700">Teams found</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {filteredTeams.filter(team => team.verified_level !== 'unverified').length}
              </div>
              <div className="text-sm text-green-700">Verified teams</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{countries.length}</div>
              <div className="text-sm text-purple-700">Countries represented</div>
            </div>
          </div>
        </div>
      </div>

      {/* Teams Grid */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {filteredTeams.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">⚽</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No teams found</h3>
            <p className="text-gray-600">
              Try modifying your filters or contribute by adding a new team
            </p>
          </div>
        ) : (
          <>
            {/* Grid View */}
            {displayOptions.viewMode === 'grid' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredTeams.map((team) => (
                  <div key={team.id} className="relative group">
                    <TeamCard team={team} />
                    {user && (
                      <button
                        onClick={(e) => handleContributeClick(team, e)}
                        className="absolute top-2 right-2 bg-white/90 hover:bg-white text-blue-600 p-1 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Improve this profile"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Thumbnail View */}
            {displayOptions.viewMode === 'thumbnail' && (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
                {filteredTeams.map((team) => (
                  <div key={team.id} className="relative group">
                    <TeamThumbnail team={team} />
                    {user && (
                      <button
                        onClick={(e) => handleContributeClick(team, e)}
                        className="absolute top-1 right-1 bg-white/90 hover:bg-white text-blue-600 p-1 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Improve this profile"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* List View */}
            {displayOptions.viewMode === 'list' && (
              <div className="space-y-4">
                {filteredTeams.map((team) => (
                  <div key={team.id} className="relative group">
                    <TeamListItem team={team} />
                    {user && (
                      <button
                        onClick={(e) => handleContributeClick(team, e)}
                        className="absolute top-4 right-4 bg-white/90 hover:bg-white text-blue-600 p-2 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Improve this profile"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>


      {/* Contribution Modal */}
      {showContributionModal && (
        <ContributionModal
          isOpen={showContributionModal}
          onClose={() => {
            setShowContributionModal(false);
            setSelectedTeamForContribution(null);
          }}
          selectedEntity={selectedTeamForContribution}
          entityType="team"
          user={user}
          API={API}
          onDataUpdate={() => {
            onDataUpdate();
            setShowContributionModal(false);
            setSelectedTeamForContribution(null);
          }}
        />
      )}
    </div>
  );
};

export default CollaborativeTeamsPage;