/**
 * CriticalityBadge Component
 * Visual indicator for BIA process criticality level
 * Professional, consistent styling across the platform
 */

import { CriticalityLevel } from '@/types/bia';
import { AlertTriangle } from 'lucide-react';

interface CriticalityBadgeProps {
  level: CriticalityLevel;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const CRITICALITY_CONFIG = {
  [CriticalityLevel.CRITICAL]: {
    label: 'Critical',
    bgClass: 'bg-red-100',
    textClass: 'text-red-800',
    borderClass: 'border-red-200',
    iconColor: 'text-red-600',
  },
  [CriticalityLevel.HIGH]: {
    label: 'High',
    bgClass: 'bg-orange-100',
    textClass: 'text-orange-800',
    borderClass: 'border-orange-200',
    iconColor: 'text-orange-600',
  },
  [CriticalityLevel.MODERATE]: {
    label: 'Moderate',
    bgClass: 'bg-yellow-100',
    textClass: 'text-yellow-800',
    borderClass: 'border-yellow-200',
    iconColor: 'text-yellow-600',
  },
  [CriticalityLevel.MINOR]: {
    label: 'Minor',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
    borderClass: 'border-blue-200',
    iconColor: 'text-blue-600',
  },
  [CriticalityLevel.LOW]: {
    label: 'Low',
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-800',
    borderClass: 'border-gray-200',
    iconColor: 'text-gray-600',
  },
};

const SIZE_CONFIG = {
  sm: {
    textClass: 'text-xs',
    paddingClass: 'px-2 py-0.5',
    iconSize: 'w-3 h-3',
  },
  md: {
    textClass: 'text-sm',
    paddingClass: 'px-3 py-1',
    iconSize: 'w-4 h-4',
  },
  lg: {
    textClass: 'text-base',
    paddingClass: 'px-4 py-1.5',
    iconSize: 'w-5 h-5',
  },
};

export function CriticalityBadge({
  level,
  showIcon = false,
  size = 'md',
}: CriticalityBadgeProps) {
  const config = CRITICALITY_CONFIG[level];
  const sizeConfig = SIZE_CONFIG[size];

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium border
        ${config.bgClass} ${config.textClass} ${config.borderClass}
        ${sizeConfig.textClass} ${sizeConfig.paddingClass}
      `}
    >
      {showIcon && (
        <AlertTriangle className={`${sizeConfig.iconSize} ${config.iconColor}`} />
      )}
      {config.label}
    </span>
  );
}

/**
 * Get criticality score (1-5) for sorting/filtering
 */
export function getCriticalityScore(level: CriticalityLevel): number {
  const scores = {
    [CriticalityLevel.CRITICAL]: 5,
    [CriticalityLevel.HIGH]: 4,
    [CriticalityLevel.MODERATE]: 3,
    [CriticalityLevel.MINOR]: 2,
    [CriticalityLevel.LOW]: 1,
  };
  return scores[level];
}
