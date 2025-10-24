/**
 * Response Module - Types & Enums
 * ISO 22301:2019 Clause 8.4 - Incident Response & Recovery
 * AI Platform ISO Project
 *
 * Created: 2025-10-24
 * Agent: 22 (Response Module Round 1)
 */

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Incident Status Enumeration
 * Lifecycle status of incident management
 */
export enum IncidentStatus {
  REPORTED = 'reported',
  INVESTIGATING = 'investigating',
  RESPONDING = 'responding',
  RECOVERING = 'recovering',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

/**
 * Incident Severity Enumeration
 * Severity classification for incident impact
 */
export enum IncidentSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Incident Type Enumeration
 * Classification of incident causes
 */
export enum IncidentType {
  NATURAL_DISASTER = 'natural_disaster',
  CYBER_ATTACK = 'cyber_attack',
  SYSTEM_FAILURE = 'system_failure',
  HUMAN_ERROR = 'human_error',
  PANDEMIC = 'pandemic',
  SECURITY_BREACH = 'security_breach',
  DATA_BREACH = 'data_breach',
  SUPPLIER_FAILURE = 'supplier_failure',
  SERVICE_DISRUPTION = 'service_disruption',
  INFRASTRUCTURE_FAILURE = 'infrastructure_failure',
  POWER_OUTAGE = 'power_outage',
  NETWORK_OUTAGE = 'network_outage',
  OTHER = 'other',
}

/**
 * Incident Category Enumeration
 * Business area categorization
 */
export enum IncidentCategory {
  IT_SYSTEMS = 'it_systems',
  FACILITIES = 'facilities',
  OPERATIONS = 'operations',
  HR = 'hr',
  SUPPLY_CHAIN = 'supply_chain',
  FINANCIAL = 'financial',
  SECURITY = 'security',
  ENVIRONMENTAL = 'environmental',
  REGULATORY = 'regulatory',
  REPUTATION = 'reputation',
}

/**
 * Response Status Enumeration
 * Status of response activities
 */
export enum ResponseStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ON_HOLD = 'on_hold',
  CANCELLED = 'cancelled',
}

/**
 * Response Priority Enumeration
 * Priority levels for response actions
 */
export enum ResponsePriority {
  IMMEDIATE = 'immediate',
  URGENT = 'urgent',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Escalation Level Enumeration
 * Escalation hierarchy levels
 */
export enum EscalationLevel {
  LEVEL_1 = 'level_1',
  LEVEL_2 = 'level_2',
  LEVEL_3 = 'level_3',
  EXECUTIVE = 'executive',
  BOARD = 'board',
}

/**
 * Team Role Enumeration
 * Response team member roles (ICS structure)
 */
export enum TeamRole {
  INCIDENT_COMMANDER = 'incident_commander',
  OPERATIONS_CHIEF = 'operations_chief',
  PLANNING_CHIEF = 'planning_chief',
  LOGISTICS_CHIEF = 'logistics_chief',
  FINANCE_CHIEF = 'finance_chief',
  TECHNICAL_LEAD = 'technical_lead',
  COMMUNICATIONS_LEAD = 'communications_lead',
  SECURITY_LEAD = 'security_lead',
  BUSINESS_CONTINUITY = 'business_continuity',
  LEGAL = 'legal',
  HR = 'hr',
  EXECUTIVE = 'executive',
  SUPPORT = 'support',
}

/**
 * Action Type Enumeration
 * Classification of response actions by phase
 */
export enum ActionType {
  IMMEDIATE = 'immediate',
  SHORT_TERM = 'short_term',
  RECOVERY = 'recovery',
  POST_INCIDENT = 'post_incident',
  PREVENTIVE = 'preventive',
  CORRECTIVE = 'corrective',
}

/**
 * Communication Type Enumeration
 * Types of communications during incident
 */
export enum CommunicationType {
  INTERNAL = 'internal',
  EXTERNAL = 'external',
  STAKEHOLDER = 'stakeholder',
  MEDIA = 'media',
  REGULATORY = 'regulatory',
  CUSTOMER = 'customer',
  PARTNER = 'partner',
  EMAIL = 'email',
  PHONE = 'phone',
  SMS = 'sms',
  MEETING = 'meeting',
  CHAT = 'chat',
  NOTIFICATION = 'notification',
  REPORT = 'report',
}

/**
 * Action Status Enumeration
 * Execution status of response actions
 */
export enum ActionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  BLOCKED = 'blocked',
}

/**
 * Plan Status Enumeration
 * Status of response plans
 */
export enum PlanStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  ARCHIVED = 'archived',
  UNDER_REVIEW = 'under_review',
}

/**
 * Recovery Phase Enumeration
 * Phases of recovery process
 */
export enum RecoveryPhase {
  ASSESSMENT = 'assessment',
  STABILIZATION = 'stabilization',
  RECOVERY = 'recovery',
  RESTORATION = 'restoration',
  NORMALIZATION = 'normalization',
}

// ============================================================================
// SUPPORTING TYPES
// ============================================================================

/**
 * Team Member Interface
 * Response team member details
 */
export interface TeamMember {
  user_id: string;
  role: TeamRole;
  name: string;
  email: string;
  phone?: string;
  is_primary: boolean;
  availability_status: 'available' | 'busy' | 'unavailable';
  notes?: string;
}

/**
 * Contact Information Interface
 * Emergency contact details
 */
export interface ContactInfo {
  name: string;
  role: string;
  phone_primary: string;
  phone_alternate?: string;
  email: string;
  availability: '24/7' | 'business_hours' | 'on_call';
}

/**
 * Escalation Criteria Interface
 * Conditions for escalation
 */
export interface EscalationCriteria {
  level: EscalationLevel;
  triggers: string[];
  contacts: ContactInfo[];
  timeframe_minutes: number;
}

/**
 * Recovery Target Interface
 * Recovery time and point objectives
 */
export interface RecoveryTarget {
  service_name: string;
  rto_minutes: number; // Recovery Time Objective
  rpo_minutes: number; // Recovery Point Objective
  mtpd_minutes: number; // Maximum Tolerable Period of Disruption
}

/**
 * Timeline Event Interface
 * Single event in incident timeline
 */
export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  actor?: string;
  actor_id?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Action Checklist Item Interface
 * Individual checklist item within an action
 */
export interface ChecklistItem {
  id: string;
  description: string;
  completed: boolean;
  completed_by?: string;
  completed_at?: string;
}

