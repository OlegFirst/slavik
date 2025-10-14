import { SectionLayout } from '@/components/sections/SectionLayout'
import { AnalyticsOverview } from '@/components/sections/analytics/AnalyticsOverview'
import { ExecutiveDashboard } from '@/components/sections/analytics/ExecutiveDashboard'
import { CustomReportBuilder } from '@/components/sections/analytics/CustomReportBuilder'
import { KPIMonitoring } from '@/components/sections/analytics/KPIMonitoring'
import { getRelatedModulesForSection } from '@/components/sections/RelatedModules'
import { getQuickActionsForSection } from '@/components/sections/QuickActions'
import { Metadata } from 'next'
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  FileText 
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Analytics & Intelligence - BCM Platform',
  description: 'Comprehensive business continuity analytics, KPI monitoring, and intelligent reporting dashboard',
}

export default function AnalyticsSection() {
  const relatedModules = getRelatedModulesForSection('analytics')
  const quickActions = getQuickActionsForSection('analytics')

  const tabs = [
    {
      id: 'overview',
      label: 'Analytics Overview',
      icon: BarChart3,
      component: <AnalyticsOverview />
    },
    {
      id: 'executive',
      label: 'Executive Dashboard',
      icon: TrendingUp,
      component: <ExecutiveDashboard />
    },
    {
      id: 'kpi',
      label: 'KPI Monitoring',
      icon: PieChart,
      component: <KPIMonitoring />
    },
    {
      id: 'reports',
      label: 'Custom Reports',
      icon: FileText,
      component: <CustomReportBuilder />
    }
  ]

  return (
    <SectionLayout
      title="Analytics & Intelligence"
      description="Comprehensive BCM analytics with real-time KPIs, executive dashboards, and intelligent reporting"
      tabs={tabs}
      defaultTab="overview"
      relatedModules={relatedModules}
      quickActions={quickActions}
    />
  )
}
