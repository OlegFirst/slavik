/**
 * useDocument Hook
 * React Query hook for fetching single document
 * Real API integration via documentsAPI.getDocument
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type { Document } from '@/lib/api/documents-client';
import { documentsQueryKeys } from './useDocuments';

export interface UseDocumentParams {
  id: number;
  user_id: string;
}

export interface UseDocumentOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch and cache single document by ID
 * Automatically logs access for audit trail
 *
 * @param params - Document ID and user ID
 * @param options - React Query options
 * @returns Query result with document data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: document, isLoading, error } = useDocument({
 *   id: 123,
 *   user_id: 'user-456'
 * });
 *
 * if (document) {
 *   console.log(`Document: ${document.title}`);
 *   console.log(`Version: ${document.version}`);
 *   console.log(`Status: ${document.status}`);
 * }
 * ```
 */
export function useDocument(
  params: UseDocumentParams,
  options: UseDocumentOptions = {}
) {
  return useQuery({
    queryKey: documentsQueryKeys.detail(params.id),
    queryFn: () => documentsAPI.getDocument(params.id, params.user_id),

    // Caching strategy - single document changes less frequently
    staleTime: options.staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: options.gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Control refetching
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,

    // Enable/disable query
    enabled: options.enabled ?? true,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Prefetch utility for single document
 * Useful for hover states, optimistic navigation
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/documents/${document.document_id}`}
 *   onMouseEnter={() => prefetchDocument(queryClient, {
 *     id: document.document_id,
 *     user_id: currentUser.id
 *   })}
 * >
 *   {document.title}
 * </Link>
 * ```
 */
export function prefetchDocument(
  queryClient: any,
  params: UseDocumentParams
) {
  return queryClient.prefetchQuery({
    queryKey: documentsQueryKeys.detail(params.id),
    queryFn: () => documentsAPI.getDocument(params.id, params.user_id),
    staleTime: 10 * 60 * 1000,
  });
}
