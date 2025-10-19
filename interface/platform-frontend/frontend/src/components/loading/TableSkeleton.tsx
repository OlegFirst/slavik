'use client';

import React from 'react';
import { LoadingSkeleton } from './LoadingSkeleton';

/**
 * Props for the TableSkeleton component
 */
export interface TableSkeletonProps {
  /** Number of rows to display */
  rows?: number;
  /** Number of columns */
  columns?: number;
  /** Show alternating row colors */
  alternating?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * TableSkeleton component
 *
 * A skeleton loader for table views with configurable rows and columns.
 * Includes header row and supports alternating row colors.
 *
 * @example
 * ```tsx
 * <TableSkeleton rows={5} columns={4} />
 * <TableSkeleton rows={10} columns={6} alternating />
 * ```
 */
export const TableSkeleton: React.FC<TableSkeletonProps> = ({
  rows = 5,
  columns = 4,
  alternating = false,
  className = '',
}) => {
  return (
    <div
      className={`w-full overflow-hidden border border-gray-200 rounded-lg ${className}`}
      role="status"
      aria-label="Loading table"
    >
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          {/* Table Header */}
          <thead className="bg-gray-50">
            <tr>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <th
                  key={colIndex}
                  className="px-6 py-3 text-left"
                >
                  <LoadingSkeleton
                    variant="text"
                    width={colIndex === 0 ? 150 : 100}
                    height={16}
                  />
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="bg-white divide-y divide-gray-200">
            {Array.from({ length: rows }).map((_, rowIndex) => (
              <tr
                key={rowIndex}
                className={alternating && rowIndex % 2 === 1 ? 'bg-gray-50' : 'bg-white'}
              >
                {Array.from({ length: columns }).map((_, colIndex) => (
                  <td key={colIndex} className="px-6 py-4">
                    <LoadingSkeleton
                      variant="text"
                      width={
                        colIndex === 0
                          ? 180
                          : colIndex === columns - 1
                          ? 80
                          : 120
                      }
                      height={16}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <span className="sr-only">Loading table data</span>
    </div>
  );
};

export default TableSkeleton;
