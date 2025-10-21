/**
 * React Hook for Orchestrator Health Monitoring
 * ==============================================
 */

import { useQuery } from '@tanstack/react-query';
import { orchestratorAPI } from '@/services/orchestrator-api';

export const useOrchestratorHealth = (refreshInterval: number = 5000) => {
  return useQuery({
    queryKey: ['orchestrator', 'health'],
    queryFn: () => orchestratorAPI.getHealth(),
    refetchInterval: refreshInterval,
    retry: 3,
    retryDelay: 1000,
  });
};

export const useOrchestratorStats = (refreshInterval: number = 10000) => {
  return useQuery({
    queryKey: ['orchestrator', 'stats'],
    queryFn: () => orchestratorAPI.getStats(),
    refetchInterval: refreshInterval,
    retry: 2,
  });
};
