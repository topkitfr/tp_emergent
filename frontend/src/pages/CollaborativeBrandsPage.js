import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, List, LayoutGrid } from 'lucide-react';
import ContributionModal from '../ContributionModal';

const CollaborativeBrandsPage = ({ user, API, brands, onDataUpdate }) => {
  const navigate = useNavigate();
  const [filteredBrands, setFilteredBrands] = useState([]);
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
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedBrandForContribution, setSelectedBrandForContribution] = useState(null);
  
  // Get unique countries for filter
  const countries = [...new Set(brands.map(brand => brand.country).filter(Boolean))];

  // Apply filters
  useEffect(() => {
    let filtered = [...brands];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(brand =>
        brand.name.toLowerCase().includes(searchLower) ||
        brand.official_name?.toLowerCase().includes(searchLower) ||
        brand.common_names?.some(name => name.toLowerCase().includes(searchLower))
      );
    }

    if (filters.country) {
      filtered = filtered.filter(brand => brand.country === filters.country);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(brand => brand.verified_level !== 'unverified');
    }

    setFilteredBrands(filtered);
  }, [brands, filters]);

  const handleContributeClick = (brand, e) => {
    e.stopPropagation();
    setSelectedBrandForContribution(brand);
    setShowContributionModal(true);
  };

  const BrandCard = ({ brand }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
      onClick={() => navigate(`/brands/${brand.id}`)}
    >
      {/* Image section - same structure as Master Jersey */}
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {brand.logo_url ? (
          <img 
            src={brand.logo_url.startsWith('data:') || brand.logo_url.startsWith('http') ? brand.logo_url : `${API}/${brand.logo_url}`}
            alt={`${brand.name} logo`}
            className="w-full h-full object-contain p-4"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: brand.logo_url ? 'none' : 'flex'}}>
          👕
        </div>
        
        {brand.verified_level !== 'unverified' && (
          <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
        
        <div className="absolute top-2 left-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
          🌍 {brand.country}
        </div>
        
        {/* Contribution Button */}
        <button
          onClick={(e) => handleContributeClick(brand, e)}
          className="absolute bottom-2 right-2 bg-white/90 hover:bg-white text-blue-600 p-2 rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-all duration-200"
          title="Améliorer cette fiche"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
      </div>
      
      {/* Content section - same structure as Master Jersey */}
      <div className="p-4">
        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
          {brand.name}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-600 mb-3">
          {brand.official_name && (
            <div className="flex items-center">
              <span className="mr-1">🏷️</span>
              <span>{brand.official_name}</span>
            </div>
          )}
          
          {brand.founded_year && (
            <div className="flex items-center">
              <span className="mr-1">📅</span>
              <span>Founded in {brand.founded_year}</span>
            </div>
          )}
          
          {brand.website && (
            <div className="flex items-center">
              <span className="mr-1">🌐</span>
              <span className="truncate">{brand.website}</span>
            </div>
          )}
        </div>
        
        {/* Bottom section - same structure as Master Jersey */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-600 font-mono">{brand.topkit_reference}</span>
          <div className="flex items-center space-x-2 text-gray-500">
            <span>{brand.kits_count || 0} kits</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              👕 Brands
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explore our collaborative database of brands. To add a new brand, use the Community DB.
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              placeholder="Search brands..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({...prev, search: e.target.value}))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
            <select
              value={filters.country}
              onChange={(e) => setFilters(prev => ({...prev, country: e.target.value}))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Countries</option>
              {countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="verified_only"
                checked={filters.verified_only}
                onChange={(e) => setFilters(prev => ({...prev, verified_only: e.target.checked}))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="verified_only" className="ml-2 block text-sm text-gray-900">
                Verified only
              </label>
            </div>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilters({search: '', country: '', verified_only: false})}
              className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Brands Grid */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Brands ({filteredBrands.length})
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading brands...</p>
          </div>
        ) : filteredBrands.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No brands found</h3>
            <p className="text-gray-600">Try adjusting your filters or contribute to the community database.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredBrands.map((brand) => (
              <BrandCard key={brand.id} brand={brand} />
            ))}
          </div>
        )}
      </div>

      {/* Contribution Modal */}
      {showContributionModal && (
        <ContributionModal
          isOpen={showContributionModal}
          onClose={() => {
            setShowContributionModal(false);
            setSelectedBrandForContribution(null);
          }}
          selectedEntity={selectedBrandForContribution}
          entityType="brand"
          user={user}
          API={API}
          onDataUpdate={() => {
            onDataUpdate();
            setShowContributionModal(false);
            setSelectedBrandForContribution(null);
          }}
        />
      )}
    </div>
    </div>
  );
};

export default CollaborativeBrandsPage;