import React, { useState, useEffect } from 'react';
import { Plus, ThumbsUp, ThumbsDown, Eye, Filter, Image as ImageIcon, ExternalLink, Search, Grid3x3, List, MoreHorizontal } from 'lucide-react';

// Import existing components
import CollaborativeTeamsPage from './CollaborativeTeamsPage';
import CollaborativeBrandsPage from './CollaborativeBrandsPage';
import CollaborativePlayersPage from './CollaborativePlayersPage';
import CollaborativeCompetitionsPage from './CollaborativeCompetitionsPage';
import DynamicContributionForm from '../components/DynamicContributionForm';

const DatabaseContributionsPage = ({ 
  user, 
  API, 
  teams = [], 
  brands = [], 
  players = [], 
  competitions = [], 
  masterJerseys = [], 
  onDataUpdate, 
  searchQuery 
}) => {
  // Main tab state (Database vs Contributions)
  const [mainTab, setMainTab] = useState('database');
  
  // Database tab state
  const [databaseActiveTab, setDatabaseActiveTab] = useState('teams');
  
  // Contributions state
  const [contributions, setContributions] = useState([]);
  const [contributionsLoading, setContributionsLoading] = useState(false);
  const [showContributionForm, setShowContributionForm] = useState(false);
  const [selectedContributionType, setSelectedContributionType] = useState(null);
  const [contributionFilters, setContributionFilters] = useState({
    status: '',
    entity_type: '',
    page: 1
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid',
    itemsPerPage: 20,
    currentPage: 1
  });
  const [votingStates, setVotingStates] = useState({});

  // Database tabs configuration
  const databaseTabs = [
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

  // Quick add buttons configuration
  const quickAddButtons = [
    { type: 'team', label: '⚽ Team', color: 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200' },
    { type: 'brand', label: '👕 Brand', color: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200' },
    { type: 'player', label: '👤 Player', color: 'bg-purple-50 text-purple-700 hover:bg-purple-100 border-purple-200' },
    { type: 'competition', label: '🏆 Competition', color: 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border-yellow-200' }
  ];

  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    pending_review: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    needs_revision: 'bg-orange-100 text-orange-800'
  };

  // Fetch contributions when contributions tab is active
  useEffect(() => {
    if (mainTab === 'contributions') {
      fetchContributions();
    }
  }, [mainTab, contributionFilters, user]);

  const fetchContributions = async () => {
    if (!user) {
      setContributions([]);
      return;
    }

    setContributionsLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setContributions([]);
        return;
      }

      const queryParams = new URLSearchParams();
      if (contributionFilters.status) queryParams.append('status', contributionFilters.status);
      if (contributionFilters.entity_type) queryParams.append('entity_type', contributionFilters.entity_type);
      queryParams.append('page', contributionFilters.page);
      queryParams.append('limit', '20');

      const url = `${API}/api/contributions-v2/?${queryParams}`;
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setContributions(data);
      } else {
        setContributions([]);
      }
    } catch (error) {
      console.error('Error fetching contributions:', error);
      setContributions([]);
    } finally {
      setContributionsLoading(false);
    }
  };

  const handleNewContribution = (type = null) => {
    setSelectedContributionType(type);
    setShowContributionForm(true);
  };

  const handleVote = async (contributionId, voteType) => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please log in to vote');
      return;
    }

    setVotingStates(prev => ({ ...prev, [contributionId]: true }));

    try {
      const response = await fetch(
        `${API}/api/contributions-v2/${contributionId}/vote`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            vote_type: voteType,
            comment: '',
            field_votes: {}
          })
        }
      );

      if (response.ok) {
        const result = await response.json();
        setContributions(prev => prev.map(contrib => 
          contrib.id === contributionId 
            ? { 
                ...contrib, 
                upvotes: result.upvotes, 
                downvotes: result.downvotes,
                status: result.status
              }
            : contrib
        ));

        if (result.auto_approved || result.auto_rejected) {
          alert(`Contribution ${result.auto_approved ? 'auto-approved' : 'auto-rejected'} based on community votes!`);
        }
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to vote');
      }
    } catch (error) {
      console.error('Error voting:', error);
      alert('Error voting. Please try again.');
    } finally {
      setVotingStates(prev => ({ ...prev, [contributionId]: false }));
    }
  };

  const renderDatabaseContent = () => {
    const commonProps = {
      user,
      API,
      onDataUpdate,
      searchQuery
    };

    switch (databaseActiveTab) {
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

  const formatEntityType = (type) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatStatus = (status) => {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getContributionPreview = (contribution) => {
    const data = contribution.data || {};
    const entityType = contribution.entity_type;

    switch (entityType) {
      case 'team':
        return `${data.name || 'Unknown Team'} - ${data.country || 'Unknown Country'}`;
      case 'brand':
        return `${data.name || 'Unknown Brand'} - ${data.country || 'Unknown Country'}`;
      case 'player':
        return `${data.name || 'Unknown Player'} - ${data.nationality || 'Unknown Nationality'}`;
      case 'competition':
        return `${data.competition_name || 'Unknown Competition'} - ${data.country || 'Unknown Country'}`;
      default:
        return 'Unknown Contribution';
    }
  };

  const renderContributionCard = (contribution) => {
    if (displayOptions.viewMode === 'grid') {
      return (
        <div key={contribution.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <h3 className="font-semibold text-gray-900 text-sm">{contribution.title}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[contribution.status] || statusColors.draft}`}>
                  {formatStatus(contribution.status)}
                </span>
              </div>
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium mb-2 inline-block">
                {formatEntityType(contribution.entity_type)}
              </span>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {getContributionPreview(contribution)}
              </p>
              <div className="flex flex-col gap-1 text-xs text-gray-500">
                <span>Ref: {contribution.topkit_reference}</span>
                <span>Created: {new Date(contribution.created_at).toLocaleDateString()}</span>
                {contribution.images_count > 0 && (
                  <span className="flex items-center gap-1">
                    <ImageIcon className="w-3 h-3" />
                    {contribution.images_count} image{contribution.images_count !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Voting Section */}
          <div className="flex items-center gap-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => handleVote(contribution.id, 'upvote')}
              disabled={votingStates[contribution.id]}
              className="flex items-center gap-1 px-2 py-1 rounded text-sm hover:bg-green-50 text-green-600"
            >
              <ThumbsUp className="w-4 h-4" />
              <span>{contribution.upvotes || 0}</span>
            </button>
            <button
              onClick={() => handleVote(contribution.id, 'downvote')}
              disabled={votingStates[contribution.id]}
              className="flex items-center gap-1 px-2 py-1 rounded text-sm hover:bg-red-50 text-red-600"
            >
              <ThumbsDown className="w-4 h-4" />
              <span>{contribution.downvotes || 0}</span>
            </button>
            <div className="ml-auto">
              <button
                onClick={() => window.open(`/contributions-v2/${contribution.id}`, '_blank')}
                className="flex items-center gap-1 px-2 py-1 rounded text-sm hover:bg-blue-50 text-blue-600"
              >
                <Eye className="w-4 h-4" />
                View
              </button>
            </div>
          </div>
        </div>
      );
    }

    // Add list view if needed
    return renderContributionCard(contribution);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              🔍 Database & Contributions
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Browse our collaborative database and contribute new content to help grow the community
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            {databaseTabs.map((tab) => (
              <div key={tab.id} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl mb-2">{tab.icon}</div>
                <div className="text-2xl font-bold text-gray-900">{tab.count}</div>
                <div className="text-sm text-gray-600">{tab.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setMainTab('database')}
              className={`py-4 px-2 whitespace-nowrap border-b-2 font-medium text-lg transition-all flex items-center gap-2 ${
                mainTab === 'database'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Search className="w-5 h-5" />
              Browse Database
            </button>
            <button
              onClick={() => setMainTab('contributions')}
              className={`py-4 px-2 whitespace-nowrap border-b-2 font-medium text-lg transition-all flex items-center gap-2 ${
                mainTab === 'contributions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Plus className="w-5 h-5" />
              Add Contributions
              {user && (
                <span className="bg-blue-100 text-blue-600 px-2 py-1 text-xs rounded-full">
                  {contributions.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Database Tab Content */}
      {mainTab === 'database' && (
        <>
          {/* Database Sub-navigation */}
          <div className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4">
              <div className="flex space-x-6 overflow-x-auto">
                {databaseTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setDatabaseActiveTab(tab.id)}
                    className={`py-3 px-2 whitespace-nowrap border-b-2 font-medium text-sm transition-all ${
                      databaseActiveTab === tab.id
                        ? 'border-green-500 text-green-600'
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

          {/* Quick Add Section for Database */}
          {user && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-200">
              <div className="max-w-7xl mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-blue-900">Can't find what you're looking for?</h3>
                    <p className="text-sm text-blue-700">Add new items to the database and help grow the community</p>
                  </div>
                  <div className="flex gap-2">
                    {quickAddButtons.map(({ type, label, color }) => (
                      <button
                        key={type}
                        onClick={() => handleNewContribution(type)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium ${color} border transition-all hover:scale-105`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Database Content */}
          <div className="max-w-7xl mx-auto px-4 py-8">
            {renderDatabaseContent()}
          </div>
        </>
      )}

      {/* Contributions Tab Content */}
      {mainTab === 'contributions' && (
        <div className="max-w-6xl mx-auto px-6 py-8">
          {/* Contributions Header */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Community Contributions</h2>
                <p className="text-gray-600 mt-1">
                  Submit, vote, and improve content together. Help expand the TopKit database.
                </p>
              </div>
              <button
                onClick={() => handleNewContribution()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                New Contribution
              </button>
            </div>

            {/* Quick Add Buttons */}
            <div className="flex flex-wrap gap-2">
              {quickAddButtons.map(({ type, label, color }) => (
                <button
                  key={type}
                  onClick={() => handleNewContribution(type)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium ${color} border transition-all`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
            <div className="flex flex-wrap gap-4 items-end">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={contributionFilters.status}
                  onChange={(e) => setContributionFilters(prev => ({ ...prev, status: e.target.value, page: 1 }))}
                  className="border border-gray-300 rounded px-3 py-1 text-sm"
                >
                  <option value="">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="pending_review">Pending Review</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                  <option value="needs_revision">Needs Revision</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={contributionFilters.entity_type}
                  onChange={(e) => setContributionFilters(prev => ({ ...prev, entity_type: e.target.value, page: 1 }))}
                  className="border border-gray-300 rounded px-3 py-1 text-sm"
                >
                  <option value="">All Types</option>
                  <option value="team">Team</option>
                  <option value="brand">Brand</option>
                  <option value="player">Player</option>
                  <option value="competition">Competition</option>
                </select>
              </div>
              
              {/* Display Options */}
              <div className="ml-auto flex items-center gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">View</label>
                  <div className="flex border border-gray-300 rounded">
                    <button
                      onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'grid' }))}
                      className={`px-3 py-1 text-sm flex items-center gap-1 ${displayOptions.viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                    >
                      <Grid3x3 className="w-3 h-3" />
                      Grid
                    </button>
                    <button
                      onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'list' }))}
                      className={`px-3 py-1 text-sm border-l border-gray-300 flex items-center gap-1 ${displayOptions.viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                    >
                      <List className="w-3 h-3" />
                      List
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contributions List */}
          {contributionsLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading contributions...</p>
            </div>
          ) : (
            <div className={`${displayOptions.viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}`}>
              {contributions.length === 0 ? (
                <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center ${displayOptions.viewMode !== 'list' ? 'col-span-full' : ''}`}>
                  <div className="text-gray-400 mb-4">
                    <ImageIcon className="w-12 h-12 mx-auto" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No contributions found</h3>
                  <p className="text-gray-600 mb-4">
                    Be the first to contribute to the community database!
                  </p>
                  <button
                    onClick={() => handleNewContribution()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Create First Contribution
                  </button>
                </div>
              ) : (
                contributions.map(contribution => renderContributionCard(contribution))
              )}
            </div>
          )}

          {/* Voting Rules Explanation */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 mt-8">
            <h3 className="font-semibold text-blue-900 mb-3">How Community Voting Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                <div>
                  <p className="font-medium text-green-800">Auto-Approval</p>
                  <p className="text-green-700">3 upvotes automatically approve a contribution</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full mt-1.5"></div>
                <div>
                  <p className="font-medium text-red-800">Auto-Rejection</p>
                  <p className="text-red-700">2 downvotes automatically reject a contribution</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full mt-1.5"></div>
                <div>
                  <p className="font-medium text-gray-800">Visibility</p>
                  <p className="text-gray-700">Images visible to all logged-in users during review</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Contribution Form */}
      <DynamicContributionForm 
        isOpen={showContributionForm}
        onClose={() => {
          setShowContributionForm(false);
          setSelectedContributionType(null);
          if (mainTab === 'contributions') {
            fetchContributions(); // Refresh contributions list
          }
          if (onDataUpdate) {
            onDataUpdate(); // Refresh database data
          }
        }}
        selectedType={selectedContributionType}
        teams={teams}
        brands={brands}
        competitions={competitions}
        masterJerseys={masterJerseys}
        API={API}
      />
    </div>
  );
};

export default DatabaseContributionsPage;