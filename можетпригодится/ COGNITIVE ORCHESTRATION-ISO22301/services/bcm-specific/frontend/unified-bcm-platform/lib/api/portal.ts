// Portal & Client Management API Integration
import { api } from '@/lib/api'

// Portal API Types
export interface PortalAccess {
  id: string
  clientId: string
  userId: string
  role: 'admin' | 'manager' | 'viewer' | 'contributor'
  permissions: string[]
  ssoEnabled: boolean
  mfaEnabled: boolean
  lastAccess?: string
  status: 'active' | 'suspended' | 'pending'
}

export interface ClientPortal {
  id: string
  clientId: string
  name: string
  customDomain?: string
  branding: {
    logo?: string
    primaryColor: string
    secondaryColor: string
    favicon?: string
  }
  modules: PortalModule[]
  settings: PortalSettings
  analytics: PortalAnalytics
}

export interface PortalModule {
  id: string
  name: string
  type: 'dashboard' | 'documents' | 'incidents' | 'training' | 'reports' | 'communication'
  enabled: boolean
  config: Record<string, any>
  permissions: string[]
}

export interface PortalSettings {
  ssoConfig?: {
    provider: 'saml' | 'oauth2' | 'azure-ad' | 'google'
    configuration: Record<string, any>
  }
  mfaConfig?: {
    required: boolean
    methods: ('totp' | 'sms' | 'email')[]
  }
  notificationPreferences: {
    email: boolean
    sms: boolean
    inApp: boolean
    webhooks?: string[]
  }
  dataRetention: {
    days: number
    autoArchive: boolean
  }
}

export interface PortalAnalytics {
  totalUsers: number
  activeUsers: number
  documentsShared: number
  incidentsReported: number
  trainingsCompleted: number
  lastUpdated: string
}

export interface Project {
  id: string
  clientId: string
  name: string
  description: string
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived'
  type: 'implementation' | 'audit' | 'consulting' | 'training' | 'support'
  startDate: string
  endDate?: string
  budget?: number
  team: ProjectMember[]
  milestones: ProjectMilestone[]
  documents: ProjectDocument[]
  progress: number
  risks: ProjectRisk[]
}

export interface ProjectMember {
  userId: string
  name: string
  role: string
  allocation: number // percentage
  avatar?: string
}

export interface ProjectMilestone {
  id: string
  name: string
  description: string
  dueDate: string
  status: 'pending' | 'in_progress' | 'completed' | 'delayed'
  completedDate?: string
  deliverables: string[]
}

export interface ProjectDocument {
  id: string
  name: string
  type: string
  size: number
  uploadedBy: string
  uploadedAt: string
  version: number
  tags: string[]
}

export interface ProjectRisk {
  id: string
  description: string
  impact: 'low' | 'medium' | 'high' | 'critical'
  probability: 'low' | 'medium' | 'high'
  mitigation: string
  status: 'identified' | 'mitigating' | 'resolved'
  owner: string
}

export interface SpecialistProfile {
  id: string
  name: string
  title: string
  specializations: string[]
  certifications: Certification[]
  experience: number // years
  rating: number
  reviewCount: number
  availability: 'available' | 'busy' | 'unavailable'
  hourlyRate?: number
  portfolio: PortfolioItem[]
  skills: Skill[]
}

export interface Certification {
  name: string
  issuer: string
  date: string
  expiryDate?: string
  verificationUrl?: string
}

export interface PortfolioItem {
  id: string
  title: string
  description: string
  client: string
  duration: string
  outcomes: string[]
  technologies: string[]
  images?: string[]
}

export interface Skill {
  name: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  endorsements: number
}

