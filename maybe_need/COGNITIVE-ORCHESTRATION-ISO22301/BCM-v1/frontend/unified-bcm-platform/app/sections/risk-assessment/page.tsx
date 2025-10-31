'use client'

import { SectionLayout } from '@/components/sections/SectionLayout'
import { BIAModule } from '@/components/modules/BIAModule'
import { RiskManagement } from '@/components/modules/RiskManagement'
import { ContextManagement } from '@/components/modules/ContextManagement'
import { AIRiskAnalysis } from '@/components/sections/AIRiskAnalysis'
import { getRelatedModulesForSection } from '@/components/sections/RelatedModules'
import { getQuickActionsForSection } from '@/components/sections/QuickActions'
import {
  Target,
  Shield,
  Building,
  Brain
} from 'lucide-react'

export default function RiskAssessmentSection() {
  const relatedModules = getRelatedModulesForSection('risk-assessment')
  const quickActions = getQuickActionsForSection('risk-assessment')

  const tabs = [
    {
      id: 'bia',
      label: 'Business Impact Analysis',
      icon: Target,
      component: <BIAModule />
    },
    {
      id: 'risk',
      label: 'Risk Management',
      icon: Shield,
      component: <RiskManagement />
    },
    {
      id: 'context',
      label: 'Context & Dependencies',
      icon: Building,
      component: <ContextManagement />
    },
    {
      id: 'ai-analysis',
      label: 'AI Risk Insights',
      icon: Brain,
      component: <AIRiskAnalysis />
    }
  ]

  return (
    <SectionLayout
      title="Risk & Impact Assessment"
      description="Comprehensive risk analysis, business impact assessment, and AI-powered insights for informed decision-making"
      tabs={tabs}
      defaultTab="bia"
      relatedModules={relatedModules}
      quickActions={quickActions}
    />
  )
}