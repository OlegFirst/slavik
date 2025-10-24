/**
 * Planning Module - Validation Schemas
 * Zod schemas for planning module data validation
 *
 * Created: 2025-10-21
 * Agent: 2/3 (Planning Module Round 1)
 */

import { z } from 'zod';
import {
  PlanType,
  StrategyType,
  PlanStatus,
  ActionType,
  Priority,
  ActionStatus,
} from '@/types/planning';

// =============================================================================
// Supporting Type Schemas
// =============================================================================

/**
 * Resource Schema
 * Validates resources required for business continuity plans
 */
export const resourceSchema = z.object({
  resource_type: z.enum(['personnel', 'equipment', 'facility', 'technology', 'financial'], {
    errorMap: () => ({ message: 'Valid resource type is required' }),
  }),
  resource_name: z.string()
    .min(1, 'Resource name is required')
    .max(255, 'Resource name must be less than 255 characters'),
  quantity: z.number()
    .int('Quantity must be an integer')
    .min(1, 'Quantity must be at least 1')
    .optional(),
  cost_estimate: z.number()
    .nonnegative('Cost estimate must be non-negative')
    .optional(),
  availability: z.enum(['available', 'limited', 'unavailable'], {
    errorMap: () => ({ message: 'Valid availability status is required' }),
  }),
});

/**
 * Recovery Step Schema
 * Validates individual steps in a recovery strategy
 */
export const recoveryStepSchema = z.object({
  step_number: z.number()
    .int('Step number must be an integer')
    .min(1, 'Step number must be at least 1'),
  step_title: z.string()
    .min(1, 'Step title is required')
    .max(255, 'Step title must be less than 255 characters'),
  description: z.string()
    .min(10, 'Description must be at least 10 characters'),
  estimated_duration: z.number()
    .int('Estimated duration must be an integer')
    .min(1, 'Duration must be at least 1 minute'),
  responsible_role: z.string()
    .min(1, 'Responsible role is required')
    .max(255, 'Responsible role must be less than 255 characters'),
  dependencies: z.array(z.number().int())
    .default([]),
});

/**
 * Personnel Schema
 * Validates personnel assignments for recovery strategies
 */
export const personnelSchema = z.object({
  role: z.string()
    .min(1, 'Role is required')
    .max(255, 'Role must be less than 255 characters'),
  name: z.string()
    .max(255, 'Name must be less than 255 characters')
    .optional(),
  contact_info: z.string()
    .max(500, 'Contact info must be less than 500 characters')
    .optional(),
  availability: z.enum(['primary', 'backup', 'on-call'], {
    errorMap: () => ({ message: 'Valid availability status is required' }),
  }),
});

/**
 * Equipment Schema
 * Validates equipment requirements for recovery
 */
export const equipmentSchema = z.object({
  equipment_type: z.string()
    .min(1, 'Equipment type is required')
    .max(255, 'Equipment type must be less than 255 characters'),
  equipment_name: z.string()
    .min(1, 'Equipment name is required')
    .max(255, 'Equipment name must be less than 255 characters'),
  location: z.string()
    .max(500, 'Location must be less than 500 characters')
    .optional(),
  quantity: z.number()
    .int('Quantity must be an integer')
    .min(1, 'Quantity must be at least 1'),
});

/**
 * Facility Schema
 * Validates facility resources for business continuity
 */
export const facilitySchema = z.object({
  facility_type: z.enum(['primary', 'alternate', 'mobile'], {
    errorMap: () => ({ message: 'Valid facility type is required' }),
  }),
  facility_name: z.string()
    .min(1, 'Facility name is required')
    .max(255, 'Facility name must be less than 255 characters'),
  address: z.string()
    .max(500, 'Address must be less than 500 characters')
    .optional(),
  capacity: z.number()
    .int('Capacity must be an integer')
    .min(1, 'Capacity must be at least 1')
    .optional(),
});

// =============================================================================
// Business Continuity Plan Schemas
// =============================================================================

/**
 * BC Plan Create Schema
 * Validates all required fields for creating a new business continuity plan
 */
