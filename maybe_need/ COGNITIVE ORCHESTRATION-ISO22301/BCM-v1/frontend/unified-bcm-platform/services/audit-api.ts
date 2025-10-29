'use client'

// Audit & Compliance API Service
export interface AuditItem {
  id: string
  title: string
  description: string
  category: 'iso22301' | 'sox' | 'gdpr' | 'internal' | 'external'
  status: 'planned' | 'in_progress' | 'completed' | 'overdue'
  priority: 'critical' | 'high' | 'medium' | 'low'
  auditType: 'internal' | 'external' | 'certification' | 'compliance'
  scheduledDate: string
  completedDate?: string
  assignedTo: {
    id: string
    name: string
    email: string
  }
  findings: AuditFinding[]
  evidence: AuditEvidence[]
  complianceScore: number
  recommendations: string[]
}

export interface AuditFinding {
  id: string
  type: 'major' | 'minor' | 'observation' | 'opportunity'
  description: string
  requirement: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'in_progress' | 'resolved' | 'verified'
  discoveredDate: string
  targetDate: string
  assignedTo?: {
    id: string
    name: string
  }
  remediation: {
    plan: string
    progress: number
    estimatedCompletion: string
  }
}

export interface AuditEvidence {
  id: string
  name: string
  type: 'document' | 'screenshot' | 'log' | 'procedure' | 'interview'
  description: string
  uploadedBy: string
  uploadedAt: string
  fileUrl?: string
  verified: boolean
}

export interface AuditMetrics {
  auditsPassed: number
  auditsTotal: number
  findings: number
  overallScore: number
  complianceRate: number
  findingsResolved: number
  averageResolutionTime: number
  upcomingAudits: number
  overdueFindings: number
  categoryScores: Record<string, number>
  trends: {
    period: string
    score: number
    findings: number
    resolved: number
  }[]
}

export interface ComplianceFramework {
  id: string
  name: string
  description: string
  requirements: ComplianceRequirement[]
  overallScore: number
  lastAssessed: string
  nextAssessment: string
}

export interface ComplianceRequirement {
  id: string
  clause: string
  title: string
  description: string
  status: 'compliant' | 'non_compliant' | 'partial' | 'not_assessed'
  score: number
  evidence: string[]
  gaps: string[]
  recommendations: string[]
  lastReviewed: string
}

class AuditAPI {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

