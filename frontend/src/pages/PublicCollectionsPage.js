import React, { useState, useEffect } from 'react';

const PublicCollectionsPage = ({ API }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPublicCollections();
  }, []);

  const loadPublicCollections = async () => {
    setLoading(true);
    try {
      // Load public collections from all users
      const response = await fetch(`${API}/api/collections/public`);
      if (response.ok) {
        const data = await response.json();
        setCollections(data);
      }
    } catch (error) {
      console.error('Error loading public collections:', error);
    }
    setLoading(false);
  };

  const filteredCollections = collections.filter(collection => {
    const matchesFilter = filter === 'all' || collection.collection_type === filter;
    const matchesSearch = collection.user_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         collection.jersey_name?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const groupedCollections = filteredCollections.reduce((acc, collection) => {
    const userId = collection.user_id;
    if (!acc[userId]) {
      acc[userId] = {
        user: {
          id: userId,
          name: collection.user_name,
          profile_picture_url: collection.user_profile_picture,
          total_owned: 0,
          total_wanted: 0
        },
        collections: []
      };
    }
    acc[userId].collections.push(collection);
    if (collection.collection_type === 'owned') {
      acc[userId].user.total_owned++;
    } else {
      acc[userId].user.total_wanted++;
    }
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Chargement des collections...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Collections Publiques</h1>
        <p className="text-gray-600">
          Découvrez les collections de maillots des autres collectionneurs de TopKit
        </p>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          {/* Filter Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Toutes ({collections.length})
            </button>
            <button
              onClick={() => setFilter('owned')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'owned'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              💎 Possédés ({collections.filter(c => c.collection_type === 'owned').length})
            </button>
            <button
              onClick={() => setFilter('wanted')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'wanted'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              ❤️ Recherchés ({collections.filter(c => c.collection_type === 'wanted').length})
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Rechercher par collectionneur ou maillot..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full md:w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Collections Grid */}
      {Object.keys(groupedCollections).length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📱</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune collection publique</h3>
          <p className="text-gray-600">
            Il n'y a pas encore de collections publiques à afficher.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.values(groupedCollections).map((userGroup) => (
            <div key={userGroup.user.id} className="bg-white rounded-lg border border-gray-200 p-6">
              {/* User Header */}
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 rounded-full overflow-hidden">
                  {userGroup.user.profile_picture_url ? (
                    <img 
                      src={`${API}/${userGroup.user.profile_picture_url}`}
                      alt="Profile"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-lg font-bold text-white">
                        {userGroup.user.name?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{userGroup.user.name}</h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>💎 {userGroup.user.total_owned} possédés</span>
                    <span>❤️ {userGroup.user.total_wanted} recherchés</span>
                  </div>
                </div>
              </div>

              {/* Collection Items */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {userGroup.collections.map((item) => (
                  <div
                    key={item.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        <span className="text-xl">👕</span>
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{item.jersey_name || 'Maillot'}</h4>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            item.collection_type === 'owned'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {item.collection_type === 'owned' ? '💎 Possédé' : '❤️ Recherché'}
                          </span>
                          {item.size && (
                            <span className="text-xs text-gray-500">Taille {item.size}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PublicCollectionsPage;