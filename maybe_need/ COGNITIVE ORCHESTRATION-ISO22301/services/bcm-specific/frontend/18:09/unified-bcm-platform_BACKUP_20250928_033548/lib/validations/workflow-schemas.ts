/**
 * Validation schemas for Workflow Management
 * Используем Zod для type-safe validation
 */

import { z } from 'zod'

// ====== BUSINESS PROCESS VALIDATION ======
export const businessProcessSchema = z.object({
  name: z.string()
    .min(3, 'Process name must be at least 3 characters')
    .max(100, 'Process name must be less than 100 characters')
    .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Process name can only contain letters, numbers, spaces, hyphens and underscores'),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(1000, 'Description must be less than 1000 characters'),

  category: z.enum(['bcp', 'incident', 'training', 'audit', 'governance'], {
    errorMap: () => ({ message: 'Category must be one of: bcp, incident, training, audit, governance' })
  }),

  status: z.enum(['active', 'draft', 'archived', 'under_review'], {
    errorMap: () => ({ message: 'Status must be one of: active, draft, archived, under_review' })
  }),

  owner: z.string()
    .min(2, 'Owner name must be at least 2 characters')
    .max(50, 'Owner name must be less than 50 characters'),

  department: z.string()
    .min(2, 'Department must be at least 2 characters')
    .max(50, 'Department must be less than 50 characters'),

  stakeholders: z.array(z.string().min(1, 'Stakeholder name cannot be empty'))
    .min(1, 'At least one stakeholder is required')
    .max(20, 'Maximum 20 stakeholders allowed'),

  complexity: z.enum(['low', 'medium', 'high'], {
    errorMap: () => ({ message: 'Complexity must be low, medium, or high' })
  }),

  criticality: z.enum(['low', 'medium', 'high', 'critical'], {
    errorMap: () => ({ message: 'Criticality must be low, medium, high, or critical' })
  }),

  // RTO/RPO validation with business logic
  rto: z.string()
    .regex(/^\d+\s*(minutes?|hours?|days?)$/i, 'RTO must be in format "X minutes/hours/days"')
    .refine((val) => {
      const match = val.match(/^(\d+)\s*(minutes?|hours?|days?)$/i)
      if (!match) return false
      const [, num, unit] = match
      const value = parseInt(num)
      if (unit.toLowerCase().startsWith('minute')) return value >= 5 && value <= 1440 // 5 min to 24 hours
      if (unit.toLowerCase().startsWith('hour')) return value >= 1 && value <= 168 // 1 hour to 7 days
      if (unit.toLowerCase().startsWith('day')) return value >= 1 && value <= 30 // 1 to 30 days
      return false
    }, 'RTO must be between 5 minutes and 30 days'),

  rpo: z.string()
    .regex(/^\d+\s*(minutes?|hours?|days?)$/i, 'RPO must be in format "X minutes/hours/days"')
    .refine((val) => {
      const match = val.match(/^(\d+)\s*(minutes?|hours?|days?)$/i)
      if (!match) return false
      const [, num, unit] = match
      const value = parseInt(num)
      if (unit.toLowerCase().startsWith('minute')) return value >= 1 && value <= 1440
      if (unit.toLowerCase().startsWith('hour')) return value >= 1 && value <= 168
      if (unit.toLowerCase().startsWith('day')) return value >= 1 && value <= 30
      return false
    }, 'RPO must be between 1 minute and 30 days'),

  version: z.string()
    .regex(/^\d+\.\d+(\.\d+)?$/, 'Version must be in format X.Y or X.Y.Z')
    .optional()
}).refine((data) => {
  // Business rule: RTO должно быть больше или равно RPO
  const parseTime = (timeStr: string) => {
    const match = timeStr.match(/^(\d+)\s*(minutes?|hours?|days?)$/i)
    if (!match) return 0
    const [, num, unit] = match
    const value = parseInt(num)
    if (unit.toLowerCase().startsWith('minute')) return value
    if (unit.toLowerCase().startsWith('hour')) return value * 60
    if (unit.toLowerCase().startsWith('day')) return value * 60 * 24
    return 0
  }

  const rtoMinutes = parseTime(data.rto)
  const rpoMinutes = parseTime(data.rpo)

  return rtoMinutes >= rpoMinutes
}, {
  message: 'RTO (Recovery Time Objective) must be greater than or equal to RPO (Recovery Point Objective)',
  path: ['rto']
})

export type BusinessProcessInput = z.infer<typeof businessProcessSchema>

// ====== BPMN DIAGRAM VALIDATION ======
export const bpmnElementSchema = z.object({
  id: z.string().min(1, 'Element ID is required'),
  type: z.enum(['start', 'end', 'task', 'gateway', 'event', 'subprocess']),
  label: z.string()
    .min(1, 'Element label is required')
    .max(50, 'Element label must be less than 50 characters'),
  x: z.number().min(0, 'X coordinate must be positive').max(2000, 'X coordinate too large'),
  y: z.number().min(0, 'Y coordinate must be positive').max(1000, 'Y coordinate too large'),
  properties: z.record(z.any()).optional()
})

export const bpmnConnectionSchema = z.object({
  id: z.string().min(1, 'Connection ID is required'),
  source: z.string().min(1, 'Source element ID is required'),
  target: z.string().min(1, 'Target element ID is required'),
  label: z.string().max(30, 'Connection label must be less than 30 characters').optional()
})

