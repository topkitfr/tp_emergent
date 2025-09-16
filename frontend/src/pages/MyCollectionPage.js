import React, { useState, useEffect, useMemo } from 'react';
import { Edit, Trash2, Search } from 'lucide-react';

const MyCollectionPage = ({ user, API, onDataUpdate }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('owned');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [editFormData, setEditFormData] = useState({});
  const [priceEstimations, setPriceEstimations] = useState({}); // Store price estimations

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
    
    let totalPurchaseValue = 0;
    let totalEstimatedValue = 0;
    let itemsWithPurchasePrice = 0;
    let itemsWithEstimatedPrice = 0;
    
    ownedItems.forEach(item => {
      // Purchase price calculation
      if (item.purchase_price) {
        totalPurchaseValue += item.purchase_price;
        itemsWithPurchasePrice++;
      }
      
      // Estimated price calculation
      const estimation = priceEstimations[item.id];
      if (estimation?.estimated_price) {
        totalEstimatedValue += estimation.estimated_price;
        itemsWithEstimatedPrice++;
      }
    });
    
    return {
      totalPurchase: Math.round(totalPurchaseValue),
      totalEstimated: Math.round(totalEstimatedValue),
      averagePurchase: itemsWithPurchasePrice > 0 ? Math.round(totalPurchaseValue / itemsWithPurchasePrice) : 0,
      averageEstimated: itemsWithEstimatedPrice > 0 ? Math.round(totalEstimatedValue / itemsWithEstimatedPrice) : 0,
      count: ownedItems.length,
      itemsWithPurchasePrice,
      itemsWithEstimatedPrice
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
    setEditFormData({
      name_printing: item.name_printing || '',
      number_printing: item.number_printing || '',
      patches: item.patches || '',
      is_signed: item.is_signed || false,
      signed_by: item.signed_by || '',
      condition: item.condition || '',
      condition_other: item.condition_other || '',
      physical_state: item.physical_state || '',
      size: item.size || '',
      purchase_price: item.purchase_price || '',
      purchase_date: item.purchase_date || '',
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
      // Prepare form data with proper type conversions
      const processedFormData = { ...editFormData };
      
      // Convert purchase_price to float if provided
      if (processedFormData.purchase_price && processedFormData.purchase_price !== '') {
        const priceValue = parseFloat(processedFormData.purchase_price);
        if (isNaN(priceValue)) {
          alert('Error: Purchase price must be a valid number');
          return;
        }
        processedFormData.purchase_price = priceValue;
      } else {
        // Remove empty purchase_price to avoid validation errors
        delete processedFormData.purchase_price;
      }
      
      // Convert purchase_date to ISO string if provided (YYYY-MM-DD format to ISO datetime)
      if (processedFormData.purchase_date && processedFormData.purchase_date !== '') {
        try {
          // Create a date object from the YYYY-MM-DD string and convert to ISO string
          const dateObj = new Date(processedFormData.purchase_date + 'T00:00:00.000Z');
          processedFormData.purchase_date = dateObj.toISOString();
        } catch (error) {
          alert('Error: Purchase date must be a valid date');
          return;
        }
      } else {
        // Remove empty purchase_date to avoid validation errors
        delete processedFormData.purchase_date;
      }

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
        
        // Update form data to reflect the saved changes
        setEditFormData({
          name_printing: updatedItemData.name_printing || '',
          number_printing: updatedItemData.number_printing || '',
          patches: updatedItemData.patches || '',
          is_signed: updatedItemData.is_signed || false,
          signed_by: updatedItemData.signed_by || '',
          condition: updatedItemData.condition || '',
          condition_other: updatedItemData.condition_other || '',
          physical_state: updatedItemData.physical_state || '',
          size: updatedItemData.size || '',
          purchase_price: updatedItemData.purchase_price || '',
          purchase_date: updatedItemData.purchase_date || '',
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
              <div className="text-2xl font-bold text-green-600">€{collectionValue.totalPurchase}</div>
              <div className="text-sm text-green-700">Purchase Value</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">€{collectionValue.totalEstimated}</div>
              <div className="text-sm text-purple-700">Estimated Value</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">€{collectionValue.averageEstimated}</div>
              <div className="text-sm text-yellow-700">Avg. Estimated</div>
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
                  className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
                >
                  {/* Kit Image */}
                  <div className="w-full h-48 bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                    {masterKit.front_photo_url ? (
                      <img
                        src={masterKit.front_photo_url.startsWith('http') 
                          ? masterKit.front_photo_url 
                          : masterKit.front_photo_url.startsWith('uploads/') ? 
                            `${API}/api/${masterKit.front_photo_url}` :
                            `${API}/api/uploads/master_kits/${masterKit.front_photo_url}.jpg`}
                        alt={`${masterKit.club || 'Unknown'} ${masterKit.season || ''}`}
                        className="w-full h-48 object-contain rounded-lg"
                      />
                    ) : (
                      <span className="text-4xl">👕</span>
                    )}
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
                      <div>Club: {masterKit.club || 'Unknown'}</div>
                      <div>Season: {masterKit.season || 'Unknown'}</div>
                      <div>Type: {masterKit.kit_type || 'Unknown'}</div>
                      <div>Brand: {masterKit.brand || 'Unknown'}</div>
                      {item.size && <div>Size: {item.size}</div>}
                      {item.condition && <div>Condition: {item.condition}</div>}
                      {item.is_signed && <div>✍️ Signed {item.signed_by ? `by ${item.signed_by}` : ''}</div>}
                      {item.patches && <div>🏆 Patches: {item.patches}</div>}
                    </div>

                    {/* Pricing Information */}
                    <div className="border-t pt-3 mt-3">
                      {/* Estimated Price (always shown for owned items) */}
                      {item.collection_type === 'owned' && priceEstimations[item.id] && (
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-600">Estimated Value:</span>
                          <span className="font-bold text-purple-600">€{priceEstimations[item.id].estimated_price}</span>
                        </div>
                      )}
                      
                      {/* Purchase Price */}
                      {item.purchase_price && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Purchase Price:</span>
                          <span className="font-medium text-green-600">€{item.purchase_price}</span>
                        </div>
                      )}
                      
                      {/* Value Comparison */}
                      {item.collection_type === 'owned' && item.purchase_price && priceEstimations[item.id] && (
                        <div className="flex justify-between text-sm mt-1">
                          <span className="text-gray-600">Value Change:</span>
                          {(() => {
                            const purchasePrice = item.purchase_price;
                            const estimatedPrice = priceEstimations[item.id].estimated_price;
                            const difference = estimatedPrice - purchasePrice;
                            const percentage = ((difference / purchasePrice) * 100).toFixed(1);
                            
                            return (
                              <span className={`font-medium ${difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
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
                    {/* Edit button ONLY for owned items */}
                    {item.collection_type === 'owned' && (
                      <button
                        onClick={() => handleEditItem(item)}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1"
                        title="Edit personal details"
                      >
                        <Edit className="w-4 h-4" />
                        <span>Edit</span>
                      </button>
                    )}
                    
                    <button
                      onClick={() => handleDeleteItem(item)}
                      className={`${item.collection_type === 'owned' ? 'flex-1' : 'w-full'} bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1`}
                      title={`Remove from ${item.collection_type === 'owned' ? 'collection' : 'want list'}`}
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>{item.collection_type === 'owned' ? 'Remove' : 'Remove'}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Edit Modal */}
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
                  {editingItem.master_kit?.club || 'Unknown Club'} - {editingItem.master_kit?.season || 'Unknown Season'}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  Editing details for your collection
                </p>
                
                {/* Live Price Preview */}
                {priceEstimations[editingItem.id] && (
                  <div className="bg-white border border-blue-200 rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Current Estimated Value:</span>
                      <span className="text-lg font-bold text-purple-600">
                        €{priceEstimations[editingItem.id].estimated_price}
                      </span>
                    </div>
                    {editingItem.purchase_price && (
                      <div className="flex justify-between items-center mt-1">
                        <span className="text-xs text-gray-500">vs Purchase Price (€{editingItem.purchase_price}):</span>
                        {(() => {
                          const difference = priceEstimations[editingItem.id].estimated_price - editingItem.purchase_price;
                          const percentage = ((difference / editingItem.purchase_price) * 100).toFixed(1);
                          return (
                            <span className={`text-xs font-medium ${difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {difference >= 0 ? '+' : ''}€{difference.toFixed(2)} ({percentage}%)
                            </span>
                          );
                        })()}
                      </div>
                    )}
                    <div className="text-xs text-gray-500 mt-2">
                      💡 Price updates automatically when you save changes
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {/* Name Printing */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name Printing 
                    <span className="text-blue-600 ml-1" title="Adds +0.15 coefficient to estimated value">💰</span>
                  </label>
                  <input
                    type="text"
                    value={editFormData.name_printing || ''}
                    onChange={(e) => setEditFormData({...editFormData, name_printing: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Mbappé, Your Name"
                  />
                  <p className="text-xs text-gray-500 mt-1">Official name flocking (+0.15 or +0.2 if with number)</p>
                </div>

                {/* Number Printing */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number Printing
                    <span className="text-blue-600 ml-1" title="Adds +0.1 coefficient to estimated value">💰</span>
                  </label>
                  <input
                    type="text"
                    value={editFormData.number_printing || ''}
                    onChange={(e) => setEditFormData({...editFormData, number_printing: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 7, 10"
                  />
                  <p className="text-xs text-gray-500 mt-1">Official number flocking (+0.1 or +0.2 if with name)</p>
                </div>

                {/* Patches */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Patches
                    <span className="text-blue-600 ml-1" title="Adds +0.15 coefficient to estimated value">💰</span>
                  </label>
                  <select
                    value={editFormData.patches || ''}
                    onChange={(e) => setEditFormData({...editFormData, patches: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">No patches</option>
                    <option value="ligue_1">Ligue 1</option>
                    <option value="champions_league">Champions League</option>
                    <option value="europa_league">Europa League</option>
                    <option value="premier_league">Premier League</option>
                    <option value="other">Other</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Competition patches (+0.15 coefficient)</p>
                </div>

                {/* Signed Section */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <input
                      type="checkbox"
                      id="edit_is_signed"
                      checked={editFormData.is_signed || false}
                      onChange={(e) => setEditFormData({...editFormData, is_signed: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="edit_is_signed" className="ml-2 block text-sm font-medium text-gray-900">
                      This kit is signed
                      <span className="text-blue-600 ml-1" title="Adds +1.0 coefficient to estimated value">💰</span>
                    </label>
                  </div>

                  {editFormData.is_signed && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Signed by</label>
                      <input
                        type="text"
                        value={editFormData.signed_by || ''}
                        onChange={(e) => setEditFormData({...editFormData, signed_by: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                        placeholder="Player name or person who signed"
                      />
                      <p className="text-xs text-gray-500 mt-1">Signatures by famous players increase value (+1.0 coefficient)</p>
                    </div>
                  )}
                </div>

                {/* Condition */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
                  <select
                    value={editFormData.condition || ''}
                    onChange={(e) => setEditFormData({...editFormData, condition: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select condition</option>
                    <option value="club_stock">Club Stock (+1.2 coefficient)</option>
                    <option value="match_prepared">Match Prepared (+0.8 coefficient)</option>
                    <option value="match_worn">Match Worn (+1.5 coefficient)</option>
                    <option value="training">Training (+0.2 coefficient)</option>
                    <option value="other">Other</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Kit condition significantly affects estimated value
                  </p>
                </div>

                {/* Physical State */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Physical State</label>
                  <select
                    value={editFormData.physical_state || ''}
                    onChange={(e) => setEditFormData({...editFormData, physical_state: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select physical state</option>
                    <option value="new_with_tags">New with tags (+0.3 coefficient)</option>
                    <option value="very_good_condition">Very good condition (+0.15 coefficient)</option>
                    <option value="used">Used (no impact)</option>
                    <option value="damaged">Damaged (-0.25 coefficient)</option>
                    <option value="needs_restoration">Needs restoration (-0.4 coefficient)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Physical condition can positively or negatively impact value
                  </p>
                </div>

                {/* Size */}
                <div>
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

                {/* Purchase Price */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Price (€)</label>
                  <input
                    type="number"
                    value={editFormData.purchase_price || ''}
                    onChange={(e) => setEditFormData({...editFormData, purchase_price: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="120.00"
                    step="0.01"
                  />
                </div>

                {/* Purchase Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Date</label>
                  <input
                    type="date"
                    value={editFormData.purchase_date || ''}
                    onChange={(e) => setEditFormData({...editFormData, purchase_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Personal Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Personal Notes</label>
                  <textarea
                    value={editFormData.personal_notes || ''}
                    onChange={(e) => setEditFormData({...editFormData, personal_notes: e.target.value})}
                    rows="3"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="Additional notes about this kit..."
                  />
                </div>
              </div>

              <div className="flex justify-between items-center space-x-3 pt-6 border-t border-gray-200 mt-6">
                <div className="text-xs text-gray-500">
                  💡 Click "Save & Continue" to update the price estimation
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      setEditingItem(null);
                      setEditFormData({});
                    }}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Close
                  </button>
                  <button
                    onClick={handleSaveEdit}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <span>💾</span>
                    <span>Save & Continue Editing</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyCollectionPage;