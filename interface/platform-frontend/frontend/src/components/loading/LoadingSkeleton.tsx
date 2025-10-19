'use client';

import React from 'react';

/**
 * Skeleton variant types
 */
export type SkeletonVariant = 'text' | 'circle' | 'rectangle' | 'card';

/**
 * Props for the LoadingSkeleton component
 */
export interface LoadingSkeletonProps {
  /** Variant type */
  variant?: SkeletonVariant;
  /** Width in pixels or percentage string */
  width?: number | string;
  /** Height in pixels or percentage string */
  height?: number | string;
  /** Size for circle variant */
  size?: number;
  /** Number of lines for text variant */
  lines?: number;
  /** Custom className */
  className?: string;
}

/**
 * LoadingSkeleton component
 *
 * A flexible skeleton loader with multiple variants and animated shimmer effect.
 * Supports text, circle, rectangle, and card layouts.
 *
 * @example
 * ```tsx
 * <Skeleton variant="text" width={200} />
 * <Skeleton variant="circle" size={40} />
 * <Skeleton variant="rectangle" width={300} height={200} />
 * <Skeleton variant="card" />
 * ```
 */
export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'text',
  width,
  height,
  size,
  lines = 1,
  className = '',
}) => {
  const getStyles = (): React.CSSProperties => {
    const styles: React.CSSProperties = {};

    if (variant === 'circle' && size) {
      styles.width = `${size}px`;
      styles.height = `${size}px`;
    } else {
      if (width !== undefined) {
        styles.width = typeof width === 'number' ? `${width}px` : width;
      }
      if (height !== undefined) {
        styles.height = typeof height === 'number' ? `${height}px` : height;
      }
    }

    return styles;
  };

  const baseClasses = 'bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%] animate-shimmer';

  if (variant === 'text') {
    if (lines === 1) {
      return (
        <div
          className={`${baseClasses} h-4 rounded ${className}`}
          style={getStyles()}
          role="status"
          aria-label="Loading content"
        />
      );
    }

    return (
      <div className={`space-y-3 ${className}`} role="status" aria-label="Loading content">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`${baseClasses} h-4 rounded`}
            style={{
              width: index === lines - 1 ? '80%' : '100%',
              ...getStyles(),
            }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'circle') {
    return (
      <div
        className={`${baseClasses} rounded-full ${className}`}
        style={getStyles()}
        role="status"
        aria-label="Loading content"
      />
    );
  }

  if (variant === 'rectangle') {
    return (
      <div
        className={`${baseClasses} rounded-lg ${className}`}
        style={getStyles()}
        role="status"
        aria-label="Loading content"
      />
    );
  }

  if (variant === 'card') {
    return (
      <div className={`border border-gray-200 rounded-lg p-6 ${className}`} role="status" aria-label="Loading card">
        <div className={`${baseClasses} h-6 w-3/4 rounded mb-4`} />
        <div className="space-y-3">
          <div className={`${baseClasses} h-4 rounded`} />
          <div className={`${baseClasses} h-4 rounded w-5/6`} />
          <div className={`${baseClasses} h-4 rounded w-4/6`} />
        </div>
      </div>
    );
  }

  return null;
};

export default LoadingSkeleton;
