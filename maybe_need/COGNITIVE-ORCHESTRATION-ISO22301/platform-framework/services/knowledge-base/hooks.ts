// React hooks для интеграции Knowledge Base с компонентами
import { useState, useEffect, useMemo } from 'react'
import { 
  ISO22301KnowledgeBase, 
  ISO22301Requirement, 
  MODULE_COMPLIANCE_MATRIX 
} from './iso-22301-standard'

// Hook для получения требований по модулю
export function useModuleRequirements(moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX) {
  const [requirements, setRequirements] = useState<ISO22301Requirement[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const moduleRequirements = ISO22301KnowledgeBase.getRequirementsByModule(moduleName)
    setRequirements(moduleRequirements)
    setLoading(false)
  }, [moduleName])

  return { requirements, loading }
}

// Hook для анализа соответствия модуля
export function useComplianceAnalysis(moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX) {
  const analysis = useMemo(() => {
    return ISO22301KnowledgeBase.validateModuleCompliance(moduleName)
  }, [moduleName])

  return analysis
}

// Hook для получения пробелов в соответствии
export function useComplianceGaps() {
  const [gaps, setGaps] = useState<{ requirement: ISO22301Requirement, gap: string }[]>([])

  useEffect(() => {
    const complianceGaps = ISO22301KnowledgeBase.getComplianceGaps()
    setGaps(complianceGaps)
  }, [])

  return gaps
}

// Hook для дорожной карты внедрения
export function useImplementationRoadmap() {
  const [roadmap, setRoadmap] = useState<{ phase: string, requirements: ISO22301Requirement[] }[]>([])

  useEffect(() => {
    const implementationRoadmap = ISO22301KnowledgeBase.getImplementationRoadmap()
    setRoadmap(implementationRoadmap)
  }, [])

  return roadmap
}

// Hook для фильтрации требований
export function useFilteredRequirements(
  requirements: ISO22301Requirement[],
  filters: {
    type?: string
    riskLevel?: string
    complianceLevel?: string
    category?: string
  }
) {
  const filteredRequirements = useMemo(() => {
    return requirements.filter(req => {
      if (filters.type && req.type !== filters.type) return false
      if (filters.riskLevel && req.riskLevel !== filters.riskLevel) return false
      if (filters.complianceLevel && req.complianceLevel !== filters.complianceLevel) return false
      if (filters.category && req.category !== filters.category) return false
      return true
    })
  }, [requirements, filters])

  return filteredRequirements
}
