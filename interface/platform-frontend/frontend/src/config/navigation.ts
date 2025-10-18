/**
 * Navigation Configuration
 * Defines the complete platform navigation structure
 * Generated: 2025-10-17
 */

import { LucideIcon } from 'lucide-react';
import type { ServiceName } from './services';

export interface NavigationItem {
  name: string;
  href: string;
  icon?: string; // Icon name from lucide-react
  service?: ServiceName;
  status?: 'production' | 'development' | 'coming-soon';
  badge?: string;
  requiresAdmin?: boolean;
  requiresPermission?: string;
}

export interface NavigationSection {
  section: string;
  items: NavigationItem[];
}

/**
 * Main Platform Navigation
 * Used in sidebar component
 */
export const mainNavigation: NavigationSection[] = [
  {
    section: "Overview",
    items: [
      {
        name: "Dashboard",
        href: "/dashboard",
        icon: "LayoutDashboard",
        status: "production",
      },
      {
        name: "Organizations",
        href: "/organizations",
        icon: "Building2",
        status: "production",
      },
    ],
  },
  {
    section: "BCM Core", // ISO 22301 основные модули
    items: [
      {
        name: "BIA",
        href: "/bia",
        icon: "TrendingUp",
        service: "BIA",
        status: "production",
        badge: "Active",
      },
      {
        name: "Planning",
        href: "/planning",
        icon: "Target",
        service: "PLANNING",
        status: "production",
      },
      {
        name: "Risk Management",
        href: "/risk",
        icon: "AlertTriangle",
        service: "RISK",
        status: "development",
      },
      {
        name: "Response",
        href: "/response",
        icon: "Siren",
        service: "RESPONSE",
        status: "development",
      },
    ],
  },
  {
    section: "Operations",
    items: [
      {
        name: "Documents",
        href: "/documents",
        icon: "FileText",
        service: "DOCUMENTS",
        status: "development",
      },
      {
        name: "Plans",
        href: "/plans",
        icon: "FileCheck",
        service: "PLANS",
        status: "development",
      },
      {
        name: "Validation",
        href: "/validation",
        icon: "CheckCircle",
        service: "VALIDATION",
        status: "production",
      },
      {
        name: "Learning",
        href: "/learning",
        icon: "GraduationCap",
        service: "LEARNING",
        status: "production",
      },
    ],
  },
  {
    section: "Governance",
    items: [
      {
        name: "Compliance",
        href: "/compliance",
        icon: "Shield",
        service: "COMPLIANCE",
        status: "development",
      },
      {
        name: "Governance",
        href: "/governance",
        icon: "Scale",
        service: "GOVERNANCE",
        status: "development",
      },
    ],
  },
  {
    section: "Intelligence",
    items: [
      {
        name: "Digital Twin",
        href: "/digital-twin",
        icon: "Network",
        service: "DIGITAL_TWIN",
        status: "production",
        badge: "New",
      },
      {
        name: "AI Services",
        href: "/ai",
        icon: "Brain",
        service: "AI_FOUNDATION",
        status: "production",
      },
      {
        name: "Community",
        href: "/community",
        icon: "Users",
        service: "COMMUNITY",
        status: "production",
      },
      {
        name: "Analytics",
        href: "/analytics",
        icon: "BarChart3",
        service: "ANALYTICS",
        status: "production",
      },
    ],
  },
  {
    section: "Platform",
    items: [
      {
        name: "Admin",
        href: "/admin",
        icon: "Settings",
        requiresAdmin: true,
        status: "production",
      },
      {
        name: "Monitoring",
        href: "/admin/monitoring",
        icon: "Activity",
        requiresAdmin: true,
        status: "production",
      },
    ],
  },
];

/**
 * Quick Actions (for dashboard or header)
 */
export const quickActions: NavigationItem[] = [
  {
    name: "New BIA",
    href: "/bia/create",
    icon: "Plus",
    service: "BIA",
  },
  {
    name: "Platform Topology",
    href: "/digital-twin/topology",
    icon: "Network",
    service: "DIGITAL_TWIN",
  },
  {
    name: "Run Exercise",
    href: "/validation/exercises/create",
    icon: "Play",
    service: "VALIDATION",
  },
];

/**
 * User Menu Items
 */
export const userMenuItems: NavigationItem[] = [
  {
    name: "Profile",
    href: "/profile",
    icon: "User",
  },
  {
    name: "Settings",
    href: "/settings",
    icon: "Settings",
  },
  {
    name: "Notifications",
    href: "/notifications",
    icon: "Bell",
  },
];

/**
 * Get navigation items by status
 */
export function getNavigationByStatus(
  status: 'production' | 'development' | 'coming-soon'
): NavigationItem[] {
  return mainNavigation
    .flatMap(section => section.items)
    .filter(item => item.status === status);
}

/**
 * Get production-ready navigation
 */
export function getProductionNavigation(): NavigationSection[] {
  return mainNavigation.map(section => ({
    ...section,
    items: section.items.filter(item => item.status === 'production'),
  })).filter(section => section.items.length > 0);
}
