import React, { useState } from 'react';
import CollaborativeTeamsPage from './CollaborativeTeamsPage';
import CollaborativeBrandsPage from './CollaborativeBrandsPage';
import CollaborativePlayersPage from './CollaborativePlayersPage';
import CollaborativeCompetitionsPage from './CollaborativeCompetitionsPage';
import CollaborativeMasterJerseyPage from './CollaborativeMasterJerseyPage';

const CataloguePage = ({ 
  user, 
  API, 
  teams, 
  brands, 
  players, 
  competitions, 
  masterJerseys, 
  onDataUpdate, 
  searchQuery 
}) => {
  const [activeTab, setActiveTab] = useState('teams');

  const tabs = [
    { 
      id: 'teams', 
      label: 'Équipes', 
      icon: '⚽', 
      count: teams?.length || 0,
      description: 'Clubs et équipes nationales'
    },
    { 
      id: 'brands', 
      label: 'Marques', 
      icon: '👕', 
      count: brands?.length || 0,
      description: 'Fabricants de maillots'
    },
    { 
      id: 'players', 
      label: 'Joueurs', 
      icon: '👤', 
      count: players?.length || 0,
      description: 'Joueurs professionnels'
    },
    { 
      id: 'competitions', 
      label: 'Ligues', 
      icon: '🏆', 
      count: competitions?.length || 0,
      description: 'Championnats et coupes'
    },
    { 
      id: 'master-jerseys', 
      label: 'Master Jerseys', 
      icon: '📋', 
      count: masterJerseys?.length || 0,
      description: 'Designs de maillots'
    }
  ];

  const renderActiveTabContent = () => {
    const commonProps = {
      user,
      API,
      onDataUpdate,
      searchQuery
    };

    switch (activeTab) {
      case 'teams':
        return <CollaborativeTeamsPage {...commonProps} teams={teams} />;
      case 'brands':
        return <CollaborativeBrandsPage {...commonProps} brands={brands} />;
      case 'players':
        return <CollaborativePlayersPage {...commonProps} players={players} />;
      case 'competitions':
        return <CollaborativeCompetitionsPage {...commonProps} competitions={competitions} />;
      case 'master-jerseys':
        return <CollaborativeMasterJerseyPage {...commonProps} masterJerseys={masterJerseys} teams={teams} brands={brands} competitions={competitions} />;
      default:
        return <CollaborativeTeamsPage {...commonProps} teams={teams} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              📚 Catalogue TopKit
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explorez notre base de données collaborative complète : 
              équipes, marques, joueurs, compétitions et designs de maillots documentés par la communauté
            </p>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-8">
            {tabs.map((tab) => (
              <div key={tab.id} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl mb-2">{tab.icon}</div>
                <div className="text-2xl font-bold text-gray-900">{tab.count}</div>
                <div className="text-sm text-gray-600">{tab.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 whitespace-nowrap border-b-2 font-medium text-sm transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{tab.icon}</span>
                  <span>{tab.label}</span>
                  <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                    {tab.count}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Active Tab Content */}
      <div className="min-h-screen">
        {renderActiveTabContent()}
      </div>

      {/* Floating Info */}
      <div className="fixed bottom-6 right-6 z-40">
        <div className="bg-blue-600 text-white p-4 rounded-lg shadow-lg max-w-xs">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">{tabs.find(t => t.id === activeTab)?.icon}</span>
            <div>
              <div className="font-semibold">{tabs.find(t => t.id === activeTab)?.label}</div>
              <div className="text-sm opacity-90">
                {tabs.find(t => t.id === activeTab)?.description}
              </div>
              <div className="text-xs opacity-75 mt-1">
                {tabs.find(t => t.id === activeTab)?.count} entrées documentées
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default CataloguePage;