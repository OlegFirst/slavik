/**
 * Response Module - Incidents & Plans Hooks
 * React Query hooks for Incident Response and Response Plans management
 *
 * ISO 22301:2019 Clause 8.4 - Incident Response & Recovery
 * AI Platform ISO Project
 *
 * Created: 2025-10-24
 * Agent: 25 (Response Module Data Layer)
 *
 * Total Hooks: 29
 * - Incidents: 15 hooks (6 query + 9 mutation)
 * - Response Plans: 10 hooks (4 query + 6 mutation)
 * - Utility: 4 hooks (prefetch, invalidate)
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '@/lib/api/response-client';

// Import types directly from API client to avoid conflicts
type Incident = api.Incident;
type IncidentCreate = api.IncidentCreate;
type IncidentUpdate = api.IncidentUpdate;
type IncidentReport = api.IncidentReport;
type IncidentTimelineEntry = api.IncidentTimelineEntry;
type RecoveryMetrics = api.RecoveryMetrics;

// Response Plan types (placeholder - API not yet implemented)
interface ResponsePlan {
  id?: string;
  plan_name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}
type ResponsePlanCreate = Omit<ResponsePlan, 'id' | 'created_at' | 'updated_at'>;
type ResponsePlanUpdate = Partial<ResponsePlanCreate>;

// Use API client enums
const IncidentStatus = api.IncidentStatus;
const IncidentSeverity = api.IncidentSeverity;
const IncidentType = api.IncidentType;

// Create type aliases for enum types
type IncidentStatusType = api.IncidentStatus;
type IncidentSeverityType = api.IncidentSeverity;
type IncidentTypeType = api.IncidentType;

// ============================================================================
// QUERY KEY FACTORIES
// ============================================================================

/**
 * Query key factory for incidents
 * Provides centralized, type-safe query key management
 */
export const incidentQueryKeys = {
  all: ['incidents'] as const,
  lists: () => [...incidentQueryKeys.all, 'list'] as const,
  list: (params: UseIncidentsParams) => [...incidentQueryKeys.lists(), params] as const,
  details: () => [...incidentQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...incidentQueryKeys.details(), id] as const,
  timeline: (id: string) => [...incidentQueryKeys.detail(id), 'timeline'] as const,
  metrics: (id: string) => [...incidentQueryKeys.detail(id), 'metrics'] as const,
  report: (id: string) => [...incidentQueryKeys.detail(id), 'report'] as const,
  bySeverity: (severity: IncidentSeverityType) =>
    [...incidentQueryKeys.all, 'bySeverity', severity] as const,
  active: () => [...incidentQueryKeys.all, 'active'] as const,
};

/**
 * Query key factory for response plans
 * Provides centralized, type-safe query key management
 */
export const responsePlanQueryKeys = {
  all: ['responsePlans'] as const,
  lists: () => [...responsePlanQueryKeys.all, 'list'] as const,
  list: (params: UseResponsePlansParams) => [...responsePlanQueryKeys.lists(), params] as const,
  details: () => [...responsePlanQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...responsePlanQueryKeys.details(), id] as const,
  active: () => [...responsePlanQueryKeys.all, 'active'] as const,
};

// ============================================================================
// TYPE DEFINITIONS - INCIDENTS
// ============================================================================

/**
 * Parameters for listing incidents with filters
 */
