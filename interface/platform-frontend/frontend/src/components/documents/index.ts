/**
 * Documents Module - Component Exports
 * Week 4 Round 3 - Documents Module
 *
 * This module provides a comprehensive document management system for the AI Platform ISO project.
 * Components are organized by functional area:
 *
 * - Core Components: Basic document display and metadata (Round 3 Agent 8)
 * - Form Components: Document creation and editing workflows (Round 3 Agent 9)
 * - Approval Components: Approval workflow management (Round 3 Agent 10)
 * - Sharing Components: Document sharing and permissions (Round 3 Agent 11)
 * - Version & Audit Components: Version control and audit trails (Round 3 Agent 12)
 * - List & Layout Components: Document browsing and filtering (Round 3 Agent 13)
 */

// ==================== CORE COMPONENTS ====================
// Round 3 Agent 8 - Basic document display components

export { DocumentCard, ClassificationBadge } from './DocumentCard';
export type { DocumentCardProps } from './DocumentCard';

export {
  DocumentStatusBadge,
  getStatusConfig,
  getStatusProgress,
} from './DocumentStatusBadge';
export type { DocumentStatusBadgeProps } from './DocumentStatusBadge';

export {
  DocumentTypeIcon,
  getTypeConfig,
  getTypeCategory,
} from './DocumentTypeIcon';
export type { DocumentTypeIconProps } from './DocumentTypeIcon';

// ==================== FORM COMPONENTS ====================
// Round 3 Agent 9 - Document creation and editing forms

export { DocumentCreateForm } from './forms/DocumentCreateForm';
export { DocumentUploadForm } from './forms/DocumentUploadForm';
export { DocumentMetadataForm } from './forms/DocumentMetadataForm';

// ==================== APPROVAL COMPONENTS ====================
// Round 3 Agent 10 - Approval workflow management

export { ApprovalCard } from './ApprovalCard';
export type { ApprovalCardProps } from './ApprovalCard';

export { ApprovalRequestDialog } from './ApprovalRequestDialog';
export type { ApprovalRequestDialogProps } from './ApprovalRequestDialog';

export { WorkflowTimeline } from './WorkflowTimeline';
export type { WorkflowTimelineProps } from './WorkflowTimeline';

// ==================== SHARING COMPONENTS ====================
// Round 3 Agent 11 - Document sharing and permissions

export { PermissionBadge } from './PermissionBadge';
export type { PermissionBadgeProps } from './PermissionBadge';
export {
  getPermissionDescription,
  getPermissionOrder,
  isHigherPermission,
} from './PermissionBadge';

export { ShareDialog } from './ShareDialog';
export type { ShareDialogProps } from './ShareDialog';

export { SharesList } from './SharesList';
export type { SharesListProps } from './SharesList';

// ==================== VERSION & AUDIT COMPONENTS ====================
// Round 3 Agent 12 - Version control and audit trails

export { default as VersionHistory } from './VersionHistory';
export { default as RetentionInfo } from './RetentionInfo';
export { default as DocumentTimeline } from './DocumentTimeline';

// ==================== LIST & LAYOUT COMPONENTS ====================
// Round 3 Agent 13 - Document browsing and filtering

export { DocumentList } from './DocumentList';
export type { DocumentListProps, FilterState, SortOption } from './DocumentList';

export { DocumentTable } from './DocumentTable';
export type { DocumentTableProps } from './DocumentTable';

export { DocumentFilters } from './DocumentFilters';
export type { DocumentFiltersProps } from './DocumentFilters';

// ==================== TYPE EXPORTS ====================
// Re-export common types for convenience

export type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentType,
  DocumentStatus,
  DocumentClassification,
  DocumentAccess,
  DocumentShare,
  SharePermission,
  DocumentApproval,
  ApprovalStatus,
  RetentionPolicy,
  WorkflowStatus,
} from '@/types/documents';
