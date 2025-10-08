/**
 * AI Platform ISO 22301 - API Service Layer
 * =========================================
 *
 * Central service for all API interactions with AI Platform services.
 * Uses Axios for HTTP requests with proper error handling.
 *
 * Services integrated:
 * - AI Orchestrator (8000)
 * - Workflow Intelligence (8003)
 * - Community Intelligence (8004)
 * - Predictive Service (8005)
 * - Analytics Specialist (8051)
 * - Event Bus (8001)
 * - API Gateway (8777)
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

const createApiClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      console.error(`API Error [${baseURL}]:`, error.message);

      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;
        throw {
          status,
          message: (data as any)?.message || error.message,
          data,
        };
      } else if (error.request) {
        // Request made but no response
        throw {
          status: 0,
          message: 'Service unavailable. Please check if the service is running.',
          data: null,
        };
      } else {
        // Error in request setup
        throw {
          status: -1,
          message: error.message,
          data: null,
        };
      }
    }
  );

  return client;
};

// API Clients for each service
const orchestratorClient = createApiClient('/api/orchestrator');
const workflowClient = createApiClient('/api/workflow');
const communityClient = createApiClient('/api/community');
const predictiveClient = createApiClient('/api/predictive');
const analyticsClient = createApiClient('/api/analytics');
const eventbusClient = createApiClient('/api/eventbus');
const gatewayClient = createApiClient('/api/gateway');

// ============================================================================
// SERVICE HEALTH & STATUS
// ============================================================================

export interface ServiceStatus {
  service: string;
  status: 'healthy' | 'degraded' | 'down';
  url: string;
  port: number;
  response_time_ms?: number;
  version?: string;
  uptime?: number;
}

export interface PlatformHealth {
  total_services: number;
  healthy: number;
  degraded: number;
  down: number;
  services: ServiceStatus[];
  timestamp: string;
}

/**
 * Get health status of all platform services
 */
export const getPlatformHealth = async (): Promise<PlatformHealth> => {
  const services = [
    { name: 'orchestrator', client: orchestratorClient, port: 8000 },
    { name: 'workflow', client: workflowClient, port: 8003 },
    { name: 'community', client: communityClient, port: 8004 },
    { name: 'predictive', client: predictiveClient, port: 8005 },
    { name: 'analytics', client: analyticsClient, port: 8051 },
    { name: 'eventbus', client: eventbusClient, port: 8001 },
    { name: 'gateway', client: gatewayClient, port: 8777 },
  ];

  const results: ServiceStatus[] = await Promise.all(
    services.map(async ({ name, client, port }) => {
      const start = Date.now();
      try {
        const response = await client.get('/health');
        const responseTime = Date.now() - start;

        return {
          service: name,
          status: response.data.status === 'healthy' ? 'healthy' : 'degraded',
          url: `http://localhost:${port}`,
          port,
          response_time_ms: responseTime,
          version: response.data.version,
          uptime: response.data.uptime,
        };
      } catch (error) {
        return {
          service: name,
          status: 'down',
          url: `http://localhost:${port}`,
          port,
        };
      }
    })
  );

  const healthy = results.filter((s) => s.status === 'healthy').length;
  const degraded = results.filter((s) => s.status === 'degraded').length;
  const down = results.filter((s) => s.status === 'down').length;

  return {
    total_services: results.length,
    healthy,
    degraded,
    down,
    services: results,
    timestamp: new Date().toISOString(),
  };
};

/**
 * Get status of a specific service
 */
export const getServiceStatus = async (serviceName: string): Promise<ServiceStatus> => {
  const clientMap: Record<string, { client: AxiosInstance; port: number }> = {
    orchestrator: { client: orchestratorClient, port: 8000 },
    workflow: { client: workflowClient, port: 8003 },
    community: { client: communityClient, port: 8004 },
    predictive: { client: predictiveClient, port: 8005 },
    analytics: { client: analyticsClient, port: 8051 },
    eventbus: { client: eventbusClient, port: 8001 },
    gateway: { client: gatewayClient, port: 8777 },
  };

  const service = clientMap[serviceName];
  if (!service) {
    throw new Error(`Unknown service: ${serviceName}`);
  }

  const start = Date.now();
  try {
    const response = await service.client.get('/health');
    const responseTime = Date.now() - start;

    return {
      service: serviceName,
      status: response.data.status === 'healthy' ? 'healthy' : 'degraded',
      url: `http://localhost:${service.port}`,
      port: service.port,
      response_time_ms: responseTime,
      version: response.data.version,
    };
  } catch (error) {
    return {
      service: serviceName,
      status: 'down',
      url: `http://localhost:${service.port}`,
      port: service.port,
    };
  }
};

// ============================================================================
// AI ORCHESTRATOR API
// ============================================================================

export interface AgentInfo {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'busy' | 'error';
  capabilities: string[];
}

export const orchestratorAPI = {
  /**
   * Get orchestrator status
   */
  getStatus: async () => {
    const response = await orchestratorClient.get('/status');
    return response.data;
  },

  /**
   * List all available agents
   */
  listAgents: async (): Promise<AgentInfo[]> => {
    const response = await orchestratorClient.get('/api/agents');
    return response.data.agents;
  },

  /**
   * Execute a task via orchestrator
   */
  executeTask: async (task: { description: string; context?: any }) => {
    const response = await orchestratorClient.post('/api/tasks', task);
    return response.data;
  },
};

