/**
 * Risk Module Dashboard Widgets
 * AI Platform ISO 22301 BCM
 *
 * Provides dashboard widgets showing Risk module data:
 * - Critical Risks Alert Card (top 5 critical risks)
 * - Risk Heat Map Mini (3×3 simplified grid)
 * - Risk Trends Chart (last 30 days)
 * - Quick Stats (Critical/High/Medium/Low counts)
 *
 * Uses existing hooks from Risk module:
 * - useRisks, useRiskReport, useRiskTrends
 */

'use client';

import React, { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Shield,
  ArrowRight,
} from 'lucide-react';

import { useRisks, useRiskReport, useRiskTrends } from '@/hooks/risk';
import {
  getRiskSeverity,
  getSeverityColor,
  type RiskSeverity,
} from '@/types/risk';
import type { Risk, RiskReport, RiskTrends } from '@/lib/api/risk-client';

// ============================================================================
// TYPES
// ============================================================================

interface RiskWidgetsProps {
  organizationId: string;
}

interface StatCardProps {
  title: string;
  value: number;
  severity: RiskSeverity;
  icon: React.ReactNode;
  loading?: boolean;
  onClick?: () => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const SEVERITY_COLORS_MAP: Record<RiskSeverity, string> = {
  critical: '#DC2626', // red-600
  high: '#EA580C', // orange-600
  medium: '#CA8A04', // yellow-600
  low: '#16A34A', // green-600
};

// ============================================================================
// LOADING SKELETON COMPONENTS
// ============================================================================

function WidgetSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="h-24 bg-gray-100 rounded"></div>
    </div>
  );
}

function StatSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 animate-pulse">
      <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-8 bg-gray-100 rounded w-2/3"></div>
    </div>
  );
}

// ============================================================================
// STAT CARD COMPONENT
// ============================================================================

function StatCard({ title, value, severity, icon, loading, onClick }: StatCardProps) {
  const severityColor = getSeverityColor(severity);

  if (loading) {
    return <StatSkeleton />;
  }

  return (
    <div
      className={`
        bg-white rounded-lg border-2 p-4 transition-all duration-200
        ${onClick ? 'cursor-pointer hover:shadow-md hover:scale-105' : ''}
        ${severityColor.border}
      `}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={`text-sm font-medium ${severityColor.text}`}>
          {title}
        </span>
        <div className={severityColor.text}>{icon}</div>
      </div>
      <div className={`text-3xl font-bold ${severityColor.text}`}>
        {value}
      </div>
    </div>
  );
}

// ============================================================================
// CRITICAL RISKS WIDGET
// ============================================================================

