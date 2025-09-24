import React, { useState, useEffect } from 'react';

const AdminDashboard = ({ user, API }) => {
  const [activeModule, setActiveModule] = useState('overview');
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // System settings state
  const [systemSettings, setSystemSettings] = useState({
    auto_approval_enabled: true,
    admin_notifications: true,
    community_voting_enabled: true
  });
  const [settingsLoading, setSettingsLoading] = useState(false);

  // Admin modules avec leurs configurations
  const adminModules = [
    { 
      id: 'overview', 
      name: '📊 Dashboard Principal', 
      description: 'Métriques temps réel, alertes, actions rapides',
      status: 'recommended'
    },
    { 
      id: 'users', 
      name: '👥 Gestion Utilisateurs', 
      description: 'Rôles, profils, sanctions, KYC',
      status: 'recommended'
    },
    { 
      id: 'moderation', 
      name: '🔍 Modération Intelligente', 
      description: 'Queue contributions, IA assistant, modération rapide',
      status: 'recommended'
    },
    { 
      id: 'analytics', 
      name: '📈 Analytics & BI', 
      description: 'Dashboards interactifs, KPIs, rapports automatiques',
      status: 'premium'
    },
    { 
      id: 'data', 
      name: '💾 Data Management', 
      description: 'Import/Export CSV, backup, migration, cleaning',
      status: 'essential'
    },
    { 
      id: 'security', 
      name: '🛡️ Sécurité & Compliance', 
      description: 'Audit trail, RGPD, anti-fraud, contrôle accès',
      status: 'enterprise'
    },
    { 
      id: 'devtools', 
      name: '🔧 Outils Développeur', 
      description: 'Performance monitor, API management, debug console',
      status: 'advanced'
    },
    { 
      id: 'settings', 
      name: '⚙️ Configuration Système', 
      description: 'Settings globaux, integrations, workflow automation',
      status: 'essential'
    },
    { 
      id: 'ai', 
      name: '🤖 IA Admin Assistant', 
      description: 'Auto-modération, détection anomalies, insights intelligents',
      status: 'premium'
    },
    { 
      id: 'mobile', 
      name: '📱 Admin Mobile', 
      description: 'App dédiée, notifications push, quick actions',
      status: 'premium'
    },
    { 
      id: 'vip', 
      name: '👑 VIP Management', 
      description: 'Utilisateurs premium, benefits exclusifs, loyalty program',
      status: 'business'
    },
    { 
      id: 'campaigns', 
      name: '🎯 Campaign Manager', 
      description: 'Défis communautaires, événements, gamification',
      status: 'business'
    }
  ];

  // Load system settings on component mount
  useEffect(() => {
    loadSystemSettings();
    loadDashboardData();
  }, [activeModule]);

  const loadSystemSettings = async () => {
    try {
      const response = await fetch(`${API}/api/admin/settings`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const settings = await response.json();
        setSystemSettings(settings);
      }
    } catch (error) {
      console.error('Error loading system settings:', error);
    }
  };

  const updateSystemSettings = async (newSettings) => {
    setSettingsLoading(true);
    try {
      const response = await fetch(`${API}/api/admin/settings`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSettings)
      });
      
      if (response.ok) {
        const result = await response.json();
        setSystemSettings(result.settings);
        alert('Settings updated successfully!');
      } else {
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || errorData?.message || `HTTP ${response.status}: Settings update failed`;
        console.error('Settings update error:', errorData);
        alert(`Error updating settings: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error updating settings:', error);
      alert('Error updating settings');
    } finally {
      setSettingsLoading(false);
    }
  };

  const loadDashboardData = async () => {
    if (activeModule === 'overview') {
      setLoading(true);
      try {
        const response = await fetch(`${API}/api/admin/dashboard-stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setDashboardData(data);
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // Check if user is admin (topkitfr@gmail.com or emergency.admin@topkit.test or has admin role)
  if (!user || (user.email !== 'topkitfr@gmail.com' && user.email !== 'emergency.admin@topkit.test' && user.role !== 'admin')) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Accès Refusé</h2>
          <p className="text-gray-600">Seul l'administrateur TopKit peut accéder à cette interface.</p>
        </div>
      </div>
    );
  }

  const getActiveModuleData = () => {
    return adminModules.find(module => module.id === activeModule) || adminModules[0];
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header - Design Standard TopKit */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Administration TopKit</h1>
          <p className="text-gray-600">
            Interface complète de gestion et supervision de la plateforme
          </p>
        </div>
        
        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <span className="mr-2">🛡️</span>
          Modules
        </button>

        {/* Desktop User Info */}
        <div className="hidden md:flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">Super Admin</p>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>
          <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
            <span className="text-red-600 font-bold">A</span>
          </div>
        </div>
      </div>

      {/* Stats rapides - Design Standard TopKit */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{dashboardData.users?.total || 1247}</div>
          <div className="text-sm text-blue-700">Utilisateurs</div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{dashboardData.contributions?.approved || 156}</div>
          <div className="text-sm text-green-700">Contributions</div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{dashboardData.entities?.teams || 348}</div>
          <div className="text-sm text-purple-700">Équipes</div>
        </div>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">{dashboardData.contributions?.pending || 23}</div>
          <div className="text-sm text-orange-700">En attente</div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 md:hidden">
          <div className="fixed inset-y-0 left-0 w-80 bg-white shadow-xl">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Modules Admin</h2>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
            </div>
            
            <div className="p-4 overflow-y-auto">
              <ModuleSelector 
                modules={adminModules}
                activeModule={activeModule}
                setActiveModule={setActiveModule}
                setMobileMenuOpen={setMobileMenuOpen}
              />
            </div>
          </div>
        </div>
      )}

      {/* Desktop Module Selector */}
      <div className="hidden md:block mb-8">
        <ModuleSelector 
          modules={adminModules}
          activeModule={activeModule}
          setActiveModule={setActiveModule}
          isDesktop={true}
        />
      </div>

      {/* Active Module Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{getActiveModuleData().name}</h2>
            <p className="text-sm text-gray-600">{getActiveModuleData().description}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getModuleStatusColor(getActiveModuleData().status)}`}>
            {getActiveModuleData().status}
          </span>
        </div>
        
        <ModuleContent 
          activeModule={activeModule} 
          dashboardData={dashboardData}
          API={API}
          user={user}
          systemSettings={systemSettings}
          updateSystemSettings={updateSystemSettings}
          settingsLoading={settingsLoading}
          loading={loading}
        />
      </div>
    </div>
  );
};

// Module Selector Component
const ModuleSelector = ({ modules, activeModule, setActiveModule, setMobileMenuOpen, isDesktop = false }) => {
  const handleModuleClick = (moduleId) => {
    setActiveModule(moduleId);
    if (setMobileMenuOpen) {
      setMobileMenuOpen(false);
    }
  };

  if (isDesktop) {
    // Desktop: Grid layout
    return (
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Modules Disponibles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {modules.map(module => (
            <ModuleCard 
              key={module.id}
              module={module}
              isActive={activeModule === module.id}
              onClick={() => handleModuleClick(module.id)}
            />
          ))}
        </div>
      </div>
    );
  }

  // Mobile: List layout
  return (
    <div className="space-y-2">
      {modules.map(module => (
        <div
          key={module.id}
          onClick={() => handleModuleClick(module.id)}
          className={`p-3 rounded-lg cursor-pointer transition-all border ${
            activeModule === module.id 
              ? 'bg-blue-50 border-blue-200 shadow-sm' 
              : 'hover:bg-gray-50 border-transparent'
          }`}
        >
          <div className="flex items-start justify-between mb-1">
            <h3 className={`text-sm font-medium ${
              activeModule === module.id ? 'text-blue-900' : 'text-gray-900'
            }`}>
              {module.name}
            </h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModuleStatusColor(module.status)}`}>
              {module.status}
            </span>
          </div>
          <p className="text-xs text-gray-600">{module.description}</p>
        </div>
      ))}
    </div>
  );
};

// Module Card Component
const ModuleCard = ({ module, isActive, onClick }) => (
  <div
    onClick={onClick}
    className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
      isActive 
        ? 'bg-blue-50 border-blue-200 shadow-sm' 
        : 'bg-white border-gray-200 hover:border-gray-300'
    }`}
  >
    <div className="flex items-start justify-between mb-2">
      <h3 className={`text-sm font-medium ${
        isActive ? 'text-blue-900' : 'text-gray-900'
      }`}>
        {module.name}
      </h3>
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModuleStatusColor(module.status)}`}>
        {module.status}
      </span>
    </div>
    <p className="text-xs text-gray-600">{module.description}</p>
  </div>
);

const getModuleStatusColor = (status) => {
  const colors = {
    'recommended': 'bg-green-100 text-green-800',
    'essential': 'bg-blue-100 text-blue-800', 
    'premium': 'bg-purple-100 text-purple-800',
    'enterprise': 'bg-red-100 text-red-800',
    'advanced': 'bg-yellow-100 text-yellow-800',
    'business': 'bg-pink-100 text-pink-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

// Component for rendering different module contents
const ModuleContent = ({ activeModule, dashboardData, API, user, systemSettings, updateSystemSettings, settingsLoading, loading }) => {
  
  switch (activeModule) {
    case 'overview':
      return <OverviewModule 
        dashboardData={dashboardData} 
        systemSettings={systemSettings}
        updateSystemSettings={updateSystemSettings}
        settingsLoading={settingsLoading}
        loading={loading}
      />;
    case 'users':
      return <UsersModule API={API} />;
    case 'moderation':
      return <ModerationModule API={API} />;
    case 'analytics':
      return <AnalyticsModule dashboardData={dashboardData} />;
    case 'data':
      return <DataManagementModule API={API} />;
    case 'security':
      return <SecurityModule API={API} />;
    case 'devtools':
      return <DevToolsModule API={API} />;
    case 'settings':
      return <SettingsModule API={API} />;
    case 'ai':
      return <AIAssistantModule API={API} />;
    case 'mobile':
      return <MobileAdminModule />;
    case 'vip':
      return <VIPManagementModule API={API} />;
    case 'campaigns':
      return <CampaignManagerModule API={API} />;
    default:
      return <OverviewModule 
        dashboardData={dashboardData} 
        systemSettings={systemSettings}
        updateSystemSettings={updateSystemSettings}
        settingsLoading={settingsLoading}
        loading={loading}
      />;
  }
};

// Overview Module - Dashboard Principal
const OverviewModule = ({ dashboardData, systemSettings, updateSystemSettings, settingsLoading, loading }) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold text-gray-900">📊 Dashboard Principal</h2>
      <div className="text-sm text-gray-500">Temps réel</div>
    </div>

    {/* System Settings Toggle */}
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">⚙️ Paramètres Système</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <span className="font-medium">Auto-Approval Mode</span>
            <p className="text-sm text-gray-600">
              {systemSettings.auto_approval_enabled 
                ? "✅ Activated - New entities appear directly in catalogue" 
                : "🔄 Disabled - New entities require manual approval"}
            </p>
          </div>
          <button
            onClick={() => updateSystemSettings({
              auto_approval_enabled: !systemSettings.auto_approval_enabled
            })}
            disabled={settingsLoading}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              systemSettings.auto_approval_enabled ? 'bg-green-600' : 'bg-gray-300'
            } ${settingsLoading ? 'opacity-50' : ''}`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                systemSettings.auto_approval_enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <span className="font-medium">Community Voting</span>
            <p className="text-sm text-gray-600">Enable community voting on contributions</p>
          </div>
          <button
            onClick={() => updateSystemSettings({
              community_voting_enabled: !systemSettings.community_voting_enabled
            })}
            disabled={settingsLoading}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              systemSettings.community_voting_enabled ? 'bg-blue-600' : 'bg-gray-300'
            } ${settingsLoading ? 'opacity-50' : ''}`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                systemSettings.community_voting_enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
    </div>

    {/* Dashboard Statistics */}
    {loading ? (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading dashboard statistics...</p>
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Users Stats */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Users</p>
              <p className="text-3xl font-bold">{dashboardData.users?.total || 0}</p>
              <p className="text-blue-100 text-sm">Active: {dashboardData.users?.active_30d || 0}</p>
            </div>
            <div className="text-4xl opacity-80">👥</div>
          </div>
        </div>

        {/* Content Stats */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Total Content</p>
              <p className="text-3xl font-bold">
                {(dashboardData.content?.teams || 0) + 
                 (dashboardData.content?.competitions || 0) + 
                 (dashboardData.content?.brands || 0)}
              </p>
              <p className="text-green-100 text-sm">Teams: {dashboardData.content?.teams || 0}</p>
            </div>
            <div className="text-4xl opacity-80">🏆</div>
          </div>
        </div>

        {/* Collections Stats */}
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Collections</p>
              <p className="text-3xl font-bold">
                {(dashboardData.content?.personal_kits || 0) + (dashboardData.content?.wanted_kits || 0)}
              </p>
              <p className="text-purple-100 text-sm">Personal: {dashboardData.content?.personal_kits || 0}</p>
            </div>
            <div className="text-4xl opacity-80">👕</div>
          </div>
        </div>

        {/* Moderation Stats */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">Pending Review</p>
              <p className="text-3xl font-bold">{dashboardData.moderation?.pending_contributions || 0}</p>
              <p className="text-orange-100 text-sm">
                Rate: {dashboardData.moderation?.approval_rate || 0}%
              </p>
            </div>
            <div className="text-4xl opacity-80">🔍</div>
          </div>
        </div>
      </div>
    )}

    {/* System Status */}
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">System Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${
            systemSettings.auto_approval_enabled ? 'bg-green-500' : 'bg-orange-500'
          }`}></div>
          <p className="text-sm font-medium">Auto Approval</p>
          <p className="text-xs text-gray-600">
            {systemSettings.auto_approval_enabled ? 'Active' : 'Manual'}
          </p>
        </div>
        <div className="text-center">
          <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${
            systemSettings.community_voting_enabled ? 'bg-green-500' : 'bg-gray-400'
          }`}></div>
          <p className="text-sm font-medium">Community Voting</p>
          <p className="text-xs text-gray-600">
            {systemSettings.community_voting_enabled ? 'Enabled' : 'Disabled'}
          </p>
        </div>
        <div className="text-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
          <p className="text-sm font-medium">System Health</p>
          <p className="text-xs text-gray-600">Operational</p>
        </div>
      </div>
    </div>
  </div>
);

