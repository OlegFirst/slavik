// User & Auth Types
export type UserRole =
  | 'platform_admin'
  | 'org_admin'
  | 'bcm_specialist'
  | 'viewer'

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  organization_id: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  token: string
  user: User
}

// Organization Types
export type OrganizationSize = 'small' | 'medium' | 'large' | 'enterprise'

export interface Organization {
  id: string
  name: string
  industry: string
  size: OrganizationSize
  created_at: string
  updated_at: string
}

// BIA Types
export type BIAStatus =
  | 'draft'
  | 'in_progress'
  | 'completed'
  | 'approved'
  | 'archived'

export interface BIAAssessment {
  id: string
  organization_id: string
  name: string
  description?: string
  status: BIAStatus
  criticality_score: number
  rto: number // Recovery Time Objective (hours)
  rpo: number // Recovery Point Objective (hours)
  mtpd: number // Maximum Tolerable Period of Disruption (hours)
  created_by: string
  created_at: string
  updated_at: string
}

export interface BusinessProcess {
  id: string
  assessment_id: string
  name: string
  description: string
  criticality: 1 | 2 | 3 | 4 | 5
  dependencies: string[]
  resources_required: string[]
  rto: number
  rpo: number
  financial_impact: number
  created_at: string
  updated_at: string
}

// Risk Types
export type RiskStatus =
  | 'identified'
  | 'assessed'
  | 'treated'
  | 'monitored'
  | 'closed'

export type RiskCategory =
  | 'strategic'
  | 'operational'
  | 'financial'
  | 'compliance'
  | 'reputational'
  | 'technology'

export interface Risk {
  id: string
  organization_id: string
  name: string
  description: string
  category: RiskCategory
  likelihood: 1 | 2 | 3 | 4 | 5
  impact: 1 | 2 | 3 | 4 | 5
  risk_score: number // likelihood * impact
  status: RiskStatus
  owner: string
  mitigation_strategy?: string
  created_at: string
  updated_at: string
}

export interface RiskMatrixData {
  low: Risk[]
  medium: Risk[]
  high: Risk[]
  critical: Risk[]
}

// Document Types
export type DocumentType =
  | 'policy'
  | 'procedure'
  | 'plan'
  | 'template'
  | 'report'

export type DocumentStatus =
  | 'draft'
  | 'review'
  | 'approved'
  | 'archived'

export interface Document {
  id: string
  organization_id: string
  title: string
  type: DocumentType
  status: DocumentStatus
  version: string
  content: string
  created_by: string
  approved_by?: string
  created_at: string
  updated_at: string
}

// Compliance Types
export interface ComplianceStatus {
  standard: string
  overall_score: number
  total_controls: number
  implemented: number
  partial: number
  not_implemented: number
  last_assessment: string
}

export interface GapAnalysisItem {
  id: string
  control_id: string
  control_name: string
  status: 'implemented' | 'partial' | 'not_implemented'
  gap_description: string
  remediation_plan?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  due_date?: string
}

// Governance Types
export type DecisionStatus =
  | 'proposed'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'implemented'

export interface GovernanceDecision {
  id: string
  organization_id: string
  title: string
  description: string
  category: string
  status: DecisionStatus
  proposed_by: string
  approved_by?: string
  decision_date?: string
  implementation_date?: string
  impact_assessment: string
  created_at: string
  updated_at: string
}

// Dashboard Types
export interface DashboardSummary {
  total_assessments: number
  active_risks: number
  compliance_score: number
  active_incidents: number
  critical_processes: number
  overdue_tasks: number
}

export interface DashboardMetrics {
  bia: {
    total: number
    by_status: Record<BIAStatus, number>
    avg_criticality: number
  }
  risk: {
    total: number
    by_category: Record<RiskCategory, number>
    by_severity: {
      low: number
      medium: number
      high: number
      critical: number
    }
  }
  compliance: {
    overall_score: number
    by_standard: Record<string, number>
  }
}

export interface Activity {
  id: string
  type: 'bia' | 'risk' | 'document' | 'compliance' | 'incident'
  action: string
  description: string
  user: string
  timestamp: string
  metadata?: Record<string, any>
}

// Admin/Monitoring Types
export interface ServiceHealth {
  service_name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime: number
  last_check: string
  response_time_ms: number
  error_count: number
}

export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  active_connections: number
  requests_per_minute: number
  error_rate: number
}

// WebSocket/Event Types
export interface PlatformEvent {
  event_type: string
  payload: any
  timestamp: string
  user_id?: string
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_prev: boolean
}

// Form Types
export interface BIAFormData {
  name: string
  description?: string
  status: BIAStatus
  rto: number
  rpo: number
  mtpd: number
}

export interface RiskFormData {
  name: string
  description: string
  category: RiskCategory
  likelihood: 1 | 2 | 3 | 4 | 5
  impact: 1 | 2 | 3 | 4 | 5
  owner: string
  mitigation_strategy?: string
}
