/**
 * Compliance Module Hooks - Barrel Export
 * Centralized exports for all compliance management hooks
 *
 * Created: 2025-10-24
 * Agent: 21 (Compliance Module - Analytics & Integration)
 */

// ==================== QUERY KEY FACTORIES ====================
export { analyticsKeys } from './analytics';

// ==================== ANALYTICS & INTEGRATION HOOKS (Agent 21) ====================

// Dashboard Query Hooks
export {
  useComplianceOverview,
  useComplianceScore,
  useComplianceTrends,
  useComplianceRoadmap,
  useBenchmarks,
} from './analytics';

export type {
  UseComplianceOverviewParams,
  UseComplianceScoreParams,
  UseComplianceTrendsParams,
  UseComplianceRoadmapParams,
  UseBenchmarksParams,
} from './analytics';

// Analytics Query Hooks
export {
  useAnalytics,
  useRequirementsMatrix,
  useGapAnalysis,
  useAIAdvice,
  useKnowledgeBase,
} from './analytics';

export type {
  UseAnalyticsParams,
  UseRequirementsMatrixParams,
  UseGapAnalysisParams,
  UseAIAdviceParams,
  UseKnowledgeBaseParams,
} from './analytics';

// Corrective Actions & Improvements Query Hooks
export {
  useCorrectiveActions,
  useImprovements,
  useManagementReviews,
} from './analytics';

export type {
  UseCorrectiveActionsParams,
  UseImprovementsParams,
  UseManagementReviewsParams,
} from './analytics';

// Integration Query Hooks
export {
  useBIAAlignment,
  useRiskAlignment,
} from './analytics';

export type {
  UseBIAAlignmentParams,
  UseRiskAlignmentParams,
} from './analytics';

// Helper Functions
export {
  calculateCompliancePercentage,
  getComplianceStatus,
  categorizeGapsBySeverity,
  getOverdueActions,
  getAverageScoresByClause,
  getUpcomingMilestones,
  calculateImprovementROI,
  getRiskBasedPriority,
} from './analytics';
