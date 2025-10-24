/**
 * PriorityBadge Component
 * Visual indicator for priority levels (Critical/High/Medium/Low)
 * Based on ISO 22301:2019 priority classification
 */

'use client';

import React from 'react';
import { Priority, getPriorityLabel, getPriorityColor } from '@/types/planning';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  MinusCircle,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PriorityBadgeProps {
  priority: Priority;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface PriorityConfig {
  label: string;
  description: string;
  icon: LucideIcon;
  bgColor: string;
  textColor: string;
  borderColor: string;
}

const PRIORITY_CONFIG: Record<Priority, PriorityConfig> = {
  [Priority.CRITICAL]: {
    label: 'Critical',
    description: 'Critical priority requiring immediate action',
    icon: AlertTriangle,
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
  },
  [Priority.HIGH]: {
    label: 'High',
    description: 'High priority requiring prompt attention',
    icon: AlertCircle,
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    borderColor: 'border-orange-300',
  },
  [Priority.MEDIUM]: {
    label: 'Medium',
    description: 'Medium priority with moderate urgency',
    icon: Info,
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
  },
  [Priority.LOW]: {
    label: 'Low',
    description: 'Low priority with minimal urgency',
    icon: MinusCircle,
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
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
    paddingClass: 'px-2.5 py-1',
    iconSize: 'w-3.5 h-3.5',
  },
  lg: {
    textClass: 'text-base',
    paddingClass: 'px-3 py-1.5',
    iconSize: 'w-4 h-4',
  },
};

/**
 * PriorityBadge displays a colored badge representing priority level
 *
 * @param priority - The Priority value ('critical', 'high', 'medium', 'low')
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function PriorityBadge({
  priority,
  showIcon = true,
  size = 'md',
  className,
}: PriorityBadgeProps) {
  const config = PRIORITY_CONFIG[priority];
  const sizeConfig = SIZE_CONFIG[size];
  const Icon = config.icon;

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
      aria-label={`Priority: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * Get priority badge configuration (useful for external components)
 */
export function getPriorityConfig(priority: Priority): PriorityConfig {
  return PRIORITY_CONFIG[priority];
}
