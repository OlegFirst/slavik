/**
 * useRiskPatterns Hook
 * React Query hook for analyzing risk patterns over time using AI/ML
 * Real API integration with Workflow Intelligence service
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';

/**
 * Query key factory for risk patterns
 * Enables fine-grained cache management and invalidation
 */
export const patternsKeys = {
  all: ['riskPatterns'] as const,
  byPeriod: (days: number) => [...patternsKeys.all, days] as const,
};

export interface UseRiskPatternsOptions {
  /**
   * Number of days to analyze for patterns
   * @default 90
   */
  days?: number;
  /**
   * Enable/disable the query
   * Set to false to prevent automatic fetching
   * @default true
   */
  enabled?: boolean;
}

export interface RiskTheme {
  theme: string;
  frequency: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  related_categories: string[];
  example_risk_ids: string[];
}

export interface SeasonalTrend {
  period: string;
  risk_count: number;
  average_severity: number;
  dominant_categories: string[];
  notes?: string;
}

export interface CategoryCorrelation {
  category_pair: [string, string];
  correlation_strength: number;
  co_occurrence_count: number;
  interpretation: string;
}

export interface TreatmentEffectiveness {
  strategy: string;
  total_uses: number;
  success_rate: number;
  average_resolution_days: number;
  best_suited_for: string[];
  effectiveness_trend: 'improving' | 'declining' | 'stable';
}

export interface RiskPatternsResponse {
  analysis_period_days: number;
  total_risks_analyzed: number;
  patterns: {
    recurring_themes: RiskTheme[];
    seasonal_trends: SeasonalTrend[];
    category_correlations: CategoryCorrelation[];
    treatment_effectiveness: TreatmentEffectiveness[];
  };
  key_findings: string[];
  recommendations: string[];
  generated_at: string;
}

/**
 * Analyze risk patterns using AI/ML
 *
 * Uses Workflow Intelligence to identify patterns across historical risk data:
 * - **Recurring risk themes**: Common risk scenarios that appear repeatedly
 * - **Seasonal trends**: Time-based patterns (quarterly spikes, year-end issues)
 * - **Category correlations**: Risk categories that frequently occur together
 * - **Effectiveness of treatments**: Which strategies work best for different risks
 *
 * This helps organizations:
 * - Proactively prepare for predictable risk patterns
 * - Optimize resource allocation based on seasonal trends
 * - Understand systemic risk relationships
 * - Choose the most effective treatment strategies
 *
 * @param options - Configuration options
 * @returns React Query result with pattern analysis
 *
 * @example
 * ```tsx
 * // Basic usage - analyze last 90 days
 * const { data: patterns, isLoading } = useRiskPatterns();
 *
 * // Custom time period - analyze last 6 months
 * const { data: patterns } = useRiskPatterns({ days: 180 });
 *
 * // Conditional fetching
 * const { data: patterns } = useRiskPatterns({
 *   days: 90,
 *   enabled: userHasAnalyticsAccess
 * });
 *
 * // Display recurring themes
 * {patterns?.patterns.recurring_themes.map(theme => (
 *   <ThemeCard
 *     key={theme.theme}
 *     title={theme.theme}
 *     frequency={theme.frequency}
 *     trend={theme.trend}
 *     categories={theme.related_categories}
 *   />
 * ))}
 *
 * // Show treatment effectiveness
 * {patterns?.patterns.treatment_effectiveness.map(treatment => (
 *   <EffectivenessChart
 *     strategy={treatment.strategy}
 *     successRate={treatment.success_rate}
 *     avgResolutionDays={treatment.average_resolution_days}
 *     trend={treatment.effectiveness_trend}
 *   />
 * ))}
 * ```
 */
export function useRiskPatterns(options?: UseRiskPatternsOptions) {
  const days = options?.days || 90;

  return useQuery<RiskPatternsResponse>({
    queryKey: patternsKeys.byPeriod(days),
    queryFn: () => riskClient.analyzePatterns({ days }),
    enabled: options?.enabled ?? true,
    // Pattern analysis is expensive and changes slowly - cache for 20 minutes
    staleTime: 20 * 60 * 1000,
    // Keep in cache for 1 hour even when unused
    gcTime: 60 * 60 * 1000,
    // Pattern analysis is computationally intensive, retry conservatively
    retry: 1,
    retryDelay: 5000,
  });
}

