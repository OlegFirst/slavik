/**
 * Service Catalog API Client
 *
 * Connects to Service Discovery v2.0 API to fetch service catalog data.
 */

import { secureApiClient } from '../security/api/SecureApiClient';

const SERVICE_DISCOVERY_URL = 'http://localhost:8500';

export interface ServiceInfo {
  name: string;
  type: string;
  description?: string;
  business_process?: string;
  status: string;
  expected_port?: number;
  actual_port?: number;
  registration_status: 'registered' | 'not_registered' | 'unknown';
  health_status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  metrics_endpoint?: string;
  dependencies?: string[];
  integrations?: any[];
  known_issues?: any[];
}

export interface CatalogStats {
  totals: {
    total_services: number;
    registered_services: number;
    missing_services: number;
    unknown_services: number;
    coverage_percent: number;
    healthy_services: number;
  };
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_business_process: Record<string, number>;
  metadata: {
    platform_name: string;
    version: string;
    total_services: number;
    schema_version: string;
    generated_at: string;
    auto_generated: boolean;
  };
}

export const serviceCatalogAPI = {
  /**
   * Get all services with unified catalog + runtime data
   */
  async getAllServices(): Promise<{ services: ServiceInfo[]; count: number }> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/catalog/services`);
      if (!response.ok) {
        throw new Error(`Failed to fetch services: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching services:', error);
      throw error;
    }
  },

  /**
   * Get detailed unified view of a single service
   */
  async getService(serviceName: string): Promise<ServiceInfo> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/catalog/services/${serviceName}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch service ${serviceName}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching service ${serviceName}:`, error);
      throw error;
    }
  },

  /**
   * Get comprehensive catalog statistics
   */
  async getStats(): Promise<CatalogStats> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/catalog/stats`);
      if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  },

  /**
   * Get services that are in catalog but not registered
   */
  async getMissingServices(): Promise<{ services: ServiceInfo[]; count: number }> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/catalog/missing`);
      if (!response.ok) {
        throw new Error(`Failed to fetch missing services: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching missing services:', error);
      throw error;
    }
  },

  /**
   * Get services that are running but not in catalog
   */
  async getUnknownServices(): Promise<{ services: ServiceInfo[]; count: number }> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/catalog/unknown`);
      if (!response.ok) {
        throw new Error(`Failed to fetch unknown services: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching unknown services:', error);
      throw error;
    }
  },

  /**
   * Get all healthy services
   */
  async getHealthyServices(): Promise<{ services: ServiceInfo[]; count: number }> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/catalog/healthy`);
      if (!response.ok) {
        throw new Error(`Failed to fetch healthy services: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching healthy services:', error);
      throw error;
    }
  },

  /**
   * Get all services from service registry (runtime only)
   */
  async getRegistryServices(): Promise<{ services: ServiceInfo[]; count: number }> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/registry/services`);
      if (!response.ok) {
        throw new Error(`Failed to fetch registry services: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching registry services:', error);
      throw error;
    }
  },

  /**
   * Get service registry statistics
   */
  async getRegistryStats(): Promise<any> {
    try {
      const response = await fetch(`${SERVICE_DISCOVERY_URL}/v2/registry/stats`);
      if (!response.ok) {
        throw new Error(`Failed to fetch registry stats: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching registry stats:', error);
      throw error;
    }
  },
};
