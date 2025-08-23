import React, { useState, useEffect } from 'react';

const CollaborativePlayersPage = ({ user, API, players, onDataUpdate }) => {
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    nationality: '',
    position: '',
    verified_only: false
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Get unique values for filters
  const nationalities = [...new Set(players.map(player => player.nationality).filter(Boolean))];
  const positions = [...new Set(players.map(player => player.position).filter(Boolean))];

  // Apply filters
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
  }, [players, filters]);

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
      onClick={() => window.location.href = `/players/${player.id}`}
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
        
        {player.position && (
          <div className="absolute top-2 left-2 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
            ⚽ {player.position}
          </div>
        )}
      </div>
      
      {/* Content section - same structure as Master Jersey */}
      <div className="p-4">
        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
          {player.name}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-600 mb-3">
          {player.full_name && player.full_name !== player.name && (
            <div className="flex items-center">
              <span className="mr-1">📋</span>
              <span className="truncate">{player.full_name}</span>
            </div>
          )}
          
          {player.nationality && (
            <div className="flex items-center">
              <span className="mr-1">🌍</span>
              <span>{player.nationality}</span>
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

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!formData.name) {
        alert('Le nom du joueur est obligatoire');
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
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-bold mb-4">Créer un nouveau joueur</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom du joueur *
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
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Création...' : 'Créer le joueur'}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Joueurs de football</h1>
          <p className="text-gray-600">
            Base de données collaborative des joueurs et de leurs maillots
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
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recherche
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Nom du joueur..."
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
              <span className="text-sm text-gray-700">Joueurs vérifiés uniquement</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ search: '', nationality: '', position: '', verified_only: false })}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Réinitialiser les filtres
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{filteredPlayers.length}</div>
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

      {/* Players Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPlayers.map(player => (
          <PlayerCard key={player.id} player={player} />
        ))}
      </div>

      {filteredPlayers.length === 0 && (
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
      )}

      {/* Create Player Modal */}
      {showCreateModal && <CreatePlayerModal />}

      {/* Player Detail Modal */}
      {selectedPlayer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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