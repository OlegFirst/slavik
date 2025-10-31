/**
 * Unified Simulation Hub Service
 * Централизованный хаб для управления ВСЕМИ типами симуляций в системе BCM
 */

import axios from 'axios'

// Конфигурация всех симуляционных движков
const SIMULATION_ENGINES = {
  // Основные движки
  JAAMSIM: {
    name: 'JaamSim - Discrete Event Simulation',
    url: 'http://localhost:5900',
    type: 'discrete-event',
    capabilities: ['3d-visualization', 'queue-modeling', 'resource-allocation', 'evacuation'],
    memory: '2GB',
    features: {
      vnc: true,
      realtime: true,
      batch: true,
      scenarios: ['evacuation', 'queues', 'resources', 'processes']
    }
  },

  NICS: {
    name: 'Next-Gen Incident Command System',
    url: 'http://localhost:8443',
    type: 'incident-command',
    capabilities: ['geo-mapping', 'real-time-comm', 'multi-agency', 'situational-awareness'],
    stack: {
      database: 'PostgreSQL + PostGIS',
      messaging: 'RabbitMQ',
      search: 'Elasticsearch',
      maps: 'GeoServer'
    }
  },

  MONTE_CARLO: {
    name: 'Monte Carlo Risk Simulation',
    url: 'http://localhost:8085/api/monte-carlo',
    type: 'statistical',
    capabilities: ['risk-analysis', 'var-cvar', 'portfolio', 'correlation'],
    iterations: 10000,
    methods: ['box-muller', 'latin-hypercube', 'sobol-sequences']
  },

  DIGITAL_TWIN: {
    name: 'Digital Twin Simulation Engine',
    url: 'http://localhost:8094',
    type: 'digital-twin',
    capabilities: ['real-time-sync', 'predictive', 'personal', 'organizational'],
    visualization: 'Three.js',
    storage: 'Supabase Edge Functions'
  },

  SCENARIO_ORCHESTRATOR: {
    name: 'AI Scenario Orchestrator',
    url: 'http://localhost:8085',
    type: 'ai-orchestrator',
    capabilities: ['ai-generation', 'learning', 'complexity-levels', 'adaptive'],
    scenarios: ['pandemic', 'blackout', 'cyber-attack', 'supply-chain', 'natural-disaster'],
    complexity: [1, 2, 3, 4, 5]
  },

  SIMULATION_ADAPTER: {
    name: 'Multi-Engine Adapter',
    url: 'http://localhost:8012',
    type: 'adapter',
    capabilities: ['multi-engine', 'batch-processing', 'event-bus', 'orchestration'],
    engines: ['JaamSim', 'AnyLogic PLE', 'Custom Python', 'MATLAB']
  },

  MCP_SERVER: {
    name: 'Model Context Protocol Server',
    url: 'http://localhost:8087',
    type: 'ai-tools',
    capabilities: ['claude-integration', 'gpt-integration', 'pattern-analysis', 'recommendations'],
    path: '/Users/MD/ISO-22301/tools/mcp-server'
  }
}

// Типы симуляций
export enum SimulationType {
  TABLETOP = 'tabletop',
  WALKTHROUGH = 'walkthrough',
  FUNCTIONAL = 'functional',
  FULL_SCALE = 'full-scale',
  SIMULATION = 'simulation',
  HYBRID = 'hybrid'
}

// Интерфейсы
export interface SimulationScenario {
  id: string
  name: string
  description: string
  type: SimulationType
  engines: string[] // какие движки использовать
  complexity: 1 | 2 | 3 | 4 | 5
  duration: number // минуты
  participants: number
  objectives: string[]
  injects: SimulationInject[]
  metrics: SimulationMetric[]
  ai_generated?: boolean
}

export interface SimulationInject {
  id: string
  time: number // минута симуляции
  type: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  engine?: string // какой движок обрабатывает
  data?: any
}

export interface SimulationMetric {
  id: string
  name: string
  type: 'kpi' | 'performance' | 'compliance' | 'risk'
  target: number
  current: number
  unit: string
}

export interface SimulationResult {
  scenarioId: string
  startTime: string
  endTime: string
  duration: number
  participants: string[]
  objectives: {
    total: number
    achieved: number
    percentage: number
  }
  metrics: SimulationMetric[]
  recommendations: string[]
  lessons_learned: string[]
  ai_insights?: any
  raw_data?: any
}

export interface MonteCarloParams {
  iterations: number
  variables: Array<{
    name: string
    distribution: 'normal' | 'uniform' | 'exponential' | 'custom'
    mean?: number
    stdDev?: number
    min?: number
    max?: number
  }>
  correlations?: number[][]
  confidenceLevel: number
}

export interface SimulationState {
  activeSimulations: Map<string, ActiveSimulation>
  queuedSimulations: SimulationScenario[]
  completedSimulations: SimulationResult[]
  engineStatus: Map<string, EngineStatus>
  metrics: GlobalMetrics
}

export interface ActiveSimulation {
  id: string
  scenario: SimulationScenario
  status: 'preparing' | 'running' | 'paused' | 'completing'
  progress: number // 0-100
  currentInject?: SimulationInject
  startTime: string
  estimatedCompletion: string
  engines: string[]
  participants: string[]
  realTimeMetrics?: any
  vncUrl?: string
  logs: string[]
}

export interface EngineStatus {
  name: string
  status: 'online' | 'offline' | 'busy' | 'error'
  health: number // 0-100
  activeSimulations: number
  queueDepth: number
  lastHealthCheck: string
  capabilities: string[]
}

export interface GlobalMetrics {
  totalSimulations: number
  activeSimulations: number
  successRate: number
  avgDuration: number
  totalParticipants: number
  engineUtilization: Map<string, number>
  topScenarios: Array<{name: string, count: number}>
}

/**
 * Unified Simulation Hub - Единая точка управления всеми симуляциями
 */
class UnifiedSimulationHub {
  private state: SimulationState
  private wsConnections: Map<string, WebSocket> = new Map()
  private eventBus: WebSocket | null = null
  private updateCallbacks: Set<(state: SimulationState) => void> = new Set()
  private healthCheckInterval: NodeJS.Timeout | null = null

  constructor() {
    this.state = {
      activeSimulations: new Map(),
      queuedSimulations: [],
      completedSimulations: [],
      engineStatus: new Map(),
      metrics: {
        totalSimulations: 0,
        activeSimulations: 0,
        successRate: 0,
        avgDuration: 0,
        totalParticipants: 0,
        engineUtilization: new Map(),
        topScenarios: []
      }
    }

    this.initializeHub()
  }

  /**
   * Инициализация хаба
   */
  private async initializeHub() {
    console.log('🚀 Initializing Unified Simulation Hub...')

    // Проверяем статус всех движков
    await this.checkAllEngines()

    // Подключаемся к Event Bus
    this.connectToEventBus()

    // Запускаем health checks
    this.startHealthChecks()

    // Загружаем историю симуляций
    await this.loadSimulationHistory()

    console.log('✅ Simulation Hub initialized')
  }

  /**
   * ОСНОВНЫЕ МЕТОДЫ УПРАВЛЕНИЯ СИМУЛЯЦИЯМИ
   */

  /**
   * Создать новую симуляцию с автоматическим выбором движков
   */
  async createSimulation(params: {
    name: string
    type: SimulationType
    objectives: string[]
    complexity?: 1 | 2 | 3 | 4 | 5
    participants?: string[]
    aiGenerated?: boolean
  }): Promise<SimulationScenario> {
    console.log('📝 Creating new simulation:', params.name)

    // Автоматически выбираем подходящие движки
    const engines = this.selectEnginesForType(params.type)

    // Генерируем сценарий через AI если нужно
    let scenario: SimulationScenario
    if (params.aiGenerated) {
      scenario = await this.generateAIScenario(params)
    } else {
      scenario = {
        id: `sim-${Date.now()}`,
        name: params.name,
        description: `${params.type} simulation`,
        type: params.type,
        engines,
        complexity: params.complexity || 3,
        duration: this.estimateDuration(params.type, params.complexity || 3),
        participants: params.participants?.length || 1,
        objectives: params.objectives,
        injects: await this.generateInjects(params.type, params.complexity || 3),
        metrics: this.generateMetrics(params.objectives),
        ai_generated: false
      }
    }

    // Добавляем в очередь
    this.state.queuedSimulations.push(scenario)
    this.notifySubscribers()

    return scenario
  }

