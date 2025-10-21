/**
 * useRiskInsights Hook
 * React Query hook for AI-generated risk insights
 * Real API integration with Workflow Intelligence service
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';

/**
 * Query key factory for risk insights
 * Enables fine-grained cache management and invalidation
 */
export const insightsKeys = {
  all: ['riskInsights'] as const,
  byPeriod: (days: number) => [...insightsKeys.all, days] as const,
};

export interface UseRiskInsightsOptions {
  /**
   * Number of days to analyze for insights
   * @default 30
   */
  days?: number;
  /**
   * Enable/disable the query
   * Set to false to prevent automatic fetching
   * @default true
   */
  enabled?: boolean;
}

export interface RiskInsight {
  insight_type: 'emerging_pattern' | 'anomaly' | 'risk_cluster' | 'predictive_alert';
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  confidence: number;
  affected_risks?: string[];
  recommendation?: string;
  data?: Record<string, any>;
}

export interface RiskInsightsResponse {
  period_days: number;
  total_insights: number;
  insights: RiskInsight[];
  summary: {
    emerging_patterns: number;
    anomalies_detected: number;
    risk_clusters: number;
    predictive_alerts: number;
  };
  generated_at: string;
}

/**
 * Fetch AI-generated insights about risks
 *
 * Uses Workflow Intelligence to analyze risk data and provide:
 * - **Emerging risk patterns**: Identifies new trends in risk occurrences
 * - **Anomaly detection**: Flags unusual risk behaviors requiring attention
 * - **Risk clustering**: Groups related risks for holistic treatment
 * - **Predictive alerts**: Forecasts potential future risk scenarios
 *
 * @param options - Configuration options
 * @returns React Query result with AI insights
 *
 * @example
 * ```tsx
 * // Basic usage - last 30 days
 * const { data: insights, isLoading } = useRiskInsights();
 *
 * // Custom time period
 * const { data: insights } = useRiskInsights({ days: 90 });
 *
 * // Conditional fetching
 * const { data: insights } = useRiskInsights({
 *   days: 60,
 *   enabled: userHasAIAccess
 * });
 *
 * // Display insights
 * {insights?.insights.map(insight => (
 *   <InsightCard
 *     key={insight.title}
 *     type={insight.insight_type}
 *     title={insight.title}
 *     description={insight.description}
 *     severity={insight.severity}
 *     confidence={Math.round(insight.confidence * 100)}
 *   />
 * ))}
 * ```
 */
export function useRiskInsights(options?: UseRiskInsightsOptions) {
  const days = options?.days || 30;

  return useQuery<RiskInsightsResponse>({
    queryKey: insightsKeys.byPeriod(days),
    queryFn: () => riskClient.getWorkflowInsights({ days }),
    enabled: options?.enabled ?? true,
    // AI insights are computationally expensive - cache for 10 minutes
    staleTime: 10 * 60 * 1000,
    // Keep in cache for 30 minutes even when unused
    gcTime: 30 * 60 * 1000,
    // Don't retry failed AI requests too aggressively
    retry: 1,
    retryDelay: 3000,
  });
}

/**
 * Helper function to filter insights by severity
 *
 * @example
 * ```tsx
 * const { data: insights } = useRiskInsights();
 * const criticalInsights = filterInsightsBySeverity(insights, 'critical');
 * ```
 */
export function filterInsightsBySeverity(
  response: RiskInsightsResponse | undefined,
  severity: RiskInsight['severity']
): RiskInsight[] {
  if (!response) return [];
  return response.insights.filter(insight => insight.severity === severity);
}

/**
 * Helper function to filter insights by type
 *
 * @example
 * ```tsx
 * const { data: insights } = useRiskInsights();
 * const anomalies = filterInsightsByType(insights, 'anomaly');
 * ```
 */
export function filterInsightsByType(
  response: RiskInsightsResponse | undefined,
  type: RiskInsight['insight_type']
): RiskInsight[] {
  if (!response) return [];
  return response.insights.filter(insight => insight.insight_type === type);
}

/**
 * Helper function to get high-confidence insights only
 *
 * @param response - Insights response
 * @param minConfidence - Minimum confidence threshold (0-1)
 * @default 0.75
 *
 * @example
 * ```tsx
 * const { data: insights } = useRiskInsights();
 * const trustedInsights = getHighConfidenceInsights(insights, 0.8);
 * ```
 */
export function getHighConfidenceInsights(
  response: RiskInsightsResponse | undefined,
  minConfidence = 0.75
): RiskInsight[] {
  if (!response) return [];
  return response.insights.filter(insight => insight.confidence >= minConfidence);
}
