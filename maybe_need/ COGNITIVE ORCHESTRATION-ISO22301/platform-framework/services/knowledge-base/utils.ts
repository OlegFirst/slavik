// Утилиты для работы с ISO 22301 Knowledge Base

import { 
  ISO22301Requirement, 
  ISO22301Process,
  ISO22301Control,
  ISO22301KnowledgeBase 
} from './iso-22301-standard'

// Интерфейсы для отчетов
export interface ComplianceReport {
  moduleName: string
  totalRequirements: number
  compliance: {
    compliant: boolean
    coverage: number
    missingRequirements: string[]
  }
  breakdown: {
    implemented: number
    partial: number
    notImplemented: number
  }
  implementedRequirements: ISO22301Requirement[]
  partialRequirements: ISO22301Requirement[]
  notImplementedRequirements: ISO22301Requirement[]
  recommendations: string[]
  generatedAt: string
}

export interface FullComplianceReport {
  overallCompliance: number
  moduleReports: ComplianceReport[]
  criticalGaps: ISO22301Requirement[]
  nextPriorityActions: string[]
  roadmapProgress: {
    phase: string
    completion: number
    remainingRequirements: number
  }[]
  generatedAt: string
}

// Утилита для поиска требований
export class RequirementSearchEngine {
  
  static searchByKeyword(keyword: string): ISO22301Requirement[] {
    const allRequirements = this.getAllRequirements()
    return allRequirements.filter(req => 
      req.title.toLowerCase().includes(keyword.toLowerCase()) ||
      req.description.toLowerCase().includes(keyword.toLowerCase()) ||
      req.evidence.some(evidence => evidence.toLowerCase().includes(keyword.toLowerCase()))
    )
  }

  static searchByCategory(category: string): ISO22301Requirement[] {
    const allRequirements = this.getAllRequirements()
    return allRequirements.filter(req => req.category === category)
  }

  static searchByRiskLevel(riskLevel: 'low' | 'medium' | 'high' | 'critical'): ISO22301Requirement[] {
    const allRequirements = this.getAllRequirements()
    return allRequirements.filter(req => req.riskLevel === riskLevel)
  }

  static getAllRequirements(): ISO22301Requirement[] {
    const allRequirements: ISO22301Requirement[] = []
    
    // Импортируем все требования из всех разделов
    const { ISO22301_CLAUSES } = require('./iso-22301-standard')
    
    for (const section of Object.values(ISO22301_CLAUSES)) {
      if (section && typeof section === 'object' && 'requirements' in section) {
        allRequirements.push(...(section as any).requirements as ISO22301Requirement[])
      }
    }
    
    return allRequirements
  }

  static findRelatedRequirements(requirementId: string): ISO22301Requirement[] {
    const requirement = ISO22301KnowledgeBase.getRequirementById(requirementId)
    if (!requirement) return []

    const allRequirements = this.getAllRequirements()
    return allRequirements.filter(req => 
      requirement.relatedClauses.includes(req.id) ||
      req.relatedClauses.includes(requirementId)
    )
  }
}

// Генератор отчетов по соответствию
export class ComplianceReportGenerator {

  static generateModuleReport(moduleName: keyof typeof import('./iso-22301-standard').MODULE_COMPLIANCE_MATRIX): ComplianceReport {
    const analysis = ISO22301KnowledgeBase.validateModuleCompliance(moduleName)
    const requirements = ISO22301KnowledgeBase.getRequirementsByModule(moduleName)
    
    const implemented = requirements.filter(req => req.complianceLevel === 'full')
    const partial = requirements.filter(req => req.complianceLevel === 'partial')
    const notImplemented = requirements.filter(req => req.complianceLevel === 'none')

    return {
      moduleName,
      totalRequirements: requirements.length,
      compliance: analysis,
      breakdown: {
        implemented: implemented.length,
        partial: partial.length,
        notImplemented: notImplemented.length
      },
      implementedRequirements: implemented,
      partialRequirements: partial,
      notImplementedRequirements: notImplemented,
      recommendations: this.generateRecommendations(notImplemented),
      generatedAt: new Date().toISOString()
    }
  }