export const bpmnDiagramSchema = z.object({
  name: z.string()
    .min(3, 'Diagram name must be at least 3 characters')
    .max(100, 'Diagram name must be less than 100 characters'),

  description: z.string()
    .max(500, 'Description must be less than 500 characters')
    .optional(),

  category: z.string()
    .min(2, 'Category must be at least 2 characters')
    .max(30, 'Category must be less than 30 characters'),

  elements: z.array(bpmnElementSchema)
    .min(2, 'Diagram must have at least 2 elements (start and end)')
    .max(50, 'Diagram cannot have more than 50 elements'),

  connections: z.array(bpmnConnectionSchema)
    .max(100, 'Diagram cannot have more than 100 connections'),

  xml: z.string().optional()
}).refine((data) => {
  // Business rule: Должен быть хотя бы один start и один end элемент
  const hasStart = data.elements.some(el => el.type === 'start')
  const hasEnd = data.elements.some(el => el.type === 'end')
  return hasStart && hasEnd
}, {
  message: 'Diagram must have at least one start element and one end element',
  path: ['elements']
}).refine((data) => {
  // Business rule: Все connections должны ссылаться на существующие элементы
  const elementIds = new Set(data.elements.map(el => el.id))
  const invalidConnections = data.connections.filter(conn =>
    !elementIds.has(conn.source) || !elementIds.has(conn.target)
  )
  return invalidConnections.length === 0
}, {
  message: 'All connections must reference existing elements',
  path: ['connections']
})

export type BPMNDiagramInput = z.infer<typeof bpmnDiagramSchema>

// ====== AUTOMATION RULE VALIDATION ======
export const automationActionSchema = z.object({
  type: z.enum(['notification', 'email', 'webhook', 'workflow_start', 'data_update', 'report_generate']),
  config: z.record(z.any())
    .refine((config) => Object.keys(config).length > 0, 'Action configuration cannot be empty'),
  order: z.number().min(1, 'Action order must be at least 1').max(20, 'Maximum 20 actions allowed')
})

export const automationTriggerSchema = z.object({
  type: z.enum(['incident', 'schedule', 'event', 'condition']),
  config: z.record(z.any())
    .refine((config) => Object.keys(config).length > 0, 'Trigger configuration cannot be empty')
})

export const automationRuleSchema = z.object({
  name: z.string()
    .min(5, 'Rule name must be at least 5 characters')
    .max(100, 'Rule name must be less than 100 characters'),

  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(500, 'Description must be less than 500 characters'),

  trigger: automationTriggerSchema,

  actions: z.array(automationActionSchema)
    .min(1, 'At least one action is required')
    .max(10, 'Maximum 10 actions allowed'),

  category: z.enum(['notification', 'escalation', 'workflow', 'reporting', 'compliance']),

  status: z.enum(['active', 'paused', 'draft'])
}).refine((data) => {
  // Business rule: Actions должны иметь уникальные order
  const orders = data.actions.map(action => action.order)
  const uniqueOrders = new Set(orders)
  return orders.length === uniqueOrders.size
}, {
  message: 'Action orders must be unique',
  path: ['actions']
})

export type AutomationRuleInput = z.infer<typeof automationRuleSchema>

// ====== FORM VALIDATION HELPERS ======
export const validateField = <T>(schema: z.ZodSchema<T>, value: unknown) => {
  try {
    schema.parse(value)
    return { success: true as const, data: value as T }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false as const,
        errors: error.errors.map(err => ({
          path: err.path.join('.'),
          message: err.message
        }))
      }
    }
    return {
      success: false as const,
      errors: [{ path: 'unknown', message: 'Validation failed' }]
    }
  }
}

export const validatePartial = <T>(schema: z.ZodSchema<T>, value: unknown) => {
  return validateField(schema.partial(), value)
}

// ====== DATABASE CONSTRAINT HELPERS ======
export const dbConstraints = {
  businessProcess: {
    uniqueFields: ['name'], // На уровне БД должен быть UNIQUE INDEX
    requiredFields: ['name', 'category', 'owner', 'department', 'rto', 'rpo'],
    maxLengths: {
      name: 100,
      description: 1000,
      owner: 50,
      department: 50
    }
  },

  bpmnDiagram: {
    uniqueFields: ['name'],
    requiredFields: ['name', 'category'],
    maxLengths: {
      name: 100,
      description: 500,
      category: 30
    }
  },

  automationRule: {
    uniqueFields: ['name'],
    requiredFields: ['name', 'description', 'trigger', 'actions'],
    maxLengths: {
      name: 100,
      description: 500
    }
  }
} as const

// ====== API RESPONSE VALIDATION ======
export const apiResponseSchema = z.object({
  success: z.boolean(),
  data: z.any().optional(),
  error: z.string().optional(),
  message: z.string().optional(),
  timestamp: z.string().datetime().optional()
})

export const paginatedResponseSchema = <T>(dataSchema: z.ZodSchema<T>) => z.object({
  success: z.boolean(),
  data: z.array(dataSchema),
  pagination: z.object({
    page: z.number().min(1),
    limit: z.number().min(1).max(100),
    total: z.number().min(0),
    totalPages: z.number().min(0)
  }),
  error: z.string().optional()
})

export type ApiResponse<T> = {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp?: string
}

export type PaginatedResponse<T> = {
  success: boolean
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
  error?: string
}