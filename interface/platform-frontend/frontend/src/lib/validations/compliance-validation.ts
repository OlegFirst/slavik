/**
 * Compliance Module - Validation Schemas
 * Zod schemas for compliance management data validation
 *
 * Created: 2025-10-23
 * Agent: 16 (Compliance Module Round 1)
 * Module: Compliance Management
 */

import { z } from 'zod';

// =============================================================================
// ENUMS (Define common compliance enums for validation)
// =============================================================================

/**
 * Compliance Status Enumeration
 * Status of compliance programs, requirements, and assessments
 */
export enum ComplianceStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLIANT = 'compliant',
  NON_COMPLIANT = 'non_compliant',
  PARTIALLY_COMPLIANT = 'partially_compliant',
  UNDER_REVIEW = 'under_review',
}

/**
 * Requirement Type Enumeration
 * Types of compliance requirements
 */
export enum RequirementType {
  MANDATORY = 'mandatory',
  ADVISORY = 'advisory',
  OPTIONAL = 'optional',
  RECOMMENDED = 'recommended',
}

/**
 * Assessment Status Enumeration
 * Status of compliance assessments
 */
export enum AssessmentStatus {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

/**
 * Gap Severity Enumeration
 * Severity levels for compliance gaps
 */
export enum GapSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Action Status Enumeration
 * Status of corrective actions
 */
export enum ActionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  VERIFIED = 'verified',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
}

/**
 * Action Priority Enumeration
 * Priority levels for corrective actions
 */
export enum ActionPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Evidence Type Enumeration
 * Types of compliance evidence
 */
export enum EvidenceType {
  DOCUMENT = 'document',
  SCREENSHOT = 'screenshot',
  POLICY = 'policy',
  PROCEDURE = 'procedure',
  CERTIFICATION = 'certification',
  AUDIT_LOG = 'audit_log',
  TEST_RESULT = 'test_result',
  REPORT = 'report',
}

/**
 * Audit Type Enumeration
 * Types of compliance audits
 */
export enum AuditType {
  INTERNAL = 'internal',
  EXTERNAL = 'external',
  THIRD_PARTY = 'third_party',
  REGULATORY = 'regulatory',
  CERTIFICATION = 'certification',
}

/**
 * Framework Type Enumeration
 * Compliance frameworks and standards
 */
export enum FrameworkType {
  ISO_27001 = 'iso_27001',
  ISO_22301 = 'iso_22301',
  SOC2 = 'soc2',
  GDPR = 'gdpr',
  HIPAA = 'hipaa',
  PCI_DSS = 'pci_dss',
  NIST = 'nist',
  CUSTOM = 'custom',
}

// =============================================================================
// COMPLIANCE PROGRAM SCHEMAS
// =============================================================================

/**
 * Compliance Program Create Schema
 * Validates all required fields for creating a new compliance program
 */
export const complianceProgramCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  // Program Details
  program_name: z.string()
    .min(3, 'Program name must be at least 3 characters')
    .max(200, 'Program name must be less than 200 characters'),

  program_code: z.string()
    .min(2, 'Program code must be at least 2 characters')
    .max(50, 'Program code must be less than 50 characters')
    .optional(),

  framework: z.nativeEnum(FrameworkType, {
    errorMap: () => ({ message: 'Valid framework type is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters'),

  // Scope
  scope_description: z.string()
    .min(10, 'Scope description must be at least 10 characters')
    .max(2000, 'Scope must be less than 2000 characters')
    .optional(),

  applicable_departments: z.array(z.string().min(1))
    .default([]),

  applicable_processes: z.array(z.string().min(1))
    .default([]),

  // Status & Ownership
  status: z.nativeEnum(ComplianceStatus, {
    errorMap: () => ({ message: 'Valid compliance status is required' }),
  }),

  program_owner_id: z.string()
    .min(1, 'Program owner is required'),

  program_manager_id: z.string()
    .min(1, 'Program manager is required')
    .optional(),

  // Timeline
  start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  target_completion_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Target completion date must be a valid date',
    })
    .optional(),

  next_review_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Next review date must be a valid date',
    })
    .optional(),

  // Metrics
  compliance_score: z.number()
    .int('Compliance score must be an integer')
    .min(0, 'Compliance score must be between 0 and 100')
    .max(100, 'Compliance score must be between 0 and 100')
    .default(0),

  // Metadata
  created_by: z.string()
    .min(1, 'Creator is required'),

  tags: z.array(z.string().min(1))
    .default([]),

  is_active: z.boolean()
    .default(true),
})
  // Business Rule: target_completion_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.target_completion_date) return true;
      const start = new Date(data.start_date);
      const target = new Date(data.target_completion_date);
      return target >= start;
    },
    {
      message: 'Target completion date must be after or equal to start date',
      path: ['target_completion_date'],
    }
  );

