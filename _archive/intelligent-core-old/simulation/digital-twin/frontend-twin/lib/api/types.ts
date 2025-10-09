// Authentication
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
  user: User;
}

export interface User {
  id: string;
  username: string;
  tenant_id: string;
  is_active: boolean;
  created_at: string;
}

// Organizations
export interface Organization {
  id: string;
  name: string;
  industry: string;
  size: string;
  country: string;
  maturity_level: number;
  twin_health_score?: number;
  risk_landscape?: Record<string, any>;
  compliance_status?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TwinInsight {
  id: string;
  type: 'risk' | 'opportunity' | 'warning' | 'recommendation' | 'compliance' | 'trend' | 'anomaly';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  actionable: boolean;
  suggested_actions: string[];
  metadata?: Record<string, any>;
  created_at: string;
}

export interface OrganizationInsights {
  organization_id: string;
  organization_name: string;
  insights_count: number;
  insights: TwinInsight[];
  summary: {
    critical_count: number;
    high_count: number;
    medium_count: number;
    low_count: number;
  };
  generated_at: string;
}

// Queue Theory BIA
export interface QueueTheoryRequest {
  name: string;
  description?: string;
  arrival_rate: number;
  service_rate: number;
  num_servers: number;
  simulation_hours?: number;
  revenue_per_hour: number;
  cost_per_hour_downtime: number;
  max_acceptable_wait: number;
  max_data_loss_hours: number;
}

export interface QueueTheoryResponse {
  bia_id: string;
  name: string;
  queue_metrics: {
    average_wait_time: number;
    average_queue_length: number;
    server_utilization: number;
    probability_wait: number;
  };
  business_impact: {
    potential_revenue_loss_per_hour: number;
    estimated_annual_risk: number;
    mtd: number;
    impact_category: string;
  };
  rto_rpo_recommendations: {
    recommended_rto_hours: number;
    recommended_rpo_hours: number;
    rationale: string;
  };
  recovery_strategies: Array<{
    name: string;
    estimated_cost_annual: number;
    expected_rto_hours: number;
    risk_reduction_percentage: number;
  }>;
  simulation_details: {
    total_customers_served: number;
    total_simulation_time: number;
    confidence_level: number;
  };
  created_at: string;
}

// Scenarios
export interface ScenarioTemplate {
  id: string;
  name: string;
  description: string;
  category: 'cyber' | 'natural_disaster' | 'pandemic' | 'supply_chain' | 'technology_failure' | 'human_error' | 'custom';
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  estimated_duration_minutes: number;
  objectives: string[];
  injects: Inject[];
  success_criteria: Record<string, any>;
  ai_generated: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Inject {
  id: string;
  time_offset_minutes: number;
  title: string;
  description: string;
  inject_type: 'information' | 'question' | 'decision' | 'action';
  expected_actions: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface AdvancedAIRequest {
  organization_id: string;
  base_category: string;
  difficulty: string;
  focus_areas: string[];
  duration_minutes: number;
  include_historical_context: boolean;
  complexity_level: number;
}
