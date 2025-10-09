/**
 * Infrastructure Coordinator API Client
 *
 * Управление Infrastructure Coordinator (Phase 1.1)
 * - Health Monitor
 * - Auto-Recovery
 * - Resource Optimizer
 * - EventBus Management
 * - Governance Layer (Decision Center)
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_COORDINATOR_API_URL || 'http://localhost:9092';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Types
// ============================================================================

export interface CoordinatorHealth {
  status: string;
  components: {
    eventbus: boolean;
    health_monitor: boolean;
    auto_recovery: boolean;
    resource_optimizer: boolean;
    decision_center: boolean;
    escalation_manager: boolean;
  };
  registered_services: number;
  uptime_seconds: number;
}

export interface ServiceHealth {
  service_name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  last_check: string;
  response_time_ms: number;
  consecutive_failures: number;
}

export interface RecoveryAction {
  id: string;
  timestamp: string;
  service_name: string;
  strategy: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  attempt_number: number;
  decision_approved: boolean;
}

export interface OptimizationRecommendation {
  id: string;
  timestamp: string;
  service_name: string;
  resource_type: 'cpu' | 'memory' | 'disk';
  current_usage: number;
  threshold: number;
  recommendation: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  auto_applied: boolean;
}

export interface EventBusStats {
  backend: 'memory' | 'redis';
  connected: boolean;
  total_events_published: number;
  total_subscriptions: number;
  active_consumers: number;
  queue_depth: number;
}

export interface CoordinatorStats {
  health_checks_total: number;
  recovery_attempts_total: number;
  recovery_successes: number;
  recovery_failures: number;
  optimizations_applied: number;
  escalations_triggered: number;
  avg_recovery_time_seconds: number;
}

// ============================================================================
// API Methods
// ============================================================================

export const coordinatorService = {
  /**
   * Get coordinator health
   */
  async getHealth(): Promise<CoordinatorHealth> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Get coordinator statistics
   */
  async getStats(): Promise<CoordinatorStats> {
    const response = await apiClient.get('/stats');
    return response.data;
  },

  /**
   * Get all monitored services health
   */
  async getServicesHealth(): Promise<ServiceHealth[]> {
    const response = await apiClient.get('/services/health');
    return response.data;
  },

  /**
   * Get specific service health
   */
  async getServiceHealth(serviceName: string): Promise<ServiceHealth> {
    const response = await apiClient.get(`/services/${serviceName}/health`);
    return response.data;
  },

  /**
   * Get recent recovery actions
   */
  async getRecoveryActions(limit: number = 50): Promise<RecoveryAction[]> {
    const response = await apiClient.get('/recovery/history', {
      params: { limit }
    });
    return response.data;
  },

  /**
   * Trigger manual recovery
   */
  async triggerRecovery(serviceName: string, strategy: string): Promise<RecoveryAction> {
    const response = await apiClient.post('/recovery/trigger', {
      service_name: serviceName,
      strategy: strategy
    });
    return response.data;
  },

  /**
   * Get optimization recommendations
   */
  async getOptimizationRecommendations(): Promise<OptimizationRecommendation[]> {
    const response = await apiClient.get('/optimization/recommendations');
    return response.data;
  },

  /**
   * Apply optimization recommendation
   */
  async applyOptimization(recommendationId: string): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/optimization/${recommendationId}/apply`);
    return response.data;
  },

  /**
   * Get EventBus statistics
   */
  async getEventBusStats(): Promise<EventBusStats> {
    const response = await apiClient.get('/eventbus/stats');
    return response.data;
  },

  /**
   * Get EventBus event stream (recent events)
   */
  async getEventStream(limit: number = 100): Promise<any[]> {
    const response = await apiClient.get('/eventbus/events', {
      params: { limit }
    });
    return response.data;
  },

  /**
   * Publish event to EventBus
   */
  async publishEvent(eventType: string, data: any): Promise<{ success: boolean; event_id: string }> {
    const response = await apiClient.post('/eventbus/publish', {
      event_type: eventType,
      data: data
    });
    return response.data;
  },

  /**
   * Start coordinator (if stopped)
   */
  async start(): Promise<{ success: boolean }> {
    const response = await apiClient.post('/coordinator/start');
    return response.data;
  },

  /**
   * Stop coordinator
   */
  async stop(): Promise<{ success: boolean }> {
    const response = await apiClient.post('/coordinator/stop');
    return response.data;
  },

  /**
   * Reload configuration
   */
  async reloadConfig(): Promise<{ success: boolean }> {
    const response = await apiClient.post('/coordinator/reload');
    return response.data;
  },

  /**
   * Get Prometheus metrics
   */
  async getMetrics(): Promise<string> {
    const response = await apiClient.get('/metrics');
    return response.data;
  },
};

export default coordinatorService;
