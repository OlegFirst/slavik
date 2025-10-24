/**
 * Planning Module - API Client
 * Handles all API communication for Business Continuity Planning module
 *
 * Created: 2025-10-21
 * Agent: 3/3 (Planning Module Round 1)
 *
 * Total Endpoints: 35
 * - Plan Management: 10 endpoints
 * - Recovery Strategies: 8 endpoints
 * - Action Plans: 8 endpoints
 * - Analytics: 5 endpoints
 * - Integration: 4 endpoints
 */

import { apiClient } from './client';

// ==================== TYPE DEFINITIONS ====================

/**
 * Plan Types
 */
export enum PlanType {
  BCP = 'bcp',
  DRP = 'drp',
  CRISIS = 'crisis',
  IT_RECOVERY = 'it_recovery',
  COMMUNICATION = 'communication',
}

/**
 * Plan Status
 */
export enum PlanStatus {
  DRAFT = 'draft',
  REVIEW = 'review',
  APPROVED = 'approved',
  ACTIVE = 'active',
  ARCHIVED = 'archived',
}

/**
 * Strategy Types
 */
export enum StrategyType {
  PREVENTIVE = 'preventive',
  DETECTIVE = 'detective',
  CORRECTIVE = 'corrective',
  RECOVERY = 'recovery',
}

/**
 * Action Status
 */
export enum ActionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/**
 * BC Plan
 */