// Portal API Functions
export const portalAPI = {
  // Portal Management
  async getClientPortal(clientId: string): Promise<ClientPortal> {
    const response = await api.get(`/api/portal/client/${clientId}`)
    return response.data
  },

  async updatePortalSettings(clientId: string, settings: Partial<PortalSettings>): Promise<void> {
    await api.patch(`/api/portal/client/${clientId}/settings`, settings)
  },

  async updatePortalBranding(clientId: string, branding: any): Promise<void> {
    await api.patch(`/api/portal/client/${clientId}/branding`, branding)
  },

  // Access Management
  async getPortalAccess(clientId: string): Promise<PortalAccess[]> {
    const response = await api.get(`/api/portal/access/${clientId}`)
    return response.data
  },

  async grantPortalAccess(access: Omit<PortalAccess, 'id'>): Promise<PortalAccess> {
    const response = await api.post('/api/portal/access', access)
    return response.data
  },

  async revokePortalAccess(accessId: string): Promise<void> {
    await api.delete(`/api/portal/access/${accessId}`)
  },

  async updateAccessPermissions(accessId: string, permissions: string[]): Promise<void> {
    await api.patch(`/api/portal/access/${accessId}/permissions`, { permissions })
  },

  // SSO Configuration
  async configureSso(clientId: string, ssoConfig: any): Promise<void> {
    await api.post(`/api/portal/sso/${clientId}`, ssoConfig)
  },

  async testSsoConnection(clientId: string): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`/api/portal/sso/${clientId}/test`)
    return response.data
  },

  // MFA Configuration
  async configureMfa(clientId: string, mfaConfig: any): Promise<void> {
    await api.post(`/api/portal/mfa/${clientId}`, mfaConfig)
  },

  async resetMfa(userId: string): Promise<void> {
    await api.post(`/api/portal/mfa/reset/${userId}`)
  },

  // Portal Content
  async uploadPortalContent(clientId: string, content: FormData): Promise<string> {
    const response = await api.post(`/api/portal/content/${clientId}`, content, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.contentId
  },

  async getPortalContent(clientId: string): Promise<any[]> {
    const response = await api.get(`/api/portal/content/${clientId}`)
    return response.data
  },

  // Portal Analytics
  async getPortalAnalytics(clientId: string, period?: string): Promise<PortalAnalytics> {
    const response = await api.get(`/api/portal/analytics/${clientId}`, {
      params: { period }
    })
    return response.data
  },

  async exportPortalAnalytics(clientId: string, format: 'pdf' | 'excel' | 'csv'): Promise<Blob> {
    const response = await api.get(`/api/portal/analytics/${clientId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  },

  // Project Management
  async getProjects(filters?: any): Promise<Project[]> {
    const response = await api.get('/api/projects', { params: filters })
    return response.data
  },

  async getProject(projectId: string): Promise<Project> {
    const response = await api.get(`/api/projects/${projectId}`)
    return response.data
  },

  async createProject(project: Omit<Project, 'id'>): Promise<Project> {
    const response = await api.post('/api/projects', project)
    return response.data
  },

  async updateProject(projectId: string, updates: Partial<Project>): Promise<void> {
    await api.patch(`/api/projects/${projectId}`, updates)
  },

  async updateProjectProgress(projectId: string, milestoneId: string, progress: number): Promise<void> {
    await api.patch(`/api/projects/${projectId}/milestones/${milestoneId}`, { progress })
  },

  async addProjectDocument(projectId: string, document: FormData): Promise<ProjectDocument> {
    const response = await api.post(`/api/projects/${projectId}/documents`, document, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async addProjectRisk(projectId: string, risk: Omit<ProjectRisk, 'id'>): Promise<ProjectRisk> {
    const response = await api.post(`/api/projects/${projectId}/risks`, risk)
    return response.data
  },

  // Specialist Directory
  async getSpecialists(filters?: any): Promise<SpecialistProfile[]> {
    const response = await api.get('/api/specialists', { params: filters })
    return response.data
  },

  async getSpecialist(specialistId: string): Promise<SpecialistProfile> {
    const response = await api.get(`/api/specialists/${specialistId}`)
    return response.data
  },

  async requestSpecialist(projectId: string, specialistId: string, details: any): Promise<void> {
    await api.post('/api/specialists/request', {
      projectId,
      specialistId,
      ...details
    })
  },

  // Client Communication
  async sendClientNotification(clientId: string, notification: any): Promise<void> {
    await api.post(`/api/portal/notify/${clientId}`, notification)
  },

  async getClientCommunications(clientId: string): Promise<any[]> {
    const response = await api.get(`/api/portal/communications/${clientId}`)
    return response.data
  }
}

// Mock data for development
// Production-ready error handling
export class PortalAPIError extends Error {
  constructor(message: string, public statusCode?: number, public details?: any) {
    super(message)
    this.name = 'PortalAPIError'
  }
}

// Validation schemas
export const validatePortalConfig = (config: Partial<ClientPortal>): string[] => {
  const errors: string[] = []

  if (config.name && config.name.length < 3) {
    errors.push('Portal name must be at least 3 characters')
  }

  if (config.customDomain && !/^[a-z0-9.-]+$/.test(config.customDomain)) {
    errors.push('Invalid domain format')
  }

  if (config.branding?.primaryColor && !/^#[0-9A-F]{6}$/i.test(config.branding.primaryColor)) {
    errors.push('Invalid primary color format')
  }

  return errors
}

// Environment configuration
const PORTAL_API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_PORTAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069',
  timeout: 15000,
  retries: 3
}