/**
 * PlanStatusBadge Component
 * Visual indicator for plan status (Draft/Review/Approved/Active/Archived)
 * Based on ISO 22301:2019 plan lifecycle states
 */

'use client';

import React from 'react';
import { PlanStatus, getPlanStatusLabel, getPlanStatusColor } from '@/types/planning';
import {
  CheckCircle,
  Clock,
  FileText,
  Shield,
  Archive,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PlanStatusBadgeProps {
  status: PlanStatus;
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

const STATUS_CONFIG: Record<PlanStatus, StatusConfig> = {
  [PlanStatus.DRAFT]: {
    label: 'Draft',
    description: 'Plan is in draft state',
    icon: FileText,
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
  },
  [PlanStatus.REVIEW]: {
    label: 'In Review',
    description: 'Plan is under review',
    icon: Clock,
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
  },
  [PlanStatus.APPROVED]: {
    label: 'Approved',
    description: 'Plan has been approved',
    icon: CheckCircle,
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
  },
  [PlanStatus.ACTIVE]: {
    label: 'Active',
    description: 'Plan is currently active',
    icon: Shield,
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
  },
  [PlanStatus.ARCHIVED]: {
    label: 'Archived',
    description: 'Plan has been archived',
    icon: Archive,
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
 * PlanStatusBadge displays a colored badge representing plan status
 *
 * @param status - The PlanStatus value ('draft', 'review', 'approved', 'active', 'archived')
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function PlanStatusBadge({
  status,
  showIcon = true,
  size = 'md',
  className,
}: PlanStatusBadgeProps) {
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
      aria-label={`Plan status: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * Get plan status badge configuration (useful for external components)
 */
export function getPlanStatusConfig(status: PlanStatus): StatusConfig {
  return STATUS_CONFIG[status];
}
