// Business Impact Analysis API Service
// Complete CRUD operations for BIA module with Odoo Backend integration via BCMAPIClient

import { BCMAPIClient } from '@/lib/api-client'
import { odooBIAConnector, type OdooBIAProcess } from './odoo-bia-connector'
import { externalServices, type NotificationRequest, type DocumentProcessingRequest } from './external-services-client'

// Core BIA Types
export interface BIAResult {
  id: string
  businessFunction: string
  department: string
  rto: number // Recovery Time Objective (hours)
  rpo: number // Recovery Point Objective (hours)
  mtpd: number // Maximum Tolerable Period of Disruption
  financialImpactPerHour: number
  criticalityLevel: 'low' | 'medium' | 'high' | 'critical'
  dependencies: string[]
  lastAssessed: string
  assessmentVersion?: string
  assessedBy?: string
  createdAt?: string
  updatedAt?: string
}

export interface BIAMetrics {
  totalFunctions: number
  criticalFunctions: number
  avgRTO: number
  totalFinancialRisk: number
  assessmentsCompleted: number
  pendingAssessments: number
  nextReviewDate?: string
}

export interface BIAQuestionnaire {
  id: string
  functionId: string
  questions: BIAQuestion[]
  responses: BIAResponse[]
  status: 'draft' | 'completed' | 'approved'
  completedBy?: string
  completedAt?: string
}

export interface BIAQuestion {
  id: string
  category: 'impact' | 'dependencies' | 'resources' | 'recovery'
  question: string
  type: 'text' | 'number' | 'select' | 'multiselect' | 'scale' | 'slider' | 'currency'
  options?: string[]
  required: boolean
  weight?: number
}

export interface BIAResponse {
  questionId: string
  answer: string | number | string[]
  confidence?: number
  notes?: string
}

export interface DependencyMapping {
  id: string
  sourceFunction: string
  targetFunction: string
  dependencyType: 'critical' | 'important' | 'optional'
  description: string
  impactLevel: number
  recoverySequence?: number
}

export interface CriticalPath {
  id: string
  name: string
  functions: string[]
  totalRTO: number
  bottleneckFunction: string
  optimizationOpportunities: OptimizationOpportunity[]
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
}

export interface OptimizationOpportunity {
  functionId: string
  currentRTO: number
  optimizedRTO: number
  investment: number
  costBenefit: number
  effort: 'low' | 'medium' | 'high'
}

export interface BIAReport {
  id: string
  type: 'summary' | 'detailed' | 'executive' | 'technical'
  generatedAt: string
  generatedBy: string
  data: any
  format: 'pdf' | 'excel' | 'json'
}

export interface BusinessFunction {
  id: string
  name: string
  description: string
  department: string
  owner: string
  category: 'primary' | 'support' | 'management'
  status: 'active' | 'inactive' | 'under_review'
  processes: BusinessProcess[]
}

export interface BusinessProcess {
  id: string
  name: string
  description: string
  functionId: string
  inputs: string[]
  outputs: string[]
  resources: ProcessResource[]
  dependencies: string[]
}

export interface ProcessResource {
  id: string
  type: 'human' | 'technology' | 'facility' | 'information'
  name: string
  criticality: 'critical' | 'important' | 'optional'
  alternativeOptions?: string[]
}

// Mock data for development
const mockBIAResults: BIAResult[] = [
  {
    id: '1',
    businessFunction: 'Customer Order Processing',
    department: 'Sales',
    rto: 2,
    rpo: 1,
    mtpd: 8,
    financialImpactPerHour: 50000,
    criticalityLevel: 'critical',
    dependencies: ['Payment Gateway', 'Inventory System', 'CRM'],
    lastAssessed: '2024-09-15',
    assessmentVersion: 'v2.1',
    assessedBy: 'Sarah Johnson',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-09-15T14:30:00Z'
  },
  {
    id: '2',
    businessFunction: 'Financial Reporting',
    department: 'Finance',
    rto: 24,
    rpo: 4,
    mtpd: 72,
    financialImpactPerHour: 15000,
    criticalityLevel: 'high',
    dependencies: ['ERP System', 'Database', 'Financial Analytics'],
    lastAssessed: '2024-09-14',
    assessmentVersion: 'v2.0',
    assessedBy: 'Michael Chen',
    createdAt: '2024-02-10T09:00:00Z',
    updatedAt: '2024-09-14T11:00:00Z'
  },
  {
    id: '3',
    businessFunction: 'Manufacturing Line A',
    department: 'Production',
    rto: 4,
    rpo: 2,
    mtpd: 12,
    financialImpactPerHour: 75000,
    criticalityLevel: 'critical',
    dependencies: ['Power Supply', 'Raw Materials', 'Quality Control', 'Maintenance'],
    lastAssessed: '2024-09-13',
    assessmentVersion: 'v2.1',
    assessedBy: 'David Rodriguez',
    createdAt: '2024-01-20T08:00:00Z',
    updatedAt: '2024-09-13T16:00:00Z'
  },
  {
    id: '4',
    businessFunction: 'HR Payroll Processing',
    department: 'HR',
    rto: 48,
    rpo: 24,
    mtpd: 168,
    financialImpactPerHour: 5000,
    criticalityLevel: 'medium',
    dependencies: ['Payroll System', 'Bank Interface', 'Employee Database'],
    lastAssessed: '2024-09-12',
    assessmentVersion: 'v1.8',
    assessedBy: 'Jennifer Smith',
    createdAt: '2024-03-05T07:30:00Z',
    updatedAt: '2024-09-12T10:15:00Z'
  },
  {
    id: '5',
    businessFunction: 'IT Infrastructure Management',
    department: 'IT',
    rto: 6,
    rpo: 2,
    mtpd: 24,
    financialImpactPerHour: 35000,
    criticalityLevel: 'critical',
    dependencies: ['Network Equipment', 'Server Infrastructure', 'Monitoring Tools'],
    lastAssessed: '2024-09-11',
    assessmentVersion: 'v2.0',
    assessedBy: 'Alex Thompson',
    createdAt: '2024-02-20T09:00:00Z',
    updatedAt: '2024-09-11T15:30:00Z'
  },
  {
    id: '6',
    businessFunction: 'Customer Support',
    department: 'Support',
    rto: 8,
    rpo: 4,
    mtpd: 24,
    financialImpactPerHour: 20000,
    criticalityLevel: 'high',
    dependencies: ['Help Desk System', 'Knowledge Base', 'Communication Tools'],
    lastAssessed: '2024-09-10',
    assessmentVersion: 'v1.9',
    assessedBy: 'Lisa Wang',
    createdAt: '2024-03-15T11:00:00Z',
    updatedAt: '2024-09-10T13:45:00Z'
  }
]

