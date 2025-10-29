/**
 * BCM BIA API Service
 * Integrates with Odoo bcm_bia module and BIA Engine v2.0
 */

import apiClient from './apiClient'

class BCMBIAService {
  constructor() {
    this.biaURL = '/web/dataset/call_kw/bcm.bia'
    this.processURL = '/web/dataset/call_kw/bcm.business.process'
    this.engineURL = 'http://localhost:8082' // BIA Engine v2.0
  }

  /**
   * Get business processes for BIA
   */
  async getBusinessProcesses() {
    try {
      const response = await apiClient.post(this.processURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'name', 'description', 'criticality',
              'optimized_rto_hours', 'optimized_rpo_minutes',
              'total_financial_impact_24h', 'confidence_score'
            ]
          }
        }
      })

      return this.formatProcesses(response.data.result)
    } catch (error) {
      console.error('Failed to get business processes:', error)
      return this.getMockProcesses()
    }
  }

  /**
   * Format processes for display
   */
  formatProcesses(processes) {
    return processes.map(p => ({
      id: p.id,
      name: p.name,
      description: p.description,
      criticality: p.criticality,
      rto: p.optimized_rto_hours || 0,
      rpo: p.optimized_rpo_minutes || 0,
      financialImpact: p.total_financial_impact_24h || 0,
      aiConfidence: Math.round((p.confidence_score || 0) * 100)
    }))
  }

  /**
   * Get BIA metrics
   */
  async getBIAMetrics() {
    try {
      const response = await apiClient.post(this.biaURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.bia',
          method: 'get_platform_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get BIA metrics:', error)
      return {
        criticalProcesses: 0,
        financialImpact: 0,
        optimizationScore: 0,
        dependencyDepth: 0
      }
    }
  }

  /**
   * Start new BIA analysis
   */
  async startAnalysis(processIds = []) {
    try {
      // Call Odoo BIA module
      const odooResponse = await apiClient.post(this.biaURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.bia',
          method: 'start_analysis',
          args: [processIds],
          kwargs: {}
        }
      })

      // Call BIA Engine v2.0 for ML optimization
      const engineResponse = await fetch(`${this.engineURL}/api/v1/bia/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processes: processIds,
          analysis_type: 'comprehensive'
        })
      })

      const engineData = await engineResponse.json()

      return {
        odoo: odooResponse.data.result,
        aiEngine: engineData
      }
    } catch (error) {
      console.error('Failed to start BIA analysis:', error)
      throw error
    }
  }

  /**
   * Run AI optimization
   */
  async runAIOptimization(processes) {
    try {
      const response = await fetch(`${this.engineURL}/api/v1/bia/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processes: processes.map(p => ({
            id: p.id,
            name: p.name,
            criticality: p.criticality,
            current_rto: p.rto,
            current_rpo: p.rpo,
            financial_impact: p.financialImpact
          }))
        })
      })

      const data = await response.json()
      return {
        recommendations: data.recommendations || [],
        optimizedProcesses: data.processes || []
      }
    } catch (error) {
      console.error('AI optimization failed:', error)
      return { recommendations: [], optimizedProcesses: [] }
    }
  }

  /**
   * Quick industry-specific analysis
   */
  async quickAnalysis(industry) {
    try {
      const response = await fetch(`${this.engineURL}/api/v1/bia/quick-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          industry: industry,
          analysis_scope: 'standard'
        })
      })

      return await response.json()
    } catch (error) {
      console.error('Quick analysis failed:', error)
      return { processes: [], metrics: {} }
    }
  }

  /**
   * Analyze specific process
   */
  async analyzeProcess(processId) {
    try {
      const response = await apiClient.post(this.processURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'run_ai_analysis',
          args: [processId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Process analysis failed:', error)
      throw error
    }
  }

  /**
   * Apply AI recommendation
   */
  async applyRecommendation(recommendationId) {
    try {
      const response = await apiClient.post(this.biaURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.bia',
          method: 'apply_ai_recommendation',
          args: [recommendationId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to apply recommendation:', error)
      throw error
    }
  }

  /**
   * Get AI recommendations
   */
  async getAIRecommendations() {
    try {
      const response = await fetch(`${this.engineURL}/api/v1/bia/recommendations`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get AI recommendations:', error)
      return []
    }
  }

  /**
   * Mock data for fallback
   */
  getMockProcesses() {
    return [
      {
        id: 1,
        name: 'Payment Processing',
        description: 'Core payment system operations',
        criticality: 'Critical',
        rto: 2,
        rpo: 15,
        financialImpact: 50000,
        aiConfidence: 95
      },
      {
        id: 2,
        name: 'Customer Support',
        description: '24/7 customer service operations',
        criticality: 'High',
        rto: 4,
        rpo: 60,
        financialImpact: 15000,
        aiConfidence: 88
      }
    ]
  }
}

export default new BCMBIAService()