/**
 * Response Module - API Client
 * Handles all API communication for Incident Response module
 *
 * Created: 2025-10-24
 * Agent: 24 (Response Module Foundation)
 *
 * Total Endpoints: 37
 * - Incidents: 10 endpoints
 * - Response Actions: 4 endpoints
 * - Response Teams: 4 endpoints
 * - Communications: 2 endpoints
 * - Timeline: 1 endpoint
 * - Recovery Metrics: 3 endpoints
 * - Reporting: 1 endpoint
 * - Dashboard & Analytics: 2 endpoints
 * - Health: 1 endpoint
 */

import { apiClient } from './client';

// ==================== TYPE DEFINITIONS ====================

/**
 * Incident Severity Levels
 */
export enum IncidentSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Incident Lifecycle Status
 */
export enum IncidentStatus {
  DETECTED = 'detected',
  INVESTIGATING = 'investigating',
  CONTAINED = 'contained',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

/**
 * Types of Incidents
 */
export enum IncidentType {
  SECURITY_BREACH = 'security_breach',
  SYSTEM_FAILURE = 'system_failure',
  NATURAL_DISASTER = 'natural_disaster',
  HUMAN_ERROR = 'human_error',
  SUPPLIER_FAILURE = 'supplier_failure',
  CYBER_ATTACK = 'cyber_attack',
  DATA_BREACH = 'data_breach',
  SERVICE_DISRUPTION = 'service_disruption',
  INFRASTRUCTURE_FAILURE = 'infrastructure_failure',
  OTHER = 'other',
}

/**
 * Response Action Status
 */
export enum ActionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/**
 * Response Action Priority
 */
export enum ActionPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

/**
 * Communication Channel Types
 */
export enum CommunicationType {
  EMAIL = 'email',
  PHONE = 'phone',
  SMS = 'sms',
  MEETING = 'meeting',
  CHAT = 'chat',
  NOTIFICATION = 'notification',
  REPORT = 'report',
}

/**
 * Response Team Member Roles
 */
export enum TeamMemberRole {
  INCIDENT_MANAGER = 'incident_manager',
  TECHNICAL_LEAD = 'technical_lead',
  COMMUNICATIONS_LEAD = 'communications_lead',
  BUSINESS_CONTINUITY = 'business_continuity',
  SECURITY_ANALYST = 'security_analyst',
  LEGAL = 'legal',
  EXECUTIVE = 'executive',
  SUPPORT = 'support',
}

/**
 * Response Team Member
 */
export interface ResponseTeamMember {
  id?: string;
  team_id?: string;
  user_id: string;
  role: TeamMemberRole;
  name: string;
  email: string;
  phone?: string;
  is_primary?: boolean;
  availability_status?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Response Team Member Create
 */
export interface ResponseTeamMemberCreate {
  user_id: string;
  role: TeamMemberRole;
  name: string;
  email: string;
  phone?: string;
  is_primary?: boolean;
  availability_status?: string;
  notes?: string;
}

/**
 * Response Team Member Update
 */
export interface ResponseTeamMemberUpdate {
  role?: TeamMemberRole;
  name?: string;
  email?: string;
  phone?: string;
  is_primary?: boolean;
  availability_status?: string;
  notes?: string;
}

/**
 * Response Team
 */
export interface ResponseTeam {
  id?: string;
  organization_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  activation_criteria?: Record<string, any>;
  escalation_procedures?: Record<string, any>;
  members?: ResponseTeamMember[];
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

/**
 * Response Team Create
 */
export interface ResponseTeamCreate {
  name: string;
  description?: string;
  is_active?: boolean;
  activation_criteria?: Record<string, any>;
  escalation_procedures?: Record<string, any>;
  members?: ResponseTeamMemberCreate[];
}

/**
 * Response Team Update
 */
export interface ResponseTeamUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
  activation_criteria?: Record<string, any>;
  escalation_procedures?: Record<string, any>;
}

/**
 * Response Action
 */
export interface ResponseAction {
  id?: string;
  incident_id: string;
  title: string;
  description: string;
  action_type: string;
  priority: ActionPriority;
  status: ActionStatus;
  assigned_to?: string;
  assigned_to_name?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  started_at?: string;
  completed_at?: string;
  completion_notes?: string;
  dependencies?: string[];
  checklist?: Record<string, any>[];
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

/**
 * Response Action Create
 */
export interface ResponseActionCreate {
  title: string;
  description: string;
  action_type: string;
  priority: ActionPriority;
  assigned_to?: string;
  assigned_to_name?: string;
  due_date?: string;
  estimated_hours?: number;
  dependencies?: string[];
  checklist?: Record<string, any>[];
}

/**
 * Response Action Update
 */
export interface ResponseActionUpdate {
  title?: string;
  description?: string;
  action_type?: string;
  priority?: ActionPriority;
  status?: ActionStatus;
  assigned_to?: string;
  assigned_to_name?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  completion_notes?: string;
  dependencies?: string[];
  checklist?: Record<string, any>[];
}

/**
 * Communication Log
 */
export interface CommunicationLog {
  id?: string;
  incident_id: string;
  communication_type: CommunicationType;
  subject: string;
  content: string;
  sender: string;
  recipients: string[];
  cc_recipients?: string[];
  channel?: string;
  is_stakeholder_notification?: boolean;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

/**
 * Communication Log Create
 */
export interface CommunicationLogCreate {
  communication_type: CommunicationType;
  subject: string;
  content: string;
  sender: string;
  recipients: string[];
  cc_recipients?: string[];
  channel?: string;
  is_stakeholder_notification?: boolean;
  metadata?: Record<string, any>;
}

/**
 * Communication Log Update
 */
export interface CommunicationLogUpdate {
  subject?: string;
  content?: string;
  metadata?: Record<string, any>;
}

/**
 * Incident Timeline Entry
 */
export interface IncidentTimelineEntry {
  id: string;
  incident_id: string;
  timestamp: string;
  event_type: string;
  description: string;
  actor?: string;
  actor_id?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

/**
 * Recovery Metrics
 */
export interface RecoveryMetrics {
  id?: string;
  incident_id: string;
  service_name: string;
  target_rto_hours: number;
  target_rpo_hours: number;
  actual_rto_hours?: number;
  actual_rpo_hours?: number;
  downtime_start: string;
  downtime_end?: string;
  data_loss_start?: string;
  data_loss_end?: string;
  impact_description?: string;
  recovery_actions?: string[];
  rto_met?: boolean;
  rpo_met?: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Recovery Metrics Create
 */
export interface RecoveryMetricsCreate {
  service_name: string;
  target_rto_hours: number;
  target_rpo_hours: number;
  actual_rto_hours?: number;
  actual_rpo_hours?: number;
  downtime_start: string;
  downtime_end?: string;
  data_loss_start?: string;
  data_loss_end?: string;
  impact_description?: string;
  recovery_actions?: string[];
}

/**
 * Recovery Metrics Update
 */
export interface RecoveryMetricsUpdate {
  actual_rto_hours?: number;
  actual_rpo_hours?: number;
  downtime_end?: string;
  data_loss_start?: string;
  data_loss_end?: string;
  impact_description?: string;
  recovery_actions?: string[];
}

/**
 * Incident
 */
export interface Incident {
  id?: string;
  organization_id: string;
  incident_number: string;
  title: string;
  description: string;
  incident_type: IncidentType;
  severity: IncidentSeverity;
  status: IncidentStatus;
  affected_systems: string[];
  affected_locations?: string[];
  estimated_impact?: string;
  root_cause?: string;
  lessons_learned?: string;
  external_reference?: string;
  tags?: string[];
  detected_at: string;
  detected_by?: string;
  resolved_at?: string;
  closed_at?: string;
  duration_hours?: number;
  response_team_id?: string;
  response_team?: ResponseTeam;
  actions?: ResponseAction[];
  communications?: CommunicationLog[];
  timeline?: IncidentTimelineEntry[];
  metrics?: RecoveryMetrics[];
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
}

/**
 * Incident Create
 */
export interface IncidentCreate {
  title: string;
  description: string;
  incident_type: IncidentType;
  severity: IncidentSeverity;
  affected_systems: string[];
  affected_locations?: string[];
  estimated_impact?: string;
  external_reference?: string;
  tags?: string[];
  detected_at?: string;
  detected_by?: string;
  initial_response?: string;
}

/**
 * Incident Update
 */
export interface IncidentUpdate {
  title?: string;
  description?: string;
  incident_type?: IncidentType;
  severity?: IncidentSeverity;
  status?: IncidentStatus;
  affected_systems?: string[];
  affected_locations?: string[];
  estimated_impact?: string;
  root_cause?: string;
  lessons_learned?: string;
  external_reference?: string;
  tags?: string[];
}

/**
 * Incident Status Change
 */
export interface IncidentStatusChange {
  status: IncidentStatus;
  reason?: string;
  notes?: string;
}

/**
 * Incident Escalation
 */
export interface IncidentEscalation {
  escalation_reason: string;
  escalate_to?: string[];
  escalation_level: string;
  notify_stakeholders?: boolean;
  additional_notes?: string;
}

/**
 * Incident Report
 */
export interface IncidentReport {
  incident: Incident;
  summary: Record<string, any>;
  impact_analysis: Record<string, any>;
  timeline_summary: Record<string, any>[];
  actions_summary: Record<string, any>;
  metrics_summary: Record<string, any>;
  recommendations: string[];
  generated_at: string;
}

/**
 * Incident Dashboard
 */
export interface IncidentDashboard {
  organization_id: string;
  total_incidents: number;
  active_incidents: number;
  critical_incidents: number;
  incidents_by_status: Record<string, number>;
  incidents_by_severity: Record<string, number>;
  incidents_by_type: Record<string, number>;
  avg_resolution_hours?: number;
  avg_response_hours?: number;
  rto_compliance_rate?: number;
  rpo_compliance_rate?: number;
  recent_incidents: Incident[];
  trending_types: Record<string, any>[];
  period_start: string;
  period_end: string;
  generated_at: string;
}

/**
 * Organization Metrics
 */
export interface OrganizationMetrics {
  organization_id: string;
  total_incidents: number;
  total_actions: number;
  total_communications: number;
  avg_incident_duration_hours?: number;
  avg_actions_per_incident?: number;
  incidents_this_month: number;
  incidents_last_month: number;
  trend_percentage?: number;
  mttr?: number;
  mtbf?: number;
  calculated_at: string;
}

/**
 * Incident List Query Parameters
 */
export interface IncidentListQuery {
  status?: IncidentStatus;
  severity?: IncidentSeverity;
  incident_type?: IncidentType;
  from_date?: string;
  to_date?: string;
  search?: string;
  tags?: string[];
  skip?: number;
  limit?: number;
}

/**
 * Incident List Response
 */
export interface IncidentListResponse {
  items: Incident[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== API CLIENT ====================

const API_BASE = '/api/v1/response';

/**
 * Response Module API Client
 * Comprehensive client for all incident response endpoints
 */
export const responseClient = {
  // ============= INCIDENTS (10 functions) =============

  /**
   * Create new incident
   * POST /api/v1/response/incidents
   *
   * ISO 22301:2019 Clause 8.4.3 - Incident response structure
   */
  async createIncident(data: IncidentCreate): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'POST',
      url: `${API_BASE}/incidents`,
      data,
    });
  },

