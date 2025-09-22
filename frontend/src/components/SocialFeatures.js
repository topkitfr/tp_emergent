import React, { useState, useEffect } from 'react';

const SocialFeatures = ({ user, targetUserId, API }) => {
  const [followStatus, setFollowStatus] = useState(null);
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [activeTab, setActiveTab] = useState('followers');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (user && targetUserId) {
      fetchSocialData();
    }
  }, [user, targetUserId]);

  const fetchSocialData = async () => {
    try {
      setLoading(true);
      
      // Fetch follow status, followers, and following in parallel
      const [statusResponse, followersResponse, followingResponse] = await Promise.all([
        fetch(`${API}/api/users/${targetUserId}/follow-status`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        }),
        fetch(`${API}/api/users/${targetUserId}/followers?limit=20`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        }),
        fetch(`${API}/api/users/${targetUserId}/following?limit=20`, {
          headers: { 'Authorization': `Bearer ${user.token}` }
        })
      ]);

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setFollowStatus(statusData);
      }

      if (followersResponse.ok) {
        const followersData = await followersResponse.json();
        setFollowers(followersData);
      }

      if (followingResponse.ok) {
        const followingData = await followingResponse.json();
        setFollowing(followingData);
      }
    } catch (error) {
      console.error('Error fetching social data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowToggle = async () => {
    if (!followStatus?.can_follow) return;
    
    try {
      setActionLoading(true);
      
      const method = followStatus.is_following ? 'DELETE' : 'POST';
      const response = await fetch(`${API}/api/users/${targetUserId}/follow`, {
        method,
        headers: { 'Authorization': `Bearer ${user.token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setFollowStatus(prev => ({
          ...prev,
          is_following: data.following,
          followed_at: data.following ? new Date().toISOString() : null
        }));
        
        // Refresh social data to update counts
        fetchSocialData();
      }
    } catch (error) {
      console.error('Error toggling follow:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUserFollowToggle = async (userId, currentlyFollowing) => {
    try {
      const method = currentlyFollowing ? 'DELETE' : 'POST';
      const response = await fetch(`${API}/api/users/${userId}/follow`, {
        method,
        headers: { 'Authorization': `Bearer ${user.token}` }
      });

      if (response.ok) {
        // Update the local state
        if (activeTab === 'followers') {
          setFollowers(prev => prev.map(user => 
            user.id === userId 
              ? { ...user, is_following: !currentlyFollowing }
              : user
          ));
        } else {
          setFollowing(prev => prev.map(user => 
            user.id === userId 
              ? { ...user, is_following: !currentlyFollowing }
              : user
          ));
        }
      }
    } catch (error) {
      console.error('Error toggling user follow:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-24 mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-16"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Don't show follow button if viewing own profile
  const isOwnProfile = user.id === targetUserId;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Follow Button and Stats */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex space-x-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{followers.length}</div>
            <div className="text-sm text-gray-600">Followers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{following.length}</div>
            <div className="text-sm text-gray-600">Following</div>
          </div>
        </div>
        
        {!isOwnProfile && followStatus?.can_follow && (
          <button
            onClick={handleFollowToggle}
            disabled={actionLoading}
            className={`px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 ${
              followStatus.is_following
                ? 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {actionLoading ? '...' : (followStatus.is_following ? 'Following' : 'Follow')}
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex space-x-0 mb-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('followers')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'followers'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Followers ({followers.length})
        </button>
        <button
          onClick={() => setActiveTab('following')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'following'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Following ({following.length})
        </button>
      </div>

      {/* User Lists */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {(activeTab === 'followers' ? followers : following).map((person) => (
          <div key={person.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {person.profile_picture_url ? (
                  <img
                    src={`${API}/${person.profile_picture_url}`}
                    alt={person.name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">
                    {person.name?.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <div>
                <div className="font-medium text-gray-900">{person.name}</div>
                <div className="text-sm text-gray-500">
                  {person.xp} XP • {person.level}
                </div>
              </div>
            </div>
            
            {person.id !== user.id && (
              <button
                onClick={() => handleUserFollowToggle(person.id, person.is_following)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  person.is_following
                    ? 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {person.is_following ? 'Following' : 'Follow'}
              </button>
            )}
          </div>
        ))}
        
        {(activeTab === 'followers' ? followers : following).length === 0 && (
          <div className="text-center py-8 text-gray-500">
            {activeTab === 'followers' 
              ? 'No followers yet' 
              : 'Not following anyone yet'
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialFeatures;