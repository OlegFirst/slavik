/**
 * DocumentStatusBadge Component
 * Visual indicator for document lifecycle status
 * Supports all DocumentStatus enum values with color coding and tooltips
 */

'use client';

import { DocumentStatus } from '@/types/documents';
import { cn } from '@/lib/utils';
import {
  FileText,
  Clock,
  CheckCircle,
  Globe,
  Archive,
  GitBranch,
  XCircle,
} from 'lucide-react';

export interface DocumentStatusBadgeProps {
  status: DocumentStatus;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const STATUS_CONFIG = {
  [DocumentStatus.DRAFT]: {
    label: 'Draft',
    description: 'Document is in draft state and being edited',
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-800',
    borderClass: 'border-gray-300',
    Icon: FileText,
  },
  [DocumentStatus.UNDER_REVIEW]: {
    label: 'Under Review',
    description: 'Document is being reviewed by approvers',
    bgClass: 'bg-amber-100',
    textClass: 'text-amber-800',
    borderClass: 'border-amber-300',
    Icon: Clock,
  },
  [DocumentStatus.APPROVED]: {
    label: 'Approved',
    description: 'Document has been approved but not yet published',
    bgClass: 'bg-green-100',
    textClass: 'text-green-800',
    borderClass: 'border-green-300',
    Icon: CheckCircle,
  },
  [DocumentStatus.PUBLISHED]: {
    label: 'Published',
    description: 'Document is active and available to users',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
    borderClass: 'border-blue-300',
    Icon: Globe,
  },
  [DocumentStatus.ARCHIVED]: {
    label: 'Archived',
    description: 'Document has been archived for retention',
    bgClass: 'bg-slate-100',
    textClass: 'text-slate-800',
    borderClass: 'border-slate-300',
    Icon: Archive,
  },
  [DocumentStatus.SUPERSEDED]: {
    label: 'Superseded',
    description: 'Document has been replaced by a newer version',
    bgClass: 'bg-purple-100',
    textClass: 'text-purple-800',
    borderClass: 'border-purple-300',
    Icon: GitBranch,
  },
  [DocumentStatus.OBSOLETE]: {
    label: 'Obsolete',
    description: 'Document is no longer valid or in use',
    bgClass: 'bg-red-100',
    textClass: 'text-red-800',
    borderClass: 'border-red-300',
    Icon: XCircle,
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

/**
 * DocumentStatusBadge displays a colored badge representing document lifecycle status
 *
 * @param status - The DocumentStatus enum value
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function DocumentStatusBadge({
  status,
  showIcon = true,
  size = 'md',
  className,
}: DocumentStatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const sizeConfig = SIZE_CONFIG[size];
  const Icon = config.Icon;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium border transition-colors duration-200',
        config.bgClass,
        config.textClass,
        config.borderClass,
        sizeConfig.textClass,
        sizeConfig.paddingClass,
        className
      )}
      title={config.description}
      role="status"
      aria-label={`Document status: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * Get status badge configuration (useful for external components)
 */
export function getStatusConfig(status: DocumentStatus) {
  return STATUS_CONFIG[status];
}

/**
 * Get status workflow order (0-100, higher = further in lifecycle)
 */
export function getStatusProgress(status: DocumentStatus): number {
  const progress = {
    [DocumentStatus.DRAFT]: 0,
    [DocumentStatus.UNDER_REVIEW]: 30,
    [DocumentStatus.APPROVED]: 60,
    [DocumentStatus.PUBLISHED]: 100,
    [DocumentStatus.ARCHIVED]: 100,
    [DocumentStatus.SUPERSEDED]: 80,
    [DocumentStatus.OBSOLETE]: 50,
  };
  return progress[status];
}
