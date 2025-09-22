import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { OptimizedImage } from './PerformanceOptimizations';

const RecentCollection = ({ user, targetUserId, API, onViewMore }) => {
  const [recentItems, setRecentItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (user && targetUserId) {
      fetchRecentCollection();
    }
  }, [user, targetUserId]);

  const fetchRecentCollection = async () => {
    try {
      const response = await fetch(`${API}/api/users/${targetUserId}/recent-collection?limit=5`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecentItems(data);
      }
    } catch (error) {
      console.error('Error fetching recent collection:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const itemTime = new Date(timestamp);
    const diffInDays = Math.floor((now - itemTime) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    
    return itemTime.toLocaleDateString();
  };

  const getCollectionTypeIcon = (type) => {
    switch (type) {
      case 'owned': return '🏠';
      case 'wanted': return '❤️';
      default: return '👕';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Collection</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="animate-pulse">
              <div className="aspect-square bg-gray-200 rounded-lg mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-3/4 mb-1"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Collection</h3>
        {recentItems.length > 0 && (
          <button
            onClick={onViewMore}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
          >
            View More →
          </button>
        )}
      </div>
      
      {recentItems.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">👕</div>
          <p className="text-gray-600">No collection items yet</p>
          <p className="text-sm text-gray-500 mt-1">
            Start collecting kits to see them here
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {recentItems.map((item) => (
            <div key={item.collection_id} className="group cursor-pointer">
              <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden mb-2 hover:shadow-md transition-shadow">
                {item.master_kit.image_url ? (
                  <OptimizedImage
                    src={`${API}/${item.master_kit.image_url}`}
                    alt={`${item.master_kit.club} ${item.master_kit.season}`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    width={200}
                    height={200}
                    quality={80}
                    placeholder="👕"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-3xl text-gray-400">
                    👕
                  </div>
                )}
                
                {/* Collection type badge */}
                <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded-full text-xs flex items-center">
                  <span className="mr-1">{getCollectionTypeIcon(item.collection_type)}</span>
                  <span className="capitalize">{item.collection_type}</span>
                </div>
                
                {/* Date badge */}
                <div className="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded-full text-xs">
                  {formatTimeAgo(item.created_at)}
                </div>
              </div>
              
              <div className="text-center">
                <div className="font-medium text-gray-900 text-sm truncate">
                  {item.master_kit.club}
                </div>
                <div className="text-xs text-gray-500 truncate">
                  {item.master_kit.season} • {item.master_kit.kit_type}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {item.master_kit.brand}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecentCollection;