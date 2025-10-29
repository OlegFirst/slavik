// Unified Authentication Bridge for Enterprise BCM Platform
// Integrates: Keycloak (SSO) + Odoo (Business) + Supabase (AI/Real-time)
// WITH FALLBACK MODES for development and offline usage

import React from 'react'
import { initializePlatform, demoUser, isServiceOnline, getPlatformConfig } from './service-health-check'

// Authentication providers configuration
export const AUTH_CONFIG = {
  keycloak: {
    url: process.env.NEXT_PUBLIC_KEYCLOAK_URL || 'http://localhost:8080',
    realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM || 'bcm-platform',
    clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || 'bcm-frontend'
  },
  odoo: {
    url: process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069',
    database: process.env.NEXT_PUBLIC_ODOO_DB || 'bcm_db'
  },
  supabase: {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
  },
  redis: {
    url: process.env.NEXT_PUBLIC_REDIS_URL || 'redis://localhost:6379'
  }
}

// User roles and permissions
export type UserRole = 'super_admin' | 'org_admin' | 'manager' | 'analyst' | 'viewer'

export interface UnifiedUser {
  // Core identity (compatible with centralized bcm_users)
  id: string
  email: string
  firstName: string
  lastName: string
  fullName?: string

  // Business context (integrated with bcm_companies)
  companyId: number
  companyName: string
  role: UserRole
  departments?: string[]

  // Session management
  sessionId: string
  accessToken?: string
  refreshToken?: string
  expiresAt: Date

  // Permissions and features
  permissions: string[]
  modules?: string[]

  // Additional context
  source: string // 'keycloak', 'supabase', 'demo', etc.
  avatarUrl?: string
  theme?: string
  language?: string
  timezone?: string
}

export interface AuthTokens {
  keycloakToken: string
  odooSessionId: string
  supabaseToken: string
  unifiedToken: string
}

// Import centralized database clients
import { centralizedBCM, centralizedSupabase } from '@/lib/supabase/centralized-client'
import { postgresClient } from '@/lib/database/postgres-client'
import { unifiedDB } from '@/lib/database/unified-database-manager'

// Use centralized clients
const supabase = centralizedSupabase

// Unified Authentication Bridge Class
export class UnifiedAuthBridge {
  private user: UnifiedUser | null = null
  private tokens: AuthTokens | null = null
  private listeners: ((user: UnifiedUser | null) => void)[] = []

  // Initialize platform and check services
  async initialize() {
    try {
      const { health, config } = await initializePlatform()
      console.log('Platform initialized:', config)
      return { health, config }
    } catch (error) {
      console.error('Platform initialization failed:', error)
      return null
    }
  }

  // 1. Smart Login (auto-detects available services)
  async login(email: string, password: string): Promise<UnifiedUser> {
    const config = getPlatformConfig()

    if (!config) {
      // Fallback to demo mode
      return this.loginDemo(email, password)
    }

    switch (config.authMode) {
      case 'keycloak':
        return this.loginWithKeycloak(email, password)
      case 'postgres':
        return this.loginWithPostgreSQL(email, password)
      case 'demo':
        return this.loginDemo(email, password)
      case 'offline':
        return this.loginOffline(email, password)
      default:
        // Try PostgreSQL first, fallback to demo
        try {
          return await this.loginWithPostgreSQL(email, password)
        } catch (error) {
          console.log('PostgreSQL login failed, using demo mode:', error)
          return this.loginDemo(email, password)
        }
    }
  }

  // 2. Keycloak SSO Login
  async loginWithKeycloak(email: string, password: string): Promise<UnifiedUser> {
    try {
      // Step 1: Authenticate with Keycloak
      const keycloakResponse = await fetch(`${AUTH_CONFIG.keycloak.url}/realms/${AUTH_CONFIG.keycloak.realm}/protocol/openid-connect/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'password',
          client_id: AUTH_CONFIG.keycloak.clientId,
          username: email,
          password: password
        })
      })

      if (!keycloakResponse.ok) {
        throw new Error('Keycloak authentication failed')
      }

      const keycloakData = await keycloakResponse.json()

      // Step 2: Get user info from Keycloak
      const userInfoResponse = await fetch(`${AUTH_CONFIG.keycloak.url}/realms/${AUTH_CONFIG.keycloak.realm}/protocol/openid-connect/userinfo`, {
        headers: {
          'Authorization': `Bearer ${keycloakData.access_token}`
        }
      })

      const keycloakUser = await userInfoResponse.json()

      // Step 3: Authenticate with Odoo using Keycloak token
      const odooUser = await this.authenticateWithOdoo(keycloakUser.email, keycloakData.access_token)

      // Step 4: Authenticate with Supabase
      const supabaseUser = await this.authenticateWithSupabase(keycloakUser.email, keycloakData.access_token)

      // Step 5: Create unified user session
      const unifiedUser = await this.createUnifiedSession({
        keycloakUser,
        keycloakData,
        odooUser,
        supabaseUser
      })

      this.user = unifiedUser
      this.tokens = {
        keycloakToken: keycloakData.access_token,
        odooSessionId: odooUser.session_id,
        supabaseToken: supabaseUser.access_token,
        unifiedToken: await this.generateUnifiedToken(unifiedUser)
      }

      // Notify listeners
      this.notifyListeners(unifiedUser)

      return unifiedUser

    } catch (error) {
      console.error('Keycloak authentication failed:', error)
      // Fallback to demo mode
      return this.loginDemo(email, password)
    }
  }

  // 2. PostgreSQL/Odoo Login
  async loginWithPostgreSQL(email: string, password: string): Promise<UnifiedUser> {
    try {
      console.log('🐘 PostgreSQL/Odoo Authentication')

      // Authenticate with Odoo/PostgreSQL backend
      const sessionInfo = await postgresClient.authenticate({
        database: AUTH_CONFIG.odoo.database,
        username: email,
        password: password
      })

      // Get user details from PostgreSQL via Odoo
      const userDetails = await postgresClient.rpcCall({
        model: 'res.users',
        method: 'read',
        args: [sessionInfo.user_id],
        kwargs: {
          fields: [
            'name', 'login', 'email', 'active', 'company_id',
            'company_ids', 'groups_id', 'image_1920', 'lang',
            'tz', 'last_login', 'create_date'
          ]
        }
      })

      const user = userDetails[0]

      // Get company information
      const companyInfo = await postgresClient.rpcCall({
        model: 'res.company',
        method: 'read',
        args: [user.company_id[0]],
        kwargs: {
          fields: ['name', 'email', 'phone', 'country_id']
        }
      })

      const company = companyInfo[0]

      // Get user permissions/groups
      const userGroups = await postgresClient.rpcCall({
        model: 'res.groups',
        method: 'read',
        args: [user.groups_id],
        kwargs: {
          fields: ['name', 'category_id', 'implied_ids']
        }
      })

      // Map to UnifiedUser format
      const unifiedUser: UnifiedUser = {
        id: sessionInfo.user_id.toString(),
        email: user.email || user.login,
        firstName: user.name.split(' ')[0] || 'User',
        lastName: user.name.split(' ').slice(1).join(' ') || '',
        fullName: user.name,
        companyId: user.company_id[0],
        companyName: company.name,
        role: this.mapOdooGroupsToRole(userGroups),
        permissions: this.mapOdooGroupsToPermissions(userGroups),
        sessionId: sessionInfo.session_id,
        accessToken: sessionInfo.session_id,
        expiresAt: new Date(Date.now() + 8 * 60 * 60 * 1000), // 8 hours
        source: 'postgres-odoo',
        avatarUrl: user.image_1920 ? `data:image/png;base64,${user.image_1920}` : undefined,
        theme: 'light',
        language: user.lang || 'en',
        timezone: user.tz || 'UTC'
      }

      // Store session in Redis
      await unifiedDB.setSession(sessionInfo.session_id, {
        user_id: sessionInfo.user_id,
        company_id: sessionInfo.company_id,
        login_time: new Date(),
        user_context: sessionInfo.user_context
      })

      // Store user in Supabase for AI features (if not exists)
      try {
        await centralizedBCM.getUser(sessionInfo.user_id.toString()) ||
        await centralizedSupabase.from('bcm_users').upsert({
          id: sessionInfo.user_id.toString(),
          email: user.email || user.login,
          full_name: user.name,
          company_id: user.company_id[0],
          role: this.mapOdooGroupsToRole(userGroups),
          theme: 'light',
          language: user.lang || 'en',
          timezone: user.tz || 'UTC',
          last_login: new Date().toISOString()
        }, { onConflict: 'id' })
      } catch (supabaseError) {
        console.warn('Supabase sync failed (non-critical):', supabaseError)
      }

      this.user = unifiedUser
      this.tokens = {
        keycloakToken: '',
        odooSessionId: sessionInfo.session_id,
        supabaseToken: '',
        unifiedToken: await this.generateUnifiedToken(unifiedUser)
      }

      this.notifyListeners(unifiedUser)
      return unifiedUser

    } catch (error) {
      console.error('PostgreSQL login failed:', error)
      throw new Error('PostgreSQL authentication failed')
    }
  }

  // 3. Demo Mode Login (for development)
  async loginDemo(email: string, password: string): Promise<UnifiedUser> {
    console.log('🎭 Demo Mode Authentication')

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Accept any credentials in demo mode
    if (email && password) {
      const user = {
        ...demoUser,
        email: email,
        firstName: email.split('@')[0].split('.')[0] || 'Demo',
        lastName: email.split('@')[0].split('.')[1] || 'User'
      }

      this.user = user
      this.tokens = {
        keycloakToken: 'demo-keycloak-token',
        odooSessionId: 'demo-odoo-session',
        supabaseToken: 'demo-supabase-token',
        unifiedToken: 'demo-unified-token'
      }

      this.notifyListeners(user)
      return user
    } else {
      throw new Error('Please provide email and password')
    }
  }

  // 4. Offline Mode Login (cached credentials)
  async loginOffline(email: string, password: string): Promise<UnifiedUser> {
    console.log('📴 Offline Mode Authentication')

    // Check for cached credentials
    const cachedUser = localStorage.getItem('bcm_offline_user')
    if (cachedUser) {
      const user = JSON.parse(cachedUser)
      this.user = user
      this.notifyListeners(user)
      return user
    }

    // If no cached user, create demo user and cache it
    const user = await this.loginDemo(email, password)
    localStorage.setItem('bcm_offline_user', JSON.stringify(user))
    return user
  }

  // 2. Odoo Business Authentication
  private async authenticateWithOdoo(email: string, keycloakToken: string) {
    const response = await fetch(`${AUTH_CONFIG.odoo.url}/web/session/authenticate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${keycloakToken}`
      },
      body: JSON.stringify({
        db: AUTH_CONFIG.odoo.database,
        login: email,
        password: keycloakToken // Use Keycloak token as password for SSO
      })
    })

    if (!response.ok) {
      throw new Error('Odoo authentication failed')
    }

    return response.json()
  }

  // 3. Supabase AI Authentication
  private async authenticateWithSupabase(email: string, keycloakToken: string) {
    // Custom Supabase auth with Keycloak integration
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password: keycloakToken // Custom integration
    })

    if (error) {
      // Fallback: create/update user in Supabase with Keycloak context
      const { data: userData, error: createError } = await supabase.auth.signUp({
        email,
        password: keycloakToken,
        options: {
          data: {
            provider: 'keycloak',
            keycloak_token: keycloakToken
          }
        }
      })

      if (createError) {
        throw new Error('Supabase authentication failed')
      }

      return userData.user!
    }

    return data.user!
  }

  // 4. Create unified session
  private async createUnifiedSession({
    keycloakUser,
    keycloakData,
    odooUser,
    supabaseUser
  }: any): Promise<UnifiedUser> {

    // Get user permissions from Odoo
    const permissions = await this.getOdooPermissions(odooUser.uid)

    // Get company info from Odoo
    const company = await this.getOdooCompany(odooUser.company_id)

    return {
      // Keycloak identity
      keycloakId: keycloakUser.sub,
      email: keycloakUser.email,
      firstName: keycloakUser.given_name || '',
      lastName: keycloakUser.family_name || '',

      // Odoo business context
      odooUserId: odooUser.uid,
      companyId: odooUser.company_id,
      companyName: company.name,
      role: this.mapOdooRoleToUnified(permissions),
      departments: permissions.departments || [],

      // Supabase AI context
      supabaseId: supabaseUser.id,
      aiPreferences: supabaseUser.user_metadata?.ai_preferences || {},
      realtimeSubscriptions: [],

      // Unified session
      sessionId: this.generateSessionId(),
      accessToken: keycloakData.access_token,
      refreshToken: keycloakData.refresh_token,
      expiresAt: new Date(Date.now() + (keycloakData.expires_in * 1000)),

      // Permissions
      permissions: permissions.permissions || [],
      modules: permissions.modules || []
    }
  }

  // 5. Permission management
  private async getOdooPermissions(userId: number) {
    const response = await fetch(`${AUTH_CONFIG.odoo.url}/web/dataset/call_kw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.tokens?.odooSessionId}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'res.users',
          method: 'get_user_permissions',
          args: [userId],
          kwargs: {}
        }
      })
    })

    return response.json()
  }

  private async getOdooCompany(companyId: number) {
    const response = await fetch(`${AUTH_CONFIG.odoo.url}/web/dataset/call_kw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.tokens?.odooSessionId}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'res.company',
          method: 'read',
          args: [[companyId], ['name', 'vat', 'country_id']],
          kwargs: {}
        }
      })
    })

    const result = await response.json()
    return result.result[0]
  }

  private mapOdooRoleToUnified(permissions: any): UserRole {
    if (permissions.is_superuser) return 'super_admin'
    if (permissions.groups.includes('bcm_base.group_bcm_admin')) return 'org_admin'
    if (permissions.groups.includes('bcm_base.group_bcm_manager')) return 'manager'
    if (permissions.groups.includes('bcm_base.group_bcm_analyst')) return 'analyst'
    return 'viewer'
  }

  // 6. Multi-tenant data access
  async executeOdooQuery(model: string, method: string, args: any[] = [], kwargs: any = {}) {
    if (!this.user) throw new Error('Not authenticated')

    // Automatically add company filter for multi-tenancy
    if (kwargs.domain && !kwargs.domain.some((d: any) => d[0] === 'company_id')) {
      kwargs.domain.push(['company_id', '=', this.user.companyId])
    }

    const response = await fetch(`${AUTH_CONFIG.odoo.url}/web/dataset/call_kw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.tokens?.odooSessionId}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model,
          method,
          args,
          kwargs
        }
      })
    })

    return response.json()
  }

  // 7. Supabase real-time with user context
  async subscribeToRealtimeChannel(channel: string, callback: (payload: any) => void) {
    if (!this.user) throw new Error('Not authenticated')

    const subscription = supabase
      .channel(channel)
      .on('*', { user_id: this.user.supabaseId }, callback)
      .subscribe()

    this.user.realtimeSubscriptions.push(channel)
    return subscription
  }

  // 8. Session management
  async refreshSession(): Promise<void> {
    if (!this.tokens?.refreshToken) throw new Error('No refresh token available')

    const response = await fetch(`${AUTH_CONFIG.keycloak.url}/realms/${AUTH_CONFIG.keycloak.realm}/protocol/openid-connect/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        client_id: AUTH_CONFIG.keycloak.clientId,
        refresh_token: this.tokens.refreshToken
      })
    })

    if (!response.ok) {
      await this.logout()
      throw new Error('Session refresh failed')
    }

    const data = await response.json()

    if (this.tokens) {
      this.tokens.keycloakToken = data.access_token
      this.tokens.unifiedToken = await this.generateUnifiedToken(this.user!)
    }

    if (this.user) {
      this.user.accessToken = data.access_token
      this.user.expiresAt = new Date(Date.now() + (data.expires_in * 1000))
    }
  }

  async logout(): Promise<void> {
    if (this.tokens?.keycloakToken) {
      // Logout from Keycloak
      await fetch(`${AUTH_CONFIG.keycloak.url}/realms/${AUTH_CONFIG.keycloak.realm}/protocol/openid-connect/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.tokens.keycloakToken}`
        }
      })
    }

    // Logout from Supabase
    await supabase.auth.signOut()

    // Clear session
    this.user = null
    this.tokens = null
    this.notifyListeners(null)
  }

  // 9. Utilities
  private generateSessionId(): string {
    return `unified_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private async generateUnifiedToken(user: UnifiedUser): string {
    // Create JWT with user context for frontend
    const payload = {
      sub: user.keycloakId,
      email: user.email,
      company_id: user.companyId,
      role: user.role,
      permissions: user.permissions,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(user.expiresAt.getTime() / 1000)
    }

    // Simple JWT encoding (in production use proper JWT library)
    const header = { alg: 'HS256', typ: 'JWT' }
    const encodedHeader = btoa(JSON.stringify(header))
    const encodedPayload = btoa(JSON.stringify(payload))

    return `${encodedHeader}.${encodedPayload}.signature`
  }

  // 10. Event listeners
  onAuthStateChange(callback: (user: UnifiedUser | null) => void) {
    this.listeners.push(callback)

    return () => {
      this.listeners = this.listeners.filter(l => l !== callback)
    }
  }

  private notifyListeners(user: UnifiedUser | null) {
    this.listeners.forEach(listener => listener(user))
  }

  // 11. Current user access
  getCurrentUser(): UnifiedUser | null {
    return this.user
  }

  isAuthenticated(): boolean {
    return this.user !== null && this.user.expiresAt > new Date()
  }

  hasPermission(permission: string): boolean {
    return this.user?.permissions.includes(permission) || false
  }

  hasRole(role: UserRole): boolean {
    return this.user?.role === role
  }

  getCompanyId(): number | null {
    return this.user?.companyId || null
  }

  // Helper methods for Odoo integration
  private mapOdooGroupsToRole(groups: any[]): UserRole {
    const groupNames = groups.map(g => g.name.toLowerCase())

    // Map Odoo groups to unified roles
    if (groupNames.some(name =>
      name.includes('admin') ||
      name.includes('manager') ||
      name.includes('bcm_admin')
    )) {
      return 'org_admin'
    }

    if (groupNames.some(name =>
      name.includes('bcm_manager') ||
      name.includes('user') ||
      name.includes('officer')
    )) {
      return 'manager'
    }

    if (groupNames.some(name =>
      name.includes('analyst') ||
      name.includes('bcm_analyst')
    )) {
      return 'analyst'
    }

    return 'viewer'
  }

  private mapOdooGroupsToPermissions(groups: any[]): string[] {
    const permissions: string[] = []
    const groupNames = groups.map(g => g.name.toLowerCase())

    // Base permissions for all users
    permissions.push('bcm.read_basic')

    // Admin permissions
    if (groupNames.some(name => name.includes('admin'))) {
      permissions.push(
        'bcm.read_all',
        'bcm.write_all',
        'bcm.admin',
        'users.manage',
        'company.admin'
      )
    }

    // Manager permissions
    if (groupNames.some(name => name.includes('manager'))) {
      permissions.push(
        'bcm.read_all',
        'bcm.write_basic',
        'incidents.manage',
        'scenarios.create',
        'reports.generate'
      )
    }

    // Analyst permissions
    if (groupNames.some(name => name.includes('analyst'))) {
      permissions.push(
        'bcm.read_all',
        'bcm.analyze',
        'reports.generate',
        'risk.assess'
      )
    }

    // Module-specific permissions based on groups
    if (groupNames.some(name => name.includes('bia'))) {
      permissions.push('bcm.read_bia', 'bcm.write_bia')
    }

    if (groupNames.some(name => name.includes('risk'))) {
      permissions.push('bcm.read_risk_assessment', 'bcm.write_risk_assessment')
    }

    if (groupNames.some(name => name.includes('incident'))) {
      permissions.push('bcm.read_incidents', 'bcm.write_incidents')
    }

    if (groupNames.some(name => name.includes('exercise'))) {
      permissions.push('bcm.read_exercises', 'bcm.write_exercises')
    }

    if (groupNames.some(name => name.includes('compliance'))) {
      permissions.push('bcm.read_compliance', 'bcm.write_compliance')
    }

    return permissions
  }

  // Get PostgreSQL client for direct access
  getPostgreSQLClient() {
    return postgresClient
  }

  // Get unified database manager
  getUnifiedDB() {
    return unifiedDB
  }
}

// Singleton instance
export const unifiedAuth = new UnifiedAuthBridge()

// React hook for easy usage
export function useUnifiedAuth() {
  const [user, setUser] = React.useState<UnifiedUser | null>(unifiedAuth.getCurrentUser())

  React.useEffect(() => {
    const unsubscribe = unifiedAuth.onAuthStateChange(setUser)
    return unsubscribe
  }, [])

  return {
    user,
    isAuthenticated: unifiedAuth.isAuthenticated(),
    login: unifiedAuth.loginWithKeycloak.bind(unifiedAuth),
    logout: unifiedAuth.logout.bind(unifiedAuth),
    hasPermission: unifiedAuth.hasPermission.bind(unifiedAuth),
    hasRole: unifiedAuth.hasRole.bind(unifiedAuth),
    executeOdooQuery: unifiedAuth.executeOdooQuery.bind(unifiedAuth),
    subscribeToRealtime: unifiedAuth.subscribeToRealtimeChannel.bind(unifiedAuth)
  }
}

// Export for global access
declare global {
  interface Window {
    unifiedAuth: UnifiedAuthBridge
  }
}

if (typeof window !== 'undefined') {
  window.unifiedAuth = unifiedAuth
}