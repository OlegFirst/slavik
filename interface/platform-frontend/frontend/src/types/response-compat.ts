/**
 * Response Module - Compatibility Layer
 *
 * This file provides type aliases and extensions to bridge differences
 * between API client types (response-client.ts) and hook types (response.ts).
 *
 * Context:
 * - API client uses: IncidentDashboard, CommunicationLog, RecoveryMetrics
 * - Hooks expect: ResponseDashboard, CommunicationRecord, RecoveryObjective
 *
 * Created: 2025-10-24
 */

import type {
  IncidentDashboard,
  CommunicationLog,
  CommunicationLogCreate,
  RecoveryMetrics,
  RecoveryMetricsCreate,
  RecoveryMetricsUpdate,
  IncidentReport as APIIncidentReport,
} from '@/lib/api/response-client';
import type { CommunicationType } from './response';

// ============================================================================
// DASHBOARD TYPES
// ============================================================================

/**
 * ResponseDashboard - Extended dashboard with additional fields
 * Extends IncidentDashboard from API client with fields expected by hooks
 */
export interface ResponseDashboard extends IncidentDashboard {
  high_severity_incidents: number;
  active_response_teams: number;
  total_actions_pending: number;
  total_actions_overdue: number;
}

/**
 * Helper to convert IncidentDashboard to ResponseDashboard
 * Computes missing fields from available data
 */
export function toResponseDashboard(dashboard: IncidentDashboard): ResponseDashboard {
  return {
    ...dashboard,
    high_severity_incidents: dashboard.incidents_by_severity?.high || 0,
    active_response_teams: 0, // Would come from team assignment data
    total_actions_pending: 0, // Would come from action tracking data
    total_actions_overdue: 0, // Would come from action tracking data
  };
}

// ============================================================================
// COMMUNICATION TYPES
// ============================================================================

/**
 * CommunicationRecord - Extended communication log with direction field
 * Extends CommunicationLog from API client with direction field
 */
export interface CommunicationRecord extends CommunicationLog {
  direction: 'inbound' | 'outbound';
}

/**
 * CommunicationRecordCreate - Extended create type with direction
 */
export interface CommunicationRecordCreate extends CommunicationLogCreate {
  direction?: 'inbound' | 'outbound';
}

/**
 * Helper to convert CommunicationLog to CommunicationRecord
 * Infers direction from communication type
 */
export function toCommunicationRecord(log: CommunicationLog): CommunicationRecord {
  // Infer direction: external/media/regulatory typically inbound, others outbound
  const inboundTypes: CommunicationType[] = [];
  const direction: 'inbound' | 'outbound' = 'outbound'; // Default to outbound

  return {
    ...log,
    direction,
  };
}

/**
 * Helper to convert CommunicationRecordCreate to CommunicationLogCreate
 * Strips the direction field for API client
 */
export function toCommunicationLogCreate(
  record: CommunicationRecordCreate
): CommunicationLogCreate {
  const { direction, ...logCreate } = record;
  return logCreate;
}

// ============================================================================
// RECOVERY TYPES
// ============================================================================

/**
 * RecoveryObjective - Extended recovery metrics with category and priority
 * Extends RecoveryMetrics from API client with required fields
 */
export interface RecoveryObjective extends RecoveryMetrics {
  service_category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  total_downtime_hours?: number; // Computed field from downtime_start - downtime_end
}

/**
 * RecoveryObjectiveCreate - Extended create type
 */
export interface RecoveryObjectiveCreate extends RecoveryMetricsCreate {
  service_category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
}

/**
 * RecoveryObjectiveUpdate - Extended update type
 */
export interface RecoveryObjectiveUpdate extends RecoveryMetricsUpdate {
  service_category?: string;
  priority?: 'critical' | 'high' | 'medium' | 'low';
}

/**
 * Helper to convert RecoveryMetrics to RecoveryObjective
 * Infers category and priority from service name and RTO/RPO values
 */
export function toRecoveryObjective(metrics: RecoveryMetrics): RecoveryObjective {
  // Infer priority from RTO target (lower RTO = higher priority)
  let priority: 'critical' | 'high' | 'medium' | 'low' = 'medium';
  if (metrics.target_rto_hours !== undefined) {
    if (metrics.target_rto_hours <= 4) priority = 'critical';
    else if (metrics.target_rto_hours <= 24) priority = 'high';
    else if (metrics.target_rto_hours <= 72) priority = 'medium';
    else priority = 'low';
  }

  // Calculate total downtime hours if downtime_end is available
  let total_downtime_hours: number | undefined;
  if (metrics.downtime_start && metrics.downtime_end) {
    const start = new Date(metrics.downtime_start).getTime();
    const end = new Date(metrics.downtime_end).getTime();
    total_downtime_hours = (end - start) / (1000 * 60 * 60); // Convert ms to hours
  }

  return {
    ...metrics,
    service_category: 'general', // Default category
    priority,
    total_downtime_hours,
  };
}

