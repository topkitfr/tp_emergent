import React, { useState, useEffect } from 'react';

const CollaborativeContributePage = ({ teams, brands, competitions, players, masterJerseys, currentUser }) => {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');
  const [selectedContribution, setSelectedContribution] = useState(null);
  const [showContributionModal, setShowContributionModal] = useState(false);
  const [userVotes, setUserVotes] = useState({});

  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadContributions();
  }, [filter]);

  const loadContributions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const queryParams = filter !== 'all' ? `?status=${filter}` : '';
      
      const response = await fetch(`${API}/api/contributions${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setContributions(data);
        
        // Extraire les votes de l'utilisateur
        const votes = {};
        data.forEach(contrib => {
          if (contrib.user_vote) {
            votes[contrib.id] = contrib.user_vote;
          }
        });
        setUserVotes(votes);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des contributions:', error);
    } finally {
      setLoading(false);
    }
  };

  const vote = async (contributionId, voteType) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API}/api/contributions/${contributionId}/vote`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          vote_type: voteType,
          comment: null
        })
      });

      if (response.ok) {
        // Recharger les contributions pour avoir les compteurs mis à jour
        loadContributions();
        
        // Mettre à jour le vote local
        setUserVotes(prev => ({
          ...prev,
          [contributionId]: voteType
        }));
      }
    } catch (error) {
      console.error('Erreur lors du vote:', error);
    }
  };

  const getEntityDisplayName = (contribution) => {
    const entityData = contribution.changes_summary?.[0];
    if (!entityData) return contribution.entity_reference;
    
    // Essayer de trouver le nom dans les changements ou utiliser la référence
    const nameField = entityData.field === 'name' ? entityData.to : entityData.from;
    return nameField || contribution.entity_reference;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'approved': return 'text-green-600 bg-green-100';
      case 'auto_approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return 'En attente';
      case 'approved': return 'Approuvé';
      case 'auto_approved': return 'Auto-approuvé';
      case 'rejected': return 'Rejeté';
      default: return status;
    }
  };

  const formatChangeValue = (value) => {
    if (value === null || value === undefined) return 'Non défini';
    if (Array.isArray(value)) return value.join(', ');
    if (typeof value === 'boolean') return value ? 'Oui' : 'Non';
    return String(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🤝 Contributions Collaboratives
          </h1>
          <p className="text-gray-600 mb-4">
            Participez à l'amélioration de la base de données TopKit en votant sur les contributions de la communauté.
          </p>
          
          {/* Filtres */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('pending')}
              className={`px-4 py-2 rounded-lg font-medium ${
                filter === 'pending' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              En attente ({contributions.filter(c => c.status === 'pending').length})
            </button>
            <button
              onClick={() => setFilter('approved')}
              className={`px-4 py-2 rounded-lg font-medium ${
                filter === 'approved' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Approuvées
            </button>
            <button
              onClick={() => setFilter('rejected')}
              className={`px-4 py-2 rounded-lg font-medium ${
                filter === 'rejected' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Rejetées
            </button>
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium ${
                filter === 'all' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Toutes
            </button>
          </div>
        </div>

        {/* Liste des contributions */}
        {contributions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="text-gray-400 text-6xl mb-4">📝</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Aucune contribution trouvée
            </h3>
            <p className="text-gray-600">
              {filter === 'pending' 
                ? "Il n'y a actuellement aucune contribution en attente de validation."
                : "Aucune contribution ne correspond à vos critères de filtrage."}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {contributions.map((contribution) => (
              <div key={contribution.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                
                {/* En-tête de la contribution */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {contribution.title}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contribution.status)}`}>
                        {getStatusText(contribution.status)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>
                        <strong>{contribution.entity_type}</strong>: {getEntityDisplayName(contribution)}
                      </span>
                      <span>•</span>
                      <span>Par <strong>{contribution.contributor.username}</strong></span>
                      <span>•</span>
                      <span>{new Date(contribution.created_at).toLocaleDateString('fr-FR')}</span>
                      <span>•</span>
                      <span className="text-blue-600 font-medium">{contribution.topkit_reference}</span>
                    </div>
                  </div>
                </div>

                {/* Description */}
                {contribution.description && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">{contribution.description}</p>
                  </div>
                )}

                {/* Changements proposés */}
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Changements proposés :</h4>
                  <div className="space-y-2">
                    {contribution.changes_summary.map((change, index) => (
                      <div key={index} className="flex items-center gap-4 text-sm p-2 bg-blue-50 rounded border-l-4 border-blue-400">
                        <span className="font-medium text-blue-900 min-w-0 flex-shrink-0">
                          {change.field}:
                        </span>
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          <span className="text-red-600 truncate">
                            {formatChangeValue(change.from)}
                          </span>
                          <span className="text-gray-400">→</span>
                          <span className="text-green-600 truncate font-medium">
                            {formatChangeValue(change.to)}
                          </span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          change.type === 'add' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                        }`}>
                          {change.type === 'add' ? 'Ajout' : 'Modification'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Section de vote */}
                {contribution.status === 'pending' && currentUser && contribution.contributor.id !== currentUser.id && (
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-gray-600">Votre avis sur cette contribution :</span>
                      
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => vote(contribution.id, 'upvote')}
                          className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                            userVotes[contribution.id] === 'upvote'
                              ? 'bg-green-100 text-green-700 border border-green-300'
                              : 'bg-gray-100 text-gray-600 hover:bg-green-50 hover:text-green-600'
                          }`}
                        >
                          <span>👍</span>
                          <span>Approuver</span>
                        </button>
                        
                        <button
                          onClick={() => vote(contribution.id, 'downvote')}
                          className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                            userVotes[contribution.id] === 'downvote'
                              ? 'bg-red-100 text-red-700 border border-red-300'
                              : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-600'
                          }`}
                        >
                          <span>👎</span>
                          <span>Rejeter</span>
                        </button>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <span className="text-green-600">👍 {contribution.upvotes}</span>
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="text-red-600">👎 {contribution.downvotes}</span>
                      </span>
                      <span className="font-medium text-blue-600">
                        Score: {contribution.vote_score > 0 ? '+' : ''}{contribution.vote_score}
                      </span>
                    </div>
                  </div>
                )}

                {/* Informations de vote pour les contributions non-pending */}
                {contribution.status !== 'pending' && (
                  <div className="flex items-center justify-end gap-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
                    <span>👍 {contribution.upvotes}</span>
                    <span>👎 {contribution.downvotes}</span>
                    <span className="font-medium">Score final: {contribution.vote_score > 0 ? '+' : ''}{contribution.vote_score}</span>
                  </div>
                )}

                {/* Message si c'est la contribution de l'utilisateur */}
                {currentUser && contribution.contributor.id === currentUser.id && (
                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-sm text-blue-600">
                      <span>ℹ️</span>
                      <span>Votre contribution</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Guide pour les nouveaux utilisateurs */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            💡 Comment ça marche ?
          </h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <h4 className="font-medium mb-2">Voter sur les contributions :</h4>
              <ul className="space-y-1">
                <li>• 👍 <strong>Approuver</strong> : La contribution améliore la qualité des données</li>
                <li>• 👎 <strong>Rejeter</strong> : La contribution contient des erreurs ou est inappropriée</li>
                <li>• Score ≥ 3 : Approbation automatique</li>
                <li>• Score ≤ -2 : Rejet automatique</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Faire une contribution :</h4>
              <ul className="space-y-1">
                <li>• Allez sur la fiche d'une équipe, compétition, etc.</li>
                <li>• Cliquez sur "✏️ Améliorer cette fiche"</li>
                <li>• Proposez vos améliorations avec justification</li>
                <li>• La communauté votera sur votre contribution</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollaborativeContributePage;