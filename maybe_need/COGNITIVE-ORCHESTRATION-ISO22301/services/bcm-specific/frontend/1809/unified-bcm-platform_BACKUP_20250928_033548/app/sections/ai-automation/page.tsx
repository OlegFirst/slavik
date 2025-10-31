import { SectionLayout } from '@/components/sections/SectionLayout'
import { AIControlCenterModule } from '@/components/modules/AIControlCenter'
import { AutomationWorkflows } from '@/components/sections/AutomationWorkflows'
import { getRelatedModulesForSection } from '@/components/sections/RelatedModules'
import { getQuickActionsForSection } from '@/components/sections/QuickActions'
import { Metadata } from 'next'
import { 
  Brain, 
  Bot, 
  Workflow, 
  Zap 
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'AI & Automation Command Center - BCM Platform',
  description: 'AI orchestration, intelligent automation, and digital twin management for enhanced BCM operations',
}

export default function AIAutomationSection() {
  const relatedModules = getRelatedModulesForSection('ai-automation')
  const quickActions = getQuickActionsForSection('ai-automation')

  const tabs = [
    {
      id: 'ai-control',
      label: 'AI Control Center', 
      icon: Brain,
      component: <AIControlCenterModule />
    },
    {
      id: 'ai-consultant',
      label: 'AI Consultant',
      icon: Bot,
      component: (
        <div className="p-6 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg border">
          <div className="text-center">
            <Bot className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              AI BCM Consultant
            </h3>
            <p className="text-gray-600 mb-4">
              Your intelligent BCM advisor for strategic guidance and recommendations.
            </p>
            <div className="bg-white rounded-lg p-4 text-sm text-gray-500">
              🤖 AI Consultant integration will be implemented by TEAM 1
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'automation',
      label: 'Automation Workflows',
      icon: Workflow,
      component: <AutomationWorkflows />
    },
    {
      id: 'digital-twin-ai',
      label: 'Digital Twin AI',
      icon: Zap,
      component: (
        <div className="p-6 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg border">
          <div className="text-center">
            <Zap className="h-12 w-12 text-orange-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Digital Twin AI Orchestration
            </h3>
            <p className="text-gray-600 mb-4">
              AI-powered analysis and optimization of your organizational digital twin.
            </p>
            <div className="bg-white rounded-lg p-4 text-sm text-gray-500">
              🔮 Digital Twin AI features will be implemented by TEAM 1
            </div>
          </div>
        </div>
      )
    }
  ]

  return (
    <SectionLayout
      title="AI & Automation Command Center"
      description="Orchestrate AI-powered BCM operations with intelligent automation and digital twin management"
      tabs={tabs}
      defaultTab="ai-control"
      relatedModules={relatedModules}
      quickActions={quickActions}
    />
  )
}