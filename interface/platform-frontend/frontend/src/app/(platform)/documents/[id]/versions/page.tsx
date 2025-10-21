'use client';

/**
 * Document Version History Page
 * Dedicated page for viewing and comparing document versions
 * Week 4 - Documents Module - Advanced Pages
 */

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  ArrowLeft,
  GitBranch,
  Clock,
  Download,
  History,
  FileText,
  AlertCircle,
  RefreshCw,
  User,
  CheckCircle,
  Filter,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Hooks
import {
  useDocument,
  useDocumentVersions,
} from '@/hooks/documents';

// Components
import VersionHistory from '@/components/documents/VersionHistory';
import { VersionComparison } from '@/components/documents/VersionComparison';
import { DocumentStatusBadge } from '@/components/documents/DocumentStatusBadge';
import type { Document } from '@/types/documents';

// ==================== TYPES ====================

interface PageProps {
  params: {
    id: string;
  };
}

type VersionFilter = 'all' | 'published' | 'draft';

// ==================== HELPER FUNCTIONS ====================

function formatFileSize(bytes: number | null): string {
  if (!bytes) return 'Unknown';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getLatestVersion(versions: Document[]): Document | null {
  if (!versions || versions.length === 0) return null;
  return versions.reduce((latest, current) => {
    return (current.version || 0) > (latest.version || 0) ? current : latest;
  }, versions[0]);
}

function sortVersionsByDate(versions: Document[]): Document[] {
  return [...versions].sort((a, b) => {
    const dateA = new Date(a.created_at || 0).getTime();
    const dateB = new Date(b.created_at || 0).getTime();
    return dateB - dateA; // Most recent first
  });
}

// ==================== MAIN COMPONENT ====================

export default function DocumentVersionsPage({ params }: PageProps) {
  const router = useRouter();
  const documentId = parseInt(params.id, 10);

  // TODO: Get actual user_id from auth context
  const currentUserId = 'current-user';

  // State
  const [versionFilter, setVersionFilter] = useState<VersionFilter>('all');
  const [compareMode, setCompareMode] = useState(false);
  const [selectedVersion1, setSelectedVersion1] = useState<Document | null>(null);
  const [selectedVersion2, setSelectedVersion2] = useState<Document | null>(null);

  // Fetch document data
  const {
    data: document,
    isLoading: documentLoading,
    error: documentError,
  } = useDocument({ id: documentId, user_id: currentUserId });

  // Fetch versions
  const {
    data: versions,
    isLoading: versionsLoading,
    error: versionsError,
    refetch: refetchVersions,
  } = useDocumentVersions(documentId);

  // Calculate version stats
  const versionStats = useMemo(() => {
    if (!versions) return null;

    const latest = getLatestVersion(versions);
    const sorted = sortVersionsByDate(versions);
    const publishedCount = versions.filter(v => v.status === 'published').length;
    const draftCount = versions.filter(v => v.status === 'draft').length;

    return {
      total: versions.length,
      published: publishedCount,
      draft: draftCount,
      current: latest?.version || 'N/A',
      lastModified: latest?.updated_at || null,
    };
  }, [versions]);

  // Filter versions
  const filteredVersions = useMemo(() => {
    if (!versions) return [];

    if (versionFilter === 'published') {
      return versions.filter(v => v.status === 'published');
    } else if (versionFilter === 'draft') {
      return versions.filter(v => v.status === 'draft');
    }

    return versions;
  }, [versions, versionFilter]);

  // Handlers
  const handleViewVersion = (version: Document) => {
    router.push(`/documents/${version.document_id}`);
  };

  const handleCompareVersions = (v1: Document, v2: Document) => {
    setSelectedVersion1(v1);
    setSelectedVersion2(v2);
    setCompareMode(true);
  };

  const handleDownloadVersion = (version: Document) => {
    // TODO: Implement actual download
    toast.success(`Downloading version ${version.version}`);
    console.log('Download version:', version.file_path);
  };

  const handleBackToDocument = () => {
    router.push(`/documents/${documentId}`);
  };

  const handleCloseComparison = () => {
    setCompareMode(false);
    setSelectedVersion1(null);
    setSelectedVersion2(null);
  };

  const handleCreateNewVersion = () => {
    router.push(`/documents/${documentId}/new-version`);
  };

  // Loading state
  if (documentLoading || versionsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
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
  if (documentError || versionsError || !document) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Versions</h1>
            <p className="text-gray-600 mb-6">
              {documentError
                ? (documentError as Error).message
                : versionsError
                ? (versionsError as Error).message
                : 'Failed to load document versions'}
            </p>
            <button
              onClick={handleBackToDocument}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Document
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty state - only 1 version exists
  if (versions && versions.length <= 1) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Breadcrumbs */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <button onClick={() => router.push('/')} className="hover:text-orange-600 transition-colors">
              Home
            </button>
            <span>/</span>
            <button onClick={() => router.push('/documents')} className="hover:text-orange-600 transition-colors">
              Documents
            </button>
            <span>/</span>
            <button onClick={handleBackToDocument} className="hover:text-orange-600 transition-colors">
              {document.title}
            </button>
            <span>/</span>
            <span className="text-gray-900 font-medium">Version History</span>
          </div>

          {/* Empty State Card */}
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">No Version History</h1>
            <p className="text-gray-600 mb-6">
              This document only has one version. Create a new version to start tracking changes.
            </p>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={handleBackToDocument}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Document
              </button>
              <button
                onClick={handleCreateNewVersion}
                className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
              >
                <GitBranch className="w-5 h-5" />
                Create New Version
              </button>
            </div>
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
          <button onClick={() => router.push('/')} className="hover:text-orange-600 transition-colors">
            Home
          </button>
          <span>/</span>
          <button onClick={() => router.push('/documents')} className="hover:text-orange-600 transition-colors">
            Documents
          </button>
          <span>/</span>
          <button onClick={handleBackToDocument} className="hover:text-orange-600 transition-colors truncate max-w-md">
            {document.title}
          </button>
          <span>/</span>
          <span className="text-gray-900 font-medium">Version History</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-3">
                <button
                  onClick={handleBackToDocument}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  aria-label="Back to document"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <History className="w-8 h-8 text-orange-600" />
                <div className="flex-1 min-w-0">
                  <h1 className="text-3xl font-bold text-gray-900 truncate">Version History</h1>
                  <p className="text-gray-600 truncate">{document.title}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => refetchVersions()}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                onClick={handleCreateNewVersion}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
              >
                <GitBranch className="w-4 h-4" />
                Create New Version
              </button>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        {versionStats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Versions</p>
                  <p className="text-2xl font-bold text-gray-900">{versionStats.total}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Current Version</p>
                  <p className="text-2xl font-bold text-gray-900">v{versionStats.current}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Published</p>
                  <p className="text-2xl font-bold text-gray-900">{versionStats.published}</p>
                </div>
                <GitBranch className="w-8 h-8 text-emerald-600" />
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Drafts</p>
                  <p className="text-2xl font-bold text-gray-900">{versionStats.draft}</p>
                </div>
                <User className="w-8 h-8 text-amber-600" />
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Last Modified</p>
                  <p className="text-sm font-medium text-gray-900">
                    {versionStats.lastModified ? format(new Date(versionStats.lastModified), 'MMM d, yyyy') : 'N/A'}
                  </p>
                </div>
                <Clock className="w-8 h-8 text-orange-600" />
              </div>
            </div>
          </div>
        )}

        {/* Version Comparison View */}
        {compareMode && selectedVersion1 && selectedVersion2 ? (
          <div className="bg-white rounded-xl shadow-lg">
            <VersionComparison
              documentId={documentId}
              version1={selectedVersion1.document_id}
              version2={selectedVersion2.document_id}
              userId={currentUserId}
              onDownloadVersion={(versionId) => {
                const version = versions?.find(v => v.document_id === versionId);
                if (version) handleDownloadVersion(version);
              }}
              onClose={handleCloseComparison}
            />
          </div>
        ) : (
          /* Version History List */
          <div className="bg-white rounded-xl shadow-lg p-6">
            <VersionHistory
              documentId={documentId}
              onViewVersion={handleViewVersion}
              onCompareVersions={handleCompareVersions}
              onDownloadVersion={handleDownloadVersion}
            />
          </div>
        )}
      </div>
    </div>
  );
}
