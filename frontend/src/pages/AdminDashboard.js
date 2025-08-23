import React, { useState, useEffect } from 'react';

const AdminDashboard = ({ user, API }) => {
  const [activeModule, setActiveModule] = useState('overview');
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

  // Charger les données du dashboard
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Simuler le chargement des métriques admin
      const mockData = {
        users: { total: 1247, active: 856, new_today: 23 },
        contributions: { pending: 23, approved: 156, rejected: 12 },
        entities: { teams: 348, brands: 67, players: 89, competitions: 29 },
        system: { uptime: '99.9%', performance: 'excellent', alerts: 2 }
      };
      setDashboardData(mockData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
    setLoading(false);
  };

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

  // Check if user is admin (topkitfr@gmail.com)
  if (!user || user.email !== 'topkitfr@gmail.com') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Accès Refusé</h2>
          <p className="text-gray-600">Seul l'administrateur TopKit peut accéder à cette interface.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header Admin */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-2xl">🛡️</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">TopKit Administration</h1>
              <p className="text-sm text-gray-600">Interface complète de gestion • Version Enterprise</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">Super Admin</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>
            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-red-600 font-bold">A</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        
        {/* Sidebar Navigation */}
        <div className="w-80 bg-white border-r border-gray-200 min-h-screen">
          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Modules Disponibles</h2>
            
            {/* Module Selection */}
            <div className="space-y-2">
              {adminModules.map(module => (
                <div
                  key={module.id}
                  onClick={() => setActiveModule(module.id)}
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

            {/* Quick Stats */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Stats Rapides</h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Utilisateurs:</span>
                  <span className="font-medium">{dashboardData.users?.total || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">En attente:</span>
                  <span className="font-medium text-orange-600">{dashboardData.contributions?.pending || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Équipes:</span>
                  <span className="font-medium">{dashboardData.entities?.teams || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Module Content will be rendered here */}
          <ModuleContent 
            activeModule={activeModule} 
            dashboardData={dashboardData}
            API={API}
            user={user}
          />
        </div>
      </div>
    </div>
  );
};

// Component for rendering different module contents
const ModuleContent = ({ activeModule, dashboardData, API, user }) => {
  
  switch (activeModule) {
    case 'overview':
      return <OverviewModule dashboardData={dashboardData} />;
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
      return <OverviewModule dashboardData={dashboardData} />;
  }
};

// Overview Module - Dashboard Principal
const OverviewModule = ({ dashboardData }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">📊 Dashboard Principal</h2>
      <p className="text-gray-600 mt-1">Vue d'ensemble temps réel de votre plateforme TopKit</p>
    </div>

    {/* Metrics Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      
      {/* Users Metric */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Utilisateurs Totaux</p>
            <p className="text-3xl font-bold text-gray-900">{dashboardData.users?.total || 0}</p>
            <p className="text-sm text-green-600 mt-1">+{dashboardData.users?.new_today || 0} aujourd'hui</p>
          </div>
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span className="text-blue-600 text-xl">👥</span>
          </div>
        </div>
      </div>

      {/* Contributions Metric */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Contributions</p>
            <p className="text-3xl font-bold text-gray-900">{dashboardData.contributions?.approved || 0}</p>
            <p className="text-sm text-orange-600 mt-1">{dashboardData.contributions?.pending || 0} en attente</p>
          </div>
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <span className="text-green-600 text-xl">✏️</span>
          </div>
        </div>
      </div>

      {/* Entities Metric */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Entités Totales</p>
            <p className="text-3xl font-bold text-gray-900">
              {(dashboardData.entities?.teams || 0) + (dashboardData.entities?.brands || 0) + (dashboardData.entities?.players || 0)}
            </p>
            <p className="text-sm text-gray-500 mt-1">Teams, Brands, Players</p>
          </div>
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <span className="text-purple-600 text-xl">🏆</span>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Santé Système</p>
            <p className="text-3xl font-bold text-green-600">{dashboardData.system?.uptime || '99.9%'}</p>
            <p className="text-sm text-gray-500 mt-1">Uptime</p>
          </div>
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <span className="text-green-600 text-xl">⚡</span>
          </div>
        </div>
      </div>
    </div>

    {/* Quick Actions */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions Rapides</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-4 text-left transition-colors">
          <div className="text-green-600 text-xl mb-2">✅</div>
          <h4 className="font-medium text-green-900">Approuver Tout</h4>
          <p className="text-sm text-green-700">Approuver toutes les contributions en attente</p>
        </button>
        <button className="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-4 text-left transition-colors">
          <div className="text-blue-600 text-xl mb-2">💾</div>
          <h4 className="font-medium text-blue-900">Export Backup</h4>
          <p className="text-sm text-blue-700">Télécharger sauvegarde complète</p>
        </button>
        <button className="bg-orange-50 hover:bg-orange-100 border border-orange-200 rounded-lg p-4 text-left transition-colors">
          <div className="text-orange-600 text-xl mb-2">🔧</div>
          <h4 className="font-medium text-orange-900">Mode Maintenance</h4>
          <p className="text-sm text-orange-700">Activer maintenance planifiée</p>
        </button>
      </div>
    </div>

    {/* Recent Activity */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Activité Récente</h3>
      <div className="space-y-4">
        <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <span className="text-green-600 text-sm">✓</span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Contribution approuvée</p>
            <p className="text-xs text-gray-500">FC Barcelona logo - Il y a 2 minutes</p>
          </div>
        </div>
        <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-blue-600 text-sm">👤</span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Nouvel utilisateur inscrit</p>
            <p className="text-xs text-gray-500">user@example.com - Il y a 5 minutes</p>
          </div>
        </div>
        <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
            <span className="text-orange-600 text-sm">⚠️</span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Contribution signalée</p>
            <p className="text-xs text-gray-500">Nike brand modification - Il y a 10 minutes</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Users Module - Gestion Utilisateurs
const UsersModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">👥 Gestion Utilisateurs</h2>
      <p className="text-gray-600 mt-1">Assignation rôles, profils détaillés, sanctions et KYC</p>
    </div>

    {/* User Management Preview */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Fonctionnalités Utilisateurs</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Role Management */}
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-2xl mb-3">🎭</div>
          <h4 className="font-semibold text-gray-900 mb-2">Assignation Rôles</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Super Admin</li>
            <li>• Admin</li>
            <li>• Modérateur</li>
            <li>• VIP</li>
            <li>• User</li>
            <li>• Suspect</li>
            <li>• Banni</li>
          </ul>
        </div>

        {/* User Profiles */}
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-2xl mb-3">📋</div>
          <h4 className="font-semibold text-gray-900 mb-2">Profils Détaillés</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Historique complet</li>
            <li>• Score réputation</li>
            <li>• Sanctions actives</li>
            <li>• Contributions</li>
            <li>• Temps connexion</li>
            <li>• Géolocalisation</li>
          </ul>
        </div>

        {/* Mass Actions */}
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-2xl mb-3">⚡</div>
          <h4 className="font-semibold text-gray-900 mb-2">Actions en Masse</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Promotion groupe</li>
            <li>• Suspension multiple</li>
            <li>• Export données</li>
            <li>• Notifications bulk</li>
            <li>• Reset passwords</li>
            <li>• Badge assignment</li>
          </ul>
        </div>
      </div>
    </div>

    {/* User List Preview */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Aperçu Liste Utilisateurs</h3>
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
            {/* More users... */}
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
const DataManagementModule = ({ API }) => (
  <div>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-gray-900">💾 Data Management Enterprise</h2>
      <p className="text-gray-600 mt-1">Import/Export, backup, migration, data cleaning</p>
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