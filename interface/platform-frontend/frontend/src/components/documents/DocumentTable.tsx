/**
 * DocumentTable Component
 * Table view for document browsing with sorting, selection, and bulk actions
 * Week 4 Round 3 - Documents Module
 */

'use client';

import { useState, useMemo } from 'react';
import {
  Eye,
  Edit,
  Share2,
  Download,
  Archive,
  Trash2,
  MoreVertical,
  ArrowUp,
  ArrowDown,
  Loader2,
  FileQuestion,
  CheckSquare,
  Square,
  X,
  Tag,
  FileDown,
} from 'lucide-react';
import { useDocuments } from '@/hooks/documents';
import { DocumentType, DocumentStatus, DocumentClassification } from '@/types/documents';
import type { Document } from '@/types/documents';
import { DocumentStatusBadge } from './DocumentStatusBadge';
import { DocumentTypeIcon } from './DocumentTypeIcon';

export interface DocumentTableProps {
  tenantId: string;
  filters?: any;
  onDocumentClick?: (document: Document) => void;
  onEdit?: (document: Document) => void;
  onShare?: (document: Document) => void;
  onDownload?: (document: Document) => void;
  onArchive?: (document: Document) => void;
  onDelete?: (document: Document) => void;
  onBulkShare?: (documents: Document[]) => void;
  onBulkArchive?: (documents: Document[]) => void;
  onBulkExport?: (documents: Document[]) => void;
  onBulkTag?: (documents: Document[]) => void;
}

type SortColumn = 'title' | 'type' | 'status' | 'classification' | 'owner' | 'modified';
type SortDirection = 'asc' | 'desc';

interface ActionMenuState {
  documentId: number | null;
  anchorEl: HTMLElement | null;
}

const CLASSIFICATION_COLORS = {
  [DocumentClassification.PUBLIC]: 'bg-green-100 text-green-800',
  [DocumentClassification.INTERNAL]: 'bg-blue-100 text-blue-800',
  [DocumentClassification.CONFIDENTIAL]: 'bg-yellow-100 text-yellow-800',
  [DocumentClassification.RESTRICTED]: 'bg-red-100 text-red-800',
  [DocumentClassification.HIGHLY_RESTRICTED]: 'bg-purple-100 text-purple-800',
};

