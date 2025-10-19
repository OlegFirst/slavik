'use client';

/**
 * SharesList Component
 * Display and manage all shares for a document
 * Week 4 Round 3 - Documents Module
 */

import { useState } from 'react';
import {
  Users,
  Trash2,
  ChevronDown,
  ChevronUp,
  Clock,
  AlertCircle,
  UserCheck,
  Mail,
  Search,
  Shield,
} from 'lucide-react';
import type { DocumentShare } from '@/types/documents';
import { SharePermission } from '@/types/documents';
import {
  useDocumentShares,
  useRevokeShare,
  getActiveShares,
  getExpiredShares,
  groupSharesByPermission,
  getShareRecipient,
  isShareExpiringSoon,
} from '@/hooks/documents';
import { PermissionBadge } from './PermissionBadge';

export interface SharesListProps {
  documentId: number;
  currentUserId: string;
  isOwner: boolean;
  isAdmin: boolean;
}

/**
 * Confirm dialog for revoking share
 */
function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  recipient,
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  recipient: string;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-in fade-in slide-in-from-bottom-4 duration-200">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-red-100 rounded-full">
            <AlertCircle className="w-6 h-6 text-red-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Revoke Share Access?
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to revoke access for <strong>{recipient}</strong>?
              They will no longer be able to access this document.
            </p>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onConfirm();
                  onClose();
                }}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Revoke Access
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Loading skeleton for shares list
 */
function SharesListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="animate-pulse">
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="w-10 h-10 bg-gray-200 rounded-full" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-1/4" />
            </div>
            <div className="w-20 h-6 bg-gray-200 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Individual share item component
 */
