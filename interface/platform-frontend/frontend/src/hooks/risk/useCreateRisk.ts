/**
 * useCreateRisk Hook
 * React Query mutation hook for creating risk assessments
 * Real API integration via riskClient.createRisk
 * Week 5 - Risk Assessment Module
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { riskClient, type RiskCreate } from '@/lib/api/risk-client';
import type { Risk } from '@/types/risk';
import { riskQueryKeys } from './useRisks';
import toast from 'react-hot-toast';

export interface UseCreateRiskOptions {
  onSuccess?: (data: Risk) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create new risk assessment
 * Automatically invalidates risk list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createRisk = useCreateRisk({
 *   onSuccess: (risk) => {
 *     toast.success(`Risk "${risk.risk_title}" created`);
 *     router.push(`/risks/${risk.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create risk: ${error.message}`);
 *   }
 * });
 *
 * // In form submit
 * createRisk.mutate({
 *   organization_id: 'org-123',
 *   risk_title: 'Data Center Power Failure',
 *   risk_category: RiskCategory.OPERATIONAL,
 *   description: 'Risk of complete power loss to primary data center',
 *   threat_source: 'Infrastructure failure, natural disaster',
 *   vulnerabilities: ['Single power source', 'No backup generator'],
 *   likelihood: RiskLikelihood.POSSIBLE,
 *   impact: RiskImpact.CATASTROPHIC,
 *   risk_owner_id: 'user-456',
 *   status: RiskStatus.IDENTIFIED,
 *   // ... other fields
 * });
 * ```
 */
export function useCreateRisk(options: UseCreateRiskOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<Risk, Error, RiskCreate>({
    mutationFn: (data: RiskCreate) => riskClient.createRisk(data),

    onSuccess: (data) => {
      // Invalidate risk lists to refetch with new risk
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Optimistically set the single risk cache
      if (data.id) {
        queryClient.setQueryData(
          riskQueryKeys.detail(data.id),
          data
        );
      }

      // Show success toast
      if (showToast) {
        toast.success(`Risk "${data.risk_title}" created successfully`);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      // Show error toast
      if (showToast) {
        toast.error(`Failed to create risk: ${error.message}`);
      }

      // Call user callback
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      // Call user callback
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook to create risk with automatic score calculation
 * Calculates inherent_risk_score from likelihood and impact
 *
 * @example
 * ```tsx
 * const createRiskWithScore = useCreateRiskWithScore({
 *   onSuccess: (risk) => {
 *     console.log(`Created risk with score: ${risk.inherent_risk_score}`);
 *   }
 * });
 *
 * createRiskWithScore.mutate({
 *   organization_id: 'org-123',
 *   risk_title: 'Cybersecurity Breach',
 *   risk_category: RiskCategory.CYBERSECURITY,
 *   description: 'Potential ransomware attack',
 *   vulnerabilities: ['Outdated antivirus', 'No employee training'],
 *   likelihood: RiskLikelihood.LIKELY,
 *   impact: RiskImpact.MAJOR,
 *   // inherent_risk_score will be calculated as 4 × 4 = 16
 * });
 * ```
 */
export function useCreateRiskWithScore(options: UseCreateRiskOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<Risk, Error, RiskCreate>({
    mutationFn: (data: RiskCreate) => {
      // Calculate inherent risk score if not provided
      const enrichedData = {
        ...data,
        inherent_risk_score: data.likelihood * data.impact,
      };

      return riskClient.createRisk(enrichedData);
    },

    onSuccess: (data) => {
      // Invalidate risk lists
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Set detail cache
      if (data.id) {
        queryClient.setQueryData(
          riskQueryKeys.detail(data.id),
          data
        );
      }

      // Show success toast
      if (showToast) {
        toast.success(`Risk created with score ${data.inherent_risk_score}`);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      if (showToast) {
        toast.error(`Failed to create risk: ${error.message}`);
      }

      callbackOptions.onError?.(error);
    },

    onSettled: callbackOptions.onSettled,
  });
}

/**
 * Hook to create multiple risks in batch
 * Creates risks sequentially with progress tracking
 *
 * @example
 * ```tsx
 * const createRisksBatch = useCreateRisksBatch({
 *   onSuccess: (results) => {
 *     toast.success(`Created ${results.success} of ${results.total} risks`);
 *   }
 * });
 *
 * createRisksBatch.mutate([
 *   { organization_id: 'org-123', risk_title: 'Risk 1', ... },
 *   { organization_id: 'org-123', risk_title: 'Risk 2', ... },
 *   { organization_id: 'org-123', risk_title: 'Risk 3', ... },
 * ]);
 * ```
 */
export function useCreateRisksBatch(
  options: Omit<UseCreateRiskOptions, 'onSuccess'> & {
    onSuccess?: (results: { total: number; success: number; failed: number; risks: Risk[] }) => void;
  } = {}
) {
  const queryClient = useQueryClient();
  const { showToast = true, ...callbackOptions } = options;

  return useMutation<
    { total: number; success: number; failed: number; risks: Risk[] },
    Error,
    RiskCreate[]
  >({
    mutationFn: async (risksData: RiskCreate[]) => {
      const results = await Promise.allSettled(
        risksData.map((data) => riskClient.createRisk(data))
      );

      const successResults = results.filter((r) => r.status === 'fulfilled');
      const failedResults = results.filter((r) => r.status === 'rejected');

      return {
        total: risksData.length,
        success: successResults.length,
        failed: failedResults.length,
        risks: successResults.map((r) => (r as PromiseFulfilledResult<Risk>).value),
      };
    },

    onSuccess: (results) => {
      // Invalidate all risk lists
      queryClient.invalidateQueries({
        queryKey: riskQueryKeys.lists(),
      });

      // Cache all created risks
      results.risks.forEach((risk) => {
        if (risk.id) {
          queryClient.setQueryData(
            riskQueryKeys.detail(risk.id),
            risk
          );
        }
      });

      // Show success toast
      if (showToast) {
        if (results.failed === 0) {
          toast.success(`Successfully created ${results.success} risks`);
        } else {
          toast.success(
            `Created ${results.success} of ${results.total} risks (${results.failed} failed)`
          );
        }
      }

      callbackOptions.onSuccess?.(results);
    },

    onError: (error: Error) => {
      if (showToast) {
        toast.error(`Batch creation failed: ${error.message}`);
      }

      callbackOptions.onError?.(error);
    },

    onSettled: callbackOptions.onSettled,
  });
}
