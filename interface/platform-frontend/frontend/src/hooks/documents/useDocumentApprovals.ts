/**
 * useDocumentApprovals Hook
 * React Query hooks for multi-stage approval workflow
 * Real API integration via documentsAPI.{getApprovals, requestApproval, respondToApproval}
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type {
  DocumentApproval,
  ApprovalRequest,
  ApprovalResponse,
} from '@/lib/api/documents-client';
import { ApprovalStatus } from '@/types/documents';

// ==================== QUERY KEYS ====================

export const approvalQueryKeys = {
  all: (documentId: number) => ['documents', documentId, 'approvals'] as const,
  detail: (approvalId: number) => ['documents', 'approval', approvalId] as const,
};

// ==================== TYPES ====================

export interface UseDocumentApprovalsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface UseRequestApprovalOptions {
  onSuccess?: (data: DocumentApproval) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UseRespondToApprovalOptions {
  onSuccess?: (data: DocumentApproval) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface ApprovalProgress {
  total: number;
  approved: number;
  pending: number;
  rejected: number;
  deferred: number;
  completionRate: number;
}

// ==================== MAIN HOOKS ====================

/**
 * Hook to fetch all approvals for a document
 * Retrieves the complete approval workflow history and current state
 *
 * @param documentId - Document ID to fetch approvals for
 * @param options - React Query options
 * @returns Query result with approvals data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: approvals, isLoading, error } = useDocumentApprovals(123, {
 *   staleTime: 30000, // 30 seconds
 *   enabled: isApprovalTabActive
 * });
 *
 * const progress = getApprovalProgress(approvals || []);
 * const pending = getPendingApprovals(approvals || []);
 * ```
 */
