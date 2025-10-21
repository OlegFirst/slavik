/**
 * RiskStatusBadge Component
 * Visual indicator for risk lifecycle status
 * Supports all 5 RiskStatus enum values with workflow-based color coding
 */

'use client';

import React from 'react';
import { RiskStatus } from '@/types/risk';
import {
  Search,
  BarChart3,
  CheckCircle,
  Eye,
  Lock,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RiskStatusBadgeProps {
  status: RiskStatus;
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

const STATUS_CONFIG: Record<RiskStatus, StatusConfig> = {
  [RiskStatus.IDENTIFIED]: {
    label: 'Identified',
    description: 'Risk has been identified and documented',
    icon: Search,
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
  },
  [RiskStatus.ANALYZING]: {
    label: 'Analyzing',
    description: 'Risk is being analyzed and assessed',
    icon: BarChart3,
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
  },
  [RiskStatus.TREATED]: {
    label: 'Treated',
    description: 'Risk treatment plan has been implemented',
    icon: CheckCircle,
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
  },
  [RiskStatus.MONITORING]: {
    label: 'Monitoring',
    description: 'Risk is being actively monitored',
    icon: Eye,
    bgColor: 'bg-amber-100',
    textColor: 'text-amber-800',
    borderColor: 'border-amber-300',
  },
  [RiskStatus.CLOSED]: {
    label: 'Closed',
    description: 'Risk has been closed or resolved',
    icon: Lock,
    bgColor: 'bg-slate-100',
    textColor: 'text-slate-800',
    borderColor: 'border-slate-300',
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
 * RiskStatusBadge displays a colored badge representing risk lifecycle status
 *
 * @param status - The RiskStatus enum value
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function RiskStatusBadge({
  status,
  showIcon = true,
  size = 'md',
  className,
}: RiskStatusBadgeProps) {
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
      aria-label={`Risk status: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * Get status badge configuration (useful for external components)
 */
export function getStatusConfig(status: RiskStatus): StatusConfig {
  return STATUS_CONFIG[status];
}

/**
 * Get status workflow order (0-100, higher = further in lifecycle)
 */
export function getStatusProgress(status: RiskStatus): number {
  const progress = {
    [RiskStatus.IDENTIFIED]: 0,
    [RiskStatus.ANALYZING]: 25,
    [RiskStatus.TREATED]: 50,
    [RiskStatus.MONITORING]: 75,
    [RiskStatus.CLOSED]: 100,
  };
  return progress[status];
}
