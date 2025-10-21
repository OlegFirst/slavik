/**
 * RiskMatrix Component
 * 5×5 Likelihood × Impact Heat Map Visualization
 * Week 5 - Risk Assessment Module - Round 3 UI Components
 *
 * Features:
 * - Interactive 5×5 grid layout with color-coded severity zones
 * - Risk positioning with counts per cell
 * - Hover effects with detailed information
 * - Click handlers for drill-down interaction
 * - Highlighted risk tracking
 * - Summary statistics dashboard
 * - Responsive design with accessibility support
 *
 * Severity Calculation:
 * - Score = Likelihood × Impact (1-25)
 * - Critical: 20-25 (red)
 * - High: 15-19 (orange)
 * - Medium: 8-14 (yellow)
 * - Low: 1-7 (green)
 *
 * ISO 31000 Compliance: Risk Matrix Methodology
 */

'use client';

import React, { useState } from 'react';
import { useRiskHeatMap } from '@/hooks/risk';
import type { RiskMatrixPosition } from '@/types/risk';
import { getRiskSeverity, getSeverityColor } from '@/types/risk';
import { AlertTriangle, Info, TrendingUp, Target } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// TYPES
// ============================================================================

interface RiskMatrixProps {
  organizationId?: string;
  onCellClick?: (likelihood: number, impact: number, risks: RiskMatrixPosition[]) => void;
  highlightedRisk?: string; // Risk ID to highlight
  className?: string;
}

interface HoveredCell {
  likelihood: number;
  impact: number;
}

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Likelihood axis labels with descriptions
 * Y-axis (vertical): Bottom to top (1-5)
 */
const LIKELIHOOD_LABELS = [
  { value: 5, label: 'Almost Certain', desc: '> 80%' },
  { value: 4, label: 'Likely', desc: '50-80%' },
  { value: 3, label: 'Possible', desc: '20-50%' },
  { value: 2, label: 'Unlikely', desc: '5-20%' },
  { value: 1, label: 'Rare', desc: '< 5%' },
] as const;

/**
 * Impact axis labels
 * X-axis (horizontal): Left to right (1-5)
 */
const IMPACT_LABELS = [
  { value: 1, label: 'Insignificant' },
  { value: 2, label: 'Minor' },
  { value: 3, label: 'Moderate' },
  { value: 4, label: 'Major' },
  { value: 5, label: 'Catastrophic' },
] as const;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Calculate cell severity based on likelihood and impact
 */
function getCellSeverity(likelihood: number, impact: number): string {
  const score = likelihood * impact;
  if (score >= 20) return 'critical';
  if (score >= 15) return 'high';
  if (score >= 8) return 'medium';
  return 'low';
}

/**
 * Get Tailwind CSS classes for cell background based on severity
 */
function getCellColorClasses(severity: string): string {
  switch (severity) {
    case 'critical':
      return 'bg-red-100 hover:bg-red-200 border-red-300';
    case 'high':
      return 'bg-orange-100 hover:bg-orange-200 border-orange-300';
    case 'medium':
      return 'bg-yellow-100 hover:bg-yellow-200 border-yellow-300';
    case 'low':
      return 'bg-green-100 hover:bg-green-200 border-green-300';
    default:
      return 'bg-gray-50 hover:bg-gray-100 border-gray-300';
  }
}

/**
 * Format cell key for risks_by_cell lookup
 * API uses "likelihood_impact" format
 */
