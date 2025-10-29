// ISO 22301:2019 Knowledge Base - Source of Truth
// Библиотека стандарта как основа для всех BCM модулей

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
        complianceLevel: 'none' as const
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
        complianceLevel: 'none' as const
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
        complianceLevel: 'none' as const
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
        complianceLevel: 'none' as const
      }
    ]
  },

  SUPPORT: {
    id: '7',
    title: 'Support',
    requirements: [
      {
        id: '7.1',
        clause: '7.1',
        title: 'Resources',
        description: 'The organization shall determine and provide the resources needed for the establishment, implementation, maintenance and continual improvement of the BCMS.',
        type: 'mandatory' as const,
        category: 'Support',
        evidence: [
          'Resource allocation documentation',
          'Budget approvals',
          'Staff assignments'
        ],
        controls: ['RES-001', 'RES-002'],
        relatedClauses: ['5.1', '7.2'],
        riskLevel: 'high' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '7.2',
        clause: '7.2',
        title: 'Competence',
        description: 'The organization shall determine the necessary competence of person(s) doing work under its control that affects the performance of the BCMS.',
        type: 'mandatory' as const,
        category: 'Support',
        evidence: [
          'Competency requirements',
          'Training records',
          'Competency evaluations'
        ],
        controls: ['COM-001', 'COM-002'],
        relatedClauses: ['7.1', '7.3'],
        riskLevel: 'medium' as const,
        complianceLevel: 'none' as const
      }
    ]
  }
} as const

// Основные процессы BCM согласно ISO 22301
export const BCM_PROCESSES: Record<string, ISO22301Process> = {
  CONTEXT_ESTABLISHMENT: {
    id: 'PROC-001',
    name: 'Context Establishment',
    description: 'Process to understand organizational context and stakeholder requirements',
    inputs: ['Business environment data', 'Stakeholder feedback', 'Regulatory requirements'],
    outputs: ['Context analysis', 'Stakeholder register', 'Requirements documentation'],
    controls: ['CTX-001', 'CTX-002', 'CTX-003'],
    responsibilities: ['BC Manager', 'Senior Management', 'Department Heads'],
    kpis: ['Context review frequency', 'Stakeholder engagement rate', 'Requirements coverage'],
    relatedRequirements: ['4.1', '4.2']
  },

  RISK_ASSESSMENT: {
    id: 'PROC-002', 
    name: 'Business Continuity Risk Assessment',
    description: 'Process to identify, analyze and evaluate BC risks',
    inputs: ['Context analysis', 'Asset register', 'Threat intelligence'],
    outputs: ['Risk register', 'Risk assessment report', 'Risk treatment plan'],
    controls: ['RSK-001', 'RSK-002', 'RSK-003'],
    responsibilities: ['Risk Manager', 'BC Manager', 'Department Representatives'],
    kpis: ['Risk assessment coverage', 'Risk treatment effectiveness', 'Residual risk levels'],
    relatedRequirements: ['6.1', '8.1']
  },

  BIA_PROCESS: {
    id: 'PROC-003',
    name: 'Business Impact Analysis',
    description: 'Process to analyze business activities and determine impact priorities',
    inputs: ['Business process documentation', 'Dependency mapping', 'Financial data'],
    outputs: ['BIA report', 'Recovery time objectives', 'Recovery point objectives'],
    controls: ['BIA-001', 'BIA-002', 'BIA-003'],
    responsibilities: ['BIA Analyst', 'Process Owners', 'Finance Team'],
    kpis: ['BIA coverage', 'RTO accuracy', 'Critical process identification'],
    relatedRequirements: ['8.1', '8.2']
  }
}

// Контроли безопасности для BCM
export const BCM_CONTROLS: Record<string, ISO22301Control> = {
  'CTX-001': {
    id: 'CTX-001',
    name: 'Organizational Context Assessment',
    description: 'Regular assessment of internal and external factors affecting BC',
    type: 'detective',
    category: 'Context Management',
    implementation: 'manual',
    effectiveness: 75,
    maturity: 3
  },

  'RSK-001': {
    id: 'RSK-001',
    name: 'BC Risk Identification',
    description: 'Systematic identification of business continuity risks',
    type: 'detective',
    category: 'Risk Management',
    implementation: 'hybrid',
    effectiveness: 85,
    maturity: 4
  },

  'BIA-001': {
    id: 'BIA-001',
    name: 'Business Impact Analysis',
    description: 'Analysis of potential impacts from disruptions',
    type: 'detective',
    category: 'Impact Assessment',
    implementation: 'manual',
    effectiveness: 90,
    maturity: 4
  },

  'POL-001': {
    id: 'POL-001',
    name: 'BC Policy Management',
    description: 'Establishment and maintenance of BC policy',
    type: 'preventive',
    category: 'Governance',
    implementation: 'manual',
    effectiveness: 80,
    maturity: 3
  }
}

// Матрица соответствия модулей требованиям стандарта
export const MODULE_COMPLIANCE_MATRIX = {
  bcm_context: ['4.1', '4.2', '4.3', '4.4'],
  bcm_governance: ['5.1', '5.2', '5.3'],
  bcm_risk_management: ['6.1', '8.1.1', '8.1.2'],
  bcm_bia: ['8.1.3', '8.1.4'],
  bcm_plans: ['8.2.1', '8.2.2', '8.2.3'],
  bcm_incident_management: ['8.3'],
  bcm_exercise: ['8.4', '8.5'],
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

  static getControlById(id: string): ISO22301Control | undefined {
    return BCM_CONTROLS[id]
  }

  static getProcessById(id: string): ISO22301Process | undefined {
    return Object.values(BCM_PROCESSES).find(proc => proc.id === id)
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