/**
 * Incident Response Module - Validation Schemas
 * Zod schemas for incident response management data validation
 *
 * Created: 2025-10-24
 * Agent: 23 (Response Module Round 1)
 * Module: Incident Response
 */

import { z } from 'zod';

// =============================================================================
// ENUMS (Will be imported from @/types/response once Agent 22 completes)
// =============================================================================

/**
 * Incident Status Enumeration
 * Status of security incidents
 */
export enum IncidentStatus {
  REPORTED = 'reported',
  INVESTIGATING = 'investigating',
  CONTAINED = 'contained',
  ERADICATED = 'eradicated',
  RECOVERED = 'recovered',
  CLOSED = 'closed',
  REOPENED = 'reopened',
}

/**
 * Incident Severity Enumeration
 * Severity levels for security incidents
 */
export enum IncidentSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  INFORMATIONAL = 'informational',
}

/**
 * Incident Category Enumeration
 * Types of security incidents
 */
export enum IncidentCategory {
  DATA_BREACH = 'data_breach',
  MALWARE = 'malware',
  PHISHING = 'phishing',
  DDOS = 'ddos',
  UNAUTHORIZED_ACCESS = 'unauthorized_access',
  INSIDER_THREAT = 'insider_threat',
  SYSTEM_COMPROMISE = 'system_compromise',
  POLICY_VIOLATION = 'policy_violation',
  OTHER = 'other',
}

/**
 * Response Plan Status Enumeration
 * Status of response plans
 */
export enum ResponsePlanStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ARCHIVED = 'archived',
  UNDER_REVIEW = 'under_review',
}

/**
 * Response Action Status Enumeration
 * Status of response actions
 */
export enum ResponseActionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  BLOCKED = 'blocked',
  CANCELLED = 'cancelled',
  VERIFIED = 'verified',
}

/**
 * Response Action Priority Enumeration
 * Priority levels for response actions
 */
export enum ResponseActionPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Team Member Role Enumeration
 * Roles for response team members
 */
export enum TeamMemberRole {
  INCIDENT_COMMANDER = 'incident_commander',
  TECHNICAL_LEAD = 'technical_lead',
  COMMUNICATIONS_LEAD = 'communications_lead',
  LEGAL_ADVISOR = 'legal_advisor',
  SECURITY_ANALYST = 'security_analyst',
  FORENSICS_SPECIALIST = 'forensics_specialist',
  MEMBER = 'member',
}

/**
 * Escalation Trigger Type Enumeration
 * Types of escalation triggers
 */
export enum EscalationTriggerType {
  SEVERITY = 'severity',
  DURATION = 'duration',
  IMPACT = 'impact',
  DATA_SENSITIVITY = 'data_sensitivity',
  MANUAL = 'manual',
}

/**
 * Communication Channel Enumeration
 * Communication channels for incident response
 */
export enum CommunicationChannel {
  EMAIL = 'email',
  PHONE = 'phone',
  SLACK = 'slack',
  TEAMS = 'teams',
  SMS = 'sms',
  IN_PERSON = 'in_person',
  VIDEO_CONFERENCE = 'video_conference',
}

/**
 * Resource Type Enumeration
 * Types of resources for incident response
 */
export enum ResourceType {
  PERSONNEL = 'personnel',
  TOOL = 'tool',
  SYSTEM = 'system',
  DOCUMENTATION = 'documentation',
  BUDGET = 'budget',
}

// =============================================================================
// INCIDENT SCHEMAS
// =============================================================================

/**
 * Incident Create Schema
 * Validates all required fields for creating a new security incident
 */
