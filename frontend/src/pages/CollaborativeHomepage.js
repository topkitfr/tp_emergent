import React from 'react';

const CollaborativeHomepage = ({ user, teams, brands, players, masterJerseys, onViewChange }) => {
  
  // Statistics
  const stats = [
    { label: 'Équipes', value: teams?.length || 0, icon: '⚽', color: 'text-gray-900' },
    { label: 'Marques', value: brands?.length || 0, icon: '👕', color: 'text-gray-900' },
    { label: 'Joueurs', value: players?.length || 0, icon: '👤', color: 'text-gray-900' },
    { label: 'Maillots', value: masterJerseys?.length || 0, icon: '📋', color: 'text-gray-900' }
  ];

  const recentTeams = teams?.slice(0, 6) || [];
  const recentBrands = brands?.slice(0, 4) || [];
  const recentMasterJerseys = masterJerseys?.slice(0, 12) || [];

  return (
    <div className="min-h-screen bg-white">
      
      {/* Hero Section - TopKit Narrative */}
      <div className="bg-white py-16 md:py-24">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Estimez votre collection<br />
            <span className="text-gray-600">de maillots de football</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Découvrez la valeur de vos maillots avec TopKit, 
            la base de données collaborative la plus complète du monde sur le football
          </p>
          
          {/* CTA Buttons - TopKit Focus */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button
              onClick={() => onViewChange('explore')}
              className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-full font-semibold transition-all text-lg"
            >
              Explorer la base
            </button>
            <button
              onClick={() => onViewChange('teams')}
              className="border border-gray-300 hover:border-gray-900 text-gray-900 hover:bg-gray-50 px-8 py-3 rounded-full font-semibold transition-all text-lg"
            >
              Documenter
            </button>
          </div>
        </div>
      </div>

      {/* Categories Carousel - Like WhenToCop top brands */}
      <div className="py-8 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex overflow-x-auto space-x-4 pb-4" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
            {recentTeams.map((team, index) => (
              <button
                key={team.id}
                onClick={() => onViewChange('teams')}
                className="flex-shrink-0 bg-white rounded-lg p-4 hover:shadow-md transition-all border border-gray-100 min-w-[120px]"
              >
                <div className="text-center">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span className="text-xl">⚽</span>
                  </div>
                  <div className="font-medium text-sm text-gray-900 truncate">{team.name}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Maillots les plus recherchés Section - TopKit Focus */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Maillots les plus recherchés</h2>
            <button
              onClick={() => onViewChange('master-jerseys')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              Tous les maillots
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterJerseys.map((jersey, index) => (
              <div
                key={jersey.id || index}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100"
                onClick={() => onViewChange('master-jerseys')}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center">
                  <span className="text-4xl">👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {jersey.team_info?.name || 'Équipe inconnue'}
                  </h3>
                  <p className="text-xs text-gray-500 mb-2">{jersey.season}</p>
                  <p className="text-sm font-semibold text-gray-900">
                    Valeur estimée<br />
                    <span className="text-lg">120€</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Les dernières contributions Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              Les dernières contributions à la base 🔥
            </h2>
            <button
              onClick={() => onViewChange('teams')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              Voir les contributions
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recentTeams.slice(0, 2).map((team, index) => (
              <div
                key={team.id}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group"
                onClick={() => onViewChange('teams')}
              >
                <div className="flex items-center p-6">
                  <div className="flex-shrink-0 mr-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                      <span className="text-2xl">⚽</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm text-gray-500 mb-1">
                      Jan
                      <br />
                      {15 + index}
                    </div>
                  </div>
                  <div className="flex-2">
                    <h3 className="font-semibold text-gray-900 mb-1">{team.name}</h3>
                    <p className="text-sm text-gray-500 mb-2">Nouvelle équipe documentée</p>
                    <p className="text-sm font-semibold text-gray-900">
                      <span className="text-green-600">+5 maillots référencés</span>
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Maillots rares et recherchés */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Maillots rares et recherchés</h2>
            <button
              onClick={() => onViewChange('master-jerseys')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              Voir plus de maillots rares
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterJerseys.slice(0, 6).map((jersey, index) => {
              const rareValues = [450, 680, 1200, 350, 890, 750];
              const rareValue = rareValues[index % 6];
              
              return (
                <div
                  key={jersey.id || index}
                  className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100 relative"
                  onClick={() => onViewChange('master-jerseys')}
                >
                  <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-bold">
                    RARE
                  </div>
                  <div className="aspect-square bg-gray-100 flex items-center justify-center">
                    <span className="text-4xl">👕</span>
                  </div>
                  <div className="p-3">
                    <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                      {jersey.team_info?.name || 'Équipe inconnue'}
                    </h3>
                    <div className="flex items-baseline space-x-2">
                      <span className="text-lg font-bold text-gray-900">{rareValue}€</span>
                      <span className="text-xs text-orange-600">Estimation</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Les dernières documentations */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
            Les dernières documentations 📋
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterJerseys.slice(0, 6).map((jersey, index) => (
              <div
                key={jersey.id || index}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100"
                onClick={() => onViewChange('master-jerseys')}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center">
                  <span className="text-4xl">👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {jersey.team_info?.name || 'Équipe inconnue'} {jersey.season}
                  </h3>
                  <p className="text-sm text-green-600">
                    <span className="text-lg font-bold">Documenté ✓</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Les marques du moment */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
            Les marques du moment
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {recentBrands.map((brand) => (
              <div
                key={brand.id}
                className="bg-gray-100 rounded-lg p-6 hover:shadow-md transition-all cursor-pointer group text-center"
                onClick={() => onViewChange('brands')}
              >
                <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <span className="text-2xl">👕</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{brand.name}</h3>
                <button className="text-sm text-gray-600 hover:text-black transition-colors">
                  Voir les maillots
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Newsletter Section - WhenToCop Style */}
      <div className="py-16 bg-black">
        <div className="max-w-4xl mx-auto px-4 text-center text-white">
          <div className="mb-6">
            <span className="text-4xl">🔥</span>
          </div>
          
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Sois le premier informé des dernières documentations et estimations exclusives
          </h2>
          <p className="text-lg opacity-90 mb-8">
            Rejoins notre newsletter pour recevoir les nouveaux maillots documentés, les estimations de valeurs et les infos exclusives de la communauté TopKit.
          </p>
          
          <div className="flex flex-col sm:flex-row max-w-md mx-auto gap-4">
            <input
              type="email"
              placeholder="Adresse e-mail"
              className="flex-1 px-4 py-3 rounded-full text-black focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button className="bg-white text-black px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors">
              S'abonner
            </button>
          </div>
          
          <p className="text-sm opacity-70 mt-4">
            En cliquant sur "S'abonner", tu acceptes les conditions générales de TopKit
          </p>
        </div>
      </div>

      {/* Footer Description */}
      <div className="py-8 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Achète tes maillots au meilleur prix
          </h3>
          <p className="text-gray-600 text-sm leading-relaxed">
            Avec TopKit, trouve des maillots de football pour toutes les équipes au meilleur prix ! 
            Compare les prix des marques comme Nike, Adidas, Puma, et Umbro pour dénicher la meilleure offre. 
            TopKit, c'est aussi une base de données collaborative complète pour ne rater aucun maillot. 
            Reçois des alertes en temps réel pour être parmi les premiers à connaître les nouvelles sorties, 
            et reste au courant des dernières news maillots et football pour ne rien manquer des tendances.
          </p>
        </div>
      </div>

    </div>
  );
};

export default CollaborativeHomepage;