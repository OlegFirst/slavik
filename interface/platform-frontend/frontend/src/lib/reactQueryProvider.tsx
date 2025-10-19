/**
 * React Query Provider Component
 *
 * Wraps the application with QueryClientProvider and includes
 * development tools, focus management, and online status handling.
 *
 * @module reactQueryProvider
 */

'use client';

import React, { useEffect } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './queryClient';

/**
 * Props for ReactQueryProvider component
 */
interface ReactQueryProviderProps {
  /**
   * Child components to wrap with React Query context
   */
  children: React.ReactNode;
}

/**
 * React Query Provider Component
 *
 * Sets up the React Query context for the entire application.
 * Includes:
 * - QueryClientProvider with configured client
 * - DevTools (development only)
 * - Online status management
 * - Window focus management
 *
 * @example
 * ```tsx
 * // In your root layout or app component
 * function App() {
 *   return (
 *     <ReactQueryProvider>
 *       <YourApp />
 *     </ReactQueryProvider>
 *   );
 * }
 * ```
 */
export function ReactQueryProvider({ children }: ReactQueryProviderProps) {
  useEffect(() => {
    // Set up online status listener
    const handleOnline = () => {
      queryClient.resumePausedMutations();
    };

    const handleOffline = () => {
      // Queries will automatically pause when offline due to networkMode: 'online'
      console.info('[React Query] Network connection lost - queries paused');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools
          initialIsOpen={false}
        />
      )}
    </QueryClientProvider>
  );
}

/**
 * Hook to check if React Query DevTools are available
 *
 * @returns true if running in development mode
 */
export function useDevToolsAvailable(): boolean {
  return process.env.NODE_ENV === 'development';
}

/**
 * Custom hook for online status
 *
 * Provides the current online/offline status of the browser.
 * Automatically updates when the connection status changes.
 *
 * @returns true if browser is online, false otherwise
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const isOnline = useOnlineStatus();
 *
 *   if (!isOnline) {
 *     return <div>You are currently offline</div>;
 *   }
 *
 *   return <div>Connected</div>;
 * }
 * ```
 */
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = React.useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

/**
 * Hook to access the global query client
 *
 * Useful for imperative operations like invalidation or prefetching
 * outside of React Query hooks.
 *
 * @returns The global QueryClient instance
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const client = useQueryClient();
 *
 *   const handleRefresh = () => {
 *     client.invalidateQueries({ queryKey: ['documents'] });
 *   };
 *
 *   return <button onClick={handleRefresh}>Refresh</button>;
 * }
 * ```
 */
export { useQueryClient } from '@tanstack/react-query';
