/**
 * VersionComparison Component
 * Side-by-side comparison of two document versions
 * Week 4 - Documents Module
 */

'use client';

import { useCompareVersions } from '@/hooks/documents/useDocumentVersions';
import { Document, VersionComparison as ComparisonData } from '@/types/documents';
import { cn } from '@/lib/utils';
import {
  GitCompare,
  Download,
  FileText,
  Calendar,
  User,
  Lock,
  AlertCircle,
  Loader2,
  CheckCircle,
  XCircle,
  Info,
  Printer,
  TrendingUp,
} from 'lucide-react';
import { format } from 'date-fns';
import { useState } from 'react';

export interface VersionComparisonProps {
  documentId: number;
  version1: number;
  version2: number;
  userId: string;
  onDownloadVersion?: (versionId: number) => void;
  onClose?: () => void;
  className?: string;
}

/**
 * Format file size to human-readable format
 */
function formatFileSize(bytes: number | null): string {
  if (!bytes) return 'N/A';

  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';

  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, i);

  return `${size.toFixed(1)} ${sizes[i]}`;
}

/**
 * Get similarity score color
 */
function getSimilarityColor(score: number): string {
  if (score >= 90) return 'text-green-700 bg-green-100 border-green-300';
  if (score >= 70) return 'text-blue-700 bg-blue-100 border-blue-300';
  if (score >= 50) return 'text-amber-700 bg-amber-100 border-amber-300';
  return 'text-red-700 bg-red-100 border-red-300';
}

/**
 * MetadataRow - Display a single metadata field comparison
 */
interface MetadataRowProps {
  label: string;
  value1: any;
  value2: any;
  isDifferent: boolean;
}

function MetadataRow({ label, value1, value2, isDifferent }: MetadataRowProps) {
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (Array.isArray(value)) return value.join(', ') || 'None';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  return (
    <div
      className={cn(
        'grid grid-cols-3 gap-4 py-3 border-b border-gray-200',
        isDifferent && 'bg-amber-50'
      )}
    >
      <div className="font-medium text-gray-700 flex items-center gap-2">
        {label}
        {isDifferent && (
          <AlertCircle className="w-4 h-4 text-amber-600" aria-label="Different values" />
        )}
      </div>
      <div className={cn('text-gray-900', isDifferent && 'font-semibold')}>
        {formatValue(value1)}
      </div>
      <div className={cn('text-gray-900', isDifferent && 'font-semibold')}>
        {formatValue(value2)}
      </div>
    </div>
  );
}

/**
 * VersionPane - Display single version details
 */
interface VersionPaneProps {
  version: Document;
  title: string;
  onDownload?: () => void;
}

