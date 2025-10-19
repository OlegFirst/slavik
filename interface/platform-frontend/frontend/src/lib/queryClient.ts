/**
 * React Query Client Configuration
 *
 * Production-ready QueryClient with optimized defaults for caching,
 * refetching, and error handling.
 *
 * @module queryClient
 */

import { QueryClient } from '@tanstack/react-query';

/**
 * Global QueryClient instance with production-ready defaults
 *
 * Configuration includes:
 * - Intelligent caching with 5min stale time
 * - Automatic refetching on focus/reconnect
 * - Exponential backoff retry strategy
 * - Proper error handling
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Caching configuration
      staleTime: 5 * 60 * 1000, // 5 minutes - data considered fresh
      gcTime: 10 * 60 * 1000, // 10 minutes - garbage collection time (formerly cacheTime)

      // Refetching behavior
      refetchOnWindowFocus: true, // Refetch when user focuses window
      refetchOnReconnect: true, // Refetch when network reconnects
      refetchOnMount: true, // Refetch when component mounts

      // Retry configuration
      retry: 3, // Number of retry attempts
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff, max 30s

      // Error handling
      throwOnError: false, // Don't throw errors, handle them in components

      // Network mode
      networkMode: 'online', // Only run queries when online
    },
    mutations: {
      // Retry configuration for mutations
      retry: 1, // Retry once on failure
      retryDelay: 1000, // 1 second delay before retry

      // Error handling
      throwOnError: false, // Don't throw errors, handle them in components

      // Network mode
      networkMode: 'online', // Only run mutations when online
    },
  },
});

/**
 * Type-safe query key factory
 *
 * Provides a centralized, hierarchical structure for all query keys.
 * This ensures consistency and makes invalidation easier.
 *
 * @example
 * ```typescript
 * // Use in a query
 * useQuery({
 *   queryKey: queryKeys.documentDetail(123),
 *   queryFn: () => fetchDocument(123)
 * })
 *
 * // Invalidate all documents
 * queryClient.invalidateQueries({ queryKey: queryKeys.documents() })
 * ```
 */
export const queryKeys = {
  /**
   * Root key for all application queries
   */
  all: ['app'] as const,

  // ==========================================
  // Authentication & User Management
  // ==========================================

  /**
   * Base key for all auth-related queries
   */
  auth: () => [...queryKeys.all, 'auth'] as const,

  /**
   * Current authenticated user
   */
  user: () => [...queryKeys.auth(), 'user'] as const,

  /**
   * Tenant information by ID
   * @param tenantId - Unique tenant identifier
   */
  tenant: (tenantId: string) => [...queryKeys.auth(), 'tenant', tenantId] as const,

  // ==========================================
  // Documents
  // ==========================================

  /**
   * Base key for all document queries
   */
  documents: () => [...queryKeys.all, 'documents'] as const,

  /**
   * Document list with filters
   * @param filters - Filter parameters for document list
   */
  documentsList: (filters: Record<string, any>) => [...queryKeys.documents(), 'list', filters] as const,

  /**
   * Single document detail by ID
   * @param id - Document ID
   */
  documentDetail: (id: number) => [...queryKeys.documents(), 'detail', id] as const,

  /**
   * Document versions by document ID
   * @param documentId - Parent document ID
   */
  documentVersions: (documentId: number) => [...queryKeys.documents(), 'versions', documentId] as const,

  // ==========================================
  // Business Impact Analysis (BIA)
  // ==========================================

  /**
   * Base key for all BIA queries
   */
  bia: () => [...queryKeys.all, 'bia'] as const,

  /**
   * BIA list with filters
   * @param filters - Filter parameters for BIA list
   */
  biaList: (filters: Record<string, any>) => [...queryKeys.bia(), 'list', filters] as const,

  /**
   * Single BIA detail by ID
   * @param id - BIA ID
   */
  biaDetail: (id: number) => [...queryKeys.bia(), 'detail', id] as const,

  // ==========================================
  // AI & Conversations
  // ==========================================

  /**
   * Base key for all AI queries
   */
  ai: () => [...queryKeys.all, 'ai'] as const,

  /**
   * List of AI conversations
   */
  aiConversations: () => [...queryKeys.ai(), 'conversations'] as const,

  /**
   * Single AI conversation by ID
   * @param id - Conversation ID
   */
  aiConversation: (id: string) => [...queryKeys.ai(), 'conversation', id] as const,

  /**
   * AI chat messages for a conversation
   * @param conversationId - Conversation ID
   */
  aiMessages: (conversationId: string) => [...queryKeys.ai(), 'messages', conversationId] as const,

  // ==========================================
  // Workflows
  // ==========================================

  /**
   * Base key for all workflow queries
   */
  workflows: () => [...queryKeys.all, 'workflows'] as const,

  /**
   * Workflow list with filters
   * @param filters - Filter parameters for workflow list
   */
  workflowsList: (filters: Record<string, any>) => [...queryKeys.workflows(), 'list', filters] as const,

  /**
   * Single workflow detail by ID
   * @param id - Workflow ID
   */
  workflowDetail: (id: string) => [...queryKeys.workflows(), 'detail', id] as const,

  // ==========================================
  // Analytics & Metrics
  // ==========================================

  /**
   * Base key for all analytics queries
   */
  analytics: () => [...queryKeys.all, 'analytics'] as const,

  /**
   * Dashboard metrics
   * @param timeRange - Time range for metrics (e.g., '7d', '30d')
   */
  dashboardMetrics: (timeRange: string) => [...queryKeys.analytics(), 'dashboard', timeRange] as const,

  /**
   * System health metrics
   */
  systemHealth: () => [...queryKeys.analytics(), 'system-health'] as const,
};
