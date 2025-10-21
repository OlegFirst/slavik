/**
 * useUpdateRisk Hook
 * React Query mutation hook for updating risk assessments
 * Real API integration via riskClient.updateRisk
 * Week 5 - Risk Assessment Module
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { riskClient, type RiskUpdate } from '@/lib/api/risk-client';
import type { Risk } from '@/types/risk';
import { riskQueryKeys } from './useRisks';
import toast from 'react-hot-toast';

export interface UseUpdateRiskOptions {
  onSuccess?: (data: Risk) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

export interface UpdateRiskParams {
  riskId: string;
  data: RiskUpdate;
}

/**
 * Hook to update risk assessment metadata
 * Automatically invalidates risk list and detail cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateRisk = useUpdateRisk({
 *   onSuccess: (risk) => {
 *     toast.success(`Risk "${risk.risk_title}" updated`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to update risk: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * updateRisk.mutate({
 *   riskId: 'risk-123',
 *   data: {
 *     risk_title: 'Updated Data Center Risk',
 *     description: 'Updated description with new details',
 *     likelihood: RiskLikelihood.UNLIKELY,
 *     impact: RiskImpact.MAJOR,
 *     status: RiskStatus.MONITORING,
 *     // ... other fields
 *   }
 * });
 * ```
 */
