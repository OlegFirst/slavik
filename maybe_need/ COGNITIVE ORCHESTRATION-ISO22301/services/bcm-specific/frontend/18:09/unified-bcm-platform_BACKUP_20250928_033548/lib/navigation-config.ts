import {
  Home,
  Shield,
  FileText,
  AlertTriangle,
  GitBranch,
  GraduationCap,
  Building2,
  Bot,
  BarChart3,
  User,
  Settings,
  Building,
  Building3D,
  Target,
  Brain,
  Users,
  Activity,
  ClipboardList,
  BookOpen,
  Database,
  FileCheck,
  TrendingUp,
  Globe,
  UserCheck
} from 'lucide-react'

export interface NavigationItem {
  name: string
  href: string
  icon: any
  description?: string
  badge?: string
  disabled?: boolean
}

export interface NavigationSection {
  title: string
  items: NavigationItem[]
}

// Business Sections Navigation (New Architecture)
export const sectionNavigation: NavigationItem[] = [
  {
    name: 'Central Hub',
    href: '/',
    icon: Home,
    description: 'Main dashboard and overview'
  },
  {
    name: 'Digital Twin',
    href: '/sections/digital-twin',
    icon: Building,
    description: '3D organizational visualization'
  },
  {
    name: 'Risk Assessment',
    href: '/sections/risk-assessment',
    icon: Shield,
    description: 'BIA, Risk Management & Context'
  },
  {
    name: 'Strategy Planning',
    href: '/sections/strategy-planning',
    icon: FileText,
    description: 'Plans, Governance & Templates'
  },
  {
    name: 'Incident Management',
    href: '/sections/incident-management',
    icon: AlertTriangle,
    description: 'Incidents, Exercise & Crisis'
  },
  {
    name: 'Workflow Management',
    href: '/sections/workflow-management',
    icon: GitBranch,
    description: 'BPMN, Process & Automation'
  },
  {
    name: 'Learning Community',
    href: '/sections/learning-community',
    icon: GraduationCap,
    description: 'Training, Community & Knowledge',
    badge: 'New'
  },
  {
    name: 'Client Management',
    href: '/sections/client-management',
    icon: Building2,
    description: 'Clients, Projects & Portal',
    badge: 'New'
  },
  {
    name: 'AI Automation',
    href: '/sections/ai-automation',
    icon: Bot,
    description: 'AI Control & Orchestration'
  },
  {
    name: 'Analytics',
    href: '/sections/analytics',
    icon: BarChart3,
    description: 'Reporting, KPI & BI'
  },
  {
    name: 'My Workspace',
    href: '/sections/workspace',
    icon: User,
    description: 'Personal dashboard & settings'
  },
  {
    name: 'Admin Panel',
    href: '/sections/admin',
    icon: Settings,
    description: 'System configuration & monitoring'
  }
]

// Module Navigation (Original - for compatibility)
export const moduleNavigation: NavigationSection[] = [
  {
    title: 'Core Modules',
    items: [
      { name: 'BIA Module', href: '/modules/bia', icon: Target },
      { name: 'Risk Management', href: '/modules/risk-management', icon: Shield },
      { name: 'Context Management', href: '/modules/context', icon: Database },
      { name: 'Incident Management', href: '/modules/incidents', icon: AlertTriangle }
    ]
  },
  {
    title: 'Planning & Governance',
    items: [
      { name: 'Plans Management', href: '/modules/plans', icon: FileText },
      { name: 'Governance', href: '/modules/governance', icon: FileCheck },
      { name: 'Templates', href: '/modules/templates', icon: BookOpen },
      { name: 'Audit', href: '/modules/audit', icon: ClipboardList }
    ]
  },
  {
    title: 'Operations',
    items: [
      { name: 'Exercise', href: '/modules/exercise', icon: Activity },
      { name: 'Training', href: '/modules/training', icon: GraduationCap },
      { name: 'Clients', href: '/modules/clients', icon: Users },
      { name: 'KPI Management', href: '/modules/kpi', icon: TrendingUp }
    ]
  },
  {
    title: 'AI & Automation',
    items: [
      { name: 'AI Control', href: '/modules/ai-control', icon: Brain },
      { name: 'AI Consultant', href: '/modules/ai-consultant', icon: Bot },
      { name: 'BCM Core', href: '/modules/bcm-core', icon: Database }
    ]
  },
  {
    title: 'Administration',
    items: [
      { name: 'Reporting', href: '/modules/reporting', icon: BarChart3 },
      { name: 'Configuration', href: '/modules/config', icon: Settings },
      { name: 'Portal', href: '/modules/portal', icon: Globe },
      { name: 'User Management', href: '/modules/users', icon: UserCheck }
    ]
  }
]

