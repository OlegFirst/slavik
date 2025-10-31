// Копируем Knowledge Base в основной проект
export * from '../../../services/knowledge-base/iso-22301-standard'
export * from '../../../services/knowledge-base/complete-requirements'
export * from '../../../services/knowledge-base/utils'
export * from '../../../services/knowledge-base/hooks'
export * from '../../../services/knowledge-base/templates/document-templates'

// Re-export для удобства импорта в компонентах
export { 
  ISO22301KnowledgeBase,
  MODULE_COMPLIANCE_MATRIX,
  ISO22301_CLAUSES,
  BCM_PROCESSES,
  BCM_CONTROLS
} from '../../../services/knowledge-base/iso-22301-standard'

export {
  RequirementSearchEngine,
  ComplianceReportGenerator, 
  DocumentValidator,
  ImplementationPlanner
} from '../../../services/knowledge-base/utils'

export {
  useModuleRequirements,
  useComplianceAnalysis,
  useComplianceGaps,
  useImplementationRoadmap
} from '../../../services/knowledge-base/hooks'

export {
  DOCUMENT_TEMPLATES,
  TemplateGenerator
} from '../../../services/knowledge-base/templates/document-templates'
