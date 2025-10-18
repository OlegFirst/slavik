/**
 * useAIImpactCalculation Hook
 * AI-powered impact calculation using BIA Specialist AI
 */

import { useMutation } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';

interface ImpactCalculationParams {
  name: string;
  daily_revenue?: number;
  customers?: number;
  tenant_id?: string;
}

interface ImpactCalculationResult {
  impact_curve: string;
  critical_timeframes: any;
  confidence: number;
  metadata: any;
}

export interface UseAIImpactCalculationOptions {
  onSuccess?: (data: ImpactCalculationResult) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook to calculate impact over time using AI
 */
export function useAIImpactCalculation(
  options: UseAIImpactCalculationOptions = {}
) {
  return useMutation({
    mutationFn: (params: ImpactCalculationParams) =>
      biaAPI.calculateImpactOverTime(params),

    onSuccess: options.onSuccess,
    onError: options.onError,
  });
}
