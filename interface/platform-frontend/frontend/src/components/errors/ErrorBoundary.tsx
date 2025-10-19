'use client';

import React from 'react';
import { ErrorFallback } from './ErrorFallback';

/**
 * Props for the ErrorBoundary component
 */
export interface ErrorBoundaryProps {
  /** Child components to render */
  children: React.ReactNode;
  /** Custom fallback component */
  fallback?: React.ComponentType<ErrorFallbackProps>;
  /** Callback when an error is caught */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Whether to reset error on location change */
  resetOnLocationChange?: boolean;
  /** Custom error boundary name for logging */
  boundaryName?: string;
}

/**
 * Props passed to the error fallback component
 */
export interface ErrorFallbackProps {
  error: Error;
  errorInfo: React.ErrorInfo | null;
  errorId: string;
  onReset: () => void;
  boundaryName?: string;
}

/**
 * State for the ErrorBoundary component
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  errorId: string;
}

/**
 * Generates a unique error ID for tracking and support
 */
function generateErrorId(): string {
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 9);
  return `ERR-${timestamp}-${randomStr}`.toUpperCase();
}

/**
 * Reports error to logging/monitoring service
 */
function reportError(
  error: Error,
  errorInfo: React.ErrorInfo,
  errorId: string,
  boundaryName?: string
): void {
  // In production, this would send to Sentry, LogRocket, etc.
  const isDevelopment = process.env.NODE_ENV === 'development';

  const errorReport = {
    errorId,
    boundaryName: boundaryName || 'RootErrorBoundary',
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    timestamp: new Date().toISOString(),
    userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'unknown',
    url: typeof window !== 'undefined' ? window.location.href : 'unknown',
  };

  if (isDevelopment) {
    console.group(`🚨 Error Boundary: ${errorReport.boundaryName}`);
    console.error('Error ID:', errorId);
    console.error('Error:', error);
    console.error('Error Info:', errorInfo);
    console.error('Full Report:', errorReport);
    console.groupEnd();
  } else {
    // Production: Send to error tracking service
    // Example: Sentry.captureException(error, { contexts: { errorReport } });
    console.error('Error Report:', errorReport);
  }

  // Send to backend logging endpoint
  if (typeof window !== 'undefined') {
    try {
      fetch('/api/errors/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorReport),
      }).catch(() => {
        // Silently fail if error reporting fails
      });
    } catch {
      // Silently fail
    }
  }
}

/**
 * Root-level Error Boundary Component
 *
 * Catches React errors and displays a fallback UI with error reporting.
 * Includes development mode features like stack traces and production-ready
 * error tracking with unique error IDs.
 *
 * @example
 * ```tsx
 * <ErrorBoundary
 *   onError={(error) => console.log('Error caught:', error)}
 *   boundaryName="MainApp"
 * >
 *   <App />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    };
  }

  /**
   * Update state when an error is caught
   */
  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: generateErrorId(),
    };
  }

  /**
   * Log error details and report to monitoring service
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    const { onError, boundaryName } = this.props;

    // Update state with error info
    this.setState({ errorInfo });

    // Generate error ID if not already set
    const errorId = this.state.errorId || generateErrorId();

    // Report error
    reportError(error, errorInfo, errorId, boundaryName);

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
      errorInfo: null,
      errorId: '',
    });
  };

  render(): React.ReactNode {
    const { hasError, error, errorInfo, errorId } = this.state;
    const { children, fallback: CustomFallback, boundaryName } = this.props;

    if (hasError && error) {
      const fallbackProps: ErrorFallbackProps = {
        error,
        errorInfo,
        errorId,
        onReset: this.resetErrorBoundary,
        boundaryName,
      };

      // Use custom fallback if provided
      if (CustomFallback) {
        return <CustomFallback {...fallbackProps} />;
      }

      // Default fallback
      return <ErrorFallback {...fallbackProps} />;
    }

    return children;
  }
}

export default ErrorBoundary;
