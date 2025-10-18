/**
 * useDocumentWorkflow Hook
 * React Query hooks for document lifecycle workflow management
 * Real API integration via documentsAPI
 * Week 4 - Documents Module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import { DocumentStatus } from '@/types/documents';
import type { WorkflowStatus } from '@/types/documents';

// ==================== TYPES ====================

export interface UseWorkflowStatusOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface UseExecuteWorkflowActionOptions {
  onSuccess?: (data: WorkflowStatus) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface ExecuteWorkflowActionParams {
  documentId: number;
  action: WorkflowAction;
  userId: string;
  notes?: string;
}

export type WorkflowAction =
  | 'submit_for_review'
  | 'approve'
  | 'reject'
  | 'publish'
  | 'archive'
  | 'supersede'
  | 'mark_obsolete'
  | 'restore'
  | 'revise';

// ==================== QUERY KEYS ====================

export const workflowQueryKeys = {
  status: (documentId: number) => ['documents', documentId, 'workflow'] as const,
  all: () => ['documents', 'workflow'] as const,
};

// ==================== HELPER FUNCTIONS ====================

/**
 * Get available workflow actions based on current document status
 *
 * @param status - Current document status
 * @returns Array of available workflow actions
 *
 * @example
 * ```tsx
 * const actions = getAvailableActions(DocumentStatus.DRAFT);
 * // ['submit_for_review', 'archive']
 * ```
 */
export function getAvailableActions(status: DocumentStatus): WorkflowAction[] {
  const actionMap: Record<DocumentStatus, WorkflowAction[]> = {
    [DocumentStatus.DRAFT]: ['submit_for_review', 'archive'],
    [DocumentStatus.UNDER_REVIEW]: ['approve', 'reject', 'revise', 'archive'],
    [DocumentStatus.APPROVED]: ['publish', 'revise', 'archive'],
    [DocumentStatus.PUBLISHED]: ['archive', 'supersede', 'revise'],
    [DocumentStatus.ARCHIVED]: ['restore'],
    [DocumentStatus.SUPERSEDED]: ['restore', 'mark_obsolete'],
    [DocumentStatus.OBSOLETE]: ['restore'],
  };

  return actionMap[status] || [];
}

/**
 * Check if a workflow action can be executed on the current status
 *
 * @param status - Current document status
 * @param action - Workflow action to check
 * @returns True if action is available
 *
 * @example
 * ```tsx
 * const canPublish = canExecuteAction(DocumentStatus.APPROVED, 'publish');
 * // true
 * ```
 */
export function canExecuteAction(
  status: DocumentStatus,
  action: WorkflowAction
): boolean {
  const availableActions = getAvailableActions(status);
  return availableActions.includes(action);
}

/**
 * Get the target status for a workflow action
 *
 * @param action - Workflow action
 * @returns Expected target document status
 *
 * @example
 * ```tsx
 * const targetStatus = getTargetStatus('publish');
 * // DocumentStatus.PUBLISHED
 * ```
 */
export function getTargetStatus(action: WorkflowAction): DocumentStatus {
  const targetStatusMap: Record<WorkflowAction, DocumentStatus> = {
    submit_for_review: DocumentStatus.UNDER_REVIEW,
    approve: DocumentStatus.APPROVED,
    reject: DocumentStatus.DRAFT,
    publish: DocumentStatus.PUBLISHED,
    archive: DocumentStatus.ARCHIVED,
    supersede: DocumentStatus.SUPERSEDED,
    mark_obsolete: DocumentStatus.OBSOLETE,
    restore: DocumentStatus.DRAFT,
    revise: DocumentStatus.DRAFT,
  };

  return targetStatusMap[action];
}

/**
 * Validate if workflow action is allowed
 *
 * @param currentStatus - Current document status
 * @param action - Workflow action to validate
 * @returns Validation result with error message if invalid
 */
export function validateWorkflowAction(
  currentStatus: DocumentStatus,
  action: WorkflowAction
): { valid: boolean; error?: string } {
  if (!canExecuteAction(currentStatus, action)) {
    return {
      valid: false,
      error: `Cannot execute "${action}" on document with status "${currentStatus}"`,
    };
  }

  return { valid: true };
}

// ==================== HOOKS ====================

/**
 * Hook to fetch workflow status for a document
 * Provides current status and available actions
 *
 * @param documentId - Document ID
 * @param options - React Query options
 * @returns Query result with workflow status, loading state, error
 *
 * @example
 * ```tsx
 * const { data: workflow, isLoading } = useWorkflowStatus(123, {
 *   enabled: true,
 *   staleTime: 5 * 60 * 1000, // 5 minutes
 * });
 *
 * if (workflow) {
 *   console.log('Current status:', workflow.current_state);
 *   console.log('Available actions:', workflow.available_actions);
 * }
 * ```
 */
