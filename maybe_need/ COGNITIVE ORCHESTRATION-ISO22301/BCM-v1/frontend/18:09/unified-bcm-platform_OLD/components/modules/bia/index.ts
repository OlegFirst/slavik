// BIA Module Components Export
export { DependencyMap } from './DependencyMap'
export { default as CriticalPathAnalysis } from './CriticalPathAnalysis'

// Re-export types from bia-api for convenience
export type {
  CriticalPath,
  OptimizationOpportunity,
  BIAResult,
  BIAMetrics,
  DependencyMapping,
  BusinessFunction,
  BusinessProcess,
  ProcessResource
} from '@/services/bia-api'