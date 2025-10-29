'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { UnifiedUser, unifiedAuth } from '@/lib/auth/unified-auth'

// Auth Context
interface AuthContextType {
  user: UnifiedUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  hasPermission: (permission: string) => boolean
  hasRole: (role: string) => boolean
  refreshSession: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

// Auth Provider Component
interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<UnifiedUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Initialize auth state
    const initializeAuth = async () => {
      try {
        // Check for existing session
        const savedSession = localStorage.getItem('unified_auth_session')
        if (savedSession) {
          const sessionData = JSON.parse(savedSession)

          // Validate session hasn't expired
          if (new Date(sessionData.expiresAt) > new Date()) {
            setUser(sessionData)
          } else {
            localStorage.removeItem('unified_auth_session')
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()

    // Listen for auth state changes
    const unsubscribe = unifiedAuth.onAuthStateChange((newUser) => {
      setUser(newUser)

      // Persist session
      if (newUser) {
        localStorage.setItem('unified_auth_session', JSON.stringify(newUser))
      } else {
        localStorage.removeItem('unified_auth_session')
      }
    })

    return unsubscribe
  }, [])

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!user) return

    const refreshInterval = setInterval(async () => {
      const timeUntilExpiry = user.expiresAt.getTime() - Date.now()

      // Refresh if less than 5 minutes remaining
      if (timeUntilExpiry < 5 * 60 * 1000) {
        try {
          await unifiedAuth.refreshSession()
        } catch (error) {
          console.error('Auto-refresh failed:', error)
          await handleLogout()
        }
      }
    }, 60 * 1000) // Check every minute

    return () => clearInterval(refreshInterval)
  }, [user])

  const handleLogin = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // Initialize platform first (if not already done)
      await unifiedAuth.initialize()

      // Use smart login that auto-detects available services
      const user = await unifiedAuth.login(email, password)
      setUser(user)
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = async () => {
    setIsLoading(true)
    try {
      await unifiedAuth.logout()
      setUser(null)
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefreshSession = async () => {
    try {
      await unifiedAuth.refreshSession()
    } catch (error) {
      console.error('Session refresh failed:', error)
      await handleLogout()
      throw error
    }
  }

  const hasPermission = (permission: string): boolean => {
    return user?.permissions.includes(permission) || false
  }

  const hasRole = (role: string): boolean => {
    return user?.role === role
  }

  const contextValue: AuthContextType = {
    user,
    isAuthenticated: user !== null && user.expiresAt > new Date(),
    isLoading,
    login: handleLogin,
    logout: handleLogout,
    hasPermission,
    hasRole,
    refreshSession: handleRefreshSession
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Higher-order component for protected routes
interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: string
  requiredPermission?: string
  fallback?: ReactNode
}

export function ProtectedRoute({
  children,
  requiredRole,
  requiredPermission,
  fallback
}: ProtectedRouteProps) {
  const { isAuthenticated, hasRole, hasPermission, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return fallback || <LoginRequired />
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return fallback || <AccessDenied />
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return fallback || <AccessDenied />
  }

  return <>{children}</>
}

// Login required component
function LoginRequired() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Authentication Required
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please log in to access this page
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  )
}

// Access denied component
function AccessDenied() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Access Denied
        </h2>
        <p className="text-gray-600">
          You don't have permission to access this resource
        </p>
      </div>
    </div>
  )
}

// Login form component
function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, isLoading } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      await login(email, password)
    } catch (error) {
      setError('Authentication failed. Please check your credentials.')
    }
  }

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email" className="sr-only">
          Email address
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="password" className="sr-only">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div>
        <button
          type="submit"
          disabled={isLoading}
          className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isLoading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
          ) : (
            'Sign in'
          )}
        </button>
      </div>
    </form>
  )
}

// Role-based component wrapper
interface RoleGuardProps {
  children: ReactNode
  roles: string[]
  fallback?: ReactNode
}

export function RoleGuard({ children, roles, fallback }: RoleGuardProps) {
  const { hasRole } = useAuth()

  const hasRequiredRole = roles.some(role => hasRole(role))

  if (!hasRequiredRole) {
    return fallback || null
  }

  return <>{children}</>
}

// Permission-based component wrapper
interface PermissionGuardProps {
  children: ReactNode
  permissions: string[]
  fallback?: ReactNode
}

export function PermissionGuard({ children, permissions, fallback }: PermissionGuardProps) {
  const { hasPermission } = useAuth()

  const hasRequiredPermission = permissions.some(permission => hasPermission(permission))

  if (!hasRequiredPermission) {
    return fallback || null
  }

  return <>{children}</>
}