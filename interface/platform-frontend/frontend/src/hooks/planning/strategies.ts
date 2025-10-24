/**
 * Planning Module - Strategy & Action Hooks
 * React Query hooks for Recovery Strategies and Action Plans
 * ISO 22301:2019 Clause 8.3 - Business Continuity Strategies and Solutions
 *
 * Created: 2025-10-21
 * Agent: 5/6 (Planning Module Round 2)
 *
 * Total Hooks: 16
 * - Recovery Strategies: 8 hooks (4 query + 4 mutation)
 * - Action Plans: 8 hooks (4 query + 4 mutation)
 */

'use client';

import { useQuery, useMutation, useQueryClient, type QueryClient } from '@tanstack/react-query';
import {
  // Strategy imports
  createRecoveryStrategy,
  listRecoveryStrategies,
  getRecoveryStrategy,
  updateRecoveryStrategy,
  deleteRecoveryStrategy,
  recordStrategyTest,
  getStrategyEffectiveness,
  getStrategiesByProcess,
  // Action imports
  createActionPlan,
  listActionPlans,
  getActionPlan,
  updateActionPlan,
  deleteActionPlan,
  completeActionPlan,
  getActionsByUser,
  getOverdueActions,
  // Type imports
  type RecoveryStrategy,
  type RecoveryStrategyCreate,
  type RecoveryStrategyUpdate,
  type ActionPlan,
  type ActionPlanCreate,
  type ActionPlanUpdate,
  type StrategyTestResult,
  type StrategyEffectiveness,
} from '@/lib/api/planning-client';

// ============================================================================
// QUERY KEY FACTORIES
// ============================================================================

/**
 * Query key factory for recovery strategies
 * Provides consistent cache key generation for all strategy-related queries
 */
export const strategyQueryKeys = {
  all: ['strategies'] as const,
  lists: () => [...strategyQueryKeys.all, 'list'] as const,
  list: (planId: string) => [...strategyQueryKeys.lists(), { planId }] as const,
  details: () => [...strategyQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...strategyQueryKeys.details(), id] as const,
  effectiveness: (id: string) => [...strategyQueryKeys.detail(id), 'effectiveness'] as const,
  byProcess: (processId: string) => [...strategyQueryKeys.all, 'by-process', processId] as const,
};

/**
 * Query key factory for action plans
 * Provides consistent cache key generation for all action-related queries
 */
export const actionQueryKeys = {
  all: ['actions'] as const,
  lists: () => [...actionQueryKeys.all, 'list'] as const,
  list: (planId: string) => [...actionQueryKeys.lists(), { planId }] as const,
  details: () => [...actionQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...actionQueryKeys.details(), id] as const,
  byUser: (userId: string, organizationId: string) =>
    [...actionQueryKeys.all, 'by-user', userId, organizationId] as const,
  overdue: (organizationId: string) => [...actionQueryKeys.all, 'overdue', organizationId] as const,
};

// ============================================================================
// RECOVERY STRATEGIES - QUERY HOOKS (4 hooks)
// ============================================================================

/**
 * Hook Parameters - List Strategies
 */
export interface UseStrategiesParams {
  planId: string;
  enabled?: boolean;
}

/**
 * Hook Options - Strategies Query
 */
export interface UseStrategiesOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch recovery strategies for a plan
 *
 * @param params - Query parameters with planId
 * @returns Query result with strategies array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: strategies, isLoading } = useStrategies({
 *   planId: 'plan-123',
 *   enabled: true
 * });
 *
 * if (strategies) {
 *   console.log(`Found ${strategies.length} recovery strategies`);
 * }
 * ```
 */
export function useStrategies({ planId, enabled = true }: UseStrategiesParams) {
  return useQuery({
    queryKey: strategyQueryKeys.list(planId),
    queryFn: () => listRecoveryStrategies(planId),
    enabled: enabled && !!planId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Strategy
 */
export interface UseStrategyParams {
  strategyId: string;
  enabled?: boolean;
}

/**
 * Hook Options - Strategy Query
 */
export interface UseStrategyOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch a single recovery strategy by ID
 *
 * @param params - Query parameters with strategyId
 * @returns Query result with strategy data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: strategy, isLoading, error } = useStrategy({
 *   strategyId: 'strategy-123',
 *   enabled: true
 * });
 *
 * if (strategy) {
 *   console.log(`Strategy: ${strategy.strategy_name}`);
 *   console.log(`Type: ${strategy.strategy_type}`);
 *   console.log(`Effectiveness: ${strategy.effectiveness_rating}/5`);
 * }
 * ```
 */
