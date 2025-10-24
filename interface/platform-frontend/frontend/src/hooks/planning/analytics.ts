/**
 * Planning Module - Analytics & Integration Hooks
 * React Query hooks for planning analytics and cross-module integration
 *
 * Created: 2025-10-21
 * Agent: 6/6 (Planning Module Round 2)
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  PlanCoverage,
  MaturityAssessment,
  PlanningGap,
  TimelineEvent,
  ExecutiveSummary,
  BIAAlignment,
  RiskAlignment,
  PlanDependency,
  SyncRequest,
  SyncResult,
} from '@/lib/api/planning-client';
import toast from 'react-hot-toast';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for planning analytics
 * Provides centralized query key management for analytics and integration
 */
export const analyticsKeys = {
  all: ['planning', 'analytics'] as const,
  coverage: (orgId: string) => ['planning', 'coverage', orgId] as const,
  maturity: (orgId: string) => ['planning', 'maturity', orgId] as const,
  gaps: (orgId: string) => ['planning', 'gaps', orgId] as const,
  timeline: (orgId: string, start?: string, end?: string) =>
    ['planning', 'timeline', orgId, start, end] as const,
  executiveSummary: (orgId: string) => ['planning', 'executive-summary', orgId] as const,
  biaAlignment: (orgId: string) => ['planning', 'bia-alignment', orgId] as const,
  riskAlignment: (orgId: string) => ['planning', 'risk-alignment', orgId] as const,
  dependencies: (planId: string) => ['planning', 'dependencies', planId] as const,
};

// ==================== TYPES ====================

