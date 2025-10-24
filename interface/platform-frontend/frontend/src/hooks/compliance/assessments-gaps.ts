/**
 * Compliance Module - Assessments & Gaps Hooks
 * React Query hooks for Compliance Assessments and Gap Management
 * ISO 22301:2019 Clause 10 - Improvement
 *
 * Created: 2025-10-24
 * Agent: 19 (Compliance Module Round 2)
 *
 * Total Hooks: 30
 * - Assessment Hooks: 12 hooks (6 query + 6 mutation)
 * - Gap Hooks: 18 hooks (9 query + 9 mutation)
 */

'use client';

import { useQuery, useMutation, useQueryClient, type QueryClient } from '@tanstack/react-query';
import { complianceClient } from '@/lib/api/compliance-client';
import type {
  ComplianceAssessment,
  ComplianceAssessmentUpdate as ApiComplianceAssessmentUpdate,
  ComplianceGap,
  ComplianceGapUpdate as ApiComplianceGapUpdate,
  RCAAnalysis,
  RCAAnalysisCreate as ApiRCAAnalysisCreate,
  AssessmentResults,
  EffectivenessReview,
} from '@/lib/api/compliance-client';
import type {
  GapSeverity,
} from '@/types/compliance';

// ============================================================================
// QUERY KEY FACTORIES
// ============================================================================

/**
 * Query key factory for compliance assessments
 * Provides consistent cache key generation for all assessment-related queries
 */
export const assessmentQueryKeys = {
  all: ['compliance', 'assessments'] as const,
  lists: () => [...assessmentQueryKeys.all, 'list'] as const,
  list: (organizationId: string, status?: string) =>
    [...assessmentQueryKeys.lists(), { organizationId, status }] as const,
  details: () => [...assessmentQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...assessmentQueryKeys.details(), id] as const,
  results: (id: string) => [...assessmentQueryKeys.detail(id), 'results'] as const,
  compliance: (organizationId: string) =>
    [...assessmentQueryKeys.all, 'check', organizationId] as const,
};

/**
 * Query key factory for compliance gaps
 * Provides consistent cache key generation for all gap-related queries
 */
export const gapQueryKeys = {
  all: ['compliance', 'gaps'] as const,
  lists: () => [...gapQueryKeys.all, 'list'] as const,
  list: (organizationId: string, status?: string) =>
    [...gapQueryKeys.lists(), { organizationId, status }] as const,
  details: () => [...gapQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...gapQueryKeys.details(), id] as const,
  rca: (id: string) => [...gapQueryKeys.detail(id), 'rca'] as const,
  effectivenessReviews: (id: string) =>
    [...gapQueryKeys.detail(id), 'effectiveness-reviews'] as const,
  bySeverity: (severity: GapSeverity, organizationId: string) =>
    [...gapQueryKeys.all, 'severity', severity, organizationId] as const,
  overdue: (organizationId: string) =>
    [...gapQueryKeys.all, 'overdue', organizationId] as const,
};

// ============================================================================
// COMPLIANCE ASSESSMENTS - QUERY HOOKS (6 hooks)
// ============================================================================

/**
 * Hook Parameters - List Assessments
 */
export interface UseAssessmentsParams {
  organizationId: string;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Hook to fetch compliance assessments for an organization
 *
 * @param params - Query parameters with organizationId and optional filters
 * @returns Query result with assessments array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: assessments, isLoading } = useComplianceAssessments({
 *   organizationId: 'org-123',
 *   status: 'in_progress',
 *   enabled: true
 * });
 *
 * if (assessments) {
 *   console.log(`Found ${assessments.length} assessments`);
 * }
 * ```
 */
export function useComplianceAssessments({
  organizationId,
  status,
  search,
  page,
  limit,
  enabled = true,
}: UseAssessmentsParams) {
  return useQuery({
    queryKey: assessmentQueryKeys.list(organizationId, status),
    queryFn: () => complianceClient.listAssessments({
      organization_id: organizationId,
      status,
      search,
      page,
      limit,
    }),
    enabled: enabled && !!organizationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Assessment
 */
export interface UseAssessmentParams {
  assessmentId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch a single compliance assessment by ID
 *
 * @param params - Query parameters with assessmentId
 * @returns Query result with assessment data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: assessment, isLoading, error } = useComplianceAssessment({
 *   assessmentId: 'assessment-123',
 *   enabled: true
 * });
 *
 * if (assessment) {
 *   console.log(`Assessment: ${assessment.assessment_name}`);
 *   console.log(`Standard: ${assessment.standard}`);
 *   console.log(`Status: ${assessment.status}`);
 *   console.log(`Score: ${assessment.overall_score}`);
 * }
 * ```
 */
export function useComplianceAssessment({ assessmentId, enabled = true }: UseAssessmentParams) {
  return useQuery({
    queryKey: assessmentQueryKeys.detail(assessmentId),
    queryFn: () => complianceClient.getAssessment(assessmentId),
    enabled: enabled && !!assessmentId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Assessment Results
 */
export interface UseAssessmentResultsParams {
  assessmentId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch assessment results and metrics
 * Returns overall score, compliance by clause, gaps, and recommendations
 *
 * @param params - Query parameters with assessmentId
 * @returns Query result with results data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: results } = useGetAssessmentResults({
 *   assessmentId: 'assessment-123'
 * });
 *
 * if (results) {
 *   console.log(`Overall Score: ${results.overall_score}/100`);
 *   console.log(`Compliance: ${results.compliance_percentage}%`);
 *   console.log(`Gaps Identified: ${results.gaps_identified}`);
 *   console.log(`Recommendations: ${results.recommendations.length}`);
 * }
 * ```
 */
export function useGetAssessmentResults({
  assessmentId,
  enabled = true
}: UseAssessmentResultsParams) {
  return useQuery({
    queryKey: assessmentQueryKeys.results(assessmentId),
    queryFn: () => complianceClient.getAssessmentResults(assessmentId),
    enabled: enabled && !!assessmentId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Check Compliance
 */
export interface UseCheckComplianceParams {
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to check overall compliance status for an organization
 * Returns current compliance level and key metrics
 *
 * @param params - Query parameters with organizationId
 * @returns Query result with compliance status, loading state, error
 *
 * @example
 * ```tsx
 * const { data: complianceStatus } = useCheckCompliance({
 *   organizationId: 'org-123'
 * });
 *
 * if (complianceStatus) {
 *   console.log(`Compliance Level: ${complianceStatus.level}`);
 *   console.log(`Score: ${complianceStatus.score}/100`);
 * }
 * ```
 */
export function useCheckCompliance({
  organizationId,
  enabled = true
}: UseCheckComplianceParams) {
  return useQuery({
    queryKey: assessmentQueryKeys.compliance(organizationId),
    queryFn: () => complianceClient.checkCompliance(organizationId),
    enabled: enabled && !!organizationId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// COMPLIANCE ASSESSMENTS - MUTATION HOOKS (6 hooks)
// ============================================================================

/**
 * Hook Options - Create Assessment
 */
export interface UseCreateAssessmentOptions {
  onSuccess?: (assessment: ComplianceAssessment) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create a new compliance assessment
 * Automatically invalidates assessment list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createAssessment = useCreateComplianceAssessment({
 *   onSuccess: (assessment) => {
 *     console.log(`Assessment "${assessment.assessment_name}" created`);
 *     router.push(`/compliance/assessments/${assessment.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create assessment: ${error.message}`);
 *   }
 * });
 *
 * createAssessment.mutate({
 *   organization_id: 'org-123',
 *   assessment_name: 'ISO 22301:2019 Annual Assessment',
 *   description: 'Full compliance assessment against ISO 22301 standard',
 *   standard: 'iso_22301',
 *   scope: 'All business continuity processes',
 *   assessor_id: 'user-456',
 *   start_date: '2025-11-01',
 *   end_date: '2025-11-30'
 * });
 * ```
 */
export function useCreateComplianceAssessment(options: UseCreateAssessmentOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAssessment, Error, any>({
    mutationFn: (data: any) =>
      complianceClient.createAssessment(data),

    onSuccess: (data) => {
      // Invalidate assessment lists to refetch with new assessment
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.lists(),
      });

      // Invalidate compliance check
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Optimistically set the single assessment cache
      if (data.id) {
        queryClient.setQueryData(
          assessmentQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Assessment
 */
export interface UseUpdateAssessmentOptions {
  onSuccess?: (assessment: ComplianceAssessment) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Assessment Parameters
 */
export interface UpdateAssessmentParams {
  assessmentId: string;
  data: ApiComplianceAssessmentUpdate;
}

/**
 * Hook to update an existing compliance assessment
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateAssessment = useUpdateComplianceAssessment({
 *   onSuccess: (assessment) => {
 *     console.log(`Assessment updated: ${assessment.assessment_name}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * updateAssessment.mutate({
 *   assessmentId: 'assessment-123',
 *   data: {
 *     status: 'in_progress',
 *     overall_score: 75,
 *     completion_date: '2025-11-30'
 *   }
 * });
 * ```
 */
export function useUpdateComplianceAssessment(options: UseUpdateAssessmentOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAssessment, Error, UpdateAssessmentParams>({
    mutationFn: ({ assessmentId, data }) =>
      complianceClient.updateAssessment(assessmentId, data),

    onSuccess: (data) => {
      // Invalidate assessment lists
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.lists(),
      });

      // Invalidate the specific assessment detail
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.detail(data.id!),
      });

      // Invalidate results if they might have changed
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.results(data.id!),
      });

      // Invalidate compliance check
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Update the cached assessment data
      if (data.id) {
        queryClient.setQueryData(
          assessmentQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Delete Assessment
 */
export interface UseDeleteAssessmentOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete a compliance assessment
 * Automatically invalidates assessment cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteAssessment = useDeleteComplianceAssessment({
 *   onSuccess: () => {
 *     console.log('Assessment deleted successfully');
 *     router.push('/compliance/assessments');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * deleteAssessment.mutate('assessment-123');
 * ```
 */
export function useDeleteComplianceAssessment(options: UseDeleteAssessmentOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: (assessmentId: string) =>
      complianceClient.deleteAssessment(assessmentId),

    onSuccess: (_, assessmentId) => {
      // Invalidate all assessment lists
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.lists(),
      });

      // Invalidate the deleted assessment detail
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.detail(assessmentId),
      });

      // Invalidate compliance checks
      queryClient.invalidateQueries({
        queryKey: [...assessmentQueryKeys.all, 'check'],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: assessmentQueryKeys.detail(assessmentId),
      });

      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Run Assessment
 */
export interface UseRunAssessmentOptions {
  onSuccess?: (assessment: ComplianceAssessment) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to execute a compliance assessment
 * Runs the assessment process and updates status and results
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const runAssessment = useRunAssessment({
 *   onSuccess: (assessment) => {
 *     console.log(`Assessment completed with score: ${assessment.overall_score}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Assessment failed: ${error.message}`);
 *   }
 * });
 *
 * runAssessment.mutate('assessment-123');
 * ```
 */
export function useRunAssessment(options: UseRunAssessmentOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAssessment, Error, string>({
    mutationFn: (assessmentId) =>
      complianceClient.runAssessment(assessmentId),

    onSuccess: (data) => {
      // Invalidate assessment lists
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.lists(),
      });

      // Invalidate the specific assessment detail
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.detail(data.id!),
      });

      // Invalidate results - critical as they just changed
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.results(data.id!),
      });

      // Invalidate compliance check
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Invalidate gaps as assessment may identify new ones
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Update the cached assessment data
      if (data.id) {
        queryClient.setQueryData(
          assessmentQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Batch AI Scan
 */
export interface UseBatchAIScanOptions {
  onSuccess?: (result: any) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to perform batch AI scan on multiple assessments
 * Uses AI to analyze and provide insights across assessments
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const batchScan = useBatchAIScan({
 *   onSuccess: (result) => {
 *     console.log(`Scanned ${result.scanned_count} assessments`);
 *     console.log(`Insights: ${result.insights.length}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Batch scan failed: ${error.message}`);
 *   }
 * });
 *
 * batchScan.mutate(['assessment-1', 'assessment-2', 'assessment-3']);
 * ```
 */
export function useBatchAIScan(options: UseBatchAIScanOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<any, Error, string[]>({
    mutationFn: (assessmentIds: string[]) =>
      complianceClient.batchAIScan(assessmentIds),

    onSuccess: (data) => {
      // Invalidate all assessment lists and details
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.lists(),
      });

      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.details(),
      });

      // Invalidate compliance checks
      queryClient.invalidateQueries({
        queryKey: [...assessmentQueryKeys.all, 'check'],
      });

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// COMPLIANCE GAPS - QUERY HOOKS (9 hooks)
// ============================================================================

/**
 * Hook Parameters - List Gaps
 */
export interface UseGapsParams {
  organizationId: string;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Hook to fetch compliance gaps for an organization
 *
 * @param params - Query parameters with organizationId and optional filters
 * @returns Query result with gaps array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: gaps, isLoading } = useComplianceGaps({
 *   organizationId: 'org-123',
 *   status: 'identified',
 *   enabled: true
 * });
 *
 * if (gaps) {
 *   console.log(`Found ${gaps.length} compliance gaps`);
 *   const critical = gaps.filter(g => g.severity === 'critical');
 *   console.log(`Critical gaps: ${critical.length}`);
 * }
 * ```
 */
export function useComplianceGaps({
  organizationId,
  status,
  search,
  page,
  limit,
  enabled = true,
}: UseGapsParams) {
  return useQuery({
    queryKey: gapQueryKeys.list(organizationId, status),
    queryFn: () => complianceClient.listGaps({
      organization_id: organizationId,
      status,
      search,
      page,
      limit,
    }),
    enabled: enabled && !!organizationId,
    staleTime: 3 * 60 * 1000, // 3 minutes (shorter for gap tracking)
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Gap
 */
export interface UseGapParams {
  gapId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch a single compliance gap by ID
 *
 * @param params - Query parameters with gapId
 * @returns Query result with gap data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: gap, isLoading, error } = useComplianceGap({
 *   gapId: 'gap-123',
 *   enabled: true
 * });
 *
 * if (gap) {
 *   console.log(`Gap: ${gap.gap_description}`);
 *   console.log(`Severity: ${gap.severity}`);
 *   console.log(`Priority: ${gap.priority}`);
 *   console.log(`Status: ${gap.status}`);
 *   console.log(`Coverage: ${gap.current_coverage}% / ${gap.target_coverage}%`);
 * }
 * ```
 */
export function useComplianceGap({ gapId, enabled = true }: UseGapParams) {
  return useQuery({
    queryKey: gapQueryKeys.detail(gapId),
    queryFn: () => complianceClient.getGap(gapId),
    enabled: enabled && !!gapId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Gap RCA
 */
export interface UseGapRCAParams {
  gapId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch root cause analysis for a gap
 * Returns RCA method, root causes, and recommendations
 *
 * @param params - Query parameters with gapId
 * @returns Query result with RCA data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: rca } = useGapRCA({
 *   gapId: 'gap-123'
 * });
 *
 * if (rca) {
 *   console.log(`RCA Method: ${rca.method}`);
 *   console.log(`Root Causes: ${rca.root_causes.length}`);
 *   console.log(`Analysis: ${rca.analysis_summary}`);
 * }
 * ```
 */
export function useGapRCA({ gapId, enabled = true }: UseGapRCAParams) {
  return useQuery({
    queryKey: gapQueryKeys.rca(gapId),
    queryFn: () => complianceClient.getGapRCA(gapId),
    enabled: enabled && !!gapId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Effectiveness Reviews
 */
export interface UseEffectivenessReviewsParams {
  gapId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch effectiveness reviews for a gap
 * Returns historical reviews of remediation effectiveness
 *
 * @param params - Query parameters with gapId
 * @returns Query result with reviews array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: reviews } = useEffectivenessReviews({
 *   gapId: 'gap-123'
 * });
 *
 * if (reviews) {
 *   console.log(`${reviews.length} effectiveness reviews`);
 *   const effective = reviews.filter(r => r.is_effective);
 *   console.log(`Effective: ${effective.length}/${reviews.length}`);
 * }
 * ```
 */
export function useEffectivenessReviews({ gapId, enabled = true }: UseEffectivenessReviewsParams) {
  return useQuery({
    queryKey: gapQueryKeys.effectivenessReviews(gapId),
    queryFn: () => complianceClient.getEffectivenessReviews(gapId),
    enabled: enabled && !!gapId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Gaps by Severity
 */
export interface UseGapsBySeverityParams {
  severity: GapSeverity;
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch gaps filtered by severity level
 * Returns all gaps of a specific severity (critical, high, medium, low)
 *
 * @param params - Query parameters with severity and organizationId
 * @returns Query result with gaps array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: criticalGaps } = useGapsBySeverity({
 *   severity: GapSeverity.CRITICAL,
 *   organizationId: 'org-123'
 * });
 *
 * if (criticalGaps) {
 *   console.log(`${criticalGaps.length} critical gaps found`);
 *   criticalGaps.forEach(gap => {
 *     console.log(`- ${gap.gap_description}`);
 *   });
 * }
 * ```
 */
export function useGapsBySeverity({
  severity,
  organizationId,
  enabled = true
}: UseGapsBySeverityParams) {
  return useQuery({
    queryKey: gapQueryKeys.bySeverity(severity, organizationId),
    queryFn: () => complianceClient.getGapsBySeverity(severity, organizationId),
    enabled: enabled && !!severity && !!organizationId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Overdue Gaps
 */
export interface UseGapsOverdueParams {
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch overdue compliance gaps
 * Returns gaps past their due date that are not resolved
 *
 * @param params - Query parameters with organizationId
 * @returns Query result with overdue gaps array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: overdueGaps } = useGapsOverdue({
 *   organizationId: 'org-123',
 *   enabled: true
 * });
 *
 * if (overdueGaps && overdueGaps.length > 0) {
 *   console.warn(`⚠️ ${overdueGaps.length} overdue gaps!`);
 *   overdueGaps.forEach(gap => {
 *     const daysPast = Math.floor(
 *       (Date.now() - new Date(gap.due_date!).getTime()) / (1000 * 60 * 60 * 24)
 *     );
 *     console.log(`- ${gap.gap_description}: ${daysPast} days overdue`);
 *   });
 * }
 * ```
 */
export function useGapsOverdue({ organizationId, enabled = true }: UseGapsOverdueParams) {
  return useQuery({
    queryKey: gapQueryKeys.overdue(organizationId),
    queryFn: () => {
      // Use the listGaps endpoint with appropriate filters
      // Backend should support filtering by overdue status
      return complianceClient.listGaps({
        organization_id: organizationId,
        status: 'overdue', // Assuming backend supports this filter
      });
    },
    enabled: enabled && !!organizationId,
    staleTime: 1 * 60 * 1000, // 1 minute (very short for overdue tracking)
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// COMPLIANCE GAPS - MUTATION HOOKS (9 hooks)
// ============================================================================

/**
 * Hook Options - Create Gap
 */
export interface UseCreateGapOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create a new compliance gap
 * Automatically invalidates gap list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createGap = useCreateComplianceGap({
 *   onSuccess: (gap) => {
 *     console.log(`Gap "${gap.gap_description}" created`);
 *     router.push(`/compliance/gaps/${gap.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create gap: ${error.message}`);
 *   }
 * });
 *
 * createGap.mutate({
 *   organization_id: 'org-123',
 *   requirement_id: 'req-456',
 *   assessment_id: 'assessment-789',
 *   gap_description: 'Insufficient documentation of incident response procedures',
 *   severity: GapSeverity.HIGH,
 *   priority: GapPriority.P2_HIGH,
 *   current_coverage: 40,
 *   target_coverage: 100,
 *   assigned_to: 'user-123',
 *   due_date: '2025-12-31',
 *   remediation_actions: [{
 *     description: 'Create comprehensive incident response documentation',
 *     responsible: 'Security Manager',
 *     deadline: '2025-11-30',
 *     status: ActionStatus.PENDING
 *   }]
 * });
 * ```
 */
export function useCreateComplianceGap(options: UseCreateGapOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, any>({
    mutationFn: (data: any) =>
      complianceClient.createGap(data),

    onSuccess: (data) => {
      // Invalidate gap lists to refetch with new gap
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate assessment results if associated
      if (data.assessment_id) {
        queryClient.invalidateQueries({
          queryKey: assessmentQueryKeys.results(data.assessment_id),
        });
      }

      // Invalidate compliance check
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Optimistically set the single gap cache
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Gap
 */
export interface UseUpdateGapOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Gap Parameters
 */
export interface UpdateGapParams {
  gapId: string;
  data: ApiComplianceGapUpdate;
}

/**
 * Hook to update an existing compliance gap
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateGap = useUpdateComplianceGap({
 *   onSuccess: (gap) => {
 *     console.log(`Gap updated: ${gap.gap_description}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * updateGap.mutate({
 *   gapId: 'gap-123',
 *   data: {
 *     current_coverage: 60,
 *     status: GapState.IN_REMEDIATION,
 *     remediation_plan: 'Updated remediation approach with additional resources'
 *   }
 * });
 * ```
 */
export function useUpdateComplianceGap(options: UseUpdateGapOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, UpdateGapParams>({
    mutationFn: ({ gapId, data }) =>
      complianceClient.updateGap(gapId, data),

    onSuccess: (data) => {
      // Invalidate gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the specific gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.id!),
      });

      // Invalidate severity filters
      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'severity'],
      });

      // Invalidate overdue gaps in case status changed
      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'overdue'],
      });

      // Invalidate assessment results if associated
      if (data.assessment_id) {
        queryClient.invalidateQueries({
          queryKey: assessmentQueryKeys.results(data.assessment_id),
        });
      }

      // Update the cached gap data
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Delete Gap
 */
export interface UseDeleteGapOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete a compliance gap
 * Automatically invalidates gap cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteGap = useDeleteComplianceGap({
 *   onSuccess: () => {
 *     console.log('Gap deleted successfully');
 *     router.push('/compliance/gaps');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * deleteGap.mutate('gap-123');
 * ```
 */
export function useDeleteComplianceGap(options: UseDeleteGapOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: (gapId: string) =>
      complianceClient.deleteGap(gapId),

    onSuccess: (_, gapId) => {
      // Invalidate all gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the deleted gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(gapId),
      });

      // Invalidate all severity and overdue queries
      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'severity'],
      });

      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'overdue'],
      });

      // Invalidate compliance checks
      queryClient.invalidateQueries({
        queryKey: [...assessmentQueryKeys.all, 'check'],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: gapQueryKeys.detail(gapId),
      });

      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Resolve Gap
 */
export interface UseResolveGapOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Resolve Gap Parameters
 */
export interface ResolveGapParams {
  gapId: string;
  resolutionNotes: string;
}

/**
 * Hook to resolve a compliance gap
 * Marks gap as resolved and records resolution details
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const resolveGap = useResolveGap({
 *   onSuccess: (gap) => {
 *     console.log(`Gap resolved: ${gap.gap_description}`);
 *     console.log(`Resolved at: ${gap.resolved_at}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to resolve gap: ${error.message}`);
 *   }
 * });
 *
 * resolveGap.mutate({
 *   gapId: 'gap-123',
 *   resolutionNotes: 'Comprehensive incident response documentation completed and approved by management'
 * });
 * ```
 */
export function useResolveGap(options: UseResolveGapOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, ResolveGapParams>({
    mutationFn: ({ gapId, resolutionNotes }) =>
      complianceClient.resolveGap(gapId, resolutionNotes),

    onSuccess: (data) => {
      // Invalidate gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the specific gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.id!),
      });

      // Invalidate severity and overdue queries
      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'severity'],
      });

      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'overdue'],
      });

      // Invalidate compliance check - resolution affects compliance score
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Update the cached gap data
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Reopen Gap
 */
export interface UseReopenGapOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Reopen Gap Parameters
 */
export interface ReopenGapParams {
  gapId: string;
  reason: string;
}

/**
 * Hook to reopen a resolved compliance gap
 * Changes status back to identified/reopened with reason
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const reopenGap = useReopenGap({
 *   onSuccess: (gap) => {
 *     console.log(`Gap reopened: ${gap.gap_description}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to reopen gap: ${error.message}`);
 *   }
 * });
 *
 * reopenGap.mutate({
 *   gapId: 'gap-123',
 *   reason: 'Follow-up audit found documentation incomplete in certain areas'
 * });
 * ```
 */
export function useReopenGap(options: UseReopenGapOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, ReopenGapParams>({
    mutationFn: ({ gapId, reason }) =>
      complianceClient.reopenGap(gapId, reason),

    onSuccess: (data) => {
      // Invalidate gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the specific gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.id!),
      });

      // Invalidate severity and overdue queries
      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'severity'],
      });

      queryClient.invalidateQueries({
        queryKey: [...gapQueryKeys.all, 'overdue'],
      });

      // Invalidate compliance check - reopening affects compliance score
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Update the cached gap data
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Start Gap Remediation
 */
export interface UseStartGapRemediationOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to start remediation process for a gap
 * Changes status to in_remediation
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const startRemediation = useStartGapRemediation({
 *   onSuccess: (gap) => {
 *     console.log(`Remediation started for: ${gap.gap_description}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to start remediation: ${error.message}`);
 *   }
 * });
 *
 * startRemediation.mutate('gap-123');
 * ```
 */
export function useStartGapRemediation(options: UseStartGapRemediationOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, string>({
    mutationFn: (gapId) =>
      complianceClient.startGapRemediation(gapId),

    onSuccess: (data) => {
      // Invalidate gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the specific gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.id!),
      });

      // Update the cached gap data
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Gap Progress
 */
export interface UseUpdateGapProgressOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Gap Progress Parameters
 */
export interface UpdateGapProgressParams {
  gapId: string;
  progress: number;
}

/**
 * Hook to update remediation progress for a gap
 * Updates progress percentage (0-100)
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateProgress = useUpdateGapProgress({
 *   onSuccess: (gap) => {
 *     console.log(`Progress updated: ${gap.current_coverage}%`);
 *   },
 *   onError: (error) => {
 *     console.error(`Progress update failed: ${error.message}`);
 *   }
 * });
 *
 * updateProgress.mutate({
 *   gapId: 'gap-123',
 *   progress: 75
 * });
 * ```
 */
export function useUpdateGapProgress(options: UseUpdateGapProgressOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, UpdateGapProgressParams>({
    mutationFn: ({ gapId, progress }) =>
      complianceClient.updateGapProgress(gapId, progress),

    onSuccess: (data) => {
      // Invalidate gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the specific gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.id!),
      });

      // Update the cached gap data
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Verify Gap
 */
export interface UseVerifyGapOptions {
  onSuccess?: (gap: ComplianceGap) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Verify Gap Parameters
 */
export interface VerifyGapParams {
  gapId: string;
  verificationNotes: string;
}

/**
 * Hook to verify gap closure
 * Marks gap as verified and records verification details
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const verifyGap = useVerifyGap({
 *   onSuccess: (gap) => {
 *     console.log(`Gap verified: ${gap.gap_description}`);
 *     console.log(`Verified by: ${gap.verified_by}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Verification failed: ${error.message}`);
 *   }
 * });
 *
 * verifyGap.mutate({
 *   gapId: 'gap-123',
 *   verificationNotes: 'Reviewed all documentation. Incident response procedures meet requirements.'
 * });
 * ```
 */
export function useVerifyGap(options: UseVerifyGapOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceGap, Error, VerifyGapParams>({
    mutationFn: ({ gapId, verificationNotes }) =>
      complianceClient.verifyGap(gapId, verificationNotes),

    onSuccess: (data) => {
      // Invalidate gap lists
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.lists(),
      });

      // Invalidate the specific gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.id!),
      });

      // Invalidate compliance check - verification affects compliance score
      queryClient.invalidateQueries({
        queryKey: assessmentQueryKeys.compliance(data.organization_id),
      });

      // Update the cached gap data
      if (data.id) {
        queryClient.setQueryData(
          gapQueryKeys.detail(data.id),
          data
        );
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Create Gap RCA
 */
export interface UseCreateGapRCAOptions {
  onSuccess?: (rca: RCAAnalysis) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create root cause analysis for a gap
 * Documents RCA method, findings, and recommendations
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createRCA = useCreateGapRCA({
 *   onSuccess: (rca) => {
 *     console.log(`RCA created using ${rca.method}`);
 *     console.log(`Root causes: ${rca.root_causes.length}`);
 *   },
 *   onError: (error) => {
 *     console.error(`RCA creation failed: ${error.message}`);
 *   }
 * });
 *
 * createRCA.mutate({
 *   gap_id: 'gap-123',
 *   method: RCAMethod.FIVE_WHYS,
 *   analysis_data: {
 *     why1: 'Why was documentation incomplete?',
 *     answer1: 'No standard template was available',
 *     why2: 'Why was no template available?',
 *     answer2: 'Documentation standards were not established'
 *   },
 *   root_causes: ['Lack of standardized documentation framework'],
 *   contributing_factors: ['Insufficient training', 'No documentation review process'],
 *   recommendations: [
 *     'Establish documentation standards',
 *     'Create templates for all required documents',
 *     'Implement peer review process'
 *   ]
 * });
 * ```
 */
export function useCreateGapRCA(options: UseCreateGapRCAOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<RCAAnalysis, Error, ApiRCAAnalysisCreate>({
    mutationFn: (data) =>
      complianceClient.createGapRCA(data),

    onSuccess: (data) => {
      // Invalidate the gap's RCA query
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.rca(data.gap_id),
      });

      // Invalidate the gap detail
      queryClient.invalidateQueries({
        queryKey: gapQueryKeys.detail(data.gap_id),
      });

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// PREFETCH UTILITIES
// ============================================================================

/**
 * Prefetch utility for assessments list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/assessments`}
 *   onMouseEnter={() => prefetchAssessments(queryClient, 'org-123')}
 * >
 *   View Assessments
 * </Link>
 * ```
 */
export function prefetchAssessments(
  queryClient: QueryClient,
  organizationId: string,
  status?: string
) {
  return queryClient.prefetchQuery({
    queryKey: assessmentQueryKeys.list(organizationId, status),
    queryFn: () => complianceClient.listAssessments({
      organization_id: organizationId,
      status,
    }),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single assessment
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/assessments/${assessmentId}`}
 *   onMouseEnter={() => prefetchAssessment(queryClient, assessmentId)}
 * >
 *   View Assessment Details
 * </Link>
 * ```
 */
export function prefetchAssessment(queryClient: QueryClient, assessmentId: string) {
  return queryClient.prefetchQuery({
    queryKey: assessmentQueryKeys.detail(assessmentId),
    queryFn: () => complianceClient.getAssessment(assessmentId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for gaps list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/gaps`}
 *   onMouseEnter={() => prefetchGaps(queryClient, 'org-123')}
 * >
 *   View Gaps
 * </Link>
 * ```
 */
export function prefetchGaps(
  queryClient: QueryClient,
  organizationId: string,
  status?: string
) {
  return queryClient.prefetchQuery({
    queryKey: gapQueryKeys.list(organizationId, status),
    queryFn: () => complianceClient.listGaps({
      organization_id: organizationId,
      status,
    }),
    staleTime: 3 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single gap
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/gaps/${gapId}`}
 *   onMouseEnter={() => prefetchGap(queryClient, gapId)}
 * >
 *   View Gap Details
 * </Link>
 * ```
 */
export function prefetchGap(queryClient: QueryClient, gapId: string) {
  return queryClient.prefetchQuery({
    queryKey: gapQueryKeys.detail(gapId),
    queryFn: () => complianceClient.getGap(gapId),
    staleTime: 3 * 60 * 1000,
  });
}
