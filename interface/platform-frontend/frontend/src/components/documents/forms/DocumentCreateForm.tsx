'use client';

/**
 * DocumentCreateForm Component
 * Form for creating new document metadata with validation
 * Uses React Hook Form + Zod for robust validation
 */

import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Loader2, X, Plus } from 'lucide-react';

import { useCreateDocument } from '@/hooks/documents/useCreateDocument';
import { documentCreateSchema } from '@/lib/validations/document';
import { DocumentType, DocumentClassification } from '@/types/documents';

// Form schema - extends the base schema with UI-specific fields
const formSchema = documentCreateSchema.extend({
  version: z.string().default('1.0.0'),
});

type FormData = z.infer<typeof formSchema>;

interface DocumentCreateFormProps {
  tenantId: string;
  userId: string;
  onSuccess?: (documentId: number) => void;
  onCancel?: () => void;
}

// All 21 document types as options
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
  { value: DocumentClassification.PUBLIC, label: 'Public', description: 'Available to anyone' },
  { value: DocumentClassification.INTERNAL, label: 'Internal', description: 'Organization members only' },
  { value: DocumentClassification.CONFIDENTIAL, label: 'Confidential', description: 'Authorized personnel only' },
  { value: DocumentClassification.RESTRICTED, label: 'Restricted', description: 'Highly sensitive information' },
];

export function DocumentCreateForm({
  tenantId,
  userId,
  onSuccess,
  onCancel,
}: DocumentCreateFormProps) {
  const [tagInput, setTagInput] = useState('');

  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isValid, isDirty },
    watch,
    setValue,
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: 'onChange',
    defaultValues: {
      tenant_id: tenantId,
      owner_id: userId,
      version: '1.0.0',
      tags: [],
      classification: DocumentClassification.INTERNAL,
      is_controlled: false,
      requires_approval: false,
    },
  });

  const tags = watch('tags') || [];

  const createDocument = useCreateDocument({
    onSuccess: (document) => {
      toast.success(`Document "${document.title}" created successfully`);
      onSuccess?.(document.document_id);
    },
    onError: (error) => {
      toast.error(`Failed to create document: ${error.message}`);
    },
  });

  const onSubmit = (data: FormData) => {
    // Convert form data to DocumentCreate type
    const createData: any = {
      ...data,
      document_type: data.document_type as DocumentType,
      classification: data.classification as DocumentClassification,
    };
    createDocument.mutate(createData);
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

  const handleTagInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const isLoading = createDocument.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Title Field */}
      <div className="space-y-2">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Document Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          type="text"
          {...register('title')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          placeholder="Enter document title"
          disabled={isLoading}
          aria-invalid={errors.title ? 'true' : 'false'}
          aria-describedby={errors.title ? 'title-error' : undefined}
        />
        {errors.title && (
          <p id="title-error" className="text-sm text-red-600" role="alert">
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Document Type Field */}
      <div className="space-y-2">
        <label htmlFor="document_type" className="block text-sm font-medium text-gray-700">
          Document Type <span className="text-red-500">*</span>
        </label>
        <select
          id="document_type"
          {...register('document_type')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          disabled={isLoading}
          aria-invalid={errors.document_type ? 'true' : 'false'}
          aria-describedby={errors.document_type ? 'document-type-error' : undefined}
        >
          <option value="">Select document type</option>
          {DOCUMENT_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.document_type && (
          <p id="document-type-error" className="text-sm text-red-600" role="alert">
            {errors.document_type.message}
          </p>
        )}
      </div>

      {/* Classification Field (Radio Group) */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Classification <span className="text-red-500">*</span>
        </label>
        <Controller
          name="classification"
          control={control}
          render={({ field }) => (
            <div className="space-y-3" role="radiogroup" aria-labelledby="classification-label">
              {CLASSIFICATION_LEVELS.map((level) => (
                <label
                  key={level.value}
                  className="flex items-start space-x-3 p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="radio"
                    value={level.value}
                    checked={field.value === level.value}
                    onChange={() => field.onChange(level.value)}
                    disabled={isLoading}
                    className="mt-0.5 h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{level.label}</div>
                    <div className="text-sm text-gray-500">{level.description}</div>
                  </div>
                </label>
              ))}
            </div>
          )}
        />
        {errors.classification && (
          <p className="text-sm text-red-600" role="alert">
            {errors.classification.message}
          </p>
        )}
      </div>

      {/* Owner Field */}
      <div className="space-y-2">
        <label htmlFor="owner_id" className="block text-sm font-medium text-gray-700">
          Owner <span className="text-red-500">*</span>
        </label>
        <input
          id="owner_id"
          type="text"
          {...register('owner_id')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          placeholder="Owner ID or email"
          disabled={isLoading}
          aria-invalid={errors.owner_id ? 'true' : 'false'}
          aria-describedby={errors.owner_id ? 'owner-error' : undefined}
        />
        {errors.owner_id && (
          <p id="owner-error" className="text-sm text-red-600" role="alert">
            {errors.owner_id.message}
          </p>
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
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          placeholder="e.g., Risk Management"
          disabled={isLoading}
        />
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
          maxLength={500}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed resize-none"
          placeholder="Brief description of the document (max 500 characters)"
          disabled={isLoading}
        />
        <div className="text-sm text-gray-500 text-right">
          {watch('description')?.length || 0} / 500
        </div>
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
            onKeyDown={handleTagInputKeyDown}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Add tags (press Enter)"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={handleAddTag}
            disabled={isLoading || !tagInput.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
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
                  className="hover:text-blue-900 disabled:opacity-50"
                  aria-label={`Remove tag ${tag}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Version Field (Read-only) */}
      <div className="space-y-2">
        <label htmlFor="version" className="block text-sm font-medium text-gray-700">
          Version
        </label>
        <input
          id="version"
          type="text"
          {...register('version')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50 cursor-not-allowed"
          readOnly
          disabled
        />
        <p className="text-sm text-gray-500">Initial version will be 1.0.0</p>
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button
          type="submit"
          disabled={isLoading || !isValid}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Creating...
            </>
          ) : (
            'Create Document'
          )}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
