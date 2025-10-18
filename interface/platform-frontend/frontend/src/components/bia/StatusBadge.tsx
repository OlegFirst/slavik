/**
 * StatusBadge Component
 * Visual indicator for BIA process status
 * Professional, consistent styling across the platform
 */

import { ProcessStatus } from '@/types/bia';
import { FileText, Loader2, CheckCircle2 } from 'lucide-react';

interface StatusBadgeProps {
  status: ProcessStatus;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const STATUS_CONFIG = {
  [ProcessStatus.DRAFT]: {
    label: 'Draft',
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-800',
    borderClass: 'border-gray-200',
    Icon: FileText,
  },
  [ProcessStatus.IN_PROGRESS]: {
    label: 'In Progress',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
    borderClass: 'border-blue-200',
    Icon: Loader2,
  },
  [ProcessStatus.COMPLETED]: {
    label: 'Completed',
    bgClass: 'bg-green-100',
    textClass: 'text-green-800',
    borderClass: 'border-green-200',
    Icon: CheckCircle2,
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

export function StatusBadge({
  status,
  showIcon = true,
  size = 'md',
}: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const sizeConfig = SIZE_CONFIG[size];
  const Icon = config.Icon;

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium border
        ${config.bgClass} ${config.textClass} ${config.borderClass}
        ${sizeConfig.textClass} ${sizeConfig.paddingClass}
      `}
    >
      {showIcon && (
        <Icon
          className={`${sizeConfig.iconSize} ${status === ProcessStatus.IN_PROGRESS ? 'animate-spin' : ''}`}
        />
      )}
      {config.label}
    </span>
  );
}

/**
 * Get status progress percentage (0-100)
 */
export function getStatusProgress(status: ProcessStatus): number {
  const progress = {
    [ProcessStatus.DRAFT]: 0,
    [ProcessStatus.IN_PROGRESS]: 50,
    [ProcessStatus.COMPLETED]: 100,
  };
  return progress[status];
}
