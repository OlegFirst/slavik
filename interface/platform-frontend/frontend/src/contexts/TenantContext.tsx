import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuth, Tenant, User } from './AuthContext';

/**
 * Tenant context value with tenant-specific state and methods
 */
export interface TenantContextValue {
  currentTenant: Tenant | null;
  tenants: Tenant[];
  departments: string[];
  users: User[];
  isLoading: boolean;
  error: Error | null;

  // Methods
  switchTenant: (tenantId: string) => Promise<void>;
  getTenantSetting: (key: string) => any;
  updateTenantSetting: (key: string, value: any) => Promise<void>;
  refreshTenantData: () => Promise<void>;
}

/**
 * Tenant context
 */
const TenantContext = createContext<TenantContextValue | undefined>(undefined);

/**
 * Tenant provider props
 */
interface TenantProviderProps {
  children: ReactNode;
}

/**
 * TenantProvider component that manages tenant-specific state
 */
export const TenantProvider: React.FC<TenantProviderProps> = ({ children }) => {
  const { user, tenant, isAuthenticated, switchTenant: authSwitchTenant } = useAuth();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [departments, setDepartments] = useState<string[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Get access token from localStorage
   */
  const getAccessToken = useCallback((): string | null => {
    return localStorage.getItem('auth_access_token');
  }, []);

  /**
   * Fetch all tenants for current user
   */
  const fetchTenants = useCallback(async (): Promise<void> => {
    if (!user || !isAuthenticated) return;

    try {
      const accessToken = getAccessToken();
      if (!accessToken) {
        throw new Error('No access token');
      }

      const response = await fetch('/api/tenants', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tenants');
      }

      const data = await response.json();
      setTenants(data.tenants || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch tenants:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch tenants'));
    }
  }, [user, isAuthenticated, getAccessToken]);

  /**
   * Fetch departments for current tenant
   */
  const fetchDepartments = useCallback(async (): Promise<void> => {
    if (!tenant || !isAuthenticated) return;

    try {
      const accessToken = getAccessToken();
      if (!accessToken) {
        throw new Error('No access token');
      }

      const response = await fetch(`/api/tenants/${tenant.id}/departments`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch departments');
      }

      const data = await response.json();
      setDepartments(data.departments || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch departments:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch departments'));
    }
  }, [tenant, isAuthenticated, getAccessToken]);

  /**
   * Fetch users for current tenant
   */
  const fetchUsers = useCallback(async (): Promise<void> => {
    if (!tenant || !isAuthenticated) return;

    try {
      const accessToken = getAccessToken();
      if (!accessToken) {
        throw new Error('No access token');
      }

      const response = await fetch(`/api/tenants/${tenant.id}/users`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data.users || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch users'));
    }
  }, [tenant, isAuthenticated, getAccessToken]);

  /**
   * Fetch all tenant data
   */
  const fetchTenantData = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      await Promise.all([fetchTenants(), fetchDepartments(), fetchUsers()]);
    } finally {
      setIsLoading(false);
    }
  }, [fetchTenants, fetchDepartments, fetchUsers]);

  /**
   * Switch to a different tenant
   */
  const switchTenant = useCallback(
    async (tenantId: string): Promise<void> => {
      setIsLoading(true);
      setError(null);

      try {
        await authSwitchTenant(tenantId);
        await fetchTenantData();
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to switch tenant');
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [authSwitchTenant, fetchTenantData]
  );

  /**
   * Get a specific tenant setting
   */
  const getTenantSetting = useCallback(
    (key: string): any => {
      if (!tenant || !tenant.settings) {
        return undefined;
      }
      return tenant.settings[key];
    },
    [tenant]
  );

  /**
   * Update a tenant setting
   */
  const updateTenantSetting = useCallback(
    async (key: string, value: any): Promise<void> => {
      if (!tenant) {
        throw new Error('No tenant selected');
      }

      setIsLoading(true);
      setError(null);

      try {
        const accessToken = getAccessToken();
        if (!accessToken) {
          throw new Error('No access token');
        }

        const response = await fetch(`/api/tenants/${tenant.id}/settings`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({ [key]: value }),
        });

        if (!response.ok) {
          throw new Error('Failed to update tenant setting');
        }

        // Update local state optimistically
        if (tenant.settings) {
          tenant.settings[key] = value;
        }

        setError(null);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to update tenant setting');
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [tenant, getAccessToken]
  );

  /**
   * Refresh tenant data
   */
  const refreshTenantData = useCallback(async (): Promise<void> => {
    await fetchTenantData();
  }, [fetchTenantData]);

  /**
   * Load tenant data when authenticated and tenant changes
   */
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchTenantData();
    }
  }, [isAuthenticated, user, tenant?.id, fetchTenantData]);

  const value: TenantContextValue = {
    currentTenant: tenant,
    tenants,
    departments,
    users,
    isLoading,
    error,
    switchTenant,
    getTenantSetting,
    updateTenantSetting,
    refreshTenantData,
  };

  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
};

/**
 * Custom hook to use tenant context
 * @throws {Error} If used outside of TenantProvider
 */
export const useTenant = (): TenantContextValue => {
  const context = useContext(TenantContext);
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
};
