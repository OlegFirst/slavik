/**
 * Real-time Data Integration Service
 * ==================================
 *
 * NO MOCK DATA - All data fetched from real AI Platform services
 * Integrates with Prometheus, Grafana, and platform tools
 */

import axios, { AxiosInstance } from 'axios';
import {
  getPlatformHealth,
  getServiceStatus,
  orchestratorAPI,
  workflowAPI,
  communityAPI,
  predictiveAPI,
  analyticsAPI,
  type ServiceStatus
} from './platform';

// ============================================================================
// PROMETHEUS INTEGRATION - Real metrics from Prometheus
// ============================================================================

const prometheusClient = axios.create({
  baseURL: '/prometheus',
  timeout: 10000,
});

export interface PrometheusMetric {
  metric: Record<string, string>;
  value: [number, string]; // [timestamp, value]
}

export interface PrometheusQueryResult {
  status: 'success' | 'error';
  data: {
    resultType: 'vector' | 'matrix' | 'scalar' | 'string';
    result: PrometheusMetric[];
  };
}

export const prometheusService = {
  /**
   * Query Prometheus for instant metrics
   */
  async query(promql: string): Promise<PrometheusQueryResult> {
    const response = await prometheusClient.get('/api/v1/query', {
      params: { query: promql }
    });
    return response.data;
  },

  /**
   * Query Prometheus for range metrics
   */
  async queryRange(
    promql: string,
    start: number,
    end: number,
    step: string = '15s'
  ): Promise<PrometheusQueryResult> {
    const response = await prometheusClient.get('/api/v1/query_range', {
      params: { query: promql, start, end, step }
    });
    return response.data;
  },

  /**
   * Get CPU usage for all services
   */
  async getCPUUsage(): Promise<Record<string, number>> {
    const result = await this.query(
      'rate(process_cpu_seconds_total[5m]) * 100'
    );

    const cpuByService: Record<string, number> = {};
    result.data.result.forEach(metric => {
      const service = metric.metric.job || metric.metric.instance;
      const value = parseFloat(metric.value[1]);
      cpuByService[service] = Math.round(value * 10) / 10;
    });

    return cpuByService;
  },

  /**
   * Get memory usage for all services
   */
  async getMemoryUsage(): Promise<Record<string, number>> {
    const result = await this.query(
      'process_resident_memory_bytes / 1024 / 1024'
    );

    const memoryByService: Record<string, number> = {};
    result.data.result.forEach(metric => {
      const service = metric.metric.job || metric.metric.instance;
      const value = parseFloat(metric.value[1]);
      memoryByService[service] = Math.round(value);
    });

    return memoryByService;
  },

  /**
   * Get service uptime
   */
  async getUptime(): Promise<Record<string, number>> {
    const result = await this.query('process_uptime_seconds');

    const uptimeByService: Record<string, number> = {};
    result.data.result.forEach(metric => {
      const service = metric.metric.job || metric.metric.instance;
      const value = parseFloat(metric.value[1]);
      uptimeByService[service] = Math.round(value);
    });

    return uptimeByService;
  },

  /**
   * Get HTTP request rate
   */
  async getRequestRate(): Promise<Record<string, number>> {
    const result = await this.query(
      'rate(http_requests_total[5m])'
    );

    const rateByService: Record<string, number> = {};
    result.data.result.forEach(metric => {
      const service = metric.metric.job || metric.metric.instance;
      const value = parseFloat(metric.value[1]);
      rateByService[service] = Math.round(value * 100) / 100;
    });

    return rateByService;
  },

  /**
   * Get error rate
   */
  async getErrorRate(): Promise<Record<string, number>> {
    const result = await this.query(
      'rate(http_requests_total{status=~"5.."}[5m])'
    );

    const errorByService: Record<string, number> = {};
    result.data.result.forEach(metric => {
      const service = metric.metric.job || metric.metric.instance;
      const value = parseFloat(metric.value[1]);
      errorByService[service] = Math.round(value * 100) / 100;
    });

    return errorByService;
  },

  /**
   * Get comprehensive system metrics
   */
  async getSystemMetrics() {
    const [cpu, memory, uptime, requestRate, errorRate] = await Promise.all([
      this.getCPUUsage(),
      this.getMemoryUsage(),
      this.getUptime(),
      this.getRequestRate(),
      this.getErrorRate(),
    ]);

    return {
      cpu,
      memory,
      uptime,
      requestRate,
      errorRate,
      timestamp: new Date().toISOString(),
    };
  },
};

// ============================================================================
// GRAFANA INTEGRATION - Embed Grafana dashboards
// ============================================================================

export const grafanaService = {
  /**
   * Get Grafana dashboard URL
   */
  getDashboardURL(
    dashboardId: string,
    options: {
      theme?: 'light' | 'dark';
      kiosk?: boolean;
      refresh?: string;
      from?: string;
      to?: string;
    } = {}
  ): string {
    const params = new URLSearchParams();

    if (options.theme) params.append('theme', options.theme);
    if (options.kiosk) params.append('kiosk', 'tv');
    if (options.refresh) params.append('refresh', options.refresh);
    if (options.from) params.append('from', options.from);
    if (options.to) params.append('to', options.to);

    const queryString = params.toString();
    return `/grafana/d/${dashboardId}${queryString ? '?' + queryString : ''}`;
  },

  /**
   * Get platform overview dashboard
   */
  getPlatformDashboardURL(): string {
    return this.getDashboardURL('platform-overview', {
      theme: 'light',
      kiosk: true,
      refresh: '30s',
    });
  },

  /**
   * Get service-specific dashboard
   */
  getServiceDashboardURL(serviceName: string): string {
    return this.getDashboardURL(`service-${serviceName}`, {
      theme: 'light',
      refresh: '10s',
    });
  },
};

