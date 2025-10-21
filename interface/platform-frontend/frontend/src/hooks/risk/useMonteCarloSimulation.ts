/**
 * useMonteCarloSimulation Hook
 * React Query hooks for Monte Carlo probabilistic risk simulations
 * Real API integration via riskClient
 * Week 5 - Risk Assessment Module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskClient } from '@/lib/api/risk-client';
import type { MonteCarloSimulation, MonteCarloSimulationCreate } from '@/types/risk';
import toast from 'react-hot-toast';

// ==================== QUERY KEYS ====================

/**
 * Query key factory for Monte Carlo simulations
 * Provides centralized query key management
 */
export const monteCarloKeys = {
  all: ['monteCarlo'] as const,
  detail: (riskId: string) => [...monteCarloKeys.all, riskId] as const,
};

// ==================== TYPES ====================

/**
 * Options for useMonteCarlo query hook
 */
export interface UseMonteCarloOptions {
  riskId: string;
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Options for useRunMonteCarlo mutation hook
 */
export interface UseRunMonteCarloOptions {
  onSuccess?: (data: MonteCarloSimulation) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

// ==================== HOOKS ====================

/**
 * Hook to fetch Monte Carlo simulation results for a risk
 * Retrieves probabilistic analysis with VaR, CVaR, and distribution data
 *
 * @param options - Query options including riskId
 * @returns Query result with simulation data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: simulation, isLoading, error } = useMonteCarlo({
 *   riskId: 'risk-123',
 *   enabled: true,
 * });
 *
 * if (simulation) {
 *   console.log('Mean Loss:', simulation.mean_loss);
 *   console.log('Median Loss:', simulation.median_loss);
 *   console.log('VaR (95%):', simulation.percentile_95);
 *   console.log('CVaR (99%):', simulation.percentile_99);
 *   console.log('Iterations:', simulation.iterations);
 * }
 * ```
 */
export function useMonteCarlo({
  riskId,
  enabled = true,
  staleTime,
  gcTime,
  refetchOnWindowFocus,
}: UseMonteCarloOptions) {
  return useQuery({
    queryKey: monteCarloKeys.detail(riskId),
    queryFn: () => riskClient.getMonteCarloSimulation(riskId),

    // Enable/disable query
    enabled: enabled && !!riskId,

    // Caching strategy - simulation results are stable, don't change often
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
 * Hook to run Monte Carlo simulation on a risk
 * Performs probabilistic analysis using triangular distributions
 *
 * @param riskId - Risk ID to simulate
 * @param options - Callback options
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const runSimulation = useRunMonteCarlo('risk-123', {
 *   onSuccess: (result) => {
 *     toast.success(`Simulation complete (${result.iterations} iterations)`);
 *     console.log('VaR (95%):', result.percentile_95);
 *     console.log('CVaR (99%):', result.percentile_99);
 *   },
 *   onError: (error) => {
 *     toast.error(`Simulation failed: ${error.message}`);
 *   },
 * });
 *
 * // Execute Monte Carlo simulation
 * runSimulation.mutate({
 *   iterations: 10000, // Default: 10,000
 *   factors: [
 *     {
 *       name: 'Loss Magnitude',
 *       min: 10000,
 *       most_likely: 50000,
 *       max: 100000,
 *     },
 *     {
 *       name: 'Frequency',
 *       min: 1,
 *       most_likely: 5,
 *       max: 12,
 *     },
 *   ],
 * });
 * ```
 */
export function useRunMonteCarlo(
  riskId: string,
  options: UseRunMonteCarloOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: MonteCarloSimulationCreate) =>
      riskClient.runMonteCarloSimulation(riskId, data),

    onSuccess: (data) => {
      // Update simulation cache with new results
      queryClient.setQueryData(monteCarloKeys.detail(riskId), data);

      // Invalidate risk detail to reflect updated simulation
      queryClient.invalidateQueries({
        queryKey: ['risks', riskId],
      });

      // Show success notification with key metrics
      toast.success(
        `Monte Carlo simulation completed (${data.iterations.toLocaleString()} iterations)`
      );

      options.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error notification
      toast.error(`Simulation failed: ${error.message}`);
      options.onError?.(error);
    },

    onSettled: () => {
      options.onSettled?.();
    },

    // Retry configuration - simulations can be resource-intensive
    retry: 1,
    retryDelay: 2000,
  });
}
