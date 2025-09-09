import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, List, LayoutGrid } from 'lucide-react';

const CollaborativePlayersPage = ({ user, API, players, onDataUpdate }) => {
  const navigate = useNavigate();
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    nationality: '',
    position: '',
    verified_only: false
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid', // 'grid', 'thumbnail', 'list'
    itemsPerPage: 20,
    currentPage: 1
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Get unique values for filters
  const nationalities = [...new Set(players.map(player => player.nationality).filter(Boolean))];
  const positions = [...new Set(players.map(player => player.position).filter(Boolean))];

  // Apply filters and pagination
  useEffect(() => {
    let filtered = [...players];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(player =>
        player.name.toLowerCase().includes(searchLower) ||
        player.full_name?.toLowerCase().includes(searchLower) ||
        player.common_names?.some(name => name.toLowerCase().includes(searchLower))
      );
    }

    if (filters.nationality) {
      filtered = filtered.filter(player => player.nationality === filters.nationality);
    }

    if (filters.position) {
      filtered = filtered.filter(player => player.position === filters.position);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(player => player.verified_level !== 'unverified');
    }

    setFilteredPlayers(filtered);
    // Reset to first page when filters change
    setDisplayOptions(prev => ({ ...prev, currentPage: 1 }));
  }, [players, filters]);

  // Calculate pagination
  const totalItems = filteredPlayers.length;
  const totalPages = Math.ceil(totalItems / displayOptions.itemsPerPage);
  const startIndex = (displayOptions.currentPage - 1) * displayOptions.itemsPerPage;
  const endIndex = startIndex + displayOptions.itemsPerPage;
  const currentItems = filteredPlayers.slice(startIndex, endIndex);

  // Pagination handlers
  const goToPage = (page) => {
    setDisplayOptions(prev => ({ ...prev, currentPage: Math.max(1, Math.min(page, totalPages)) }));
  };

  // Create new player
  const handleCreatePlayer = async (playerData) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await fetch(`${API}/api/players`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(playerData)
      });

      if (response.ok) {
        const newPlayer = await response.json();
        alert(`✅ Joueur "${newPlayer.name}" créé avec succès ! (${newPlayer.topkit_reference})`);
        setShowCreateModal(false);
        onDataUpdate(); // Refresh data
      } else {
        const error = await response.json();
        alert(`❌ Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating player:', error);
      alert('❌ Erreur lors de la création du joueur');
    }
    setLoading(false);
  };

  const PlayerCard = ({ player }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
      onClick={() => navigate(`/players/${player.id}`)}
    >
      {/* Image section - same structure as Master Jersey */}
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {player.photo_url ? (
          <img 
            src={player.photo_url.startsWith('data:') || player.photo_url.startsWith('http') ? player.photo_url : `${API}/${player.photo_url}`}
            alt={`${player.name} photo`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: player.photo_url ? 'none' : 'flex'}}>
          👤
        </div>
        
        {player.verified_level !== 'unverified' && (
          <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
        
        {player.nationality && (
          <div className="absolute top-2 left-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
            🌍 {player.nationality}
          </div>
        )}
      </div>
      
      {/* Content section - same structure as Master Jersey */}
      <div className="p-4">
        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
          {player.name}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-600 mb-3">
          {player.position && (
            <div className="flex items-center">
              <span className="mr-1">⚽</span>
              <span>{player.position}</span>
            </div>
          )}
          
          {player.birth_date && (
            <div className="flex items-center">
              <span className="mr-1">📅</span>
              <span>Né en {new Date(player.birth_date).getFullYear()}</span>
            </div>
          )}
          
          {player.common_names && player.common_names.length > 0 && (
            <div className="flex items-center">
              <span className="mr-1">🏷️</span>
              <span className="truncate">{player.common_names.slice(0, 2).join(", ")}</span>
              {player.common_names.length > 2 && (
                <span className="ml-1 text-gray-400">+{player.common_names.length - 2}</span>
              )}
            </div>
          )}
        </div>
        
        {/* Bottom section - same structure as Master Jersey */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-600 font-mono">{player.topkit_reference}</span>
          <div className="flex items-center space-x-2 text-gray-500">
            <span>{player.jerseys_count || 0} maillots</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Thumbnail version - smaller cards
  const PlayerThumbnail = ({ player }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
      onClick={() => navigate(`/players/${player.id}`)}
    >
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {player.photo_url ? (
          <img 
            src={player.photo_url.startsWith('data:') || player.photo_url.startsWith('http') ? player.photo_url : `${API}/${player.photo_url}`}
            alt={`${player.name} photo`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-2xl flex items-center justify-center w-full h-full" style={{display: player.photo_url ? 'none' : 'flex'}}>
          👤
        </div>
        
        {player.verified_level !== 'unverified' && (
          <div className="absolute top-1 right-1 bg-green-100 text-green-800 px-1 py-0.5 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
      </div>
      
      <div className="p-2">
        <h3 className="font-bold text-xs text-gray-900 mb-1 group-hover:text-blue-600 line-clamp-1">
          {player.name}
        </h3>
        <div className="text-xs text-gray-600 mb-1">
          {player.position && <span>{player.position}</span>}
        </div>
        <div className="text-xs text-blue-600 font-mono truncate">{player.topkit_reference}</div>
      </div>
    </div>
  );

  // List version - horizontal layout
  const PlayerListItem = ({ player }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all cursor-pointer group flex items-center space-x-4"
      onClick={() => navigate(`/players/${player.id}`)}
    >
      <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-gray-200 transition-colors">
        {player.photo_url ? (
          <img 
            src={player.photo_url.startsWith('data:') || player.photo_url.startsWith('http') ? player.photo_url : `${API}/${player.photo_url}`}
            alt={`${player.name} photo`}
            className="w-full h-full object-cover rounded-lg"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-2xl flex items-center justify-center w-full h-full" style={{display: player.photo_url ? 'none' : 'flex'}}>
          👤
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 truncate">
            {player.name}
          </h3>
          {player.verified_level !== 'unverified' && (
            <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium ml-2">
              ✓
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
          {player.nationality && (
            <span className="flex items-center">
              <span className="mr-1">🌍</span>
              {player.nationality}
            </span>
          )}
          {player.position && (
            <span className="flex items-center">
              <span className="mr-1">⚽</span>
              {player.position}
            </span>
          )}
          {player.birth_date && (
            <span className="flex items-center">
              <span className="mr-1">📅</span>
              Né en {new Date(player.birth_date).getFullYear()}
            </span>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <span className="text-blue-600 font-mono text-sm">{player.topkit_reference}</span>
          <span className="text-gray-500 text-sm">{player.jerseys_count || 0} maillots</span>
        </div>
      </div>
    </div>
  );

  const CreatePlayerModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      full_name: '',
      nationality: '',
      position: '',
      birth_date: '',
      common_names: []
    });

    const [newName, setNewName] = useState('');
    
    // États pour la gestion des images
    const [imageFiles, setImageFiles] = useState({
      photo: null,
      secondary_photos: []
    });
    const [imagePreviews, setImagePreviews] = useState({
      photo: '',
      secondary_photos: []
    });

    const handleImageUpload = async (imageType, file) => {
      if (!file) return;
      
      if (file.size > 5 * 1024 * 1024) {
        alert('L\'image est trop volumineuse. Taille maximale : 5MB');
        return;
      }

      try {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (imageType === 'photo') {
            setImageFiles(prev => ({ ...prev, photo: file }));
            setImagePreviews(prev => ({ ...prev, photo: e.target.result }));
          } else if (imageType === 'secondary_photo') {
            setImageFiles(prev => ({
              ...prev,
              secondary_photos: [...prev.secondary_photos, file]
            }));
            setImagePreviews(prev => ({
              ...prev,
              secondary_photos: [...prev.secondary_photos, e.target.result]
            }));
          }
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error('Erreur lors du traitement de l\'image:', error);
        alert('Erreur lors du traitement de l\'image');
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

    const convertFileToBase64 = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!formData.name) {
        alert('Player name is required');
        return;
      }
      handleCreatePlayer({
        ...formData,
        birth_date: formData.birth_date ? new Date(formData.birth_date) : null
      });
    };

    const addName = () => {
      if (newName && !formData.common_names.includes(newName)) {
        setFormData({
          ...formData,
          common_names: [...formData.common_names, newName]
        });
        setNewName('');
      }
    };

    const removeName = (nameToRemove) => {
      setFormData({
        ...formData,
        common_names: formData.common_names.filter(name => name !== nameToRemove)
      });
    };

    const commonPositions = [
      'Gardien', 'Défenseur central', 'Arrière gauche', 'Arrière droit',
      'Milieu défensif', 'Milieu central', 'Milieu offensif',
      'Ailier gauche', 'Ailier droit', 'Attaquant', 'Avant-centre'
    ];

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-bold mb-4">Create New Player</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Player Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Kylian Mbappé"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom complet
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Kylian Mbappé Lottin"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nationalité
                </label>
                <input
                  type="text"
                  value={formData.nationality}
                  onChange={(e) => setFormData({...formData, nationality: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: France"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Position
                </label>
                <select
                  value={formData.position}
                  onChange={(e) => setFormData({...formData, position: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Sélectionner...</option>
                  {commonPositions.map(position => (
                    <option key={position} value={position}>{position}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date de naissance
              </label>
              <input
                type="date"
                value={formData.birth_date}
                onChange={(e) => setFormData({...formData, birth_date: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                max={new Date().toISOString().split('T')[0]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Noms alternatifs
              </label>
              <div className="flex space-x-2 mb-2">
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Mbappé, K. Mbappé"
                />
                <button
                  type="button"
                  onClick={addName}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  +
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.common_names.map((name, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm flex items-center"
                  >
                    {name}
                    <button
                      type="button"
                      onClick={() => removeName(name)}
                      className="ml-2 text-red-500 hover:text-red-700"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            
            {/* Section Upload d'Images */}
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 flex items-center gap-2">
                📸 Images du joueur
                <span className="text-xs text-gray-500 font-normal">(optionnel, max 5MB par image)</span>
              </h4>
              
              {/* Photo du joueur */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Photo du joueur
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload('photo', e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {imagePreviews.photo && (
                    <div className="relative">
                      <img src={imagePreviews.photo} alt="Aperçu photo" className="w-12 h-12 object-cover rounded-lg border" />
                      <button
                        type="button"
                        onClick={() => {
                          setImageFiles(prev => ({ ...prev, photo: null }));
                          setImagePreviews(prev => ({ ...prev, photo: '' }));
                        }}
                        className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Images secondaires */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Images secondaires (autres photos, célébrations, etc.)
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
                        <img src={preview} alt={`Aperçu ${index + 1}`} className="w-full h-16 object-cover rounded-lg border" />
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
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Player'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Football Players</h1>
          <p className="text-gray-600">
            Collaborative database of professional football players
          </p>
        </div>
        
        {user && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center"
          >
            <span className="mr-2">➕</span>
            Ajouter un joueur
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h3 className="font-semibold mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recherche
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Player name..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nationalité
            </label>
            <select
              value={filters.nationality}
              onChange={(e) => setFilters({...filters, nationality: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les nationalités</option>
              {nationalities.map(nationality => (
                <option key={nationality} value={nationality}>{nationality}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Position
            </label>
            <select
              value={filters.position}
              onChange={(e) => setFilters({...filters, position: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les positions</option>
              {positions.map(position => (
                <option key={position} value={position}>{position}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.verified_only}
                onChange={(e) => setFilters({...filters, verified_only: e.target.checked})}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Vérifiés uniquement</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ search: '', nationality: '', position: '', verified_only: false })}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Réinitialiser
            </button>
          </div>

          {/* Display Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Vue</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Par Page</label>
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

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{totalItems}</div>
          <div className="text-sm text-blue-700">Joueurs trouvés</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            {filteredPlayers.filter(p => p.verified_level !== 'unverified').length}
          </div>
          <div className="text-sm text-green-700">Joueurs vérifiés</div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{nationalities.length}</div>
          <div className="text-sm text-purple-700">Nationalités</div>
        </div>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">{positions.length}</div>
          <div className="text-sm text-orange-700">Positions</div>
        </div>
      </div>

      {/* Players Display with Pagination */}
      {currentItems.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">👤</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucun joueur trouvé</h3>
          <p className="text-gray-600 mb-4">
            Essayez de modifier vos filtres ou contribuez en ajoutant un nouveau joueur
          </p>
          {user && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Ajouter le premier joueur
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Grid View */}
          {displayOptions.viewMode === 'grid' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {currentItems.map(player => (
                <PlayerCard key={player.id} player={player} />
              ))}
            </div>
          )}

          {/* Thumbnail View */}
          {displayOptions.viewMode === 'thumbnail' && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
              {currentItems.map(player => (
                <PlayerThumbnail key={player.id} player={player} />
              ))}
            </div>
          )}

          {/* List View */}
          {displayOptions.viewMode === 'list' && (
            <div className="space-y-4">
              {currentItems.map(player => (
                <PlayerListItem key={player.id} player={player} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
              <div className="text-sm text-gray-700">
                Affichage {startIndex + 1} à {Math.min(endIndex, totalItems)} sur {totalItems} joueurs
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => goToPage(displayOptions.currentPage - 1)}
                  disabled={displayOptions.currentPage === 1}
                  className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Précédent
                </button>
                
                {/* Page numbers */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (displayOptions.currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (displayOptions.currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = displayOptions.currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => goToPage(pageNum)}
                      className={`px-3 py-2 text-sm font-medium rounded-md ${
                        pageNum === displayOptions.currentPage
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => goToPage(displayOptions.currentPage + 1)}
                  disabled={displayOptions.currentPage === totalPages}
                  className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Suivant
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create Player Modal */}
      {showCreateModal && <CreatePlayerModal />}

      {/* Player Detail Modal */}
      {selectedPlayer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedPlayer.name}</h2>
                {selectedPlayer.full_name && selectedPlayer.full_name !== selectedPlayer.name && (
                  <p className="text-gray-600">{selectedPlayer.full_name}</p>
                )}
                <p className="text-blue-600 font-mono text-sm">{selectedPlayer.topkit_reference}</p>
              </div>
              <button
                onClick={() => setSelectedPlayer(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="text-2xl">×</span>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Informations générales</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {selectedPlayer.nationality && (
                    <div>
                      <span className="text-gray-600">Nationalité:</span>
                      <span className="ml-2">{selectedPlayer.nationality}</span>
                    </div>
                  )}
                  {selectedPlayer.position && (
                    <div>
                      <span className="text-gray-600">Position:</span>
                      <span className="ml-2">{selectedPlayer.position}</span>
                    </div>
                  )}
                  {selectedPlayer.birth_date && (
                    <div>
                      <span className="text-gray-600">Naissance:</span>
                      <span className="ml-2">{new Date(selectedPlayer.birth_date).getFullYear()}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-600">Statut:</span>
                    <span className={`ml-2 ${selectedPlayer.verified_level !== 'unverified' ? 'text-green-600' : 'text-orange-600'}`}>
                      {selectedPlayer.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
                    </span>
                  </div>
                </div>
              </div>

              {selectedPlayer.common_names && selectedPlayer.common_names.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Noms alternatifs</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedPlayer.common_names.map((name, index) => (
                      <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                        {name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="font-semibold mb-2">Statistiques</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Maillots portés:</span>
                    <span className="ml-2 font-medium">{selectedPlayer.jerseys_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Collectionneurs:</span>
                    <span className="ml-2 font-medium">{selectedPlayer.collectors_count || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default CollaborativePlayersPage;