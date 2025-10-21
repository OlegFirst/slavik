/**
 * BIA Dashboard Widgets Component
 * Displays BIA module data in 4 professional widget cards
 * - Critical Processes: Top 5 processes with RTO < 4h
 * - Coverage Stats: BIA completion percentage
 * - Impact Analysis: Financial/Operational/Reputational metrics
 * - Dependency Map: Simple visualization of dependencies
 *
 * Real data integration via useBIAProcesses and useBIASummary hooks
 * Production-ready, TypeScript strict, no mocks
 */

'use client';

import React, { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  Activity,
  DollarSign,
  Users,
  Shield,
  Network,
  Target,
  Zap,
} from 'lucide-react';
import { useBIAProcesses } from '@/hooks/bia/useBIAProcesses';
import { useBIASummary, formatPotentialLoss, formatAverageRTO } from '@/hooks/bia/useBIASummary';
import { BIAProcess, CriticalityLevel, ReputationalImpact } from '@/types/bia';
import { CardSkeleton } from '@/components/loading/CardSkeleton';

interface BIAWidgetsProps {
  organizationId: string;
}

/**
 * Main BIA Widgets Component
 * Grid layout: 2x2 responsive grid
 */
export function BIAWidgets({ organizationId }: BIAWidgetsProps) {
  const router = useRouter();

  // Fetch all processes and summary data
  const {
    data: allProcesses,
    isLoading: processesLoading,
    error: processesError,
  } = useBIAProcesses({ tenant_id: organizationId });

  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useBIASummary(organizationId);

  const isLoading = processesLoading || summaryLoading;
  const hasError = processesError || summaryError;

  // Calculate critical processes (RTO < 4 hours)
  const criticalProcesses = useMemo(() => {
    if (!allProcesses) return [];
    return allProcesses
      .filter((p) => p.rto_hours < 4)
      .sort((a, b) => a.rto_hours - b.rto_hours)
      .slice(0, 5);
  }, [allProcesses]);

  // Calculate impact analysis metrics
  const impactMetrics = useMemo(() => {
    if (!allProcesses) {
      return {
        totalFinancial24h: 0,
        operationalCount: 0,
        reputationalRisk: 'none' as ReputationalImpact,
        avgImpact: 0,
      };
    }

    let totalFinancial = 0;
    let operationalCount = 0;
    const reputationalLevels: Record<ReputationalImpact, number> = {
      [ReputationalImpact.NONE]: 0,
      [ReputationalImpact.MINOR]: 1,
      [ReputationalImpact.MODERATE]: 2,
      [ReputationalImpact.MAJOR]: 3,
      [ReputationalImpact.CATASTROPHIC]: 4,
    };
    let maxReputational = ReputationalImpact.NONE;

    allProcesses.forEach((process) => {
      // Financial impact
      if (process.financial_impact?.['24_hours']) {
        totalFinancial += process.financial_impact['24_hours'];
      }

      // Operational impact
      if (process.operational_impact && Object.keys(process.operational_impact).length > 0) {
        operationalCount++;
      }

      // Reputational impact
      if (
        process.reputational_impact &&
        reputationalLevels[process.reputational_impact] > reputationalLevels[maxReputational]
      ) {
        maxReputational = process.reputational_impact;
      }
    });

    return {
      totalFinancial24h: totalFinancial,
      operationalCount,
      reputationalRisk: maxReputational,
      avgImpact: allProcesses.length > 0 ? totalFinancial / allProcesses.length : 0,
    };
  }, [allProcesses]);

  // Calculate dependency statistics
  const dependencyStats = useMemo(() => {
    if (!allProcesses) {
      return {
        totalDependencies: 0,
        criticalDependencies: 0,
        dependencyTypes: {} as Record<string, number>,
        avgPerProcess: 0,
      };
    }

    let total = 0;
    let critical = 0;
    const types: Record<string, number> = {};

    allProcesses.forEach((process) => {
      if (process.dependencies && Array.isArray(process.dependencies)) {
        total += process.dependencies.length;
        critical += process.dependencies.filter((d) => d.required).length;

        process.dependencies.forEach((dep) => {
          types[dep.type] = (types[dep.type] || 0) + 1;
        });
      }
    });

    return {
      totalDependencies: total,
      criticalDependencies: critical,
      dependencyTypes: types,
      avgPerProcess: allProcesses.length > 0 ? total / allProcesses.length : 0,
    };
  }, [allProcesses]);

  // Navigate to BIA module
  const handleNavigateToBIA = () => {
    router.push('/bia');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CardSkeleton count={4} showFooter={false} />
      </div>
    );
  }

  // Error state
  if (hasError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Failed to load BIA data</h3>
            <p className="text-sm text-red-700 mt-1">
              {processesError?.message || summaryError?.message || 'Unknown error occurred'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Widget 1: Critical Processes */}
      <CriticalProcessesWidget
        processes={criticalProcesses}
        totalProcesses={allProcesses?.length || 0}
        onClick={handleNavigateToBIA}
      />

      {/* Widget 2: BIA Coverage Stats */}
      <CoverageStatsWidget summary={summary} onClick={handleNavigateToBIA} />

      {/* Widget 3: Impact Analysis Summary */}
      <ImpactAnalysisWidget metrics={impactMetrics} onClick={handleNavigateToBIA} />

      {/* Widget 4: Dependency Map Preview */}
      <DependencyMapWidget stats={dependencyStats} onClick={handleNavigateToBIA} />
    </div>
  );
}

