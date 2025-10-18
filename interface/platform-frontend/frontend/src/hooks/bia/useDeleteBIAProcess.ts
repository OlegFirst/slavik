/**
 * useDeleteBIAProcess Hook
 * React Query mutation hook for deleting BIA processes
 * Real API integration via biaAPI.deleteProcess
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import type { BIAProcess } from '@/types/bia';

export interface UseDeleteBIAProcessOptions {
  onSuccess?: (processId: number) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface DeleteBIAProcessParams {
  id: number;
  tenant_id: string;
}

/**
 * Hook to delete BIA process
 * Automatically invalidates caches and removes from cache on success
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteProcess = useDeleteBIAProcess({
 *   onSuccess: (processId) => {
 *     toast.success('Process deleted successfully');
 *     router.push('/bia');
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to delete: ${error.message}`);
 *   }
 * });
 *
 * // In delete confirmation
 * deleteProcess.mutate({
 *   id: 123,
 *   tenant_id: 'org-123'
 * });
 * ```
 */
export function useDeleteBIAProcess(options: UseDeleteBIAProcessOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, tenant_id }: DeleteBIAProcessParams) =>
      biaAPI.deleteProcess(id, tenant_id),

    onMutate: async ({ id, tenant_id }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: ['bia', 'process', id, tenant_id],
      });

      await queryClient.cancelQueries({
        queryKey: ['bia', 'processes'],
      });

      // Snapshot for rollback
      const previousProcess = queryClient.getQueryData<BIAProcess>([
        'bia',
        'process',
        id,
        tenant_id,
      ]);

      const previousProcesses = queryClient.getQueriesData<BIAProcess[]>({
        queryKey: ['bia', 'processes'],
      });

      // Optimistically remove from list cache
      queryClient.setQueriesData<BIAProcess[]>(
        { queryKey: ['bia', 'processes'] },
        (old) => {
          if (!old) return old;
          return old.filter((p) => p.id !== id);
        }
      );

      // Optimistically remove single process cache
      queryClient.removeQueries({
        queryKey: ['bia', 'process', id, tenant_id],
      });

      return { previousProcess, previousProcesses };
    },

    onSuccess: (data, variables) => {
      // Invalidate all process lists
      queryClient.invalidateQueries({
        queryKey: ['bia', 'processes'],
      });

      // Remove single process cache permanently
      queryClient.removeQueries({
        queryKey: ['bia', 'process', variables.id, variables.tenant_id],
      });

      // Invalidate summary
      queryClient.invalidateQueries({
        queryKey: ['bia', 'summary', variables.tenant_id],
      });

      options.onSuccess?.(variables.id);
    },

    onError: (error: Error, variables, context) => {
      // Rollback optimistic updates
      if (context?.previousProcess) {
        queryClient.setQueryData(
          ['bia', 'process', variables.id, variables.tenant_id],
          context.previousProcess
        );
      }

      if (context?.previousProcesses) {
        context.previousProcesses.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

/**
 * Hook for bulk deleting BIA processes
 *
 * @example
 * ```tsx
 * const bulkDelete = useBulkDeleteBIAProcesses({
 *   onSuccess: (report) => {
 *     toast.success(`Deleted ${report.success_count}/${report.total_count} processes`);
 *   }
 * });
 *
 * bulkDelete.mutate({
 *   tenant_id: 'org-123',
 *   process_ids: [1, 2, 3, 4, 5]
 * });
 * ```
 */
export function useBulkDeleteBIAProcesses(
  options: UseDeleteBIAProcessOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      tenant_id,
      process_ids,
      max_concurrency = 10,
    }: {
      tenant_id: string;
      process_ids: number[];
      max_concurrency?: number;
    }) => biaAPI.bulkDeleteProcesses(process_ids, tenant_id, max_concurrency),

    onMutate: async ({ process_ids }) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({
        queryKey: ['bia'],
      });

      // Snapshot for rollback
      const previousProcesses = queryClient.getQueriesData<BIAProcess[]>({
        queryKey: ['bia', 'processes'],
      });

      // Optimistically remove from lists
      queryClient.setQueriesData<BIAProcess[]>(
        { queryKey: ['bia', 'processes'] },
        (old) => {
          if (!old) return old;
          return old.filter((p) => !process_ids.includes(p.id!));
        }
      );

      return { previousProcesses };
    },

    onSuccess: (data, variables) => {
      // Invalidate all queries
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

    onError: (error: Error, _variables, context) => {
      // Rollback
      if (context?.previousProcesses) {
        context.previousProcesses.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      options.onError?.(error);
    },

    onSettled: options.onSettled,
  });
}
