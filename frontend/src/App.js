import React, { useState, useEffect, createContext, useContext, useReducer } from 'react';
import './App.css';
import axios from 'axios';
import AuthModal from './AuthModal';
import TwoFactorAuthSetup from './TwoFactorAuthSetup';
import SecuritySettingsModal from './SecuritySettingsModal';
import SmartJerseySubmissionForm from './SmartJerseySubmissionForm';
import JerseyDetailEditor from './JerseyDetailEditor';
import { useCSVData } from './utils/csvLoader';
import tokenManager from './utils/tokenManager';

// Football data for suggestions
const LEAGUES_DATA = {
  'Premier League': [
    'Arsenal FC', 'Aston Villa', 'Brighton & Hove Albion', 'Burnley', 'Chelsea FC', 'Crystal Palace', 
    'Everton', 'Fulham', 'Liverpool FC', 'Luton Town', 'Manchester City', 'Manchester United', 
    'Newcastle United', 'Nottingham Forest', 'Sheffield United', 'Tottenham Hotspur', 'West Ham United', 'Wolverhampton Wanderers'
  ],
  'La Liga': [
    'Athletic Bilbao', 'Atletico Madrid', 'FC Barcelona', 'Real Betis', 'Celta Vigo', 'Deportivo Alaves', 
    'Getafe CF', 'Girona FC', 'Granada CF', 'Las Palmas', 'Mallorca', 'Osasuna', 'Rayo Vallecano', 
    'Real Madrid', 'Real Sociedad', 'Sevilla FC', 'Valencia CF', 'Villarreal CF'
  ],
  'Serie A': [
    'AC Milan', 'AS Roma', 'Atalanta', 'Bologna', 'Cagliari', 'Empoli', 'Fiorentina', 'Frosinone', 
    'Genoa', 'Hellas Verona', 'Inter Milan', 'Juventus', 'Lazio', 'Lecce', 'Monza', 'Napoli', 
    'Salernitana', 'Sassuolo', 'Torino', 'Udinese'
  ],
  'Bundesliga': [
    'FC Augsburg', 'Bayer Leverkusen', 'Bayern Munich', 'Borussia Dortmund', 'Borussia Monchengladbach', 
    'Eintracht Frankfurt', 'SC Freiburg', 'FC Heidenheim', 'TSG Hoffenheim', 'FC Koln', 'RB Leipzig', 
    'Mainz 05', 'SV Darmstadt 98', 'Union Berlin', 'VfB Stuttgart', 'VfL Bochum', 'VfL Wolfsburg', 'Werder Bremen'
  ],
  'Ligue 1': [
    'AS Monaco', 'Brest', 'Clermont Foot', 'FC Lorient', 'FC Metz', 'Lille OSC', 'Le Havre', 
    'Lens', 'Lyon', 'Marseille', 'Montpellier', 'Nantes', 'Nice', 'Paris Saint-Germain', 
    'Reims', 'Rennes', 'Strasbourg', 'Toulouse FC'
  ],
  'Liga Portugal': [
    'SL Benfica', 'FC Porto', 'Sporting CP', 'SC Braga', 'Vitória SC', 'Boavista FC', 'FC Famalicão', 
    'Gil Vicente FC', 'Moreirense FC', 'Rio Ave FC', 'CD Santa Clara', 'Estoril Praia'
  ],
  'Eredivisie': [
    'Ajax', 'PSV Eindhoven', 'Feyenoord', 'AZ Alkmaar', 'FC Utrecht', 'FC Twente', 'Vitesse', 
    'Go Ahead Eagles', 'NEC Nijmegen', 'SC Heerenveen', 'PEC Zwolle', 'Sparta Rotterdam'
  ],
  'Scottish Premiership': [
    'Celtic FC', 'Rangers FC', 'Aberdeen FC', 'Heart of Midlothian', 'Hibernian FC', 'St Mirren', 
    'Dundee FC', 'Motherwell FC', 'St Johnstone FC', 'Kilmarnock FC', 'Ross County FC', 'Livingston FC'
  ],
  'Belgian Pro League': [
    'Club Brugge', 'Royal Antwerp FC', 'KAA Gent', 'Standard Liège', 'RSC Anderlecht', 'KRC Genk', 
    'Royal Union SG', 'OH Leuven', 'Cercle Brugge', 'Westerlo', 'Kortrijk', 'Charleroi'
  ],
  'MLS': [
    'LA Galaxy', 'LAFC', 'Inter Miami CF', 'New York City FC', 'New York Red Bulls', 'Atlanta United FC', 
    'Seattle Sounders FC', 'Portland Timbers', 'Austin FC', 'FC Cincinnati', 'Orlando City SC', 
    'Toronto FC', 'Vancouver Whitecaps FC', 'Montreal Impact', 'Chicago Fire FC', 'Colorado Rapids'
  ],
  'Liga MX': [
    'Club América', 'Chivas Guadalajara', 'Cruz Azul', 'Pumas UNAM', 'Club León', 'Tigres UANL', 
    'Monterrey', 'Santos Laguna', 'Pachuca', 'Atlas FC', 'Toluca FC', 'Puebla FC'
  ],
  'Brazilian Serie A': [
    'Flamengo', 'Palmeiras', 'São Paulo FC', 'Corinthians', 'Santos FC', 'Grêmio', 'Internacional', 
    'Atlético Mineiro', 'Botafogo', 'Vasco da Gama', 'Fluminense', 'Cruzeiro', 'Bahia'
  ],
  'Argentine Primera': [
    'Boca Juniors', 'River Plate', 'Independiente', 'Racing Club', 'San Lorenzo', 'Estudiantes', 
    'Vélez Sarsfield', 'Lanús', 'Defensa y Justicia', 'Talleres', 'Colón', 'Godoy Cruz'
  ],
  'Champions League': [
    'All European clubs participating'
  ],
  'Europa League': [
    'All European clubs participating'  
  ],
  'Conference League': [
    'All European clubs participating'
  ],
  'Nation': [
    'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Canada', 'Colombia', 'Croatia', 
    'Czech Republic', 'Denmark', 'England', 'France', 'Germany', 'Hungary', 'Italy', 'Japan', 
    'Mexico', 'Morocco', 'Netherlands', 'Peru', 'Poland', 'Portugal', 'Qatar', 'Senegal', 
    'Slovakia', 'Slovenia', 'South Korea', 'Spain', 'Switzerland', 'Turkey', 'Ukraine', 'United States', 'Uruguay'
  ]
};

