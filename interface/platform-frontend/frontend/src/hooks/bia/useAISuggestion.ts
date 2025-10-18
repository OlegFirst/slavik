/**
 * useAISuggestion Hook
 * React Query hook for AI-powered RTO suggestions
 * Real API integration with BIA Specialist AI via biaAPI.getAISuggestion
 */

import { useMutation } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import type { AIRTOSuggestion, CriticalityLevel } from '@/types/bia';

export interface AIRTOSuggestionParams {
  name: string;
  industry: string;
  criticality: CriticalityLevel;
  financial_impact: Record<string, number>;
  staff_count?: number;
}

export interface UseAISuggestionOptions {
  onSuccess?: (data: AIRTOSuggestion) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

/**
 * Hook to get AI-powered RTO/RPO/MTPD suggestions
 * Uses BIA Specialist AI from intelligent_core for analysis
 *
 * @param options - Callback options
 * @returns Mutation result with AI suggestion data
 *
 * @example
 * ```tsx
 * const getAISuggestion = useAISuggestion({
 *   onSuccess: (suggestion) => {
 *     // Auto-fill form with AI suggestions
 *     setValue('rto_hours', suggestion.suggested_rto_hours);
 *     setValue('rpo_hours', suggestion.suggested_rpo_hours);
 *     setValue('mtpd_hours', suggestion.suggested_mtpd_hours);
 *     setValue('ai_recommendations', suggestion.reasoning);
 *
 *     toast.success(
 *       `AI Suggestion: RTO ${suggestion.suggested_rto_hours}h (${Math.round(suggestion.confidence * 100)}% confidence)`
 *     );
 *   },
 *   onError: (error) => {
 *     toast.error(`AI analysis failed: ${error.message}`);
 *   }
 * });
 *
 * // When user clicks "Get AI Suggestion"
 * getAISuggestion.mutate({
 *   name: 'Patient Admission Process',
 *   industry: 'healthcare',
 *   criticality: CriticalityLevel.CRITICAL,
 *   financial_impact: {
 *     '1_hour': 5000,
 *     '4_hours': 20000,
 *     '24_hours': 100000,
 *     '7_days': 500000
 *   },
 *   staff_count: 50
 * });
 * ```
 */
export function useAISuggestion(options: UseAISuggestionOptions = {}) {
  return useMutation({
    mutationFn: (params: AIRTOSuggestionParams) =>
      biaAPI.getAISuggestion(params),

    onSuccess: (data) => {
      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // AI calls can take time, increase timeout tolerance
    retry: 1,
    retryDelay: 2000,
  });
}

/**
 * Hook variant with automatic form field population
 * Returns helper to apply suggestions to React Hook Form
 *
 * @example
 * ```tsx
 * const { mutate: getAISuggestion, applySuggestion } = useAISuggestionWithForm(setValue);
 *
 * getAISuggestion({
 *   name: form.watch('name'),
 *   industry: form.watch('industry'),
 *   criticality: form.watch('criticality'),
 *   financial_impact: form.watch('financial_impact'),
 *   staff_count: form.watch('staff_count')
 * });
 * ```
 */
export function useAISuggestionWithForm(
  setValue: any, // React Hook Form setValue
  options: UseAISuggestionOptions = {}
) {
  const mutation = useAISuggestion({
    ...options,
    onSuccess: (data) => {
      // Auto-populate form fields
      setValue('rto_hours', data.suggested_rto_hours);

      if (data.suggested_rpo_hours !== undefined) {
        setValue('rpo_hours', data.suggested_rpo_hours);
      }

      if (data.suggested_mtpd_hours !== undefined) {
        setValue('mtpd_hours', data.suggested_mtpd_hours);
      }

      if (data.reasoning) {
        setValue('ai_recommendations', data.reasoning);
        setValue('ai_confidence', data.confidence);
        setValue('ai_suggested_rto', data.suggested_rto_hours);
      }

      options.onSuccess?.(data);
    },
  });

  return {
    ...mutation,
    applySuggestion: (suggestion: AIRTOSuggestion) => {
      setValue('rto_hours', suggestion.suggested_rto_hours);
      if (suggestion.suggested_rpo_hours !== undefined) {
        setValue('rpo_hours', suggestion.suggested_rpo_hours);
      }
      if (suggestion.suggested_mtpd_hours !== undefined) {
        setValue('mtpd_hours', suggestion.suggested_mtpd_hours);
      }
      if (suggestion.reasoning) {
        setValue('ai_recommendations', suggestion.reasoning);
        setValue('ai_confidence', suggestion.confidence);
      }
    },
  };
}

/**
 * Parse AI suggestion confidence into user-friendly label
 */
export function getConfidenceLabel(confidence: number): {
  label: string;
  color: string;
} {
  if (confidence >= 0.9) {
    return { label: 'Very High', color: 'green' };
  } else if (confidence >= 0.75) {
    return { label: 'High', color: 'blue' };
  } else if (confidence >= 0.6) {
    return { label: 'Medium', color: 'yellow' };
  } else {
    return { label: 'Low', color: 'orange' };
  }
}

/**
 * Check if AI suggestion should be trusted based on confidence
 */
export function shouldTrustSuggestion(confidence: number): boolean {
  return confidence >= 0.7;
}