export function useWorkflowStatus(
  documentId: number,
  options: UseWorkflowStatusOptions = {}
) {
  return useQuery({
    queryKey: workflowQueryKeys.status(documentId),
    queryFn: () => documentsAPI.getWorkflowStatus(documentId),

    // Caching strategy - workflow status can change frequently
    staleTime: options.staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: options.gcTime ?? 10 * 60 * 1000, // 10 minutes

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
 * Hook to execute workflow actions on a document
 * Supports optimistic updates and automatic cache invalidation
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const executeAction = useExecuteWorkflowAction({
 *   onSuccess: (workflowStatus) => {
 *     toast.success(`Document transitioned to ${workflowStatus.current_state}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Workflow action failed: ${error.message}`);
 *   }
 * });
 *
 * // Execute action
 * executeAction.mutate({
 *   documentId: 123,
 *   action: 'publish',
 *   userId: 'user-123',
 *   notes: 'Ready for publication'
 * });
 * ```
 */
export function useExecuteWorkflowAction(
  options: UseExecuteWorkflowActionOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      documentId,
      action,
      userId,
      notes,
    }: ExecuteWorkflowActionParams) =>
      documentsAPI.executeWorkflowAction(documentId, action, userId, notes),

    onMutate: async ({ documentId, action }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: workflowQueryKeys.status(documentId),
      });

      // Snapshot previous workflow status for rollback
      const previousWorkflow = queryClient.getQueryData<WorkflowStatus>(
        workflowQueryKeys.status(documentId)
      );

      // Optimistically update workflow status
      if (previousWorkflow) {
        const targetStatus = getTargetStatus(action);
        const newAvailableActions = getAvailableActions(targetStatus);

        queryClient.setQueryData<WorkflowStatus>(
          workflowQueryKeys.status(documentId),
          {
            ...previousWorkflow,
            current_state: targetStatus,
            available_actions: newAvailableActions,
          }
        );
      }

      return { previousWorkflow };
    },

    onSuccess: (data, variables) => {
      // Update workflow status cache with real server data
      queryClient.setQueryData(
        workflowQueryKeys.status(variables.documentId),
        data
      );

      // Invalidate document detail (status might have changed)
      queryClient.invalidateQueries({
        queryKey: ['documents', variables.documentId],
      });

      // Invalidate document list (status filter might be affected)
      queryClient.invalidateQueries({
        queryKey: ['documents', 'list'],
      });

      // Invalidate approvals if action was approve/reject
      if (['approve', 'reject'].includes(variables.action)) {
        queryClient.invalidateQueries({
          queryKey: ['documents', variables.documentId, 'approvals'],
        });
      }

      options.onSuccess?.(data);
    },

    onError: (error: Error, variables, context) => {
      // Rollback on error
      if (context?.previousWorkflow) {
        queryClient.setQueryData(
          workflowQueryKeys.status(variables.documentId),
          context.previousWorkflow
        );
      }

      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

/**
 * Hook to submit document for review
 * Convenience wrapper around useExecuteWorkflowAction
 *
 * @param options - Callback options
 * @returns Mutation result
 *
 * @example
 * ```tsx
 * const submitForReview = useSubmitForReview({
 *   onSuccess: () => toast.success('Submitted for review'),
 * });
 *
 * submitForReview.mutate({
 *   documentId: 123,
 *   userId: 'user-123',
 *   notes: 'Please review ASAP'
 * });
 * ```
 */
export function useSubmitForReview(
  options: UseExecuteWorkflowActionOptions = {}
) {
  const executeAction = useExecuteWorkflowAction(options);

  return {
    ...executeAction,
    mutate: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutate({ ...params, action: 'submit_for_review' }),
    mutateAsync: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutateAsync({ ...params, action: 'submit_for_review' }),
  };
}

/**
 * Hook to approve document
 * Convenience wrapper around useExecuteWorkflowAction
 *
 * @param options - Callback options
 * @returns Mutation result
 */
export function useApproveDocument(
  options: UseExecuteWorkflowActionOptions = {}
) {
  const executeAction = useExecuteWorkflowAction(options);

  return {
    ...executeAction,
    mutate: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutate({ ...params, action: 'approve' }),
    mutateAsync: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutateAsync({ ...params, action: 'approve' }),
  };
}

/**
 * Hook to reject document
 * Convenience wrapper around useExecuteWorkflowAction
 *
 * @param options - Callback options
 * @returns Mutation result
 */
export function useRejectDocument(
  options: UseExecuteWorkflowActionOptions = {}
) {
  const executeAction = useExecuteWorkflowAction(options);

  return {
    ...executeAction,
    mutate: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutate({ ...params, action: 'reject' }),
    mutateAsync: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutateAsync({ ...params, action: 'reject' }),
  };
}

/**
 * Hook to publish document
 * Convenience wrapper around useExecuteWorkflowAction
 *
 * @param options - Callback options
 * @returns Mutation result
 */
export function usePublishDocument(
  options: UseExecuteWorkflowActionOptions = {}
) {
  const executeAction = useExecuteWorkflowAction(options);

  return {
    ...executeAction,
    mutate: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutate({ ...params, action: 'publish' }),
    mutateAsync: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutateAsync({ ...params, action: 'publish' }),
  };
}

/**
 * Hook to archive document
 * Convenience wrapper around useExecuteWorkflowAction
 *
 * @param options - Callback options
 * @returns Mutation result
 */
export function useArchiveDocument(
  options: UseExecuteWorkflowActionOptions = {}
) {
  const executeAction = useExecuteWorkflowAction(options);

  return {
    ...executeAction,
    mutate: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutate({ ...params, action: 'archive' }),
    mutateAsync: (params: Omit<ExecuteWorkflowActionParams, 'action'>) =>
      executeAction.mutateAsync({ ...params, action: 'archive' }),
  };
}
