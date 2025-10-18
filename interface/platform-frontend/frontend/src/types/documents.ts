/**
 * Documents Module Types - Generated from backend models
 * Source: /platform_services/documents_service/models/
 * Week 4 Implementation - AI Platform ISO Project
 */

/**
 * Document Type Enumeration
 * Covers all supported document categories in the ISO compliance system
 */
export enum DocumentType {
  POLICY = 'policy',
  PROCEDURE = 'procedure',
  PLAN = 'plan',
  RISK_ASSESSMENT = 'risk_assessment',
  BIA = 'bia',
  EXERCISE_REPORT = 'exercise_report',
  AUDIT_REPORT = 'audit_report',
  MANAGEMENT_REVIEW = 'management_review',
  FORM = 'form',
  TEMPLATE = 'template',
  CHECKLIST = 'checklist',
  CONTACT_LIST = 'contact_list',
  COMMUNICATION = 'communication',
  TRAINING_MATERIAL = 'training_material',
  EVIDENCE = 'evidence',
  CONTRACT = 'contract',
  SOP = 'sop',
  REPORT = 'report',
  PRESENTATION = 'presentation',
  SPREADSHEET = 'spreadsheet',
  OTHER = 'other'
}

/**
 * Document Status Enumeration
 * Represents the lifecycle state of a document
 */
export enum DocumentStatus {
  DRAFT = 'draft',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
  SUPERSEDED = 'superseded',
  OBSOLETE = 'obsolete'
}

/**
 * Document Classification Enumeration
 * Security classification levels for access control
 */
export enum DocumentClassification {
  PUBLIC = 'public',
  INTERNAL = 'internal',
  CONFIDENTIAL = 'confidential',
  RESTRICTED = 'restricted',
  HIGHLY_RESTRICTED = 'highly_restricted'
}

/**
 * Access Action Enumeration
 * All possible audit log actions for document access tracking
 */
export enum AccessAction {
  CREATED = 'created',
  UPDATED = 'updated',
  VIEWED = 'viewed',
  DOWNLOADED = 'downloaded',
  SHARED = 'shared',
  DELETED = 'deleted',
  RESTORED = 'restored',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
  VERSION_CREATED = 'version_created'
}

/**
 * Share Permission Enumeration
 * Permission levels for document sharing
 */
export enum SharePermission {
  VIEW = 'view',
  COMMENT = 'comment',
  EDIT = 'edit',
  ADMIN = 'admin'
}

/**
 * Approval Status Enumeration
 * Status of approval workflow requests
 */
export enum ApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  RECALLED = 'recalled'
}

/**
 * Main Document Interface
 * Represents a complete document entity with all metadata
 */
export interface Document {
  document_id: number;
  tenant_id: string;
  document_code: string;
  title: string;
  description: string | null;
  document_type: DocumentType;
  version: string;
  parent_id: number | null;
  is_latest: boolean;
  status: DocumentStatus;
  classification: DocumentClassification;

  // File properties
  file_name: string;
  file_path: string | null;
  file_size: number | null;
  file_type: string | null;
  mime_type: string | null;
  page_count: number | null;
  word_count: number | null;

  // AI-powered features
  ai_summary: string | null;

  // Ownership and organization
  owner_id: string;
  created_by: string;
  department: string | null;
  process_area: string | null;

  // Control and approval
  is_controlled: boolean;
  requires_approval: boolean;

  // Timestamps
  created_at: string;
  updated_at: string;
  approved_at: string | null;
  published_at: string | null;
  archived_at: string | null;

  // Review and retention
  next_review_date: string | null;
  last_reviewed_at: string | null;
  last_reviewed_by: string | null;
  retention_years: number | null;
  expiration_date: string | null;
  is_permanent: boolean;

  // Metadata and compliance
  tags: string[] | null;
  iso_clauses: string[] | null;
  bci_practices: string[] | null;
  compliance_frameworks: string[] | null;
  custom_metadata: Record<string, any> | null;
}

/**
 * Document Creation Payload
 * Required and optional fields for creating a new document
 */
export interface DocumentCreate {
  tenant_id: string;
  title: string;
  description?: string;
  document_type: DocumentType;
  classification?: DocumentClassification;
  is_controlled?: boolean;
  requires_approval?: boolean;
  owner_id: string;
  department?: string;
  process_area?: string;
  tags?: string[];
  custom_metadata?: Record<string, any>;
}

