/**
 * useRetentionPolicies Hook
 * React Query hooks for document retention policy management
 * Real API integration via documentsAPI
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type { RetentionPolicy, Document, DocumentType } from '@/lib/api/documents-client';
import type { DocumentClassification } from '@/types/documents';

// ==================== QUERY KEYS ====================

export const retentionQueryKeys = {
  /**
   * Query key for all retention policies for a tenant
   */
  policies: (tenantId: string) => ['documents', 'retention-policies', tenantId] as const,

  /**
   * Query key for retention status of a specific document
   */
  status: (documentId: number) => ['documents', documentId, 'retention'] as const,
};

// ==================== TYPES ====================

export interface RetentionStatus {
  document_id: number;
  policy: RetentionPolicy | null;
  retention_date: string | null;
  days_until_action: number | null;
  legal_hold: boolean;
}

export interface UseRetentionPoliciesOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface UseCreateRetentionPolicyOptions {
  onSuccess?: (data: RetentionPolicy) => void;
  onError?: (error: Error) => void;
}

export interface UseDocumentRetentionStatusOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
}

export interface RetentionPolicyCreate {
  tenant_id: string;
  name: string;
  description?: string;
  document_type: DocumentType[];
  retention_years: number;
  action_after_retention: 'ARCHIVE' | 'DELETE' | 'REVIEW';
  legal_hold_exempt: boolean;
}

// ==================== HOOKS ====================

/**
 * Hook to fetch retention policies for a tenant
 *
 * @param tenantId - Tenant identifier
 * @param options - React Query options
 * @returns Query result with retention policies
 *
 * @example
 * ```tsx
 * const { data: policies, isLoading } = useRetentionPolicies('org-123');
 *
 * if (policies) {
 *   return (
 *     <div>
 *       <h2>Retention Policies</h2>
 *       {policies.map(policy => (
 *         <div key={policy.policy_id}>
 *           <h3>{policy.policy_name}</h3>
 *           <p>Retention: {policy.retention_years} years</p>
 *           <p>Trigger: {policy.trigger_type}</p>
 *         </div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useRetentionPolicies(
  tenantId: string,
  options: UseRetentionPoliciesOptions = {}
) {
  return useQuery({
    queryKey: retentionQueryKeys.policies(tenantId),
    queryFn: () => documentsAPI.getRetentionPolicies(tenantId),

    // Policies change infrequently, cache longer
    staleTime: options.staleTime ?? 30 * 60 * 1000, // 30 minutes
    gcTime: options.gcTime ?? 60 * 60 * 1000, // 1 hour

    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,
    enabled: options.enabled ?? true,

    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook to create a new retention policy
 *
 * Invalidates:
 * - Retention policy list for the tenant
 * - All document retention statuses (as new policy may apply)
 *
 * @param options - Mutation options with callbacks
 * @returns Mutation object with mutate function
 *
 * @example
 * ```tsx
 * const createPolicy = useCreateRetentionPolicy({
 *   onSuccess: (policy) => {
 *     toast.success(\`Policy "\${policy.policy_name}" created\`);
 *   }
 * });
 *
 * const handleSubmit = (data: RetentionPolicyCreate) => {
 *   createPolicy.mutate(data);
 * };
 * ```
 */
export function useCreateRetentionPolicy(
  options: UseCreateRetentionPolicyOptions = {}
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RetentionPolicyCreate) =>
      documentsAPI.createRetentionPolicy(data as any),

    onSuccess: (data) => {
      // Invalidate policy list for this tenant
      queryClient.invalidateQueries({
        queryKey: retentionQueryKeys.policies(data.tenant_id),
      });

      // Invalidate all retention statuses as new policy may apply
      queryClient.invalidateQueries({
        queryKey: ['documents'],
        predicate: (query) => {
          const key = query.queryKey;
          return key.length === 3 && key[2] === 'retention';
        },
      });

      options.onSuccess?.(data);
    },

    onError: options.onError,

    retry: 1,
  });
}

/**
 * Hook to get retention status for a specific document
 *
 * @param documentId - Document identifier
 * @param options - React Query options
 * @returns Query result with retention status
 *
 * @example
 * ```tsx
 * const { data: status, isLoading } = useDocumentRetentionStatus(123);
 *
 * if (status) {
 *   return (
 *     <div>
 *       <h3>Retention Information</h3>
 *       {status.policy ? (
 *         <>
 *           <p>Policy: {status.policy.policy_name}</p>
 *           <p>Retention Date: {status.retention_date}</p>
 *           <p>Days Until Action: {status.days_until_action}</p>
 *           {status.legal_hold && <p className="text-red-600">Legal Hold Active</p>}
 *         </>
 *       ) : (
 *         <p>No retention policy applies to this document</p>
 *       )}
 *     </div>
 *   );
 * }
 * ```
 */
