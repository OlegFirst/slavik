// Odoo BIA Connector - Real Database Integration
// Connects to Odoo 18.0 BCM BIA module

import axios from 'axios'

// Odoo connection configuration
const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069'
const ODOO_DB = process.env.NEXT_PUBLIC_ODOO_DB || 'bcm_platform'

interface OdooSession {
  session_id: string
  uid: number
  username: string
  company_id: number
}

interface OdooBIAProcess {
  id: number
  name: string
  description: string
  criticality: 'low' | 'medium' | 'high' | 'critical'
  industry_id: [number, string]
  annual_revenue_impact: number
  peak_concurrent_users: number
  staff_count: number
  dependency_ids: number[]
  geographical_scope: 'local' | 'regional' | 'national' | 'global'

  // AI-computed fields
  optimized_rto_hours: number
  optimized_rpo_minutes: number
  mtpd_hours: number
  confidence_score: number
  total_financial_impact_24h: number
  hourly_impact_rate: number
  annual_risk_exposure: number
  cascade_risk_score: number
  dependency_depth: number
  impact_breadth: number

  // Metadata
  last_ai_analysis: string
  ai_recommendations: string
  analysis_confidence: 'low' | 'medium' | 'high'
  company_id: [number, string]
}

class OdooBIAConnector {
  private session: OdooSession | null = null
  private axiosInstance = axios.create({
    baseURL: ODOO_URL,
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // Authenticate with Odoo
  async authenticate(login: string = 'admin', password: string = 'admin'): Promise<boolean> {
    try {
      const response = await this.axiosInstance.post('/web/session/authenticate', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          db: ODOO_DB,
          login,
          password
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      if (response.data.result && response.data.result.uid) {
        this.session = {
          session_id: response.data.result.session_id,
          uid: response.data.result.uid,
          username: response.data.result.username,
          company_id: response.data.result.company_id
        }

        // Store session in localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('odoo_session', JSON.stringify(this.session))
        }

        return true
      }

      return false
    } catch (error) {
      console.error('Odoo authentication failed:', error)
      return false
    }
  }

  // Check and restore session
  async checkSession(): Promise<boolean> {
    // Try to restore from localStorage
    if (!this.session && typeof window !== 'undefined') {
      const stored = localStorage.getItem('odoo_session')
      if (stored) {
        this.session = JSON.parse(stored)
      }
    }

    // If no session, try to authenticate
    if (!this.session) {
      return await this.authenticate()
    }

    return true
  }

  // Get all BIA business processes
  async getBIAProcesses(): Promise<OdooBIAProcess[]> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/search_read', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          domain: [],
          fields: [
            'id', 'name', 'description', 'criticality',
            'industry_id', 'annual_revenue_impact', 'peak_concurrent_users',
            'staff_count', 'dependency_ids', 'geographical_scope',
            'optimized_rto_hours', 'optimized_rpo_minutes', 'mtpd_hours',
            'confidence_score', 'total_financial_impact_24h', 'hourly_impact_rate',
            'annual_risk_exposure', 'cascade_risk_score', 'dependency_depth',
            'impact_breadth', 'last_ai_analysis', 'ai_recommendations',
            'analysis_confidence'
          ],
          sort: 'criticality desc, name',
          limit: 100
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      if (response.data.result) {
        return response.data.result.records || []
      }

      return []
    } catch (error) {
      console.error('Failed to fetch BIA processes:', error)
      return []
    }
  }

  // Create new BIA process
  async createBIAProcess(data: Partial<OdooBIAProcess>): Promise<number | null> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/call_kw', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'create',
          args: [{
            name: data.name,
            description: data.description,
            criticality: data.criticality || 'medium',
            annual_revenue_impact: data.annual_revenue_impact || 0,
            peak_concurrent_users: data.peak_concurrent_users || 0,
            staff_count: data.staff_count || 1,
            geographical_scope: data.geographical_scope || 'local'
          }],
          kwargs: {}
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      return response.data.result
    } catch (error) {
      console.error('Failed to create BIA process:', error)
      return null
    }
  }

  // Update BIA process
  async updateBIAProcess(id: number, data: Partial<OdooBIAProcess>): Promise<boolean> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/call_kw', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'write',
          args: [[id], data],
          kwargs: {}
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      return !!response.data.result
    } catch (error) {
      console.error('Failed to update BIA process:', error)
      return false
    }
  }

  // Delete BIA process
  async deleteBIAProcess(id: number): Promise<boolean> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/call_kw', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'unlink',
          args: [[id]],
          kwargs: {}
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      return !!response.data.result
    } catch (error) {
      console.error('Failed to delete BIA process:', error)
      return false
    }
  }

  // Run AI BIA analysis
  async runBIAAnalysis(processId: number): Promise<any> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/call_kw', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'action_compute_bia',
          args: [[processId]],
          kwargs: {}
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      return response.data.result
    } catch (error) {
      console.error('Failed to run BIA analysis:', error)
      return null
    }
  }

  // Get BIA metrics
  async getBIAMetrics(): Promise<any> {
    const processes = await this.getBIAProcesses()

    const metrics = {
      totalFunctions: processes.length,
      criticalFunctions: processes.filter(p => p.criticality === 'critical').length,
      avgRTO: processes.length > 0
        ? processes.reduce((sum, p) => sum + (p.optimized_rto_hours || 0), 0) / processes.length
        : 0,
      totalFinancialRisk: processes.reduce((sum, p) => sum + (p.annual_risk_exposure || 0), 0),
      highRiskFunctions: processes.filter(p => p.cascade_risk_score > 7).length,
      lastAnalysisDate: processes
        .map(p => p.last_ai_analysis)
        .filter(Boolean)
        .sort()
        .reverse()[0] || null
    }

    return metrics
  }

  // Get dependencies for a process
  async getProcessDependencies(processId: number): Promise<any[]> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/call_kw', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.business.process',
          method: 'read',
          args: [[processId], ['dependency_ids']],
          kwargs: {}
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      if (response.data.result && response.data.result[0]) {
        const depIds = response.data.result[0].dependency_ids

        // Fetch dependency details
        if (depIds && depIds.length > 0) {
          const depResponse = await this.axiosInstance.post('/web/dataset/search_read', {
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'bcm.business.process',
              domain: [['id', 'in', depIds]],
              fields: ['id', 'name', 'criticality']
            },
            id: Math.floor(Math.random() * 1000000000)
          })

          return depResponse.data.result?.records || []
        }
      }

      return []
    } catch (error) {
      console.error('Failed to fetch dependencies:', error)
      return []
    }
  }

  // Get industry types
  async getIndustryTypes(): Promise<any[]> {
    await this.checkSession()

    try {
      const response = await this.axiosInstance.post('/web/dataset/search_read', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.industry.type',
          domain: [],
          fields: ['id', 'name', 'code', 'revenue_loss_multiplier',
                  'base_rto_hours', 'base_rpo_minutes'],
          sort: 'sequence, name'
        },
        id: Math.floor(Math.random() * 1000000000)
      })

      return response.data.result?.records || []
    } catch (error) {
      console.error('Failed to fetch industry types:', error)
      return []
    }
  }
}

// Export singleton instance
export const odooBIAConnector = new OdooBIAConnector()

// Export types
export type { OdooBIAProcess, OdooSession }