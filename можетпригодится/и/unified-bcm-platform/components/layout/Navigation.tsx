'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { 
  Home,
  Shield,
  AlertTriangle,
  TrendingUp,
  Users,
  BookOpen,
  Settings,
  BarChart3,
  Brain,
  Globe,
  FileText,
  Activity,
  Target,
  Zap,
  Building,
  UserCheck,
  Calendar,
  MessageSquare,
  Puzzle,
  Gamepad2,
  PieChart,
  CheckSquare,
  Briefcase,
  Monitor,
  Layout,
  Database,
  Cpu,
  HeadphonesIcon
} from 'lucide-react'

// Конфигурация модулей BCM
const BCM_MODULES = [
  // Core Infrastructure
  {
    category: 'Core Infrastructure',
    modules: [
      { name: 'Dashboard', href: '/', icon: Home },
      { name: 'BCM Core', href: '/modules/bcm-core', icon: Building },
      { name: 'AI Control Center', href: '/modules/ai-control', icon: Brain },
      { name: 'Digital Twin', href: '/modules/digital-twin', icon: Globe },
      { name: 'Context Management', href: '/modules/context', icon: Layout },
      { name: 'Configuration', href: '/modules/config', icon: Settings },
    ]
  },
  
  // Business Process
  {
    category: 'Business Process',
    modules: [
      { name: 'BIA Analysis', href: '/modules/bia', icon: TrendingUp },
      { name: 'Risk Management', href: '/modules/risk-management', icon: Shield },
      { name: 'Incident Management', href: '/modules/incidents', icon: AlertTriangle },
      { name: 'Governance', href: '/modules/governance', icon: UserCheck },
      { name: 'Plans Management', href: '/modules/plans', icon: FileText },
    ]
  },
  
  // Training & Community
  {
    category: 'Training & Community', 
    modules: [
      { name: 'Training', href: '/modules/training', icon: BookOpen },
      { name: 'Community', href: '/modules/community', icon: MessageSquare },
      { name: 'Scenario Hub', href: '/modules/scenarios', icon: Puzzle },
      { name: 'Exercises', href: '/modules/exercises', icon: Gamepad2 },
    ]
  },
  
  // Analytics & Reporting
  {
    category: 'Analytics & Reporting',
    modules: [
      { name: 'Reporting', href: '/modules/reporting', icon: BarChart3 },
      { name: 'KPI Management', href: '/modules/kpi', icon: Target },
      { name: 'Audit', href: '/modules/audit', icon: CheckSquare },
    ]
  },
  
  // Client & Portal
  {
    category: 'Client & Portal',
    modules: [
      { name: 'Clients', href: '/modules/clients', icon: Briefcase },
      { name: 'Portal', href: '/modules/portal', icon: Monitor },
      { name: 'Templates', href: '/modules/templates', icon: Database },
    ]
  },
  
  // AI & Advanced
  {
    category: 'AI & Advanced',
    modules: [
      { name: 'AI Assistant', href: '/modules/ai-assistant', icon: HeadphonesIcon },
      { name: 'AI Orchestrator', href: '/modules/ai-orchestrator', icon: Cpu },
      { name: 'Intelligent Base', href: '/modules/intelligent-base', icon: Zap },
    ]
  },
  
  // Sections (Advanced Views)
  {
    category: 'Advanced Sections',
    modules: [
      { name: 'Digital Twin Section', href: '/sections/digital-twin', icon: Globe },
      { name: 'Admin Panel', href: '/sections/admin-panel', icon: Settings },
      { name: 'Personal Dashboard', href: '/sections/personal', icon: Users },
      { name: 'Analytics Hub', href: '/sections/analytics', icon: PieChart },
    ]
  }
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white border-r h-screen overflow-y-auto">
      {/* Логотип */}
      <div className="p-6 border-b">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-gray-900">BCM Platform</div>
            <div className="text-xs text-gray-500">Business Continuity</div>
          </div>
        </Link>
      </div>

      {/* Навигация по модулям */}
      <div className="p-4 space-y-6">
        {BCM_MODULES.map((category) => (
          <div key={category.category}>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              {category.category}
            </h3>
            <div className="space-y-1">
              {category.modules.map((module) => {
                const isActive = pathname === module.href
                const Icon = module.icon
                
                return (
                  <Link
                    key={module.href}
                    href={module.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                      isActive 
                        ? "bg-blue-50 text-blue-700 font-medium"
                        : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {module.name}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function TopBar() {
  return (
    <div className="h-16 bg-white border-b px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-gray-900">BCM Platform</h1>
      </div>
      
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm">
          <Activity className="h-4 w-4 mr-2" />
          System Health
        </Button>
        <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
      </div>
    </div>
  )
}