  /**
   * List incidents with filters and pagination
   * GET /api/v1/response/incidents
   */
  async listIncidents(params: IncidentListQuery): Promise<IncidentListResponse> {
    const query = new URLSearchParams();

    if (params.status) query.set('status_filter', params.status);
    if (params.severity) query.set('severity_filter', params.severity);
    if (params.incident_type) query.set('incident_type_filter', params.incident_type);
    if (params.from_date) query.set('from_date', params.from_date);
    if (params.to_date) query.set('to_date', params.to_date);
    if (params.search) query.set('search', params.search);
    if (params.skip !== undefined) query.set('skip', String(params.skip));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<IncidentListResponse>({
      method: 'GET',
      url: `${API_BASE}/incidents?${query.toString()}`,
    });
  },

  /**
   * Get single incident by ID
   * GET /api/v1/response/incidents/{incident_id}
   *
   * Returns detailed incident information including actions, communications, and timeline
   */
  async getIncident(incidentId: string): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}`,
    });
  },

  /**
   * Update incident
   * PUT /api/v1/response/incidents/{incident_id}
   */
  async updateIncident(incidentId: string, data: IncidentUpdate): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'PUT',
      url: `${API_BASE}/incidents/${incidentId}`,
      data,
    });
  },

  /**
   * Delete incident (soft delete)
   * DELETE /api/v1/response/incidents/{incident_id}
   */
  async deleteIncident(incidentId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${API_BASE}/incidents/${incidentId}`,
    });
  },

