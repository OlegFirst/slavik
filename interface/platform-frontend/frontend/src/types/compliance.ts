/**
 * Compliance Module - Types & Enums
 * ISO 22301:2019 Clause 10 - Improvement
 * AI Platform ISO Project
 *
 * Created: 2025-10-23
 * Agent: 15 (Compliance Module Round 1)
 */

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Compliance Standard Enumeration
 * International and regulatory compliance standards
 */
export enum ComplianceStandard {
  ISO_22301 = 'iso_22301',
  ISO_27001 = 'iso_27001',
  ISO_9001 = 'iso_9001',
  BCI_GPG = 'bci_gpg',
  NIST = 'nist_framework',
  GDPR = 'gdpr',
  SOX = 'sarbanes_oxley',
  HIPAA = 'hipaa',
  PCI_DSS = 'pci_dss',
  CMS = 'cms_emergency_prep',
  JOINT_COMMISSION = 'joint_commission',
  COBIT = 'cobit',
  CUSTOM = 'custom',
}

/**
 * Compliance Status Enumeration
 * Overall compliance level for requirements, assessments, and programs
 */
export enum ComplianceStatus {
  COMPLIANT = 'compliant',
  PARTIAL = 'partial_compliance',
  NON_COMPLIANT = 'non_compliant',
  NOT_ASSESSED = 'not_assessed',
  PENDING_REVIEW = 'pending_review',
}

/**
 * Requirement Type Enumeration
 * Classification of requirement criticality
 */
export enum RequirementType {
  MANDATORY = 'mandatory',
  RECOMMENDED = 'recommended',
  BEST_PRACTICE = 'best_practice',
}

/**
 * Requirement Category Enumeration
 * ISO 22301:2019 requirement categories
 */
export enum RequirementCategory {
  GOVERNANCE = 'governance',
  RISK_MANAGEMENT = 'risk_management',
  BUSINESS_CONTINUITY = 'business_continuity',
  INCIDENT_MANAGEMENT = 'incident_management',
  DOCUMENTATION = 'documentation',
  TRAINING = 'training',
  MONITORING = 'monitoring',
  AUDIT = 'audit',
  IMPROVEMENT = 'improvement',
  TESTING = 'testing',
}

/**
 * Assessment Method Enumeration
 * Methods used to assess compliance
 */
export enum AssessmentMethod {
  SELF_ASSESSMENT = 'self_assessment',
  INTERNAL_AUDIT = 'internal_audit',
  EXTERNAL_AUDIT = 'external_audit',
  CERTIFICATION = 'certification',
  PRE_AUDIT = 'pre_audit',
  POST_INCIDENT = 'post_incident',
  POST_EXERCISE = 'post_exercise',
}

/**
 * Assessment Type Enumeration
 * Type of compliance assessment
 */
export enum AssessmentType {
  REGULAR = 'regular',
  SELF = 'self_assessment',
  PRE_AUDIT = 'pre_audit',
  POST_INCIDENT = 'post_incident',
  POST_EXERCISE = 'post_exercise',
}

/**
 * Gap Severity Enumeration
 * Severity level of identified compliance gaps
 */
export enum GapSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Gap Priority Enumeration
 * Priority level for gap remediation
 */
export enum GapPriority {
  P1_CRITICAL = 'p1_critical',
  P2_HIGH = 'p2_high',
  P3_MEDIUM = 'p3_medium',
  P4_LOW = 'p4_low',
}

/**
 * Action Status Enumeration
 * Status of corrective actions and remediation actions
 */
export enum ActionStatus {
  OPEN = 'open',
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  VERIFIED = 'verified',
  CANCELLED = 'cancelled',
}

/**
 * Evidence Type Enumeration
 * Types of compliance evidence documents
 */
export enum EvidenceType {
  POLICY = 'policy',
  PROCEDURE = 'procedure',
  PLAN = 'plan',
  RECORD = 'record',
  REPORT = 'report',
  CERTIFICATE = 'certificate',
  TRAINING_RECORD = 'training_record',
  EXERCISE_REPORT = 'exercise_report',
  MEETING_MINUTES = 'meeting_minutes',
  AUDIT_REPORT = 'audit_report',
  ASSESSMENT = 'assessment',
  DOCUMENT = 'document',
  SCREENSHOT = 'screenshot',
  LOG = 'log',
  OTHER = 'other',
}

/**
 * Audit Type Enumeration
 * Types of compliance audits
 */
export enum AuditType {
  INTERNAL = 'internal',
  EXTERNAL = 'external',
  CERTIFICATION = 'certification',
  SURVEILLANCE = 'surveillance',
  RECERTIFICATION = 'recertification',
}

/**
 * Audit Result Enumeration
 * Overall audit outcome
 */
export enum AuditResult {
  PASS = 'pass',
  CONDITIONAL_PASS = 'conditional_pass',
  FAIL = 'fail',
  PENDING = 'pending',
}

/**
 * Nonconformity Type Enumeration
 * Classification of audit findings and nonconformities
 */
export enum NonconformityType {
  MAJOR = 'major',
  MINOR = 'minor',
  OBSERVATION = 'observation',
}

/**
 * Nonconformity Source Enumeration
 * Source of nonconformity identification
 */
export enum NonconformitySource {
  INTERNAL_AUDIT = 'internal_audit',
  EXTERNAL_AUDIT = 'external_audit',
  MANAGEMENT_REVIEW = 'management_review',
  INCIDENT = 'incident',
  EXERCISE = 'exercise',
  MONITORING = 'monitoring',
  SELF_ASSESSMENT = 'self_assessment',
}

/**
 * RCA Method Enumeration
 * Root Cause Analysis methodologies
 */
export enum RCAMethod {
  FIVE_WHYS = '5_whys',
  FISHBONE = 'fishbone',
  FAULT_TREE = 'fault_tree',
  PARETO = 'pareto',
  BARRIER_ANALYSIS = 'barrier_analysis',
}

/**
 * Evidence State Enumeration
 * Workflow states for evidence verification
 */
export enum EvidenceState {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
}

/**
 * Assessment State Enumeration
 * Workflow states for assessments
 */
