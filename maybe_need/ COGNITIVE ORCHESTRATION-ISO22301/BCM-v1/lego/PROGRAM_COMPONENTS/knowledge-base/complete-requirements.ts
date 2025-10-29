// Полный набор требований ISO 22301:2019
// Расширенная версия с детальными требованиями всех разделов

import { ISO22301_CLAUSES } from './iso-22301-standard'

// Дополняем базовую структуру полным набором требований
export const COMPLETE_ISO22301_REQUIREMENTS = {
  ...ISO22301_CLAUSES,
  
  // Раздел 4.3 - Determining the scope of the BCMS
  SCOPE: {
    id: '4.3',
    title: 'Determining the scope of the business continuity management system',
    requirements: [
      {
        id: '4.3',
        clause: '4.3',
        title: 'Determining the scope of the business continuity management system',
        description: 'The organization shall determine the boundaries and applicability of the business continuity management system to establish its scope.',
        type: 'mandatory' as const,
        category: 'Scope',
        evidence: [
          'BCMS scope document',
          'Boundary definitions',
          'Applicability statements'
        ],
        controls: ['SCP-001', 'SCP-002'],
        relatedClauses: ['4.1', '4.2', '8.1'],
        riskLevel: 'high' as const,
        complianceLevel: 'none' as const
      }
    ]
  },

  // Раздел 8 - Operation (полный)
  OPERATION: {
    id: '8',
    title: 'Operation',
    requirements: [
      {
        id: '8.1',
        clause: '8.1',
        title: 'Operational planning and control',
        description: 'The organization shall plan, implement and control the processes needed to meet requirements and to implement the actions determined in 6.1.',
        type: 'mandatory' as const,
        category: 'Operation',
        evidence: [
          'Operational procedures',
          'Process documentation',
          'Control mechanisms'
        ],
        controls: ['OPR-001', 'OPR-002'],
        relatedClauses: ['6.1', '8.2'],
        riskLevel: 'critical' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '8.1.1',
        clause: '8.1.1',
        title: 'General',
        description: 'The organization shall establish criteria for the processes and shall control these processes in accordance with the criteria.',
        type: 'mandatory' as const,
        category: 'Operation',
        evidence: [
          'Process criteria',
          'Control measures',
          'Performance indicators'
        ],
        controls: ['OPR-003'],
        relatedClauses: ['8.1', '8.1.2'],
        riskLevel: 'high' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '8.1.2',
        clause: '8.1.2',
        title: 'Business impact analysis and risk assessment',
        description: 'The organization shall conduct and maintain business impact analysis and risk assessment.',
        type: 'mandatory' as const,
        category: 'Assessment',
        subcategory: 'BIA and Risk',
        evidence: [
          'BIA documentation',
          'Risk assessment reports',
          'Impact analysis'
        ],
        controls: ['BIA-001', 'RSK-001'],
        relatedClauses: ['6.1', '8.2'],
        riskLevel: 'critical' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '8.2',
        clause: '8.2',
        title: 'Business continuity strategy and solutions',
        description: 'The organization shall determine and select business continuity strategies and solutions.',
        type: 'mandatory' as const,
        category: 'Strategy',
        evidence: [
          'BC strategy documentation',
          'Solution alternatives',
          'Strategy justification'
        ],
        controls: ['STR-001', 'STR-002'],
        relatedClauses: ['8.1.2', '8.3'],
        riskLevel: 'critical' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '8.3',
        clause: '8.3',
        title: 'Business continuity procedures',
        description: 'The organization shall establish and maintain business continuity procedures.',
        type: 'mandatory' as const,
        category: 'Procedures',
        evidence: [
          'BC procedures',
          'Response protocols',
          'Recovery procedures'
        ],
        controls: ['PRC-001', 'PRC-002'],
        relatedClauses: ['8.2', '8.4'],
        riskLevel: 'critical' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '8.4',
        clause: '8.4',
        title: 'Business continuity exercises',
        description: 'The organization shall conduct business continuity exercises.',
        type: 'mandatory' as const,
        category: 'Exercises',
        evidence: [
          'Exercise plans',
          'Exercise reports',
          'Lessons learned'
        ],
        controls: ['EXR-001', 'EXR-002'],
        relatedClauses: ['8.3', '8.5'],
        riskLevel: 'high' as const,
        complianceLevel: 'none' as const
      }
    ]
  },

  // Раздел 9 - Performance evaluation (полный)
  EVALUATION: {
    id: '9',
    title: 'Performance evaluation',
    requirements: [
      {
        id: '9.1',
        clause: '9.1',
        title: 'Monitoring, measurement, analysis and evaluation',
        description: 'The organization shall determine what needs to be monitored and measured, the methods for monitoring, measurement, analysis and evaluation.',
        type: 'mandatory' as const,
        category: 'Monitoring',
        evidence: [
          'Monitoring procedures',
          'Measurement criteria',
          'Analysis reports'
        ],
        controls: ['MON-001', 'MON-002'],
        relatedClauses: ['6.2', '9.2'],
        riskLevel: 'medium' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '9.2',
        clause: '9.2',
        title: 'Internal audit',
        description: 'The organization shall conduct internal audits at planned intervals.',
        type: 'mandatory' as const,
        category: 'Audit',
        evidence: [
          'Audit programs',
          'Audit reports',
          'Corrective actions'
        ],
        controls: ['AUD-001', 'AUD-002'],
        relatedClauses: ['9.1', '9.3'],
        riskLevel: 'medium' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '9.3',
        clause: '9.3',
        title: 'Management review',
        description: 'Top management shall review the organizations business continuity management system at planned intervals.',
        type: 'mandatory' as const,
        category: 'Review',
        evidence: [
          'Management review agendas',
          'Review meeting minutes',
          'Management decisions'
        ],
        controls: ['REV-001', 'REV-002'],
        relatedClauses: ['9.2', '10.1'],
        riskLevel: 'high' as const,
        complianceLevel: 'none' as const
      }
    ]
  },

  // Раздел 10 - Improvement (полный)
  IMPROVEMENT: {
    id: '10',
    title: 'Improvement',
    requirements: [
      {
        id: '10.1',
        clause: '10.1',
        title: 'Nonconformity and corrective action',
        description: 'When a nonconformity occurs, the organization shall react to the nonconformity and take action to control and correct it.',
        type: 'mandatory' as const,
        category: 'Corrective Action',
        evidence: [
          'Nonconformity records',
          'Corrective action plans',
          'Effectiveness reviews'
        ],
        controls: ['COR-001', 'COR-002'],
        relatedClauses: ['9.3', '10.2'],
        riskLevel: 'medium' as const,
        complianceLevel: 'none' as const
      },
      {
        id: '10.2',
        clause: '10.2',
        title: 'Continual improvement',
        description: 'The organization shall continually improve the suitability, adequacy and effectiveness of the business continuity management system.',
        type: 'mandatory' as const,
        category: 'Improvement',
        evidence: [
          'Improvement plans',
          'Performance trends',
          'Innovation records'
        ],
        controls: ['IMP-001', 'IMP-002'],
        relatedClauses: ['10.1', '6.2'],
        riskLevel: 'medium' as const,
        complianceLevel: 'none' as const
      }
    ]
  }
}

