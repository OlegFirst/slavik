/**
 * Planning Module Hooks - Barrel Export
 * Centralized exports for all business continuity planning hooks
 *
 * Created: 2025-10-21
 * Planning Module Round 2
 * Updated: 2025-10-22 (Agent 13 - Added BCPlan hooks export)
 */

// ==================== QUERY KEY FACTORIES ====================
export { planQueryKeys } from './plans';
export { strategyQueryKeys, actionQueryKeys } from './strategies';

// ==================== BC PLAN HOOKS (Agent 4 / Agent 13) ====================

// Query Hooks
export {
  usePlans,
  usePlan,
  usePlanVersionHistory,
  useActivePlans,
  useDraftPlans,
  usePlansByType,
  usePlansByProcess,
  usePrefetchPlan,
  useIsPlanCached,
  useCachedPlan,
  usePlanRequired,
} from './plans';

export type {
  UsePlansParams,
  UsePlansOptions,
  UsePlanParams,
  UsePlanOptions,
  UsePlanVersionHistoryOptions,
} from './plans';

// Mutation Hooks
export {
  useCreatePlan,
  useUpdatePlan,
  useDeletePlan,
  useApprovePlan,
  useActivatePlan,
  useArchivePlan,
  useClonePlan,
} from './plans';

export type {
  UseCreatePlanOptions,
  UseDeletePlanOptions,
  UpdatePlanParams,
  ApprovePlanParams,
  ClonePlanParams,
} from './plans';

// ==================== RECOVERY STRATEGY HOOKS (Agent 5) ====================

// Query Hooks
export {
  useStrategies,
  useStrategy,
  useStrategyEffectiveness,
  useStrategiesByProcess,
  prefetchStrategies,
  prefetchStrategy,
} from './strategies';

export type {
  UseStrategiesParams,
  UseStrategiesOptions,
  UseStrategyParams,
  UseStrategyOptions,
  UseStrategyEffectivenessParams,
  UseStrategiesByProcessParams,
} from './strategies';

// Mutation Hooks
export {
  useCreateStrategy,
  useUpdateStrategy,
  useDeleteStrategy,
  useRecordStrategyTest,
} from './strategies';

export type {
  UseCreateStrategyOptions,
  UseUpdateStrategyOptions,
  UpdateStrategyParams,
  UseDeleteStrategyOptions,
  UseRecordStrategyTestOptions,
  RecordTestParams,
} from './strategies';

// ==================== ACTION PLAN HOOKS (Agent 5) ====================

// Query Hooks
export {
  useActions,
  useAction,
  useActionsByUser,
  useOverdueActions,
  prefetchActions,
  prefetchAction,
} from './strategies';

export type {
  UseActionsParams,
  UseActionsOptions,
  UseActionParams,
  UseActionOptions,
  UseActionsByUserParams,
  UseOverdueActionsParams,
} from './strategies';

// Mutation Hooks
export {
  useCreateAction,
  useUpdateAction,
  useDeleteAction,
  useCompleteAction,
} from './strategies';

export type {
  UseCreateActionOptions,
  UseUpdateActionOptions,
  UpdateActionParams,
  UseDeleteActionOptions,
  UseCompleteActionOptions,
  CompleteActionParams,
} from './strategies';

// ==================== ANALYTICS & INTEGRATION HOOKS (Agent 6) ====================

export { analyticsKeys } from './analytics';

// Analytics Query Hooks
export {
  usePlanCoverage,
  useMaturityAssessment,
  usePlanningGaps,
  useImplementationTimeline,
  useExecutiveSummary,
} from './analytics';

export type {
  UsePlanCoverageParams,
  UseMaturityAssessmentParams,
  UsePlanningGapsParams,
  UseImplementationTimelineParams,
  UseExecutiveSummaryParams,
} from './analytics';

// Integration Query Hooks
export {
  useBIAAlignment,
  useRiskAlignment,
  usePlanDependencies,
} from './analytics';

export type {
  UseBIAAlignmentParams,
  UseRiskAlignmentParams,
  UsePlanDependenciesParams,
} from './analytics';
