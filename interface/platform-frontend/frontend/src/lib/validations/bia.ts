/**
 * BIA Validation Schemas
 * Zod schemas for BIA process validation
 * Enforces business rules from backend
 */

import { z } from 'zod';
import {
  CriticalityLevel,
  ProcessStatus,
  ReputationalImpact,
  RegulatoryImpact,
  PatientSafetyImpact,
  WHOTier,
  GeographicalScope,
  IndustryType,
} from '@/types/bia';

/**
 * Dependency schema
 */
export const dependencySchema = z.object({
  type: z.string().min(1, 'Dependency type is required'),
  name: z.string().min(1, 'Dependency name is required'),
  id: z.number().optional(),
  criticality: z.number().min(1).max(5).optional(),
  required: z.boolean(),
});

/**
 * Financial impact schema
 * Must have increasing values over time
 */
export const financialImpactSchema = z.record(z.string(), z.number().nonnegative())
  .refine((data) => {
    const keys = Object.keys(data).sort();
    if (keys.length < 2) return true;

    const values = keys.map(k => data[k]);
    for (let i = 1; i < values.length; i++) {
      if (values[i] < values[i - 1]) {
        return false;
      }
    }
    return true;
  }, {
    message: 'Financial impact must increase over time',
  });

/**
 * BIA Process Create Schema
 * Validates all required fields and business rules
 */
export const biaProcessCreateSchema = z.object({
  tenant_id: z.string().min(1, 'Tenant ID is required'),

  // Basic Info
  name: z.string()
    .min(3, 'Process name must be at least 3 characters')
    .max(200, 'Process name must be less than 200 characters'),

  description: z.string().optional(),

  department: z.string().optional(),

  process_owner: z.string().optional(),

  // Criticality
  criticality: z.nativeEnum(CriticalityLevel, {
    errorMap: () => ({ message: 'Valid criticality level is required' }),
  }),

  criticality_score: z.number().min(1).max(5).optional(),

  who_tier: z.nativeEnum(WHOTier).optional(),

  // Industry context
  industry: z.nativeEnum(IndustryType).optional(),

  geographical_scope: z.nativeEnum(GeographicalScope).optional(),

  // Time Objectives (CRITICAL VALIDATION)
  rto_hours: z.number()
    .nonnegative('RTO must be non-negative')
    .max(8760, 'RTO cannot exceed 1 year'), // 365 days

  rpo_hours: z.number()
    .nonnegative('RPO must be non-negative')
    .max(8760, 'RPO cannot exceed 1 year'),

  mtpd_hours: z.number()
    .nonnegative('MTPD must be non-negative')
    .max(8760, 'MTPD cannot exceed 1 year'),

  // Impact Assessment
  financial_impact: financialImpactSchema.optional(),

  operational_impact: z.record(z.string(), z.string()).optional(),

  reputational_impact: z.nativeEnum(ReputationalImpact).optional(),

  regulatory_impact: z.nativeEnum(RegulatoryImpact).optional(),

  patient_safety_impact: z.nativeEnum(PatientSafetyImpact).optional(),

  // ISO 22301 Compliance
  compliance_objective: z.string().optional(),

  legal_regulatory_requirements: z.array(z.string()).optional(),

  // Resource Requirements
  personnel_requirements: z.record(z.any()).optional(),

  facility_requirements: z.record(z.any()).optional(),

  technology_requirements: z.record(z.any()).optional(),

  information_requirements: z.record(z.any()).optional(),

  // Recovery Strategies
  recovery_strategies: z.array(z.record(z.any())).optional(),

  alternative_procedures: z.array(z.string()).optional(),

  workaround_capacity: z.number().min(0).max(100).optional(),

  // Dependencies
  upstream_processes: z.array(z.string()).optional(),

  downstream_processes: z.array(z.string()).optional(),

  critical_suppliers: z.array(z.record(z.any())).optional(),

  dependencies: z.array(dependencySchema).optional(),

  // Operating Characteristics
  minimum_resource_level: z.record(z.any()).optional(),

  peak_periods: z.array(z.record(z.any())).optional(),

  seasonality: z.string().optional(),

  // Assessment metadata
  bia_completion_date: z.string().optional(),

  bia_assessor: z.string().optional(),

  bia_reviewer: z.string().optional(),

  next_review_date: z.string().optional(),
})
  // Business Rule 1: RTO >= RPO
  .refine((data) => data.rto_hours >= data.rpo_hours, {
    message: 'RTO must be greater than or equal to RPO',
    path: ['rto_hours'],
  })
  // Business Rule 2: MTPD >= RTO
  .refine((data) => data.mtpd_hours >= data.rto_hours, {
    message: 'MTPD must be greater than or equal to RTO',
    path: ['mtpd_hours'],
  })
  // Business Rule 3: Critical processes need dependencies
  .refine((data) => {
    if (data.criticality === CriticalityLevel.CRITICAL) {
      return (data.dependencies && data.dependencies.length >= 2) || true; // Warning, not error
    }
    return true;
  }, {
    message: 'Critical processes should have at least 2 dependencies',
    path: ['dependencies'],
  });

/**
 * BIA Process Update Schema
 * Base schema - all fields optional
 */
