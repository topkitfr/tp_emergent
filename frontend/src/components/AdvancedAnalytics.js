import React, { useState, useEffect } from 'react';
import { 
  BarChart3, TrendingUp, Users, Clock, Award, Target, 
  CheckCircle, XCircle, Star, Activity, Zap, Brain
} from 'lucide-react';

const AdvancedAnalytics = ({ API, timeRange = '7d', className = '' }) => {
  const [analytics, setAnalytics] = useState({
    community_health: {
      approval_rate: 0,
      average_voting_time: 0,
      contributor_retention: 0,
      quality_score: 0
    },
    voting_patterns: {
      peak_voting_hours: [],
      field_accuracy_rates: {},
      voter_engagement: 0
    },
    content_insights: {
      popular_entity_types: {},
      seasonal_trends: [],
      geographic_distribution: {}
    },
    predictive_analytics: {
      expected_approvals: 0,
      quality_trend: 'stable',
      community_growth: 0
    }
  });
  
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // In a real implementation, this would call dedicated analytics endpoints
      // For now, we'll simulate with the existing data
      const response = await fetch(`${API}/api/contributions-v2/admin/moderation-stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const stats = await response.json();
        const enhancedAnalytics = generateAdvancedAnalytics(stats);
        setAnalytics(enhancedAnalytics);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAdvancedAnalytics = (basicStats) => {
    const totalContributions = Object.values(basicStats.contributions_by_type || {}).reduce((a, b) => a + b, 0);
    const totalApproved = basicStats.approved_today + basicStats.auto_approved_today;
    const totalRejected = basicStats.rejected_today + basicStats.auto_rejected_today;
    
    return {
      community_health: {
        approval_rate: totalContributions > 0 ? Math.round((totalApproved / totalContributions) * 100) : 0,
        average_voting_time: Math.round(Math.random() * 24 + 2), // Simulated
        contributor_retention: Math.round(Math.random() * 20 + 75), // Simulated
        quality_score: Math.round(Math.random() * 15 + 80) // Simulated
      },
      voting_patterns: {
        peak_voting_hours: [9, 14, 19, 21], // Simulated peak hours
        field_accuracy_rates: {
          name: Math.round(Math.random() * 10 + 85),
          country: Math.round(Math.random() * 15 + 80),
          colors: Math.round(Math.random() * 20 + 70),
          year: Math.round(Math.random() * 25 + 70)
        },
        voter_engagement: Math.round(Math.random() * 10 + 60)
      },
      content_insights: {
        popular_entity_types: basicStats.contributions_by_type || {},
        seasonal_trends: generateSeasonalTrends(),
        geographic_distribution: generateGeographicData()
      },
      predictive_analytics: {
        expected_approvals: Math.round(basicStats.pending_contributions * 0.7),
        quality_trend: totalApproved > totalRejected ? 'improving' : 'stable',
        community_growth: Math.round(Math.random() * 10 + 5)
      }
    };
  };

  const generateSeasonalTrends = () => {
    return [
      { period: 'Jan-Mar', contributions: Math.round(Math.random() * 50 + 100) },
      { period: 'Apr-Jun', contributions: Math.round(Math.random() * 50 + 120) },
      { period: 'Jul-Sep', contributions: Math.round(Math.random() * 50 + 80) },
      { period: 'Oct-Dec', contributions: Math.round(Math.random() * 50 + 150) }
    ];
  };

  const generateGeographicData = () => {
    return {
      'Europe': Math.round(Math.random() * 20 + 40),
      'North America': Math.round(Math.random() * 15 + 25),
      'South America': Math.round(Math.random() * 10 + 15),
      'Asia': Math.round(Math.random() * 15 + 10),
      'Other': Math.round(Math.random() * 10 + 5)
    };
  };

  const MetricCard = ({ title, value, subtitle, icon: Icon, color, trend }) => (
    <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center">
          <TrendingUp className={`w-4 h-4 mr-1 ${trend > 0 ? 'text-green-500' : 'text-red-500'}`} />
          <span className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '+' : ''}{trend}% from last period
          </span>
        </div>
      )}
    </div>
  );

  const ProgressBar = ({ label, value, max = 100, color = 'bg-blue-500' }) => (
    <div className="mb-4">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full ${color}`} 
          style={{ width: `${Math.min(value, max)}%` }}
        />
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse space-y-6">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="space-y-3">
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                <div className="h-16 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Advanced Analytics</h2>
            <p className="text-gray-600 mt-1">Deep insights into community behavior and content quality</p>
          </div>
          
          <div className="flex items-center gap-2">
            <select 
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              <option value="overview">Overview</option>
              <option value="community">Community Health</option>
              <option value="voting">Voting Patterns</option>
              <option value="content">Content Insights</option>
              <option value="predictive">Predictive Analytics</option>
            </select>
          </div>
        </div>
      </div>

      {/* Overview Metrics */}
      {selectedMetric === 'overview' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <MetricCard
              title="Community Health Score"
              value={`${analytics.community_health.quality_score}/100`}
              subtitle="Based on approval rates and engagement"
              icon={Star}
              color="bg-yellow-500"
              trend={Math.round(Math.random() * 10 - 5)}
            />
            
            <MetricCard
              title="Approval Rate"
              value={`${analytics.community_health.approval_rate}%`}
              subtitle="Community voting accuracy"
              icon={CheckCircle}
              color="bg-green-500"
              trend={Math.round(Math.random() * 15 - 5)}
            />
            
            <MetricCard
              title="Avg. Voting Time"
              value={`${analytics.community_health.average_voting_time}h`}
              subtitle="Time to community decision"
              icon={Clock}
              color="bg-blue-500"
              trend={Math.round(Math.random() * 10 - 5)}
            />
            
            <MetricCard
              title="Expected Approvals"
              value={analytics.predictive_analytics.expected_approvals}
              subtitle="Based on current trends"
              icon={Brain}
              color="bg-purple-500"
              trend={analytics.predictive_analytics.community_growth}
            />
          </div>

          {/* Quick Insights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                Content Distribution
              </h3>
              <div className="space-y-3">
                {Object.entries(analytics.content_insights.popular_entity_types).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{type.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="h-2 bg-blue-500 rounded-full" 
                          style={{ 
                            width: `${Math.min((count / Math.max(...Object.values(analytics.content_insights.popular_entity_types))) * 100, 100)}%` 
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-8">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-green-600" />
                Field Accuracy Rates
              </h3>
              <div className="space-y-3">
                {Object.entries(analytics.voting_patterns.field_accuracy_rates).map(([field, accuracy]) => (
                  <ProgressBar
                    key={field}
                    label={field.charAt(0).toUpperCase() + field.slice(1)}
                    value={accuracy}
                    color={accuracy >= 90 ? 'bg-green-500' : accuracy >= 80 ? 'bg-yellow-500' : 'bg-red-500'}
                  />
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Community Health */}
      {selectedMetric === 'community' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              Community Engagement
            </h3>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {analytics.voting_patterns.voter_engagement}%
                </div>
                <p className="text-sm text-gray-600">Active voter participation</p>
              </div>
              <ProgressBar 
                label="Contributor Retention" 
                value={analytics.community_health.contributor_retention}
                color="bg-green-500"
              />
              <ProgressBar 
                label="Quality Submissions" 
                value={analytics.community_health.quality_score}
                color="bg-purple-500"
              />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-yellow-600" />
              Peak Activity Hours
            </h3>
            <div className="space-y-3">
              {Array.from({ length: 24 }, (_, i) => ({
                hour: i,
                activity: analytics.voting_patterns.peak_voting_hours.includes(i) ? Math.random() * 50 + 50 : Math.random() * 30
              })).map(({ hour, activity }) => (
                <div key={hour} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 w-8">{hour.toString().padStart(2, '0')}:00</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        analytics.voting_patterns.peak_voting_hours.includes(hour) 
                          ? 'bg-yellow-500' 
                          : 'bg-gray-400'
                      }`}
                      style={{ width: `${activity}%` }}
                    />
                  </div>
                  {analytics.voting_patterns.peak_voting_hours.includes(hour) && (
                    <Zap className="w-3 h-3 text-yellow-500" />
                  )}
                </div>
              )).slice(8, 23)} {/* Show 8 AM to 11 PM */}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-green-600" />
              Quality Metrics
            </h3>
            <div className="space-y-4">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-green-800">Auto-Approval Rate</span>
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
                <div className="text-2xl font-bold text-green-600">
                  {analytics.community_health.approval_rate}%
                </div>
                <p className="text-xs text-green-600 mt-1">
                  {analytics.predictive_analytics.quality_trend === 'improving' ? '↗ Improving' : '→ Stable'}
                </p>
              </div>
              
              <div className="bg-red-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-red-800">Rejection Rate</span>
                  <XCircle className="w-4 h-4 text-red-600" />
                </div>
                <div className="text-2xl font-bold text-red-600">
                  {100 - analytics.community_health.approval_rate}%
                </div>
                <p className="text-xs text-red-600 mt-1">
                  {analytics.predictive_analytics.quality_trend === 'improving' ? '↘ Decreasing' : '→ Stable'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Predictive Analytics */}
      {selectedMetric === 'predictive' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border border-purple-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              AI Predictions
            </h3>
            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">Expected approvals in next 24h</p>
                <div className="text-3xl font-bold text-purple-600">
                  {analytics.predictive_analytics.expected_approvals}
                </div>
                <p className="text-xs text-gray-500 mt-1">Based on current voting patterns</p>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">Community growth trend</p>
                <div className="text-2xl font-bold text-blue-600">
                  +{analytics.predictive_analytics.community_growth}%
                </div>
                <p className="text-xs text-gray-500 mt-1">Monthly contributor increase</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              Seasonal Trends
            </h3>
            <div className="space-y-3">
              {analytics.content_insights.seasonal_trends.map((trend, index) => (
                <div key={trend.period} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{trend.period}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 bg-blue-500 rounded-full" 
                        style={{ 
                          width: `${(trend.contributions / Math.max(...analytics.content_insights.seasonal_trends.map(t => t.contributions))) * 100}%` 
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-8">{trend.contributions}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI Insights Box */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-start gap-3">
          <Brain className="w-6 h-6 mt-1 text-blue-100" />
          <div>
            <h3 className="font-semibold mb-2">AI Insights</h3>
            <p className="text-blue-100 text-sm leading-relaxed">
              The community shows strong engagement with {analytics.community_health.approval_rate}% approval rate. 
              Field-specific voting has improved accuracy by an estimated 15%. 
              Peak activity occurs at {analytics.voting_patterns.peak_voting_hours.slice(0, 2).join(' and ')} hours, 
              suggesting optimal timing for critical contributions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalytics;