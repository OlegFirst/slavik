import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const TOKEN_KEY = process.env.NEXT_PUBLIC_TOKEN_STORAGE_KEY || 'bcm_auth_token'

interface ApiError {
  message: string
  status?: number
  code?: string
}

class APIClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem(TOKEN_KEY)
    }

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.token && config.headers) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          this.clearToken()
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login'
          }
        }
        return Promise.reject(this.handleError(error))
      }
    )
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      return {
        message: (error.response.data as any)?.detail || 'An error occurred',
        status: error.response.status,
        code: (error.response.data as any)?.code,
      }
    } else if (error.request) {
      return {
        message: 'No response from server. Please check your connection.',
        code: 'NETWORK_ERROR',
      }
    } else {
      return {
        message: error.message || 'An unexpected error occurred',
      }
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  getToken(): string | null {
    return this.token
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/api/v1/auth/login', {
      email,
      password,
    })
    this.setToken(response.data.token)
    return response.data
  }

  async logout() {
    this.clearToken()
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/v1/auth/me')
    return response.data
  }

  // Dashboard endpoints
  async getDashboardSummary() {
    const response = await this.client.get('/api/v1/dashboard/summary')
    return response.data
  }

  async getDashboardMetrics() {
    const response = await this.client.get('/api/v1/dashboard/metrics')
    return response.data
  }

  async getRecentActivities(limit: number = 10) {
    const response = await this.client.get('/api/v1/dashboard/activities', {
      params: { limit },
    })
    return response.data
  }

  // BIA endpoints
  async getBIAs(params?: { status?: string; limit?: number; offset?: number }) {
    const response = await this.client.get('/api/v1/bia/assessments', { params })
    return response.data
  }

  async getBIA(id: string) {
    const response = await this.client.get(`/api/v1/bia/assessments/${id}`)
    return response.data
  }

  async createBIA(data: any) {
    const response = await this.client.post('/api/v1/bia/assessments', data)
    return response.data
  }

  async updateBIA(id: string, data: any) {
    const response = await this.client.put(`/api/v1/bia/assessments/${id}`, data)
    return response.data
  }

  async deleteBIA(id: string) {
    const response = await this.client.delete(`/api/v1/bia/assessments/${id}`)
    return response.data
  }

  async getBIAProcesses(assessmentId: string) {
    const response = await this.client.get(
      `/api/v1/bia/assessments/${assessmentId}/processes`
    )
    return response.data
  }

  // Risk endpoints
  async getRisks(params?: { status?: string; limit?: number; offset?: number }) {
    const response = await this.client.get('/api/v1/risk/risks', { params })
    return response.data
  }

  async getRisk(id: string) {
    const response = await this.client.get(`/api/v1/risk/risks/${id}`)
    return response.data
  }

  async createRisk(data: any) {
    const response = await this.client.post('/api/v1/risk/risks', data)
    return response.data
  }

  async updateRisk(id: string, data: any) {
    const response = await this.client.put(`/api/v1/risk/risks/${id}`, data)
    return response.data
  }

  async deleteRisk(id: string) {
    const response = await this.client.delete(`/api/v1/risk/risks/${id}`)
    return response.data
  }

  async getRiskMatrix() {
    const response = await this.client.get('/api/v1/risk/matrix')
    return response.data
  }

  // Compliance endpoints
  async getComplianceStatus() {
    const response = await this.client.get('/api/v1/compliance/status')
    return response.data
  }

  async getGapAnalysis() {
    const response = await this.client.get('/api/v1/compliance/gap-analysis')
    return response.data
  }

  // Documents endpoints
  async getDocuments(params?: { type?: string; status?: string }) {
    const response = await this.client.get('/api/v1/documents', { params })
    return response.data
  }

  async getDocument(id: string) {
    const response = await this.client.get(`/api/v1/documents/${id}`)
    return response.data
  }

  // Governance endpoints
  async getDecisions(params?: { status?: string; limit?: number }) {
    const response = await this.client.get('/api/v1/governance/decisions', { params })
    return response.data
  }

  async getDecision(id: string) {
    const response = await this.client.get(`/api/v1/governance/decisions/${id}`)
    return response.data
  }

  async createDecision(data: any) {
    const response = await this.client.post('/api/v1/governance/decisions', data)
    return response.data
  }

  // Admin/Monitoring endpoints
  async getServiceHealth() {
    const response = await this.client.get('/api/v1/admin/health')
    return response.data
  }

  async getSystemMetrics() {
    const response = await this.client.get('/api/v1/admin/metrics')
    return response.data
  }

  async getServiceStatus(serviceName: string) {
    const response = await this.client.get(`/api/v1/admin/services/${serviceName}/status`)
    return response.data
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export class for testing
export { APIClient }
