/**
 * WorkflowActions Component
 * Action buttons for document workflow transitions
 * Provides available actions based on current status and user permissions
 * Week 4 - Documents Module
 */

'use client';

import React, { useState } from 'react';
import { DocumentStatus } from '@/types/documents';
import {
  useExecuteWorkflowAction,
  getAvailableActions,
  type WorkflowAction,
} from '@/hooks/documents/useDocumentWorkflow';
import { cn } from '@/lib/utils';
import {
  Send,
  CheckCircle2,
  XCircle,
  Globe,
  Archive,
  GitBranch,
  AlertCircle,
  RotateCcw,
  Edit,
  Loader2,
} from 'lucide-react';
import toast from 'react-hot-toast';

export interface WorkflowActionsProps {
  documentId: string;
  currentStatus: DocumentStatus;
  onActionComplete?: () => void;
  className?: string;
}

/**
 * Action configuration with icons, labels, and styles
 */
const ACTION_CONFIG: Record<
  WorkflowAction,
  {
    label: string;
    icon: React.ElementType;
    variant: 'primary' | 'success' | 'danger' | 'warning' | 'secondary';
    requiresConfirmation: boolean;
    confirmationMessage?: string;
  }
> = {
  submit_for_review: {
    label: 'Submit for Review',
    icon: Send,
    variant: 'primary',
    requiresConfirmation: false,
  },
  approve: {
    label: 'Approve',
    icon: CheckCircle2,
    variant: 'success',
    requiresConfirmation: false,
  },
  reject: {
    label: 'Reject',
    icon: XCircle,
    variant: 'danger',
    requiresConfirmation: true,
    confirmationMessage: 'Are you sure you want to reject this document? It will be sent back to draft status.',
  },
  publish: {
    label: 'Publish',
    icon: Globe,
    variant: 'primary',
    requiresConfirmation: false,
  },
  archive: {
    label: 'Archive',
    icon: Archive,
    variant: 'warning',
    requiresConfirmation: true,
    confirmationMessage: 'Are you sure you want to archive this document? Archived documents can be restored later.',
  },
  supersede: {
    label: 'Supersede',
    icon: GitBranch,
    variant: 'secondary',
    requiresConfirmation: true,
    confirmationMessage: 'Are you sure you want to supersede this document? This indicates a newer version exists.',
  },
  mark_obsolete: {
    label: 'Mark Obsolete',
    icon: AlertCircle,
    variant: 'danger',
    requiresConfirmation: true,
    confirmationMessage: 'Are you sure you want to mark this document as obsolete? This indicates it is no longer valid.',
  },
  restore: {
    label: 'Restore',
    icon: RotateCcw,
    variant: 'secondary',
    requiresConfirmation: false,
  },
  revise: {
    label: 'Revise',
    icon: Edit,
    variant: 'secondary',
    requiresConfirmation: true,
    confirmationMessage: 'Are you sure you want to revise this document? It will be moved back to draft status.',
  },
};

/**
 * Button variant styles
 */
const BUTTON_VARIANTS = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600',
  success: 'bg-green-600 hover:bg-green-700 text-white border-green-600',
  danger: 'bg-red-600 hover:bg-red-700 text-white border-red-600',
  warning: 'bg-orange-600 hover:bg-orange-700 text-white border-orange-600',
  secondary: 'bg-gray-600 hover:bg-gray-700 text-white border-gray-600',
};

/**
 * WorkflowActions displays action buttons for workflow transitions
 *
 * Features:
 * - Shows available actions based on current document status
 * - Executes workflow actions using useDocumentWorkflow hook
 * - Confirmation dialogs for destructive actions (reject, archive, etc.)
 * - Loading states during action execution
 * - Error handling with toast notifications
 * - Success notifications on action completion
 *
 * @param documentId - Document ID to perform actions on
 * @param currentStatus - Current document status
 * @param onActionComplete - Callback when action completes successfully
 * @param className - Additional CSS classes
 */
