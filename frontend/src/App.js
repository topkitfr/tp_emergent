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
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showJerseyEditor, setShowJerseyEditor] = useState(false);
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [editingJersey, setEditingJersey] = useState(null);
  const [userCollections, setUserCollections] = useState({
    owned: [],
    wanted: []
  });
  const [userSubmissions, setUserSubmissions] = useState([]);

  // CSV Data
  const { csvData, loading: csvLoading, error: csvError } = useCSVData();

  // Load data on mount and when user changes
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
        setNotifications(data);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
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
      }
    } catch (error) {
      console.error('Error loading friends:', error);
    }
  };

  const loadUserCollections = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`${API}/api/users/${user.id}/collections`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUserCollections(data);
      }
    } catch (error) {
      console.error('Error loading user collections:', error);
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

      if (response.ok) {
        loadUserCollections();
      }
    } catch (error) {
      console.error('Error toggling collection item:', error);
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

  // Check if jersey is in user collection
  const isInCollection = (jerseyId, type) => {
    return userCollections[type]?.some(item => item.jersey_id === jerseyId);
  };

  // Get unique leagues and teams for filters
  const availableLeagues = [...new Set(jerseys.map(j => j.league).filter(Boolean))];
  const availableTeams = filters.league 
    ? [...new Set(jerseys.filter(j => j.league === filters.league).map(j => j.team).filter(Boolean))]
    : [...new Set(jerseys.map(j => j.team).filter(Boolean))];

  // Header Component
  const Header = () => (
    <header className="bg-black shadow-lg border-b border-gray-800 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <button
              onClick={() => setCurrentView('home')}
              className="text-2xl font-bold text-white hover:text-gray-300 transition-colors"
            >
              TopKit
            </button>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <button
              onClick={() => setCurrentView('home')}
              className={`${currentView === 'home' 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-300 hover:text-white'
              } px-3 py-2 text-sm font-medium transition-colors`}
            >
              Home
            </button>
            <button
              onClick={() => setCurrentView('explore')}
              className={`${currentView === 'explore' 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-300 hover:text-white'
              } px-3 py-2 text-sm font-medium transition-colors`}
            >
              Explorez
            </button>
            <button
              onClick={() => setCurrentView('marketplace')}
              className={`${currentView === 'marketplace' 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-300 hover:text-white'
              } px-3 py-2 text-sm font-medium transition-colors`}
            >
              Marketplace
            </button>
          </nav>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="hidden md:block">
              <input
                type="text"
                placeholder="Rechercher..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>

            {user ? (
              <div className="flex items-center space-x-3">
                {/* Notifications */}
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="text-gray-300 hover:text-white relative p-2"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5zm-5-17h5l-5 5-5-5h5zm10 10v2a8 8 0 01-16 0V7a8 8 0 0116 0z" />
                  </svg>
                  {(notifications && Array.isArray(notifications) && notifications.filter(n => !n.read).length > 0) && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {notifications.filter(n => !n.read).length}
                    </span>
                  )}
                </button>

                {/* User Menu */}
                <div className="relative">
                  <button
                    onClick={() => setCurrentView('profile')}
                    className="flex items-center text-gray-300 hover:text-white space-x-2"
                  >
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-white">
                        {user.name?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                    <span className="hidden md:block">{user.name}</span>
                  </button>
                </div>

                <button
                  onClick={handleLogout}
                  className="text-gray-300 hover:text-white text-sm"
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Se connecter
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Notifications Dropdown */}
      {showNotifications && user && (
        <div className="absolute right-4 top-16 w-80 bg-gray-900 rounded-lg shadow-xl border border-gray-700 z-50">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-white font-semibold">Notifications</h3>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {(notifications && Array.isArray(notifications) && notifications.length > 0) ? (
              notifications.slice(0, 10).map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-700 last:border-b-0 ${
                    !notification.read ? 'bg-blue-900/20' : ''
                  }`}
                >
                  <div className="text-sm text-white font-medium mb-1">
                    {notification.title}
                  </div>
                  <div className="text-xs text-gray-400">
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

  // Home Page Component
  const HomePage = () => (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-black via-gray-900 to-black">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-black/80"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-24">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              TopKit
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              La marketplace premium pour collectionneurs de maillots de foot
            </p>
            <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto">
              Découvrez les maillots les plus recherchés, connectez-vous avec des collectionneurs passionnés, 
              et trouvez la pièce rare qui manque à votre collection.
            </p>
            
            {/* Search Bar */}
            <div className="max-w-2xl mx-auto mb-12">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Rechercher un maillot, une équipe, un joueur..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full bg-gray-800/50 backdrop-blur-sm text-white px-6 py-4 rounded-2xl border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                />
                <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <button
                onClick={() => setCurrentView('explore')}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all transform hover:scale-105 shadow-lg"
              >
                🔍 Explorez
              </button>
              <button
                onClick={() => setCurrentView('marketplace')}
                className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all transform hover:scale-105 shadow-lg"
              >
                🛒 Marketplace
              </button>
              {user && (
                <button
                  onClick={() => setCurrentView('profile')}
                  className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all transform hover:scale-105 shadow-lg"
                >
                  👤 Ma Collection
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Featured Leagues Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12 text-white">
          Championnat en vedette
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[
            { name: 'Premier League', color: 'from-purple-600 to-pink-600', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
            { name: 'La Liga', color: 'from-red-600 to-yellow-600', flag: '🇪🇸' },
            { name: 'Serie A', color: 'from-green-600 to-red-600', flag: '🇮🇹' },
            { name: 'Bundesliga', color: 'from-black to-red-600', flag: '🇩🇪' },
            { name: 'Ligue 1', color: 'from-blue-600 to-red-600', flag: '🇫🇷' },
            { name: 'Liga Portugal', color: 'from-green-600 to-red-600', flag: '🇵🇹' },
            { name: 'Eredivisie', color: 'from-orange-600 to-blue-600', flag: '🇳🇱' },
            { name: 'MLS', color: 'from-blue-600 to-red-600', flag: '🇺🇸' },
            { name: 'Liga MX', color: 'from-green-600 to-red-600', flag: '🇲🇽' },
            { name: 'Champions League', color: 'from-blue-800 to-purple-800', flag: '🏆' }
          ].map((league) => (
            <button
              key={league.name}
              onClick={() => {
                handleFilterChange({ league: league.name });
                setCurrentView('explore');
              }}
              className={`bg-gradient-to-br ${league.color} p-6 rounded-2xl hover:scale-105 transition-all shadow-lg text-center`}
            >
              <div className="text-2xl mb-2">{league.flag}</div>
              <div className="text-white font-semibold text-sm">{league.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Statistics Section */}
      <div className="bg-gradient-to-r from-gray-900 to-black py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">50K+</div>
              <div className="text-gray-400">Maillots référencés</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-400 mb-2">15K+</div>
              <div className="text-gray-400">Collectionneurs actifs</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-400 mb-2">500+</div>
              <div className="text-gray-400">Équipes couvertes</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-pink-400 mb-2">98%</div>
              <div className="text-gray-400">Satisfaction clients</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Explore Page Component with filters
  const ExplorePage = () => (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header with Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
            <h1 className="text-3xl font-bold mb-4 lg:mb-0">
              Explorez les maillots
            </h1>
            
            {/* View Toggle */}
            <div className="flex items-center space-x-2 bg-gray-800 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="bg-gray-900 p-6 rounded-2xl mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Championnat
                </label>
                <select
                  value={filters.league}
                  onChange={(e) => handleFilterChange({ league: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Tous les championnats</option>
                  {availableLeagues.map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Équipe
                </label>
                <select
                  value={filters.team}
                  onChange={(e) => handleFilterChange({ team: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Toutes les équipes</option>
                  {availableTeams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Saison
                </label>
                <select
                  value={filters.season}
                  onChange={(e) => handleFilterChange({ season: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Toutes les saisons</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2 lg:col-span-2">
                <div className="flex space-x-2">
                  <button
                    onClick={clearFilters}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg transition-colors"
                  >
                    Effacer filtres
                  </button>
                  <div className="flex-1 text-right">
                    <span className="text-gray-400 text-sm">
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
              className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Results */}
        {filteredJerseys.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏟️</div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Aucun maillot trouvé
            </h3>
            <p className="text-gray-400 mb-4">
              Essayez de modifier vos critères de recherche
            </p>
            <button
              onClick={clearFilters}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Voir tous les maillots
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            : "space-y-4"
          }>
            {filteredJerseys.map((jersey) => (
              <div
                key={jersey.id}
                className={viewMode === 'grid'
                  ? "bg-gray-900 rounded-2xl overflow-hidden hover:bg-gray-800 transition-colors shadow-lg"
                  : "bg-gray-900 rounded-2xl p-4 hover:bg-gray-800 transition-colors shadow-lg flex items-center space-x-4"
                }
              >
                {viewMode === 'grid' ? (
                  <>
                    <div className="aspect-square bg-gray-800 flex items-center justify-center">
                      <div className="text-4xl">👕</div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-white mb-1 truncate">
                        {jersey.team}
                      </h3>
                      <p className="text-sm text-gray-400 mb-2">
                        {jersey.league} • {jersey.season}
                      </p>
                      {jersey.player_name && (
                        <p className="text-sm text-blue-400 mb-3">
                          {jersey.player_name}
                        </p>
                      )}
                      
                      {/* Collection buttons */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => toggleCollectionItem(jersey, 'owned')}
                          className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-colors ${
                            isInCollection(jersey.id, 'owned')
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {isInCollection(jersey.id, 'owned') ? '✓ Possédé' : '+ Own'}
                        </button>
                        <button
                          onClick={() => toggleCollectionItem(jersey, 'wanted')}
                          className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-colors ${
                            isInCollection(jersey.id, 'wanted')
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {isInCollection(jersey.id, 'wanted') ? '⭐ Voulu' : '+ Want'}
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                      <div className="text-2xl">👕</div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-white mb-1">
                        {jersey.team}
                      </h3>
                      <p className="text-sm text-gray-400 mb-2">
                        {jersey.league} • {jersey.season}
                      </p>
                      {jersey.player_name && (
                        <p className="text-sm text-blue-400">
                          {jersey.player_name}
                        </p>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => toggleCollectionItem(jersey, 'owned')}
                        className={`py-2 px-4 rounded-lg text-xs font-medium transition-colors ${
                          isInCollection(jersey.id, 'owned')
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {isInCollection(jersey.id, 'owned') ? '✓ Possédé' : '+ Own'}
                      </button>
                      <button
                        onClick={() => toggleCollectionItem(jersey, 'wanted')}
                        className={`py-2 px-4 rounded-lg text-xs font-medium transition-colors ${
                          isInCollection(jersey.id, 'wanted')
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
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
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header with Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
            <h1 className="text-3xl font-bold mb-4 lg:mb-0">
              Marketplace
            </h1>
            
            {/* View Toggle */}
            <div className="flex items-center space-x-2 bg-gray-800 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="bg-gray-900 p-6 rounded-2xl mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Championnat
                </label>
                <select
                  value={filters.league}
                  onChange={(e) => handleFilterChange({ league: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Tous</option>
                  {[...new Set(marketplaceItems.map(item => item.league).filter(Boolean))].map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Équipe
                </label>
                <select
                  value={filters.team}
                  onChange={(e) => handleFilterChange({ team: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Toutes</option>
                  {[...new Set(marketplaceItems.map(item => item.team).filter(Boolean))].map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Prix min
                </label>
                <input
                  type="number"
                  placeholder="0€"
                  value={filters.minPrice}
                  onChange={(e) => handleFilterChange({ minPrice: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Prix max
                </label>
                <input
                  type="number"
                  placeholder="500€"
                  value={filters.maxPrice}
                  onChange={(e) => handleFilterChange({ maxPrice: e.target.value })}
                  className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="md:col-span-2">
                <div className="flex space-x-2 pt-7">
                  <button
                    onClick={clearFilters}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg transition-colors"
                  >
                    Effacer
                  </button>
                  <div className="flex-1 text-right pt-3">
                    <span className="text-gray-400 text-sm">
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
            <h3 className="text-xl font-semibold text-white mb-2">
              Aucun article trouvé
            </h3>
            <p className="text-gray-400 mb-4">
              Essayez de modifier vos critères de recherche
            </p>
            <button
              onClick={clearFilters}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Voir tous les articles
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            : "space-y-4"
          }>
            {filteredMarketplace.map((item) => (
              <div
                key={item.id}
                className={viewMode === 'grid'
                  ? "bg-gray-900 rounded-2xl overflow-hidden hover:bg-gray-800 transition-colors shadow-lg relative"
                  : "bg-gray-900 rounded-2xl p-4 hover:bg-gray-800 transition-colors shadow-lg flex items-center space-x-4"
                }
              >
                {viewMode === 'grid' ? (
                  <>
                    <div className="aspect-square bg-gray-800 flex items-center justify-center relative">
                      <div className="text-4xl">👕</div>
                      {/* Price overlay */}
                      <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded-lg text-sm font-bold">
                        dès {item.min_price}€
                      </div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-white mb-1 truncate">
                        {item.team}
                      </h3>
                      <p className="text-sm text-gray-400 mb-2">
                        {item.league}
                      </p>
                      {item.player_name && (
                        <p className="text-sm text-blue-400 mb-3">
                          {item.player_name}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mb-3">
                        {item.listing_count} annonce{item.listing_count > 1 ? 's' : ''}
                      </p>
                      
                      <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium transition-colors">
                        Voir les annonces
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                      <div className="text-2xl">👕</div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-white mb-1">
                        {item.team}
                      </h3>
                      <p className="text-sm text-gray-400 mb-1">
                        {item.league}
                      </p>
                      {item.player_name && (
                        <p className="text-sm text-blue-400 mb-1">
                          {item.player_name}
                        </p>
                      )}
                      <p className="text-xs text-gray-500">
                        {item.listing_count} annonce{item.listing_count > 1 ? 's' : ''}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 font-bold mb-2">
                        dès {item.min_price}€
                      </div>
                      <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors">
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
              <h3 className="text-xl font-semibold mb-6 text-white">Ma Collection</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Owned Jerseys */}
                <div className="bg-gray-900 rounded-2xl p-6">
                  <h4 className="text-lg font-semibold text-green-400 mb-4 flex items-center">
                    <span className="mr-2">✓</span>
                    Maillots possédés ({userCollections.owned?.length || 0})
                  </h4>
                  {userCollections.owned?.length > 0 ? (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {userCollections.owned.map((item) => (
                        <div key={item.id} className="bg-gray-800 p-3 rounded-lg">
                          <div className="font-medium text-white">
                            {item.jersey?.team || 'Équipe inconnue'}
                          </div>
                          <div className="text-sm text-gray-400">
                            {item.jersey?.league || 'Ligue inconnue'} • {item.jersey?.season || 'Saison inconnue'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <div className="text-4xl mb-2">👕</div>
                      <p>Votre collection est vide</p>
                      <p className="text-sm">Explorez des maillots et ajoutez-les à votre collection</p>
                    </div>
                  )}
                </div>

                {/* Wanted Jerseys */}
                <div className="bg-gray-900 rounded-2xl p-6">
                  <h4 className="text-lg font-semibold text-blue-400 mb-4 flex items-center">
                    <span className="mr-2">⭐</span>
                    Wishlist ({userCollections.wanted?.length || 0})
                  </h4>
                  {userCollections.wanted?.length > 0 ? (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {userCollections.wanted.map((item) => (
                        <div key={item.id} className="bg-gray-800 p-3 rounded-lg">
                          <div className="font-medium text-white">
                            {item.jersey?.team || 'Équipe inconnue'}
                          </div>
                          <div className="text-sm text-gray-400">
                            {item.jersey?.league || 'Ligue inconnue'} • {item.jersey?.season || 'Saison inconnue'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
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
                <h3 className="text-xl font-semibold text-white">Mes Soumissions</h3>
                <button
                  onClick={() => {
                    console.log('Submit button clicked!');
                    console.log('Current showSubmitModal state:', showSubmitModal);
                    setShowSubmitModal(true);
                    console.log('Modal state should be true now');
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Soumettre un maillot
                </button>
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Total', value: userSubmissions.length, color: 'blue' },
                  { label: 'En attente', value: userSubmissions.filter(s => s.status === 'pending').length, color: 'yellow' },
                  { label: 'Approuvés', value: userSubmissions.filter(s => s.status === 'approved').length, color: 'green' },
                  { label: 'Refusés', value: userSubmissions.filter(s => s.status === 'rejected').length, color: 'red' }
                ].map((stat) => (
                  <div key={stat.label} className="bg-gray-900 p-4 rounded-lg text-center">
                    <div className={`text-2xl font-bold text-${stat.color}-400 mb-1`}>
                      {stat.value}
                    </div>
                    <div className="text-sm text-gray-400">{stat.label}</div>
                  </div>
                ))}
              </div>

              {/* Submissions List */}
              {userSubmissions.length > 0 ? (
                <div className="space-y-4">
                  {userSubmissions.map((submission) => (
                    <div key={submission.id} className="bg-gray-900 p-6 rounded-2xl">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="text-lg font-semibold text-white">
                            {submission.team} - {submission.player_name || 'Joueur non spécifié'}
                          </h4>
                          <p className="text-gray-400">
                            {submission.league} • {submission.season}
                          </p>
                          <p className="text-sm text-gray-500">
                            Réf: {submission.reference}
                          </p>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            submission.status === 'approved' ? 'bg-green-900 text-green-300' :
                            submission.status === 'pending' ? 'bg-yellow-900 text-yellow-300' :
                            'bg-red-900 text-red-300'
                          }`}>
                            {submission.status === 'approved' ? 'Approuvé' :
                             submission.status === 'pending' ? 'En attente' : 'Refusé'}
                          </span>
                          {(submission.status === 'rejected' || (submission.status === 'needs_modification')) && (
                            <button
                              onClick={() => openJerseyEditor(submission)}
                              className="text-blue-400 hover:text-blue-300 text-sm"
                            >
                              Modifier
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {/* Admin feedback */}
                      {submission.admin_feedback && (
                        <div className="bg-gray-800 p-3 rounded-lg">
                          <div className="text-sm text-gray-300">
                            <strong>Retour admin:</strong> {submission.admin_feedback}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-400">
                  <div className="text-6xl mb-4">📝</div>
                  <h3 className="text-xl font-semibold mb-2">Aucune soumission</h3>
                  <p className="mb-4">Vous n'avez pas encore soumis de maillot</p>
                  <button
                    onClick={() => setShowSubmitModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Soumettre votre premier maillot
                  </button>
                </div>
              )}
            </div>
          );

        case 'listings':
          return (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏗️</div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Bientôt disponible
              </h3>
              <p className="text-gray-400 mb-6">
                La fonctionnalité de vente sera bientôt disponible. En attendant, vous pourrez :
              </p>
              <div className="bg-gray-900 p-6 rounded-2xl max-w-md mx-auto">
                <ul className="text-left text-gray-300 space-y-3">
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">✓</span>
                    Créer vos annonces de vente
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">✓</span>
                    Fixer vos prix et conditions
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">✓</span>
                    Recevoir des messages d'acheteurs
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">✓</span>
                    Suivre vos ventes en temps réel
                  </li>
                </ul>
              </div>
            </div>
          );

        case 'friends':
          return (
            <div>
              <h3 className="text-xl font-semibold mb-6 text-white">Mes Amis</h3>
              {friends.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {friends.map((friend) => (
                    <div key={friend.id} className="bg-gray-900 p-4 rounded-2xl">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                          <span className="text-white font-medium">
                            {friend.name?.charAt(0).toUpperCase() || 'U'}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-white">{friend.name}</div>
                          <div className="text-sm text-gray-400">{friend.email}</div>
                        </div>
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-700">
                        <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium transition-colors">
                          Envoyer un message
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-400">
                  <div className="text-6xl mb-4">👥</div>
                  <h3 className="text-xl font-semibold mb-2">Aucun ami</h3>
                  <p className="mb-4">Commencez à vous connecter avec d'autres collectionneurs</p>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    Rechercher des amis
                  </button>
                </div>
              )}
            </div>
          );

        case 'messages':
          return (
            <div className="text-center py-12 text-gray-400">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-xl font-semibold mb-2">Messages</h3>
              <p>Fonctionnalité de messagerie en développement</p>
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div className="min-h-screen bg-black text-white p-4">
        <div className="max-w-7xl mx-auto">
          {/* Profile Header */}
          <div className="bg-gradient-to-r from-gray-900 to-black p-8 rounded-2xl mb-8">
            <div className="flex items-center space-x-6">
              <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">{user?.name || 'Utilisateur'}</h1>
                <p className="text-gray-400">{user?.email}</p>
                <div className="flex items-center space-x-6 mt-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{userCollections.owned?.length || 0}</div>
                    <div className="text-sm text-gray-400">Possédés</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">{userCollections.wanted?.length || 0}</div>
                    <div className="text-sm text-gray-400">Recherchés</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{userSubmissions.length || 0}</div>
                    <div className="text-sm text-gray-400">Soumissions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-pink-400">{friends.length || 0}</div>
                    <div className="text-sm text-gray-400">Amis</div>
                  </div>
                </div>
              </div>
              
              {/* Admin Panel Access */}
              {user?.role === 'admin' && (
                <div className="ml-auto">
                  <button
                    onClick={() => setCurrentView('admin')}
                    className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-6 py-3 rounded-lg font-semibold transition-all flex items-center space-x-2"
                  >
                    <span>🔧</span>
                    <span>Admin Panel</span>
                  </button>
                  <button
                    onClick={() => setShowSecurityModal(true)}
                    className="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-all flex items-center space-x-2 mt-2"
                  >
                    <span>🔒</span>
                    <span>Settings</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="bg-gray-900 rounded-2xl p-2 mb-8">
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
                  className={`flex items-center space-x-2 px-4 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${
                    activeTab === tab.key
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="bg-gray-900/50 rounded-2xl p-8">
            {renderTabContent()}
          </div>
        </div>
      </div>
    );
  };

  // Admin Panel Component (simplified)
  const AdminPanel = () => (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-red-900 to-black p-8 rounded-2xl mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">🔧 Admin Panel</h1>
          <p className="text-gray-400">Gestion de la plateforme TopKit</p>
        </div>
        
        <div className="text-center py-12 text-gray-400">
          <div className="text-6xl mb-4">🚧</div>
          <h3 className="text-xl font-semibold mb-2">Panel d'administration</h3>
          <p className="mb-4">Interface d'administration complète disponible</p>
          <button
            onClick={() => setCurrentView('profile')}
            className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Retour au profil
          </button>
        </div>
      </div>
    </div>
  );

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
          onUpdateSuccess={handleJerseyUpdate}
          jersey={editingJersey}
          user={user}
        />
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