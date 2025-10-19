/**
 * useDocumentSharing Hook
 * React Query hooks for document sharing and collaboration
 * Real API integration via documentsAPI.{getShares, shareDocument}
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type {
  DocumentShare,
  ShareRequest,
} from '@/lib/api/documents-client';
import { SharePermission } from '@/types/documents';

// ==================== QUERY KEYS ====================

export const shareQueryKeys = {
  all: (documentId: number) => ['documents', documentId, 'shares'] as const,
  detail: (shareId: number) => ['documents', 'share', shareId] as const,
};

// ==================== TYPES ====================

export interface UseDocumentSharesOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface UseShareDocumentOptions {
  onSuccess?: (data: DocumentShare) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export interface SharesByPermission {
  view: DocumentShare[];
  approve: DocumentShare[];
  edit: DocumentShare[];
  admin: DocumentShare[];
}

// ==================== MAIN HOOKS ====================

/**
 * Hook to fetch all shares for a document
 * Retrieves complete sharing history and current active shares
 *
 * @param documentId - Document ID to fetch shares for
 * @param options - React Query options
 * @returns Query result with shares data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: shares, isLoading, error } = useDocumentShares(123, {
 *   staleTime: 60000, // 1 minute
 *   enabled: isSharingTabActive
 * });
 *
 * const active = getActiveShares(shares || []);
 * const byPermission = groupSharesByPermission(shares || []);
 * ```
 */