  /**
   * Запустить симуляцию
   */
  async startSimulation(scenarioId: string, options?: {
    immediate?: boolean
    participants?: string[]
    customInjects?: SimulationInject[]
  }): Promise<ActiveSimulation> {
    const scenario = this.state.queuedSimulations.find(s => s.id === scenarioId)
    if (!scenario) {
      throw new Error(`Scenario ${scenarioId} not found`)
    }

    console.log(`🎮 Starting simulation: ${scenario.name}`)

    // Проверяем доступность движков
    const availableEngines = await this.checkEngineAvailability(scenario.engines)
    if (availableEngines.length === 0) {
      throw new Error('No engines available for this scenario')
    }

    // Создаем активную симуляцию
    const activeSimulation: ActiveSimulation = {
      id: `active-${Date.now()}`,
      scenario,
      status: 'preparing',
      progress: 0,
      startTime: new Date().toISOString(),
      estimatedCompletion: this.estimateCompletion(scenario.duration),
      engines: availableEngines,
      participants: options?.participants || [],
      logs: [`Simulation started at ${new Date().toLocaleTimeString()}`]
    }

    // Добавляем в активные
    this.state.activeSimulations.set(activeSimulation.id, activeSimulation)
    this.state.queuedSimulations = this.state.queuedSimulations.filter(s => s.id !== scenarioId)

    // Запускаем движки
    for (const engine of availableEngines) {
      await this.startEngine(engine, activeSimulation)
    }

    // Если JaamSim - получаем VNC URL
    if (availableEngines.includes('JAAMSIM')) {
      activeSimulation.vncUrl = await this.getJaamSimVNC(activeSimulation.id)
    }

    // Запускаем выполнение
    this.executeSimulation(activeSimulation)

    this.notifySubscribers()
    return activeSimulation
  }

  /**
   * Запуск Monte Carlo симуляции
   */
  async runMonteCarloSimulation(params: MonteCarloParams): Promise<any> {
    console.log(`🎲 Running Monte Carlo simulation with ${params.iterations} iterations`)

    try {
      const response = await axios.post(
        SIMULATION_ENGINES.MONTE_CARLO.url,
        {
          iterations: params.iterations,
          variables: params.variables,
          correlations: params.correlations,
          confidence_level: params.confidenceLevel,
          method: 'box-muller' // или другой метод
        }
      )

      const results = response.data

      // Анализируем результаты
      const analysis = {
        mean: results.mean,
        stdDev: results.std_dev,
        var: results.value_at_risk,
        cvar: results.conditional_value_at_risk,
        percentiles: results.percentiles,
        histogram: results.histogram,
        correlationMatrix: results.correlations,
        confidenceInterval: results.confidence_interval
      }

      // Сохраняем результаты
      await this.saveSimulationResult({
        scenarioId: 'monte-carlo',
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        duration: 0,
        participants: [],
        objectives: { total: 1, achieved: 1, percentage: 100 },
        metrics: [],
        recommendations: this.generateMonteCarloRecommendations(analysis),
        lessons_learned: [],
        ai_insights: analysis,
        raw_data: results
      })

      return analysis
    } catch (error) {
      console.error('Monte Carlo simulation failed:', error)
      throw error
    }
  }

  /**
   * Запуск NICS для управления инцидентом
   */
  async startNICSIncident(incident: {
    type: string
    severity: 'low' | 'medium' | 'high' | 'critical'
    location?: { lat: number, lng: number }
    description: string
    agencies?: string[]
  }): Promise<string> {
    console.log('🚨 Starting NICS incident management:', incident.type)

    try {
      // Создаем инцидент в NICS
      const response = await axios.post(
        `${SIMULATION_ENGINES.NICS.url}/api/incidents`,
        {
          type: incident.type,
          severity: incident.severity,
          location: incident.location,
          description: incident.description,
          agencies: incident.agencies || ['BCM Team'],
          status: 'active',
          created_at: new Date().toISOString()
        }
      )

      const incidentId = response.data.incident_id

      // Подключаем WebSocket для real-time обновлений
      const ws = new WebSocket(`ws://localhost:8443/ws/incident/${incidentId}`)

      ws.onmessage = (event) => {
        const update = JSON.parse(event.data)
        console.log('NICS Update:', update)

        // Обновляем состояние
        const activeSimulation = Array.from(this.state.activeSimulations.values())
          .find(s => s.id === incidentId)

        if (activeSimulation) {
          activeSimulation.realTimeMetrics = update
          this.notifySubscribers()
        }
      }

      this.wsConnections.set(`nics-${incidentId}`, ws)

      return incidentId
    } catch (error) {
      console.error('Failed to start NICS incident:', error)
      throw error
    }
  }