export enum AssessmentState {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  UNDER_REVIEW = 'under_review',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/**
 * Gap State Enumeration
 * Workflow states for compliance gaps
 */
export enum GapState {
  IDENTIFIED = 'identified',
  IN_REMEDIATION = 'in_remediation',
  PENDING_VERIFICATION = 'pending_verification',
  RESOLVED = 'resolved',
  RISK_ACCEPTED = 'risk_accepted',
  REOPENED = 'reopened',
}

/**
 * Audit State Enumeration
 * Workflow states for audits
 */
export enum AuditState {
  PLANNED = 'planned',
  PREPARING = 'preparing',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/**
 * Nonconformity State Enumeration
 * Workflow states for nonconformities
 */
export enum NonconformityState {
  IDENTIFIED = 'identified',
  RCA_IN_PROGRESS = 'rca_in_progress',
  ACTION_PLANNING = 'action_planning',
  ACTIONS_IN_PROGRESS = 'actions_in_progress',
  PENDING_VERIFICATION = 'pending_verification',
  VERIFIED = 'verified',
  CLOSED = 'closed',
}

// ============================================================================
// SUPPORTING TYPES
// ============================================================================

/**
 * Remediation Action Interface
 * Individual action to address a compliance gap
 */
export interface RemediationAction {
  description: string;
  responsible: string;
  deadline?: string;
  status: ActionStatus;
}

/**
 * Root Cause Interface
 * Identified root cause from RCA
 */
export interface RootCause {
  id: string;
  description: string;
  evidence?: string;
}

/**
 * Corrective Action Interface
 * Action to address nonconformity root causes
 */
export interface CorrectiveAction {
  description: string;
  owner: string;
  deadline: string;
  addresses_cause_id: string;
  status: ActionStatus;
}

/**
 * Root Cause Analysis Interface
 * Complete RCA results
 */
export interface RootCauseAnalysis {
  method: RCAMethod;
  root_causes: RootCause[];
  analysis_summary: string;
  completed_at: string;
  completed_by: string;
}

/**
 * Audit Finding Interface
 * Individual finding from an audit
 */
export interface AuditFinding {
  type: NonconformityType;
  clause: string;
  description: string;
  evidence: string;
}

/**
 * Assessment Requirement Result Interface
 * Results for a single requirement in an assessment
 */
export interface AssessmentRequirementResult {
  requirement_id: string;
  clause: string;
  compliance_score: number;
  status: ComplianceStatus;
  evidence_count: number;
  gaps_identified: number;
  notes?: string;
}

// ============================================================================
// MAIN INTERFACES
// ============================================================================

/**
 * Compliance Program Interface
 * Overall compliance program for an organization and standard
 */
export interface ComplianceProgram {
  id: string;
  organization_id: string;

  // Program Details
  program_name: string;
  standard: ComplianceStandard;
  description?: string;

  // Scope
  scope_description?: string;
  applicable_departments: string[];
  applicable_processes: string[];

  // Status
  overall_score: number;
  compliance_status: ComplianceStatus;

  // Certification
  certification_target_date?: string;
  certification_valid_until?: string;
  certification_body?: string;

  // Reviews
  last_review_date?: string;
  next_review_date?: string;

  // Ownership
  program_owner: string;
  compliance_officer?: string;

  // Metadata
  created_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * Compliance Requirement Interface
 * Specific compliance requirement from a standard
 */
export interface ComplianceRequirement {
  id: string;
  organization_id: string;

  // Standard Reference
  standard: ComplianceStandard;
  clause: string;
  title: string;
  description: string;

  // Classification
  category: RequirementCategory;
  requirement_type: RequirementType;
  is_mandatory: boolean;

  // Weighting
  weight: number;

  // Evidence Requirements
  evidence_types: string[];
  min_evidence_count: number;

  // Status
  is_active: boolean;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Compliance Assessment Interface
 * Assessment of compliance against requirements
 */
export interface ComplianceAssessment {
  id: string;
  organization_id: string;

  // Assessment Details
  standard: ComplianceStandard;
  assessment_type: AssessmentType;
  assessment_method: AssessmentMethod;

  // Scope
  scope?: string;
  scope_clauses: string[];

  // Scheduling
  planned_date?: string;
  start_date?: string;
  review_date?: string;
  completion_date?: string;

  // Personnel
  assessor_id?: string;
  reviewer_id?: string;
  approved_by?: string;

  // Status
  status: AssessmentState;

  // Results
  overall_score?: number;
  compliance_status?: ComplianceStatus;
  requirements_assessed?: Record<string, AssessmentRequirementResult>;
  gaps_identified?: Record<string, unknown>;
  recommendations?: string[];

  // Comments
  assessment_comment?: string;
  approval_comment?: string;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

/**
 * Compliance Gap Interface
 * Identified gap in compliance requirements
 */
export interface ComplianceGap {
  id: string;
  organization_id: string;

  // Association
  requirement_id: string;
  assessment_id?: string;

  // Gap Details
  gap_description: string;
  severity: GapSeverity;
  priority: GapPriority;

  // Coverage
  current_coverage?: number;
  target_coverage: number;
  impact_score?: number;

  // Remediation
  remediation_actions?: RemediationAction[];
  estimated_effort?: string;
  assigned_to?: string;
  due_date?: string;

  // Status
  status: GapState;

  // Resolution
  resolution_description?: string;
  resolved_by?: string;
  resolved_at?: string;
  evidence_id?: string;

  // Verification
  verification_comment?: string;
  verified_by?: string;
  verified_at?: string;

  // Risk Acceptance
  risk_acceptance_justification?: string;
  accepted_by?: string;
  risk_owner?: string;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

/**
 * Corrective Action Record Interface
 * Action to address non-conformities and gaps
 */
export interface CorrectiveActionRecord {
  id: string;
  organization_id: string;

  // Association
  nonconformity_id?: string;
  gap_id?: string;
  audit_id?: string;

  // Action Details
  action_title: string;
  description: string;
  action_type: 'corrective' | 'preventive' | 'improvement';

  // Root Cause
  root_cause_id?: string;
  root_cause_description?: string;

  // Assignment
  owner: string;
  assigned_to: string;
  backup_responsible?: string;

  // Timeline
  target_date?: string;
  completion_date?: string;

  // Status
  status: ActionStatus;
  progress_percentage: number;

  // Effectiveness
  effectiveness_review_required: boolean;
  effectiveness_review_date?: string;
  effectiveness_confirmed?: boolean;
  effectiveness_notes?: string;

  // Verification
  verified_by?: string;
  verified_at?: string;
  verification_notes?: string;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Compliance Evidence Interface
 * Documentary evidence of compliance
 */
export interface ComplianceEvidence {
  id: string;
  organization_id: string;

  // Association
  requirement_id: string;
  assessment_id?: string;
  gap_id?: string;

  // Evidence Details
  title: string;
  description?: string;
  evidence_type: EvidenceType;

  // Document Reference
  document_id?: string;
  document_reference?: string;
  file_url?: string;

  // Validity
  validity_period_start?: string;
  validity_period_end?: string;

  // Status
  status: EvidenceState;
  verification_status: 'not_verified' | 'verified' | 'rejected';

  // Review
  reviewer_id?: string;
  review_started_at?: string;
  verified_by?: string;
  verified_at?: string;
  rejection_reason?: string;

  // Metadata
  metadata?: Record<string, unknown>;
  created_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

/**
 * Compliance Audit Interface
 * Formal audit of compliance program
 */
export interface ComplianceAudit {
  id: string;
  organization_id: string;

  // Audit Details
  audit_number: string;
  audit_type: AuditType;
  standard: ComplianceStandard;

  // Scope
  scope?: string;
  scope_clauses: string[];

  // Scheduling
  planned_date?: string;
  actual_date?: string;
  completion_date?: string;

  // Auditor Information
  auditor_name?: string;
  auditor_organization?: string;
  auditor_independent: boolean;

