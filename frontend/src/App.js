import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

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

const API = process.env.REACT_APP_BACKEND_URL;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('AuthProvider mounted, checking for existing token...');
    const token = localStorage.getItem('token');
    console.log('Token found in localStorage:', token ? token.substring(0, 20) + '...' : 'none');
    if (token) {
      console.log('Calling fetchProfile with existing token');
      fetchProfile(token);
    } else {
      console.log('No token found, setting loading to false');
      setLoading(false);
    }
  }, []);

  const fetchProfile = async (token) => {
    try {
      console.log('Fetching profile with token:', token.substring(0, 20) + '...');
      const response = await axios.get(`${API}/api/profile`, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000
      });
      console.log('Profile response:', response.data);
      if (response.data?.user) {
        setUser(response.data.user);
        console.log('✅ Profile loaded successfully:', response.data.user);
      } else {
        console.error('❌ Invalid profile response structure:', response.data);
        localStorage.removeItem('token');
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      console.error('Error response:', error.response?.data);
      localStorage.removeItem('token');
      setUser(null);
      setLoading(false);
    }
  };

  const login = (token, userData) => {
    console.log('🔑 Login called with token:', token ? token.substring(0, 20) + '...' : 'NO TOKEN');
    console.log('👤 Login called with user data:', userData);
    
    if (!token || !userData) {
      console.error('❌ Login failed: missing token or userData');
      return false;
    }
    
    try {
      localStorage.setItem('token', token);
      console.log('💾 Token saved to localStorage');
      
      // Set user data and stop loading immediately
      setUser(userData);
      setLoading(false);
      console.log('✅ Login successful - user state set:', userData);
      return true;
    } catch (error) {
      console.error('❌ Login failed during state update:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Loading Spinner Component
const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };
  
  return (
    <div className={`${sizeClasses[size]} ${className} animate-spin rounded-full border-2 border-gray-300 border-t-blue-600`}></div>
  );
};

// Toast Notification Component
const Toast = ({ message, type = 'success', onClose }) => {
  const typeClasses = {
    success: 'bg-green-600 text-white',
    error: 'bg-red-600 text-white',
    info: 'bg-blue-600 text-white',
    warning: 'bg-yellow-600 text-white'
  };
  
  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠'
  };
  
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 4000);
    
    return () => clearTimeout(timer);
  }, [onClose]);
  
  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out ${typeClasses[type]} animate-pulse`}>
      <div className="flex items-center space-x-2">
        <span className="text-lg">{icons[type]}</span>
        <span className="font-medium">{message}</span>
        <button 
          onClick={onClose}
          className="ml-4 text-white hover:text-gray-200 font-bold"
        >
          ×
        </button>
      </div>
    </div>
  );
};

// Enhanced Button Component
const Button = ({ children, variant = 'primary', size = 'md', loading = false, disabled = false, className = '', ...props }) => {
  const baseClasses = 'font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500 hover:scale-105 shadow-lg',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500 hover:scale-105 shadow-lg',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500 hover:scale-105 shadow-lg',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 hover:scale-105 shadow-lg',
    outline: 'border-2 border-gray-300 hover:border-gray-400 text-gray-700 hover:bg-gray-50 focus:ring-gray-500'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="flex items-center justify-center space-x-2">
          <LoadingSpinner size="sm" />
          <span>Loading...</span>
        </div>
      ) : children}
    </button>
  );
};

// Notification Bell Component
const NotificationBell = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch notifications
  const fetchNotifications = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/notifications?limit=10`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNotifications(response.data.notifications || []);
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/notifications/${notificationId}/mark-read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setNotifications(notifications.map(notif => 
        notif.id === notificationId ? { ...notif, is_read: true } : notif
      ));
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/notifications/mark-all-read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setNotifications(notifications.map(notif => ({ ...notif, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  // Fetch notifications on mount and when user changes
  useEffect(() => {
    if (user) {
      fetchNotifications();
      // Refresh notifications every 30 seconds
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  // Don't render if user is not logged in
  if (!user) return null;

  return (
    <div className="relative">
      {/* Notification Bell Button */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 text-gray-300 hover:text-white transition-colors"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5zM12 3a7 7 0 00-7 7v4.09L3 16l1.82.91L12 21l7.18-4.09L21 16l-2-1.91V10a7 7 0 00-7-7z" />
        </svg>
        
        {/* Unread Count Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notifications Dropdown */}
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-gray-900 rounded-lg shadow-xl border border-gray-700 z-50">
          <div className="p-4 border-b border-gray-700">
            <div className="flex justify-between items-center">
              <h3 className="text-white font-semibold">Notifications</h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  Mark all read
                </button>
              )}
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-400">
                <LoadingSpinner size="sm" className="mx-auto mb-2" />
                Loading notifications...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                No notifications yet
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800 transition-colors ${
                    !notification.is_read ? 'bg-blue-900/20' : ''
                  }`}
                  onClick={() => !notification.is_read && markAsRead(notification.id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className={`font-medium ${!notification.is_read ? 'text-white' : 'text-gray-300'}`}>
                        {notification.title}
                      </h4>
                      <p className="text-gray-400 text-sm mt-1">{notification.message}</p>
                      <p className="text-gray-500 text-xs mt-2">
                        {new Date(notification.created_at).toLocaleDateString()} {new Date(notification.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                    {!notification.is_read && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-1 ml-2"></div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="p-3 border-t border-gray-700">
            <button
              onClick={() => setShowDropdown(false)}
              className="w-full bg-gray-800 hover:bg-gray-700 text-white py-2 rounded-lg transition-colors text-sm"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Avatar Component with default styling
const Avatar = ({ user, size = 'sm', className = '', onClick }) => {
  const sizeClasses = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-sm', 
    md: 'w-12 h-12 text-base',
    lg: 'w-16 h-16 text-lg',
    xl: 'w-20 h-20 text-xl'
  };
  
  const baseClasses = `${sizeClasses[size]} rounded-full border-2 border-gray-600 flex items-center justify-center font-semibold transition-all hover:border-gray-400 ${className} ${onClick ? 'cursor-pointer' : ''}`;
  
  // If user has profile picture
  if (user?.picture) {
    return (
      <img 
        src={user.picture} 
        alt={user.name || 'User'}
        className={`${baseClasses} object-cover`}
        onClick={onClick}
        onError={(e) => {
          // Fallback to initials if image fails to load
          e.target.style.display = 'none';
          e.target.nextSibling.style.display = 'flex';
        }}
      />
    );
  }
  
  // Generate initials from name
  const initials = user?.name 
    ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : '?';
    
  // Beautiful gradient background
  const gradients = [
    'bg-gradient-to-br from-blue-500 to-purple-600',
    'bg-gradient-to-br from-green-500 to-blue-600', 
    'bg-gradient-to-br from-pink-500 to-red-600',
    'bg-gradient-to-br from-yellow-500 to-orange-600',
    'bg-gradient-to-br from-indigo-500 to-purple-600',
    'bg-gradient-to-br from-teal-500 to-cyan-600'
  ];
  
  // Generate consistent gradient based on user name/id
  const gradientIndex = user?.name 
    ? user.name.charCodeAt(0) % gradients.length 
    : 0;
    
  return (
    <div className={`${baseClasses} ${gradients[gradientIndex]} text-white shadow-lg`} onClick={onClick}>
      {initials}
    </div>
  );
};

// Header Component
const Header = ({ currentView, setCurrentView }) => {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Debug user state in Header
  useEffect(() => {
    console.log('🎯 Header - user state changed:', user);
    console.log('🎯 Header - user is:', user ? 'LOGGED IN' : 'NOT LOGGED IN');
    console.log('🎯 Header - will show navigation:', user ? 'YES' : 'NO');
  }, [user]);

  return (
    <>
      {/* Main Header: Logo centré + Login à droite */}
      <header className="bg-black text-white shadow-2xl border-b border-gray-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            {/* Espace gauche (pour équilibrer) */}
            <div className="flex-1"></div>
            
            {/* Logo centré */}
            <div className="flex justify-center flex-1">
              <img 
                src="https://customer-assets.emergentagent.com/job_football-threads-5/artifacts/d38ypztj_ho7nwfgn_topkit_logo_nobc_wh.png"
                alt="TopKit Logo"
                className="h-12 w-auto cursor-pointer hover:opacity-80 transition-opacity"
                onClick={() => setCurrentView('home')}
                style={{ maxWidth: 'none', flexShrink: 0 }}
              />
            </div>
            
            {/* Login/Logout à droite */}
            <div className="flex justify-end flex-1">
              {user ? (
                <div className="flex items-center space-x-4">
                  <NotificationBell />
                  <div className="flex items-center space-x-3">
                    <Avatar 
                      user={user} 
                      size="md" 
                      className="hover:scale-105 cursor-pointer hover:border-blue-400" 
                      onClick={() => setCurrentView('profile')}
                    />
                    <div className="flex flex-col">
                      <span className="text-white font-medium text-sm">Welcome back!</span>
                      <span className="text-gray-300 text-xs">{user.name}</span>
                    </div>
                  </div>
                  <button 
                    onClick={logout}
                    className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-all duration-200 border border-gray-600 text-sm font-medium hover:scale-105 shadow-lg"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button 
                  onClick={() => setShowAuthModal(true)}
                  className="bg-white text-black px-6 py-2 rounded-lg font-semibold hover:bg-gray-200 transition-all duration-200 hover:scale-105 shadow-lg"
                >
                  Login / Sign Up
                </button>
              )}
            </div>
          </div>
        </div>
        
        {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      </header>

      {/* Navigation Bar: En dessous du header */}
      <nav className="bg-gray-900 shadow-sm border-b border-gray-800">
        <div className="container mx-auto px-6">
          <div className="flex justify-center items-center space-x-8 py-3">
            <button 
              onClick={() => setCurrentView('home')}
              className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                currentView === 'home' 
                  ? 'bg-white text-black' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
            >
              Home
            </button>
            <button 
              onClick={() => setCurrentView('jerseys')}
              className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                currentView === 'jerseys' 
                  ? 'bg-white text-black' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
            >
              Browse Jerseys
            </button>
            <button 
              onClick={() => setCurrentView('marketplace')}
              className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                currentView === 'marketplace' 
                  ? 'bg-white text-black' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
            >
              Marketplace
            </button>
            {user && (
              <>
                <button 
                  onClick={() => setCurrentView('profile')}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    currentView === 'profile' 
                      ? 'bg-white text-black' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  Profile
                </button>
                <button 
                  onClick={() => setCurrentView('collections')}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    currentView === 'collections' 
                      ? 'bg-white text-black' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  My Collection
                </button>
                {user.email === 'topkitfr@gmail.com' && (
                  <button 
                    onClick={() => setCurrentView('admin')}
                    className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                      currentView === 'admin' 
                        ? 'bg-red-600 text-white' 
                        : 'text-red-400 hover:text-white hover:bg-red-800'
                    }`}
                  >
                    🔧 Admin Panel
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </nav>
    </>
  );
};

// Image Upload Component
const ImageUpload = ({ images, setImages }) => {
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploading(true);
    const newImages = [];

    for (const file of files) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        alert(`File ${file.name} is too large. Maximum size is 5MB.`);
        continue;
      }

      if (!file.type.startsWith('image/')) {
        alert(`File ${file.name} is not an image.`);
        continue;
      }

      // Convert to base64 for demo purposes
      // In production, you'd upload to a cloud storage service
      const reader = new FileReader();
      reader.onload = (e) => {
        newImages.push(e.target.result);
        if (newImages.length === files.filter(f => f.type.startsWith('image/') && f.size <= 5 * 1024 * 1024).length) {
          setImages([...images, ...newImages]);
          setUploading(false);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUrlAdd = () => {
    const url = prompt('Enter image URL:');
    if (url) {
      setImages([...images, url]);
    }
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div className="flex space-x-3">
        <label className="bg-white text-black px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer text-sm font-semibold">
          {uploading ? 'Uploading...' : 'Upload Photos'}
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
            disabled={uploading}
          />
        </label>
        <button
          type="button"
          onClick={handleUrlAdd}
          className="bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm font-semibold border border-gray-600"
        >
          Add URL
        </button>
      </div>

      {images.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {images.map((image, index) => (
            <div key={index} className="relative group">
              <img 
                src={image} 
                alt={`Jersey ${index + 1}`}
                className="w-full h-24 object-cover rounded border border-gray-600"
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/100x100?text=Invalid+Image';
                }}
              />
              <button
                type="button"
                onClick={() => removeImage(index)}
                className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-6 h-6 text-xs hover:bg-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Jersey Detail Modal Component
const JerseyDetailModal = ({ jersey, listing = null, onClose }) => {
  const { user } = useAuth();
  const [showContactSeller, setShowContactSeller] = useState(false);

  const handleContactSeller = () => {
    if (!user) {
      alert('Please login to contact sellers');
      return;
    }
    setShowContactSeller(true);
  };

  const handleBuyNow = () => {
    if (!user) {
      alert('Please login to buy jerseys');
      return;
    }
    // Implement buy now functionality
    alert('Buy now functionality will be implemented with payment system');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-4xl w-full max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center p-6 border-b border-gray-800">
          <h2 className="text-2xl font-bold text-white">Jersey Details</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Image Gallery */}
            <div>
              <div className="bg-gray-800 rounded-lg overflow-hidden mb-4">
                <img
                  src={jersey.images?.[0] || 'https://via.placeholder.com/400x500?text=Jersey+Image'}
                  alt={`${jersey.team} ${jersey.season}`}
                  className="w-full h-96 object-cover"
                />
              </div>
              {jersey.images && jersey.images.length > 1 && (
                <div className="grid grid-cols-4 gap-2">
                  {jersey.images.slice(1, 5).map((image, index) => (
                    <img
                      key={index}
                      src={image}
                      alt={`Jersey ${index + 2}`}
                      className="w-full h-16 object-cover rounded border border-gray-700 cursor-pointer hover:border-white transition-colors"
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Jersey Details */}
            <div className="space-y-6">
              <div>
                <h3 className="text-3xl font-bold text-white mb-2">{jersey.team}</h3>
                <p className="text-xl text-gray-300">{jersey.season} • {jersey.home_away}</p>
                {jersey.player && <p className="text-2xl text-white font-semibold mt-2">{jersey.player}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-gray-400">Size:</span>
                  <span className="text-white ml-2 font-semibold">{jersey.size}</span>
                </div>
                <div>
                  <span className="text-gray-400">Condition:</span>
                  <span className="text-white ml-2 font-semibold capitalize">{jersey.condition}</span>
                </div>
                <div>
                  <span className="text-gray-400">Manufacturer:</span>
                  <span className="text-white ml-2 font-semibold">{jersey.manufacturer}</span>
                </div>
                <div>
                  <span className="text-gray-400">League:</span>
                  <span className="text-white ml-2 font-semibold">{jersey.league}</span>
                </div>
              </div>

              {listing && (
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-gray-400">Listed Price:</span>
                    <span className="text-3xl font-bold text-white">${listing.price}</span>
                  </div>
                  <p className="text-gray-300 mb-4">{listing.description}</p>
                  
                  <div className="space-y-3">
                    <button 
                      onClick={handleBuyNow}
                      className="w-full bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
                    >
                      Buy Now - ${listing.price}
                    </button>
                    <button 
                      onClick={handleContactSeller}
                      className="w-full bg-gray-700 text-white py-3 rounded-lg hover:bg-gray-600 transition-colors font-semibold border border-gray-600"
                    >
                      Contact Seller
                    </button>
                  </div>
                </div>
              )}

              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Description</h4>
                <p className="text-gray-300 leading-relaxed">{jersey.description}</p>
              </div>
            </div>
          </div>
        </div>

        {showContactSeller && listing && (
          <ContactSellerModal
            listing={listing}
            onClose={() => setShowContactSeller(false)}
          />
        )}
      </div>
    </div>
  );
};

// Contact Seller Modal
const ContactSellerModal = ({ listing, onClose }) => {
  const [message, setMessage] = useState('');
  const [sellerInfo, setSellerInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSellerInfo();
  }, []);

  const fetchSellerInfo = async () => {
    try {
      const response = await axios.get(`${API}/api/users/${listing.seller_id}/public`);
      setSellerInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch seller info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim()) {
      alert('Please enter a message');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/messages`, {
        recipient_id: listing.seller_id,
        listing_id: listing.id,
        message: message.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Message sent successfully!');
      onClose();
    } catch (error) {
      alert('Failed to send message. Please try again.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-60 p-4">
      <div className="bg-gray-900 rounded-xl max-w-md w-full border border-gray-800">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-white">Contact Seller</h3>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          {loading ? (
            <div className="text-center py-4 text-gray-400">Loading seller info...</div>
          ) : sellerInfo ? (
            <div className="mb-6">
              <div className="flex items-center space-x-3 mb-4">
                {sellerInfo.picture && (
                  <img 
                    src={sellerInfo.picture} 
                    alt={sellerInfo.name}
                    className="w-12 h-12 rounded-full"
                  />
                )}
                <div>
                  <h4 className="text-white font-semibold">{sellerInfo.name}</h4>
                  <p className="text-gray-400 text-sm">Jersey Collector</p>
                </div>
              </div>
              
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Hi! I'm interested in your jersey listing. Is it still available?"
                className="w-full h-32 bg-gray-800 border border-gray-700 rounded-lg p-3 text-white placeholder-gray-400 resize-none focus:ring-2 focus:ring-white focus:border-transparent"
              />
            </div>
          ) : (
            <div className="text-center py-4 text-red-400">Failed to load seller information</div>
          )}

          <div className="flex space-x-3">
            <button 
              onClick={onClose}
              className="flex-1 bg-gray-800 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors border border-gray-600"
            >
              Cancel
            </button>
            <button 
              onClick={handleSendMessage}
              disabled={!message.trim() || loading}
              className="flex-1 bg-white text-black py-2 rounded-lg hover:bg-gray-200 transition-colors font-semibold disabled:opacity-50"
            >
              Send Message
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Add Jersey Modal Component (for adding jersey to collection without listing)
const AddJerseyModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    team: '',
    season: '',
    player: '',
    size: 'M',
    condition: 'excellent',
    manufacturer: '',
    home_away: 'home',
    league: '',
    description: '',
    reference_code: '',
    images: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedLeague, setSelectedLeague] = useState('');
  const [availableTeams, setAvailableTeams] = useState([]);

  // Update available teams when league changes
  useEffect(() => {
    if (selectedLeague && LEAGUES_DATA[selectedLeague]) {
      setAvailableTeams(LEAGUES_DATA[selectedLeague]);
      if (!LEAGUES_DATA[selectedLeague].includes(formData.team)) {
        setFormData({...formData, team: '', league: selectedLeague});
      }
    } else {
      setAvailableTeams([]);
    }
  }, [selectedLeague]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to add a jersey');
      }

      // Create jersey only (no listing)
      const jerseyData = {
        team: formData.team,
        season: formData.season,
        player: formData.player || null,
        size: formData.size,
        condition: formData.condition,
        manufacturer: formData.manufacturer,
        home_away: formData.home_away,
        league: formData.league,
        description: formData.description,
        images: formData.images,
        reference_code: formData.reference_code
      };

      const jerseyResponse = await axios.post(`${API}/api/jerseys`, jerseyData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const jerseyId = jerseyResponse.data.id;
      
      // Automatically add the jersey to the user's owned collection
      try {
        await axios.post(`${API}/api/collections`, {
          jersey_id: jerseyId,
          collection_type: 'owned'
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (collectionError) {
        console.warn('Failed to add jersey to collection automatically:', collectionError);
      }

      alert('Jersey added to your collection successfully!');
      onClose();
      // Trigger refresh of collections
      window.location.reload();
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'Failed to add jersey');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-4xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Add New Jersey</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="border border-gray-700 rounded-lg p-6 bg-gray-800">
            <h3 className="text-lg font-semibold mb-4 text-white">Jersey Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">League*</label>
                <select
                  value={selectedLeague}
                  onChange={(e) => setSelectedLeague(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select League</option>
                  {Object.keys(LEAGUES_DATA).map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Club/National Team*</label>
                <select
                  value={formData.team}
                  onChange={(e) => setFormData({...formData, team: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                  disabled={!selectedLeague}
                >
                  <option value="">Select Team</option>
                  {availableTeams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Season*</label>
                <select
                  value={formData.season}
                  onChange={(e) => setFormData({...formData, season: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select Season</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Brand/Manufacturer*</label>
                <select
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select Brand</option>
                  <option value="Adidas">Adidas</option>
                  <option value="Nike">Nike</option>
                  <option value="Puma">Puma</option>
                  <option value="New Balance">New Balance</option>
                  <option value="Under Armour">Under Armour</option>
                  <option value="Hummel">Hummel</option>
                  <option value="Kappa">Kappa</option>
                  <option value="Umbro">Umbro</option>
                  <option value="Macron">Macron</option>
                  <option value="Errea">Errea</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Player Name</label>
                <input
                  type="text"
                  placeholder="e.g., Bruno Fernandes (optional)"
                  value={formData.player}
                  onChange={(e) => setFormData({...formData, player: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Code Référence</label>
                <input
                  type="text"
                  placeholder="e.g., 779963-01"
                  value={formData.reference_code}
                  onChange={(e) => setFormData({...formData, reference_code: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Type*</label>
                <select
                  value={formData.home_away}
                  onChange={(e) => setFormData({...formData, home_away: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="home">Home</option>
                  <option value="away">Away</option>
                  <option value="third">Third Kit</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Size*</label>
                <select
                  value={formData.size}
                  onChange={(e) => setFormData({...formData, size: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="XS">XS</option>
                  <option value="S">S</option>
                  <option value="M">M</option>
                  <option value="L">L</option>
                  <option value="XL">XL</option>
                  <option value="XXL">XXL</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Condition*</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="mint">Mint</option>
                  <option value="excellent">Excellent</option>
                  <option value="very_good">Very Good</option>
                  <option value="good">Good</option>
                  <option value="fair">Fair</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                <textarea
                  placeholder="Add details about the jersey, special features, etc."
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-20"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">Jersey Photos</label>
                <ImageUpload 
                  images={formData.images}
                  setImages={(images) => setFormData({...formData, images})}
                />
                <p className="text-xs text-gray-400 mt-2">
                  Upload photos of your jersey. Optional but recommended.
                </p>
              </div>
            </div>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 font-semibold"
            >
              {loading ? 'Adding Jersey...' : 'Add to Collection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Submit Jersey Modal Component (for submitting new jerseys to the database)
const SubmitJerseyModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    team: '',
    season: '',
    player: '',
    size: 'M',
    condition: 'excellent',
    manufacturer: '',
    home_away: 'home',
    league: '',
    description: '',
    reference_code: '',
    images: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedLeague, setSelectedLeague] = useState('');
  const [availableTeams, setAvailableTeams] = useState([]);

  // Update available teams when league changes
  useEffect(() => {
    if (selectedLeague && LEAGUES_DATA[selectedLeague]) {
      setAvailableTeams(LEAGUES_DATA[selectedLeague]);
      if (!LEAGUES_DATA[selectedLeague].includes(formData.team)) {
        setFormData({...formData, team: '', league: selectedLeague});
      }
    } else {
      setAvailableTeams([]);
    }
  }, [selectedLeague]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to submit a jersey');
      }

      // Create jersey submission
      const jerseyData = {
        team: formData.team,
        season: formData.season,
        player: formData.player || null,
        size: formData.size,
        condition: formData.condition,
        manufacturer: formData.manufacturer,
        home_away: formData.home_away,
        league: formData.league,
        description: formData.description,
        images: formData.images,
        reference_code: formData.reference_code
      };

      await axios.post(`${API}/api/jerseys`, jerseyData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Jersey submitted successfully for review!');
      if (onSuccess) onSuccess();
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'Failed to submit jersey');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-4xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Submit New Jersey</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <div className="text-blue-400 text-xl mr-3 mt-1">ℹ️</div>
            <div>
              <h3 className="text-blue-300 font-semibold mb-2">Submission Process</h3>
              <p className="text-blue-200 text-sm leading-relaxed">
                All jersey submissions are reviewed by our moderation team before being published. 
                This ensures database quality and prevents duplicates.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="border border-gray-700 rounded-lg p-6 bg-gray-800">
            <h3 className="text-lg font-semibold mb-4 text-white">Jersey Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">League*</label>
                <select
                  value={selectedLeague}
                  onChange={(e) => setSelectedLeague(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select League</option>
                  {Object.keys(LEAGUES_DATA).map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Club/National Team*</label>
                <select
                  value={formData.team}
                  onChange={(e) => setFormData({...formData, team: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                  disabled={!selectedLeague}
                >
                  <option value="">Select Team</option>
                  {availableTeams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Season*</label>
                <select
                  value={formData.season}
                  onChange={(e) => setFormData({...formData, season: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select Season</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Brand/Manufacturer*</label>
                <select
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select Brand</option>
                  <option value="Adidas">Adidas</option>
                  <option value="Nike">Nike</option>
                  <option value="Puma">Puma</option>
                  <option value="New Balance">New Balance</option>
                  <option value="Under Armour">Under Armour</option>
                  <option value="Hummel">Hummel</option>
                  <option value="Kappa">Kappa</option>
                  <option value="Umbro">Umbro</option>
                  <option value="Macron">Macron</option>
                  <option value="Errea">Errea</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Player Name</label>
                <input
                  type="text"
                  placeholder="e.g., Bruno Fernandes (optional)"
                  value={formData.player}
                  onChange={(e) => setFormData({...formData, player: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Reference Code</label>
                <input
                  type="text"
                  placeholder="e.g., 779963-01"
                  value={formData.reference_code}
                  onChange={(e) => setFormData({...formData, reference_code: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Type*</label>
                <select
                  value={formData.home_away}
                  onChange={(e) => setFormData({...formData, home_away: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="home">Home</option>
                  <option value="away">Away</option>
                  <option value="third">Third Kit</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Size*</label>
                <select
                  value={formData.size}
                  onChange={(e) => setFormData({...formData, size: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="XS">XS</option>
                  <option value="S">S</option>
                  <option value="M">M</option>
                  <option value="L">L</option>
                  <option value="XL">XL</option>
                  <option value="XXL">XXL</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Condition*</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="mint">Mint</option>
                  <option value="excellent">Excellent</option>
                  <option value="very_good">Very Good</option>
                  <option value="good">Good</option>
                  <option value="fair">Fair</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                <textarea
                  placeholder="Add details about the jersey, special features, etc."
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-20"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">Jersey Photos</label>
                <ImageUpload 
                  images={formData.images}
                  setImages={(images) => setFormData({...formData, images})}
                />
                <p className="text-xs text-gray-400 mt-2">
                  Upload photos of the jersey. Optional but recommended for approval.
                </p>
              </div>
            </div>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 font-semibold"
            >
              {loading ? 'Submitting for Review...' : 'Submit for Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Resubmission Modal Component (for resubmitting jerseys with modifications)
const ResubmissionModal = ({ originalJersey, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    team: originalJersey?.team || '',
    season: originalJersey?.season || '',
    player: originalJersey?.player || '',
    size: originalJersey?.size || 'M',
    condition: originalJersey?.condition || 'excellent',
    manufacturer: originalJersey?.manufacturer || '',
    home_away: originalJersey?.home_away || 'home',
    league: originalJersey?.league || '',
    description: originalJersey?.description || '',
    reference_code: originalJersey?.reference_code || '',
    images: originalJersey?.images || []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedLeague, setSelectedLeague] = useState(originalJersey?.league || '');
  const [availableTeams, setAvailableTeams] = useState([]);

  // Update available teams when league changes
  useEffect(() => {
    if (selectedLeague && LEAGUES_DATA[selectedLeague]) {
      setAvailableTeams(LEAGUES_DATA[selectedLeague]);
      if (!LEAGUES_DATA[selectedLeague].includes(formData.team)) {
        setFormData({...formData, team: '', league: selectedLeague});
      }
    } else {
      setAvailableTeams([]);
    }
  }, [selectedLeague]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to resubmit a jersey');
      }

      // Create jersey resubmission with the original jersey ID
      const jerseyData = {
        team: formData.team,
        season: formData.season,
        player: formData.player || null,
        size: formData.size,
        condition: formData.condition,
        manufacturer: formData.manufacturer,
        home_away: formData.home_away,
        league: formData.league,
        description: formData.description,
        images: formData.images,
        reference_code: formData.reference_code
      };

      await axios.post(`${API}/api/jerseys?resubmission_id=${originalJersey.id}`, jerseyData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Jersey resubmitted successfully for review!');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'Failed to resubmit jersey');
    } finally {
      setLoading(false);
    }
  };

  if (!originalJersey) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-4xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Resubmit Jersey with Modifications</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <div className="text-blue-400 text-xl mr-3 mt-1">🔄</div>
            <div>
              <h3 className="text-blue-300 font-semibold mb-2">Resubmission Process</h3>
              <p className="text-blue-200 text-sm leading-relaxed">
                You are resubmitting your jersey with modifications based on moderator feedback. 
                Make sure to address all the suggested changes before submitting.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="border border-gray-700 rounded-lg p-6 bg-gray-800">
            <h3 className="text-lg font-semibold mb-4 text-white">Updated Jersey Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">League*</label>
                <select
                  value={selectedLeague}
                  onChange={(e) => setSelectedLeague(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select League</option>
                  {Object.keys(LEAGUES_DATA).map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Club/National Team*</label>
                <select
                  value={formData.team}
                  onChange={(e) => setFormData({...formData, team: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                  disabled={!selectedLeague}
                >
                  <option value="">Select Team</option>
                  {availableTeams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Season*</label>
                <select
                  value={formData.season}
                  onChange={(e) => setFormData({...formData, season: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select Season</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Brand/Manufacturer*</label>
                <select
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Select Brand</option>
                  <option value="Adidas">Adidas</option>
                  <option value="Nike">Nike</option>
                  <option value="Puma">Puma</option>
                  <option value="New Balance">New Balance</option>
                  <option value="Under Armour">Under Armour</option>
                  <option value="Hummel">Hummel</option>
                  <option value="Kappa">Kappa</option>
                  <option value="Umbro">Umbro</option>
                  <option value="Macron">Macron</option>
                  <option value="Errea">Errea</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Player Name</label>
                <input
                  type="text"
                  placeholder="e.g., Bruno Fernandes (optional)"
                  value={formData.player}
                  onChange={(e) => setFormData({...formData, player: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Reference Code</label>
                <input
                  type="text"
                  placeholder="e.g., 779963-01"
                  value={formData.reference_code}
                  onChange={(e) => setFormData({...formData, reference_code: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Type*</label>
                <select
                  value={formData.home_away}
                  onChange={(e) => setFormData({...formData, home_away: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="home">Home</option>
                  <option value="away">Away</option>
                  <option value="third">Third Kit</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Size*</label>
                <select
                  value={formData.size}
                  onChange={(e) => setFormData({...formData, size: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="XS">XS</option>
                  <option value="S">S</option>
                  <option value="M">M</option>
                  <option value="L">L</option>
                  <option value="XL">XL</option>
                  <option value="XXL">XXL</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Condition*</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="mint">Mint</option>
                  <option value="excellent">Excellent</option>
                  <option value="very_good">Very Good</option>
                  <option value="good">Good</option>
                  <option value="fair">Fair</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                <textarea
                  placeholder="Add details about the jersey, special features, etc."
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-20"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">Jersey Photos</label>
                <ImageUpload 
                  images={formData.images}
                  setImages={(images) => setFormData({...formData, images})}
                />
                <p className="text-xs text-gray-400 mt-2">
                  Update photos based on moderator feedback if necessary.
                </p>
              </div>
            </div>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 font-semibold"
            >
              {loading ? 'Resubmitting...' : 'Resubmit for Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Listing Modal Component (for creating listings from existing jerseys)
const CreateListingModal = ({ onClose, jerseyId, jersey = null }) => {
  const [formData, setFormData] = useState({
    listing_description: '',
    price: '',
    images: jersey?.images || []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to create a listing');
      }

      if (!jerseyId) {
        throw new Error('No jersey selected for listing');
      }

      // Create the listing with price
      const listingData = {
        jersey_id: jerseyId,
        description: formData.listing_description,
        price: formData.price ? parseFloat(formData.price) : null,
        images: formData.images
      };

      await axios.post(`${API}/api/listings`, listingData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Jersey listed successfully!');
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'Failed to create listing');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Create Listing</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {jersey && (
          <div className="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">Jersey to List</h3>
            <div className="flex items-center space-x-4">
              {jersey.images && jersey.images[0] && (
                <img 
                  src={jersey.images[0]} 
                  alt={`${jersey.team} ${jersey.season}`}
                  className="w-16 h-16 object-cover rounded border border-gray-600"
                />
              )}
              <div>
                <p className="text-white font-medium">{jersey.team} - {jersey.season}</p>
                {jersey.player && <p className="text-gray-300">{jersey.player}</p>}
                <p className="text-gray-400 text-sm">Size: {jersey.size} • Condition: {jersey.condition}</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Price (€)*</label>
            <input
              type="number"
              placeholder="Prix minimum 0.10€"
              value={formData.price}
              onChange={(e) => setFormData({...formData, price: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
              step="0.01"
              min="0.10"
              required
            />
            <p className="text-xs text-gray-400 mt-1">
              Prix minimum : 0.10€
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Description*</label>
            <textarea
              placeholder="Describe the jersey condition, any special features, authenticity, etc."
              value={formData.listing_description}
              onChange={(e) => setFormData({...formData, listing_description: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-32"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Additional Photos</label>
            <ImageUpload 
              images={formData.images}
              setImages={(images) => setFormData({...formData, images})}
            />
            <p className="text-xs text-gray-400 mt-2">
              Add extra photos for your listing. High-quality images help with sales.
            </p>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 font-semibold"
            >
              {loading ? 'Creating Listing...' : 'Create Listing'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Edit Jersey Modal Component
const EditJerseyModal = ({ jersey, onClose, onJerseyUpdated }) => {
  const [formData, setFormData] = useState({
    team: jersey?.team || '',
    season: jersey?.season || '',
    player: jersey?.player || '',
    size: jersey?.size || 'M',
    condition: jersey?.condition || 'excellent',
    manufacturer: jersey?.manufacturer || '',
    home_away: jersey?.home_away || 'home',
    league: jersey?.league || '',
    description: jersey?.description || '',
    images: jersey?.images || [],
    reference_code: jersey?.reference_code || ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to edit jerseys');
      }

      const response = await axios.put(`${API}/api/jerseys/${jersey.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Jersey updated successfully!');
      if (onJerseyUpdated) {
        onJerseyUpdated(response.data);
      }
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'Failed to update jersey');
    } finally {
      setLoading(false);
    }
  };

  if (!jersey) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-4xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Edit Jersey</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Jersey Details */}
          <div className="border border-gray-700 rounded-lg p-6 bg-gray-800">
            <h3 className="text-lg font-semibold mb-4 text-white">Jersey Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Club/National Team*</label>
                <input
                  type="text"
                  placeholder="e.g., Manchester United"
                  value={formData.team}
                  onChange={(e) => setFormData({...formData, team: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Season*</label>
                <input
                  type="text"
                  placeholder="e.g., 2023-24"
                  value={formData.season}
                  onChange={(e) => setFormData({...formData, season: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Brand/Manufacturer*</label>
                <input
                  type="text"
                  placeholder="e.g., Nike, Adidas, Puma"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">League*</label>
                <input
                  type="text"
                  placeholder="e.g., Premier League, La Liga"
                  value={formData.league}
                  onChange={(e) => setFormData({...formData, league: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Player Name</label>
                <input
                  type="text"
                  placeholder="e.g., Bruno Fernandes (optional)"
                  value={formData.player}
                  onChange={(e) => setFormData({...formData, player: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Type*</label>
                <select
                  value={formData.home_away}
                  onChange={(e) => setFormData({...formData, home_away: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="home">Home</option>
                  <option value="away">Away</option>
                  <option value="third">Third Kit</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Size*</label>
                <select
                  value={formData.size}
                  onChange={(e) => setFormData({...formData, size: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="XS">XS</option>
                  <option value="S">S</option>
                  <option value="M">M</option>
                  <option value="L">L</option>
                  <option value="XL">XL</option>
                  <option value="XXL">XXL</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Condition*</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="mint">Mint</option>
                  <option value="excellent">Excellent</option>
                  <option value="very_good">Very Good</option>
                  <option value="good">Good</option>
                  <option value="fair">Fair</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
              <textarea
                placeholder="Describe the jersey condition, any special features, authenticity, etc."
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-24"
              />
            </div>

            {/* Images */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">Jersey Photos</label>
              <ImageUpload 
                images={formData.images}
                setImages={(images) => setFormData({...formData, images})}
              />
              <p className="text-xs text-gray-400 mt-2">
                Upload high-quality photos of your jersey. First image will be the main photo.
              </p>
            </div>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={async () => {
                if (confirm('Êtes-vous sûr de vouloir supprimer cet article de votre collection ?')) {
                  try {
                    setLoading(true);
                    const token = localStorage.getItem('token');
                    await axios.delete(`${API}/api/collections/${jersey.id}`, {
                      headers: { Authorization: `Bearer ${token}` }
                    });
                    alert('Article supprimé de votre collection !');
                    // Dispatch refresh event for collections
                    const refreshEvent = new CustomEvent('refreshCollections');
                    window.dispatchEvent(refreshEvent);
                    onClose();
                  } catch (error) {
                    alert(error.response?.data?.detail || 'Erreur lors de la suppression');
                  } finally {
                    setLoading(false);
                  }
                }
              }}
              disabled={loading}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 font-semibold"
            >
              🗑️ Remove from Collection
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 font-semibold"
            >
              {loading ? 'Updating Jersey...' : 'Update Jersey'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// User Profile Modal Component
const UserProfileModal = ({ userId, onClose }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [userJerseys, setUserJerseys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    if (userId) {
      fetchUserProfile();
      fetchUserJerseys();
    }
  }, [userId]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/api/users/${userId}/profile`);
      setUserProfile(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserJerseys = async () => {
    try {
      const response = await axios.get(`${API}/api/users/${userId}/jerseys`);
      setUserJerseys(response.data);
    } catch (error) {
      console.error('Failed to fetch user jerseys:', error);
      setUserJerseys([]);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
        <div className="bg-gray-900 rounded-xl max-w-4xl w-full border border-gray-800 p-8">
          <div className="text-center py-8 text-gray-400">Loading user profile...</div>
        </div>
      </div>
    );
  }

  if (!userProfile) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
        <div className="bg-gray-900 rounded-xl max-w-md w-full border border-gray-800 p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">User Profile</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">✕</button>
          </div>
          <div className="text-center py-8 text-red-400">User profile not found</div>
        </div>
      </div>
    );
  }

  const isPrivate = userProfile.profile_privacy === 'private';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-4xl w-full max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center p-6 border-b border-gray-800">
          <h2 className="text-2xl font-bold text-white">User Profile</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">✕</button>
        </div>

        <div className="p-6">
          {/* User Profile Header */}
          <div className="flex items-center space-x-6 mb-8">
            {userProfile.picture && (
              <img 
                src={userProfile.picture} 
                alt={userProfile.name}
                className="w-20 h-20 rounded-full border-4 border-gray-700"
              />
            )}
            <div>
              <h1 className="text-3xl font-bold text-white">{userProfile.name}</h1>
              <div className="flex items-center space-x-3 mt-2">
                <span className="inline-block bg-gray-800 text-white text-xs px-2 py-1 rounded-full border border-gray-600">
                  {userProfile.provider} user
                </span>
                <span className={`inline-block text-xs px-2 py-1 rounded-full ${
                  isPrivate 
                    ? 'bg-red-900 text-red-300 border border-red-700' 
                    : 'bg-green-900 text-green-300 border border-green-700'
                }`}>
                  {isPrivate ? 'Private Profile' : 'Public Profile'}
                </span>
              </div>
              {userProfile.created_at && (
                <p className="text-sm text-gray-500 mt-1">
                  Member since {new Date(userProfile.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>

          {isPrivate ? (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🔒</div>
              <h2 className="text-2xl font-bold text-white mb-4">Private Profile</h2>
              <p className="text-gray-400">{userProfile.message}</p>
            </div>
          ) : (
            <>
              {/* Stats Section */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-800 p-4 rounded-lg text-center border border-gray-700">
                  <div className="text-2xl font-bold text-white mb-1">
                    {userProfile.stats?.jerseys_created || 0}
                  </div>
                  <div className="text-gray-300 text-sm">Jerseys Created</div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg text-center border border-gray-700">
                  <div className="text-2xl font-bold text-white mb-1">
                    {userProfile.stats?.owned_jerseys || 0}
                  </div>
                  <div className="text-gray-300 text-sm">Owned</div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg text-center border border-gray-700">
                  <div className="text-2xl font-bold text-white mb-1">
                    {userProfile.stats?.wanted_jerseys || 0}
                  </div>
                  <div className="text-gray-300 text-sm">Wanted</div>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg text-center border border-gray-700">
                  <div className="text-2xl font-bold text-white mb-1">
                    {userProfile.stats?.active_listings || 0}
                  </div>
                  <div className="text-gray-300 text-sm">Active Listings</div>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex space-x-1 bg-gray-800 rounded-lg p-1 border border-gray-700 mb-6">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`px-4 py-2 rounded-lg transition-colors flex-1 ${
                    activeTab === 'profile'
                      ? 'bg-white text-black'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  Profile Info
                </button>
                <button
                  onClick={() => setActiveTab('jerseys')}
                  className={`px-4 py-2 rounded-lg transition-colors flex-1 ${
                    activeTab === 'jerseys'
                      ? 'bg-white text-black'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  Created Jerseys ({userJerseys.length})
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === 'profile' && (
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-lg font-semibold text-white mb-4">Profile Information</h3>
                  <div className="space-y-3 text-gray-300">
                    <div>
                      <span className="text-gray-400">Name:</span>
                      <span className="ml-2 text-white">{userProfile.name}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Account Type:</span>
                      <span className="ml-2 text-white">{userProfile.provider} account</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Profile Visibility:</span>
                      <span className="ml-2 text-white">{userProfile.profile_privacy}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Member Since:</span>
                      <span className="ml-2 text-white">
                        {userProfile.created_at ? new Date(userProfile.created_at).toLocaleDateString() : 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'jerseys' && (
                <div>
                  {userJerseys.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {userJerseys.map((jersey) => (
                        <JerseyCard 
                          key={jersey.id}
                          jersey={jersey}
                          onClick={() => {}}
                          onCreatorClick={onClose} // Close current modal if someone clicks on creator
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-16">
                      <div className="text-6xl mb-4">👕</div>
                      <h3 className="text-xl font-bold text-white mb-4">No jerseys created</h3>
                      <p className="text-gray-400">This user hasn't created any jerseys yet.</p>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const AuthModal = ({ onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: '', password: '', name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      console.log('Attempting authentication:', `${API}${endpoint}`, formData);
      
      const response = await axios.post(`${API}${endpoint}`, formData, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log('Authentication response:', response.data);
      
      if (response.data?.token && response.data?.user) {
        console.log('✅ Authentication successful, calling login...');
        const loginSuccess = login(response.data.token, response.data.user);
        if (loginSuccess) {
          console.log('✅ Login completed successfully, closing modal...');
          onClose();
        } else {
          console.error('❌ Login failed during context update');
          setError('Erreur lors de la mise à jour de la session. Veuillez réessayer.');
        }
      } else {
        console.error('❌ Invalid authentication response:', response.data);
        setError('Authentication response was invalid. Please try again.');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      if (error.code === 'ECONNABORTED') {
        setError('Connexion timeout - Vérifiez votre connexion internet');
      } else if (error.response?.status === 404) {
        setError('Service d\'authentification non disponible');
      } else if (error.response?.status === 500) {
        setError('Erreur serveur - Réessayez plus tard');
      } else {
        setError(error.response?.data?.detail || 'Erreur d\'authentification');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = () => {
    window.location.href = `${API}/api/auth/google`;
  };



  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] pointer-events-none">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 relative z-[10000] pointer-events-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {isLogin ? 'Login' : 'Sign Up'}
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <input
              type="text"
              placeholder="Full Name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 bg-white"
              required={!isLogin}
            />
          )}
          
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 bg-white"
            required
          />
          
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 bg-white"
            required
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : (isLogin ? 'Login' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-6 space-y-3">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <button
            onClick={handleGoogleAuth}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <img 
              src="https://developers.google.com/identity/images/g-logo.png" 
              alt="Google" 
              className="w-5 h-5 mr-3"
            />
            Continue with Google
          </button>

        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-green-600 hover:text-green-700"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

// Profile Settings Modal Component
const ProfileSettingsModal = ({ onClose }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    picture: user?.picture || ''
  });
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be less than 5MB');
      return;
    }

    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      // Convert to base64 for now (in production, you'd upload to cloud storage)
      const reader = new FileReader();
      reader.onload = (e) => {
        setFormData({...formData, picture: e.target.result});
        setUploading(false);
        setSuccess('Profile picture updated!');
      };
      reader.readAsDataURL(file);
    } catch (error) {
      setError('Failed to upload image');
      setUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/api/profile/settings`, {
        name: formData.name,
        picture: formData.picture
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setSuccess('Profile updated successfully!');
      
      // Update user context (would need to be implemented)
      setTimeout(() => {
        window.location.reload(); // Simple refresh for now
      }, 1500);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Profile Settings</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
              {success}
            </div>
          )}

          {/* Profile Picture Section */}
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <Avatar 
                user={{...user, picture: formData.picture}} 
                size="xl" 
                className="shadow-lg"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Profile Picture
              </label>
              <div className="flex justify-center">
                <label className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors cursor-pointer text-sm font-medium">
                  {uploading ? 'Uploading...' : 'Change Photo'}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    disabled={uploading}
                  />
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-1">Max 5MB, JPG/PNG/GIF</p>
            </div>
          </div>

          {/* Name Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Display Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              required
            />
          </div>

          {/* Email Field (Read-only for now) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-500"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
          </div>

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || uploading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 font-medium"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
// Profile Page Component
const ProfilePage = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfileData(response.data);
    } catch (error) {
      console.error('Failed to fetch profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingsUpdate = (newSettings) => {
    setProfileData({
      ...profileData,
      user: {
        ...profileData.user,
        ...newSettings
      }
    });
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading profile...</div>;
  }

  if (!user) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-white mb-4">Please Login</h2>
        <p className="text-gray-400">You need to login to view your profile.</p>
      </div>
    );
  }

  const valuations = profileData?.valuations;
  const portfolio = valuations?.portfolio_summary;

  return (
    <div className="max-w-6xl mx-auto">
      {/* User Profile Section */}
      <div className="bg-gray-900 rounded-xl shadow-2xl p-8 mb-8 border border-gray-800">
        <div className="flex justify-between items-start mb-8">
          <div className="flex items-center space-x-6">
            {user.picture && (
              <img 
                src={user.picture} 
                alt={user.name}
                className="w-20 h-20 rounded-full border-4 border-white"
              />
            )}
            <div>
              <h1 className="text-3xl font-bold text-white">{user.name}</h1>
              <p className="text-gray-400">{user.email}</p>
              <p className="text-sm text-gray-500">
                Member since {new Date(user.created_at).toLocaleDateString()}
              </p>
              <div className="flex items-center space-x-3 mt-2">
                <span className="inline-block bg-gray-800 text-white text-xs px-2 py-1 rounded-full border border-gray-600">
                  {user.provider} user
                </span>
                <span className={`inline-block text-xs px-2 py-1 rounded-full ${
                  profileData?.user?.profile_privacy === 'private' 
                    ? 'bg-red-900 text-red-300 border border-red-700' 
                    : 'bg-green-900 text-green-300 border border-green-700'
                }`}>
                  {profileData?.user?.profile_privacy === 'private' ? 'Private Profile' : 'Public Profile'}
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={() => setShowSettings(true)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors border border-gray-600"
          >
            Settings
          </button>
        </div>

        {/* Collection Stats */}
        {profileData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-800 p-6 rounded-lg text-center border border-gray-700">
              <div className="text-3xl font-bold text-white mb-2">
                {profileData.stats?.owned_jerseys || 0}
              </div>
              <div className="text-gray-300">Owned Jerseys</div>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg text-center border border-gray-700">
              <div className="text-3xl font-bold text-white mb-2">
                {profileData.stats?.wanted_jerseys || 0}
              </div>
              <div className="text-gray-300">Wanted Jerseys</div>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg text-center border border-gray-700">
              <div className="text-3xl font-bold text-white mb-2">
                {profileData.stats?.active_listings || 0}
              </div>
              <div className="text-gray-300">Active Listings</div>
            </div>
          </div>
        )}
      </div>

      {/* Portfolio Valuation Section - Only show if user enabled it */}
      {portfolio && profileData?.user?.show_collection_value && (
        <div className="bg-gray-900 rounded-xl shadow-2xl p-8 mb-8 border border-gray-800">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-3xl mr-3">💰</span>
            Collection Portfolio Valuation
            <span className="text-sm bg-gray-800 text-gray-300 px-3 py-1 rounded-full ml-4 border border-gray-600">
              Private - Only Visible to You
            </span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-gradient-to-br from-green-900 to-green-800 p-6 rounded-xl border border-green-700">
              <div className="text-sm font-medium text-green-300 mb-2">Low Estimate</div>
              <div className="text-2xl font-bold text-green-100">
                ${portfolio.total_low_estimate?.toLocaleString() || '0'}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-6 rounded-xl border border-blue-700">
              <div className="text-sm font-medium text-blue-300 mb-2">Median Estimate</div>
              <div className="text-2xl font-bold text-blue-100">
                ${portfolio.total_median_estimate?.toLocaleString() || '0'}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-6 rounded-xl border border-purple-700">
              <div className="text-sm font-medium text-purple-300 mb-2">High Estimate</div>
              <div className="text-2xl font-bold text-purple-100">
                ${portfolio.total_high_estimate?.toLocaleString() || '0'}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-amber-900 to-amber-800 p-6 rounded-xl border border-amber-700">
              <div className="text-sm font-medium text-amber-300 mb-2">Average Value</div>
              <div className="text-2xl font-bold text-amber-100">
                ${portfolio.average_value?.toLocaleString() || '0'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-400">
            <div>
              <span className="font-medium">Total Items:</span> {portfolio.total_items || 0}
            </div>
            <div>
              <span className="font-medium">Valued Items:</span> {portfolio.valued_items || 0}
            </div>
          </div>

          {portfolio.valued_items < portfolio.total_items && (
            <div className="mt-4 p-4 bg-yellow-900 border border-yellow-700 rounded-lg">
              <div className="flex items-center">
                <span className="text-yellow-300 text-xl mr-2">⚠️</span>
                <div>
                  <div className="font-medium text-yellow-200">Incomplete Valuation Data</div>
                  <div className="text-sm text-yellow-300">
                    {portfolio.total_items - portfolio.valued_items} of your jerseys don't have enough market data for accurate valuation. 
                    As more similar jerseys are listed or sold, valuations will become available.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Individual Jersey Valuations - Only show if user enabled collection values */}
      {valuations?.collections && valuations.collections.length > 0 && profileData?.user?.show_collection_value && (
        <div className="bg-gray-900 rounded-xl shadow-2xl p-8 border border-gray-800">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-3xl mr-3">📊</span>
            Individual Jersey Valuations
            <span className="text-sm bg-gray-800 text-gray-300 px-3 py-1 rounded-full ml-4 border border-gray-600">
              Private
            </span>
          </h2>
          
          <div className="space-y-4">
            {valuations.collections.map((item) => (
              <div key={item.collection_id} className="border border-gray-700 rounded-lg p-6 hover:shadow-lg transition-shadow bg-gray-800">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        {item.jersey.team} {item.jersey.season}
                      </h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.collection_type === 'owned' 
                          ? 'bg-green-900 text-green-300 border border-green-700' 
                          : 'bg-blue-900 text-blue-300 border border-blue-700'
                      }`}>
                        {item.collection_type}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-400 space-y-1">
                      <div>
                        {item.jersey.player && <span className="font-medium text-white">{item.jersey.player}</span>}
                        {item.jersey.player && ' • '}
                        <span>{item.jersey.home_away} • {item.jersey.size} • {item.jersey.condition}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Added: {new Date(item.added_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    {item.valuation ? (
                      <div className="space-y-2">
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div className="text-center">
                            <div className="text-green-300 font-bold">${item.valuation.low_estimate}</div>
                            <div className="text-gray-500 text-xs">Low</div>
                          </div>
                          <div className="text-center">
                            <div className="text-blue-300 font-bold text-lg">${item.valuation.median_estimate}</div>
                            <div className="text-gray-500 text-xs">Median</div>
                          </div>
                          <div className="text-center">
                            <div className="text-purple-300 font-bold">${item.valuation.high_estimate}</div>
                            <div className="text-gray-500 text-xs">High</div>
                          </div>
                        </div>
                        
                        <div className="text-xs text-gray-500">
                          Based on {item.valuation.total_sales} sales • {item.valuation.total_listings} listings
                        </div>
                        
                        {item.valuation.market_data?.confidence_score && (
                          <div className="text-xs">
                            <span className={`px-2 py-1 rounded ${
                              item.valuation.market_data.confidence_score >= 70 
                                ? 'bg-green-900 text-green-300 border border-green-700'
                                : item.valuation.market_data.confidence_score >= 40
                                ? 'bg-yellow-900 text-yellow-300 border border-yellow-700'
                                : 'bg-red-900 text-red-300 border border-red-700'
                            }`}>
                              {item.valuation.market_data.confidence_score}% confidence
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-gray-500 text-sm">
                        <div>No valuation data</div>
                        <div className="text-xs">Need more market data</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <ProfileSettingsModal
          onClose={() => setShowSettings(false)}
          onUpdate={handleSettingsUpdate}
        />
      )}
    </div>
  );
};

// Jersey Suggestions View Modal Component
const JerseySuggestionsModal = ({ jersey, onClose, onResubmit }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSuggestions();
  }, [jersey?.id]);

  const fetchSuggestions = async () => {
    if (!jersey?.id) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/jerseys/${jersey.id}/suggestions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!jersey) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-4xl w-full max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center p-6 border-b border-gray-800">
          <h2 className="text-2xl font-bold text-white">Moderator Feedback</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        <div className="p-6">
          {/* Jersey Info */}
          <div className="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">Jersey: {jersey.team} {jersey.season}</h3>
            <div className="flex items-center space-x-4">
              {jersey.images && jersey.images[0] && (
                <img 
                  src={jersey.images[0]} 
                  alt={`${jersey.team} ${jersey.season}`}
                  className="w-16 h-16 object-cover rounded border border-gray-600"
                />
              )}
              <div>
                {jersey.player && <p className="text-gray-300">{jersey.player}</p>}
                <p className="text-gray-400 text-sm">
                  Size: {jersey.size} • Condition: {jersey.condition} • Status: <span className="capitalize font-medium">{jersey.status}</span>
                </p>
              </div>
            </div>
          </div>

          {/* Suggestions */}
          {loading ? (
            <div className="text-center py-8 text-gray-400">
              <LoadingSpinner size="md" className="mx-auto mb-2" />
              Loading feedback...
            </div>
          ) : suggestions.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No moderator feedback available.
            </div>
          ) : (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white">Moderator Feedback:</h3>
              {suggestions.map((suggestion, index) => (
                <div key={suggestion.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-lg font-semibold text-white">
                        Feedback #{index + 1}
                      </h4>
                      <p className="text-gray-400 text-sm">
                        From: {suggestion.moderator_info?.name || 'Moderator'} • {new Date(suggestion.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      suggestion.status === 'pending' ? 'bg-yellow-900 text-yellow-300' :
                      suggestion.status === 'addressed' ? 'bg-green-900 text-green-300' :
                      'bg-gray-900 text-gray-300'
                    }`}>
                      {suggestion.status}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <h5 className="text-white font-medium mb-2">Suggested Changes:</h5>
                      <p className="text-gray-300 bg-gray-900 p-3 rounded border border-gray-600 leading-relaxed">
                        {suggestion.suggested_changes}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          {jersey.status === 'needs_modification' && (
            <div className="mt-8 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
              <div className="flex items-start">
                <div className="text-blue-400 text-xl mr-3 mt-1">💡</div>
                <div className="flex-1">
                  <h3 className="text-blue-300 font-semibold mb-2">Ready to Address Feedback?</h3>
                  <p className="text-blue-200 text-sm leading-relaxed mb-4">
                    You can resubmit this jersey with the suggested modifications. The original submission will be marked as superseded, and your new submission will go through the review process again.
                  </p>
                  <button
                    onClick={() => onResubmit && onResubmit()}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors font-medium"
                  >
                    Resubmit with Modifications
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end mt-6">
            <button
              onClick={onClose}
              className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Collections Page Component
const CollectionsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('owned');
  const [collections, setCollections] = useState([]);
  const [pendingSubmissions, setPendingSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSubmitJerseyModal, setShowSubmitJerseyModal] = useState(false);
  const [showSuggestionsModal, setShowSuggestionsModal] = useState(false);
  const [selectedJerseyForSuggestions, setSelectedJerseyForSuggestions] = useState(null);
  const [showResubmissionModal, setShowResubmissionModal] = useState(false);
  const [jerseyToResubmit, setJerseyToResubmit] = useState(null);

  useEffect(() => {
    if (user) {
      fetchCollections();
    }

    // Listen for refresh events
    const handleRefreshCollections = () => {
      if (user) {
        fetchCollections();
      }
    };

    window.addEventListener('refreshCollections', handleRefreshCollections);

    return () => {
      window.removeEventListener('refreshCollections', handleRefreshCollections);
    };
  }, [user, activeTab]);

  const fetchCollections = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      if (activeTab === 'pending') {
        // Fetch pending submissions for submit jersey tab
        const response = await axios.get(`${API}/api/collections/pending`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setPendingSubmissions(response.data);
        setCollections([]); // Clear regular collections
      } else if (activeTab === 'submit') {
        // Fetch all submissions (pending, approved, rejected) for submit jersey history
        const pendingResponse = await axios.get(`${API}/api/collections/pending`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        // For now, we'll show pending submissions. Later we can add an endpoint for all user submissions
        setPendingSubmissions(pendingResponse.data);
        setCollections([]); // Clear regular collections
      } else {
        // Fetch regular collections (owned/wanted)
        const response = await axios.get(`${API}/api/collections/${activeTab}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCollections(response.data);
        setPendingSubmissions([]); // Clear pending submissions
      }
    } catch (error) {
      console.error('Failed to fetch collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFromCollection = async (jerseyId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.delete(`${API}/api/collections/${jerseyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.status === 200) {
        // Show success message
        window.alert('Article retiré de votre collection avec succès !');
        // Refresh collections
        fetchCollections();
      }
    } catch (error) {
      console.error('Failed to remove from collection:', error);
      window.alert('Erreur lors du retrait de l\'article de votre collection.');
    }
  };

  const handleViewSuggestions = (jersey) => {
    setSelectedJerseyForSuggestions(jersey);
    setShowSuggestionsModal(true);
  };

  const handleResubmitJersey = (jersey) => {
    setJerseyToResubmit(jersey);
    setShowSuggestionsModal(false);
    setShowResubmissionModal(true);
  };

  const handleResubmissionSuccess = () => {
    setShowResubmissionModal(false);
    setJerseyToResubmit(null);
    fetchCollections(); // Refresh to show updated status
  };

  const handleSellJersey = (jersey) => {
    // This will trigger the main app's listing creation modal with the jersey data
    window.parent?.postMessage({ 
      type: 'SELL_JERSEY', 
      jersey: jersey 
    }, '*');
    
    // Alternative: Use a custom event
    const event = new CustomEvent('sellJersey', { detail: jersey });
    window.dispatchEvent(event);
  };

  const handleEditJersey = (jersey) => {
    // This will trigger the main app's edit jersey modal with the jersey data
    const event = new CustomEvent('editJersey', { detail: jersey });
    window.dispatchEvent(event);
  };

  const handleCreatorClick = (userId) => {
    // This will trigger the main app's user profile modal with the user ID
    const event = new CustomEvent('showUserProfile', { detail: userId });
    window.dispatchEvent(event);
  };

  const handleSubmitNewJersey = () => {
    // Open submit jersey modal instead of navigating
    setShowSubmitJerseyModal(true);
  };

  const handleJerseyClick = (jersey) => {
    // Jersey detail functionality can be added here
    console.log('Jersey clicked:', jersey);
  };

  if (!user) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-white mb-4">Please Login</h2>
        <p className="text-gray-400">You need to login to view your collections.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">My Collections</h1>
        <div className="flex space-x-1 bg-gray-800 rounded-lg p-1 border border-gray-700">
          <button
            onClick={() => setActiveTab('owned')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'owned'
                ? 'bg-white text-black'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            👕 Owned
          </button>
          <button
            onClick={() => setActiveTab('wanted')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'wanted'
                ? 'bg-white text-black'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            ❤️ Wanted
          </button>
          <button
            onClick={() => setActiveTab('submit')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'submit'
                ? 'bg-green-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            📝 Submit Jersey
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-400">Loading collections...</div>
      ) : activeTab === 'submit' ? (
        <div className="space-y-8">
          {/* Submit New Jersey Section */}
          <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-2xl p-8 border border-green-700">
            <div className="text-center">
              <div className="text-6xl mb-4">📝</div>
              <h2 className="text-2xl font-bold text-white mb-4">Soumettre un nouveau maillot</h2>
              <p className="text-green-200 mb-8">
                Proposez de nouveaux maillots à la base de données. Ils seront examinés par nos modérateurs avant d'être publiés.
              </p>
              <button
                onClick={handleSubmitNewJersey}
                className="bg-white text-green-900 px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold text-lg"
              >
                📝 Soumettre un nouveau maillot
              </button>
            </div>
          </div>

          {/* Submissions History Section */}
          <div>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              📚 Historique de mes propositions
              <span className="ml-2 text-sm text-gray-400 font-normal">
                ({pendingSubmissions.length} propositions)
              </span>
            </h3>
            
            {pendingSubmissions.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-2xl border border-gray-700">
                <div className="text-4xl mb-4">📋</div>
                <h4 className="text-lg font-bold text-white mb-2">Aucune proposition pour le moment</h4>
                <p className="text-gray-400">Vos propositions de maillots apparaîtront ici avec leur statut de validation.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pendingSubmissions.map((submission) => (
                  <div key={submission.id} className="relative">
                    <div className={`opacity-70 ${
                      submission.status === 'approved' ? 'border-2 border-green-500' : 
                      submission.status === 'rejected' ? 'border-2 border-red-500' : 
                      'border-2 border-yellow-500'
                    }`}>
                      <JerseyCard
                        jersey={submission}
                        showActions={false}
                        onClick={() => {}}
                      />
                    </div>
                    <div className="absolute inset-0 bg-black bg-opacity-50 rounded-2xl flex items-center justify-center">
                      <div className="text-center text-white">
                        <div className="text-3xl mb-2">
                          {submission.status === 'pending' ? '⏳' : 
                           submission.status === 'approved' ? '✅' : 
                           submission.status === 'rejected' ? '❌' : '❓'}
                        </div>
                        <div className="font-bold text-lg mb-1">
                          {submission.status === 'pending' ? 'En attente de validation' : 
                           submission.status === 'approved' ? 'Validé' : 
                           submission.status === 'rejected' ? 'Rejeté' : 'Statut inconnu'}
                        </div>
                        <div className="text-sm opacity-75">
                          {submission.status === 'pending' 
                            ? 'En cours d\'examen par les modérateurs' 
                            : submission.status === 'approved'
                            ? 'Maillot publié dans la base de données'
                            : submission.rejection_reason || 'Voir les commentaires des modérateurs'
                          }
                        </div>
                        <div className="text-xs mt-2 opacity-60">
                          Soumis le {new Date(submission.created_at).toLocaleDateString('fr-FR')}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : activeTab === 'pending' ? (
        pendingSubmissions.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">⏳</div>
            <h2 className="text-2xl font-bold text-white mb-4">No pending submissions</h2>
            <p className="text-gray-400 mb-8">Your jersey submissions will appear here while they are being reviewed.</p>
            <button
              onClick={() => setActiveTab('submit')}
              className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
            >
              Submit a Jersey
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pendingSubmissions.map((submission) => (
              <div key={submission.id} className="relative">
                <div className={`opacity-60 ${
                  submission.status === 'rejected' ? 'border-2 border-red-500' : 
                  submission.status === 'needs_modification' ? 'border-2 border-yellow-500' : 
                  'border-2 border-blue-500'
                }`}>
                  <JerseyCard
                    jersey={submission}
                    showActions={false}
                    onClick={() => {}}
                  />
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-50 rounded-2xl flex items-center justify-center">
                  <div className="text-center text-white">
                    <div className="text-3xl mb-2">
                      {submission.status === 'pending' ? '⏳' : 
                       submission.status === 'needs_modification' ? '🔧' : 
                       '❌'}
                    </div>
                    <div className="font-bold text-lg mb-1">
                      {submission.status === 'pending' ? 'Under Review' : 
                       submission.status === 'needs_modification' ? 'Needs Modification' :
                       'Rejected'}
                    </div>
                    <div className="text-sm opacity-75 mb-3">
                      {submission.status === 'pending' 
                        ? 'Waiting for admin approval' 
                        : submission.status === 'needs_modification'
                        ? 'Moderator has suggested changes'
                        : submission.rejection_reason || 'See admin feedback'
                      }
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="space-y-2">
                      {submission.status === 'needs_modification' && (
                        <>
                          <button
                            onClick={() => handleViewSuggestions(submission)}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors w-full"
                          >
                            View Feedback
                          </button>
                          <button
                            onClick={() => handleResubmitJersey(submission)}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors w-full"
                          >
                            Resubmit
                          </button>
                        </>
                      )}
                      
                      {submission.status === 'rejected' && (
                        <button
                          onClick={() => handleViewSuggestions(submission)}
                          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                        >
                          View Details
                        </button>
                      )}
                    </div>
                    
                    <div className="text-xs mt-2 opacity-60">
                      Submitted {new Date(submission.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      ) : collections.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-6xl mb-4">{activeTab === 'owned' ? '👕' : '❤️'}</div>
          <h2 className="text-2xl font-bold text-white mb-4">
            No {activeTab} jerseys yet
          </h2>
          <p className="text-gray-400 mb-8">
            Start building your collection by browsing jerseys and adding them to your {activeTab} list.
          </p>
          <button 
            onClick={() => {
              const event = new CustomEvent('navigateToJerseys');
              window.dispatchEvent(event);
            }}
            className="bg-white text-black px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
          >
            Browse Jerseys
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {collections.map((collection) => (
            <JerseyCard 
              key={collection.id} 
              jersey={collection.jersey}
              showActions={true}
              showCollectionDate={true}
              addedAt={collection.added_at}
              showRemove={true}
              onRemoveFromCollection={handleRemoveFromCollection}
              showSellButton={activeTab === 'owned'} // Only show sell button for owned jerseys
              onSellJersey={handleSellJersey}
              showEditButton={activeTab === 'owned'} // Only show edit button for owned jerseys
              onEditJersey={handleEditJersey}
              onClick={handleJerseyClick}
              onCreatorClick={handleCreatorClick}
            />
          ))}
        </div>
      )}
      
      {/* Submit Jersey Modal */}
      {showSubmitJerseyModal && (
        <SubmitJerseyModal 
          onClose={() => setShowSubmitJerseyModal(false)}
          onSuccess={() => {
            setShowSubmitJerseyModal(false);
            // Refresh submissions after successful submission
            fetchCollections();
          }}
        />
      )}
      
      {/* Jersey Suggestions Modal */}
      {showSuggestionsModal && selectedJerseyForSuggestions && (
        <JerseySuggestionsModal
          jersey={selectedJerseyForSuggestions}
          onClose={() => {
            setShowSuggestionsModal(false);
            setSelectedJerseyForSuggestions(null);
          }}
          onResubmit={() => handleResubmitJersey(selectedJerseyForSuggestions)}
        />
      )}
      
      {/* Resubmission Modal */}
      {showResubmissionModal && jerseyToResubmit && (
        <ResubmissionModal
          originalJersey={jerseyToResubmit}
          onClose={() => {
            setShowResubmissionModal(false);
            setJerseyToResubmit(null);
          }}
          onSuccess={handleResubmissionSuccess}
        />
      )}
    </div>
  );
};

// Jersey Card Component (updated)
const JerseyCard = ({ jersey, showActions = false, onAddToCollection, showCollectionDate = false, addedAt, onRemoveFromCollection, showRemove = false, showSellButton = false, onSellJersey, showEditButton = false, onEditJersey, onClick, onCreatorClick }) => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl overflow-hidden hover:shadow-3xl transition-all duration-300 border border-gray-700 hover:border-gray-600 cursor-pointer group transform hover:scale-105"
      onClick={() => onClick && onClick(jersey)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Image Container with Overlay */}
      <div className="relative overflow-hidden">
        <img
          src={jersey.images?.[0] || 'https://via.placeholder.com/300x400?text=Jersey+Image'}
          alt={`${jersey.team} ${jersey.season}`}
          className={`w-full h-48 object-cover transition-transform duration-300 ${isHovered ? 'scale-110' : ''}`}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Floating badges */}
        <div className="absolute top-3 left-3 space-y-2">
          {jersey.home_away && (
            <span className="bg-black/70 backdrop-blur-sm text-white px-2 py-1 rounded-full text-xs font-medium">
              {jersey.home_away}
            </span>
          )}
        </div>
      </div>

      <div className="p-5">
        {/* Header */}
        <div className="mb-4">
          <div className="flex justify-between items-start mb-1">
            <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">
              {jersey.team}
            </h3>
            {jersey.reference_number && (
              <span className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded-md text-xs font-mono border border-blue-500/30">
                {jersey.reference_number}
              </span>
            )}
          </div>
          <p className="text-gray-400 text-sm font-medium">{jersey.season}</p>
          {jersey.player && (
            <p className="text-blue-300 font-medium text-sm mt-1">#{jersey.player}</p>
          )}
        </div>
        
        {/* Creator information with Avatar */}
        {jersey.creator_info && (
          <div className="mb-4" onClick={(e) => e.stopPropagation()}>
            <p className="text-xs text-gray-500 mb-1">Added by</p>
            <div className="flex items-center space-x-2">
              <Avatar 
                user={jersey.creator_info} 
                size="xs" 
                className="border-gray-600"
              />
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  onCreatorClick && onCreatorClick(jersey.creator_info.id); 
                }}
                className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors hover:underline"
              >
                {jersey.creator_info.name}
              </button>
            </div>
          </div>
        )}
        
        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
            {jersey.size}
          </span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold shadow-lg ${
            jersey.condition === 'mint' ? 'bg-gradient-to-r from-green-600 to-green-700 text-white' :
            jersey.condition === 'excellent' ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 text-white' :
            jersey.condition === 'very_good' ? 'bg-gradient-to-r from-yellow-600 to-yellow-700 text-white' :
            jersey.condition === 'good' ? 'bg-gradient-to-r from-orange-600 to-orange-700 text-white' :
            'bg-gradient-to-r from-red-600 to-red-700 text-white'
          }`}>
            {jersey.condition.replace('_', ' ')}
          </span>
          {jersey.manufacturer && (
            <span className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
              {jersey.manufacturer}
            </span>
          )}
        </div>
        
        {/* Description */}
        {jersey.description && (
          <p className="text-sm text-gray-300 mb-4 line-clamp-2 leading-relaxed">{jersey.description}</p>
        )}
        
        {showCollectionDate && (
          <p className="text-xs text-gray-500 mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Added {new Date(addedAt).toLocaleDateString()}
          </p>
        )}
        
        {showActions && (
          <div className="space-y-2" onClick={(e) => e.stopPropagation()}>
            {showSellButton && (
              <Button
                onClick={(e) => { e.stopPropagation(); onSellJersey && onSellJersey(jersey); }}
                variant="success"
                size="sm"
                className="w-full"
              >
                💰 Sell This Jersey
              </Button>
            )}
            {showEditButton && (
              <Button
                onClick={(e) => { e.stopPropagation(); onEditJersey && onEditJersey(jersey); }}
                variant="secondary"
                size="sm"
                className="w-full"
              >
                ✏️ Edit Jersey
              </Button>
            )}
            {showRemove && onRemoveFromCollection && (
              <Button
                onClick={(e) => { e.stopPropagation(); onRemoveFromCollection(jersey.id); }}
                variant="danger"
                size="sm"
                className="w-full"
              >
                🗑️ Retirer de la collection
              </Button>
            )}
          </div>
        )}
        
        {onAddToCollection && (
          <div className="flex space-x-2 mt-4" onClick={(e) => e.stopPropagation()}>
            <Button
              onClick={(e) => { e.stopPropagation(); onAddToCollection(jersey.id, 'owned'); }}
              variant="primary"
              size="sm"
              className="flex-1"
            >
              ❤️ Own
            </Button>
            <Button
              onClick={(e) => { e.stopPropagation(); onAddToCollection(jersey.id, 'wanted'); }}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              ⭐ Want
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

// Listing Card Component
const ListingCard = ({ listing, onClick }) => {
  return (
    <div className="bg-gray-900 rounded-xl shadow-2xl overflow-hidden hover:shadow-3xl transition-all border border-gray-800 hover:border-gray-700 cursor-pointer"
         onClick={() => onClick && onClick(listing.jersey, listing)}>
      <img
        src={listing.images?.[0] || listing.jersey?.images?.[0] || 'https://via.placeholder.com/300x400?text=Jersey+Image'}
        alt={`${listing.jersey?.team} ${listing.jersey?.season}`}
        className="w-full h-48 object-cover"
      />
      <div className="p-6">
        <h3 className="text-xl font-semibold text-white mb-2">{listing.jersey?.team}</h3>
        <p className="text-gray-400 mb-1">{listing.jersey?.season} • {listing.jersey?.home_away}</p>
        {listing.jersey?.player && <p className="text-white font-medium mb-3">{listing.jersey?.player}</p>}
        
        <div className="mt-4 flex justify-between items-center mb-3">
          <div className="text-sm text-gray-400">
            <span className="bg-gray-800 text-white px-3 py-1 rounded-full border border-gray-700">{listing.jersey?.size}</span>
            <span className="bg-gray-800 text-white px-3 py-1 rounded-full ml-2 border border-gray-700">
              {listing.jersey?.condition}
            </span>
          </div>
          <div className="text-3xl font-bold text-white">${listing.price}</div>
        </div>
        
        <p className="text-sm text-gray-300 mt-3 mb-6 line-clamp-2">{listing.description}</p>
        
        <button 
          onClick={(e) => { e.stopPropagation(); onClick && onClick(listing.jersey, listing); }}
          className="w-full bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
        >
          View Details
        </button>
      </div>
    </div>
  );
};

// Search and Filter Component
const SearchFilter = ({ onFilter }) => {
  const [filters, setFilters] = useState({
    team: '',
    season: '',
    player: '',
    size: '',
    condition: '',
    league: '',
    minPrice: '',
    maxPrice: ''
  });

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilter(newFilters);
  };

  return (
    <div className="bg-gray-900 rounded-xl shadow-2xl p-6 mb-8 border border-gray-800">
      <h3 className="text-xl font-semibold mb-6 text-white">Search & Filter</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <input
          type="text"
          placeholder="Team"
          value={filters.team}
          onChange={(e) => handleFilterChange('team', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
        />
        <input
          type="text"
          placeholder="Season (e.g., 2023-24)"
          value={filters.season}
          onChange={(e) => handleFilterChange('season', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
        />
        <input
          type="text"
          placeholder="Player"
          value={filters.player}
          onChange={(e) => handleFilterChange('player', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
        />
        <select
          value={filters.size}
          onChange={(e) => handleFilterChange('size', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white"
        >
          <option value="" className="bg-gray-800">Any Size</option>
          <option value="XS" className="bg-gray-800">XS</option>
          <option value="S" className="bg-gray-800">S</option>
          <option value="M" className="bg-gray-800">M</option>
          <option value="L" className="bg-gray-800">L</option>
          <option value="XL" className="bg-gray-800">XL</option>
          <option value="XXL" className="bg-gray-800">XXL</option>
        </select>
        <select
          value={filters.condition}
          onChange={(e) => handleFilterChange('condition', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white"
        >
          <option value="" className="bg-gray-800">Any Condition</option>
          <option value="mint" className="bg-gray-800">Mint</option>
          <option value="excellent" className="bg-gray-800">Excellent</option>
          <option value="very_good" className="bg-gray-800">Very Good</option>
          <option value="good" className="bg-gray-800">Good</option>
          <option value="fair" className="bg-gray-800">Fair</option>
        </select>
        <input
          type="text"
          placeholder="League"
          value={filters.league}
          onChange={(e) => handleFilterChange('league', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
        />
        <input
          type="number"
          placeholder="Min Price"
          value={filters.minPrice}
          onChange={(e) => handleFilterChange('minPrice', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
        />
        <input
          type="number"
          placeholder="Max Price"
          value={filters.maxPrice}
          onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
        />
      </div>
    </div>
  );
};

// Main App Component
const AppContent = () => {
  const { user } = useAuth();
  const [currentView, setCurrentView] = useState('home');
  const [jerseys, setJerseys] = useState([]);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateListing, setShowCreateListing] = useState(false);
  const [showAddJersey, setShowAddJersey] = useState(false); // For adding new jerseys
  const [selectedListingJersey, setSelectedListingJersey] = useState(null); // For selling from collection
  const [selectedJerseyForListing, setSelectedJerseyForListing] = useState(null);
  const [showJerseyDetail, setShowJerseyDetail] = useState(false);
  const [selectedJerseyDetail, setSelectedJerseyDetail] = useState(null);
  const [selectedListingDetail, setSelectedListingDetail] = useState(null);
  const [showEditJersey, setShowEditJersey] = useState(false);
  const [selectedEditJersey, setSelectedEditJersey] = useState(null);
  const [showUserProfile, setShowUserProfile] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [showAuthModalFromAction, setShowAuthModalFromAction] = useState(false);

  // Debug user state changes  
  useEffect(() => {
    console.log('🔄 AppContent - user state changed:', user);
    console.log('🔄 AppContent - user is:', user ? 'LOGGED IN' : 'NOT LOGGED IN');
    console.log('🔄 AppContent - token in localStorage:', localStorage.getItem('token') ? 'EXISTS' : 'MISSING');
  }, [user]);

  // Utility function to check authentication and redirect if needed
  const requireAuth = (action, actionName = 'perform this action') => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert(`Please login to ${actionName}`);
      setShowAuthModalFromAction(true);
      return false;
    }
    return true;
  };

  const fetchJerseys = async (filters = {}) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const url = `${API}/api/jerseys?${params.toString()}`;
      const response = await axios.get(url);
      setJerseys(response.data);
    } catch (error) {
      console.error('❌ Failed to fetch jerseys:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchListings = async (filters = {}) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/api/listings?${params.toString()}`);
      setListings(response.data);
    } catch (error) {
      console.error('Failed to fetch listings:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add event listener for sell jersey functionality
  useEffect(() => {
    const handleSellJersey = (event) => {
      setSelectedListingJersey(event.detail);
      setShowCreateListing(true);
    };

    const handleAddNewJersey = () => {
      setShowAddJersey(true); // Use the new AddJerseyModal for adding jerseys to collection
    };

    const handleEditJersey = (event) => {
      setSelectedEditJersey(event.detail);
      setShowEditJersey(true);
    };

    const handleShowUserProfile = (event) => {
      setSelectedUserId(event.detail);
      setShowUserProfile(true);
    };

    const handleRemoveFromCollectionEvent = (event) => {
      handleRemoveFromCollection(event.detail);
    };

    const handleNavigateToJerseys = () => {
      setCurrentView('jerseys');
    };

    window.addEventListener('sellJersey', handleSellJersey);
    window.addEventListener('addNewJersey', handleAddNewJersey);
    window.addEventListener('editJersey', handleEditJersey);
    window.addEventListener('showUserProfile', handleShowUserProfile);
    window.addEventListener('removeFromCollection', handleRemoveFromCollectionEvent);
    window.addEventListener('navigateToJerseys', handleNavigateToJerseys);
    
    return () => {
      window.removeEventListener('sellJersey', handleSellJersey);
      window.removeEventListener('addNewJersey', handleAddNewJersey);
      window.removeEventListener('editJersey', handleEditJersey);
      window.removeEventListener('showUserProfile', handleShowUserProfile);
      window.removeEventListener('removeFromCollection', handleRemoveFromCollectionEvent);
      window.removeEventListener('navigateToJerseys', handleNavigateToJerseys);
    };
  }, []);

  const handleAddToCollection = async (jerseyId, collectionType) => {
    if (!requireAuth(() => {}, `add jerseys to your ${collectionType} collection`)) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      await axios.post(`${API}/api/collections`, 
        { jersey_id: jerseyId, collection_type: collectionType },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`Added to ${collectionType} collection!`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to add to collection');
    }
  };

  const handleRemoveFromCollection = async (jerseyId) => {
    if (!requireAuth(() => {}, 'manage your collection')) {
      return;
    }

    if (!confirm('Êtes-vous sûr de vouloir supprimer cet article de votre collection ?')) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      await axios.delete(`${API}/api/collections/${jerseyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Article supprimé de votre collection !');
      // Refresh collections if we're on that page
      if (currentView === 'collections') {
        // Force refresh the collections data by dispatching an event
        const refreshEvent = new CustomEvent('refreshCollections');
        window.dispatchEvent(refreshEvent);
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const handleJerseyUpdated = (updatedJersey) => {
    // Refresh the current view data if needed
    if (currentView === 'collections') {
      // This will trigger a re-render of the collections page
      window.location.reload();
    } else if (currentView === 'jerseys') {
      fetchJerseys();
    }
  };

  const handleCreateListing = (jerseyId = null, jersey = null) => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please login to create a listing');
      return;
    }
    
    setSelectedJerseyForListing(jersey);
    setShowCreateListing(true);
  };

  const handleCloseCreateListing = () => {
    setShowCreateListing(false);
    setSelectedJerseyForListing(null);
    // Refresh listings if we're on marketplace
    if (currentView === 'marketplace') {
      fetchListings();
    }
  };

  const handleJerseyClick = (jersey, listing = null) => {
    setSelectedJerseyDetail(jersey);
    setSelectedListingDetail(listing);
    setShowJerseyDetail(true);
  };

  const handleCloseJerseyDetail = () => {
    setShowJerseyDetail(false);
    setSelectedJerseyDetail(null);
    setSelectedListingDetail(null);
  };

  const handleCreatorClick = (userId) => {
    if (userId) {
      setSelectedUserId(userId);
      setShowUserProfile(true);
    }
  };

  const handleCloseUserProfile = () => {
    setShowUserProfile(false);
    setSelectedUserId(null);
  };

  useEffect(() => {
    if (currentView === 'jerseys') {
      fetchJerseys();
    } else if (currentView === 'marketplace') {
      fetchListings();
    }
  }, [currentView]);

  // Event listeners for custom events from subcomponents
  useEffect(() => {
    const handleShowAuthModal = () => setShowAuthModalFromAction(true);
    const handleChangeView = (e) => setCurrentView(e.detail);
    
    window.addEventListener('showAuthModal', handleShowAuthModal);
    window.addEventListener('changeView', handleChangeView);
    
    return () => {
      window.removeEventListener('showAuthModal', handleShowAuthModal);
      window.removeEventListener('changeView', handleChangeView);
    };
  }, []);

  const renderContent = () => {
    switch (currentView) {
      case 'profile':
        return <ProfilePage />;
      
      case 'collections':
        return <CollectionsPage />;
      
      case 'submit':
        return <SubmitJerseyPage />;
      
      case 'admin':
        return <AdminPanel />;
      
      case 'jerseys':
        return (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-4xl font-bold text-white">Browse Jerseys</h1>
            </div>
            <SearchFilter onFilter={fetchJerseys} />
            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg">Loading jerseys...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {jerseys.map((jersey) => (
                  <JerseyCard 
                    key={jersey.id} 
                    jersey={jersey} 
                    showActions={true}
                    onAddToCollection={handleAddToCollection}
                    onClick={handleJerseyClick}
                    onCreatorClick={handleCreatorClick}
                  />
                ))}
              </div>
            )}
          </div>
        );
      
      case 'marketplace':
        return (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-4xl font-bold text-white">Marketplace</h1>
            </div>
            <SearchFilter onFilter={fetchListings} />
            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg">Loading listings...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {listings.map((listing) => (
                  <ListingCard 
                    key={listing.id} 
                    listing={listing}
                    onClick={handleJerseyClick}
                  />
                ))}
              </div>
            )}
          </div>
        );
      
      default:
        return (
          <div className="text-center py-24">
            <h2 className="text-5xl font-bold text-white mb-4">Welcome to TopKit</h2>
            <p className="text-xl text-gray-300 mb-12">The ultimate soccer jersey marketplace</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              <div className="bg-gray-900 p-8 rounded-xl shadow-2xl border border-gray-800 hover:border-gray-700 transition-all hover:shadow-3xl">
                <div className="text-white text-5xl mb-6">🏆</div>
                <h3 className="text-2xl font-semibold mb-4 text-white">Discover Jerseys</h3>
                <p className="text-gray-400 mb-6 leading-relaxed">Browse thousands of soccer jerseys from teams around the world</p>
                <button 
                  onClick={() => setCurrentView('jerseys')}
                  className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
                >
                  Browse Now
                </button>
              </div>
              <div className="bg-gray-900 p-8 rounded-xl shadow-2xl border border-gray-800 hover:border-gray-700 transition-all hover:shadow-3xl">
                <div className="text-white text-5xl mb-6">🛒</div>
                <h3 className="text-2xl font-semibold mb-4 text-white">Buy & Sell</h3>
                <p className="text-gray-400 mb-6 leading-relaxed">Trade jerseys with collectors worldwide in our secure marketplace</p>
                <button 
                  onClick={() => setCurrentView('marketplace')}
                  className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
                >
                  Shop Now
                </button>
              </div>
              <div className="bg-gray-900 p-8 rounded-xl shadow-2xl border border-gray-800 hover:border-gray-700 transition-all hover:shadow-3xl">
                <div className="text-white text-5xl mb-6">📚</div>
                <h3 className="text-2xl font-semibold mb-4 text-white">Manage Collection</h3>
                <p className="text-gray-400 mb-6 leading-relaxed">Keep track of your owned jerseys and create wishlists</p>
                <button 
                  onClick={() => setCurrentView('collections')}
                  className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
                >
                  Get Started
                </button>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <>
      <div className="min-h-screen bg-black text-white">
        <Header currentView={currentView} setCurrentView={setCurrentView} />
        
        {/* Main Content */}
        <main className="container mx-auto px-6 py-8">
          {renderContent()}
        </main>

        {/* Modals */}
        {showCreateListing && (
          <CreateListingModal 
            onClose={() => {
              setShowCreateListing(false);
              setSelectedListingJersey(null);
            }}
            jerseyId={selectedListingJersey?.id}
            jersey={selectedListingJersey}
          />
        )}

        {showAddJersey && (
          <AddJerseyModal 
            onClose={() => setShowAddJersey(false)}
          />
        )}

        {showEditJersey && selectedEditJersey && (
          <EditJerseyModal 
            jersey={selectedEditJersey}
            onClose={() => {
              setShowEditJersey(false);
              setSelectedEditJersey(null);
            }}
            onJerseyUpdated={handleJerseyUpdated}
          />
        )}

        {showJerseyDetail && selectedJerseyDetail && (
          <JerseyDetailModal
            jersey={selectedJerseyDetail}
            listing={selectedListingDetail}
            onClose={handleCloseJerseyDetail}
          />
        )}

        {showUserProfile && selectedUserId && (
          <UserProfileModal
            userId={selectedUserId}
            onClose={handleCloseUserProfile}
          />
        )}

        {showAuthModalFromAction && (
          <AuthModal 
            onClose={() => setShowAuthModalFromAction(false)} 
          />
        )}

        {/* Footer */}
        <footer className="bg-black border-t border-gray-800 text-white py-12 mt-16">
          <div className="container mx-auto px-6">
            <div className="text-center">
              <img 
                src="https://customer-assets.emergentagent.com/job_football-threads-5/artifacts/d38ypztj_ho7nwfgn_topkit_logo_nobc_wh.png"
                alt="TopKit"
                className="h-8 w-auto mx-auto mb-4 opacity-60"
              />
              <p className="text-gray-400 mb-6">The world's premier soccer jersey marketplace</p>
              <div className="flex justify-center space-x-8">
                <a href="#" className="text-gray-500 hover:text-white transition-colors">About</a>
                <a href="#" className="text-gray-500 hover:text-white transition-colors">Privacy</a>
                <a href="#" className="text-gray-500 hover:text-white transition-colors">Terms</a>
                <a href="#" className="text-gray-500 hover:text-white transition-colors">Support</a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

// Submit Jersey Page Component (Discogs-like submission system)
const SubmitJerseyPage = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    team: '',
    season: '',
    player: '',
    size: '',
    condition: '',
    manufacturer: '',
    home_away: '',
    league: '',
    description: '',
    reference_code: ''
  });
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      alert('Please login to submit a jersey');
      return;
    }

    if (!formData.team || !formData.season || !formData.size || !formData.condition) {
      alert('Please fill in all required fields (Team, Season, Size, Condition)');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Clean and prepare data
      const jerseyData = {
        team: formData.team.trim(),
        season: formData.season,
        player: formData.player?.trim() || null,
        size: formData.size,
        condition: formData.condition,
        manufacturer: formData.manufacturer?.trim() || "",
        home_away: formData.home_away || "",
        league: formData.league?.trim() || "",
        description: formData.description?.trim() || "",
        reference_code: formData.reference_code?.trim() || null,
        images: images
      };

      console.log('🟡 Submitting jersey data:', jerseyData);

      const response = await axios.post(`${API}/api/jerseys`, jerseyData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('✅ Jersey submission successful:', response.data);

      // Only set submitted to true if we get a successful response
      if (response.status === 200 || response.status === 201) {
        setSubmitted(true);
        setFormData({
          team: '', season: '', player: '', size: '', condition: '', 
          manufacturer: '', home_away: '', league: '', description: '', reference_code: ''
        });
        setImages([]);
      }
    } catch (error) {
      console.error('❌ Jersey submission error:', error);
      
      let errorMessage = 'Failed to submit jersey';
      
      if (error.response) {
        // Server responded with error status
        errorMessage = error.response.data?.detail || `Server error (${error.response.status})`;
        console.error('Server error details:', error.response.data);
      } else if (error.request) {
        // Request made but no response
        errorMessage = 'No response from server - check your connection';
      } else {
        // Something happened in setting up the request
        errorMessage = error.message;
      }
      
      alert(`❌ Submission failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-24">
        <div className="text-6xl mb-6">🔒</div>
        <h2 className="text-3xl font-bold text-white mb-4">Login Required</h2>
        <p className="text-gray-400 mb-8">You need to be logged in to submit jerseys to the database.</p>
        <button 
          onClick={() => window.dispatchEvent(new CustomEvent('showAuthModal'))}
          className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
        >
          Login / Sign Up
        </button>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="text-center py-24">
        <div className="text-6xl mb-6">🎉</div>
        <h2 className="text-3xl font-bold text-white mb-4">Jersey Submitted!</h2>
        <p className="text-gray-400 mb-4">Your jersey submission has been sent for review.</p>
        <p className="text-sm text-gray-500 mb-8">
          Our team will review your submission and approve it if it meets our quality standards. 
          This usually takes 1-2 business days.
        </p>
        <button 
          onClick={() => setSubmitted(false)}
          className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold mr-4"
        >
          Submit Another Jersey
        </button>
        <button 
          onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'jerseys' }))}
          className="bg-gray-700 text-white px-8 py-3 rounded-lg hover:bg-gray-600 transition-colors font-semibold"
        >
          Browse Jerseys
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Submit New Jersey</h1>
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-start">
            <div className="text-blue-400 text-xl mr-3 mt-1">ℹ️</div>
            <div>
              <h3 className="text-blue-300 font-semibold mb-2">Submission Process</h3>
              <p className="text-blue-200 text-sm leading-relaxed">
                Similar to Discogs, all jersey submissions are reviewed by our moderation team before being published. 
                This ensures database quality and prevents duplicates. Your submission will be visible to all users once approved.
              </p>
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-gray-900 rounded-xl shadow-2xl p-8 border border-gray-800">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Team */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Team *</label>
            <input
              type="text"
              required
              value={formData.team}
              onChange={(e) => setFormData({...formData, team: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
              placeholder="e.g., Manchester United, FC Barcelona"
            />
          </div>

          {/* Season */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Season *</label>
            <select
              required
              value={formData.season}
              onChange={(e) => setFormData({...formData, season: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white"
            >
              <option value="">Select Season</option>
              {SEASONS.map(season => (
                <option key={season} value={season} className="bg-gray-800">{season}</option>
              ))}
            </select>
          </div>

          {/* Player */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Player (Optional)</label>
            <input
              type="text"
              value={formData.player}
              onChange={(e) => setFormData({...formData, player: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
              placeholder="e.g., Ronaldo, Messi"
            />
          </div>

          {/* Size */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Size *</label>
            <select
              required
              value={formData.size}
              onChange={(e) => setFormData({...formData, size: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white"
            >
              <option value="">Select Size</option>
              <option value="XS" className="bg-gray-800">XS</option>
              <option value="S" className="bg-gray-800">S</option>
              <option value="M" className="bg-gray-800">M</option>
              <option value="L" className="bg-gray-800">L</option>
              <option value="XL" className="bg-gray-800">XL</option>
              <option value="XXL" className="bg-gray-800">XXL</option>
            </select>
          </div>

          {/* Condition */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Condition *</label>
            <select
              required
              value={formData.condition}
              onChange={(e) => setFormData({...formData, condition: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white"
            >
              <option value="">Select Condition</option>
              <option value="new" className="bg-gray-800">New</option>
              <option value="near_mint" className="bg-gray-800">Near Mint</option>
              <option value="very_good" className="bg-gray-800">Very Good</option>
              <option value="good" className="bg-gray-800">Good</option>
              <option value="poor" className="bg-gray-800">Poor</option>
            </select>
          </div>

          {/* Manufacturer */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Manufacturer</label>
            <input
              type="text"
              value={formData.manufacturer}
              onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
              placeholder="e.g., Nike, Adidas, Puma"
            />
          </div>

          {/* Home/Away */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Type</label>
            <select
              value={formData.home_away}
              onChange={(e) => setFormData({...formData, home_away: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white"
            >
              <option value="">Select Type</option>
              <option value="home" className="bg-gray-800">Home</option>
              <option value="away" className="bg-gray-800">Away</option>
              <option value="third" className="bg-gray-800">Third</option>
              <option value="special" className="bg-gray-800">Special Edition</option>
            </select>
          </div>

          {/* League */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">League/Competition</label>
            <input
              type="text"
              value={formData.league}
              onChange={(e) => setFormData({...formData, league: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
              placeholder="e.g., Premier League, La Liga, World Cup"
            />
          </div>

          {/* Reference Code */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Reference Code</label>
            <input
              type="text"
              value={formData.reference_code}
              onChange={(e) => setFormData({...formData, reference_code: e.target.value})}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
              placeholder="Internal reference code (if known)"
            />
          </div>
        </div>

        {/* Description */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows={4}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-white placeholder-gray-400"
            placeholder="Additional details about this jersey..."
          />
        </div>

        {/* Image Upload */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Images</label>
          <ImageUpload images={images} setImages={setImages} />
        </div>

        {/* Submit Button */}
        <div className="mt-8 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="bg-white text-black px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit for Review'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Admin Panel Component (topkitfr@gmail.com only)
const AdminPanel = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('jerseys');
  const [pendingJerseys, setPendingJerseys] = useState([]);
  const [users, setUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (user?.email === 'topkitfr@gmail.com') {
      if (activeTab === 'jerseys') {
        fetchPendingJerseys();
      } else if (activeTab === 'users') {
        fetchUsers();
      } else if (activeTab === 'activities') {
        fetchActivities();
      }
    }
  }, [user, activeTab]);

  const fetchPendingJerseys = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/admin/jerseys/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingJerseys(response.data);
    } catch (error) {
      console.error('Failed to fetch pending jerseys:', error);
      alert('Failed to load pending submissions');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data.users);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      alert('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/admin/activities`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActivities(response.data.activities);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
      alert('Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (jerseyId) => {
    if (!confirm('Approve this jersey submission?')) return;
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/admin/jerseys/${jerseyId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Jersey approved successfully!');
      fetchPendingJerseys();
      setSelectedJersey(null);
    } catch (error) {
      console.error('Approval error:', error);
      alert('Failed to approve jersey');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (jerseyId) => {
    const reason = prompt('Reason for rejection (optional):');
    if (reason === null) return; // User cancelled
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/admin/jerseys/${jerseyId}/reject`, {
        reason: reason || 'No reason provided'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Jersey rejected successfully!');
      fetchPendingJerseys();
      setSelectedJersey(null);
    } catch (error) {
      console.error('Rejection error:', error);
      alert('Failed to reject jersey');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSuggestModifications = async (jerseyId) => {
    const suggestedChanges = prompt('What modifications would you like to suggest to the user? Please provide detailed feedback:');
    if (!suggestedChanges || suggestedChanges.trim() === '') return;
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/admin/jerseys/${jerseyId}/suggest-modifications`, {
        jersey_id: jerseyId,
        suggested_changes: suggestedChanges.trim(),
        suggested_modifications: {}
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Modification suggestions sent to user successfully!');
      fetchPendingJerseys();
      setSelectedJersey(null);
    } catch (error) {
      console.error('Suggest modifications error:', error);
      alert('Failed to send modification suggestions');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAssignRole = async (userId, newRole, userName) => {
    const reason = prompt(`Assigning ${newRole} role to ${userName}. Reason (optional):`);
    if (reason === null) return; // User cancelled
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/admin/users/${userId}/assign-role`, {
        user_id: userId,
        role: newRole,
        reason: reason || 'No reason provided'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert(`Role ${newRole} assigned successfully to ${userName}!`);
      fetchUsers();
    } catch (error) {
      console.error('Role assignment error:', error);
      alert('Failed to assign role');
    } finally {
      setActionLoading(false);
    }
  };

  if (user?.email !== 'topkitfr@gmail.com') {
    return (
      <div className="text-center py-24">
        <div className="text-6xl mb-6">🚫</div>
        <h2 className="text-3xl font-bold text-white mb-4">Access Denied</h2>
        <p className="text-gray-400">This area is restricted to administrators only.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">🔧 Admin Panel</h1>
        <div className="flex space-x-1 bg-gray-800 rounded-lg p-1 border border-gray-700">
          <button
            onClick={() => setActiveTab('jerseys')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'jerseys'
                ? 'bg-red-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            📝 Jersey Validation
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'users'
                ? 'bg-red-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            👥 User Management
          </button>
          <button
            onClick={() => setActiveTab('activities')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'activities'
                ? 'bg-red-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            📊 Activities
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-400">Loading...</div>
      ) : activeTab === 'jerseys' ? (
        <div>
          <h2 className="text-xl font-bold text-white mb-6">
            📝 Pending Jersey Submissions ({pendingJerseys.length})
          </h2>
          
          {pendingJerseys.length === 0 ? (
            <div className="text-center py-16 bg-gray-800 rounded-2xl">
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-2xl font-bold text-white mb-4">All caught up!</h3>
              <p className="text-gray-400">No pending jersey submissions to review.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {pendingJerseys.map((jersey) => (
                <div key={jersey.id} className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white truncate">
                      {jersey.team} {jersey.season}
                    </h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleApprove(jersey.id)}
                        disabled={actionLoading}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                      >
                        ✅ Approve
                      </button>
                      <button
                        onClick={() => handleSuggestModifications(jersey.id)}
                        disabled={actionLoading}
                        className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                      >
                        🔧 Suggest Changes
                      </button>
                      <button
                        onClick={() => handleReject(jersey.id)}
                        disabled={actionLoading}
                        className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                      >
                        ❌ Reject
                      </button>
                    </div>
                  </div>
                  
                  <div className="text-gray-300 text-sm space-y-1">
                    {jersey.player && <p><span className="text-gray-400">Player:</span> {jersey.player}</p>}
                    <p><span className="text-gray-400">Size:</span> {jersey.size}</p>
                    <p><span className="text-gray-400">Condition:</span> {jersey.condition}</p>
                    {jersey.manufacturer && <p><span className="text-gray-400">Brand:</span> {jersey.manufacturer}</p>}
                    {jersey.league && <p><span className="text-gray-400">League:</span> {jersey.league}</p>}
                    {jersey.reference_code && <p><span className="text-gray-400">Ref:</span> {jersey.reference_code}</p>}
                    {jersey.description && <p><span className="text-gray-400">Description:</span> {jersey.description}</p>}
                    <p className="text-xs text-gray-500 pt-2">
                      Submitted: {new Date(jersey.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : activeTab === 'users' ? (
        <div>
          <h2 className="text-xl font-bold text-white mb-6">
            👥 User Management ({users.length} users)
          </h2>
          
          <div className="space-y-4">
            {users.map((userData) => (
              <div key={userData.id} className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-4">
                      <Avatar user={userData} size="md" />
                      <div>
                        <h3 className="text-lg font-bold text-white">{userData.name}</h3>
                        <p className="text-gray-400 text-sm">{userData.email}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            userData.role === 'admin' ? 'bg-red-900 text-red-300' :
                            userData.role === 'moderator' ? 'bg-blue-900 text-blue-300' :
                            'bg-gray-900 text-gray-300'
                          }`}>
                            {userData.role === 'admin' ? '👑 Admin' : 
                             userData.role === 'moderator' ? '🔧 Moderator' : 
                             '👤 User'}
                          </span>
                          <span className="text-gray-500 text-xs">
                            {userData.provider} • {new Date(userData.created_at).toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                      <div className="bg-gray-700 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-white">{userData.stats.jerseys_submitted}</div>
                        <div className="text-xs text-gray-400">Submitted</div>
                      </div>
                      <div className="bg-gray-700 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-green-400">{userData.stats.jerseys_approved}</div>
                        <div className="text-xs text-gray-400">Approved</div>
                      </div>
                      <div className="bg-gray-700 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-red-400">{userData.stats.jerseys_rejected}</div>
                        <div className="text-xs text-gray-400">Rejected</div>
                      </div>
                      <div className="bg-gray-700 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-blue-400">{userData.stats.collections_added}</div>
                        <div className="text-xs text-gray-400">Collections</div>
                      </div>
                      <div className="bg-gray-700 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-purple-400">{userData.stats.listings_created}</div>
                        <div className="text-xs text-gray-400">Listings</div>
                      </div>
                    </div>

                    {userData.recent_activities && userData.recent_activities.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-2">Recent Activities</h4>
                        <div className="space-y-1">
                          {userData.recent_activities.slice(0, 3).map((activity, index) => (
                            <div key={index} className="text-xs text-gray-500">
                              <span className="text-gray-300">{activity.action.replace('_', ' ')}</span>
                              <span className="mx-2">•</span>
                              {new Date(activity.created_at).toLocaleDateString('fr-FR')}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col space-y-2 ml-4">
                    {userData.email !== 'topkitfr@gmail.com' && (
                      <>
                        {userData.role !== 'moderator' && (
                          <button
                            onClick={() => handleAssignRole(userData.id, 'moderator', userData.name)}
                            disabled={actionLoading}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                          >
                            🔧 Make Moderator
                          </button>
                        )}
                        {userData.role === 'moderator' && (
                          <button
                            onClick={() => handleAssignRole(userData.id, 'user', userData.name)}
                            disabled={actionLoading}
                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                          >
                            👤 Remove Moderator
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div>
          <h2 className="text-xl font-bold text-white mb-6">
            📊 System Activities ({activities.length} recent)
          </h2>
          
          <div className="space-y-3">
            {activities.map((activity) => (
              <div key={activity.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-white">
                        {activity.user_name || activity.user_email}
                      </span>
                      <span className="text-gray-500">•</span>
                      <span className="text-sm text-gray-400">
                        {activity.action.replace('_', ' ')}
                      </span>
                    </div>
                    
                    {activity.details && Object.keys(activity.details).length > 0 && (
                      <div className="text-xs text-gray-500">
                        {activity.details.jersey_name && (
                          <span>Jersey: {activity.details.jersey_name}</span>
                        )}
                        {activity.details.new_role && (
                          <span>New role: {activity.details.new_role}</span>
                        )}
                        {activity.details.reason && (
                          <span>Reason: {activity.details.reason}</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <span className="text-xs text-gray-500">
                    {new Date(activity.created_at).toLocaleDateString('fr-FR', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;