/**
 * 7 User Journeys Type Definitions
 * Based on AI-Platform-ISO architecture
 */

// ============================================================================
// JOURNEY TYPES
// ============================================================================

export type JourneyType =
  | 'certification'  // Journey 1, 4, 7: Get ISO certified
  | 'auditor'        // Journey 2: Auditor tools & marketplace
  | 'academy'        // Journey 3: Learning & community
  | 'twin'           // Journey 5: Digital twin & simulation
  | 'crisis'         // Journey 6: Crisis recovery

export interface Journey {
  id: JourneyType
  title: string
  description: string
  icon: string
  color: string
  cta: string
  features: string[]
}

// ============================================================================
// USER & ORGANIZATION
// ============================================================================

export type UserRole =
  | 'platform_admin'
  | 'org_admin'
  | 'bcm_manager'
  | 'auditor'
  | 'learner'
  | 'viewer'

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  role: UserRole
  organization_id?: string
  created_at: Date
  last_login?: Date
}

export interface Organization {
  id: string
  name: string
  industry: string
  size: 'small' | 'medium' | 'large' | 'enterprise'
  subscription_tier: 'starter' | 'professional' | 'enterprise'
  created_at: Date
}

// ============================================================================
// JOURNEY 1: CERTIFICATION
// ============================================================================

export interface GapAnalysisAnswers {
  [clauseId: string]: {
    compliance: 'yes' | 'partial' | 'no'
    evidence: string
    documents?: string[]
  }
}

export interface GapAnalysisResult {
  id: string
  organization_id: string
  standard: 'ISO_22301' | 'ISO_27001' | 'NIST'
  overall_score: number // 0-100
  compliance_percentage: number
  identified_gaps: Gap[]
  recommendations: Recommendation[]
  timeline_weeks: number
  estimated_cost: number
  created_at: Date
}

export interface Gap {
  clause_id: string
  clause_title: string
  severity: 'critical' | 'major' | 'minor'
  description: string
  current_state: string
  required_state: string
  gap_size: number // 0-100
}

export interface Recommendation {
  id: string
  gap_id: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  estimated_effort_hours: number
  estimated_cost: number
  order: number
}

export interface CertificationRoadmap {
  id: string
  analysis_id: string
  organization_id: string
  current_score: number
  target_score: number
  timeline_weeks: number
  estimated_cost: number
  critical_gaps_count: number
  phases: RoadmapPhase[]
  created_at: Date
}

export interface RoadmapPhase {
  id: string
  title: string
  description: string
  duration_weeks: number
  order: number
  status: 'pending' | 'in_progress' | 'completed'
  tasks: RoadmapTask[]
  milestones: Milestone[]
}

export interface RoadmapTask {
  id: string
  title: string
  description: string
  assigned_to?: string
  due_date?: Date
  status: 'todo' | 'in_progress' | 'done'
  priority: 'high' | 'medium' | 'low'
}

export interface Milestone {
  id: string
  title: string
  description: string
  target_date: Date
  achieved: boolean
}

export interface DocumentTemplate {
  id: string
  title: string
  category: 'policy' | 'procedure' | 'plan' | 'report' | 'template'
  iso_clause?: string
  ai_generation: boolean
  estimated_time: string
  description: string
  questions?: AIQuestion[]
}

export interface AIQuestion {
  id: string
  question: string
  type: 'text' | 'select' | 'multiselect' | 'number'
  options?: string[]
  required: boolean
  help_text?: string
}

export interface ReadinessStatus {
  overall_score: number
  documentation: SectionStatus
  processes: SectionStatus
  training: SectionStatus
  exercises: SectionStatus
  reviews: SectionStatus
  last_updated: Date
}

export interface SectionStatus {
  completeness: number // 0-100
  missing_items: string[]
  completed_items: string[]
  alerts: Alert[]
}

export interface Alert {
  severity: 'critical' | 'warning' | 'info'
  title: string
  description: string
  action_required?: string
}

// ============================================================================
// JOURNEY 2: AUDITOR
// ============================================================================

export interface AuditorProfile {
  id: string
  user_id: string
  name: string
  avatar?: string
  bio: string
  certifications: string[]
  experience_years: number
  industry_experience: string[]
  rating: number // 1-5
  reviews_count: number
  completed_audits: number
  pricing: AuditorPricing
  availability: AuditorAvailability
  services_offered: AuditorService[]
  portfolio: PortfolioItem[]
  created_at: Date
}

export interface AuditorPricing {
  consultation: number // $/hour
  document_review: number // $/package
  training: number // $/person
  certification_audit: number // flat fee
}

export interface AuditorAvailability {
  timezone: string
  available_hours: WeeklyHours
  booked_slots: BookedSlot[]
}

export interface WeeklyHours {
  monday: TimeSlot[]
  tuesday: TimeSlot[]
  wednesday: TimeSlot[]
  thursday: TimeSlot[]
  friday: TimeSlot[]
  saturday: TimeSlot[]
  sunday: TimeSlot[]
}