export const incidentCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  // Incident Details
  title: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters'),

  incident_id: z.string()
    .min(3, 'Incident ID must be at least 3 characters')
    .max(100, 'Incident ID must be less than 100 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters'),

  category: z.nativeEnum(IncidentCategory, {
    errorMap: () => ({ message: 'Valid incident category is required' }),
  }),

  severity: z.nativeEnum(IncidentSeverity, {
    errorMap: () => ({ message: 'Valid severity level is required' }),
  }),

  status: z.nativeEnum(IncidentStatus, {
    errorMap: () => ({ message: 'Valid incident status is required' }),
  }),

  // Detection & Reporting
  detected_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Detection date must be a valid date',
    }),

  reported_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Reported date must be a valid date',
    })
    .optional(),

  reported_by: z.string()
    .min(1, 'Reporter is required')
    .max(200, 'Reporter must be less than 200 characters'),

  detection_source: z.string()
    .max(200, 'Detection source must be less than 200 characters')
    .optional(),

  // Assignment
  assigned_to: z.string()
    .min(1, 'Assigned user is required')
    .optional(),

  response_team_id: z.string()
    .min(1, 'Response team ID is required')
    .optional(),

  response_plan_id: z.string()
    .min(1, 'Response plan ID is required')
    .optional(),

  // Impact Assessment
  affected_systems: z.array(z.string().min(1))
    .default([]),

  affected_data_types: z.array(z.string().min(1))
    .default([]),

  affected_users_count: z.number()
    .int('Affected users count must be an integer')
    .min(0, 'Affected users count must be non-negative')
    .optional(),

  estimated_impact: z.string()
    .max(1000, 'Estimated impact must be less than 1000 characters')
    .optional(),

  financial_impact: z.number()
    .nonnegative('Financial impact must be non-negative')
    .optional(),

  // Timeline
  containment_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Containment date must be a valid date',
    })
    .optional(),

  eradication_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Eradication date must be a valid date',
    })
    .optional(),

  recovery_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Recovery date must be a valid date',
    })
    .optional(),

  closed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Closed date must be a valid date',
    })
    .optional(),

  // Analysis
  root_cause: z.string()
    .max(2000, 'Root cause must be less than 2000 characters')
    .optional(),

  lessons_learned: z.string()
    .max(2000, 'Lessons learned must be less than 2000 characters')
    .optional(),

  // Metadata
  tags: z.array(z.string().min(1))
    .default([]),

  is_confidential: z.boolean()
    .default(false),

  requires_notification: z.boolean()
    .default(false),

  notification_sent_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Notification sent date must be a valid date',
    })
    .optional(),

  created_by: z.string()
    .min(1, 'Creator is required'),
})
  // Business Rule: reported_at must be after or equal to detected_at
  .refine(
    (data) => {
      if (!data.detected_at || !data.reported_at) return true;
      const detected = new Date(data.detected_at);
      const reported = new Date(data.reported_at);
      return reported >= detected;
    },
    {
      message: 'Reported date must be after or equal to detection date',
      path: ['reported_at'],
    }
  )
  // Business Rule: containment_at must be after detected_at
  .refine(
    (data) => {
      if (!data.detected_at || !data.containment_at) return true;
      const detected = new Date(data.detected_at);
      const containment = new Date(data.containment_at);
      return containment >= detected;
    },
    {
      message: 'Containment date must be after or equal to detection date',
      path: ['containment_at'],
    }
  );

/**
 * Incident Update Schema
 * All fields optional for partial updates
 */
export const incidentUpdateSchema = z.object({
  title: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  category: z.nativeEnum(IncidentCategory).optional(),
  severity: z.nativeEnum(IncidentSeverity).optional(),
  status: z.nativeEnum(IncidentStatus).optional(),

  detected_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Detection date must be a valid date',
    })
    .optional(),

  reported_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Reported date must be a valid date',
    })
    .optional(),

  reported_by: z.string()
    .min(1, 'Reporter is required')
    .max(200, 'Reporter must be less than 200 characters')
    .optional(),

  detection_source: z.string()
    .max(200, 'Detection source must be less than 200 characters')
    .optional(),

  assigned_to: z.string().min(1, 'Assigned user is required').optional(),
  response_team_id: z.string().min(1, 'Response team ID is required').optional(),
  response_plan_id: z.string().min(1, 'Response plan ID is required').optional(),

  affected_systems: z.array(z.string().min(1)).optional(),
  affected_data_types: z.array(z.string().min(1)).optional(),

  affected_users_count: z.number()
    .int('Affected users count must be an integer')
    .min(0, 'Affected users count must be non-negative')
    .optional(),

  estimated_impact: z.string()
    .max(1000, 'Estimated impact must be less than 1000 characters')
    .optional(),

  financial_impact: z.number()
    .nonnegative('Financial impact must be non-negative')
    .optional(),

  containment_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Containment date must be a valid date',
    })
    .optional(),

  eradication_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Eradication date must be a valid date',
    })
    .optional(),

  recovery_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Recovery date must be a valid date',
    })
    .optional(),

  closed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Closed date must be a valid date',
    })
    .optional(),

  root_cause: z.string()
    .max(2000, 'Root cause must be less than 2000 characters')
    .optional(),

  lessons_learned: z.string()
    .max(2000, 'Lessons learned must be less than 2000 characters')
    .optional(),

  tags: z.array(z.string().min(1)).optional(),
  is_confidential: z.boolean().optional(),
  requires_notification: z.boolean().optional(),

  notification_sent_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Notification sent date must be a valid date',
    })
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
// RESPONSE PLAN SCHEMAS
// =============================================================================