export function useStrategy({ strategyId, enabled = true }: UseStrategyParams) {
  return useQuery({
    queryKey: strategyQueryKeys.detail(strategyId),
    queryFn: () => getRecoveryStrategy(strategyId),
    enabled: enabled && !!strategyId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Strategy Effectiveness
 */
export interface UseStrategyEffectivenessParams {
  strategyId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch strategy effectiveness metrics
 * Returns average rating, test count, and trend analysis
 *
 * @param params - Query parameters with strategyId
 * @returns Query result with effectiveness data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: effectiveness } = useStrategyEffectiveness({
 *   strategyId: 'strategy-123'
 * });
 *
 * if (effectiveness) {
 *   console.log(`Average Rating: ${effectiveness.average_rating}/5`);
 *   console.log(`Tests Conducted: ${effectiveness.test_count}`);
 *   console.log(`Trend: ${effectiveness.trend}`);
 * }
 * ```
 */
export function useStrategyEffectiveness({ strategyId, enabled = true }: UseStrategyEffectivenessParams) {
  return useQuery({
    queryKey: strategyQueryKeys.effectiveness(strategyId),
    queryFn: () => getStrategyEffectiveness(strategyId),
    enabled: enabled && !!strategyId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Strategies by Process
 */
export interface UseStrategiesByProcessParams {
  processId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch recovery strategies for a specific process
 * Returns all strategies related to a business process
 *
 * @param params - Query parameters with processId
 * @returns Query result with strategies array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: processStrategies } = useStrategiesByProcess({
 *   processId: 'process-123'
 * });
 *
 * if (processStrategies) {
 *   console.log(`Found ${processStrategies.length} strategies for this process`);
 *   processStrategies.forEach(s => {
 *     console.log(`- ${s.strategy_name} (${s.strategy_type})`);
 *   });
 * }
 * ```
 */
export function useStrategiesByProcess({ processId, enabled = true }: UseStrategiesByProcessParams) {
  return useQuery({
    queryKey: strategyQueryKeys.byProcess(processId),
    queryFn: () => getStrategiesByProcess(processId),
    enabled: enabled && !!processId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// RECOVERY STRATEGIES - MUTATION HOOKS (4 hooks)
// ============================================================================

/**
 * Hook Options - Create Strategy
 */
export interface UseCreateStrategyOptions {
  onSuccess?: (strategy: RecoveryStrategy) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create a new recovery strategy
 * Automatically invalidates strategy list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createStrategy = useCreateStrategy({
 *   onSuccess: (strategy) => {
 *     console.log(`Strategy "${strategy.strategy_name}" created`);
 *     router.push(`/planning/strategies/${strategy.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create strategy: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * createStrategy.mutate({
 *   plan_id: 'plan-123',
 *   strategy_name: 'Primary Data Center Recovery',
 *   strategy_type: StrategyType.RECOVERY,
 *   description: 'Recovery procedures for primary data center failure',
 *   rto_target: 240, // 4 hours
 *   rpo_target: 60,  // 1 hour
 *   resource_requirements: {
 *     personnel: ['IT Manager', 'System Administrator'],
 *     facilities: ['Backup Data Center'],
 *     technology: ['Replication Software', 'VPN Access']
 *   },
 *   estimated_cost: 50000,
 *   dependencies: ['network-connectivity', 'power-supply'],
 *   testing_schedule: 'Quarterly'
 * });
 * ```
 */
export function useCreateStrategy(options: UseCreateStrategyOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<RecoveryStrategy, Error, RecoveryStrategyCreate>({
    mutationFn: (data: RecoveryStrategyCreate) => createRecoveryStrategy(data),

    onSuccess: (data) => {
      // Invalidate strategy lists to refetch with new strategy
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.lists(),
      });

      // Invalidate parent plan queries
      queryClient.invalidateQueries({
        queryKey: ['plans', data.plan_id],
      });

      // Optimistically set the single strategy cache
      if (data.id) {
        queryClient.setQueryData(
          strategyQueryKeys.detail(data.id),
          data
        );
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
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
 * Hook Options - Update Strategy
 */
export interface UseUpdateStrategyOptions {
  onSuccess?: (strategy: RecoveryStrategy) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Strategy Parameters
 */
export interface UpdateStrategyParams {
  strategyId: string;
  data: RecoveryStrategyUpdate;
}

/**
 * Hook to update an existing recovery strategy
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateStrategy = useUpdateStrategy({
 *   onSuccess: (strategy) => {
 *     console.log(`Strategy "${strategy.strategy_name}" updated`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * // Update strategy details
 * updateStrategy.mutate({
 *   strategyId: 'strategy-123',
 *   data: {
 *     description: 'Updated recovery procedures with new protocols',
 *     rto_target: 180, // Reduced to 3 hours
 *     estimated_cost: 75000, // Updated cost estimate
 *     testing_schedule: 'Monthly' // Increased testing frequency
 *   }
 * });
 * ```
 */
export function useUpdateStrategy(options: UseUpdateStrategyOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<RecoveryStrategy, Error, UpdateStrategyParams>({
    mutationFn: ({ strategyId, data }: UpdateStrategyParams) =>
      updateRecoveryStrategy(strategyId, data),

    onSuccess: (data) => {
      // Invalidate strategy lists
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.lists(),
      });

      // Invalidate the specific strategy detail
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.detail(data.id!),
      });

      // Invalidate effectiveness if it might have changed
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.effectiveness(data.id!),
      });

      // Invalidate parent plan queries
      queryClient.invalidateQueries({
        queryKey: ['plans', data.plan_id],
      });

      // Update the cached strategy data
      if (data.id) {
        queryClient.setQueryData(
          strategyQueryKeys.detail(data.id),
          data
        );
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
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
 * Hook Options - Delete Strategy
 */
export interface UseDeleteStrategyOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete a recovery strategy
 * Automatically invalidates strategy cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteStrategy = useDeleteStrategy({
 *   onSuccess: () => {
 *     console.log('Strategy deleted successfully');
 *     router.push('/planning/strategies');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * // Delete strategy
 * deleteStrategy.mutate('strategy-123');
 * ```
 */
export function useDeleteStrategy(options: UseDeleteStrategyOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: (strategyId: string) => deleteRecoveryStrategy(strategyId),

    onSuccess: (_, strategyId) => {
      // Invalidate all strategy lists
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.lists(),
      });

      // Invalidate the deleted strategy detail
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.detail(strategyId),
      });

      // Invalidate all plans to reflect the deletion
      queryClient.invalidateQueries({
        queryKey: ['plans'],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: strategyQueryKeys.detail(strategyId),
      });

      // Call user callback
      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
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
 * Hook Options - Record Strategy Test
 */
export interface UseRecordStrategyTestOptions {
  onSuccess?: (strategy: RecoveryStrategy) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Record Test Parameters
 */
export interface RecordTestParams {
  strategyId: string;
  testData: StrategyTestResult;
}

/**
 * Hook to record recovery strategy test results
 * Updates strategy with test date, results, and effectiveness rating
 * Automatically invalidates effectiveness metrics on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const recordTest = useRecordStrategyTest({
 *   onSuccess: (strategy) => {
 *     console.log(`Test recorded for "${strategy.strategy_name}"`);
 *     console.log(`New rating: ${strategy.effectiveness_rating}/5`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to record test: ${error.message}`);
 *   }
 * });
 *
 * // Record test results
 * recordTest.mutate({
 *   strategyId: 'strategy-123',
 *   testData: {
 *     test_date: new Date().toISOString(),
 *     test_results: 'All recovery steps executed successfully. RTO met at 3.5 hours. Minor improvements needed in communication protocols.',
 *     effectiveness_rating: 4,
 *     tester: 'John Doe - IT Manager'
 *   }
 * });
 * ```
 */
export function useRecordStrategyTest(options: UseRecordStrategyTestOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<RecoveryStrategy, Error, RecordTestParams>({
    mutationFn: ({ strategyId, testData }: RecordTestParams) =>
      recordStrategyTest(strategyId, testData),

    onSuccess: (data) => {
      // Invalidate strategy lists
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.lists(),
      });

      // Invalidate the specific strategy detail
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.detail(data.id!),
      });

      // Invalidate effectiveness - this is critical as test results affect it
      queryClient.invalidateQueries({
        queryKey: strategyQueryKeys.effectiveness(data.id!),
      });

      // Invalidate parent plan queries
      queryClient.invalidateQueries({
        queryKey: ['plans', data.plan_id],
      });

      // Update the cached strategy data
      if (data.id) {
        queryClient.setQueryData(
          strategyQueryKeys.detail(data.id),
          data
        );
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Call user callback
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      // Call user callback
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// ACTION PLANS - QUERY HOOKS (4 hooks)
// ============================================================================

/**
 * Hook Parameters - List Actions
 */
export interface UseActionsParams {
  planId: string;
  enabled?: boolean;
}

/**
 * Hook Options - Actions Query
 */
export interface UseActionsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch action plans for a plan
 *
 * @param params - Query parameters with planId
 * @returns Query result with actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: actions, isLoading } = useActions({
 *   planId: 'plan-123',
 *   enabled: true
 * });
 *
 * if (actions) {
 *   console.log(`Found ${actions.length} action items`);
 *   const completed = actions.filter(a => a.status === ActionStatus.COMPLETED);
 *   console.log(`Completed: ${completed.length}/${actions.length}`);
 * }
 * ```
 */
export function useActions({ planId, enabled = true }: UseActionsParams) {
  return useQuery({
    queryKey: actionQueryKeys.list(planId),
    queryFn: () => listActionPlans(planId),
    enabled: enabled && !!planId,
    staleTime: 3 * 60 * 1000, // 3 minutes (shorter for action tracking)
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Action
 */
export interface UseActionParams {
  actionId: string;
  enabled?: boolean;
}

/**
 * Hook Options - Action Query
 */
export interface UseActionOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch a single action plan by ID
 *
 * @param params - Query parameters with actionId
 * @returns Query result with action data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: action, isLoading, error } = useAction({
 *   actionId: 'action-123',
 *   enabled: true
 * });
 *
 * if (action) {
 *   console.log(`Action: ${action.action_title}`);
 *   console.log(`Priority: ${action.priority}`);
 *   console.log(`Status: ${action.status}`);
 *   console.log(`Progress: ${action.progress_percentage}%`);
 *   console.log(`Assigned to: ${action.assigned_to}`);
 * }
 * ```
 */
export function useAction({ actionId, enabled = true }: UseActionParams) {
  return useQuery({
    queryKey: actionQueryKeys.detail(actionId),
    queryFn: () => getActionPlan(actionId),
    enabled: enabled && !!actionId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Actions by User
 */
export interface UseActionsByUserParams {
  userId: string;
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch action plans assigned to a specific user
 * Returns all actions where the user is the responsible party
 *
 * @param params - Query parameters with userId and organizationId
 * @returns Query result with actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: myActions } = useActionsByUser({
 *   userId: 'user-123',
 *   organizationId: 'org-456',
 *   enabled: true
 * });
 *
 * if (myActions) {
 *   console.log(`You have ${myActions.length} assigned actions`);
 *   const pending = myActions.filter(a => a.status === ActionStatus.PENDING);
 *   const inProgress = myActions.filter(a => a.status === ActionStatus.IN_PROGRESS);
 *   console.log(`Pending: ${pending.length}, In Progress: ${inProgress.length}`);
 * }
 * ```
 */
export function useActionsByUser({ userId, organizationId, enabled = true }: UseActionsByUserParams) {
  return useQuery({
    queryKey: actionQueryKeys.byUser(userId, organizationId),
    queryFn: () => getActionsByUser(userId, organizationId),
    enabled: enabled && !!userId && !!organizationId,
    staleTime: 2 * 60 * 1000, // 2 minutes (shorter for personal actions)
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true, // Refetch when user returns to tab
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Overdue Actions
 */
export interface UseOverdueActionsParams {
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch overdue action plans
 * Returns all actions past their due date that are not completed
 *
 * @param params - Query parameters with organizationId
 * @returns Query result with overdue actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: overdueActions } = useOverdueActions({
 *   organizationId: 'org-123',
 *   enabled: true
 * });
 *
 * if (overdueActions && overdueActions.length > 0) {
 *   console.warn(`⚠️ ${overdueActions.length} overdue actions!`);
 *   overdueActions.forEach(action => {
 *     const daysPast = Math.floor(
 *       (Date.now() - new Date(action.due_date!).getTime()) / (1000 * 60 * 60 * 24)
 *     );
 *     console.log(`- ${action.action_title}: ${daysPast} days overdue`);
 *   });
 * }
 * ```
 */
export function useOverdueActions({ organizationId, enabled = true }: UseOverdueActionsParams) {
  return useQuery({
    queryKey: actionQueryKeys.overdue(organizationId),
    queryFn: () => getOverdueActions(organizationId),
    enabled: enabled && !!organizationId,
    staleTime: 1 * 60 * 1000, // 1 minute (very short for overdue tracking)
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true, // Always refetch when user returns
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// ACTION PLANS - MUTATION HOOKS (4 hooks)
// ============================================================================

/**
 * Hook Options - Create Action
 */
export interface UseCreateActionOptions {
  onSuccess?: (action: ActionPlan) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create a new action plan
 * Automatically invalidates action list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createAction = useCreateAction({
 *   onSuccess: (action) => {
 *     console.log(`Action "${action.action_title}" created`);
 *     router.push(`/planning/actions/${action.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create action: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * createAction.mutate({
 *   plan_id: 'plan-123',
 *   action_title: 'Conduct DR Test Exercise',
 *   description: 'Execute full disaster recovery test for IT systems',
 *   action_type: 'short_term',
 *   responsible_user_id: 'user-456',
 *   assigned_to: 'IT Security Team',
 *   due_date: '2025-12-31',
 *   priority: 'high',
 *   estimated_duration: 480, // 8 hours in minutes
 *   prerequisites: ['Notify stakeholders', 'Prepare test environment'],
 *   deliverables: ['Test report', 'Lessons learned document']
 * });
 * ```
 */
export function useCreateAction(options: UseCreateActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ActionPlan, Error, ActionPlanCreate>({
    mutationFn: (data: ActionPlanCreate) => createActionPlan(data),

    onSuccess: (data) => {
      // Invalidate action lists to refetch with new action
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate parent plan queries
      queryClient.invalidateQueries({
        queryKey: ['plans', data.plan_id],
      });

      // Invalidate user actions if assigned
      if (data.responsible_user_id) {
        queryClient.invalidateQueries({
          queryKey: [...actionQueryKeys.all, 'by-user', data.responsible_user_id],
        });
      }

      // Optimistically set the single action cache
      if (data.id) {
        queryClient.setQueryData(
          actionQueryKeys.detail(data.id),
          data
        );
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
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
 * Hook Options - Update Action
 */
export interface UseUpdateActionOptions {
  onSuccess?: (action: ActionPlan) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Action Parameters
 */
export interface UpdateActionParams {
  actionId: string;
  data: ActionPlanUpdate;
}

/**
 * Hook to update an existing action plan
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateAction = useUpdateAction({
 *   onSuccess: (action) => {
 *     console.log(`Action "${action.action_title}" updated`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * // Update action progress
 * updateAction.mutate({
 *   actionId: 'action-123',
 *   data: {
 *     status: ActionStatus.IN_PROGRESS,
 *     progress_percentage: 45,
 *     notes: 'Test environment prepared. Stakeholder notification in progress.'
 *   }
 * });
 * ```
 */
export function useUpdateAction(options: UseUpdateActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ActionPlan, Error, UpdateActionParams>({
    mutationFn: ({ actionId, data }: UpdateActionParams) =>
      updateActionPlan(actionId, data),

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.detail(data.id!),
      });

      // Invalidate parent plan queries
      queryClient.invalidateQueries({
        queryKey: ['plans', data.plan_id],
      });

      // Invalidate user actions if assigned
      if (data.responsible_user_id) {
        queryClient.invalidateQueries({
          queryKey: [...actionQueryKeys.all, 'by-user', data.responsible_user_id],
        });
      }

      // Invalidate overdue actions in case status changed
      queryClient.invalidateQueries({
        queryKey: [...actionQueryKeys.all, 'overdue'],
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(
          actionQueryKeys.detail(data.id),
          data
        );
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
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
 * Hook Options - Delete Action
 */
export interface UseDeleteActionOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete an action plan
 * Automatically invalidates action cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteAction = useDeleteAction({
 *   onSuccess: () => {
 *     console.log('Action deleted successfully');
 *     router.push('/planning/actions');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * // Delete action
 * deleteAction.mutate('action-123');
 * ```
 */
export function useDeleteAction(options: UseDeleteActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: (actionId: string) => deleteActionPlan(actionId),

    onSuccess: (_, actionId) => {
      // Invalidate all action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the deleted action detail
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.detail(actionId),
      });

      // Invalidate all plans to reflect the deletion
      queryClient.invalidateQueries({
        queryKey: ['plans'],
      });

      // Invalidate user actions
      queryClient.invalidateQueries({
        queryKey: [...actionQueryKeys.all, 'by-user'],
      });

      // Invalidate overdue actions
      queryClient.invalidateQueries({
        queryKey: [...actionQueryKeys.all, 'overdue'],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: actionQueryKeys.detail(actionId),
      });

      // Call user callback
      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
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
 * Hook Options - Complete Action
 */
export interface UseCompleteActionOptions {
  onSuccess?: (action: ActionPlan) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Complete Action Parameters
 */
export interface CompleteActionParams {
  actionId: string;
  completionDate: string;
}

/**
 * Hook to mark an action plan as complete
 * Sets status to completed and records completion date
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const completeAction = useCompleteAction({
 *   onSuccess: (action) => {
 *     console.log(`Action "${action.action_title}" completed!`);
 *     console.log(`Completed on: ${action.completion_date}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to complete action: ${error.message}`);
 *   }
 * });
 *
 * // Mark action as complete
 * completeAction.mutate({
 *   actionId: 'action-123',
 *   completionDate: new Date().toISOString()
 * });
 * ```
 */
export function useCompleteAction(options: UseCompleteActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ActionPlan, Error, CompleteActionParams>({
    mutationFn: ({ actionId, completionDate }: CompleteActionParams) =>
      completeActionPlan(actionId, completionDate),

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.detail(data.id!),
      });

      // Invalidate parent plan queries
      queryClient.invalidateQueries({
        queryKey: ['plans', data.plan_id],
      });

      // Invalidate user actions if assigned
      if (data.responsible_user_id) {
        queryClient.invalidateQueries({
          queryKey: [...actionQueryKeys.all, 'by-user', data.responsible_user_id],
        });
      }

      // Invalidate overdue actions - completion removes from overdue
      queryClient.invalidateQueries({
        queryKey: [...actionQueryKeys.all, 'overdue'],
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(
          actionQueryKeys.detail(data.id),
          data
        );
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Call user callback
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      // Call user callback
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// PREFETCH UTILITIES
// ============================================================================

/**
 * Prefetch utility for strategies list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/planning/plans/${planId}/strategies`}
 *   onMouseEnter={() => prefetchStrategies(queryClient, planId)}
 * >
 *   View Strategies
 * </Link>
 * ```
 */
export function prefetchStrategies(queryClient: QueryClient, planId: string) {
  return queryClient.prefetchQuery({
    queryKey: strategyQueryKeys.list(planId),
    queryFn: () => listRecoveryStrategies(planId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single strategy
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/planning/strategies/${strategyId}`}
 *   onMouseEnter={() => prefetchStrategy(queryClient, strategyId)}
 * >
 *   View Strategy Details
 * </Link>
 * ```
 */
export function prefetchStrategy(queryClient: QueryClient, strategyId: string) {
  return queryClient.prefetchQuery({
    queryKey: strategyQueryKeys.detail(strategyId),
    queryFn: () => getRecoveryStrategy(strategyId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for actions list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/planning/plans/${planId}/actions`}
 *   onMouseEnter={() => prefetchActions(queryClient, planId)}
 * >
 *   View Actions
 * </Link>
 * ```
 */
export function prefetchActions(queryClient: QueryClient, planId: string) {
  return queryClient.prefetchQuery({
    queryKey: actionQueryKeys.list(planId),
    queryFn: () => listActionPlans(planId),
    staleTime: 3 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single action
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/planning/actions/${actionId}`}
 *   onMouseEnter={() => prefetchAction(queryClient, actionId)}
 * >
 *   View Action Details
 * </Link>
 * ```
 */
export function prefetchAction(queryClient: QueryClient, actionId: string) {
  return queryClient.prefetchQuery({
    queryKey: actionQueryKeys.detail(actionId),
    queryFn: () => getActionPlan(actionId),
    staleTime: 3 * 60 * 1000,
  });
}
