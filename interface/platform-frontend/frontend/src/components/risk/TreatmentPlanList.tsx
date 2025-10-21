'use client';

import React from 'react';
import { useTreatmentPlans } from '@/hooks/risk';
import type { RiskTreatmentPlan } from '@/types/risk';
import { format } from 'date-fns';
import {
  Shield,
  DollarSign,
  Calendar,
  CheckCircle,
  Clock,
  AlertCircle,
  ArrowRightLeft,
  XCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TreatmentPlanListProps {
  riskId: string;
  onPlanClick?: (plan: RiskTreatmentPlan) => void;
  className?: string;
}

export function TreatmentPlanList({ riskId, onPlanClick, className }: TreatmentPlanListProps) {
  const { data: plans, isLoading, error } = useTreatmentPlans({ riskId });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-6 h-6 bg-gray-200 rounded" />
                <div className="flex-1">
                  <div className="h-5 bg-gray-200 rounded w-32 mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-full" />
                </div>
              </div>
              <div className="w-20 h-6 bg-gray-200 rounded-full" />
            </div>
            <div className="mb-4">
              <div className="h-2 bg-gray-200 rounded w-full" />
            </div>
            <div className="flex gap-4">
              <div className="h-4 bg-gray-200 rounded w-24" />
              <div className="h-4 bg-gray-200 rounded w-32" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-lg border border-red-200 p-8 text-center">
        <XCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
        <p className="text-red-800 font-medium mb-2">Error loading treatment plans</p>
        <p className="text-red-600 text-sm">{error.message}</p>
      </div>
    );
  }

  if (!plans || plans.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <Shield className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-900 font-medium mb-1">No treatment plans yet</p>
        <p className="text-gray-600 text-sm">
          Create a treatment plan to manage this risk
        </p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'planned':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStrategyIcon = (strategy: string) => {
    switch (strategy) {
      case 'avoid':
        return AlertCircle;
      case 'mitigate':
        return Shield;
      case 'transfer':
        return ArrowRightLeft;
      case 'accept':
        return CheckCircle;
      default:
        return Shield;
    }
  };

  const getStrategyColor = (strategy: string) => {
    switch (strategy) {
      case 'avoid':
        return 'text-red-600';
      case 'mitigate':
        return 'text-orange-600';
      case 'transfer':
        return 'text-blue-600';
      case 'accept':
        return 'text-green-600';
      default:
        return 'text-orange-600';
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {plans.map((plan) => {
        const Icon = getStrategyIcon(plan.strategy);
        const completedActions = plan.actions.filter(a => a.status === 'completed').length;
        const totalActions = plan.actions.length;
        const progress = totalActions > 0 ? (completedActions / totalActions) * 100 : 0;

        return (
          <div
            key={plan.id}
            onClick={() => onPlanClick?.(plan)}
            className={cn(
              'bg-white rounded-lg border border-gray-200 p-6 transition-all',
              onPlanClick && 'cursor-pointer hover:shadow-lg hover:border-orange-300'
            )}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3 flex-1">
                <Icon className={cn('w-6 h-6', getStrategyColor(plan.strategy))} />
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 capitalize mb-1">
                    {plan.strategy}
                  </h4>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {plan.description}
                  </p>
                </div>
              </div>

              <span className={cn(
                'px-3 py-1 rounded-full border text-xs font-medium whitespace-nowrap',
                getStatusColor(plan.status)
              )}>
                {plan.status.replace('_', ' ')}
              </span>
            </div>

            {/* Progress Bar */}
            {totalActions > 0 && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span className="inline-flex items-center gap-1.5">
                    <Clock className="w-4 h-4" />
                    Action Items
                  </span>
                  <span className="font-medium">
                    {completedActions}/{totalActions} completed
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={cn(
                      'h-2 rounded-full transition-all',
                      progress === 100 ? 'bg-green-600' : 'bg-orange-600'
                    )}
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center gap-4 text-sm text-gray-500">
              {plan.estimated_cost !== undefined && plan.estimated_cost !== null && (
                <span className="inline-flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  ${plan.estimated_cost.toLocaleString()}
                </span>
              )}
              {plan.target_date && (
                <span className="inline-flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {format(new Date(plan.target_date), 'MMM d, yyyy')}
                </span>
              )}
              {plan.responsible_party && (
                <span className="text-gray-600">
                  {plan.responsible_party}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
