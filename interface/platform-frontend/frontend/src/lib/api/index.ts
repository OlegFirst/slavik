/**
 * API Layer - Main Entry Point
 *
 * Exports all API functionality including:
 * - Client with interceptors
 * - Request methods
 * - Error handling
 * - Retry logic
 */

// Export API client
export { apiClient, APIClient } from './client';
export type { APIClientConfig } from './client';

// Export request methods
export {
  request,
  get,
  post,
  put,
  patch,
  del,
  uploadFile,
  downloadFile,
  getPaginated,
  batch,
  sequence,
  createCancelToken,
  isCancelError,
} from './request';
export type {
  RequestOptions,
  PaginatedRequestOptions,
  PaginatedResponse,
} from './request';

// Export error classes and utilities
export {
  APIError,
  AuthenticationError,
  AuthorizationError,
  ValidationError,
  NotFoundError,
  ConflictError,
  RateLimitError,
  ServerError,
  NetworkError,
  TimeoutError,
  parseAPIError,
  isAuthenticationError,
  isAuthorizationError,
  isValidationError,
  isNotFoundError,
  isServerError,
  isNetworkError,
  isRateLimitError,
  isTimeoutError,
} from './errors';

// Export retry utilities
export {
  retryRequest,
  retryAxiosRequest,
  retryWithLinearBackoff,
  retryImmediate,
  createRetryWrapper,
  defaultShouldRetry,
  calculateDelay,
  sleep,
} from './retry';
export type { RetryOptions } from './retry';
