/**
 * useDocumentVersions Hook
 * React Query hooks for document version control and comparison
 * Real API integration via documentsAPI
 * Week 4 - Documents Module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type { Document, VersionComparison } from '@/types/documents';

// ==================== TYPES ====================

export interface UseDocumentVersionsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface UseCreateVersionOptions {
  onSuccess?: (data: Document) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface UseCompareVersionsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface CreateVersionParams {
  documentId: number;
  userId: string;
  versionNotes?: string;
}

export interface CompareVersionsParams {
  sourceId: number;
  targetId: number;
  userId: string;
}

// ==================== QUERY KEYS ====================

export const versionQueryKeys = {
  all: (documentId: number) => ['documents', documentId, 'versions'] as const,
  comparison: (sourceId: number, targetId: number) =>
    ['documents', 'comparison', sourceId, targetId] as const,
  comparisons: () => ['documents', 'comparison'] as const,
};

// ==================== HELPER FUNCTIONS ====================

/**
 * Get the latest version from a list of document versions
 *
 * @param versions - Array of document versions
 * @returns Latest version or null if empty
 *
 * @example
 * ```tsx
 * const { data: versions } = useDocumentVersions(123);
 * const latest = getLatestVersion(versions || []);
 * console.log('Latest version:', latest?.version);
 * ```
 */
export function getLatestVersion(versions: Document[]): Document | null {
  if (!versions || versions.length === 0) return null;

  // First try to find version marked as latest
  const latestMarked = versions.find((v) => v.is_latest);
  if (latestMarked) return latestMarked;

  // Fallback: sort by version string and return last
  const sorted = sortVersionsByDate(versions);
  return sorted[sorted.length - 1] || null;
}

/**
 * Sort versions by creation date (oldest to newest)
 *
 * @param versions - Array of document versions
 * @returns Sorted array
 *
 * @example
 * ```tsx
 * const sorted = sortVersionsByDate(versions);
 * // [v1.0, v1.1, v2.0]
 * ```
 */
export function sortVersionsByDate(versions: Document[]): Document[] {
  return [...versions].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();
    return dateA - dateB;
  });
}

/**
 * Sort versions by version string (semantic versioning aware)
 *
 * @param versions - Array of document versions
 * @returns Sorted array
 *
 * @example
 * ```tsx
 * const sorted = sortVersionsByNumber(versions);
 * // [v1.0, v1.1, v2.0]
 * ```
 */
export function sortVersionsByNumber(versions: Document[]): Document[] {
  return [...versions].sort((a, b) => {
    // Parse version strings (e.g., "1.0", "2.1.3")
    const parseVersion = (version: string): number[] => {
      return version.split('.').map((v) => parseInt(v, 10) || 0);
    };

    const versionA = parseVersion(a.version);
    const versionB = parseVersion(b.version);

    // Compare each segment
    for (let i = 0; i < Math.max(versionA.length, versionB.length); i++) {
      const segmentA = versionA[i] || 0;
      const segmentB = versionB[i] || 0;

      if (segmentA !== segmentB) {
        return segmentA - segmentB;
      }
    }

    return 0;
  });
}

/**
 * Get version difference count (how many versions between two documents)
 *
 * @param versions - Array of all versions
 * @param sourceVersion - Source version string
 * @param targetVersion - Target version string
 * @returns Number of versions between source and target
 */
export function getVersionDifference(
  versions: Document[],
  sourceVersion: string,
  targetVersion: string
): number {
  const sorted = sortVersionsByNumber(versions);
  const sourceIndex = sorted.findIndex((v) => v.version === sourceVersion);
  const targetIndex = sorted.findIndex((v) => v.version === targetVersion);

  if (sourceIndex === -1 || targetIndex === -1) return 0;

  return Math.abs(targetIndex - sourceIndex);
}

/**
 * Check if a version is the latest
 *
 * @param version - Version to check
 * @param allVersions - All versions of the document
 * @returns True if this is the latest version
 */
export function isLatestVersion(
  version: Document,
  allVersions: Document[]
): boolean {
  const latest = getLatestVersion(allVersions);
  return latest?.document_id === version.document_id;
}

/**
 * Get version history summary
 *
 * @param versions - Array of versions
 * @returns Summary statistics
 */
export function getVersionHistorySummary(versions: Document[]) {
  const sorted = sortVersionsByDate(versions);
  const latest = getLatestVersion(versions);

  return {
    totalVersions: versions.length,
    latestVersion: latest?.version || 'N/A',
    oldestVersion: sorted[0]?.version || 'N/A',
    latestDate: latest?.created_at || null,
    oldestDate: sorted[0]?.created_at || null,
    hasMultipleVersions: versions.length > 1,
  };
}

// ==================== HOOKS ====================

/**
 * Hook to fetch all versions of a document
 *
 * @param documentId - Document ID
 * @param options - React Query options
 * @returns Query result with versions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: versions, isLoading } = useDocumentVersions(123, {
 *   enabled: true,
 *   staleTime: 5 * 60 * 1000,
 * });
 *
 * if (versions) {
 *   const latest = getLatestVersion(versions);
 *   const sorted = sortVersionsByDate(versions);
 * }
 * ```
 */
