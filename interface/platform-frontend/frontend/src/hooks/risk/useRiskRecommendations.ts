/**
 * useRiskRecommendations Hook
 * React Query hook for AI-powered risk management recommendations
 * Real API integration with Workflow Intelligence service
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';

/**
 * Query key factory for risk recommendations
 * Enables fine-grained cache management and invalidation
 */
export const recommendationsKeys = {
  all: ['riskRecommendations'] as const,
  limited: (limit: number) => [...recommendationsKeys.all, limit] as const,
};

export interface UseRiskRecommendationsOptions {
  /**
   * Maximum number of recommendations to return
   * @default 5
   */
  limit?: number;
  /**
   * Enable/disable the query
   * Set to false to prevent automatic fetching
   * @default true
   */
  enabled?: boolean;
}

export interface RiskRecommendation {
  recommendation_id: string;
  title: string;
  description: string;
  recommendation_type: 'treatment' | 'priority' | 'resource_allocation' | 'compliance';
  priority: 'urgent' | 'high' | 'medium' | 'low';
  confidence: number;
  impacted_risks: string[];
  suggested_actions: Array<{
    action: string;
    estimated_effort: string;
    expected_impact: string;
  }>;
  estimated_risk_reduction?: number;
  compliance_frameworks?: string[];
  rationale: string;
}

export interface RiskRecommendationsResponse {
  total_recommendations: number;
  recommendations: RiskRecommendation[];
  summary: {
    treatment_strategies: number;
    priority_rankings: number;
    resource_allocations: number;
    compliance_reminders: number;
  };
  generated_at: string;
}

/**
 * Fetch AI-powered recommendations for risk management
 *
 * Uses Workflow Intelligence to provide actionable recommendations including:
 * - **Suggested treatment strategies**: Optimal approaches to mitigate specific risks
 * - **Priority rankings**: AI-driven prioritization based on impact and likelihood
 * - **Resource allocation advice**: Guidance on where to focus limited resources
 * - **Compliance reminders**: Proactive alerts about regulatory requirements
 *
 * @param options - Configuration options
 * @returns React Query result with AI recommendations
 *
 * @example
 * ```tsx
 * // Basic usage - top 5 recommendations
 * const { data: recommendations, isLoading } = useRiskRecommendations();
 *
 * // Request more recommendations
 * const { data: recommendations } = useRiskRecommendations({ limit: 10 });
 *
 * // Conditional fetching
 * const { data: recommendations } = useRiskRecommendations({
 *   limit: 5,
 *   enabled: shouldFetchAIRecommendations
 * });
 *
 * // Display recommendations
 * {recommendations?.recommendations.map(rec => (
 *   <RecommendationCard
 *     key={rec.recommendation_id}
 *     title={rec.title}
 *     priority={rec.priority}
 *     confidence={Math.round(rec.confidence * 100)}
 *     actions={rec.suggested_actions}
 *   />
 * ))}
 * ```
 */
export function useRiskRecommendations(options?: UseRiskRecommendationsOptions) {
  const limit = options?.limit || 5;

  return useQuery<RiskRecommendationsResponse>({
    queryKey: recommendationsKeys.limited(limit),
    queryFn: () => riskClient.getAIRecommendations({ limit }),
    enabled: options?.enabled ?? true,
    // AI recommendations change less frequently - cache for 15 minutes
    staleTime: 15 * 60 * 1000,
    // Keep in cache for 45 minutes even when unused
    gcTime: 45 * 60 * 1000,
    // AI requests are expensive, retry conservatively
    retry: 1,
    retryDelay: 3000,
  });
}

/**
 * Helper function to filter recommendations by priority
 *
 * @example
 * ```tsx
 * const { data: recommendations } = useRiskRecommendations();
 * const urgentRecs = filterRecommendationsByPriority(recommendations, 'urgent');
 * ```
 */
export function filterRecommendationsByPriority(
  response: RiskRecommendationsResponse | undefined,
  priority: RiskRecommendation['priority']
): RiskRecommendation[] {
  if (!response) return [];
  return response.recommendations.filter(rec => rec.priority === priority);
}

/**
 * Helper function to filter recommendations by type
 *
 * @example
 * ```tsx
 * const { data: recommendations } = useRiskRecommendations();
 * const complianceRecs = filterRecommendationsByType(recommendations, 'compliance');
 * ```
 */
export function filterRecommendationsByType(
  response: RiskRecommendationsResponse | undefined,
  type: RiskRecommendation['recommendation_type']
): RiskRecommendation[] {
  if (!response) return [];
  return response.recommendations.filter(rec => rec.recommendation_type === type);
}

/**
 * Helper function to get high-confidence recommendations only
 *
 * @param response - Recommendations response
 * @param minConfidence - Minimum confidence threshold (0-1)
 * @default 0.7
 *
 * @example
 * ```tsx
 * const { data: recommendations } = useRiskRecommendations();
 * const trustedRecs = getHighConfidenceRecommendations(recommendations, 0.8);
 * ```
 */
export function getHighConfidenceRecommendations(
  response: RiskRecommendationsResponse | undefined,
  minConfidence = 0.7
): RiskRecommendation[] {
  if (!response) return [];
  return response.recommendations.filter(rec => rec.confidence >= minConfidence);
}

/**
 * Helper function to get recommendations for a specific risk
 *
 * @example
 * ```tsx
 * const { data: recommendations } = useRiskRecommendations();
 * const riskRecs = getRecommendationsForRisk(recommendations, 'risk-123');
 * ```
 */
export function getRecommendationsForRisk(
  response: RiskRecommendationsResponse | undefined,
  riskId: string
): RiskRecommendation[] {
  if (!response) return [];
  return response.recommendations.filter(rec =>
    rec.impacted_risks.includes(riskId)
  );
}

/**
 * Helper function to calculate total estimated risk reduction
 *
 * @example
 * ```tsx
 * const { data: recommendations } = useRiskRecommendations();
 * const totalReduction = calculateTotalRiskReduction(recommendations);
 * ```
 */
export function calculateTotalRiskReduction(
  response: RiskRecommendationsResponse | undefined
): number {
  if (!response) return 0;
  return response.recommendations.reduce(
    (total, rec) => total + (rec.estimated_risk_reduction || 0),
    0
  );
}