// ============================================================================
// WORKFLOW INTELLIGENCE API
// ============================================================================

export interface Workflow {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  type: string;
  created_at: string;
  updated_at: string;
}

export const workflowAPI = {
  /**
   * List all workflows
   */
  listWorkflows: async (): Promise<Workflow[]> => {
    const response = await workflowClient.get('/api/workflows');
    return response.data.workflows;
  },

  /**
   * Get workflow by ID
   */
  getWorkflow: async (workflowId: string): Promise<Workflow> => {
    const response = await workflowClient.get(`/api/workflows/${workflowId}`);
    return response.data;
  },

  /**
   * Get workflow executions
   */
  getExecutions: async (workflowId: string) => {
    const response = await workflowClient.get(`/api/workflows/${workflowId}/executions`);
    return response.data;
  },

  /**
   * Start a new workflow
   */
  startWorkflow: async (workflowData: any) => {
    const response = await workflowClient.post('/api/workflows', workflowData);
    return response.data;
  },
};

// ============================================================================
// COMMUNITY INTELLIGENCE API
// ============================================================================

export interface CommunityMetrics {
  total_members: number;
  active_members: number;
  total_contributions: number;
  average_reputation: number;
}

export const communityAPI = {
  /**
   * Get community metrics
   */
  getMetrics: async (): Promise<CommunityMetrics> => {
    const response = await communityClient.get('/api/metrics');
    return response.data;
  },

  /**
   * List contributions
   */
  listContributions: async () => {
    const response = await communityClient.get('/api/contributions');
    return response.data;
  },

  /**
   * Get member reputation
   */
  getMemberReputation: async (memberId: string) => {
    const response = await communityClient.get(`/api/reputation/${memberId}`);
    return response.data;
  },
};

// ============================================================================
// PREDICTIVE SERVICE API
// ============================================================================

export interface Prediction {
  id: string;
  type: string;
  confidence: number;
  prediction: any;
  timestamp: string;
}

export const predictiveAPI = {
  /**
   * Get predictions
   */
  getPredictions: async (): Promise<Prediction[]> => {
    const response = await predictiveClient.get('/api/predictions');
    return response.data.predictions;
  },

  /**
   * Request new prediction
   */
  requestPrediction: async (data: { type: string; input: any }) => {
    const response = await predictiveClient.post('/api/predictions', data);
    return response.data;
  },

  /**
   * Get ML model status
   */
  getModelStatus: async () => {
    const response = await predictiveClient.get('/api/models/status');
    return response.data;
  },
};

// ============================================================================
// ANALYTICS SPECIALIST API
// ============================================================================

export interface AnalysisResult {
  type: string;
  status: 'success' | 'error';
  results: any;
  timestamp: string;
}

export interface Insight {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  message: string;
  details?: any;
  recommendation?: string;
}

export const analyticsAPI = {
  /**
   * Get Analytics Specialist status
   */
  getStatus: async () => {
    const response = await analyticsClient.get('/status');
    return response.data;
  },

  /**
   * Run platform analysis
   */
  analyzeplatform: async (): Promise<AnalysisResult> => {
    const response = await analyticsClient.post('/analyze');
    return response.data;
  },

  /**
   * Get insights
   */
  getInsights: async (): Promise<Insight[]> => {
    const response = await analyticsClient.get('/insights');
    return response.data.insights;
  },

  /**
   * Run specific tool
   */
  runTool: async (toolName: string, params?: any) => {
    const response = await analyticsClient.post(`/tools/${toolName}`, params);
    return response.data;
  },

  /**
   * Get available tools
   */
  listTools: async () => {
    const response = await analyticsClient.get('/tools');
    return response.data.tools;
  },
};

// ============================================================================
// EVENT BUS API
// ============================================================================

export const eventbusAPI = {
  /**
   * Publish event
   */
  publishEvent: async (event: { type: string; data: any }) => {
    const response = await eventbusClient.post('/events', event);
    return response.data;
  },

  /**
   * Get event history
   */
  getEventHistory: async (limit = 100) => {
    const response = await eventbusClient.get(`/events/history?limit=${limit}`);
    return response.data;
  },

  /**
   * Subscribe to event type
   */
  subscribe: async (eventType: string) => {
    const response = await eventbusClient.post('/subscribe', { event_type: eventType });
    return response.data;
  },
};

// ============================================================================
// API GATEWAY
// ============================================================================

export const gatewayAPI = {
  /**
   * Get gateway stats
   */
  getStats: async () => {
    const response = await gatewayClient.get('/stats');
    return response.data;
  },

  /**
   * Get rate limit info
   */
  getRateLimits: async () => {
    const response = await gatewayClient.get('/rate-limits');
    return response.data;
  },
};

// ============================================================================
// EXPORT ALL
// ============================================================================

export default {
  getPlatformHealth,
  getServiceStatus,
  orchestrator: orchestratorAPI,
  workflow: workflowAPI,
  community: communityAPI,
  predictive: predictiveAPI,
  analytics: analyticsAPI,
  eventbus: eventbusAPI,
  gateway: gatewayAPI,
};
