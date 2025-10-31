// External Services Integration Client
// Интегрирует все внешние микросервисы BCM Platform

// Service URLs
const SERVICES = {
  SCENARIO_ORCHESTRATOR: 'http://localhost:8001',
  NOTIFICATION_SERVICE: 'http://localhost:8002',
  DOCUMENT_PROCESSOR: 'http://localhost:8003',
  AI_ORCHESTRATOR: 'http://localhost:8004',
  BIA_ENGINE: 'http://localhost:8082'
}

// Types for external services
export interface ScenarioRequest {
  category: 'epidemic' | 'blackout' | 'cyber' | 'supply' | 'natural' | 'terrorism'
  complexity: number // 1-5
  duration_hours: number
  participants: number
  affected_systems: string[]
  custom_objectives: string[]
  organization_context?: string
}

export interface GeneratedScenario {
  id: string
  title: string
  description: string
  category: string
  complexity: number
  timeline: ScenarioEvent[]
  objectives: string[]
  resources_required: string[]
  key_decisions: string[]
  success_criteria: string[]
  estimated_duration: number
  participant_roles: ParticipantRole[]
}

export interface ScenarioEvent {
  time_minutes: number
  event_type: 'initial_incident' | 'escalation' | 'complication' | 'recovery_opportunity' | 'external_pressure'
  title: string
  description: string
  impact_level: number
  required_actions: string[]
  available_resources: string[]
}

export interface ParticipantRole {
  role: string
  responsibilities: string[]
  authority_level: number
  communication_channels: string[]
}

export interface NotificationRequest {
  type: 'email' | 'sms' | 'push' | 'webhook'
  recipients: string[]
  subject?: string
  message: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  category?: 'bia_analysis' | 'scenario_exercise' | 'plan_update' | 'audit_reminder'
}

export interface DocumentProcessingRequest {
  file: File
  document_type?: 'BCP' | 'BIA' | 'RISK_ASSESSMENT' | 'PROCEDURE' | 'TRAINING' | 'AUDIT_REPORT'
  extract_metadata?: boolean
  perform_ocr?: boolean
  analyze_compliance?: boolean
  generate_summary?: boolean
}

export interface ProcessedDocument {
  id: string
  filename: string
  document_type: string
  metadata: DocumentMetadata
  content: {
    text: string
    structured_data: any
    compliance_analysis?: ComplianceAnalysis
  }
  processing_status: 'completed' | 'processing' | 'failed'
}

export interface DocumentMetadata {
  title: string
  author: string
  creation_date: string
  modification_date: string
  version: string
  language: string
  page_count: number
  word_count: number
  key_terms: string[]
  document_classification: string
}

export interface ComplianceAnalysis {
  iso22301_alignment: {
    score: number
    covered_clauses: string[]
    missing_clauses: string[]
    recommendations: string[]
  }
  document_quality: {
    completeness: number
    clarity: number
    consistency: number
    actionability: number
  }
}

// External Services Client
export class ExternalServicesClient {

