import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ChevronRight, Grid, List } from 'lucide-react';

const AllVersionsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [masterJersey, setMasterJersey] = useState(null);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('list');

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
        throw new Error('Failed to fetch master jersey details');
      }

      const data = await response.json();
      setMasterJersey(data);
    } catch (error) {
      console.error('Error fetching master jersey details:', error);
      setError('Failed to load master jersey details');
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
      setError('Failed to load versions');
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

  const teamName = masterJersey.team_info?.name || 'Unknown Team';
  const brandName = masterJersey.brand_info?.name || 'Unknown Brand';
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
              Kit Area
            </button>
            <ChevronRight className="w-4 h-4 text-gray-400" />
            <Link
              to={`/kit-area/master/${id}`}
              className="text-gray-600 hover:text-gray-900"
            >
              Master Jersey
            </Link>
            <ChevronRight className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">All Versions</span>
          </div>
          
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                All Versions
              </h1>
              <p className="text-lg text-gray-600 mt-1">
                {teamName} - {masterJersey.season} - {masterJersey.jersey_type?.charAt(0).toUpperCase() + masterJersey.jersey_type?.slice(1)}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {versions.length} versions found
              </p>
            </div>
            
            <div className="flex items-center space-x-4 mt-4 lg:mt-0">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">View:</span>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                >
                  <List className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                >
                  <Grid className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {versions.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👕</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No versions found</h3>
            <p className="text-gray-600">This master jersey doesn't have any versions yet.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(groupedVersions).map(([competition, competitionVersions]) => (
              <div key={competition} className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">{competition}</h2>
                  <p className="text-sm text-gray-600">{competitionVersions.length} versions</p>
                </div>
                
                <div className="p-6">
                  {viewMode === 'list' ? (
                    <div className="space-y-4">
                      {competitionVersions.map((version) => (
                        <div
                          key={version.id}
                          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                          onClick={() => handleVersionClick(version.id)}
                        >
                          <div className="flex items-center space-x-4">
                            <div className="w-16 h-16 bg-gray-100 rounded-lg flex-shrink-0">
                              {version.product_images && version.product_images[0] ? (
                                <img
                                  src={version.product_images[0].startsWith('http') ? version.product_images[0] : `${process.env.REACT_APP_BACKEND_URL}/${version.product_images[0]}`}
                                  alt="Version"
                                  className="w-16 h-16 object-cover rounded-lg"
                                />
                              ) : (
                                <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                                  <span className="text-xl">👕</span>
                                </div>
                              )}
                            </div>
                            <div>
                              <h3 className="font-medium text-gray-900">
                                {version.model_name || `${teamName} ${masterJersey.season} ${masterJersey.jersey_type}`}
                              </h3>
                              <p className="text-sm text-gray-600">
                                {version.release_type?.charAt(0).toUpperCase() + version.release_type?.slice(1)} • {version.topkit_reference}
                              </p>
                              {version.original_retail_price && (
                                <p className="text-sm text-gray-500">
                                  Original Price: €{version.original_retail_price}
                                </p>
                              )}
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-gray-400" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                      {competitionVersions.map((version) => (
                        <div
                          key={version.id}
                          className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                          onClick={() => handleVersionClick(version.id)}
                        >
                          <div className="aspect-w-16 aspect-h-12 bg-gray-100">
                            {version.product_images && version.product_images[0] ? (
                              <img
                                src={version.product_images[0].startsWith('http') ? version.product_images[0] : `${process.env.REACT_APP_BACKEND_URL}/${version.product_images[0]}`}
                                alt="Version"
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
                              {version.model_name || `${teamName} ${masterJersey.season}`}
                            </h3>
                            <p className="text-xs text-gray-600 mb-2">
                              {version.release_type?.charAt(0).toUpperCase() + version.release_type?.slice(1)}
                            </p>
                            <p className="text-xs text-gray-500 mb-2">
                              {version.topkit_reference}
                            </p>
                            {version.original_retail_price && (
                              <p className="text-xs text-gray-500">
                                €{version.original_retail_price}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AllVersionsPage;