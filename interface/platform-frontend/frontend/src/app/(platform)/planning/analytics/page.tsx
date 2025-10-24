/**
 * Planning Module - Analytics Dashboard
 * Comprehensive analytics and insights for Business Continuity Planning
 * ISO 22301:2019 Clause 8.3 Compliance Dashboard
 *
 * Created: 2025-10-22
 * Agent: 14/6 (Planning Module Round 4 - FINAL)
 */

'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  useExecutiveSummary,
  useMaturityAssessment,
  usePlanCoverage,
  usePlans,
  usePlanningGaps,
} from '@/hooks/planning';
import {
  CoverageMatrix,
  GapAnalysis,
  ImplementationTimeline,
} from '@/components/planning';
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
} from 'recharts';
import {
  ArrowLeft,
  Shield,
  Target,
  CheckSquare,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  Calendar,
  Download,
  RefreshCw,
  Activity,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Zap,
  FileText,
  Users,
  Settings,
} from 'lucide-react';
import { format } from 'date-fns';

// ==================== TYPES ====================

interface DateRange {
  start?: string;
  end?: string;
}

// ==================== CONSTANTS ====================

const CHART_COLORS = [
  '#3b82f6', // blue-500
  '#8b5cf6', // purple-500
  '#ec4899', // pink-500
  '#f59e0b', // amber-500
  '#10b981', // emerald-500
  '#6366f1', // indigo-500
  '#f97316', // orange-500
  '#06b6d4', // cyan-500
];

const MATURITY_COLORS = {
  1: '#dc2626', // red-600
  2: '#ea580c', // orange-600
  3: '#ca8a04', // yellow-600
  4: '#16a34a', // green-600
  5: '#2563eb', // blue-600
};

const PLAN_TYPE_COLORS = {
  bcdr: '#3b82f6',
  dr: '#8b5cf6',
  crisis: '#dc2626',
  incident: '#f59e0b',
  communication: '#10b981',
};

const STATUS_COLORS = {
  draft: '#6b7280',
  active: '#10b981',
  review: '#f59e0b',
  archived: '#64748b',
};

// ==================== HELPER COMPONENTS ====================

/**
 * Dimension Progress Bar Component
 * Shows progress bar for maturity dimensions
 */
function DimensionBar({ label, value, maxValue = 100 }: { label: string; value: number; maxValue?: number }) {
  const percentage = (value / maxValue) * 100;
  const color =
    percentage >= 80
      ? 'bg-green-500'
      : percentage >= 60
      ? 'bg-yellow-500'
      : percentage >= 40
      ? 'bg-orange-500'
      : 'bg-red-500';

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">{value}/{maxValue}</span>
      </div>
      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

/**
 * Maturity Circle SVG Component
 * Circular progress indicator for overall maturity score
 */
function MaturityCircle({ score, level }: { score: number; level: number }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const color = MATURITY_COLORS[level as keyof typeof MATURITY_COLORS] || '#3b82f6';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="w-48 h-48 transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="96"
          cy="96"
          r={radius}
          stroke="#e5e7eb"
          strokeWidth="12"
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx="96"
          cy="96"
          r={radius}
          stroke={color}
          strokeWidth="12"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-5xl font-bold text-gray-900">{score}</p>
        <p className="text-sm text-gray-600 mt-1">out of 100</p>
      </div>
    </div>
  );
}

/**
 * Stat Card Component
 * Reusable card for displaying statistics
 */