export interface BCPlan {
  id?: string;
  organization_id: string;
  plan_name: string;
  plan_type: PlanType;
  description: string;
  scope: string;
  objectives: string[];
  status: PlanStatus;
  owner_id?: string;
  version: string;
  effective_date?: string;
  review_date?: string;
  approval_date?: string;
  approved_by?: string;
  related_processes: string[];
  related_risks: string[];
  related_assets: string[];
  activation_criteria?: string;
  deactivation_criteria?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * BC Plan Create
 */
export interface BCPlanCreate {
  organization_id: string;
  plan_name: string;
  plan_type: PlanType;
  description: string;
  scope: string;
  objectives: string[];
  owner_id?: string;
  related_processes?: string[];
  related_risks?: string[];
  related_assets?: string[];
  activation_criteria?: string;
  deactivation_criteria?: string;
}

/**
 * BC Plan Update
 */
export interface BCPlanUpdate {
  plan_name?: string;
  plan_type?: PlanType;
  description?: string;
  scope?: string;
  objectives?: string[];
  status?: PlanStatus;
  owner_id?: string;
  effective_date?: string;
  review_date?: string;
  related_processes?: string[];
  related_risks?: string[];
  related_assets?: string[];
  activation_criteria?: string;
  deactivation_criteria?: string;
}

/**
 * Recovery Strategy
 */
export interface RecoveryStrategy {
  id?: string;
  plan_id: string;
  strategy_name: string;
  strategy_type: StrategyType;
  description: string;
  rto_target?: number;
  rpo_target?: number;
  resource_requirements: {
    personnel?: string[];
    equipment?: string[];
    facilities?: string[];
    technology?: string[];
  };
  estimated_cost?: number;
  dependencies: string[];
  testing_schedule?: string;
  last_tested_at?: string;
  test_results?: string;
  effectiveness_rating?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Recovery Strategy Create
 */
export interface RecoveryStrategyCreate {
  plan_id: string;
  strategy_name: string;
  strategy_type: StrategyType;
  description: string;
  rto_target?: number;
  rpo_target?: number;
  resource_requirements?: {
    personnel?: string[];
    equipment?: string[];
    facilities?: string[];
    technology?: string[];
  };
  estimated_cost?: number;
  dependencies?: string[];
  testing_schedule?: string;
}

/**
 * Recovery Strategy Update
 */
export interface RecoveryStrategyUpdate {
  strategy_name?: string;
  strategy_type?: StrategyType;
  description?: string;
  rto_target?: number;
  rpo_target?: number;
  resource_requirements?: {
    personnel?: string[];
    equipment?: string[];
    facilities?: string[];
    technology?: string[];
  };
  estimated_cost?: number;
  dependencies?: string[];
  testing_schedule?: string;
  last_tested_at?: string;
  test_results?: string;
  effectiveness_rating?: number;
}

/**
 * Action Plan
 */
export interface ActionPlan {
  id?: string;
  plan_id: string;
  action_title: string;
  description: string;
  action_type: 'immediate' | 'short_term' | 'long_term';
  responsible_user_id?: string;
  assigned_to?: string;
  due_date?: string;
  completion_date?: string;
  status: ActionStatus;
  priority: 'critical' | 'high' | 'medium' | 'low';
  estimated_duration?: number;
  actual_duration?: number;
  prerequisites: string[];
  deliverables: string[];
  progress_percentage?: number;
  notes?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Action Plan Create
 */
export interface ActionPlanCreate {
  plan_id: string;
  action_title: string;
  description: string;
  action_type: 'immediate' | 'short_term' | 'long_term';
  responsible_user_id?: string;
  assigned_to?: string;
  due_date?: string;
  priority?: 'critical' | 'high' | 'medium' | 'low';
  estimated_duration?: number;
  prerequisites?: string[];
  deliverables?: string[];
}

/**
 * Action Plan Update
 */
export interface ActionPlanUpdate {
  action_title?: string;
  description?: string;
  action_type?: 'immediate' | 'short_term' | 'long_term';
  responsible_user_id?: string;
  assigned_to?: string;
  due_date?: string;
  completion_date?: string;
  status?: ActionStatus;
  priority?: 'critical' | 'high' | 'medium' | 'low';
  estimated_duration?: number;
  actual_duration?: number;
  prerequisites?: string[];
  deliverables?: string[];
  progress_percentage?: number;
  notes?: string;
}

/**
 * Plan Version
 */
export interface PlanVersion {
  version: string;
  created_at: string;
  created_by: string;
  changes: string;
}

/**
 * Strategy Test Result
 */
export interface StrategyTestResult {
  test_date: string;
  test_results: string;
  effectiveness_rating: number;
  tester: string;
}

/**
 * Strategy Effectiveness
 */
export interface StrategyEffectiveness {
  strategy_id: string;
  average_rating: number;
  test_count: number;
  last_test_date?: string;
  trend: 'improving' | 'stable' | 'declining';
}

/**
 * Plan Coverage
 */
export interface PlanCoverage {
  total_plans: number;
  by_type: Record<PlanType, number>;
  by_status: Record<PlanStatus, number>;
  processes_covered: number;
  processes_total: number;
  coverage_percentage: number;
  risks_covered: number;
  risks_total: number;
}

/**
 * Maturity Assessment
 */
export interface MaturityAssessment {
  overall_score: number;
  dimensions: {
    plan_coverage: number;
    strategy_effectiveness: number;
    action_completion: number;
    review_frequency: number;
    resource_adequacy: number;
  };
  maturity_level: 'initial' | 'developing' | 'defined' | 'managed' | 'optimizing';
  recommendations: string[];
}

/**
 * Planning Gap
 */
export interface PlanningGap {
  gap_type: 'missing_plan' | 'outdated_plan' | 'incomplete_strategy' | 'missing_resources';
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  affected_process?: string;
  affected_risk?: string;
  recommendation: string;
}

/**
 * Timeline Event
 */
export interface TimelineEvent {
  event_type: 'plan_created' | 'plan_approved' | 'plan_activated' | 'strategy_tested' | 'action_completed';
  event_date: string;
  plan_id?: string;
  plan_name?: string;
  description: string;
}

/**
 * Executive Summary
 */
export interface ExecutiveSummary {
  organization_id: string;
  report_date: string;

  plans: {
    total: number;
    active: number;
    draft: number;
    review_needed: number;
  };

  coverage: {
    processes: number;
    risks: number;
    percentage: number;
  };

  actions: {
    total: number;
    completed: number;
    in_progress: number;
    overdue: number;
  };

  maturity: {
    score: number;
    level: string;
  };

