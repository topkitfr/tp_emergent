import React, { useState, useEffect, useMemo } from 'react';

const MyCollectionPage = ({ user, API, onDataUpdate }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('owned');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [editFormData, setEditFormData] = useState({});

  useEffect(() => {
    if (user) {
      loadCollections();
    }
  }, [user]);

  const loadCollections = async () => {
    if (!user?.id) return;
    
    try {
      setLoading(true);
      console.log('🔄 Loading reference kit collections for user:', user.id);

      // Load both owned and wanted reference kit collections using the new endpoints
      const [ownedResponse, wantedResponse] = await Promise.all([
        fetch(`${API}/api/users/${user.id}/reference-kit-collections/owned`, {
          headers: {
            'Authorization': `Bearer ${user.token}`
          }
        }),
        fetch(`${API}/api/users/${user.id}/reference-kit-collections/wanted`, {
          headers: {
            'Authorization': `Bearer ${user.token}`
          }
        })
      ]);

      console.log('📥 Reference Kit Collection responses:', {
        owned: ownedResponse.status,
        wanted: wantedResponse.status
      });

      if (ownedResponse.ok && wantedResponse.ok) {
        const [ownedData, wantedData] = await Promise.all([
          ownedResponse.json(),
          wantedResponse.json()
        ]);

        console.log('📊 Reference Kit Collections Data:', {
          owned: Array.isArray(ownedData) ? ownedData.length : 'not array',
          wanted: Array.isArray(wantedData) ? wantedData.length : 'not array'
        });

        // Combine collections with type markers
        const allCollections = [
          ...(Array.isArray(ownedData) ? ownedData.map(item => ({ ...item, collection_type: 'owned' })) : []),
          ...(Array.isArray(wantedData) ? wantedData.map(item => ({ ...item, collection_type: 'wanted' })) : [])
        ];

        setCollections(allCollections);
        
        console.log('Reference Kit Collections Data:', {
          owned: Array.isArray(ownedData) ? ownedData : [],
          wanted: Array.isArray(wantedData) ? wantedData : [],
          ownedCount: Array.isArray(ownedData) ? ownedData.length : 0,
          wantedCount: Array.isArray(wantedData) ? wantedData.length : 0
        });
      } else {
        console.error('❌ Failed to load reference kit collections');
        setCollections([]);
      }
    } catch (error) {
      console.error('Error loading reference kit collections:', error);
      setCollections([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter collections based on active tab and search
  const filteredCollections = collections.filter((item) => {
    // Filter by tab
    const matchesTab = item.collection_type === activeTab;
    
    // Filter by search query
    if (searchQuery) {
      const referenceKit = item.reference_kit_info || {};
      const masterKit = item.master_kit_info || {};
      const teamInfo = item.team_info || {};
      
      const matchesSearch = 
        item.printed_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        teamInfo.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        referenceKit.topkit_reference?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        masterKit.topkit_reference?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchesTab && matchesSearch;
    }
    
    // If no search query, just filter by tab
    return matchesTab;
  });

  const collectionValue = useMemo(() => {
    const ownedItems = collections.filter(c => c.collection_type === 'owned');
    
    let totalLow = 0;
    let totalMid = 0;
    let totalHigh = 0;
    
    ownedItems.forEach(item => {
      // Use reference kit pricing or fallback to purchase price
      const referenceKit = item.reference_kit_info || {};
      const baseValue = item.purchase_price || referenceKit.original_retail_price || referenceKit.current_market_estimate || 50;
      const condition = item.condition || 'good';
      
      // Condition multiplier
      const conditionMultiplier = {
        'mint': 1.2,
        'near_mint': 1.1,
        'good': 1.0,
        'fair': 0.8,
        'poor': 0.6
      };
      
      const multiplier = conditionMultiplier[condition] || 1.0;
      
      // Calculate range
      const lowValue = baseValue * multiplier * 0.8;
      const midValue = baseValue * multiplier;
      const highValue = baseValue * multiplier * 1.2;
      
      totalLow += lowValue;
      totalMid += midValue;
      totalHigh += highValue;
    });
    
    return {
      low: Math.round(totalLow),
      mid: Math.round(totalMid),
      high: Math.round(totalHigh),
      count: ownedItems.length
    };
  }, [collections]);

  // Use useMemo to ensure reactive updates
  const ownedCount = useMemo(() => {
    return collections.filter(c => c.collection_type === 'owned').length;
  }, [collections]);

  const wantedCount = useMemo(() => {
    return collections.filter(c => c.collection_type === 'wanted').length;
  }, [collections]);

  const handleEditItem = (item) => {
    setEditingItem(item);
    setEditFormData({
      // Basic fields
      size: item.size || '',
      condition: item.condition || 'good',
      
      // Purchase Information - Match creation form field names
      price_buy: item.purchase_price || item.price_buy || '', // Map purchase_price to price_buy
      price_value: item.price_value || '', // Current value estimate
      purchase_date: item.purchase_date || '',
      purchase_location: item.purchase_location || '',
      
      // Personal Notes - Map personal_notes to info to match creation form
      info: item.personal_notes || item.info || '', // Map personal_notes to info
      
      // Printing Details - Match creation form structure
      has_printing: item.has_printing || false,
      is_custom_printing: item.is_custom_printing || false,
      player_name: item.printed_name || item.player_name || '', // Map printed_name to player_name
      player_number: item.printed_number || item.player_number || '', // Map printed_number to player_number
      custom_print_text: item.custom_print_text || '',
      
      // Physical Details
      is_worn: item.is_worn || false,
      is_signed: item.is_signed || false,
      signed_by: item.signed_by || '',
      
      // Special Attributes  
      is_match_worn: item.is_match_worn || false,
      match_details: item.match_details || '',
      is_authenticated: item.is_authenticated || false,
      authentication_details: item.authentication_details || '',
      
      // Collection Management
      times_worn: item.times_worn || 0,
      acquisition_story: item.acquisition_story || '',
      
      // Marketplace
      for_sale: item.is_for_sale || item.for_sale || false,
      asking_price: item.asking_price || ''
    });
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;

    try {
      // Map frontend form fields to backend field names
      const backendData = {
        // Basic fields
        size: editFormData.size,
        condition: editFormData.condition,
        
        // Purchase Information - Map to backend field names
        purchase_price: parseFloat(editFormData.price_buy) || null,
        price_value: parseFloat(editFormData.price_value) || null,
        purchase_date: editFormData.purchase_date || null,
        purchase_location: editFormData.purchase_location || null,
        
        // Personal Notes - Map info back to personal_notes for backend
        personal_notes: editFormData.info || null,
        acquisition_story: editFormData.acquisition_story || null,
        
        // Printing Details - Map to backend field names
        has_printing: editFormData.has_printing,
        printed_name: editFormData.player_name || null, // Map player_name back to printed_name
        printed_number: parseInt(editFormData.player_number) || null, // Map player_number back to printed_number
        printing_type: editFormData.is_custom_printing ? 'custom' : 'player',
        
        // Physical Details
        is_worn: editFormData.is_worn,
        is_signed: editFormData.is_signed,
        signed_by: editFormData.signed_by || null,
        
        // Special Attributes
        is_match_worn: editFormData.is_match_worn,
        match_details: editFormData.match_details || null,
        is_authenticated: editFormData.is_authenticated,
        authentication_details: editFormData.authentication_details || null,
        
        // Collection Management
        times_worn: parseInt(editFormData.times_worn) || 0,
        
        // Marketplace
        for_sale: editFormData.for_sale,
        asking_price: parseFloat(editFormData.asking_price) || null
      };

      console.log('🔄 Updating personal kit with data:', backendData);

      const response = await fetch(`${API}/api/personal-kits/${editingItem.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`
        },
        body: JSON.stringify(backendData)
      });

      if (response.ok) {
        console.log('✅ Personal kit updated successfully');
        await loadCollections(); // Reload collections
        setEditingItem(null);
        setEditFormData({});
        alert('Personal kit updated successfully!');
      } else {
        const errorData = await response.json();
        console.error('❌ Update failed:', errorData);
        alert(`Error: ${errorData.detail || 'Failed to update personal kit'}`);
      }
    } catch (error) {
      console.error('Error updating personal kit:', error);
      alert('Error updating personal kit');
    }
  };

  const handleDeleteItem = async (item) => {
    // Determine if this is an owned item (PersonalKit) or wanted item (WantedKit)
    const isOwnedItem = activeTab === 'owned';
    const itemType = isOwnedItem ? 'owned collection' : 'want list';
    const confirmMessage = `Are you sure you want to remove this kit from your ${itemType}?`;
    
    if (!confirm(confirmMessage)) return;

    try {
      console.log(`🗑️ Attempting to delete item:`, {
        item_id: item.id,
        item_type: itemType,
        active_tab: activeTab,
        is_owned: isOwnedItem,
        user_token_length: user.token ? user.token.length : 'no token'
      });
      
      // Use different endpoints for owned vs wanted items
      const endpoint = isOwnedItem 
        ? `${API}/api/personal-kits/${item.id}`  // Delete PersonalKit
        : `${API}/api/wanted-kits/${item.id}`;   // Delete WantedKit
      
      console.log(`🎯 DELETE endpoint: ${endpoint}`);
      
      const response = await fetch(endpoint, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${user.token || localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      console.log(`📥 DELETE response:`, {
        status: response.status,
        ok: response.ok,
        endpoint: endpoint
      });

      if (response.ok) {
        console.log(`✅ Successfully deleted from ${itemType}`);
        await loadCollections(); // Reload collections
        alert(`Kit removed from ${itemType}!`);
      } else {
        const errorData = await response.json();
        console.error(`❌ Delete failed:`, errorData);
        alert(`Error: ${errorData.detail || `Failed to remove from ${itemType}`}`);
      }
    } catch (error) {
      console.error(`Error deleting from ${itemType}:`, error);
      alert(`Error removing from ${itemType}`);
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
              Manage your personal kit collection and track its estimated value
            </p>
          </div>

          {/* Collection Value Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{ownedCount}</div>
              <div className="text-sm text-blue-700">Owned Kits</div>
            </div>
            <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{wantedCount}</div>
              <div className="text-sm text-red-700">Wanted Kits</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-lg font-bold text-green-600">€{collectionValue.low} - €{collectionValue.high}</div>
              <div className="text-sm text-green-700">Estimated Value Range</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">€{collectionValue.mid}</div>
              <div className="text-sm text-purple-700">Average Estimated Value</div>
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
            <input
              type="text"
              placeholder="Search in my collection..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
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
              ? 'Start adding kits to your collection'
              : 'Add kits to your wishlist'
            }
          </p>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCollections.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                {/* Kit Image */}
                <div className="w-full h-48 bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                  <span className="text-4xl">👕</span>
                </div>

                {/* Kit Details */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                      {item.reference_kit_info?.topkit_reference || 'No Ref'}
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
                    {item.printed_name || item.team_info?.name || 'Unknown Kit'}
                  </h3>
                  
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Team: {item.team_info?.name || 'Unknown'}</div>
                    <div>Season: {item.master_kit_info?.season || 'Unknown'}</div>
                    {item.size && <div>Size: {item.size}</div>}
                    {item.condition && <div>Condition: {item.condition}</div>}
                    {item.is_signed && <div>✍️ Signed {item.signed_by ? `by ${item.signed_by}` : ''}</div>}
                    {item.has_printing && item.printed_name && (
                      <div>👕 Printed: {item.printed_name} {item.printed_number ? `#${item.printed_number}` : ''}</div>
                    )}
                  </div>

                  {/* Pricing Information */}
                  <div className="border-t pt-3 mt-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Original Price:</span>
                      <span className="font-medium">€{item.reference_kit_info?.original_retail_price || 'N/A'}</span>
                    </div>
                    {item.purchase_price && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Paid:</span>
                        <span className="font-medium">€{item.purchase_price}</span>
                      </div>
                    )}
                    {item.reference_kit_info?.current_market_estimate && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Market Estimate:</span>
                        <span className="font-medium text-blue-600">€{item.reference_kit_info.current_market_estimate}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  {/* Edit button ONLY for owned items (PersonalKits) */}
                  {activeTab === 'owned' && (
                    <button
                      onClick={() => handleEditItem(item)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors"
                      title="Edit personal kit details"
                    >
                      Edit Details
                    </button>
                  )}
                  
                  {/* Remove button for both owned and wanted items */}
                  <button
                    onClick={() => handleDeleteItem(item)}
                    className={`${activeTab === 'owned' ? 'flex-1' : 'w-full'} bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors`}
                    title={`Remove from ${activeTab === 'owned' ? 'owned collection' : 'want list'}`}
                  >
                    {activeTab === 'owned' ? 'Remove from Collection' : 'Remove from Want List'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Edit Modal - IDENTICAL to Creation Form */}
      {editingItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Edit Kit Details</h2>
              <button
                onClick={() => setEditingItem(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6">
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-900">
                  {editingItem.team_info?.name || 'Unknown Team'} - {editingItem.master_kit_info?.season || 'Unknown Season'}
                </h3>
                <p className="text-sm text-gray-600">
                  Editing details for your <span className="font-medium text-green-600">owned collection</span>
                </p>
              </div>

              <div className="space-y-4">
                {/* Price Information */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">💰 Purchase Information</h3>
                  
                  {/* Price (buy) */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Price</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editFormData.price_buy || ''}
                      onChange={(e) => setEditFormData({...editFormData, price_buy: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      placeholder="99.99"
                    />
                  </div>

                  {/* Price Value */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Value Estimate</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editFormData.price_value || ''}
                      onChange={(e) => setEditFormData({...editFormData, price_value: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      placeholder="120.00"
                    />
                  </div>

                  {/* Purchase Date */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Date</label>
                    <input
                      type="date"
                      value={editFormData.purchase_date || ''}
                      onChange={(e) => setEditFormData({...editFormData, purchase_date: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Purchase Location */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Location</label>
                    <input
                      type="text"
                      value={editFormData.purchase_location || ''}
                      onChange={(e) => setEditFormData({...editFormData, purchase_location: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Official club store, online retailer, etc."
                    />
                  </div>
                </div>

                {/* Physical Details */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">👕 Physical Details</h3>
                  
                  {/* Size */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Size</label>
                    <select
                      value={editFormData.size || ''}
                      onChange={(e) => setEditFormData({...editFormData, size: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select size</option>
                      <option value="XS">XS</option>
                      <option value="S">S</option>
                      <option value="M">M</option>
                      <option value="L">L</option>
                      <option value="XL">XL</option>
                      <option value="XXL">XXL</option>
                    </select>
                  </div>

                  {/* Condition Details */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Condition Details</label>
                    <select
                      value={editFormData.condition || 'good'}
                      onChange={(e) => setEditFormData({...editFormData, condition: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="mint">Mint - New with tags, perfect condition</option>
                      <option value="near_mint">Near Mint - Like new, minor wear</option>
                      <option value="excellent">Excellent - Very good condition, light wear</option>
                      <option value="good">Good - Normal wear, all functional</option>
                      <option value="fair">Fair - Noticeable wear, still wearable</option>
                      <option value="poor">Poor - Heavy wear, damage visible</option>
                    </select>
                  </div>

                  {/* Usage Status Checkboxes */}
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="edit_is_worn"
                        checked={editFormData.is_worn || false}
                        onChange={(e) => setEditFormData({...editFormData, is_worn: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="edit_is_worn" className="ml-2 block text-sm text-gray-900">
                        I have worn this kit
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="edit_is_signed"
                        checked={editFormData.is_signed || false}
                        onChange={(e) => setEditFormData({...editFormData, is_signed: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="edit_is_signed" className="ml-2 block text-sm text-gray-900">
                        This kit is signed
                      </label>
                    </div>

                    {/* Signed by field - Only show if is_signed is true */}
                    {editFormData.is_signed && (
                      <div className="ml-6">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Signed by</label>
                        <input
                          type="text"
                          value={editFormData.signed_by || ''}
                          onChange={(e) => setEditFormData({...editFormData, signed_by: e.target.value})}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="Player name or person who signed"
                        />
                      </div>
                    )}

                    {/* Additional Usage Details */}
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="edit_is_match_worn"
                        checked={editFormData.is_match_worn || false}
                        onChange={(e) => setEditFormData({...editFormData, is_match_worn: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="edit_is_match_worn" className="ml-2 block text-sm text-gray-900">
                        Match worn (actual game use)
                      </label>
                    </div>

                    {editFormData.is_match_worn && (
                      <div className="ml-6">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Match details</label>
                        <input
                          type="text"
                          value={editFormData.match_details || ''}
                          onChange={(e) => setEditFormData({...editFormData, match_details: e.target.value})}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="e.g., Champions League Final 2023, vs Barcelona"
                        />
                      </div>
                    )}
                  </div>
                </div>

                {/* Printing (Flocking) Section */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Printing (Flocking)</h3>
                  
                  {/* Has Printing Toggle */}
                  <div className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      id="edit_has_printing"
                      checked={editFormData.has_printing || false}
                      onChange={(e) => setEditFormData({
                        ...editFormData, 
                        has_printing: e.target.checked,
                        // Reset printing fields if unchecked
                        player_name: e.target.checked ? editFormData.player_name : '',
                        player_number: e.target.checked ? editFormData.player_number : '',
                        is_custom_printing: false
                      })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="edit_has_printing" className="ml-2 block text-sm text-gray-900">
                      This kit has printing/flocking
                    </label>
                  </div>

                  {/* Printing Fields - Only show if has_printing is true */}
                  {editFormData.has_printing && (
                    <div className="space-y-4 pl-6 border-l-2 border-blue-200">
                      {/* Custom Printing Checkbox */}
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="edit_is_custom_printing"
                          checked={editFormData.is_custom_printing || false}
                          onChange={(e) => setEditFormData({
                            ...editFormData, 
                            is_custom_printing: e.target.checked,
                            // Reset player fields if custom printing is selected
                            player_name: e.target.checked ? '' : editFormData.player_name,
                            player_number: e.target.checked ? '' : editFormData.player_number
                          })}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="edit_is_custom_printing" className="ml-2 block text-sm text-gray-900">
                          Custom Printing (non-player name/number)
                        </label>
                      </div>

                      {/* Player Name Input - Only show if NOT custom printing */}
                      {!editFormData.is_custom_printing && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Player Name {editFormData.has_printing && !editFormData.is_custom_printing ? '(Required)' : ''}
                          </label>
                          <input
                            type="text"
                            value={editFormData.player_name || ''}
                            onChange={(e) => setEditFormData({...editFormData, player_name: e.target.value})}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter player name"
                          />
                        </div>
                      )}

                      {/* Player Number Input - Only show if player name exists and NOT custom printing */}
                      {editFormData.player_name && !editFormData.is_custom_printing && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Player Number</label>
                          <input
                            type="number"
                            value={editFormData.player_number || ''}
                            onChange={(e) => setEditFormData({...editFormData, player_number: e.target.value})}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter player number"
                          />
                        </div>
                      )}

                      {/* Custom Printing Text - Only show if custom printing is selected */}
                      {editFormData.is_custom_printing && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Custom Print Text</label>
                          <input
                            type="text"
                            value={editFormData.custom_print_text || ''}
                            onChange={(e) => setEditFormData({...editFormData, custom_print_text: e.target.value})}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                            placeholder="e.g., Your Name, Custom Text, etc."
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Additional Notes */}
                <div className="border-b border-gray-200 pb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">📝 Additional Notes</label>
                  <textarea
                    value={editFormData.info || ''}
                    onChange={(e) => setEditFormData({...editFormData, info: e.target.value})}
                    rows="3"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="Additional information about this kit (purchase story, wear occasions, etc.)"
                  />
                </div>

                {/* Marketplace Options */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">🏪 Marketplace Options</h3>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="edit_for_sale"
                      checked={editFormData.for_sale || false}
                      onChange={(e) => setEditFormData({...editFormData, for_sale: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      disabled
                    />
                    <label htmlFor="edit_for_sale" className="ml-2 block text-sm text-gray-500">
                      List for sale on marketplace (Coming Soon)
                    </label>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    This feature will be available soon. You'll be able to list your kits for sale to other collectors.
                  </p>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 mt-6">
                <button
                  onClick={() => setEditingItem(null)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  ✅ Update Kit Details
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyCollectionPage;