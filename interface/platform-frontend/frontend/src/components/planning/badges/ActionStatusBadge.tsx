/**
 * ActionStatusBadge Component
 * Visual indicator for action status (Not Started/In Progress/Completed/Delayed/Cancelled)
 * Based on ISO 22301:2019 action execution tracking
 */

'use client';

import React from 'react';
import { ActionStatus, getActionStatusLabel, getActionStatusColor } from '@/types/planning';
import {
  Circle,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ActionStatusBadgeProps {
  status: ActionStatus;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface StatusConfig {
  label: string;
  description: string;
  icon: LucideIcon;
  bgColor: string;
  textColor: string;
  borderColor: string;
}

const STATUS_CONFIG: Record<ActionStatus, StatusConfig> = {
  [ActionStatus.NOT_STARTED]: {
    label: 'Not Started',
    description: 'Action has not been started',
    icon: Circle,
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
  },
  [ActionStatus.IN_PROGRESS]: {
    label: 'In Progress',
    description: 'Action is currently in progress',
    icon: Clock,
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
  },
  [ActionStatus.COMPLETED]: {
    label: 'Completed',
    description: 'Action has been completed',
    icon: CheckCircle,
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
  },
  [ActionStatus.DELAYED]: {
    label: 'Delayed',
    description: 'Action is delayed or behind schedule',
    icon: AlertCircle,
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
  },
  [ActionStatus.CANCELLED]: {
    label: 'Cancelled',
    description: 'Action has been cancelled',
    icon: XCircle,
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    borderColor: 'border-gray-200',
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
 * ActionStatusBadge displays a colored badge representing action status
 *
 * @param status - The ActionStatus value ('not_started', 'in_progress', 'completed', 'delayed', 'cancelled')
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function ActionStatusBadge({
  status,
  showIcon = true,
  size = 'md',
  className,
}: ActionStatusBadgeProps) {
  const config = STATUS_CONFIG[status];
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
      aria-label={`Action status: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * Get action status badge configuration (useful for external components)
 */
export function getActionStatusConfig(status: ActionStatus): StatusConfig {
  return STATUS_CONFIG[status];
}
