/**
 * Compliance Module - Evidence & Audits Hooks
 * React Query hooks for Compliance Evidence and Audits
 * ISO 22301:2019 Clause 10 - Improvement & Compliance Management
 *
 * Created: 2025-10-24
 * Agent: 20 (Compliance Module Round 2)
 *
 * Total Hooks: 25
 * - Evidence Hooks: 11 hooks (5 query + 6 mutation)
 * - Audit Hooks: 14 hooks (6 query + 8 mutation)
 */

'use client';

import { useQuery, useMutation, useQueryClient, type QueryClient } from '@tanstack/react-query';
import {
  // Evidence imports
  listEvidence,
  getEvidence,
  uploadEvidence,
  updateEvidence,
  deleteEvidence,
  transitionEvidence,
  getEvidenceHistory,
  bulkEvidenceOperation,
  // Audit imports
  listAudits,
  getAudit,
  createAudit,
  updateAudit,
  deleteAudit,
  startAudit,
  completeAudit,
  getAuditChecklist,
  getAuditFindings,
  createAuditFinding,
  getAuditReport,
  // Type imports
  type ComplianceEvidence,
  type ComplianceEvidenceCreate,
  type ComplianceEvidenceUpdate,
  type EvidenceStatus,
  type EvidenceHistory,
  type BulkOperationRequest,
  type BulkOperationResult,
  type ComplianceAudit,
  type ComplianceAuditCreate,
  type ComplianceAuditUpdate,
  type AuditChecklist,
  type AuditFinding,
  type AuditReport,
  type ListParams,
} from '@/lib/api/compliance-client';

import type { EvidenceType, EvidenceState } from '@/types/compliance';

// ============================================================================
// QUERY KEY FACTORIES
// ============================================================================

/**
 * Query key factory for compliance evidence
 * Provides consistent cache key generation for all evidence-related queries
 */
export const evidenceQueryKeys = {
  all: ['compliance', 'evidence'] as const,
  lists: () => [...evidenceQueryKeys.all, 'list'] as const,
  list: (organizationId: string, filters?: Record<string, unknown>) =>
    [...evidenceQueryKeys.lists(), { organizationId, ...filters }] as const,
  details: () => [...evidenceQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...evidenceQueryKeys.details(), id] as const,
  history: (id: string) => [...evidenceQueryKeys.detail(id), 'history'] as const,
  byType: (type: EvidenceType, organizationId: string) =>
    [...evidenceQueryKeys.all, 'by-type', type, organizationId] as const,
  byRequirement: (requirementId: string) =>
    [...evidenceQueryKeys.all, 'by-requirement', requirementId] as const,
  byStatus: (status: EvidenceState, organizationId: string) =>
    [...evidenceQueryKeys.all, 'by-status', status, organizationId] as const,
};

/**
 * Query key factory for compliance audits
 * Provides consistent cache key generation for all audit-related queries
 */
export const auditQueryKeys = {
  all: ['compliance', 'audits'] as const,
  lists: () => [...auditQueryKeys.all, 'list'] as const,
  list: (organizationId: string, filters?: Record<string, unknown>) =>
    [...auditQueryKeys.lists(), { organizationId, ...filters }] as const,
  details: () => [...auditQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...auditQueryKeys.details(), id] as const,
  checklist: (id: string) => [...auditQueryKeys.detail(id), 'checklist'] as const,
  findings: (id: string) => [...auditQueryKeys.detail(id), 'findings'] as const,
  report: (id: string) => [...auditQueryKeys.detail(id), 'report'] as const,
  byType: (type: string, organizationId: string) =>
    [...auditQueryKeys.all, 'by-type', type, organizationId] as const,
  upcoming: (organizationId: string) => [...auditQueryKeys.all, 'upcoming', organizationId] as const,
};

// ============================================================================
// EVIDENCE - QUERY HOOKS (5 hooks)
// ============================================================================

/**
 * Hook Parameters - List Evidence
 */
