# Error Boundary Components

Production-ready error boundary components for comprehensive error handling in React applications.

## Components

### 1. ErrorBoundary (Root-Level)

The main error boundary for catching React errors at the application root level.

**Features:**
- Catches all React errors in child components
- Generates unique error IDs for support tracking
- Reports errors to logging services (configurable)
- Development vs production mode support
- Stack trace display in development
- Automatic error reporting to backend

**Usage:**

```tsx
import { ErrorBoundary } from '@/components/errors';

function App() {
  return (
    <ErrorBoundary
      boundaryName="RootApp"
      onError={(error, errorInfo) => {
        // Custom error handling
        console.log('Error caught:', error);
      }}
    >
      <YourApp />
    </ErrorBoundary>
  );
}
```

**Props:**
- `children`: React components to wrap
- `fallback`: Custom fallback component (optional)
- `onError`: Callback when error is caught (optional)
- `boundaryName`: Name for logging/tracking (optional)

---

### 2. ErrorFallback

Generic error fallback UI component with a polished user experience.

**Features:**
- Friendly error message
- Unique error ID display
- Copy error details to clipboard
- Retry functionality
- Navigate to home page
- Contact support with pre-filled email
- Collapsible error details
- Stack trace (development mode only)
- Responsive design

**Usage:**

```tsx
import { ErrorBoundary, ErrorFallback } from '@/components/errors';

<ErrorBoundary fallback={ErrorFallback}>
  <YourComponent />
</ErrorBoundary>
```

---

### 3. RouteErrorBoundary

Lighter-weight error boundary for individual routes/pages.

**Features:**
- Page-specific error recovery
- Less disruptive than root boundary
- Automatic reset on route change
- Breadcrumb context in errors
- Smaller, focused fallback UI

**Usage:**

```tsx
import { RouteErrorBoundary } from '@/components/errors';

function DashboardPage() {
  return (
    <RouteErrorBoundary routeName="Dashboard">
      <DashboardContent />
    </RouteErrorBoundary>
  );
}
```

**Props:**
- `children`: Components to wrap
- `routeName`: Name of the route for context
- `onError`: Error callback (optional)
- `fallback`: Custom fallback component (optional)

---

### 4. AsyncBoundary

Combines React Suspense with Error Boundary for async component handling.

**Features:**
- Unified loading and error states
- Configurable timeout handling
- Custom loading fallback
- Custom error fallback
- Automatic retry on error
- Loading spinner integration

**Usage:**

```tsx
import { AsyncBoundary } from '@/components/errors';

function DataDisplay() {
  return (
    <AsyncBoundary
      suspenseFallback={<CustomLoadingSpinner />}
      loadingMessage="Loading data..."
      timeout={10000} // 10 seconds
      boundaryName="DataDisplay"
      onError={(error) => console.error(error)}
    >
      <AsyncDataComponent />
    </AsyncBoundary>
  );
}
```

**Props:**
- `children`: Async components to wrap
- `suspenseFallback`: Loading fallback component (optional)
- `errorFallback`: Error fallback component (optional)
- `onError`: Error callback (optional)
- `boundaryName`: Name for logging (optional)
- `timeout`: Timeout in milliseconds (optional)
- `loadingMessage`: Message to display while loading (optional)

---

### 5. QueryErrorBoundary

React Query specific error boundary with cache management.

**Features:**
- Reset React Query cache on error
- Query-specific error messages
- Network error detection
- API error handling
- Retry query functionality
- Clear cache option

**Usage:**

```tsx
import { QueryErrorBoundary } from '@/components/errors';

function UsersList() {
  return (
    <QueryErrorBoundary
      queryKeys={['users', 'posts']}
      onError={(error) => console.error('Query error:', error)}
    >
      <UsersDataTable />
    </QueryErrorBoundary>
  );
}
```

**Props:**
- `children`: Components to wrap
- `queryKeys`: Array of query keys to reset on error (optional)
- `onError`: Error callback (optional)
- `fallback`: Custom fallback component (optional)

---

