/**
 * Digital Twin Service
 * Централизованный сервис для управления всеми 4 блоками Digital Twin
 */

import { simulationService } from './simulationService'
import { bcmService } from './bcm'
import { analyticsService } from './analyticsService'

// Типы данных для Digital Twin
export interface TwinBlock {
  id: number
  name: string
  status: 'active' | 'idle' | 'error' | 'processing'
  health: number // 0-100
  lastUpdate: string
  metrics?: Record<string, any>
}

export interface DataStream {
  id: string
  source: string
  type: string
  frequency: number // messages per second
  status: 'connected' | 'disconnected' | 'error'
  lastMessage?: string
  eventCount: number
}

export interface OrganizationProfile {
  id: string
  name: string
  departments: number
  processes: number
  employees: number
  riskPoints: number
  criticalAssets: number
  resilienceScore: number
  maturityLevel: 1 | 2 | 3 | 4 | 5
  digitalReadiness: number // 0-100
  lastAssessment: string
}

export interface TwinInsight {
  id: string
  type: 'risk' | 'opportunity' | 'warning' | 'recommendation'
  title: string
  description: string
  confidence: number // 0-100
  impact: 'low' | 'medium' | 'high' | 'critical'
  source: string
  timestamp: string
  actionable: boolean
  suggestedActions?: string[]
}

export interface SimulationScenario {
  id: string
  name: string
  description: string
  type: string
  complexity: 1 | 2 | 3 | 4 | 5
  duration: number // minutes
  requiredData: string[]
  outcomes: string[]
  jaamsimModel?: string
}

export interface DecisionRecommendation {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  expectedImpact: number
  implementation: {
    effort: 'low' | 'medium' | 'high'
    timeframe: string
    resources: string[]
    steps: string[]
  }
  risks: string[]
  benefits: string[]
  status: 'pending' | 'approved' | 'implementing' | 'completed' | 'rejected'
}

export interface DigitalTwinState {
  blocks: TwinBlock[]
  dataStreams: DataStream[]
  organizationProfile: OrganizationProfile
  insights: TwinInsight[]
  activeSimulations: string[]
  recommendations: DecisionRecommendation[]
  eventBus: {
    connected: boolean
    messagesPerSecond: number
    totalMessages: number
    queueDepth: number
  }
}

class DigitalTwinService {
  private state: DigitalTwinState
  private wsConnection: WebSocket | null = null
  private eventBusConnection: WebSocket | null = null
  private updateCallbacks: Set<(state: DigitalTwinState) => void> = new Set()
  private metricsInterval: NodeJS.Timeout | null = null

  constructor() {
    this.state = this.initializeState()
    this.startMonitoring()
  }

  /**
   * Инициализация начального состояния Digital Twin
   */
  private initializeState(): DigitalTwinState {
    return {
      blocks: [
        {
          id: 1,
          name: 'Data Collection & Event Bus',
          status: 'idle',
          health: 100,
          lastUpdate: new Date().toISOString()
        },
        {
          id: 2,
          name: 'Intelligent Assembly',
          status: 'idle',
          health: 100,
          lastUpdate: new Date().toISOString()
        },
        {
          id: 3,
          name: 'Simulation Engine',
          status: 'idle',
          health: 100,
          lastUpdate: new Date().toISOString()
        },
        {
          id: 4,
          name: 'Decision Support',
          status: 'idle',
          health: 100,
          lastUpdate: new Date().toISOString()
        }
      ],
      dataStreams: [],
      organizationProfile: {
        id: 'org-001',
        name: 'Organization',
        departments: 0,
        processes: 0,
        employees: 0,
        riskPoints: 0,
        criticalAssets: 0,
        resilienceScore: 0,
        maturityLevel: 1,
        digitalReadiness: 0,
        lastAssessment: new Date().toISOString()
      },
      insights: [],
      activeSimulations: [],
      recommendations: [],
      eventBus: {
        connected: false,
        messagesPerSecond: 0,
        totalMessages: 0,
        queueDepth: 0
      }
    }
  }