// Analytics Hook Options
export interface UsePlanCoverageParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseMaturityAssessmentParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UsePlanningGapsParams {
  organizationId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseImplementationTimelineParams {
  organizationId: string;
  startDate?: string;
  endDate?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseExecutiveSummaryParams {
  organizationId: string;
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

export interface UsePlanDependenciesParams {
  planId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

// Mutation Options
export interface UseSyncPlanningDataOptions {
  onSuccess?: (result: SyncResult) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface SyncPlanningDataParams {
  organizationId: string;
  request: SyncRequest;
}

// ==================== ANALYTICS HOOKS ====================

/**
 * Hook to fetch plan coverage analysis
 * Shows which ISO 22301 controls are covered by plans
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with coverage data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: coverage, isLoading, error } = usePlanCoverage({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (coverage) {
 *   console.log('Coverage percentage:', coverage.coveragePercentage);
 *   console.log('Covered controls:', coverage.coveredControls);
 *   console.log('Uncovered controls:', coverage.uncoveredControls);
 * }
 * ```
 */
export function usePlanCoverage({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UsePlanCoverageParams) {
  return useQuery({
    queryKey: analyticsKeys.coverage(organizationId),
    queryFn: async (): Promise<PlanCoverage> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getPlanCoverage(organizationId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/coverage?organizationId=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch plan coverage');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - coverage changes moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch maturity assessment
 * Evaluates organizational BCM maturity level based on plans and controls
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with maturity assessment data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: maturity, isLoading, error } = useMaturityAssessment({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (maturity) {
 *   console.log('Maturity level:', maturity.level); // 1-5
 *   console.log('Score:', maturity.score);
 *   console.log('Strengths:', maturity.strengths);
 *   console.log('Improvement areas:', maturity.improvementAreas);
 * }
 * ```
 */
export function useMaturityAssessment({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseMaturityAssessmentParams) {
  return useQuery({
    queryKey: analyticsKeys.maturity(organizationId),
    queryFn: async (): Promise<MaturityAssessment> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getMaturityAssessment(organizationId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/maturity?organizationId=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch maturity assessment');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - maturity changes slowly
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch planning gaps analysis
 * Identifies missing or incomplete controls and plans
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with gaps data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: gaps, isLoading, error } = usePlanningGaps({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (gaps) {
 *   console.log('Total gaps:', gaps.totalGaps);
 *   console.log('Critical gaps:', gaps.criticalGaps);
 *   console.log('Gap details:', gaps.gaps);
 * }
 * ```
 */
export function usePlanningGaps({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UsePlanningGapsParams) {
  return useQuery({
    queryKey: analyticsKeys.gaps(organizationId),
    queryFn: async (): Promise<PlanningGap[]> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getPlanningGaps(organizationId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/gaps?organizationId=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch planning gaps');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - gaps change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch implementation timeline
 * Shows planned and actual implementation dates for strategies and actions
 *
 * @param params - Query parameters including organizationId and optional date range
 * @returns Query result with timeline events, loading state, error
 *
 * @example
 * ```tsx
 * const { data: timeline, isLoading, error } = useImplementationTimeline({
 *   organizationId: 'org-123',
 *   startDate: '2025-01-01',
 *   endDate: '2025-12-31',
 *   enabled: true,
 * });
 *
 * if (timeline) {
 *   console.log('Timeline events:', timeline.events);
 *   console.log('Upcoming milestones:', timeline.upcomingMilestones);
 *   console.log('Overdue items:', timeline.overdueItems);
 * }
 * ```
 */
export function useImplementationTimeline({
  organizationId,
  startDate,
  endDate,
  enabled = true,
  staleTime,
  gcTime,
}: UseImplementationTimelineParams) {
  return useQuery({
    queryKey: analyticsKeys.timeline(organizationId, startDate, endDate),
    queryFn: async (): Promise<TimelineEvent[]> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getImplementationTimeline(organizationId, startDate, endDate);

      // Placeholder implementation
      const params = new URLSearchParams({ organizationId });
      if (startDate) params.append('startDate', startDate);
      if (endDate) params.append('endDate', endDate);

      const response = await fetch(`/api/planning/timeline?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch implementation timeline');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - timeline changes frequently
    staleTime: staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: gcTime ?? 15 * 60 * 1000, // 15 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch executive summary
 * Provides high-level overview for leadership and stakeholders
 *
 * @param params - Query parameters including organizationId
 * @returns Query result with executive summary data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: summary, isLoading, error } = useExecutiveSummary({
 *   organizationId: 'org-123',
 *   enabled: true,
 * });
 *
 * if (summary) {
 *   console.log('Overall status:', summary.overallStatus);
 *   console.log('Key metrics:', summary.keyMetrics);
 *   console.log('Critical issues:', summary.criticalIssues);
 *   console.log('Recommendations:', summary.recommendations);
 * }
 * ```
 */
export function useExecutiveSummary({
  organizationId,
  enabled = true,
  staleTime,
  gcTime,
}: UseExecutiveSummaryParams) {
  return useQuery({
    queryKey: analyticsKeys.executiveSummary(organizationId),
    queryFn: async (): Promise<ExecutiveSummary> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getExecutiveSummary(organizationId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/executive-summary?organizationId=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch executive summary');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - summaries change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== INTEGRATION HOOKS ====================

/**
 * Hook to fetch BIA alignment analysis
 * Shows how BCM plans align with Business Impact Analysis results
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
 *   console.log('Aligned processes:', alignment.alignedProcesses);
 *   console.log('Unaligned processes:', alignment.unalignedProcesses);
 *   console.log('Coverage gaps:', alignment.coverageGaps);
 *   console.log('RTO/RPO alignment:', alignment.rtoRpoAlignment);
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
    queryFn: async (): Promise<BIAAlignment> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getBIAAlignment(organizationId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/bia-alignment?organizationId=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch BIA alignment');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - alignment changes slowly
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch risk alignment analysis
 * Shows how BCM strategies address identified risks
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
 *   console.log('Covered risks:', alignment.coveredRisks);
 *   console.log('Uncovered risks:', alignment.uncoveredRisks);
 *   console.log('Risk mitigation strategies:', alignment.mitigationStrategies);
 *   console.log('Effectiveness score:', alignment.effectivenessScore);
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
    queryFn: async (): Promise<RiskAlignment> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getRiskAlignment(organizationId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/risk-alignment?organizationId=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch risk alignment');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - alignment changes slowly
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch plan dependencies
 * Shows dependencies between plans, strategies, and actions
 *
 * @param params - Query parameters including planId
 * @returns Query result with dependency data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: dependencies, isLoading, error } = usePlanDependencies({
 *   planId: 'plan-123',
 *   enabled: true,
 * });
 *
 * if (dependencies) {
 *   console.log('Upstream dependencies:', dependencies.upstream);
 *   console.log('Downstream dependencies:', dependencies.downstream);
 *   console.log('Circular dependencies:', dependencies.circularDependencies);
 *   console.log('Critical path:', dependencies.criticalPath);
 * }
 * ```
 */
export function usePlanDependencies({
  planId,
  enabled = true,
  staleTime,
  gcTime,
}: UsePlanDependenciesParams) {
  return useQuery({
    queryKey: analyticsKeys.dependencies(planId),
    queryFn: async (): Promise<PlanDependency> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.getPlanDependencies(planId);

      // Placeholder implementation
      const response = await fetch(`/api/planning/dependencies?planId=${planId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch plan dependencies');
      }
      return response.json();
    },

    // Enable/disable query
    enabled: enabled && !!planId,

    // Caching strategy - dependencies change slowly
    staleTime: staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: gcTime ?? 60 * 60 * 1000, // 60 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== MUTATION HOOKS ====================

/**
 * Hook to sync planning data with other modules
 * Synchronizes plans with BIA, Risk, and other integrated systems
 *
 * @param options - Callback options for success, error, and settled states
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const syncPlanning = useSyncPlanningData({
 *   onSuccess: (result) => {
 *     toast.success(`Sync completed: ${result.syncedItems} items synchronized`);
 *     console.log('Sync summary:', result.summary);
 *   },
 *   onError: (error) => {
 *     toast.error(`Sync failed: ${error.message}`);
 *   },
 * });
 *
 * // Execute sync operation
 * syncPlanning.mutate({
 *   organizationId: 'org-123',
 *   request: {
 *     modules: ['bia', 'risk'],
 *     fullSync: false,
 *     includeArchived: false,
 *   },
 * });
 * ```
 */
export function useSyncPlanningData(options: UseSyncPlanningDataOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ organizationId, request }: SyncPlanningDataParams): Promise<SyncResult> => {
      // TODO: Replace with actual API call when planning-client is ready
      // return planningClient.syncPlanningData(organizationId, request);

      // Placeholder implementation
      const response = await fetch(`/api/planning/sync?organizationId=${organizationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error('Failed to sync planning data');
      }

      return response.json();
    },

    onSuccess: (data, variables) => {
      // Invalidate all planning-related caches after successful sync
      queryClient.invalidateQueries({ queryKey: ['planning'] });
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
      queryClient.invalidateQueries({ queryKey: ['actions'] });

      // Also invalidate related module caches if synced
      if (variables.request.sync_bia) {
        queryClient.invalidateQueries({ queryKey: ['bia'] });
      }
      if (variables.request.sync_risks) {
        queryClient.invalidateQueries({ queryKey: ['risks'] });
      }

      // Show success notification
      const totalSynced = data.processes_synced + data.risks_synced + data.assets_synced;
      toast.success(
        `Planning data synchronized successfully. ${totalSynced} items updated.`
      );

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Sync failed: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration - sync operations are important but expensive
    retry: 1,
    retryDelay: 2000,
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Helper function to calculate coverage percentage
 * @param coverage - Plan coverage data
 * @returns Coverage percentage (0-100)
 */
export function calculateCoveragePercentage(coverage: PlanCoverage): number {
  if (!coverage || typeof coverage !== 'object') return 0;

  const total = (coverage as any).totalControls || 0;
  const covered = (coverage as any).coveredControls?.length || 0;

  if (total === 0) return 0;
  return Math.round((covered / total) * 100);
}

/**
 * Helper function to get maturity level description
 * @param level - Maturity level (1-5)
 * @returns Level description
 */
export function getMaturityLevelDescription(level: number): string {
  const descriptions: Record<number, string> = {
    1: 'Initial - Ad-hoc processes',
    2: 'Developing - Documented processes',
    3: 'Defined - Standardized processes',
    4: 'Managed - Measured processes',
    5: 'Optimizing - Continuous improvement',
  };

  return descriptions[level] || 'Unknown';
}

/**
 * Helper function to categorize gaps by severity
 * @param gaps - Planning gaps array
 * @returns Gaps categorized by severity
 */
export function categorizeGapsBySeverity(gaps: PlanningGap[]): {
  critical: PlanningGap[];
  high: PlanningGap[];
  medium: PlanningGap[];
  low: PlanningGap[];
} {
  if (!Array.isArray(gaps)) {
    return { critical: [], high: [], medium: [], low: [] };
  }

  return {
    critical: gaps.filter((g) => (g as any).severity === 'critical'),
    high: gaps.filter((g) => (g as any).severity === 'high'),
    medium: gaps.filter((g) => (g as any).severity === 'medium'),
    low: gaps.filter((g) => (g as any).severity === 'low'),
  };
}

/**
 * Helper function to get upcoming timeline events
 * @param events - Timeline events array
 * @param days - Number of days to look ahead
 * @returns Upcoming events within specified days
 */
export function getUpcomingEvents(events: TimelineEvent[], days: number = 30): TimelineEvent[] {
  if (!Array.isArray(events)) return [];

  const now = new Date();
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + days);

  return events.filter((event) => {
    const eventDate = new Date((event as any).date || (event as any).dueDate);
    return eventDate >= now && eventDate <= futureDate;
  });
}

/**
 * Helper function to get overdue timeline events
 * @param events - Timeline events array
 * @returns Overdue events
 */
export function getOverdueEvents(events: TimelineEvent[]): TimelineEvent[] {
  if (!Array.isArray(events)) return [];

  const now = new Date();

  return events.filter((event) => {
    const eventDate = new Date((event as any).dueDate);
    const status = (event as any).status;
    return eventDate < now && status !== 'completed';
  });
}

/**
 * Helper function to calculate alignment score
 * @param alignment - Alignment data (BIA or Risk)
 * @returns Alignment score (0-100)
 */
export function calculateAlignmentScore(alignment: BIAAlignment | RiskAlignment): number {
  if (!alignment || typeof alignment !== 'object') return 0;

  const total = (alignment as any).totalItems || 0;
  const aligned = (alignment as any).alignedItems?.length || 0;

  if (total === 0) return 0;
  return Math.round((aligned / total) * 100);
}

/**
 * Helper function to detect circular dependencies
 * @param dependencies - Plan dependencies
 * @returns True if circular dependencies detected
 */
export function hasCircularDependencies(dependencies: PlanDependency): boolean {
  if (!dependencies || typeof dependencies !== 'object') return false;

  const circular = (dependencies as any).circularDependencies;
  return Array.isArray(circular) && circular.length > 0;
}

/**
 * Helper function to get critical path from dependencies
 * @param dependencies - Plan dependencies
 * @returns Critical path array
 */
export function getCriticalPath(dependencies: PlanDependency): string[] {
  if (!dependencies || typeof dependencies !== 'object') return [];

  const criticalPath = (dependencies as any).criticalPath;
  return Array.isArray(criticalPath) ? criticalPath : [];
}
