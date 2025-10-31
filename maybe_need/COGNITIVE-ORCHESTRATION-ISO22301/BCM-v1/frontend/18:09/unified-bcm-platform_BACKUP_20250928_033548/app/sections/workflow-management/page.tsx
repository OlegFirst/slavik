'use client'

import { SectionLayout } from '@/components/sections/SectionLayout'
import { WorkflowDashboard } from '@/components/sections/workflow/WorkflowDashboard'
import { ProcessManagement } from '@/components/sections/workflow/ProcessManagement'
import { AutomationCenter } from '@/components/sections/workflow/AutomationCenter'
import { BPMNDesigner } from '@/components/sections/workflow/BPMNDesigner'
import { TemplateMarketplace } from '@/components/sections/workflow/templates/TemplateMarketplace'
import {
  Workflow,
  Settings,
  Zap,
  Diagram3,
  Target,
  FileText,
  Users,
  Activity,
  Library
} from 'lucide-react'

const workflowTabs = [
  {
    id: 'dashboard',
    label: 'Workflow Dashboard',
    icon: Activity,
    component: <WorkflowDashboard />
  },
  {
    id: 'bpmn',
    label: 'BPMN Designer',
    icon: Diagram3,
    component: <BPMNDesigner />
  },
  {
    id: 'processes',
    label: 'Process Management',
    icon: Settings,
    component: <ProcessManagement />
  },
  {
    id: 'automation',
    label: 'Automation Center',
    icon: Zap,
    component: <AutomationCenter />
  },
  {
    id: 'templates',
    label: 'Template Library',
    icon: Library,
    component: <TemplateMarketplace />
  }
]

const relatedModules = [
  {
    name: 'BIA Module',
    href: '/modules/bia',
    icon: Target,
    description: 'Business Impact Analysis processes'
  },
  {
    name: 'Plans Management',
    href: '/modules/plans',
    icon: FileText,
    description: 'Business continuity planning workflows'
  },
  {
    name: 'Training',
    href: '/modules/training',
    icon: Users,
    description: 'Training workflow automation'
  }
]

const quickActions = [
  {
    id: 'new-workflow',
    label: 'New Workflow',
    icon: Workflow,
    onClick: () => console.log('Creating new workflow'),
    variant: 'default' as const
  },
  {
    id: 'import-bpmn',
    label: 'Import BPMN',
    icon: Diagram3,
    onClick: () => console.log('Importing BPMN'),
    variant: 'outline' as const
  },
  {
    id: 'automation-rules',
    label: 'Setup Automation',
    icon: Zap,
    onClick: () => console.log('Setting up automation'),
    variant: 'secondary' as const
  }
]

export default function WorkflowManagementPage() {
  return (
    <SectionLayout
      title="Workflow Management"
      description="Design, manage and automate business continuity workflows with BPMN support"
      tabs={workflowTabs}
      defaultTab="dashboard"
      relatedModules={relatedModules}
      quickActions={quickActions}
    />
  )
}