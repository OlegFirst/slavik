/**
 * Planning Module - Types & Enums
 * ISO 22301:2019 Clause 8.3 - Business Continuity Strategies and Solutions
 * AI Platform ISO Project
 *
 * Created: 2025-10-21
 * Agent: 1/3 (Planning Module Round 1)
 */

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Plan Type Enumeration
 * Classification of business continuity plans by organizational level
 */
export enum PlanType {
  STRATEGIC = "strategic",
  TACTICAL = "tactical",
  OPERATIONAL = "operational"
}

/**
 * Strategy Type Enumeration
 * Risk treatment and continuity strategy categories
 */
export enum StrategyType {
  PREVENTION = "prevention",
  MITIGATION = "mitigation",
  RECOVERY = "recovery",
  TRANSFER = "transfer"
}

/**
 * Plan Status Enumeration
 * Lifecycle state of business continuity plans
 */
export enum PlanStatus {
  DRAFT = "draft",
  REVIEW = "review",
  APPROVED = "approved",
  ACTIVE = "active",
  ARCHIVED = "archived"
}

/**
 * Action Type Enumeration
 * Classification of action items within plans
 */
export enum ActionType {
  PREVENTIVE = "preventive",
  DETECTIVE = "detective",
  CORRECTIVE = "corrective",
  RECOVERY = "recovery"
}

/**
 * Priority Enumeration
 * Priority level classification for plans and actions
 */
export enum Priority {
  CRITICAL = "critical",
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low"
}

/**
 * Action Status Enumeration
 * Execution status of action items
 */
export enum ActionStatus {
  NOT_STARTED = "not_started",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  DELAYED = "delayed",
  CANCELLED = "cancelled"
}

// ============================================================================
// SUPPORTING TYPES
// ============================================================================

/**
 * Resource Interface
 * Represents resources required for plan execution
 */
export interface Resource {
  resource_type: 'personnel' | 'equipment' | 'facility' | 'technology' | 'financial';
  resource_name: string;
  quantity?: number;
  cost_estimate?: number;
  availability: 'available' | 'limited' | 'unavailable';
}

/**
 * Recovery Step Interface
 * Individual step in a recovery strategy sequence
 */
export interface RecoveryStep {
  step_number: number;
  step_title: string;
  description: string;
  estimated_duration: number; // minutes
  responsible_role: string;
  dependencies?: number[]; // step numbers
}

/**
 * Personnel Interface
 * Personnel resources and contact information
 */
export interface Personnel {
  role: string;
  name?: string;
  contact_info?: string;
  availability: 'primary' | 'backup' | 'on-call';
}

/**
 * Equipment Interface
 * Equipment and hardware resources
 */
export interface Equipment {
  equipment_type: string;
  equipment_name: string;
  location?: string;
  quantity: number;
}

/**
 * Facility Interface
 * Physical facility resources
 */
export interface Facility {
  facility_type: 'primary' | 'alternate' | 'mobile';
  facility_name: string;
  address?: string;
  capacity?: number;
}

// ============================================================================
// MAIN INTERFACES
// ============================================================================

/**
 * BCPlan Interface
 * Business Continuity Plan - primary planning entity
 * Comprehensive plan for business continuity management
 */
export interface BCPlan {
  id: string;
  organization_id: string;

  // Metadata
  plan_name: string;
  plan_code: string;
  plan_type: PlanType;
  plan_version: string;

  // Scope
  scope_description: string;
  applicable_processes: string[];
  applicable_assets: string[];
  covered_risks: string[];

  // Objectives (ISO 22301:2019 recovery time objectives)
  rto_target: number; // Recovery Time Objective (minutes)
  rpo_target: number; // Recovery Point Objective (minutes)
  mtpd_target: number; // Maximum Tolerable Period of Disruption (minutes)

  // Strategy
  strategy_type: StrategyType;
  strategy_description: string;

  // Resources
  required_resources: Resource[];
  estimated_cost: number;

  // Status & Review
  status: PlanStatus;
  approved_by?: string;
  approved_at?: string;
  last_reviewed_at?: string;
  next_review_date?: string;

  // Metadata
  created_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * Recovery Strategy Interface
 * Detailed recovery strategy with steps and resources
 * Defines how to recover from disruptions
 */
export interface RecoveryStrategy {
  id: string;
  plan_id: string;