export function useUpdateRisk(options: UseUpdateRiskOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<Risk, Error, UpdateRiskParams>({
    mutationFn: ({ riskId, data }: UpdateRiskParams) =>
      riskClient.updateRisk(riskId, data),

    onSuccess: (data, variables) => {
      // Invalidate risk lists to refetch with updated data
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Invalidate specific risk detail
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.detail(variables.riskId),
      });

      // Optimistically update the risk cache
      queryClient.setQueryData(
        riskQueryKeys.detail(variables.riskId),
        data
      );

      // Show success toast
      if (showToast) {
        toast.success(`Risk "${data.risk_title}" updated successfully`);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error toast
      if (showToast) {
        toast.error(`Failed to update risk: ${error.message}`);
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
 * Hook to update risk with optimistic updates
 * Immediately updates UI before server confirms
 * Rollback on error
 *
 * @example
 * ```tsx
 * const updateRiskOptimistic = useUpdateRiskOptimistic({
 *   onError: (error, variables, context) => {
 *     // Rollback happened automatically
 *     toast.error('Update failed, changes reverted');
 *   }
 * });
 *
 * // Quick UI updates with automatic rollback on failure
 * updateRiskOptimistic.mutate({
 *   riskId: 'risk-123',
 *   data: { status: RiskStatus.MONITORING }
 * });
 * ```
 */
export function useUpdateRiskOptimistic(options: UseUpdateRiskOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<Risk, Error, UpdateRiskParams, { previousRisk?: Risk }>({
    mutationFn: ({ riskId, data }: UpdateRiskParams) =>
      riskClient.updateRisk(riskId, data),

    onMutate: async ({ riskId, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: riskQueryKeys.detail(riskId),
      });

      // Snapshot previous value
      const previousRisk = queryClient.getQueryData<Risk>(
        riskQueryKeys.detail(riskId)
      );

      // Optimistically update to new value
      if (previousRisk) {
        // Recalculate scores if likelihood or impact changed
        let updatedRisk = {
          ...previousRisk,
          ...data,
          updated_at: new Date().toISOString(),
        };

        // Recalculate inherent_risk_score if likelihood or impact changed
        if (data.likelihood !== undefined || data.impact !== undefined) {
          const newLikelihood = data.likelihood ?? previousRisk.likelihood;
          const newImpact = data.impact ?? previousRisk.impact;
          updatedRisk.inherent_risk_score = newLikelihood * newImpact;
        }

        // Recalculate residual_risk_score if residual values changed
        if (data.residual_likelihood !== undefined || data.residual_impact !== undefined) {
          const newResidualLikelihood = data.residual_likelihood ?? previousRisk.residual_likelihood;
          const newResidualImpact = data.residual_impact ?? previousRisk.residual_impact;
          if (newResidualLikelihood && newResidualImpact) {
            updatedRisk.residual_risk_score = newResidualLikelihood * newResidualImpact;
          }
        }

        queryClient.setQueryData<Risk>(
          riskQueryKeys.detail(riskId),
          updatedRisk
        );
      }

      // Return context with snapshot for rollback
      return { previousRisk };
    },

    onSuccess: (data, variables) => {
      // Invalidate lists to refetch
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Update with server response (authoritative data)
      queryClient.setQueryData(
        riskQueryKeys.detail(variables.riskId),
        data
      );

      // Show success toast
      if (showToast) {
        toast.success(`Risk updated successfully`);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error, variables, context) => {
      // Rollback to previous value on error
      if (context?.previousRisk) {
        queryClient.setQueryData(
          riskQueryKeys.detail(variables.riskId),
          context.previousRisk
        );
      }

      // Show error toast
      if (showToast) {
        toast.error(`Update failed: ${error.message}`);
      }

      callbackOptions.onError?.(error);
    },

    onSettled: (data, error, variables) => {
      // Always refetch after error or success
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.detail(variables.riskId),
      });

      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook to update risk status only
 * Specialized mutation for status changes
 *
 * @example
 * ```tsx
 * const updateStatus = useUpdateRiskStatus({
 *   onSuccess: (risk) => {
 *     toast.success(`Risk status changed to ${risk.status}`);
 *   }
 * });
 *
 * updateStatus.mutate({
 *   riskId: 'risk-123',
 *   status: RiskStatus.CLOSED
 * });
 * ```
 */
export function useUpdateRiskStatus(options: UseUpdateRiskOptions = {}) {
  const updateRisk = useUpdateRiskOptimistic(options);

  return useMutation<Risk, Error, { riskId: string; status: string }>({
    mutationFn: ({ riskId, status }: { riskId: string; status: string }) =>
      updateRisk.mutateAsync({
        riskId,
        data: { status: status as any },
      }),

    onSuccess: options.onSuccess,
    onError: options.onError,
    onSettled: options.onSettled,
  });
}

/**
 * Hook to mark risk as reviewed
 * Updates last_reviewed_at and schedules next review
 *
 * @example
 * ```tsx
 * const markReviewed = useMarkRiskReviewed({
 *   onSuccess: (risk) => {
 *     toast.success('Risk review recorded');
 *   }
 * });
 *
 * markReviewed.mutate({
 *   riskId: 'risk-123',
 *   reviewerId: 'user-456',
 *   notes: 'Reviewed during monthly audit',
 *   nextReviewDate: '2025-11-20'
 * });
 * ```
 */
export function useMarkRiskReviewed(options: UseUpdateRiskOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<
    Risk,
    Error,
    {
      riskId: string;
      reviewerId: string;
      notes?: string;
      nextReviewDate?: string;
    }
  >({
    mutationFn: async ({
      riskId,
      reviewerId,
      notes,
      nextReviewDate,
    }: {
      riskId: string;
      reviewerId: string;
      notes?: string;
      nextReviewDate?: string;
    }) => {
      // Update risk with review data
      // Note: last_reviewed_at is typically set by the backend
      return riskClient.updateRisk(riskId, {
        next_review_date: nextReviewDate,
      });
    },

    onSuccess: (data, variables) => {
      // Invalidate lists and detail
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      queryClient.setQueryData(
        riskQueryKeys.detail(variables.riskId),
        data
      );

      // Show success toast
      if (showToast) {
        toast.success('Risk review recorded successfully');
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      if (showToast) {
        toast.error(`Failed to record review: ${error.message}`);
      }

      callbackOptions.onError?.(error);
    },

    onSettled: callbackOptions.onSettled,
  });
}
