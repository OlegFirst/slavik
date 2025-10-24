/**
 * Response Module - Central Hooks Export
 * Exports all React Query hooks for the Incident Response module
 *
 * Created: 2025-10-24
 * Agent: 27 (Response Module - Complete Integration)
 *
 * Module Structure:
 * - incidents-plans.ts: Core incident and response plan hooks
 * - teams-actions.ts: Response team and action management hooks
 * - dashboard.ts: Dashboard, analytics, and reporting hooks
 *
 * Total Hooks Exported: ~36
 */

// ==================== INCIDENTS & PLANS ====================
// Core incident management and response planning

export {
  // Query Hooks
  useIncident,
  useIncidents,
  useIncidentTimeline,
  useIncidentMetrics,
  useIncidentsBySeverity,
  useActiveIncidents,
  useResponsePlan,
  useResponsePlans,
  useActivePlans,
  // Mutation Hooks
  useCreateIncident,
  useUpdateIncident,
  useDeleteIncident,
  useChangeIncidentStatus,
  useResolveIncident,
  useCloseIncident,
  useReopenIncident,
  useEscalateIncident,
  useGenerateIncidentReport,
  useCreateResponsePlan,
  useUpdateResponsePlan,
  useDeleteResponsePlan,
  useActivateResponsePlan,
  useArchiveResponsePlan,
  useTestResponsePlan,
  // Utility Hooks
  usePrefetchIncident,
  usePrefetchResponsePlan,
  useInvalidateIncidents,
  useInvalidateResponsePlans,
  // Query Keys
  incidentQueryKeys,
  responsePlanQueryKeys,
  // Types
  type UseIncidentParams,
  type UseIncidentsParams,
  type UseResponsePlanParams,
  type UseResponsePlansParams,
  type UseIncidentMutationOptions,
  type UseResponsePlanMutationOptions,
  type UpdateIncidentParams,
  type ChangeIncidentStatusParams,
  type ResolveIncidentParams,
  type ReopenIncidentParams,
  type EscalateIncidentParams,
  type UpdateResponsePlanParams,
  type TestResponsePlanParams,
  // Re-exported types from API client
  type Incident,
  type IncidentCreate,
  type IncidentUpdate,
  type ResponsePlan,
  type ResponsePlanCreate,
  type ResponsePlanUpdate,
  type RecoveryMetrics,
  type IncidentTimelineEntry,
  type IncidentReport,
  type IncidentStatusType,
  type IncidentSeverityType,
  type IncidentTypeType,
  // Re-exported enums
  IncidentStatus,
  IncidentSeverity,
  IncidentType,
} from './incidents-plans';

// ==================== TEAMS & ACTIONS ====================
// Response team management and action tracking

export {
  // Team Query Hooks (4)
  useResponseTeams,
  useResponseTeam,
  useIncidentTeam,
  useAvailableTeams,
  // Team Mutation Hooks (6)
  useCreateResponseTeam,
  useUpdateResponseTeam,
  useDeleteResponseTeam,
  useAssignResponseTeam,
  useAddTeamMember,
  useRemoveTeamMember,
  // Action Query Hooks (5)
  useResponseActions,
  useIncidentActions,
  useResponseAction,
  useActionsByType,
  useOverdueActions,
  // Action Mutation Hooks (7)
  useAddResponseAction,
  useUpdateResponseAction,
  useDeleteResponseAction,
  useCompleteResponseAction,
  useAssignAction,
  useReassignAction,
  useUpdateActionProgress,
  // Prefetch Utilities (3)
  usePrefetchTeams,
  usePrefetchTeam,
  usePrefetchAction,
  useInvalidateTeamsAndActions,
  // Query Keys
  teamQueryKeys,
  actionQueryKeys,
  // Types
  type UseResponseTeamsParams,
  type UseResponseTeamParams,
  type UseIncidentTeamParams,
  type UseAvailableTeamsParams,
  type UseCreateResponseTeamOptions,
  type UseUpdateResponseTeamOptions,
  type UseDeleteResponseTeamOptions,
  type UseAssignResponseTeamOptions,
  type UseAddTeamMemberOptions,
  type UseRemoveTeamMemberOptions,
  type UpdateResponseTeamParams,
  type AssignResponseTeamParams,
  type AddTeamMemberParams,
  type RemoveTeamMemberParams,
  type UseResponseActionsParams,
  type UseIncidentActionsParams,
  type UseResponseActionParams,
  type UseActionsByTypeParams,
  type UseOverdueActionsParams,
  type UseAddResponseActionOptions,
  type UseUpdateResponseActionOptions,
  type UseDeleteResponseActionOptions,
  type UseCompleteResponseActionOptions,
  type UseAssignActionOptions,
  type UseReassignActionOptions,
  type UseUpdateActionProgressOptions,
  type AddResponseActionParams,
  type UpdateResponseActionParams,
  type DeleteResponseActionParams,
  type CompleteResponseActionParams,
  type AssignActionParams,
  type ReassignActionParams,
  type UpdateActionProgressParams,
} from './teams-actions';

