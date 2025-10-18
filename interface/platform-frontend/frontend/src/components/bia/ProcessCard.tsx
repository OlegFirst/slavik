/**
 * ProcessCard Component
 * Professional card display for BIA process
 * Real data, no mocks - production ready
 */

import { Clock, Users, Building2, TrendingUp, Edit, Trash2, Eye } from 'lucide-react';
import { BIAProcess } from '@/types/bia';
import { CriticalityBadge } from './CriticalityBadge';
import { StatusBadge } from './StatusBadge';
import { WHOTierBadge } from './WHOTierBadge';
import { formatPotentialLoss } from '@/hooks/bia';

interface ProcessCardProps {
  process: BIAProcess;
  onView?: (process: BIAProcess) => void;
  onEdit?: (process: BIAProcess) => void;
  onDelete?: (process: BIAProcess) => void;
  showActions?: boolean;
  compact?: boolean;
}

export function ProcessCard({
  process,
  onView,
  onEdit,
  onDelete,
  showActions = true,
  compact = false,
}: ProcessCardProps) {
  // Calculate 24h financial impact if available
  const financialImpact24h = process.financial_impact?.['24_hours'];

  return (
    <div
      className={`
        bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-200
        border border-gray-200 hover:border-orange-300
        ${compact ? 'p-4' : 'p-6'}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3
            className={`font-semibold text-gray-900 ${compact ? 'text-base' : 'text-lg'}`}
          >
            {process.name}
          </h3>
          {process.description && !compact && (
            <p className="text-gray-600 text-sm mt-1 line-clamp-2">
              {process.description}
            </p>
          )}
        </div>

        {showActions && (
          <div className="flex items-center gap-1 ml-4">
            {onView && (
              <button
                onClick={() => onView(process)}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="View details"
              >
                <Eye className="w-4 h-4" />
              </button>
            )}
            {onEdit && (
              <button
                onClick={() => onEdit(process)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit process"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(process)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete process"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Badges */}
      <div className="flex items-center gap-2 flex-wrap mb-4">
        <CriticalityBadge level={process.criticality} size={compact ? 'sm' : 'md'} />
        <StatusBadge status={process.status} size={compact ? 'sm' : 'md'} />
        {process.who_tier && (
          <WHOTierBadge tier={process.who_tier} size={compact ? 'sm' : 'md'} />
        )}
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {process.department && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Building2 className="w-4 h-4 text-gray-400" />
            <span className="truncate">{process.department}</span>
          </div>
        )}
        {process.process_owner && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Users className="w-4 h-4 text-gray-400" />
            <span className="truncate">{process.process_owner}</span>
          </div>
        )}
      </div>

      {/* RTO/RPO/MTPD */}
      <div className="bg-gray-50 rounded-lg p-3 mb-4">
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <div className="flex items-center justify-center gap-1 text-gray-600 text-xs mb-1">
              <Clock className="w-3 h-3" />
              <span>RTO</span>
            </div>
            <div className="font-semibold text-orange-600">
              {process.rto_hours}h
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-xs mb-1">RPO</div>
            <div className="font-semibold text-blue-600">
              {process.rpo_hours}h
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-xs mb-1">MTPD</div>
            <div className="font-semibold text-purple-600">
              {process.mtpd_hours}h
            </div>
          </div>
        </div>
      </div>

      {/* Financial Impact */}
      {financialImpact24h && !compact && (
        <div className="flex items-center gap-2 text-sm bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <TrendingUp className="w-4 h-4 text-red-600" />
          <span className="text-gray-700">24h Loss Potential:</span>
          <span className="font-semibold text-red-700">
            {formatPotentialLoss(financialImpact24h)}
          </span>
        </div>
      )}

      {/* AI Suggestions */}
      {process.ai_suggested_rto && !compact && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">AI Suggested RTO:</span>
            <span className="font-semibold text-blue-700">
              {process.ai_suggested_rto}h
            </span>
          </div>
          {process.ai_confidence && (
            <div className="mt-1">
              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>Confidence</span>
                <span>{Math.round(process.ai_confidence * 100)}%</span>
              </div>
              <div className="bg-white rounded-full h-1.5">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all"
                  style={{ width: `${process.ai_confidence * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Dependencies Count */}
      {process.dependencies && process.dependencies.length > 0 && !compact && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <span className="font-medium">{process.dependencies.length}</span> dependencies
            {process.dependencies.some((d) => d.required) && (
              <span className="text-red-600 ml-2">
                ({process.dependencies.filter((d) => d.required).length} critical)
              </span>
            )}
          </div>
        </div>
      )}

      {/* Timestamps */}
      {!compact && (
        <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
          <div className="flex items-center justify-between">
            <span>
              Created: {new Date(process.created_at).toLocaleDateString()}
            </span>
            {process.completed_at && (
              <span>
                Completed: {new Date(process.completed_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact variant for lists
 */
export function ProcessCardCompact(props: Omit<ProcessCardProps, 'compact'>) {
  return <ProcessCard {...props} compact={true} />;
}
