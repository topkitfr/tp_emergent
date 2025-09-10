import React, { useState, useEffect } from 'react';

const VestiairePage = ({ user, API, onDataUpdate }) => {
  const [referenceKits, setReferenceKits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userCollectionCounts, setUserCollectionCounts] = useState({ owned: 0, wanted: 0 });
  const [filters, setFilters] = useState({
    search: '',
    team_id: '',
    season: '',
    kit_type: ''
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid', // 'grid', 'thumbnail', 'list'
    itemsPerPage: 20,
    currentPage: 1
  });
  const [showReleaseDetailModal, setShowReleaseDetailModal] = useState(false);
  const [selectedReleaseForDetail, setSelectedReleaseForDetail] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadKitStore();
    loadPlayers();
    if (user) {
      loadUserCollectionCounts();
    }
  }, [user]);

  const loadUserCollectionCounts = async () => {
    if (!user?.id) return;
    
    try {
      const [ownedResponse, wantedResponse] = await Promise.all([
        fetch(`${API}/api/users/${user.id}/reference-kit-collections/owned`, {
          headers: {
            'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
          }
        }),
        fetch(`${API}/api/users/${user.id}/reference-kit-collections/wanted`, {
          headers: {
            'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
          }
        })
      ]);

      if (ownedResponse.ok && wantedResponse.ok) {
        const [ownedData, wantedData] = await Promise.all([
          ownedResponse.json(),
          wantedResponse.json()
        ]);

        setUserCollectionCounts({
          owned: Array.isArray(ownedData) ? ownedData.length : 0,
          wanted: Array.isArray(wantedData) ? wantedData.length : 0
        });
      }
    } catch (error) {
      console.error('Error loading user collection counts:', error);
    }
  };

  // Define addToCollection function for new Personal Kit API
  // States for personal details inline form when adding to collection
  const [showPersonalDetailsForm, setShowPersonalDetailsForm] = useState(false);
  const [selectedReferenceKit, setSelectedReferenceKit] = useState(null);
  const [selectedCollectionType, setSelectedCollectionType] = useState('');
  const [players, setPlayers] = useState([]); // For player dropdown
  const [playerNumbers, setPlayerNumbers] = useState([]); // For player number dropdown based on selected player
  const [personalDetails, setPersonalDetails] = useState({
    // Form Collection Kit fields according to specifications
    price_buy: '', // Price (buy)
    price_value: '', // Price Value
    player_name: '', // Player name* (Required - Dropdown from database)
    player_number: '', // Player number* (Required - Dropdown based on player)
    condition: 'good', // State (condition)
    info: '', // Info+ (free text)
    // Keep size for practical collection management
    size: '',
    // Printing/Flocking Details
    has_printing: false, // Whether the kit has printing (flocking)
    is_custom_printing: false, // Custom printing checkbox
    custom_print_text: '', // Custom print text
    // Physical Condition & Usage
    is_worn: false, // Whether the kit has been worn
    is_signed: false, // Whether the kit is signed
    signed_by: '', // Who signed the kit
    // Special Attributes
    is_match_worn: false, // Match worn status
    match_details: '', // Match details
    is_authenticated: false, // Authentication status
    authentication_details: '', // Authentication details
    // Purchase Details
    purchase_date: '', // Purchase date
    purchase_location: '', // Where it was purchased
    acquisition_story: '', // Story of how it was acquired
    times_worn: 0, // How many times worn
    // Marketplace
    for_sale: false // Option to list for sale on marketplace (coming soon)
  });

  const addToCollection = async (referenceKitId, collectionType) => {
    if (!user) {
      alert('You must be signed in to add items to your collection');
      return;
    }

    // Find the reference kit details
    const referenceKit = referenceKits.find(kit => kit.id === referenceKitId);
    if (!referenceKit) {
      alert('Reference kit not found');
      return;
    }

    if (collectionType === 'wanted') {
      // For "wanted" items, add directly without detailed form
      await addToWantedDirectly(referenceKit);
    } else {
      // For "owned" items, show detailed personal details form
      setSelectedReferenceKit(referenceKit);
      setSelectedCollectionType(collectionType);
      setShowPersonalDetailsForm(true);
    }
  };

  const addToWantedDirectly = async (referenceKit) => {
    try {
      console.log(`🔄 Adding Reference Kit ${referenceKit.id} to wanted list (remains as Reference Kit)`);
      
      const wantedKitData = {
        reference_kit_id: referenceKit.id,
        preferred_size: null, // Optional - user can specify later
        max_price_willing_to_pay: null, // Optional - user can specify later
        notes: null, // Optional notes
        priority: "medium" // Default priority
      };

      const response = await fetch(`${API}/api/wanted-kits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
        },
        body: JSON.stringify(wantedKitData)
      });

      const responseData = await response.json();

      if (response.ok) {
        console.log(`✅ Successfully added to wanted list (kit remains Reference Kit)`);
        alert(`Kit added to your want list! 🎯\n\nThe kit remains a Reference Kit - no personal details needed.`);
        loadKitStore(); // Refresh list
      } else {
        console.error(`❌ Failed to add to wanted list: ${response.status}`);
        console.error('Error details:', responseData);
        
        // Better error handling to avoid [object Object] display
        let errorMessage = 'Failed to add to want list';
        if (responseData && typeof responseData === 'object') {
          if (responseData.detail) {
            errorMessage = responseData.detail;
          } else if (responseData.message) {
            errorMessage = responseData.message;
          } else if (Array.isArray(responseData.detail)) {
            // Handle Pydantic validation errors
            errorMessage = responseData.detail.map(err => err.msg || err.message).join(', ');
          }
        }
        alert(`Error: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error adding to wanted list:', error);
      alert('Error adding to want list. Please try again.');
    }
  };

  // Handle adding reference kit to personal collection with simplified details
  const handlePersonalDetailsSubmit = async () => {
    if (!selectedReferenceKit) return;
    
    try {
      const personalKitData = {
        reference_kit_id: selectedReferenceKit.id,
        condition: personalDetails.condition,
        player_id: personalDetails.player_name,
        number: personalDetails.player_number,
        purchase_price: personalDetails.price_buy ? parseFloat(personalDetails.price_buy) : null,
        estimated_value: personalDetails.price_value ? parseFloat(personalDetails.price_value) : null
      };

      const response = await fetch(`${API}/api/personal-kits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(personalKitData)
      });

      if (response.ok) {
        console.log('✅ Successfully added to personal collection');
        setShowPersonalDetailsForm(false);
        
        // Reset form
        setPersonalDetails({
          condition: '',
          player_name: '',
          player_number: '',
          price_buy: '',
          price_value: ''
        });
        
        // Notify parent if callback provided
        if (onDataUpdate) onDataUpdate();
      } else {
        const errorData = await response.json();
        console.error('❌ Failed to add to personal collection:', errorData);
        alert(`Error: ${errorData.detail || 'Failed to add to collection'}`);
      }
    } catch (error) {
      console.error('Error adding to personal collection:', error);
      alert('Error adding to collection. Please try again.');
    }
  };

  // Define showReleaseDetails function
  const showReleaseDetails = (referenceKit) => {
    setSelectedReleaseForDetail(referenceKit);
    setShowReleaseDetailModal(true);
  };

  const loadKitStore = async () => {
    try {
      setLoading(true);
      
      // Build query parameters for new vestiaire API
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.team_id) params.append('team_id', filters.team_id);
      if (filters.season) params.append('season', filters.season);
      if (filters.kit_type) params.append('kit_type', filters.kit_type);

      console.log(`🔄 Loading kit store with params: ${params}`);
      
      const response = await fetch(`${API}/api/vestiaire?${params}`);
      
      console.log(`📥 Kit store response: ${response.status}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Loaded ${Array.isArray(data) ? data.length : 'non-array'} reference kits:`, data);
        
        if (Array.isArray(data)) {
          setReferenceKits(data);
        } else {
          console.warn('Kit Store API returned non-array data:', data);
          setReferenceKits([]);
        }
      } else {
        console.error(`❌ Kit Store API error: ${response.status}`);
        setReferenceKits([]);
      }
    } catch (error) {
      console.error('Error loading kit store:', error);
      setReferenceKits([]);
    } finally {
      setLoading(false);
    }
  };
  // Handle player selection and load their numbers for personal details modal
  const handlePlayerChange = async (playerId) => {
    setPersonalDetails(prev => ({ 
      ...prev, 
      player_name: playerId, 
      player_number: '' // Reset number when player changes
    }));
    
    if (playerId) {
      try {
        // Load player numbers for the selected player
        const response = await fetch(`${API}/api/players/${playerId}/numbers`);
        if (response.ok) {
          const numbers = await response.json();
          setPlayerNumbers(numbers);
        } else {
          // If no specific numbers endpoint, use a default set
          setPlayerNumbers(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']);
        }
      } catch (error) {
        console.error('Error loading player numbers:', error);
        // Default numbers if error
        setPlayerNumbers(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']);
      }
    } else {
      setPlayerNumbers([]);
    }
  };

  // Load players for dropdown
  const loadPlayers = async () => {
    try {
      const response = await fetch(`${API}/api/players`);
      if (response.ok) {
        const playersData = await response.json();
        setPlayers(playersData);
      }
    } catch (error) {
      console.error('Error loading players:', error);
    }
  };

  // Reference Kit Card Component
  const JerseyReleaseCard = ({ release }) => {
    const masterKitInfo = release.master_kit_info || {};
    const teamInfo = release.team_info || {};
    const brandInfo = release.brand_info || {};
    
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
                {release.is_limited_edition && (
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
                    Limited Edition
                  </span>
                )}
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {teamInfo.name || 'Unknown Team'} - {masterKitInfo.season || 'Unknown Season'}
              </h3>
              
              <div className="text-sm text-gray-600 space-y-1">
                <div>Kit Type: {masterKitInfo.kit_type || 'Unknown'}</div>
                <div>Model: {masterKitInfo.model || 'Unknown'}</div>
                <div>Brand: {brandInfo.name || 'Unknown'}</div>
                {release.available_sizes && release.available_sizes.length > 0 && (
                  <div>Sizes: {release.available_sizes.join(', ')}</div>
                )}
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-lg font-bold text-green-600">
                €{release.original_retail_price || 'N/A'}
              </div>
              <div className="text-sm text-gray-500">Original Price</div>
              {release.current_market_estimate && (
                <div className="text-sm text-blue-600 mt-1">
                  Est. €{release.current_market_estimate}
                </div>
              )}
            </div>
          </div>

          {/* Collection Statistics */}
          {(release.total_in_collections > 0 || release.total_for_sale > 0) && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-700 space-y-1">
                {release.total_in_collections > 0 && (
                  <div>👥 {release.total_in_collections} collectors own this</div>
                )}
                {release.total_for_sale > 0 && (
                  <div>🏪 {release.total_for_sale} available for sale</div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-2">
            {user && (
              <>
                <button
                  onClick={() => addToCollection(release.id, 'owned')}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  title="Add with detailed information (condition, price, size, etc.)"
                >
                  📝 Add to Owned
                </button>
                <button
                  onClick={() => addToCollection(release.id, 'wanted')}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  title="Add to want list (no details needed)"
                >
                  🎯 Add to Wanted
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

  // Reference Kit Detail Modal
  const JerseyReleaseDetailModal = ({ release, isOpen, onClose }) => {
    if (!isOpen || !release) return null;

    const masterKitInfo = release.master_kit_info || {};
    const teamInfo = release.team_info || {};
    const brandInfo = release.brand_info || {};

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Reference Kit Details</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>

          <div className="p-6 space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Reference Kit Information</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <div><span className="font-medium text-gray-900">Reference:</span> {release.topkit_reference || 'No reference'}</div>
                  <div><span className="font-medium text-gray-900">Available Sizes:</span> {release.available_sizes?.join(', ') || 'Not specified'}</div>
                  <div><span className="font-medium text-gray-900">Limited Edition:</span> {release.is_limited_edition ? 'Yes' : 'No'}</div>
                  <div><span className="font-medium text-gray-900">Verification:</span> {release.verified_level || 'Unverified'}</div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Pricing</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <div><span className="font-medium text-gray-900">Original Retail Price:</span> €{release.original_retail_price || 'N/A'}</div>
                  <div><span className="font-medium text-gray-900">Current Market Estimate:</span> €{release.current_market_estimate || 'N/A'}</div>
                  {release.price_range_min && release.price_range_max && (
                    <div><span className="font-medium text-gray-900">Price Range:</span> €{release.price_range_min} - €{release.price_range_max}</div>
                  )}
                </div>
              </div>
            </div>

            {/* Master Kit Information */}
            <div className="space-y-3">
              <h3 className="font-semibold text-lg text-gray-900">Master Kit Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
                <div className="space-y-2">
                  <div><span className="font-medium text-gray-900">Team:</span> {teamInfo.name || 'Unknown'}</div>
                  <div><span className="font-medium text-gray-900">Season:</span> {masterKitInfo.season || 'Unknown'}</div>
                  <div><span className="font-medium text-gray-900">Kit Type:</span> {masterKitInfo.kit_type || 'Unknown'}</div>
                </div>
                <div className="space-y-2">
                  <div><span className="font-medium text-gray-900">Brand:</span> {brandInfo.name || 'Unknown'}</div>
                  <div><span className="font-medium text-gray-900">Model:</span> {masterKitInfo.model || 'Unknown'}</div>
                  <div><span className="font-medium text-gray-900">Master Kit Reference:</span> {masterKitInfo.topkit_reference || 'No reference'}</div>
                </div>
              </div>
            </div>

            {/* Collection Statistics */}
            <div className="space-y-3">
              <h3 className="font-semibold text-lg text-gray-900">Collection Statistics</h3>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{release.total_in_collections || 0}</div>
                  <div className="text-blue-700">Collectors</div>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{release.total_for_sale || 0}</div>
                  <div className="text-green-700">For Sale</div>
                </div>
              </div>
            </div>

            {/* Available Prints */}
            {release.available_prints && release.available_prints.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Available Player Prints</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {release.available_prints.map((print, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded text-sm text-gray-700">
                      {print.player_name} #{print.number}
                    </div>
                  ))}
                </div>
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

  // Create Reference Kit Modal Component
  const CreateKitReleaseModal = () => {
    const [formData, setFormData] = useState({
      master_kit_id: '',
      league_competition: '', // League/Competition field
      model: 'replica', // Model field (Replica/Authentic)
      is_limited_edition: false,
      production_run: '',
      official_product_code: '', // SKU Code
      barcode: '', // Barcode field
      main_photo: null, // Main Photo (required)
      secondary_photos: [] // Secondary Photos
    });
    const [loading, setLoading] = useState(false);
    const [teams, setTeams] = useState([]);
    const [selectedTeam, setSelectedTeam] = useState('');
    const [masterKitsForTeam, setMasterKitsForTeam] = useState([]);
    const [loadingMasterKits, setLoadingMasterKits] = useState(false);
    const [competitions, setCompetitions] = useState([]); // New state for competitions
    const [mainPhotoPreview, setMainPhotoPreview] = useState(''); // Preview for main photo
    const [secondaryPhotoPreviews, setSecondaryPhotoPreviews] = useState([]); // Previews for secondary photos

    // Load teams when modal opens
    useEffect(() => {
      if (showCreateModal) {
        if (teams.length === 0) {
          loadTeams();
        }
        if (competitions.length === 0) {
          loadCompetitions();
        }
        if (players.length === 0) {
          loadPlayers();
        }
      }
    }, [showCreateModal]);

    const loadTeams = async () => {
      try {
        const response = await fetch(`${API}/api/teams`);
        if (response.ok) {
          const teamsData = await response.json();
          setTeams(teamsData);
        }
      } catch (error) {
        console.error('Error loading teams:', error);
      }
    };

    const loadCompetitions = async () => {
      try {
        const response = await fetch(`${API}/api/competitions`);
        if (response.ok) {
          const competitionsData = await response.json();
          setCompetitions(competitionsData);
        }
      } catch (error) {
        console.error('Error loading competitions:', error);
      }
    };

    const loadMasterKitsForTeam = async (teamId) => {
      setLoadingMasterKits(true);
      try {
        const response = await fetch(`${API}/api/master-kits?team_id=${teamId}`, {
          headers: {
            'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
          }
        });
        if (response.ok) {
          const masterKits = await response.json();
          setMasterKitsForTeam(masterKits);
        } else {
          setMasterKitsForTeam([]);
        }
      } catch (error) {
        console.error('Error loading master kits:', error);
        setMasterKitsForTeam([]);
      } finally {
        setLoadingMasterKits(false);
      }
    };

    const handleTeamChange = (teamId) => {
      setSelectedTeam(teamId);
      setFormData(prev => ({ ...prev, master_kit_id: '' })); // Reset master kit selection
      setMasterKitsForTeam([]); // Clear previous master kits
      
      if (teamId) {
        loadMasterKitsForTeam(teamId);
      }
    };

    // Load players for dropdown
    const loadPlayers = async () => {
      try {
        const response = await fetch(`${API}/api/players`);
        if (response.ok) {
          const playersData = await response.json();
          setPlayers(playersData);
        }
      } catch (error) {
        console.error('Error loading players:', error);
      }
    };

    // Handle player selection and load their numbers
    const handlePlayerChange = async (playerId) => {
      setPersonalDetails(prev => ({ 
        ...prev, 
        player_name: playerId, 
        player_number: '' // Reset number when player changes
      }));
      
      if (playerId) {
        try {
          // Load player numbers for the selected player
          const response = await fetch(`${API}/api/players/${playerId}/numbers`);
          if (response.ok) {
            const numbers = await response.json();
            setPlayerNumbers(numbers);
          } else {
            // If no specific numbers endpoint, use a default set
            setPlayerNumbers(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']);
          }
        } catch (error) {
          console.error('Error loading player numbers:', error);
          // Default numbers if error
          setPlayerNumbers(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']);
        }
      } else {
        setPlayerNumbers([]);
      }
    };

    // Photo handling functions
    const handleMainPhotoUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
          alert('Photo is too large. Maximum size is 5MB');
          return;
        }
        
        setFormData(prev => ({ ...prev, main_photo: file }));
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => setMainPhotoPreview(e.target.result);
        reader.readAsDataURL(file);
      }
    };

    const handleSecondaryPhotosUpload = (event) => {
      const files = Array.from(event.target.files);
      const maxFiles = 3; // back, left sleeve, right sleeve
      
      if (formData.secondary_photos.length + files.length > maxFiles) {
        alert(`You can only upload up to ${maxFiles} secondary photos`);
        return;
      }
      
      files.forEach(file => {
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
          alert(`Photo ${file.name} is too large. Maximum size is 5MB`);
          return;
        }
        
        setFormData(prev => ({
          ...prev,
          secondary_photos: [...prev.secondary_photos, file]
        }));
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          setSecondaryPhotoPreviews(prev => [...prev, e.target.result]);
        };
        reader.readAsDataURL(file);
      });
    };

    const removeSecondaryPhoto = (index) => {
      setFormData(prev => ({
        ...prev,
        secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
      }));
      setSecondaryPhotoPreviews(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      // Updated validation for Release Form Kit
      if (!formData.master_kit_id || !formData.league_competition || !formData.model || !formData.main_photo) {
        alert('Master Kit, League/Competition, Model, and Main Photo are required');
        return;
      }

      setLoading(true);
      try {
        // Convert photos to base64 for submission
        const convertToBase64 = (file) => {
          return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
          });
        };

        let mainPhotoBase64 = '';
        if (formData.main_photo) {
          mainPhotoBase64 = await convertToBase64(formData.main_photo);
        }

        let secondaryPhotosBase64 = [];
        for (const photo of formData.secondary_photos) {
          const base64 = await convertToBase64(photo);
          secondaryPhotosBase64.push(base64);
        }

        const submitData = {
          master_kit_id: formData.master_kit_id,
          league_competition: formData.league_competition,
          model: formData.model,
          is_limited_edition: formData.is_limited_edition,
          production_run: parseInt(formData.production_run) || null,
          official_product_code: formData.official_product_code, // SKU Code
          barcode: formData.barcode,
          main_photo: mainPhotoBase64,
          secondary_photos: secondaryPhotosBase64
        };

        const response = await fetch(`${API}/api/reference-kits`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
          },
          body: JSON.stringify(submitData)
        });

        if (response.ok) {
          alert('Reference Kit created successfully!');
          setShowCreateModal(false);
          // Reset form
          setFormData({
            master_kit_id: '',
            league_competition: '',
            model: 'replica',
            is_limited_edition: false,
            production_run: '',
            official_product_code: '',
            barcode: '',
            main_photo: null,
            secondary_photos: []
          });
          setMainPhotoPreview('');
          setSecondaryPhotoPreviews([]);
          loadKitStore(); // Refresh the list
        } else {
          const errorData = await response.json();
          alert(`Error: ${errorData.detail || 'Failed to create reference kit'}`);
        }
      } catch (error) {
        console.error('Error creating reference kit:', error);
        alert('Error creating reference kit');
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Add New Reference Kit</h2>
            <button
              onClick={() => setShowCreateModal(false)}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Step 1: Select Club */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Club *
              </label>
              <select
                value={selectedTeam}
                onChange={(e) => handleTeamChange(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Choose a club...</option>
                {teams.map(team => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </select>
              {teams.length === 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  Loading clubs...
                </p>
              )}
            </div>

            {/* Step 2: Select Master Kit (only shown after club selection) */}
            {selectedTeam && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Master Kit *
                </label>
                {loadingMasterKits ? (
                  <div className="w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-500">
                    Loading master kits for this club...
                  </div>
                ) : (
                  <select
                    value={formData.master_kit_id}
                    onChange={(e) => setFormData(prev => ({...prev, master_kit_id: e.target.value}))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Choose a master kit...</option>
                    {masterKitsForTeam.map(kit => (
                      <option key={kit.id} value={kit.id}>
                        {kit.season} {kit.kit_type} - {kit.design_name || `${kit.kit_type} Kit`}
                      </option>
                    ))}
                  </select>
                )}
                {masterKitsForTeam.length === 0 && selectedTeam && !loadingMasterKits && (
                  <div className="text-xs text-amber-600 mt-1 p-2 bg-amber-50 border border-amber-200 rounded">
                    <p><strong>No master kits found for this club.</strong></p>
                    <p>You need to create a Master Kit first before adding a Reference Kit.</p>
                    <button
                      type="button"
                      className="text-blue-600 hover:text-blue-800 underline mt-1"
                      onClick={() => {
                        setShowCreateModal(false);
                        if (onDataUpdate) {
                          onDataUpdate('master-jerseys'); // Navigate to master jersey creation
                        }
                      }}
                    >
                      → Create Master Kit for this club
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Reference Kit Details (only shown after master kit selection) */}
            {selectedTeam && formData.master_kit_id && (
              <>
                <div className="border-t pt-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Reference Kit Details</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Complete the commercial release information for this master kit.
                  </p>
                </div>

                {/* League/Competition */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    League/Competition *
                  </label>
                  <select
                    value={formData.league_competition}
                    onChange={(e) => setFormData(prev => ({...prev, league_competition: e.target.value}))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Choose a league/competition...</option>
                    {competitions.map(comp => (
                      <option key={comp.id} value={comp.id}>
                        {comp.competition_name || comp.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Model */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Model *
                  </label>
                  <select
                    value={formData.model}
                    onChange={(e) => setFormData(prev => ({...prev, model: e.target.value}))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Choose model type...</option>
                    <option value="replica">Replica</option>
                    <option value="authentic">Authentic</option>
                  </select>
                </div>

                {/* Limited Edition */}
                <div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="limited_edition"
                      checked={formData.is_limited_edition}
                      onChange={(e) => setFormData(prev => ({...prev, is_limited_edition: e.target.checked}))}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="limited_edition" className="ml-2 text-sm text-gray-700">
                      Limited Edition
                    </label>
                  </div>
                  
                  {/* Conditional field for number of units */}
                  {formData.is_limited_edition && (
                    <div className="mt-3">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Number of Units *
                      </label>
                      <input
                        type="number"
                        value={formData.production_run}
                        onChange={(e) => setFormData(prev => ({...prev, production_run: e.target.value}))}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter number of units produced"
                        required={formData.is_limited_edition}
                      />
                    </div>
                  )}
                </div>

                {/* SKU Code */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    SKU Code
                  </label>
                  <input
                    type="text"
                    value={formData.official_product_code}
                    onChange={(e) => setFormData(prev => ({...prev, official_product_code: e.target.value}))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., FN2345-413"
                  />
                </div>

                {/* Barcode */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Barcode
                  </label>
                  <input
                    type="text"
                    value={formData.barcode}
                    onChange={(e) => setFormData(prev => ({...prev, barcode: e.target.value}))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 1234567890123"
                  />
                </div>

                {/* Main Photo */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Main Photo (Front View) *
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleMainPhotoUpload}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    required
                  />
                  {mainPhotoPreview && (
                    <div className="mt-2">
                      <img 
                        src={mainPhotoPreview} 
                        alt="Main Photo Preview" 
                        className="w-32 h-32 object-cover rounded border"
                      />
                    </div>
                  )}
                </div>

                {/* Secondary Photos */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Secondary Photos (Back, Left Sleeve, Right Sleeve)
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleSecondaryPhotosUpload}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  />
                  {secondaryPhotoPreviews.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {secondaryPhotoPreviews.map((preview, index) => (
                        <div key={index} className="relative">
                          <img 
                            src={preview} 
                            alt={`Secondary Photo ${index + 1}`} 
                            className="w-24 h-24 object-cover rounded border"
                          />
                          <button
                            type="button"
                            onClick={() => removeSecondaryPhoto(index)}
                            className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Reference Kit'}
              </button>
            </div>
          </form>
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
          <div className="flex justify-between items-center mb-6">
            <div className="text-center flex-1">
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                👕 Kit Store
              </h1>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Discover all available physical versions of referenced kits.
                Add them to your collection and track their value!
              </p>
            </div>
            {user && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors ml-6"
              >
                Add New Reference Kit
              </button>
            )}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {Array.isArray(referenceKits) ? referenceKits.length : 0}
              </div>
              <div className="text-sm text-blue-700">Available Releases</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {Array.isArray(referenceKits) && referenceKits.length > 0 ? Math.round(referenceKits.reduce((sum, r) => sum + (r.current_market_estimate || r.original_retail_price || 0), 0) / referenceKits.length) : 0}€
              </div>
              <div className="text-sm text-green-700">Average Estimated Price</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {Array.isArray(referenceKits) ? referenceKits.reduce((sum, r) => sum + (r.total_in_collections || 0), 0) : 0}
              </div>
              <div className="text-sm text-purple-700">Total Collections</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 items-end">
            <input
              type="text"
              placeholder="Search reference kits..."
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
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
              onClick={loadKitStore}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Filter
            </button>
            <button 
              onClick={() => setFilters({search: '', team_id: '', season: '', kit_type: ''})}
              className="text-gray-600 hover:text-gray-800 px-4 py-2"
            >
              Reset
            </button>
            
            {/* Display Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">View</label>
              <div className="flex border border-gray-300 rounded">
                <button
                  onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'grid' }))}
                  className={`px-3 py-1 text-sm ${displayOptions.viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                  📊 Grid
                </button>
                <button
                  onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'thumbnail' }))}
                  className={`px-3 py-1 text-sm border-x border-gray-300 ${displayOptions.viewMode === 'thumbnail' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                  🖼️ Thumb
                </button>
                <button
                  onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'list' }))}
                  className={`px-3 py-1 text-sm ${displayOptions.viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                  📋 List
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
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Available Versions ({referenceKits.length})
            </h2>
            {user && (
              <button 
                onClick={loadKitStore}
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
        ) : referenceKits.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No kit releases found.</p>
          </div>
        ) : (
          <div className={`${displayOptions.viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 
                           displayOptions.viewMode === 'thumbnail' ? 'grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4' : 
                           'space-y-4'}`}>
            {referenceKits.map((release) => {
              // Grid View (Default)
              if (displayOptions.viewMode === 'grid') {
                return <JerseyReleaseCard key={release.id} release={release} />;
              }
              
              // Thumbnail View (Compact)
              else if (displayOptions.viewMode === 'thumbnail') {
                return (
                  <div key={release.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                       onClick={() => {
                         setSelectedReleaseForDetail(release);
                         setShowReleaseDetailModal(true);
                       }}>
                    <div className="aspect-square bg-gray-100 flex items-center justify-center text-2xl">
                      👕
                    </div>
                    <div className="p-2">
                      <h4 className="font-medium text-xs text-gray-900 mb-1 line-clamp-1">
                        {release.master_jersey_info?.team_info?.name || release.master_kit_info?.team_info?.name || 'Unknown Team'}
                      </h4>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600 truncate">
                          {release.master_jersey_info?.season || release.master_kit_info?.season || 'N/A'}
                        </span>
                        <span className="text-blue-600 font-semibold">
                          €{release.original_retail_price || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              }
              
              // List View (Detailed)
              else {
                return (
                  <div key={release.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start gap-6">
                      <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                        👕
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-semibold text-gray-900 mb-1">
                              {release.master_jersey_info?.team_info?.name || release.master_kit_info?.team_info?.name || 'Unknown Team'}
                            </h3>
                            <p className="text-sm text-gray-600">
                              {release.master_jersey_info?.season || release.master_kit_info?.season || 'N/A'} • {release.master_jersey_info?.jersey_type || release.master_kit_info?.jersey_type || 'N/A'}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold text-blue-600">
                              €{release.original_retail_price || 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500">
                              {release.topkit_reference}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                          {release.model_name && <span>Model: {release.model_name}</span>}
                          {release.release_type && <span>Type: {release.release_type}</span>}
                          {release.is_limited_edition && <span className="text-orange-600 font-medium">Limited Edition</span>}
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex gap-2">
                            <button
                              onClick={() => {
                                setSelectedReleaseForDetail(release);
                                setShowReleaseDetailModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                            >
                              View Details
                            </button>
                            {user && (
                              <button
                                onClick={() => {
                                  setSelectedReferenceKit(release);
                                  setSelectedCollectionType('personal');
                                  setShowPersonalDetailsForm(!showPersonalDetailsForm || selectedReferenceKit?.id !== release.id);
                                }}
                                className="text-green-600 hover:text-green-800 text-sm font-medium"
                              >
                                {showPersonalDetailsForm && selectedReferenceKit?.id === release.id ? 'Hide Form' : 'Add to Collection'}
                              </button>
                            )}
                          </div>
                          <div className="text-xs text-gray-500">
                            Created: {new Date(release.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      
                      {/* Inline Personal Details Form */}
                      {showPersonalDetailsForm && selectedReferenceKit?.id === release.id && selectedCollectionType === 'personal' && (
                        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">Add to My Collection</h3>
                            <p className="text-sm text-gray-600">
                              {selectedReferenceKit.master_kit_info?.team_info?.name || 'Unknown Team'} - {selectedReferenceKit.master_kit_info?.season || 'Unknown Season'}
                            </p>
                          </div>

                          <form onSubmit={(e) => { e.preventDefault(); handlePersonalDetailsSubmit(); }} className="space-y-4">
                            {/* Condition */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Condition (state of the kit)
                              </label>
                              <select
                                value={personalDetails.condition}
                                onChange={(e) => setPersonalDetails({...personalDetails, condition: e.target.value})}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                              >
                                <option value="">Select Condition</option>
                                <option value="New">New</option>
                                <option value="Excellent">Excellent</option>
                                <option value="Good">Good</option>
                                <option value="Fair">Fair</option>
                                <option value="Poor">Poor</option>
                              </select>
                            </div>

                            {/* Player */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Player
                              </label>
                              <select
                                value={personalDetails.player_name}
                                onChange={(e) => handlePlayerChange(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                              >
                                <option value="">Select Player</option>
                                {players.map(player => (
                                  <option key={player.id} value={player.id}>{player.name}</option>
                                ))}
                              </select>
                            </div>

                            {/* Number */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Number (player's jersey number)
                              </label>
                              <input
                                type="number"
                                value={personalDetails.player_number}
                                onChange={(e) => setPersonalDetails({...personalDetails, player_number: e.target.value})}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                                placeholder="10"
                              />
                            </div>

                            {/* Purchase Price */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Purchase Price
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                value={personalDetails.price_buy}
                                onChange={(e) => setPersonalDetails({...personalDetails, price_buy: e.target.value})}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                                placeholder="99.99"
                              />
                            </div>

                            {/* Estimated Value */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Estimated Value
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                value={personalDetails.price_value}
                                onChange={(e) => setPersonalDetails({...personalDetails, price_value: e.target.value})}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                                placeholder="120.00"
                              />
                            </div>

                            {/* Submit Button */}
                            <div className="flex space-x-3 pt-4">
                              <button
                                type="button"
                                onClick={() => setShowPersonalDetailsForm(false)}
                                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium"
                              >
                                Cancel
                              </button>
                              <button
                                type="submit"
                                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
                              >
                                Add to Collection
                              </button>
                            </div>
                          </form>
                        </div>
                      )}
                    </div>
                  </div>
                );
              }
            })}
          </div>
        )}
      </div>

      {/* Jersey Release Detail Modal */}
      <JerseyReleaseDetailModal
        release={selectedReleaseForDetail}
        isOpen={showReleaseDetailModal}
        onClose={() => setShowReleaseDetailModal(false)}
      />

      {/* Create Kit Release Modal */}
      {showCreateModal && <CreateKitReleaseModal />}


    </div>
  );
};

export default VestiairePage;