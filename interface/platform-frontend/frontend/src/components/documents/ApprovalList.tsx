/**
 * ApprovalList Component
 * Displays all approvals for a document with stage indicators and response actions
 * Week 4 - Documents Module
 */

'use client';

import { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  Clock,
  MessageSquare,
  Users,
  Filter,
  ChevronRight,
  User,
  Calendar,
} from 'lucide-react';
import {
  useDocumentApprovals,
  useRespondToApproval,
  getApprovalProgress,
} from '@/hooks/documents/useDocumentApprovals';
import { ApprovalStatus } from '@/types/documents';
import type { DocumentApproval } from '@/types/documents';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

export interface ApprovalListProps {
  documentId: string;
  canRespond?: boolean;
}

type FilterStatus = 'all' | ApprovalStatus;

interface ResponseDialogState {
  isOpen: boolean;
  approval: DocumentApproval | null;
  action: 'approve' | 'reject' | null;
  comment: string;
}

const STATUS_CONFIG = {
  [ApprovalStatus.PENDING]: {
    label: 'Pending',
    Icon: Clock,
    bgClass: 'bg-orange-100',
    textClass: 'text-orange-700',
    borderClass: 'border-orange-300',
    dotClass: 'bg-orange-500',
  },
  [ApprovalStatus.APPROVED]: {
    label: 'Approved',
    Icon: CheckCircle2,
    bgClass: 'bg-green-100',
    textClass: 'text-green-700',
    borderClass: 'border-green-300',
    dotClass: 'bg-green-500',
  },
  [ApprovalStatus.REJECTED]: {
    label: 'Rejected',
    Icon: XCircle,
    bgClass: 'bg-red-100',
    textClass: 'text-red-700',
    borderClass: 'border-red-300',
    dotClass: 'bg-red-500',
  },
  [ApprovalStatus.RECALLED]: {
    label: 'Recalled',
    Icon: XCircle,
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-700',
    borderClass: 'border-gray-300',
    dotClass: 'bg-gray-500',
  },
};

/**
 * ApprovalList displays all approvals for a document
 * Shows approval stages, status, and allows approvers to respond
 *
 * @param documentId - The document ID to display approvals for
 * @param canRespond - Whether the current user can respond to approvals
 */