/**
 * Response Plan Create Schema
 * Validates incident response plan creation
 */
export const responsePlanCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  // Plan Details
  plan_name: z.string()
    .min(3, 'Plan name must be at least 3 characters')
    .max(200, 'Plan name must be less than 200 characters'),

  plan_code: z.string()
    .min(2, 'Plan code must be at least 2 characters')
    .max(50, 'Plan code must be less than 50 characters')
    .optional(),

  plan_version: z.string()
    .max(20, 'Plan version must be less than 20 characters')
    .default('1.0'),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters'),

  // Scope
  applicable_categories: z.array(z.nativeEnum(IncidentCategory))
    .default([]),

  applicable_severities: z.array(z.nativeEnum(IncidentSeverity))
    .default([]),

  scope_description: z.string()
    .min(10, 'Scope description must be at least 10 characters')
    .max(2000, 'Scope must be less than 2000 characters')
    .optional(),

  // Response Details
  activation_criteria: z.string()
    .min(10, 'Activation criteria must be at least 10 characters')
    .max(1000, 'Activation criteria must be less than 1000 characters'),

  response_objectives: z.array(z.string().min(1))
    .default([]),

  response_procedures: z.string()
    .min(10, 'Response procedures must be at least 10 characters')
    .max(2000, 'Response procedures must be less than 2000 characters')
    .optional(),

  // Escalation
  escalation_criteria: z.string()
    .max(1000, 'Escalation criteria must be less than 1000 characters')
    .optional(),

  escalation_contacts: z.array(z.string().email('Valid email address is required'))
    .default([]),

  // Timeline
  max_response_time_minutes: z.number()
    .int('Max response time must be an integer')
    .min(1, 'Max response time must be at least 1 minute')
    .optional(),

  max_resolution_time_hours: z.number()
    .int('Max resolution time must be an integer')
    .min(1, 'Max resolution time must be at least 1 hour')
    .optional(),

  // Status
  status: z.nativeEnum(ResponsePlanStatus, {
    errorMap: () => ({ message: 'Valid plan status is required' }),
  }),

  approved_by: z.string()
    .max(200, 'Approved by must be less than 200 characters')
    .optional(),

  approved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Approved date must be a valid date',
    })
    .optional(),

  last_tested_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last tested date must be a valid date',
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

  // Metadata
  created_by: z.string()
    .min(1, 'Creator is required'),

  is_active: z.boolean()
    .default(true),
});

/**
 * Response Plan Update Schema
 * All fields optional for partial updates
 */
