import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Calendar, Users, Star, ChevronRight } from 'lucide-react';

const MasterJerseyDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [masterJersey, setMasterJersey] = useState(null);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchMasterJerseyDetails();
      fetchVersions();
    }
  }, [id]);

  const fetchMasterJerseyDetails = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/master-kits/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch master kit details');
      }

      const data = await response.json();
      setMasterJersey(data);
    } catch (error) {
      console.error('Error fetching master kit details:', error);
      setError('Failed to load master kit details');
    }
  };

  const fetchVersions = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reference-kits?master_kit_id=${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch versions');
      }

      const data = await response.json();
      setVersions(data);
    } catch (error) {
      console.error('Error fetching versions:', error);
      // Don't set error state for versions as it's not critical
    } finally {
      setLoading(false);
    }
  };

  const groupVersionsByCompetition = (versions) => {
    const grouped = {};
    versions.forEach(version => {
      const competition = version.competition_info?.name || version.league_competition || 'General';
      if (!grouped[competition]) {
        grouped[competition] = [];
      }
      grouped[competition].push(version);
    });
    return grouped;
  };

  const handleVersionClick = (versionId) => {
    navigate(`/kit-area/version/${versionId}`);
  };

  const handleViewAllVersions = () => {
    navigate(`/kit-area/master/${id}/versions`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !masterJersey) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error || 'Master jersey not found'}</p>
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

  const teamName = masterJersey.club_name || masterJersey.club || 'Unknown Team';
  const brandName = masterJersey.brand_name || masterJersey.brand || 'Unknown Brand';
  const groupedVersions = groupVersionsByCompetition(versions);

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
              Back to Kit Area
            </button>
            <ChevronRight className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">Master Jersey</span>
          </div>
          
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {teamName} - {masterJersey.season} - {masterJersey.kit_type?.charAt(0).toUpperCase() + masterJersey.kit_type?.slice(1)}
              </h1>
              <p className="text-lg text-gray-600 mt-1">
                {brandName} • {masterJersey.model?.charAt(0).toUpperCase() + masterJersey.model?.slice(1)}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {masterJersey.topkit_reference}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Images */}
          <div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="aspect-w-16 aspect-h-12">
                {masterJersey.front_photo_url ? (
                  <img
                    src={masterJersey.front_photo_url.startsWith('http') ? masterJersey.front_photo_url : `${process.env.REACT_APP_BACKEND_URL}/${masterJersey.front_photo_url}`}
                    alt={`${teamName} ${masterJersey.season} ${masterJersey.kit_type}`}
                    className="w-full h-96 object-cover"
                  />
                ) : (
                  <div className="w-full h-96 bg-gray-100 flex items-center justify-center">
                    <span className="text-6xl">👕</span>
                  </div>
                )}
              </div>
              
              {/* Additional Images */}
              {masterJersey.additional_images && masterJersey.additional_images.length > 0 && (
                <div className="p-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Additional Images</h3>
                  <div className="grid grid-cols-4 gap-2">
                    {masterJersey.additional_images.map((image, index) => (
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
            {/* Master Jersey Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Master Jersey Information</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Team</h3>
                  <p className="text-gray-900">{teamName}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Brand</h3>
                  <p className="text-gray-900">{brandName}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Season</h3>
                  <p className="text-gray-900">{masterJersey.season}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Type</h3>
                  <p className="text-gray-900">{masterJersey.kit_type?.charAt(0).toUpperCase() + masterJersey.kit_type?.slice(1)}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Model</h3>
                  <p className="text-gray-900">{masterJersey.model?.charAt(0).toUpperCase() + masterJersey.model?.slice(1)}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Competition</h3>
                  <p className="text-gray-900">{masterJersey.competition_name || masterJersey.competition || 'Unknown Competition'}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Primary Color</h3>
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-4 h-4 rounded border border-gray-300"
                      style={{ backgroundColor: masterJersey.primary_color }}
                    ></div>
                    <span className="text-gray-900">{masterJersey.primary_color}</span>
                  </div>
                </div>
              </div>

              {masterJersey.secondary_colors && masterJersey.secondary_colors.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Secondary Colors</h3>
                  <div className="flex items-center space-x-2">
                    {masterJersey.secondary_colors.map((color, index) => (
                      <div key={index} className="flex items-center space-x-1">
                        <div 
                          className="w-4 h-4 rounded border border-gray-300"
                          style={{ backgroundColor: color }}
                        ></div>
                        <span className="text-sm text-gray-900">{color}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {masterJersey.pattern && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Pattern</h3>
                  <p className="text-gray-900">{masterJersey.pattern}</p>
                </div>
              )}

              {masterJersey.main_sponsor && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Main Sponsor</h3>
                  <p className="text-gray-900">{masterJersey.main_sponsor}</p>
                </div>
              )}

              {masterJersey.description && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Description</h3>
                  <p className="text-gray-900">{masterJersey.description}</p>
                </div>
              )}
            </div>

            {/* Statistics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Statistics</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{versions.length}</div>
                  <div className="text-sm text-gray-600">Versions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{masterJersey.collectors_count || 0}</div>
                  <div className="text-sm text-gray-600">Collectors</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Other Versions Section */}
        {versions.length > 0 && (
          <div className="mt-8">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Other Versions</h2>
                {versions.length > 6 && (
                  <button
                    onClick={handleViewAllVersions}
                    className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center"
                  >
                    View All {versions.length} Versions
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                )}
              </div>
              
              <div className="p-6">
                {Object.entries(groupedVersions).map(([competition, competitionVersions]) => (
                  <div key={competition} className="mb-6 last:mb-0">
                    <h3 className="text-lg font-medium text-gray-900 mb-3">{competition}</h3>
                    <div className="space-y-2">
                      {competitionVersions.slice(0, 6).map((version) => (
                        <div
                          key={version.id}
                          className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                          onClick={() => handleVersionClick(version.id)}
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-gray-100 rounded border flex-shrink-0">
                              {version.product_images && version.product_images[0] ? (
                                <img
                                  src={version.product_images[0].startsWith('http') ? version.product_images[0] : `${process.env.REACT_APP_BACKEND_URL}/${version.product_images[0]}`}
                                  alt="Version"
                                  className="w-12 h-12 object-cover rounded"
                                />
                              ) : (
                                <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
                                  <span className="text-lg">👕</span>
                                </div>
                              )}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {version.model_name || `${teamName} ${masterJersey.season} ${masterJersey.kit_type}`} • {version.release_type?.charAt(0).toUpperCase() + version.release_type?.slice(1)}
                              </p>
                              <p className="text-sm text-gray-600">{version.topkit_reference}</p>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-gray-400" />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MasterJerseyDetailPage;