/**
 * useBIASummary Hook
 * React Query hook for BIA summary reports and analytics
 * Real API integration via biaAPI.getSummaryReport
 */

import { useQuery } from '@tanstack/react-query';
import { biaAPI } from '@/lib/api/bia-client';
import type { BIASummaryReport } from '@/types/bia';

export interface UseBIASummaryOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchInterval?: number;
  refetchOnWindowFocus?: boolean;
}

/**
 * Hook to fetch BIA summary report for tenant
 * Provides high-level analytics and statistics
 *
 * @param tenant_id - Tenant identifier
 * @param options - React Query options
 * @returns Query result with summary data
 *
 * @example
 * ```tsx
 * const { data: summary, isLoading } = useBIASummary('org-123');
 *
 * if (summary) {
 *   return (
 *     <div>
 *       <h2>BIA Summary</h2>
 *       <p>Total Processes: {summary.total_processes}</p>
 *       <p>Critical Processes: {summary.critical_processes}</p>
 *       <p>Average RTO: {summary.average_rto_hours}h</p>
 *       <p>24h Loss Potential: ${summary.total_potential_loss_24h.toLocaleString()}</p>
 *       <p>Completion Rate: {(summary.bia_completion_rate * 100).toFixed(1)}%</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useBIASummary(
  tenant_id: string,
  options: UseBIASummaryOptions = {}
) {
  return useQuery({
    queryKey: ['bia', 'summary', tenant_id],
    queryFn: () => biaAPI.getSummaryReport(tenant_id),

    // Summary changes less frequently, cache longer
    staleTime: options.staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: options.gcTime ?? 60 * 60 * 1000, // 1 hour

    // Optional auto-refetch for dashboard
    refetchInterval: options.refetchInterval ?? false,
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,

    enabled: options.enabled ?? true,

    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook variant with real-time updates
 * Useful for dashboards that need live data
 *
 * @example
 * ```tsx
 * const { data: summary } = useBIASummaryLive('org-123', {
 *   refetchInterval: 30000 // Refresh every 30 seconds
 * });
 * ```
 */
export function useBIASummaryLive(
  tenant_id: string,
  options: UseBIASummaryOptions = {}
) {
  return useBIASummary(tenant_id, {
    ...options,
    refetchInterval: options.refetchInterval ?? 30000, // 30s default
    refetchOnWindowFocus: true,
    staleTime: 0, // Always consider stale for live updates
  });
}

/**
 * Calculate completion percentage for progress indicators
 */
export function calculateCompletionPercentage(
  summary: BIASummaryReport | undefined
): number {
  if (!summary) return 0;
  return Math.round(summary.bia_completion_rate * 100);
}

/**
 * Get criticality ratio for analytics
 */
export function getCriticalityRatio(
  summary: BIASummaryReport | undefined
): number {
  if (!summary || summary.total_processes === 0) return 0;
  return summary.critical_processes / summary.total_processes;
}

/**
 * Format financial loss for display
 */
export function formatPotentialLoss(amount: number): string {
  if (amount >= 1_000_000) {
    return `$${(amount / 1_000_000).toFixed(2)}M`;
  } else if (amount >= 1_000) {
    return `$${(amount / 1_000).toFixed(1)}K`;
  } else {
    return `$${amount.toFixed(0)}`;
  }
}

/**
 * Check if BIA coverage is adequate (>= 80% completion)
 */
export function hasAdequateCoverage(
  summary: BIASummaryReport | undefined
): boolean {
  if (!summary) return false;
  return summary.bia_completion_rate >= 0.8;
}

/**
 * Get health status based on summary metrics
 */
export function getBIAHealthStatus(summary: BIASummaryReport | undefined): {
  status: 'excellent' | 'good' | 'fair' | 'poor';
  color: string;
  label: string;
} {
  if (!summary) {
    return { status: 'poor', color: 'gray', label: 'No Data' };
  }

  const completionRate = summary.bia_completion_rate;
  const hasCritical = summary.critical_processes > 0;
  const hasProcesses = summary.total_processes >= 3;

  if (completionRate >= 0.9 && hasCritical && hasProcesses) {
    return { status: 'excellent', color: 'green', label: 'Excellent' };
  } else if (completionRate >= 0.7 && hasProcesses) {
    return { status: 'good', color: 'blue', label: 'Good' };
  } else if (completionRate >= 0.5 || hasProcesses) {
    return { status: 'fair', color: 'yellow', label: 'Fair' };
  } else {
    return { status: 'poor', color: 'red', label: 'Poor' };
  }
}

/**
 * Calculate average RTO in human-readable format
 */
export function formatAverageRTO(hours: number): string {
  if (hours < 1) {
    return `${Math.round(hours * 60)} minutes`;
  } else if (hours < 24) {
    return `${hours.toFixed(1)} hours`;
  } else {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return remainingHours > 0
      ? `${days}d ${remainingHours.toFixed(0)}h`
      : `${days} days`;
  }
}
