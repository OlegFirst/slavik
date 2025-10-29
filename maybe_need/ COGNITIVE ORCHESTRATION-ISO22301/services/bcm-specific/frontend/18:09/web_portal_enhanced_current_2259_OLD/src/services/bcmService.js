/**
 * BCM Service - Combined service for all BCM modules
 * Provides unified access to all BCM functionality
 */

import api from './api'

class BCMService {
  
  // KPI & Reporting
  async getKPIMetrics(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      return await api.searchRead('bcm.kpi', domain, ['name', 'value', 'target', 'status'])
    } catch (error) {
      console.error('Failed to fetch KPI metrics:', error)
      return []
    }
  }

  // Templates Management
  async getTemplates(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      return await api.searchRead('bcm.template', domain, ['name', 'template_type', 'version', 'status'])
    } catch (error) {
      console.error('Failed to fetch templates:', error)
      return []
    }
  }

  // Scenario Hub
  async getScenarios(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      return await api.searchRead('bcm.scenario', domain, ['name', 'scenario_type', 'complexity', 'rating'])
    } catch (error) {
      console.error('Failed to fetch scenarios:', error)
      return []
    }
  }

  // Reporting
  async getReports(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      return await api.searchRead('bcm.report', domain, ['name', 'report_type', 'generate_date', 'status'])
    } catch (error) {
      console.error('Failed to fetch reports:', error)
      return []
    }
  }

  // Training Management
  async getTrainingStats(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      const training = await api.searchRead('bcm.training', domain, ['status', 'completion_rate'])
      
      return {
        total: training.length,
        completed: training.filter(t => t.status === 'completed').length,
        ongoing: training.filter(t => t.status === 'ongoing').length,
        avgCompletion: training.reduce((sum, t) => sum + (t.completion_rate || 0), 0) / training.length || 0
      }
    } catch (error) {
      console.error('Failed to fetch training stats:', error)
      return { total: 0, completed: 0, ongoing: 0, avgCompletion: 0 }
    }
  }

  // Context Management
  async getOrganizationalContext(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      return await api.searchRead('bcm.context', domain, ['name', 'context_type', 'description', 'status'])
    } catch (error) {
      console.error('Failed to fetch organizational context:', error)
      return []
    }
  }

  // Portal Data
  async getPortalData(userId) {
    try {
      return await api.call('bcm.portal.dashboard', 'get_user_dashboard_data', [userId])
    } catch (error) {
      console.error('Failed to fetch portal data:', error)
      return null
    }
  }

  // Governance
  async getGovernanceItems(companyId = null) {
    try {
      const domain = companyId ? [['company_id', '=', companyId]] : []
      return await api.searchRead('bcm.governance', domain, ['name', 'policy_type', 'approval_status', 'review_date'])
    } catch (error) {
      console.error('Failed to fetch governance items:', error)
      return []
    }
  }

  // Overall Dashboard Data
  async getDashboardOverview(companyId = null) {
    try {
      // Parallel requests for all dashboard data
      const [incidents, risks, plans, exercises, audits] = await Promise.all([
        api.searchRead('bcm.incident.management', companyId ? [['company_id', '=', companyId]] : [], ['status']),
        api.searchRead('bcm.risk.management', companyId ? [['company_id', '=', companyId]] : [], ['risk_level']),
        api.searchRead('bcm.plan', companyId ? [['company_id', '=', companyId]] : [], ['status']),
        api.searchRead('bcm.exercise', companyId ? [['company_id', '=', companyId]] : [], ['status']),
        api.searchRead('bcm.audit', companyId ? [['company_id', '=', companyId]] : [], ['status'])
      ])

      return {
        incidents: {
          total: incidents.length,
          open: incidents.filter(i => i.status === 'open').length
        },
        risks: {
          total: risks.length,
          high: risks.filter(r => r.risk_level === 'high').length
        },
        plans: {
          total: plans.length,
          approved: plans.filter(p => p.status === 'approved').length
        },
        exercises: {
          total: exercises.length,
          completed: exercises.filter(e => e.status === 'completed').length
        },
        audits: {
          total: audits.length,
          ongoing: audits.filter(a => a.status === 'ongoing').length
        }
      }
    } catch (error) {
      console.error('Failed to fetch dashboard overview:', error)
      return {
        incidents: { total: 0, open: 0 },
        risks: { total: 0, high: 0 },
        plans: { total: 0, approved: 0 },
        exercises: { total: 0, completed: 0 },
        audits: { total: 0, ongoing: 0 }
      }
    }
  }
}

export default new BCMService()