  /**
   * BLOCK 1: Data Collection & Event Bus
   */
  async connectToEventBus(): Promise<void> {
    try {
      const eventBusUrl = 'ws://localhost:8001/ws/digital-twin'

      this.eventBusConnection = new WebSocket(eventBusUrl)

      this.eventBusConnection.onopen = () => {
        console.log('✅ Connected to Event Bus')
        this.updateBlockStatus(1, 'active', 100)
        this.state.eventBus.connected = true

        // Subscribe to relevant event streams
        this.eventBusConnection?.send(JSON.stringify({
          type: 'subscribe',
          channels: [
            'bcm-events',
            'risk-updates',
            'incident-alerts',
            'system-metrics',
            'ai-insights'
          ]
        }))
      }

      this.eventBusConnection.onmessage = (event) => {
        this.processEventBusMessage(JSON.parse(event.data))
      }

      this.eventBusConnection.onerror = (error) => {
        console.error('❌ Event Bus error:', error)
        this.updateBlockStatus(1, 'error', 50)
      }

      this.eventBusConnection.onclose = () => {
        console.log('Event Bus disconnected')
        this.state.eventBus.connected = false
        this.updateBlockStatus(1, 'idle', 75)

        // Attempt reconnection after 5 seconds
        setTimeout(() => this.connectToEventBus(), 5000)
      }
    } catch (error) {
      console.error('Failed to connect to Event Bus:', error)
      this.updateBlockStatus(1, 'error', 25)
    }
  }

  private processEventBusMessage(message: any): void {
    // Update event bus metrics
    this.state.eventBus.messagesPerSecond++
    this.state.eventBus.totalMessages++

    // Process based on message type
    switch (message.type) {
      case 'risk-update':
        this.processRiskUpdate(message.data)
        break
      case 'incident-alert':
        this.processIncidentAlert(message.data)
        break
      case 'system-metric':
        this.processSystemMetric(message.data)
        break
      case 'ai-insight':
        this.processAIInsight(message.data)
        break
      default:
        // Store in general event stream
        this.addDataStream(message)
    }

    this.notifySubscribers()
  }

  private addDataStream(message: any): void {
    const stream: DataStream = {
      id: `stream-${Date.now()}`,
      source: message.source || 'unknown',
      type: message.type || 'general',
      frequency: 1,
      status: 'connected',
      lastMessage: new Date().toISOString(),
      eventCount: 1
    }

    // Check if stream exists and update, otherwise add new
    const existingIndex = this.state.dataStreams.findIndex(s =>
      s.source === stream.source && s.type === stream.type
    )

    if (existingIndex >= 0) {
      this.state.dataStreams[existingIndex].eventCount++
      this.state.dataStreams[existingIndex].lastMessage = stream.lastMessage
    } else {
      this.state.dataStreams.push(stream)
    }
  }

  /**
   * BLOCK 2: Intelligent Assembly & Organization Profile
   */
  async buildOrganizationProfile(): Promise<OrganizationProfile> {
    console.log('🏗️ Building organization profile...')
    this.updateBlockStatus(2, 'processing', 100)

    try {
      // Gather data from multiple sources
      const [bcmMetrics, riskData, analytics] = await Promise.all([
        bcmService.getDashboardMetrics(),
        this.fetchRiskAssessment(),
        analyticsService.getDashboardData()
      ])

      // Build comprehensive profile
      this.state.organizationProfile = {
        id: 'org-001',
        name: 'Digital Organization',
        departments: 12,
        processes: 47,
        employees: 250,
        riskPoints: bcmMetrics.totalRisks,
        criticalAssets: 23,
        resilienceScore: bcmMetrics.complianceScore,
        maturityLevel: this.calculateMaturityLevel(bcmMetrics.complianceScore),
        digitalReadiness: analytics.dashboard.platform_effectiveness,
        lastAssessment: new Date().toISOString()
      }

      // Generate insights from profile
      this.generateProfileInsights()

      this.updateBlockStatus(2, 'active', 100)
      this.notifySubscribers()

      return this.state.organizationProfile
    } catch (error) {
      console.error('Failed to build organization profile:', error)
      this.updateBlockStatus(2, 'error', 50)
      throw error
    }
  }

