/**
 * Authentication Store
 * Manages user authentication, role, organization, and current journey
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, Organization, UserRole, JourneyType } from '@/types/journeys'
import { loginWithOdoo, logout as supabaseLogout, getSession } from '@/lib/supabase'

interface AuthState {
  // State
  user: User | null
  organization: Organization | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  currentJourney: JourneyType

  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User | null) => void
  setOrganization: (org: Organization | null) => void
  switchJourney: (journey: JourneyType) => void
  clearError: () => void
  initialize: () => Promise<void>

  // Computed
  hasRole: (role: UserRole) => boolean
  canAccessJourney: (journey: JourneyType) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // ========================================================================
      // INITIAL STATE
      // ========================================================================
      user: null,
      organization: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      currentJourney: 'certification',

      // ========================================================================
      // ACTIONS
      // ========================================================================

      /**
       * Login with Odoo SSO
       */
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })

        try {
          // 1. Authenticate with Odoo + sync to Supabase
          const { user, session } = await loginWithOdoo({ email, password })

          if (!user) {
            throw new Error('Authentication failed')
          }

          // 2. Fetch full user profile from Supabase
          const response = await fetch(
            `${import.meta.env.VITE_SUPABASE_URL}/rest/v1/user_profiles?id=eq.${user.id}`,
            {
              headers: {
                apikey: import.meta.env.VITE_SUPABASE_ANON_KEY,
                Authorization: `Bearer ${session?.access_token}`
              }
            }
          )

          if (!response.ok) {
            throw new Error('Failed to fetch user profile')
          }

          const [profile] = await response.json()

          // 3. Fetch organization if user has one
          let organization = null
          if (profile.organization_id) {
            const orgResponse = await fetch(
              `${import.meta.env.VITE_SUPABASE_URL}/rest/v1/organizations?id=eq.${profile.organization_id}`,
              {
                headers: {
                  apikey: import.meta.env.VITE_SUPABASE_ANON_KEY,
                  Authorization: `Bearer ${session?.access_token}`
                }
              }
            )

            if (orgResponse.ok) {
              const [org] = await orgResponse.json()
              organization = org
            }
          }

          // 4. Map to User type
          const userObj: User = {
            id: profile.id,
            email: profile.email,
            name: profile.name,
            avatar: profile.avatar,
            role: profile.role as UserRole,
            organization_id: profile.organization_id,
            created_at: new Date(profile.created_at),
            last_login: new Date()
          }

          // 5. Determine default journey based on role
          const defaultJourney = getDefaultJourneyForRole(userObj.role)

          set({
            user: userObj,
            organization,
            isAuthenticated: true,
            isLoading: false,
            currentJourney: defaultJourney,
            error: null
          })
        } catch (error) {
          console.error('Login error:', error)
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
            isAuthenticated: false,
            user: null,
            organization: null
          })
          throw error
        }
      },

      /**
       * Logout
       */
      logout: async () => {
        set({ isLoading: true })

        try {
          await supabaseLogout()
          set({
            user: null,
            organization: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
            currentJourney: 'certification'
          })
        } catch (error) {
          console.error('Logout error:', error)
          set({ isLoading: false })
        }
      },

      /**
       * Set user (for external updates)
       */
      setUser: (user) => {
        set({ user, isAuthenticated: !!user })
      },

      /**
       * Set organization
       */
      setOrganization: (organization) => {
        set({ organization })
      },

      /**
       * Switch current journey
       */
      switchJourney: (journey: JourneyType) => {
        const { user } = get()

        // Check if user can access this journey
        if (!user || !get().canAccessJourney(journey)) {
          console.warn(`User cannot access journey: ${journey}`)
          return
        }

        set({ currentJourney: journey })
      },

      /**
       * Clear error
       */
      clearError: () => {
        set({ error: null })
      },

      /**
       * Initialize auth state from session
       */
      initialize: async () => {
        set({ isLoading: true })

        try {
          const { session } = await getSession()

          if (!session) {
            set({ isLoading: false })
            return
          }

          // Fetch user profile
          const response = await fetch(
            `${import.meta.env.VITE_SUPABASE_URL}/rest/v1/user_profiles?id=eq.${session.user.id}`,
            {
              headers: {
                apikey: import.meta.env.VITE_SUPABASE_ANON_KEY,
                Authorization: `Bearer ${session.access_token}`
              }
            }
          )

          if (!response.ok) {
            throw new Error('Failed to fetch user profile')
          }

          const [profile] = await response.json()

          // Map to User type
          const user: User = {
            id: profile.id,
            email: profile.email,
            name: profile.name,
            avatar: profile.avatar,
            role: profile.role as UserRole,
            organization_id: profile.organization_id,
            created_at: new Date(profile.created_at),
            last_login: profile.last_login ? new Date(profile.last_login) : undefined
          }

          set({
            user,
            isAuthenticated: true,
            isLoading: false
          })
        } catch (error) {
          console.error('Initialize error:', error)
          set({
            isLoading: false,
            isAuthenticated: false,
            user: null
          })
        }
      },

      // ========================================================================
      // COMPUTED PROPERTIES
      // ========================================================================

      /**
       * Check if user has specific role
       */
      hasRole: (role: UserRole) => {
        const { user } = get()
        return user?.role === role
      },

      /**
       * Check if user can access journey
       */
      canAccessJourney: (journey: JourneyType) => {
        const { user, organization } = get()

        if (!user) return false

        // Role-based journey access
        const roleJourneyMap: Record<UserRole, JourneyType[]> = {
          platform_admin: ['certification', 'auditor', 'academy', 'twin', 'crisis'],
          org_admin: ['certification', 'academy', 'twin', 'crisis'],
          bcm_manager: ['certification', 'academy', 'twin', 'crisis'],
          auditor: ['auditor', 'academy'],
          learner: ['academy'],
          viewer: ['academy']
        }

        const allowedJourneys = roleJourneyMap[user.role] || []

        if (!allowedJourneys.includes(journey)) {
          return false
        }

        // Subscription tier checks (for organizations)
        if (organization) {
          const tierJourneyMap: Record<string, JourneyType[]> = {
            starter: ['certification', 'academy'],
            professional: ['certification', 'academy', 'twin'],
            enterprise: ['certification', 'academy', 'twin', 'crisis']
          }

          const tierJourneys = tierJourneyMap[organization.subscription_tier] || []
          return tierJourneys.includes(journey)
        }

        return true
      }
    }),
    {
      name: 'auth-storage', // LocalStorage key
      partialize: (state) => ({
        user: state.user,
        organization: state.organization,
        isAuthenticated: state.isAuthenticated,
        currentJourney: state.currentJourney
      })
    }
  )
)

// ============================================================================
// HELPERS
// ============================================================================

function getDefaultJourneyForRole(role: UserRole): JourneyType {
  const roleDefaultMap: Record<UserRole, JourneyType> = {
    platform_admin: 'certification',
    org_admin: 'certification',
    bcm_manager: 'certification',
    auditor: 'auditor',
    learner: 'academy',
    viewer: 'academy'
  }

  return roleDefaultMap[role] || 'certification'
}

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Hook to get current user
 */
export function useCurrentUser() {
  return useAuthStore((state) => state.user)
}

/**
 * Hook to get current organization
 */
export function useCurrentOrganization() {
  return useAuthStore((state) => state.organization)
}

/**
 * Hook to check if user has role
 */
export function useHasRole(role: UserRole) {
  return useAuthStore((state) => state.hasRole(role))
}

/**
 * Hook to get current journey
 */
export function useCurrentJourney() {
  return useAuthStore((state) => state.currentJourney)
}

/**
 * Hook to check if user can access journey
 */
export function useCanAccessJourney(journey: JourneyType) {
  return useAuthStore((state) => state.canAccessJourney(journey))
}
