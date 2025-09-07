import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import ContributionModal from '../ContributionModal';
import { uploadOptimizedImage, ImageUploadProgress, OptimizedImage } from '../utils/imageUpload';

const CollaborativeTeamsPage = ({ user, API, teams, onDataUpdate }) => {
  const navigate = useNavigate();
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    country: '',
    verified_only: false
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedTeamForContribution, setSelectedTeamForContribution] = useState(null);
  
  // Get unique countries for filter
  const countries = [...new Set(teams.map(team => team.country).filter(Boolean))];

  // Apply filters
  useEffect(() => {
    let filtered = [...teams];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(team =>
        team.name.toLowerCase().includes(searchLower) ||
        team.short_name?.toLowerCase().includes(searchLower) ||
        team.common_names?.some(name => name.toLowerCase().includes(searchLower))
      );
    }

    if (filters.country) {
      filtered = filtered.filter(team => team.country === filters.country);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(team => team.verified_level !== 'unverified');
    }

    setFilteredTeams(filtered);
  }, [teams, filters]);

  // Create new team
  const handleCreateTeam = async (teamData) => {
    if (!user) return;

    try {
      setLoading(true);
      const response = await fetch(`${API}/api/teams`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(teamData)
      });

      if (response.ok) {
        const newTeam = await response.json();
        setShowCreateModal(false);
        onDataUpdate();
        alert('Team created successfully!');
      } else {
        const errorData = await response.json();
        console.error('Team creation error:', errorData);
        
        // Better error handling to avoid [object Object] display
        let errorMessage = 'Failed to create team';
        if (errorData && typeof errorData === 'object') {
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              // Handle Pydantic validation errors
              errorMessage = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
            }
          } else if (errorData.message) {
            errorMessage = errorData.message;
          }
        }
        alert(`Error: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error creating team:', error);
      alert('Error creating team');
    } finally {
      setLoading(false);
    }
  };

  const handleTeamClick = (team) => {
    navigate(`/teams/${team.id}`);
  };

  const handleContributeClick = (team, e) => {
    e.stopPropagation();
    setSelectedTeamForContribution(team);
    setShowContributionModal(true);
  };

  // Team Card Component
  const TeamCard = ({ team }) => {
    return (
      <div 
        onClick={() => handleTeamClick(team)}
        className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-200 cursor-pointer group"
      >
        {/* Image section - same structure as Master Jersey */}
        <div className="relative w-full h-32 bg-gray-100 rounded-t-lg overflow-hidden flex items-center justify-center">
          {team.logo_url ? (
            <img 
              src={`${API}/${team.logo_url}`}
              alt={team.name}
              className="w-full h-full object-contain p-2"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: team.logo_url ? 'none' : 'flex'}}>
            ⚽
          </div>
          
          {team.verified_level !== 'unverified' && (
            <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
              ✓
            </div>
          )}
          
          <div className="absolute top-2 left-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
            🌍 {team.country}
          </div>
        </div>
        
        {/* Content section - same structure as Master Jersey */}
        <div className="p-4">
          <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
            {team.name}
          </h3>
          
          <div className="space-y-1 text-xs text-gray-600 mb-3">
            {team.short_name && (
              <div className="flex items-center">
                <span className="mr-1">🏷️</span>
                <span>{team.short_name}</span>
              </div>
            )}
            
            {team.city && (
              <div className="flex items-center">
                <span className="mr-1">🏙️</span>
                <span>{team.city}</span>
              </div>
            )}
            
            {team.founded_year && (
              <div className="flex items-center">
                <span className="mr-1">📅</span>
                <span>Founded in {team.founded_year}</span>
              </div>
            )}
            
            {(team.colors || team.primary_colors) && (team.colors?.length > 0 || team.primary_colors?.length > 0) && (
              <div className="flex items-center">
                <span className="mr-1">🎨</span>
                <div className="flex space-x-1">
                  {(team.colors || team.primary_colors || []).slice(0, 3).map((color, index) => (
                    <div
                      key={index}
                      className="w-3 h-3 rounded-full border border-gray-300"
                      style={{ backgroundColor: color.toLowerCase() }}
                      title={color}
                    ></div>
                  ))}
                  {(team.colors || team.primary_colors || []).length > 3 && (
                    <span className="text-xs text-gray-400">+{(team.colors || team.primary_colors || []).length - 3}</span>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Bottom section - same structure as Master Jersey */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-blue-600 font-mono">{team.topkit_reference}</span>
            <div className="flex items-center space-x-2 text-gray-500">
              <span>{team.jerseys_count || 0} kits</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const CreateTeamModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      short_name: '',
      country: '',
      city: '',
      founded_year: '',
      colors: []
    });

    const [newColor, setNewColor] = useState('');
    
    // Image management states
    const [imageFiles, setImageFiles] = useState({
      logo: null,
      secondary_photos: []
    });
    const [imagePreviews, setImagePreviews] = useState({
      logo: '',
      secondary_photos: []
    });

    const handleImageUpload = (imageType, file) => {
      if (!file) return;
      
      // Check file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file');
        return;
      }
      
      // Check size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Image size must not exceed 5MB');
        return;
      }
      
      // Update files
      if (imageType === 'secondary_photo') {
        setImageFiles(prev => ({
          ...prev,
          secondary_photos: [...prev.secondary_photos, file]
        }));
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreviews(prev => ({
            ...prev,
            secondary_photos: [...prev.secondary_photos, e.target.result]
          }));
        };
        reader.readAsDataURL(file);
      } else {
        setImageFiles(prev => ({
          ...prev,
          [imageType]: file
        }));
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreviews(prev => ({
            ...prev,
            [imageType]: e.target.result
          }));
        };
        reader.readAsDataURL(file);
      }
    };

    const removeSecondaryPhoto = (index) => {
      setImageFiles(prev => ({
        ...prev,
        secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
      }));
      setImagePreviews(prev => ({
        ...prev,
        secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
      }));
    };

    const addColor = () => {
      if (newColor && !formData.colors.includes(newColor)) {
        setFormData(prev => ({
          ...prev,
          colors: [...prev.colors, newColor]
        }));
        setNewColor('');
      }
    };

    const removeColor = (colorToRemove) => {
      setFormData(prev => ({
        ...prev,
        colors: prev.colors.filter(color => color !== colorToRemove)
      }));
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!formData.name || !formData.country) {
        alert('Name and country are required');
        return;
      }

      // Convert files to base64 if present and prepare data with proper types
      let teamDataWithImages = { 
        ...formData,
        // Convert founded_year to integer if provided
        founded_year: formData.founded_year ? parseInt(formData.founded_year) : null
      };
      
      if (imageFiles.logo) {
        const logoReader = new FileReader();
        logoReader.onload = async () => {
          teamDataWithImages.logo_base64 = logoReader.result;
          
          if (imageFiles.secondary_photos.length > 0) {
            const photoPromises = imageFiles.secondary_photos.map(file => {
              return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.readAsDataURL(file);
              });
            });
            
            const photosBase64 = await Promise.all(photoPromises);
            teamDataWithImages.secondary_photos_base64 = photosBase64;
          }
          
          handleCreateTeam(teamDataWithImages);
        };
        logoReader.readAsDataURL(imageFiles.logo);
      } else {
        if (imageFiles.secondary_photos.length > 0) {
          const photoPromises = imageFiles.secondary_photos.map(file => {
            return new Promise((resolve) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result);
              reader.readAsDataURL(file);
            });
          });
          
          const photosBase64 = await Promise.all(photoPromises);
          teamDataWithImages.secondary_photos_base64 = photosBase64;
        }
        
        handleCreateTeam(teamDataWithImages);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Add New Team</h2>
            <button
              onClick={() => setShowCreateModal(false)}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({...prev, name: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Short Name
                </label>
                <input
                  type="text"
                  value={formData.short_name}
                  onChange={(e) => setFormData(prev => ({...prev, short_name: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country *
                </label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData(prev => ({...prev, country: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData(prev => ({...prev, city: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Founded Year
                </label>
                <input
                  type="number"
                  value={formData.founded_year}
                  onChange={(e) => setFormData(prev => ({...prev, founded_year: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Team Colors
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newColor}
                  onChange={(e) => setNewColor(e.target.value)}
                  placeholder="Enter color (e.g., Red, Blue, #FF0000)"
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={addColor}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  +
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.colors.map((color, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm flex items-center"
                  >
                    {color}
                    <button
                      type="button"
                      onClick={() => removeColor(color)}
                      className="ml-2 text-red-500 hover:text-red-700"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Image Upload Section */}
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 flex items-center gap-2">
                📸 Team Images
                <span className="text-xs text-gray-500 font-normal">(optional, max 5MB per image)</span>
              </h4>
              
              {/* Team Logo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Team Logo
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload('logo', e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {imagePreviews.logo && (
                    <div className="relative">
                      <img src={imagePreviews.logo} alt="Logo preview" className="w-12 h-12 object-cover rounded-lg border" />
                      <button
                        type="button"
                        onClick={() => {
                          setImageFiles(prev => ({ ...prev, logo: null }));
                          setImagePreviews(prev => ({ ...prev, logo: '' }));
                        }}
                        className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Secondary Images */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Secondary images (old logos, photos, etc.)
                  <span className="text-xs text-gray-500 ml-1">- Maximum 3 images</span>
                </label>
                
                {imageFiles.secondary_photos.length < 3 && (
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload('secondary_photo', e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 mb-3"
                  />
                )}
                
                {imagePreviews.secondary_photos.length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    {imagePreviews.secondary_photos.map((preview, index) => (
                      <div key={index} className="relative">
                        <img src={preview} alt={`Preview ${index + 1}`} className="w-full h-16 object-cover rounded-lg border" />
                        <button
                          type="button"
                          onClick={() => removeSecondaryPhoto(index)}
                          className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
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
                {loading ? 'Creating...' : 'Create Team'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Football Teams</h1>
              <p className="text-gray-600">
                Collaborative database of football teams from around the world
              </p>
            </div>
            {user && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Add Team
              </button>
            )}
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                placeholder="Team name..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({...prev, search: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
              <select
                value={filters.country}
                onChange={(e) => setFilters(prev => ({...prev, country: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All countries</option>
                {countries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.verified_only}
                  onChange={(e) => setFilters(prev => ({...prev, verified_only: e.target.checked}))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Verified teams only</span>
              </label>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => setFilters({ search: '', country: '', verified_only: false })}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Reset filters
              </button>
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{filteredTeams.length}</div>
              <div className="text-sm text-blue-700">Teams found</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {filteredTeams.filter(team => team.verified_level !== 'unverified').length}
              </div>
              <div className="text-sm text-green-700">Verified teams</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{countries.length}</div>
              <div className="text-sm text-purple-700">Countries represented</div>
            </div>
          </div>
        </div>
      </div>

      {/* Teams Grid */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {filteredTeams.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">⚽</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No teams found</h3>
            <p className="text-gray-600 mb-6">
              Try modifying your filters or contribute by adding a new team
            </p>
            {user && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Add first team
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredTeams.map((team) => (
              <div key={team.id} className="relative group">
                <TeamCard team={team} />
                {user && (
                  <button
                    onClick={(e) => handleContributeClick(team, e)}
                    className="absolute top-2 right-2 bg-white/90 hover:bg-white text-blue-600 p-1 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Improve this profile"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Team Modal */}
      {showCreateModal && <CreateTeamModal />}

      {/* Contribution Modal */}
      {showContributionModal && selectedTeamForContribution && (
        <ContributionModal
          isOpen={showContributionModal}
          onClose={() => {
            setShowContributionModal(false);
            setSelectedTeamForContribution(null);
          }}
          entity={selectedTeamForContribution}
          entityType="team"
          onContributionCreated={() => {
            setShowContributionModal(false);
            setSelectedTeamForContribution(null);
            onDataUpdate();
          }}
        />
      )}
    </div>
  );
};

export default CollaborativeTeamsPage;