export interface UseIncidentsParams {
  status?: IncidentStatusType;
  severity?: IncidentSeverityType;
  incident_type?: IncidentTypeType;
  from_date?: string;
  to_date?: string;
  search?: string;
  tags?: string[];
  skip?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Parameters for fetching a single incident
 */
export interface UseIncidentParams {
  incidentId: string;
  enabled?: boolean;
}

/**
 * Options for incident mutations
 */
export interface UseIncidentMutationOptions {
  onSuccess?: (incident: Incident) => void;
  onError?: (error: Error) => void;
}

/**
 * Parameters for updating an incident
 */
export interface UpdateIncidentParams {
  incidentId: string;
  data: IncidentUpdate;
}

/**
 * Parameters for changing incident status
 */
export interface ChangeIncidentStatusParams {
  incidentId: string;
  status: IncidentStatusType;
  reason?: string;
  notes?: string;
}

/**
 * Parameters for resolving an incident
 */
export interface ResolveIncidentParams {
  incidentId: string;
  rootCause?: string;
  lessonsLearned?: string;
}

/**
 * Parameters for reopening an incident
 */
export interface ReopenIncidentParams {
  incidentId: string;
  reason: string;
}

/**
 * Parameters for escalating an incident
 */
export interface EscalateIncidentParams {
  incidentId: string;
  escalation_reason: string;
  escalate_to?: string[];
  escalation_level: string;
  notify_stakeholders?: boolean;
  additional_notes?: string;
}

// ============================================================================
// TYPE DEFINITIONS - RESPONSE PLANS
// ============================================================================

/**
 * Parameters for listing response plans with filters
 */
export interface UseResponsePlansParams {
  organization_id?: string;
  search?: string;
  skip?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Parameters for fetching a single response plan
 */
export interface UseResponsePlanParams {
  planId: string;
  enabled?: boolean;
}

/**
 * Options for response plan mutations
 */
export interface UseResponsePlanMutationOptions {
  onSuccess?: (plan: ResponsePlan) => void;
  onError?: (error: Error) => void;
}

/**
 * Parameters for updating a response plan
 */
export interface UpdateResponsePlanParams {
  planId: string;
  data: ResponsePlanUpdate;
}

/**
 * Parameters for testing a response plan
 */
export interface TestResponsePlanParams {
  planId: string;
  testResults: string;
  testedBy: string;
}

// ============================================================================
// QUERY HOOKS - INCIDENTS (6 Hooks)
// ============================================================================

/**
 * Hook: useIncidents
 * Fetch list of incidents with filtering, sorting, and pagination
 *
 * @param params - Filter parameters including status, severity, category, etc.
 * @returns Query result with incidents list
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useIncidents({
 *   organization_id: 'org-123',
 *   status: IncidentStatus.INVESTIGATING,
 *   severity: IncidentSeverity.HIGH,
 *   limit: 50,
 * });
 * ```
 */
export function useIncidents(params: UseIncidentsParams = {}) {
  const { enabled = true, ...queryParams } = params;

  return useQuery({
    queryKey: incidentQueryKeys.list(queryParams),
    queryFn: () => api.listIncidents(queryParams),
    enabled: enabled,
    staleTime: 10000, // 10 seconds - incidents change frequently
  });
}

/**
 * Hook: useIncident
 * Fetch a single incident by ID with all details
 *
 * @param params - Incident ID and enabled flag
 * @returns Query result with single incident
 *
 * @example
 * ```tsx
 * const { data: incident, isLoading } = useIncident({
 *   incidentId: 'inc-123',
 *   enabled: true,
 * });
 * ```
 */
export function useIncident({ incidentId, enabled = true }: UseIncidentParams) {
  return useQuery({
    queryKey: incidentQueryKeys.detail(incidentId),
    queryFn: () => api.getIncident(incidentId),
    enabled: enabled && !!incidentId,
    staleTime: 15000, // 15 seconds
  });
}

/**
 * Hook: useIncidentTimeline
 * Fetch chronological timeline of incident events
 *
 * @param incidentId - Incident ID
 * @param options - Query options
 * @returns Query result with timeline events array
 *
 * @example
 * ```tsx
 * const { data: timeline, isLoading } = useIncidentTimeline('inc-123', {
 *   enabled: true,
 * });
 * ```
 */
export function useIncidentTimeline(
  incidentId: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: incidentQueryKeys.timeline(incidentId),
    queryFn: () => api.getIncidentTimeline(incidentId),
    enabled: options?.enabled !== false && !!incidentId,
    staleTime: 5000, // 5 seconds - timeline updates frequently
  });
}

/**
 * Hook: useIncidentMetrics
 * Fetch RTO/RPO metrics and recovery objectives for an incident
 *
 * @param incidentId - Incident ID
 * @param options - Query options
 * @returns Query result with recovery metrics
 *
 * @example
 * ```tsx
 * const { data: metrics, isLoading } = useIncidentMetrics('inc-123', {
 *   enabled: true,
 * });
 * ```
 */
