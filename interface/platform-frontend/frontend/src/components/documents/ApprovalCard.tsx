/**
 * ApprovalCard Component
 * Card showing single approval request status
 * Week 4 - Documents Module - Agent 10
 */

'use client';

import { useState } from 'react';
import { formatDistanceToNow, format, isPast } from 'date-fns';
import {
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  User,
  Calendar,
  FileText,
} from 'lucide-react';
import type { DocumentApproval } from '@/types/documents';
import { ApprovalStatus } from '@/types/documents';
import { useRespondToApproval } from '@/hooks/documents';
import toast from 'react-hot-toast';

export interface ApprovalCardProps {
  approval: DocumentApproval;
  currentUserId?: string;
  onApprovalUpdate?: () => void;
  showActions?: boolean;
}

/**
 * Get status badge configuration
 */
function getStatusConfig(status: ApprovalStatus) {
  const configs = {
    [ApprovalStatus.PENDING]: {
      label: 'Pending',
      icon: Clock,
      bgClass: 'bg-yellow-50',
      textClass: 'text-yellow-800',
      borderClass: 'border-yellow-200',
      iconClass: 'text-yellow-600',
    },
    [ApprovalStatus.APPROVED]: {
      label: 'Approved',
      icon: CheckCircle2,
      bgClass: 'bg-green-50',
      textClass: 'text-green-800',
      borderClass: 'border-green-200',
      iconClass: 'text-green-600',
    },
    [ApprovalStatus.REJECTED]: {
      label: 'Rejected',
      icon: XCircle,
      bgClass: 'bg-red-50',
      textClass: 'text-red-800',
      borderClass: 'border-red-200',
      iconClass: 'text-red-600',
    },
    [ApprovalStatus.RECALLED]: {
      label: 'Recalled',
      icon: AlertCircle,
      bgClass: 'bg-gray-50',
      textClass: 'text-gray-800',
      borderClass: 'border-gray-200',
      iconClass: 'text-gray-600',
    },
  };
  return configs[status];
}

/**
 * Calculate time remaining or overdue status
 */
function getTimeStatus(dueDate: string | null) {
  if (!dueDate) return null;

  const due = new Date(dueDate);
  const now = new Date();
  const isOverdue = isPast(due);
  const timeDistance = formatDistanceToNow(due, { addSuffix: true });

  return { isOverdue, timeDistance, dueDate: due };
}

export function ApprovalCard({
  approval,
  currentUserId,
  onApprovalUpdate,
  showActions = true,
}: ApprovalCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [decisionNotes, setDecisionNotes] = useState('');

  const statusConfig = getStatusConfig(approval.approval_status);
  const timeStatus = getTimeStatus(approval.due_date);
  const isCurrentApprover = currentUserId === approval.approver_id;
  const canRespond =
    approval.approval_status === ApprovalStatus.PENDING &&
    isCurrentApprover &&
    showActions;

  const StatusIcon = statusConfig.icon;

  // Hook for responding to approval
  const respondToApproval = useRespondToApproval(approval.approval_id, {
    onSuccess: (data) => {
      const action = data.approval_status === ApprovalStatus.APPROVED ? 'approved' : 'rejected';
      toast.success(`Approval ${action} successfully`);
      onApprovalUpdate?.();
      setDecisionNotes('');
    },
    onError: (error) => {
      toast.error(`Failed to respond: ${error.message}`);
    },
  });

  const handleApprove = () => {
    respondToApproval.mutate({
      action: 'approve',
      decision_notes: decisionNotes || undefined,
    });
  };

  const handleReject = () => {
    if (!decisionNotes.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }
    respondToApproval.mutate({
      action: 'reject',
      decision_notes: decisionNotes,
    });
  };

  return (
    <div
      className={`
        rounded-lg border p-4 transition-all
        ${statusConfig.borderClass} ${statusConfig.bgClass}
        hover:shadow-md
      `}
      role="article"
      aria-label={`Approval request for ${approval.approver_role}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          {/* Approver Info */}
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gray-500" />
            <div>
              <p className="font-medium text-gray-900">{approval.approver_role}</p>
              <p className="text-sm text-gray-500">Stage {approval.approval_stage}</p>
            </div>
          </div>

          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <span
              className={`
                inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium border
                ${statusConfig.bgClass} ${statusConfig.textClass} ${statusConfig.borderClass}
              `}
            >
              <StatusIcon className={`h-4 w-4 ${statusConfig.iconClass}`} />
              {statusConfig.label}
            </span>
          </div>
        </div>

        {/* Expand Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="rounded-md p-1 hover:bg-gray-100 transition-colors"
          aria-expanded={expanded}
          aria-label={expanded ? 'Collapse details' : 'Expand details'}
        >
          {expanded ? (
            <ChevronUp className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          )}
        </button>
      </div>

      {/* Dates and SLA */}
      <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-600">
        <div className="flex items-center gap-1.5">
          <Calendar className="h-4 w-4" />
          <span>Requested {formatDistanceToNow(new Date(approval.requested_at), { addSuffix: true })}</span>
        </div>

        {timeStatus && (
          <div className={`flex items-center gap-1.5 ${timeStatus.isOverdue ? 'text-red-600 font-medium' : ''}`}>
            <Clock className="h-4 w-4" />
            <span>
              {timeStatus.isOverdue ? 'Overdue ' : 'Due '}
              {timeStatus.timeDistance}
            </span>
          </div>
        )}
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-4 space-y-3 border-t pt-4">
          {/* Response Date */}
          {approval.responded_at && (
            <div className="text-sm text-gray-600">
              <strong>Responded:</strong> {format(new Date(approval.responded_at), 'PPpp')}
            </div>
          )}

          {/* Decision Notes */}
          {approval.decision_notes && (
            <div className="rounded-md bg-white p-3 border">
              <div className="flex items-start gap-2">
                <FileText className="h-4 w-4 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-700">Decision Notes</p>
                  <p className="mt-1 text-sm text-gray-600">{approval.decision_notes}</p>
                </div>
              </div>
            </div>
          )}

          {/* Suggested Changes */}
          {approval.suggested_changes && approval.suggested_changes.length > 0 && (
            <div className="rounded-md bg-white p-3 border">
              <p className="text-sm font-medium text-gray-700 mb-2">Suggested Changes</p>
              <ul className="space-y-1 text-sm text-gray-600">
                {approval.suggested_changes.map((change: any, index: number) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-gray-400">•</span>
                    <span>{typeof change === 'string' ? change : change.description || JSON.stringify(change)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons (for pending approvals) */}
      {canRespond && (
        <div className="mt-4 space-y-3 border-t pt-4">
          <div>
            <label htmlFor={`notes-${approval.approval_id}`} className="block text-sm font-medium text-gray-700 mb-1">
              Decision Notes {approval.approval_status === ApprovalStatus.PENDING && <span className="text-red-500">*</span>}
            </label>
            <textarea
              id={`notes-${approval.approval_id}`}
              value={decisionNotes}
              onChange={(e) => setDecisionNotes(e.target.value)}
              placeholder="Add notes about your decision..."
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              disabled={respondToApproval.isPending}
              className="flex-1 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Approve document"
            >
              {respondToApproval.isPending ? 'Processing...' : 'Approve'}
            </button>
            <button
              onClick={handleReject}
              disabled={respondToApproval.isPending}
              className="flex-1 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Reject document"
            >
              {respondToApproval.isPending ? 'Processing...' : 'Reject'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