/**
 * Compliance Program Update Schema
 * All fields optional for partial updates
 */
export const complianceProgramUpdateSchema = z.object({
  program_name: z.string()
    .min(3, 'Program name must be at least 3 characters')
    .max(200, 'Program name must be less than 200 characters')
    .optional(),

  program_code: z.string()
    .min(2, 'Program code must be at least 2 characters')
    .max(50, 'Program code must be less than 50 characters')
    .optional(),

  framework: z.nativeEnum(FrameworkType).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  scope_description: z.string()
    .min(10, 'Scope description must be at least 10 characters')
    .max(2000, 'Scope must be less than 2000 characters')
    .optional(),

  applicable_departments: z.array(z.string().min(1)).optional(),
  applicable_processes: z.array(z.string().min(1)).optional(),

  status: z.nativeEnum(ComplianceStatus).optional(),
  program_owner_id: z.string().min(1, 'Program owner is required').optional(),
  program_manager_id: z.string().min(1, 'Program manager is required').optional(),

  start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  target_completion_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Target completion date must be a valid date',
    })
    .optional(),

  next_review_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Next review date must be a valid date',
    })
    .optional(),

  compliance_score: z.number()
    .int('Compliance score must be an integer')
    .min(0, 'Compliance score must be between 0 and 100')
    .max(100, 'Compliance score must be between 0 and 100')
    .optional(),

  tags: z.array(z.string().min(1)).optional(),
  is_active: z.boolean().optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// COMPLIANCE REQUIREMENT SCHEMAS
// =============================================================================

/**
 * Compliance Requirement Create Schema
 * Validates individual compliance requirements
 */
export const complianceRequirementCreateSchema = z.object({
  program_id: z.string()
    .min(1, 'Program ID is required'),

  // Requirement Details
  requirement_code: z.string()
    .min(1, 'Requirement code is required')
    .max(100, 'Requirement code must be less than 100 characters'),

  requirement_title: z.string()
    .min(3, 'Requirement title must be at least 3 characters')
    .max(200, 'Requirement title must be less than 200 characters'),

  requirement_type: z.nativeEnum(RequirementType, {
    errorMap: () => ({ message: 'Valid requirement type is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters'),

  control_objective: z.string()
    .min(10, 'Control objective must be at least 10 characters')
    .max(1000, 'Control objective must be less than 1000 characters')
    .optional(),

  // Status & Assessment
  status: z.nativeEnum(ComplianceStatus, {
    errorMap: () => ({ message: 'Valid compliance status is required' }),
  }),

  compliance_score: z.number()
    .int('Compliance score must be an integer')
    .min(0, 'Compliance score must be between 0 and 100')
    .max(100, 'Compliance score must be between 0 and 100')
    .default(0),

  // Ownership
  responsible_party_id: z.string()
    .min(1, 'Responsible party is required')
    .optional(),

  reviewer_id: z.string()
    .min(1, 'Reviewer ID is required')
    .optional(),

  // Timeline
  due_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Due date must be a valid date',
    })
    .optional(),

  last_assessed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last assessed date must be a valid date',
    })
    .optional(),

  next_assessment_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Next assessment date must be a valid date',
    })
    .optional(),

  // References
  framework_reference: z.string()
    .max(200, 'Framework reference must be less than 200 characters')
    .optional(),

  related_controls: z.array(z.string().min(1))
    .default([]),

  related_policies: z.array(z.string().min(1))
    .default([]),

  // Metadata
  priority: z.nativeEnum(ActionPriority)
    .default(ActionPriority.MEDIUM),

  is_active: z.boolean()
    .default(true),
});

/**
 * Compliance Requirement Update Schema
 * All fields optional for partial updates
 */