export const responsePlanUpdateSchema = z.object({
  plan_name: z.string()
    .min(3, 'Plan name must be at least 3 characters')
    .max(200, 'Plan name must be less than 200 characters')
    .optional(),

  plan_code: z.string()
    .min(2, 'Plan code must be at least 2 characters')
    .max(50, 'Plan code must be less than 50 characters')
    .optional(),

  plan_version: z.string()
    .max(20, 'Plan version must be less than 20 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  applicable_categories: z.array(z.nativeEnum(IncidentCategory)).optional(),
  applicable_severities: z.array(z.nativeEnum(IncidentSeverity)).optional(),

  scope_description: z.string()
    .min(10, 'Scope description must be at least 10 characters')
    .max(2000, 'Scope must be less than 2000 characters')
    .optional(),

  activation_criteria: z.string()
    .min(10, 'Activation criteria must be at least 10 characters')
    .max(1000, 'Activation criteria must be less than 1000 characters')
    .optional(),

  response_objectives: z.array(z.string().min(1)).optional(),

  response_procedures: z.string()
    .min(10, 'Response procedures must be at least 10 characters')
    .max(2000, 'Response procedures must be less than 2000 characters')
    .optional(),

  escalation_criteria: z.string()
    .max(1000, 'Escalation criteria must be less than 1000 characters')
    .optional(),

  escalation_contacts: z.array(z.string().email('Valid email address is required')).optional(),

  max_response_time_minutes: z.number()
    .int('Max response time must be an integer')
    .min(1, 'Max response time must be at least 1 minute')
    .optional(),

  max_resolution_time_hours: z.number()
    .int('Max resolution time must be an integer')
    .min(1, 'Max resolution time must be at least 1 hour')
    .optional(),

  status: z.nativeEnum(ResponsePlanStatus).optional(),

  approved_by: z.string()
    .max(200, 'Approved by must be less than 200 characters')
    .optional(),

  approved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Approved date must be a valid date',
    })
    .optional(),

  last_tested_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last tested date must be a valid date',
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
// RESPONSE TEAM SCHEMAS
// =============================================================================

/**
 * Response Team Create Schema
 * Validates incident response team creation
 */
export const responseTeamCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  // Team Details
  team_name: z.string()
    .min(3, 'Team name must be at least 3 characters')
    .max(200, 'Team name must be less than 200 characters'),

  team_code: z.string()
    .min(2, 'Team code must be at least 2 characters')
    .max(50, 'Team code must be less than 50 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  // Leadership
  team_lead_id: z.string()
    .min(1, 'Team lead is required'),

  deputy_lead_id: z.string()
    .min(1, 'Deputy lead is required')
    .optional(),

  // Availability
  availability_24_7: z.boolean()
    .default(false),

  on_call_schedule: z.string()
    .max(500, 'On-call schedule must be less than 500 characters')
    .optional(),

  // Contact Information
  primary_contact_email: z.string()
    .email('Valid email address is required'),

  primary_contact_phone: z.string()
    .max(50, 'Primary contact phone must be less than 50 characters')
    .optional(),

  secondary_contact_email: z.string()
    .email('Valid email address is required')
    .optional(),

  escalation_email: z.string()
    .email('Valid email address is required')
    .optional(),

  // Metadata
  created_by: z.string()
    .min(1, 'Creator is required'),

  is_active: z.boolean()
    .default(true),

  tags: z.array(z.string().min(1))
    .default([]),
});

/**
 * Response Team Update Schema
 * All fields optional for partial updates
 */
