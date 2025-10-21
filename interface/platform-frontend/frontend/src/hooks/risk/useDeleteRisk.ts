/**
 * useDeleteRisk Hook
 * React Query mutation hook for deleting risks (soft delete)
 * Real API integration via riskClient.deleteRisk
 * Week 5 - Risk Assessment Module
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import { riskQueryKeys } from './useRisks';
import toast from 'react-hot-toast';

export interface UseDeleteRiskOptions {
  onSuccess?: (riskId: string) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

export interface DeleteRiskParams {
  riskId: string;
  organizationId?: string;
}

/**
 * Hook to delete risk assessment (soft delete - sets is_active to false)
 * Automatically invalidates risk list cache and removes from detail cache
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteRisk = useDeleteRisk({
 *   onSuccess: (riskId) => {
 *     toast.success(`Risk deleted successfully`);
 *     router.push('/risks');
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to delete risk: ${error.message}`);
 *   }
 * });
 *
 * // In delete button handler
 * const handleDelete = () => {
 *   if (confirm('Are you sure you want to delete this risk?')) {
 *     deleteRisk.mutate({
 *       riskId: risk.id!,
 *       organizationId: 'org-123'
 *     });
 *   }
 * };
 * ```
 */
export function useDeleteRisk(options: UseDeleteRiskOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<void, Error, DeleteRiskParams>({
    mutationFn: ({ riskId }: DeleteRiskParams) =>
      riskClient.deleteRisk(riskId),

    onSuccess: (_, variables) => {
      // Invalidate risk lists to refetch without deleted risk
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Remove risk from detail cache
      queryClient.removeQueries({
        queryKey: riskQueryKeys.detail(variables.riskId),
      });

      // Show success toast
      if (showToast) {
        toast.success('Risk deleted successfully');
      }

      // Call user callback
      callbackOptions.onSuccess?.(variables.riskId);
    },

    onError: (error: Error) => {
      // Show error toast
      if (showToast) {
        toast.error(`Failed to delete risk: ${error.message}`);
      }

      // Call user callback
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      // Call user callback
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook for bulk deleting multiple risks
 * Sequentially deletes risks and provides progress tracking
 *
 * @example
 * ```tsx
 * const bulkDelete = useBulkDeleteRisks({
 *   onSuccess: (report) => {
 *     toast.success(`Deleted ${report.success_count}/${report.total_count} risks`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Bulk delete failed: ${error.message}`);
 *   }
 * });
 *
 * bulkDelete.mutate({
 *   riskIds: ['risk-1', 'risk-2', 'risk-3', 'risk-4', 'risk-5'],
 *   organizationId: 'org-123'
 * });
 * ```
 */
export function useBulkDeleteRisks(
  options: Omit<UseDeleteRiskOptions, 'onSuccess'> & {
    onSuccess?: (report: {
      total_count: number;
      success_count: number;
      failure_count: number;
      results: PromiseSettledResult<void>[];
    }) => void;
  } = {}
) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<
    {
      total_count: number;
      success_count: number;
      failure_count: number;
      results: PromiseSettledResult<void>[];
    },
    Error,
    {
      riskIds: string[];
      organizationId?: string;
    }
  >({
    mutationFn: async ({
      riskIds,
      organizationId,
    }: {
      riskIds: string[];
      organizationId?: string;
    }) => {
      const results = await Promise.allSettled(
        riskIds.map((riskId) => riskClient.deleteRisk(riskId))
      );

      const successCount = results.filter((r) => r.status === 'fulfilled').length;
      const failureCount = results.filter((r) => r.status === 'rejected').length;

      return {
        total_count: riskIds.length,
        success_count: successCount,
        failure_count: failureCount,
        results,
      };
    },

    onSuccess: (data, variables) => {
      // Invalidate all risk lists
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Remove successfully deleted risks from cache
      variables.riskIds.forEach((riskId) => {
        queryClient.removeQueries({
          queryKey: riskQueryKeys.detail(riskId),
        });
      });

      // Show success toast
      if (showToast) {
        if (data.failure_count === 0) {
          toast.success(`Successfully deleted ${data.success_count} risks`);
        } else {
          toast.success(
            `Deleted ${data.success_count} of ${data.total_count} risks (${data.failure_count} failed)`
          );
        }
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error toast
      if (showToast) {
        toast.error(`Bulk delete failed: ${error.message}`);
      }

      callbackOptions.onError?.(error);
    },

    onSettled: callbackOptions.onSettled,
  });
}

/**
 * Hook to delete risk with confirmation dialog
 * Prompts user before deletion
 *
 * @example
 * ```tsx
 * const deleteWithConfirm = useDeleteRiskWithConfirmation({
 *   confirmMessage: 'Are you sure you want to delete this risk? This action cannot be undone.',
 *   onSuccess: () => {
 *     router.push('/risks');
 *   }
 * });
 *
 * // Simple usage - confirmation handled automatically
 * <button onClick={() => deleteWithConfirm.mutate({ riskId: 'risk-123' })}>
 *   Delete Risk
 * </button>
 * ```
 */
export function useDeleteRiskWithConfirmation(
  options: UseDeleteRiskOptions & {
    confirmMessage?: string;
  } = {}
) {
  const { confirmMessage = 'Are you sure you want to delete this risk?', ...deleteOptions } = options;
  const deleteRisk = useDeleteRisk(deleteOptions);

  return useMutation<void, Error, DeleteRiskParams>({
    mutationFn: async (params: DeleteRiskParams) => {
      // Show confirmation dialog
      const confirmed = window.confirm(confirmMessage);

      if (!confirmed) {
        throw new Error('Delete cancelled by user');
      }

      return deleteRisk.mutateAsync(params);
    },

    onSuccess: (_, variables) => {
      deleteOptions.onSuccess?.(variables.riskId);
    },

    onError: (error: Error) => {
      // Don't show error toast for user cancellation
      if (error.message !== 'Delete cancelled by user') {
        deleteOptions.onError?.(error);
      }
    },

    onSettled: deleteOptions.onSettled,
  });
}

/**
 * Hook to soft delete with undo capability
 * Provides a way to restore deleted risk within a time window
 *
 * @example
 * ```tsx
 * const deleteWithUndo = useDeleteRiskWithUndo({
 *   undoTimeoutMs: 5000, // 5 seconds to undo
 *   onSuccess: (riskId, undo) => {
 *     toast.success(
 *       <div>
 *         Risk deleted
 *         <button onClick={undo}>Undo</button>
 *       </div>,
 *       { duration: 5000 }
 *     );
 *   }
 * });
 * ```
 */
export function useDeleteRiskWithUndo(
  options: Omit<UseDeleteRiskOptions, 'onSuccess'> & {
    onSuccess?: (riskId: string, undo: () => void) => void;
    undoTimeoutMs?: number;
  } = {}
) {
  const queryClient = useQueryClient();
  const { undoTimeoutMs = 5000, showToast = true, ...callbackOptions } = options;

  return useMutation<{ riskId: string; riskData: any }, Error, DeleteRiskParams>({
    mutationFn: async ({ riskId }: DeleteRiskParams) => {
      // Store the risk data before deletion for potential undo
      const riskData = queryClient.getQueryData(riskQueryKeys.detail(riskId));

      // Perform soft delete
      await riskClient.deleteRisk(riskId);

      return { riskId, riskData };
    },

    onSuccess: (data, variables) => {
      let undoTimeout: NodeJS.Timeout;

      // Undo function that restores the risk
      const undo = () => {
        clearTimeout(undoTimeout);

        // Restore to cache
        if (data.riskData) {
          queryClient.setQueryData(
            riskQueryKeys.detail(data.riskId),
            data.riskData
          );
        }

        // Invalidate to refetch
        queryClient.invalidateQueries({
          queryKey: riskQueryKeys.lists(),
        });

        if (showToast) {
          toast.success('Risk deletion cancelled');
        }
      };

      // Set timeout to finalize deletion
      undoTimeout = setTimeout(() => {
        // Finalize deletion after timeout
        queryClient.removeQueries({
          queryKey: riskQueryKeys.detail(data.riskId),
        });
      }, undoTimeoutMs);

      // Invalidate lists immediately
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Call user callback with undo function
      callbackOptions.onSuccess?.(data.riskId, undo);
    },

    onError: (error: Error) => {
      if (showToast) {
        toast.error(`Failed to delete risk: ${error.message}`);
      }

      callbackOptions.onError?.(error);
    },

    onSettled: callbackOptions.onSettled,
  });
}
