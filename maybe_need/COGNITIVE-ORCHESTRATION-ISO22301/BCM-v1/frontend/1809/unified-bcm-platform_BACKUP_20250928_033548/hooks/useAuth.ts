'use client'

import { useState, useEffect, createContext, useContext } from 'react'

export interface User {
  id: string
  name: string
  email: string
  role: 'super_admin' | 'org_admin' | 'manager' | 'analyst' | 'viewer'
  organizationId: string
  organizationName: string
  avatar?: string
  permissions: string[]
  lastLogin?: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  hasPermission: (permission: string) => boolean
  hasRole: (roles: string | string[]) => boolean
}

// Auth API configuration
const AUTH_API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8069/api/auth',
  endpoints: {
    login: '/login',
    logout: '/logout',
    refresh: '/refresh',
    user: '/user'
  }
}

// Create auth context
export const AuthContext = createContext<AuthContextType | null>(null)

// Custom hook for authentication
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Auth provider hook
export const useAuthProvider = (): AuthContextType => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  })

  // Check for existing session on mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setState(prev => ({ ...prev, isLoading: false }))
        return
      }

      const response = await fetch(`${AUTH_API_CONFIG.baseURL}${AUTH_API_CONFIG.endpoints.user}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Token validation failed')
      }

      const userData = await response.json()
      setState({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
    } catch (error) {
      localStorage.removeItem('auth_token')
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      })
    }
  }

  const login = async (email: string, password: string): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch(`${AUTH_API_CONFIG.baseURL}${AUTH_API_CONFIG.endpoints.login}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Login failed')
      }

      const { token, user } = await response.json()

      localStorage.setItem('auth_token', token)

      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
    } catch (error) {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      })
      throw error
    }
  }

  const logout = async (): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true }))

    try {
      const token = localStorage.getItem('auth_token')
      if (token) {
        await fetch(`${AUTH_API_CONFIG.baseURL}${AUTH_API_CONFIG.endpoints.logout}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
      }
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      localStorage.removeItem('auth_token')
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      })
    }
  }

  const refreshUser = async (): Promise<void> => {
    await checkAuthStatus()
  }

  const hasPermission = (permission: string): boolean => {
    return state.user?.permissions?.includes(permission) || false
  }

  const hasRole = (roles: string | string[]): boolean => {
    if (!state.user?.role) return false

    const roleArray = Array.isArray(roles) ? roles : [roles]
    return roleArray.includes(state.user.role)
  }

  return {
    ...state,
    login,
    logout,
    refreshUser,
    hasPermission,
    hasRole
  }
}

// Protected route wrapper
export const ProtectedRoute = ({
  children,
  requiredPermissions = [],
  requiredRoles = [],
  fallback = <div>Access denied</div>
}: {
  children: React.ReactNode
  requiredPermissions?: string[]
  requiredRoles?: string[]
  fallback?: React.ReactNode
}) => {
  const { isAuthenticated, isLoading, hasPermission, hasRole } = useAuth()

  if (isLoading) {
    return <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  }

  if (!isAuthenticated) {
    return <div>Please log in to continue</div>
  }

  // Check permissions
  if (requiredPermissions.length > 0) {
    const hasAllPermissions = requiredPermissions.every(permission => hasPermission(permission))
    if (!hasAllPermissions) {
      return <>{fallback}</>
    }
  }

  // Check roles
  if (requiredRoles.length > 0) {
    const hasRequiredRole = hasRole(requiredRoles)
    if (!hasRequiredRole) {
      return <>{fallback}</>
    }
  }

  return <>{children}</>
}

// Utility function to get current user (for API calls)
export const getCurrentUser = async (): Promise<User | null> => {
  const token = localStorage.getItem('auth_token')
  if (!token) return null

  try {
    const response = await fetch(`${AUTH_API_CONFIG.baseURL}${AUTH_API_CONFIG.endpoints.user}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) return null

    return await response.json()
  } catch (error) {
    console.error('Failed to get current user:', error)
    return null
  }
}

// Utility function to get auth headers for API calls
export const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}