/**
 * Widget 1: Critical Processes Card
 * Shows top 5 processes with RTO < 4 hours
 */
interface CriticalProcessesWidgetProps {
  processes: BIAProcess[];
  totalProcesses: number;
  onClick: () => void;
}

function CriticalProcessesWidget({
  processes,
  totalProcesses,
  onClick,
}: CriticalProcessesWidgetProps) {
  return (
    <div
      className="bg-white rounded-xl shadow-lg border border-gray-200 hover:border-orange-300 transition-all duration-200 cursor-pointer group"
      onClick={onClick}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">Critical Processes</h3>
              <p className="text-sm text-gray-600">RTO &lt; 4 hours</p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-orange-600 transition-colors" />
        </div>

        {/* Stats Badge */}
        <div className="flex items-center gap-2 mb-4">
          <div className="px-3 py-1 bg-orange-50 border border-orange-200 rounded-full">
            <span className="text-2xl font-bold text-orange-600">{processes.length}</span>
            <span className="text-sm text-gray-600 ml-1">of {totalProcesses}</span>
          </div>
        </div>

        {/* Process List */}
        <div className="space-y-3">
          {processes.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No critical processes defined</p>
              <p className="text-xs text-gray-400 mt-1">Click to add processes</p>
            </div>
          ) : (
            processes.map((process, idx) => (
              <div
                key={process.id || idx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 text-sm truncate">
                    {process.name}
                  </p>
                  {process.department && (
                    <p className="text-xs text-gray-600 mt-0.5 truncate">
                      {process.department}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2 ml-3">
                  <Clock className="w-4 h-4 text-orange-500" />
                  <span className="font-semibold text-orange-600 text-sm">
                    {process.rto_hours}h
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* View All Link */}
        {processes.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClick();
              }}
              className="text-sm text-orange-600 hover:text-orange-700 font-medium flex items-center gap-1 group"
            >
              View all processes
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Widget 2: BIA Coverage Stats
 * Shows completion percentage with progress bar
 */
interface CoverageStatsWidgetProps {
  summary: {
    total_processes: number;
    critical_processes: number;
    bia_completion_rate: number;
    average_rto_hours: number;
  } | undefined;
  onClick: () => void;
}

function CoverageStatsWidget({ summary, onClick }: CoverageStatsWidgetProps) {
  const completionPercentage = summary ? Math.round(summary.bia_completion_rate * 100) : 0;
  const totalProcesses = summary?.total_processes || 0;
  const completedProcesses = Math.round(totalProcesses * (summary?.bia_completion_rate || 0));

  // Determine status color
  const getStatusColor = (percentage: number) => {
    if (percentage >= 90) return 'green';
    if (percentage >= 70) return 'blue';
    if (percentage >= 50) return 'yellow';
    return 'red';
  };

  const statusColor = getStatusColor(completionPercentage);
  const colorClasses = {
    green: {
      bg: 'bg-green-100',
      text: 'text-green-600',
      progress: 'bg-green-600',
      border: 'border-green-200',
    },
    blue: {
      bg: 'bg-blue-100',
      text: 'text-blue-600',
      progress: 'bg-blue-600',
      border: 'border-blue-200',
    },
    yellow: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-600',
      progress: 'bg-yellow-600',
      border: 'border-yellow-200',
    },
    red: {
      bg: 'bg-red-100',
      text: 'text-red-600',
      progress: 'bg-red-600',
      border: 'border-red-200',
    },
  };

  const colors = colorClasses[statusColor];

  return (
    <div
      className="bg-white rounded-xl shadow-lg border border-gray-200 hover:border-blue-300 transition-all duration-200 cursor-pointer group"
      onClick={onClick}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 ${colors.bg} rounded-lg`}>
              <Activity className={`w-6 h-6 ${colors.text}`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">BIA Coverage</h3>
              <p className="text-sm text-gray-600">Assessment completion</p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
        </div>

        {/* Completion Percentage */}
        <div className="mb-4">
          <div className="flex items-baseline gap-2 mb-2">
            <span className={`text-4xl font-bold ${colors.text}`}>{completionPercentage}%</span>
            <span className="text-gray-600 text-sm">complete</span>
          </div>

          {/* Progress Bar */}
          <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`${colors.progress} h-3 rounded-full transition-all duration-500`}
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className={`p-3 ${colors.bg} ${colors.border} border rounded-lg`}>
            <div className="text-xs text-gray-600 mb-1">Total Processes</div>
            <div className={`text-2xl font-bold ${colors.text}`}>{totalProcesses}</div>
          </div>
          <div className={`p-3 ${colors.bg} ${colors.border} border rounded-lg`}>
            <div className="text-xs text-gray-600 mb-1">Completed</div>
            <div className={`text-2xl font-bold ${colors.text}`}>{completedProcesses}</div>
          </div>
        </div>

        {/* Average RTO */}
        {summary && summary.average_rto_hours > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Average RTO:</span>
              <span className="font-semibold text-gray-900">
                {formatAverageRTO(summary.average_rto_hours)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Widget 3: Impact Analysis Summary
 * Shows Financial, Operational, and Reputational metrics
 */
interface ImpactAnalysisWidgetProps {
  metrics: {
    totalFinancial24h: number;
    operationalCount: number;
    reputationalRisk: ReputationalImpact;
    avgImpact: number;
  };
  onClick: () => void;
}

function ImpactAnalysisWidget({ metrics, onClick }: ImpactAnalysisWidgetProps) {
  // Map reputational impact to display values
  const getReputationalDisplay = (risk: ReputationalImpact) => {
    const displays: Record<ReputationalImpact, { label: string; color: string; bg: string }> = {
      [ReputationalImpact.NONE]: {
        label: 'None',
        color: 'text-gray-600',
        bg: 'bg-gray-100',
      },
      [ReputationalImpact.MINOR]: {
        label: 'Minor',
        color: 'text-blue-600',
        bg: 'bg-blue-100',
      },
      [ReputationalImpact.MODERATE]: {
        label: 'Moderate',
        color: 'text-yellow-600',
        bg: 'bg-yellow-100',
      },
      [ReputationalImpact.MAJOR]: {
        label: 'Major',
        color: 'text-orange-600',
        bg: 'bg-orange-100',
      },
      [ReputationalImpact.CATASTROPHIC]: {
        label: 'Critical',
        color: 'text-red-600',
        bg: 'bg-red-100',
      },
    };
    return displays[risk];
  };

  const reputationalDisplay = getReputationalDisplay(metrics.reputationalRisk);

  return (
    <div
      className="bg-white rounded-xl shadow-lg border border-gray-200 hover:border-purple-300 transition-all duration-200 cursor-pointer group"
      onClick={onClick}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">Impact Analysis</h3>
              <p className="text-sm text-gray-600">Business impact metrics</p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-purple-600 transition-colors" />
        </div>

        {/* Impact Metrics */}
        <div className="space-y-4">
          {/* Financial Impact */}
          <div className="p-4 bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-5 h-5 text-red-600" />
              <span className="text-sm font-medium text-gray-700">Financial Impact (24h)</span>
            </div>
            <div className="text-2xl font-bold text-red-600">
              {formatPotentialLoss(metrics.totalFinancial24h)}
            </div>
            {metrics.avgImpact > 0 && (
              <div className="text-xs text-gray-600 mt-1">
                Avg: {formatPotentialLoss(metrics.avgImpact)} per process
              </div>
            )}
          </div>

          {/* Operational Impact */}
          <div className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">Operational Impact</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {metrics.operationalCount}
            </div>
            <div className="text-xs text-gray-600 mt-1">processes affected</div>
          </div>

          {/* Reputational Impact */}
          <div
            className={`p-4 bg-gradient-to-r from-${reputationalDisplay.bg.split('-')[1]}-50 to-gray-50 border ${reputationalDisplay.bg.replace('bg-', 'border-').replace('100', '200')} rounded-lg`}
          >
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-gray-700">Reputational Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${reputationalDisplay.color}`}>
                {reputationalDisplay.label}
              </span>
              {metrics.reputationalRisk !== ReputationalImpact.NONE && (
                <AlertTriangle className={`w-5 h-5 ${reputationalDisplay.color}`} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Widget 4: Dependency Map Preview
 * Shows dependency statistics and visualization
 */
interface DependencyMapWidgetProps {
  stats: {
    totalDependencies: number;
    criticalDependencies: number;
    dependencyTypes: Record<string, number>;
    avgPerProcess: number;
  };
  onClick: () => void;
}

function DependencyMapWidget({ stats, onClick }: DependencyMapWidgetProps) {
  // Get top 3 dependency types
  const topTypes = Object.entries(stats.dependencyTypes)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  // Icon mapping for dependency types
  const getTypeIcon = (type: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      process: <Activity className="w-4 h-4" />,
      technology: <Zap className="w-4 h-4" />,
      people: <Users className="w-4 h-4" />,
      facility: <Target className="w-4 h-4" />,
      supplier: <Network className="w-4 h-4" />,
    };
    return iconMap[type] || <Network className="w-4 h-4" />;
  };

  return (
    <div
      className="bg-white rounded-xl shadow-lg border border-gray-200 hover:border-green-300 transition-all duration-200 cursor-pointer group"
      onClick={onClick}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Network className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">Dependencies</h3>
              <p className="text-sm text-gray-600">Process relationships</p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-green-600 transition-colors" />
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="text-xs text-gray-600 mb-1">Total</div>
            <div className="text-2xl font-bold text-green-600">
              {stats.totalDependencies}
            </div>
          </div>
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-xs text-gray-600 mb-1">Critical</div>
            <div className="text-2xl font-bold text-red-600">
              {stats.criticalDependencies}
            </div>
          </div>
        </div>

        {/* Average per Process */}
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Avg per process:</span>
            <span className="font-semibold text-gray-900">
              {stats.avgPerProcess.toFixed(1)}
            </span>
          </div>
        </div>

        {/* Dependency Types Breakdown */}
        {topTypes.length > 0 ? (
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-700 mb-2">Top Categories:</div>
            {topTypes.map(([type, count]) => (
              <div
                key={type}
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <div className="text-green-600">{getTypeIcon(type)}</div>
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {type}
                  </span>
                </div>
                <span className="text-sm font-semibold text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 text-gray-500">
            <Network className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No dependencies mapped</p>
            <p className="text-xs text-gray-400 mt-1">Click to add dependencies</p>
          </div>
        )}

        {/* Critical Dependencies Indicator */}
        {stats.criticalDependencies > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle2 className="w-4 h-4 text-orange-500" />
              <span className="text-gray-600">
                <span className="font-semibold text-orange-600">
                  {stats.criticalDependencies}
                </span>{' '}
                critical dependencies require attention
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
