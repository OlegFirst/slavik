/**
 * Legacy BCM Service - Stub for backward compatibility
 * ====================================================
 *
 * This file provides backward compatibility for old components.
 * ALL NEW CODE SHOULD USE: src/services/platform.ts and src/services/realtime.ts
 *
 * NO MOCK DATA - All methods return empty arrays or throw errors
 */

import { bcmAPI } from './api';

// Type definitions for backward compatibility
export interface AIOrgan {
  id: number;
  name: string;
  status: 'healthy' | 'warning' | 'error';
  load: number;
  location: string;
  uptime?: string;
  tokenUsage?: number;
  responseTime?: number;
  lastCheck?: string;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  timestamp: string;
}

export interface ServiceInfo {
  name: string;
  port: string;
  status: 'running' | 'stopped' | 'error';
  uptime: string;
  health?: boolean;
  restarts?: number;
}

// API endpoints - kept for reference
export const API_ENDPOINTS = {
  AI_ORCHESTRATOR: import.meta.env.VITE_AI_ORCHESTRATOR_URL || 'http://localhost:8000',
  WORKFLOW_INTELLIGENCE: import.meta.env.VITE_WORKFLOW_URL || 'http://localhost:8003',
  COMMUNITY_INTELLIGENCE: import.meta.env.VITE_COMMUNITY_URL || 'http://localhost:8004',
  PREDICTIVE_SERVICE: import.meta.env.VITE_PREDICTIVE_URL || 'http://localhost:8005',
  ANALYTICS_SPECIALIST: import.meta.env.VITE_ANALYTICS_URL || 'http://localhost:8051',
  EVENT_BUS: import.meta.env.VITE_EVENTBUS_URL || 'http://localhost:8001',
  PROMETHEUS: import.meta.env.VITE_PROMETHEUS_URL || 'http://localhost:9090',
  GRAFANA: import.meta.env.VITE_GRAFANA_URL || 'http://localhost:3000',
};

// Legacy service object - deprecated
export const aiService = {
  async getOrgansStatus(): Promise<AIOrgan[]> {
    console.warn('️ bcm.ts is deprecated. Use src/services/platform.ts instead!');
    return [];
  },
};

// System service - stub
export const systemService = {
  async getMetrics(): Promise<SystemMetrics> {
    console.warn('️ bcm.ts is deprecated. Use src/services/platform.ts instead!');
    return {
      cpu: 0,
      memory: 0,
      disk: 0,
      network: 0,
      timestamp: new Date().toISOString(),
    };
  },

  async getServices(): Promise<ServiceInfo[]> {
    console.warn('️ bcm.ts is deprecated. Use src/services/platform.ts instead!');
    return [];
  },

  async controlService(serviceName: string, action: 'start' | 'stop' | 'restart') {
    console.warn('️ bcm.ts is deprecated. Use real service control API!');
    throw new Error('Not implemented - use real API');
  },
};

// Monitoring service - stub
export const monitoringService = {
  async getMetrics() {
    console.warn('️ bcm.ts is deprecated. Use src/services/realtime.ts instead!');
    return {
      cpu: 0,
      memory: 0,
      requests: 0,
      errors: 0,
    };
  },
};

// System config service - stub
export const systemConfigService = {
  async getConfig() {
    console.warn('️ bcm.ts is deprecated. Use real config API!');
    return {
      general: [],
      security: [],
      integration: [],
      notifications: [],
    };
  },

  async updateConfig() {
    console.warn('️ bcm.ts is deprecated. Use real config API!');
    throw new Error('Not implemented - use real API');
  },
};

// Analytics service - stub for backward compatibility
export const analyticsService = {
  async getRealAnalyticsData() {
    console.warn('️ bcm.ts is deprecated. Use src/services/analytics-hub.ts instead!');
    return {
      connected: false,
      visits: { today: 0, week: 0, month: 0, trend: 'N/A' },
      popularPages: [],
      topQueries: [],
      userActivity: {
        activeUsers: 0,
        avgSessionTime: 'N/A',
        bounceRate: 'N/A',
        newUsers: 0,
        returningUsers: 0,
      },
    };
  },
};

// Export all for backward compatibility
export default {
  aiService,
  systemService,
  monitoringService,
  systemConfigService,
  analyticsService,
  API_ENDPOINTS,
};