export interface UseComplianceEvidenceParams {
  organizationId: string;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Hook to fetch compliance evidence list
 * Supports filtering by status, search, and pagination
 *
 * @param params - Query parameters with organizationId and optional filters
 * @returns Query result with evidence array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: evidence, isLoading } = useComplianceEvidence({
 *   organizationId: 'org-123',
 *   status: 'approved',
 *   search: 'policy',
 *   page: 1,
 *   limit: 20,
 *   enabled: true
 * });
 *
 * if (evidence) {
 *   console.log(`Found ${evidence.length} evidence items`);
 *   const verified = evidence.filter(e => e.verification_status === 'verified');
 *   console.log(`Verified: ${verified.length}/${evidence.length}`);
 * }
 * ```
 */
export function useComplianceEvidence({
  organizationId,
  status,
  search,
  page,
  limit,
  enabled = true,
}: UseComplianceEvidenceParams) {
  return useQuery({
    queryKey: evidenceQueryKeys.list(organizationId, { status, search, page, limit }),
    queryFn: () => listEvidence({ organization_id: organizationId, status, search, page, limit }),
    enabled: enabled && !!organizationId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Evidence
 */
export interface UseEvidenceItemParams {
  evidenceId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch a single evidence item by ID
 * Returns complete evidence details including metadata
 *
 * @param params - Query parameters with evidenceId
 * @returns Query result with evidence data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: evidence, isLoading, error } = useEvidenceItem({
 *   evidenceId: 'evidence-123',
 *   enabled: true
 * });
 *
 * if (evidence) {
 *   console.log(`Evidence: ${evidence.evidence_name}`);
 *   console.log(`Type: ${evidence.evidence_type}`);
 *   console.log(`Status: ${evidence.status}`);
 *   console.log(`Verification: ${evidence.verification_status}`);
 *   if (evidence.verified_by && evidence.verified_at) {
 *     console.log(`Verified by ${evidence.verified_by} on ${evidence.verified_at}`);
 *   }
 * }
 * ```
 */
