/**
 * DocumentList Component
 * Main document browsing interface with filters, search, and view modes
 * Week 4 Round 3 - Documents Module
 */

'use client';

import { useState, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Grid,
  List,
  Search,
  SlidersHorizontal,
  X,
  Plus,
  ChevronLeft,
  ChevronRight,
  Loader2,
  FileQuestion,
} from 'lucide-react';
import { useDocuments } from '@/hooks/documents';
import { DocumentType, DocumentStatus, DocumentClassification } from '@/types/documents';
import type { Document } from '@/types/documents';
import { DocumentCard } from './DocumentCard';
import { DocumentFilters } from './DocumentFilters';

export interface DocumentListProps {
  tenantId: string;
  onDocumentClick?: (document: Document) => void;
  onCreateDocument?: () => void;
  defaultViewMode?: 'grid' | 'list';
  enableFilters?: boolean;
  enableSearch?: boolean;
  showCreateButton?: boolean;
}

export interface FilterState {
  documentTypes: DocumentType[];
  statuses: DocumentStatus[];
  classifications: DocumentClassification[];
  departments: string[];
  owners: string[];
  dateRange: {
    from?: Date;
    to?: Date;
  };
  search: string;
}

export interface SortOption {
  value: string;
  label: string;
}

const SORT_OPTIONS: SortOption[] = [
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'title_asc', label: 'Title A-Z' },
  { value: 'title_desc', label: 'Title Z-A' },
  { value: 'modified', label: 'Recently modified' },
  { value: 'relevance', label: 'Most relevant' },
];

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

