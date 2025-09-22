import React, { useState, useEffect } from 'react';
import UserSettingsPanel from '../UserSettingsPanel';
import ProfilePictureModal from '../ProfilePictureModal';
import GamificationProfile from '../components/GamificationProfile';
import ProfileCompleteness from '../components/ProfileCompleteness';
import SocialFeatures from '../components/SocialFeatures';
import CollectionStats from '../components/CollectionStats';
import UserActivityFeed from '../components/UserActivityFeed';

const CollaborativeProfilePage = ({ user, API }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [publicInfo, setPublicInfo] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [showProfilePictureModal, setShowProfilePictureModal] = useState(false);
  const [settingsData, setSettingsData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    bio: '',
    favorite_club: '',
    instagram_username: '',
    twitter_username: '',
    website: '',
    profile_private: false
  });
  const [settingsLoading, setSettingsLoading] = useState(false);

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
    { id: 'social', label: 'Social', icon: '👥' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
    { id: 'activity', label: 'Activity', icon: '📝' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  const handleProfileUpdate = (updatedProfile) => {
    setUserProfile(updatedProfile);
    // Update user context if needed
  };

  const handleSettingsFieldFocus = (fieldName) => {
    // Switch to settings tab and focus on specific field
    setActiveTab('settings');
    setTimeout(() => {
      const field = document.querySelector(`[name="${fieldName}"]`);
      if (field) {
        field.focus();
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  const handleSettingsUpdate = async (e) => {
    e.preventDefault();
    setSettingsLoading(true);
    
    try {
      const response = await fetch(`${API}/api/users/${user.id}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(settingsData)
      });

      if (response.ok) {
        const updatedProfile = await response.json();
        setUserProfile(updatedProfile);
        alert('Profile updated successfully!');
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to update profile'}`);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile');
    } finally {
      setSettingsLoading(false);
    }
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

  // Enhanced Badges & Achievements Component with Gamification Rewards
  const BadgesAchievements = () => {
    const [gamificationData, setGamificationData] = useState(null);
    const badges = [];
    
    // Load gamification data for XP-based badges  
    useEffect(() => {
      const loadGamificationData = async () => {
        if (!user?.id) return;
        try {
          const response = await fetch(`${API}/api/users/${user.id}/gamification`);
          if (response.ok) {
            const data = await response.json();
            setGamificationData(data);
          }
        } catch (error) {
          console.error('Error loading gamification data:', error);
        }
      };
      loadGamificationData();
    }, [user]);

    // XP-based Level Badges (Gamification Rewards)
    if (gamificationData?.xp >= 100) {
      badges.push({
        title: '⚽ Titulaire',
        description: 'Atteint le niveau Titulaire (100+ XP)',
        icon: '⚽',
        color: 'bg-blue-100 text-blue-800',
        category: 'level'
      });
    }
    
    if (gamificationData?.xp >= 500) {
      badges.push({
        title: '🏆 Légende',
        description: 'Atteint le niveau Légende (500+ XP)',
        icon: '🏆',
        color: 'bg-purple-100 text-purple-800',
        category: 'level'
      });
    }
    
    if (gamificationData?.xp >= 2000) {
      badges.push({
        title: '🔥 Ballon d\'Or',
        description: 'Atteint le niveau suprême (2000+ XP)',
        icon: '🔥',
        color: 'bg-yellow-100 text-yellow-800',
        category: 'level'
      });
    }

    // XP Milestone Badges
    if (gamificationData?.xp >= 50) {
      badges.push({
        title: 'Rising Star',
        description: 'Gagné 50+ XP',
        icon: '⭐',
        color: 'bg-indigo-100 text-indigo-800',
        category: 'xp'
      });
    }
    
    if (gamificationData?.xp >= 200) {
      badges.push({
        title: 'Dedicated Player',
        description: 'Gagné 200+ XP',
        icon: '💎',
        color: 'bg-cyan-100 text-cyan-800',
        category: 'xp'
      });
    }
    
    if (gamificationData?.xp >= 1000) {
      badges.push({
        title: 'XP Master',
        description: 'Gagné 1000+ XP',
        icon: '👑',
        color: 'bg-amber-100 text-amber-800',
        category: 'xp'
      });
    }

    // Contribution-based Achievement Badges
    if (userStats?.contributions_approved >= 1) {
      badges.push({
        title: 'First Contribution',
        description: 'Made your first contribution',
        icon: '🌟',
        color: 'bg-green-100 text-green-800',
        category: 'contribution'
      });
    }
    
    if (userStats?.contributions_approved >= 5) {
      badges.push({
        title: 'Contributor',
        description: '5+ approved contributions',
        icon: '📝',
        color: 'bg-green-100 text-green-800',
        category: 'contribution'
      });
    }
    
    if (userStats?.contributions_approved >= 10) {
      badges.push({
        title: 'Expert Contributor',
        description: '10+ approved contributions',
        icon: '🏅',
        color: 'bg-purple-100 text-purple-800',
        category: 'contribution'
      });
    }
    
    if (userStats?.contributions_approved >= 25) {
      badges.push({
        title: 'Elite Contributor',
        description: '25+ approved contributions',
        icon: '🎖️',
        color: 'bg-red-100 text-red-800',
        category: 'contribution'
      });
    }
    
    // Activity-based Badges
    if (userStats?.votes_count >= 20) {
      badges.push({
        title: 'Active Voter',
        description: '20+ votes cast',
        icon: '🗳️',
        color: 'bg-yellow-100 text-yellow-800',
        category: 'activity'
      });
    }
    
    if (userStats?.jerseys_added >= 5) {
      badges.push({
        title: 'Kit Collector',
        description: '5+ kits created',
        icon: '👕',
        color: 'bg-teal-100 text-teal-800',
        category: 'activity'
      });
    }

    // Quality-based Badges
    if (userStats && (userStats.contributions_approved + userStats.contributions_rejected) > 0) {
      const approvalRate = Math.round(
        (userStats.contributions_approved / 
         (userStats.contributions_approved + userStats.contributions_rejected)) * 100
      );
      
      if (approvalRate >= 90 && userStats.contributions_approved >= 5) {
        badges.push({
          title: 'Quality Contributor',
          description: '90%+ approval rate (5+ contributions)',
          icon: '✨',
          color: 'bg-pink-100 text-pink-800',
          category: 'quality'
        });
      }
    }

    // Group badges by category
    const badgesByCategory = {
      level: badges.filter(b => b.category === 'level'),
      xp: badges.filter(b => b.category === 'xp'),
      contribution: badges.filter(b => b.category === 'contribution'),
      activity: badges.filter(b => b.category === 'activity'),
      quality: badges.filter(b => b.category === 'quality')
    };

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Badges & Achievements</h2>
          <div className="text-sm text-gray-500">
            {badges.length} badge{badges.length !== 1 ? 's' : ''} earned
          </div>
        </div>
        
        {badges.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">🏆</div>
            <p className="text-gray-500 mb-2">Start contributing to earn your first badge!</p>
            <p className="text-xs text-gray-400">Badges are earned based on XP, contributions, and activity</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Level Badges */}
            {badgesByCategory.level.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <span className="mr-2">🏆</span>Level Rewards
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {badgesByCategory.level.map((badge, index) => (
                    <div key={`level-${index}`} className={`p-3 rounded-lg ${badge.color} border-l-4 border-current`}>
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
              </div>
            )}

            {/* XP Milestone Badges */}
            {badgesByCategory.xp.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <span className="mr-2">⭐</span>XP Milestones
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {badgesByCategory.xp.map((badge, index) => (
                    <div key={`xp-${index}`} className={`p-3 rounded-lg ${badge.color}`}>
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
              </div>
            )}

            {/* Other Categories */}
            {(badgesByCategory.contribution.length > 0 || badgesByCategory.activity.length > 0 || badgesByCategory.quality.length > 0) && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <span className="mr-2">🎯</span>Achievements
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[...badgesByCategory.contribution, ...badgesByCategory.activity, ...badgesByCategory.quality].map((badge, index) => (
                    <div key={`other-${index}`} className={`p-3 rounded-lg ${badge.color}`}>
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
              </div>
            )}

            {/* Progress Hint */}
            <div className="border-t border-gray-200 pt-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <h4 className="text-sm font-medium text-gray-700 mb-2">💡 Earn More Rewards</h4>
                <div className="text-xs text-gray-600 space-y-1">
                  <div>• Contribute kits, teams, players to earn XP and level up</div>
                  <div>• Maintain high approval rates for quality badges</div>
                  <div>• Stay active with voting and community participation</div>
                  {gamificationData?.xp < 100 && (
                    <div className="text-blue-600 font-medium">
                      • {100 - gamificationData.xp} XP until Titulaire level ⚽
                    </div>
                  )}
                </div>
              </div>
            </div>
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
                    <ProfileCompleteness 
                      user={user} 
                      API={API} 
                      onFieldClick={handleSettingsFieldFocus} 
                    />
                    <GamificationProfile user={user} API={API} />
                    <ContributionQuality />
                    <BadgesAchievements />
                  </div>
                )}
                
                {activeTab === 'social' && (
                  <div className="space-y-6">
                    <SocialFeatures 
                      user={user} 
                      targetUserId={user.id} 
                      API={API} 
                    />
                  </div>
                )}
                
                {activeTab === 'analytics' && (
                  <div className="space-y-6">
                    <CollectionStats 
                      user={user} 
                      targetUserId={user.id} 
                      API={API} 
                    />
                  </div>
                )}
                
                {activeTab === 'activity' && (
                  <div className="space-y-6">
                    <UserActivityFeed 
                      user={user} 
                      targetUserId={user.id} 
                      API={API} 
                    />
                  </div>
                )}
                
                {activeTab === 'settings' && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Settings</h3>
                    
                    <form onSubmit={handleSettingsUpdate} className="space-y-6">
                      {/* Basic Information */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Full Name
                          </label>
                          <input
                            type="text"
                            name="name"
                            value={settingsData.name}
                            onChange={(e) => setSettingsData(prev => ({...prev, name: e.target.value}))}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Email Address
                          </label>
                          <input
                            type="email"
                            name="email"
                            value={settingsData.email}
                            onChange={(e) => setSettingsData(prev => ({...prev, email: e.target.value}))}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>

                      {/* Bio */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Bio
                        </label>
                        <textarea
                          name="bio"
                          value={settingsData.bio}
                          onChange={(e) => setSettingsData(prev => ({...prev, bio: e.target.value}))}
                          rows="3"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="Tell us about yourself..."
                        />
                      </div>

                      {/* Favorite Club */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Favorite Club
                        </label>
                        <input
                          type="text"
                          name="favorite_club"
                          value={settingsData.favorite_club}
                          onChange={(e) => setSettingsData(prev => ({...prev, favorite_club: e.target.value}))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="e.g., FC Barcelona, PSG, Manchester United"
                        />
                      </div>

                      {/* Social Links */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Instagram Username
                          </label>
                          <input
                            type="text"
                            name="instagram_username"
                            value={settingsData.instagram_username}
                            onChange={(e) => setSettingsData(prev => ({...prev, instagram_username: e.target.value}))}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                            placeholder="@username"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Twitter Username
                          </label>
                          <input
                            type="text"
                            name="twitter_username"
                            value={settingsData.twitter_username}
                            onChange={(e) => setSettingsData(prev => ({...prev, twitter_username: e.target.value}))}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                            placeholder="@username"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Website
                        </label>
                        <input
                          type="url"
                          value={settingsData.website}
                          onChange={(e) => setSettingsData(prev => ({...prev, website: e.target.value}))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                          placeholder="https://yourwebsite.com"
                        />
                      </div>

                      {/* Privacy Settings */}
                      <div className="pt-6 border-t border-gray-200">
                        <h4 className="text-lg font-medium text-gray-900 mb-4">Privacy Settings</h4>
                        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div>
                            <label className="text-sm font-medium text-gray-700">
                              Private Profile
                            </label>
                            <p className="text-xs text-gray-500 mt-1">
                              When enabled, only logged-in users can view your profile details
                            </p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={settingsData.profile_private}
                              onChange={(e) => setSettingsData(prev => ({...prev, profile_private: e.target.checked}))}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      </div>

                      {/* Save Button */}
                      <div className="flex justify-end pt-4 border-t border-gray-200">
                        <button
                          type="submit"
                          disabled={settingsLoading}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                        >
                          {settingsLoading ? 'Saving...' : 'Save Changes'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

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