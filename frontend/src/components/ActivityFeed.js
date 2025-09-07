import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, Clock, ThumbsUp, ThumbsDown, CheckCircle, XCircle, 
  Upload, MessageSquare, Star, Users, RefreshCw, Bell
} from 'lucide-react';

const ActivityFeed = ({ API, currentUser, className = '' }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const intervalRef = useRef();

  const activityTypes = {
    contribution_created: { icon: Upload, color: 'text-blue-600 bg-blue-100', label: 'New Contribution' },
    voted: { icon: ThumbsUp, color: 'text-green-600 bg-green-100', label: 'Vote Cast' },
    auto_approved: { icon: CheckCircle, color: 'text-green-600 bg-green-100', label: 'Auto-Approved' },
    auto_rejected: { icon: XCircle, color: 'text-red-600 bg-red-100', label: 'Auto-Rejected' },
    moderated: { icon: Star, color: 'text-purple-600 bg-purple-100', label: 'Moderated' },
    image_uploaded: { icon: Upload, color: 'text-indigo-600 bg-indigo-100', label: 'Image Added' },
    comment_added: { icon: MessageSquare, color: 'text-yellow-600 bg-yellow-100', label: 'Comment Added' }
  };

  useEffect(() => {
    fetchActivities();
    
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchActivities, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, filter]);

  const fetchActivities = async () => {
    try {
      // In a real implementation, this would be a proper activity endpoint
      // For now, we'll simulate by getting recent contributions and their history
      const response = await fetch(`${API}/api/contributions-v2/?limit=20`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const contributions = await response.json();
        const simulatedActivities = generateActivitiesFromContributions(contributions);
        setActivities(simulatedActivities.slice(0, 50));
      }
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateActivitiesFromContributions = (contributions) => {
    const activities = [];
    
    contributions.forEach(contribution => {
      // Add contribution creation activity
      activities.push({
        id: `create_${contribution.id}`,
        type: 'contribution_created',
        user_name: 'Community Member',
        contribution_title: contribution.title,
        contribution_id: contribution.id,
        entity_type: contribution.entity_type,
        timestamp: contribution.created_at,
        details: {
          entity_type: contribution.entity_type,
          topkit_reference: contribution.topkit_reference
        }
      });

      // Add voting activities (simulated)
      if (contribution.upvotes > 0) {
        for (let i = 0; i < contribution.upvotes; i++) {
          activities.push({
            id: `vote_up_${contribution.id}_${i}`,
            type: 'voted',
            user_name: 'Community Voter',
            contribution_title: contribution.title,
            contribution_id: contribution.id,
            entity_type: contribution.entity_type,
            timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
            details: {
              vote_type: 'upvote',
              current_upvotes: contribution.upvotes,
              current_downvotes: contribution.downvotes
            }
          });
        }
      }

      if (contribution.downvotes > 0) {
        for (let i = 0; i < contribution.downvotes; i++) {
          activities.push({
            id: `vote_down_${contribution.id}_${i}`,
            type: 'voted',
            user_name: 'Community Voter',
            contribution_title: contribution.title,
            contribution_id: contribution.id,
            entity_type: contribution.entity_type,
            timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
            details: {
              vote_type: 'downvote',
              current_upvotes: contribution.upvotes,
              current_downvotes: contribution.downvotes
            }
          });
        }
      }

      // Add auto-approval/rejection activities
      if (contribution.status === 'approved' && contribution.upvotes >= 3) {
        activities.push({
          id: `auto_approved_${contribution.id}`,
          type: 'auto_approved',
          user_name: 'System',
          contribution_title: contribution.title,
          contribution_id: contribution.id,
          entity_type: contribution.entity_type,
          timestamp: contribution.updated_at,
          details: {
            votes_count: contribution.upvotes,
            auto_action: true
          }
        });
      }

      if (contribution.status === 'rejected' && contribution.downvotes >= 2) {
        activities.push({
          id: `auto_rejected_${contribution.id}`,
          type: 'auto_rejected',
          user_name: 'System',
          contribution_title: contribution.title,
          contribution_id: contribution.id,
          entity_type: contribution.entity_type,
          timestamp: contribution.updated_at,
          details: {
            votes_count: contribution.downvotes,
            auto_action: true
          }
        });
      }

      // Add image upload activities
      if (contribution.images_count > 0) {
        activities.push({
          id: `images_${contribution.id}`,
          type: 'image_uploaded',
          user_name: 'Contributor',
          contribution_title: contribution.title,
          contribution_id: contribution.id,
          entity_type: contribution.entity_type,
          timestamp: contribution.updated_at,
          details: {
            images_count: contribution.images_count
          }
        });
      }
    });

    // Sort by timestamp (newest first)
    return activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const formatEntityType = (type) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getActivityDescription = (activity) => {
    switch (activity.type) {
      case 'contribution_created':
        return `created a new ${formatEntityType(activity.entity_type).toLowerCase()}`;
      case 'voted':
        return `${activity.details.vote_type === 'upvote' ? 'upvoted' : 'downvoted'} a ${formatEntityType(activity.entity_type).toLowerCase()}`;
      case 'auto_approved':
        return `was auto-approved with ${activity.details.votes_count} community votes`;
      case 'auto_rejected':
        return `was auto-rejected with ${activity.details.votes_count} community votes`;
      case 'image_uploaded':
        return `added ${activity.details.images_count} image${activity.details.images_count !== 1 ? 's' : ''} to`;
      case 'moderated':
        return `was moderated by an admin`;
      default:
        return 'had activity';
    }
  };

  const filteredActivities = activities.filter(activity => {
    if (filter === 'all') return true;
    if (filter === 'votes') return activity.type === 'voted';
    if (filter === 'approvals') return ['auto_approved', 'auto_rejected', 'moderated'].includes(activity.type);
    if (filter === 'contributions') return activity.type === 'contribution_created';
    return true;
  });

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="flex space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Community Activity</h3>
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              Live
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-1 rounded transition-colors ${
                autoRefresh ? 'text-green-600 bg-green-100' : 'text-gray-400 bg-gray-100'
              }`}
              title={autoRefresh ? 'Auto-refresh enabled' : 'Auto-refresh disabled'}
            >
              <Bell className="w-4 h-4" />
            </button>
            
            <button
              onClick={fetchActivities}
              className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
              title="Refresh now"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="mt-3 flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {[
            { id: 'all', label: 'All Activity' },
            { id: 'contributions', label: 'New Contributions' },
            { id: 'votes', label: 'Votes' },
            { id: 'approvals', label: 'Approvals' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                filter === tab.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Activity List */}
      <div className="max-h-96 overflow-y-auto">
        {filteredActivities.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <Activity className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p>No recent activity</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredActivities.map(activity => {
              const activityConfig = activityTypes[activity.type] || activityTypes.contribution_created;
              const Icon = activityConfig.icon;
              
              return (
                <div key={activity.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${activityConfig.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-gray-900 text-sm">
                          {activity.user_name}
                        </span>
                        <span className="text-gray-600 text-sm">
                          {getActivityDescription(activity)}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-800 font-medium truncate">
                        {activity.contribution_title}
                      </p>
                      
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-gray-500">
                          {formatTimeAgo(activity.timestamp)}
                        </span>
                        
                        {activity.details.topkit_reference && (
                          <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                            {activity.details.topkit_reference}
                          </span>
                        )}
                        
                        {activity.type === 'voted' && (
                          <span className="text-xs text-gray-500">
                            {activity.details.current_upvotes}↑ {activity.details.current_downvotes}↓
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        <div className="flex justify-between items-center text-xs text-gray-600">
          <span>{filteredActivities.length} activities shown</span>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              Active community
            </span>
            {autoRefresh && (
              <span className="flex items-center gap-1 text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Live updates
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityFeed;