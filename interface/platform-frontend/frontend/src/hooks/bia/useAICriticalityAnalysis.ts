/**
 * useAICriticalityAnalysis Hook
 * AI-powered process criticality analysis using BIA Specialist AI
 */

import { useMutation } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';

interface CriticalityAnalysisParams {
  name: string;
  description?: string;
  department?: string;
  revenue_impact?: number;
  regulatory?: boolean;
  customer_impact?: string;
  tenant_id?: string;
}

interface CriticalityAnalysisResult {
  criticality_analysis: string;
  recommendations: any;
  confidence: number;
  metadata: any;
}

export interface UseAICriticalityAnalysisOptions {
  onSuccess?: (data: CriticalityAnalysisResult) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook to analyze process criticality using AI
 */
export function useAICriticalityAnalysis(
  options: UseAICriticalityAnalysisOptions = {}
) {
  return useMutation({
    mutationFn: (params: CriticalityAnalysisParams) =>
      biaAPI.analyzeProcessCriticality(params),

    onSuccess: options.onSuccess,
    onError: options.onError,
  });
}