export const responseTeamUpdateSchema = z.object({
  team_name: z.string()
    .min(3, 'Team name must be at least 3 characters')
    .max(200, 'Team name must be less than 200 characters')
    .optional(),

  team_code: z.string()
    .min(2, 'Team code must be at least 2 characters')
    .max(50, 'Team code must be less than 50 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  team_lead_id: z.string().min(1, 'Team lead is required').optional(),
  deputy_lead_id: z.string().min(1, 'Deputy lead is required').optional(),

  availability_24_7: z.boolean().optional(),

  on_call_schedule: z.string()
    .max(500, 'On-call schedule must be less than 500 characters')
    .optional(),

  primary_contact_email: z.string()
    .email('Valid email address is required')
    .optional(),

  primary_contact_phone: z.string()
    .max(50, 'Primary contact phone must be less than 50 characters')
    .optional(),

  secondary_contact_email: z.string()
    .email('Valid email address is required')
    .optional(),

  escalation_email: z.string()
    .email('Valid email address is required')
    .optional(),

  is_active: z.boolean().optional(),
  tags: z.array(z.string().min(1)).optional(),
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
// RESPONSE ACTION SCHEMAS
// =============================================================================

/**
 * Response Action Create Schema
 * Validates response action creation for incidents
 */
export const responseActionCreateSchema = z.object({
  incident_id: z.string()
    .min(1, 'Incident ID is required'),

  response_plan_id: z.string()
    .min(1, 'Response plan ID is required')
    .optional(),

  // Action Details
  action_title: z.string()
    .min(3, 'Action title must be at least 3 characters')
    .max(200, 'Action title must be less than 200 characters'),

  action_description: z.string()
    .min(10, 'Action description must be at least 10 characters')
    .max(2000, 'Action description must be less than 2000 characters'),

  action_type: z.enum(['containment', 'eradication', 'recovery', 'investigation', 'communication', 'documentation', 'prevention'], {
    errorMap: () => ({ message: 'Valid action type is required' }),
  }),

  priority: z.nativeEnum(ResponseActionPriority, {
    errorMap: () => ({ message: 'Valid priority is required' }),
  }),

  // Assignment
  assigned_to: z.string()
    .min(1, 'Assigned user is required'),

  assigned_by: z.string()
    .min(1, 'Assigner is required'),

  team_id: z.string()
    .min(1, 'Team ID is required')
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

  estimated_duration_minutes: z.number()
    .int('Estimated duration must be an integer')
    .min(1, 'Estimated duration must be at least 1 minute')
    .optional(),

  actual_duration_minutes: z.number()
    .int('Actual duration must be an integer')
    .min(0, 'Actual duration must be non-negative')
    .optional(),

  // Status & Progress
  status: z.nativeEnum(ResponseActionStatus, {
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

  result: z.string()
    .max(2000, 'Result must be less than 2000 characters')
    .optional(),

  verification_notes: z.string()
    .max(1000, 'Verification notes must be less than 1000 characters')
    .optional(),

  // Dependencies
  depends_on: z.array(z.string().min(1))
    .default([]),

  blocks: z.array(z.string().min(1))
    .default([]),

  // Metadata
  requires_approval: z.boolean()
    .default(false),

  approved_by: z.string()
    .max(200, 'Approved by must be less than 200 characters')
    .optional(),

  approved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Approval date must be a valid date',
    })
    .optional(),
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
 * Response Action Update Schema
 * All fields optional for partial updates
 */
export const responseActionUpdateSchema = z.object({
  action_title: z.string()
    .min(3, 'Action title must be at least 3 characters')
    .max(200, 'Action title must be less than 200 characters')
    .optional(),

  action_description: z.string()
    .min(10, 'Action description must be at least 10 characters')
    .max(2000, 'Action description must be less than 2000 characters')
    .optional(),

  action_type: z.enum(['containment', 'eradication', 'recovery', 'investigation', 'communication', 'documentation', 'prevention']).optional(),
  priority: z.nativeEnum(ResponseActionPriority).optional(),

  assigned_to: z.string().min(1, 'Assigned user is required').optional(),
  team_id: z.string().min(1, 'Team ID is required').optional(),

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

  estimated_duration_minutes: z.number()
    .int('Estimated duration must be an integer')
    .min(1, 'Estimated duration must be at least 1 minute')
    .optional(),

  actual_duration_minutes: z.number()
    .int('Actual duration must be an integer')
    .min(0, 'Actual duration must be non-negative')
    .optional(),

  status: z.nativeEnum(ResponseActionStatus).optional(),

  progress_percentage: z.number()
    .int('Progress percentage must be an integer')
    .min(0, 'Progress percentage must be between 0 and 100')
    .max(100, 'Progress percentage must be between 0 and 100')
    .optional(),

  implementation_notes: z.string()
    .max(2000, 'Implementation notes must be less than 2000 characters')
    .optional(),

  result: z.string()
    .max(2000, 'Result must be less than 2000 characters')
    .optional(),

  verification_notes: z.string()
    .max(1000, 'Verification notes must be less than 1000 characters')
    .optional(),

  depends_on: z.array(z.string().min(1)).optional(),
  blocks: z.array(z.string().min(1)).optional(),

  requires_approval: z.boolean().optional(),

  approved_by: z.string()
    .max(200, 'Approved by must be less than 200 characters')
    .optional(),

  approved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Approval date must be a valid date',
    })
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
// INCIDENT LOG SCHEMAS
// =============================================================================

/**
 * Incident Log Create Schema
 * Validates incident log entries for timeline tracking
 */
export const incidentLogCreateSchema = z.object({
  incident_id: z.string()
    .min(1, 'Incident ID is required'),

  // Log Details
  log_type: z.enum(['event', 'action', 'observation', 'decision', 'communication', 'status_change'], {
    errorMap: () => ({ message: 'Valid log type is required' }),
  }),

  title: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters'),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters'),

  // Timestamp
  occurred_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Occurred date must be a valid date',
    }),

  // Metadata
  logged_by: z.string()
    .min(1, 'Logger is required'),

  related_action_id: z.string()
    .min(1, 'Related action ID is required')
    .optional(),

  severity: z.nativeEnum(IncidentSeverity)
    .optional(),

  tags: z.array(z.string().min(1))
    .default([]),

  attachments: z.array(z.string().min(1))
    .default([]),
});

/**
 * Incident Log Update Schema
 * All fields optional for partial updates
 */
export const incidentLogUpdateSchema = z.object({
  log_type: z.enum(['event', 'action', 'observation', 'decision', 'communication', 'status_change']).optional(),

  title: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  occurred_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Occurred date must be a valid date',
    })
    .optional(),

  related_action_id: z.string().min(1, 'Related action ID is required').optional(),
  severity: z.nativeEnum(IncidentSeverity).optional(),
  tags: z.array(z.string().min(1)).optional(),
  attachments: z.array(z.string().min(1)).optional(),
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
// ESCALATION RULE SCHEMAS
// =============================================================================

/**
 * Escalation Rule Create Schema
 * Validates automatic escalation rules for incidents
 */
export const escalationRuleCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  response_plan_id: z.string()
    .min(1, 'Response plan ID is required')
    .optional(),

  // Rule Details
  rule_name: z.string()
    .min(3, 'Rule name must be at least 3 characters')
    .max(200, 'Rule name must be less than 200 characters'),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  // Trigger Conditions
  trigger_type: z.nativeEnum(EscalationTriggerType, {
    errorMap: () => ({ message: 'Valid trigger type is required' }),
  }),

  trigger_conditions: z.object({
    severity_levels: z.array(z.nativeEnum(IncidentSeverity)).optional(),
    categories: z.array(z.nativeEnum(IncidentCategory)).optional(),
    duration_minutes: z.number().int().min(1).optional(),
    financial_threshold: z.number().nonnegative().optional(),
    affected_users_threshold: z.number().int().min(1).optional(),
  }),

  // Escalation Actions
  escalate_to_user_id: z.string()
    .min(1, 'Escalate to user is required')
    .optional(),

  escalate_to_team_id: z.string()
    .min(1, 'Escalate to team is required')
    .optional(),

  notification_emails: z.array(z.string().email('Valid email address is required'))
    .default([]),

  notification_template: z.string()
    .max(1000, 'Notification template must be less than 1000 characters')
    .optional(),

  // Configuration
  priority: z.number()
    .int('Priority must be an integer')
    .min(1, 'Priority must be at least 1')
    .default(1),

  is_active: z.boolean()
    .default(true),

  // Metadata
  created_by: z.string()
    .min(1, 'Creator is required'),
});

