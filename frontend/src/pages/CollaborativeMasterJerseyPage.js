import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ContributionModal from '../ContributionModal';

const CollaborativeMasterJerseyPage = ({ 
  user, 
  API, 
  masterJerseys, 
  teams, 
  brands, 
  competitions, 
  onDataUpdate 
}) => {
  const navigate = useNavigate();
  const [filteredJerseys, setFilteredJerseys] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    team_id: '',
    brand_id: '',
    season: '',
    jersey_type: '',
    verified_only: false
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid', // 'grid', 'thumbnail', 'list'
    itemsPerPage: 20,
    currentPage: 1
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedJerseyForContribution, setSelectedJerseyForContribution] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Get unique values for filters - with safety checks
  const seasons = [...new Set((masterJerseys || []).map(jersey => jersey.season).filter(Boolean))];
  const jerseyTypes = [...new Set((masterJerseys || []).map(jersey => jersey.jersey_type).filter(Boolean))];

  // Apply filters and pagination
  useEffect(() => {
    let filtered = [...(masterJerseys || [])];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(jersey =>
        jersey.team_info?.name?.toLowerCase().includes(searchLower) ||
        jersey.brand_info?.name?.toLowerCase().includes(searchLower) ||
        jersey.season?.toLowerCase().includes(searchLower) ||
        jersey.design_name?.toLowerCase().includes(searchLower)
      );
    }

    if (filters.team_id) {
      filtered = filtered.filter(jersey => jersey.team_info?.id === filters.team_id);
    }

    if (filters.brand_id) {
      filtered = filtered.filter(jersey => jersey.brand_info?.id === filters.brand_id);
    }

    if (filters.season) {
      filtered = filtered.filter(jersey => jersey.season === filters.season);
    }

    if (filters.jersey_type) {
      filtered = filtered.filter(jersey => jersey.jersey_type === filters.jersey_type);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(jersey => jersey.verified_level !== 'unverified');
    }

    setFilteredJerseys(filtered);
    // Reset to first page when filters change
    setDisplayOptions(prev => ({ ...prev, currentPage: 1 }));
  }, [masterJerseys, filters]);

  // Calculate pagination
  const totalItems = filteredJerseys.length;
  const totalPages = Math.ceil(totalItems / displayOptions.itemsPerPage);
  const startIndex = (displayOptions.currentPage - 1) * displayOptions.itemsPerPage;
  const endIndex = startIndex + displayOptions.itemsPerPage;
  const currentItems = filteredJerseys.slice(startIndex, endIndex);

  // Pagination handlers
  const goToPage = (page) => {
    setDisplayOptions(prev => ({ ...prev, currentPage: Math.max(1, Math.min(page, totalPages)) }));
  };

  // Create new master jersey
  const handleCreateMasterJersey = async (jerseyData) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await fetch(`${API}/api/master-kits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(jerseyData)
      });

      if (response.ok) {
        const newJersey = await response.json();
        alert(`✅ Maillot "${newJersey.team_info?.name} ${newJersey.season}" créé avec succès ! (${newJersey.topkit_reference})`);
        setShowCreateModal(false);
        onDataUpdate(); // Refresh data
      } else {
        const error = await response.json();
        console.error('API Error Response:', error);
        
        // Handle different error response formats
        let errorMessage = 'Une erreur est survenue';
        
        if (error.detail) {
          // FastAPI validation error
          if (typeof error.detail === 'string') {
            errorMessage = error.detail;
          } else if (Array.isArray(error.detail)) {
            // Pydantic validation errors
            errorMessage = error.detail.map(err => err.msg || err.message).join(', ');
          } else if (typeof error.detail === 'object') {
            errorMessage = JSON.stringify(error.detail);
          }
        } else if (error.message) {
          errorMessage = error.message;
        } else if (typeof error === 'string') {
          errorMessage = error;
        }
        
        console.error('Processed error message:', errorMessage);
        alert(`❌ Erreur: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error creating master jersey:', error);
      const errorMessage = error.message || 'Erreur de connexion ou problème technique';
      alert(`❌ Erreur lors de la création du maillot: ${errorMessage}`);
    }
    setLoading(false);
  };

  const getJerseyTypeLabel = (type) => {
    const labels = {
      'home': 'Domicile',
      'away': 'Extérieur',
      'third': 'Troisième',
      'goalkeeper': 'Gardien',
      'training': 'Entraînement',
      'special': 'Spécial'
    };
    return labels[type] || type;
  };

  const getJerseyTypeIcon = (type) => {
    const icons = {
      'home': '🏠',
      'away': '✈️',
      'third': '3️⃣',
      'goalkeeper': '🥅',
      'training': '🏃',
      'special': '⭐'
    };
    return icons[type] || '👕';
  };

  const MasterJerseyCard = ({ jersey }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
      onClick={() => navigate(`/master-kits/${jersey.id}`)}
    >
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors overflow-hidden">
        {jersey.main_image_url ? (
          <img 
            src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `${process.env.REACT_APP_BACKEND_URL}/${jersey.main_image_url}`}
            alt={`${jersey.team_info?.name} ${jersey.season}`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <span className="text-4xl" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>👕</span>
        {jersey.verified_level !== 'unverified' && (
          <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
        <div className="absolute top-2 left-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
          {getJerseyTypeIcon(jersey.jersey_type)} {getJerseyTypeLabel(jersey.jersey_type)}
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
          {jersey.team_info?.name || 'Équipe inconnue'}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-600 mb-3">
          <div className="flex items-center">
            <span className="mr-1">📅</span>
            <span>{jersey.season}</span>
          </div>
          
          <div className="flex items-center">
            <span className="mr-1">👕</span>
            <span>{jersey.brand_info?.name || 'Marque inconnue'}</span>
          </div>
          
          {jersey.design_name && (
            <div className="flex items-center">
              <span className="mr-1">🎨</span>
              <span className="truncate">{jersey.design_name}</span>
            </div>
          )}
          
          {jersey.primary_color && (
            <div className="flex items-center">
              <div 
                className="w-3 h-3 rounded-full border border-gray-300 mr-1"
                style={{ backgroundColor: jersey.primary_color }}
              ></div>
              <span className="capitalize">{jersey.primary_color}</span>
            </div>
          )}
          
          {jersey.main_sponsor && (
            <div className="flex items-center">
              <span className="mr-1">🏢</span>
              <span className="truncate">{jersey.main_sponsor}</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-600 font-mono">{jersey.topkit_reference}</span>
          <div className="flex items-center space-x-2 text-gray-500">
            <span>{jersey.releases_count || 0} versions</span>
            <span>•</span>
            <span>{jersey.collectors_count || 0} collectionneurs</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Thumbnail version - smaller cards
  const MasterJerseyThumbnail = ({ jersey }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
      onClick={() => navigate(`/master-kits/${jersey.id}`)}
    >
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors overflow-hidden">
        {jersey.main_image_url ? (
          <img 
            src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `${process.env.REACT_APP_BACKEND_URL}/${jersey.main_image_url}`}
            alt={`${jersey.team_info?.name} ${jersey.season}`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <span className="text-2xl" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>👕</span>
        {jersey.verified_level !== 'unverified' && (
          <div className="absolute top-1 right-1 bg-green-100 text-green-800 px-1 py-0.5 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
      </div>
      
      <div className="p-2">
        <h3 className="font-bold text-xs text-gray-900 mb-1 group-hover:text-blue-600 line-clamp-1">
          {jersey.team_info?.name || 'Équipe inconnue'}
        </h3>
        <div className="text-xs text-gray-600 mb-1">
          <span>📅 {jersey.season}</span>
        </div>
        <div className="text-xs text-blue-600 font-mono truncate">{jersey.topkit_reference}</div>
      </div>
    </div>
  );

  // List version - horizontal layout
  const MasterJerseyListItem = ({ jersey }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all cursor-pointer group flex items-center space-x-4"
      onClick={() => navigate(`/master-kits/${jersey.id}`)}
    >
      <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-gray-200 transition-colors overflow-hidden">
        {jersey.main_image_url ? (
          <img 
            src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `${process.env.REACT_APP_BACKEND_URL}/${jersey.main_image_url}`}
            alt={`${jersey.team_info?.name} ${jersey.season}`}
            className="w-full h-full object-cover rounded-lg"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <span className="text-2xl" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>👕</span>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 truncate">
            {jersey.team_info?.name || 'Équipe inconnue'}
          </h3>
          {jersey.verified_level !== 'unverified' && (
            <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium ml-2">
              ✓
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
          <span className="flex items-center">
            <span className="mr-1">📅</span>
            {jersey.season}
          </span>
          <span className="flex items-center">
            <span className="mr-1">{getJerseyTypeIcon(jersey.jersey_type)}</span>
            {getJerseyTypeLabel(jersey.jersey_type)}
          </span>
          <span className="flex items-center">
            <span className="mr-1">👕</span>
            {jersey.brand_info?.name || 'Marque inconnue'}
          </span>
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <span className="text-blue-600 font-mono text-sm">{jersey.topkit_reference}</span>
          <div className="flex items-center space-x-2 text-gray-500 text-sm">
            <span>{jersey.releases_count || 0} versions</span>
            <span>•</span>
            <span>{jersey.collectors_count || 0} collectionneurs</span>
          </div>
        </div>
      </div>
    </div>
  );

  const CreateMasterJerseyModal = () => {
    const [formData, setFormData] = useState({
      team_id: '',
      brand_id: '',
      season: new Date().getFullYear() + '-' + (new Date().getFullYear() + 1).toString().slice(-2), // Default to current season
      jersey_type: 'home',
      model: 'authentic',
      colors: '',
      pattern: '',
      main_image_url: ''
    });


    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!formData.team_id || !formData.brand_id || !formData.season || !formData.jersey_type || !formData.model || !formData.colors || !formData.main_image_url) {
        alert('Tous les champs marqués * sont obligatoires');
        return;
      }

      try {
        // Prepare data according to the MasterJerseyCreate model
        const masterJerseyData = {
          team_id: formData.team_id,
          brand_id: formData.brand_id,
          season: formData.season,
          jersey_type: formData.jersey_type,
          model: formData.model,
          primary_color: formData.colors,
          secondary_colors: [], // Default empty array
          main_image_url: formData.main_image_url
        };

        console.log('Sending Master Jersey data:', masterJerseyData);
        handleCreateMasterJersey(masterJerseyData);
      } catch (error) {
        console.error('Erreur lors de la création:', error);
        alert('Erreur lors de la création du Master Kit');
      }
    };



    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
          <h3 className="text-lg font-bold mb-4">Créer un nouveau Master Jersey</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Équipe <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.team_id}
                onChange={(e) => setFormData({...formData, team_id: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Sélectionner une équipe</option>
                {(teams || []).map(team => (
                  <option key={team.id} value={team.id}>{team.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Marque <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.brand_id}
                onChange={(e) => setFormData({...formData, brand_id: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Sélectionner une marque</option>
                {(brands || []).map(brand => (
                  <option key={brand.id} value={brand.id}>{brand.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Saison <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.season}
                onChange={(e) => setFormData({...formData, season: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="2024-25"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.jersey_type}
                onChange={(e) => setFormData({...formData, jersey_type: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="home">Home</option>
                <option value="away">Away</option>
                <option value="third">Third</option>
                <option value="fourth">Fourth</option>
                <option value="goalkeeper">GK1</option>
                <option value="special">GK2</option>
                <option value="special">Special</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Modèle <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.model}
                onChange={(e) => setFormData({...formData, model: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="authentic">Authentique</option>
                <option value="replica">Réplique</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Couleurs <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.colors}
                onChange={(e) => setFormData({...formData, colors: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Blue, White, Red"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Pattern
              </label>
              <textarea
                value={formData.pattern}
                onChange={(e) => setFormData({...formData, pattern: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
                placeholder="Description du motif, design, rayures..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Photo principale (face uniquement) <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    // Check file size (max 5MB)
                    if (file.size > 5 * 1024 * 1024) {
                      alert('La taille de l\'image ne doit pas dépasser 5MB');
                      return;
                    }
                    // Convert to base64
                    const reader = new FileReader();
                    reader.onload = (e) => {
                      setFormData({...formData, main_image_url: e.target.result});
                    };
                    reader.readAsDataURL(file);
                  }
                }}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
              />
              {formData.main_image_url && (
                <div className="mt-2">
                  <img 
                    src={formData.main_image_url} 
                    alt="Aperçu de la photo principale" 
                    className="w-24 h-24 object-cover rounded-lg border"
                  />
                  <p className="text-xs text-green-600 mt-1">✓ Image chargée avec succès</p>
                </div>
              )}
              <p className="text-xs text-gray-500 mt-1">
                <strong>Image de face du maillot uniquement.</strong> Formats acceptés: JPG, PNG (max 5MB). Les photos secondaires ne sont pas autorisées pour les Master Kits.
              </p>
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
                {loading ? 'Création...' : 'Créer le Master Jersey'}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Master Jerseys</h1>
          <p className="text-gray-600">
            Base de données collaborative des designs uniques de maillots de football
          </p>
        </div>
        
        {user && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center"
          >
            <span className="mr-2">➕</span>
            Ajouter un Master Jersey
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h3 className="font-semibold mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-8 gap-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recherche
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Équipe, marque, saison..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Équipe
            </label>
            <select
              value={filters.team_id}
              onChange={(e) => setFilters({...filters, team_id: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les équipes</option>
              {(teams || []).map(team => (
                <option key={team.id} value={team.id}>{team.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Marque
            </label>
            <select
              value={filters.brand_id}
              onChange={(e) => setFilters({...filters, brand_id: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les marques</option>
              {(brands || []).map(brand => (
                <option key={brand.id} value={brand.id}>{brand.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Saison
            </label>
            <select
              value={filters.season}
              onChange={(e) => setFilters({...filters, season: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les saisons</option>
              {seasons.map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.jersey_type}
              onChange={(e) => setFilters({...filters, jersey_type: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les types</option>
              {jerseyTypes.map(type => (
                <option key={type} value={type}>{getJerseyTypeLabel(type)}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col justify-end">
            <label className="flex items-center mb-2">
              <input
                type="checkbox"
                checked={filters.verified_only}
                onChange={(e) => setFilters({...filters, verified_only: e.target.checked})}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Vérifiés uniquement</span>
            </label>
            
            <button
              onClick={() => setFilters({ search: '', team_id: '', brand_id: '', season: '', jersey_type: '', verified_only: false })}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium text-left"
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
          <div className="text-sm text-blue-700">Master Jerseys trouvés</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            {filteredJerseys.filter(j => j.verified_level !== 'unverified').length}
          </div>
          <div className="text-sm text-green-700">Maillots vérifiés</div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{seasons.length}</div>
          <div className="text-sm text-purple-700">Saisons représentées</div>
        </div>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">
            {filteredJerseys.reduce((total, jersey) => total + (jersey.releases_count || 0), 0)}
          </div>
          <div className="text-sm text-orange-700">Versions totales</div>
        </div>
      </div>

      {/* Master Jerseys Display with Pagination */}
      {currentItems.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">👕</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucun Master Jersey trouvé</h3>
          <p className="text-gray-600 mb-4">
            Essayez de modifier vos filtres ou contribuez en ajoutant un nouveau design de maillot
          </p>
          {user && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Ajouter le premier Master Jersey
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Grid View */}
          {displayOptions.viewMode === 'grid' && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
              {currentItems.map(jersey => (
                <MasterJerseyCard key={jersey.id} jersey={jersey} />
              ))}
            </div>
          )}

          {/* Thumbnail View */}
          {displayOptions.viewMode === 'thumbnail' && (
            <div className="grid grid-cols-3 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-3">
              {currentItems.map(jersey => (
                <MasterJerseyThumbnail key={jersey.id} jersey={jersey} />
              ))}
            </div>
          )}

          {/* List View */}
          {displayOptions.viewMode === 'list' && (
            <div className="space-y-4">
              {currentItems.map(jersey => (
                <MasterJerseyListItem key={jersey.id} jersey={jersey} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
              <div className="text-sm text-gray-700">
                Affichage {startIndex + 1} à {Math.min(endIndex, totalItems)} sur {totalItems} Master Jerseys
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

      {/* Create Master Jersey Modal */}
      {showCreateModal && <CreateMasterJerseyModal />}

      {/* Jersey Detail Modal */}
      {selectedJersey && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedJersey.team_info?.name || 'Équipe inconnue'} {selectedJersey.season}
                </h2>
                <p className="text-gray-600">
                  {getJerseyTypeLabel(selectedJersey.jersey_type)} - {selectedJersey.brand_info?.name}
                </p>
                <p className="text-blue-600 font-mono text-sm">{selectedJersey.topkit_reference}</p>
              </div>
              <div className="flex gap-2">
                {user && (
                  <button
                    onClick={() => {
                      setSelectedJerseyForContribution(selectedJersey);
                      setShowContributionModal(true);
                    }}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                  >
                    ✏️ Améliorer cette fiche
                  </button>
                )}
                <button
                  onClick={() => setSelectedJersey(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Image Preview */}
              <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                {selectedJersey.main_image_url ? (
                  <img 
                    src={selectedJersey.main_image_url.startsWith('data:') || selectedJersey.main_image_url.startsWith('http') ? selectedJersey.main_image_url : `${process.env.REACT_APP_BACKEND_URL}/${selectedJersey.main_image_url}`}
                    alt={`${selectedJersey.team_info?.name} ${selectedJersey.season}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <span className="text-8xl" style={{display: selectedJersey.main_image_url ? 'none' : 'flex'}}>👕</span>
              </div>

              {/* Details */}
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2 text-gray-900">Informations générales</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Équipe:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedJersey.team_info?.name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Marque:</span>
                      <span className="ml-2 text-gray-900">{selectedJersey.brand_info?.name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Saison:</span>
                      <span className="ml-2 text-gray-900">{selectedJersey.season}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Type:</span>
                      <span className="ml-2 text-gray-900">{getJerseyTypeLabel(selectedJersey.jersey_type)}</span>
                    </div>
                    {selectedJersey.design_name && (
                      <div>
                        <span className="text-gray-600">Design:</span>
                        <span className="ml-2 text-gray-900">{selectedJersey.design_name}</span>
                      </div>
                    )}
                    {selectedJersey.main_sponsor && (
                      <div>
                        <span className="text-gray-600">Sponsor:</span>
                        <span className="ml-2 text-gray-900">{selectedJersey.main_sponsor}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Colors */}
                <div>
                  <h3 className="font-semibold mb-2 text-gray-900">Couleurs</h3>
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-6 h-6 rounded-full border border-gray-300"
                      style={{ backgroundColor: selectedJersey.primary_color }}
                      title={selectedJersey.primary_color}
                    ></div>
                    <span className="text-sm capitalize text-gray-900">{selectedJersey.primary_color}</span>
                    {selectedJersey.secondary_colors && selectedJersey.secondary_colors.map((color, index) => (
                      <div key={index} className="flex items-center space-x-1">
                        <div
                          className="w-4 h-4 rounded-full border border-gray-300"
                          style={{ backgroundColor: color }}
                          title={color}
                        ></div>
                        <span className="text-xs capitalize text-gray-600">{color}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pattern Description */}
                {selectedJersey.pattern_description && (
                  <div>
                    <h3 className="font-semibold mb-2 text-gray-900">Description du motif</h3>
                    <p className="text-sm text-gray-600">{selectedJersey.pattern_description}</p>
                  </div>
                )}

                {/* Special Features */}
                {selectedJersey.special_features && selectedJersey.special_features.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2 text-gray-900">Caractéristiques spéciales</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedJersey.special_features.map((feature, index) => (
                        <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div>
                  <h3 className="font-semibold mb-2 text-gray-900">Statistiques</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Versions:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedJersey.releases_count || 0}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Collectionneurs:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedJersey.collectors_count || 0}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <span className="text-gray-600">Statut:</span>
                  <span className={`ml-2 ${selectedJersey.verified_level !== 'unverified' ? 'text-green-600' : 'text-orange-600'}`}>
                    {selectedJersey.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Contribution Modal */}
      {showContributionModal && (
        <ContributionModal
          isOpen={showContributionModal}
          onClose={() => {
            setShowContributionModal(false);
            setSelectedJerseyForContribution(null);
          }}
          entity={selectedJerseyForContribution}
          entityType="master_jersey"
          onContributionCreated={(newContribution) => {
            console.log('Contribution créée:', newContribution);
            if (onDataUpdate) {
              onDataUpdate();
            }
          }}
        />
      )}

    </div>
  );
};

export default CollaborativeMasterJerseyPage;