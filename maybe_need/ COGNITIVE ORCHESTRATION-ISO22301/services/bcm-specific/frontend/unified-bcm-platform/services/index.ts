/**
 * Unified Services Export
 * Central export point for all extracted and integrated services
 */

// Simulation services - Block 3 of Digital Twin (JaamSim integration)
export { simulationService } from './simulation/simulationService'
export type {
  SimulationStatus,
  SimulationMetrics,
  ExercisePhase,
  ParticipantActivity,
  NICSIntegration,
  SimulationResults,
  ExerciseData,
  SystemService,
  SimulationConfiguration
} from './simulation/types'

// Analytics services - Learning and performance monitoring
export { analyticsService } from './analytics/analyticsService'
export type {
  DashboardMetrics,
  TopScenario,
  AIRecommendation,
  ChartData,
  AnalyticsDashboard
} from './analytics/analyticsService'

// BCM Core services - Platform integration
export { bcmService } from './bcm/bcmService'
export type {
  BCMMetrics,
  ActivityItem,
  SystemHealth,
  AIOrganStatus
} from './bcm/bcmService'

// Digital Twin API services (existing)
export { digitalTwinApi } from './digital-twin/api'
export type {
  PersonalTwin,
  OrganizationTwin,
  TwinMetrics,
  ContextData,
  RiskData
} from './digital-twin/api'

// Consolidated exports for common use cases
export const services = {
  simulation: simulationService,
  analytics: analyticsService,
  bcm: bcmService,
  digitalTwin: digitalTwinApi
} as const

// Service health check utility
export async function checkAllServicesHealth() {
  const healthChecks = await Promise.allSettled([
    simulationService.checkServiceHealth(),
    bcmService.getSystemHealth(),
    analyticsService.getDashboardData().then(() => ({ status: 'healthy' })).catch(() => ({ status: 'unhealthy' }))
  ])

  return {
    simulation: healthChecks[0].status === 'fulfilled' ? 'healthy' : 'unhealthy',
    bcm: healthChecks[1].status === 'fulfilled' ? 'healthy' : 'unhealthy',
    analytics: healthChecks[2].status === 'fulfilled' ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString()
  }
}