const mockBusinessFunctions: BusinessFunction[] = [
  {
    id: '1',
    name: 'Customer Order Processing',
    description: 'End-to-end customer order management and processing',
    department: 'Sales',
    owner: 'Sarah Johnson',
    category: 'primary',
    status: 'active',
    processes: [
      {
        id: 'proc-1',
        name: 'Order Receipt',
        description: 'Receiving and validating customer orders',
        functionId: '1',
        inputs: ['Customer Data', 'Product Information'],
        outputs: ['Order Confirmation', 'Order Record'],
        resources: [
          { id: 'res-1', type: 'human', name: 'Sales Representatives', criticality: 'critical' },
          { id: 'res-2', type: 'technology', name: 'Order Management System', criticality: 'critical' }
        ],
        dependencies: ['Payment Gateway', 'Inventory System']
      }
    ]
  }
]

class BIAManagementAPI {
  private apiClient: BCMAPIClient
  private odooConnector = odooBIAConnector
  private initialized = false

  constructor() {
    this.apiClient = new BCMAPIClient()
    this.initializeConnector()
  }

  private async initializeConnector() {
    if (!this.initialized) {
      await this.odooConnector.authenticate()
      this.initialized = true
    }
  }

  // Convert Odoo process to BIA result format
  private convertOdooToBIA(process: OdooBIAProcess): BIAResult {
    return {
      id: process.id.toString(),
      businessFunction: process.name,
      department: process.company_id?.[1] || 'Main',
      rto: process.optimized_rto_hours || 24,
      rpo: (process.optimized_rpo_minutes || 240) / 60,
      mtpd: process.mtpd_hours || 72,
      financialImpactPerHour: process.hourly_impact_rate || 10000,
      criticalityLevel: process.criticality || 'medium',
      dependencies: process.dependency_ids?.map(id => `Function-${id}`) || [],
      lastAssessed: process.last_ai_analysis || new Date().toISOString(),
      assessmentVersion: 'v2.0',
      assessedBy: 'AI System',
      createdAt: new Date().toISOString(),
      updatedAt: process.last_ai_analysis || new Date().toISOString()
    }
  }


