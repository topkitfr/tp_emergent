import React, { useState, useEffect } from 'react';

const MyCollectionPage = ({ user, API }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('owned');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (user) {
      loadMyCollections();
    }
  }, [user]);

  const loadMyCollections = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const [ownedRes, wantedRes] = await Promise.all([
        fetch(`${API}/api/users/${user.id}/collections/owned`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${API}/api/users/${user.id}/collections/wanted`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);

      const owned = ownedRes.ok ? await ownedRes.json() : [];
      const wanted = wantedRes.ok ? await wantedRes.json() : [];

      setCollections([...owned, ...wanted]);
    } catch (error) {
      console.error('Error loading my collections:', error);
    }
    setLoading(false);
  };

  const filteredCollections = collections.filter(collection => {
    const matchesTab = collection.collection_type === activeTab;
    
    // Fix search to work with new data structure
    if (searchQuery) {
      const jerseyRelease = collection.jersey_release || {};
      const masterJersey = collection.master_jersey || {};
      const teamInfo = masterJersey.team_info || {};
      
      const matchesSearch = 
        jerseyRelease.player_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        teamInfo.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jerseyRelease.topkit_reference?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchesTab && matchesSearch;
    }
    
    // If no search query, just filter by tab
    return matchesTab;
  });

  // Calculate collection value estimates
  const calculateCollectionValue = () => {
    const ownedItems = collections.filter(c => c.collection_type === 'owned');
    
    let totalLow = 0;
    let totalMid = 0;
    let totalHigh = 0;
    
    ownedItems.forEach(item => {
      // Use jersey release retail price or fallback to purchase price
      const jerseyRelease = item.jersey_release || {};
      const baseValue = item.purchase_price || jerseyRelease.retail_price || 50; // Use retail price from jersey release
      const condition = item.condition || 'good';
      
      // Condition multiplier
      const conditionMultiplier = {
        'mint': 1.2,
        'near_mint': 1.1,
        'excellent': 1.0,
        'very_good': 0.9,
        'good': 0.8,
        'worn': 0.6
      };
      
      const multiplier = conditionMultiplier[condition] || 1.0;
      const adjustedValue = baseValue * multiplier;
      
      // Range estimation (±20% for low/high)
      totalLow += adjustedValue * 0.8;
      totalMid += adjustedValue;
      totalHigh += adjustedValue * 1.2;
    });
    
    return {
      low: Math.round(totalLow),
      mid: Math.round(totalMid),
      high: Math.round(totalHigh),
      count: ownedItems.length
    };
  };

  const collectionValue = calculateCollectionValue();
  const ownedCount = collections.filter(c => c.collection_type === 'owned').length;
  const wantedCount = collections.filter(c => c.collection_type === 'wanted').length;

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔒</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connexion requise</h3>
          <p className="text-gray-600">
            Vous devez être connecté pour accéder à votre collection
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
          <span className="ml-3 text-gray-600">Chargement de votre collection...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Ma Collection</h1>
        <p className="text-gray-600">
          Gérez vos maillots possédés et votre liste de souhaits
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-600">{ownedCount}</div>
              <div className="text-sm text-gray-600">Maillots possédés</div>
            </div>
            <div className="text-3xl">💎</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-red-600">{wantedCount}</div>
              <div className="text-sm text-gray-600">Maillots recherchés</div>
            </div>
            <div className="text-3xl">❤️</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-600">{ownedCount + wantedCount}</div>
              <div className="text-sm text-gray-600">Total collection</div>
            </div>
            <div className="text-3xl">📱</div>
          </div>
        </div>

        {/* Estimation Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-600">Valeur estimée</div>
            <div className="text-3xl">💰</div>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Basse:</span>
              <span className="font-medium">€{collectionValue.low}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Moyenne:</span>
              <span className="font-bold text-green-600">€{collectionValue.mid}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Haute:</span>
              <span className="font-medium">€{collectionValue.high}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Collection Value Details */}
      {ownedCount > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">📊</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Estimation de votre collection</h3>
                <p className="text-sm text-gray-600">Basée sur {collectionValue.count} maillot{collectionValue.count > 1 ? 's' : ''} possédé{collectionValue.count > 1 ? 's' : ''}</p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-white rounded-lg border">
              <div className="text-xl font-bold text-red-600">€{collectionValue.low}</div>
              <div className="text-xs text-gray-600">Estimation basse</div>
              <div className="text-xs text-gray-500 mt-1">État moyen, marché conservateur</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-lg border-2 border-green-500">
              <div className="text-2xl font-bold text-green-600">€{collectionValue.mid}</div>
              <div className="text-sm text-gray-700 font-medium">Estimation moyenne</div>
              <div className="text-xs text-gray-500 mt-1">Valeur de marché actuelle</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-lg border">
              <div className="text-xl font-bold text-blue-600">€{collectionValue.high}</div>
              <div className="text-xs text-gray-600">Estimation haute</div>
              <div className="text-xs text-gray-500 mt-1">Bon état, marché optimiste</div>
            </div>
          </div>
          
          <div className="mt-4 text-xs text-gray-500 text-center">
            💡 Les estimations sont calculées selon l'état, l'âge et la rareté présumée des maillots. 
            Elles sont indicatives et peuvent varier selon le marché actuel.
          </div>
        </div>
      )}

      {/* Tabs and Search */}
      <div className="bg-white rounded-lg border border-gray-200 mb-8">
        <div className="border-b border-gray-200">
          <div className="flex space-x-0">
            <button
              onClick={() => setActiveTab('owned')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                activeTab === 'owned'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">💎</span>
              Possédés ({ownedCount})
            </button>
            
            <button
              onClick={() => setActiveTab('wanted')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-all ${
                activeTab === 'wanted'
                  ? 'border-red-600 text-red-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'  
              }`}
            >
              <span className="mr-2">❤️</span>
              Recherchés ({wantedCount})
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="p-6">
          <div className="relative">
            <input
              type="text"
              placeholder="Rechercher dans ma collection..."
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

      {/* Collection Grid */}
      {filteredCollections.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">
            {activeTab === 'owned' ? '💎' : '❤️'}
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {activeTab === 'owned' ? 'Aucun maillot possédé' : 'Aucun maillot recherché'}
          </h3>
          <p className="text-gray-600">
            {activeTab === 'owned' 
              ? 'Commencez à ajouter des maillots à votre collection'
              : 'Ajoutez des maillots à votre liste de souhaits'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCollections.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              {/* Jersey Image */}
              <div className="w-full h-48 bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                {item.jersey_release?.product_images?.[0] ? (
                  <img 
                    src={item.jersey_release.product_images[0]}
                    alt={item.jersey_release?.player_name || 'Maillot'}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <span className="text-4xl">👕</span>
                )}
              </div>

              {/* Jersey Info */}
              <div className="space-y-3">
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {item.jersey_release?.player_name || 'Maillot'} 
                    {item.jersey_release?.player_number && ` #${item.jersey_release.player_number}`}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {item.master_jersey?.team_info?.name || 'Équipe inconnue'} - {item.master_jersey?.season || 'Saison inconnue'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {item.jersey_release?.topkit_reference}
                  </p>
                </div>

                {/* Details */}
                <div className="space-y-2">
                  {item.size && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Taille:</span>
                      <span className="font-medium">{item.size}</span>
                    </div>
                  )}
                  
                  {item.condition && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">État:</span>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        item.condition === 'new' ? 'bg-green-100 text-green-800' :
                        item.condition === 'near_mint' ? 'bg-blue-100 text-blue-800' :
                        item.condition === 'very_good' ? 'bg-yellow-100 text-yellow-800' :
                        item.condition === 'good' ? 'bg-orange-100 text-orange-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {item.condition === 'new' ? 'Neuf' :
                         item.condition === 'near_mint' ? 'Quasi-neuf' :
                         item.condition === 'very_good' ? 'Très bon' :
                         item.condition === 'good' ? 'Bon' : 'Usé'}
                      </span>
                    </div>
                  )}

                  {(item.purchase_price || item.jersey_release?.retail_price) && activeTab === 'owned' && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Prix d'achat:</span>
                      <span className="font-medium text-green-600">€{item.purchase_price || item.jersey_release?.retail_price}</span>
                    </div>
                  )}

                  {/* Individual Item Estimation */}
                  {activeTab === 'owned' && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-xs text-gray-600 mb-1">Estimation actuelle:</div>
                      <div className="flex items-center justify-between">
                        {(() => {
                          const baseValue = item.purchase_price || item.jersey_release?.retail_price || 50;
                          const conditionMultiplier = {
                            'mint': 1.2, 'near_mint': 1.1, 'excellent': 1.0, 'very_good': 0.9, 'good': 0.8, 'worn': 0.6
                          };
                          const multiplier = conditionMultiplier[item.condition] || 1.0;
                          const adjustedValue = baseValue * multiplier;
                          
                          return (
                            <>
                              <div className="text-xs text-gray-500">
                                €{Math.round(adjustedValue * 0.8)} - €{Math.round(adjustedValue * 1.2)}
                              </div>
                              <div className="text-sm font-bold text-blue-600">
                                €{Math.round(adjustedValue)}
                              </div>
                            </>
                          );
                        })()}
                      </div>
                    </div>
                  )}
                </div>

                {/* Collection Type Badge */}
                <div className="pt-3 border-t border-gray-100">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    item.collection_type === 'owned'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {item.collection_type === 'owned' ? '💎 Possédé' : '❤️ Recherché'}
                  </span>
                </div>

                {/* Actions */}
                <div className="pt-3 flex space-x-2">
                  <button className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                    Modifier
                  </button>
                  <button className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                    Supprimer
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyCollectionPage;