/**
 * ActionTypeBadge Component
 * Visual indicator for action types (Preventive/Detective/Corrective/Recovery)
 * Based on ISO 22301:2019 action classification
 */

'use client';

import React from 'react';
import { ActionType, getActionTypeLabel, getActionTypeColor } from '@/types/planning';
import { type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ActionTypeBadgeProps {
  type: ActionType;
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

const TYPE_CONFIG: Record<ActionType, TypeConfig> = {
  [ActionType.PREVENTIVE]: {
    label: 'Preventive',
    description: 'Preventive action to avoid incidents',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
    borderColor: 'border-purple-300',
  },
  [ActionType.DETECTIVE]: {
    label: 'Detective',
    description: 'Detective action to identify issues',
    bgColor: 'bg-pink-100',
    textColor: 'text-pink-800',
    borderColor: 'border-pink-300',
  },
  [ActionType.CORRECTIVE]: {
    label: 'Corrective',
    description: 'Corrective action to fix problems',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-700',
    borderColor: 'border-purple-200',
  },
  [ActionType.RECOVERY]: {
    label: 'Recovery',
    description: 'Recovery action to restore services',
    bgColor: 'bg-pink-100',
    textColor: 'text-pink-800',
    borderColor: 'border-pink-300',
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
 * ActionTypeBadge displays a colored badge representing action type
 *
 * @param type - The ActionType value ('preventive', 'detective', 'corrective', 'recovery')
 * @param showIcon - Whether to display an icon (default: false)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function ActionTypeBadge({
  type,
  showIcon = false,
  size = 'md',
  className,
}: ActionTypeBadgeProps) {
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
      aria-label={`Action type: ${config.label}`}
    >
      {config.label}
    </span>
  );
}

/**
 * Get action type badge configuration (useful for external components)
 */
export function getActionTypeConfig(type: ActionType): TypeConfig {
  return TYPE_CONFIG[type];
}