export function useDocumentVersions(
  documentId: number,
  options: UseDocumentVersionsOptions = {}
) {
  return useQuery({
    queryKey: versionQueryKeys.all(documentId),
    queryFn: () => documentsAPI.getVersions(documentId),

    // Caching strategy - versions don't change frequently
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
 * Hook to create a new version of a document
 *
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createVersion = useCreateVersion({
 *   onSuccess: (newVersion) => {
 *     toast.success(`Created version ${newVersion.version}`);
 *     router.push(`/documents/${newVersion.document_id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create version: ${error.message}`);
 *   }
 * });
 *
 * createVersion.mutate({
 *   documentId: 123,
 *   userId: 'user-123',
 *   versionNotes: 'Updated compliance section'
 * });
 * ```
 */
export function useCreateVersion(options: UseCreateVersionOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, userId, versionNotes }: CreateVersionParams) =>
      documentsAPI.createVersion(documentId, userId, versionNotes),

    onSuccess: (newVersion, variables) => {
      // Get parent document ID (the original document)
      const parentId = newVersion.parent_id || variables.documentId;

      // Invalidate versions list for parent document
      queryClient.invalidateQueries({
        queryKey: versionQueryKeys.all(parentId),
      });

      // Invalidate document detail for both parent and new version
      queryClient.invalidateQueries({
        queryKey: ['documents', parentId],
      });

      queryClient.invalidateQueries({
        queryKey: ['documents', newVersion.document_id],
      });

      // Invalidate document list (if is_latest flag changed)
      if (newVersion.is_latest) {
        queryClient.invalidateQueries({
          queryKey: ['documents', 'list'],
        });
      }

      // Set the new version in cache
      queryClient.setQueryData(
        ['documents', newVersion.document_id],
        newVersion
      );

      options.onSuccess?.(newVersion);
    },

    onError: (error: Error) => {
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

/**
 * Hook to compare two document versions
 *
 * @param sourceId - Source document ID
 * @param targetId - Target document ID
 * @param userId - User ID for access logging
 * @param options - React Query options
 * @returns Query result with comparison data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: comparison, isLoading } = useCompareVersions(
 *   123,  // older version
 *   124,  // newer version
 *   'user-123',
 *   { enabled: true }
 * );
 *
 * if (comparison) {
 *   console.log('Similarity:', comparison.similarity_score);
 *   console.log('Text added:', comparison.text_added);
 *   console.log('Changes:', comparison.changes_summary);
 * }
 * ```
 */
export function useCompareVersions(
  sourceId: number,
  targetId: number,
  userId: string,
  options: UseCompareVersionsOptions = {}
) {
  return useQuery({
    queryKey: versionQueryKeys.comparison(sourceId, targetId),
    queryFn: () => documentsAPI.compareVersions(sourceId, targetId, userId),

    // Caching strategy - comparisons are expensive and don't change
    staleTime: options.staleTime ?? 60 * 60 * 1000, // 1 hour
    gcTime: options.gcTime ?? 2 * 60 * 60 * 1000, // 2 hours

    // Enable/disable query
    enabled: options.enabled ?? true,

    // Error handling
    retry: 1,
    retryDelay: 2000,
  });
}

/**
 * Hook to perform on-demand version comparison (mutation style)
 * Use this when you want to trigger comparison on user action
 *
 * @param options - Callback options
 * @returns Mutation result
 *
 * @example
 * ```tsx
 * const compareVersions = useCompareVersionsMutation({
 *   onSuccess: (comparison) => {
 *     setComparisonResult(comparison);
 *     toast.success('Comparison complete');
 *   }
 * });
 *
 * // On button click
 * compareVersions.mutate({
 *   sourceId: 123,
 *   targetId: 124,
 *   userId: 'user-123'
 * });
 * ```
 */
export function useCompareVersionsMutation(
  options: UseCreateVersionOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ sourceId, targetId, userId }: CompareVersionsParams) =>
      documentsAPI.compareVersions(sourceId, targetId, userId),

    onSuccess: (data, variables) => {
      // Cache the comparison result
      queryClient.setQueryData(
        versionQueryKeys.comparison(variables.sourceId, variables.targetId),
        data
      );

      options.onSuccess?.(data as any);
    },

    onError: options.onError,
    onSettled: options.onSettled,
  });
}

/**
 * Prefetch utility for document versions
 * Useful for hover states, optimistic navigation
 *
 * @param queryClient - React Query client
 * @param documentId - Document ID to prefetch versions for
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/documents/${doc.document_id}/versions`}
 *   onMouseEnter={() => prefetchDocumentVersions(queryClient, doc.document_id)}
 * >
 *   View versions
 * </Link>
 * ```
 */
export function prefetchDocumentVersions(
  queryClient: any,
  documentId: number
) {
  return queryClient.prefetchQuery({
    queryKey: versionQueryKeys.all(documentId),
    queryFn: () => documentsAPI.getVersions(documentId),
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Prefetch utility for version comparison
 *
 * @param queryClient - React Query client
 * @param sourceId - Source document ID
 * @param targetId - Target document ID
 * @param userId - User ID
 *
 * @example
 * ```tsx
 * <Button
 *   onMouseEnter={() =>
 *     prefetchVersionComparison(queryClient, v1.id, v2.id, userId)
 *   }
 * >
 *   Compare versions
 * </Button>
 * ```
 */
export function prefetchVersionComparison(
  queryClient: any,
  sourceId: number,
  targetId: number,
  userId: string
) {
  return queryClient.prefetchQuery({
    queryKey: versionQueryKeys.comparison(sourceId, targetId),
    queryFn: () => documentsAPI.compareVersions(sourceId, targetId, userId),
    staleTime: 60 * 60 * 1000,
  });
}
