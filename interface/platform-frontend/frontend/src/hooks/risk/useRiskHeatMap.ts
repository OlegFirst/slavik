/**
 * useRiskHeatMap Hook
 * React Query hook for 5x5 risk matrix heat map data
 * Real API integration via riskClient
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type { RiskHeatMap } from '@/types/risk';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for risk heat map
 * Provides centralized query key management
 */
export const heatMapKeys = {
  all: ['riskHeatMap'] as const,
  byOrg: (organizationId?: string) =>
    organizationId ? [...heatMapKeys.all, organizationId] as const : heatMapKeys.all,
};

// ==================== TYPES ====================

/**
 * Options for useRiskHeatMap query hook
 */
export interface UseRiskHeatMapOptions {
  organizationId?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchInterval?: number | false;
  refetchOnWindowFocus?: boolean;
}

// ==================== HOOKS ====================

/**
 * Hook to fetch risk heat map data (5x5 matrix)
 * Provides risk distribution across likelihood and impact dimensions
 *
 * @param options - Query options
 * @returns Query result with heat map data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: heatMap, isLoading, error } = useRiskHeatMap({
 *   enabled: true,
 *   organizationId: 'org-123',
 * });
 *
 * if (heatMap) {
 *   console.log('Matrix:', heatMap.matrix); // 5x5 array of risk counts
 *   console.log('Total Risks:', heatMap.total_risks);
 *   console.log('Critical Count:', heatMap.critical_count);
 *   console.log('High Count:', heatMap.high_count);
 *   console.log('Medium Count:', heatMap.medium_count);
 *   console.log('Low Count:', heatMap.low_count);
 *   console.log('Risks by Cell:', heatMap.risks_by_cell);
 * }
 * ```
 *
 * @example
 * ```tsx
 * // Accessing specific cell data
 * const { data: heatMap } = useRiskHeatMap();
 *
 * if (heatMap) {
 *   // Get risks in cell (likelihood=4, impact=5)
 *   const cellKey = '4_5';
 *   const risksInCell = heatMap.risks_by_cell[cellKey] || [];
 *
 *   console.log(`Risks with likelihood=4, impact=5:`, risksInCell);
 * }
 * ```
 */
export function useRiskHeatMap(options: UseRiskHeatMapOptions = {}) {
  const {
    organizationId,
    enabled = true,
    staleTime,
    gcTime,
    refetchInterval,
    refetchOnWindowFocus,
  } = options;

  return useQuery({
    queryKey: heatMapKeys.byOrg(organizationId),
    queryFn: () => riskClient.getRiskHeatMap(organizationId),

    // Enable/disable query
    enabled,

    // Caching strategy - heat map data can change as risks are added/updated
    staleTime: staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: gcTime ?? 10 * 60 * 1000, // 10 minutes

    // Control refetching
    refetchOnWindowFocus: refetchOnWindowFocus ?? true,
    refetchInterval: refetchInterval ?? false,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}
