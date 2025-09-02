import React, { useState, useEffect } from 'react';

const VestiairePage = ({ user, API, onDataUpdate }) => {
  const [referenceKits, setReferenceKits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    team_id: '',
    season: '',
    kit_type: ''
  });
  const [showReleaseDetailModal, setShowReleaseDetailModal] = useState(false);
  const [selectedReleaseForDetail, setSelectedReleaseForDetail] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadKitStore();
  }, []);

  // Define addToCollection function for new Personal Kit API
  // States for personal details modal when adding to collection
  const [showPersonalDetailsModal, setShowPersonalDetailsModal] = useState(false);
  const [selectedReferenceKit, setSelectedReferenceKit] = useState(null);
  const [selectedCollectionType, setSelectedCollectionType] = useState('');
  const [personalDetails, setPersonalDetails] = useState({
    size: '',
    condition: 'good',
    purchase_price: '',
    purchase_date: '',
    is_signed: false,
    signed_by: '',
    has_printing: false,
    printed_name: '',
    printed_number: '',
    is_worn: false,
    personal_notes: ''
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

    // Show personal details modal instead of directly creating
    setSelectedReferenceKit(referenceKit);
    setSelectedCollectionType(collectionType);
    setShowPersonalDetailsModal(true);
  };

  const handlePersonalDetailsSubmit = async () => {
    if (!selectedReferenceKit || !selectedCollectionType) return;

    try {
      console.log(`🔄 Adding Reference Kit ${selectedReferenceKit.id} to ${selectedCollectionType} collection with personal details`);
      
      const personalKitData = {
        reference_kit_id: selectedReferenceKit.id,
        collection_type: selectedCollectionType,
        ...personalDetails,
        purchase_price: personalDetails.purchase_price ? parseFloat(personalDetails.purchase_price) : null,
        printed_number: personalDetails.printed_number ? parseInt(personalDetails.printed_number) : null
      };

      const response = await fetch(`${API}/api/personal-kits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
        },
        body: JSON.stringify(personalKitData)
      });

      const responseData = await response.json();

      if (response.ok) {
        console.log(`✅ Successfully added to ${selectedCollectionType} collection with personal details`);
        alert(`Kit added to ${selectedCollectionType === 'owned' ? 'owned' : 'wanted'} collection!`);
        
        // Reset modal state
        setShowPersonalDetailsModal(false);
        setSelectedReferenceKit(null);
        setSelectedCollectionType('');
        setPersonalDetails({
          size: '',
          condition: 'good',
          purchase_price: '',
          purchase_date: '',
          is_signed: false,
          signed_by: '',
          has_printing: false,
          printed_name: '',
          printed_number: '',
          is_worn: false,
          personal_notes: ''
        });
        
        loadKitStore(); // Refresh list
      } else {
        console.error(`❌ Failed to add to collection: ${response.status}`);
        alert(`Error: ${responseData.detail || 'Failed to add to collection'}`);
      }
    } catch (error) {
      console.error('Error adding to collection:', error);
      alert('Error adding to collection');
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
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Reference:</span> {release.topkit_reference || 'No reference'}</div>
                  <div><span className="font-medium">Available Sizes:</span> {release.available_sizes?.join(', ') || 'Not specified'}</div>
                  <div><span className="font-medium">Limited Edition:</span> {release.is_limited_edition ? 'Yes' : 'No'}</div>
                  <div><span className="font-medium">Verification:</span> {release.verified_level || 'Unverified'}</div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold text-lg text-gray-900">Pricing</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Original Retail Price:</span> €{release.original_retail_price || 'N/A'}</div>
                  <div><span className="font-medium">Current Market Estimate:</span> €{release.current_market_estimate || 'N/A'}</div>
                  {release.price_range_min && release.price_range_max && (
                    <div><span className="font-medium">Price Range:</span> €{release.price_range_min} - €{release.price_range_max}</div>
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
                  <div><span className="font-medium">Season:</span> {masterKitInfo.season || 'Unknown'}</div>
                  <div><span className="font-medium">Kit Type:</span> {masterKitInfo.kit_type || 'Unknown'}</div>
                </div>
                <div className="space-y-2">
                  <div><span className="font-medium">Brand:</span> {brandInfo.name || 'Unknown'}</div>
                  <div><span className="font-medium">Model:</span> {masterKitInfo.model || 'Unknown'}</div>
                  <div><span className="font-medium">Master Kit Reference:</span> {masterKitInfo.topkit_reference || 'No reference'}</div>
                </div>
              </div>
            </div>

            {/* Collection Statistics */}
            <div className="space-y-3">
              <h3 className="font-semibold text-lg text-gray-900">Collection Statistics</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
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
                    <div key={index} className="p-2 bg-gray-50 rounded text-sm">
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
      league_competition: '', // New field for League/Competition
      model: 'replica', // New required field (Replica/Authentic)
      available_sizes: [],
      original_retail_price: '',
      current_market_estimate: '',
      is_limited_edition: false,
      production_run: '',
      official_product_code: '', // This becomes SKU Code
      barcode: '', // New field for Barcoding
      main_photo: null, // New required field for Main Photo
      secondary_photos: [] // New field for Secondary Photos
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
      if (teams.length === 0) {
        loadTeams();
      }
      if (competitions.length === 0) {
        loadCompetitions();
      }
    }, []);

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

    const handleSizeToggle = (size) => {
      const sizes = formData.available_sizes || [];
      if (sizes.includes(size)) {
        setFormData(prev => ({
          ...prev,
          available_sizes: sizes.filter(s => s !== size)
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          available_sizes: [...sizes, size]
        }));
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
          available_sizes: formData.available_sizes,
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
            available_sizes: [],
            original_retail_price: '',
            current_market_estimate: '',
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
            {/* Step 1: Select Club/Team */}
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
            </div>

            {/* Step 2: Select Master Kit (only shown after team selection) */}
            {selectedTeam && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Master Kit *
                </label>
                {loadingMasterKits ? (
                  <div className="w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-500">
                    Loading master kits...
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
                  <p className="text-xs text-gray-500 mt-1">
                    No master kits found for this club. Create a Master Kit first.
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Sizes
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['XS', 'S', 'M', 'L', 'XL', 'XXL'].map(size => (
                  <button
                    key={size}
                    type="button"
                    onClick={() => handleSizeToggle(size)}
                    className={`px-3 py-2 text-sm rounded border transition-colors ${
                      formData.available_sizes.includes(size)
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SKU Code
                </label>
                <input
                  type="text"
                  value={formData.official_product_code}
                  onChange={(e) => setFormData(prev => ({...prev, official_product_code: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  placeholder="FN2345-413"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Barcoding
                </label>
                <input
                  type="text"
                  value={formData.barcode}
                  onChange={(e) => setFormData(prev => ({...prev, barcode: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  placeholder="1234567890123"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Production Run
                </label>
                <input
                  type="number"
                  value={formData.production_run}
                  onChange={(e) => setFormData(prev => ({...prev, production_run: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  placeholder="Total pieces"
                />
              </div>
            </div>

            {/* League/Competition - Required Field */}
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
                    {comp.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Model - Required Field */}
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
                <option value="replica">Replica</option>
                <option value="authentic">Authentic</option>
              </select>
            </div>

            {/* Main Photo - Required Field */}
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

            {/* Secondary Photos - Optional */}
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {referenceKits.map((release) => (
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

      {/* Create Kit Release Modal */}
      {showCreateModal && <CreateKitReleaseModal />}

      {/* Personal Details Modal - When Adding to Collection */}
      {showPersonalDetailsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Add Personal Details</h2>
              <button
                onClick={() => setShowPersonalDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6">
              {selectedReferenceKit && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900">
                    {selectedReferenceKit.team_info?.name || 'Unknown Team'} - {selectedReferenceKit.master_kit_info?.season || 'Unknown Season'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Adding to: <span className="font-medium">{selectedCollectionType === 'owned' ? 'Owned Collection' : 'Wanted List'}</span>
                  </p>
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Size *</label>
                  <select
                    value={personalDetails.size}
                    onChange={(e) => setPersonalDetails({...personalDetails, size: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select your size</option>
                    <option value="XS">XS</option>
                    <option value="S">S</option>
                    <option value="M">M</option>
                    <option value="L">L</option>
                    <option value="XL">XL</option>
                    <option value="XXL">XXL</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
                  <select
                    value={personalDetails.condition}
                    onChange={(e) => setPersonalDetails({...personalDetails, condition: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="mint">Mint</option>
                    <option value="near_mint">Near Mint</option>
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                    <option value="poor">Poor</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price You Paid (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={personalDetails.purchase_price}
                    onChange={(e) => setPersonalDetails({...personalDetails, purchase_price: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="How much did you pay?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Date</label>
                  <input
                    type="date"
                    value={personalDetails.purchase_date}
                    onChange={(e) => setPersonalDetails({...personalDetails, purchase_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_worn"
                      checked={personalDetails.is_worn}
                      onChange={(e) => setPersonalDetails({...personalDetails, is_worn: e.target.checked})}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="is_worn" className="ml-2 text-sm text-gray-700">
                      Worn
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_signed"
                      checked={personalDetails.is_signed}
                      onChange={(e) => setPersonalDetails({...personalDetails, is_signed: e.target.checked})}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="is_signed" className="ml-2 text-sm text-gray-700">
                      Signed
                    </label>
                  </div>

                  {personalDetails.is_signed && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Signed by</label>
                      <input
                        type="text"
                        value={personalDetails.signed_by}
                        onChange={(e) => setPersonalDetails({...personalDetails, signed_by: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                        placeholder="Player name or person who signed"
                      />
                    </div>
                  )}

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="has_printing"
                      checked={personalDetails.has_printing}
                      onChange={(e) => setPersonalDetails({...personalDetails, has_printing: e.target.checked})}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="has_printing" className="ml-2 text-sm text-gray-700">
                      Has Player Print
                    </label>
                  </div>

                  {personalDetails.has_printing && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Player Name</label>
                        <input
                          type="text"
                          value={personalDetails.printed_name}
                          onChange={(e) => setPersonalDetails({...personalDetails, printed_name: e.target.value})}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="Player name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Number</label>
                        <input
                          type="number"
                          value={personalDetails.printed_number}
                          onChange={(e) => setPersonalDetails({...personalDetails, printed_number: e.target.value})}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="10"
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Personal Notes</label>
                  <textarea
                    value={personalDetails.personal_notes}
                    onChange={(e) => setPersonalDetails({...personalDetails, personal_notes: e.target.value})}
                    rows="3"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="Any special notes about this kit..."
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 mt-6">
                <button
                  onClick={() => setShowPersonalDetailsModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePersonalDetailsSubmit}
                  disabled={!personalDetails.size}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  Add to {selectedCollectionType === 'owned' ? 'Owned' : 'Wanted'} Collection
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VestiairePage;