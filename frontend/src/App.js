import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import EditKitModal from './EditKitModal';

// Football data for suggestions - Kept for future use
// const LEAGUES_DATA = { ... }
// const SEASONS = [ ... ]

// Get the backend URL from environment variables
const API = process.env.REACT_APP_BACKEND_URL;

// AuthContext to manage user authentication globally
const AuthContext = createContext();

// AuthProvider component to wrap the app
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      if (token && userData) {
        const parsedUser = JSON.parse(userData);
        setUser({ ...parsedUser, token });
        console.log('User restored from localStorage:', parsedUser);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser({ ...userData, token });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Main App Content Component
const AppContent = () => {
  const { user, login, logout } = useAuth();
  
  // Check if we're on password reset page
  const isPasswordResetPage = window.location.pathname === '/reset-password' || 
                             window.location.search.includes('token=');
  
  // If on password reset page, render that component
  if (isPasswordResetPage) {
    return <PasswordResetPage />;
  }
  
  const [currentView, setCurrentView] = useState('home');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [jerseys, setJerseys] = useState([]);
  const [marketplaceItems, setMarketplaceItems] = useState([]);
  const [filters, setFilters] = useState({
    league: '',
    team: '',
    season: '',
    minPrice: '',
    maxPrice: '',
    availability: ''
  });
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSecurityModal, setShowSecurityModal] = useState(false);

  const [showJerseyEditor, setShowJerseyEditor] = useState(false);
  const [showJerseyDetailView, setShowJerseyDetailView] = useState(false);
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [editingJersey, setEditingJersey] = useState(null);
  const [showEditKitModal, setShowEditKitModal] = useState(false);
  const [selectedKitForEdit, setSelectedKitForEdit] = useState(null);
  const [userCollections, setUserCollections] = useState({
    owned: [],
    wanted: []
  });
  const [userSubmissions, setUserSubmissions] = useState([]);

  // Load data on mount and when user changes or view changes
  useEffect(() => {
    loadJerseys();
    loadMarketplace();
    if (user) {
      loadNotifications();
      loadUserCollections();
      loadUserSubmissions();
    }
  }, [user]);

  // Load collections when accessing profile view
  useEffect(() => {
    if (user && currentView === 'profile') {
      loadUserCollections();
    }
  }, [user, currentView]);

  // API Functions
  const loadJerseys = async () => {
    try {
      const response = await fetch(`${API}/api/jerseys/approved`);
      if (response.ok) {
        const data = await response.json();
        console.log('Jerseys loaded from API:', data);
        console.log('First jersey with photos check:', data.find(j => j.images && j.images.length > 0 || j.front_photo_url));
        setJerseys(data);
      }
    } catch (error) {
      console.error('Error loading jerseys:', error);
    }
  };

  const loadMarketplace = async () => {
    try {
      const response = await fetch(`${API}/api/marketplace/catalog`);
      if (response.ok) {
        const data = await response.json();
        setMarketplaceItems(data);
      }
    } catch (error) {
      console.error('Error loading marketplace:', error);
    }
  };

  const loadNotifications = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`${API}/api/notifications`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure notifications is always an array
        setNotifications(Array.isArray(data) ? data : []);
      } else {
        // If response is not ok, set empty array
        setNotifications([]);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
      // Ensure notifications is always an array even on error
      setNotifications([]);
    }
  };

  const loadUserCollections = async () => {
    if (!user) return;
    
    try {
      console.log('Loading user collections for user:', user.id);
      
      const response = await fetch(`${API}/api/users/${user.id}/collections`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      
      console.log('Collections API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Collections raw data received:', data);
        
        // Transform the data structure from {collections: [...]} to {owned: [...], wanted: [...]}
        const collections = data.collections || [];
        const transformedData = {
          owned: collections.filter(item => item.collection_type === 'owned'),
          wanted: collections.filter(item => item.collection_type === 'wanted')
        };
        
        console.log('Collections transformed data:', transformedData);
        setUserCollections(transformedData);
      } else {
        console.error('Failed to load collections:', response.status, await response.text());
        // Set empty collections on error
        setUserCollections({ owned: [], wanted: [] });
      }
    } catch (error) {
      console.error('Error loading user collections:', error);
      // Set empty collections on error
      setUserCollections({ owned: [], wanted: [] });
    }
  };

  const loadUserSubmissions = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`${API}/api/users/${user.id}/jerseys`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUserSubmissions(data);
      }
    } catch (error) {
      console.error('Error loading user submissions:', error);
    }
  };

  // Auth handlers
  const handleLoginSuccess = (token, userData) => {
    login(token, userData);
    // Reload data after login
    setTimeout(() => {
      loadNotifications();
      loadUserCollections();
      loadUserSubmissions();
    }, 500);
  };

  const handleLogout = () => {
    logout();
    setCurrentView('home');
    setNotifications([]);
    setUserCollections({ owned: [], wanted: [] });
    setUserSubmissions([]);
  };

  // UI handlers - Improved search
  const handleSearch = (term) => {
    setSearchTerm(term);
    
    // Si on tape quelque chose et qu'on appuie sur Entrée ou après un délai, rediriger vers exploration
    if (term.trim().length > 2 && currentView !== 'explore') {
      // Petit délai pour éviter de rediriger à chaque caractère tapé
      setTimeout(() => {
        if (searchTerm === term && term.trim().length > 2) {
          setCurrentView('explore');
        }
      }, 800); // 800ms de délai
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const clearFilters = () => {
    setFilters({
      league: '',
      team: '',
      season: '',
      minPrice: '',
      maxPrice: ''
    });
    setSearchTerm('');
  };

  const toggleCollectionItem = async (jersey, collectionType) => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    try {
      console.log('Adding to collection:', { jersey_id: jersey.id, collection_type: collectionType });
      
      const response = await fetch(`${API}/api/collections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          jersey_id: jersey.id,
          collection_type: collectionType
        })
      });

      const responseData = await response.json();
      console.log('Collection API response:', responseData);

      if (response.ok) {
        // Reload collections to get updated data
        await loadUserCollections();
        
        // Show success message
        const collectionTypeText = collectionType === 'owned' ? 'votre collection' : 'votre wishlist';
        const jerseyName = `${jersey.team || 'Maillot'} ${jersey.season || ''}`.trim();
        alert(`✅ ${jerseyName} ajouté à ${collectionTypeText} avec succès !`);
      } else {
        // Handle specific error messages
        const errorMsg = responseData.detail || `Erreur lors de l'ajout à ${collectionType === 'owned' ? 'la collection' : 'la wishlist'}`;
        alert(`❌ ${errorMsg}`);
        console.error('Collection API error:', response.status, responseData);
      }
    } catch (error) {
      console.error('Error toggling collection item:', error);
      alert('❌ Erreur de connexion lors de l\'ajout à la collection');
    }
  };

  const openJerseyEditor = (jersey) => {
    setEditingJersey(jersey);
    setShowJerseyEditor(true);
  };

  const openJerseyModal = (jersey) => {
    setSelectedJersey(jersey);
    setShowJerseyDetailView(true);
  };

  const handleJerseySubmit = () => {
    loadUserSubmissions();
  };

  const handleJerseyUpdate = () => {
    setShowJerseyEditor(false);
    setEditingJersey(null);
    loadUserSubmissions();
  };

  // Edit Kit Modal Functions
  const openEditKitModal = (jersey) => {
    setSelectedKitForEdit(jersey);
    setShowEditKitModal(true);
  };

  const closeEditKitModal = () => {
    setShowEditKitModal(false);
    setSelectedKitForEdit(null);
    // Reload jerseys to get updated data
    loadJerseys();
  };

  // Check if jersey is in user collection
  const isInCollection = (jerseyId, type) => {
    return userCollections[type]?.some(item => item.jersey_id === jerseyId);
  };

  // Collection management functions
  const handleEditCollectionItem = (item) => {
    console.log('Editing collection item:', item);
    // Create a jersey object with the collection data for the editor
    const jerseyWithCollectionData = {
      ...item.jersey,
      collection_id: item.id,
      collection_type: item.collection_type,
      size: item.size,
      condition: item.condition
    };
    setEditingJersey(jerseyWithCollectionData);
    setShowJerseyEditor(true);
  };

  const handleViewCollectionItem = (item) => {
    console.log('Viewing collection item:', item);
    // Set selected jersey for detailed view
    setSelectedJersey({
      ...item.jersey,
      collection_details: {
        collection_id: item.id,
        collection_type: item.collection_type,
        size: item.size,
        condition: item.condition,
        added_at: item.added_at
      }
    });
    setShowJerseyDetailView(true);
  };

  const handleRemoveCollectionItem = async (item, collectionType) => {
    if (!user) return;
    
    const confirmRemove = window.confirm(`Êtes-vous sûr de vouloir supprimer "${item.jersey?.team || 'ce maillot'}" de votre ${collectionType === 'owned' ? 'collection' : 'wishlist'} ?`);
    if (!confirmRemove) return;
    
    try {
      const response = await fetch(`${API}/api/collections/remove`, {
        method: 'POST', // Changed from DELETE to POST
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          jersey_id: item.jersey_id || item.jersey?.id, // Use jersey_id instead of collection_id
          collection_type: collectionType // Send collection_type as expected by backend
        })
      });

      const responseData = await response.json();

      if (response.ok) {
        // Reload collections to get updated data
        await loadUserCollections();
        alert(`✅ Maillot supprimé de votre ${collectionType === 'owned' ? 'collection' : 'wishlist'} !`);
      } else {
        const errorMsg = responseData.detail || `Erreur lors de la suppression`;
        alert(`❌ ${errorMsg}`);
        console.error('Remove collection item error:', response.status, responseData);
      }
    } catch (error) {
      console.error('Error removing collection item:', error);
      alert('❌ Erreur de connexion lors de la suppression');
    }
  };

  // Wishlist Tab Component with views and pagination
  const WishlistTabContent = () => {
    const [wishlistViewMode, setWishlistViewMode] = useState('grid');
    const [wishlistCurrentPage, setWishlistCurrentPage] = useState(1);
    const [wishlistItemsPerPage, setWishlistItemsPerPage] = useState(25);

    const wantedJerseys = userCollections.wanted || [];
    const totalItems = wantedJerseys.length;
    const totalPages = Math.ceil(totalItems / wishlistItemsPerPage);
    const startIndex = (wishlistCurrentPage - 1) * wishlistItemsPerPage;
    const currentItems = wantedJerseys.slice(startIndex, startIndex + wishlistItemsPerPage);

    return (
      <div>
        {/* Header with view controls */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-xl font-semibold text-black mb-1">Ma Wishlist</h3>
            <div className="text-sm text-gray-600">
              {totalItems} maillot{totalItems !== 1 ? 's' : ''} recherché{totalItems !== 1 ? 's' : ''}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setWishlistViewMode('grid')}
              className={`px-3 py-2 rounded ${wishlistViewMode === 'grid' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Grille
            </button>
            <button
              onClick={() => setWishlistViewMode('list')}
              className={`px-3 py-2 rounded ${wishlistViewMode === 'list' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Liste
            </button>
            <button
              onClick={() => setWishlistViewMode('thumbnail')}
              className={`px-3 py-2 rounded ${wishlistViewMode === 'thumbnail' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Vignette
            </button>
          </div>
        </div>

        {/* Wishlist content */}
        <div className="bg-white rounded-lg border border-gray-200">
          {currentItems.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {wantedJerseys.length === 0 ? (
                <>
                  <div className="text-4xl mb-2">⭐</div>
                  <p>Votre wishlist est vide</p>
                  <p className="text-sm">Ajoutez des maillots que vous recherchez</p>
                </>
              ) : (
                'Aucun résultat sur cette page'
              )}
            </div>
          ) : (
            <div className={`p-4 ${
              wishlistViewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 
              wishlistViewMode === 'thumbnail' ? 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3' :
              'space-y-4'
            }`}>
              {currentItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleViewCollectionItem(item)}
                  className={`cursor-pointer transition-shadow hover:shadow-md ${
                    wishlistViewMode === 'grid'
                      ? "bg-gray-50 rounded-lg overflow-hidden border border-gray-200"
                      : wishlistViewMode === 'thumbnail' 
                      ? "bg-gray-50 rounded-lg overflow-hidden border border-gray-200"
                      : "bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-center space-x-4"
                  }`}
                >
                  {wishlistViewMode === 'grid' ? (
                    <>
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        {(() => {
                          let imageUrl = null;
                          const jersey = item.jersey;
                          
                          if (jersey?.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          else if (jersey?.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey?.team || 'Maillot'} ${jersey?.season || ''}`}
                              className="w-full h-full object-cover"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-4xl">👕</div>
                          );
                        })()}
                        <div className="text-4xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-black mb-2">{item.jersey?.team || 'Équipe inconnue'}</h3>
                        <p className="text-sm text-gray-600 mb-1">{item.jersey?.league || 'Ligue inconnue'}</p>
                        <p className="text-sm text-gray-500 mb-2">{item.jersey?.season || 'Saison inconnue'}</p>
                        {item.jersey?.player && <p className="text-sm text-blue-600 mb-2">{item.jersey.player}</p>}
                        <div className="text-xs text-orange-600">
                          ⭐ En recherche
                        </div>
                      </div>
                    </>
                  ) : wishlistViewMode === 'thumbnail' ? (
                    <div className="aspect-square bg-white rounded-lg overflow-hidden border border-gray-200 relative">
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        {(() => {
                          let imageUrl = null;
                          const jersey = item.jersey;
                          
                          if (jersey?.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          else if (jersey?.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey?.team || 'Maillot'} ${jersey?.season || ''}`}
                              className="w-full h-full object-cover"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-3xl">👕</div>
                          );
                        })()}
                        <div className="text-3xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      {/* Overlay texte en bas */}
                      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white p-2">
                        <h3 className="text-xs font-semibold truncate leading-tight">{item.jersey?.team || 'Équipe'}</h3>
                        <p className="text-xs opacity-80 truncate leading-tight">⭐ Recherché</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-lg flex-shrink-0">
                        {(() => {
                          let imageUrl = null;
                          const jersey = item.jersey;
                          
                          if (jersey?.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          else if (jersey?.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey?.team || 'Maillot'} ${jersey?.season || ''}`}
                              className="w-full h-full object-cover rounded-lg"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-2xl">👕</div>
                          );
                        })()}
                        <div className="text-2xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-black mb-1">{item.jersey?.team || 'Équipe inconnue'}</h3>
                        <p className="text-sm text-gray-600 mb-1">
                          {item.jersey?.league || 'Ligue inconnue'} • {item.jersey?.season || 'Saison inconnue'}
                        </p>
                        {item.jersey?.player && <p className="text-sm text-blue-600 mb-1">{item.jersey.player}</p>}
                        <div className="text-xs text-orange-600">
                          ⭐ En recherche
                        </div>
                      </div>
                      <div className="flex flex-col space-y-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveCollectionItem(item, 'wanted');
                          }}
                          className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded transition-colors"
                          title="Supprimer de la wishlist"
                        >
                          Suppr
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalItems > wishlistItemsPerPage && (
            <div className="border-t border-gray-200">
              <PaginationControls
                currentPage={wishlistCurrentPage}
                totalItems={totalItems}
                itemsPerPage={wishlistItemsPerPage}
                onPageChange={setWishlistCurrentPage}
                onItemsPerPageChange={setWishlistItemsPerPage}
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  // Get unique leagues and teams for filters
  const availableLeagues = [...new Set(jerseys.map(j => j.league).filter(Boolean))];
  const availableTeams = filters.league 
    ? [...new Set(jerseys.filter(j => j.league === filters.league).map(j => j.team).filter(Boolean))]
    : [...new Set(jerseys.map(j => j.team).filter(Boolean))];

  // Header Component
  const Header = () => {
    const [showMobileMenu, setShowMobileMenu] = useState(false);

    return (
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <button
                onClick={() => setCurrentView('home')}
                className="hover:opacity-80 transition-opacity"
              >
                <img 
                  src="https://customer-assets.emergentagent.com/job_kit-explorer/artifacts/uumlohms_topkit_logo.png" 
                  alt="TOPKIT" 
                  className="h-4 md:h-5"
                />
              </button>
            </div>

            {/* Navigation Desktop */}
            <nav className="hidden md:flex space-x-8">
              <button
                onClick={() => setCurrentView('home')}
                className={`${currentView === 'home' 
                  ? 'text-black border-b-2 border-black' 
                  : 'text-gray-500 hover:text-black'
                } px-3 py-2 text-sm font-medium transition-colors`}
              >
                Home
              </button>
              <button
                onClick={() => {
                  console.log('Clicking Explorez button, setting currentView to explore');
                  setCurrentView('explore');
                }}
                className={`${currentView === 'explore' 
                  ? 'text-black border-b-2 border-black' 
                  : 'text-gray-500 hover:text-black'
                } px-3 py-2 text-sm font-medium transition-colors`}
              >
                Explorez
              </button>
              <button
                onClick={() => setCurrentView('marketplace')}
                className={`${currentView === 'marketplace' 
                  ? 'text-black border-b-2 border-black' 
                  : 'text-gray-500 hover:text-black'
                } px-3 py-2 text-sm font-medium transition-colors`}
              >
                Marketplace
              </button>
            </nav>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="text-gray-500 hover:text-black p-2"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {showMobileMenu ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>

            {/* Right side Desktop */}
            <div className="hidden md:flex items-center space-x-4">
              {/* Search */}
              <div>
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && searchTerm.trim().length > 0) {
                      setCurrentView('explore');
                    }
                  }}
                  className="bg-gray-50 text-black px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent w-64"
                />
              </div>

              {user ? (
                <div className="flex items-center space-x-3">
                  {/* Notifications */}
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="text-gray-500 hover:text-black relative p-2"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5zm-5-17h5l-5 5-5-5h5zm10 10v2a8 8 0 01-16 0V7a8 8 0 0116 0z" />
                    </svg>
                    {(notifications && Array.isArray(notifications) && notifications.filter(n => !n.read).length > 0) && (
                      <span className="absolute -top-1 -right-1 bg-black text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {notifications.filter(n => !n.read).length}
                      </span>
                    )}
                  </button>

                  {/* Admin Panel Button (Desktop) */}
                  {user.role === 'admin' && (
                    <button
                      onClick={() => setCurrentView('admin')}
                      className="text-gray-500 hover:text-black p-2 transition-colors"
                      title="Admin Panel"
                    >
                      <span className="text-lg">🔧</span>
                    </button>
                  )}

                  {/* Settings Button (Desktop) */}
                  <button
                    onClick={() => setShowSecurityModal(true)}
                    className="text-gray-500 hover:text-black p-2 transition-colors"
                    title="Settings"
                  >
                    <span className="text-lg">🔒</span>
                  </button>

                  {/* User Menu */}
                  <div className="relative">
                    <button
                      onClick={() => setCurrentView('profile')}
                      className="flex items-center text-gray-500 hover:text-black space-x-2"
                    >
                      <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-white">
                          {user.name?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      </div>
                      <span className="hidden lg:block">{user.name}</span>
                    </button>
                  </div>

                  <button
                    onClick={handleLogout}
                    className="text-gray-500 hover:text-black text-sm"
                  >
                    Déconnexion
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Se connecter
                </button>
              )}
            </div>
          </div>

          {/* Mobile Menu */}
          {showMobileMenu && (
            <div className="md:hidden bg-gray-50 border-t border-gray-200">
              <div className="px-2 pt-2 pb-3 space-y-1">
                {/* Navigation Links */}
                <button
                  onClick={() => {
                    setCurrentView('home');
                    setShowMobileMenu(false);
                  }}
                  className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    currentView === 'home' ? 'text-black bg-gray-200' : 'text-gray-500 hover:text-black hover:bg-gray-100'
                  }`}
                >
                  Home
                </button>
                <button
                  onClick={() => {
                    setCurrentView('explore');
                    setShowMobileMenu(false);
                  }}
                  className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    currentView === 'explore' ? 'text-black bg-gray-200' : 'text-gray-500 hover:text-black hover:bg-gray-100'
                  }`}
                >
                  Explorez
                </button>
                <button
                  onClick={() => {
                    setCurrentView('marketplace');
                    setShowMobileMenu(false);
                  }}
                  className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    currentView === 'marketplace' ? 'text-black bg-gray-200' : 'text-gray-500 hover:text-black hover:bg-gray-100'
                  }`}
                >
                  Marketplace
                </button>

                {/* User section */}
                {user ? (
                  <>
                    <button
                      onClick={() => {
                        setCurrentView('profile');
                        setShowMobileMenu(false);
                      }}
                      className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors ${
                        currentView === 'profile' ? 'text-black bg-gray-200' : 'text-gray-500 hover:text-black hover:bg-gray-100'
                      }`}
                    >
                      Mon Profil
                    </button>
                    {user.role === 'admin' && (
                      <>
                        <button
                          onClick={() => {
                            setCurrentView('admin');
                            setShowMobileMenu(false);
                          }}
                          className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-black hover:bg-gray-100"
                        >
                          Admin Panel
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => {
                        setShowSecurityModal(true);
                        setShowMobileMenu(false);
                      }}
                      className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-black hover:bg-gray-100"
                    >
                      Settings
                    </button>
                    {/* Séparateur avant déconnexion */}
                    <div className="pt-2 mt-2 border-t border-gray-200">
                      <button
                        onClick={() => {
                          handleLogout();
                          setShowMobileMenu(false);
                        }}
                        className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors"
                      >
                        Déconnexion
                      </button>
                    </div>
                  </>
                ) : (
                  <button
                    onClick={() => {
                      setShowAuthModal(true);
                      setShowMobileMenu(false);
                    }}
                    className="block w-full text-left px-3 py-2 rounded-md text-base font-medium bg-black text-white hover:bg-gray-800"
                  >
                    Se connecter
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Notifications Dropdown */}
        {showNotifications && user && (
          <div className="absolute right-4 top-16 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-black font-semibold">Notifications</h3>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {(notifications && Array.isArray(notifications) && notifications.length > 0) ? (
                notifications.slice(0, 10).map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 border-b border-gray-200 last:border-b-0 ${
                      !notification.read ? 'bg-gray-50' : ''
                    }`}
                  >
                    <div className="text-sm text-black font-medium mb-1">
                      {notification.title}
                    </div>
                    <div className="text-xs text-gray-600">
                      {notification.message}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      {new Date(notification.created_at).toLocaleString('fr-FR')}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-gray-400 text-center">
                  Aucune notification
                </div>
              )}
            </div>
          </div>
        )}
      </header>
    );
  };

  // Home Page Component - WhenToCop Style
  const HomePage = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 py-12 md:py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-black mb-6">
              Estimez votre collection de maillots
            </h1>
            <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              TopKit vous aide à estimer la valeur de votre collection de maillots de football. 
              Bientôt une marketplace et d'autres disciplines sportives !
            </p>
            
            {/* Search Bar */}
            <div className="max-w-md mx-auto mb-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Rechercher un maillot..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && searchTerm.trim().length > 0) {
                      setCurrentView('explore');
                    }
                  }}
                  className="w-full bg-white text-black px-6 py-4 rounded-lg border-2 border-gray-200 focus:outline-none focus:border-black text-lg"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-4">
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
              <button
                onClick={() => setCurrentView('explore')}
                className="bg-black hover:bg-gray-800 text-white px-8 py-4 rounded-lg text-lg font-medium transition-colors"
              >
                Explorez
              </button>
              <button
                onClick={() => setCurrentView('marketplace')}
                className="bg-white hover:bg-gray-50 text-black border-2 border-black px-8 py-4 rounded-lg text-lg font-medium transition-colors"
              >
                Marketplace
              </button>
              {user && (
                <button
                  onClick={() => setCurrentView('collection')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-medium transition-colors"
                >
                  Ma Collection
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Sports Disciplines */}
      <div className="bg-white py-8 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Disciplines disponibles</h3>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {['⚽ Football', '🏀 Basketball', '🏈 Rugby', '🏐 Volleyball', '🎾 Tennis', '🏒 Hockey'].map((sport) => (
              <div key={sport} className="text-lg font-medium text-gray-400 hover:text-gray-600 transition-colors cursor-pointer">
                {sport}
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-500 mt-4">Plus de disciplines bientôt disponibles</p>
        </div>
      </div>

      {/* Meilleures ventes Section */}
      <div className="py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-black">Maillots populaires</h2>
            <button 
              onClick={() => setCurrentView('explore')}
              className="text-black hover:underline font-medium"
            >
              Découvrir tous les maillots
            </button>
          </div>

          {/* Jersey Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 md:gap-6">
            {jerseys.slice(0, 6).map((jersey) => (
              <div key={jersey.id} className="bg-white rounded-lg overflow-hidden hover:shadow-lg transition-shadow border border-gray-200 cursor-pointer"
                   onClick={() => openJerseyModal(jersey)}>
                <div className="aspect-square bg-gray-100 flex items-center justify-center relative">
                  {(() => {
                    let imageUrl = null;
                    
                    if (jersey.images && jersey.images.length > 0) {
                      const img = jersey.images[0];
                      imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                    } else if (jersey.front_photo_url) {
                      const img = jersey.front_photo_url;
                      imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                    }
                    
                    return imageUrl ? (
                      <img 
                        src={imageUrl}
                        alt={jersey.team}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : (
                      <div className="text-4xl">👕</div>
                    );
                  })()}
                  <div className="w-full h-full flex items-center justify-center text-4xl" style={{display: 'none'}}>👕</div>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-black mb-1 truncate">{jersey.team}</h3>
                  <p className="text-xs text-gray-600">{jersey.league}</p>
                  <div className="mt-2">
                    <span className="text-sm font-bold text-black">Valeur estimée</span>
                    <div className="text-lg font-bold text-black">89€</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Hot Drops Section */}
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-black mb-8">Maillots récemment ajoutés ⚡</h2>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 md:gap-6">
            {jerseys.slice(6, 12).map((jersey) => (
              <div key={jersey.id} className="bg-white rounded-lg overflow-hidden hover:shadow-lg transition-shadow border border-gray-200 cursor-pointer"
                   onClick={() => openJerseyModal(jersey)}>
                <div className="aspect-square bg-gray-100 flex items-center justify-center relative">
                  {(() => {
                    let imageUrl = null;
                    
                    if (jersey.images && jersey.images.length > 0) {
                      const img = jersey.images[0];
                      imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                    } else if (jersey.front_photo_url) {
                      const img = jersey.front_photo_url;
                      imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                    }
                    
                    return imageUrl ? (
                      <img 
                        src={imageUrl}
                        alt={jersey.team}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : (
                      <div className="text-4xl">👕</div>
                    );
                  })()}
                  <div className="w-full h-full flex items-center justify-center text-4xl" style={{display: 'none'}}>👕</div>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-black mb-1 truncate">{jersey.team}</h3>
                  <p className="text-xs text-gray-600">{jersey.league}</p>
                  <div className="mt-2">
                    <span className="text-sm font-bold text-black">Valeur estimée</span>
                    <div className="text-lg font-bold text-black">127€</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Newsletter Section */}
      <div className="py-16 bg-black">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="text-4xl mb-4">🔥</div>
          <h2 className="text-3xl font-bold text-white mb-4">
            Restez informé des nouveautés TopKit
          </h2>
          <p className="text-gray-300 mb-8">
            Rejoignez notre communauté pour recevoir les dernières mises à jour sur les fonctionnalités,
            la marketplace et les nouvelles disciplines sportives !
          </p>
          
          <div className="max-w-md mx-auto flex">
            <input
              type="email"
              placeholder="Adresse e-mail"
              className="flex-1 px-4 py-3 rounded-l-lg border-none focus:outline-none"
            />
            <button className="bg-white text-black px-6 py-3 rounded-r-lg font-medium hover:bg-gray-100 transition-colors">
              S'abonner
            </button>
          </div>
          
          <p className="text-xs text-gray-400 mt-4">
            En cliquant sur "S'abonner", tu acceptes les conditions générales de TopKit
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white py-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <img 
                src="https://customer-assets.emergentagent.com/job_kit-explorer/artifacts/uumlohms_topkit_logo.png" 
                alt="TOPKIT" 
                className="h-8 mb-4"
              />
              <p className="text-gray-600 text-sm">
                L'outil d'estimation de collections pour passionnés de maillots sportifs
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-black mb-4">Explorer</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><button onClick={() => setCurrentView('explore')} className="hover:text-black">Tous les maillots</button></li>
                <li><button onClick={() => setCurrentView('marketplace')} className="hover:text-black">Marketplace</button></li>
                <li><button onClick={() => setCurrentView('collection')} className="hover:text-black">Ma Collection</button></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-black mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-black">Centre d'aide</a></li>
                <li><a href="#" className="hover:text-black">Contact</a></li>
                <li><a href="#" className="hover:text-black">CGV</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-black mb-4">Suivez-nous</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="https://www.instagram.com/topkit_fr" target="_blank" rel="noopener noreferrer" className="hover:text-black">Instagram</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-500">
              © 2025 TopKit. Tous droits réservés.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );

  // Explore Page Component with Pagination and Modal
  const ExplorePage = () => {
    const [viewMode, setViewMode] = useState('grid');
    const [filters, setFilters] = useState({
      league: '',
      team: '',
      season: ''
    });
    const [filteredJerseys, setFilteredJerseys] = useState([]);
    
    // Pagination states
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(25);
    
    // Modal state
    const [selectedJersey, setSelectedJersey] = useState(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
      applyFilters();
    }, [jerseys, filters]);

    const applyFilters = () => {
      let filtered = [...jerseys];
      
      // Recherche intelligente dans tous les champs pertinents
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        filtered = filtered.filter(jersey => {
          // Recherche dans les champs principaux
          const teamMatch = jersey.team?.toLowerCase().includes(searchLower);
          const leagueMatch = jersey.league?.toLowerCase().includes(searchLower);
          const seasonMatch = jersey.season?.toLowerCase().includes(searchLower);
          const playerMatch = jersey.player?.toLowerCase().includes(searchLower);
          
          // Recherche dans les champs techniques (soumission)
          const manufacturerMatch = jersey.manufacturer?.toLowerCase().includes(searchLower);
          const jerseyTypeMatch = jersey.jersey_type?.toLowerCase().includes(searchLower);
          const modelMatch = jersey.model?.toLowerCase().includes(searchLower);
          const descriptionMatch = jersey.description?.toLowerCase().includes(searchLower);
          const skuMatch = jersey.sku_code?.toLowerCase().includes(searchLower);
          const referenceMatch = jersey.reference_code?.toLowerCase().includes(searchLower);
          
          // Recherche dans les variantes d'équipes populaires
          const teamVariants = getTeamVariants(jersey.team?.toLowerCase() || '');
          const teamVariantMatch = teamVariants.some(variant => 
            variant.includes(searchLower) || searchLower.includes(variant)
          );
          
          return teamMatch || leagueMatch || seasonMatch || playerMatch || 
                 manufacturerMatch || jerseyTypeMatch || modelMatch || 
                 descriptionMatch || skuMatch || referenceMatch || teamVariantMatch;
        });
      }
      
      // Filtres spécifiques
      if (filters.league) {
        filtered = filtered.filter(jersey => 
          jersey.league?.toLowerCase().includes(filters.league.toLowerCase())
        );
      }
      
      if (filters.team) {
        filtered = filtered.filter(jersey => 
          jersey.team?.toLowerCase().includes(filters.team.toLowerCase())
        );
      }
      
      if (filters.season) {
        filtered = filtered.filter(jersey => 
          jersey.season?.includes(filters.season)
        );
      }
      
      setFilteredJerseys(filtered);
      setCurrentPage(1);
    };

    // Helper function pour les variantes d'équipes
    const getTeamVariants = (teamName) => {
      const variants = {
        'psg': ['paris saint germain', 'paris st germain', 'paris sg'],
        'paris saint germain': ['psg', 'paris sg', 'paris st germain'],
        'real madrid': ['real', 'madrid', 'rm'],
        'fc barcelona': ['barcelona', 'barca', 'fcb', 'fc barcelone'],
        'manchester united': ['man united', 'man utd', 'united', 'mu'],
        'manchester city': ['man city', 'city', 'mcfc'],
        'liverpool': ['lfc', 'liverpool fc'],
        'bayern munich': ['bayern', 'fcb munich', 'fc bayern'],
        'juventus': ['juve', 'juventus fc'],
        'ac milan': ['milan', 'ac milano'],
        'inter milan': ['inter', 'inter milano', 'internazionale'],
        'arsenal': ['arsenal fc', 'gunners'],
        'chelsea': ['chelsea fc', 'blues'],
        'tottenham': ['spurs', 'tottenham hotspur'],
        'olympique de marseille': ['om', 'marseille', 'olympique marseille'],
        'olympique lyonnais': ['ol', 'lyon', 'olympique lyon'],
        'as monaco': ['monaco', 'asm'],
        'atletico madrid': ['atletico', 'atleti'],
        'borussia dortmund': ['dortmund', 'bvb'],
        'ajax': ['ajax amsterdam', 'afc ajax']
      };
      
      return variants[teamName] || [teamName];
    };

    const handleFilterChange = (filterType, value) => {
      setFilters(prev => ({
        ...prev,
        [filterType]: value
      }));
    };

    const handleJerseyAction = async (action, jersey) => {
      switch (action) {
        case 'addToWishlist':
          try {
            const response = await fetch(`${API}/api/wishlist`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
              body: JSON.stringify({ jersey_id: jersey.id })
            });
            if (response.ok) {
              // Success notification could be added here
              console.log('Added to wishlist');
            }
          } catch (error) {
            console.error('Error adding to wishlist:', error);
          }
          break;
        case 'addToCollection':
          // Open collection editor modal or navigate to collection page
          console.log('Add to collection:', jersey);
          break;
      }
      setShowModal(false);
    };

    const openJerseyModal = (jersey) => {
      setSelectedJersey(jersey);
      setShowModal(true);
    };

    // Pagination calculations
    const totalItems = filteredJerseys.length;
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentItems = filteredJerseys.slice(startIndex, endIndex);

    return (
      <div className="max-w-7xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-6 text-black">Explorez les maillots</h1>
        
        {/* Filtres */}
        <div className="bg-white rounded-lg p-4 mb-6 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Championnat</label>
              <input
                type="text"
                value={filters.league}
                onChange={(e) => handleFilterChange('league', e.target.value)}
                placeholder="Ex: Ligue 1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Équipe</label>
              <input
                type="text"
                value={filters.team}
                onChange={(e) => handleFilterChange('team', e.target.value)}
                placeholder="Ex: PSG"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Saison</label>
              <input
                type="text"
                value={filters.season}
                onChange={(e) => handleFilterChange('season', e.target.value)}
                placeholder="Ex: 2024/25"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ league: '', team: '', season: '' })}
                className="px-4 py-2 text-gray-600 hover:text-black transition-colors"
              >
                Réinitialiser
              </button>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-between items-center mb-6">
          <div className="text-sm text-gray-600">
            {totalItems} maillot{totalItems !== 1 ? 's' : ''} trouvé{totalItems !== 1 ? 's' : ''}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 rounded ${viewMode === 'grid' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Grille
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 rounded ${viewMode === 'list' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Liste
            </button>
            <button
              onClick={() => setViewMode('thumbnail')}
              className={`px-3 py-2 rounded ${viewMode === 'thumbnail' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Vignette
            </button>
          </div>
        </div>

        {/* Liste des maillots */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {currentItems.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {jerseys.length === 0 ? 'Aucun maillot disponible' : 'Aucun résultat trouvé'}
            </div>
          ) : (
            <div className={`p-4 ${
              viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 
              viewMode === 'thumbnail' ? 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3' :
              'space-y-4'
            }`}>
              {currentItems.map((jersey) => {
                // Debug log pour vérifier les données du maillot
                if (jersey.images && jersey.images.length > 0 || jersey.front_photo_url) {
                  console.log('Jersey with photos:', jersey.team, {
                    images: jersey.images,
                    front_photo_url: jersey.front_photo_url,
                    back_photo_url: jersey.back_photo_url
                  });
                }
                
                return (
                <div
                  key={jersey.id}
                  className={`transition-shadow hover:shadow-md relative group ${
                    viewMode === 'grid'
                      ? "bg-white rounded-lg overflow-hidden border border-gray-200"
                      : viewMode === 'thumbnail' 
                      ? "bg-white rounded-lg overflow-hidden border border-gray-200"
                      : "bg-white rounded-lg p-4 border border-gray-200 flex items-center space-x-4"
                  }`}
                >
                  {viewMode === 'grid' ? (
                    <>
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        {/* Solution robuste multi-formats pour affichage d'images */}
                        {(() => {
                          let imageUrl = null;
                          
                          // Priorité 1: Format images array
                          if (jersey.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          // Priorité 2: Format front_photo_url
                          else if (jersey.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey.team} ${jersey.season}`}
                              className="w-full h-full object-cover"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-4xl">👕</div>
                          );
                        })()}
                        <div className="text-4xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-black mb-2">{jersey.team}</h3>
                        <p className="text-sm text-gray-600 mb-2">{jersey.league}</p>
                        <p className="text-sm text-gray-500">{jersey.season}</p>
                        {jersey.player && <p className="text-sm text-blue-600 mt-1">{jersey.player}</p>}
                      </div>
                    </>
                  ) : viewMode === 'thumbnail' ? (
                    <div className="aspect-square bg-white rounded-lg overflow-hidden border border-gray-200 relative">
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        {(() => {
                          let imageUrl = null;
                          
                          if (jersey.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          else if (jersey.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey.team} ${jersey.season}`}
                              className="w-full h-full object-cover"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-3xl">👕</div>
                          );
                        })()}
                        <div className="text-3xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      {/* Overlay texte en bas */}
                      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white p-2">
                        <h3 className="text-xs font-semibold truncate leading-tight">{jersey.team}</h3>
                        <p className="text-xs opacity-80 truncate leading-tight">{jersey.season}</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-lg flex-shrink-0">
                        {(() => {
                          let imageUrl = null;
                          
                          if (jersey.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          else if (jersey.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey.team} ${jersey.season}`}
                              className="w-full h-full object-cover rounded-lg"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-2xl">👕</div>
                          );
                        })()}
                        <div className="text-2xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-black mb-1">{jersey.team}</h3>
                        <p className="text-sm text-gray-600">{jersey.league} • {jersey.season}</p>
                        {jersey.player && <p className="text-sm text-blue-600">{jersey.player}</p>}
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => toggleCollectionItem(jersey, 'owned')}
                          className="text-xs bg-gray-100 text-gray-600 px-3 py-2 rounded hover:bg-gray-200"
                        >
                          Own
                        </button>
                        <button 
                          onClick={() => toggleCollectionItem(jersey, 'wanted')}
                          className="text-xs bg-gray-100 text-gray-600 px-3 py-2 rounded hover:bg-gray-200"
                        >
                          Want
                        </button>
                      </div>
                    </>
                  )}
                </div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {totalItems > itemsPerPage && (
            <PaginationControls
              currentPage={currentPage}
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
              onPageChange={setCurrentPage}
              onItemsPerPageChange={setItemsPerPage}
              itemName="maillots"
            />
          )}
        </div>

        {/* Modal détails */}
        <JerseyDetailModal
          jersey={selectedJersey}
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          context="explorer"
          onAction={handleJerseyAction}
        />
      </div>
    );
  };

  // Marketplace Component - Coming Soon
  const MarketplacePage = () => (
    <div className="min-h-screen bg-gray-50 text-black p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-16 md:py-24">
          <div className="text-6xl md:text-8xl mb-6">🏗️</div>
          <h1 className="text-3xl md:text-4xl font-bold text-black mb-4">
            Marketplace
          </h1>
          <h2 className="text-xl md:text-2xl font-semibold text-black mb-6">
            Bientôt disponible
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Notre marketplace arrive bientôt ! Vous pourrez acheter et vendre vos maillots 
            de football en toute sécurité avec d'autres collectionneurs.
          </p>
          
          <div className="bg-white p-8 rounded-lg max-w-2xl mx-auto border border-gray-200 shadow-sm">
            <h3 className="text-xl font-semibold text-black mb-6">
              Fonctionnalités à venir :
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
              <div className="flex items-start space-x-3">
                <span className="text-black text-xl">🛒</span>
                <div>
                  <h4 className="font-medium text-black">Achat sécurisé</h4>
                  <p className="text-sm text-gray-600">Transactions protégées</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-black text-xl">💰</span>
                <div>
                  <h4 className="font-medium text-black">Vente facile</h4>
                  <p className="text-sm text-gray-600">Listez vos maillots</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-black text-xl">🔍</span>
                <div>
                  <h4 className="font-medium text-black">Recherche avancée</h4>
                  <p className="text-sm text-gray-600">Filtres par équipe, saison</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-black text-xl">📱</span>
                <div>
                  <h4 className="font-medium text-black">Chat intégré</h4>
                  <p className="text-sm text-gray-600">Communication directe</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-black text-xl">⭐</span>
                <div>
                  <h4 className="font-medium text-black">Système de notes</h4>
                  <p className="text-sm text-gray-600">Vendeurs vérifiés</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-black text-xl">🚚</span>
                <div>
                  <h4 className="font-medium text-black">Suivi des envois</h4>
                  <p className="text-sm text-gray-600">Livraison trackée</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-8">
            <button
              onClick={() => setCurrentView('explore')}
              className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-lg font-medium transition-colors mr-4"
            >
              Découvrir les maillots
            </button>
            <button
              onClick={() => setCurrentView('home')}
              className="bg-white hover:bg-gray-50 text-black border-2 border-gray-200 px-8 py-3 rounded-lg font-medium transition-colors"
            >
              Retour à l'accueil
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Collection Tab Component with views and pagination
  const CollectionTabContent = () => {
    const [collectionViewMode, setCollectionViewMode] = useState('grid');
    const [collectionCurrentPage, setCollectionCurrentPage] = useState(1);
    const [collectionItemsPerPage, setCollectionItemsPerPage] = useState(25);

    const ownedJerseys = userCollections.owned || [];
    const totalItems = ownedJerseys.length;
    const totalPages = Math.ceil(totalItems / collectionItemsPerPage);
    const startIndex = (collectionCurrentPage - 1) * collectionItemsPerPage;
    const currentItems = ownedJerseys.slice(startIndex, startIndex + collectionItemsPerPage);

    return (
      <div>
        {/* Header with view controls */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-xl font-semibold text-black mb-1">Ma Collection</h3>
            <div className="text-sm text-gray-600">
              {totalItems} maillot{totalItems !== 1 ? 's' : ''} possédé{totalItems !== 1 ? 's' : ''}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCollectionViewMode('grid')}
              className={`px-3 py-2 rounded ${collectionViewMode === 'grid' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Grille
            </button>
            <button
              onClick={() => setCollectionViewMode('list')}
              className={`px-3 py-2 rounded ${collectionViewMode === 'list' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Liste
            </button>
            <button
              onClick={() => setCollectionViewMode('thumbnail')}
              className={`px-3 py-2 rounded ${collectionViewMode === 'thumbnail' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600'}`}
            >
              Vignette
            </button>
          </div>
        </div>

        {/* Collection content */}
        <div className="bg-white rounded-lg border border-gray-200">
          {currentItems.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {ownedJerseys.length === 0 ? (
                <>
                  <div className="text-4xl mb-2">👕</div>
                  <p>Votre collection est vide</p>
                  <p className="text-sm">Ajoutez vos premiers maillots à votre collection</p>
                </>
              ) : (
                'Aucun résultat sur cette page'
              )}
            </div>
          ) : (
            <div className={`p-4 ${
              collectionViewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 
              collectionViewMode === 'thumbnail' ? 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3' :
              'space-y-4'
            }`}>
              {currentItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleViewCollectionItem(item)}
                  className={`cursor-pointer transition-shadow hover:shadow-md ${
                    collectionViewMode === 'grid'
                      ? "bg-gray-50 rounded-lg overflow-hidden border border-gray-200"
                      : collectionViewMode === 'thumbnail' 
                      ? "bg-gray-50 rounded-lg overflow-hidden border border-gray-200"
                      : "bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-center space-x-4"
                  }`}
                >
                  {collectionViewMode === 'grid' ? (
                    <>
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        {(() => {
                          let imageUrl = null;
                          const jersey = item.jersey;
                          
                          if (jersey?.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          else if (jersey?.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `${API}/${img}` : `${API}/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey?.team || 'Maillot'} ${jersey?.season || ''}`}
                              className="w-full h-full object-cover"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-4xl">👕</div>
                          );
                        })()}
                        <div className="text-4xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-black mb-2">{item.jersey?.team || 'Équipe inconnue'}</h3>
                        <p className="text-sm text-gray-600 mb-1">{item.jersey?.league || 'Ligue inconnue'}</p>
                        <p className="text-sm text-gray-500 mb-2">{item.jersey?.season || 'Saison inconnue'}</p>
                        {item.jersey?.player && <p className="text-sm text-blue-600 mb-2">{item.jersey.player}</p>}
                        <div className="text-xs text-gray-500">
                          Taille: {item.size} • État: {item.condition}
                        </div>
                      </div>
                    </>
                  ) : collectionViewMode === 'thumbnail' ? (
                    <div className="aspect-square bg-white rounded-lg overflow-hidden border border-gray-200 relative">
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        {(() => {
                          let imageUrl = null;
                          const jersey = item.jersey;
                          
                          if (jersey?.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
                          }
                          else if (jersey?.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey?.team || 'Maillot'} ${jersey?.season || ''}`}
                              className="w-full h-full object-cover"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-3xl">👕</div>
                          );
                        })()}
                        <div className="text-3xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      {/* Overlay texte en bas */}
                      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white p-2">
                        <h3 className="text-xs font-semibold truncate leading-tight">{item.jersey?.team || 'Équipe'}</h3>
                        <p className="text-xs opacity-80 truncate leading-tight">Taille: {item.size}</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-lg flex-shrink-0">
                        {(() => {
                          let imageUrl = null;
                          const jersey = item.jersey;
                          
                          if (jersey?.images && jersey.images.length > 0) {
                            const img = jersey.images[0];
                            imageUrl = img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
                          }
                          else if (jersey?.front_photo_url) {
                            const img = jersey.front_photo_url;
                            imageUrl = img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
                          }
                          
                          return imageUrl ? (
                            <img 
                              src={imageUrl}
                              alt={`${jersey?.team || 'Maillot'} ${jersey?.season || ''}`}
                              className="w-full h-full object-cover rounded-lg"
                              style={{aspectRatio: '1'}}
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="text-2xl">👕</div>
                          );
                        })()}
                        <div className="text-2xl w-full h-full flex items-center justify-center" style={{display: 'none'}}>👕</div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-black mb-1">{item.jersey?.team || 'Équipe inconnue'}</h3>
                        <p className="text-sm text-gray-600 mb-1">
                          {item.jersey?.league || 'Ligue inconnue'} • {item.jersey?.season || 'Saison inconnue'}
                        </p>
                        {item.jersey?.player && <p className="text-sm text-blue-600 mb-1">{item.jersey.player}</p>}
                        <div className="text-xs text-gray-500">
                          Taille: {item.size} • État: {item.condition}
                        </div>
                      </div>
                      <div className="flex flex-col space-y-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveCollectionItem(item, 'owned');
                          }}
                          className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded transition-colors"
                          title="Supprimer de ma collection"
                        >
                          Suppr
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalItems > collectionItemsPerPage && (
            <div className="border-t border-gray-200">
              <PaginationControls
                currentPage={collectionCurrentPage}
                totalItems={totalItems}
                itemsPerPage={collectionItemsPerPage}
                onPageChange={setCollectionCurrentPage}
                onItemsPerPageChange={setCollectionItemsPerPage}
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  // Profile Page Component
  const ProfilePage = () => {
    const [activeTab, setActiveTab] = useState('collection');

    const renderTabContent = () => {
      switch (activeTab) {
        case 'collection':
          return (
            <CollectionTabContent />
          );

        case 'wishlist':
          return (
            <WishlistTabContent />
          );

        case 'submissions':
          return (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-black">Mes Soumissions</h3>
                <button
                  onClick={() => {
                    setEditingJersey({
                      team: '',
                      league: '',
                      season: '',
                      jersey_type: '',
                      manufacturer: '',
                      sku_code: '',
                      model: 'authentic',
                      description: '',
                      isNewSubmission: true
                    });
                    setShowJerseyEditor(true);
                  }}
                  className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Soumettre un maillot
                </button>
              </div>

              {/* Submissions List */}
              {userSubmissions && userSubmissions.length > 0 ? (
                <div className="space-y-4">
                  {userSubmissions.map((submission) => (
                    <div key={submission.id} className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="font-medium text-black mb-1">
                            {submission.team} - {submission.season}
                          </div>
                          <div className="text-sm text-gray-600 mb-1">
                            {submission.league}
                          </div>
                          <div className="text-sm text-gray-500">
                            Référence: {submission.reference_code}
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                            submission.status === 'approved' ? 'bg-green-100 text-green-800' :
                            submission.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {submission.status === 'approved' ? 'Approuvé' :
                             submission.status === 'rejected' ? 'Refusé' : 'En attente'}
                          </span>
                          <div className="text-xs text-gray-500 mt-1">
                            {new Date(submission.created_at).toLocaleDateString('fr-FR')}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📝</div>
                  <p>Aucune soumission pour le moment</p>
                  <p className="text-sm">Soumettez votre premier maillot pour commencer</p>
                </div>
              )}
            </div>
          );

        case 'listings':
          return (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏗️</div>
              <h3 className="text-xl font-semibold text-black mb-2">
                Bientôt disponible
              </h3>
              <p className="text-gray-600 mb-6">
                La fonctionnalité de vente sera bientôt disponible.
              </p>
            </div>
          );

        case 'messages':
          return (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏗️</div>
              <h3 className="text-xl font-semibold text-black mb-2">
                Bientôt disponible
              </h3>
              <p className="text-gray-600 mb-6">
                Le système de messagerie sera bientôt disponible.
              </p>
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div className="min-h-screen bg-gray-50 text-black p-4">
        <div className="max-w-4xl mx-auto">
          {/* Profile Header */}
          <div className="bg-white p-6 md:p-8 rounded-lg mb-6 md:mb-8 border border-gray-200">
            <div className="flex items-center space-x-6 mb-6">
              <div className="w-16 md:w-20 h-16 md:h-20 bg-black rounded-full flex items-center justify-center">
                <span className="text-xl md:text-2xl font-bold text-white">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-black">{user?.name || 'Utilisateur'}</h1>
                <p className="text-base md:text-lg text-gray-600">
                  {user?.email || 'email@example.com'}
                </p>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl md:text-3xl font-bold text-black">
                  {userCollections.owned?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Possédés</div>
              </div>
              <div>
                <div className="text-2xl md:text-3xl font-bold text-black">
                  {userCollections.wanted?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Recherches</div>
              </div>
              <div>
                <div className="text-2xl md:text-3xl font-bold text-black">
                  {userSubmissions?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Soumissions</div>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="mb-6 md:mb-8">
            <nav className="flex flex-wrap gap-2 md:gap-4">
              {[
                { id: 'collection', label: 'Ma Collection', icon: '👕' },
                { id: 'wishlist', label: 'Wishlist', icon: '⭐' },
                { id: 'submissions', label: 'Mes Soumissions', icon: '📝' },
                { id: 'listings', label: 'Mes Annonces', icon: '🏪' },
                { id: 'messages', label: 'Messagerie', icon: '💬' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 md:px-6 py-2 md:py-3 rounded-lg transition-colors text-sm md:text-base ${
                    activeTab === tab.id
                      ? 'bg-black text-white'
                      : 'bg-white text-gray-600 hover:text-black hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span className="text-sm md:text-base">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-lg p-6 md:p-8 border border-gray-200">
            {renderTabContent()}
          </div>
        </div>
      </div>
    );
  };

  // Admin Panel Component avec fonctionnalités complètes
  const AdminPanel = () => {
    const [adminActiveTab, setAdminActiveTab] = useState('jerseys');
    const [pendingJerseys, setPendingJerseys] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
    const [allJerseys, setAllJerseys] = useState([]);
    const [loading, setLoading] = useState(false);
    const [clearingData, setClearingData] = useState(false);

    // Load admin data
    useEffect(() => {
      if (user?.role === 'admin') {
        loadAdminData();
      }
    }, [user, adminActiveTab]);

    const loadAdminData = async () => {
      if (!user) return;
      setLoading(true);

      try {
        if (adminActiveTab === 'jerseys') {
          // Load pending jerseys
          const pendingResponse = await fetch(`${API}/api/admin/jerseys/pending`, {
            headers: { 'Authorization': `Bearer ${user.token}` }
          });
          if (pendingResponse.ok) {
            const data = await pendingResponse.json();
            setPendingJerseys(Array.isArray(data) ? data : []);
          } else {
            setPendingJerseys([]);
          }

          // Load all approved jerseys
          const jerseysResponse = await fetch(`${API}/api/jerseys`, {
            headers: { 'Authorization': `Bearer ${user.token}` }
          });
          if (jerseysResponse.ok) {
            const data = await jerseysResponse.json();
            setAllJerseys(Array.isArray(data) ? data : []);
          } else {
            setAllJerseys([]);
          }
        } else if (adminActiveTab === 'users') {
          // Load all users
          const usersResponse = await fetch(`${API}/api/admin/users`, {
            headers: { 'Authorization': `Bearer ${user.token}` }
          });
          if (usersResponse.ok) {
            const data = await usersResponse.json();
            // Ensure data is an array
            setAllUsers(Array.isArray(data) ? data : []);
          } else {
            // Set empty array on error
            setAllUsers([]);
          }
        }
      } catch (error) {
        console.error('Error loading admin data:', error);
      } finally {
        setLoading(false);
      }
    };

    // Admin actions for jerseys
    const approveJersey = async (jerseyId) => {
      try {
        const response = await fetch(`${API}/api/admin/jerseys/${jerseyId}/approve`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });
        if (response.ok) {
          alert('✅ Maillot approuvé avec succès');
          loadAdminData();
        } else {
          alert('❌ Erreur lors de l\'approbation');
        }
      } catch (error) {
        console.error('Error approving jersey:', error);
        alert('❌ Erreur de connexion');
      }
    };

    const rejectJersey = async (jerseyId) => {
      const reason = prompt('Raison du rejet (optionnel):');
      try {
        const response = await fetch(`${API}/api/admin/jerseys/${jerseyId}/reject`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${user.token}`
          },
          body: JSON.stringify({ reason })
        });
        if (response.ok) {
          alert('✅ Maillot rejeté');
          loadAdminData();
        } else {
          alert('❌ Erreur lors du rejet');
        }
      } catch (error) {
        console.error('Error rejecting jersey:', error);
        alert('❌ Erreur de connexion');
      }
    };

    const suggestModification = async (jersey) => {
      // Open jersey editor with the jersey data for modification
      console.log('Opening jersey for modification:', jersey);
      
      // Map old jersey structure to new structure
      const mappedJersey = {
        ...jersey,
        // Ensure new structure fields exist
        model: jersey.model || 'authentic', // Default to authentic if missing
        sku_code: jersey.sku_code || jersey.reference_code || '', // Map old reference_code to sku_code
        // Remove old fields that might cause conflicts
        player: undefined,
        reference_code: undefined,
        images: undefined,
        home_away: undefined,
        isAdminEdit: true // Flag to indicate this is an admin edit
      };
      
      console.log('Mapped jersey for editor:', mappedJersey);
      setEditingJersey(mappedJersey);
      setShowJerseyEditor(true);
    };

    const deleteJersey = async (jerseyId, jerseyName) => {
      const confirm = window.confirm(`Êtes-vous sûr de vouloir supprimer le maillot "${jerseyName}" ? Cette action est irréversible.`);
      if (!confirm) return;

      try {
        const response = await fetch(`${API}/api/admin/jerseys/${jerseyId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });
        if (response.ok) {
          alert('✅ Maillot supprimé de l\'explorateur');
          loadAdminData();
        } else {
          alert('❌ Erreur lors de la suppression');
        }
      } catch (error) {
        console.error('Error deleting jersey:', error);
        alert('❌ Erreur de connexion');
      }
    };

    // Admin actions for users
    const banUser = async (userId, userName) => {
      const reason = prompt(`Raison du bannissement de ${userName}:`);
      if (!reason) return;

      try {
        const response = await fetch(`${API}/api/admin/users/${userId}/ban`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${user.token}`
          },
          body: JSON.stringify({ reason })
        });
        if (response.ok) {
          alert(`✅ ${userName} a été banni`);
          loadAdminData();
        } else {
          alert('❌ Erreur lors du bannissement');
        }
      } catch (error) {
        console.error('Error banning user:', error);
        alert('❌ Erreur de connexion');
      }
    };

    const deleteUser = async (userId, userName) => {
      const confirm = window.confirm(`Êtes-vous sûr de vouloir supprimer le compte de ${userName} ? Cette action est irréversible et supprimera toutes ses données.`);
      if (!confirm) return;

      try {
        const response = await fetch(`${API}/api/admin/users/${userId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });
        if (response.ok) {
          alert(`✅ Compte de ${userName} supprimé`);
          loadAdminData();
        } else {
          alert('❌ Erreur lors de la suppression');
        }
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('❌ Erreur de connexion');
      }
    };

    // Data management functions
    const clearAllMasterKits = async () => {
      const confirm = window.confirm(
        '🚨 ATTENTION: Cette action va supprimer TOUS les Master Kits de la base de données.\n\n' +
        'Cela inclut:\n' +
        '- Tous les Master Kits\n' +
        '- Toutes les références de la base de données\n\n' +
        'Cette action est IRRÉVERSIBLE.\n\n' +
        'Êtes-vous absolument sûr de vouloir continuer ?'
      );
      if (!confirm) return;

      setClearingData(true);
      try {
        const response = await fetch(`${API}/api/admin/clear-master-kits`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });

        if (response.ok) {
          const result = await response.json();
          alert(`✅ Suppression réussie!\n\n` +
                `Master Kits supprimés: ${result.deleted_count}\n` +
                `Total avant suppression: ${result.count_before}`);
        } else {
          alert('❌ Erreur lors de la suppression des Master Kits');
        }
      } catch (error) {
        console.error('Error clearing master kits:', error);
        alert('❌ Erreur de connexion');
      } finally {
        setClearingData(false);
      }
    };

    const clearAllPersonalCollections = async () => {
      const confirm = window.confirm(
        '🚨 ATTENTION: Cette action va supprimer TOUTES les collections personnelles de la base de données.\n\n' +
        'Cela inclut:\n' +
        '- Toutes les collections personnelles des utilisateurs\n' +
        '- Tous les détails personnels ajoutés\n' +
        '- Toutes les estimations de prix personnalisées\n\n' +
        'Cette action est IRRÉVERSIBLE.\n\n' +
        'Êtes-vous absolument sûr de vouloir continuer ?'
      );
      if (!confirm) return;

      setClearingData(true);
      try {
        const response = await fetch(`${API}/api/admin/clear-personal-collections`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });

        if (response.ok) {
          const result = await response.json();
          alert(`✅ Suppression réussie!\n\n` +
                `Collections personnelles supprimées: ${result.deleted_count}\n` +
                `Total avant suppression: ${result.count_before}`);
        } else {
          alert('❌ Erreur lors de la suppression des collections personnelles');
        }
      } catch (error) {
        console.error('Error clearing personal collections:', error);
        alert('❌ Erreur de connexion');
      } finally {
        setClearingData(false);
      }
    };

    const clearAllKitsAndCollections = async () => {
      const confirm = window.confirm(
        '🚨 DANGER EXTRÊME: Cette action va supprimer TOUS les kits ET TOUTES les collections de la base de données.\n\n' +
        'Cela inclut:\n' +
        '- TOUS les Master Kits\n' +
        '- TOUTES les collections personnelles\n' +
        '- TOUS les détails personnels\n' +
        '- TOUTES les estimations\n\n' +
        'Cette action est COMPLÈTEMENT IRRÉVERSIBLE et remettra la base de données à zéro.\n\n' +
        'Tapez "SUPPRIMER TOUT" pour confirmer:'
      );
      if (!confirm) return;

      const confirmText = prompt('Tapez exactement "SUPPRIMER TOUT" pour confirmer:');
      if (confirmText !== 'SUPPRIMER TOUT') {
        alert('❌ Confirmation annulée. Texte incorrect.');
        return;
      }

      setClearingData(true);
      try {
        const response = await fetch(`${API}/api/admin/clear-all-kits`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });

        if (response.ok) {
          const result = await response.json();
          alert(`✅ Suppression totale réussie!\n\n` +
                `Master Kits supprimés: ${result.master_kits_deleted}\n` +
                `Collections supprimées: ${result.collections_deleted}\n` +
                `Total supprimé: ${result.total_deleted}\n\n` +
                `Compteurs avant suppression:\n` +
                `- Master Kits: ${result.counts_before.master_kits}\n` +
                `- Collections: ${result.counts_before.collections}`);
        } else {
          alert('❌ Erreur lors de la suppression complète');
        }
      } catch (error) {
        console.error('Error clearing all kits and collections:', error);
        alert('❌ Erreur de connexion');
      } finally {
        setClearingData(false);
      }
    };

    return (
      <div className="min-h-screen bg-white text-black p-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-gray-50 p-6 md:p-8 rounded-lg mb-6 md:mb-8 border border-gray-200">
            <h1 className="text-2xl md:text-3xl font-bold text-black mb-2">🔧 Admin Panel</h1>
            <p className="text-gray-600">Gestion de la plateforme TopKit</p>
          </div>
          
          {/* Admin Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            <button
              onClick={() => setAdminActiveTab('jerseys')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                adminActiveTab === 'jerseys' ? 'bg-black text-white' : 'bg-gray-200 text-black hover:bg-gray-300'
              }`}
            >
              Gestion des maillots
            </button>
            <button
              onClick={() => setAdminActiveTab('users')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                adminActiveTab === 'users' ? 'bg-black text-white' : 'bg-gray-200 text-black hover:bg-gray-300'
              }`}
            >
              Gestion des utilisateurs
            </button>
            <button
              onClick={() => setAdminActiveTab('data')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                adminActiveTab === 'data' ? 'bg-black text-white' : 'bg-gray-200 text-black hover:bg-gray-300'
              }`}
            >
              🗑️ Gestion des données
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="text-2xl">⏳</div>
              <p className="text-gray-600 mt-2">Chargement...</p>
            </div>
          ) : (
            <>
              {/* Jersey Management */}
              {adminActiveTab === 'jerseys' && (
                <div className="space-y-6">
                  {/* Pending Jerseys */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h2 className="text-xl font-bold text-black mb-4">
                      Maillots en attente d'approbation ({pendingJerseys.length})
                    </h2>
                    {pendingJerseys.length === 0 ? (
                      <p className="text-gray-600">Aucun maillot en attente</p>
                    ) : (
                      <div className="space-y-4">
                        {pendingJerseys.map((jersey) => (
                          <div key={jersey.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                              <div className="flex-1">
                                <h3 className="font-semibold text-black">{jersey.team}</h3>
                                <p className="text-sm text-gray-600">
                                  {jersey.league} • {jersey.season}
                                  {jersey.player && ` • ${jersey.player}`}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  Ref: {jersey.reference} • Soumis le {new Date(jersey.created_at).toLocaleDateString('fr-FR')}
                                </p>
                              </div>
                              <div className="flex space-x-2 mt-3 md:mt-0">
                                <button
                                  onClick={() => approveJersey(jersey.id)}
                                  className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  ✓ Approuver
                                </button>
                                <button
                                  onClick={() => suggestModification(jersey)}
                                  className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  📝 Modifier
                                </button>
                                <button
                                  onClick={() => rejectJersey(jersey.id)}
                                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  ✗ Rejeter
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Approved Jerseys - For deletion */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h2 className="text-xl font-bold text-black mb-4">
                      Maillots approuvés dans l'explorateur ({allJerseys.length})
                    </h2>
                    {allJerseys.length === 0 ? (
                      <p className="text-gray-600">Aucun maillot approuvé</p>
                    ) : (
                      <div className="space-y-4 max-h-96 overflow-y-auto">
                        {allJerseys.map((jersey) => (
                          <div key={jersey.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                              <div className="flex-1">
                                <h3 className="font-semibold text-black">{jersey.team}</h3>
                                <p className="text-sm text-gray-600">
                                  {jersey.league} • {jersey.season}
                                  {jersey.player && ` • ${jersey.player}`}
                                </p>
                              </div>
                              <button
                                onClick={() => deleteJersey(jersey.id, `${jersey.team} ${jersey.season}`)}
                                className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition-colors mt-2 md:mt-0"
                              >
                                🗑️ Supprimer
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* User Management */}
              {adminActiveTab === 'users' && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h2 className="text-xl font-bold text-black mb-4">
                    Gestion des utilisateurs ({allUsers.length})
                  </h2>
                  {allUsers.length === 0 ? (
                    <p className="text-gray-600">Aucun utilisateur trouvé</p>
                  ) : (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {allUsers.map((userItem) => (
                        <div key={userItem.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                            <div className="flex-1">
                              <h3 className="font-semibold text-black">{userItem.name}</h3>
                              <p className="text-sm text-gray-600">{userItem.email}</p>
                              <p className="text-xs text-gray-500">
                                Rôle: {userItem.role} • Inscrit le {new Date(userItem.created_at).toLocaleDateString('fr-FR')}
                              </p>
                              {userItem.status && userItem.status !== 'active' && (
                                <p className="text-xs text-red-600 mt-1">Statut: {userItem.status}</p>
                              )}
                            </div>
                            {userItem.role !== 'admin' && (
                              <div className="flex space-x-2 mt-3 md:mt-0">
                                <button
                                  onClick={() => banUser(userItem.id, userItem.name)}
                                  className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  🚫 Bannir
                                </button>
                                <button
                                  onClick={() => deleteUser(userItem.id, userItem.name)}
                                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  🗑️ Supprimer
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Data Management */}
              {adminActiveTab === 'data' && (
                <div className="space-y-6">
                  {/* Warning Section */}
                  <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <div className="flex items-center mb-3">
                      <span className="text-2xl mr-3">⚠️</span>
                      <h2 className="text-xl font-bold text-red-800">Zone Dangereuse - Gestion des Données</h2>
                    </div>
                    <p className="text-red-700">
                      <strong>ATTENTION:</strong> Les actions ci-dessous suppriment définitivement des données de la base. 
                      Ces actions sont <strong>IRRÉVERSIBLES</strong>. Utilisez avec précaution.
                    </p>
                  </div>

                  {/* Data Clearing Actions */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-bold text-black mb-4">Actions de suppression des données</h3>
                    
                    <div className="space-y-4">
                      {/* Clear Master Kits Only */}
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                        <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-orange-800 mb-2">🏷️ Supprimer tous les Master Kits</h4>
                            <p className="text-sm text-orange-700">
                              Supprime tous les Master Kits de la base de données, mais conserve les collections personnelles des utilisateurs.
                            </p>
                          </div>
                          <button
                            onClick={clearAllMasterKits}
                            disabled={clearingData}
                            className={`${
                              clearingData 
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-orange-500 hover:bg-orange-600'
                            } text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors mt-3 md:mt-0 md:ml-4`}
                          >
                            {clearingData ? '⏳ Suppression...' : '🗑️ Supprimer Master Kits'}
                          </button>
                        </div>
                      </div>

                      {/* Clear Personal Collections Only */}
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                        <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-orange-800 mb-2">👤 Supprimer toutes les collections personnelles</h4>
                            <p className="text-sm text-orange-700">
                              Supprime toutes les collections personnelles des utilisateurs, mais conserve les Master Kits de référence.
                            </p>
                          </div>
                          <button
                            onClick={clearAllPersonalCollections}
                            disabled={clearingData}
                            className={`${
                              clearingData 
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-orange-500 hover:bg-orange-600'
                            } text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors mt-3 md:mt-0 md:ml-4`}
                          >
                            {clearingData ? '⏳ Suppression...' : '🗑️ Supprimer Collections'}
                          </button>
                        </div>
                      </div>

                      {/* Clear Everything */}
                      <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                        <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-red-800 mb-2">💥 SUPPRIMER TOUT - Master Kits ET Collections</h4>
                            <p className="text-sm text-red-700">
                              <strong>ACTION EXTRÊME:</strong> Supprime TOUS les Master Kits ET TOUTES les collections personnelles. 
                              Remet complètement à zéro la base de données des kits.
                            </p>
                            <p className="text-xs text-red-600 mt-1">
                              ⚠️ Nécessite une double confirmation
                            </p>
                          </div>
                          <button
                            onClick={clearAllKitsAndCollections}
                            disabled={clearingData}
                            className={`${
                              clearingData 
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-red-600 hover:bg-red-700 border-2 border-red-700'
                            } text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors mt-3 md:mt-0 md:ml-4`}
                          >
                            {clearingData ? '⏳ Suppression...' : '💥 SUPPRIMER TOUT'}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Instructions */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <div className="flex items-center mb-3">
                      <span className="text-2xl mr-3">ℹ️</span>
                      <h3 className="text-lg font-bold text-blue-800">Instructions d'utilisation</h3>
                    </div>
                    <ul className="space-y-2 text-sm text-blue-700">
                      <li>• <strong>Master Kits seulement:</strong> Utilisez pour réinitialiser les données de référence tout en gardant les collections utilisateurs</li>
                      <li>• <strong>Collections seulement:</strong> Utilisez pour nettoyer les données personnelles tout en gardant les références</li>
                      <li>• <strong>Suppression totale:</strong> Utilisez uniquement pour un reset complet de la plateforme</li>
                      <li>• <strong>Toutes les suppressions sont définitives</strong> - Aucune récupération possible</li>
                    </ul>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  };

  // Main render
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      {currentView === 'home' && <HomePage />}
      {currentView === 'explore' && (
        <>
          {console.log('Rendering ExplorePage, currentView:', currentView)}
          <ExplorePage />
        </>
      )}
      {currentView === 'marketplace' && <MarketplacePage />}
      {currentView === 'profile' && (
        <ProfilePage 
          user={user} 
          API={API}
          userCollections={userCollections}
          loadUserCollections={loadUserCollections}
          handleRemoveCollectionItem={handleRemoveCollectionItem}
          handleViewCollectionItem={handleViewCollectionItem}
          userSubmissions={userSubmissions}
          handleJerseySubmit={() => {
            setEditingJersey({
              team: '',
              league: '',
              season: '',
              jersey_type: '',
              manufacturer: '',
              sku_code: '',
              model: 'authentic',
              description: '',
              isNewSubmission: true
            });
            setShowJerseyEditor(true);
          }}
        />
      )}
      {currentView === 'collection' && (
        <MyCollectionPage user={user} API={API} />
      )}
      {currentView === 'admin' && <AdminPanel />}

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {/* Security Settings Modal */}
      <SecuritySettingsModal
        isOpen={showSecurityModal}
        onClose={() => setShowSecurityModal(false)}
        user={user}
      />

      {/* Jersey Detail Editor - Used for both new submissions and editing */}
      {showJerseyEditor && editingJersey && (
        <JerseyDetailEditor
          isOpen={showJerseyEditor}
          onClose={() => {
            setShowJerseyEditor(false);
            setEditingJersey(null);
          }}
          onUpdateSuccess={() => {
            // Refresh data after successful submission or update
            if (editingJersey?.isNewSubmission) {
              // Refresh user submissions
              loadUserSubmissions();
            } else if (editingJersey?.isAdminEdit) {
              // Refresh admin data
              console.log('Admin edit completed');
            } else {
              // Refresh collection data
              loadUserCollections();
            }
            handleJerseyUpdate();
          }}
          jersey={editingJersey}
          mode={editingJersey?.isNewSubmission ? 'submission' : 
                (editingJersey?.isAdminEdit ? 'admin-modify' : 'collection-edit')}
          user={user}
        />
      )}

      {/* Jersey Detail View Modal */}
      {showJerseyDetailView && selectedJersey && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            {/* Header */}
            <div className="flex justify-between items-start p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-black">Détails du maillot</h2>
              <button
                onClick={() => {
                  setShowJerseyDetailView(false);
                  setSelectedJersey(null);
                }}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Jersey Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-black mb-3">Informations générales</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Équipe</label>
                    <div className="text-black font-medium">{selectedJersey.team || 'Non spécifié'}</div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Championnat</label>
                    <div className="text-black">{selectedJersey.league || 'Non spécifié'}</div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Saison</label>
                    <div className="text-black">{selectedJersey.season || 'Non spécifié'}</div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                    <div className="text-black">{selectedJersey.jersey_type || 'Non spécifié'}</div>
                  </div>

                  {selectedJersey.player && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Joueur</label>
                      <div className="text-black">{selectedJersey.player}</div>
                    </div>
                  )}

                  {selectedJersey.manufacturer && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Fabricant</label>
                      <div className="text-black">{selectedJersey.manufacturer}</div>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-black mb-3">Détails de collection</h3>
                  
                  {selectedJersey.collection_details?.collection_type && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Type de collection</label>
                      <div className="text-black capitalize">
                        {selectedJersey.collection_details.collection_type === 'owned' ? 'Possédé' : 'Recherché'}
                      </div>
                    </div>
                  )}

                  {selectedJersey.collection_details?.size && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Taille</label>
                      <div className="text-black">{selectedJersey.collection_details.size}</div>
                    </div>
                  )}

                  {selectedJersey.collection_details?.condition && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">État</label>
                      <div className="text-black">{selectedJersey.collection_details.condition}</div>
                    </div>
                  )}

                  {selectedJersey.collection_details?.added_at && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Ajouté le</label>
                      <div className="text-black">
                        {new Date(selectedJersey.collection_details.added_at).toLocaleDateString('fr-FR')}
                      </div>
                    </div>
                  )}

                  {selectedJersey.reference_number && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Référence</label>
                      <div className="text-black font-mono">{selectedJersey.reference_number}</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
                {selectedJersey.collection_details?.collection_type === 'owned' && (
                  <button
                    onClick={() => {
                      setShowJerseyDetailView(false);
                      handleEditCollectionItem({
                        id: selectedJersey.collection_details.collection_id,
                        jersey: selectedJersey,
                        collection_type: selectedJersey.collection_details.collection_type,
                        size: selectedJersey.collection_details.size,
                        condition: selectedJersey.collection_details.condition
                      });
                    }}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Éditer les détails
                  </button>
                )}
                <button
                  onClick={() => {
                    setShowJerseyDetailView(false);
                    setSelectedJersey(null);
                  }}
                  className="bg-gray-200 hover:bg-gray-300 text-black px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;