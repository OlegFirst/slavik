// Section-specific components
export { SectionLayout } from './SectionLayout'
export { RelatedModules, getRelatedModulesForSection } from './RelatedModules'
export { QuickActions, getQuickActionsForSection } from './QuickActions'

// Central Hub components
export { CentralHubEnhancements } from './CentralHubEnhancements'

// Section-specific components
export { AIRiskAnalysis } from './AIRiskAnalysis'
export { AutomationWorkflows } from './AutomationWorkflows'
export { CrisisCommunicationHub } from './CrisisCommunicationHub'
export { RecoveryCoordination } from './RecoveryCoordination'
export { PlanBuilder } from './PlanBuilder'
export { PersonalDashboard } from './PersonalDashboard'
export { UserSettings } from './UserSettings'

// Analytics components
export { AnalyticsOverview } from './analytics/AnalyticsOverview'
export { ExecutiveDashboard } from './analytics/ExecutiveDashboard'
export { KPIMonitoring } from './analytics/KPIMonitoring'
export { CustomReportBuilder } from './analytics/CustomReportBuilder'

// Re-export types from navigation config
export type { NavigationItem, NavigationCategory, NavigationMode } from '@/lib/navigation-config'