export const complianceRequirementUpdateSchema = z.object({
  requirement_code: z.string()
    .min(1, 'Requirement code is required')
    .max(100, 'Requirement code must be less than 100 characters')
    .optional(),

  requirement_title: z.string()
    .min(3, 'Requirement title must be at least 3 characters')
    .max(200, 'Requirement title must be less than 200 characters')
    .optional(),

  requirement_type: z.nativeEnum(RequirementType).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  control_objective: z.string()
    .min(10, 'Control objective must be at least 10 characters')
    .max(1000, 'Control objective must be less than 1000 characters')
    .optional(),

  status: z.nativeEnum(ComplianceStatus).optional(),

  compliance_score: z.number()
    .int('Compliance score must be an integer')
    .min(0, 'Compliance score must be between 0 and 100')
    .max(100, 'Compliance score must be between 0 and 100')
    .optional(),

  responsible_party_id: z.string().min(1, 'Responsible party is required').optional(),
  reviewer_id: z.string().min(1, 'Reviewer ID is required').optional(),

  due_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Due date must be a valid date',
    })
    .optional(),

  last_assessed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last assessed date must be a valid date',
    })
    .optional(),

  next_assessment_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Next assessment date must be a valid date',
    })
    .optional(),

  framework_reference: z.string()
    .max(200, 'Framework reference must be less than 200 characters')
    .optional(),

  related_controls: z.array(z.string().min(1)).optional(),
  related_policies: z.array(z.string().min(1)).optional(),
  priority: z.nativeEnum(ActionPriority).optional(),
  is_active: z.boolean().optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// COMPLIANCE ASSESSMENT SCHEMAS
// =============================================================================

/**
 * Compliance Assessment Create Schema
 * Validates compliance assessments and audits
 */
export const complianceAssessmentCreateSchema = z.object({
  program_id: z.string()
    .min(1, 'Program ID is required'),

  requirement_id: z.string()
    .min(1, 'Requirement ID is required')
    .optional(),

  // Assessment Details
  assessment_title: z.string()
    .min(3, 'Assessment title must be at least 3 characters')
    .max(200, 'Assessment title must be less than 200 characters'),

  assessment_type: z.enum(['self', 'peer', 'management', 'external', 'automated'], {
    errorMap: () => ({ message: 'Valid assessment type is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  // Status
  status: z.nativeEnum(AssessmentStatus, {
    errorMap: () => ({ message: 'Valid assessment status is required' }),
  }),

  // Ownership
  assessor_id: z.string()
    .min(1, 'Assessor is required'),

  reviewer_id: z.string()
    .min(1, 'Reviewer is required')
    .optional(),

  // Timeline
  scheduled_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Scheduled date must be a valid date',
    })
    .optional(),

  started_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  completed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Completion date must be a valid date',
    })
    .optional(),

  // Results
  findings: z.string()
    .max(2000, 'Findings must be less than 2000 characters')
    .optional(),

  compliance_percentage: z.number()
    .int('Compliance percentage must be an integer')
    .min(0, 'Compliance percentage must be between 0 and 100')
    .max(100, 'Compliance percentage must be between 0 and 100')
    .optional(),

  gaps_identified: z.number()
    .int('Gaps count must be an integer')
    .min(0, 'Gaps count must be non-negative')
    .default(0),

  recommendations: z.string()
    .max(2000, 'Recommendations must be less than 2000 characters')
    .optional(),

  // Metadata
  evidence_ids: z.array(z.string().min(1))
    .default([]),

  created_by: z.string()
    .min(1, 'Creator is required'),
})
  // Business Rule: completed_at must be after started_at
  .refine(
    (data) => {
      if (!data.started_at || !data.completed_at) return true;
      const start = new Date(data.started_at);
      const completed = new Date(data.completed_at);
      return completed >= start;
    },
    {
      message: 'Completion date must be after or equal to start date',
      path: ['completed_at'],
    }
  );

/**
 * Compliance Assessment Update Schema
 * All fields optional for partial updates
 */
export const complianceAssessmentUpdateSchema = z.object({
  assessment_title: z.string()
    .min(3, 'Assessment title must be at least 3 characters')
    .max(200, 'Assessment title must be less than 200 characters')
    .optional(),

  assessment_type: z.enum(['self', 'peer', 'management', 'external', 'automated']).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  status: z.nativeEnum(AssessmentStatus).optional(),
  assessor_id: z.string().min(1, 'Assessor is required').optional(),
  reviewer_id: z.string().min(1, 'Reviewer is required').optional(),

  scheduled_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Scheduled date must be a valid date',
    })
    .optional(),

  started_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  completed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Completion date must be a valid date',
    })
    .optional(),

  findings: z.string()
    .max(2000, 'Findings must be less than 2000 characters')
    .optional(),

  compliance_percentage: z.number()
    .int('Compliance percentage must be an integer')
    .min(0, 'Compliance percentage must be between 0 and 100')
    .max(100, 'Compliance percentage must be between 0 and 100')
    .optional(),

  gaps_identified: z.number()
    .int('Gaps count must be an integer')
    .min(0, 'Gaps count must be non-negative')
    .optional(),

  recommendations: z.string()
    .max(2000, 'Recommendations must be less than 2000 characters')
    .optional(),

  evidence_ids: z.array(z.string().min(1)).optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// COMPLIANCE GAP SCHEMAS
