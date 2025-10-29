/**
 * Centralized API Error Handler for Workflow Management
 * Handles validation, network, and business logic errors
 */

import { ZodError } from 'zod'

export class WorkflowApiError extends Error {
  public readonly type: 'validation' | 'network' | 'business' | 'permission' | 'unknown'
  public readonly statusCode?: number
  public readonly details?: any
  public readonly timestamp: string

  constructor(
    message: string,
    type: WorkflowApiError['type'] = 'unknown',
    statusCode?: number,
    details?: any
  ) {
    super(message)
    this.name = 'WorkflowApiError'
    this.type = type
    this.statusCode = statusCode
    this.details = details
    this.timestamp = new Date().toISOString()
  }
}

export interface ErrorResponse {
  success: false
  error: string
  message: string
  type: WorkflowApiError['type']
  statusCode?: number
  details?: any
  timestamp: string
}

export interface SuccessResponse<T> {
  success: true
  data: T
  message?: string
  timestamp: string
}

export type ApiResult<T> = SuccessResponse<T> | ErrorResponse

/**
 * Centralized error handler for all API operations
 */
export function handleApiError(error: unknown): ErrorResponse {
  const timestamp = new Date().toISOString()

  // Validation errors (Zod)
  if (error instanceof ZodError) {
    return {
      success: false,
      error: 'Validation failed',
      message: error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '),
      type: 'validation',
      statusCode: 400,
      details: error.errors,
      timestamp
    }
  }

  // Custom workflow errors
  if (error instanceof WorkflowApiError) {
    return {
      success: false,
      error: error.message,
      message: error.message,
      type: error.type,
      statusCode: error.statusCode,
      details: error.details,
      timestamp
    }
  }

  // Network/HTTP errors
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const httpError = error as any
    const status = httpError.response?.status
    const data = httpError.response?.data

    // Specific HTTP status handling
    switch (status) {
      case 400:
        return {
          success: false,
          error: 'Bad Request',
          message: data?.message || 'Invalid request data',
          type: 'validation',
          statusCode: 400,
          details: data,
          timestamp
        }

      case 401:
        return {
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required',
          type: 'permission',
          statusCode: 401,
          timestamp
        }

      case 403:
        return {
          success: false,
          error: 'Forbidden',
          message: 'Insufficient permissions for this operation',
          type: 'permission',
          statusCode: 403,
          timestamp
        }

      case 404:
        return {
          success: false,
          error: 'Not Found',
          message: data?.message || 'Resource not found',
          type: 'business',
          statusCode: 404,
          timestamp
        }

      case 409:
        return {
          success: false,
          error: 'Conflict',
          message: data?.message || 'Resource already exists or conflict detected',
          type: 'business',
          statusCode: 409,
          details: data,
          timestamp
        }

      case 422:
        return {
          success: false,
          error: 'Unprocessable Entity',
          message: data?.message || 'Data validation failed on server',
          type: 'validation',
          statusCode: 422,
          details: data?.errors,
          timestamp
        }

      case 500:
        return {
          success: false,
          error: 'Internal Server Error',
          message: 'An internal server error occurred. Please try again later.',
          type: 'unknown',
          statusCode: 500,
          timestamp
        }

      case 503:
        return {
          success: false,
          error: 'Service Unavailable',
          message: 'Service is temporarily unavailable. Please try again later.',
          type: 'network',
          statusCode: 503,
          timestamp
        }

      default:
        return {
          success: false,
          error: 'HTTP Error',
          message: data?.message || `HTTP ${status} error occurred`,
          type: 'network',
          statusCode: status,
          details: data,
          timestamp
        }
    }
  }

  // Network connection errors
  if (typeof error === 'object' && error !== null && 'code' in error) {
    const networkError = error as any

    if (networkError.code === 'NETWORK_ERROR' || networkError.code === 'ERR_NETWORK') {
      return {
        success: false,
        error: 'Network Error',
        message: 'Unable to connect to server. Please check your internet connection.',
        type: 'network',
        timestamp
      }
    }

    if (networkError.code === 'ECONNABORTED') {
      return {
        success: false,
        error: 'Request Timeout',
        message: 'Request timed out. Please try again.',
        type: 'network',
        timestamp
      }
    }
  }

  // Generic error fallback
  const message = error instanceof Error ? error.message : 'An unknown error occurred'

  return {
    success: false,
    error: 'Unknown Error',
    message,
    type: 'unknown',
    timestamp
  }
}

/**
 * Wrapper for API calls with error handling and validation
 */
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  options: {
    validateInput?: (input: any) => void
    validateOutput?: (output: any) => T
    context?: string
  } = {}
): Promise<ApiResult<T>> {
  const { validateInput, validateOutput, context } = options

  try {
    // Input validation if provided
    if (validateInput) {
      validateInput(undefined) // Will be called with actual input in real usage
    }

    // Execute API call
    const result = await apiCall()

    // Output validation if provided
    const validatedResult = validateOutput ? validateOutput(result) : result

    return {
      success: true,
      data: validatedResult,
      timestamp: new Date().toISOString()
    }

  } catch (error) {
    const errorResponse = handleApiError(error)

    // Add context if provided
    if (context) {
      errorResponse.message = `${context}: ${errorResponse.message}`
    }

    // Log error for monitoring (в production это должно отправляться в Sentry/LogRocket)
    console.error(`[WorkflowAPI Error] ${context || 'API Call'}:`, {
      error: errorResponse,
      originalError: error,
      timestamp: errorResponse.timestamp
    })

    return errorResponse
  }
}

/**
 * Transaction-safe wrapper for multiple API calls
 */
export class ApiTransaction {
  private operations: Array<() => Promise<any>> = []
  private rollbackOperations: Array<() => Promise<any>> = []
  private results: any[] = []

  addOperation<T>(
    operation: () => Promise<T>,
    rollback?: () => Promise<any>
  ): ApiTransaction {
    this.operations.push(operation)
    if (rollback) {
      this.rollbackOperations.push(rollback)
    }
    return this
  }

  async execute(): Promise<ApiResult<any[]>> {
    try {
      // Execute all operations
      for (const operation of this.operations) {
        const result = await operation()
        this.results.push(result)
      }

      return {
        success: true,
        data: this.results,
        timestamp: new Date().toISOString()
      }

    } catch (error) {
      // Rollback in reverse order
      console.warn('Transaction failed, rolling back...', error)

      try {
        for (let i = this.rollbackOperations.length - 1; i >= 0; i--) {
          await this.rollbackOperations[i]()
        }
      } catch (rollbackError) {
        console.error('Rollback failed:', rollbackError)
      }

      return handleApiError(error)
    }
  }
}

/**
 * Retry mechanism for failed API calls
 */
export async function retryApiCall<T>(
  apiCall: () => Promise<T>,
  options: {
    maxRetries?: number
    delayMs?: number
    exponentialBackoff?: boolean
    retryCondition?: (error: any) => boolean
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    delayMs = 1000,
    exponentialBackoff = true,
    retryCondition = (error) => {
      // Retry on network errors and 5xx server errors
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const status = (error as any).response?.status
        return status >= 500 || !status // Network errors have no status
      }
      return false
    }
  } = options

  let lastError: any

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall()
    } catch (error) {
      lastError = error

      // Don't retry if this is the last attempt or if retry condition is not met
      if (attempt === maxRetries || !retryCondition(error)) {
        throw error
      }

      // Calculate delay with optional exponential backoff
      const delay = exponentialBackoff
        ? delayMs * Math.pow(2, attempt)
        : delayMs

      console.warn(`API call failed, retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries + 1})`, error)

      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  throw lastError
}

/**
 * Performance monitoring wrapper
 */
export async function monitoredApiCall<T>(
  apiCall: () => Promise<T>,
  operationName: string
): Promise<T> {
  const startTime = performance.now()

  try {
    const result = await apiCall()
    const duration = performance.now() - startTime

    // Log performance metrics (в production отправлять в мониторинг)
    console.info(`[API Performance] ${operationName}: ${duration.toFixed(2)}ms`)

    if (duration > 5000) { // Warn if operation takes more than 5 seconds
      console.warn(`[API Performance] Slow operation detected: ${operationName} (${duration.toFixed(2)}ms)`)
    }

    return result
  } catch (error) {
    const duration = performance.now() - startTime
    console.error(`[API Performance] Failed operation: ${operationName} (${duration.toFixed(2)}ms)`, error)
    throw error
  }
}

/**
 * Rate limiting helper
 */
export class RateLimiter {
  private requests: Map<string, number[]> = new Map()

  constructor(
    private maxRequests: number = 100,
    private windowMs: number = 60000 // 1 minute
  ) {}

  isAllowed(key: string = 'default'): boolean {
    const now = Date.now()
    const requests = this.requests.get(key) || []

    // Remove requests outside the window
    const validRequests = requests.filter(time => now - time < this.windowMs)

    if (validRequests.length >= this.maxRequests) {
      return false
    }

    validRequests.push(now)
    this.requests.set(key, validRequests)

    return true
  }

  getResetTime(key: string = 'default'): number {
    const requests = this.requests.get(key) || []
    if (requests.length === 0) return 0

    const oldestRequest = Math.min(...requests)
    return oldestRequest + this.windowMs
  }
}

// Global rate limiter instance
export const workflowApiRateLimiter = new RateLimiter(50, 60000) // 50 requests per minute