  // Preparation
  preparation_lead?: string;
  audit_package_generated: boolean;
  audit_package_url?: string;

  // Status
  status: AuditState;

  // Findings
  findings?: AuditFinding[];
  nc_ids?: string[];

  // Results
  overall_result?: AuditResult;
  audit_report_url?: string;

  // Certification
  certification_valid_until?: string;
  next_surveillance_date?: string;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
  planned_by?: string;
  version: number;
}

/**
 * Compliance Mapping Interface
 * Cross-mapping between different standards and controls
 */
export interface ComplianceMapping {
  id: string;
  organization_id: string;

  // Source Requirement
  source_standard: ComplianceStandard;
  source_clause: string;
  source_requirement_id: string;

  // Target Requirement
  target_standard: ComplianceStandard;
  target_clause: string;
  target_requirement_id: string;

  // Mapping Details
  mapping_type: 'full' | 'partial' | 'related';
  mapping_rationale?: string;
  coverage_percentage?: number;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Compliance Nonconformity Interface
 * Non-conformance identified during audits or assessments
 */
export interface ComplianceNonconformity {
  id: string;
  organization_id: string;

  // NC Details
  nc_number: string;
  nc_type: NonconformityType;
  source: NonconformitySource;
  title: string;
  description: string;

  // Association
  requirement_id?: string;
  audit_id?: string;

  // Identification
  identified_by: string;
  identified_date: string;

  // Status
  status: NonconformityState;

  // Root Cause Analysis
  rca_lead?: string;
  rca_team?: string[];
  rca_method?: RCAMethod;
  rca_started_at?: string;
  rca_completed_at?: string;
  root_causes?: RootCause[];

  // Corrective Actions
  corrective_actions?: CorrectiveAction[];
  actions_completed_at?: string;

  // Verification
  evidence_ids?: string[];
  verifier_id?: string;
  verification_requested_at?: string;
  verification_result?: string;
  effectiveness_confirmed?: boolean;
  verified_by?: string;
  verified_at?: string;

  // Closure
  closed_at?: string;

  // Metadata
  created_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

// ============================================================================
// DASHBOARD & ANALYTICS TYPES
// ============================================================================

/**
 * Compliance Dashboard Interface
 * Summary dashboard data for compliance overview
 */
export interface ComplianceDashboard {
  organization_id: string;
  standard: ComplianceStandard;

  // Overall Status
  overall_score: number;
  compliance_status: ComplianceStatus;

  // Requirements
  requirements_total: number;
  requirements_compliant: number;
  requirements_partial: number;
  requirements_non_compliant: number;

  // Evidence
  evidence_count: number;
  evidence_verified_count: number;

  // Gaps
  gaps_open: number;
  gaps_critical: number;

  // Nonconformities
  nc_open: number;
  nc_major: number;

  // Dates
  last_assessment_date?: string;
  next_audit_date?: string;
  certification_valid_until?: string;