export function useDocumentApprovals(
  documentId: number,
  options: UseDocumentApprovalsOptions = {}
) {
  return useQuery({
    queryKey: approvalQueryKeys.all(documentId),
    queryFn: () => documentsAPI.getApprovals(documentId),

    // Default caching strategy
    staleTime: options.staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: options.gcTime ?? 5 * 60 * 1000, // 5 minutes

    // Control refetching
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? true,

    // Enable/disable query
    enabled: options.enabled ?? true,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to request approval from user/role
 * Creates a new approval request with optional SLA deadline
 *
 * @param documentId - Document ID to request approval for
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const requestApproval = useRequestApproval(123, {
 *   onSuccess: (approval) => {
 *     toast.success(`Approval requested from ${approval.approver_id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to request approval: ${error.message}`);
 *   }
 * });
 *
 * // Request approval with 24-hour SLA
 * requestApproval.mutate({
 *   approver_id: 'user-456',
 *   approver_role: 'Quality Manager',
 *   sla_hours: 24,
 *   notes: 'Please review updated safety procedures'
 * });
 * ```
 */
export function useRequestApproval(
  documentId: number,
  options: UseRequestApprovalOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (approvalData: ApprovalRequest) =>
      documentsAPI.requestApproval(documentId, approvalData),

    onSuccess: (data) => {
      // Invalidate approval list for this document
      queryClient.invalidateQueries({
        queryKey: approvalQueryKeys.all(documentId),
      });

      // Invalidate document detail (may affect status/metadata)
      queryClient.invalidateQueries({
        queryKey: ['documents', documentId],
      });

      // Invalidate workflow status
      queryClient.invalidateQueries({
        queryKey: ['documents', documentId, 'workflow'],
      });

      // Optimistically set the approval detail cache
      queryClient.setQueryData(
        approvalQueryKeys.detail(data.approval_id),
        data
      );

      // Call user callback
      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

/**
 * Hook to respond to an approval request (approve/reject/recall)
 * Updates approval status and triggers workflow actions
 *
 * @param approvalId - Approval ID to respond to
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const respondToApproval = useRespondToApproval(456, {
 *   onSuccess: (approval) => {
 *     if (approval.approval_status === 'approved') {
 *       toast.success('Document approved successfully');
 *     }
 *   }
 * });
 *
 * // Approve
 * respondToApproval.mutate({
 *   action: 'approve',
 *   decision_notes: 'Reviewed and approved - complies with ISO 22301',
 * });
 *
 * // Reject with suggestions
 * respondToApproval.mutate({
 *   action: 'reject',
 *   decision_notes: 'Requires revision',
 *   suggested_changes: [
 *     { section: '4.2', issue: 'Missing risk assessment reference' }
 *   ]
 * });
 *
 * // Recall (withdraw request)
 * respondToApproval.mutate({
 *   action: 'recall',
 *   decision_notes: 'Document needs major revision before approval'
 * });
 * ```
 */
export function useRespondToApproval(
  approvalId: number,
  options: UseRespondToApprovalOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (response: ApprovalResponse) =>
      documentsAPI.respondToApproval(approvalId, response),

    onSuccess: (data) => {
      // Invalidate approval list for this document
      queryClient.invalidateQueries({
        queryKey: approvalQueryKeys.all(data.document_id),
      });

      // Invalidate the specific approval detail
      queryClient.invalidateQueries({
        queryKey: approvalQueryKeys.detail(approvalId),
      });

      // Invalidate document detail (status may have changed)
      queryClient.invalidateQueries({
        queryKey: ['documents', data.document_id],
      });

      // Invalidate workflow status (available actions may have changed)
      queryClient.invalidateQueries({
        queryKey: ['documents', data.document_id, 'workflow'],
      });

      // Invalidate document list (if filtering by approval status)
      queryClient.invalidateQueries({
        queryKey: ['documents', 'list'],
      });

      // Call user callback
      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Filter approvals to get only pending ones
 * Useful for displaying "awaiting approval" lists
 *
 * @param approvals - Array of document approvals
 * @returns Filtered array of pending approvals
 *
 * @example
 * ```tsx
 * const { data: approvals } = useDocumentApprovals(123);
 * const pending = getPendingApprovals(approvals || []);
 *
 * return (
 *   <div>
 *     <h3>Pending Approvals ({pending.length})</h3>
 *     {pending.map(approval => (
 *       <ApprovalCard key={approval.approval_id} approval={approval} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function getPendingApprovals(
  approvals: DocumentApproval[]
): DocumentApproval[] {
  return approvals.filter(
    (approval) => approval.approval_status === ApprovalStatus.PENDING
  );
}

/**
 * Filter approvals to get approved ones
 *
 * @param approvals - Array of document approvals
 * @returns Filtered array of approved approvals
 */
export function getApprovedApprovals(
  approvals: DocumentApproval[]
): DocumentApproval[] {
  return approvals.filter(
    (approval) => approval.approval_status === ApprovalStatus.APPROVED
  );
}

/**
 * Filter approvals to get rejected ones
 *
 * @param approvals - Array of document approvals
 * @returns Filtered array of rejected approvals
 */
export function getRejectedApprovals(
  approvals: DocumentApproval[]
): DocumentApproval[] {
  return approvals.filter(
    (approval) => approval.approval_status === ApprovalStatus.REJECTED
  );
}

/**
 * Filter approvals to get overdue ones (past due_date)
 *
 * @param approvals - Array of document approvals
 * @returns Filtered array of overdue pending approvals
 */
export function getOverdueApprovals(
  approvals: DocumentApproval[]
): DocumentApproval[] {
  const now = new Date();

  return approvals.filter(
    (approval) =>
      approval.approval_status === ApprovalStatus.PENDING &&
      approval.due_date &&
      new Date(approval.due_date) < now
  );
}

/**
 * Calculate approval progress statistics
 * Returns comprehensive metrics about the approval workflow state
 *
 * @param approvals - Array of document approvals
 * @returns Progress metrics including total, approved, pending, rejected, and completion rate
 *
 * @example
 * ```tsx
 * const { data: approvals } = useDocumentApprovals(123);
 * const progress = getApprovalProgress(approvals || []);
 *
 * return (
 *   <div>
 *     <ProgressBar
 *       value={progress.completionRate}
 *       label={`${progress.approved}/${progress.total} approved`}
 *     />
 *     <Stats>
 *       <Stat label="Approved" value={progress.approved} color="green" />
 *       <Stat label="Pending" value={progress.pending} color="yellow" />
 *       <Stat label="Rejected" value={progress.rejected} color="red" />
 *     </Stats>
 *   </div>
 * );
 * ```
 */
export function getApprovalProgress(
  approvals: DocumentApproval[]
): ApprovalProgress {
  const total = approvals.length;
  const approved = approvals.filter((a) => a.approval_status === ApprovalStatus.APPROVED).length;
  const pending = approvals.filter((a) => a.approval_status === ApprovalStatus.PENDING).length;
  const rejected = approvals.filter((a) => a.approval_status === ApprovalStatus.REJECTED).length;
  const deferred = approvals.filter((a) => a.approval_status === ApprovalStatus.RECALLED).length;

  const completionRate = total > 0 ? (approved / total) * 100 : 0;

  return {
    total,
    approved,
    pending,
    rejected,
    deferred,
    completionRate,
  };
}

/**
 * Check if all approvals are complete (no pending)
 *
 * @param approvals - Array of document approvals
 * @returns True if all approvals are approved, rejected, or deferred (none pending)
 */
export function areAllApprovalsComplete(
  approvals: DocumentApproval[]
): boolean {
  return approvals.every(
    (approval) =>
      approval.approval_status === ApprovalStatus.APPROVED ||
      approval.approval_status === ApprovalStatus.REJECTED ||
      approval.approval_status === ApprovalStatus.RECALLED
  );
}

/**
 * Check if document can be published (all required approvals approved)
 *
 * @param approvals - Array of document approvals
 * @returns True if document has no pending approvals and no rejections
 */
export function canPublishDocument(
  approvals: DocumentApproval[]
): boolean {
  const hasRejections = approvals.some(
    (approval) => approval.approval_status === ApprovalStatus.REJECTED
  );
  const hasPending = approvals.some(
    (approval) => approval.approval_status === ApprovalStatus.PENDING
  );

  return !hasRejections && !hasPending && approvals.length > 0;
}

/**
 * Get approval status summary as human-readable string
 *
 * @param approvals - Array of document approvals
 * @returns Human-readable summary (e.g., "2/3 approved, 1 pending")
 */
export function getApprovalSummary(approvals: DocumentApproval[]): string {
  const progress = getApprovalProgress(approvals);

  if (progress.total === 0) {
    return 'No approvals';
  }

  const parts: string[] = [];

  if (progress.approved > 0) {
    parts.push(`${progress.approved}/${progress.total} approved`);
  }

  if (progress.pending > 0) {
    parts.push(`${progress.pending} pending`);
  }

  if (progress.rejected > 0) {
    parts.push(`${progress.rejected} rejected`);
  }

  if (progress.deferred > 0) {
    parts.push(`${progress.deferred} deferred`);
  }

  return parts.join(', ');
}
