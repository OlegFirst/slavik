// Odoo API Client for BCM Platform integration

import { getAuthHeaders } from '@/hooks/useAuth'
import { secureApiRequest, validateUserId, ValidationError } from '@/lib/security/validation'

export class OdooAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public odooError?: any
  ) {
    super(message)
    this.name = 'OdooAPIError'
  }
}

// Odoo API Configuration
const ODOO_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069',
  apiPath: '/web/api/v1',
  timeout: 30000
}

// Base Odoo API client
class OdooClient {
  private baseURL: string

  constructor() {
    this.baseURL = `${ODOO_CONFIG.baseURL}${ODOO_CONFIG.apiPath}`
  }

  async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseURL}${endpoint}`

    try {
      const response = await secureApiRequest(url, {
        ...options,
        headers: {
          ...getAuthHeaders(),
          ...options.headers
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new OdooAPIError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof OdooAPIError) throw error
      if (error instanceof ValidationError) throw error

      throw new OdooAPIError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    }
  }

  async get(endpoint: string, params?: Record<string, any>): Promise<any> {
    const url = new URL(endpoint, this.baseURL)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    return this.request(url.pathname + url.search, { method: 'GET' })
  }

  async post(endpoint: string, data?: any): Promise<any> {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    })
  }

  async put(endpoint: string, data?: any): Promise<any> {
    return this.request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    })
  }

  async patch(endpoint: string, data?: any): Promise<any> {
    return this.request(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    })
  }

  async delete(endpoint: string): Promise<any> {
    return this.request(endpoint, { method: 'DELETE' })
  }
}

// Create singleton instance
export const odooClient = new OdooClient()

// BCM Training Module API
export const bcmTrainingAPI = {
  // Get user learning paths
  async getUserLearningPaths(userId: string): Promise<any[]> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_training/learning_paths`, { user_id: validUserId })
  },

  // Get user achievements
  async getUserAchievements(userId: string): Promise<any[]> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_training/achievements`, { user_id: validUserId })
  },

  // Get training progress
  async getTrainingProgress(userId: string): Promise<any> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_training/progress/${validUserId}`)
  },

  // Enroll in training module
  async enrollInTraining(userId: string, moduleId: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post(`/bcm_training/enroll`, {
      user_id: validUserId,
      module_id: moduleId
    })
  },

  // Update training progress
  async updateProgress(userId: string, moduleId: string, progress: number): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.patch(`/bcm_training/progress`, {
      user_id: validUserId,
      module_id: moduleId,
      progress: Math.min(100, Math.max(0, progress))
    })
  }
}

// BCM Community Module API
export const bcmCommunityAPI = {
  // Get forum posts
  async getForumPosts(params?: {
    category?: string
    limit?: number
    offset?: number
  }): Promise<any> {
    return odooClient.get('/bcm_community/forum/posts', params)
  },

  // Create forum post
  async createForumPost(data: {
    title: string
    content: string
    category: string
    tags?: string[]
  }): Promise<any> {
    return odooClient.post('/bcm_community/forum/posts', data)
  },

  // Get knowledge articles
  async getKnowledgeArticles(params?: {
    category?: string
    type?: string
    limit?: number
    offset?: number
  }): Promise<any> {
    return odooClient.get('/bcm_community/knowledge', params)
  },

  // Get community leaderboard
  async getLeaderboard(period: 'weekly' | 'monthly' | 'all-time' = 'weekly'): Promise<any[]> {
    return odooClient.get(`/bcm_community/leaderboard`, { period })
  }
}

