'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, RefreshCw, Home, Copy, Check, ChevronDown, ChevronUp, Mail } from 'lucide-react';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function PlatformError({ error, reset }: ErrorProps) {
  const [errorId] = useState(() => `ERR-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  useEffect(() => {
    // Log error to reporting service
    console.error('Platform Error:', {
      message: error.message,
      digest: error.digest,
      errorId,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      location: window.location.href,
    });

    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error);
    }
  }, [error, errorId]);

  const handleReset = async () => {
    setIsRetrying(true);
    await new Promise(resolve => setTimeout(resolve, 500));
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
    <div className="flex items-center justify-center min-h-[calc(100vh-200px)] px-4 py-12">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden border-2 border-orange-100">
          {/* Error Header - Compact for platform layout */}
          <div className="bg-gradient-to-r from-orange-500 to-amber-600 p-6 text-white">
            <div className="flex items-center gap-4">
              {/* Icon */}
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-white/20 rounded-full blur-lg animate-pulse" />
                <div className="relative bg-white/20 backdrop-blur-sm rounded-full p-3">
                  <AlertTriangle className="w-8 h-8 text-white" />
                </div>
              </div>

              <div className="flex-1">
                <h1 className="text-2xl font-bold mb-1">
                  Something Went Wrong
                </h1>
                <p className="text-orange-100">
                  We encountered an unexpected error in this section.
                </p>
              </div>
            </div>
          </div>

          {/* Error Content */}
          <div className="p-6">
            {/* Error ID Badge */}
            <div className="mb-6 p-4 bg-orange-50 border-2 border-orange-100 rounded-lg">
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-muted-foreground mb-1">Error Reference ID</div>
                  <div className="font-mono text-sm font-semibold text-foreground truncate">
                    {errorId}
                  </div>
                  {error.digest && (
                    <div className="text-xs text-muted-foreground mt-1">
                      Digest: {error.digest}
                    </div>
                  )}
                </div>
                <button
                  onClick={copyErrorDetails}
                  className="flex-shrink-0 p-2 hover:bg-orange-100 rounded-lg transition-colors"
                  title="Copy error details"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4 text-orange-600" />
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
                {error.message || 'An unexpected error occurred while loading this page.'}
              </p>
            </div>

            {/* Development Mode - Error Details */}
            {isDevelopment && error.stack && (
              <div className="mb-6">
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="flex items-center gap-2 text-sm font-medium text-orange-600 hover:text-orange-700 transition-colors mb-3"
                >
                  {showDetails ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      Hide Technical Details
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      Show Technical Details (Dev Mode)
                    </>
                  )}
                </button>

                {showDetails && (
                  <div className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-auto max-h-80">
                    <pre className="text-xs font-mono whitespace-pre-wrap break-all">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <button
                onClick={handleReset}
                disabled={isRetrying}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 disabled:from-orange-300 disabled:to-amber-400 text-white font-medium rounded-lg transition-all shadow-md hover:shadow-lg disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${isRetrying ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">{isRetrying ? 'Retrying...' : 'Try Again'}</span>
                <span className="sm:hidden">{isRetrying ? 'Retry' : 'Retry'}</span>
              </button>

              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-white border-2 border-orange-200 hover:border-orange-300 text-foreground font-medium rounded-lg transition-all"
              >
                <Home className="w-4 h-4" />
                <span className="hidden sm:inline">Dashboard</span>
                <span className="sm:hidden">Home</span>
              </Link>
            </div>

            {/* Compact Help Section */}
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Need Help?
              </h3>
              <p className="text-xs text-muted-foreground mb-3">
                If this error persists, contact support with the error reference ID.
              </p>
              <div className="flex flex-wrap gap-3 text-sm">
                <a
                  href="mailto:support@aiplatform.com"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  Email Support
                </a>
                <Link
                  href="/help"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  Help Center
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-4 text-center text-xs text-muted-foreground">
          This error has been logged automatically for investigation.
        </div>
      </div>
    </div>
  );
}
