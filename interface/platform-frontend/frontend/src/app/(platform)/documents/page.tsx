'use client';

/**
 * Documents Module - Main List Page
 * Production-ready document management with tabs, filters, and multi-view
 * Week 4 Round 4 - AI Platform ISO Project
 */

import { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Plus,
  Filter,
  Grid,
  List as ListIcon,
  Search,
  X,
  FileText,
  Clock,
  CheckCircle,
  Archive,
  User,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import {
  useDocuments,
  useDraftDocuments,
  usePublishedDocuments,
  useArchivedDocuments,
  useDocumentsUnderReview,
} from '@/hooks/documents';
import { DocumentStatus, DocumentType, DocumentClassification } from '@/types/documents';
import type { Document } from '@/types/documents';
import { DocumentCard } from '@/components/documents/DocumentCard';
import { DocumentTable } from '@/components/documents/DocumentTable';
import { DocumentFilters, FilterState } from '@/components/documents/DocumentFilters';
import { DocumentCreateForm } from '@/components/documents/forms/DocumentCreateForm';
import { DocumentUploadForm } from '@/components/documents/forms/DocumentUploadForm';
import toast from 'react-hot-toast';

/**
 * Tab Definition
 */
interface TabConfig {
  id: string;
  label: string;
  icon: React.ReactNode;
  status?: DocumentStatus;
  description: string;
}

const TABS: TabConfig[] = [
  {
    id: 'all',
    label: 'All Documents',
    icon: <FileText className="w-4 h-4" />,
    description: 'All documents across all statuses',
  },
  {
    id: 'my-documents',
    label: 'My Documents',
    icon: <User className="w-4 h-4" />,
    description: 'Documents you own',
  },
  {
    id: 'drafts',
    label: 'Drafts',
    icon: <Clock className="w-4 h-4" />,
    status: DocumentStatus.DRAFT,
    description: 'Documents in draft state',
  },
  {
    id: 'under-review',
    label: 'Under Review',
    icon: <AlertCircle className="w-4 h-4" />,
    status: DocumentStatus.UNDER_REVIEW,
    description: 'Documents pending approval',
  },
  {
    id: 'published',
    label: 'Published',
    icon: <CheckCircle className="w-4 h-4" />,
    status: DocumentStatus.PUBLISHED,
    description: 'Published and active documents',
  },
  {
    id: 'archived',
    label: 'Archived',
    icon: <Archive className="w-4 h-4" />,
    status: DocumentStatus.ARCHIVED,
    description: 'Archived documents',
  },
];

/**
 * View Mode Type
 */
type ViewMode = 'grid' | 'table';

/**
 * Create Dialog Step
 */
type CreateDialogStep = 'metadata' | 'upload' | 'closed';

export default function DocumentsPage() {
  const router = useRouter();

  // TODO: Get tenant_id and user_id from auth context when implemented
  const tenant_id = 'default-tenant';
  const user_id = 'current-user'; // FIXME: Replace with real user from auth

  // Tab state
  const [activeTab, setActiveTab] = useState<string>('all');

  // View mode state (persisted to localStorage)
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // Filter state
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    documentTypes: [],
    statuses: [],
    classifications: [],
    departments: [],
    owners: [],
    dateRange: {},
    search: '',
  });

  // Create dialog state
  const [createDialogStep, setCreateDialogStep] = useState<CreateDialogStep>('closed');
  const [createdDocumentId, setCreatedDocumentId] = useState<number | null>(null);

  // Load view mode from localStorage on mount
  useEffect(() => {
    const savedViewMode = localStorage.getItem('documents-view-mode') as ViewMode;
    if (savedViewMode === 'grid' || savedViewMode === 'table') {
      setViewMode(savedViewMode);
    }
  }, []);

  // Save view mode to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('documents-view-mode', viewMode);
  }, [viewMode]);

  // Build query params based on active tab and filters
  const queryParams = useMemo(() => {
    const params: any = {
      tenant_id,
      search: filters.search || undefined,
      document_type: filters.documentTypes[0] || undefined,
      classification: filters.classifications[0] || undefined,
      department: filters.departments[0] || undefined,
    };

    // Apply tab-specific filters
    const tab = TABS.find((t) => t.id === activeTab);

    if (tab?.status) {
      params.status = tab.status;
    } else if (activeTab === 'my-documents') {
      params.owner_id = user_id;
    }

    // Override with explicit filter status if set
    if (filters.statuses.length > 0) {
      params.status = filters.statuses[0];
    }

    // Override with explicit owner filter
    if (filters.owners.length > 0) {
      params.owner_id = filters.owners[0];
    }

    return params;
  }, [tenant_id, user_id, activeTab, filters]);

  // Fetch documents using the appropriate hook
  const { data, isLoading, error, refetch } = useDocuments(queryParams);

  // Calculate counts for each tab (simplified - in production, use separate count endpoints)
  const tabCounts = useMemo(() => {
    if (!data?.documents) return {};

    return {
      all: data.total,
      drafts: data.documents.filter((d) => d.status === DocumentStatus.DRAFT).length,
      'under-review': data.documents.filter((d) => d.status === DocumentStatus.UNDER_REVIEW)
        .length,
      published: data.documents.filter((d) => d.status === DocumentStatus.PUBLISHED).length,
      archived: data.documents.filter((d) => d.status === DocumentStatus.ARCHIVED).length,
      'my-documents': data.documents.filter((d) => d.owner_id === user_id).length,
    };
  }, [data, user_id]);

  // Handle filter changes
  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
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
  };

  // Handle document click
  const handleDocumentClick = (document: Document) => {
    router.push(`/documents/${document.document_id}`);
  };

  // Handle create document success
  const handleCreateSuccess = (documentId: number) => {
    setCreatedDocumentId(documentId);
    setCreateDialogStep('upload');
  };

  // Handle upload success
  const handleUploadSuccess = () => {
    setCreateDialogStep('closed');
    setCreatedDocumentId(null);
    toast.success('Document uploaded successfully');
    refetch();
    if (createdDocumentId) {
      router.push(`/documents/${createdDocumentId}`);
    }
  };

  // Handle skip upload
  const handleSkipUpload = () => {
    setCreateDialogStep('closed');
    toast.success('Document created (no file attached)');
    refetch();
    if (createdDocumentId) {
      router.push(`/documents/${createdDocumentId}`);
    }
    setCreatedDocumentId(null);
  };

  // Handle cancel create
  const handleCancelCreate = () => {
    setCreateDialogStep('closed');
    setCreatedDocumentId(null);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // C: Create document
      if (e.key === 'c' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          e.preventDefault();
          setCreateDialogStep('metadata');
        }
      }

      // F: Toggle filters
      if (e.key === 'f' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          e.preventDefault();
          setShowFilters((prev) => !prev);
        }
      }

      // G: Toggle grid/table
      if (e.key === 'g' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          e.preventDefault();
          setViewMode((prev) => (prev === 'grid' ? 'table' : 'grid'));
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Count active filters
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-[1800px] mx-auto p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Documents</h1>
            <p className="text-gray-600 mt-2">
              Manage your ISO compliance documentation
            </p>
          </div>

          <button
            onClick={() => setCreateDialogStep('metadata')}
            className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2 font-medium shadow-lg"
          >
            <Plus className="w-5 h-5" />
            Create Document
          </button>
        </div>

        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <a href="/" className="hover:text-orange-600 transition-colors">
            Home
          </a>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">Documents</span>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="border-b border-gray-200">
            <div className="flex overflow-x-auto">
              {TABS.map((tab) => {
                const isActive = activeTab === tab.id;
                const count = tabCounts[tab.id as keyof typeof tabCounts] || 0;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-6 py-4 border-b-2 transition-colors whitespace-nowrap ${
                      isActive
                        ? 'border-orange-600 text-orange-600 bg-orange-50'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                    title={tab.description}
                  >
                    {tab.icon}
                    <span className="font-medium">{tab.label}</span>
                    {count > 0 && (
                      <span
                        className={`px-2 py-0.5 text-xs rounded-full ${
                          isActive
                            ? 'bg-orange-600 text-white'
                            : 'bg-gray-200 text-gray-700'
                        }`}
                      >
                        {count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Controls Bar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documents by title, description, tags..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange({ search: e.target.value })}
                  className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
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

              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
                  showFilters
                    ? 'bg-orange-50 border-orange-600 text-orange-700'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Filter className="w-4 h-4" />
                Filters
                {activeFilterCount > 0 && (
                  <span className="px-2 py-0.5 bg-orange-600 text-white text-xs rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </button>

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
                  onClick={() => setViewMode('table')}
                  className={`p-2 border-l border-gray-300 ${
                    viewMode === 'table'
                      ? 'bg-orange-50 text-orange-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                  title="Table view"
                >
                  <ListIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex">
            {/* Filters Sidebar */}
            {showFilters && (
              <div className="w-80 border-r border-gray-200 bg-white overflow-y-auto max-h-[800px]">
                <DocumentFilters
                  filters={filters}
                  onChange={handleFilterChange}
                  onClear={handleClearFilters}
                />
              </div>
            )}

            {/* Document List/Table */}
            <div className="flex-1 overflow-y-auto max-h-[800px] bg-gray-50">
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
                    <AlertCircle className="w-8 h-8 text-red-600 mx-auto mb-3" />
                    <p className="text-red-800 font-medium">Error loading documents</p>
                    <p className="text-sm text-red-600 mt-2">
                      {error instanceof Error ? error.message : 'Unknown error'}
                    </p>
                    <button
                      onClick={() => refetch()}
                      className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                )}

                {/* Empty State */}
                {!isLoading && !error && (!data?.documents || data.documents.length === 0) && (
                  <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {activeFilterCount > 0 ? 'No documents found' : 'No documents yet'}
                    </h3>
                    <p className="text-gray-600 mb-6">
                      {activeFilterCount > 0
                        ? 'Try adjusting your filters or search terms'
                        : TABS.find((t) => t.id === activeTab)?.description ||
                          'Get started by creating your first document'}
                    </p>
                    <button
                      onClick={() => setCreateDialogStep('metadata')}
                      className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      Create Document
                    </button>
                  </div>
                )}

                {/* Document Grid */}
                {!isLoading &&
                  !error &&
                  data?.documents &&
                  data.documents.length > 0 &&
                  viewMode === 'grid' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {data.documents.map((document) => (
                        <DocumentCard
                          key={document.document_id}
                          document={document}
                          onClick={() => handleDocumentClick(document)}
                          layout="grid"
                        />
                      ))}
                    </div>
                  )}

                {/* Document Table */}
                {!isLoading &&
                  !error &&
                  data?.documents &&
                  data.documents.length > 0 &&
                  viewMode === 'table' && (
                    <DocumentTable
                      tenantId={tenant_id}
                      filters={queryParams}
                      onDocumentClick={handleDocumentClick}
                    />
                  )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create Document Dialog */}
      {createDialogStep === 'metadata' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Create Document</h2>
              <button
                onClick={handleCancelCreate}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6">
              <DocumentCreateForm
                tenantId={tenant_id}
                userId={user_id}
                onSuccess={handleCreateSuccess}
                onCancel={handleCancelCreate}
              />
            </div>
          </div>
        </div>
      )}

      {/* Upload Document Dialog */}
      {createDialogStep === 'upload' && createdDocumentId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Upload File (Optional)</h2>
              <button
                onClick={handleSkipUpload}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6">
              <DocumentUploadForm
                documentId={createdDocumentId}
                userId={user_id}
                onSuccess={handleUploadSuccess}
                onCancel={handleSkipUpload}
              />
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Hint */}
      <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-xs text-gray-600 opacity-60 hover:opacity-100 transition-opacity">
        <div className="font-semibold mb-1">Keyboard Shortcuts</div>
        <div className="space-y-0.5">
          <div>
            <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded">C</kbd>{' '}
            Create
          </div>
          <div>
            <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded">F</kbd>{' '}
            Filters
          </div>
          <div>
            <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded">G</kbd>{' '}
            Toggle view
          </div>
        </div>
      </div>
    </div>
  );
}