// Детальные контроли для всех процессов
export const EXTENDED_BCM_CONTROLS = {
  // Context Controls
  'CTX-001': {
    id: 'CTX-001',
    name: 'Organizational Context Assessment',
    description: 'Regular assessment of internal and external factors affecting BC',
    type: 'detective' as const,
    category: 'Context Management',
    implementation: 'manual' as const,
    effectiveness: 75,
    maturity: 3
  },
  'CTX-002': {
    id: 'CTX-002',
    name: 'Environmental Monitoring',
    description: 'Continuous monitoring of business environment changes',
    type: 'detective' as const,
    category: 'Context Management',
    implementation: 'hybrid' as const,
    effectiveness: 80,
    maturity: 3
  },

  // Governance Controls
  'GOV-001': {
    id: 'GOV-001',
    name: 'BCMS Governance Framework',
    description: 'Establishment of governance structure for BCMS',
    type: 'preventive' as const,
    category: 'Governance',
    implementation: 'manual' as const,
    effectiveness: 85,
    maturity: 4
  },
  'POL-001': {
    id: 'POL-001',
    name: 'BC Policy Management',
    description: 'Establishment and maintenance of BC policy',
    type: 'preventive' as const,
    category: 'Governance',
    implementation: 'manual' as const,
    effectiveness: 80,
    maturity: 3
  },

  // Risk Management Controls
  'RSK-001': {
    id: 'RSK-001',
    name: 'BC Risk Identification',
    description: 'Systematic identification of business continuity risks',
    type: 'detective' as const,
    category: 'Risk Management',
    implementation: 'hybrid' as const,
    effectiveness: 85,
    maturity: 4
  },
  'RSK-002': {
    id: 'RSK-002',
    name: 'Risk Analysis and Evaluation',
    description: 'Analysis and evaluation of identified BC risks',
    type: 'detective' as const,
    category: 'Risk Management',
    implementation: 'manual' as const,
    effectiveness: 80,
    maturity: 3
  },

  // BIA Controls
  'BIA-001': {
    id: 'BIA-001',
    name: 'Business Impact Analysis',
    description: 'Analysis of potential impacts from disruptions',
    type: 'detective' as const,
    category: 'Impact Assessment',
    implementation: 'manual' as const,
    effectiveness: 90,
    maturity: 4
  },
  'BIA-002': {
    id: 'BIA-002',
    name: 'Dependency Analysis',
    description: 'Analysis of business process dependencies',
    type: 'detective' as const,
    category: 'Impact Assessment',
    implementation: 'manual' as const,
    effectiveness: 85,
    maturity: 3
  },

  // Exercise Controls
  'EXR-001': {
    id: 'EXR-001',
    name: 'Exercise Planning',
    description: 'Planning and scheduling of BC exercises',
    type: 'preventive' as const,
    category: 'Testing',
    implementation: 'manual' as const,
    effectiveness: 70,
    maturity: 3
  },
  'EXR-002': {
    id: 'EXR-002',
    name: 'Exercise Execution',
    description: 'Execution and evaluation of BC exercises',
    type: 'detective' as const,
    category: 'Testing',
    implementation: 'manual' as const,
    effectiveness: 75,
    maturity: 3
  }
}

// Шаблоны документации по ISO 22301
export const DOCUMENTATION_TEMPLATES = {
  POLICY: {
    name: 'Business Continuity Policy Template',
    sections: [
      'Purpose and Scope',
      'Policy Statement',
      'Roles and Responsibilities',
      'Key Principles',
      'Compliance Requirements',
      'Review and Updates'
    ]
  },
  
  PROCEDURE: {
    name: 'BC Procedure Template',
    sections: [
      'Objective',
      'Scope',
      'Definitions',
      'Responsibilities',
      'Procedure Steps',
      'Documentation Requirements',
      'Training and Awareness'
    ]
  },

  PLAN: {
    name: 'Business Continuity Plan Template',
    sections: [
      'Plan Overview',
      'Activation Criteria',
      'Response Team Structure',
      'Communication Plan',
      'Recovery Procedures',
      'Resource Requirements',
      'Plan Maintenance'
    ]
  }
}
