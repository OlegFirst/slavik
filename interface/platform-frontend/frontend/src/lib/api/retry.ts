/**
 * Retry Logic with Exponential Backoff
 *
 * Implements automatic retry for failed requests with:
 * - Exponential backoff
 * - Jitter to prevent thundering herd
 * - Configurable retry conditions
 * - Maximum retry limits
 */

import { AxiosError } from 'axios';
import { APIError } from './errors';

/**
 * Retry options configuration
 */
export interface RetryOptions {
  /** Maximum number of retry attempts (default: 3) */
  maxRetries?: number;
  /** Base delay in milliseconds (default: 1000) */
  baseDelay?: number;
  /** Maximum delay in milliseconds (default: 30000) */
  maxDelay?: number;
  /** Function to determine if error should be retried */
  shouldRetry?: (error: any) => boolean;
  /** Enable jitter to prevent thundering herd (default: true) */
  enableJitter?: boolean;
  /** Backoff multiplier (default: 2 for exponential) */
  backoffMultiplier?: number;
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 30000,
  shouldRetry: defaultShouldRetry,
  enableJitter: true,
  backoffMultiplier: 2,
};

/**
 * Default function to determine if an error should be retried
 */
export function defaultShouldRetry(error: any): boolean {
  // Retry network errors
  if (!error.response) {
    return true;
  }

  // Extract status code
  let statusCode: number | undefined;
  if (error.response?.status) {
    statusCode = error.response.status;
  } else if (error.statusCode) {
    statusCode = error.statusCode;
  }

  // Don't retry client errors (4xx) except 408, 429
  if (statusCode && statusCode >= 400 && statusCode < 500) {
    return statusCode === 408 || statusCode === 429;
  }

  // Retry server errors (5xx)
  if (statusCode && statusCode >= 500) {
    return true;
  }

  // Retry timeout errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return true;
  }

  // Don't retry by default
  return false;
}

/**
 * Calculate delay with exponential backoff and optional jitter
 */
export function calculateDelay(
  attempt: number,
  baseDelay: number,
  maxDelay: number,
  enableJitter: boolean = true,
  backoffMultiplier: number = 2
): number {
  // Calculate exponential backoff: baseDelay * (multiplier ^ attempt)
  const exponentialDelay = baseDelay * Math.pow(backoffMultiplier, attempt);

  // Cap at maximum delay
  const cappedDelay = Math.min(exponentialDelay, maxDelay);

  // Add jitter to prevent thundering herd problem
  if (enableJitter) {
    // Random jitter between 0 and cappedDelay
    const jitter = Math.random() * cappedDelay;
    return jitter;
  }

  return cappedDelay;
}

/**
 * Sleep utility function
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 *
 * @param fn Function to retry
 * @param options Retry configuration options
 * @returns Promise resolving to function result
 * @throws Last error if all retries exhausted
 */
export async function retryRequest<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const config = { ...DEFAULT_RETRY_OPTIONS, ...options };
  const {
    maxRetries,
    baseDelay,
    maxDelay,
    shouldRetry,
    enableJitter,
    backoffMultiplier,
  } = config;

  let lastError: any;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Attempt the request
      const result = await fn();

      // Log retry success if this wasn't the first attempt
      if (attempt > 0 && process.env.NODE_ENV === 'development') {
        console.log(`[Retry] Request succeeded on attempt ${attempt + 1}`);
      }

      return result;
    } catch (error) {
      lastError = error;

      // Check if we should retry
      const isLastAttempt = attempt === maxRetries;
      const shouldRetryError = shouldRetry(error);

      if (process.env.NODE_ENV === 'development') {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.log(
          `[Retry] Attempt ${attempt + 1}/${maxRetries + 1} failed:`,
          errorMessage
        );
      }

      // Don't retry if it's the last attempt or error is not retryable
      if (isLastAttempt || !shouldRetryError) {
        if (isLastAttempt && process.env.NODE_ENV === 'development') {
          console.error(`[Retry] All ${maxRetries + 1} attempts exhausted`);
        } else if (!shouldRetryError && process.env.NODE_ENV === 'development') {
          console.log('[Retry] Error is not retryable, skipping retry');
        }
        throw error;
      }

      // Calculate delay for next retry
      const delay = calculateDelay(
        attempt,
        baseDelay,
        maxDelay,
        enableJitter,
        backoffMultiplier
      );

      if (process.env.NODE_ENV === 'development') {
        console.log(`[Retry] Waiting ${Math.round(delay)}ms before retry...`);
      }

      // Wait before retrying
      await sleep(delay);
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError;
}

/**
 * Create a retry wrapper with preset configuration
 */
export function createRetryWrapper(options: RetryOptions) {
  return <T>(fn: () => Promise<T>) => retryRequest(fn, options);
}

/**
 * Retry specifically for Axios requests with status code awareness
 */
export async function retryAxiosRequest<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  return retryRequest(fn, {
    ...options,
    shouldRetry: (error: AxiosError | APIError) => {
      // Use custom shouldRetry if provided
      if (options.shouldRetry) {
        return options.shouldRetry(error);
      }

      // Default Axios-specific retry logic
      return defaultShouldRetry(error);
    },
  });
}

/**
 * Retry with custom backoff strategy (linear instead of exponential)
 */
export async function retryWithLinearBackoff<T>(
  fn: () => Promise<T>,
  options: Omit<RetryOptions, 'backoffMultiplier'> = {}
): Promise<T> {
  return retryRequest(fn, {
    ...options,
    backoffMultiplier: 1, // Linear backoff
  });
}

/**
 * Retry with immediate retry (no backoff)
 */
export async function retryImmediate<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  return retryRequest(fn, {
    maxRetries,
    baseDelay: 0,
    enableJitter: false,
  });
}
