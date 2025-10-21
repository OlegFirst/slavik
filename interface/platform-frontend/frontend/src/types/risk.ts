/**
 * Risk Assessment Module Types - Week 5 Implementation
 * Source: Risk Management Service (Port 8040)
 * ISO Standard: ISO 22301:2019 Clause 8.2.3
 * AI Platform ISO Project
 */

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Risk Category Enumeration
 * Comprehensive categorization of organizational risks
 */
export enum RiskCategory {
  OPERATIONAL = "operational",
  FINANCIAL = "financial",
  STRATEGIC = "strategic",
  COMPLIANCE = "compliance",
  REPUTATIONAL = "reputational",
  CYBERSECURITY = "cybersecurity",
  NATURAL_DISASTER = "natural_disaster"
}

/**
 * Risk Likelihood Enumeration (1-5 scale)
 * Probability assessment of risk occurrence
 */
export enum RiskLikelihood {
  RARE = 1,              // < 5% probability
  UNLIKELY = 2,          // 5-20% probability
  POSSIBLE = 3,          // 20-50% probability
  LIKELY = 4,            // 50-80% probability
  ALMOST_CERTAIN = 5     // > 80% probability
}

/**
 * Risk Impact Enumeration (1-5 scale)
 * Severity assessment of risk consequences
 */
export enum RiskImpact {
  INSIGNIFICANT = 1,
  MINOR = 2,
  MODERATE = 3,
  MAJOR = 4,
  CATASTROPHIC = 5
}

/**
 * Treatment Strategy Enumeration
 * Risk response strategies per ISO 31000
 */
export enum TreatmentStrategy {
  AVOID = "avoid",       // Eliminate the risk
  MITIGATE = "mitigate", // Reduce likelihood or impact
  TRANSFER = "transfer", // Share or transfer (e.g., insurance)
  ACCEPT = "accept"      // Accept the risk as-is
}

/**
 * Risk Status Enumeration
 * Lifecycle state of risk assessment
 */
export enum RiskStatus {
  IDENTIFIED = "identified",
  ANALYZING = "analyzing",
  TREATED = "treated",
  MONITORING = "monitoring",
  CLOSED = "closed"
}

// ============================================================================
// CORE INTERFACES
// ============================================================================

/**
 * Main Risk Interface
 * Primary risk assessment entity with complete metadata
 */
export interface Risk {
  id?: string;  // UUID
  organization_id: string;

  // Identification
  risk_title: string;
  risk_code?: string;  // Unique identifier (e.g., "RISK-2024-001")
  risk_category: RiskCategory;
  description: string;
  threat_source?: string;
  vulnerabilities: string[];

  // Analysis (1-5 scale)
  likelihood: RiskLikelihood;
  impact: RiskImpact;
  inherent_risk_score: number;  // likelihood × impact (1-25)

  // Treatment
  treatment_strategy?: TreatmentStrategy;
  residual_likelihood?: RiskLikelihood;
  residual_impact?: RiskImpact;
  residual_risk_score?: number;

  // Ownership & Review
  risk_owner_id?: string;
  status: RiskStatus;
  last_reviewed_at?: string;
  next_review_date?: string;

  // Relations
  related_processes: any[];
  related_assets: any[];

  // Metadata
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Risk Creation Payload
 * Required and optional fields for creating a new risk
 */
export interface RiskCreate {
  organization_id: string;
  risk_title: string;
  risk_code?: string;
  risk_category: RiskCategory;
  description: string;
  threat_source?: string;
  vulnerabilities: string[];
  likelihood: RiskLikelihood;
  impact: RiskImpact;
  treatment_strategy?: TreatmentStrategy;
  risk_owner_id?: string;
  status?: RiskStatus;
  related_processes?: any[];
  related_assets?: any[];
}

/**
 * Risk Update Payload
 * All fields optional for partial updates
 */
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
  last_reviewed_at?: string;
  next_review_date?: string;
  related_processes?: any[];
  related_assets?: any[];
  is_active?: boolean;
}

// ============================================================================
// FAIR ANALYSIS (Quantitative Risk Analysis)
// ============================================================================

/**
 * FAIR Analysis Interface
 * Factor Analysis of Information Risk (FAIR) methodology
 * Provides quantitative risk assessment with Annual Loss Expectancy (ALE)
 */
export interface FAIRAnalysis {
  risk_id: string;

  // Frequency
  threat_event_frequency: number;  // Threats per year
  vulnerability_score: number;     // Probability (0-1)
  loss_event_frequency: number;    // Calculated: TEF × Vulnerability

  // Loss Magnitude (triangular distribution)
  primary_loss_min: number;         // USD
  primary_loss_max: number;         // USD
  primary_loss_most_likely: number; // USD
  secondary_loss_min: number;       // USD
  secondary_loss_max: number;       // USD

