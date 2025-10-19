'use client';

import React from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, RefreshCw, WifiOff } from 'lucide-react';

/**
 * Props for the QueryErrorBoundary component
 */
export interface QueryErrorBoundaryProps {
  /** Child components to render */
  children: React.ReactNode;
  /** Query keys to reset on error */
  queryKeys?: string[];
  /** Callback when an error is caught */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Custom fallback component */
  fallback?: React.ComponentType<QueryErrorFallbackProps>;
}

/**
 * Props passed to the query error fallback component
 */
export interface QueryErrorFallbackProps {
  error: Error;
  onReset: () => void;
  onRetryQuery: () => void;
}

/**
 * State for the QueryErrorBoundary component
 */
interface QueryErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Determines if an error is a network error
 */
function isNetworkError(error: Error): boolean {
  const networkErrorMessages = [
    'network error',
    'failed to fetch',
    'networkerror',
    'network request failed',
    'load failed',
  ];

  const message = error.message.toLowerCase();
  return networkErrorMessages.some((msg) => message.includes(msg));
}

/**
 * Determines if an error is an API error
 */
function isAPIError(error: Error): boolean {
  // Check if error has response status (axios-like error)
  return 'response' in error || 'status' in error;
}

/**
 * Default fallback component for query errors
 */
const DefaultQueryErrorFallback: React.FC<QueryErrorFallbackProps> = ({
  error,
  onReset,
  onRetryQuery,
}) => {
  const isNetwork = isNetworkError(error);
  const isAPI = isAPIError(error);

  return (
    <div className="min-h-[300px] flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 border border-red-100">
        {/* Error Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            {isNetwork ? (
              <WifiOff className="w-6 h-6 text-red-600" aria-hidden="true" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-red-600" aria-hidden="true" />
            )}
          </div>
        </div>

        {/* Error Title */}
        <div className="text-center mb-4">
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            {isNetwork ? 'Connection Error' : isAPI ? 'API Error' : 'Data Error'}
          </h2>
          <p className="text-sm text-gray-600">
            {isNetwork
              ? 'Unable to connect to the server. Please check your internet connection.'
              : isAPI
              ? 'The server returned an error. Please try again.'
              : 'An error occurred while fetching data.'
            }
          </p>
        </div>

        {/* Error Message */}
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <p className="text-sm text-red-900">{error.message}</p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          <button
            onClick={onRetryQuery}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors text-sm font-medium"
            aria-label="Retry query"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Query
          </button>
          <button
            onClick={onReset}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium"
            aria-label="Reset and clear cache"
          >
            Reset & Clear Cache
          </button>
        </div>

        {/* Help Text */}
        {isNetwork && (
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              Make sure you are connected to the internet and try again.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Query Error Boundary Component
 *
 * React Query specific error boundary with cache reset functionality.
 * Handles network errors, API errors, and provides query retry capabilities.
 *
 * @example
 * ```tsx
 * <QueryErrorBoundary queryKeys={['users', 'posts']}>
 *   <UsersList />
 * </QueryErrorBoundary>
 * ```
 */
export class QueryErrorBoundary extends React.Component<
  QueryErrorBoundaryProps,
  QueryErrorBoundaryState
> {
  constructor(props: QueryErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  /**
   * Update state when an error is caught
   */
  static getDerivedStateFromError(error: Error): Partial<QueryErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Log error details
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    const { onError } = this.props;

    console.error('Query Error Boundary caught error:', error, errorInfo);

    // Call custom error handler
    if (onError) {
      onError(error, errorInfo);
    }
  }

  /**
   * Reset error state
   */
  resetErrorBoundary = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render(): React.ReactNode {
    const { hasError, error } = this.state;
    const { children, fallback: CustomFallback, queryKeys } = this.props;

    if (hasError && error) {
      return (
        <QueryErrorFallbackWrapper
          error={error}
          queryKeys={queryKeys}
          onReset={this.resetErrorBoundary}
          CustomFallback={CustomFallback}
        />
      );
    }

    return children;
  }
}

/**
 * Wrapper component to use React Query hooks in fallback
 */
const QueryErrorFallbackWrapper: React.FC<{
  error: Error;
  queryKeys?: string[];
  onReset: () => void;
  CustomFallback?: React.ComponentType<QueryErrorFallbackProps>;
}> = ({ error, queryKeys, onReset, CustomFallback }) => {
  const queryClient = useQueryClient();

  /**
   * Retry query by invalidating query cache
   */
  const handleRetryQuery = (): void => {
    if (queryKeys && queryKeys.length > 0) {
      // Invalidate specific queries
      queryKeys.forEach((key) => {
        queryClient.invalidateQueries({ queryKey: [key] });
      });
    } else {
      // Invalidate all queries
      queryClient.invalidateQueries();
    }
    onReset();
  };

  /**
   * Reset and clear all cache
   */
  const handleReset = (): void => {
    if (queryKeys && queryKeys.length > 0) {
      // Remove specific queries
      queryKeys.forEach((key) => {
        queryClient.removeQueries({ queryKey: [key] });
      });
    } else {
      // Clear all cache
      queryClient.clear();
    }
    onReset();
  };

  const fallbackProps: QueryErrorFallbackProps = {
    error,
    onReset: handleReset,
    onRetryQuery: handleRetryQuery,
  };

  // Use custom fallback if provided
  if (CustomFallback) {
    return <CustomFallback {...fallbackProps} />;
  }

  // Default fallback
  return <DefaultQueryErrorFallback {...fallbackProps} />;
};

export default QueryErrorBoundary;
