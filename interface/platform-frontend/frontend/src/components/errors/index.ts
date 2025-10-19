/**
 * Error Boundary Components
 *
 * Comprehensive error handling components for production-ready React applications.
 * Includes root-level, route-level, async, and React Query specific error boundaries.
 */

// Root Error Boundary
export { ErrorBoundary } from './ErrorBoundary';
export type { ErrorBoundaryProps, ErrorFallbackProps } from './ErrorBoundary';

// Error Fallback UI
export { ErrorFallback } from './ErrorFallback';

// Route Error Boundary
export { RouteErrorBoundary } from './RouteErrorBoundary';
export type {
  RouteErrorBoundaryProps,
  RouteErrorFallbackProps,
} from './RouteErrorBoundary';

// Async Boundary (Suspense + Error Boundary)
export { AsyncBoundary } from './AsyncBoundary';
export type { AsyncBoundaryProps } from './AsyncBoundary';

// React Query Error Boundary
export { QueryErrorBoundary } from './QueryErrorBoundary';
export type {
  QueryErrorBoundaryProps,
  QueryErrorFallbackProps,
} from './QueryErrorBoundary';
