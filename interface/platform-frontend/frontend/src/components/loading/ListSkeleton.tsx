'use client';

import React from 'react';
import { LoadingSkeleton } from './LoadingSkeleton';

/**
 * Props for the ListSkeleton component
 */
export interface ListSkeletonProps {
  /** Number of list items to display */
  items?: number;
  /** Show avatar */
  showAvatar?: boolean;
  /** Show action buttons */
  showActions?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * ListSkeleton component
 *
 * A skeleton loader for list views with avatar and text layout.
 * Supports configurable item count and optional action buttons.
 *
 * @example
 * ```tsx
 * <ListSkeleton items={5} />
 * <ListSkeleton items={3} showAvatar showActions />
 * ```
 */
export const ListSkeleton: React.FC<ListSkeletonProps> = ({
  items = 5,
  showAvatar = true,
  showActions = true,
  className = '',
}) => {
  return (
    <div className={`space-y-4 ${className}`} role="status" aria-label="Loading list">
      {Array.from({ length: items }).map((_, index) => (
        <div
          key={index}
          className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
        >
          <div className="flex items-center space-x-4 flex-1">
            {showAvatar && <LoadingSkeleton variant="circle" size={48} />}

            <div className="flex-1 space-y-2">
              <LoadingSkeleton variant="text" width="40%" height={20} />
              <LoadingSkeleton variant="text" width="60%" height={16} />
            </div>
          </div>

          {showActions && (
            <div className="flex space-x-2 ml-4">
              <LoadingSkeleton variant="rectangle" width={80} height={36} />
              <LoadingSkeleton variant="rectangle" width={80} height={36} />
            </div>
          )}
        </div>
      ))}

      <span className="sr-only">Loading list items</span>
    </div>
  );
};

export default ListSkeleton;
