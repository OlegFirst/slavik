/**
 * Service Configuration
 * Complete platform service endpoints
 * Generated: 2025-10-17
 */

export interface ServiceConfig {
  url: string;
  port: number;
  status?: 'production' | 'development' | 'disabled';
}

export const SERVICES = {
  // ========================================
  // INFRASTRUCTURE SERVICES
  // ========================================
  AUTH: {
    url: process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8001',
    port: 8001,
    status: 'production' as const,
  },
  API_GATEWAY: {
    url: process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080',
    port: 8080,
    status: 'production' as const,
  },
  EVENTBUS: {
    url: process.env.NEXT_PUBLIC_EVENTBUS_URL || 'http://localhost:8055',
    port: 8055,
    status: 'production' as const,
  },
  WEBSOCKET: {
    url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8056',
    port: 8056,
    status: 'production' as const,
  },

  // ========================================
  // PLATFORM SERVICES (ISO 22301 Core)
  // ========================================
  BIA: {
    url: process.env.NEXT_PUBLIC_BIA_URL || 'http://localhost:8012',
    port: 8012,
    status: 'production' as const,
  },
  PLANNING: {
    url: process.env.NEXT_PUBLIC_PLANNING_URL || 'http://localhost:8011',
    port: 8011,
    status: 'production' as const,
  },
  LEARNING: {
    url: process.env.NEXT_PUBLIC_LEARNING_URL || 'http://localhost:8021',
    port: 8021,
    status: 'production' as const,
  },
  VALIDATION: {
    url: process.env.NEXT_PUBLIC_VALIDATION_URL || 'http://localhost:8022',
    port: 8022,
    status: 'production' as const,
  },
  DIGITAL_TWIN: {
    url: process.env.NEXT_PUBLIC_DIGITAL_TWIN_URL || 'http://localhost:8096',
    port: 8096,
    status: 'production' as const,
  },
  COMPLIANCE: {
    url: process.env.NEXT_PUBLIC_COMPLIANCE_URL || 'http://localhost:8014',
    port: 8014,
    status: 'development' as const,
  },
  DOCUMENTS: {
    url: process.env.NEXT_PUBLIC_DOCUMENTS_URL || 'http://localhost:8024',
    port: 8024,
    status: 'development' as const,
  },
  GOVERNANCE: {
    url: process.env.NEXT_PUBLIC_GOVERNANCE_URL || 'http://localhost:8025',
    port: 8025,
    status: 'development' as const,
  },
  PLANS: {
    url: process.env.NEXT_PUBLIC_PLANS_URL || 'http://localhost:8023',
    port: 8023,
    status: 'development' as const,
  },
  RESPONSE: {
    url: process.env.NEXT_PUBLIC_RESPONSE_URL || 'http://localhost:8027',
    port: 8027,
    status: 'development' as const,
  },
  RISK: {
    url: process.env.NEXT_PUBLIC_RISK_URL || 'http://localhost:8026',
    port: 8026,
    status: 'development' as const,
  },

  // ========================================
  // INTELLIGENT CORE SERVICES
  // ========================================
  AI_FOUNDATION: {
    url: process.env.NEXT_PUBLIC_AI_FOUNDATION_URL || 'http://localhost:8040',
    port: 8040,
    status: 'production' as const,
  },
  SYSTEM_BCM: {
    url: process.env.NEXT_PUBLIC_SYSTEM_BCM_URL || 'http://localhost:8050',
    port: 8050,
    status: 'production' as const,
  },
  WORKFLOW_INTELLIGENCE: {
    url: process.env.NEXT_PUBLIC_WORKFLOW_INTELLIGENCE_URL || 'http://localhost:8037',
    port: 8037,
    status: 'production' as const,
  },
  COMMUNITY: {
    url: process.env.NEXT_PUBLIC_COMMUNITY_URL || 'http://localhost:8030',
    port: 8030,
    status: 'production' as const,
  },
  ANALYTICS: {
    url: process.env.NEXT_PUBLIC_ANALYTICS_URL || 'http://localhost:8051',
    port: 8051,
    status: 'production' as const,
  },
  SIMULATION: {
    url: process.env.NEXT_PUBLIC_SIMULATION_URL || 'http://localhost:8095',
    port: 8095,
    status: 'production' as const,
  },

  // ========================================
  // LEGACY / FALLBACK
  // ========================================
  LEGACY_API: {
    url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    port: 8000,
    status: 'production' as const,
  },
} as const;

export type ServiceName = keyof typeof SERVICES;

/**
 * Get service URL by name
 */
export function getServiceUrl(serviceName: ServiceName): string {
  return SERVICES[serviceName].url;
}

/**
 * Check if service is available (production status)
 */
export function isServiceAvailable(serviceName: ServiceName): boolean {
  return SERVICES[serviceName].status === 'production';
}

/**
 * Get all production-ready services
 */
export function getProductionServices(): ServiceName[] {
  return Object.entries(SERVICES)
    .filter(([_, config]) => config.status === 'production')
    .map(([name]) => name as ServiceName);
}