  private calculateMaturityLevel(score: number): 1 | 2 | 3 | 4 | 5 {
    if (score >= 90) return 5
    if (score >= 75) return 4
    if (score >= 60) return 3
    if (score >= 40) return 2
    return 1
  }

  private generateProfileInsights(): void {
    const profile = this.state.organizationProfile

    // Risk-based insights
    if (profile.riskPoints > 100) {
      this.addInsight({
        type: 'warning',
        title: 'High Risk Exposure',
        description: `Organization has ${profile.riskPoints} identified risk points. Consider prioritizing risk mitigation strategies.`,
        confidence: 95,
        impact: 'high',
        actionable: true,
        suggestedActions: [
          'Conduct detailed risk assessment',
          'Implement risk mitigation controls',
          'Update BCPs for high-risk areas'
        ]
      })
    }

    // Resilience insights
    if (profile.resilienceScore < 70) {
      this.addInsight({
        type: 'recommendation',
        title: 'Improve Resilience Score',
        description: `Current resilience score of ${profile.resilienceScore}% is below optimal. Enhancement needed.`,
        confidence: 85,
        impact: 'medium',
        actionable: true,
        suggestedActions: [
          'Enhance incident response procedures',
          'Conduct resilience training',
          'Update recovery strategies'
        ]
      })
    }

    // Digital readiness insights
    if (profile.digitalReadiness > 80) {
      this.addInsight({
        type: 'opportunity',
        title: 'Digital Transformation Ready',
        description: 'High digital readiness score indicates potential for advanced automation.',
        confidence: 90,
        impact: 'medium',
        actionable: true,
        suggestedActions: [
          'Implement AI-driven decision support',
          'Automate routine BCM tasks',
          'Deploy predictive analytics'
        ]
      })
    }
  }

  private addInsight(insight: Omit<TwinInsight, 'id' | 'source' | 'timestamp'>): void {
    const newInsight: TwinInsight = {
      id: `insight-${Date.now()}`,
      source: 'Digital Twin AI',
      timestamp: new Date().toISOString(),
      ...insight
    }

    this.state.insights.unshift(newInsight)

    // Keep only last 50 insights
    if (this.state.insights.length > 50) {
      this.state.insights = this.state.insights.slice(0, 50)
    }
  }

  /**
   * BLOCK 3: Simulation Engine (JaamSim Integration)
   */
  async runSimulation(scenarioId: string, parameters?: any): Promise<void> {
    console.log('🎮 Starting simulation:', scenarioId)
    this.updateBlockStatus(3, 'processing', 100)

    try {
      // Start JaamSim simulation
      const result = await simulationService.startSimulation(scenarioId)

      if (result.success && result.simulation_id) {
        this.state.activeSimulations.push(result.simulation_id)

        // Monitor simulation progress
        this.monitorSimulation(scenarioId, result.simulation_id)

        this.updateBlockStatus(3, 'active', 100)
      } else {
        throw new Error('Failed to start simulation')
      }
    } catch (error) {
      console.error('Simulation error:', error)
      this.updateBlockStatus(3, 'error', 50)
      throw error
    }
  }

  private async monitorSimulation(exerciseId: string, simulationId: string): Promise<void> {
    const monitorInterval = setInterval(async () => {
      try {
        const metrics = await simulationService.getJaamSimMetrics(exerciseId)

        // Update Block 3 metrics
        this.state.blocks[2].metrics = {
          processedEvents: metrics.processedEvents,
          activeEntities: metrics.activeEntities,
          utilization: metrics.utilization
        }

        // Check if simulation completed
        const status = await simulationService.getSimulationStatus(exerciseId)
        if (status.status !== 'running') {
          clearInterval(monitorInterval)
          await this.processSimulationResults(exerciseId)
        }

        this.notifySubscribers()
      } catch (error) {
        console.error('Error monitoring simulation:', error)
        clearInterval(monitorInterval)
      }
    }, 2000)
  }

