import React, { useState, useEffect } from 'react';

const CollectionStats = ({ user, targetUserId, API }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && targetUserId) {
      fetchCollectionStats();
    }
  }, [user, targetUserId]);

  const fetchCollectionStats = async () => {
    try {
      const response = await fetch(`${API}/api/users/${targetUserId}/collection-stats`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching collection stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="h-6 bg-gray-200 rounded w-12 mx-auto mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-16 mx-auto"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <div className="text-2xl mb-2">📊</div>
          <p>No collection statistics available</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const getRarityColor = (score) => {
    if (score >= 80) return 'text-purple-600 bg-purple-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    if (score >= 40) return 'text-green-600 bg-green-100';
    if (score >= 20) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Collection Statistics</h3>
      
      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{stats.owned_count}</div>
          <div className="text-sm text-gray-600">Kits Owned</div>
        </div>
        
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{stats.wanted_count}</div>
          <div className="text-sm text-gray-600">Want List</div>
        </div>
        
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{stats.rare_kits}</div>
          <div className="text-sm text-gray-600">Rare Kits</div>
        </div>
        
        <div className="text-center p-3 bg-orange-50 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">{stats.signed_kits}</div>
          <div className="text-sm text-gray-600">Signed</div>
        </div>
      </div>

      {/* Collection Value */}
      {stats.total_estimated_value > 0 && (
        <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-3">Collection Value</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">Estimated Value</div>
              <div className="text-xl font-bold text-green-600">
                {formatCurrency(stats.total_estimated_value)}
              </div>
            </div>
            {stats.total_purchase_value > 0 && (
              <div>
                <div className="text-sm text-gray-600">Purchase Value</div>
                <div className="text-xl font-bold text-blue-600">
                  {formatCurrency(stats.total_purchase_value)}
                </div>
                {stats.value_gain !== 0 && (
                  <div className={`text-sm font-medium ${
                    stats.value_gain > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stats.value_gain > 0 ? '+' : ''}{formatCurrency(stats.value_gain)} gain
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Rarity Score */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-semibold text-gray-900">Rarity Score</h4>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRarityColor(stats.rarity_score.score)}`}>
            {stats.rarity_score.score}%
          </div>
        </div>
        <div className="text-sm font-medium text-gray-800 mb-1">
          {stats.rarity_score.level}
        </div>
        <div className="text-sm text-gray-600 mb-3">
          {stats.rarity_score.description}
        </div>
        
        {/* Rarity Breakdown */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-gray-600">Rare Kits:</span>
            <span className="font-medium">{stats.rarity_score?.breakdown?.rare_kits || '0%'}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-600">Vintage Kits:</span>
            <span className="font-medium">{stats.rarity_score?.breakdown?.vintage_kits || '0%'}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-600">Signed Kits:</span>
            <span className="font-medium">{stats.rarity_score?.breakdown?.signed_kits || '0%'}</span>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-4">
        {/* Top Kit Types */}
        {Object.keys(stats.categories.kit_types).length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Top Kit Types</h4>
            <div className="space-y-2">
              {Object.entries(stats.categories.kit_types).map(([type, count]) => (
                <div key={type} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 capitalize">{type.replace('_', ' ')}</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Clubs */}
        {Object.keys(stats.categories.clubs).length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Top Clubs</h4>
            <div className="space-y-2">
              {Object.entries(stats.categories.clubs).slice(0, 5).map(([club, count]) => (
                <div key={club} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{club}</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Brands */}
        {Object.keys(stats.categories.brands).length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Top Brands</h4>
            <div className="space-y-2">
              {Object.entries(stats.categories.brands).slice(0, 5).map(([brand, count]) => (
                <div key={brand} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{brand}</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CollectionStats;