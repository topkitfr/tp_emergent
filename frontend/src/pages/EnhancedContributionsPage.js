import React, { useState, useEffect } from 'react';
import ContributionDetailModal from '../components/ContributionDetailModal';

const EnhancedContributionsPage = ({ user, API }) => {
  const [pendingContributions, setPendingContributions] = useState([]);
  const [recentContributions, setRecentContributions] = useState([]);
  const [filters, setFilters] = useState({
    entity_type: '',
    status: 'all'
  });
  const [loading, setLoading] = useState(false);
  const [voting, setVoting] = useState({});
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' | 'recent' | 'my'
  const [selectedContribution, setSelectedContribution] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Load pending contributions (for voting)
  const loadPendingContributions = async () => {
    setLoading(true);
    try {
      let url = `${API}/api/contributions?status=pending`;
      if (filters.entity_type) {
        url += `&entity_type=${filters.entity_type}`;
      }
      
      const response = await fetch(url, {
        headers: user ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {}
      });

      if (response.ok) {
        const data = await response.json();
        setPendingContributions(data);
      }
    } catch (error) {
      console.error('Error loading pending contributions:', error);
    }
    setLoading(false);
  };

  // Load recent contributions (for "Dernières contributions 🔥")
  const loadRecentContributions = async () => {
    try {
      let url = `${API}/api/contributions?status=approved&limit=20`;
      if (filters.entity_type) {
        url += `&entity_type=${filters.entity_type}`;
      }
      
      const response = await fetch(url, {
        headers: user ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {}
      });

      if (response.ok) {
        const data = await response.json();
        setRecentContributions(data);
      }
    } catch (error) {
      console.error('Error loading recent contributions:', error);
    }
  };

  // Vote on contribution
  const submitVote = async (contributionId, voteType) => {
    if (!user) return;

    setVoting(prev => ({ ...prev, [contributionId]: true }));

    try {
      const response = await fetch(`${API}/api/contributions/${contributionId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          vote_type: voteType,
          voter_id: user.id
        })
      });

      if (response.ok) {
        // Refresh contributions after voting
        await loadPendingContributions();
        await loadRecentContributions();
      } else {
        console.error('Erreur lors du vote');
      }
    } catch (error) {
      console.error('Erreur lors du vote:', error);
    } finally {
      setVoting(prev => ({ ...prev, [contributionId]: false }));
    }
  };

  useEffect(() => {
    loadPendingContributions();
    loadRecentContributions();
  }, [user, filters]);

  // Helper functions
  const getEntityTypeLabel = (type) => {
    const labels = {
      'team': 'Équipe',
      'brand': 'Marque', 
      'player': 'Joueur',
      'competition': 'Compétition',
      'master_jersey': 'Master Jersey',
      'jersey_release': 'Jersey Release'
    };
    return labels[type] || type;
  };

  const formatChangeValue = (key, value) => {
    if (key === 'colors' && Array.isArray(value)) {
      return value.join(', ');
    }
    return value || 'Non spécifié';
  };

  const getStatusInfo = (status) => {
    const statusInfo = {
      'pending': { label: 'En attente', bgColor: 'bg-orange-100', textColor: 'text-orange-800' },
      'approved': { label: 'Approuvé', bgColor: 'bg-green-100', textColor: 'text-green-800' },
      'rejected': { label: 'Rejeté', bgColor: 'bg-red-100', textColor: 'text-red-800' }
    };
    return statusInfo[status] || { label: status, bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
  };

  // Contribution Card Component
  const ContributionCard = ({ contribution, showVoting = false, isRecent = false }) => {
    const statusInfo = getStatusInfo(contribution.status);
    
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all ${isRecent ? 'border-l-4 border-l-green-400' : ''}`}>
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <h4 className="font-medium text-sm text-gray-900 mb-1">
              {contribution.title || `${getEntityTypeLabel(contribution.entity_type)} - Modification`}
            </h4>
            <p className="text-xs text-gray-600 mb-2">{contribution.description}</p>
            <p className="text-xs text-gray-500">
              Par {contribution.contributor_name || 'Anonyme'} • {new Date(contribution.created_at).toLocaleDateString('fr-FR')}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.textColor}`}>
              {statusInfo.label}
            </div>
            {!isRecent && (
              <div className="flex items-center space-x-1 text-xs">
                <span className="text-green-600">👍 {contribution.upvotes || 0}</span>
                <span className="text-red-600">👎 {contribution.downvotes || 0}</span>
              </div>
            )}
          </div>
        </div>

        {/* Affichage des changements proposés */}
        {contribution.proposed_data && Object.keys(contribution.proposed_data).length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-medium text-gray-700 mb-2">Changements proposés:</p>
            <div className="space-y-1">
              {Object.entries(contribution.proposed_data).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex text-xs">
                  <span className="text-gray-600 w-20 capitalize">{key.replace('_', ' ')}:</span>
                  <span className="text-gray-900 font-medium truncate">{formatChangeValue(key, value)}</span>
                </div>
              ))}
              {Object.keys(contribution.proposed_data).length > 3 && (
                <p className="text-xs text-gray-500">+{Object.keys(contribution.proposed_data).length - 3} autres changements</p>
              )}
            </div>
          </div>
        )}

        {/* Affichage des images */}
        {contribution.images && Object.keys(contribution.images).length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-medium text-gray-700 mb-2">Images proposées:</p>
            <div className="flex space-x-2">
              {Object.entries(contribution.images).slice(0, 3).map(([imageKey, imageData]) => (
                <div key={imageKey} className="text-center">
                  <img 
                    src={Array.isArray(imageData) ? imageData[0] : imageData}
                    alt={imageKey}
                    className="w-12 h-12 object-cover rounded border"
                  />
                  <p className="text-xs text-gray-500 mt-1 capitalize">{imageKey}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Boutons de vote */}
        {showVoting && user && contribution.status === 'pending' && (
          <div className="flex space-x-2 pt-2 border-t">
            <button
              onClick={() => submitVote(contribution.id, 'upvote')}
              disabled={voting[contribution.id]}
              className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 px-3 py-2 rounded text-xs font-medium disabled:opacity-50 transition-colors"
            >
              {voting[contribution.id] ? '...' : '👍 Approuver'}
            </button>
            <button
              onClick={() => submitVote(contribution.id, 'downvote')}
              disabled={voting[contribution.id]}
              className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 px-3 py-2 rounded text-xs font-medium disabled:opacity-50 transition-colors"
            >
              {voting[contribution.id] ? '...' : '👎 Rejeter'}
            </button>
          </div>
        )}

        {/* Pour les contributions récentes, afficher un bouton d'action rapide */}
        {isRecent && user && (
          <div className="pt-2 border-t">
            <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
              Voir les détails →
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">🗳️ Contributions Communautaires</h1>
        <p className="text-gray-600">Participez à l'amélioration collaborative de TopKit</p>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type d'entité</label>
            <select
              value={filters.entity_type}
              onChange={(e) => setFilters(prev => ({ ...prev, entity_type: e.target.value }))}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les types</option>
              <option value="team">Équipes</option>
              <option value="brand">Marques</option>
              <option value="player">Joueurs</option>
              <option value="competition">Compétitions</option>
              <option value="master_jersey">Master Jerseys</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('pending')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'pending'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🗳️ En attente de vote ({pendingContributions.length})
            </button>
            <button
              onClick={() => setActiveTab('recent')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'recent'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🔥 Dernières contributions ({recentContributions.length})
            </button>
            {user && (
              <button
                onClick={() => setActiveTab('my')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'my'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📝 Mes contributions
              </button>
            )}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4">
        
        {/* Pending Contributions Tab */}
        {activeTab === 'pending' && (
          <div>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse bg-gray-200 h-32 rounded-lg"></div>
                ))}
              </div>
            ) : pendingContributions.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {pendingContributions.map(contribution => (
                  <ContributionCard 
                    key={contribution.id} 
                    contribution={contribution} 
                    showVoting={true}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <p className="text-gray-500 mb-2">🎉 Aucune contribution en attente</p>
                <p className="text-sm text-gray-400">Toutes les contributions ont été traitées !</p>
              </div>
            )}
          </div>
        )}

        {/* Recent Contributions Tab */}
        {activeTab === 'recent' && (
          <div>
            {recentContributions.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {recentContributions.map(contribution => (
                  <ContributionCard 
                    key={contribution.id} 
                    contribution={contribution} 
                    isRecent={true}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <p className="text-gray-500 mb-2">📭 Aucune contribution récente</p>
                <p className="text-sm text-gray-400">Les contributions approuvées apparaîtront ici</p>
              </div>
            )}
          </div>
        )}

        {/* My Contributions Tab */}
        {activeTab === 'my' && user && (
          <div>
            <p className="text-center text-gray-500 py-8">
              Cette section affichera vos contributions personnelles
            </p>
          </div>
        )}

      </div>
    </div>
  );
};

export default EnhancedContributionsPage;