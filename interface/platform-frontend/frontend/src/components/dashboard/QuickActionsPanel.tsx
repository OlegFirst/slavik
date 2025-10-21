/**
 * QuickActionsPanel Component
 * Enhanced quick action buttons for dashboard
 * Production ready with full TypeScript support
 *
 * Features:
 * - 6 Quick action cards with icons, descriptions, and links
 * - Responsive grid layout (1/2/3 columns)
 * - Gradient backgrounds with hover effects
 * - Smooth transitions and animations
 * - Color-coded by action type
 * - Direct navigation to key platform features
 */

'use client';

import Link from 'next/link';
import {
  AlertTriangle,
  Upload,
  Activity,
  Calendar,
  FileText,
  CheckCircle2,
  LucideIcon,
  ArrowRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Action configuration type
 */
interface QuickAction {
  title: string;
  description: string;
  icon: LucideIcon;
  href: string;
  color: ActionColor;
  gradient: string;
  hoverGradient: string;
  iconBg: string;
  textColor: string;
}

/**
 * Available color themes
 */
type ActionColor = 'red' | 'blue' | 'purple' | 'green' | 'gray' | 'teal';

/**
 * Quick Actions configuration
 * Defines all available quick actions with their properties
 */
const quickActions: QuickAction[] = [
  {
    title: 'Create Risk Assessment',
    description: 'Identify and assess new organizational risks with comprehensive analysis tools',
    icon: AlertTriangle,
    href: '/risk/new',
    color: 'red',
    gradient: 'from-red-50 to-orange-50',
    hoverGradient: 'hover:from-red-100 hover:to-orange-100',
    iconBg: 'bg-red-100',
    textColor: 'text-red-600',
  },
  {
    title: 'Upload Document',
    description: 'Upload and manage business continuity documents with version control',
    icon: Upload,
    href: '/documents/upload',
    color: 'blue',
    gradient: 'from-blue-50 to-cyan-50',
    hoverGradient: 'hover:from-blue-100 hover:to-cyan-100',
    iconBg: 'bg-blue-100',
    textColor: 'text-blue-600',
  },
  {
    title: 'Start BIA Analysis',
    description: 'Begin business impact analysis to identify critical processes and dependencies',
    icon: Activity,
    href: '/bia/new',
    color: 'purple',
    gradient: 'from-purple-50 to-pink-50',
    hoverGradient: 'hover:from-purple-100 hover:to-pink-100',
    iconBg: 'bg-purple-100',
    textColor: 'text-purple-600',
  },
  {
    title: 'Schedule Exercise',
    description: 'Plan and schedule business continuity exercises and validation tests',
    icon: Calendar,
    href: '/validation/exercises/create',
    color: 'green',
    gradient: 'from-green-50 to-emerald-50',
    hoverGradient: 'hover:from-green-100 hover:to-emerald-100',
    iconBg: 'bg-green-100',
    textColor: 'text-green-600',
  },
  {
    title: 'View Reports',
    description: 'Access comprehensive reports and analytics for all platform activities',
    icon: FileText,
    href: '/reports',
    color: 'gray',
    gradient: 'from-gray-50 to-slate-50',
    hoverGradient: 'hover:from-gray-100 hover:to-slate-100',
    iconBg: 'bg-gray-100',
    textColor: 'text-gray-600',
  },
  {
    title: 'Compliance Check',
    description: 'Generate compliance reports and verify ISO 22301 standard adherence',
    icon: CheckCircle2,
    href: '/compliance',
    color: 'teal',
    gradient: 'from-teal-50 to-cyan-50',
    hoverGradient: 'hover:from-teal-100 hover:to-cyan-100',
    iconBg: 'bg-teal-100',
    textColor: 'text-teal-600',
  },
];

/**
 * ActionCard Component
 * Individual action card with icon, title, description and link
 */
interface ActionCardProps {
  action: QuickAction;
}

function ActionCard({ action }: ActionCardProps) {
  const Icon = action.icon;

  return (
    <Link
      href={action.href}
      className={cn(
        'group relative overflow-hidden',
        'bg-gradient-to-br',
        action.gradient,
        action.hoverGradient,
        'rounded-xl shadow-md hover:shadow-xl',
        'border border-gray-200 hover:border-gray-300',
        'transition-all duration-300 ease-in-out',
        'transform hover:-translate-y-1',
        'p-6',
        'flex flex-col',
        'min-h-[180px]'
      )}
    >
      {/* Decorative gradient overlay on hover */}
      <div
        className={cn(
          'absolute inset-0 opacity-0 group-hover:opacity-10',
          'bg-gradient-to-br from-white to-transparent',
          'transition-opacity duration-300'
        )}
      />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Icon */}
        <div className="mb-4">
          <div
            className={cn(
              action.iconBg,
              'rounded-lg p-3 inline-flex',
              'group-hover:scale-110 transition-transform duration-300'
            )}
          >
            <Icon className={cn('w-6 h-6', action.textColor)} />
          </div>
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-gray-800">
          {action.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4 flex-grow leading-relaxed">
          {action.description}
        </p>

        {/* Action indicator */}
        <div className="flex items-center gap-2 text-sm font-medium">
          <span className={action.textColor}>Get started</span>
          <ArrowRight
            className={cn(
              'w-4 h-4',
              action.textColor,
              'group-hover:translate-x-1 transition-transform duration-300'
            )}
          />
        </div>
      </div>

      {/* Hover border effect */}
      <div
        className={cn(
          'absolute inset-0 rounded-xl',
          'ring-2 ring-transparent',
          'group-hover:ring-opacity-50',
          action.textColor.replace('text-', 'group-hover:ring-'),
          'transition-all duration-300 pointer-events-none'
        )}
      />
    </Link>
  );
}

/**
 * QuickActionsPanel Component
 * Main component that renders the grid of quick action cards
 *
 * Layout:
 * - Mobile: 1 column
 * - Tablet: 2 columns
 * - Desktop: 3 columns
 */
export function QuickActionsPanel() {
  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Quick Actions</h2>
        <p className="text-gray-600">
          Access key platform features and start important tasks
        </p>
      </div>

      {/* Actions Grid */}
      <div
        className={cn(
          'grid gap-4',
          'grid-cols-1',
          'md:grid-cols-2',
          'lg:grid-cols-3',
          'auto-rows-fr'
        )}
      >
        {quickActions.map((action) => (
          <ActionCard key={action.title} action={action} />
        ))}
      </div>

      {/* Additional Info */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Activity className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Need Help?</h4>
            <p className="text-sm text-blue-700">
              Each action includes guided workflows and built-in validation to help you complete
              tasks efficiently. Click any card above to get started.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * QuickActionsPanelCompact Component
 * Compact variant without header and info sections
 * Useful for embedding in smaller spaces
 */
export function QuickActionsPanelCompact() {
  return (
    <div
      className={cn(
        'grid gap-3',
        'grid-cols-1',
        'sm:grid-cols-2',
        'lg:grid-cols-3',
        'auto-rows-fr'
      )}
    >
      {quickActions.map((action) => (
        <ActionCard key={action.title} action={action} />
      ))}
    </div>
  );
}

/**
 * Individual action exports for standalone use
 */
export const actions = quickActions;

/**
 * Hook to get specific actions by color
 */
export function useActionsByColor(color: ActionColor): QuickAction[] {
  return quickActions.filter((action) => action.color === color);
}

/**
 * Hook to get action by href
 */
export function useActionByHref(href: string): QuickAction | undefined {
  return quickActions.find((action) => action.href === href);
}

/**
 * Example usage in a page:
 *
 * import { QuickActionsPanel } from '@/components/dashboard/QuickActionsPanel';
 *
 * export default function DashboardPage() {
 *   return (
 *     <div className="container mx-auto p-6">
 *       <QuickActionsPanel />
 *     </div>
 *   );
 * }
 *
 * For compact version:
 *
 * import { QuickActionsPanelCompact } from '@/components/dashboard/QuickActionsPanel';
 *
 * export default function SidebarWidget() {
 *   return (
 *     <div className="p-4">
 *       <QuickActionsPanelCompact />
 *     </div>
 *   );
 * }
 */
