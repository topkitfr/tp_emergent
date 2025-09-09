import React, { useState } from 'react';
import ProfilePictureModal from '../ProfilePictureModal';

const CollaborativeHeader = ({ 
  user, 
  currentView, 
  onViewChange, 
  onSearch, 
  onLogin, 
  onLogout, 
  searchQuery,
  onUserUpdate
}) => {
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showProfilePictureModal, setShowProfilePictureModal] = useState(false);

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  const handleSearchChange = (e) => {
    onSearch(e.target.value);
  };

  const navigationItems = [
    { id: 'home', label: 'Home', icon: '🏠', requiresAuth: false },
    { id: 'kit-area', label: 'Kit Area', icon: '👕', requiresAuth: false },
    { id: 'catalogue', label: 'Database', icon: '📚', requiresAuth: false },
    { id: 'contributions-v2', label: 'Contributions', icon: '🎯', requiresAuth: true }
  ];

  // Filter navigation items based on authentication
  const visibleNavigationItems = navigationItems.filter(item => 
    !item.requiresAuth || user
  );

  return (
    <>
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-full px-4 sm:px-6">
          <div className="flex justify-between items-center h-16">
          
          {/* Logo */}
          <div className="flex-shrink-0">
            <button
              onClick={() => onViewChange('home')}
              className="hover:opacity-80 transition-opacity"
            >
              <div className="flex items-center">
                <img 
                  src="https://customer-assets.emergentagent.com/job_kit-explorer/artifacts/uumlohms_topkit_logo.png" 
                  alt="TopKit Logo" 
                  className="h-5 w-auto"
                />
              </div>
            </button>
          </div>

          {/* Desktop Navigation - WhenToCop Style */}
          <nav className="hidden lg:flex space-x-8">
            {visibleNavigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`text-sm font-medium transition-colors ${
                  currentView === item.id
                    ? 'text-black font-semibold'
                    : 'text-gray-600 hover:text-black'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* Search Bar - WhenToCop Style */}
          <div className="hidden md:flex flex-1 max-w-xs mx-4 lg:mx-8">
            <div className="relative w-full">
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full bg-gray-50 border-0 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:bg-white placeholder-gray-500"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-2 lg:space-x-4">
            
            {/* User Menu or Login */}
            {user ? (
              <div className="relative">
                <div className="flex items-center space-x-2">
                  {/* Profile Picture - Display only */}
                  <div className="w-8 h-8 rounded-full overflow-hidden">
                    {user.profile_picture_url ? (
                      <img 
                        src={`${API}/${user.profile_picture_url}`}
                        alt="Profile"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div 
                      className="w-8 h-8 bg-black rounded-full flex items-center justify-center" 
                      style={{display: user.profile_picture_url ? 'none' : 'flex'}}
                    >
                      <span className="text-sm font-medium text-white">
                        {user.name?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                  </div>

                  {/* Dropdown Button */}
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center space-x-1 text-gray-700 hover:text-black transition-colors"
                  >
                    <span className="hidden xl:block font-medium">{user.name}</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>

                {/* User Dropdown - WhenToCop Style */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-2 z-50">
                    <button
                      onClick={() => {
                        onViewChange('profile');
                        setShowUserMenu(false);
                      }}
                      className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      My Profile
                    </button>
                    
                    <button
                      onClick={() => {
                        onViewChange('my-collection');
                        setShowUserMenu(false);
                      }}
                      className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      My Collection
                    </button>
                    
                    {user.role === 'admin' && (
                      <>
                        <button
                          onClick={() => {
                            onViewChange('admin');
                            setShowUserMenu(false);
                          }}
                          className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          Administration
                        </button>
                        <button
                          onClick={() => {
                            onViewChange('moderation');
                            setShowUserMenu(false);
                          }}
                          className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          🛡️ Moderation Dashboard
                        </button>
                      </>
                    )}
                    
                    <hr className="my-2 border-gray-100" />
                    <button
                      onClick={() => {
                        onLogout();
                        setShowUserMenu(false);
                      }}
                      className="block w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onLogin}
                className="bg-black hover:bg-gray-800 text-white px-3 lg:px-4 py-2 rounded-full text-sm font-medium transition-colors"
              >
                <span className="hidden sm:inline">Sign In</span>
                <span className="sm:hidden">Login</span>
              </button>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="lg:hidden p-2 text-gray-600 hover:text-black"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

          {/* Mobile Menu - WhenToCop Style */}
          {showMobileMenu && (
            <div className="lg:hidden bg-white border-t border-gray-100 py-4">
              {/* Mobile Search Bar */}
              <div className="px-4 pb-4 md:hidden">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                    className="w-full bg-gray-50 border-0 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:bg-white placeholder-gray-500"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="space-y-1">
                {visibleNavigationItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      onViewChange(item.id);
                      setShowMobileMenu(false);
                    }}
                    className={`block w-full text-left px-4 py-3 text-sm font-medium transition-all ${
                      currentView === item.id
                        ? 'text-black bg-gray-50 font-semibold'
                        : 'text-gray-600 hover:text-black hover:bg-gray-50'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
                
                {user && (
                  <>
                    <hr className="my-3 border-gray-100" />
                    <button
                      onClick={() => {
                        onLogout();
                        setShowMobileMenu(false);
                      }}
                      className="block w-full text-left px-4 py-3 text-sm font-medium text-red-600 hover:bg-red-50"
                    >
                      Sign Out
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Profile Picture Modal */}
      {showProfilePictureModal && (
        <ProfilePictureModal
          user={user}
          onClose={() => setShowProfilePictureModal(false)}
          onUpdate={onUserUpdate}
        />
      )}
    </>
  );
};

export default CollaborativeHeader;