export function WorkflowActions({
  documentId,
  currentStatus,
  onActionComplete,
  className,
}: WorkflowActionsProps) {
  const [confirmingAction, setConfirmingAction] = useState<WorkflowAction | null>(null);
  const [actionNotes, setActionNotes] = useState('');

  // Get available actions based on current status
  const availableActions = getAvailableActions(currentStatus);

  // Execute workflow action mutation
  const executeAction = useExecuteWorkflowAction({
    onSuccess: (workflowStatus) => {
      toast.success(`Document status updated to ${workflowStatus.current_state}`);
      setConfirmingAction(null);
      setActionNotes('');
      onActionComplete?.();
    },
    onError: (error) => {
      toast.error(`Action failed: ${error.message}`);
    },
  });

  /**
   * Handle action button click
   */
  const handleActionClick = (action: WorkflowAction) => {
    const config = ACTION_CONFIG[action];

    if (config.requiresConfirmation) {
      setConfirmingAction(action);
    } else {
      executeActionDirectly(action);
    }
  };

  /**
   * Execute action without confirmation
   */
  const executeActionDirectly = (action: WorkflowAction) => {
    executeAction.mutate({
      documentId: parseInt(documentId),
      action,
      userId: 'current-user', // TODO: Get from auth context
      notes: actionNotes || undefined,
    });
  };

  /**
   * Confirm and execute action
   */
  const handleConfirmAction = () => {
    if (confirmingAction) {
      executeActionDirectly(confirmingAction);
    }
  };

  /**
   * Cancel confirmation dialog
   */
  const handleCancelConfirmation = () => {
    setConfirmingAction(null);
    setActionNotes('');
  };

  if (availableActions.length === 0) {
    return (
      <div
        className={cn(
          'bg-gray-50 border border-gray-200 rounded-lg p-4 text-center',
          className
        )}
      >
        <AlertCircle className="h-5 w-5 text-gray-400 mx-auto mb-2" aria-hidden="true" />
        <p className="text-sm text-gray-600">No actions available for this document status</p>
      </div>
    );
  }

  return (
    <>
      {/* Action Buttons */}
      <div className={cn('space-y-3', className)} role="group" aria-label="Workflow actions">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Available Actions</h3>

        <div className="flex flex-wrap gap-2">
          {availableActions.map((action) => {
            const config = ACTION_CONFIG[action];
            const Icon = config.icon;
            const isExecuting = executeAction.isPending;

            return (
              <button
                key={action}
                onClick={() => handleActionClick(action)}
                disabled={isExecuting}
                className={cn(
                  'inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border font-medium text-sm transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  BUTTON_VARIANTS[config.variant],
                  isExecuting && 'opacity-75'
                )}
                aria-label={config.label}
              >
                {isExecuting ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <Icon className="h-4 w-4" aria-hidden="true" />
                )}
                {config.label}
              </button>
            );
          })}
        </div>

        {/* Action Guidance */}
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs text-blue-800 font-medium">
            Current Status: <span className="font-semibold">{currentStatus}</span>
          </p>
          <p className="text-xs text-blue-600 mt-1">
            Select an action above to transition the document to the next stage
          </p>
        </div>
      </div>

      {/* Confirmation Dialog */}
      {confirmingAction && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={handleCancelConfirmation}
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirmation-dialog-title"
        >
          <div
            className="relative w-full max-w-md bg-white rounded-lg shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Dialog Header */}
            <div className="border-b px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-6 w-6 text-orange-600" aria-hidden="true" />
                </div>
                <h2 id="confirmation-dialog-title" className="text-lg font-semibold text-gray-900">
                  Confirm Action
                </h2>
              </div>
            </div>

            {/* Dialog Content */}
            <div className="px-6 py-4 space-y-4">
              <p className="text-sm text-gray-700">
                {ACTION_CONFIG[confirmingAction].confirmationMessage}
              </p>

              {/* Optional Notes */}
              <div>
                <label htmlFor="action-notes" className="block text-sm font-medium text-gray-700 mb-2">
                  Add notes (optional)
                </label>
                <textarea
                  id="action-notes"
                  value={actionNotes}
                  onChange={(e) => setActionNotes(e.target.value)}
                  placeholder="Provide a reason or additional context..."
                  rows={3}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Dialog Actions */}
            <div className="border-t px-6 py-4 flex items-center justify-end gap-3">
              <button
                onClick={handleCancelConfirmation}
                disabled={executeAction.isPending}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAction}
                disabled={executeAction.isPending}
                className={cn(
                  'inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
                  BUTTON_VARIANTS[ACTION_CONFIG[confirmingAction].variant]
                )}
              >
                {executeAction.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                    Processing...
                  </>
                ) : (
                  <>
                    {React.createElement(ACTION_CONFIG[confirmingAction].icon, {
                      className: 'h-4 w-4',
                      'aria-hidden': 'true',
                    })}
                    Confirm
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
