/**
 * Standardized API Error Handling
 *
 * Provides error classes and parsing utilities for consistent error handling
 * across the application.
 */

import { AxiosError } from 'axios';

/**
 * Base API Error class
 */
export class APIError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly details?: any;
  public readonly timestamp: string;
  public readonly requestId?: string;

  constructor(
    message: string,
    statusCode: number = 500,
    code: string = 'INTERNAL_ERROR',
    details?: any,
    requestId?: string
  ) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
    this.timestamp = new Date().toISOString();
    this.requestId = requestId;

    // Maintains proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * Convert error to JSON format
   */
  public toJSON() {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      code: this.code,
      details: this.details,
      timestamp: this.timestamp,
      requestId: this.requestId,
    };
  }

  /**
   * Check if error is retryable
   */
  public isRetryable(): boolean {
    return this.statusCode >= 500 || this.statusCode === 429;
  }
}

/**
 * Authentication Error (401)
 */
export class AuthenticationError extends APIError {
  constructor(message: string = 'Authentication failed', details?: any, requestId?: string) {
    super(message, 401, 'AUTHENTICATION_ERROR', details, requestId);
    this.name = 'AuthenticationError';
  }
}

/**
 * Authorization Error (403)
 */
export class AuthorizationError extends APIError {
  constructor(
    message: string = 'Access forbidden',
    details?: any,
    requestId?: string
  ) {
    super(message, 403, 'AUTHORIZATION_ERROR', details, requestId);
    this.name = 'AuthorizationError';
  }
}

/**
 * Validation Error (400, 422)
 */
export class ValidationError extends APIError {
  public readonly errors?: Record<string, string[]>;

  constructor(
    message: string = 'Validation failed',
    errors?: Record<string, string[]>,
    details?: any,
    requestId?: string
  ) {
    super(message, 400, 'VALIDATION_ERROR', details, requestId);
    this.name = 'ValidationError';
    this.errors = errors;
  }

  public toJSON() {
    return {
      ...super.toJSON(),
      errors: this.errors,
    };
  }
}

/**
 * Not Found Error (404)
 */
export class NotFoundError extends APIError {
  constructor(
    message: string = 'Resource not found',
    details?: any,
    requestId?: string
  ) {
    super(message, 404, 'NOT_FOUND', details, requestId);
    this.name = 'NotFoundError';
  }
}

/**
 * Conflict Error (409)
 */
export class ConflictError extends APIError {
  constructor(
    message: string = 'Resource conflict',
    details?: any,
    requestId?: string
  ) {
    super(message, 409, 'CONFLICT_ERROR', details, requestId);
    this.name = 'ConflictError';
  }
}

/**
 * Rate Limit Error (429)
 */
export class RateLimitError extends APIError {
  public readonly retryAfter?: number;

  constructor(
    message: string = 'Rate limit exceeded',
    retryAfter?: number,
    details?: any,
    requestId?: string
  ) {
    super(message, 429, 'RATE_LIMIT_ERROR', details, requestId);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }

  public toJSON() {
    return {
      ...super.toJSON(),
      retryAfter: this.retryAfter,
    };
  }
}

/**
 * Server Error (500+)
 */
export class ServerError extends APIError {
  constructor(
    message: string = 'Internal server error',
    statusCode: number = 500,
    details?: any,
    requestId?: string
  ) {
    super(message, statusCode, 'SERVER_ERROR', details, requestId);
    this.name = 'ServerError';
  }
}

/**
 * Network Error (no response from server)
 */
export class NetworkError extends APIError {
  constructor(message: string = 'Network error', details?: any) {
    super(message, 0, 'NETWORK_ERROR', details);
    this.name = 'NetworkError';
  }

  public isRetryable(): boolean {
    return true;
  }
}

/**
 * Timeout Error
 */
export class TimeoutError extends APIError {
  constructor(message: string = 'Request timeout', details?: any, requestId?: string) {
    super(message, 408, 'TIMEOUT_ERROR', details, requestId);
    this.name = 'TimeoutError';
  }

  public isRetryable(): boolean {
    return true;
  }
}

/**
 * Parse Axios error into standardized APIError
 */
export function parseAPIError(error: any): APIError {
  // Extract request ID from headers if available
  const requestId = error.config?.headers?.['X-Request-ID'];

  // Handle Axios errors
  if (error.isAxiosError || error.response) {
    const axiosError = error as AxiosError<any>;

    // Network error (no response)
    if (!axiosError.response) {
      if (axiosError.code === 'ECONNABORTED' || axiosError.message.includes('timeout')) {
        return new TimeoutError(
          axiosError.message || 'Request timeout',
          { originalError: axiosError.message },
          requestId
        );
      }
      return new NetworkError(
        axiosError.message || 'Network error',
        { originalError: axiosError.message }
      );
    }

    const { status, data } = axiosError.response;
    const message = data?.message || data?.error || axiosError.message || 'An error occurred';
    const details = data?.details || data;

    // Map status codes to error classes
    switch (status) {
      case 400:
        return new ValidationError(message, data?.errors, details, requestId);

      case 401:
        return new AuthenticationError(message, details, requestId);

      case 403:
        return new AuthorizationError(message, details, requestId);

      case 404:
        return new NotFoundError(message, details, requestId);

      case 409:
        return new ConflictError(message, details, requestId);

      case 422:
        return new ValidationError(message, data?.errors, details, requestId);

      case 429:
        const retryAfter = axiosError.response.headers['retry-after'];
        return new RateLimitError(
          message,
          retryAfter ? parseInt(retryAfter, 10) : undefined,
          details,
          requestId
        );

      case 500:
      case 502:
      case 503:
      case 504:
        return new ServerError(message, status, details, requestId);

      default:
        if (status >= 500) {
          return new ServerError(message, status, details, requestId);
        }
        return new APIError(message, status, `HTTP_${status}`, details, requestId);
    }
  }

  // Handle generic errors
  if (error instanceof APIError) {
    return error;
  }

  // Unknown error type
  return new APIError(
    error.message || 'An unknown error occurred',
    500,
    'UNKNOWN_ERROR',
    { originalError: error }
  );
}

/**
 * Check if error is a specific type
 */
export function isAuthenticationError(error: any): error is AuthenticationError {
  return error instanceof AuthenticationError;
}

export function isAuthorizationError(error: any): error is AuthorizationError {
  return error instanceof AuthorizationError;
}

export function isValidationError(error: any): error is ValidationError {
  return error instanceof ValidationError;
}

export function isNotFoundError(error: any): error is NotFoundError {
  return error instanceof NotFoundError;
}

export function isServerError(error: any): error is ServerError {
  return error instanceof ServerError;
}

export function isNetworkError(error: any): error is NetworkError {
  return error instanceof NetworkError;
}

export function isRateLimitError(error: any): error is RateLimitError {
  return error instanceof RateLimitError;
}

export function isTimeoutError(error: any): error is TimeoutError {
  return error instanceof TimeoutError;
}
