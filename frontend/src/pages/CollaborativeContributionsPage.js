import React, { useState, useEffect } from 'react';

const CollaborativeContributionsPage = ({ user, API }) => {
  const [contributions, setContributions] = useState([]);
  const [filters, setFilters] = useState({
    entity_type: '',
    status: '',
    contribution_type: ''
  });
  const [loading, setLoading] = useState(false);

  // Load contributions
  const loadContributions = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        contributor_id: user.id,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v))
      });
      
      const response = await fetch(`${API}/api/contributions?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContributions(data);
      }
    } catch (error) {
      console.error('Error loading contributions:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadContributions();
  }, [user, filters]);

  // Get entity type label
  const getEntityTypeLabel = (type) => {
    const labels = {
      'team': 'Équipe',
      'brand': 'Marque',
      'player': 'Joueur',
      'competition': 'Compétition',
      'master_jersey': 'Master Jersey',
      'jersey_release': 'Version Jersey'
    };
    return labels[type] || type;
  };

  // Get contribution type label
  const getContributionTypeLabel = (type) => {
    const labels = {
      'create': 'Création',
      'update': 'Modification',
      'merge': 'Fusion',
      'delete': 'Suppression'
    };
    return labels[type] || type;
  };

  // Get status label and color
  const getStatusInfo = (status) => {
    const statusInfo = {
      'pending': { label: 'En attente', color: 'orange', bgColor: 'bg-orange-100', textColor: 'text-orange-800' },
      'approved': { label: 'Approuvé', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-800' },
      'rejected': { label: 'Rejeté', color: 'red', bgColor: 'bg-red-100', textColor: 'text-red-800' },
      'needs_review': { label: 'Révision requise', color: 'blue', bgColor: 'bg-blue-100', textColor: 'text-blue-800' }
    };
    return statusInfo[status] || { label: status, color: 'gray', bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
  };

  const ContributionCard = ({ contribution }) => {
    const statusInfo = getStatusInfo(contribution.status);
    
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">
              {getEntityTypeLabel(contribution.entity_type)} - {getContributionTypeLabel(contribution.contribution_type)}
            </h3>
            <p className="text-sm text-gray-600">{contribution.description}</p>
          </div>
          
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.textColor}`}>
            {statusInfo.label}
          </div>
        </div>

        {/* Proposed Changes Preview */}
        {contribution.proposed_changes && Object.keys(contribution.proposed_changes).length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Modifications proposées</h4>
            <div className="bg-gray-50 rounded p-3 text-sm">
              {Object.entries(contribution.proposed_changes).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex justify-between py-1">
                  <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                  <span className="font-medium text-gray-900 truncate ml-2">
                    {typeof value === 'string' ? value : JSON.stringify(value)}
                  </span>
                </div>
              ))}
              {Object.keys(contribution.proposed_changes).length > 3 && (
                <div className="text-xs text-gray-500 mt-2">
                  +{Object.keys(contribution.proposed_changes).length - 3} autres modifications...
                </div>
              )}
            </div>
          </div>
        )}

        {/* Evidence URLs */}
        {contribution.evidence_urls && contribution.evidence_urls.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Preuves fournies</h4>
            <div className="flex flex-wrap gap-2">
              {contribution.evidence_urls.map((url, index) => (
                <a
                  key={index}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-700 text-xs bg-blue-50 px-2 py-1 rounded"
                >
                  📎 Preuve {index + 1}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Voting */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <span className="text-green-600">👍</span>
              <span className="text-gray-600">{contribution.upvotes || 0}</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-red-600">👎</span>
              <span className="text-gray-600">{contribution.downvotes || 0}</span>
            </div>
            <div className="text-gray-500">
              {contribution.total_votes || 0} vote{(contribution.total_votes || 0) !== 1 ? 's' : ''}
            </div>
          </div>
          
          <div className="text-xs text-gray-500">
            {new Date(contribution.created_at).toLocaleDateString('fr-FR')}
          </div>
        </div>

        {/* Review Notes */}
        {contribution.review_notes && (
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <h4 className="text-sm font-medium text-gray-700 mb-1">Notes de révision</h4>
            <p className="text-sm text-gray-600">{contribution.review_notes}</p>
          </div>
        )}
      </div>
    );
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔒</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connexion requise</h3>
          <p className="text-gray-600">
            Vous devez être connecté pour voir vos contributions
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mes Contributions</h1>
        <p className="text-gray-600">
          Suivez l'état de vos contributions à la base de données collaborative TopKit
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{contributions.length}</div>
          <div className="text-sm text-blue-700">Contributions totales</div>
        </div>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">
            {contributions.filter(c => c.status === 'pending').length}
          </div>
          <div className="text-sm text-orange-700">En attente</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            {contributions.filter(c => c.status === 'approved').length}
          </div>
          <div className="text-sm text-green-700">Approuvées</div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-red-600">
            {contributions.filter(c => c.status === 'rejected').length}
          </div>
          <div className="text-sm text-red-700">Rejetées</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h3 className="font-semibold mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type d'entité
            </label>
            <select
              value={filters.entity_type}
              onChange={(e) => setFilters({...filters, entity_type: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les entités</option>
              <option value="team">Équipes</option>
              <option value="brand">Marques</option>
              <option value="player">Joueurs</option>
              <option value="competition">Compétitions</option>
              <option value="master_jersey">Master Jerseys</option>
              <option value="jersey_release">Versions Jersey</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Statut
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les statuts</option>
              <option value="pending">En attente</option>
              <option value="approved">Approuvé</option>
              <option value="rejected">Rejeté</option>
              <option value="needs_review">Révision requise</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type de contribution
            </label>
            <select
              value={filters.contribution_type}
              onChange={(e) => setFilters({...filters, contribution_type: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les types</option>
              <option value="create">Création</option>
              <option value="update">Modification</option>
              <option value="merge">Fusion</option>
              <option value="delete">Suppression</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ entity_type: '', status: '', contribution_type: '' })}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Réinitialiser les filtres
            </button>
          </div>
        </div>
      </div>

      {/* Contributions List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Chargement des contributions...</span>
        </div>
      ) : contributions.length > 0 ? (
        <div className="space-y-6">
          {contributions.map(contribution => (
            <ContributionCard key={contribution.id} contribution={contribution} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📝</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune contribution trouvée</h3>
          <p className="text-gray-600 mb-4">
            {Object.values(filters).some(v => v) 
              ? "Aucune contribution ne correspond à vos filtres."
              : "Vous n'avez pas encore fait de contributions à la base de données collaborative."
            }
          </p>
          <p className="text-sm text-gray-500">
            Commencez en ajoutant une nouvelle équipe, marque, joueur ou maillot !
          </p>
        </div>
      )}

      {/* How to Contribute Section */}
      <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Comment contribuer ?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div className="text-center">
            <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl">⚽</span>
            </div>
            <h3 className="font-semibold mb-2">Équipes</h3>
            <p className="text-sm text-gray-600">
              Ajoutez de nouvelles équipes de football avec leurs informations détaillées
            </p>
          </div>

          <div className="text-center">
            <div className="bg-gray-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl">👕</span>
            </div>
            <h3 className="font-semibold mb-2">Marques</h3>
            <p className="text-sm text-gray-600">
              Documentez les fabricants et marques de maillots de football
            </p>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl">👤</span>
            </div>
            <h3 className="font-semibold mb-2">Joueurs</h3>
            <p className="text-sm text-gray-600">
              Ajoutez des joueurs et l'historique des maillots qu'ils ont portés
            </p>
          </div>

          <div className="text-center">
            <div className="bg-yellow-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl">🏆</span>
            </div>
            <h3 className="font-semibold mb-2">Maillots</h3>
            <p className="text-sm text-gray-600">
              Créez des Master Jerseys avec tous les détails de design
            </p>
          </div>

        </div>

        <div className="text-center mt-6">
          <p className="text-sm text-gray-600 mb-4">
            Toutes vos contributions sont vérifiées par la communauté pour assurer la qualité des données.
          </p>
        </div>
      </div>

    </div>
  );
};

export default CollaborativeContributionsPage;