/**
 * RiskCard Component
 * Professional card display for risk assessment in list/grid views
 * Week 5 Round 3 - Risk Assessment Module
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import type { Risk } from '@/types/risk';
import {
  getRiskSeverity,
  getSeverityColor,
  formatCurrency,
  getCategoryLabel,
  getStatusLabel
} from '@/types/risk';
import {
  AlertTriangle,
  Calendar,
  User,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Shield,
  Activity,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RiskCardProps {
  risk: Risk;
  layout?: 'grid' | 'list';
  onClick?: () => void;
  showActions?: boolean;
  className?: string;
}

/**
 * RiskCard displays a risk assessment in card format
 *
 * Features:
 * - Risk title, category, severity
 * - Inherent and residual risk scores
 * - Status and ownership
 * - Last review date
 * - Click to navigate to detail page
 * - Responsive grid/list layouts
 */
export function RiskCard({
  risk,
  layout = 'grid',
  onClick,
  showActions = true,
  className
}: RiskCardProps) {
  const severity = getRiskSeverity(risk.inherent_risk_score);
  const severityColors = getSeverityColor(severity);

  const residualSeverity = risk.residual_risk_score
    ? getRiskSeverity(risk.residual_risk_score)
    : null;

  const riskReduction = risk.residual_risk_score
    ? risk.inherent_risk_score - risk.residual_risk_score
    : null;

  const isGridLayout = layout === 'grid';

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    }
  };

  return (
    <div
      className={cn(
        'bg-white rounded-xl border transition-all duration-200',
        'hover:shadow-xl hover:border-orange-300',
        onClick && 'cursor-pointer',
        isGridLayout
          ? 'p-6 shadow-lg'
          : 'p-4 shadow-md flex items-start gap-4',
        className
      )}
      onClick={handleCardClick}
      role="article"
      aria-label={`Risk: ${risk.risk_title}`}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {/* Severity Badge - Left side for list layout */}
      {!isGridLayout && (
        <div className="flex-shrink-0">
          <div className={cn(
            'w-16 h-16 rounded-lg flex items-center justify-center',
            severityColors.bg
          )}>
            <AlertTriangle className={cn('w-8 h-8', severityColors.text)} />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className={cn('flex-1', isGridLayout ? 'space-y-4' : 'space-y-2')}>
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {isGridLayout && risk.risk_code && (
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {risk.risk_code}
                </span>
              </div>
            )}

            <h3
              className={cn(
                'font-semibold text-gray-900 group-hover:text-orange-600 transition-colors',
                isGridLayout ? 'text-lg mb-1' : 'text-base',
                !isGridLayout && 'line-clamp-1'
              )}
            >
              {risk.risk_title}
            </h3>

            {/* Category Badge */}
            <div className="flex items-center gap-2 mt-1">
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 border border-blue-300">
                {getCategoryLabel(risk.risk_category)}
              </span>
            </div>
          </div>

          {/* Severity Badge - Top right for grid layout */}
          {isGridLayout && (
            <div className={cn(
              'px-3 py-1 rounded-full text-sm font-medium border whitespace-nowrap',
              severityColors.bg,
              severityColors.text,
              severityColors.border
            )}>
              {severity.toUpperCase()}
            </div>
          )}
        </div>

        {/* Description */}
        {isGridLayout && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {risk.description}
          </p>
        )}

        {/* Risk Scores */}
        <div className={cn(
          'grid gap-3',
          risk.residual_risk_score ? 'grid-cols-2' : 'grid-cols-1'
        )}>
          {/* Inherent Risk */}
          <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div className="flex items-center gap-1 mb-1">
              <Activity className="w-3 h-3 text-gray-500" />
              <p className="text-xs text-gray-600 font-medium">Inherent Risk</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {risk.inherent_risk_score}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              L:{risk.likelihood} × I:{risk.impact}
            </p>
          </div>

          {/* Residual Risk */}
          {risk.residual_risk_score && (
            <div className="bg-green-50 rounded-lg p-3 border border-green-200">
              <div className="flex items-center gap-1 mb-1">
                <Shield className="w-3 h-3 text-green-700" />
                <p className="text-xs text-green-700 font-medium">Residual Risk</p>
              </div>
              <p className="text-2xl font-bold text-green-900">
                {risk.residual_risk_score}
              </p>
              {riskReduction && riskReduction > 0 && (
                <div className="flex items-center gap-1 mt-0.5">
                  <TrendingDown className="w-3 h-3 text-green-600" />
                  <p className="text-xs text-green-600">
                    -{riskReduction} reduction
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Metadata */}
        <div className={cn(
          'flex items-center justify-between text-sm pt-3 border-t border-gray-100',
          !isGridLayout && 'flex-wrap gap-2'
        )}>
          <div className="flex items-center gap-4 flex-wrap">
            {/* Status */}
            <span className="inline-flex items-center gap-1 text-gray-600">
              <Shield className="w-4 h-4 text-gray-400" aria-hidden="true" />
              <span className="text-xs">{getStatusLabel(risk.status)}</span>
            </span>

            {/* Last Review */}
            {risk.last_reviewed_at && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`Last reviewed: ${new Date(risk.last_reviewed_at).toLocaleString()}`}
              >
                <Calendar className="w-4 h-4 text-gray-400" aria-hidden="true" />
                <span className="text-xs">
                  {format(new Date(risk.last_reviewed_at), 'MMM d, yyyy')}
                </span>
              </span>
            )}

            {/* Owner */}
            {risk.risk_owner_id && isGridLayout && (
              <span
                className="inline-flex items-center gap-1 text-gray-600"
                title={`Owner: ${risk.risk_owner_id}`}
              >
                <User className="w-4 h-4 text-gray-400" aria-hidden="true" />
                <span className="text-xs truncate max-w-[120px]">
                  {risk.risk_owner_id}
                </span>
              </span>
            )}
          </div>

          {/* Arrow Icon */}
          {showActions && onClick && (
            <ArrowRight
              className="w-5 h-5 text-gray-400 group-hover:text-orange-600 group-hover:translate-x-1 transition-all flex-shrink-0"
              aria-hidden="true"
            />
          )}
        </div>

        {/* Treatment Indicator */}
        {risk.treatment_strategy && isGridLayout && (
          <div className="flex items-center gap-1.5 text-xs text-purple-700 bg-purple-50 px-3 py-1.5 rounded-lg border border-purple-200">
            <TrendingUp className="w-3 h-3" aria-hidden="true" />
            <span>Treatment: {risk.treatment_strategy}</span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Inline Severity Badge Component
 * Can be used standalone for displaying risk severity
 */
export function SeverityBadge({
  severity,
  size = 'sm',
}: {
  severity: 'low' | 'medium' | 'high' | 'critical';
  size?: 'sm' | 'md';
}) {
  const colors = getSeverityColor(severity);

  const sizeClasses =
    size === 'sm'
      ? 'text-xs px-2 py-0.5'
      : 'text-sm px-3 py-1';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium border',
        colors.bg,
        colors.text,
        colors.border,
        sizeClasses
      )}
      title={`Severity: ${severity}`}
    >
      <AlertTriangle className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} aria-hidden="true" />
      {severity.toUpperCase()}
    </span>
  );
}
