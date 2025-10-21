/**
 * Risk Assessment Hooks - Barrel Export
 * Centralized exports for all risk assessment hooks
 * Week 5 - Risk Assessment Module
 */

// ==================== QUERY KEY FACTORY ====================
export { riskQueryKeys } from './useRisks';

// ==================== LIST HOOKS (CRUD - Round 2) ====================
export {
  useRisks,
  useCriticalRisks,
  useHighRisks,
  useActiveRisks,
  useTreatedRisks,
  useRisksByCategory,
  useRisksByOwner,
  prefetchRisks,
} from './useRisks';

export type {
  UseRisksParams,
  UseRisksOptions,
  RisksResponse,
} from './useRisks';

// ==================== SINGLE RISK HOOKS (CRUD - Round 2) ====================
export {
  useRisk,
  useRiskRequired,
  prefetchRisk,
  useIsRiskCached,
  useCachedRisk,
} from './useRisk';

export type {
  UseRiskParams,
  UseRiskOptions,
} from './useRisk';

// ==================== CREATE HOOKS (CRUD - Round 2) ====================
export {
  useCreateRisk,
  useCreateRiskWithScore,
  useCreateRisksBatch,
} from './useCreateRisk';

export type {
  UseCreateRiskOptions,
} from './useCreateRisk';

// ==================== UPDATE HOOKS (CRUD - Round 2) ====================
export {
  useUpdateRisk,
  useUpdateRiskOptimistic,
  useUpdateRiskStatus,
  useMarkRiskReviewed,
} from './useUpdateRisk';

export type {
  UseUpdateRiskOptions,
  UpdateRiskParams,
} from './useUpdateRisk';

// ==================== DELETE HOOKS (CRUD - Round 2) ====================
export {
  useDeleteRisk,
  useBulkDeleteRisks,
  useDeleteRiskWithConfirmation,
  useDeleteRiskWithUndo,
} from './useDeleteRisk';

export type {
  UseDeleteRiskOptions,
  DeleteRiskParams,
} from './useDeleteRisk';

// ==================== ANALYTICS HOOKS ====================

// FAIR Analysis
export {
  useFAIRAnalysis,
  usePerformFAIR,
  fairKeys,
} from './useFAIRAnalysis';

export type {
  UseFAIRAnalysisOptions,
  UsePerformFAIROptions,
} from './useFAIRAnalysis';

// Monte Carlo Simulation
export {
  useMonteCarlo,
  useRunMonteCarlo,
  monteCarloKeys,
} from './useMonteCarloSimulation';

export type {
  UseMonteCarloOptions,
  UseRunMonteCarloOptions,
} from './useMonteCarloSimulation';

// Risk Heat Map
export {
  useRiskHeatMap,
  heatMapKeys,
} from './useRiskHeatMap';

export type {
  UseRiskHeatMapOptions,
} from './useRiskHeatMap';

// Risk Trends
export {
  useRiskTrends,
  trendKeys,
} from './useRiskTrends';

export type {
  UseRiskTrendsOptions,
} from './useRiskTrends';

// Treatment Plans
export {
  useTreatmentPlans,
  useCreateTreatmentPlan,
  useUpdateTreatmentPlan,
  useDeleteTreatmentPlan,
  treatmentKeys,
} from './useTreatmentPlans';

export type {
  UseTreatmentPlansOptions,
  UseCreateTreatmentPlanOptions,
  UseUpdateTreatmentPlanOptions,
  UseDeleteTreatmentPlanOptions,
  UpdateTreatmentPlanParams,
} from './useTreatmentPlans';

// Risk Report
export {
  useRiskReport,
  reportKeys,
  getSeverityPercentages,
  getTrendIndicator,
} from './useRiskReport';

export type {
  UseRiskReportOptions,
} from './useRiskReport';

// ==================== AI/WORKFLOW INTELLIGENCE HOOKS ====================

// Risk Insights (AI)
export {
  useRiskInsights,
  insightsKeys,
  filterInsightsBySeverity,
  filterInsightsByType,
  getHighConfidenceInsights,
} from './useRiskInsights';

export type {
  UseRiskInsightsOptions,
  RiskInsight,
  RiskInsightsResponse,
} from './useRiskInsights';

// Risk Recommendations (AI)
export {
  useRiskRecommendations,
  recommendationsKeys,
  filterRecommendationsByPriority,
  filterRecommendationsByType,
  getHighConfidenceRecommendations,
  getRecommendationsForRisk,
  calculateTotalRiskReduction,
} from './useRiskRecommendations';

export type {
  UseRiskRecommendationsOptions,
  RiskRecommendation,
  RiskRecommendationsResponse,
} from './useRiskRecommendations';

// Similar Cases (AI)
export {
  useSimilarCases,
  similarCasesKeys,
  filterBySimilarityScore,
  filterBySimilarityAspect,
  getMostEffectiveTreatment,
  getAverageResolutionTime,
  getAllLessonsLearned,
} from './useSimilarCases';

export type {
  UseSimilarCasesOptions,
  SimilarCase,
  SimilarCasesResponse,
} from './useSimilarCases';

// Risk Patterns (AI)
export {
  useRiskPatterns,
  patternsKeys,
  getIncreasingThemes,
  getMostEffectiveTreatments,
  getStrongCorrelations,
  getSeasonalTrendByPeriod,
  getBestTreatmentForCategory,
  getAverageSeverity,
  getDecliningTreatments,
} from './useRiskPatterns';

export type {
  UseRiskPatternsOptions,
  RiskTheme,
  SeasonalTrend,
  CategoryCorrelation,
  TreatmentEffectiveness,
  RiskPatternsResponse,
} from './useRiskPatterns';
