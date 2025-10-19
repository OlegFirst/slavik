'use client';

import React from 'react';
import { LoadingSkeleton } from './LoadingSkeleton';

/**
 * Props for the CardSkeleton component
 */
export interface CardSkeletonProps {
  /** Number of cards to display */
  count?: number;
  /** Show header skeleton */
  showHeader?: boolean;
  /** Show footer skeleton */
  showFooter?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * CardSkeleton component
 *
 * A skeleton loader that matches DocumentCard layout.
 * Includes header, content lines, and footer sections with proper spacing.
 *
 * @example
 * ```tsx
 * <CardSkeleton />
 * <CardSkeleton count={3} />
 * <CardSkeleton showFooter={false} />
 * ```
 */
export const CardSkeleton: React.FC<CardSkeletonProps> = ({
  count = 1,
  showHeader = true,
  showFooter = true,
  className = '',
}) => {
  const SingleCard = () => (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm" role="status" aria-label="Loading card">
      {showHeader && (
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <LoadingSkeleton variant="text" width="60%" height={24} />
            <div className="mt-2">
              <LoadingSkeleton variant="text" width="40%" height={16} />
            </div>
          </div>
          <LoadingSkeleton variant="circle" size={40} />
        </div>
      )}

      <div className="space-y-3 mb-4">
        <LoadingSkeleton variant="text" width="100%" />
        <LoadingSkeleton variant="text" width="95%" />
        <LoadingSkeleton variant="text" width="80%" />
      </div>

      {showFooter && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex space-x-2">
            <LoadingSkeleton variant="rectangle" width={60} height={24} />
            <LoadingSkeleton variant="rectangle" width={80} height={24} />
          </div>
          <LoadingSkeleton variant="text" width={100} height={16} />
        </div>
      )}

      <span className="sr-only">Loading card content</span>
    </div>
  );

  if (count === 1) {
    return <SingleCard />;
  }

  return (
    <div className={`grid gap-6 ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <SingleCard key={index} />
      ))}
    </div>
  );
};

export default CardSkeleton;
