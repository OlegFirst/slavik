/**
 * useDocumentAudit Hook
 * React Query hooks for document access logs and audit trails
 * Real API integration via documentsAPI
 */

import { useQuery } from '@tanstack/react-query';
import { documentsAPI } from '@/lib/api/documents-client';
import type { DocumentAccess, AccessAction } from '@/types/documents';

// ==================== QUERY KEYS ====================

export const auditQueryKeys = {
  /**
   * Query key for document access logs with optional filters
   */
  logs: (documentId: number, filters?: AccessLogFilters) =>
    ['documents', documentId, 'access-log', filters] as const,
};

// ==================== TYPES ====================

export interface AccessLogFilters {
  action_type?: string;
  user_id?: string;
  skip?: number;
  limit?: number;
}

export interface AccessLogResponse {
  logs: DocumentAccess[];
  total: number;
}

export interface UseDocumentAccessLogOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface GroupedByAction {
  [key: string]: DocumentAccess[];
}

export interface GroupedByUser {
  [userId: string]: DocumentAccess[];
}

export interface ActionSummary {
  action_type: AccessAction;
  count: number;
  latest: string;
  users: string[];
}

// ==================== HOOKS ====================

/**
 * Hook to fetch document access log with filtering
 */
export function useDocumentAccessLog(
  documentId: number,
  filters: AccessLogFilters = {},
  options: UseDocumentAccessLogOptions = {}
) {
  return useQuery({
    queryKey: auditQueryKeys.logs(documentId, filters),
    queryFn: () => documentsAPI.getAccessLog(documentId, filters),

    // Access logs change frequently, shorter cache
    staleTime: options.staleTime ?? 2 * 60 * 1000, // 2 minutes
    gcTime: options.gcTime ?? 10 * 60 * 1000, // 10 minutes

    refetchOnWindowFocus: options.refetchOnWindowFocus ?? true,
    enabled: options.enabled ?? true,

    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Group access logs by action type
 */
export function groupByAction(
  logs: DocumentAccess[] | undefined
): GroupedByAction {
  if (!logs || logs.length === 0) {
    return {};
  }

  return logs.reduce((acc, log) => {
    const action = log.action_type;
    if (!acc[action]) {
      acc[action] = [];
    }
    acc[action].push(log);
    return acc;
  }, {} as GroupedByAction);
}

/**
 * Group access logs by user
 */
export function groupByUser(
  logs: DocumentAccess[] | undefined
): GroupedByUser {
  if (!logs || logs.length === 0) {
    return {};
  }

  return logs.reduce((acc, log) => {
    const userId = log.user_id;
    if (!acc[userId]) {
      acc[userId] = [];
    }
    acc[userId].push(log);
    return acc;
  }, {} as GroupedByUser);
}

/**
 * Get logs from the last N hours
 */
export function getRecentAccess(
  logs: DocumentAccess[] | undefined,
  hours: number
): DocumentAccess[] {
  if (!logs || logs.length === 0) {
    return [];
  }

  const now = new Date();
  const cutoff = new Date(now.getTime() - hours * 60 * 60 * 1000);

  return logs.filter((log) => {
    const accessTime = new Date(log.accessed_at);
    return accessTime >= cutoff;
  });
}

/**
 * Get unique users who accessed the document
 */
export function getUniqueUsers(logs: DocumentAccess[] | undefined): string[] {
  if (!logs || logs.length === 0) {
    return [];
  }

  const userSet = new Set(logs.map((log) => log.user_id));
  return Array.from(userSet);
}

/**
 * Get action summary statistics
 */
export function getActionSummary(
  logs: DocumentAccess[] | undefined
): ActionSummary[] {
  if (!logs || logs.length === 0) {
    return [];
  }

  const grouped = groupByAction(logs);

  return Object.entries(grouped).map(([action, actionLogs]) => {
    const sorted = [...actionLogs].sort(
      (a, b) =>
        new Date(b.accessed_at).getTime() - new Date(a.accessed_at).getTime()
    );

    const uniqueUsers = new Set(actionLogs.map((log) => log.user_id));

    return {
      action_type: action as AccessAction,
      count: actionLogs.length,
      latest: sorted[0].accessed_at,
      users: Array.from(uniqueUsers),
    };
  });
}

/**
 * Filter logs by specific action type
 */
export function filterByActionType(
  logs: DocumentAccess[] | undefined,
  actionType: AccessAction | string
): DocumentAccess[] {
  if (!logs || logs.length === 0) {
    return [];
  }

  return logs.filter((log) => log.action_type === actionType);
}

/**
 * Get most recent access for each user
 */
export function getMostRecentAccessPerUser(
  logs: DocumentAccess[] | undefined
): Map<string, DocumentAccess> {
  if (!logs || logs.length === 0) {
    return new Map();
  }

  const userMap = new Map<string, DocumentAccess>();

  logs.forEach((log) => {
    const existing = userMap.get(log.user_id);
    if (
      !existing ||
      new Date(log.accessed_at) > new Date(existing.accessed_at)
    ) {
      userMap.set(log.user_id, log);
    }
  });

  return userMap;
}

/**
 * Calculate access frequency statistics
 */
export function getAccessStatistics(logs: DocumentAccess[] | undefined): {
  total_accesses: number;
  unique_users: number;
  most_common_action: string | null;
  first_access: string | null;
  last_access: string | null;
  actions_by_type: Record<string, number>;
} {
  if (!logs || logs.length === 0) {
    return {
      total_accesses: 0,
      unique_users: 0,
      most_common_action: null,
      first_access: null,
      last_access: null,
      actions_by_type: {},
    };
  }

  const uniqueUsers = getUniqueUsers(logs);
  const actionCounts: Record<string, number> = {};

  logs.forEach((log) => {
    actionCounts[log.action_type] = (actionCounts[log.action_type] || 0) + 1;
  });

  const mostCommonAction =
    Object.entries(actionCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;

  const sorted = [...logs].sort(
    (a, b) =>
      new Date(a.accessed_at).getTime() - new Date(b.accessed_at).getTime()
  );

  return {
    total_accesses: logs.length,
    unique_users: uniqueUsers.length,
    most_common_action: mostCommonAction,
    first_access: sorted[0]?.accessed_at || null,
    last_access: sorted[sorted.length - 1]?.accessed_at || null,
    actions_by_type: actionCounts,
  };
}

/**
 * Format time difference for display
 */
export function formatTimeSince(timestamp: string): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();

  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return days + ' day' + (days > 1 ? 's' : '') + ' ago';
  if (hours > 0) return hours + ' hour' + (hours > 1 ? 's' : '') + ' ago';
  if (minutes > 0) return minutes + ' minute' + (minutes > 1 ? 's' : '') + ' ago';
  return 'Just now';
}
