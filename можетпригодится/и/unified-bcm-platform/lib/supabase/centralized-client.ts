// Centralized Supabase Client for BCM Platform
// Integrates with existing schema at /Users/MD/ISO-22301/supabase
// Uses bcm_users, bcm_companies, ai_organism_memory, etc.

import { createClient, SupabaseClient } from '@supabase/supabase-js'

// Centralized configuration using existing Supabase instance
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// Create the centralized client
export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey)

// Database types based on centralized schema
export interface BCMUser {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  company_id?: number
  client_id?: string
  subscription_plan: string
  is_active: boolean
  theme: string
  language: string
  timezone: string
  created_at: string
  updated_at: string
  last_login?: string
  login_count: number
  bcm_companies?: BCMCompany
}

export interface BCMCompany {
  id: number
  name: string
  slug: string
  subscription_plan: string
  subscription_status: string
  max_users: number
  settings: Record<string, any>
  features: Record<string, any>
  created_at: string
  updated_at: string
}

export interface AIOrganismMemory {
  id: string
  memory_type: string
  memory_category: string
  memory_title: string
  memory_summary?: string
  memory_content: Record<string, any>
  memory_tags: string[]
  source_data?: Record<string, any>
  wisdom_level: number
  reliability_score: number
  applicability_score: number
  access_count: number
  successful_applications: number
  failed_applications: number
  last_accessed?: string
  source_organ?: string
  source_module?: string
  source_company?: string
  memory_version: number
  parent_memory_id?: string
  evolution_reason?: string
  created_at: string
  updated_at: string
  tenant_id: string
}

export interface AIConversationContext {
  id: string
  conversation_id: string
  user_id?: string
  session_id?: string
  chat_platform?: string
  conversation_history?: Record<string, any>
  platform_context?: Record<string, any>
  active_workflows?: Record<string, any>
  user_preferences?: Record<string, any>
  consulted_organs: string[]
  organ_responses?: Record<string, any>
  cross_organ_collaboration?: Record<string, any>
  successful_actions: string[]
  user_satisfaction_score?: number
  conversation_effectiveness?: number
  platform_actions_triggered: number
  ai_helpfulness_score?: number
  conversation_patterns?: Record<string, any>
  context_evolution?: Record<string, any>
  learning_extracted?: string
  context_ttl_hours: number
  auto_cleanup: boolean
  created_at: string
  last_interaction: string
  expires_at: string
  tenant_id: string
}

// Centralized BCM Supabase API
export class CentralizedBCMAPI {
  private client: SupabaseClient

  constructor() {
    this.client = supabase
  }

  // User management with centralized schema
  async getUser(userId: string): Promise<BCMUser | null> {
    const { data, error } = await this.client
      .from('bcm_users')
      .select(`
        *,
        bcm_companies (
          id,
          name,
          subscription_plan,
          features
        )
      `)
      .eq('id', userId)
      .single()

    if (error) {
      console.error('Error getting user:', error)
      return null
    }

    return data
  }

  async updateUser(userId: string, updates: Partial<BCMUser>): Promise<boolean> {
    const { error } = await this.client
      .from('bcm_users')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', userId)

    if (error) {
      console.error('Error updating user:', error)
      return false
    }

    return true
  }

  async getUsersByCompany(companyId: number): Promise<BCMUser[]> {
    const { data, error } = await this.client
      .from('bcm_users')
      .select('*')
      .eq('company_id', companyId)
      .eq('is_active', true)

    if (error) {
      console.error('Error getting company users:', error)
      return []
    }

    return data || []
  }

  // AI Memory management with centralized schema
  async storeAIMemory(memory: Omit<AIOrganismMemory, 'id' | 'created_at' | 'updated_at'>): Promise<string | null> {
    const { data, error } = await this.client
      .from('ai_organism_memory')
      .insert(memory)
      .select('id')
      .single()

    if (error) {
      console.error('Error storing AI memory:', error)
      return null
    }

    return data.id
  }

  async getRelevantMemories(
    memoryType: string,
    tenantId: string,
    limit: number = 10
  ): Promise<AIOrganismMemory[]> {
    const { data, error } = await this.client
      .from('ai_organism_memory')
      .select('*')
      .eq('memory_type', memoryType)
      .eq('tenant_id', tenantId)
      .gte('wisdom_level', 0.3)
      .order('wisdom_level', { ascending: false })
      .order('created_at', { ascending: false })
      .limit(limit)

    if (error) {
      console.error('Error getting relevant memories:', error)
      return []
    }

    return data || []
  }

