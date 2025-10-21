/**
 * WorkflowStatus Component
 * Display current workflow status and progress for documents
 * Shows lifecycle stage with visual progress indicator
 * Week 4 - Documents Module
 */

'use client';

import { DocumentStatus } from '@/types/documents';
import { DocumentStatusBadge, getStatusProgress } from './DocumentStatusBadge';
import { cn } from '@/lib/utils';
import {
  CheckCircle2,
  Clock,
  FileCheck,
  Globe,
  Archive,
  User,
  Calendar,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export interface WorkflowStatusProps {
  status: DocumentStatus;
  metadata?: {
    assignees?: string[];
    estimatedCompletion?: string;
    lastUpdated?: string;
    approvalStage?: number;
    totalStages?: number;
  };
  className?: string;
}

/**
 * Workflow lifecycle stages with progress mapping
 */
const LIFECYCLE_STAGES = [
  { status: DocumentStatus.DRAFT, label: 'Draft', progress: 0 },
  { status: DocumentStatus.UNDER_REVIEW, label: 'Under Review', progress: 33 },
  { status: DocumentStatus.APPROVED, label: 'Approved', progress: 66 },
  { status: DocumentStatus.PUBLISHED, label: 'Published', progress: 100 },
] as const;

/**
 * Get the current stage index based on status
 */
function getCurrentStageIndex(status: DocumentStatus): number {
  // Handle special statuses
  if (status === DocumentStatus.ARCHIVED) return 4;
  if (status === DocumentStatus.SUPERSEDED) return 3;
  if (status === DocumentStatus.OBSOLETE) return 0;

  const index = LIFECYCLE_STAGES.findIndex(stage => stage.status === status);
  return index !== -1 ? index : 0;
}

/**
 * WorkflowStatus displays current workflow status and progress
 *
 * Features:
 * - Visual progress indicator (stepper/timeline)
 * - Shows lifecycle stage (DRAFT → UNDER_REVIEW → APPROVED → PUBLISHED → ARCHIVED)
 * - Displays current assignees if in review
 * - Shows estimated completion time if available
 * - Uses DocumentStatusBadge for status display
 *
 * @param status - Current document status
 * @param metadata - Optional metadata (assignees, completion time, etc.)
 * @param className - Additional CSS classes
 */
export function WorkflowStatus({
  status,
  metadata = {},
  className
}: WorkflowStatusProps) {
  const currentStageIndex = getCurrentStageIndex(status);
  const progressPercentage = getStatusProgress(status);

  // Handle archived/superseded/obsolete separately
  const isSpecialStatus = [
    DocumentStatus.ARCHIVED,
    DocumentStatus.SUPERSEDED,
    DocumentStatus.OBSOLETE,
  ].includes(status);

  return (
    <div
      className={cn(
        'bg-white rounded-lg border p-6 space-y-6',
        className
      )}
      role="region"
      aria-label="Workflow Status"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Workflow Status
        </h3>
        <DocumentStatusBadge status={status} size="md" />
      </div>

      {/* Progress Indicator - Only for normal workflow */}
      {!isSpecialStatus && (
        <div className="space-y-4">
          {/* Progress Bar */}
          <div className="relative">
            <div className="overflow-hidden h-2 bg-gray-200 rounded-full">
              <div
                className="h-full bg-gradient-to-r from-orange-500 to-amber-500 transition-all duration-500 ease-out"
                style={{ width: `${progressPercentage}%` }}
                role="progressbar"
                aria-valuenow={progressPercentage}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Workflow progress: ${progressPercentage}%`}
              />
            </div>
          </div>

          {/* Stage Stepper */}
          <div className="relative flex justify-between items-center">
            {LIFECYCLE_STAGES.map((stage, index) => {
              const isCompleted = index < currentStageIndex;
              const isCurrent = index === currentStageIndex;
              const Icon = getStageIcon(stage.status);

              return (
                <div
                  key={stage.status}
                  className="flex flex-col items-center flex-1"
                >
                  {/* Stage Icon */}
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300',
                      isCompleted && 'bg-green-100 border-green-500',
                      isCurrent && 'bg-orange-100 border-orange-500',
                      !isCompleted && !isCurrent && 'bg-gray-100 border-gray-300'
                    )}
                    aria-current={isCurrent ? 'step' : undefined}
                  >
                    <Icon
                      className={cn(
                        'w-5 h-5',
                        isCompleted && 'text-green-600',
                        isCurrent && 'text-orange-600',
                        !isCompleted && !isCurrent && 'text-gray-400'
                      )}
                      aria-hidden="true"
                    />
                  </div>

                  {/* Stage Label */}
                  <span
                    className={cn(
                      'mt-2 text-xs font-medium text-center',
                      isCurrent && 'text-orange-700',
                      isCompleted && 'text-green-700',
                      !isCompleted && !isCurrent && 'text-gray-500'
                    )}
                  >
                    {stage.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Special Status Message */}
      {isSpecialStatus && (
        <div className={cn(
          'p-4 rounded-lg border-l-4',
          status === DocumentStatus.ARCHIVED && 'bg-gray-50 border-gray-400',
          status === DocumentStatus.SUPERSEDED && 'bg-purple-50 border-purple-400',
          status === DocumentStatus.OBSOLETE && 'bg-red-50 border-red-400'
        )}>
          <div className="flex items-center gap-2">
            <Archive className={cn(
              'w-5 h-5',
              status === DocumentStatus.ARCHIVED && 'text-gray-600',
              status === DocumentStatus.SUPERSEDED && 'text-purple-600',
              status === DocumentStatus.OBSOLETE && 'text-red-600'
            )} />
            <p className="text-sm font-medium text-gray-900">
              {status === DocumentStatus.ARCHIVED && 'Document has been archived'}
              {status === DocumentStatus.SUPERSEDED && 'Document has been superseded by a newer version'}
              {status === DocumentStatus.OBSOLETE && 'Document is obsolete and no longer in use'}
            </p>
          </div>
        </div>
      )}

      {/* Metadata Section */}
      <div className="space-y-3 pt-4 border-t border-gray-200">
        {/* Current Assignees */}
        {metadata.assignees && metadata.assignees.length > 0 && (
          <div className="flex items-start gap-2">
            <User className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-700">Current Reviewers</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {metadata.assignees.map((assignee, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200"
                  >
                    {assignee}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Approval Stage Progress */}
        {metadata.approvalStage !== undefined && metadata.totalStages !== undefined && (
          <div className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-700">Approval Progress</p>
              <p className="text-xs text-gray-600 mt-0.5">
                Stage {metadata.approvalStage} of {metadata.totalStages}
              </p>
            </div>
          </div>
        )}

        {/* Estimated Completion */}
        {metadata.estimatedCompletion && (
          <div className="flex items-start gap-2">
            <Clock className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-700">Estimated Completion</p>
              <p className="text-xs text-gray-600 mt-0.5">
                {formatDistanceToNow(new Date(metadata.estimatedCompletion), { addSuffix: true })}
              </p>
            </div>
          </div>
        )}

        {/* Last Updated */}
        {metadata.lastUpdated && (
          <div className="flex items-start gap-2">
            <Calendar className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-700">Last Updated</p>
              <p className="text-xs text-gray-600 mt-0.5">
                {formatDistanceToNow(new Date(metadata.lastUpdated), { addSuffix: true })}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Get icon for each workflow stage
 */
function getStageIcon(status: DocumentStatus) {
  const iconMap = {
    [DocumentStatus.DRAFT]: FileCheck,
    [DocumentStatus.UNDER_REVIEW]: Clock,
    [DocumentStatus.APPROVED]: CheckCircle2,
    [DocumentStatus.PUBLISHED]: Globe,
    [DocumentStatus.ARCHIVED]: Archive,
    [DocumentStatus.SUPERSEDED]: Archive,
    [DocumentStatus.OBSOLETE]: Archive,
  };

  return iconMap[status] || FileCheck;
}
