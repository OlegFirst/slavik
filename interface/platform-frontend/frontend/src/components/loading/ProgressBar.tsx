'use client';

import React from 'react';

/**
 * Progress bar variant types
 */
export type ProgressVariant = 'linear' | 'circular';

/**
 * Progress bar color variants
 */
export type ProgressColor = 'primary' | 'secondary' | 'success' | 'warning';

/**
 * Progress bar size variants
 */
export type ProgressSize = 'sm' | 'md' | 'lg';

/**
 * Props for the ProgressBar component
 */
export interface ProgressBarProps {
  /** Current progress value */
  value?: number;
  /** Maximum value */
  max?: number;
  /** Indeterminate loading state */
  indeterminate?: boolean;
  /** Variant type */
  variant?: ProgressVariant;
  /** Color variant */
  color?: ProgressColor;
  /** Size variant */
  size?: ProgressSize;
  /** Show percentage */
  showPercentage?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * ProgressBar component
 *
 * A flexible progress indicator supporting both determinate and indeterminate states.
 * Available in linear and circular variants with multiple color and size options.
 *
 * @example
 * ```tsx
 * <ProgressBar value={75} max={100} />
 * <ProgressBar indeterminate />
 * <ProgressBar value={30} variant="circular" size="lg" />
 * ```
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  value = 0,
  max = 100,
  indeterminate = false,
  variant = 'linear',
  color = 'primary',
  size = 'md',
  showPercentage = false,
  className = '',
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const colorClasses = {
    primary: 'bg-orange-500',
    secondary: 'bg-amber-600',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
  };

  const sizeClasses = {
    linear: {
      sm: 'h-1',
      md: 'h-2',
      lg: 'h-3',
    },
    circular: {
      sm: 'w-12 h-12',
      md: 'w-16 h-16',
      lg: 'w-24 h-24',
    },
  };

  if (variant === 'circular') {
    const strokeWidth = size === 'sm' ? 4 : size === 'md' ? 5 : 6;
    const radius = size === 'sm' ? 20 : size === 'md' ? 28 : 42;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = indeterminate ? 0 : circumference - (percentage / 100) * circumference;

    return (
      <div className={`relative inline-flex items-center justify-center ${className}`} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max}>
        <svg className={sizeClasses.circular[size]} viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${colorClasses[color]} transition-all duration-300 ${indeterminate ? 'animate-spin' : ''}`}
            style={{
              transform: 'rotate(-90deg)',
              transformOrigin: '50% 50%',
            }}
          />
        </svg>
        {showPercentage && !indeterminate && (
          <span className="absolute text-sm font-semibold text-gray-700">
            {Math.round(percentage)}%
          </span>
        )}
      </div>
    );
  }

  // Linear variant
  return (
    <div className={className} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max}>
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses.linear[size]}`}>
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-300 ${
            indeterminate ? 'animate-indeterminate' : ''
          }`}
          style={{
            width: indeterminate ? '30%' : `${percentage}%`,
          }}
        />
      </div>
      {showPercentage && !indeterminate && (
        <p className="text-sm text-gray-600 mt-1 text-center">
          {Math.round(percentage)}%
        </p>
      )}
    </div>
  );
};

export default ProgressBar;