export function useIncidentMetrics(
  incidentId: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: incidentQueryKeys.metrics(incidentId),
    queryFn: () => api.getIncidentMetrics(incidentId),
    enabled: options?.enabled !== false && !!incidentId,
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook: useIncidentsBySeverity
 * Fetch incidents filtered by severity level
 *
 * @param severity - Incident severity level
 * @returns Query result with filtered incidents
 *
 * @example
 * ```tsx
 * const { data } = useIncidentsBySeverity(IncidentSeverity.CRITICAL);
 * const criticalIncidents = data?.items || [];
 * ```
 */
export function useIncidentsBySeverity(
  severity: IncidentSeverityType
) {
  return useIncidents({
    severity,
  });
}

/**
 * Hook: useActiveIncidents
 * Fetch only active incidents (not resolved or closed)
 *
 * @param organizationId - Organization ID
 * @returns Query result with active incidents
 *
 * @example
 * ```tsx
 * const { data } = useActiveIncidents('org-123');
 * const activeIncidents = data?.items || [];
 * ```
 */
export function useActiveIncidents(organizationId?: string) {
  return useQuery({
    queryKey: incidentQueryKeys.active(),
    queryFn: async () => {
      // Fetch incidents that are not resolved or closed
      const statuses: IncidentStatusType[] = [
        IncidentStatus.DETECTED,
        IncidentStatus.INVESTIGATING,
        IncidentStatus.CONTAINED,
      ];

      // Fetch all active statuses and combine
      const results = await Promise.all(
        statuses.map((status) =>
          api.listIncidents({ status })
        )
      );

      // Combine all results
      const allIncidents = results.flatMap((r) => r.items);
      const total = results.reduce((sum, r) => sum + r.total, 0);

      return {
        items: allIncidents,
        total,
        skip: 0,
        limit: allIncidents.length,
      };
    },
    staleTime: 10000, // 10 seconds
  });
}

// ============================================================================
// MUTATION HOOKS - INCIDENTS (9 Hooks)
// ============================================================================

/**
 * Hook: useCreateIncident
 * Create a new incident (report incident)
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for creating incidents
 *
 * @example
 * ```tsx
 * const createIncident = useCreateIncident({
 *   onSuccess: (incident) => {
 *     toast.success(`Incident ${incident.incident_number} created`);
 *     router.push(`/response/incidents/${incident.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create incident: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * createIncident.mutate({
 *   organization_id: 'org-123',
 *   title: 'Database Server Outage',
 *   description: 'Primary database server is unresponsive',
 *   incident_type: IncidentType.SYSTEM_FAILURE,
 *   severity: IncidentSeverity.CRITICAL,
 *   affected_systems: ['db-primary-01'],
 *   detected_at: new Date().toISOString(),
 * });
 * ```
 */
export function useCreateIncident(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: IncidentCreate) => api.createIncident(data),
    onSuccess: (data) => {
      // Invalidate all incident lists
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.active() });

      // Set the new incident in cache
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useUpdateIncident
 * Update an existing incident
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for updating incidents
 *
 * @example
 * ```tsx
 * const updateIncident = useUpdateIncident({
 *   onSuccess: (incident) => {
 *     toast.success('Incident updated successfully');
 *   },
 * });
 *
 * // Usage
 * updateIncident.mutate({
 *   incidentId: 'inc-123',
 *   data: {
 *     description: 'Updated description with more details',
 *     estimated_impact: 'All users affected in US-East region',
 *   },
 * });
 * ```
 */
export function useUpdateIncident(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, data }: UpdateIncidentParams) =>
      api.updateIncident(incidentId, data),
    onSuccess: (data) => {
      // Invalidate lists and specific detail
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.detail(data.id!) });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.timeline(data.id!) });

      // Update cache with new data
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useDeleteIncident
 * Delete an incident (soft delete)
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for deleting incidents
 *
 * @example
 * ```tsx
 * const deleteIncident = useDeleteIncident({
 *   onSuccess: () => {
 *     toast.success('Incident deleted successfully');
 *     router.push('/response/incidents');
 *   },
 * });
 *
 * // Usage
 * deleteIncident.mutate('inc-123');
 * ```
 */
