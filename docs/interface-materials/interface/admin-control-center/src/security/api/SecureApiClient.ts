import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { config } from '../../config/environment';
import { InputSanitizer } from '../validation/InputSanitizer';
import { useKeycloakAuth } from '../../auth/KeycloakAuthProvider';

class SecureApiClient {
  private client: AxiosInstance;
  private csrfToken: string | null = null;

  constructor() {
    // HTTPS enforcement from config
    const baseURL = config.security.httpsOnly
      ? config.api.baseUrl.replace('http://', 'https://')
      : config.api.baseUrl;

    this.client = axios.create({
      baseURL,
      timeout: config.api.timeout,
      withCredentials: true, // httpOnly cookies
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        // CORS headers
        'Access-Control-Allow-Origin': config.cors.allowedOrigins.join(','),
        'Access-Control-Allow-Credentials': 'true'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - добавляем CSRF + Keycloak token + Input validation
    this.client.interceptors.request.use(
      async (config) => {
        // Input validation для request data
        if (config.data) {
          config.data = InputSanitizer.validateApiResponse(config.data, {});
        }

        // Keycloak token
        const keycloakToken = this.getKeycloakToken();
        if (keycloakToken) {
          config.headers['Authorization'] = `Bearer ${keycloakToken}`;
        }

        // CSRF token
        if (!this.csrfToken && config.method !== 'get') {
          await this.refreshCSRFToken();
        }

        if (this.csrfToken) {
          config.headers['X-CSRF-Token'] = this.csrfToken;
        }

        // CORS validation
        if (!this.isAllowedOrigin(config.baseURL || '')) {
          throw new Error('CORS: Origin not allowed');
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - обрабатываем ошибки
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 403) {
          // CSRF token expired, refresh
          await this.refreshCSRFToken();
          return this.client.request(error.config);
        }

        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          window.location.href = '/login';
        }

        return Promise.reject(error);
      }
    );
  }

  private async refreshCSRFToken(): Promise<void> {
    try {
      const response = await axios.get(`${this.client.defaults.baseURL}/auth/csrf`, {
        withCredentials: true
      });
      this.csrfToken = response.data.token;
    } catch (error) {
      console.error('Failed to refresh CSRF token:', error);
    }
  }

  // Secure HTTP methods
  async get<T = any>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config);
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.post<T>(url, data, config);
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.put<T>(url, data, config);
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config);
  }

  // Keycloak token getter
  private getKeycloakToken(): string | undefined {
    // В реальном приложении получаем через useKeycloakAuth hook
    try {
      const keycloak = (window as any).keycloak;
      return keycloak?.token;
    } catch {
      return undefined;
    }
  }

  // CORS origin validation
  private isAllowedOrigin(url: string): boolean {
    try {
      const origin = new URL(url).origin;
      return config.cors.allowedOrigins.includes(origin) ||
             config.cors.allowedOrigins.includes('*');
    } catch {
      return false;
    }
  }

  // Rate limiting check
  private checkRateLimit(endpoint: string): void {
    const key = `rate_limit_${endpoint}`;
    const requests = JSON.parse(localStorage.getItem(key) || '[]');
    const now = Date.now();
    const minute = 60 * 1000;

    // Filter requests from last minute
    const recent = requests.filter((time: number) => now - time < minute);

    if (recent.length >= 100) { // 100 requests per minute
      throw new Error('Rate limit exceeded. Please try again later.');
    }

    recent.push(now);
    localStorage.setItem(key, JSON.stringify(recent));
  }
}

export const secureApiClient = new SecureApiClient();