/**
 * Escalation Rule Update Schema
 * All fields optional for partial updates
 */
export const escalationRuleUpdateSchema = z.object({
  rule_name: z.string()
    .min(3, 'Rule name must be at least 3 characters')
    .max(200, 'Rule name must be less than 200 characters')
    .optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),

  trigger_type: z.nativeEnum(EscalationTriggerType).optional(),

  trigger_conditions: z.object({
    severity_levels: z.array(z.nativeEnum(IncidentSeverity)).optional(),
    categories: z.array(z.nativeEnum(IncidentCategory)).optional(),
    duration_minutes: z.number().int().min(1).optional(),
    financial_threshold: z.number().nonnegative().optional(),
    affected_users_threshold: z.number().int().min(1).optional(),
  }).optional(),

  escalate_to_user_id: z.string().min(1, 'Escalate to user is required').optional(),
  escalate_to_team_id: z.string().min(1, 'Escalate to team is required').optional(),
  notification_emails: z.array(z.string().email('Valid email address is required')).optional(),

  notification_template: z.string()
    .max(1000, 'Notification template must be less than 1000 characters')
    .optional(),

  priority: z.number()
    .int('Priority must be an integer')
    .min(1, 'Priority must be at least 1')
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
// COMMUNICATION RECORD SCHEMAS
// =============================================================================

/**
 * Communication Record Create Schema
 * Validates communication records for incident response
 */
export const communicationRecordCreateSchema = z.object({
  incident_id: z.string()
    .min(1, 'Incident ID is required'),

  // Communication Details
  communication_type: z.enum(['internal', 'external', 'stakeholder', 'regulatory', 'customer'], {
    errorMap: () => ({ message: 'Valid communication type is required' }),
  }),

  channel: z.nativeEnum(CommunicationChannel, {
    errorMap: () => ({ message: 'Valid communication channel is required' }),
  }),

  subject: z.string()
    .min(3, 'Subject must be at least 3 characters')
    .max(200, 'Subject must be less than 200 characters'),

  message_content: z.string()
    .min(10, 'Message content must be at least 10 characters')
    .max(2000, 'Message content must be less than 2000 characters'),

  // Parties
  sender_id: z.string()
    .min(1, 'Sender is required'),

  sender_name: z.string()
    .max(200, 'Sender name must be less than 200 characters')
    .optional(),

  recipient_ids: z.array(z.string().min(1))
    .default([]),

  recipient_emails: z.array(z.string().email('Valid email address is required'))
    .default([]),

  cc_emails: z.array(z.string().email('Valid email address is required'))
    .default([]),

  // Timestamp
  sent_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Sent date must be a valid date',
    }),

  // Metadata
  is_confidential: z.boolean()
    .default(false),

  requires_response: z.boolean()
    .default(false),

  response_received: z.boolean()
    .default(false),

  response_received_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Response received date must be a valid date',
    })
    .optional(),

  attachments: z.array(z.string().min(1))
    .default([]),

  tags: z.array(z.string().min(1))
    .default([]),
});