export const bcPlanCreateSchema = z.object({
  organization_id: z.string()
    .min(1, 'Organization ID is required'),

  // Metadata
  plan_name: z.string()
    .min(3, 'Plan name must be at least 3 characters')
    .max(255, 'Plan name must be less than 255 characters'),

  plan_code: z.string()
    .min(2, 'Plan code must be at least 2 characters')
    .max(50, 'Plan code must be less than 50 characters'),

  plan_type: z.nativeEnum(PlanType, {
    errorMap: () => ({ message: 'Valid plan type is required' }),
  }),

  plan_version: z.string()
    .max(20, 'Plan version must be less than 20 characters')
    .default('1.0'),

  // Scope
  scope_description: z.string()
    .min(10, 'Scope description must be at least 10 characters'),

  applicable_processes: z.array(z.string().min(1))
    .default([]),

  applicable_assets: z.array(z.string().min(1))
    .default([]),

  covered_risks: z.array(z.string().min(1))
    .default([]),

  // Objectives (time in minutes)
  rto_target: z.number()
    .int('RTO must be an integer')
    .min(1, 'RTO must be at least 1 minute'),

  rpo_target: z.number()
    .int('RPO must be an integer')
    .min(0, 'RPO cannot be negative'),

  mtpd_target: z.number()
    .int('MTPD must be an integer')
    .min(1, 'MTPD must be at least 1 minute'),

  // Strategy
  strategy_type: z.nativeEnum(StrategyType, {
    errorMap: () => ({ message: 'Valid strategy type is required' }),
  }),

  strategy_description: z.string()
    .min(10, 'Strategy description must be at least 10 characters'),

  // Resources
  required_resources: z.array(resourceSchema)
    .default([]),

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .default(0),

  // Status
  status: z.nativeEnum(PlanStatus, {
    errorMap: () => ({ message: 'Valid plan status is required' }),
  }),

  approved_by: z.string()
    .max(255, 'Approved by must be less than 255 characters')
    .optional(),

  approved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Approved at must be a valid date',
    })
    .optional(),

  last_reviewed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last reviewed at must be a valid date',
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
    .min(1, 'Creator is required')
    .max(255, 'Creator must be less than 255 characters'),
})
  // Business Rule: RTO must be <= MTPD
  .refine((data) => data.rto_target <= data.mtpd_target, {
    message: 'RTO must be less than or equal to MTPD',
    path: ['rto_target'],
  })
  // Business Rule: RPO should be <= RTO (data loss window should not exceed recovery time)
  .refine((data) => data.rpo_target <= data.rto_target, {
    message: 'RPO should be less than or equal to RTO',
    path: ['rpo_target'],
  });

/**
 * BC Plan Update Schema
 * All fields optional except organization_id and created_by
 */
const bcPlanUpdateBaseSchema = z.object({
  // Metadata
  plan_name: z.string()
    .min(3, 'Plan name must be at least 3 characters')
    .max(255, 'Plan name must be less than 255 characters')
    .optional(),

  plan_code: z.string()
    .min(2, 'Plan code must be at least 2 characters')
    .max(50, 'Plan code must be less than 50 characters')
    .optional(),

  plan_type: z.nativeEnum(PlanType).optional(),

  plan_version: z.string()
    .max(20, 'Plan version must be less than 20 characters')
    .optional(),

  // Scope
  scope_description: z.string()
    .min(10, 'Scope description must be at least 10 characters')
    .optional(),

  applicable_processes: z.array(z.string().min(1))
    .optional(),

  applicable_assets: z.array(z.string().min(1))
    .optional(),

  covered_risks: z.array(z.string().min(1))
    .optional(),

  // Objectives (time in minutes)
  rto_target: z.number()
    .int('RTO must be an integer')
    .min(1, 'RTO must be at least 1 minute')
    .optional(),

  rpo_target: z.number()
    .int('RPO must be an integer')
    .min(0, 'RPO cannot be negative')
    .optional(),

  mtpd_target: z.number()
    .int('MTPD must be an integer')
    .min(1, 'MTPD must be at least 1 minute')
    .optional(),

  // Strategy
  strategy_type: z.nativeEnum(StrategyType).optional(),

  strategy_description: z.string()
    .min(10, 'Strategy description must be at least 10 characters')
    .optional(),

  // Resources
  required_resources: z.array(resourceSchema)
    .optional(),

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  // Status
  status: z.nativeEnum(PlanStatus).optional(),

  approved_by: z.string()
    .max(255, 'Approved by must be less than 255 characters')
    .optional(),

  approved_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Approved at must be a valid date',
    })
    .optional(),

  last_reviewed_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last reviewed at must be a valid date',
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
});