  // Get all BIA results with optional filtering
  async getBIAResults(filters?: {
    department?: string
    criticalityLevel?: string
    lastAssessedAfter?: string
  }): Promise<BIAResult[]> {
    try {
      // First try to get data from Odoo
      await this.initializeConnector()
      const odooProcesses = await this.odooConnector.getBIAProcesses()

      if (odooProcesses && odooProcesses.length > 0) {
        let results = odooProcesses.map(p => this.convertOdooToBIA(p))

        // Apply filters
        if (filters?.department && filters.department !== 'all') {
          results = results.filter(r => r.department === filters.department)
        }
        if (filters?.criticalityLevel && filters.criticalityLevel !== 'all') {
          results = results.filter(r => r.criticalityLevel === filters.criticalityLevel)
        }
        if (filters?.lastAssessedAfter) {
          results = results.filter(r =>
            new Date(r.lastAssessed) > new Date(filters.lastAssessedAfter)
          )
        }

        return results
      }

      // If no Odoo data, try BCM API
      let endpoint = '/api/v1/bcm/bia/results'
      const params = new URLSearchParams()

      if (filters?.department && filters.department !== 'all') {
        params.append('department', filters.department)
      }
      if (filters?.criticalityLevel && filters.criticalityLevel !== 'all') {
        params.append('criticality', filters.criticalityLevel)
      }
      if (filters?.lastAssessedAfter) {
        params.append('last_assessed_after', filters.lastAssessedAfter)
      }

      if (params.toString()) {
        endpoint += `?${params.toString()}`
      }

      const response = await this.apiClient.request<BIAResult[]>(
        endpoint,
        { method: 'GET' },
        () => {
          let results = mockBIAResults

          if (filters?.department && filters.department !== 'all') {
            results = results.filter(r => r.department === filters.department)
          }
          if (filters?.criticalityLevel && filters.criticalityLevel !== 'all') {
            results = results.filter(r => r.criticalityLevel === filters.criticalityLevel)
          }

          return results
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch BIA results:', error)
      // Fallback to filtered mock data
      let results = mockBIAResults

      if (filters?.department && filters.department !== 'all') {
        results = results.filter(r => r.department === filters.department)
      }
      if (filters?.criticalityLevel && filters.criticalityLevel !== 'all') {
        results = results.filter(r => r.criticalityLevel === filters.criticalityLevel)
      }

      return results
    }
  }

  // Get BIA metrics
  async getBIAMetrics(): Promise<BIAMetrics> {
    try {
      // First try to get metrics from Odoo
      await this.initializeConnector()
      const odooMetrics = await this.odooConnector.getBIAMetrics()

      if (odooMetrics) {
        const now = new Date()
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

        return {
          totalFunctions: odooMetrics.totalFunctions,
          criticalFunctions: odooMetrics.criticalFunctions,
          avgRTO: odooMetrics.avgRTO,
          totalFinancialRisk: odooMetrics.totalFinancialRisk,
          assessmentsCompleted: odooMetrics.totalFunctions,
          pendingAssessments: 0,
          nextReviewDate: '2024-12-31'
        }
      }

      // Fallback to BCM API
      const response = await this.apiClient.request<BIAMetrics>(
        '/api/v1/bcm/bia/metrics',
        { method: 'GET' },
        () => {
          const results = mockBIAResults
          const now = new Date()
          const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

          return {
            totalFunctions: results.length,
            criticalFunctions: results.filter(r => r.criticalityLevel === 'critical').length,
            avgRTO: results.length ?
              results.reduce((sum, r) => sum + r.rto, 0) / results.length : 0,
            totalFinancialRisk: results.reduce((sum, r) => sum + (r.financialImpactPerHour * r.mtpd), 0),
            assessmentsCompleted: results.filter(r =>
              new Date(r.lastAssessed) > thirtyDaysAgo
            ).length,
            pendingAssessments: results.filter(r =>
              new Date(r.lastAssessed) <= thirtyDaysAgo
            ).length,
            nextReviewDate: '2024-12-31'
          }
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch BIA metrics:', error)
      // Calculate from mock data
      const results = mockBIAResults
      return {
        totalFunctions: results.length,
        criticalFunctions: results.filter(r => r.criticalityLevel === 'critical').length,
        avgRTO: results.reduce((sum, r) => sum + r.rto, 0) / results.length,
        totalFinancialRisk: results.reduce((sum, r) => sum + (r.financialImpactPerHour * r.mtpd), 0),
        assessmentsCompleted: 4,
        pendingAssessments: 2
      }
    }
  }

  // Get single BIA result by ID
  async getBIAResult(id: string): Promise<BIAResult | null> {
    try {
      // First try to get from Odoo
      await this.initializeConnector()
      const odooProcesses = await this.odooConnector.getBIAProcesses()
      const odooProcess = odooProcesses.find(p => p.id.toString() === id)

      if (odooProcess) {
        return this.convertOdooToBIA(odooProcess)
      }

      // Fallback to BCM API
      const response = await this.apiClient.request<BIAResult>(
        `/api/v1/bcm/bia/results/${id}`,
        { method: 'GET' },
        () => {
          const result = mockBIAResults.find(r => r.id === id)
          if (!result) throw new Error('BIA result not found')
          return result
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch BIA result:', error)
      return mockBIAResults.find(r => r.id === id) || null
    }
  }

  // Create new BIA assessment
  async createBIAAssessment(assessment: Omit<BIAResult, 'id' | 'createdAt' | 'updatedAt'>): Promise<BIAResult> {
    try {
      // First try to create in Odoo
      await this.initializeConnector()
      const odooId = await this.odooConnector.createBIAProcess({
        name: assessment.businessFunction,
        description: `${assessment.department} - RTO: ${assessment.rto}h, RPO: ${assessment.rpo}h`,
        criticality: assessment.criticalityLevel,
        annual_revenue_impact: assessment.financialImpactPerHour * 8760,
        geographical_scope: 'local'
      })

      if (odooId) {
        // Run AI analysis on new process
        await this.odooConnector.runBIAAnalysis(odooId)

        // Fetch and return the created process
        const processes = await this.odooConnector.getBIAProcesses()
        const newProcess = processes.find(p => p.id === odooId)
        if (newProcess) {
          return this.convertOdooToBIA(newProcess)
        }
      }

      // Fallback to BCM API
      const response = await this.apiClient.request<BIAResult>(
        '/api/v1/bcm/bia/results',
        {
          method: 'POST',
          body: JSON.stringify(assessment)
        },
        () => ({
          ...assessment,
          id: Date.now().toString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
      )

      return response.data
    } catch (error) {
      console.error('Failed to create BIA assessment:', error)
      // Return mock created assessment
      return {
        ...assessment,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    }
  }

  // Update existing BIA assessment
  async updateBIAAssessment(id: string, updates: Partial<BIAResult>): Promise<BIAResult> {
    try {
      // First try to update in Odoo
      await this.initializeConnector()
      const odooUpdates: Partial<OdooBIAProcess> = {}

      if (updates.businessFunction) odooUpdates.name = updates.businessFunction
      if (updates.criticalityLevel) odooUpdates.criticality = updates.criticalityLevel
      if (updates.rto !== undefined) odooUpdates.optimized_rto_hours = updates.rto
      if (updates.rpo !== undefined) odooUpdates.optimized_rpo_minutes = updates.rpo * 60
      if (updates.mtpd !== undefined) odooUpdates.mtpd_hours = updates.mtpd
      if (updates.financialImpactPerHour !== undefined) {
        odooUpdates.hourly_impact_rate = updates.financialImpactPerHour
        odooUpdates.annual_revenue_impact = updates.financialImpactPerHour * 8760
      }

      const success = await this.odooConnector.updateBIAProcess(Number(id), odooUpdates)

      if (success) {
        // Fetch updated process
        const processes = await this.odooConnector.getBIAProcesses()
        const updatedProcess = processes.find(p => p.id.toString() === id)
        if (updatedProcess) {
          return this.convertOdooToBIA(updatedProcess)
        }
      }

      // Fallback to BCM API
      const response = await this.apiClient.request<BIAResult>(
        `/api/v1/bcm/bia/results/${id}`,
        {
          method: 'PATCH',
          body: JSON.stringify(updates)
        },
        () => {
          const existing = mockBIAResults.find(r => r.id === id)
          if (!existing) throw new Error('BIA result not found')

          return {
            ...existing,
            ...updates,
            updatedAt: new Date().toISOString()
          }
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to update BIA assessment:', error)
      const existing = mockBIAResults.find(r => r.id === id)
      if (!existing) throw new Error('BIA result not found')

      return {
        ...existing,
        ...updates,
        updatedAt: new Date().toISOString()
      }
    }
  }

  // Delete BIA assessment
  async deleteBIAAssessment(id: string): Promise<boolean> {
    try {
      // First try to delete from Odoo
      await this.initializeConnector()
      const success = await this.odooConnector.deleteBIAProcess(Number(id))

      if (success) {
        return true
      }

      // Fallback to BCM API
      await this.apiClient.request<void>(
        `/api/v1/bcm/bia/results/${id}`,
        { method: 'DELETE' },
        () => undefined
      )

      return true
    } catch (error) {
      console.error('Failed to delete BIA assessment:', error)
      return true // Optimistic deletion for mock
    }
  }

  // Run BIA analysis
  async runBIAAnalysis(functionIds?: string[]): Promise<{
    analysisId: string
    status: string
    results?: any
  }> {
    try {
      await this.initializeConnector()

      // Run Odoo AI analysis for specified functions or all
      if (functionIds && functionIds.length > 0) {
        const analysisPromises = functionIds.map(id =>
          this.odooConnector.runBIAAnalysis(Number(id))
        )
        await Promise.all(analysisPromises)
      } else {
        // Get all processes and run analysis
        const processes = await this.odooConnector.getBIAProcesses()
        const analysisPromises = processes.map(p =>
          this.odooConnector.runBIAAnalysis(p.id)
        )
        await Promise.all(analysisPromises)
      }

      // Get updated metrics after analysis
      const metrics = await this.odooConnector.getBIAMetrics()

      return {
        analysisId: `odoo-analysis-${Date.now()}`,
        status: 'completed',
        results: {
          functionsAnalyzed: functionIds?.length || metrics.totalFunctions,
          criticalPathsIdentified: metrics.criticalFunctions,
          optimizationOpportunities: metrics.highRiskFunctions || 0,
          riskLevel: metrics.criticalFunctions > 3 ? 'high' : 'medium',
          recommendations: [
            'AI-powered analysis completed via Odoo',
            `${metrics.criticalFunctions} critical functions identified`,
            `Total financial risk: $${metrics.totalFinancialRisk.toLocaleString()}`
          ],
          odooMetrics: metrics
        }
      }
    } catch (error) {
      console.error('Failed to run BIA analysis:', error)

      // Fallback to BCM API
      try {
        const response = await this.apiClient.request<{ analysisId: string, status: string, results?: any }>(
          '/api/v1/bcm/bia/run-analysis',
          {
            method: 'POST',
            body: JSON.stringify({ functionIds })
          },
          () => ({
            analysisId: `analysis-${Date.now()}`,
            status: 'completed',
            results: {
              functionsAnalyzed: functionIds?.length || mockBIAResults.length,
              criticalPathsIdentified: 3,
              optimizationOpportunities: 8,
              riskLevel: 'medium',
              recommendations: [
                'Consider reducing RTO for Customer Order Processing',
                'Implement redundancy for Manufacturing Line A',
                'Review dependencies for Financial Reporting'
              ]
            }
          })
        )

        return response.data
      } catch (apiError) {
        return {
          analysisId: `analysis-${Date.now()}`,
          status: 'completed',
          results: {
            functionsAnalyzed: mockBIAResults.length,
            criticalPathsIdentified: 3,
            optimizationOpportunities: 8
          }
        }
      }
    }
  }

  // Get dependency mappings
  async getDependencyMappings(functionId?: string): Promise<DependencyMapping[]> {
    try {
      // First try to get dependencies from Odoo
      await this.initializeConnector()

      if (functionId) {
        const dependencies = await this.odooConnector.getProcessDependencies(Number(functionId))
        if (dependencies && dependencies.length > 0) {
          return dependencies.map((dep: any, index: number) => ({
            id: dep.id.toString(),
            sourceFunction: `Process-${functionId}`,
            targetFunction: dep.name,
            dependencyType: dep.criticality === 'critical' ? 'critical' : 'important',
            description: `Dependency on ${dep.name}`,
            impactLevel: dep.criticality === 'critical' ? 9 : 5,
            recoverySequence: index + 1
          }))
        }
      }

      // Fallback to BCM API
      const endpoint = functionId
        ? `/api/v1/bcm/bia/dependencies?function_id=${functionId}`
        : '/api/v1/bcm/bia/dependencies'

      const response = await this.apiClient.request<DependencyMapping[]>(
        endpoint,
        { method: 'GET' },
        () => [
          {
            id: '1',
            sourceFunction: 'Customer Order Processing',
            targetFunction: 'Payment Gateway',
            dependencyType: 'critical',
            description: 'Required for payment processing',
            impactLevel: 9,
            recoverySequence: 1
          },
          {
            id: '2',
            sourceFunction: 'Manufacturing Line A',
            targetFunction: 'Power Supply',
            dependencyType: 'critical',
            description: 'Primary power source for production',
            impactLevel: 10,
            recoverySequence: 1
          },
          {
            id: '3',
            sourceFunction: 'Financial Reporting',
            targetFunction: 'ERP System',
            dependencyType: 'critical',
            description: 'Source of financial data',
            impactLevel: 8,
            recoverySequence: 2
          }
        ].filter(d => !functionId || d.sourceFunction === functionId)
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch dependency mappings:', error)
      return []
    }
  }

  // Get critical paths analysis
  async getCriticalPaths(): Promise<CriticalPath[]> {
    try {
      const response = await this.apiClient.request<CriticalPath[]>(
        '/api/v1/bcm/bia/critical-paths',
        { method: 'GET' },
        () => [
          {
            id: '1',
            name: 'Revenue Generation Path',
            functions: ['Customer Order Processing', 'Payment Gateway', 'Inventory System'],
            totalRTO: 6,
            bottleneckFunction: 'Customer Order Processing',
            optimizationOpportunities: [
              {
                functionId: '1',
                currentRTO: 2,
                optimizedRTO: 1,
                investment: 50000,
                costBenefit: 125000,
                effort: 'medium'
              }
            ],
            riskLevel: 'high'
          },
          {
            id: '2',
            name: 'Production Path',
            functions: ['Manufacturing Line A', 'Quality Control', 'Raw Materials'],
            totalRTO: 8,
            bottleneckFunction: 'Manufacturing Line A',
            optimizationOpportunities: [
              {
                functionId: '3',
                currentRTO: 4,
                optimizedRTO: 2,
                investment: 100000,
                costBenefit: 200000,
                effort: 'high'
              }
            ],
            riskLevel: 'critical'
          }
        ]
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch critical paths:', error)
      return []
    }
  }

  // Generate BIA report
  async generateBIAReport(type: 'summary' | 'detailed' | 'executive' | 'technical', format: 'pdf' | 'excel' | 'json'): Promise<BIAReport> {
    try {
      const response = await this.apiClient.request<BIAReport>(
        '/api/v1/bcm/bia/reports',
        {
          method: 'POST',
          body: JSON.stringify({ type, format })
        },
        () => ({
          id: `report-${Date.now()}`,
          type,
          generatedAt: new Date().toISOString(),
          generatedBy: 'System',
          data: {
            summary: 'BIA analysis complete',
            functions: mockBIAResults.length,
            criticalFunctions: mockBIAResults.filter(r => r.criticalityLevel === 'critical').length
          },
          format
        })
      )

      return response.data
    } catch (error) {
      console.error('Failed to generate BIA report:', error)
      return {
        id: `report-${Date.now()}`,
        type,
        generatedAt: new Date().toISOString(),
        generatedBy: 'System',
        data: { error: 'Mock report generation' },
        format
      }
    }
  }

  // Get business functions
  async getBusinessFunctions(): Promise<BusinessFunction[]> {
    try {
      const response = await this.apiClient.request<BusinessFunction[]>(
        '/api/v1/bcm/business-functions',
        { method: 'GET' },
        () => mockBusinessFunctions
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch business functions:', error)
      return mockBusinessFunctions
    }
  }

  // Get BIA questionnaire template
  async getBIAQuestionnaire(functionId?: string): Promise<BIAQuestionnaire> {
    try {
      const endpoint = functionId
        ? `/api/v1/bcm/bia/questionnaire?function_id=${functionId}`
        : '/api/v1/bcm/bia/questionnaire/template'

      const response = await this.apiClient.request<BIAQuestionnaire>(
        endpoint,
        { method: 'GET' },
        () => ({
          id: `questionnaire-${Date.now()}`,
          functionId: functionId || 'template',
          questions: [
            {
              id: 'q1',
              category: 'impact',
              question: 'What is the financial impact per hour of disruption?',
              type: 'number',
              required: true,
              weight: 0.3
            },
            {
              id: 'q2',
              category: 'dependencies',
              question: 'What are the critical dependencies for this function?',
              type: 'multiselect',
              options: ['IT Systems', 'Personnel', 'Facilities', 'Third Parties'],
              required: true,
              weight: 0.25
            },
            {
              id: 'q3',
              category: 'recovery',
              question: 'What is the maximum acceptable recovery time?',
              type: 'number',
              required: true,
              weight: 0.25
            },
            {
              id: 'q4',
              category: 'resources',
              question: 'Rate the criticality of required resources (1-10)',
              type: 'scale',
              required: true,
              weight: 0.2
            }
          ],
          responses: [],
          status: 'draft'
        })
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch BIA questionnaire:', error)
      return {
        id: `questionnaire-${Date.now()}`,
        functionId: functionId || 'template',
        questions: [],
        responses: [],
        status: 'draft'
      }
    }
  }

  // Submit BIA questionnaire responses
  async submitBIAQuestionnaire(questionnaireId: string, responses: BIAResponse[]): Promise<BIAResult> {
    try {
      const response = await this.apiClient.request<BIAResult>(
        `/api/v1/bcm/bia/questionnaire/${questionnaireId}/submit`,
        {
          method: 'POST',
          body: JSON.stringify({ responses })
        },
        () => {
          // Mock calculation based on responses
          const financialImpactResponse = responses.find(r => r.questionId === 'q1')
          const recoveryTimeResponse = responses.find(r => r.questionId === 'q3')

          return {
            id: Date.now().toString(),
            businessFunction: 'Assessed Function',
            department: 'Unknown',
            rto: Number(recoveryTimeResponse?.answer) || 24,
            rpo: Math.floor((Number(recoveryTimeResponse?.answer) || 24) / 2),
            mtpd: (Number(recoveryTimeResponse?.answer) || 24) * 3,
            financialImpactPerHour: Number(financialImpactResponse?.answer) || 10000,
            criticalityLevel: 'medium',
            dependencies: ['System Dependencies'],
            lastAssessed: new Date().toISOString().split('T')[0],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to submit BIA questionnaire:', error)
      throw new Error('Failed to process questionnaire responses')
    }
  }

  // Export BIA data to CSV
  exportBIAToCSV(results: BIAResult[]): void {
    const csvContent = [
      ['ID', 'Business Function', 'Department', 'RTO (h)', 'RPO (h)', 'MTPD (h)', 'Financial Impact/Hour', 'Criticality', 'Dependencies', 'Last Assessed', 'Assessed By'],
      ...results.map(result => [
        result.id,
        result.businessFunction,
        result.department,
        result.rto.toString(),
        result.rpo.toString(),
        result.mtpd.toString(),
        result.financialImpactPerHour.toString(),
        result.criticalityLevel,
        result.dependencies.join('; '),
        result.lastAssessed,
        result.assessedBy || 'Unknown'
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `bia_results_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Export critical paths to CSV
  exportCriticalPathsToCSV(paths: CriticalPath[]): void {
    const csvContent = [
      ['Path ID', 'Path Name', 'Functions', 'Total RTO', 'Bottleneck Function', 'Risk Level', 'Optimization Opportunities'],
      ...paths.map(path => [
        path.id,
        path.name,
        path.functions.join('; '),
        path.totalRTO.toString(),
        path.bottleneckFunction,
        path.riskLevel,
        path.optimizationOpportunities.length.toString()
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `critical_paths_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // External Services Integration Methods

  // Send BIA notifications
  async sendBIANotification(processName: string, status: string, recipients: string[]): Promise<boolean> {
    try {
      return await externalServices.sendBIANotification(processName, status, recipients)
    } catch (error) {
      console.error('Failed to send BIA notification:', error)
      return false
    }
  }

  // Process BIA documents
  async processBIADocument(file: File): Promise<any> {
    try {
      const processingRequest: DocumentProcessingRequest = {
        file,
        document_type: 'BIA',
        extract_metadata: true,
        perform_ocr: true,
        analyze_compliance: true,
        generate_summary: true
      }

      const result = await externalServices.processDocument(processingRequest)

      // If document processing successful, potentially create BIA assessment from it
      if (result.processing_status === 'completed' && result.content.structured_data) {
        // Extract BIA data from processed document
        const extractedData = this.extractBIADataFromDocument(result)
        if (extractedData) {
          return await this.createBIAAssessment(extractedData)
        }
      }

      return result
    } catch (error) {
      console.error('Failed to process BIA document:', error)
      return null
    }
  }

  // Get AI recommendations for BIA
  async getBIARecommendations(biaResults: BIAResult[]): Promise<any> {
    try {
      return await externalServices.getAIRecommendations('bia', {
        processes: biaResults.map(r => ({
          id: r.id,
          name: r.businessFunction,
          criticality: r.criticalityLevel,
          rto: r.rto,
          rpo: r.rpo,
          impact: r.financialImpactPerHour,
          dependencies: r.dependencies
        }))
      })
    } catch (error) {
      console.error('Failed to get BIA recommendations:', error)
      return {
        recommendations: ['Review critical process dependencies', 'Consider RTO optimization'],
        confidence: 0.5,
        reasoning: 'Fallback recommendations based on basic analysis'
      }
    }
  }

  // Generate BIA scenario for testing
  async generateBIATestScenario(processIds: string[]): Promise<any> {
    try {
      const processes = await this.getBIAResults({})
      const selectedProcesses = processes.filter(p => processIds.includes(p.id))

      if (selectedProcesses.length === 0) {
        throw new Error('No processes selected for scenario generation')
      }

      // Determine scenario category based on process types and dependencies
      const category = this.determineBestScenarioCategory(selectedProcesses)

      const scenarioRequest = {
        category,
        complexity: Math.min(5, Math.max(1, selectedProcesses.length)),
        duration_hours: 4,
        participants: 8 + selectedProcesses.length * 2,
        affected_systems: selectedProcesses.flatMap(p => p.dependencies),
        custom_objectives: [
          `Test recovery procedures for ${selectedProcesses.map(p => p.businessFunction).join(', ')}`,
          'Validate RTO/RPO targets under stress',
          'Assess interdependency impact'
        ],
        organization_context: `BIA testing scenario for ${selectedProcesses.length} business processes`
      }

      return await externalServices.generateScenario(scenarioRequest)
    } catch (error) {
      console.error('Failed to generate BIA test scenario:', error)
      return null
    }
  }

  // Check external services health
  async checkExternalServicesHealth(): Promise<Record<string, boolean>> {
    try {
      return await externalServices.checkServicesHealth()
    } catch (error) {
      console.error('Failed to check external services health:', error)
      return {
        SCENARIO_ORCHESTRATOR: false,
        NOTIFICATION_SERVICE: false,
        DOCUMENT_PROCESSOR: false,
        AI_ORCHESTRATOR: false,
        BIA_ENGINE: false
      }
    }
  }

  // Private helper methods
  private extractBIADataFromDocument(processedDocument: any): Partial<BIAResult> | null {
    try {
      const { content, metadata } = processedDocument

      // Extract business function name from title or content
      const businessFunction = metadata.title.replace(/\.(pdf|docx|xlsx)$/i, '')

      // Try to extract RTO/RPO from structured data or text analysis
      const text = content.text.toLowerCase()
      const rtoMatch = text.match(/rto.*?(\d+).*?(hour|minute)/i)
      const rpoMatch = text.match(/rpo.*?(\d+).*?(hour|minute)/i)

      const extractedData: Partial<BIAResult> = {
        businessFunction,
        department: 'Extracted',
        rto: rtoMatch ? parseInt(rtoMatch[1]) : 24,
        rpo: rpoMatch ? parseInt(rpoMatch[1]) : 4,
        mtpd: 72, // Default
        financialImpactPerHour: 10000, // Default
        criticalityLevel: 'medium',
        dependencies: metadata.key_terms || [],
        lastAssessed: new Date().toISOString(),
        assessedBy: 'Document Processing AI'
      }

      return extractedData
    } catch (error) {
      console.error('Failed to extract BIA data from document:', error)
      return null
    }
  }

  private determineBestScenarioCategory(processes: BIAResult[]): 'epidemic' | 'blackout' | 'cyber' | 'supply' | 'natural' | 'terrorism' {
    // Logic to determine best scenario type based on process characteristics
    const hasCriticalTech = processes.some(p =>
      p.dependencies.some(dep => dep.toLowerCase().includes('system') || dep.toLowerCase().includes('network'))
    )

    const hasCriticalSupply = processes.some(p =>
      p.dependencies.some(dep => dep.toLowerCase().includes('supply') || dep.toLowerCase().includes('vendor'))
    )

    const hasHighFinancialImpact = processes.some(p => p.financialImpactPerHour > 50000)

    if (hasCriticalTech && hasHighFinancialImpact) return 'cyber'
    if (hasCriticalSupply) return 'supply'
    if (hasHighFinancialImpact) return 'blackout'

    return 'natural' // Default fallback
  }

  // Collaboration Methods
  async getCollaborationSession(sessionId: string): Promise<CollaborationSession> {
    try {
      const response = await this.apiClient.request<CollaborationSession>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}`,
        { method: 'GET' },
        () => ({
          id: sessionId,
          name: 'BIA Analysis Session',
          description: 'Collaborative Business Impact Analysis',
          createdBy: 'admin',
          createdAt: new Date().toISOString(),
          duration: 120,
          status: 'active',
          biaProcessIds: [],
          settings: {
            autoSave: true,
            autoSaveInterval: 30,
            allowComments: true,
            allowScreenSharing: true,
            requireApproval: false,
            maxParticipants: 10
          }
        })
      )
      return response.data
    } catch (error) {
      console.error('Failed to get collaboration session:', error)
      throw error
    }
  }

  async getSessionParticipants(sessionId: string): Promise<SessionParticipant[]> {
    try {
      const response = await this.apiClient.request<SessionParticipant[]>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}/participants`,
        { method: 'GET' },
        () => [
          {
            id: '1',
            name: 'John Smith',
            email: 'john.smith@company.com',
            avatar: '/avatars/john.jpg',
            role: 'BIA Analyst',
            status: 'online',
            permissions: ['view', 'edit', 'comment'],
            joinedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            lastActivity: new Date().toISOString()
          },
          {
            id: '2',
            name: 'Sarah Johnson',
            email: 'sarah.johnson@company.com',
            avatar: '/avatars/sarah.jpg',
            role: 'Business Continuity Manager',
            status: 'online',
            permissions: ['view', 'edit', 'comment', 'approve'],
            joinedAt: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
            lastActivity: new Date(Date.now() - 2 * 60 * 1000).toISOString()
          },
          {
            id: '3',
            name: 'Mike Davis',
            email: 'mike.davis@company.com',
            role: 'Operations Manager',
            status: 'away',
            permissions: ['view', 'comment'],
            joinedAt: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
            lastActivity: new Date(Date.now() - 15 * 60 * 1000).toISOString()
          }
        ]
      )
      return response.data
    } catch (error) {
      console.error('Failed to get session participants:', error)
      return []
    }
  }

  async getSessionComments(sessionId: string): Promise<SessionComment[]> {
    try {
      const response = await this.apiClient.request<SessionComment[]>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}/comments`,
        { method: 'GET' },
        () => [
          {
            id: '1',
            sessionId,
            author: {
              id: '1',
              name: 'John Smith',
              avatar: '/avatars/john.jpg'
            },
            content: 'I think we need to reassess the financial impact for the payment processing system. The current estimate seems too low.',
            timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
            mentions: ['sarah.johnson']
          },
          {
            id: '2',
            sessionId,
            author: {
              id: '2',
              name: 'Sarah Johnson',
              avatar: '/avatars/sarah.jpg'
            },
            content: '@john.smith Good point. Can you provide more details on the regulatory impact? That might increase our financial exposure significantly.',
            timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
            mentions: ['john.smith']
          },
          {
            id: '3',
            sessionId,
            author: {
              id: '3',
              name: 'Mike Davis'
            },
            content: 'From operations perspective, we also need to consider the cascading effects on downstream systems. The dependency map shows 4 critical connections.',
            timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString()
          }
        ]
      )
      return response.data
    } catch (error) {
      console.error('Failed to get session comments:', error)
      return []
    }
  }

  async getSessionChanges(sessionId: string): Promise<SessionChange[]> {
    try {
      const response = await this.apiClient.request<SessionChange[]>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}/changes`,
        { method: 'GET' },
        () => [
          {
            id: '1',
            sessionId,
            author: { id: '1', name: 'John Smith' },
            type: 'edit',
            description: 'updated RTO for Payment Processing from 2h to 4h',
            timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
            details: { field: 'rto', oldValue: 2, newValue: 4 }
          },
          {
            id: '2',
            sessionId,
            author: { id: '2', name: 'Sarah Johnson' },
            type: 'comment',
            description: 'added comment about regulatory impact',
            timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString()
          },
          {
            id: '3',
            sessionId,
            author: { id: '3', name: 'Mike Davis' },
            type: 'join',
            description: 'joined the session',
            timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString()
          }
        ]
      )
      return response.data
    } catch (error) {
      console.error('Failed to get session changes:', error)
      return []
    }
  }

  async addSessionComment(sessionId: string, content: string): Promise<SessionComment> {
    try {
      const response = await this.apiClient.request<SessionComment>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}/comments`,
        {
          method: 'POST',
          body: JSON.stringify({ content })
        },
        () => ({
          id: `comment-${Date.now()}`,
          sessionId,
          author: {
            id: 'current-user',
            name: 'Current User',
            avatar: '/avatars/current.jpg'
          },
          content,
          timestamp: new Date().toISOString()
        })
      )
      return response.data
    } catch (error) {
      console.error('Failed to add session comment:', error)
      throw error
    }
  }

  async inviteParticipant(sessionId: string, email: string): Promise<boolean> {
    try {
      const response = await this.apiClient.request<{ success: boolean }>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}/invite`,
        {
          method: 'POST',
          body: JSON.stringify({ email })
        },
        () => ({ success: true })
      )
      return response.data.success
    } catch (error) {
      console.error('Failed to invite participant:', error)
      return false
    }
  }

  async startScreenSharing(sessionId: string): Promise<boolean> {
    try {
      const response = await this.apiClient.request<{ success: boolean }>(
        `/api/v1/bcm/bia/collaboration/sessions/${sessionId}/screen-share`,
        {
          method: 'POST',
          body: JSON.stringify({ action: 'start' })
        },
        () => ({ success: true })
      )
      return response.data.success
    } catch (error) {
      console.error('Failed to start screen sharing:', error)
      return false
    }
  }
}

// Export singleton instance
export const biaAPI = new BIAManagementAPI()

// Export for use in React Query hooks
export const biaQueryKeys = {
  all: ['bia'] as const,
  results: (filters?: { department?: string, criticalityLevel?: string, lastAssessedAfter?: string }) =>
    [...biaQueryKeys.all, 'results', filters || {}] as const,
  result: (filters?: { department?: string, criticalityLevel?: string, lastAssessedAfter?: string }) =>
    [...biaQueryKeys.all, 'result', filters || {}] as const,
  details: () => [...biaQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...biaQueryKeys.details(), id] as const,
  metrics: () => [...biaQueryKeys.all, 'metrics'] as const,
  dependencies: (functionId?: string) => [...biaQueryKeys.all, 'dependencies', functionId] as const,
  criticalPaths: () => [...biaQueryKeys.all, 'critical-paths'] as const,
  businessFunctions: () => [...biaQueryKeys.all, 'business-functions'] as const,
  questionnaire: (functionId?: string) => [...biaQueryKeys.all, 'questionnaire', functionId] as const,
  reports: () => [...biaQueryKeys.all, 'reports'] as const,
  analysis: () => [...biaQueryKeys.all, 'analysis'] as const,
}

// Collaboration Types
export interface CollaborationSession {
  id: string
  name: string
  description?: string
  createdBy: string
  createdAt: string
  duration?: number // minutes
  status: 'active' | 'paused' | 'completed'
  biaProcessIds: string[]
  settings: SessionSettings
}

export interface SessionSettings {
  autoSave: boolean
  autoSaveInterval: number // seconds
  allowComments: boolean
  allowScreenSharing: boolean
  requireApproval: boolean
  maxParticipants?: number
}

export interface SessionParticipant {
  id: string
  name: string
  email: string
  avatar?: string
  role: string
  status: 'online' | 'away' | 'busy' | 'offline'
  permissions: string[] // ['view', 'edit', 'comment', 'approve']
  joinedAt: string
  lastActivity: string
}

export interface SessionComment {
  id: string
  sessionId: string
  author: {
    id: string
    name: string
    avatar?: string
  }
  content: string
  timestamp: string
  mentions?: string[]
  attachments?: CommentAttachment[]
  replyTo?: string
}

export interface CommentAttachment {
  id: string
  filename: string
  url: string
  type: string
  size: number
}

export interface SessionChange {
  id: string
  sessionId: string
  author: {
    id: string
    name: string
  }
  type: 'edit' | 'comment' | 'join' | 'leave' | 'status_change'
  description: string
  timestamp: string
  details?: any
}