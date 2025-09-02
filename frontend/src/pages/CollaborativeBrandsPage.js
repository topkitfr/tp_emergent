import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ContributionModal from '../ContributionModal';

const CollaborativeBrandsPage = ({ user, API, brands, onDataUpdate }) => {
  const navigate = useNavigate();
  const [filteredBrands, setFilteredBrands] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    country: '',
    verified_only: false
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [selectedBrandForContribution, setSelectedBrandForContribution] = useState(null);
  
  // Get unique countries for filter
  const countries = [...new Set(brands.map(brand => brand.country).filter(Boolean))];

  // Apply filters
  useEffect(() => {
    let filtered = [...brands];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(brand =>
        brand.name.toLowerCase().includes(searchLower) ||
        brand.official_name?.toLowerCase().includes(searchLower) ||
        brand.common_names?.some(name => name.toLowerCase().includes(searchLower))
      );
    }

    if (filters.country) {
      filtered = filtered.filter(brand => brand.country === filters.country);
    }

    if (filters.verified_only) {
      filtered = filtered.filter(brand => brand.verified_level !== 'unverified');
    }

    setFilteredBrands(filtered);
  }, [brands, filters]);

  // Create new brand
  const handleCreateBrand = async (brandData) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await fetch(`${API}/api/brands`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(brandData)
      });

      if (response.ok) {
        const newBrand = await response.json();
        alert(`✅ Marque "${newBrand.name}" créée avec succès ! (${newBrand.topkit_reference})`);
        setShowCreateModal(false);
        onDataUpdate(); // Refresh data
      } else {
        const error = await response.json();
        alert(`❌ Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating brand:', error);
      alert('❌ Erreur lors de la création de la marque');
    }
    setLoading(false);
  };

  const BrandCard = ({ brand }) => (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
      onClick={() => navigate(`/brands/${brand.id}`)}
    >
      {/* Image section - same structure as Master Jersey */}
      <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
        {brand.logo_url ? (
          <img 
            src={brand.logo_url.startsWith('data:') || brand.logo_url.startsWith('http') ? brand.logo_url : `${API}/${brand.logo_url}`}
            alt={`${brand.name} logo`}
            className="w-full h-full object-contain p-4"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="text-4xl flex items-center justify-center w-full h-full" style={{display: brand.logo_url ? 'none' : 'flex'}}>
          👕
        </div>
        
        {brand.verified_level !== 'unverified' && (
          <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
            ✓
          </div>
        )}
        
        {brand.country && (
          <div className="absolute top-2 left-2 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
            🌍 {brand.country}
          </div>
        )}
      </div>
      
      {/* Content section - same structure as Master Jersey */}
      <div className="p-4">
        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-blue-600 line-clamp-2">
          {brand.name}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-600 mb-3">
          {brand.official_name && brand.official_name !== brand.name && (
            <div className="flex items-center">
              <span className="mr-1">📋</span>
              <span className="truncate">{brand.official_name}</span>
            </div>
          )}
          
          {brand.founded_year && (
            <div className="flex items-center">
              <span className="mr-1">📅</span>
              <span>Fondée en {brand.founded_year}</span>
            </div>
          )}
          
          {brand.common_names && brand.common_names.length > 0 && (
            <div className="flex items-center">
              <span className="mr-1">🏷️</span>
              <span className="truncate">{brand.common_names.slice(0, 2).join(", ")}</span>
              {brand.common_names.length > 2 && (
                <span className="ml-1 text-gray-400">+{brand.common_names.length - 2}</span>
              )}
            </div>
          )}
        </div>
        
        {/* Bottom section - same structure as Master Jersey */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-600 font-mono">{brand.topkit_reference}</span>
          <div className="flex items-center space-x-2 text-gray-500">
            <span>{brand.jerseys_count || 0} maillots</span>
          </div>
        </div>
      </div>
    </div>
  );

  const CreateBrandModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      official_name: '',
      country: '',
      founded_year: '',
      website: '',
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
      if (!formData.name) {
        alert('Le nom de la marque est obligatoire');
        return;
      }

      try {
        // Préparer les données avec les images en base64
        const brandData = {
          ...formData,
          founded_year: formData.founded_year ? parseInt(formData.founded_year) : null
        };

        // Ajouter le logo si présent
        if (imageFiles.logo) {
          const logoBase64 = await convertFileToBase64(imageFiles.logo);
          brandData.logo_url = logoBase64;
        }

        // Ajouter les images secondaires si présentes
        if (imageFiles.secondary_photos.length > 0) {
          const secondaryImagesBase64 = await Promise.all(
            imageFiles.secondary_photos.map(file => convertFileToBase64(file))
          );
          brandData.secondary_images = secondaryImagesBase64;
        }

        handleCreateBrand(brandData);
      } catch (error) {
        console.error('Erreur lors de la création:', error);
        alert('Erreur lors de la création de la marque');
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
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-bold mb-4">Create New Brand</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom de la marque *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Nike"
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
                placeholder="Ex: Nike Inc."
              />
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
                  placeholder="Ex: United States"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Année de fondation
                </label>
                <input
                  type="number"
                  value={formData.founded_year}
                  onChange={(e) => setFormData({...formData, founded_year: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: 1964"
                  min="1800"
                  max="2030"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Site web
              </label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData({...formData, website: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: https://www.nike.com"
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
                  placeholder="Ex: Nike Football, Swoosh"
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
                📸 Images de la marque
                <span className="text-xs text-gray-500 font-normal">(optionnel, max 5MB par image)</span>
              </h4>
              
              {/* Logo de la marque */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo de la marque
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
                  Images secondaires (évolution du logo, etc.)
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
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Création...' : 'Créer la marque'}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Football Brands</h1>
          <p className="text-gray-600">
            Collaborative database of football kit manufacturers and brands
          </p>
        </div>
        
        {user && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center"
          >
            <span className="mr-2">➕</span>
            Add Brand
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h3 className="font-semibold mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recherche
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Nom de la marque..."
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

          <div className="flex items-center">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.verified_only}
                onChange={(e) => setFilters({...filters, verified_only: e.target.checked})}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Marques vérifiées uniquement</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ search: '', country: '', verified_only: false })}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Réinitialiser les filtres
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{filteredBrands.length}</div>
          <div className="text-sm text-blue-700">Marques trouvées</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            {filteredBrands.filter(b => b.verified_level !== 'unverified').length}
          </div>
          <div className="text-sm text-green-700">Marques vérifiées</div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{countries.length}</div>
          <div className="text-sm text-purple-700">Pays représentés</div>
        </div>
      </div>

      {/* Brands Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredBrands.map(brand => (
          <BrandCard key={brand.id} brand={brand} />
        ))}
      </div>

      {filteredBrands.length === 0 && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">👕</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune marque trouvée</h3>
          <p className="text-gray-600 mb-4">
            Essayez de modifier vos filtres ou contribuez en ajoutant une nouvelle marque
          </p>
          {user && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Ajouter la première marque
            </button>
          )}
        </div>
      )}

      {/* Create Brand Modal */}
      {showCreateModal && <CreateBrandModal />}

      {/* Brand Detail Modal */}
      {selectedBrand && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedBrand.name}</h2>
                {selectedBrand.official_name && selectedBrand.official_name !== selectedBrand.name && (
                  <p className="text-gray-600">{selectedBrand.official_name}</p>
                )}
                <p className="text-blue-600 font-mono text-sm">{selectedBrand.topkit_reference}</p>
              </div>
              <div className="flex gap-2">
                {user && (
                  <button
                    onClick={() => {
                      setSelectedBrandForContribution(selectedBrand);
                      setShowContributionModal(true);
                    }}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                  >
                    ✏️ Améliorer cette fiche
                  </button>
                )}
                <button
                  onClick={() => setSelectedBrand(null)}
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
                  {selectedBrand.country && (
                    <div>
                      <span className="text-gray-600">Pays:</span>
                      <span className="ml-2">{selectedBrand.country}</span>
                    </div>
                  )}
                  {selectedBrand.founded_year && (
                    <div>
                      <span className="text-gray-600">Fondation:</span>
                      <span className="ml-2">{selectedBrand.founded_year}</span>
                    </div>
                  )}
                  {selectedBrand.website && (
                    <div>
                      <span className="text-gray-600">Site web:</span>
                      <a href={selectedBrand.website} target="_blank" rel="noopener noreferrer" className="ml-2 text-blue-600 hover:underline">
                        Visiter
                      </a>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-600">Statut:</span>
                    <span className={`ml-2 ${selectedBrand.verified_level !== 'unverified' ? 'text-green-600' : 'text-orange-600'}`}>
                      {selectedBrand.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
                    </span>
                  </div>
                </div>
              </div>

              {selectedBrand.common_names && selectedBrand.common_names.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Noms alternatifs</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedBrand.common_names.map((name, index) => (
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
                    <span className="text-gray-600">Maillots produits:</span>
                    <span className="ml-2 font-medium">{selectedBrand.jerseys_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Collectionneurs:</span>
                    <span className="ml-2 font-medium">{selectedBrand.collectors_count || 0}</span>
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
            setSelectedBrandForContribution(null);
          }}
          entity={selectedBrandForContribution}
          entityType="brand"
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

export default CollaborativeBrandsPage;