/**
 * React Query Helper Utilities
 *
 * Provides utility functions for common React Query operations
 * like invalidation, prefetching, and optimistic updates.
 *
 * @module queryHelpers
 */

import { queryClient } from './queryClient';
import type { QueryKey, QueryFunction } from '@tanstack/react-query';

/**
 * Invalidate all queries for a specific resource
 *
 * Marks all queries matching the resource key as stale,
 * triggering a refetch if they are currently being observed.
 *
 * @param resource - The resource name or query key prefix
 *
 * @example
 * ```typescript
 * // Invalidate all document queries
 * invalidateResource('documents');
 *
 * // After a successful mutation
 * await createDocument(data);
 * invalidateResource('documents');
 * ```
 */
export async function invalidateResource(resource: string): Promise<void> {
  await queryClient.invalidateQueries({ queryKey: [resource] });
}

/**
 * Invalidate multiple resources at once
 *
 * @param resources - Array of resource names to invalidate
 *
 * @example
 * ```typescript
 * // Invalidate both documents and BIA after a complex operation
 * await invalidateMultipleResources(['documents', 'bia']);
 * ```
 */
export async function invalidateMultipleResources(resources: string[]): Promise<void> {
  await Promise.all(
    resources.map(resource => queryClient.invalidateQueries({ queryKey: [resource] }))
  );
}

/**
 * Prefetch a query
 *
 * Fetches data in advance and stores it in the cache.
 * Useful for improving perceived performance.
 *
 * @param queryKey - The query key
 * @param queryFn - The query function to execute
 * @param staleTime - Optional stale time in milliseconds
 *
 * @example
 * ```typescript
 * // Prefetch a document when hovering over a link
 * const handleMouseEnter = () => {
 *   prefetchQuery(
 *     queryKeys.documentDetail(123),
 *     () => fetchDocument(123)
 *   );
 * };
 * ```
 */
export async function prefetchQuery<T>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  staleTime?: number
): Promise<void> {
  await queryClient.prefetchQuery({
    queryKey,
    queryFn,
    staleTime,
  });
}

/**
 * Set query data optimistically
 *
 * Immediately updates the cached data without waiting for a server response.
 * Useful for optimistic UI updates.
 *
 * @param queryKey - The query key
 * @param updater - Function to update the data, or the new data directly
 *
 * @example
 * ```typescript
 * // Optimistically update a document in the list
 * setOptimisticData(
 *   queryKeys.documentsList({}),
 *   (old) => old?.map(doc =>
 *     doc.id === 123 ? { ...doc, title: 'New Title' } : doc
 *   )
 * );
 * ```
 */
export function setOptimisticData<T>(
  queryKey: QueryKey,
  updater: T | ((old: T | undefined) => T)
): void {
  queryClient.setQueryData(queryKey, updater);
}

/**
 * Get current query data from cache
 *
 * Retrieves the current cached data for a query without triggering a fetch.
 *
 * @param queryKey - The query key
 * @returns The cached data or undefined
 *
 * @example
 * ```typescript
 * const currentDoc = getQueryData(queryKeys.documentDetail(123));
 * if (currentDoc) {
 *   console.log('Document is cached:', currentDoc);
 * }
 * ```
 */
export function getQueryData<T>(queryKey: QueryKey): T | undefined {
  return queryClient.getQueryData<T>(queryKey);
}

/**
 * Cancel ongoing queries
 *
 * Cancels any in-flight queries matching the query key.
 * Useful before performing optimistic updates.
 *
 * @param queryKey - The query key
 *
 * @example
 * ```typescript
 * // Cancel pending queries before optimistic update
 * await cancelQueries(queryKeys.documentsList({}));
 * setOptimisticData(queryKeys.documentsList({}), newData);
 * ```
 */
export async function cancelQueries(queryKey: QueryKey): Promise<void> {
  await queryClient.cancelQueries({ queryKey });
}

/**
 * Remove a query from the cache
 *
 * Completely removes a query and its data from the cache.
 * Different from invalidation which keeps the data but marks it stale.
 *
 * @param queryKey - The query key
 *
 * @example
 * ```typescript
 * // Remove a deleted document from cache
 * await deleteDocument(123);
 * removeQuery(queryKeys.documentDetail(123));
 * ```
 */
export function removeQuery(queryKey: QueryKey): void {
  queryClient.removeQueries({ queryKey });
}

/**
 * Reset all queries
 *
 * Clears all cached data and resets the query cache.
 * Use sparingly, typically only on logout or major state changes.
 *
 * @example
 * ```typescript
 * // Clear all cached data on logout
 * const handleLogout = async () => {
 *   await logout();
 *   resetQueries();
 *   navigate('/login');
 * };
 * ```
 */
export function resetQueries(): void {
  queryClient.resetQueries();
}

/**
 * Clear all cached data
 *
 * Removes all queries from the cache without resetting the query client.
 *
 * @example
 * ```typescript
 * // Clear cache when switching tenants
 * clearCache();
 * ```
 */
export function clearCache(): void {
  queryClient.clear();
}

/**
 * Check if a query is fetching
 *
 * @param queryKey - The query key to check
 * @returns true if the query is currently fetching
 *
 * @example
 * ```typescript
 * if (isQueryFetching(queryKeys.documentsList({}))) {
 *   console.log('Documents are being fetched');
 * }
 * ```
 */
export function isQueryFetching(queryKey: QueryKey): boolean {
  return queryClient.isFetching({ queryKey }) > 0;
}

/**
 * Fetch a query imperatively
 *
 * Executes a query and returns the result, similar to prefetch
 * but returns the data.
 *
 * @param queryKey - The query key
 * @param queryFn - The query function to execute
 * @returns The query result
 *
 * @example
 * ```typescript
 * const document = await fetchQuery(
 *   queryKeys.documentDetail(123),
 *   () => fetchDocument(123)
 * );
 * ```
 */
export async function fetchQuery<T>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>
): Promise<T> {
  return queryClient.fetchQuery({ queryKey, queryFn });
}