// Combined navigation for dual-mode support
export const dualNavigation = {
  sections: sectionNavigation,
  modules: moduleNavigation,

  // Helper to find section by module
  getSectionForModule: (moduleHref: string): string | null => {
    const mapping: Record<string, string> = {
      '/modules/bia': '/sections/risk-assessment',
      '/modules/risk-management': '/sections/risk-assessment',
      '/modules/context': '/sections/risk-assessment',
      '/modules/incidents': '/sections/incident-management',
      '/modules/exercise': '/sections/incident-management',
      '/modules/plans': '/sections/strategy-planning',
      '/modules/governance': '/sections/strategy-planning',
      '/modules/templates': '/sections/strategy-planning',
      '/modules/training': '/sections/learning-community',
      '/modules/clients': '/sections/client-management',
      '/modules/portal': '/sections/client-management',
      '/modules/ai-control': '/sections/ai-automation',
      '/modules/ai-consultant': '/sections/ai-automation',
      '/modules/reporting': '/sections/analytics',
      '/modules/kpi': '/sections/analytics',
      '/modules/audit': '/sections/analytics',
      '/modules/config': '/sections/admin',
      '/modules/users': '/sections/admin'
    }
    return mapping[moduleHref] || null
  },

  // Helper to find modules for section
  getModulesForSection: (sectionHref: string): string[] => {
    const mapping: Record<string, string[]> = {
      '/sections/risk-assessment': ['/modules/bia', '/modules/risk-management', '/modules/context'],
      '/sections/incident-management': ['/modules/incidents', '/modules/exercise'],
      '/sections/strategy-planning': ['/modules/plans', '/modules/governance', '/modules/templates'],
      '/sections/learning-community': ['/modules/training'],
      '/sections/client-management': ['/modules/clients', '/modules/portal'],
      '/sections/ai-automation': ['/modules/ai-control', '/modules/ai-consultant'],
      '/sections/analytics': ['/modules/reporting', '/modules/kpi', '/modules/audit'],
      '/sections/admin': ['/modules/config', '/modules/users']
    }
    return mapping[sectionHref] || []
  }
}

// Quick Actions for different user roles
export const quickActions = {
  admin: [
    { label: 'Create User', icon: UserCheck, action: 'create-user' },
    { label: 'System Settings', icon: Settings, action: 'system-settings' },
    { label: 'View Logs', icon: FileText, action: 'view-logs' }
  ],
  manager: [
    { label: 'New Project', icon: FileText, action: 'new-project' },
    { label: 'Assign Team', icon: Users, action: 'assign-team' },
    { label: 'View Reports', icon: BarChart3, action: 'view-reports' }
  ],
  user: [
    { label: 'My Tasks', icon: ClipboardList, action: 'my-tasks' },
    { label: 'Training', icon: GraduationCap, action: 'training' },
    { label: 'Submit Request', icon: FileText, action: 'submit-request' }
  ]
}

// Export aliases for compatibility
export const SECTIONS_NAVIGATION = sectionNavigation
export const MODULES_NAVIGATION = moduleNavigation

// Navigation mode type
export type NavigationMode = 'sections' | 'modules'

// Helper function to determine navigation mode from path
export function getNavigationMode(pathname: string): NavigationMode {
  if (pathname.startsWith('/modules/')) {
    return 'modules'
  }
  return 'sections'
}