  // Get audit metrics for analytics
  async getAuditMetrics(timeRange: string = '30d'): Promise<{
    data: AuditMetrics
  }> {
    const metrics: AuditMetrics = {
      auditsPassed: 18,
      auditsTotal: 21,
      findings: 7,
      overallScore: 86,
      complianceRate: 94,
      findingsResolved: 15,
      averageResolutionTime: 12.5,
      upcomingAudits: 3,
      overdueFindings: 2,
      categoryScores: {
        'ISO 22301': 88,
        'SOX': 92,
        'GDPR': 85,
        'Internal Controls': 89,
        'Security': 84
      },
      trends: [
        { period: '2024-01-01', score: 84, findings: 12, resolved: 8 },
        { period: '2024-01-02', score: 86, findings: 8, resolved: 10 },
        { period: '2024-01-03', score: 85, findings: 15, resolved: 12 },
        { period: '2024-01-04', score: 87, findings: 6, resolved: 14 },
        { period: '2024-01-05', score: 86, findings: 7, resolved: 15 }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: metrics }), 600)
    })
  }

  // Get all audits with filtering
  async getAudits(filters?: {
    status?: string[]
    category?: string[]
    auditType?: string[]
    assignee?: string
    timeRange?: string
  }): Promise<{ data: AuditItem[] }> {
    const mockAudits: AuditItem[] = [
      {
        id: 'AUD-001',
        title: 'ISO 22301 Annual Certification Audit',
        description: 'Annual certification audit for Business Continuity Management System compliance',
        category: 'iso22301',
        status: 'in_progress',
        priority: 'critical',
        auditType: 'certification',
        scheduledDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        assignedTo: {
          id: 'user-1',
          name: 'Sarah Johnson',
          email: 'sarah.johnson@company.com'
        },
        findings: [
          {
            id: 'finding-1',
            type: 'minor',
            description: 'Business Impact Analysis documentation needs updating for new processes',
            requirement: 'ISO 22301:2019 - Clause 8.2.2',
            severity: 'medium',
            status: 'open',
            discoveredDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            targetDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
            assignedTo: {
              id: 'user-2',
              name: 'Mike Davis'
            },
            remediation: {
              plan: 'Update BIA documentation to include new business processes added in Q4',
              progress: 30,
              estimatedCompletion: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString()
            }
          }
        ],
        evidence: [
          {
            id: 'evidence-1',
            name: 'BCP Documentation Review',
            type: 'document',
            description: 'Business Continuity Plan documentation package',
            uploadedBy: 'Sarah Johnson',
            uploadedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            verified: true
          }
        ],
        complianceScore: 88,
        recommendations: [
          'Update BIA documentation quarterly',
          'Implement automated compliance monitoring',
          'Enhance evidence collection processes'
        ]
      },
      {
        id: 'AUD-002',
        title: 'Internal Security Controls Review',
        description: 'Quarterly review of information security controls and procedures',
        category: 'internal',
        status: 'completed',
        priority: 'high',
        auditType: 'internal',
        scheduledDate: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
        completedDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        assignedTo: {
          id: 'user-3',
          name: 'Alex Thompson',
          email: 'alex.thompson@company.com'
        },
        findings: [
          {
            id: 'finding-2',
            type: 'observation',
            description: 'Password policy enforcement could be strengthened',
            requirement: 'Internal Security Standard - IS-001',
            severity: 'low',
            status: 'resolved',
            discoveredDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
            targetDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            assignedTo: {
              id: 'user-4',
              name: 'IT Security Team'
            },
            remediation: {
              plan: 'Implement stronger password complexity requirements and multi-factor authentication',
              progress: 100,
              estimatedCompletion: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
            }
          }
        ],
        evidence: [
          {
            id: 'evidence-2',
            name: 'Security Configuration Screenshots',
            type: 'screenshot',
            description: 'System security configuration evidence',
            uploadedBy: 'Alex Thompson',
            uploadedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            verified: true
          }
        ],
        complianceScore: 92,
        recommendations: [
          'Continue regular security control reviews',
          'Implement automated vulnerability scanning',
          'Enhance incident response documentation'
        ]
      },
      {
        id: 'AUD-003',
        title: 'GDPR Compliance Assessment',
        description: 'Annual assessment of GDPR compliance and data protection measures',
        category: 'gdpr',
        status: 'planned',
        priority: 'high',
        auditType: 'compliance',
        scheduledDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000).toISOString(),
        assignedTo: {
          id: 'user-5',
          name: 'Emma Wilson',
          email: 'emma.wilson@company.com'
        },
        findings: [],
        evidence: [],
        complianceScore: 0,
        recommendations: []
      }
    ]

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: mockAudits }), 500)
    })
  }

  // Get audit by ID
  async getAudit(auditId: string): Promise<{ data: AuditItem }> {
    const audits = await this.getAudits().then(result => result.data)
    const audit = audits.find(a => a.id === auditId)

    if (!audit) {
      throw new Error(`Audit ${auditId} not found`)
    }

    return Promise.resolve({ data: audit })
  }

  // Create new audit
  async createAudit(audit: Partial<AuditItem>): Promise<{ data: AuditItem }> {
    const newAudit: AuditItem = {
      id: `AUD-${String(Date.now()).slice(-3)}`,
      title: audit.title || '',
      description: audit.description || '',
      category: audit.category || 'internal',
      status: 'planned',
      priority: audit.priority || 'medium',
      auditType: audit.auditType || 'internal',
      scheduledDate: audit.scheduledDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      assignedTo: audit.assignedTo || {
        id: 'current-user',
        name: 'Current User',
        email: 'user@company.com'
      },
      findings: [],
      evidence: [],
      complianceScore: 0,
      recommendations: []
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: newAudit }), 800)
    })
  }

  // Update audit
  async updateAudit(auditId: string, updates: Partial<AuditItem>): Promise<{ data: AuditItem }> {
    const audit = await this.getAudit(auditId).then(result => result.data)

    const updatedAudit: AuditItem = {
      ...audit,
      ...updates
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: updatedAudit }), 600)
    })
  }

  // Add finding to audit
  async addFinding(auditId: string, finding: Partial<AuditFinding>): Promise<{ data: AuditFinding }> {
    const newFinding: AuditFinding = {
      id: `finding-${Date.now()}`,
      type: finding.type || 'observation',
      description: finding.description || '',
      requirement: finding.requirement || '',
      severity: finding.severity || 'medium',
      status: 'open',
      discoveredDate: new Date().toISOString(),
      targetDate: finding.targetDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      assignedTo: finding.assignedTo,
      remediation: {
        plan: '',
        progress: 0,
        estimatedCompletion: finding.targetDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      }
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: newFinding }), 600)
    })
  }

  // Get compliance frameworks
  async getComplianceFrameworks(): Promise<{ data: ComplianceFramework[] }> {
    const frameworks: ComplianceFramework[] = [
      {
        id: 'iso22301',
        name: 'ISO 22301:2019',
        description: 'Business Continuity Management Systems',
        requirements: [
          {
            id: 'iso22301-4.1',
            clause: '4.1',
            title: 'Understanding the organization and its context',
            description: 'The organization shall determine external and internal issues relevant to its purpose',
            status: 'compliant',
            score: 90,
            evidence: ['Context analysis document', 'Stakeholder register'],
            gaps: [],
            recommendations: ['Regular context review'],
            lastReviewed: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 'iso22301-8.2.2',
            clause: '8.2.2',
            title: 'Business impact analysis',
            description: 'The organization shall establish and maintain a business impact analysis',
            status: 'partial',
            score: 75,
            evidence: ['BIA procedures', 'Process assessments'],
            gaps: ['Missing documentation for new processes'],
            recommendations: ['Update BIA for new processes', 'Automate BIA reviews'],
            lastReviewed: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
          }
        ],
        overallScore: 88,
        lastAssessed: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        nextAssessment: new Date(Date.now() + 335 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'gdpr',
        name: 'GDPR',
        description: 'General Data Protection Regulation',
        requirements: [
          {
            id: 'gdpr-art25',
            clause: 'Article 25',
            title: 'Data protection by design and by default',
            description: 'Data protection principles must be integrated into processing activities',
            status: 'compliant',
            score: 85,
            evidence: ['Privacy policies', 'Data mapping'],
            gaps: [],
            recommendations: ['Regular privacy training'],
            lastReviewed: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString()
          }
        ],
        overallScore: 85,
        lastAssessed: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
        nextAssessment: new Date(Date.now() + 305 * 24 * 60 * 60 * 1000).toISOString()
      }
    ]

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: frameworks }), 400)
    })
  }

  // Get audit analytics
  async getAuditAnalytics(timeRange: string = '30d'): Promise<{
    data: {
      summary: {
        totalAudits: number
        completionRate: number
        averageScore: number
        findingsRate: number
      }
      trends: {
        audit_scores: Array<{ date: string; score: number }>
        findings_count: Array<{ date: string; count: number }>
        compliance_rate: Array<{ date: string; rate: number }>
      }
      findingsByType: Array<{ type: string; count: number }>
      topNonCompliantAreas: Array<{ area: string; score: number; findings: number }>
    }
  }> {
    const analytics = {
      summary: {
        totalAudits: 21,
        completionRate: 0.86,
        averageScore: 86,
        findingsRate: 0.33
      },
      trends: {
        audit_scores: [
          { date: '2024-01-01', score: 84 },
          { date: '2024-01-02', score: 86 },
          { date: '2024-01-03', score: 85 },
          { date: '2024-01-04', score: 87 },
          { date: '2024-01-05', score: 86 }
        ],
        findings_count: [
          { date: '2024-01-01', count: 12 },
          { date: '2024-01-02', count: 8 },
          { date: '2024-01-03', count: 15 },
          { date: '2024-01-04', count: 6 },
          { date: '2024-01-05', count: 7 }
        ],
        compliance_rate: [
          { date: '2024-01-01', rate: 92 },
          { date: '2024-01-02', rate: 94 },
          { date: '2024-01-03', rate: 91 },
          { date: '2024-01-04', rate: 95 },
          { date: '2024-01-05', rate: 94 }
        ]
      },
      findingsByType: [
        { type: 'major', count: 2 },
        { type: 'minor', count: 8 },
        { type: 'observation', count: 12 },
        { type: 'opportunity', count: 5 }
      ],
      topNonCompliantAreas: [
        { area: 'Documentation Management', score: 78, findings: 5 },
        { area: 'Training Records', score: 82, findings: 3 },
        { area: 'Risk Assessment', score: 85, findings: 2 },
        { area: 'Incident Response', score: 87, findings: 1 }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: analytics }), 800)
    })
  }

  // Generate compliance report
  async generateComplianceReport(
    frameworkId: string,
    timeRange: string = '1y'
  ): Promise<{
    data: {
      framework: ComplianceFramework
      summary: {
        overallScore: number
        compliantRequirements: number
        totalRequirements: number
        majorGaps: number
        recommendations: string[]
      }
      detailedFindings: ComplianceRequirement[]
      actionPlan: Array<{
        priority: string
        requirement: string
        action: string
        timeline: string
        owner: string
      }>
    }
  }> {
    const frameworks = await this.getComplianceFrameworks().then(result => result.data)
    const framework = frameworks.find(f => f.id === frameworkId)

    if (!framework) {
      throw new Error(`Framework ${frameworkId} not found`)
    }

    const report = {
      framework,
      summary: {
        overallScore: framework.overallScore,
        compliantRequirements: framework.requirements.filter(r => r.status === 'compliant').length,
        totalRequirements: framework.requirements.length,
        majorGaps: framework.requirements.filter(r => r.status === 'non_compliant').length,
        recommendations: [
          'Address critical compliance gaps immediately',
          'Implement regular compliance monitoring',
          'Enhance documentation processes',
          'Provide additional staff training'
        ]
      },
      detailedFindings: framework.requirements,
      actionPlan: [
        {
          priority: 'High',
          requirement: '8.2.2 Business Impact Analysis',
          action: 'Update BIA documentation for new processes',
          timeline: '2 weeks',
          owner: 'Business Continuity Team'
        },
        {
          priority: 'Medium',
          requirement: '4.1 Context Analysis',
          action: 'Schedule quarterly context reviews',
          timeline: '1 month',
          owner: 'Management Team'
        }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: report }), 1200)
    })
  }
}

export const auditAPI = new AuditAPI()

// Export query keys for React Query
export const auditQueryKeys = {
  all: ['audits'] as const,
  lists: () => [...auditQueryKeys.all, 'list'] as const,
  list: (filters?: any) => [...auditQueryKeys.lists(), filters] as const,
  details: () => [...auditQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...auditQueryKeys.details(), id] as const,
  metrics: (timeRange: string) => [...auditQueryKeys.all, 'metrics', timeRange] as const,
  analytics: (timeRange: string) => [...auditQueryKeys.all, 'analytics', timeRange] as const,
  frameworks: () => [...auditQueryKeys.all, 'frameworks'] as const,
  compliance: (frameworkId: string) => [...auditQueryKeys.all, 'compliance', frameworkId] as const
}

// Re-export types
export type {
  AuditItem,
  AuditFinding,
  AuditEvidence,
  AuditMetrics,
  ComplianceFramework,
  ComplianceRequirement
}