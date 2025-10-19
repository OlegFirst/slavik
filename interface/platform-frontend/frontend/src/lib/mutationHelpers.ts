/**
 * React Query Mutation Helpers
 *
 * Provides utility functions for handling mutations with
 * optimistic updates, rollback, and cache invalidation.
 *
 * @module mutationHelpers
 */

import { queryClient } from './queryClient';
import type { QueryKey, MutationOptions } from '@tanstack/react-query';

/**
 * Context returned by optimistic update
 */
interface OptimisticContext<T> {
  /**
   * Previous data before optimistic update
   */
  previous: T | undefined;
}

/**
 * Create optimistic update handlers for a mutation
 *
 * Returns mutation options that handle optimistic updates with automatic
 * rollback on error and refetch on success.
 *
 * @param queryKey - The query key to update optimistically
 * @param updateFn - Function to update the cached data with mutation variables
 * @returns Mutation options with onMutate, onError, and onSettled handlers
 *
 * @example
 * ```typescript
 * // Update a document optimistically
 * const mutation = useMutation({
 *   mutationFn: updateDocument,
 *   ...createOptimisticUpdate(
 *     queryKeys.documentDetail(123),
 *     (old, variables) => ({ ...old, ...variables })
 *   )
 * });
 * ```
 */
export function createOptimisticUpdate<T, V>(
  queryKey: QueryKey,
  updateFn: (old: T, variables: V) => T
): Pick<MutationOptions<unknown, unknown, V, OptimisticContext<T>>, 'onMutate' | 'onError' | 'onSettled'> {
  return {
    onMutate: async (variables: V) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey });

      // Snapshot the previous value
      const previous = queryClient.getQueryData<T>(queryKey);

      // Optimistically update to the new value
      if (previous !== undefined) {
        queryClient.setQueryData(queryKey, updateFn(previous, variables));
      }

      // Return context with previous value for rollback
      return { previous };
    },

    onError: (err: unknown, variables: V, context: OptimisticContext<T> | undefined) => {
      // Rollback to previous value on error
      if (context?.previous !== undefined) {
        queryClient.setQueryData(queryKey, context.previous);
      }
    },

    onSettled: () => {
      // Always refetch after error or success to ensure data consistency
      queryClient.invalidateQueries({ queryKey });
    },
  };
}

/**
 * Create optimistic list update handlers
 *
 * Specialized helper for updating lists (add, update, delete operations).
 *
 * @param queryKey - The query key for the list
 * @param operation - The type of operation (add, update, delete)
 * @param itemIdentifier - Function to identify items in the list
 * @returns Mutation options for list operations
 *
 * @example
 * ```typescript
 * // Delete a document from the list optimistically
 * const deleteMutation = useMutation({
 *   mutationFn: deleteDocument,
 *   ...createOptimisticListUpdate(
 *     queryKeys.documentsList({}),
 *     'delete',
 *     (item, id) => item.id === id
 *   )
 * });
 * ```
 */
export function createOptimisticListUpdate<T, V>(
  queryKey: QueryKey,
  operation: 'add' | 'update' | 'delete',
  itemIdentifier: (item: T, variables: V) => boolean
): Pick<MutationOptions<unknown, unknown, V, OptimisticContext<T[]>>, 'onMutate' | 'onError' | 'onSettled'> {
  return {
    onMutate: async (variables: V) => {
      await queryClient.cancelQueries({ queryKey });

      const previous = queryClient.getQueryData<T[]>(queryKey);

      if (previous !== undefined) {
        let updated: T[];

        switch (operation) {
          case 'add':
            updated = [...previous, variables as unknown as T];
            break;
          case 'update':
            updated = previous.map(item =>
              itemIdentifier(item, variables) ? { ...item, ...(variables as any) } : item
            );
            break;
          case 'delete':
            updated = previous.filter(item => !itemIdentifier(item, variables));
            break;
        }

        queryClient.setQueryData(queryKey, updated);
      }

      return { previous };
    },

    onError: (err: unknown, variables: V, context: OptimisticContext<T[]> | undefined) => {
      if (context?.previous !== undefined) {
        queryClient.setQueryData(queryKey, context.previous);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  };
}

/**
 * Create mutation handlers with automatic invalidation
 *
 * Simpler alternative to optimistic updates - just invalidates
 * the cache on success.
 *
 * @param queryKeys - Query keys to invalidate on success
 * @returns Mutation options with onSuccess handler
 *
 * @example
 * ```typescript
 * const mutation = useMutation({
 *   mutationFn: createDocument,
 *   ...createMutationWithInvalidation([
 *     queryKeys.documentsList({}),
 *     queryKeys.dashboardMetrics('7d')
 *   ])
 * });
 * ```
 */
export function createMutationWithInvalidation(
  queryKeys: QueryKey[]
): Pick<MutationOptions<unknown, unknown, unknown, unknown>, 'onSuccess'> {
  return {
    onSuccess: async () => {
      await Promise.all(
        queryKeys.map(key => queryClient.invalidateQueries({ queryKey: key }))
      );
    },
  };
}

/**
 * Create mutation handlers with manual cache update
 *
 * Directly updates the cache with the mutation result instead of refetching.
 * More efficient than invalidation for simple updates.
 *
 * @param queryKey - The query key to update
 * @param updateFn - Function to update cached data with mutation result
 * @returns Mutation options with onSuccess handler
 *
 * @example
 * ```typescript
 * const mutation = useMutation({
 *   mutationFn: updateDocument,
 *   ...createMutationWithCacheUpdate(
 *     queryKeys.documentDetail(123),
 *     (old, result) => ({ ...old, ...result })
 *   )
 * });
 * ```
 */
export function createMutationWithCacheUpdate<T, R>(
  queryKey: QueryKey,
  updateFn: (old: T | undefined, result: R) => T
): Pick<MutationOptions<R, unknown, unknown, unknown>, 'onSuccess'> {
  return {
    onSuccess: (result: R) => {
      const old = queryClient.getQueryData<T>(queryKey);
      const updated = updateFn(old, result);
      queryClient.setQueryData(queryKey, updated);
    },
  };
}

/**
 * Reset mutation state
 *
 * Clears error and data from a mutation, useful for form resets.
 * Note: This requires access to the mutation instance.
 *
 * @param mutationKey - The mutation key (optional)
 *
 * @example
 * ```typescript
 * const mutation = useMutation({
 *   mutationFn: createDocument,
 *   mutationKey: ['createDocument']
 * });
 *
 * // Later, reset the mutation
 * resetMutation(['createDocument']);
 * ```
 */
export function resetMutation(mutationKey?: QueryKey): void {
  if (mutationKey) {
    queryClient.resetQueries({ queryKey: mutationKey });
  }
}