  /**
   * Change incident status
   * PATCH /api/v1/response/incidents/{incident_id}/status
   *
   * Status flow: detected → investigating → contained → resolved → closed
   */
  async changeIncidentStatus(incidentId: string, statusChange: IncidentStatusChange): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'PATCH',
      url: `${API_BASE}/incidents/${incidentId}/status`,
      data: statusChange,
    });
  },

  /**
   * Resolve incident
   * POST /api/v1/response/incidents/{incident_id}/resolve
   *
   * ISO 22301:2019 Clause 8.4.5 - Incident analysis
   */
  async resolveIncident(
    incidentId: string,
    rootCause?: string,
    lessonsLearned?: string
  ): Promise<Incident> {
    const query = new URLSearchParams();
    if (rootCause) query.set('root_cause', rootCause);
    if (lessonsLearned) query.set('lessons_learned', lessonsLearned);

    return apiClient.request<Incident>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/resolve?${query.toString()}`,
    });
  },

  /**
   * Close incident
   * POST /api/v1/response/incidents/{incident_id}/close
   */
  async closeIncident(incidentId: string): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/close`,
    });
  },

  /**
   * Reopen incident
   * POST /api/v1/response/incidents/{incident_id}/reopen
   */
  async reopenIncident(incidentId: string, reason: string): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/reopen`,
      data: { reason },
    });
  },

  /**
   * Escalate incident
   * POST /api/v1/response/incidents/{incident_id}/escalate
   *
   * ISO 22301:2019 Clause 8.4.2 - Incident escalation
   */
  async escalateIncident(incidentId: string, escalation: IncidentEscalation): Promise<Incident> {
    return apiClient.request<Incident>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/escalate`,
      data: escalation,
    });
  },

  // ============= RESPONSE ACTIONS (4 functions) =============

  /**
   * Add response action to incident
   * POST /api/v1/response/incidents/{incident_id}/actions
   */
  async addResponseAction(incidentId: string, actionData: ResponseActionCreate): Promise<ResponseAction> {
    return apiClient.request<ResponseAction>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/actions`,
      data: actionData,
    });
  },

  /**
   * List incident actions
   * GET /api/v1/response/incidents/{incident_id}/actions
   */
  async listIncidentActions(incidentId: string): Promise<ResponseAction[]> {
    return apiClient.request<ResponseAction[]>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}/actions`,
    });
  },

  /**
   * Update response action
   * PUT /api/v1/response/actions/{action_id}
   */
  async updateResponseAction(actionId: string, actionData: ResponseActionUpdate): Promise<ResponseAction> {
    return apiClient.request<ResponseAction>({
      method: 'PUT',
      url: `${API_BASE}/actions/${actionId}`,
      data: actionData,
    });
  },

  /**
   * Complete response action
   * POST /api/v1/response/actions/{action_id}/complete
   */
  async completeResponseAction(actionId: string, completionNotes?: string): Promise<ResponseAction> {
    return apiClient.request<ResponseAction>({
      method: 'POST',
      url: `${API_BASE}/actions/${actionId}/complete`,
      data: { completion_notes: completionNotes },
    });
  },

  // ============= RESPONSE TEAMS (4 functions) =============

  /**
   * Create response team
   * POST /api/v1/response/teams
   *
   * ISO 22301:2019 Clause 8.4.1 - Incident response team
   */
  async createResponseTeam(teamData: ResponseTeamCreate): Promise<ResponseTeam> {
    return apiClient.request<ResponseTeam>({
      method: 'POST',
      url: `${API_BASE}/teams`,
      data: teamData,
    });
  },

  /**
   * List response teams
   * GET /api/v1/response/teams
   */
  async listResponseTeams(isActive?: boolean): Promise<ResponseTeam[]> {
    const query = new URLSearchParams();
    if (isActive !== undefined) query.set('is_active', String(isActive));

    const url = query.toString() ? `${API_BASE}/teams?${query.toString()}` : `${API_BASE}/teams`;
    return apiClient.request<ResponseTeam[]>({
      method: 'GET',
      url,
    });
  },

  /**
   * Assign response team to incident
   * POST /api/v1/response/incidents/{incident_id}/team
   */
  async assignResponseTeam(incidentId: string, teamId: string): Promise<Incident> {
    const query = new URLSearchParams();
    query.set('team_id', teamId);

    return apiClient.request<Incident>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/team?${query.toString()}`,
    });
  },

  /**
   * Get incident response team
   * GET /api/v1/response/incidents/{incident_id}/team
   */
  async getIncidentTeam(incidentId: string): Promise<ResponseTeam | null> {
    return apiClient.request<ResponseTeam | null>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}/team`,
    });
  },

  // ============= COMMUNICATIONS (2 functions) =============

  /**
   * Log communication
   * POST /api/v1/response/incidents/{incident_id}/communications
   *
   * ISO 22301:2019 Clause 7.4 - Communication
   */
  async logCommunication(
    incidentId: string,
    communicationData: CommunicationLogCreate
  ): Promise<CommunicationLog> {
    return apiClient.request<CommunicationLog>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/communications`,
      data: communicationData,
    });
  },

  /**
   * List incident communications
   * GET /api/v1/response/incidents/{incident_id}/communications
   */
  async listIncidentCommunications(incidentId: string): Promise<CommunicationLog[]> {
    return apiClient.request<CommunicationLog[]>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}/communications`,
    });
  },

  // ============= TIMELINE (1 function) =============

  /**
   * Get incident timeline
   * GET /api/v1/response/incidents/{incident_id}/timeline
   *
   * Returns chronological timeline of incident events
   */
  async getIncidentTimeline(incidentId: string): Promise<IncidentTimelineEntry[]> {
    return apiClient.request<IncidentTimelineEntry[]>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}/timeline`,
    });
  },

  // ============= RECOVERY METRICS (3 functions) =============

  /**
   * Add recovery metrics
   * POST /api/v1/response/incidents/{incident_id}/metrics
   *
   * ISO 22301:2019 Clause 8.4.4 - Recovery time and point objectives
   */
  async addRecoveryMetrics(incidentId: string, metricsData: RecoveryMetricsCreate): Promise<RecoveryMetrics> {
    return apiClient.request<RecoveryMetrics>({
      method: 'POST',
      url: `${API_BASE}/incidents/${incidentId}/metrics`,
      data: metricsData,
    });
  },

  /**
   * Update recovery metrics
   * PUT /api/v1/response/metrics/{metrics_id}
   */
  async updateRecoveryMetrics(metricsId: string, metricsData: RecoveryMetricsUpdate): Promise<RecoveryMetrics> {
    return apiClient.request<RecoveryMetrics>({
      method: 'PUT',
      url: `${API_BASE}/metrics/${metricsId}`,
      data: metricsData,
    });
  },

  /**
   * Get incident metrics
   * GET /api/v1/response/incidents/{incident_id}/metrics
   */
  async getIncidentMetrics(incidentId: string): Promise<RecoveryMetrics[]> {
    return apiClient.request<RecoveryMetrics[]>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}/metrics`,
    });
  },

  // ============= REPORTING (1 function) =============

  /**
   * Generate incident report
   * GET /api/v1/response/incidents/{incident_id}/report
   *
   * ISO 22301:2019 Clause 8.4.5 - Incident reporting
   */
  async generateIncidentReport(incidentId: string): Promise<IncidentReport> {
    return apiClient.request<IncidentReport>({
      method: 'GET',
      url: `${API_BASE}/incidents/${incidentId}/report`,
    });
  },

  // ============= DASHBOARD & ANALYTICS (2 functions) =============

  /**
   * Get incident dashboard
   * GET /api/v1/response/dashboard
   *
   * ISO 22301:2019 Clause 9.1 - Monitoring, measurement, analysis and evaluation
   */
  async getIncidentDashboard(fromDate?: string, toDate?: string): Promise<IncidentDashboard> {
    const query = new URLSearchParams();
    if (fromDate) query.set('from_date', fromDate);
    if (toDate) query.set('to_date', toDate);

    const url = query.toString() ? `${API_BASE}/dashboard?${query.toString()}` : `${API_BASE}/dashboard`;
    return apiClient.request<IncidentDashboard>({
      method: 'GET',
      url,
    });
  },

  /**
   * Get organization metrics
   * GET /api/v1/response/metrics
   *
   * Includes: MTTR, MTBF, incident trends, RTO/RPO compliance
   */
  async getOrganizationMetrics(): Promise<OrganizationMetrics> {
    return apiClient.request<OrganizationMetrics>({
      method: 'GET',
      url: `${API_BASE}/metrics`,
    });
  },

  // ============= HEALTH (1 function) =============

  /**
   * Health check endpoint
   * GET /api/v1/response/health
   */
  async healthCheck(): Promise<{ status: string; service: string; iso_standard: string; timestamp: string }> {
    return apiClient.request<{ status: string; service: string; iso_standard: string; timestamp: string }>({
      method: 'GET',
      url: `${API_BASE}/health`,
    });
  },
};

