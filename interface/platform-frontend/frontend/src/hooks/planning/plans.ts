/**
 * Planning Module - Plan CRUD Hooks
 * React Query hooks for Business Continuity Plan management
 *
 * Created: 2025-10-21
 * Agent: 4/6 (Planning Module Round 2)
 *
 * Total Hooks: 10 (3 query + 7 mutation)
 * - Query: usePlans, usePlan, usePlanVersionHistory
 * - Mutation: useCreatePlan, useUpdatePlan, useDeletePlan, useApprovePlan,
 *             useActivatePlan, useArchivePlan, useClonePlan
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createBCPlan,
  listBCPlans,
  getBCPlan,
  updateBCPlan,
  deleteBCPlan,
  approveBCPlan,
  activateBCPlan,
  archiveBCPlan,
  getBCPlanVersionHistory,
  cloneBCPlan,
} from '@/lib/api/planning-client';
import type {
  BCPlan,
  BCPlanCreate,
  BCPlanUpdate,
  PlanType,
  ListBCPlansResponse,
  PlanVersion,
} from '@/lib/api/planning-client';
import { PlanStatus } from '@/lib/api/planning-client';

// ============================================================================
// QUERY KEY FACTORY
// ============================================================================

/**
 * Query key factory for BC plans
 * Provides centralized, type-safe query key management
 */
export const planQueryKeys = {
  all: ['plans'] as const,
  lists: () => [...planQueryKeys.all, 'list'] as const,
  list: (params: UsePlansParams) => [...planQueryKeys.lists(), params] as const,
  details: () => [...planQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...planQueryKeys.details(), id] as const,
  versions: (id: string) => [...planQueryKeys.detail(id), 'versions'] as const,
};

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

/**
 * Parameters for listing BC plans with filters
 */
