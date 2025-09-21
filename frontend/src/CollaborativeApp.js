import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import CollaborativeHeader from './components/CollaborativeHeader';
import CollaborativeHomepage from './pages/CollaborativeHomepage';
import CollaborativeExplorePage from './pages/CollaborativeExplorePage';
import CataloguePage from './pages/CataloguePage';
import MyCollectionPage from './pages/MyCollectionPage';
import CollaborativeTeamsPage from './pages/CollaborativeTeamsPage';
import CollaborativeBrandsPage from './pages/CollaborativeBrandsPage';
import CollaborativePlayersPage from './pages/CollaborativePlayersPage';
import CollaborativeCompetitionsPage from './pages/CollaborativeCompetitionsPage';
import CollaborativeMasterJerseyPage from './pages/CollaborativeMasterJerseyPage';
import ContributionsV2Page from './pages/ContributionsV2Page';
import ModerationDashboard from './pages/ModerationDashboard';
import CollaborativeProfilePage from './pages/CollaborativeProfilePage';
import AdminDashboard from './pages/AdminDashboard';
import LeaderboardPage from './pages/LeaderboardPage';
// Import nouvelles pages détaillées
import TeamDetailPage from './pages/TeamDetailPage';
import BrandDetailPage from './pages/BrandDetailPage';
import CompetitionDetailPage from './pages/CompetitionDetailPage';
import PlayerDetailPage from './pages/PlayerDetailPage';
import MasterJerseyDetailPage from './pages/MasterJerseyDetailPage';
import ContributionDetailPage from './pages/ContributionDetailPage';
// Import Kit Area pages (Discogs-like structure)
import KitAreaPage from './pages/KitAreaPage';
import AllVersionsPage from './pages/AllVersionsPage';
import VersionDetailPage from './pages/VersionDetailPage';
import AuthModal from './AuthModal';

// Get the backend URL from environment variables
const API = process.env.REACT_APP_BACKEND_URL;