export function DocumentList({
  tenantId,
  onDocumentClick,
  onCreateDocument,
  defaultViewMode = 'grid',
  enableFilters = true,
  enableSearch = true,
  showCreateButton = true,
}: DocumentListProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // View mode state
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(defaultViewMode);
  const [showFilters, setShowFilters] = useState(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    documentTypes: [],
    statuses: [],
    classifications: [],
    departments: [],
    owners: [],
    dateRange: {},
    search: '',
  });

  // Sort state
  const [sortBy, setSortBy] = useState('newest');

  // Build query parameters for API
  const queryParams = useMemo(() => {
    const params: any = {
      tenant_id: tenantId,
      skip: (currentPage - 1) * pageSize,
      limit: pageSize,
    };

    // Add filters
    if (filters.documentTypes.length > 0) {
      params.document_type = filters.documentTypes[0]; // API supports single type
    }
    if (filters.statuses.length > 0) {
      params.status = filters.statuses[0];
    }
    if (filters.classifications.length > 0) {
      params.classification = filters.classifications[0];
    }
    if (filters.departments.length > 0) {
      params.department = filters.departments[0];
    }
    if (filters.owners.length > 0) {
      params.owner_id = filters.owners[0];
    }
    if (filters.search) {
      params.search = filters.search;
    }

    return params;
  }, [tenantId, currentPage, pageSize, filters]);

  // Fetch documents
  const { data, isLoading, error } = useDocuments(queryParams);

  // Calculate active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.documentTypes.length > 0) count++;
    if (filters.statuses.length > 0) count++;
    if (filters.classifications.length > 0) count++;
    if (filters.departments.length > 0) count++;
    if (filters.owners.length > 0) count++;
    if (filters.dateRange.from || filters.dateRange.to) count++;
    if (filters.search) count++;
    return count;
  }, [filters]);

  // Sort documents client-side (for demo - should be server-side in production)
  const sortedDocuments = useMemo(() => {
    if (!data?.documents) return [];

    const docs = [...data.documents];

    switch (sortBy) {
      case 'newest':
        return docs.sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      case 'oldest':
        return docs.sort(
          (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
      case 'title_asc':
        return docs.sort((a, b) => a.title.localeCompare(b.title));
      case 'title_desc':
        return docs.sort((a, b) => b.title.localeCompare(a.title));
      case 'modified':
        return docs.sort(
          (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );
      case 'relevance':
        // Relevance sorting would come from search API
        return docs;
      default:
        return docs;
    }
  }, [data?.documents, sortBy]);

  // Handle filter changes
  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  // Clear all filters
  const handleClearFilters = () => {
    setFilters({
      documentTypes: [],
      statuses: [],
      classifications: [],
      departments: [],
      owners: [],
      dateRange: {},
      search: '',
    });
    setCurrentPage(1);
  };

  // Pagination calculations
  const totalPages = data?.total ? Math.ceil(data.total / pageSize) : 0;
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, data?.total || 0);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
            <p className="text-sm text-gray-600 mt-1">
              {data?.total || 0} documents found
            </p>
          </div>

          {showCreateButton && onCreateDocument && (
            <button
              onClick={onCreateDocument}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Document
            </button>
          )}
        </div>

        {/* Search and Controls */}
        <div className="flex items-center gap-4">
          {/* Search */}
          {enableSearch && (
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents by title, description, tags..."
                value={filters.search}
                onChange={(e) => handleFilterChange({ search: e.target.value })}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
              {filters.search && (
                <button
                  onClick={() => handleFilterChange({ search: '' })}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          >
            {SORT_OPTIONS.filter(
              (opt) => opt.value !== 'relevance' || filters.search
            ).map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Filter Toggle */}
          {enableFilters && (
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
                showFilters
                  ? 'bg-orange-50 border-orange-600 text-orange-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filters
              {activeFilterCount > 0 && (
                <span className="px-2 py-0.5 bg-orange-600 text-white text-xs rounded-full">
                  {activeFilterCount}
                </span>
              )}
            </button>
          )}

          {/* View Mode Toggle */}
          <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 ${
                viewMode === 'grid'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
              title="Grid view"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 border-l border-gray-300 ${
                viewMode === 'list'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
              title="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Active Filters */}
        {activeFilterCount > 0 && (
          <div className="flex items-center gap-2 mt-4 flex-wrap">
            <span className="text-sm text-gray-600">Active filters:</span>
            {filters.documentTypes.map((type) => (
              <span
                key={type}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-2"
              >
                Type: {type}
                <button
                  onClick={() =>
                    handleFilterChange({
                      documentTypes: filters.documentTypes.filter((t) => t !== type),
                    })
                  }
                  className="hover:text-blue-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {filters.statuses.map((status) => (
              <span
                key={status}
                className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm flex items-center gap-2"
              >
                Status: {status}
                <button
                  onClick={() =>
                    handleFilterChange({
                      statuses: filters.statuses.filter((s) => s !== status),
                    })
                  }
                  className="hover:text-green-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            <button
              onClick={handleClearFilters}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 underline"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* Filters Sidebar */}
        {enableFilters && showFilters && (
          <div className="w-80 border-r border-gray-200 bg-white overflow-y-auto">
            <DocumentFilters
              filters={filters}
              onChange={handleFilterChange}
              onClear={handleClearFilters}
            />
          </div>
        )}

        {/* Document Grid/List */}
        <div className="flex-1 overflow-y-auto bg-gray-50">
          <div className="p-6">
            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <p className="text-red-800">Error loading documents</p>
                <p className="text-sm text-red-600 mt-2">
                  {error instanceof Error ? error.message : 'Unknown error'}
                </p>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && !error && sortedDocuments.length === 0 && (
              <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <FileQuestion className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No documents found
                </h3>
                <p className="text-gray-600 mb-6">
                  {activeFilterCount > 0
                    ? 'Try adjusting your filters'
                    : 'Get started by creating your first document'}
                </p>
                {showCreateButton && onCreateDocument && (
                  <button
                    onClick={onCreateDocument}
                    className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Create Document
                  </button>
                )}
              </div>
            )}

            {/* Document Grid */}
            {!isLoading && !error && sortedDocuments.length > 0 && (
              <>
                <div
                  className={
                    viewMode === 'grid'
                      ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                      : 'space-y-4'
                  }
                >
                  {sortedDocuments.map((document) => (
                    <DocumentCard
                      key={document.document_id}
                      document={document}
                      onClick={() => onDocumentClick?.(document)}
                      layout={viewMode}
                    />
                  ))}
                </div>

                {/* Pagination */}
                <div className="mt-8 flex items-center justify-between border-t border-gray-200 pt-6">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">
                      Showing {startItem}-{endItem} of {data?.total || 0}
                    </span>
                    <select
                      value={pageSize}
                      onChange={(e) => {
                        setPageSize(Number(e.target.value));
                        setCurrentPage(1);
                      }}
                      className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                    >
                      {PAGE_SIZE_OPTIONS.map((size) => (
                        <option key={size} value={size}>
                          {size} per page
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>

                    {/* Page Numbers */}
                    <div className="flex items-center gap-1">
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum;
                        if (totalPages <= 5) {
                          pageNum = i + 1;
                        } else if (currentPage <= 3) {
                          pageNum = i + 1;
                        } else if (currentPage >= totalPages - 2) {
                          pageNum = totalPages - 4 + i;
                        } else {
                          pageNum = currentPage - 2 + i;
                        }

                        return (
                          <button
                            key={pageNum}
                            onClick={() => setCurrentPage(pageNum)}
                            className={`px-3 py-1 rounded-lg ${
                              currentPage === pageNum
                                ? 'bg-orange-600 text-white'
                                : 'text-gray-700 hover:bg-gray-100'
                            }`}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                    </div>

                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
