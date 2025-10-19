'use client';

import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';
import { ProgressBar } from './ProgressBar';

/**
 * Props for the PageLoader component
 */
export interface PageLoaderProps {
  /** Loading message to display */
  message?: string;
  /** Show logo/branding */
  showLogo?: boolean;
  /** Progress value (0-100) for progress bar */
  progress?: number;
  /** Custom className */
  className?: string;
}

/**
 * PageLoader component
 *
 * A full-page loading screen with overlay, spinner, and optional progress bar.
 * Prevents user interaction while loading and provides visual feedback.
 *
 * @example
 * ```tsx
 * <PageLoader message="Loading application..." />
 * <PageLoader message="Processing..." progress={75} />
 * <PageLoader showLogo />
 * ```
 */
export const PageLoader: React.FC<PageLoaderProps> = ({
  message = 'Loading...',
  showLogo = true,
  progress,
  className = '',
}) => {
  return (
    <div
      className={`
        fixed inset-0 z-50
        flex flex-col items-center justify-center
        bg-gradient-to-br from-orange-50 via-amber-50 to-orange-100
        animate-fadeIn
        ${className}
      `}
      role="status"
      aria-live="polite"
      aria-label="Page loading"
    >
      <div className="flex flex-col items-center space-y-6">
        {showLogo && (
          <div className="mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-amber-600 rounded-2xl shadow-lg flex items-center justify-center">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
          </div>
        )}

        <LoadingSpinner size="xl" color="primary" />

        {message && (
          <p className="text-lg font-medium text-gray-700 animate-pulse">
            {message}
          </p>
        )}

        {progress !== undefined && (
          <div className="w-64">
            <ProgressBar value={progress} max={100} color="primary" />
            <p className="text-sm text-gray-600 text-center mt-2">
              {progress}% complete
            </p>
          </div>
        )}
      </div>

      <span className="sr-only">{message}</span>
    </div>
  );
};

export default PageLoader;