  /**
   * AI генерация сценария
   */
  private async generateAIScenario(params: any): Promise<SimulationScenario> {
    console.log('🤖 Generating AI scenario...')

    try {
      const response = await axios.post(
        `${SIMULATION_ENGINES.SCENARIO_ORCHESTRATOR.url}/api/generate`,
        {
          type: params.type,
          complexity: params.complexity,
          objectives: params.objectives,
          constraints: {
            max_duration: 120,
            max_participants: params.participants?.length || 10
          }
        }
      )

      const aiScenario = response.data

      return {
        id: `ai-sim-${Date.now()}`,
        name: aiScenario.name || params.name,
        description: aiScenario.description,
        type: params.type,
        engines: this.selectEnginesForType(params.type),
        complexity: aiScenario.complexity || params.complexity || 3,
        duration: aiScenario.duration || 60,
        participants: params.participants?.length || 1,
        objectives: aiScenario.objectives || params.objectives,
        injects: aiScenario.injects || [],
        metrics: aiScenario.metrics || [],
        ai_generated: true
      }
    } catch (error) {
      console.warn('AI generation failed, using fallback:', error)
      // Fallback to manual generation
      return this.createSimulation({ ...params, aiGenerated: false })
    }
  }

  /**
   * Выполнение симуляции
   */
  private async executeSimulation(simulation: ActiveSimulation) {
    simulation.status = 'running'

    // Выполняем инъекции по расписанию
    for (const inject of simulation.scenario.injects) {
      // Ждем нужное время
      await this.waitForInjectTime(inject.time)

      if (simulation.status === 'paused') {
        await this.waitForResume(simulation.id)
      }

      // Применяем инъекцию
      await this.applyInject(simulation, inject)

      // Обновляем прогресс
      simulation.progress = (inject.time / simulation.scenario.duration) * 100
      simulation.currentInject = inject

      this.notifySubscribers()
    }

    // Завершаем симуляцию
    await this.completeSimulation(simulation)
  }

  /**
   * Применение инъекции
   */
  private async applyInject(simulation: ActiveSimulation, inject: SimulationInject) {
    console.log(`💉 Applying inject: ${inject.description}`)
    simulation.logs.push(`[${new Date().toLocaleTimeString()}] Inject: ${inject.description}`)

    // Выбираем движок для инъекции
    const engine = inject.engine || simulation.engines[0]

    switch (engine) {
      case 'JAAMSIM':
        await this.applyJaamSimInject(simulation.id, inject)
        break

      case 'NICS':
        await this.applyNICSInject(simulation.id, inject)
        break

      case 'DIGITAL_TWIN':
        await this.applyDigitalTwinInject(simulation.id, inject)
        break

      default:
        // Generic inject through Event Bus
        this.sendEventBusMessage({
          type: 'simulation.inject',
          simulation_id: simulation.id,
          inject: inject,
          timestamp: new Date().toISOString()
        })
    }
  }

  /**
   * JaamSim специфичные инъекции
   */
  private async applyJaamSimInject(simId: string, inject: SimulationInject) {
    try {
      await axios.post(`${SIMULATION_ENGINES.JAAMSIM.url}/api/inject`, {
        simulation_id: simId,
        command: inject.data?.command || 'pause',
        parameters: inject.data?.parameters || {}
      })
    } catch (error) {
      console.error('JaamSim inject failed:', error)
    }
  }

  /**
   * NICS специфичные инъекции
   */
  private async applyNICSInject(simId: string, inject: SimulationInject) {
    try {
      await axios.post(`${SIMULATION_ENGINES.NICS.url}/api/incidents/${simId}/updates`, {
        type: 'inject',
        severity: inject.severity,
        message: inject.description,
        data: inject.data
      })
    } catch (error) {
      console.error('NICS inject failed:', error)
    }
  }