function CriticalRisksWidget({
  organizationId,
  onClick,
}: {
  organizationId: string;
  onClick?: () => void;
}) {
  const { data, isLoading, error } = useRisks({
    organization_id: organizationId,
    min_score: 20, // Critical threshold
  });

  const criticalRisks = useMemo(() => {
    if (!data) return [];
    return data.slice(0, 5); // Top 5
  }, [data]);

  if (isLoading) {
    return <WidgetSkeleton />;
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-red-200 p-6">
        <div className="flex items-center gap-2 text-red-600 mb-4">
          <AlertTriangle className="h-5 w-5" />
          <h3 className="font-semibold">Critical Risks</h3>
        </div>
        <p className="text-sm text-red-600">Failed to load critical risks</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-red-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-red-600">
          <AlertTriangle className="h-5 w-5" />
          <h3 className="font-semibold">Critical Risks</h3>
        </div>
        <button
          onClick={onClick}
          className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1"
        >
          View All
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {criticalRisks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Shield className="h-12 w-12 mx-auto mb-2 text-green-500" />
          <p className="text-sm">No critical risks</p>
        </div>
      ) : (
        <div className="space-y-2">
          {criticalRisks.map((risk) => {
            const severity = getRiskSeverity(risk.inherent_risk_score);
            const severityColor = getSeverityColor(severity);

            return (
              <div
                key={risk.id}
                className={`p-3 rounded-md border ${severityColor.border} ${severityColor.bg} hover:opacity-80 transition-opacity cursor-pointer`}
                onClick={onClick}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${severityColor.text}`}>
                      {risk.risk_title}
                    </p>
                    {risk.risk_code && (
                      <p className={`text-xs ${severityColor.text} opacity-75 mt-1`}>
                        {risk.risk_code}
                      </p>
                    )}
                  </div>
                  <span className={`text-sm font-bold ${severityColor.text} ml-2`}>
                    {risk.inherent_risk_score}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// RISK HEAT MAP MINI WIDGET
// ============================================================================

function RiskHeatMapMiniWidget({
  organizationId,
  onClick,
}: {
  organizationId: string;
  onClick?: () => void;
}) {
  const { data: report, isLoading, error } = useRiskReport({
    organizationId,
    enabled: true,
  });

  // Create simplified 3x3 grid from report data
  const heatMapData = useMemo(() => {
    if (!report) return null;

    return {
      critical: report.by_severity.critical,
      high: report.by_severity.high,
      medium: report.by_severity.medium,
      low: report.by_severity.low,
      total: report.total_risks,
    };
  }, [report]);

  if (isLoading) {
    return <WidgetSkeleton />;
  }

  if (error || !heatMapData) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-semibold mb-4">Risk Distribution</h3>
        <p className="text-sm text-gray-500">Failed to load heat map</p>
      </div>
    );
  }

  const pieData = [
    { name: 'Critical', value: heatMapData.critical, color: SEVERITY_COLORS_MAP.critical },
    { name: 'High', value: heatMapData.high, color: SEVERITY_COLORS_MAP.high },
    { name: 'Medium', value: heatMapData.medium, color: SEVERITY_COLORS_MAP.medium },
    { name: 'Low', value: heatMapData.low, color: SEVERITY_COLORS_MAP.low },
  ].filter((item) => item.value > 0);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Risk Distribution</h3>
        <button
          onClick={onClick}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          View Heat Map
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      <div className="flex items-center gap-4">
        {/* Pie Chart */}
        <div className="w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={50}
                paddingAngle={2}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="flex-1 space-y-2">
          {pieData.map((item) => {
            const percentage =
              heatMapData.total > 0
                ? Math.round((item.value / heatMapData.total) * 100)
                : 0;

            return (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-700">{item.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">{item.value}</span>
                  <span className="text-gray-500">({percentage}%)</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {heatMapData.total === 0 && (
        <div className="text-center py-4 text-gray-500">
          <p className="text-sm">No risks to display</p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// RISK TRENDS WIDGET
// ============================================================================

function RiskTrendsWidget({
  organizationId,
  onClick,
}: {
  organizationId: string;
  onClick?: () => void;
}) {
  const { data: trends, isLoading, error } = useRiskTrends({
    days: 30,
    organizationId,
    enabled: true,
  });

  const chartData = useMemo(() => {
    if (!trends) return [];

    return trends.data_points.map((point) => ({
      date: new Date(point.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      critical: point.critical,
      high: point.high,
      medium: point.medium,
      low: point.low,
      total: point.total_risks,
    }));
  }, [trends]);

  const trendIndicator = useMemo(() => {
    if (!trends) return null;

    const change = trends.summary.average_score_change;

    // Determine direction from change value
    let direction: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (change > 0.5) direction = 'increasing';
    else if (change < -0.5) direction = 'decreasing';

    return { direction, change };
  }, [trends]);

  if (isLoading) {
    return <WidgetSkeleton />;
  }

  if (error || !trends) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-semibold mb-4">Risk Trends (30 Days)</h3>
        <p className="text-sm text-gray-500">Failed to load trends</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold">Risk Trends (30 Days)</h3>
        </div>
        <button
          onClick={onClick}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          Details
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* Trend Indicator */}
      {trendIndicator && (
        <div className="mb-4 flex items-center gap-2">
          {trendIndicator.direction === 'increasing' && (
            <>
              <TrendingUp className="h-4 w-4 text-red-600" />
              <span className="text-sm text-red-600 font-medium">
                Increasing trend (+{Math.abs(trendIndicator.change).toFixed(1)})
              </span>
            </>
          )}
          {trendIndicator.direction === 'decreasing' && (
            <>
              <TrendingDown className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-600 font-medium">
                Decreasing trend ({trendIndicator.change.toFixed(1)})
              </span>
            </>
          )}
          {trendIndicator.direction === 'stable' && (
            <span className="text-sm text-gray-600 font-medium">
              Stable trend
            </span>
          )}
        </div>
      )}

      {/* Chart */}
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="criticalGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SEVERITY_COLORS_MAP.critical} stopOpacity={0.3} />
                <stop offset="95%" stopColor={SEVERITY_COLORS_MAP.critical} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="highGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SEVERITY_COLORS_MAP.high} stopOpacity={0.3} />
                <stop offset="95%" stopColor={SEVERITY_COLORS_MAP.high} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              stroke="#9CA3AF"
            />
            <YAxis
              tick={{ fontSize: 11 }}
              stroke="#9CA3AF"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
              }}
            />
            <Area
              type="monotone"
              dataKey="critical"
              stackId="1"
              stroke={SEVERITY_COLORS_MAP.critical}
              fill="url(#criticalGradient)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="high"
              stackId="1"
              stroke={SEVERITY_COLORS_MAP.high}
              fill="url(#highGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ============================================================================
// QUICK STATS WIDGET
// ============================================================================

function QuickStatsWidget({
  organizationId,
  onClick,
}: {
  organizationId: string;
  onClick?: () => void;
}) {
  const { data: report, isLoading } = useRiskReport({
    organizationId,
    enabled: true,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Risk Summary</h3>
        <button
          onClick={onClick}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          View All
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          title="Critical"
          value={report?.by_severity.critical ?? 0}
          severity="critical"
          icon={<AlertTriangle className="h-5 w-5" />}
          loading={isLoading}
          onClick={onClick}
        />
        <StatCard
          title="High"
          value={report?.by_severity.high ?? 0}
          severity="high"
          icon={<AlertTriangle className="h-5 w-5" />}
          loading={isLoading}
          onClick={onClick}
        />
        <StatCard
          title="Medium"
          value={report?.by_severity.medium ?? 0}
          severity="medium"
          icon={<Activity className="h-5 w-5" />}
          loading={isLoading}
          onClick={onClick}
        />
        <StatCard
          title="Low"
          value={report?.by_severity.low ?? 0}
          severity="low"
          icon={<Shield className="h-5 w-5" />}
          loading={isLoading}
          onClick={onClick}
        />
      </div>

      {report && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Total Risks</span>
            <span className="font-bold text-gray-900 text-lg">
              {report.total_risks}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function RiskWidgets({ organizationId }: RiskWidgetsProps) {
  const router = useRouter();

  const handleNavigateToRisk = () => {
    router.push('/risk');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Risk Management</h2>
        <button
          onClick={handleNavigateToRisk}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center gap-2"
        >
          Open Risk Module
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* Desktop Layout: 2x2 Grid */}
      <div className="hidden md:grid md:grid-cols-2 gap-6">
        {/* Top Left: Critical Risks */}
        <CriticalRisksWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />

        {/* Top Right: Heat Map */}
        <RiskHeatMapMiniWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />

        {/* Bottom Left: Trends */}
        <RiskTrendsWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />

        {/* Bottom Right: Quick Stats */}
        <div>
          <QuickStatsWidget
            organizationId={organizationId}
            onClick={handleNavigateToRisk}
          />
        </div>
      </div>

      {/* Mobile Layout: Stacked */}
      <div className="md:hidden space-y-4">
        <QuickStatsWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />
        <CriticalRisksWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />
        <RiskHeatMapMiniWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />
        <RiskTrendsWidget
          organizationId={organizationId}
          onClick={handleNavigateToRisk}
        />
      </div>
    </div>
  );
}
