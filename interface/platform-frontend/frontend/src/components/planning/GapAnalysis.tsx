'use client';

import { usePlanningGaps } from '@/hooks/planning';
import type { PlanningGap } from '@/lib/api/planning-client';
import { AlertTriangle, AlertCircle, Info, XCircle } from 'lucide-react';

interface GapAnalysisProps {
  organizationId: string;
}

type GapSeverity = 'critical' | 'high' | 'medium' | 'low';
type GapType = 'missing_plan' | 'outdated_plan' | 'incomplete_strategy' | 'missing_resources';

export function GapAnalysis({ organizationId }: GapAnalysisProps) {
  const { data: gaps, isLoading, error } = usePlanningGaps({ organizationId });

  // Gap severity icons
  const severityIcons: Record<GapSeverity, typeof AlertTriangle> = {
    critical: AlertTriangle,
    high: AlertCircle,
    medium: Info,
    low: Info,
  };

  // Gap severity colors
  const severityColors: Record<GapSeverity, string> = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'blue',
  };

  // Gap type labels
  const gapTypeLabels: Record<GapType, string> = {
    missing_plan: 'Missing Plan',
    outdated_plan: 'Outdated Plan',
    incomplete_strategy: 'Incomplete Strategy',
    missing_resources: 'Missing Resources',
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-lg h-32 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-600">Failed to load gap analysis</p>
      </div>
    );
  }

  if (!gaps || gaps.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-green-900">No Gaps Found</h3>
            <p className="text-sm text-green-700">All processes are adequately covered by plans</p>
          </div>
        </div>
      </div>
    );
  }

  // Group gaps by severity
  const gapsBySeverity: Record<GapSeverity, PlanningGap[]> = {
    critical: gaps.filter((g: PlanningGap) => g.severity === 'critical'),
    high: gaps.filter((g: PlanningGap) => g.severity === 'high'),
    medium: gaps.filter((g: PlanningGap) => g.severity === 'medium'),
    low: gaps.filter((g: PlanningGap) => g.severity === 'low'),
  };

  return (
    <div className="space-y-6">
      {/* Gap Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border-l-4 border-red-500 p-4">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <p className="text-sm font-medium text-gray-600">Critical</p>
          </div>
          <p className="text-2xl font-bold text-red-600">{gapsBySeverity.critical.length}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border-l-4 border-orange-500 p-4">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle className="w-4 h-4 text-orange-600" />
            <p className="text-sm font-medium text-gray-600">High</p>
          </div>
          <p className="text-2xl font-bold text-orange-600">{gapsBySeverity.high.length}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border-l-4 border-yellow-500 p-4">
          <div className="flex items-center gap-2 mb-1">
            <Info className="w-4 h-4 text-yellow-600" />
            <p className="text-sm font-medium text-gray-600">Medium</p>
          </div>
          <p className="text-2xl font-bold text-yellow-600">{gapsBySeverity.medium.length}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border-l-4 border-blue-500 p-4">
          <div className="flex items-center gap-2 mb-1">
            <Info className="w-4 h-4 text-blue-600" />
            <p className="text-sm font-medium text-gray-600">Low</p>
          </div>
          <p className="text-2xl font-bold text-blue-600">{gapsBySeverity.low.length}</p>
        </div>
      </div>

      {/* Gap List */}
      <div className="space-y-4">
        {gaps.map((gap: PlanningGap, index: number) => {
          const Icon = severityIcons[gap.severity];
          const color = severityColors[gap.severity];

          return (
            <div
              key={index}
              className={`bg-white rounded-lg shadow-sm border-l-4 border-${color}-500 p-4`}
            >
              <div className="flex items-start gap-4">
                {/* Severity indicator */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-full bg-${color}-100 flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 text-${color}-600`} />
                </div>

                {/* Gap content */}
                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900">
                        {gapTypeLabels[gap.gap_type]}
                      </h4>
                      {gap.affected_process && (
                        <p className="text-xs text-gray-500">
                          Process: {gap.affected_process}
                        </p>
                      )}
                      {gap.affected_risk && (
                        <p className="text-xs text-gray-500">
                          Risk: {gap.affected_risk}
                        </p>
                      )}
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800 uppercase`}>
                      {gap.severity}
                    </span>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-gray-700 mb-3">
                    {gap.description}
                  </p>

                  {/* Recommendation */}
                  <div className="bg-gray-50 rounded-md p-3">
                    <p className="text-xs font-medium text-gray-600 mb-1">
                      Recommended Action:
                    </p>
                    <p className="text-sm text-gray-700">
                      {gap.recommendation}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action prompt */}
      {gaps.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-blue-900 mb-1">
                Action Required
              </h4>
              <p className="text-sm text-blue-700">
                {gapsBySeverity.critical.length > 0 && (
                  <>
                    <strong>{gapsBySeverity.critical.length} critical gap{gapsBySeverity.critical.length > 1 ? 's' : ''}</strong> require immediate attention.
                  </>
                )}
                {' '}Review the recommendations above and create appropriate plans to close these gaps.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