function VersionPane({ version, title, onDownload }: VersionPaneProps) {
  return (
    <div className="flex-1 min-w-0">
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="text-sm opacity-90">Version {version.version}</p>
          </div>
          {onDownload && (
            <button
              onClick={onDownload}
              className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-colors"
              title="Download this version"
              aria-label="Download this version"
            >
              <Download className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      <div className="bg-white border border-t-0 border-gray-200 p-4 rounded-b-lg space-y-3">
        {/* Document Code */}
        <div>
          <span className="text-sm text-gray-500">Document Code</span>
          <p className="text-sm font-medium text-gray-900">{version.document_code}</p>
        </div>

        {/* Title */}
        <div>
          <span className="text-sm text-gray-500">Title</span>
          <p className="text-sm font-medium text-gray-900">{version.title}</p>
        </div>

        {/* Created */}
        <div className="flex items-center gap-2 text-sm">
          <Calendar className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">
            {format(new Date(version.created_at), 'MMM d, yyyy HH:mm')}
          </span>
        </div>

        {/* Author */}
        <div className="flex items-center gap-2 text-sm">
          <User className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">{version.created_by}</span>
        </div>

        {/* File Info */}
        <div className="flex items-center gap-2 text-sm">
          <FileText className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">
            {formatFileSize(version.file_size)} • {version.file_type?.toUpperCase() || 'N/A'}
          </span>
        </div>

        {/* Status Badge */}
        <div>
          <span
            className={cn(
              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
              version.status === 'published' && 'bg-green-100 text-green-700 border border-green-300',
              version.status === 'draft' && 'bg-gray-100 text-gray-700 border border-gray-300',
              version.status === 'approved' && 'bg-blue-100 text-blue-700 border border-blue-300',
              version.status === 'archived' && 'bg-amber-100 text-amber-700 border border-amber-300'
            )}
          >
            {version.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>

        {/* Classification */}
        {version.classification && (
          <div className="flex items-center gap-2 text-sm">
            <Lock className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600 capitalize">
              {version.classification.replace('_', ' ')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * DiffView - Display text differences
 */
interface DiffViewProps {
  changes: ComparisonData['diff_json'];
}

function DiffView({ changes }: DiffViewProps) {
  if (!changes || typeof changes !== 'object') {
    return (
      <div className="text-center py-8 text-gray-500">
        <Info className="w-8 h-8 mx-auto mb-2 text-gray-400" />
        <p>No detailed diff available</p>
      </div>
    );
  }

  // Render diff blocks (simplified version)
  return (
    <div className="space-y-2 font-mono text-sm">
      {Object.entries(changes).map(([key, value], index) => (
        <div key={index} className="p-2 bg-gray-50 rounded border border-gray-200">
          <div className="font-semibold text-gray-700 mb-1">{key}</div>
          <div className="text-gray-900">{JSON.stringify(value, null, 2)}</div>
        </div>
      ))}
    </div>
  );
}

/**
 * VersionComparison - Main component
 */
export function VersionComparison({
  documentId,
  version1,
  version2,
  userId,
  onDownloadVersion,
  onClose,
  className,
}: VersionComparisonProps) {
  const [activeTab, setActiveTab] = useState<'metadata' | 'content'>('metadata');

  // Fetch comparison data
  const {
    data: comparison,
    isLoading,
    isError,
    error,
    refetch,
  } = useCompareVersions(version1, version2, userId);

  // Handle print
  const handlePrint = () => {
    window.print();
  };

  // Handle download both versions
  const handleDownloadBoth = () => {
    if (onDownloadVersion) {
      onDownloadVersion(version1);
      setTimeout(() => onDownloadVersion(version2), 500);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-xl border shadow-lg p-12', className)}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <Loader2 className="w-12 h-12 animate-spin text-orange-500" />
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Analyzing Versions...
            </h3>
            <p className="text-gray-600">
              Our AI is comparing the documents. This may take a moment.
            </p>
          </div>
          {/* Progress skeleton */}
          <div className="w-full max-w-md space-y-3 mt-8">
            <div className="h-4 bg-gray-100 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-100 rounded animate-pulse w-3/4"></div>
            <div className="h-4 bg-gray-100 rounded animate-pulse w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (isError || !comparison) {
    return (
      <div className={cn('bg-white rounded-xl border shadow-lg p-12', className)}>
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Failed to Compare Versions
          </h3>
          <p className="text-gray-600 mb-6">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => refetch()}
              className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              Try Again
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Get version documents from comparison metadata
  const doc1 = comparison.metadata_changes?.source_document as Document | undefined;
  const doc2 = comparison.metadata_changes?.target_document as Document | undefined;

  return (
    <div className={cn('bg-white rounded-xl border shadow-lg', className)}>
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <GitCompare className="w-6 h-6 text-orange-500" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Version Comparison</h2>
              <p className="text-sm text-gray-600 mt-1">
                Comparing version {version1} with version {version2}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              title="Print comparison"
            >
              <Printer className="w-4 h-4" />
              Print
            </button>
            {onDownloadVersion && (
              <button
                onClick={handleDownloadBoth}
                className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                title="Download both versions"
              >
                <Download className="w-4 h-4" />
                Download Both
              </button>
            )}
            {onClose && (
              <button
                onClick={onClose}
                className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Close
              </button>
            )}
          </div>
        </div>

        {/* Similarity Score */}
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Similarity Score</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-orange-500 to-amber-500 transition-all duration-500"
                style={{ width: `${comparison.similarity_score}%` }}
              ></div>
            </div>
          </div>
          <div
            className={cn(
              'px-4 py-2 rounded-lg border font-bold text-2xl',
              getSimilarityColor(comparison.similarity_score)
            )}
          >
            {comparison.similarity_score.toFixed(1)}%
          </div>
        </div>

        {/* Change Summary */}
        {comparison.changes_summary && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <Info className="w-4 h-4" />
              AI Change Summary
            </h3>
            <p className="text-sm text-blue-800">{comparison.changes_summary}</p>
          </div>
        )}

        {/* Stats */}
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm text-green-800 font-medium">Text Added</p>
                <p className="text-2xl font-bold text-green-900">{comparison.text_added}</p>
              </div>
            </div>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-sm text-red-800 font-medium">Text Removed</p>
                <p className="text-2xl font-bold text-red-900">{comparison.text_removed}</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-800 font-medium">Text Modified</p>
                <p className="text-2xl font-bold text-blue-900">{comparison.text_modified}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setActiveTab('metadata')}
            className={cn(
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'metadata'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            )}
          >
            Metadata Differences
          </button>
          <button
            onClick={() => setActiveTab('content')}
            className={cn(
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'content'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            )}
          >
            Content Diff
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'metadata' && doc1 && doc2 ? (
          <div>
            {/* Side-by-side version preview */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <VersionPane
                version={doc1}
                title="Older Version"
                onDownload={onDownloadVersion ? () => onDownloadVersion(version1) : undefined}
              />
              <VersionPane
                version={doc2}
                title="Newer Version"
                onDownload={onDownloadVersion ? () => onDownloadVersion(version2) : undefined}
              />
            </div>

            {/* Metadata comparison table */}
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="bg-gray-50 border-b border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900">Metadata Comparison</h3>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-3 gap-4 pb-3 border-b-2 border-gray-300 font-semibold text-gray-700">
                  <div>Field</div>
                  <div>Version {version1}</div>
                  <div>Version {version2}</div>
                </div>
                <MetadataRow
                  label="Title"
                  value1={doc1.title}
                  value2={doc2.title}
                  isDifferent={doc1.title !== doc2.title}
                />
                <MetadataRow
                  label="Owner"
                  value1={doc1.owner_id}
                  value2={doc2.owner_id}
                  isDifferent={doc1.owner_id !== doc2.owner_id}
                />
                <MetadataRow
                  label="Classification"
                  value1={doc1.classification}
                  value2={doc2.classification}
                  isDifferent={doc1.classification !== doc2.classification}
                />
                <MetadataRow
                  label="Status"
                  value1={doc1.status}
                  value2={doc2.status}
                  isDifferent={doc1.status !== doc2.status}
                />
                <MetadataRow
                  label="Department"
                  value1={doc1.department}
                  value2={doc2.department}
                  isDifferent={doc1.department !== doc2.department}
                />
                <MetadataRow
                  label="File Name"
                  value1={doc1.file_name}
                  value2={doc2.file_name}
                  isDifferent={doc1.file_name !== doc2.file_name}
                />
                <MetadataRow
                  label="File Size"
                  value1={formatFileSize(doc1.file_size)}
                  value2={formatFileSize(doc2.file_size)}
                  isDifferent={doc1.file_size !== doc2.file_size}
                />
                <MetadataRow
                  label="Tags"
                  value1={doc1.tags}
                  value2={doc2.tags}
                  isDifferent={JSON.stringify(doc1.tags) !== JSON.stringify(doc2.tags)}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p>Metadata not available for comparison</p>
          </div>
        )}

        {activeTab === 'content' && (
          <div>
            <DiffView changes={comparison.diff_json} />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center gap-4">
            <span>
              Processing time: {comparison.processing_time_ms}ms
            </span>
            <span>
              Compared: {format(new Date(comparison.compared_at), 'PPpp')}
            </span>
          </div>
          <div className="text-xs text-gray-500">
            Comparison ID: {comparison.comparison_id}
          </div>
        </div>
      </div>
    </div>
  );
}
