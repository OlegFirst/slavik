/**
 * BCM Risk Management API Service
 * Handles communication with Odoo bcm_risk_management module
 */

import apiClient from './apiClient'

class BCMRiskManagementService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.risk'
    this.mitigationURL = '/web/dataset/call_kw/bcm.risk.mitigation'
    this.assessmentURL = '/web/dataset/call_kw/bcm.risk.assessment'
  }

  /**
   * Get all risks with metrics
   */
  async getRisks(filters = {}) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk',
          method: 'search_read',
          args: [this.buildFilters(filters)],
          kwargs: {
            fields: [
              'name', 'description', 'risk_id', 'category', 'likelihood',
              'impact', 'risk_score', 'status', 'owner_id', 'owner_name',
              'next_review_date', 'mitigation_status', 'severity'
            ],
            order: 'risk_score desc'
          }
        }
      })

      const risks = response.data.result
      const metrics = await this.getRiskMetrics()

      return { risks, metrics }
    } catch (error) {
      console.error('Failed to get risks:', error)
      throw error
    }
  }

  /**
   * Get risk metrics
   */
  async getRiskMetrics() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk',
          method: 'get_risk_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get risk metrics:', error)
      return {
        critical_risks: 0,
        total_risks: 0,
        mitigated_risks: 0,
        overdue: 0
      }
    }
  }

  /**
   * Create new risk
   */
  async createRisk(riskData) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk',
          method: 'create',
          args: [riskData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create risk:', error)
      throw error
    }
  }

  /**
   * Update risk
   */
  async updateRisk(riskId, riskData) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk',
          method: 'write',
          args: [riskId, riskData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update risk:', error)
      throw error
    }
  }

  /**
   * Delete risk
   */
  async deleteRisk(riskId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk',
          method: 'unlink',
          args: [riskId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to delete risk:', error)
      throw error
    }
  }

  /**
   * Duplicate risk
   */
  async duplicateRisk(riskId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk',
          method: 'copy',
          args: [riskId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to duplicate risk:', error)
      throw error
    }
  }

  /**
   * Get mitigation actions
   */
  async getMitigations(filters = {}) {
    try {
      const response = await apiClient.post(this.mitigationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk.mitigation',
          method: 'search_read',
          args: [this.buildMitigationFilters(filters)],
          kwargs: {
            fields: [
              'action', 'risk_id', 'risk_name', 'priority', 'status',
              'completion', 'due_date', 'responsible_id', 'cost',
              'effectiveness'
            ],
            order: 'due_date asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get mitigations:', error)
      return []
    }
  }

  /**
   * Create mitigation
   */
  async createMitigation(mitigationData) {
    try {
      const response = await apiClient.post(this.mitigationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.risk.mitigation',
          method: 'create',
          args: [mitigationData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create mitigation:', error)
      throw error
    }
  }

  /**
   * Get users for assignment
   */
  async getUsers() {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/res.users', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'res.users',
          method: 'search_read',
          args: [['active', '=', true]],
          kwargs: {
            fields: ['name', 'email'],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get users:', error)
      return []
    }
  }

  /**
   * Build search filters
   */
  buildFilters(filters) {
    const domain = []

    if (filters.category) {
      domain.push(['category', '=', filters.category])
    }

    if (filters.status) {
      domain.push(['status', '=', filters.status])
    }

    if (filters.severity) {
      domain.push(['severity', '=', filters.severity])
    }

    return domain
  }

  /**
   * Build mitigation filters
   */
  buildMitigationFilters(filters) {
    const domain = []

    if (filters.status) {
      domain.push(['status', '=', filters.status])
    }

    if (filters.priority) {
      domain.push(['priority', '=', filters.priority])
    }

    return domain
  }
}

export default new BCMRiskManagementService()