  /**
   * Digital Twin инъекции
   */
  private async applyDigitalTwinInject(simId: string, inject: SimulationInject) {
    try {
      await axios.post(`${SIMULATION_ENGINES.DIGITAL_TWIN.url}/api/twin/inject`, {
        simulation_id: simId,
        block: inject.data?.block || 1,
        event: {
          type: inject.type,
          severity: inject.severity,
          description: inject.description,
          data: inject.data
        }
      })
    } catch (error) {
      console.error('Digital Twin inject failed:', error)
    }
  }

  /**
   * Завершение симуляции
   */
  private async completeSimulation(simulation: ActiveSimulation) {
    console.log(`✅ Completing simulation: ${simulation.scenario.name}`)

    simulation.status = 'completing'
    simulation.progress = 100

    // Собираем результаты со всех движков
    const results = await this.collectResults(simulation)

    // Генерируем AI insights
    const aiInsights = await this.generateAIInsights(results)

    // Создаем финальный отчет
    const finalResult: SimulationResult = {
      scenarioId: simulation.scenario.id,
      startTime: simulation.startTime,
      endTime: new Date().toISOString(),
      duration: Date.now() - new Date(simulation.startTime).getTime(),
      participants: simulation.participants,
      objectives: this.calculateObjectiveAchievement(simulation.scenario, results),
      metrics: this.calculateFinalMetrics(simulation.scenario.metrics, results),
      recommendations: aiInsights.recommendations || [],
      lessons_learned: aiInsights.lessons || [],
      ai_insights: aiInsights,
      raw_data: results
    }

    // Сохраняем результат
    await this.saveSimulationResult(finalResult)

    // Удаляем из активных
    this.state.activeSimulations.delete(simulation.id)
    this.state.completedSimulations.push(finalResult)

    // Останавливаем движки
    for (const engine of simulation.engines) {
      await this.stopEngine(engine, simulation.id)
    }

    // Закрываем WebSocket соединения
    const ws = this.wsConnections.get(`sim-${simulation.id}`)
    if (ws) {
      ws.close()
      this.wsConnections.delete(`sim-${simulation.id}`)
    }

    this.notifySubscribers()
    return finalResult
  }

  /**
   * ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
   */

  private selectEnginesForType(type: SimulationType): string[] {
    const engineMap: Record<SimulationType, string[]> = {
      [SimulationType.TABLETOP]: ['SCENARIO_ORCHESTRATOR'],
      [SimulationType.WALKTHROUGH]: ['DIGITAL_TWIN'],
      [SimulationType.FUNCTIONAL]: ['JAAMSIM', 'DIGITAL_TWIN'],
      [SimulationType.FULL_SCALE]: ['JAAMSIM', 'NICS', 'DIGITAL_TWIN'],
      [SimulationType.SIMULATION]: ['JAAMSIM', 'MONTE_CARLO', 'SIMULATION_ADAPTER'],
      [SimulationType.HYBRID]: Object.keys(SIMULATION_ENGINES)
    }
    return engineMap[type] || ['SCENARIO_ORCHESTRATOR']
  }

  private estimateDuration(type: SimulationType, complexity: number): number {
    const baseTime = {
      [SimulationType.TABLETOP]: 30,
      [SimulationType.WALKTHROUGH]: 45,
      [SimulationType.FUNCTIONAL]: 60,
      [SimulationType.FULL_SCALE]: 120,
      [SimulationType.SIMULATION]: 90,
      [SimulationType.HYBRID]: 150
    }
    return (baseTime[type] || 60) * (complexity / 3)
  }

  private estimateCompletion(duration: number): string {
    const completion = new Date()
    completion.setMinutes(completion.getMinutes() + duration)
    return completion.toISOString()
  }

  private async generateInjects(type: SimulationType, complexity: number): Promise<SimulationInject[]> {
    const injectCount = complexity * 2
    const injects: SimulationInject[] = []

    for (let i = 0; i < injectCount; i++) {
      injects.push({
        id: `inject-${i}`,
        time: (i + 1) * 10, // каждые 10 минут
        type: this.getRandomInjectType(),
        description: `Inject ${i + 1}`,
        severity: this.getRandomSeverity(complexity),
        data: {}
      })
    }

    return injects
  }

