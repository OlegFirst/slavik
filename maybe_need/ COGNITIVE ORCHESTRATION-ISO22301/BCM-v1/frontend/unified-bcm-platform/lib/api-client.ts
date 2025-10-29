/**
 * BCM Platform API Client
 * Централизованный клиент для всех API сервисов
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8090'
const AI_ORCHESTRATOR_URL = process.env.NEXT_PUBLIC_AI_ORCHESTRATOR_URL || 'http://localhost:8000'
const MODULE_VALIDATOR_URL = process.env.NEXT_PUBLIC_MODULE_VALIDATOR_URL || 'http://localhost:5001'

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

interface AuthTokens {
  access_token: string
  token_type: string
  user: {
    username: string
    id: number
    role: string
  }
}

class BCMApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL
    this.loadToken()
  }

  private loadToken() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('bcm_token')
    }
  }

  private saveToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('bcm_token', token)
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    return headers
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    })

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken()
        throw new Error('Authentication required')
      }
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  private clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('bcm_token')
    }
  }

  // ===========================
  // AUTHENTICATION
  // ===========================

  async login(username: string, password: string): Promise<AuthTokens> {
    const response = await this.request<AuthTokens>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })

    this.saveToken(response.access_token)
    return response
  }

  async logout(): Promise<void> {
    this.clearToken()
  }

  // ===========================
  // MODULES API
  // ===========================

  async getModules() {
    return this.request<any[]>('/api/bcm/modules')
  }

  async getModuleConfig() {
    return this.request<Record<string, any[]>>('/api/bcm/config')
  }

  async updateConfig(configId: number, value: string) {
    return this.request(`/api/bcm/config/${configId}`, {
      method: 'POST',
      body: JSON.stringify({ value }),
    })
  }

  // ===========================
  // TEMPLATES API
  // ===========================

  async getTemplates() {
    return this.request<any[]>('/api/bcm/templates')
  }

  // ===========================
  // CLIENTS API
  // ===========================

  async getClients() {
    return this.request<any[]>('/api/bcm/clients')
  }

  // ===========================
  // USERS API
  // ===========================

  async getUsers() {
    return this.request<any[]>('/api/bcm/users')
  }

  // ===========================
  // HEALTH CHECK
  // ===========================

  async getHealth() {
    return this.request<{
      status: string
      services: Record<string, string>
      timestamp: string
    }>('/api/health')
  }

  // ===========================
  // MICROSERVICES PROXY
  // ===========================

  async callService<T>(
    service: string,
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    return this.request<T>(`/api/services/${service}/${path}`, options)
  }
}

// ===========================
// AI ORCHESTRATOR CLIENT
// ===========================

interface RiskAnalysisRequest {
  id: number
  name: string
  description?: string
  criticality: number
  rto_hours: number
  rpo_hours: number
  dependencies: number[]
  resources_required: string[]
}

interface IncidentAnalysisRequest {
  id?: number
  title: string
  description: string
  category: 'operational' | 'security' | 'natural_disaster' | 'technology' | 'human_error' | 'external_threat'
  severity: 'low' | 'medium' | 'high' | 'critical'
  affected_processes: number[]
  estimated_impact?: number
}

interface NLPQueryRequest {
  query: string
  context?: Record<string, any>
  user_role?: string
}

class AIOrchestatorClient {
  private baseURL: string
  private apiClient: BCMApiClient

  constructor(baseURL = AI_ORCHESTRATOR_URL, apiClient: BCMApiClient) {
    this.baseURL = baseURL
    this.apiClient = apiClient
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...this.apiClient['getHeaders'](),
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`AI Orchestrator Error: ${response.status}`)
    }

    return response.json()
  }

  async analyzeProcessRisk(process: RiskAnalysisRequest) {
    return this.request('/analyze/process-risk', {
      method: 'POST',
      body: JSON.stringify(process),
    })
  }

  async classifyIncident(incident: IncidentAnalysisRequest) {
    return this.request('/analyze/incident', {
      method: 'POST',
      body: JSON.stringify(incident),
    })
  }

  async queryNLP(query: NLPQueryRequest) {
    return this.request('/nlp/query', {
      method: 'POST',
      body: JSON.stringify(query),
    })
  }

  async getHealth() {
    return this.request('/health')
  }

  // ===========================
  // AI AGENTS INTEGRATION
  // ===========================

  async processWithAIAgent(capability: string, data: any, context?: any) {
    return this.request('/ai/process', {
      method: 'POST',
      body: JSON.stringify({
        capability,
        data,
        context,
        priority: 'normal'
      }),
    })
  }

  async getAIAgentsHealth() {
    return this.request('/ai/agents/health')
  }

  async getAIAgentsAnalytics() {
    return this.request('/ai/agents/analytics')
  }

  // ===========================
  // CLAUDE INTEGRATION
  // ===========================

  async claudeAnalyzeChanges(changes: string, context?: any) {
    return this.request('/claude/analyze-changes', {
      method: 'POST',
      body: JSON.stringify({ changes, ...context }),
    })
  }

  async claudeGenerateConfig(requirements: any) {
    return this.request('/claude/generate-config', {
      method: 'POST',
      body: JSON.stringify(requirements),
    })
  }

  async claudeAnalyzeDeployment(deploymentData: any) {
    return this.request('/claude/analyze-deployment', {
      method: 'POST',
      body: JSON.stringify(deploymentData),
    })
  }
}

// ===========================
// MODULE VALIDATOR CLIENT
// ===========================

class ModuleValidatorClient {
  private baseURL: string

  constructor(baseURL = MODULE_VALIDATOR_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`Module Validator Error: ${response.status}`)
    }

    return response.json()
  }

  async validateAllModules() {
    return this.request('/api/modules/validate')
  }

  async listModules() {
    return this.request('/api/modules/list')
  }

  async getModuleDetails(moduleName: string) {
    return this.request(`/api/modules/${moduleName}`)
  }

  async getDependenciesGraph() {
    return this.request('/api/modules/dependencies')
  }

  async fixModuleIssues(moduleName: string) {
    return this.request(`/api/modules/fix/${moduleName}`, {
      method: 'POST',
    })
  }
}

// ===========================
// СОЗДАЕМ ГЛОБАЛЬНЫЕ ЭКЗЕМПЛЯРЫ
// ===========================

// Основной API клиент
export const bcmApiClient = new BCMApiClient()

// AI Orchestrator клиент
export const aiOrchestratorClient = new AIOrchestatorClient(
  AI_ORCHESTRATOR_URL, 
  bcmApiClient
)

// Module Validator клиент  
export const moduleValidatorClient = new ModuleValidatorClient()

// ===========================
// ТИПЫ ДЛЯ ЭКСПОРТА
// ===========================

export type {
  ApiResponse,
  AuthTokens,
  RiskAnalysisRequest,
  IncidentAnalysisRequest,
  NLPQueryRequest,
}

export {
  BCMApiClient,
  AIOrchestatorClient,
  ModuleValidatorClient,
}

// ===========================
// ДОПОЛНИТЕЛЬНЫЕ ЭКСПОРТЫ ДЛЯ СОВМЕСТИМОСТИ
// ===========================

// Экспорт основного клиента как apiClient для совместимости
export const apiClient = bcmApiClient

// Экспорт класса как BCMAPIClient для совместимости
export const BCMAPIClient = BCMApiClient

// Экспорт по умолчанию - основной API клиент
export default bcmApiClient
