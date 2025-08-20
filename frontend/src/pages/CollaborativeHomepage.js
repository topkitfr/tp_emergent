import React from 'react';

const CollaborativeHomepage = ({ user, teams, brands, players, masterJerseys, onViewChange }) => {
  
  // Statistics
  const stats = [
    { label: 'Équipes', value: teams?.length || 0, icon: '⚽', color: 'blue' },
    { label: 'Marques', value: brands?.length || 0, icon: '👕', color: 'green' },
    { label: 'Joueurs', value: players?.length || 0, icon: '👤', color: 'purple' },
    { label: 'Maillots', value: masterJerseys?.length || 0, icon: '📋', color: 'red' }
  ];

  const recentTeams = teams?.slice(0, 6) || [];
  const recentBrands = brands?.slice(0, 4) || [];
  const recentMasterJerseys = masterJerseys?.slice(0, 8) || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-700"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-16 md:py-24 text-center text-white">
          <div className="mb-8">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              Base de données collaborative
            </h1>
            <p className="text-xl md:text-2xl opacity-90 mb-2">
              de maillots de football
            </p>
            <p className="text-lg opacity-75 max-w-3xl mx-auto">
              Découvrez, documentez et partagez l'univers des maillots de football avec la communauté TopKit
            </p>
          </div>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => onViewChange('explore')}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all shadow-lg"
            >
              🔍 Explorer la base de données
            </button>
            {user && (
              <button
                onClick={() => onViewChange('contributions')}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold transition-all shadow-lg"
              >
                📝 Contribuer
              </button>
            )}
            {!user && (
              <button
                onClick={() => onViewChange('teams')}
                className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3 rounded-lg font-semibold transition-all"
              >
                👥 Parcourir sans compte
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="max-w-7xl mx-auto px-4 -mt-12 relative z-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg p-6 shadow-lg text-center">
              <div className={`text-3xl mb-2`}>{stat.icon}</div>
              <div className={`text-2xl font-bold text-${stat.color}-600 mb-1`}>
                {stat.value.toLocaleString()}
              </div>
              <div className="text-gray-600 text-sm font-medium">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* How it Works Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Comment ça marche ?</h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            TopKit fonctionne comme un Wikipedia pour les maillots de football. Chaque contributeur enrichit 
            la base de données qui est ensuite vérifiée par la communauté.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🔍</span>
            </div>
            <h3 className="text-xl font-semibold mb-3">1. Explorez</h3>
            <p className="text-gray-600">
              Parcourez les équipes, marques, joueurs et maillots référencés par la communauté
            </p>
          </div>

          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📝</span>
            </div>
            <h3 className="text-xl font-semibold mb-3">2. Contribuez</h3>
            <p className="text-gray-600">
              Ajoutez de nouvelles informations, photos et détails sur vos maillots préférés
            </p>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">✅</span>
            </div>
            <h3 className="text-xl font-semibold mb-3">3. Validez</h3>
            <p className="text-gray-600">
              Participez à la vérification des contributions pour garantir la qualité des données
            </p>
          </div>
        </div>
      </div>

      {/* Recent Additions */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4">
          
          {/* Recent Teams */}
          <div className="mb-16">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Équipes récemment ajoutées</h2>
              <button
                onClick={() => onViewChange('teams')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Voir toutes les équipes →
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {recentTeams.map((team) => (
                <div
                  key={team.id}
                  className="bg-white rounded-lg p-4 hover:shadow-md transition-all cursor-pointer group"
                  onClick={() => onViewChange('teams')}
                >
                  <div className="text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:bg-blue-200 transition-colors">
                      <span className="text-xl">⚽</span>
                    </div>
                    <h3 className="font-semibold text-sm text-gray-900 mb-1 line-clamp-2">{team.name}</h3>
                    <p className="text-xs text-gray-500">{team.country}</p>
                    <p className="text-xs text-blue-600 mt-2">{team.topkit_reference}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Brands */}
          <div className="mb-16">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Marques populaires</h2>
              <button
                onClick={() => onViewChange('brands')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Voir toutes les marques →
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {recentBrands.map((brand) => (
                <div
                  key={brand.id}
                  className="bg-white rounded-lg p-6 hover:shadow-md transition-all cursor-pointer group"
                  onClick={() => onViewChange('brands')}
                >
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
                      <span className="text-2xl">👕</span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">{brand.name}</h3>
                    <p className="text-sm text-gray-500 mb-1">{brand.country || 'Pays inconnu'}</p>
                    <p className="text-xs text-blue-600">{brand.topkit_reference}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Master Jerseys */}
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Maillots récemment documentés</h2>
              <button
                onClick={() => onViewChange('master-jerseys')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Voir tous les maillots →
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
              {recentMasterJerseys.map((jersey) => (
                <div
                  key={jersey.id}
                  className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group"
                  onClick={() => onViewChange('master-jerseys')}
                >
                  <div className="aspect-square bg-gray-100 flex items-center justify-center">
                    <span className="text-3xl">👕</span>
                  </div>
                  <div className="p-3">
                    <h3 className="font-semibold text-xs text-gray-900 mb-1 line-clamp-2">
                      {jersey.team_info?.name || 'Équipe inconnue'}
                    </h3>
                    <p className="text-xs text-gray-500 mb-1">{jersey.season}</p>
                    <p className="text-xs text-blue-600">{jersey.topkit_reference}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-blue-600 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Rejoignez la communauté TopKit</h2>
          <p className="text-xl opacity-90 mb-8">
            Aidez-nous à construire la plus grande base de données collaborative de maillots de football
          </p>
          {user ? (
            <button
              onClick={() => onViewChange('contributions')}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all shadow-lg"
            >
              🚀 Commencer à contribuer
            </button>
          ) : (
            <button
              onClick={() => onViewChange('teams')}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all shadow-lg"
            >
              🔍 Découvrir la base de données
            </button>
          )}
        </div>
      </div>

    </div>
  );
};

export default CollaborativeHomepage;