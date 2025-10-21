/**
 * Risk Assessment Service API Client
 * Real integration with backend (port 8040)
 * Comprehensive API client for all Risk Assessment Service endpoints
 * Week 5 - Risk Assessment Module
 */

import { apiClient } from './client';

// ==================== TYPE IMPORTS ====================
// Types will be imported from @/types/risk once created
// For now, using placeholders that match the backend schema

export interface Risk {
  id?: string;
  organization_id: string;
  risk_title: string;
  risk_code?: string;
  risk_category: RiskCategory;
  description: string;
  threat_source?: string;
  vulnerabilities: string[];
  likelihood: RiskLikelihood;
  impact: RiskImpact;
  inherent_risk_score: number;
  treatment_strategy?: TreatmentStrategy;
  residual_likelihood?: RiskLikelihood;
  residual_impact?: RiskImpact;
  residual_risk_score?: number;
  risk_owner_id?: string;
  status: RiskStatus;
  last_reviewed_at?: string;
  next_review_date?: string;
  related_processes: any[];
  related_assets: any[];
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface RiskCreate {
  organization_id: string;
  risk_title: string;
  risk_code?: string;
  risk_category: RiskCategory;
  description: string;
  threat_source?: string;
  vulnerabilities?: string[];
  likelihood: RiskLikelihood;
  impact: RiskImpact;
  risk_owner_id?: string;
  related_processes?: any[];
  related_assets?: any[];
}

export interface RiskUpdate {
  risk_title?: string;
  risk_code?: string;
  risk_category?: RiskCategory;
  description?: string;
  threat_source?: string;
  vulnerabilities?: string[];
  likelihood?: RiskLikelihood;
  impact?: RiskImpact;
  treatment_strategy?: TreatmentStrategy;
  residual_likelihood?: RiskLikelihood;
  residual_impact?: RiskImpact;
  risk_owner_id?: string;
  status?: RiskStatus;
  next_review_date?: string;
  related_processes?: any[];
  related_assets?: any[];
}

export interface FAIRAnalysis {
  risk_id: string;
  threat_event_frequency: number;
  vulnerability_score: number;
  loss_event_frequency: number;
  primary_loss_min: number;
  primary_loss_max: number;
  primary_loss_most_likely: number;
  secondary_loss_min: number;
  secondary_loss_max: number;
  annual_loss_expectancy: number;
  risk_rating: string;
  confidence_interval_low: number;
  confidence_interval_high: number;
  analyzed_at?: string;
  analyzed_by?: string;
}

export interface FAIRAnalysisCreate {
  threat_event_frequency: number;
  vulnerability_score: number;
  primary_loss_min: number;
  primary_loss_max: number;
  primary_loss_most_likely: number;
  secondary_loss_min?: number;
  secondary_loss_max?: number;
  analyzed_by?: string;
}

export interface MonteCarloSimulation {
  risk_id: string;
  iterations: number;
  factors: Array<{
    name?: string;
    min: number;
    most_likely: number;
    max: number;
  }>;
  mean_loss: number;
  median_loss: number;
  percentile_95: number;
  percentile_99: number;
  distribution_data?: {
    histogram: number[];
    bin_edges: number[];
    min: number;
    max: number;
    std_dev: number;
  };
  simulated_at?: string;
}

export interface MonteCarloSimulationCreate {
  iterations?: number;
  factors: Array<{
    name?: string;
    min: number;
    most_likely: number;
    max: number;
  }>;
}

export interface RiskTreatmentPlan {
  id?: string;
  risk_id: string;
  strategy: TreatmentStrategy;
  description: string;
  actions: Array<{
    action?: string;
    responsible?: string;
    deadline?: string;
    status?: string;
  }>;
  responsible_party?: string;
  start_date?: string;
  target_date?: string;
  completion_date?: string;
  estimated_cost?: number;
  actual_cost?: number;
  expected_residual_likelihood?: RiskLikelihood;
  expected_residual_impact?: RiskImpact;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface TreatmentPlanCreate {
  strategy: TreatmentStrategy;
  description: string;
  actions?: Array<{
    action?: string;
    responsible?: string;
    deadline?: string;
    status?: string;
  }>;
  responsible_party?: string;
  start_date?: string;
  target_date?: string;
  estimated_cost?: number;
  expected_residual_likelihood?: RiskLikelihood;
  expected_residual_impact?: RiskImpact;
}

export interface TreatmentPlanUpdate {
  strategy?: TreatmentStrategy;
  description?: string;
  actions?: Array<{
    action?: string;
    responsible?: string;
    deadline?: string;
    status?: string;
  }>;
  responsible_party?: string;
  start_date?: string;
  target_date?: string;
  completion_date?: string;
  estimated_cost?: number;
  actual_cost?: number;
  expected_residual_likelihood?: RiskLikelihood;
  expected_residual_impact?: RiskImpact;
  status?: string;
}

export interface RiskReport {
  total_risks: number;
  by_category: Record<RiskCategory, number>;
  by_status: Record<RiskStatus, number>;
  by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  average_score: number;
  trends: {
    new_this_month: number;
    closed_this_month: number;
    overdue_reviews: number;
  };
  generated_at: string;
}

export interface RiskMatrixPosition {
  risk_id: string;
  likelihood: number;
  impact: number;
  score: number;
  severity: string;
  position: {
    x: number;
    y: number;
  };
}

export interface RiskHeatMap {
  matrix: number[][];
  risks_by_cell: Record<string, Risk[]>;
  severity_zones: {
    critical: Array<{ x: number; y: number }>;
    high: Array<{ x: number; y: number }>;
    medium: Array<{ x: number; y: number }>;
    low: Array<{ x: number; y: number }>;
  };
}

export interface RiskTrends {
  period_days: number;
  data_points: Array<{
    date: string;
    total_risks: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    average_score: number;
  }>;
  summary: {
    total_change: number;
    critical_change: number;
    average_score_change: number;
  };
}

// ==================== ENUMS ====================

export enum RiskCategory {
  OPERATIONAL = 'operational',
  FINANCIAL = 'financial',
  STRATEGIC = 'strategic',
  COMPLIANCE = 'compliance',
  REPUTATIONAL = 'reputational',
  CYBERSECURITY = 'cybersecurity',
  NATURAL_DISASTER = 'natural_disaster',
}

export enum RiskLikelihood {
  RARE = 1,
  UNLIKELY = 2,
  POSSIBLE = 3,
  LIKELY = 4,
  ALMOST_CERTAIN = 5,
}

export enum RiskImpact {
  INSIGNIFICANT = 1,
  MINOR = 2,
  MODERATE = 3,
  MAJOR = 4,
  CATASTROPHIC = 5,
}

export enum TreatmentStrategy {
  AVOID = 'avoid',
  MITIGATE = 'mitigate',
  TRANSFER = 'transfer',
  ACCEPT = 'accept',
}

export enum RiskStatus {
  IDENTIFIED = 'identified',
  ANALYZING = 'analyzing',
  TREATED = 'treated',
  MONITORING = 'monitoring',
  CLOSED = 'closed',
}

// ==================== QUERY PARAMS ====================

export interface RiskFilters {
  category?: RiskCategory;
  status?: RiskStatus;
  min_score?: number;
  max_score?: number;
  owner_id?: string;
  organization_id?: string;
  skip?: number;
  limit?: number;
}

export interface WorkflowAIParams {
  case_id?: string;
  query?: string;
  status?: string;
  severity?: string;
  days?: number;
  limit?: number;
  offset?: number;
}

// ==================== API CLIENT ====================

const BASE_URL = '/api/v1/risk';
const AI_BASE_URL = '/api/v1/workflow-ai';

/**
 * Risk Assessment API Client
 * Comprehensive client for all risk assessment endpoints
 */
export const riskClient = {
  // ==================== RISK CRUD OPERATIONS ====================

  /**
   * Get list of risks with optional filters
   * GET /api/v1/risk/assessments
   */
  async getRisks(params?: RiskFilters): Promise<Risk[]> {
    const queryParams = new URLSearchParams();

    if (params?.category) queryParams.append('category', params.category);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.min_score !== undefined) queryParams.append('min_score', String(params.min_score));
    if (params?.max_score !== undefined) queryParams.append('max_score', String(params.max_score));
    if (params?.owner_id) queryParams.append('owner_id', params.owner_id);
    if (params?.organization_id) queryParams.append('organization_id', params.organization_id);
    if (params?.skip !== undefined) queryParams.append('skip', String(params.skip));
    if (params?.limit !== undefined) queryParams.append('limit', String(params.limit));

    return apiClient.request<Risk[]>({
      method: 'GET',
      url: `${BASE_URL}/assessments?${queryParams.toString()}`,
    });
  },

