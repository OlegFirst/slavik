import axios from 'axios'
import type {
  SimulationMetrics,
  ExercisePhase,
  ParticipantActivity,
  NICSIntegration,
  SimulationResults,
  SimulationStatus,
  ExerciseData,
  SystemService,
  ApiResponse,
  SimulationApiResponse,
  HealthCheckResponse,
  WebSocketMessage,
  SimulationConfiguration
} from '@/types/simulation'

// API Base URLs for different services
const EXERCISE_SIMULATORS_BRIDGE_URL = 'http://localhost:8094'
const SIMULATION_ADAPTER_URL = 'http://localhost:8012'
const JAAMSIM_ENGINE_URL = 'http://localhost:5900'

class SimulationService {
  private api = axios.create({
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  constructor() {
    // Add request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Simulation API Error:', error)

        if (error.response?.status === 401) {
          // Handle authentication error
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }

        return Promise.reject(error)
      }
    )
  }

  // Exercise Management
  async getExerciseDetails(exerciseId: string): Promise<ExerciseData> {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/exercises/${exerciseId}`
      )
      return response.data
    } catch (error) {
      throw new Error(`Failed to get exercise details: ${error.message}`)
    }
  }

  async getExercisePhases(exerciseId: string): Promise<ExercisePhase[]> {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/exercises/${exerciseId}/phases`
      )
      return response.data.phases || []
    } catch (error) {
      console.error('Error fetching exercise phases:', error)
      return []
    }
  }

  async getRecentActivity(exerciseId: string): Promise<ParticipantActivity[]> {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/exercises/${exerciseId}/activity`,
        { params: { limit: 10 } }
      )
      return response.data.activities || []
    } catch (error) {
      console.error('Error fetching recent activity:', error)
      return []
    }
  }

  // Simulation Control
  async startSimulation(exerciseId: string): Promise<SimulationApiResponse> {
    try {
      const response = await this.api.post(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/simulations/${exerciseId}/start`,
        {
          jaamsim_config: {
            vnc_port: 5900,
            enable_graphics: true,
            real_time_factor: 1.0
          },
          monitoring: {
            enable_websocket: true,
            metrics_interval: 5000
          }
        }
      )

      return {
        success: response.data.success,
        simulation_id: response.data.simulation_id,
        jaamsim_pid: response.data.jaamsim_pid,
        vnc_url: response.data.vnc_url,
        message: response.data.message,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(`Failed to start simulation: ${error.message}`)
    }
  }

  async pauseSimulation(exerciseId: string): Promise<ApiResponse> {
    try {
      const response = await this.api.post(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/simulations/${exerciseId}/pause`
      )
      return {
        success: response.data.success,
        message: response.data.message,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(`Failed to pause simulation: ${error.message}`)
    }
  }

  async stopSimulation(exerciseId: string): Promise<ApiResponse> {
    try {
      const response = await this.api.post(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/simulations/${exerciseId}/stop`
      )
      return {
        success: response.data.success,
        message: response.data.message,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(`Failed to stop simulation: ${error.message}`)
    }
  }

  async getSimulationStatus(exerciseId: string): Promise<SimulationStatus> {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/simulations/${exerciseId}/status`
      )
      return {
        status: response.data.status,
        jaamsim_running: response.data.jaamsim_running,
        vnc_available: response.data.vnc_available,
        uptime: response.data.uptime,
        simulation_id: response.data.simulation_id,
        started_at: response.data.started_at,
        elapsed_time: response.data.elapsed_time
      }
    } catch (error) {
      throw new Error(`Failed to get simulation status: ${error.message}`)
    }
  }

  // JaamSim Integration
  async getJaamSimMetrics(exerciseId: string): Promise<SimulationMetrics> {
    try {
      const response = await this.api.get(
        `${SIMULATION_ADAPTER_URL}/api/jaamsim/${exerciseId}/metrics`
      )
      return response.data.metrics
    } catch (error) {
      console.error('Error fetching JaamSim metrics:', error)
      return {
        processedEvents: 0,
        activeEntities: 0,
        queueLength: 0,
        utilization: 0,
        timestamp: new Date().toISOString()
      }
    }
  }

  async sendJaamSimCommand(exerciseId: string, command: string, params: Record<string, any> = {}) {
    try {
      const response = await this.api.post(
        `${SIMULATION_ADAPTER_URL}/api/jaamsim/${exerciseId}/command`,
        { command, params }
      )
      return response.data
    } catch (error) {
      throw new Error(`Failed to send JaamSim command: ${error.message}`)
    }
  }

  async getJaamSimConfiguration(exerciseId: string) {
    try {
      const response = await this.api.get(
        `${SIMULATION_ADAPTER_URL}/api/jaamsim/${exerciseId}/config`
      )
      return response.data.config
    } catch (error) {
      throw new Error(`Failed to get JaamSim configuration: ${error.message}`)
    }
  }

  // NICS Integration
  async getNICSIntegration(exerciseId: string): Promise<NICSIntegration> {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/exercises/${exerciseId}/nics`
      )
      return {
        enabled: response.data.nics_enabled || false,
        roles: response.data.command_structure || []
      }
    } catch (error) {
      console.error('Error fetching NICS integration:', error)
      return {
        enabled: false,
        roles: []
      }
    }
  }

  async updateNICSRoleAssignment(exerciseId: string, roleCode: string, userId: string) {
    try {
      const response = await this.api.put(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/exercises/${exerciseId}/nics/roles/${roleCode}`,
        { user_id: userId }
      )
      return response.data
    } catch (error) {
      throw new Error(`Failed to update NICS role assignment: ${error.message}`)
    }
  }

  // Results and Analytics
  async getSimulationResults(exerciseId: string): Promise<SimulationResults | null> {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/simulations/${exerciseId}/results`
      )
      return response.data.results
    } catch (error) {
      console.error('Error fetching simulation results:', error)
      return null
    }
  }

  async exportResultsToCSV(results: SimulationResults): Promise<string> {
    try {
      const headers = ['Timestamp', 'Processed Events', 'Active Entities', 'Queue Length', 'Utilization']
      const rows = results.metrics.map(metric => [
        metric.timestamp,
        metric.processedEvents,
        metric.activeEntities,
        metric.queueLength,
        metric.utilization
      ])

      return [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n')
    } catch (error) {
      throw new Error(`Failed to export results to CSV: ${error.message}`)
    }
  }

  // Learning and Experience
  async saveExerciseExperience(exerciseId: string, experienceData: Record<string, any>) {
    try {
      const response = await this.api.post(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/exercises/${exerciseId}/experience`,
        {
          simulation_results: experienceData.results,
          participant_feedback: experienceData.feedback,
          lessons_learned: experienceData.lessons,
          improvement_suggestions: experienceData.improvements,
          timestamp: new Date().toISOString()
        }
      )
      return response.data
    } catch (error) {
      throw new Error(`Failed to save exercise experience: ${error.message}`)
    }
  }

  async getHistoricalPerformance(exerciseType: string, limit: number = 10) {
    try {
      const response = await this.api.get(
        `${EXERCISE_SIMULATORS_BRIDGE_URL}/api/analytics/performance`,
        { params: { exercise_type: exerciseType, limit } }
      )
      return response.data.performance_data
    } catch (error) {
      console.error('Error fetching historical performance:', error)
      return []
    }
  }

  // WebSocket Connection Management
  createWebSocketConnection(exerciseId: string, onMessage: (data: any) => void): WebSocket {
    const ws = new WebSocket(`ws://localhost:8094/ws/simulation/${exerciseId}`)

    ws.onopen = () => {
      console.log(`WebSocket connected for exercise ${exerciseId}`)
      // Send initial subscription message
      ws.send(JSON.stringify({
        type: 'subscribe',
        exercise_id: exerciseId,
        events: ['metrics_update', 'phase_update', 'participant_activity']
      }))
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
    }

    return ws
  }

  // Utility Methods
  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }

  calculateEfficiency(metrics: SimulationMetrics[]): number {
    if (metrics.length === 0) return 0

    const totalUtilization = metrics.reduce((sum, metric) => sum + metric.utilization, 0)
    return Math.round(totalUtilization / metrics.length)
  }

  // Health Check
  async checkServiceHealth(): Promise<SystemService[]> {
    const services = [
      { name: 'Exercise Simulators Bridge', url: `${EXERCISE_SIMULATORS_BRIDGE_URL}/health`, endpoint: ':8094' },
      { name: 'Simulation Adapter', url: `${SIMULATION_ADAPTER_URL}/health`, endpoint: ':8012' },
      { name: 'JaamSim Engine', url: `${JAAMSIM_ENGINE_URL}/health`, endpoint: ':5900' }
    ]

    const healthChecks = await Promise.allSettled(
      services.map(async (service) => {
        const startTime = Date.now()
        try {
          const response = await this.api.get(service.url, { timeout: 5000 })
          const responseTime = Date.now() - startTime

          return {
            name: service.name,
            endpoint: service.endpoint,
            status: 'healthy' as const,
            uptime: response.data.uptime || 99.5,
            response_time: responseTime,
            last_check: new Date().toISOString()
          }
        } catch (error) {
          const responseTime = Date.now() - startTime

          return {
            name: service.name,
            endpoint: service.endpoint,
            status: 'unhealthy' as const,
            uptime: 0,
            response_time: responseTime,
            last_check: new Date().toISOString(),
            error_details: error.message
          }
        }
      })
    )

    return healthChecks.map((result) =>
      (result as any).value || {
        name: 'Unknown Service',
        endpoint: '',
        status: 'unhealthy' as const,
        uptime: 0,
        error_details: (result as any).reason
      }
    )
  }
}

// Export singleton instance
export const simulationService = new SimulationService()
export default simulationService