function ShareItem({
  share,
  canRevoke,
  onRevoke,
}: {
  share: DocumentShare;
  canRevoke: boolean;
  onRevoke: (shareId: number) => void;
}) {
  const recipient = getShareRecipient(share);
  const isEmail = !!share.shared_with_email;
  const isExpiringSoon = isShareExpiringSoon(share);
  const isExpired = share.expires_at && new Date(share.expires_at) <= new Date();

  // Format dates
  const sharedDate = new Date(share.shared_at).toLocaleDateString();
  const expiresDate = share.expires_at
    ? new Date(share.expires_at).toLocaleDateString()
    : null;

  // Calculate days until expiry
  const daysUntilExpiry = share.expires_at
    ? Math.ceil(
        (new Date(share.expires_at).getTime() - new Date().getTime()) /
          (1000 * 60 * 60 * 24)
      )
    : null;

  return (
    <div
      className={`flex items-start gap-4 p-4 rounded-lg border transition-colors ${
        isExpired
          ? 'bg-gray-50 border-gray-200 opacity-75'
          : 'bg-white border-gray-200 hover:border-gray-300'
      }`}
    >
      {/* Avatar/Icon */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isEmail ? 'bg-blue-100' : 'bg-green-100'
        }`}
      >
        {isEmail ? (
          <Mail className="w-5 h-5 text-blue-600" />
        ) : (
          <UserCheck className="w-5 h-5 text-green-600" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Recipient */}
        <div className="flex items-center gap-2 mb-1">
          <p className="font-medium text-gray-900 truncate">{recipient}</p>
          {share.can_reshare && (
            <span title="Can reshare">
              <Shield className="w-4 h-4 text-amber-500" />
            </span>
          )}
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600">
          <span>Shared {sharedDate}</span>
          {expiresDate && (
            <span
              className={`flex items-center gap-1 ${
                isExpiringSoon ? 'text-amber-600 font-medium' : ''
              } ${isExpired ? 'text-red-600 font-medium' : ''}`}
            >
              <Clock className="w-3 h-3" />
              {isExpired
                ? `Expired ${expiresDate}`
                : `Expires ${expiresDate}`}
              {!isExpired && daysUntilExpiry !== null && (
                <span>({daysUntilExpiry}d)</span>
              )}
            </span>
          )}
          {share.access_count > 0 && (
            <span>
              {share.access_count} access{share.access_count !== 1 ? 'es' : ''}
            </span>
          )}
          {share.last_accessed_at && (
            <span>
              Last accessed{' '}
              {new Date(share.last_accessed_at).toLocaleDateString()}
            </span>
          )}
        </div>

        {/* Share message */}
        {share.share_message && (
          <p className="mt-2 text-sm text-gray-600 italic">
            "{share.share_message}"
          </p>
        )}
      </div>

      {/* Permission Badge & Actions */}
      <div className="flex items-center gap-2">
        <PermissionBadge
          permission={share.permission_level}
          size="sm"
          showTooltip={true}
        />
        {canRevoke && !isExpired && (
          <button
            onClick={() => onRevoke(share.share_id)}
            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Revoke access"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

export function SharesList({
  documentId,
  currentUserId,
  isOwner,
  isAdmin,
}: SharesListProps) {
  // State
  const [showExpired, setShowExpired] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [confirmRevoke, setConfirmRevoke] = useState<{
    shareId: number;
    recipient: string;
  } | null>(null);

  // Hooks
  const { data: shares, isLoading, error } = useDocumentShares(documentId);
  const revokeShare = useRevokeShare({
    onSuccess: () => {
      // Toast notification would go here
    },
  });

  // Process shares
  const activeShares = shares ? getActiveShares(shares) : [];
  const expiredShares = shares ? getExpiredShares(shares) : [];
  const groupedShares = groupSharesByPermission(activeShares);

  // Filter shares by search query
  const filterShares = (sharesToFilter: DocumentShare[]) => {
    if (!searchQuery) return sharesToFilter;

    return sharesToFilter.filter((share) => {
      const recipient = getShareRecipient(share).toLowerCase();
      return recipient.includes(searchQuery.toLowerCase());
    });
  };

  // Handle revoke
  const handleRevoke = (shareId: number, recipient: string) => {
    setConfirmRevoke({ shareId, recipient });
  };

  const confirmRevokeAction = () => {
    if (confirmRevoke) {
      revokeShare.mutate({
        shareId: confirmRevoke.shareId,
        documentId,
      });
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4">
        <SharesListSkeleton />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-red-900">Error Loading Shares</h3>
            <p className="text-sm text-red-700 mt-1">
              {error.message || 'Failed to load document shares'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (!shares || shares.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
          <Users className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No Shares Yet
        </h3>
        <p className="text-sm text-gray-600">
          This document hasn't been shared with anyone.
        </p>
      </div>
    );
  }

  const canRevoke = isOwner || isAdmin;

  return (
    <div className="space-y-6">
      {/* Header with Search */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Document Shares
          </h3>
          <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded-full">
            {activeShares.length} active
          </span>
        </div>

        {/* Search */}
        {activeShares.length > 3 && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search shares..."
              className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}
      </div>

      {/* Active Shares by Permission Level */}
      <div className="space-y-6">
        {/* Admin Shares */}
        {filterShares(groupedShares.admin).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Administrators ({filterShares(groupedShares.admin).length})
            </h4>
            <div className="space-y-2">
              {filterShares(groupedShares.admin).map((share) => (
                <ShareItem
                  key={share.share_id}
                  share={share}
                  canRevoke={canRevoke}
                  onRevoke={(id) => handleRevoke(id, getShareRecipient(share))}
                />
              ))}
            </div>
          </div>
        )}

        {/* Edit Shares */}
        {filterShares(groupedShares.edit).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">
              Can Edit ({filterShares(groupedShares.edit).length})
            </h4>
            <div className="space-y-2">
              {filterShares(groupedShares.edit).map((share) => (
                <ShareItem
                  key={share.share_id}
                  share={share}
                  canRevoke={canRevoke}
                  onRevoke={(id) => handleRevoke(id, getShareRecipient(share))}
                />
              ))}
            </div>
          </div>
        )}

        {/* Comment Shares */}
        {filterShares(groupedShares.approve).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">
              Can Comment ({filterShares(groupedShares.approve).length})
            </h4>
            <div className="space-y-2">
              {filterShares(groupedShares.approve).map((share) => (
                <ShareItem
                  key={share.share_id}
                  share={share}
                  canRevoke={canRevoke}
                  onRevoke={(id) => handleRevoke(id, getShareRecipient(share))}
                />
              ))}
            </div>
          </div>
        )}

        {/* View Shares */}
        {filterShares(groupedShares.view).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">
              View Only ({filterShares(groupedShares.view).length})
            </h4>
            <div className="space-y-2">
              {filterShares(groupedShares.view).map((share) => (
                <ShareItem
                  key={share.share_id}
                  share={share}
                  canRevoke={canRevoke}
                  onRevoke={(id) => handleRevoke(id, getShareRecipient(share))}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Expired Shares Section */}
      {expiredShares.length > 0 && (
        <div className="pt-6 border-t border-gray-200">
          <button
            onClick={() => setShowExpired(!showExpired)}
            className="flex items-center justify-between w-full text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
          >
            <span className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Expired Shares ({expiredShares.length})
            </span>
            {showExpired ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          {showExpired && (
            <div className="mt-3 space-y-2">
              {filterShares(expiredShares).map((share) => (
                <ShareItem
                  key={share.share_id}
                  share={share}
                  canRevoke={false}
                  onRevoke={() => {}}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Confirm Dialog */}
      {confirmRevoke && (
        <ConfirmDialog
          isOpen={true}
          onClose={() => setConfirmRevoke(null)}
          onConfirm={confirmRevokeAction}
          recipient={confirmRevoke.recipient}
        />
      )}
    </div>
  );
}