/**
 * Communication Record Update Schema
 * All fields optional for partial updates
 */
export const communicationRecordUpdateSchema = z.object({
  communication_type: z.enum(['internal', 'external', 'stakeholder', 'regulatory', 'customer']).optional(),
  channel: z.nativeEnum(CommunicationChannel).optional(),

  subject: z.string()
    .min(3, 'Subject must be at least 3 characters')
    .max(200, 'Subject must be less than 200 characters')
    .optional(),

  message_content: z.string()
    .min(10, 'Message content must be at least 10 characters')
    .max(2000, 'Message content must be less than 2000 characters')
    .optional(),

  sender_name: z.string()
    .max(200, 'Sender name must be less than 200 characters')
    .optional(),

  recipient_ids: z.array(z.string().min(1)).optional(),
  recipient_emails: z.array(z.string().email('Valid email address is required')).optional(),
  cc_emails: z.array(z.string().email('Valid email address is required')).optional(),

  sent_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Sent date must be a valid date',
    })
    .optional(),

  is_confidential: z.boolean().optional(),
  requires_response: z.boolean().optional(),
  response_received: z.boolean().optional(),

  response_received_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Response received date must be a valid date',
    })
    .optional(),

  attachments: z.array(z.string().min(1)).optional(),
  tags: z.array(z.string().min(1)).optional(),
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
// RESOURCE ALLOCATION SCHEMAS
// =============================================================================

/**
 * Resource Allocation Create Schema
 * Validates resource allocation for incident response
 */
