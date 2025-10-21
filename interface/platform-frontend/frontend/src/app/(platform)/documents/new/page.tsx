'use client';

/**
 * Create New Document Page
 * Two-step process: 1) Create metadata, 2) Upload file (optional)
 * Week 4 Documents Module - AI Platform ISO Project
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  FileText,
  Upload,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  Save,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Components
import { DocumentCreateForm } from '@/components/documents/forms/DocumentCreateForm';
import { DocumentUploadForm } from '@/components/documents/forms/DocumentUploadForm';

// Types
type CreateStep = 'metadata' | 'upload' | 'complete';

/**
 * New Document Page
 * Handles document creation workflow with metadata and file upload
 */
export default function NewDocumentPage() {
  const router = useRouter();

  // TODO: Get tenant_id and user_id from auth context when implemented
  const tenant_id = 'default-tenant';
  const user_id = 'current-user';

  // State
  const [currentStep, setCurrentStep] = useState<CreateStep>('metadata');
  const [createdDocumentId, setCreatedDocumentId] = useState<number | null>(null);
  const [showExitConfirm, setShowExitConfirm] = useState(false);

  // Warn before leaving if document is partially created
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (currentStep !== 'complete' && createdDocumentId) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [currentStep, createdDocumentId]);

  /**
   * Handle successful document metadata creation
   * Moves to upload step with the created document ID
   */
  const handleMetadataSuccess = (documentId: number) => {
    setCreatedDocumentId(documentId);
    setCurrentStep('upload');
    toast.success('Document created successfully');
  };

  /**
   * Handle successful file upload
   * Redirects to document detail page
   */
  const handleUploadSuccess = () => {
    setCurrentStep('complete');
    toast.success('File uploaded successfully');

    // Navigate to document detail page
    if (createdDocumentId) {
      setTimeout(() => {
        router.push(`/documents/${createdDocumentId}`);
      }, 1000);
    }
  };

  /**
   * Skip file upload and complete creation
   * Creates metadata-only document
   */
  const handleSkipUpload = () => {
    setCurrentStep('complete');
    toast.success('Document created (no file attached)');

    // Navigate to document detail page
    if (createdDocumentId) {
      setTimeout(() => {
        router.push(`/documents/${createdDocumentId}`);
      }, 1000);
    }
  };

  /**
   * Cancel creation and navigate back
   * Shows confirmation if document was partially created
   */
  const handleCancel = () => {
    if (createdDocumentId && currentStep !== 'complete') {
      setShowExitConfirm(true);
    } else {
      router.push('/documents');
    }
  };

  /**
   * Confirm exit without uploading file
   */
  const handleConfirmExit = () => {
    toast.success('Document saved without file');
    router.push('/documents');
  };

  /**
   * Go back to previous step
   */
  const handleBack = () => {
    if (currentStep === 'upload') {
      setCurrentStep('metadata');
      setCreatedDocumentId(null);
    } else {
      router.push('/documents');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-4xl mx-auto p-8 space-y-6">
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
          <span className="text-gray-900 font-medium">New Document</span>
        </div>

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={handleBack}
              className="p-2 hover:bg-white rounded-lg transition-colors"
              aria-label="Back"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Create New Document</h1>
              <p className="text-gray-600 mt-2">
                {currentStep === 'metadata'
                  ? 'Enter document metadata and details'
                  : currentStep === 'upload'
                  ? 'Upload document file (optional)'
                  : 'Document created successfully'}
              </p>
            </div>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            {/* Step 1: Metadata */}
            <div className="flex items-center gap-3 flex-1">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep === 'metadata'
                    ? 'border-orange-600 bg-orange-50 text-orange-600'
                    : currentStep === 'upload' || currentStep === 'complete'
                    ? 'border-green-600 bg-green-50 text-green-600'
                    : 'border-gray-300 bg-white text-gray-400'
                }`}
              >
                {currentStep === 'upload' || currentStep === 'complete' ? (
                  <CheckCircle className="w-6 h-6" />
                ) : (
                  <FileText className="w-5 h-5" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-gray-900">Document Metadata</div>
                <div className="text-xs text-gray-500">Basic information</div>
              </div>
            </div>

            {/* Connector Line */}
            <div className="flex-1 mx-4">
              <div
                className={`h-0.5 ${
                  currentStep === 'upload' || currentStep === 'complete'
                    ? 'bg-green-600'
                    : 'bg-gray-300'
                }`}
              />
            </div>

            {/* Step 2: Upload */}
            <div className="flex items-center gap-3 flex-1">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep === 'upload'
                    ? 'border-orange-600 bg-orange-50 text-orange-600'
                    : currentStep === 'complete'
                    ? 'border-green-600 bg-green-50 text-green-600'
                    : 'border-gray-300 bg-white text-gray-400'
                }`}
              >
                {currentStep === 'complete' ? (
                  <CheckCircle className="w-6 h-6" />
                ) : (
                  <Upload className="w-5 h-5" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-gray-900">Upload File</div>
                <div className="text-xs text-gray-500">Optional</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="p-8">
            {/* Step 1: Metadata Form */}
            {currentStep === 'metadata' && (
              <div className="space-y-6">
                <div className="border-b border-gray-200 pb-4">
                  <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <FileText className="w-6 h-6 text-orange-600" />
                    Document Information
                  </h2>
                  <p className="text-gray-600 mt-2">
                    Fill in the required metadata for your document. You can add a file in the next
                    step.
                  </p>
                </div>

                <DocumentCreateForm
                  tenantId={tenant_id}
                  userId={user_id}
                  onSuccess={handleMetadataSuccess}
                  onCancel={handleCancel}
                />
              </div>
            )}

            {/* Step 2: File Upload */}
            {currentStep === 'upload' && createdDocumentId && (
              <div className="space-y-6">
                <div className="border-b border-gray-200 pb-4">
                  <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <Upload className="w-6 h-6 text-orange-600" />
                    Upload Document File
                  </h2>
                  <p className="text-gray-600 mt-2">
                    Upload the document file or skip to complete creation without a file.
                  </p>
                </div>

                {/* Success message for metadata */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-900">
                      Document metadata created successfully
                    </p>
                    <p className="text-sm text-green-700 mt-1">
                      Document ID: {createdDocumentId}
                    </p>
                  </div>
                </div>

                <DocumentUploadForm
                  documentId={createdDocumentId}
                  userId={user_id}
                  onSuccess={handleUploadSuccess}
                  onCancel={handleSkipUpload}
                />

                {/* Skip Upload Button */}
                <div className="pt-4 border-t border-gray-200">
                  <button
                    onClick={handleSkipUpload}
                    className="w-full px-4 py-3 border-2 border-dashed border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors flex items-center justify-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    Skip Upload and Save Document
                  </button>
                  <p className="text-xs text-gray-500 text-center mt-2">
                    You can add a file later from the document detail page
                  </p>
                </div>
              </div>
            )}

            {/* Step 3: Complete */}
            {currentStep === 'complete' && (
              <div className="text-center py-12">
                <div className="flex justify-center mb-6">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-10 h-10 text-green-600" />
                  </div>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Document Created Successfully!
                </h2>
                <p className="text-gray-600 mb-8">Redirecting to document details...</p>

                <div className="flex gap-3 justify-center">
                  <button
                    onClick={() => router.push('/documents')}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Back to Documents
                  </button>
                  {createdDocumentId && (
                    <button
                      onClick={() => router.push(`/documents/${createdDocumentId}`)}
                      className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                    >
                      View Document
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Help Text */}
        {currentStep === 'metadata' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-blue-900">Quick Tips</h3>
                <ul className="text-sm text-blue-800 mt-2 space-y-1 list-disc list-inside">
                  <li>Choose a clear, descriptive title for easy searching</li>
                  <li>Select the appropriate classification level for access control</li>
                  <li>Add relevant tags to improve discoverability</li>
                  <li>You can upload a file in the next step or skip it for now</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Exit Confirmation Dialog */}
      {showExitConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-orange-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Leave Without Uploading?
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Your document metadata has been saved, but no file has been uploaded yet. You can
                  add a file later from the document detail page.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowExitConfirm(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Continue Editing
                  </button>
                  <button
                    onClick={handleConfirmExit}
                    className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                  >
                    Leave
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