// =============================================================================

/**
 * Compliance Gap Create Schema
 * Validates identified compliance gaps and deficiencies
 */
export const complianceGapCreateSchema = z.object({
  program_id: z.string()
    .min(1, 'Program ID is required'),

  requirement_id: z.string()
    .min(1, 'Requirement ID is required'),

  assessment_id: z.string()
    .min(1, 'Assessment ID is required')
    .optional(),

  // Gap Details
  gap_title: z.string()
    .min(3, 'Gap title must be at least 3 characters')
    .max(200, 'Gap title must be less than 200 characters'),

  gap_description: z.string()
    .min(10, 'Gap description must be at least 10 characters')
    .max(2000, 'Gap description must be less than 2000 characters'),

  severity: z.nativeEnum(GapSeverity, {
    errorMap: () => ({ message: 'Valid severity level is required' }),
  }),

  // Impact
  impact_description: z.string()
    .min(10, 'Impact description must be at least 10 characters')
    .max(1000, 'Impact description must be less than 1000 characters')
    .optional(),

  risk_level: z.enum(['low', 'medium', 'high', 'critical'])
    .default('medium'),

  // Ownership
  identified_by: z.string()
    .min(1, 'Identifier is required'),

  assigned_to: z.string()
    .min(1, 'Assignee is required')
    .optional(),

  // Timeline
  identified_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Identified date must be a valid date',
    })
    .optional(),

  due_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Due date must be a valid date',
    })
    .optional(),

  resolved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Resolved date must be a valid date',
    })
    .optional(),

  // Status
  status: z.enum(['open', 'in_progress', 'resolved', 'accepted', 'deferred'])
    .default('open'),

  resolution_notes: z.string()
    .max(2000, 'Resolution notes must be less than 2000 characters')
    .optional(),

  // References
  related_gaps: z.array(z.string().min(1))
    .default([]),
});

/**
 * Compliance Gap Update Schema
 * All fields optional for partial updates
 */
export const complianceGapUpdateSchema = z.object({
  gap_title: z.string()
    .min(3, 'Gap title must be at least 3 characters')
    .max(200, 'Gap title must be less than 200 characters')
    .optional(),

  gap_description: z.string()
    .min(10, 'Gap description must be at least 10 characters')
    .max(2000, 'Gap description must be less than 2000 characters')
    .optional(),

  severity: z.nativeEnum(GapSeverity).optional(),

  impact_description: z.string()
    .min(10, 'Impact description must be at least 10 characters')
    .max(1000, 'Impact description must be less than 1000 characters')
    .optional(),

  risk_level: z.enum(['low', 'medium', 'high', 'critical']).optional(),
  assigned_to: z.string().min(1, 'Assignee is required').optional(),

  identified_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Identified date must be a valid date',
    })
    .optional(),

  due_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Due date must be a valid date',
    })
    .optional(),

  resolved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Resolved date must be a valid date',
    })
    .optional(),

  status: z.enum(['open', 'in_progress', 'resolved', 'accepted', 'deferred']).optional(),

  resolution_notes: z.string()
    .max(2000, 'Resolution notes must be less than 2000 characters')
    .optional(),

  related_gaps: z.array(z.string().min(1)).optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// CORRECTIVE ACTION SCHEMAS
// =============================================================================

/**
 * Corrective Action Create Schema
 * Validates corrective and preventive actions for compliance gaps
 */
