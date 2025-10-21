/**
 * useFAIRAnalysis Hook
 * React Query hooks for FAIR (Factor Analysis of Information Risk) analysis
 * Real API integration via riskClient
 * Week 5 - Risk Assessment Module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type { FAIRAnalysis, FAIRAnalysisCreate } from '@/types/risk';
import toast from 'react-hot-toast';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for FAIR analysis
 * Provides centralized query key management
 */
export const fairKeys = {
  all: ['fair'] as const,
  detail: (riskId: string) => [...fairKeys.all, riskId] as const,
};

// ==================== TYPES ====================

/**
 * Options for useFAIRAnalysis query hook
 */
export interface UseFAIRAnalysisOptions {
  riskId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Options for usePerformFAIR mutation hook
 */
export interface UsePerformFAIROptions {
  onSuccess?: (data: FAIRAnalysis) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

// ==================== HOOKS ====================

/**
 * Hook to fetch FAIR analysis results for a risk
 * Retrieves quantitative risk assessment with Annual Loss Expectancy (ALE)
 *
 * @param options - Query options including riskId
 * @returns Query result with FAIR analysis data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: fairAnalysis, isLoading, error } = useFAIRAnalysis({
 *   riskId: 'risk-123',
 *   enabled: true,
 * });
 *
 * if (fairAnalysis) {
 *   console.log('Annual Loss Expectancy:', fairAnalysis.annual_loss_expectancy);
 *   console.log('Risk Rating:', fairAnalysis.risk_rating);
 *   console.log('Loss Event Frequency:', fairAnalysis.loss_event_frequency);
 * }
 * ```
 */
export function useFAIRAnalysis({
  riskId,
  enabled = true,
  staleTime,
  gcTime,
  refetchOnWindowFocus,
}: UseFAIRAnalysisOptions) {
  return useQuery({
    queryKey: fairKeys.detail(riskId),
    queryFn: () => riskClient.getFAIRAnalysis(riskId),

    // Enable/disable query
    enabled: enabled && !!riskId,

    // Caching strategy - analysis results are stable, don't change often
    staleTime: staleTime ?? 10 * 60 * 1000, // 10 minutes
    gcTime: gcTime ?? 30 * 60 * 1000, // 30 minutes

    // Control refetching
    refetchOnWindowFocus: refetchOnWindowFocus ?? false,

    // Error handling
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to perform FAIR analysis on a risk
 * Calculates Annual Loss Expectancy, risk rating, and confidence intervals
 *
 * @param riskId - Risk ID to analyze
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const performFAIR = usePerformFAIR('risk-123', {
 *   onSuccess: (analysis) => {
 *     toast.success(`FAIR analysis complete. ALE: $${analysis.annual_loss_expectancy}`);
 *     console.log('Risk Rating:', analysis.risk_rating);
 *   },
 *   onError: (error) => {
 *     toast.error(`Analysis failed: ${error.message}`);
 *   },
 * });
 *
 * // Execute FAIR analysis
 * performFAIR.mutate({
 *   threat_event_frequency: 12, // 12 events per year
 *   vulnerability_score: 0.7, // 70% probability
 *   primary_loss_min: 10000,
 *   primary_loss_max: 100000,
 *   primary_loss_most_likely: 50000,
 *   secondary_loss_min: 5000,
 *   secondary_loss_max: 50000,
 * });
 * ```
 */
export function usePerformFAIR(
  riskId: string,
  options: UsePerformFAIROptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FAIRAnalysisCreate) =>
      riskClient.performFAIRAnalysis(riskId, data),

    onSuccess: (data) => {
      // Update FAIR analysis cache with new results
      queryClient.setQueryData(fairKeys.detail(riskId), data);

      // Invalidate risk detail to reflect updated analysis
      queryClient.invalidateQueries({
        queryKey: ['risks', riskId],
      });

      // Show success notification
      toast.success(
        `FAIR analysis completed. ALE: $${data.annual_loss_expectancy.toLocaleString()}`
      );

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`FAIR analysis failed: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration
    retry: 1,
    retryDelay: 1000,
  });
}