/**
 * Helper function to get increasing risk themes
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const emergingThemes = getIncreasingThemes(patterns);
 * ```
 */
export function getIncreasingThemes(
  response: RiskPatternsResponse | undefined
): RiskTheme[] {
  if (!response) return [];
  return response.patterns.recurring_themes.filter(
    theme => theme.trend === 'increasing'
  );
}

/**
 * Helper function to get most effective treatment strategies
 *
 * @param response - Patterns response
 * @param minSuccessRate - Minimum success rate threshold (0-1)
 * @default 0.7
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const bestTreatments = getMostEffectiveTreatments(patterns, 0.8);
 * ```
 */
export function getMostEffectiveTreatments(
  response: RiskPatternsResponse | undefined,
  minSuccessRate = 0.7
): TreatmentEffectiveness[] {
  if (!response) return [];
  return response.patterns.treatment_effectiveness
    .filter(treatment => treatment.success_rate >= minSuccessRate)
    .sort((a, b) => b.success_rate - a.success_rate);
}

/**
 * Helper function to get strong category correlations
 *
 * @param response - Patterns response
 * @param minStrength - Minimum correlation strength (0-1)
 * @default 0.6
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const strongCorrelations = getStrongCorrelations(patterns, 0.7);
 * ```
 */
export function getStrongCorrelations(
  response: RiskPatternsResponse | undefined,
  minStrength = 0.6
): CategoryCorrelation[] {
  if (!response) return [];
  return response.patterns.category_correlations
    .filter(correlation => correlation.correlation_strength >= minStrength)
    .sort((a, b) => b.correlation_strength - a.correlation_strength);
}

/**
 * Helper function to get seasonal trends for a specific period
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const q4Trend = getSeasonalTrendByPeriod(patterns, 'Q4');
 * ```
 */
export function getSeasonalTrendByPeriod(
  response: RiskPatternsResponse | undefined,
  period: string
): SeasonalTrend | undefined {
  if (!response) return undefined;
  return response.patterns.seasonal_trends.find(
    trend => trend.period.includes(period)
  );
}

/**
 * Helper function to find best treatment for a specific category
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const bestForCyber = getBestTreatmentForCategory(patterns, 'cybersecurity');
 * ```
 */
export function getBestTreatmentForCategory(
  response: RiskPatternsResponse | undefined,
  category: string
): TreatmentEffectiveness | undefined {
  if (!response) return undefined;

  const relevantTreatments = response.patterns.treatment_effectiveness.filter(
    treatment => treatment.best_suited_for.includes(category)
  );

  if (relevantTreatments.length === 0) return undefined;

  return relevantTreatments.reduce((best, current) =>
    current.success_rate > best.success_rate ? current : best
  );
}

/**
 * Helper function to calculate average risk severity over the period
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const avgSeverity = getAverageSeverity(patterns);
 * ```
 */
export function getAverageSeverity(
  response: RiskPatternsResponse | undefined
): number | null {
  if (!response || response.patterns.seasonal_trends.length === 0) return null;

  const total = response.patterns.seasonal_trends.reduce(
    (sum, trend) => sum + trend.average_severity,
    0
  );

  return Number((total / response.patterns.seasonal_trends.length).toFixed(2));
}

/**
 * Helper function to identify declining treatment strategies
 *
 * @example
 * ```tsx
 * const { data: patterns } = useRiskPatterns();
 * const decliningStrategies = getDecliningTreatments(patterns);
 * ```
 */
export function getDecliningTreatments(
  response: RiskPatternsResponse | undefined
): TreatmentEffectiveness[] {
  if (!response) return [];
  return response.patterns.treatment_effectiveness.filter(
    treatment => treatment.effectiveness_trend === 'declining'
  );
}
