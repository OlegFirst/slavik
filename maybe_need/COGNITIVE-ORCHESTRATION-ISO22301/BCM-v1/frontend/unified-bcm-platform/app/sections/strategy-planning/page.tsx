'use client'

import { SectionLayout } from '@/components/sections/SectionLayout'
import { PlansManagement } from '@/components/modules/PlansManagement'
import { GovernanceModule } from '@/components/modules/GovernanceModule'
import { Templates } from '@/components/modules/Templates'
import { PlanBuilder } from '@/components/sections/PlanBuilder'
import { FileText, Shield, BookOpen, Wrench } from 'lucide-react'

const sectionTabs = [
  {
    id: 'plans',
    label: 'Plans Management',
    icon: FileText,
    component: PlansManagement,
    description: 'Business continuity and recovery plans'
  },
  {
    id: 'governance',
    label: 'Governance',
    icon: Shield,
    component: GovernanceModule,
    description: 'BCM governance framework and policies'
  },
  {
    id: 'templates',
    label: 'Templates',
    icon: BookOpen,
    component: Templates,
    description: 'Document templates and standards'
  },
  {
    id: 'builder',
    label: 'Plan Builder',
    icon: Wrench,
    component: PlanBuilder,
    description: 'Enhanced plan creation and management'
  }
]

const relatedModules = [
  '/modules/plans',
  '/modules/governance',
  '/modules/templates',
  '/modules/audit'
]

export default function StrategyPlanningSection() {
  return (
    <SectionLayout
      title="Strategy & Planning"
      description="Strategic business continuity planning, governance, and policy management"
      tabs={sectionTabs}
      relatedModules={relatedModules}
    />
  )
}