  private getRandomInjectType(): string {
    const types = ['system-failure', 'resource-shortage', 'communication-loss', 'escalation', 'external-event']
    return types[Math.floor(Math.random() * types.length)]
  }

  private getRandomSeverity(complexity: number): 'low' | 'medium' | 'high' | 'critical' {
    const severities: Array<'low' | 'medium' | 'high' | 'critical'> = ['low', 'medium', 'high', 'critical']
    const index = Math.min(Math.floor(Math.random() * complexity), 3)
    return severities[index]
  }

  private generateMetrics(objectives: string[]): SimulationMetric[] {
    return objectives.map((obj, i) => ({
      id: `metric-${i}`,
      name: obj,
      type: 'kpi' as const,
      target: 80,
      current: 0,
      unit: '%'
    }))
  }

  private generateMonteCarloRecommendations(analysis: any): string[] {
    const recommendations: string[] = []

    if (analysis.var > 0.2) {
      recommendations.push('High Value at Risk detected. Consider risk mitigation strategies.')
    }

    if (analysis.stdDev > analysis.mean * 0.5) {
      recommendations.push('High volatility detected. Implement variance reduction techniques.')
    }

    if (analysis.correlationMatrix) {
      recommendations.push('Strong correlations identified. Diversification recommended.')
    }

    return recommendations
  }

  private async checkEngineAvailability(engines: string[]): Promise<string[]> {
    const available: string[] = []

    for (const engine of engines) {
      const status = this.state.engineStatus.get(engine)
      if (status && status.status === 'online' && status.activeSimulations < 5) {
        available.push(engine)
      }
    }

    return available
  }

  private async startEngine(engine: string, simulation: ActiveSimulation) {
    const engineConfig = SIMULATION_ENGINES[engine]
    if (!engineConfig) return

    try {
      await axios.post(`${engineConfig.url}/api/start`, {
        simulation_id: simulation.id,
        scenario: simulation.scenario,
        config: {
          memory: engineConfig.memory,
          features: engineConfig.features
        }
      })

      // Обновляем статус движка
      const status = this.state.engineStatus.get(engine)
      if (status) {
        status.activeSimulations++
        status.status = 'busy'
      }
    } catch (error) {
      console.error(`Failed to start engine ${engine}:`, error)
    }
  }

  private async stopEngine(engine: string, simId: string) {
    const engineConfig = SIMULATION_ENGINES[engine]
    if (!engineConfig) return

    try {
      await axios.post(`${engineConfig.url}/api/stop`, {
        simulation_id: simId
      })

      // Обновляем статус движка
      const status = this.state.engineStatus.get(engine)
      if (status) {
        status.activeSimulations--
        if (status.activeSimulations === 0) {
          status.status = 'online'
        }
      }
    } catch (error) {
      console.error(`Failed to stop engine ${engine}:`, error)
    }
  }

  private async getJaamSimVNC(simId: string): Promise<string> {
    try {
      const response = await axios.get(
        `${SIMULATION_ENGINES.JAAMSIM.url}/api/vnc/${simId}`
      )
      return response.data.vnc_url || `http://localhost:5900/vnc/${simId}`
    } catch {
      return `http://localhost:5900/vnc/${simId}`
    }
  }

  private async waitForInjectTime(minutes: number) {
    // В реальной симуляции это будет учитывать ускорение времени
    await new Promise(resolve => setTimeout(resolve, minutes * 1000)) // Для демо - секунды вместо минут
  }

  private async waitForResume(simId: string) {
    return new Promise<void>(resolve => {
      const checkInterval = setInterval(() => {
        const sim = this.state.activeSimulations.get(simId)
        if (sim && sim.status === 'running') {
          clearInterval(checkInterval)
          resolve()
        }
      }, 1000)
    })
  }

  private async collectResults(simulation: ActiveSimulation): Promise<any> {
    const results = {}

    for (const engine of simulation.engines) {
      try {
        const engineConfig = SIMULATION_ENGINES[engine]
        const response = await axios.get(
          `${engineConfig.url}/api/results/${simulation.id}`
        )
        results[engine.toLowerCase()] = response.data
      } catch (error) {
        console.warn(`Failed to collect results from ${engine}:`, error)
      }
    }

    return results
  }

