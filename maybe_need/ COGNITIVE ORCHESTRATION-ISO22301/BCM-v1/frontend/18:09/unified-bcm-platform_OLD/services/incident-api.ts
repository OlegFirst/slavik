'use client'

// Incident Management API Service
export interface Incident {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  category: string
  reportedBy: {
    id: string
    name: string
    email: string
  }
  assignedTo?: {
    id: string
    name: string
    email: string
  }
  createdAt: string
  updatedAt: string
  resolvedAt?: string
  impactedSystems: string[]
  estimatedImpact: {
    financial: number
    operational: string
    reputational: string
  }
  timelineEvents: IncidentEvent[]
  attachments: IncidentAttachment[]
}

export interface IncidentEvent {
  id: string
  timestamp: string
  type: 'created' | 'updated' | 'escalated' | 'resolved' | 'comment'
  description: string
  user: {
    id: string
    name: string
  }
  metadata?: Record<string, any>
}

export interface IncidentAttachment {
  id: string
  name: string
  type: string
  size: number
  url: string
  uploadedBy: string
  uploadedAt: string
}

export interface IncidentMetrics {
  activeIncidents: number
  incidentChange: number
  avgResolutionTime: number
  mttrChange: number
  totalIncidents: number
  resolvedIncidents: number
  escalatedIncidents: number
  severityDistribution: {
    critical: number
    high: number
    medium: number
    low: number
  }
  categoryBreakdown: Record<string, number>
  trends: {
    period: string
    incidents: number
    resolved: number
    avgResolution: number
  }[]
}

export interface IncidentTemplate {
  id: string
  name: string
  category: string
  description: string
  severity: string
  checklistItems: string[]
  estimatedResolutionTime: number
}

class IncidentAPI {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

