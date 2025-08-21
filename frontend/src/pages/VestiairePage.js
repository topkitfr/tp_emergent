import React, { useState, useEffect } from 'react';

const VestiairePage = ({ user, API, onDataUpdate }) => {
  const [jerseyReleases, setJerseyReleases] = useState([]);
  const [masterJerseys, setMasterJerseys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    team_id: '',
    season: '',
    player_name: ''
  });
  const [newRelease, setNewRelease] = useState({
    master_jersey_id: '',
    player_name: '',
    player_number: '',
    release_type: 'player_version',
    retail_price: '',
    size_range: [],
    sku_code: ''
  });

  useEffect(() => {
    loadVestiaire();
    loadMasterJerseys();
  }, [filters]);

  const loadMasterJerseys = async () => {
    try {
      const response = await fetch(`${API}/api/master-jerseys`);
      const data = await response.json();
      setMasterJerseys(data || []);
    } catch (error) {
      console.error('Error loading master jerseys:', error);
    }
  };

  const loadVestiaire = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.team_id) params.append('team_id', filters.team_id);
      if (filters.season) params.append('season', filters.season);
      if (filters.player_name) params.append('player_name', filters.player_name);
      
      const response = await fetch(`${API}/api/vestiaire?${params}`);
      const data = await response.json();
      setJerseyReleases(data || []);
    } catch (error) {
      console.error('Error loading vestiaire:', error);
    }
    setLoading(false);
  };

  const createJerseyRelease = async () => {
    if (!user) {
      alert('Connectez-vous pour créer une version');
      return;
    }
    
    try {
      const releaseData = {
        ...newRelease,
        retail_price: parseFloat(newRelease.retail_price) || 80.0,
        player_number: parseInt(newRelease.player_number) || null,
        size_range: newRelease.size_range.length > 0 ? newRelease.size_range : ["S", "M", "L", "XL"],
        topkit_reference: `TK-RELEASE-${Date.now()}`
      };

      const response = await fetch(`${API}/api/jersey-releases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(releaseData)
      });
      
      if (response.ok) {
        setShowCreateModal(false);
        setNewRelease({
          master_jersey_id: '',
          player_name: '',
          player_number: '',
          release_type: 'player_version',
          retail_price: '',
          size_range: [],
          sku_code: ''
        });
        loadVestiaire(); // Refresh list
        alert('Version créée avec succès !');
      } else {
        const error = await response.text();
        alert(`Erreur: ${error}`);
      }
    } catch (error) {
      console.error('Error creating release:', error);
      alert('Erreur lors de la création');
    }
  };

  const CreateReleaseModal = () => (
    showCreateModal && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold">Créer une nouvelle version</h3>
            <button 
              onClick={() => setShowCreateModal(false)}
              className="text-gray-500 hover:text-gray-700 text-xl"
            >
              ✕
            </button>
          </div>

          <div className="space-y-4">
            {/* Master Jersey Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">Master Jersey *</label>
              <select
                value={newRelease.master_jersey_id}
                onChange={(e) => setNewRelease({...newRelease, master_jersey_id: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              >
                <option value="">Sélectionner un design</option>
                {masterJerseys.map(master => (
                  <option key={master.id} value={master.id}>
                    {master.team_info?.name} {master.season} - {master.jersey_type}
                  </option>
                ))}
              </select>
            </div>

            {/* Player Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nom du joueur</label>
                <input
                  type="text"
                  value={newRelease.player_name}
                  onChange={(e) => setNewRelease({...newRelease, player_name: e.target.value})}
                  placeholder="ex: Mbappé"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Numéro</label>
                <input
                  type="number"
                  value={newRelease.player_number}
                  onChange={(e) => setNewRelease({...newRelease, player_number: e.target.value})}
                  placeholder="ex: 7"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
            </div>

            {/* Release Type & Price */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Type de version</label>
                <select
                  value={newRelease.release_type}
                  onChange={(e) => setNewRelease({...newRelease, release_type: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="player_version">Version Joueur</option>
                  <option value="fan_version">Version Fan</option>
                  <option value="authentic">Authentique</option>
                  <option value="replica">Réplique</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Prix de vente (€)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newRelease.retail_price}
                  onChange={(e) => setNewRelease({...newRelease, retail_price: e.target.value})}
                  placeholder="89.99"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
            </div>

            {/* SKU Code */}
            <div>
              <label className="block text-sm font-medium mb-2">Code SKU</label>
              <input
                type="text"
                value={newRelease.sku_code}
                onChange={(e) => setNewRelease({...newRelease, sku_code: e.target.value})}
                placeholder="ex: DJ7949-001"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={createJerseyRelease}
              disabled={!newRelease.master_jersey_id}
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Créer la version
            </button>
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-6 py-3 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
          </div>
        </div>
      </div>
    )
  );

  const addToCollection = async (release) => {
    if (!user) {
      alert('Connectez-vous pour ajouter à votre collection');
      return;
    }
    
    try {
      const response = await fetch(`${API}/api/users/${user.id}/collections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          jersey_release_id: release.id,
          size: 'M', // Default, could be selection modal
          condition: 'excellent'
        })
      });
      
      if (response.ok) {
        alert('Maillot ajouté à votre collection !');
      }
    } catch (error) {
      console.error('Error adding to collection:', error);
    }
  };

  const JerseyReleaseCard = ({ release }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      
      {/* Jersey Image */}
      <div className="aspect-square bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
        {release.product_images?.[0] ? (
          <img 
            src={release.product_images[0]} 
            alt="Jersey" 
            className="w-full h-full object-cover rounded-lg"
          />
        ) : (
          <span className="text-4xl">👕</span>
        )}
      </div>

      {/* Master Jersey Info */}
      <div className="space-y-2 mb-4">
        <h3 className="font-bold text-gray-900">
          {release.master_jersey_info?.team_info?.name || 'Équipe inconnue'}
        </h3>
        <p className="text-sm text-gray-600">
          {release.master_jersey_info?.season} • {release.master_jersey_info?.jersey_type}
        </p>
        <p className="text-xs text-gray-500">
          {release.master_jersey_info?.brand_info?.name}
        </p>
      </div>

      {/* Release Specific Info */}
      <div className="space-y-1 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Type:</span>
          <span className="font-medium">{release.release_type}</span>
        </div>
        {release.player_name && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Joueur:</span>
            <span className="font-medium">{release.player_name} #{release.player_number}</span>
          </div>
        )}
        {release.size_range?.length > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Tailles:</span>
            <span className="font-medium">{release.size_range.join(', ')}</span>
          </div>
        )}
        {release.sku_code && (
          <div className="text-xs text-gray-500">
            SKU: {release.sku_code}
          </div>
        )}
      </div>

      {/* Price Estimation */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-green-700">Estimation:</span>
          <div className="text-right">
            <div className="font-bold text-green-600">
              {release.estimated_value}€
            </div>
            <div className="text-xs text-green-500">
              {release.estimated_min}€ - {release.estimated_max}€
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button 
          onClick={() => addToCollection(release)}
          className="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 transition-colors"
        >
          + Collection
        </button>
        <button className="px-3 py-2 text-gray-600 hover:text-gray-800 text-sm border border-gray-300 rounded">
          Détails
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              👕 Le Vestiaire
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Découvrez toutes les versions physiques disponibles des maillots référencés.
              Ajoutez-les à votre collection et suivez leur valeur !
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{jerseyReleases.length}</div>
              <div className="text-sm text-blue-700">Releases disponibles</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {jerseyReleases.length > 0 ? Math.round(jerseyReleases.reduce((sum, r) => sum + (r.estimated_value || 0), 0) / jerseyReleases.length) : 0}€
              </div>
              <div className="text-sm text-green-700">Prix moyen estimé</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {new Set(jerseyReleases.map(r => r.player_name).filter(Boolean)).size}
              </div>
              <div className="text-sm text-purple-700">Joueurs différents</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Rechercher un joueur..."
              value={filters.player_name}
              onChange={(e) => setFilters({...filters, player_name: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Saison (ex: 2022-23)"
              value={filters.season}
              onChange={(e) => setFilters({...filters, season: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={loadVestiaire}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Filtrer
            </button>
            <button 
              onClick={() => setFilters({search: '', team_id: '', season: '', player_name: ''})}
              className="text-gray-600 hover:text-gray-800"
            >
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement du vestiaire...</p>
          </div>
        ) : jerseyReleases.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {jerseyReleases.map(release => (
              <JerseyReleaseCard key={release.id} release={release} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👕</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune release trouvée</h3>
            <p className="text-gray-600">
              Aucun maillot ne correspond à vos critères. Essayez d'autres filtres !
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VestiairePage;