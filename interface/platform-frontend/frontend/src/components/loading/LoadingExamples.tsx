'use client';

import React from 'react';
import {
  LoadingSpinner,
  LoadingSkeleton,
  ProgressBar,
  CardSkeleton,
  TableSkeleton,
  ListSkeleton,
} from './index';

/**
 * LoadingExamples component
 *
 * A showcase of all loading components with various configurations.
 * Use this as a reference for implementing loading states in your application.
 *
 * @example
 * ```tsx
 * import LoadingExamples from '@/components/loading/LoadingExamples';
 *
 * // Display in a page or story
 * <LoadingExamples />
 * ```
 */
export default function LoadingExamples() {
  return (
    <div className="p-8 space-y-12 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900">Loading Components</h1>

      {/* Loading Spinners */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Loading Spinners</h2>
        <div className="bg-white p-6 rounded-lg shadow-sm space-y-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Sizes</p>
            <div className="flex items-center gap-6">
              <LoadingSpinner size="sm" label="Small" />
              <LoadingSpinner size="md" label="Medium" />
              <LoadingSpinner size="lg" label="Large" />
              <LoadingSpinner size="xl" label="Extra Large" />
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Colors</p>
            <div className="flex items-center gap-6">
              <LoadingSpinner color="primary" label="Primary" />
              <LoadingSpinner color="secondary" label="Secondary" />
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded">
            <LoadingSpinner color="white" label="White (on dark bg)" />
          </div>
        </div>
      </section>

      {/* Progress Bars */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Progress Bars</h2>
        <div className="bg-white p-6 rounded-lg shadow-sm space-y-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Linear Progress</p>
            <ProgressBar value={25} showPercentage />
            <ProgressBar value={50} color="secondary" showPercentage />
            <ProgressBar value={75} color="success" showPercentage />
            <ProgressBar indeterminate color="primary" />
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Circular Progress</p>
            <div className="flex items-center gap-6">
              <ProgressBar value={30} variant="circular" size="sm" showPercentage />
              <ProgressBar value={60} variant="circular" size="md" showPercentage />
              <ProgressBar value={90} variant="circular" size="lg" showPercentage />
            </div>
          </div>
        </div>
      </section>

      {/* Skeletons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Skeletons</h2>
        <div className="bg-white p-6 rounded-lg shadow-sm space-y-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Text Skeletons</p>
            <LoadingSkeleton variant="text" width={200} />
            <LoadingSkeleton variant="text" lines={3} />
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Shapes</p>
            <div className="flex items-center gap-4">
              <LoadingSkeleton variant="circle" size={40} />
              <LoadingSkeleton variant="circle" size={60} />
              <LoadingSkeleton variant="rectangle" width={120} height={80} />
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Card Skeleton</p>
            <LoadingSkeleton variant="card" />
          </div>
        </div>
      </section>

      {/* Card Skeleton */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Card Skeleton</h2>
        <CardSkeleton count={2} />
      </section>

      {/* List Skeleton */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">List Skeleton</h2>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <ListSkeleton items={3} />
        </div>
      </section>

      {/* Table Skeleton */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Table Skeleton</h2>
        <TableSkeleton rows={5} columns={4} alternating />
      </section>
    </div>
  );
}