  // Get incident metrics for analytics
  async getIncidentMetrics(timeRange: string = '30d'): Promise<{
    data: IncidentMetrics
  }> {
    const metrics: IncidentMetrics = {
      activeIncidents: 3,
      incidentChange: -12.5,
      avgResolutionTime: 4.2,
      mttrChange: -8.7,
      totalIncidents: 47,
      resolvedIncidents: 44,
      escalatedIncidents: 2,
      severityDistribution: {
        critical: 1,
        high: 2,
        medium: 0,
        low: 0
      },
      categoryBreakdown: {
        'System Outage': 15,
        'Security Breach': 8,
        'Data Loss': 6,
        'Network Issues': 12,
        'Application Error': 6
      },
      trends: [
        { period: '2024-01-01', incidents: 12, resolved: 11, avgResolution: 4.8 },
        { period: '2024-01-02', incidents: 8, resolved: 9, avgResolution: 4.2 },
        { period: '2024-01-03', incidents: 15, resolved: 13, avgResolution: 5.1 },
        { period: '2024-01-04', incidents: 6, resolved: 8, avgResolution: 3.9 },
        { period: '2024-01-05', incidents: 6, resolved: 3, avgResolution: 4.0 }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: metrics }), 600)
    })
  }

  // Get all incidents with filtering
  async getIncidents(filters?: {
    status?: string[]
    severity?: string[]
    category?: string
    assignee?: string
    timeRange?: string
  }): Promise<{ data: Incident[] }> {
    const mockIncidents: Incident[] = [
      {
        id: 'INC-001',
        title: 'Database Connection Timeout',
        description: 'Primary database experiencing connection timeouts affecting user authentication',
        severity: 'critical',
        status: 'in_progress',
        category: 'System Outage',
        reportedBy: {
          id: 'user-1',
          name: 'John Doe',
          email: 'john.doe@company.com'
        },
        assignedTo: {
          id: 'user-2',
          name: 'Sarah Smith',
          email: 'sarah.smith@company.com'
        },
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        impactedSystems: ['Authentication Service', 'User Portal', 'Mobile App'],
        estimatedImpact: {
          financial: 50000,
          operational: 'High - User access severely limited',
          reputational: 'Medium - Public facing services affected'
        },
        timelineEvents: [
          {
            id: 'event-1',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            type: 'created',
            description: 'Incident reported by monitoring system',
            user: { id: 'system', name: 'System' }
          },
          {
            id: 'event-2',
            timestamp: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
            type: 'updated',
            description: 'Assigned to database team for investigation',
            user: { id: 'user-3', name: 'Mike Johnson' }
          }
        ],
        attachments: []
      },
      {
        id: 'INC-002',
        title: 'Network Latency Issues',
        description: 'Increased network latency reported in European region',
        severity: 'high',
        status: 'open',
        category: 'Network Issues',
        reportedBy: {
          id: 'user-4',
          name: 'Anna Wilson',
          email: 'anna.wilson@company.com'
        },
        createdAt: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        updatedAt: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        impactedSystems: ['CDN', 'API Gateway'],
        estimatedImpact: {
          financial: 15000,
          operational: 'Medium - Performance degradation',
          reputational: 'Low - Limited user impact'
        },
        timelineEvents: [
          {
            id: 'event-3',
            timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
            type: 'created',
            description: 'Network performance degradation reported',
            user: { id: 'user-4', name: 'Anna Wilson' }
          }
        ],
        attachments: []
      },
      {
        id: 'INC-003',
        title: 'API Rate Limiting Error',
        description: 'Third-party API returning rate limit errors, affecting data synchronization',
        severity: 'medium',
        status: 'resolved',
        category: 'Application Error',
        reportedBy: {
          id: 'user-5',
          name: 'David Brown',
          email: 'david.brown@company.com'
        },
        assignedTo: {
          id: 'user-6',
          name: 'Lisa Chen',
          email: 'lisa.chen@company.com'
        },
        createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        resolvedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        impactedSystems: ['Data Sync Service', 'Reporting Module'],
        estimatedImpact: {
          financial: 5000,
          operational: 'Low - Delayed data updates',
          reputational: 'Minimal - Internal process affected'
        },
        timelineEvents: [
          {
            id: 'event-4',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
            type: 'created',
            description: 'API rate limiting errors detected',
            user: { id: 'user-5', name: 'David Brown' }
          },
          {
            id: 'event-5',
            timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
            type: 'resolved',
            description: 'Implemented exponential backoff and request throttling',
            user: { id: 'user-6', name: 'Lisa Chen' }
          }
        ],
        attachments: []
      }
    ]

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: mockIncidents }), 500)
    })
  }

  // Get incident by ID
  async getIncident(incidentId: string): Promise<{ data: Incident }> {
    const incidents = await this.getIncidents().then(result => result.data)
    const incident = incidents.find(i => i.id === incidentId)

    if (!incident) {
      throw new Error(`Incident ${incidentId} not found`)
    }

    return Promise.resolve({ data: incident })
  }

  // Create new incident
  async createIncident(incident: Partial<Incident>): Promise<{ data: Incident }> {
    const newIncident: Incident = {
      id: `INC-${String(Date.now()).slice(-3)}`,
      title: incident.title || '',
      description: incident.description || '',
      severity: incident.severity || 'medium',
      status: 'open',
      category: incident.category || 'General',
      reportedBy: incident.reportedBy || {
        id: 'current-user',
        name: 'Current User',
        email: 'user@company.com'
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      impactedSystems: incident.impactedSystems || [],
      estimatedImpact: incident.estimatedImpact || {
        financial: 0,
        operational: 'To be assessed',
        reputational: 'To be assessed'
      },
      timelineEvents: [
        {
          id: 'event-1',
          timestamp: new Date().toISOString(),
          type: 'created',
          description: 'Incident created',
          user: { id: 'current-user', name: 'Current User' }
        }
      ],
      attachments: []
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: newIncident }), 800)
    })
  }

  // Update incident
  async updateIncident(incidentId: string, updates: Partial<Incident>): Promise<{ data: Incident }> {
    const incident = await this.getIncident(incidentId).then(result => result.data)

    const updatedIncident: Incident = {
      ...incident,
      ...updates,
      updatedAt: new Date().toISOString(),
      timelineEvents: [
        ...incident.timelineEvents,
        {
          id: `event-${Date.now()}`,
          timestamp: new Date().toISOString(),
          type: 'updated',
          description: 'Incident updated',
          user: { id: 'current-user', name: 'Current User' }
        }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: updatedIncident }), 600)
    })
  }

  // Resolve incident
  async resolveIncident(incidentId: string, resolution: string): Promise<{ data: Incident }> {
    const incident = await this.getIncident(incidentId).then(result => result.data)

    const resolvedIncident: Incident = {
      ...incident,
      status: 'resolved',
      resolvedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      timelineEvents: [
        ...incident.timelineEvents,
        {
          id: `event-${Date.now()}`,
          timestamp: new Date().toISOString(),
          type: 'resolved',
          description: resolution,
          user: { id: 'current-user', name: 'Current User' }
        }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: resolvedIncident }), 700)
    })
  }

  // Add comment to incident
  async addIncidentComment(incidentId: string, comment: string): Promise<{ success: boolean }> {
    // Mock implementation
    return new Promise((resolve) => {
      setTimeout(() => resolve({ success: true }), 400)
    })
  }

  // Get incident templates
  async getIncidentTemplates(): Promise<{ data: IncidentTemplate[] }> {
    const templates: IncidentTemplate[] = [
      {
        id: 'template-1',
        name: 'System Outage',
        category: 'System Outage',
        description: 'Complete or partial system unavailability',
        severity: 'critical',
        checklistItems: [
          'Identify affected systems and services',
          'Assess user impact and communicate status',
          'Engage technical teams for investigation',
          'Implement temporary workarounds if possible',
          'Monitor system recovery and validate resolution'
        ],
        estimatedResolutionTime: 120
      },
      {
        id: 'template-2',
        name: 'Security Incident',
        category: 'Security Breach',
        description: 'Potential or confirmed security breach',
        severity: 'high',
        checklistItems: [
          'Isolate affected systems immediately',
          'Notify security team and management',
          'Preserve evidence and logs',
          'Assess scope of potential data exposure',
          'Implement containment measures',
          'Conduct forensic analysis'
        ],
        estimatedResolutionTime: 240
      },
      {
        id: 'template-3',
        name: 'Performance Degradation',
        category: 'Performance Issues',
        description: 'System performance below acceptable thresholds',
        severity: 'medium',
        checklistItems: [
          'Monitor system metrics and identify bottlenecks',
          'Check resource utilization (CPU, memory, disk)',
          'Review recent changes or deployments',
          'Optimize queries or processes if needed',
          'Scale resources if necessary'
        ],
        estimatedResolutionTime: 60
      }
    ]

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: templates }), 300)
    })
  }

  // Get incident analytics
  async getIncidentAnalytics(timeRange: string = '30d'): Promise<{
    data: {
      summary: {
        totalIncidents: number
        avgResolutionTime: number
        escalationRate: number
        reopenRate: number
      }
      trends: {
        incident_volume: Array<{ date: string; count: number }>
        resolution_time: Array<{ date: string; time: number }>
        severity_distribution: Array<{ severity: string; count: number }>
      }
      topCategories: Array<{ category: string; count: number; avgResolution: number }>
    }
  }> {
    const analytics = {
      summary: {
        totalIncidents: 47,
        avgResolutionTime: 4.2,
        escalationRate: 0.15,
        reopenRate: 0.08
      },
      trends: {
        incident_volume: [
          { date: '2024-01-01', count: 12 },
          { date: '2024-01-02', count: 8 },
          { date: '2024-01-03', count: 15 },
          { date: '2024-01-04', count: 6 },
          { date: '2024-01-05', count: 6 }
        ],
        resolution_time: [
          { date: '2024-01-01', time: 4.8 },
          { date: '2024-01-02', time: 4.2 },
          { date: '2024-01-03', time: 5.1 },
          { date: '2024-01-04', time: 3.9 },
          { date: '2024-01-05', time: 4.0 }
        ],
        severity_distribution: [
          { severity: 'critical', count: 3 },
          { severity: 'high', count: 8 },
          { severity: 'medium', count: 21 },
          { severity: 'low', count: 15 }
        ]
      },
      topCategories: [
        { category: 'System Outage', count: 15, avgResolution: 3.2 },
        { category: 'Network Issues', count: 12, avgResolution: 2.8 },
        { category: 'Security Breach', count: 8, avgResolution: 6.5 },
        { category: 'Data Loss', count: 6, avgResolution: 8.1 },
        { category: 'Application Error', count: 6, avgResolution: 2.1 }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: analytics }), 800)
    })
  }
}

export const incidentAPI = new IncidentAPI()

// Export query keys for React Query
export const incidentQueryKeys = {
  all: ['incidents'] as const,
  lists: () => [...incidentQueryKeys.all, 'list'] as const,
  list: (filters?: any) => [...incidentQueryKeys.lists(), filters] as const,
  details: () => [...incidentQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...incidentQueryKeys.details(), id] as const,
  metrics: (timeRange: string) => [...incidentQueryKeys.all, 'metrics', timeRange] as const,
  analytics: (timeRange: string) => [...incidentQueryKeys.all, 'analytics', timeRange] as const,
  templates: () => [...incidentQueryKeys.all, 'templates'] as const
}

// Re-export types
export type {
  Incident,
  IncidentEvent,
  IncidentAttachment,
  IncidentMetrics,
  IncidentTemplate
}