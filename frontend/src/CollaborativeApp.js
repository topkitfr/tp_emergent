import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import CollaborativeHeader from './components/CollaborativeHeader';
import CollaborativeHomepage from './pages/CollaborativeHomepage';
import CollaborativeExplorePage from './pages/CollaborativeExplorePage';
import CataloguePage from './pages/CataloguePage';
import VestiairePage from './pages/VestiairePage';
import CollectionsPage from './pages/CollectionsPage';
import ContributePage from './pages/ContributePage';
import CollaborativeTeamsPage from './pages/CollaborativeTeamsPage';
import CollaborativeBrandsPage from './pages/CollaborativeBrandsPage';
import CollaborativePlayersPage from './pages/CollaborativePlayersPage';
import CollaborativeCompetitionsPage from './pages/CollaborativeCompetitionsPage';
import CollaborativeMasterJerseyPage from './pages/CollaborativeMasterJerseyPage';
import CollaborativeContributionsPage from './pages/CollaborativeContributionsPage';
import EnhancedContributionsPage from './pages/EnhancedContributionsPage';
import CollaborativeProfilePage from './pages/CollaborativeProfilePage';
import AdminDashboard from './pages/AdminDashboard';
// Import nouvelles pages détaillées
import TeamDetailPage from './pages/TeamDetailPage';
import BrandDetailPage from './pages/BrandDetailPage';
import CompetitionDetailPage from './pages/CompetitionDetailPage';
import PlayerDetailPage from './pages/PlayerDetailPage';
import MasterJerseyDetailPage from './pages/MasterJerseyDetailPage';
import AuthModal from './AuthModal';

// Get the backend URL from environment variables
const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

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
    if (path === '/vestiaire') return 'vestiaire';
    if (path === '/collections') return 'collections';
    if (path === '/contributions') return 'contributions';
    if (path === '/teams') return 'teams';
    if (path === '/brands') return 'brands';
    if (path === '/players') return 'players';
    if (path === '/competitions') return 'competitions';
    if (path === '/master-jerseys') return 'master-jerseys';
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
    // Reload collaborative data
    loadCollaborativeData();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/');
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
        fetch(`${API}/api/master-jerseys`)
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
          // Switch to explore view with search results
          setCurrentView('explore');
        }
      } catch (error) {
        console.error('Search error:', error);
      }
    }
  };

  // Render current view
  const renderCurrentView = () => {
    const commonProps = {
      user,
      API,
      teams,
      brands,
      players,
      competitions,
      masterJerseys,
      onDataUpdate: loadCollaborativeData,
      searchQuery
    };

    switch (currentView) {
      case 'home':
        return <CollaborativeHomepage {...commonProps} onViewChange={setCurrentView} />;
      
      case 'catalogue':
        return <CataloguePage {...commonProps} />;
      
      case 'vestiaire':
        return <VestiairePage {...commonProps} />;
      
      case 'collections':
        return <CollectionsPage {...commonProps} />;
      
      case 'contributions':
        return <EnhancedContributionsPage {...commonProps} />;
      
      case 'contribute': // Legacy support
        return <EnhancedContributionsPage {...commonProps} />;
      
      // Legacy routes (keep for direct access)
      case 'explore':
        return <CollaborativeExplorePage {...commonProps} />;
      
      case 'teams':
        return <CollaborativeTeamsPage {...commonProps} />;
      
      case 'brands':
        return <CollaborativeBrandsPage {...commonProps} />;
      
      case 'players':
        return <CollaborativePlayersPage {...commonProps} />;
      
      case 'competitions':
        return <CollaborativeCompetitionsPage {...commonProps} />;
      
      case 'master-jerseys':
        return <CollaborativeMasterJerseyPage {...commonProps} />;
      
      case 'profile':
        return <CollaborativeProfilePage {...commonProps} />;
      
      case 'admin':
        return <AdminDashboard user={user} API={API} />;
      
      default:
        return <CollaborativeHomepage {...commonProps} onViewChange={setCurrentView} />;
    }
  };

  return (
    <div className="collaborative-app min-h-screen bg-gray-50">
      {/* Header */}
      <CollaborativeHeader
        user={user}
        currentView={currentView}
        onViewChange={setCurrentView}
        onSearch={handleSearch}
        onLogin={() => setShowAuthModal(true)}
        onLogout={handleLogout}
        searchQuery={searchQuery}
      />

      {/* Main Content */}
      <main className="min-h-screen">
        {renderCurrentView()}
      </main>

          {/* Auth Modal */}
          {showAuthModal && (
            <div className="fixed inset-0 z-50">
              <AuthModal
                isOpen={showAuthModal}
                onClose={() => setShowAuthModal(false)}
                onLoginSuccess={handleLoginSuccess}
              />
            </div>
          )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement des données collaboratives...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollaborativeApp;