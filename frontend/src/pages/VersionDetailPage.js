import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ChevronRight, ShoppingCart, Heart, ExternalLink, Calendar, Package, Star } from 'lucide-react';

const VersionDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [version, setVersion] = useState(null);
  const [masterJersey, setMasterJersey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchVersionDetails();
    }
  }, [id]);

  const fetchVersionDetails = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reference-kits/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch version details');
      }

      const data = await response.json();
      setVersion(data);
      
      // Fetch master jersey details if we have the master_kit_id
      if (data.master_kit_id) {
        fetchMasterJerseyDetails(data.master_kit_id);
      }
    } catch (error) {
      console.error('Error fetching version details:', error);
      setError('Failed to load version details');
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterJerseyDetails = async (masterKitId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/master-jerseys/${masterKitId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMasterJersey(data);
      }
    } catch (error) {
      console.error('Error fetching master jersey details:', error);
    }
  };

  const handleAddToCollection = async (type) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/collections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          reference_kit_id: version.id,
          collection_type: type
        })
      });

      if (response.ok) {
        alert(`Successfully added to ${type === 'own' ? 'collection' : 'wantlist'}!`);
      } else {
        const errorData = await response.json();
        alert(errorData.message || 'Failed to add to collection');
      }
    } catch (error) {
      console.error('Error adding to collection:', error);
      alert('Failed to add to collection');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error || 'Version not found'}</p>
          <button
            onClick={() => navigate('/kit-area')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Kit Area
          </button>
        </div>
      </div>
    );
  }

  const teamName = version.team_info?.name || masterJersey?.team_info?.name || 'Unknown Team';
  const brandName = version.brand_info?.name || masterJersey?.brand_info?.name || 'Unknown Brand';
  const season = masterJersey?.season || 'Unknown Season';
  const jerseyType = masterJersey?.jersey_type || 'Unknown Type';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/kit-area')}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              Kit Area
            </button>
            <ChevronRight className="w-4 h-4 text-gray-400" />
            {masterJersey && (
              <>
                <Link
                  to={`/kit-area/master/${masterJersey.id}`}
                  className="text-gray-600 hover:text-gray-900"
                >
                  Master Jersey
                </Link>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </>
            )}
            <span className="text-gray-600">Version</span>
          </div>
          
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {version.model_name || `${teamName} - ${season} - ${jerseyType?.charAt(0).toUpperCase() + jerseyType?.slice(1)}`}
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              {version.release_type?.charAt(0).toUpperCase() + version.release_type?.slice(1)} • {brandName}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {version.topkit_reference}
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Images */}
          <div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="aspect-w-16 aspect-h-12">
                {version.main_photo ? (
                  <img
                    src={version.main_photo.startsWith('http') ? version.main_photo : `${process.env.REACT_APP_BACKEND_URL}/${version.main_photo}`}
                    alt={version.model_name || `${teamName} ${season} ${jerseyType}`}
                    className="w-full h-96 object-cover"
                  />
                ) : version.product_images && version.product_images[0] ? (
                  <img
                    src={version.product_images[0].startsWith('http') ? version.product_images[0] : `${process.env.REACT_APP_BACKEND_URL}/${version.product_images[0]}`}
                    alt={version.model_name || `${teamName} ${season} ${jerseyType}`}
                    className="w-full h-96 object-cover"
                  />
                ) : (
                  <div className="w-full h-96 bg-gray-100 flex items-center justify-center">
                    <span className="text-6xl">👕</span>
                  </div>
                )}
              </div>
              
              {/* Additional Images */}
              {version.product_images && version.product_images.length > 1 && (
                <div className="p-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Product Images</h3>
                  <div className="grid grid-cols-4 gap-2">
                    {version.product_images.slice(1).map((image, index) => (
                      <img
                        key={index}
                        src={image.startsWith('http') ? image : `${process.env.REACT_APP_BACKEND_URL}/${image}`}
                        alt={`Product view ${index + 2}`}
                        className="w-full h-20 object-cover rounded border"
                      />
                    ))}
                  </div>
                </div>
              )}
              
              {version.secondary_photos && version.secondary_photos.length > 0 && (
                <div className="p-4 border-t">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Additional Photos</h3>
                  <div className="grid grid-cols-4 gap-2">
                    {version.secondary_photos.map((image, index) => (
                      <img
                        key={index}
                        src={image.startsWith('http') ? image : `${process.env.REACT_APP_BACKEND_URL}/${image}`}
                        alt={`Additional view ${index + 1}`}
                        className="w-full h-20 object-cover rounded border"
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Details */}
          <div className="space-y-6">
            {/* Version Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Version Information</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Model Name</h3>
                  <p className="text-gray-900">{version.model_name || 'Not specified'}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Release Type</h3>
                  <p className="text-gray-900">{version.release_type?.charAt(0).toUpperCase() + version.release_type?.slice(1)}</p>
                </div>
                
                {/* Master Kit Information */}
                {version.master_kit_info && (
                  <>
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-1">Master Kit</h3>
                      <p className="text-gray-900">
                        {version.master_kit_info.model} - {version.master_kit_info.season} {version.master_kit_info.jersey_type}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-1">Master Kit ID</h3>
                      <p className="text-gray-900 font-mono text-sm">{version.master_kit_info.id}</p>
                    </div>
                  </>
                )}
                
                {version.sku_code && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">SKU Code</h3>
                    <p className="text-gray-900">{version.sku_code}</p>
                  </div>
                )}
                
                {version.barcode && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">Barcode</h3>
                    <p className="text-gray-900">{version.barcode}</p>
                  </div>
                )}
                
                {(version.competition_info || version.league_competition) && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">League/Competition</h3>
                    <p className="text-gray-900">
                      {version.competition_info && version.competition_info.name ? 
                        version.competition_info.name : 
                        version.competition_info && version.competition_info.type ? 
                          `${version.competition_info.type} (${version.competition_info.country})` :
                          version.league_competition
                      }
                    </p>
                  </div>
                )}
                
                {version.release_date && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">Release Date</h3>
                    <p className="text-gray-900">{new Date(version.release_date).toLocaleDateString()}</p>
                  </div>
                )}
              </div>

              {version.description && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Description</h3>
                  <p className="text-gray-900">{version.description}</p>
                </div>
              )}
            </div>

            {/* Pricing Information */}
            {(version.original_retail_price || version.current_market_price) && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Pricing Information</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {version.original_retail_price && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-1">Original Retail Price</h3>
                      <p className="text-2xl font-bold text-gray-900">€{version.original_retail_price}</p>
                    </div>
                  )}
                  
                  {version.current_market_price && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-1">Current Market Price</h3>
                      <p className="text-2xl font-bold text-green-600">€{version.current_market_price}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Availability & Features */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Availability & Features</h2>
              
              {version.available_sizes && version.available_sizes.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Available Sizes</h3>
                  <div className="flex flex-wrap gap-2">
                    {version.available_sizes.map((size, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                      >
                        {size}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {version.is_limited_edition && (
                <div className="mb-4">
                  <div className="flex items-center space-x-2">
                    <Star className="w-5 h-5 text-yellow-500" />
                    <span className="font-medium text-gray-900">Limited Edition</span>
                  </div>
                  {version.production_run && (
                    <p className="text-sm text-gray-600 mt-1">
                      Production run: {version.production_run} pieces
                    </p>
                  )}
                </div>
              )}

              {version.material_composition && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Material Composition</h3>
                  <p className="text-gray-900">{version.material_composition}</p>
                </div>
              )}

              {version.care_instructions && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Care Instructions</h3>
                  <p className="text-gray-900">{version.care_instructions}</p>
                </div>
              )}

              {version.authenticity_features && version.authenticity_features.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Authenticity Features</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {version.authenticity_features.map((feature, index) => (
                      <li key={index} className="text-sm text-gray-700">{feature}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Statistics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Statistics</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{version.total_in_collections || 0}</div>
                  <div className="text-sm text-gray-600">In Collections</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{version.total_for_sale || 0}</div>
                  <div className="text-sm text-gray-600">For Sale</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Available Player Prints */}
        {version.available_prints && version.available_prints.length > 0 && (
          <div className="mt-8">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Available Player Prints</h2>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {version.available_prints.map((print, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-medium text-gray-900">{print.player_name}</h3>
                          <p className="text-sm text-gray-600">#{print.number}</p>
                        </div>
                        <div className="text-right">
                          {print.player_id && (
                            <p className="text-xs text-gray-500">ID: {print.player_id}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Collection Actions */}
        <div className="mt-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Add to Collection</h2>
            <p className="text-gray-600 mb-4">Add this reference kit to your personal collection or wantlist</p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => handleAddToCollection('own')}
                className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <span>📦</span>
                Own This Kit
              </button>
              
              <button
                onClick={() => handleAddToCollection('want')}
                className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <span>❤️</span>
                Want This Kit
              </button>
            </div>
            
            <p className="text-xs text-gray-500 mt-2">
              Note: A kit can only be in your collection OR wantlist, not both
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VersionDetailPage;