## Error Boundary Hierarchy

For best results, use error boundaries at multiple levels:

```tsx
import {
  ErrorBoundary,
  RouteErrorBoundary,
  AsyncBoundary,
  QueryErrorBoundary,
} from '@/components/errors';

function App() {
  return (
    // Root level - catches all errors
    <ErrorBoundary boundaryName="RootApp">
      <Layout>
        {/* Route level - catches page-specific errors */}
        <RouteErrorBoundary routeName="Dashboard">
          {/* Query level - handles data fetching errors */}
          <QueryErrorBoundary queryKeys={['dashboard-data']}>
            {/* Async level - handles loading states */}
            <AsyncBoundary loadingMessage="Loading dashboard...">
              <DashboardPage />
            </AsyncBoundary>
          </QueryErrorBoundary>
        </RouteErrorBoundary>
      </Layout>
    </ErrorBoundary>
  );
}
```

---

## Error Reporting Integration

The ErrorBoundary component includes built-in error reporting. To integrate with services like Sentry:

```tsx
// In your ErrorBoundary or custom error handler:

import * as Sentry from '@sentry/react';

function reportError(error: Error, errorInfo: React.ErrorInfo, errorId: string) {
  Sentry.captureException(error, {
    contexts: {
      react: {
        componentStack: errorInfo.componentStack,
      },
      errorBoundary: {
        errorId,
      },
    },
  });
}
```

Or configure in the ErrorBoundary file at line ~70.

---

## Custom Fallback Components

Create custom fallback components by implementing the appropriate props interface:

```tsx
import type { ErrorFallbackProps } from '@/components/errors';

const CustomErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorInfo,
  errorId,
  onReset,
}) => {
  return (
    <div>
      <h1>Custom Error UI</h1>
      <p>Error: {error.message}</p>
      <p>Error ID: {errorId}</p>
      <button onClick={onReset}>Try Again</button>
    </div>
  );
};

// Use with ErrorBoundary
<ErrorBoundary fallback={CustomErrorFallback}>
  <YourComponent />
</ErrorBoundary>
```

---

## Development vs Production

The error boundaries automatically detect the environment:

**Development Mode:**
- Full stack traces displayed
- Component stack visible
- Detailed console logging
- Verbose error information

**Production Mode:**
- User-friendly error messages
- Error IDs for support
- Backend error reporting
- Minimal technical details

---

## Accessibility

All error boundaries include proper ARIA labels and semantic HTML:

- `role="status"` for loading states
- Descriptive `aria-label` attributes
- Keyboard navigation support
- Screen reader friendly error messages

---

## Styling

Components use Tailwind CSS with the project's color scheme:

- Orange tones for primary actions (`orange-600`, `orange-700`)
- Red tones for errors (`red-50`, `red-600`)
- Amber tones for warnings (`amber-600`)
- Responsive design with mobile-first approach

---

## TypeScript Support

All components are fully typed with exported interfaces:

```tsx
import type {
  ErrorBoundaryProps,
  ErrorFallbackProps,
  RouteErrorBoundaryProps,
  AsyncBoundaryProps,
  QueryErrorBoundaryProps,
} from '@/components/errors';
```

---

## Best Practices

1. **Use multiple boundaries**: Don't rely on a single root boundary
2. **Provide context**: Use `boundaryName` and `routeName` for better error tracking
3. **Custom handlers**: Implement `onError` callbacks for logging/analytics
4. **Test error states**: Simulate errors in development to verify boundaries work
5. **User-friendly messages**: Customize fallback components for better UX
6. **Monitor errors**: Integrate with error tracking services (Sentry, LogRocket)
7. **Reset strategies**: Consider when to auto-reset vs manual reset

---

## Testing Error Boundaries

Create a component that throws errors for testing:

```tsx
function ErrorThrower({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error for error boundary');
  }
  return <div>No error</div>;
}

// Test with:
<ErrorBoundary>
  <ErrorThrower shouldThrow={true} />
</ErrorBoundary>
```

---

## License

Part of the AI Platform ISO frontend application.