// Composant interne qui utilise les hooks de React Router
const AppContent = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // State management
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Global data states
  const [teams, setTeams] = useState([]);
  const [brands, setBrands] = useState([]);
  const [players, setPlayers] = useState([]);
  const [competitions, setCompetitions] = useState([]);
  const [masterJerseys, setMasterJerseys] = useState([]);
  const [loading, setLoading] = useState(false);

  // Déterminer la vue actuelle à partir de l'URL
  const getCurrentView = () => {
    const path = location.pathname;
    if (path === '/') return 'home';
    if (path === '/explore') return 'explore';
    if (path === '/catalogue') return 'catalogue';
    if (path === '/kit-area') return 'kit-area';
    if (path === '/my-collection') return 'my-collection';
    if (path === '/contributions-v2') return 'contributions-v2';
    if (path === '/moderation') return 'moderation';
    if (path === '/teams') return 'teams';
    if (path === '/brands') return 'brands';
    if (path === '/players') return 'players';
    if (path === '/competitions') return 'competitions';
    if (path === '/master-kits') return 'master-kits';
    if (path === '/profile') return 'profile';
    if (path === '/admin') return 'admin';
    return 'home';
  };

  // Authentication check
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      if (token && userData) {
        const parsedUser = JSON.parse(userData);
        setUser({ ...parsedUser, token });
        console.log('User authenticated:', parsedUser);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
    }
  };

  // Authentication handlers
  const handleLoginSuccess = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser({ ...userData, token });
    setShowAuthModal(false);
    
    // Handle pending actions after login
    const pendingActionStr = localStorage.getItem('pendingAction');
    if (pendingActionStr) {
      try {
        const pendingAction = JSON.parse(pendingActionStr);
        localStorage.removeItem('pendingAction'); // Clear the pending action
        
        // Handle different types of pending actions
        if (pendingAction.action === 'addKit') {
          // Navigate to Kit Area if not already there, and trigger kit creation
          if (location.pathname !== '/kit-area') {
            navigate('/kit-area');
          }
          // Delay to ensure component is mounted
          setTimeout(() => {
            // Trigger the kit creation modal by dispatching a custom event
            window.dispatchEvent(new CustomEvent('openMasterKitForm'));
          }, 500);
        } else if (pendingAction.action === 'addToCollection' && pendingAction.masterKit) {
          // Handle add to collection action
          window.dispatchEvent(new CustomEvent('addToCollection', { 
            detail: { 
              masterKit: pendingAction.masterKit, 
              collectionType: pendingAction.collectionType || 'owned' 
            } 
          }));
        } else if (pendingAction.action === 'addToWantList' && pendingAction.masterKit) {
          // Handle add to want list action
          window.dispatchEvent(new CustomEvent('addToWantList', { 
            detail: { masterKit: pendingAction.masterKit } 
          }));
        }
      } catch (error) {
        console.error('Error handling pending action:', error);
      }
    }
    
    // Reload collaborative data
    loadCollaborativeData();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/');
  };

  // Update user data (for profile picture changes, etc.)
  const handleUserUpdate = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${API}/api/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        const updatedUser = { ...userData, token };
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(updatedUser);
      }
    } catch (error) {
      console.error('Error updating user data:', error);
    }
  };

  // Data loading functions
  const loadCollaborativeData = async () => {
    setLoading(true);
    try {
      // Load basic data for all entities (removing limits to get all data)
      const [teamsRes, brandsRes, playersRes, competitionsRes, masterJerseysRes] = await Promise.all([
        fetch(`${API}/api/teams`),
        fetch(`${API}/api/brands`),
        fetch(`${API}/api/players`),
        fetch(`${API}/api/competitions`),
        fetch(`${API}/api/master-kits`)
      ]);

      if (teamsRes.ok) setTeams(await teamsRes.json());
      if (brandsRes.ok) setBrands(await brandsRes.json());
      if (playersRes.ok) setPlayers(await playersRes.json());
      if (competitionsRes.ok) setCompetitions(await competitionsRes.json());
      if (masterJerseysRes.ok) setMasterJerseys(await masterJerseysRes.json());

    } catch (error) {
      console.error('Error loading collaborative data:', error);
    }
    setLoading(false);
  };

  // Load data on mount
  useEffect(() => {
    loadCollaborativeData();
  }, []);

  // Search function
  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length > 2) {
      try {
        const response = await fetch(`${API}/api/search/collaborative?q=${encodeURIComponent(query)}&limit=50`);
        if (response.ok) {
          const results = await response.json();
          console.log('Search results:', results);
          // Navigate to explore view with search results
          navigate('/explore');
        }
      } catch (error) {
        console.error('Search error:', error);
      }
    }
  };

  // Handler pour le changement de vue depuis le header
  const handleViewChange = (viewName) => {
    const routes = {
      'home': '/',
      'explore': '/explore',
      'catalogue': '/catalogue',
      'kit-area': '/kit-area',
      'my-collection': '/my-collection',
      'contributions-v2': '/contributions-v2',
      'moderation': '/moderation',
      'teams': '/teams',
      'brands': '/brands',
      'players': '/players',
      'competitions': '/competitions',
      'master-kits': '/master-kits',
      'profile': '/profile',
      'admin': '/admin'
    };
    
    const route = routes[viewName] || '/';
    navigate(route);
  };

  const commonProps = {
    user,
    API,
    teams,
    brands,
    players,
    competitions,
    masterJerseys,
    onDataUpdate: loadCollaborativeData,
    searchQuery,
    setShowAuthModal
  };

  return (
    <div className="collaborative-app min-h-screen bg-gray-50">
      {/* Header */}
      <CollaborativeHeader
        user={user}
        currentView={getCurrentView()}
        onViewChange={handleViewChange}
        onSearch={handleSearch}
        onLogin={() => setShowAuthModal(true)}
        onLogout={handleLogout}
        searchQuery={searchQuery}
        onUserUpdate={handleUserUpdate}
      />

      {/* Main Content */}
      <div>
        <Routes>
          <Route path="/" element={<CollaborativeHomepage {...commonProps} onViewChange={handleViewChange} />} />
          <Route path="/explore" element={<CollaborativeExplorePage {...commonProps} />} />
          <Route path="/catalogue" element={<CataloguePage {...commonProps} />} />
          <Route path="/kit-area" element={<KitAreaPage {...commonProps} />} />
          <Route path="/my-collection" element={<MyCollectionPage {...commonProps} />} />
          <Route path="/contributions-v2" element={<ContributionsV2Page {...commonProps} />} />
          <Route path="/moderation" element={<ModerationDashboard {...commonProps} />} />
          <Route path="/teams" element={<CollaborativeTeamsPage {...commonProps} />} />
          <Route path="/brands" element={<CollaborativeBrandsPage {...commonProps} />} />
          <Route path="/players" element={<CollaborativePlayersPage {...commonProps} />} />
          <Route path="/competitions" element={<CollaborativeCompetitionsPage {...commonProps} />} />
          <Route path="/master-kits" element={<CollaborativeMasterJerseyPage {...commonProps} />} />
          <Route path="/profile" element={<CollaborativeProfilePage {...commonProps} />} />
          <Route path="/admin" element={<AdminDashboard user={user} API={API} />} />
          
          {/* Routes pour les pages détaillées */}
          <Route path="/teams/:teamId" element={<TeamDetailPage {...commonProps} />} />
          <Route path="/brands/:brandId" element={<BrandDetailPage {...commonProps} />} />
          <Route path="/competitions/:competitionId" element={<CompetitionDetailPage {...commonProps} />} />
          <Route path="/players/:playerId" element={<PlayerDetailPage {...commonProps} />} />
          <Route path="/master-kits/:jerseyId" element={<MasterJerseyDetailPage {...commonProps} />} />
          <Route path="/contributions-v2/:contributionId" element={
            <ContributionDetailPage 
              {...commonProps} 
              contributionId={window.location.pathname.split('/contributions-v2/')[1]}
              onNavigateBack={() => navigate('/contributions-v2')}
            />
          } />

          {/* Kit Area routes (Discogs-like structure) */}
          <Route path="/kit-area/master/:id" element={<MasterJerseyDetailPage {...commonProps} />} />
          <Route path="/kit-area/master/:id/versions" element={<AllVersionsPage {...commonProps} />} />
          <Route path="/kit-area/version/:id" element={<VersionDetailPage {...commonProps} />} />
        </Routes>
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Chargement des données collaboratives...</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Composant principal avec BrowserRouter
const CollaborativeApp = () => {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
};

export default CollaborativeApp;