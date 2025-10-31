import api from './api'
import { odooApi } from './api'
import axios from 'axios'

// Compliance Checker service
const complianceApi = axios.create({
  baseURL: 'http://localhost:8084',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // ======================
  // RISK MANAGEMENT
  // ======================

  // Get all risks with filtering and pagination
  async getRisks(filters = {}) {
    try {
      const params = new URLSearchParams()
      if (filters.severity) params.append('severity', filters.severity)
      if (filters.category) params.append('category', filters.category)
      if (filters.status) params.append('status', filters.status)
      if (filters.owner) params.append('owner', filters.owner)

      const response = await odooApi.get(`/api/bcm_governance/risks?${params}`)
      return response.data
    } catch (error) {
      console.error('Error fetching risks:', error)
      return { risks: [], total: 0 }
    }
  },

  // Create new risk assessment
  async createRisk(riskData) {
    try {
      const response = await odooApi.post('/api/bcm_governance/risks', {
        name: riskData.name,
        description: riskData.description,
        category: riskData.category,
        likelihood: riskData.likelihood,
        impact: riskData.impact,
        inherent_risk_score: riskData.inherent_risk_score,
        residual_risk_score: riskData.residual_risk_score,
        risk_owner: riskData.risk_owner,
        mitigation_controls: riskData.mitigation_controls,
        status: riskData.status || 'identified',
        review_date: riskData.review_date
      })
      return response.data
    } catch (error) {
      console.error('Error creating risk:', error)
      throw error
    }
  },

  // Update existing risk
  async updateRisk(riskId, riskData) {
    try {
      const response = await odooApi.put(`/api/bcm_governance/risks/${riskId}`, riskData)
      return response.data
    } catch (error) {
      console.error('Error updating risk:', error)
      throw error
    }
  },

  // Delete risk
  async deleteRisk(riskId) {
    try {
      await odooApi.delete(`/api/bcm_governance/risks/${riskId}`)
      return { success: true }
    } catch (error) {
      console.error('Error deleting risk:', error)
      throw error
    }
  },

  // Get risk heat map data
  async getRiskHeatMap() {
    try {
      const response = await odooApi.get('/api/bcm_governance/risks/heatmap')
      return response.data
    } catch (error) {
      console.error('Error fetching risk heat map:', error)
      return { matrix: [], risks: [] }
    }
  },

  // Get risk analytics and trends
  async getRiskAnalytics(timeframe = '12m') {
    try {
      const response = await api.get(`/governance/risks/analytics?timeframe=${timeframe}`)
      return response.data
    } catch (error) {
      console.error('Error fetching risk analytics:', error)
      return {
        trends: [],
        metrics: {},
        predictions: []
      }
    }
  },

  // ======================
  // COMPLIANCE MANAGEMENT
  // ======================

  // Get compliance frameworks
  async getComplianceFrameworks() {
    try {
      const response = await complianceApi.get('/api/frameworks')
      return response.data
    } catch (error) {
      console.error('Error fetching compliance frameworks:', error)
      return [
        {
          id: 'iso22301',
          name: 'ISO 22301:2019',
          description: 'Business Continuity Management',
          version: '2019',
          requirements: 45,
          compliance_level: 0
        },
        {
          id: 'nist',
          name: 'NIST Cybersecurity Framework',
          description: 'NIST CSF 2.0',
          version: '2.0',
          requirements: 108,
          compliance_level: 0
        },
        {
          id: 'cobit',
          name: 'COBIT 2019',
          description: 'Control Objectives for IT',
          version: '2019',
          requirements: 89,
          compliance_level: 0
        }
      ]
    }
  },

  // Get compliance status for specific framework
  async getComplianceStatus(frameworkId) {
    try {
      const response = await complianceApi.get(`/api/compliance/${frameworkId}/status`)
      return response.data
    } catch (error) {
      console.error('Error fetching compliance status:', error)
      return {
        framework_id: frameworkId,
        overall_compliance: 0,
        requirements: [],
        gaps: [],
        last_assessment: null
      }
    }
  },

  // Perform compliance gap analysis
  async performGapAnalysis(frameworkId, scope = {}) {
    try {
      const response = await complianceApi.post(`/api/compliance/${frameworkId}/gap-analysis`, {
        scope: scope,
        include_recommendations: true
      })
      return response.data
    } catch (error) {
      console.error('Error performing gap analysis:', error)
      return {
        gaps: [],
        recommendations: [],
        priority_actions: [],
        compliance_score: 0
      }
    }
  },

  // Update compliance requirement status
  async updateComplianceRequirement(frameworkId, requirementId, status, evidence = null) {
    try {
      const response = await complianceApi.put(`/api/compliance/${frameworkId}/requirements/${requirementId}`, {
        status: status,
        evidence: evidence,
        updated_by: 'current_user', // TODO: Get from auth context
        updated_at: new Date().toISOString()
      })
      return response.data
    } catch (error) {
      console.error('Error updating compliance requirement:', error)
      throw error
    }
  },

  // ======================
  // POLICY MANAGEMENT
  // ======================

  // Get all policies with version control
  async getPolicies(filters = {}) {
    try {
      const response = await odooApi.get('/api/bcm_governance/policies', { params: filters })
      return response.data
    } catch (error) {
      console.error('Error fetching policies:', error)
      return { policies: [], total: 0 }
    }
  },

  // Create new policy
  async createPolicy(policyData) {
    try {
      const response = await odooApi.post('/api/bcm_governance/policies', {
        ...policyData,
        version: '1.0',
        status: 'draft',
        created_date: new Date().toISOString()
      })
      return response.data
    } catch (error) {
      console.error('Error creating policy:', error)
      throw error
    }
  },

  // Update policy (creates new version)
  async updatePolicy(policyId, policyData, createNewVersion = true) {
    try {
      const endpoint = createNewVersion
        ? `/api/bcm_governance/policies/${policyId}/new-version`
        : `/api/bcm_governance/policies/${policyId}`

      const response = await odooApi.put(endpoint, policyData)
      return response.data
    } catch (error) {
      console.error('Error updating policy:', error)
      throw error
    }
  },

  // Get policy version history
  async getPolicyVersions(policyId) {
    try {
      const response = await odooApi.get(`/api/bcm_governance/policies/${policyId}/versions`)
      return response.data
    } catch (error) {
      console.error('Error fetching policy versions:', error)
      return []
    }
  },

  // Approve policy
  async approvePolicy(policyId, approvalData) {
    try {
      const response = await odooApi.post(`/api/bcm_governance/policies/${policyId}/approve`, {
        approved_by: approvalData.approved_by,
        approval_date: new Date().toISOString(),
        comments: approvalData.comments,
        effective_date: approvalData.effective_date
      })
      return response.data
    } catch (error) {
      console.error('Error approving policy:', error)
      throw error
    }
  },

  // ======================
  // GOVERNANCE STRUCTURE
  // ======================

  // Get governance structure
  async getGovernanceStructure() {
    try {
      const response = await odooApi.get('/api/bcm_governance/structure')
      return response.data
    } catch (error) {
      console.error('Error fetching governance structure:', error)
      return {
        board: [],
        committees: [],
        roles: [],
        reporting_lines: []
      }
    }
  },

  // Update governance structure
  async updateGovernanceStructure(structureData) {
    try {
      const response = await odooApi.put('/api/bcm_governance/structure', structureData)
      return response.data
    } catch (error) {
      console.error('Error updating governance structure:', error)
      throw error
    }
  },

  // ======================
  // AUDIT TRAIL & DOCUMENTATION
  // ======================

  // Get audit trail
  async getAuditTrail(filters = {}) {
    try {
      const response = await odooApi.get('/api/bcm_governance/audit-trail', { params: filters })
      return response.data
    } catch (error) {
      console.error('Error fetching audit trail:', error)
      return { entries: [], total: 0 }
    }
  },

  // Create audit entry
  async createAuditEntry(entryData) {
    try {
      const response = await odooApi.post('/api/bcm_governance/audit-trail', {
        ...entryData,
        timestamp: new Date().toISOString(),
        user: 'current_user' // TODO: Get from auth context
      })
      return response.data
    } catch (error) {
      console.error('Error creating audit entry:', error)
      throw error
    }
  },

  // ======================
  // REGULATORY REQUIREMENTS
  // ======================

  // Get regulatory requirements
  async getRegulatoryRequirements(jurisdiction = 'all') {
    try {
      const response = await complianceApi.get(`/api/regulatory-requirements?jurisdiction=${jurisdiction}`)
      return response.data
    } catch (error) {
      console.error('Error fetching regulatory requirements:', error)
      return []
    }
  },

  // Track regulatory changes
  async getRegulatoryUpdates(since = null) {
    try {
      const params = since ? `?since=${since}` : ''
      const response = await complianceApi.get(`/api/regulatory-updates${params}`)
      return response.data
    } catch (error) {
      console.error('Error fetching regulatory updates:', error)
      return []
    }
  },

  // ======================
  // RISK APPETITE & TOLERANCE
  // ======================

  // Get risk appetite settings
  async getRiskAppetite() {
    try {
      const response = await odooApi.get('/api/bcm_governance/risk-appetite')
      return response.data
    } catch (error) {
      console.error('Error fetching risk appetite:', error)
      return {
        risk_categories: [],
        tolerance_levels: {},
        thresholds: {}
      }
    }
  },

  // Update risk appetite
  async updateRiskAppetite(appetiteData) {
    try {
      const response = await odooApi.put('/api/bcm_governance/risk-appetite', appetiteData)
      return response.data
    } catch (error) {
      console.error('Error updating risk appetite:', error)
      throw error
    }
  },

  // ======================
  // REPORTING & DASHBOARDS
  // ======================

  // Get executive dashboard data
  async getExecutiveDashboard() {
    try {
      const response = await api.get('/governance/executive-dashboard')
      return response.data
    } catch (error) {
      console.error('Error fetching executive dashboard:', error)
      return {
        risk_summary: {},
        compliance_overview: {},
        key_metrics: {},
        alerts: []
      }
    }
  },

  // Generate governance report
  async generateGovernanceReport(reportType, parameters = {}) {
    try {
      const response = await api.post('/governance/reports/generate', {
        type: reportType,
        parameters: parameters,
        format: 'pdf' // or 'excel', 'html'
      })
      return response.data
    } catch (error) {
      console.error('Error generating report:', error)
      throw error
    }
  },

  // ======================
  // AI INTEGRATION
  // ======================

  // Get AI risk analysis
  async getAIRiskAnalysis(riskData) {
    try {
      const response = await api.post('/ai/risk-analysis', {
        risk_data: riskData,
        analysis_type: 'comprehensive',
        include_recommendations: true
      })
      return response.data
    } catch (error) {
      console.error('Error getting AI risk analysis:', error)
      return {
        analysis: {},
        recommendations: [],
        confidence_score: 0
      }
    }
  },

  // Get AI compliance recommendations
  async getAIComplianceRecommendations(frameworkId, currentStatus) {
    try {
      const response = await api.post('/ai/compliance-recommendations', {
        framework_id: frameworkId,
        current_status: currentStatus,
        priority: 'high'
      })
      return response.data
    } catch (error) {
      console.error('Error getting AI compliance recommendations:', error)
      return {
        recommendations: [],
        priority_actions: [],
        estimated_effort: {}
      }
    }
  },

  // ======================
  // UTILITY FUNCTIONS
  // ======================

  // Calculate risk score
  calculateRiskScore(likelihood, impact) {
    return likelihood * impact
  },

  // Get risk severity level
  getRiskSeverity(riskScore) {
    if (riskScore >= 15) return 'Critical'
    if (riskScore >= 10) return 'High'
    if (riskScore >= 6) return 'Medium'
    if (riskScore >= 3) return 'Low'
    return 'Very Low'
  },

  // Format compliance percentage
  formatCompliancePercentage(compliant, total) {
    if (total === 0) return 0
    return Math.round((compliant / total) * 100)
  }
}