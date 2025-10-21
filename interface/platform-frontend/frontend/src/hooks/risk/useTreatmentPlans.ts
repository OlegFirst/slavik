/**
 * useTreatmentPlans Hook
 * React Query hooks for risk treatment plan management
 * Real API integration via riskClient
 * Week 5 - Risk Assessment Module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type {
  RiskTreatmentPlan,
  TreatmentPlanCreate,
  TreatmentPlanUpdate,
} from '@/types/risk';
import toast from 'react-hot-toast';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for treatment plans
 * Provides centralized query key management
 */
export const treatmentKeys = {
  all: ['treatmentPlans'] as const,
  byRisk: (riskId: string) => [...treatmentKeys.all, 'risk', riskId] as const,
  detail: (planId: string) => [...treatmentKeys.all, 'detail', planId] as const,
};

// ==================== TYPES ====================

/**
 * Options for useTreatmentPlans query hook
 */
export interface UseTreatmentPlansOptions {
  riskId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Options for useCreateTreatmentPlan mutation hook
 */
export interface UseCreateTreatmentPlanOptions {
  onSuccess?: (data: RiskTreatmentPlan) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

/**
 * Options for useUpdateTreatmentPlan mutation hook
 */
export interface UseUpdateTreatmentPlanOptions {
  onSuccess?: (data: RiskTreatmentPlan) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

/**
 * Options for useDeleteTreatmentPlan mutation hook
 */
export interface UseDeleteTreatmentPlanOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

/**
 * Parameters for updateTreatmentPlan mutation
 */
export interface UpdateTreatmentPlanParams {
  planId: string;
  data: TreatmentPlanUpdate;
}

// ==================== HOOKS ====================

/**
 * Hook to fetch treatment plans for a specific risk
 * Retrieves all treatment plans associated with a risk
 *
 * @param options - Query options including riskId
 * @returns Query result with treatment plans array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: plans, isLoading, error } = useTreatmentPlans({
 *   riskId: 'risk-123',
 *   enabled: true,
 * });
 *
 * if (plans) {
 *   plans.forEach(plan => {
 *     console.log('Strategy:', plan.strategy);
 *     console.log('Status:', plan.status);
 *     console.log('Actions:', plan.actions);
 *     console.log('Cost:', plan.estimated_cost);
 *   });
 * }
 * ```
 */
export function useTreatmentPlans({
  riskId,
  enabled = true,
  staleTime,
  gcTime,
  refetchOnWindowFocus,
}: UseTreatmentPlansOptions) {
  return useQuery({
    queryKey: treatmentKeys.byRisk(riskId),
    queryFn: () => riskClient.getTreatmentPlans(riskId),

    // Enable/disable query
    enabled: enabled && !!riskId,

    // Caching strategy - treatment plans change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Control refetching
    refetchOnWindowFocus: refetchOnWindowFocus ?? true,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to create a new treatment plan for a risk
 * Defines mitigation strategy and action items
 *
 * @param riskId - Risk ID to create treatment plan for
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createPlan = useCreateTreatmentPlan('risk-123', {
 *   onSuccess: (plan) => {
 *     toast.success(`Treatment plan created: ${plan.strategy}`);
 *     console.log('Plan ID:', plan.id);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create plan: ${error.message}`);
 *   },
 * });
 *
 * // Create treatment plan
 * createPlan.mutate({
 *   strategy: 'mitigate',
 *   description: 'Implement security controls to reduce likelihood',
 *   actions: [
 *     {
 *       action: 'Install firewall',
 *       responsible: 'IT Security Team',
 *       deadline: '2024-12-31',
 *       status: 'planned',
 *     },
 *     {
 *       action: 'Conduct security training',
 *       responsible: 'HR Department',
 *       deadline: '2024-11-30',
 *       status: 'planned',
 *     },
 *   ],
 *   responsible_party: 'John Doe',
 *   start_date: '2024-10-01',
 *   target_date: '2024-12-31',
 *   estimated_cost: 50000,
 *   expected_residual_likelihood: 2,
 *   expected_residual_impact: 3,
 * });
 * ```
 */
export function useCreateTreatmentPlan(
  riskId: string,
  options: UseCreateTreatmentPlanOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TreatmentPlanCreate) =>
      riskClient.createTreatmentPlan(riskId, data),

    onSuccess: (data) => {
      // Invalidate treatment plans list for this risk
      queryClient.invalidateQueries({
        queryKey: treatmentKeys.byRisk(riskId),
      });

      // Invalidate risk detail (may include treatment info)
      queryClient.invalidateQueries({
        queryKey: ['risks', riskId],
      });

      // Show success notification
      toast.success('Treatment plan created successfully');

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to create treatment plan: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}

/**
 * Hook to update an existing treatment plan
 * Supports partial updates of plan properties
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updatePlan = useUpdateTreatmentPlan({
 *   onSuccess: (plan) => {
 *     toast.success('Treatment plan updated');
 *     console.log('Updated status:', plan.status);
 *   },
 *   onError: (error) => {
 *     toast.error(`Update failed: ${error.message}`);
 *   },
 * });
 *
 * // Update treatment plan status and completion date
 * updatePlan.mutate({
 *   planId: 'plan-456',
 *   data: {
 *     status: 'completed',
 *     completion_date: '2024-10-15',
 *     actual_cost: 45000,
 *   },
 * });
 * ```
 */
export function useUpdateTreatmentPlan(
  options: UseUpdateTreatmentPlanOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ planId, data }: UpdateTreatmentPlanParams) =>
      riskClient.updateTreatmentPlan(planId, data),

    onSuccess: (data) => {
      // Update plan detail cache
      if (data.id) {
        queryClient.setQueryData(treatmentKeys.detail(data.id), data);
      }

      // Invalidate treatment plans list for this risk
      queryClient.invalidateQueries({
        queryKey: treatmentKeys.byRisk(data.risk_id),
      });

      // Invalidate risk detail
      queryClient.invalidateQueries({
        queryKey: ['risks', data.risk_id],
      });

      // Show success notification
      toast.success('Treatment plan updated successfully');

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to update treatment plan: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}

/**
 * Hook to delete a treatment plan
 * Removes treatment plan from the system
 *
 * @param riskId - Risk ID associated with the treatment plan
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deletePlan = useDeleteTreatmentPlan('risk-123', {
 *   onSuccess: () => {
 *     toast.success('Treatment plan deleted');
 *   },
 *   onError: (error) => {
 *     toast.error(`Delete failed: ${error.message}`);
 *   },
 * });
 *
 * // Delete treatment plan
 * deletePlan.mutate('plan-456');
 * ```
 */
export function useDeleteTreatmentPlan(
  riskId: string,
  options: UseDeleteTreatmentPlanOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (planId: string) => riskClient.deleteTreatmentPlan(planId),

    onSuccess: (_, planId) => {
      // Remove from plan detail cache
      queryClient.removeQueries({
        queryKey: treatmentKeys.detail(planId),
      });

      // Invalidate treatment plans list for this risk
      queryClient.invalidateQueries({
        queryKey: treatmentKeys.byRisk(riskId),
      });

      // Invalidate risk detail
      queryClient.invalidateQueries({
        queryKey: ['risks', riskId],
      });

      // Show success notification
      toast.success('Treatment plan deleted successfully');

      options.onSuccess?.();
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to delete treatment plan: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}