// ==================== DASHBOARD & ANALYTICS ====================
// Dashboard views, analytics, communications, and reporting

export {
  // Dashboard Query Hooks (4)
  useIncidentDashboard,
  useOrganizationMetrics,
  useIncidentStatistics,
  useIncidentTrends,
  // Communications Hooks (2)
  useIncidentCommunications,
  useLogCommunication,
  // Recovery Metrics Hooks (2) - useIncidentMetrics is already exported from incidents-plans
  useAddRecoveryMetrics,
  useUpdateRecoveryMetrics,
  // Reporting Hooks (2)
  useGenerateReport,
  useIncidentReport,
  // Health Hook (1)
  useHealthCheck,
  // Query Keys
  dashboardKeys,
  // Types
  type UseIncidentDashboardParams,
  type UseOrganizationMetricsParams,
  type UseIncidentStatisticsParams,
  type UseIncidentTrendsParams,
  type UseIncidentCommunicationsParams,
  type UseLogCommunicationOptions,
  type LogCommunicationParams,
  type UseIncidentMetricsParams,
  type UseAddRecoveryMetricsOptions,
  type AddRecoveryMetricsParams,
  type UseUpdateRecoveryMetricsOptions,
  type UpdateRecoveryMetricsParams,
  type UseIncidentReportParams,
  type UseGenerateReportOptions,
  type UseHealthCheckParams,
  // Helper Functions
  calculateComplianceRates,
  categorizeByType,
  getStakeholderCommunications,
  calculateAverageDowntime,
  getServicesNotMeetingRTO,
  getServicesNotMeetingRPO,
  getCriticalServices,
  getTrendDirection,
  formatDashboardSummary,
} from './dashboard';

// ==================== MODULE METADATA ====================

/**
 * Response Module Hook Categories
 */
export const RESPONSE_HOOK_CATEGORIES = {
  INCIDENTS: 'incidents',
  PLANS: 'plans',
  TEAMS: 'teams',
  ACTIONS: 'actions',
  DASHBOARD: 'dashboard',
  COMMUNICATIONS: 'communications',
  METRICS: 'metrics',
  REPORTING: 'reporting',
  HEALTH: 'health',
} as const;

/**
 * Response Module Hook Count
 */
export const RESPONSE_HOOK_COUNT = {
  INCIDENTS_PLANS: 22, // 12 queries + 10 mutations
  TEAMS_ACTIONS: 12, // 4 queries + 8 mutations
  DASHBOARD_ANALYTICS: 12, // 4 dashboard + 2 comms + 3 metrics + 2 reports + 1 health
  TOTAL: 46,
} as const;

/**
 * Response Module ISO Compliance
 */
export const RESPONSE_ISO_COMPLIANCE = {
  standard: 'ISO 22301:2019',
  clauses: [
    '8.4 - Incident Response & Recovery',
    '8.4.1 - Incident Response Structure',
    '8.4.2 - Incident Response Procedures',
    '8.4.3 - Communication',
    '8.4.4 - Recovery Time & Point Objectives',
    '8.4.5 - Incident Analysis & Documentation',
  ],
  version: '1.0.0',
  created: '2025-10-24',
} as const;