export const bcPlanUpdateSchema = bcPlanUpdateBaseSchema.refine(
  (data) => {
    const keys = Object.keys(data);
    return keys.length > 0;
  },
  {
    message: 'At least one field must be provided for update',
  }
);

// =============================================================================
// Recovery Strategy Schemas
// =============================================================================

/**
 * Recovery Strategy Create Schema
 * Validates recovery strategy creation with steps and resources
 */
export const recoveryStrategyCreateSchema = z.object({
  plan_id: z.string()
    .min(1, 'Plan ID is required'),

  strategy_name: z.string()
    .min(3, 'Strategy name must be at least 3 characters')
    .max(255, 'Strategy name must be less than 255 characters'),

  strategy_type: z.nativeEnum(StrategyType, {
    errorMap: () => ({ message: 'Valid strategy type is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters'),

  // Timeline
  activation_trigger: z.string()
    .min(5, 'Activation trigger must be at least 5 characters')
    .max(500, 'Activation trigger must be less than 500 characters'),

  activation_time: z.number()
    .int('Activation time must be an integer')
    .min(1, 'Activation time must be at least 1 minute'),

  recovery_steps: z.array(recoveryStepSchema)
    .default([]),

  // Resources
  required_personnel: z.array(personnelSchema)
    .default([]),

  required_equipment: z.array(equipmentSchema)
    .default([]),

  required_facilities: z.array(facilitySchema)
    .default([]),

  // Testing
  last_tested_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last tested at must be a valid date',
    })
    .optional(),

  test_results: z.string()
    .max(2000, 'Test results must be less than 2000 characters')
    .optional(),

  effectiveness_rating: z.number()
    .int('Effectiveness rating must be an integer')
    .min(1, 'Effectiveness rating must be between 1 and 5')
    .max(5, 'Effectiveness rating must be between 1 and 5')
    .optional(),
});

/**
 * Recovery Strategy Update Schema
 * All fields optional except plan_id
 */
export const recoveryStrategyUpdateSchema = z.object({
  strategy_name: z.string()
    .min(3, 'Strategy name must be at least 3 characters')
    .max(255, 'Strategy name must be less than 255 characters')
    .optional(),

  strategy_type: z.nativeEnum(StrategyType).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .optional(),

  // Timeline
  activation_trigger: z.string()
    .min(5, 'Activation trigger must be at least 5 characters')
    .max(500, 'Activation trigger must be less than 500 characters')
    .optional(),

  activation_time: z.number()
    .int('Activation time must be an integer')
    .min(1, 'Activation time must be at least 1 minute')
    .optional(),

  recovery_steps: z.array(recoveryStepSchema)
    .optional(),

  // Resources
  required_personnel: z.array(personnelSchema)
    .optional(),

  required_equipment: z.array(equipmentSchema)
    .optional(),

  required_facilities: z.array(facilitySchema)
    .optional(),

  // Testing
  last_tested_at: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Last tested at must be a valid date',
    })
    .optional(),

  test_results: z.string()
    .max(2000, 'Test results must be less than 2000 characters')
    .optional(),

  effectiveness_rating: z.number()
    .int('Effectiveness rating must be an integer')
    .min(1, 'Effectiveness rating must be between 1 and 5')
    .max(5, 'Effectiveness rating must be between 1 and 5')
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
// Action Plan Schemas
// =============================================================================

/**
 * Action Plan Create Schema
 * Validates action items for plan implementation and maintenance
 */
export const actionPlanCreateSchema = z.object({
  plan_id: z.string()
    .min(1, 'Plan ID is required'),

  action_title: z.string()
    .min(3, 'Action title must be at least 3 characters')
    .max(255, 'Action title must be less than 255 characters'),

  action_type: z.nativeEnum(ActionType, {
    errorMap: () => ({ message: 'Valid action type is required' }),
  }),

  priority: z.nativeEnum(Priority, {
    errorMap: () => ({ message: 'Valid priority is required' }),
  }),

  // Details
  description: z.string()
    .min(10, 'Description must be at least 10 characters'),

  responsible_party: z.string()
    .min(1, 'Responsible party is required')
    .max(255, 'Responsible party must be less than 255 characters'),

  backup_responsible: z.string()
    .max(255, 'Backup responsible must be less than 255 characters')
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

  target_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Target date must be a valid date',
    })
    .optional(),

  completion_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Completion date must be a valid date',
    })
    .optional(),

  // Progress
  status: z.nativeEnum(ActionStatus, {
    errorMap: () => ({ message: 'Valid action status is required' }),
  }),

  progress_percentage: z.number()
    .int('Progress percentage must be an integer')
    .min(0, 'Progress percentage must be between 0 and 100')
    .max(100, 'Progress percentage must be between 0 and 100')
    .default(0),

  // Dependencies
  depends_on: z.array(z.string().min(1))
    .default([]),

  blocks: z.array(z.string().min(1))
    .default([]),
})
  // Business Rule: target_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.target_date) return true;
      const start = new Date(data.start_date);
      const target = new Date(data.target_date);
      return target >= start;
    },
    {
      message: 'Target date must be after or equal to start date',
      path: ['target_date'],
    }
  )
  // Business Rule: completion_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.completion_date) return true;
      const start = new Date(data.start_date);
      const completion = new Date(data.completion_date);
      return completion >= start;
    },
    {
      message: 'Completion date must be after or equal to start date',
      path: ['completion_date'],
    }
  );

