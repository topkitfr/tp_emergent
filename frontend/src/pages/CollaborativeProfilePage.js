import React, { useState, useEffect } from 'react';
import UserSettingsPanel from '../UserSettingsPanel';
import ProfilePictureModal from '../ProfilePictureModal';

const CollaborativeProfilePage = ({ user, API }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [publicInfo, setPublicInfo] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showProfilePictureModal, setShowProfilePictureModal] = useState(false);

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
      const [profileRes, publicInfoRes, statsRes] = await Promise.all([
        fetch(`${API}/api/users/${user.id}/profile`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        }),
        fetch(`${API}/api/users/profile/public-info`, {
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

      if (publicInfoRes.ok) {
        const publicData = await publicInfoRes.json();
        setPublicInfo(publicData);
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setUserStats(statsData);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '👤' },
    { id: 'contributions', label: 'Contributions', icon: '📝' },
    { id: 'activity', label: 'Activity', icon: '📈' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  const handleProfileUpdate = (updatedProfile) => {
    setUserProfile(updatedProfile);
    // Update user context if needed
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign In Required</h1>
          <p className="text-gray-600">You need to sign in to view your profile.</p>
        </div>
      </div>
    );
  }

  // User Info Card Component
  const UserInfoCard = () => {
    const memberSinceDate = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown';
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start space-x-4">
          {/* Profile Picture */}
          <div className="flex-shrink-0">
            <div className="relative">
              {user.profile_picture_url ? (
                <img 
                  src={`${API}/${user.profile_picture_url}`}
                  alt="Profile"
                  className="w-20 h-20 rounded-full object-cover border-2 border-gray-200"
                />
              ) : (
                <div className="w-20 h-20 bg-gray-300 rounded-full flex items-center justify-center text-2xl font-bold text-gray-600">
                  {user.name?.charAt(0).toUpperCase() || 'U'}
                </div>
              )}
              
              <button
                onClick={() => setShowProfilePictureModal(true)}
                className="absolute bottom-0 right-0 bg-blue-600 text-white rounded-full p-1 hover:bg-blue-700 transition-colors"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* User Details */}
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
                <p className="text-gray-600 mb-2">{user.email}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Member since {memberSinceDate}</span>
                  {user.role === 'admin' && (
                    <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">
                      Admin
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Stats Cards Component
  const StatsCards = () => {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {userStats?.collections_count || 0}
          </div>
          <div className="text-sm text-gray-600">Collections</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {userStats?.contributions_count || 0}
          </div>
          <div className="text-sm text-gray-600">Contributions</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {userStats?.votes_count || 0}
          </div>
          <div className="text-sm text-gray-600">Votes Cast</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {userStats?.jerseys_added || 0}
          </div>
          <div className="text-sm text-gray-600">Kits Created</div>
        </div>
      </div>
    );
  };

  // Contribution Quality Component
  const ContributionQuality = () => {
    if (!userStats || (userStats.contributions_approved + userStats.contributions_rejected) === 0) {
      return null;
    }

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Contribution Quality</h2>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-xl font-bold text-green-600">
              {userStats?.contributions_approved || 0}
            </div>
            <div className="text-sm text-gray-600">Approved Contributions</div>
          </div>
          
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <div className="text-xl font-bold text-yellow-600">
              {userStats?.contributions_pending || 0}
            </div>
            <div className="text-sm text-gray-600">Pending</div>
          </div>
          
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="text-xl font-bold text-red-600">
              {userStats?.contributions_rejected || 0}
            </div>
            <div className="text-sm text-gray-600">Rejected Contributions</div>
          </div>
        </div>
        
        {userStats && (userStats.contributions_approved + userStats.contributions_rejected) > 0 && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Approval Rate</span>
              <span className="text-sm font-medium">
                {Math.round(
                  (userStats.contributions_approved / 
                   (userStats.contributions_approved + userStats.contributions_rejected)) * 100
                )}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-300"
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
    );
  };

  // Badges & Achievements Component
  const BadgesAchievements = () => {
    const badges = [];
    
    // Add badges based on achievements
    if (userStats?.contributions_approved >= 1) {
      badges.push({
        title: 'First Contribution',
        description: 'Made your first contribution',
        icon: '🌟',
        color: 'bg-blue-100 text-blue-800'
      });
    }
    
    if (userStats?.contributions_approved >= 5) {
      badges.push({
        title: 'Contributor',
        description: '5+ approved contributions',
        icon: '📝',
        color: 'bg-green-100 text-green-800'
      });
    }
    
    if (userStats?.contributions_approved >= 10) {
      badges.push({
        title: 'Expert Contributor',
        description: '10+ approved contributions',
        icon: '🏆',
        color: 'bg-purple-100 text-purple-800'
      });
    }
    
    if (userStats?.votes_count >= 20) {
      badges.push({
        title: 'Active Voter',
        description: '20+ votes cast',
        icon: '🗳️',
        color: 'bg-yellow-100 text-yellow-800'
      });
    }

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Badges & Achievements</h2>
        
        {badges.length === 0 ? (
          <p className="text-gray-500 text-center py-4">
            Start contributing to earn your first badge!
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {badges.map((badge, index) => (
              <div key={index} className={`p-3 rounded-lg ${badge.color}`}>
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{badge.icon}</span>
                  <div>
                    <h4 className="font-medium">{badge.title}</h4>
                    <p className="text-sm opacity-75">{badge.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Contributor Profile</h1>
          <p className="text-gray-600">
            Manage your profile and view your contributions to TopKit
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading your profile...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* User Info Card */}
            <UserInfoCard />
            
            {/* Stats Cards */}
            <StatsCards />
            
            {/* Tabs Navigation */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200">
                <div className="flex space-x-0">
                  {tabs.map((tab) => (
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
              
              <div className="p-6">
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    <ContributionQuality />
                    <BadgesAchievements />
                  </div>
                )}
                
                {activeTab === 'contributions' && (
                  <div className="text-center py-12">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">My Contributions</h3>
                    <p className="text-gray-600">
                      This section will display the detailed history of your contributions
                    </p>
                  </div>
                )}
                
                {activeTab === 'activity' && (
                  <div className="text-center py-12">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Recent Activity</h3>
                    <p className="text-gray-600">
                      This section will display your recent activity on the platform
                    </p>
                  </div>
                )}
                
                {activeTab === 'settings' && (
                  <div className="text-center py-12">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Settings</h3>
                    <p className="text-gray-600 mb-6">
                      This section will allow you to modify your preferences and settings
                    </p>
                    <button
                      onClick={() => setShowSettingsModal(true)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                      Open Settings
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Settings Modal */}
      {showSettingsModal && (
        <UserSettingsPanel
          isOpen={showSettingsModal}
          onClose={() => setShowSettingsModal(false)}
          user={user}
          onUpdate={handleProfileUpdate}
        />
      )}

      {/* Profile Picture Modal */}
      {showProfilePictureModal && (
        <ProfilePictureModal
          user={user}
          onClose={() => setShowProfilePictureModal(false)}
          onUpdate={handleProfileUpdate}
        />
      )}
    </div>
  );
};

export default CollaborativeProfilePage;