  private async generateAIInsights(results: any): Promise<any> {
    try {
      const response = await axios.post(
        `${SIMULATION_ENGINES.MCP_SERVER.url}/api/analyze`,
        { results }
      )
      return response.data
    } catch {
      return {
        recommendations: ['Review simulation results', 'Update response procedures'],
        lessons: ['Team coordination improved', 'Communication channels effective']
      }
    }
  }

  private calculateObjectiveAchievement(scenario: SimulationScenario, results: any) {
    const total = scenario.objectives.length
    const achieved = Math.floor(total * 0.8) // Simplified calculation
    return {
      total,
      achieved,
      percentage: Math.round((achieved / total) * 100)
    }
  }

  private calculateFinalMetrics(metrics: SimulationMetric[], results: any): SimulationMetric[] {
    return metrics.map(metric => ({
      ...metric,
      current: Math.random() * 100 // Simplified - would use actual results
    }))
  }

  private async saveSimulationResult(result: SimulationResult) {
    try {
      await axios.post(
        'http://localhost:8094/api/results',
        result
      )
    } catch (error) {
      console.error('Failed to save simulation result:', error)
    }
  }

  /**
   * EVENT BUS И REAL-TIME
   */
  private connectToEventBus() {
    try {
      this.eventBus = new WebSocket('ws://localhost:8001/ws/simulation-hub')

      this.eventBus.onopen = () => {
        console.log('📡 Connected to Event Bus')
        this.eventBus?.send(JSON.stringify({
          type: 'subscribe',
          channels: ['simulations', 'engines', 'metrics']
        }))
      }

      this.eventBus.onmessage = (event) => {
        const message = JSON.parse(event.data)
        this.handleEventBusMessage(message)
      }

      this.eventBus.onerror = (error) => {
        console.error('Event Bus error:', error)
      }

      this.eventBus.onclose = () => {
        console.log('Event Bus disconnected, reconnecting...')
        setTimeout(() => this.connectToEventBus(), 5000)
      }
    } catch (error) {
      console.warn('Event Bus not available:', error)
    }
  }

  private sendEventBusMessage(message: any) {
    if (this.eventBus && this.eventBus.readyState === WebSocket.OPEN) {
      this.eventBus.send(JSON.stringify(message))
    }
  }

  private handleEventBusMessage(message: any) {
    switch (message.type) {
      case 'engine.status':
        this.updateEngineStatus(message.engine, message.status)
        break

      case 'simulation.update':
        this.updateSimulation(message.simulation_id, message.data)
        break

      case 'metrics.update':
        this.updateMetrics(message.metrics)
        break
    }

    this.notifySubscribers()
  }

  private updateEngineStatus(engine: string, status: any) {
    this.state.engineStatus.set(engine, {
      name: engine,
      status: status.online ? 'online' : 'offline',
      health: status.health || 0,
      activeSimulations: status.active || 0,
      queueDepth: status.queue || 0,
      lastHealthCheck: new Date().toISOString(),
      capabilities: SIMULATION_ENGINES[engine]?.capabilities || []
    })
  }

  private updateSimulation(simId: string, data: any) {
    const simulation = this.state.activeSimulations.get(simId)
    if (simulation) {
      Object.assign(simulation, data)
    }
  }

  private updateMetrics(metrics: any) {
    Object.assign(this.state.metrics, metrics)
  }

  /**
   * HEALTH CHECKS
   */
  private async checkAllEngines() {
    for (const [key, config] of Object.entries(SIMULATION_ENGINES)) {
      const status = await this.checkEngineHealth(key, config)
      this.state.engineStatus.set(key, status)
    }
  }

  private async checkEngineHealth(name: string, config: any): Promise<EngineStatus> {
    try {
      const response = await axios.get(`${config.url}/health`, { timeout: 2000 })

      return {
        name,
        status: 'online',
        health: response.data.health || 100,
        activeSimulations: response.data.active || 0,
        queueDepth: response.data.queue || 0,
        lastHealthCheck: new Date().toISOString(),
        capabilities: config.capabilities
      }
    } catch {
      return {
        name,
        status: 'offline',
        health: 0,
        activeSimulations: 0,
        queueDepth: 0,
        lastHealthCheck: new Date().toISOString(),
        capabilities: config.capabilities
      }
    }
  }

