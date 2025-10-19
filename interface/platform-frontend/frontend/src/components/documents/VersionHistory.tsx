'use client';

/**
 * VersionHistory Component
 * Displays document version history with comparison capabilities
 * Week 4 - Documents Module
 */

import { useState, useMemo } from 'react';
import { format } from 'date-fns';
import {
  FileText,
  Download,
  Eye,
  GitCompare,
  ChevronDown,
  ChevronUp,
  Filter,
  Clock,
  User,
  FileCheck,
} from 'lucide-react';
import { useDocumentVersions, sortVersionsByDate } from '@/hooks/documents/useDocumentVersions';
import type { Document, DocumentStatus } from '@/types/documents';

// ==================== TYPES ====================

interface VersionHistoryProps {
  documentId: number;
  onViewVersion?: (version: Document) => void;
  onCompareVersions?: (v1: Document, v2: Document) => void;
  onDownloadVersion?: (version: Document) => void;
}

type StatusFilter = 'all' | 'published' | 'draft';

interface VersionNode {
  version: Document;
  children: VersionNode[];
  level: number;
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Parse semantic version string to components
 */
function parseVersion(versionString: string): { major: number; minor: number; patch: number } {
  const parts = versionString.split('.').map(p => parseInt(p, 10) || 0);
  return {
    major: parts[0] || 0,
    minor: parts[1] || 0,
    patch: parts[2] || 0,
  };
}

/**
 * Determine version change type
 */
function getVersionChangeType(current: string, previous: string): 'major' | 'minor' | 'patch' | null {
  const curr = parseVersion(current);
  const prev = parseVersion(previous);

  if (curr.major > prev.major) return 'major';
  if (curr.minor > prev.minor) return 'minor';
  if (curr.patch > prev.patch) return 'patch';
  return null;
}

/**
 * Build version tree structure
 */
function buildVersionTree(versions: Document[]): VersionNode[] {
  const sorted = sortVersionsByDate(versions);
  const nodeMap = new Map<number, VersionNode>();
  const roots: VersionNode[] = [];

  // Create nodes
  sorted.forEach(version => {
    nodeMap.set(version.document_id, {
      version,
      children: [],
      level: 0,
    });
  });

  // Build tree structure
  sorted.forEach(version => {
    const node = nodeMap.get(version.document_id);
    if (!node) return;

    if (version.parent_id && nodeMap.has(version.parent_id)) {
      const parent = nodeMap.get(version.parent_id)!;
      parent.children.push(node);
      node.level = parent.level + 1;
    } else {
      roots.push(node);
    }
  });

  return roots;
}

/**
 * Format file size
 */
function formatFileSize(bytes: number | null): string {
  if (!bytes) return 'N/A';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Get status badge color
 */
function getStatusColor(status: DocumentStatus): string {
  const colors: Record<DocumentStatus, string> = {
    draft: 'bg-gray-100 text-gray-700',
    under_review: 'bg-blue-100 text-blue-700',
    approved: 'bg-green-100 text-green-700',
    published: 'bg-emerald-100 text-emerald-700',
    archived: 'bg-amber-100 text-amber-700',
    superseded: 'bg-orange-100 text-orange-700',
    obsolete: 'bg-red-100 text-red-700',
  };
  return colors[status] || 'bg-gray-100 text-gray-700';
}

// ==================== SUB-COMPONENTS ====================

interface VersionCardProps {
  version: Document;
  isLatest: boolean;
  changeType: 'major' | 'minor' | 'patch' | null;
  isSelected: boolean;
  onToggleSelect: () => void;
  onView: () => void;
  onDownload: () => void;
  level: number;
}

function VersionCard({
  version,
  isLatest,
  changeType,
  isSelected,
  onToggleSelect,
  onView,
  onDownload,
  level,
}: VersionCardProps) {
  const [expanded, setExpanded] = useState(false);

  const changeTypeColors = {
    major: 'border-l-4 border-l-red-500',
    minor: 'border-l-4 border-l-blue-500',
    patch: 'border-l-4 border-l-green-500',
  };

  return (
    <div
      className={`
        rounded-lg border bg-white p-4 transition-all
        ${isSelected ? 'ring-2 ring-blue-500' : ''}
        ${changeType ? changeTypeColors[changeType] : ''}
      `}
      style={{ marginLeft: `${level * 24}px` }}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Left: Version info */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={onToggleSelect}
              className="h-4 w-4 rounded border-gray-300"
            />
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold">v{version.version}</h3>
              {isLatest && (
                <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded">
                  Latest
                </span>
              )}
              {changeType && (
                <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded capitalize">
                  {changeType}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(version.status)}`}>
              {version.status.replace('_', ' ')}
            </span>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {format(new Date(version.created_at), 'MMM d, yyyy HH:mm')}
            </div>
            <div className="flex items-center gap-1">
              <User className="h-4 w-4" />
              {version.created_by}
            </div>
            <div className="flex items-center gap-1">
              <FileText className="h-4 w-4" />
              {formatFileSize(version.file_size)}
            </div>
          </div>

          {version.description && (
            <p className="text-sm text-gray-700 line-clamp-2">{version.description}</p>
          )}
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onView}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
            title="View version"
          >
            <Eye className="h-5 w-5 text-gray-600" />
          </button>
          <button
            onClick={onDownload}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
            title="Download"
          >
            <Download className="h-5 w-5 text-gray-600" />
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
            title={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? (
              <ChevronUp className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            )}
          </button>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Document Code:</span>
            <span className="ml-2 font-medium">{version.document_code}</span>
          </div>
          <div>
            <span className="text-gray-500">File Name:</span>
            <span className="ml-2 font-medium">{version.file_name}</span>
          </div>
          {version.approved_at && (
            <div>
              <span className="text-gray-500">Approved:</span>
              <span className="ml-2 font-medium">
                {format(new Date(version.approved_at), 'MMM d, yyyy')}
              </span>
            </div>
          )}
          {version.published_at && (
            <div>
              <span className="text-gray-500">Published:</span>
              <span className="ml-2 font-medium">
                {format(new Date(version.published_at), 'MMM d, yyyy')}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ==================== MAIN COMPONENT ====================

export default function VersionHistory({
  documentId,
  onViewVersion,
  onCompareVersions,
  onDownloadVersion,
}: VersionHistoryProps) {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [selectedVersions, setSelectedVersions] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const { data: versions, isLoading, error } = useDocumentVersions(documentId);

  // Filter versions
  const filteredVersions = useMemo(() => {
    if (!versions) return [];

    let filtered = [...versions];

    if (statusFilter === 'published') {
      filtered = filtered.filter(v => v.status === 'published');
    } else if (statusFilter === 'draft') {
      filtered = filtered.filter(v => v.status === 'draft');
    }

    return sortVersionsByDate(filtered).reverse();
  }, [versions, statusFilter]);

  // Pagination
  const totalPages = Math.ceil(filteredVersions.length / itemsPerPage);
  const paginatedVersions = filteredVersions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Handle selection
  const handleToggleSelect = (versionId: number) => {
    const newSelected = new Set(selectedVersions);
    if (newSelected.has(versionId)) {
      newSelected.delete(versionId);
    } else if (newSelected.size < 2) {
      newSelected.add(versionId);
    }
    setSelectedVersions(newSelected);
  };

  const handleCompare = () => {
    if (selectedVersions.size !== 2 || !versions) return;
    const selected = Array.from(selectedVersions);
    const v1 = versions.find(v => v.document_id === selected[0]);
    const v2 = versions.find(v => v.document_id === selected[1]);
    if (v1 && v2 && onCompareVersions) {
      onCompareVersions(v1, v2);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading version history...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6 bg-red-50 rounded-lg border border-red-200">
        <p className="text-red-800">Failed to load version history: {error.message}</p>
      </div>
    );
  }

  // Empty state
  if (!versions || versions.length === 0) {
    return (
      <div className="text-center py-12">
        <FileCheck className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Version History</h3>
        <p className="text-gray-600">This document only has one version.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Version History</h2>
          <p className="text-gray-600 mt-1">
            {filteredVersions.length} version{filteredVersions.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="all">All Versions</option>
              <option value="published">Published Only</option>
              <option value="draft">Drafts Only</option>
            </select>
          </div>

          {selectedVersions.size === 2 && (
            <button
              onClick={handleCompare}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <GitCompare className="h-5 w-5" />
              Compare Selected
            </button>
          )}
        </div>
      </div>

      {/* Version list */}
      <div className="space-y-3">
        {paginatedVersions.map((version, index) => {
          const prevVersion = paginatedVersions[index + 1];
          const changeType = prevVersion
            ? getVersionChangeType(version.version, prevVersion.version)
            : null;

          return (
            <VersionCard
              key={version.document_id}
              version={version}
              isLatest={version.is_latest}
              changeType={changeType}
              isSelected={selectedVersions.has(version.document_id)}
              onToggleSelect={() => handleToggleSelect(version.document_id)}
              onView={() => onViewVersion?.(version)}
              onDownload={() => onDownloadVersion?.(version)}
              level={0}
            />
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t">
          <p className="text-sm text-gray-600">
            Showing {(currentPage - 1) * itemsPerPage + 1} to{' '}
            {Math.min(currentPage * itemsPerPage, filteredVersions.length)} of{' '}
            {filteredVersions.length} versions
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
