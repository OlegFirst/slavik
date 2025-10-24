/**
 * PlanCard Component
 * Professional card display for business continuity plans
 * Planning Module Round 3 - Agent 8
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { BCPlan } from '@/types/planning';
import { PlanTypeBadge } from './badges/PlanTypeBadge';
import { PlanStatusBadge } from './badges/PlanStatusBadge';
import { Calendar, Target, DollarSign, Users, Clock, Activity, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PlanCardProps {
  plan: BCPlan;
  layout?: 'grid' | 'list';
  onClick?: () => void;
  showActions?: boolean;
  className?: string;
}

/**
 * PlanCard displays a business continuity plan in card format
 *
 * Features:
 * - Plan name, code, type, status badges
 * - Scope description
 * - Key metrics: RTO, cost, update date, processes count
 * - Click to navigate to detail page
 * - Responsive grid/list layouts
 */
export function PlanCard({
  plan,
  layout = 'grid',
  onClick,
  showActions = true,
  className
}: PlanCardProps) {
  const isGridLayout = layout === 'grid';

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    }
  };

  // Calculate days since last update
  const daysSinceUpdate = Math.floor(
    (Date.now() - new Date(plan.updated_at).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div
      className={cn(
        'bg-white rounded-xl border transition-all duration-200',
        'hover:shadow-xl hover:border-blue-300',
        onClick && 'cursor-pointer',
        isGridLayout
          ? 'p-6 shadow-lg'
          : 'p-4 shadow-md flex items-start gap-4',
        className
      )}
      onClick={handleCardClick}
      role="article"
      aria-label={`Business Continuity Plan: ${plan.plan_name}`}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {/* Main Content */}
      <div className={cn('flex-1', isGridLayout ? 'space-y-4' : 'space-y-2')}>
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {isGridLayout && plan.plan_code && (
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {plan.plan_code}
                </span>
                <span className="text-xs text-gray-400">v{plan.plan_version}</span>
              </div>
            )}

            <h3
              className={cn(
                'font-semibold text-gray-900 group-hover:text-blue-600 transition-colors',
                isGridLayout ? 'text-lg mb-1' : 'text-base',
                !isGridLayout && 'line-clamp-1'
              )}
            >
              {plan.plan_name}
            </h3>

            {/* Type Badge */}
            <div className="flex items-center gap-2 mt-2">
              <PlanTypeBadge type={plan.plan_type} />
            </div>
          </div>

          {/* Status Badge - Top right */}
          {isGridLayout && (
            <PlanStatusBadge status={plan.status} />
          )}
        </div>

        {/* Description */}
        {isGridLayout && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {plan.scope_description}
          </p>
        )}

        {/* Key Metrics Grid */}
        <div className={cn(
          'grid gap-3',
          isGridLayout ? 'grid-cols-2' : 'grid-cols-1'
        )}>
          {/* RTO Target */}
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-1 mb-1">
              <Target className="w-3 h-3 text-blue-700" />
              <p className="text-xs text-blue-700 font-medium">RTO Target</p>
            </div>
            <p className="text-2xl font-bold text-blue-900">
              {plan.rto_target}
            </p>
            <p className="text-xs text-blue-600 mt-0.5">minutes</p>
          </div>

          {/* Estimated Cost */}
          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
            <div className="flex items-center gap-1 mb-1">
              <DollarSign className="w-3 h-3 text-green-700" />
              <p className="text-xs text-green-700 font-medium">Estimated Cost</p>
            </div>
            <p className="text-2xl font-bold text-green-900">
              ${(plan.estimated_cost / 1000).toFixed(0)}k
            </p>
            <p className="text-xs text-green-600 mt-0.5">
              ${plan.estimated_cost.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Secondary Metrics */}
        {isGridLayout && (
          <div className="grid grid-cols-2 gap-3">
            {/* RPO Target */}
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-purple-500" />
              <div>
                <p className="text-xs text-gray-500">RPO</p>
                <p className="text-sm font-semibold text-gray-900">
                  {plan.rpo_target} min
                </p>
              </div>
            </div>

            {/* MTPD Target */}
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-orange-500" />
              <div>
                <p className="text-xs text-gray-500">MTPD</p>
                <p className="text-sm font-semibold text-gray-900">
                  {plan.mtpd_target} min
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Footer Metadata */}
        <div className={cn(
          'flex items-center justify-between text-sm pt-3 border-t border-gray-100',
          !isGridLayout && 'flex-wrap gap-2'
        )}>
          <div className="flex items-center gap-4 flex-wrap">
            {/* Last Updated */}
            <span
              className="inline-flex items-center gap-1 text-gray-600"
              title={`Last updated: ${new Date(plan.updated_at).toLocaleString()}`}
            >
              <Calendar className="w-4 h-4 text-gray-400" aria-hidden="true" />
              <span className="text-xs">
                {daysSinceUpdate === 0 ? 'Today' : `${daysSinceUpdate}d ago`}
              </span>
            </span>

            {/* Applicable Processes Count */}
            <span
              className="inline-flex items-center gap-1 text-gray-600"
              title={`${plan.applicable_processes.length} applicable processes`}
            >
              <Users className="w-4 h-4 text-gray-400" aria-hidden="true" />
              <span className="text-xs">
                {plan.applicable_processes.length} processes
              </span>
            </span>

            {/* Covered Risks Count */}
            {isGridLayout && plan.covered_risks && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`${plan.covered_risks.length} covered risks`}
              >
                <Activity className="w-4 h-4 text-gray-400" aria-hidden="true" />
                <span className="text-xs">
                  {plan.covered_risks.length} risks
                </span>
              </span>
            )}
          </div>

          {/* Arrow Icon */}
          {showActions && onClick && (
            <ArrowRight
              className="w-5 h-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all flex-shrink-0"
              aria-hidden="true"
            />
          )}
        </div>

        {/* Actions */}
        {showActions && !onClick && isGridLayout && (
          <div className="flex gap-3 pt-4 border-t border-gray-100">
            <Link
              href={`/planning/plans/${plan.id}`}
              className="flex-1 text-center px-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              View Details
            </Link>
            <Link
              href={`/planning/plans/${plan.id}/edit`}
              className="flex-1 text-center px-4 py-2 text-sm text-gray-600 hover:text-gray-700 font-medium bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Edit Plan
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