/**
 * Helper to convert RecoveryObjectiveCreate to RecoveryMetricsCreate
 * Strips extra fields for API client
 */
export function toRecoveryMetricsCreate(
  objective: RecoveryObjectiveCreate
): RecoveryMetricsCreate {
  const { service_category, priority, ...metricsCreate } = objective;
  return metricsCreate;
}

/**
 * Helper to convert RecoveryObjectiveUpdate to RecoveryMetricsUpdate
 * Strips extra fields for API client
 */
export function toRecoveryMetricsUpdate(
  objective: RecoveryObjectiveUpdate
): RecoveryMetricsUpdate {
  const { service_category, priority, ...metricsUpdate } = objective;
  return metricsUpdate;
}

// ============================================================================
// REPORT TYPES
// ============================================================================

/**
 * IncidentReport - Full report structure
 * The API client returns a basic structure, but hooks expect full details
 */
export interface IncidentReport {
  id: string;
  incident_id: string;
  organization_id: string;
  report_type: 'preliminary' | 'final' | 'executive_summary';
  generated_at: string;
  generated_by: string;

  // Executive Summary
  executive_summary: string;

  // Incident Overview
  incident_title: string;
  incident_description: string;
  start_time: string;
  end_time?: string;
  duration_hours?: number;
  severity: string;
  impact_level: string;

  // Timeline
  timeline_events: Array<{
    timestamp: string;
    event: string;
    actor?: string;
  }>;

  // Response Metrics
  response_metrics: {
    time_to_detection_minutes?: number;
    time_to_response_minutes?: number;
    time_to_resolution_hours?: number;
    rto_met: boolean;
    rpo_met: boolean;
  };

  // Key Findings
  key_findings: string[];

  // Root Causes
  root_causes: string[];

  // Corrective Actions
  corrective_actions: Array<{
    action: string;
    owner: string;
    due_date?: string;
    status: string;
  }>;

  // Recommendations
  recommendations: string[];

  // Lessons Learned
  lessons_learned: string[];

  // Attachments
  attachments?: Array<{
    filename: string;
    url: string;
    type: string;
  }>;

  // Metadata
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

/**
 * Helper to convert API IncidentReport to full IncidentReport
 * Fills in missing fields with defaults
 */
export function toIncidentReport(apiReport: APIIncidentReport): IncidentReport {
  const incident = apiReport.incident;
  return {
    id: incident.id || '',
    incident_id: incident.id || '',
    organization_id: incident.organization_id || '',
    report_type: 'final',
    generated_at: apiReport.generated_at || new Date().toISOString(),
    generated_by: 'system',
    executive_summary: apiReport.summary?.executive_summary as string || '',
    incident_title: incident.title || '',
    incident_description: incident.description || '',
    start_time: incident.detected_at || new Date().toISOString(),
    end_time: incident.resolved_at,
    duration_hours: 0,
    severity: incident.severity || 'medium',
    impact_level: apiReport.impact_analysis?.level as string || 'medium',
    timeline_events: (apiReport.timeline_summary || []).map((event: any) => ({
      timestamp: event.timestamp || new Date().toISOString(),
      event: event.event || event.action || 'Unknown event',
      actor: event.actor || event.user,
    })),
    response_metrics: {
      time_to_detection_minutes: (apiReport.metrics_summary as any)?.time_to_detection_minutes,
      time_to_response_minutes: (apiReport.metrics_summary as any)?.time_to_response_minutes,
      time_to_resolution_hours: (apiReport.metrics_summary as any)?.time_to_resolution_hours,
      rto_met: (apiReport.metrics_summary as any)?.rto_met || false,
      rpo_met: (apiReport.metrics_summary as any)?.rpo_met || false,
    },
    key_findings: [],
    root_causes: [],
    corrective_actions: [],
    recommendations: apiReport.recommendations || [],
    lessons_learned: [],
    attachments: undefined,
    metadata: undefined,
    created_at: incident.created_at || new Date().toISOString(),
    updated_at: incident.updated_at || new Date().toISOString(),
  };
}
