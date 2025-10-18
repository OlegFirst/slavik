'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { mainNavigation } from '@/config/navigation';
import {
  LayoutDashboard,
  Building2,
  TrendingUp,
  Target,
  AlertTriangle,
  Siren,
  FileText,
  FileCheck,
  CheckCircle,
  GraduationCap,
  Shield,
  Scale,
  Network,
  Brain,
  Users,
  BarChart3,
  Settings,
  Activity,
  ChevronRight,
  type LucideIcon,
} from 'lucide-react';

// Icon mapping
const iconMap: Record<string, LucideIcon> = {
  LayoutDashboard,
  Building2,
  TrendingUp,
  Target,
  AlertTriangle,
  Siren,
  FileText,
  FileCheck,
  CheckCircle,
  GraduationCap,
  Shield,
  Scale,
  Network,
  Brain,
  Users,
  BarChart3,
  Settings,
  Activity,
};

interface SidebarProps {
  collapsed?: boolean;
}

export function Sidebar({ collapsed = false }: SidebarProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={cn(
        'flex flex-col border-r bg-background transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo / Brand */}
      <div className="flex h-16 items-center border-b px-6">
        {!collapsed ? (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600" />
            <div>
              <h1 className="text-lg font-semibold">AI Platform</h1>
              <p className="text-xs text-muted-foreground">ISO 22301 BCM</p>
            </div>
          </Link>
        ) : (
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600" />
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {mainNavigation.map((section, sectionIdx) => (
          <div key={section.section} className="mb-6">
            {!collapsed && (
              <h3 className="mb-2 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {section.section}
              </h3>
            )}
            <ul className="space-y-1 px-3">
              {section.items.map((item) => {
                const Icon = item.icon ? iconMap[item.icon] : null;
                const active = isActive(item.href);
                const isDevelopment = item.status === 'development';

                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all',
                        active
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                        isDevelopment && 'opacity-60 cursor-not-allowed',
                        collapsed && 'justify-center'
                      )}
                      onClick={(e) => {
                        if (isDevelopment) {
                          e.preventDefault();
                        }
                      }}
                      title={collapsed ? item.name : undefined}
                    >
                      {Icon && <Icon className="h-4 w-4 shrink-0" />}

                      {!collapsed && (
                        <>
                          <span className="flex-1">{item.name}</span>

                          {item.badge && (
                            <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                              {item.badge}
                            </span>
                          )}

                          {isDevelopment && (
                            <span className="text-xs opacity-60">Dev</span>
                          )}

                          {active && (
                            <ChevronRight className="h-4 w-4" />
                          )}
                        </>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer / User Info */}
      <div className="border-t p-4">
        {!collapsed ? (
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600" />
            <div className="flex-1 text-sm">
              <p className="font-medium">Platform User</p>
              <p className="text-xs text-muted-foreground">admin@platform.com</p>
            </div>
          </div>
        ) : (
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 mx-auto" />
        )}
      </div>
    </aside>
  );
}
