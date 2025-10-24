/**
 * Compliance Module - Analytics & Integration Hooks
 * React Query hooks for compliance analytics and cross-module integration
 *
 * Created: 2025-10-24
 * Agent: 21 (Compliance Module - Analytics & Integration)
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complianceClient } from '@/lib/api/compliance-client';
import type {
  ComplianceAssessment,
  ComplianceGap,
  CorrectiveActionRecord,
  ComplianceScore,
  ComplianceTrendsResponse,
} from '@/types/compliance';
import { ComplianceStandard, ComplianceStatus } from '@/types/compliance';
import type {
  DashboardOverview,
  RequirementsMatrix,
  ComplianceRoadmap,
  AIAdvice,
  BenchmarkData,
  ImprovementInitiative,
  ManagementReview,
} from '@/lib/api/compliance-client';
import toast from 'react-hot-toast';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for compliance analytics
 * Provides centralized query key management for analytics and integration
 */
export const analyticsKeys = {
  all: ['compliance', 'analytics'] as const,
  overview: (orgId: string) => ['compliance', 'overview', orgId] as const,
  score: (orgId: string) => ['compliance', 'score', orgId] as const,
  trends: (orgId: string, days?: number) => ['compliance', 'trends', orgId, days] as const,
  roadmap: (orgId: string) => ['compliance', 'roadmap', orgId] as const,
  benchmarks: (orgId: string, type?: string) => ['compliance', 'benchmarks', orgId, type] as const,
  analytics: (orgId: string, type?: string) => ['compliance', 'analytics', orgId, type] as const,
  requirementsMatrix: (orgId: string, standard?: string) =>
    ['compliance', 'requirements-matrix', orgId, standard] as const,
  gapAnalysis: (orgId: string) => ['compliance', 'gap-analysis', orgId] as const,
  aiAdvice: (itemId: string, itemType: string) => ['compliance', 'ai-advice', itemId, itemType] as const,
  knowledgeBase: (query?: string) => ['compliance', 'knowledge-base', query] as const,
  biaAlignment: (orgId: string) => ['compliance', 'bia-alignment', orgId] as const,
  riskAlignment: (orgId: string) => ['compliance', 'risk-alignment', orgId] as const,
};

// ==================== TYPES ====================

