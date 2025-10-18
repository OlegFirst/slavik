/**
 * WHOTierBadge Component
 * Visual indicator for WHO Essential Services Tier (healthcare)
 * Maps to specific RTO requirements per WHO guidelines
 */

import { WHOTier } from '@/types/bia';
import { Activity } from 'lucide-react';

interface WHOTierBadgeProps {
  tier: WHOTier;
  showIcon?: boolean;
  showRTO?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const WHO_TIER_CONFIG = {
  [WHOTier.TIER_1]: {
    label: 'Tier 1 - Immediate',
    shortLabel: 'T1',
    rto: '0 min',
    description: 'Life-saving services',
    bgClass: 'bg-red-100',
    textClass: 'text-red-800',
    borderClass: 'border-red-300',
    iconColor: 'text-red-600',
  },
  [WHOTier.TIER_2]: {
    label: 'Tier 2 - Urgent',
    shortLabel: 'T2',
    rto: '2-4 hours',
    description: 'Critical care services',
    bgClass: 'bg-orange-100',
    textClass: 'text-orange-800',
    borderClass: 'border-orange-300',
    iconColor: 'text-orange-600',
  },
  [WHOTier.TIER_3]: {
    label: 'Tier 3 - Important',
    shortLabel: 'T3',
    rto: '24 hours',
    description: 'Essential services',
    bgClass: 'bg-yellow-100',
    textClass: 'text-yellow-800',
    borderClass: 'border-yellow-300',
    iconColor: 'text-yellow-600',
  },
  [WHOTier.TIER_4]: {
    label: 'Tier 4 - Normal',
    shortLabel: 'T4',
    rto: '3-5 days',
    description: 'Standard services',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
    borderClass: 'border-blue-300',
    iconColor: 'text-blue-600',
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

export function WHOTierBadge({
  tier,
  showIcon = true,
  showRTO = false,
  size = 'md',
}: WHOTierBadgeProps) {
  const config = WHO_TIER_CONFIG[tier];
  const sizeConfig = SIZE_CONFIG[size];

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium border
        ${config.bgClass} ${config.textClass} ${config.borderClass}
        ${sizeConfig.textClass} ${sizeConfig.paddingClass}
      `}
      title={`${config.description} - RTO: ${config.rto}`}
    >
      {showIcon && <Activity className={`${sizeConfig.iconSize} ${config.iconColor}`} />}
      {size === 'sm' ? config.shortLabel : config.label}
      {showRTO && <span className="opacity-75">({config.rto})</span>}
    </span>
  );
}

/**
 * Get recommended RTO hours for WHO tier
 */
export function getWHOTierRTO(tier: WHOTier): number {
  const rtoHours = {
    [WHOTier.TIER_1]: 0,
    [WHOTier.TIER_2]: 4,
    [WHOTier.TIER_3]: 24,
    [WHOTier.TIER_4]: 96, // 4 days
  };
  return rtoHours[tier];
}

/**
 * Suggest WHO tier based on RTO hours
 */
export function suggestWHOTier(rtoHours: number): WHOTier {
  if (rtoHours <= 1) return WHOTier.TIER_1;
  if (rtoHours <= 4) return WHOTier.TIER_2;
  if (rtoHours <= 24) return WHOTier.TIER_3;
  return WHOTier.TIER_4;
}
