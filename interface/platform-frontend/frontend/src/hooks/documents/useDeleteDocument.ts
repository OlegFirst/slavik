/**
 * useDeleteDocument Hook
 * React Query mutation hook for deleting documents (soft delete)
 * Real API integration via documentsAPI.deleteDocument
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import { documentsQueryKeys } from './useDocuments';

export interface UseDeleteDocumentOptions {
  onSuccess?: (documentId: number) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface DeleteDocumentParams {
  documentId: number;
  userId: string;
}

/**
 * Hook to delete document (soft delete - sets status to ARCHIVED)
 * Automatically invalidates document list cache and removes from detail cache
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteDocument = useDeleteDocument({
 *   onSuccess: (documentId) => {
 *     toast.success(`Document archived successfully`);
 *     router.push('/documents');
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to archive document: ${error.message}`);
 *   }
 * });
 *
 * // In delete button handler
 * const handleDelete = () => {
 *   if (confirm('Are you sure you want to archive this document?')) {
 *     deleteDocument.mutate({
 *       documentId: document.document_id,
 *       userId: currentUser.id
 *     });
 *   }
 * };
 * ```
 */
export function useDeleteDocument(options: UseDeleteDocumentOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, userId }: DeleteDocumentParams) =>
      documentsAPI.deleteDocument(documentId, userId),

    onSuccess: (_, variables) => {
      // Invalidate document lists to refetch without deleted document
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Remove document from detail cache
      queryClient.removeQueries({
        queryKey: documentsQueryKeys.detail(variables.documentId),
      });

      // Call user callback
      options.onSuccess?.(variables.documentId);
    },

    onError: (error: Error) => {
      // Call user callback
      options.onError?.(error);
    },

    onSettled: () => {
      // Call user callback
      options.onSettled?.();
    },
  });
}

/**
 * Hook for bulk deleting multiple documents
 * Sequentially deletes documents and provides progress tracking
 *
 * @example
 * ```tsx
 * const bulkDelete = useBulkDeleteDocuments({
 *   onSuccess: (report) => {
 *     toast.success(`Archived ${report.success_count}/${report.total_count} documents`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Bulk archive failed: ${error.message}`);
 *   }
 * });
 *
 * bulkDelete.mutate({
 *   documentIds: [1, 2, 3, 4, 5],
 *   userId: currentUser.id
 * });
 * ```
 */
export function useBulkDeleteDocuments(
  options: UseDeleteDocumentOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      documentIds,
      userId,
    }: {
      documentIds: number[];
      userId: string;
    }) => {
      const results = await Promise.allSettled(
        documentIds.map((documentId) =>
          documentsAPI.deleteDocument(documentId, userId)
        )
      );

      const successCount = results.filter((r) => r.status === 'fulfilled').length;
      const failureCount = results.filter((r) => r.status === 'rejected').length;

      return {
        total_count: documentIds.length,
        success_count: successCount,
        failure_count: failureCount,
        results,
      };
    },

    onSuccess: (data, variables) => {
      // Invalidate all document lists
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Remove successfully deleted documents from cache
      variables.documentIds.forEach((documentId) => {
        queryClient.removeQueries({
          queryKey: documentsQueryKeys.detail(documentId),
        });
      });

      // Call user callback with the first documentId (for backward compatibility)
      options.onSuccess?.(variables.documentIds[0]);
    },

    onError: options.onError,
    onSettled: options.onSettled,
  });
}