// Dashboard Hook Options
export interface UseComplianceOverviewParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseComplianceScoreParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseComplianceTrendsParams {
  organizationId: string;
  periodDays?: number;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseComplianceRoadmapParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseBenchmarksParams {
  organizationId: string;
  benchmarkType?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

// Analytics Hook Options
export interface UseAnalyticsParams {
  organizationId: string;
  metricType?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseRequirementsMatrixParams {
  organizationId: string;
  standard?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseGapAnalysisParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseAIAdviceParams {
  itemId: string;
  itemType: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseKnowledgeBaseParams {
  searchQuery?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

// Corrective Actions & Improvements Hook Options
export interface UseCorrectiveActionsParams {
  organizationId: string;
  status?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseImprovementsParams {
  organizationId: string;
  status?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseManagementReviewsParams {
  organizationId: string;
  status?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

// Integration Hook Options
export interface UseBIAAlignmentParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseRiskAlignmentParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

// ==================== DASHBOARD HOOKS ====================

/**
 * Hook to fetch compliance dashboard overview
 * Provides high-level compliance metrics and status
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with dashboard overview data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: overview, isLoading, error } = useComplianceOverview({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (overview) {
 *   console.log('Compliance score:', overview.compliance_score);
 *   console.log('Total gaps:', overview.gaps.total);
 *   console.log('Upcoming audits:', overview.audits.upcoming);
 * }
 * ```
 */
export function useComplianceOverview({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseComplianceOverviewParams) {
  return useQuery({
    queryKey: analyticsKeys.overview(organizationId),
    queryFn: async (): Promise<DashboardOverview> => {
      return complianceClient.getComplianceOverview(organizationId);
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - overview changes frequently
    staleTime: staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: gcTime ?? 15 * 60 * 1000, // 15 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch compliance score breakdown
 * Shows detailed compliance scoring by clause, category, etc.
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with compliance score data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: score, isLoading, error } = useComplianceScore({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (score) {
 *   console.log('Overall score:', score.overall_score);
 *   console.log('Clause scores:', score.clause_scores);
 *   console.log('Coverage:', score.coverage);
 * }
 * ```
 */
export function useComplianceScore({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseComplianceScoreParams) {
  return useQuery({
    queryKey: analyticsKeys.score(organizationId),
    queryFn: async (): Promise<ComplianceScore> => {
      // This would typically be a dedicated endpoint
      const overview = await complianceClient.getComplianceOverview(organizationId);
      return {
        overall_score: overview.compliance_score,
        clause_scores: {}, // Would come from detailed API
        coverage: (overview.gaps.total > 0
          ? ((overview.assessments.completed / overview.assessments.total) * 100)
          : 100),
        gaps: [], // Would be populated from gap analysis
        recommendations: [], // Would come from AI analysis
      };
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - scores change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch compliance trends over time
 * Shows historical compliance score and status changes
 *
 * @param params - Query parameters including organizationId and period
 * @returns Query result with trend data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: trends, isLoading, error } = useComplianceTrends({
 *   organizationId: 'org-123',
 *   periodDays: 90,
 *   enabled: true,
 * });
 *
 * if (trends) {
 *   console.log('Trend direction:', trends.trend);
 *   console.log('Data points:', trends.data_points);
 * }
 * ```
 */
export function useComplianceTrends({
  organizationId,
  periodDays = 90,
  enabled = true,
  staleTime,
  gcTime,
}: UseComplianceTrendsParams) {
  return useQuery({
    queryKey: analyticsKeys.trends(organizationId, periodDays),
    queryFn: async (): Promise<ComplianceTrendsResponse> => {
      // Placeholder - would call dedicated trends endpoint
      const overview = await complianceClient.getComplianceOverview(organizationId);
      return {
        standard: ComplianceStandard.ISO_22301,
        period_days: periodDays,
        trend: 'stable',
        data_points: [
          {
            date: new Date().toISOString(),
            score: overview.compliance_score,
            status: ComplianceStatus.PARTIAL,
          },
        ],
      };
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - trends change slowly
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch compliance implementation roadmap
 * Shows planned milestones and timeline for compliance program
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with roadmap data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: roadmap, isLoading, error } = useComplianceRoadmap({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (roadmap) {
 *   console.log('Milestones:', roadmap.milestones);
 *   console.log('Timeline:', roadmap.timeline);
 * }
 * ```
 */
export function useComplianceRoadmap({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseComplianceRoadmapParams) {
  return useQuery({
    queryKey: analyticsKeys.roadmap(organizationId),
    queryFn: async () => {
      return complianceClient.getComplianceRoadmap(organizationId);
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - roadmap changes infrequently
    staleTime: staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch industry benchmarks
 * Compares organization's compliance metrics to industry standards
 *
 * @param params - Query parameters including organizationId and benchmark type
 * @returns Query result with benchmark data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: benchmarks, isLoading, error } = useBenchmarks({
 *   organizationId: 'org-123',
 *   benchmarkType: 'healthcare',
 *   enabled: true,
 * });
 *
 * if (benchmarks) {
 *   console.log('Industry average:', benchmarks[0].industry_average);
 *   console.log('Percentile ranking:', benchmarks[0].percentile_ranking);
 * }
 * ```
 */
export function useBenchmarks({
  organizationId,
  benchmarkType,
  enabled = true,
  staleTime,
  gcTime,
}: UseBenchmarksParams) {
  return useQuery({
    queryKey: analyticsKeys.benchmarks(organizationId, benchmarkType),
    queryFn: async () => {
      return complianceClient.getBenchmarks(organizationId, benchmarkType);
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - benchmarks change slowly
    staleTime: staleTime ?? 30 * 60 * 1000, // 30 minutes
    gcTime: gcTime ?? 2 * 60 * 60 * 1000, // 2 hours

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== ANALYTICS HOOKS ====================

/**
 * Hook to fetch general compliance analytics
 * Provides various compliance metrics and KPIs
 *
 * @param params - Query parameters including organizationId and metric type
 * @returns Query result with analytics data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: analytics, isLoading, error } = useAnalytics({
 *   organizationId: 'org-123',
 *   metricType: 'gap_closure_rate',
 *   enabled: true,
 * });
 *
 * if (analytics) {
 *   console.log('Analytics data:', analytics);
 * }
 * ```
 */
export function useAnalytics({
  organizationId,
  metricType,
  enabled = true,
  staleTime,
  gcTime,
}: UseAnalyticsParams) {
  return useQuery({
    queryKey: analyticsKeys.analytics(organizationId, metricType),
    queryFn: async () => {
      return complianceClient.getAnalytics(organizationId, metricType);
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - analytics change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch requirements coverage matrix
 * Shows which requirements are covered and by what evidence
 *
 * @param params - Query parameters including organizationId and standard
 * @returns Query result with requirements matrix data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: matrix, isLoading, error } = useRequirementsMatrix({
 *   organizationId: 'org-123',
 *   standard: 'iso_22301',
 *   enabled: true,
 * });
 *
 * if (matrix) {
 *   console.log('Requirements:', matrix.requirements);
 *   console.log('Coverage by clause:', matrix.requirements.filter(r => r.compliance_status === 'compliant'));
 * }
 * ```
 */
export function useRequirementsMatrix({
  organizationId,
  standard,
  enabled = true,
  staleTime,
  gcTime,
}: UseRequirementsMatrixParams) {
  return useQuery({
    queryKey: analyticsKeys.requirementsMatrix(organizationId, standard),
    queryFn: async () => {
      return complianceClient.getRequirementsMatrix(organizationId, standard);
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - matrix changes moderately
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch gap analysis
 * Analyzes compliance gaps by severity, status, and category
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with gap analysis data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: gapAnalysis, isLoading, error } = useGapAnalysis({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (gapAnalysis) {
 *   console.log('Total gaps:', gapAnalysis.length);
 *   console.log('Critical gaps:', gapAnalysis.filter(g => g.severity === 'critical'));
 * }
 * ```
 */
export function useGapAnalysis({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseGapAnalysisParams) {
  return useQuery({
    queryKey: analyticsKeys.gapAnalysis(organizationId),
    queryFn: async () => {
      return complianceClient.listGaps({ organization_id: organizationId });
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - gaps change frequently
    staleTime: staleTime ?? 3 * 60 * 1000, // 3 minutes
    gcTime: gcTime ?? 20 * 60 * 1000, // 20 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch AI-powered compliance advice
 * Provides AI recommendations for compliance items
 *
 * @param params - Query parameters including itemId and itemType
 * @returns Query result with AI advice data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: advice, isLoading, error } = useAIAdvice({
 *   itemId: 'gap-123',
 *   itemType: 'gap',
 *   enabled: true,
 * });
 *
 * if (advice) {
 *   console.log('Recommendations:', advice.recommendations);
 *   console.log('Confidence:', advice.confidence_score);
 * }
 * ```
 */
export function useAIAdvice({
  itemId,
  itemType,
  enabled = true,
  staleTime,
  gcTime,
}: UseAIAdviceParams) {
  return useQuery({
    queryKey: analyticsKeys.aiAdvice(itemId, itemType),
    queryFn: async () => {
      return complianceClient.getAIAdvice(itemId, itemType);
    },

    // Enable/disable query
    enabled: enabled && !!itemId && !!itemType,

    // Caching strategy - AI advice is relatively static
    staleTime: staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 1, // Less retries for AI services
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to search compliance knowledge base
 * Searches standards, best practices, and guidance
 *
 * @param params - Query parameters including search query
 * @returns Query result with knowledge base results, loading state, error
 *
 * @example
 * ```tsx
 * const { data: results, isLoading, error } = useKnowledgeBase({
 *   searchQuery: 'business continuity plan',
 *   enabled: true,
 * });
 *
 * if (results) {
 *   console.log('Search results:', results);
 * }
 * ```
 */
export function useKnowledgeBase({
  searchQuery,
  enabled = true,
  staleTime,
  gcTime,
}: UseKnowledgeBaseParams) {
  return useQuery({
    queryKey: analyticsKeys.knowledgeBase(searchQuery),
    queryFn: async (): Promise<any[]> => {
      if (!searchQuery) return [];
      return complianceClient.searchKnowledgeBase(searchQuery);
    },

    // Enable/disable query
    enabled: enabled && !!searchQuery && searchQuery.length >= 3,

    // Caching strategy - knowledge base is static
    staleTime: staleTime ?? 60 * 60 * 1000, // 60 minutes
    gcTime: gcTime ?? 4 * 60 * 60 * 1000, // 4 hours

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== CORRECTIVE ACTIONS & IMPROVEMENTS ====================

/**
 * Hook to fetch corrective actions list
 * Lists all corrective actions with optional filtering
 *
 * @param params - Query parameters including organizationId and status
 * @returns Query result with corrective actions data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: actions, isLoading, error } = useCorrectiveActions({
 *   organizationId: 'org-123',
 *   status: 'in_progress',
 *   enabled: true,
 * });
 *
 * if (actions) {
 *   console.log('Corrective actions:', actions);
 * }
 * ```
 */
export function useCorrectiveActions({
  organizationId,
  status,
  enabled = true,
  staleTime,
  gcTime,
}: UseCorrectiveActionsParams) {
  return useQuery({
    queryKey: ['compliance', 'corrective-actions', organizationId, status],
    queryFn: async (): Promise<CorrectiveActionRecord[]> => {
      // Placeholder - would call dedicated corrective actions endpoint
      // For now, return empty array
      return [];
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - actions change frequently
    staleTime: staleTime ?? 3 * 60 * 1000, // 3 minutes
    gcTime: gcTime ?? 20 * 60 * 1000, // 20 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch improvement initiatives
 * Lists all improvement initiatives with optional filtering
 *
 * @param params - Query parameters including organizationId and status
 * @returns Query result with improvements data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: improvements, isLoading, error } = useImprovements({
 *   organizationId: 'org-123',
 *   status: 'in_progress',
 *   enabled: true,
 * });
 *
 * if (improvements) {
 *   console.log('Improvement initiatives:', improvements);
 *   console.log('Total investment:', improvements.reduce((sum, i) => sum + (i.actual_cost || 0), 0));
 * }
 * ```
 */
export function useImprovements({
  organizationId,
  status,
  enabled = true,
  staleTime,
  gcTime,
}: UseImprovementsParams) {
  return useQuery({
    queryKey: ['compliance', 'improvements', organizationId, status],
    queryFn: async () => {
      return complianceClient.listImprovements({
        organization_id: organizationId,
        status,
      });
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - improvements change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch management reviews
 * Lists all management reviews with optional filtering
 *
 * @param params - Query parameters including organizationId and status
 * @returns Query result with management reviews data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: reviews, isLoading, error } = useManagementReviews({
 *   organizationId: 'org-123',
 *   status: 'completed',
 *   enabled: true,
 * });
 *
 * if (reviews) {
 *   console.log('Management reviews:', reviews);
 *   console.log('Decisions made:', reviews.flatMap(r => r.decisions || []));
 * }
 * ```
 */
export function useManagementReviews({
  organizationId,
  status,
  enabled = true,
  staleTime,
  gcTime,
}: UseManagementReviewsParams) {
  return useQuery({
    queryKey: ['compliance', 'management-reviews', organizationId, status],
    queryFn: async () => {
      return complianceClient.listManagementReviews({
        organization_id: organizationId,
        status,
      });
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - reviews change slowly
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== INTEGRATION HOOKS ====================

/**
 * Hook to fetch BIA alignment analysis
 * Shows how compliance program aligns with Business Impact Analysis
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with BIA alignment data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: alignment, isLoading, error } = useBIAAlignment({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (alignment) {
 *   console.log('BIA alignment:', alignment);
 * }
 * ```
 */
export function useBIAAlignment({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseBIAAlignmentParams) {
  return useQuery({
    queryKey: analyticsKeys.biaAlignment(organizationId),
    queryFn: async (): Promise<any> => {
      // Placeholder - would call BIA integration endpoint
      // For now, return mock data
      return {
        aligned_processes: [],
        unaligned_processes: [],
        coverage_percentage: 0,
      };
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - alignment changes slowly
    staleTime: staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch risk alignment analysis
 * Shows how compliance program addresses identified risks
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with risk alignment data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: alignment, isLoading, error } = useRiskAlignment({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (alignment) {
 *   console.log('Risk alignment:', alignment);
 * }
 * ```
 */
export function useRiskAlignment({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseRiskAlignmentParams) {
  return useQuery({
    queryKey: analyticsKeys.riskAlignment(organizationId),
    queryFn: async (): Promise<any> => {
      // Placeholder - would call Risk integration endpoint
      // For now, return mock data
      return {
        covered_risks: [],
        uncovered_risks: [],
        mitigation_effectiveness: 0,
      };
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - alignment changes slowly
    staleTime: staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Helper function to calculate compliance percentage
 * @param compliant - Number of compliant requirements
 * @param total - Total number of requirements
 * @returns Compliance percentage (0-100)
 */
export function calculateCompliancePercentage(compliant: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((compliant / total) * 100);
}

/**
 * Helper function to get compliance status from score
 * @param score - Compliance score (0-100)
 * @returns Compliance status
 */
export function getComplianceStatus(score: number): string {
  if (score >= 90) return 'compliant';
  if (score >= 70) return 'partial_compliance';
  if (score >= 50) return 'non_compliant';
  return 'not_assessed';
}

/**
 * Helper function to categorize gaps by severity
 * @param gaps - Array of compliance gaps
 * @returns Gaps categorized by severity
 */
export function categorizeGapsBySeverity(gaps: ComplianceGap[]): {
  critical: ComplianceGap[];
  high: ComplianceGap[];
  medium: ComplianceGap[];
  low: ComplianceGap[];
} {
  if (!Array.isArray(gaps)) {
    return { critical: [], high: [], medium: [], low: [] };
  }

  return {
    critical: gaps.filter((g) => g.severity === 'critical'),
    high: gaps.filter((g) => g.severity === 'high'),
    medium: gaps.filter((g) => g.severity === 'medium'),
    low: gaps.filter((g) => g.severity === 'low'),
  };
}

/**
 * Helper function to get overdue corrective actions
 * @param actions - Array of corrective actions
 * @returns Overdue actions
 */
export function getOverdueActions(actions: CorrectiveActionRecord[]): CorrectiveActionRecord[] {
  if (!Array.isArray(actions)) return [];

  const now = new Date();

  return actions.filter((action) => {
    if (!action.target_date) return false;
    const targetDate = new Date(action.target_date);
    return targetDate < now && action.status !== 'completed' && action.status !== 'verified';
  });
}

/**
 * Helper function to calculate average compliance score by clause
 * @param matrix - Requirements matrix
 * @returns Average scores by clause
 */
export function getAverageScoresByClause(matrix: RequirementsMatrix): Record<string, number> {
  if (!matrix || !matrix.requirements) return {};

  const clauseGroups: Record<string, number[]> = {};

  matrix.requirements.forEach((req) => {
    const clause = req.clause.split('.')[0]; // Get main clause number
    if (!clauseGroups[clause]) {
      clauseGroups[clause] = [];
    }
    // Convert status to score
    let score = 0;
    switch (req.compliance_status) {
      case 'compliant':
        score = 100;
        break;
      case 'partial':
        score = 50;
        break;
      case 'non_compliant':
        score = 0;
        break;
      case 'not_assessed':
        score = 0;
        break;
    }
    clauseGroups[clause].push(score);
  });

  const averages: Record<string, number> = {};
  Object.entries(clauseGroups).forEach(([clause, scores]) => {
    averages[clause] = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  });

  return averages;
}

/**
 * Helper function to get upcoming milestones
 * @param roadmap - Compliance roadmap
 * @param days - Number of days to look ahead
 * @returns Upcoming milestones
 */
export function getUpcomingMilestones(roadmap: ComplianceRoadmap, days: number = 30): any[] {
  if (!roadmap || !roadmap.milestones) return [];

  const now = new Date();
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + days);

  return roadmap.milestones.filter((milestone) => {
    const targetDate = new Date(milestone.target_date);
    return targetDate >= now && targetDate <= futureDate;
  });
}

/**
 * Helper function to calculate improvement ROI
 * @param improvement - Improvement initiative
 * @returns ROI percentage
 */
export function calculateImprovementROI(improvement: ImprovementInitiative): number {
  if (!improvement.actual_cost || improvement.actual_cost === 0) return 0;

  // This is simplified - real ROI would consider actual benefits value
  const benefitsValue = (improvement.actual_benefits?.length || 0) * 10000; // Mock calculation
  const cost = improvement.actual_cost;

  return Math.round(((benefitsValue - cost) / cost) * 100);
}

/**
 * Helper function to get risk-based priority
 * @param gap - Compliance gap
 * @returns Priority score (1-10)
 */
export function getRiskBasedPriority(gap: ComplianceGap): number {
  let score = 0;

  // Severity scoring
  switch (gap.severity) {
    case 'critical':
      score += 4;
      break;
    case 'high':
      score += 3;
      break;
    case 'medium':
      score += 2;
      break;
    case 'low':
      score += 1;
      break;
  }

  // Add urgency based on due date
  if (gap.due_date) {
    const now = new Date();
    const dueDate = new Date(gap.due_date);
    const daysUntilDue = Math.ceil((dueDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (daysUntilDue < 7) score += 3;
    else if (daysUntilDue < 30) score += 2;
    else if (daysUntilDue < 90) score += 1;
  }

  return Math.min(score, 10);
}