  // Results
  annual_loss_expectancy: number;   // USD (ALE = LEF × Loss Magnitude)
  risk_rating: string;              // low/medium/high/critical
  confidence_interval_low: number;  // USD (95% CI)
  confidence_interval_high: number; // USD (95% CI)

  // Metadata
  analyzed_at?: string;
  analyzed_by?: string;
}

/**
 * FAIR Analysis Creation Payload
 * Parameters for performing FAIR analysis on a risk
 */
export interface FAIRAnalysisCreate {
  threat_event_frequency: number;
  vulnerability_score: number;
  primary_loss_min: number;
  primary_loss_max: number;
  primary_loss_most_likely: number;
  secondary_loss_min?: number;
  secondary_loss_max?: number;
}

// ============================================================================
// MONTE CARLO SIMULATION
// ============================================================================

/**
 * Monte Carlo Simulation Factor
 * Individual risk factor with triangular distribution
 */
export interface MonteCarloFactor {
  name?: string;
  min: number;
  most_likely: number;
  max: number;
}

/**
 * Monte Carlo Distribution Data
 * Statistical results from simulation
 */
export interface MonteCarloDistribution {
  histogram: number[];      // 50 bins
  bin_edges: number[];      // 51 edges
  min: number;
  max: number;
  std_dev: number;
}

/**
 * Monte Carlo Simulation Interface
 * Probabilistic risk analysis using triangular distributions
 * Provides Value at Risk (VaR) and Conditional VaR (CVaR)
 */
export interface MonteCarloSimulation {
  risk_id: string;
  iterations: number;  // 1000-100000, default 10000

  factors: MonteCarloFactor[];

  // Statistical Results
  mean_loss: number;
  median_loss: number;
  percentile_95: number;  // VaR (95th percentile)
  percentile_99: number;  // CVaR (99th percentile)

  distribution_data?: MonteCarloDistribution;

  // Metadata
  simulated_at?: string;
}

/**
 * Monte Carlo Simulation Creation Payload
 * Parameters for running simulation
 */
export interface MonteCarloSimulationCreate {
  iterations?: number;  // Default 10000
  factors: MonteCarloFactor[];
}

// ============================================================================
// TREATMENT PLANS
// ============================================================================

/**
 * Treatment Action Item
 * Individual action in a treatment plan
 */
export interface TreatmentAction {
  action?: string;
  responsible?: string;
  deadline?: string;
  status?: string;  // planned/in_progress/completed
}

/**
 * Risk Treatment Plan Interface
 * Detailed plan for risk mitigation and management
 */
export interface RiskTreatmentPlan {
  id?: string;
  risk_id: string;
  strategy: TreatmentStrategy;
  description: string;

  actions: TreatmentAction[];

  responsible_party?: string;
  start_date?: string;
  target_date?: string;
  completion_date?: string;

  estimated_cost?: number;
  actual_cost?: number;

  expected_residual_likelihood?: RiskLikelihood;
  expected_residual_impact?: RiskImpact;

  status: string;  // planned/in_progress/completed
  created_at?: string;
  updated_at?: string;
}

/**
 * Treatment Plan Creation Payload
 * Required fields for creating a new treatment plan
 */
export interface TreatmentPlanCreate {
  strategy: TreatmentStrategy;
  description: string;
  actions?: TreatmentAction[];
  responsible_party?: string;
  start_date?: string;
  target_date?: string;
  estimated_cost?: number;
  expected_residual_likelihood?: RiskLikelihood;
  expected_residual_impact?: RiskImpact;
}

/**
 * Treatment Plan Update Payload
 * All fields optional for partial updates
 */
export interface TreatmentPlanUpdate {
  strategy?: TreatmentStrategy;
  description?: string;
  actions?: TreatmentAction[];
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

// ============================================================================
// ANALYTICS & REPORTING
// ============================================================================

/**
 * Risk Matrix Position
 * Position of a risk on the 5x5 heat map
 */
export interface RiskMatrixPosition {
  risk_id: string;
  risk_title: string;
  likelihood: number;  // 1-5
  impact: number;      // 1-5
  score: number;       // 1-25
  severity: RiskSeverity;
  category: RiskCategory;
}

/**
 * Risk Heat Map Data
 * Complete 5x5 matrix with risk counts and positions
 */
export interface RiskHeatMap {
  matrix: number[][];  // 5x5 array of risk counts
  risks_by_cell: Record<string, RiskMatrixPosition[]>;  // Key: "likelihood_impact"
  total_risks: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

/**
 * Risk Trend Daily Data Point
 * Daily snapshot of risk metrics
 */
export interface RiskTrendDataPoint {
  date: string;
  total_risks: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  avg_score: number;
}

/**
 * Risk Trends Analysis
 * Time-series analysis of risk metrics
 */
export interface RiskTrends {
  start_date: string;
  end_date: string;
  days: number;
  daily_data: RiskTrendDataPoint[];
  overall_trend: 'increasing' | 'decreasing' | 'stable';
  avg_score_change: number;
  total_risks_change: number;
}

/**
 * Risk Report
 * Comprehensive analytics and dashboard data
 */
export interface RiskReport {
  organization_id: string;
  generated_at: string;

