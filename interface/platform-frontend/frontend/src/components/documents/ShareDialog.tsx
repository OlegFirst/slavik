'use client';

/**
 * ShareDialog Component
 * Modal dialog for sharing documents with users or external emails
 * Week 4 Round 3 - Documents Module
 */

import { useState, useEffect } from 'react';
import { X, Mail, User, Clock, Copy, Check, Calendar, Send } from 'lucide-react';
import { SharePermission } from '@/types/documents';
import type { DocumentShare } from '@/types/documents';
import { useShareDocument, useDocumentShares, getShareRecipient } from '@/hooks/documents';
import { PermissionBadge } from './PermissionBadge';

export interface ShareDialogProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: number;
  documentTitle: string;
  onSuccess?: (share: DocumentShare) => void;
}

/**
 * Email validation regex (RFC 5322 compliant)
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Expiration presets for quick selection
 */
const EXPIRATION_PRESETS = [
  { label: '1 week', days: 7 },
  { label: '1 month', days: 30 },
  { label: '3 months', days: 90 },
  { label: '1 year', days: 365 },
  { label: 'Never', days: null },
];

/**
 * Quick share presets for common scenarios
 */
const QUICK_SHARE_PRESETS = [
  {
    name: 'View for 1 week',
    permission: SharePermission.VIEW,
    days: 7,
    canReshare: false,
  },
  {
    name: 'Comment for 1 month',
    permission: SharePermission.COMMENT,
    days: 30,
    canReshare: false,
  },
  {
    name: 'Edit - no expiry',
    permission: SharePermission.EDIT,
    days: null,
    canReshare: true,
  },
];

export function ShareDialog({
  isOpen,
  onClose,
  documentId,
  documentTitle,
  onSuccess,
}: ShareDialogProps) {
  // Form state
  const [recipient, setRecipient] = useState('');
  const [recipientType, setRecipientType] = useState<'user' | 'email'>('email');
  const [permission, setPermission] = useState<SharePermission>(SharePermission.VIEW);
  const [canReshare, setCanReshare] = useState(false);
  const [expirationDate, setExpirationDate] = useState<string>('');
  const [shareMessage, setShareMessage] = useState('');
  const [emailError, setEmailError] = useState('');
  const [showShareLink, setShowShareLink] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  // Hooks
  const { data: existingShares, isLoading: sharesLoading } = useDocumentShares(documentId, {
    enabled: isOpen,
  });
  const shareDocument = useShareDocument(documentId, {
    onSuccess: (share) => {
      // Show success message
      setShowShareLink(true);

      // Call parent callback
      onSuccess?.(share);

      // Reset form after short delay
      setTimeout(() => {
        resetForm();
      }, 2000);
    },
    onError: (error) => {
      setEmailError(error.message || 'Failed to share document');
    },
  });

  // Reset form
  const resetForm = () => {
    setRecipient('');
    setRecipientType('email');
    setPermission(SharePermission.VIEW);
    setCanReshare(false);
    setExpirationDate('');
    setShareMessage('');
    setEmailError('');
    setShowShareLink(false);
    setLinkCopied(false);
  };

  // Handle ESC key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Reset form when dialog closes
  useEffect(() => {
    if (!isOpen) {
      resetForm();
    }
  }, [isOpen]);

  // Validate email when recipient changes
  useEffect(() => {
    if (recipientType === 'email' && recipient) {
      if (!EMAIL_REGEX.test(recipient)) {
        setEmailError('Please enter a valid email address');
      } else {
        setEmailError('');
      }
    } else {
      setEmailError('');
    }
  }, [recipient, recipientType]);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate recipient
    if (!recipient) {
      setEmailError('Recipient is required');
      return;
    }

    // Validate email format
    if (recipientType === 'email' && !EMAIL_REGEX.test(recipient)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    // Check if already shared
    const alreadyShared = existingShares?.some(
      (share) =>
        (recipientType === 'email' && share.shared_with_email === recipient) ||
        (recipientType === 'user' && share.shared_with_user_id === recipient)
    );

    if (alreadyShared) {
      setEmailError('This document is already shared with this recipient');
      return;
    }

    // Prepare share data
    const shareData = {
      ...(recipientType === 'email'
        ? { shared_with_email: recipient }
        : { shared_with_user_id: recipient }),
      permission_level: permission,
      can_reshare: canReshare,
      ...(expirationDate && { expires_at: new Date(expirationDate).toISOString() }),
      ...(shareMessage && { share_message: shareMessage }),
    };

    // Submit
    shareDocument.mutate(shareData);
  };

  // Apply quick share preset
  const applyPreset = (preset: typeof QUICK_SHARE_PRESETS[0]) => {
    setPermission(preset.permission);
    setCanReshare(preset.canReshare);
    if (preset.days) {
      const date = new Date();
      date.setDate(date.getDate() + preset.days);
      setExpirationDate(date.toISOString().split('T')[0]);
    } else {
      setExpirationDate('');
    }
  };

  // Apply expiration preset
  const applyExpirationPreset = (days: number | null) => {
    if (days === null) {
      setExpirationDate('');
    } else {
      const date = new Date();
      date.setDate(date.getDate() + days);
      setExpirationDate(date.toISOString().split('T')[0]);
    }
  };

  // Copy share link (placeholder for future feature)
  const copyShareLink = () => {
    const shareLink = `${window.location.origin}/documents/${documentId}/shared`;
    navigator.clipboard.writeText(shareLink);
    setLinkCopied(true);
    setTimeout(() => setLinkCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Share Document</h2>
            <p className="text-sm text-gray-600 mt-1">{documentTitle}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Success message */}
          {showShareLink && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-900">
                    Document shared successfully!
                  </p>
                  <button
                    onClick={copyShareLink}
                    className="mt-2 inline-flex items-center gap-2 text-sm text-green-700 hover:text-green-800"
                  >
                    {linkCopied ? (
                      <>
                        <Check className="w-4 h-4" />
                        Link copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy share link
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Quick Share Presets */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quick Share
            </label>
            <div className="flex flex-wrap gap-2">
              {QUICK_SHARE_PRESETS.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => applyPreset(preset)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Share Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Recipient Type Toggle */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Share with
              </label>
              <div className="flex gap-2 mb-3">
                <button
                  type="button"
                  onClick={() => setRecipientType('email')}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-colors ${
                    recipientType === 'email'
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email Address
                </button>
                <button
                  type="button"
                  onClick={() => setRecipientType('user')}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-colors ${
                    recipientType === 'user'
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <User className="w-4 h-4 inline mr-2" />
                  User ID
                </button>
              </div>

              {/* Recipient Input */}
              <input
                type={recipientType === 'email' ? 'email' : 'text'}
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder={
                  recipientType === 'email'
                    ? 'colleague@example.com'
                    : 'Enter user ID'
                }
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  emailError ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {emailError && (
                <p className="mt-1 text-sm text-red-600">{emailError}</p>
              )}
            </div>

            {/* Permission Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Permission Level
              </label>
              <div className="space-y-2">
                {Object.values(SharePermission).map((perm) => (
                  <label
                    key={perm}
                    className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                      permission === perm
                        ? 'bg-blue-50 border-blue-500'
                        : 'border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="permission"
                      value={perm}
                      checked={permission === perm}
                      onChange={(e) => setPermission(e.target.value as SharePermission)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <PermissionBadge permission={perm} size="sm" showTooltip={false} />
                      </div>
                      <p className="text-xs text-gray-600">
                        {perm === SharePermission.VIEW &&
                          'Can view only'}
                        {perm === SharePermission.COMMENT &&
                          'Can view and add comments/suggestions'}
                        {perm === SharePermission.EDIT &&
                          'Can view, comment, and edit content'}
                        {perm === SharePermission.ADMIN &&
                          'Full access including sharing and deletion'}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Can Reshare */}
            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={canReshare}
                  onChange={(e) => setCanReshare(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  Allow recipient to reshare this document
                </span>
              </label>
            </div>

            {/* Expiration Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-1" />
                Expiration Date (optional)
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {EXPIRATION_PRESETS.map((preset) => (
                  <button
                    key={preset.label}
                    type="button"
                    onClick={() => applyExpirationPreset(preset.days)}
                    className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
              <input
                type="date"
                value={expirationDate}
                onChange={(e) => setExpirationDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Share Message */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message (optional)
              </label>
              <textarea
                value={shareMessage}
                onChange={(e) => setShareMessage(e.target.value)}
                placeholder="Add a note for the recipient..."
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={shareDocument.isPending || !!emailError}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {shareDocument.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Sharing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Share Document
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Current Shares List */}
          {existingShares && existingShares.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                Current Shares ({existingShares.length})
              </h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {existingShares.slice(0, 5).map((share) => (
                  <div
                    key={share.share_id}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg text-sm"
                  >
                    <span className="text-gray-700">
                      {getShareRecipient(share)}
                    </span>
                    <PermissionBadge
                      permission={share.permission_level}
                      size="sm"
                      showTooltip={false}
                    />
                  </div>
                ))}
                {existingShares.length > 5 && (
                  <p className="text-xs text-gray-500 text-center">
                    +{existingShares.length - 5} more
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
