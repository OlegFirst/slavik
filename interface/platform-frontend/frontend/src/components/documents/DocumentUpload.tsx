/**
 * DocumentUpload Component
 * Reusable file upload component with drag-and-drop support
 * Week 4 Documents Module - AI Platform ISO Project
 */

'use client';

import React, { useState, useRef, useCallback, ChangeEvent, DragEvent } from 'react';
import {
  Upload,
  File,
  FileText,
  Image as ImageIcon,
  X,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface DocumentUploadProps {
  onFileSelect: (file: File) => void;
  maxSize?: number; // in MB
  accept?: string;
  className?: string;
  multiple?: boolean;
  disabled?: boolean;
}

interface FilePreview {
  file: File;
  preview?: string; // For image previews
}

const DEFAULT_MAX_SIZE = 50; // 50MB
const DEFAULT_ACCEPT = '.pdf,.docx,.doc,.xlsx,.xls,.ppt,.pptx,.png,.jpg,.jpeg';

const ACCEPTED_FILE_TYPES = {
  'application/pdf': { ext: 'PDF', icon: FileText, color: 'text-red-500' },
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {
    ext: 'DOCX',
    icon: FileText,
    color: 'text-blue-500',
  },
  'application/msword': { ext: 'DOC', icon: FileText, color: 'text-blue-500' },
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
    ext: 'XLSX',
    icon: FileText,
    color: 'text-green-500',
  },
  'application/vnd.ms-excel': { ext: 'XLS', icon: FileText, color: 'text-green-500' },
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': {
    ext: 'PPTX',
    icon: FileText,
    color: 'text-orange-500',
  },
  'application/vnd.ms-powerpoint': {
    ext: 'PPT',
    icon: FileText,
    color: 'text-orange-500',
  },
  'image/png': { ext: 'PNG', icon: ImageIcon, color: 'text-purple-500' },
  'image/jpeg': { ext: 'JPG', icon: ImageIcon, color: 'text-purple-500' },
  'image/jpg': { ext: 'JPG', icon: ImageIcon, color: 'text-purple-500' },
};

/**
 * Format file size in human-readable format
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Get file type configuration
 */
function getFileTypeConfig(mimeType: string) {
  return (
    ACCEPTED_FILE_TYPES[mimeType as keyof typeof ACCEPTED_FILE_TYPES] || {
      ext: 'FILE',
      icon: File,
      color: 'text-gray-500',
    }
  );
}

/**
 * DocumentUpload - Drag-and-drop file upload component
 *
 * Features:
 * - Drag-and-drop zone with visual feedback
 * - Click to browse files
 * - File preview with name, size, and type
 * - File validation (size and type)
 * - Image thumbnail preview
 * - Multiple file support
 * - Remove/change file
 * - Accessible keyboard navigation
 */
