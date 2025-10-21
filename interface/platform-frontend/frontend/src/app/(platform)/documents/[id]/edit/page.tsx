'use client';

/**
 * Edit Document Page
 * Edit existing document metadata with option to upload new version
 * Week 4 Documents Module - AI Platform ISO Project
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  ArrowLeft,
  Edit,
  Upload,
  ChevronRight,
  AlertCircle,
  Loader2,
  FileText,
  Download,
  Calendar,
  User,
  Shield,
  HardDrive,
  CheckCircle,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Hooks
import { useDocument } from '@/hooks/documents/useDocument';
import { useUploadFile } from '@/hooks/documents/useCreateDocument';

// Components
import { DocumentMetadataForm } from '@/components/documents/forms/DocumentMetadataForm';
import { DocumentTypeIcon } from '@/components/documents/DocumentTypeIcon';
import { DocumentStatusBadge } from '@/components/documents/DocumentStatusBadge';

// Types
import type { DocumentClassification } from '@/types/documents';

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
  if (!bytes) return 'No file';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

/**
 * Edit Document Page Component
 */
export default function EditDocumentPage({ params }: PageProps) {
  const router = useRouter();
  const documentId = parseInt(params.id, 10);

  // TODO: Get actual user_id from auth context
  const currentUserId = 'current-user';

  // State
  const [showReplaceFile, setShowReplaceFile] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Fetch document data
  const {
    data: document,
    isLoading: documentLoading,
    error: documentError,
    refetch,
  } = useDocument({ id: documentId, user_id: currentUserId });

  // File upload mutation
  const uploadFile = useUploadFile({
    onSuccess: () => {
      toast.success('File uploaded successfully');
      setUploadProgress(100);
      setShowReplaceFile(false);
      setSelectedFile(null);
      refetch();
      setTimeout(() => setUploadProgress(0), 1000);
    },
    onError: (error) => {
      toast.error(`Upload failed: ${error.message}`);
      setUploadProgress(0);
    },
  });

  // Permission checks
  const isOwner = document?.owner_id === currentUserId;
  const canEdit = isOwner; // TODO: Add role-based permissions

  // Warn before leaving if there are unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  /**
   * Handle file selection for replacement
   */
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  /**
   * Handle file upload
   */
  const handleUploadFile = async () => {
    if (!selectedFile) return;

    // Simulate progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    uploadFile.mutate({
      documentId,
      file: selectedFile,
      userId: currentUserId,
      autoProcess: true,
    });
  };

  /**
   * Handle successful metadata update
   */
  const handleMetadataSuccess = () => {
    setHasUnsavedChanges(false);
    toast.success('Document updated successfully');
    setTimeout(() => {
      router.push(`/documents/${documentId}`);
    }, 500);
  };

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    if (hasUnsavedChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
        router.push(`/documents/${documentId}`);
      }
    } else {
      router.push(`/documents/${documentId}`);
    }
  };

  /**
   * Handle download current file
   */
  const handleDownload = () => {
    if (!document) return;
    // TODO: Implement actual download
    toast.success('Download started');
    console.log('Downloading document:', document.file_path);
  };

  // Loading state
  if (documentLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-64 bg-gray-200 rounded" />
            <div className="h-12 w-96 bg-gray-200 rounded" />
            <div className="h-96 bg-white rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (documentError || !document) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-5xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Not Found</h1>
            <p className="text-gray-600 mb-6">
              {documentError
                ? (documentError as Error).message
                : 'The document you are trying to edit does not exist.'}
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

  // Permission check
  if (!canEdit) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-5xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Shield className="w-16 h-16 text-orange-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Permission Denied</h1>
            <p className="text-gray-600 mb-6">
              You do not have permission to edit this document. Only the document owner can make
              changes.
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => router.push('/documents')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Back to Documents
              </button>
              <button
                onClick={() => router.push(`/documents/${documentId}`)}
                className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
              >
                View Document
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-5xl mx-auto p-8 space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-orange-600 transition-colors"
          >
            Home
          </button>
          <ChevronRight className="w-4 h-4" />
          <button
            onClick={() => router.push('/documents')}
            className="hover:text-orange-600 transition-colors"
          >
            Documents
          </button>
          <ChevronRight className="w-4 h-4" />
          <button
            onClick={() => router.push(`/documents/${documentId}`)}
            className="hover:text-orange-600 transition-colors truncate max-w-xs"
          >
            {document.title}
          </button>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">Edit</span>
        </div>

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push(`/documents/${documentId}`)}
              className="p-2 hover:bg-white rounded-lg transition-colors"
              aria-label="Back to document"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Edit Document</h1>
              <p className="text-gray-600 mt-2">Update document metadata and replace file</p>
            </div>
          </div>
        </div>

        {/* Document Summary Card */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start gap-4">
            <DocumentTypeIcon type={document.document_type} className="w-12 h-12" />
            <div className="flex-1 min-w-0">
              <h2 className="text-2xl font-bold text-gray-900 truncate">{document.title}</h2>
              <div className="flex items-center gap-3 flex-wrap mt-2">
                <DocumentStatusBadge status={document.status} />
                <div
                  className={`px-3 py-1 rounded-full text-sm font-medium border ${getClassificationColor(
                    document.classification
                  )}`}
                >
                  {document.classification.replace('_', ' ')}
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Calendar className="w-4 h-4" />
                  v{document.version}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Info Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-400" />
              <div>
                <div className="text-xs text-gray-500">Owner</div>
                <div className="text-sm font-medium text-gray-900">{document.owner_id}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <div>
                <div className="text-xs text-gray-500">Updated</div>
                <div className="text-sm font-medium text-gray-900">
                  {format(new Date(document.updated_at), 'MMM d, yyyy')}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-gray-400" />
              <div>
                <div className="text-xs text-gray-500">File Size</div>
                <div className="text-sm font-medium text-gray-900">
                  {formatFileSize(document.file_size)}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-gray-400" />
              <div>
                <div className="text-xs text-gray-500">Format</div>
                <div className="text-sm font-medium text-gray-900">
                  {document.file_type || 'Unknown'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Edit Form */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="border-b border-gray-200 bg-gray-50 px-6 py-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Edit className="w-5 h-5 text-orange-600" />
              Edit Metadata
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Update document information, classification, and tags
            </p>
          </div>

          <div className="p-6">
            <DocumentMetadataForm
              document={document}
              onSuccess={handleMetadataSuccess}
              onCancel={handleCancel}
            />
          </div>
        </div>

        {/* File Replacement Section */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="border-b border-gray-200 bg-gray-50 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <Upload className="w-5 h-5 text-orange-600" />
                  Document File
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  View current file or upload a new version
                </p>
              </div>
              {document.file_path && (
                <button
                  onClick={handleDownload}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2 text-sm"
                >
                  <Download className="w-4 h-4" />
                  Download Current
                </button>
              )}
            </div>
          </div>

          <div className="p-6">
            {/* Current File Info */}
            {document.file_path ? (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-4">
                  <FileText className="w-10 h-10 text-blue-600" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {document.file_name}
                    </p>
                    <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                      <span>{formatFileSize(document.file_size)}</span>
                      <span>{document.file_type}</span>
                      <span>
                        Uploaded {format(new Date(document.created_at), 'MMM d, yyyy')}
                      </span>
                    </div>
                  </div>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-yellow-900">No file attached</p>
                    <p className="text-sm text-yellow-700 mt-1">
                      This document has metadata but no file. Upload one below.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Replace File Section */}
            {!showReplaceFile ? (
              <button
                onClick={() => setShowReplaceFile(true)}
                className="w-full px-4 py-3 border-2 border-dashed border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:border-orange-400 transition-colors flex items-center justify-center gap-2"
              >
                <Upload className="w-5 h-5" />
                {document.file_path ? 'Upload New Version' : 'Upload File'}
              </button>
            ) : (
              <div className="space-y-4">
                {/* File Input */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <input
                    type="file"
                    onChange={handleFileSelect}
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.md"
                    className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, MD (Max 50MB)
                  </p>
                </div>

                {/* Selected File Preview */}
                {selectedFile && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <FileText className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-blue-900 truncate">
                          {selectedFile.name}
                        </p>
                        <p className="text-xs text-blue-700 mt-1">
                          {formatFileSize(selectedFile.size)}
                        </p>
                      </div>
                      <button
                        onClick={() => setSelectedFile(null)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}

                {/* Upload Progress */}
                {uploadProgress > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-700">Uploading...</span>
                      <span className="text-gray-500">{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-orange-600 h-full rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={handleUploadFile}
                    disabled={!selectedFile || uploadFile.isPending}
                    className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {uploadFile.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Upload File
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setShowReplaceFile(false);
                      setSelectedFile(null);
                    }}
                    disabled={uploadFile.isPending}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
