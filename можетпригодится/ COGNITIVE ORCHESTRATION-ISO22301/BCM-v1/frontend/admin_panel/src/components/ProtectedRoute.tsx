import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth, UserRole } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole | UserRole[];
  requiredPermission?: string;
  fallbackPath?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredPermission,
  fallbackPath = '/login'
}) => {
  const { isAuthenticated, loading, hasRole, checkPermission } = useAuth();
  const location = useLocation();

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  // Check authentication
  if (!isAuthenticated) {
    // Save the attempted location
    return <Navigate to={fallbackPath} state={{ from: location }} replace />;
  }

  // Check role requirement
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <div className="max-w-md w-full bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-red-800 mb-2">Access Denied</h2>
          <p className="text-red-600 mb-4">
            You don't have the required role to access this page.
          </p>
          <p className="text-sm text-red-500">
            Required role: {Array.isArray(requiredRole) ? requiredRole.join(', ') : requiredRole}
          </p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Check permission requirement
  if (requiredPermission && !checkPermission(requiredPermission)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <div className="max-w-md w-full bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-yellow-800 mb-2">Permission Required</h2>
          <p className="text-yellow-600 mb-4">
            You don't have the required permission to access this feature.
          </p>
          <p className="text-sm text-yellow-500">
            Required permission: {requiredPermission}
          </p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // All checks passed, render children
  return <>{children}</>;
};

// Lazy loading wrapper for protected routes
export const LazyProtectedRoute: React.FC<{
  component: React.LazyExoticComponent<React.ComponentType<any>>;
  requiredRole?: UserRole | UserRole[];
  requiredPermission?: string;
}> = ({ component: Component, requiredRole, requiredPermission }) => {
  return (
    <ProtectedRoute requiredRole={requiredRole} requiredPermission={requiredPermission}>
      <React.Suspense fallback={
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      }>
        <Component />
      </React.Suspense>
    </ProtectedRoute>
  );
};

// Permission-based visibility component
export const CanAccess: React.FC<{
  role?: UserRole | UserRole[];
  permission?: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ role, permission, children, fallback = null }) => {
  const { hasRole, checkPermission } = useAuth();

  const hasAccess =
    (!role || hasRole(role)) &&
    (!permission || checkPermission(permission));

  return hasAccess ? <>{children}</> : <>{fallback}</>;
};