export function DocumentUpload({
  onFileSelect,
  maxSize = DEFAULT_MAX_SIZE,
  accept = DEFAULT_ACCEPT,
  className,
  multiple = false,
  disabled = false,
}: DocumentUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<FilePreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Validate file size and type
   */
  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file size
      const maxSizeBytes = maxSize * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        return `File size exceeds ${maxSize}MB limit`;
      }

      // Check file type
      const acceptedTypes = accept.split(',').map((type) => type.trim());
      const fileExtension = `.${file.name.split('.').pop()?.toLowerCase()}`;
      const isAccepted = acceptedTypes.some((type) => {
        if (type.startsWith('.')) {
          return type === fileExtension;
        }
        return file.type === type;
      });

      if (!isAccepted) {
        return `File type not supported. Accepted types: ${acceptedTypes.join(', ')}`;
      }

      return null;
    },
    [maxSize, accept]
  );

  /**
   * Create image preview for image files
   */
  const createPreview = useCallback((file: File): Promise<string | undefined> => {
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          resolve(reader.result as string);
        };
        reader.onerror = () => {
          resolve(undefined);
        };
        reader.readAsDataURL(file);
      } else {
        resolve(undefined);
      }
    });
  }, []);

  /**
   * Handle file selection
   */
  const handleFileSelect = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;

      const fileArray = Array.from(files);
      const filesToProcess = multiple ? fileArray : [fileArray[0]];

      // Validate all files
      const validationErrors: string[] = [];
      for (const file of filesToProcess) {
        const validationError = validateFile(file);
        if (validationError) {
          validationErrors.push(`${file.name}: ${validationError}`);
        }
      }

      if (validationErrors.length > 0) {
        setError(validationErrors.join('\n'));
        return;
      }

      setError(null);

      // Create previews for all files
      const filePreviews: FilePreview[] = await Promise.all(
        filesToProcess.map(async (file) => ({
          file,
          preview: await createPreview(file),
        }))
      );

      setSelectedFiles(filePreviews);

      // Notify parent component (for single file mode)
      if (!multiple && filePreviews.length > 0) {
        onFileSelect(filePreviews[0].file);
      }
    },
    [multiple, validateFile, createPreview, onFileSelect]
  );

  /**
   * Handle drag over event
   */
  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  /**
   * Handle drag leave event
   */
  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  /**
   * Handle drop event
   */
  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (!disabled) {
        handleFileSelect(e.dataTransfer.files);
      }
    },
    [disabled, handleFileSelect]
  );

  /**
   * Handle file input change
   */
  const handleFileInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      handleFileSelect(e.target.files);
    },
    [handleFileSelect]
  );

  /**
   * Handle browse button click
   */
  const handleBrowseClick = useCallback(() => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  }, [disabled]);

  /**
   * Remove a specific file
   */
  const handleRemoveFile = useCallback(
    (index: number) => {
      const newFiles = selectedFiles.filter((_, i) => i !== index);
      setSelectedFiles(newFiles);
      setError(null);

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Notify parent if no files left
      if (newFiles.length === 0) {
        setUploadProgress(0);
      }
    },
    [selectedFiles]
  );

  /**
   * Clear all files
   */
  const handleClearAll = useCallback(() => {
    setSelectedFiles([]);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // Parse accepted file types for display
  const acceptedTypesDisplay = accept
    .split(',')
    .map((type) => type.trim().replace('.', '').toUpperCase())
    .join(', ');

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drag and Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
          isDragging && !disabled
            ? 'border-orange-500 bg-orange-50 scale-[1.02]'
            : 'border-gray-300 hover:border-orange-400',
          selectedFiles.length > 0 ? 'bg-gray-50' : 'bg-white',
          disabled && 'opacity-50 cursor-not-allowed',
          !disabled && 'hover:shadow-md'
        )}
        role="button"
        aria-label="File upload zone"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            handleBrowseClick();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileInputChange}
          accept={accept}
          multiple={multiple}
          disabled={disabled}
          className="hidden"
          aria-label="File input"
        />

        {selectedFiles.length === 0 ? (
          // Empty state
          <div className="space-y-4">
            <div className="flex justify-center">
              <div
                className={cn(
                  'p-4 rounded-full transition-colors duration-200',
                  isDragging
                    ? 'bg-orange-100'
                    : 'bg-gray-100 group-hover:bg-orange-50'
                )}
              >
                <Upload
                  className={cn(
                    'h-12 w-12 transition-colors duration-200',
                    isDragging ? 'text-orange-600' : 'text-gray-400'
                  )}
                  aria-hidden="true"
                />
              </div>
            </div>

            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragging
                  ? 'Drop your file here'
                  : 'Drag and drop your file here'}
              </p>
              <p className="text-sm text-gray-500 mt-1">or</p>
            </div>

            <button
              type="button"
              onClick={handleBrowseClick}
              disabled={disabled}
              className={cn(
                'px-6 py-2.5 bg-orange-600 text-white rounded-lg font-medium transition-all duration-200',
                'hover:bg-orange-700 hover:shadow-lg',
                'focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2',
                'disabled:bg-gray-300 disabled:cursor-not-allowed disabled:hover:shadow-none'
              )}
            >
              Browse Files
            </button>

            <div className="text-xs text-gray-500 space-y-1 mt-4">
              <p>
                <span className="font-medium">Accepted formats:</span>{' '}
                {acceptedTypesDisplay}
              </p>
              <p>
                <span className="font-medium">Maximum file size:</span> {maxSize}MB
              </p>
              {multiple && (
                <p>
                  <span className="font-medium">Multiple files:</span> Supported
                </p>
              )}
            </div>
          </div>
        ) : (
          // File previews
          <div className="space-y-3">
            {selectedFiles.map((filePreview, index) => {
              const fileConfig = getFileTypeConfig(filePreview.file.type);
              const FileIcon = fileConfig.icon;

              return (
                <div
                  key={`${filePreview.file.name}-${index}`}
                  className="flex items-start gap-4 p-4 bg-white border border-gray-200 rounded-lg hover:border-orange-300 transition-colors"
                >
                  {/* File Icon or Image Preview */}
                  <div className="flex-shrink-0">
                    {filePreview.preview ? (
                      <img
                        src={filePreview.preview}
                        alt={filePreview.file.name}
                        className="w-16 h-16 object-cover rounded-lg border border-gray-200"
                      />
                    ) : (
                      <div className="w-16 h-16 flex items-center justify-center bg-gray-100 rounded-lg">
                        <FileIcon className={cn('h-8 w-8', fileConfig.color)} />
                      </div>
                    )}
                  </div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {filePreview.file.name}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-sm text-gray-500">
                        {formatFileSize(filePreview.file.size)}
                      </p>
                      <span className="text-gray-400">•</span>
                      <p className="text-xs text-gray-400">
                        {fileConfig.ext}
                      </p>
                    </div>
                    {filePreview.file.type && (
                      <p className="text-xs text-gray-400 mt-1 truncate">
                        {filePreview.file.type}
                      </p>
                    )}
                  </div>

                  {/* Remove Button */}
                  {!disabled && (
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(index)}
                      className="flex-shrink-0 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      aria-label={`Remove ${filePreview.file.name}`}
                    >
                      <X className="h-5 w-5" />
                    </button>
                  )}
                </div>
              );
            })}

            {/* Clear All Button */}
            {multiple && selectedFiles.length > 1 && !disabled && (
              <button
                type="button"
                onClick={handleClearAll}
                className="text-sm text-gray-600 hover:text-red-600 font-medium transition-colors"
              >
                Clear all files
              </button>
            )}

            {/* Change File Button for single file mode */}
            {!multiple && !disabled && (
              <button
                type="button"
                onClick={handleBrowseClick}
                className="text-sm text-orange-600 hover:text-orange-700 font-medium transition-colors"
              >
                Change file
              </button>
            )}
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div
          className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg"
          role="alert"
          aria-live="polite"
        >
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-800">Upload Error</p>
            <p className="text-sm text-red-700 mt-1 whitespace-pre-line">{error}</p>
          </div>
          <button
            type="button"
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-600 transition-colors"
            aria-label="Dismiss error"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Upload Progress (optional - can be controlled by parent) */}
      {isUploading && uploadProgress > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700 font-medium">
              Uploading {selectedFiles.length} {selectedFiles.length === 1 ? 'file' : 'files'}...
            </span>
            <span className="text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-orange-600 h-full transition-all duration-300 ease-out"
              style={{ width: `${uploadProgress}%` }}
              role="progressbar"
              aria-valuenow={uploadProgress}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
        </div>
      )}

      {/* Success Message */}
      {uploadProgress === 100 && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <p className="text-sm text-green-800 font-medium">
            Upload complete!
          </p>
        </div>
      )}
    </div>
  );
}
