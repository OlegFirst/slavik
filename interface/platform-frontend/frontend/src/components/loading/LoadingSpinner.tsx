'use client';

import React from 'react';

/**
 * Size variants for the loading spinner
 */
export type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';

/**
 * Color variants for the loading spinner
 */
export type SpinnerColor = 'primary' | 'secondary' | 'white';

/**
 * Props for the LoadingSpinner component
 */
export interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: SpinnerSize;
  /** Color variant */
  color?: SpinnerColor;
  /** Optional text label */
  label?: string;
  /** Center the spinner */
  centered?: boolean;
  /** Custom className */
  className?: string;
  /** Accessible label for screen readers */
  ariaLabel?: string;
}

/**
 * LoadingSpinner component
 *
 * A configurable loading spinner with size and color variants.
 * Includes accessibility features and optional text label.
 *
 * @example
 * ```tsx
 * <LoadingSpinner size="md" color="primary" label="Loading..." />
 * <LoadingSpinner size="lg" centered />
 * ```
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  label,
  centered = false,
  className = '',
  ariaLabel = 'Loading',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-[3px]',
    xl: 'w-12 h-12 border-[3px]',
  };

  const colorClasses = {
    primary: 'border-gray-200 border-t-orange-500',
    secondary: 'border-gray-200 border-t-amber-600',
    white: 'border-white/30 border-t-white',
  };

  const textColorClasses = {
    primary: 'text-gray-700',
    secondary: 'text-amber-700',
    white: 'text-white',
  };

  return (
    <div
      className={`${centered ? 'flex justify-center items-center' : 'inline-flex items-center'} ${className}`}
      role="status"
      aria-label={ariaLabel}
    >
      <div
        className={`
          ${sizeClasses[size]}
          ${colorClasses[color]}
          rounded-full
          animate-spin
        `}
      />
      {label && (
        <span className={`ml-3 text-sm font-medium ${textColorClasses[color]}`}>
          {label}
        </span>
      )}
      <span className="sr-only">{ariaLabel}</span>
    </div>
  );
};

export default LoadingSpinner;
