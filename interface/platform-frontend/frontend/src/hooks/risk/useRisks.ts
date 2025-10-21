/**
 * useRisks Hook
 * React Query hook for listing risks with filters
 * Real API integration via riskClient.getRisks
 * Week 5 - Risk Assessment Module
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { riskClient, type RiskFilters } from '@/lib/api/risk-client';
import type { Risk } from '@/types/risk';
import { RiskCategory, RiskStatus } from '@/types/risk';

export interface UseRisksParams {
  organization_id: string;
  category?: RiskCategory | RiskCategory[];
  status?: RiskStatus | RiskStatus[];
  min_score?: number;
  max_score?: number;
  risk_owner_id?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface UseRisksOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface RisksResponse {
  risks: Risk[];
  total: number;
}

/**
 * Query key factory for risks
 * Provides consistent cache key generation
 */
export const riskQueryKeys = {
  all: ['risks'] as const,
  lists: () => [...riskQueryKeys.all, 'list'] as const,
  list: (params: UseRisksParams) => [...riskQueryKeys.lists(), params] as const,
  details: () => [...riskQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...riskQueryKeys.details(), id] as const,
};

/**
 * Hook to fetch and cache risks list
 *
 * @param params - Filter parameters (organization_id, category, status, etc.)
 * @param options - React Query options
 * @returns Query result with risks data, loading state, error
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useRisks({
 *   organization_id: 'org-123',
 *   category: RiskCategory.CYBERSECURITY,
 *   status: RiskStatus.MONITORING
 * });
 *
 * if (data) {
 *   console.log(`Found ${data.length} risks`);
 * }
 * ```
 */
export function useRisks(
  params: UseRisksParams,
  options: UseRisksOptions = {}
) {
  return useQuery({
    queryKey: riskQueryKeys.list(params),
    queryFn: async () => {
      // Convert params to RiskFilters format
      const filters: RiskFilters = {
        organization_id: params.organization_id,
        category: Array.isArray(params.category) ? params.category[0] : params.category,
        status: Array.isArray(params.status) ? params.status[0] : params.status,
        min_score: params.min_score,
        max_score: params.max_score,
        owner_id: params.risk_owner_id,
        skip: params.skip,
        limit: params.limit,
      };

      return riskClient.getRisks(filters);
    },

    // Default caching strategy
    staleTime: options.staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: options.gcTime ?? 10 * 60 * 1000, // 10 minutes (formerly cacheTime)

    // Control refetching
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,

    // Enable/disable query
    enabled: options.enabled ?? true,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook variant for critical risks only (score >= 20)
 *
 * @example
 * ```tsx
 * const { data: criticalRisks } = useCriticalRisks('org-123');
 * ```
 */
export function useCriticalRisks(
  organization_id: string,
  options: UseRisksOptions = {}
) {
  return useRisks(
    {
      organization_id,
      min_score: 20,
      max_score: 25,
    },
    options
  );
}

/**
 * Hook variant for high risks only (score 15-19)
 *
 * @example
 * ```tsx
 * const { data: highRisks } = useHighRisks('org-123');
 * ```
 */
export function useHighRisks(
  organization_id: string,
  options: UseRisksOptions = {}
) {
  return useRisks(
    {
      organization_id,
      min_score: 15,
      max_score: 19,
    },
    options
  );
}

/**
 * Hook variant for active risks only
 *
 * @example
 * ```tsx
 * const { data: activeRisks } = useActiveRisks('org-123', {
 *   category: RiskCategory.OPERATIONAL
 * });
 * ```
 */
export function useActiveRisks(
  organization_id: string,
  additionalParams: Omit<UseRisksParams, 'organization_id'> = {},
  options: UseRisksOptions = {}
) {
  return useRisks(
    {
      organization_id,
      ...additionalParams,
      status: RiskStatus.MONITORING,
    },
    options
  );
}

/**
 * Hook variant for risks under treatment
 *
 * @example
 * ```tsx
 * const { data: treatedRisks } = useTreatedRisks('org-123');
 * ```
 */
export function useTreatedRisks(
  organization_id: string,
  additionalParams: Omit<UseRisksParams, 'organization_id' | 'status'> = {},
  options: UseRisksOptions = {}
) {
  return useRisks(
    {
      organization_id,
      ...additionalParams,
      status: RiskStatus.TREATED,
    },
    options
  );
}

/**
 * Hook variant for risks by category
 *
 * @example
 * ```tsx
 * const { data: cyberRisks } = useRisksByCategory('org-123', RiskCategory.CYBERSECURITY);
 * ```
 */
export function useRisksByCategory(
  organization_id: string,
  category: RiskCategory,
  additionalParams: Omit<UseRisksParams, 'organization_id' | 'category'> = {},
  options: UseRisksOptions = {}
) {
  return useRisks(
    {
      organization_id,
      category,
      ...additionalParams,
    },
    options
  );
}

/**
 * Hook variant for risks by owner
 *
 * @example
 * ```tsx
 * const { data: myRisks } = useRisksByOwner('org-123', 'user-456');
 * ```
 */
export function useRisksByOwner(
  organization_id: string,
  risk_owner_id: string,
  additionalParams: Omit<UseRisksParams, 'organization_id' | 'risk_owner_id'> = {},
  options: UseRisksOptions = {}
) {
  return useRisks(
    {
      organization_id,
      risk_owner_id,
      ...additionalParams,
    },
    options
  );
}

/**
 * Prefetch utility for risks list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href="/risks"
 *   onMouseEnter={() => prefetchRisks(queryClient, {
 *     organization_id: 'org-123',
 *     category: RiskCategory.OPERATIONAL
 *   })}
 * >
 * ```
 */
export function prefetchRisks(
  queryClient: any,
  params: UseRisksParams
) {
  return queryClient.prefetchQuery({
    queryKey: riskQueryKeys.list(params),
    queryFn: async () => {
      const filters: RiskFilters = {
        organization_id: params.organization_id,
        category: Array.isArray(params.category) ? params.category[0] : params.category,
        status: Array.isArray(params.status) ? params.status[0] : params.status,
        min_score: params.min_score,
        max_score: params.max_score,
        owner_id: params.risk_owner_id,
        skip: params.skip,
        limit: params.limit,
      };

      return riskClient.getRisks(filters);
    },
    staleTime: 5 * 60 * 1000,
  });
}
