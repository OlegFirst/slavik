import { SectionLayout } from '@/components/sections/SectionLayout'
import { ModuleValidatorDashboard } from '@/components/sections/module-validator/ModuleValidatorDashboard'
import { ModulesList } from '@/components/sections/module-validator/ModulesList'
import { DependencyGraph } from '@/components/sections/module-validator/DependencyGraph' 
import { ValidationHistory } from '@/components/sections/module-validator/ValidationHistory'
import { getRelatedModulesForSection } from '@/components/sections/RelatedModules'
import { getQuickActionsForSection } from '@/components/sections/QuickActions'
import { Metadata } from 'next'
import { 
  CheckCircle, 
  List, 
  GitBranch, 
  History 
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Module Validator - BCM Platform',
  description: 'Comprehensive module validation, dependency analysis, and automated fixing tools',
}

export default function ModuleValidatorSection() {
  const relatedModules = getRelatedModulesForSection('module-validator')
  const quickActions = getQuickActionsForSection('module-validator')

  const tabs = [
    {
      id: 'dashboard',
      label: 'Validation Dashboard',
      icon: CheckCircle,
      component: <ModuleValidatorDashboard />
    },
    {
      id: 'modules',
      label: 'Modules List',
      icon: List,
      component: <ModulesList />
    },
    {
      id: 'dependencies',
      label: 'Dependencies Graph',
      icon: GitBranch,
      component: <DependencyGraph />
    },
    {
      id: 'history',
      label: 'Validation History',
      icon: History,
      component: <ValidationHistory />
    }
  ]

  return (
    <SectionLayout
      title="Module Validator"
      description="Comprehensive module validation, dependency analysis, and automated fixing tools for BCM modules"
      tabs={tabs}
      defaultTab="dashboard"
      relatedModules={relatedModules}
      quickActions={quickActions}
    />
  )
}