export const resourceAllocationCreateSchema = z.object({
  incident_id: z.string()
    .min(1, 'Incident ID is required'),

  response_action_id: z.string()
    .min(1, 'Response action ID is required')
    .optional(),

  // Resource Details
  resource_type: z.nativeEnum(ResourceType, {
    errorMap: () => ({ message: 'Valid resource type is required' }),
  }),

  resource_name: z.string()
    .min(3, 'Resource name must be at least 3 characters')
    .max(200, 'Resource name must be less than 200 characters'),

  resource_description: z.string()
    .max(1000, 'Resource description must be less than 1000 characters')
    .optional(),

  // Allocation
  allocated_by: z.string()
    .min(1, 'Allocator is required'),

  allocated_to: z.string()
    .min(1, 'Allocated to user is required')
    .optional(),

  team_id: z.string()
    .min(1, 'Team ID is required')
    .optional(),

  // Quantity & Cost
  quantity: z.number()
    .int('Quantity must be an integer')
    .min(1, 'Quantity must be at least 1')
    .default(1),

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  actual_cost: z.number()
    .nonnegative('Actual cost must be non-negative')
    .optional(),

  // Timeline
  allocated_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Allocation date must be a valid date',
    }),

  start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  end_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'End date must be a valid date',
    })
    .optional(),

  returned_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Return date must be a valid date',
    })
    .optional(),

  // Status
  status: z.enum(['allocated', 'in_use', 'returned', 'unavailable'], {
    errorMap: () => ({ message: 'Valid resource status is required' }),
  }),

  availability_notes: z.string()
    .max(500, 'Availability notes must be less than 500 characters')
    .optional(),

  // Metadata
  tags: z.array(z.string().min(1))
    .default([]),
})
  // Business Rule: end_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.end_date) return true;
      const start = new Date(data.start_date);
      const end = new Date(data.end_date);
      return end >= start;
    },
    {
      message: 'End date must be after or equal to start date',
      path: ['end_date'],
    }
  );

/**
 * Resource Allocation Update Schema
 * All fields optional for partial updates
 */
export const resourceAllocationUpdateSchema = z.object({
  resource_type: z.nativeEnum(ResourceType).optional(),

  resource_name: z.string()
    .min(3, 'Resource name must be at least 3 characters')
    .max(200, 'Resource name must be less than 200 characters')
    .optional(),

  resource_description: z.string()
    .max(1000, 'Resource description must be less than 1000 characters')
    .optional(),

  allocated_to: z.string().min(1, 'Allocated to user is required').optional(),
  team_id: z.string().min(1, 'Team ID is required').optional(),

  quantity: z.number()
    .int('Quantity must be an integer')
    .min(1, 'Quantity must be at least 1')
    .optional(),

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  actual_cost: z.number()
    .nonnegative('Actual cost must be non-negative')
    .optional(),

  allocated_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Allocation date must be a valid date',
    })
    .optional(),

  start_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Start date must be a valid date',
    })
    .optional(),

  end_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'End date must be a valid date',
    })
    .optional(),

  returned_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Return date must be a valid date',
    })
    .optional(),

  status: z.enum(['allocated', 'in_use', 'returned', 'unavailable']).optional(),

  availability_notes: z.string()
    .max(500, 'Availability notes must be less than 500 characters')
    .optional(),

  tags: z.array(z.string().min(1)).optional(),
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

// Incident Types
export type IncidentCreate = z.infer<typeof incidentCreateSchema>;
export type IncidentUpdate = z.infer<typeof incidentUpdateSchema>;

// Response Plan Types
export type ResponsePlanCreate = z.infer<typeof responsePlanCreateSchema>;
export type ResponsePlanUpdate = z.infer<typeof responsePlanUpdateSchema>;

// Response Team Types
export type ResponseTeamCreate = z.infer<typeof responseTeamCreateSchema>;
export type ResponseTeamUpdate = z.infer<typeof responseTeamUpdateSchema>;

// Response Action Types
export type ResponseActionCreate = z.infer<typeof responseActionCreateSchema>;
export type ResponseActionUpdate = z.infer<typeof responseActionUpdateSchema>;

// Incident Log Types
export type IncidentLogCreate = z.infer<typeof incidentLogCreateSchema>;
export type IncidentLogUpdate = z.infer<typeof incidentLogUpdateSchema>;

// Escalation Rule Types
export type EscalationRuleCreate = z.infer<typeof escalationRuleCreateSchema>;
export type EscalationRuleUpdate = z.infer<typeof escalationRuleUpdateSchema>;

// Communication Record Types
export type CommunicationRecordCreate = z.infer<typeof communicationRecordCreateSchema>;
export type CommunicationRecordUpdate = z.infer<typeof communicationRecordUpdateSchema>;

// Resource Allocation Types
export type ResourceAllocationCreate = z.infer<typeof resourceAllocationCreateSchema>;
export type ResourceAllocationUpdate = z.infer<typeof resourceAllocationUpdateSchema>;
