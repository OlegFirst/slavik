/**
 * Risk Assessment Validation Schemas
 * Zod schemas for Risk Management validation
 * Enforces business rules and data integrity per ISO 22301:2019 Clause 8.2.3
 */

import { z } from 'zod';

/**
 * Risk Category Enum
 * 7 standard risk categories
 */
export enum RiskCategory {
  OPERATIONAL = 'operational',
  FINANCIAL = 'financial',
  STRATEGIC = 'strategic',
  COMPLIANCE = 'compliance',
  REPUTATIONAL = 'reputational',
  CYBERSECURITY = 'cybersecurity',
  NATURAL_DISASTER = 'natural_disaster',
}

/**
 * Risk Status Enum
 * Lifecycle stages of a risk
 */
export enum RiskStatus {
  IDENTIFIED = 'identified',
  ANALYZING = 'analyzing',
  TREATED = 'treated',
  MONITORING = 'monitoring',
  CLOSED = 'closed',
}

/**
 * Risk Severity Enum
 * Calculated based on risk score (likelihood × impact)
 */
export enum RiskSeverity {
  LOW = 'low',         // score 1-7
  MEDIUM = 'medium',   // score 8-14
  HIGH = 'high',       // score 15-19
  CRITICAL = 'critical', // score 20-25
}

/**
 * Treatment Strategy Enum
 * Standard risk treatment approaches
 */
export enum TreatmentStrategy {
  AVOID = 'avoid',       // Eliminate the risk
  MITIGATE = 'mitigate', // Reduce likelihood or impact
  TRANSFER = 'transfer', // Insurance or outsourcing
  ACCEPT = 'accept',     // Accept the risk
}

/**
 * Risk Create Schema
 * Validates all required fields for creating a new risk
 */
export const riskCreateSchema = z.object({
  organization_id: z.string().min(1, 'Organization ID is required'),

  // Identification
  risk_title: z.string()
    .min(1, 'Risk title is required')
    .max(255, 'Risk title must be less than 255 characters'),

  risk_code: z.string()
    .max(50, 'Risk code must be less than 50 characters')
    .optional(),

  risk_category: z.nativeEnum(RiskCategory, {
    errorMap: () => ({ message: 'Valid risk category is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters'),

  threat_source: z.string()
    .max(255, 'Threat source must be less than 255 characters')
    .optional(),

  vulnerabilities: z.array(z.string().min(1, 'Vulnerability cannot be empty'))
    .min(1, 'At least one vulnerability is required'),

  // Analysis (1-5 scale)
  likelihood: z.number()
    .int('Likelihood must be an integer')
    .min(1, 'Likelihood must be between 1 and 5')
    .max(5, 'Likelihood must be between 1 and 5'),

  impact: z.number()
    .int('Impact must be an integer')
    .min(1, 'Impact must be between 1 and 5')
    .max(5, 'Impact must be between 1 and 5'),

  // Ownership
  risk_owner_id: z.string()
    .uuid('Risk owner ID must be a valid UUID')
    .optional(),

  status: z.nativeEnum(RiskStatus, {
    errorMap: () => ({ message: 'Valid risk status is required' }),
  }),

  // Relations
  related_processes: z.array(z.any()).optional(),

  related_assets: z.array(z.any()).optional(),
});

/**
 * Risk Update Schema
 * All fields optional except organization_id
 */
const riskUpdateBaseSchema = z.object({
  organization_id: z.string().min(1, 'Organization ID is required'),

  risk_title: z.string()
    .min(1, 'Risk title is required')
    .max(255, 'Risk title must be less than 255 characters')
    .optional(),

  risk_code: z.string()
    .max(50, 'Risk code must be less than 50 characters')
    .optional(),

  risk_category: z.nativeEnum(RiskCategory).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .optional(),

  threat_source: z.string()
    .max(255, 'Threat source must be less than 255 characters')
    .optional(),

  vulnerabilities: z.array(z.string().min(1))
    .min(1, 'At least one vulnerability is required')
    .optional(),

  likelihood: z.number()
    .int('Likelihood must be an integer')
    .min(1, 'Likelihood must be between 1 and 5')
    .max(5, 'Likelihood must be between 1 and 5')
    .optional(),

  impact: z.number()
    .int('Impact must be an integer')
    .min(1, 'Impact must be between 1 and 5')
    .max(5, 'Impact must be between 1 and 5')
    .optional(),

  risk_owner_id: z.string()
    .uuid('Risk owner ID must be a valid UUID')
    .optional(),

  status: z.nativeEnum(RiskStatus).optional(),

  related_processes: z.array(z.any()).optional(),

  related_assets: z.array(z.any()).optional(),
});

export const riskUpdateSchema = riskUpdateBaseSchema.refine(
  (data) => {
    const keys = Object.keys(data).filter(k => k !== 'organization_id');
    return keys.length > 0;
  },
  {
    message: 'At least one field must be provided for update',
  }
);

/**
 * FAIR Analysis Create Schema
 * Factor Analysis of Information Risk
 */
export const fairAnalysisCreateSchema = z.object({
  threat_event_frequency: z.number()
    .nonnegative('Threat event frequency must be non-negative')
    .finite('Threat event frequency must be a finite number'),

  vulnerability_score: z.number()
    .min(0, 'Vulnerability score must be between 0 and 1')
    .max(1, 'Vulnerability score must be between 0 and 1'),

  // Primary loss (triangular distribution)
  primary_loss_min: z.number()
    .nonnegative('Primary loss minimum must be non-negative'),

  primary_loss_max: z.number()
    .nonnegative('Primary loss maximum must be non-negative'),

  primary_loss_most_likely: z.number()
    .nonnegative('Primary loss most likely must be non-negative'),

  // Secondary loss (optional, defaults to 0)
  secondary_loss_min: z.number()
    .nonnegative('Secondary loss minimum must be non-negative')
    .default(0),

  secondary_loss_max: z.number()
    .nonnegative('Secondary loss maximum must be non-negative')
    .default(0),

  secondary_loss_most_likely: z.number()
    .nonnegative('Secondary loss most likely must be non-negative')
    .optional(),
})
  // Business Rule: primary_loss_max >= primary_loss_min
  .refine((data) => data.primary_loss_max >= data.primary_loss_min, {
    message: 'Primary loss maximum must be greater than or equal to minimum',
    path: ['primary_loss_max'],
  })
  // Business Rule: primary_loss_most_likely between min and max
  .refine(
    (data) =>
      data.primary_loss_most_likely >= data.primary_loss_min &&
      data.primary_loss_most_likely <= data.primary_loss_max,
    {
      message: 'Primary loss most likely must be between minimum and maximum',
      path: ['primary_loss_most_likely'],
    }
  )
  // Business Rule: secondary_loss_max >= secondary_loss_min
  .refine((data) => data.secondary_loss_max >= data.secondary_loss_min, {
    message: 'Secondary loss maximum must be greater than or equal to minimum',
    path: ['secondary_loss_max'],
  });

/**
 * Monte Carlo Simulation Factor Schema
 */
export const monteCarloFactorSchema = z.object({
  name: z.string().optional(),
  min: z.number().finite('Minimum must be a finite number'),
  most_likely: z.number().finite('Most likely must be a finite number'),
  max: z.number().finite('Maximum must be a finite number'),
})
  .refine((data) => data.min <= data.most_likely, {
    message: 'Most likely value must be greater than or equal to minimum',
    path: ['most_likely'],
  })
  .refine((data) => data.most_likely <= data.max, {
    message: 'Most likely value must be less than or equal to maximum',
    path: ['most_likely'],
  });

/**
 * Monte Carlo Simulation Create Schema
 * Probabilistic risk analysis
 */
export const monteCarloSimulationCreateSchema = z.object({
  iterations: z.number()
    .int('Iterations must be an integer')
    .min(1000, 'Iterations must be at least 1,000')
    .max(100000, 'Iterations cannot exceed 100,000')
    .default(10000),

  factors: z.array(monteCarloFactorSchema)
    .min(1, 'At least one factor is required'),
});

/**
 * Treatment Plan Action Schema
 */
export const treatmentActionSchema = z.object({
  action: z.string()
    .min(1, 'Action description is required')
    .optional(),

  responsible: z.string()
    .optional(),

  deadline: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Deadline must be a valid date',
    })
    .optional(),

  status: z.string().optional(),
});

/**
 * Treatment Plan Create Schema
 * Risk mitigation/treatment planning
 */
export const treatmentPlanCreateSchema = z.object({
  strategy: z.nativeEnum(TreatmentStrategy, {
    errorMap: () => ({ message: 'Valid treatment strategy is required' }),
  }),

  description: z.string()
    .min(10, 'Description must be at least 10 characters'),

  actions: z.array(treatmentActionSchema)
    .min(1, 'At least one action is required'),

  responsible_party: z.string()
    .uuid('Responsible party must be a valid UUID')
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

  target_date: z.string()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      return !isNaN(date.getTime());
    }, {
      message: 'Target date must be a valid date',
    })
    .optional(),

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  expected_residual_likelihood: z.number()
    .int('Expected residual likelihood must be an integer')
    .min(1, 'Expected residual likelihood must be between 1 and 5')
    .max(5, 'Expected residual likelihood must be between 1 and 5')
    .optional(),

  expected_residual_impact: z.number()
    .int('Expected residual impact must be an integer')
    .min(1, 'Expected residual impact must be between 1 and 5')
    .max(5, 'Expected residual impact must be between 1 and 5')
    .optional(),
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
  );