  private async processSimulationResults(exerciseId: string): Promise<void> {
    const results = await simulationService.getSimulationResults(exerciseId)

    if (results) {
      // Generate insights from simulation
      this.addInsight({
        type: 'recommendation',
        title: 'Simulation Completed',
        description: `Simulation achieved ${results.summary.completionRate}% completion with ${results.summary.efficiency}% efficiency`,
        confidence: results.summary.efficiency,
        impact: 'medium',
        actionable: true,
        suggestedActions: results.recommendations?.map(r => r.title) || []
      })

      // Generate recommendations for Block 4
      this.generateDecisionRecommendations(results)
    }

    // Remove from active simulations
    this.state.activeSimulations = this.state.activeSimulations.filter(
      id => id !== exerciseId
    )

    this.updateBlockStatus(3, 'idle', 100)
  }

  /**
   * BLOCK 4: Decision Support & Implementation
   */
  private generateDecisionRecommendations(simulationResults: any): void {
    console.log('🎯 Generating decision recommendations...')
    this.updateBlockStatus(4, 'processing', 100)

    // Convert simulation recommendations to decision recommendations
    if (simulationResults.recommendations) {
      simulationResults.recommendations.forEach((rec: any) => {
        const recommendation: DecisionRecommendation = {
          id: `dec-${Date.now()}-${Math.random()}`,
          title: rec.title,
          description: rec.description,
          priority: this.mapPriority(rec.priority),
          confidence: 80,
          expectedImpact: rec.expected_impact || 50,
          implementation: {
            effort: rec.implementation_effort || 'medium',
            timeframe: '2-4 weeks',
            resources: ['BCM Team', 'IT Support'],
            steps: [
              'Review recommendation details',
              'Assess organizational impact',
              'Develop implementation plan',
              'Execute and monitor'
            ]
          },
          risks: ['Implementation complexity', 'Resource availability'],
          benefits: ['Improved resilience', 'Risk reduction'],
          status: 'pending'
        }

        this.state.recommendations.push(recommendation)
      })
    }

    this.updateBlockStatus(4, 'active', 100)
    this.notifySubscribers()
  }

  async implementRecommendation(recommendationId: string): Promise<void> {
    const rec = this.state.recommendations.find(r => r.id === recommendationId)

    if (!rec) {
      throw new Error('Recommendation not found')
    }

    // Update status
    rec.status = 'implementing'

    // Log implementation
    console.log(`Implementing recommendation: ${rec.title}`)

    // Simulate implementation process
    setTimeout(() => {
      rec.status = 'completed'
      this.addInsight({
        type: 'opportunity',
        title: 'Recommendation Implemented',
        description: `Successfully implemented: ${rec.title}`,
        confidence: 100,
        impact: 'low',
        actionable: false
      })
      this.notifySubscribers()
    }, 5000)

    this.notifySubscribers()
  }

  /**
   * Utility Methods
   */
  private updateBlockStatus(blockId: number, status: TwinBlock['status'], health: number): void {
    const block = this.state.blocks.find(b => b.id === blockId)
    if (block) {
      block.status = status
      block.health = health
      block.lastUpdate = new Date().toISOString()
    }
  }

  private mapPriority(priority: string): DecisionRecommendation['priority'] {
    const map: Record<string, DecisionRecommendation['priority']> = {
      'low': 'low',
      'medium': 'medium',
      'high': 'high',
      'critical': 'critical'
    }
    return map[priority.toLowerCase()] || 'medium'
  }

  private async fetchRiskAssessment(): Promise<any> {
    try {
      // Fetch from BIA Engine or similar
      return await fetch('http://localhost:8082/api/risks/assessment')
        .then(r => r.json())
        .catch(() => ({ risks: [], score: 70 }))
    } catch {
      return { risks: [], score: 70 }
    }
  }

  private processRiskUpdate(data: any): void {
    this.addInsight({
      type: 'risk',
      title: 'Risk Level Updated',
      description: data.description || 'Risk parameters have changed',
      confidence: 75,
      impact: data.severity || 'medium',
      actionable: true,
      suggestedActions: ['Review risk assessment', 'Update mitigation plans']
    })
  }

  private processIncidentAlert(data: any): void {
    this.addInsight({
      type: 'warning',
      title: 'Incident Alert',
      description: data.description || 'New incident detected',
      confidence: 90,
      impact: 'high',
      actionable: true,
      suggestedActions: ['Activate incident response', 'Notify stakeholders']
    })
  }

