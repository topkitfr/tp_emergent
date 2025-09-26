import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Edit, Trash2, Search, Eye } from 'lucide-react';
import EnhancedEditKitForm from '../components/EnhancedEditKitForm';

const MyCollectionPage = ({ user, API, onDataUpdate }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('owned');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [editFormData, setEditFormData] = useState({});
  const [priceEstimations, setPriceEstimations] = useState({}); // Store price estimations
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      loadCollections();
    }
  }, [user]);

  const loadCollections = async () => {
    if (!user?.id) return;
    
    // Get token with proper validation
    const token = user.token || localStorage.getItem('token');
    if (!token) {
      console.error('❌ No authentication token available');
      setCollections([]);
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      console.log('🔄 Loading My Collection for user:', user.id);

      const response = await fetch(`${API}/api/my-collection`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('📥 My Collection response:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('📊 My Collection Data:', Array.isArray(data) ? data.length : 'not array', data);
        setCollections(Array.isArray(data) ? data : []);
        
        // Load price estimations for all collection items
        if (Array.isArray(data) && data.length > 0) {
          await loadPriceEstimations(data, token);
        }
      } else {
        console.error('❌ Failed to load My Collection');
        setCollections([]);
      }
    } catch (error) {
      console.error('Error loading My Collection:', error);
      setCollections([]);
    } finally {
      setLoading(false);
    }
  };

  const loadPriceEstimations = async (collectionItems, token) => {
    try {
      const estimations = {};
      
      // Load price estimations for each collection item
      for (const item of collectionItems) {
        try {
          const response = await fetch(`${API}/api/my-collection/${item.id}/price-estimation`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const priceData = await response.json();
            estimations[item.id] = priceData;
          }
        } catch (error) {
          console.error(`Error loading price estimation for item ${item.id}:`, error);
        }
      }
      
      setPriceEstimations(estimations);
    } catch (error) {
      console.error('Error loading price estimations:', error);
    }
  };

  // Filter collections based on active tab and search
  const filteredCollections = collections.filter((item) => {
    // Filter by tab (owned/wanted)
    const matchesTab = item.collection_type === activeTab;
    
    // Filter by search query
    if (searchQuery) {
      const masterKit = item.master_kit || {};
      
      const matchesSearch = 
        item.name_printing?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        masterKit.club?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        masterKit.season?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        masterKit.brand?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        masterKit.topkit_reference?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchesTab && matchesSearch;
    }
    
    return matchesTab;
  });

  const collectionValue = useMemo(() => {
    // Only calculate value for owned items
    const ownedItems = collections.filter(c => c.collection_type === 'owned');
    
    let totalUserEstimate = 0;
    let totalTopKitEstimate = 0;
    let itemsWithUserEstimate = 0;
    let itemsWithTopKitEstimate = 0;
    
    ownedItems.forEach(item => {
      // User estimate calculation (from field F. User Estimate)
      if (item.user_estimate) {
        totalUserEstimate += parseFloat(item.user_estimate);
        itemsWithUserEstimate++;
      }
      
      // TopKit estimated price calculation
      const estimation = priceEstimations[item.id];
      if (estimation?.estimated_price) {
        totalTopKitEstimate += estimation.estimated_price;
        itemsWithTopKitEstimate++;
      }
    });
    
    return {
      totalUserEstimate: Math.round(totalUserEstimate),
      totalTopKitEstimate: Math.round(totalTopKitEstimate),
      averageUserEstimate: itemsWithUserEstimate > 0 ? Math.round(totalUserEstimate / itemsWithUserEstimate) : 0,
      averageTopKitEstimate: itemsWithTopKitEstimate > 0 ? Math.round(totalTopKitEstimate / itemsWithTopKitEstimate) : 0,
      count: ownedItems.length,
      itemsWithUserEstimate,
      itemsWithTopKitEstimate
    };
  }, [collections, priceEstimations]);

  // Use useMemo to ensure reactive updates
  const ownedCount = useMemo(() => {
    return collections.filter(c => c.collection_type === 'owned').length;
  }, [collections]);

  const wantedCount = useMemo(() => {
    return collections.filter(c => c.collection_type === 'wanted').length;
  }, [collections]);

  const handleEditItem = (item) => {
    setEditingItem(item);
    
    // Convert purchase_date from ISO string to YYYY-MM-DD format for date input
    let formattedPurchaseDate = '';
    if (item.purchase_date) {
      try {
        const date = new Date(item.purchase_date);
        if (!isNaN(date.getTime())) {
          // Format as YYYY-MM-DD for HTML date input
          formattedPurchaseDate = date.toISOString().split('T')[0];
        }
      } catch (error) {
        console.warn('Invalid purchase_date format:', item.purchase_date);
      }
    }

    // Convert match_date from ISO string to YYYY-MM-DD format for date input
    let formattedMatchDate = '';
    if (item.match_date) {
      try {
        const date = new Date(item.match_date);
        if (!isNaN(date.getTime())) {
          // Format as YYYY-MM-DD for HTML date input
          formattedMatchDate = date.toISOString().split('T')[0];
        }
      } catch (error) {
        console.warn('Invalid match_date format:', item.match_date);
      }
    }

    // Convert patches from string to array if needed
    let patchesArray = [];
    if (item.patches) {
      if (typeof item.patches === 'string') {
        patchesArray = item.patches.split(',').map(p => p.trim()).filter(p => p);
      } else if (Array.isArray(item.patches)) {
        patchesArray = item.patches;
      }
    } else if (item.patches_list) {
      patchesArray = Array.isArray(item.patches_list) ? item.patches_list : [];
    }

    // Convert authenticity_proof to array if needed
    let authenticityProofArray = [];
    if (item.authenticity_proof) {
      authenticityProofArray = Array.isArray(item.authenticity_proof) ? item.authenticity_proof : [];
    }
    
    setEditFormData({
      // A. Basic Information
      gender: item.gender || '',
      size: item.size || '',
      
      // B. Player & Printing
      associated_player: item.associated_player_id || '',
      name_printing: item.name_printing || '',
      number_printing: item.number_printing || '',
      
      // C. Origin & Authenticity
      origin_type: item.origin_type || '',
      competition: item.competition || '',
      authenticity_proof: authenticityProofArray,
      match_date: formattedMatchDate,
      opponent: item.opponent_id || '',
      
      // D. Physical Condition
      general_condition: item.general_condition || '',
      photo_urls: item.photo_urls || [],
      
      // E. Technical Details
      patches: patchesArray,
      other_patches: item.other_patches || '',
      signature: item.signature || false,
      signature_player: item.signature_player_id || '',
      signature_certificate: item.signature_certificate || '',
      
      // F. User Estimate
      user_estimate: item.user_estimate || '',
      
      // G. Comments
      comments: item.comments || '',
      
      // Legacy fields (for backward compatibility)
      is_signed: item.is_signed || false,
      signed_by: item.signed_by || '',
      condition: item.condition || '',
      condition_other: item.condition_other || '',
      physical_state: item.physical_state || '',
      purchase_price: item.purchase_price || '',
      purchase_date: formattedPurchaseDate,
      personal_notes: item.personal_notes || ''
    });
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;

    // Get token with proper validation
    const token = user?.token || localStorage.getItem('token');
    if (!token) {
      console.error('❌ No authentication token available for edit');
      return;
    }

    try {
      // Prepare form data with proper type conversions and empty field handling
      const processedFormData = {};
      
      // Helper function to add non-empty values to processed data
      const addFieldIfNotEmpty = (fieldName, value) => {
        if (value !== null && value !== undefined && value !== '') {
          processedFormData[fieldName] = value;
        }
      };
      
      // A. Basic Information
      addFieldIfNotEmpty('gender', editFormData.gender);
      addFieldIfNotEmpty('size', editFormData.size);
      
      // B. Player & Printing
      addFieldIfNotEmpty('associated_player_id', editFormData.associated_player);
      addFieldIfNotEmpty('name_printing', editFormData.name_printing);
      addFieldIfNotEmpty('number_printing', editFormData.number_printing);
      
      // C. Origin & Authenticity
      addFieldIfNotEmpty('origin_type', editFormData.origin_type);
      addFieldIfNotEmpty('competition', editFormData.competition);
      if (editFormData.authenticity_proof && Array.isArray(editFormData.authenticity_proof) && editFormData.authenticity_proof.length > 0) {
        processedFormData.authenticity_proof = editFormData.authenticity_proof;
      }
      if (editFormData.match_date && editFormData.match_date !== '') {
        try {
          const dateObj = new Date(editFormData.match_date + 'T00:00:00.000Z');
          processedFormData.match_date = dateObj.toISOString();
        } catch (error) {
          console.error('❌ Error converting match_date:', error);
          alert('Error: Match date must be a valid date');
          return;
        }
      }
      addFieldIfNotEmpty('opponent_id', editFormData.opponent);
      
      // D. Physical Condition
      addFieldIfNotEmpty('general_condition', editFormData.general_condition);
      if (editFormData.photo_urls && Array.isArray(editFormData.photo_urls) && editFormData.photo_urls.length > 0) {
        processedFormData.photo_urls = editFormData.photo_urls;
      }
      
      // E. Technical Details
      // Handle patches conversion from array to string for backend compatibility
      if (editFormData.patches && Array.isArray(editFormData.patches) && editFormData.patches.length > 0) {
        processedFormData.patches = editFormData.patches.join(', ');
        processedFormData.patches_list = editFormData.patches; // Keep array version too
      }
      addFieldIfNotEmpty('other_patches', editFormData.other_patches);
      
      // Process signature fields
      processedFormData.signature = editFormData.signature || false;
      if (editFormData.signature) {
        addFieldIfNotEmpty('signature_player_id', editFormData.signature_player);
        addFieldIfNotEmpty('signature_certificate', editFormData.signature_certificate);
      }
      
      // F. User Estimate
      if (editFormData.user_estimate && editFormData.user_estimate !== '') {
        const estimateValue = parseFloat(editFormData.user_estimate);
        if (isNaN(estimateValue)) {
          alert('Error: User estimate must be a valid number');
          return;
        }
        processedFormData.user_estimate = estimateValue;
      }
      
      // G. Comments
      addFieldIfNotEmpty('comments', editFormData.comments);
      
      // Legacy fields (for backward compatibility) - only add if not already covered by new fields
      if (!processedFormData.signature) {
        processedFormData.is_signed = editFormData.is_signed || false;
      }
      addFieldIfNotEmpty('signed_by', editFormData.signed_by);
      addFieldIfNotEmpty('condition', editFormData.condition);
      addFieldIfNotEmpty('condition_other', editFormData.condition_other);
      addFieldIfNotEmpty('physical_state', editFormData.physical_state);
      addFieldIfNotEmpty('personal_notes', editFormData.personal_notes);
      
      // Convert purchase_price to float if provided
      if (editFormData.purchase_price && editFormData.purchase_price !== '') {
        const priceValue = parseFloat(editFormData.purchase_price);
        if (isNaN(priceValue)) {
          alert('Error: Purchase price must be a valid number');
          return;
        }
        processedFormData.purchase_price = priceValue;
      }
      
      // Convert purchase_date to ISO string if provided (YYYY-MM-DD format to ISO datetime)
      if (editFormData.purchase_date && editFormData.purchase_date !== '') {
        console.log('🗓️ Processing purchase_date:', editFormData.purchase_date);
        try {
          // Create a date object from the YYYY-MM-DD string and convert to ISO string
          const dateObj = new Date(editFormData.purchase_date + 'T00:00:00.000Z');
          processedFormData.purchase_date = dateObj.toISOString();
          console.log('✅ Converted purchase_date to ISO:', processedFormData.purchase_date);
        } catch (error) {
          console.error('❌ Error converting purchase_date:', error);
          alert('Error: Purchase date must be a valid date');
          return;
        }
      } else {
        console.log('📝 Purchase date is empty, will be omitted from request');
      }

      console.log('📤 Sending update data:', processedFormData);

      const response = await fetch(`${API}/api/my-collection/${editingItem.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(processedFormData)
      });

      if (response.ok) {
        console.log('✅ Collection item updated successfully');
        
        // Get the updated data from the response
        const updatedItemData = await response.json();
        
        // Reload collections with price estimations
        await loadCollections();
        
        // Update the editing item with new data to keep modal open
        setEditingItem(updatedItemData);
        
        // Update form data with the saved values for continued editing
        const formattedUpdatedPurchaseDate = updatedItemData.purchase_date ? 
          new Date(updatedItemData.purchase_date).toISOString().split('T')[0] : '';
        const formattedUpdatedMatchDate = updatedItemData.match_date ? 
          new Date(updatedItemData.match_date).toISOString().split('T')[0] : '';

        // Convert patches back to array format for the form
        let updatedPatchesArray = [];
        if (updatedItemData.patches) {
          if (typeof updatedItemData.patches === 'string') {
            updatedPatchesArray = updatedItemData.patches.split(',').map(p => p.trim()).filter(p => p);
          } else if (Array.isArray(updatedItemData.patches)) {
            updatedPatchesArray = updatedItemData.patches;
          }
        } else if (updatedItemData.patches_list) {
          updatedPatchesArray = Array.isArray(updatedItemData.patches_list) ? updatedItemData.patches_list : [];
        }

        let updatedAuthenticityProofArray = [];
        if (updatedItemData.authenticity_proof) {
          updatedAuthenticityProofArray = Array.isArray(updatedItemData.authenticity_proof) ? updatedItemData.authenticity_proof : [];
        }
        
        setEditFormData({
          // A. Basic Information
          gender: updatedItemData.gender || '',
          size: updatedItemData.size || '',
          
          // B. Player & Printing
          associated_player: updatedItemData.associated_player_id || '',
          name_printing: updatedItemData.name_printing || '',
          number_printing: updatedItemData.number_printing || '',
          
          // C. Origin & Authenticity
          origin_type: updatedItemData.origin_type || '',
          competition: updatedItemData.competition || '',
          authenticity_proof: updatedAuthenticityProofArray,
          match_date: formattedUpdatedMatchDate,
          opponent: updatedItemData.opponent_id || '',
          
          // D. Physical Condition
          general_condition: updatedItemData.general_condition || '',
          photo_urls: updatedItemData.photo_urls || [],
          
          // E. Technical Details
          patches: updatedPatchesArray,
          other_patches: updatedItemData.other_patches || '',
          signature: updatedItemData.signature || false,
          signature_player: updatedItemData.signature_player_id || '',
          signature_certificate: updatedItemData.signature_certificate || '',
          
          // F. User Estimate
          user_estimate: updatedItemData.user_estimate || '',
          
          // G. Comments
          comments: updatedItemData.comments || '',
          
          // Legacy fields (for backward compatibility)
          is_signed: updatedItemData.is_signed || false,
          signed_by: updatedItemData.signed_by || '',
          condition: updatedItemData.condition || '',
          condition_other: updatedItemData.condition_other || '',
          physical_state: updatedItemData.physical_state || '',
          purchase_price: updatedItemData.purchase_price || '',
          purchase_date: formattedUpdatedPurchaseDate,
          personal_notes: updatedItemData.personal_notes || ''
        });
        
        alert('✅ Kit details updated successfully! You can continue editing or close the modal.');
      } else {
        const errorData = await response.json();
        console.error('❌ Update failed:', errorData);
        
        // Handle different error formats
        let errorMessage = 'Failed to update kit details';
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // Handle validation errors from Pydantic
            errorMessage = errorData.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join('\n');
          } else if (typeof errorData.detail === 'object') {
            // Handle object errors
            errorMessage = JSON.stringify(errorData.detail, null, 2);
          }
        }
        
        alert(`Error: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error updating collection item:', error);
      
      // Handle network or unexpected errors
      let errorMessage = 'Error updating kit details';
      if (error.message) {
        errorMessage = `Network error: ${error.message}`;
      }
      
      alert(errorMessage);
    }
  };

  const handleDeleteItem = async (item) => {
    const confirmMessage = `Are you sure you want to remove this kit from your collection?`;
    
    if (!confirm(confirmMessage)) return;

    // Get token with proper validation
    const token = user?.token || localStorage.getItem('token');
    if (!token) {
      console.error('❌ No authentication token available for delete');
      return;
    }

    try {
      console.log(`🗑️ Attempting to delete collection item:`, item.id);
      
      const response = await fetch(`${API}/api/my-collection/${item.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log(`📥 DELETE response:`, response.status);

      if (response.ok) {
        console.log(`✅ Successfully deleted from collection`);
        await loadCollections(); // Reload collections
        alert('Kit removed from collection!');
      } else {
        const errorData = await response.json();
        console.error(`❌ Delete failed:`, errorData);
        alert(`Error: ${errorData.detail || 'Failed to remove from collection'}`);
      }
    } catch (error) {
      console.error('Error deleting from collection:', error);
      alert('Error removing from collection');
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign In Required</h1>
          <p className="text-gray-600">You need to sign in to view your collection.</p>
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
              💎 My Collection
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Manage your personal kit collection with detailed information and track its value
            </p>
          </div>

          {/* Collection Stats */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-8">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{ownedCount}</div>
              <div className="text-sm text-blue-700">Owned Kits</div>
            </div>
            <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{wantedCount}</div>
              <div className="text-sm text-red-700">Wanted Kits</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">€{collectionValue.totalUserEstimate}</div>
              <div className="text-sm text-green-700">User Estimates</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">€{collectionValue.totalTopKitEstimate}</div>
              <div className="text-sm text-purple-700">TopKit Estimates</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">€{collectionValue.averageTopKitEstimate}</div>
              <div className="text-sm text-yellow-700">Avg. TopKit Est.</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-0">
            <button
              onClick={() => setActiveTab('owned')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                activeTab === 'owned'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">💎</span>
              Owned ({ownedCount})
            </button>
            
            <button
              onClick={() => setActiveTab('wanted')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                activeTab === 'wanted'
                  ? 'border-red-600 text-red-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'  
              }`}
            >
              <span className="mr-2">❤️</span>
              Wanted ({wantedCount})
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search in my collection..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Collection Grid */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading your collection...</p>
        </div>
      ) : filteredCollections.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">
            {activeTab === 'owned' ? '💎' : '❤️'}
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {activeTab === 'owned' ? 'No owned kits' : 'No wanted kits'}
          </h3>
          <p className="text-gray-600">
            {activeTab === 'owned' 
              ? 'Start adding Master Kits to your collection from the Kit Area'
              : 'Start adding Master Kits to your want list from the Kit Area'
            }
          </p>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gaps-6">
            {filteredCollections.map((item) => {
              const masterKit = item.master_kit || {};
              return (
                <div
                  key={item.id}
                  className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/my-collection/${item.id}`)}
                  title="Click to view detailed page"
                >
                  {/* Kit Image - Prioritize personal photos over master kit photos */}
                  <div className="w-full h-48 bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                    {(() => {
                      // Priority 1: Personal photos from Edit Kit Details form
                      const personalPhotos = item.photo_urls || [];
                      if (personalPhotos.length > 0) {
                        const firstPhoto = personalPhotos[0];
                        const photoUrl = firstPhoto.startsWith('http') 
                          ? firstPhoto 
                          : firstPhoto.startsWith('uploads/') ? 
                            `${API}/api/${firstPhoto}` :
                            `${API}/api/uploads/personal_photos/${firstPhoto}`;
                        
                        return (
                          <img
                            src={photoUrl}
                            alt={`Personal ${masterKit.club || 'Unknown'} ${masterKit.season || ''}`}
                            className="w-full h-48 object-contain rounded-lg"
                          />
                        );
                      }
                      
                      // Priority 2: Master kit photos (fallback)
                      if (masterKit.front_photo_url) {
                        return (
                          <img
                            src={masterKit.front_photo_url.startsWith('http') 
                              ? masterKit.front_photo_url 
                              : masterKit.front_photo_url.startsWith('uploads/') ? 
                                `${API}/api/${masterKit.front_photo_url}` :
                                `${API}/api/uploads/${masterKit.front_photo_url}`}
                            alt={`${masterKit.club || 'Unknown'} ${masterKit.season || ''}`}
                            className="w-full h-48 object-contain rounded-lg opacity-60"
                          />
                        );
                      }
                      
                      // Priority 3: Default kit icon
                      return <span className="text-4xl">👕</span>;
                    })()}
                  </div>

                  {/* Kit Details */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center space-x-2">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                        {masterKit.topkit_reference || 'No Ref'}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.collection_type === 'owned' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {item.collection_type === 'owned' ? 'OWNED' : 'WANTED'}
                      </span>
                    </div>
                    
                    <h3 className="font-semibold text-gray-900">
                      {item.name_printing || masterKit.club || 'Unknown Kit'}
                      {item.number_printing && ` #${item.number_printing}`}
                    </h3>
                    
                    <div className="text-sm text-gray-600 space-y-1">
                      <div><strong>Club:</strong> {masterKit.club || 'Unknown'}</div>
                      <div><strong>Season:</strong> {masterKit.season || 'Unknown'}</div>
                      <div><strong>Type:</strong> {masterKit.kit_style || masterKit.kit_type || 'Unknown'}</div>
                      <div><strong>Brand:</strong> {masterKit.brand || 'Unknown'}</div>
                      <div><strong>Model:</strong> {masterKit.model || 'Unknown'}</div>
                      {item.size && <div><strong>Size:</strong> {item.size}</div>}
                      {item.condition && <div><strong>Condition:</strong> {item.condition}</div>}
                      {item.general_condition && <div><strong>Physical Condition:</strong> {item.general_condition.replace('_', ' ')}</div>}
                      {item.origin_type && <div><strong>Origin:</strong> {item.origin_type.replace('_', ' ')}</div>}
                      {(item.signature || item.is_signed) && <div>✍️ <strong>Signed</strong> {item.signed_by ? `by ${item.signed_by}` : ''}</div>}
                      {item.patches && <div>🏆 <strong>Patches:</strong> {item.patches}</div>}
                      {item.comments && <div><strong>Comments:</strong> {item.comments}</div>}
                    </div>

                    {/* Pricing Information */}
                    <div className="border-t pt-3 mt-3">
                      {/* User Estimate (from form field F) */}
                      {item.collection_type === 'owned' && item.user_estimate && (
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-600">User Estimate:</span>
                          <span className="font-bold text-blue-600">€{item.user_estimate}</span>
                        </div>
                      )}
                      
                      {/* TopKit Estimated Price (calculated with coefficients) */}
                      {item.collection_type === 'owned' && priceEstimations[item.id] && (
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-600">TopKit Estimate:</span>
                          <span className="font-bold text-purple-600">€{priceEstimations[item.id].estimated_price}</span>
                        </div>
                      )}

                      {/* User vs TopKit Estimate Comparison */}
                      {item.collection_type === 'owned' && item.user_estimate && priceEstimations[item.id] && (
                        <div className="flex justify-between text-sm mt-1">
                          <span className="text-gray-600">Estimate Difference:</span>
                          {(() => {
                            const userEstimate = parseFloat(item.user_estimate);
                            const topkitEstimate = priceEstimations[item.id].estimated_price;
                            const difference = userEstimate - topkitEstimate;
                            const percentage = ((difference / topkitEstimate) * 100).toFixed(1);
                            
                            return (
                              <span className={`font-medium text-xs ${difference >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                                {difference >= 0 ? '+' : ''}€{difference.toFixed(2)} ({percentage}%)
                              </span>
                            );
                          })()}
                        </div>
                      )}
                      
                      {item.purchase_date && (
                        <div className="flex justify-between text-sm mt-1">
                          <span className="text-gray-600">Purchase Date:</span>
                          <span className="font-medium">{new Date(item.purchase_date).toLocaleDateString()}</span>
                        </div>
                      )}
                      
                      {/* Price Estimation Details (only for owned items) */}
                      {item.collection_type === 'owned' && priceEstimations[item.id]?.calculation_details && (
                        <div className="mt-2 pt-2 border-t border-gray-100">
                          <details className="text-xs">
                            <summary className="cursor-pointer text-gray-500 hover:text-gray-700">Price Breakdown</summary>
                            <div className="mt-2 space-y-1 text-gray-600">
                              <div>Base: €{priceEstimations[item.id].calculation_details.base_price} ({masterKit.model})</div>
                              {priceEstimations[item.id].calculation_details.coefficients_applied?.map((coeff, idx) => (
                                <div key={idx}>+ {coeff.factor}: {coeff.value}</div>
                              ))}
                              <div className="font-medium pt-1 border-t">{priceEstimations[item.id].calculation_details.formula}</div>
                            </div>
                          </details>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    {/* View Details button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/my-collection/${item.id}`);
                      }}
                      className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1"
                      title="View detailed page"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View</span>
                    </button>
                    
                    {/* Edit button ONLY for owned items */}
                    {item.collection_type === 'owned' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditItem(item);
                        }}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1"
                        title="Edit personal details"
                      >
                        <Edit className="w-4 h-4" />
                        <span>Edit</span>
                      </button>
                    )}
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteItem(item);
                      }}
                      className={`${item.collection_type === 'owned' ? 'flex-1' : 'flex-1'} bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1`}
                      title={`Remove from ${item.collection_type === 'owned' ? 'collection' : 'want list'}`}
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>Remove</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Enhanced Edit Modal */}
      <EnhancedEditKitForm
        isOpen={!!editingItem}
        onClose={() => setEditingItem(null)}
        editingItem={editingItem}
        formData={editFormData}
        onFormDataChange={(key, value) => setEditFormData({...editFormData, [key]: value})}
        onSave={handleSaveEdit}
        API={process.env.REACT_APP_BACKEND_URL}
      />
    </div>
  );
};

export default MyCollectionPage;