import axios, { AxiosInstance, AxiosResponse } from 'axios'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069'
const AI_ORCHESTRATOR_URL = process.env.NEXT_PUBLIC_AI_URL || 'http://localhost:8000'
const BIA_ENGINE_URL = process.env.NEXT_PUBLIC_BIA_URL || 'http://localhost:8082'

// Create API clients
const odooAPI: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

const aiAPI: AxiosInstance = axios.create({
  baseURL: AI_ORCHESTRATOR_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

const biaAPI: AxiosInstance = axios.create({
  baseURL: BIA_ENGINE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interfaces
export interface BCMResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
}

// AI Organs status
export interface AIOrgan {
  id: string
  name: string
  status: 'active' | 'idle' | 'error' | 'maintenance'
  health: number
  lastActivity: string
  responseTime: number
  tokensUsed: number
  capabilities: string[]
}

// System metrics
export interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: number
  timestamp: string
  services: {
    odoo: boolean
    postgres: boolean
    redis: boolean
    ai_orchestrator: boolean
    bia_engine: boolean
  }
}

// BCM Dashboard data
export interface DashboardData {
  kpis: {
    totalRisks: number
    activeBCPs: number
    criticalIncidents: number
    complianceScore: number
  }
  recentActivity: Array<{
    id: string
    type: 'risk' | 'incident' | 'bcp' | 'training' | 'audit'
    title: string
    description: string
    timestamp: string
    severity?: 'low' | 'medium' | 'high' | 'critical'
  }>
  aiOrgans: AIOrgan[]
  systemHealth: SystemMetrics
}

// API Service
export class BCMAPIService {
  // Dashboard data
  async getDashboardData(): Promise<DashboardData> {
    try {
      // Try to get real data from multiple sources
      const [kpis, activity, aiStatus, systemHealth] = await Promise.allSettled([
        this.getKPIs(),
        this.getRecentActivity(),
        this.getAIOrganStatus(),
        this.getSystemHealth(),
      ])

      return {
        kpis: kpis.status === 'fulfilled' ? kpis.value : this.getMockKPIs(),
        recentActivity: activity.status === 'fulfilled' ? activity.value : this.getMockActivity(),
        aiOrgans: aiStatus.status === 'fulfilled' ? aiStatus.value : this.getMockAIOrganStatus(),
        systemHealth: systemHealth.status === 'fulfilled' ? systemHealth.value : this.getMockSystemHealth(),
      }
    } catch (error) {
      console.warn('API unavailable, using mock data:', error)
      return this.getMockDashboardData()
    }
  }

  // KPIs from Odoo
  async getKPIs() {
    try {
      const response = await odooAPI.get('/api/bcm/dashboard/kpis')
      return response.data
    } catch (error) {
      console.warn('Odoo KPIs API unavailable')
      return this.getMockKPIs()
    }
  }

  // Recent activity
  async getRecentActivity() {
    try {
      const response = await odooAPI.get('/api/bcm/dashboard/activity')
      return response.data
    } catch (error) {
      console.warn('Activity API unavailable')
      return this.getMockActivity()
    }
  }

  // AI Organs status
  async getAIOrganStatus(): Promise<AIOrgan[]> {
    try {
      const response = await aiAPI.get('/api/organs/status')
      return this.mapAIOrganResponse(response.data)
    } catch (error) {
      console.warn('AI Orchestrator unavailable')
      return this.getMockAIOrganStatus()
    }
  }

  // System health
  async getSystemHealth(): Promise<SystemMetrics> {
    try {
      const response = await aiAPI.get('/api/system/health')
      return response.data
    } catch (error) {
      console.warn('System health API unavailable')
      return this.getMockSystemHealth()
    }
  }

  // Mock data methods
  private getMockKPIs() {
    return {
      totalRisks: 147,
      activeBCPs: 23,
      criticalIncidents: 3,
      complianceScore: 94,
    }
  }

  private getMockActivity() {
    return [
      {
        id: '1',
        type: 'risk' as const,
        title: 'High-risk vulnerability identified',
        description: 'Critical security vulnerability detected in customer database',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        severity: 'high' as const,
      },
      {
        id: '2',
        type: 'bcp' as const,
        title: 'Business Continuity Plan updated',
        description: 'IT infrastructure recovery plan updated with new procedures',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        severity: 'medium' as const,
      },
      {
        id: '3',
        type: 'incident' as const,
        title: 'Network outage resolved',
        description: 'Data center connectivity restored within RTO',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        severity: 'critical' as const,
      },
    ]
  }

  private getMockAIOrganStatus(): AIOrgan[] {
    const organs = [
      'Governance Brain',
      'Risk Advisor', 
      'Incident Commander',
      'Training Mentor',
      'Audit Inspector',
      'Recovery Planner',
      'Communication Hub',
      'Resource Manager',
      'Performance Monitor',
      'Knowledge Keeper'
    ]

    return organs.map((name, index) => ({
      id: `organ-${index + 1}`,
      name,
      status: Math.random() > 0.2 ? 'active' : Math.random() > 0.5 ? 'idle' : 'error',
      health: Math.floor(Math.random() * 40) + 60,
      lastActivity: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      responseTime: Math.floor(Math.random() * 200) + 50,
      tokensUsed: Math.floor(Math.random() * 10000),
      capabilities: ['analysis', 'recommendations', 'automation'],
    }))
  }

  private getMockSystemHealth(): SystemMetrics {
    return {
      cpu: Math.random() * 30 + 40,
      memory: Math.random() * 40 + 30,
      disk: Math.random() * 50 + 20,
      network: Math.random() * 100 + 50,
      timestamp: new Date().toISOString(),
      services: {
        odoo: Math.random() > 0.1,
        postgres: Math.random() > 0.05,
        redis: Math.random() > 0.05,
        ai_orchestrator: Math.random() > 0.2,
        bia_engine: Math.random() > 0.3,
      },
    }
  }

  private getMockDashboardData(): DashboardData {
    return {
      kpis: this.getMockKPIs(),
      recentActivity: this.getMockActivity(),
      aiOrgans: this.getMockAIOrganStatus(),
      systemHealth: this.getMockSystemHealth(),
    }
  }

  private mapAIOrganResponse(data: any): AIOrgan[] {
    // Map real API response to our interface
    if (Array.isArray(data)) {
      return data.map((organ: any, index: number) => ({
        id: organ.id || `organ-${index + 1}`,
        name: organ.name || `AI Organ ${index + 1}`,
        status: organ.healthy ? 'active' : 'error',
        health: organ.health || Math.floor(Math.random() * 40) + 60,
        lastActivity: organ.lastActivity || new Date().toISOString(),
        responseTime: organ.responseTime || Math.floor(Math.random() * 200) + 50,
        tokensUsed: organ.tokensUsed || Math.floor(Math.random() * 10000),
        capabilities: organ.capabilities || ['analysis', 'recommendations'],
      }))
    }
    return this.getMockAIOrganStatus()
  }
}

// Export singleton instance
export const bcmAPI = new BCMAPIService()

// Health check function
export const checkServiceHealth = async (url: string): Promise<boolean> => {
  try {
    const response = await axios.get(`${url}/health`, { timeout: 3000 })
    return response.status === 200
  } catch {
    return false
  }
}
