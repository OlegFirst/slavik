'use client';

import React, { useState } from 'react';
import { AlertTriangle, Home, RefreshCw, Mail, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import type { ErrorFallbackProps } from './ErrorBoundary';

/**
 * Generic Error Fallback UI Component
 *
 * Displays a user-friendly error message with options to:
 * - Retry/reset the error boundary
 * - Navigate home
 * - Contact support
 * - View error details (collapsible)
 * - Copy error information
 *
 * @example
 * ```tsx
 * <ErrorFallback
 *   error={error}
 *   errorInfo={errorInfo}
 *   errorId="ERR-123"
 *   onReset={() => window.location.reload()}
 * />
 * ```
 */
export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorInfo,
  errorId,
  onReset,
  boundaryName,
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const isDevelopment = process.env.NODE_ENV === 'development';

  /**
   * Navigate to home page
   */
  const handleGoHome = (): void => {
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  /**
   * Open email client with pre-filled error details
   */
  const handleContactSupport = (): void => {
    const subject = encodeURIComponent(`Error Report: ${errorId}`);
    const body = encodeURIComponent(
      `Error ID: ${errorId}\n` +
      `Error Message: ${error.message}\n` +
      `Boundary: ${boundaryName || 'Unknown'}\n` +
      `Time: ${new Date().toISOString()}\n\n` +
      `Please describe what you were doing when this error occurred:`
    );
    window.location.href = `mailto:support@example.com?subject=${subject}&body=${body}`;
  };

  /**
   * Copy error details to clipboard
   */
  const handleCopyError = async (): Promise<void> => {
    const errorDetails = formatErrorDetails();

    try {
      await navigator.clipboard.writeText(errorDetails);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy error details:', err);
    }
  };

  /**
   * Format error details for copying
   */
  const formatErrorDetails = (): string => {
    return [
      `Error ID: ${errorId}`,
      `Boundary: ${boundaryName || 'Unknown'}`,
      `Time: ${new Date().toISOString()}`,
      `Message: ${error.message}`,
      '',
      'Stack Trace:',
      error.stack || 'No stack trace available',
      '',
      'Component Stack:',
      errorInfo?.componentStack || 'No component stack available',
    ].join('\n');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-amber-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8 border border-red-100">
        {/* Error Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-red-600" aria-hidden="true" />
          </div>
        </div>

        {/* Error Title */}
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Oops! Something went wrong
          </h1>
          <p className="text-gray-600">
            We apologize for the inconvenience. The application encountered an unexpected error.
          </p>
        </div>

        {/* Error ID */}
        <div className="bg-gray-50 border border-gray-200 rounded-md p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Error ID</p>
              <p className="text-lg font-mono text-gray-900">{errorId}</p>
              {boundaryName && (
                <p className="text-xs text-gray-500 mt-1">Boundary: {boundaryName}</p>
              )}
            </div>
            <button
              onClick={handleCopyError}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              aria-label="Copy error details"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy
                </>
              )}
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <button
            onClick={onReset}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors font-medium"
            aria-label="Try again"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          <button
            onClick={handleGoHome}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors font-medium"
            aria-label="Go to home page"
          >
            <Home className="w-4 h-4" />
            Go Home
          </button>
          <button
            onClick={handleContactSupport}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors font-medium"
            aria-label="Contact support"
          >
            <Mail className="w-4 h-4" />
            Contact Support
          </button>
        </div>

        {/* Error Details (Collapsible) */}
        <div className="border-t border-gray-200 pt-4">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
            aria-expanded={showDetails}
            aria-controls="error-details"
          >
            <span>{showDetails ? 'Hide' : 'Show'} Error Details</span>
            {showDetails ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          {showDetails && (
            <div id="error-details" className="mt-4 space-y-4">
              {/* Error Message */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Error Message</h3>
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-900 font-mono">{error.message}</p>
                </div>
              </div>

              {/* Stack Trace (Development Only) */}
              {isDevelopment && error.stack && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Stack Trace</h3>
                  <div className="bg-gray-900 rounded-md p-3 overflow-x-auto">
                    <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap">
                      {error.stack}
                    </pre>
                  </div>
                </div>
              )}

              {/* Component Stack */}
              {errorInfo?.componentStack && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Component Stack</h3>
                  <div className="bg-gray-50 border border-gray-200 rounded-md p-3 overflow-x-auto">
                    <pre className="text-xs text-gray-700 font-mono whitespace-pre-wrap">
                      {errorInfo.componentStack}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            If this problem persists, please contact support with the Error ID above.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ErrorFallback;