  async updateMemoryWisdom(
    memoryId: string,
    success: boolean,
    applicationContext?: Record<string, any>
  ): Promise<boolean> {
    const { data: currentMemory, error: fetchError } = await this.client
      .from('ai_organism_memory')
      .select('wisdom_level, access_count, successful_applications, failed_applications')
      .eq('id', memoryId)
      .single()

    if (fetchError) {
      console.error('Error fetching memory for wisdom update:', fetchError)
      return false
    }

    const wisdomDelta = success ? 0.1 : -0.05
    const newWisdomLevel = Math.min(1.0, Math.max(0.0, currentMemory.wisdom_level + wisdomDelta))

    const { error } = await this.client
      .from('ai_organism_memory')
      .update({
        access_count: currentMemory.access_count + 1,
        successful_applications: success
          ? currentMemory.successful_applications + 1
          : currentMemory.successful_applications,
        failed_applications: !success
          ? currentMemory.failed_applications + 1
          : currentMemory.failed_applications,
        last_accessed: new Date().toISOString(),
        wisdom_level: newWisdomLevel,
        updated_at: new Date().toISOString()
      })
      .eq('id', memoryId)

    if (error) {
      console.error('Error updating memory wisdom:', error)
      return false
    }

    return true
  }

  // Conversation context management
  async storeConversationContext(
    context: Omit<AIConversationContext, 'id' | 'created_at' | 'last_interaction'>
  ): Promise<string | null> {
    const now = new Date().toISOString()
    const expiresAt = new Date(Date.now() + (context.context_ttl_hours * 60 * 60 * 1000)).toISOString()

    const { data, error } = await this.client
      .from('ai_conversation_context')
      .insert({
        ...context,
        created_at: now,
        last_interaction: now,
        expires_at: expiresAt
      })
      .select('id')
      .single()

    if (error) {
      console.error('Error storing conversation context:', error)
      return null
    }

    return data.id
  }

  async getConversationContext(
    conversationId: string,
    tenantId: string
  ): Promise<AIConversationContext | null> {
    const { data, error } = await this.client
      .from('ai_conversation_context')
      .select('*')
      .eq('conversation_id', conversationId)
      .eq('tenant_id', tenantId)
      .gt('expires_at', new Date().toISOString())
      .order('last_interaction', { ascending: false })
      .limit(1)
      .single()

    if (error) {
      console.error('Error getting conversation context:', error)
      return null
    }

    return data
  }

  async updateConversationContext(
    contextId: string,
    updates: Partial<AIConversationContext>
  ): Promise<boolean> {
    const { error } = await this.client
      .from('ai_conversation_context')
      .update({
        ...updates,
        last_interaction: new Date().toISOString()
      })
      .eq('id', contextId)

    if (error) {
      console.error('Error updating conversation context:', error)
      return false
    }

    return true
  }

  // Real-time subscriptions with tenant isolation
  subscribeToUserUpdates(
    userId: string,
    callback: (payload: any) => void
  ) {
    return this.client
      .channel(`user-updates-${userId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'bcm_users',
          filter: `id=eq.${userId}`
        },
        callback
      )
      .subscribe()
  }

  subscribeToCompanyUpdates(
    companyId: number,
    callback: (payload: any) => void
  ) {
    return this.client
      .channel(`company-updates-${companyId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'bcm_users',
          filter: `company_id=eq.${companyId}`
        },
        callback
      )
      .subscribe()
  }

  subscribeToAIMemoryUpdates(
    tenantId: string,
    callback: (payload: any) => void
  ) {
    return this.client
      .channel(`ai-memory-${tenantId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'ai_organism_memory',
          filter: `tenant_id=eq.${tenantId}`
        },
        callback
      )
      .subscribe()
  }

  // Multi-tenant operations
  async setTenantContext(tenantId: string): Promise<void> {
    // Set the current tenant for RLS policies
    await this.client.rpc('set_config', {
      setting_name: 'app.current_tenant',
      setting_value: tenantId,
      is_local: true
    })
  }

  // Company management
  async getCompany(companyId: number): Promise<BCMCompany | null> {
    const { data, error } = await this.client
      .from('bcm_companies')
      .select('*')
      .eq('id', companyId)
      .single()

    if (error) {
      console.error('Error getting company:', error)
      return null
    }

    return data
  }

  async updateCompany(companyId: number, updates: Partial<BCMCompany>): Promise<boolean> {
    const { error } = await this.client
      .from('bcm_companies')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', companyId)

    if (error) {
      console.error('Error updating company:', error)
      return false
    }

    return true
  }

  // Authentication integration
  async authenticateUser(email: string, password: string): Promise<{ user: BCMUser; session: any } | null> {
    // Use centralized Supabase auth
    const { data: authData, error: authError } = await this.client.auth.signInWithPassword({
      email,
      password
    })

    if (authError) {
      console.error('Auth error:', authError)
      return null
    }

    // Get user profile from centralized bcm_users table
    const user = await this.getUser(authData.user.id)
    if (!user) {
      console.error('User profile not found')
      return null
    }

    // Set tenant context for RLS
    if (user.company_id) {
      await this.setTenantContext(user.company_id.toString())
    }

    return { user, session: authData.session }
  }

  async signOut(): Promise<void> {
    await this.client.auth.signOut()
  }

  // Health check
  async checkConnection(): Promise<boolean> {
    try {
      const { data, error } = await this.client
        .from('bcm_users')
        .select('count')
        .limit(1)

      return !error
    } catch (error) {
      console.error('Connection check failed:', error)
      return false
    }
  }
}

// Export singleton instance
export const centralizedBCM = new CentralizedBCMAPI()

// Export the Supabase client for direct use if needed
export { supabase as centralizedSupabase }