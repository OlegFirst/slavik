'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  FileText,
  AlertTriangle,
  Shield,
  Settings,
  Users,
  BookOpen,
  Activity,
  Database,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'BIA',
    href: '/bia',
    icon: FileText,
    description: 'Business Impact Analysis',
  },
  {
    name: 'Risk Management',
    href: '/risk',
    icon: AlertTriangle,
  },
  {
    name: 'Compliance',
    href: '/compliance',
    icon: Shield,
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: BookOpen,
  },
  {
    name: 'Governance',
    href: '/governance',
    icon: Users,
  },
  {
    name: 'Digital Twin',
    href: '/digital-twin',
    icon: Database,
  },
  {
    name: 'Admin',
    href: '/admin',
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          <span className="text-lg font-bold">AI-Platform-ISO</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname?.startsWith(item.href)
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-xs text-muted-foreground">
            BCM Platform v2.0.0
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            ISO 22301 Compliant
          </p>
        </div>
      </div>
    </div>
  )
}