// ============================================================================
// TOOLS MANAGEMENT - Real integration with Analytics Specialist
// ============================================================================

export interface Tool {
  name: string;
  description: string;
  category: 'analysis' | 'security' | 'quality' | 'monitoring';
  competency_required: 'junior' | 'middle' | 'senior' | 'expert';
  last_run?: string;
  status?: 'idle' | 'running' | 'completed' | 'error';
  output_location?: string;
}

export const toolsService = {
  /**
   * Get all available tools from Analytics Specialist
   */
  async listTools(): Promise<Tool[]> {
    try {
      const tools = await analyticsAPI.listTools();
      return tools;
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      return [];
    }
  },

  /**
   * Run a specific tool
   */
  async runTool(toolName: string, params?: any): Promise<any> {
    try {
      const result = await analyticsAPI.runTool(toolName, params);
      return result;
    } catch (error) {
      console.error(`Failed to run tool ${toolName}:`, error);
      throw error;
    }
  },

  /**
   * Get tool execution history
   */
  async getToolHistory(toolName: string): Promise<any[]> {
    try {
      // This would call a real API endpoint for tool history
      const response = await axios.get(`/api/analytics/tools/${toolName}/history`);
      return response.data.history;
    } catch (error) {
      console.error(`Failed to get history for ${toolName}:`, error);
      return [];
    }
  },

  /**
   * Get tool output/results
   */
  async getToolResults(toolName: string): Promise<any> {
    try {
      const response = await axios.get(`/api/analytics/tools/${toolName}/results`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get results for ${toolName}:`, error);
      return null;
    }
  },
};

// ============================================================================
// UNIFIED DASHBOARD DATA - Aggregated real-time data
// ============================================================================

export interface DashboardData {
  services: {
    total: number;
    healthy: number;
    degraded: number;
    down: number;
    details: ServiceStatus[];
  };
  metrics: {
    cpu: Record<string, number>;
    memory: Record<string, number>;
    uptime: Record<string, number>;
    requestRate: Record<string, number>;
    errorRate: Record<string, number>;
  };
  workflows: {
    total: number;
    active: number;
    completed: number;
    failed: number;
  };
  community: {
    total_members: number;
    active_members: number;
    total_contributions: number;
  };
  insights: Array<{
    severity: 'low' | 'medium' | 'high' | 'critical';
    category: string;
    message: string;
  }>;
  tools: Tool[];
  timestamp: string;
}

export const dashboardService = {
  /**
   * Get complete dashboard data - ALL REAL DATA, NO MOCKS
   */
  async getDashboardData(): Promise<DashboardData> {
    try {
      // Fetch all data in parallel
      const [
        platformHealth,
        systemMetrics,
        workflows,
        communityMetrics,
        insights,
        tools,
      ] = await Promise.all([
        getPlatformHealth(),
        prometheusService.getSystemMetrics(),
        workflowAPI.listWorkflows().catch(() => []),
        communityAPI.getMetrics().catch(() => ({
          total_members: 0,
          active_members: 0,
          total_contributions: 0,
          average_reputation: 0,
        })),
        analyticsAPI.getInsights().catch(() => []),
        toolsService.listTools(),
      ]);

      // Aggregate workflow stats
      const workflowStats = workflows.reduce(
        (acc, wf) => {
          acc.total++;
          if (wf.status === 'active') acc.active++;
          if (wf.status === 'completed') acc.completed++;
          if (wf.status === 'failed') acc.failed++;
          return acc;
        },
        { total: 0, active: 0, completed: 0, failed: 0 }
      );

      return {
        services: {
          total: platformHealth.total_services,
          healthy: platformHealth.healthy,
          degraded: platformHealth.degraded,
          down: platformHealth.down,
          details: platformHealth.services,
        },
        metrics: systemMetrics,
        workflows: workflowStats,
        community: communityMetrics,
        insights,
        tools,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      throw error;
    }
  },

  /**
   * Get service-specific details
   */
  async getServiceDetails(serviceName: string) {
    try {
      const [status, metrics, logs] = await Promise.all([
        getServiceStatus(serviceName),
        prometheusService.query(`up{job="${serviceName}"}`),
        // Get service logs (would need real endpoint)
        axios.get(`/api/${serviceName}/logs`).catch(() => ({ data: { logs: [] } })),
      ]);

      return {
        status,
        metrics: metrics.data.result,
        logs: logs.data.logs,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error(`Failed to fetch details for ${serviceName}:`, error);
      throw error;
    }
  },
};

// ============================================================================
// EXPORT ALL SERVICES
// ============================================================================

export default {
  prometheus: prometheusService,
  grafana: grafanaService,
  tools: toolsService,
  dashboard: dashboardService,
};
