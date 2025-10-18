/**
 * useBIAProcess Hook
 * React Query hook for fetching single BIA process
 * Real API integration via biaAPI.getProcess
 */

import { useQuery } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import type { BIAProcess } from '@/types/bia';

export interface UseBIAProcessParams {
  id: number;
  tenant_id: string;
}

export interface UseBIAProcessOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch and cache single BIA process by ID
 *
 * @param params - Process ID and tenant ID
 * @param options - React Query options
 * @returns Query result with process data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: process, isLoading, error } = useBIAProcess({
 *   id: 123,
 *   tenant_id: 'org-123'
 * });
 * ```
 */
export function useBIAProcess(
  params: UseBIAProcessParams,
  options: UseBIAProcessOptions = {}
) {
  return useQuery({
    queryKey: ['bia', 'process', params.id, params.tenant_id],
    queryFn: () => biaAPI.getProcess(params.id, params.tenant_id),

    // Caching strategy - single process changes less frequently
    staleTime: options.staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: options.gcTime ?? 30 * 60 * 1000, // 30 minutes

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
 * Prefetch utility for BIA process
 * Useful for hover states, optimistic navigation
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/bia/${process.id}`}
 *   onMouseEnter={() => prefetchBIAProcess(queryClient, { id: process.id, tenant_id })}
 * >
 * ```
 */
export function prefetchBIAProcess(
  queryClient: any,
  params: UseBIAProcessParams
) {
  return queryClient.prefetchQuery({
    queryKey: ['bia', 'process', params.id, params.tenant_id],
    queryFn: () => biaAPI.getProcess(params.id, params.tenant_id),
    staleTime: 10 * 60 * 1000,
  });
}
