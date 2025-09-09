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
      label: 'Teams', 
      icon: '⚽', 
      count: teams?.length || 0,
      description: 'Clubs and national teams'
    },
    { 
      id: 'brands', 
      label: 'Brand/Sponsor', 
      icon: '👕', 
      count: brands?.length || 0,
      description: 'Kit manufacturers'
    },
    { 
      id: 'players', 
      label: 'Players', 
      icon: '👤', 
      count: players?.length || 0,
      description: 'Professional players'
    },
    { 
      id: 'competitions', 
      label: 'Competitions', 
      icon: '🏆', 
      count: competitions?.length || 0,
      description: 'Championships and cups'
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
              📚 TopKit Database
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explore our complete collaborative database: 
              teams, brands, players and competitions documented by the community
            </p>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
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
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                  <span className="bg-gray-100 text-gray-700 px-2 py-1 text-xs rounded-full">
                    {tab.count}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {renderActiveTabContent()}
      </div>
    </div>
  );
};

export default CataloguePage;