/**
 * Error Boundary Usage Examples
 *
 * This file contains practical examples of how to use each error boundary component.
 * These examples can be referenced when implementing error handling in your application.
 */

'use client';

import React, { Suspense } from 'react';
import {
  ErrorBoundary,
  RouteErrorBoundary,
  AsyncBoundary,
  QueryErrorBoundary,
} from './index';
import type { ErrorFallbackProps } from './ErrorBoundary';

// ============================================================================
// Example 1: Basic Root Error Boundary
// ============================================================================

export function Example1_RootErrorBoundary() {
  return (
    <ErrorBoundary boundaryName="AppRoot">
      <App />
    </ErrorBoundary>
  );
}

// ============================================================================
// Example 2: Error Boundary with Custom Error Handler
// ============================================================================

export function Example2_CustomErrorHandler() {
  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    // Send to analytics
    console.log('Sending error to analytics:', error.message);

    // Log to monitoring service
    // logToMonitoring({ error, errorInfo });
  };

  return (
    <ErrorBoundary boundaryName="CustomHandler" onError={handleError}>
      <YourComponent />
    </ErrorBoundary>
  );
}

// ============================================================================
// Example 3: Custom Error Fallback Component
// ============================================================================

const CustomErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorId,
  onReset,
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Custom Error Page
        </h1>
        <p className="text-gray-600 mb-4">{error.message}</p>
        <p className="text-sm text-gray-500 mb-4">Error ID: {errorId}</p>
        <button
          onClick={onReset}
          className="w-full px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
        >
          Try Again
        </button>
      </div>
    </div>
  );
};

export function Example3_CustomFallback() {
  return (
    <ErrorBoundary fallback={CustomErrorFallback} boundaryName="CustomUI">
      <YourComponent />
    </ErrorBoundary>
  );
}

// ============================================================================
// Example 4: Route Error Boundary for Pages
// ============================================================================

export function Example4_RouteBoundary() {
  return (
    <RouteErrorBoundary
      routeName="Dashboard"
      onError={(error) => console.error('Dashboard error:', error)}
    >
      <DashboardPage />
    </RouteErrorBoundary>
  );
}

// ============================================================================
// Example 5: Async Boundary with Loading State
// ============================================================================

export function Example5_AsyncBoundary() {
  return (
    <AsyncBoundary
      loadingMessage="Loading user data..."
      timeout={10000} // 10 second timeout
      boundaryName="UserData"
    >
      <Suspense fallback={<div>Loading...</div>}>
        <AsyncUserComponent />
      </Suspense>
    </AsyncBoundary>
  );
}

// ============================================================================
// Example 6: Query Error Boundary with React Query
// ============================================================================

export function Example6_QueryBoundary() {
  return (
    <QueryErrorBoundary
      queryKeys={['users', 'posts']}
      onError={(error) => console.error('Query failed:', error)}
    >
      <UsersDataTable />
    </QueryErrorBoundary>
  );
}

// ============================================================================
// Example 7: Nested Error Boundaries (Recommended Pattern)
// ============================================================================

export function Example7_NestedBoundaries() {
  return (
    // Root level - catches everything
    <ErrorBoundary boundaryName="App">
      <Layout>
        <Sidebar />

        {/* Route level - catches page errors */}
        <RouteErrorBoundary routeName="Dashboard">

          {/* Query level - handles data fetching */}
          <QueryErrorBoundary queryKeys={['dashboard']}>

            {/* Async level - handles loading */}
            <AsyncBoundary loadingMessage="Loading dashboard...">
              <DashboardContent />
            </AsyncBoundary>

          </QueryErrorBoundary>
        </RouteErrorBoundary>
      </Layout>
    </ErrorBoundary>
  );
}

// ============================================================================
// Example 8: Multiple Route Boundaries
// ============================================================================

export function Example8_MultipleRoutes() {
  return (
    <ErrorBoundary boundaryName="App">
      <Router>
        <Route path="/dashboard">
          <RouteErrorBoundary routeName="Dashboard">
            <DashboardPage />
          </RouteErrorBoundary>
        </Route>

        <Route path="/users">
          <RouteErrorBoundary routeName="Users">
            <UsersPage />
          </RouteErrorBoundary>
        </Route>

        <Route path="/settings">
          <RouteErrorBoundary routeName="Settings">
            <SettingsPage />
          </RouteErrorBoundary>
        </Route>
      </Router>
    </ErrorBoundary>
  );
}

// ============================================================================
// Example 9: Conditional Error Boundaries
// ============================================================================

export function Example9_ConditionalBoundary({ useErrorBoundary = true }) {
  const content = <YourComponent />;

  if (useErrorBoundary) {
    return (
      <ErrorBoundary boundaryName="ConditionalBoundary">
        {content}
      </ErrorBoundary>
    );
  }

  return content;
}

// ============================================================================
// Example 10: Error Boundary with Reset on Route Change
// ============================================================================

export function Example10_ResetOnRouteChange() {
  const [routeKey, setRouteKey] = React.useState(0);

  // Reset error boundary when route changes
  React.useEffect(() => {
    setRouteKey(prev => prev + 1);
  }, [/* route dependency */]);

  return (
    <ErrorBoundary key={routeKey} boundaryName="RouteReset">
      <YourComponent />
    </ErrorBoundary>
  );
}

// ============================================================================
// Mock Components (for demonstration purposes)
// ============================================================================

function App() {
  return <div>App Component</div>;
}

function YourComponent() {
  return <div>Your Component</div>;
}

function DashboardPage() {
  return <div>Dashboard Page</div>;
}

function DashboardContent() {
  return <div>Dashboard Content</div>;
}

function AsyncUserComponent() {
  return <div>Async User Component</div>;
}

function UsersDataTable() {
  return <div>Users Data Table</div>;
}

function Layout({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
}

function Sidebar() {
  return <div>Sidebar</div>;
}

function Router({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
}

function Route({ path, children }: { path: string; children: React.ReactNode }) {
  return <div data-path={path}>{children}</div>;
}

function UsersPage() {
  return <div>Users Page</div>;
}

function SettingsPage() {
  return <div>Settings Page</div>;
}
