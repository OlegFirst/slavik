// Интегрируем ISO 22301 Knowledge Base в BCM Platform
import { 
  ISO22301KnowledgeBase,
  ISO22301Requirement,
  MODULE_COMPLIANCE_MATRIX 
} from '../../knowledge-base/iso-22301-standard'

import { 
  ComplianceReportGenerator,
  RequirementSearchEngine 
} from '../../knowledge-base/utils'

// Расширяем существующий bcm-store.ts с Knowledge Base
interface ComplianceState {
  overallCompliance: number
  moduleCompliance: Record<string, {
    coverage: number
    compliant: boolean
    missingRequirements: string[]
  }>
  criticalGaps: ISO22301Requirement[]
  roadmapProgress: {
    phase: string
    completion: number
    remainingRequirements: number
  }[]
}

// Добавляем compliance slice в существующий store
export const useComplianceStore = create<ComplianceState>((set, get) => ({
  overallCompliance: 0,
  moduleCompliance: {},
  criticalGaps: [],
  roadmapProgress: [],

  // Методы для работы с соответствием
  updateModuleCompliance: (moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX) => {
    const analysis = ISO22301KnowledgeBase.validateModuleCompliance(moduleName)
    
    set((state) => ({
      moduleCompliance: {
        ...state.moduleCompliance,
        [moduleName]: analysis
      }
    }))
  },

  refreshCompliance: async () => {
    const report = ComplianceReportGenerator.generateFullComplianceReport()
    
    set({
      overallCompliance: report.overallCompliance,
      criticalGaps: report.criticalGaps,
      roadmapProgress: report.roadmapProgress,
      moduleCompliance: report.moduleReports.reduce((acc, moduleReport) => {
        acc[moduleReport.moduleName] = moduleReport.compliance
        return acc
      }, {} as Record<string, any>)
    })
  },

  getCriticalRequirements: () => {
    return RequirementSearchEngine.searchByRiskLevel('critical')
  },

  getModuleRequirements: (moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX) => {
    return ISO22301KnowledgeBase.getRequirementsByModule(moduleName)
  }
}))