const SEASONS = [
  '25/26', '24/25', '23/24', '22/23', '21/22', '20/21', '19/20', '18/19', '17/18', '16/17', 
  '15/16', '14/15', '13/14', '12/13', '11/12', '10/11', '09/10', '08/09', '07/08', '06/07'
];

// Get the backend URL from environment variables
const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

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
  const [currentView, setCurrentView] = useState('home');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [jerseys, setJerseys] = useState([]);
  const [marketplaceItems, setMarketplaceItems] = useState([]);
  const [filteredJerseys, setFilteredJerseys] = useState([]);
  const [filteredMarketplace, setFilteredMarketplace] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [filters, setFilters] = useState({
    league: '',
    team: '',
    season: '',
    minPrice: '',
    maxPrice: ''
  });
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSecurityModal, setShowSecurityModal] = useState(false);
  const [friends, setFriends] = useState([]);
  const [pendingRequests, setPendingRequests] = useState({ received: [], sent: [] });
  const [friendsStats, setFriendsStats] = useState({ total_friends: 0, pending_received: 0, pending_sent: 0 });
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showJerseyEditor, setShowJerseyEditor] = useState(false);
  const [showJerseyDetailView, setShowJerseyDetailView] = useState(false);
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [editingJersey, setEditingJersey] = useState(null);
  const [userCollections, setUserCollections] = useState({
    owned: [],
    wanted: []
  });
  const [userSubmissions, setUserSubmissions] = useState([]);

  // CSV Data
  const { csvData, loading: csvLoading, error: csvError } = useCSVData();

  // Load data on mount and when user changes or view changes
  useEffect(() => {
    loadJerseys();
    loadMarketplace();
    if (user) {
      loadNotifications();
      loadFriends();
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

  // Filter jerseys based on search and filters
  useEffect(() => {
    let filtered = jerseys;

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(jersey => 
        jersey.team?.toLowerCase().includes(search) ||
        jersey.league?.toLowerCase().includes(search) ||
        jersey.player_name?.toLowerCase().includes(search) ||
        jersey.season?.toLowerCase().includes(search)
      );
    }

    if (filters.league) {
      filtered = filtered.filter(jersey => jersey.league === filters.league);
    }

    if (filters.team) {
      filtered = filtered.filter(jersey => jersey.team === filters.team);
    }

    if (filters.season) {
      filtered = filtered.filter(jersey => jersey.season === filters.season);
    }

    setFilteredJerseys(filtered);
  }, [jerseys, searchTerm, filters]);

  // Filter marketplace based on search and filters
  useEffect(() => {
    let filtered = marketplaceItems;

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        item.team?.toLowerCase().includes(search) ||
        item.league?.toLowerCase().includes(search) ||
        item.player_name?.toLowerCase().includes(search)
      );
    }

    if (filters.league) {
      filtered = filtered.filter(item => item.league === filters.league);
    }

    if (filters.team) {
      filtered = filtered.filter(item => item.team === filters.team);
    }

    if (filters.minPrice) {
      filtered = filtered.filter(item => parseFloat(item.min_price || 0) >= parseFloat(filters.minPrice));
    }

    if (filters.maxPrice) {
      filtered = filtered.filter(item => parseFloat(item.min_price || 0) <= parseFloat(filters.maxPrice));
    }

    setFilteredMarketplace(filtered);
  }, [marketplaceItems, searchTerm, filters]);

  // API Functions
  const loadJerseys = async () => {
    try {
      const response = await fetch(`${API}/api/jerseys/approved`);
      if (response.ok) {
        const data = await response.json();
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

  const loadFriends = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`${API}/api/friends`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setFriends(data.friends || []);
        setPendingRequests(data.pending_requests || { received: [], sent: [] });
        setFriendsStats(data.stats || { total_friends: 0, pending_received: 0, pending_sent: 0 });
      }
    } catch (error) {
      console.error('Error loading friends:', error);
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
      loadFriends();
      loadUserCollections();
      loadUserSubmissions();
    }, 500);
  };

  const handleLogout = () => {
    logout();
    setCurrentView('home');
    setNotifications([]);
    setFriends([]);
    setPendingRequests({ received: [], sent: [] });
    setFriendsStats({ total_friends: 0, pending_received: 0, pending_sent: 0 });
    setUserCollections({ owned: [], wanted: [] });
    setUserSubmissions([]);
  };

  // UI handlers
  const handleSearch = (term) => {
    setSearchTerm(term);
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

  const handleJerseySubmit = () => {
    setShowSubmitModal(false);
    loadUserSubmissions();
  };

  const handleJerseyUpdate = () => {
    setShowJerseyEditor(false);
    setEditingJersey(null);
    loadUserSubmissions();
  };

  // Friend management functions
  const respondToFriendRequest = async (requestId, accept) => {
    if (!user) return;
    
    try {
      const response = await fetch(`${API}/api/friends/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          request_id: requestId,
          accept: accept
        })
      });

      if (response.ok) {
        // Reload friends data
        loadFriends();
        // Show success message
        alert(accept ? 'Demande d\'ami acceptée!' : 'Demande d\'ami refusée!');
      } else {
        alert('Erreur lors du traitement de la demande');
      }
    } catch (error) {
      console.error('Error responding to friend request:', error);
      alert('Erreur lors du traitement de la demande');
    }
  };

  const removeFriend = async (friendId, friendName) => {
    if (!user) return;
    
    const confirmRemove = window.confirm(`Êtes-vous sûr de vouloir supprimer ${friendName} de vos amis ?`);
    if (!confirmRemove) return;
    
    try {
      const response = await fetch(`${API}/api/friends/${friendId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });

      if (response.ok) {
        // Reload friends data
        loadFriends();
        alert(`${friendName} a été supprimé de vos amis`);
      } else {
        alert('Erreur lors de la suppression de l\'ami');
      }
    } catch (error) {
      console.error('Error removing friend:', error);
      alert('Erreur lors de la suppression de l\'ami');
    }
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
                  src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjQwIiB2aWV3Qm94PSIwIDAgMTIwIDQwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8dGV4dCB4PSI2MCIgeT0iMjgiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNCIgZm9udC13ZWlnaHQ9IjkwMCIgZmlsbD0iIzAwMDAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSI+VE9QS0lUPC90ZXh0Pgo8L3N2Zz4K" 
                  alt="TOPKIT" 
                  className="h-8 md:h-10"
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
                onClick={() => setCurrentView('explore')}
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
                      className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-black hover:bg-gray-100"
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
                          🔧 Admin Panel
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
                      🔒 Settings
                    </button>
                    <button
                      onClick={() => {
                        handleLogout();
                        setShowMobileMenu(false);
                      }}
                      className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-black hover:bg-gray-100"
                    >
                      Déconnexion
                    </button>
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

                {/* Mobile Search */}
                <div className="px-3 py-2">
                  <input
                    type="text"
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="w-full bg-white text-black px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>
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

  // Home Page Component
  const HomePage = () => (
    <div className="min-h-screen bg-white text-black">
      {/* Hero Section */}
      <div className="relative bg-white">
        <div className="max-w-4xl mx-auto px-4 py-16 md:py-24">
          <div className="text-center">
            {/* Large TOPKIT logo */}
            <div className="mb-8 md:mb-12">
              <img 
                src="https://customer-assets.emergentagent.com/job_notif-system-fix/artifacts/qdnnknkl_topkit_logo.png" 
                alt="TOPKIT" 
                className="w-full max-w-md mx-auto h-auto"
              />
            </div>
            
            <p className="text-lg md:text-xl text-gray-600 mb-6 md:mb-8 max-w-2xl mx-auto leading-relaxed">
              La marketplace premium pour collectionneurs de maillots de foot
            </p>
            
            {/* Search Bar - Mobile First */}
            <div className="mb-8 md:mb-12">
              <div className="relative max-w-lg mx-auto">
                <input
                  type="text"
                  placeholder="Rechercher un maillot..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full bg-gray-50 text-black px-4 py-3 md:py-4 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-base"
                />
                <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Action Buttons - Mobile Stack */}
            <div className="flex flex-col sm:flex-row gap-3 md:gap-4 max-w-sm mx-auto mb-12 md:mb-16">
              <button
                onClick={() => setCurrentView('explore')}
                className="bg-black hover:bg-gray-800 text-white px-6 py-3 md:py-4 rounded-lg font-medium text-base transition-colors w-full"
              >
                Explorez
              </button>
              <button
                onClick={() => setCurrentView('marketplace')}
                className="bg-gray-200 hover:bg-gray-300 text-black px-6 py-3 md:py-4 rounded-lg font-medium text-base transition-colors w-full"
              >
                Marketplace
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section - Mobile Optimized */}
      <div className="bg-gray-50 py-12 md:py-16">
        <div className="max-w-4xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8 text-center">
            <div>
              <div className="text-2xl md:text-3xl font-bold text-black mb-1 md:mb-2">50K+</div>
              <div className="text-sm md:text-base text-gray-600">Maillots</div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-bold text-black mb-1 md:mb-2">15K+</div>
              <div className="text-sm md:text-base text-gray-600">Collectionneurs</div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-bold text-black mb-1 md:mb-2">500+</div>
              <div className="text-sm md:text-base text-gray-600">Équipes</div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-bold text-black mb-1 md:mb-2">98%</div>
              <div className="text-sm md:text-base text-gray-600">Satisfaction</div>
            </div>
          </div>
        </div>
      </div>

      {/* Leagues Section - Simplified for Mobile */}
      <div className="py-12 md:py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-xl md:text-2xl font-bold text-center mb-8 md:mb-12 text-black">
            Championnats
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
            {[
              { name: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
              { name: 'La Liga', flag: '🇪🇸' },
              { name: 'Serie A', flag: '🇮🇹' },
              { name: 'Bundesliga', flag: '🇩🇪' },
              { name: 'Ligue 1', flag: '🇫🇷' },
              { name: 'Liga Portugal', flag: '🇵🇹' },
              { name: 'Eredivisie', flag: '🇳🇱' },
              { name: 'MLS', flag: '🇺🇸' },
              { name: 'Liga MX', flag: '🇲🇽' },
              { name: 'Champions League', flag: '🏆' }
            ].map((league) => (
              <button
                key={league.name}
                onClick={() => {
                  handleFilterChange({ league: league.name });
                  setCurrentView('explore');
                }}
                className="bg-gray-100 hover:bg-gray-200 p-3 md:p-4 rounded-lg transition-colors text-center border border-gray-200"
              >
                <div className="text-xl md:text-2xl mb-1 md:mb-2">{league.flag}</div>
                <div className="text-black font-medium text-xs md:text-sm leading-tight">{league.name}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Explore Page Component with filters
  const ExplorePage = () => (
    <div className="min-h-screen bg-white text-black p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header with Search and Filters */}
        <div className="mb-6 md:mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4 md:mb-6">
            <h1 className="text-2xl md:text-3xl font-bold mb-4 lg:mb-0">
              Explorez les maillots
            </h1>
            
            {/* View Toggle */}
            <div className="flex items-center space-x-2 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-black text-white' : 'text-gray-600'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-black text-white' : 'text-gray-600'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="bg-gray-50 p-4 md:p-6 rounded-lg mb-4 md:mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Championnat
                </label>
                <select
                  value={filters.league}
                  onChange={(e) => handleFilterChange({ league: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Tous les championnats</option>
                  {availableLeagues.map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Équipe
                </label>
                <select
                  value={filters.team}
                  onChange={(e) => handleFilterChange({ team: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Toutes les équipes</option>
                  {availableTeams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Saison
                </label>
                <select
                  value={filters.season}
                  onChange={(e) => handleFilterChange({ season: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Toutes les saisons</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2 lg:col-span-2">
                <div className="flex space-x-2 pt-7">
                  <button
                    onClick={clearFilters}
                    className="bg-gray-200 hover:bg-gray-300 text-black px-4 py-3 rounded-lg transition-colors"
                  >
                    Effacer filtres
                  </button>
                  <div className="flex-1 text-right pt-3">
                    <span className="text-gray-600 text-sm">
                      {filteredJerseys.length} maillots trouvés
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Mobile Search */}
          <div className="md:hidden mb-6">
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full bg-gray-50 text-black px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
        </div>

        {/* Results */}
        {filteredJerseys.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏟️</div>
            <h3 className="text-xl font-semibold text-black mb-2">
              Aucun maillot trouvé
            </h3>
            <p className="text-gray-600 mb-4">
              Essayez de modifier vos critères de recherche
            </p>
            <button
              onClick={clearFilters}
              className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Voir tous les maillots
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6"
            : "space-y-4"
          }>
            {filteredJerseys.map((jersey) => (
              <div
                key={jersey.id}
                className={viewMode === 'grid'
                  ? "bg-white rounded-lg overflow-hidden hover:shadow-md transition-shadow border border-gray-200"
                  : "bg-white rounded-lg p-4 hover:shadow-md transition-shadow border border-gray-200 flex items-center space-x-4"
                }
              >
                {viewMode === 'grid' ? (
                  <>
                    <div className="aspect-square bg-gray-100 flex items-center justify-center">
                      <div className="text-4xl">👕</div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-black mb-1 truncate">
                        {jersey.team}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {jersey.league} • {jersey.season}
                      </p>
                      {jersey.player_name && (
                        <p className="text-sm text-black mb-3 font-medium">
                          {jersey.player_name}
                        </p>
                      )}
                      
                      {/* Collection buttons */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => toggleCollectionItem(jersey, 'owned')}
                          className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-colors ${
                            isInCollection(jersey.id, 'owned')
                              ? 'bg-black text-white'
                              : 'bg-gray-100 text-black hover:bg-gray-200'
                          }`}
                        >
                          {isInCollection(jersey.id, 'owned') ? '✓ Possédé' : '+ Own'}
                        </button>
                        <button
                          onClick={() => toggleCollectionItem(jersey, 'wanted')}
                          className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-colors ${
                            isInCollection(jersey.id, 'wanted')
                              ? 'bg-gray-800 text-white'
                              : 'bg-gray-100 text-black hover:bg-gray-200'
                          }`}
                        >
                          {isInCollection(jersey.id, 'wanted') ? '⭐ Voulu' : '+ Want'}
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <div className="text-2xl">👕</div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-black mb-1">
                        {jersey.team}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {jersey.league} • {jersey.season}
                      </p>
                      {jersey.player_name && (
                        <p className="text-sm text-black font-medium">
                          {jersey.player_name}
                        </p>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => toggleCollectionItem(jersey, 'owned')}
                        className={`py-2 px-4 rounded-lg text-xs font-medium transition-colors ${
                          isInCollection(jersey.id, 'owned')
                            ? 'bg-black text-white'
                            : 'bg-gray-100 text-black hover:bg-gray-200'
                        }`}
                      >
                        {isInCollection(jersey.id, 'owned') ? '✓ Possédé' : '+ Own'}
                      </button>
                      <button
                        onClick={() => toggleCollectionItem(jersey, 'wanted')}
                        className={`py-2 px-4 rounded-lg text-xs font-medium transition-colors ${
                          isInCollection(jersey.id, 'wanted')
                            ? 'bg-gray-800 text-white'
                            : 'bg-gray-100 text-black hover:bg-gray-200'
                        }`}
                      >
                        {isInCollection(jersey.id, 'wanted') ? '⭐ Voulu' : '+ Want'}
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  // Marketplace Component
  const MarketplacePage = () => (
    <div className="min-h-screen bg-white text-black p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header with Search and Filters */}
        <div className="mb-6 md:mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4 md:mb-6">
            <h1 className="text-2xl md:text-3xl font-bold mb-4 lg:mb-0">
              Marketplace
            </h1>
            
            {/* View Toggle */}
            <div className="flex items-center space-x-2 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-black text-white' : 'text-gray-600'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-black text-white' : 'text-gray-600'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="bg-gray-50 p-4 md:p-6 rounded-lg mb-4 md:mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Championnat
                </label>
                <select
                  value={filters.league}
                  onChange={(e) => handleFilterChange({ league: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Tous</option>
                  {[...new Set(marketplaceItems.map(item => item.league).filter(Boolean))].map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Équipe
                </label>
                <select
                  value={filters.team}
                  onChange={(e) => handleFilterChange({ team: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Toutes</option>
                  {[...new Set(marketplaceItems.map(item => item.team).filter(Boolean))].map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prix min
                </label>
                <input
                  type="number"
                  placeholder="0€"
                  value={filters.minPrice}
                  onChange={(e) => handleFilterChange({ minPrice: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prix max
                </label>
                <input
                  type="number"
                  placeholder="500€"
                  value={filters.maxPrice}
                  onChange={(e) => handleFilterChange({ maxPrice: e.target.value })}
                  className="w-full bg-white text-black p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div className="md:col-span-2">
                <div className="flex space-x-2 pt-7">
                  <button
                    onClick={clearFilters}
                    className="bg-gray-200 hover:bg-gray-300 text-black px-4 py-3 rounded-lg transition-colors"
                  >
                    Effacer
                  </button>
                  <div className="flex-1 text-right pt-3">
                    <span className="text-gray-600 text-sm">
                      {filteredMarketplace.length} articles trouvés
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        {filteredMarketplace.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🛒</div>
            <h3 className="text-xl font-semibold text-black mb-2">
              Aucun article trouvé
            </h3>
            <p className="text-gray-600 mb-4">
              Essayez de modifier vos critères de recherche
            </p>
            <button
              onClick={clearFilters}
              className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Voir tous les articles
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6"
            : "space-y-4"
          }>
            {filteredMarketplace.map((item) => (
              <div
                key={item.id}
                className={viewMode === 'grid'
                  ? "bg-white rounded-lg overflow-hidden hover:shadow-md transition-shadow border border-gray-200 relative"
                  : "bg-white rounded-lg p-4 hover:shadow-md transition-shadow border border-gray-200 flex items-center space-x-4"
                }
              >
                {viewMode === 'grid' ? (
                  <>
                    <div className="aspect-square bg-gray-100 flex items-center justify-center relative">
                      <div className="text-4xl">👕</div>
                      {/* Price overlay */}
                      <div className="absolute top-2 right-2 bg-black text-white px-2 py-1 rounded-lg text-sm font-bold">
                        dès {item.min_price}€
                      </div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-black mb-1 truncate">
                        {item.team}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {item.league}
                      </p>
                      {item.player_name && (
                        <p className="text-sm text-black mb-3 font-medium">
                          {item.player_name}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mb-3">
                        {item.listing_count} annonce{item.listing_count > 1 ? 's' : ''}
                      </p>
                      
                      <button className="w-full bg-black hover:bg-gray-800 text-white py-2 rounded-lg text-sm font-medium transition-colors">
                        Voir les annonces
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <div className="text-2xl">👕</div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-black mb-1">
                        {item.team}
                      </h3>
                      <p className="text-sm text-gray-600 mb-1">
                        {item.league}
                      </p>
                      {item.player_name && (
                        <p className="text-sm text-black mb-1 font-medium">
                          {item.player_name}
                        </p>
                      )}
                      <p className="text-xs text-gray-500">
                        {item.listing_count} annonce{item.listing_count > 1 ? 's' : ''}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-black font-bold mb-2">
                        dès {item.min_price}€
                      </div>
                      <button className="bg-black hover:bg-gray-800 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors">
                        Voir
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  // Profile Page Component
  const ProfilePage = () => {
    const [activeTab, setActiveTab] = useState('collection');

    const renderTabContent = () => {
      switch (activeTab) {
        case 'collection':
          return (
            <div>
              <h3 className="text-xl font-semibold mb-6 text-black">Ma Collection</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Owned Jerseys */}
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h4 className="text-lg font-semibold text-black mb-4 flex items-center">
                    <span className="mr-2">✓</span>
                    Maillots possédés ({userCollections.owned?.length || 0})
                  </h4>
                  {userCollections.owned?.length > 0 ? (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {userCollections.owned.map((item, index) => (
                        <div key={item.id || index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="font-medium text-black">
                                {item.jersey?.team || item.team || 'Équipe inconnue'}
                              </div>
                              <div className="text-sm text-gray-600">
                                {(item.jersey?.league || item.league || 'Ligue inconnue')} • {(item.jersey?.season || item.season || 'Saison inconnue')}
                              </div>
                              {(item.jersey?.player || item.player) && (
                                <div className="text-sm text-gray-500 mt-1">
                                  {item.jersey?.player || item.player}
                                </div>
                              )}
                              {/* Collection details if available */}
                              {(item.size || item.condition) && (
                                <div className="text-xs text-gray-500 mt-2">
                                  {item.size && `Taille: ${item.size}`}
                                  {item.size && item.condition && ' • '}
                                  {item.condition && `État: ${item.condition}`}
                                </div>
                              )}
                            </div>
                            {/* Action buttons */}
                            <div className="flex flex-col space-y-1 ml-3">
                              <button
                                onClick={() => handleEditCollectionItem(item)}
                                className="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-center transition-colors touch-manipulation"
                                title="Éditer les détails"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleViewCollectionItem(item)}
                                className="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded text-center transition-colors touch-manipulation"
                                title="Voir les détails"
                              >
                                View
                              </button>
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  handleRemoveCollectionItem(item, 'owned');
                                }}
                                className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-center transition-colors touch-manipulation"
                                title="Supprimer de la collection"
                              >
                                Suppr
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-600">
                      <div className="text-4xl mb-2">👕</div>
                      <p>Votre collection est vide</p>
                      <p className="text-sm">Explorez des maillots et ajoutez-les à votre collection</p>
                    </div>
                  )}
                </div>

                {/* Wanted Jerseys */}
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h4 className="text-lg font-semibold text-black mb-4 flex items-center">
                    <span className="mr-2">⭐</span>
                    Wishlist ({userCollections.wanted?.length || 0})
                  </h4>
                  {userCollections.wanted?.length > 0 ? (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {userCollections.wanted.map((item) => (
                        <div key={item.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="font-medium text-black">
                                {item.jersey?.team || 'Équipe inconnue'}
                              </div>
                              <div className="text-sm text-gray-600">
                                {item.jersey?.league || 'Ligue inconnue'} • {item.jersey?.season || 'Saison inconnue'}
                              </div>
                              {item.jersey?.player && (
                                <div className="text-sm text-gray-500 mt-1">
                                  {item.jersey.player}
                                </div>
                              )}
                            </div>
                            {/* Action buttons for wanted items */}
                            <div className="flex flex-col space-y-1 ml-3">
                              <button
                                onClick={() => handleViewCollectionItem(item)}
                                className="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded text-center transition-colors"
                                title="Voir les détails"
                              >
                                View
                              </button>
                              <button
                                onClick={() => handleRemoveCollectionItem(item, 'wanted')}
                                className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-center transition-colors"
                                title="Supprimer de la wishlist"
                              >
                                Suppr
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-600">
                      <div className="text-4xl mb-2">⭐</div>
                      <p>Votre wishlist est vide</p>
                      <p className="text-sm">Ajoutez des maillots que vous recherchez</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );

        case 'submissions':
          return (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-black">Mes Soumissions</h3>
                <button
                  onClick={() => {
                    console.log('Submit button clicked!');
                    // Open jersey editor for new jersey submission
                    setEditingJersey({
                      // Empty jersey object for new submission
                      team: '',
                      league: '',
                      season: '',
                      jersey_type: '',
                      player: '',
                      manufacturer: '',
                      isNewSubmission: true // Flag to indicate this is a new submission
                    });
                    setShowJerseyEditor(true);
                  }}
                  className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Soumettre un maillot
                </button>
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Total', value: userSubmissions.length, color: 'black' },
                  { label: 'En attente', value: userSubmissions.filter(s => s.status === 'pending').length, color: 'gray' },
                  { label: 'Approuvés', value: userSubmissions.filter(s => s.status === 'approved').length, color: 'black' },
                  { label: 'Refusés', value: userSubmissions.filter(s => s.status === 'rejected').length, color: 'gray' }
                ].map((stat) => (
                  <div key={stat.label} className="bg-white p-4 rounded-lg text-center border border-gray-200">
                    <div className={`text-2xl font-bold text-black mb-1`}>
                      {stat.value}
                    </div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                  </div>
                ))}
              </div>

              {/* Submissions List */}
              {userSubmissions.length > 0 ? (
                <div className="space-y-4">
                  {userSubmissions.map((submission) => (
                    <div key={submission.id} className="bg-white p-6 rounded-lg border border-gray-200">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="text-lg font-semibold text-black">
                            {submission.team} - {submission.player_name || 'Joueur non spécifié'}
                          </h4>
                          <p className="text-gray-600">
                            {submission.league} • {submission.season}
                          </p>
                          <p className="text-sm text-gray-500">
                            Réf: {submission.reference}
                          </p>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            submission.status === 'approved' ? 'bg-green-100 text-green-800' :
                            submission.status === 'pending' ? 'bg-gray-100 text-gray-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {submission.status === 'approved' ? 'Approuvé' :
                             submission.status === 'pending' ? 'En attente' : 'Refusé'}
                          </span>
                          {(submission.status === 'rejected' || (submission.status === 'needs_modification')) && (
                            <button
                              onClick={() => openJerseyEditor(submission)}
                              className="text-black hover:text-gray-700 text-sm underline"
                            >
                              Modifier
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {/* Admin feedback */}
                      {submission.admin_feedback && (
                        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                          <div className="text-sm text-gray-700">
                            <strong>Retour admin:</strong> {submission.admin_feedback}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-600">
                  <div className="text-6xl mb-4">📝</div>
                  <h3 className="text-xl font-semibold mb-2">Aucune soumission</h3>
                  <p className="mb-4">Vous n'avez pas encore soumis de maillot</p>
                  <p className="text-sm text-gray-500">
                    Utilisez le bouton "Soumettre un maillot" ci-dessus pour ajouter votre premier maillot
                  </p>
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
                La fonctionnalité de vente sera bientôt disponible. En attendant, vous pourrez :
              </p>
              <div className="bg-white p-6 rounded-lg max-w-md mx-auto border border-gray-200">
                <ul className="text-left text-gray-700 space-y-3">
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Créer vos annonces de vente
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Fixer vos prix et conditions
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Recevoir des messages d'acheteurs
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Suivre vos ventes en temps réel
                  </li>
                </ul>
              </div>
            </div>
          );

        case 'friends':
          return (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏗️</div>
              <h3 className="text-xl font-semibold text-black mb-2">
                Bientôt disponible
              </h3>
              <p className="text-gray-600 mb-6">
                La fonctionnalité d'amis sera bientôt disponible. En attendant, vous pourrez :
              </p>
              <div className="bg-white p-6 rounded-lg max-w-md mx-auto border border-gray-200">
                <ul className="text-left text-gray-700 space-y-3">
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Ajouter des amis collectionneurs
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Voir leurs collections publiques
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Échanger des maillots entre amis
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Suivre leurs dernières acquisitions
                  </li>
                </ul>
              </div>
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
                La fonctionnalité de messagerie sera bientôt disponible. En attendant, vous pourrez :
              </p>
              <div className="bg-white p-6 rounded-lg max-w-md mx-auto border border-gray-200">
                <ul className="text-left text-gray-700 space-y-3">
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Contacter les vendeurs directement
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Négocier les prix en privé
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Organiser les échanges de maillots
                  </li>
                  <li className="flex items-start">
                    <span className="text-black mr-2">✓</span>
                    Recevoir des notifications en temps réel
                  </li>
                </ul>
              </div>
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div className="min-h-screen bg-white text-black p-4">
        <div className="max-w-4xl mx-auto">
          {/* Profile Header */}
          <div className="bg-gray-50 p-6 md:p-8 rounded-lg mb-6 md:mb-8 border border-gray-200">
            <div className="flex items-center space-x-6">
              <div className="w-16 md:w-20 h-16 md:h-20 bg-black rounded-full flex items-center justify-center">
                <span className="text-xl md:text-2xl font-bold text-white">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-black mb-2">{user?.name || 'Utilisateur'}</h1>
                <p className="text-gray-600">{user?.email}</p>
                <div className="flex items-center space-x-6 mt-4">
                  <div className="text-center">
                    <div className="text-xl md:text-2xl font-bold text-black">{userCollections.owned?.length || 0}</div>
                    <div className="text-xs md:text-sm text-gray-600">Possédés</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl md:text-2xl font-bold text-black">{userCollections.wanted?.length || 0}</div>
                    <div className="text-xs md:text-sm text-gray-600">Recherchés</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl md:text-2xl font-bold text-black">{userSubmissions.length || 0}</div>
                    <div className="text-xs md:text-sm text-gray-600">Soumissions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl md:text-2xl font-bold text-black">{friendsStats.total_friends || 0}</div>
                    <div className="text-xs md:text-sm text-gray-600">Amis</div>
                  </div>
                </div>
              </div>
              
              {/* No Admin Panel button here - moved to hamburger menu */}
              {user?.role === 'admin' && (
                <div className="ml-auto">
                  {/* Settings button removed - moved to hamburger menu */}
                </div>
              )}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="bg-gray-50 rounded-lg p-2 mb-6 md:mb-8 border border-gray-200">
            <nav className="flex space-x-2 overflow-x-auto">
              {[
                { key: 'collection', label: 'Ma Collection', icon: '👕' },
                { key: 'submissions', label: 'Mes Soumissions', icon: '📝' },
                { key: 'listings', label: 'Mes Listings', icon: '💰' },
                { key: 'friends', label: 'Mes Amis', icon: '👥' },
                { key: 'messages', label: 'Messages', icon: '💬' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center space-x-2 px-3 md:px-4 py-2 md:py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                    activeTab === tab.key
                      ? 'bg-black text-white'
                      : 'text-gray-600 hover:text-black hover:bg-gray-100'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span className="text-sm md:text-base">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="bg-gray-50 rounded-lg p-6 md:p-8 border border-gray-200">
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
      setEditingJersey({
        ...jersey,
        isAdminEdit: true // Flag to indicate this is an admin edit
      });
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
            </>
          )}
        </div>
      </div>
    );
  };

  // Main render
  return (
    <div className="min-h-screen bg-black">
      <Header />
      
      {currentView === 'home' && <HomePage />}
      {currentView === 'explore' && <ExplorePage />}
      {currentView === 'marketplace' && <MarketplacePage />}
      {currentView === 'profile' && <ProfilePage />}
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

      {/* Smart Jersey Submission Form */}
      {showSubmitModal && (
        <SmartJerseySubmissionForm
          isOpen={showSubmitModal}
          onClose={() => setShowSubmitModal(false)}
          onSubmitSuccess={handleJerseySubmit}
          csvData={csvData}
          user={user}
        />
      )}

      {/* Jersey Detail Editor */}
      {showJerseyEditor && editingJersey && (
        <JerseyDetailEditor
          isOpen={showJerseyEditor}
          onClose={() => {
            setShowJerseyEditor(false);
            setEditingJersey(null);
          }}
          onUpdateSuccess={() => {
            handleJerseyUpdate();
            loadUserCollections(); // Reload collections after update
          }}
          jersey={editingJersey}
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