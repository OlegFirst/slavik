/**
 * StrategyCard Component
 * Professional card display for recovery strategies
 * Planning Module Round 3 - Agent 8
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { RecoveryStrategy } from '@/types/planning';
import { StrategyTypeBadge } from './badges/StrategyTypeBadge';
import {
  Zap,
  Clock,
  Users,
  Calendar,
  Star,
  CheckCircle,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StrategyCardProps {
  strategy: RecoveryStrategy;
  layout?: 'grid' | 'list';
  onClick?: () => void;
  showActions?: boolean;
  className?: string;
}

/**
 * StrategyCard displays a recovery strategy in card format
 *
 * Features:
 * - Strategy name, type badge
 * - Activation trigger and timing
 * - Required personnel count
 * - Last tested date
 * - Effectiveness rating (stars)
 * - Recovery steps count
 */
export function StrategyCard({
  strategy,
  layout = 'grid',
  onClick,
  showActions = true,
  className
}: StrategyCardProps) {
  const isGridLayout = layout === 'grid';

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    }
  };

  // Calculate days since last test
  const daysSinceTest = strategy.last_tested_at
    ? Math.floor(
        (Date.now() - new Date(strategy.last_tested_at).getTime()) / (1000 * 60 * 60 * 24)
      )
    : null;

  // Render effectiveness stars
  const renderEffectivenessStars = () => {
    if (!strategy.effectiveness_rating) return null;

    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={cn(
              'w-3 h-3',
              star <= strategy.effectiveness_rating!
                ? 'text-yellow-500 fill-yellow-500'
                : 'text-gray-300'
            )}
          />
        ))}
      </div>
    );
  };

  return (
    <div
      className={cn(
        'bg-white rounded-xl border transition-all duration-200',
        'hover:shadow-xl hover:border-green-300',
        onClick && 'cursor-pointer',
        isGridLayout
          ? 'p-6 shadow-lg'
          : 'p-4 shadow-md flex items-start gap-4',
        className
      )}
      onClick={handleCardClick}
      role="article"
      aria-label={`Recovery Strategy: ${strategy.strategy_name}`}
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
                'font-semibold text-gray-900 group-hover:text-green-600 transition-colors',
                isGridLayout ? 'text-lg mb-2' : 'text-base mb-1',
                !isGridLayout && 'line-clamp-1'
              )}
            >
              {strategy.strategy_name}
            </h3>

            {/* Type Badge */}
            <div className="flex items-center gap-2">
              <StrategyTypeBadge type={strategy.strategy_type} />
            </div>
          </div>

          {/* Effectiveness Rating */}
          {isGridLayout && strategy.effectiveness_rating && (
            <div className="flex flex-col items-end">
              {renderEffectivenessStars()}
              <span className="text-xs text-gray-500 mt-1">
                {strategy.effectiveness_rating}/5
              </span>
            </div>
          )}
        </div>

        {/* Description */}
        {isGridLayout && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {strategy.description}
          </p>
        )}

        {/* Activation Trigger */}
        <div className="bg-orange-50 rounded-lg p-3 border border-orange-200">
          <div className="flex items-center gap-1 mb-1">
            <Zap className="w-3 h-3 text-orange-700" />
            <p className="text-xs text-orange-700 font-medium">Activation Trigger</p>
          </div>
          <p className="text-sm text-orange-900 font-semibold">
            {strategy.activation_trigger}
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-3">
          {/* Activation Time */}
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-500" />
            <div>
              <p className="text-xs text-gray-500">Activation Time</p>
              <p className="text-sm font-semibold text-gray-900">
                {strategy.activation_time} min
              </p>
            </div>
          </div>

          {/* Recovery Steps */}
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <div>
              <p className="text-xs text-gray-500">Recovery Steps</p>
              <p className="text-sm font-semibold text-gray-900">
                {strategy.recovery_steps.length} steps
              </p>
            </div>
          </div>
        </div>

        {/* Personnel & Testing */}
        {isGridLayout && (
          <div className="grid grid-cols-2 gap-3">
            {/* Required Personnel */}
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-purple-500" />
              <div>
                <p className="text-xs text-gray-500">Personnel</p>
                <p className="text-sm font-semibold text-gray-900">
                  {strategy.required_personnel.length} roles
                </p>
              </div>
            </div>

            {/* Last Tested */}
            {strategy.last_tested_at ? (
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-teal-500" />
                <div>
                  <p className="text-xs text-gray-500">Last Tested</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {daysSinceTest === 0 ? 'Today' : `${daysSinceTest}d ago`}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <div>
                  <p className="text-xs text-red-500">Not Tested</p>
                  <p className="text-sm font-semibold text-red-600">
                    Requires Testing
                  </p>
                </div>
              </div>
            )}
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
              title={`Last updated: ${new Date(strategy.updated_at).toLocaleString()}`}
            >
              <Calendar className="w-4 h-4 text-gray-400" aria-hidden="true" />
              <span className="text-xs">
                Updated {new Date(strategy.updated_at).toLocaleDateString()}
              </span>
            </span>

            {/* Test Status */}
            {!isGridLayout && strategy.last_tested_at && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`Tested ${daysSinceTest} days ago`}
              >
                <CheckCircle className="w-4 h-4 text-teal-400" aria-hidden="true" />
                <span className="text-xs">
                  Tested {daysSinceTest}d ago
                </span>
              </span>
            )}
          </div>

          {/* Arrow Icon */}
          {showActions && onClick && (
            <ArrowRight
              className="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all flex-shrink-0"
              aria-hidden="true"
            />
          )}
        </div>

        {/* Actions */}
        {showActions && !onClick && isGridLayout && (
          <div className="flex gap-3 pt-4 border-t border-gray-100">
            <Link
              href={`/planning/strategies/${strategy.id}`}
              className="flex-1 text-center px-4 py-2 text-sm text-green-600 hover:text-green-700 font-medium bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
            >
              View Strategy
            </Link>
            <Link
              href={`/planning/strategies/${strategy.id}/test`}
              className="flex-1 text-center px-4 py-2 text-sm text-teal-600 hover:text-teal-700 font-medium bg-teal-50 hover:bg-teal-100 rounded-lg transition-colors"
            >
              Run Test
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
