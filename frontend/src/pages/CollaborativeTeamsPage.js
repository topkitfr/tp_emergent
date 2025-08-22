import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import ContributionModal from '../ContributionModal';
import PendingContributions from '../PendingContributions';

const CollaborativeTeamsPage = ({ user, API, teams, onDataUpdate }) => {
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

    setLoading(true);
    try {
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
        alert(`✅ Équipe "${newTeam.name}" créée avec succès ! (${newTeam.topkit_reference})`);
        setShowCreateModal(false);
        onDataUpdate(); // Refresh data
      } else {
        const error = await response.json();
        alert(`❌ Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating team:', error);
      alert('❌ Erreur lors de la création de l\'équipe');
    }
    setLoading(false);
  };

  const TeamCard = ({ team }) => {
    const handleTeamClick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setSelectedTeam(team);
    };

    return (
      <div 
        className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
        onClick={handleTeamClick}
      >
        {/* Image section - same structure as Master Jersey */}
        <div className="aspect-square bg-gray-100 flex items-center justify-center relative group-hover:bg-gray-200 transition-colors">
          {team.logo_url ? (
            <img 
              src={team.logo_url.startsWith('data:') || team.logo_url.startsWith('http') ? team.logo_url : `${API}/${team.logo_url}`}
              alt={`${team.name} logo`}
              className="w-full h-full object-contain p-4"
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
                <span>Fondée en {team.founded_year}</span>
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
              <span>{team.jerseys_count || 0} maillots</span>
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

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!formData.name || !formData.country) {
        alert('Nom et pays sont obligatoires');
        return;
      }
      handleCreateTeam({
        ...formData,
        founded_year: formData.founded_year ? parseInt(formData.founded_year) : null
      });
    };

    const addColor = () => {
      if (newColor && !formData.colors.includes(newColor)) {
        setFormData({
          ...formData,
          colors: [...formData.colors, newColor]
        });
        setNewColor('');
      }
    };

    const removeColor = (colorToRemove) => {
      setFormData({
        ...formData,
        colors: formData.colors.filter(color => color !== colorToRemove)
      });
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-bold mb-4">Créer une nouvelle équipe</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom de l'équipe *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: FC Barcelona"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom court
              </label>
              <input
                type="text"
                value={formData.short_name}
                onChange={(e) => setFormData({...formData, short_name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: FCB"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pays *
                </label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({...formData, country: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Spain"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ville
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Barcelona"
                />
              </div>
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
                placeholder="Ex: 1899"
                min="1800"
                max="2030"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Couleurs de l'équipe
              </label>
              <div className="flex space-x-2 mb-2">
                <input
                  type="text"
                  value={newColor}
                  onChange={(e) => setNewColor(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: blue, red, white"
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
                {loading ? 'Création...' : 'Créer l\'équipe'}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Équipes de football</h1>
          <p className="text-gray-600">
            Base de données collaborative des équipes de football du monde entier
          </p>
        </div>
        
        {user && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center"
          >
            <span className="mr-2">➕</span>
            Ajouter une équipe
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
              placeholder="Nom de l'équipe..."
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
              <span className="text-sm text-gray-700">Équipes vérifiées uniquement</span>
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
          <div className="text-2xl font-bold text-blue-600">{filteredTeams.length}</div>
          <div className="text-sm text-blue-700">Équipes trouvées</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            {filteredTeams.filter(t => t.verified_level !== 'unverified').length}
          </div>
          <div className="text-sm text-green-700">Équipes vérifiées</div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{countries.length}</div>
          <div className="text-sm text-purple-700">Pays représentés</div>
        </div>
      </div>

      {/* Teams Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTeams.map(team => (
          <TeamCard key={team.id} team={team} />
        ))}
      </div>

      {filteredTeams.length === 0 && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">⚽</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune équipe trouvée</h3>
          <p className="text-gray-600 mb-4">
            Essayez de modifier vos filtres ou contribuez en ajoutant une nouvelle équipe
          </p>
          {user && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Ajouter la première équipe
            </button>
          )}
        </div>
      )}

      {/* Create Team Modal */}
      {showCreateModal && <CreateTeamModal />}

      {/* Team Detail Modal */}
      {selectedTeam && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedTeam.name}</h2>
                {selectedTeam.short_name && (
                  <p className="text-gray-600">{selectedTeam.short_name}</p>
                )}
                <p className="text-blue-600 font-mono text-sm">{selectedTeam.topkit_reference}</p>
              </div>
              <div className="flex gap-2">
                {user && (
                  <button
                    onClick={() => {
                      setSelectedTeamForContribution(selectedTeam);
                      setShowContributionModal(true);
                    }}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                  >
                    ✏️ Améliorer cette fiche
                  </button>
                )}
                <button
                  onClick={() => setSelectedTeam(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Informations générales</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Pays:</span>
                    <span className="ml-2 font-medium text-gray-900">{selectedTeam.country || 'Non spécifié'}</span>
                  </div>
                  {selectedTeam.city && (
                    <div>
                      <span className="text-gray-600">Ville:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedTeam.city}</span>
                    </div>
                  )}
                  {selectedTeam.founded_year && (
                    <div>
                      <span className="text-gray-600">Fondation:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedTeam.founded_year}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-600">Statut:</span>
                    <span className={`ml-2 ${selectedTeam.verified_level !== 'unverified' ? 'text-green-600' : 'text-orange-600'}`}>
                      {selectedTeam.verified_level !== 'unverified' ? '✓ Vérifié' : 'En attente de vérification'}
                    </span>
                  </div>
                </div>
              </div>

              {(selectedTeam.colors || selectedTeam.primary_colors) && (selectedTeam.colors?.length > 0 || selectedTeam.primary_colors?.length > 0) && (
                <div>
                  <h3 className="font-semibold mb-2 text-gray-900">Couleurs</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedTeam.colors || selectedTeam.primary_colors || []).map((color, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div
                          className="w-6 h-6 rounded-full border border-gray-300"
                          style={{ backgroundColor: color.toLowerCase() }}
                        ></div>
                        <span className="text-sm text-gray-600 capitalize">{color}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="font-semibold mb-2">Statistiques</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Maillots référencés:</span>
                    <span className="ml-2 font-medium">{selectedTeam.master_jerseys_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Collectionneurs:</span>
                    <span className="ml-2 font-medium">{selectedTeam.total_collectors || 0}</span>
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
            setSelectedTeamForContribution(null);
          }}
          entity={selectedTeamForContribution}
          entityType="team"
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

export default CollaborativeTeamsPage;