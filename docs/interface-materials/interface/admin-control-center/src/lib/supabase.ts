/**
 * Supabase Client for AI Platform ISO
 * Handles user authentication, profiles, marketplace data
 */

import { createClient } from '@supabase/supabase-js'
import type { Database } from '@/types/supabase'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Please check .env file.'
  )
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// ============================================================================
// AUTHENTICATION HELPERS
// ============================================================================

/**
 * Login with Odoo SSO
 * 1. Authenticate with Odoo backend
 * 2. Create/update Supabase session with Odoo token
 */
export async function loginWithOdoo(credentials: {
  email: string
  password: string
}) {
  try {
    // 1. Call Odoo authentication endpoint
    const odooUrl = import.meta.env.VITE_ODOO_URL
    const response = await fetch(`${odooUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    })

    if (!response.ok) {
      throw new Error('Odoo authentication failed')
    }

    const { token, user } = await response.json()

    // 2. Set session in Supabase
    const { data, error } = await supabase.auth.setSession({
      access_token: token,
      refresh_token: token // Odoo doesn't use refresh tokens
    })

    if (error) throw error

    // 3. Sync user profile to Supabase
    await syncUserProfile(user)

    return { user: data.user, session: data.session }
  } catch (error) {
    console.error('Login error:', error)
    throw error
  }
}

/**
 * Sync Odoo user to Supabase user_profiles table
 */
async function syncUserProfile(odooUser: {
  id: string
  email: string
  name: string
  role: string
  organization_id?: string
}) {
  const { error } = await supabase.from('user_profiles').upsert(
    {
      id: odooUser.id,
      email: odooUser.email,
      name: odooUser.name,
      role: odooUser.role,
      organization_id: odooUser.organization_id,
      last_login: new Date().toISOString()
    },
    { onConflict: 'id' }
  )

  if (error) {
    console.error('Profile sync error:', error)
  }
}

/**
 * Logout and clear session
 */
export async function logout() {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.error('Logout error:', error)
  }
  return { error }
}

/**
 * Get current session
 */
export async function getSession() {
  const {
    data: { session },
    error
  } = await supabase.auth.getSession()
  return { session, error }
}

/**
 * Check if user has access to organization
 */
export async function checkOrganizationAccess(
  userId: string,
  orgId: string
): Promise<boolean> {
  const { data } = await supabase
    .from('user_organizations')
    .select('*')
    .eq('user_id', userId)
    .eq('org_id', orgId)
    .single()

  return !!data
}

// ============================================================================
// USER PROFILE QUERIES
// ============================================================================

export async function getUserProfile(userId: string) {
  const { data, error } = await supabase
    .from('user_profiles')
    .select('*')
    .eq('id', userId)
    .single()

  if (error) {
    console.error('Get profile error:', error)
    return null
  }

  return data
}

export async function updateUserProfile(userId: string, updates: Partial<{
  name: string
  avatar: string
  bio: string
  role: string
}>) {
  const { data, error } = await supabase
    .from('user_profiles')
    .update(updates)
    .eq('id', userId)
    .select()
    .single()

  if (error) {
    console.error('Update profile error:', error)
    throw error
  }

  return data
}

// ============================================================================
// MARKETPLACE QUERIES
// ============================================================================

export async function getAuditorProfile(auditorId: string) {
  const { data, error } = await supabase
    .from('auditor_profiles')
    .select(`
      *,
      user_profiles!inner(name, email, avatar)
    `)
    .eq('id', auditorId)
    .single()

  if (error) {
    console.error('Get auditor error:', error)
    return null
  }

  return data
}

export async function searchAuditors(filters: {
  certifications?: string[]
  industry?: string
  min_rating?: number
  price_max?: number
}) {
  let query = supabase
    .from('auditor_profiles')
    .select(`
      *,
      user_profiles!inner(name, email, avatar)
    `)

  if (filters.min_rating) {
    query = query.gte('rating', filters.min_rating)
  }

  if (filters.price_max) {
    query = query.lte('pricing->consultation', filters.price_max)
  }

  if (filters.certifications && filters.certifications.length > 0) {
    query = query.contains('certifications', filters.certifications)
  }

  if (filters.industry) {
    query = query.contains('industry_experience', [filters.industry])
  }

  const { data, error } = await query

  if (error) {
    console.error('Search auditors error:', error)
    return []
  }

  return data
}

// ============================================================================
// LEARNING & COURSES
// ============================================================================

export async function getCourses(filters?: {
  category?: string
  level?: string
  certification_only?: boolean
}) {
  let query = supabase.from('courses').select('*')

  if (filters?.category) {
    query = query.eq('category', filters.category)
  }

  if (filters?.level) {
    query = query.eq('level', filters.level)
  }

  if (filters?.certification_only) {
    query = query.eq('certification', true)
  }

  const { data, error } = await query.order('created_at', { ascending: false })

  if (error) {
    console.error('Get courses error:', error)
    return []
  }

  return data
}

export async function getUserProgress(userId: string) {
  const { data, error } = await supabase
    .from('learning_progress')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (error) {
    console.error('Get progress error:', error)
    return null
  }

  return data
}

// ============================================================================
// REAL-TIME SUBSCRIPTIONS
// ============================================================================

/**
 * Subscribe to user profile changes
 */
export function subscribeToUserProfile(
  userId: string,
  callback: (payload: unknown) => void
) {
  return supabase
    .channel(`user_profile:${userId}`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'user_profiles',
        filter: `id=eq.${userId}`
      },
      callback
    )
    .subscribe()
}

/**
 * Subscribe to crisis incidents (Journey 6)
 */
export function subscribeToCrisisIncidents(
  orgId: string,
  callback: (payload: unknown) => void
) {
  return supabase
    .channel(`incidents:${orgId}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'incidents',
        filter: `organization_id=eq.${orgId}`
      },
      callback
    )
    .subscribe()
}
