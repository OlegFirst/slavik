/**
 * Compliance Module - API Client
 * Handles all API communication for Compliance Management module
 *
 * Created: 2025-10-23
 * Agent: 17 (Compliance Module Foundation)
 *
 * Total Endpoints: 97
 * - Assessments: 9 endpoints
 * - Gaps: 14 endpoints
 * - Evidence: 8 endpoints
 * - Audits: 10 endpoints
 * - Management Reviews: 7 endpoints
 * - Improvements: 8 endpoints
 * - Templates: 12 endpoints
 * - Nonconformities: 5 endpoints
 * - Analytics & Dashboard: 6 endpoints
 * - Knowledge Base: 8 endpoints
 * - Bulk Operations: 4 endpoints
 * - Health & Registry: 6 endpoints
 */

import { apiClient } from './client';

// ==================== TYPE DEFINITIONS ====================

/**
 * Assessment Status
 */
export enum AssessmentStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  APPROVED = 'approved',
  ARCHIVED = 'archived',
}

/**
 * Gap Status
 */
export enum GapStatus {
  IDENTIFIED = 'identified',
  IN_REMEDIATION = 'in_remediation',
  PENDING_VERIFICATION = 'pending_verification',
  RESOLVED = 'resolved',
  REOPENED = 'reopened',
}

/**
 * Gap Severity
 */
export enum GapSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Evidence Status
 */
export enum EvidenceStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

/**
 * Audit Status
 */
