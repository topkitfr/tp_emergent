import React, { useState, useEffect } from 'react';
import ContributionModal from '../ContributionModal';

const CollaborativeBrandsPage = ({ user, API, brands, onDataUpdate }) => {
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
      className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-all cursor-pointer group"
      onClick={() => setSelectedBrand(brand)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center group-hover:bg-gray-200 transition-colors">
            <span className="text-xl">👕</span>
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600">
              {brand.name}
            </h3>
            {brand.official_name && brand.official_name !== brand.name && (
              <p className="text-sm text-gray-500">{brand.official_name}</p>
            )}
          </div>
        </div>
        
        {brand.verified_level !== 'unverified' && (
          <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
            ✓ Vérifié
          </div>
        )}
      </div>

      <div className="space-y-2 text-sm">
        {brand.country && (
          <div className="flex items-center text-gray-600">
            <span className="mr-2">🌍</span>
            <span>{brand.country}</span>
          </div>
        )}
        
        {brand.founded_year && (
          <div className="flex items-center text-gray-600">
            <span className="mr-2">📅</span>
            <span>Fondée en {brand.founded_year}</span>
          </div>
        )}

        {brand.common_names && brand.common_names.length > 0 && (
          <div className="flex items-start text-gray-600">
            <span className="mr-2">🏷️</span>
            <div className="flex flex-wrap gap-1">
              {brand.common_names.slice(0, 3).map((name, index) => (
                <span key={index} className="bg-gray-100 px-2 py-1 rounded text-xs">
                  {name}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <span className="text-blue-600 font-mono text-xs">{brand.topkit_reference}</span>
          <div className="text-xs text-gray-500">
            {brand.jerseys_count || 0} maillots
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

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!formData.name) {
        alert('Le nom de la marque est obligatoire');
        return;
      }
      handleCreateBrand({
        ...formData,
        founded_year: formData.founded_year ? parseInt(formData.founded_year) : null
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

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-bold mb-4">Créer une nouvelle marque</h3>
          
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Marques de maillots</h1>
          <p className="text-gray-600">
            Base de données collaborative des marques et fabricants de maillots de football
          </p>
        </div>
        
        {user && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center"
          >
            <span className="mr-2">➕</span>
            Ajouter une marque
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
              <button
                onClick={() => setSelectedBrand(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="text-2xl">×</span>
              </button>
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

    </div>
  );
};

export default CollaborativeBrandsPage;