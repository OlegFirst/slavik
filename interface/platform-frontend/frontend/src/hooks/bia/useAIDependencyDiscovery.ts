/**
 * useAIDependencyDiscovery Hook
 * AI-powered dependency discovery using BIA Specialist AI
 */

import { useMutation } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';

interface DependencyDiscoveryParams {
  name: string;
  function?: string;
  tenant_id?: string;
}

interface DependencyDiscoveryResult {
  dependency_map: string;
  risks: any;
  confidence: number;
  metadata: any;
}

export interface UseAIDependencyDiscoveryOptions {
  onSuccess?: (data: DependencyDiscoveryResult) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook to discover dependencies using AI
 */
export function useAIDependencyDiscovery(
  options: UseAIDependencyDiscoveryOptions = {}
) {
  return useMutation({
    mutationFn: (params: DependencyDiscoveryParams) =>
      biaAPI.mapDependencies(params),

    onSuccess: options.onSuccess,
    onError: options.onError,
  });
}
