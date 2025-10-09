// SECURITY UPDATE: Replace insecure localStorage with SecureApiClient
import { secureApiClient } from '../security/api/SecureApiClient';
import { config } from '../config/environment';

// Legacy API exports - redirected to secure implementation
export const bcmAPI = {
  get: (url: string, config?: any) => secureApiClient.get(url, config),
  post: (url: string, data?: any, config?: any) => secureApiClient.post(url, data, config),
  put: (url: string, data?: any, config?: any) => secureApiClient.put(url, data, config),
  delete: (url: string, config?: any) => secureApiClient.delete(url, config)
};

// Prometheus API Client - secured
export const prometheusAPI = {
  get: (url: string, config?: any) => secureApiClient.get(`${config.api.baseUrl}/prometheus/api/v1${url}`, config),
  post: (url: string, data?: any, config?: any) => secureApiClient.post(`${config.api.baseUrl}/prometheus/api/v1${url}`, data, config)
};

// Docker API Client - secured
export const dockerAPI = {
  get: (url: string, config?: any) => secureApiClient.get(`${config.api.baseUrl}/api/docker${url}`, config),
  post: (url: string, data?: any, config?: any) => secureApiClient.post(`${config.api.baseUrl}/api/docker${url}`, data, config)
};