/**
 * Action Plan Update Schema
 * All fields optional except plan_id
 */
export const actionPlanUpdateSchema = z.object({
  action_title: z.string()
    .min(3, 'Action title must be at least 3 characters')
    .max(255, 'Action title must be less than 255 characters')
    .optional(),

  action_type: z.nativeEnum(ActionType).optional(),

  priority: z.nativeEnum(Priority).optional(),

  // Details
  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .optional(),

  responsible_party: z.string()
    .min(1, 'Responsible party is required')
    .max(255, 'Responsible party must be less than 255 characters')
    .optional(),

  backup_responsible: z.string()
    .max(255, 'Backup responsible must be less than 255 characters')
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

  target_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Target date must be a valid date',
    })
    .optional(),

  completion_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Completion date must be a valid date',
    })
    .optional(),

  // Progress
  status: z.nativeEnum(ActionStatus).optional(),

  progress_percentage: z.number()
    .int('Progress percentage must be an integer')
    .min(0, 'Progress percentage must be between 0 and 100')
    .max(100, 'Progress percentage must be between 0 and 100')
    .optional(),

  // Dependencies
  depends_on: z.array(z.string().min(1))
    .optional(),

  blocks: z.array(z.string().min(1))
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
  )
  // Business Rule: target_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.target_date) return true;
      const start = new Date(data.start_date);
      const target = new Date(data.target_date);
      return target >= start;
    },
    {
      message: 'Target date must be after or equal to start date',
      path: ['target_date'],
    }
  )
  // Business Rule: completion_date must be after start_date
  .refine(
    (data) => {
      if (!data.start_date || !data.completion_date) return true;
      const start = new Date(data.start_date);
      const completion = new Date(data.completion_date);
      return completion >= start;
    },
    {
      message: 'Completion date must be after or equal to start date',
      path: ['completion_date'],
    }
  );

// =============================================================================
// Type Exports
// =============================================================================

/**
 * Type exports for TypeScript inference
 */
export type BCPlanCreateInput = z.infer<typeof bcPlanCreateSchema>;
export type BCPlanUpdateInput = z.infer<typeof bcPlanUpdateSchema>;
export type RecoveryStrategyCreateInput = z.infer<typeof recoveryStrategyCreateSchema>;
export type RecoveryStrategyUpdateInput = z.infer<typeof recoveryStrategyUpdateSchema>;
export type ActionPlanCreateInput = z.infer<typeof actionPlanCreateSchema>;
export type ActionPlanUpdateInput = z.infer<typeof actionPlanUpdateSchema>;