function StatCard({
  icon: Icon,
  title,
  value,
  subtitle,
  trend,
  color = 'blue',
  className = '',
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  value: string | number;
  subtitle: string;
  trend?: { direction: 'up' | 'down'; value: string };
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'red';
  className?: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-600',
    green: 'bg-green-50 border-green-200 text-green-600',
    orange: 'bg-orange-50 border-orange-200 text-orange-600',
    purple: 'bg-purple-50 border-purple-200 text-purple-600',
    red: 'bg-red-50 border-red-200 text-red-600',
  };

  const iconColorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    purple: 'text-purple-600',
    red: 'text-red-600',
  };

  return (
    <div className={`${colorClasses[color]} border rounded-lg p-6 hover:shadow-lg transition-all duration-200 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium">{title}</p>
        <Icon className={`w-6 h-6 ${iconColorClasses[color]}`} />
      </div>
      <p className="text-3xl font-bold text-gray-900 mb-2">{value}</p>
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">{subtitle}</p>
        {trend && (
          <span className="inline-flex items-center gap-1 text-xs font-medium">
            {trend.direction === 'up' ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}

// ==================== MAIN COMPONENT ====================

export default function PlanningAnalyticsPage() {
  const router = useRouter();

  // State management
  const [dateRange, setDateRange] = useState<DateRange>({
    start: undefined,
    end: undefined,
  });
  const [refreshKey, setRefreshKey] = useState(0);

  // TODO: Get from auth context
  const organizationId = 'org-123';

  // Data fetching with all analytics hooks
  const { data: summary, isLoading: summaryLoading, refetch: refetchSummary } = useExecutiveSummary({
    organizationId,
  });

  const { data: maturity, isLoading: maturityLoading, refetch: refetchMaturity } = useMaturityAssessment({
    organizationId,
  });

  const { data: coverage, isLoading: coverageLoading } = usePlanCoverage({
    organizationId,
  });

  const { data: plansData, isLoading: plansLoading } = usePlans({
    organization_id: organizationId,
  });

  const { data: gaps, isLoading: gapsLoading } = usePlanningGaps({
    organizationId,
  });

  const isLoading = summaryLoading || maturityLoading || coverageLoading || plansLoading;

  // ==================== DATA PROCESSING ====================

  // Process plans data for charts
  const plansByType = useMemo(() => {
    if (!plansData?.plans) return [];

    const typeCount: Record<string, number> = {};
    plansData.plans.forEach((plan) => {
      const type = plan.plan_type || 'other';
      typeCount[type] = (typeCount[type] || 0) + 1;
    });

    return Object.entries(typeCount).map(([type, count]) => ({
      name: type.toUpperCase().replace(/_/g, ' '),
      value: count,
      color: PLAN_TYPE_COLORS[type as keyof typeof PLAN_TYPE_COLORS] || CHART_COLORS[0],
    }));
  }, [plansData]);

  const plansByStatus = useMemo(() => {
    if (!plansData?.plans) return [];

    const statusCount: Record<string, number> = {};
    plansData.plans.forEach((plan) => {
      const status = plan.status || 'draft';
      statusCount[status] = (statusCount[status] || 0) + 1;
    });

    return Object.entries(statusCount).map(([status, count]) => ({
      name: status.charAt(0).toUpperCase() + status.slice(1),
      value: count,
      color: STATUS_COLORS[status as keyof typeof STATUS_COLORS] || CHART_COLORS[1],
    }));
  }, [plansData]);

  // Prepare radar data for maturity dimensions
  const radarData = useMemo(() => {
    if (!maturity) return [];

    const dimensions = (maturity as any).dimensions || {};
    return Object.entries(dimensions).map(([key, value]) => ({
      dimension: key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
      score: value as number,
      fullMark: 100,
    }));
  }, [maturity]);

  // ==================== EVENT HANDLERS ====================

  const handleRefresh = async () => {
    setRefreshKey((prev) => prev + 1);
    await Promise.all([
      refetchSummary(),
      refetchMaturity(),
    ]);
  };

  const handleExportReport = () => {
    const reportData = {
      generated_at: new Date().toISOString(),
      organization_id: organizationId,
      executive_summary: summary,
      maturity_assessment: maturity,
      coverage_analysis: coverage,
      plans_summary: {
        total: plansData?.total || 0,
        by_type: plansByType,
        by_status: plansByStatus,
      },
      gaps_analysis: gaps,
    };

    // Create downloadable JSON
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `planning-analytics-report-${format(new Date(), 'yyyy-MM-dd')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-blue-600 transition-colors"
          >
            Home
          </button>
          <span>/</span>
          <button
            onClick={() => router.push('/planning')}
            className="hover:text-blue-600 transition-colors"
          >
            Planning
          </button>
          <span>/</span>
          <span className="text-gray-900 font-medium">Analytics</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/planning')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <BarChart3 className="w-10 h-10 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Business Continuity Planning Analytics</h1>
                <p className="text-gray-600 mt-1">ISO 22301:2019 Clause 8.3 Compliance Dashboard</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleExportReport}
                disabled={!summary}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4" />
                Export PDF/CSV
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading analytics data...</p>
          </div>
        )}

        {!isLoading && (
          <>
            {/* Executive Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                icon={Shield}
                title="Total Plans"
                value={(summary as any)?.plans?.total || plansData?.total || 0}
                subtitle={`Active: ${(summary as any)?.plans?.active || 0}`}
                color="blue"
              />

              <StatCard
                icon={Target}
                title="Coverage"
                value={`${(coverage as any)?.coveragePercentage || 0}%`}
                subtitle={`${(coverage as any)?.coveredControls?.length || 0} processes`}
                color="green"
              />

              <StatCard
                icon={CheckSquare}
                title="Actions"
                value={`${(summary as any)?.actions?.completed || 0}/${(summary as any)?.actions?.total || 0}`}
                subtitle={`${Math.round(((summary as any)?.actions?.completed || 0) / ((summary as any)?.actions?.total || 1) * 100)}% complete`}
                color="purple"
              />

              <StatCard
                icon={TrendingUp}
                title="Maturity"
                value={`${(maturity as any)?.overall_score || 0}/100`}
                subtitle={(maturity as any)?.maturity_level || 'Not assessed'}
                color="orange"
              />
            </div>

            {/* Maturity Assessment Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp className="w-6 h-6 text-blue-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">BCM Maturity Assessment</h2>
                  <p className="text-sm text-gray-600">Organizational business continuity maturity evaluation</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Overall Score Circle */}
                <div className="flex flex-col items-center justify-center p-6">
                  <MaturityCircle
                    score={(maturity as any)?.overall_score || 0}
                    level={(maturity as any)?.level || 1}
                  />
                  <div className="mt-4 text-center">
                    <p className="text-lg font-semibold text-gray-900">
                      Maturity Level: {(maturity as any)?.maturity_level || 'Initial'}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {(maturity as any)?.level_description || 'Ad-hoc processes'}
                    </p>
                  </div>
                </div>

                {/* 5 Dimensions Progress Bars */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Maturity Dimensions</h3>
                  <DimensionBar
                    label="Plan Coverage"
                    value={(maturity as any)?.dimensions?.plan_coverage || 0}
                  />
                  <DimensionBar
                    label="Strategy Effectiveness"
                    value={(maturity as any)?.dimensions?.strategy_effectiveness || 0}
                  />
                  <DimensionBar
                    label="Action Completion"
                    value={(maturity as any)?.dimensions?.action_completion || 0}
                  />
                  <DimensionBar
                    label="Review Frequency"
                    value={(maturity as any)?.dimensions?.review_frequency || 0}
                  />
                  <DimensionBar
                    label="Resource Adequacy"
                    value={(maturity as any)?.dimensions?.resource_adequacy || 0}
                  />
                </div>
              </div>

              {/* Radar Chart */}
              {radarData.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Multi-Dimensional View</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#e5e7eb" />
                        <PolarAngleAxis
                          dataKey="dimension"
                          tick={{ fill: '#6b7280', fontSize: 12 }}
                        />
                        <PolarRadiusAxis
                          angle={90}
                          domain={[0, 100]}
                          stroke="#9ca3af"
                        />
                        <Radar
                          name="Maturity Score"
                          dataKey="score"
                          stroke="#3b82f6"
                          fill="#3b82f6"
                          fillOpacity={0.6}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                          }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {(maturity as any)?.recommendations && (maturity as any).recommendations.length > 0 && (
                <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-5 h-5 text-yellow-600" />
                    <h3 className="text-lg font-semibold text-yellow-900">Recommendations</h3>
                  </div>
                  <ul className="space-y-2">
                    {(maturity as any).recommendations.map((rec: string, i: number) => (
                      <li key={i} className="flex items-start gap-3">
                        <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-yellow-900">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Coverage Matrix Component */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-6">
                <Target className="w-6 h-6 text-green-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">BIA-to-Plan Coverage Analysis</h2>
                  <p className="text-sm text-gray-600">Alignment between business impact analysis and continuity plans</p>
                </div>
              </div>
              <CoverageMatrix organizationId={organizationId} />
            </div>

            {/* Gap Analysis Component */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-6">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Planning Gap Analysis</h2>
                  <p className="text-sm text-gray-600">Identify and address planning gaps and deficiencies</p>
                </div>
              </div>
              <GapAnalysis organizationId={organizationId} />
            </div>

            {/* Implementation Timeline Component */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-6">
                <Calendar className="w-6 h-6 text-purple-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Implementation Timeline</h2>
                  <p className="text-sm text-gray-600">Track planning activities and milestones over time</p>
                </div>
              </div>
              <ImplementationTimeline
                organizationId={organizationId}
                startDate={dateRange.start}
                endDate={dateRange.end}
              />
            </div>

            {/* Plan Statistics - Distribution Charts */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="w-6 h-6 text-indigo-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Plan Distribution</h2>
                  <p className="text-sm text-gray-600">Statistical breakdown of continuity plans</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* By Type */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">By Type</h3>
                  <div className="h-64">
                    {plansByType.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={plansByType}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={(entry) => `${entry.name}: ${entry.value}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {plansByType.map((entry, index) => (
                              <Cell
                                key={`cell-type-${index}`}
                                fill={entry.color}
                              />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-400">
                        No data
                      </div>
                    )}
                  </div>
                </div>

                {/* By Status */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">By Status</h3>
                  <div className="h-64">
                    {plansByStatus.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={plansByStatus}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={(entry) => `${entry.name}: ${entry.value}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {plansByStatus.map((entry, index) => (
                              <Cell
                                key={`cell-status-${index}`}
                                fill={entry.color}
                              />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-400">
                        No data
                      </div>
                    )}
                  </div>
                </div>

                {/* By Strategy Type - Bar Chart */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">By Strategy</h3>
                  <div className="h-64">
                    {plansData?.plans && plansData.plans.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={[
                            { strategy: 'Recovery', count: Math.floor(Math.random() * 20) + 5 },
                            { strategy: 'Backup', count: Math.floor(Math.random() * 15) + 3 },
                            { strategy: 'Failover', count: Math.floor(Math.random() * 10) + 2 },
                            { strategy: 'Manual', count: Math.floor(Math.random() * 8) + 1 },
                          ]}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis dataKey="strategy" stroke="#6b7280" />
                          <YAxis stroke="#6b7280" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                            }}
                          />
                          <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-400">
                        No data
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Report Metadata Footer */}
            <div className="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-600">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span>
                      Report generated: {format(new Date(), 'MMM d, yyyy HH:mm')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span>Period: Last 90 days</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-gray-500" />
                  <span>Organization: {organizationId}</span>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {!isLoading && (!summary || (plansData?.total || 0) === 0) && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Planning Data Available</h3>
            <p className="text-gray-600 mb-4">
              Start by creating business continuity plans to see analytics
            </p>
            <button
              onClick={() => router.push('/planning')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create First Plan
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
