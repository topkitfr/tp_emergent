import React, { useState, useEffect } from 'react';

const CollectionsPage = ({ user, API, onDataUpdate }) => {
  const [activeTab, setActiveTab] = useState('owned');
  const [collections, setCollections] = useState({
    owned: [],
    wanted: [],
    listings: []
  });
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    totalValue: 0,
    totalItems: 0,
    wantedItems: 0
  });

  // Load user collections
  useEffect(() => {
    if (user) {
      loadCollections();
    }
  }, [user]);

  const loadCollections = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      // Load owned jerseys
      const ownedResponse = await fetch(`${API}/api/users/${user.id}/collections/owned`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      });
      
      // Load wanted jerseys  
      const wantedResponse = await fetch(`${API}/api/users/${user.id}/collections/wanted`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      });

      if (ownedResponse.ok && wantedResponse.ok) {
        const owned = await ownedResponse.json();
        const wanted = await wantedResponse.json();
        
        setCollections({
          owned: owned || [],
          wanted: wanted || [],
          listings: [] // TODO: Load user listings
        });

        // Calculate stats
        const totalValue = owned.reduce((sum, item) => sum + (item.estimated_value || 0), 0);
        setStats({
          totalValue,
          totalItems: owned.length,
          wantedItems: wanted.length
        });
      }
    } catch (error) {
      console.error('Error loading collections:', error);
    }
    setLoading(false);
  };

  const tabs = [
    { 
      id: 'owned', 
      label: 'Mes maillots', 
      icon: '💎', 
      count: collections.owned.length,
      description: 'Maillots que vous possédez'
    },
    { 
      id: 'wanted', 
      label: 'Ma wishlist', 
      icon: '❤️', 
      count: collections.wanted.length,
      description: 'Maillots recherchés'
    },
    { 
      id: 'estimates', 
      label: 'Estimations', 
      icon: '📊', 
      count: collections.owned.length,
      description: 'Valeurs estimées'
    }
  ];

  const renderJerseyCard = (jerseyCollection, type = 'owned') => (
    <div key={jerseyCollection.id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      
      {/* Jersey Image */}
      <div className="aspect-square bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
        {jerseyCollection.jersey_release?.product_images?.[0] ? (
          <img 
            src={jerseyCollection.jersey_release.product_images[0]} 
            alt="Jersey" 
            className="w-full h-full object-cover rounded-lg"
          />
        ) : (
          <span className="text-4xl">👕</span>
        )}
      </div>

      {/* Jersey Info */}
      <div className="space-y-2">
        <h3 className="font-semibold text-gray-900">
          {jerseyCollection.master_jersey?.team_info?.name || 'Équipe inconnue'}
        </h3>
        <p className="text-sm text-gray-600">
          {jerseyCollection.master_jersey?.season} • {jerseyCollection.master_jersey?.jersey_type}
        </p>
        
        {/* Release specific info */}
        {jerseyCollection.jersey_release && (
          <div className="text-sm text-gray-500">
            {jerseyCollection.jersey_release.player_name && (
              <p>Flocage: {jerseyCollection.jersey_release.player_name} #{jerseyCollection.jersey_release.player_number}</p>
            )}
            {jerseyCollection.size && (
              <p>Taille: {jerseyCollection.size}</p>
            )}
            {jerseyCollection.condition && (
              <p>État: {jerseyCollection.condition}</p>
            )}
          </div>
        )}

        {type === 'owned' && (
          <>
            {/* Estimated value */}
            <div className="pt-2 border-t border-gray-100">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Valeur estimée:</span>
                <span className="font-semibold text-green-600">
                  {jerseyCollection.estimated_value ? `${jerseyCollection.estimated_value}€` : 'Non évaluée'}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-3 flex gap-2">
              <button className="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 transition-colors">
                Actualiser estimation
              </button>
              <button className="px-3 py-2 text-gray-600 hover:text-gray-800 text-sm">
                ⚙️
              </button>
            </div>
          </>
        )}

        {type === 'wanted' && (
          <div className="pt-3">
            <button className="w-full bg-red-100 text-red-700 py-2 px-3 rounded text-sm hover:bg-red-200 transition-colors">
              ❤️ Dans ma wishlist
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const renderEstimateView = () => (
    <div className="space-y-6">
      
      {/* Value Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              {stats.totalValue.toLocaleString()}€
            </h3>
            <p className="text-gray-600">Valeur totale estimée de votre collection</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Moyenne par maillot</div>
            <div className="font-semibold text-gray-900">
              {stats.totalItems > 0 ? Math.round(stats.totalValue / stats.totalItems) : 0}€
            </div>
          </div>
        </div>
      </div>

      {/* Top valued jerseys */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Maillots les plus valorisés</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {collections.owned
            .filter(item => item.estimated_value > 0)
            .sort((a, b) => (b.estimated_value || 0) - (a.estimated_value || 0))
            .slice(0, 6)
            .map(item => renderJerseyCard(item, 'estimate'))}
        </div>
      </div>
    </div>
  );

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-6xl mb-4">💎</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Collections TopKit</h2>
          <p className="text-gray-600 mb-6">
            Connectez-vous pour gérer votre collection de maillots et obtenir des estimations de valeur
          </p>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
            Se connecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              💎 Mes Collections
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Gérez votre collection de maillots, suivez leur valeur et découvrez de nouvelles pièces à acquérir
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.totalItems}</div>
              <div className="text-sm text-green-700">Maillots possédés</div>
            </div>
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.totalValue.toLocaleString()}€</div>
              <div className="text-sm text-blue-700">Valeur estimée</div>
            </div>
            <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{stats.wantedItems}</div>
              <div className="text-sm text-red-700">Dans ma wishlist</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{tab.icon}</span>
                  <span>{tab.label}</span>
                  <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                    {tab.count}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement de votre collection...</p>
          </div>
        ) : (
          <>
            {activeTab === 'owned' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Mes maillots ({collections.owned.length})
                  </h2>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors">
                    Ajouter un maillot
                  </button>
                </div>
                
                {collections.owned.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {collections.owned.map(item => renderJerseyCard(item, 'owned'))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">👕</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucun maillot dans votre collection</h3>
                    <p className="text-gray-600 mb-6">
                      Commencez à documenter votre collection pour obtenir des estimations de valeur
                    </p>
                    <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                      Ajouter votre premier maillot
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'wanted' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Ma wishlist ({collections.wanted.length})
                  </h2>
                </div>
                
                {collections.wanted.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {collections.wanted.map(item => renderJerseyCard(item, 'wanted'))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">❤️</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Votre wishlist est vide</h3>
                    <p className="text-gray-600 mb-6">
                      Parcourez le catalogue pour ajouter des maillots à votre wishlist
                    </p>
                    <button className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors">
                      Explorer le catalogue
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'estimates' && renderEstimateView()}
          </>
        )}
      </div>
    </div>
  );
};

export default CollectionsPage;