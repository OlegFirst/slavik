'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, Home, RefreshCw, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  const [errorId] = useState(() => `ERR-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  useEffect(() => {
    // Log error to reporting service
    console.error('Application Error:', {
      message: error.message,
      digest: error.digest,
      errorId,
      stack: error.stack,
      timestamp: new Date().toISOString(),
    });

    // In production, send to error tracking service (e.g., Sentry)
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error);
    }
  }, [error, errorId]);

  const handleReset = async () => {
    setIsRetrying(true);
    await new Promise(resolve => setTimeout(resolve, 500)); // Brief delay for UX
    reset();
  };

  const copyErrorDetails = () => {
    const errorDetails = `
Error ID: ${errorId}
Digest: ${error.digest || 'N/A'}
Message: ${error.message}
Timestamp: ${new Date().toISOString()}
User Agent: ${navigator.userAgent}
URL: ${window.location.href}
${error.stack ? `\nStack Trace:\n${error.stack}` : ''}
    `.trim();

    navigator.clipboard.writeText(errorDetails);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-amber-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Error Header */}
          <div className="bg-gradient-to-r from-orange-500 to-amber-600 p-8 text-white">
            <div className="flex items-start gap-4">
              {/* Animated Icon */}
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-white/20 rounded-full blur-xl animate-pulse" />
                <div className="relative bg-white/20 backdrop-blur-sm rounded-full p-4">
                  <AlertTriangle className="w-12 h-12 text-white" />
                </div>
              </div>

              <div className="flex-1">
                <h1 className="text-3xl font-bold mb-2">
                  Something Went Wrong
                </h1>
                <p className="text-orange-100 text-lg">
                  We encountered an unexpected error. Don't worry, our team has been notified.
                </p>
              </div>
            </div>
          </div>

          {/* Error Content */}
          <div className="p-8">
            {/* Error ID */}
            <div className="mb-6 p-4 bg-orange-50 border-2 border-orange-100 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Error Reference ID</div>
                  <div className="font-mono text-sm font-semibold text-foreground">{errorId}</div>
                  {error.digest && (
                    <div className="text-xs text-muted-foreground mt-1">
                      Digest: {error.digest}
                    </div>
                  )}
                </div>
                <button
                  onClick={copyErrorDetails}
                  className="p-2 hover:bg-orange-100 rounded-lg transition-colors"
                  title="Copy error details"
                >
                  {copied ? (
                    <Check className="w-5 h-5 text-green-600" />
                  ) : (
                    <Copy className="w-5 h-5 text-orange-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Error Message */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">
                What happened?
              </h3>
              <p className="text-foreground">
                {error.message || 'An unexpected error occurred while processing your request.'}
              </p>
            </div>

            {/* Development Mode - Error Details */}
            {isDevelopment && error.stack && (
              <div className="mb-6">
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="flex items-center gap-2 text-sm font-medium text-orange-600 hover:text-orange-700 transition-colors"
                >
                  {showDetails ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      Hide Technical Details
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      Show Technical Details
                    </>
                  )}
                </button>

                {showDetails && (
                  <div className="mt-4 p-4 bg-gray-900 text-gray-100 rounded-lg overflow-auto max-h-96">
                    <pre className="text-xs font-mono whitespace-pre-wrap break-all">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <button
                onClick={handleReset}
                disabled={isRetrying}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 disabled:from-orange-300 disabled:to-amber-400 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${isRetrying ? 'animate-spin' : ''}`} />
                {isRetrying ? 'Retrying...' : 'Try Again'}
              </button>

              <Link
                href="/"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-orange-200 hover:border-orange-300 text-foreground font-medium rounded-lg transition-all"
              >
                <Home className="w-4 h-4" />
                Go Home
              </Link>
            </div>

            {/* Help Section */}
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="text-sm font-medium text-foreground mb-2">
                Need assistance?
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                If this problem persists, please contact our support team with the error reference ID above.
              </p>
              <div className="flex flex-wrap gap-4 text-sm">
                <a
                  href="mailto:support@aiplatform.com"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  support@aiplatform.com
                </a>
                <Link
                  href="/help"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  Help Center
                </Link>
                <Link
                  href="/status"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  System Status
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>
            This error has been automatically logged and our team will investigate.
          </p>
        </div>
      </div>
    </div>
  );
}