  /**
   * Get single risk by ID
   * GET /api/v1/risk/assessments/{risk_id}
   */
  async getRisk(riskId: string): Promise<Risk> {
    return apiClient.request<Risk>({
      method: 'GET',
      url: `${BASE_URL}/assessments/${riskId}`,
    });
  },

  /**
   * Create new risk assessment
   * POST /api/v1/risk/assessments
   */
  async createRisk(data: RiskCreate): Promise<Risk> {
    return apiClient.request<Risk>({
      method: 'POST',
      url: `${BASE_URL}/assessments`,
      data,
    });
  },

  /**
   * Update existing risk assessment
   * PUT /api/v1/risk/assessments/{risk_id}
   */
  async updateRisk(riskId: string, data: RiskUpdate): Promise<Risk> {
    return apiClient.request<Risk>({
      method: 'PUT',
      url: `${BASE_URL}/assessments/${riskId}`,
      data,
    });
  },

  /**
   * Delete risk assessment (soft delete)
   * DELETE /api/v1/risk/assessments/{risk_id}
   * Sets is_active to false instead of hard delete
   */
  async deleteRisk(riskId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/assessments/${riskId}`,
    });
  },

  // ==================== FAIR ANALYSIS ====================

  /**
   * Perform FAIR (Factor Analysis of Information Risk) analysis
   * POST /api/v1/risk/assessments/{risk_id}/fair-analysis
   * Calculates Annual Loss Expectancy (ALE) and risk rating
   */
  async performFAIRAnalysis(riskId: string, data: FAIRAnalysisCreate): Promise<FAIRAnalysis> {
    return apiClient.request<FAIRAnalysis>({
      method: 'POST',
      url: `${BASE_URL}/assessments/${riskId}/fair-analysis`,
      data,
    });
  },

  /**
   * Get FAIR analysis results for a risk
   * GET /api/v1/risk/assessments/{risk_id}/fair-analysis
   */
  async getFAIRAnalysis(riskId: string): Promise<FAIRAnalysis> {
    return apiClient.request<FAIRAnalysis>({
      method: 'GET',
      url: `${BASE_URL}/assessments/${riskId}/fair-analysis`,
    });
  },

  // ==================== MONTE CARLO SIMULATION ====================

  /**
   * Run Monte Carlo simulation for risk quantification
   * POST /api/v1/risk/assessments/{risk_id}/monte-carlo
   * Performs probabilistic risk analysis with configurable iterations
   * Default: 10,000 iterations
   */
  async runMonteCarloSimulation(
    riskId: string,
    data: MonteCarloSimulationCreate
  ): Promise<MonteCarloSimulation> {
    return apiClient.request<MonteCarloSimulation>({
      method: 'POST',
      url: `${BASE_URL}/assessments/${riskId}/monte-carlo`,
      data,
    });
  },

  /**
   * Get Monte Carlo simulation results for a risk
   * GET /api/v1/risk/assessments/{risk_id}/monte-carlo
   * Returns VaR (95th percentile), CVaR (99th percentile), and distribution data
   */
  async getMonteCarloSimulation(riskId: string): Promise<MonteCarloSimulation> {
    return apiClient.request<MonteCarloSimulation>({
      method: 'GET',
      url: `${BASE_URL}/assessments/${riskId}/monte-carlo`,
    });
  },

  // ==================== TREATMENT PLANS ====================

  /**
   * Create risk treatment plan
   * POST /api/v1/risk/assessments/{risk_id}/treatment-plans
   * Defines mitigation strategy and action items
   */
  async createTreatmentPlan(riskId: string, data: TreatmentPlanCreate): Promise<RiskTreatmentPlan> {
    return apiClient.request<RiskTreatmentPlan>({
      method: 'POST',
      url: `${BASE_URL}/assessments/${riskId}/treatment-plans`,
      data,
    });
  },

  /**
   * Get all treatment plans for a specific risk
   * GET /api/v1/risk/assessments/{risk_id}/treatment-plans
   */
  async getTreatmentPlans(riskId: string): Promise<RiskTreatmentPlan[]> {
    return apiClient.request<RiskTreatmentPlan[]>({
      method: 'GET',
      url: `${BASE_URL}/assessments/${riskId}/treatment-plans`,
    });
  },

  /**
   * Update treatment plan
   * PUT /api/v1/risk/treatment-plans/{plan_id}
   */
  async updateTreatmentPlan(planId: string, data: TreatmentPlanUpdate): Promise<RiskTreatmentPlan> {
    return apiClient.request<RiskTreatmentPlan>({
      method: 'PUT',
      url: `${BASE_URL}/treatment-plans/${planId}`,
      data,
    });
  },

  /**
   * Delete treatment plan
   * DELETE /api/v1/risk/treatment-plans/{plan_id}
   */
  async deleteTreatmentPlan(planId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/treatment-plans/${planId}`,
    });
  },

  // ==================== ANALYTICS & VISUALIZATIONS ====================

  /**
   * Generate comprehensive risk report
   * GET /api/v1/risk/reports
   * Includes risk distribution by category, status, severity, and trends
   */
  async getRiskReport(organizationId?: string): Promise<RiskReport> {
    const queryParams = new URLSearchParams();
    if (organizationId) queryParams.append('organization_id', organizationId);

    return apiClient.request<RiskReport>({
      method: 'GET',
      url: `${BASE_URL}/reports?${queryParams.toString()}`,
    });
  },

  /**
   * Get risk matrix position (likelihood × impact)
   * GET /api/v1/risk/assessments/{risk_id}/matrix-position
   * Returns position in 5×5 risk matrix
   */
  async getRiskMatrixPosition(riskId: string): Promise<RiskMatrixPosition> {
    return apiClient.request<RiskMatrixPosition>({
      method: 'GET',
      url: `${BASE_URL}/assessments/${riskId}/matrix-position`,
    });
  },

  /**
   * Get risk heat map data (5×5 matrix)
   * GET /api/v1/risk/risk-heat-map
   * Returns matrix with risk counts in each cell and severity zones
   */
  async getRiskHeatMap(organizationId?: string): Promise<RiskHeatMap> {
    const queryParams = new URLSearchParams();
    if (organizationId) queryParams.append('organization_id', organizationId);

    return apiClient.request<RiskHeatMap>({
      method: 'GET',
      url: `${BASE_URL}/risk-heat-map?${queryParams.toString()}`,
    });
  },

  /**
   * Get risk trends over time
   * GET /api/v1/risk/risk-trends
   * Tracks risk evolution across configurable time period (default: 90 days)
   */
  async getRiskTrends(params?: { days?: number; organization_id?: string }): Promise<RiskTrends> {
    const queryParams = new URLSearchParams();
    if (params?.days) queryParams.append('days', String(params.days));
    if (params?.organization_id) queryParams.append('organization_id', params.organization_id);

    return apiClient.request<RiskTrends>({
      method: 'GET',
      url: `${BASE_URL}/risk-trends?${queryParams.toString()}`,
    });
  },

  /**
   * Get critical risks (score >= 20)
   * GET /api/v1/risk/critical-risks
   * Returns all risks with critical severity requiring immediate attention
   */
  async getCriticalRisks(organizationId?: string): Promise<Risk[]> {
    const queryParams = new URLSearchParams();
    if (organizationId) queryParams.append('organization_id', organizationId);

    return apiClient.request<Risk[]>({
      method: 'GET',
      url: `${BASE_URL}/critical-risks?${queryParams.toString()}`,
    });
  },

  // ==================== AI/WORKFLOW INTELLIGENCE ====================

  /**
   * Get workflow insights from AI analysis
   * GET /api/v1/workflow-ai/insights
   * Returns AI-powered insights about risk patterns and trends
   */
  async getWorkflowInsights(params?: WorkflowAIParams): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.case_id) queryParams.append('case_id', params.case_id);
    if (params?.days) queryParams.append('days', String(params.days));

    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/insights?${queryParams.toString()}`,
    });
  },

  /**
   * Get AI-powered risk recommendations
   * GET /api/v1/workflow-ai/recommendations
   * Provides actionable recommendations based on risk analysis
   */
  async getAIRecommendations(params?: WorkflowAIParams): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.case_id) queryParams.append('case_id', params.case_id);
    if (params?.limit) queryParams.append('limit', String(params.limit));

    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/recommendations?${queryParams.toString()}`,
    });
  },

  /**
   * Search cases with AI-powered semantic search
   * GET /api/v1/workflow-ai/cases/search
   * Supports natural language queries and filtering
   */
  async searchCases(params?: WorkflowAIParams): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.query) queryParams.append('query', params.query);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.offset) queryParams.append('offset', String(params.offset));

    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/cases/search?${queryParams.toString()}`,
    });
  },

  /**
   * Find similar cases using AI similarity matching
   * GET /api/v1/workflow-ai/cases/{case_id}/similar
   * Returns cases with similar characteristics and patterns
   */
  async getSimilarCases(caseId: string, params?: { limit?: number }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', String(params.limit));

    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/cases/${caseId}/similar?${queryParams.toString()}`,
    });
  },

  /**
   * Get case timeline with events and updates
   * GET /api/v1/workflow-ai/cases/{case_id}/timeline
   * Returns chronological history of case events
   */
  async getCaseTimeline(caseId: string): Promise<any> {
    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/cases/${caseId}/timeline`,
    });
  },

  /**
   * Analyze patterns in risk data using AI
   * GET /api/v1/workflow-ai/analytics/patterns
   * Identifies recurring patterns and correlations
   */
  async analyzePatterns(params?: { days?: number }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.days) queryParams.append('days', String(params.days));

    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/analytics/patterns?${queryParams.toString()}`,
    });
  },

  /**
   * Get performance metrics and KPIs
   * GET /api/v1/workflow-ai/analytics/performance
   * Returns key performance indicators for risk management
   */
  async getPerformanceMetrics(params?: { days?: number }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.days) queryParams.append('days', String(params.days));

    return apiClient.request<any>({
      method: 'GET',
      url: `${AI_BASE_URL}/analytics/performance?${queryParams.toString()}`,
    });
  },

  // ==================== RISK REVIEW & MONITORING ====================

  /**
   * Mark risk as reviewed
   * POST /api/v1/risk/assessments/{risk_id}/review
   * Updates last_reviewed_at and schedules next review
   */
  async markRiskReviewed(riskId: string, reviewData: { reviewer_id: string; notes?: string }): Promise<Risk> {
    return apiClient.request<Risk>({
      method: 'POST',
      url: `${BASE_URL}/assessments/${riskId}/review`,
      data: reviewData,
    });
  },

  /**
   * Get overdue reviews
   * GET /api/v1/risk/overdue-reviews
   * Returns risks that require review based on next_review_date
   */
  async getOverdueReviews(organizationId?: string): Promise<Risk[]> {
    const queryParams = new URLSearchParams();
    if (organizationId) queryParams.append('organization_id', organizationId);

    return apiClient.request<Risk[]>({
      method: 'GET',
      url: `${BASE_URL}/overdue-reviews?${queryParams.toString()}`,
    });
  },

  /**
   * Get risks by owner
   * GET /api/v1/risk/by-owner/{owner_id}
   * Returns all risks assigned to a specific owner
   */
  async getRisksByOwner(ownerId: string): Promise<Risk[]> {
    return apiClient.request<Risk[]>({
      method: 'GET',
      url: `${BASE_URL}/by-owner/${ownerId}`,
    });
  },

  // ==================== RISK RELATIONSHIPS ====================

  /**
   * Link risk to process
   * POST /api/v1/risk/assessments/{risk_id}/processes
   * Associates risk with business processes
   */
  async linkRiskToProcess(riskId: string, processId: string): Promise<Risk> {
    return apiClient.request<Risk>({
      method: 'POST',
      url: `${BASE_URL}/assessments/${riskId}/processes`,
      data: { process_id: processId },
    });
  },

  /**
   * Link risk to asset
   * POST /api/v1/risk/assessments/{risk_id}/assets
   * Associates risk with organizational assets
   */
  async linkRiskToAsset(riskId: string, assetId: string): Promise<Risk> {
    return apiClient.request<Risk>({
      method: 'POST',
      url: `${BASE_URL}/assessments/${riskId}/assets`,
      data: { asset_id: assetId },
    });
  },

  /**
   * Unlink risk from process
   * DELETE /api/v1/risk/assessments/{risk_id}/processes/{process_id}
   */
  async unlinkRiskFromProcess(riskId: string, processId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/assessments/${riskId}/processes/${processId}`,
    });
  },

  /**
   * Unlink risk from asset
   * DELETE /api/v1/risk/assessments/{risk_id}/assets/{asset_id}
   */
  async unlinkRiskFromAsset(riskId: string, assetId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/assessments/${riskId}/assets/${assetId}`,
    });
  },

  // ==================== BULK OPERATIONS ====================

  /**
   * Bulk update risk status
   * POST /api/v1/risk/bulk/update-status
   * Updates status for multiple risks at once
   */
  async bulkUpdateStatus(riskIds: string[], status: RiskStatus): Promise<Risk[]> {
    return apiClient.request<Risk[]>({
      method: 'POST',
      url: `${BASE_URL}/bulk/update-status`,
      data: { risk_ids: riskIds, status },
    });
  },

  /**
   * Bulk delete risks
   * POST /api/v1/risk/bulk/delete
   * Soft deletes multiple risks (sets is_active to false)
   */
  async bulkDeleteRisks(riskIds: string[]): Promise<void> {
    return apiClient.request<void>({
      method: 'POST',
      url: `${BASE_URL}/bulk/delete`,
      data: { risk_ids: riskIds },
    });
  },

  /**
   * Export risks to CSV/Excel
   * GET /api/v1/risk/export
   * Downloads risk data in specified format
   */
  async exportRisks(params?: { format?: 'csv' | 'excel'; filters?: RiskFilters }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    if (params?.format) queryParams.append('format', params.format);
    if (params?.filters?.category) queryParams.append('category', params.filters.category);
    if (params?.filters?.status) queryParams.append('status', params.filters.status);

    const response = await fetch(
      `${BASE_URL}/export?${queryParams.toString()}`,
      {
        headers: {
          Authorization: `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('auth_token') : ''}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Export failed');
    }

    return response.blob();
  },

  // ==================== SYSTEM & HEALTH ====================

  /**
   * Check Risk service health
   * GET /api/v1/risk/health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return apiClient.request<{ status: string; timestamp: string }>({
      method: 'GET',
      url: `${BASE_URL}/health`,
    });
  },

  /**
   * Get service statistics
   * GET /api/v1/risk/stats
   * Returns overall risk management statistics
   */
  async getServiceStats(): Promise<{
    total_risks: number;
    total_treatment_plans: number;
    total_fair_analyses: number;
    total_simulations: number;
    active_risks: number;
    closed_risks: number;
  }> {
    return apiClient.request<any>({
      method: 'GET',
      url: `${BASE_URL}/stats`,
    });
  },
};

// Export default client
export default riskClient;
