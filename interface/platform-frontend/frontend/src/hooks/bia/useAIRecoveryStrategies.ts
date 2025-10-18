/**
 * useAIRecoveryStrategies Hook
 * AI-powered recovery strategy suggestions using BIA Specialist AI
 */

import { useMutation } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';

interface RecoveryStrategiesParams {
  name: string;
  rto_hours: number;
  dependencies?: any[];
  tenant_id?: string;
}

interface RecoveryStrategiesResult {
  strategies: any[];
  confidence: number;
  metadata: any;
}

export interface UseAIRecoveryStrategiesOptions {
  onSuccess?: (data: RecoveryStrategiesResult) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook to suggest recovery strategies using AI
 */
export function useAIRecoveryStrategies(
  options: UseAIRecoveryStrategiesOptions = {}
) {
  return useMutation({
    mutationFn: (params: RecoveryStrategiesParams) =>
      biaAPI.suggestRecoveryStrategies(params),

    onSuccess: options.onSuccess,
    onError: options.onError,
  });
}