export function useDocumentShares(
  documentId: number,
  options: UseDocumentSharesOptions = {}
) {
  return useQuery({
    queryKey: shareQueryKeys.all(documentId),
    queryFn: () => documentsAPI.getShares(documentId),

    // Default caching strategy
    staleTime: options.staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: options.gcTime ?? 5 * 60 * 1000, // 5 minutes

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
 * Hook to share document with user or email
 * Creates a new share with specified permission level and optional expiration
 *
 * @param documentId - Document ID to share
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const shareDocument = useShareDocument(123, {
 *   onSuccess: (share) => {
 *     toast.success(`Document shared with ${share.shared_with_email || share.shared_with_user_id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to share document: ${error.message}`);
 *   }
 * });
 *
 * // Share with existing user
 * shareDocument.mutate({
 *   shared_with_user_id: 'user-456',
 *   permission_level: 'edit',
 *   can_reshare: false,
 *   expires_at: '2025-12-31T23:59:59Z',
 *   share_message: 'Please review and provide feedback'
 * });
 *
 * // Share with external email
 * shareDocument.mutate({
 *   shared_with_email: 'external@partner.com',
 *   permission_level: 'view',
 *   can_reshare: false,
 *   expires_at: '2025-11-30T23:59:59Z'
 * });
 * ```
 */
export function useShareDocument(
  documentId: number,
  options: UseShareDocumentOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (shareData: ShareRequest) =>
      documentsAPI.shareDocument(documentId, shareData),

    onSuccess: (data) => {
      // Invalidate share list for this document
      queryClient.invalidateQueries({
        queryKey: shareQueryKeys.all(documentId),
      });

      // Invalidate document detail (access tracking may have changed)
      queryClient.invalidateQueries({
        queryKey: ['documents', documentId],
      });

      // Invalidate document list (sharing affects access metadata)
      queryClient.invalidateQueries({
        queryKey: ['documents', 'list'],
      });

      // Optimistically set the share detail cache
      queryClient.setQueryData(
        shareQueryKeys.detail(data.share_id),
        data
      );

      // Call user callback
      options.onSuccess?.(data);
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
 * Hook to revoke a document share
 * Note: This assumes an API endpoint exists. If not implemented in backend,
 * this will need to be updated once the endpoint is available.
 *
 * @param shareId - Share ID to revoke
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const revokeShare = useRevokeShare({
 *   onSuccess: () => {
 *     toast.success('Share revoked successfully');
 *   }
 * });
 *
 * // Revoke share
 * revokeShare.mutate({ shareId: 789, documentId: 123 });
 * ```
 */
export function useRevokeShare(options: UseShareDocumentOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      shareId,
      documentId,
    }: {
      shareId: number;
      documentId: number;
    }) => {
      // Note: This endpoint may need to be implemented in documentsAPI
      // For now, this is a placeholder structure
      const response = await fetch(
        `${documentsAPI}api/documents/shares/${shareId}`,
        {
          method: 'DELETE',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to revoke share');
      }

      return { shareId, documentId };
    },

    onSuccess: (data) => {
      // Invalidate share list for this document
      queryClient.invalidateQueries({
        queryKey: shareQueryKeys.all(data.documentId),
      });

      // Invalidate the specific share detail
      queryClient.invalidateQueries({
        queryKey: shareQueryKeys.detail(data.shareId),
      });

      // Invalidate document detail
      queryClient.invalidateQueries({
        queryKey: ['documents', data.documentId],
      });

      // Call user callback
      options.onSuccess?.(data as any);
    },

    onError: (error: Error) => {
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Filter shares to get only active (non-expired) ones
 * Checks expiration date
 *
 * @param shares - Array of document shares
 * @returns Filtered array of active shares
 *
 * @example
 * ```tsx
 * const { data: shares } = useDocumentShares(123);
 * const active = getActiveShares(shares || []);
 *
 * return (
 *   <div>
 *     <h3>Active Shares ({active.length})</h3>
 *     {active.map(share => (
 *       <ShareCard key={share.share_id} share={share} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function getActiveShares(shares: DocumentShare[]): DocumentShare[] {
  const now = new Date();

  return shares.filter((share) => {
    // Check if share has not expired
    if (share.expires_at) {
      return new Date(share.expires_at) > now;
    }

    // No expiration means it's active
    return true;
  });
}

/**
 * Filter shares to get expired ones
 * Useful for displaying share history and cleanup
 *
 * @param shares - Array of document shares
 * @returns Filtered array of expired shares
 *
 * @example
 * ```tsx
 * const { data: shares } = useDocumentShares(123);
 * const expired = getExpiredShares(shares || []);
 *
 * return (
 *   <div>
 *     <h4>Expired Shares ({expired.length})</h4>
 *     {expired.map(share => (
 *       <ExpiredShareCard key={share.share_id} share={share} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function getExpiredShares(shares: DocumentShare[]): DocumentShare[] {
  const now = new Date();

  return shares.filter((share) => {
    // Share has an expiration date that has passed
    if (share.expires_at && new Date(share.expires_at) <= now) {
      return true;
    }

    return false;
  });
}

/**
 * Filter shares to get those expiring soon (within specified days)
 *
 * @param shares - Array of document shares
 * @param daysThreshold - Number of days to consider "soon" (default: 7)
 * @returns Filtered array of shares expiring soon
 */
export function getExpiringSoonShares(
  shares: DocumentShare[],
  daysThreshold: number = 7
): DocumentShare[] {
  const now = new Date();
  const thresholdDate = new Date();
  thresholdDate.setDate(thresholdDate.getDate() + daysThreshold);

  return shares.filter((share) => {
    if (!share.expires_at) {
      return false;
    }

    const expiresAt = new Date(share.expires_at);
    return expiresAt > now && expiresAt <= thresholdDate;
  });
}

/**
 * Group shares by permission level
 * Returns organized map of shares by their access level
 *
 * @param shares - Array of document shares
 * @returns Object with shares grouped by permission (view, comment, edit, admin)
 *
 * @example
 * ```tsx
 * const { data: shares } = useDocumentShares(123);
 * const grouped = groupSharesByPermission(shares || []);
 *
 * return (
 *   <div>
 *     <Section title="Admins" count={grouped.admin.length}>
 *       {grouped.admin.map(share => <ShareCard key={share.share_id} share={share} />)}
 *     </Section>
 *     <Section title="Editors" count={grouped.edit.length}>
 *       {grouped.edit.map(share => <ShareCard key={share.share_id} share={share} />)}
 *     </Section>
 *     <Section title="Commenters" count={grouped.comment.length}>
 *       {grouped.comment.map(share => <ShareCard key={share.share_id} share={share} />)}
 *     </Section>
 *     <Section title="Viewers" count={grouped.view.length}>
 *       {grouped.view.map(share => <ShareCard key={share.share_id} share={share} />)}
 *     </Section>
 *   </div>
 * );
 * ```
 */
export function groupSharesByPermission(
  shares: DocumentShare[]
): SharesByPermission {
  return {
    view: shares.filter((share) => share.permission_level === SharePermission.VIEW),
    approve: shares.filter((share) => share.permission_level === SharePermission.COMMENT),
    edit: shares.filter((share) => share.permission_level === SharePermission.EDIT),
    admin: shares.filter((share) => share.permission_level === SharePermission.ADMIN),
  };
}

/**
 * Get permission level display name
 * Converts permission enum to human-readable label
 *
 * @param permission - Share permission level
 * @returns Human-readable permission name
 */
export function getPermissionLabel(permission: SharePermission): string {
  const labels: Record<SharePermission, string> = {
    [SharePermission.VIEW]: 'View Only',
    [SharePermission.COMMENT]: 'Can Comment',
    [SharePermission.EDIT]: 'Can Edit',
    [SharePermission.ADMIN]: 'Admin Access',
  };

  return labels[permission] || permission;
}

/**
 * Get permission level icon name (for UI components)
 *
 * @param permission - Share permission level
 * @returns Icon name (compatible with common icon libraries)
 */
export function getPermissionIcon(permission: SharePermission): string {
  const icons: Record<SharePermission, string> = {
    [SharePermission.VIEW]: 'eye',
    [SharePermission.COMMENT]: 'message-circle',
    [SharePermission.EDIT]: 'edit',
    [SharePermission.ADMIN]: 'shield',
  };

  return icons[permission] || 'help-circle';
}

/**
 * Check if share is about to expire (within 7 days)
 *
 * @param share - Document share to check
 * @returns True if share expires within 7 days
 */
export function isShareExpiringSoon(share: DocumentShare): boolean {
  if (!share.expires_at) {
    return false;
  }

  const now = new Date();
  const expiresAt = new Date(share.expires_at);
  const daysUntilExpiry = Math.ceil(
    (expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  );

  return daysUntilExpiry > 0 && daysUntilExpiry <= 7;
}

/**
 * Get share recipient identifier (user ID or email)
 *
 * @param share - Document share
 * @returns User ID or email, whichever is present
 */
export function getShareRecipient(share: DocumentShare): string {
  return (
    share.shared_with_user_id ||
    share.shared_with_user_id ||
    share.shared_with_email ||
    'Unknown'
  );
}