  // Metadata
  last_updated: string;
}

/**
 * Compliance Score Interface
 * Detailed compliance scoring breakdown
 */
export interface ComplianceScore {
  overall_score: number;
  clause_scores: Record<string, number>;
  coverage: number;
  gaps: string[];
  recommendations: string[];
}

/**
 * Compliance Trend Interface
 * Point-in-time compliance metric
 */
export interface ComplianceTrend {
  date: string;
  score: number;
  status: ComplianceStatus;
}

/**
 * Compliance Trends Response Interface
 * Historical compliance trends
 */
export interface ComplianceTrendsResponse {
  standard: ComplianceStandard;
  period_days: number;
  trend: 'improving' | 'stable' | 'declining';
  data_points: ComplianceTrend[];
}

// ============================================================================
// CREATE/UPDATE TYPES
// ============================================================================

/**
 * Compliance Program Creation Payload
 */
export type ComplianceProgramCreate = Omit<ComplianceProgram, 'id' | 'created_at' | 'updated_at'>;

/**
 * Compliance Program Update Payload
 */
export type ComplianceProgramUpdate = Partial<ComplianceProgramCreate>;

/**
 * Compliance Requirement Creation Payload
 */
export type ComplianceRequirementCreate = Omit<ComplianceRequirement, 'id' | 'created_at' | 'updated_at'>;

/**
 * Compliance Requirement Update Payload
 */
export type ComplianceRequirementUpdate = Partial<ComplianceRequirementCreate>;

/**
 * Compliance Assessment Creation Payload
 */
export type ComplianceAssessmentCreate = Omit<ComplianceAssessment, 'id' | 'created_at' | 'updated_at' | 'version'>;

/**
 * Compliance Assessment Update Payload
 */
export type ComplianceAssessmentUpdate = Partial<ComplianceAssessmentCreate>;

/**
 * Compliance Gap Creation Payload
 */
export type ComplianceGapCreate = Omit<ComplianceGap, 'id' | 'created_at' | 'updated_at' | 'version'>;

/**
 * Compliance Gap Update Payload
 */
export type ComplianceGapUpdate = Partial<ComplianceGapCreate>;

/**
 * Corrective Action Creation Payload
 */
export type CorrectiveActionRecordCreate = Omit<CorrectiveActionRecord, 'id' | 'created_at' | 'updated_at'>;

/**
 * Corrective Action Update Payload
 */
export type CorrectiveActionRecordUpdate = Partial<CorrectiveActionRecordCreate>;

/**
 * Compliance Evidence Creation Payload
 */
export type ComplianceEvidenceCreate = Omit<ComplianceEvidence, 'id' | 'created_at' | 'updated_at' | 'version'>;

/**
 * Compliance Evidence Update Payload
 */
export type ComplianceEvidenceUpdate = Partial<ComplianceEvidenceCreate>;

/**
 * Compliance Audit Creation Payload
 */
export type ComplianceAuditCreate = Omit<ComplianceAudit, 'id' | 'created_at' | 'updated_at' | 'version' | 'audit_number'>;

/**
 * Compliance Audit Update Payload
 */
export type ComplianceAuditUpdate = Partial<ComplianceAuditCreate>;

/**
 * Compliance Nonconformity Creation Payload
 */
export type ComplianceNonconformityCreate = Omit<ComplianceNonconformity, 'id' | 'created_at' | 'updated_at' | 'version' | 'nc_number'>;

/**
 * Compliance Nonconformity Update Payload
 */
export type ComplianceNonconformityUpdate = Partial<ComplianceNonconformityCreate>;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get compliance standard label
 */
export function getComplianceStandardLabel(standard: ComplianceStandard): string {
  const labels: Record<ComplianceStandard, string> = {
    [ComplianceStandard.ISO_22301]: 'ISO 22301:2019',
    [ComplianceStandard.ISO_27001]: 'ISO 27001',
    [ComplianceStandard.ISO_9001]: 'ISO 9001',
    [ComplianceStandard.BCI_GPG]: 'BCI Good Practice Guidelines',
    [ComplianceStandard.NIST]: 'NIST Framework',
    [ComplianceStandard.GDPR]: 'GDPR',
    [ComplianceStandard.SOX]: 'Sarbanes-Oxley',
    [ComplianceStandard.HIPAA]: 'HIPAA',
    [ComplianceStandard.PCI_DSS]: 'PCI DSS',
    [ComplianceStandard.CMS]: 'CMS Emergency Preparedness',
    [ComplianceStandard.JOINT_COMMISSION]: 'Joint Commission',
    [ComplianceStandard.COBIT]: 'COBIT',
    [ComplianceStandard.CUSTOM]: 'Custom Standard',
  };
  return labels[standard] || 'Unknown';
}

/**
 * Get compliance standard color
 */
export function getComplianceStandardColor(standard: ComplianceStandard): string {
  const colors: Record<ComplianceStandard, string> = {
    [ComplianceStandard.ISO_22301]: 'blue-600',
    [ComplianceStandard.ISO_27001]: 'indigo-600',
    [ComplianceStandard.ISO_9001]: 'purple-600',
    [ComplianceStandard.BCI_GPG]: 'teal-600',
    [ComplianceStandard.NIST]: 'cyan-600',
    [ComplianceStandard.GDPR]: 'green-600',
    [ComplianceStandard.SOX]: 'orange-600',
    [ComplianceStandard.HIPAA]: 'pink-600',
    [ComplianceStandard.PCI_DSS]: 'red-600',
    [ComplianceStandard.CMS]: 'violet-600',
    [ComplianceStandard.JOINT_COMMISSION]: 'fuchsia-600',
    [ComplianceStandard.COBIT]: 'rose-600',
    [ComplianceStandard.CUSTOM]: 'gray-600',
  };
  return colors[standard] || 'gray-500';
}

/**
 * Get compliance standard icon
 */
export function getComplianceStandardIcon(standard: ComplianceStandard): string {
  const icons: Record<ComplianceStandard, string> = {
    [ComplianceStandard.ISO_22301]: 'Shield',
    [ComplianceStandard.ISO_27001]: 'ShieldCheck',
    [ComplianceStandard.ISO_9001]: 'Award',
    [ComplianceStandard.BCI_GPG]: 'BookOpen',
    [ComplianceStandard.NIST]: 'Building2',
    [ComplianceStandard.GDPR]: 'Lock',
    [ComplianceStandard.SOX]: 'Scale',
    [ComplianceStandard.HIPAA]: 'Heart',
    [ComplianceStandard.PCI_DSS]: 'CreditCard',
    [ComplianceStandard.CMS]: 'Hospital',
    [ComplianceStandard.JOINT_COMMISSION]: 'Stethoscope',
    [ComplianceStandard.COBIT]: 'Network',
    [ComplianceStandard.CUSTOM]: 'FileText',
  };
  return icons[standard] || 'HelpCircle';
}

/**
 * Get compliance status label
 */
export function getComplianceStatusLabel(status: ComplianceStatus): string {
  const labels: Record<ComplianceStatus, string> = {
    [ComplianceStatus.COMPLIANT]: 'Compliant',
    [ComplianceStatus.PARTIAL]: 'Partially Compliant',
    [ComplianceStatus.NON_COMPLIANT]: 'Non-Compliant',
    [ComplianceStatus.NOT_ASSESSED]: 'Not Assessed',
    [ComplianceStatus.PENDING_REVIEW]: 'Pending Review',
  };
  return labels[status] || 'Unknown';
}

/**
 * Get compliance status color
 */
export function getComplianceStatusColor(status: ComplianceStatus): string {
  const colors: Record<ComplianceStatus, string> = {
    [ComplianceStatus.COMPLIANT]: 'green-600',
    [ComplianceStatus.PARTIAL]: 'yellow-500',
    [ComplianceStatus.NON_COMPLIANT]: 'red-600',
    [ComplianceStatus.NOT_ASSESSED]: 'gray-500',
    [ComplianceStatus.PENDING_REVIEW]: 'blue-500',
  };
  return colors[status] || 'gray-500';
}

/**
 * Get compliance status icon
 */
export function getComplianceStatusIcon(status: ComplianceStatus): string {
  const icons: Record<ComplianceStatus, string> = {
    [ComplianceStatus.COMPLIANT]: 'CheckCircle',
    [ComplianceStatus.PARTIAL]: 'AlertCircle',
    [ComplianceStatus.NON_COMPLIANT]: 'XCircle',
    [ComplianceStatus.NOT_ASSESSED]: 'HelpCircle',
    [ComplianceStatus.PENDING_REVIEW]: 'Clock',
  };
  return icons[status] || 'HelpCircle';
}

/**
 * Get requirement type label
 */
export function getRequirementTypeLabel(type: RequirementType): string {
  const labels: Record<RequirementType, string> = {
    [RequirementType.MANDATORY]: 'Mandatory',
    [RequirementType.RECOMMENDED]: 'Recommended',
    [RequirementType.BEST_PRACTICE]: 'Best Practice',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get requirement type color
 */
export function getRequirementTypeColor(type: RequirementType): string {
  const colors: Record<RequirementType, string> = {
    [RequirementType.MANDATORY]: 'red-600',
    [RequirementType.RECOMMENDED]: 'yellow-500',
    [RequirementType.BEST_PRACTICE]: 'green-500',
  };
  return colors[type] || 'gray-500';
}

/**
 * Get requirement type icon
 */
export function getRequirementTypeIcon(type: RequirementType): string {
  const icons: Record<RequirementType, string> = {
    [RequirementType.MANDATORY]: 'AlertCircle',
    [RequirementType.RECOMMENDED]: 'Info',
    [RequirementType.BEST_PRACTICE]: 'Star',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get requirement category label
 */
export function getRequirementCategoryLabel(category: RequirementCategory): string {
  const labels: Record<RequirementCategory, string> = {
    [RequirementCategory.GOVERNANCE]: 'Governance',
    [RequirementCategory.RISK_MANAGEMENT]: 'Risk Management',
    [RequirementCategory.BUSINESS_CONTINUITY]: 'Business Continuity',
    [RequirementCategory.INCIDENT_MANAGEMENT]: 'Incident Management',
    [RequirementCategory.DOCUMENTATION]: 'Documentation',
    [RequirementCategory.TRAINING]: 'Training',
    [RequirementCategory.MONITORING]: 'Monitoring',
    [RequirementCategory.AUDIT]: 'Audit',
    [RequirementCategory.IMPROVEMENT]: 'Improvement',
    [RequirementCategory.TESTING]: 'Testing',
  };
  return labels[category] || 'Unknown';
}

/**
 * Get requirement category color
 */
export function getRequirementCategoryColor(category: RequirementCategory): string {
  const colors: Record<RequirementCategory, string> = {
    [RequirementCategory.GOVERNANCE]: 'purple-600',
    [RequirementCategory.RISK_MANAGEMENT]: 'orange-600',
    [RequirementCategory.BUSINESS_CONTINUITY]: 'blue-600',
    [RequirementCategory.INCIDENT_MANAGEMENT]: 'red-600',
    [RequirementCategory.DOCUMENTATION]: 'gray-600',
    [RequirementCategory.TRAINING]: 'green-600',
    [RequirementCategory.MONITORING]: 'cyan-600',
    [RequirementCategory.AUDIT]: 'indigo-600',
    [RequirementCategory.IMPROVEMENT]: 'teal-600',
    [RequirementCategory.TESTING]: 'pink-600',
  };
  return colors[category] || 'gray-500';
}

/**
 * Get requirement category icon
 */
export function getRequirementCategoryIcon(category: RequirementCategory): string {
  const icons: Record<RequirementCategory, string> = {
    [RequirementCategory.GOVERNANCE]: 'Building2',
    [RequirementCategory.RISK_MANAGEMENT]: 'AlertTriangle',
    [RequirementCategory.BUSINESS_CONTINUITY]: 'Activity',
    [RequirementCategory.INCIDENT_MANAGEMENT]: 'AlertCircle',
    [RequirementCategory.DOCUMENTATION]: 'FileText',
    [RequirementCategory.TRAINING]: 'GraduationCap',
    [RequirementCategory.MONITORING]: 'Eye',
    [RequirementCategory.AUDIT]: 'Search',
    [RequirementCategory.IMPROVEMENT]: 'TrendingUp',
    [RequirementCategory.TESTING]: 'FlaskConical',
  };
  return icons[category] || 'HelpCircle';
}

/**
 * Get assessment method label
 */
export function getAssessmentMethodLabel(method: AssessmentMethod): string {
  const labels: Record<AssessmentMethod, string> = {
    [AssessmentMethod.SELF_ASSESSMENT]: 'Self Assessment',
    [AssessmentMethod.INTERNAL_AUDIT]: 'Internal Audit',
    [AssessmentMethod.EXTERNAL_AUDIT]: 'External Audit',
    [AssessmentMethod.CERTIFICATION]: 'Certification',
    [AssessmentMethod.PRE_AUDIT]: 'Pre-Audit',
    [AssessmentMethod.POST_INCIDENT]: 'Post-Incident',
    [AssessmentMethod.POST_EXERCISE]: 'Post-Exercise',
  };
  return labels[method] || 'Unknown';
}

/**
 * Get assessment method color
 */
export function getAssessmentMethodColor(method: AssessmentMethod): string {
  const colors: Record<AssessmentMethod, string> = {
    [AssessmentMethod.SELF_ASSESSMENT]: 'blue-500',
    [AssessmentMethod.INTERNAL_AUDIT]: 'purple-500',
    [AssessmentMethod.EXTERNAL_AUDIT]: 'indigo-600',
    [AssessmentMethod.CERTIFICATION]: 'green-600',
    [AssessmentMethod.PRE_AUDIT]: 'yellow-500',
    [AssessmentMethod.POST_INCIDENT]: 'orange-500',
    [AssessmentMethod.POST_EXERCISE]: 'teal-500',
  };
  return colors[method] || 'gray-500';
}

/**
 * Get assessment method icon
 */
export function getAssessmentMethodIcon(method: AssessmentMethod): string {
  const icons: Record<AssessmentMethod, string> = {
    [AssessmentMethod.SELF_ASSESSMENT]: 'ClipboardCheck',
    [AssessmentMethod.INTERNAL_AUDIT]: 'Search',
    [AssessmentMethod.EXTERNAL_AUDIT]: 'UserSearch',
    [AssessmentMethod.CERTIFICATION]: 'Award',
    [AssessmentMethod.PRE_AUDIT]: 'FileSearch',
    [AssessmentMethod.POST_INCIDENT]: 'AlertCircle',
    [AssessmentMethod.POST_EXERCISE]: 'Target',
  };
  return icons[method] || 'HelpCircle';
}

/**
 * Get gap severity label
 */
export function getGapSeverityLabel(severity: GapSeverity): string {
  const labels: Record<GapSeverity, string> = {
    [GapSeverity.CRITICAL]: 'Critical',
    [GapSeverity.HIGH]: 'High',
    [GapSeverity.MEDIUM]: 'Medium',
    [GapSeverity.LOW]: 'Low',
  };
  return labels[severity] || 'Unknown';
}

/**
 * Get gap severity color
 */
export function getGapSeverityColor(severity: GapSeverity): string {
  const colors: Record<GapSeverity, string> = {
    [GapSeverity.CRITICAL]: 'red-600',
    [GapSeverity.HIGH]: 'orange-500',
    [GapSeverity.MEDIUM]: 'yellow-500',
    [GapSeverity.LOW]: 'blue-500',
  };
  return colors[severity] || 'gray-500';
}

/**
 * Get gap severity icon
 */
export function getGapSeverityIcon(severity: GapSeverity): string {
  const icons: Record<GapSeverity, string> = {
    [GapSeverity.CRITICAL]: 'AlertOctagon',
    [GapSeverity.HIGH]: 'AlertTriangle',
    [GapSeverity.MEDIUM]: 'AlertCircle',
    [GapSeverity.LOW]: 'Info',
  };
  return icons[severity] || 'HelpCircle';
}

/**
 * Get gap priority label
 */
export function getGapPriorityLabel(priority: GapPriority): string {
  const labels: Record<GapPriority, string> = {
    [GapPriority.P1_CRITICAL]: 'P1 - Critical',
    [GapPriority.P2_HIGH]: 'P2 - High',
    [GapPriority.P3_MEDIUM]: 'P3 - Medium',
    [GapPriority.P4_LOW]: 'P4 - Low',
  };
  return labels[priority] || 'Unknown';
}

/**
 * Get gap priority color
 */
export function getGapPriorityColor(priority: GapPriority): string {
  const colors: Record<GapPriority, string> = {
    [GapPriority.P1_CRITICAL]: 'red-600',
    [GapPriority.P2_HIGH]: 'orange-500',
    [GapPriority.P3_MEDIUM]: 'yellow-500',
    [GapPriority.P4_LOW]: 'green-500',
  };
  return colors[priority] || 'gray-500';
}

/**
 * Get gap priority icon
 */
export function getGapPriorityIcon(priority: GapPriority): string {
  const icons: Record<GapPriority, string> = {
    [GapPriority.P1_CRITICAL]: 'Flame',
    [GapPriority.P2_HIGH]: 'ArrowUp',
    [GapPriority.P3_MEDIUM]: 'Minus',
    [GapPriority.P4_LOW]: 'ArrowDown',
  };
  return icons[priority] || 'HelpCircle';
}

/**
 * Get action status label
 */
export function getActionStatusLabel(status: ActionStatus): string {
  const labels: Record<ActionStatus, string> = {
    [ActionStatus.OPEN]: 'Open',
    [ActionStatus.PENDING]: 'Pending',
    [ActionStatus.IN_PROGRESS]: 'In Progress',
    [ActionStatus.COMPLETED]: 'Completed',
    [ActionStatus.VERIFIED]: 'Verified',
    [ActionStatus.CANCELLED]: 'Cancelled',
  };
  return labels[status] || 'Unknown';
}

/**
 * Get action status color
 */
export function getActionStatusColor(status: ActionStatus): string {
  const colors: Record<ActionStatus, string> = {
    [ActionStatus.OPEN]: 'gray-500',
    [ActionStatus.PENDING]: 'yellow-500',
    [ActionStatus.IN_PROGRESS]: 'blue-600',
    [ActionStatus.COMPLETED]: 'green-600',
    [ActionStatus.VERIFIED]: 'green-700',
    [ActionStatus.CANCELLED]: 'gray-400',
  };
  return colors[status] || 'gray-500';
}

/**
 * Get action status icon
 */
export function getActionStatusIcon(status: ActionStatus): string {
  const icons: Record<ActionStatus, string> = {
    [ActionStatus.OPEN]: 'Circle',
    [ActionStatus.PENDING]: 'Clock',
    [ActionStatus.IN_PROGRESS]: 'PlayCircle',
    [ActionStatus.COMPLETED]: 'CheckCircle',
    [ActionStatus.VERIFIED]: 'CheckCircle2',
    [ActionStatus.CANCELLED]: 'XCircle',
  };
  return icons[status] || 'HelpCircle';
}

/**
 * Get evidence type label
 */
export function getEvidenceTypeLabel(type: EvidenceType): string {
  const labels: Record<EvidenceType, string> = {
    [EvidenceType.POLICY]: 'Policy',
    [EvidenceType.PROCEDURE]: 'Procedure',
    [EvidenceType.PLAN]: 'Plan',
    [EvidenceType.RECORD]: 'Record',
    [EvidenceType.REPORT]: 'Report',
    [EvidenceType.CERTIFICATE]: 'Certificate',
    [EvidenceType.TRAINING_RECORD]: 'Training Record',
    [EvidenceType.EXERCISE_REPORT]: 'Exercise Report',
    [EvidenceType.MEETING_MINUTES]: 'Meeting Minutes',
    [EvidenceType.AUDIT_REPORT]: 'Audit Report',
    [EvidenceType.ASSESSMENT]: 'Assessment',
    [EvidenceType.DOCUMENT]: 'Document',
    [EvidenceType.SCREENSHOT]: 'Screenshot',
    [EvidenceType.LOG]: 'Log',
    [EvidenceType.OTHER]: 'Other',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get evidence type color
 */
export function getEvidenceTypeColor(type: EvidenceType): string {
  const colors: Record<EvidenceType, string> = {
    [EvidenceType.POLICY]: 'blue-600',
    [EvidenceType.PROCEDURE]: 'indigo-600',
    [EvidenceType.PLAN]: 'purple-600',
    [EvidenceType.RECORD]: 'gray-600',
    [EvidenceType.REPORT]: 'cyan-600',
    [EvidenceType.CERTIFICATE]: 'green-600',
    [EvidenceType.TRAINING_RECORD]: 'teal-600',
    [EvidenceType.EXERCISE_REPORT]: 'orange-600',
    [EvidenceType.MEETING_MINUTES]: 'pink-600',
    [EvidenceType.AUDIT_REPORT]: 'red-600',
    [EvidenceType.ASSESSMENT]: 'violet-600',
    [EvidenceType.DOCUMENT]: 'gray-500',
    [EvidenceType.SCREENSHOT]: 'yellow-500',
    [EvidenceType.LOG]: 'slate-600',
    [EvidenceType.OTHER]: 'gray-400',
  };
  return colors[type] || 'gray-500';
}

/**
 * Get evidence type icon
 */
export function getEvidenceTypeIcon(type: EvidenceType): string {
  const icons: Record<EvidenceType, string> = {
    [EvidenceType.POLICY]: 'BookOpen',
    [EvidenceType.PROCEDURE]: 'ListChecks',
    [EvidenceType.PLAN]: 'Map',
    [EvidenceType.RECORD]: 'FileText',
    [EvidenceType.REPORT]: 'BarChart',
    [EvidenceType.CERTIFICATE]: 'Award',
    [EvidenceType.TRAINING_RECORD]: 'GraduationCap',
    [EvidenceType.EXERCISE_REPORT]: 'Target',
    [EvidenceType.MEETING_MINUTES]: 'Users',
    [EvidenceType.AUDIT_REPORT]: 'Search',
    [EvidenceType.ASSESSMENT]: 'ClipboardCheck',
    [EvidenceType.DOCUMENT]: 'File',
    [EvidenceType.SCREENSHOT]: 'Image',
    [EvidenceType.LOG]: 'ScrollText',
    [EvidenceType.OTHER]: 'FileQuestion',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get audit type label
 */
export function getAuditTypeLabel(type: AuditType): string {
  const labels: Record<AuditType, string> = {
    [AuditType.INTERNAL]: 'Internal Audit',
    [AuditType.EXTERNAL]: 'External Audit',
    [AuditType.CERTIFICATION]: 'Certification Audit',
    [AuditType.SURVEILLANCE]: 'Surveillance Audit',
    [AuditType.RECERTIFICATION]: 'Recertification Audit',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get audit type color
 */
export function getAuditTypeColor(type: AuditType): string {
  const colors: Record<AuditType, string> = {
    [AuditType.INTERNAL]: 'blue-600',
    [AuditType.EXTERNAL]: 'indigo-600',
    [AuditType.CERTIFICATION]: 'green-600',
    [AuditType.SURVEILLANCE]: 'yellow-500',
    [AuditType.RECERTIFICATION]: 'purple-600',
  };
  return colors[type] || 'gray-500';
}

/**
 * Get audit type icon
 */
export function getAuditTypeIcon(type: AuditType): string {
  const icons: Record<AuditType, string> = {
    [AuditType.INTERNAL]: 'Search',
    [AuditType.EXTERNAL]: 'UserSearch',
    [AuditType.CERTIFICATION]: 'Award',
    [AuditType.SURVEILLANCE]: 'Eye',
    [AuditType.RECERTIFICATION]: 'RefreshCw',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get audit result label
 */
export function getAuditResultLabel(result: AuditResult): string {
  const labels: Record<AuditResult, string> = {
    [AuditResult.PASS]: 'Pass',
    [AuditResult.CONDITIONAL_PASS]: 'Conditional Pass',
    [AuditResult.FAIL]: 'Fail',
    [AuditResult.PENDING]: 'Pending',
  };
  return labels[result] || 'Unknown';
}

/**
 * Get audit result color
 */
export function getAuditResultColor(result: AuditResult): string {
  const colors: Record<AuditResult, string> = {
    [AuditResult.PASS]: 'green-600',
    [AuditResult.CONDITIONAL_PASS]: 'yellow-500',
    [AuditResult.FAIL]: 'red-600',
    [AuditResult.PENDING]: 'gray-500',
  };
  return colors[result] || 'gray-500';
}

/**
 * Get audit result icon
 */
export function getAuditResultIcon(result: AuditResult): string {
  const icons: Record<AuditResult, string> = {
    [AuditResult.PASS]: 'CheckCircle2',
    [AuditResult.CONDITIONAL_PASS]: 'AlertCircle',
    [AuditResult.FAIL]: 'XCircle',
    [AuditResult.PENDING]: 'Clock',
  };
  return icons[result] || 'HelpCircle';
}

/**
 * Get nonconformity type label
 */
export function getNonconformityTypeLabel(type: NonconformityType): string {
  const labels: Record<NonconformityType, string> = {
    [NonconformityType.MAJOR]: 'Major',
    [NonconformityType.MINOR]: 'Minor',
    [NonconformityType.OBSERVATION]: 'Observation',
  };
  return labels[type] || 'Unknown';
}

/**
 * Get nonconformity type color
 */
export function getNonconformityTypeColor(type: NonconformityType): string {
  const colors: Record<NonconformityType, string> = {
    [NonconformityType.MAJOR]: 'red-600',
    [NonconformityType.MINOR]: 'yellow-500',
    [NonconformityType.OBSERVATION]: 'blue-500',
  };
  return colors[type] || 'gray-500';
}

/**
 * Get nonconformity type icon
 */
export function getNonconformityTypeIcon(type: NonconformityType): string {
  const icons: Record<NonconformityType, string> = {
    [NonconformityType.MAJOR]: 'XOctagon',
    [NonconformityType.MINOR]: 'AlertTriangle',
    [NonconformityType.OBSERVATION]: 'Info',
  };
  return icons[type] || 'HelpCircle';
}

/**
 * Get nonconformity source label
 */
export function getNonconformitySourceLabel(source: NonconformitySource): string {
  const labels: Record<NonconformitySource, string> = {
    [NonconformitySource.INTERNAL_AUDIT]: 'Internal Audit',
    [NonconformitySource.EXTERNAL_AUDIT]: 'External Audit',
    [NonconformitySource.MANAGEMENT_REVIEW]: 'Management Review',
    [NonconformitySource.INCIDENT]: 'Incident',
    [NonconformitySource.EXERCISE]: 'Exercise',
    [NonconformitySource.MONITORING]: 'Monitoring',
    [NonconformitySource.SELF_ASSESSMENT]: 'Self Assessment',
  };
  return labels[source] || 'Unknown';
}

/**
 * Get nonconformity source color
 */
export function getNonconformitySourceColor(source: NonconformitySource): string {
  const colors: Record<NonconformitySource, string> = {
    [NonconformitySource.INTERNAL_AUDIT]: 'blue-600',
    [NonconformitySource.EXTERNAL_AUDIT]: 'indigo-600',
    [NonconformitySource.MANAGEMENT_REVIEW]: 'purple-600',
    [NonconformitySource.INCIDENT]: 'red-600',
    [NonconformitySource.EXERCISE]: 'orange-500',
    [NonconformitySource.MONITORING]: 'cyan-600',
    [NonconformitySource.SELF_ASSESSMENT]: 'teal-600',
  };
  return colors[source] || 'gray-500';
}

/**
 * Get nonconformity source icon
 */
export function getNonconformitySourceIcon(source: NonconformitySource): string {
  const icons: Record<NonconformitySource, string> = {
    [NonconformitySource.INTERNAL_AUDIT]: 'Search',
    [NonconformitySource.EXTERNAL_AUDIT]: 'UserSearch',
    [NonconformitySource.MANAGEMENT_REVIEW]: 'ClipboardList',
    [NonconformitySource.INCIDENT]: 'AlertCircle',
    [NonconformitySource.EXERCISE]: 'Target',
    [NonconformitySource.MONITORING]: 'Eye',
    [NonconformitySource.SELF_ASSESSMENT]: 'ClipboardCheck',
  };
  return icons[source] || 'HelpCircle';
}

/**
 * Get RCA method label
 */
export function getRCAMethodLabel(method: RCAMethod): string {
  const labels: Record<RCAMethod, string> = {
    [RCAMethod.FIVE_WHYS]: '5 Whys',
    [RCAMethod.FISHBONE]: 'Fishbone Diagram',
    [RCAMethod.FAULT_TREE]: 'Fault Tree Analysis',
    [RCAMethod.PARETO]: 'Pareto Analysis',
    [RCAMethod.BARRIER_ANALYSIS]: 'Barrier Analysis',
  };
  return labels[method] || 'Unknown';
}

/**
 * Get RCA method color
 */
export function getRCAMethodColor(method: RCAMethod): string {
  const colors: Record<RCAMethod, string> = {
    [RCAMethod.FIVE_WHYS]: 'blue-600',
    [RCAMethod.FISHBONE]: 'purple-600',
    [RCAMethod.FAULT_TREE]: 'indigo-600',
    [RCAMethod.PARETO]: 'orange-600',
    [RCAMethod.BARRIER_ANALYSIS]: 'teal-600',
  };
  return colors[method] || 'gray-500';
}

/**
 * Get RCA method icon
 */
export function getRCAMethodIcon(method: RCAMethod): string {
  const icons: Record<RCAMethod, string> = {
    [RCAMethod.FIVE_WHYS]: 'HelpCircle',
    [RCAMethod.FISHBONE]: 'GitBranch',
    [RCAMethod.FAULT_TREE]: 'TreeDeciduous',
    [RCAMethod.PARETO]: 'BarChart3',
    [RCAMethod.BARRIER_ANALYSIS]: 'ShieldAlert',
  };
  return icons[method] || 'HelpCircle';
}

/**
 * Get evidence state label
 */
export function getEvidenceStateLabel(state: EvidenceState): string {
  const labels: Record<EvidenceState, string> = {
    [EvidenceState.DRAFT]: 'Draft',
    [EvidenceState.SUBMITTED]: 'Submitted',
    [EvidenceState.UNDER_REVIEW]: 'Under Review',
    [EvidenceState.APPROVED]: 'Approved',
    [EvidenceState.REJECTED]: 'Rejected',
    [EvidenceState.EXPIRED]: 'Expired',
  };
  return labels[state] || 'Unknown';
}

/**
 * Get evidence state color
 */
export function getEvidenceStateColor(state: EvidenceState): string {
  const colors: Record<EvidenceState, string> = {
    [EvidenceState.DRAFT]: 'gray-500',
    [EvidenceState.SUBMITTED]: 'blue-500',
    [EvidenceState.UNDER_REVIEW]: 'yellow-500',
    [EvidenceState.APPROVED]: 'green-600',
    [EvidenceState.REJECTED]: 'red-600',
    [EvidenceState.EXPIRED]: 'orange-500',
  };
  return colors[state] || 'gray-500';
}

/**
 * Get evidence state icon
 */
export function getEvidenceStateIcon(state: EvidenceState): string {
  const icons: Record<EvidenceState, string> = {
    [EvidenceState.DRAFT]: 'FileEdit',
    [EvidenceState.SUBMITTED]: 'Send',
    [EvidenceState.UNDER_REVIEW]: 'Eye',
    [EvidenceState.APPROVED]: 'CheckCircle',
    [EvidenceState.REJECTED]: 'XCircle',
    [EvidenceState.EXPIRED]: 'Clock',
  };
  return icons[state] || 'HelpCircle';
}

/**
 * Get assessment state label
 */
export function getAssessmentStateLabel(state: AssessmentState): string {
  const labels: Record<AssessmentState, string> = {
    [AssessmentState.PLANNED]: 'Planned',
    [AssessmentState.IN_PROGRESS]: 'In Progress',
    [AssessmentState.UNDER_REVIEW]: 'Under Review',
    [AssessmentState.COMPLETED]: 'Completed',
    [AssessmentState.CANCELLED]: 'Cancelled',
  };
  return labels[state] || 'Unknown';
}

/**
 * Get assessment state color
 */
export function getAssessmentStateColor(state: AssessmentState): string {
  const colors: Record<AssessmentState, string> = {
    [AssessmentState.PLANNED]: 'gray-500',
    [AssessmentState.IN_PROGRESS]: 'blue-600',
    [AssessmentState.UNDER_REVIEW]: 'yellow-500',
    [AssessmentState.COMPLETED]: 'green-600',
    [AssessmentState.CANCELLED]: 'gray-400',
  };
  return colors[state] || 'gray-500';
}

/**
 * Get assessment state icon
 */
export function getAssessmentStateIcon(state: AssessmentState): string {
  const icons: Record<AssessmentState, string> = {
    [AssessmentState.PLANNED]: 'Calendar',
    [AssessmentState.IN_PROGRESS]: 'PlayCircle',
    [AssessmentState.UNDER_REVIEW]: 'Eye',
    [AssessmentState.COMPLETED]: 'CheckCircle',
    [AssessmentState.CANCELLED]: 'XCircle',
  };
  return icons[state] || 'HelpCircle';
}

/**
 * Get gap state label
 */
export function getGapStateLabel(state: GapState): string {
  const labels: Record<GapState, string> = {
    [GapState.IDENTIFIED]: 'Identified',
    [GapState.IN_REMEDIATION]: 'In Remediation',
    [GapState.PENDING_VERIFICATION]: 'Pending Verification',
    [GapState.RESOLVED]: 'Resolved',
    [GapState.RISK_ACCEPTED]: 'Risk Accepted',
    [GapState.REOPENED]: 'Reopened',
  };
  return labels[state] || 'Unknown';
}

/**
 * Get gap state color
 */
export function getGapStateColor(state: GapState): string {
  const colors: Record<GapState, string> = {
    [GapState.IDENTIFIED]: 'red-500',
    [GapState.IN_REMEDIATION]: 'blue-600',
    [GapState.PENDING_VERIFICATION]: 'yellow-500',
    [GapState.RESOLVED]: 'green-600',
    [GapState.RISK_ACCEPTED]: 'purple-500',
    [GapState.REOPENED]: 'orange-600',
  };
  return colors[state] || 'gray-500';
}

/**
 * Get gap state icon
 */
export function getGapStateIcon(state: GapState): string {
  const icons: Record<GapState, string> = {
    [GapState.IDENTIFIED]: 'AlertCircle',
    [GapState.IN_REMEDIATION]: 'Wrench',
    [GapState.PENDING_VERIFICATION]: 'Clock',
    [GapState.RESOLVED]: 'CheckCircle',
    [GapState.RISK_ACCEPTED]: 'Shield',
    [GapState.REOPENED]: 'RotateCcw',
  };
  return icons[state] || 'HelpCircle';
}

/**
 * Get audit state label
 */
export function getAuditStateLabel(state: AuditState): string {
  const labels: Record<AuditState, string> = {
    [AuditState.PLANNED]: 'Planned',
    [AuditState.PREPARING]: 'Preparing',
    [AuditState.IN_PROGRESS]: 'In Progress',
    [AuditState.REVIEW]: 'Under Review',
    [AuditState.COMPLETED]: 'Completed',
    [AuditState.CANCELLED]: 'Cancelled',
  };
  return labels[state] || 'Unknown';
}

/**
 * Get audit state color
 */
export function getAuditStateColor(state: AuditState): string {
  const colors: Record<AuditState, string> = {
    [AuditState.PLANNED]: 'gray-500',
    [AuditState.PREPARING]: 'blue-500',
    [AuditState.IN_PROGRESS]: 'blue-600',
    [AuditState.REVIEW]: 'yellow-500',
    [AuditState.COMPLETED]: 'green-600',
    [AuditState.CANCELLED]: 'gray-400',
  };
  return colors[state] || 'gray-500';
}

/**
 * Get audit state icon
 */
export function getAuditStateIcon(state: AuditState): string {
  const icons: Record<AuditState, string> = {
    [AuditState.PLANNED]: 'Calendar',
    [AuditState.PREPARING]: 'FileText',
    [AuditState.IN_PROGRESS]: 'Search',
    [AuditState.REVIEW]: 'Eye',
    [AuditState.COMPLETED]: 'CheckCircle',
    [AuditState.CANCELLED]: 'XCircle',
  };
  return icons[state] || 'HelpCircle';
}

/**
 * Get nonconformity state label
 */
export function getNonconformityStateLabel(state: NonconformityState): string {
  const labels: Record<NonconformityState, string> = {
    [NonconformityState.IDENTIFIED]: 'Identified',
    [NonconformityState.RCA_IN_PROGRESS]: 'RCA In Progress',
    [NonconformityState.ACTION_PLANNING]: 'Action Planning',
    [NonconformityState.ACTIONS_IN_PROGRESS]: 'Actions In Progress',
    [NonconformityState.PENDING_VERIFICATION]: 'Pending Verification',
    [NonconformityState.VERIFIED]: 'Verified',
    [NonconformityState.CLOSED]: 'Closed',
  };
  return labels[state] || 'Unknown';
}

/**
 * Get nonconformity state color
 */
export function getNonconformityStateColor(state: NonconformityState): string {
  const colors: Record<NonconformityState, string> = {
    [NonconformityState.IDENTIFIED]: 'red-500',
    [NonconformityState.RCA_IN_PROGRESS]: 'orange-500',
    [NonconformityState.ACTION_PLANNING]: 'yellow-500',
    [NonconformityState.ACTIONS_IN_PROGRESS]: 'blue-600',
    [NonconformityState.PENDING_VERIFICATION]: 'purple-500',
    [NonconformityState.VERIFIED]: 'green-500',
    [NonconformityState.CLOSED]: 'green-600',
  };
  return colors[state] || 'gray-500';
}

/**
 * Get nonconformity state icon
 */
export function getNonconformityStateIcon(state: NonconformityState): string {
  const icons: Record<NonconformityState, string> = {
    [NonconformityState.IDENTIFIED]: 'AlertCircle',
    [NonconformityState.RCA_IN_PROGRESS]: 'Search',
    [NonconformityState.ACTION_PLANNING]: 'ClipboardList',
    [NonconformityState.ACTIONS_IN_PROGRESS]: 'Wrench',
    [NonconformityState.PENDING_VERIFICATION]: 'Clock',
    [NonconformityState.VERIFIED]: 'CheckCircle',
    [NonconformityState.CLOSED]: 'CheckCircle2',
  };
  return icons[state] || 'HelpCircle';
}
