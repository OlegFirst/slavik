'use client';

/**
 * PermissionBadge Component
 * Badge component for displaying document share permission levels
 * Week 4 Round 3 - Documents Module
 */

import { SharePermission } from '@/types/documents';
import { Eye, MessageCircle, Edit, Shield } from 'lucide-react';
import { getPermissionLabel, getPermissionIcon } from '@/hooks/documents';

export interface PermissionBadgeProps {
  permission: SharePermission;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showTooltip?: boolean;
  interactive?: boolean;
  onClick?: () => void;
}

/**
 * Permission configuration with colors, descriptions, and icons
 */
const PERMISSION_CONFIG = {
  [SharePermission.VIEW]: {
    label: 'View Only',
    description: 'Can view document content only. No editing or commenting allowed.',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
    borderClass: 'border-blue-200',
    Icon: Eye,
  },
  [SharePermission.COMMENT]: {
    label: 'Can Comment',
    description: 'Can view document and add comments or suggestions. Cannot edit content.',
    bgClass: 'bg-amber-100',
    textClass: 'text-amber-800',
    borderClass: 'border-amber-200',
    Icon: MessageCircle,
  },
  [SharePermission.EDIT]: {
    label: 'Can Edit',
    description: 'Can view, comment, and edit document content. Cannot manage sharing.',
    bgClass: 'bg-orange-100',
    textClass: 'text-orange-800',
    borderClass: 'border-orange-200',
    Icon: Edit,
  },
  [SharePermission.ADMIN]: {
    label: 'Admin Access',
    description: 'Full access including viewing, editing, sharing, and deleting the document.',
    bgClass: 'bg-rose-100',
    textClass: 'text-rose-800',
    borderClass: 'border-rose-200',
    Icon: Shield,
  },
};

/**
 * Size configuration for different badge variants
 */
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

export function PermissionBadge({
  permission,
  size = 'md',
  showIcon = true,
  showTooltip = true,
  interactive = false,
  onClick,
}: PermissionBadgeProps) {
  const config = PERMISSION_CONFIG[permission];
  const sizeConfig = SIZE_CONFIG[size];
  const Icon = config.Icon;

  const baseClasses = `
    inline-flex items-center gap-1.5 rounded-full font-medium border
    ${config.bgClass} ${config.textClass} ${config.borderClass}
    ${sizeConfig.textClass} ${sizeConfig.paddingClass}
    ${interactive ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
  `;

  const badge = (
    <span
      className={baseClasses}
      onClick={interactive ? onClick : undefined}
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
      aria-label={`Permission level: ${config.label}`}
      aria-description={showTooltip ? config.description : undefined}
      onKeyDown={
        interactive
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick?.();
              }
            }
          : undefined
      }
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );

  // If tooltip is enabled, wrap in a container with title attribute
  if (showTooltip) {
    return (
      <span title={config.description} className="inline-block">
        {badge}
      </span>
    );
  }

  return badge;
}

/**
 * Get permission level description for accessibility
 */
export function getPermissionDescription(permission: SharePermission): string {
  return PERMISSION_CONFIG[permission]?.description || '';
}

/**
 * Get permission level order (for sorting)
 * Higher number = more permissions
 */
export function getPermissionOrder(permission: SharePermission): number {
  const order = {
    [SharePermission.VIEW]: 1,
    [SharePermission.COMMENT]: 2,
    [SharePermission.EDIT]: 3,
    [SharePermission.ADMIN]: 4,
  };
  return order[permission] || 0;
}

/**
 * Compare two permissions to determine which is higher
 * Returns true if permission1 is higher than permission2
 */
export function isHigherPermission(
  permission1: SharePermission,
  permission2: SharePermission
): boolean {
  return getPermissionOrder(permission1) > getPermissionOrder(permission2);
}
