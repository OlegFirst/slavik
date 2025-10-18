/**
 * useCreateDocument Hook
 * React Query mutation hook for creating documents and uploading files
 * Real API integration via documentsAPI.createDocument and documentsAPI.uploadFile
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type { Document, DocumentCreate } from '@/lib/api/documents-client';
import { documentsQueryKeys } from './useDocuments';

export interface UseCreateDocumentOptions {
  onSuccess?: (data: Document) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UseUploadFileOptions {
  onSuccess?: (data: Document) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UploadFileParams {
  documentId: number;
  file: File;
  userId: string;
  autoProcess?: boolean;
}

/**
 * Hook to create new document metadata
 * Automatically invalidates document list cache on success
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createDocument = useCreateDocument({
 *   onSuccess: (document) => {
 *     toast.success(`Document "${document.title}" created`);
 *     router.push(`/documents/${document.document_id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create document: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * createDocument.mutate({
 *   tenant_id: 'org-123',
 *   title: 'Business Continuity Policy',
 *   document_type: DocumentType.POLICY,
 *   classification: DocumentClassification.INTERNAL,
 *   owner_id: 'user-456',
 *   department: 'Risk Management',
 *   tags: ['bcm', 'iso-22301'],
 *   // ... other fields
 * });
 * ```
 */
export function useCreateDocument(options: UseCreateDocumentOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentCreate) => documentsAPI.createDocument(data),

    onSuccess: (data) => {
      // Invalidate document lists to refetch with new document
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Optimistically set the single document cache
      queryClient.setQueryData(
        documentsQueryKeys.detail(data.document_id),
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
 * Hook to upload file to existing document
 * Automatically invalidates document detail cache on success
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const uploadFile = useUploadFile({
 *   onSuccess: (document) => {
 *     toast.success(`File uploaded successfully`);
 *     console.log(`File size: ${document.file_size} bytes`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to upload file: ${error.message}`);
 *   }
 * });
 *
 * // In file input handler
 * const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
 *   const file = event.target.files?.[0];
 *   if (file) {
 *     uploadFile.mutate({
 *       documentId: document.document_id,
 *       file,
 *       userId: currentUser.id,
 *       autoProcess: true
 *     });
 *   }
 * };
 * ```
 */
export function useUploadFile(options: UseUploadFileOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, file, userId, autoProcess = true }: UploadFileParams) =>
      documentsAPI.uploadFile(documentId, file, userId, autoProcess),

    onSuccess: (data, variables) => {
      // Invalidate document lists
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Invalidate and update specific document detail
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
 * Combined hook for create + upload workflow
 * First creates document metadata, then uploads file
 *
 * @example
 * ```tsx
 * const createWithFile = useCreateDocumentWithFile({
 *   onSuccess: (document) => {
 *     toast.success(`Document created and file uploaded`);
 *   }
 * });
 *
 * createWithFile.mutate({
 *   metadata: {
 *     tenant_id: 'org-123',
 *     title: 'New Policy',
 *     document_type: DocumentType.POLICY,
 *     owner_id: 'user-456'
 *   },
 *   file: selectedFile,
 *   userId: currentUser.id
 * });
 * ```
 */
export function useCreateDocumentWithFile(options: UseCreateDocumentOptions = {}) {
  const queryClient = useQueryClient();
  const createDocument = useCreateDocument();
  const uploadFile = useUploadFile();

  return useMutation({
    mutationFn: async ({
      metadata,
      file,
      userId,
      autoProcess = true,
    }: {
      metadata: DocumentCreate;
      file: File;
      userId: string;
      autoProcess?: boolean;
    }) => {
      // Step 1: Create document metadata
      const document = await createDocument.mutateAsync(metadata);

      // Step 2: Upload file
      const updatedDocument = await uploadFile.mutateAsync({
        documentId: document.document_id,
        file,
        userId,
        autoProcess,
      });

      return updatedDocument;
    },

    onSuccess: (data) => {
      // Invalidate document lists
      queryClient.invalidateQueries({
        queryKey: documentsQueryKeys.lists(),
      });

      // Update specific document cache
      queryClient.setQueryData(
        documentsQueryKeys.detail(data.document_id),
        data
      );

      // Call user callback
      options.onSuccess?.(data);
    },

    onError: options.onError,
    onSettled: options.onSettled,
  });
}