export function useEvidenceItem({ evidenceId, enabled = true }: UseEvidenceItemParams) {
  return useQuery({
    queryKey: evidenceQueryKeys.detail(evidenceId),
    queryFn: () => getEvidence(evidenceId),
    enabled: enabled && !!evidenceId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Evidence History
 */
export interface UseEvidenceHistoryParams {
  evidenceId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch evidence audit trail/history
 * Returns all status changes, updates, and actions performed on the evidence
 *
 * @param params - Query parameters with evidenceId
 * @returns Query result with history data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: history } = useEvidenceHistory({
 *   evidenceId: 'evidence-123',
 *   enabled: true
 * });
 *
 * if (history && history.history) {
 *   console.log(`Found ${history.history.length} history entries`);
 *   history.history.forEach(entry => {
 *     console.log(`[${entry.timestamp}] ${entry.action} by ${entry.user_id || 'system'}`);
 *     if (entry.changes) {
 *       console.log('Changes:', entry.changes);
 *     }
 *   });
 * }
 * ```
 */
export function useEvidenceHistory({ evidenceId, enabled = true }: UseEvidenceHistoryParams) {
  return useQuery({
    queryKey: evidenceQueryKeys.history(evidenceId),
    queryFn: () => getEvidenceHistory(evidenceId),
    enabled: enabled && !!evidenceId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Evidence by Type
 */
export interface UseEvidenceByTypeParams {
  evidenceType: EvidenceType;
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch evidence items filtered by type
 * Returns all evidence of a specific type (policy, procedure, record, etc.)
 *
 * @param params - Query parameters with evidenceType and organizationId
 * @returns Query result with filtered evidence array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: policies } = useEvidenceByType({
 *   evidenceType: EvidenceType.POLICY,
 *   organizationId: 'org-123',
 *   enabled: true
 * });
 *
 * if (policies) {
 *   console.log(`Found ${policies.length} policy documents`);
 *   const approved = policies.filter(p => p.status === EvidenceState.APPROVED);
 *   console.log(`Approved policies: ${approved.length}/${policies.length}`);
 * }
 * ```
 */
export function useEvidenceByType({
  evidenceType,
  organizationId,
  enabled = true,
}: UseEvidenceByTypeParams) {
  return useQuery({
    queryKey: evidenceQueryKeys.byType(evidenceType, organizationId),
    queryFn: async () => {
      const allEvidence = await listEvidence({ organization_id: organizationId });
      return allEvidence.filter((e) => e.evidence_type === evidenceType);
    },
    enabled: enabled && !!organizationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Evidence by Status
 */
export interface UseEvidenceByStatusParams {
  status: EvidenceState;
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch evidence items filtered by status
 * Returns all evidence in a specific workflow state
 *
 * @param params - Query parameters with status and organizationId
 * @returns Query result with filtered evidence array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: pendingEvidence } = useEvidenceByStatus({
 *   status: EvidenceState.UNDER_REVIEW,
 *   organizationId: 'org-123',
 *   enabled: true
 * });
 *
 * if (pendingEvidence && pendingEvidence.length > 0) {
 *   console.log(`${pendingEvidence.length} evidence items pending review`);
 *   pendingEvidence.forEach(e => {
 *     console.log(`- ${e.evidence_name} (${e.evidence_type})`);
 *   });
 * }
 * ```
 */
export function useEvidenceByStatus({
  status,
  organizationId,
  enabled = true,
}: UseEvidenceByStatusParams) {
  return useQuery({
    queryKey: evidenceQueryKeys.byStatus(status, organizationId),
    queryFn: async () => {
      // Use the listEvidence API directly with status filter
      return listEvidence({ organization_id: organizationId, status: status as any });
    },
    enabled: enabled && !!organizationId,
    staleTime: 2 * 60 * 1000, // 2 minutes - shorter for status tracking
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true, // Refetch on focus for status updates
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// EVIDENCE - MUTATION HOOKS (6 hooks)
// ============================================================================

/**
 * Hook Options - Upload Evidence
 */
export interface UseUploadEvidenceOptions {
  onSuccess?: (evidence: ComplianceEvidence) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to upload new compliance evidence
 * Automatically invalidates evidence list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const uploadEvidence = useUploadEvidence({
 *   onSuccess: (evidence) => {
 *     console.log(`Evidence "${evidence.evidence_name}" uploaded`);
 *     router.push(`/compliance/evidence/${evidence.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Upload failed: ${error.message}`);
 *   }
 * });
 *
 * // Upload new evidence
 * uploadEvidence.mutate({
 *   organization_id: 'org-123',
 *   evidence_name: 'Business Continuity Policy 2025',
 *   description: 'Updated BC policy document for annual review',
 *   evidence_type: 'policy',
 *   file_url: 's3://bucket/bc-policy-2025.pdf',
 *   file_metadata: {
 *     size: 245680,
 *     format: 'pdf',
 *     pages: 24
 *   },
 *   requirement_ids: ['req-001', 'req-002'],
 *   collected_date: new Date().toISOString(),
 *   expiry_date: '2026-12-31'
 * });
 * ```
 */
export function useUploadEvidence(options: UseUploadEvidenceOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceEvidence, Error, ComplianceEvidenceCreate>({
    mutationFn: (data: ComplianceEvidenceCreate) => uploadEvidence(data),

    onSuccess: (data) => {
      // Invalidate evidence lists to refetch with new evidence
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.lists(),
      });

      // Invalidate type-based and status-based queries
      if (data.evidence_type) {
        queryClient.invalidateQueries({
          queryKey: [...evidenceQueryKeys.all, 'by-type'],
        });
      }
      queryClient.invalidateQueries({
        queryKey: [...evidenceQueryKeys.all, 'by-status'],
      });

      // Invalidate requirement-based queries if linked
      if (data.requirement_ids && data.requirement_ids.length > 0) {
        data.requirement_ids.forEach((reqId) => {
          queryClient.invalidateQueries({
            queryKey: evidenceQueryKeys.byRequirement(reqId),
          });
        });
      }

      // Optimistically set the single evidence cache
      if (data.id) {
        queryClient.setQueryData(evidenceQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Evidence
 */
export interface UseUpdateEvidenceOptions {
  onSuccess?: (evidence: ComplianceEvidence) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Evidence Parameters
 */
export interface UpdateEvidenceParams {
  evidenceId: string;
  data: ComplianceEvidenceUpdate;
}

/**
 * Hook to update existing compliance evidence
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateEvidence = useUpdateEvidence({
 *   onSuccess: (evidence) => {
 *     console.log(`Evidence "${evidence.evidence_name}" updated`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * // Update evidence details
 * updateEvidence.mutate({
 *   evidenceId: 'evidence-123',
 *   data: {
 *     description: 'Updated policy with quarterly review comments',
 *     verified_by: 'user-456',
 *     verification_date: new Date().toISOString(),
 *     status: EvidenceStatus.APPROVED
 *   }
 * });
 * ```
 */
export function useUpdateEvidence(options: UseUpdateEvidenceOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceEvidence, Error, UpdateEvidenceParams>({
    mutationFn: ({ evidenceId, data }: UpdateEvidenceParams) => updateEvidence(evidenceId, data),

    onSuccess: (data) => {
      // Invalidate evidence lists
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.lists(),
      });

      // Invalidate the specific evidence detail
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.detail(data.id!),
      });

      // Invalidate history as update creates history entry
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.history(data.id!),
      });

      // Invalidate type and status queries
      queryClient.invalidateQueries({
        queryKey: [...evidenceQueryKeys.all, 'by-type'],
      });
      queryClient.invalidateQueries({
        queryKey: [...evidenceQueryKeys.all, 'by-status'],
      });

      // Update the cached evidence data
      if (data.id) {
        queryClient.setQueryData(evidenceQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Delete Evidence
 */
export interface UseDeleteEvidenceOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete compliance evidence
 * Automatically invalidates evidence cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteEvidence = useDeleteEvidence({
 *   onSuccess: () => {
 *     console.log('Evidence deleted successfully');
 *     router.push('/compliance/evidence');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * // Delete evidence
 * deleteEvidence.mutate('evidence-123');
 * ```
 */
export function useDeleteEvidence(options: UseDeleteEvidenceOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: (evidenceId: string) => deleteEvidence(evidenceId),

    onSuccess: (_, evidenceId) => {
      // Invalidate all evidence lists
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.lists(),
      });

      // Invalidate the deleted evidence detail
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.detail(evidenceId),
      });

      // Invalidate type and status queries
      queryClient.invalidateQueries({
        queryKey: [...evidenceQueryKeys.all, 'by-type'],
      });
      queryClient.invalidateQueries({
        queryKey: [...evidenceQueryKeys.all, 'by-status'],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: evidenceQueryKeys.detail(evidenceId),
      });

      // Call user callback
      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Transition Evidence
 */
export interface UseTransitionEvidenceOptions {
  onSuccess?: (evidence: ComplianceEvidence) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Transition Evidence Parameters
 */
export interface TransitionEvidenceParams {
  evidenceId: string;
  newStatus: EvidenceStatus;
}

/**
 * Hook to transition evidence status through workflow
 * Changes evidence state (draft -> submitted -> under_review -> approved/rejected)
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const transitionEvidence = useTransitionEvidence({
 *   onSuccess: (evidence) => {
 *     console.log(`Evidence transitioned to ${evidence.status}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Transition failed: ${error.message}`);
 *   }
 * });
 *
 * // Submit evidence for review
 * transitionEvidence.mutate({
 *   evidenceId: 'evidence-123',
 *   newStatus: EvidenceStatus.SUBMITTED
 * });
 *
 * // Approve evidence
 * transitionEvidence.mutate({
 *   evidenceId: 'evidence-123',
 *   newStatus: EvidenceStatus.APPROVED
 * });
 * ```
 */
export function useTransitionEvidence(options: UseTransitionEvidenceOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceEvidence, Error, TransitionEvidenceParams>({
    mutationFn: ({ evidenceId, newStatus }: TransitionEvidenceParams) =>
      transitionEvidence(evidenceId, newStatus),

    onSuccess: (data) => {
      // Invalidate evidence lists
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.lists(),
      });

      // Invalidate the specific evidence detail
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.detail(data.id!),
      });

      // Invalidate history as transition creates history entry
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.history(data.id!),
      });

      // Invalidate status-based queries - critical for workflow
      queryClient.invalidateQueries({
        queryKey: [...evidenceQueryKeys.all, 'by-status'],
      });

      // Update the cached evidence data
      if (data.id) {
        queryClient.setQueryData(evidenceQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Bulk Evidence Operation
 */
export interface UseBulkEvidenceOperationOptions {
  onSuccess?: (result: BulkOperationResult) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to perform bulk operations on evidence
 * Supports bulk create, update, and delete operations
 * Automatically invalidates evidence cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const bulkOperation = useBulkEvidenceOperation({
 *   onSuccess: (result) => {
 *     console.log(`Bulk operation complete:`);
 *     console.log(`Total: ${result.total}`);
 *     console.log(`Successful: ${result.successful}`);
 *     console.log(`Failed: ${result.failed}`);
 *     if (result.errors.length > 0) {
 *       console.error('Errors:', result.errors);
 *     }
 *   },
 *   onError: (error) => {
 *     console.error(`Bulk operation failed: ${error.message}`);
 *   }
 * });
 *
 * // Bulk delete evidence
 * bulkOperation.mutate({
 *   operation: 'delete',
 *   items: ['evidence-1', 'evidence-2', 'evidence-3']
 * });
 *
 * // Bulk update status
 * bulkOperation.mutate({
 *   operation: 'update',
 *   items: [
 *     { id: 'evidence-1', status: EvidenceStatus.APPROVED },
 *     { id: 'evidence-2', status: EvidenceStatus.APPROVED },
 *   ]
 * });
 * ```
 */
export function useBulkEvidenceOperation(options: UseBulkEvidenceOperationOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<BulkOperationResult, Error, BulkOperationRequest>({
    mutationFn: (request: BulkOperationRequest) => bulkEvidenceOperation(request),

    onSuccess: (result) => {
      // Invalidate all evidence-related queries
      queryClient.invalidateQueries({
        queryKey: evidenceQueryKeys.all,
      });

      // Call user callback
      callbackOptions.onSuccess?.(result);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// AUDITS - QUERY HOOKS (6 hooks)
// ============================================================================

/**
 * Hook Parameters - List Audits
 */
export interface UseComplianceAuditsParams {
  organizationId: string;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Hook to fetch compliance audits list
 * Supports filtering by status, search, and pagination
 *
 * @param params - Query parameters with organizationId and optional filters
 * @returns Query result with audits array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: audits, isLoading } = useComplianceAudits({
 *   organizationId: 'org-123',
 *   status: 'in_progress',
 *   search: 'ISO',
 *   page: 1,
 *   limit: 20,
 *   enabled: true
 * });
 *
 * if (audits) {
 *   console.log(`Found ${audits.length} audits`);
 *   const completed = audits.filter(a => a.status === 'completed');
 *   console.log(`Completed: ${completed.length}/${audits.length}`);
 * }
 * ```
 */
export function useComplianceAudits({
  organizationId,
  status,
  search,
  page,
  limit,
  enabled = true,
}: UseComplianceAuditsParams) {
  return useQuery({
    queryKey: auditQueryKeys.list(organizationId, { status, search, page, limit }),
    queryFn: () => listAudits({ organization_id: organizationId, status, search, page, limit }),
    enabled: enabled && !!organizationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Audit
 */
export interface UseComplianceAuditParams {
  auditId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch a single compliance audit by ID
 * Returns complete audit details including findings and results
 *
 * @param params - Query parameters with auditId
 * @returns Query result with audit data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: audit, isLoading, error } = useComplianceAudit({
 *   auditId: 'audit-123',
 *   enabled: true
 * });
 *
 * if (audit) {
 *   console.log(`Audit: ${audit.audit_name}`);
 *   console.log(`Type: ${audit.audit_type}`);
 *   console.log(`Status: ${audit.status}`);
 *   console.log(`Lead Auditor: ${audit.lead_auditor_id}`);
 *   if (audit.findings_count) {
 *     console.log(`Findings: ${audit.findings_count}`);
 *   }
 * }
 * ```
 */
export function useComplianceAudit({ auditId, enabled = true }: UseComplianceAuditParams) {
  return useQuery({
    queryKey: auditQueryKeys.detail(auditId),
    queryFn: () => getAudit(auditId),
    enabled: enabled && !!auditId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Audit Checklist
 */
export interface UseAuditChecklistParams {
  auditId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch audit checklist
 * Returns checklist items with compliance status for each requirement
 *
 * @param params - Query parameters with auditId
 * @returns Query result with checklist data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: checklist } = useAuditChecklist({
 *   auditId: 'audit-123',
 *   enabled: true
 * });
 *
 * if (checklist && checklist.items) {
 *   console.log(`Checklist has ${checklist.items.length} items`);
 *   const compliant = checklist.items.filter(i => i.status === 'compliant');
 *   const nonCompliant = checklist.items.filter(i => i.status === 'non_compliant');
 *   console.log(`Compliant: ${compliant.length}, Non-Compliant: ${nonCompliant.length}`);
 * }
 * ```
 */
export function useAuditChecklist({ auditId, enabled = true }: UseAuditChecklistParams) {
  return useQuery({
    queryKey: auditQueryKeys.checklist(auditId),
    queryFn: () => getAuditChecklist(auditId),
    enabled: enabled && !!auditId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Audit Findings
 */
export interface UseAuditFindingsParams {
  auditId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch audit findings
 * Returns all findings/non-conformities identified during the audit
 *
 * @param params - Query parameters with auditId
 * @returns Query result with findings array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: findings } = useAuditFindings({
 *   auditId: 'audit-123',
 *   enabled: true
 * });
 *
 * if (findings) {
 *   console.log(`Found ${findings.length} audit findings`);
 *   const critical = findings.filter(f => f.severity === 'critical');
 *   const high = findings.filter(f => f.severity === 'high');
 *   console.log(`Critical: ${critical.length}, High: ${high.length}`);
 *
 *   findings.forEach(finding => {
 *     console.log(`- [${finding.severity}] ${finding.finding_title}`);
 *     console.log(`  ${finding.description}`);
 *   });
 * }
 * ```
 */
export function useAuditFindings({ auditId, enabled = true }: UseAuditFindingsParams) {
  return useQuery({
    queryKey: auditQueryKeys.findings(auditId),
    queryFn: () => getAuditFindings(auditId),
    enabled: enabled && !!auditId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Audit Report
 */
export interface UseAuditReportParams {
  auditId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch audit report
 * Returns complete audit report with executive summary, findings, and recommendations
 *
 * @param params - Query parameters with auditId
 * @returns Query result with report data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: report } = useAuditReport({
 *   auditId: 'audit-123',
 *   enabled: true
 * });
 *
 * if (report) {
 *   console.log(`Audit Report: ${report.audit_name}`);
 *   console.log(`Overall Rating: ${report.overall_rating}`);
 *   console.log(`Executive Summary: ${report.executive_summary}`);
 *   console.log(`Scope: ${report.scope}`);
 *   console.log(`Methodology: ${report.methodology}`);
 *   console.log(`Findings: ${report.findings.length}`);
 *   console.log(`Recommendations: ${report.recommendations.length}`);
 *   console.log(`Generated: ${report.generated_at}`);
 * }
 * ```
 */
export function useAuditReport({ auditId, enabled = true }: UseAuditReportParams) {
  return useQuery({
    queryKey: auditQueryKeys.report(auditId),
    queryFn: () => getAuditReport(auditId),
    enabled: enabled && !!auditId,
    staleTime: 10 * 60 * 1000, // 10 minutes - reports are static
    gcTime: 30 * 60 * 1000, // 30 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Audits by Type
 */
export interface UseAuditsByTypeParams {
  auditType: string;
  organizationId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch audits filtered by type
 * Returns all audits of a specific type (internal, external, certification, etc.)
 *
 * @param params - Query parameters with auditType and organizationId
 * @returns Query result with filtered audits array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: internalAudits } = useAuditsByType({
 *   auditType: 'internal',
 *   organizationId: 'org-123',
 *   enabled: true
 * });
 *
 * if (internalAudits) {
 *   console.log(`Found ${internalAudits.length} internal audits`);
 *   const thisYear = new Date().getFullYear();
 *   const thisYearAudits = internalAudits.filter(a =>
 *     a.actual_start && new Date(a.actual_start).getFullYear() === thisYear
 *   );
 *   console.log(`Audits this year: ${thisYearAudits.length}`);
 * }
 * ```
 */
export function useAuditsByType({ auditType, organizationId, enabled = true }: UseAuditsByTypeParams) {
  return useQuery({
    queryKey: auditQueryKeys.byType(auditType, organizationId),
    queryFn: async () => {
      const allAudits = await listAudits({ organization_id: organizationId });
      return allAudits.filter((a) => a.audit_type === auditType);
    },
    enabled: enabled && !!organizationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// AUDITS - MUTATION HOOKS (8 hooks)
// ============================================================================

/**
 * Hook Options - Create Audit
 */
export interface UseCreateComplianceAuditOptions {
  onSuccess?: (audit: ComplianceAudit) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create a new compliance audit
 * Automatically invalidates audit list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createAudit = useCreateComplianceAudit({
 *   onSuccess: (audit) => {
 *     console.log(`Audit "${audit.audit_name}" created`);
 *     router.push(`/compliance/audits/${audit.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create audit: ${error.message}`);
 *   }
 * });
 *
 * // Create new audit
 * createAudit.mutate({
 *   organization_id: 'org-123',
 *   audit_name: 'ISO 22301 Certification Audit 2025',
 *   description: 'Annual certification audit for ISO 22301:2019',
 *   audit_type: 'certification',
 *   standard: 'ISO 22301',
 *   scope: 'All business continuity management processes',
 *   lead_auditor_id: 'user-456',
 *   audit_team: ['user-789', 'user-012'],
 *   scheduled_start: '2025-06-01',
 *   scheduled_end: '2025-06-05'
 * });
 * ```
 */
export function useCreateComplianceAudit(options: UseCreateComplianceAuditOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAudit, Error, ComplianceAuditCreate>({
    mutationFn: (data: ComplianceAuditCreate) => createAudit(data),

    onSuccess: (data) => {
      // Invalidate audit lists to refetch with new audit
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.lists(),
      });

      // Invalidate type-based queries
      if (data.audit_type) {
        queryClient.invalidateQueries({
          queryKey: [...auditQueryKeys.all, 'by-type'],
        });
      }

      // Invalidate upcoming audits
      queryClient.invalidateQueries({
        queryKey: [...auditQueryKeys.all, 'upcoming'],
      });

      // Optimistically set the single audit cache
      if (data.id) {
        queryClient.setQueryData(auditQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Audit
 */
export interface UseUpdateComplianceAuditOptions {
  onSuccess?: (audit: ComplianceAudit) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Audit Parameters
 */
export interface UpdateComplianceAuditParams {
  auditId: string;
  data: ComplianceAuditUpdate;
}

/**
 * Hook to update an existing compliance audit
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateAudit = useUpdateComplianceAudit({
 *   onSuccess: (audit) => {
 *     console.log(`Audit "${audit.audit_name}" updated`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * // Update audit details
 * updateAudit.mutate({
 *   auditId: 'audit-123',
 *   data: {
 *     description: 'Updated scope to include new processes',
 *     scope: 'All BC processes including new digital services',
 *     audit_team: ['user-789', 'user-012', 'user-345']
 *   }
 * });
 * ```
 */
export function useUpdateComplianceAudit(options: UseUpdateComplianceAuditOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAudit, Error, UpdateComplianceAuditParams>({
    mutationFn: ({ auditId, data }: UpdateComplianceAuditParams) => updateAudit(auditId, data),

    onSuccess: (data) => {
      // Invalidate audit lists
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.lists(),
      });

      // Invalidate the specific audit detail
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.detail(data.id!),
      });

      // Invalidate type-based queries
      queryClient.invalidateQueries({
        queryKey: [...auditQueryKeys.all, 'by-type'],
      });

      // Update the cached audit data
      if (data.id) {
        queryClient.setQueryData(auditQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Delete Audit
 */
export interface UseDeleteComplianceAuditOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete a compliance audit
 * Automatically invalidates audit cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteAudit = useDeleteComplianceAudit({
 *   onSuccess: () => {
 *     console.log('Audit deleted successfully');
 *     router.push('/compliance/audits');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * // Delete audit
 * deleteAudit.mutate('audit-123');
 * ```
 */
export function useDeleteComplianceAudit(options: UseDeleteComplianceAuditOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: (auditId: string) => deleteAudit(auditId),

    onSuccess: (_, auditId) => {
      // Invalidate all audit lists
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.lists(),
      });

      // Invalidate the deleted audit detail
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.detail(auditId),
      });

      // Invalidate type-based queries
      queryClient.invalidateQueries({
        queryKey: [...auditQueryKeys.all, 'by-type'],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: auditQueryKeys.detail(auditId),
      });

      // Call user callback
      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Start Audit
 */
export interface UseStartAuditOptions {
  onSuccess?: (audit: ComplianceAudit) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to start a compliance audit
 * Changes status from planned to in_progress and records start date
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const startAudit = useStartAudit({
 *   onSuccess: (audit) => {
 *     console.log(`Audit "${audit.audit_name}" started`);
 *     console.log(`Started on: ${audit.actual_start}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to start audit: ${error.message}`);
 *   }
 * });
 *
 * // Start audit execution
 * startAudit.mutate('audit-123');
 * ```
 */
export function useStartAudit(options: UseStartAuditOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAudit, Error, string>({
    mutationFn: (auditId: string) => startAudit(auditId),

    onSuccess: (data) => {
      // Invalidate audit lists
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.lists(),
      });

      // Invalidate the specific audit detail
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.detail(data.id!),
      });

      // Invalidate upcoming audits - status changed
      queryClient.invalidateQueries({
        queryKey: [...auditQueryKeys.all, 'upcoming'],
      });

      // Update the cached audit data
      if (data.id) {
        queryClient.setQueryData(auditQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Complete Audit
 */
export interface UseCompleteAuditOptions {
  onSuccess?: (audit: ComplianceAudit) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to complete a compliance audit
 * Changes status to completed and records completion date
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const completeAudit = useCompleteAudit({
 *   onSuccess: (audit) => {
 *     console.log(`Audit "${audit.audit_name}" completed`);
 *     console.log(`Completed on: ${audit.actual_end}`);
 *     console.log(`Total findings: ${audit.findings_count}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to complete audit: ${error.message}`);
 *   }
 * });
 *
 * // Complete audit
 * completeAudit.mutate('audit-123');
 * ```
 */
export function useCompleteAudit(options: UseCompleteAuditOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ComplianceAudit, Error, string>({
    mutationFn: (auditId: string) => completeAudit(auditId),

    onSuccess: (data) => {
      // Invalidate audit lists
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.lists(),
      });

      // Invalidate the specific audit detail
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.detail(data.id!),
      });

      // Invalidate type-based queries
      queryClient.invalidateQueries({
        queryKey: [...auditQueryKeys.all, 'by-type'],
      });

      // Invalidate report as it may be generated on completion
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.report(data.id!),
      });

      // Update the cached audit data
      if (data.id) {
        queryClient.setQueryData(auditQueryKeys.detail(data.id), data);
      }

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Create Audit Finding
 */
export interface UseCreateAuditFindingOptions {
  onSuccess?: (finding: AuditFinding) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Create Finding Parameters
 */
export interface CreateAuditFindingParams {
  auditId: string;
  finding: Omit<AuditFinding, 'id' | 'audit_id' | 'created_at'>;
}

/**
 * Hook to create a new audit finding
 * Records non-conformity or observation during audit
 * Automatically invalidates findings cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createFinding = useCreateAuditFinding({
 *   onSuccess: (finding) => {
 *     console.log(`Finding created: ${finding.finding_title}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create finding: ${error.message}`);
 *   }
 * });
 *
 * // Create new finding
 * createFinding.mutate({
 *   auditId: 'audit-123',
 *   finding: {
 *     finding_title: 'Incomplete BIA Documentation',
 *     description: 'Business Impact Analysis does not cover all critical processes',
 *     severity: 'high',
 *     requirement_id: 'req-004',
 *     evidence_id: 'evidence-567',
 *     recommendation: 'Complete BIA for all critical processes within 30 days'
 *   }
 * });
 * ```
 */
export function useCreateAuditFinding(options: UseCreateAuditFindingOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<AuditFinding, Error, CreateAuditFindingParams>({
    mutationFn: ({ auditId, finding }: CreateAuditFindingParams) => createAuditFinding(auditId, finding),

    onSuccess: (data, variables) => {
      // Invalidate findings list for this audit
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.findings(variables.auditId),
      });

      // Invalidate the audit detail - findings count may change
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.detail(variables.auditId),
      });

      // Invalidate audit lists
      queryClient.invalidateQueries({
        queryKey: auditQueryKeys.lists(),
      });

      // Call user callback
      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// PREFETCH UTILITIES
// ============================================================================

/**
 * Prefetch utility for evidence list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href="/compliance/evidence"
 *   onMouseEnter={() => prefetchEvidence(queryClient, organizationId)}
 * >
 *   View Evidence
 * </Link>
 * ```
 */
export function prefetchEvidence(
  queryClient: QueryClient,
  organizationId: string,
  filters?: Record<string, unknown>
) {
  return queryClient.prefetchQuery({
    queryKey: evidenceQueryKeys.list(organizationId, filters),
    queryFn: () => listEvidence({ organization_id: organizationId, ...filters }),
    staleTime: 3 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single evidence
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/evidence/${evidenceId}`}
 *   onMouseEnter={() => prefetchEvidenceItem(queryClient, evidenceId)}
 * >
 *   View Evidence Details
 * </Link>
 * ```
 */
export function prefetchEvidenceItem(queryClient: QueryClient, evidenceId: string) {
  return queryClient.prefetchQuery({
    queryKey: evidenceQueryKeys.detail(evidenceId),
    queryFn: () => getEvidence(evidenceId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for audits list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href="/compliance/audits"
 *   onMouseEnter={() => prefetchAudits(queryClient, organizationId)}
 * >
 *   View Audits
 * </Link>
 * ```
 */
export function prefetchAudits(
  queryClient: QueryClient,
  organizationId: string,
  filters?: Record<string, unknown>
) {
  return queryClient.prefetchQuery({
    queryKey: auditQueryKeys.list(organizationId, filters),
    queryFn: () => listAudits({ organization_id: organizationId, ...filters }),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single audit
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/audits/${auditId}`}
 *   onMouseEnter={() => prefetchAudit(queryClient, auditId)}
 * >
 *   View Audit Details
 * </Link>
 * ```
 */
export function prefetchAudit(queryClient: QueryClient, auditId: string) {
  return queryClient.prefetchQuery({
    queryKey: auditQueryKeys.detail(auditId),
    queryFn: () => getAudit(auditId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for audit findings
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/audits/${auditId}/findings`}
 *   onMouseEnter={() => prefetchAuditFindings(queryClient, auditId)}
 * >
 *   View Findings
 * </Link>
 * ```
 */
export function prefetchAuditFindings(queryClient: QueryClient, auditId: string) {
  return queryClient.prefetchQuery({
    queryKey: auditQueryKeys.findings(auditId),
    queryFn: () => getAuditFindings(auditId),
    staleTime: 3 * 60 * 1000,
  });
}

/**
 * Prefetch utility for audit report
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/compliance/audits/${auditId}/report`}
 *   onMouseEnter={() => prefetchAuditReport(queryClient, auditId)}
 * >
 *   View Report
 * </Link>
 * ```
 */
export function prefetchAuditReport(queryClient: QueryClient, auditId: string) {
  return queryClient.prefetchQuery({
    queryKey: auditQueryKeys.report(auditId),
    queryFn: () => getAuditReport(auditId),
    staleTime: 10 * 60 * 1000,
  });
}
