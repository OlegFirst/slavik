/**
 * Response Module - Dashboard & Analytics Hooks
 * React Query hooks for incident response dashboard, analytics, and reporting
 *
 * Created: 2025-10-24
 * Agent: 27 (Response Module - Dashboard & Analytics)
 *
 * Total Hooks: 12
 * - Dashboard Queries: 4
 * - Communications: 2
 * - Recovery Metrics: 3
 * - Reporting: 2
 * - Health: 1
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { responseClient } from '@/lib/api/response-client';
import type {
  IncidentMetrics,
  ResponseTrendsResponse,
} from '@/types/response';
import type {
  ResponseDashboard,
  CommunicationRecord,
  CommunicationRecordCreate,
  RecoveryObjective,
  RecoveryObjectiveCreate,
  RecoveryObjectiveUpdate,
  IncidentReport,
} from '@/types/response-compat';
import {
  toResponseDashboard,
  toCommunicationRecord,
  toCommunicationLogCreate,
  toRecoveryObjective,
  toRecoveryMetricsCreate,
  toRecoveryMetricsUpdate,
  toIncidentReport,
} from '@/types/response-compat';
import toast from 'react-hot-toast';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for response dashboard and analytics
 * Provides centralized query key management for dashboard operations
 */
export const dashboardKeys = {
  all: ['response', 'dashboard'] as const,
  overview: (orgId: string) => ['response', 'dashboard-overview', orgId] as const,
  metrics: (orgId: string) => ['response', 'org-metrics', orgId] as const,
  statistics: (orgId: string, period?: number) => ['response', 'statistics', orgId, period] as const,
  trends: (orgId: string, days?: number) => ['response', 'trends', orgId, days] as const,
  communications: (incidentId: string) => ['response', 'communications', incidentId] as const,
  recoveryMetrics: (incidentId: string) => ['response', 'recovery-metrics', incidentId] as const,
  report: (incidentId: string) => ['response', 'report', incidentId] as const,
  health: () => ['response', 'health'] as const,
};

// ==================== TYPES ====================

