import React, { useState, useEffect } from 'react';
import ContributionDetailModal from '../components/ContributionDetailModal';

const UnifiedContributionsPage = ({ user, API }) => {
  const [activeTab, setActiveTab] = useState('all');
  const [contributions, setContributions] = useState([]);
  const [myContributions, setMyContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedContribution, setSelectedContribution] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [voting, setVoting] = useState(false);

  useEffect(() => {
    if (user) {
      loadContributions();
    }
  }, [user, activeTab]);

  const loadContributions = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      // Get token from localStorage for authentication
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No authentication token found');
        setLoading(false);
        return;
      }

      console.log(`🔄 Loading ${activeTab === 'all' ? 'community' : 'personal'} contributions...`);
      
      if (activeTab === 'all') {
        // Load all community contributions
        const response = await fetch(`${API}/api/contributions/community`, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log(`📥 Community contributions response: ${response.status}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log(`✅ Loaded ${data.length} community contributions:`, data);
          setContributions(data);
        } else {
          console.error('Failed to load community contributions:', response.status);
          // Fallback to basic contributions endpoint
          const fallbackResponse = await fetch(`${API}/api/contributions`, {
            headers: { 
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          if (fallbackResponse.ok) {
            const fallbackData = await fallbackResponse.json();
            console.log(`✅ Fallback: Loaded ${fallbackData.length} contributions:`, fallbackData);
            setContributions(fallbackData);
          }
        }
      } else {
        // Load user's own contributions
        const response = await fetch(`${API}/api/contributions/my-contributions`, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log(`📥 Personal contributions response: ${response.status}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log(`✅ Loaded ${data.length} personal contributions:`, data);
          setMyContributions(data);
        } else {
          console.error('Failed to load personal contributions:', response.status);
        }
      }
    } catch (error) {
      console.error('Error loading contributions:', error);
    }
    setLoading(false);
  };

  const handleVote = async (contributionId, voteType, voteData = null) => {
    setVoting(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No authentication token found');
        return;
      }

      console.log(`🗳️ Voting ${voteType} on contribution ${contributionId}`);
      
      const requestBody = voteData || {
        vote_type: voteType === 'up' ? 'upvote' : 'downvote',
        comment: `Voted ${voteType === 'up' ? 'positively' : 'negatively'} via UI`
      };
      
      const response = await fetch(`${API}/api/contributions/${contributionId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`📥 Vote response: ${response.status}`);

      if (response.ok) {
        const result = await response.json();
        console.log(`✅ Vote successful:`, result);
        
        // Reload contributions to show updated vote counts
        await loadContributions();
      } else {
        const error = await response.text();
        console.error('Vote failed:', response.status, error);
      }
    } catch (error) {
      console.error('Error voting on contribution:', error);
    } finally {
      setVoting(false);
    }
  };

  const openDetailModal = (contribution) => {
    setSelectedContribution(contribution);
    setIsDetailModalOpen(true);
  };

  const closeDetailModal = () => {
    setSelectedContribution(null);
    setIsDetailModalOpen(false);
  };

  const filteredData = activeTab === 'all' 
    ? contributions.filter(contrib => {
        const searchLower = searchQuery.toLowerCase();
        const entityName = contrib.entity_name || contrib.title || '';
        const userName = contrib.user_name || contrib.author_name || '';
        
        return entityName.toLowerCase().includes(searchLower) ||
               userName.toLowerCase().includes(searchLower);
      })
    : myContributions.filter(contrib => {
        const searchLower = searchQuery.toLowerCase();
        const entityName = contrib.entity_name || contrib.title || '';
        
        return entityName.toLowerCase().includes(searchLower);
      });

  // Debug logging
  console.log('🔍 UnifiedContributionsPage Debug:', {
    activeTab,
    contributionsCount: contributions.length,
    myContributionsCount: myContributions.length,
    filteredDataCount: filteredData.length,
    searchQuery,
    sampleContribution: contributions[0]
  });

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

                  {/* Proposed Data Preview */}
                  {contribution.proposed_data && Object.keys(contribution.proposed_data).length > 0 && (
                    <div className="bg-blue-50 rounded-lg p-3 mb-4">
                      <h4 className="text-sm font-medium text-blue-900 mb-2">📝 Aperçu des modifications :</h4>
                      <div className="text-sm text-blue-800 space-y-1">
                        {Object.entries(contribution.proposed_data).slice(0, 3).map(([field, value]) => (
                          <div key={field} className="flex">
                            <span className="font-medium mr-2">{field}:</span>
                            <span className="truncate">{Array.isArray(value) ? value.join(', ') : String(value).slice(0, 50)}{String(value).length > 50 ? '...' : ''}</span>
                          </div>
                        ))}
                        {Object.keys(contribution.proposed_data).length > 3 && (
                          <div className="text-blue-600 text-xs">+ {Object.keys(contribution.proposed_data).length - 3} autre(s) modification(s)</div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Images Preview */}
                  {contribution.images && Object.keys(contribution.images).length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">📸 Images proposées :</h4>
                      <div className="flex space-x-2">
                        {Object.entries(contribution.images).slice(0, 4).map(([key, img], index) => (
                          <div key={index} className="w-12 h-12 bg-gray-200 rounded border overflow-hidden">
                            <img 
                              src={Array.isArray(img) ? img[0] : img}
                              alt={key}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        ))}
                        {Object.keys(contribution.images).length > 4 && (
                          <div className="w-12 h-12 bg-gray-200 rounded border flex items-center justify-center text-xs text-gray-600">
                            +{Object.keys(contribution.images).length - 4}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => openDetailModal(contribution)}
                    className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
                  >
                    <span>👁️</span>
                    <span>Voir détails complets</span>
                  </button>
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
                      onClick={() => handleVote(contribution.id, 'up')}
                      className="flex items-center space-x-1 bg-green-100 hover:bg-green-200 text-green-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                      disabled={voting}
                    >
                      <span>👍</span>
                      <span>Approuver</span>
                    </button>
                    <button
                      onClick={() => handleVote(contribution.id, 'down')}
                      className="flex items-center space-x-1 bg-red-100 hover:bg-red-200 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                      disabled={voting}
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
      
      {/* Contribution Detail Modal */}
      <ContributionDetailModal
        contribution={selectedContribution}
        isOpen={isDetailModalOpen}
        onClose={closeDetailModal}
        onVote={handleVote}
        voting={voting}
        API={API}
      />
    </div>
  );
};

export default UnifiedContributionsPage;