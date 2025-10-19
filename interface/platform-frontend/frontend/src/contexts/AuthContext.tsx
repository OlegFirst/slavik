import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

/**
 * User role types with hierarchical permissions
 */
export type UserRole = 'ADMIN' | 'MANAGER' | 'USER' | 'VIEWER';

/**
 * User interface representing authenticated user
 */
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  department?: string;
  tenants: string[]; // tenant IDs user has access to
}

/**
 * Tenant plan types
 */
export type TenantPlan = 'FREE' | 'PROFESSIONAL' | 'ENTERPRISE';

/**
 * Tenant interface representing organization
 */
export interface Tenant {
  id: string;
  name: string;
  plan: TenantPlan;
  settings: Record<string, any>;
}

/**
 * Authentication tokens
 */
interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

/**
 * Auth context value with all auth-related state and methods
 */
export interface AuthContextValue {
  user: User | null;
  tenant: Tenant | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: Error | null;

  // Authentication methods
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  switchTenant: (tenantId: string) => void;
  refreshUser: () => Promise<void>;

  // Permission helpers
  isAdmin: () => boolean;
  canEditDocument: (ownerId: string) => boolean;
  canDeleteDocument: (ownerId: string) => boolean;
  hasPermission: (permission: string) => boolean;
}

/**
 * Auth context
 */
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Local storage keys
 */
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_access_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  TOKEN_EXPIRES_AT: 'auth_token_expires_at',
  CURRENT_TENANT: 'auth_current_tenant',
} as const;

/**
 * Auth provider props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component that manages authentication state
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Get tokens from localStorage
   */
  const getTokens = useCallback((): AuthTokens | null => {
    const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    const expiresAt = localStorage.getItem(STORAGE_KEYS.TOKEN_EXPIRES_AT);

    if (!accessToken || !refreshToken || !expiresAt) {
      return null;
    }

    return {
      accessToken,
      refreshToken,
      expiresAt: parseInt(expiresAt, 10),
    };
  }, []);

  /**
   * Save tokens to localStorage
   */
  const saveTokens = useCallback((tokens: AuthTokens): void => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.accessToken);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refreshToken);
    localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRES_AT, tokens.expiresAt.toString());
  }, []);

  /**
   * Clear tokens from localStorage
   */
  const clearTokens = useCallback((): void => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRES_AT);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_TENANT);
  }, []);

  /**
   * Check if token is expired or about to expire (within 5 minutes)
   */
  const isTokenExpired = useCallback((expiresAt: number): boolean => {
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;
    return now >= expiresAt - fiveMinutes;
  }, []);

  /**
   * Refresh access token using refresh token
   */
  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    try {
      const tokens = getTokens();
      if (!tokens) {
        return false;
      }

      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken: tokens.refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const data = await response.json();
      const newTokens: AuthTokens = {
        accessToken: data.accessToken,
        refreshToken: data.refreshToken || tokens.refreshToken,
        expiresAt: Date.now() + data.expiresIn * 1000,
      };

      saveTokens(newTokens);
      return true;
    } catch (err) {
      console.error('Token refresh failed:', err);
      clearTokens();
      return false;
    }
  }, [getTokens, saveTokens, clearTokens]);

  /**
   * Fetch current user from API
   */
  const fetchCurrentUser = useCallback(async (): Promise<void> => {
    try {
      const tokens = getTokens();
      if (!tokens) {
        setIsLoading(false);
        return;
      }

      // Check if token needs refresh
      if (isTokenExpired(tokens.expiresAt)) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          setIsLoading(false);
          return;
        }
      }

      const response = await fetch('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${tokens.accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }

      const data = await response.json();
      setUser(data.user);

      // Load current tenant
      const currentTenantId = localStorage.getItem(STORAGE_KEYS.CURRENT_TENANT) || data.user.tenants[0];
      if (currentTenantId) {
        await loadTenant(currentTenantId, tokens.accessToken);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to fetch user:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch user'));
      clearTokens();
    } finally {
      setIsLoading(false);
    }
  }, [getTokens, isTokenExpired, refreshAccessToken, clearTokens]);

  /**
   * Load tenant data
   */
  const loadTenant = useCallback(async (tenantId: string, accessToken: string): Promise<void> => {
    try {
      const response = await fetch(`/api/tenants/${tenantId}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tenant');
      }

      const data = await response.json();
      setTenant(data.tenant);
      localStorage.setItem(STORAGE_KEYS.CURRENT_TENANT, tenantId);
    } catch (err) {
      console.error('Failed to fetch tenant:', err);
    }
  }, []);

  /**
   * Login with email and password
   */
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }

      const data = await response.json();
      const tokens: AuthTokens = {
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
        expiresAt: Date.now() + data.expiresIn * 1000,
      };

      saveTokens(tokens);
      await fetchCurrentUser();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Login failed');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [saveTokens, fetchCurrentUser]);

  /**
   * Logout and clear all auth data
   */
  const logout = useCallback((): void => {
    setUser(null);
    setTenant(null);
    setError(null);
    clearTokens();
  }, [clearTokens]);

  /**
   * Switch to a different tenant
   */
  const switchTenant = useCallback(
    async (tenantId: string): Promise<void> => {
      if (!user || !user.tenants.includes(tenantId)) {
        throw new Error('User does not have access to this tenant');
      }

      const tokens = getTokens();
      if (!tokens) {
        throw new Error('Not authenticated');
      }

      await loadTenant(tenantId, tokens.accessToken);
    },
    [user, getTokens, loadTenant]
  );

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async (): Promise<void> => {
    await fetchCurrentUser();
  }, [fetchCurrentUser]);

  /**
   * Check if user is admin
   */
  const isAdmin = useCallback((): boolean => {
    return user?.role === 'ADMIN';
  }, [user]);

  /**
   * Check if user can edit a document
   * Admins and managers can edit all documents
   * Users can only edit their own documents
   */
  const canEditDocument = useCallback(
    (ownerId: string): boolean => {
      if (!user) return false;
      if (user.role === 'ADMIN' || user.role === 'MANAGER') return true;
      return user.id === ownerId;
    },
    [user]
  );

  /**
   * Check if user can delete a document
   * Only admins and managers can delete documents
   * Users can delete their own documents
   */
  const canDeleteDocument = useCallback(
    (ownerId: string): boolean => {
      if (!user) return false;
      if (user.role === 'ADMIN' || user.role === 'MANAGER') return true;
      return user.id === ownerId && user.role === 'USER';
    },
    [user]
  );

  /**
   * Check if user has a specific permission
   * This is a simplified permission check based on role
   */
  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false;

      // Admin has all permissions
      if (user.role === 'ADMIN') return true;

      // Role-based permission mapping
      const rolePermissions: Record<UserRole, string[]> = {
        ADMIN: ['*'],
        MANAGER: [
          'documents:create',
          'documents:edit',
          'documents:delete',
          'documents:approve',
          'bia:create',
          'bia:edit',
          'bia:delete',
        ],
        USER: ['documents:create', 'documents:edit:own', 'bia:create', 'bia:edit:own'],
        VIEWER: ['documents:view', 'bia:view'],
      };

      const permissions = rolePermissions[user.role] || [];
      return permissions.includes('*') || permissions.includes(permission);
    },
    [user]
  );

  /**
   * Load user on mount
   */
  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  /**
   * Setup auto-refresh interval
   */
  useEffect(() => {
    const interval = setInterval(
      async () => {
        const tokens = getTokens();
        if (tokens && isTokenExpired(tokens.expiresAt)) {
          await refreshAccessToken();
        }
      },
      5 * 60 * 1000
    ); // Check every 5 minutes

    return () => clearInterval(interval);
  }, [getTokens, isTokenExpired, refreshAccessToken]);

  const value: AuthContextValue = {
    user,
    tenant,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    logout,
    switchTenant,
    refreshUser,
    isAdmin,
    canEditDocument,
    canDeleteDocument,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Custom hook to use auth context
 * @throws {Error} If used outside of AuthProvider
 */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
