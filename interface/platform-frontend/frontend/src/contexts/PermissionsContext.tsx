import React, { createContext, useContext, useMemo, ReactNode } from 'react';
import { useAuth, UserRole } from './AuthContext';

/**
 * Permission types for different resources
 */
export type Permission =
  // Document permissions
  | 'documents:create'
  | 'documents:view'
  | 'documents:edit:own'
  | 'documents:edit:all'
  | 'documents:delete:own'
  | 'documents:delete:all'
  | 'documents:approve'
  // BIA permissions
  | 'bia:create'
  | 'bia:view'
  | 'bia:edit:own'
  | 'bia:edit:all'
  | 'bia:delete:own'
  | 'bia:delete:all'
  | 'bia:approve'
  // User management
  | 'users:view'
  | 'users:create'
  | 'users:edit'
  | 'users:delete'
  | 'users:manage'
  // Settings
  | 'settings:view'
  | 'settings:edit'
  | 'settings:manage'
  // Tenant management
  | 'tenant:view'
  | 'tenant:edit'
  | 'tenant:manage'
  // Workflow permissions
  | 'workflows:create'
  | 'workflows:edit:own'
  | 'workflows:edit:all'
  | 'workflows:delete:own'
  | 'workflows:delete:all'
  // Report permissions
  | 'reports:view'
  | 'reports:create'
  | 'reports:export';

/**
 * Role-based permission mapping
 */
const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  ADMIN: [
    // All permissions (wildcard handled separately)
    'documents:create',
    'documents:view',
    'documents:edit:own',
    'documents:edit:all',
    'documents:delete:own',
    'documents:delete:all',
    'documents:approve',
    'bia:create',
    'bia:view',
    'bia:edit:own',
    'bia:edit:all',
    'bia:delete:own',
    'bia:delete:all',
    'bia:approve',
    'users:view',
    'users:create',
    'users:edit',
    'users:delete',
    'users:manage',
    'settings:view',
    'settings:edit',
    'settings:manage',
    'tenant:view',
    'tenant:edit',
    'tenant:manage',
    'workflows:create',
    'workflows:edit:own',
    'workflows:edit:all',
    'workflows:delete:own',
    'workflows:delete:all',
    'reports:view',
    'reports:create',
    'reports:export',
  ],
  MANAGER: [
    'documents:create',
    'documents:view',
    'documents:edit:own',
    'documents:edit:all',
    'documents:delete:own',
    'documents:delete:all',
    'documents:approve',
    'bia:create',
    'bia:view',
    'bia:edit:own',
    'bia:edit:all',
    'bia:delete:own',
    'bia:delete:all',
    'bia:approve',
    'users:view',
    'settings:view',
    'tenant:view',
    'workflows:create',
    'workflows:edit:own',
    'workflows:edit:all',
    'workflows:delete:own',
    'reports:view',
    'reports:create',
    'reports:export',
  ],
  USER: [
    'documents:create',
    'documents:view',
    'documents:edit:own',
    'documents:delete:own',
    'bia:create',
    'bia:view',
    'bia:edit:own',
    'bia:delete:own',
    'settings:view',
    'tenant:view',
    'workflows:create',
    'workflows:edit:own',
    'workflows:delete:own',
    'reports:view',
    'reports:create',
  ],
  VIEWER: [
    'documents:view',
    'bia:view',
    'settings:view',
    'tenant:view',
    'reports:view',
  ],
};

/**
 * Resource ownership context for permission checking
 */
export interface ResourceOwnership {
  ownerId: string;
  createdBy?: string;
}

/**
 * Permissions context value
 */
export interface PermissionsContextValue {
  // Check if user has a specific permission
  hasPermission: (permission: Permission) => boolean;

  // Check multiple permissions (AND logic)
  hasAllPermissions: (permissions: Permission[]) => boolean;

  // Check multiple permissions (OR logic)
  hasAnyPermission: (permissions: Permission[]) => boolean;

  // Resource-based permission checks
  canEditResource: (resource: ResourceOwnership) => boolean;
  canDeleteResource: (resource: ResourceOwnership) => boolean;

  // Get all permissions for current user
  getUserPermissions: () => Permission[];

  // Check if user has admin privileges
  isAdmin: () => boolean;

  // Check if user has manager privileges
  isManager: () => boolean;
}

/**
 * Permissions context
 */
const PermissionsContext = createContext<PermissionsContextValue | undefined>(undefined);

/**
 * Permissions provider props
 */
interface PermissionsProviderProps {
  children: ReactNode;
}

/**
 * PermissionsProvider component that manages permission checking
 */
export const PermissionsProvider: React.FC<PermissionsProviderProps> = ({ children }) => {
  const { user } = useAuth();

  /**
   * Get all permissions for current user (memoized)
   */
  const getUserPermissions = useMemo((): Permission[] => {
    if (!user) return [];
    return ROLE_PERMISSIONS[user.role] || [];
  }, [user]);

  /**
   * Check if user has a specific permission
   */
  const hasPermission = useMemo(
    () => (permission: Permission): boolean => {
      if (!user) return false;

      // Admin has all permissions
      if (user.role === 'ADMIN') return true;

      return getUserPermissions.includes(permission);
    },
    [user, getUserPermissions]
  );

  /**
   * Check if user has all specified permissions (AND logic)
   */
  const hasAllPermissions = useMemo(
    () => (permissions: Permission[]): boolean => {
      return permissions.every((permission) => hasPermission(permission));
    },
    [hasPermission]
  );

  /**
   * Check if user has any of the specified permissions (OR logic)
   */
  const hasAnyPermission = useMemo(
    () => (permissions: Permission[]): boolean => {
      return permissions.some((permission) => hasPermission(permission));
    },
    [hasPermission]
  );

  /**
   * Check if user can edit a resource
   * Checks both ownership-based and global edit permissions
   */
  const canEditResource = useMemo(
    () => (resource: ResourceOwnership): boolean => {
      if (!user) return false;

      // Check global edit permission
      if (hasPermission('documents:edit:all')) return true;

      // Check ownership-based edit permission
      const isOwner = resource.ownerId === user.id || resource.createdBy === user.id;
      return isOwner && hasPermission('documents:edit:own');
    },
    [user, hasPermission]
  );

  /**
   * Check if user can delete a resource
   * Checks both ownership-based and global delete permissions
   */
  const canDeleteResource = useMemo(
    () => (resource: ResourceOwnership): boolean => {
      if (!user) return false;

      // Check global delete permission
      if (hasPermission('documents:delete:all')) return true;

      // Check ownership-based delete permission
      const isOwner = resource.ownerId === user.id || resource.createdBy === user.id;
      return isOwner && hasPermission('documents:delete:own');
    },
    [user, hasPermission]
  );

  /**
   * Check if user is admin
   */
  const isAdmin = useMemo(
    () => (): boolean => {
      return user?.role === 'ADMIN';
    },
    [user]
  );

  /**
   * Check if user is manager or above
   */
  const isManager = useMemo(
    () => (): boolean => {
      return user?.role === 'ADMIN' || user?.role === 'MANAGER';
    },
    [user]
  );

  const value: PermissionsContextValue = {
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    canEditResource,
    canDeleteResource,
    getUserPermissions: () => getUserPermissions,
    isAdmin,
    isManager,
  };

  return <PermissionsContext.Provider value={value}>{children}</PermissionsContext.Provider>;
};

/**
 * Custom hook to use permissions context
 * @throws {Error} If used outside of PermissionsProvider
 */
export const usePermissions = (): PermissionsContextValue => {
  const context = useContext(PermissionsContext);
  if (context === undefined) {
    throw new Error('usePermissions must be used within a PermissionsProvider');
  }
  return context;
};

/**
 * HOC to require specific permissions for a component
 */
export function withPermissions<P extends object>(
  Component: React.ComponentType<P>,
  requiredPermissions: Permission[],
  FallbackComponent?: React.ComponentType
): React.FC<P> {
  return function PermissionGatedComponent(props: P) {
    const { hasAllPermissions } = usePermissions();

    if (!hasAllPermissions(requiredPermissions)) {
      if (FallbackComponent) {
        return <FallbackComponent />;
      }
      return null;
    }

    return <Component {...props} />;
  };
}
