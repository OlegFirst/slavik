/**
 * StrategyTypeBadge Component
 * Visual indicator for strategy types (Prevention/Mitigation/Recovery/Transfer)
 * Based on ISO 22301:2019 risk treatment strategies
 */

'use client';

import React from 'react';
import { StrategyType, getStrategyTypeLabel, getStrategyTypeColor } from '@/types/planning';
import { type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StrategyTypeBadgeProps {
  type: StrategyType;
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

const TYPE_CONFIG: Record<StrategyType, TypeConfig> = {
  [StrategyType.PREVENTION]: {
    label: 'Prevention',
    description: 'Preventive strategy to avoid disruptions',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
  },
  [StrategyType.MITIGATION]: {
    label: 'Mitigation',
    description: 'Mitigation strategy to reduce impact',
    bgColor: 'bg-teal-100',
    textColor: 'text-teal-800',
    borderColor: 'border-teal-300',
  },
  [StrategyType.RECOVERY]: {
    label: 'Recovery',
    description: 'Recovery strategy to restore operations',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    borderColor: 'border-green-200',
  },
  [StrategyType.TRANSFER]: {
    label: 'Transfer',
    description: 'Transfer strategy to shift risk',
    bgColor: 'bg-teal-100',
    textColor: 'text-teal-800',
    borderColor: 'border-teal-300',
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
 * StrategyTypeBadge displays a colored badge representing strategy type
 *
 * @param type - The StrategyType value ('prevention', 'mitigation', 'recovery', 'transfer')
 * @param showIcon - Whether to display an icon (default: false)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function StrategyTypeBadge({
  type,
  showIcon = false,
  size = 'md',
  className,
}: StrategyTypeBadgeProps) {
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
      aria-label={`Strategy type: ${config.label}`}
    >
      {config.label}
    </span>
  );
}

/**
 * Get strategy type badge configuration (useful for external components)
 */
export function getStrategyTypeConfig(type: StrategyType): TypeConfig {
  return TYPE_CONFIG[type];
}
