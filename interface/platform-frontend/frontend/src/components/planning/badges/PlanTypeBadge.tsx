/**
 * PlanTypeBadge Component
 * Visual indicator for plan types (Strategic/Tactical/Operational)
 * Based on ISO 22301:2019 organizational planning levels
 */

'use client';

import React from 'react';
import { PlanType, getPlanTypeLabel, getPlanTypeColor } from '@/types/planning';
import { type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PlanTypeBadgeProps {
  type: PlanType;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface TypeConfig {
  label: string;
  description: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
}

const TYPE_CONFIG: Record<PlanType, TypeConfig> = {
  [PlanType.STRATEGIC]: {
    label: 'Strategic',
    description: 'Strategic-level business continuity plan',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
  },
  [PlanType.TACTICAL]: {
    label: 'Tactical',
    description: 'Tactical-level business continuity plan',
    bgColor: 'bg-indigo-100',
    textColor: 'text-indigo-800',
    borderColor: 'border-indigo-300',
  },
  [PlanType.OPERATIONAL]: {
    label: 'Operational',
    description: 'Operational-level business continuity plan',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    borderColor: 'border-blue-200',
  },
};

const SIZE_CONFIG = {
  sm: {
    textClass: 'text-xs',
    paddingClass: 'px-2 py-0.5',
  },
  md: {
    textClass: 'text-sm',
    paddingClass: 'px-2.5 py-1',
  },
  lg: {
    textClass: 'text-base',
    paddingClass: 'px-3 py-1.5',
  },
};

/**
 * PlanTypeBadge displays a colored badge representing plan type
 *
 * @param type - The PlanType value ('strategic', 'tactical', 'operational')
 * @param showIcon - Whether to display an icon (default: false)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function PlanTypeBadge({
  type,
  showIcon = false,
  size = 'md',
  className,
}: PlanTypeBadgeProps) {
  const config = TYPE_CONFIG[type];
  const sizeConfig = SIZE_CONFIG[size];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium border transition-colors duration-200',
        config.bgColor,
        config.textColor,
        config.borderColor,
        sizeConfig.textClass,
        sizeConfig.paddingClass,
        className
      )}
      title={config.description}
      role="status"
      aria-label={`Plan type: ${config.label}`}
    >
      {config.label}
    </span>
  );
}

/**
 * Get plan type badge configuration (useful for external components)
 */
export function getPlanTypeConfig(type: PlanType): TypeConfig {
  return TYPE_CONFIG[type];
}