export const correctiveActionCreateSchema = z.object({
  gap_id: z.string()
    .min(1, 'Gap ID is required'),

  program_id: z.string()
    .min(1, 'Program ID is required')
    .optional(),

  // Action Details
  action_title: z.string()
    .min(3, 'Action title must be at least 3 characters')
    .max(200, 'Action title must be less than 200 characters'),

  action_description: z.string()
    .min(10, 'Action description must be at least 10 characters')
    .max(2000, 'Action description must be less than 2000 characters'),

  action_type: z.enum(['corrective', 'preventive', 'detective'], {
    errorMap: () => ({ message: 'Valid action type is required' }),
  }),

  priority: z.nativeEnum(ActionPriority, {
    errorMap: () => ({ message: 'Valid priority is required' }),
  }),

  // Ownership
  assigned_to: z.string()
    .min(1, 'Assignee is required'),

  assigned_by: z.string()
    .min(1, 'Assigner is required'),

  reviewer_id: z.string()
    .min(1, 'Reviewer is required')
    .optional(),

  // Timeline
  start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  due_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Due date must be a valid date',
    }),

  completed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Completion date must be a valid date',
    })
    .optional(),

  // Status & Progress
  status: z.nativeEnum(ActionStatus, {
    errorMap: () => ({ message: 'Valid action status is required' }),
  }),

  progress_percentage: z.number()
    .int('Progress percentage must be an integer')
    .min(0, 'Progress percentage must be between 0 and 100')
    .max(100, 'Progress percentage must be between 0 and 100')
    .default(0),

  // Implementation
  implementation_notes: z.string()
    .max(2000, 'Implementation notes must be less than 2000 characters')
    .optional(),

  verification_notes: z.string()
    .max(2000, 'Verification notes must be less than 2000 characters')
    .optional(),

  // Cost & Resources
  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  actual_cost: z.number()
    .nonnegative('Actual cost must be non-negative')
    .optional(),

  // Dependencies
  depends_on: z.array(z.string().min(1))
    .default([]),

  blocks: z.array(z.string().min(1))
    .default([]),
})
  // Business Rule: due_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.due_date) return true;
      const start = new Date(data.start_date);
      const due = new Date(data.due_date);
      return due >= start;
    },
    {
      message: 'Due date must be after or equal to start date',
      path: ['due_date'],
    }
  )
  // Business Rule: completed_at must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.completed_at) return true;
      const start = new Date(data.start_date);
      const completed = new Date(data.completed_at);
      return completed >= start;
    },
    {
      message: 'Completion date must be after or equal to start date',
      path: ['completed_at'],
    }
  );

/**
 * Corrective Action Update Schema
 * All fields optional for partial updates
 */
export const correctiveActionUpdateSchema = z.object({
  action_title: z.string()
    .min(3, 'Action title must be at least 3 characters')
    .max(200, 'Action title must be less than 200 characters')
    .optional(),

  action_description: z.string()
    .min(10, 'Action description must be at least 10 characters')
    .max(2000, 'Action description must be less than 2000 characters')
    .optional(),

  action_type: z.enum(['corrective', 'preventive', 'detective']).optional(),
  priority: z.nativeEnum(ActionPriority).optional(),
  assigned_to: z.string().min(1, 'Assignee is required').optional(),
  reviewer_id: z.string().min(1, 'Reviewer is required').optional(),

  start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  due_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Due date must be a valid date',
    })
    .optional(),

  completed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Completion date must be a valid date',
    })
    .optional(),

  status: z.nativeEnum(ActionStatus).optional(),

  progress_percentage: z.number()
    .int('Progress percentage must be an integer')
    .min(0, 'Progress percentage must be between 0 and 100')
    .max(100, 'Progress percentage must be between 0 and 100')
    .optional(),

  implementation_notes: z.string()
    .max(2000, 'Implementation notes must be less than 2000 characters')
    .optional(),

  verification_notes: z.string()
    .max(2000, 'Verification notes must be less than 2000 characters')
    .optional(),

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  actual_cost: z.number()
    .nonnegative('Actual cost must be non-negative')
    .optional(),

  depends_on: z.array(z.string().min(1)).optional(),
  blocks: z.array(z.string().min(1)).optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// COMPLIANCE EVIDENCE SCHEMAS
// =============================================================================

/**
 * Compliance Evidence Create Schema
 * Validates evidence and documentation for compliance
 */
