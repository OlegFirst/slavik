/**
 * BCM Context API Service
 * Handles communication with Odoo bcm_context module
 */

import api from './api'

class BCMContextService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.context'
    this.stakeholderURL = '/web/dataset/call_kw/bcm.stakeholder'
    this.factorURL = '/web/dataset/call_kw/bcm.context.factor'
    this.requirementURL = '/web/dataset/call_kw/bcm.stakeholder.requirement'
  }

  /**
   * Get complete organizational context
   */
  async getOrganizationalContext() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'get_organizational_context',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get organizational context:', error)
      throw error
    }
  }

  /**
   * Get organization profile
   */
  async getOrganizationProfile() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'get_organization_profile',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get organization profile:', error)
      return {}
    }
  }

  /**
   * Update organization profile
   */
  async updateOrganizationProfile(profileData) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'update_organization_profile',
          args: [profileData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update organization profile:', error)
      throw error
    }
  }

  /**
   * Get context metrics and statistics
   */
  async getContextMetrics() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'get_context_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get context metrics:', error)
      return {
        total_stakeholders: 0,
        analysis_complete: 0,
        critical_issues: 0,
        last_update: null
      }
    }
  }

  /**
   * Get all stakeholders
   */
  async getStakeholders(filters = {}) {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'search_read',
          args: [this.buildStakeholderFilters(filters)],
          kwargs: {
            fields: [
              'name', 'role', 'organization', 'type', 'interest_level',
              'influence_level', 'engagement_status', 'contact_info',
              'notes', 'last_contact', 'next_review', 'requirements'
            ],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get stakeholders:', error)
      return []
    }
  }

  /**
   * Get single stakeholder
   */
  async getStakeholder(stakeholderId) {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'read',
          args: [stakeholderId],
          kwargs: {
            fields: [
              'name', 'role', 'organization', 'type', 'interest_level',
              'influence_level', 'engagement_status', 'contact_info',
              'notes', 'requirements', 'expectations', 'communication_preferences'
            ]
          }
        }
      })
      return response.data.result[0]
    } catch (error) {
      console.error('Failed to get stakeholder:', error)
      throw error
    }
  }

  /**
   * Create new stakeholder
   */
  async createStakeholder(stakeholderData) {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'create',
          args: [stakeholderData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create stakeholder:', error)
      throw error
    }
  }

  /**
   * Update stakeholder
   */
  async updateStakeholder(stakeholderId, stakeholderData) {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'write',
          args: [stakeholderId, stakeholderData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update stakeholder:', error)
      throw error
    }
  }

  /**
   * Delete stakeholder
   */
  async deleteStakeholder(stakeholderId) {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'unlink',
          args: [stakeholderId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to delete stakeholder:', error)
      throw error
    }
  }

  /**
   * Get stakeholder matrix data
   */
  async getStakeholderMatrix() {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'get_stakeholder_matrix',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get stakeholder matrix:', error)
      return {}
    }
  }

  /**
   * Update stakeholder engagement
   */
  async updateStakeholderEngagement(stakeholderId, engagementData) {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'update_engagement',
          args: [stakeholderId, engagementData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update stakeholder engagement:', error)
      throw error
    }
  }

  /**
   * Record stakeholder communication
   */
  async recordCommunication(stakeholderId, communicationData) {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.stakeholder.communication', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder.communication',
          method: 'create',
          args: [{
            stakeholder_id: stakeholderId,
            ...communicationData
          }],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to record communication:', error)
      throw error
    }
  }

  /**
   * Get internal factors
   */
  async getInternalFactors() {
    try {
      const response = await api.post(this.factorURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.factor',
          method: 'search_read',
          args: [['factor_type', '=', 'internal']],
          kwargs: {
            fields: ['name', 'description', 'factor_type', 'impact', 'likelihood', 'mitigation'],
            order: 'impact desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get internal factors:', error)
      return []
    }
  }

  /**
   * Get external factors
   */
  async getExternalFactors() {
    try {
      const response = await api.post(this.factorURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.factor',
          method: 'search_read',
          args: [['factor_type', '=', 'external']],
          kwargs: {
            fields: ['name', 'description', 'factor_type', 'impact', 'likelihood', 'mitigation'],
            order: 'impact desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get external factors:', error)
      return []
    }
  }

  /**
   * Create context factor
   */
  async createFactor(factorData) {
    try {
      const response = await api.post(this.factorURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.factor',
          method: 'create',
          args: [factorData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create factor:', error)
      throw error
    }
  }

  /**
   * Update context factor
   */
  async updateFactor(factorId, factorData) {
    try {
      const response = await api.post(this.factorURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.factor',
          method: 'write',
          args: [factorId, factorData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update factor:', error)
      throw error
    }
  }

  /**
   * Delete context factor
   */
  async deleteFactor(factorId) {
    try {
      const response = await api.post(this.factorURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.factor',
          method: 'unlink',
          args: [factorId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to delete factor:', error)
      throw error
    }
  }

  /**
   * Get stakeholder requirements
   */
  async getStakeholderRequirements() {
    try {
      const response = await api.post(this.requirementURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder.requirement',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'stakeholder_id', 'stakeholder_name', 'requirements',
              'expectations', 'compliance_status', 'review_date',
              'responsible_id', 'notes'
            ],
            order: 'stakeholder_name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get stakeholder requirements:', error)
      return []
    }
  }

  /**
   * Create stakeholder requirement
   */
  async createRequirement(requirementData) {
    try {
      const response = await api.post(this.requirementURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder.requirement',
          method: 'create',
          args: [requirementData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create requirement:', error)
      throw error
    }
  }

  /**
   * Update stakeholder requirement
   */
  async updateRequirement(requirementId, requirementData) {
    try {
      const response = await api.post(this.requirementURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder.requirement',
          method: 'write',
          args: [requirementId, requirementData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update requirement:', error)
      throw error
    }
  }

  /**
   * Get BCMS scope definition
   */
  async getBCMSScope() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'get_bcms_scope',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get BCMS scope:', error)
      return {}
    }
  }

  /**
   * Update BCMS scope
   */
  async updateBCMSScope(scopeData) {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'update_bcms_scope',
          args: [scopeData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update BCMS scope:', error)
      throw error
    }
  }

  /**
   * Get context analysis report
   */
  async getContextAnalysis() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'generate_context_analysis',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get context analysis:', error)
      throw error
    }
  }

  /**
   * Get interested parties analysis
   */
  async getInterestedPartiesAnalysis() {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'get_interested_parties_analysis',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get interested parties analysis:', error)
      return {}
    }
  }

  /**
   * Get recent context activities
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
            ['|',
              ['model', '=', 'bcm.context'],
              ['model', '=', 'bcm.stakeholder']
            ]
          ],
          kwargs: {
            fields: ['subject', 'body', 'date', 'model', 'res_id'],
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
   * Export context data
   */
  async exportContextData(format = 'xlsx') {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'export_context_data',
          args: [format],
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
      console.error('Failed to export context data:', error)
      throw error
    }
  }

  /**
   * Import stakeholders from file
   */
  async importStakeholders(fileData, format = 'xlsx') {
    try {
      const response = await api.post(this.stakeholderURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder',
          method: 'import_stakeholders',
          args: [fileData, format],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to import stakeholders:', error)
      throw error
    }
  }

  /**
   * Validate context completeness
   */
  async validateContext() {
    try {
      const response = await api.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context',
          method: 'validate_context_completeness',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to validate context:', error)
      throw error
    }
  }

  /**
   * Get context review schedule
   */
  async getReviewSchedule() {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.context.review', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.review',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'review_type', 'scheduled_date', 'reviewer_id', 'status',
              'findings', 'recommendations', 'next_review_date'
            ],
            order: 'scheduled_date asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get review schedule:', error)
      return []
    }
  }

  /**
   * Schedule context review
   */
  async scheduleReview(reviewData) {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.context.review', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.context.review',
          method: 'create',
          args: [reviewData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to schedule review:', error)
      throw error
    }
  }

  /**
   * Get stakeholder communication history
   */
  async getCommunicationHistory(stakeholderId) {
    try {
      const response = await api.post('/web/dataset/call_kw/bcm.stakeholder.communication', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.stakeholder.communication',
          method: 'search_read',
          args: [['stakeholder_id', '=', stakeholderId]],
          kwargs: {
            fields: [
              'communication_date', 'communication_type', 'subject',
              'content', 'response_received', 'follow_up_required'
            ],
            order: 'communication_date desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get communication history:', error)
      return []
    }
  }

  /**
   * Build stakeholder filters
   */
  buildStakeholderFilters(filters) {
    const domain = []

    if (filters.type) {
      domain.push(['type', '=', filters.type])
    }

    if (filters.influence_level) {
      domain.push(['influence_level', '=', filters.influence_level])
    }

    if (filters.engagement_status) {
      domain.push(['engagement_status', '=', filters.engagement_status])
    }

    if (filters.search) {
      domain.push('|', '|',
        ['name', 'ilike', filters.search],
        ['role', 'ilike', filters.search],
        ['organization', 'ilike', filters.search]
      )
    }

    return domain
  }

  /**
   * Format activities for display
   */
  formatActivities(messages) {
    return messages.map(msg => ({
      id: msg.id,
      title: msg.subject || 'Context Update',
      description: this.stripHTML(msg.body || ''),
      timestamp: new Date(msg.date),
      type: this.getActivityType(msg.model)
    }))
  }

  /**
   * Get activity type based on model
   */
  getActivityType(model) {
    if (model.includes('stakeholder')) return 'stakeholder'
    if (model.includes('context')) return 'context'
    return 'general'
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
   * Calculate stakeholder priority score
   */
  calculateStakeholderPriority(stakeholder) {
    const interestWeight = 0.4
    const influenceWeight = 0.6

    const interestScore = parseInt(stakeholder.interest_level) || 1
    const influenceScore = this.getInfluenceScore(stakeholder.influence_level)

    return (interestScore * interestWeight) + (influenceScore * influenceWeight)
  }

  /**
   * Get numerical influence score
   */
  getInfluenceScore(influenceLevel) {
    const scores = {
      'low': 1,
      'medium': 3,
      'high': 5
    }
    return scores[influenceLevel] || 1
  }

  /**
   * Get stakeholder engagement recommendations
   */
  getEngagementRecommendations(stakeholder) {
    const interest = parseInt(stakeholder.interest_level) || 1
    const influence = this.getInfluenceScore(stakeholder.influence_level)

    if (influence >= 4 && interest >= 4) {
      return {
        strategy: 'Manage Closely',
        actions: ['Regular meetings', 'Detailed reports', 'Direct involvement in decisions']
      }
    } else if (influence >= 4 && interest < 4) {
      return {
        strategy: 'Keep Satisfied',
        actions: ['Keep informed', 'Address concerns promptly', 'Maintain good relationship']
      }
    } else if (influence < 4 && interest >= 4) {
      return {
        strategy: 'Keep Informed',
        actions: ['Regular updates', 'Respond to queries', 'Involve in relevant activities']
      }
    } else {
      return {
        strategy: 'Monitor',
        actions: ['Periodic updates', 'Monitor for changes', 'Minimal effort required']
      }
    }
  }

  /**
   * Validate stakeholder data
   */
  validateStakeholder(stakeholderData) {
    const errors = []

    if (!stakeholderData.name || stakeholderData.name.trim() === '') {
      errors.push('Name is required')
    }

    if (!stakeholderData.type) {
      errors.push('Type is required')
    }

    if (stakeholderData.interest_level && (stakeholderData.interest_level < 1 || stakeholderData.interest_level > 5)) {
      errors.push('Interest level must be between 1 and 5')
    }

    if (stakeholderData.influence_level && !['low', 'medium', 'high'].includes(stakeholderData.influence_level)) {
      errors.push('Influence level must be low, medium, or high')
    }

    return errors
  }
}

export default new BCMContextService()