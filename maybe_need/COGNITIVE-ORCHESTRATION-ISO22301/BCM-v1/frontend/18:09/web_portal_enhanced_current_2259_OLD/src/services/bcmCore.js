/**
 * BCM Core API Service
 * Handles communication with Odoo bcm_core module
 */

import api from './api'

class BCMCoreService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.core'
    this.contextURL = '/web/dataset/call_kw/bcm.context'
  }

  /**
   * Get organization context
   */
  async getOrganizationContext() {
    try {
      const response = await api.post(this.contextURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'description', 'status', 'review_date']
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get organization context:', error)
      throw error
    }
  }

  /**
   * Get BCM metrics and KPIs
   */
  async getBCMMetrics() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.core',
          method: 'get_platform_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get BCM metrics:', error)
      return {
        riskScore: 0,
        complianceLevel: 0,
        avgRTO: 0,
        activeProcesses: 0
      }
    }
  }

  /**
   * Get recent BCM activities
   */
  async getRecentActivities(limit = 10) {
    try {
      const response = await api.post('/web/dataset/call_kw/mail.message', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'mail.message',
          method: 'search_read',
          args: [
            [['model', 'like', 'bcm.%']]
          ],
          kwargs: {
            fields: ['subject', 'body', 'date', 'model', 'author_id'],
            limit: limit,
            order: 'date desc'
          }
        }
      })
      return this.formatActivities(response.data.result)
    } catch (error) {
      console.error('Failed to get recent activities:', error)
      return []
    }
  }

  /**
   * Format activities for display
   */
  formatActivities(messages) {
    return messages.map(msg => ({
      id: msg.id,
      title: msg.subject || 'BCM Activity',
      description: this.stripHTML(msg.body || ''),
      timestamp: new Date(msg.date),
      type: this.getActivityType(msg.model),
      icon: this.getActivityIcon(msg.model)
    }))
  }

  /**
   * Get activity type based on model
   */
  getActivityType(model) {
    if (model.includes('incident')) return 'danger'
    if (model.includes('training')) return 'info'
    if (model.includes('risk')) return 'warning'
    return 'success'
  }

  /**
   * Get activity icon based on model
   */
  getActivityIcon(model) {
    if (model.includes('incident')) return 'fas fa-exclamation-triangle'
    if (model.includes('training')) return 'fas fa-graduation-cap'
    if (model.includes('risk')) return 'fas fa-shield-alt'
    if (model.includes('exercise')) return 'fas fa-dumbbell'
    return 'fas fa-info-circle'
  }

  /**
   * Strip HTML tags from text
   */
  stripHTML(html) {
    const tmp = document.createElement('div')
    tmp.innerHTML = html
    return tmp.textContent || tmp.innerText || ''
  }

  /**
   * Get system health status
   */
  async getSystemHealth() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.core',
          method: 'get_system_health',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get system health:', error)
      return {
        status: 'unknown',
        statusText: 'Status Unknown'
      }
    }
  }

  /**
   * Trigger BIA analysis
   */
  async triggerBIA(processIds = []) {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.bia', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.bia',
          method: 'start_analysis',
          args: [processIds],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to trigger BIA:', error)
      throw error
    }
  }

  /**
   * Create new incident
   */
  async createIncident(incidentData) {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.incident', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident',
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
}

export default new BCMCoreService()