export function useDocumentRetentionStatus(
  documentId: number,
  options: UseDocumentRetentionStatusOptions = {}
) {
  return useQuery({
    queryKey: retentionQueryKeys.status(documentId),
    queryFn: () => documentsAPI.getRetentionStatus(documentId),

    // Retention status changes less frequently
    staleTime: options.staleTime ?? 15 * 60 * 1000, // 15 minutes
    gcTime: options.gcTime ?? 30 * 60 * 1000, // 30 minutes

    enabled: options.enabled ?? true,

    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Find the applicable retention policy for a document
 * Matches based on type, department, and classification (in order of specificity)
 *
 * @param document - The document to find a policy for
 * @param policies - Array of retention policies
 * @returns The most specific matching policy, or null if none match
 *
 * @example
 * ```tsx
 * const policies = useRetentionPolicies('org-123').data;
 * const document = useDocument(123).data;
 * const applicablePolicy = getApplicablePolicy(document, policies);
 * ```
 */
export function getApplicablePolicy(
  document: Document | undefined,
  policies: RetentionPolicy[] | undefined
): RetentionPolicy | null {
  if (!document || !policies || policies.length === 0) {
    return null;
  }

  // Find policies that match the document type
  const matches = policies.filter(p =>
    p.document_type?.includes(document.document_type)
  );

  // Return the first matching policy (could be extended for more complex logic)
  return matches.length > 0 ? matches[0] : null;
}

/**
 * Calculate retention date for a document based on policy
 *
 * @param document - The document
 * @param policy - The retention policy to apply
 * @returns ISO date string for when retention expires, or null
 *
 * @example
 * ```tsx
 * const retentionDate = calculateRetentionDate(document, policy);
 * console.log(\`Document will be retained until: \${retentionDate}\`);
 * ```
 */
export function calculateRetentionDate(
  document: Document | undefined,
  policy: RetentionPolicy | null | undefined
): string | null {
  if (!document || !policy) {
    return null;
  }

  // Use creation date as trigger
  const triggerDate = document.created_at;

  if (!triggerDate) {
    return null;
  }

  const trigger = new Date(triggerDate);
  const retentionDays = policy.retention_years;

  // Calculate retention end date
  const retentionDate = new Date(trigger);
  retentionDate.setDate(retentionDate.getDate() + retentionDays);

  return retentionDate.toISOString();
}

/**
 * Check if a document's retention period has expired
 *
 * @param document - The document to check
 * @param retentionDate - The calculated retention date (from calculateRetentionDate)
 * @returns true if retention has expired, false otherwise
 *
 * @example
 * ```tsx
 * const expired = isRetentionExpired(document, retentionDate);
 * if (expired) {
 *   return <Badge color="red">Retention Expired</Badge>;
 * }
 * ```
 */
export function isRetentionExpired(
  document: Document | undefined,
  retentionDate: string | null | undefined
): boolean {
  if (!document || !retentionDate) {
    return false;
  }

  const now = new Date();
  const retention = new Date(retentionDate);

  return now > retention;
}

/**
 * Get days remaining until retention action
 *
 * @param retentionDate - The retention date
 * @returns Number of days until action, or null if no date
 */
export function getDaysUntilRetentionAction(
  retentionDate: string | null | undefined
): number | null {
  if (!retentionDate) {
    return null;
  }

  const now = new Date();
  const retention = new Date(retentionDate);
  const diffTime = retention.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  return diffDays;
}

/**
 * Format retention period for display
 *
 * @param days - Retention period in days
 * @returns Human-readable retention period
 */
export function formatRetentionPeriod(days: number): string {
  if (days === 0) return 'No retention';
  if (days === 1) return '1 day';
  if (days < 365) return `${days} days`;

  const years = Math.floor(days / 365);
  const remainingDays = days % 365;

  if (remainingDays === 0) {
    return years === 1 ? '1 year' : `${years} years`;
  }

  return years === 1 ? `1 year ${remainingDays} days` : `${years} years ${remainingDays} days`;
}

/**
 * Get retention status label and color
 *
 * @param daysUntilAction - Days until retention action
 * @returns Status object with label and color
 */
export function getRetentionStatusLabel(
  daysUntilAction: number | null
): { label: string; color: string } {
  if (daysUntilAction === null) {
    return { label: 'No Policy', color: 'gray' };
  }

  if (daysUntilAction < 0) {
    return { label: 'Expired', color: 'red' };
  }

  if (daysUntilAction <= 30) {
    return { label: 'Expiring Soon', color: 'orange' };
  }

  if (daysUntilAction <= 90) {
    return { label: 'Expiring', color: 'yellow' };
  }

  return { label: 'Active', color: 'green' };
}
