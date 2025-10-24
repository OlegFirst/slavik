/**
 * Compliance Module - Compatibility Layer
 *
 * This file provides type aliases and missing types to bridge differences
 * between Agent-generated types and hooks.
 *
 * TODO: Consolidate types into main compliance.ts file
 */

import type {
  ComplianceDashboard,
  ComplianceScore,
  ComplianceTrend,
  ComplianceTrendsResponse,
} from './compliance';

// Dashboard & Analytics type aliases
export type DashboardOverview = ComplianceDashboard;
export type AnalyticsData = ComplianceScore;

export interface RequirementsMatrix {
  requirements: Array<{
    requirement_id: string;
    requirement_name: string;
    clause: string;
    standard: string;
    category: string;
    compliance_status: string;
    coverage_percentage: number;
    evidence_count: number;
    gaps_count: number;
  }>;
}

export interface ComplianceRoadmap {
  milestones: Array<{
    milestone_id: string;
    milestone_name: string;
    target_date: string;
    status: 'not_started' | 'in_progress' | 'completed' | 'delayed';
    dependencies: string[];
    completion_percentage: number;
  }>;
}

export type AIAdvice = {
  recommendation_id: string;
  category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  recommendation: string;
  rationale: string;
  estimated_effort: string;
  expected_benefit: string;
};

export type BenchmarkData = {
  metric_name: string;
  your_value: number;
  industry_average: number;
  top_quartile: number;
  comparison: 'above' | 'at' | 'below';
};

export type ImprovementInitiative = {
  id: string;
  organization_id: string;
  title: string;
  description: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'critical' | 'high' | 'medium' | 'low';
  target_date?: string;
  completion_date?: string;
  actual_cost?: number;
  actual_benefits?: string[];
  created_at: string;
  updated_at: string;
};

export type ManagementReview = {
  id: string;
  organization_id: string;
  review_date: string;
  attendees: string[];
  decisions: string[];
  action_items: string[];
  status: 'scheduled' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
};

export type AssessmentResults = {
  assessment_id: string;
  total_requirements: number;
  compliant: number;
  partial: number;
  non_compliant: number;
  not_assessed: number;
  overall_score: number;
};

export type RCAAnalysis = {
  id: string;
  gap_id: string;
  root_causes: Array<{
    cause: string;
    category: string;
    description: string;
  }>;
  analysis_method: string;
  completed_at: string;
  created_at: string;
  updated_at: string;
};

export type RCAAnalysisCreate = {
  gap_id: string;
  root_causes: Array<{
    cause: string;
    category: string;
    description: string;
  }>;
  analysis_method: string;
};

export type EffectivenessReview = {
  id: string;
  gap_id: string;
  review_date: string;
  effectiveness_rating: number;
  findings: string;
  recommendations: string[];
  created_at: string;
  updated_at: string;
};
