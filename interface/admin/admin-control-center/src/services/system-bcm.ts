/**
 * System BCM Service API Client
 *
 * REAL API integration - NO MOCKS!
 * Connects to System BCM Service on port 8050
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_SYSTEM_BCM_API_URL || 'http://localhost:8050';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[System BCM API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[System BCM API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[System BCM API] Response:`, response.status, response.statusText);
    return response;
  },
  (error) => {
    console.error('[System BCM API] Response error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// ============================================================================
// Types
// ============================================================================

export interface SystemBCMHealth {
  status: string;
  running: boolean;
  eventbus_connected: boolean;
  last_cycle: string | null;
  cycle_count: number;
  total_improvements: number;
}

export interface SystemBCMStatus {
  service: string;
  version: string;
  status: string;
  running: boolean;
  cycle_count: number;
  last_cycle_time: string | null;
  last_cycle_result: BCMCycleResult | null;
  total_improvements_applied: number;
  eventbus_status: string;
}

export interface BCMCycleResult {
  cycle_number: number;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  status: string;
  integrated_cycle: any;
  improvements_applied: number;
  integration_metrics: IntegrationMetrics;
}

export interface IntegrationMetrics {
  patterns_detected: number;
  knowledge_shared_with_community: number;
  ai_specialists_consulted: number;
  insights_generated: number;
  platform_health_score: number;
}

export interface SystemBCMMetrics {
  system_bcm_cycles_total: number;
  system_bcm_improvements_total: number;
  system_bcm_patterns_shared_total: number;
  system_bcm_specialists_consulted_total: number;
  system_bcm_running: number;
  system_bcm_cycle_duration_seconds: number;
  system_bcm_insights_generated: number;
  system_bcm_platform_health_score: number;
  system_bcm_patterns_detected: number;
  system_bcm_knowledge_shared: number;
}

export interface TriggerCycleResponse {
  cycle_number: number;
  start_time: string;
  status: string;
  message: string;
}

export interface RecoveryTriggerRequest {
  service: string;
  incident_type: string;
}

export interface RecoveryTriggerResponse {
  status: string;
  service: string;
  type: string;
  timestamp: string;
}

// ============================================================================
// API Methods
// ============================================================================

export const systemBCMService = {
  /**
   * Get health check
   * GET /health
   */
  async getHealth(): Promise<SystemBCMHealth> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Get detailed status
   * GET /status
   */
  async getStatus(): Promise<SystemBCMStatus> {
    const response = await apiClient.get('/status');
    return response.data;
  },

  /**
   * Get Prometheus metrics
   * GET /metrics
   */
  async getMetrics(): Promise<string> {
    const response = await apiClient.get('/metrics');
    return response.data;
  },

  /**
   * Parse Prometheus metrics into structured object
   */
  parseMetrics(metricsText: string): Partial<SystemBCMMetrics> {
    const metrics: Partial<SystemBCMMetrics> = {};
    const lines = metricsText.split('\n');

    for (const line of lines) {
      if (line.startsWith('#') || !line.trim()) continue;

      const parts = line.split(' ');
      if (parts.length >= 2) {
        const key = parts[0] as keyof SystemBCMMetrics;
        const value = parseFloat(parts[1]);

        if (!isNaN(value)) {
          metrics[key] = value;
        }
      }
    }

    return metrics;
  },

  /**
   * Trigger BCM cycle manually
   * POST /cycle/trigger
   */
  async triggerCycle(): Promise<TriggerCycleResponse> {
    const response = await apiClient.post('/cycle/trigger');
    return response.data;
  },

  /**
   * Trigger recovery procedure manually
   * POST /recovery/trigger
   */
  async triggerRecovery(data: RecoveryTriggerRequest): Promise<RecoveryTriggerResponse> {
    const response = await apiClient.post('/recovery/trigger', null, {
      params: data
    });
    return response.data;
  },

  /**
   * Get cycle history (if endpoint exists)
   * GET /cycle/history
   */
  async getCycleHistory(limit: number = 10): Promise<BCMCycleResult[]> {
    try {
      const response = await apiClient.get('/cycle/history', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.warn('[System BCM] Cycle history endpoint not available');
      return [];
    }
  },

  /**
   * Get recovery history (if endpoint exists)
   * GET /recovery/history
   */
  async getRecoveryHistory(limit: number = 10): Promise<any[]> {
    try {
      const response = await apiClient.get('/recovery/history', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.warn('[System BCM] Recovery history endpoint not available');
      return [];
    }
  },

  /**
   * Get learning insights (if endpoint exists)
   * GET /insights
   */
  async getInsights(): Promise<any[]> {
    try {
      const response = await apiClient.get('/insights');
      return response.data;
    } catch (error) {
      console.warn('[System BCM] Insights endpoint not available');
      return [];
    }
  },

  /**
   * Get detected patterns (if endpoint exists)
   * GET /patterns
   */
  async getPatterns(): Promise<any[]> {
    try {
      const response = await apiClient.get('/patterns');
      return response.data;
    } catch (error) {
      console.warn('[System BCM] Patterns endpoint not available');
      return [];
    }
  },

  /**
   * Get learning effectiveness (if endpoint exists)
   * GET /learning/effectiveness
   */
  async getLearningEffectiveness(): Promise<any> {
    try {
      const response = await apiClient.get('/learning/effectiveness');
      return response.data;
    } catch (error) {
      console.warn('[System BCM] Learning effectiveness endpoint not available');
      return null;
    }
  },
};

export default systemBCMService;
