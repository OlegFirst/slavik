import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { bcmAPI } from '@/services/api';

// User roles
export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  ANALYST = 'analyst',
  VIEWER = 'viewer'
}

// User interface
interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: string[];
  avatar?: string;
}

// Auth context interface
interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkPermission: (permission: string) => boolean;
  hasRole: (role: UserRole | UserRole[]) => boolean;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth Provider
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Check authentication status
  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Validate token with API
      const response = await bcmAPI.get('/auth/validate');
      if (response.data.valid) {
        setUser(response.data.user);
      } else {
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const response = await bcmAPI.post('/auth/login', { email, password });
      const { token, user } = response.data;

      // Store token
      localStorage.setItem('auth_token', token);

      // Set user
      setUser(user);

      // Update API client with token
      bcmAPI.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await bcmAPI.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      setUser(null);
      delete bcmAPI.defaults.headers.common['Authorization'];
    }
  };

  // Check if user has specific permission
  const checkPermission = (permission: string): boolean => {
    if (!user) return false;
    if (user.role === UserRole.ADMIN) return true; // Admin has all permissions
    return user.permissions.includes(permission);
  };

  // Check if user has specific role
  const hasRole = (role: UserRole | UserRole[]): boolean => {
    if (!user) return false;
    const roles = Array.isArray(role) ? role : [role];
    return roles.includes(user.role);
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
    checkPermission,
    hasRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// HOC for protecting components
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  requiredRole?: UserRole | UserRole[],
  requiredPermission?: string
) => {
  return (props: P) => {
    const { isAuthenticated, hasRole, checkPermission } = useAuth();

    // Check authentication
    if (!isAuthenticated) {
      return (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Authentication Required</h2>
            <p className="text-gray-600">Please login to access this page</p>
          </div>
        </div>
      );
    }

    // Check role
    if (requiredRole && !hasRole(requiredRole)) {
      return (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Access Denied</h2>
            <p className="text-gray-600">You don't have permission to access this page</p>
          </div>
        </div>
      );
    }

    // Check permission
    if (requiredPermission && !checkPermission(requiredPermission)) {
      return (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Permission Denied</h2>
            <p className="text-gray-600">You don't have the required permission: {requiredPermission}</p>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };
};