// ==================== EXPORTED FUNCTIONS ====================

// Incidents
export async function createIncident(data: IncidentCreate): Promise<Incident> {
  return responseClient.createIncident(data);
}

export async function listIncidents(params: IncidentListQuery): Promise<IncidentListResponse> {
  return responseClient.listIncidents(params);
}

export async function getIncident(incidentId: string): Promise<Incident> {
  return responseClient.getIncident(incidentId);
}

export async function updateIncident(incidentId: string, data: IncidentUpdate): Promise<Incident> {
  return responseClient.updateIncident(incidentId, data);
}

export async function deleteIncident(incidentId: string): Promise<void> {
  return responseClient.deleteIncident(incidentId);
}

export async function changeIncidentStatus(
  incidentId: string,
  statusChange: IncidentStatusChange
): Promise<Incident> {
  return responseClient.changeIncidentStatus(incidentId, statusChange);
}

export async function resolveIncident(
  incidentId: string,
  rootCause?: string,
  lessonsLearned?: string
): Promise<Incident> {
  return responseClient.resolveIncident(incidentId, rootCause, lessonsLearned);
}

export async function closeIncident(incidentId: string): Promise<Incident> {
  return responseClient.closeIncident(incidentId);
}

export async function reopenIncident(incidentId: string, reason: string): Promise<Incident> {
  return responseClient.reopenIncident(incidentId, reason);
}