export const complianceEvidenceCreateSchema = z.object({
  program_id: z.string()
    .min(1, 'Program ID is required'),

  requirement_id: z.string()
    .min(1, 'Requirement ID is required')
    .optional(),

  assessment_id: z.string()
    .min(1, 'Assessment ID is required')
    .optional(),

  // Evidence Details
  evidence_title: z.string()
    .min(3, 'Evidence title must be at least 3 characters')
    .max(200, 'Evidence title must be less than 200 characters'),

  evidence_type: z.nativeEnum(EvidenceType, {
    errorMap: () => ({ message: 'Valid evidence type is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  // File Information
  file_name: z.string()
    .min(1, 'File name is required')
    .max(255, 'File name must be less than 255 characters')
    .optional(),

  file_path: z.string()
    .min(1, 'File path is required')
    .max(500, 'File path must be less than 500 characters')
    .optional(),

  file_size: z.number()
    .int('File size must be an integer')
    .min(0, 'File size must be non-negative')
    .optional(),

  mime_type: z.string()
    .max(100, 'MIME type must be less than 100 characters')
    .optional(),

  // Metadata
  collected_by: z.string()
    .min(1, 'Collector is required'),

  collected_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Collection date must be a valid date',
    })
    .optional(),

  expiry_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Expiry date must be a valid date',
    })
    .optional(),

  // Status
  is_verified: z.boolean()
    .default(false),

  verified_by: z.string()
    .min(1, 'Verifier is required')
    .optional(),

  verified_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Verification date must be a valid date',
    })
    .optional(),

  // References
  tags: z.array(z.string().min(1))
    .default([]),

  notes: z.string()
    .max(1000, 'Notes must be less than 1000 characters')
    .optional(),
});

/**
 * Compliance Evidence Update Schema
 * All fields optional for partial updates
 */
export const complianceEvidenceUpdateSchema = z.object({
  evidence_title: z.string()
    .min(3, 'Evidence title must be at least 3 characters')
    .max(200, 'Evidence title must be less than 200 characters')
    .optional(),

  evidence_type: z.nativeEnum(EvidenceType).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  file_name: z.string()
    .min(1, 'File name is required')
    .max(255, 'File name must be less than 255 characters')
    .optional(),

  file_path: z.string()
    .min(1, 'File path is required')
    .max(500, 'File path must be less than 500 characters')
    .optional(),

  file_size: z.number()
    .int('File size must be an integer')
    .min(0, 'File size must be non-negative')
    .optional(),

  mime_type: z.string()
    .max(100, 'MIME type must be less than 100 characters')
    .optional(),

  collected_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Collection date must be a valid date',
    })
    .optional(),

  expiry_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Expiry date must be a valid date',
    })
    .optional(),

  is_verified: z.boolean().optional(),
  verified_by: z.string().min(1, 'Verifier is required').optional(),

  verified_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Verification date must be a valid date',
    })
    .optional(),

  tags: z.array(z.string().min(1)).optional(),
  notes: z.string()
    .max(1000, 'Notes must be less than 1000 characters')
    .optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// COMPLIANCE AUDIT SCHEMAS
// =============================================================================

/**
 * Compliance Audit Create Schema
 * Validates compliance audits (internal and external)
 */