  private processSystemMetric(data: any): void {
    // Update relevant block metrics
    if (data.block) {
      const block = this.state.blocks.find(b => b.id === data.block)
      if (block) {
        block.metrics = { ...block.metrics, ...data.metrics }
      }
    }
  }

  private processAIInsight(data: any): void {
    this.addInsight({
      type: 'recommendation',
      title: data.title || 'AI Insight',
      description: data.description,
      confidence: data.confidence || 70,
      impact: data.impact || 'medium',
      actionable: data.actionable !== false,
      suggestedActions: data.actions || []
    })
  }

  /**
   * Monitoring and Subscriptions
   */
  private startMonitoring(): void {
    // Update metrics every second
    this.metricsInterval = setInterval(() => {
      // Reset messages per second counter
      this.state.eventBus.messagesPerSecond = 0

      // Check block health
      this.state.blocks.forEach(block => {
        // Degrade health if not updated recently
        const lastUpdate = new Date(block.lastUpdate)
        const now = new Date()
        const minutesSinceUpdate = (now.getTime() - lastUpdate.getTime()) / 60000

        if (minutesSinceUpdate > 5 && block.health > 50) {
          block.health = Math.max(50, block.health - 5)
        }
      })

      this.notifySubscribers()
    }, 1000)
  }

  subscribe(callback: (state: DigitalTwinState) => void): () => void {
    this.updateCallbacks.add(callback)

    // Return unsubscribe function
    return () => {
      this.updateCallbacks.delete(callback)
    }
  }

  private notifySubscribers(): void {
    this.updateCallbacks.forEach(callback => {
      callback(this.state)
    })
  }

  /**
   * Public API
   */
  getState(): DigitalTwinState {
    return this.state
  }

  async initialize(): Promise<void> {
    console.log('🚀 Initializing Digital Twin Service...')

    // Connect to Event Bus (Block 1)
    await this.connectToEventBus()

    // Build Organization Profile (Block 2)
    await this.buildOrganizationProfile()

    // Block 3 (Simulation) initialized on demand
    // Block 4 (Decision) activated after simulations

    console.log('✅ Digital Twin Service initialized')
  }

  async shutdown(): void {
    console.log('Shutting down Digital Twin Service...')

    if (this.metricsInterval) {
      clearInterval(this.metricsInterval)
    }

    if (this.eventBusConnection) {
      this.eventBusConnection.close()
    }

    if (this.wsConnection) {
      this.wsConnection.close()
    }

    this.updateCallbacks.clear()
  }

  // Scenarios management
  async getAvailableScenarios(): Promise<SimulationScenario[]> {
    return [
      {
        id: 'dt-scenario-1',
        name: 'System Failure Recovery',
        description: 'Test organization response to critical system failure',
        type: 'technical',
        complexity: 3,
        duration: 30,
        requiredData: ['system-metrics', 'dependency-map'],
        outcomes: ['recovery-time', 'impact-assessment']
      },
      {
        id: 'dt-scenario-2',
        name: 'Supply Chain Disruption',
        description: 'Evaluate business continuity during supply chain issues',
        type: 'operational',
        complexity: 4,
        duration: 45,
        requiredData: ['supplier-data', 'inventory-levels'],
        outcomes: ['alternative-suppliers', 'stock-management']
      },
      {
        id: 'dt-scenario-3',
        name: 'Cyber Attack Response',
        description: 'Test incident response to cyber security breach',
        type: 'security',
        complexity: 5,
        duration: 60,
        requiredData: ['security-logs', 'access-patterns'],
        outcomes: ['containment-time', 'data-integrity']
      },
      {
        id: 'dt-scenario-4',
        name: 'Pandemic Business Continuity',
        description: 'Assess organizational resilience during pandemic',
        type: 'strategic',
        complexity: 5,
        duration: 90,
        requiredData: ['workforce-data', 'remote-capabilities'],
        outcomes: ['operational-continuity', 'workforce-productivity']
      }
    ]
  }
}

// Export singleton instance
export const digitalTwinService = new DigitalTwinService()
export default digitalTwinService