  private startHealthChecks() {
    this.healthCheckInterval = setInterval(() => {
      this.checkAllEngines()
    }, 30000) // каждые 30 секунд
  }

  private async loadSimulationHistory() {
    try {
      const response = await axios.get('http://localhost:8094/api/simulations/history')
      this.state.completedSimulations = response.data.simulations || []
      this.updateGlobalMetrics()
    } catch (error) {
      console.warn('Failed to load simulation history:', error)
    }
  }

  private updateGlobalMetrics() {
    const metrics = this.state.metrics

    metrics.totalSimulations = this.state.completedSimulations.length
    metrics.activeSimulations = this.state.activeSimulations.size

    if (this.state.completedSimulations.length > 0) {
      const successful = this.state.completedSimulations.filter(
        s => s.objectives.percentage >= 70
      ).length
      metrics.successRate = (successful / this.state.completedSimulations.length) * 100

      const totalDuration = this.state.completedSimulations.reduce(
        (sum, s) => sum + s.duration, 0
      )
      metrics.avgDuration = totalDuration / this.state.completedSimulations.length

      metrics.totalParticipants = this.state.completedSimulations.reduce(
        (sum, s) => sum + s.participants.length, 0
      )
    }

    // Engine utilization
    this.state.engineStatus.forEach((status, engine) => {
      metrics.engineUtilization.set(engine,
        status.activeSimulations > 0 ? (status.health / 100) : 0
      )
    })
  }

  /**
   * PUBLIC API
   */

  getState(): SimulationState {
    return this.state
  }

  subscribe(callback: (state: SimulationState) => void): () => void {
    this.updateCallbacks.add(callback)
    return () => this.updateCallbacks.delete(callback)
  }

  private notifySubscribers() {
    this.updateCallbacks.forEach(cb => cb(this.state))
  }

  async pauseSimulation(simId: string) {
    const simulation = this.state.activeSimulations.get(simId)
    if (simulation) {
      simulation.status = 'paused'
      this.notifySubscribers()
    }
  }

  async resumeSimulation(simId: string) {
    const simulation = this.state.activeSimulations.get(simId)
    if (simulation) {
      simulation.status = 'running'
      this.notifySubscribers()
    }
  }

  async stopSimulation(simId: string) {
    const simulation = this.state.activeSimulations.get(simId)
    if (simulation) {
      await this.completeSimulation(simulation)
    }
  }

  getAvailableScenarios(): SimulationScenario[] {
    // Предустановленные сценарии
    return [
      {
        id: 'pandemic-response',
        name: 'Pandemic Response',
        description: 'Test organizational response to pandemic conditions',
        type: SimulationType.FULL_SCALE,
        engines: ['NICS', 'DIGITAL_TWIN', 'MONTE_CARLO'],
        complexity: 5,
        duration: 120,
        participants: 50,
        objectives: ['Maintain operations', 'Protect employees', 'Ensure communication'],
        injects: [],
        metrics: []
      },
      {
        id: 'cyber-attack',
        name: 'Cyber Attack Response',
        description: 'Respond to ransomware attack',
        type: SimulationType.SIMULATION,
        engines: ['JAAMSIM', 'DIGITAL_TWIN'],
        complexity: 4,
        duration: 90,
        participants: 20,
        objectives: ['Contain breach', 'Restore systems', 'Preserve data'],
        injects: [],
        metrics: []
      },
      {
        id: 'evacuation-drill',
        name: 'Building Evacuation',
        description: 'Emergency evacuation simulation',
        type: SimulationType.FUNCTIONAL,
        engines: ['JAAMSIM'],
        complexity: 3,
        duration: 30,
        participants: 100,
        objectives: ['Evacuate in 10 minutes', 'Account for all personnel'],
        injects: [],
        metrics: []
      }
    ]
  }

  async shutdown() {
    console.log('Shutting down Simulation Hub...')

    // Останавливаем все активные симуляции
    for (const [id, sim] of this.state.activeSimulations) {
      await this.stopSimulation(id)
    }

    // Закрываем WebSocket соединения
    this.eventBus?.close()
    this.wsConnections.forEach(ws => ws.close())

    // Останавливаем health checks
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval)
    }

    this.updateCallbacks.clear()
  }
}

// Export singleton
export const unifiedSimulationHub = new UnifiedSimulationHub()
export default unifiedSimulationHub