// Dashboard Hook Options
export interface UseIncidentDashboardParams {
  fromDate?: string;
  toDate?: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseOrganizationMetricsParams {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseIncidentStatisticsParams {
  organizationId: string;
  periodDays?: number;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseIncidentTrendsParams {
  organizationId: string;
  periodDays?: number;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

// Communications Hook Options
export interface UseIncidentCommunicationsParams {
  incidentId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseLogCommunicationOptions {
  onSuccess?: (communication: CommunicationRecord) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface LogCommunicationParams {
  incidentId: string;
  data: CommunicationRecordCreate;
}

// Recovery Metrics Hook Options
export interface UseIncidentMetricsParams {
  incidentId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseAddRecoveryMetricsOptions {
  onSuccess?: (metrics: RecoveryObjective) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface AddRecoveryMetricsParams {
  incidentId: string;
  data: RecoveryObjectiveCreate;
}

export interface UseUpdateRecoveryMetricsOptions {
  onSuccess?: (metrics: RecoveryObjective) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UpdateRecoveryMetricsParams {
  metricsId: string;
  data: RecoveryObjectiveUpdate;
}

// Reporting Hook Options
export interface UseIncidentReportParams {
  incidentId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface UseGenerateReportOptions {
  onSuccess?: (report: IncidentReport) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

// Health Hook Options
export interface UseHealthCheckParams {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchInterval?: number;
}

// ==================== DASHBOARD QUERY HOOKS ====================

/**
 * Hook to fetch incident response dashboard
 * Provides comprehensive dashboard data for incident response overview
 *
 * @param params - Query parameters including optional date range
 * @returns Query result with dashboard data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: dashboard, isLoading, error } = useIncidentDashboard({
 *   fromDate: '2025-01-01',
 *   toDate: '2025-12-31',
 *   enabled: true,
 * });
 *
 * if (dashboard) {
 *   console.log('Active incidents:', dashboard.active_incidents);
 *   console.log('Critical incidents:', dashboard.critical_incidents);
 *   console.log('RTO compliance:', dashboard.rto_compliance_rate);
 *   console.log('Recent incidents:', dashboard.recent_incidents);
 * }
 * ```
 */
export function useIncidentDashboard({
  fromDate,
  toDate,
  enabled = true,
  staleTime,
  gcTime,
}: UseIncidentDashboardParams = {}) {
  return useQuery({
    queryKey: dashboardKeys.overview(fromDate || toDate || 'current'),
    queryFn: async (): Promise<ResponseDashboard> => {
      const dashboard = await responseClient.getIncidentDashboard(fromDate, toDate);
      return toResponseDashboard(dashboard);
    },

    // Enable/disable query
    enabled,

    // Caching strategy - dashboard changes frequently
    staleTime: staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: gcTime ?? 15 * 60 * 1000, // 15 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch organization-level incident metrics
 * Provides MTTR, MTBF, and other org-wide performance metrics
 *
 * @param params - Query parameters
 * @returns Query result with organization metrics data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: metrics, isLoading, error } = useOrganizationMetrics({
 *   enabled: true,
 * });
 *
 * if (metrics) {
 *   console.log('Total incidents:', metrics.total_incidents);
 *   console.log('MTTR:', metrics.mttr);
 *   console.log('MTBF:', metrics.mtbf);
 *   console.log('Incident trend:', metrics.trend_percentage);
 * }
 * ```
 */
export function useOrganizationMetrics({
  enabled = true,
  staleTime,
  gcTime,
}: UseOrganizationMetricsParams = {}) {
  return useQuery({
    queryKey: dashboardKeys.metrics('organization'),
    queryFn: async () => {
      return responseClient.getOrganizationMetrics();
    },

    // Enable/disable query
    enabled,

    // Caching strategy - org metrics change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch incident statistics by period
 * Provides aggregated statistics for a specific time period
 *
 * @param params - Query parameters including organizationId and period
 * @returns Query result with statistics data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: stats, isLoading, error } = useIncidentStatistics({
 *   organizationId: 'org-123',
 *   periodDays: 30,
 *   enabled: true,
 * });
 *
 * if (stats) {
 *   console.log('Incidents this period:', stats.active_incidents);
 *   console.log('Average resolution time:', stats.avg_resolution_time_hours);
 *   console.log('Incidents by status:', stats.incidents_by_status);
 * }
 * ```
 */
export function useIncidentStatistics({
  organizationId,
  periodDays = 30,
  enabled = true,
  staleTime,
  gcTime,
}: UseIncidentStatisticsParams) {
  return useQuery({
    queryKey: dashboardKeys.statistics(organizationId, periodDays),
    queryFn: async (): Promise<ResponseDashboard> => {
      const toDate = new Date().toISOString();
      const fromDate = new Date(Date.now() - periodDays * 24 * 60 * 60 * 1000).toISOString();
      const dashboard = await responseClient.getIncidentDashboard(fromDate, toDate);
      return toResponseDashboard(dashboard);
    },

    // Enable/disable query
    enabled: enabled && !!organizationId,

    // Caching strategy - statistics change moderately
    staleTime: staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to fetch incident trends over time
 * Shows historical trends in incident response metrics
 *
 * @param params - Query parameters including organizationId and period
 * @returns Query result with trends data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: trends, isLoading, error } = useIncidentTrends({
 *   organizationId: 'org-123',
 *   periodDays: 90,
 *   enabled: true,
 * });
 *
 * if (trends) {
 *   console.log('Trend direction:', trends.trend);
 *   console.log('Data points:', trends.data_points);
 *   console.log('Average resolution time:', trends.summary.avg_resolution_hours);
 * }
 * ```
 */
export function useIncidentTrends({
  organizationId,
  periodDays = 90,
  enabled = true,
  staleTime,
  gcTime,
}: UseIncidentTrendsParams) {
  return useQuery({
    queryKey: dashboardKeys.trends(organizationId, periodDays),
    queryFn: async (): Promise<ResponseTrendsResponse> => {
      // Get dashboard data for the period
      const toDate = new Date().toISOString();
      const fromDate = new Date(Date.now() - periodDays * 24 * 60 * 60 * 1000).toISOString();
      const apiDashboard = await responseClient.getIncidentDashboard(fromDate, toDate);
      const dashboard = toResponseDashboard(apiDashboard);

      // Transform to trends format
      // This is a simplified version - real implementation would have dedicated endpoint
      return {
        period_days: periodDays,
        trend: 'stable', // Would be calculated from historical data
        data_points: [
          {
            date: toDate,
            incidents_count: dashboard.active_incidents,
            critical_count: dashboard.critical_incidents,
            high_count: dashboard.high_severity_incidents,
            avg_resolution_hours: apiDashboard.avg_resolution_hours || 0,
            rto_compliance_rate: dashboard.rto_compliance_rate || 0,
          },
        ],
        summary: {
          total_incidents: dashboard.active_incidents,
          avg_resolution_hours: apiDashboard.avg_resolution_hours || 0,
          rto_compliance_rate: dashboard.rto_compliance_rate || 0,
          most_common_type: dashboard.trending_types[0]?.type || 'system_failure',
        },
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

// ==================== COMMUNICATIONS HOOKS ====================

/**
 * Hook to fetch incident communications
 * Lists all communications for a specific incident
 *
 * @param params - Query parameters including incidentId
 * @returns Query result with communications data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: communications, isLoading, error } = useIncidentCommunications({
 *   incidentId: 'incident-123',
 *   enabled: true,
 * });
 *
 * if (communications) {
 *   console.log('Total communications:', communications.length);
 *   console.log('Stakeholder notifications:', communications.filter(c => c.is_stakeholder_notification));
 * }
 * ```
 */
export function useIncidentCommunications({
  incidentId,
  enabled = true,
  staleTime,
  gcTime,
}: UseIncidentCommunicationsParams) {
  return useQuery({
    queryKey: dashboardKeys.communications(incidentId),
    queryFn: async (): Promise<CommunicationRecord[]> => {
      const logs = await responseClient.listIncidentCommunications(incidentId);
      return logs.map(toCommunicationRecord);
    },

    // Enable/disable query
    enabled: enabled && !!incidentId,

    // Caching strategy - communications change frequently
    staleTime: staleTime ?? 1 * 60 * 1000, // 1 minute
    gcTime: gcTime ?? 10 * 60 * 1000, // 10 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to log new communication for an incident
 * Mutation for creating communication records
 *
 * @param options - Callback options for success, error, and settled states
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const logCommunication = useLogCommunication({
 *   onSuccess: (communication) => {
 *     toast.success('Communication logged successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to log communication: ${error.message}`);
 *   },
 * });
 *
 * // Log a communication
 * logCommunication.mutate({
 *   incidentId: 'incident-123',
 *   data: {
 *     communication_type: 'email',
 *     subject: 'Incident Status Update',
 *     content: 'Current status of the incident...',
 *     sender: 'John Doe',
 *     recipients: ['stakeholder1@example.com'],
 *     is_stakeholder_notification: true,
 *   },
 * });
 * ```
 */
export function useLogCommunication(options: UseLogCommunicationOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ incidentId, data }: LogCommunicationParams): Promise<CommunicationRecord> => {
      const logCreate = toCommunicationLogCreate(data);
      const log = await responseClient.logCommunication(incidentId, logCreate);
      return toCommunicationRecord(log);
    },

    onSuccess: (data, variables) => {
      // Invalidate communications cache
      queryClient.invalidateQueries({ queryKey: dashboardKeys.communications(variables.incidentId) });

      // Also invalidate incident details cache
      queryClient.invalidateQueries({ queryKey: ['response', 'incidents', variables.incidentId] });

      // Show success notification
      toast.success('Communication logged successfully');

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to log communication: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}

// ==================== RECOVERY METRICS HOOKS ====================

/**
 * Hook to fetch incident recovery metrics
 * Lists all RTO/RPO metrics for a specific incident
 *
 * @param params - Query parameters including incidentId
 * @returns Query result with recovery metrics data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: metrics, isLoading, error } = useIncidentMetrics({
 *   incidentId: 'incident-123',
 *   enabled: true,
 * });
 *
 * if (metrics) {
 *   console.log('Total services tracked:', metrics.length);
 *   console.log('RTO compliance:', metrics.filter(m => m.rto_met).length);
 *   console.log('RPO compliance:', metrics.filter(m => m.rpo_met).length);
 * }
 * ```
 */
export function useIncidentMetrics({
  incidentId,
  enabled = true,
  staleTime,
  gcTime,
}: UseIncidentMetricsParams) {
  return useQuery({
    queryKey: dashboardKeys.recoveryMetrics(incidentId),
    queryFn: async (): Promise<RecoveryObjective[]> => {
      const metrics = await responseClient.getIncidentMetrics(incidentId);
      return metrics.map(toRecoveryObjective);
    },

    // Enable/disable query
    enabled: enabled && !!incidentId,

    // Caching strategy - metrics change moderately
    staleTime: staleTime ?? 3 * 60 * 1000, // 3 minutes
    gcTime: gcTime ?? 20 * 60 * 1000, // 20 minutes

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to add recovery metrics for an incident
 * Mutation for creating recovery objective records
 *
 * @param options - Callback options for success, error, and settled states
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const addMetrics = useAddRecoveryMetrics({
 *   onSuccess: (metrics) => {
 *     toast.success('Recovery metrics added successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to add metrics: ${error.message}`);
 *   },
 * });
 *
 * // Add recovery metrics
 * addMetrics.mutate({
 *   incidentId: 'incident-123',
 *   data: {
 *     service_name: 'Customer Portal',
 *     service_category: 'web_application',
 *     priority: 'critical',
 *     target_rto_hours: 4,
 *     target_rpo_hours: 1,
 *     downtime_start: new Date().toISOString(),
 *   },
 * });
 * ```
 */
export function useAddRecoveryMetrics(options: UseAddRecoveryMetricsOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ incidentId, data }: AddRecoveryMetricsParams): Promise<RecoveryObjective> => {
      const metricsCreate = toRecoveryMetricsCreate(data);
      const metrics = await responseClient.addRecoveryMetrics(incidentId, metricsCreate);
      return toRecoveryObjective(metrics);
    },

    onSuccess: (data, variables) => {
      // Invalidate recovery metrics cache
      queryClient.invalidateQueries({ queryKey: dashboardKeys.recoveryMetrics(variables.incidentId) });

      // Also invalidate incident details and dashboard
      queryClient.invalidateQueries({ queryKey: ['response', 'incidents', variables.incidentId] });
      queryClient.invalidateQueries({ queryKey: dashboardKeys.overview('current') });

      // Show success notification
      toast.success(`Recovery metrics added for ${data.service_name}`);

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to add recovery metrics: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}

/**
 * Hook to update recovery metrics
 * Mutation for updating existing recovery objective records
 *
 * @param options - Callback options for success, error, and settled states
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateMetrics = useUpdateRecoveryMetrics({
 *   onSuccess: (metrics) => {
 *     toast.success('Recovery metrics updated successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to update metrics: ${error.message}`);
 *   },
 * });
 *
 * // Update recovery metrics
 * updateMetrics.mutate({
 *   metricsId: 'metrics-123',
 *   data: {
 *     actual_rto_hours: 3.5,
 *     actual_rpo_hours: 0.5,
 *     downtime_end: new Date().toISOString(),
 *   },
 * });
 * ```
 */
export function useUpdateRecoveryMetrics(options: UseUpdateRecoveryMetricsOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ metricsId, data }: UpdateRecoveryMetricsParams): Promise<RecoveryObjective> => {
      const metricsUpdate = toRecoveryMetricsUpdate(data);
      const metrics = await responseClient.updateRecoveryMetrics(metricsId, metricsUpdate);
      return toRecoveryObjective(metrics);
    },

    onSuccess: (data) => {
      // Invalidate recovery metrics cache
      queryClient.invalidateQueries({ queryKey: dashboardKeys.recoveryMetrics(data.incident_id) });

      // Also invalidate incident details and dashboard
      queryClient.invalidateQueries({ queryKey: ['response', 'incidents', data.incident_id] });
      queryClient.invalidateQueries({ queryKey: dashboardKeys.overview('current') });

      // Show success notification
      const rtoStatus = data.rto_met ? 'met' : 'not met';
      const rpoStatus = data.rpo_met ? 'met' : 'not met';
      toast.success(`Recovery metrics updated - RTO: ${rtoStatus}, RPO: ${rpoStatus}`);

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to update recovery metrics: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}

// ==================== REPORTING HOOKS ====================

/**
 * Hook to generate incident report
 * Mutation for generating comprehensive incident reports
 *
 * @param options - Callback options for success, error, and settled states
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const generateReport = useGenerateReport({
 *   onSuccess: (report) => {
 *     toast.success('Incident report generated successfully');
 *     // Download or display report
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to generate report: ${error.message}`);
 *   },
 * });
 *
 * // Generate report
 * generateReport.mutate('incident-123');
 * ```
 */
export function useGenerateReport(options: UseGenerateReportOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (incidentId: string): Promise<IncidentReport> => {
      const apiReport = await responseClient.generateIncidentReport(incidentId);
      return toIncidentReport(apiReport);
    },

    onSuccess: (data, incidentId) => {
      // Cache the generated report
      queryClient.setQueryData(dashboardKeys.report(incidentId), data);

      // Show success notification
      toast.success('Incident report generated successfully');

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Failed to generate report: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration - reports can be resource intensive
    retry: 1,
    retryDelay: 2000,
  });
}

/**
 * Hook to fetch existing incident report
 * Query for retrieving previously generated reports
 *
 * @param params - Query parameters including incidentId
 * @returns Query result with report data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: report, isLoading, error } = useIncidentReport({
 *   incidentId: 'incident-123',
 *   enabled: true,
 * });
 *
 * if (report) {
 *   console.log('Executive summary:', report.executive_summary);
 *   console.log('Key findings:', report.key_findings);
 *   console.log('Recommendations:', report.recommendations);
 * }
 * ```
 */
export function useIncidentReport({
  incidentId,
  enabled = true,
  staleTime,
  gcTime,
}: UseIncidentReportParams) {
  return useQuery({
    queryKey: dashboardKeys.report(incidentId),
    queryFn: async (): Promise<IncidentReport> => {
      const apiReport = await responseClient.generateIncidentReport(incidentId);
      return toIncidentReport(apiReport);
    },

    // Enable/disable query
    enabled: enabled && !!incidentId,

    // Caching strategy - reports are static once generated
    staleTime: staleTime ?? 30 * 60 * 1000, // 30 minutes
    gcTime: gcTime ?? 2 * 60 * 60 * 1000, // 2 hours

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== HEALTH CHECK HOOK ====================

/**
 * Hook to check response service health
 * Monitors service availability and status
 *
 * @param params - Query parameters including optional auto-refresh
 * @returns Query result with health status, loading state, error
 *
 * @example
 * ```tsx
 * const { data: health, isLoading, error } = useHealthCheck({
 *   enabled: true,
 *   refetchInterval: 30000, // Check every 30 seconds
 * });
 *
 * if (health) {
 *   console.log('Service status:', health.status);
 *   console.log('ISO standard:', health.iso_standard);
 *   console.log('Last check:', health.timestamp);
 * }
 * ```
 */
export function useHealthCheck({
  enabled = true,
  staleTime,
  gcTime,
  refetchInterval,
}: UseHealthCheckParams = {}) {
  return useQuery({
    queryKey: dashboardKeys.health(),
    queryFn: async () => {
      return responseClient.healthCheck();
    },

    // Enable/disable query
    enabled,

    // Caching strategy - health checks are transient
    staleTime: staleTime ?? 30 * 1000, // 30 seconds
    gcTime: gcTime ?? 2 * 60 * 1000, // 2 minutes

    // Auto-refresh
    refetchInterval: refetchInterval ?? false,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Helper function to calculate RTO/RPO compliance rate
 * @param metrics - Array of recovery metrics
 * @returns Object with RTO and RPO compliance percentages
 */
export function calculateComplianceRates(metrics: RecoveryObjective[]): {
  rto_compliance: number;
  rpo_compliance: number;
} {
  if (!Array.isArray(metrics) || metrics.length === 0) {
    return { rto_compliance: 0, rpo_compliance: 0 };
  }

  const rtoMet = metrics.filter((m) => m.rto_met === true).length;
  const rpoMet = metrics.filter((m) => m.rpo_met === true).length;
  const total = metrics.length;

  return {
    rto_compliance: Math.round((rtoMet / total) * 100),
    rpo_compliance: Math.round((rpoMet / total) * 100),
  };
}

/**
 * Helper function to categorize communications by type
 * @param communications - Array of communication records
 * @returns Communications grouped by type
 */
export function categorizeByType(communications: CommunicationRecord[]): Record<string, CommunicationRecord[]> {
  if (!Array.isArray(communications)) return {};

  return communications.reduce(
    (acc, comm) => {
      const type = comm.communication_type;
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(comm);
      return acc;
    },
    {} as Record<string, CommunicationRecord[]>
  );
}

/**
 * Helper function to get stakeholder communications
 * @param communications - Array of communication records
 * @returns Only stakeholder notifications
 */
export function getStakeholderCommunications(communications: CommunicationRecord[]): CommunicationRecord[] {
  if (!Array.isArray(communications)) return [];
  return communications.filter((c) => c.is_stakeholder_notification === true);
}

/**
 * Helper function to calculate average downtime
 * @param metrics - Array of recovery metrics
 * @returns Average downtime in hours
 */
export function calculateAverageDowntime(metrics: RecoveryObjective[]): number {
  if (!Array.isArray(metrics) || metrics.length === 0) return 0;

  const totalDowntime = metrics.reduce((sum, m) => sum + (m.total_downtime_hours || 0), 0);
  return Math.round((totalDowntime / metrics.length) * 100) / 100;
}

/**
 * Helper function to get services not meeting RTO
 * @param metrics - Array of recovery metrics
 * @returns Services that missed RTO targets
 */
export function getServicesNotMeetingRTO(metrics: RecoveryObjective[]): RecoveryObjective[] {
  if (!Array.isArray(metrics)) return [];
  return metrics.filter((m) => m.rto_met === false);
}

/**
 * Helper function to get services not meeting RPO
 * @param metrics - Array of recovery metrics
 * @returns Services that missed RPO targets
 */
export function getServicesNotMeetingRPO(metrics: RecoveryObjective[]): RecoveryObjective[] {
  if (!Array.isArray(metrics)) return [];
  return metrics.filter((m) => m.rpo_met === false);
}

/**
 * Helper function to get critical services from metrics
 * @param metrics - Array of recovery metrics
 * @returns Only critical priority services
 */
export function getCriticalServices(metrics: RecoveryObjective[]): RecoveryObjective[] {
  if (!Array.isArray(metrics)) return [];
  return metrics.filter((m) => m.priority === 'critical');
}

/**
 * Helper function to calculate incident trend direction
 * @param trends - Response trends data
 * @returns Trend direction indicator
 */
export function getTrendDirection(trends: ResponseTrendsResponse): 'improving' | 'stable' | 'declining' {
  if (!trends || !trends.data_points || trends.data_points.length < 2) {
    return 'stable';
  }

  const points = trends.data_points;
  const firstHalf = points.slice(0, Math.floor(points.length / 2));
  const secondHalf = points.slice(Math.floor(points.length / 2));

  const avgFirst = firstHalf.reduce((sum, p) => sum + p.incidents_count, 0) / firstHalf.length;
  const avgSecond = secondHalf.reduce((sum, p) => sum + p.incidents_count, 0) / secondHalf.length;

  const threshold = 0.1; // 10% change threshold

  if (avgSecond < avgFirst * (1 - threshold)) return 'improving';
  if (avgSecond > avgFirst * (1 + threshold)) return 'declining';
  return 'stable';
}

/**
 * Helper function to format dashboard summary
 * @param dashboard - Response dashboard data
 * @returns Formatted summary object
 */
export function formatDashboardSummary(dashboard: ResponseDashboard): {
  active: number;
  critical: number;
  highSeverity: number;
  rtoCompliance: string;
  rpoCompliance: string;
} {
  return {
    active: dashboard.active_incidents,
    critical: dashboard.critical_incidents,
    highSeverity: dashboard.high_severity_incidents,
    rtoCompliance: `${dashboard.rto_compliance_rate}%`,
    rpoCompliance: `${dashboard.rpo_compliance_rate}%`,
  };
}
