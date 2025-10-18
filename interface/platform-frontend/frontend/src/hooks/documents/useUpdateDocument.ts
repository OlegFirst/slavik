/**
 * useUpdateDocument Hook
 * React Query mutation hook for updating document metadata
 * Real API integration via documentsAPI.updateDocument
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type { Document, DocumentUpdate } from '@/lib/api/documents-client';
import { documentsQueryKeys } from './useDocuments';

export interface UseUpdateDocumentOptions {
  onSuccess?: (data: Document) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UpdateDocumentParams {
  documentId: number;
  data: DocumentUpdate;
}

/**
 * Hook to update document metadata
 * Automatically invalidates document list and detail cache on success
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateDocument = useUpdateDocument({
 *   onSuccess: (document) => {
 *     toast.success(`Document "${document.title}" updated`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to update document: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * updateDocument.mutate({
 *   documentId: 123,
 *   data: {
 *     title: 'Updated Business Continuity Policy',
 *     description: 'Updated description',
 *     tags: ['bcm', 'iso-22301', 'updated'],
 *     classification: DocumentClassification.CONFIDENTIAL,
 *     // ... other fields
 *   }
 * });
 * ```
 */
export function useUpdateDocument(options: UseUpdateDocumentOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, data }: UpdateDocumentParams) =>
      documentsAPI.updateDocument(documentId, data),

    onSuccess: (data, variables) => {
      // Invalidate document lists to refetch with updated data
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Invalidate specific document detail
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.detail(variables.documentId),
      });

      // Optimistically update the document cache
      queryClient.setQueryData(
        documentsQueryKeys.detail(variables.documentId),
        data
      );

      // Call user callback
      options.onSuccess?.(data);
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
 * Hook to update document with optimistic updates
 * Immediately updates UI before server confirms
 *
 * @example
 * ```tsx
 * const updateDocumentOptimistic = useUpdateDocumentOptimistic({
 *   onError: (error, variables, context) => {
 *     // Rollback on error
 *     toast.error('Update failed, changes reverted');
 *   }
 * });
 * ```
 */
export function useUpdateDocumentOptimistic(options: UseUpdateDocumentOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, data }: UpdateDocumentParams) =>
      documentsAPI.updateDocument(documentId, data),

    onMutate: async ({ documentId, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: documentsQueryKeys.detail(documentId),
      });

      // Snapshot previous value
      const previousDocument = queryClient.getQueryData<Document>(
        documentsQueryKeys.detail(documentId)
      );

      // Optimistically update to new value
      if (previousDocument) {
        queryClient.setQueryData<Document>(
          documentsQueryKeys.detail(documentId),
          {
            ...previousDocument,
            ...data,
            updated_at: new Date().toISOString(),
          }
        );
      }

      // Return context with snapshot
      return { previousDocument };
    },

    onSuccess: (data, variables) => {
      // Invalidate lists
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Update with server response
      queryClient.setQueryData(
        documentsQueryKeys.detail(variables.documentId),
        data
      );

      options.onSuccess?.(data);
    },

    onError: (error, variables, context) => {
      // Rollback to previous value on error
      if (context?.previousDocument) {
        queryClient.setQueryData(
          documentsQueryKeys.detail(variables.documentId),
          context.previousDocument
        );
      }

      options.onError?.(error);
    },

    onSettled: (data, error, variables) => {
      // Always refetch after error or success
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.detail(variables.documentId),
      });

      options.onSettled?.();
    },
  });
}