export async function escalateIncident(incidentId: string, escalation: IncidentEscalation): Promise<Incident> {
  return responseClient.escalateIncident(incidentId, escalation);
}

// Response Actions
export async function addResponseAction(
  incidentId: string,
  actionData: ResponseActionCreate
): Promise<ResponseAction> {
  return responseClient.addResponseAction(incidentId, actionData);
}

export async function listIncidentActions(incidentId: string): Promise<ResponseAction[]> {
  return responseClient.listIncidentActions(incidentId);
}

export async function updateResponseAction(
  actionId: string,
  actionData: ResponseActionUpdate
): Promise<ResponseAction> {
  return responseClient.updateResponseAction(actionId, actionData);
}

export async function completeResponseAction(actionId: string, completionNotes?: string): Promise<ResponseAction> {
  return responseClient.completeResponseAction(actionId, completionNotes);
}

// Response Teams
export async function createResponseTeam(teamData: ResponseTeamCreate): Promise<ResponseTeam> {
  return responseClient.createResponseTeam(teamData);
}

export async function listResponseTeams(isActive?: boolean): Promise<ResponseTeam[]> {
  return responseClient.listResponseTeams(isActive);
}

export async function assignResponseTeam(incidentId: string, teamId: string): Promise<Incident> {
  return responseClient.assignResponseTeam(incidentId, teamId);
}

