/**
 * RiskSeverityBadge Component
 * Visual indicator for risk severity levels (Critical/High/Medium/Low)
 * Based on risk score (1-25) or direct severity input
 */

'use client';

import React from 'react';
import { RiskSeverity, getRiskSeverity, getSeverityColor } from '@/types/risk';
import {
  AlertTriangle,
  AlertOctagon,
  AlertCircle,
  Info,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RiskSeverityBadgeProps {
  severity: RiskSeverity;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export interface RiskSeverityBadgeFromScoreProps {
  score: number;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface SeverityConfig {
  label: string;
  description: string;
  icon: LucideIcon;
  bgColor: string;
  textColor: string;
  borderColor: string;
  badgeColor: string;
}

const SEVERITY_CONFIG: Record<RiskSeverity, SeverityConfig> = {
  critical: {
    label: 'Critical',
    description: 'Critical risk requiring immediate action (score 20-25)',
    icon: AlertOctagon,
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    badgeColor: 'bg-red-600 text-white',
  },
  high: {
    label: 'High',
    description: 'High risk requiring prompt attention (score 15-19)',
    icon: AlertTriangle,
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    borderColor: 'border-orange-300',
    badgeColor: 'bg-orange-600 text-white',
  },
  medium: {
    label: 'Medium',
    description: 'Medium risk requiring monitoring and mitigation (score 8-14)',
    icon: AlertCircle,
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
    badgeColor: 'bg-yellow-600 text-white',
  },
  low: {
    label: 'Low',
    description: 'Low risk with minimal impact (score 1-7)',
    icon: Info,
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
    badgeColor: 'bg-green-600 text-white',
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
 * RiskSeverityBadge displays a colored badge representing risk severity
 *
 * @param severity - The RiskSeverity value ('low', 'medium', 'high', 'critical')
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function RiskSeverityBadge({
  severity,
  showIcon = true,
  size = 'md',
  className,
}: RiskSeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity];
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
      aria-label={`Risk severity: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * RiskSeverityBadgeFromScore displays severity badge calculated from risk score
 *
 * @param score - Risk score (1-25, calculated as likelihood × impact)
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function RiskSeverityBadgeFromScore({
  score,
  showIcon = true,
  size = 'md',
  className,
}: RiskSeverityBadgeFromScoreProps) {
  const severity = getRiskSeverity(score);
  return (
    <RiskSeverityBadge
      severity={severity}
      showIcon={showIcon}
      size={size}
      className={className}
    />
  );
}

/**
 * Get severity badge configuration (useful for external components)
 */
export function getSeverityConfig(severity: RiskSeverity): SeverityConfig {
  return SEVERITY_CONFIG[severity];
}
