'use client';

/**
 * DocumentUploadForm Component
 * File upload with drag-and-drop, validation, and progress tracking
 * Supports PDF, DOCX, XLSX, PPTX, TXT, MD files
 */

import { useState, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
  Upload,
  File,
  FileText,
  FileSpreadsheet,
  Presentation,
  X,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

import { useUploadFile } from '@/hooks/documents/useCreateDocument';
import { validateFileSize, validateFileType } from '@/lib/validations/document';

interface DocumentUploadFormProps {
  documentId: number;
  userId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
  maxSizeMB?: number;
  allowedTypes?: string[];
}

const ALLOWED_TYPES = ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt', 'md'];

const FILE_TYPE_ICONS: Record<string, any> = {
  pdf: FileText,
  docx: FileText,
  doc: FileText,
  xlsx: FileSpreadsheet,
  xls: FileSpreadsheet,
  pptx: Presentation,
  ppt: Presentation,
  txt: File,
  md: File,
};

export function DocumentUploadForm({
  documentId,
  userId,
  onSuccess,
  onCancel,
  maxSizeMB = 50,
  allowedTypes = ALLOWED_TYPES,
}: DocumentUploadFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [autoProcess, setAutoProcess] = useState(true);
  const [validationError, setValidationError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFile = useUploadFile({
    onSuccess: () => {
      toast.success('File uploaded successfully');
      setUploadProgress(100);
      setTimeout(() => {
        onSuccess?.();
      }, 500);
    },
    onError: (error) => {
      toast.error(`Upload failed: ${error.message}`);
      setUploadProgress(0);
    },
  });

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!validateFileType(file.name, allowedTypes)) {
      return `File type not supported. Allowed types: ${allowedTypes.join(', ').toUpperCase()}`;
    }

    // Check file size
    if (!validateFileSize(file.size, maxSizeMB)) {
      return `File size exceeds ${maxSizeMB}MB limit`;
    }

    return null;
  };

  const handleFileSelect = useCallback(
    (file: File) => {
      const error = validateFile(file);
      if (error) {
        setValidationError(error);
        setSelectedFile(null);
        return;
      }

      setValidationError(null);
      setSelectedFile(file);
      setUploadProgress(0);
    },
    [maxSizeMB, allowedTypes]
  );

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    // Simulate progress for UX (real implementation would use upload progress events)
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
      userId,
      autoProcess,
    });
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    const Icon = extension ? FILE_TYPE_ICONS[extension] || File : File;
    return Icon;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const isUploading = uploadFile.isPending;
  const isUploadComplete = uploadProgress === 100;

  return (
    <div className="space-y-6">
      {/* Drag and Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${selectedFile ? 'bg-gray-50' : 'bg-white'}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileInputChange}
          accept={allowedTypes.map((type) => `.${type}`).join(',')}
          className="hidden"
          disabled={isUploading}
          aria-label="File input"
        />

        {!selectedFile ? (
          <div className="space-y-4">
            <div className="flex justify-center">
              <Upload className="h-12 w-12 text-gray-400" />
            </div>
            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragging ? 'Drop file here' : 'Drag and drop your file here'}
              </p>
              <p className="text-sm text-gray-500 mt-1">or</p>
            </div>
            <button
              type="button"
              onClick={handleBrowseClick}
              disabled={isUploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Browse Files
            </button>
            <div className="text-xs text-gray-500 mt-4">
              <p>Supported formats: {allowedTypes.join(', ').toUpperCase()}</p>
              <p className="mt-1">Maximum file size: {maxSizeMB}MB</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* File Preview */}
            <div className="flex items-start gap-4 p-4 bg-white border border-gray-200 rounded-md">
              <div className="flex-shrink-0">
                {isUploadComplete ? (
                  <CheckCircle2 className="h-10 w-10 text-green-500" />
                ) : (
                  (() => {
                    const Icon = getFileIcon(selectedFile.name);
                    return <Icon className="h-10 w-10 text-blue-500" />;
                  })()
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                <p className="text-xs text-gray-400 mt-1">
                  Type: {selectedFile.type || 'Unknown'}
                </p>
              </div>
              {!isUploading && !isUploadComplete && (
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="flex-shrink-0 text-gray-400 hover:text-gray-600"
                  aria-label="Remove file"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>

            {/* Upload Progress */}
            {(isUploading || isUploadComplete) && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">
                    {isUploadComplete ? 'Upload complete' : 'Uploading...'}
                  </span>
                  <span className="text-gray-500">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-600 h-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Validation Error */}
      {validationError && (
        <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{validationError}</p>
        </div>
      )}

      {/* Auto-process Option */}
      {selectedFile && !isUploadComplete && (
        <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <input
            type="checkbox"
            id="autoProcess"
            checked={autoProcess}
            onChange={(e) => setAutoProcess(e.target.checked)}
            disabled={isUploading}
            className="mt-0.5 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <label htmlFor="autoProcess" className="flex-1 text-sm">
            <span className="font-medium text-gray-900">Auto-extract metadata</span>
            <p className="text-gray-600 mt-1">
              Automatically extract document information using AI processing (recommended)
            </p>
          </label>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || isUploading || isUploadComplete || !!validationError}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isUploading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : isUploadComplete ? (
            <>
              <CheckCircle2 className="h-4 w-4" />
              Upload Complete
            </>
          ) : (
            <>
              <Upload className="h-4 w-4" />
              Upload File
            </>
          )}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isUploading}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
