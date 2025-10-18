/**
 * useDocuments Hook
 * React Query hook for listing documents with filters
 * Real API integration via documentsAPI.listDocuments
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { documentsAPI, type DocumentFilters } from '@/lib/api/documents-client';
import type { Document, DocumentStatus, DocumentType, DocumentClassification } from '@/lib/api/documents-client';

export interface UseDocumentsParams {
  tenant_id: string;
  document_type?: DocumentType;
  status?: DocumentStatus;
  classification?: DocumentClassification;
  owner_id?: string;
  department?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface UseDocumentsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
}

/**
 * Query key factory for documents
 * Provides consistent cache key generation
 */
export const documentsQueryKeys = {
  all: ['documents'] as const,
  lists: () => [...documentsQueryKeys.all, 'list'] as const,
  list: (params: UseDocumentsParams) => [...documentsQueryKeys.lists(), params] as const,
  details: () => [...documentsQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...documentsQueryKeys.details(), id] as const,
};

/**
 * Hook to fetch and cache documents list
 *
 * @param params - Filter parameters (tenant_id, document_type, status, etc.)
 * @param options - React Query options
 * @returns Query result with documents data, loading state, error
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useDocuments({
 *   tenant_id: 'org-123',
 *   document_type: DocumentType.POLICY,
 *   status: DocumentStatus.PUBLISHED
 * });
 *
 * if (data) {
 *   console.log(`Found ${data.total} documents`);
 *   console.log(data.documents);
 * }
 * ```
 */
export function useDocuments(
  params: UseDocumentsParams,
  options: UseDocumentsOptions = {}
) {
  return useQuery({
    queryKey: documentsQueryKeys.list(params),
    queryFn: () => documentsAPI.listDocuments(params),

    // Default caching strategy
    staleTime: options.staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: options.gcTime ?? 10 * 60 * 1000, // 10 minutes (formerly cacheTime)

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
 * Hook variant for draft documents only
 *
 * @example
 * ```tsx
 * const { data: drafts } = useDraftDocuments('org-123', {
 *   document_type: DocumentType.POLICY
 * });
 * ```
 */
export function useDraftDocuments(
  tenant_id: string,
  additionalParams: Omit<UseDocumentsParams, 'tenant_id' | 'status'> = {},
  options: UseDocumentsOptions = {}
) {
  return useDocuments(
    {
      tenant_id,
      ...additionalParams,
      status: 'DRAFT' as DocumentStatus,
    },
    options
  );
}

/**
 * Hook variant for published documents only
 *
 * @example
 * ```tsx
 * const { data: published } = usePublishedDocuments('org-123', {
 *   document_type: DocumentType.PROCEDURE
 * });
 * ```
 */
export function usePublishedDocuments(
  tenant_id: string,
  additionalParams: Omit<UseDocumentsParams, 'tenant_id' | 'status'> = {},
  options: UseDocumentsOptions = {}
) {
  return useDocuments(
    {
      tenant_id,
      ...additionalParams,
      status: 'PUBLISHED' as DocumentStatus,
    },
    options
  );
}

/**
 * Hook variant for archived documents only
 *
 * @example
 * ```tsx
 * const { data: archived } = useArchivedDocuments('org-123');
 * ```
 */
export function useArchivedDocuments(
  tenant_id: string,
  additionalParams: Omit<UseDocumentsParams, 'tenant_id' | 'status'> = {},
  options: UseDocumentsOptions = {}
) {
  return useDocuments(
    {
      tenant_id,
      ...additionalParams,
      status: 'ARCHIVED' as DocumentStatus,
    },
    options
  );
}

/**
 * Hook variant for documents under review
 *
 * @example
 * ```tsx
 * const { data: underReview } = useDocumentsUnderReview('org-123');
 * ```
 */
export function useDocumentsUnderReview(
  tenant_id: string,
  additionalParams: Omit<UseDocumentsParams, 'tenant_id' | 'status'> = {},
  options: UseDocumentsOptions = {}
) {
  return useDocuments(
    {
      tenant_id,
      ...additionalParams,
      status: 'IN_REVIEW' as DocumentStatus,
    },
    options
  );
}

/**
 * Prefetch utility for documents list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href="/documents/policies"
 *   onMouseEnter={() => prefetchDocuments(queryClient, {
 *     tenant_id: 'org-123',
 *     document_type: DocumentType.POLICY
 *   })}
 * >
 * ```
 */
export function prefetchDocuments(
  queryClient: any,
  params: UseDocumentsParams
) {
  return queryClient.prefetchQuery({
    queryKey: documentsQueryKeys.list(params),
    queryFn: () => documentsAPI.listDocuments(params),
    staleTime: 5 * 60 * 1000,
  });
}
