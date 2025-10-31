// Progressive API Client with Mock Fallback

import { ODOO_ENDPOINTS, transformOdooToFrontend, transformFrontendToOdoo } from './odoo-api-mapper'

interface APIConfig {
  baseURL: string
  useRealAPI: boolean
  fallbackToMock: boolean
  timeout: number
  retryAttempts: number
}

interface APIResponse<T> {
  data: T
  status: number
  source: 'real' | 'mock'
  timestamp: string
}

class BCMAPIClient {
  private config: APIConfig
  private authToken: string | null = null

  constructor(config?: Partial<APIConfig>) {
    this.config = {
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069',
      useRealAPI: process.env.NEXT_PUBLIC_USE_REAL_API === 'true',
      fallbackToMock: true,
      timeout: 10000,
      retryAttempts: 3,
      ...config
    }
  }

  // Authentication
  async authenticate(username: string, password: string): Promise<boolean> {
    if (!this.config.useRealAPI) {
      // Mock authentication
      this.authToken = 'mock-jwt-token'
      return true
    }

    try {
      const response = await fetch(`${this.config.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })

      if (response.ok) {
        const data = await response.json()
        this.authToken = data.token
        return true
      }
      return false
    } catch (error) {
      console.error('Authentication failed:', error)
      if (this.config.fallbackToMock) {
        this.authToken = 'mock-jwt-token'
        return true
      }
      return false
    }
  }

  // Generic request method with fallback
  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    mockDataProvider?: () => T
  ): Promise<APIResponse<T>> {
    const endpointConfig = ODOO_ENDPOINTS.find(e => e.endpoint === endpoint)

    if (!this.config.useRealAPI || !endpointConfig?.realImplemented) {
      // Use mock data
      if (mockDataProvider) {
        return {
          data: mockDataProvider(),
          status: 200,
          source: 'mock',
          timestamp: new Date().toISOString()
        }
      }
      throw new Error(`No mock data provider for endpoint: ${endpoint}`)
    }

    // Try real API
    let lastError: Error | null = null
    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const response = await fetch(`${this.config.baseURL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.authToken}`,
            ...options.headers
          },
          signal: AbortSignal.timeout(this.config.timeout)
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        return {
          data,
          status: response.status,
          source: 'real',
          timestamp: new Date().toISOString()
        }
      } catch (error) {
        lastError = error as Error
        console.warn(`API attempt ${attempt} failed:`, error)

        if (attempt < this.config.retryAttempts) {
          // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000))
        }
      }
    }

    // Fallback to mock if enabled
    if (this.config.fallbackToMock && mockDataProvider) {
      console.warn('Falling back to mock data after API failure')
      return {
        data: mockDataProvider(),
        status: 200,
        source: 'mock',
        timestamp: new Date().toISOString()
      }
    }

    throw lastError || new Error('API request failed')
  }

  // Risk Management API
  async getRisks(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/bcm/risks', { method: 'GET' }, () => [
      {
        id: '1',
        title: 'Supply Chain Disruption',
        description: 'Risk of supply chain failure',
        category: 'operational',
        probability: 3,
        impact: 4,
        score: 12,
        status: 'active',
        owner: 'John Smith',
        treatment: 'Diversify suppliers',
        createdAt: new Date().toISOString()
      },
      {
        id: '2',
        title: 'Cyber Security Breach',
        description: 'Risk of data breach or ransomware',
        category: 'technological',
        probability: 4,
        impact: 5,
        score: 20,
        status: 'active',
        owner: 'Jane Doe',
        treatment: 'Implement advanced security measures',
        createdAt: new Date().toISOString()
      }
    ])
  }

  async createRisk(risk: any): Promise<APIResponse<any>> {
    return this.request(
      '/api/v1/bcm/risks',
      {
        method: 'POST',
        body: JSON.stringify(transformFrontendToOdoo(risk, 'Risk'))
      },
      () => ({ ...risk, id: Date.now().toString() })
    )
  }

  async updateRisk(id: string, updates: any): Promise<APIResponse<any>> {
    return this.request(
      `/api/v1/bcm/risks/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(transformFrontendToOdoo(updates, 'Risk'))
      },
      () => ({ id, ...updates })
    )
  }

