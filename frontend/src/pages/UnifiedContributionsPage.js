import React, { useState, useEffect } from 'react';

const UnifiedContributionsPage = ({ user, API }) => {
  const [activeTab, setActiveTab] = useState('all');
  const [contributions, setContributions] = useState([]);
  const [myContributions, setMyContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (user) {
      loadContributions();
    }
  }, [user, activeTab]);

  const loadContributions = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      if (activeTab === 'all') {
        // Load all community contributions
        const response = await fetch(`${API}/api/contributions/community`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setContributions(data);
        }
      } else {
        // Load user's own contributions
        const response = await fetch(`${API}/api/contributions/my-contributions`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setMyContributions(data);
        }
      }
    } catch (error) {
      console.error('Error loading contributions:', error);
    }
    setLoading(false);
  };

  const handleVote = async (contributionId, voteType) => {
    try {
      const response = await fetch(`${API}/api/contributions/${contributionId}/vote`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vote_type: voteType })
      });

      if (response.ok) {
        // Reload contributions after voting
        loadContributions();
      }
    } catch (error) {
      console.error('Error voting on contribution:', error);
    }
  };

  const filteredData = activeTab === 'all' 
    ? contributions.filter(contrib => 
        contrib.entity_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contrib.user_name?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : myContributions.filter(contrib => 
        contrib.entity_name?.toLowerCase().includes(searchQuery.toLowerCase())
      );

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔒</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connexion requise</h3>
          <p className="text-gray-600">
            Vous devez être connecté pour accéder aux contributions
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Chargement des contributions...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Contributions</h1>
        <p className="text-gray-600">
          Participez à l'amélioration collaborative de TopKit
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-gray-200 mb-8">
        <div className="border-b border-gray-200">
          <div className="flex space-x-0">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                activeTab === 'all'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">🌍</span>
              Toutes les contributions
            </button>
            
            <button
              onClick={() => setActiveTab('mine')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                activeTab === 'mine'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'  
              }`}
            >
              <span className="mr-2">📝</span>
              Mes contributions
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="p-6">
          <div className="relative">
            <input
              type="text"
              placeholder={activeTab === 'all' ? "Rechercher par entité ou contributeur..." : "Rechercher dans mes contributions..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      {filteredData.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">
            {activeTab === 'all' ? '🌍' : '📝'}
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {activeTab === 'all' ? 'Aucune contribution communautaire' : 'Aucune contribution personnelle'}
          </h3>
          <p className="text-gray-600">
            {activeTab === 'all' 
              ? 'Il n\'y a pas encore de contributions de la communauté.'
              : 'Vous n\'avez pas encore soumis de contributions.'
            }
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredData.map((contribution) => (
            <div
              key={contribution.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  {/* Contribution Header */}
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="w-8 h-8 rounded-full overflow-hidden">
                      {contribution.user_profile_picture ? (
                        <img 
                          src={`${API}/${contribution.user_profile_picture}`}
                          alt="Profile"
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                          <span className="text-xs font-bold text-white">
                            {contribution.user_name?.charAt(0).toUpperCase() || 'U'}
                          </span>
                        </div>
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{contribution.entity_name}</h3>
                      <p className="text-sm text-gray-600">
                        par {contribution.user_name} • {new Date(contribution.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Contribution Details */}
                  <div className="mb-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      contribution.entity_type === 'team' ? 'bg-blue-100 text-blue-800' :
                      contribution.entity_type === 'brand' ? 'bg-purple-100 text-purple-800' :
                      contribution.entity_type === 'player' ? 'bg-green-100 text-green-800' :
                      contribution.entity_type === 'competition' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {contribution.entity_type === 'team' ? '⚽ Équipe' :
                       contribution.entity_type === 'brand' ? '👕 Marque' :
                       contribution.entity_type === 'player' ? '🏃 Joueur' :
                       contribution.entity_type === 'competition' ? '🏆 Compétition' :
                       'Maillot'}
                    </span>
                    
                    <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      contribution.status === 'pending' ? 'bg-orange-100 text-orange-800' :
                      contribution.status === 'approved' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {contribution.status === 'pending' ? '⏳ En attente' :
                       contribution.status === 'approved' ? '✅ Approuvée' :
                       '❌ Rejetée'}
                    </span>
                  </div>

                  {/* Changes Summary */}
                  {contribution.changes_summary && (
                    <div className="bg-gray-50 rounded-lg p-3 mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Modifications proposées :</h4>
                      <p className="text-sm text-gray-700">{contribution.changes_summary}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Voting Section (only for community tab and pending contributions) */}
              {activeTab === 'all' && contribution.status === 'pending' && (
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-4">
                    <div className="text-sm text-gray-600">
                      Score: <span className="font-medium">{contribution.vote_score || 0}</span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Votes: 👍 {contribution.upvotes || 0} • 👎 {contribution.downvotes || 0}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleVote(contribution.id, 'upvote')}
                      className="flex items-center space-x-1 bg-green-100 hover:bg-green-200 text-green-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      <span>👍</span>
                      <span>Approuver</span>
                    </button>
                    <button
                      onClick={() => handleVote(contribution.id, 'downvote')}
                      className="flex items-center space-x-1 bg-red-100 hover:bg-red-200 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      <span>👎</span>
                      <span>Rejeter</span>
                    </button>
                  </div>
                </div>
              )}

              {/* My Contributions Info */}
              {activeTab === 'mine' && (
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div>
                      Score actuel: <span className="font-medium">{contribution.vote_score || 0}</span>
                    </div>
                    <div>
                      Votes: 👍 {contribution.upvotes || 0} • 👎 {contribution.downvotes || 0}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UnifiedContributionsPage;