/**
 * Resource Requirement Interface
 * Resources needed for response
 */
export interface ResourceRequirement {
  resource_type: 'personnel' | 'equipment' | 'facility' | 'technology' | 'financial';
  resource_name: string;
  quantity: number;
  allocated: number;
  status: 'requested' | 'allocated' | 'deployed';
}

/**
 * Impact Assessment Interface
 * Business impact details
 */
export interface ImpactAssessment {
  affected_services: string[];
  affected_customers: number;
  financial_impact?: number;
  operational_impact: 'critical' | 'high' | 'medium' | 'low';
  reputational_impact: 'critical' | 'high' | 'medium' | 'low';
  regulatory_impact?: string;
}

// ============================================================================
// MAIN INTERFACES
// ============================================================================

/**
 * Incident Interface
 * Core incident record - primary entity for incident management
 */
export interface Incident {
  id: string;
  organization_id: string;

  // Identification
  incident_number: string;
  title: string;
  description: string;

  // Classification
  incident_type: IncidentType;
  category: IncidentCategory;
  severity: IncidentSeverity;
  status: IncidentStatus;

  // Impact
  affected_systems: string[];
  affected_locations?: string[];
  estimated_impact?: string;
  impact_assessment?: ImpactAssessment;

  // Timeline
  detected_at: string;
  detected_by?: string;
  reported_at?: string;
  reported_by?: string;
  acknowledged_at?: string;
  response_started_at?: string;
  contained_at?: string;
  resolved_at?: string;
  closed_at?: string;
  duration_hours?: number;

  // Assignment
  response_team_id?: string;
  incident_commander?: string;
  incident_commander_id?: string;

  // Analysis
  root_cause?: string;
  contributing_factors?: string[];
  lessons_learned?: string;
  recommendations?: string[];

  // References
  external_reference?: string;
  related_incidents?: string[];
  tags?: string[];

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
  updated_by?: string;
}

/**
 * Response Plan Interface
 * Pre-defined response procedures for incident types
 */
export interface ResponsePlan {
  id: string;
  organization_id: string;

  // Plan Details
  plan_name: string;
  plan_code: string;
  description: string;
  status: PlanStatus;
  version: string;

  // Scope
  incident_types: IncidentType[];
  severity_levels: IncidentSeverity[];
  applicable_categories: IncidentCategory[];

  // Activation
  activation_criteria: string[];
  auto_activate: boolean;

  // Response Structure
  response_team_template?: string;
  initial_actions: string[];
  escalation_rules: EscalationCriteria[];

  // Resources
  required_resources: ResourceRequirement[];
  contact_list: ContactInfo[];

  // Testing
  last_tested_at?: string;
  test_results?: string;
  next_test_date?: string;

  // Review
  last_reviewed_at?: string;
  next_review_date?: string;
  approved_by?: string;
  approved_at?: string;

  // Metadata
  created_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * Response Team Interface
 * Incident response team structure and members
 */
export interface ResponseTeam {
  id: string;
  organization_id: string;

  // Team Details
  name: string;
  description?: string;
  is_active: boolean;

  // Members
  members: TeamMember[];

  // Configuration
  activation_criteria?: Record<string, unknown>;
  escalation_procedures?: Record<string, unknown>;
  roles_required: TeamRole[];

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Response Action Interface
 * Actions and tasks during incident response
 */
export interface ResponseAction {
  id: string;
  incident_id: string;

  // Action Details
  title: string;
  description: string;
  action_type: ActionType;
  priority: ResponsePriority;

  // Assignment
  assigned_to?: string;
  assigned_to_name?: string;
  backup_assigned?: string;

  // Status
  status: ActionStatus;
  progress_percentage: number;

  // Timeline
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  started_at?: string;
  completed_at?: string;

  // Dependencies
  dependencies?: string[];
  blocks?: string[];

  // Checklist
  checklist?: ChecklistItem[];
  checklist_completed: number;
  checklist_total: number;

  // Completion
  completion_notes?: string;
  effectiveness_rating?: number; // 1-5 scale

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Incident Log Interface
 * Chronological log of incident events
 */
export interface IncidentLog {
  id: string;
  incident_id: string;

  // Event Details
  timestamp: string;
  event_type: string;
  description: string;
  severity?: 'info' | 'warning' | 'critical';

  // Actor
  actor?: string;
  actor_id?: string;
  actor_role?: TeamRole;

  // Context
  related_action_id?: string;
  related_communication_id?: string;
  metadata?: Record<string, unknown>;

  // Metadata
  created_at: string;
}

/**
 * Escalation Rule Interface
 * Escalation procedures and triggers
 */
export interface EscalationRule {
  id: string;
  organization_id: string;

  // Rule Details
  rule_name: string;
  description: string;
  is_active: boolean;

  // Triggers
  trigger_conditions: string[];
  trigger_timeframe_minutes?: number;
  incident_severity: IncidentSeverity[];
  incident_types: IncidentType[];

  // Escalation
  escalation_level: EscalationLevel;
  escalate_to_roles: TeamRole[];
  escalate_to_users?: string[];
  notification_template?: string;

  // Actions
  automatic_actions?: string[];
  require_acknowledgment: boolean;

  // Metadata
  created_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * Communication Record Interface
 * Communications log during incident
 */
export interface CommunicationRecord {
  id: string;
  incident_id: string;

  // Communication Details
  communication_type: CommunicationType;
  subject: string;
  content: string;

  // Participants
  sender: string;
  sender_id?: string;
  recipients: string[];
  cc_recipients?: string[];

  // Channel
  channel?: string;
  direction: 'inbound' | 'outbound';
  is_stakeholder_notification: boolean;

  // Status
  sent_at?: string;
  delivery_status?: 'sent' | 'delivered' | 'failed';
  read_at?: string;

  // Attachments
  attachments?: string[];

  // Metadata
  metadata?: Record<string, unknown>;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Resource Allocation Interface
 * Resource assignment and tracking
 */
export interface ResourceAllocation {
  id: string;
  incident_id: string;

  // Resource Details
  resource_type: 'personnel' | 'equipment' | 'facility' | 'technology' | 'financial';
  resource_name: string;
  description?: string;

  // Allocation
  quantity_requested: number;
  quantity_allocated: number;
  allocation_status: 'requested' | 'approved' | 'allocated' | 'deployed' | 'released';