export interface TimeSlot {
  start: string // HH:MM
  end: string // HH:MM
}

export interface BookedSlot {
  start: Date
  end: Date
  client_id: string
  service_type: AuditorService
}

export type AuditorService =
  | 'consultation'
  | 'gap_analysis'
  | 'document_review'
  | 'training'
  | 'certification_audit'
  | 'continuous_improvement'

export interface PortfolioItem {
  id: string
  title: string
  description: string
  industry: string
  certification: string
  year: number
  testimonial?: string
}

export interface ClientWorkPackage {
  id: string
  client_id: string
  organization_id: string
  auditor_id: string
  status: 'in_progress' | 'review' | 'completed'
  contents: WorkPackageContent[]
  audit_trail: AuditTrailEntry[]
  created_at: Date
  updated_at: Date
}

export interface WorkPackageContent {
  type: 'document' | 'bia' | 'risk_register' | 'exercise' | 'training_record'
  item_id: string
  title: string
  version: string
  last_modified: Date
  status: 'draft' | 'review' | 'approved'
}

export interface AuditTrailEntry {
  timestamp: Date
  user_id: string
  action: string
  item_id: string
  changes: Record<string, unknown>
}

// ============================================================================
// JOURNEY 3: ACADEMY & LEARNING
// ============================================================================

export interface Course {
  id: string
  title: string
  description: string
  category: 'iso_22301' | 'bia' | 'risk' | 'incident' | 'general'
  level: 'beginner' | 'intermediate' | 'advanced'
  duration_hours: number
  format: 'self_paced' | 'instructor_led' | 'blended'
  certification: boolean
  auditor_approved: boolean
  price: number
  modules: CourseModule[]
  instructor?: Instructor
  rating: number
  enrolled_count: number
  completion_rate: number
  created_at: Date
}

export interface CourseModule {
  id: string
  title: string
  order: number
  duration_minutes: number
  content_type: 'video' | 'text' | 'quiz' | 'exercise' | 'case_study'
  content_url?: string
  is_completed?: boolean
}

export interface Instructor {
  id: string
  name: string
  avatar?: string
  bio: string
  certifications: string[]
  courses_taught: number
  rating: number
}

export interface CaseStudy {
  id: string
  title: string
  industry: string
  incident_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  timeline: CaseStudyEvent[]
  outcomes: string[]
  lessons_learned: string[]
  discussion_points: string[]
  is_anonymized: boolean
  created_at: Date
}

export interface CaseStudyEvent {
  timestamp: string
  event: string
  impact: string
}

export interface LearningProgress {
  user_id: string
  courses_enrolled: string[]
  courses_completed: string[]
  total_hours: number
  certificates_earned: Certificate[]
  current_streak_days: number
  gamification: GamificationStats
}

export interface Certificate {
  id: string
  course_id: string
  course_title: string
  issued_date: Date
  expires_date?: Date
  certificate_url: string
  auditor_signed: boolean
  auditor_id?: string
}

export interface GamificationStats {
  total_points: number
  level: number
  badges: Badge[]
  achievements: Achievement[]
  leaderboard_rank: number
}

export interface Badge {
  id: string
  name: string
  description: string
  icon_url: string
  earned_date: Date
}

export interface Achievement {
  id: string
  name: string
  description: string
  progress: number // 0-100
  target: number
  current: number
  unlocked: boolean
}

// ============================================================================
// JOURNEY 5: DIGITAL TWIN
// ============================================================================

export interface DigitalTwin {
  id: string
  organization_id: string
  name: string
  description: string
  created_at: Date
  last_updated: Date
  components: TwinComponent[]
  metadata: TwinMetadata
}

export interface TwinComponent {
  id: string
  type: 'department' | 'process' | 'resource' | 'system' | 'vendor'
  name: string
  criticality: 'low' | 'medium' | 'high' | 'critical'
  dependencies: string[] // IDs of other components
  attributes: Record<string, unknown>
  position?: { x: number; y: number; z: number }
}

export interface TwinMetadata {
  total_employees: number
  annual_revenue: number
  critical_processes: number
  it_systems: number
  key_vendors: number
  last_sync: Date
}

export interface Scenario {
  id: string
  name: string
  category: 'cyber' | 'natural_disaster' | 'pandemic' | 'supply_chain' | 'financial' | 'custom'
  description: string
  severity: 'minor' | 'moderate' | 'major' | 'catastrophic'
  initial_conditions: ScenarioCondition[]
  parameters: ScenarioParameter[]
  is_template: boolean
  created_by: string
  created_at: Date
}

export interface ScenarioCondition {
  component_id: string
  impact_type: 'unavailable' | 'degraded' | 'delayed' | 'compromised'
  impact_percentage: number
  duration_hours: number
}

export interface ScenarioParameter {
  name: string
  type: 'number' | 'percentage' | 'duration'
  value: number
  unit?: string
}

export interface SimulationResult {
  id: string
  scenario_id: string
  twin_id: string
  executed_at: Date
  duration_seconds: number
  impact_analysis: ImpactAnalysis
  recommendations: SimulationRecommendation[]
  timeline: SimulationEvent[]
}

