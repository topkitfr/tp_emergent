import React, { useState, useEffect } from 'react';
import { 
  Eye, CheckCircle, XCircle, Clock, Users, FileText, 
  TrendingUp, AlertTriangle, Search, Filter, RefreshCw,
  ThumbsUp, ThumbsDown, MessageSquare, Calendar, BarChart3,
  Trash2, RotateCcw
} from 'lucide-react';
import AdvancedAnalytics from '../components/AdvancedAnalytics';
import ActivityFeed from '../components/ActivityFeed';
import FieldSpecificVoting from '../components/FieldSpecificVoting';
import PaginationControls from '../PaginationControls';

const ModerationDashboard = ({ user, API }) => {
  const [stats, setStats] = useState({
    pending_contributions: 0,
    approved_today: 0,
    rejected_today: 0,
    total_votes_today: 0,
    auto_approved_today: 0,
    auto_rejected_today: 0,
    contributions_by_type: {},
    top_contributors: []
  });
  
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [filters, setFilters] = useState({
    status: '',
    entity_type: '',
    search: ''
  });

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  const [totalContributions, setTotalContributions] = useState(0);

  // Cache for contributions by tab to remember them
  const [contributionsCache, setContributionsCache] = useState({
    overview: [],
    pending: [],
    approved: [],
    rejected: []
  });

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchModerationData();
    }
  }, [user, activeTab, currentPage, itemsPerPage]);

  useEffect(() => {
    // Reset page when changing tabs
    setCurrentPage(1);
  }, [activeTab]);

  const fetchModerationData = async () => {
    try {
      setLoading(true);
      
      // Fetch moderation stats
      const statsResponse = await fetch(`${API}/api/contributions-v2/admin/moderation-stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch contributions based on active tab with pagination
      await fetchContributionsByTab(activeTab);
      
    } catch (error) {
      console.error('Error fetching moderation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchContributionsByTab = async (tab) => {
    try {
      let status = '';
      let limit = itemsPerPage;
      
      // Determine status based on tab
      switch (tab) {
        case 'overview':
          // For overview, get recent pending contributions
          status = 'pending_review';
          limit = 6; // Just show 6 recent ones in overview
          break;
        case 'pending':
          status = 'pending_review';
          break;
        case 'approved':
          status = 'approved';
          break;
        case 'rejected':
          status = 'rejected';
          break;
        default:
          status = 'pending_review';
      }

      const contribResponse = await fetch(
        `${API}/api/contributions-v2/?status=${status}&page=${tab === 'overview' ? 1 : currentPage}&limit=${limit}`, 
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (contribResponse.ok) {
        const contribData = await contribResponse.json();
        
        // Update contributions and cache
        setContributions(contribData);
        setContributionsCache(prev => ({
          ...prev,
          [tab]: contribData
        }));

        // For non-overview tabs, we need to get total count for pagination
        if (tab !== 'overview') {
          // Get total count by making another request with a high limit to count all
          const countResponse = await fetch(
            `${API}/api/contributions-v2/?status=${status}&page=1&limit=1000`, 
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              }
            }
          );
          
          if (countResponse.ok) {
            const countData = await countResponse.json();
            setTotalContributions(countData.length);
          }
        }
      }
      
    } catch (error) {
      console.error('Error fetching contributions:', error);
    }
  };

  const handleModerationAction = async (contributionId, action, reason = '') => {
    try {
      const response = await fetch(`${API}/api/contributions-v2/${contributionId}/moderate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          action: action,
          reason: reason,
          notify_contributor: true
        })
      });

      if (response.ok) {
        // Refresh data
        fetchModerationData();
        alert(`Contribution ${action}d successfully!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Moderation action error:', error);
      alert('Error performing moderation action');
    }
  };

  // Handle pagination
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1);
  };

  // Handle tab change
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    // Use cached data if available to remember contributions
    if (contributionsCache[tabId] && contributionsCache[tabId].length > 0) {
      setContributions(contributionsCache[tabId]);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color, trend }) => (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className={`text-xs ${trend.positive ? 'text-green-600' : 'text-red-600'} flex items-center mt-1`}>
              <TrendingUp className="w-3 h-3 mr-1" />
              {trend.value}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  const ContributionCard = ({ contribution }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{contribution.title}</h3>
          <p className="text-sm text-gray-600 mt-1">
            {contribution.entity_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} • 
            Ref: {contribution.topkit_reference}
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <div className="flex items-center gap-1 text-green-600">
            <ThumbsUp className="w-4 h-4" />
            {contribution.upvotes}
          </div>
          <div className="flex items-center gap-1 text-red-600">
            <ThumbsDown className="w-4 h-4" />
            {contribution.downvotes}
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
        <span>Created: {new Date(contribution.created_at).toLocaleDateString()}</span>
        <span>Images: {contribution.images_count}</span>
      </div>
      
      <div className="flex gap-2">
        <button
          onClick={() => handleModerationAction(contribution.id, 'approve')}
          className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-1"
        >
          <CheckCircle className="w-4 h-4" />
          Approve
        </button>
        <button
          onClick={() => {
            const reason = prompt('Reason for rejection:');
            if (reason) handleModerationAction(contribution.id, 'reject', reason);
          }}
          className="flex-1 bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-1"
        >
          <XCircle className="w-4 h-4" />
          Reject
        </button>
        <button
          onClick={() => window.open(`/contributions-v2/${contribution.id}`, '_blank')}
          className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Eye className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600">You need admin privileges to access the moderation dashboard.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-600 mx-auto animate-spin mb-4" />
          <p className="text-gray-600">Loading moderation dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Moderation Dashboard</h1>
          <p className="text-gray-600">Manage community contributions and maintain database quality</p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            {[
              { id: 'overview', label: 'Overview', icon: TrendingUp },
              { id: 'pending', label: 'Pending Review', icon: Clock },
              { id: 'analytics', label: 'Advanced Analytics', icon: BarChart3 },
              { id: 'activity', label: 'Live Activity', icon: Users }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Pending Review"
                value={stats.pending_contributions}
                icon={Clock}
                color="bg-yellow-500"
              />
              <StatCard
                title="Approved Today"
                value={stats.approved_today}
                icon={CheckCircle}
                color="bg-green-500"
              />
              <StatCard
                title="Auto-Approved"
                value={stats.auto_approved_today}
                icon={TrendingUp}
                color="bg-blue-500"
              />
              <StatCard
                title="Total Votes Today"
                value={stats.total_votes_today}
                icon={Users}
                color="bg-purple-500"
              />
            </div>

            {/* Contributions by Type */}
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contributions by Type</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {Object.entries(stats.contributions_by_type).map(([type, count]) => (
                  <div key={type} className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-gray-900">{count}</p>
                    <p className="text-xs text-gray-600 capitalize">{type.replace('_', ' ')}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Contributions</h3>
                <button
                  onClick={fetchModerationData}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {contributions.slice(0, 6).map(contribution => (
                  <ContributionCard key={contribution.id} contribution={contribution} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Pending Tab */}
        {activeTab === 'pending' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-64">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search contributions..."
                      value={filters.search}
                      onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <select
                  value={filters.entity_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, entity_type: e.target.value }))}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  <option value="team">Teams</option>
                  <option value="brand">Brands</option>
                  <option value="player">Players</option>
                  <option value="competition">Competitions</option>
                  <option value="master_kit">Master Kits</option>
                  <option value="reference_kit">Reference Kits</option>
                </select>
              </div>
            </div>

            {/* Pending Contributions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {contributions
                .filter(c => 
                  (!filters.entity_type || c.entity_type === filters.entity_type) &&
                  (!filters.search || c.title.toLowerCase().includes(filters.search.toLowerCase()))
                )
                .map(contribution => (
                  <ContributionCard key={contribution.id} contribution={contribution} />
                ))}
            </div>

            {contributions.length === 0 && (
              <div className="text-center py-12">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">All Caught Up!</h3>
                <p className="text-gray-600">No contributions pending review at the moment.</p>
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <AdvancedAnalytics API={process.env.REACT_APP_BACKEND_URL} />
        )}

        {/* Activity Tab */}
        {activeTab === 'activity' && (
          <div className="space-y-6">
            <ActivityFeed 
              API={process.env.REACT_APP_BACKEND_URL} 
              currentUser={user}
              className="max-w-4xl mx-auto"
            />
            
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
              <h3 className="font-semibold text-green-900 mb-3">Real-Time Community Monitoring</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5 animate-pulse"></div>
                  <div>
                    <p className="font-medium text-green-800">Live Activity Feed</p>
                    <p className="text-green-700">Real-time updates every 30 seconds</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                  <div>
                    <p className="font-medium text-blue-800">Community Pulse</p>
                    <p className="text-blue-700">Track voting patterns and engagement</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mt-1.5"></div>
                  <div>
                    <p className="font-medium text-purple-800">Quality Insights</p>
                    <p className="text-purple-700">AI-powered content analysis</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Legacy Analytics Tab - now replaced with Advanced Analytics */}
        {activeTab === 'legacy-analytics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Community Moderation Analytics</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">{stats.auto_approved_today}</p>
                  <p className="text-sm text-green-700">Auto-Approved Today</p>
                  <p className="text-xs text-gray-600 mt-1">Via community voting (3+ upvotes)</p>
                </div>
                
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-3xl font-bold text-red-600">{stats.auto_rejected_today}</p>
                  <p className="text-sm text-red-700">Auto-Rejected Today</p>
                  <p className="text-xs text-gray-600 mt-1">Via community voting (2+ downvotes)</p>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">
                    {stats.auto_approved_today + stats.auto_rejected_today > 0 
                      ? Math.round((stats.auto_approved_today / (stats.auto_approved_today + stats.auto_rejected_today)) * 100)
                      : 0}%
                  </p>
                  <p className="text-sm text-blue-700">Auto-Approval Rate</p>
                  <p className="text-xs text-gray-600 mt-1">Community moderation efficiency</p>
                </div>
              </div>

              <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Discogs-Style Moderation Rules</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="flex items-start gap-2">
                    <ThumbsUp className="w-4 h-4 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-green-800">Auto-Approval</p>
                      <p className="text-green-700">3 community upvotes = automatic approval</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <ThumbsDown className="w-4 h-4 text-red-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-red-800">Auto-Rejection</p>
                      <p className="text-red-700">2 community downvotes = automatic rejection</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModerationDashboard;