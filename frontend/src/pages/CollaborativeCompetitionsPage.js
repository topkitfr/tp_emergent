import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, List, LayoutGrid } from 'lucide-react';
import ContributionModal from '../ContributionModal';

const CollaborativeCompetitionsPage = ({ user, API, competitions, onDataUpdate }) => {
  const navigate = useNavigate();
  const [filteredCompetitions, setFilteredCompetitions] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    country: '',
    competition_type: '',
    verified_only: false
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid', // 'grid', 'thumbnail', 'list'
    itemsPerPage: 20,
    currentPage: 1
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCompetition, setSelectedCompetition] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedCompetitionForContribution, setSelectedCompetitionForContribution] = useState(null);
  
  // Get unique values for filters
  const countries = [...new Set(competitions.map(comp => comp.country).filter(Boolean))];
  const competitionTypes = [...new Set(competitions.map(comp => comp.competition_type).filter(Boolean))];

  // Apply filters and pagination
  useEffect(() => {
    let filtered = [...competitions];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(comp =>
        comp.name.toLowerCase().includes(searchLower) ||
        comp.official_name?.toLowerCase().includes(searchLower) ||
        comp.common_names?.some(name => name.toLowerCase().includes(searchLower))
      );
    }

    if (filters.country) {
      filtered = filtered.filter(comp => comp.country === filters.country);
    }

    if (filters.competition_type) {
      filtered = filtered.filter(comp => comp.competition_type === filters.competition_type);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(comp => comp.verified_level !== 'unverified');
    }

    setFilteredCompetitions(filtered);
    // Reset to first page when filters change
    setDisplayOptions(prev => ({ ...prev, currentPage: 1 }));
  }, [competitions, filters]);

  // Calculate pagination
  const totalItems = filteredCompetitions.length;
  const totalPages = Math.ceil(totalItems / displayOptions.itemsPerPage);
  const startIndex = (displayOptions.currentPage - 1) * displayOptions.itemsPerPage;
  const endIndex = startIndex + displayOptions.itemsPerPage;
  const currentItems = filteredCompetitions.slice(startIndex, endIndex);

  // Pagination handlers
  const goToPage = (page) => {
    setDisplayOptions(prev => ({ ...prev, currentPage: Math.max(1, Math.min(page, totalPages)) }));
  };

  // Create new competition
  const handleCreateCompetition = async (competitionData) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await fetch(`${API}/api/competitions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(competitionData)
      });

      if (response.ok) {
        const newCompetition = await response.json();
        alert(`✅ Compétition "${newCompetition.name}" créée avec succès ! (${newCompetition.topkit_reference})`);
        setShowCreateModal(false);
        onDataUpdate(); // Refresh data
      } else {
        const errorData = await response.json();
        console.error('Competition creation error:', errorData);
        
        // Better error handling to avoid [object Object] display
        let errorMessage = 'Failed to create competition';
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
        alert(`❌ Error: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error creating competition:', error);
      alert('❌ Erreur lors de la création de la compétition');
    }
    setLoading(false);
  };

  const getCompetitionIcon = (type) => {
    switch (type) {
      case 'domestic_league':
        return '🏆';
      case 'cup':
        return '🥇';
      case 'international':
        return '🌍';
      case 'friendly':
        return '🤝';
      default:
        return '🏆';
    }
  };

  const getCompetitionTypeLabel = (type) => {
    const labels = {
      'domestic_league': 'Championnat national',
      'cup': 'Coupe',
      'international': 'Compétition internationale',
      'friendly': 'Match amical'
    };
    return labels[type] || type;
  };

  const CompetitionCard = ({ competition }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
      onClick={() => navigate(`/competitions/${competition.id}`)}
    >
      {/* Image section - same structure as Master Jersey */}
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {competition.logo_url ? (
          <img 
            src={competition.logo_url.startsWith('data:') || competition.logo_url.startsWith('http') ? competition.logo_url : `${API}/${competition.logo_url}`}
            alt={`${competition.name} logo`}
            className="w-full h-full object-contain p-4"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: competition.logo_url ? 'none' : 'flex'}}>
          {getCompetitionIcon(competition.competition_type)}
        </div>
        
        {competition.verified_level !== 'unverified' && (
          <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
        
        <div className="absolute top-2 left-2 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">
          {getCompetitionIcon(competition.competition_type)} {getCompetitionTypeLabel(competition.competition_type)}
        </div>
      </div>
      
      {/* Content section - same structure as Master Jersey */}
      <div className="p-4">
        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
          {competition.name}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-600 mb-3">
          {competition.official_name && competition.official_name !== competition.name && (
            <div className="flex items-center">
              <span className="mr-1">📋</span>
              <span className="truncate">{competition.official_name}</span>
            </div>
          )}
          
          {competition.country && (
            <div className="flex items-center">
              <span className="mr-1">🌍</span>
              <span>{competition.country}</span>
            </div>
          )}
          
          {competition.level && (
            <div className="flex items-center">
              <span className="mr-1">📊</span>
              <span>Niveau {competition.level}</span>
            </div>
          )}
          
          {competition.organizer && (
            <div className="flex items-center">
              <span className="mr-1">🏢</span>
              <span className="truncate">{competition.organizer}</span>
            </div>
          )}
        </div>
        
        {/* Bottom section - same structure as Master Jersey */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-600 font-mono">{competition.topkit_reference}</span>
          <div className="flex items-center space-x-2 text-gray-500">
            <span>{competition.teams_count || 0} équipes</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Thumbnail version - smaller cards
  const CompetitionThumbnail = ({ competition }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-all cursor-pointer group"
      onClick={() => navigate(`/competitions/${competition.id}`)}
    >
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {competition.logo_url ? (
          <img 
            src={competition.logo_url.startsWith('data:') || competition.logo_url.startsWith('http') ? competition.logo_url : `${API}/${competition.logo_url}`}
            alt={`${competition.name} logo`}
            className="w-full h-full object-contain p-2"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-2xl flex items-center justify-center w-full h-full" style={{display: competition.logo_url ? 'none' : 'flex'}}>
          {getCompetitionIcon(competition.competition_type)}
        </div>
        
        {competition.verified_level !== 'unverified' && (
          <div className="absolute top-1 right-1 bg-green-100 text-green-800 px-1 py-0.5 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
      </div>
      
      <div className="p-2">
        <h3 className="font-bold text-xs text-gray-900 mb-1 group-hover:text-blue-600 line-clamp-1">
          {competition.name}
        </h3>
        <div className="text-xs text-gray-600 mb-1">
          {competition.country && <span>🌍 {competition.country}</span>}
        </div>
        <div className="text-xs text-blue-600 font-mono truncate">{competition.topkit_reference}</div>
      </div>
    </div>
  );

  // List version - horizontal layout
  const CompetitionListItem = ({ competition }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all cursor-pointer group flex items-center space-x-4"
      onClick={() => navigate(`/competitions/${competition.id}`)}
    >
      <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-gray-200 transition-colors">
        {competition.logo_url ? (
          <img 
            src={competition.logo_url.startsWith('data:') || competition.logo_url.startsWith('http') ? competition.logo_url : `${API}/${competition.logo_url}`}
            alt={`${competition.name} logo`}
            className="w-full h-full object-contain rounded-lg p-1"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-2xl flex items-center justify-center w-full h-full" style={{display: competition.logo_url ? 'none' : 'flex'}}>
          {getCompetitionIcon(competition.competition_type)}
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 truncate">
            {competition.name}
          </h3>
          {competition.verified_level !== 'unverified' && (
            <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium ml-2">
              ✓
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
          {competition.country && (
            <span className="flex items-center">
              <span className="mr-1">🌍</span>
              {competition.country}
            </span>
          )}
          {competition.competition_type && (
            <span className="flex items-center">
              <span className="mr-1">{getCompetitionIcon(competition.competition_type)}</span>
              {getCompetitionTypeLabel(competition.competition_type)}
            </span>
          )}
          {competition.level && (
            <span className="flex items-center">
              <span className="mr-1">📊</span>
              Niveau {competition.level}
            </span>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <span className="text-blue-600 font-mono text-sm">{competition.topkit_reference}</span>
          <span className="text-gray-500 text-sm">{competition.teams_count || 0} équipes</span>
        </div>
      </div>
    </div>
  );

  const CreateCompetitionModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      official_name: '',
      competition_type: 'domestic_league',
      country: '',
      level: '',
      start_year: '',
      current_season: '',
      common_names: []
    });

    const [newName, setNewName] = useState('');
    
    // États pour la gestion des images
    const [imageFiles, setImageFiles] = useState({
      logo: null,
      secondary_photos: []
    });
    const [imagePreviews, setImagePreviews] = useState({
      logo: '',
      secondary_photos: []
    });

    const handleImageUpload = async (imageType, file) => {
      if (!file) return;
      
      // Vérifier la taille du fichier (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        alert('L\'image est trop volumineuse. Taille maximale : 5MB');
        return;
      }

      try {
        // Convertir en base64 pour l'aperçu
        const reader = new FileReader();
        reader.onload = (e) => {
          if (imageType === 'logo') {
            setImageFiles(prev => ({ ...prev, logo: file }));
            setImagePreviews(prev => ({ ...prev, logo: e.target.result }));
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

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!formData.name || !formData.competition_type) {
        alert('Le nom et le type de compétition sont obligatoires');
        return;
      }

      try {
        // Map frontend form fields to backend model fields
        const competitionData = {
          ...formData,
          competition_name: formData.name, // Map name to competition_name
          type: formData.competition_type, // Map competition_type to type
          alternative_names: formData.common_names, // Map common_names to alternative_names
          level: formData.level ? parseInt(formData.level) : null,
          year_created: formData.start_year ? parseInt(formData.start_year) : null
        };

        // Remove frontend-only fields
        delete competitionData.name;
        delete competitionData.competition_type;
        delete competitionData.common_names;
        delete competitionData.start_year;

        // Ajouter le logo si présent
        if (imageFiles.logo) {
          const logoBase64 = await convertFileToBase64(imageFiles.logo);
          competitionData.logo = logoBase64; // Fixed: use 'logo' not 'logo_url'
        }

        // Ajouter les images secondaires si présentes
        if (imageFiles.secondary_photos.length > 0) {
          const secondaryImagesBase64 = await Promise.all(
            imageFiles.secondary_photos.map(file => convertFileToBase64(file))
          );
          competitionData.secondary_images = secondaryImagesBase64;
        }

        handleCreateCompetition(competitionData);
      } catch (error) {
        console.error('Erreur lors de la création:', error);
        alert('Erreur lors de la création de la compétition');
      }
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

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-bold mb-4">Create New League</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom de la ligue *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Ligue 1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom officiel
              </label>
              <input
                type="text"
                value={formData.official_name}
                onChange={(e) => setFormData({...formData, official_name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Ligue 1 Uber Eats"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type de ligue *
              </label>
              <select
                value={formData.competition_type}
                onChange={(e) => setFormData({...formData, competition_type: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="domestic_league">Championnat national</option>
                <option value="cup">Coupe</option>
                <option value="international">Compétition internationale</option>
                <option value="friendly">Match amical</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pays
                </label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({...formData, country: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: France"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Niveau
                </label>
                <select
                  value={formData.level}
                  onChange={(e) => setFormData({...formData, level: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Sélectionner le niveau</option>
                  <option value="pro">Pro</option>
                  <option value="semi pro">Semi Pro</option>
                  <option value="amateur">Amateur</option>
                  <option value="special">Special</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Année de création
                </label>
                <input
                  type="number"
                  value={formData.start_year}
                  onChange={(e) => setFormData({...formData, start_year: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: 1932"
                  min="1800"
                  max="2030"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Saison actuelle
                </label>
                <input
                  type="text"
                  value={formData.current_season}
                  onChange={(e) => setFormData({...formData, current_season: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: 2024-25"
                />
              </div>
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
                  placeholder="Ex: L1, Championnat de France"
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

            {/* Section Upload d'Images */}
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 flex items-center gap-2">
                📸 Images de la compétition
                <span className="text-xs text-gray-500 font-normal">(optionnel, max 5MB par image)</span>
              </h4>
              
              {/* Logo de la compétition */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo de la compétition
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
                      <img src={imagePreviews.logo} alt="Aperçu logo" className="w-12 h-12 object-cover rounded-lg border" />
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

              {/* Images secondaires */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Images secondaires (anciens logos, trophées, etc.)
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
                {loading ? 'Creating...' : 'Create Competition'}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Football Leagues</h1>
          <p className="text-gray-600">
            Collaborative database of football leagues and competitions
          </p>
        </div>
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
              placeholder="Nom de la compétition..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pays
            </label>
            <select
              value={filters.country}
              onChange={(e) => setFilters({...filters, country: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les pays</option>
              {countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.competition_type}
              onChange={(e) => setFilters({...filters, competition_type: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les types</option>
              {competitionTypes.map(type => (
                <option key={type} value={type}>{getCompetitionTypeLabel(type)}</option>
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
              <span className="text-sm text-gray-700">Vérifiées uniquement</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ search: '', country: '', competition_type: '', verified_only: false })}
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
                className={`px-3 py-2 text-sm flex items-center ${displayOptions.viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <Grid className="w-4 h-4 mr-1" />
                Grid
              </button>
              <button
                onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'thumbnail' }))}
                className={`px-3 py-2 text-sm border-x border-gray-300 flex items-center ${displayOptions.viewMode === 'thumbnail' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <LayoutGrid className="w-4 h-4 mr-1" />
                Thumb
              </button>
              <button
                onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'list' }))}
                className={`px-3 py-2 text-sm flex items-center ${displayOptions.viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <List className="w-4 h-4 mr-1" />
                List
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
          <div className="text-sm text-blue-700">Ligues trouvées</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            {filteredCompetitions.filter(c => c.verified_level !== 'unverified').length}
          </div>
          <div className="text-sm text-green-700">Ligues vérifiées</div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{countries.length}</div>
          <div className="text-sm text-purple-700">Pays représentés</div>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-yellow-600">{competitionTypes.length}</div>
          <div className="text-sm text-yellow-700">Types de ligues</div>
        </div>
      </div>

      {/* Competitions Display with Pagination */}
      {currentItems.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🏆</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune compétition trouvée</h3>
          <p className="text-gray-600 mb-4">
            Essayez de modifier vos filtres ou contribuez en ajoutant une nouvelle compétition
          </p>
          {user && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Ajouter la première compétition
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Grid View */}
          {displayOptions.viewMode === 'grid' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {currentItems.map(competition => (
                <CompetitionCard key={competition.id} competition={competition} />
              ))}
            </div>
          )}

          {/* Thumbnail View */}
          {displayOptions.viewMode === 'thumbnail' && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
              {currentItems.map(competition => (
                <CompetitionThumbnail key={competition.id} competition={competition} />
              ))}
            </div>
          )}

          {/* List View */}
          {displayOptions.viewMode === 'list' && (
            <div className="space-y-4">
              {currentItems.map(competition => (
                <CompetitionListItem key={competition.id} competition={competition} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
              <div className="text-sm text-gray-700">
                Affichage {startIndex + 1} à {Math.min(endIndex, totalItems)} sur {totalItems} compétitions
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

      {/* Create Competition Modal */}
      {showCreateModal && <CreateCompetitionModal />}

      {/* Competition Detail Modal */}
      {selectedCompetition && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedCompetition.name}</h2>
                {selectedCompetition.official_name && selectedCompetition.official_name !== selectedCompetition.name && (
                  <p className="text-gray-600">{selectedCompetition.official_name}</p>
                )}
                <p className="text-blue-600 font-mono text-sm">{selectedCompetition.topkit_reference}</p>
              </div>
              <div className="flex gap-2">
                {user && (
                  <button
                    onClick={() => {
                      setSelectedCompetitionForContribution(selectedCompetition);
                      setShowContributionModal(true);
                    }}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                  >
                    ✏️ Améliorer cette fiche
                  </button>
                )}
                <button
                  onClick={() => setSelectedCompetition(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Informations générales</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Type:</span>
                    <span className="ml-2">{getCompetitionTypeLabel(selectedCompetition.competition_type)}</span>
                  </div>
                  {selectedCompetition.country && (
                    <div>
                      <span className="text-gray-600">Pays:</span>
                      <span className="ml-2">{selectedCompetition.country}</span>
                    </div>
                  )}
                  {selectedCompetition.level && (
                    <div>
                      <span className="text-gray-600">Niveau:</span>
                      <span className="ml-2">{selectedCompetition.level}</span>
                    </div>
                  )}
                  {selectedCompetition.start_year && (
                    <div>
                      <span className="text-gray-600">Création:</span>
                      <span className="ml-2">{selectedCompetition.start_year}</span>
                    </div>
                  )}
                  {selectedCompetition.current_season && (
                    <div>
                      <span className="text-gray-600">Saison actuelle:</span>
                      <span className="ml-2">{selectedCompetition.current_season}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-600">Statut:</span>
                    <span className={`ml-2 ${selectedCompetition.verified_level !== 'unverified' ? 'text-green-600' : 'text-orange-600'}`}>
                      {selectedCompetition.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
                    </span>
                  </div>
                </div>
              </div>

              {selectedCompetition.common_names && selectedCompetition.common_names.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Noms alternatifs</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedCompetition.common_names.map((name, index) => (
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
                    <span className="text-gray-600">Équipes participantes:</span>
                    <span className="ml-2 font-medium">{selectedCompetition.teams_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Maillots référencés:</span>
                    <span className="ml-2 font-medium">{selectedCompetition.jerseys_count || 0}</span>
                  </div>
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
            setSelectedCompetitionForContribution(null);
          }}
          entity={selectedCompetitionForContribution}
          entityType="competition"
          onContributionCreated={(newContribution) => {
            console.log('Contribution créée:', newContribution);
            // Optionnel: rafraîchir les données
            if (onDataUpdate) {
              onDataUpdate();
            }
          }}
        />
      )}

    </div>
  );
};

export default CollaborativeCompetitionsPage;