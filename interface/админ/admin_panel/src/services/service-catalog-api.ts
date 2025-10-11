/**
 * Service Catalog API Client
 * ===========================
 *
 * Client for Service Discovery v2.0 API (http://localhost:8500)
 * Provides access to unified service catalog with 47 services
 */

const BASE_URL = 'http://localhost:8500';

export interface ServiceCatalogService {
  name: string;
  display_name?: string;
  type: string;
  category?: string;
  expected_port?: number;
  actual_port?: number;
  registration_status: 'registered' | 'missing' | 'unknown';
  health_status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  description?: string;
  version?: string;
  endpoints?: Record<string, string>;
  dependencies?: {
    required?: string[];
    optional?: string[];
  };
  business_process?: string[];
  metadata?: Record<string, any>;
}

export interface ServiceCatalogStats {
  totals: {
    total_services: number;
    registered_services: number;
    missing_services: number;
    unknown_services: number;
    healthy_services: number;
    coverage_percent: number;
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

export interface ServiceCategory {
  name: string;
  count: number;
  services: ServiceCatalogService[];
}

class ServiceCatalogAPI {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get all services (unified catalog + runtime)
   */
  async getAllServices(): Promise<ServiceCatalogService[]> {
    const response = await fetch(`${this.baseUrl}/v2/catalog/services`);
    if (!response.ok) {
      throw new Error(`Failed to fetch services: ${response.statusText}`);
    }
    const data = await response.json();
    return data.services || [];
  }

  /**
   * Get single service details
   */
  async getService(serviceName: string): Promise<ServiceCatalogService> {
    const response = await fetch(`${this.baseUrl}/v2/catalog/services/${serviceName}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch service ${serviceName}: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get catalog statistics
   */
  async getStats(): Promise<ServiceCatalogStats> {
    const response = await fetch(`${this.baseUrl}/v2/catalog/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get missing services (in catalog but not running)
   */
  async getMissingServices(): Promise<ServiceCatalogService[]> {
    const response = await fetch(`${this.baseUrl}/v2/catalog/missing`);
    if (!response.ok) {
      throw new Error(`Failed to fetch missing services: ${response.statusText}`);
    }
    const data = await response.json();
    return data.services || [];
  }

  /**
   * Get unknown services (running but not in catalog)
   */
  async getUnknownServices(): Promise<ServiceCatalogService[]> {
    const response = await fetch(`${this.baseUrl}/v2/catalog/unknown`);
    if (!response.ok) {
      throw new Error(`Failed to fetch unknown services: ${response.statusText}`);
    }
    const data = await response.json();
    return data.services || [];
  }

  /**
   * Get healthy services only
   */
  async getHealthyServices(): Promise<ServiceCatalogService[]> {
    const response = await fetch(`${this.baseUrl}/v2/catalog/healthy`);
    if (!response.ok) {
      throw new Error(`Failed to fetch healthy services: ${response.statusText}`);
    }
    const data = await response.json();
    return data.services || [];
  }

  /**
   * Get services grouped by category
   */
  async getServicesByCategory(): Promise<ServiceCategory[]> {
    const services = await this.getAllServices();
    const stats = await this.getStats();

    // Group by type (category)
    const categoryMap = new Map<string, ServiceCatalogService[]>();

    services.forEach(service => {
      const category = service.type || 'uncategorized';
      if (!categoryMap.has(category)) {
        categoryMap.set(category, []);
      }
      categoryMap.get(category)!.push(service);
    });

    // Convert to array and sort by count
    const categories: ServiceCategory[] = Array.from(categoryMap.entries())
      .map(([name, services]) => ({
        name,
        count: services.length,
        services: services.sort((a, b) => a.name.localeCompare(b.name))
      }))
      .sort((a, b) => b.count - a.count);

    return categories;
  }

  /**
   * Check Service Discovery health
   */
  async checkHealth(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get Prometheus metrics
   */
  async getMetrics(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/metrics`);
    if (!response.ok) {
      throw new Error(`Failed to fetch metrics: ${response.statusText}`);
    }
    return response.text();
  }
}

export const serviceCatalogAPI = new ServiceCatalogAPI();
