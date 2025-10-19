'use client';

/**
 * RetentionInfo Component
 * Display retention policy information for a document
 * Week 4 - Documents Module
 */

import { useMemo } from 'react';
import { format, differenceInDays } from 'date-fns';
import {
  Shield,
  Calendar,
  Clock,
  AlertTriangle,
  Info,
  Archive,
  Trash2,
  FileSearch,
  Lock,
  TrendingUp,
} from 'lucide-react';
import {
  useDocumentRetentionStatus,
  calculateRetentionDate,
  getDaysUntilRetentionAction,
  formatRetentionPeriod,
  getRetentionStatusLabel,
} from '@/hooks/documents/useRetentionPolicies';
import { useDocument } from '@/hooks/documents/useDocument';

// ==================== TYPES ====================

interface RetentionInfoProps {
  documentId: number;
  showAdminActions?: boolean;
  onExtendRetention?: () => void;
  onApplyLegalHold?: () => void;
}

interface RetentionAction {
  type: 'ARCHIVE' | 'DELETE' | 'REVIEW';
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  label: string;
  description: string;
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Get retention action configuration
 */
function getRetentionAction(actionType: string | null | undefined): RetentionAction {
  const actions: Record<string, RetentionAction> = {
    ARCHIVE: {
      type: 'ARCHIVE',
      icon: Archive,
      color: 'text-blue-600',
      label: 'Archive Document',
      description: 'Document will be moved to archive storage',
    },
    DELETE: {
      type: 'DELETE',
      icon: Trash2,
      color: 'text-red-600',
      label: 'Delete Document',
      description: 'Document will be permanently deleted',
    },
    REVIEW: {
      type: 'REVIEW',
      icon: FileSearch,
      color: 'text-amber-600',
      label: 'Review Required',
      description: 'Document requires manual review before action',
    },
  };

  return (
    actions[actionType || ''] || {
      type: 'REVIEW',
      icon: FileSearch,
      color: 'text-gray-600',
      label: 'No Action',
      description: 'No automatic action configured',
    }
  );
}

/**
 * Get visual indicator color based on days remaining
 */
function getIndicatorColor(daysRemaining: number | null): string {
  if (daysRemaining === null) return 'bg-gray-400';
  if (daysRemaining < 0) return 'bg-red-500';
  if (daysRemaining < 7) return 'bg-red-400';
  if (daysRemaining < 30) return 'bg-orange-400';
  if (daysRemaining < 90) return 'bg-yellow-400';
  return 'bg-green-500';
}

/**
 * Calculate progress percentage for timeline
 */
function calculateProgress(
  createdAt: string,
  retentionDate: string | null
): number {
  if (!retentionDate) return 0;

  const created = new Date(createdAt).getTime();
  const retention = new Date(retentionDate).getTime();
  const now = Date.now();

  const total = retention - created;
  const elapsed = now - created;

  const progress = Math.min(Math.max((elapsed / total) * 100, 0), 100);
  return Math.round(progress);
}

/**
 * Format trigger type for display
 */
function formatTriggerType(triggerType: string): string {
  const triggers: Record<string, string> = {
    creation: 'Document Creation',
    approval: 'Document Approval',
    publication: 'Document Publication',
    archival: 'Document Archival',
  };
  return triggers[triggerType] || triggerType;
}

// ==================== SUB-COMPONENTS ====================

interface RetentionProgressBarProps {
  progress: number;
  daysRemaining: number | null;
}

function RetentionProgressBar({ progress, daysRemaining }: RetentionProgressBarProps) {
  const color = getIndicatorColor(daysRemaining);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">Retention Timeline</span>
        <span className="font-medium text-gray-900">{progress}% elapsed</span>
      </div>
      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-500`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

interface InfoRowProps {
  label: string;
  value: string | number | null;
  icon?: React.ComponentType<{ className?: string }>;
  highlight?: boolean;
}

function InfoRow({ label, value, icon: Icon, highlight }: InfoRowProps) {
  return (
    <div className="flex items-start justify-between py-3 border-b last:border-b-0">
      <div className="flex items-center gap-2 text-gray-600">
        {Icon && <Icon className="h-4 w-4" />}
        <span>{label}</span>
      </div>
      <div className={`font-medium text-right ${highlight ? 'text-blue-600' : 'text-gray-900'}`}>
        {value || 'N/A'}
      </div>
    </div>
  );
}

// ==================== MAIN COMPONENT ====================

export default function RetentionInfo({
  documentId,
  showAdminActions = false,
  onExtendRetention,
  onApplyLegalHold,
}: RetentionInfoProps) {
  const { data: document, isLoading: docLoading } = useDocument({ id: documentId, user_id: 'current-user' });
  const { data: retentionStatus, isLoading: statusLoading } = useDocumentRetentionStatus(documentId);

  const isLoading = docLoading || statusLoading;

  // Calculate retention details
  const retentionDetails = useMemo(() => {
    if (!document || !retentionStatus) return null;

    const policy = retentionStatus.policy;
    const retentionDate = calculateRetentionDate(document, policy);
    const daysUntil = getDaysUntilRetentionAction(retentionDate);
    const statusLabel = getRetentionStatusLabel(daysUntil);
    const progress = retentionDate
      ? calculateProgress(document.created_at, retentionDate)
      : 0;

    return {
      policy,
      retentionDate,
      daysUntil,
      statusLabel,
      progress,
      legalHold: retentionStatus.legal_hold || false,
    };
  }, [document, retentionStatus]);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-3" />
          <p className="text-gray-600">Loading retention information...</p>
        </div>
      </div>
    );
  }

  // No policy state
  if (!retentionDetails?.policy) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
        <Shield className="h-12 w-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Retention Policy</h3>
        <p className="text-gray-600">
          No retention policy currently applies to this document.
        </p>
        {showAdminActions && (
          <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            Assign Policy
          </button>
        )}
      </div>
    );
  }

  const { policy, retentionDate, daysUntil, statusLabel, progress, legalHold } = retentionDetails;
  const action = getRetentionAction(policy.trigger_type);
  const ActionIcon = action.icon;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Retention Information</h2>
          <p className="text-gray-600">Document retention policy and status</p>
        </div>

        {/* Status badge */}
        <div className="flex items-center gap-2">
          <div
            className={`
              px-3 py-1.5 rounded-full text-sm font-medium
              ${statusLabel.color === 'green' ? 'bg-green-100 text-green-700' : ''}
              ${statusLabel.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' : ''}
              ${statusLabel.color === 'orange' ? 'bg-orange-100 text-orange-700' : ''}
              ${statusLabel.color === 'red' ? 'bg-red-100 text-red-700' : ''}
              ${statusLabel.color === 'gray' ? 'bg-gray-100 text-gray-700' : ''}
            `}
          >
            {statusLabel.label}
          </div>
        </div>
      </div>

      {/* Legal hold warning */}
      {legalHold && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <Lock className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-red-900 mb-1">Legal Hold Active</h4>
            <p className="text-sm text-red-800">
              This document is under legal hold and cannot be deleted or modified until the hold is released.
            </p>
          </div>
        </div>
      )}

      {/* Policy details */}
      <div className="bg-white border rounded-lg p-6 space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b">
          <Shield className="h-6 w-6 text-blue-600" />
          <div>
            <h3 className="font-semibold text-gray-900">{policy.policy_name}</h3>
            {policy.description && (
              <p className="text-sm text-gray-600 mt-1">{policy.description}</p>
            )}
          </div>
        </div>

        <div className="space-y-0">
          <InfoRow
            label="Retention Period"
            value={formatRetentionPeriod(policy.retention_years)}
            icon={Clock}
            highlight
          />
          <InfoRow
            label="Trigger Event"
            value={formatTriggerType(policy.trigger_type)}
            icon={TrendingUp}
          />
          {retentionDate && (
            <InfoRow
              label="Retention Expires"
              value={format(new Date(retentionDate), 'MMM d, yyyy')}
              icon={Calendar}
            />
          )}
          {daysUntil !== null && (
            <InfoRow
              label="Days Until Action"
              value={daysUntil < 0 ? 'Expired' : `${daysUntil} days`}
              icon={AlertTriangle}
              highlight={daysUntil < 30}
            />
          )}
          <InfoRow
            label="Action After Retention"
            value={action.label}
            icon={ActionIcon}
          />
        </div>
      </div>

      {/* Progress bar */}
      {retentionDate && (
        <div className="bg-white border rounded-lg p-6">
          <RetentionProgressBar progress={progress} daysRemaining={daysUntil} />

          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Started:</span>
              <span className="ml-2 font-medium">
                {document && format(new Date(document.created_at), 'MMM d, yyyy')}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Expires:</span>
              <span className="ml-2 font-medium">
                {format(new Date(retentionDate), 'MMM d, yyyy')}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Action after retention */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
        <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="font-semibold text-blue-900 mb-1">Retention Action</h4>
          <p className="text-sm text-blue-800">{action.description}</p>
        </div>
      </div>

      {/* Admin actions */}
      {showAdminActions && (
        <div className="flex gap-3 pt-4 border-t">
          <button
            onClick={onExtendRetention}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors font-medium"
          >
            Extend Retention
          </button>
          <button
            onClick={onApplyLegalHold}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium"
          >
            Apply Legal Hold
          </button>
        </div>
      )}

      {/* Tooltip/Help */}
      <details className="bg-gray-50 rounded-lg p-4">
        <summary className="cursor-pointer font-medium text-gray-900 flex items-center gap-2">
          <Info className="h-4 w-4" />
          Understanding Retention Rules
        </summary>
        <div className="mt-3 text-sm text-gray-700 space-y-2">
          <p>
            Retention policies ensure documents are kept for the required period and properly
            disposed of when no longer needed.
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Documents cannot be deleted before the retention period expires</li>
            <li>Legal holds override retention policies and prevent any modifications</li>
            <li>Some policies require manual review before final disposition</li>
            <li>Retention periods typically start from creation, approval, or publication date</li>
          </ul>
        </div>
      </details>
    </div>
  );
}