export function useDeleteIncident(options?: { onSuccess?: () => void; onError?: (error: Error) => void }) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (incidentId: string) => api.deleteIncident(incidentId),
    onSuccess: (_, incidentId) => {
      // Invalidate all incident lists
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.active() });

      // Remove from cache
      queryClient.removeQueries({ queryKey: incidentQueryKeys.detail(incidentId) });
      queryClient.removeQueries({ queryKey: incidentQueryKeys.timeline(incidentId) });
      queryClient.removeQueries({ queryKey: incidentQueryKeys.metrics(incidentId) });

      options?.onSuccess?.();
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useChangeIncidentStatus
 * Change incident status with reason and notes
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for changing incident status
 *
 * @example
 * ```tsx
 * const changeStatus = useChangeIncidentStatus({
 *   onSuccess: (incident) => {
 *     toast.success(`Status changed to ${incident.status}`);
 *   },
 * });
 *
 * // Usage
 * changeStatus.mutate({
 *   incidentId: 'inc-123',
 *   status: IncidentStatus.RESPONDING,
 *   reason: 'Response team assembled',
 *   notes: 'Team lead: John Doe',
 * });
 * ```
 */
export function useChangeIncidentStatus(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, status, reason, notes }: ChangeIncidentStatusParams) =>
      api.changeIncidentStatus(incidentId, { status, reason, notes }),
    onSuccess: (data) => {
      // Invalidate lists and details
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.active() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.detail(data.id!) });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.timeline(data.id!) });

      // Update cache
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useResolveIncident
 * Resolve incident with root cause analysis and lessons learned
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for resolving incidents
 *
 * @example
 * ```tsx
 * const resolveIncident = useResolveIncident({
 *   onSuccess: (incident) => {
 *     toast.success('Incident resolved');
 *   },
 * });
 *
 * // Usage
 * resolveIncident.mutate({
 *   incidentId: 'inc-123',
 *   rootCause: 'Database connection pool exhausted',
 *   lessonsLearned: 'Implement better connection pool monitoring',
 * });
 * ```
 */
export function useResolveIncident(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, rootCause, lessonsLearned }: ResolveIncidentParams) =>
      api.resolveIncident(incidentId, rootCause, lessonsLearned),
    onSuccess: (data) => {
      // Invalidate all relevant queries
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.active() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.detail(data.id!) });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.timeline(data.id!) });

      // Update cache
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useCloseIncident
 * Close an incident (final state)
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for closing incidents
 *
 * @example
 * ```tsx
 * const closeIncident = useCloseIncident({
 *   onSuccess: (incident) => {
 *     toast.success('Incident closed');
 *   },
 * });
 *
 * // Usage
 * closeIncident.mutate('inc-123');
 * ```
 */
export function useCloseIncident(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (incidentId: string) => api.closeIncident(incidentId),
    onSuccess: (data) => {
      // Invalidate all relevant queries
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.active() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.detail(data.id!) });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.timeline(data.id!) });

      // Update cache
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useReopenIncident
 * Reopen a closed incident
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for reopening incidents
 *
 * @example
 * ```tsx
 * const reopenIncident = useReopenIncident({
 *   onSuccess: (incident) => {
 *     toast.success('Incident reopened');
 *   },
 * });
 *
 * // Usage
 * reopenIncident.mutate({
 *   incidentId: 'inc-123',
 *   reason: 'Issue recurred after 2 hours',
 * });
 * ```
 */
