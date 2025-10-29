import { z } from 'zod';

// ===========================
// AUTH SCHEMAS
// ===========================

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters')
});

export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  role: z.enum(['admin', 'manager', 'analyst', 'viewer']).optional()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// ===========================
// USER SCHEMAS
// ===========================

export const userSchema = z.object({
  id: z.string().uuid().optional(),
  email: z.string().email('Invalid email address'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  role: z.enum(['admin', 'manager', 'analyst', 'viewer']),
  department: z.string().optional(),
  phone: z.string().optional(),
  active: z.boolean().default(true)
});

export const updateUserSchema = userSchema.partial();

// ===========================
// CLIENT SCHEMAS
// ===========================

export const clientSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string().min(2, 'Company name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  address: z.string().optional(),
  industry: z.string(),
  status: z.enum(['prospect', 'active', 'inactive', 'churned']),
  riskLevel: z.enum(['low', 'medium', 'high', 'critical']),
  contractStartDate: z.string().datetime().optional(),
  contractEndDate: z.string().datetime().optional(),
  notes: z.string().max(1000, 'Notes must be less than 1000 characters').optional()
});

// ===========================
// TEMPLATE SCHEMAS
// ===========================

export const templateSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string().min(3, 'Template name must be at least 3 characters'),
  category: z.enum(['Policy', 'Procedure', 'Plan', 'Assessment', 'Report', 'Form']),
  version: z.string().regex(/^\d+\.\d+(\.\d+)?$/, 'Version must be in format X.Y or X.Y.Z'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  tags: z.array(z.string()).optional(),
  active: z.boolean().default(true)
});

// ===========================
// CONFIG SCHEMAS
// ===========================

export const configSchema = z.object({
  general: z.object({
    companyName: z.string().min(2, 'Company name is required'),
    timezone: z.string(),
    language: z.enum(['en', 'es', 'fr', 'de', 'zh', 'ja']),
    dateFormat: z.enum(['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'])
  }),
  security: z.object({
    passwordPolicy: z.enum(['weak', 'medium', 'strong']),
    mfaEnabled: z.boolean(),
    sessionTimeout: z.number().min(300).max(86400), // 5 min to 24 hours in seconds
    maxLoginAttempts: z.number().min(3).max(10),
    passwordExpiry: z.number().min(0).max(365) // days
  }),
  notifications: z.object({
    emailEnabled: z.boolean(),
    smsEnabled: z.boolean(),
    pushEnabled: z.boolean(),
    criticalAlerts: z.boolean(),
    dailyDigest: z.boolean()
  }),
  integration: z.object({
    odooEnabled: z.boolean(),
    aiServicesEnabled: z.boolean(),
    webhookEnabled: z.boolean(),
    apiRateLimit: z.number().min(10).max(10000)
  })
});

// ===========================
// SERVICE CONTROL SCHEMAS
// ===========================

export const serviceActionSchema = z.object({
  serviceName: z.string(),
  action: z.enum(['start', 'stop', 'restart', 'status']),
  force: z.boolean().optional()
});

// ===========================
// AI ORGANISM SCHEMAS
// ===========================

export const aiOrganismConfigSchema = z.object({
  id: z.string(),
  name: z.string(),
  model: z.string(),
  temperature: z.number().min(0).max(2),
  maxTokens: z.number().min(100).max(8000),
  topP: z.number().min(0).max(1),
  frequencyPenalty: z.number().min(-2).max(2),
  presencePenalty: z.number().min(-2).max(2),
  stopSequences: z.array(z.string()).optional(),
  systemPrompt: z.string().optional()
});

// ===========================
// METRIC SCHEMAS
// ===========================

export const metricSchema = z.object({
  timestamp: z.string().datetime(),
  cpu: z.number().min(0).max(100),
  memory: z.number().min(0).max(100),
  disk: z.number().min(0).max(100),
  network: z.number().min(0),
  activeUsers: z.number().min(0),
  requestsPerSecond: z.number().min(0)
});

// ===========================
// NOTIFICATION SCHEMAS
// ===========================

export const notificationSchema = z.object({
  id: z.string().uuid().optional(),
  type: z.enum(['info', 'warning', 'error', 'success']),
  title: z.string(),
  message: z.string(),
  timestamp: z.string().datetime(),
  read: z.boolean().default(false),
  actionUrl: z.string().url().optional()
});

// ===========================
// API REQUEST SCHEMAS
// ===========================

export const paginationSchema = z.object({
  page: z.number().min(1).default(1),
  limit: z.number().min(1).max(100).default(20),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('asc')
});

export const filterSchema = z.object({
  search: z.string().optional(),
  status: z.array(z.string()).optional(),
  dateFrom: z.string().datetime().optional(),
  dateTo: z.string().datetime().optional(),
  tags: z.array(z.string()).optional()
});

// ===========================
// HELPER FUNCTIONS
// ===========================

// Validate and parse data
export function validateData<T>(schema: z.ZodSchema<T>, data: unknown): T {
  return schema.parse(data);
}

// Safe parse with error handling
export function safeValidate<T>(schema: z.ZodSchema<T>, data: unknown): {
  success: boolean;
  data?: T;
  errors?: z.ZodError;
} {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, errors: result.error };
}

// Format validation errors for display
export function formatValidationErrors(errors: z.ZodError): Record<string, string> {
  const formatted: Record<string, string> = {};
  errors.issues.forEach((issue) => {
    const path = issue.path.join('.');
    formatted[path] = issue.message;
  });
  return formatted;
}

// Type exports
export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type UserInput = z.infer<typeof userSchema>;
export type ClientInput = z.infer<typeof clientSchema>;
export type TemplateInput = z.infer<typeof templateSchema>;
export type ConfigInput = z.infer<typeof configSchema>;
export type ServiceActionInput = z.infer<typeof serviceActionSchema>;
export type AIOrganismConfigInput = z.infer<typeof aiOrganismConfigSchema>;
export type MetricInput = z.infer<typeof metricSchema>;
export type NotificationInput = z.infer<typeof notificationSchema>;
export type PaginationInput = z.infer<typeof paginationSchema>;
export type FilterInput = z.infer<typeof filterSchema>;