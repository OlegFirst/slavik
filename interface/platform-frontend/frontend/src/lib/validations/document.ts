/**
 * Document Validation Schemas
 * Zod schemas for Document Management validation
 * Enforces business rules and data integrity
 */

import { z } from 'zod';

// Note: These enums should match the ones in @/types/documents
// Since types file is being created by Agent 1, we define expected structure here

/**
 * Document Create Schema
 * Validates all required fields for creating a new document
 */
export const documentCreateSchema = z.object({
  tenant_id: z.string().min(1, 'Tenant ID is required'),

  title: z.string()
    .min(3, 'Document title must be at least 3 characters')
    .max(500, 'Document title must be less than 500 characters')
    .refine((val) => validateDocumentTitle(val), {
      message: 'Invalid title: no leading/trailing spaces, cannot be only numbers, avoid special characters',
    }),

  description: z.string().optional(),

  document_type: z.string().min(1, 'Document type is required'),

  classification: z.string().optional(),

  is_controlled: z.boolean().optional(),

  requires_approval: z.boolean().optional(),

  owner_id: z.string().min(1, 'Owner ID is required'),

  department: z.string().optional(),

  process_area: z.string().optional(),

  tags: z.array(z.string()).optional(),

  custom_metadata: z.record(z.any()).optional(),
});

/**
 * Document Update Schema
 * All fields optional, but at least one field required
 */
const documentUpdateBaseSchema = z.object({
  title: z.string()
    .min(3, 'Document title must be at least 3 characters')
    .max(500, 'Document title must be less than 500 characters')
    .optional(),

  description: z.string().optional(),

  document_type: z.string().optional(),

  classification: z.string().optional(),

  is_controlled: z.boolean().optional(),

  requires_approval: z.boolean().optional(),

  owner_id: z.string().optional(),

  department: z.string().optional(),

  process_area: z.string().optional(),

  tags: z.array(z.string()).optional(),

  custom_metadata: z.record(z.any()).optional(),
});

export const documentUpdateSchema = documentUpdateBaseSchema.refine(
  (data) => Object.keys(data).length > 0,
  {
    message: 'At least one field must be provided for update',
  }
);

/**
 * Share Request Schema
 * Validates document sharing requests
 */
export const shareRequestSchema = z.object({
  shared_with_user_id: z.string().optional(),

  shared_with_email: z.string()
    .email('Invalid email format')
    .optional(),

  permission_level: z.string().optional().default('VIEW'),

  can_reshare: z.boolean().optional().default(false),

  expires_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime()) && date > new Date();
    }, {
      message: 'Expiration date must be a valid future date',
    })
    .optional(),

  share_message: z.string()
    .max(1000, 'Share message must be less than 1000 characters')
    .optional(),
}).refine(
  (data) => data.shared_with_user_id || data.shared_with_email,
  {
    message: 'Either shared_with_user_id or shared_with_email is required',
    path: ['shared_with_user_id'],
  }
);

/**
 * Approval Request Schema
 * Validates approval workflow initiation
 */
export const approvalRequestSchema = z.object({
  approver_id: z.string().min(1, 'Approver ID is required'),

  approver_role: z.string()
    .min(1, 'Approver role is required')
    .max(100, 'Approver role must be less than 100 characters'),

  sla_hours: z.number()
    .min(1, 'SLA must be at least 1 hour')
    .max(720, 'SLA cannot exceed 720 hours (30 days)')
    .optional(),

  notes: z.string()
    .max(2000, 'Notes must be less than 2000 characters')
    .optional(),
});

/**
 * Approval Response Schema
 * Validates approver's decision
 */
export const approvalResponseSchema = z.object({
  action: z.enum(['approve', 'reject', 'recall'], {
    errorMap: () => ({ message: 'Action must be approve, reject, or recall' }),
  }),

  decision_notes: z.string()
    .max(2000, 'Decision notes must be less than 2000 characters')
    .optional(),

  suggested_changes: z.array(z.string()).optional(),
});

/**
 * Retention Policy Create Schema
 * Validates retention policy configuration
 */
