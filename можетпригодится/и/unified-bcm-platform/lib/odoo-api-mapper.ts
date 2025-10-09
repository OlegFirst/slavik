// Odoo API Endpoint Mapping System

export interface OdooEndpoint {
  module: string
  model: string
  endpoint: string
  methods: ('GET' | 'POST' | 'PUT' | 'DELETE')[]
  mockImplemented: boolean
  realImplemented: boolean
  authentication: 'jwt' | 'session' | 'api-key'
  rateLimit?: number
  description: string
}

export interface APIFieldMapping {
  odooField: string
  frontendField: string
  type: 'string' | 'number' | 'boolean' | 'date' | 'array' | 'object'
  required: boolean
  transformation?: string
}

export interface ModelMapping {
  odooModel: string
  frontendInterface: string
  fields: APIFieldMapping[]
}

// Complete API endpoint registry
export const ODOO_ENDPOINTS: OdooEndpoint[] = [
  // Risk Management endpoints
  {
    module: 'bcm_risk_management',
    model: 'bcm.risk',
    endpoint: '/api/v1/bcm/risks',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'jwt',
    rateLimit: 100,
    description: 'Risk management CRUD operations'
  },
  {
    module: 'bcm_risk_management',
    model: 'bcm.risk.assessment',
    endpoint: '/api/v1/bcm/risk-assessments',
    methods: ['GET', 'POST'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Risk assessment operations'
  },
  {
    module: 'bcm_risk_management',
    model: 'bcm.risk.matrix',
    endpoint: '/api/v1/bcm/risk-matrix',
    methods: ['GET'],
    mockImplemented: false,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Risk matrix visualization data'
  },

  // BIA endpoints
  {
    module: 'bcm_bia',
    model: 'bcm.bia.result',
    endpoint: '/api/v1/bcm/bia/results',
    methods: ['GET', 'POST', 'PUT'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'jwt',
    description: 'BIA results management'
  },
  {
    module: 'bcm_bia',
    model: 'bcm.critical.function',
    endpoint: '/api/v1/bcm/critical-functions',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Critical business functions'
  },
  {
    module: 'bcm_bia',
    model: 'bcm.rto.rpo',
    endpoint: '/api/v1/bcm/rto-rpo',
    methods: ['GET', 'POST'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'jwt',
    description: 'RTO/RPO calculations'
  },

  // AI Control endpoints
  {
    module: 'bcm_ai_control',
    model: 'ai.organ',
    endpoint: '/api/v1/ai/organs',
    methods: ['GET'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'api-key',
    rateLimit: 1000,
    description: 'AI organ status monitoring'
  },
  {
    module: 'bcm_ai_control',
    model: 'ai.organ.control',
    endpoint: '/api/v1/ai/organs/{id}/control',
    methods: ['POST'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'api-key',
    description: 'AI organ control operations'
  },
  {
    module: 'bcm_ai_control',
    model: 'ai.decision.log',
    endpoint: '/api/v1/ai/decisions',
    methods: ['GET'],
    mockImplemented: true,
    realImplemented: false,
    authentication: 'api-key',
    description: 'AI decision history'
  },

  // BCM Core endpoints
  {
    module: 'bcm_core',
    model: 'bcm.organization',
    endpoint: '/api/v1/bcm/organizations',
    methods: ['GET', 'POST', 'PUT'],
    mockImplemented: false,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Organization management'
  },
  {
    module: 'bcm_core',
    model: 'bcm.business.unit',
    endpoint: '/api/v1/bcm/business-units',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    mockImplemented: false,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Business units hierarchy'
  },
  {
    module: 'bcm_core',
    model: 'bcm.stakeholder',
    endpoint: '/api/v1/bcm/stakeholders',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    mockImplemented: false,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Stakeholder management'
  },

  // Incident Management endpoints
  {
    module: 'bcm_incident_management',
    model: 'bcm.incident',
    endpoint: '/api/v1/bcm/incidents',
    methods: ['GET', 'POST', 'PUT'],
    mockImplemented: false,
    realImplemented: false,
    authentication: 'jwt',
    rateLimit: 200,
    description: 'Incident management'
  },
  {
    module: 'bcm_incident_management',
    model: 'bcm.incident.response',
    endpoint: '/api/v1/bcm/incident-responses',
    methods: ['GET', 'POST'],
    mockImplemented: false,
    realImplemented: false,
    authentication: 'jwt',
    description: 'Incident response actions'
  }
]

// Model field mappings
export const MODEL_MAPPINGS: ModelMapping[] = [
  {
    odooModel: 'bcm.risk',
    frontendInterface: 'Risk',
    fields: [
      { odooField: 'id', frontendField: 'id', type: 'string', required: true },
      { odooField: 'name', frontendField: 'title', type: 'string', required: true },
      { odooField: 'description', frontendField: 'description', type: 'string', required: true },
      { odooField: 'risk_category_id', frontendField: 'category', type: 'string', required: true },
      { odooField: 'probability', frontendField: 'probability', type: 'number', required: true },
      { odooField: 'impact', frontendField: 'impact', type: 'number', required: true },
      { odooField: 'risk_score', frontendField: 'score', type: 'number', required: false, transformation: 'probability * impact' },
      { odooField: 'risk_owner_id', frontendField: 'owner', type: 'string', required: false },
      { odooField: 'treatment_plan', frontendField: 'treatment', type: 'string', required: false },
      { odooField: 'state', frontendField: 'status', type: 'string', required: true },
      { odooField: 'create_date', frontendField: 'createdAt', type: 'date', required: true },
      { odooField: 'write_date', frontendField: 'updatedAt', type: 'date', required: false }
    ]
  },
  {
    odooModel: 'bcm.bia.result',
    frontendInterface: 'BIAResult',
    fields: [
      { odooField: 'id', frontendField: 'id', type: 'string', required: true },
      { odooField: 'business_function_id', frontendField: 'functionId', type: 'string', required: true },
      { odooField: 'function_name', frontendField: 'functionName', type: 'string', required: true },
      { odooField: 'criticality_level', frontendField: 'criticality', type: 'string', required: true },
      { odooField: 'rto_hours', frontendField: 'rto', type: 'number', required: true },
      { odooField: 'rpo_hours', frontendField: 'rpo', type: 'number', required: true },
      { odooField: 'financial_impact', frontendField: 'financialImpact', type: 'number', required: false },
      { odooField: 'dependencies', frontendField: 'dependencies', type: 'array', required: false },
      { odooField: 'assessment_date', frontendField: 'assessmentDate', type: 'date', required: true }
    ]
  },
  {
    odooModel: 'ai.organ',
    frontendInterface: 'AIOrgan',
    fields: [
      { odooField: 'id', frontendField: 'id', type: 'string', required: true },
      { odooField: 'name', frontendField: 'name', type: 'string', required: true },
      { odooField: 'organ_type', frontendField: 'category', type: 'string', required: true },
      { odooField: 'status', frontendField: 'status', type: 'string', required: true },
      { odooField: 'health_score', frontendField: 'health', type: 'number', required: true },
      { odooField: 'last_activity_time', frontendField: 'lastActivity', type: 'date', required: false },
      { odooField: 'response_time_ms', frontendField: 'responseTime', type: 'number', required: false },
      { odooField: 'tokens_used_today', frontendField: 'tokensUsed', type: 'number', required: false },
      { odooField: 'capabilities', frontendField: 'capabilities', type: 'array', required: false }
    ]
  }
]

// API implementation status tracker
export function getAPIImplementationStatus(): {
  total: number
  mockImplemented: number
  realImplemented: number
  percentMock: number
  percentReal: number
} {
  const total = ODOO_ENDPOINTS.length
  const mockImplemented = ODOO_ENDPOINTS.filter(e => e.mockImplemented).length
  const realImplemented = ODOO_ENDPOINTS.filter(e => e.realImplemented).length

  return {
    total,
    mockImplemented,
    realImplemented,
    percentMock: Math.round((mockImplemented / total) * 100),
    percentReal: Math.round((realImplemented / total) * 100)
  }
}

// Get endpoints by module
export function getEndpointsByModule(moduleId: string): OdooEndpoint[] {
  return ODOO_ENDPOINTS.filter(e => e.module === moduleId)
}

// Get missing real implementations
export function getMissingRealImplementations(): OdooEndpoint[] {
  return ODOO_ENDPOINTS.filter(e => e.mockImplemented && !e.realImplemented)
}

// Data transformation utilities
export function transformOdooToFrontend<T>(
  odooData: any,
  modelName: string
): T | null {
  const mapping = MODEL_MAPPINGS.find(m => m.odooModel === modelName)
  if (!mapping) return null

  const transformed: any = {}

  mapping.fields.forEach(field => {
    const value = odooData[field.odooField]

    if (value !== undefined) {
      // Apply transformation if specified
      if (field.transformation) {
        // Execute simple transformations (expand as needed)
        transformed[field.frontendField] = eval(field.transformation)
      } else {
        transformed[field.frontendField] = value
      }
    } else if (field.required) {
      console.warn(`Missing required field: ${field.odooField}`)
    }
  })

  return transformed as T
}

export function transformFrontendToOdoo(
  frontendData: any,
  modelName: string
): any {
  const mapping = MODEL_MAPPINGS.find(m => m.frontendInterface === modelName)
  if (!mapping) return null

  const transformed: any = {}

  mapping.fields.forEach(field => {
    const value = frontendData[field.frontendField]

    if (value !== undefined) {
      transformed[field.odooField] = value
    }
  })

  return transformed
}

// Generate API documentation
export function generateAPIDocumentation(): string {
  const doc: string[] = ['# BCM Platform API Documentation', '']
  doc.push(`Generated: ${new Date().toISOString()}`, '')

  doc.push('## API Implementation Status', '')
  const status = getAPIImplementationStatus()
  doc.push(`Total Endpoints: ${status.total}`)
  doc.push(`Mock Implemented: ${status.mockImplemented} (${status.percentMock}%)`)
  doc.push(`Real Implemented: ${status.realImplemented} (${status.percentReal}%)`)
  doc.push('')

  doc.push('## Endpoints by Module', '')

  const moduleGroups = ODOO_ENDPOINTS.reduce((acc, endpoint) => {
    if (!acc[endpoint.module]) acc[endpoint.module] = []
    acc[endpoint.module].push(endpoint)
    return acc
  }, {} as Record<string, OdooEndpoint[]>)

  Object.entries(moduleGroups).forEach(([module, endpoints]) => {
    doc.push(`### ${module}`, '')

    endpoints.forEach(endpoint => {
      const mockStatus = endpoint.mockImplemented ? '[MOCK]' : '[TODO]'
      const realStatus = endpoint.realImplemented ? '[REAL]' : '[TODO]'

      doc.push(`#### ${endpoint.endpoint}`)
      doc.push(`- Model: ${endpoint.model}`)
      doc.push(`- Methods: ${endpoint.methods.join(', ')}`)
      doc.push(`- Authentication: ${endpoint.authentication}`)
      doc.push(`- Status: Mock ${mockStatus} | Real ${realStatus}`)
      doc.push(`- Description: ${endpoint.description}`)
      doc.push('')
    })
  })

  doc.push('## Model Mappings', '')

  MODEL_MAPPINGS.forEach(mapping => {
    doc.push(`### ${mapping.odooModel} → ${mapping.frontendInterface}`, '')
    doc.push('| Odoo Field | Frontend Field | Type | Required |')
    doc.push('|------------|---------------|------|----------|')

    mapping.fields.forEach(field => {
      doc.push(`| ${field.odooField} | ${field.frontendField} | ${field.type} | ${field.required ? 'Yes' : 'No'} |`)
    })
    doc.push('')
  })

  return doc.join('\n')
}