// Simulation Control Interface Types

export interface SimulationStatus {
  status: 'stopped' | 'running' | 'paused' | 'error'
  jaamsim_running: boolean
  vnc_available: boolean
  uptime: number
  simulation_id?: string
  started_at?: string
  elapsed_time?: number
}

export interface SimulationMetrics {
  processedEvents: number
  activeEntities: number
  queueLength: number
  utilization: number
  responseTime?: number
  throughput?: number
  timestamp: string
}

export interface ExercisePhase {
  id: string
  name: string
  description: string
  status: 'pending' | 'active' | 'completed'
  startTime?: string
  completedAt?: string
  duration?: number
  progress?: number
  requirements?: string[]
  outputs?: string[]
}

export interface ParticipantActivity {
  id: string
  user_id: string
  user_name: string
  action: string
  timestamp: string
  exercise_phase?: string
  details?: Record<string, any>
  result?: 'success' | 'warning' | 'error'
}

export interface NICSRole {
  code: string
  name: string
  level: number
  assignee?: string
  responsibilities?: string[]
  authority_level?: number
}

export interface NICSIntegration {
  enabled: boolean
  platform_url?: string
  incident_id?: string
  roles: NICSRole[]
  command_structure?: {
    incident_commander?: string
    operations_chief?: string
    planning_chief?: string
    logistics_chief?: string
    finance_admin_chief?: string
  }
}

export interface ExerciseData {
  id: string
  name: string
  description: string
  type: string
  status: 'planning' | 'preparing' | 'running' | 'paused' | 'completed' | 'cancelled'
  created_at: string
  started_at?: string
  completed_at?: string
  duration?: number
  participants_count: number
  simulation_engine: string
  ai_generated?: boolean
  nics_enabled?: boolean
  learning_objectives?: string[]
  success_criteria?: string[]
}

export interface Participant {
  id: string
  user_id: string
  name: string
  email: string
  role: string
  status: 'active' | 'idle' | 'disconnected'
  current_action?: string
  actions_completed?: number
  score?: number
  avg_response_time?: number
  session_duration?: number
  joined_at: string
  last_activity?: string
  performance_metrics?: {
    decisions_made: number
    correct_decisions: number
    communication_score: number
    leadership_score: number
  }
}

export interface SimulationResults {
  exercise_id: string
  summary: {
    totalEvents: number
    totalDuration: number
    completionRate: number
    efficiency: number
    participantsCount: number
    successfulObjectives: number
    totalObjectives: number
  }
  metrics: SimulationMetrics[]
  phaseBreakdown: Array<{
    name: string
    duration: number
    performance: number
    events: number
    objectives_met: number
    participants_active: number
  }>
  participantResults: Array<{
    participant_id: string
    completion_rate: number
    score: number
    performance_rating: string
    strengths: string[]
    improvement_areas: string[]
  }>
  learningOutcomes: Array<{
    objective: string
    achievement_rate: number
    assessment: string
    evidence: string[]
  }>
  recommendations: Array<{
    category: string
    priority: 'low' | 'medium' | 'high'
    title: string
    description: string
    implementation_effort: string
  }>
  raw: Record<string, any>
}

export interface SystemService {
  name: string
  endpoint: string
  status: 'healthy' | 'degraded' | 'unhealthy'
  uptime: number
  response_time?: number
  last_check?: string
  error_details?: string
}

export interface VNCConfiguration {
  host: string
  port: number
  quality: 'low' | 'medium' | 'high'
  compression_level: number
  color_depth: number
  cursor_enabled: boolean
  clipboard_enabled: boolean
}

export interface JaamSimConfiguration {
  model_file: string
  run_time: number
  real_time_factor: number
  output_interval: number
  graphics_enabled: boolean
  batch_mode: boolean
  log_level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  custom_parameters: Record<string, any>
}

export interface SimulationConfiguration {
  exercise_id: string
  jaamsim: JaamSimConfiguration
  vnc: VNCConfiguration
  monitoring: {
    enable_websocket: boolean
    metrics_interval: number
    log_participant_actions: boolean
    record_session: boolean
  }
  nics: {
    enabled: boolean
    platform_url?: string
    auto_assign_roles: boolean
  }
}