export enum AuditStatus {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/**
 * Template Category
 */
export enum TemplateCategory {
  POLICY = 'policy',
  PROCEDURE = 'procedure',
  PLAN = 'plan',
  FORM = 'form',
  CHECKLIST = 'checklist',
  REPORT = 'report',
}

/**
 * RCA Method
 */
export enum RCAMethod {
  FIVE_WHYS = '5_whys',
  FISHBONE = 'fishbone',
  FAULT_TREE = 'fault_tree',
  ROOT_CAUSE_TREE = 'root_cause_tree',
}

/**
 * Improvement Status
 */
export enum ImprovementStatus {
  PROPOSED = 'proposed',
  APPROVED = 'approved',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  VERIFIED = 'verified',
  CANCELLED = 'cancelled',
}

/**
 * Review Status
 */
export enum ReviewStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/**
 * Compliance Assessment
 */
export interface ComplianceAssessment {
  id?: string;
  organization_id: string;
  assessment_name: string;
  description?: string;
  standard?: string;
  scope?: string;
  status: AssessmentStatus;
  assessor_id?: string;
  start_date?: string;
  end_date?: string;
  completion_date?: string;
  overall_score?: number;
  findings_count?: number;
  gaps_identified?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Assessment Create
 */
export interface ComplianceAssessmentCreate {
  organization_id: string;
  assessment_name: string;
  description?: string;
  standard?: string;
  scope?: string;
  assessor_id?: string;
  start_date?: string;
  end_date?: string;
}

/**
 * Assessment Update
 */
export interface ComplianceAssessmentUpdate {
  assessment_name?: string;
  description?: string;
  standard?: string;
  scope?: string;
  status?: AssessmentStatus;
  assessor_id?: string;
  start_date?: string;
  end_date?: string;
  completion_date?: string;
  overall_score?: number;
}

/**
 * Assessment Results
 */
export interface AssessmentResults {
  assessment_id: string;
  overall_score: number;
  by_clause: Record<string, number>;
  gaps_identified: number;
  compliance_percentage: number;
  recommendations: string[];
}

/**
 * Compliance Gap
 */
export interface ComplianceGap {
  id?: string;
  organization_id: string;
  gap_title: string;
  description: string;
  severity: GapSeverity;
  status: GapStatus;
  requirement_id?: string;
  assessment_id?: string;
  identified_date?: string;
  target_closure_date?: string;
  actual_closure_date?: string;
  responsible_user_id?: string;
  remediation_plan?: string;
  progress_percentage?: number;
  verification_notes?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Gap Create
 */
export interface ComplianceGapCreate {
  organization_id: string;
  gap_title: string;
  description: string;
  severity: GapSeverity;
  requirement_id?: string;
  assessment_id?: string;
  target_closure_date?: string;
  responsible_user_id?: string;
  remediation_plan?: string;
}

/**
 * Gap Update
 */
export interface ComplianceGapUpdate {
  gap_title?: string;
  description?: string;
  severity?: GapSeverity;
  status?: GapStatus;
  target_closure_date?: string;
  actual_closure_date?: string;
  responsible_user_id?: string;
  remediation_plan?: string;
  progress_percentage?: number;
  verification_notes?: string;
}

/**
 * RCA Analysis
 */
export interface RCAAnalysis {
  id?: string;
  gap_id: string;
  method: RCAMethod;
  analysis_data: Record<string, any>;
  root_causes: string[];
  contributing_factors?: string[];
  recommendations: string[];
  analyzed_by?: string;
  analyzed_at?: string;
}

/**
 * RCA Create
 */
export interface RCAAnalysisCreate {
  gap_id: string;
  method: RCAMethod;
  analysis_data: Record<string, any>;
  root_causes: string[];
  contributing_factors?: string[];
  recommendations: string[];
}

/**
 * Effectiveness Review
 */
export interface EffectivenessReview {
  id?: string;
  gap_id: string;
  review_date: string;
  is_effective: boolean;
  findings: string;
  recommendations?: string[];
  reviewer_id?: string;
}

/**
 * Compliance Evidence
 */
export interface ComplianceEvidence {
  id?: string;
  organization_id: string;
  evidence_name: string;
  description?: string;
  evidence_type: string;
  file_url?: string;
  file_metadata?: Record<string, any>;
  status: EvidenceStatus;
  requirement_ids?: string[];
  assessment_id?: string;
  collected_date?: string;
  expiry_date?: string;
  verified_by?: string;
  verification_date?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Evidence Create
 */
export interface ComplianceEvidenceCreate {
  organization_id: string;
  evidence_name: string;
  description?: string;
  evidence_type: string;
  file_url?: string;
  file_metadata?: Record<string, any>;
  requirement_ids?: string[];
  assessment_id?: string;
  collected_date?: string;
  expiry_date?: string;
}

/**
 * Evidence Update
 */
export interface ComplianceEvidenceUpdate {
  evidence_name?: string;
  description?: string;
  evidence_type?: string;
  file_url?: string;
  file_metadata?: Record<string, any>;
  status?: EvidenceStatus;
  requirement_ids?: string[];
  collected_date?: string;
  expiry_date?: string;
  verified_by?: string;
  verification_date?: string;
}

/**
 * Evidence History
 */
export interface EvidenceHistory {
  evidence_id: string;
  history: Array<{
    timestamp: string;
    action: string;
    user_id?: string;
    changes?: Record<string, any>;
  }>;
}

/**
 * Compliance Audit
 */
export interface ComplianceAudit {
  id?: string;
  organization_id: string;
  audit_name: string;
  description?: string;
  audit_type: string;
  standard?: string;
  scope?: string;
  status: AuditStatus;
  lead_auditor_id?: string;
  audit_team?: string[];
  scheduled_start?: string;
  scheduled_end?: string;
  actual_start?: string;
  actual_end?: string;
  findings_count?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Audit Create
 */
export interface ComplianceAuditCreate {
  organization_id: string;
  audit_name: string;
  description?: string;
  audit_type: string;
  standard?: string;
  scope?: string;
  lead_auditor_id?: string;
  audit_team?: string[];
  scheduled_start?: string;
  scheduled_end?: string;
}

/**
 * Audit Update
 */
export interface ComplianceAuditUpdate {
  audit_name?: string;
  description?: string;
  audit_type?: string;
  standard?: string;
  scope?: string;
  status?: AuditStatus;
  lead_auditor_id?: string;
  audit_team?: string[];
  scheduled_start?: string;
  scheduled_end?: string;
  actual_start?: string;
  actual_end?: string;
}

/**
 * Audit Finding
 */
export interface AuditFinding {
  id?: string;
  audit_id: string;
  finding_title: string;
  description: string;
  severity: GapSeverity;
  requirement_id?: string;
  evidence_id?: string;
  recommendation?: string;
  created_at?: string;
}

/**
 * Audit Checklist
 */
export interface AuditChecklist {
  audit_id: string;
  items: Array<{
    id: string;
    requirement: string;
    status: 'compliant' | 'non_compliant' | 'not_applicable' | 'pending';
    notes?: string;
  }>;
}

/**
 * Audit Report
 */
export interface AuditReport {
  audit_id: string;
  audit_name: string;
  executive_summary: string;
  scope: string;
  methodology: string;
  findings: AuditFinding[];
  recommendations: string[];
  overall_rating: string;
  generated_at: string;
}

/**
 * Management Review
 */
export interface ManagementReview {
  id?: string;
  organization_id: string;
  review_name: string;
  review_date: string;
  status: ReviewStatus;
  attendees?: string[];
  agenda?: string[];
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  decisions?: string[];
  action_items?: string[];
  next_review_date?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Management Review Create
 */
export interface ManagementReviewCreate {
  organization_id: string;
  review_name: string;
  review_date: string;
  attendees?: string[];
  agenda?: string[];
}

/**
 * Review Inputs
 */
export interface ReviewInputs {
  performance_metrics: Record<string, any>;
  audit_results: any[];
  incidents: any[];
  compliance_status: Record<string, any>;
  resource_adequacy: Record<string, any>;
}

/**
 * Review Decision
 */
export interface ReviewDecision {
  decision_type: string;
  decision: string;
  rationale?: string;
  assigned_to?: string;
  due_date?: string;
}

/**
 * Improvement Initiative
 */
export interface ImprovementInitiative {
  id?: string;
  organization_id: string;
  initiative_title: string;
  description: string;
  category: string;
  status: ImprovementStatus;
  priority: 'critical' | 'high' | 'medium' | 'low';
  owner_id?: string;
  start_date?: string;
  target_date?: string;
  completion_date?: string;
  estimated_cost?: number;
  actual_cost?: number;
  expected_benefits?: string[];
  actual_benefits?: string[];
  progress_percentage?: number;
  verification_status?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Improvement Create
 */
export interface ImprovementInitiativeCreate {
  organization_id: string;
  initiative_title: string;
  description: string;
  category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  owner_id?: string;
  start_date?: string;
  target_date?: string;
  estimated_cost?: number;
  expected_benefits?: string[];
}

/**
 * Improvement Update
 */
export interface ImprovementInitiativeUpdate {
  initiative_title?: string;
  description?: string;
  category?: string;
  status?: ImprovementStatus;
  priority?: 'critical' | 'high' | 'medium' | 'low';
  owner_id?: string;
  start_date?: string;
  target_date?: string;
  completion_date?: string;
  estimated_cost?: number;
  actual_cost?: number;
  expected_benefits?: string[];
  actual_benefits?: string[];
  progress_percentage?: number;
}

/**
 * Improvement Dashboard
 */
export interface ImprovementDashboard {
  total_initiatives: number;
  by_status: Record<ImprovementStatus, number>;
  by_priority: Record<string, number>;
  total_investment: number;
  expected_roi: number;
  completion_rate: number;
  on_time_delivery: number;
}

/**
 * ROI Analysis
 */
export interface ROIAnalysis {
  initiative_id: string;
  estimated_cost: number;
  actual_cost: number;
  expected_benefits_value: number;
  actual_benefits_value: number;
  roi_percentage: number;
  payback_period_months: number;
}

/**
 * Compliance Template
 */
export interface ComplianceTemplate {
  id?: string;
  template_name: string;
  description?: string;
  category: TemplateCategory;
  template_type: string;
  content: string;
  variables?: string[];
  standard?: string;
  iso_clause?: string;
  workflow_type?: string;
  version: string;
  is_active: boolean;
  usage_count?: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * Template Create
 */
export interface ComplianceTemplateCreate {
  template_name: string;
  description?: string;
  category: TemplateCategory;
  template_type: string;
  content: string;
  variables?: string[];
  standard?: string;
  iso_clause?: string;
  workflow_type?: string;
}

/**
 * Template Update
 */
export interface ComplianceTemplateUpdate {
  template_name?: string;
  description?: string;
  category?: TemplateCategory;
  template_type?: string;
  content?: string;
  variables?: string[];
  standard?: string;
  iso_clause?: string;
}

/**
 * Template Render Request
 */
export interface TemplateRenderRequest {
  template_id: string;
  context: Record<string, any>;
}

/**
 * Template Render Result
 */
export interface TemplateRenderResult {
  rendered_content: string;
  format: string;
}

/**
 * BPMN Template
 */
export interface BPMNTemplate {
  workflow_type: string;
  bpmn_xml: string;
  description: string;
}

/**
 * Nonconformity
 */
export interface Nonconformity {
  id?: string;
  organization_id: string;
  nc_title: string;
  description: string;
  severity: GapSeverity;
  status: string;
  source: string;
  identified_date?: string;
  responsible_user_id?: string;
  corrective_action?: string;
  preventive_action?: string;
  rca_analysis?: RCAAnalysis;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * RCA Template
 */
export interface RCATemplate {
  method: RCAMethod;
  template_structure: Record<string, any>;
  instructions: string[];
  example?: Record<string, any>;
}

/**
 * Dashboard Overview
 */
export interface DashboardOverview {
  organization_id: string;
  compliance_score: number;
  assessments: {
    total: number;
    in_progress: number;
    completed: number;
  };
  gaps: {
    total: number;
    by_severity: Record<GapSeverity, number>;
    by_status: Record<GapStatus, number>;
  };
  audits: {
    total: number;
    upcoming: number;
    in_progress: number;
  };
  evidence: {
    total: number;
    expiring_soon: number;
  };
  recent_activities: any[];
}

/**
 * Analytics Data
 */
export interface AnalyticsData {
  metric_type: string;
  data: Record<string, any>;
  timestamp: string;
}

/**
 * Requirements Matrix
 */
export interface RequirementsMatrix {
  standard: string;
  requirements: Array<{
    requirement_id: string;
    clause: string;
    description: string;
    compliance_status: 'compliant' | 'partial' | 'non_compliant' | 'not_assessed';
    evidence_count: number;
    gap_count: number;
  }>;
}

/**
 * Compliance Roadmap
 */
export interface ComplianceRoadmap {
  milestones: Array<{
    milestone_name: string;
    target_date: string;
    status: string;
    dependencies: string[];
    deliverables: string[];
  }>;
  timeline: Array<{
    date: string;
    event: string;
    type: string;
  }>;
}

/**
 * Standard
 */
export interface ComplianceStandard {
  id: string;
  standard_name: string;
  version: string;
  description: string;
  clauses: any[];
}

/**
 * ISO 22301 Clause
 */
export interface ISO22301Clause {
  clause_number: string;
  title: string;
  description: string;
  requirements: string[];
  guidance: string[];
}

/**
 * BCI Practice
 */
export interface BCIPractice {
  practice_id: string;
  practice_name: string;
  category: string;
  description: string;
  implementation_guide: string[];
}

/**
 * WHO Framework
 */
export interface WHOFramework {
  framework_id: string;
  framework_name: string;
  components: any[];
  guidance: string[];
}

/**
 * Mapping Data
 */
export interface MappingData {
  source_standard: string;
  target_standard: string;
  mappings: Array<{
    source_clause: string;
    target_clauses: string[];
    mapping_type: 'equivalent' | 'similar' | 'related' | 'none';
  }>;
}

/**
 * Library Resource
 */
export interface LibraryResource {
  id: string;
  resource_type: 'guide' | 'best_practice' | 'case_study' | 'research';
  title: string;
  description: string;
  content: string;
  tags: string[];
  author?: string;
  published_date?: string;
}

/**
 * Bulk Operation Request
 */
export interface BulkOperationRequest {
  operation: 'create' | 'update' | 'delete';
  items: any[];
}

/**
 * Bulk Operation Result
 */
export interface BulkOperationResult {
  total: number;
  successful: number;
  failed: number;
  errors: Array<{
    index: number;
    error: string;
  }>;
}

/**
 * Health Status
 */
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  dependencies: Record<string, string>;
}

/**
 * Service Info
 */
export interface ServiceInfo {
  service_name: string;
  version: string;
  description: string;
  endpoints_count: number;
}

/**
 * Service Registry
 */
export interface ServiceRegistry {
  services: Array<{
    name: string;
    status: string;
    url: string;
    version: string;
  }>;
}

/**
 * AI Advice
 */
export interface AIAdvice {
  item_id: string;
  advice_type: string;
  recommendations: string[];
  confidence_score: number;
  generated_at: string;
}

/**
 * Benchmark Data
 */
export interface BenchmarkData {
  benchmark_type: string;
  metrics: Record<string, any>;
  industry_average: Record<string, any>;
  percentile_ranking: number;
}

/**
 * List Parameters
 */
export interface ListParams {
  organization_id: string;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
}

/**
 * List Response
 */
export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

// ==================== API CLIENT ====================

const API_BASE = '/api/v1/compliance';

/**
 * Compliance Module API Client
 * Comprehensive client for all compliance management endpoints
 */
export const complianceClient = {
  // ============= ASSESSMENTS (9 functions) =============

  /**
   * List compliance assessments
   * GET /
   */
  async listAssessments(params: ListParams): Promise<ComplianceAssessment[]> {
    const query = new URLSearchParams();
    query.set('organization_id', params.organization_id);
    if (params.status) query.set('status', params.status);
    if (params.search) query.set('search', params.search);
    if (params.page !== undefined) query.set('page', String(params.page));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<ComplianceAssessment[]>({
      method: 'GET',
      url: `${API_BASE}?${query.toString()}`,
    });
  },

  /**
   * Get single assessment by ID
   * GET /{assessment_id}
   */
  async getAssessment(assessmentId: string): Promise<ComplianceAssessment> {
    return apiClient.request<ComplianceAssessment>({
      method: 'GET',
      url: `${API_BASE}/${assessmentId}`,
    });
  },

  /**
   * Create new assessment
   * POST /
   */
  async createAssessment(data: ComplianceAssessmentCreate): Promise<ComplianceAssessment> {
    return apiClient.request<ComplianceAssessment>({
      method: 'POST',
      url: `${API_BASE}`,
      data,
    });
  },

  /**
   * Update assessment
   * PUT /{assessment_id}
   */
  async updateAssessment(assessmentId: string, data: ComplianceAssessmentUpdate): Promise<ComplianceAssessment> {
    return apiClient.request<ComplianceAssessment>({
      method: 'PUT',
      url: `${API_BASE}/${assessmentId}`,
      data,
    });
  },

  /**
   * Delete assessment
   * DELETE /{assessment_id}
   */
  async deleteAssessment(assessmentId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${API_BASE}/${assessmentId}`,
    });
  },

  /**
   * Run assessment
   * POST /{assessment_id}/run
   */
  async runAssessment(assessmentId: string): Promise<ComplianceAssessment> {
    return apiClient.request<ComplianceAssessment>({
      method: 'POST',
      url: `${API_BASE}/${assessmentId}/run`,
    });
  },

  /**
   * Get assessment results
   * GET /{assessment_id}/results
   */
  async getAssessmentResults(assessmentId: string): Promise<AssessmentResults> {
    return apiClient.request<AssessmentResults>({
      method: 'GET',
      url: `${API_BASE}/${assessmentId}/results`,
    });
  },

  /**
   * Batch AI scan for assessments
   * POST /batch-ai-scan
   */
  async batchAIScan(assessmentIds: string[]): Promise<any> {
    return apiClient.request<any>({
      method: 'POST',
      url: `${API_BASE}/batch-ai-scan`,
      data: { assessment_ids: assessmentIds },
    });
  },

  /**
   * Check compliance status
   * GET /api/compliance/check
   */
  async checkCompliance(organizationId: string): Promise<any> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<any>({
      method: 'GET',
      url: `/api/compliance/check?${query.toString()}`,
    });
  },

  // ============= GAPS (14 functions) =============

  /**
   * List compliance gaps
   * GET /gaps
   */
  async listGaps(params: ListParams): Promise<ComplianceGap[]> {
    const query = new URLSearchParams();
    query.set('organization_id', params.organization_id);
    if (params.status) query.set('status', params.status);
    if (params.search) query.set('search', params.search);
    if (params.page !== undefined) query.set('page', String(params.page));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<ComplianceGap[]>({
      method: 'GET',
      url: `${API_BASE}/gaps?${query.toString()}`,
    });
  },

  /**
   * Get single gap by ID
   * GET /{gap_id}
   */
  async getGap(gapId: string): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'GET',
      url: `${API_BASE}/${gapId}`,
    });
  },

  /**
   * Create new gap
   * POST /gaps
   */
  async createGap(data: ComplianceGapCreate): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'POST',
      url: `${API_BASE}/gaps`,
      data,
    });
  },

  /**
   * Update gap
   * PATCH /{gap_id}
   */
  async updateGap(gapId: string, data: ComplianceGapUpdate): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'PATCH',
      url: `${API_BASE}/${gapId}`,
      data,
    });
  },

  /**
   * Delete gap
   * DELETE /{gap_id}
   */
  async deleteGap(gapId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${API_BASE}/${gapId}`,
    });
  },

