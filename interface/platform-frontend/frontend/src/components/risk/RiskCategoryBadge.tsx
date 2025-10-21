/**
 * RiskCategoryBadge Component
 * Visual indicator for risk category classification
 * Supports all 7 RiskCategory enum values with icons and color coding
 */

'use client';

import React from 'react';
import { RiskCategory } from '@/types/risk';
import {
  Building2,
  DollarSign,
  Target,
  FileCheck,
  MessageSquare,
  Shield,
  CloudLightning,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RiskCategoryBadgeProps {
  category: RiskCategory;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface CategoryConfig {
  label: string;
  description: string;
  icon: LucideIcon;
  bgColor: string;
  textColor: string;
  borderColor: string;
}

const CATEGORY_CONFIG: Record<RiskCategory, CategoryConfig> = {
  [RiskCategory.OPERATIONAL]: {
    label: 'Operational',
    description: 'Operational and process-related risks',
    icon: Building2,
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
  },
  [RiskCategory.FINANCIAL]: {
    label: 'Financial',
    description: 'Financial and economic risks',
    icon: DollarSign,
    bgColor: 'bg-emerald-100',
    textColor: 'text-emerald-800',
    borderColor: 'border-emerald-300',
  },
  [RiskCategory.STRATEGIC]: {
    label: 'Strategic',
    description: 'Strategic and business direction risks',
    icon: Target,
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
    borderColor: 'border-purple-300',
  },
  [RiskCategory.COMPLIANCE]: {
    label: 'Compliance',
    description: 'Regulatory and compliance risks',
    icon: FileCheck,
    bgColor: 'bg-indigo-100',
    textColor: 'text-indigo-800',
    borderColor: 'border-indigo-300',
  },
  [RiskCategory.REPUTATIONAL]: {
    label: 'Reputational',
    description: 'Brand and reputation risks',
    icon: MessageSquare,
    bgColor: 'bg-pink-100',
    textColor: 'text-pink-800',
    borderColor: 'border-pink-300',
  },
  [RiskCategory.CYBERSECURITY]: {
    label: 'Cybersecurity',
    description: 'Information security and cyber risks',
    icon: Shield,
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
  },
  [RiskCategory.NATURAL_DISASTER]: {
    label: 'Natural Disaster',
    description: 'Natural disaster and environmental risks',
    icon: CloudLightning,
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    borderColor: 'border-orange-300',
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
 * RiskCategoryBadge displays a colored badge representing the risk category
 *
 * @param category - The RiskCategory enum value
 * @param showIcon - Whether to display an icon (default: true)
 * @param size - Badge size variant (default: 'md')
 * @param className - Additional CSS classes
 */
export function RiskCategoryBadge({
  category,
  showIcon = true,
  size = 'md',
  className,
}: RiskCategoryBadgeProps) {
  const config = CATEGORY_CONFIG[category];
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
      aria-label={`Risk category: ${config.label}`}
    >
      {showIcon && <Icon className={sizeConfig.iconSize} aria-hidden="true" />}
      {config.label}
    </span>
  );
}

/**
 * Get category badge configuration (useful for external components)
 */
export function getCategoryConfig(category: RiskCategory): CategoryConfig {
  return CATEGORY_CONFIG[category];
}