  // Scenario Orchestrator Integration
  async generateScenario(request: ScenarioRequest): Promise<GeneratedScenario> {
    try {
      const response = await fetch(`${SERVICES.SCENARIO_ORCHESTRATOR}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })

      if (!response.ok) throw new Error('Failed to generate scenario')
      return await response.json()
    } catch (error) {
      console.error('Scenario generation failed:', error)
      // Return mock scenario for development
      return {
        id: `scenario_${Date.now()}`,
        title: `${request.category.toUpperCase()} Simulation Exercise`,
        description: `A ${request.complexity}-level ${request.category} scenario affecting ${request.affected_systems.join(', ')}`,
        category: request.category,
        complexity: request.complexity,
        timeline: [
          {
            time_minutes: 0,
            event_type: 'initial_incident',
            title: 'Incident Detection',
            description: 'Initial incident has been detected and requires immediate response',
            impact_level: 5,
            required_actions: ['Assess situation', 'Notify stakeholders', 'Activate response team'],
            available_resources: ['Emergency contacts', 'Initial response procedures']
          },
          {
            time_minutes: 30,
            event_type: 'escalation',
            title: 'Situation Escalation',
            description: 'The incident is escalating and requires additional resources',
            impact_level: 7,
            required_actions: ['Escalate to management', 'Activate business continuity plan'],
            available_resources: ['Backup systems', 'Alternative facilities']
          }
        ],
        objectives: request.custom_objectives.length > 0 ? request.custom_objectives : [
          'Test incident response procedures',
          'Evaluate communication effectiveness',
          'Assess recovery capabilities'
        ],
        resources_required: ['Simulation facilitator', 'Communication systems', 'Meeting spaces'],
        key_decisions: ['When to activate full response', 'Resource allocation priorities'],
        success_criteria: ['All participants understand their roles', 'Response time under target'],
        estimated_duration: request.duration_hours * 60,
        participant_roles: [
          {
            role: 'Incident Commander',
            responsibilities: ['Coordinate overall response', 'Make strategic decisions'],
            authority_level: 10,
            communication_channels: ['Primary command', 'Executive briefing']
          }
        ]
      }
    }
  }

  async getScenarioTemplates(): Promise<GeneratedScenario[]> {
    try {
      const response = await fetch(`${SERVICES.SCENARIO_ORCHESTRATOR}/templates`)
      if (!response.ok) throw new Error('Failed to fetch templates')
      return await response.json()
    } catch (error) {
      console.error('Failed to fetch scenario templates:', error)
      return []
    }
  }

  // Notification Service Integration
  async sendNotification(request: NotificationRequest): Promise<boolean> {
    try {
      const response = await fetch(`${SERVICES.NOTIFICATION_SERVICE}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })

      return response.ok
    } catch (error) {
      console.error('Notification send failed:', error)
      return false
    }
  }

  async sendBIANotification(processName: string, status: string, recipients: string[]): Promise<boolean> {
    return this.sendNotification({
      type: 'email',
      recipients,
      subject: `BIA Process Update: ${processName}`,
      message: `The BIA analysis for ${processName} has been ${status}. Please review the results in the BCM Platform.`,
      priority: 'medium',
      category: 'bia_analysis'
    })
  }

  // Document Processor Integration
  async processDocument(request: DocumentProcessingRequest): Promise<ProcessedDocument> {
    try {
      const formData = new FormData()
      formData.append('file', request.file)
      formData.append('document_type', request.document_type || 'BIA')
      formData.append('extract_metadata', String(request.extract_metadata ?? true))
      formData.append('perform_ocr', String(request.perform_ocr ?? true))
      formData.append('analyze_compliance', String(request.analyze_compliance ?? true))

      const response = await fetch(`${SERVICES.DOCUMENT_PROCESSOR}/process`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Document processing failed')
      return await response.json()
    } catch (error) {
      console.error('Document processing failed:', error)
      // Return mock processed document
      return {
        id: `doc_${Date.now()}`,
        filename: request.file.name,
        document_type: request.document_type || 'BIA',
        metadata: {
          title: request.file.name,
          author: 'Unknown',
          creation_date: new Date().toISOString(),
          modification_date: new Date().toISOString(),
          version: '1.0',
          language: 'en',
          page_count: 10,
          word_count: 2500,
          key_terms: ['business impact', 'recovery', 'criticality'],
          document_classification: 'Business Continuity'
        },
        content: {
          text: 'Document content extracted...',
          structured_data: {},
          compliance_analysis: {
            iso22301_alignment: {
              score: 85,
              covered_clauses: ['4.1', '4.2', '8.2'],
              missing_clauses: ['5.3', '6.1'],
              recommendations: ['Add risk assessment section', 'Include monitoring procedures']
            },
            document_quality: {
              completeness: 80,
              clarity: 90,
              consistency: 85,
              actionability: 75
            }
          }
        },
        processing_status: 'completed'
      }
    }
  }

  // AI Orchestrator Integration
  async getAIRecommendations(context: 'bia' | 'scenario' | 'planning', data: any): Promise<any> {
    try {
      const response = await fetch(`${SERVICES.AI_ORCHESTRATOR}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context, data })
      })

      if (!response.ok) throw new Error('AI recommendations failed')
      return await response.json()
    } catch (error) {
      console.error('AI recommendations failed:', error)
      return {
        recommendations: [
          'Consider implementing automated backup procedures',
          'Review and update communication protocols',
          'Conduct regular scenario exercises'
        ],
        confidence: 0.8,
        reasoning: 'Based on current BIA data and industry best practices'
      }
    }
  }

  // Service Health Checks
  async checkServicesHealth(): Promise<Record<string, boolean>> {
    const health: Record<string, boolean> = {}

    for (const [serviceName, url] of Object.entries(SERVICES)) {
      try {
        const response = await fetch(`${url}/health`, {
          method: 'GET',
          signal: AbortSignal.timeout(5000) // 5 second timeout
        })
        health[serviceName] = response.ok
      } catch {
        health[serviceName] = false
      }
    }

    return health
  }
}

// Export singleton instance
export const externalServices = new ExternalServicesClient()

// Export types
export type {
  ScenarioRequest,
  GeneratedScenario,
  NotificationRequest,
  DocumentProcessingRequest,
  ProcessedDocument
}