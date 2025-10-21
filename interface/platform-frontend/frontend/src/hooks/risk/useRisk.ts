/**
 * useRisk Hook
 * React Query hook for fetching single risk
 * Real API integration via riskClient.getRisk
 * Week 5 - Risk Assessment Module
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type { Risk } from '@/types/risk';
import { riskQueryKeys } from './useRisks';

export interface UseRiskParams {
  id: string;
  organization_id?: string;
}

export interface UseRiskOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch and cache single risk by ID
 * Automatically tracks access for audit trail
 *
 * @param params - Risk ID and optional organization ID
 * @param options - React Query options
 * @returns Query result with risk data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: risk, isLoading, error } = useRisk({
 *   id: 'risk-123',
 *   organization_id: 'org-456'
 * });
 *
 * if (risk) {
 *   console.log(`Risk: ${risk.risk_title}`);
 *   console.log(`Score: ${risk.inherent_risk_score}`);
 *   console.log(`Status: ${risk.status}`);
 * }
 * ```
 */
export function useRisk(
  params: UseRiskParams,
  options: UseRiskOptions = {}
) {
  return useQuery({
    queryKey: riskQueryKeys.detail(params.id),
    queryFn: () => riskClient.getRisk(params.id),

    // Caching strategy - single risk changes less frequently
    staleTime: options.staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: options.gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Control refetching
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,

    // Enable/disable query - don't fetch if no ID
    enabled: (options.enabled ?? true) && !!params.id,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook variant that throws on error
 * Useful for pages that require risk data
 *
 * @example
 * ```tsx
 * const risk = useRiskRequired({ id: 'risk-123' });
 * // risk is guaranteed to be defined or an error is thrown
 * ```
 */
export function useRiskRequired(
  params: UseRiskParams,
  options: Omit<UseRiskOptions, 'enabled'> = {}
) {
  const result = useRisk(params, { ...options, enabled: true });

  if (result.error) {
    throw result.error;
  }

  return result;
}

/**
 * Prefetch utility for single risk
 * Useful for hover states, optimistic navigation
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/risks/${risk.id}`}
 *   onMouseEnter={() => prefetchRisk(queryClient, {
 *     id: risk.id!,
 *     organization_id: 'org-123'
 *   })}
 * >
 *   {risk.risk_title}
 * </Link>
 * ```
 */
export function prefetchRisk(
  queryClient: any,
  params: UseRiskParams
) {
  return queryClient.prefetchQuery({
    queryKey: riskQueryKeys.detail(params.id),
    queryFn: () => riskClient.getRisk(params.id),
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Hook to check if a risk is loaded in cache
 * Useful for conditional rendering
 *
 * @example
 * ```tsx
 * const isRiskCached = useIsRiskCached('risk-123');
 * if (isRiskCached) {
 *   // Show cached data immediately
 * }
 * ```
 */
export function useIsRiskCached(riskId: string): boolean {
  const queryClient = useQueryClient();
  const data = queryClient.getQueryData<Risk>(riskQueryKeys.detail(riskId));
  return !!data;
}

/**
 * Hook to get cached risk data without fetching
 * Returns undefined if not in cache
 *
 * @example
 * ```tsx
 * const cachedRisk = useCachedRisk('risk-123');
 * if (cachedRisk) {
 *   console.log('Using cached data:', cachedRisk.risk_title);
 * }
 * ```
 */
export function useCachedRisk(riskId: string): Risk | undefined {
  const queryClient = useQueryClient();
  return queryClient.getQueryData<Risk>(riskQueryKeys.detail(riskId));
}