export interface ImpactAnalysis {
  financial_loss: {
    min: number
    max: number
    most_likely: number
    currency: string
  }
  rto: number // hours
  rpo: number // hours
  affected_components: string[]
  cascading_effects: CascadingEffect[]
  confidence: number // 0-100
}

export interface CascadingEffect {
  from_component: string
  to_component: string
  delay_hours: number
  impact_percentage: number
}

export interface SimulationRecommendation {
  priority: 'critical' | 'high' | 'medium' | 'low'
  category: 'prevention' | 'detection' | 'response' | 'recovery'
  title: string
  description: string
  estimated_cost: number
  risk_reduction_percentage: number
  roi: number
}

export interface SimulationEvent {
  timestamp: number // seconds from start
  event_type: 'impact' | 'cascading' | 'recovery_action' | 'milestone'
  component_id: string
  description: string
  severity: 'info' | 'warning' | 'critical'
}

// ============================================================================
// JOURNEY 6: CRISIS MANAGEMENT
// ============================================================================

export interface Incident {
  id: string
  organization_id: string
  type: 'cyber_attack' | 'natural_disaster' | 'pandemic' | 'system_failure' | 'other'
  severity: 'minor' | 'moderate' | 'major' | 'catastrophic'
  status: 'active' | 'contained' | 'recovering' | 'resolved'
  title: string
  description: string
  activated_at: Date
  resolved_at?: Date
  crisis_team: CrisisTeamMember[]
  timeline: IncidentEvent[]
  recovery_plan?: RecoveryPlan
}

export interface CrisisTeamMember {
  user_id: string
  name: string
  role: 'incident_commander' | 'technical_lead' | 'communications' | 'logistics' | 'liaison'
  status: 'active' | 'standby' | 'unavailable'
  contact: string
}

export interface IncidentEvent {
  id: string
  timestamp: Date
  event_type: 'initial_impact' | 'escalation' | 'action_taken' | 'communication' | 'milestone'
  description: string
  reported_by: string
  severity: 'info' | 'warning' | 'critical'
  actions: Action[]
}

export interface Action {
  id: string
  title: string
  description: string
  assigned_to: string
  status: 'pending' | 'in_progress' | 'completed'
  deadline?: Date
  completed_at?: Date
}

export interface RecoveryPlan {
  id: string
  incident_id: string
  generated_by: 'ai' | 'manual'
  generated_at: Date
  similar_cases: string[] // Case study IDs
  phases: RecoveryPhase[]
  budget_projection: BudgetProjection
  forecasts: RecoveryForecast[]
}

export interface RecoveryPhase {
  id: string
  title: string
  duration: string
  order: number
  steps: RecoveryStep[]
  resources_needed: ResourceRequirement[]
}

export interface RecoveryStep {
  id: string
  title: string
  description: string
  assigned_to?: string
  deadline?: Date
  status: 'pending' | 'in_progress' | 'completed'
  dependencies: string[] // Step IDs
}

export interface ResourceRequirement {
  type: 'people' | 'budget' | 'system' | 'vendor'
  name: string
  quantity?: number
  estimated_cost?: number
}

export interface BudgetProjection {
  immediate_costs: number
  recovery_costs: number
  lost_revenue: number
  total_impact: number
  currency: string
}

export interface RecoveryForecast {
  scenario: 'best_case' | 'most_likely' | 'worst_case'
  recovery_time_days: number
  financial_impact: number
  confidence: number // 0-100
  key_assumptions: string[]
}

// ============================================================================
// MARKETPLACE
// ============================================================================

export interface MarketplaceFilters {
  certifications: string[]
  industry?: string
  price_range: [number, number]
  rating: number
  availability?: 'immediate' | 'this_week' | 'this_month'
  service_type?: AuditorService
}

export interface ServiceRequest {
  id: string
  client_id: string
  auditor_id: string
  service_type: AuditorService
  status: 'requested' | 'accepted' | 'in_progress' | 'completed' | 'cancelled'
  description: string
  requested_date: Date
  scheduled_date?: Date
  duration_hours?: number
  price: number
  payment_status: 'pending' | 'paid' | 'refunded'
  created_at: Date
}

export interface Review {
  id: string
  request_id: string
  reviewer_id: string
  auditor_id: string
  rating: number // 1-5
  comment: string
  categories: ReviewCategories
  created_at: Date
}

export interface ReviewCategories {
  professionalism: number // 1-5
  expertise: number // 1-5
  communication: number // 1-5
  value: number // 1-5
}

// ============================================================================
// PLATFORM ANALYTICS
// ============================================================================

export interface PlatformMetrics {
  users: {
    total: number
    active_monthly: number
    retention_rate: number
  }
  revenue: {
    mrr: number
    arr: number
    gmv: number // Gross Marketplace Volume
  }
  engagement: {
    daily_active_users: number
    avg_session_duration: number
    nps: number
  }
  marketplace: {
    total_auditors: number
    gmv_monthly: number
    booking_rate: number
  }
}
