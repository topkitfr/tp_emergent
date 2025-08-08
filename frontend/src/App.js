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
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('Profile response:', response.data);
      setUser(response.data.user);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      console.error('Error response:', error.response?.data);
      localStorage.removeItem('token');
      setLoading(false);
    }
  };

  const login = (token, userData) => {
    console.log('Login called with token:', token.substring(0, 20) + '...');
    console.log('Login called with user data:', userData);
    localStorage.setItem('token', token);
    setUser(userData);
    console.log('User state set to:', userData);
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

// Header Component
const Header = ({ currentView, setCurrentView }) => {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

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
                  <div className="flex items-center space-x-2">
                    {user.picture && (
                      <img 
                        src={user.picture} 
                        alt={user.name}
                        className="w-8 h-8 rounded-full border-2 border-gray-600"
                      />
                    )}
                    <span className="text-sm text-gray-300">Welcome, <span className="text-white font-medium">{user.name}</span></span>
                  </div>
                  <button 
                    onClick={logout}
                    className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors border border-gray-600 text-sm font-medium"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button 
                  onClick={() => setShowAuthModal(true)}
                  className="bg-white text-black px-6 py-2 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
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
                  onClick={() => setCurrentView('collections')}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    currentView === 'collections' 
                      ? 'bg-white text-black' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  My Collection
                </button>
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

// Create Listing Modal Component (for creating listings from existing jerseys)
const CreateListingModal = ({ onClose, jerseyId, jersey = null }) => {
  const [formData, setFormData] = useState({
    listing_description: '',
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

      // Create the listing without price (price determined by market like Discogs)
      const listingData = {
        jersey_id: jerseyId,
        description: formData.listing_description,
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
            <label className="block text-sm font-medium text-gray-300 mb-1">Description*</label>
            <textarea
              placeholder="Describe the jersey condition, any special features, authenticity, etc."
              value={formData.listing_description}
              onChange={(e) => setFormData({...formData, listing_description: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-white text-white placeholder-gray-400 h-32"
              required
            />
            <p className="text-xs text-gray-400 mt-1">
              Note: Price will be determined by market value based on similar sales (like Discogs)
            </p>
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
              className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
            >
              Cancel
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
      const response = await axios.post(`${API}${endpoint}`, formData);
      login(response.data.token, response.data.user);
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = () => {
    window.location.href = `${API}/api/auth/google`;
  };

  const handleEmergentAuth = async () => {
    try {
      const response = await axios.get(`${API}/api/auth/emergent/redirect`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      setError('Failed to redirect to Emergent Auth');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
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

          <button
            onClick={handleEmergentAuth}
            className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Continue with Emergent Auth
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

// Profile Settings Modal
const ProfileSettingsModal = ({ user, onClose, onSettingsUpdate }) => {
  const [settings, setSettings] = useState({
    profile_privacy: user?.profile_privacy || 'public',
    show_collection_value: user?.show_collection_value || false
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/api/profile/settings`, settings, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Profile settings updated successfully!');
      onSettingsUpdate(settings);
      onClose();
    } catch (error) {
      alert('Failed to update settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-md w-full border border-gray-800">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-white">Profile Settings</h3>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Profile Visibility</label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="public"
                    checked={settings.profile_privacy === 'public'}
                    onChange={(e) => setSettings({...settings, profile_privacy: e.target.value})}
                    className="mr-2"
                  />
                  <span className="text-white">Public</span>
                  <span className="text-gray-400 text-sm ml-2">- Anyone can view your profile and collections</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="private"
                    checked={settings.profile_privacy === 'private'}
                    onChange={(e) => setSettings({...settings, profile_privacy: e.target.value})}
                    className="mr-2"
                  />
                  <span className="text-white">Private</span>
                  <span className="text-gray-400 text-sm ml-2">- Only you can view your profile and collections</span>
                </label>
              </div>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.show_collection_value}
                  onChange={(e) => setSettings({...settings, show_collection_value: e.target.checked})}
                  className="mr-3"
                />
                <div>
                  <span className="text-white">Show Collection Values</span>
                  <p className="text-gray-400 text-sm">Display estimated values of your jersey collection (only visible to you)</p>
                </div>
              </label>
            </div>

            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <h4 className="text-white font-medium mb-2">Privacy Information</h4>
              <ul className="text-gray-300 text-sm space-y-1">
                <li>• Collection values are always private and only visible to you</li>
                <li>• Private profiles hide your collection from other users</li>
                <li>• Your listings and public interactions remain visible regardless of privacy setting</li>
              </ul>
            </div>

            <div className="flex space-x-3">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-800 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors border border-gray-600"
              >
                Cancel
              </button>
              <button 
                type="submit"
                disabled={loading}
                className="flex-1 bg-white text-black py-2 rounded-lg hover:bg-gray-200 transition-colors font-semibold disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </form>
        </div>
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
          user={profileData?.user}
          onClose={() => setShowSettings(false)}
          onSettingsUpdate={handleSettingsUpdate}
        />
      )}
    </div>
  );
};

// Collections Page Component
const CollectionsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('owned');
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchCollections();
    }
  }, [user, activeTab]);

  const fetchCollections = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/collections/${activeTab}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCollections(response.data);
    } catch (error) {
      console.error('Failed to fetch collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFromCollection = async (jerseyId) => {
    // Use the main App's remove function via custom event
    const event = new CustomEvent('removeFromCollection', { detail: jerseyId });
    window.dispatchEvent(event);
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

  const handleAddNewJersey = () => {
    // This will trigger the main app's listing creation modal for creating a new jersey
    const event = new CustomEvent('addNewJersey');
    window.dispatchEvent(event);
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
        <div className="flex items-center space-x-4">
          <button
            onClick={handleAddNewJersey}
            className="bg-white text-black px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
          >
            + Add New Jersey
          </button>
          <div className="flex space-x-1 bg-gray-800 rounded-lg p-1 border border-gray-700">
            <button
              onClick={() => setActiveTab('owned')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'owned'
                  ? 'bg-white text-black'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              Owned Jerseys
            </button>
            <button
              onClick={() => setActiveTab('wanted')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'wanted'
                  ? 'bg-white text-black'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              Wanted Jerseys
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-400">Loading collections...</div>
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
    </div>
  );
};

// Jersey Card Component (updated)
const JerseyCard = ({ jersey, showActions = false, onAddToCollection, showCollectionDate = false, addedAt, onRemoveFromCollection, showRemove = false, showSellButton = false, onSellJersey, showEditButton = false, onEditJersey, onClick, onCreatorClick }) => {
  return (
    <div className="bg-gray-900 rounded-xl shadow-2xl overflow-hidden hover:shadow-3xl transition-all border border-gray-800 hover:border-gray-700 cursor-pointer"
         onClick={() => onClick && onClick(jersey)}>
      <img
        src={jersey.images?.[0] || 'https://via.placeholder.com/300x400?text=Jersey+Image'}
        alt={`${jersey.team} ${jersey.season}`}
        className="w-full h-48 object-cover"
      />
      <div className="p-6">
        <h3 className="text-xl font-semibold text-white mb-2">{jersey.team}</h3>
        <p className="text-gray-400 mb-1">{jersey.season} • {jersey.home_away}</p>
        {jersey.player && <p className="text-white font-medium mb-3">{jersey.player}</p>}
        
        {/* Creator information */}
        {jersey.creator_info && (
          <div className="mb-3" onClick={(e) => e.stopPropagation()}>
            <p className="text-xs text-gray-500">Added by</p>
            <div className="flex items-center space-x-2 mt-1">
              {jersey.creator_info.picture && (
                <img 
                  src={jersey.creator_info.picture} 
                  alt={jersey.creator_info.name}
                  className="w-5 h-5 rounded-full"
                />
              )}
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  onCreatorClick && onCreatorClick(jersey.creator_info.id); 
                }}
                className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
              >
                {jersey.creator_info.name}
              </button>
            </div>
          </div>
        )}
        
        <div className="mt-4 flex justify-between items-center mb-3">
          <div className="text-sm text-gray-400">
            <span className="bg-gray-800 text-white px-3 py-1 rounded-full border border-gray-700">{jersey.size}</span>
            <span className="bg-gray-800 text-white px-3 py-1 rounded-full ml-2 border border-gray-700">
              {jersey.condition}
            </span>
          </div>
        </div>
        
        <p className="text-sm text-gray-300 mt-3 line-clamp-2">{jersey.description}</p>
        
        {showCollectionDate && (
          <p className="text-xs text-gray-500 mt-3">
            Added {new Date(addedAt).toLocaleDateString()}
          </p>
        )}
        
        {showActions && (
          <div className="mt-6 space-y-3" onClick={(e) => e.stopPropagation()}>
            <button 
              onClick={(e) => { e.stopPropagation(); onAddToCollection(jersey.id, 'owned'); }}
              className="w-full bg-white text-black py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm font-semibold"
            >
              Add to Owned
            </button>
            <button 
              onClick={(e) => { e.stopPropagation(); onAddToCollection(jersey.id, 'wanted'); }}
              className="w-full bg-gray-800 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm font-semibold border border-gray-600"
            >
              Add to Wanted
            </button>
          </div>
        )}

        {showSellButton && (
          <div className="mt-4" onClick={(e) => e.stopPropagation()}>
            <button 
              onClick={(e) => { e.stopPropagation(); onSellJersey(jersey); }}
              className="w-full bg-green-900 text-green-300 py-2 rounded-lg hover:bg-green-800 transition-colors text-sm font-semibold border border-green-700"
            >
              Sell This Jersey
            </button>
          </div>
        )}

        {showEditButton && (
          <div className="mt-3" onClick={(e) => e.stopPropagation()}>
            <button 
              onClick={(e) => { e.stopPropagation(); onEditJersey(jersey); }}
              className="w-full bg-blue-900 text-blue-300 py-2 rounded-lg hover:bg-blue-800 transition-colors text-sm font-semibold border border-blue-700"
            >
              Edit Jersey
            </button>
          </div>
        )}

        {showRemove && (
          <div className="mt-4" onClick={(e) => e.stopPropagation()}>
            <button 
              onClick={(e) => { e.stopPropagation(); onRemoveFromCollection(jersey.id); }}
              className="w-full bg-red-900 text-red-300 py-2 rounded-lg hover:bg-red-800 transition-colors text-sm font-semibold border border-red-700"
            >
              Remove from Collection
            </button>
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
const App = () => {
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
      
      const response = await axios.get(`${API}/api/jerseys?${params.toString()}`);
      setJerseys(response.data);
    } catch (error) {
      console.error('Failed to fetch jerseys:', error);
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

    if (!confirm('Are you sure you want to remove this jersey from your collection?')) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      await axios.delete(`${API}/api/collections/${jerseyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Removed from collection!');
      // Refresh collections if we're on that page
      if (currentView === 'collections') {
        // This will trigger a re-render of the collections page
        window.location.reload();
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to remove from collection');
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

  const renderContent = () => {
    switch (currentView) {
      case 'profile':
        return <ProfilePage />;
      
      case 'collections':
        return <CollectionsPage />;
      
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
    <AuthProvider>
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
    </AuthProvider>
  );
};

export default App;