export function DocumentTable({
  tenantId,
  filters = {},
  onDocumentClick,
  onEdit,
  onShare,
  onDownload,
  onArchive,
  onDelete,
  onBulkShare,
  onBulkArchive,
  onBulkExport,
  onBulkTag,
}: DocumentTableProps) {
  // Selection state
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [actionMenu, setActionMenu] = useState<ActionMenuState>({
    documentId: null,
    anchorEl: null,
  });

  // Sort state
  const [sortColumn, setSortColumn] = useState<SortColumn>('modified');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Fetch documents
  const { data, isLoading, error } = useDocuments({
    tenant_id: tenantId,
    ...filters,
  });

  // Sorted documents
  const sortedDocuments = useMemo(() => {
    if (!data?.documents) return [];

    const docs = [...data.documents];

    docs.sort((a, b) => {
      let aVal: any;
      let bVal: any;

      switch (sortColumn) {
        case 'title':
          aVal = a.title.toLowerCase();
          bVal = b.title.toLowerCase();
          break;
        case 'type':
          aVal = a.document_type;
          bVal = b.document_type;
          break;
        case 'status':
          aVal = a.status;
          bVal = b.status;
          break;
        case 'classification':
          aVal = a.classification;
          bVal = b.classification;
          break;
        case 'owner':
          aVal = a.owner_id;
          bVal = b.owner_id;
          break;
        case 'modified':
          aVal = new Date(a.updated_at).getTime();
          bVal = new Date(b.updated_at).getTime();
          break;
        default:
          return 0;
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return docs;
  }, [data?.documents, sortColumn, sortDirection]);

  // Handle column sort
  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Handle row selection
  const handleSelectAll = () => {
    if (selectedIds.size === sortedDocuments.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(sortedDocuments.map((d) => d.document_id)));
    }
  };

  const handleSelectRow = (documentId: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(documentId)) {
      newSelected.delete(documentId);
    } else {
      newSelected.add(documentId);
    }
    setSelectedIds(newSelected);
  };

  const getSelectedDocuments = () => {
    return sortedDocuments.filter((d) => selectedIds.has(d.document_id));
  };

  // Handle bulk actions
  const handleBulkAction = (action: 'share' | 'archive' | 'export' | 'tag') => {
    const selected = getSelectedDocuments();
    if (selected.length === 0) return;

    switch (action) {
      case 'share':
        onBulkShare?.(selected);
        break;
      case 'archive':
        onBulkArchive?.(selected);
        break;
      case 'export':
        onBulkExport?.(selected);
        break;
      case 'tag':
        onBulkTag?.(selected);
        break;
    }

    setSelectedIds(new Set()); // Clear selection after action
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  // Render sort icon
  const SortIcon = ({ column }: { column: SortColumn }) => {
    if (sortColumn !== column) return null;
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4" />
    ) : (
      <ArrowDown className="w-4 h-4" />
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-800">Error loading documents</p>
        <p className="text-sm text-red-600 mt-2">
          {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </div>
    );
  }

  if (sortedDocuments.length === 0) {
    return (
      <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
        <FileQuestion className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No documents found</h3>
        <p className="text-gray-600">Try adjusting your filters</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Bulk Actions Toolbar */}
      {selectedIds.size > 0 && (
        <div className="bg-orange-50 border-b border-orange-200 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-900">
              {selectedIds.size} selected
            </span>
            <button
              onClick={() => setSelectedIds(new Set())}
              className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
            >
              <X className="w-4 h-4" />
              Clear selection
            </button>
          </div>

          <div className="flex items-center gap-2">
            {onBulkShare && (
              <button
                onClick={() => handleBulkAction('share')}
                className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors flex items-center gap-2"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
            )}
            {onBulkArchive && (
              <button
                onClick={() => handleBulkAction('archive')}
                className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors flex items-center gap-2"
              >
                <Archive className="w-4 h-4" />
                Archive
              </button>
            )}
            {onBulkExport && (
              <button
                onClick={() => handleBulkAction('export')}
                className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors flex items-center gap-2"
              >
                <FileDown className="w-4 h-4" />
                Export metadata
              </button>
            )}
            {onBulkTag && (
              <button
                onClick={() => handleBulkAction('tag')}
                className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors flex items-center gap-2"
              >
                <Tag className="w-4 h-4" />
                Add tags
              </button>
            )}
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
            <tr>
              {/* Selection */}
              <th className="w-12 px-6 py-3 text-left">
                <button onClick={handleSelectAll} className="text-gray-600 hover:text-gray-900">
                  {selectedIds.size === sortedDocuments.length ? (
                    <CheckSquare className="w-5 h-5" />
                  ) : (
                    <Square className="w-5 h-5" />
                  )}
                </button>
              </th>

              {/* Icon */}
              <th className="w-12 px-3 py-3"></th>

              {/* Title */}
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('title')}
                  className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider hover:text-gray-900"
                >
                  Title
                  <SortIcon column="title" />
                </button>
              </th>

              {/* Type */}
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('type')}
                  className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider hover:text-gray-900"
                >
                  Type
                  <SortIcon column="type" />
                </button>
              </th>

              {/* Status */}
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('status')}
                  className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider hover:text-gray-900"
                >
                  Status
                  <SortIcon column="status" />
                </button>
              </th>

              {/* Classification */}
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('classification')}
                  className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider hover:text-gray-900"
                >
                  Classification
                  <SortIcon column="classification" />
                </button>
              </th>

              {/* Owner */}
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('owner')}
                  className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider hover:text-gray-900"
                >
                  Owner
                  <SortIcon column="owner" />
                </button>
              </th>

              {/* Modified */}
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('modified')}
                  className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider hover:text-gray-900"
                >
                  Modified
                  <SortIcon column="modified" />
                </button>
              </th>

              {/* Actions */}
              <th className="w-12 px-3 py-3"></th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {sortedDocuments.map((document) => (
              <tr
                key={document.document_id}
                className="hover:bg-gray-50 transition-colors"
              >
                {/* Selection */}
                <td className="px-6 py-4">
                  <button
                    onClick={() => handleSelectRow(document.document_id)}
                    className="text-gray-600 hover:text-gray-900"
                  >
                    {selectedIds.has(document.document_id) ? (
                      <CheckSquare className="w-5 h-5 text-orange-600" />
                    ) : (
                      <Square className="w-5 h-5" />
                    )}
                  </button>
                </td>

                {/* Icon */}
                <td className="px-3 py-4">
                  <DocumentTypeIcon type={document.document_type} className="w-5 h-5" />
                </td>

                {/* Title */}
                <td className="px-6 py-4">
                  <button
                    onClick={() => onDocumentClick?.(document)}
                    className="text-left hover:underline"
                  >
                    <div className="font-medium text-gray-900">{document.title}</div>
                    {document.description && (
                      <div className="text-sm text-gray-500 mt-1 line-clamp-1">
                        {document.description}
                      </div>
                    )}
                  </button>
                </td>

                {/* Type */}
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-700 capitalize">
                    {document.document_type.replace(/_/g, ' ')}
                  </span>
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <DocumentStatusBadge status={document.status} />
                </td>

                {/* Classification */}
                <td className="px-6 py-4">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      CLASSIFICATION_COLORS[document.classification]
                    }`}
                  >
                    {document.classification}
                  </span>
                </td>

                {/* Owner */}
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-700">{document.owner_id}</span>
                </td>

                {/* Modified */}
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-500">
                    {formatDate(document.updated_at)}
                  </span>
                </td>

                {/* Actions */}
                <td className="px-3 py-4 relative">
                  <div className="flex items-center gap-1">
                    {onDocumentClick && (
                      <button
                        onClick={() => onDocumentClick(document)}
                        className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                        title="View"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    )}
                    {onEdit && (
                      <button
                        onClick={() => onEdit(document)}
                        className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    )}
                    {onShare && (
                      <button
                        onClick={() => onShare(document)}
                        className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                        title="Share"
                      >
                        <Share2 className="w-4 h-4" />
                      </button>
                    )}
                    {onDownload && (
                      <button
                        onClick={() => onDownload(document)}
                        className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    )}
                    {(onArchive || onDelete) && (
                      <button
                        className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                        title="More actions"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
