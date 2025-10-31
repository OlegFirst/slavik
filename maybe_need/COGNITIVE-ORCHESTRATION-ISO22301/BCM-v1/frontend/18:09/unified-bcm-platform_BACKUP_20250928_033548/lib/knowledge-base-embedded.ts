// Копируем Knowledge Base прямо в проект для немедленного использования
// Базовая копия iso-22301-standard.ts

export interface ISO22301Requirement {
  id: string
  clause: string
  title: string
  description: string
  type: 'mandatory' | 'recommended' | 'guidance'
  category: string
  subcategory?: string
  evidence: string[]
  controls: string[]
  relatedClauses: string[]
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  complianceLevel: 'none' | 'partial' | 'full'
}

export interface ISO22301Process {
  id: string
  name: string
  description: string
  inputs: string[]
  outputs: string[]
  controls: string[]
  responsibilities: string[]
  kpis: string[]
  relatedRequirements: string[]
}

export interface ISO22301Control {
  id: string
  name: string
  description: string
  type: 'preventive' | 'detective' | 'corrective'
  category: string
  implementation: 'manual' | 'automated' | 'hybrid'
  effectiveness: number // 0-100
  maturity: 1 | 2 | 3 | 4 | 5
}

// Основные разделы стандарта ISO 22301:2019
export const ISO22301_CLAUSES = {
  CONTEXT: {
    id: '4',
    title: 'Context of the organization',
    requirements: [
      {
        id: '4.1',
        clause: '4.1',
        title: 'Understanding the organization and its context',
        description: 'The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its business continuity management system.',
        type: 'mandatory' as const,
        category: 'Context',
        evidence: [
          'Context analysis documentation',
          'Stakeholder register',
          'Business environment assessment'
        ],
        controls: ['CTX-001', 'CTX-002'],
        relatedClauses: ['4.2', '6.1'],
        riskLevel: 'high' as const,
        complianceLevel: 'partial' as const
      },
      {
        id: '4.2',
        clause: '4.2',
        title: 'Understanding the needs and expectations of interested parties',
        description: 'The organization shall determine the interested parties that are relevant to the business continuity management system and the relevant requirements of these interested parties.',
        type: 'mandatory' as const,
        category: 'Context',
        evidence: [
          'Stakeholder analysis',
          'Requirements documentation',
          'Communication records'
        ],
        controls: ['CTX-003', 'CTX-004'],
        relatedClauses: ['4.1', '4.3'],
        riskLevel: 'medium' as const,
        complianceLevel: 'partial' as const
      }
    ]
  },
  
  LEADERSHIP: {
    id: '5',
    title: 'Leadership',
    requirements: [
      {
        id: '5.1',
        clause: '5.1',
        title: 'Leadership and commitment',
        description: 'Top management shall demonstrate leadership and commitment with respect to the business continuity management system.',
        type: 'mandatory' as const,
        category: 'Leadership',
        evidence: [
          'Management commitment statements',
          'Resource allocation records',
          'Policy approval documentation'
        ],
        controls: ['LDR-001', 'LDR-002'],
        relatedClauses: ['5.2', '5.3'],
        riskLevel: 'critical' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '5.2',
        clause: '5.2',
        title: 'Policy',
        description: 'Top management shall establish, implement and maintain a business continuity policy.',
        type: 'mandatory' as const,
        category: 'Leadership',
        evidence: [
          'Business continuity policy',
          'Policy communication records',
          'Policy review documentation'
        ],
        controls: ['POL-001', 'POL-002'],
        relatedClauses: ['5.1', '6.2'],
        riskLevel: 'high' as const,
        complianceLevel: 'none' as const
      }
    ]
  },

  PLANNING: {
    id: '6',
    title: 'Planning',
    requirements: [
      {
        id: '6.1',
        clause: '6.1',
        title: 'Actions to address risks and opportunities',
        description: 'When planning for the business continuity management system, the organization shall consider the issues and requirements and determine the risks and opportunities.',
        type: 'mandatory' as const,
        category: 'Planning',
        evidence: [
          'Risk assessment documentation',
          'Opportunity analysis',
          'Risk treatment plans'
        ],
        controls: ['RSK-001', 'RSK-002', 'RSK-003'],
        relatedClauses: ['4.1', '8.1'],
        riskLevel: 'critical' as const,
        complianceLevel: 'full' as const
      },
      {
        id: '6.2',
        clause: '6.2',
        title: 'Business continuity objectives and planning to achieve them',
        description: 'The organization shall establish business continuity objectives at relevant functions and levels.',
        type: 'mandatory' as const,
        category: 'Planning',
        evidence: [
          'BC objectives documentation',
          'Objective measurement criteria',
          'Achievement plans'
        ],
        controls: ['OBJ-001', 'OBJ-002'],
        relatedClauses: ['5.2', '9.3'],
        riskLevel: 'high' as const,
        complianceLevel: 'partial' as const
      }
    ]
  },

  OPERATION: {
    id: '8',
    title: 'Operation',
    requirements: [
      {
        id: '8.1.3',
        clause: '8.1.3',
        title: 'Business impact analysis',
        description: 'The organization shall establish and maintain a methodology for conducting business impact analysis.',
        type: 'mandatory' as const,
        category: 'Operation',
        evidence: [
          'BIA methodology',
          'Impact analysis reports',
          'Recovery requirements'
        ],
        controls: ['BIA-001', 'BIA-002'],
        relatedClauses: ['8.1.2', '8.2'],
        riskLevel: 'critical' as const,
        complianceLevel: 'full' as const
      }
    ]
  }
} as const

