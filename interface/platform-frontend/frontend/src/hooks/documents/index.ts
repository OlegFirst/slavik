/**
 * Documents Hooks - Index
 * Central export point for all document-related React Query hooks
 * Week 4 - Documents Module
 */

// List hooks
export {
  useDocuments,
  useDraftDocuments,
  usePublishedDocuments,
  useArchivedDocuments,
  useDocumentsUnderReview,
  prefetchDocuments,
  documentsQueryKeys,
  type UseDocumentsParams,
  type UseDocumentsOptions,
  type DocumentsResponse,
} from './useDocuments';

// Single document hooks
export {
  useDocument,
  prefetchDocument,
  type UseDocumentParams,
  type UseDocumentOptions,
} from './useDocument';

// Create hooks
export {
  useCreateDocument,
  useUploadFile,
  useCreateDocumentWithFile,
  type UseCreateDocumentOptions,
  type UseUploadFileOptions,
  type UploadFileParams,
} from './useCreateDocument';

// Update hooks
export {
  useUpdateDocument,
  useUpdateDocumentOptimistic,
  type UseUpdateDocumentOptions,
  type UpdateDocumentParams,
} from './useUpdateDocument';

// Delete hooks
export {
  useDeleteDocument,
  useBulkDeleteDocuments,
  type UseDeleteDocumentOptions,
  type DeleteDocumentParams,
} from './useDeleteDocument';

// Workflow hooks
export {
  useWorkflowStatus,
  useExecuteWorkflowAction,
  type UseWorkflowStatusOptions,
  type UseExecuteWorkflowActionOptions,
  type ExecuteWorkflowActionParams,
} from './useDocumentWorkflow';

// Version control hooks
export {
  useDocumentVersions,
  useCreateVersion,
  useCompareVersions,
  type UseDocumentVersionsOptions,
  type UseCreateVersionOptions,
  type UseCompareVersionsOptions,
  type CompareVersionsParams,
} from './useDocumentVersions';

// Approval workflow hooks
export {
  useDocumentApprovals,
  useRequestApproval,
  useRespondToApproval,
  approvalQueryKeys,
  type UseDocumentApprovalsOptions,
  type UseRequestApprovalOptions,
  type UseRespondToApprovalOptions,
  type ApprovalProgress,
} from './useDocumentApprovals';

// Approval helper functions
export {
  getPendingApprovals,
  getApprovedApprovals,
  getRejectedApprovals,
  getOverdueApprovals,
  getApprovalProgress,
  areAllApprovalsComplete,
  canPublishDocument,
  getApprovalSummary,
} from './useDocumentApprovals';

// Sharing hooks
export {
  useDocumentShares,
  useShareDocument,
  useRevokeShare,
  shareQueryKeys,
  type UseDocumentSharesOptions,
  type UseShareDocumentOptions,
  type SharesByPermission,
} from './useDocumentSharing';

// Sharing helper functions
export {
  getActiveShares,
  getExpiredShares,
  getExpiringSoonShares,
  groupSharesByPermission,
  getPermissionLabel,
  getPermissionIcon,
  isShareExpiringSoon,
  getShareRecipient,
} from './useDocumentSharing';

// ==================== RETENTION & AUDIT HOOKS ====================
// Week 4 Round 2 - Active exports

// Retention policies
export {
  useRetentionPolicies,
  useCreateRetentionPolicy,
  useDocumentRetentionStatus,
  retentionQueryKeys,
} from './useRetentionPolicies';

export type {
  UseRetentionPoliciesOptions,
  UseCreateRetentionPolicyOptions,
  UseDocumentRetentionStatusOptions,
  RetentionPolicyCreate,
  RetentionStatus,
} from './useRetentionPolicies';

// Retention helper functions
export {
  getApplicablePolicy,
  calculateRetentionDate,
  isRetentionExpired,
  getDaysUntilRetentionAction,
  formatRetentionPeriod,
  getRetentionStatusLabel,
} from './useRetentionPolicies';

// Audit log
export {
  useDocumentAccessLog,
  auditQueryKeys,
} from './useDocumentAudit';

export type {
  UseDocumentAccessLogOptions,
  AccessLogFilters,
  AccessLogResponse,
  GroupedByAction,
  GroupedByUser,
  ActionSummary,
} from './useDocumentAudit';

// Audit helper functions
export {
  groupByAction,
  groupByUser,
  getRecentAccess,
  getUniqueUsers,
  getActionSummary,
  filterByActionType,
  getMostRecentAccessPerUser,
  getAccessStatistics,
  formatTimeSince,
} from './useDocumentAudit';
