/**
 * ActionCard Component
 * Professional card display for action plans
 * Planning Module Round 3 - Agent 8
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { ActionPlan } from '@/types/planning';
import { ActionTypeBadge } from './badges/ActionTypeBadge';
import { PriorityBadge } from './badges/PriorityBadge';
import { ActionStatusBadge } from './badges/ActionStatusBadge';
import {
  User,
  Calendar,
  Link2,
  AlertCircle,
  ArrowRight,
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ActionCardProps {
  action: ActionPlan;
  layout?: 'grid' | 'list';
  onClick?: () => void;
  showActions?: boolean;
  className?: string;
}

/**
 * ActionCard displays an action plan in card format
 *
 * Features:
 * - Action title, type badge, priority badge, status badge
 * - Responsible party
 * - Progress percentage with visual bar
 * - Target date with urgency indicator
 * - Dependencies count
 * - Completion status
 */
export function ActionCard({
  action,
  layout = 'grid',
  onClick,
  showActions = true,
  className
}: ActionCardProps) {
  const isGridLayout = layout === 'grid';

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    }
  };

  // Calculate urgency based on target date
  const getUrgencyStatus = () => {
    if (!action.target_date) return null;

    const daysUntilDue = Math.ceil(
      (new Date(action.target_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
    );

    if (daysUntilDue < 0) return { status: 'overdue', text: 'Overdue', color: 'red' };
    if (daysUntilDue === 0) return { status: 'today', text: 'Due Today', color: 'orange' };
    if (daysUntilDue <= 3) return { status: 'urgent', text: `${daysUntilDue}d left`, color: 'yellow' };
    return { status: 'normal', text: `${daysUntilDue}d left`, color: 'gray' };
  };

  const urgency = getUrgencyStatus();

  // Get progress bar color based on status and progress
  const getProgressColor = () => {
    if (action.status === 'completed') return 'bg-green-500';
    if (action.status === 'delayed') return 'bg-red-500';
    if (action.progress_percentage >= 75) return 'bg-blue-500';
    if (action.progress_percentage >= 50) return 'bg-teal-500';
    if (action.progress_percentage >= 25) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  return (
    <div
      className={cn(
        'bg-white rounded-xl border transition-all duration-200',
        'hover:shadow-xl hover:border-purple-300',
        onClick && 'cursor-pointer',
        isGridLayout
          ? 'p-6 shadow-lg'
          : 'p-4 shadow-md flex items-start gap-4',
        className
      )}
      onClick={handleCardClick}
      role="article"
      aria-label={`Action Plan: ${action.action_title}`}
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
            <h3
              className={cn(
                'font-semibold text-gray-900 group-hover:text-purple-600 transition-colors',
                isGridLayout ? 'text-lg mb-2' : 'text-base mb-1',
                !isGridLayout && 'line-clamp-1'
              )}
            >
              {action.action_title}
            </h3>

            {/* Badges Row */}
            <div className="flex items-center gap-2 flex-wrap">
              <ActionTypeBadge type={action.action_type} />
              <PriorityBadge priority={action.priority} />
              {!isGridLayout && <ActionStatusBadge status={action.status} />}
            </div>
          </div>

          {/* Status Badge - Top right for grid layout */}
          {isGridLayout && (
            <ActionStatusBadge status={action.status} />
          )}
        </div>

        {/* Description */}
        {isGridLayout && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {action.description}
          </p>
        )}

        {/* Progress Section */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-700">Progress</span>
            <span className="text-xs font-bold text-gray-900">
              {action.progress_percentage}%
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className={cn(
                'h-full transition-all duration-500',
                getProgressColor()
              )}
              style={{ width: `${action.progress_percentage}%` }}
              role="progressbar"
              aria-valuenow={action.progress_percentage}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
        </div>

        {/* Responsible Party & Target Date */}
        <div className="grid grid-cols-2 gap-3">
          {/* Responsible Party */}
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-purple-500 flex-shrink-0" />
            <div className="min-w-0">
              <p className="text-xs text-gray-500">Responsible</p>
              <p className="text-sm font-semibold text-gray-900 truncate">
                {action.responsible_party}
              </p>
            </div>
          </div>

          {/* Target Date */}
          {action.target_date && (
            <div className="flex items-center gap-2">
              <Calendar className={cn(
                'w-4 h-4 flex-shrink-0',
                urgency?.status === 'overdue' && 'text-red-500',
                urgency?.status === 'today' && 'text-orange-500',
                urgency?.status === 'urgent' && 'text-yellow-500',
                urgency?.status === 'normal' && 'text-gray-500'
              )} />
              <div className="min-w-0">
                <p className="text-xs text-gray-500">Target Date</p>
                <p className={cn(
                  'text-sm font-semibold truncate',
                  urgency?.status === 'overdue' && 'text-red-600',
                  urgency?.status === 'today' && 'text-orange-600',
                  urgency?.status === 'urgent' && 'text-yellow-600',
                  urgency?.status === 'normal' && 'text-gray-900'
                )}>
                  {new Date(action.target_date).toLocaleDateString()}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Urgency Indicator */}
        {urgency && isGridLayout && (
          <div className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg border',
            urgency.status === 'overdue' && 'bg-red-50 border-red-200',
            urgency.status === 'today' && 'bg-orange-50 border-orange-200',
            urgency.status === 'urgent' && 'bg-yellow-50 border-yellow-200',
            urgency.status === 'normal' && 'bg-gray-50 border-gray-200'
          )}>
            <Clock className={cn(
              'w-4 h-4',
              urgency.status === 'overdue' && 'text-red-600',
              urgency.status === 'today' && 'text-orange-600',
              urgency.status === 'urgent' && 'text-yellow-600',
              urgency.status === 'normal' && 'text-gray-600'
            )} />
            <span className={cn(
              'text-sm font-medium',
              urgency.status === 'overdue' && 'text-red-700',
              urgency.status === 'today' && 'text-orange-700',
              urgency.status === 'urgent' && 'text-yellow-700',
              urgency.status === 'normal' && 'text-gray-700'
            )}>
              {urgency.text}
            </span>
          </div>
        )}

        {/* Footer Metadata */}
        <div className={cn(
          'flex items-center justify-between text-sm pt-3 border-t border-gray-100',
          !isGridLayout && 'flex-wrap gap-2'
        )}>
          <div className="flex items-center gap-4 flex-wrap">
            {/* Dependencies */}
            {action.depends_on && action.depends_on.length > 0 && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`${action.depends_on.length} dependencies`}
              >
                <Link2 className="w-4 h-4 text-gray-400" aria-hidden="true" />
                <span className="text-xs">
                  {action.depends_on.length} dependencies
                </span>
              </span>
            )}

            {/* Blocks */}
            {action.blocks && action.blocks.length > 0 && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`Blocks ${action.blocks.length} actions`}
              >
                <AlertCircle className="w-4 h-4 text-gray-400" aria-hidden="true" />
                <span className="text-xs">
                  Blocks {action.blocks.length}
                </span>
              </span>
            )}

            {/* Start Date */}
            {action.start_date && isGridLayout && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`Started: ${new Date(action.start_date).toLocaleDateString()}`}
              >
                <Calendar className="w-4 h-4 text-gray-400" aria-hidden="true" />
                <span className="text-xs">
                  Started {new Date(action.start_date).toLocaleDateString()}
                </span>
              </span>
            )}
          </div>

          {/* Arrow Icon */}
          {showActions && onClick && (
            <ArrowRight
              className="w-5 h-5 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all flex-shrink-0"
              aria-hidden="true"
            />
          )}
        </div>

        {/* Actions */}
        {showActions && !onClick && isGridLayout && (
          <div className="flex gap-3 pt-4 border-t border-gray-100">
            <Link
              href={`/planning/actions/${action.id}`}
              className="flex-1 text-center px-4 py-2 text-sm text-purple-600 hover:text-purple-700 font-medium bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
            >
              View Action
            </Link>
            <Link
              href={`/planning/actions/${action.id}/edit`}
              className="flex-1 text-center px-4 py-2 text-sm text-gray-600 hover:text-gray-700 font-medium bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Update Progress
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
