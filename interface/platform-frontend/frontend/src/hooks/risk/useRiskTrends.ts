/**
 * useRiskTrends Hook
 * React Query hook for risk trend analysis over time
 * Real API integration via riskClient
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type { RiskTrends } from '@/types/risk';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for risk trends
 * Provides centralized query key management
 */
export const trendKeys = {
  all: ['riskTrends'] as const,
  byPeriod: (days: number, organizationId?: string) =>
    organizationId
      ? [...trendKeys.all, days, organizationId] as const
      : [...trendKeys.all, days] as const,
};

// ==================== TYPES ====================

/**
 * Options for useRiskTrends query hook
 */
export interface UseRiskTrendsOptions {
  days?: number;
  organizationId?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchInterval?: number | false;
  refetchOnWindowFocus?: boolean;
}

// ==================== HOOKS ====================

/**
 * Hook to fetch risk trend analysis over time
 * Provides time-series data showing risk evolution
 *
 * @param options - Query options
 * @returns Query result with trend data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: trends, isLoading, error } = useRiskTrends({
 *   days: 90, // Last 90 days
 *   enabled: true,
 * });
 *
 * if (trends) {
 *   console.log('Period:', trends.start_date, 'to', trends.end_date);
 *   console.log('Overall Trend:', trends.overall_trend);
 *   console.log('Avg Score Change:', trends.avg_score_change);
 *   console.log('Total Risks Change:', trends.total_risks_change);
 *
 *   // Access daily data points
 *   trends.daily_data.forEach(point => {
 *     console.log(point.date, ':', {
 *       total: point.total_risks,
 *       critical: point.critical_count,
 *       high: point.high_count,
 *       medium: point.medium_count,
 *       low: point.low_count,
 *       avgScore: point.avg_score,
 *     });
 *   });
 * }
 * ```
 *
 * @example
 * ```tsx
 * // Chart data preparation
 * const { data: trends } = useRiskTrends({ days: 30 });
 *
 * const chartData = trends?.daily_data.map(point => ({
 *   date: new Date(point.date).toLocaleDateString(),
 *   critical: point.critical_count,
 *   high: point.high_count,
 *   medium: point.medium_count,
 *   low: point.low_count,
 * }));
 * ```
 */
export function useRiskTrends(options: UseRiskTrendsOptions = {}) {
  const {
    days = 90,
    organizationId,
    enabled = true,
    staleTime,
    gcTime,
    refetchInterval,
    refetchOnWindowFocus,
  } = options;

  return useQuery({
    queryKey: trendKeys.byPeriod(days, organizationId),
    queryFn: () =>
      riskClient.getRiskTrends({
        days,
        organization_id: organizationId,
      }),

    // Enable/disable query
    enabled,

    // Caching strategy - trend data updates daily
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Control refetching
    refetchOnWindowFocus: refetchOnWindowFocus ?? true,
    refetchInterval: refetchInterval ?? false,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}
