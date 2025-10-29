// Simulation Components Export Index

// Main Components
export { default as SimulationControlPanel } from './SimulationControlPanel.vue'
export { default as ExerciseMonitor } from './ExerciseMonitor.vue'
export { default as SimulationSummaryChart } from './SimulationSummaryChart.vue'
export { default as SimulationMetricsTable } from './SimulationMetricsTable.vue'

// Chart Components
export { default as MetricsChart } from './charts/MetricsChart.vue'
export { default as UtilizationChart } from './charts/UtilizationChart.vue'
export { default as ResponseTimeChart } from './charts/ResponseTimeChart.vue'

// Services
export { simulationService } from '@/services/simulationService'

// Types
export type {
  SimulationStatus,
  SimulationMetrics,
  ExercisePhase,
  ParticipantActivity,
  NICSIntegration,
  SimulationResults,
  ExerciseData,
  Participant,
  SystemService,
  WebSocketMessage,
  SimulationConfiguration,
  VNCConfiguration,
  JaamSimConfiguration
} from '@/types/simulation'

// Re-export commonly used types with shorter names
export type {
  SimulationStatus as Status,
  SimulationMetrics as Metrics,
  ExerciseData as Exercise,
  Participant as ExerciseParticipant,
  SimulationResults as Results
} from '@/types/simulation'