/**
 * Treatment Plan Update Schema
 * All fields optional
 */
export const treatmentPlanUpdateSchema = z.object({
  strategy: z.nativeEnum(TreatmentStrategy).optional(),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .optional(),

  actions: z.array(treatmentActionSchema)
    .min(1, 'At least one action is required')
    .optional(),

  responsible_party: z.string()
    .uuid('Responsible party must be a valid UUID')
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

  estimated_cost: z.number()
    .nonnegative('Estimated cost must be non-negative')
    .optional(),

  actual_cost: z.number()
    .nonnegative('Actual cost must be non-negative')
    .optional(),

  expected_residual_likelihood: z.number()
    .int('Expected residual likelihood must be an integer')
    .min(1, 'Expected residual likelihood must be between 1 and 5')
    .max(5, 'Expected residual likelihood must be between 1 and 5')
    .optional(),

  expected_residual_impact: z.number()
    .int('Expected residual impact must be an integer')
    .min(1, 'Expected residual impact must be between 1 and 5')
    .max(5, 'Expected residual impact must be between 1 and 5')
    .optional(),

  status: z.string().optional(),
})
  // Business Rule: target_date must be after start_date (if both provided)
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
  );

/**
 * Risk Filters Schema
 * For list filtering and search
 */
export const riskFiltersSchema = z.object({
  category: z.array(z.nativeEnum(RiskCategory)).optional(),

  status: z.array(z.nativeEnum(RiskStatus)).optional(),

  severity: z.array(z.nativeEnum(RiskSeverity)).optional(),

  min_score: z.number()
    .int('Minimum score must be an integer')
    .min(1, 'Minimum score must be between 1 and 25')
    .max(25, 'Minimum score must be between 1 and 25')
    .optional(),

  max_score: z.number()
    .int('Maximum score must be an integer')
    .min(1, 'Maximum score must be between 1 and 25')
    .max(25, 'Maximum score must be between 1 and 25')
    .optional(),

  search: z.string()
    .min(2, 'Search query must be at least 2 characters for performance')
    .optional(),
})
  // Business Rule: max_score >= min_score
  .refine(
    (data) => {
      if (data.min_score === undefined || data.max_score === undefined) return true;
      return data.max_score >= data.min_score;
    },
    {
      message: 'Maximum score must be greater than or equal to minimum score',
      path: ['max_score'],
    }
  );

/**
 * Type exports for TypeScript inference
 */
export type RiskCreateInput = z.infer<typeof riskCreateSchema>;
export type RiskUpdateInput = z.infer<typeof riskUpdateSchema>;
export type FAIRAnalysisCreateInput = z.infer<typeof fairAnalysisCreateSchema>;
export type MonteCarloSimulationCreateInput = z.infer<typeof monteCarloSimulationCreateSchema>;
export type TreatmentPlanCreateInput = z.infer<typeof treatmentPlanCreateSchema>;
export type TreatmentPlanUpdateInput = z.infer<typeof treatmentPlanUpdateSchema>;
export type RiskFiltersInput = z.infer<typeof riskFiltersSchema>;

/**
 * Helper Functions
 */

/**
 * Calculate risk score (inherent or residual)
 * @param likelihood - Risk likelihood (1-5)
 * @param impact - Risk impact (1-5)
 * @returns Risk score (1-25)
 */
export function calculateRiskScore(likelihood: number, impact: number): number {
  return likelihood * impact;
}

/**
 * Calculate risk severity based on risk score
 * @param score - Risk score (1-25)
 * @returns Risk severity level
 */
export function calculateRiskSeverity(score: number): RiskSeverity {
  if (score >= 20) return RiskSeverity.CRITICAL;
  if (score >= 15) return RiskSeverity.HIGH;
  if (score >= 8) return RiskSeverity.MEDIUM;
  return RiskSeverity.LOW;
}