  recent_activities: TimelineEvent[];
  critical_gaps: PlanningGap[];
}

/**
 * BIA Alignment
 */
export interface BIAAlignment {
  process_id: string;
  process_name: string;
  has_plan: boolean;
  plan_ids: string[];
  rto_target?: number;
  rto_current?: number;
  gap?: number;
}

/**
 * Risk Alignment
 */
export interface RiskAlignment {
  risk_id: string;
  risk_title: string;
  risk_score: number;
  has_plan: boolean;
  plan_ids: string[];
  mitigation_status: 'none' | 'partial' | 'full';
}

/**
 * Plan Dependency
 */
export interface PlanDependency {
  plan_id: string;
  plan_name: string;
  depends_on: {
    processes: string[];
    assets: string[];
    risks: string[];
  };
  impacts: {
    processes: string[];
    other_plans: string[];
  };
}

/**
 * Sync Request
 */
export interface SyncRequest {
  sync_bia?: boolean;
  sync_risks?: boolean;
  sync_assets?: boolean;
}

/**
 * Sync Result
 */
export interface SyncResult {
  synced_at: string;
  processes_synced: number;
  risks_synced: number;
  assets_synced: number;
  new_alignments: number;
}

/**
 * List BC Plans Parameters
 */
export interface ListBCPlansParams {
  organization_id: string;
  plan_type?: PlanType;
  status?: PlanStatus;
  process_id?: string;
  page?: number;
  limit?: number;
}

/**
 * List BC Plans Response
 */
export interface ListBCPlansResponse {
  plans: BCPlan[];
  total: number;
  page: number;
  limit: number;
}

// ==================== API CLIENT ====================

const BASE_URL = '/api/v1/planning';

/**
 * Planning Module API Client
 * Comprehensive client for all business continuity planning endpoints
 */
export const planningClient = {
  // ============= PLAN MANAGEMENT (10 functions) =============

  /**
   * Create new BC plan
   * POST /api/v1/planning/plans
   */
  async createBCPlan(data: BCPlanCreate): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'POST',
      url: `${BASE_URL}/plans`,
      data,
    });
  },

  /**
   * List BC plans with filters
   * GET /api/v1/planning/plans
   */
  async listBCPlans(params: ListBCPlansParams): Promise<ListBCPlansResponse> {
    const queryParams = new URLSearchParams();

    queryParams.append('organization_id', params.organization_id);
    if (params.plan_type) queryParams.append('plan_type', params.plan_type);
    if (params.status) queryParams.append('status', params.status);
    if (params.process_id) queryParams.append('process_id', params.process_id);
    if (params.page !== undefined) queryParams.append('page', String(params.page));
    if (params.limit !== undefined) queryParams.append('limit', String(params.limit));

    return apiClient.request<ListBCPlansResponse>({
      method: 'GET',
      url: `${BASE_URL}/plans?${queryParams.toString()}`,
    });
  },

