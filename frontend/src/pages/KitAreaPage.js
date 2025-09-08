import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Grid, List, ChevronDown } from 'lucide-react';

const KitAreaPage = () => {
  const [masterJerseys, setMasterJerseys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState('grid');
  const [itemsPerPage, setItemsPerPage] = useState(20);
  
  // Filter states
  const [filters, setFilters] = useState({
    team_id: '',
    brand_id: '',
    season: '',
    jersey_type: ''
  });
  
  // Filter options
  const [teams, setTeams] = useState([]);
  const [brands, setBrands] = useState([]);
  const [seasons, setSeasons] = useState([]);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchFilterOptions();
    fetchMasterJerseys();
  }, []);

  useEffect(() => {
    fetchMasterJerseys();
  }, [filters, currentPage, itemsPerPage]);

  const fetchFilterOptions = async () => {
    try {
      const [teamsRes, brandsRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teams`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/brands`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
      ]);

      if (teamsRes.ok) {
        const teamsData = await teamsRes.json();
        setTeams(teamsData);
      }

      if (brandsRes.ok) {
        const brandsData = await brandsRes.json();
        setBrands(brandsData);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const fetchMasterJerseys = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (filters.team_id) params.append('team_id', filters.team_id);
      if (filters.brand_id) params.append('brand_id', filters.brand_id);
      if (filters.season) params.append('season', filters.season);
      if (filters.jersey_type) params.append('jersey_type', filters.jersey_type);
      params.append('limit', itemsPerPage);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/master-jerseys?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch master jerseys');
      }

      const data = await response.json();
      setMasterJerseys(data);
      
      // Extract unique seasons for filter
      const uniqueSeasons = [...new Set(data.map(jersey => jersey.season))].filter(Boolean);
      setSeasons(uniqueSeasons);
      
    } catch (error) {
      console.error('Error fetching master jerseys:', error);
      setError('Failed to load master jerseys');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setCurrentPage(1); // Reset to first page when filtering
  };

  const clearFilters = () => {
    setFilters({
      team_id: '',
      brand_id: '',
      season: '',
      jersey_type: ''
    });
  };

  const handleMasterJerseyClick = (jerseyId) => {
    navigate(`/kit-area/master/${jerseyId}`);
  };

  const renderMasterJerseyCard = (jersey) => {
    const teamName = jersey.team_info?.name || 'Unknown Team';
    const brandName = jersey.brand_info?.name || 'Unknown Brand';
    
    return (
      <div 
        key={jersey.id}
        className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => handleMasterJerseyClick(jersey.id)}
      >
        <div className="aspect-w-16 aspect-h-12 bg-gray-100">
          {jersey.main_image_url ? (
            <img
              src={jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `${process.env.REACT_APP_BACKEND_URL}/${jersey.main_image_url}`}
              alt={`${teamName} ${jersey.season} ${jersey.jersey_type}`}
              className="w-full h-48 object-cover"
            />
          ) : (
            <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
              <span className="text-4xl">👕</span>
            </div>
          )}
        </div>
        
        <div className="p-4">
          <h3 className="font-medium text-gray-900 text-sm mb-1">
            {teamName}
          </h3>
          <p className="text-xs text-gray-600 mb-2">
            {jersey.season} • {jersey.jersey_type?.charAt(0).toUpperCase() + jersey.jersey_type?.slice(1)}
          </p>
          <p className="text-xs text-gray-500 mb-2">
            {brandName} • {jersey.model?.charAt(0).toUpperCase() + jersey.model?.slice(1)}
          </p>
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>{jersey.releases_count || 0} versions</span>
            <span>{jersey.collectors_count || 0} collectors</span>
          </div>
        </div>
      </div>
    );
  };

  const renderMasterJerseyList = (jersey) => {
    const teamName = jersey.team_info?.name || 'Unknown Team';
    const brandName = jersey.brand_info?.name || 'Unknown Brand';
    
    return (
      <div 
        key={jersey.id}
        className="bg-white border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer flex items-center space-x-4"
        onClick={() => handleMasterJerseyClick(jersey.id)}
      >
        <div className="w-16 h-16 bg-gray-100 rounded-lg flex-shrink-0">
          {jersey.main_image_url ? (
            <img
              src={jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `${process.env.REACT_APP_BACKEND_URL}/${jersey.main_image_url}`}
              alt={`${teamName} ${jersey.season} ${jersey.jersey_type}`}
              className="w-16 h-16 object-cover rounded-lg"
            />
          ) : (
            <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
              <span className="text-xl">👕</span>
            </div>
          )}
        </div>
        
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">
            {teamName} - {jersey.season} - {jersey.jersey_type?.charAt(0).toUpperCase() + jersey.jersey_type?.slice(1)}
          </h3>
          <p className="text-sm text-gray-600">
            {brandName} • {jersey.model?.charAt(0).toUpperCase() + jersey.model?.slice(1)}
          </p>
          <div className="flex space-x-4 text-xs text-gray-500 mt-1">
            <span>{jersey.releases_count || 0} versions</span>
            <span>{jersey.collectors_count || 0} collectors</span>
          </div>
        </div>
        
        <div className="text-right">
          <p className="text-sm font-medium text-gray-900">{jersey.topkit_reference}</p>
          <p className="text-xs text-gray-500">Master Jersey</p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Kit Area</h1>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">View:</span>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Team</label>
              <select
                value={filters.team_id}
                onChange={(e) => handleFilterChange('team_id', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Teams</option>
                {teams.map(team => (
                  <option key={team.id} value={team.id}>{team.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
              <select
                value={filters.brand_id}
                onChange={(e) => handleFilterChange('brand_id', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Brands</option>
                {brands.map(brand => (
                  <option key={brand.id} value={brand.id}>{brand.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Season</label>
              <select
                value={filters.season}
                onChange={(e) => handleFilterChange('season', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Seasons</option>
                {seasons.map(season => (
                  <option key={season} value={season}>{season}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={filters.jersey_type}
                onChange={(e) => handleFilterChange('jersey_type', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value="home">Home</option>
                <option value="away">Away</option>
                <option value="third">Third</option>
                <option value="fourth">Fourth</option>
                <option value="goalkeeper">Goalkeeper</option>
                <option value="special">Special</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={clearFilters}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Results Summary */}
          <div className="flex justify-between items-center mb-4">
            <p className="text-sm text-gray-600">
              {masterJerseys.length} master jerseys found
            </p>
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Show:</label>
              <select
                value={itemsPerPage}
                onChange={(e) => setItemsPerPage(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {masterJerseys.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👕</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No master jerseys found</h3>
            <p className="text-gray-600">Try adjusting your filters to see more results.</p>
          </div>
        ) : (
          <>
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {masterJerseys.map(renderMasterJerseyCard)}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                {masterJerseys.map(renderMasterJerseyList)}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default KitAreaPage;