'use client';

import React, { Suspense } from 'react';
import { ErrorBoundary, ErrorBoundaryProps } from './ErrorBoundary';
import { LoadingSpinner } from '../loading/LoadingSpinner';

/**
 * Props for the AsyncBoundary component
 */
export interface AsyncBoundaryProps {
  /** Child components to render */
  children: React.ReactNode;
  /** Fallback component to show while loading */
  suspenseFallback?: React.ReactNode;
  /** Fallback component to show on error */
  errorFallback?: ErrorBoundaryProps['fallback'];
  /** Callback when an error is caught */
  onError?: ErrorBoundaryProps['onError'];
  /** Custom boundary name for logging */
  boundaryName?: string;
  /** Timeout in milliseconds before showing timeout error */
  timeout?: number;
  /** Loading message to display */
  loadingMessage?: string;
}

/**
 * State for timeout handling
 */
interface AsyncBoundaryState {
  timedOut: boolean;
}

/**
 * Default loading fallback component
 */
const DefaultLoadingFallback: React.FC<{ message?: string }> = ({ message }) => (
  <div className="flex flex-col items-center justify-center min-h-[300px] p-6">
    <LoadingSpinner size="lg" color="primary" />
    {message && (
      <p className="mt-4 text-sm text-gray-600 font-medium">{message}</p>
    )}
  </div>
);

/**
 * Timeout error component
 */
const TimeoutError: React.FC<{ onRetry: () => void }> = ({ onRetry }) => (
  <div className="flex flex-col items-center justify-center min-h-[300px] p-6">
    <div className="text-center max-w-md">
      <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg
          className="w-6 h-6 text-amber-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading Timeout</h3>
      <p className="text-sm text-gray-600 mb-4">
        This is taking longer than expected. Please check your connection and try again.
      </p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors text-sm font-medium"
      >
        Retry
      </button>
    </div>
  </div>
);

/**
 * Async Boundary Component
 *
 * Combines React Suspense with Error Boundary for comprehensive
 * async component handling. Includes loading states, error handling,
 * and optional timeout functionality.
 *
 * @example
 * ```tsx
 * <AsyncBoundary
 *   suspenseFallback={<LoadingSpinner />}
 *   loadingMessage="Loading data..."
 *   timeout={10000}
 *   onError={(error) => console.error(error)}
 * >
 *   <AsyncComponent />
 * </AsyncBoundary>
 * ```
 */
export class AsyncBoundary extends React.Component<
  AsyncBoundaryProps,
  AsyncBoundaryState
> {
  private timeoutId?: NodeJS.Timeout;

  constructor(props: AsyncBoundaryProps) {
    super(props);
    this.state = {
      timedOut: false,
    };
  }

  componentDidMount(): void {
    this.startTimeout();
  }

  componentWillUnmount(): void {
    this.clearTimeout();
  }

  componentDidUpdate(prevProps: AsyncBoundaryProps): void {
    // Reset timeout if children change
    if (prevProps.children !== this.props.children) {
      this.setState({ timedOut: false });
      this.clearTimeout();
      this.startTimeout();
    }
  }

  /**
   * Start timeout timer if timeout is specified
   */
  startTimeout = (): void => {
    const { timeout } = this.props;

    if (timeout && timeout > 0) {
      this.timeoutId = setTimeout(() => {
        this.setState({ timedOut: true });
      }, timeout);
    }
  };

  /**
   * Clear timeout timer
   */
  clearTimeout = (): void => {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = undefined;
    }
  };

  /**
   * Retry after timeout
   */
  handleRetry = (): void => {
    this.setState({ timedOut: false });
    this.clearTimeout();
    this.startTimeout();
  };

  render(): React.ReactNode {
    const {
      children,
      suspenseFallback,
      errorFallback,
      onError,
      boundaryName,
      loadingMessage,
    } = this.props;
    const { timedOut } = this.state;

    // Show timeout error if timed out
    if (timedOut) {
      return <TimeoutError onRetry={this.handleRetry} />;
    }

    // Determine loading fallback
    const loadingFallback = suspenseFallback || (
      <DefaultLoadingFallback message={loadingMessage} />
    );

    return (
      <ErrorBoundary
        fallback={errorFallback}
        onError={(error, errorInfo) => {
          this.clearTimeout();
          if (onError) {
            onError(error, errorInfo);
          }
        }}
        boundaryName={boundaryName || 'AsyncBoundary'}
      >
        <Suspense fallback={loadingFallback}>
          {children}
        </Suspense>
      </ErrorBoundary>
    );
  }
}

export default AsyncBoundary;