export const complianceAuditCreateSchema = z.object({
  program_id: z.string()
    .min(1, 'Program ID is required'),

  // Audit Details
  audit_title: z.string()
    .min(3, 'Audit title must be at least 3 characters')
    .max(200, 'Audit title must be less than 200 characters'),

  audit_type: z.nativeEnum(AuditType, {
    errorMap: () => ({ message: 'Valid audit type is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  scope: z.string()
    .min(10, 'Scope must be at least 10 characters')
    .max(2000, 'Scope must be less than 2000 characters')
    .optional(),

  // Audit Team
  lead_auditor_id: z.string()
    .min(1, 'Lead auditor is required'),

  audit_team_ids: z.array(z.string().min(1))
    .default([]),

  external_auditor_name: z.string()
    .max(200, 'External auditor name must be less than 200 characters')
    .optional(),

  external_auditor_email: z.string()
    .email('Valid email address is required')
    .optional(),

  // Timeline
  scheduled_start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Scheduled start date must be a valid date',
    }),

  scheduled_end_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Scheduled end date must be a valid date',
    }),

  actual_start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Actual start date must be a valid date',
    })
    .optional(),

  actual_end_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Actual end date must be a valid date',
    })
    .optional(),

  // Status
  status: z.enum(['planned', 'in_progress', 'completed', 'cancelled'], {
    errorMap: () => ({ message: 'Valid audit status is required' }),
  }),

  // Results
  findings_summary: z.string()
    .max(2000, 'Findings summary must be less than 2000 characters')
    .optional(),

  overall_rating: z.enum(['excellent', 'good', 'satisfactory', 'needs_improvement', 'unsatisfactory'])
    .optional(),

  conformities_count: z.number()
    .int('Conformities count must be an integer')
    .min(0, 'Conformities count must be non-negative')
    .default(0),

  non_conformities_count: z.number()
    .int('Non-conformities count must be an integer')
    .min(0, 'Non-conformities count must be non-negative')
    .default(0),

  observations_count: z.number()
    .int('Observations count must be an integer')
    .min(0, 'Observations count must be non-negative')
    .default(0),

  recommendations: z.string()
    .max(2000, 'Recommendations must be less than 2000 characters')
    .optional(),

  // Metadata
  created_by: z.string()
    .min(1, 'Creator is required'),

  report_file_path: z.string()
    .max(500, 'Report file path must be less than 500 characters')
    .optional(),
})
  // Business Rule: scheduled_end_date must be after scheduled_start_date
  .refine(
    (data) => {
      if (!data.scheduled_start_date || !data.scheduled_end_date) return true;
      const start = new Date(data.scheduled_start_date);
      const end = new Date(data.scheduled_end_date);
      return end >= start;
    },
    {
      message: 'Scheduled end date must be after or equal to scheduled start date',
      path: ['scheduled_end_date'],
    }
  )
  // Business Rule: actual_end_date must be after actual_start_date
  .refine(
    (data) => {
      if (!data.actual_start_date || !data.actual_end_date) return true;
      const start = new Date(data.actual_start_date);
      const end = new Date(data.actual_end_date);
      return end >= start;
    },
    {
      message: 'Actual end date must be after or equal to actual start date',
      path: ['actual_end_date'],
    }
  );

/**
 * Compliance Audit Update Schema
 * All fields optional for partial updates
 */
export const complianceAuditUpdateSchema = z.object({
  audit_title: z.string()
    .min(3, 'Audit title must be at least 3 characters')
    .max(200, 'Audit title must be less than 200 characters')
    .optional(),

  audit_type: z.nativeEnum(AuditType).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  scope: z.string()
    .min(10, 'Scope must be at least 10 characters')
    .max(2000, 'Scope must be less than 2000 characters')
    .optional(),

  lead_auditor_id: z.string().min(1, 'Lead auditor is required').optional(),
  audit_team_ids: z.array(z.string().min(1)).optional(),

  external_auditor_name: z.string()
    .max(200, 'External auditor name must be less than 200 characters')
    .optional(),

  external_auditor_email: z.string()
    .email('Valid email address is required')
    .optional(),

  scheduled_start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Scheduled start date must be a valid date',
    })
    .optional(),

  scheduled_end_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Scheduled end date must be a valid date',
    })
    .optional(),

  actual_start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Actual start date must be a valid date',
    })
    .optional(),

  actual_end_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Actual end date must be a valid date',
    })
    .optional(),

  status: z.enum(['planned', 'in_progress', 'completed', 'cancelled']).optional(),

  findings_summary: z.string()
    .max(2000, 'Findings summary must be less than 2000 characters')
    .optional(),

  overall_rating: z.enum(['excellent', 'good', 'satisfactory', 'needs_improvement', 'unsatisfactory']).optional(),

  conformities_count: z.number()
    .int('Conformities count must be an integer')
    .min(0, 'Conformities count must be non-negative')
    .optional(),

  non_conformities_count: z.number()
    .int('Non-conformities count must be an integer')
    .min(0, 'Non-conformities count must be non-negative')
    .optional(),

  observations_count: z.number()
    .int('Observations count must be an integer')
    .min(0, 'Observations count must be non-negative')
    .optional(),

  recommendations: z.string()
    .max(2000, 'Recommendations must be less than 2000 characters')
    .optional(),

  report_file_path: z.string()
    .max(500, 'Report file path must be less than 500 characters')
    .optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// COMPLIANCE MAPPING SCHEMAS
// =============================================================================

/**
 * Compliance Mapping Create Schema
 * Validates framework-to-framework and control mappings
 */