// Матрица соответствия модулей требованиям стандарта
export const MODULE_COMPLIANCE_MATRIX = {
  bcm_context: ['4.1', '4.2'],
  bcm_governance: ['5.1', '5.2'],
  bcm_risk_management: ['6.1'],
  bcm_bia: ['8.1.3'],
  bcm_plans: ['8.2.1', '8.2.2'],
  bcm_incident_management: ['8.3'],
  bcm_exercise: ['8.4'],
  bcm_audit: ['9.2'],
  bcm_review: ['9.3'],
  bcm_improvement: ['10.1', '10.2']
} as const

// Утилиты для работы с Knowledge Base
export class ISO22301KnowledgeBase {
  
  static getRequirementById(id: string): ISO22301Requirement | undefined {
    for (const section of Object.values(ISO22301_CLAUSES)) {
      const requirement = section.requirements.find(req => req.id === id)
      if (requirement) return requirement
    }
    return undefined
  }

  static getRequirementsByModule(moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX): ISO22301Requirement[] {
    const clauseIds = MODULE_COMPLIANCE_MATRIX[moduleName] || []
    return clauseIds
      .map(id => this.getRequirementById(id))
      .filter((req): req is ISO22301Requirement => req !== undefined)
  }

  static getComplianceGaps(): { requirement: ISO22301Requirement, gap: string }[] {
    const gaps: { requirement: ISO22301Requirement, gap: string }[] = []
    
    for (const section of Object.values(ISO22301_CLAUSES)) {
      for (const requirement of section.requirements) {
        if (requirement.complianceLevel === 'none') {
          gaps.push({
            requirement,
            gap: 'Not implemented'
          })
        } else if (requirement.complianceLevel === 'partial') {
          gaps.push({
            requirement,
            gap: 'Partially implemented'
          })
        }
      }
    }
    
    return gaps
  }

  static getImplementationRoadmap(): { phase: string, requirements: ISO22301Requirement[] }[] {
    const phases = [
      {
        phase: 'Foundation (Phase 1)',
        requirements: this.getRequirementsByModule('bcm_context')
          .concat(this.getRequirementsByModule('bcm_governance'))
      },
      {
        phase: 'Assessment (Phase 2)', 
        requirements: this.getRequirementsByModule('bcm_risk_management')
          .concat(this.getRequirementsByModule('bcm_bia'))
      },
      {
        phase: 'Response (Phase 3)',
        requirements: this.getRequirementsByModule('bcm_plans')
          .concat(this.getRequirementsByModule('bcm_incident_management'))
      },
      {
        phase: 'Validation (Phase 4)',
        requirements: this.getRequirementsByModule('bcm_exercise')
          .concat(this.getRequirementsByModule('bcm_audit'))
      }
    ]
    
    return phases
  }

  static validateModuleCompliance(moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX): {
    compliant: boolean
    coverage: number
    missingRequirements: string[]
  } {
    const requirements = this.getRequirementsByModule(moduleName)
    const totalRequirements = requirements.length
    const implementedRequirements = requirements.filter(req => req.complianceLevel === 'full').length
    
    const coverage = totalRequirements > 0 ? (implementedRequirements / totalRequirements) * 100 : 0
    const compliant = coverage >= 80 // 80% threshold for compliance
    
    const missingRequirements = requirements
      .filter(req => req.complianceLevel !== 'full')
      .map(req => req.id)
    
    return {
      compliant,
      coverage,
      missingRequirements
    }
  }
}

// Поисковый движок для требований
export class RequirementSearchEngine {
  
  static getAllRequirements(): ISO22301Requirement[] {
    const allRequirements: ISO22301Requirement[] = []
    
    for (const section of Object.values(ISO22301_CLAUSES)) {
      allRequirements.push(...section.requirements)
    }
    
    return allRequirements
  }

  static searchByRiskLevel(riskLevel: 'low' | 'medium' | 'high' | 'critical'): ISO22301Requirement[] {
    const allRequirements = this.getAllRequirements()
    return allRequirements.filter(req => req.riskLevel === riskLevel)
  }

  static searchByCategory(category: string): ISO22301Requirement[] {
    const allRequirements = this.getAllRequirements()
    return allRequirements.filter(req => req.category === category)
  }
}

// Генератор отчетов
export class ComplianceReportGenerator {
  
  static generateFullComplianceReport(): {
    overallCompliance: number
    criticalGaps: ISO22301Requirement[]
    roadmapProgress: any[]
    moduleReports: any[]
  } {
    const allRequirements = RequirementSearchEngine.getAllRequirements()
    const implementedRequirements = allRequirements.filter(req => req.complianceLevel === 'full')
    const overallCompliance = allRequirements.length > 0 ? 
      (implementedRequirements.length / allRequirements.length) * 100 : 0

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
      criticalGaps,
      roadmapProgress,
      moduleReports: []
    }
  }
}

// React hooks для интеграции
export function useModuleRequirements(moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX) {
  return {
    requirements: ISO22301KnowledgeBase.getRequirementsByModule(moduleName),
    loading: false
  }
}

export function useComplianceAnalysis(moduleName: keyof typeof MODULE_COMPLIANCE_MATRIX) {
  return ISO22301KnowledgeBase.validateModuleCompliance(moduleName)
}

export function useComplianceGaps() {
  return ISO22301KnowledgeBase.getComplianceGaps()
}

export function useImplementationRoadmap() {
  return ISO22301KnowledgeBase.getImplementationRoadmap()
}