  /**
   * Get single BC plan by ID
   * GET /api/v1/planning/plans/{plan_id}
   */
  async getBCPlan(planId: string): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'GET',
      url: `${BASE_URL}/plans/${planId}`,
    });
  },

  /**
   * Update existing BC plan
   * PUT /api/v1/planning/plans/{plan_id}
   */
  async updateBCPlan(planId: string, data: BCPlanUpdate): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'PUT',
      url: `${BASE_URL}/plans/${planId}`,
      data,
    });
  },

  /**
   * Delete BC plan (soft delete)
   * DELETE /api/v1/planning/plans/{plan_id}
   * Sets is_active to false instead of hard delete
   */
  async deleteBCPlan(planId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/plans/${planId}`,
    });
  },

  /**
   * Approve BC plan
   * POST /api/v1/planning/plans/{plan_id}/approve
   * Changes status to approved and records approval metadata
   */
  async approveBCPlan(planId: string, approvedBy: string): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'POST',
      url: `${BASE_URL}/plans/${planId}/approve`,
      data: { approved_by: approvedBy },
    });
  },

  /**
   * Activate BC plan
   * POST /api/v1/planning/plans/{plan_id}/activate
   * Changes status to active and sets effective date
   */
  async activateBCPlan(planId: string): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'POST',
      url: `${BASE_URL}/plans/${planId}/activate`,
    });
  },

  /**
   * Archive BC plan
   * POST /api/v1/planning/plans/{plan_id}/archive
   * Changes status to archived
   */
  async archiveBCPlan(planId: string): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'POST',
      url: `${BASE_URL}/plans/${planId}/archive`,
    });
  },

  /**
   * Get BC plan version history
   * GET /api/v1/planning/plans/{plan_id}/versions
   * Returns chronological history of all plan versions
   */
  async getBCPlanVersionHistory(planId: string): Promise<PlanVersion[]> {
    return apiClient.request<PlanVersion[]>({
      method: 'GET',
      url: `${BASE_URL}/plans/${planId}/versions`,
    });
  },

  /**
   * Clone BC plan
   * POST /api/v1/planning/plans/{plan_id}/clone
   * Creates a copy of the plan with a new name
   */
  async cloneBCPlan(planId: string, newPlanName: string): Promise<BCPlan> {
    return apiClient.request<BCPlan>({
      method: 'POST',
      url: `${BASE_URL}/plans/${planId}/clone`,
      data: { new_plan_name: newPlanName },
    });
  },

  // ============= RECOVERY STRATEGIES (8 functions) =============

  /**
   * Create recovery strategy
   * POST /api/v1/planning/plans/{plan_id}/strategies
   */
  async createRecoveryStrategy(data: RecoveryStrategyCreate): Promise<RecoveryStrategy> {
    return apiClient.request<RecoveryStrategy>({
      method: 'POST',
      url: `${BASE_URL}/plans/${data.plan_id}/strategies`,
      data,
    });
  },

  /**
   * List recovery strategies for a plan
   * GET /api/v1/planning/plans/{plan_id}/strategies
   */
  async listRecoveryStrategies(planId: string): Promise<RecoveryStrategy[]> {
    return apiClient.request<RecoveryStrategy[]>({
      method: 'GET',
      url: `${BASE_URL}/plans/${planId}/strategies`,
    });
  },

  /**
   * Get single recovery strategy by ID
   * GET /api/v1/planning/strategies/{strategy_id}
   */
  async getRecoveryStrategy(strategyId: string): Promise<RecoveryStrategy> {
    return apiClient.request<RecoveryStrategy>({
      method: 'GET',
      url: `${BASE_URL}/strategies/${strategyId}`,
    });
  },

  /**
   * Update recovery strategy
   * PUT /api/v1/planning/strategies/{strategy_id}
   */
  async updateRecoveryStrategy(strategyId: string, data: RecoveryStrategyUpdate): Promise<RecoveryStrategy> {
    return apiClient.request<RecoveryStrategy>({
      method: 'PUT',
      url: `${BASE_URL}/strategies/${strategyId}`,
      data,
    });
  },

  /**
   * Delete recovery strategy
   * DELETE /api/v1/planning/strategies/{strategy_id}
   */
  async deleteRecoveryStrategy(strategyId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/strategies/${strategyId}`,
    });
  },

  /**
   * Record strategy test results
   * POST /api/v1/planning/strategies/{strategy_id}/test
   * Records test execution and effectiveness rating
   */
  async recordStrategyTest(strategyId: string, testData: StrategyTestResult): Promise<RecoveryStrategy> {
    return apiClient.request<RecoveryStrategy>({
      method: 'POST',
      url: `${BASE_URL}/strategies/${strategyId}/test`,
      data: testData,
    });
  },

  /**
   * Get strategy effectiveness metrics
   * GET /api/v1/planning/strategies/{strategy_id}/effectiveness
   * Returns average rating, test count, and trend analysis
   */
  async getStrategyEffectiveness(strategyId: string): Promise<StrategyEffectiveness> {
    return apiClient.request<StrategyEffectiveness>({
      method: 'GET',
      url: `${BASE_URL}/strategies/${strategyId}/effectiveness`,
    });
  },

  /**
   * Get strategies by process
   * GET /api/v1/planning/processes/{process_id}/strategies
   * Returns all strategies related to a specific process
   */
  async getStrategiesByProcess(processId: string): Promise<RecoveryStrategy[]> {
    return apiClient.request<RecoveryStrategy[]>({
      method: 'GET',
      url: `${BASE_URL}/processes/${processId}/strategies`,
    });
  },

  // ============= ACTION PLANS (8 functions) =============

  /**
   * Create action plan
   * POST /api/v1/planning/plans/{plan_id}/actions
   */
  async createActionPlan(data: ActionPlanCreate): Promise<ActionPlan> {
    return apiClient.request<ActionPlan>({
      method: 'POST',
      url: `${BASE_URL}/plans/${data.plan_id}/actions`,
      data,
    });
  },

  /**
   * List action plans for a plan
   * GET /api/v1/planning/plans/{plan_id}/actions
   */
  async listActionPlans(planId: string): Promise<ActionPlan[]> {
    return apiClient.request<ActionPlan[]>({
      method: 'GET',
      url: `${BASE_URL}/plans/${planId}/actions`,
    });
  },

  /**
   * Get single action plan by ID
   * GET /api/v1/planning/actions/{action_id}
   */
  async getActionPlan(actionId: string): Promise<ActionPlan> {
    return apiClient.request<ActionPlan>({
      method: 'GET',
      url: `${BASE_URL}/actions/${actionId}`,
    });
  },

  /**
   * Update action plan
   * PUT /api/v1/planning/actions/{action_id}
   */
  async updateActionPlan(actionId: string, data: ActionPlanUpdate): Promise<ActionPlan> {
    return apiClient.request<ActionPlan>({
      method: 'PUT',
      url: `${BASE_URL}/actions/${actionId}`,
      data,
    });
  },

  /**
   * Delete action plan
   * DELETE /api/v1/planning/actions/{action_id}
   */
  async deleteActionPlan(actionId: string): Promise<void> {
    return apiClient.request<void>({
      method: 'DELETE',
      url: `${BASE_URL}/actions/${actionId}`,
    });
  },

  /**
   * Mark action plan as complete
   * POST /api/v1/planning/actions/{action_id}/complete
   * Sets status to completed and records completion date
   */
  async completeActionPlan(actionId: string, completionDate: string): Promise<ActionPlan> {
    return apiClient.request<ActionPlan>({
      method: 'POST',
      url: `${BASE_URL}/actions/${actionId}/complete`,
      data: { completion_date: completionDate },
    });
  },

  /**
   * Get actions by responsible user
   * GET /api/v1/planning/users/{user_id}/actions
   * Returns all actions assigned to a specific user
   */
  async getActionsByUser(userId: string, organizationId: string): Promise<ActionPlan[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<ActionPlan[]>({
      method: 'GET',
      url: `${BASE_URL}/users/${userId}/actions?${queryParams.toString()}`,
    });
  },

  /**
   * Get overdue actions
   * GET /api/v1/planning/actions/overdue
   * Returns all actions past their due date
   */
  async getOverdueActions(organizationId: string): Promise<ActionPlan[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<ActionPlan[]>({
      method: 'GET',
      url: `${BASE_URL}/actions/overdue?${queryParams.toString()}`,
    });
  },

  // ============= ANALYTICS (5 functions) =============

  /**
   * Get plan coverage statistics
   * GET /api/v1/planning/analytics/coverage
   * Returns coverage metrics across processes and risks
   */
  async getPlanCoverage(organizationId: string): Promise<PlanCoverage> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<PlanCoverage>({
      method: 'GET',
      url: `${BASE_URL}/analytics/coverage?${queryParams.toString()}`,
    });
  },

  /**
   * Get maturity assessment
   * GET /api/v1/planning/analytics/maturity
   * Returns BC maturity level and dimensional scores
   */
  async getMaturityAssessment(organizationId: string): Promise<MaturityAssessment> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<MaturityAssessment>({
      method: 'GET',
      url: `${BASE_URL}/analytics/maturity?${queryParams.toString()}`,
    });
  },

  /**
   * Get planning gaps
   * GET /api/v1/planning/analytics/gaps
   * Identifies missing plans, outdated plans, and resource gaps
   */
  async getPlanningGaps(organizationId: string): Promise<PlanningGap[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<PlanningGap[]>({
      method: 'GET',
      url: `${BASE_URL}/analytics/gaps?${queryParams.toString()}`,
    });
  },

  /**
   * Get implementation timeline
   * GET /api/v1/planning/analytics/timeline
   * Returns chronological events for planning activities
   */
  async getImplementationTimeline(organizationId: string, startDate?: string, endDate?: string): Promise<TimelineEvent[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);
    if (startDate) queryParams.append('start_date', startDate);
    if (endDate) queryParams.append('end_date', endDate);

    return apiClient.request<TimelineEvent[]>({
      method: 'GET',
      url: `${BASE_URL}/analytics/timeline?${queryParams.toString()}`,
    });
  },

  /**
   * Get executive summary
   * GET /api/v1/planning/analytics/executive-summary
   * Comprehensive dashboard data for leadership
   */
  async getExecutiveSummary(organizationId: string): Promise<ExecutiveSummary> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<ExecutiveSummary>({
      method: 'GET',
      url: `${BASE_URL}/analytics/executive-summary?${queryParams.toString()}`,
    });
  },

  // ============= INTEGRATION (4 functions) =============

  /**
   * Get BIA alignment
   * GET /api/v1/planning/integration/bia-alignment
   * Shows which processes have BC plans and RTO gaps
   */
  async getBIAAlignment(organizationId: string): Promise<BIAAlignment[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<BIAAlignment[]>({
      method: 'GET',
      url: `${BASE_URL}/integration/bia-alignment?${queryParams.toString()}`,
    });
  },

  /**
   * Get risk alignment
   * GET /api/v1/planning/integration/risk-alignment
   * Shows which risks have mitigation plans
   */
  async getRiskAlignment(organizationId: string): Promise<RiskAlignment[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<RiskAlignment[]>({
      method: 'GET',
      url: `${BASE_URL}/integration/risk-alignment?${queryParams.toString()}`,
    });
  },

  /**
   * Get plan dependencies
   * GET /api/v1/planning/plans/{plan_id}/dependencies
   * Returns what the plan depends on and what depends on it
   */
  async getPlanDependencies(planId: string): Promise<PlanDependency> {
    return apiClient.request<PlanDependency>({
      method: 'GET',
      url: `${BASE_URL}/plans/${planId}/dependencies`,
    });
  },

  /**
   * Sync planning data with other modules
   * POST /api/v1/planning/integration/sync
   * Synchronizes with BIA, Risk, and Asset modules
   */
  async syncPlanningData(organizationId: string, request: SyncRequest): Promise<SyncResult> {
    const queryParams = new URLSearchParams();
    queryParams.append('organization_id', organizationId);

    return apiClient.request<SyncResult>({
      method: 'POST',
      url: `${BASE_URL}/integration/sync?${queryParams.toString()}`,
      data: request,
    });
  },
};

