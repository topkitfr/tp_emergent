import React, { useState, useEffect } from 'react';
import { Plus, ThumbsUp, ThumbsDown, Eye, Filter, Image as ImageIcon, ExternalLink } from 'lucide-react';
import DynamicContributionForm from '../components/DynamicContributionForm';

const ContributionsV2Page = ({ user, teams = [], brands = [], competitions = [], masterJerseys = [] }) => {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedType, setSelectedType] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    entity_type: '',
    page: 1
  });
  const [displayOptions, setDisplayOptions] = useState({
    viewMode: 'grid', // 'grid', 'thumbnail', 'list'
    itemsPerPage: 20,
    currentPage: 1
  });
  const [votingStates, setVotingStates] = useState({});

  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    pending_review: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    needs_revision: 'bg-orange-100 text-orange-800'
  };

  useEffect(() => {
    fetchContributions();
  }, [filters]);

  // Add effect to refetch when user changes
  useEffect(() => {
    console.log('🔄 User changed effect triggered, user:', user ? 'AUTHENTICATED' : 'NOT_AUTHENTICATED');
    if (user) {
      console.log('✅ User is authenticated:', {
        name: user.name,
        email: user.email,
        role: user.role,
        hasToken: !!user.token
      });
      // Add small delay to ensure token is properly set
      setTimeout(() => {
        fetchContributions();
      }, 500);
    } else {
      console.log('❌ No user, clearing contributions');
      setContributions([]);
    }
  }, [user]);

  // Add effect to refetch when component mounts and token is available
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token && contributions.length === 0) {
      console.log('🔄 Component mounted with token, fetching contributions...');
      fetchContributions();
    }
  }, []);

  const fetchContributions = async () => {
    console.log('📡 fetchContributions called');
    try {
      const token = localStorage.getItem('token');
      console.log('🔑 Token check:', token ? `Found token (${token.length} chars)` : 'No token');
      
      if (!token) {
        console.log('❌ No token available, skipping contributions fetch');
        setContributions([]);
        setLoading(false);
        return;
      }

      const queryParams = new URLSearchParams();
      if (filters.status) queryParams.append('status', filters.status);
      if (filters.entity_type) queryParams.append('entity_type', filters.entity_type);
      queryParams.append('page', filters.page);
      queryParams.append('limit', '20');

      const url = `${process.env.REACT_APP_BACKEND_URL}/api/contributions-v2/?${queryParams}`;
      console.log('📤 Fetching from:', url);

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('📨 Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Fetched ${data.length} contributions:`, data.map(c => c.title));
        setContributions(data);
      } else {
        console.error('❌ Failed to fetch contributions:', response.status);
        setContributions([]);
      }
    } catch (error) {
      console.error('💥 Error fetching contributions:', error);
      setContributions([]);
    } finally {
      setLoading(false);
    }
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
        `${process.env.REACT_APP_BACKEND_URL}/api/contributions-v2/${contributionId}/vote`,
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
        
        // Update the contribution in the list
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

  const handleNewContribution = (type = null) => {
    setSelectedType(type);
    setShowForm(true);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading contributions...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Community Contributions</h1>
              <p className="text-gray-600 mt-1">
                Discogs-style collaborative database. Submit, vote, and improve content together.
              </p>
            </div>
            <button
              onClick={() => handleNewContribution()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Contribution
            </button>
          </div>

          {/* Quick Add Buttons */}
          <div className="flex flex-wrap gap-2">
            {[
              { type: 'team', label: '⚽ Team', color: 'bg-green-50 text-green-700 hover:bg-green-100' },
              { type: 'brand', label: '👕 Brand', color: 'bg-blue-50 text-blue-700 hover:bg-blue-100' },
              { type: 'player', label: '👤 Player', color: 'bg-purple-50 text-purple-700 hover:bg-purple-100' },
              { type: 'competition', label: '🏆 Competition', color: 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100' }
            ].map(({ type, label, color }) => (
              <button
                key={type}
                onClick={() => handleNewContribution(type)}
                className={`px-3 py-1 rounded-lg text-sm font-medium ${color} border border-transparent hover:border-gray-200`}
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
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value, page: 1 }))}
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
                value={filters.entity_type}
                onChange={(e) => setFilters(prev => ({ ...prev, entity_type: e.target.value, page: 1 }))}
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
                    className={`px-3 py-1 text-sm ${displayOptions.viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    📊 Grid
                  </button>
                  <button
                    onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'thumbnail' }))}
                    className={`px-3 py-1 text-sm border-x border-gray-300 ${displayOptions.viewMode === 'thumbnail' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    🖼️ Thumb
                  </button>
                  <button
                    onClick={() => setDisplayOptions(prev => ({ ...prev, viewMode: 'list' }))}
                    className={`px-3 py-1 text-sm ${displayOptions.viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    📋 List
                  </button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Per Page</label>
                <select
                  value={displayOptions.itemsPerPage}
                  onChange={(e) => setDisplayOptions(prev => ({ ...prev, itemsPerPage: parseInt(e.target.value), currentPage: 1 }))}
                  className="border border-gray-300 rounded px-3 py-1 text-sm"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Contributions List */}
        <div className={`${displayOptions.viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 
                         displayOptions.viewMode === 'thumbnail' ? 'grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4' : 
                         'space-y-4'}`}>
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
            contributions.map(contribution => {
              // Grid View (Default)
              if (displayOptions.viewMode === 'grid') {
                return (
                  <div key={contribution.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow relative">
                    {/* Pending Approval Sticker */}
                    {contribution.status === 'pending_review' && (
                      <div className="absolute top-3 right-3 bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded-lg shadow-md z-10">
                        PENDING APPROVAL
                      </div>
                    )}
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
                        disabled={votingStates[contribution.id]?.loading}
                        className="flex items-center gap-1 px-2 py-1 rounded text-sm hover:bg-green-50 text-green-600"
                      >
                        <ThumbsUp className="w-4 h-4" />
                        <span>{contribution.upvotes || 0}</span>
                      </button>
                      <button
                        onClick={() => handleVote(contribution.id, 'downvote')}
                        disabled={votingStates[contribution.id]?.loading}
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
              
              // Thumbnail View (Images Only)
              else if (displayOptions.viewMode === 'thumbnail') {
                return (
                  <div key={contribution.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                    <div className="aspect-square bg-gray-100 flex items-center justify-center text-2xl">
                      {contribution.entity_type === 'team' && '⚽'}
                      {contribution.entity_type === 'brand' && '👕'}
                      {contribution.entity_type === 'player' && '👤'}
                      {contribution.entity_type === 'competition' && '🏆'}
                    </div>
                    <div className="p-2">
                      <h4 className="font-medium text-xs text-gray-900 mb-1 line-clamp-1">{contribution.title}</h4>
                      <div className="flex items-center justify-between text-xs">
                        <span className={`px-1 py-0.5 rounded text-xs ${statusColors[contribution.status] || statusColors.draft}`}>
                          {formatStatus(contribution.status).substring(0, 3)}
                        </span>
                        <div className="flex items-center gap-1">
                          <ThumbsUp className="w-3 h-3 text-green-600" />
                          <span className="text-green-600">{contribution.upvotes || 0}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              }
              
              // List View (Detailed)
              else {
                return (
                  <div key={contribution.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-gray-900">{contribution.title}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[contribution.status] || statusColors.draft}`}>
                            {formatStatus(contribution.status)}
                          </span>
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                            {formatEntityType(contribution.entity_type)}
                          </span>
                        </div>
                        <p className="text-gray-600 text-sm mb-2">
                          {getContributionPreview(contribution)}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
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
                    <div className="flex items-center gap-4 pt-4 border-t border-gray-100">
                      <button
                        onClick={() => handleVote(contribution.id, 'upvote')}
                        disabled={votingStates[contribution.id]?.loading}
                        className="flex items-center gap-2 px-3 py-1 rounded-lg text-sm hover:bg-green-50 text-green-600"
                      >
                        <ThumbsUp className="w-4 h-4" />
                        <span>{contribution.upvotes || 0} upvotes</span>
                      </button>
                      <button
                        onClick={() => handleVote(contribution.id, 'downvote')}
                        disabled={votingStates[contribution.id]?.loading}
                        className="flex items-center gap-2 px-3 py-1 rounded-lg text-sm hover:bg-red-50 text-red-600"
                      >
                        <ThumbsDown className="w-4 h-4" />
                        <span>{contribution.downvotes || 0} downvotes</span>
                      </button>
                      <div className="ml-auto">
                        <button
                          onClick={() => window.open(`/contributions-v2/${contribution.id}`, '_blank')}
                          className="flex items-center gap-2 px-3 py-1 rounded-lg text-sm hover:bg-blue-50 text-blue-600"
                        >
                          <Eye className="w-4 h-4" />
                          View Details
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>

                    {/* Voting Rules Info */}
                    {contribution.status === 'pending_review' && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm mt-4">
                        <p className="text-blue-800">
                          <strong>Community Voting:</strong> 3 upvotes = auto-approved ✅ | 2 downvotes = auto-rejected ❌
                        </p>
                      </div>
                    )}
                  </div>
                );
              }
            })
          )}
        </div>

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

      {/* Dynamic Contribution Form */}
      <DynamicContributionForm 
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          setSelectedType(null);
          fetchContributions(); // Refresh list after form closes
        }}
        selectedType={selectedType}
        teams={teams}
        brands={brands}
        competitions={competitions}
        masterJerseys={masterJerseys}
        API={process.env.REACT_APP_BACKEND_URL}
      />
    </div>
  );
};

export default ContributionsV2Page;