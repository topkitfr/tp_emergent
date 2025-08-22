import React, { useState, useEffect } from 'react';

const PendingContributions = ({ entityId, entityType, onVoteSubmitted, user }) => {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [voting, setVoting] = useState({});

  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    if (entityId) {
      loadPendingContributions();
    }
  }, [entityId, entityType]);

  const loadPendingContributions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/contributions?entity_id=${entityId}&entity_type=${entityType}&status=pending`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setContributions(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des contributions:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitVote = async (contributionId, voteType) => {
    if (!user) return;

    setVoting(prev => ({ ...prev, [contributionId]: true }));

    try {
      const response = await fetch(`${API}/contributions/${contributionId}/vote`, {
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
        if (onVoteSubmitted) {
          onVoteSubmitted();
        }
      } else {
        console.error('Erreur lors du vote');
      }
    } catch (error) {
      console.error('Erreur lors du vote:', error);
    } finally {
      setVoting(prev => ({ ...prev, [contributionId]: false }));
    }
  };

  const formatChangeValue = (key, value) => {
    if (key === 'colors' && Array.isArray(value)) {
      return value.join(', ');
    }
    return value || 'Non spécifié';
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded mb-2"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (contributions.length === 0) {
    return null; // Ne pas afficher la section s'il n'y a pas de contributions
  }

  return (
    <div>
      <h3 className="font-semibold mb-3 flex items-center">
        🗳️ Contributions en attente de validation 
        <span className="ml-2 bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">
          {contributions.length}
        </span>
      </h3>

      <div className="space-y-3">
        {contributions.map((contribution) => (
          <div key={contribution.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h4 className="font-medium text-sm text-gray-900">{contribution.title}</h4>
                <p className="text-xs text-gray-600 mt-1">{contribution.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Par {contribution.contributor_name} • {new Date(contribution.created_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <div className="flex items-center space-x-1 text-xs">
                <span className="text-green-600">👍 {contribution.upvotes || 0}</span>
                <span className="text-red-600">👎 {contribution.downvotes || 0}</span>
              </div>
            </div>

            {/* Affichage des changements proposés */}
            {contribution.proposed_data && Object.keys(contribution.proposed_data).length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-gray-700 mb-2">Changements proposés:</p>
                <div className="space-y-1">
                  {Object.entries(contribution.proposed_data).map(([key, value]) => (
                    <div key={key} className="flex text-xs">
                      <span className="text-gray-600 w-24 capitalize">{key.replace('_', ' ')}:</span>
                      <span className="text-gray-900 font-medium">{formatChangeValue(key, value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Affichage des images */}
            {contribution.images && Object.keys(contribution.images).length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-gray-700 mb-2">Images proposées:</p>
                <div className="flex space-x-2">
                  {Object.entries(contribution.images).map(([imageKey, imageData]) => (
                    <div key={imageKey} className="text-center">
                      <img 
                        src={Array.isArray(imageData) ? imageData[0] : imageData}
                        alt={imageKey}
                        className="w-16 h-16 object-cover rounded border"
                      />
                      <p className="text-xs text-gray-500 mt-1 capitalize">{imageKey}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Boutons de vote */}
            {user && (
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
          </div>
        ))}
      </div>
    </div>
  );
};

export default PendingContributions;