// ==================== EXPORTED FUNCTIONS ====================

/**
 * Create BC plan
 */
export async function createBCPlan(data: BCPlanCreate): Promise<BCPlan> {
  return planningClient.createBCPlan(data);
}

/**
 * List BC plans
 */
export async function listBCPlans(params: ListBCPlansParams): Promise<ListBCPlansResponse> {
  return planningClient.listBCPlans(params);
}

/**
 * Get BC plan
 */
export async function getBCPlan(planId: string): Promise<BCPlan> {
  return planningClient.getBCPlan(planId);
}

/**
 * Update BC plan
 */
export async function updateBCPlan(planId: string, data: BCPlanUpdate): Promise<BCPlan> {
  return planningClient.updateBCPlan(planId, data);
}

/**
 * Delete BC plan
 */
export async function deleteBCPlan(planId: string): Promise<void> {
  return planningClient.deleteBCPlan(planId);
}

/**
 * Approve BC plan
 */
export async function approveBCPlan(planId: string, approvedBy: string): Promise<BCPlan> {
  return planningClient.approveBCPlan(planId, approvedBy);
}

/**
 * Activate BC plan
 */
export async function activateBCPlan(planId: string): Promise<BCPlan> {
  return planningClient.activateBCPlan(planId);
}

/**
 * Archive BC plan
 */
