/**
 * PlanList Component
 * List container for displaying multiple business continuity plans
 * Planning Module Round 3 - Agent 8
 */

'use client';

import React from 'react';
import { BCPlan } from '@/types/planning';
import { PlanCard } from './PlanCard';
import { FileText, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PlanListProps {
  plans: BCPlan[];
  loading?: boolean;
  emptyMessage?: string;
  emptyDescription?: string;
  layout?: 'grid' | 'list';
  onPlanClick?: (plan: BCPlan) => void;
  showActions?: boolean;
  className?: string;
}

/**
 * PlanList displays a collection of business continuity plans
 *
 * Features:
 * - Grid or list layout
 * - Loading skeleton states
 * - Empty state with custom message
 * - Click handlers for plan navigation
 * - Responsive design
 */
export function PlanList({
  plans,
  loading = false,
  emptyMessage = 'No plans found',
  emptyDescription = 'Create your first business continuity plan to get started.',
  layout = 'grid',
  onPlanClick,
  showActions = true,
  className
}: PlanListProps) {
  // Loading State
  if (loading) {
    return (
      <div
        className={cn(
          'space-y-4',
          layout === 'grid' && 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
          className
        )}
      >
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="bg-gray-100 rounded-xl h-80 animate-pulse flex items-center justify-center"
            role="status"
            aria-label="Loading plans"
          >
            <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
          </div>
        ))}
      </div>
    );
  }

  // Empty State
  if (plans.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <div className="bg-blue-50 rounded-full p-6 mb-4">
          <FileText className="w-12 h-12 text-blue-500" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {emptyMessage}
        </h3>
        <p className="text-sm text-gray-500 max-w-md mb-6">
          {emptyDescription}
        </p>
        <button
          type="button"
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          onClick={() => {
            // This would typically navigate to create plan page
            console.log('Create new plan clicked');
          }}
        >
          Create Plan
        </button>
      </div>
    );
  }

  // Plans Grid/List View
  return (
    <div
      className={cn(
        layout === 'grid'
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
          : 'space-y-4',
        className
      )}
    >
      {plans.map((plan) => (
        <PlanCard
          key={plan.id}
          plan={plan}
          layout={layout}
          onClick={onPlanClick ? () => onPlanClick(plan) : undefined}
          showActions={showActions}
        />
      ))}
    </div>
  );
}

/**
 * PlanListHeader Component
 * Optional header for plan lists with count and view toggle
 */
export interface PlanListHeaderProps {
  title?: string;
  count?: number;
  layout?: 'grid' | 'list';
  onLayoutChange?: (layout: 'grid' | 'list') => void;
}

export function PlanListHeader({
  title = 'Business Continuity Plans',
  count,
  layout = 'grid',
  onLayoutChange
}: PlanListHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {count !== undefined && (
          <p className="text-sm text-gray-500 mt-1">
            {count} {count === 1 ? 'plan' : 'plans'} total
          </p>
        )}
      </div>

      {onLayoutChange && (
        <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
          <button
            type="button"
            onClick={() => onLayoutChange('grid')}
            className={cn(
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              layout === 'grid'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
            aria-label="Grid view"
          >
            Grid
          </button>
          <button
            type="button"
            onClick={() => onLayoutChange('list')}
            className={cn(
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              layout === 'list'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
            aria-label="List view"
          >
            List
          </button>
        </div>
      )}
    </div>
  );
}
