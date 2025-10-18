/**
 * BIA Hooks - Barrel Export
 * All React Query hooks for Business Impact Analysis
 * Real API integration, no mocks
 */

// List hooks
export {
  useBIAProcesses,
  useCriticalProcesses,
  useCompletedProcesses,
  useDraftProcesses,
} from './useBIAProcesses';
export type { UseBIAProcessesParams, UseBIAProcessesOptions } from './useBIAProcesses';

// Single process hooks
export { useBIAProcess, prefetchBIAProcess } from './useBIAProcess';
export type { UseBIAProcessParams, UseBIAProcessOptions } from './useBIAProcess';

// Create hooks
export {
  useCreateBIAProcess,
  useBulkCreateBIAProcesses,
} from './useCreateBIAProcess';
export type { UseCreateBIAProcessOptions } from './useCreateBIAProcess';

// Update hooks
export {
  useUpdateBIAProcess,
  useCompleteBIAProcess,
  useBulkUpdateBIAProcesses,
} from './useUpdateBIAProcess';
export type {
  UseUpdateBIAProcessOptions,
  UpdateBIAProcessParams,
} from './useUpdateBIAProcess';

// Delete hooks
export {
  useDeleteBIAProcess,
  useBulkDeleteBIAProcesses,
} from './useDeleteBIAProcess';
export type {
  UseDeleteBIAProcessOptions,
  DeleteBIAProcessParams,
} from './useDeleteBIAProcess';

// AI hooks
export {
  useAISuggestion,
  useAISuggestionWithForm,
  getConfidenceLabel,
  shouldTrustSuggestion,
} from './useAISuggestion';
export type {
  AIRTOSuggestionParams,
  UseAISuggestionOptions,
} from './useAISuggestion';

// AI Advanced hooks
export { useAIDependencyDiscovery } from './useAIDependencyDiscovery';
export { useAIImpactCalculation } from './useAIImpactCalculation';
export { useAICriticalityAnalysis } from './useAICriticalityAnalysis';
export { useAIRecoveryStrategies } from './useAIRecoveryStrategies';
export type { UseAIRecoveryStrategiesOptions } from './useAIRecoveryStrategies';

// Summary/reporting hooks
export {
  useBIASummary,
  useBIASummaryLive,
  calculateCompletionPercentage,
  getCriticalityRatio,
  formatPotentialLoss,
  hasAdequateCoverage,
  getBIAHealthStatus,
  formatAverageRTO,
} from './useBIASummary';
export type { UseBIASummaryOptions } from './useBIASummary';
