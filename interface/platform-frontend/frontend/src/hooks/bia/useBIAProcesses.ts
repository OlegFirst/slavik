/**
 * useBIAProcesses Hook
 * React Query hook for listing BIA processes with filters
 * Real API integration via biaAPI.listProcesses
 */

import { useQuery } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import { CriticalityLevel, ProcessStatus } from '@/types/bia';
import type { BIAProcess } from '@/types/bia';

export interface UseBIAProcessesParams {
  tenant_id: string;
  criticality?: CriticalityLevel;
  status?: ProcessStatus;
}

export interface UseBIAProcessesOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch and cache BIA processes list
 *
 * @param params - Filter parameters (tenant_id, criticality, status)
 * @param options - React Query options
 * @returns Query result with processes data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: processes, isLoading, error } = useBIAProcesses({
 *   tenant_id: 'org-123',
 *   criticality: CriticalityLevel.CRITICAL,
 *   status: ProcessStatus.COMPLETED
 * });
 * ```
 */
export function useBIAProcesses(
  params: UseBIAProcessesParams,
  options: UseBIAProcessesOptions = {}
) {
  return useQuery({
    queryKey: ['bia', 'processes', params],
    queryFn: () => biaAPI.listProcesses(params),

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
 * Hook variant for critical processes only
 */
export function useCriticalProcesses(
  tenant_id: string,
  options: UseBIAProcessesOptions = {}
) {
  return useBIAProcesses(
    {
      tenant_id,
      criticality: CriticalityLevel.CRITICAL,
    },
    options
  );
}

/**
 * Hook variant for completed processes only
 */
export function useCompletedProcesses(
  tenant_id: string,
  options: UseBIAProcessesOptions = {}
) {
  return useBIAProcesses(
    {
      tenant_id,
      status: ProcessStatus.COMPLETED,
    },
    options
  );
}

/**
 * Hook variant for draft processes only
 */
export function useDraftProcesses(
  tenant_id: string,
  options: UseBIAProcessesOptions = {}
) {
  return useBIAProcesses(
    {
      tenant_id,
      status: ProcessStatus.DRAFT,
    },
    options
  );
}
