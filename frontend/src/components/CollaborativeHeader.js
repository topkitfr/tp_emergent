import React, { useState } from 'react';

const CollaborativeHeader = ({ 
  user, 
  currentView, 
  onViewChange, 
  onSearch, 
  onLogin, 
  onLogout, 
  searchQuery 
}) => {
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearchChange = (e) => {
    onSearch(e.target.value);
  };

  const navigationItems = [
    { id: 'home', label: 'Accueil', icon: '🏠' },
    { id: 'explore', label: 'Explorer', icon: '🔍' },
    { id: 'teams', label: 'Équipes', icon: '⚽' },
    { id: 'brands', label: 'Marques', icon: '👕' },
    { id: 'players', label: 'Joueurs', icon: '👤' },
    { id: 'competitions', label: 'Compétitions', icon: '🏆' },
    { id: 'master-jerseys', label: 'Maillots', icon: '📋' }
  ];

  return (
    <header className="bg-white shadow-lg border-b-2 border-blue-600 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo */}
          <div className="flex-shrink-0">
            <button
              onClick={() => onViewChange('home')}
              className="hover:opacity-80 transition-opacity"
            >
              <div className="flex items-center space-x-2">
                <span className="text-2xl font-bold text-blue-600">TopKit</span>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium">
                  COLLABORATIVE
                </span>
              </div>
            </button>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex space-x-1">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentView === item.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>

          {/* Search Bar */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <input
                type="text"
                placeholder="Rechercher équipes, marques, joueurs..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full bg-gray-50 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            
            {/* Contributions Button */}
            {user && (
              <button
                onClick={() => onViewChange('contributions')}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentView === 'contributions'
                    ? 'bg-green-600 text-white'
                    : 'text-gray-600 hover:text-green-600 hover:bg-green-50'
                }`}
                title="Mes Contributions"
              >
                <span className="mr-1">📝</span>
                <span className="hidden md:inline">Contribuer</span>
              </button>
            )}

            {/* User Menu or Login */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user.name?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  </div>
                  <span className="hidden lg:block font-medium">{user.name}</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* User Dropdown */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50">
                    <button
                      onClick={() => {
                        onViewChange('profile');
                        setShowUserMenu(false);
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <span className="mr-2">👤</span>
                      Mon Profil
                    </button>
                    
                    {user.role === 'admin' && (
                      <button
                        onClick={() => {
                          onViewChange('admin');
                          setShowUserMenu(false);
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <span className="mr-2">⚙️</span>
                        Administration
                      </button>
                    )}
                    
                    <hr className="my-2 border-gray-200" />
                    <button
                      onClick={() => {
                        onLogout();
                        setShowUserMenu(false);
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <span className="mr-2">🚪</span>
                      Déconnexion
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onLogin}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Se connecter
              </button>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="lg:hidden p-2 text-gray-600 hover:text-blue-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {showMobileMenu && (
          <div className="lg:hidden bg-gray-50 border-t border-gray-200 py-4">
            <div className="space-y-2">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    onViewChange(item.id);
                    setShowMobileMenu(false);
                  }}
                  className={`block w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    currentView === item.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default CollaborativeHeader;