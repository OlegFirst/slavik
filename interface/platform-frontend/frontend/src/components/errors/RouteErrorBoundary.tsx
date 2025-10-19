'use client';

import React from 'react';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

/**
 * Props for the RouteErrorBoundary component
 */
export interface RouteErrorBoundaryProps {
  /** Child components to render */
  children: React.ReactNode;
  /** Route name for error context */
  routeName?: string;
  /** Callback when an error is caught */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Custom fallback component */
  fallback?: React.ComponentType<RouteErrorFallbackProps>;
}

/**
 * Props passed to the route error fallback component
 */
export interface RouteErrorFallbackProps {
  error: Error;
  routeName?: string;
  onReset: () => void;
}

/**
 * State for the RouteErrorBoundary component
 */
interface RouteErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Default fallback component for route errors
 */
const DefaultRouteErrorFallback: React.FC<RouteErrorFallbackProps> = ({
  error,
  routeName,
  onReset,
}) => {
  const handleGoHome = (): void => {
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  return (
    <div className="min-h-[400px] flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 border border-orange-100">
        {/* Error Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-orange-600" aria-hidden="true" />
          </div>
        </div>

        {/* Error Title */}
        <div className="text-center mb-4">
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Page Error
          </h2>
          <p className="text-sm text-gray-600">
            {routeName
              ? `An error occurred while loading ${routeName}`
              : 'An error occurred while loading this page'
            }
          </p>
        </div>

        {/* Error Message */}
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <p className="text-sm text-red-900">{error.message}</p>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={onReset}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors text-sm font-medium"
            aria-label="Try again"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          <button
            onClick={handleGoHome}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium"
            aria-label="Go to home page"
          >
            <Home className="w-4 h-4" />
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Route-level Error Boundary Component
 *
 * A lighter-weight error boundary for individual routes/pages.
 * Provides less disruptive error handling than the root error boundary.
 * Automatically resets when the route changes.
 *
 * @example
 * ```tsx
 * <RouteErrorBoundary routeName="Dashboard">
 *   <DashboardPage />
 * </RouteErrorBoundary>
 * ```
 */
export class RouteErrorBoundary extends React.Component<
  RouteErrorBoundaryProps,
  RouteErrorBoundaryState
> {
  constructor(props: RouteErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  /**
   * Update state when an error is caught
   */
  static getDerivedStateFromError(error: Error): Partial<RouteErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Log error details
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    const { onError, routeName } = this.props;

    console.error(`Route Error [${routeName || 'Unknown Route'}]:`, error, errorInfo);

    // Call custom error handler
    if (onError) {
      onError(error, errorInfo);
    }
  }

  /**
   * Reset error state when route changes
   */
  componentDidUpdate(prevProps: RouteErrorBoundaryProps): void {
    if (this.state.hasError && prevProps.routeName !== this.props.routeName) {
      this.resetErrorBoundary();
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
    const { children, fallback: CustomFallback, routeName } = this.props;

    if (hasError && error) {
      const fallbackProps: RouteErrorFallbackProps = {
        error,
        routeName,
        onReset: this.resetErrorBoundary,
      };

      // Use custom fallback if provided
      if (CustomFallback) {
        return <CustomFallback {...fallbackProps} />;
      }

      // Default fallback
      return <DefaultRouteErrorFallback {...fallbackProps} />;
    }

    return children;
  }
}

export default RouteErrorBoundary;