function formatCellKey(likelihood: number, impact: number): string {
  return `${likelihood}_${impact}`;
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

/**
 * Loading skeleton for matrix
 */
function MatrixSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-48" />
        <div className="aspect-square bg-gray-200 rounded" />
        <div className="grid grid-cols-4 gap-4 mt-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-20 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Legend showing severity color coding
 */
function SeverityLegend() {
  return (
    <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
      <span className="text-sm font-medium text-gray-700">Severity Zones:</span>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-green-500 rounded" />
        <span className="text-sm text-gray-600">Low (1-7)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-yellow-500 rounded" />
        <span className="text-sm text-gray-600">Medium (8-14)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-orange-500 rounded" />
        <span className="text-sm text-gray-600">High (15-19)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-red-500 rounded" />
        <span className="text-sm text-gray-600">Critical (20-25)</span>
      </div>
    </div>
  );
}

/**
 * Hovered cell information panel
 */
interface HoveredCellInfoProps {
  cell: HoveredCell;
  riskCount: number;
}

function HoveredCellInfo({ cell, riskCount }: HoveredCellInfoProps) {
  const score = cell.likelihood * cell.impact;
  const severity = getCellSeverity(cell.likelihood, cell.impact);
  const likelihoodLabel = LIKELIHOOD_LABELS.find(l => l.value === cell.likelihood)?.label;
  const impactLabel = IMPACT_LABELS.find(i => i.value === cell.impact)?.label;

  return (
    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-start gap-3">
        <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="space-y-1">
          <p className="text-sm font-medium text-blue-900">
            {likelihoodLabel} × {impactLabel} = Score {score} ({severity})
          </p>
          <p className="text-sm text-blue-700">
            {riskCount} {riskCount === 1 ? 'risk' : 'risks'} in this cell
          </p>
          <p className="text-xs text-blue-600">
            Likelihood: {cell.likelihood} | Impact: {cell.impact}
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Summary statistics cards
 */
interface SummaryStatsProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

function SummaryStats({ critical, high, medium, low, total }: SummaryStatsProps) {
  return (
    <div className="mt-6 space-y-3">
      {/* Total Risks Header */}
      <div className="flex items-center justify-between p-3 bg-gray-100 border border-gray-300 rounded-lg">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Total Risks</span>
        </div>
        <span className="text-2xl font-bold text-gray-900">{total}</span>
      </div>

      {/* Severity Breakdown */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs font-medium text-red-700">Critical</p>
          <p className="text-2xl font-bold text-red-900">{critical}</p>
          <p className="text-xs text-red-600 mt-1">
            {total > 0 ? Math.round((critical / total) * 100) : 0}%
          </p>
        </div>
        <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <p className="text-xs font-medium text-orange-700">High</p>
          <p className="text-2xl font-bold text-orange-900">{high}</p>
          <p className="text-xs text-orange-600 mt-1">
            {total > 0 ? Math.round((high / total) * 100) : 0}%
          </p>
        </div>
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs font-medium text-yellow-700">Medium</p>
          <p className="text-2xl font-bold text-yellow-900">{medium}</p>
          <p className="text-xs text-yellow-600 mt-1">
            {total > 0 ? Math.round((medium / total) * 100) : 0}%
          </p>
        </div>
        <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-xs font-medium text-green-700">Low</p>
          <p className="text-2xl font-bold text-green-900">{low}</p>
          <p className="text-xs text-green-600 mt-1">
            {total > 0 ? Math.round((low / total) * 100) : 0}%
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Matrix cell component
 */
interface MatrixCellProps {
  likelihood: number;
  impact: number;
  risks: RiskMatrixPosition[];
  highlightedRisk?: string;
  isHovered: boolean;
  onHover: (hovered: boolean) => void;
  onClick: () => void;
}

function MatrixCell({
  likelihood,
  impact,
  risks,
  highlightedRisk,
  isHovered,
  onHover,
  onClick,
}: MatrixCellProps) {
  const score = likelihood * impact;
  const severity = getCellSeverity(likelihood, impact);
  const hasHighlighted = highlightedRisk && risks.some(r => r.risk_id === highlightedRisk);
  const riskCount = risks.length;

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
      className={cn(
        'relative aspect-square border-2 rounded-lg transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-1',
        getCellColorClasses(severity),
        hasHighlighted && 'ring-4 ring-blue-500 ring-offset-2',
        isHovered && 'scale-105 shadow-lg z-10'
      )}
      aria-label={`Cell: Likelihood ${likelihood}, Impact ${impact}, ${riskCount} risks, Score ${score}`}
    >
      {/* Risk Count */}
      {riskCount > 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-gray-900">{riskCount}</span>
        </div>
      )}

      {/* Score Badge */}
      <div className="absolute top-1 right-1 bg-white/80 rounded px-1.5 py-0.5 shadow-sm">
        <span className="text-xs font-medium text-gray-600">{score}</span>
      </div>

      {/* Highlighted Risk Indicator */}
      {hasHighlighted && (
        <div className="absolute top-1 left-1 bg-blue-600 rounded-full p-1">
          <AlertTriangle className="w-3 h-3 text-white" />
        </div>
      )}

      {/* Empty Cell Indicator */}
      {riskCount === 0 && (
        <div className="absolute inset-0 flex items-center justify-center opacity-40">
          <span className="text-sm text-gray-500">—</span>
        </div>
      )}
    </button>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * RiskMatrix Component
 *
 * Interactive 5×5 heat map showing risk distribution across
 * likelihood and impact dimensions with color-coded severity zones.
 *
 * @example
 * ```tsx
 * <RiskMatrix
 *   organizationId="org-123"
 *   onCellClick={(likelihood, impact, risks) => {
 *     console.log(`Cell clicked: L=${likelihood}, I=${impact}`, risks);
 *   }}
 *   highlightedRisk="risk-456"
 * />
 * ```
 */
export function RiskMatrix({
  organizationId,
  onCellClick,
  highlightedRisk,
  className,
}: RiskMatrixProps) {
  const { data: heatMapData, isLoading, error } = useRiskHeatMap({ organizationId });
  const [hoveredCell, setHoveredCell] = useState<HoveredCell | null>(null);

  // Handle loading state
  if (isLoading) {
    return <MatrixSkeleton />;
  }

  // Handle error state
  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex items-center gap-3 text-red-600">
          <AlertTriangle className="w-6 h-6" />
          <div>
            <p className="font-medium">Failed to load risk matrix</p>
            <p className="text-sm text-gray-600 mt-1">
              {error instanceof Error ? error.message : 'Unknown error occurred'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Handle no data state
  if (!heatMapData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center text-gray-500">
          <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No heat map data available</p>
        </div>
      </div>
    );
  }

  // Get risks for hovered cell
  const hoveredCellRisks = hoveredCell
    ? heatMapData.risks_by_cell[formatCellKey(hoveredCell.likelihood, hoveredCell.impact)] || []
    : [];

  return (
    <div className={cn('bg-white rounded-xl shadow-lg p-6', className)}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-orange-600" />
          Risk Heat Map
        </h2>
        <p className="text-gray-600">5×5 Likelihood × Impact Matrix</p>
      </div>

      {/* Legend */}
      <SeverityLegend />

      {/* Matrix Container */}
      <div className="relative overflow-visible">
        {/* Y-axis Label (Likelihood) - Vertical on left */}
        <div className="absolute -left-20 top-1/2 -translate-y-1/2 -rotate-90 origin-center">
          <p className="text-sm font-semibold text-gray-700 whitespace-nowrap">
            Likelihood →
          </p>
        </div>

        {/* Matrix Grid */}
        <div className="grid grid-cols-[auto_repeat(5,1fr)] gap-2">
          {/* Top-left corner (empty) */}
          <div />

          {/* Impact Labels (X-axis - horizontal top) */}
          {IMPACT_LABELS.map(({ value, label }) => (
            <div key={`impact-${value}`} className="text-center pb-2">
              <p className="text-xs font-semibold text-gray-700">{label}</p>
              <p className="text-xs text-gray-500">{value}</p>
            </div>
          ))}

          {/* Matrix Rows (likelihood from 5 to 1, top to bottom) */}
          {LIKELIHOOD_LABELS.map(({ value: likelihood, label, desc }) => (
            <React.Fragment key={`row-${likelihood}`}>
              {/* Likelihood Label (Y-axis - vertical left) */}
              <div className="flex items-center justify-end pr-3">
                <div className="text-right">
                  <p className="text-xs font-semibold text-gray-700">{label}</p>
                  <p className="text-xs text-gray-500">{desc}</p>
                </div>
              </div>

              {/* Cells for this likelihood row */}
              {IMPACT_LABELS.map(({ value: impact }) => {
                const cellKey = formatCellKey(likelihood, impact);
                const cellRisks = heatMapData.risks_by_cell[cellKey] || [];
                const isCellHovered = hoveredCell?.likelihood === likelihood && hoveredCell?.impact === impact;

                return (
                  <MatrixCell
                    key={cellKey}
                    likelihood={likelihood}
                    impact={impact}
                    risks={cellRisks}
                    highlightedRisk={highlightedRisk}
                    isHovered={isCellHovered}
                    onHover={(hovered) => {
                      if (hovered) {
                        setHoveredCell({ likelihood, impact });
                      } else if (isCellHovered) {
                        setHoveredCell(null);
                      }
                    }}
                    onClick={() => onCellClick?.(likelihood, impact, cellRisks)}
                  />
                );
              })}
            </React.Fragment>
          ))}
        </div>

        {/* X-axis Label (Impact) - Horizontal below */}
        <div className="text-center mt-3">
          <p className="text-sm font-semibold text-gray-700">Impact →</p>
        </div>
      </div>

      {/* Hovered Cell Info */}
      {hoveredCell && (
        <HoveredCellInfo
          cell={hoveredCell}
          riskCount={hoveredCellRisks.length}
        />
      )}

      {/* Summary Stats */}
      <SummaryStats
        critical={heatMapData.critical_count || 0}
        high={heatMapData.high_count || 0}
        medium={heatMapData.medium_count || 0}
        low={heatMapData.low_count || 0}
        total={heatMapData.total_risks || 0}
      />
    </div>
  );
}