export async function archiveBCPlan(planId: string): Promise<BCPlan> {
  return planningClient.archiveBCPlan(planId);
}

/**
 * Get BC plan version history
 */
export async function getBCPlanVersionHistory(planId: string): Promise<PlanVersion[]> {
  return planningClient.getBCPlanVersionHistory(planId);
}

/**
 * Clone BC plan
 */
export async function cloneBCPlan(planId: string, newPlanName: string): Promise<BCPlan> {
  return planningClient.cloneBCPlan(planId, newPlanName);
}

/**
 * Create recovery strategy
 */
export async function createRecoveryStrategy(data: RecoveryStrategyCreate): Promise<RecoveryStrategy> {
  return planningClient.createRecoveryStrategy(data);
}

/**
 * List recovery strategies
 */
export async function listRecoveryStrategies(planId: string): Promise<RecoveryStrategy[]> {
  return planningClient.listRecoveryStrategies(planId);
}

/**
 * Get recovery strategy
 */
export async function getRecoveryStrategy(strategyId: string): Promise<RecoveryStrategy> {
  return planningClient.getRecoveryStrategy(strategyId);
}

/**
 * Update recovery strategy
 */
export async function updateRecoveryStrategy(strategyId: string, data: RecoveryStrategyUpdate): Promise<RecoveryStrategy> {
  return planningClient.updateRecoveryStrategy(strategyId, data);
}

