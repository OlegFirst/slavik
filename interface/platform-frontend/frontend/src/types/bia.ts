/**
 * BIA Types - Generated from backend models
 * Source: /platform_services/bia_service/models/
 */

export enum CriticalityLevel {
  LOW = 'low',
  MINOR = 'minor',
  MODERATE = 'moderate',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ProcessStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

export enum ReputationalImpact {
  NONE = 'none',
  MINOR = 'minor',
  MODERATE = 'moderate',
  MAJOR = 'major',
  CATASTROPHIC = 'catastrophic'
}

export enum RegulatoryImpact {
  NO_VIOLATIONS = 'no_violations',
  MINOR_VIOLATIONS = 'minor_violations',
  MAJOR_VIOLATIONS = 'major_violations',
  LICENSE_AT_RISK = 'license_at_risk',
  CRIMINAL_LIABILITY = 'criminal_liability'
}

export enum PatientSafetyImpact {
  NO_IMPACT = 'no_impact',
  DELAYED_CARE = 'delayed_care',
  COMPROMISED_QUALITY = 'compromised_quality',
  PATIENT_HARM_PROBABLE = 'patient_harm_probable',
  LIFE_THREATENING = 'life_threatening'
}

export enum WHOTier {
  TIER_1 = 'tier_1', // IMMEDIATE - RTO: 0 minutes
  TIER_2 = 'tier_2', // URGENT - RTO: 2-4 hours
  TIER_3 = 'tier_3', // IMPORTANT - RTO: 24 hours
  TIER_4 = 'tier_4'  // NORMAL - RTO: 3-5 days
}

export enum GeographicalScope {
  LOCAL = 'local',
  REGIONAL = 'regional',
  NATIONAL = 'national',
  GLOBAL = 'global'
}

export enum IndustryType {
  HEALTHCARE = 'healthcare',
  FINANCIAL = 'financial',
  MANUFACTURING = 'manufacturing',
  RETAIL = 'retail',
  IT = 'it',
  ENERGY = 'energy',
  TRANSPORT = 'transport',
  GOVERNMENT = 'government',
  EDUCATION = 'education',
  OTHER = 'other'
}

export interface Dependency {
  type: string; // process, technology, people, facility, supplier
  name: string;
  id?: number;
  criticality?: number; // 1-5
  required: boolean;
}

export interface BIAProcess {
  id?: number;
  tenant_id: string;
  name: string;
  description?: string;
  department?: string;
  process_owner?: string;

  // Criticality
  criticality: CriticalityLevel;
  criticality_score?: number; // 1-5
  who_tier?: WHOTier;

  // Industry context
  industry?: IndustryType;
  geographical_scope?: GeographicalScope;

  // Time Objectives
  rto_hours: number;
  rpo_hours: number;
  mtpd_hours: number;

  // Impact Assessment
  financial_impact?: Record<string, number>; // {1_hour: 5000, 4_hours: 20000, ...}
  operational_impact?: Record<string, string>;
  reputational_impact?: ReputationalImpact;
  regulatory_impact?: RegulatoryImpact;
  patient_safety_impact?: PatientSafetyImpact;

  // ISO 22301 Compliance Fields
  compliance_objective?: string;
  legal_regulatory_requirements?: string[];

  // Resource Requirements
  personnel_requirements?: Record<string, any>;
  facility_requirements?: Record<string, any>;
  technology_requirements?: Record<string, any>;
  information_requirements?: Record<string, any>;

  // Recovery Strategies
  recovery_strategies?: Array<Record<string, any>>;
  alternative_procedures?: string[];
  workaround_capacity?: number; // 0-100%

  // Dependencies
  upstream_processes?: string[];
  downstream_processes?: string[];
  critical_suppliers?: Array<Record<string, any>>;
  dependencies: Dependency[];
  resources_required: Array<Record<string, any>>;

  // Operating Characteristics
  minimum_resource_level?: Record<string, any>;
  peak_periods?: Array<Record<string, any>>;
  seasonality?: string;

  // ISO 22301 Assessment Results
  bia_completion_date?: string;
  bia_assessor?: string;
  bia_reviewer?: string;
  next_review_date?: string;

  // Process metrics
  annual_revenue_impact?: number;
  peak_concurrent_users?: number;
  staff_count?: number;

  // AI Analysis results
  ai_suggested_rto?: number;
  ai_confidence?: number;
  ai_recommendations?: string;

  // Status
  status: ProcessStatus;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BIAProcessCreate {
  tenant_id: string;
  name: string;
  description?: string;
  department?: string;
  process_owner?: string;
  criticality: CriticalityLevel;
  industry?: IndustryType;
  rto_hours: number;
  rpo_hours: number;
  mtpd_hours: number;
  financial_impact?: Record<string, number>;
  operational_impact?: Record<string, string>;
  dependencies?: Dependency[];

  // Optional ISO 22301 fields
  compliance_objective?: string;
  legal_regulatory_requirements?: string[];
  personnel_requirements?: Record<string, any>;
  facility_requirements?: Record<string, any>;
  technology_requirements?: Record<string, any>;
  information_requirements?: Record<string, any>;
  recovery_strategies?: Array<Record<string, any>>;
  alternative_procedures?: string[];
  workaround_capacity?: number;
  upstream_processes?: string[];
  downstream_processes?: string[];
  critical_suppliers?: Array<Record<string, any>>;
  minimum_resource_level?: Record<string, any>;
  peak_periods?: Array<Record<string, any>>;
  seasonality?: string;
  bia_completion_date?: string;
  bia_assessor?: string;
  bia_reviewer?: string;
  next_review_date?: string;
}

export interface AIRTOSuggestion {
  suggested_rto_hours: number;
  suggested_rpo_hours?: number;
  suggested_mtpd_hours?: number;
  confidence: number; // 0-1
  reasoning: string;
  benchmarks?: Record<string, number>;
}

export interface BIASummaryReport {
  tenant_id: string;
  total_processes: number;
  critical_processes: number;
  average_rto_hours: number;
  total_potential_loss_24h: number;
  top_critical_processes: Array<Record<string, any>>;
  bia_completion_rate: number;
}

export interface BulkOperationReport {
  total_count: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  total_duration_ms: number;
  successes: any[];
  failures: Array<{
    item: any;
    error: string;
  }>;
}