  // Assignment
  requested_by: string;
  approved_by?: string;
  allocated_by?: string;

  // Timeline
  requested_at: string;
  approved_at?: string;
  allocated_at?: string;
  deployed_at?: string;
  released_at?: string;

  // Cost
  estimated_cost?: number;
  actual_cost?: number;

  // Metadata
  notes?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Recovery Objective Interface
 * Recovery time and point objectives tracking
 */
export interface RecoveryObjective {
  id: string;
  incident_id: string;

  // Service Details
  service_name: string;
  service_category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';

  // Target Objectives
  target_rto_hours: number; // Recovery Time Objective
  target_rpo_hours: number; // Recovery Point Objective
  target_mtpd_hours?: number; // Maximum Tolerable Period of Disruption

  // Actual Performance
  actual_rto_hours?: number;
  actual_rpo_hours?: number;
  rto_met?: boolean;
  rpo_met?: boolean;

  // Downtime Tracking
  downtime_start: string;
  downtime_end?: string;
  total_downtime_hours?: number;

  // Data Loss Tracking
  data_loss_start?: string;
  data_loss_end?: string;
  data_loss_amount?: string;

  // Impact
  impact_description?: string;
  recovery_actions?: string[];
  customers_affected?: number;
  financial_impact?: number;

  // Metadata
  created_at: string;
  updated_at: string;
}

/**
 * Incident Report Interface
 * Comprehensive post-incident report
 */
export interface IncidentReport {
  id: string;
  incident_id: string;
  organization_id: string;

  // Report Details
  report_type: 'preliminary' | 'interim' | 'final' | 'post_incident_review';
  report_title: string;
  report_date: string;

  // Executive Summary
  executive_summary: string;
  key_findings: string[];
  recommendations: string[];

  // Incident Overview
  incident_overview: {
    detection: string;
    response: string;
    resolution: string;
    impact: ImpactAssessment;
  };

  // Timeline
  timeline_summary: TimelineEvent[];
  critical_events: TimelineEvent[];

  // Actions Analysis
  actions_taken: string[];
  actions_effective: string[];
  actions_ineffective: string[];
  improvement_opportunities: string[];

  // Recovery Metrics
  recovery_metrics: {
    total_downtime_hours: number;
    rto_compliance: boolean;
    rpo_compliance: boolean;
    services_affected: number;
    services_recovered: number;
  };

  // Root Cause
  root_cause_analysis?: {
    method: string;
    root_causes: string[];
    contributing_factors: string[];
    evidence: string[];
  };

  // Lessons Learned
  lessons_learned: {
    what_worked_well: string[];
    what_needs_improvement: string[];
    action_items: string[];
  };

  // Compliance
  regulatory_notifications?: string[];
  compliance_requirements?: string[];

  // Approvals
  prepared_by: string;
  reviewed_by?: string;
  approved_by?: string;
  approval_date?: string;

  // Metadata
  created_at: string;
  updated_at: string;
}

// ============================================================================
// DASHBOARD & ANALYTICS TYPES
// ============================================================================

/**
 * Response Dashboard Interface
 * Summary dashboard data for response overview
 */
export interface ResponseDashboard {
  organization_id: string;

  // Active Incidents
  active_incidents: number;
  critical_incidents: number;
  high_severity_incidents: number;

  // Incidents by Status
  incidents_by_status: Record<IncidentStatus, number>;

  // Incidents by Type
  incidents_by_type: Record<IncidentType, number>;

  // Incidents by Severity
  incidents_by_severity: Record<IncidentSeverity, number>;

  // Performance Metrics
  avg_detection_time_minutes?: number;
  avg_response_time_minutes?: number;
  avg_resolution_time_hours?: number;
  mttr?: number; // Mean Time To Resolve
  mtbf?: number; // Mean Time Between Failures

  // Recovery Compliance
  rto_compliance_rate: number; // percentage
  rpo_compliance_rate: number; // percentage

  // Team Performance
  active_response_teams: number;
  total_actions_pending: number;
  total_actions_overdue: number;

  // Recent Activity
  recent_incidents: Incident[];
  trending_types: Array<{ type: IncidentType; count: number; trend: 'up' | 'down' | 'stable' }>;

  // Period
  period_start: string;
  period_end: string;
  generated_at: string;
}

/**
 * Incident Metrics Interface
 * Detailed metrics for incident analysis
 */
export interface IncidentMetrics {
  incident_id: string;

  // Timeline Metrics
  detection_to_report_minutes: number;
  report_to_acknowledge_minutes: number;
  acknowledge_to_response_minutes: number;
  response_to_contained_minutes: number;
  contained_to_resolved_hours: number;
  total_duration_hours: number;

  // Action Metrics
  total_actions: number;
  actions_completed: number;
  actions_on_time: number;
  actions_delayed: number;
  avg_action_completion_hours: number;

  // Communication Metrics
  total_communications: number;
  internal_communications: number;
  external_communications: number;
  stakeholder_notifications: number;

  // Resource Metrics
  resources_requested: number;
  resources_allocated: number;
  total_resource_cost?: number;

  // Recovery Metrics
  services_affected: number;
  services_recovered: number;
  rto_met_count: number;
  rpo_met_count: number;
  rto_compliance_rate: number;
  rpo_compliance_rate: number;

