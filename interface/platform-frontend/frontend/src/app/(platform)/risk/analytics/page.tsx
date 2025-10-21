'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  useRiskHeatMap,
  useRiskTrends,
  useRiskReport,
  useRiskInsights,
  useRiskRecommendations,
} from '@/hooks/risk';
import { RiskMatrix } from '@/components/risk';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  AreaChart,
  Area,
} from 'recharts';
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Shield,
  BarChart3,
  Calendar,
  Download,
  RefreshCw,
  Activity,
  Target,
  Zap,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
} from 'lucide-react';
import { format } from 'date-fns';

export default function RiskAnalyticsPage() {
  const router = useRouter();
  const [trendDays, setTrendDays] = useState(90);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // TODO: Get from auth context
  const organizationId = 'org-123';

  // Fetch data
  const { data: heatMap, isLoading: heatMapLoading } = useRiskHeatMap({ organizationId });
  const { data: trends, isLoading: trendsLoading } = useRiskTrends({ days: trendDays, organizationId });
  const { data: report, isLoading: reportLoading, refetch: refetchReport } = useRiskReport({ organizationId });
  const { data: insights, isLoading: insightsLoading } = useRiskInsights({ days: 30 });
  const { data: recommendations, isLoading: recommendationsLoading } = useRiskRecommendations({
    limit: 5
  });

  const isLoading = heatMapLoading || trendsLoading || reportLoading;

  // Colors for charts
  const SEVERITY_COLORS = {
    critical: '#dc2626',
    high: '#ea580c',
    medium: '#ca8a04',
    low: '#16a34a',
  };

  const STATUS_COLORS = {
    identified: '#6b7280',
    assessed: '#3b82f6',
    treated: '#10b981',
    monitored: '#8b5cf6',
    accepted: '#f59e0b',
    closed: '#64748b',
  };

  const CHART_COLORS = [
    '#ea580c', // orange-600
    '#dc2626', // red-600
    '#ca8a04', // yellow-600
    '#16a34a', // green-600
    '#2563eb', // blue-600
    '#9333ea', // purple-600
    '#db2777', // pink-600
    '#0891b2', // cyan-600
  ];

  // Calculate trend direction
  const calculateTrend = () => {
    if (!trends?.data_points || trends.data_points.length < 2) return null;

    const recent = trends.data_points.slice(-7);
    const older = trends.data_points.slice(-14, -7);

    const recentAvg = recent.reduce((sum, d) => sum + d.critical + d.high, 0) / recent.length;
    const olderAvg = older.reduce((sum, d) => sum + d.critical + d.high, 0) / older.length;

    const change = ((recentAvg - olderAvg) / olderAvg) * 100;

    return {
      direction: change > 0 ? 'up' : 'down',
      percentage: Math.abs(change).toFixed(1),
    };
  };

  const trend = calculateTrend();

  // Prepare radar chart data for risk categories
  const prepareRadarData = () => {
    if (!report) return [];

    return Object.entries(report.by_category).map(([category, count]) => ({
      category: category.replace(/_/g, ' ').toUpperCase(),
      count,
      fullMark: Math.max(...Object.values(report.by_category)) * 1.2,
    }));
  };

  // Export report functionality
  const handleExportReport = () => {
    if (!report) return;

    const reportData = {
      generated_at: new Date().toISOString(),
      organization_id: organizationId,
      summary: {
        total_risks: report.total_risks,
        critical_count: report.by_severity.critical,
        high_count: report.by_severity.high,
        medium_count: report.by_severity.medium,
        low_count: report.by_severity.low,
        average_score: report.average_score,
      },
      category_distribution: report.by_category,
      status_distribution: report.by_status,
      trends: trends,
      insights: insights,
      recommendations: recommendations,
    };

    // Create downloadable JSON
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `risk-analytics-report-${format(new Date(), 'yyyy-MM-dd')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-orange-600 transition-colors"
          >
            Home
          </button>
          <span>/</span>
          <button
            onClick={() => router.push('/risk')}
            className="hover:text-orange-600 transition-colors"
          >
            Risk Assessment
          </button>
          <span>/</span>
          <span className="text-gray-900 font-medium">Analytics</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/risk')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <BarChart3 className="w-10 h-10 text-orange-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Risk Analytics</h1>
                <p className="text-gray-600 mt-1">Comprehensive risk analysis and insights</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => refetchReport()}
                disabled={isLoading}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleExportReport}
                disabled={!report}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mb-4"></div>
            <p className="text-gray-600">Loading analytics data...</p>
          </div>
        )}

        {!isLoading && report && (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-600">Total Risks</p>
                  <Shield className="w-6 h-6 text-blue-600" />
                </div>
                <p className="text-3xl font-bold text-gray-900">{report.total_risks}</p>
                <p className="text-sm text-gray-500 mt-1">All categories</p>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-red-700">Critical Risks</p>
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <p className="text-3xl font-bold text-red-900">{report.by_severity.critical}</p>
                <p className="text-sm text-red-600 mt-1">
                  {report.total_risks > 0
                    ? `${((report.by_severity.critical / report.total_risks) * 100).toFixed(1)}% of total`
                    : 'Score ≥ 20'
                  }
                </p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-green-700">Treated Risks</p>
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <p className="text-3xl font-bold text-green-900">
                  {report.by_status.treated || 0}
                </p>
                <p className="text-sm text-green-600 mt-1">With treatment plans</p>
              </div>

              <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-orange-700">Avg Risk Score</p>
                  <TrendingUp className="w-6 h-6 text-orange-600" />
                </div>
                <p className="text-3xl font-bold text-orange-900">
                  {report.average_score.toFixed(1)}
                </p>
                <p className="text-sm text-orange-600 mt-1">
                  {trend && (
                    <span className="inline-flex items-center gap-1">
                      {trend.direction === 'up' ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      {trend.percentage}% this week
                    </span>
                  )}
                  {!trend && 'Organization average'}
                </p>
              </div>
            </div>

            {/* Secondary Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">High Risks</p>
                    <p className="text-2xl font-bold text-orange-600">{report.by_severity.high}</p>
                  </div>
                  <Activity className="w-8 h-8 text-orange-400" />
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Medium Risks</p>
                    <p className="text-2xl font-bold text-yellow-600">{report.by_severity.medium}</p>
                  </div>
                  <Target className="w-8 h-8 text-yellow-400" />
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Low Risks</p>
                    <p className="text-2xl font-bold text-green-600">{report.by_severity.low}</p>
                  </div>
                  <Zap className="w-8 h-8 text-green-400" />
                </div>
              </div>
            </div>

            {/* Risk Heat Map */}
            <RiskMatrix
              organizationId={organizationId}
              onCellClick={(likelihood, impact, risks) => {
                console.log('Cell clicked:', likelihood, impact, risks);
                // TODO: Show modal or navigate to filtered list
                if (risks.length > 0) {
                  router.push(`/risk?likelihood=${likelihood}&impact=${impact}`);
                }
              }}
            />

            {/* Trends Chart */}
            {trends && trends.data_points && trends.data_points.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Risk Trends</h2>
                    <p className="text-gray-600 text-sm">Daily risk counts over time by severity</p>
                  </div>

                  <select
                    value={trendDays}
                    onChange={(e) => setTrendDays(parseInt(e.target.value))}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value={30}>Last 30 days</option>
                    <option value={60}>Last 60 days</option>
                    <option value={90}>Last 90 days</option>
                    <option value={180}>Last 6 months</option>
                  </select>
                </div>

                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trends.data_points}>
                      <defs>
                        <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={SEVERITY_COLORS.critical} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={SEVERITY_COLORS.critical} stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={SEVERITY_COLORS.high} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={SEVERITY_COLORS.high} stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorMedium" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={SEVERITY_COLORS.medium} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={SEVERITY_COLORS.medium} stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorLow" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={SEVERITY_COLORS.low} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={SEVERITY_COLORS.low} stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(date) => format(new Date(date), 'MMM d')}
                        stroke="#6b7280"
                      />
                      <YAxis stroke="#6b7280" />
                      <Tooltip
                        labelFormatter={(date) => format(new Date(date), 'MMM d, yyyy')}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                        }}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="critical"
                        stroke={SEVERITY_COLORS.critical}
                        fillOpacity={1}
                        fill="url(#colorCritical)"
                        strokeWidth={2}
                        name="Critical"
                      />
                      <Area
                        type="monotone"
                        dataKey="high"
                        stroke={SEVERITY_COLORS.high}
                        fillOpacity={1}
                        fill="url(#colorHigh)"
                        strokeWidth={2}
                        name="High"
                      />
                      <Area
                        type="monotone"
                        dataKey="medium"
                        stroke={SEVERITY_COLORS.medium}
                        fillOpacity={1}
                        fill="url(#colorMedium)"
                        strokeWidth={2}
                        name="Medium"
                      />
                      <Area
                        type="monotone"
                        dataKey="low"
                        stroke={SEVERITY_COLORS.low}
                        fillOpacity={1}
                        fill="url(#colorLow)"
                        strokeWidth={2}
                        name="Low"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Category & Status Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Category Distribution Pie Chart */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Risk by Category</h3>
                    <p className="text-sm text-gray-600">Distribution across risk categories</p>
                  </div>
                  <Filter className="w-5 h-5 text-gray-400" />
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(report.by_category).map(([category, count]) => ({
                          name: category.replace(/_/g, ' ').toUpperCase(),
                          value: count,
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => `${entry.name}: ${entry.value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.keys(report.by_category).map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={CHART_COLORS[index % CHART_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Status Distribution Bar Chart */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Risk by Status</h3>
                    <p className="text-sm text-gray-600">Current status distribution</p>
                  </div>
                  <Activity className="w-5 h-5 text-gray-400" />
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(report.by_status).map(([status, count]) => ({
                        status: status.charAt(0).toUpperCase() + status.slice(1),
                        count,
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="status" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px'
                        }}
                      />
                      <Bar dataKey="count" fill="#ea580c" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Radar Chart - Category Analysis */}
            {Object.keys(report.by_category).length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Category Risk Profile</h3>
                    <p className="text-sm text-gray-600">Multi-dimensional view of risk categories</p>
                  </div>
                  <Target className="w-5 h-5 text-gray-400" />
                </div>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={prepareRadarData()}>
                      <PolarGrid stroke="#e5e7eb" />
                      <PolarAngleAxis
                        dataKey="category"
                        tick={{ fill: '#6b7280', fontSize: 12 }}
                      />
                      <PolarRadiusAxis stroke="#9ca3af" />
                      <Radar
                        name="Risk Count"
                        dataKey="count"
                        stroke="#ea580c"
                        fill="#ea580c"
                        fillOpacity={0.5}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px'
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* AI Insights */}
            {insights && insights.insights && insights.insights.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Zap className="w-6 h-6 text-purple-600" />
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">AI Insights</h2>
                    <p className="text-sm text-gray-600">Automated analysis and pattern detection</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {insights.insights.slice(0, 5).map((insight, index) => (
                    <div
                      key={index}
                      className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-medium text-blue-900">{insight.title}</p>
                          <p className="text-sm text-blue-700 mt-1">{insight.description}</p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-blue-600">
                            <span className="inline-flex items-center gap-1">
                              <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                              Confidence: {(insight.confidence * 100).toFixed(0)}%
                            </span>
                            <span>•</span>
                            <span className="capitalize">{insight.insight_type.replace(/_/g, ' ')}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Recommendations */}
            {recommendations && recommendations.recommendations && recommendations.recommendations.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="w-6 h-6 text-green-600" />
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">AI Recommendations</h2>
                    <p className="text-sm text-gray-600">Actionable steps to improve risk posture</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {recommendations.recommendations.map((rec, index) => (
                    <div
                      key={rec.recommendation_id || index}
                      className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                          {rec.priority === 'urgent' || rec.priority === 'high' ? (
                            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                          ) : (
                            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-start justify-between gap-2">
                            <p className="font-medium text-green-900">{rec.title}</p>
                            <span
                              className={`px-2 py-0.5 rounded text-xs font-medium flex-shrink-0 ${
                                rec.priority === 'urgent'
                                  ? 'bg-red-100 text-red-700'
                                  : rec.priority === 'high'
                                  ? 'bg-orange-100 text-orange-700'
                                  : rec.priority === 'medium'
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-green-100 text-green-700'
                              }`}
                            >
                              {rec.priority}
                            </span>
                          </div>
                          <p className="text-sm text-green-700 mt-1">{rec.description}</p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-green-600">
                            <span className="inline-flex items-center gap-1">
                              <span className="w-2 h-2 rounded-full bg-green-600"></span>
                              Confidence: {(rec.confidence * 100).toFixed(0)}%
                            </span>
                            <span>•</span>
                            <span className="capitalize">{rec.recommendation_type.replace(/_/g, ' ')}</span>
                            {rec.estimated_risk_reduction && (
                              <>
                                <span>•</span>
                                <span>Risk Reduction: {rec.estimated_risk_reduction}%</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Report Metadata */}
            <div className="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-600">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span>
                      Report generated: {format(new Date(report.generated_at), 'MMM d, yyyy HH:mm')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span>Period: {trendDays} days</span>
                  </div>
                </div>
                <span className="text-gray-500">Organization: {organizationId}</span>
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {!isLoading && (!report || report.total_risks === 0) && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Risk Data Available</h3>
            <p className="text-gray-600 mb-4">
              Start by identifying and assessing risks to see analytics
            </p>
            <button
              onClick={() => router.push('/risk/register')}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
            >
              Add First Risk
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
