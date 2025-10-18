/**
 * useUpdateBIAProcess Hook
 * React Query mutation hook for updating BIA processes
 * Real API integration via biaAPI.updateProcess
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import type { BIAProcess } from '@/types/bia';

export interface UseUpdateBIAProcessOptions {
  onSuccess?: (data: BIAProcess) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UpdateBIAProcessParams {
  id: number;
  tenant_id: string;
  updates: Partial<BIAProcess>;
}

/**
 * Hook to update existing BIA process
 * Automatically invalidates caches on success
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateProcess = useUpdateBIAProcess({
 *   onSuccess: (process) => {
 *     toast.success(`Process "${process.name}" updated`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to update: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * updateProcess.mutate({
 *   id: 123,
 *   tenant_id: 'org-123',
 *   updates: {
 *     rto_hours: 2,
 *     ai_recommendations: 'New AI insights...'
 *   }
 * });
 * ```
 */
export function useUpdateBIAProcess(options: UseUpdateBIAProcessOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, tenant_id, updates }: UpdateBIAProcessParams) =>
      biaAPI.updateProcess(id, tenant_id, updates),

    onMutate: async ({ id, tenant_id, updates }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: ['bia', 'process', id, tenant_id],
      });

      // Snapshot previous value for rollback
      const previousProcess = queryClient.getQueryData<BIAProcess>([
        'bia',
        'process',
        id,
        tenant_id,
      ]);

      // Optimistically update cache
      if (previousProcess) {
        queryClient.setQueryData<BIAProcess>(
          ['bia', 'process', id, tenant_id],
          {
            ...previousProcess,
            ...updates,
            updated_at: new Date().toISOString(),
          }
        );
      }

      return { previousProcess };
    },

    onSuccess: (data) => {
      // Update the single process cache with real server data
      queryClient.setQueryData(
        ['bia', 'process', data.id, data.tenant_id],
        data
      );

      // Invalidate process lists (might affect filtering)
      queryClient.invalidateQueries({
        queryKey: ['bia', 'processes'],
      });

      // Invalidate summary report
      queryClient.invalidateQueries({
        queryKey: ['bia', 'summary', data.tenant_id],
      });

      options.onSuccess?.(data);
    },

    onError: (error: Error, variables, context) => {
      // Rollback on error
      if (context?.previousProcess) {
        queryClient.setQueryData(
          ['bia', 'process', variables.id, variables.tenant_id],
          context.previousProcess
        );
      }

      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

/**
 * Hook to mark BIA process as completed
 *
 * @example
 * ```tsx
 * const completeProcess = useCompleteBIAProcess({
 *   onSuccess: (result) => {
 *     toast.success('BIA process completed!');
 *   }
 * });
 *
 * completeProcess.mutate({
 *   id: 123,
 *   tenant_id: 'org-123'
 * });
 * ```
 */
export function useCompleteBIAProcess(
  options: UseUpdateBIAProcessOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, tenant_id }: { id: number; tenant_id: string }) =>
      biaAPI.completeProcess(id, tenant_id),

    onSuccess: (data) => {
      // Update cache with completed process
      queryClient.setQueryData(
        ['bia', 'process', data.process.id, data.process.tenant_id],
        data.process
      );

      // Invalidate lists
      queryClient.invalidateQueries({
        queryKey: ['bia', 'processes'],
      });

      // Invalidate summary
      queryClient.invalidateQueries({
        queryKey: ['bia', 'summary', data.process.tenant_id],
      });

      options.onSuccess?.(data.process);
    },

    onError: options.onError,
    onSettled: options.onSettled,
  });
}

/**
 * Hook for bulk updating BIA processes
 *
 * @example
 * ```tsx
 * const bulkUpdate = useBulkUpdateBIAProcesses({
 *   onSuccess: (report) => {
 *     toast.success(`Updated ${report.success_count}/${report.total_count} processes`);
 *   }
 * });
 *
 * bulkUpdate.mutate({
 *   tenant_id: 'org-123',
 *   updates: [
 *     { process_id: 1, rto_hours: 4 },
 *     { process_id: 2, rto_hours: 8 }
 *   ]
 * });
 * ```
 */
export function useBulkUpdateBIAProcesses(
  options: UseUpdateBIAProcessOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      tenant_id,
      updates,
      max_concurrency = 10,
    }: {
      tenant_id: string;
      updates: Array<{ process_id: number; [key: string]: any }>;
      max_concurrency?: number;
    }) => biaAPI.bulkUpdateProcesses(updates, tenant_id, max_concurrency),

    onSuccess: (data, variables) => {
      // Invalidate all process queries
      queryClient.invalidateQueries({
        queryKey: ['bia', 'processes'],
      });

      queryClient.invalidateQueries({
        queryKey: ['bia', 'process'],
      });

      queryClient.invalidateQueries({
        queryKey: ['bia', 'summary', variables.tenant_id],
      });

      options.onSuccess?.(data as any);
    },

    onError: options.onError,
    onSettled: options.onSettled,
  });
}