  static generateFullComplianceReport(): FullComplianceReport {
    const { MODULE_COMPLIANCE_MATRIX } = require('./iso-22301-standard')
    const moduleNames = Object.keys(MODULE_COMPLIANCE_MATRIX) as (keyof typeof MODULE_COMPLIANCE_MATRIX)[]
    
    const moduleReports = moduleNames.map(moduleName => 
      this.generateModuleReport(moduleName)
    )

    const overallCompliance = moduleReports.reduce((sum, report) => 
      sum + report.compliance.coverage, 0
    ) / moduleReports.length

    const criticalGaps = RequirementSearchEngine.searchByRiskLevel('critical')
      .filter(req => req.complianceLevel === 'none')

    const roadmap = ISO22301KnowledgeBase.getImplementationRoadmap()
    const roadmapProgress = roadmap.map(phase => {
      const phaseRequirements = phase.requirements
      const implemented = phaseRequirements.filter(req => req.complianceLevel === 'full').length
      const completion = phaseRequirements.length > 0 ? 
        (implemented / phaseRequirements.length) * 100 : 0

      return {
        phase: phase.phase,
        completion,
        remainingRequirements: phaseRequirements.length - implemented
      }
    })

    return {
      overallCompliance,
      moduleReports,
      criticalGaps,
      nextPriorityActions: this.generatePriorityActions(criticalGaps),
      roadmapProgress,
      generatedAt: new Date().toISOString()
    }
  }

  private static generateRecommendations(notImplemented: ISO22301Requirement[]): string[] {
    const recommendations: string[] = []
    
    // Группируем по категориям
    const byCategory = notImplemented.reduce((acc, req) => {
      if (!acc[req.category]) acc[req.category] = []
      acc[req.category].push(req)
      return acc
    }, {} as Record<string, ISO22301Requirement[]>)

    for (const [category, requirements] of Object.entries(byCategory)) {
      if (requirements.length > 0) {
        recommendations.push(
          `Implement ${category} controls: Focus on ${requirements.length} requirements including ${requirements[0].title}`
        )
      }
    }

    // Приоритизируем критические требования
    const critical = notImplemented.filter(req => req.riskLevel === 'critical')
    if (critical.length > 0) {
      recommendations.unshift(`PRIORITY: Address ${critical.length} critical requirements immediately`)
    }

    return recommendations
  }

  private static generatePriorityActions(criticalGaps: ISO22301Requirement[]): string[] {
    const actions: string[] = []

    if (criticalGaps.length > 0) {
      actions.push(`Address ${criticalGaps.length} critical compliance gaps`)
      
      // Группируем по категориям для более конкретных действий
      const categories = [...new Set(criticalGaps.map(gap => gap.category))]
      categories.forEach(category => {
        const categoryGaps = criticalGaps.filter(gap => gap.category === category)
        actions.push(`Implement ${category} framework (${categoryGaps.length} requirements)`)
      })
    }

    return actions
  }
}

// Валидатор документов на соответствие требованиям
export class DocumentValidator {
  
  static validateDocument(content: string, requirementIds: string[]): DocumentValidationResult {
    const results: RequirementValidation[] = []
    
    for (const reqId of requirementIds) {
      const requirement = ISO22301KnowledgeBase.getRequirementById(reqId)
      if (!requirement) continue

      const validation = this.validateRequirement(content, requirement)
      results.push(validation)
    }

    const coverage = results.filter(r => r.satisfied).length / results.length * 100
    const missingEvidence = results
      .filter(r => !r.satisfied)
      .map(r => r.missingEvidence)
      .flat()

    return {
      coverage,
      validations: results,
      missingEvidence,
      recommendations: this.generateDocumentRecommendations(results)
    }
  }

  private static validateRequirement(content: string, requirement: ISO22301Requirement): RequirementValidation {
    const contentLower = content.toLowerCase()
    const foundEvidence: string[] = []
    const missingEvidence: string[] = []

    // Проверяем наличие ключевых слов из требования
    const keywords = this.extractKeywords(requirement)
    const foundKeywords = keywords.filter(keyword => 
      contentLower.includes(keyword.toLowerCase())
    )

    // Проверяем доказательства
    requirement.evidence.forEach(evidence => {
      if (contentLower.includes(evidence.toLowerCase())) {
        foundEvidence.push(evidence)
      } else {
        missingEvidence.push(evidence)
      }
    })

    const satisfied = foundKeywords.length >= keywords.length * 0.5 && 
                     foundEvidence.length >= requirement.evidence.length * 0.3

    return {
      requirementId: requirement.id,
      requirementTitle: requirement.title,
      satisfied,
      foundEvidence,
      missingEvidence,
      keywordMatch: foundKeywords.length / keywords.length * 100
    }
  }

  private static extractKeywords(requirement: ISO22301Requirement): string[] {
    const keywords: string[] = []
    
    // Извлекаем ключевые слова из названия и описания
    const text = `${requirement.title} ${requirement.description}`.toLowerCase()
    
    // Простой алгоритм извлечения ключевых слов
    const words = text.match(/\b\w{4,}\b/g) || []
    const commonWords = ['shall', 'must', 'should', 'organization', 'management', 'system', 'process']
    
    return [...new Set(words.filter(word => !commonWords.includes(word)))]
  }