export async function getIncidentTeam(incidentId: string): Promise<ResponseTeam | null> {
  return responseClient.getIncidentTeam(incidentId);
}

// Communications
export async function logCommunication(
  incidentId: string,
  communicationData: CommunicationLogCreate
): Promise<CommunicationLog> {
  return responseClient.logCommunication(incidentId, communicationData);
}

export async function listIncidentCommunications(incidentId: string): Promise<CommunicationLog[]> {
  return responseClient.listIncidentCommunications(incidentId);
}

// Timeline
export async function getIncidentTimeline(incidentId: string): Promise<IncidentTimelineEntry[]> {
  return responseClient.getIncidentTimeline(incidentId);
}

// Recovery Metrics
export async function addRecoveryMetrics(
  incidentId: string,
  metricsData: RecoveryMetricsCreate
): Promise<RecoveryMetrics> {
  return responseClient.addRecoveryMetrics(incidentId, metricsData);
}

export async function updateRecoveryMetrics(
  metricsId: string,
  metricsData: RecoveryMetricsUpdate
): Promise<RecoveryMetrics> {
  return responseClient.updateRecoveryMetrics(metricsId, metricsData);
}

export async function getIncidentMetrics(incidentId: string): Promise<RecoveryMetrics[]> {
  return responseClient.getIncidentMetrics(incidentId);
}

// Reporting
export async function generateIncidentReport(incidentId: string): Promise<IncidentReport> {
  return responseClient.generateIncidentReport(incidentId);
}

// Dashboard & Analytics
export async function getIncidentDashboard(fromDate?: string, toDate?: string): Promise<IncidentDashboard> {
  return responseClient.getIncidentDashboard(fromDate, toDate);
}

export async function getOrganizationMetrics(): Promise<OrganizationMetrics> {
  return responseClient.getOrganizationMetrics();
}

// Health
export async function healthCheck(): Promise<{ status: string; service: string; iso_standard: string; timestamp: string }> {
  return responseClient.healthCheck();
}

// Export default client
export default responseClient;
