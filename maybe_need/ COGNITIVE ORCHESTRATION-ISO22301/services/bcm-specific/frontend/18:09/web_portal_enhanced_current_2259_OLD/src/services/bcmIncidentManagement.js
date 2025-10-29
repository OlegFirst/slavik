/**
 * BCM Incident Management API Service
 * Handles communication with Odoo bcm_incident_management module
 */

import api from './api'

class BCMIncidentManagementService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.incident.advanced'
    this.crisisURL = '/web/dataset/call_kw/bcm.crisis.response'
    this.recoveryURL = '/web/dataset/call_kw/bcm.recovery.process'
    this.emergencyURL = '/web/dataset/call_kw/bcm.emergency'
  }

  /**
   * Get all incidents with metrics
   */
  async getIncidents(filters = {}) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'search_read',
          args: [this.buildFilters(filters)],
          kwargs: {
            fields: [
              'incident_id', 'title', 'description', 'severity', 'status',
              'category', 'created_date', 'assignee_id', 'assignee_name',
              'affected_services', 'response_time', 'resolution_time'
            ],
            order: 'created_date desc'
          }
        }
      })

      const incidents = response.data.result
      const metrics = await this.getIncidentMetrics()

      return { incidents, metrics }
    } catch (error) {
      console.error('Failed to get incidents:', error)
      throw error
    }
  }

  /**
   * Get incident metrics
   */
  async getIncidentMetrics() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'get_incident_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get incident metrics:', error)
      return {
        active_incidents: 0,
        avg_response_time: 0,
        resolved_incidents: 0,
        team_members: 0
      }
    }
  }

  /**
   * Create new incident
   */
  async createIncident(incidentData) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'create',
          args: [incidentData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create incident:', error)
      throw error
    }
  }

  /**
   * Update incident
   */
  async updateIncident(incidentId, incidentData) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'write',
          args: [incidentId, incidentData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update incident:', error)
      throw error
    }
  }

  /**
   * Escalate incident
   */
  async escalateIncident(incidentId) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'escalate_incident',
          args: [incidentId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to escalate incident:', error)
      throw error
    }
  }

  /**
   * Declare emergency
   */
  async declareEmergency(emergencyData) {
    try {
      const response = await api.post(this.emergencyURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.emergency',
          method: 'declare_emergency',
          args: [emergencyData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to declare emergency:', error)
      throw error
    }
  }

  /**
   * End emergency
   */
  async endEmergency(emergencyId) {
    try {
      const response = await api.post(this.emergencyURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.emergency',
          method: 'end_emergency',
          args: [emergencyId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to end emergency:', error)
      throw error
    }
  }

  /**
   * Get crisis events
   */
  async getCrisisEvents() {
    try {
      const response = await api.post(this.crisisURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.crisis.response',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'title', 'description', 'timestamp', 'type', 'icon',
              'user_id', 'user_name', 'status'
            ],
            order: 'timestamp desc',
            limit: 20
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get crisis events:', error)
      return []
    }
  }

  /**
   * Activate crisis team
   */
  async activateCrisisTeam(teamData) {
    try {
      const response = await api.post(this.crisisURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.crisis.response',
          method: 'activate_crisis_team',
          args: [teamData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to activate crisis team:', error)
      throw error
    }
  }

  /**
   * Send crisis communication
   */
  async sendCommunication(communicationData) {
    try {
      const response = await api.post(this.crisisURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.crisis.response',
          method: 'send_communication',
          args: [communicationData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to send communication:', error)
      throw error
    }
  }

  /**
   * Get recovery data
   */
  async getRecoveryData() {
    try {
      const [processes, metrics] = await Promise.all([
        this.getRecoveryProcesses(),
        this.getRecoveryMetrics()
      ])

      return { processes, metrics }
    } catch (error) {
      console.error('Failed to get recovery data:', error)
      return { processes: [], metrics: {} }
    }
  }

  /**
   * Get recovery processes
   */
  async getRecoveryProcesses() {
    try {
      const response = await api.post(this.recoveryURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.recovery.process',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'name', 'status', 'completion', 'rto', 'rpo',
              'responsible_id', 'start_time', 'estimated_completion'
            ],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get recovery processes:', error)
      return []
    }
  }

  /**
   * Get recovery metrics
   */
  async getRecoveryMetrics() {
    try {
      const response = await api.post(this.recoveryURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.recovery.process',
          method: 'get_recovery_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get recovery metrics:', error)
      return {
        totalTime: 0,
        dataRecovery: 0,
        availability: 0,
        cost: 0
      }
    }
  }

  /**
   * Activate recovery process
   */
  async activateRecovery(recoveryData) {
    try {
      const response = await api.post(this.recoveryURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.recovery.process',
          method: 'activate_recovery',
          args: [recoveryData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to activate recovery:', error)
      throw error
    }
  }

  /**
   * Generate incident report
   */
  async generateReport(reportType = 'incident', filters = {}) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'generate_report',
          args: [reportType, filters],
          kwargs: {}
        }
      })

      // Handle file download
      if (response.data.result.file_data) {
        const link = document.createElement('a')
        link.href = `data:application/octet-stream;base64,${response.data.result.file_data}`
        link.download = response.data.result.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }

      return response.data.result
    } catch (error) {
      console.error('Failed to generate report:', error)
      throw error
    }
  }

  /**
   * Get incident analytics
   */
  async getIncidentAnalytics(timeRange = '30d') {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'get_incident_analytics',
          args: [timeRange],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get incident analytics:', error)
      return {}
    }
  }

  /**
   * Update incident workflow
   */
  async updateWorkflow(incidentId, workflowData) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'update_workflow',
          args: [incidentId, workflowData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update workflow:', error)
      throw error
    }
  }

  /**
   * Get incident timeline
   */
  async getIncidentTimeline(incidentId) {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.incident.timeline', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.timeline',
          method: 'search_read',
          args: [['incident_id', '=', incidentId]],
          kwargs: {
            fields: ['timestamp', 'action', 'description', 'user_name', 'status_from', 'status_to'],
            order: 'timestamp desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get incident timeline:', error)
      return []
    }
  }

  /**
   * Assign incident team
   */
  async assignTeam(incidentId, teamMembers) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident.advanced',
          method: 'assign_team',
          args: [incidentId, teamMembers],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to assign team:', error)
      throw error
    }
  }

  /**
   * Build search filters
   */
  buildFilters(filters) {
    const domain = []

    if (filters.status) {
      domain.push(['status', '=', filters.status])
    }

    if (filters.severity) {
      domain.push(['severity', '=', filters.severity])
    }

    if (filters.category) {
      domain.push(['category', '=', filters.category])
    }

    if (filters.assignee_id) {
      domain.push(['assignee_id', '=', filters.assignee_id])
    }

    if (filters.date_from) {
      domain.push(['created_date', '>=', filters.date_from])
    }

    if (filters.date_to) {
      domain.push(['created_date', '<=', filters.date_to])
    }

    return domain
  }

  /**
   * Calculate incident priority
   */
  calculatePriority(incident) {
    const severityWeights = {
      critical: 4,
      high: 3,
      medium: 2,
      low: 1
    }

    const impactFactors = {
      system: 1.5,
      security: 2.0,
      data: 1.8,
      natural: 1.3,
      human: 1.0
    }

    const severityWeight = severityWeights[incident.severity] || 1
    const impactFactor = impactFactors[incident.category] || 1

    return severityWeight * impactFactor
  }

  /**
   * Format incident for display
   */
  formatIncident(incident) {
    return {
      ...incident,
      priority: this.calculatePriority(incident),
      age: this.calculateAge(incident.created_date),
      status_class: this.getStatusClass(incident.status),
      severity_class: this.getSeverityClass(incident.severity)
    }
  }

  /**
   * Calculate incident age
   */
  calculateAge(createdDate) {
    const now = new Date()
    const created = new Date(createdDate)
    const diffMs = now - created
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

    if (diffHours < 24) {
      return `${diffHours}h`
    } else {
      const diffDays = Math.floor(diffHours / 24)
      return `${diffDays}d`
    }
  }

  /**
   * Get status CSS class
   */
  getStatusClass(status) {
    const classes = {
      open: 'status-open',
      investigating: 'status-investigating',
      resolving: 'status-resolving',
      resolved: 'status-resolved',
      closed: 'status-closed'
    }
    return classes[status] || 'status-open'
  }

  /**
   * Get severity CSS class
   */
  getSeverityClass(severity) {
    const classes = {
      critical: 'severity-critical',
      high: 'severity-high',
      medium: 'severity-medium',
      low: 'severity-low'
    }
    return classes[severity] || 'severity-medium'
  }
}

export default new BCMIncidentManagementService()