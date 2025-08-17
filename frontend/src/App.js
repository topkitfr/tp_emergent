import React, { useState, useEffect, createContext, useContext, useReducer } from 'react';
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

// Get the backend URL from environment variables
const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const SITE_MODE = process.env.REACT_APP_SITE_MODE || 'public';

// Site Access Check Component
const SiteAccessGate = ({ children }) => {
  const { user, loading: authLoading } = useAuth();
  const [hasAccess, setHasAccess] = useState(null);
  const [siteMode, setSiteMode] = useState('public');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSiteAccess();
  }, [user, user?.token]); // Added user.token as dependency

  useEffect(() => {
    // Listen for login events to refresh access
    const handleLoginSuccess = () => {
      setTimeout(() => {
        checkSiteAccess();
      }, 500); // Small delay to ensure token is saved
    };

    window.addEventListener('login-success', handleLoginSuccess);
    return () => window.removeEventListener('login-success', handleLoginSuccess);
  }, []);

  const checkSiteAccess = async () => {
    try {
      const headers = {};
      const token = user?.token || localStorage.getItem('token');
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API}/api/site/access-check`, {
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setHasAccess(data.has_access);
        setSiteMode(data.mode);
        console.log('Access check result:', data);
      } else {
        // If endpoint fails, fall back to environment variable
        setHasAccess(SITE_MODE === 'public');
        setSiteMode(SITE_MODE);
        console.log('Access check failed, using fallback');
      }
    } catch (error) {
      console.error('Error checking site access:', error);
      // Fall back to environment variable on error
      setHasAccess(SITE_MODE === 'public');
      setSiteMode(SITE_MODE);
    } finally {
      setLoading(false);
    }
  };

  // Show loading while checking access
  if (loading || authLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-bold text-white">TopKit</h2>
          <p className="text-gray-400">Chargement...</p>
        </div>
      </div>
    );
  }

  // If user has access, show the normal app
  if (hasAccess) {
    return children;
  }

  // Show private beta page for unauthorized users
  return (
    <PrivateBetaPage 
      siteMode={siteMode} 
      onAccessRequest={() => checkSiteAccess()} 
    />
  );
};

// Private Beta Landing Page
const PrivateBetaPage = ({ siteMode, onAccessRequest }) => {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showBetaRequestForm, setShowBetaRequestForm] = useState(false);
  const [betaFormData, setBetaFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    message: ''
  });
  const [betaFormSubmitting, setBetaFormSubmitting] = useState(false);
  const [betaFormSuccess, setBetaFormSuccess] = useState(false);

  const handleBetaFormSubmit = async (e) => {
    e.preventDefault();
    setBetaFormSubmitting(true);

    try {
      const response = await fetch(`${API}/api/beta/request-access`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(betaFormData)
      });

      if (response.ok) {
        const data = await response.json();
        setBetaFormSuccess(true);
        setBetaFormData({ email: '', first_name: '', last_name: '', message: '' });
      } else {
        const errorData = await response.json();
        alert(`Erreur: ${errorData.detail || 'Échec de la soumission'}`);
      }
    } catch (error) {
      console.error('Error submitting beta request:', error);
      alert('Erreur de connexion. Veuillez réessayer.');
    } finally {
      setBetaFormSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900 to-black">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-6">
        <div className="max-w-2xl mx-auto text-center">
          
          {/* Logo */}
          <div className="mb-8">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-400 via-white to-blue-400 bg-clip-text text-transparent mb-4">
              TopKit
            </h1>
            <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto rounded-full"></div>
          </div>

          {/* Status Badge */}
          <div className="inline-flex items-center space-x-2 bg-blue-900/30 border border-blue-500/50 rounded-full px-6 py-2 mb-8">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span className="text-blue-300 font-medium text-sm">Bêta Privée</span>
          </div>

          {/* Main Content */}
          <h2 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
            La Révolution du
            <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Marketplace Football
            </span>
          </h2>

          <p className="text-xl text-gray-300 mb-8 leading-relaxed">
            TopKit transforme l'achat et la vente de maillots de football. 
            Découvrez une plateforme dédiée aux passionnés, avec un système 
            de collection révolutionnaire inspiré de Discogs.
          </p>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
              <div className="text-3xl mb-3">👕</div>
              <h3 className="text-lg font-semibold mb-2">Marketplace Unique</h3>
              <p className="text-gray-400 text-sm">Achetez et vendez des maillots authentiques dans un environnement sécurisé</p>
            </div>
            <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="text-lg font-semibold mb-2">Collections Privées</h3>
              <p className="text-gray-400 text-sm">Gérez vos collections avec un système avancé de wishlist et inventaire</p>
            </div>
            <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
              <div className="text-3xl mb-3">💳</div>
              <h3 className="text-lg font-semibold mb-2">Paiements Sécurisés</h3>
              <p className="text-gray-400 text-sm">Transactions protégées avec Stripe et commission transparente</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            <button
              onClick={() => setShowAuthModal(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 px-8 rounded-xl transition-all transform hover:scale-105 shadow-lg hover:shadow-blue-500/25"
            >
              Accéder à la Bêta Privée
            </button>
            
            <div className="text-gray-400 text-sm">
              Réservé aux utilisateurs invités • Connexion requise
            </div>
          </div>

          {/* Beta Access Request Section */}
          <div className="mt-12 p-6 bg-gray-900/50 border border-gray-700 rounded-xl">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-white mb-3">🚀 Rejoignez la Bêta !</h3>
              <p className="text-gray-300">
                Pas encore d'accès ? Demandez une invitation à la phase de test privée.
              </p>
            </div>

            {!showBetaRequestForm && !betaFormSuccess ? (
              <div className="text-center">
                <button
                  onClick={() => setShowBetaRequestForm(true)}
                  className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-semibold py-3 px-6 rounded-lg transition-all transform hover:scale-105"
                >
                  Demander un Accès Bêta
                </button>
                <p className="text-gray-400 text-sm mt-2">
                  Gratuit • Traitement sous 24-48h
                </p>
              </div>
            ) : betaFormSuccess ? (
              <div className="text-center p-6 bg-green-900/20 border border-green-500/30 rounded-lg">
                <div className="text-4xl mb-3">✅</div>
                <h4 className="text-xl font-bold text-green-400 mb-2">Demande Soumise !</h4>
                <p className="text-green-300 mb-4">
                  Votre demande d'accès bêta a été envoyée avec succès. Nous examinerons votre demande et vous contacterons bientôt !
                </p>
                <button
                  onClick={() => {
                    setBetaFormSuccess(false);
                    setShowBetaRequestForm(false);
                  }}
                  className="text-green-400 hover:text-green-300 text-sm underline"
                >
                  Faire une autre demande
                </button>
              </div>
            ) : (
              <form onSubmit={handleBetaFormSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Prénom *
                    </label>
                    <input
                      type="text"
                      required
                      value={betaFormData.first_name}
                      onChange={(e) => setBetaFormData({...betaFormData, first_name: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      placeholder="Jean"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Nom *
                    </label>
                    <input
                      type="text"
                      required
                      value={betaFormData.last_name}
                      onChange={(e) => setBetaFormData({...betaFormData, last_name: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      placeholder="Dupont"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={betaFormData.email}
                    onChange={(e) => setBetaFormData({...betaFormData, email: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    placeholder="jean.dupont@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Message (optionnel)
                  </label>
                  <textarea
                    value={betaFormData.message}
                    onChange={(e) => setBetaFormData({...betaFormData, message: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    placeholder="Dites-nous pourquoi vous souhaitez rejoindre la bêta..."
                  />
                </div>
                
                <div className="flex space-x-3">
                  <button
                    type="submit"
                    disabled={betaFormSubmitting}
                    className="flex-1 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-all"
                  >
                    {betaFormSubmitting ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Envoi en cours...
                      </span>
                    ) : (
                      '📨 Envoyer ma Demande'
                    )}
                  </button>
                  
                  <button
                    type="button"
                    onClick={() => setShowBetaRequestForm(false)}
                    className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white rounded-lg transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Status Info */}
          <div className="mt-16 p-6 bg-gray-900/30 border border-gray-700 rounded-xl">
            <h4 className="text-lg font-semibold mb-3 text-blue-400">État de la Bêta</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Mode:</span>
                <span className="text-white capitalize">{siteMode}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Statut:</span>
                <span className="text-green-400">En développement</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  );
};

// Auth Context with useReducer for robust state management
const AuthContext = createContext();

// Auth actions
const authActions = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_ERROR: 'LOGIN_ERROR',
  LOGOUT: 'LOGOUT',
  SET_LOADING: 'SET_LOADING'
};

// Initial auth state
const initialAuthState = {
  user: null,
  loading: true,
  isAuthenticated: false,
  error: null
};

// Auth reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case authActions.LOGIN_START:
      return {
        ...state,
        loading: true,
        error: null
      };
    case authActions.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        loading: false,
        isAuthenticated: true,
        error: null
      };
    case authActions.LOGIN_ERROR:
      return {
        ...state,
        user: null,
        loading: false,
        isAuthenticated: false,
        error: action.payload.error
      };
    case authActions.LOGOUT:
      return {
        ...initialAuthState,
        loading: false
      };
    case authActions.SET_LOADING:
      return {
        ...state,
        loading: action.payload.loading
      };
    default:
      return state;
  }
};

const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);
  const [siteMode, setSiteMode] = useState('public');
  const [siteSettingsLoading, setSiteSettingsLoading] = useState(false);
  const [betaRequests, setBetaRequests] = useState([]);
  const [betaRequestsLoading, setBetaRequestsLoading] = useState(false);

  useEffect(() => {
    console.log('AuthProvider mounted, checking for existing token...');
    const token = localStorage.getItem('token');
    console.log('Token found in localStorage:', token ? token.substring(0, 20) + '...' : 'none');
    
    if (token) {
      console.log('Calling fetchProfile with existing token');
      fetchProfile(token);
    } else {
      console.log('No token found, setting loading to false');
      dispatch({ type: authActions.SET_LOADING, payload: { loading: false } });
    }
  }, []);

  const fetchProfile = async (token) => {
    try {
      dispatch({ type: authActions.LOGIN_START });
      console.log('Fetching profile with token:', token.substring(0, 20) + '...');
      
      const response = await axios.get(`${API}/api/profile`, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000
      });
      
      console.log('Profile response:', response.data);
      
      if (response.data?.user) {
        dispatch({ 
          type: authActions.LOGIN_SUCCESS, 
          payload: { user: response.data.user } 
        });
        console.log('✅ Profile loaded successfully:', response.data.user);
      } else {
        console.error('❌ Invalid profile response structure:', response.data);
        localStorage.removeItem('token');
        dispatch({ 
          type: authActions.LOGIN_ERROR, 
          payload: { error: 'Invalid profile response' } 
        });
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      console.error('Error response:', error.response?.data);
      localStorage.removeItem('token');
      dispatch({ 
        type: authActions.LOGIN_ERROR, 
        payload: { error: 'Failed to fetch profile' } 
      });
    }
  };

  const fetchSiteSettings = async () => {
    try {
      setSiteSettingsLoading(true);
      const response = await axios.get(`${API}/api/site/mode`);
      setSiteMode(response.data.mode);
    } catch (error) {
      console.error('Failed to fetch site settings:', error);
    } finally {
      setSiteSettingsLoading(false);
    }
  };

  const updateSiteMode = async (newMode) => {
    if (!window.confirm(`Changer le mode du site vers "${newMode}" ?`)) return;

    try {
      setSiteSettingsLoading(true);
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/site/mode`, {
        mode: newMode
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSiteMode(newMode);
      alert(`Mode du site changé vers: ${newMode}`);
    } catch (error) {
      console.error('Failed to update site mode:', error);
      alert('Erreur lors du changement de mode');
    } finally {
      setSiteSettingsLoading(false);
    }
  };

  const login = (token, userData) => {
    console.log('🔑 Login called with token:', token ? token.substring(0, 20) + '...' : 'NO TOKEN');
    console.log('👤 Login called with user data:', userData);
    
    if (!token || !userData) {
      console.error('❌ Login failed: missing token or userData');
      dispatch({ 
        type: authActions.LOGIN_ERROR, 
        payload: { error: 'Missing token or user data' } 
      });
      return false;
    }
    
    try {
      localStorage.setItem('token', token);
      console.log('💾 Token saved to localStorage');
      
      // Set user data immediately using reducer
      dispatch({ 
        type: authActions.LOGIN_SUCCESS, 
        payload: { user: userData } 
      });
      
      console.log('✅ Login successful - user state set:', userData);
      return true;
    } catch (error) {
      console.error('❌ Login failed during state update:', error);
      dispatch({ 
        type: authActions.LOGIN_ERROR, 
        payload: { error: 'Failed to save login state' } 
      });
      return false;
    }
  };

  const logout = () => {
    console.log('🚪 Logout called');
    localStorage.removeItem('token');
    dispatch({ type: authActions.LOGOUT });
  };

  const value = {
    user: state.user,
    loading: state.loading,
    isAuthenticated: state.isAuthenticated,
    error: state.error,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
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

// Shopping Cart Page Component with Stripe Integration
const ShoppingCartPage = ({ 
  cart, 
  setCart, 
  onRemoveFromCart, 
  onUpdateQuantity, 
  onClearCart 
}) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [processingPayment, setProcessingPayment] = useState(false);
  const [orderSummary, setOrderSummary] = useState({
    subtotal: 0,
    shipping: 0,
    taxes: 0,
    total: 0
  });
  const [purchaseHistory, setPurchaseHistory] = useState([]);
  const [salesHistory, setSalesHistory] = useState([]);
  
  // Check for payment return from Stripe
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId && !processingPayment) {
      setProcessingPayment(true);
      setPaymentStatus('checking');
      checkPaymentStatus(sessionId);
    }
  }, []);

  // Calculate order totals
  useEffect(() => {
    if (cart && cart.length > 0) {
      const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      const shipping = subtotal > 50 ? 0 : 9.99; // Free shipping over 50€
      const taxes = subtotal * 0.20; // 20% VAT
      const total = subtotal + shipping + taxes;
      
      setOrderSummary({
        subtotal: subtotal.toFixed(2),
        shipping: shipping.toFixed(2), 
        taxes: taxes.toFixed(2),
        total: total.toFixed(2)
      });
    }
  }, [cart]);

  const checkPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      setProcessingPayment(false);
      return;
    }

    try {
      const headers = {};
      if (user?.token) {
        headers.Authorization = `Bearer ${user.token}`;
      }

      const response = await fetch(`${API}/api/payments/checkout/status/${sessionId}`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      const data = await response.json();
      
      if (data.payment_status === 'paid') {
        setPaymentStatus('success');
        setProcessingPayment(false);
        // Clear cart on successful payment
        if (onClearCart) {
          onClearCart();
        }
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
      } else if (data.status === 'expired' || data.status === 'failed') {
        setPaymentStatus('failed');
        setProcessingPayment(false);
        return;
      }

      // If payment is still pending, continue polling
      setPaymentStatus('processing');
      setTimeout(() => checkPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setPaymentStatus('error');
      setProcessingPayment(false);
    }
  };

  const fetchPaymentHistory = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      
      // Fetch both purchase and sales history
      const [purchasesRes, salesRes] = await Promise.all([
        axios.get(`${API}/api/payments/history`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/api/payments/sales`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setPurchaseHistory(purchasesRes.data.purchases || []);
      setSalesHistory(salesRes.data.sales || []);
      
    } catch (error) {
      console.error('Failed to fetch payment history:', error);
      setPurchaseHistory([]);
      setSalesHistory([]);
    }
  };

  const fetchPaymentHistoryProfile = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      
      // Fetch both purchase and sales history
      const [purchasesRes, salesRes] = await Promise.all([
        axios.get(`${API}/api/payments/history`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/api/payments/sales`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setPurchaseHistory(purchasesRes.data.purchases || []);
      setSalesHistory(salesRes.data.sales || []);
      
    } catch (error) {
      console.error('Failed to fetch payment history:', error);
      setPurchaseHistory([]);
      setSalesHistory([]);
    }
  };

  const handleProceedToCheckout = async () => {
    if (!cart || cart.length === 0) return;
    
    // For now, handle single item checkout (cart should have one item for marketplace)
    // In a full implementation, you'd need to handle multiple items or batch processing
    const firstItem = cart[0];
    
    if (!firstItem.listingId) {
      alert('Erreur: Informations de listing manquantes. Veuillez réessayer.');
      return;
    }

    setLoading(true);
    
    try {
      const checkoutData = {
        listing_id: firstItem.listingId,
        origin_url: window.location.origin + '/cart'
      };

      const headers = {
        'Content-Type': 'application/json'
      };
      
      if (user?.token) {
        headers.Authorization = `Bearer ${user.token}`;
      }

      const response = await fetch(`${API}/api/payments/checkout/session`, {
        method: 'POST',
        headers,
        body: JSON.stringify(checkoutData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      console.error('Payment error:', error);
      alert(`Erreur de paiement: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Payment status display
  if (paymentStatus === 'checking' || paymentStatus === 'processing') {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold mb-2">Vérification du paiement...</h2>
          <p className="text-gray-400">Veuillez patienter pendant que nous confirmons votre paiement.</p>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'success') {
    return (
      <div className="min-h-screen bg-black text-white">
        <div className="container mx-auto px-6 py-12">
          <div className="text-center py-24">
            <div className="text-6xl mb-8">✅</div>
            <h1 className="text-4xl font-bold mb-4 text-green-400">Paiement réussi !</h1>
            <p className="text-xl text-gray-400 mb-12">
              Votre achat a été confirmé. Le vendeur sera contacté pour les détails de livraison.
            </p>
            
            <div className="space-y-4 max-w-md mx-auto">
              <button
                onClick={() => {
                  setPaymentStatus(null);
                  window.dispatchEvent(new CustomEvent('changeView', { detail: 'profile' }));
                }}
                className="w-full bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg"
              >
                Voir mes achats
              </button>
              <button
                onClick={() => {
                  setPaymentStatus(null);
                  window.dispatchEvent(new CustomEvent('changeView', { detail: 'marketplace' }));
                }}
                className="w-full bg-gray-700 text-white px-8 py-4 rounded-lg hover:bg-gray-600 transition-colors font-semibold"
              >
                Continuer mes achats
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'failed' || paymentStatus === 'error' || paymentStatus === 'timeout') {
    return (
      <div className="min-h-screen bg-black text-white">
        <div className="container mx-auto px-6 py-12">
          <div className="text-center py-24">
            <div className="text-6xl mb-8">❌</div>
            <h1 className="text-4xl font-bold mb-4 text-red-400">Paiement échoué</h1>
            <p className="text-xl text-gray-400 mb-12">
              {paymentStatus === 'timeout' 
                ? "Le délai de vérification du paiement a expiré. Veuillez vérifier votre email pour confirmation."
                : "Votre paiement n'a pas pu être traité. Veuillez réessayer."
              }
            </p>
            
            <div className="space-y-4 max-w-md mx-auto">
              <button
                onClick={() => {
                  setPaymentStatus(null);
                  window.history.replaceState({}, document.title, window.location.pathname);
                }}
                className="w-full bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg"
              >
                Réessayer
              </button>
              <button
                onClick={() => {
                  setPaymentStatus(null);
                  window.dispatchEvent(new CustomEvent('changeView', { detail: 'marketplace' }));
                }}
                className="w-full bg-gray-700 text-white px-8 py-4 rounded-lg hover:bg-gray-600 transition-colors font-semibold"
              >
                Retour au marketplace
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!cart || cart.length === 0) {
    return (
      <div className="min-h-screen bg-black text-white">
        <div className="container mx-auto px-6 py-12">
          <div className="text-center py-24">
            <div className="text-6xl mb-8">🛒</div>
            <h1 className="text-4xl font-bold mb-4">Votre panier est vide</h1>
            <p className="text-xl text-gray-400 mb-12">
              Découvrez des milliers de maillots de football dans notre marketplace
            </p>
            
            <div className="space-y-4 max-w-md mx-auto">
              <button
                onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'marketplace' }))}
                className="w-full bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg"
              >
                Commencer vos achats
              </button>
              <button
                onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'jerseys' }))}
                className="w-full bg-gray-700 text-white px-8 py-4 rounded-lg hover:bg-gray-600 transition-colors font-semibold"
              >
                Explorez les maillots
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto px-6 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Mon Panier</h1>
          <p className="text-gray-400">{cart.length} article{cart.length > 1 ? 's' : ''} dans votre panier</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-gray-900 rounded-lg border border-gray-700">
              
              {/* Cart Header */}
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Articles</h2>
                  <button
                    onClick={onClearCart}
                    className="text-red-400 hover:text-red-300 text-sm font-medium"
                  >
                    Vider le panier
                  </button>
                </div>
              </div>

              {/* Cart Items List */}
              <div className="divide-y divide-gray-700">
                {cart.map((item, index) => (
                  <div key={`${item.jerseyId}-${item.size}-${index}`} className="p-6">
                    <div className="flex items-start space-x-4">
                      
                      {/* Jersey Image */}
                      <div className="flex-shrink-0">
                        <img
                          src={item.images?.[0] || '/placeholder-jersey.png'}
                          alt={`${item.team} ${item.season}`}
                          className="w-20 h-20 object-cover rounded-lg bg-gray-800"
                        />
                      </div>

                      {/* Jersey Details */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-white mb-1">
                          {item.team}
                        </h3>
                        <p className="text-gray-400 text-sm mb-2">
                          {item.season} • {item.player || 'Maillot d\'équipe'} • Taille {item.size}
                        </p>
                        <p className="text-gray-400 text-sm mb-2">
                          État: {item.condition} • {item.manufacturer}
                        </p>
                        <div className="flex items-center space-x-4">
                          <span className="text-sm text-gray-400">Quantité:</span>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => onUpdateQuantity(item, Math.max(1, item.quantity - 1))}
                              className="w-8 h-8 flex items-center justify-center bg-gray-700 text-white rounded hover:bg-gray-600"
                            >
                              -
                            </button>
                            <span className="w-8 text-center">{item.quantity}</span>
                            <button
                              onClick={() => onUpdateQuantity(item, item.quantity + 1)}
                              className="w-8 h-8 flex items-center justify-center bg-gray-700 text-white rounded hover:bg-gray-600"
                            >
                              +
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Price and Actions */}
                      <div className="flex flex-col items-end space-y-2">
                        <div className="text-right">
                          <div className="text-lg font-semibold text-white">
                            {item.price.toFixed(2)} €
                          </div>
                          {item.quantity > 1 && (
                            <div className="text-sm text-gray-400">
                              {(item.price * item.quantity).toFixed(2)} € total
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => onRemoveFromCart(item)}
                          className="text-red-400 hover:text-red-300 text-sm font-medium"
                        >
                          Retirer
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 sticky top-8">
              
              <h2 className="text-xl font-semibold mb-6">Récapitulatif</h2>
              
              <div className="space-y-4 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-400">Sous-total</span>
                  <span className="text-white">{orderSummary.subtotal} €</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    Livraison
                    {parseFloat(orderSummary.subtotal) > 50 && (
                      <span className="text-green-400 text-sm ml-1">(Gratuite)</span>
                    )}
                  </span>
                  <span className="text-white">{orderSummary.shipping} €</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">TVA (20%)</span>
                  <span className="text-white">{orderSummary.taxes} €</span>
                </div>
                <hr className="border-gray-700" />
                <div className="flex justify-between text-lg font-semibold">
                  <span className="text-white">Total</span>
                  <span className="text-white">{orderSummary.total} €</span>
                </div>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleProceedToCheckout}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:opacity-50"
                >
                  {loading ? 'Traitement...' : 'Finaliser la commande'}
                </button>
                
                <button
                  onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'marketplace' }))}
                  className="w-full bg-gray-700 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  Continuer mes achats
                </button>
              </div>

              {/* Trust & Security */}
              <div className="mt-6 pt-6 border-t border-gray-700">
                <div className="text-center">
                  <div className="text-green-400 text-2xl mb-2">🔒</div>
                  <p className="text-sm text-gray-400">
                    Paiement sécurisé SSL
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Discogs-Style Header Component
const Header = ({ currentView, setCurrentView, setShowAuthModal, cartCount = 0 }) => {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showGeneralMenu, setShowGeneralMenu] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Handle search functionality
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Navigate to Explorez page and pass search query
      setCurrentView('jerseys');
      // You can add search query state management here if needed
      console.log('Searching for:', searchQuery);
    }
  };

  return (
    <>
      {/* Main Discogs-Style Header */}
      <header className="bg-black text-white shadow-lg border-b border-gray-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            
            {/* Left side - Logo */}
            <div className="flex items-center">
              <img 
                src="https://customer-assets.emergentagent.com/job_football-threads-5/artifacts/d38ypztj_ho7nwfgn_topkit_logo_nobc_wh.png"
                alt="TopKit Logo"
                className="h-8 w-auto cursor-pointer hover:opacity-80 transition-opacity"
                onClick={() => setCurrentView('home')}
              />
            </div>

            {/* Center-left - Search Bar */}
            <div className="flex-1 max-w-xl mx-8 hidden md:block">
              <form onSubmit={handleSearch} className="relative">
                <input
                  type="text"
                  placeholder="Rechercher des maillots..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-gray-900 text-white placeholder-gray-400 border border-gray-700 rounded-lg px-4 py-2 pr-10 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </form>
            </div>

            {/* Right side - Navigation and Utility Icons */}
            <div className="flex items-center space-x-1">
              
              {/* Main Navigation - Desktop */}
              <nav className="hidden lg:flex items-center space-x-1 mr-4">
                <button 
                  onClick={() => setCurrentView('home')}
                  className={`px-3 py-2 rounded transition-colors text-sm font-medium ${
                    currentView === 'home' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  Home
                </button>
                <button 
                  onClick={() => setCurrentView('jerseys')}
                  className={`px-3 py-2 rounded transition-colors text-sm font-medium ${
                    currentView === 'jerseys' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  Explorez
                </button>
                <button 
                  onClick={() => setCurrentView('marketplace')}
                  className={`px-3 py-2 rounded transition-colors text-sm font-medium ${
                    currentView === 'marketplace' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  Marketplace
                </button>
              </nav>

              {/* Utility Icons */}
              <div className="flex items-center space-x-2">
                
                {/* Cart Icon with Badge */}
                <button 
                  onClick={() => setCurrentView('cart')}
                  className={`p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors relative ${
                    currentView === 'cart' ? 'bg-gray-700 text-white' : ''
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5H20M7 13v4a2 2 0 002 2h6a2 2 0 002-2v-4" />
                  </svg>
                  {cartCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                      {cartCount > 9 ? '9+' : cartCount}
                    </span>
                  )}
                </button>

                {/* Messages Icon */}
                <button 
                  onClick={() => user ? setCurrentView('profile') : setShowAuthModal(true)}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </button>

                {/* Notifications */}
                {user && <NotificationBell />}

                {/* Profile Menu */}
                {user ? (
                  <div className="relative">
                    <button
                      onClick={() => setShowProfileMenu(!showProfileMenu)}
                      className="flex items-center space-x-2 p-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded transition-colors"
                    >
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-6 h-6 rounded-full" />
                      ) : (
                        <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-xs">
                          {user.name?.[0]?.toUpperCase()}
                        </div>
                      )}
                      <svg className={`w-3 h-3 transition-transform ${showProfileMenu ? 'rotate-180' : ''}`} fill="currentColor" viewBox="0 0 12 12">
                        <path d="M6 8L2 4h8l-4 4z"/>
                      </svg>
                    </button>
                    
                    {/* Profile Dropdown */}
                    {showProfileMenu && (
                      <div className="absolute right-0 top-full mt-1 w-48 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50">
                        <div className="p-3 border-b border-gray-700">
                          <div className="text-sm font-medium text-white">{user.name}</div>
                          <div className="text-xs text-gray-400">{user.email}</div>
                        </div>
                        <div className="py-1">
                          <button
                            onClick={() => {
                              setCurrentView('profile');
                              setShowProfileMenu(false);
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800"
                          >
                            👤 Mon Profil
                          </button>
                          <button
                            onClick={() => {
                              setCurrentView('settings');
                              setShowProfileMenu(false);
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800"
                          >
                            ⚙️ Paramètres
                          </button>
                          {user.email === 'topkitfr@gmail.com' && (
                            <button
                              onClick={() => {
                                setCurrentView('admin');
                                setShowProfileMenu(false);
                              }}
                              className="w-full text-left px-4 py-2 text-sm text-red-400 hover:text-white hover:bg-red-800"
                            >
                              🔧 Admin Panel
                            </button>
                          )}
                          <hr className="border-gray-700 my-1" />
                          <button
                            onClick={() => {
                              logout();
                              setShowProfileMenu(false);
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-red-400 hover:text-white hover:bg-red-800"
                          >
                            Déconnexion
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <button 
                    onClick={() => setShowAuthModal(true)}
                    className="px-3 py-2 text-sm font-medium text-blue-400 hover:text-white hover:bg-blue-800 rounded transition-colors"
                  >
                    Se connecter
                  </button>
                )}

                {/* General Menu Button */}
                <button
                  onClick={() => setShowGeneralMenu(!showGeneralMenu)}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors lg:hidden"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Mobile Search Bar */}
          <div className="md:hidden mt-3">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Rechercher des maillots..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-900 text-white placeholder-gray-400 border border-gray-700 rounded-lg px-4 py-2 pr-10 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </form>
          </div>
        </div>
      </header>

      {/* General Menu Side Panel */}
      {showGeneralMenu && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 lg:hidden" onClick={() => setShowGeneralMenu(false)}>
          <div 
            className="fixed left-0 top-0 h-full w-80 bg-gray-900 shadow-xl transform transition-transform"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white">Navigation</h3>
                <button 
                  onClick={() => setShowGeneralMenu(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <nav className="space-y-2">
                <button 
                  onClick={() => {
                    setCurrentView('home');
                    setShowGeneralMenu(false);
                  }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors font-medium ${
                    currentView === 'home' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  🏠 Home
                </button>
                <button 
                  onClick={() => {
                    setCurrentView('jerseys');
                    setShowGeneralMenu(false);
                  }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors font-medium ${
                    currentView === 'jerseys' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  🔍 Explorez
                </button>
                <button 
                  onClick={() => {
                    setCurrentView('marketplace');
                    setShowGeneralMenu(false);
                  }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors font-medium ${
                    currentView === 'marketplace' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  🛒 Marketplace
                </button>
                <button 
                  onClick={() => {
                    setCurrentView('cart');
                    setShowGeneralMenu(false);
                  }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors font-medium ${
                    currentView === 'cart' 
                      ? 'bg-gray-700 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  🛍️ Mon Panier {cartCount > 0 && `(${cartCount})`}
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Close dropdowns when clicking outside */}
      {(showProfileMenu || showGeneralMenu) && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => {
            setShowProfileMenu(false);
            setShowGeneralMenu(false);
          }}
        />
      )}
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
                  e.target.src = 'https://dummyimage.com/100x100/333/fff.png&text=Invalid+Image';
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
                  src={jersey.images?.[0] || 'https://dummyimage.com/400x500/333/fff.png&text=Jersey+Image'}
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
      await axios.post(`${API}/api/conversations`, {
        recipient_id: listing.seller_id,
        message: message.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Message sent successfully!');
      onClose();
    } catch (error) {
      console.error('Error sending message:', error);
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
      
      // Note: Jersey is not automatically added to collection when submitted for review
      // User can add it to their collection after admin approval

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
    e.stopPropagation();
    
    console.log('🚀 Form submitted - handleSubmit called');
    console.log('📧 Form data:', { email: formData.email, password: formData.password ? '***' : 'empty', name: formData.name });
    console.log('🔄 isLogin:', isLogin);
    console.log('🌐 API URL:', API);
    
    if (!formData.email || !formData.password) {
      console.error('❌ Missing required fields');
      setError('Please fill in all required fields');
      return;
    }
    
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const fullUrl = `${API}${endpoint}`;
      console.log('🔄 Making request to:', fullUrl);
      
      const response = await axios.post(fullUrl, formData, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log('✅ Response received:', response.status, response.data);
      
      // Handle different response types for login vs registration
      if (isLogin) {
        // Login flow - expect token and user
        if (response.data?.token && response.data?.user) {
          console.log('🔑 Token and user received, calling login...');
          const loginSuccess = login(response.data.token, response.data.user);
          if (loginSuccess) {
            console.log('✅ Login successful, closing modal and triggering access check');
            // Dispatch event to trigger site access check
            window.dispatchEvent(new Event('login-success'));
            // Force immediate UI update by dispatching a custom event
            window.dispatchEvent(new Event('authStateChanged'));
            // Small delay to ensure state propagation
            setTimeout(() => {
              onClose();
            }, 100);
          } else {
            console.error('❌ Login context update failed');
            setError('Erreur lors de la mise à jour de la session. Veuillez réessayer.');
          }
        } else {
          console.error('❌ Invalid login response structure:', response.data);
          setError('Réponse d\'authentification invalide. Veuillez réessayer.');
        }
      } else {
        // Registration flow - expect message and user (no immediate token)
        if (response.data?.message && response.data?.user) {
          console.log('✅ Registration successful:', response.data.message);
          
          // Show success message with email verification instructions
          setError(''); // Clear any previous errors
          alert(`✅ ${response.data.message}\n\n${response.data.instructions}\n\n${response.data.dev_verification_link ? 'Lien de développement: ' + response.data.dev_verification_link : ''}`);
          
          // Switch to login mode after successful registration
          setIsLogin(true);
          setFormData({ email: formData.email, password: '', name: '' }); // Clear password but keep email
          
        } else if (response.data?.token && response.data?.user) {
          // Fallback: immediate login after registration (for admin accounts)
          console.log('🔑 Registration with immediate token received');
          const loginSuccess = login(response.data.token, response.data.user);
          if (loginSuccess) {
            console.log('✅ Registration and login successful');
            window.dispatchEvent(new Event('authStateChanged'));
            setTimeout(() => {
              onClose();
            }, 100);
          }
        } else {
          console.error('❌ Invalid registration response structure:', response.data);
          setError('Erreur lors de la création du compte. Veuillez réessayer.');
        }
      }
    } catch (error) {
      console.error('❌ Authentication request failed:', error);
      if (error.code === 'ECONNABORTED') {
        setError('Connexion timeout - Vérifiez votre connexion internet');
      } else if (error.response?.status === 404) {
        setError('Service d\'authentification non disponible');
      } else if (error.response?.status === 500) {
        setError('Erreur serveur - Réessayez plus tard');
      } else if (error.response?.status === 401) {
        setError('Email ou mot de passe incorrect');
      } else if (error.response?.status === 403 && isLogin) {
        // Email not verified error
        const errorMessage = error.response?.data?.detail || '';
        if (errorMessage.includes('vérifier') || errorMessage.includes('email')) {
          setError(errorMessage + '\n\nSouhaitez-vous recevoir un nouveau lien de vérification ?');
          // TODO: Add resend verification button here
        } else {
          setError(errorMessage);
        }
      } else if (error.response?.status === 429) {
        // Rate limiting error
        setError(error.response?.data?.detail || 'Trop de tentatives. Réessayez plus tard.');
      } else if (error.response?.status === 400) {
        // Validation errors (password strength, user exists, etc.)
        setError(error.response?.data?.detail || 'Données invalides');
      } else {
        setError(error.response?.data?.detail || error.message || 'Erreur d\'authentification');
      }
    } finally {
      setLoading(false);
    }
  };

  // Google OAuth removed - function no longer needed
  // const handleGoogleAuth = () => {
  //   window.location.href = `${API}/api/auth/google`;
  // };



  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]" 
         onClick={(e) => {
           // Only close modal if clicking directly on backdrop, not on form elements or their children
           if (e.target === e.currentTarget) {
             onClose();
           }
         }}>
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 relative z-[9999]" 
           onClick={(e) => {
             // Only prevent clicks that would close the modal, but allow form interactions
             // Don't stopPropagation on form elements or their children
             const target = e.target;
             const isFormElement = target.tagName === 'INPUT' || 
                                   target.tagName === 'BUTTON' || 
                                   target.tagName === 'FORM' ||
                                   target.closest('form');
             
             if (!isFormElement) {
               e.stopPropagation();
             }
           }}>
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
              placeholder="Nom complet"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 bg-white"
              required={!isLogin}
              minLength={2}
              maxLength={50}
            />
          )}
          
          <input
            type="email"
            placeholder="Adresse email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 bg-white"
            required
          />
          
          <div className="space-y-2">
            <input
              type="password"
              placeholder={isLogin ? "Mot de passe" : "Mot de passe (min. 8 caractères)"}
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 bg-white"
              required
              minLength={isLogin ? 1 : 8}
            />
            
            {!isLogin && formData.password && (
              <div className="text-xs space-y-1 px-2">
                <div className="text-gray-600">Votre mot de passe doit contenir :</div>
                <div className={`flex items-center space-x-1 ${formData.password.length >= 8 ? 'text-green-600' : 'text-gray-400'}`}>
                  <span>{formData.password.length >= 8 ? '✓' : '○'}</span>
                  <span>Au moins 8 caractères</span>
                </div>
                <div className={`flex items-center space-x-1 ${/[A-Z]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'}`}>
                  <span>{/[A-Z]/.test(formData.password) ? '✓' : '○'}</span>
                  <span>Une majuscule</span>
                </div>
                <div className={`flex items-center space-x-1 ${/[a-z]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'}`}>
                  <span>{/[a-z]/.test(formData.password) ? '✓' : '○'}</span>
                  <span>Une minuscule</span>
                </div>
                <div className={`flex items-center space-x-1 ${/\d/.test(formData.password) ? 'text-green-600' : 'text-gray-400'}`}>
                  <span>{/\d/.test(formData.password) ? '✓' : '○'}</span>
                  <span>Un chiffre</span>
                </div>
                <div className={`flex items-center space-x-1 ${/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'}`}>
                  <span>{/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? '✓' : '○'}</span>
                  <span>Un caractère spécial</span>
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Chargement...' : (isLogin ? 'Se connecter' : 'Créer mon compte')}
          </button>
        </form>

        {/* OAuth options removed - using email/password authentication only */}
        {/* Google OAuth was non-functional and has been disabled for security reasons */}
        
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            {isLogin ? 
              "Pas encore de compte ? " : 
              "Vous avez déjà un compte ? "
            }
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setFormData({ email: '', password: '', name: '' });
              }}
              className="text-green-600 hover:text-green-500 font-medium"
            >
              {isLogin ? 'Créer un compte' : 'Se connecter'}
            </button>
          </p>
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

// Enhanced Browse Jerseys Page with Dark Theme  
const BrowseJerseysPage = ({ jerseys, loading, onFilter, onAddToCollection, onJerseyClick, onCreatorClick, onViewUserProfile }) => {
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState('list');
  const [sortBy, setSortBy] = useState('newest');
  const [searchQuery, setSearchQuery] = useState('');
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [activeTab, setActiveTab] = useState('jerseys');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  const [filters, setFilters] = useState({
    league: '',
    team: '',
    season: '',
    size: '',
    condition: '',
    manufacturer: ''
  });

  // Get unique values for filters
  const getUniqueValues = (field) => {
    const values = jerseys.map(jersey => jersey[field]).filter(v => v && v.trim());
    return [...new Set(values)].sort();
  };

  // Filter and search jerseys
  const getFilteredJerseys = () => {
    let filtered = jerseys;

    if (searchQuery) {
      filtered = filtered.filter(jersey => 
        jersey.team?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.player?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.league?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.season?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        filtered = filtered.filter(jersey => 
          jersey[key]?.toLowerCase().includes(value.toLowerCase())
        );
      }
    });

    switch (sortBy) {
      case 'team':
        filtered.sort((a, b) => (a.team || '').localeCompare(b.team || ''));
        break;
      case 'season':
        filtered.sort((a, b) => (b.season || '').localeCompare(a.season || ''));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      default:
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    return filtered;
  };

  // Handle user search
  const handleUserSearch = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.length >= 2) {
      setSearchLoading(true);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API}/api/users/search?query=${encodeURIComponent(query)}`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (response.ok) {
          const users = await response.json();
          setSearchResults(users);
        } else {
          setSearchResults([]);
        }
      } catch (error) {
        console.error('Failed to search users:', error);
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    } else {
      setSearchResults([]);
      setSearchLoading(false);
    }
  };

  const DarkJerseyCard = ({ jersey, isListView }) => (
    <div 
      className={`bg-gray-900 border border-gray-700 hover:border-gray-600 transition-all duration-200 cursor-pointer group relative ${
        isListView ? 'flex items-center p-4 rounded-lg mb-2' : 'rounded-lg overflow-hidden'
      }`}
      onClick={() => onJerseyClick && onJerseyClick(jersey)}
    >
      {isListView ? (
        <>
          <div className="w-16 h-16 md:w-20 md:h-20 bg-gray-800 rounded flex items-center justify-center overflow-hidden mr-4 flex-shrink-0">
            {jersey.images && jersey.images.length > 0 ? (
              <img
                src={jersey.images[0]}
                alt={`${jersey.team} ${jersey.season}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://dummyimage.com/80x80/333/fff.png&text=Jersey';
                }}
              />
            ) : (
              <span className="text-gray-500 text-2xl">👕</span>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold text-sm md:text-base mb-1 truncate">
              {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
            </h3>
            <div className="text-gray-400 text-xs md:text-sm mb-2">
              {jersey.league} • {jersey.season} • {jersey.home_away}
            </div>
            <div className="text-xs text-gray-500">
              TK{jersey.reference_number} • Taille: {jersey.size}
            </div>
          </div>

          {user && (
            <div className="flex flex-col sm:flex-row gap-2 ml-4">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAddToCollection && onAddToCollection(jersey.id, 'owned');
                }}
                className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                title="Ajouter à ma collection"
              >
                ❤️ Own
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAddToCollection && onAddToCollection(jersey.id, 'wanted');
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                title="Ajouter à ma wishlist"
              >
                ⭐ Want
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="aspect-square bg-gray-800 flex items-center justify-center overflow-hidden">
            {jersey.images && jersey.images.length > 0 ? (
              <img
                src={jersey.images[0]}
                alt={`${jersey.team} ${jersey.season}`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                onError={(e) => {
                  e.target.src = 'https://dummyimage.com/200x200/333/fff.png&text=Jersey';
                }}
              />
            ) : (
              <div className="text-gray-500 text-center">
                <div className="text-4xl mb-2">👕</div>
                <div className="text-sm">No Image</div>
              </div>
            )}
          </div>
          
          <div className="p-4">
            <h3 className="text-white font-semibold text-sm mb-1 truncate">
              {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
            </h3>
            <p className="text-gray-400 text-xs mb-2">
              {jersey.league} • {jersey.season}
            </p>
            <p className="text-gray-500 text-xs mb-3">
              TK{jersey.reference_number}
            </p>
            
            {user && (
              <div className="space-y-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onAddToCollection && onAddToCollection(jersey.id, 'owned');
                  }}
                  className="w-full bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                >
                  ❤️ Own
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onAddToCollection && onAddToCollection(jersey.id, 'wanted');
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-xs font-medium transition-colors"
                >
                  ⭐ Want
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-black">
      {/* Responsive Header */}
      <div className="bg-gray-900 border-b border-gray-700">
        <div className="container mx-auto px-4 md:px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl md:text-2xl font-bold text-white">Explorez</h1>
            <div className="text-sm text-gray-400">
              {getFilteredJerseys().length} résultats
            </div>
          </div>
          
          {/* Responsive Search Bar */}
          <div className="flex space-x-2 md:space-x-4 mb-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Rechercher par équipe, joueur..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-3 md:px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
            <button 
              className="md:hidden bg-gray-700 text-white px-3 py-2 rounded-lg hover:bg-gray-600 transition-colors text-sm"
              onClick={() => setShowMobileFilters(!showMobileFilters)}
            >
              🔍
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 md:px-6 py-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Mobile Filters */}
          {showMobileFilters && (
            <div className="md:hidden bg-gray-900 rounded-lg border border-gray-700 p-4 mb-6">
              <h3 className="font-semibold text-white mb-4">Filtres</h3>
              <div className="space-y-4">
                {/* League Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Championnat</label>
                  <select
                    value={filters.league}
                    onChange={(e) => setFilters({...filters, league: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Tous les championnats</option>
                    {getUniqueValues('league').map(league => (
                      <option key={league} value={league}>{league}</option>
                    ))}
                  </select>
                </div>
                
                {/* Team Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Équipe</label>
                  <select
                    value={filters.team}
                    onChange={(e) => setFilters({...filters, team: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Toutes les équipes</option>
                    {getUniqueValues('team').slice(0, 20).map(team => (
                      <option key={team} value={team}>{team}</option>
                    ))}
                  </select>
                </div>
                
                {/* Season Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Saison</label>
                  <select
                    value={filters.season}
                    onChange={(e) => setFilters({...filters, season: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Toutes les saisons</option>
                    {getUniqueValues('season').map(season => (
                      <option key={season} value={season}>{season}</option>
                    ))}
                  </select>
                </div>
                
                {/* Size Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Taille</label>
                  <select
                    value={filters.size}
                    onChange={(e) => setFilters({...filters, size: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Toutes les tailles</option>
                    {['XS', 'S', 'M', 'L', 'XL', 'XXL'].map(size => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>
                
                <button
                  onClick={() => {
                    setFilters({
                      league: '', team: '', season: '', size: '', condition: '', manufacturer: ''
                    });
                    setShowMobileFilters(false);
                  }}
                  className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                >
                  Effacer
                </button>
              </div>
            </div>
          )}

          {/* Desktop Sidebar */}
          <div className="hidden md:block w-64 flex-shrink-0">
            <div className="bg-gray-900 rounded-lg border border-gray-700 p-4 sticky top-6">
              <h3 className="font-semibold text-white mb-4">Filtres</h3>
              <div className="space-y-4">
                {/* League Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Championnat</label>
                  <select
                    value={filters.league}
                    onChange={(e) => setFilters({...filters, league: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Tous les championnats</option>
                    {getUniqueValues('league').map(league => (
                      <option key={league} value={league}>{league}</option>
                    ))}
                  </select>
                </div>
                
                {/* Team Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Équipe</label>
                  <select
                    value={filters.team}
                    onChange={(e) => setFilters({...filters, team: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Toutes les équipes</option>
                    {getUniqueValues('team').slice(0, 20).map(team => (
                      <option key={team} value={team}>{team}</option>
                    ))}
                  </select>
                </div>
                
                {/* Season Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Saison</label>
                  <select
                    value={filters.season}
                    onChange={(e) => setFilters({...filters, season: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Toutes les saisons</option>
                    {getUniqueValues('season').map(season => (
                      <option key={season} value={season}>{season}</option>
                    ))}
                  </select>
                </div>
                
                {/* Size Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Taille</label>
                  <select
                    value={filters.size}
                    onChange={(e) => setFilters({...filters, size: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Toutes les tailles</option>
                    {['XS', 'S', 'M', 'L', 'XL', 'XXL'].map(size => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>
                
                {/* Condition Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">État</label>
                  <select
                    value={filters.condition}
                    onChange={(e) => setFilters({...filters, condition: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Tous les états</option>
                    <option value="mint">Mint</option>
                    <option value="excellent">Excellent</option>
                    <option value="very_good">Very Good</option>
                    <option value="good">Good</option>
                    <option value="poor">Poor</option>
                  </select>
                </div>
                
                {/* Manufacturer Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Fabricant</label>
                  <select
                    value={filters.manufacturer}
                    onChange={(e) => setFilters({...filters, manufacturer: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Tous les fabricants</option>
                    {getUniqueValues('manufacturer').map(manufacturer => (
                      <option key={manufacturer} value={manufacturer}>{manufacturer}</option>
                    ))}
                  </select>
                </div>
                
                <button
                  onClick={() => setFilters({
                    league: '', team: '', season: '', size: '', condition: '', manufacturer: ''
                  })}
                  className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                >
                  Effacer les filtres
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Tabs */}
            <div className="bg-gray-900 rounded-lg border border-gray-700 mb-6">
              <div className="flex border-b border-gray-700">
                <button
                  onClick={() => setActiveTab('jerseys')}
                  className={`px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === 'jerseys'
                      ? 'border-b-2 border-white text-white bg-gray-800'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  👕 Maillots ({jerseys.length})
                </button>
                <button
                  onClick={() => setActiveTab('users')}
                  className={`px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === 'users'
                      ? 'border-b-2 border-white text-white bg-gray-800'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  👥 Utilisateurs
                </button>
              </div>
            </div>

            {activeTab === 'jerseys' ? (
              <>
                {/* View Controls */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
              <div className="flex items-center space-x-4">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="newest">Plus récents</option>
                  <option value="oldest">Plus anciens</option>
                  <option value="team">Par équipe</option>
                  <option value="season">Par saison</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded text-sm ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
                >
                  📋
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded text-sm ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
                >
                  🎯
                </button>
              </div>
            </div>

            {/* Results */}
            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-400">Chargement des maillots...</div>
              </div>
            ) : (
              <div>
                {viewMode === 'list' ? (
                  <div className="space-y-2">
                    {getFilteredJerseys().map((jersey) => (
                      <DarkJerseyCard 
                        key={jersey.id} 
                        jersey={jersey} 
                        isListView={true}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {getFilteredJerseys().map((jersey) => (
                      <DarkJerseyCard 
                        key={jersey.id} 
                        jersey={jersey} 
                        isListView={false}
                      />
                    ))}
                  </div>
                )}
                
                {getFilteredJerseys().length === 0 && (
                  <div className="text-center py-12 bg-gray-900 rounded-lg border border-gray-700">
                    <div className="text-gray-400">Aucun maillot trouvé.</div>
                    <button
                      onClick={() => {
                        setFilters({
                          league: '', team: '', season: '', size: '', condition: '', manufacturer: ''
                        });
                        setSearchQuery('');
                      }}
                      className="mt-4 text-blue-400 hover:text-blue-300 font-medium"
                    >
                      Effacer les filtres
                    </button>
                  </div>
                )}
              </div>
            )}
            </>
            ) : (
              /* Users Tab */
              <div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Rechercher des utilisateurs
                  </label>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleUserSearch}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
                    placeholder="Nom d'utilisateur ou email..."
                  />
                </div>

                {searchLoading && (
                  <div className="text-center py-8">
                    <div className="text-gray-400">Recherche en cours...</div>
                  </div>
                )}

                {searchResults.length > 0 && (
                  <div className="space-y-4">
                    {searchResults.map((user) => (
                      <div key={user.id} className="bg-gray-800 rounded-lg border border-gray-600 p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                              {user.picture ? (
                                <img src={user.picture} alt={user.name} className="w-12 h-12 rounded-full" />
                              ) : (
                                <span className="text-gray-300 text-lg">👤</span>
                              )}
                            </div>
                            <div>
                              <h3 className="text-white font-medium">{user.name}</h3>
                              <p className="text-gray-400 text-sm">{user.email}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => onViewUserProfile && onViewUserProfile(user.id)}
                            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                          >
                            👤 Voir profil
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {searchQuery.length >= 2 && searchResults.length === 0 && !searchLoading && (
                  <div className="text-center py-8">
                    <div className="text-gray-400">Aucun utilisateur trouvé</div>
                  </div>
                )}

                {searchQuery.length < 2 && (
                  <div className="text-center py-12 bg-gray-900 rounded-lg border border-gray-700">
                    <div className="text-gray-400 mb-2">🔍 Recherche d'utilisateurs</div>
                    <p className="text-gray-500 text-sm">
                      Tapez au moins 2 caractères pour rechercher des utilisateurs de TopKit
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Nouveau composant : Paramètres Utilisateur Avancés  
const AdvancedSettingsPage = () => {
  const { user } = useAuth();
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  
  const [activeTab, setActiveTab] = useState('profile');  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // États pour les différentes sections
  const [profileData, setProfileData] = useState({
    display_name: '',
    bio: '',
    location: '',
    languages: [],
    website: '',
    social_links: {}
  });

  const [sellerSettings, setSellerSettings] = useState({
    is_seller: false,
    business_name: '',
    address: '',
    phone: '',
    return_policy: '',
    shipping_policy: '',
    payment_methods: [],
    processing_time_days: 3,
    return_days: 14,
    seller_notes: ''
  });

  const [buyerSettings, setBuyerSettings] = useState({
    max_budget_per_item: null,
    notify_new_matches: true,
    notify_price_drops: true,
    notify_watchlist_available: true
  });

  const [collectionSettings, setCollectionSettings] = useState({
    visibility: 'public',
    show_statistics: true,
    show_estimated_value: false,
    show_acquisition_dates: true,
    notify_similar_items: true
  });

  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: 'public',
    show_last_seen: true,
    allow_private_messages: true,
    show_location: true,
    show_join_date: true
  });

  const [userRatings, setUserRatings] = useState({
    seller_ratings: [],
    buyer_ratings: []
  });

  // Chargement des données au montage
  useEffect(() => {
    fetchAdvancedProfile();
  }, []);

  const fetchAdvancedProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/profile/advanced`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = response.data;
      
      // Mise à jour des états avec les données récupérées
      setProfileData({
        display_name: data.display_name || '',
        bio: data.bio || '',
        location: data.location || '',
        languages: data.languages || [],
        website: data.website || '',
        social_links: data.social_links || {}
      });

      setSellerSettings(data.seller_settings || {
        is_seller: false,
        business_name: '',
        address: '',
        phone: '',
        return_policy: '',
        shipping_policy: '',
        payment_methods: [],
        processing_time_days: 3,
        return_days: 14,
        seller_notes: ''
      });

      setBuyerSettings(data.buyer_settings || {
        max_budget_per_item: null,
        notify_new_matches: true,
        notify_price_drops: true,
        notify_watchlist_available: true
      });

      setCollectionSettings(data.collection_settings || {
        visibility: 'public',
        show_statistics: true,
        show_estimated_value: false,
        show_acquisition_dates: true,
        notify_similar_items: true
      });

      setPrivacySettings(data.privacy_settings || {
        profile_visibility: 'public',
        show_last_seen: true,
        allow_private_messages: true,
        show_location: true,
        show_join_date: true
      });

      setLoading(false);
    } catch (error) {
      console.error('Erreur lors de la récupération du profil:', error);
      setLoading(false);
    }
  };

  const saveSettings = async (section, data) => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/api/profile/${section}`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setMessage('Paramètres sauvegardés avec succès !');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      setMessage('Erreur lors de la sauvegarde');
      setTimeout(() => setMessage(''), 3000);
    }
    setSaving(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Chargement des paramètres...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Paramètres Avancés</h1>
          <p className="text-gray-400">Gérez votre profil, vos préférences et vos paramètres de confidentialité</p>
        </div>

        {/* Message de feedback */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('succès') ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'
          }`}>
            {message}
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Navigation des onglets */}
          <div className="lg:w-64 flex-shrink-0">
            <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
              <nav className="space-y-2">
                {[
                  { id: 'profile', label: 'Profil', icon: '👤' },
                  { id: 'seller-settings', label: 'Vendeur', icon: '🏪' },
                  { id: 'buyer-settings', label: 'Acheteur', icon: '🛒' },
                  { id: 'collection-settings', label: 'Collection', icon: '📚' },
                  { id: 'privacy-settings', label: 'Confidentialité', icon: '🔒' },
                  { id: 'ratings', label: 'Évaluations', icon: '⭐' }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      activeTab === tab.id 
                        ? 'bg-blue-600 text-white' 
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <span className="mr-3">{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Contenu des onglets */}
          <div className="flex-1">
            <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
              
              {/* Onglet Profil */}
              {activeTab === 'profile' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Informations du Profil</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Nom d'affichage
                      </label>
                      <input
                        type="text"
                        value={profileData.display_name}
                        onChange={(e) => setProfileData({...profileData, display_name: e.target.value})}
                        className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                        placeholder="Votre nom d'affichage"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Biographie
                      </label>
                      <textarea
                        value={profileData.bio}
                        onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                        rows={4}
                        className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                        placeholder="Parlez-nous de vous et de votre passion pour les maillots..."
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Localisation
                        </label>
                        <input
                          type="text"
                          value={profileData.location}
                          onChange={(e) => setProfileData({...profileData, location: e.target.value})}
                          className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                          placeholder="Paris, France"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Site web
                        </label>
                        <input
                          type="url"
                          value={profileData.website}
                          onChange={(e) => setProfileData({...profileData, website: e.target.value})}
                          className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                          placeholder="https://monsite.com"
                        />
                      </div>
                    </div>

                    <button
                      onClick={() => saveSettings('advanced', profileData)}
                      disabled={saving}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      {saving ? 'Sauvegarde...' : 'Sauvegarder le profil'}
                    </button>
                  </div>
                </div>
              )}

              {/* Onglet Paramètres Vendeur */}
              {activeTab === 'seller-settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Paramètres Vendeur</h2>
                  <div className="space-y-6">
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        id="is_seller"
                        checked={sellerSettings.is_seller}
                        onChange={(e) => setSellerSettings({...sellerSettings, is_seller: e.target.checked})}
                        className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <label htmlFor="is_seller" className="text-white font-medium">
                        Je souhaite vendre des maillots sur TopKit
                      </label>
                    </div>

                    {sellerSettings.is_seller && (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                              Nom de l'entreprise (optionnel)
                            </label>
                            <input
                              type="text"
                              value={sellerSettings.business_name}
                              onChange={(e) => setSellerSettings({...sellerSettings, business_name: e.target.value})}
                              className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                              placeholder="Mon Shop Maillots"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                              Téléphone
                            </label>
                            <input
                              type="tel"
                              value={sellerSettings.phone}
                              onChange={(e) => setSellerSettings({...sellerSettings, phone: e.target.value})}
                              className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                              placeholder="+33 1 23 45 67 89"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Adresse complète
                          </label>
                          <textarea
                            value={sellerSettings.address}
                            onChange={(e) => setSellerSettings({...sellerSettings, address: e.target.value})}
                            rows={3}
                            className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                            placeholder="123 Rue du Football, 75001 Paris, France"
                          />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                              Délai de traitement (jours)
                            </label>
                            <input
                              type="number"
                              value={sellerSettings.processing_time_days}
                              onChange={(e) => setSellerSettings({...sellerSettings, processing_time_days: parseInt(e.target.value)})}
                              className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                              min="1"
                              max="30"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                              Période de retour (jours)
                            </label>
                            <input
                              type="number"
                              value={sellerSettings.return_days}
                              onChange={(e) => setSellerSettings({...sellerSettings, return_days: parseInt(e.target.value)})}
                              className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                              min="0"
                              max="365"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Politique de retour
                          </label>
                          <textarea
                            value={sellerSettings.return_policy}
                            onChange={(e) => setSellerSettings({...sellerSettings, return_policy: e.target.value})}
                            rows={4}
                            className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                            placeholder="Décrivez votre politique de retour..."
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Notes pour les acheteurs
                          </label>
                          <textarea
                            value={sellerSettings.seller_notes}
                            onChange={(e) => setSellerSettings({...sellerSettings, seller_notes: e.target.value})}
                            rows={3}
                            className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                            placeholder="Informations importantes pour vos acheteurs..."
                          />
                        </div>

                        {/* Shipping Settings */}
                        <div className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                          <h3 className="text-lg font-semibold text-white mb-4">📦 Frais d'envoi</h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-300 mb-2">
                                France métropolitaine (€)
                              </label>
                              <input
                                type="number"
                                value={sellerSettings.shipping_cost_france || ''}
                                onChange={(e) => setSellerSettings({...sellerSettings, shipping_cost_france: parseFloat(e.target.value) || 0})}
                                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-blue-500"
                                placeholder="5.00"
                                step="0.50"
                                min="0"
                              />
                            </div>
                            
                            <div>
                              <label className="block text-sm font-medium text-gray-300 mb-2">
                                Europe (€)
                              </label>
                              <input
                                type="number"
                                value={sellerSettings.shipping_cost_europe || ''}
                                onChange={(e) => setSellerSettings({...sellerSettings, shipping_cost_europe: parseFloat(e.target.value) || 0})}
                                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-blue-500"
                                placeholder="8.00"
                                step="0.50"
                                min="0"
                              />
                            </div>
                            
                            <div>
                              <label className="block text-sm font-medium text-gray-300 mb-2">
                                International (€)
                              </label>
                              <input
                                type="number"
                                value={sellerSettings.shipping_cost_international || ''}
                                onChange={(e) => setSellerSettings({...sellerSettings, shipping_cost_international: parseFloat(e.target.value) || 0})}
                                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-blue-500"
                                placeholder="15.00"
                                step="0.50"
                                min="0"
                              />
                            </div>
                            
                            <div>
                              <label className="block text-sm font-medium text-gray-300 mb-2">
                                Envoi gratuit à partir de (€)
                              </label>
                              <input
                                type="number"
                                value={sellerSettings.free_shipping_threshold || ''}
                                onChange={(e) => setSellerSettings({...sellerSettings, free_shipping_threshold: parseFloat(e.target.value) || 0})}
                                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-blue-500"
                                placeholder="50.00"
                                step="5.00"
                                min="0"
                              />
                            </div>
                          </div>

                          <div className="mt-4">
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                              Transporteurs acceptés
                            </label>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                              {['La Poste', 'Chronopost', 'DHL', 'UPS', 'FedEx', 'Mondial Relay'].map((carrier) => (
                                <div key={carrier} className="flex items-center space-x-2">
                                  <input
                                    type="checkbox"
                                    id={`carrier_${carrier.replace(' ', '_')}`}
                                    checked={(sellerSettings.accepted_carriers || []).includes(carrier)}
                                    onChange={(e) => {
                                      const carriers = sellerSettings.accepted_carriers || [];
                                      if (e.target.checked) {
                                        setSellerSettings({...sellerSettings, accepted_carriers: [...carriers, carrier]});
                                      } else {
                                        setSellerSettings({...sellerSettings, accepted_carriers: carriers.filter(c => c !== carrier)});
                                      }
                                    }}
                                    className="w-4 h-4 text-blue-600 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                                  />
                                  <label htmlFor={`carrier_${carrier.replace(' ', '_')}`} className="text-sm text-gray-300">
                                    {carrier}
                                  </label>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </>
                    )}

                    <button
                      onClick={() => saveSettings('seller-settings', sellerSettings)}
                      disabled={saving}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      {saving ? 'Sauvegarde...' : 'Sauvegarder les paramètres vendeur'}
                    </button>
                  </div>
                </div>
              )}

              {/* Onglet Paramètres Acheteur */}
              {activeTab === 'buyer-settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Paramètres Acheteur</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Budget maximum par article (€)
                      </label>
                      <input
                        type="number"
                        value={buyerSettings.max_budget_per_item || ''}
                        onChange={(e) => setBuyerSettings({...buyerSettings, max_budget_per_item: e.target.value ? parseInt(e.target.value) : null})}
                        className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                        placeholder="500"
                        min="0"
                      />
                      <p className="text-gray-500 text-sm mt-1">Laissez vide pour aucune limite</p>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-white">Notifications</h3>
                      
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="notify_new_matches"
                            checked={buyerSettings.notify_new_matches}
                            onChange={(e) => setBuyerSettings({...buyerSettings, notify_new_matches: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="notify_new_matches" className="text-white">
                            Nouveaux maillots correspondant à mes critères
                          </label>
                        </div>

                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="notify_price_drops"
                            checked={buyerSettings.notify_price_drops}
                            onChange={(e) => setBuyerSettings({...buyerSettings, notify_price_drops: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="notify_price_drops" className="text-white">
                            Baisses de prix sur mes maillots favoris
                          </label>
                        </div>

                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="notify_watchlist_available"
                            checked={buyerSettings.notify_watchlist_available}
                            onChange={(e) => setBuyerSettings({...buyerSettings, notify_watchlist_available: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="notify_watchlist_available" className="text-white">
                            Maillots de ma wishlist disponibles à la vente
                          </label>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => saveSettings('buyer-settings', buyerSettings)}
                      disabled={saving}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      {saving ? 'Sauvegarde...' : 'Sauvegarder les paramètres acheteur'}
                    </button>
                  </div>
                </div>
              )}

              {/* Onglet Paramètres de Collection */}
              {activeTab === 'collection-settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Paramètres de Collection</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Visibilité de la collection
                      </label>
                      <select
                        value={collectionSettings.visibility}
                        onChange={(e) => setCollectionSettings({...collectionSettings, visibility: e.target.value})}
                        className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="public">🌍 Publique - Tout le monde peut voir</option>
                        <option value="private">🔒 Privée - Seulement moi</option>
                        <option value="friends">👥 Amis seulement</option>
                      </select>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-white">Affichage</h3>
                      
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="show_statistics"
                            checked={collectionSettings.show_statistics}
                            onChange={(e) => setCollectionSettings({...collectionSettings, show_statistics: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="show_statistics" className="text-white">
                            Afficher les statistiques de ma collection
                          </label>
                        </div>

                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="show_estimated_value"
                            checked={collectionSettings.show_estimated_value}
                            onChange={(e) => setCollectionSettings({...collectionSettings, show_estimated_value: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="show_estimated_value" className="text-white">
                            Afficher la valeur estimée de ma collection
                          </label>
                        </div>

                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="show_acquisition_dates"
                            checked={collectionSettings.show_acquisition_dates}
                            onChange={(e) => setCollectionSettings({...collectionSettings, show_acquisition_dates: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="show_acquisition_dates" className="text-white">
                            Afficher les dates d'acquisition
                          </label>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-white">Notifications</h3>
                      
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="notify_similar_items"
                            checked={collectionSettings.notify_similar_items}
                            onChange={(e) => setCollectionSettings({...collectionSettings, notify_similar_items: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="notify_similar_items" className="text-white">
                            Nouveaux maillots similaires à ma collection
                          </label>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => saveSettings('collection-settings', collectionSettings)}
                      disabled={saving}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      {saving ? 'Sauvegarde...' : 'Sauvegarder les paramètres de collection'}
                    </button>
                  </div>
                </div>
              )}

              {/* Onglet Paramètres de Confidentialité */}
              {activeTab === 'privacy-settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Paramètres de Confidentialité</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Visibilité du profil
                      </label>
                      <select
                        value={privacySettings.profile_visibility}
                        onChange={(e) => setPrivacySettings({...privacySettings, profile_visibility: e.target.value})}
                        className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="public">🌍 Public - Visible par tous</option>
                        <option value="private">🔒 Privé - Seulement moi</option>
                      </select>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-white">Informations visibles</h3>
                      
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="show_location"
                            checked={privacySettings.show_location}
                            onChange={(e) => setPrivacySettings({...privacySettings, show_location: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="show_location" className="text-white">
                            Afficher ma localisation
                          </label>
                        </div>

                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="show_join_date"
                            checked={privacySettings.show_join_date}
                            onChange={(e) => setPrivacySettings({...privacySettings, show_join_date: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="show_join_date" className="text-white">
                            Afficher ma date d'inscription
                          </label>
                        </div>

                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="show_last_seen"
                            checked={privacySettings.show_last_seen}
                            onChange={(e) => setPrivacySettings({...privacySettings, show_last_seen: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="show_last_seen" className="text-white">
                            Afficher ma dernière connexion
                          </label>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-white">Communications</h3>
                      
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id="allow_private_messages"
                            checked={privacySettings.allow_private_messages}
                            onChange={(e) => setPrivacySettings({...privacySettings, allow_private_messages: e.target.checked})}
                            className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <label htmlFor="allow_private_messages" className="text-white">
                            Autoriser les messages privés
                          </label>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => saveSettings('privacy-settings', privacySettings)}
                      disabled={saving}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      {saving ? 'Sauvegarde...' : 'Sauvegarder les paramètres de confidentialité'}
                    </button>
                  </div>
                </div>
              )}

              {/* Onglet Évaluations */}
              {activeTab === 'ratings' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Mes Évaluations</h2>
                  <div className="space-y-6">
                    <div className="bg-gray-800 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-white mb-4">Statistiques</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-green-400 mb-2">
                            N/A
                          </div>
                          <div className="text-gray-400">Note Vendeur</div>
                          <div className="text-sm text-gray-500">(0 évaluations)</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-blue-400 mb-2">
                            N/A
                          </div>
                          <div className="text-gray-400">Note Acheteur</div>
                          <div className="text-sm text-gray-500">(0 évaluations)</div>
                        </div>
                      </div>
                    </div>

                    <div className="text-center py-12">
                      <div className="text-gray-400 mb-4">
                        <span className="text-6xl">⭐</span>
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">Aucune évaluation pour le moment</h3>
                      <p className="text-gray-400">
                        Vos évaluations apparaîtront ici après vos premières transactions
                      </p>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Friends Page Component
const FriendsPage = () => {
  const { user } = useAuth();
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  
  const [activeTab, setActiveTab] = useState('friends');
  const [loading, setLoading] = useState(true);
  const [friends, setFriends] = useState([]);
  const [pendingRequests, setPendingRequests] = useState({ received: [], sent: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    fetchFriendsData();
  }, [user]);

  const fetchFriendsData = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/friends`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFriends(data.friends || []);
        setPendingRequests(data.pending_requests || { received: [], sent: [] });
      }
    } catch (error) {
      console.error('Error fetching friends:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchUsers = async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    try {
      setSearchLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/users/search?query=${encodeURIComponent(query)}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const users = await response.json();
        setSearchResults(users);
      }
    } catch (error) {
      console.error('Error searching users:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const sendFriendRequest = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/friends/request`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
      });
      
      if (response.ok) {
        alert('Demande d\'ami envoyée !');
        fetchFriendsData(); // Refresh data
        setSearchQuery('');
        setSearchResults([]);
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors de l\'envoi de la demande');
      }
    } catch (error) {
      console.error('Error sending friend request:', error);
      alert('Erreur lors de l\'envoi de la demande');
    }
  };

  const respondToFriendRequest = async (requestId, accept) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/friends/respond`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ request_id: requestId, accept })
      });
      
      if (response.ok) {
        alert(accept ? 'Demande d\'ami acceptée !' : 'Demande d\'ami refusée');
        fetchFriendsData(); // Refresh data
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors de la réponse');
      }
    } catch (error) {
      console.error('Error responding to friend request:', error);
      alert('Erreur lors de la réponse');
    }
  };

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    searchUsers(query);
  };

  const startConversation = async (friendId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/conversations/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipient_id: friendId,
          message: "👋 Salut ! Comment ça va ?"
        })
      });
      
      if (response.ok) {
        // Switch to messages page
        // We need to access the setCurrentView from parent component
        alert('Conversation démarrée ! Rendez-vous dans la section Messages.');
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors du démarrage de la conversation');
      }
    } catch (error) {
      console.error('Error starting conversation:', error);
      alert('Erreur lors du démarrage de la conversation');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">Chargement...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">👥 Mes Amis</h1>
        
        {/* Tabs */}
        <div className="bg-gray-900 rounded-lg border border-gray-700 mb-6">
          <div className="flex flex-wrap border-b border-gray-700">
            {[
              { id: 'friends', label: '👥 Amis', count: friends.length },
              { id: 'received', label: '📨 Reçues', count: pendingRequests.received.length },
              { id: 'sent', label: '📤 Envoyées', count: pendingRequests.sent.length },
              { id: 'search', label: '🔍 Rechercher' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-b-2 border-white text-white bg-gray-800'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                {tab.label}
                {tab.count !== undefined && (
                  <span className="ml-2 px-2 py-1 bg-blue-600 text-white text-xs rounded-full">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Friends List */}
            {activeTab === 'friends' && (
              <div>
                {friends.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg mb-4">Aucun ami pour le moment</div>
                    <p className="text-gray-500">Recherchez des utilisateurs pour commencer à construire votre réseau !</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {friends.map((friend) => (
                      <div key={friend.friend_id} className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                            {friend.picture ? (
                              <img src={friend.picture} alt={friend.name} className="w-12 h-12 rounded-full" />
                            ) : (
                              <span className="text-gray-300 text-lg">👤</span>
                            )}
                          </div>
                          <div className="flex-1">
                            <h3 className="text-white font-medium">{friend.name}</h3>
                            <p className="text-gray-400 text-sm">{friend.email}</p>
                            {friend.friends_since && (
                              <p className="text-gray-500 text-xs">
                                Amis depuis {new Date(friend.friends_since).toLocaleDateString('fr-FR')}
                              </p>
                            )}
                          </div>
                          <button 
                            onClick={() => startConversation(friend.friend_id)}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            💬 Message
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Pending Requests - Received */}
            {activeTab === 'received' && (
              <div>
                {pendingRequests.received.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg">Aucune demande reçue</div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {pendingRequests.received.map((request) => (
                      <div key={request.request_id} className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                              {request.picture ? (
                                <img src={request.picture} alt={request.name} className="w-12 h-12 rounded-full" />
                              ) : (
                                <span className="text-gray-300 text-lg">👤</span>
                              )}
                            </div>
                            <div>
                              <h3 className="text-white font-medium">{request.name}</h3>
                              <p className="text-gray-400 text-sm">{request.email}</p>
                              <p className="text-gray-500 text-xs">
                                Demande envoyée le {new Date(request.requested_at).toLocaleDateString('fr-FR')}
                              </p>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => respondToFriendRequest(request.request_id, true)}
                              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                            >
                              ✓ Accepter
                            </button>
                            <button
                              onClick={() => respondToFriendRequest(request.request_id, false)}
                              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                            >
                              ✗ Refuser
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Pending Requests - Sent */}
            {activeTab === 'sent' && (
              <div>
                {pendingRequests.sent.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg">Aucune demande envoyée</div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {pendingRequests.sent.map((request) => (
                      <div key={request.request_id} className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                            {request.picture ? (
                              <img src={request.picture} alt={request.name} className="w-12 h-12 rounded-full" />
                            ) : (
                              <span className="text-gray-300 text-lg">👤</span>
                            )}
                          </div>
                          <div className="flex-1">
                            <h3 className="text-white font-medium">{request.name}</h3>
                            <p className="text-gray-400 text-sm">{request.email}</p>
                            <p className="text-gray-500 text-xs">
                              En attente depuis le {new Date(request.requested_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                          <span className="bg-yellow-600 text-white px-3 py-1 rounded text-sm">
                            ⏳ En attente
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Search Users */}
            {activeTab === 'search' && (
              <div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Rechercher des utilisateurs
                  </label>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
                    placeholder="Nom d'utilisateur ou email..."
                  />
                </div>

                {searchLoading && (
                  <div className="text-center py-8">
                    <div className="text-gray-400">Recherche en cours...</div>
                  </div>
                )}

                {searchResults.length > 0 && (
                  <div className="space-y-4">
                    {searchResults.map((user) => (
                      <div key={user.id} className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                              {user.picture ? (
                                <img src={user.picture} alt={user.name} className="w-12 h-12 rounded-full" />
                              ) : (
                                <span className="text-gray-300 text-lg">👤</span>
                              )}
                            </div>
                            <div>
                              <h3 className="text-white font-medium">{user.name}</h3>
                              <p className="text-gray-400 text-sm">{user.email}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => sendFriendRequest(user.id)}
                            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                          >
                            👥 Ajouter
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {searchQuery.length >= 2 && searchResults.length === 0 && !searchLoading && (
                  <div className="text-center py-8">
                    <div className="text-gray-400">Aucun utilisateur trouvé</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Messages Page Component
const MessagesPage = () => {
  const { user } = useAuth();
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    if (user) {
      fetchConversations();
      // Initialize WebSocket connection for real-time messaging
      initializeWebSocket();
    }
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [user]);

  const initializeWebSocket = () => {
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = API.replace('http://', '').replace('https://', '');
      const wsUrl = `${wsProtocol}//${wsHost}/ws/${user.id}`;
      
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        console.log('WebSocket connected for real-time messaging');
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'new_message') {
          // Add new message to current conversation if it's the active one
          if (selectedConversation && data.message.conversation_id === selectedConversation.conversation_id) {
            setMessages(prev => [...prev, {
              ...data.message,
              sent_by_me: false
            }]);
          }
          // Refresh conversations list to update last message
          fetchConversations();
        }
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        // Reconnect after 3 seconds
        setTimeout(() => {
          if (user) {
            initializeWebSocket();
          }
        }, 3000);
      };
      
      setWs(websocket);
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  };

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/conversations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      setMessagesLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/conversations/${conversationId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setMessagesLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/conversations/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conversation_id: selectedConversation.conversation_id,
          message: newMessage.trim()
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Add message to current conversation
        const newMsg = {
          id: data.message_id,
          message: newMessage.trim(),
          created_at: new Date().toISOString(),
          sent_by_me: true
        };
        
        setMessages(prev => [...prev, newMsg]);
        setNewMessage('');
        
        // Refresh conversations to update last message
        fetchConversations();
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    fetchMessages(conversation.conversation_id);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">Chargement...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="max-w-7xl mx-auto p-4">
        <h1 className="text-3xl font-bold mb-8">💬 Messages</h1>
        
        <div className="bg-gray-900 rounded-lg border border-gray-700 h-[calc(100vh-200px)] flex">
          {/* Conversations List */}
          <div className="w-1/3 border-r border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h2 className="text-lg font-semibold">Conversations</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto">
              {conversations.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-400">Aucune conversation</div>
                  <p className="text-gray-500 text-sm mt-2">
                    Commencez par ajouter des amis pour pouvoir leur envoyer des messages !
                  </p>
                </div>
              ) : (
                conversations.map((conversation) => (
                  <div
                    key={conversation.conversation_id}
                    onClick={() => selectConversation(conversation)}
                    className={`p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800 transition-colors ${
                      selectedConversation?.conversation_id === conversation.conversation_id ? 'bg-gray-800' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                        {conversation.other_user.picture ? (
                          <img 
                            src={conversation.other_user.picture} 
                            alt={conversation.other_user.name} 
                            className="w-12 h-12 rounded-full" 
                          />
                        ) : (
                          <span className="text-gray-300 text-lg">👤</span>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-white font-medium truncate">
                          {conversation.other_user.name}
                        </h3>
                        {conversation.last_message && (
                          <p className="text-gray-400 text-sm truncate">
                            {conversation.last_message.sent_by_me ? 'Vous: ' : ''}
                            {conversation.last_message.message}
                          </p>
                        )}
                        {conversation.last_message_at && (
                          <p className="text-gray-500 text-xs">
                            {new Date(conversation.last_message_at).toLocaleString('fr-FR')}
                          </p>
                        )}
                      </div>
                      {conversation.last_message && !conversation.last_message.read && !conversation.last_message.sent_by_me && (
                        <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 flex flex-col">
            {selectedConversation ? (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-700 bg-gray-800">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                      {selectedConversation.other_user.picture ? (
                        <img 
                          src={selectedConversation.other_user.picture} 
                          alt={selectedConversation.other_user.name} 
                          className="w-10 h-10 rounded-full" 
                        />
                      ) : (
                        <span className="text-gray-300">👤</span>
                      )}
                    </div>
                    <div>
                      <h3 className="text-white font-medium">{selectedConversation.other_user.name}</h3>
                      <p className="text-gray-400 text-sm">En ligne</p>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messagesLoading ? (
                    <div className="text-center py-8">
                      <div className="text-gray-400">Chargement des messages...</div>
                    </div>
                  ) : messages.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="text-gray-400">Aucun message encore</div>
                      <p className="text-gray-500 text-sm mt-2">Commencez la conversation !</p>
                    </div>
                  ) : (
                    messages.map((message, index) => (
                      <div
                        key={message.id || index}
                        className={`flex ${message.sent_by_me ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[70%] p-3 rounded-lg ${
                            message.sent_by_me
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-700 text-white'
                          }`}
                        >
                          <p className="text-sm">{message.message}</p>
                          <p className={`text-xs mt-1 ${
                            message.sent_by_me ? 'text-blue-100' : 'text-gray-400'
                          }`}>
                            {new Date(message.created_at).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Message Input */}
                <div className="p-4 border-t border-gray-700">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
                      placeholder="Tapez votre message..."
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim()}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Envoyer
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-gray-400 text-lg mb-2">💬 Sélectionnez une conversation</div>
                  <p className="text-gray-500">
                    Choisissez une conversation dans la liste pour commencer à échanger !
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// User Profile Page Component
const UserProfilePage = ({ selectedUserId, onBack }) => {
  const { user } = useAuth();
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  
  const [profileData, setProfileData] = useState(null);
  const [userJerseys, setUserJerseys] = useState([]);
  const [userCollections, setUserCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isFriend, setIsFriend] = useState(false);
  const [friendRequestSent, setFriendRequestSent] = useState(false);

  useEffect(() => {
    if (selectedUserId) {
      fetchUserProfile();
      fetchUserJerseys();
      fetchUserCollections();
      checkFriendStatus();
    }
  }, [selectedUserId]);

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/users/${selectedUserId}/profile`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      
      if (response.ok) {
        const data = await response.json();
        setProfileData(data);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchUserJerseys = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/users/${selectedUserId}/jerseys`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserJerseys(data);
      }
    } catch (error) {
      console.error('Error fetching user jerseys:', error);
    }
  };

  const fetchUserCollections = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/users/${selectedUserId}/collections`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      
      if (response.ok) {
        const data = await response.json();
        // Ensure data is always an array
        setUserCollections(Array.isArray(data) ? data : []);
      } else {
        setUserCollections([]);
      }
    } catch (error) {
      console.error('Error fetching user collections:', error);
      setUserCollections([]);
    } finally {
      setLoading(false);
    }
  };

  const checkFriendStatus = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/friends`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        const isAlreadyFriend = data.friends.some(friend => friend.friend_id === selectedUserId);
        const hasSentRequest = data.pending_requests.sent.some(req => req.addressee_id === selectedUserId);
        
        setIsFriend(isAlreadyFriend);
        setFriendRequestSent(hasSentRequest);
      }
    } catch (error) {
      console.error('Error checking friend status:', error);
    }
  };

  const sendFriendRequest = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/friends/request`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: selectedUserId })
      });
      
      if (response.ok) {
        setFriendRequestSent(true);
        alert('Demande d\'ami envoyée !');
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors de l\'envoi de la demande');
      }
    } catch (error) {
      console.error('Error sending friend request:', error);
      alert('Erreur lors de l\'envoi de la demande');
    }
  };

  const startConversation = async () => {
    if (!user || !isFriend) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/conversations/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipient_id: selectedUserId,
          message: "👋 Salut ! Comment ça va ?"
        })
      });
      
      if (response.ok) {
        alert('Conversation démarrée ! Rendez-vous dans la section Messages.');
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors du démarrage de la conversation');
      }
    } catch (error) {
      console.error('Error starting conversation:', error);
      alert('Erreur lors du démarrage de la conversation');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">Chargement du profil...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="min-h-screen bg-black text-white p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="text-red-400 text-lg">Profil introuvable</div>
            <button 
              onClick={onBack}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Retour
            </button>
          </div>
        </div>
      </div>
    );
  }

  const isOwnProfile = user && user.id === selectedUserId;

  return (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header with Back Button */}
        <div className="mb-6">
          <button 
            onClick={onBack}
            className="text-blue-400 hover:text-blue-300 flex items-center space-x-2"
          >
            <span>←</span>
            <span>Retour</span>
          </button>
        </div>

        {/* Profile Header */}
        <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex items-center space-x-6 mb-4 md:mb-0">
              <div className="w-20 h-20 bg-gray-700 rounded-full flex items-center justify-center">
                {profileData.picture ? (
                  <img src={profileData.picture} alt={profileData.display_name} className="w-20 h-20 rounded-full" />
                ) : (
                  <span className="text-gray-300 text-3xl">👤</span>
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold">{profileData.display_name || profileData.name}</h1>
                <p className="text-gray-400">{profileData.email}</p>
                {profileData.location && (
                  <p className="text-gray-500 flex items-center mt-2">
                    <span className="mr-2">📍</span>
                    {profileData.location}
                  </p>
                )}
                {profileData.bio && (
                  <p className="text-gray-300 mt-2 max-w-md">{profileData.bio}</p>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            {!isOwnProfile && user && (
              <div className="flex space-x-3">
                {isFriend ? (
                  <button
                    onClick={startConversation}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                  >
                    <span>💬</span>
                    <span>Message</span>
                  </button>
                ) : friendRequestSent ? (
                  <button
                    disabled
                    className="bg-yellow-600 text-white px-4 py-2 rounded-lg opacity-75 cursor-not-allowed"
                  >
                    ⏳ Demande envoyée
                  </button>
                ) : (
                  <button
                    onClick={sendFriendRequest}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
                  >
                    <span>👥</span>
                    <span>Ajouter ami</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-700">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">{userJerseys.length}</div>
              <div className="text-gray-400 text-sm">Maillots soumis</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{Array.isArray(userCollections) ? userCollections.filter(c => c.collection_type === 'owned').length : 0}</div>
              <div className="text-gray-400 text-sm">Possédés</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">{Array.isArray(userCollections) ? userCollections.filter(c => c.collection_type === 'wanted').length : 0}</div>
              <div className="text-gray-400 text-sm">Recherchés</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">
                {profileData.stats?.avg_seller_rating ? profileData.stats.avg_seller_rating.toFixed(1) : '-'}
              </div>
              <div className="text-gray-400 text-sm">Note vendeur</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-900 rounded-lg border border-gray-700">
          <div className="flex flex-wrap border-b border-gray-700">
            {[
              { id: 'overview', label: '📊 Vue d\'ensemble' },
              { id: 'jerseys', label: '👕 Maillots soumis', count: userJerseys.length },
              { id: 'collection', label: '📚 Collection', count: Array.isArray(userCollections) ? userCollections.length : 0 },
              { id: 'badges', label: '🏆 Badges' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-b-2 border-white text-white bg-gray-800'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                {tab.label}
                {tab.count !== undefined && (
                  <span className="ml-2 px-2 py-1 bg-blue-600 text-white text-xs rounded-full">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Recent Activity */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Activité récente</h3>
                  <div className="bg-gray-800 rounded-lg p-4">
                    <p className="text-gray-400">Aucune activité récente disponible</p>
                  </div>
                </div>

                {/* Seller Info */}
                {profileData.seller_info && (
                  <div>
                    <h3 className="text-xl font-semibold mb-4">🏪 Informations vendeur</h3>
                    <div className="bg-gray-800 rounded-lg p-4 space-y-3">
                      {profileData.seller_info.business_name && (
                        <div>
                          <span className="text-gray-400">Nom commercial: </span>
                          <span className="text-white">{profileData.seller_info.business_name}</span>
                        </div>
                      )}
                      <div>
                        <span className="text-gray-400">Délai de traitement: </span>
                        <span className="text-white">{profileData.seller_info.processing_time_days} jours</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Retours acceptés: </span>
                        <span className="text-white">{profileData.seller_info.return_days} jours</span>
                      </div>
                      {profileData.seller_info.payment_methods && profileData.seller_info.payment_methods.length > 0 && (
                        <div>
                          <span className="text-gray-400">Méthodes de paiement: </span>
                          <span className="text-white">{profileData.seller_info.payment_methods.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Jerseys Tab */}
            {activeTab === 'jerseys' && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Maillots soumis par {profileData.display_name || profileData.name}</h3>
                {userJerseys.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg">Aucun maillot soumis</div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {userJerseys.map((jersey) => (
                      <div key={jersey.id} className="bg-gray-800 rounded-lg border border-gray-600 p-4">
                        <div className="aspect-square bg-gray-700 rounded-lg mb-3 flex items-center justify-center">
                          {jersey.images && jersey.images.length > 0 ? (
                            <img src={jersey.images[0]} alt={jersey.team} className="w-full h-full object-cover rounded-lg" />
                          ) : (
                            <span className="text-gray-400 text-4xl">👕</span>
                          )}
                        </div>
                        <h4 className="text-white font-semibold">{jersey.team}</h4>
                        <p className="text-gray-400 text-sm">{jersey.season}</p>
                        {jersey.player && <p className="text-gray-300 text-sm">{jersey.player}</p>}
                        <div className="flex justify-between items-center mt-2">
                          <span className="text-xs bg-gray-700 px-2 py-1 rounded">{jersey.size}</span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            jersey.status === 'approved' ? 'bg-green-600' : 
                            jersey.status === 'pending' ? 'bg-yellow-600' : 'bg-red-600'
                          }`}>
                            {jersey.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Collection Tab */}
            {activeTab === 'collection' && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Collection de {profileData.display_name || profileData.name}</h3>
                {Array.isArray(userCollections) && userCollections.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg">Collection privée ou vide</div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Owned Collection */}
                    <div>
                      <h4 className="text-lg font-medium mb-3 text-green-400">📗 Maillots possédés ({Array.isArray(userCollections) ? userCollections.filter(c => c.collection_type === 'owned').length : 0})</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Array.isArray(userCollections) && userCollections.filter(c => c.collection_type === 'owned').map((item) => (
                          <div key={item.id} className="bg-gray-800 rounded-lg border border-gray-600 p-3">
                            <h5 className="text-white font-medium">{item.jersey?.team}</h5>
                            <p className="text-gray-400 text-sm">{item.jersey?.season}</p>
                            {item.jersey?.player && <p className="text-gray-300 text-sm">{item.jersey?.player}</p>}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Wanted Collection */}
                    <div>
                      <h4 className="text-lg font-medium mb-3 text-yellow-400">📒 Maillots recherchés ({Array.isArray(userCollections) ? userCollections.filter(c => c.collection_type === 'wanted').length : 0})</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Array.isArray(userCollections) && userCollections.filter(c => c.collection_type === 'wanted').map((item) => (
                          <div key={item.id} className="bg-gray-800 rounded-lg border border-gray-600 p-3">
                            <h5 className="text-white font-medium">{item.jersey?.team}</h5>
                            <p className="text-gray-400 text-sm">{item.jersey?.season}</p>
                            {item.jersey?.player && <p className="text-gray-300 text-sm">{item.jersey?.player}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Badges Tab */}
            {activeTab === 'badges' && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Badges et récompenses</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {profileData.verified_seller && (
                    <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-4 text-center">
                      <div className="text-2xl mb-2">✅</div>
                      <div className="text-white font-medium">Vendeur vérifié</div>
                    </div>
                  )}
                  {profileData.badges && profileData.badges.length > 0 ? (
                    profileData.badges.map((badge, index) => (
                      <div key={index} className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-4 text-center">
                        <div className="text-2xl mb-2">🏆</div>
                        <div className="text-white font-medium">{badge}</div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8">
                      <div className="text-gray-400">Aucun badge pour le moment</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};


// Global Marketplace Page - Discogs Style (Jersey References then Listings)
const GlobalMarketplacePage = ({ onAddToCart = null }) => {
  const [jerseys, setJerseys] = useState([]); // Jersey references available for sale
  const [selectedJersey, setSelectedJersey] = useState(null); // Selected jersey to view listings
  const [selectedJerseyListings, setSelectedJerseyListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [listingsLoading, setListingsLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [filters, setFilters] = useState({
    team: '',
    league: '',
    season: '',
    condition: '',
    size: '',
    minPrice: '',
    maxPrice: ''
  });
  const [sortBy, setSortBy] = useState('newest');
  const [searchQuery, setSearchQuery] = useState('');
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  useEffect(() => {
    fetchAvailableJerseys();
  }, []);

  // Fetch jerseys that have active listings (Discogs style catalog)
  const fetchAvailableJerseys = async () => {
    try {
      setLoading(true);
      // Get all jerseys that have at least one active listing
      const response = await axios.get(`${API}/api/marketplace/catalog`);
      setJerseys(response.data || []);
    } catch (error) {
      console.error('Failed to fetch marketplace catalog:', error);
      // Fallback: get all approved jerseys and check which have listings
      try {
        const jerseysResponse = await axios.get(`${API}/api/jerseys?status=approved`);
        const listingsResponse = await axios.get(`${API}/api/listings`);
        
        const jerseysWithListings = jerseysResponse.data.filter(jersey => 
          listingsResponse.data.some(listing => listing.jersey_id === jersey.id)
        );
        setJerseys(jerseysWithListings || []);
      } catch (fallbackError) {
        console.error('Fallback failed:', fallbackError);
        setJerseys([]);
      }
    } finally {
      setLoading(false);
    }
  };

  // Fetch listings for a specific jersey (Discogs style listings page)
  const fetchJerseyListings = async (jerseyId) => {
    try {
      setListingsLoading(true);
      const response = await axios.get(`${API}/api/listings?jersey_id=${jerseyId}`);
      setSelectedJerseyListings(response.data || []);
    } catch (error) {
      console.error('Failed to fetch jersey listings:', error);
      setSelectedJerseyListings([]);
    } finally {
      setListingsLoading(false);
    }
  };

  const handleJerseyClick = async (jersey) => {
    setSelectedJersey(jersey);
    await fetchJerseyListings(jersey.id);
  };

  const handleBackToCatalog = () => {
    setSelectedJersey(null);
    setSelectedJerseyListings([]);
  };

  // Get unique values for filters
  const getUniqueValues = (field) => {
    const values = jerseys
      .map(jersey => jersey[field])
      .filter(v => v && v.trim());
    return [...new Set(values)].sort();
  };

  // Filter and search jerseys
  const getFilteredJerseys = () => {
    let filtered = jerseys;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(jersey => 
        jersey.team?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.player?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.league?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filters
    if (filters.team) {
      filtered = filtered.filter(jersey => 
        jersey.team?.toLowerCase().includes(filters.team.toLowerCase())
      );
    }
    if (filters.league) {
      filtered = filtered.filter(jersey => 
        jersey.league?.toLowerCase().includes(filters.league.toLowerCase())
      );
    }
    if (filters.season) {
      filtered = filtered.filter(jersey => 
        jersey.season === filters.season
      );
    }

    return filtered;
  };

  // Sort listings for selected jersey
  const getSortedListings = () => {
    let sorted = [...selectedJerseyListings];
    
    switch (sortBy) {
      case 'price_low':
        sorted.sort((a, b) => a.price - b.price);
        break;
      case 'price_high':
        sorted.sort((a, b) => b.price - a.price);
        break;
      case 'condition':
        const conditionOrder = { 'mint': 5, 'excellent': 4, 'very_good': 3, 'good': 2, 'fair': 1 };
        sorted.sort((a, b) => (conditionOrder[b.jersey?.condition] || 0) - (conditionOrder[a.jersey?.condition] || 0));
        break;
      case 'newest':
      default:
        sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
    }
    
    return sorted;
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const getConditionBadge = (condition) => {
    const badges = {
      'mint': 'bg-green-100 text-green-800',
      'excellent': 'bg-blue-100 text-blue-800', 
      'very_good': 'bg-yellow-100 text-yellow-800',
      'good': 'bg-orange-100 text-orange-800',
      'fair': 'bg-red-100 text-red-800'
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badges[condition] || 'bg-gray-100 text-gray-800'}`}>
        {condition?.toUpperCase() || 'N/A'}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading marketplace...</div>
      </div>
    );
  }

  // Show listings for selected jersey (Step C in Discogs flow)
  if (selectedJersey) {
    return (
      <div className="min-h-screen bg-black">
        <div className="container mx-auto px-4 py-8">
          {/* Back button and jersey info */}
          <div className="mb-8">
            <button
              onClick={handleBackToCatalog}
              className="text-blue-400 hover:text-white mb-4 flex items-center space-x-2"
            >
              <span>←</span>
              <span>Retour au catalogue</span>
            </button>
            
            <div className="bg-gray-900 rounded-xl border border-gray-700 p-6">
              <div className="flex items-start space-x-6">
                <div className="w-32 h-32 bg-gray-800 rounded overflow-hidden flex-shrink-0">
                  {selectedJersey.images?.[0] ? (
                    <img 
                      src={selectedJersey.images[0]} 
                      alt={selectedJersey.team}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-500">
                      👕
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-white mb-2">
                    {selectedJersey.player ? `${selectedJersey.team} - ${selectedJersey.player}` : selectedJersey.team}
                  </h1>
                  <p className="text-gray-300 text-lg mb-4">
                    {selectedJersey.league} • {selectedJersey.season} • {selectedJersey.home_away}
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Référence:</span>
                      <span className="text-white ml-2 font-mono">{selectedJersey.reference_number}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Fabricant:</span>
                      <span className="text-white ml-2">{selectedJersey.manufacturer}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Annonces:</span>
                      <span className="text-white ml-2">{selectedJerseyListings.length}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Prix dès:</span>
                      <span className="text-white ml-2 font-bold">
                        {selectedJerseyListings.length > 0 ? `${Math.min(...selectedJerseyListings.map(l => l.price))}€` : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Listings controls */}
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">
                Annonces disponibles ({selectedJerseyListings.length})
              </h2>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white"
              >
                <option value="price_low">Prix croissant</option>
                <option value="price_high">Prix décroissant</option>
                <option value="condition">Par état</option>
                <option value="newest">Plus récent</option>
              </select>
            </div>
          </div>

          {/* Listings */}
          {listingsLoading ? (
            <div className="text-center py-8 text-gray-400">Chargement des annonces...</div>
          ) : selectedJerseyListings.length > 0 ? (
            <div className="space-y-4">
              {getSortedListings().map((listing) => (
                <div key={listing.id} className="bg-gray-900 rounded-lg border border-gray-700 p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-3">
                        <div className="text-2xl font-bold text-white">{listing.price}€</div>
                        {getConditionBadge(listing.jersey?.condition)}
                        <div className="text-sm text-gray-400">Taille {listing.jersey?.size}</div>
                      </div>
                      
                      {listing.description && (
                        <p className="text-gray-300 mb-4">{listing.description}</p>
                      )}
                      
                      <div className="flex items-center space-x-6 text-sm text-gray-400">
                        <div><span className="font-medium">Vendeur:</span> Anonyme</div>
                        <div><span className="font-medium">Publié:</span> {new Date(listing.created_at).toLocaleDateString('fr-FR')}</div>
                      </div>
                    </div>
                    
                    <div className="ml-6 space-y-2">
                      <button 
                        onClick={() => {
                          if (onAddToCart) {
                            // Créer un objet listing compatible avec le panier
                            const cartListing = {
                              jersey: selectedJersey,
                              id: listing.id,
                              price: listing.price,
                              size: listing.jersey?.size || listing.size,
                              condition: listing.jersey?.condition || listing.condition,
                              user: { 
                                id: listing.user_id || 'anonymous',
                                name: 'Vendeur anonyme' 
                              }
                            };
                            onAddToCart(cartListing, 1);
                          }
                        }}
                        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors font-medium flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5H20M7 13v4a2 2 0 002 2h6a2 2 0 002-2v-4" />
                        </svg>
                        <span>Ajouter au panier</span>
                      </button>
                      <button 
                        onClick={() => {
                          // TODO: Implement contact seller functionality
                          // This would open the messaging interface with a pre-filled message to the seller
                          alert('Fonctionnalité de contact vendeur à venir ! Pour l\'instant, utilisez la section Messages.');
                        }}
                        className="block bg-gray-800 text-gray-300 px-6 py-2 rounded hover:bg-gray-700 transition-colors text-center"
                      >
                        Contacter vendeur
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">Aucune annonce disponible pour ce maillot</div>
              <p className="text-gray-500">Ajoutez-le à votre wishlist pour être notifié quand une annonce sera disponible.</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Show jersey catalog (Step A & B in Discogs flow)
  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Marketplace</h1>
          <p className="text-gray-400 mb-4">Découvrez et achetez des maillots mis en vente par la communauté</p>
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-3 text-blue-300 text-sm">
            💡 <strong>Astuce :</strong> Cliquez sur un maillot pour voir les annonces disponibles et ajouter au panier
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Rechercher par équipe, joueur, championnat..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-white focus:border-transparent"
              />
            </div>
            
            {/* View Toggle Buttons */}
            <div className="flex bg-gray-800 rounded-lg border border-gray-700 p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z"/>
                </svg>
                <span className="hidden sm:inline">Grille</span>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z"/>
                </svg>
                <span className="hidden sm:inline">Liste</span>
              </button>
            </div>
            
            <button
              onClick={() => setShowMobileFilters(!showMobileFilters)}
              className="lg:hidden bg-gray-800 text-white px-4 py-3 rounded-lg border border-gray-700"
            >
              Filtres {showMobileFilters ? '▲' : '▼'}
            </button>
          </div>

          {/* Filters */}
          <div className={`grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 ${showMobileFilters ? 'block' : 'hidden lg:grid'}`}>
            <select
              value={filters.league}
              onChange={(e) => handleFilterChange('league', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Tous les championnats</option>
              {getUniqueValues('league').map(league => (
                <option key={league} value={league}>{league}</option>
              ))}
            </select>
            <select
              value={filters.team}
              onChange={(e) => handleFilterChange('team', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Toutes les équipes</option>
              {getUniqueValues('team').map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
            <select
              value={filters.season}
              onChange={(e) => handleFilterChange('season', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="">Toutes les saisons</option>
              {getUniqueValues('season').map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Prix min €"
              value={filters.minPrice}
              onChange={(e) => handleFilterChange('minPrice', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm placeholder-gray-400"
            />
            <input
              type="number"
              placeholder="Prix max €"
              value={filters.maxPrice}
              onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm placeholder-gray-400"
            />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="newest">Plus récent</option>
              <option value="team">Par équipe</option>
              <option value="league">Par championnat</option>
            </select>
          </div>
        </div>

        {/* Jersey Catalog */}
        {viewMode === 'grid' ? (
          // Grid View
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {getFilteredJerseys().map((jersey) => (
              <div
                key={jersey.id}
                onClick={() => handleJerseyClick(jersey)}
                className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden hover:border-blue-500 hover:shadow-blue-500/25 transition-all cursor-pointer group hover:shadow-xl transform hover:scale-102"
              >
                <div className="aspect-square bg-gray-800 overflow-hidden">
                  {jersey.images?.[0] ? (
                    <img
                      src={jersey.images[0]}
                      alt={jersey.team}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-500 text-6xl">
                      👕
                    </div>
                  )}
                  {/* Price overlay */}
                  <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm font-medium">
                    dès {jersey.min_price || '?'}€
                  </div>
                </div>
                
                <div className="p-4">
                  <h3 className="font-semibold text-white text-sm mb-1 truncate">
                    {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
                  </h3>
                  <p className="text-gray-400 text-xs mb-2">
                    {jersey.league} • {jersey.season}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 text-xs">{jersey.reference_number}</span>
                    <span className="text-blue-400 text-xs font-medium flex items-center space-x-1">
                      <span>{jersey.listing_count || 1} annonce{(jersey.listing_count || 1) > 1 ? 's' : ''}</span>
                      <span>→</span>
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          // List View
          <div className="space-y-4">
            {getFilteredJerseys().map((jersey) => (
              <div
                key={jersey.id}
                onClick={() => handleJerseyClick(jersey)}
                className="bg-gray-900 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-all cursor-pointer group hover:shadow-lg"
              >
                <div className="flex items-center space-x-6">
                  {/* Jersey Image */}
                  <div className="w-20 h-20 bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                    {jersey.images?.[0] ? (
                      <img
                        src={jersey.images[0]}
                        alt={jersey.team}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-500 text-2xl">
                        👕
                      </div>
                    )}
                  </div>
                  
                  {/* Jersey Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white text-lg mb-1 truncate">
                      {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
                    </h3>
                    <p className="text-gray-400 text-sm mb-2">
                      {jersey.league} • {jersey.season} • {jersey.home_away}
                    </p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>Réf: {jersey.reference_number}</span>
                      <span>•</span>
                      <span>{jersey.manufacturer}</span>
                      <span>•</span>
                      <span>{jersey.listing_count || 1} annonce{(jersey.listing_count || 1) > 1 ? 's' : ''}</span>
                    </div>
                  </div>
                  
                  {/* Price and Action */}
                  <div className="text-right">
                    <div className="text-lg font-bold text-white mb-1">
                      dès {jersey.min_price || '?'}€
                    </div>
                    <div className="text-sm text-blue-400 group-hover:text-blue-300">
                      Voir les annonces →
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {getFilteredJerseys().length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4 text-lg">Aucun maillot trouvé</div>
            <p className="text-gray-500">Essayez de modifier vos filtres ou votre recherche</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Jersey Detail Page Component (moved from marketplace)  
const JerseyDetailPage = ({ jerseyId, referenceNumber }) => {
  const { user } = useAuth();
  const [jersey, setJersey] = useState(null);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userCollection, setUserCollection] = useState({ owned: false, wanted: false });
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchJerseyDetails();
    if (user) {
      checkUserCollection();
    }
  }, [jerseyId, referenceNumber, user]);

  const fetchJerseyDetails = async () => {
    // Implementation for fetching jersey details
  };

  const checkUserCollection = async () => {
    // Implementation for checking user collection
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Component content will be implemented here */}
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white">Jersey Detail Page</h1>
        <p className="text-gray-400">Jersey ID: {jerseyId}</p>
        <p className="text-gray-400">Reference: {referenceNumber}</p>
      </div>
    </div>
  );
};

// MessagingInterface Component
const MessagingInterface = () => {
  const { user } = useAuth();
  const [searchResults, setSearchResults] = useState([]);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [showNewConversation, setShowNewConversation] = useState(false);

  // Fetch conversations
  const fetchConversations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(response.data || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch messages for a specific conversation
  const fetchMessages = async (conversationId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/conversations/${conversationId}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      setMessages([]);
    }
  };

  // Send message
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation || sendingMessage) return;

    try {
      setSendingMessage(true);
      const token = localStorage.getItem('token');
      
      await axios.post(`${API}/api/conversations/send`, {
        conversation_id: selectedConversation.id,
        message: newMessage.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setNewMessage('');
      // Refresh messages
      await fetchMessages(selectedConversation.id);
      // Refresh conversations to update last message
      await fetchConversations();
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSendingMessage(false);
    }
  };

  // Start new conversation
  const startConversation = async (recipientId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/conversations`, {
        recipient_id: recipientId,
        message: "Hello! I'd like to connect with you on TopKit."
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh conversations
      await fetchConversations();
      setShowNewConversation(false);
      setUserSearchQuery('');
      setSearchResults([]);
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };

  // Search users
  const searchForUsers = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      setSearchingUsers(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/users/search?q=${encodeURIComponent(query)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSearchResults(response.data.users || []);
    } catch (error) {
      console.error('Failed to search users:', error);
      setSearchResults([]);
    } finally {
      setSearchingUsers(false);
    }
  };

  // Effect to handle search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (userSearchQuery) {
        searchForUsers(userSearchQuery);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [userSearchQuery]);

  // Load conversations on mount
  useEffect(() => {
    if (user) {
      fetchConversations();
    }
  }, [user]);

  // Load messages when conversation is selected
  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id);
    }
  }, [selectedConversation]);

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatConversationTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg border border-gray-700 p-8">
        <div className="flex items-center justify-center">
          <LoadingSpinner size="lg" className="mr-3" />
          <span className="text-gray-400">Loading conversations...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg border border-gray-700 h-96 flex">
      {/* Conversations List */}
      <div className="w-1/3 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold">Conversations</h3>
            <button
              onClick={() => setShowNewConversation(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
            >
              + New
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <div className="text-4xl mb-2">💬</div>
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new conversation!</p>
            </div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation)}
                className={`p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800 transition-colors ${
                  selectedConversation?.id === conversation.id ? 'bg-gray-800' : ''
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Avatar
                    user={conversation.other_participant}
                    size="sm"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-white text-sm font-medium truncate">
                        {conversation.other_participant?.name || 'Unknown User'}
                      </p>
                      {conversation.last_message && (
                        <p className="text-xs text-gray-500">
                          {formatConversationTime(conversation.last_message.created_at)}
                        </p>
                      )}
                    </div>
                    {conversation.last_message && (
                      <p className="text-gray-400 text-xs truncate mt-1">
                        {conversation.last_message.sent_by_me ? 'You: ' : ''}{conversation.last_message.message}
                      </p>
                    )}
                  </div>
                  {conversation.unread_count > 0 && (
                    <div className="bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {conversation.unread_count}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Message Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Conversation Header */}
            <div className="p-4 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <Avatar
                  user={selectedConversation.other_participant}
                  size="sm"
                />
                <div>
                  <h3 className="text-white font-medium">
                    {selectedConversation.other_participant?.name || 'Unknown User'}
                  </h3>
                  <p className="text-gray-400 text-xs">
                    {selectedConversation.other_participant?.name ? 'TopKit Collector' : 'User not found'}
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  <p>Start the conversation!</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender_id === user?.id 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-800 text-white'
                    }`}>
                      <p className="text-sm">{message.message}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender_id === user?.id ? 'text-blue-200' : 'text-gray-400'
                      }`}>
                        {formatMessageTime(message.created_at)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-700">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={sendingMessage || !newMessage.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {sendingMessage ? 'Sending...' : 'Send'}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-6xl mb-4">💬</div>
              <p className="text-lg mb-2">Select a conversation to start chatting</p>
              <p className="text-sm">Choose from your conversations on the left</p>
            </div>
          </div>
        )}
      </div>

      {/* New Conversation Modal */}
      {showNewConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 w-96">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-white font-semibold">Start New Conversation</h3>
              <button
                onClick={() => {
                  setShowNewConversation(false);
                  setUserSearchQuery('');
                  setSearchResults([]);
                }}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Search for users</label>
                <input
                  type="text"
                  value={userSearchQuery}
                  onChange={(e) => setUserSearchQuery(e.target.value)}
                  placeholder="Type username or email..."
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="max-h-60 overflow-y-auto">
                {searchingUsers ? (
                  <div className="flex items-center justify-center py-4">
                    <LoadingSpinner size="sm" className="mr-2" />
                    <span className="text-gray-400 text-sm">Searching...</span>
                  </div>
                ) : searchResults.length > 0 ? (
                  <div className="space-y-2">
                    {searchResults.map((searchUser) => (
                      <div
                        key={searchUser.id}
                        className="flex items-center justify-between p-3 bg-gray-800 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <Avatar user={searchUser} size="sm" />
                          <div>
                            <p className="text-white text-sm font-medium">{searchUser.name}</p>
                            <p className="text-gray-400 text-xs">{searchUser.email}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => startConversation(searchUser.id)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                        >
                          Message
                        </button>
                      </div>
                    ))}
                  </div>
                ) : userSearchQuery.length >= 2 ? (
                  <div className="text-center py-4 text-gray-400 text-sm">
                    No users found
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-400 text-sm">
                    Type at least 2 characters to search
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced Submission Card Component
const EnhancedSubmissionCard = ({ jersey, onResubmit }) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showResubmissionModal, setShowResubmissionModal] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-800 text-green-200';
      case 'rejected': return 'bg-red-800 text-red-200';
      case 'needs_modification': return 'bg-orange-800 text-orange-200';
      default: return 'bg-yellow-800 text-yellow-200';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'approved': return '✅ Approuvé';
      case 'rejected': return '❌ Rejeté';
      case 'needs_modification': return '🔧 Modifications requises';
      default: return '⏳ En attente';
    }
  };

  const fetchSuggestions = async () => {
    if (!jersey || jersey.status !== 'needs_modification') return;
    
    try {
      setLoadingSuggestions(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/jerseys/${jersey.id}/suggestions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuggestions(response.data || []);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleViewSuggestions = async () => {
    setShowSuggestions(true);
    await fetchSuggestions();
  };

  const handleResubmit = () => {
    setShowResubmissionModal(true);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <>
      <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
        <div className="flex items-start space-x-4">
          {/* Jersey Image */}
          <div className="w-20 h-20 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden">
            {jersey.images && jersey.images.length > 0 ? (
              <img
                src={jersey.images[0]}
                alt={`${jersey.team} ${jersey.season}`}
                className="w-full h-full object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = 'https://dummyimage.com/80x80/333/fff.png&text=Jersey';
                }}
              />
            ) : (
              <div className="text-gray-500 text-2xl">👕</div>
            )}
          </div>

          {/* Jersey Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1 truncate">
                  {jersey.team}
                </h3>
                <p className="text-gray-400 text-sm mb-1">
                  {jersey.season} • {jersey.home_away || 'Domicile'}
                  {jersey.player && ` • ${jersey.player}`}
                </p>
                <p className="text-gray-500 text-xs">
                  Référence: {jersey.reference_number}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(jersey.status)}`}>
                {getStatusText(jersey.status)}
              </span>
            </div>

            {/* Jersey Specs */}
            <div className="flex items-center space-x-4 mb-3 text-sm text-gray-400">
              <span>Taille: {jersey.size}</span>
              <span>État: {jersey.condition}</span>
              {jersey.manufacturer && <span>Marque: {jersey.manufacturer}</span>}
            </div>

            {/* Submission Date */}
            <div className="text-xs text-gray-500 mb-4">
              Soumis le {formatDate(jersey.created_at)}
              {jersey.approved_at && jersey.status === 'approved' && (
                <span> • Approuvé le {formatDate(jersey.approved_at)}</span>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-3">
              {jersey.status === 'needs_modification' && (
                <>
                  <button
                    onClick={handleViewSuggestions}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    📝 Voir les suggestions
                  </button>
                  <button
                    onClick={handleResubmit}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    🔄 Resoumettre
                  </button>
                </>
              )}
              
              {jersey.status === 'rejected' && jersey.rejection_reason && (
                <div className="text-red-400 text-sm">
                  <span className="font-medium">Motif:</span> {jersey.rejection_reason}
                </div>
              )}

              {jersey.status === 'approved' && (
                <div className="text-green-400 text-sm font-medium">
                  🎉 Maillot publié dans la base de données
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Suggestions Modal */}
      {showSuggestions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl max-w-2xl w-full max-h-screen overflow-y-auto border border-gray-700">
            <div className="flex justify-between items-center p-6 border-b border-gray-700">
              <h3 className="text-xl font-bold text-white">Suggestions de modification</h3>
              <button
                onClick={() => setShowSuggestions(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ✕
              </button>
            </div>

            <div className="p-6">
              {loadingSuggestions ? (
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner size="md" className="mr-3" />
                  <span className="text-gray-400">Chargement des suggestions...</span>
                </div>
              ) : suggestions.length > 0 ? (
                <div className="space-y-4">
                  {suggestions.map((suggestion, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg border border-gray-600 p-4">
                      <div className="flex items-start space-x-3 mb-3">
                        <Avatar user={{ name: suggestion.moderator_info?.name }} size="sm" />
                        <div>
                          <div className="text-white font-medium">
                            {suggestion.moderator_info?.name || 'Modérateur'}
                          </div>
                          <div className="text-gray-400 text-xs">
                            {formatDate(suggestion.created_at)}
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-gray-700 rounded-lg p-3 mb-3">
                        <p className="text-white text-sm leading-relaxed">
                          {suggestion.suggested_changes}
                        </p>
                      </div>

                      {suggestion.suggested_modifications && Object.keys(suggestion.suggested_modifications).length > 0 && (
                        <div className="space-y-2">
                          <div className="text-gray-300 text-sm font-medium">Modifications suggérées:</div>
                          {Object.entries(suggestion.suggested_modifications).map(([field, value]) => (
                            <div key={field} className="text-xs text-gray-400 bg-gray-700 px-3 py-2 rounded">
                              <span className="font-medium capitalize">{field}:</span> {value}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  Aucune suggestion trouvée
                </div>
              )}

              <div className="flex justify-between items-center mt-6 pt-6 border-t border-gray-700">
                <button
                  onClick={() => setShowSuggestions(false)}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Fermer
                </button>
                <button
                  onClick={() => {
                    setShowSuggestions(false);
                    handleResubmit();
                  }}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  🔄 Resoumettre ce maillot
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Resubmission Modal */}
      {showResubmissionModal && (
        <ResubmissionModal
          originalJersey={jersey}
          onClose={() => setShowResubmissionModal(false)}
          onSuccess={() => {
            setShowResubmissionModal(false);
            onResubmit();
          }}
        />
      )}
    </>
  );
};

// Unified Profile & Collection Page with Dark Theme
const ProfileCollectionPage = ({ shouldRefresh = false, setShowSubmitModal }) => {
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('collection');
  const [ownedJerseys, setOwnedJerseys] = useState([]);
  const [wantedJerseys, setWantedJerseys] = useState([]);
  const [submittedJerseys, setSubmittedJerseys] = useState([]);
  const [userListings, setUserListings] = useState([]);
  const [purchaseHistory, setPurchaseHistory] = useState([]);
  const [salesHistory, setSalesHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(Date.now());
  const [collectionStats, setCollectionStats] = useState({
    totalValue: 0,
    averageValue: 0,
    totalItems: 0,
    mostValuableItem: null,
    totalListings: 0,
    activeListings: 0,
    soldListings: 0,
    totalRevenue: 0
  });

  // Friends data states
  const [friendsData, setFriendsData] = useState({
    friends: [],
    pendingReceived: [],
    pendingSent: [],
    totalFriends: 0
  });
  const [friendsActiveTab, setFriendsActiveTab] = useState('friends');

  // Messages data states
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);

  // Site settings states
  const [siteMode, setSiteMode] = useState('public');
  const [siteSettingsLoading, setSiteSettingsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      fetchCollectionData();
      fetchFriendsData();
      fetchUserListings();
      fetchPaymentHistoryProfile();
      fetchSiteSettings();
    }
  }, [user, lastRefresh]);

  // Add effect to handle page visibility and refresh data when user comes back
  useEffect(() => {
    const handleFocus = () => {
      if (user) {
        fetchCollectionData();
        fetchFriendsData();
      }
    };

    const handleCustomRefresh = () => {
      setLastRefresh(Date.now());
    };

    window.addEventListener('focus', handleFocus);
    window.addEventListener('refreshProfile', handleCustomRefresh);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('refreshProfile', handleCustomRefresh);
    };
  }, [user]);

  const fetchCollectionData = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch collections
      const [ownedRes, wantedRes, submittedRes] = await Promise.all([
        axios.get(`${API}/api/collections/owned`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/api/collections/wanted`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/api/users/${user.id}/jerseys`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      const owned = ownedRes.data || [];
      const wanted = wantedRes.data || [];
      const submitted = submittedRes.data || [];
      
      setOwnedJerseys(owned);
      setWantedJerseys(wanted);
      setSubmittedJerseys(submitted);
      
      // Calculate collection value estimate (mock values for demo)
      const estimatedValues = owned.map(() => Math.floor(Math.random() * 200) + 50); // Random values 50-250€
      const totalValue = estimatedValues.reduce((sum, val) => sum + val, 0);
      const averageValue = owned.length > 0 ? Math.round(totalValue / owned.length) : 0;
      const mostValuable = owned.length > 0 ? owned[estimatedValues.indexOf(Math.max(...estimatedValues))] : null;
      
      setCollectionStats({
        totalValue,
        averageValue,
        totalItems: owned.length,
        mostValuableItem: mostValuable
      });
      
    } catch (error) {
      console.error('Failed to fetch collection data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFriendsData = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/friends`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const { friends, received_requests, sent_requests } = response.data;
      
      setFriendsData({
        friends: friends || [],
        pendingReceived: received_requests || [],
        pendingSent: sent_requests || [],
        totalFriends: friends ? friends.length : 0
      });
      
    } catch (error) {
      console.error('Failed to fetch friends data:', error);
      setFriendsData({
        friends: [],
        pendingReceived: [],
        pendingSent: [],
        totalFriends: 0
      });
    }
  };

  const fetchUserListings = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/listings?seller_id=${user.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const listings = response.data || [];
      setUserListings(listings);
      
      // Calculate listing stats and update collection stats
      const activeListings = listings.filter(listing => listing.status === 'active');
      const soldListings = listings.filter(listing => listing.status === 'sold');
      const totalRevenue = soldListings.reduce((sum, listing) => sum + (listing.price || 0), 0);
      
      setCollectionStats(prev => ({
        ...prev,
        totalListings: listings.length,
        activeListings: activeListings.length,
        soldListings: soldListings.length,
        totalRevenue
      }));
      
    } catch (error) {
      console.error('Failed to fetch user listings:', error);
      setUserListings([]);
    }
  };

  const fetchPaymentHistoryProfile = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      
      // Fetch both purchase and sales history
      const [purchasesRes, salesRes] = await Promise.all([
        axios.get(`${API}/api/payments/history`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/api/payments/sales`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setPurchaseHistory(purchasesRes.data.purchases || []);
      setSalesHistory(salesRes.data.sales || []);
      
    } catch (error) {
      console.error('Failed to fetch payment history:', error);
      setPurchaseHistory([]);
      setSalesHistory([]);
    }
  };

  const fetchSiteSettings = async () => {
    try {
      setSiteSettingsLoading(true);
      const response = await axios.get(`${API}/api/site/mode`);
      setSiteMode(response.data.mode);
    } catch (error) {
      console.error('Failed to fetch site settings:', error);
    } finally {
      setSiteSettingsLoading(false);
    }
  };

  const updateSiteMode = async (newMode) => {
    if (!window.confirm(`Changer le mode du site vers "${newMode}" ?`)) return;

    try {
      setSiteSettingsLoading(true);
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/site/mode`, {
        mode: newMode
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSiteMode(newMode);
      alert(`Mode du site changé vers: ${newMode}`);
    } catch (error) {
      console.error('Failed to update site mode:', error);
      alert('Erreur lors du changement de mode');
    } finally {
      setSiteSettingsLoading(false);
    }
  };

  const handleRemoveFromCollection = async (jerseyId, collectionType) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/collections/remove`, {
        jersey_id: jerseyId,
        collection_type: collectionType
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Refresh collection data
      fetchCollectionData();
    } catch (error) {
      console.error('Failed to remove from collection:', error);
      alert('Failed to remove jersey from collection. Please try again.');
    }
  };

  const handleFriendResponse = async (requestId, accept) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/friends/respond`, {
        request_id: requestId,
        accept: accept
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Refresh friends data
      fetchFriendsData();
      
      if (accept) {
        alert('Demande d\'ami acceptée !');
      } else {
        alert('Demande d\'ami refusée.');
      }
    } catch (error) {
      console.error('Failed to respond to friend request:', error);
      alert('Impossible de répondre à la demande d\'ami. Veuillez réessayer.');
    }
  };

  const renderCollectionList = (items, collectionType) => (
    <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
      {/* Desktop Table View */}
      <div className="hidden md:block">
        {/* Table Header */}
        <div className="bg-gray-800 px-6 py-3 border-b border-gray-700">
          <div className="grid grid-cols-12 gap-4 text-xs font-medium text-gray-400 uppercase tracking-wide">
            <div className="col-span-1"></div>
            <div className="col-span-3">Maillot</div>
            <div className="col-span-2">Équipe</div>
            <div className="col-span-2">Saison</div>
            <div className="col-span-1">Taille</div>
            <div className="col-span-1">État</div>
            {collectionType === 'owned' && <div className="col-span-1">Valeur</div>}
            <div className="col-span-1">Actions</div>
          </div>
        </div>
        
        {/* Table Body */}
        <div className="divide-y divide-gray-700">
          {items.map((item, index) => (
            <div key={item.id} className="px-6 py-4 hover:bg-gray-800 transition-colors">
              <div className="grid grid-cols-12 gap-4 items-center">
                {/* Image */}
                <div className="col-span-1">
                  <div className="w-12 h-12 bg-gray-800 rounded flex items-center justify-center overflow-hidden">
                    {item.jersey?.images && item.jersey.images.length > 0 ? (
                      <img
                        src={item.jersey.images[0]}
                        alt={`${item.jersey.team} ${item.jersey.season}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.src = 'https://dummyimage.com/48x48/333/fff.png&text=Jersey';
                        }}
                      />
                    ) : (
                      <span className="text-gray-500 text-lg">👕</span>
                    )}
                  </div>
                </div>
                
                {/* Jersey Name */}
                <div className="col-span-3">
                  <div className="text-white font-medium text-sm truncate">
                    {item.jersey?.player ? `${item.jersey.team} - ${item.jersey.player}` : item.jersey?.team}
                  </div>
                  <div className="text-gray-400 text-xs">
                    {item.jersey?.league} • {item.jersey?.home_away}
                  </div>
                </div>
                
                {/* Team */}
                <div className="col-span-2">
                  <div className="text-white text-sm truncate">{item.jersey?.team}</div>
                </div>
                
                {/* Season */}
                <div className="col-span-2">
                  <div className="text-white text-sm">{item.jersey?.season}</div>
                </div>
                
                {/* Size */}
                <div className="col-span-1">
                  <div className="text-white text-sm">{item.jersey?.size}</div>
                </div>
                
                {/* Condition */}
                <div className="col-span-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    item.jersey?.condition === 'new' ? 'bg-green-800 text-green-200' :
                    item.jersey?.condition === 'near_mint' ? 'bg-blue-800 text-blue-200' :
                    item.jersey?.condition === 'very_good' ? 'bg-yellow-800 text-yellow-200' :
                    item.jersey?.condition === 'good' ? 'bg-orange-800 text-orange-200' :
                    'bg-red-800 text-red-200'
                  }`}>
                    {item.jersey?.condition === 'new' ? 'N' :
                     item.jersey?.condition === 'near_mint' ? 'NM' :
                     item.jersey?.condition === 'very_good' ? 'VG+' :
                     item.jersey?.condition === 'good' ? 'VG' : 'P'}
                  </span>
                </div>
                
                {/* Value (only for owned) */}
                {collectionType === 'owned' && (
                  <div className="col-span-1">
                    <div className="text-green-400 font-semibold text-sm">
                      {Math.floor(Math.random() * 200) + 50}€
                    </div>
                  </div>
                )}
                
                {/* Actions */}
                <div className="col-span-1">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => window.dispatchEvent(new CustomEvent('changeView', { 
                        detail: `jersey-detail-${item.jersey?.reference_number || item.jersey?.id}` 
                      }))}
                      className="text-blue-400 hover:text-blue-300 text-xs"
                      title="Voir le détail"
                    >
                      👁️
                    </button>
                    <button
                      onClick={() => handleRemoveFromCollection(item.jersey.id, collectionType)}
                      className="text-red-400 hover:text-red-300 text-xs"
                      title="Retirer"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3 p-4">
        {items.map((item, index) => (
          <div key={item.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-start space-x-3">
              {/* Mobile Image */}
              <div className="w-16 h-16 bg-gray-700 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                {item.jersey?.images && item.jersey.images.length > 0 ? (
                  <img
                    src={item.jersey.images[0]}
                    alt={`${item.jersey.team} ${item.jersey.season}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://dummyimage.com/64x64/333/fff.png&text=Jersey';
                    }}
                  />
                ) : (
                  <span className="text-gray-500 text-xl">👕</span>
                )}
              </div>
              
              {/* Mobile Content */}
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-medium text-sm truncate">
                  {item.jersey?.player ? `${item.jersey.team} - ${item.jersey.player}` : item.jersey?.team}
                </h3>
                <div className="text-gray-400 text-xs mt-1">
                  {item.jersey?.league} • {item.jersey?.season} • {item.jersey?.home_away}
                </div>
                
                {/* Mobile Details Row */}
                <div className="flex items-center space-x-4 mt-2">
                  <span className="text-white text-xs">
                    <span className="text-gray-400">Taille:</span> {item.jersey?.size}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    item.jersey?.condition === 'new' ? 'bg-green-800 text-green-200' :
                    item.jersey?.condition === 'near_mint' ? 'bg-blue-800 text-blue-200' :
                    item.jersey?.condition === 'very_good' ? 'bg-yellow-800 text-yellow-200' :
                    item.jersey?.condition === 'good' ? 'bg-orange-800 text-orange-200' :
                    'bg-red-800 text-red-200'
                  }`}>
                    {item.jersey?.condition === 'new' ? 'Neuf' :
                     item.jersey?.condition === 'near_mint' ? 'Quasi-neuf' :
                     item.jersey?.condition === 'very_good' ? 'Très bon' :
                     item.jersey?.condition === 'good' ? 'Bon' : 'Correct'}
                  </span>
                  {collectionType === 'owned' && (
                    <span className="text-green-400 font-semibold text-sm">
                      {Math.floor(Math.random() * 200) + 50}€
                    </span>
                  )}
                </div>
                
                {/* Mobile Actions */}
                <div className="flex items-center space-x-3 mt-3">
                  <button
                    onClick={() => window.dispatchEvent(new CustomEvent('changeView', { 
                      detail: `jersey-detail-${item.jersey?.reference_number || item.jersey?.id}` 
                    }))}
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-xs font-medium hover:bg-blue-700 transition-colors"
                  >
                    👁️ Voir détail
                  </button>
                  <button
                    onClick={() => handleRemoveFromCollection(item.jersey.id, collectionType)}
                    className="flex-1 bg-red-600 text-white px-3 py-2 rounded text-xs font-medium hover:bg-red-700 transition-colors"
                  >
                    🗑️ Retirer
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Footer with count */}
      <div className="bg-gray-800 px-6 py-3 border-t border-gray-700">
        <div className="text-sm text-gray-400">
          {items.length} maillot{items.length > 1 ? 's' : ''} • Valeur totale estimée: {
            collectionType === 'owned' ? `${items.reduce((sum, item) => sum + (Math.floor(Math.random() * 200) + 50), 0)}€` : '-'
          }
        </div>
      </div>
    </div>
  );
  
  const renderJerseyCard = (item, collectionType) => (
    <div key={item.id} className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors">
      <div className="aspect-square bg-gray-800 flex items-center justify-center overflow-hidden">
        {item.jersey?.images && item.jersey.images.length > 0 ? (
          <img
            src={item.jersey.images[0]}
            alt={`${item.jersey.team} ${item.jersey.season}`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.src = 'https://dummyimage.com/200x200/333/fff.png&text=Jersey';
            }}
          />
        ) : (
          <div className="text-gray-500 text-center">
            <div className="text-4xl mb-2">👕</div>
            <div className="text-sm">No Image</div>
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="text-white font-semibold text-sm mb-1 truncate">
          {item.jersey?.team}
        </h3>
        <p className="text-gray-400 text-xs mb-2">
          {item.jersey?.season} • {item.jersey?.home_away}
        </p>
        {item.jersey?.player && (
          <p className="text-white text-xs font-medium mb-2 truncate">
            {item.jersey.player}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">
            {item.jersey?.reference_number}
          </span>
          {collectionType === 'owned' && (
            <span className="text-xs text-green-400 font-semibold">
              ~{Math.floor(Math.random() * 200) + 50}€
            </span>
          )}
        </div>
        
        <button
          onClick={() => handleRemoveFromCollection(item.jersey.id, collectionType)}
          className="w-full mt-3 bg-red-600 text-white px-3 py-2 rounded text-xs hover:bg-red-700 transition-colors"
        >
          Retirer de {collectionType === 'owned' ? 'ma collection' : 'ma wishlist'}
        </button>
      </div>
    </div>
  );

  const renderSubmittedJerseyCard = (jersey) => (
    <div key={jersey.id} className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors">
      <div className="aspect-square bg-gray-800 flex items-center justify-center overflow-hidden">
        {jersey.images && jersey.images.length > 0 ? (
          <img
            src={jersey.images[0]}
            alt={`${jersey.team} ${jersey.season}`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.src = 'https://dummyimage.com/200x200/333/fff.png&text=Jersey';
            }}
          />
        ) : (
          <div className="text-gray-500 text-center">
            <div className="text-4xl mb-2">👕</div>
            <div className="text-sm">No Image</div>
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="text-white font-semibold text-sm mb-1 truncate">
          {jersey.team}
        </h3>
        <p className="text-gray-400 text-xs mb-2">
          {jersey.season} • {jersey.home_away}
        </p>
        {jersey.player && (
          <p className="text-white text-xs font-medium mb-2 truncate">
            {jersey.player}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">
            {jersey.reference_number}
          </span>
          <span className={`text-xs px-2 py-1 rounded font-medium ${
            jersey.status === 'approved' ? 'bg-green-800 text-green-200' :
            jersey.status === 'rejected' ? 'bg-red-800 text-red-200' :
            'bg-yellow-800 text-yellow-200'
          }`}>
            {jersey.status === 'approved' ? 'Approuvé' :
             jersey.status === 'rejected' ? 'Rejeté' : 'En attente'}
          </span>
        </div>
      </div>
    </div>
  );

  if (!user) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 mb-4">Please login to view your profile</div>
          <button 
            onClick={() => window.dispatchEvent(new CustomEvent('showAuthModal', {}))}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700">
        <div className="container mx-auto px-4 md:px-6 py-4 md:py-6">
          <div className="flex items-start space-x-4 md:space-x-6">
            {/* Profile Picture */}
            <div className="w-16 h-16 md:w-24 md:h-24 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
              {user.profile_picture ? (
                <img
                  src={user.profile_picture}
                  alt={user.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <span className="text-gray-400 text-xl md:text-3xl">👤</span>
              )}
            </div>
            
            {/* Profile Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-xl md:text-3xl font-bold text-white mb-1 md:mb-2 truncate">
                {user.name || user.email?.split('@')[0]}
              </h1>
              <p className="text-gray-400 mb-2 md:mb-4 text-sm md:text-base truncate">{user.email}</p>
              
              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-2 md:gap-4">
                <div className="bg-gray-800 rounded-lg p-2 md:p-3">
                  <div className="text-lg md:text-xl font-bold text-white">{collectionStats.totalItems}</div>
                  <div className="text-xs text-gray-400">Possédés</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-2 md:p-3">
                  <div className="text-lg md:text-xl font-bold text-green-400">{collectionStats.totalValue}€</div>
                  <div className="text-xs text-gray-400">Valeur estimée</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-2 md:p-3">
                  <div className="text-lg md:text-xl font-bold text-blue-400">{wantedJerseys.length}</div>
                  <div className="text-xs text-gray-400">En recherche</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-2 md:p-3">
                  <div className="text-lg md:text-xl font-bold text-purple-400">{collectionStats.activeListings}</div>
                  <div className="text-xs text-gray-400">En vente</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-2 md:p-3">
                  <div className="text-lg md:text-xl font-bold text-yellow-400">{submittedJerseys.length}</div>
                  <div className="text-xs text-gray-400">Soumis</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-2 md:p-3">
                  <div className="text-lg md:text-xl font-bold text-orange-400">{collectionStats.totalRevenue}€</div>
                  <div className="text-xs text-gray-400">Revenus</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-gray-900 border-b border-gray-700">
        <div className="container mx-auto px-4 md:px-6">
          <nav className="flex space-x-4 md:space-x-8 overflow-x-auto scrollbar-hide">
            <button
              onClick={() => setActiveTab('collection')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'collection'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Ma Collection ({ownedJerseys.length})
            </button>
            <button
              onClick={() => setActiveTab('wishlist')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'wishlist'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Ma Wishlist ({wantedJerseys.length})
            </button>
            <button
              onClick={() => setActiveTab('submitted')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'submitted'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Mes Soumissions ({submittedJerseys.length})
            </button>
            <button
              onClick={() => setActiveTab('listings')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'listings'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              💰 Mes Listings ({collectionStats.totalListings})
            </button>
            <button
              onClick={() => setActiveTab('purchases')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'purchases'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              🛒 Mes Achats ({purchaseHistory.length})
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'stats'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Statistiques
            </button>
            <button
              onClick={() => setActiveTab('friends')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'friends'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              👥 Mes Amis ({friendsData.totalFriends})
            </button>
            <button
              onClick={() => setActiveTab('messages')}
              className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                activeTab === 'messages'
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              💬 Messages
            </button>
            {user?.email === 'topkitfr@gmail.com' && (
              <button
                onClick={() => setActiveTab('settings')}
                className={`py-3 md:py-4 px-2 border-b-2 font-medium text-xs md:text-sm whitespace-nowrap flex-shrink-0 ${
                  activeTab === 'settings'
                    ? 'border-white text-white'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                ⚙️ Paramètres
              </button>
            )}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="container mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="text-gray-400">Chargement...</div>
          </div>
        ) : (
          <>
            {activeTab === 'collection' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">Ma Collection</h2>
                  <div className="flex items-center space-x-4 text-sm text-gray-400">
                    <span>{ownedJerseys.length} maillots</span>
                    <span>•</span>
                    <span className="text-green-400 font-semibold">
                      Valeur estimée: {collectionStats.totalValue}€
                    </span>
                  </div>
                </div>
                
                {ownedJerseys.length > 0 ? (
                  renderCollectionList(ownedJerseys, 'owned')
                ) : (
                  <div className="text-center py-12 bg-gray-900 rounded-lg border border-gray-700">
                    <div className="text-gray-400 mb-4">
                      <span className="text-4xl block mb-4">👕</span>
                      Votre collection est vide
                    </div>
                    <p className="text-gray-500 mb-6">
                      Commencez à collectionner en explorant nos maillots disponibles.
                    </p>
                    <button
                      onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'jerseys' }))}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Explorez les maillots
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'wishlist' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">Ma Wishlist</h2>
                  <div className="text-sm text-gray-400">
                    {wantedJerseys.length} maillot{wantedJerseys.length > 1 ? 's' : ''}
                  </div>
                </div>
                
                {wantedJerseys.length > 0 ? (
                  renderCollectionList(wantedJerseys, 'wanted')
                ) : (
                  <div className="text-center py-12 bg-gray-900 rounded-lg border border-gray-700">
                    <div className="text-gray-400 mb-4">
                      <span className="text-4xl block mb-4">💫</span>
                      Votre wishlist est vide
                    </div>
                    <p className="text-gray-500 mb-6">
                      Ajoutez des maillots que vous aimeriez posséder à votre wishlist.
                    </p>
                    <button
                      onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'jerseys' }))}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Explorez les maillots
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'submitted' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">Mes Soumissions</h2>
                  <button
                    onClick={() => setShowSubmitModal(true)}
                    className="bg-white text-black px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors font-semibold flex items-center space-x-2"
                  >
                    <span>➕</span>
                    <span>Soumettre un maillot</span>
                  </button>
                </div>

                {/* Submission Status Summary */}
                {submittedJerseys.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-xl font-bold text-green-400">
                        {submittedJerseys.filter(j => j.status === 'approved').length}
                      </div>
                      <div className="text-xs text-gray-400">Approuvés</div>
                    </div>
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-xl font-bold text-yellow-400">
                        {submittedJerseys.filter(j => j.status === 'pending').length}
                      </div>
                      <div className="text-xs text-gray-400">En attente</div>
                    </div>
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-xl font-bold text-orange-400">
                        {submittedJerseys.filter(j => j.status === 'needs_modification').length}
                      </div>
                      <div className="text-xs text-gray-400">Modifications requises</div>
                    </div>
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-xl font-bold text-red-400">
                        {submittedJerseys.filter(j => j.status === 'rejected').length}
                      </div>
                      <div className="text-xs text-gray-400">Rejetés</div>
                    </div>
                  </div>
                )}
                
                {submittedJerseys.length > 0 ? (
                  <div className="space-y-4">
                    {submittedJerseys.map((jersey) => (
                      <EnhancedSubmissionCard key={jersey.id} jersey={jersey} onResubmit={fetchCollectionData} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 bg-gray-900 rounded-lg border border-gray-700">
                    <div className="text-gray-400 mb-4">
                      <span className="text-4xl block mb-4">📝</span>
                      Aucune soumission
                    </div>
                    <p className="text-gray-500 mb-6">
                      Vous n'avez pas encore soumis de maillots à la base de données.
                    </p>
                    <button
                      onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'submit' }))}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Soumettre un maillot
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'stats' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Statistiques de Collection</h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Collection Value */}
                  <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Estimation de Valeur</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">Valeur totale estimée</span>
                        <span className="text-2xl font-bold text-green-400">{collectionStats.totalValue}€</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">Valeur moyenne par maillot</span>
                        <span className="text-lg font-semibold text-white">{collectionStats.averageValue}€</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">Nombre de maillots</span>
                        <span className="text-lg font-semibold text-white">{collectionStats.totalItems}</span>
                      </div>
                      {collectionStats.mostValuableItem && (
                        <div className="pt-4 border-t border-gray-700">
                          <span className="text-gray-400 text-sm">Maillot le plus précieux</span>
                          <div className="mt-2">
                            <span className="text-white font-medium">
                              {collectionStats.mostValuableItem.jersey?.team} {collectionStats.mostValuableItem.jersey?.season}
                            </span>
                            <span className="text-green-400 font-bold ml-2">~250€</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Collection Breakdown */}
                  <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Répartition</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">Maillots possédés</span>
                        <span className="text-white font-semibold">{ownedJerseys.length}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">En wishlist</span>
                        <span className="text-white font-semibold">{wantedJerseys.length}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">Soumissions approuvées</span>
                        <span className="text-white font-semibold">
                          {submittedJerseys.filter(j => j.status === 'approved').length}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">Soumissions en attente</span>
                        <span className="text-white font-semibold">
                          {submittedJerseys.filter(j => j.status === 'pending').length}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional stats could go here */}
                <div className="mt-8 bg-gray-900 rounded-lg border border-gray-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Activité Récente</h3>
                  <div className="text-gray-400 text-center py-8">
                    <span className="text-2xl block mb-4">📊</span>
                    Les statistiques détaillées seront bientôt disponibles
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'listings' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">💰 Mes Listings</h2>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-400">{collectionStats.totalListings} listing{collectionStats.totalListings > 1 ? 's' : ''}</span>
                    <span className="text-gray-400">•</span>
                    <span className="text-purple-400 font-semibold">{collectionStats.activeListings} actif{collectionStats.activeListings > 1 ? 's' : ''}</span>
                    <span className="text-gray-400">•</span>
                    <span className="text-green-400 font-semibold">{collectionStats.totalRevenue}€ de revenus</span>
                  </div>
                </div>

                {/* Listings Status Summary */}
                {userListings.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400 mb-2">{collectionStats.totalListings}</div>
                        <div className="text-xs text-gray-400">Total listings</div>
                      </div>
                    </div>
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400 mb-2">{collectionStats.activeListings}</div>
                        <div className="text-xs text-gray-400">En vente</div>
                      </div>
                    </div>
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-400 mb-2">{collectionStats.soldListings}</div>
                        <div className="text-xs text-gray-400">Vendus</div>
                      </div>
                    </div>
                    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400 mb-2">{collectionStats.totalRevenue}€</div>
                        <div className="text-xs text-gray-400">Revenus totaux</div>
                      </div>
                    </div>
                  </div>
                )}

                {userListings.length > 0 ? (
                  <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
                    {/* Desktop Table View */}
                    <div className="hidden md:block">
                      <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                        <div className="grid grid-cols-7 gap-4 text-xs font-medium text-gray-300 uppercase tracking-wider">
                          <div className="col-span-2">Maillot</div>
                          <div>Taille</div>
                          <div>Condition</div>
                          <div>Prix</div>
                          <div>Status</div>
                          <div>Actions</div>
                        </div>
                      </div>
                      <div className="divide-y divide-gray-700">
                        {userListings.map((listing, index) => (
                          <div key={listing.id} className="px-6 py-4 hover:bg-gray-800 transition-colors">
                            <div className="grid grid-cols-7 gap-4 items-center">
                              {/* Jersey Info */}
                              <div className="col-span-2 flex items-center space-x-3">
                                <div className="w-12 h-12 bg-gray-700 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                                  {listing.jersey?.images && listing.jersey.images.length > 0 ? (
                                    <img
                                      src={listing.jersey.images[0]}
                                      alt={`${listing.jersey.team} ${listing.jersey.season}`}
                                      className="w-full h-full object-cover"
                                      onError={(e) => {
                                        e.target.src = 'https://dummyimage.com/48x48/333/fff.png&text=Jersey';
                                      }}
                                    />
                                  ) : (
                                    <span className="text-gray-500 text-lg">👕</span>
                                  )}
                                </div>
                                <div className="min-w-0 flex-1">
                                  <h3 className="text-white font-medium text-sm truncate">
                                    {listing.jersey?.player ? `${listing.jersey.team} - ${listing.jersey.player}` : listing.jersey?.team}
                                  </h3>
                                  <div className="text-gray-400 text-xs truncate">
                                    {listing.jersey?.season} • {listing.jersey?.home_away}
                                  </div>
                                </div>
                              </div>
                              
                              {/* Size */}
                              <div className="text-white text-sm">{listing.jersey?.size}</div>
                              
                              {/* Condition */}
                              <div>
                                <span className={`px-2 py-1 text-xs font-medium rounded ${
                                  listing.jersey?.condition === 'new' ? 'bg-green-800 text-green-200' :
                                  listing.jersey?.condition === 'near_mint' ? 'bg-blue-800 text-blue-200' :
                                  listing.jersey?.condition === 'very_good' ? 'bg-yellow-800 text-yellow-200' :
                                  listing.jersey?.condition === 'good' ? 'bg-orange-800 text-orange-200' :
                                  'bg-red-800 text-red-200'
                                }`}>
                                  {listing.jersey?.condition === 'new' ? 'Neuf' :
                                   listing.jersey?.condition === 'near_mint' ? 'Quasi-neuf' :
                                   listing.jersey?.condition === 'very_good' ? 'Très bon' :
                                   listing.jersey?.condition === 'good' ? 'Bon' : 'Correct'}
                                </span>
                              </div>
                              
                              {/* Price */}
                              <div className="text-green-400 font-semibold">{listing.price}€</div>
                              
                              {/* Status */}
                              <div>
                                <span className={`px-2 py-1 text-xs font-medium rounded ${
                                  listing.status === 'active' ? 'bg-green-800 text-green-200' :
                                  listing.status === 'sold' ? 'bg-blue-800 text-blue-200' :
                                  listing.status === 'paused' ? 'bg-yellow-800 text-yellow-200' :
                                  'bg-gray-800 text-gray-200'
                                }`}>
                                  {listing.status === 'active' ? 'Actif' :
                                   listing.status === 'sold' ? 'Vendu' :
                                   listing.status === 'paused' ? 'Suspendu' : listing.status}
                                </span>
                              </div>
                              
                              {/* Actions */}
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => window.dispatchEvent(new CustomEvent('changeView', { 
                                    detail: `jersey-detail-${listing.jersey?.reference_number || listing.jersey?.id}` 
                                  }))}
                                  className="text-blue-400 hover:text-blue-300 text-xs"
                                  title="Voir le détail"
                                >
                                  👁️
                                </button>
                                {listing.status === 'active' && (
                                  <button
                                    className="text-yellow-400 hover:text-yellow-300 text-xs"
                                    title="Modifier"
                                  >
                                    ✏️
                                  </button>
                                )}
                                <button
                                  className="text-red-400 hover:text-red-300 text-xs"
                                  title="Retirer"
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Mobile Card View */}
                    <div className="md:hidden space-y-3 p-4">
                      {userListings.map((listing, index) => (
                        <div key={listing.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                          <div className="flex items-start space-x-3">
                            {/* Mobile Image */}
                            <div className="w-16 h-16 bg-gray-700 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                              {listing.jersey?.images && listing.jersey.images.length > 0 ? (
                                <img
                                  src={listing.jersey.images[0]}
                                  alt={`${listing.jersey.team} ${listing.jersey.season}`}
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    e.target.src = 'https://dummyimage.com/64x64/333/fff.png&text=Jersey';
                                  }}
                                />
                              ) : (
                                <span className="text-gray-500 text-xl">👕</span>
                              )}
                            </div>
                            
                            {/* Mobile Content */}
                            <div className="flex-1 min-w-0">
                              <h3 className="text-white font-medium text-sm truncate">
                                {listing.jersey?.player ? `${listing.jersey.team} - ${listing.jersey.player}` : listing.jersey?.team}
                              </h3>
                              <div className="text-gray-400 text-xs mt-1">
                                {listing.jersey?.league} • {listing.jersey?.season} • {listing.jersey?.home_away}
                              </div>
                              
                              {/* Mobile Details Row */}
                              <div className="flex items-center space-x-4 mt-2">
                                <span className="text-white text-xs">
                                  <span className="text-gray-400">Taille:</span> {listing.jersey?.size}
                                </span>
                                <span className="text-green-400 font-semibold text-sm">
                                  {listing.price}€
                                </span>
                                <span className={`px-2 py-1 text-xs font-medium rounded ${
                                  listing.status === 'active' ? 'bg-green-800 text-green-200' :
                                  listing.status === 'sold' ? 'bg-blue-800 text-blue-200' :
                                  listing.status === 'paused' ? 'bg-yellow-800 text-yellow-200' :
                                  'bg-gray-800 text-gray-200'
                                }`}>
                                  {listing.status === 'active' ? 'Actif' :
                                   listing.status === 'sold' ? 'Vendu' :
                                   listing.status === 'paused' ? 'Suspendu' : listing.status}
                                </span>
                              </div>
                              
                              {/* Mobile Actions */}
                              <div className="flex items-center space-x-3 mt-3">
                                <button
                                  onClick={() => window.dispatchEvent(new CustomEvent('changeView', { 
                                    detail: `jersey-detail-${listing.jersey?.reference_number || listing.jersey?.id}` 
                                  }))}
                                  className="text-blue-400 hover:text-blue-300 text-xs px-2 py-1 bg-blue-900/30 rounded"
                                >
                                  👁️ Voir
                                </button>
                                {listing.status === 'active' && (
                                  <button className="text-yellow-400 hover:text-yellow-300 text-xs px-2 py-1 bg-yellow-900/30 rounded">
                                    ✏️ Modifier
                                  </button>
                                )}
                                <button className="text-red-400 hover:text-red-300 text-xs px-2 py-1 bg-red-900/30 rounded">
                                  🗑️ Retirer
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 bg-gray-900 rounded-lg border border-gray-700">
                    <div className="text-gray-400 mb-4">
                      <span className="text-4xl block mb-4">💰</span>
                      Aucun listing actuel
                    </div>
                    <p className="text-gray-500 mb-6">
                      Vous n'avez pas encore créé de listing de vente.
                    </p>
                    <button
                      onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'jerseys' }))}
                      className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Parcourir pour vendre
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Purchases Tab */}
            {activeTab === 'purchases' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">🛒 Mes Achats</h2>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-400">{purchaseHistory.length} achat{purchaseHistory.length > 1 ? 's' : ''}</span>
                    <span className="text-gray-400">•</span>
                    <span className="text-green-400 font-semibold">
                      {purchaseHistory.reduce((sum, purchase) => sum + purchase.amount_paid, 0).toFixed(2)}€ dépensés
                    </span>
                  </div>
                </div>

                {purchaseHistory.length > 0 ? (
                  <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
                    {/* Desktop Table View */}
                    <div className="hidden md:block">
                      <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                        <div className="grid grid-cols-7 gap-4 text-xs font-medium text-gray-300 uppercase tracking-wider">
                          <div className="col-span-2">Maillot</div>
                          <div>Vendeur</div>
                          <div>Taille</div>
                          <div>Condition</div>
                          <div>Prix payé</div>
                          <div>Date d'achat</div>
                        </div>
                      </div>
                      <div className="divide-y divide-gray-700">
                        {purchaseHistory.map((purchase, index) => (
                          <div key={purchase.transaction_id} className="px-6 py-4 hover:bg-gray-800 transition-colors">
                            <div className="grid grid-cols-7 gap-4 items-center">
                              {/* Jersey Info */}
                              <div className="col-span-2 flex items-center space-x-3">
                                <div className="w-12 h-12 bg-gray-700 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                                  <span className="text-gray-500 text-lg">👕</span>
                                </div>
                                <div className="min-w-0 flex-1">
                                  <h3 className="text-white font-medium text-sm truncate">
                                    {purchase.jersey_info.player ? 
                                      `${purchase.jersey_info.team} - ${purchase.jersey_info.player}` : 
                                      purchase.jersey_info.team
                                    }
                                  </h3>
                                  <div className="text-gray-400 text-xs truncate">
                                    {purchase.jersey_info.season}
                                  </div>
                                </div>
                              </div>
                              
                              {/* Seller */}
                              <div className="text-white text-sm truncate">{purchase.seller_info.name}</div>
                              
                              {/* Size */}
                              <div className="text-white text-sm">{purchase.jersey_info.size}</div>
                              
                              {/* Condition */}
                              <div>
                                <span className={`px-2 py-1 text-xs font-medium rounded ${
                                  purchase.jersey_info.condition === 'new' ? 'bg-green-800 text-green-200' :
                                  purchase.jersey_info.condition === 'near_mint' ? 'bg-blue-800 text-blue-200' :
                                  purchase.jersey_info.condition === 'very_good' ? 'bg-yellow-800 text-yellow-200' :
                                  purchase.jersey_info.condition === 'good' ? 'bg-orange-800 text-orange-200' :
                                  'bg-red-800 text-red-200'
                                }`}>
                                  {purchase.jersey_info.condition === 'new' ? 'Neuf' :
                                   purchase.jersey_info.condition === 'near_mint' ? 'Quasi-neuf' :
                                   purchase.jersey_info.condition === 'very_good' ? 'Très bon' :
                                   purchase.jersey_info.condition === 'good' ? 'Bon' : 'Correct'}
                                </span>
                              </div>
                              
                              {/* Price */}
                              <div className="text-green-400 font-semibold text-sm">
                                {purchase.amount_paid.toFixed(2)}€
                              </div>
                              
                              {/* Purchase Date */}
                              <div className="text-gray-400 text-sm">
                                {new Date(purchase.purchase_date).toLocaleDateString('fr-FR')}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Mobile Card View */}
                    <div className="md:hidden divide-y divide-gray-700">
                      {purchaseHistory.map((purchase, index) => (
                        <div key={purchase.transaction_id} className="p-4">
                          <div className="flex items-start space-x-3">
                            <div className="w-16 h-16 bg-gray-700 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                              <span className="text-gray-500 text-xl">👕</span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="text-white font-medium mb-1">
                                {purchase.jersey_info.player ? 
                                  `${purchase.jersey_info.team} - ${purchase.jersey_info.player}` : 
                                  purchase.jersey_info.team
                                }
                              </h3>
                              <div className="text-gray-400 text-sm mb-2">
                                {purchase.jersey_info.season} • Taille {purchase.jersey_info.size}
                              </div>
                              <div className="flex items-center justify-between">
                                <div className="text-green-400 font-semibold">
                                  {purchase.amount_paid.toFixed(2)}€
                                </div>
                                <div className="text-gray-400 text-sm">
                                  {new Date(purchase.purchase_date).toLocaleDateString('fr-FR')}
                                </div>
                              </div>
                              <div className="text-gray-400 text-sm mt-1">
                                Vendeur: {purchase.seller_info.name}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-900 rounded-lg border border-gray-700 p-12">
                    <div className="text-center">
                      <div className="text-gray-400 mb-4">
                        <span className="text-6xl block mb-4">🛒</span>
                        Aucun achat pour le moment
                      </div>
                      <p className="text-gray-500 mb-6">
                        Vous n'avez pas encore acheté de maillots sur TopKit. Explorez notre marketplace pour découvrir des pièces uniques !
                      </p>
                      <button
                        onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'marketplace' }))}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                      >
                        Explorer la Marketplace
                      </button>
                    </div>
                  </div>
                )}

                {/* Sales History Section */}
                {salesHistory.length > 0 && (
                  <div className="mt-8">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-white">💰 Mes Ventes</h3>
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="text-gray-400">{salesHistory.length} vente{salesHistory.length > 1 ? 's' : ''}</span>
                        <span className="text-gray-400">•</span>
                        <span className="text-green-400 font-semibold">
                          {salesHistory.reduce((sum, sale) => sum + sale.net_amount, 0).toFixed(2)}€ reçus
                        </span>
                      </div>
                    </div>

                    <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
                      {/* Desktop Table View */}
                      <div className="hidden md:block">
                        <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                          <div className="grid grid-cols-7 gap-4 text-xs font-medium text-gray-300 uppercase tracking-wider">
                            <div className="col-span-2">Maillot</div>
                            <div>Acheteur</div>
                            <div>Prix brut</div>
                            <div>Commission</div>
                            <div>Montant net</div>
                            <div>Date de vente</div>
                          </div>
                        </div>
                        <div className="divide-y divide-gray-700">
                          {salesHistory.map((sale, index) => (
                            <div key={sale.transaction_id} className="px-6 py-4 hover:bg-gray-800 transition-colors">
                              <div className="grid grid-cols-7 gap-4 items-center">
                                {/* Jersey Info */}
                                <div className="col-span-2 flex items-center space-x-3">
                                  <div className="w-12 h-12 bg-gray-700 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                                    <span className="text-gray-500 text-lg">👕</span>
                                  </div>
                                  <div className="min-w-0 flex-1">
                                    <h3 className="text-white font-medium text-sm truncate">
                                      {sale.jersey_info.player ? 
                                        `${sale.jersey_info.team} - ${sale.jersey_info.player}` : 
                                        sale.jersey_info.team
                                      }
                                    </h3>
                                    <div className="text-gray-400 text-xs truncate">
                                      {sale.jersey_info.season}
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Buyer */}
                                <div className="text-white text-sm truncate">{sale.buyer_info.name}</div>
                                
                                {/* Gross Amount */}
                                <div className="text-white text-sm font-medium">
                                  {sale.gross_amount.toFixed(2)}€
                                </div>
                                
                                {/* Commission */}
                                <div className="text-red-400 text-sm">
                                  -{sale.commission_amount.toFixed(2)}€
                                </div>
                                
                                {/* Net Amount */}
                                <div className="text-green-400 font-semibold text-sm">
                                  {sale.net_amount.toFixed(2)}€
                                </div>
                                
                                {/* Sale Date */}
                                <div className="text-gray-400 text-sm">
                                  {new Date(sale.sale_date).toLocaleDateString('fr-FR')}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Friends Tab */}
            {activeTab === 'friends' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">👥 Mes Amis</h2>
                
                {/* Friends Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-400 mb-2">{friendsData.totalFriends}</div>
                      <div className="text-gray-400">Amis</div>
                    </div>
                  </div>
                  <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-400 mb-2">{friendsData.pendingReceived.length}</div>
                      <div className="text-gray-400">Demandes reçues</div>
                    </div>
                  </div>
                  <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-400 mb-2">{friendsData.pendingSent.length}</div>
                      <div className="text-gray-400">Demandes envoyées</div>
                    </div>
                  </div>
                </div>

                {/* Friends Sub-tabs */}
                <div className="mb-6">
                  <nav className="flex space-x-4">
                    <button
                      onClick={() => setFriendsActiveTab('friends')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        friendsActiveTab === 'friends'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      Mes Amis ({friendsData.totalFriends})
                    </button>
                    <button
                      onClick={() => setFriendsActiveTab('received')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        friendsActiveTab === 'received'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      Demandes reçues ({friendsData.pendingReceived.length})
                    </button>
                    <button
                      onClick={() => setFriendsActiveTab('sent')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        friendsActiveTab === 'sent'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      Demandes envoyées ({friendsData.pendingSent.length})
                    </button>
                  </nav>
                </div>

                {/* Friends Content */}
                <div className="bg-gray-900 rounded-lg border border-gray-700">
                  {friendsActiveTab === 'friends' && (
                    <div className="p-6">
                      {friendsData.friends.length === 0 ? (
                        <div className="text-center py-12">
                          <div className="text-gray-400 mb-4">
                            <span className="text-4xl block mb-4">👥</span>
                            Aucun ami pour le moment
                          </div>
                          <p className="text-gray-500 mb-6">
                            Commencez à construire votre réseau en recherchant d'autres collectionneurs
                          </p>
                          <button
                            onClick={() => window.dispatchEvent(new CustomEvent('changeView', { detail: 'friends' }))}
                            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Trouver des amis
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {friendsData.friends.map((friend) => (
                            <div key={friend.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700">
                              <div className="flex items-center space-x-4">
                                <img
                                  src={friend.picture || 'https://dummyimage.com/40x40/666/fff.png&text=👤'}
                                  alt={friend.name}
                                  className="w-10 h-10 rounded-full"
                                />
                                <div>
                                  <h3 className="text-white font-medium">{friend.name}</h3>
                                  <p className="text-gray-400 text-sm">Ami depuis {new Date(friend.created_at).toLocaleDateString()}</p>
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => {
                                    window.dispatchEvent(new CustomEvent('changeView', { detail: 'user-profile' }));
                                    window.dispatchEvent(new CustomEvent('setSelectedUserId', { detail: friend.id }));
                                  }}
                                  className="bg-gray-700 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 transition-colors"
                                >
                                  Voir profil
                                </button>
                                <button
                                  onClick={() => {
                                    window.dispatchEvent(new CustomEvent('changeView', { detail: 'messages' }));
                                    window.dispatchEvent(new CustomEvent('startConversation', { detail: friend.id }));
                                  }}
                                  className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                                >
                                  Message
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {friendsActiveTab === 'received' && (
                    <div className="p-6">
                      {friendsData.pendingReceived.length === 0 ? (
                        <div className="text-center py-12">
                          <div className="text-gray-400 mb-4">
                            <span className="text-4xl block mb-4">📥</span>
                            Aucune demande d'ami en attente
                          </div>
                          <p className="text-gray-500">
                            Les demandes d'ami que vous recevez apparaîtront ici
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {friendsData.pendingReceived.map((request) => (
                            <div key={request.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700">
                              <div className="flex items-center space-x-4">
                                <img
                                  src={request.picture || 'https://dummyimage.com/40x40/666/fff.png&text=👤'}
                                  alt={request.name}
                                  className="w-10 h-10 rounded-full"
                                />
                                <div>
                                  <h3 className="text-white font-medium">{request.name}</h3>
                                  <p className="text-gray-400 text-sm">Demande envoyée le {new Date(request.requested_at).toLocaleDateString()}</p>
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleFriendResponse(request.id, true)}
                                  className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 transition-colors"
                                >
                                  Accepter
                                </button>
                                <button
                                  onClick={() => handleFriendResponse(request.id, false)}
                                  className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700 transition-colors"
                                >
                                  Refuser
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {friendsActiveTab === 'sent' && (
                    <div className="p-6">
                      {friendsData.pendingSent.length === 0 ? (
                        <div className="text-center py-12">
                          <div className="text-gray-400 mb-4">
                            <span className="text-4xl block mb-4">📤</span>
                            Aucune demande d'ami envoyée
                          </div>
                          <p className="text-gray-500">
                            Les demandes d'ami que vous envoyez apparaîtront ici
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {friendsData.pendingSent.map((request) => (
                            <div key={request.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700">
                              <div className="flex items-center space-x-4">
                                <img
                                  src={request.picture || 'https://dummyimage.com/40x40/666/fff.png&text=👤'}
                                  alt={request.name}
                                  className="w-10 h-10 rounded-full"
                                />
                                <div>
                                  <h3 className="text-white font-medium">{request.name}</h3>
                                  <p className="text-gray-400 text-sm">Demande envoyée le {new Date(request.requested_at).toLocaleDateString()}</p>
                                </div>
                              </div>
                              <div className="text-gray-400 text-sm">
                                En attente...
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Messages Tab */}
            {activeTab === 'messages' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">💬 Messages</h2>
                <MessagingInterface />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Collections Page Component
const CollectionsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('collection');
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
      ) : activeTab === 'settings' ? (
        <div>
          <h2 className="text-xl font-bold text-white mb-6">
            ⚙️ Site Settings & Privacy Control
          </h2>
          
          {/* Site Mode Control */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Mode du Site</h3>
                <p className="text-gray-400 text-sm">
                  Contrôlez qui peut accéder à TopKit. En mode privé, seuls les utilisateurs autorisés peuvent accéder au site.
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${siteMode === 'private' ? 'bg-red-400' : 'bg-green-400'}`}></div>
                <span className="text-white font-medium capitalize">{siteMode}</span>
              </div>
            </div>
            
            {/* Current Status */}
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400">État Actuel</label>
                  <div className="text-white font-medium">
                    {siteMode === 'private' ? (
                      <span className="text-red-400">🔒 Site en Mode Privé</span>
                    ) : (
                      <span className="text-green-400">🌐 Site Public</span>
                    )}
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Accès</label>
                  <div className="text-white text-sm">
                    {siteMode === 'private' ? (
                      'Admins et utilisateurs autorisés uniquement'
                    ) : (
                      'Accessible à tous les visiteurs'
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Mode Toggle Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={() => updateSiteMode('public')}
                disabled={siteSettingsLoading || siteMode === 'public'}
                className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                  siteMode === 'public'
                    ? 'bg-green-600 text-white cursor-not-allowed'
                    : 'bg-gray-700 text-gray-300 hover:bg-green-600 hover:text-white'
                } ${siteSettingsLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {siteSettingsLoading && siteMode !== 'public' ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Activation...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    🌐 Mode Public
                    {siteMode === 'public' && <span className="ml-2 text-xs">(Actuel)</span>}
                  </span>
                )}
              </button>
              
              <button
                onClick={() => updateSiteMode('private')}
                disabled={siteSettingsLoading || siteMode === 'private'}
                className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                  siteMode === 'private'
                    ? 'bg-red-600 text-white cursor-not-allowed'
                    : 'bg-gray-700 text-gray-300 hover:bg-red-600 hover:text-white'
                } ${siteSettingsLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {siteSettingsLoading && siteMode !== 'private' ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Activation...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    🔒 Mode Privé (Bêta)
                    {siteMode === 'private' && <span className="ml-2 text-xs">(Actuel)</span>}
                  </span>
                )}
              </button>
            </div>
            
            {/* Information Box */}
            <div className="mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
              <div className="flex items-start space-x-3">
                <div className="text-blue-400 text-lg">💡</div>
                <div>
                  <h4 className="text-blue-300 font-medium mb-1">Information</h4>
                  <p className="text-blue-200 text-sm">
                    <strong>Mode Privé :</strong> Seuls l'administrateur et les utilisateurs avec <code className="bg-blue-800 px-1 rounded text-xs">beta_access: true</code> peuvent accéder au site.
                    <br />
                    <strong>Mode Public :</strong> Le site est accessible à tous les visiteurs.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Deployment Info */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">🚀 Informations de Déploiement</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-white font-medium mb-2">État du Site</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Mode:</span>
                    <span className="text-white capitalize">{siteMode}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Statut:</span>
                    <span className="text-green-400">Opérationnel</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Base de données:</span>
                    <span className="text-green-400">Connectée</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Paiements:</span>
                    <span className="text-green-400">Stripe Configuré</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="text-white font-medium mb-2">Sécurité</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Authentification:</span>
                    <span className="text-green-400">JWT Active</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Validation Email:</span>
                    <span className="text-green-400">Activée</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Rate Limiting:</span>
                    <span className="text-green-400">Active</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Mots de passe:</span>
                    <span className="text-green-400">Sécurisés</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="text-green-400">✅</div>
                <span className="text-green-300 text-sm font-medium">TopKit est prêt pour le déploiement en production</span>
              </div>
            </div>
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
          src={jersey.images?.[0] || 'https://dummyimage.com/300x400/333/fff.png&text=Jersey+Image'}
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
        src={listing.images?.[0] || listing.jersey?.images?.[0] || 'https://dummyimage.com/300x400/333/fff.png&text=Jersey+Image'}
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
  const { user, loading: authLoading } = useAuth();
  const [currentView, setCurrentView] = useState('home');
  const [jerseys, setJerseys] = useState([]);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateListing, setShowCreateListing] = useState(false);
  const [showAddJersey, setShowAddJersey] = useState(false); // For adding new jerseys
  const [showSubmitModal, setShowSubmitModal] = useState(false); // For submitting new jerseys
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
  
  // Shopping Cart State
  const [cart, setCart] = useState([]);
  
  // Load cart from localStorage on app start
  useEffect(() => {
    const savedCart = localStorage.getItem('topkit_cart');
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
        setCart([]);
      }
    }
  }, []);
  
  // Save cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('topkit_cart', JSON.stringify(cart));
  }, [cart]);
  
  // Cart management functions
  const addToCart = (listing, quantity = 1) => {
    const cartItem = {
      id: `${listing.jersey.id}-${listing.size}-${listing.id}`,
      jerseyId: listing.jersey.id,
      listingId: listing.id,
      team: listing.jersey.team,
      season: listing.jersey.season,
      player: listing.jersey.player,
      size: listing.size,
      condition: listing.condition,
      manufacturer: listing.jersey.manufacturer,
      images: listing.jersey.images || [],
      price: listing.price,
      sellerId: listing.user.id,
      sellerName: listing.user.name,
      quantity: quantity
    };
    
    // Check if item already exists in cart
    const existingItemIndex = cart.findIndex(item => item.id === cartItem.id);
    
    if (existingItemIndex >= 0) {
      // Update quantity if item exists
      const newCart = [...cart];
      newCart[existingItemIndex].quantity += quantity;
      setCart(newCart);
    } else {
      // Add new item to cart
      setCart([...cart, cartItem]);
    }
    
    // Show success notification
    console.log('Article ajouté au panier:', cartItem.team, cartItem.season);
  };
  
  const removeFromCart = (itemToRemove) => {
    setCart(cart.filter(item => item.id !== itemToRemove.id));
  };
  
  const updateCartItemQuantity = (itemToUpdate, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(itemToUpdate);
      return;
    }
    
    setCart(cart.map(item => 
      item.id === itemToUpdate.id 
        ? { ...item, quantity: newQuantity }
        : item
    ));
  };
  
  const clearCart = () => {
    setCart([]);
  };
  
  const getCartCount = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

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
      // First, check if user already has this jersey in any collection
      const [ownedRes, wantedRes] = await Promise.all([
        axios.get(`${API}/api/collections/owned`, {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(() => ({ data: [] })),
        axios.get(`${API}/api/collections/wanted`, {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(() => ({ data: [] }))
      ]);
      
      const isInOwned = ownedRes.data.some(item => item.jersey.id === jerseyId);
      const isInWanted = wantedRes.data.some(item => item.jersey.id === jerseyId);
      
      // If trying to add to same collection type and already there, remove it
      if ((collectionType === 'owned' && isInOwned) || (collectionType === 'wanted' && isInWanted)) {
        await axios.post(`${API}/api/collections/remove`, 
          { jersey_id: jerseyId, collection_type: collectionType },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const actionText = collectionType === 'owned' ? 'votre collection' : 'votre wishlist';
        alert(`✅ Maillot retiré de ${actionText} !`);
        return;
      }
      
      // If in other collection type, remove from there first
      if (collectionType === 'owned' && isInWanted) {
        await axios.post(`${API}/api/collections/remove`, 
          { jersey_id: jerseyId, collection_type: 'wanted' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else if (collectionType === 'wanted' && isInOwned) {
        await axios.post(`${API}/api/collections/remove`, 
          { jersey_id: jerseyId, collection_type: 'owned' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }
      
      // Add to new collection
      await axios.post(`${API}/api/collections`, 
        { jersey_id: jerseyId, collection_type: collectionType },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const actionText = collectionType === 'owned' ? 'votre collection' : 'votre wishlist';
      alert(`✅ Maillot ajouté à ${actionText} !`);
      
    } catch (error) {
      console.error('Collection action error:', error);
      alert(error.response?.data?.detail || 'Erreur lors de la gestion de la collection');
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
      setCurrentView('user-profile');
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

  // Helper function to extract jersey identifier from currentView
  const getJerseyIdentifier = (viewString, prefix) => {
    const identifier = viewString.replace(prefix, '');
    return {
      isReference: identifier.startsWith('TK-'),
      jerseyId: identifier.startsWith('TK-') ? null : identifier,
      referenceNumber: identifier.startsWith('TK-') ? identifier : null
    };
  };

  const renderContent = () => {
    // Handle jersey detail pages with reference numbers
    if (currentView.startsWith('jersey-detail-')) {
      const { jerseyId, referenceNumber } = getJerseyIdentifier(currentView, 'jersey-detail-');
      return (
        <JerseyDetailPage 
          jerseyId={jerseyId}
          referenceNumber={referenceNumber}
        />
      );
    }
    
    // Handle jersey marketplace pages with reference numbers
    if (currentView.startsWith('jersey-marketplace-')) {
      const { jerseyId, referenceNumber } = getJerseyIdentifier(currentView, 'jersey-marketplace-');
      return (
        <JerseyMarketplacePage 
          jerseyId={jerseyId}
          referenceNumber={referenceNumber}
        />
      );
    }

    switch (currentView) {
      case 'profile':
        return <ProfileCollectionPage setShowSubmitModal={setShowSubmitModal} />;
        
      case 'settings':
        return <AdvancedSettingsPage />;
        
      case 'user-profile':
        return <UserProfilePage selectedUserId={selectedUserId} onBack={() => setCurrentView('home')} />;
        
      case 'friends':
        return <FriendsPage onViewUserProfile={(userId) => { setSelectedUserId(userId); setCurrentView('user-profile'); }} />;
        
      case 'messages':
        return <MessagesPage />;
      
      case 'submit':
        return <SubmitJerseyPage />;
      
      case 'admin':
        return <AdminPanel />;
      
      case 'marketplace':
        return (
          <GlobalMarketplacePage
            onAddToCart={addToCart}
          />
        );
      
      case 'jerseys':
        return (
          <BrowseJerseysPage 
            jerseys={jerseys}
            loading={loading}
            onFilter={fetchJerseys}
            onAddToCollection={handleAddToCollection}
            onJerseyClick={handleJerseyClick}
            onCreatorClick={handleCreatorClick}
            onViewUserProfile={(userId) => { setSelectedUserId(userId); setCurrentView('user-profile'); }}
          />
        );
      
      case 'cart':
        return (
          <ShoppingCartPage
            cart={cart}
            setCart={setCart}
            onRemoveFromCart={removeFromCart}
            onUpdateQuantity={updateCartItemQuantity}
            onClearCart={clearCart}
          />
        );
      
// Discogs-Style Homepage Component
const DiscogsStyleHomepage = ({ onNavigate }) => {
  const [featuredJerseys, setFeaturedJerseys] = useState([]);
  const [trendingJerseys, setTrendingJerseys] = useState([]);
  const [staffPicks, setStaffPicks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHomepageData();
  }, []);

  const fetchHomepageData = async () => {
    try {
      setLoading(true);
      
      // Fetch different sections of content
      const [featuredResponse, trendingResponse, staffPicksResponse] = await Promise.all([
        axios.get(`${API}/api/explorer/latest-additions?limit=8`).catch(() => ({ data: [] })),
        axios.get(`${API}/api/explorer/most-collected?limit=6`).catch(() => ({ data: [] })),
        axios.get(`${API}/api/explorer/most-wanted?limit=6`).catch(() => ({ data: [] }))
      ]);

      setFeaturedJerseys(featuredResponse.data || []);
      setTrendingJerseys(trendingResponse.data || []);
      setStaffPicks(staffPicksResponse.data || []);
    } catch (error) {
      console.error('Failed to fetch homepage data:', error);
      // Set empty arrays as fallback
      setFeaturedJerseys([]);
      setTrendingJerseys([]);
      setStaffPicks([]);
    } finally {
      setLoading(false);
    }
  };

  const JerseyCard = ({ jersey, size = 'normal' }) => (
    <div
      className={`bg-gray-900 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-all cursor-pointer group hover:shadow-xl ${
        size === 'large' ? 'col-span-2 row-span-2' : ''
      }`}
      onClick={() => onNavigate('jerseys')}
    >
      <div className={`bg-gray-800 overflow-hidden ${size === 'large' ? 'aspect-square' : 'aspect-[4/3]'}`}>
        {jersey.images?.[0] ? (
          <img
            src={jersey.images[0]}
            alt={jersey.team}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500 text-4xl">
            👕
          </div>
        )}
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
          {jersey.league || 'Football'}
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-white mb-1 truncate">
          {jersey.player ? `${jersey.team} - ${jersey.player}` : jersey.team}
        </h3>
        <p className="text-gray-400 text-sm truncate">{jersey.season}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-500">{jersey.manufacturer}</span>
          {jersey.collection_count > 0 && (
            <span className="text-xs text-blue-400">❤️ {jersey.collection_count}</span>
          )}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mb-4"></div>
          <div className="text-gray-400">Chargement de la page d'accueil...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      
      {/* Hero Section with Search */}
      <section className="bg-gradient-to-b from-gray-900 to-black py-16">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Découvrez les maillots <br />
            <span className="text-blue-400">les plus recherchés</span>
          </h1>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            La plus grande base de données de maillots de football au monde. 
            Achetez, vendez et collectionnez avec des passionnés du monde entier.
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="relative">
              <input
                type="text"
                placeholder="Rechercher par équipe, joueur, championnat..."
                className="w-full bg-gray-800 text-white placeholder-gray-400 border border-gray-600 rounded-xl px-6 py-4 pr-16 text-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => onNavigate('jerseys')}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <button
              onClick={() => onNavigate('jerseys')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              🔍 Explorez la base de données
            </button>
            <button
              onClick={() => onNavigate('marketplace')}
              className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              🛒 Marketplace
            </button>
            <button
              onClick={() => onNavigate('profile')}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              📚 Ma Collection
            </button>
          </div>
        </div>
      </section>

      {/* Latest Additions */}
      <section className="py-16 bg-black">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-3xl font-bold text-white">Derniers ajouts</h2>
            <button
              onClick={() => onNavigate('jerseys')}
              className="text-blue-400 hover:text-white transition-colors font-medium"
            >
              Voir tout →
            </button>
          </div>
          
          {featuredJerseys.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-6">
              {featuredJerseys.slice(0, 8).map((jersey) => (
                <JerseyCard key={jersey.id} jersey={jersey} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">👕</div>
              <p className="text-gray-400 text-lg mb-6">Aucun maillot disponible pour le moment</p>
              <button
                onClick={() => onNavigate('jerseys')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                Explorer la base de données
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Trending & Staff Picks */}
      <section className="py-16 bg-gray-950">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            
            {/* Most Collected */}
            <div>
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold text-white">Plus collectionnés</h2>
                <button
                  onClick={() => onNavigate('jerseys')}
                  className="text-blue-400 hover:text-white transition-colors"
                >
                  Voir tout →
                </button>
              </div>
              
              {trendingJerseys.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {trendingJerseys.slice(0, 6).map((jersey) => (
                    <JerseyCard key={jersey.id} jersey={jersey} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400">Aucun maillot populaire pour le moment</div>
                </div>
              )}
            </div>

            {/* Most Wanted */}
            <div>
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold text-white">Plus recherchés</h2>
                <button
                  onClick={() => onNavigate('jerseys')}
                  className="text-blue-400 hover:text-white transition-colors"
                >
                  Voir tout →
                </button>
              </div>
              
              {staffPicks.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {staffPicks.slice(0, 6).map((jersey) => (
                    <JerseyCard key={jersey.id} jersey={jersey} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400">Aucun maillot recherché pour le moment</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Categories/Leagues */}
      <section className="py-16 bg-black">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">Parcourir par championnat</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {[
              { name: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', color: 'bg-purple-600' },
              { name: 'La Liga', flag: '🇪🇸', color: 'bg-red-600' },
              { name: 'Serie A', flag: '🇮🇹', color: 'bg-green-600' },
              { name: 'Bundesliga', flag: '🇩🇪', color: 'bg-yellow-600' },
              { name: 'Ligue 1', flag: '🇫🇷', color: 'bg-blue-600' },
              { name: 'Champions League', flag: '⚽', color: 'bg-indigo-600' },
              { name: 'Nations', flag: '🌍', color: 'bg-teal-600' },
              { name: 'MLS', flag: '🇺🇸', color: 'bg-orange-600' },
              { name: 'Liga MX', flag: '🇲🇽', color: 'bg-pink-600' },
              { name: 'Autres', flag: '🏆', color: 'bg-gray-600' }
            ].map((league) => (
              <button
                key={league.name}
                onClick={() => onNavigate('jerseys')}
                className={`${league.color} hover:opacity-90 text-white p-6 rounded-xl font-semibold transition-all hover:shadow-lg hover:scale-105`}
              >
                <div className="text-3xl mb-2">{league.flag}</div>
                <div className="text-sm font-medium">{league.name}</div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Statistics */}
      <section className="py-16 bg-gray-950">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-12">TopKit en chiffres</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">50K+</div>
              <div className="text-gray-400">Maillots référencés</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-400 mb-2">15K+</div>
              <div className="text-gray-400">Collectionneurs</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-yellow-400 mb-2">200+</div>
              <div className="text-gray-400">Équipes</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-400 mb-2">30+</div>
              <div className="text-gray-400">Championnats</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

      default:
        return (
          <div className="min-h-screen bg-black">
            {/* Hero Section with Search */}
            <section className="bg-gradient-to-b from-gray-900 to-black py-16">
              <div className="container mx-auto px-6 text-center">
                <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
                  Découvrez les maillots <br />
                  <span className="text-blue-400">les plus recherchés</span>
                </h1>
                <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
                  La plus grande base de données de maillots de football au monde. 
                  Achetez, vendez et collectionnez avec des passionnés du monde entier.
                </p>
                
                {/* Search Bar */}
                <div className="max-w-2xl mx-auto mb-12">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Rechercher par équipe, joueur, championnat..."
                      className="w-full bg-gray-800 text-white placeholder-gray-400 border border-gray-600 rounded-xl px-6 py-4 pr-16 text-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => setCurrentView('jerseys')}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                  <button
                    onClick={() => setCurrentView('jerseys')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
                  >
                    🔍 Explorez la base de données
                  </button>
                  <button
                    onClick={() => setCurrentView('marketplace')}
                    className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
                  >
                    🛒 Marketplace
                  </button>
                  <button
                    onClick={() => setCurrentView('profile')}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
                  >
                    📚 Ma Collection
                  </button>
                </div>
              </div>
            </section>

            {/* Categories/Leagues */}
            <section className="py-16 bg-black">
              <div className="container mx-auto px-6">
                <h2 className="text-3xl font-bold text-white mb-12 text-center">Parcourir par championnat</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                  {[
                    { name: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', color: 'bg-purple-600' },
                    { name: 'La Liga', flag: '🇪🇸', color: 'bg-red-600' },
                    { name: 'Serie A', flag: '🇮🇹', color: 'bg-green-600' },
                    { name: 'Bundesliga', flag: '🇩🇪', color: 'bg-yellow-600' },
                    { name: 'Ligue 1', flag: '🇫🇷', color: 'bg-blue-600' },
                    { name: 'Champions League', flag: '⚽', color: 'bg-indigo-600' },
                    { name: 'Nations', flag: '🌍', color: 'bg-teal-600' },
                    { name: 'MLS', flag: '🇺🇸', color: 'bg-orange-600' },
                    { name: 'Liga MX', flag: '🇲🇽', color: 'bg-pink-600' },
                    { name: 'Autres', flag: '🏆', color: 'bg-gray-600' }
                  ].map((league) => (
                    <button
                      key={league.name}
                      onClick={() => setCurrentView('jerseys')}
                      className={`${league.color} hover:opacity-90 text-white p-6 rounded-xl font-semibold transition-all hover:shadow-lg hover:scale-105`}
                    >
                      <div className="text-3xl mb-2">{league.flag}</div>
                      <div className="text-sm font-medium">{league.name}</div>
                    </button>
                  ))}
                </div>
              </div>
            </section>

            {/* Statistics */}
            <section className="py-16 bg-gray-950">
              <div className="container mx-auto px-6 text-center">
                <h2 className="text-3xl font-bold text-white mb-12">TopKit en chiffres</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                  <div>
                    <div className="text-4xl font-bold text-blue-400 mb-2">50K+</div>
                    <div className="text-gray-400">Maillots référencés</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-green-400 mb-2">15K+</div>
                    <div className="text-gray-400">Collectionneurs</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-yellow-400 mb-2">200+</div>
                    <div className="text-gray-400">Équipes</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-purple-400 mb-2">30+</div>
                    <div className="text-gray-400">Championnats</div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        );
    }
  };

  // Show loading spinner while authentication is being checked
  if (authLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mb-4"></div>
          <div className="text-gray-400">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-black text-white">
        <Header 
          currentView={currentView} 
          setCurrentView={setCurrentView}
          setShowAuthModal={setShowAuthModalFromAction}
          cartCount={getCartCount()}
        />
        
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

        {/* Submit Jersey Modal - Moved to ProfileCollectionPage */}
        {showSubmitModal && (
          <SubmitJerseyModal 
            onClose={() => setShowSubmitModal(false)}
            onSuccess={() => {
              setShowSubmitModal(false);
              // Refresh submissions
              if (user) {
                window.location.reload();
              }
            }}
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

// Admin Edit Jersey Modal Component for Admin Panel
const AdminEditJerseyModal = ({ jersey, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    team: jersey.team || '',
    season: jersey.season || '',
    player: jersey.player || '',
    size: jersey.size || 'M',
    condition: jersey.condition || 'excellent',
    manufacturer: jersey.manufacturer || '',
    home_away: jersey.home_away || 'home',
    league: jersey.league || '',
    description: jersey.description || '',
    reference_code: jersey.reference_code || '',
    images: jersey.images || []
  });
  const [loading, setLoading] = useState(false);
  const [selectedLeague, setSelectedLeague] = useState(jersey.league || '');
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

    try {
      await onSave(formData);
    } catch (error) {
      console.error('Failed to save jersey:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-4xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">✏️ Corriger la soumission</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <div className="text-blue-400 text-xl mr-3 mt-1">ℹ️</div>
            <div>
              <h3 className="text-blue-300 font-semibold mb-2">Mode Correction Admin</h3>
              <p className="text-blue-200 text-sm leading-relaxed">
                Vous pouvez corriger directement les informations soumises par l'utilisateur. 
                Après correction, vous pourrez approuver le jersey en une seule étape.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="border border-gray-700 rounded-lg p-6 bg-gray-800">
            <h3 className="text-lg font-semibold mb-4 text-white">Détails du Maillot</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Ligue*</label>
                <select
                  value={selectedLeague}
                  onChange={(e) => setSelectedLeague(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Sélectionner une ligue</option>
                  {Object.keys(LEAGUES_DATA).map(league => (
                    <option key={league} value={league}>{league}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Club/Équipe nationale*</label>
                <select
                  value={formData.team}
                  onChange={(e) => setFormData({...formData, team: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                  disabled={!selectedLeague}
                >
                  <option value="">Sélectionner une équipe</option>
                  {availableTeams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Saison*</label>
                <select
                  value={formData.season}
                  onChange={(e) => setFormData({...formData, season: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Sélectionner une saison</option>
                  {SEASONS.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Marque/Fabricant*</label>
                <select
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="">Sélectionner une marque</option>
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
                  <option value="Other">Autre</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Nom du joueur</label>
                <input
                  type="text"
                  placeholder="ex: Bruno Fernandes (optionnel)"
                  value={formData.player}
                  onChange={(e) => setFormData({...formData, player: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Code Référence</label>
                <input
                  type="text"
                  placeholder="ex: 779963-01"
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
                  <option value="home">Domicile</option>
                  <option value="away">Extérieur</option>
                  <option value="third">Troisième tenue</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Taille*</label>
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
                <label className="block text-sm font-medium text-gray-300 mb-1">État*</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white"
                  required
                >
                  <option value="new">Neuf</option>
                  <option value="near_mint">Excellent</option>
                  <option value="very_good">Très bon</option>
                  <option value="good">Bon</option>
                  <option value="poor">Acceptable</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                <textarea
                  placeholder="Ajouter des détails sur le maillot, caractéristiques spéciales, etc."
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-20"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">Photos du maillot</label>
                <ImageUpload 
                  images={formData.images}
                  setImages={(images) => setFormData({...formData, images})}
                />
                <p className="text-xs text-gray-400 mt-2">
                  Télécharger des photos du maillot. Optionnel mais recommandé.
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
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 font-semibold"
            >
              {loading ? 'Sauvegarde...' : 'Sauvegarder les corrections'}
            </button>
          </div>
        </form>
      </div>
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
  const [trafficStats, setTrafficStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [jerseyToEdit, setJerseyToEdit] = useState(null);
  const [siteMode, setSiteMode] = useState('public');
  const [siteSettingsLoading, setSiteSettingsLoading] = useState(false);

  useEffect(() => {
    if (user?.email === 'topkitfr@gmail.com') {
      if (activeTab === 'jerseys') {
        fetchPendingJerseys();
      } else if (activeTab === 'users') {
        fetchUsers();
      } else if (activeTab === 'activities') {
        fetchActivities();
        fetchTrafficStats();
      } else if (activeTab === 'settings') {
        fetchSiteSettings();
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

  const fetchTrafficStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/admin/traffic-stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTrafficStats(response.data);
    } catch (error) {
      console.error('Failed to fetch traffic stats:', error);
    }
  };

  const fetchSiteSettings = async () => {
    try {
      setSiteSettingsLoading(true);
      const response = await axios.get(`${API}/api/site/mode`);
      setSiteMode(response.data.mode);
    } catch (error) {
      console.error('Failed to fetch site settings:', error);
    } finally {
      setSiteSettingsLoading(false);
    }
  };

  const updateSiteMode = async (newMode) => {
    if (!window.confirm(`Changer le mode du site vers "${newMode}" ?`)) return;

    try {
      setSiteSettingsLoading(true);
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/site/mode`, {
        mode: newMode
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSiteMode(newMode);
      alert(`Mode du site changé vers: ${newMode}`);
    } catch (error) {
      console.error('Failed to update site mode:', error);
      alert('Erreur lors du changement de mode');
    } finally {
      setSiteSettingsLoading(false);
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

  const handleEdit = (jersey) => {
    setJerseyToEdit({...jersey}); // Create a copy for editing
    setShowEditModal(true);
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
            📊 Traffic & Analytics
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'settings'
                ? 'bg-red-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            ⚙️ Site Settings
          </button>
          <button
            onClick={() => setActiveTab('beta-requests')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'beta-requests'
                ? 'bg-red-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            🚀 Beta Requests
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
                        onClick={() => handleEdit(jersey)}
                        disabled={actionLoading}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                      >
                        ✏️ Corriger
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
      ) : activeTab === 'activities' ? (
        <div>
          <h2 className="text-xl font-bold text-white mb-6">
            📊 Traffic & Analytics Dashboard
          </h2>
          
          {trafficStats && (
            <div className="space-y-6">
              {/* Overview Stats */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">System Overview</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div className="text-2xl font-bold text-white">{trafficStats.overview.total_users}</div>
                    <div className="text-sm text-gray-400">Total Users</div>
                    <div className="text-xs text-green-400 mt-1">
                      +{trafficStats.recent_activity.new_users_7d} this week
                    </div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div className="text-2xl font-bold text-white">{trafficStats.overview.total_jerseys}</div>
                    <div className="text-sm text-gray-400">Total Jerseys</div>
                    <div className="text-xs text-green-400 mt-1">
                      +{trafficStats.recent_activity.new_jerseys_7d} this week
                    </div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div className="text-2xl font-bold text-white">{trafficStats.overview.total_listings}</div>
                    <div className="text-sm text-gray-400">Total Listings</div>
                    <div className="text-xs text-green-400 mt-1">
                      +{trafficStats.recent_activity.new_listings_7d} this week
                    </div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div className="text-2xl font-bold text-white">{trafficStats.overview.total_collections}</div>
                    <div className="text-sm text-gray-400">Total Collections</div>
                    <div className="text-xs text-green-400 mt-1">
                      +{trafficStats.recent_activity.new_collections_7d} this week
                    </div>
                  </div>
                </div>
              </div>

              {/* Moderation Queue */}
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-300 mb-3">
                  🚨 Moderation Queue
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-800 rounded-lg p-3 border border-red-700">
                    <div className="text-xl font-bold text-red-400">{trafficStats.overview.pending_jerseys}</div>
                    <div className="text-sm text-gray-400">Pending Approval</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-3 border border-yellow-700">
                    <div className="text-xl font-bold text-yellow-400">{trafficStats.overview.needs_modification}</div>
                    <div className="text-sm text-gray-400">Needs Modification</div>
                  </div>
                </div>
              </div>

              {/* Jersey Status Breakdown */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Jersey Status Distribution</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {trafficStats.jersey_statuses.map((status, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                      <div className="text-lg font-bold text-white">{status.count}</div>
                      <div className="text-sm text-gray-400 capitalize">{status.status.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Leagues */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Top Leagues by Jersey Count</h3>
                <div className="bg-gray-800 rounded-lg border border-gray-700">
                  {trafficStats.top_leagues.slice(0, 8).map((league, index) => (
                    <div key={index} className={`flex justify-between items-center p-3 ${index < trafficStats.top_leagues.length - 1 ? 'border-b border-gray-700' : ''}`}>
                      <span className="text-white">{league.league}</span>
                      <span className="text-gray-400">{league.count} jerseys</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Most Active Users */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Most Active Collectors</h3>
                <div className="bg-gray-800 rounded-lg border border-gray-700">
                  {trafficStats.active_users.slice(0, 8).map((user, index) => (
                    <div key={index} className={`flex justify-between items-center p-3 ${index < trafficStats.active_users.length - 1 ? 'border-b border-gray-700' : ''}`}>
                      <div>
                        <span className="text-white font-medium">{user.user_name}</span>
                        <div className="text-xs text-gray-500">{user.user_email}</div>
                      </div>
                      <span className="text-blue-400">{user.collection_count} items</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent System Activities */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Recent System Activities</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {activities.slice(0, 20).map((activity) => (
                    <div key={activity.id} className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
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
            </div>
          )}

          {!trafficStats && loading && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-2xl font-bold text-white mb-4">Loading Analytics...</h3>
              <p className="text-gray-400">Fetching system statistics and traffic data.</p>
            </div>
          )}

          {!trafficStats && !loading && (
            <div className="text-center py-16 bg-gray-800 rounded-2xl">
              <div className="text-6xl mb-4">❌</div>
              <h3 className="text-2xl font-bold text-white mb-4">Analytics Unavailable</h3>
              <p className="text-gray-400">Unable to load system analytics data.</p>
            </div>
          )}
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
      
      {/* Edit Jersey Modal */}
      {showEditModal && jerseyToEdit && (
        <AdminEditJerseyModal
          jersey={jerseyToEdit}
          onClose={() => {
            setShowEditModal(false);
            setJerseyToEdit(null);
          }}
          onSave={async (updatedJersey) => {
            try {
              setActionLoading(true);
              const token = localStorage.getItem('token');
              await axios.put(`${API}/api/admin/jerseys/${jerseyToEdit.id}/edit`, updatedJersey, {
                headers: { Authorization: `Bearer ${token}` }
              });
              alert('Jersey mis à jour avec succès !');
              fetchPendingJerseys();
              setShowEditModal(false);
              setJerseyToEdit(null);
            } catch (error) {
              console.error('Update error:', error);
              alert('Erreur lors de la mise à jour du jersey');
            } finally {
              setActionLoading(false);
            }
          }}
        />
      )}
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <SiteAccessGate>
        <AppContent />
      </SiteAccessGate>
    </AuthProvider>
  );
};

export default App;