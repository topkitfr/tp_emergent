import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Trash2, Eye } from 'lucide-react';
import EnhancedEditKitForm from '../components/EnhancedEditKitForm';

const CollectionItemDetailPage = ({ user, API, onDataUpdate }) => {
  const { itemId } = useParams();
  const navigate = useNavigate();
  const [collectionItem, setCollectionItem] = useState(null);
  const [priceEstimation, setPriceEstimation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({});

  useEffect(() => {
    if (user && itemId) {
      loadCollectionItem();
    }
  }, [user, itemId]);

  const loadCollectionItem = async () => {
    if (!user?.id || !itemId) return;
    
    const token = user.token || localStorage.getItem('token');
    if (!token) {
      setError('Authentication required');
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      
      // Load collection item details
      const response = await fetch(`${API}/api/my-collection/${itemId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCollectionItem(data);
        
        // Load price estimation if owned item
        if (data.collection_type === 'owned') {
          try {
            const priceResponse = await fetch(`${API}/api/my-collection/${itemId}/price-estimation`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            
            if (priceResponse.ok) {
              const priceData = await priceResponse.json();
              setPriceEstimation(priceData);
            }
          } catch (priceError) {
            console.error('Error loading price estimation:', priceError);
          }
        }
      } else {
        setError('Failed to load collection item');
      }
    } catch (error) {
      console.error('Error loading collection item:', error);
      setError('Error loading collection item');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    // Convert the collection item data to form format
    let formattedPurchaseDate = '';
    if (collectionItem.purchase_date) {
      try {
        const date = new Date(collectionItem.purchase_date);
        if (!isNaN(date.getTime())) {
          formattedPurchaseDate = date.toISOString().split('T')[0];
        }
      } catch (error) {
        console.warn('Invalid purchase_date format:', collectionItem.purchase_date);
      }
    }

    let formattedMatchDate = '';
    if (collectionItem.match_date) {
      try {
        const date = new Date(collectionItem.match_date);
        if (!isNaN(date.getTime())) {
          formattedMatchDate = date.toISOString().split('T')[0];
        }
      } catch (error) {
        console.warn('Invalid match_date format:', collectionItem.match_date);
      }
    }

    // Convert patches from string to array if needed
    let patchesArray = [];
    if (collectionItem.patches) {
      if (typeof collectionItem.patches === 'string') {
        patchesArray = collectionItem.patches.split(',').map(p => p.trim()).filter(p => p);
      } else if (Array.isArray(collectionItem.patches)) {
        patchesArray = collectionItem.patches;
      }
    } else if (collectionItem.patches_list) {
      patchesArray = Array.isArray(collectionItem.patches_list) ? collectionItem.patches_list : [];
    }

    let authenticityProofArray = [];
    if (collectionItem.authenticity_proof) {
      authenticityProofArray = Array.isArray(collectionItem.authenticity_proof) ? collectionItem.authenticity_proof : [];
    }
    
    setEditFormData({
      // A. Basic Information
      gender: collectionItem.gender || '',
      size: collectionItem.size || '',
      
      // B. Player & Printing
      associated_player: collectionItem.associated_player_id || '',
      name_printing: collectionItem.name_printing || '',
      number_printing: collectionItem.number_printing || '',
      
      // C. Origin & Authenticity
      origin_type: collectionItem.origin_type || '',
      competition: collectionItem.competition || '',
      authenticity_proof: authenticityProofArray,
      match_date: formattedMatchDate,
      opponent: collectionItem.opponent_id || '',
      
      // D. Physical Condition
      general_condition: collectionItem.general_condition || '',
      photo_urls: collectionItem.photo_urls || [],
      
      // E. Technical Details
      patches: patchesArray,
      other_patches: collectionItem.other_patches || '',
      signature: collectionItem.signature || false,
      signature_player: collectionItem.signature_player_id || '',
      signature_certificate: collectionItem.signature_certificate || '',
      
      // F. User Estimate
      user_estimate: collectionItem.user_estimate || '',
      
      // G. Comments
      comments: collectionItem.comments || '',
      
      // Legacy fields
      is_signed: collectionItem.is_signed || false,
      signed_by: collectionItem.signed_by || '',
      condition: collectionItem.condition || '',
      condition_other: collectionItem.condition_other || '',
      physical_state: collectionItem.physical_state || '',
      purchase_price: collectionItem.purchase_price || '',
      purchase_date: formattedPurchaseDate,
      personal_notes: collectionItem.personal_notes || ''
    });
    
    setIsEditing(true);
  };

  const handleSaveEdit = async () => {
    if (!collectionItem) return;

    const token = user?.token || localStorage.getItem('token');
    if (!token) {
      console.error('❌ No authentication token available for edit');
      return;
    }

    try {
      // Process form data similar to MyCollectionPage
      const processedFormData = {};
      
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
      if (editFormData.patches && Array.isArray(editFormData.patches) && editFormData.patches.length > 0) {
        processedFormData.patches = editFormData.patches.join(', ');
        processedFormData.patches_list = editFormData.patches;
      }
      addFieldIfNotEmpty('other_patches', editFormData.other_patches);
      
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

      const response = await fetch(`${API}/api/my-collection/${collectionItem.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(processedFormData)
      });

      if (response.ok) {
        console.log('✅ Collection item updated successfully');
        setIsEditing(false);
        // Reload the collection item data
        await loadCollectionItem();
        alert('✅ Kit details updated successfully!');
      } else {
        const errorData = await response.json();
        console.error('❌ Update failed:', errorData);
        
        let errorMessage = 'Failed to update kit details';
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join('\n');
          } else if (typeof errorData.detail === 'object') {
            errorMessage = JSON.stringify(errorData.detail, null, 2);
          }
        }
        
        alert(`Error: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error updating collection item:', error);
      alert(`Error updating kit details: ${error.message}`);
    }
  };

  const handleDelete = async () => {
    const confirmMessage = `Are you sure you want to remove this kit from your collection?`;
    
    if (!confirm(confirmMessage)) return;

    const token = user?.token || localStorage.getItem('token');
    if (!token) {
      console.error('❌ No authentication token available for delete');
      return;
    }

    try {
      const response = await fetch(`${API}/api/my-collection/${collectionItem.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('Kit removed from collection!');
        // Navigate back to collection page
        navigate('/my-collection');
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !collectionItem) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error || 'Collection item not found'}</p>
          <button
            onClick={() => navigate('/my-collection')}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Back to Collection
          </button>
        </div>
      </div>
    );
  }

  const masterKit = collectionItem.master_kit || {};

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/my-collection')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Collection</span>
              </button>
            </div>
            
            <div className="flex items-center space-x-3">
              {collectionItem.collection_type === 'owned' && (
                <button
                  onClick={handleEdit}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
                >
                  <Edit className="w-4 h-4" />
                  <span>Edit Kit Details</span>
                </button>
              )}
              
              <button
                onClick={handleDelete}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Remove</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Images */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Photos</h3>
              
              {/* Personal Photos (Priority) */}
              {collectionItem.photo_urls && collectionItem.photo_urls.length > 0 ? (
                <div className="space-y-4">
                  <h4 className="text-md font-medium text-gray-700">Your Personal Photos</h4>
                  <div className="grid grid-cols-1 gap-4">
                    {collectionItem.photo_urls.map((photo, index) => {
                      const photoUrl = photo.startsWith('http') 
                        ? photo 
                        : photo.startsWith('uploads/') ? 
                          `${API}/api/${photo}` :
                          `${API}/api/uploads/personal_photos/${photo}`;
                      
                      return (
                        <div key={index} className="relative">
                          <img
                            src={photoUrl}
                            alt={`Personal photo ${index + 1}`}
                            className="w-full h-64 object-contain bg-gray-50 rounded-lg border"
                          />
                          <div className="absolute top-2 right-2 bg-blue-600 text-white px-2 py-1 rounded text-sm">
                            Personal
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                /* Master Kit Photos (Fallback) */
                <div className="space-y-4">
                  <h4 className="text-md font-medium text-gray-500">Master Kit Reference Photos</h4>
                  <div className="grid grid-cols-1 gap-4">
                    {masterKit.front_photo_url && (
                      <div className="relative">
                        <img
                          src={masterKit.front_photo_url.startsWith('http') 
                            ? masterKit.front_photo_url 
                            : masterKit.front_photo_url.startsWith('uploads/') ? 
                              `${API}/api/${masterKit.front_photo_url}` :
                              `${API}/api/uploads/${masterKit.front_photo_url}`}
                          alt="Front view"
                          className="w-full h-64 object-contain bg-gray-50 rounded-lg border opacity-75"
                        />
                        <div className="absolute top-2 right-2 bg-gray-600 text-white px-2 py-1 rounded text-sm">
                          Master Kit
                        </div>
                      </div>
                    )}
                    
                    {masterKit.back_photo_url && (
                      <div className="relative">
                        <img
                          src={masterKit.back_photo_url.startsWith('http') 
                            ? masterKit.back_photo_url 
                            : masterKit.back_photo_url.startsWith('uploads/') ? 
                              `${API}/api/${masterKit.back_photo_url}` :
                              `${API}/api/uploads/${masterKit.back_photo_url}`}
                          alt="Back view"
                          className="w-full h-64 object-contain bg-gray-50 rounded-lg border opacity-75"
                        />
                        <div className="absolute top-2 right-2 bg-gray-600 text-white px-2 py-1 rounded text-sm">
                          Master Kit
                        </div>
                      </div>
                    )}
                    
                    {/* Secondary Images */}
                    {masterKit.secondary_images && Array.isArray(masterKit.secondary_images) && 
                     masterKit.secondary_images.length > 0 && (
                      <div className="grid grid-cols-2 gap-2">
                        {masterKit.secondary_images.slice(0, 3).map((img, index) => (
                          <div key={index} className="relative">
                            <img
                              src={img.startsWith('http') 
                                ? img 
                                : img.startsWith('uploads/') ? 
                                  `${API}/api/${img}` :
                                  `${API}/api/uploads/${img}`}
                              alt={`Detail ${index + 1}`}
                              className="w-full h-32 object-contain bg-gray-50 rounded-lg border opacity-75"
                            />
                            <div className="absolute top-1 right-1 bg-gray-600 text-white px-1 py-0.5 rounded text-xs">
                              Master Kit
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {!masterKit.front_photo_url && (
                    <div className="text-center py-12 bg-gray-50 rounded-lg">
                      <span className="text-4xl">👕</span>
                      <p className="text-gray-500 mt-2">No photos available</p>
                      {collectionItem.collection_type === 'owned' && (
                        <p className="text-sm text-gray-400 mt-1">Add personal photos by editing this kit</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Details */}
          <div className="space-y-6">
            {/* Kit Information */}
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  {collectionItem.name_printing || masterKit.club || 'Unknown Kit'}
                  {collectionItem.number_printing && ` #${collectionItem.number_printing}`}
                </h2>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  collectionItem.collection_type === 'owned' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {collectionItem.collection_type === 'owned' ? 'OWNED' : 'WANTED'}
                </span>
              </div>

              <div className="space-y-3 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div><strong>Club:</strong> {masterKit.club || 'Unknown'}</div>
                  <div><strong>Season:</strong> {masterKit.season || 'Unknown'}</div>
                  <div><strong>Type:</strong> {masterKit.kit_style || masterKit.kit_type || 'Unknown'}</div>
                  <div><strong>Brand:</strong> {masterKit.brand || 'Unknown'}</div>
                  <div><strong>Model:</strong> {masterKit.model || 'Unknown'}</div>
                  <div><strong>Reference:</strong> {masterKit.topkit_reference || 'No Ref'}</div>
                </div>

                {/* Personal Details */}
                {collectionItem.collection_type === 'owned' && (
                  <>
                    <hr className="my-4" />
                    <h4 className="font-medium text-gray-700 mb-2">Personal Details</h4>
                    <div className="grid grid-cols-2 gap-4">
                      {collectionItem.size && <div><strong>Size:</strong> {collectionItem.size}</div>}
                      {collectionItem.gender && <div><strong>Gender:</strong> {collectionItem.gender}</div>}
                      {collectionItem.general_condition && <div><strong>Condition:</strong> {collectionItem.general_condition.replace('_', ' ')}</div>}
                      {collectionItem.origin_type && <div><strong>Origin:</strong> {collectionItem.origin_type.replace('_', ' ')}</div>}
                    </div>

                    {(collectionItem.signature || collectionItem.is_signed) && (
                      <div className="bg-yellow-50 p-3 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <span className="text-yellow-600">✍️</span>
                          <span><strong>Signed</strong> {collectionItem.signed_by ? `by ${collectionItem.signed_by}` : ''}</span>
                        </div>
                      </div>
                    )}

                    {collectionItem.patches && (
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <span className="text-blue-600">🏆</span>
                          <span><strong>Patches:</strong> {collectionItem.patches}</span>
                        </div>
                      </div>
                    )}

                    {collectionItem.comments && (
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <strong>Comments:</strong> {collectionItem.comments}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            {/* Pricing Information (Only for owned items) */}
            {collectionItem.collection_type === 'owned' && (
              <div className="bg-white rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Valuation</h3>
                
                <div className="space-y-3">
                  {/* User Estimate */}
                  {collectionItem.user_estimate && (
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">User Estimate:</span>
                      <span className="font-bold text-blue-600 text-lg">€{collectionItem.user_estimate}</span>
                    </div>
                  )}
                  
                  {/* TopKit Estimated Price */}
                  {priceEstimation && (
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">TopKit Estimate:</span>
                      <span className="font-bold text-purple-600 text-lg">€{priceEstimation.estimated_price}</span>
                    </div>
                  )}

                  {/* Comparison */}
                  {collectionItem.user_estimate && priceEstimation && (
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Difference:</span>
                      {(() => {
                        const userEstimate = parseFloat(collectionItem.user_estimate);
                        const topkitEstimate = priceEstimation.estimated_price;
                        const difference = userEstimate - topkitEstimate;
                        const percentage = ((difference / topkitEstimate) * 100).toFixed(1);
                        
                        return (
                          <span className={`font-medium ${difference >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                            {difference >= 0 ? '+' : ''}€{difference.toFixed(2)} ({percentage}%)
                          </span>
                        );
                      })()}
                    </div>
                  )}
                  
                  {/* Price Breakdown */}
                  {priceEstimation?.calculation_details && (
                    <div className="mt-4 pt-4 border-t">
                      <details className="text-sm">
                        <summary className="cursor-pointer text-gray-500 hover:text-gray-700 mb-2">
                          Price Breakdown Details
                        </summary>
                        <div className="space-y-2 text-gray-600">
                          <div className="flex justify-between">
                            <span>Base Price ({masterKit.model}):</span>
                            <span>€{priceEstimation.calculation_details.base_price}</span>
                          </div>
                          {priceEstimation.calculation_details.coefficients_applied?.map((coeff, idx) => (
                            <div key={idx} className="flex justify-between">
                              <span>{coeff.factor}:</span>
                              <span>{coeff.value}</span>
                            </div>
                          ))}
                          <div className="font-medium pt-2 border-t text-gray-700">
                            {priceEstimation.calculation_details.formula}
                          </div>
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      <EnhancedEditKitForm
        isOpen={isEditing}
        onClose={() => setIsEditing(false)}
        editingItem={collectionItem}
        formData={editFormData}
        onFormDataChange={(key, value) => setEditFormData({...editFormData, [key]: value})}
        onSave={handleSaveEdit}
        API={API}
        title="Edit Kit Details"
      />
    </div>
  );
};

export default CollectionItemDetailPage;