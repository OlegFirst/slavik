/**
 * High-level Request Wrapper
 *
 * Type-safe request methods with:
 * - Automatic retry
 * - Request deduplication
 * - Progress tracking
 * - Cache control
 * - Convenient method shortcuts
 */

import { AxiosRequestConfig, AxiosProgressEvent, CancelTokenSource } from 'axios';
import { apiClient } from './client';
import { retryRequest } from './retry';

/**
 * Request options interface
 */
export interface RequestOptions {
  /** HTTP method (default: GET) */
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';
  /** Request body data */
  data?: any;
  /** URL query parameters */
  params?: Record<string, any>;
  /** Custom headers */
  headers?: Record<string, string>;
  /** Enable automatic retry (default: true) */
  retry?: boolean;
  /** Number of retry attempts (default: 3) */
  maxRetries?: number;
  /** Enable request deduplication (default: true) */
  deduplicate?: boolean;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Upload progress callback */
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void;
  /** Download progress callback */
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void;
  /** Response type (default: json) */
  responseType?: 'json' | 'blob' | 'text' | 'arraybuffer' | 'document' | 'stream';
  /** Cancel token for request cancellation */
  cancelToken?: CancelTokenSource;
  /** Enable credentials (cookies) */
  withCredentials?: boolean;
  /** Custom error handler */
  onError?: (error: any) => void;
}

/**
 * Paginated request options
 */
export interface PaginatedRequestOptions extends Omit<RequestOptions, 'params'> {
  page?: number;
  pageSize?: number;
  params?: Record<string, any>;
}

/**
 * Paginated response interface
 */
export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

/**
 * Make a type-safe HTTP request
 *
 * @param url Request URL
 * @param options Request options
 * @returns Promise resolving to typed response data
 */
export async function request<T = any>(
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    method = 'GET',
    data,
    params,
    headers,
    retry = true,
    maxRetries = 3,
    deduplicate = true,
    timeout,
    onUploadProgress,
    onDownloadProgress,
    responseType = 'json',
    cancelToken,
    withCredentials,
    onError,
  } = options;

  // Build Axios config
  const config: AxiosRequestConfig = {
    url,
    method,
    data,
    params,
    headers,
    timeout,
    onUploadProgress,
    onDownloadProgress,
    responseType,
    cancelToken: cancelToken?.token,
    withCredentials,
  };

  // Request executor function
  const executeRequest = async (): Promise<T> => {
    if (deduplicate) {
      // Use deduplication from API client
      return apiClient.request<T>(config);
    } else {
      // Direct request without deduplication
      const response = await apiClient.getAxiosInstance().request<T>(config);
      return response.data as T;
    }
  };

  try {
    // Execute with retry if enabled
    if (retry) {
      return await retryRequest(executeRequest, {
        maxRetries,
        shouldRetry: (error) => {
          // Don't retry if request was cancelled
          if (cancelToken?.token.reason) {
            return false;
          }
          // Use default retry logic
          return error.isRetryable?.() ?? false;
        },
      });
    } else {
      return await executeRequest();
    }
  } catch (error) {
    // Call custom error handler if provided
    if (onError) {
      onError(error);
    }
    throw error;
  }
}

/**
 * GET request shorthand
 */
export async function get<T = any>(
  url: string,
  options?: Omit<RequestOptions, 'method' | 'data'>
): Promise<T> {
  return request<T>(url, { ...options, method: 'GET' });
}

/**
 * POST request shorthand
 */
export async function post<T = any>(
  url: string,
  data?: any,
  options?: Omit<RequestOptions, 'method' | 'data'>
): Promise<T> {
  return request<T>(url, { ...options, method: 'POST', data });
}

/**
 * PUT request shorthand
 */
export async function put<T = any>(
  url: string,
  data?: any,
  options?: Omit<RequestOptions, 'method' | 'data'>
): Promise<T> {
  return request<T>(url, { ...options, method: 'PUT', data });
}

/**
 * PATCH request shorthand
 */
export async function patch<T = any>(
  url: string,
  data?: any,
  options?: Omit<RequestOptions, 'method' | 'data'>
): Promise<T> {
  return request<T>(url, { ...options, method: 'PATCH', data });
}

/**
 * DELETE request shorthand
 */
export async function del<T = any>(
  url: string,
  options?: Omit<RequestOptions, 'method' | 'data'>
): Promise<T> {
  return request<T>(url, { ...options, method: 'DELETE' });
}

/**
 * Upload file with progress tracking
 */
export async function uploadFile<T = any>(
  url: string,
  file: File | Blob,
  fieldName: string = 'file',
  additionalData?: Record<string, any>,
  onProgress?: (percent: number) => void
): Promise<T> {
  const formData = new FormData();
  formData.append(fieldName, file);

  // Add additional fields
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, typeof value === 'object' ? JSON.stringify(value) : value);
    });
  }

  return post<T>(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });
}

/**
 * Download file with progress tracking
 */
export async function downloadFile(
  url: string,
  filename?: string,
  onProgress?: (percent: number) => void
): Promise<Blob> {
  const blob = await get<Blob>(url, {
    responseType: 'blob',
    onDownloadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });

  // Trigger download if filename provided
  if (filename && typeof window !== 'undefined') {
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  }

  return blob;
}

/**
 * Paginated GET request
 */
export async function getPaginated<T = any>(
  url: string,
  options?: PaginatedRequestOptions
): Promise<PaginatedResponse<T>> {
  const { page = 1, pageSize = 20, params, ...restOptions } = options || {};

  return get<PaginatedResponse<T>>(url, {
    ...restOptions,
    params: {
      ...params,
      page,
      page_size: pageSize,
    },
  });
}

/**
 * Batch multiple requests in parallel
 */
export async function batch<T = any>(
  requests: Array<{ url: string; options?: RequestOptions }>
): Promise<T[]> {
  const promises = requests.map(({ url, options }) => request<T>(url, options));
  return Promise.all(promises);
}

/**
 * Sequential requests (one after another)
 */
export async function sequence<T = any>(
  requests: Array<{ url: string; options?: RequestOptions }>
): Promise<T[]> {
  const results: T[] = [];

  for (const { url, options } of requests) {
    const result = await request<T>(url, options);
    results.push(result);
  }

  return results;
}

/**
 * Create a cancel token source for request cancellation
 */
export function createCancelToken(): CancelTokenSource {
  const axios = require('axios');
  return axios.CancelToken.source();
}

/**
 * Check if error is a cancellation error
 */
export function isCancelError(error: any): boolean {
  const axios = require('axios');
  return axios.isCancel(error);
}

// Re-export for convenience
export { apiClient } from './client';
export * from './errors';
export { retryRequest } from './retry';