/**
 * Get severity color classes for UI
 * @param severity - Risk severity level
 * @returns Tailwind CSS classes
 */
export function getSeverityColors(severity: RiskSeverity): {
  bg: string;
  text: string;
  border: string;
  badge: string;
} {
  const SEVERITY_COLORS = {
    [RiskSeverity.CRITICAL]: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-300',
      badge: 'bg-red-600 text-white',
    },
    [RiskSeverity.HIGH]: {
      bg: 'bg-orange-100',
      text: 'text-orange-800',
      border: 'border-orange-300',
      badge: 'bg-orange-600 text-white',
    },
    [RiskSeverity.MEDIUM]: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      border: 'border-yellow-300',
      badge: 'bg-yellow-600 text-white',
    },
    [RiskSeverity.LOW]: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-300',
      badge: 'bg-green-600 text-white',
    },
  };

  return SEVERITY_COLORS[severity];
}

/**
 * Validate risk likelihood/impact values
 * @param likelihood - Likelihood value (1-5)
 * @param impact - Impact value (1-5)
 * @returns Validation result
 */
export function validateRiskAssessment(
  likelihood: number,
  impact: number
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (likelihood < 1 || likelihood > 5) {
    errors.push('Likelihood must be between 1 and 5');
  }

  if (impact < 1 || impact > 5) {
    errors.push('Impact must be between 1 and 5');
  }

  if (!Number.isInteger(likelihood)) {
    errors.push('Likelihood must be an integer');
  }

  if (!Number.isInteger(impact)) {
    errors.push('Impact must be an integer');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate FAIR analysis triangular distribution
 * @param min - Minimum value
 * @param mostLikely - Most likely value
 * @param max - Maximum value
 * @returns Validation result
 */
export function validateTriangularDistribution(
  min: number,
  mostLikely: number,
  max: number
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (min < 0 || mostLikely < 0 || max < 0) {
    errors.push('All values must be non-negative');
  }

  if (mostLikely < min) {
    errors.push('Most likely value must be greater than or equal to minimum');
  }

  if (mostLikely > max) {
    errors.push('Most likely value must be less than or equal to maximum');
  }

  if (max < min) {
    errors.push('Maximum value must be greater than or equal to minimum');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate treatment plan date range
 * @param startDate - Start date string
 * @param targetDate - Target date string
 * @returns Validation result
 */
export function validateTreatmentDates(
  startDate?: string,
  targetDate?: string
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!startDate || !targetDate) {
    return { valid: true, errors: [] };
  }

  const start = new Date(startDate);
  const target = new Date(targetDate);

  if (isNaN(start.getTime())) {
    errors.push('Invalid start date format');
  }

  if (isNaN(target.getTime())) {
    errors.push('Invalid target date format');
  }

  if (errors.length === 0 && target < start) {
    errors.push('Target date must be after or equal to start date');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Check if risk requires treatment plan
 * @param score - Risk score (1-25)
 * @param severity - Risk severity level
 * @returns Whether treatment is required
 */
export function requiresTreatmentPlan(score: number, severity: RiskSeverity): boolean {
  // Critical and High risks require treatment plans
  return severity === RiskSeverity.CRITICAL || severity === RiskSeverity.HIGH;
}

/**
 * Get recommended treatment strategy based on risk characteristics
 * @param score - Risk score (1-25)
 * @param category - Risk category
 * @returns Recommended treatment strategy
 */
export function getRecommendedStrategy(
  score: number,
  category: RiskCategory
): TreatmentStrategy {
  const severity = calculateRiskSeverity(score);

  // Critical risks: avoid or mitigate
  if (severity === RiskSeverity.CRITICAL) {
    if (category === RiskCategory.CYBERSECURITY || category === RiskCategory.COMPLIANCE) {
      return TreatmentStrategy.AVOID;
    }
    return TreatmentStrategy.MITIGATE;
  }

  // High risks: mitigate or transfer
  if (severity === RiskSeverity.HIGH) {
    if (category === RiskCategory.FINANCIAL) {
      return TreatmentStrategy.TRANSFER;
    }
    return TreatmentStrategy.MITIGATE;
  }

  // Medium/Low risks: accept or mitigate
  return score >= 8 ? TreatmentStrategy.MITIGATE : TreatmentStrategy.ACCEPT;
}