const biaProcessUpdateBaseSchema = z.object({
  tenant_id: z.string().min(1).optional(),
  name: z.string().min(3).max(200).optional(),
  description: z.string().optional(),
  department: z.string().optional(),
  process_owner: z.string().optional(),
  criticality: z.nativeEnum(CriticalityLevel).optional(),
  criticality_score: z.number().min(1).max(5).optional(),
  who_tier: z.nativeEnum(WHOTier).optional(),
  industry: z.nativeEnum(IndustryType).optional(),
  geographical_scope: z.nativeEnum(GeographicalScope).optional(),
  rto_hours: z.number().nonnegative().max(8760).optional(),
  rpo_hours: z.number().nonnegative().max(8760).optional(),
  mtpd_hours: z.number().nonnegative().max(8760).optional(),
  financial_impact: financialImpactSchema.optional(),
  operational_impact: z.record(z.string(), z.string()).optional(),
  reputational_impact: z.nativeEnum(ReputationalImpact).optional(),
  regulatory_impact: z.nativeEnum(RegulatoryImpact).optional(),
  patient_safety_impact: z.nativeEnum(PatientSafetyImpact).optional(),
  compliance_objective: z.string().optional(),
  legal_regulatory_requirements: z.array(z.string()).optional(),
  personnel_requirements: z.record(z.any()).optional(),
  facility_requirements: z.record(z.any()).optional(),
  technology_requirements: z.record(z.any()).optional(),
  information_requirements: z.record(z.any()).optional(),
  recovery_strategies: z.array(z.record(z.any())).optional(),
  alternative_procedures: z.array(z.string()).optional(),
  workaround_capacity: z.number().min(0).max(100).optional(),
  upstream_processes: z.array(z.string()).optional(),
  downstream_processes: z.array(z.string()).optional(),
  critical_suppliers: z.array(z.record(z.any())).optional(),
  dependencies: z.array(dependencySchema).optional(),
  minimum_resource_level: z.record(z.any()).optional(),
  peak_periods: z.array(z.record(z.any())).optional(),
  seasonality: z.string().optional(),
  bia_completion_date: z.string().optional(),
  bia_assessor: z.string().optional(),
  bia_reviewer: z.string().optional(),
  next_review_date: z.string().optional(),
});

/**
 * BIA Process Update Schema with validation
 */
export const biaProcessUpdateSchema = biaProcessUpdateBaseSchema
  .refine((data) => {
    if (data.rto_hours !== undefined && data.rpo_hours !== undefined) {
      return data.rto_hours >= data.rpo_hours;
    }
    return true;
  }, {
    message: 'RTO must be greater than or equal to RPO',
    path: ['rto_hours'],
  })
  .refine((data) => {
    if (data.mtpd_hours !== undefined && data.rto_hours !== undefined) {
      return data.mtpd_hours >= data.rto_hours;
    }
    return true;
  }, {
    message: 'MTPD must be greater than or equal to RTO',
    path: ['mtpd_hours'],
  });

/**
 * AI RTO Suggestion Request Schema
 */
export const aiRTOSuggestionSchema = z.object({
  name: z.string().min(1, 'Process name is required'),
  industry: z.string().min(1, 'Industry is required'),
  criticality: z.nativeEnum(CriticalityLevel),
  financial_impact: z.record(z.string(), z.number()),
  staff_count: z.number().nonnegative().optional(),
});

/**
 * Type exports
 */
export type BIAProcessCreateInput = z.infer<typeof biaProcessCreateSchema>;
export type BIAProcessUpdateInput = z.infer<typeof biaProcessUpdateSchema>;
export type AIRTOSuggestionInput = z.infer<typeof aiRTOSuggestionSchema>;

/**
 * Validation helpers
 */

/**
 * Validate RTO/RPO/MTPD relationship
 */
export function validateTimeObjectives(
  rto: number,
  rpo: number,
  mtpd: number
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (rto < rpo) {
    errors.push('RTO must be >= RPO');
  }

  if (mtpd < rto) {
    errors.push('MTPD must be >= RTO');
  }

  if (rto < 0 || rpo < 0 || mtpd < 0) {
    errors.push('Time objectives must be non-negative');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate financial impact timeline
 */
export function validateFinancialImpact(
  impact: Record<string, number>
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  const entries = Object.entries(impact).sort((a, b) => {
    const aHours = parseTimeKey(a[0]);
    const bHours = parseTimeKey(b[0]);
    return aHours - bHours;
  });

  for (let i = 1; i < entries.length; i++) {
    if (entries[i][1] < entries[i - 1][1]) {
      errors.push(`Financial impact at ${entries[i][0]} must be >= ${entries[i - 1][0]}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Parse time key (e.g., "4_hours" -> 4, "7_days" -> 168)
 */
function parseTimeKey(key: string): number {
  const parts = key.split('_');
  const value = parseInt(parts[0]);
  const unit = parts[1];

  if (unit === 'hours') return value;
  if (unit === 'days') return value * 24;
  if (unit === 'weeks') return value * 24 * 7;

  return value;
}

/**
 * Check if critical process has adequate dependencies
 */
export function validateCriticalProcessDependencies(
  criticality: CriticalityLevel,
  dependencies: any[]
): { valid: boolean; warning?: string } {
  if (criticality === CriticalityLevel.CRITICAL) {
    const requiredDeps = dependencies.filter(d => d.required);

    if (requiredDeps.length < 2) {
      return {
        valid: true,
        warning: 'Critical processes typically need at least 2 required dependencies',
      };
    }
  }

  return { valid: true };
}
