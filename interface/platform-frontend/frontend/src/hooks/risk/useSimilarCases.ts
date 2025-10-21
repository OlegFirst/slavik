/**
 * useSimilarCases Hook
 * React Query hook for finding similar risk cases using AI
 * Real API integration with Workflow Intelligence service
 * Week 5 - Risk Assessment Module
 */

import { useQuery } from '@tanstack/react-query';
import { riskClient, Risk } from '@/lib/api/risk-client';

/**
 * Query key factory for similar cases
 * Enables fine-grained cache management and invalidation
 */
export const similarCasesKeys = {
  all: ['similarCases'] as const,
  byRisk: (riskId: string, limit: number) => [...similarCasesKeys.all, riskId, limit] as const,
};

export interface UseSimilarCasesOptions {
  /**
   * Risk ID to find similar cases for
   * @required
   */
  riskId: string;
  /**
   * Maximum number of similar cases to return
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

export interface SimilarCase {
  risk: Risk;
  similarity_score: number;
  similarity_reasons: Array<{
    aspect: 'description' | 'category' | 'impact' | 'treatment' | 'outcome';
    match_strength: number;
    explanation: string;
  }>;
  outcome_summary?: {
    treatment_effectiveness: number;
    resolution_time_days: number;
    final_status: string;
    lessons_learned?: string[];
  };
}

export interface SimilarCasesResponse {
  reference_risk_id: string;
  total_similar_cases: number;
  similar_cases: SimilarCase[];
  search_metadata: {
    embedding_model: string;
    similarity_threshold: number;
    search_time_ms: number;
  };
  generated_at: string;
}

/**
 * Find similar risk cases using AI similarity search
 *
 * Uses vector embeddings and semantic similarity to find risks with:
 * - **Similar descriptions**: Text-based similarity using NLP embeddings
 * - **Similar categories/impacts**: Comparable risk profiles and severity levels
 * - **Similar treatment outcomes**: Risks that responded to similar interventions
 * - **Historical patterns**: Past cases that follow similar progression
 *
 * This helps risk managers:
 * - Learn from past cases when treating new risks
 * - Apply proven treatment strategies
 * - Estimate resolution timeframes
 * - Avoid repeated mistakes
 *
 * @param options - Configuration options
 * @returns React Query result with similar cases
 *
 * @example
 * ```tsx
 * // Basic usage - find 5 similar cases
 * const { data: similarCases, isLoading } = useSimilarCases({
 *   riskId: 'risk-123'
 * });
 *
 * // Request more similar cases
 * const { data: similarCases } = useSimilarCases({
 *   riskId: 'risk-123',
 *   limit: 10
 * });
 *
 * // Conditional fetching (only when viewing risk detail)
 * const { data: similarCases } = useSimilarCases({
 *   riskId: selectedRisk?.id || '',
 *   enabled: !!selectedRisk?.id && showSimilarCases
 * });
 *
 * // Display similar cases
 * {similarCases?.similar_cases.map(similar => (
 *   <SimilarCaseCard
 *     key={similar.risk.id}
 *     risk={similar.risk}
 *     similarityScore={Math.round(similar.similarity_score * 100)}
 *     reasons={similar.similarity_reasons}
 *     outcome={similar.outcome_summary}
 *   />
 * ))}
 * ```
 */
export function useSimilarCases(options: UseSimilarCasesOptions) {
  const { riskId, limit = 5, enabled = true } = options;

  return useQuery<SimilarCasesResponse>({
    queryKey: similarCasesKeys.byRisk(riskId, limit),
    queryFn: () => riskClient.getSimilarCases(riskId, { limit }),
    // Only run when riskId is provided and enabled is true
    enabled: enabled && !!riskId,
    // Similarity doesn't change often - cache for 30 minutes
    staleTime: 30 * 60 * 1000,
    // Keep in cache for 1 hour even when unused
    gcTime: 60 * 60 * 1000,
    // Similarity search is expensive, retry conservatively
    retry: 1,
    retryDelay: 3000,
  });
}

/**
 * Helper function to filter similar cases by minimum similarity score
 *
 * @param response - Similar cases response
 * @param minScore - Minimum similarity score threshold (0-1)
 * @default 0.7
 *
 * @example
 * ```tsx
 * const { data: similarCases } = useSimilarCases({ riskId: 'risk-123' });
 * const highSimilarity = filterBySimilarityScore(similarCases, 0.8);
 * ```
 */
export function filterBySimilarityScore(
  response: SimilarCasesResponse | undefined,
  minScore = 0.7
): SimilarCase[] {
  if (!response) return [];
  return response.similar_cases.filter(
    similar => similar.similarity_score >= minScore
  );
}

/**
 * Helper function to filter similar cases by specific similarity aspect
 *
 * @example
 * ```tsx
 * const { data: similarCases } = useSimilarCases({ riskId: 'risk-123' });
 * const treatmentSimilar = filterBySimilarityAspect(similarCases, 'treatment');
 * ```
 */
export function filterBySimilarityAspect(
  response: SimilarCasesResponse | undefined,
  aspect: SimilarCase['similarity_reasons'][0]['aspect']
): SimilarCase[] {
  if (!response) return [];
  return response.similar_cases.filter(similar =>
    similar.similarity_reasons.some(reason => reason.aspect === aspect)
  );
}

/**
 * Helper function to get the most effective treatment from similar cases
 *
 * @example
 * ```tsx
 * const { data: similarCases } = useSimilarCases({ riskId: 'risk-123' });
 * const bestTreatment = getMostEffectiveTreatment(similarCases);
 * ```
 */
export function getMostEffectiveTreatment(
  response: SimilarCasesResponse | undefined
): SimilarCase | null {
  if (!response || response.similar_cases.length === 0) return null;

  return response.similar_cases.reduce((best, current) => {
    const currentEffectiveness =
      current.outcome_summary?.treatment_effectiveness || 0;
    const bestEffectiveness =
      best.outcome_summary?.treatment_effectiveness || 0;

    return currentEffectiveness > bestEffectiveness ? current : best;
  }, response.similar_cases[0]);
}

/**
 * Helper function to calculate average resolution time from similar cases
 *
 * @example
 * ```tsx
 * const { data: similarCases } = useSimilarCases({ riskId: 'risk-123' });
 * const avgDays = getAverageResolutionTime(similarCases);
 * ```
 */
export function getAverageResolutionTime(
  response: SimilarCasesResponse | undefined
): number | null {
  if (!response || response.similar_cases.length === 0) return null;

  const casesWithOutcomes = response.similar_cases.filter(
    similar => similar.outcome_summary?.resolution_time_days
  );

  if (casesWithOutcomes.length === 0) return null;

  const total = casesWithOutcomes.reduce(
    (sum, similar) => sum + (similar.outcome_summary?.resolution_time_days || 0),
    0
  );

  return Math.round(total / casesWithOutcomes.length);
}

/**
 * Helper function to extract all lessons learned from similar cases
 *
 * @example
 * ```tsx
 * const { data: similarCases } = useSimilarCases({ riskId: 'risk-123' });
 * const lessons = getAllLessonsLearned(similarCases);
 * ```
 */
export function getAllLessonsLearned(
  response: SimilarCasesResponse | undefined
): string[] {
  if (!response) return [];

  const lessons: string[] = [];
  response.similar_cases.forEach(similar => {
    if (similar.outcome_summary?.lessons_learned) {
      lessons.push(...similar.outcome_summary.lessons_learned);
    }
  });

  // Remove duplicates
  return Array.from(new Set(lessons));
}