/**
 * Document Update Payload
 * All fields optional for partial updates
 */
export interface DocumentUpdate {
  title?: string;
  description?: string;
  document_type?: DocumentType;
  classification?: DocumentClassification;
  is_controlled?: boolean;
  requires_approval?: boolean;
  department?: string;
  process_area?: string;
  tags?: string[];
  custom_metadata?: Record<string, any>;
}

/**
 * Document Access Audit Log Entry
 * Tracks all user interactions with documents for compliance
 */
export interface DocumentAccess {
  access_id: number;
  document_id: number;
  user_id: string;
  action_type: AccessAction;
  ip_address: string | null;
  user_agent: string | null;
  location: string | null;
  changes_made: Record<string, any> | null;
  reason: string | null;
  accessed_at: string;
}

/**
 * Document Share Record
 * Manages document sharing permissions and tracking
 */
export interface DocumentShare {
  share_id: number;
  document_id: number;
  shared_by_user_id: string;
  shared_with_user_id: string | null;
  shared_with_email: string | null;
  permission_level: SharePermission;
  can_reshare: boolean;
  is_active: boolean;
  expires_at: string | null;
  shared_at: string;
  accessed_at: string | null;
  last_accessed_at: string | null;
  access_count: number;
  share_message: string | null;
}

/**
 * Share Request Payload
 * Parameters for creating a new document share
 */
export interface ShareRequest {
  shared_with_user_id?: string;
  shared_with_email?: string;
  permission_level?: SharePermission;
  can_reshare?: boolean;
  expires_at?: string;
  share_message?: string;
}

/**
 * Document Approval Workflow Entry
 * Tracks approval requests and responses in multi-stage workflows
 */
export interface DocumentApproval {
  approval_id: number;
  document_id: number;
  approval_stage: number;
  approver_id: string;
  approver_role: string;
  approval_status: ApprovalStatus;
  decision_notes: string | null;
  suggested_changes: any[] | null;
  requested_at: string;
  responded_at: string | null;
  due_date: string | null;
  reminder_sent: boolean;
  reminder_sent_at: string | null;
}

/**
 * Approval Request Payload
 * Parameters for requesting document approval
 */
export interface ApprovalRequest {
  approver_id: string;
  approver_role: string;
  sla_hours?: number;
  notes?: string;
}

/**
 * Approval Response Payload
 * Approver's decision on a document approval request
 */
export interface ApprovalResponse {
  action: 'approve' | 'reject' | 'recall';
  decision_notes?: string;
  suggested_changes?: any[];
}

/**
 * Retention Policy Configuration
 * Defines document retention rules based on type, department, and classification
 */
export interface RetentionPolicy {
  policy_id: number;
  tenant_id: string;
  policy_name: string;
  description: string | null;
  document_type: DocumentType | null;
  department: string | null;
  classification: DocumentClassification | null;
  retention_years: number;
  is_permanent: boolean;
  trigger_type: string;
  archive_after_days: number | null;
  destroy_after_days: number | null;
  require_review_before_destruction: boolean;
  is_active: boolean;
  created_at: string;
  created_by: string;
  updated_at: string;
}

/**
 * Workflow Status Information
 * Provides current state and available actions for a document
 */
export interface WorkflowStatus {
  current_state: DocumentStatus;
  available_actions: string[];
  is_controlled: boolean;
  requires_approval: boolean;
  can_submit_for_review: boolean;
  can_publish: boolean;
  can_archive: boolean;
  approval_summary?: {
    total: number;
    approved: number;
    pending: number;
    rejected: number;
  };
  dates: {
    created_at: string | null;
    updated_at: string | null;
    approved_at: string | null;
    published_at: string | null;
    archived_at: string | null;
  };
}

/**
 * Version Comparison Result
 * AI-powered diff analysis between document versions
 */
export interface VersionComparison {
  comparison_id: number;
  source_document_id: number;
  target_document_id: number;
  similarity_score: number;
  text_added: number;
  text_removed: number;
  text_modified: number;
  diff_json: any;
  changes_summary: string | null;
  sections_added: any[] | null;
  sections_removed: any[] | null;
  sections_modified: any[] | null;
  metadata_changes: Record<string, any> | null;
  compared_at: string;
  processing_time_ms: number;
}
