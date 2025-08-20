import React, { useState, useEffect } from 'react';

const CollaborativeProfilePage = ({ user, API }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);

  // Load user profile data
  useEffect(() => {
    if (user) {
      loadUserProfile();
    }
  }, [user]);

  const loadUserProfile = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const [profileRes, statsRes] = await Promise.all([
        fetch(`${API}/api/users/${user.id}/profile`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        }),
        fetch(`${API}/api/users/${user.id}/stats`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        })
      ]);

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setUserProfile(profileData);
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setUserStats(statsData);
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: '📊' },
    { id: 'contributions', label: 'Contributions', icon: '📝' },
    { id: 'activity', label: 'Activité', icon: '📈' },
    { id: 'settings', label: 'Paramètres', icon: '⚙️' }
  ];

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔒</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connexion requise</h3>
          <p className="text-gray-600">
            Vous devez être connecté pour accéder à votre profil
          </p>
        </div>
      </div>
    );
  }

  const OverviewTab = () => (
    <div className="space-y-8">
      
      {/* Profile Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-start space-x-6">
          <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-3xl font-bold text-white">
              {user.name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{user.name}</h1>
            <p className="text-gray-600 mb-4">{user.email}</p>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Rôle:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  user.role === 'admin' 
                    ? 'bg-red-100 text-red-800' 
                    : user.role === 'moderator'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {user.role === 'admin' ? 'Administrateur' : 
                   user.role === 'moderator' ? 'Modérateur' : 'Utilisateur'}
                </span>
              </div>
              
              {user.verified_level && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Statut:</span>
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                    ✓ Vérifié
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {userStats?.teams_created || 0}
              </div>
              <div className="text-sm text-gray-600">Équipes créées</div>
            </div>
            <div className="text-2xl">⚽</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-600">
                {userStats?.brands_created || 0}
              </div>
              <div className="text-sm text-gray-600">Marques créées</div>
            </div>
            <div className="text-2xl">👕</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {userStats?.players_created || 0}
              </div>
              <div className="text-sm text-gray-600">Joueurs créés</div>
            </div>
            <div className="text-2xl">👤</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {userStats?.master_jerseys_created || 0}
              </div>
              <div className="text-sm text-gray-600">Maillots créés</div>
            </div>
            <div className="text-2xl">📋</div>
          </div>
        </div>
      </div>

      {/* Contribution Quality */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Qualité des contributions</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {userStats?.contributions_approved || 0}
            </div>
            <div className="text-sm text-gray-600">Contributions approuvées</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">
              {userStats?.contributions_pending || 0}
            </div>
            <div className="text-sm text-gray-600">En attente de révision</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">
              {userStats?.contributions_rejected || 0}
            </div>
            <div className="text-sm text-gray-600">Contributions rejetées</div>
          </div>
        </div>

        {/* Approval Rate */}
        {userStats && (userStats.contributions_approved + userStats.contributions_rejected) > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Taux d'approbation</span>
              <span className="text-sm font-medium">
                {Math.round(
                  (userStats.contributions_approved / 
                   (userStats.contributions_approved + userStats.contributions_rejected)) * 100
                )}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full"
                style={{
                  width: `${Math.round(
                    (userStats.contributions_approved / 
                     (userStats.contributions_approved + userStats.contributions_rejected)) * 100
                  )}%`
                }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Badges & Achievements */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Badges & Réalisations</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {userStats?.teams_created >= 1 && (
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">⚽</div>
              <div className="text-xs font-medium text-blue-800">Premier pas</div>
              <div className="text-xs text-blue-600">Première équipe créée</div>
            </div>
          )}

          {userStats?.teams_created >= 5 && (
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">🏟️</div>
              <div className="text-xs font-medium text-blue-800">Architecte</div>
              <div className="text-xs text-blue-600">5+ équipes créées</div>
            </div>
          )}

          {userStats?.contributions_approved >= 10 && (
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">✅</div>
              <div className="text-xs font-medium text-green-800">Contributeur fiable</div>
              <div className="text-xs text-green-600">10+ contributions approuvées</div>
            </div>
          )}

          {userStats?.master_jerseys_created >= 1 && (
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl mb-2">👕</div>
              <div className="text-xs font-medium text-orange-800">Designer</div>
              <div className="text-xs text-orange-600">Premier maillot créé</div>
            </div>
          )}
        </div>
      </div>

    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mon Profil Collaborateur</h1>
        <p className="text-gray-600">
          Gérez votre profil et consultez vos contributions à TopKit
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-gray-200 mb-8">
        <div className="border-b border-gray-200">
          <div className="flex space-x-0">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Chargement du profil...</span>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && <OverviewTab />}
              
              {activeTab === 'contributions' && (
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">📝</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Mes Contributions</h3>
                  <p className="text-gray-600">
                    Cette section affichera l'historique détaillé de vos contributions
                  </p>
                </div>
              )}
              
              {activeTab === 'activity' && (
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">📈</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Activité Récente</h3>
                  <p className="text-gray-600">
                    Cette section affichera votre activité récente sur la plateforme
                  </p>
                </div>
              )}
              
              {activeTab === 'settings' && (
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">⚙️</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Paramètres du Compte</h3>
                  <p className="text-gray-600">
                    Cette section permettra de modifier vos préférences et paramètres
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

    </div>
  );
};

export default CollaborativeProfilePage;