  /**
   * Resolve gap
   * POST /{gap_id}/resolve
   */
  async resolveGap(gapId: string, resolutionNotes: string): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'POST',
      url: `${API_BASE}/${gapId}/resolve`,
      data: { resolution_notes: resolutionNotes },
    });
  },

  /**
   * Reopen gap
   * POST /{gap_id}/reopen
   */
  async reopenGap(gapId: string, reason: string): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'POST',
      url: `${API_BASE}/${gapId}/reopen`,
      data: { reason },
    });
  },

  /**
   * Start gap remediation
   * POST /{gap_id}/start-remediation
   */
  async startGapRemediation(gapId: string): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'POST',
      url: `${API_BASE}/${gapId}/start-remediation`,
    });
  },

  /**
   * Update gap progress
   * POST /{gap_id}/update-progress
   */
  async updateGapProgress(gapId: string, progress: number): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'POST',
      url: `${API_BASE}/${gapId}/update-progress`,
      data: { progress_percentage: progress },
    });
  },

  /**
   * Verify gap closure
   * POST /{gap_id}/verify
   */
  async verifyGap(gapId: string, verificationNotes: string): Promise<ComplianceGap> {
    return apiClient.request<ComplianceGap>({
      method: 'POST',
      url: `${API_BASE}/${gapId}/verify`,
      data: { verification_notes: verificationNotes },
    });
  },

  /**
   * Get gap RCA
   * GET /{gap_id}/rca
   */
  async getGapRCA(gapId: string): Promise<RCAAnalysis> {
    return apiClient.request<RCAAnalysis>({
      method: 'GET',
      url: `${API_BASE}/${gapId}/rca`,
    });
  },

  /**
   * Create gap RCA
   * POST /{gap_id}/rca
   */
  async createGapRCA(data: RCAAnalysisCreate): Promise<RCAAnalysis> {
    return apiClient.request<RCAAnalysis>({
      method: 'POST',
      url: `${API_BASE}/${data.gap_id}/rca`,
      data,
    });
  },

  /**
   * Get effectiveness reviews
   * GET /{gap_id}/effectiveness-reviews
   */
  async getEffectivenessReviews(gapId: string): Promise<EffectivenessReview[]> {
    return apiClient.request<EffectivenessReview[]>({
      method: 'GET',
      url: `${API_BASE}/${gapId}/effectiveness-reviews`,
    });
  },

  /**
   * Create effectiveness review
   * POST /{gap_id}/effectiveness-review
   */
  async createEffectivenessReview(gapId: string, review: Omit<EffectivenessReview, 'id' | 'gap_id'>): Promise<EffectivenessReview> {
    return apiClient.request<EffectivenessReview>({
      method: 'POST',
      url: `${API_BASE}/${gapId}/effectiveness-review`,
      data: review,
    });
  },

  /**
   * Get gaps by severity
   * GET /severity/{severity}
   */
  async getGapsBySeverity(severity: GapSeverity, organizationId: string): Promise<ComplianceGap[]> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<ComplianceGap[]>({
      method: 'GET',
      url: `${API_BASE}/severity/${severity}?${query.toString()}`,
    });
  },

  // ============= EVIDENCE (8 functions) =============

  /**
   * List evidence
   * GET /evidence
   */
  async listEvidence(params: ListParams): Promise<ComplianceEvidence[]> {
    const query = new URLSearchParams();
    query.set('organization_id', params.organization_id);
    if (params.status) query.set('status', params.status);
    if (params.search) query.set('search', params.search);
    if (params.page !== undefined) query.set('page', String(params.page));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<ComplianceEvidence[]>({
      method: 'GET',
      url: `${API_BASE}/evidence?${query.toString()}`,
    });
  },

  /**
   * Get single evidence by ID
   * GET /{evidence_id}
   */
  async getEvidence(evidenceId: string): Promise<ComplianceEvidence> {
    return apiClient.request<ComplianceEvidence>({
      method: 'GET',
      url: `${API_BASE}/${evidenceId}`,
    });
  },

  /**
   * Upload evidence
   * POST /evidence
   */
  async uploadEvidence(data: ComplianceEvidenceCreate): Promise<ComplianceEvidence> {
    return apiClient.request<ComplianceEvidence>({
      method: 'POST',
      url: `${API_BASE}/evidence`,
      data,
    });
  },

  /**
   * Update evidence
   * PATCH /{evidence_id}
   */
  async updateEvidence(evidenceId: string, data: ComplianceEvidenceUpdate): Promise<ComplianceEvidence> {
    return apiClient.request<ComplianceEvidence>({
      method: 'PATCH',
      url: `${API_BASE}/${evidenceId}`,
      data,
    });
  },

  /**
   * Delete evidence
   * DELETE /{evidence_id}
   */
  async deleteEvidence(evidenceId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${API_BASE}/${evidenceId}`,
    });
  },

  /**
   * Transition evidence status
   * POST /{evidence_id}/transition
   */
  async transitionEvidence(evidenceId: string, newStatus: EvidenceStatus): Promise<ComplianceEvidence> {
    return apiClient.request<ComplianceEvidence>({
      method: 'POST',
      url: `${API_BASE}/${evidenceId}/transition`,
      data: { new_status: newStatus },
    });
  },

  /**
   * Get evidence history
   * GET /{evidence_id}/history
   */
  async getEvidenceHistory(evidenceId: string): Promise<EvidenceHistory> {
    return apiClient.request<EvidenceHistory>({
      method: 'GET',
      url: `${API_BASE}/${evidenceId}/history`,
    });
  },

  /**
   * Bulk evidence operations
   * POST /evidence/bulk
   */
  async bulkEvidenceOperation(request: BulkOperationRequest): Promise<BulkOperationResult> {
    return apiClient.request<BulkOperationResult>({
      method: 'POST',
      url: `${API_BASE}/evidence/bulk`,
      data: request,
    });
  },

  // ============= AUDITS (10 functions) =============

  /**
   * List audits
   * GET /audits
   */
  async listAudits(params: ListParams): Promise<ComplianceAudit[]> {
    const query = new URLSearchParams();
    query.set('organization_id', params.organization_id);
    if (params.status) query.set('status', params.status);
    if (params.search) query.set('search', params.search);
    if (params.page !== undefined) query.set('page', String(params.page));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<ComplianceAudit[]>({
      method: 'GET',
      url: `${API_BASE}/audits?${query.toString()}`,
    });
  },

  /**
   * Get single audit by ID
   * GET /{audit_id}
   */
  async getAudit(auditId: string): Promise<ComplianceAudit> {
    return apiClient.request<ComplianceAudit>({
      method: 'GET',
      url: `${API_BASE}/audits/${auditId}`,
    });
  },

  /**
   * Create audit
   * POST /audits
   */
  async createAudit(data: ComplianceAuditCreate): Promise<ComplianceAudit> {
    return apiClient.request<ComplianceAudit>({
      method: 'POST',
      url: `${API_BASE}/audits`,
      data,
    });
  },

  /**
   * Update audit
   * PUT /{audit_id}
   */
  async updateAudit(auditId: string, data: ComplianceAuditUpdate): Promise<ComplianceAudit> {
    return apiClient.request<ComplianceAudit>({
      method: 'PUT',
      url: `${API_BASE}/audits/${auditId}`,
      data,
    });
  },

  /**
   * Delete audit
   * DELETE /{audit_id}
   */
  async deleteAudit(auditId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${API_BASE}/audits/${auditId}`,
    });
  },

  /**
   * Start audit
   * POST /{audit_id}/start
   */
  async startAudit(auditId: string): Promise<ComplianceAudit> {
    return apiClient.request<ComplianceAudit>({
      method: 'POST',
      url: `${API_BASE}/${auditId}/start`,
    });
  },

  /**
   * Complete audit
   * POST /{audit_id}/complete
   */
  async completeAudit(auditId: string): Promise<ComplianceAudit> {
    return apiClient.request<ComplianceAudit>({
      method: 'POST',
      url: `${API_BASE}/${auditId}/complete`,
    });
  },

  /**
   * Get audit checklist
   * GET /{audit_id}/checklist
   */
  async getAuditChecklist(auditId: string): Promise<AuditChecklist> {
    return apiClient.request<AuditChecklist>({
      method: 'GET',
      url: `${API_BASE}/${auditId}/checklist`,
    });
  },

  /**
   * Get audit findings
   * GET /{audit_id}/findings
   */
  async getAuditFindings(auditId: string): Promise<AuditFinding[]> {
    return apiClient.request<AuditFinding[]>({
      method: 'GET',
      url: `${API_BASE}/${auditId}/findings`,
    });
  },

  /**
   * Create audit finding
   * POST /{audit_id}/findings
   */
  async createAuditFinding(auditId: string, finding: Omit<AuditFinding, 'id' | 'audit_id' | 'created_at'>): Promise<AuditFinding> {
    return apiClient.request<AuditFinding>({
      method: 'POST',
      url: `${API_BASE}/${auditId}/findings`,
      data: finding,
    });
  },

  /**
   * Get audit report
   * GET /{audit_id}/report
   */
  async getAuditReport(auditId: string): Promise<AuditReport> {
    return apiClient.request<AuditReport>({
      method: 'GET',
      url: `${API_BASE}/${auditId}/report`,
    });
  },

  /**
   * List audit programs
   * GET /programs
   */
  async listAuditPrograms(organizationId: string): Promise<any[]> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<any[]>({
      method: 'GET',
      url: `${API_BASE}/programs?${query.toString()}`,
    });
  },

  // ============= MANAGEMENT REVIEWS (7 functions) =============

  /**
   * List management reviews
   * GET /reviews
   */
  async listManagementReviews(params: ListParams): Promise<ManagementReview[]> {
    const query = new URLSearchParams();
    query.set('organization_id', params.organization_id);
    if (params.status) query.set('status', params.status);
    if (params.page !== undefined) query.set('page', String(params.page));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<ManagementReview[]>({
      method: 'GET',
      url: `${API_BASE}/reviews?${query.toString()}`,
    });
  },

  /**
   * Get single review by ID
   * GET /{review_id}
   */
  async getManagementReview(reviewId: string): Promise<ManagementReview> {
    return apiClient.request<ManagementReview>({
      method: 'GET',
      url: `${API_BASE}/${reviewId}`,
    });
  },

  /**
   * Create management review
   * POST /reviews
   */
  async createManagementReview(data: ManagementReviewCreate): Promise<ManagementReview> {
    return apiClient.request<ManagementReview>({
      method: 'POST',
      url: `${API_BASE}/reviews`,
      data,
    });
  },

  /**
   * Start management review
   * POST /{review_id}/start
   */
  async startManagementReview(reviewId: string): Promise<ManagementReview> {
    return apiClient.request<ManagementReview>({
      method: 'POST',
      url: `${API_BASE}/${reviewId}/start`,
    });
  },

  /**
   * Complete management review
   * POST /{review_id}/complete
   */
  async completeManagementReview(reviewId: string): Promise<ManagementReview> {
    return apiClient.request<ManagementReview>({
      method: 'POST',
      url: `${API_BASE}/${reviewId}/complete`,
    });
  },

  /**
   * Get review inputs
   * GET /{review_id}/inputs
   */
  async getReviewInputs(reviewId: string): Promise<ReviewInputs> {
    return apiClient.request<ReviewInputs>({
      method: 'GET',
      url: `${API_BASE}/${reviewId}/inputs`,
    });
  },

  /**
   * Add review decision
   * POST /{review_id}/decisions
   */
  async addReviewDecision(reviewId: string, decision: ReviewDecision): Promise<ManagementReview> {
    return apiClient.request<ManagementReview>({
      method: 'POST',
      url: `${API_BASE}/${reviewId}/decisions`,
      data: decision,
    });
  },

  /**
   * Get review report
   * GET /{review_id}/report
   */
  async getReviewReport(reviewId: string): Promise<any> {
    return apiClient.request<any>({
      method: 'GET',
      url: `${API_BASE}/${reviewId}/report`,
    });
  },

  // ============= IMPROVEMENTS (8 functions) =============

  /**
   * List improvement initiatives
   * GET /improvements
   */
  async listImprovements(params: ListParams): Promise<ImprovementInitiative[]> {
    const query = new URLSearchParams();
    query.set('organization_id', params.organization_id);
    if (params.status) query.set('status', params.status);
    if (params.search) query.set('search', params.search);
    if (params.page !== undefined) query.set('page', String(params.page));
    if (params.limit !== undefined) query.set('limit', String(params.limit));

    return apiClient.request<ImprovementInitiative[]>({
      method: 'GET',
      url: `${API_BASE}/improvements?${query.toString()}`,
    });
  },

  /**
   * Get single improvement by ID
   * GET /improvements/{initiative_id}
   */
  async getImprovement(initiativeId: string): Promise<ImprovementInitiative> {
    return apiClient.request<ImprovementInitiative>({
      method: 'GET',
      url: `${API_BASE}/improvements/${initiativeId}`,
    });
  },

  /**
   * Create improvement initiative
   * POST /improvements
   */
  async createImprovement(data: ImprovementInitiativeCreate): Promise<ImprovementInitiative> {
    return apiClient.request<ImprovementInitiative>({
      method: 'POST',
      url: `${API_BASE}/improvements`,
      data,
    });
  },

  /**
   * Update improvement initiative
   * PATCH /improvements/{initiative_id}
   */
  async updateImprovement(initiativeId: string, data: ImprovementInitiativeUpdate): Promise<ImprovementInitiative> {
    return apiClient.request<ImprovementInitiative>({
      method: 'PATCH',
      url: `${API_BASE}/improvements/${initiativeId}`,
      data,
    });
  },

  /**
   * Update improvement progress
   * PATCH /improvements/{initiative_id}/progress
   */
  async updateImprovementProgress(initiativeId: string, progress: number): Promise<ImprovementInitiative> {
    return apiClient.request<ImprovementInitiative>({
      method: 'PATCH',
      url: `${API_BASE}/improvements/${initiativeId}/progress`,
      data: { progress_percentage: progress },
    });
  },

  /**
   * Verify improvement initiative
   * POST /improvements/{initiative_id}/verify
   */
  async verifyImprovement(initiativeId: string, verificationData: any): Promise<ImprovementInitiative> {
    return apiClient.request<ImprovementInitiative>({
      method: 'POST',
      url: `${API_BASE}/improvements/${initiativeId}/verify`,
      data: verificationData,
    });
  },

  /**
   * Get improvement dashboard
   * GET /improvements/dashboard
   */
  async getImprovementDashboard(organizationId: string): Promise<ImprovementDashboard> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<ImprovementDashboard>({
      method: 'GET',
      url: `${API_BASE}/improvements/dashboard?${query.toString()}`,
    });
  },

  /**
   * Get ROI analysis
   * GET /improvements/roi-analysis
   */
  async getROIAnalysis(organizationId: string): Promise<ROIAnalysis[]> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<ROIAnalysis[]>({
      method: 'GET',
      url: `${API_BASE}/improvements/roi-analysis?${query.toString()}`,
    });
  },

  // ============= TEMPLATES (12 functions) =============

  /**
   * List templates
   * GET /templates
   */
  async listTemplates(category?: TemplateCategory): Promise<ComplianceTemplate[]> {
    const query = new URLSearchParams();
    if (category) query.set('category', category);

    const url = query.toString() ? `${API_BASE}/templates?${query.toString()}` : `${API_BASE}/templates`;
    return apiClient.request<ComplianceTemplate[]>({
      method: 'GET',
      url,
    });
  },

  /**
   * Get single template by ID
   * GET /templates/{template_id}
   */
  async getTemplate(templateId: string): Promise<ComplianceTemplate> {
    return apiClient.request<ComplianceTemplate>({
      method: 'GET',
      url: `${API_BASE}/templates/${templateId}`,
    });
  },

  /**
   * Create template
   * POST /templates
   */
  async createTemplate(data: ComplianceTemplateCreate): Promise<ComplianceTemplate> {
    return apiClient.request<ComplianceTemplate>({
      method: 'POST',
      url: `${API_BASE}/templates`,
      data,
    });
  },

  /**
   * Update template
   * PUT /templates/{template_id}
   */
  async updateTemplate(templateId: string, data: ComplianceTemplateUpdate): Promise<ComplianceTemplate> {
    return apiClient.request<ComplianceTemplate>({
      method: 'PUT',
      url: `${API_BASE}/templates/${templateId}`,
      data,
    });
  },

  /**
   * Delete template
   * DELETE /templates/{template_id}
   */
  async deleteTemplate(templateId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${API_BASE}/templates/${templateId}`,
    });
  },

  /**
   * Render template
   * POST /templates/{template_id}/render
   */
  async renderTemplate(request: TemplateRenderRequest): Promise<TemplateRenderResult> {
    return apiClient.request<TemplateRenderResult>({
      method: 'POST',
      url: `${API_BASE}/templates/${request.template_id}/render`,
      data: { context: request.context },
    });
  },

  /**
   * Verify template
   * POST /templates/{template_id}/verify
   */
  async verifyTemplate(templateId: string): Promise<any> {
    return apiClient.request<any>({
      method: 'POST',
      url: `${API_BASE}/templates/${templateId}/verify`,
    });
  },

  /**
   * Get template usage stats
   * GET /templates/{template_id}/usage-stats
   */
  async getTemplateUsageStats(templateId: string): Promise<any> {
    return apiClient.request<any>({
      method: 'GET',
      url: `${API_BASE}/templates/${templateId}/usage-stats`,
    });
  },

  /**
   * Get templates by category
   * GET /templates/category/{category}
   */
  async getTemplatesByCategory(category: TemplateCategory): Promise<ComplianceTemplate[]> {
    return apiClient.request<ComplianceTemplate[]>({
      method: 'GET',
      url: `${API_BASE}/templates/category/${category}`,
    });
  },

  /**
   * Get templates by ISO clause
   * GET /templates/iso-clause/{clause}
   */
  async getTemplatesByISOClause(clause: string): Promise<ComplianceTemplate[]> {
    return apiClient.request<ComplianceTemplate[]>({
      method: 'GET',
      url: `${API_BASE}/templates/iso-clause/${clause}`,
    });
  },

  /**
   * Get BPMN template
   * GET /templates/bpmn/{workflow_type}
   */
  async getBPMNTemplate(workflowType: string): Promise<BPMNTemplate> {
    return apiClient.request<BPMNTemplate>({
      method: 'GET',
      url: `${API_BASE}/templates/bpmn/${workflowType}`,
    });
  },

  /**
   * Generate template
   * POST /templates/generate
   */
  async generateTemplate(templateData: any): Promise<ComplianceTemplate> {
    return apiClient.request<ComplianceTemplate>({
      method: 'POST',
      url: `${API_BASE}/templates/generate`,
      data: templateData,
    });
  },

  // ============= NONCONFORMITIES (5 functions) =============

  /**
   * Start RCA for nonconformity
   * POST /nonconformities/{nc_id}/rca/start
   */
  async startNonconformityRCA(ncId: string, method: RCAMethod): Promise<any> {
    return apiClient.request<any>({
      method: 'POST',
      url: `${API_BASE}/nonconformities/${ncId}/rca/start`,
      data: { method },
    });
  },

  /**
   * Complete RCA for nonconformity
   * POST /nonconformities/{nc_id}/rca/complete
   */
  async completeNonconformityRCA(ncId: string, rcaData: any): Promise<any> {
    return apiClient.request<any>({
      method: 'POST',
      url: `${API_BASE}/nonconformities/${ncId}/rca/complete`,
      data: rcaData,
    });
  },

  /**
   * Get RCA methods
   * GET /rca/methods
   */
  async getRCAMethods(): Promise<RCAMethod[]> {
    return apiClient.request<RCAMethod[]>({
      method: 'GET',
      url: `${API_BASE}/rca/methods`,
    });
  },

  /**
   * Get RCA template
   * GET /rca/templates/{method}
   */
  async getRCATemplate(method: RCAMethod): Promise<RCATemplate> {
    return apiClient.request<RCATemplate>({
      method: 'GET',
      url: `${API_BASE}/rca/templates/${method}`,
    });
  },

  /**
   * Bulk nonconformity operations
   * POST /nonconformities/bulk
   */
  async bulkNonconformityOperation(request: BulkOperationRequest): Promise<BulkOperationResult> {
    return apiClient.request<BulkOperationResult>({
      method: 'POST',
      url: `${API_BASE}/nonconformities/bulk`,
      data: request,
    });
  },

  // ============= ANALYTICS & DASHBOARD (6 functions) =============

  /**
   * Get compliance overview
   * GET /overview
   */
  async getComplianceOverview(organizationId: string): Promise<DashboardOverview> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<DashboardOverview>({
      method: 'GET',
      url: `${API_BASE}/overview?${query.toString()}`,
    });
  },

  /**
   * Get analytics data
   * GET /analytics
   */
  async getAnalytics(organizationId: string, metricType?: string): Promise<AnalyticsData[]> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);
    if (metricType) query.set('metric_type', metricType);

    return apiClient.request<AnalyticsData[]>({
      method: 'GET',
      url: `${API_BASE}/analytics?${query.toString()}`,
    });
  },

  /**
   * Get requirements matrix
   * GET /requirements-matrix
   */
  async getRequirementsMatrix(organizationId: string, standard?: string): Promise<RequirementsMatrix> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);
    if (standard) query.set('standard', standard);

    return apiClient.request<RequirementsMatrix>({
      method: 'GET',
      url: `${API_BASE}/requirements-matrix?${query.toString()}`,
    });
  },

  /**
   * Get compliance roadmap
   * GET /roadmap
   */
  async getComplianceRoadmap(organizationId: string): Promise<ComplianceRoadmap> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);

    return apiClient.request<ComplianceRoadmap>({
      method: 'GET',
      url: `${API_BASE}/roadmap?${query.toString()}`,
    });
  },

  /**
   * Get AI advice for item
   * GET /{item_id}/ai-advice
   */
  async getAIAdvice(itemId: string, itemType: string): Promise<AIAdvice> {
    const query = new URLSearchParams();
    query.set('item_type', itemType);

    return apiClient.request<AIAdvice>({
      method: 'GET',
      url: `${API_BASE}/${itemId}/ai-advice?${query.toString()}`,
    });
  },

  /**
   * Get benchmarks
   * GET /benchmarks
   */
  async getBenchmarks(organizationId: string, benchmarkType?: string): Promise<BenchmarkData[]> {
    const query = new URLSearchParams();
    query.set('organization_id', organizationId);
    if (benchmarkType) query.set('benchmark_type', benchmarkType);

    return apiClient.request<BenchmarkData[]>({
      method: 'GET',
      url: `${API_BASE}/benchmarks?${query.toString()}`,
    });
  },

  // ============= KNOWLEDGE BASE (8 functions) =============

  /**
   * List compliance standards
   * GET /standards
   */
  async listStandards(): Promise<ComplianceStandard[]> {
    return apiClient.request<ComplianceStandard[]>({
      method: 'GET',
      url: `${API_BASE}/standards`,
    });
  },

  /**
   * Get ISO 22301 clauses
   * GET /iso22301/clauses
   */
  async getISO22301Clauses(): Promise<ISO22301Clause[]> {
    return apiClient.request<ISO22301Clause[]>({
      method: 'GET',
      url: `${API_BASE}/iso22301/clauses`,
    });
  },

  /**
   * Get ISO 22301 clause details
   * GET /iso22301/{clause}
   */
  async getISO22301Clause(clause: string): Promise<ISO22301Clause> {
    return apiClient.request<ISO22301Clause>({
      method: 'GET',
      url: `${API_BASE}/iso22301/${clause}`,
    });
  },

  /**
   * Get BCI practices
   * GET /bci/practices
   */
  async getBCIPractices(): Promise<BCIPractice[]> {
    return apiClient.request<BCIPractice[]>({
      method: 'GET',
      url: `${API_BASE}/bci/practices`,
    });
  },

  /**
   * Get WHO framework
   * GET /who/framework
   */
  async getWHOFramework(): Promise<WHOFramework> {
    return apiClient.request<WHOFramework>({
      method: 'GET',
      url: `${API_BASE}/who/framework`,
    });
  },

  /**
   * Get standard mapping
   * GET /mapping
   */
  async getStandardMapping(sourceStandard: string, targetStandard: string): Promise<MappingData> {
    const query = new URLSearchParams();
    query.set('source', sourceStandard);
    query.set('target', targetStandard);

    return apiClient.request<MappingData>({
      method: 'GET',
      url: `${API_BASE}/mapping?${query.toString()}`,
    });
  },

  /**
   * Search knowledge base
   * GET /search
   */
  async searchKnowledgeBase(searchQuery: string): Promise<any[]> {
    const query = new URLSearchParams();
    query.set('q', searchQuery);

    return apiClient.request<any[]>({
      method: 'GET',
      url: `${API_BASE}/search?${query.toString()}`,
    });
  },

  /**
   * Get library items
   * GET /items
   */
  async getLibraryItems(itemType?: string): Promise<any[]> {
    const query = new URLSearchParams();
    if (itemType) query.set('type', itemType);

    const url = query.toString() ? `${API_BASE}/items?${query.toString()}` : `${API_BASE}/items`;
    return apiClient.request<any[]>({
      method: 'GET',
      url,
    });
  },

  // ============= LIBRARY RESOURCES (4 functions) =============

  /**
   * Get guides
   * GET /guides
   */
  async getGuides(): Promise<LibraryResource[]> {
    return apiClient.request<LibraryResource[]>({
      method: 'GET',
      url: `${API_BASE}/guides`,
    });
  },

  /**
   * Get single guide
   * GET /guides/{guide_id}
   */
  async getGuide(guideId: string): Promise<LibraryResource> {
    return apiClient.request<LibraryResource>({
      method: 'GET',
      url: `${API_BASE}/guides/${guideId}`,
    });
  },

  /**
   * Get best practices
   * GET /best-practices
   */
  async getBestPractices(): Promise<LibraryResource[]> {
    return apiClient.request<LibraryResource[]>({
      method: 'GET',
      url: `${API_BASE}/best-practices`,
    });
  },

  /**
   * Get case studies
   * GET /case-studies
   */
  async getCaseStudies(): Promise<LibraryResource[]> {
    return apiClient.request<LibraryResource[]>({
      method: 'GET',
      url: `${API_BASE}/case-studies`,
    });
  },

  /**
   * Get research
   * GET /research
   */
  async getResearch(): Promise<LibraryResource[]> {
    return apiClient.request<LibraryResource[]>({
      method: 'GET',
      url: `${API_BASE}/research`,
    });
  },

  /**
   * Get research by source
   * GET /research/{source}
   */
  async getResearchBySource(source: string): Promise<LibraryResource[]> {
    return apiClient.request<LibraryResource[]>({
      method: 'GET',
      url: `${API_BASE}/research/${source}`,
    });
  },

  // ============= BULK OPERATIONS (2 functions) =============

  /**
   * Bulk corrective actions operations
   * POST /corrective-actions/bulk
   */
  async bulkCorrectiveActionsOperation(request: BulkOperationRequest): Promise<BulkOperationResult> {
    return apiClient.request<BulkOperationResult>({
      method: 'POST',
      url: `${API_BASE}/corrective-actions/bulk`,
      data: request,
    });
  },

  /**
   * Bulk RCA validation
   * POST /rca/bulk-validate
   */
  async bulkRCAValidation(rcaIds: string[]): Promise<any> {
    return apiClient.request<any>({
      method: 'POST',
      url: `${API_BASE}/rca/bulk-validate`,
      data: { rca_ids: rcaIds },
    });
  },

  // ============= HEALTH & REGISTRY (6 functions) =============

  /**
   * Get health status
   * GET /health
   */
  async getHealthStatus(): Promise<HealthStatus> {
    return apiClient.request<HealthStatus>({
      method: 'GET',
      url: `${API_BASE}/health`,
    });
  },

  /**
   * Get service info
   * GET /health/info
   */
  async getServiceInfo(): Promise<ServiceInfo> {
    return apiClient.request<ServiceInfo>({
      method: 'GET',
      url: `${API_BASE}/health/info`,
    });
  },

  /**
   * Get readiness status
   * GET /health/ready
   */
  async getReadinessStatus(): Promise<any> {
    return apiClient.request<any>({
      method: 'GET',
      url: `${API_BASE}/health/ready`,
    });
  },

  /**
   * Get service health by name
   * GET /health/{service_name}
   */
  async getServiceHealth(serviceName: string): Promise<any> {
    return apiClient.request<any>({
      method: 'GET',
      url: `${API_BASE}/health/${serviceName}`,
    });
  },

  /**
   * Get service registry
   * GET /registry
   */
  async getServiceRegistry(): Promise<ServiceRegistry> {
    return apiClient.request<ServiceRegistry>({
      method: 'GET',
      url: `${API_BASE}/registry`,
    });
  },

  /**
   * Register service
   * POST /registry
   */
  async registerService(serviceData: any): Promise<any> {
    return apiClient.request<any>({
      method: 'POST',
      url: `${API_BASE}/registry`,
      data: serviceData,
    });
  },
};

// ==================== EXPORTED FUNCTIONS ====================

// Assessments
export async function listAssessments(params: ListParams): Promise<ComplianceAssessment[]> {
  return complianceClient.listAssessments(params);
}

export async function getAssessment(assessmentId: string): Promise<ComplianceAssessment> {
  return complianceClient.getAssessment(assessmentId);
}

export async function createAssessment(data: ComplianceAssessmentCreate): Promise<ComplianceAssessment> {
  return complianceClient.createAssessment(data);
}

export async function updateAssessment(assessmentId: string, data: ComplianceAssessmentUpdate): Promise<ComplianceAssessment> {
  return complianceClient.updateAssessment(assessmentId, data);
}

export async function deleteAssessment(assessmentId: string): Promise<void> {
  return complianceClient.deleteAssessment(assessmentId);
}

export async function runAssessment(assessmentId: string): Promise<ComplianceAssessment> {
  return complianceClient.runAssessment(assessmentId);
}

export async function getAssessmentResults(assessmentId: string): Promise<AssessmentResults> {
  return complianceClient.getAssessmentResults(assessmentId);
}

// Gaps
export async function listGaps(params: ListParams): Promise<ComplianceGap[]> {
  return complianceClient.listGaps(params);
}

export async function getGap(gapId: string): Promise<ComplianceGap> {
  return complianceClient.getGap(gapId);
}

export async function createGap(data: ComplianceGapCreate): Promise<ComplianceGap> {
  return complianceClient.createGap(data);
}

export async function updateGap(gapId: string, data: ComplianceGapUpdate): Promise<ComplianceGap> {
  return complianceClient.updateGap(gapId, data);
}

export async function resolveGap(gapId: string, resolutionNotes: string): Promise<ComplianceGap> {
  return complianceClient.resolveGap(gapId, resolutionNotes);
}

export async function reopenGap(gapId: string, reason: string): Promise<ComplianceGap> {
  return complianceClient.reopenGap(gapId, reason);
}

// Evidence
export async function listEvidence(params: ListParams): Promise<ComplianceEvidence[]> {
  return complianceClient.listEvidence(params);
}

export async function getEvidence(evidenceId: string): Promise<ComplianceEvidence> {
  return complianceClient.getEvidence(evidenceId);
}

export async function uploadEvidence(data: ComplianceEvidenceCreate): Promise<ComplianceEvidence> {
  return complianceClient.uploadEvidence(data);
}

export async function updateEvidence(evidenceId: string, data: ComplianceEvidenceUpdate): Promise<ComplianceEvidence> {
  return complianceClient.updateEvidence(evidenceId, data);
}

export async function deleteEvidence(evidenceId: string): Promise<void> {
  return complianceClient.deleteEvidence(evidenceId);
}

export async function transitionEvidence(evidenceId: string, newStatus: EvidenceStatus): Promise<ComplianceEvidence> {
  return complianceClient.transitionEvidence(evidenceId, newStatus);
}

export async function getEvidenceHistory(evidenceId: string): Promise<EvidenceHistory> {
  return complianceClient.getEvidenceHistory(evidenceId);
}

export async function bulkEvidenceOperation(operation: any): Promise<any> {
  return complianceClient.bulkEvidenceOperation(operation);
}

// Audits
export async function listAudits(params: ListParams): Promise<ComplianceAudit[]> {
  return complianceClient.listAudits(params);
}

export async function getAudit(auditId: string): Promise<ComplianceAudit> {
  return complianceClient.getAudit(auditId);
}

export async function createAudit(data: ComplianceAuditCreate): Promise<ComplianceAudit> {
  return complianceClient.createAudit(data);
}

export async function updateAudit(auditId: string, data: ComplianceAuditUpdate): Promise<ComplianceAudit> {
  return complianceClient.updateAudit(auditId, data);
}

export async function startAudit(auditId: string): Promise<ComplianceAudit> {
  return complianceClient.startAudit(auditId);
}

export async function completeAudit(auditId: string): Promise<ComplianceAudit> {
  return complianceClient.completeAudit(auditId);
}

export async function getAuditReport(auditId: string): Promise<AuditReport> {
  return complianceClient.getAuditReport(auditId);
}

export async function deleteAudit(auditId: string): Promise<void> {
  return complianceClient.deleteAudit(auditId);
}

export async function getAuditChecklist(auditId: string): Promise<AuditChecklist> {
  return complianceClient.getAuditChecklist(auditId);
}

export async function getAuditFindings(auditId: string): Promise<any[]> {
  return complianceClient.getAuditFindings(auditId);
}

export async function createAuditFinding(auditId: string, finding: any): Promise<any> {
  return complianceClient.createAuditFinding(auditId, finding);
}

// Management Reviews
export async function listManagementReviews(params: ListParams): Promise<ManagementReview[]> {
  return complianceClient.listManagementReviews(params);
}

export async function getManagementReview(reviewId: string): Promise<ManagementReview> {
  return complianceClient.getManagementReview(reviewId);
}

export async function createManagementReview(data: ManagementReviewCreate): Promise<ManagementReview> {
  return complianceClient.createManagementReview(data);
}

// Improvements
export async function listImprovements(params: ListParams): Promise<ImprovementInitiative[]> {
  return complianceClient.listImprovements(params);
}

export async function getImprovement(initiativeId: string): Promise<ImprovementInitiative> {
  return complianceClient.getImprovement(initiativeId);
}

export async function createImprovement(data: ImprovementInitiativeCreate): Promise<ImprovementInitiative> {
  return complianceClient.createImprovement(data);
}

export async function getImprovementDashboard(organizationId: string): Promise<ImprovementDashboard> {
  return complianceClient.getImprovementDashboard(organizationId);
}

// Templates
export async function listTemplates(category?: TemplateCategory): Promise<ComplianceTemplate[]> {
  return complianceClient.listTemplates(category);
}

export async function getTemplate(templateId: string): Promise<ComplianceTemplate> {
  return complianceClient.getTemplate(templateId);
}

export async function createTemplate(data: ComplianceTemplateCreate): Promise<ComplianceTemplate> {
  return complianceClient.createTemplate(data);
}

export async function renderTemplate(request: TemplateRenderRequest): Promise<TemplateRenderResult> {
  return complianceClient.renderTemplate(request);
}

// Analytics
export async function getComplianceOverview(organizationId: string): Promise<DashboardOverview> {
  return complianceClient.getComplianceOverview(organizationId);
}

export async function getAnalytics(organizationId: string, metricType?: string): Promise<AnalyticsData[]> {
  return complianceClient.getAnalytics(organizationId, metricType);
}

export async function getRequirementsMatrix(organizationId: string, standard?: string): Promise<RequirementsMatrix> {
  return complianceClient.getRequirementsMatrix(organizationId, standard);
}

export async function getComplianceRoadmap(organizationId: string): Promise<ComplianceRoadmap> {
  return complianceClient.getComplianceRoadmap(organizationId);
}

// Knowledge Base
export async function listStandards(): Promise<ComplianceStandard[]> {
  return complianceClient.listStandards();
}

export async function getISO22301Clauses(): Promise<ISO22301Clause[]> {
  return complianceClient.getISO22301Clauses();
}

export async function getBCIPractices(): Promise<BCIPractice[]> {
  return complianceClient.getBCIPractices();
}

export async function searchKnowledgeBase(searchQuery: string): Promise<any[]> {
  return complianceClient.searchKnowledgeBase(searchQuery);
}

// Health
export async function getHealthStatus(): Promise<HealthStatus> {
  return complianceClient.getHealthStatus();
}

// Export default client
export default complianceClient;