/**
 * Delete recovery strategy
 */
export async function deleteRecoveryStrategy(strategyId: string): Promise<void> {
  return planningClient.deleteRecoveryStrategy(strategyId);
}

/**
 * Record strategy test
 */
export async function recordStrategyTest(strategyId: string, testData: StrategyTestResult): Promise<RecoveryStrategy> {
  return planningClient.recordStrategyTest(strategyId, testData);
}

/**
 * Get strategy effectiveness
 */
export async function getStrategyEffectiveness(strategyId: string): Promise<StrategyEffectiveness> {
  return planningClient.getStrategyEffectiveness(strategyId);
}

/**
 * Get strategies by process
 */
export async function getStrategiesByProcess(processId: string): Promise<RecoveryStrategy[]> {
  return planningClient.getStrategiesByProcess(processId);
}

/**
 * Create action plan
 */
export async function createActionPlan(data: ActionPlanCreate): Promise<ActionPlan> {
  return planningClient.createActionPlan(data);
}

/**
 * List action plans
 */
export async function listActionPlans(planId: string): Promise<ActionPlan[]> {
  return planningClient.listActionPlans(planId);
}

/**
 * Get action plan
 */
export async function getActionPlan(actionId: string): Promise<ActionPlan> {
  return planningClient.getActionPlan(actionId);
}

/**
 * Update action plan
 */
export async function updateActionPlan(actionId: string, data: ActionPlanUpdate): Promise<ActionPlan> {
  return planningClient.updateActionPlan(actionId, data);
}

/**
 * Delete action plan
 */
export async function deleteActionPlan(actionId: string): Promise<void> {
  return planningClient.deleteActionPlan(actionId);
}

/**
 * Complete action plan
 */
export async function completeActionPlan(actionId: string, completionDate: string): Promise<ActionPlan> {
  return planningClient.completeActionPlan(actionId, completionDate);
}

/**
 * Get actions by user
 */
export async function getActionsByUser(userId: string, organizationId: string): Promise<ActionPlan[]> {
  return planningClient.getActionsByUser(userId, organizationId);
}

/**
 * Get overdue actions
 */
export async function getOverdueActions(organizationId: string): Promise<ActionPlan[]> {
  return planningClient.getOverdueActions(organizationId);
}

/**
 * Get plan coverage
 */
export async function getPlanCoverage(organizationId: string): Promise<PlanCoverage> {
  return planningClient.getPlanCoverage(organizationId);
}

/**
 * Get maturity assessment
 */
export async function getMaturityAssessment(organizationId: string): Promise<MaturityAssessment> {
  return planningClient.getMaturityAssessment(organizationId);
}

/**
 * Get planning gaps
 */
export async function getPlanningGaps(organizationId: string): Promise<PlanningGap[]> {
  return planningClient.getPlanningGaps(organizationId);
}

/**
 * Get implementation timeline
 */
export async function getImplementationTimeline(organizationId: string, startDate?: string, endDate?: string): Promise<TimelineEvent[]> {
  return planningClient.getImplementationTimeline(organizationId, startDate, endDate);
}

/**
 * Get executive summary
 */
export async function getExecutiveSummary(organizationId: string): Promise<ExecutiveSummary> {
  return planningClient.getExecutiveSummary(organizationId);
}

/**
 * Get BIA alignment
 */
export async function getBIAAlignment(organizationId: string): Promise<BIAAlignment[]> {
  return planningClient.getBIAAlignment(organizationId);
}

/**
 * Get risk alignment
 */
export async function getRiskAlignment(organizationId: string): Promise<RiskAlignment[]> {
  return planningClient.getRiskAlignment(organizationId);
}

/**
 * Get plan dependencies
 */
export async function getPlanDependencies(planId: string): Promise<PlanDependency> {
  return planningClient.getPlanDependencies(planId);
}

/**
 * Sync planning data
 */
export async function syncPlanningData(organizationId: string, request: SyncRequest): Promise<SyncResult> {
  return planningClient.syncPlanningData(organizationId, request);
}

// Export default client
export default planningClient;