// Users Module - Gestion Utilisateurs
const UsersModule = ({ API }) => (
  <div className="space-y-6">

    {/* User Management Features */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      {/* Role Management */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="text-3xl mb-3">🎭</div>
        <h4 className="font-semibold text-gray-900 mb-3">Assignation Rôles</h4>
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center justify-between">
            <span>Super Admin</span>
            <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">1</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Admin</span>
            <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs">2</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Modérateur</span>
            <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">5</span>
          </div>
          <div className="flex items-center justify-between">
            <span>VIP</span>
            <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">12</span>
          </div>
          <div className="flex items-center justify-between">
            <span>User</span>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">1,227</span>
          </div>
        </div>
      </div>

      {/* User Profiles */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="text-3xl mb-3">📋</div>
        <h4 className="font-semibold text-gray-900 mb-3">Profils Détaillés</h4>
        <ul className="text-sm text-gray-600 space-y-2">
          <li className="flex items-center">
            <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
            Historique complet
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
            Score réputation
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></span>
            Sanctions actives
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
            Contributions
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
            Géolocalisation
          </li>
        </ul>
      </div>

      {/* Mass Actions */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="text-3xl mb-3">⚡</div>
        <h4 className="font-semibold text-gray-900 mb-3">Actions en Masse</h4>
        <div className="space-y-2">
          <button className="w-full bg-blue-50 hover:bg-blue-100 text-blue-700 py-2 px-3 rounded text-sm transition-colors">
            Promotion groupe
          </button>
          <button className="w-full bg-orange-50 hover:bg-orange-100 text-orange-700 py-2 px-3 rounded text-sm transition-colors">
            Suspension multiple
          </button>
          <button className="w-full bg-green-50 hover:bg-green-100 text-green-700 py-2 px-3 rounded text-sm transition-colors">
            Export données
          </button>
          <button className="w-full bg-purple-50 hover:bg-purple-100 text-purple-700 py-2 px-3 rounded text-sm transition-colors">
            Notifications bulk
          </button>
        </div>
      </div>
    </div>

    {/* User List Preview */}
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Liste Utilisateurs</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-medium text-gray-900">Utilisateur</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">Rôle</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">Réputation</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">Dernière activité</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-gray-100">
              <td className="py-3 px-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 text-sm font-medium">S</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">steinmetzlivio@gmail.com</p>
                    <p className="text-xs text-gray-500">ID: user_123</p>
                  </div>
                </div>
              </td>
              <td className="py-3 px-4">
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">User</span>
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">85%</span>
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{width: '85%'}}></div>
                  </div>
                </div>
              </td>
              <td className="py-3 px-4 text-sm text-gray-600">Il y a 2h</td>
              <td className="py-3 px-4">
                <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">Voir détails</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

// Moderation Module
const ModerationModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">🔍 Modération Intelligente</h2>
      <p className="text-gray-600 mt-1">Queue unifiée, IA assistant, modération rapide</p>
    </div>

    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 IA Assistant de Modération</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 border border-purple-200">
          <h4 className="font-medium text-purple-900 mb-2">Auto-détection</h4>
          <p className="text-sm text-purple-700">Contenu inapproprié, spam, duplicats</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-blue-200">
          <h4 className="font-medium text-blue-900 mb-2">Scores de Confiance</h4>
          <p className="text-sm text-blue-700">Probabilité d'approbation calculée</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-green-200">
          <h4 className="font-medium text-green-900 mb-2">Recommandations</h4>
          <p className="text-sm text-green-700">Actions suggérées basées sur l'historique</p>
        </div>
      </div>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Queue de Modération</h3>
      <p className="text-gray-600 mb-4">Interface de modération rapide avec raccourcis clavier et swipe gestures</p>
      
      <div className="space-y-4">
        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">🏟️ ÉQUIPE</span>
              <h4 className="font-medium text-gray-900">Modification FC Barcelona</h4>
            </div>
            <div className="text-xs text-gray-500">Il y a 5min</div>
          </div>
          
          <p className="text-sm text-gray-600 mb-3">Mise à jour du nom et ajout du logo officiel</p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Confiance IA:</span>
              <div className="flex items-center space-x-1">
                <span className="text-green-600 font-medium">92%</span>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Recommandé</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button className="bg-red-50 hover:bg-red-100 text-red-700 px-3 py-1 rounded text-sm">
                ❌ Rejeter (X)
              </button>
              <button className="bg-green-50 hover:bg-green-100 text-green-700 px-3 py-1 rounded text-sm">
                ✅ Approuver (A)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Data Management Module 
const DataManagementModule = ({ API }) => {
  const [clearingData, setClearingData] = useState(false);
  
  // Data clearing functions
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
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
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
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
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
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
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
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">💾 Data Management Enterprise</h2>
        <p className="text-gray-600 mt-1">Import/Export, backup, migration, data cleaning</p>
      </div>

      {/* WARNING SECTION FOR KIT CLEARING */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <div className="flex items-center mb-3">
          <span className="text-2xl mr-3">⚠️</span>
          <h3 className="text-xl font-bold text-red-800">Zone Dangereuse - Suppression des Kits</h3>
        </div>
        <p className="text-red-700 mb-4">
          <strong>ATTENTION:</strong> Les actions ci-dessous suppriment définitivement des données de la base. 
          Ces actions sont <strong>IRRÉVERSIBLES</strong>. Utilisez avec précaution.
        </p>

        {/* Kit Clearing Actions */}
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

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <span className="text-xl mr-2">ℹ️</span>
            <h4 className="text-lg font-bold text-blue-800">Instructions d'utilisation</h4>
          </div>
          <ul className="space-y-2 text-sm text-blue-700">
            <li>• <strong>Master Kits seulement:</strong> Utilisez pour réinitialiser les données de référence tout en gardant les collections utilisateurs</li>
            <li>• <strong>Collections seulement:</strong> Utilisez pour nettoyer les données personnelles tout en gardant les références</li>
            <li>• <strong>Suppression totale:</strong> Utilisez uniquement pour un reset complet de la plateforme</li>
            <li>• <strong>Toutes les suppressions sont définitives</strong> - Aucune récupération possible</li>
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        
        {/* Import/Export */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📤 Import/Export</h3>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Export CSV Complet</h4>
              <p className="text-sm text-gray-600 mb-3">Télécharger toutes les données en CSV avec mapping intelligent</p>
              <div className="flex space-x-2">
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm">
                  📥 Export Teams
                </button>
                <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm">
                  📥 Export All
                </button>
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Import en Masse</h4>
              <p className="text-sm text-gray-600 mb-3">Importer CSV/Excel avec validation automatique</p>
              <div className="border-dashed border-2 border-gray-300 rounded-lg p-4 text-center">
                <div className="text-gray-400 text-2xl mb-2">📁</div>
                <p className="text-sm text-gray-500">Glisser-déposer vos fichiers ici</p>
              </div>
            </div>
          </div>
        </div>

        {/* Backup System */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🛡️ Système de Backup</h3>
          <div className="space-y-4">
            <div className="border border-green-200 bg-green-50 rounded-lg p-4">
              <h4 className="font-medium text-green-900 mb-2">Backup Automatique</h4>
              <p className="text-sm text-green-700 mb-2">Dernière sauvegarde: Aujourd'hui 03:00</p>
              <div className="text-xs text-green-600">✅ Backup quotidien actif</div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Backup Manuel</h4>
              <p className="text-sm text-gray-600 mb-3">Créer une sauvegarde complète maintenant</p>
              <button className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded text-sm w-full">
                🔄 Créer Backup Maintenant
              </button>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Restauration Point-in-Time</h4>
              <p className="text-sm text-gray-600 mb-3">Restaurer à une date spécifique</p>
              <input type="date" className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
            </div>
          </div>
        </div>
      </div>

      {/* Data Quality Tools */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔧 Outils Qualité des Données</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">🔍</div>
            <h4 className="font-medium text-gray-900 mb-1">Détection Doublons</h4>
            <p className="text-xs text-gray-600 mb-3">Identifier et fusionner les entrées en double</p>
            <button className="bg-yellow-600 text-white px-3 py-1 rounded text-sm">Scanner</button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">✨</div>
            <h4 className="font-medium text-gray-900 mb-1">Normalisation</h4>
            <p className="text-xs text-gray-600 mb-3">Standardiser formats et conventions</p>
            <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm">Normaliser</button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">✅</div>
            <h4 className="font-medium text-gray-900 mb-1">Validation</h4>
            <p className="text-xs text-gray-600 mb-3">Vérifier intégrité et cohérence</p>
            <button className="bg-green-600 text-white px-3 py-1 rounded text-sm">Valider</button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Analytics Module
const AnalyticsModule = ({ dashboardData }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">📈 Analytics & Business Intelligence</h2>
      <p className="text-gray-600 mt-1">Dashboards interactifs, KPIs métier, rapports automatiques</p>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 KPIs Métier</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
          <div className="text-2xl text-blue-600 mb-2">📈</div>
          <div className="text-2xl font-bold text-blue-900">+15.2%</div>
          <div className="text-sm text-blue-700">Croissance Utilisateurs</div>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
          <div className="text-2xl text-green-600 mb-2">⚡</div>
          <div className="text-2xl font-bold text-green-900">94.8%</div>
          <div className="text-sm text-green-700">Taux d'Engagement</div>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
          <div className="text-2xl text-purple-600 mb-2">🎯</div>
          <div className="text-2xl font-bold text-purple-900">88.3%</div>
          <div className="text-sm text-purple-700">Qualité Contributions</div>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
          <div className="text-2xl text-orange-600 mb-2">👥</div>
          <div className="text-2xl font-bold text-orange-900">67.1%</div>
          <div className="text-sm text-orange-700">Rétention 30j</div>
        </div>
      </div>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Rapports Automatiques</h3>
      <p className="text-gray-600 mb-4">Rapports générés automatiquement et envoyés par email</p>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div>
            <h4 className="font-medium text-gray-900">Rapport Hebdomadaire</h4>
            <p className="text-sm text-gray-600">KPIs, croissance, alertes • Envoyé chaque lundi</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Actif</span>
            <button className="text-blue-600 hover:text-blue-800 text-sm">Configurer</button>
          </div>
        </div>
        
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div>
            <h4 className="font-medium text-gray-900">Analyse de Performance</h4>
            <p className="text-sm text-gray-600">Performances système, optimisations • Envoyé chaque mois</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">Inactif</span>
            <button className="text-blue-600 hover:text-blue-800 text-sm">Activer</button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Security Module
const SecurityModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">🛡️ Sécurité & Compliance</h2>
      <p className="text-gray-600 mt-1">Audit trail, RGPD, anti-fraud, contrôle accès</p>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      
      {/* Audit Trail */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📜 Audit Trail</h3>
        <p className="text-sm text-gray-600 mb-4">Traçabilité complète de toutes les actions administratives</p>
        
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Admin Login</p>
              <p className="text-xs text-gray-500">topkitfr@gmail.com • 192.168.1.1 • Il y a 2h</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">User Role Changed</p>
              <p className="text-xs text-gray-500">user123 → Moderator • Il y a 4h</p>
            </div>
          </div>
        </div>
        
        <button className="w-full mt-4 bg-blue-50 hover:bg-blue-100 text-blue-700 py-2 rounded text-sm font-medium">
          Voir Audit Complet
        </button>
      </div>

      {/* RGPD Compliance */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Conformité RGPD</h3>
        <div className="space-y-4">
          <div className="border border-gray-200 rounded-lg p-3">
            <h4 className="font-medium text-gray-900 mb-1">Export Données Utilisateur</h4>
            <p className="text-xs text-gray-600 mb-2">Générer export complet pour un utilisateur</p>
            <div className="flex space-x-2">
              <input 
                type="email" 
                placeholder="Email utilisateur"
                className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
              />
              <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm">Export</button>
            </div>
          </div>
          
          <div className="border border-red-200 bg-red-50 rounded-lg p-3">
            <h4 className="font-medium text-red-900 mb-1">Suppression Définitive</h4>
            <p className="text-xs text-red-700 mb-2">Supprimer toutes les données d'un utilisateur</p>
            <button className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm">
              Supprimer Utilisateur
            </button>
          </div>
        </div>
      </div>
    </div>

    {/* Anti-Fraud */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🚨 Système Anti-Fraud</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-4 border border-orange-200 bg-orange-50 rounded-lg">
          <div className="text-2xl text-orange-600 mb-2">👥</div>
          <div className="text-lg font-bold text-orange-900">3</div>
          <div className="text-sm text-orange-700">Multi-comptes détectés</div>
        </div>
        <div className="text-center p-4 border border-red-200 bg-red-50 rounded-lg">
          <div className="text-2xl text-red-600 mb-2">⚠️</div>
          <div className="text-lg font-bold text-red-900">1</div>
          <div className="text-sm text-red-700">Comportement suspect</div>
        </div>
        <div className="text-center p-4 border border-green-200 bg-green-50 rounded-lg">
          <div className="text-2xl text-green-600 mb-2">✅</div>
          <div className="text-lg font-bold text-green-900">99.2%</div>
          <div className="text-sm text-green-700">Taux de confiance</div>
        </div>
      </div>
    </div>
  </div>
);

// Dev Tools Module
const DevToolsModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">🔧 Outils Développeur</h2>
      <p className="text-gray-600 mt-1">Performance monitor, API management, debug console</p>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      
      {/* Performance Monitor */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Performance Monitor</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
            <span className="text-sm font-medium text-green-900">Temps de réponse API</span>
            <span className="text-sm text-green-700">127ms</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
            <span className="text-sm font-medium text-blue-900">Requêtes/minute</span>
            <span className="text-sm text-blue-700">1,247</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
            <span className="text-sm font-medium text-orange-900">Requêtes lentes</span>
            <span className="text-sm text-orange-700">3</span>
          </div>
        </div>
      </div>

      {/* API Management */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔌 API Management</h3>
        <div className="space-y-3">
          <div className="border border-gray-200 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-900">Rate Limiting</span>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Actif</span>
            </div>
            <p className="text-xs text-gray-600">1000 req/hour par utilisateur</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-900">Documentation API</span>
              <button className="text-blue-600 hover:text-blue-800 text-xs">Voir</button>
            </div>
            <p className="text-xs text-gray-600">Swagger UI interactive</p>
          </div>
        </div>
      </div>
    </div>

    {/* Debug Console */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🐛 Console de Debug</h3>
      <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm">
        <div className="text-green-400">[INFO] 2025-08-22 16:47:23 - API Server Started</div>
        <div className="text-blue-400">[DEBUG] 2025-08-22 16:47:24 - Database Connection: OK</div>
        <div className="text-yellow-400">[WARN] 2025-08-22 16:47:25 - High memory usage detected</div>
        <div className="text-green-400">[INFO] 2025-08-22 16:47:26 - Cache cleared successfully</div>
      </div>
      
      <div className="mt-4 flex space-x-2">
        <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">
          Clear Cache
        </button>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
          Restart Services
        </button>
        <button className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm">
          Export Logs
        </button>
      </div>
    </div>
  </div>
);

// Settings Module
const SettingsModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">⚙️ Configuration Système</h2>
      <p className="text-gray-600 mt-1">Settings globaux, intégrations, workflow automation</p>
    </div>

    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🌍 Paramètres Globaux</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Nom de l'application</label>
            <input type="text" defaultValue="TopKit" className="w-full border border-gray-300 rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Mode maintenance</label>
            <select className="w-full border border-gray-300 rounded px-3 py-2">
              <option>Désactivé</option>
              <option>Activé</option>
              <option>Programmé</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔗 Hub d'Intégrations</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Slack</h4>
            <p className="text-xs text-gray-600 mb-3">Notifications équipe admin</p>
            <button className="bg-slack text-white px-3 py-1 rounded text-sm w-full">Connecter</button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Discord</h4>
            <p className="text-xs text-gray-600 mb-3">Bot communauté</p>
            <button className="bg-purple-600 text-white px-3 py-1 rounded text-sm w-full">Configurer</button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Webhooks</h4>
            <p className="text-xs text-gray-600 mb-3">Intégrations custom</p>
            <button className="bg-gray-600 text-white px-3 py-1 rounded text-sm w-full">Gérer</button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// AI Assistant Module
const AIAssistantModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">🤖 IA Admin Assistant</h2>
      <p className="text-gray-600 mt-1">Auto-modération, détection anomalies, insights intelligents</p>
    </div>

    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🧠 Intelligence Artificielle</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-4 border border-purple-200">
          <h4 className="font-medium text-purple-900 mb-2">Auto-Modération</h4>
          <p className="text-sm text-purple-700 mb-3">L'IA pré-approuve les contributions de haute qualité automatiquement</p>
          <div className="flex justify-between items-center">
            <span className="text-sm text-purple-600">Statut:</span>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Actif</span>
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-blue-200">
          <h4 className="font-medium text-blue-900 mb-2">Détection d'Anomalies</h4>
          <p className="text-sm text-blue-700 mb-3">Identification automatique des comportements suspects</p>
          <div className="flex justify-between items-center">
            <span className="text-sm text-blue-600">Alertes:</span>
            <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs">2 nouvelles</span>
          </div>
        </div>
      </div>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Insights Intelligents</h3>
      <div className="space-y-4">
        <div className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-r-lg">
          <h4 className="font-medium text-blue-900 mb-1">📈 Tendance Détectée</h4>
          <p className="text-sm text-blue-800">Pic d'activité sur les équipes de Ligue 1 (+40% cette semaine)</p>
        </div>
        <div className="border-l-4 border-green-500 bg-green-50 p-4 rounded-r-lg">
          <h4 className="font-medium text-green-900 mb-1">✅ Recommandation</h4>
          <p className="text-sm text-green-800">L'utilisateur steinmetzlivio@gmail.com pourrait être promu Modérateur (95% contributions approuvées)</p>
        </div>
        <div className="border-l-4 border-orange-500 bg-orange-50 p-4 rounded-r-lg">
          <h4 className="font-medium text-orange-900 mb-1">⚠️ Attention</h4>
          <p className="text-sm text-orange-800">Augmentation des signalements sur les logos de marques (vérifier qualité)</p>
        </div>
      </div>
    </div>
  </div>
);

// Mobile Admin Module
const MobileAdminModule = () => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">📱 Admin Mobile</h2>
      <p className="text-gray-600 mt-1">App dédiée, notifications push, quick actions</p>
    </div>

    <div className="text-center py-12">
      <div className="text-6xl mb-4">📱</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">Application Mobile Admin</h3>
      <p className="text-gray-600 mb-6">Modération en déplacement avec notifications push instantanées</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
        <div className="border border-gray-200 rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-2">📲 Features</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Modération swipe gauche/droite</li>
            <li>• Push notifications critiques</li>
            <li>• Stats temps réel</li>
            <li>• Actions rapides</li>
          </ul>
        </div>
        <div className="border border-gray-200 rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-2">🚀 Disponibilité</h4>
          <div className="space-y-2">
            <button className="w-full bg-black text-white py-2 px-4 rounded">
              📱 iOS App Store
            </button>
            <button className="w-full bg-green-600 text-white py-2 px-4 rounded">
              🤖 Google Play
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// VIP Management Module
const VIPManagementModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">👑 VIP Management</h2>
      <p className="text-gray-600 mt-1">Utilisateurs premium, benefits exclusifs, loyalty program</p>
    </div>

    <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">💎 Programme VIP</h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-white rounded-lg border border-yellow-200">
          <div className="text-2xl text-yellow-600 mb-2">🥉</div>
          <h4 className="font-medium text-yellow-900">Bronze</h4>
          <p className="text-xs text-yellow-700">25 contributions</p>
        </div>
        <div className="text-center p-4 bg-white rounded-lg border border-gray-300">
          <div className="text-2xl text-gray-600 mb-2">🥈</div>
          <h4 className="font-medium text-gray-900">Argent</h4>
          <p className="text-xs text-gray-700">100 contributions</p>
        </div>
        <div className="text-center p-4 bg-white rounded-lg border border-yellow-400">
          <div className="text-2xl text-yellow-500 mb-2">🥇</div>
          <h4 className="font-medium text-yellow-900">Or</h4>
          <p className="text-xs text-yellow-700">500 contributions</p>
        </div>
        <div className="text-center p-4 bg-white rounded-lg border border-purple-400">
          <div className="text-2xl text-purple-600 mb-2">💎</div>
          <h4 className="font-medium text-purple-900">Diamant</h4>
          <p className="text-xs text-purple-700">1000+ contributions</p>
        </div>
      </div>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Benefits Exclusifs</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div>
            <h4 className="font-medium text-gray-900">Badge Personnalisé</h4>
            <p className="text-sm text-gray-600">Flair unique visible sur profil</p>
          </div>
          <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">VIP Only</span>
        </div>
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div>
            <h4 className="font-medium text-gray-900">Accès Anticipé</h4>
            <p className="text-sm text-gray-600">Nouvelles fonctionnalités en avant-première</p>
          </div>
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">Premium</span>
        </div>
      </div>
    </div>
  </div>
);

// Campaign Manager Module
const CampaignManagerModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">🎯 Campaign Manager</h2>
      <p className="text-gray-600 mt-1">Défis communautaires, événements spéciaux, gamification</p>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🏆 Défis Actifs</h3>
      <div className="space-y-4">
        <div className="border border-green-200 bg-green-50 rounded-lg p-4">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-medium text-green-900">Défi Ligue 1</h4>
            <span className="bg-green-600 text-white px-2 py-1 rounded text-xs">En cours</span>
          </div>
          <p className="text-sm text-green-700 mb-2">Compléter 10 fiches d'équipes de Ligue 1</p>
          <div className="flex justify-between text-xs text-green-600">
            <span>Participants: 23</span>
            <span>Fin: Dans 5 jours</span>
          </div>
        </div>
        
        <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-medium text-blue-900">Mois des Logos</h4>
            <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">Planifié</span>
          </div>
          <p className="text-sm text-blue-700 mb-2">Ajouter des logos haute qualité aux équipes</p>
          <div className="flex justify-between text-xs text-blue-600">
            <span>Récompense: Badge Spécial</span>
            <span>Début: 1er Septembre</span>
          </div>
        </div>
      </div>
    </div>

    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🎮 Système de Gamification</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-4 border border-gray-200 rounded-lg">
          <div className="text-2xl mb-2">🏅</div>
          <h4 className="font-medium text-gray-900 mb-1">Points XP</h4>
          <p className="text-xs text-gray-600">Système de progression</p>
        </div>
        <div className="text-center p-4 border border-gray-200 rounded-lg">
          <div className="text-2xl mb-2">🎖️</div>
          <h4 className="font-medium text-gray-900 mb-1">Badges</h4>
          <p className="text-xs text-gray-600">Achievements déblocables</p>
        </div>
        <div className="text-center p-4 border border-gray-200 rounded-lg">
          <div className="text-2xl mb-2">📊</div>
          <h4 className="font-medium text-gray-900 mb-1">Classements</h4>
          <p className="text-xs text-gray-600">Leaderboards mensuels</p>
        </div>
      </div>
    </div>
  </div>
);

export default AdminDashboard;