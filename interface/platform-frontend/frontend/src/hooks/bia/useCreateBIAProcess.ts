/**
 * useCreateBIAProcess Hook
 * React Query mutation hook for creating BIA processes
 * Real API integration via biaAPI.createProcess
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import type { BIAProcess, BIAProcessCreate } from '@/types/bia';

export interface UseCreateBIAProcessOptions {
  onSuccess?: (data: BIAProcess) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

/**
 * Hook to create new BIA process
 * Automatically invalidates process list cache on success
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createProcess = useCreateBIAProcess({
 *   onSuccess: (process) => {
 *     toast.success(`Process "${process.name}" created`);
 *     router.push(`/bia/${process.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create process: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * createProcess.mutate({
 *   tenant_id: 'org-123',
 *   name: 'Patient Admission',
 *   criticality: CriticalityLevel.CRITICAL,
 *   rto_hours: 4,
 *   rpo_hours: 1,
 *   mtpd_hours: 8,
 *   // ... other fields
 * });
 * ```
 */
export function useCreateBIAProcess(options: UseCreateBIAProcessOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BIAProcessCreate) => biaAPI.createProcess(data),

    onSuccess: (data) => {
      // Invalidate process lists to refetch with new process
      queryClient.invalidateQueries({
        queryKey: ['bia', 'processes'],
      });

      // Invalidate summary report
      queryClient.invalidateQueries({
        queryKey: ['bia', 'summary', data.tenant_id],
      });

      // Optimistically set the single process cache
      queryClient.setQueryData(
        ['bia', 'process', data.id, data.tenant_id],
        data
      );

      // Call user callback
      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Call user callback
      options.onError?.(error);
    },

    onSettled: () => {
      // Call user callback
      options.onSettled?.();
    },
  });
}

/**
 * Hook for bulk creating BIA processes
 *
 * @example
 * ```tsx
 * const bulkCreate = useBulkCreateBIAProcesses({
 *   onSuccess: (report) => {
 *     toast.success(`Created ${report.success_count}/${report.total_count} processes`);
 *   }
 * });
 *
 * bulkCreate.mutate({
 *   processes: [process1, process2, process3],
 *   max_concurrency: 10
 * });
 * ```
 */
export function useBulkCreateBIAProcesses(
  options: UseCreateBIAProcessOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      processes,
      max_concurrency = 10,
    }: {
      processes: BIAProcessCreate[];
      max_concurrency?: number;
    }) => biaAPI.bulkCreateProcesses(processes, max_concurrency),

    onSuccess: (data, variables) => {
      // Invalidate all process lists
      queryClient.invalidateQueries({
        queryKey: ['bia', 'processes'],
      });

      // Invalidate summary for the tenant
      const tenant_id = variables.processes[0]?.tenant_id;
      if (tenant_id) {
        queryClient.invalidateQueries({
          queryKey: ['bia', 'summary', tenant_id],
        });
      }

      // Call user callback
      options.onSuccess?.(data as any);
    },

    onError: options.onError,
    onSettled: options.onSettled,
  });
}
