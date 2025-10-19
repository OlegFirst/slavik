'use client';

/**
 * DocumentMetadataForm Component
 * Form for editing existing document metadata
 * Includes dirty state detection and unsaved changes warning
 */

import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Loader2, X, Plus, AlertTriangle, RotateCcw } from 'lucide-react';
import { format } from 'date-fns';

import { useUpdateDocument } from '@/hooks/documents/useUpdateDocument';
import { documentUpdateSchema } from '@/lib/validations/document';
import { Document, DocumentType, DocumentClassification } from '@/types/documents';

// Form schema for metadata updates
const formSchema = documentUpdateSchema;

type FormData = z.infer<typeof formSchema>;

interface DocumentMetadataFormProps {
  document: Document;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const DOCUMENT_TYPES = [
  { value: DocumentType.POLICY, label: 'Policy' },
  { value: DocumentType.PROCEDURE, label: 'Procedure' },
  { value: DocumentType.PLAN, label: 'Plan' },
  { value: DocumentType.RISK_ASSESSMENT, label: 'Risk Assessment' },
  { value: DocumentType.BIA, label: 'Business Impact Analysis' },
  { value: DocumentType.EXERCISE_REPORT, label: 'Exercise Report' },
  { value: DocumentType.AUDIT_REPORT, label: 'Audit Report' },
  { value: DocumentType.MANAGEMENT_REVIEW, label: 'Management Review' },
  { value: DocumentType.FORM, label: 'Form' },
  { value: DocumentType.TEMPLATE, label: 'Template' },
  { value: DocumentType.CHECKLIST, label: 'Checklist' },
  { value: DocumentType.CONTACT_LIST, label: 'Contact List' },
  { value: DocumentType.COMMUNICATION, label: 'Communication' },
  { value: DocumentType.TRAINING_MATERIAL, label: 'Training Material' },
  { value: DocumentType.EVIDENCE, label: 'Evidence' },
  { value: DocumentType.CONTRACT, label: 'Contract' },
  { value: DocumentType.SOP, label: 'Standard Operating Procedure' },
  { value: DocumentType.REPORT, label: 'Report' },
  { value: DocumentType.PRESENTATION, label: 'Presentation' },
  { value: DocumentType.SPREADSHEET, label: 'Spreadsheet' },
  { value: DocumentType.OTHER, label: 'Other' },
];

const CLASSIFICATION_LEVELS = [
  { value: DocumentClassification.PUBLIC, label: 'Public', level: 1 },
  { value: DocumentClassification.INTERNAL, label: 'Internal', level: 2 },
  { value: DocumentClassification.CONFIDENTIAL, label: 'Confidential', level: 3 },
  { value: DocumentClassification.RESTRICTED, label: 'Restricted', level: 4 },
];

export function DocumentMetadataForm({
  document,
  onSuccess,
  onCancel,
}: DocumentMetadataFormProps) {
  const [tagInput, setTagInput] = useState('');
  const [customMetadataKey, setCustomMetadataKey] = useState('');
  const [customMetadataValue, setCustomMetadataValue] = useState('');
  const [showDowngradeWarning, setShowDowngradeWarning] = useState(false);

  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isDirty, isValid },
    watch,
    setValue,
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: 'onChange',
    defaultValues: {
      title: document.title,
      description: document.description || '',
      document_type: document.document_type,
      classification: document.classification,
      department: document.department || '',
      tags: document.tags || [],
      custom_metadata: document.custom_metadata || {},
    },
  });

  const tags = watch('tags') || [];
  const customMetadata = watch('custom_metadata') || {};
  const currentClassification = watch('classification');

  const updateDocument = useUpdateDocument({
    onSuccess: () => {
      toast.success('Document metadata updated successfully');
      reset(watch()); // Reset form to current values
      onSuccess?.();
    },
    onError: (error) => {
      toast.error(`Failed to update document: ${error.message}`);
    },
  });

  // Warn before navigating away with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  // Check for classification downgrade
  useEffect(() => {
    if (currentClassification) {
      const currentLevel =
        CLASSIFICATION_LEVELS.find((l) => l.value === document.classification)?.level || 0;
      const newLevel =
        CLASSIFICATION_LEVELS.find((l) => l.value === currentClassification)?.level || 0;
      setShowDowngradeWarning(newLevel < currentLevel);
    }
  }, [currentClassification, document.classification]);

  const onSubmit = (data: FormData) => {
    // Remove empty/undefined fields
    const cleanData = Object.fromEntries(
      Object.entries(data).filter(([_, v]) => v !== undefined && v !== '' && v !== null)
    );

    updateDocument.mutate({
      documentId: document.document_id,
      data: cleanData,
    });
  };

  const handleReset = () => {
    reset();
    setShowDowngradeWarning(false);
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setValue('tags', [...tags, tagInput.trim()], { shouldValidate: true, shouldDirty: true });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setValue(
      'tags',
      tags.filter((tag) => tag !== tagToRemove),
      { shouldValidate: true, shouldDirty: true }
    );
  };

  const handleAddCustomMetadata = () => {
    if (customMetadataKey.trim() && customMetadataValue.trim()) {
      setValue(
        'custom_metadata',
        {
          ...customMetadata,
          [customMetadataKey.trim()]: customMetadataValue.trim(),
        },
        { shouldValidate: true, shouldDirty: true }
      );
      setCustomMetadataKey('');
      setCustomMetadataValue('');
    }
  };

  const handleRemoveCustomMetadata = (key: string) => {
    const updated = { ...customMetadata };
    delete updated[key];
    setValue('custom_metadata', updated, { shouldValidate: true, shouldDirty: true });
  };

  const isLoading = updateDocument.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Read-only Document Info */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
        <h3 className="text-sm font-semibold text-gray-700">Document Information</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Document ID:</span>
            <span className="ml-2 font-medium">{document.document_code}</span>
          </div>
          <div>
            <span className="text-gray-500">Version:</span>
            <span className="ml-2 font-medium">{document.version}</span>
          </div>
          <div>
            <span className="text-gray-500">Status:</span>
            <span className="ml-2 font-medium capitalize">{document.status.replace('_', ' ')}</span>
          </div>
          <div>
            <span className="text-gray-500">Owner:</span>
            <span className="ml-2 font-medium">{document.owner_id}</span>
          </div>
          <div>
            <span className="text-gray-500">Created:</span>
            <span className="ml-2 font-medium">
              {format(new Date(document.created_at), 'MMM d, yyyy')}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Updated:</span>
            <span className="ml-2 font-medium">
              {format(new Date(document.updated_at), 'MMM d, yyyy')}
            </span>
          </div>
        </div>
      </div>

      {/* Title Field */}
      <div className="space-y-2">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Document Title
        </label>
        <input
          id="title"
          type="text"
          {...register('title')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          disabled={isLoading}
        />
        {errors.title && (
          <p className="text-sm text-red-600" role="alert">
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Description Field */}
      <div className="space-y-2">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          {...register('description')}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 resize-none"
          disabled={isLoading}
        />
      </div>

      {/* Classification Field */}
      <div className="space-y-2">
        <label htmlFor="classification" className="block text-sm font-medium text-gray-700">
          Classification
        </label>
        <select
          id="classification"
          {...register('classification')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          disabled={isLoading}
        >
          {CLASSIFICATION_LEVELS.map((level) => (
            <option key={level.value} value={level.value}>
              {level.label}
            </option>
          ))}
        </select>
        {showDowngradeWarning && (
          <div className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-800">
              You are downgrading the security classification. This may affect access controls and
              compliance requirements.
            </p>
          </div>
        )}
      </div>

      {/* Department Field */}
      <div className="space-y-2">
        <label htmlFor="department" className="block text-sm font-medium text-gray-700">
          Department
        </label>
        <input
          id="department"
          type="text"
          {...register('department')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          disabled={isLoading}
        />
      </div>

      {/* Tags Field */}
      <div className="space-y-2">
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
          Tags
        </label>
        <div className="flex gap-2">
          <input
            id="tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            placeholder="Add tags"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={handleAddTag}
            disabled={isLoading || !tagInput.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  disabled={isLoading}
                  className="hover:text-blue-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Custom Metadata */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Custom Metadata</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={customMetadataKey}
            onChange={(e) => setCustomMetadataKey(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Key"
            disabled={isLoading}
          />
          <input
            type="text"
            value={customMetadataValue}
            onChange={(e) => setCustomMetadataValue(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Value"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={handleAddCustomMetadata}
            disabled={isLoading || !customMetadataKey.trim() || !customMetadataValue.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add
          </button>
        </div>
        {Object.keys(customMetadata).length > 0 && (
          <div className="mt-2 space-y-2">
            {Object.entries(customMetadata).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center justify-between p-2 bg-gray-50 border border-gray-200 rounded"
              >
                <div className="flex-1">
                  <span className="text-sm font-medium text-gray-700">{key}:</span>
                  <span className="ml-2 text-sm text-gray-600">{String(value)}</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveCustomMetadata(key)}
                  disabled={isLoading}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Unsaved Changes Warning */}
      {isDirty && (
        <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <AlertTriangle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-800">You have unsaved changes</p>
        </div>
      )}

      {/* Form Actions */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button
          type="submit"
          disabled={isLoading || !isDirty || !isValid}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            'Save Changes'
          )}
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading || !isDirty}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
