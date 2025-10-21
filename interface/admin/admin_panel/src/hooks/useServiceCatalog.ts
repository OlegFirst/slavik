/**
 * Service Catalog Hooks
 * ======================
 * React hooks for Service Catalog data fetching
 */

import { useQuery } from '@tanstack/react-query';
import { serviceCatalogAPI, ServiceCatalogStats, ServiceCatalogService, ServiceCategory } from '@/services/service-catalog-api';

/**
 * Fetch all services
 */
export function useServiceCatalog(refetchInterval: number = 30000) {
  return useQuery<ServiceCatalogService[], Error>({
    queryKey: ['serviceCatalog', 'all'],
    queryFn: () => serviceCatalogAPI.getAllServices(),
    refetchInterval,
    staleTime: 10000,
  });
}

/**
 * Fetch service catalog statistics
 */
export function useServiceCatalogStats(refetchInterval: number = 30000) {
  return useQuery<ServiceCatalogStats, Error>({
    queryKey: ['serviceCatalog', 'stats'],
    queryFn: () => serviceCatalogAPI.getStats(),
    refetchInterval,
    staleTime: 10000,
  });
}

/**
 * Fetch single service details
 */
export function useService(serviceName: string, enabled: boolean = true) {
  return useQuery<ServiceCatalogService, Error>({
    queryKey: ['serviceCatalog', 'service', serviceName],
    queryFn: () => serviceCatalogAPI.getService(serviceName),
    enabled: enabled && !!serviceName,
    staleTime: 10000,
  });
}

/**
 * Fetch missing services
 */
export function useMissingServices(refetchInterval: number = 30000) {
  return useQuery<ServiceCatalogService[], Error>({
    queryKey: ['serviceCatalog', 'missing'],
    queryFn: () => serviceCatalogAPI.getMissingServices(),
    refetchInterval,
    staleTime: 10000,
  });
}

/**
 * Fetch unknown services
 */
export function useUnknownServices(refetchInterval: number = 30000) {
  return useQuery<ServiceCatalogService[], Error>({
    queryKey: ['serviceCatalog', 'unknown'],
    queryFn: () => serviceCatalogAPI.getUnknownServices(),
    refetchInterval,
    staleTime: 10000,
  });
}

/**
 * Fetch healthy services
 */
export function useHealthyServices(refetchInterval: number = 30000) {
  return useQuery<ServiceCatalogService[], Error>({
    queryKey: ['serviceCatalog', 'healthy'],
    queryFn: () => serviceCatalogAPI.getHealthyServices(),
    refetchInterval,
    staleTime: 10000,
  });
}

/**
 * Fetch services grouped by category
 */
export function useServicesByCategory(refetchInterval: number = 30000) {
  return useQuery<ServiceCategory[], Error>({
    queryKey: ['serviceCatalog', 'categories'],
    queryFn: () => serviceCatalogAPI.getServicesByCategory(),
    refetchInterval,
    staleTime: 10000,
  });
}

/**
 * Check Service Discovery health
 */
export function useServiceDiscoveryHealth(refetchInterval: number = 10000) {
  return useQuery<{ status: string; version: string }, Error>({
    queryKey: ['serviceCatalog', 'health'],
    queryFn: () => serviceCatalogAPI.checkHealth(),
    refetchInterval,
    staleTime: 5000,
  });
}
