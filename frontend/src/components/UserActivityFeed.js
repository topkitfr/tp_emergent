import React, { useState, useEffect } from 'react';

const UserActivityFeed = ({ user, targetUserId, API }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && targetUserId) {
      fetchActivityFeed();
    }
  }, [user, targetUserId]);

  const fetchActivityFeed = async () => {
    try {
      const response = await fetch(`${API}/api/users/${targetUserId}/activity-feed?limit=20`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setActivities(data);
      }
    } catch (error) {
      console.error('Error fetching activity feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffInSeconds = Math.floor((now - activityTime) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    
    return activityTime.toLocaleDateString();
  };

  const getActivityIcon = (activity) => {
    switch (activity.type) {
      case 'contribution':
        switch (activity.item_type) {
          case 'team': return '🏆';
          case 'brand': return '👕';
          case 'player': return '⚽';
          case 'competition': return '🏟️';
          case 'jersey': return '👔';
          default: return '➕';
        }
      case 'collection':
        return activity.action.includes('owned') ? '🏠' : '❤️';
      default:
        return '📝';
    }
  };

  const getActivityColor = (activity) => {
    switch (activity.type) {
      case 'contribution':
        return 'bg-green-100 text-green-800';
      case 'collection':
        return activity.action.includes('owned') 
          ? 'bg-blue-100 text-blue-800' 
          : 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="animate-pulse flex items-start space-x-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
      
      {activities.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📋</div>
          <p className="text-gray-600">No recent activity</p>
          <p className="text-sm text-gray-500 mt-1">
            Activity will appear here when contributions are made or kits are added to collections
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
              {/* Activity Icon */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${getActivityColor(activity)}`}>
                {getActivityIcon(activity)}
              </div>
              
              {/* Activity Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">{activity.action}</span>
                      {activity.item_name && (
                        <span className="ml-1">
                          <span className="font-semibold text-blue-600">
                            {activity.item_name}
                          </span>
                        </span>
                      )}
                    </p>
                    
                    {/* XP Award */}
                    {activity.xp_awarded > 0 && (
                      <div className="mt-1">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          +{activity.xp_awarded} XP
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-xs text-gray-500 ml-2 flex-shrink-0">
                    {formatTimeAgo(activity.timestamp)}
                  </div>
                </div>
                
                {/* Activity Type Badge */}
                <div className="mt-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getActivityColor(activity)}`}>
                    {activity.type === 'contribution' ? `${activity.item_type} contribution` : 'collection update'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {activities.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <button
              onClick={fetchActivityFeed}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Refresh Activity
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserActivityFeed;