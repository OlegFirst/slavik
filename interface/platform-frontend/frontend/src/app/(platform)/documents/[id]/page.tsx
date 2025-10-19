'use client';

/**
 * Document Detail Page
 * Comprehensive document detail view with tabs for overview, versions, approvals, sharing, activity, and retention
 * Week 4 - Documents Module - Agent 15 Round 4
 */

import { useState, useEffect, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  ArrowLeft,
  Edit,
  Share2,
  Download,
  Archive,
  MoreVertical,
  Trash2,
  Eye,
  Clock,
  FileText,
  GitBranch,
  CheckCircle,
  Users,
  Activity,
  Shield,
  Copy,
  Send,
  FileCheck,
  AlertCircle,
  Tag,
  User,
  Calendar,
  Folder,
  HardDrive,
  BarChart3,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Types
import type { Document, DocumentStatus, DocumentClassification, DocumentType } from '@/types/documents';

// Hooks
import {
  useDocument,
  useDocumentVersions,
  useDocumentApprovals,
  useDocumentShares,
  useDocumentAccessLog,
  useDocumentRetentionStatus,
  useUpdateDocument,
  useDeleteDocument,
  useExecuteWorkflowAction,
  getApprovalProgress,
  getActiveShares,
  formatTimeSince,
} from '@/hooks/documents';

// Components
import { DocumentStatusBadge } from '@/components/documents/DocumentStatusBadge';
import { DocumentTypeIcon } from '@/components/documents/DocumentTypeIcon';
import VersionHistory from '@/components/documents/VersionHistory';
import { ApprovalCard } from '@/components/documents/ApprovalCard';
import { ApprovalRequestDialog } from '@/components/documents/ApprovalRequestDialog';
import { WorkflowTimeline } from '@/components/documents/WorkflowTimeline';
import { ShareDialog } from '@/components/documents/ShareDialog';
import { SharesList } from '@/components/documents/SharesList';
import DocumentTimeline from '@/components/documents/DocumentTimeline';
import RetentionInfo from '@/components/documents/RetentionInfo';

// Tab enumeration
type TabType = 'overview' | 'versions' | 'approvals' | 'sharing' | 'activity' | 'retention';

// Props interface for page params
interface PageProps {
  params: {
    id: string;
  };
}

/**
 * Get classification badge color
 */
function getClassificationColor(classification: DocumentClassification): string {
  const colors: Record<DocumentClassification, string> = {
    public: 'bg-green-100 text-green-700 border-green-300',
    internal: 'bg-blue-100 text-blue-700 border-blue-300',
    confidential: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    restricted: 'bg-orange-100 text-orange-700 border-orange-300',
    highly_restricted: 'bg-red-100 text-red-700 border-red-300',
  };
  return colors[classification] || 'bg-gray-100 text-gray-700 border-gray-300';
}

/**
 * Format file size
 */
function formatFileSize(bytes: number | null): string {
  if (!bytes) return 'Unknown';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

/**
 * Document Detail Page Component
 */
export default function DocumentDetailPage({ params }: PageProps) {
  const router = useRouter();
  const documentId = parseInt(params.id, 10);

  // TODO: Get actual user_id from auth context
  const currentUserId = 'current-user';

  // State
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [isApprovalDialogOpen, setIsApprovalDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [showMoreMenu, setShowMoreMenu] = useState(false);

  // Fetch document data
  const {
    data: document,
    isLoading: documentLoading,
    error: documentError,
  } = useDocument({ id: documentId, user_id: currentUserId });

  // Fetch related data based on active tab
  const { data: versions, isLoading: versionsLoading } = useDocumentVersions(documentId, {
    enabled: activeTab === 'versions',
  });

  const { data: approvals, isLoading: approvalsLoading } = useDocumentApprovals(documentId, {
    enabled: activeTab === 'approvals',
  });

  const { data: shares, isLoading: sharesLoading } = useDocumentShares(documentId, {
    enabled: activeTab === 'sharing',
  });

  const { data: accessLog, isLoading: activityLoading } = useDocumentAccessLog(
    documentId,
    {},
    {
      enabled: activeTab === 'activity',
    }
  );

  const { data: retentionStatus, isLoading: retentionLoading } = useDocumentRetentionStatus(documentId, {
    enabled: activeTab === 'retention',
  });

  // Mutations
  const updateDocument = useUpdateDocument({
    onSuccess: () => {
      toast.success('Document updated successfully');
      setIsEditDialogOpen(false);
    },
    onError: (error) => {
      toast.error(`Failed to update document: ${error.message}`);
    },
  });

  const deleteDocument = useDeleteDocument({
    onSuccess: () => {
      toast.success('Document deleted successfully');
      router.push('/documents');
    },
    onError: (error) => {
      toast.error(`Failed to delete document: ${error.message}`);
    },
  });

  const executeWorkflowAction = useExecuteWorkflowAction({
    onSuccess: () => {
      toast.success('Document status updated');
    },
    onError: (error) => {
      toast.error(`Failed to update status: ${error.message}`);
    },
  });

  // Permission checks
  const isOwner = document?.owner_id === currentUserId;
  const canEdit = isOwner; // TODO: Add role-based permissions
  const canDelete = isOwner; // TODO: Add role-based permissions

  // Calculated values
  const approvalProgress = approvals ? getApprovalProgress(approvals) : null;
  const activeShares = shares ? getActiveShares(shares) : [];

  // Handle actions
  const handleDownload = () => {
    if (!document) return;
    // TODO: Implement actual download
    toast.success('Download started');
    console.log('Downloading document:', document.file_path);
  };

  const handleArchive = () => {
    if (!document) return;
    if (confirm('Archive this document? It will be moved to archived status.')) {
      executeWorkflowAction.mutate({
        documentId,
        action: 'archive',
        userId: currentUserId,
      });
    }
  };

  const handleDelete = () => {
    if (!document) return;
    if (confirm('Delete this document? This action cannot be undone.')) {
      deleteDocument.mutate({
        documentId,
        userId: currentUserId,
      });
    }
  };

  const handleCopyLink = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    toast.success('Link copied to clipboard');
  };

  // Sync active tab with URL
  useEffect(() => {
    const hash = window.location.hash.replace('#', '');
    if (hash && ['overview', 'versions', 'approvals', 'sharing', 'activity', 'retention'].includes(hash)) {
      setActiveTab(hash as TabType);
    }
  }, []);

  useEffect(() => {
    window.location.hash = activeTab;
  }, [activeTab]);

  // Loading state
  if (documentLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Skeleton header */}
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-64 bg-gray-200 rounded" />
            <div className="h-12 w-96 bg-gray-200 rounded" />
            <div className="h-32 bg-white rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (documentError || !document) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Not Found</h1>
            <p className="text-gray-600 mb-6">
              {documentError ? (documentError as Error).message : 'The document you are looking for does not exist.'}
            </p>
            <button
              onClick={() => router.push('/documents')}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Documents
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-orange-600 transition-colors"
          >
            Home
          </button>
          <span>/</span>
          <button
            onClick={() => router.push('/documents')}
            className="hover:text-orange-600 transition-colors"
          >
            Documents
          </button>
          <span>/</span>
          <span className="text-gray-900 font-medium truncate max-w-md">{document.title}</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start justify-between gap-4">
            {/* Left: Document info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-3">
                <button
                  onClick={() => router.push('/documents')}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  aria-label="Back to documents"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <DocumentTypeIcon type={document.document_type} className="w-8 h-8" />
                <div className="flex-1 min-w-0">
                  <h1 className="text-3xl font-bold text-gray-900 truncate">{document.title}</h1>
                </div>
              </div>

              <div className="flex items-center gap-3 flex-wrap ml-14">
                <DocumentStatusBadge status={document.status} />
                <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getClassificationColor(document.classification)}`}>
                  {document.classification.replace('_', ' ')}
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <GitBranch className="w-4 h-4" />
                  v{document.version}
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  Modified {format(new Date(document.updated_at), 'MMM d, yyyy')}
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <User className="w-4 h-4" />
                  {document.owner_id}
                </div>
              </div>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-2">
              {canEdit && (
                <button
                  onClick={() => setIsEditDialogOpen(true)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Edit
                </button>
              )}
              <button
                onClick={() => setIsShareDialogOpen(true)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <button
                onClick={handleDownload}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
              {canEdit && (
                <button
                  onClick={handleArchive}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
                >
                  <Archive className="w-4 h-4" />
                  Archive
                </button>
              )}

              {/* More actions dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowMoreMenu(!showMoreMenu)}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>
                {showMoreMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-10">
                    <button
                      onClick={() => {
                        setShowMoreMenu(false);
                        handleCopyLink();
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2"
                    >
                      <Copy className="w-4 h-4" />
                      Copy link
                    </button>
                    <button
                      onClick={() => {
                        setShowMoreMenu(false);
                        setActiveTab('activity');
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2"
                    >
                      <Activity className="w-4 h-4" />
                      View history
                    </button>
                    <button
                      onClick={() => {
                        setShowMoreMenu(false);
                        setIsApprovalDialogOpen(true);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Request approval
                    </button>
                    <button
                      onClick={() => {
                        setShowMoreMenu(false);
                        router.push(`/documents/${documentId}/new-version`);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2"
                    >
                      <GitBranch className="w-4 h-4" />
                      Create new version
                    </button>
                    {canDelete && (
                      <>
                        <div className="my-2 border-t border-gray-200" />
                        <button
                          onClick={() => {
                            setShowMoreMenu(false);
                            handleDelete();
                          }}
                          className="w-full px-4 py-2 text-left hover:bg-red-50 transition-colors flex items-center gap-2 text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete document
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px overflow-x-auto">
              {[
                { key: 'overview', label: 'Overview', icon: Eye },
                { key: 'versions', label: 'Versions', icon: GitBranch },
                { key: 'approvals', label: 'Approvals', icon: CheckCircle },
                { key: 'sharing', label: 'Sharing', icon: Users },
                { key: 'activity', label: 'Activity', icon: Activity },
                { key: 'retention', label: 'Retention', icon: Shield },
              ].map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key as TabType)}
                  className={`
                    flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap
                    ${activeTab === key
                      ? 'border-orange-600 text-orange-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  {label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Metadata Card */}
                <div className="bg-white border rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Metadata</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm text-gray-600">Type</span>
                        <div className="flex items-center gap-2 mt-1">
                          <DocumentTypeIcon type={document.document_type} className="w-5 h-5" />
                          <span className="font-medium">{document.document_type.replace('_', ' ')}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Classification</span>
                        <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium border mt-1 ${getClassificationColor(document.classification)}`}>
                          {document.classification.replace('_', ' ')}
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Department</span>
                        <div className="flex items-center gap-2 mt-1">
                          <Folder className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{document.department || 'N/A'}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Owner</span>
                        <div className="flex items-center gap-2 mt-1">
                          <User className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{document.owner_id}</span>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm text-gray-600">Created</span>
                        <div className="flex items-center gap-2 mt-1">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{format(new Date(document.created_at), 'PPP')}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Modified</span>
                        <div className="flex items-center gap-2 mt-1">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{format(new Date(document.updated_at), 'PPP')}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">File Size</span>
                        <div className="flex items-center gap-2 mt-1">
                          <HardDrive className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{formatFileSize(document.file_size)}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Format</span>
                        <div className="flex items-center gap-2 mt-1">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{document.file_type || 'Unknown'}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {document.description && (
                    <div className="mt-4 pt-4 border-t">
                      <span className="text-sm text-gray-600">Description</span>
                      <p className="mt-1 text-gray-900">{document.description}</p>
                    </div>
                  )}

                  {document.tags && document.tags.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <span className="text-sm text-gray-600 mb-2 block">Tags</span>
                      <div className="flex flex-wrap gap-2">
                        {document.tags.map((tag) => (
                          <span
                            key={tag}
                            className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                          >
                            <Tag className="w-3 h-3" />
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-blue-600 font-medium">Views</p>
                        <p className="text-2xl font-bold text-blue-900 mt-1">
                          {accessLog?.logs?.length || 0}
                        </p>
                      </div>
                      <Eye className="w-8 h-8 text-blue-600" />
                    </div>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-green-600 font-medium">Shares</p>
                        <p className="text-2xl font-bold text-green-900 mt-1">
                          {activeShares.length}
                        </p>
                      </div>
                      <Users className="w-8 h-8 text-green-600" />
                    </div>
                  </div>
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-amber-600 font-medium">Approval Status</p>
                        <p className="text-2xl font-bold text-amber-900 mt-1">
                          {approvalProgress
                            ? `${approvalProgress.completionRate}%`
                            : 'N/A'}
                        </p>
                      </div>
                      <CheckCircle className="w-8 h-8 text-amber-600" />
                    </div>
                  </div>
                </div>

                {/* Content Preview */}
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Preview</h3>
                  <div className="bg-white rounded-lg p-8 text-center">
                    <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">
                      Preview not available. Download the document to view its contents.
                    </p>
                    <button
                      onClick={handleDownload}
                      className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download to View
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Versions Tab */}
            {activeTab === 'versions' && (
              <Suspense fallback={<div className="text-center py-12">Loading versions...</div>}>
                {versionsLoading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading versions...</p>
                  </div>
                ) : (
                  <VersionHistory
                    documentId={documentId}
                    onViewVersion={(version) => {
                      console.log('View version:', version);
                      toast.success(`Viewing version ${version.version}`);
                    }}
                    onCompareVersions={(v1, v2) => {
                      console.log('Compare versions:', v1, v2);
                      toast.success('Version comparison coming soon');
                    }}
                    onDownloadVersion={(version) => {
                      console.log('Download version:', version);
                      toast.success(`Downloading version ${version.version}`);
                    }}
                  />
                )}
              </Suspense>
            )}

            {/* Approvals Tab */}
            {activeTab === 'approvals' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Approval Workflow</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Manage document approval requests and track approval status
                    </p>
                  </div>
                  <button
                    onClick={() => setIsApprovalDialogOpen(true)}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Request Approval
                  </button>
                </div>

                {approvalsLoading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading approvals...</p>
                  </div>
                ) : approvals && approvals.length > 0 ? (
                  <div className="space-y-4">
                    {approvals.map((approval) => (
                      <ApprovalCard key={approval.approval_id} approval={approval} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                    <FileCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No approval requests yet</p>
                  </div>
                )}
              </div>
            )}

            {/* Sharing Tab */}
            {activeTab === 'sharing' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Document Sharing</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Manage who has access to this document
                    </p>
                  </div>
                  <button
                    onClick={() => setIsShareDialogOpen(true)}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                  >
                    <Share2 className="w-4 h-4" />
                    Share Document
                  </button>
                </div>

                {/* Share link section */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 mr-4">
                      <p className="text-sm font-medium text-blue-900 mb-1">Share Link</p>
                      <code className="text-sm text-blue-700 break-all">
                        {window.location.href}
                      </code>
                    </div>
                    <button
                      onClick={handleCopyLink}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2 shrink-0"
                    >
                      <Copy className="w-4 h-4" />
                      Copy
                    </button>
                  </div>
                </div>

                {sharesLoading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading shares...</p>
                  </div>
                ) : (
                  <SharesList
                    documentId={documentId}
                    currentUserId={currentUserId}
                    isOwner={isOwner}
                    isAdmin={false}
                  />
                )}
              </div>
            )}

            {/* Activity Tab */}
            {activeTab === 'activity' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Activity Log</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Complete audit trail of all document actions
                  </p>
                </div>

                {activityLoading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading activity...</p>
                  </div>
                ) : (
                  <DocumentTimeline documentId={documentId} />
                )}
              </div>
            )}

            {/* Retention Tab */}
            {activeTab === 'retention' && (
              <Suspense fallback={<div className="text-center py-12">Loading retention info...</div>}>
                {retentionLoading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading retention information...</p>
                  </div>
                ) : (
                  <RetentionInfo
                    documentId={documentId}
                    showAdminActions={canEdit}
                    onExtendRetention={() => {
                      toast.success('Retention extension coming soon');
                    }}
                    onApplyLegalHold={() => {
                      toast.success('Legal hold application coming soon');
                    }}
                  />
                )}
              </Suspense>
            )}
          </div>
        </div>
      </div>

      {/* Dialogs */}
      <ShareDialog
        isOpen={isShareDialogOpen}
        onClose={() => setIsShareDialogOpen(false)}
        documentId={documentId}
        documentTitle={document.title}
        onSuccess={() => {
          toast.success('Document shared successfully');
        }}
      />

      <ApprovalRequestDialog
        documentId={documentId}
        open={isApprovalDialogOpen}
        onOpenChange={setIsApprovalDialogOpen}
      />

      {/* Close dropdown when clicking outside */}
      {showMoreMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowMoreMenu(false)}
        />
      )}
    </div>
  );
}