export const complianceMappingCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  // Source
  source_framework: z.nativeEnum(FrameworkType, {
    errorMap: () => ({ message: 'Valid source framework is required' }),
  }),

  source_control_id: z.string()
    .min(1, 'Source control ID is required')
    .max(100, 'Source control ID must be less than 100 characters'),

  source_control_title: z.string()
    .min(1, 'Source control title is required')
    .max(200, 'Source control title must be less than 200 characters'),

  // Target
  target_framework: z.nativeEnum(FrameworkType, {
    errorMap: () => ({ message: 'Valid target framework is required' }),
  }),

  target_control_id: z.string()
    .min(1, 'Target control ID is required')
    .max(100, 'Target control ID must be less than 100 characters'),

  target_control_title: z.string()
    .min(1, 'Target control title is required')
    .max(200, 'Target control title must be less than 200 characters'),

  // Mapping Details
  mapping_type: z.enum(['full', 'partial', 'related', 'subset'], {
    errorMap: () => ({ message: 'Valid mapping type is required' }),
  }),

  mapping_strength: z.number()
    .int('Mapping strength must be an integer')
    .min(0, 'Mapping strength must be between 0 and 100')
    .max(100, 'Mapping strength must be between 0 and 100')
    .default(100),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  implementation_notes: z.string()
    .max(1000, 'Implementation notes must be less than 1000 characters')
    .optional(),

  // Metadata
  created_by: z.string()
    .min(1, 'Creator is required'),

  is_active: z.boolean()
    .default(true),
});

/**
 * Compliance Mapping Update Schema
 * All fields optional for partial updates
 */
export const complianceMappingUpdateSchema = z.object({
  source_control_id: z.string()
    .min(1, 'Source control ID is required')
    .max(100, 'Source control ID must be less than 100 characters')
    .optional(),

  source_control_title: z.string()
    .min(1, 'Source control title is required')
    .max(200, 'Source control title must be less than 200 characters')
    .optional(),

  target_control_id: z.string()
    .min(1, 'Target control ID is required')
    .max(100, 'Target control ID must be less than 100 characters')
    .optional(),

  target_control_title: z.string()
    .min(1, 'Target control title is required')
    .max(200, 'Target control title must be less than 200 characters')
    .optional(),

  mapping_type: z.enum(['full', 'partial', 'related', 'subset']).optional(),

  mapping_strength: z.number()
    .int('Mapping strength must be an integer')
    .min(0, 'Mapping strength must be between 0 and 100')
    .max(100, 'Mapping strength must be between 0 and 100')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  implementation_notes: z.string()
    .max(1000, 'Implementation notes must be less than 1000 characters')
    .optional(),

  is_active: z.boolean().optional(),
})
  .refine(
    (data) => {
      const keys = Object.keys(data);
      return keys.length > 0;
    },
    {
      message: 'At least one field must be provided for update',
    }
  );

// =============================================================================
// TYPE EXPORTS
// =============================================================================

/**
 * Type exports for TypeScript inference
 * These types are automatically inferred from the Zod schemas above
 */

// Program Types
export type ComplianceProgramCreate = z.infer<typeof complianceProgramCreateSchema>;
export type ComplianceProgramUpdate = z.infer<typeof complianceProgramUpdateSchema>;

// Requirement Types
export type ComplianceRequirementCreate = z.infer<typeof complianceRequirementCreateSchema>;
export type ComplianceRequirementUpdate = z.infer<typeof complianceRequirementUpdateSchema>;

// Assessment Types
export type ComplianceAssessmentCreate = z.infer<typeof complianceAssessmentCreateSchema>;
export type ComplianceAssessmentUpdate = z.infer<typeof complianceAssessmentUpdateSchema>;

// Gap Types
export type ComplianceGapCreate = z.infer<typeof complianceGapCreateSchema>;
export type ComplianceGapUpdate = z.infer<typeof complianceGapUpdateSchema>;

// Corrective Action Types
export type CorrectiveActionCreate = z.infer<typeof correctiveActionCreateSchema>;
export type CorrectiveActionUpdate = z.infer<typeof correctiveActionUpdateSchema>;

// Evidence Types
export type ComplianceEvidenceCreate = z.infer<typeof complianceEvidenceCreateSchema>;
export type ComplianceEvidenceUpdate = z.infer<typeof complianceEvidenceUpdateSchema>;

// Audit Types
export type ComplianceAuditCreate = z.infer<typeof complianceAuditCreateSchema>;
export type ComplianceAuditUpdate = z.infer<typeof complianceAuditUpdateSchema>;

// Mapping Types
export type ComplianceMappingCreate = z.infer<typeof complianceMappingCreateSchema>;
export type ComplianceMappingUpdate = z.infer<typeof complianceMappingUpdateSchema>;
