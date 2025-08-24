import React, { useState, useEffect } from 'react';

const PublicCollectionsPage = ({ API }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPublicUsers();
  }, []);

  const loadPublicUsers = async () => {
    setLoading(true);
    try {
      // Load users with public collections
      const response = await fetch(`${API}/api/users/with-collections`);
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error loading users with collections:', error);
    }
    setLoading(false);
  };

  const filteredUsers = users.filter(user => 
    user.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.favorite_club_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Chargement des collectionneurs...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Collections</h1>
        <p className="text-gray-600">
          Découvrez les collectionneurs de maillots de TopKit et leurs collections
        </p>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <div className="relative">
          <input
            type="text"
            placeholder="Rechercher un collectionneur ou club préféré..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">{users.length}</div>
          <div className="text-gray-600">Collectionneurs actifs</div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">
            {users.reduce((sum, user) => sum + user.total_owned, 0)}
          </div>
          <div className="text-gray-600">Maillots possédés</div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
          <div className="text-3xl font-bold text-red-600 mb-2">
            {users.reduce((sum, user) => sum + user.total_wanted, 0)}
          </div>
          <div className="text-gray-600">Maillots recherchés</div>
        </div>
      </div>

      {/* Users Grid */}
      {filteredUsers.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">👥</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucun collectionneur trouvé</h3>
          <p className="text-gray-600">
            {searchQuery ? 'Aucun collectionneur ne correspond à votre recherche.' : 'Il n\'y a pas encore de collectionneurs actifs.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredUsers.map((user) => (
            <div key={user.id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer">
              {/* User Header */}
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-16 h-16 rounded-full overflow-hidden">
                  {user.profile_picture_url ? (
                    <img 
                      src={`${API}/${user.profile_picture_url}`}
                      alt="Profile"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-xl font-bold text-white">
                        {user.name?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{user.name}</h3>
                  <p className="text-sm text-gray-600">
                    Membre depuis {new Date(user.created_at).getFullYear()}
                  </p>
                </div>
              </div>

              {/* User Info */}
              {user.bio && (
                <p className="text-sm text-gray-700 mb-3 italic">"{user.bio}"</p>
              )}

              {user.favorite_club_name && (
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-sm text-gray-600">Club préféré:</span>
                  <span className="text-sm font-medium text-blue-600">⚽ {user.favorite_club_name}</span>
                </div>
              )}

              {/* Collection Stats */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center bg-green-50 rounded-lg p-3">
                  <div className="text-lg font-bold text-green-600">{user.total_owned}</div>
                  <div className="text-xs text-gray-600">Possédés</div>
                </div>
                <div className="text-center bg-red-50 rounded-lg p-3">
                  <div className="text-lg font-bold text-red-600">{user.total_wanted}</div>
                  <div className="text-xs text-gray-600">Recherchés</div>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex justify-center space-x-3">
                {user.instagram_username && (
                  <a 
                    href={`https://instagram.com/${user.instagram_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-pink-600 hover:text-pink-700"
                    title="Instagram"
                  >
                    📷
                  </a>
                )}
                
                {user.twitter_username && (
                  <a 
                    href={`https://x.com/${user.twitter_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600"
                    title="X/Twitter"
                  >
                    🐦
                  </a>
                )}
                
                {user.website && (
                  <a 
                    href={user.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-gray-700"
                    title="Site web"
                  >
                    🌐
                  </a>
                )}
              </div>

              {/* View Collection Button */}
              <div className="mt-4">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                  Voir la collection
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PublicCollectionsPage;