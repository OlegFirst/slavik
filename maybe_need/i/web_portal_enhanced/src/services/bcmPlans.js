/**
 * BCM Plans API Service
 * Handles communication with Odoo bcm_plans module
 */

import apiClient from './apiClient'

class BCMPlansService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.plans'
    this.testURL = '/web/dataset/call_kw/bcm.plan.test'
    this.activationURL = '/web/dataset/call_kw/bcm.plan.activation'
  }

  /**
   * Get all plans with statistics
   */
  async getPlans(filters = {}) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'search_read',
          args: [this.buildFilters(filters)],
          kwargs: {
            fields: [
              'name', 'description', 'plan_type', 'version', 'status',
              'owner_id', 'owner_name', 'write_date', 'next_review_date',
              'priority', 'scope', 'approval_date', 'expiry_date'
            ],
            order: 'write_date desc'
          }
        }
      })

      const plans = response.data.result
      const stats = await this.getPlanStatistics()

      return {
        plans,
        stats
      }
    } catch (error) {
      console.error('Failed to get plans:', error)
      throw error
    }
  }

  /**
   * Get plan statistics
   */
  async getPlanStatistics() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'get_plan_statistics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get plan statistics:', error)
      return {
        total: 0,
        approved: 0,
        expiring: 0,
        active: 0
      }
    }
  }

  /**
   * Get single plan by ID
   */
  async getPlan(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'read',
          args: [planId],
          kwargs: {
            fields: [
              'name', 'description', 'plan_type', 'version', 'status',
              'owner_id', 'owner_name', 'priority', 'scope', 'content',
              'objectives', 'procedures', 'resources', 'communication_plan',
              'recovery_strategies', 'roles_responsibilities', 'contact_details',
              'approval_date', 'next_review_date', 'create_date', 'write_date'
            ]
          }
        }
      })
      return response.data.result[0]
    } catch (error) {
      console.error('Failed to get plan:', error)
      throw error
    }
  }

  /**
   * Create new plan
   */
  async createPlan(planData) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'create',
          args: [planData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create plan:', error)
      throw error
    }
  }

  /**
   * Update plan
   */
  async updatePlan(planId, planData) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'write',
          args: [planId, planData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update plan:', error)
      throw error
    }
  }

  /**
   * Delete plan
   */
  async deletePlan(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'unlink',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to delete plan:', error)
      throw error
    }
  }

  /**
   * Create new version of plan
   */
  async createVersion(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'create_version',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create plan version:', error)
      throw error
    }
  }

  /**
   * Duplicate plan
   */
  async duplicatePlan(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'copy',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to duplicate plan:', error)
      throw error
    }
  }

  /**
   * Activate plan
   */
  async activatePlan(planId, activationData = {}) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'activate_plan',
          args: [planId],
          kwargs: activationData
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to activate plan:', error)
      throw error
    }
  }

  /**
   * Deactivate plan
   */
  async deactivatePlan(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'deactivate_plan',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to deactivate plan:', error)
      throw error
    }
  }

  /**
   * Approve plan
   */
  async approvePlan(planId, approvalData = {}) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'approve_plan',
          args: [planId],
          kwargs: approvalData
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to approve plan:', error)
      throw error
    }
  }

  /**
   * Submit plan for review
   */
  async submitForReview(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'submit_for_review',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to submit plan for review:', error)
      throw error
    }
  }

  /**
   * Export plan to PDF/Word
   */
  async exportPlan(planId, format = 'pdf') {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'export_plan',
          args: [planId],
          kwargs: { format }
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
      console.error('Failed to export plan:', error)
      throw error
    }
  }

  /**
   * Get testing schedule
   */
  async getTestingSchedule(filters = {}) {
    try {
      const response = await apiClient.post(this.testURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.test',
          method: 'search_read',
          args: [this.buildTestFilters(filters)],
          kwargs: {
            fields: [
              'plan_id', 'plan_name', 'test_type', 'scheduled_date',
              'duration', 'status', 'participants', 'objectives',
              'facilitator_id', 'facilitator_name', 'results'
            ],
            order: 'scheduled_date asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get testing schedule:', error)
      return []
    }
  }

  /**
   * Schedule plan test
   */
  async scheduleTest(testData) {
    try {
      const response = await apiClient.post(this.testURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.test',
          method: 'create',
          args: [testData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to schedule test:', error)
      throw error
    }
  }

  /**
   * Update test results
   */
  async updateTestResults(testId, results) {
    try {
      const response = await apiClient.post(this.testURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.test',
          method: 'update_results',
          args: [testId, results],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update test results:', error)
      throw error
    }
  }

  /**
   * Get activation history
   */
  async getActivationHistory(limit = 20) {
    try {
      const response = await apiClient.post(this.activationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.activation',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'plan_id', 'plan_name', 'activation_date', 'deactivation_date',
              'reason', 'status', 'activated_by', 'incident_id',
              'effectiveness_rating', 'lessons_learned'
            ],
            limit: limit,
            order: 'activation_date desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get activation history:', error)
      return []
    }
  }

  /**
   * Get plan templates
   */
  async getPlanTemplates() {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.plan.template', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.template',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'description', 'plan_type', 'template_content']
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get plan templates:', error)
      return []
    }
  }

  /**
   * Create plan from template
   */
  async createFromTemplate(templateId, planData) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.plan.template', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.template',
          method: 'create_plan_from_template',
          args: [templateId, planData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create plan from template:', error)
      throw error
    }
  }

  /**
   * Get plan dependencies
   */
  async getPlanDependencies(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'get_dependencies',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get plan dependencies:', error)
      return []
    }
  }

  /**
   * Get plan workflows
   */
  async getPlanWorkflows(planId) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.plan.workflow', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.workflow',
          method: 'search_read',
          args: [['plan_id', '=', planId]],
          kwargs: {
            fields: [
              'name', 'description', 'sequence', 'step_type', 'responsible_id',
              'estimated_duration', 'dependencies', 'status', 'completion_date'
            ],
            order: 'sequence asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get plan workflows:', error)
      return []
    }
  }

  /**
   * Update workflow step
   */
  async updateWorkflowStep(stepId, stepData) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.plan.workflow', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.workflow',
          method: 'write',
          args: [stepId, stepData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update workflow step:', error)
      throw error
    }
  }

  /**
   * Get plan metrics
   */
  async getPlanMetrics(planId) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plans',
          method: 'get_plan_metrics',
          args: [planId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get plan metrics:', error)
      return {}
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
            fields: ['name', 'email', 'phone'],
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
   * Get plan review history
   */
  async getReviewHistory(planId) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.plan.review', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.review',
          method: 'search_read',
          args: [['plan_id', '=', planId]],
          kwargs: {
            fields: [
              'review_date', 'reviewer_id', 'reviewer_name', 'status',
              'comments', 'recommendations', 'next_review_date'
            ],
            order: 'review_date desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get review history:', error)
      return []
    }
  }

  /**
   * Submit plan review
   */
  async submitReview(reviewData) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.plan.review', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan.review',
          method: 'create',
          args: [reviewData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to submit review:', error)
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

    if (filters.plan_type) {
      domain.push(['plan_type', '=', filters.plan_type])
    }

    if (filters.owner_id) {
      domain.push(['owner_id', '=', filters.owner_id])
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
   * Build test filters
   */
  buildTestFilters(filters) {
    const domain = []

    if (filters.status) {
      domain.push(['status', '=', filters.status])
    }

    if (filters.test_type) {
      domain.push(['test_type', '=', filters.test_type])
    }

    if (filters.plan_id) {
      domain.push(['plan_id', '=', filters.plan_id])
    }

    // Only upcoming tests by default
    if (!filters.include_past) {
      domain.push(['scheduled_date', '>=', new Date().toISOString()])
    }

    return domain
  }

  /**
   * Format date for API
   */
  formatDate(date) {
    if (!date) return null
    return new Date(date).toISOString()
  }
}

export default new BCMPlansService()