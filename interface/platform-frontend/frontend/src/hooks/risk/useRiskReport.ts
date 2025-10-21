/**
 * useRiskReport Hook
 * React Query hook for generating comprehensive risk reports
 * Real API integration via riskClient
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type { RiskReport } from '@/types/risk';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for risk reports
 * Provides centralized query key management
 */
export const reportKeys = {
  all: ['riskReports'] as const,
  byOrg: (organizationId?: string) =>
    organizationId ? [...reportKeys.all, organizationId] as const : reportKeys.all,
};

// ==================== TYPES ====================

/**
 * Options for useRiskReport query hook
 */
export interface UseRiskReportOptions {
  organizationId?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

// ==================== HOOKS ====================

/**
 * Hook to generate comprehensive risk report
 * Provides complete analytics and dashboard data
 *
 * Note: This query is not enabled by default - must be explicitly triggered
 * by the user to avoid unnecessary report generation
 *
 * @param options - Query options
 * @returns Query result with report data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: report, isLoading, error, refetch } = useRiskReport({
 *   enabled: false, // Don't auto-fetch
 *   organizationId: 'org-123',
 * });
 *
 * // Trigger report generation
 * const handleGenerateReport = () => {
 *   refetch();
 * };
 *
 * if (report) {
 *   console.log('Total Risks:', report.total_risks);
 *   console.log('Active Risks:', report.active_risks);
 *   console.log('Closed Risks:', report.closed_risks);
 *
 *   // By Severity
 *   console.log('Critical:', report.critical_count);
 *   console.log('High:', report.high_count);
 *   console.log('Medium:', report.medium_count);
 *   console.log('Low:', report.low_count);
 *
 *   // By Status
 *   console.log('Status Breakdown:', report.status_breakdown);
 *
 *   // By Category
 *   console.log('Category Breakdown:', report.category_breakdown);
 *
 *   // Averages
 *   console.log('Avg Inherent Score:', report.avg_inherent_score);
 *   console.log('Avg Residual Score:', report.avg_residual_score);
 *
 *   // Treatment
 *   console.log('Total Treatment Plans:', report.total_treatment_plans);
 *   console.log('Strategy Breakdown:', report.treatment_strategy_breakdown);
 *
 *   // Top Risks
 *   console.log('Top Risks:', report.top_risks);
 *
 *   // Trends
 *   console.log('7-day Trend:', report.trend_7d);
 *   console.log('30-day Trend:', report.trend_30d);
 * }
 * ```
 *
 * @example
 * ```tsx
 * // Auto-enabled report for dashboard
 * const { data: report } = useRiskReport({
 *   enabled: true, // Auto-fetch for dashboard
 *   staleTime: 10 * 60 * 1000, // 10 minutes
 * });
 * ```
 */
export function useRiskReport(options: UseRiskReportOptions = {}) {
  const {
    organizationId,
    enabled = false, // Don't auto-fetch by default - user must trigger
    staleTime,
    gcTime,
    refetchOnWindowFocus,
  } = options;

  return useQuery({
    queryKey: reportKeys.byOrg(organizationId),
    queryFn: () => riskClient.getRiskReport(organizationId),

    // Enable/disable query
    enabled,

    // Caching strategy - reports are expensive to generate
    staleTime: staleTime ?? 1 * 60 * 1000, // 1 minute
    gcTime: gcTime ?? 5 * 60 * 1000, // 5 minutes

    // Control refetching
    refetchOnWindowFocus: refetchOnWindowFocus ?? false,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Helper function to calculate risk severity percentages from report
 *
 * @param report - Risk report data
 * @returns Object with severity percentages
 *
 * @example
 * ```tsx
 * const report = useRiskReport({ enabled: true });
 *
 * if (report.data) {
 *   const percentages = getSeverityPercentages(report.data);
 *   console.log('Critical:', percentages.critical + '%');
 *   console.log('High:', percentages.high + '%');
 *   console.log('Medium:', percentages.medium + '%');
 *   console.log('Low:', percentages.low + '%');
 * }
 * ```
 */
export function getSeverityPercentages(report: RiskReport): {
  critical: number;
  high: number;
  medium: number;
  low: number;
} {
  const total = report.total_risks || 1; // Avoid division by zero

  return {
    critical: Math.round((report.critical_count / total) * 100),
    high: Math.round((report.high_count / total) * 100),
    medium: Math.round((report.medium_count / total) * 100),
    low: Math.round((report.low_count / total) * 100),
  };
}

/**
 * Helper function to get trend indicator from report
 *
 * @param report - Risk report data
 * @param period - Period to check ('7d' or '30d')
 * @returns Trend indicator object
 *
 * @example
 * ```tsx
 * const report = useRiskReport({ enabled: true });
 *
 * if (report.data) {
 *   const trend = getTrendIndicator(report.data, '7d');
 *   console.log('Direction:', trend.direction); // 'up' | 'down' | 'stable'
 *   console.log('Value:', trend.value);
 *   console.log('Percentage:', trend.percentage);
 * }
 * ```
 */
export function getTrendIndicator(
  report: RiskReport,
  period: '7d' | '30d' = '7d'
): {
  direction: 'up' | 'down' | 'stable';
  value: number;
  percentage: string;
} {
  const trendValue = period === '7d' ? report.trend_7d : report.trend_30d;
  const value = trendValue ?? 0;

  let direction: 'up' | 'down' | 'stable' = 'stable';
  if (value > 0.5) direction = 'up';
  else if (value < -0.5) direction = 'down';

  return {
    direction,
    value,
    percentage: `${Math.abs(value).toFixed(1)}%`,
  };
}