  private static generateDocumentRecommendations(validations: RequirementValidation[]): string[] {
    const recommendations: string[] = []
    const unsatisfied = validations.filter(v => !v.satisfied)

    if (unsatisfied.length > 0) {
      recommendations.push(`Document is missing coverage for ${unsatisfied.length} requirements`)
      
      const commonMissing = this.findCommonMissingEvidence(unsatisfied)
      commonMissing.forEach(evidence => {
        recommendations.push(`Add section covering: ${evidence}`)
      })
    }

    return recommendations
  }

  private static findCommonMissingEvidence(validations: RequirementValidation[]): string[] {
    const evidenceCounts: Record<string, number> = {}
    
    validations.forEach(v => {
      v.missingEvidence.forEach(evidence => {
        evidenceCounts[evidence] = (evidenceCounts[evidence] || 0) + 1
      })
    })

    return Object.entries(evidenceCounts)
      .filter(([, count]) => count >= 2)
      .map(([evidence]) => evidence)
      .slice(0, 5) // Топ 5 общих недостающих доказательств
  }
}

// Интерфейсы для валидации документов
export interface DocumentValidationResult {
  coverage: number
  validations: RequirementValidation[]
  missingEvidence: string[]
  recommendations: string[]
}

export interface RequirementValidation {
  requirementId: string
  requirementTitle: string
  satisfied: boolean
  foundEvidence: string[]
  missingEvidence: string[]
  keywordMatch: number
}

// Планировщик внедрения
export class ImplementationPlanner {
  
  static createImplementationPlan(targetDate: Date, availableResources: number = 1): ImplementationPlan {
    const roadmap = ISO22301KnowledgeBase.getImplementationRoadmap()
    const totalRequirements = roadmap.reduce((sum, phase) => sum + phase.requirements.length, 0)
    
    const weeksAvailable = Math.ceil((targetDate.getTime() - Date.now()) / (7 * 24 * 60 * 60 * 1000))
    const requirementsPerWeek = Math.ceil(totalRequirements / weeksAvailable / availableResources)

    const phases: PhasePlan[] = roadmap.map((phase, index) => {
      const estimatedWeeks = Math.ceil(phase.requirements.length / requirementsPerWeek)
      const startDate = new Date()
      startDate.setDate(startDate.getDate() + (index * estimatedWeeks * 7))
      
      const endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + (estimatedWeeks * 7))

      return {
        name: phase.phase,
        requirements: phase.requirements,
        estimatedWeeks,
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        resources: availableResources,
        deliverables: this.generateDeliverables(phase.requirements)
      }
    })

    return {
      targetDate: targetDate.toISOString(),
      totalRequirements,
      estimatedDuration: weeksAvailable,
      phases,
      riskFactors: this.assessRisks(phases),
      generatedAt: new Date().toISOString()
    }
  }

  private static generateDeliverables(requirements: ISO22301Requirement[]): string[] {
    const deliverables = new Set<string>()
    
    requirements.forEach(req => {
      req.evidence.forEach(evidence => {
        deliverables.add(evidence)
      })
    })

    return Array.from(deliverables).slice(0, 10) // Топ 10 ключевых результатов
  }

  private static assessRisks(phases: PhasePlan[]): string[] {
    const risks: string[] = []

    // Проверяем перегрузку фаз
    phases.forEach(phase => {
      if (phase.requirements.length > 10) {
        risks.push(`Phase "${phase.name}" has ${phase.requirements.length} requirements - consider splitting`)
      }
      
      if (phase.estimatedWeeks < 2) {
        risks.push(`Phase "${phase.name}" timeline may be too aggressive (${phase.estimatedWeeks} weeks)`)
      }
    })

    // Проверяем критические требования
    const criticalRequirements = phases
      .flatMap(p => p.requirements)
      .filter(req => req.riskLevel === 'critical')
    
    if (criticalRequirements.length > 5) {
      risks.push(`${criticalRequirements.length} critical requirements may require additional resources`)
    }

    return risks
  }
}

// Интерфейсы для планирования
export interface ImplementationPlan {
  targetDate: string
  totalRequirements: number
  estimatedDuration: number
  phases: PhasePlan[]
  riskFactors: string[]
  generatedAt: string
}

export interface PhasePlan {
  name: string
  requirements: ISO22301Requirement[]
  estimatedWeeks: number
  startDate: string
  endDate: string
  resources: number
  deliverables: string[]
}

// Экспорт всех утилит
export {
  RequirementSearchEngine,
  ComplianceReportGenerator,
  DocumentValidator,
  ImplementationPlanner
}
