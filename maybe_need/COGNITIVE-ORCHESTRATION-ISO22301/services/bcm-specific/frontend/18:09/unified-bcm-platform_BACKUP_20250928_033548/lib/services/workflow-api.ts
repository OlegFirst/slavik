/**
 * Workflow Management API Integration
 * Backend services: bpmn_service, bcm_core processes, bcm_foundation config
 */

import { apiClient } from '@/lib/api-client'
import {
  businessProcessSchema,
  bpmnDiagramSchema,
  automationRuleSchema,
  validateField,
  apiResponseSchema,
  paginatedResponseSchema,
  type BusinessProcessInput,
  type BPMNDiagramInput,
  type AutomationRuleInput,
  type ApiResponse,
  type PaginatedResponse
} from '@/lib/validations/workflow-schemas'
import {
  WorkflowApiError,
  safeApiCall,
  retryApiCall,
  monitoredApiCall,
  workflowApiRateLimiter,
  ApiTransaction,
  type ApiResult
} from '@/lib/utils/api-error-handler'
import { ZodError } from 'zod'

// Types
export interface WorkflowMetrics {
  totalWorkflows: number
  activeWorkflows: number
  completedToday: number
  averageCompletionTime: string
  automationRate: number
}

// 🆕 NEW: Analytics Types
export interface ProcessPerformanceMetrics {
  processId: string
  processName: string
  averageExecutionTime: number
  executionCount: number
  successRate: number
  bottleneckScore: number
  efficiency: number
  slaCompliance: number
  lastExecuted: string
}

export interface BottleneckAnalysis {
  processId: string
  bottleneckPoints: {
    stepName: string
    averageTime: number
    frequency: number
    impact: 'low' | 'medium' | 'high' | 'critical'
  }[]
  recommendations: string[]
  optimizationPotential: number
}

export interface TrendData {
  period: string
  executionCount: number
  averageTime: number
  successRate: number
  slaBreaches: number
}

export interface SLADefinition {
  id: string
  processId: string
  slaType: 'execution_time' | 'response_time' | 'resolution_time'
  targetTime: number
  warningThreshold: number
  escalationRules: {
    level: number
    triggerAfter: number
    action: string
    assignee: string
  }[]
}

export interface SLAStatus {
  processId: string
  currentStatus: 'compliant' | 'warning' | 'breach'
  timeRemaining: number
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  lastUpdated: string
}

export interface BusinessProcess {
  id: string
  name: string
  description: string
  category: 'bcp' | 'incident' | 'training' | 'audit' | 'governance'
  status: 'active' | 'draft' | 'archived' | 'under_review'
  owner: string
  department: string
  lastModified: string
  version: string
  stakeholders: string[]
  complexity: 'low' | 'medium' | 'high'
  criticality: 'low' | 'medium' | 'high' | 'critical'
  rto: string
  rpo: string
}

export interface BPMNDiagram {
  id: string
  name: string
  description?: string
  elements: BPMNElement[]
  connections: BPMNConnection[]
  category: string
  lastModified: string
  xml?: string // BPMN XML format
}

export interface BPMNElement {
  id: string
  type: 'start' | 'end' | 'task' | 'gateway' | 'event' | 'subprocess'
  label: string
  x: number
  y: number
  properties?: Record<string, any>
}

export interface BPMNConnection {
  id: string
  source: string
  target: string
  label?: string
}

export interface AutomationRule {
  id: string
  name: string
  description: string
  trigger: {
    type: 'incident' | 'schedule' | 'event' | 'condition'
    config: Record<string, any>
  }
  actions: AutomationAction[]
  status: 'active' | 'paused' | 'draft'
  category: 'notification' | 'escalation' | 'workflow' | 'reporting' | 'compliance'
  lastExecuted?: string
  executionCount: number
  successRate: number
  avgExecutionTime: string
}

export interface AutomationAction {
  id: string
  type: 'notification' | 'email' | 'webhook' | 'workflow_start' | 'data_update' | 'report_generate'
  config: Record<string, any>
  order: number
}

export interface ActiveWorkflow {
  id: string
  name: string
  type: 'bcp' | 'incident' | 'training' | 'audit'
  status: 'running' | 'paused' | 'waiting' | 'completed'
  progress: number
  assignedTo: string
  startTime: string
  estimatedCompletion: string
}

/**
 * Workflow Dashboard API
 */
export const workflowDashboardApi = {
  // Get workflow metrics and statistics
  async getMetrics(): Promise<WorkflowMetrics> {
    try {
      const response = await apiClient.get('/api/v1/bcm/core/workflow-metrics')
      return response.data
    } catch (error) {
      console.error('Failed to fetch workflow metrics:', error)
      throw error
    }
  },

  // Get active workflows
  async getActiveWorkflows(): Promise<ActiveWorkflow[]> {
    try {
      const response = await apiClient.get('/api/v1/bcm/core/workflows/active')
      return response.data
    } catch (error) {
      console.error('Failed to fetch active workflows:', error)
      throw error
    }
  },

  // Get workflow by ID
  async getWorkflow(id: string): Promise<ActiveWorkflow> {
    try {
      const response = await apiClient.get(`/api/v1/bcm/core/workflows/${id}`)
      return response.data
    } catch (error) {
      console.error(`Failed to fetch workflow ${id}:`, error)
      throw error
    }
  }
}

/**
 * Process Management API with validation and error handling
 */
export const processManagementApi = {
  // Get all business processes with proper error handling
  async getProcesses(filters?: {
    category?: string
    status?: string
    search?: string
    page?: number
    limit?: number
  }): Promise<ApiResult<PaginatedResponse<BusinessProcess>>> {
    return safeApiCall(
      async () => {
        // Input validation
        if (filters?.page && filters.page < 1) {
          throw new WorkflowApiError('Page number must be greater than 0', 'validation')
        }
        if (filters?.limit && (filters.limit < 1 || filters.limit > 100)) {
          throw new WorkflowApiError('Limit must be between 1 and 100', 'validation')
        }

        const params = new URLSearchParams()
        if (filters?.category) params.append('category', filters.category)
        if (filters?.status) params.append('status', filters.status)
        if (filters?.search) params.append('search', filters.search)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.limit) params.append('limit', filters.limit.toString())

        const response = await retryApiCall(
          () => apiClient.get(`/api/v1/bcm/core/processes?${params.toString()}`),
          { maxRetries: 2 }
        )

        // Validate response structure
        const validatedResponse = paginatedResponseSchema(businessProcessSchema).parse(response.data)
        return validatedResponse
      },
      {
        context: 'Get Business Processes'
      }
    )
  },

  // Create new process with full validation
  async createProcess(processInput: BusinessProcessInput): Promise<ApiResult<BusinessProcess>> {
    return safeApiCall(
      async () => {
        // Validate input data
        const validationResult = validateField(businessProcessSchema, processInput)
        if (!validationResult.success) {
          throw new ZodError(validationResult.errors.map(err => ({
            path: err.path.split('.'),
            message: err.message,
            code: 'custom' as any
          })))
        }

        // Check rate limiting
        if (!workflowApiRateLimiter.isAllowed('create_process')) {
          throw new WorkflowApiError(
            'Rate limit exceeded. Please wait before creating another process.',
            'business',
            429
          )
        }

        const response = await monitoredApiCall(
          () => apiClient.post('/api/v1/bcm/core/processes', validationResult.data),
          'Create Business Process'
        )

        // Validate response
        const validatedProcess = businessProcessSchema.parse(response.data)
        return validatedProcess
      },
      {
        context: 'Create Business Process'
      }
    )
  },

  // Update process
  async updateProcess(id: string, process: Partial<BusinessProcess>): Promise<BusinessProcess> {
    try {
      const response = await apiClient.put(`/api/v1/bcm/core/processes/${id}`, process)
      return response.data
    } catch (error) {
      console.error(`Failed to update process ${id}:`, error)
      throw error
    }
  },

  // Delete process
  async deleteProcess(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/bcm/core/processes/${id}`)
    } catch (error) {
      console.error(`Failed to delete process ${id}:`, error)
      throw error
    }
  },

  // Archive process
  async archiveProcess(id: string): Promise<ApiResult<BusinessProcess>> {
    return safeApiCall(
      async () => {
        if (!id || id.trim() === '') {
          throw new WorkflowApiError('Process ID is required', 'validation')
        }

        const response = await apiClient.patch(`/api/v1/bcm/core/processes/${id}/archive`)
        return businessProcessSchema.parse(response.data)
      },
      { context: 'Archive Business Process' }
    )
  },

  // 🔥 NEW: Transaction-safe process creation with BPMN
  async createProcessWithWorkflow(
    processInput: BusinessProcessInput,
    bpmnData?: BPMNDiagramInput,
    automationRules?: AutomationRuleInput[]
  ): Promise<ApiResult<{
    process: BusinessProcess
    bpmnDiagram?: BPMNDiagram
    automationRules?: AutomationRule[]
  }>> {
    return safeApiCall(
      async () => {
        const transaction = new ApiTransaction()
        let createdProcessId: string | null = null
        let createdBpmnId: string | null = null
        let createdRuleIds: string[] = []

        // Step 1: Create business process
        transaction.addOperation(
          async () => {
            const processResult = await processManagementApi.createProcess(processInput)
            if (!processResult.success) {
              throw new WorkflowApiError('Failed to create process', 'business')
            }
            createdProcessId = processResult.data.id
            return processResult.data
          },
          // Rollback: Delete created process
          async () => {
            if (createdProcessId) {
              await apiClient.delete(`/api/v1/bcm/core/processes/${createdProcessId}`)
            }
          }
        )

        // Step 2: Create BPMN diagram if provided
        if (bpmnData) {
          transaction.addOperation(
            async () => {
              const bpmnResult = await bpmnDesignerApi.createDiagram({
                ...bpmnData,
                category: processInput.category // Link to process category
              })
              if (!bpmnResult.success) {
                throw new WorkflowApiError('Failed to create BPMN diagram', 'business')
              }
              createdBpmnId = bpmnResult.data.id
              return bpmnResult.data
            },
            // Rollback: Delete created BPMN diagram
            async () => {
              if (createdBpmnId) {
                await apiClient.delete(`/api/v1/bpmn/diagrams/${createdBpmnId}`)
              }
            }
          )
        }

        // Step 3: Create automation rules if provided
        if (automationRules && automationRules.length > 0) {
          transaction.addOperation(
            async () => {
              const ruleResults = await Promise.all(
                automationRules.map(rule => automationApi.createRule(rule))
              )

              const failedRules = ruleResults.filter(result => !result.success)
              if (failedRules.length > 0) {
                throw new WorkflowApiError('Failed to create automation rules', 'business')
              }

              createdRuleIds = ruleResults.map(result => result.data.id)
              return ruleResults.map(result => result.data)
            },
            // Rollback: Delete created automation rules
            async () => {
              await Promise.all(
                createdRuleIds.map(ruleId =>
                  apiClient.delete(`/api/v1/bcm/foundation/automation/rules/${ruleId}`)
                )
              )
            }
          )
        }

        // Execute transaction
        const results = await transaction.execute()
        if (!results.success) {
          throw new WorkflowApiError('Transaction failed during process creation', 'business')
        }

        return {
          process: results.data[0],
          bpmnDiagram: results.data[1] || undefined,
          automationRules: results.data[2] || undefined
        }
      },
      { context: 'Create Process with Workflow' }
    )
  }
}

/**
 * BPMN Designer API
 */
export const bpmnDesignerApi = {
  // Get all BPMN diagrams
  async getDiagrams(): Promise<BPMNDiagram[]> {
    try {
      const response = await apiClient.get('/api/v1/bpmn/diagrams')
      return response.data
    } catch (error) {
      console.error('Failed to fetch BPMN diagrams:', error)
      throw error
    }
  },

  // Get diagram by ID
  async getDiagram(id: string): Promise<BPMNDiagram> {
    try {
      const response = await apiClient.get(`/api/v1/bpmn/diagrams/${id}`)
      return response.data
    } catch (error) {
      console.error(`Failed to fetch BPMN diagram ${id}:`, error)
      throw error
    }
  },

  // Create new diagram
  async createDiagram(diagram: Omit<BPMNDiagram, 'id' | 'lastModified'>): Promise<BPMNDiagram> {
    try {
      const response = await apiClient.post('/api/v1/bpmn/diagrams', diagram)
      return response.data
    } catch (error) {
      console.error('Failed to create BPMN diagram:', error)
      throw error
    }
  },

  // Update diagram
  async updateDiagram(id: string, diagram: Partial<BPMNDiagram>): Promise<BPMNDiagram> {
    try {
      const response = await apiClient.put(`/api/v1/bpmn/diagrams/${id}`, diagram)
      return response.data
    } catch (error) {
      console.error(`Failed to update BPMN diagram ${id}:`, error)
      throw error
    }
  },

  // Delete diagram
  async deleteDiagram(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/bpmn/diagrams/${id}`)
    } catch (error) {
      console.error(`Failed to delete BPMN diagram ${id}:`, error)
      throw error
    }
  },

  // Export diagram as XML
  async exportDiagram(id: string, format: 'xml' | 'svg' | 'png'): Promise<Blob> {
    try {
      const response = await apiClient.get(`/api/v1/bpmn/diagrams/${id}/export`, {
        params: { format },
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error(`Failed to export BPMN diagram ${id}:`, error)
      throw error
    }
  },

  // Import diagram from XML
  async importDiagram(file: File): Promise<BPMNDiagram> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post('/api/v1/bpmn/diagrams/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to import BPMN diagram:', error)
      throw error
    }
  },

  // Validate diagram
  async validateDiagram(id: string): Promise<{ valid: boolean; errors: string[] }> {
    try {
      const response = await apiClient.post(`/api/v1/bpmn/diagrams/${id}/validate`)
      return response.data
    } catch (error) {
      console.error(`Failed to validate BPMN diagram ${id}:`, error)
      throw error
    }
  },

  // Simulate workflow execution
  async simulateWorkflow(id: string): Promise<{ simulationId: string; status: string }> {
    try {
      const response = await apiClient.post(`/api/v1/bpmn/diagrams/${id}/simulate`)
      return response.data
    } catch (error) {
      console.error(`Failed to simulate BPMN workflow ${id}:`, error)
      throw error
    }
  }
}

/**
 * Automation Center API
 */
export const automationApi = {
  // Get all automation rules
  async getRules(): Promise<AutomationRule[]> {
    try {
      const response = await apiClient.get('/api/v1/bcm/foundation/automation/rules')
      return response.data
    } catch (error) {
      console.error('Failed to fetch automation rules:', error)
      throw error
    }
  },

  // Create automation rule
  async createRule(rule: Omit<AutomationRule, 'id' | 'executionCount' | 'lastExecuted'>): Promise<AutomationRule> {
    try {
      const response = await apiClient.post('/api/v1/bcm/foundation/automation/rules', rule)
      return response.data
    } catch (error) {
      console.error('Failed to create automation rule:', error)
      throw error
    }
  },

  // Update automation rule
  async updateRule(id: string, rule: Partial<AutomationRule>): Promise<AutomationRule> {
    try {
      const response = await apiClient.put(`/api/v1/bcm/foundation/automation/rules/${id}`, rule)
      return response.data
    } catch (error) {
      console.error(`Failed to update automation rule ${id}:`, error)
      throw error
    }
  },

  // Delete automation rule
  async deleteRule(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/bcm/foundation/automation/rules/${id}`)
    } catch (error) {
      console.error(`Failed to delete automation rule ${id}:`, error)
      throw error
    }
  },

  // Toggle rule status (active/paused)
  async toggleRule(id: string): Promise<AutomationRule> {
    try {
      const response = await apiClient.patch(`/api/v1/bcm/foundation/automation/rules/${id}/toggle`)
      return response.data
    } catch (error) {
      console.error(`Failed to toggle automation rule ${id}:`, error)
      throw error
    }
  },

  // Execute rule manually
  async executeRule(id: string): Promise<{ executionId: string; status: string }> {
    try {
      const response = await apiClient.post(`/api/v1/bcm/foundation/automation/rules/${id}/execute`)
      return response.data
    } catch (error) {
      console.error(`Failed to execute automation rule ${id}:`, error)
      throw error
    }
  },

  // Get rule execution history
  async getRuleHistory(id: string): Promise<any[]> {
    try {
      const response = await apiClient.get(`/api/v1/bcm/foundation/automation/rules/${id}/history`)
      return response.data
    } catch (error) {
      console.error(`Failed to fetch rule history ${id}:`, error)
      throw error
    }
  },

  // Get automation analytics
  async getAnalytics(): Promise<{
    totalExecutions: number
    avgSuccessRate: number
    timeSaved: number
    costSavings: number
  }> {
    try {
      const response = await apiClient.get('/api/v1/bcm/foundation/automation/analytics')
      return response.data
    } catch (error) {
      console.error('Failed to fetch automation analytics:', error)
      throw error
    }
  }
}

/**
 * Integration Status API
 */
export const integrationApi = {
  // Get service status
  async getServiceStatus(): Promise<{
    bpmn_service: 'connected' | 'disconnected' | 'error'
    bcm_core: 'connected' | 'disconnected' | 'error'
    bcm_foundation: 'connected' | 'disconnected' | 'error'
  }> {
    try {
      const response = await apiClient.get('/api/v1/status/services')
      return response.data
    } catch (error) {
      console.error('Failed to fetch service status:', error)
      throw error
    }
  },

  // Test BPMN service connection
  async testBPMNService(): Promise<{ status: 'ok' | 'error'; message?: string }> {
    try {
      const response = await apiClient.get('/api/v1/bpmn/health')
      return { status: 'ok', message: response.data.message }
    } catch (error) {
      console.error('BPMN service test failed:', error)
      return { status: 'error', message: 'BPMN service unavailable' }
    }
  }
}

/**
 * Workflow Templates API
 */
export const workflowTemplatesApi = {
  // Get process templates
  async getProcessTemplates(): Promise<any[]> {
    try {
      const response = await apiClient.get('/api/v1/bcm/core/templates/processes')
      return response.data
    } catch (error) {
      console.error('Failed to fetch process templates:', error)
      throw error
    }
  },

  // Get automation templates
  async getAutomationTemplates(): Promise<any[]> {
    try {
      const response = await apiClient.get('/api/v1/bcm/foundation/automation/templates')
      return response.data
    } catch (error) {
      console.error('Failed to fetch automation templates:', error)
      throw error
    }
  },

  // Create process from template
  async createFromTemplate(templateId: string, customization: any): Promise<BusinessProcess> {
    try {
      const response = await apiClient.post(`/api/v1/bcm/core/templates/processes/${templateId}/create`, customization)
      return response.data
    } catch (error) {
      console.error(`Failed to create process from template ${templateId}:`, error)
      throw error
    }
  }
}

/**
 * 🆕 NEW: Workflow Analytics API
 */
export const workflowAnalyticsApi = {
  // Get process performance metrics
  async getProcessPerformance(filters?: {
    processIds?: string[]
    department?: string
    category?: string
    dateRange?: { from: string; to: string }
  }): Promise<ApiResult<ProcessPerformanceMetrics[]>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.get('/api/v1/analytics/workflow/performance', {
          params: filters
        })
        return response.data
      },
      { context: 'Get Process Performance Metrics' }
    )
  },

  // Get bottleneck analysis
  async getBottleneckAnalysis(processId?: string): Promise<ApiResult<BottleneckAnalysis[]>> {
    return safeApiCall(
      async () => {
        const endpoint = processId
          ? `/api/v1/analytics/workflow/bottlenecks/${processId}`
          : '/api/v1/analytics/workflow/bottlenecks'
        const response = await apiClient.get(endpoint)
        return response.data
      },
      { context: 'Get Bottleneck Analysis' }
    )
  },

  // Get trend analysis
  async getTrendAnalysis(processId: string, period: '7d' | '30d' | '90d' | '1y'): Promise<ApiResult<TrendData[]>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.get(`/api/v1/analytics/workflow/trends/${processId}`, {
          params: { period }
        })
        return response.data
      },
      { context: 'Get Trend Analysis' }
    )
  },

  // Get aggregated analytics
  async getWorkflowAnalytics(filters?: {
    department?: string
    category?: string
    dateRange?: { from: string; to: string }
  }): Promise<ApiResult<{
    totalProcesses: number
    avgExecutionTime: number
    totalExecutions: number
    successRate: number
    topBottlenecks: BottleneckAnalysis[]
    performanceMetrics: ProcessPerformanceMetrics[]
  }>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.get('/api/v1/analytics/workflow/overview', {
          params: filters
        })
        return response.data
      },
      { context: 'Get Workflow Analytics Overview' }
    )
  },

  // Generate custom report
  async generateReport(config: {
    processIds: string[]
    metrics: string[]
    format: 'json' | 'csv' | 'pdf'
    dateRange: { from: string; to: string }
  }): Promise<ApiResult<any>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.post('/api/v1/analytics/workflow/reports', config)
        return response.data
      },
      { context: 'Generate Analytics Report' }
    )
  }
}

/**
 * 🆕 NEW: SLA Management API
 */
export const slaManagementApi = {
  // Get SLA definitions for process
  async getSLADefinitions(processId?: string): Promise<ApiResult<SLADefinition[]>> {
    return safeApiCall(
      async () => {
        const endpoint = processId
          ? `/api/v1/sla/definitions/process/${processId}`
          : '/api/v1/sla/definitions'
        const response = await apiClient.get(endpoint)
        return response.data
      },
      { context: 'Get SLA Definitions' }
    )
  },

  // Create SLA definition
  async createSLADefinition(sla: Omit<SLADefinition, 'id'>): Promise<ApiResult<SLADefinition>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.post('/api/v1/sla/definitions', sla)
        return response.data
      },
      { context: 'Create SLA Definition' }
    )
  },

  // Update SLA definition
  async updateSLADefinition(id: string, sla: Partial<SLADefinition>): Promise<ApiResult<SLADefinition>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.put(`/api/v1/sla/definitions/${id}`, sla)
        return response.data
      },
      { context: 'Update SLA Definition' }
    )
  },

  // Get current SLA status
  async getSLAStatus(processIds?: string[]): Promise<ApiResult<SLAStatus[]>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.get('/api/v1/sla/status', {
          params: processIds ? { processIds: processIds.join(',') } : {}
        })
        return response.data
      },
      { context: 'Get SLA Status' }
    )
  },

  // Get SLA breach alerts
  async getSLABreaches(filters?: {
    severity?: 'warning' | 'breach'
    department?: string
    dateRange?: { from: string; to: string }
  }): Promise<ApiResult<any[]>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.get('/api/v1/sla/breaches', {
          params: filters
        })
        return response.data
      },
      { context: 'Get SLA Breaches' }
    )
  },

  // Get SLA compliance report
  async getSLAComplianceReport(filters?: {
    processIds?: string[]
    department?: string
    period?: '7d' | '30d' | '90d'
  }): Promise<ApiResult<{
    overallCompliance: number
    processCompliance: { processId: string; compliance: number; breaches: number }[]
    trends: { date: string; compliance: number }[]
  }>> {
    return safeApiCall(
      async () => {
        const response = await apiClient.get('/api/v1/sla/compliance-report', {
          params: filters
        })
        return response.data
      },
      { context: 'Get SLA Compliance Report' }
    )
  }
}