  // Calculated
  calculated_at: string;
}

/**
 * Response Trend Interface
 * Trending data for response analytics
 */
export interface ResponseTrend {
  date: string;
  incidents_count: number;
  critical_count: number;
  high_count: number;
  avg_resolution_hours: number;
  rto_compliance_rate: number;
}

/**
 * Response Trends Response Interface
 * Historical response trends
 */
export interface ResponseTrendsResponse {
  period_days: number;
  trend: 'improving' | 'stable' | 'declining';
  data_points: ResponseTrend[];
  summary: {
    total_incidents: number;
    avg_resolution_hours: number;
    rto_compliance_rate: number;
    most_common_type: IncidentType;
  };
}

// ============================================================================
// CREATE/UPDATE TYPES
// ============================================================================

/**
 * Incident Creation Payload
 */
export type IncidentCreate = Omit<Incident, 'id' | 'incident_number' | 'created_at' | 'updated_at'>;

/**
 * Incident Update Payload
 */
export type IncidentUpdate = Partial<IncidentCreate>;

/**
 * Response Plan Creation Payload
 */
export type ResponsePlanCreate = Omit<ResponsePlan, 'id' | 'created_at' | 'updated_at'>;

/**
 * Response Plan Update Payload
 */
export type ResponsePlanUpdate = Partial<ResponsePlanCreate>;

/**
 * Response Team Creation Payload
 */
export type ResponseTeamCreate = Omit<ResponseTeam, 'id' | 'created_at' | 'updated_at'>;

/**
 * Response Team Update Payload
 */
export type ResponseTeamUpdate = Partial<ResponseTeamCreate>;

/**
 * Response Action Creation Payload
 */
export type ResponseActionCreate = Omit<ResponseAction, 'id' | 'created_at' | 'updated_at' | 'progress_percentage' | 'checklist_completed' | 'checklist_total'>;

/**
 * Response Action Update Payload
 */
export type ResponseActionUpdate = Partial<ResponseActionCreate>;

/**
 * Escalation Rule Creation Payload
 */
export type EscalationRuleCreate = Omit<EscalationRule, 'id' | 'created_at' | 'updated_at'>;

/**
 * Escalation Rule Update Payload
 */
export type EscalationRuleUpdate = Partial<EscalationRuleCreate>;

/**
 * Communication Record Creation Payload
 */
export type CommunicationRecordCreate = Omit<CommunicationRecord, 'id' | 'created_at' | 'updated_at'>;

/**
 * Communication Record Update Payload
 */
export type CommunicationRecordUpdate = Partial<CommunicationRecordCreate>;

/**
 * Resource Allocation Creation Payload
 */
export type ResourceAllocationCreate = Omit<ResourceAllocation, 'id' | 'created_at' | 'updated_at'>;

/**
 * Resource Allocation Update Payload
 */
export type ResourceAllocationUpdate = Partial<ResourceAllocationCreate>;

/**
 * Recovery Objective Creation Payload
 */
export type RecoveryObjectiveCreate = Omit<RecoveryObjective, 'id' | 'created_at' | 'updated_at'>;

/**
 * Recovery Objective Update Payload
 */
export type RecoveryObjectiveUpdate = Partial<RecoveryObjectiveCreate>;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get incident status label with proper formatting
 * @param status - Incident status enum value
 * @returns Human-readable label
 */
export function getIncidentStatusLabel(status: IncidentStatus): string {
  const labels: Record<IncidentStatus, string> = {
    [IncidentStatus.REPORTED]: 'Reported',
    [IncidentStatus.INVESTIGATING]: 'Investigating',
    [IncidentStatus.RESPONDING]: 'Responding',
    [IncidentStatus.RECOVERING]: 'Recovering',
    [IncidentStatus.RESOLVED]: 'Resolved',
    [IncidentStatus.CLOSED]: 'Closed',
  };
  return labels[status] || 'Unknown';
}

/**
 * Get incident status color for visual representation
 * @param status - Incident status enum value
 * @returns Tailwind CSS color class
 */
export function getIncidentStatusColor(status: IncidentStatus): string {
  const colors: Record<IncidentStatus, string> = {
    [IncidentStatus.REPORTED]: 'orange-500',
    [IncidentStatus.INVESTIGATING]: 'yellow-500',
    [IncidentStatus.RESPONDING]: 'blue-600',
    [IncidentStatus.RECOVERING]: 'purple-500',
    [IncidentStatus.RESOLVED]: 'green-600',
    [IncidentStatus.CLOSED]: 'gray-500',
  };
  return colors[status] || 'gray-400';
}

/**
 * Get incident status icon for visual representation
 * @param status - Incident status enum value
 * @returns Lucide icon name
 */
export function getIncidentStatusIcon(status: IncidentStatus): string {
  const icons: Record<IncidentStatus, string> = {
    [IncidentStatus.REPORTED]: 'Bell',
    [IncidentStatus.INVESTIGATING]: 'Search',
    [IncidentStatus.RESPONDING]: 'Activity',
    [IncidentStatus.RECOVERING]: 'RefreshCw',
    [IncidentStatus.RESOLVED]: 'CheckCircle',
    [IncidentStatus.CLOSED]: 'Archive',
  };
  return icons[status] || 'HelpCircle';
}

/**
 * Get incident severity label with proper formatting
 * @param severity - Incident severity enum value
 * @returns Human-readable label
 */
export function getIncidentSeverityLabel(severity: IncidentSeverity): string {
  const labels: Record<IncidentSeverity, string> = {
    [IncidentSeverity.CRITICAL]: 'Critical',
    [IncidentSeverity.HIGH]: 'High',
    [IncidentSeverity.MEDIUM]: 'Medium',
    [IncidentSeverity.LOW]: 'Low',
  };
  return labels[severity] || 'Unknown';
}

/**
 * Get incident severity color for visual representation
 * @param severity - Incident severity enum value
 * @returns Tailwind CSS color class
 */
export function getIncidentSeverityColor(severity: IncidentSeverity): string {
  const colors: Record<IncidentSeverity, string> = {
    [IncidentSeverity.CRITICAL]: 'red-600',
    [IncidentSeverity.HIGH]: 'orange-500',
    [IncidentSeverity.MEDIUM]: 'yellow-500',
    [IncidentSeverity.LOW]: 'blue-500',
  };
  return colors[severity] || 'gray-400';
}

/**
 * Get incident severity icon for visual representation
 * @param severity - Incident severity enum value
 * @returns Lucide icon name
 */
export function getIncidentSeverityIcon(severity: IncidentSeverity): string {
  const icons: Record<IncidentSeverity, string> = {
    [IncidentSeverity.CRITICAL]: 'AlertOctagon',
    [IncidentSeverity.HIGH]: 'AlertTriangle',
    [IncidentSeverity.MEDIUM]: 'AlertCircle',
    [IncidentSeverity.LOW]: 'Info',
  };
  return icons[severity] || 'HelpCircle';
}

/**
 * Get incident type label with proper formatting
 * @param type - Incident type enum value
 * @returns Human-readable label
 */
export function getIncidentTypeLabel(type: IncidentType): string {
  const labels: Record<IncidentType, string> = {
    [IncidentType.NATURAL_DISASTER]: 'Natural Disaster',
    [IncidentType.CYBER_ATTACK]: 'Cyber Attack',
    [IncidentType.SYSTEM_FAILURE]: 'System Failure',
    [IncidentType.HUMAN_ERROR]: 'Human Error',
    [IncidentType.PANDEMIC]: 'Pandemic',
    [IncidentType.SECURITY_BREACH]: 'Security Breach',
    [IncidentType.DATA_BREACH]: 'Data Breach',
    [IncidentType.SUPPLIER_FAILURE]: 'Supplier Failure',
    [IncidentType.SERVICE_DISRUPTION]: 'Service Disruption',
    [IncidentType.INFRASTRUCTURE_FAILURE]: 'Infrastructure Failure',
    [IncidentType.POWER_OUTAGE]: 'Power Outage',
    [IncidentType.NETWORK_OUTAGE]: 'Network Outage',
    [IncidentType.OTHER]: 'Other',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get incident type color for visual representation
 * @param type - Incident type enum value
 * @returns Tailwind CSS color class
 */
export function getIncidentTypeColor(type: IncidentType): string {
  const colors: Record<IncidentType, string> = {
    [IncidentType.NATURAL_DISASTER]: 'orange-600',
    [IncidentType.CYBER_ATTACK]: 'red-600',
    [IncidentType.SYSTEM_FAILURE]: 'blue-600',
    [IncidentType.HUMAN_ERROR]: 'yellow-600',
    [IncidentType.PANDEMIC]: 'purple-600',
    [IncidentType.SECURITY_BREACH]: 'red-700',
    [IncidentType.DATA_BREACH]: 'red-800',
    [IncidentType.SUPPLIER_FAILURE]: 'orange-500',
    [IncidentType.SERVICE_DISRUPTION]: 'blue-500',
    [IncidentType.INFRASTRUCTURE_FAILURE]: 'indigo-600',
    [IncidentType.POWER_OUTAGE]: 'amber-600',
    [IncidentType.NETWORK_OUTAGE]: 'cyan-600',
    [IncidentType.OTHER]: 'gray-600',
  };
  return colors[type] || 'gray-400';
}

/**
 * Get incident type icon for visual representation
 * @param type - Incident type enum value
 * @returns Lucide icon name
 */
export function getIncidentTypeIcon(type: IncidentType): string {
  const icons: Record<IncidentType, string> = {
    [IncidentType.NATURAL_DISASTER]: 'CloudLightning',
    [IncidentType.CYBER_ATTACK]: 'Shield',
    [IncidentType.SYSTEM_FAILURE]: 'Server',
    [IncidentType.HUMAN_ERROR]: 'UserX',
    [IncidentType.PANDEMIC]: 'Thermometer',
    [IncidentType.SECURITY_BREACH]: 'ShieldAlert',
    [IncidentType.DATA_BREACH]: 'Database',
    [IncidentType.SUPPLIER_FAILURE]: 'Package',
    [IncidentType.SERVICE_DISRUPTION]: 'XCircle',
    [IncidentType.INFRASTRUCTURE_FAILURE]: 'HardDrive',
    [IncidentType.POWER_OUTAGE]: 'Zap',
    [IncidentType.NETWORK_OUTAGE]: 'Wifi',
    [IncidentType.OTHER]: 'HelpCircle',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get incident category label with proper formatting
 * @param category - Incident category enum value
 * @returns Human-readable label
 */
export function getIncidentCategoryLabel(category: IncidentCategory): string {
  const labels: Record<IncidentCategory, string> = {
    [IncidentCategory.IT_SYSTEMS]: 'IT Systems',
    [IncidentCategory.FACILITIES]: 'Facilities',
    [IncidentCategory.OPERATIONS]: 'Operations',
    [IncidentCategory.HR]: 'Human Resources',
    [IncidentCategory.SUPPLY_CHAIN]: 'Supply Chain',
    [IncidentCategory.FINANCIAL]: 'Financial',
    [IncidentCategory.SECURITY]: 'Security',
    [IncidentCategory.ENVIRONMENTAL]: 'Environmental',
    [IncidentCategory.REGULATORY]: 'Regulatory',
    [IncidentCategory.REPUTATION]: 'Reputation',
  };
  return labels[category] || 'Unknown';
}

/**
 * Get incident category color for visual representation
 * @param category - Incident category enum value
 * @returns Tailwind CSS color class
 */
export function getIncidentCategoryColor(category: IncidentCategory): string {
  const colors: Record<IncidentCategory, string> = {
    [IncidentCategory.IT_SYSTEMS]: 'blue-600',
    [IncidentCategory.FACILITIES]: 'amber-600',
    [IncidentCategory.OPERATIONS]: 'purple-600',
    [IncidentCategory.HR]: 'pink-600',
    [IncidentCategory.SUPPLY_CHAIN]: 'orange-600',
    [IncidentCategory.FINANCIAL]: 'green-600',
    [IncidentCategory.SECURITY]: 'red-600',
    [IncidentCategory.ENVIRONMENTAL]: 'teal-600',
    [IncidentCategory.REGULATORY]: 'indigo-600',
    [IncidentCategory.REPUTATION]: 'rose-600',
  };
  return colors[category] || 'gray-400';
}

/**
 * Get incident category icon for visual representation
 * @param category - Incident category enum value
 * @returns Lucide icon name
 */
export function getIncidentCategoryIcon(category: IncidentCategory): string {
  const icons: Record<IncidentCategory, string> = {
    [IncidentCategory.IT_SYSTEMS]: 'Monitor',
    [IncidentCategory.FACILITIES]: 'Building2',
    [IncidentCategory.OPERATIONS]: 'Activity',
    [IncidentCategory.HR]: 'Users',
    [IncidentCategory.SUPPLY_CHAIN]: 'Truck',
    [IncidentCategory.FINANCIAL]: 'DollarSign',
    [IncidentCategory.SECURITY]: 'Lock',
    [IncidentCategory.ENVIRONMENTAL]: 'Leaf',
    [IncidentCategory.REGULATORY]: 'Scale',
    [IncidentCategory.REPUTATION]: 'Star',
  };
  return icons[category] || 'HelpCircle';
}

/**
 * Get response status label with proper formatting
 * @param status - Response status enum value
 * @returns Human-readable label
 */
export function getResponseStatusLabel(status: ResponseStatus): string {
  const labels: Record<ResponseStatus, string> = {
    [ResponseStatus.NOT_STARTED]: 'Not Started',
    [ResponseStatus.IN_PROGRESS]: 'In Progress',
    [ResponseStatus.COMPLETED]: 'Completed',
    [ResponseStatus.ON_HOLD]: 'On Hold',
    [ResponseStatus.CANCELLED]: 'Cancelled',
  };
  return labels[status] || 'Unknown';
}

/**
 * Get response status color for visual representation
 * @param status - Response status enum value
 * @returns Tailwind CSS color class
 */
export function getResponseStatusColor(status: ResponseStatus): string {
  const colors: Record<ResponseStatus, string> = {
    [ResponseStatus.NOT_STARTED]: 'gray-500',
    [ResponseStatus.IN_PROGRESS]: 'blue-600',
    [ResponseStatus.COMPLETED]: 'green-600',
    [ResponseStatus.ON_HOLD]: 'yellow-500',
    [ResponseStatus.CANCELLED]: 'gray-400',
  };
  return colors[status] || 'gray-400';
}

/**
 * Get response status icon for visual representation
 * @param status - Response status enum value
 * @returns Lucide icon name
 */
export function getResponseStatusIcon(status: ResponseStatus): string {
  const icons: Record<ResponseStatus, string> = {
    [ResponseStatus.NOT_STARTED]: 'Circle',
    [ResponseStatus.IN_PROGRESS]: 'PlayCircle',
    [ResponseStatus.COMPLETED]: 'CheckCircle',
    [ResponseStatus.ON_HOLD]: 'PauseCircle',
    [ResponseStatus.CANCELLED]: 'XCircle',
  };
  return icons[status] || 'HelpCircle';
}

/**
 * Get response priority label with proper formatting
 * @param priority - Response priority enum value
 * @returns Human-readable label
 */
export function getResponsePriorityLabel(priority: ResponsePriority): string {
  const labels: Record<ResponsePriority, string> = {
    [ResponsePriority.IMMEDIATE]: 'Immediate',
    [ResponsePriority.URGENT]: 'Urgent',
    [ResponsePriority.HIGH]: 'High',
    [ResponsePriority.MEDIUM]: 'Medium',
    [ResponsePriority.LOW]: 'Low',
  };
  return labels[priority] || 'Unknown';
}

/**
 * Get response priority color for visual representation
 * @param priority - Response priority enum value
 * @returns Tailwind CSS color class
 */
export function getResponsePriorityColor(priority: ResponsePriority): string {
  const colors: Record<ResponsePriority, string> = {
    [ResponsePriority.IMMEDIATE]: 'red-700',
    [ResponsePriority.URGENT]: 'red-600',
    [ResponsePriority.HIGH]: 'orange-500',
    [ResponsePriority.MEDIUM]: 'yellow-500',
    [ResponsePriority.LOW]: 'gray-500',
  };
  return colors[priority] || 'gray-400';
}

/**
 * Get response priority icon for visual representation
 * @param priority - Response priority enum value
 * @returns Lucide icon name
 */
export function getResponsePriorityIcon(priority: ResponsePriority): string {
  const icons: Record<ResponsePriority, string> = {
    [ResponsePriority.IMMEDIATE]: 'Flame',
    [ResponsePriority.URGENT]: 'AlertOctagon',
    [ResponsePriority.HIGH]: 'ArrowUp',
    [ResponsePriority.MEDIUM]: 'Minus',
    [ResponsePriority.LOW]: 'ArrowDown',
  };
  return icons[priority] || 'HelpCircle';
}

/**
 * Get escalation level label with proper formatting
 * @param level - Escalation level enum value
 * @returns Human-readable label
 */
export function getEscalationLevelLabel(level: EscalationLevel): string {
  const labels: Record<EscalationLevel, string> = {
    [EscalationLevel.LEVEL_1]: 'Level 1 - Team Lead',
    [EscalationLevel.LEVEL_2]: 'Level 2 - Manager',
    [EscalationLevel.LEVEL_3]: 'Level 3 - Director',
    [EscalationLevel.EXECUTIVE]: 'Executive Level',
    [EscalationLevel.BOARD]: 'Board Level',
  };
  return labels[level] || 'Unknown';
}

/**
 * Get escalation level color for visual representation
 * @param level - Escalation level enum value
 * @returns Tailwind CSS color class
 */
export function getEscalationLevelColor(level: EscalationLevel): string {
  const colors: Record<EscalationLevel, string> = {
    [EscalationLevel.LEVEL_1]: 'blue-500',
    [EscalationLevel.LEVEL_2]: 'yellow-500',
    [EscalationLevel.LEVEL_3]: 'orange-600',
    [EscalationLevel.EXECUTIVE]: 'red-600',
    [EscalationLevel.BOARD]: 'red-700',
  };
  return colors[level] || 'gray-400';
}

/**
 * Get escalation level icon for visual representation
 * @param level - Escalation level enum value
 * @returns Lucide icon name
 */
export function getEscalationLevelIcon(level: EscalationLevel): string {
  const icons: Record<EscalationLevel, string> = {
    [EscalationLevel.LEVEL_1]: 'User',
    [EscalationLevel.LEVEL_2]: 'Users',
    [EscalationLevel.LEVEL_3]: 'UserCog',
    [EscalationLevel.EXECUTIVE]: 'Crown',
    [EscalationLevel.BOARD]: 'Building2',
  };
  return icons[level] || 'HelpCircle';
}

/**
 * Get team role label with proper formatting
 * @param role - Team role enum value
 * @returns Human-readable label
 */
export function getTeamRoleLabel(role: TeamRole): string {
  const labels: Record<TeamRole, string> = {
    [TeamRole.INCIDENT_COMMANDER]: 'Incident Commander',
    [TeamRole.OPERATIONS_CHIEF]: 'Operations Chief',
    [TeamRole.PLANNING_CHIEF]: 'Planning Chief',
    [TeamRole.LOGISTICS_CHIEF]: 'Logistics Chief',
    [TeamRole.FINANCE_CHIEF]: 'Finance Chief',
    [TeamRole.TECHNICAL_LEAD]: 'Technical Lead',
    [TeamRole.COMMUNICATIONS_LEAD]: 'Communications Lead',
    [TeamRole.SECURITY_LEAD]: 'Security Lead',
    [TeamRole.BUSINESS_CONTINUITY]: 'Business Continuity',
    [TeamRole.LEGAL]: 'Legal',
    [TeamRole.HR]: 'Human Resources',
    [TeamRole.EXECUTIVE]: 'Executive',
    [TeamRole.SUPPORT]: 'Support',
  };
  return labels[role] || 'Unknown';
}

/**
 * Get team role color for visual representation
 * @param role - Team role enum value
 * @returns Tailwind CSS color class
 */
export function getTeamRoleColor(role: TeamRole): string {
  const colors: Record<TeamRole, string> = {
    [TeamRole.INCIDENT_COMMANDER]: 'red-600',
    [TeamRole.OPERATIONS_CHIEF]: 'blue-600',
    [TeamRole.PLANNING_CHIEF]: 'purple-600',
    [TeamRole.LOGISTICS_CHIEF]: 'orange-600',
    [TeamRole.FINANCE_CHIEF]: 'green-600',
    [TeamRole.TECHNICAL_LEAD]: 'cyan-600',
    [TeamRole.COMMUNICATIONS_LEAD]: 'pink-600',
    [TeamRole.SECURITY_LEAD]: 'red-700',
    [TeamRole.BUSINESS_CONTINUITY]: 'indigo-600',
    [TeamRole.LEGAL]: 'gray-700',
    [TeamRole.HR]: 'rose-600',
    [TeamRole.EXECUTIVE]: 'amber-600',
    [TeamRole.SUPPORT]: 'teal-600',
  };
  return colors[role] || 'gray-400';
}

/**
 * Get team role icon for visual representation
 * @param role - Team role enum value
 * @returns Lucide icon name
 */
export function getTeamRoleIcon(role: TeamRole): string {
  const icons: Record<TeamRole, string> = {
    [TeamRole.INCIDENT_COMMANDER]: 'Crown',
    [TeamRole.OPERATIONS_CHIEF]: 'Settings',
    [TeamRole.PLANNING_CHIEF]: 'ClipboardList',
    [TeamRole.LOGISTICS_CHIEF]: 'Truck',
    [TeamRole.FINANCE_CHIEF]: 'DollarSign',
    [TeamRole.TECHNICAL_LEAD]: 'Code',
    [TeamRole.COMMUNICATIONS_LEAD]: 'MessageSquare',
    [TeamRole.SECURITY_LEAD]: 'Shield',
    [TeamRole.BUSINESS_CONTINUITY]: 'Activity',
    [TeamRole.LEGAL]: 'Scale',
    [TeamRole.HR]: 'Users',
    [TeamRole.EXECUTIVE]: 'Briefcase',
    [TeamRole.SUPPORT]: 'LifeBuoy',
  };
  return icons[role] || 'HelpCircle';
}

/**
 * Get action type label with proper formatting
 * @param type - Action type enum value
 * @returns Human-readable label
 */
export function getActionTypeLabel(type: ActionType): string {
  const labels: Record<ActionType, string> = {
    [ActionType.IMMEDIATE]: 'Immediate',
    [ActionType.SHORT_TERM]: 'Short-term',
    [ActionType.RECOVERY]: 'Recovery',
    [ActionType.POST_INCIDENT]: 'Post-Incident',
    [ActionType.PREVENTIVE]: 'Preventive',
    [ActionType.CORRECTIVE]: 'Corrective',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get action type color for visual representation
 * @param type - Action type enum value
 * @returns Tailwind CSS color class
 */
export function getActionTypeColor(type: ActionType): string {
  const colors: Record<ActionType, string> = {
    [ActionType.IMMEDIATE]: 'red-600',
    [ActionType.SHORT_TERM]: 'orange-500',
    [ActionType.RECOVERY]: 'blue-600',
    [ActionType.POST_INCIDENT]: 'purple-600',
    [ActionType.PREVENTIVE]: 'green-600',
    [ActionType.CORRECTIVE]: 'yellow-600',
  };
  return colors[type] || 'gray-400';
}

/**
 * Get action type icon for visual representation
 * @param type - Action type enum value
 * @returns Lucide icon name
 */
export function getActionTypeIcon(type: ActionType): string {
  const icons: Record<ActionType, string> = {
    [ActionType.IMMEDIATE]: 'Zap',
    [ActionType.SHORT_TERM]: 'Clock',
    [ActionType.RECOVERY]: 'RefreshCw',
    [ActionType.POST_INCIDENT]: 'FileText',
    [ActionType.PREVENTIVE]: 'ShieldCheck',
    [ActionType.CORRECTIVE]: 'Wrench',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get communication type label with proper formatting
 * @param type - Communication type enum value
 * @returns Human-readable label
 */
export function getCommunicationTypeLabel(type: CommunicationType): string {
  const labels: Record<CommunicationType, string> = {
    [CommunicationType.INTERNAL]: 'Internal',
    [CommunicationType.EXTERNAL]: 'External',
    [CommunicationType.STAKEHOLDER]: 'Stakeholder',
    [CommunicationType.MEDIA]: 'Media',
    [CommunicationType.REGULATORY]: 'Regulatory',
    [CommunicationType.CUSTOMER]: 'Customer',
    [CommunicationType.PARTNER]: 'Partner',
    [CommunicationType.EMAIL]: 'Email',
    [CommunicationType.PHONE]: 'Phone',
    [CommunicationType.SMS]: 'SMS',
    [CommunicationType.MEETING]: 'Meeting',
    [CommunicationType.CHAT]: 'Chat',
    [CommunicationType.NOTIFICATION]: 'Notification',
    [CommunicationType.REPORT]: 'Report',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get communication type color for visual representation
 * @param type - Communication type enum value
 * @returns Tailwind CSS color class
 */
export function getCommunicationTypeColor(type: CommunicationType): string {
  const colors: Record<CommunicationType, string> = {
    [CommunicationType.INTERNAL]: 'blue-600',
    [CommunicationType.EXTERNAL]: 'purple-600',
    [CommunicationType.STAKEHOLDER]: 'indigo-600',
    [CommunicationType.MEDIA]: 'pink-600',
    [CommunicationType.REGULATORY]: 'red-600',
    [CommunicationType.CUSTOMER]: 'green-600',
    [CommunicationType.PARTNER]: 'teal-600',
    [CommunicationType.EMAIL]: 'gray-600',
    [CommunicationType.PHONE]: 'orange-600',
    [CommunicationType.SMS]: 'yellow-600',
    [CommunicationType.MEETING]: 'cyan-600',
    [CommunicationType.CHAT]: 'violet-600',
    [CommunicationType.NOTIFICATION]: 'blue-500',
    [CommunicationType.REPORT]: 'slate-600',
  };
  return colors[type] || 'gray-400';
}

/**
 * Get communication type icon for visual representation
 * @param type - Communication type enum value
 * @returns Lucide icon name
 */
export function getCommunicationTypeIcon(type: CommunicationType): string {
  const icons: Record<CommunicationType, string> = {
    [CommunicationType.INTERNAL]: 'Users',
    [CommunicationType.EXTERNAL]: 'ExternalLink',
    [CommunicationType.STAKEHOLDER]: 'Briefcase',
    [CommunicationType.MEDIA]: 'Megaphone',
    [CommunicationType.REGULATORY]: 'FileText',
    [CommunicationType.CUSTOMER]: 'UserCheck',
    [CommunicationType.PARTNER]: 'Handshake',
    [CommunicationType.EMAIL]: 'Mail',
    [CommunicationType.PHONE]: 'Phone',
    [CommunicationType.SMS]: 'MessageSquare',
    [CommunicationType.MEETING]: 'Calendar',
    [CommunicationType.CHAT]: 'MessageCircle',
    [CommunicationType.NOTIFICATION]: 'Bell',
    [CommunicationType.REPORT]: 'FileText',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get action status label with proper formatting
 * @param status - Action status enum value
 * @returns Human-readable label
 */
export function getActionStatusLabel(status: ActionStatus): string {
  const labels: Record<ActionStatus, string> = {
    [ActionStatus.PENDING]: 'Pending',
    [ActionStatus.IN_PROGRESS]: 'In Progress',
    [ActionStatus.COMPLETED]: 'Completed',
    [ActionStatus.CANCELLED]: 'Cancelled',
    [ActionStatus.BLOCKED]: 'Blocked',
  };
  return labels[status] || 'Unknown';
}

/**
 * Get action status color for visual representation
 * @param status - Action status enum value
 * @returns Tailwind CSS color class
 */
export function getActionStatusColor(status: ActionStatus): string {
  const colors: Record<ActionStatus, string> = {
    [ActionStatus.PENDING]: 'gray-500',
    [ActionStatus.IN_PROGRESS]: 'blue-600',
    [ActionStatus.COMPLETED]: 'green-600',
    [ActionStatus.CANCELLED]: 'gray-400',
    [ActionStatus.BLOCKED]: 'red-500',
  };
  return colors[status] || 'gray-400';
}

/**
 * Get action status icon for visual representation
 * @param status - Action status enum value
 * @returns Lucide icon name
 */
export function getActionStatusIcon(status: ActionStatus): string {
  const icons: Record<ActionStatus, string> = {
    [ActionStatus.PENDING]: 'Clock',
    [ActionStatus.IN_PROGRESS]: 'PlayCircle',
    [ActionStatus.COMPLETED]: 'CheckCircle',
    [ActionStatus.CANCELLED]: 'XCircle',
    [ActionStatus.BLOCKED]: 'AlertCircle',
  };
  return icons[status] || 'HelpCircle';
}

/**
 * Get plan status label with proper formatting
 * @param status - Plan status enum value
 * @returns Human-readable label
 */
export function getPlanStatusLabel(status: PlanStatus): string {
  const labels: Record<PlanStatus, string> = {
    [PlanStatus.DRAFT]: 'Draft',
    [PlanStatus.ACTIVE]: 'Active',
    [PlanStatus.ARCHIVED]: 'Archived',
    [PlanStatus.UNDER_REVIEW]: 'Under Review',
  };
  return labels[status] || 'Unknown';
}

/**
 * Get plan status color for visual representation
 * @param status - Plan status enum value
 * @returns Tailwind CSS color class
 */
export function getPlanStatusColor(status: PlanStatus): string {
  const colors: Record<PlanStatus, string> = {
    [PlanStatus.DRAFT]: 'gray-500',
    [PlanStatus.ACTIVE]: 'green-600',
    [PlanStatus.ARCHIVED]: 'gray-400',
    [PlanStatus.UNDER_REVIEW]: 'yellow-500',
  };
  return colors[status] || 'gray-400';
}

/**
 * Get plan status icon for visual representation
 * @param status - Plan status enum value
 * @returns Lucide icon name
 */
export function getPlanStatusIcon(status: PlanStatus): string {
  const icons: Record<PlanStatus, string> = {
    [PlanStatus.DRAFT]: 'FileEdit',
    [PlanStatus.ACTIVE]: 'CheckCircle',
    [PlanStatus.ARCHIVED]: 'Archive',
    [PlanStatus.UNDER_REVIEW]: 'Eye',
  };
  return icons[status] || 'HelpCircle';
}

/**
 * Get recovery phase label with proper formatting
 * @param phase - Recovery phase enum value
 * @returns Human-readable label
 */
export function getRecoveryPhaseLabel(phase: RecoveryPhase): string {
  const labels: Record<RecoveryPhase, string> = {
    [RecoveryPhase.ASSESSMENT]: 'Assessment',
    [RecoveryPhase.STABILIZATION]: 'Stabilization',
    [RecoveryPhase.RECOVERY]: 'Recovery',
    [RecoveryPhase.RESTORATION]: 'Restoration',
    [RecoveryPhase.NORMALIZATION]: 'Normalization',
  };
  return labels[phase] || 'Unknown';
}

/**
 * Get recovery phase color for visual representation
 * @param phase - Recovery phase enum value
 * @returns Tailwind CSS color class
 */
export function getRecoveryPhaseColor(phase: RecoveryPhase): string {
  const colors: Record<RecoveryPhase, string> = {
    [RecoveryPhase.ASSESSMENT]: 'yellow-500',
    [RecoveryPhase.STABILIZATION]: 'orange-500',
    [RecoveryPhase.RECOVERY]: 'blue-600',
    [RecoveryPhase.RESTORATION]: 'purple-600',
    [RecoveryPhase.NORMALIZATION]: 'green-600',
  };
  return colors[phase] || 'gray-400';
}

/**
 * Get recovery phase icon for visual representation
 * @param phase - Recovery phase enum value
 * @returns Lucide icon name
 */
export function getRecoveryPhaseIcon(phase: RecoveryPhase): string {
  const icons: Record<RecoveryPhase, string> = {
    [RecoveryPhase.ASSESSMENT]: 'Search',
    [RecoveryPhase.STABILIZATION]: 'Anchor',
    [RecoveryPhase.RECOVERY]: 'RefreshCw',
    [RecoveryPhase.RESTORATION]: 'ArrowUpCircle',
    [RecoveryPhase.NORMALIZATION]: 'CheckCircle',
  };
  return icons[phase] || 'HelpCircle';
}