export function useReopenIncident(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, reason }: ReopenIncidentParams) =>
      api.reopenIncident(incidentId, reason),
    onSuccess: (data) => {
      // Invalidate all relevant queries
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.active() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.detail(data.id!) });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.timeline(data.id!) });

      // Update cache
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useEscalateIncident
 * Escalate incident to higher management level
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for escalating incidents
 *
 * @example
 * ```tsx
 * const escalateIncident = useEscalateIncident({
 *   onSuccess: (incident) => {
 *     toast.success('Incident escalated');
 *   },
 * });
 *
 * // Usage
 * escalateIncident.mutate({
 *   incidentId: 'inc-123',
 *   escalation_reason: 'Critical systems down for 2+ hours',
 *   escalation_level: 'executive',
 *   escalate_to: ['cto@company.com', 'ceo@company.com'],
 *   notify_stakeholders: true,
 * });
 * ```
 */
export function useEscalateIncident(options?: UseIncidentMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      incidentId,
      escalation_reason,
      escalate_to,
      escalation_level,
      notify_stakeholders,
      additional_notes,
    }: EscalateIncidentParams) =>
      api.escalateIncident(incidentId, {
        escalation_reason,
        escalate_to,
        escalation_level,
        notify_stakeholders,
        additional_notes,
      }),
    onSuccess: (data) => {
      // Invalidate all relevant queries
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.detail(data.id!) });
      queryClient.invalidateQueries({ queryKey: incidentQueryKeys.timeline(data.id!) });

      // Update cache
      queryClient.setQueryData(incidentQueryKeys.detail(data.id!), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useGenerateIncidentReport
 * Generate comprehensive incident report
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for generating incident reports
 *
 * @example
 * ```tsx
 * const generateReport = useGenerateIncidentReport({
 *   onSuccess: (report) => {
 *     toast.success('Report generated successfully');
 *     // Download or display report
 *   },
 * });
 *
 * // Usage
 * generateReport.mutate('inc-123');
 * ```
 */
export function useGenerateIncidentReport(options?: {
  onSuccess?: (report: api.IncidentReport) => void;
  onError?: (error: Error) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (incidentId: string) => api.generateIncidentReport(incidentId),
    onSuccess: (data, incidentId) => {
      // Cache the report
      queryClient.setQueryData(incidentQueryKeys.report(incidentId), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

// ============================================================================
// QUERY HOOKS - RESPONSE PLANS (4 Hooks)
// ============================================================================

/**
 * Hook: useResponsePlans
 * Fetch list of response plans with filtering
 *
 * @param params - Filter parameters including status, category, etc.
 * @returns Query result with response plans list
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useResponsePlans({
 *   organization_id: 'org-123',
 *   status: PlanStatus.ACTIVE,
 * });
 * ```
 */
export function useResponsePlans(params: UseResponsePlansParams = {}) {
  const { enabled = true, organization_id, ...queryParams } = params;

  return useQuery({
    queryKey: responsePlanQueryKeys.list(params),
    queryFn: async () => {
      // Note: API endpoint not yet implemented
      // This is a placeholder that will work once the endpoint is added
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    enabled: enabled && !!organization_id,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook: useResponsePlan
 * Fetch a single response plan by ID
 *
 * @param params - Plan ID and enabled flag
 * @returns Query result with single response plan
 *
 * @example
 * ```tsx
 * const { data: plan, isLoading } = useResponsePlan({
 *   planId: 'plan-123',
 *   enabled: true,
 * });
 * ```
 */
export function useResponsePlan({ planId, enabled = true }: UseResponsePlanParams) {
  return useQuery({
    queryKey: responsePlanQueryKeys.detail(planId),
    queryFn: async () => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    enabled: enabled && !!planId,
    staleTime: 120000, // 2 minutes
  });
}

/**
 * Hook: useActivePlans
 * Fetch only active response plans
 *
 * @param organizationId - Organization ID
 * @returns Query result with active plans
 *
 * @example
 * ```tsx
 * const { data } = useActivePlans('org-123');
 * ```
 */
export function useActivePlans(organizationId: string) {
  return useQuery({
    queryKey: responsePlanQueryKeys.active(),
    queryFn: async () => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    enabled: !!organizationId,
    staleTime: 60000, // 1 minute
  });
}

// ============================================================================
// MUTATION HOOKS - RESPONSE PLANS (6 Hooks)
// ============================================================================

/**
 * Hook: useCreateResponsePlan
 * Create a new response plan
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for creating response plans
 *
 * @example
 * ```tsx
 * const createPlan = useCreateResponsePlan({
 *   onSuccess: (plan) => {
 *     toast.success(`Plan "${plan.plan_name}" created`);
 *     router.push(`/response/plans/${plan.id}`);
 *   },
 * });
 *
 * // Usage
 * createPlan.mutate({
 *   organization_id: 'org-123',
 *   plan_name: 'Cyber Attack Response',
 *   plan_code: 'RESP-CYBER-001',
 *   description: 'Response procedures for cyber attacks',
 *   status: PlanStatus.DRAFT,
 *   version: '1.0',
 *   incident_types: [IncidentType.CYBER_ATTACK],
 *   severity_levels: [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
 *   applicable_categories: [IncidentCategory.IT_SYSTEMS],
 *   activation_criteria: ['Unauthorized access detected', 'Data exfiltration suspected'],
 *   auto_activate: false,
 *   initial_actions: ['Isolate affected systems', 'Notify security team'],
 *   escalation_rules: [],
 *   required_resources: [],
 *   contact_list: [],
 *   created_by: 'user-123',
 * });
 * ```
 */
export function useCreateResponsePlan(options?: UseResponsePlanMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<ResponsePlan, Error, ResponsePlanCreate>({
    mutationFn: async (data: ResponsePlanCreate) => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    onSuccess: (data) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.active() });

      // Set the new plan in cache
      if (data.id) {
        queryClient.setQueryData(responsePlanQueryKeys.detail(data.id), data);
      }

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useUpdateResponsePlan
 * Update an existing response plan
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for updating response plans
 *
 * @example
 * ```tsx
 * const updatePlan = useUpdateResponsePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Plan updated successfully');
 *   },
 * });
 *
 * // Usage
 * updatePlan.mutate({
 *   planId: 'plan-123',
 *   data: {
 *     description: 'Updated response procedures',
 *     version: '1.1',
 *   },
 * });
 * ```
 */
export function useUpdateResponsePlan(options?: UseResponsePlanMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<ResponsePlan, Error, UpdateResponsePlanParams>({
    mutationFn: async ({ planId, data }: UpdateResponsePlanParams) => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    onSuccess: (data) => {
      // Invalidate lists and specific detail
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.lists() });
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.detail(data.id) });
        queryClient.setQueryData(responsePlanQueryKeys.detail(data.id), data);
      }

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useDeleteResponsePlan
 * Delete a response plan
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for deleting response plans
 *
 * @example
 * ```tsx
 * const deletePlan = useDeleteResponsePlan({
 *   onSuccess: () => {
 *     toast.success('Plan deleted successfully');
 *     router.push('/response/plans');
 *   },
 * });
 *
 * // Usage
 * deletePlan.mutate('plan-123');
 * ```
 */
export function useDeleteResponsePlan(options?: {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (planId: string) => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    onSuccess: (_, planId) => {
      // Invalidate all plan lists
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.active() });

      // Remove from cache
      queryClient.removeQueries({ queryKey: responsePlanQueryKeys.detail(planId) });

      options?.onSuccess?.();
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useActivateResponsePlan
 * Activate a response plan (change status to active)
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for activating response plans
 *
 * @example
 * ```tsx
 * const activatePlan = useActivateResponsePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Plan is now active');
 *   },
 * });
 *
 * // Usage
 * activatePlan.mutate('plan-123');
 * ```
 */
export function useActivateResponsePlan(options?: UseResponsePlanMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<ResponsePlan, Error, string>({
    mutationFn: async (planId: string) => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    onSuccess: (data) => {
      // Invalidate lists and details
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.active() });
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.detail(data.id) });
        queryClient.setQueryData(responsePlanQueryKeys.detail(data.id), data);
      }

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useArchiveResponsePlan
 * Archive a response plan (change status to archived)
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for archiving response plans
 *
 * @example
 * ```tsx
 * const archivePlan = useArchiveResponsePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Plan archived successfully');
 *   },
 * });
 *
 * // Usage
 * archivePlan.mutate('plan-123');
 * ```
 */
export function useArchiveResponsePlan(options?: UseResponsePlanMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<ResponsePlan, Error, string>({
    mutationFn: async (planId: string) => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    onSuccess: (data) => {
      // Invalidate lists and details
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.active() });
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.detail(data.id) });
        queryClient.setQueryData(responsePlanQueryKeys.detail(data.id), data);
      }

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useTestResponsePlan
 * Test a response plan and record results
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for testing response plans
 *
 * @example
 * ```tsx
 * const testPlan = useTestResponsePlan({
 *   onSuccess: (plan) => {
 *     toast.success('Test results recorded');
 *   },
 * });
 *
 * // Usage
 * testPlan.mutate({
 *   planId: 'plan-123',
 *   testResults: 'All procedures executed successfully. Response time: 12 minutes.',
 *   testedBy: 'user-456',
 * });
 * ```
 */
export function useTestResponsePlan(options?: UseResponsePlanMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<ResponsePlan, Error, TestResponsePlanParams>({
    mutationFn: async ({ planId, testResults, testedBy }: TestResponsePlanParams) => {
      // Note: API endpoint not yet implemented
      throw new Error('Response Plans API endpoint not yet implemented');
    },
    onSuccess: (data) => {
      // Invalidate lists and details
      queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.lists() });
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.detail(data.id) });
        queryClient.setQueryData(responsePlanQueryKeys.detail(data.id), data);
      }

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

// ============================================================================
// UTILITY HOOKS (4 Hooks)
// ============================================================================

/**
 * Hook: usePrefetchIncident
 * Prefetch an incident for improved performance (hover states, navigation)
 *
 * @example
 * ```tsx
 * const prefetchIncident = usePrefetchIncident();
 *
 * <div onMouseEnter={() => prefetchIncident('inc-123')}>
 *   View Incident
 * </div>
 * ```
 */
export function usePrefetchIncident() {
  const queryClient = useQueryClient();

  return (incidentId: string) => {
    queryClient.prefetchQuery({
      queryKey: incidentQueryKeys.detail(incidentId),
      queryFn: () => api.getIncident(incidentId),
      staleTime: 15000,
    });
  };
}

/**
 * Hook: usePrefetchResponsePlan
 * Prefetch a response plan for improved performance
 *
 * @example
 * ```tsx
 * const prefetchPlan = usePrefetchResponsePlan();
 *
 * <div onMouseEnter={() => prefetchPlan('plan-123')}>
 *   View Plan
 * </div>
 * ```
 */
export function usePrefetchResponsePlan() {
  const queryClient = useQueryClient();

  return (planId: string) => {
    queryClient.prefetchQuery({
      queryKey: responsePlanQueryKeys.detail(planId),
      queryFn: async () => {
        throw new Error('Response Plans API endpoint not yet implemented');
      },
      staleTime: 120000,
    });
  };
}

/**
 * Hook: useInvalidateIncidents
 * Manually invalidate all incident queries to force refetch
 *
 * @example
 * ```tsx
 * const invalidateIncidents = useInvalidateIncidents();
 *
 * // After external data change
 * invalidateIncidents();
 * ```
 */
export function useInvalidateIncidents() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: incidentQueryKeys.all });
  };
}

/**
 * Hook: useInvalidateResponsePlans
 * Manually invalidate all response plan queries to force refetch
 *
 * @example
 * ```tsx
 * const invalidatePlans = useInvalidateResponsePlans();
 *
 * // After external data change
 * invalidatePlans();
 * ```
 */
export function useInvalidateResponsePlans() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: responsePlanQueryKeys.all });
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

// Re-export types for consumers
export type {
  Incident,
  IncidentCreate,
  IncidentUpdate,
  ResponsePlan,
  ResponsePlanCreate,
  ResponsePlanUpdate,
  RecoveryMetrics,
  IncidentTimelineEntry,
  IncidentReport,
  IncidentStatusType,
  IncidentSeverityType,
  IncidentTypeType,
};

// Re-export enums
export { IncidentStatus, IncidentSeverity, IncidentType };
