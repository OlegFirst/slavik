/**
 * API Client with Axios interceptors
 *
 * Features:
 * - Authentication token injection
 * - Tenant header management
 * - Request/response logging
 * - Error handling with retry logic
 * - Token refresh flow
 * - Request cancellation support
 * - Request deduplication
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { parseAPIError } from './errors';
import { retryRequest } from './retry';

/**
 * API client configuration
 */
export interface APIClientConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  retryEnabled?: boolean;
  deduplicationEnabled?: boolean;
}

/**
 * Request metadata for tracking and deduplication
 */
interface RequestMetadata {
  requestId: string;
  timestamp: number;
  url: string;
  method: string;
}

/**
 * Token refresh callback type
 */
type TokenRefreshCallback = () => Promise<string | null>;

class APIClient {
  private instance: AxiosInstance;
  private tokenRefreshCallback: TokenRefreshCallback | null = null;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (reason?: any) => void;
  }> = [];
  private pendingRequests = new Map<string, Promise<any>>();

  constructor(config: APIClientConfig = {}) {
    const {
      baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8024',
      timeout = 30000,
      headers = {},
      retryEnabled = true,
    } = config;

    // Create axios instance
    this.instance = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    });

    // Setup interceptors
    this.setupRequestInterceptor();
    this.setupResponseInterceptor();
  }

  /**
   * Setup request interceptor to add auth tokens and headers
   */
  private setupRequestInterceptor() {
    this.instance.interceptors.request.use(
      (config) => {
        // Generate unique request ID for tracing
        const requestId = uuidv4();
        config.headers['X-Request-ID'] = requestId;

        // Add authentication token
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add tenant ID from localStorage or context
        const tenantId = this.getTenantId();
        if (tenantId) {
          config.headers['X-Tenant-ID'] = tenantId;
        }

        // Add timestamp for request tracking
        config.headers['X-Request-Time'] = new Date().toISOString();

        // Log request in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
            requestId,
            data: config.data,
            params: config.params,
          });
        }

        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Setup response interceptor for error handling and token refresh
   */
  private setupResponseInterceptor() {
    this.instance.interceptors.response.use(
      (response) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`[API Response] ${response.status} ${response.config.url}`, {
            requestId: response.config.headers['X-Request-ID'],
            data: response.data,
          });
        }

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle 401 Unauthorized - Token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Queue the request while token is being refreshed
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                return this.instance(originalRequest);
              })
              .catch((err) => Promise.reject(err));
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newToken = await this.refreshToken();
            if (newToken) {
              // Update token in storage
              this.setAuthToken(newToken);

              // Retry all queued requests
              this.processQueue(null, newToken);

              // Retry original request
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
              }
              return this.instance(originalRequest);
            }
          } catch (refreshError) {
            this.processQueue(refreshError, null);
            this.handleAuthFailure();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // Handle 403 Forbidden
        if (error.response?.status === 403) {
          console.error('[API] Access forbidden:', error.response.data);
          // Optionally redirect to forbidden page
          if (typeof window !== 'undefined') {
            // window.location.href = '/forbidden';
          }
        }

        // Handle 404 Not Found
        if (error.response?.status === 404) {
          console.warn('[API] Resource not found:', originalRequest.url);
        }

        // Handle 500+ Server Errors with retry
        if (error.response?.status && error.response.status >= 500) {
          if (!originalRequest._retry) {
            return retryRequest(() => this.instance(originalRequest), {
              maxRetries: 3,
              shouldRetry: (err) => {
                const status = (err as AxiosError).response?.status;
                return status ? status >= 500 : true;
              },
            });
          }
        }

        // Handle network errors
        if (!error.response) {
          console.error('[API] Network error:', error.message);
        }

        // Parse and throw standardized error
        const apiError = parseAPIError(error);
        return Promise.reject(apiError);
      }
    );
  }

  /**
   * Process queued requests after token refresh
   */
  private processQueue(error: any, token: string | null = null) {
    this.failedQueue.forEach((promise) => {
      if (error) {
        promise.reject(error);
      } else {
        promise.resolve(token);
      }
    });
    this.failedQueue = [];
  }

  /**
   * Get authentication token from storage
   */
  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
  }

  /**
   * Set authentication token in storage
   */
  private setAuthToken(token: string) {
    if (typeof window === 'undefined') return;
    localStorage.setItem('auth_token', token);
  }

  /**
   * Get tenant ID from storage
   */
  private getTenantId(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('tenant_id');
  }

  /**
   * Refresh authentication token
   */
  private async refreshToken(): Promise<string | null> {
    if (this.tokenRefreshCallback) {
      return this.tokenRefreshCallback();
    }

    // Default refresh implementation
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return null;

      const response = await axios.post(
        `${this.instance.defaults.baseURL}/auth/refresh`,
        { refresh_token: refreshToken }
      );

      return response.data.access_token;
    } catch (error) {
      console.error('[API] Token refresh failed:', error);
      return null;
    }
  }

  /**
   * Handle authentication failure (logout)
   */
  private handleAuthFailure() {
    if (typeof window === 'undefined') return;

    // Clear tokens
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.clear();

    // Redirect to login
    window.location.href = '/login';
  }

  /**
   * Set custom token refresh callback
   */
  public setTokenRefreshCallback(callback: TokenRefreshCallback) {
    this.tokenRefreshCallback = callback;
  }

  /**
   * Get the axios instance
   */
  public getAxiosInstance(): AxiosInstance {
    return this.instance;
  }

  /**
   * Create a request key for deduplication
   */
  private createRequestKey(config: AxiosRequestConfig): string {
    const { method, url, params, data } = config;
    return `${method}:${url}:${JSON.stringify(params)}:${JSON.stringify(data)}`;
  }

  /**
   * Make a request with deduplication
   */
  public async request<T>(config: AxiosRequestConfig): Promise<T> {
    const requestKey = this.createRequestKey(config);

    // Check if identical request is already in flight
    if (this.pendingRequests.has(requestKey)) {
      console.log('[API] Deduplicating request:', requestKey);
      return this.pendingRequests.get(requestKey);
    }

    // Create new request promise
    const requestPromise = this.instance.request<T>(config).then((response) => response.data);

    // Store in pending requests
    this.pendingRequests.set(requestKey, requestPromise);

    // Remove from pending when complete
    requestPromise.finally(() => {
      this.pendingRequests.delete(requestKey);
    });

    return requestPromise;
  }

  /**
   * Clear all pending requests
   */
  public clearPendingRequests() {
    this.pendingRequests.clear();
  }
}

// Create default API client instance
export const apiClient = new APIClient();

// Export client class for custom instances
export { APIClient };
