import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchProfile = async (token) => {
    try {
      const response = await axios.get(`${API}/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data.user);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      localStorage.removeItem('token');
      setLoading(false);
    }
  };

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
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
    <header className="bg-black text-white shadow-2xl border-b border-gray-800">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_football-threads-5/artifacts/d38ypztj_ho7nwfgn_topkit_logo_nobc_wh.png"
              alt="TopKit Logo"
              className="h-12 w-auto cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => setCurrentView('home')}
            />
          </div>
          
          {/* Navigation */}
          <nav className="flex items-center space-x-8">
            <button 
              onClick={() => setCurrentView('jerseys')}
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              Browse
            </button>
            <button 
              onClick={() => setCurrentView('marketplace')}
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              Marketplace
            </button>
            {user && (
              <>
                <button 
                  onClick={() => setCurrentView('collections')}
                  className="text-gray-300 hover:text-white transition-colors font-medium"
                >
                  My Collection
                </button>
                <button 
                  onClick={() => setCurrentView('profile')}
                  className="text-gray-300 hover:text-white transition-colors font-medium"
                >
                  Profile
                </button>
              </>
            )}
            
            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-400">Welcome, {user.name}</span>
                <button 
                  onClick={logout}
                  className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors border border-gray-600"
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
          </nav>
        </div>
      </div>
      
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </header>
  );
};

// Create Listing Modal Component
const CreateListingModal = ({ onClose, jerseyId, jersey = null }) => {
  const [formData, setFormData] = useState({
    price: '',
    description: '',
    images: [],
    // Additional jersey details if creating new jersey
    team: jersey?.team || '',
    season: jersey?.season || '',
    player: jersey?.player || '',
    size: jersey?.size || 'M',
    condition: jersey?.condition || 'excellent',
    manufacturer: jersey?.manufacturer || '',
    home_away: jersey?.home_away || 'home',
    league: jersey?.league || '',
    model: 'replica', // replica, professional, special
    color: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCreatingNewJersey, setIsCreatingNewJersey] = useState(!jerseyId);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to create a listing');
      }

      let finalJerseyId = jerseyId;

      // If creating a new jersey first
      if (isCreatingNewJersey || !jerseyId) {
        const jerseyData = {
          team: formData.team,
          season: formData.season,
          player: formData.player || null,
          size: formData.size,
          condition: formData.condition,
          manufacturer: formData.manufacturer,
          home_away: formData.home_away,
          league: formData.league,
          description: `${formData.model} ${formData.color} jersey - ${formData.description}`,
          images: formData.images
        };

        const jerseyResponse = await axios.post(`${API}/jerseys`, jerseyData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        finalJerseyId = jerseyResponse.data.id;
      }

      // Create the listing
      const listingData = {
        jersey_id: finalJerseyId,
        price: parseFloat(formData.price),
        description: formData.description,
        images: formData.images
      };

      await axios.post(`${API}/listings`, listingData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Listing created successfully!');
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'Failed to create listing');
    } finally {
      setLoading(false);
    }
  };

  const handleImageAdd = () => {
    const imageUrl = prompt('Enter image URL:');
    if (imageUrl) {
      setFormData({
        ...formData,
        images: [...formData.images, imageUrl]
      });
    }
  };

  const removeImage = (index) => {
    setFormData({
      ...formData,
      images: formData.images.filter((_, i) => i !== index)
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Create Jersey Listing</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
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
          {/* Toggle for new jersey creation */}
          {jerseyId && (
            <div className="bg-blue-50 p-4 rounded-lg mb-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={isCreatingNewJersey}
                  onChange={(e) => setIsCreatingNewJersey(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-700">Create new jersey instead of using existing one</span>
              </label>
            </div>
          )}

          {/* Jersey Details (only if creating new jersey) */}
          {(isCreatingNewJersey || !jerseyId) && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">Jersey Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Club/National Team*</label>
                  <input
                    type="text"
                    placeholder="e.g., Manchester United"
                    value={formData.team}
                    onChange={(e) => setFormData({...formData, team: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Season*</label>
                  <input
                    type="text"
                    placeholder="e.g., 2023-24"
                    value={formData.season}
                    onChange={(e) => setFormData({...formData, season: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brand/Manufacturer*</label>
                  <input
                    type="text"
                    placeholder="e.g., Nike, Adidas, Puma"
                    value={formData.manufacturer}
                    onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">League*</label>
                  <input
                    type="text"
                    placeholder="e.g., Premier League, La Liga"
                    value={formData.league}
                    onChange={(e) => setFormData({...formData, league: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Player Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Bruno Fernandes (optional)"
                    value={formData.player}
                    onChange={(e) => setFormData({...formData, player: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Primary Color*</label>
                  <input
                    type="text"
                    placeholder="e.g., Red, Blue, Black"
                    value={formData.color}
                    onChange={(e) => setFormData({...formData, color: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type*</label>
                  <select
                    value={formData.home_away}
                    onChange={(e) => setFormData({...formData, home_away: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  >
                    <option value="home">Home</option>
                    <option value="away">Away</option>
                    <option value="third">Third Kit</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Model*</label>
                  <select
                    value={formData.model}
                    onChange={(e) => setFormData({...formData, model: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  >
                    <option value="replica">Replica</option>
                    <option value="professional">Professional/Authentic</option>
                    <option value="special">Special Edition</option>
                    <option value="retro">Retro/Vintage</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Size*</label>
                  <select
                    value={formData.size}
                    onChange={(e) => setFormData({...formData, size: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Condition*</label>
                  <select
                    value={formData.condition}
                    onChange={(e) => setFormData({...formData, condition: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
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
            </div>
          )}

          {/* Listing Details */}
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Listing Details</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Price (USD)*</label>
              <input
                type="number"
                step="0.01"
                placeholder="e.g., 89.99"
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                required
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Description*</label>
              <textarea
                placeholder="Describe the jersey condition, any special features, authenticity, etc."
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 h-24"
                required
              />
            </div>

            {/* Images */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Images</label>
              <button
                type="button"
                onClick={handleImageAdd}
                className="mb-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                Add Image URL
              </button>
              {formData.images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {formData.images.map((image, index) => (
                    <div key={index} className="relative">
                      <img 
                        src={image} 
                        alt={`Jersey ${index + 1}`}
                        className="w-full h-24 object-cover rounded border"
                        onError={(e) => {
                          e.target.src = 'https://via.placeholder.com/100x100?text=Invalid+URL';
                        }}
                      />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating Listing...' : 'Create Listing'}
            </button>
          </div>
        </form>
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
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
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
    window.location.href = `${API}/auth/google`;
  };

  const handleEmergentAuth = async () => {
    try {
      const response = await axios.get(`${API}/auth/emergent/redirect`);
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
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required={!isLogin}
            />
          )}
          
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
          
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
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

// Profile Page Component
const ProfilePage = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfileData(response.data);
    } catch (error) {
      console.error('Failed to fetch profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading profile...</div>;
  }

  if (!user) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Please Login</h2>
        <p className="text-gray-600">You need to login to view your profile.</p>
      </div>
    );
  }

  const valuations = profileData?.valuations;
  const portfolio = valuations?.portfolio_summary;

  return (
    <div className="max-w-6xl mx-auto">
      {/* User Profile Section */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="flex items-center space-x-6 mb-8">
          {user.picture && (
            <img 
              src={user.picture} 
              alt={user.name}
              className="w-20 h-20 rounded-full border-4 border-green-500"
            />
          )}
          <div>
            <h1 className="text-3xl font-bold text-gray-800">{user.name}</h1>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-500">
              Member since {new Date(user.created_at).toLocaleDateString()}
            </p>
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mt-2">
              {user.provider} user
            </span>
          </div>
        </div>

        {/* Collection Stats */}
        {profileData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-green-50 p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {profileData.stats?.owned_jerseys || 0}
              </div>
              <div className="text-gray-700">Owned Jerseys</div>
            </div>
            <div className="bg-blue-50 p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {profileData.stats?.wanted_jerseys || 0}
              </div>
              <div className="text-gray-700">Wanted Jerseys</div>
            </div>
            <div className="bg-purple-50 p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {profileData.stats?.active_listings || 0}
              </div>
              <div className="text-gray-700">Active Listings</div>
            </div>
          </div>
        )}
      </div>

      {/* Portfolio Valuation Section */}
      {portfolio && (
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="text-3xl mr-3">💰</span>
            Collection Portfolio Valuation
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200">
              <div className="text-sm font-medium text-green-700 mb-2">Low Estimate</div>
              <div className="text-2xl font-bold text-green-800">
                ${portfolio.total_low_estimate?.toLocaleString() || '0'}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
              <div className="text-sm font-medium text-blue-700 mb-2">Median Estimate</div>
              <div className="text-2xl font-bold text-blue-800">
                ${portfolio.total_median_estimate?.toLocaleString() || '0'}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
              <div className="text-sm font-medium text-purple-700 mb-2">High Estimate</div>
              <div className="text-2xl font-bold text-purple-800">
                ${portfolio.total_high_estimate?.toLocaleString() || '0'}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 p-6 rounded-xl border border-amber-200">
              <div className="text-sm font-medium text-amber-700 mb-2">Average Value</div>
              <div className="text-2xl font-bold text-amber-800">
                ${portfolio.average_value?.toLocaleString() || '0'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <span className="font-medium">Total Items:</span> {portfolio.total_items || 0}
            </div>
            <div>
              <span className="font-medium">Valued Items:</span> {portfolio.valued_items || 0}
            </div>
          </div>

          {portfolio.valued_items < portfolio.total_items && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center">
                <span className="text-yellow-600 text-xl mr-2">⚠️</span>
                <div>
                  <div className="font-medium text-yellow-800">Incomplete Valuation Data</div>
                  <div className="text-sm text-yellow-700">
                    {portfolio.total_items - portfolio.valued_items} of your jerseys don't have enough market data for accurate valuation. 
                    As more similar jerseys are listed or sold, valuations will become available.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Individual Jersey Valuations */}
      {valuations?.collections && valuations.collections.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="text-3xl mr-3">📊</span>
            Individual Jersey Valuations
          </h2>
          
          <div className="space-y-4">
            {valuations.collections.map((item) => (
              <div key={item.collection_id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-800">
                        {item.jersey.team} {item.jersey.season}
                      </h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.collection_type === 'owned' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {item.collection_type}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>
                        {item.jersey.player && <span className="font-medium">{item.jersey.player}</span>}
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
                            <div className="text-green-600 font-bold">${item.valuation.low_estimate}</div>
                            <div className="text-gray-500 text-xs">Low</div>
                          </div>
                          <div className="text-center">
                            <div className="text-blue-600 font-bold text-lg">${item.valuation.median_estimate}</div>
                            <div className="text-gray-500 text-xs">Median</div>
                          </div>
                          <div className="text-center">
                            <div className="text-purple-600 font-bold">${item.valuation.high_estimate}</div>
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
                                ? 'bg-green-100 text-green-700'
                                : item.valuation.market_data.confidence_score >= 40
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-red-100 text-red-700'
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
      const response = await axios.get(`${API}/collections/${activeTab}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCollections(response.data);
    } catch (error) {
      console.error('Failed to fetch collections:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Please Login</h2>
        <p className="text-gray-600">You need to login to view your collections.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">My Collections</h1>
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('owned')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'owned'
                ? 'bg-green-600 text-white'
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            Owned Jerseys
          </button>
          <button
            onClick={() => setActiveTab('wanted')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'wanted'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            Wanted Jerseys
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading collections...</div>
      ) : collections.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-6xl mb-4">{activeTab === 'owned' ? '👕' : '❤️'}</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            No {activeTab} jerseys yet
          </h2>
          <p className="text-gray-600 mb-8">
            Start building your collection by browsing jerseys and adding them to your {activeTab} list.
          </p>
          <button 
            onClick={() => window.location.hash = '#jerseys'}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
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
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Jersey Card Component (updated)
const JerseyCard = ({ jersey, showActions = false, onAddToCollection, onCreateListing, showCollectionDate = false, addedAt }) => {
  return (
    <div className="bg-gray-900 rounded-xl shadow-2xl overflow-hidden hover:shadow-3xl transition-all border border-gray-800 hover:border-gray-700">
      <img
        src={jersey.images?.[0] || 'https://via.placeholder.com/300x400?text=Jersey+Image'}
        alt={`${jersey.team} ${jersey.season}`}
        className="w-full h-48 object-cover"
      />
      <div className="p-6">
        <h3 className="text-xl font-semibold text-white mb-2">{jersey.team}</h3>
        <p className="text-gray-400 mb-1">{jersey.season} • {jersey.home_away}</p>
        {jersey.player && <p className="text-white font-medium mb-3">{jersey.player}</p>}
        
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
          <div className="mt-6 space-y-3">
            <button 
              onClick={() => onAddToCollection(jersey.id, 'owned')}
              className="w-full bg-white text-black py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm font-semibold"
            >
              Add to Owned
            </button>
            <button 
              onClick={() => onAddToCollection(jersey.id, 'wanted')}
              className="w-full bg-gray-800 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm font-semibold border border-gray-600"
            >
              Add to Wanted
            </button>
            <button 
              onClick={() => onCreateListing(jersey.id)}
              className="w-full bg-gray-800 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm font-semibold border border-gray-600"
            >
              Create Listing
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Listing Card Component
const ListingCard = ({ listing }) => {
  return (
    <div className="bg-gray-900 rounded-xl shadow-2xl overflow-hidden hover:shadow-3xl transition-all border border-gray-800 hover:border-gray-700">
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
        
        <button className="w-full bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold">
          Buy Now
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
  const [selectedJerseyForListing, setSelectedJerseyForListing] = useState(null);

  const fetchJerseys = async (filters = {}) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/jerseys?${params.toString()}`);
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
      
      const response = await axios.get(`${API}/listings?${params.toString()}`);
      setListings(response.data);
    } catch (error) {
      console.error('Failed to fetch listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCollection = async (jerseyId, collectionType) => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please login to add jerseys to your collection');
      return;
    }

    try {
      await axios.post(`${API}/collections`, 
        { jersey_id: jerseyId, collection_type: collectionType },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`Added to ${collectionType} collection!`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to add to collection');
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
              <button 
                onClick={() => handleCreateListing()}
                className="bg-white text-black px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
              >
                + Create New Listing
              </button>
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
                    onCreateListing={() => handleCreateListing(jersey.id, jersey)}
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
              <button 
                onClick={() => handleCreateListing()}
                className="bg-white text-black px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
              >
                + Create Listing
              </button>
            </div>
            <SearchFilter onFilter={fetchListings} />
            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg">Loading listings...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {listings.map((listing) => (
                  <ListingCard key={listing.id} listing={listing} />
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
        
        {/* Navigation */}
        <nav className="bg-gray-900 shadow-sm border-b border-gray-800">
          <div className="container mx-auto px-6">
            <div className="flex space-x-8">
              <button
                onClick={() => setCurrentView('home')}
                className={`py-4 px-2 border-b-2 transition-colors font-medium ${
                  currentView === 'home' 
                    ? 'border-white text-white' 
                    : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentView('jerseys')}
                className={`py-4 px-2 border-b-2 transition-colors font-medium ${
                  currentView === 'jerseys' 
                    ? 'border-white text-white' 
                    : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
                }`}
              >
                Browse Jerseys
              </button>
              <button
                onClick={() => setCurrentView('marketplace')}
                className={`py-4 px-2 border-b-2 transition-colors font-medium ${
                  currentView === 'marketplace' 
                    ? 'border-white text-white' 
                    : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
                }`}
              >
                Marketplace
              </button>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="container mx-auto px-6 py-8">
          {renderContent()}
        </main>

        {/* Modals */}
        {showCreateListing && (
          <CreateListingModal 
            onClose={handleCloseCreateListing}
            jerseyId={selectedJerseyForListing?.id || null}
            jersey={selectedJerseyForListing}
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