  // BIA API
  async getBIAResults(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/bcm/bia/results', { method: 'GET' }, () => [
      {
        id: '1',
        functionId: 'func-1',
        functionName: 'Customer Service',
        criticality: 'critical',
        rto: 4,
        rpo: 2,
        financialImpact: 50000,
        dependencies: ['IT Systems', 'Call Center'],
        assessmentDate: new Date().toISOString()
      },
      {
        id: '2',
        functionId: 'func-2',
        functionName: 'Manufacturing',
        criticality: 'critical',
        rto: 8,
        rpo: 4,
        financialImpact: 100000,
        dependencies: ['Supply Chain', 'Equipment'],
        assessmentDate: new Date().toISOString()
      }
    ])
  }

  async getCriticalFunctions(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/bcm/critical-functions', { method: 'GET' }, () => [
      {
        id: '1',
        name: 'Customer Service',
        department: 'Operations',
        criticality: 'critical',
        description: 'Customer support and service delivery'
      },
      {
        id: '2',
        name: 'Manufacturing',
        department: 'Production',
        criticality: 'critical',
        description: 'Core manufacturing operations'
      }
    ])
  }

  // AI Control API
  async getAIOrgans(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/ai/organs', { method: 'GET' }, () => [
      {
        id: 'governance-brain',
        name: 'Governance Brain',
        category: 'strategic',
        status: 'active',
        health: 95,
        lastActivity: new Date(Date.now() - 60000).toISOString(),
        responseTime: 250,
        tokensUsed: 12500,
        capabilities: ['strategy', 'governance', 'policy']
      },
      {
        id: 'risk-advisor',
        name: 'Risk Advisor',
        category: 'analysis',
        status: 'active',
        health: 88,
        lastActivity: new Date(Date.now() - 120000).toISOString(),
        responseTime: 320,
        tokensUsed: 8900,
        capabilities: ['risk-analysis', 'prediction', 'monte-carlo']
      }
    ])
  }

  async controlAIOrgan(organId: string, action: 'start' | 'stop' | 'restart'): Promise<APIResponse<any>> {
    return this.request(
      `/api/v1/ai/organs/${organId}/control`,
      {
        method: 'POST',
        body: JSON.stringify({ action })
      },
      () => ({ organId, action, status: 'success' })
    )
  }

  async getAIDecisions(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/ai/decisions', { method: 'GET' }, () => [
      {
        id: '1',
        organId: 'risk-advisor',
        decision: 'Supply chain risk elevated',
        confidence: 0.92,
        context: 'Risk Analysis',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        organId: 'governance-brain',
        decision: 'Policy update required',
        confidence: 0.88,
        context: 'Governance',
        timestamp: new Date().toISOString()
      }
    ])
  }

  // BCM Core API (not yet implemented)
  async getOrganizations(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/bcm/organizations', { method: 'GET' }, () => [
      {
        id: '1',
        name: 'Acme Corporation',
        industry: 'Manufacturing',
        size: 'large',
        bcmMaturity: 3
      }
    ])
  }

  async getBusinessUnits(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/bcm/business-units', { method: 'GET' }, () => [
      {
        id: '1',
        name: 'Operations',
        parentId: null,
        level: 1,
        headCount: 150
      },
      {
        id: '2',
        name: 'IT Department',
        parentId: '1',
        level: 2,
        headCount: 50
      }
    ])
  }

  // Incident Management API
  async getIncidents(): Promise<APIResponse<any[]>> {
    return this.request('/api/v1/bcm/incidents', { method: 'GET' }, () => [
      {
        id: '1',
        title: 'Server Outage',
        severity: 'high',
        status: 'active',
        assignedTo: 'IT Team',
        createdAt: new Date().toISOString()
      },
      {
        id: '2',
        title: 'Security Alert',
        severity: 'medium',
        status: 'investigating',
        assignedTo: 'Security Team',
        createdAt: new Date().toISOString()
      }
    ])
  }

  // Utility methods
  isUsingRealAPI(): boolean {
    return this.config.useRealAPI
  }

  setUseRealAPI(use: boolean): void {
    this.config.useRealAPI = use
  }

  getAPIStatus(): {
    mode: 'real' | 'mock' | 'hybrid'
    authenticated: boolean
    baseURL: string
  } {
    return {
      mode: this.config.useRealAPI ? 'real' : 'mock',
      authenticated: !!this.authToken,
      baseURL: this.config.baseURL
    }
  }

  // Convenience methods for common HTTP operations
  async get<T>(endpoint: string, mockDataProvider?: () => T): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' }, mockDataProvider)
  }

  async post<T>(endpoint: string, data?: any, mockDataProvider?: () => T): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    }, mockDataProvider)
  }

  async patch<T>(endpoint: string, data?: any, mockDataProvider?: () => T): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    }, mockDataProvider)
  }

  async put<T>(endpoint: string, data?: any, mockDataProvider?: () => T): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    }, mockDataProvider)
  }

  async delete<T>(endpoint: string, mockDataProvider?: () => T): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' }, mockDataProvider)
  }

  // Add placeholder properties that other components are expecting
  templates = {
    list: () => this.get('/api/v1/bcm/templates', () => []),
    create: (template: any) => this.post('/api/v1/bcm/templates', template, () => ({ ...template, id: Date.now().toString() })),
    update: (id: string, template: any) => this.patch(`/api/v1/bcm/templates/${id}`, template, () => ({ ...template, id }))
  }

  training = {
    courses: () => this.get('/api/v1/bcm/training/courses', () => []),
    enrollments: () => this.get('/api/v1/bcm/training/enrollments', () => []),
    progress: () => this.get('/api/v1/bcm/training/progress', () => []),
    certificates: () => this.get('/api/v1/bcm/training/certificates', () => [])
  }

  // Health check
  async healthCheck(): Promise<{ status: 'healthy' | 'degraded' | 'offline', services: any[] }> {
    const services = []

    // Check Odoo
    try {
      const response = await fetch(`${this.config.baseURL}/health`, { method: 'GET' })
      services.push({
        name: 'Odoo',
        status: response.ok ? 'healthy' : 'degraded',
        responseTime: 0
      })
    } catch {
      services.push({ name: 'Odoo', status: 'offline' })
    }

    // Check AI Service
    try {
      const response = await fetch('http://localhost:8000/health', { method: 'GET' })
      services.push({
        name: 'AI Service',
        status: response.ok ? 'healthy' : 'degraded'
      })
    } catch {
      services.push({ name: 'AI Service', status: 'offline' })
    }

    const overallStatus = services.every(s => s.status === 'healthy') ? 'healthy' :
                          services.some(s => s.status === 'healthy') ? 'degraded' : 'offline'

    return { status: overallStatus, services }
  }
}

// Singleton instance
let apiClientInstance: BCMAPIClient | null = null

export function getAPIClient(): BCMAPIClient {
  if (!apiClientInstance) {
    apiClientInstance = new BCMAPIClient()
  }
  return apiClientInstance
}

// Export the class for manual instantiation
export { BCMAPIClient }

// Export for direct use
export const apiClient = getAPIClient()

// React Query integration helpers
export function createQueryKey(endpoint: string, params?: any): string[] {
  return params ? [endpoint, params] : [endpoint]
}

export async function queryFetcher<T>(endpoint: string): Promise<T> {
  const response = await apiClient.request<T>(endpoint, { method: 'GET' })
  return response.data
}