export interface UsePlansParams {
  organization_id: string;
  plan_type?: PlanType;
  status?: PlanStatus;
  process_id?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Options for usePlans hook
 */
export interface UsePlansOptions {
  enabled?: boolean;
  onSuccess?: (data: ListBCPlansResponse) => void;
  onError?: (error: Error) => void;
}

/**
 * Parameters for fetching a single BC plan
 */
export interface UsePlanParams {
  planId: string;
  enabled?: boolean;
}

/**
 * Options for usePlan hook
 */
export interface UsePlanOptions {
  enabled?: boolean;
  onSuccess?: (data: BCPlan) => void;
  onError?: (error: Error) => void;
}

/**
 * Options for plan version history hook
 */
export interface UsePlanVersionHistoryOptions {
  enabled?: boolean;
  onSuccess?: (data: PlanVersion[]) => void;
  onError?: (error: Error) => void;
}

/**
 * Options for plan creation/update mutations
 */
export interface UseCreatePlanOptions {
  onSuccess?: (plan: BCPlan) => void;
  onError?: (error: Error) => void;
}

/**
 * Options for plan deletion mutation
 */
export interface UseDeletePlanOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Parameters for updating a BC plan
 */
export interface UpdatePlanParams {
  planId: string;
  data: BCPlanUpdate;
}

/**
 * Parameters for approving a BC plan
 */
export interface ApprovePlanParams {
  planId: string;
  approvedBy: string;
}

/**
 * Parameters for cloning a BC plan
 */
export interface ClonePlanParams {
  planId: string;
  newPlanName: string;
}

// ============================================================================
// QUERY HOOKS (Read Operations)
// ============================================================================

/**
 * Hook: usePlans
 * Fetch list of BC plans with filtering, sorting, and pagination
 *
 * @param params - Filter parameters including organization_id, plan_type, status, etc.
 * @returns Query result with BC plans list
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = usePlans({
 *   organization_id: 'org-123',
 *   status: PlanStatus.ACTIVE,
 *   page: 1,
 *   limit: 20,
 * });
 * ```
 */
export function usePlans(params: UsePlansParams) {
  const { enabled = true, ...queryParams } = params;

  return useQuery({
    queryKey: planQueryKeys.list(queryParams),
    queryFn: () => listBCPlans(queryParams),
    enabled: enabled && !!queryParams.organization_id,
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook: usePlan
 * Fetch a single BC plan by ID
 *
 * @param params - Plan ID and enabled flag
 * @returns Query result with single BC plan
 *
 * @example
 * ```tsx
 * const { data: plan, isLoading } = usePlan({
 *   planId: 'plan-123',
 *   enabled: true,
 * });
 * ```
 */
export function usePlan({ planId, enabled = true }: UsePlanParams) {
  return useQuery({
    queryKey: planQueryKeys.detail(planId),
    queryFn: () => getBCPlan(planId),
    enabled: enabled && !!planId,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook: usePlanVersionHistory
 * Fetch version history for a BC plan
 *
 * @param planId - Plan ID
 * @param options - Query options
 * @returns Query result with version history array
 *
 * @example
 * ```tsx
 * const { data: versions, isLoading } = usePlanVersionHistory('plan-123', {
 *   enabled: true,
 *   onSuccess: (data) => console.log('Loaded versions:', data.length),
 * });
 * ```
 */
export function usePlanVersionHistory(
  planId: string,
  options?: UsePlanVersionHistoryOptions
) {
  const query = useQuery({
    queryKey: planQueryKeys.versions(planId),
    queryFn: () => getBCPlanVersionHistory(planId),
    enabled: options?.enabled !== false && !!planId,
    staleTime: 120000, // 2 minutes (version history changes infrequently)
  });

  // Handle callbacks manually since onSuccess/onError were removed in v5
  if (query.isSuccess && options?.onSuccess) {
    options.onSuccess(query.data);
  }
  if (query.isError && options?.onError) {
    options.onError(query.error);
  }

  return query;
}

// ============================================================================
// MUTATION HOOKS (Write Operations)
// ============================================================================

/**
 * Hook: useCreatePlan
 * Create a new BC plan
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for creating BC plans
 *
 * @example
 * ```tsx
 * const createPlan = useCreatePlan({
 *   onSuccess: (plan) => {
 *     toast.success(`Plan "${plan.plan_name}" created successfully`);
 *     router.push(`/planning/plans/${plan.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create plan: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * createPlan.mutate({
 *   organization_id: 'org-123',
 *   plan_name: 'IT Disaster Recovery Plan',
 *   plan_type: PlanType.DRP,
 *   description: 'Comprehensive IT recovery strategy',
 *   scope: 'All IT systems and infrastructure',
 *   objectives: ['Restore critical systems within 4 hours'],
 * });
 * ```
 */
export function useCreatePlan(options?: UseCreatePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BCPlanCreate) => createBCPlan(data),
    onSuccess: (data) => {
      // Invalidate all plan lists to ensure data consistency
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Set the new plan in cache
      queryClient.setQueryData(planQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useUpdatePlan
 * Update an existing BC plan
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for updating BC plans
 *
 * @example
 * ```tsx
 * const updatePlan = useUpdatePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Plan updated successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Update failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * updatePlan.mutate({
 *   planId: 'plan-123',
 *   data: {
 *     plan_name: 'Updated Plan Name',
 *     status: PlanStatus.REVIEW,
 *   },
 * });
 * ```
 */
export function useUpdatePlan(options?: UseCreatePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ planId, data }: UpdatePlanParams) => updateBCPlan(planId, data),
    onSuccess: (data) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Invalidate specific plan detail
      queryClient.invalidateQueries({ queryKey: planQueryKeys.detail(data.id!) });

      // Update the cache with new data
      queryClient.setQueryData(planQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useDeletePlan
 * Delete a BC plan (soft delete)
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for deleting BC plans
 *
 * @example
 * ```tsx
 * const deletePlan = useDeletePlan({
 *   onSuccess: () => {
 *     toast.success('Plan deleted successfully');
 *     router.push('/planning/plans');
 *   },
 *   onError: (error) => {
 *     toast.error(`Delete failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * deletePlan.mutate('plan-123');
 * ```
 */
export function useDeletePlan(options?: UseDeletePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (planId: string) => deleteBCPlan(planId),
    onSuccess: (_, planId) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Remove the deleted plan from cache
      queryClient.removeQueries({ queryKey: planQueryKeys.detail(planId) });

      options?.onSuccess?.();
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useApprovePlan
 * Approve a BC plan and change status to approved
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for approving BC plans
 *
 * @example
 * ```tsx
 * const approvePlan = useApprovePlan({
 *   onSuccess: (plan) => {
 *     toast.success(`Plan approved by ${plan.approved_by}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Approval failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * approvePlan.mutate({
 *   planId: 'plan-123',
 *   approvedBy: 'user-456',
 * });
 * ```
 */
export function useApprovePlan(options?: UseCreatePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ planId, approvedBy }: ApprovePlanParams) =>
      approveBCPlan(planId, approvedBy),
    onSuccess: (data) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Invalidate specific plan detail
      queryClient.invalidateQueries({ queryKey: planQueryKeys.detail(data.id!) });

      // Invalidate version history to show approval as new version
      queryClient.invalidateQueries({ queryKey: planQueryKeys.versions(data.id!) });

      // Update the cache with new data
      queryClient.setQueryData(planQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useActivatePlan
 * Activate a BC plan and change status to active
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for activating BC plans
 *
 * @example
 * ```tsx
 * const activatePlan = useActivatePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Plan is now active');
 *   },
 *   onError: (error) => {
 *     toast.error(`Activation failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * activatePlan.mutate('plan-123');
 * ```
 */
export function useActivatePlan(options?: UseCreatePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (planId: string) => activateBCPlan(planId),
    onSuccess: (data) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Invalidate specific plan detail
      queryClient.invalidateQueries({ queryKey: planQueryKeys.detail(data.id!) });

      // Update the cache with new data
      queryClient.setQueryData(planQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useArchivePlan
 * Archive a BC plan and change status to archived
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for archiving BC plans
 *
 * @example
 * ```tsx
 * const archivePlan = useArchivePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Plan archived successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Archive failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * archivePlan.mutate('plan-123');
 * ```
 */
export function useArchivePlan(options?: UseCreatePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (planId: string) => archiveBCPlan(planId),
    onSuccess: (data) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Invalidate specific plan detail
      queryClient.invalidateQueries({ queryKey: planQueryKeys.detail(data.id!) });

      // Update the cache with new data
      queryClient.setQueryData(planQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useClonePlan
 * Clone an existing BC plan with a new name
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for cloning BC plans
 *
 * @example
 * ```tsx
 * const clonePlan = useClonePlan({
 *   onSuccess: (newPlan) => {
 *     toast.success(`Plan cloned as "${newPlan.plan_name}"`);
 *     router.push(`/planning/plans/${newPlan.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Clone failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * clonePlan.mutate({
 *   planId: 'plan-123',
 *   newPlanName: 'Q2 2025 IT Recovery Plan',
 * });
 * ```
 */
export function useClonePlan(options?: UseCreatePlanOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ planId, newPlanName }: ClonePlanParams) =>
      cloneBCPlan(planId, newPlanName),
    onSuccess: (data) => {
      // Invalidate all plan lists to show the new cloned plan
      queryClient.invalidateQueries({ queryKey: planQueryKeys.lists() });

      // Set the new plan in cache
      queryClient.setQueryData(planQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

// ============================================================================
// UTILITY HOOKS
// ============================================================================

/**
 * Hook: usePrefetchPlan
 * Prefetch a plan for improved performance (hover states, navigation)
 *
 * @example
 * ```tsx
 * const prefetchPlan = usePrefetchPlan();
 *
 * <div onMouseEnter={() => prefetchPlan('plan-123')}>
 *   View Plan
 * </div>
 * ```
 */
export function usePrefetchPlan() {
  const queryClient = useQueryClient();

  return (planId: string) => {
    queryClient.prefetchQuery({
      queryKey: planQueryKeys.detail(planId),
      queryFn: () => getBCPlan(planId),
      staleTime: 60000,
    });
  };
}

/**
 * Hook: useIsPlanCached
 * Check if a plan is already in cache
 *
 * @param planId - Plan ID to check
 * @returns Boolean indicating if plan is cached
 *
 * @example
 * ```tsx
 * const isCached = useIsPlanCached('plan-123');
 * if (!isCached) {
 *   // Show loading indicator
 * }
 * ```
 */
export function useIsPlanCached(planId: string): boolean {
  const queryClient = useQueryClient();
  const data = queryClient.getQueryData(planQueryKeys.detail(planId));
  return !!data;
}

/**
 * Hook: useCachedPlan
 * Get cached plan data without triggering a fetch
 *
 * @param planId - Plan ID to retrieve from cache
 * @returns Cached plan data or undefined
 *
 * @example
 * ```tsx
 * const cachedPlan = useCachedPlan('plan-123');
 * if (cachedPlan) {
 *   // Use cached data for optimistic UI
 * }
 * ```
 */
export function useCachedPlan(planId: string): BCPlan | undefined {
  const queryClient = useQueryClient();
  return queryClient.getQueryData<BCPlan>(planQueryKeys.detail(planId));
}

/**
 * Hook: usePlanRequired
 * Fetch plan with assertion that planId exists (throws if planId is invalid)
 * Useful when planId comes from URL params that are validated by router
 *
 * @param planId - Plan ID (must be truthy)
 * @returns Query result with single BC plan
 *
 * @example
 * ```tsx
 * // In a page component where planId is from validated route params
 * const { data: plan } = usePlanRequired(params.planId);
 * // TypeScript knows plan will be loaded or query is loading/errored
 * ```
 */
export function usePlanRequired(planId: string) {
  if (!planId) {
    throw new Error('usePlanRequired: planId is required');
  }

  return usePlan({ planId, enabled: true });
}

// ============================================================================
// ADVANCED QUERY HOOKS (Filtered/Specialized)
// ============================================================================

/**
 * Hook: useActivePlans
 * Fetch only active BC plans
 *
 * @param organizationId - Organization ID
 * @returns Query result with active plans
 *
 * @example
 * ```tsx
 * const { data } = useActivePlans('org-123');
 * const activePlans = data?.plans || [];
 * ```
 */
export function useActivePlans(organizationId: string) {
  return usePlans({
    organization_id: organizationId,
    status: PlanStatus.ACTIVE,
  });
}

/**
 * Hook: useDraftPlans
 * Fetch only draft BC plans
 *
 * @param organizationId - Organization ID
 * @returns Query result with draft plans
 *
 * @example
 * ```tsx
 * const { data } = useDraftPlans('org-123');
 * const draftPlans = data?.plans || [];
 * ```
 */
export function useDraftPlans(organizationId: string) {
  return usePlans({
    organization_id: organizationId,
    status: PlanStatus.DRAFT,
  });
}

/**
 * Hook: usePlansByType
 * Fetch BC plans filtered by plan type
 *
 * @param organizationId - Organization ID
 * @param planType - Plan type to filter by
 * @returns Query result with filtered plans
 *
 * @example
 * ```tsx
 * const { data } = usePlansByType('org-123', PlanType.DRP);
 * const drpPlans = data?.plans || [];
 * ```
 */
export function usePlansByType(organizationId: string, planType: PlanType) {
  return usePlans({
    organization_id: organizationId,
    plan_type: planType,
  });
}

/**
 * Hook: usePlansByProcess
 * Fetch BC plans related to a specific process
 *
 * @param organizationId - Organization ID
 * @param processId - Process ID to filter by
 * @returns Query result with process-related plans
 *
 * @example
 * ```tsx
 * const { data } = usePlansByProcess('org-123', 'process-456');
 * const processPlans = data?.plans || [];
 * ```
 */
export function usePlansByProcess(organizationId: string, processId: string) {
  return usePlans({
    organization_id: organizationId,
    process_id: processId,
  });
}

// ============================================================================
// EXPORTS
// ============================================================================

export type { ListBCPlansResponse, PlanVersion };