export function ApprovalList({
  documentId,
  canRespond = false,
}: ApprovalListProps) {
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [responseDialog, setResponseDialog] = useState<ResponseDialogState>({
    isOpen: false,
    approval: null,
    action: null,
    comment: '',
  });

  const { data: approvals, isLoading, error } = useDocumentApprovals(parseInt(documentId));

  const progress = approvals ? getApprovalProgress(approvals) : null;

  const filteredApprovals = approvals?.filter((approval) => {
    if (filterStatus === 'all') return true;
    return approval.approval_status === filterStatus;
  });

  const handleOpenResponseDialog = (
    approval: DocumentApproval,
    action: 'approve' | 'reject'
  ) => {
    setResponseDialog({
      isOpen: true,
      approval,
      action,
      comment: '',
    });
  };

  const handleCloseResponseDialog = () => {
    setResponseDialog({
      isOpen: false,
      approval: null,
      action: null,
      comment: '',
    });
  };

  const respondToApproval = useRespondToApproval(
    responseDialog.approval?.approval_id || 0,
    {
      onSuccess: (data) => {
        const actionLabel = data.approval_status === ApprovalStatus.APPROVED ? 'approved' : 'rejected';
        toast.success(`Document ${actionLabel} successfully`);
        handleCloseResponseDialog();
      },
      onError: (error) => {
        toast.error(`Failed to respond: ${error.message}`);
      },
    }
  );

  const handleSubmitResponse = async () => {
    if (!responseDialog.approval || !responseDialog.action) return;

    try {
      await respondToApproval.mutateAsync({
        action: responseDialog.action,
        decision_notes: responseDialog.comment || undefined,
      });
    } catch (error) {
      // Error handled by mutation callbacks
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin" />
          <span className="ml-3 text-gray-600">Loading approvals...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-red-200 p-8">
        <div className="flex items-center gap-2 text-red-700">
          <XCircle className="w-5 h-5" />
          <span>Failed to load approvals: {error.message}</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-amber-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-orange-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                Approval History
              </h2>
            </div>
            {progress && progress.total > 0 && (
              <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-600">
                  {progress.approved}/{progress.total} approved
                </span>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {progress && progress.total > 0 && (
            <div className="mt-3">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-500 to-amber-500 transition-all duration-500"
                  style={{ width: `${progress.completionRate}%` }}
                />
              </div>
              <div className="flex items-center justify-between mt-2 text-xs text-gray-600">
                <span>{progress.completionRate.toFixed(0)}% complete</span>
                <span>{progress.pending} pending</span>
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex gap-2">
              <button
                onClick={() => setFilterStatus('all')}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-medium transition-colors',
                  filterStatus === 'all'
                    ? 'bg-orange-100 text-orange-700 border border-orange-300'
                    : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'
                )}
              >
                All ({approvals?.length || 0})
              </button>
              <button
                onClick={() => setFilterStatus(ApprovalStatus.PENDING)}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-medium transition-colors',
                  filterStatus === ApprovalStatus.PENDING
                    ? 'bg-orange-100 text-orange-700 border border-orange-300'
                    : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'
                )}
              >
                Pending ({progress?.pending || 0})
              </button>
              <button
                onClick={() => setFilterStatus(ApprovalStatus.APPROVED)}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-medium transition-colors',
                  filterStatus === ApprovalStatus.APPROVED
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'
                )}
              >
                Approved ({progress?.approved || 0})
              </button>
              <button
                onClick={() => setFilterStatus(ApprovalStatus.REJECTED)}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-medium transition-colors',
                  filterStatus === ApprovalStatus.REJECTED
                    ? 'bg-red-100 text-red-700 border border-red-300'
                    : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'
                )}
              >
                Rejected ({progress?.rejected || 0})
              </button>
            </div>
          </div>
        </div>

        {/* Approvals List */}
        <div className="divide-y divide-gray-200">
          {!filteredApprovals || filteredApprovals.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">
                {filterStatus === 'all'
                  ? 'No approvals yet'
                  : `No ${filterStatus} approvals`}
              </p>
            </div>
          ) : (
            filteredApprovals.map((approval) => {
              const config = STATUS_CONFIG[approval.approval_status];
              const StatusIcon = config.Icon;
              const isPending = approval.approval_status === ApprovalStatus.PENDING;

              return (
                <div
                  key={approval.approval_id}
                  className="px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Left Side: Approval Info */}
                    <div className="flex-1 min-w-0">
                      {/* Stage & Status */}
                      <div className="flex items-center gap-3 mb-2">
                        <div className="flex items-center gap-2">
                          <div className={cn('w-2 h-2 rounded-full', config.dotClass)} />
                          <span className="text-sm font-medium text-gray-500">
                            Stage {approval.approval_stage}
                          </span>
                        </div>
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                        <span
                          className={cn(
                            'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border',
                            config.bgClass,
                            config.textClass,
                            config.borderClass
                          )}
                        >
                          <StatusIcon className="w-3 h-3" />
                          {config.label}
                        </span>
                      </div>

                      {/* Approver Info */}
                      <div className="flex items-center gap-4 mb-2">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">
                            {approval.approver_id}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <span>•</span>
                          <span>{approval.approver_role}</span>
                        </div>
                      </div>

                      {/* Timestamps */}
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>
                            Requested {formatDistanceToNow(new Date(approval.requested_at), { addSuffix: true })}
                          </span>
                        </div>
                        {approval.responded_at && (
                          <div className="flex items-center gap-1">
                            <span>•</span>
                            <span>
                              Responded {formatDistanceToNow(new Date(approval.responded_at), { addSuffix: true })}
                            </span>
                          </div>
                        )}
                        {approval.due_date && isPending && (
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span>
                              Due {formatDistanceToNow(new Date(approval.due_date), { addSuffix: true })}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Decision Notes */}
                      {approval.decision_notes && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <div className="flex items-start gap-2">
                            <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-gray-700">{approval.decision_notes}</p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Right Side: Actions */}
                    {canRespond && isPending && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleOpenResponseDialog(approval, 'approve')}
                          className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleOpenResponseDialog(approval, 'reject')}
                          className="flex items-center gap-1 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                        >
                          <XCircle className="w-4 h-4" />
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Response Dialog */}
      {responseDialog.isOpen && responseDialog.approval && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={handleCloseResponseDialog}
        >
          <div
            className="relative w-full max-w-lg bg-white rounded-xl shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Dialog Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {responseDialog.action === 'approve' ? 'Approve Document' : 'Reject Document'}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Provide feedback for the document owner
              </p>
            </div>

            {/* Dialog Body */}
            <div className="px-6 py-4">
              <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-2">
                Comments {responseDialog.action === 'reject' && <span className="text-red-500">*</span>}
              </label>
              <textarea
                id="comment"
                value={responseDialog.comment}
                onChange={(e) =>
                  setResponseDialog({ ...responseDialog, comment: e.target.value })
                }
                placeholder={
                  responseDialog.action === 'approve'
                    ? 'Add any feedback or notes (optional)...'
                    : 'Please explain why you are rejecting this document...'
                }
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm resize-none"
                required={responseDialog.action === 'reject'}
              />
            </div>

            {/* Dialog Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-2">
              <button
                onClick={handleCloseResponseDialog}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitResponse}
                disabled={
                  respondToApproval.isPending ||
                  (responseDialog.action === 'reject' && !responseDialog.comment.trim())
                }
                className={cn(
                  'flex items-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors',
                  responseDialog.action === 'approve'
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-red-600 hover:bg-red-700',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {respondToApproval.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Submitting...</span>
                  </>
                ) : (
                  <>
                    {responseDialog.action === 'approve' ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Approve</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-4 h-4" />
                        <span>Reject</span>
                      </>
                    )}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