// BCM Clients Module API
export const bcmClientsAPI = {
  // Get client list
  async getClients(params?: {
    search?: string
    status?: string
    limit?: number
    offset?: number
  }): Promise<any> {
    return odooClient.get('/bcm_clients', params)
  },

  // Get client details
  async getClient(clientId: string): Promise<any> {
    return odooClient.get(`/bcm_clients/${clientId}`)
  },

  // Get client projects
  async getClientProjects(clientId: string): Promise<any[]> {
    return odooClient.get(`/bcm_clients/${clientId}/projects`)
  },

  // Create new project
  async createProject(data: {
    client_id: string
    name: string
    description: string
    type: string
    start_date: string
    end_date?: string
    budget?: number
  }): Promise<any> {
    return odooClient.post('/bcm_clients/projects', data)
  },

  // Update project
  async updateProject(projectId: string, data: any): Promise<any> {
    return odooClient.patch(`/bcm_clients/projects/${projectId}`, data)
  }
}

// BCM Web Portal Module API
export const bcmWebPortalAPI = {
  // Get portal configuration
  async getPortalConfig(clientId: string): Promise<any> {
    return odooClient.get(`/bcm_web_portal/config/${clientId}`)
  },

  // Update portal configuration
  async updatePortalConfig(clientId: string, config: any): Promise<any> {
    return odooClient.patch(`/bcm_web_portal/config/${clientId}`, config)
  },

  // Get portal analytics
  async getPortalAnalytics(clientId: string, period?: string): Promise<any> {
    return odooClient.get(`/bcm_web_portal/analytics/${clientId}`, { period })
  },

  // Manage portal users
  async getPortalUsers(clientId: string): Promise<any[]> {
    return odooClient.get(`/bcm_web_portal/users/${clientId}`)
  },

  async addPortalUser(clientId: string, userData: any): Promise<any> {
    return odooClient.post(`/bcm_web_portal/users/${clientId}`, userData)
  },

  async updatePortalUser(clientId: string, userId: string, userData: any): Promise<any> {
    return odooClient.patch(`/bcm_web_portal/users/${clientId}/${userId}`, userData)
  },

  // SSO Configuration
  async configureSso(clientId: string, ssoConfig: any): Promise<any> {
    return odooClient.post(`/bcm_web_portal/sso/${clientId}`, ssoConfig)
  },

  async testSsoConnection(clientId: string): Promise<{ success: boolean; message: string }> {
    return odooClient.post(`/bcm_web_portal/sso/${clientId}/test`)
  }
}

// BCM Content Training Bridge API (from sandbox)
export const bcmGamificationAPI = {
  // Points system
  async getUserPoints(userId: string): Promise<any> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_gamification/points/${validUserId}`)
  },

  async awardPoints(userId: string, points: number, reason: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post('/bcm_gamification/points/award', {
      user_id: validUserId,
      points,
      reason
    })
  },

  // Achievements
  async getUserAchievements(userId: string): Promise<any[]> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_gamification/achievements/${validUserId}`)
  },

  async unlockAchievement(userId: string, achievementId: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post('/bcm_gamification/achievements/unlock', {
      user_id: validUserId,
      achievement_id: achievementId
    })
  },

  // Leaderboard
  async getLeaderboard(period: 'weekly' | 'monthly' | 'all-time' = 'weekly', limit: number = 10): Promise<any[]> {
    return odooClient.get('/bcm_gamification/leaderboard', { period, limit })
  },

  // Learning paths
  async getLearningPaths(userId?: string): Promise<any[]> {
    const params: any = {}
    if (userId) {
      params.user_id = validateUserId(userId)
    }
    return odooClient.get('/bcm_gamification/learning_paths', params)
  },

  async enrollInLearningPath(userId: string, pathId: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post('/bcm_gamification/learning_paths/enroll', {
      user_id: validUserId,
      path_id: pathId
    })
  }
}

// Health check endpoint
export const healthCheck = async (): Promise<{ status: string; modules: string[] }> => {
  return odooClient.get('/health')
}

// Export combined API
export const odooAPI = {
  training: bcmTrainingAPI,
  community: bcmCommunityAPI,
  clients: bcmClientsAPI,
  portal: bcmWebPortalAPI,
  gamification: bcmGamificationAPI,
  healthCheck
}