export interface ExerciseTemplate {
  id: string
  name: string
  description: string
  category: string
  difficulty_level: 1 | 2 | 3 | 4 | 5
  estimated_duration: number
  participant_roles: string[]
  learning_objectives: string[]
  scenario_description: string
  jaamsim_model: string
  configuration: Partial<SimulationConfiguration>
  prerequisites?: string[]
  resources_required?: string[]
}

export interface ActivityFeedItem {
  id: string
  type: 'exercise_started' | 'exercise_completed' | 'exercise_paused' | 'exercise_error' | 'participant_joined' | 'phase_completed' | 'objective_met'
  message: string
  timestamp: string
  exercise_id?: string
  participant_id?: string
  severity?: 'info' | 'warning' | 'error' | 'success'
  metadata?: Record<string, any>
}

export interface LearningObjective {
  id: string
  title: string
  description: string
  category: string
  target_achievement: number
  assessment_criteria: string[]
  weight: number
}

export interface PerformanceKPI {
  id: string
  name: string
  description: string
  unit: string
  target_value: number
  current_value: number
  trend: 'up' | 'down' | 'stable'
  status: 'excellent' | 'good' | 'fair' | 'poor'
}

export interface WebSocketMessage {
  type: 'metrics_update' | 'phase_update' | 'participant_activity' | 'simulation_completed' | 'system_alert'
  timestamp: string
  exercise_id: string
  data: any
}

export interface SimulationSettings {
  refreshInterval: number
  showNotifications: boolean
  vncQuality: 'low' | 'medium' | 'high'
  logLevel: 'debug' | 'info' | 'warn' | 'error'
  trackActions: boolean
  recordSession: boolean
  autoSaveInterval: number
  enableAnalytics: boolean
}

export interface ExerciseStatistics {
  totalExercises: number
  thisMonth: number
  thisWeek: number
  successRate: number
  avgDuration: string
  totalParticipants: number
  mostUsedScenarios: Array<{
    name: string
    count: number
  }>
  performanceTrends: Array<{
    date: string
    success_rate: number
    avg_score: number
    participation_rate: number
  }>
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  timestamp: string
}

export interface SimulationApiResponse extends ApiResponse {
  simulation_id?: string
  jaamsim_pid?: number
  vnc_url?: string
}

export interface HealthCheckResponse {
  service: string
  status: 'healthy' | 'degraded' | 'unhealthy'
  uptime: number
  response_time: number
  details?: Record<string, any>
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string | Date
  value: number
  label?: string
  metadata?: Record<string, any>
}

export interface MetricsChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    borderColor: string
    backgroundColor: string
    fill?: boolean
    tension?: number
  }>
}

export interface UtilizationChartData {
  timestamp: string | Date
  cpu?: number
  memory?: number
  network?: number
  storage?: number
  overall?: number
}

export interface ResponseTimeChartData {
  timestamp: string | Date
  responseTime: number
  endpoint?: string
  operation?: string
  status?: 'success' | 'warning' | 'error'
}

// Event Types
export interface SimulationEvent {
  id: string
  type: string
  timestamp: string
  exercise_id: string
  participant_id?: string
  phase_id?: string
  data: Record<string, any>
  severity: 'low' | 'medium' | 'high'
  processed: boolean
}

export interface ExerciseAchievement {
  id: string
  title: string
  description: string
  status: 'completed' | 'partial' | 'missed'
  progress: number
  points: number
  category: string
  requirements?: string[]
}

export interface TeamPerformanceMetrics {
  communication: number
  collaboration: number
  decisionMaking: number
  leadership: number
  problemSolving: number
  adaptability: number
}

export interface SkillDevelopmentArea {
  name: string
  level: 1 | 2 | 3 | 4 | 5
  feedback: string
  improvement_suggestions?: string[]
  related_training?: string[]
}

// Export all types for easy importing
export type {
  // Re-export commonly used types
  SimulationStatus as Status,
  SimulationMetrics as Metrics,
  ExerciseData as Exercise,
  Participant as ExerciseParticipant,
  SimulationResults as Results
}