export const retentionPolicyCreateSchema = z.object({
  tenant_id: z.string().min(1, 'Tenant ID is required'),

  policy_name: z.string()
    .min(3, 'Policy name must be at least 3 characters')
    .max(200, 'Policy name must be less than 200 characters'),

  description: z.string().optional(),

  document_type: z.string().optional(),

  department: z.string().optional(),

  classification: z.string().optional(),

  retention_years: z.number()
    .min(0, 'Retention years must be 0 or positive')
    .max(100, 'Retention years cannot exceed 100 years'),

  is_permanent: z.boolean().optional().default(false),

  trigger_type: z.string().min(1, 'Trigger type is required'),

  archive_after_days: z.number()
    .min(0, 'Archive days must be non-negative')
    .optional(),

  destroy_after_days: z.number()
    .min(0, 'Destroy days must be non-negative')
    .optional(),

  require_review_before_destruction: z.boolean().optional().default(false),

  is_active: z.boolean().optional().default(true),
}).refine(
  (data) => {
    // Business rule: If permanent, retention_years should be 0
    if (data.is_permanent && data.retention_years !== 0) {
      return false;
    }
    return true;
  },
  {
    message: 'Permanent retention policies must have retention_years set to 0',
    path: ['retention_years'],
  }
);

/**
 * Document Filters Schema
 * Validates search and filter parameters
 */
export const documentFiltersSchema = z.object({
  tenant_id: z.string().optional(),

  document_type: z.string().optional(),

  status: z.string().optional(),

  classification: z.string().optional(),

  owner_id: z.string().optional(),

  department: z.string().optional(),

  search: z.string()
    .min(2, 'Search query must be at least 2 characters for performance')
    .optional(),

  tags: z.array(z.string()).optional(),

  from_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Invalid from_date format',
    })
    .optional(),

  to_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Invalid to_date format',
    })
    .optional(),
});

/**
 * Type exports for TypeScript inference
 */
export type DocumentCreateInput = z.infer<typeof documentCreateSchema>;
export type DocumentUpdateInput = z.infer<typeof documentUpdateSchema>;
export type ShareRequestInput = z.infer<typeof shareRequestSchema>;
export type ApprovalRequestInput = z.infer<typeof approvalRequestSchema>;
export type ApprovalResponseInput = z.infer<typeof approvalResponseSchema>;
export type RetentionPolicyCreateInput = z.infer<typeof retentionPolicyCreateSchema>;
export type DocumentFiltersInput = z.infer<typeof documentFiltersSchema>;

/**
 * Helper Functions
 */

/**
 * Validate document title
 * Checks for special characters, leading/trailing spaces, and numeric-only titles
 */
export function validateDocumentTitle(title: string): boolean {
  // Check for leading/trailing spaces
  if (title !== title.trim()) {
    return false;
  }

  // Check if only numbers
  if (/^\d+$/.test(title)) {
    return false;
  }

  // Allow alphanumeric, spaces, hyphens, underscores, periods, parentheses
  const validPattern = /^[a-zA-Z0-9\s\-_.()]+$/;
  if (!validPattern.test(title)) {
    return false;
  }

  return true;
}

/**
 * Validate file size
 * Checks if file size is within acceptable limits
 */
export function validateFileSize(sizeBytes: number, maxMB: number = 50): boolean {
  const maxBytes = maxMB * 1024 * 1024;
  return sizeBytes > 0 && sizeBytes <= maxBytes;
}

/**
 * Validate file type
 * Checks if file extension is in allowed types
 */
export function validateFileType(
  fileName: string,
  allowedTypes?: string[]
): boolean {
  const defaultAllowedTypes = [
    'pdf',
    'docx',
    'doc',
    'xlsx',
    'xls',
    'pptx',
    'ppt',
    'txt',
    'md',
    'jpg',
    'jpeg',
    'png',
  ];

  const allowed = allowedTypes || defaultAllowedTypes;
  const extension = fileName.split('.').pop()?.toLowerCase();

  if (!extension) {
    return false;
  }

  return allowed.includes(extension);
}

/**
 * Get classification level as numeric value
 * Useful for permission checks and comparisons
 */
export function getClassificationLevel(classification: string): number {
  const levels: Record<string, number> = {
    PUBLIC: 1,
    INTERNAL: 2,
    CONFIDENTIAL: 3,
    RESTRICTED: 4,
    HIGHLY_RESTRICTED: 5,
  };

  return levels[classification.toUpperCase()] || 0;
}

/**
 * Check if user can share document based on classification levels
 * User clearance must be >= document classification
 */
export function canShareWithClassification(
  docClassification: string,
  userClearance: string
): boolean {
  const docLevel = getClassificationLevel(docClassification);
  const userLevel = getClassificationLevel(userClearance);

  return userLevel >= docLevel;
}