  strategy_name: string;
  strategy_type: StrategyType;
  description: string;

  // Timeline
  activation_trigger: string;
  activation_time: number; // minutes
  recovery_steps: RecoveryStep[];

  // Resources
  required_personnel: Personnel[];
  required_equipment: Equipment[];
  required_facilities: Facility[];

  // Testing & Validation
  last_tested_at?: string;
  test_results?: string;
  effectiveness_rating?: number; // 1-5 scale

  // Metadata
  created_at: string;
  updated_at: string;
}

/**
 * Action Plan Interface
 * Action items and tasks within business continuity plans
 * Tracks execution of specific activities
 */
export interface ActionPlan {
  id: string;
  plan_id: string;

  action_title: string;
  action_type: ActionType;
  priority: Priority;

  // Details
  description: string;
  responsible_party: string;
  backup_responsible?: string;

  // Timeline
  start_date?: string;
  target_date?: string;
  completion_date?: string;

  // Progress Tracking
  status: ActionStatus;
  progress_percentage: number;

  // Dependencies
  depends_on: string[];
  blocks: string[];

  // Metadata
  created_at: string;
  updated_at: string;
}

// ============================================================================
// CREATE/UPDATE TYPES
// ============================================================================

/**
 * BCPlan Creation Payload
 * Required and optional fields for creating a new BC plan
 */
export type BCPlanCreate = Omit<BCPlan, 'id' | 'created_at' | 'updated_at'>;

/**
 * BCPlan Update Payload
 * All fields optional for partial updates
 */
export type BCPlanUpdate = Partial<BCPlanCreate>;

/**
 * Recovery Strategy Creation Payload
 * Required fields for creating a new recovery strategy
 */
export type RecoveryStrategyCreate = Omit<RecoveryStrategy, 'id' | 'created_at' | 'updated_at'>;

/**
 * Recovery Strategy Update Payload
 * All fields optional for partial updates
 */
export type RecoveryStrategyUpdate = Partial<RecoveryStrategyCreate>;

/**
 * Action Plan Creation Payload
 * Required fields for creating a new action plan
 */
export type ActionPlanCreate = Omit<ActionPlan, 'id' | 'created_at' | 'updated_at'>;

/**
 * Action Plan Update Payload
 * All fields optional for partial updates
 */
export type ActionPlanUpdate = Partial<ActionPlanCreate>;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get plan type label with proper formatting
 * @param type - Plan type enum value
 * @returns Human-readable label
 */
export function getPlanTypeLabel(type: PlanType): string {
  switch (type) {
    case PlanType.STRATEGIC:
      return 'Strategic';
    case PlanType.TACTICAL:
      return 'Tactical';
    case PlanType.OPERATIONAL:
      return 'Operational';
    default:
      return 'Unknown';
  }
}

/**
 * Get plan type color for visual representation
 * @param type - Plan type enum value
 * @returns Tailwind CSS color class
 */
export function getPlanTypeColor(type: PlanType): string {
  switch (type) {
    case PlanType.STRATEGIC:
      return 'blue-600';
    case PlanType.TACTICAL:
      return 'indigo-500';
    case PlanType.OPERATIONAL:
      return 'blue-500';
    default:
      return 'gray-500';
  }
}

/**
 * Get strategy type label with proper formatting
 * @param type - Strategy type enum value
 * @returns Human-readable label
 */
export function getStrategyTypeLabel(type: StrategyType): string {
  switch (type) {
    case StrategyType.PREVENTION:
      return 'Prevention';
    case StrategyType.MITIGATION:
      return 'Mitigation';
    case StrategyType.RECOVERY:
      return 'Recovery';
    case StrategyType.TRANSFER:
      return 'Transfer';
    default:
      return 'Unknown';
  }
}

/**
 * Get strategy type color for visual representation
 * @param type - Strategy type enum value
 * @returns Tailwind CSS color class
 */
export function getStrategyTypeColor(type: StrategyType): string {
  switch (type) {
    case StrategyType.PREVENTION:
      return 'green-600';
    case StrategyType.MITIGATION:
      return 'teal-500';
    case StrategyType.RECOVERY:
      return 'green-500';
    case StrategyType.TRANSFER:
      return 'teal-600';
    default:
      return 'gray-500';
  }
}

/**
 * Get plan status label with proper formatting
 * @param status - Plan status enum value
 * @returns Human-readable label
 */
export function getPlanStatusLabel(status: PlanStatus): string {
  switch (status) {
    case PlanStatus.DRAFT:
      return 'Draft';
    case PlanStatus.REVIEW:
      return 'In Review';
    case PlanStatus.APPROVED:
      return 'Approved';
    case PlanStatus.ACTIVE:
      return 'Active';
    case PlanStatus.ARCHIVED:
      return 'Archived';
    default:
      return 'Unknown';
  }
}

/**
 * Get plan status color for visual representation
 * @param status - Plan status enum value
 * @returns Tailwind CSS color class
 */
export function getPlanStatusColor(status: PlanStatus): string {
  switch (status) {
    case PlanStatus.DRAFT:
      return 'gray-500';
    case PlanStatus.REVIEW:
      return 'yellow-500';
    case PlanStatus.APPROVED:
      return 'green-500';
    case PlanStatus.ACTIVE:
      return 'blue-600';
    case PlanStatus.ARCHIVED:
      return 'gray-400';
    default:
      return 'gray-500';
  }
}

/**
 * Get action type label with proper formatting
 * @param type - Action type enum value
 * @returns Human-readable label
 */
export function getActionTypeLabel(type: ActionType): string {
  switch (type) {
    case ActionType.PREVENTIVE:
      return 'Preventive';
    case ActionType.DETECTIVE:
      return 'Detective';
    case ActionType.CORRECTIVE:
      return 'Corrective';
    case ActionType.RECOVERY:
      return 'Recovery';
    default:
      return 'Unknown';
  }
}

/**
 * Get action type color for visual representation
 * @param type - Action type enum value
 * @returns Tailwind CSS color class
 */
export function getActionTypeColor(type: ActionType): string {
  switch (type) {
    case ActionType.PREVENTIVE:
      return 'purple-600';
    case ActionType.DETECTIVE:
      return 'pink-500';
    case ActionType.CORRECTIVE:
      return 'purple-500';
    case ActionType.RECOVERY:
      return 'pink-600';
    default:
      return 'gray-500';
  }
}

/**
 * Get priority label with proper formatting
 * @param priority - Priority enum value
 * @returns Human-readable label
 */
export function getPriorityLabel(priority: Priority): string {
  switch (priority) {
    case Priority.CRITICAL:
      return 'Critical';
    case Priority.HIGH:
      return 'High';
    case Priority.MEDIUM:
      return 'Medium';
    case Priority.LOW:
      return 'Low';
    default:
      return 'Unknown';
  }
}

/**
 * Get priority color for visual representation
 * @param priority - Priority enum value
 * @returns Tailwind CSS color class
 */
export function getPriorityColor(priority: Priority): string {
  switch (priority) {
    case Priority.CRITICAL:
      return 'red-600';
    case Priority.HIGH:
      return 'orange-500';
    case Priority.MEDIUM:
      return 'yellow-500';
    case Priority.LOW:
      return 'gray-500';
    default:
      return 'gray-400';
  }
}

/**
 * Get action status label with proper formatting
 * @param status - Action status enum value
 * @returns Human-readable label
 */
export function getActionStatusLabel(status: ActionStatus): string {
  switch (status) {
    case ActionStatus.NOT_STARTED:
      return 'Not Started';
    case ActionStatus.IN_PROGRESS:
      return 'In Progress';
    case ActionStatus.COMPLETED:
      return 'Completed';
    case ActionStatus.DELAYED:
      return 'Delayed';
    case ActionStatus.CANCELLED:
      return 'Cancelled';
    default:
      return 'Unknown';
  }
}

/**
 * Get action status color for visual representation
 * @param status - Action status enum value
 * @returns Tailwind CSS color class
 */
export function getActionStatusColor(status: ActionStatus): string {
  switch (status) {
    case ActionStatus.NOT_STARTED:
      return 'gray-500';
    case ActionStatus.IN_PROGRESS:
      return 'blue-600';
    case ActionStatus.COMPLETED:
      return 'green-600';
    case ActionStatus.DELAYED:
      return 'red-500';
    case ActionStatus.CANCELLED:
      return 'gray-400';
    default:
      return 'gray-500';
  }
}
