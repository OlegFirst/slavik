/**
 * BCM Incident Management Service
 * Integrates with Odoo bcm_incident module and AI Orchestrator
 */

import api from './api'
import eventBus from './eventbus'

class BCMIncidentService {
  constructor() {
    this.model = 'bcm.incident'
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
  }

  /**
   * Get all incidents with optional filters
   */
  async getIncidents(filters = {}) {
    const cacheKey = `incidents_${JSON.stringify(filters)}`

    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey)
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data
      }
    }

    try {
      const domain = this._buildDomain(filters)
      const fields = [
        'id', 'name', 'description', 'severity', 'status', 'incident_type',
        'reported_by', 'response_team_ids', 'created_date', 'resolved_date',
        'impact_level', 'escalation_level', 'location', 'affected_systems',
        'timeline_ids', 'classification', 'ai_confidence', 'tags',
        'estimated_recovery_time', 'actual_recovery_time', 'lessons_learned'
      ]

      // Mock incidents data for development
      const incidents = [
        {
          id: 1,
          name: 'Network Infrastructure Failure',
          description: 'Critical network outage affecting main data center',
          severity: 'critical',
          status: 'in_progress',
          incident_type: 'infrastructure',
          reported_by: 'IT Team',
          response_team_ids: [1, 2],
          created_date: new Date().toISOString(),
          impact_level: 'high',
          escalation_level: 2,
          location: 'Main DC',
          affected_systems: ['Network', 'Email', 'ERP'],
          classification: 'Infrastructure Failure',
          ai_confidence: 0.95,
          tags: ['critical', 'network', 'outage']
        },
        {
          id: 2,
          name: 'Security Breach Attempt',
          description: 'Suspicious activity detected on external firewall',
          severity: 'high',
          status: 'open',
          incident_type: 'security',
          reported_by: 'Security Team',
          response_team_ids: [3],
          created_date: new Date(Date.now() - 3600000).toISOString(),
          impact_level: 'medium',
          escalation_level: 1,
          location: 'External Perimeter',
          affected_systems: ['Firewall', 'VPN'],
          classification: 'Security Incident',
          ai_confidence: 0.87,
          tags: ['security', 'firewall', 'breach']
        }
      ]
      // const incidents = await api.get(`/${this.model}`, { params: { domain, fields, ...options } })

      // Cache the result
      this.cache.set(cacheKey, {
        data: incidents,
        timestamp: Date.now()
      })

      return incidents
    } catch (error) {
      console.error('Failed to fetch incidents:', error)
      throw new Error('Unable to retrieve incidents. Please check your connection.')
    }
  }

  /**
   * Get active incidents (not resolved)
   */
  async getActiveIncidents() {
    return this.getIncidents({
      status: ['!=', 'resolved']
    })
  }

  /**
   * Get critical incidents
   */
  async getCriticalIncidents() {
    return this.getIncidents({
      severity: 'critical'
    })
  }

  /**
   * Create new incident
   */
  async createIncident(incidentData) {
    try {
      // Validate required fields
      this._validateIncidentData(incidentData)

      // Prepare data for Odoo
      const odooData = {
        name: incidentData.title,
        description: incidentData.description,
        severity: incidentData.severity || 'medium',
        incident_type: incidentData.incident_type || 'operational',
        reported_by: incidentData.reported_by,
        location: incidentData.location,
        affected_systems: incidentData.affected_systems || [],
        impact_level: incidentData.impact_level || 'medium',
        tags: incidentData.tags || [],
        status: 'open'
      }

      const incidentId = await api.create(this.model, odooData)

      // Get AI classification if enabled
      if (incidentData.use_ai_classification) {
        await this.requestAIClassification(incidentId, incidentData.description)
      }

      // Assign response team if provided
      if (incidentData.response_team_ids && incidentData.response_team_ids.length > 0) {
        await this.assignResponseTeam(incidentId, incidentData.response_team_ids)
      }

      // Publish incident created event
      await eventBus.publish('bcm.incident.created', {
        incident_id: incidentId,
        severity: odooData.severity,
        type: odooData.incident_type,
        created_by: odooData.reported_by
      })

      // Clear cache
      this._clearCache()

      return incidentId
    } catch (error) {
      console.error('Failed to create incident:', error)
      throw new Error('Unable to create incident. Please try again.')
    }
  }

  /**
   * Update incident
   */
  async updateIncident(incidentId, updates) {
    try {
      await api.write(this.model, [incidentId], updates)

      // Publish incident updated event
      await eventBus.publish('bcm.incident.updated', {
        incident_id: incidentId,
        updates: Object.keys(updates),
        timestamp: new Date().toISOString()
      })

      // Clear cache
      this._clearCache()

      return true
    } catch (error) {
      console.error('Failed to update incident:', error)
      throw new Error('Unable to update incident. Please try again.')
    }
  }

  /**
   * Resolve incident
   */
  async resolveIncident(incidentId, resolution) {
    try {
      const updates = {
        status: 'resolved',
        resolved_date: new Date().toISOString(),
        resolution_notes: resolution.notes,
        lessons_learned: resolution.lessons_learned,
        actual_recovery_time: resolution.recovery_time
      }

      await this.updateIncident(incidentId, updates)

      // Publish incident resolved event
      await eventBus.publish('bcm.incident.resolved', {
        incident_id: incidentId,
        resolution: resolution,
        resolved_at: updates.resolved_date
      })

      return true
    } catch (error) {
      console.error('Failed to resolve incident:', error)
      throw new Error('Unable to resolve incident. Please try again.')
    }
  }

  /**
   * Escalate incident
   */
  async escalateIncident(incidentId, escalationLevel) {
    try {
      const updates = {
        escalation_level: escalationLevel,
        status: 'escalated'
      }

      await this.updateIncident(incidentId, updates)

      // Publish escalation event
      await eventBus.publish('bcm.incident.escalated', {
        incident_id: incidentId,
        escalation_level: escalationLevel,
        escalated_at: new Date().toISOString()
      })

      return true
    } catch (error) {
      console.error('Failed to escalate incident:', error)
      throw new Error('Unable to escalate incident. Please try again.')
    }
  }

  /**
   * Assign response team
   */
  async assignResponseTeam(incidentId, teamIds) {
    try {
      await api.write(this.model, [incidentId], {
        response_team_ids: [[6, 0, teamIds]] // Odoo many2many syntax
      })

      // Publish team assignment event
      await eventBus.publish('bcm.incident.team_assigned', {
        incident_id: incidentId,
        team_ids: teamIds,
        assigned_at: new Date().toISOString()
      })

      return true
    } catch (error) {
      console.error('Failed to assign response team:', error)
      throw new Error('Unable to assign response team. Please try again.')
    }
  }

  /**
   * Add timeline entry
   */
  async addTimelineEntry(incidentId, entry) {
    try {
      const timelineData = {
        incident_id: incidentId,
        timestamp: entry.timestamp || new Date().toISOString(),
        event_type: entry.type,
        description: entry.description,
        user_id: entry.user_id,
        attachments: entry.attachments || []
      }

      const timelineId = await api.create('bcm.incident.timeline', timelineData)

      // Publish timeline update event
      await eventBus.publish('bcm.incident.timeline_updated', {
        incident_id: incidentId,
        timeline_id: timelineId,
        event_type: entry.type
      })

      return timelineId
    } catch (error) {
      console.error('Failed to add timeline entry:', error)
      throw new Error('Unable to add timeline entry. Please try again.')
    }
  }

  /**
   * Request AI classification for incident
   */
  async requestAIClassification(incidentId, description) {
    try {
      const response = await api.post('/api/ai/classify-incident', {
        incident_id: incidentId,
        description: description,
        context: {
          timestamp: new Date().toISOString(),
          source: 'bcm_incident_management'
        }
      })

      if (response.data.classification) {
        // Update incident with AI classification
        await this.updateIncident(incidentId, {
          classification: response.data.classification.category,
          ai_confidence: response.data.classification.confidence,
          suggested_severity: response.data.classification.severity,
          suggested_response_team: response.data.classification.recommended_team
        })

        // Publish AI classification event
        await eventBus.publish('bcm.incident.ai_classified', {
          incident_id: incidentId,
          classification: response.data.classification,
          timestamp: new Date().toISOString()
        })
      }

      return response.data
    } catch (error) {
      console.error('AI classification request failed:', error)
      // Don't throw error for AI classification failure
      return { error: 'AI classification unavailable' }
    }
  }

  /**
   * Generate incident response plan
   */
  async generateResponsePlan(incidentId) {
    try {
      // Mock incident data for response plan
      const incident = [{
        id: incidentId,
        name: 'Network Infrastructure Failure',
        description: 'Critical network outage affecting main data center',
        severity: 'critical',
        incident_type: 'infrastructure'
      }]
      // const incident = await api.get(`/${this.model}/${incidentId}`)

      if (!incident.length) {
        throw new Error('Incident not found')
      }

      const response = await api.post('/api/ai/generate-response-plan', {
        incident: incident[0],
        context: {
          timestamp: new Date().toISOString(),
          source: 'bcm_incident_management'
        }
      })

      // Publish response plan generated event
      await eventBus.publish('bcm.incident.response_plan_generated', {
        incident_id: incidentId,
        plan_id: response.data.plan_id,
        generated_at: new Date().toISOString()
      })

      return response.data
    } catch (error) {
      console.error('Failed to generate response plan:', error)
      throw new Error('Unable to generate response plan. Please try again.')
    }
  }

  /**
   * Get incident statistics
   */
  async getIncidentStats(timeframe = 'month') {
    try {
      const domain = this._getTimeframeDomain(timeframe)

      // Mock incident statistics data
      const incidents = [
        { severity: 'critical', status: 'open', incident_type: 'infrastructure' },
        { severity: 'high', status: 'in_progress', incident_type: 'security' },
        { severity: 'medium', status: 'resolved', incident_type: 'application' },
        { severity: 'low', status: 'closed', incident_type: 'network' },
        { severity: 'critical', status: 'open', incident_type: 'security' }
      ]
      // const incidents = await api.get(`/${this.model}/stats`)

      return this._calculateStats(incidents)
    } catch (error) {
      console.error('Failed to get incident statistics:', error)
      throw new Error('Unable to retrieve incident statistics.')
    }
  }

  /**
   * Get available response teams
   */
  async getResponseTeams() {
    try {
      // Mock response teams data
      return [
        {
          id: 1,
          name: 'IT Emergency Response',
          description: 'Infrastructure and network emergency response',
          members: ['John Smith', 'Alice Johnson', 'Bob Wilson'],
          specialization: 'Infrastructure',
          availability: 'available'
        },
        {
          id: 2,
          name: 'Security Response Team',
          description: 'Cybersecurity incident response',
          members: ['Sarah Davis', 'Mike Brown', 'Lisa Garcia'],
          specialization: 'Security',
          availability: 'busy'
        },
        {
          id: 3,
          name: 'Application Support',
          description: 'Business application incident response',
          members: ['Tom Anderson', 'Maria Rodriguez'],
          specialization: 'Application',
          availability: 'available'
        }
      ]
      // return await api.get('/bcm.response.team')
    } catch (error) {
      console.error('Failed to get response teams:', error)
      return []
    }
  }

  /**
   * Export incidents to CSV
   */
  async exportIncidents(filters = {}) {
    try {
      const incidents = await this.getIncidents(filters)

      const csvData = incidents.map(incident => ({
        ID: incident.id,
        Title: incident.name,
        Severity: incident.severity,
        Status: incident.status,
        Type: incident.incident_type,
        'Created Date': incident.created_date,
        'Resolved Date': incident.resolved_date || 'N/A',
        Location: incident.location,
        'Impact Level': incident.impact_level
      }))

      return this._generateCSV(csvData)
    } catch (error) {
      console.error('Failed to export incidents:', error)
      throw new Error('Unable to export incidents.')
    }
  }

  // Private methods

  /**
   * Build domain for Odoo search
   */
  _buildDomain(filters) {
    const domain = []

    if (filters.status) {
      if (Array.isArray(filters.status)) {
        domain.push(['status', 'in', filters.status])
      } else {
        domain.push(['status', '=', filters.status])
      }
    }

    if (filters.severity) {
      if (Array.isArray(filters.severity)) {
        domain.push(['severity', 'in', filters.severity])
      } else {
        domain.push(['severity', '=', filters.severity])
      }
    }

    if (filters.incident_type) {
      domain.push(['incident_type', '=', filters.incident_type])
    }

    if (filters.date_from) {
      domain.push(['created_date', '>=', filters.date_from])
    }

    if (filters.date_to) {
      domain.push(['created_date', '<=', filters.date_to])
    }

    if (filters.search) {
      domain.push('|',
        ['name', 'ilike', filters.search],
        ['description', 'ilike', filters.search]
      )
    }

    return domain
  }

  /**
   * Get timeframe domain
   */
  _getTimeframeDomain(timeframe) {
    const now = new Date()
    let startDate

    switch (timeframe) {
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
        break
      case 'quarter':
        startDate = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate())
        break
      case 'year':
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
        break
      default:
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
    }

    return [['created_date', '>=', startDate.toISOString()]]
  }

  /**
   * Calculate incident statistics
   */
  _calculateStats(incidents) {
    const stats = {
      total: incidents.length,
      by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
      by_status: { open: 0, in_progress: 0, escalated: 0, resolved: 0 },
      by_type: {},
      avg_resolution_time: 0,
      trends: {}
    }

    let totalResolutionTime = 0
    let resolvedCount = 0

    incidents.forEach(incident => {
      // Count by severity
      stats.by_severity[incident.severity] = (stats.by_severity[incident.severity] || 0) + 1

      // Count by status
      stats.by_status[incident.status] = (stats.by_status[incident.status] || 0) + 1

      // Count by type
      stats.by_type[incident.incident_type] = (stats.by_type[incident.incident_type] || 0) + 1

      // Calculate resolution time for resolved incidents
      if (incident.status === 'resolved' && incident.resolved_date) {
        const createdDate = new Date(incident.created_date)
        const resolvedDate = new Date(incident.resolved_date)
        const resolutionTime = resolvedDate - createdDate
        totalResolutionTime += resolutionTime
        resolvedCount++
      }
    })

    // Calculate average resolution time in hours
    if (resolvedCount > 0) {
      stats.avg_resolution_time = Math.round(totalResolutionTime / resolvedCount / (1000 * 60 * 60))
    }

    return stats
  }

  /**
   * Validate incident data
   */
  _validateIncidentData(data) {
    if (!data.title || data.title.trim().length === 0) {
      throw new Error('Incident title is required')
    }

    if (!data.description || data.description.trim().length === 0) {
      throw new Error('Incident description is required')
    }

    if (!data.reported_by) {
      throw new Error('Reporter information is required')
    }

    const validSeverities = ['low', 'medium', 'high', 'critical']
    if (data.severity && !validSeverities.includes(data.severity)) {
      throw new Error('Invalid severity level')
    }
  }

  /**
   * Clear cache
   */
  _clearCache() {
    this.cache.clear()
  }

  /**
   * Generate CSV content
   */
  _generateCSV(data) {
    if (!data.length) return ''

    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row =>
        headers.map(field => `"${String(row[field]).replace(/"/g, '""')}"`).join(',')
      )
    ].join('\n')

    return csvContent
  }
}

export default new BCMIncidentService()