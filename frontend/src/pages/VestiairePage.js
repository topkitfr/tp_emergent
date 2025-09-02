import React, { useState, useEffect } from 'react';

const VestiairePage = ({ user, API, onDataUpdate }) => {
  const [jerseyReleases, setJerseyReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    team_id: '',
    season: '',
    player_name: ''
  });
  const [showReleaseDetailModal, setShowReleaseDetailModal] = useState(false);
  const [selectedReleaseForDetail, setSelectedReleaseForDetail] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadVestiaire();
  }, []);

  // Define addToCollection function BEFORE JerseyReleaseCard component
  const addToCollection = async (jerseyReleaseId, collectionType) => {
    if (!user) {
      alert('You must be signed in to add items to your collection');
      return;
    }

    try {
      console.log(`🔄 Adding Jersey Release ${jerseyReleaseId} to ${collectionType} collection for user ${user.id}`);
      
      const response = await fetch(`${API}/api/users/${user.id}/collections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          jersey_release_id: jerseyReleaseId,
          collection_type: collectionType
        })
      });

      const responseData = await response.json();
      console.log(`📥 Add to collection response:`, responseData);

      if (response.ok) {
        console.log(`✅ Successfully added to ${collectionType} collection`);
        alert(`Kit added to ${collectionType === 'owned' ? 'owned' : 'wanted'} collection!`);
        loadVestiaire(); // Refresh list
      } else {
        console.error(`❌ Failed to add to collection: ${response.status}`);
        alert(`Error: ${responseData.detail || 'Failed to add to collection'}`);
      }
    } catch (error) {
      console.error('Error adding to collection:', error);
      alert('Error adding to collection');
    }
  };

  // Define showReleaseDetails function BEFORE JerseyReleaseCard component  
  const showReleaseDetails = (release) => {
    setSelectedReleaseForDetail(release);
    setShowReleaseDetailModal(true);
  };

  const loadVestiaire = async () => {
    try {
      setLoading(true);
      
      // Build query parameters
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.team_id) params.append('team_id', filters.team_id);
      if (filters.season) params.append('season', filters.season);
      if (filters.player_name) params.append('player_name', filters.player_name);

      console.log(`🔄 Loading vestiaire with params: ${params}`);
      
      const response = await fetch(`${API}/api/vestiaire?${params}`);
      
      console.log(`📥 Vestiaire response: ${response.status}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Loaded ${Array.isArray(data) ? data.length : 'non-array'} vestiaire items:`, data);
        
        if (Array.isArray(data)) {
          setJerseyReleases(data);
        } else {
          console.warn('Vestiaire API returned non-array data:', data);
          setJerseyReleases([]);
        }
      } else {
        console.error(`❌ Vestiaire API error: ${response.status}`);
        setJerseyReleases([]);
      }
    } catch (error) {
      console.error('Error loading vestiaire:', error);
      setJerseyReleases([]);
    } finally {
      setLoading(false);
    }
  };

  // Jersey Release Card Component
  const JerseyReleaseCard = ({ release }) => {
    const masterJerseyInfo = release.master_jersey_info || {};
    const teamInfo = masterJerseyInfo.team_info || {};
    const brandInfo = masterJerseyInfo.brand_info || {};
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-200">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                  {release.topkit_reference || 'No Ref'}
                </span>
                {release.condition && (
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                    {release.condition}
                  </span>
                )}
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {teamInfo.name || 'Unknown Team'} - {masterJerseyInfo.season || 'Unknown Season'}
              </h3>
              
              <div className="text-sm text-gray-600 space-y-1">
                {release.player_name && (
                  <div>Player: {release.player_name}</div>
                )}
                <div>Kit Type: {masterJerseyInfo.jersey_type || 'Unknown'}</div>
                <div>Brand: {brandInfo.name || 'Unknown'}</div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-lg font-bold text-green-600">
                €{release.retail_price || 'N/A'}
              </div>
              <div className="text-sm text-gray-500">Retail Price</div>
            </div>
          </div>

          {/* Description */}
          {release.description && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700">{release.description}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-2">
            {user && (
              <>
                <button
                  onClick={() => addToCollection(release.id, 'owned')}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Owned
                </button>
                <button
                  onClick={() => addToCollection(release.id, 'wanted')}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Wanted
                </button>
              </>
            )}
            <button
              onClick={() => showReleaseDetails(release)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              View Details
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Jersey Release Detail Modal
  const JerseyReleaseDetailModal = ({ release, isOpen, onClose }) => {
    if (!isOpen || !release) return null;

    const masterJerseyInfo = release.master_jersey_info || {};
    const teamInfo = masterJerseyInfo.team_info || {};
    const brandInfo = masterJerseyInfo.brand_info || {};

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Kit Details</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>

          <div className="p-6 space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Kit Information</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Reference:</span> {release.topkit_reference || 'No reference'}</div>
                  <div><span className="font-medium">Player:</span> {release.player_name || 'No specific player'}</div>
                  <div><span className="font-medium">Size:</span> {release.size || 'Not specified'}</div>
                  <div><span className="font-medium">Condition:</span> {release.condition || 'Not specified'}</div>
                  <div><span className="font-medium">Release Type:</span> {release.release_type || 'Not specified'}</div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Pricing</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Retail Price:</span> €{release.retail_price || 'N/A'}</div>
                  <div><span className="font-medium">Estimated Value:</span> €{release.estimated_value || 'N/A'}</div>
                  {release.purchase_price && (
                    <div><span className="font-medium">Purchase Price:</span> €{release.purchase_price}</div>
                  )}
                </div>
              </div>
            </div>

            {/* Master Kit Information */}
            <div className="space-y-3">
              <h3 className="font-semibold text-lg text-gray-900">Master Kit Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <div><span className="font-medium">Team:</span> {teamInfo.name || 'Unknown'}</div>
                  <div><span className="font-medium">Season:</span> {masterJerseyInfo.season || 'Unknown'}</div>
                  <div><span className="font-medium">Kit Type:</span> {masterJerseyInfo.jersey_type || 'Unknown'}</div>
                </div>
                <div className="space-y-2">
                  <div><span className="font-medium">Brand:</span> {brandInfo.name || 'Unknown'}</div>
                  <div><span className="font-medium">Reference:</span> {masterJerseyInfo.topkit_reference || 'No reference'}</div>
                </div>
              </div>
            </div>

            {/* Description */}
            {release.description && (
              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Description</h3>
                <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">{release.description}</p>
              </div>
            )}

            {/* Actions */}
            {user && (
              <div className="flex space-x-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    addToCollection(release.id, 'owned');
                    onClose();
                  }}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Add to Owned Collection
                </button>
                <button
                  onClick={() => {
                    addToCollection(release.id, 'wanted');
                    onClose();
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Add to Wanted List
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign In Required</h1>
          <p className="text-gray-600">You need to sign in to access the Kit Store.</p>
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
              👕 Kit Store
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Discover all available physical versions of referenced kits.
              Add them to your collection and track their value!
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {Array.isArray(jerseyReleases) ? jerseyReleases.length : 0}
              </div>
              <div className="text-sm text-blue-700">Available Releases</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {Array.isArray(jerseyReleases) && jerseyReleases.length > 0 ? Math.round(jerseyReleases.reduce((sum, r) => sum + (r.estimated_value || 0), 0) / jerseyReleases.length) : 0}€
              </div>
              <div className="text-sm text-green-700">Average Estimated Price</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {Array.isArray(jerseyReleases) ? new Set(jerseyReleases.map(r => r.player_name).filter(Boolean)).size : 0}
              </div>
              <div className="text-sm text-purple-700">Different Players</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Search for a player..."
              value={filters.player_name}
              onChange={(e) => setFilters({...filters, player_name: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Season (ex: 2022-23)"
              value={filters.season}
              onChange={(e) => setFilters({...filters, season: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={loadVestiaire}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Filter
            </button>
            <button 
              onClick={() => setFilters({search: '', team_id: '', season: '', player_name: ''})}
              className="text-gray-600 hover:text-gray-800"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Available Versions ({jerseyReleases.length})
            </h2>
            {user && (
              <button 
                onClick={loadVestiaire}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Refresh
              </button>
            )}
          </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading kit store...</p>
          </div>
        ) : jerseyReleases.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No kit releases found.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jerseyReleases.map((release) => (
              <JerseyReleaseCard key={release.id} release={release} />
            ))}
          </div>
        )}
      </div>

      {/* Jersey Release Detail Modal */}
      <JerseyReleaseDetailModal
        release={selectedReleaseForDetail}
        isOpen={showReleaseDetailModal}
        onClose={() => setShowReleaseDetailModal(false)}
      />
    </div>
  );
};

export default VestiairePage;