  // Summary Statistics
  total_risks: number;
  active_risks: number;
  closed_risks: number;

  // By Severity
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;

  // By Status
  status_breakdown: Record<RiskStatus, number>;

  // By Category
  category_breakdown: Record<RiskCategory, number>;

  // Average Scores
  avg_inherent_score: number;
  avg_residual_score: number;

  // Treatment
  total_treatment_plans: number;
  treatment_strategy_breakdown: Record<TreatmentStrategy, number>;

  // High Priority Risks
  top_risks: Risk[];

  // Trends
  trend_7d?: number;   // 7-day change in avg score
  trend_30d?: number;  // 30-day change in avg score
}

/**
 * Risk Filters
 * Filter parameters for risk list queries
 */
export interface RiskFilters {
  category?: RiskCategory | RiskCategory[];
  status?: RiskStatus | RiskStatus[];
  severity?: RiskSeverity | RiskSeverity[];
  min_score?: number;
  max_score?: number;
  risk_owner_id?: string;
  search?: string;
  is_active?: boolean;
}

// ============================================================================
// HELPER TYPES
// ============================================================================

/**
 * Risk Severity Type
 * Calculated severity level based on score
 */
export type RiskSeverity = 'low' | 'medium' | 'high' | 'critical';

/**
 * FAIR Risk Rating Type
 * Risk level based on Annual Loss Expectancy
 */
export type FAIRRiskRating = 'low' | 'medium' | 'high' | 'critical';

/**
 * Treatment Plan Status Type
 * Execution status of treatment plan
 */
export type TreatmentPlanStatus = 'planned' | 'in_progress' | 'completed';

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Risk Severity Thresholds
 * Score ranges for severity classification
 * Score = Likelihood × Impact (1-25)
 */
export const RISK_SEVERITY_THRESHOLDS = {
  CRITICAL: { min: 20, max: 25 },
  HIGH: { min: 15, max: 19 },
  MEDIUM: { min: 8, max: 14 },
  LOW: { min: 1, max: 7 }
} as const;

/**
 * FAIR Risk Rating Thresholds
 * Annual Loss Expectancy ranges (USD)
 */
export const FAIR_RISK_RATING_THRESHOLDS = {
  LOW: { max: 10000 },
  MEDIUM: { min: 10000, max: 100000 },
  HIGH: { min: 100000, max: 1000000 },
  CRITICAL: { min: 1000000 }
} as const;

/**
 * Severity Color Classes
 * Tailwind CSS classes for visual representation
 */
export const SEVERITY_COLORS = {
  CRITICAL: {
    bg: "bg-red-100",
    text: "text-red-800",
    border: "border-red-300",
    badge: "bg-red-600 text-white"
  },
  HIGH: {
    bg: "bg-orange-100",
    text: "text-orange-800",
    border: "border-orange-300",
    badge: "bg-orange-600 text-white"
  },
  MEDIUM: {
    bg: "bg-yellow-100",
    text: "text-yellow-800",
    border: "border-yellow-300",
    badge: "bg-yellow-600 text-white"
  },
  LOW: {
    bg: "bg-green-100",
    text: "text-green-800",
    border: "border-green-300",
    badge: "bg-green-600 text-white"
  }
} as const;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Calculate risk score from likelihood and impact
 * @param likelihood - Risk likelihood (1-5)
 * @param impact - Risk impact (1-5)
 * @returns Risk score (1-25)
 */
export function calculateRiskScore(likelihood: number, impact: number): number {
  return likelihood * impact;
}

/**
 * Get severity level from risk score
 * @param score - Risk score (1-25)
 * @returns Severity level
 */
export function getRiskSeverity(score: number): RiskSeverity {
  if (score >= RISK_SEVERITY_THRESHOLDS.CRITICAL.min) {
    return 'critical';
  }
  if (score >= RISK_SEVERITY_THRESHOLDS.HIGH.min) {
    return 'high';
  }
  if (score >= RISK_SEVERITY_THRESHOLDS.MEDIUM.min) {
    return 'medium';
  }
  return 'low';
}

/**
 * Get FAIR risk rating from Annual Loss Expectancy
 * @param ale - Annual Loss Expectancy (USD)
 * @returns FAIR risk rating
 */
export function getFAIRRiskRating(ale: number): FAIRRiskRating {
  if (ale >= FAIR_RISK_RATING_THRESHOLDS.CRITICAL.min) {
    return 'critical';
  }
  if (ale >= FAIR_RISK_RATING_THRESHOLDS.HIGH.min) {
    return 'high';
  }
  if (ale >= FAIR_RISK_RATING_THRESHOLDS.MEDIUM.min) {
    return 'medium';
  }
  return 'low';
}

/**
 * Get severity color classes for styling
 * @param severity - Risk severity level
 * @returns Object with Tailwind CSS classes
 */
export function getSeverityColor(severity: RiskSeverity): {
  bg: string;
  text: string;
  border: string;
  badge: string
} {
  const severityKey = severity.toUpperCase() as keyof typeof SEVERITY_COLORS;
  return SEVERITY_COLORS[severityKey] || SEVERITY_COLORS.LOW;
}

/**
 * Format currency value
 * @param value - Numeric value in USD
 * @returns Formatted currency string
 */
export function formatCurrency(value: number): string {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`;
  }
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(1)}K`;
  }
  return `$${value.toFixed(2)}`;
}

/**
 * Format percentage value
 * @param value - Numeric value (0-1 or 0-100)
 * @returns Formatted percentage string
 */
export function formatPercentage(value: number): string {
  // Handle both 0-1 and 0-100 ranges
  const percentage = value <= 1 ? value * 100 : value;
  return `${percentage.toFixed(1)}%`;
}

/**
 * Get likelihood label from numeric value
 * @param likelihood - Likelihood value (1-5)
 * @returns Human-readable label
 */
export function getLikelihoodLabel(likelihood: RiskLikelihood): string {
  const labels: Record<RiskLikelihood, string> = {
    [RiskLikelihood.RARE]: 'Rare',
    [RiskLikelihood.UNLIKELY]: 'Unlikely',
    [RiskLikelihood.POSSIBLE]: 'Possible',
    [RiskLikelihood.LIKELY]: 'Likely',
    [RiskLikelihood.ALMOST_CERTAIN]: 'Almost Certain'
  };
  return labels[likelihood] || 'Unknown';
}

/**
 * Get impact label from numeric value
 * @param impact - Impact value (1-5)
 * @returns Human-readable label
 */
export function getImpactLabel(impact: RiskImpact): string {
  const labels: Record<RiskImpact, string> = {
    [RiskImpact.INSIGNIFICANT]: 'Insignificant',
    [RiskImpact.MINOR]: 'Minor',
    [RiskImpact.MODERATE]: 'Moderate',
    [RiskImpact.MAJOR]: 'Major',
    [RiskImpact.CATASTROPHIC]: 'Catastrophic'
  };
  return labels[impact] || 'Unknown';
}

/**
 * Get category label with proper formatting
 * @param category - Risk category enum value
 * @returns Human-readable label
 */
export function getCategoryLabel(category: RiskCategory): string {
  const labels: Record<RiskCategory, string> = {
    [RiskCategory.OPERATIONAL]: 'Operational',
    [RiskCategory.FINANCIAL]: 'Financial',
    [RiskCategory.STRATEGIC]: 'Strategic',
    [RiskCategory.COMPLIANCE]: 'Compliance',
    [RiskCategory.REPUTATIONAL]: 'Reputational',
    [RiskCategory.CYBERSECURITY]: 'Cybersecurity',
    [RiskCategory.NATURAL_DISASTER]: 'Natural Disaster'
  };
  return labels[category] || 'Unknown';
}

/**
 * Get status label with proper formatting
 * @param status - Risk status enum value
 * @returns Human-readable label
 */
export function getStatusLabel(status: RiskStatus): string {
  const labels: Record<RiskStatus, string> = {
    [RiskStatus.IDENTIFIED]: 'Identified',
    [RiskStatus.ANALYZING]: 'Analyzing',
    [RiskStatus.TREATED]: 'Treated',
    [RiskStatus.MONITORING]: 'Monitoring',
    [RiskStatus.CLOSED]: 'Closed'
  };
  return labels[status] || 'Unknown';
}

/**
 * Get treatment strategy label with proper formatting
 * @param strategy - Treatment strategy enum value
 * @returns Human-readable label
 */
export function getStrategyLabel(strategy: TreatmentStrategy): string {
  const labels: Record<TreatmentStrategy, string> = {
    [TreatmentStrategy.AVOID]: 'Avoid',
    [TreatmentStrategy.MITIGATE]: 'Mitigate',
    [TreatmentStrategy.TRANSFER]: 'Transfer',
    [TreatmentStrategy.ACCEPT]: 'Accept'
  };
  return labels[strategy] || 'Unknown';
}
