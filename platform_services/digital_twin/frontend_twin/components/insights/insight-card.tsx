'use client';

import { TwinInsight } from '@/lib/api/types';
import {
  AlertTriangle,
  Lightbulb,
  AlertCircle,
  CheckCircle,
  FileText,
  TrendingUp,
  Search,
} from 'lucide-react';

const impactColors = {
  low: 'bg-green-50 border-l-green-500 text-green-900',
  medium: 'bg-yellow-50 border-l-yellow-500 text-yellow-900',
  high: 'bg-orange-50 border-l-orange-500 text-orange-900',
  critical: 'bg-red-50 border-l-red-500 text-red-900',
};

const impactBadges = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

const icons = {
  risk: AlertTriangle,
  opportunity: Lightbulb,
  warning: AlertCircle,
  recommendation: CheckCircle,
  compliance: FileText,
  trend: TrendingUp,
  anomaly: Search,
};

interface Props {
  insight: TwinInsight;
}

export function InsightCard({ insight }: Props) {
  const Icon = icons[insight.type];
  const colorClass = impactColors[insight.impact];
  const badgeClass = impactBadges[insight.impact];

  return (
    <div className={`p-6 rounded-lg border-l-4 ${colorClass}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <Icon size={24} className="flex-shrink-0" />
            <h3 className="font-semibold text-lg">{insight.title}</h3>
            <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${badgeClass}`}>
              {insight.impact}
            </span>
          </div>

          <p className="text-sm leading-relaxed mb-4">{insight.description}</p>

          <div className="flex items-center gap-6 text-xs mb-4">
            <div className="flex items-center gap-2">
              <span className="font-medium">Confidence:</span>
              <div className="flex-1 min-w-[100px]">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 rounded-full"
                    style={{ width: `${insight.confidence}%` }}
                  />
                </div>
              </div>
              <span className="font-medium">{insight.confidence}%</span>
            </div>
            <div>
              <span className="font-medium">Source:</span> {insight.source}
            </div>
          </div>

          {insight.actionable && insight.suggested_actions.length > 0 && (
            <div className="mt-4 p-4 bg-white rounded-lg border">
              <p className="text-xs font-semibold uppercase tracking-wide mb-2">
                Suggested Actions:
              </p>
              <ul className="space-y-2">
                {insight.suggested_actions.map((action, i) => (
                  <li key={i} className="text-sm flex items-start gap-2">
                    <span className="text-blue-600 font-bold">→</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
