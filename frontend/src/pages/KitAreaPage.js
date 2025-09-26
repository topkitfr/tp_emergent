import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Search, Filter, Grid, List, ChevronDown, Plus, Heart, User } from 'lucide-react';
import MasterKitForm from '../components/MasterKitForm';
import EnhancedEditKitForm from '../components/EnhancedEditKitForm';

const KitAreaPage = ({ user, setShowAuthModal }) => {
  const [masterKits, setMasterKits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState('grid');
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter states
  const [filters, setFilters] = useState({
    club: '',
    brand: '',
    season: '',
    kit_type: '',
    competition: ''
  });
  
  // Modal states
  const [showMasterKitForm, setShowMasterKitForm] = useState(false);
  const [showPersonalDetailsForm, setShowPersonalDetailsForm] = useState(false);
  const [selectedMasterKit, setSelectedMasterKit] = useState(null);
  const [selectedCollectionType, setSelectedCollectionType] = useState('owned'); // 'owned' or 'wanted'
  
  // Enhanced edit form data for adding to collection
  const [editFormData, setEditFormData] = useState({});
  
  // Filter options
  const [brands, setBrands] = useState([]);
  const [seasons, setSeasons] = useState([]);
  
  const navigate = useNavigate();
  const location = useLocation();

  // Parse URL parameters on component mount
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const urlFilters = {
      club: searchParams.get('club') || '',
      brand: searchParams.get('brand') || '',
      season: searchParams.get('season') || '',
      kit_type: searchParams.get('kit_type') || '',
      competition: searchParams.get('competition') || ''
    };
    
    // Only update filters if there are URL parameters
    if (Object.values(urlFilters).some(value => value !== '')) {
      setFilters(prev => ({
        ...prev,
        ...urlFilters
      }));
    }
  }, [location.search]);

  useEffect(() => {
    fetchMasterKits();
  }, []);

  useEffect(() => {
    fetchMasterKits();
  }, [filters, currentPage, itemsPerPage, searchQuery]);

  // Listen for custom events to handle pending actions after login
  useEffect(() => {
    const handleOpenMasterKitForm = () => {
      setShowMasterKitForm(true);
    };

    const handleAddToCollection = (event) => {
      const { masterKit, collectionType } = event.detail;
      setSelectedMasterKit(masterKit);
      setSelectedCollectionType(collectionType);
      setShowPersonalDetailsForm(true);
    };

    const handleAddToWantListEvent = async (event) => {
      const { masterKit } = event.detail;
      await handleAddToWantList(masterKit);
    };

    window.addEventListener('openMasterKitForm', handleOpenMasterKitForm);
    window.addEventListener('addToCollection', handleAddToCollection);
    window.addEventListener('addToWantList', handleAddToWantListEvent);

    return () => {
      window.removeEventListener('openMasterKitForm', handleOpenMasterKitForm);
      window.removeEventListener('addToCollection', handleAddToCollection);
      window.removeEventListener('addToWantList', handleAddToWantListEvent);
    };
  }, []);

  const fetchMasterKits = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (filters.club) params.append('club', filters.club);
      if (filters.brand) params.append('brand', filters.brand);
      if (filters.season) params.append('season', filters.season);
      if (filters.kit_type) params.append('kit_type', filters.kit_type);
      if (filters.competition) params.append('competition', filters.competition);
      if (searchQuery) params.append('q', searchQuery);
      params.append('limit', itemsPerPage);
      params.append('skip', (currentPage - 1) * itemsPerPage);

      const endpoint = searchQuery 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/master-kits/search?${params}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/master-kits?${params}`;

      const response = await fetch(endpoint);

      if (!response.ok) {
        throw new Error('Failed to fetch master kits');
      }

      const data = await response.json();
      setMasterKits(data);
      
      // Extract unique brands and seasons for filters
      const uniqueBrands = [...new Set(data.map(kit => kit.brand))].filter(Boolean);
      const uniqueSeasons = [...new Set(data.map(kit => kit.season))].filter(Boolean);
      setBrands(uniqueBrands);
      setSeasons(uniqueSeasons);
      
    } catch (error) {
      console.error('Error fetching master kits:', error);
      setError('Failed to load master kits');
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
      club: '',
      brand: '',
      season: '',
      kit_type: '',
      competition: ''
    });
    setSearchQuery('');
  };

  const handleMasterKitClick = (kitId) => {
    navigate(`/kit-area/master/${kitId}`);
  };

  const handleAddToCollection = (masterKit, collectionType = 'owned') => {
    // Check if user is authenticated
    if (!user) {
      // Show authentication modal
      if (setShowAuthModal) {
        setShowAuthModal(true);
        // Store the action to perform after login
        localStorage.setItem('pendingAction', JSON.stringify({
          action: 'addToCollection',
          masterKit: masterKit,
          collectionType: collectionType
        }));
      } else {
        alert('Please sign in to add kits to your collection');
      }
      return;
    }

    setSelectedMasterKit(masterKit);
    setSelectedCollectionType(collectionType);
    setShowPersonalDetailsForm(true);
  };

  const handleAddToWantList = async (masterKit) => {
    // Check if user is authenticated
    if (!user) {
      // Show authentication modal
      if (setShowAuthModal) {
        setShowAuthModal(true);
        // Store the action to perform after login
        localStorage.setItem('pendingAction', JSON.stringify({
          action: 'addToWantList',
          masterKit: masterKit
        }));
      } else {
        alert('Please sign in to add kits to your want list');
      }
      return;
    }

    // Directly add to want list without form
    try {
      // Get token with proper validation
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('❌ No authentication token available for want list');
        alert('Authentication error. Please sign in again.');
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/my-collection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          master_kit_id: masterKit.id,
          collection_type: 'wanted'
        })
      });

      if (response.ok) {
        alert('Kit added to your want list!');
        // Refresh master kits to update any UI counters
        fetchMasterKits();
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to add to want list'}`);
      }
    } catch (error) {
      console.error('Error adding to want list:', error);
      alert('Error adding to want list');
    }
  };

  const handleAddKitClick = () => {
    // Check if user is authenticated
    if (!user) {
      // Show authentication modal
      if (setShowAuthModal) {
        setShowAuthModal(true);
        // Store the action to perform after login
        localStorage.setItem('pendingAction', JSON.stringify({
          action: 'addKit'
        }));
      } else {
        alert('Please sign in to add a kit');
      }
      return;
    }

    // User is authenticated, show the Master Kit form
    setShowMasterKitForm(true);
  };

  const handleMasterKitCreated = (newMasterKit) => {
    // Refresh the list
    fetchMasterKits();
    
    // Show confirmation message instead of immediately opening personal form
    alert('Master kit created successfully! Your submission is pending approval. Once approved, it will appear in the Kit Area and you can add it to your collection.');
    
    // Don't automatically show personal details form - user should add to collection manually later
    // setSelectedMasterKit(newMasterKit); 
    // setShowPersonalDetailsForm(true);
  };

  const handleAddedToCollection = () => {
    // Refresh the list to update collector counts
    fetchMasterKits();
  };

  // Enhanced edit form handlers for adding to collection
  const handleFormDataChange = (key, value) => {
    setEditFormData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveToCollection = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please log in to add to collection');
        return;
      }

      console.log('Form data being processed:', editFormData);

      // Helper functions to map enum values
      const mapConditionValue = (value) => {
        if (!value) return null;
        
        // Map origin_type to condition enum values
        const mapping = {
          'standard': null, // Standard doesn't need special condition
          'match_issued': 'match_prepared',  
          'match_worn': 'match_worn',
          'training': 'training'
        };
        
        return mapping[value] || null;
      };

      const mapPhysicalStateValue = (value) => {
        if (!value) return null;
        
        // Map EnhancedEditKitForm values to backend enum values
        const mapping = {
          'new_with_tags': 'new_with_tags',
          'very_good': 'very_good_condition',  // Fix the mismatch
          'used': 'used',
          'damaged': 'damaged',
          'needs_restoration': 'needs_restoration'
        };
        
        return mapping[value] || null;
      };

      // Convert patches array to string if it exists - with detailed logging
      let patchesString = null;
      console.log('Raw patches from form:', editFormData.patches, 'Type:', typeof editFormData.patches);
      
      if (editFormData.patches) {
        if (Array.isArray(editFormData.patches)) {
          // Filter out any empty values and join with comma
          const validPatches = editFormData.patches.filter(p => p && p.trim() !== '');
          patchesString = validPatches.length > 0 ? validPatches.join(', ') : null;
          console.log('Converted patches array to string:', patchesString);
        } else if (typeof editFormData.patches === 'string' && editFormData.patches.trim() !== '') {
          patchesString = editFormData.patches.trim();
          console.log('Using patches as string:', patchesString);
        }
      }
      
      console.log('Final patches value:', patchesString, 'Type:', typeof patchesString);

      // Map EnhancedEditKitForm fields to MyCollectionCreate fields correctly
      const collectionData = {
        master_kit_id: selectedMasterKit.id,
        collection_type: selectedCollectionType,
        
        // Basic fields - direct mapping with correct field names
        name_printing: editFormData.name_printing || null,
        number_printing: editFormData.number_printing || null,
        size: editFormData.size || null,
        
        // Personal notes mapping fix
        personal_notes: editFormData.comments || null,
        
        // Patches - convert array to string  
        patches: patchesString,
        
        // Signature fields with correct mapping
        is_signed: editFormData.signature || false,
        signed_by: editFormData.signature && editFormData.signature_player ? editFormData.signature_player : null,
        
        // Condition mapping with improved logic
        condition: mapConditionValue(editFormData.origin_type), // Use origin_type for condition
        physical_state: mapPhysicalStateValue(editFormData.general_condition), // Use general_condition for physical_state
        
        // Price and date fields with correct mapping
        purchase_price: editFormData.user_estimate ? parseFloat(editFormData.user_estimate) : null,
        purchase_date: editFormData.match_date || null
      };

      console.log('Sending collection data:', collectionData);

      // Final data sanitization - ensure no arrays are sent to backend
      const sanitizedData = { ...collectionData };
      
      // Double-check patches field
      if (sanitizedData.patches && Array.isArray(sanitizedData.patches)) {
        console.warn('PATCHES STILL AN ARRAY - Converting again:', sanitizedData.patches);
        sanitizedData.patches = sanitizedData.patches.join(', ');
      }
      
      // Remove any undefined or null fields that might cause issues
      Object.keys(sanitizedData).forEach(key => {
        if (sanitizedData[key] === undefined) {
          delete sanitizedData[key];
        }
      });
      
      console.log('Final sanitized data:', sanitizedData);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/my-collection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(sanitizedData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error Response:', errorData);
        
        // Handle validation errors properly
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => 
            `${err.loc ? err.loc.join('.') : 'Field'}: ${err.msg}`
          ).join('\n');
          throw new Error(`Validation errors:\n${errorMessages}`);
        } else if (errorData.detail) {
          throw new Error(errorData.detail);
        } else {
          throw new Error(`Failed to add to collection (${response.status})`);
        }
      }

      const result = await response.json();
      console.log('Success response:', result);

      const successMessage = selectedCollectionType === 'owned' 
        ? 'Master Kit added to your collection successfully!' 
        : 'Master Kit added to your want list successfully!';
      
      alert(successMessage);
      
      // Reset form and close modal
      setEditFormData({});
      setShowPersonalDetailsForm(false);
      setSelectedMasterKit(null);
      handleAddedToCollection();

    } catch (error) {
      console.error('Error adding to collection:', error);
      alert(`Error: ${error.message}`);
    }
  };

  const renderMasterKitCard = (kit) => {
    return (
      <div 
        key={kit.id}
        className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
      >
        <div 
          className="cursor-pointer"
          onClick={() => handleMasterKitClick(kit.id)}
        >
          <div className="aspect-w-16 aspect-h-12 bg-gray-100">
            {kit.front_photo_url ? (
              <img
                src={kit.front_photo_url.startsWith('http') ? kit.front_photo_url : 
                     kit.front_photo_url.startsWith('uploads/') ? 
                     `${process.env.REACT_APP_BACKEND_URL}/api/${kit.front_photo_url}` :
                     `${process.env.REACT_APP_BACKEND_URL}/api/uploads/${kit.front_photo_url}`}
                alt={`${kit.club} ${kit.season} ${kit.kit_type}`}
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
              {kit.club}
            </h3>
            <p className="text-xs text-gray-600 mb-2">
              {kit.season} • {kit.kit_type?.charAt(0).toUpperCase() + kit.kit_type?.slice(1)}
            </p>
            <p className="text-xs text-gray-500 mb-2">
              {kit.brand} • {kit.model?.charAt(0).toUpperCase() + kit.model?.slice(1)}
            </p>
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>{kit.competition}</span>
              <span>{kit.total_collectors || 0} collectors</span>
            </div>
          </div>
        </div>
        
        {/* Add to Collection and Want List Buttons */}
        <div className="px-4 pb-4 space-y-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAddToCollection(kit, 'owned');
            }}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-1"
          >
            <User className="w-4 h-4" />
            <span>Add to My Collection</span>
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAddToWantList(kit);
            }}
            className="w-full bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-1"
          >
            <Heart className="w-4 h-4" />
            <span>Add to Want List</span>
          </button>
        </div>
      </div>
    );
  };

  const renderMasterKitList = (kit) => {
    return (
      <div 
        key={kit.id}
        className="bg-white border-b border-gray-200 p-4 hover:bg-gray-50 transition-colors flex items-center space-x-4"
      >
        <div 
          className="cursor-pointer flex items-center space-x-4 flex-1"
          onClick={() => handleMasterKitClick(kit.id)}
        >
          <div className="w-16 h-16 bg-gray-100 rounded-lg flex-shrink-0">
            {kit.front_photo_url ? (
              <img
                src={kit.front_photo_url.startsWith('http') ? kit.front_photo_url : 
                     kit.front_photo_url.startsWith('uploads/') ? 
                     `${process.env.REACT_APP_BACKEND_URL}/api/${kit.front_photo_url}` :
                     `${process.env.REACT_APP_BACKEND_URL}/api/uploads/${kit.front_photo_url}`}
                alt={`${kit.club} ${kit.season} ${kit.kit_type}`}
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
              {kit.club} - {kit.season} - {kit.kit_type?.charAt(0).toUpperCase() + kit.kit_type?.slice(1)}
            </h3>
            <p className="text-sm text-gray-600">
              {kit.brand} • {kit.model?.charAt(0).toUpperCase() + kit.model?.slice(1)} • {kit.competition}
            </p>
            <div className="flex space-x-4 text-xs text-gray-500 mt-1">
              <span>{kit.total_collectors || 0} collectors</span>
              <span>#{kit.topkit_reference}</span>
            </div>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => handleAddToCollection(kit, 'owned')}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-1"
          >
            <User className="w-4 h-4" />
            <span>Own</span>
          </button>
          
          <button
            onClick={() => handleAddToWantList(kit)}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-1"
          >
            <Heart className="w-4 h-4" />
            <span>Want</span>
          </button>
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
              <button
                onClick={handleAddKitClick}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add a kit</span>
              </button>
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

          {/* Search Bar */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search master kits by club, season, brand, competition..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Club</label>
              <input
                type="text"
                value={filters.club}
                onChange={(e) => handleFilterChange('club', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                placeholder="Filter by club"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
              <select
                value={filters.brand}
                onChange={(e) => handleFilterChange('brand', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Brands</option>
                {brands.map(brand => (
                  <option key={brand} value={brand}>{brand}</option>
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
                value={filters.kit_type}
                onChange={(e) => handleFilterChange('kit_type', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value="home">Home</option>
                <option value="away">Away</option>
                <option value="third">Third</option>
                <option value="training">Training</option>
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
              {masterKits.length} master kits found
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
        {masterKits.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👕</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No master kits found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || Object.values(filters).some(f => f) 
                ? "Try adjusting your search or filters to see more results."
                : "No master kits have been created yet."
              }
            </p>
            <button
              onClick={handleAddKitClick}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium"
            >
              Create First Master Kit
            </button>
          </div>
        ) : (
          <>
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {masterKits.map(renderMasterKitCard)}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                {masterKits.map(renderMasterKitList)}
              </div>
            )}
          </>
        )}
      </div>

      {/* Master Kit Form Modal */}
      <MasterKitForm
        isOpen={showMasterKitForm}
        onClose={() => setShowMasterKitForm(false)}
        onSuccess={handleMasterKitCreated}
        API={process.env.REACT_APP_BACKEND_URL}
      />

      {/* Enhanced Personal Details Form Modal - Using same form as Edit Kit Details */}
      <EnhancedEditKitForm
        isOpen={showPersonalDetailsForm}
        onClose={() => {
          setShowPersonalDetailsForm(false);
          setSelectedMasterKit(null);
          setSelectedCollectionType('owned');
          setEditFormData({});
        }}
        editingItem={selectedMasterKit ? { master_kit: selectedMasterKit } : null}
        formData={editFormData}
        onFormDataChange={handleFormDataChange}
        onSave={handleSaveToCollection}
        API={process.env.REACT_APP_BACKEND_URL}
        title={selectedCollectionType === 'owned' ? 'Edit Kit Details' : 'Add to Want List'}
      />
    </div>
  );
};

export default KitAreaPage;