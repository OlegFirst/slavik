import { useEffect, useCallback, useRef } from 'react';
import { useSystemStore, useAppStore } from '@/stores/system';
import { aiService, systemService, monitoringService } from '@/services/bcm';

export const useSystemData = () => {
  const {
    aiOrgans,
    systemMetrics,
    services,
    loading,
    setAIOrgans,
    setSystemMetrics,
    setServices,
    setLoading,
    setError
  } = useSystemStore();

  const { autoRefresh, refreshInterval, addNotification } = useAppStore();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchAIOrgans = useCallback(async () => {
    setLoading('organs', true);
    setError('organs', null);
    
    try {
      console.log('🧠 Fetching AI Organs status...');
      const organs = await aiService.getOrgansStatus();
      console.log('✅ AI Organs fetched:', organs.length);
      setAIOrgans(organs);
      
      // Check if any organs are unhealthy
      const unhealthyOrgans = organs.filter(organ => organ.status !== 'healthy');
      if (unhealthyOrgans.length > 0) {
        addNotification({
          type: 'warning',
          title: 'AI Organs Health Alert',
          message: `${unhealthyOrgans.length} AI organ(s) are not healthy: ${unhealthyOrgans.map(o => o.name).join(', ')}`
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch AI organisms';
      console.error('❌ AI Organs fetch failed:', message);
      setError('organs', message);
      addNotification({
        type: 'error',
        title: 'AI Organisms Error',
        message
      });
    } finally {
      setLoading('organs', false);
    }
  }, [setAIOrgans, setLoading, setError, addNotification]);

  const fetchSystemMetrics = useCallback(async () => {
    setLoading('metrics', true);
    setError('metrics', null);
    
    try {
      console.log('📊 Fetching system metrics...');
      const metrics = await systemService.getSystemMetrics();
      console.log('✅ System metrics fetched:', metrics);
      setSystemMetrics(metrics);

      // Check for high resource usage
      if (metrics.cpu > 90) {
        addNotification({
          type: 'warning',
          title: 'High CPU Usage',
          message: `CPU usage is at ${metrics.cpu.toFixed(1)}%`
        });
      }
      if (metrics.memory > 90) {
        addNotification({
          type: 'warning',
          title: 'High Memory Usage',
          message: `Memory usage is at ${metrics.memory.toFixed(1)}%`
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch system metrics';
      console.error('❌ System metrics fetch failed:', message);
      setError('metrics', message);
    } finally {
      setLoading('metrics', false);
    }
  }, [setSystemMetrics, setLoading, setError, addNotification]);

  const fetchServices = useCallback(async () => {
    setLoading('services', true);
    setError('services', null);
    
    try {
      console.log('🔧 Fetching services status...');
      const servicesData = await systemService.getServicesStatus();
      console.log('✅ Services status fetched:', servicesData.length);
      setServices(servicesData);

      // Check for stopped services
      const stoppedServices = servicesData.filter(service => service.status !== 'running');
      if (stoppedServices.length > 0) {
        addNotification({
          type: 'error',
          title: 'Services Down',
          message: `${stoppedServices.length} service(s) are not running: ${stoppedServices.map(s => s.name).join(', ')}`
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch services';
      console.error('❌ Services fetch failed:', message);
      setError('services', message);
    } finally {
      setLoading('services', false);
    }
  }, [setServices, setLoading, setError, addNotification]);

  const refreshAll = useCallback(async () => {
    console.log('🔄 Refreshing all data...');
    const startTime = Date.now();
    
    try {
      await Promise.allSettled([
        fetchAIOrgans(),
        fetchSystemMetrics(),
        fetchServices()
      ]);
      
      const duration = Date.now() - startTime;
      console.log(`✅ All data refreshed in ${duration}ms`);
      
      addNotification({
        type: 'success',
        title: 'Data Refreshed',
        message: `All system data updated in ${duration}ms`
      });
    } catch (error) {
      console.error('❌ Refresh failed:', error);
      addNotification({
        type: 'error',
        title: 'Refresh Failed',
        message: 'Failed to refresh some system data'
      });
    }
  }, [fetchAIOrgans, fetchSystemMetrics, fetchServices, addNotification]);

  const controlService = useCallback(async (serviceName: string, action: 'start' | 'stop' | 'restart') => {
    console.log(`🔧 ${action} ${serviceName} via Deployer Service...`);

    try {
      // Use the new real control service
      await systemService.realControlService(serviceName, action);
      addNotification({
        type: 'success',
        title: 'Service Control',
        message: `Successfully ${action}ed ${serviceName} via Deployer Service`
      });

      // Refresh services after action with delay
      setTimeout(() => {
        console.log('🔄 Refreshing services after control action...');
        fetchServices();
      }, 2000);
    } catch (error) {
      const message = error instanceof Error ? error.message : `Failed to ${action} ${serviceName}`;
      console.error(`❌ Service control failed:`, message);

      addNotification({
        type: 'error',
        title: 'Service Control Error',
        message
      });
    }
  }, [addNotification, fetchServices]);

  // Enhanced auto-refresh with error handling
  useEffect(() => {
    if (!autoRefresh) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    console.log(`🔄 Setting up auto-refresh every ${refreshInterval}ms`);
    
    const startAutoRefresh = () => {
      intervalRef.current = setInterval(async () => {
        console.log('🔄 Auto-refresh triggered');
        try {
          await Promise.allSettled([
            fetchSystemMetrics(), // Most important - system health
            fetchServices(),      // Service status
            fetchAIOrgans()       // AI organs (can be slower)
          ]);
        } catch (error) {
          console.error('❌ Auto-refresh error:', error);
        }
      }, refreshInterval);
    };

    startAutoRefresh();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [autoRefresh, refreshInterval, fetchAIOrgans, fetchSystemMetrics, fetchServices]);

  // Initial load on mount
  useEffect(() => {
    console.log('🚀 Initial data load...');
    refreshAll();
  }, []); // Empty dependency array for mount only

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    // Data
    aiOrgans,
    systemMetrics,
    services,
    loading,
    
    // Actions
    refreshAll,
    controlService,
    fetchAIOrgans,
    fetchSystemMetrics,
    fetchServices,
    
    // Status
    isRefreshing: loading.organs || loading.metrics || loading.services
  };
};

export const usePrometheusMetrics = () => {
  const fetchMetric = useCallback(async (query: string) => {
    try {
      console.log(`📊 Fetching Prometheus metric: ${query}`);
      const result = await monitoringService.getMetric(query);
      console.log('✅ Prometheus metric fetched:', result);
      return result;
    } catch (error) {
      console.error('❌ Prometheus metric failed:', error);
      return null;
    }
  }, []);

  const getCommonMetrics = useCallback(async () => {
    const queries = {
      cpuUsage: '100-(avg(irate(node_cpu_seconds_total{mode="idle"}[5m]))*100)',
      memoryUsage: '(1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100',
      httpRequests: 'rate(http_requests_total[5m])',
      responseTime: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
      diskUsage: '(1-(node_filesystem_avail_bytes/node_filesystem_size_bytes))*100',
      networkIO: 'rate(node_network_receive_bytes_total[5m])'
    };

    console.log('📊 Fetching common Prometheus metrics...');
    
    const results: Record<string, any> = {};
    for (const [key, query] of Object.entries(queries)) {
      try {
        results[key] = await fetchMetric(query);
      } catch (error) {
        console.warn(`⚠️ Failed to fetch ${key}:`, error);
        results[key] = null;
      }
    }

    console.log('✅ Common metrics fetched:', Object.keys(results));
    return results;
  }, [fetchMetric]);

  const checkPrometheusHealth = useCallback(async () => {
    try {
      const isHealthy = await monitoringService.checkPrometheusHealth();
      console.log(`📊 Prometheus health: ${isHealthy ? '✅ Healthy' : '❌ Unhealthy'}`);
      return isHealthy;
    } catch (error) {
      console.error('❌ Prometheus health check failed:', error);
      return false;
    }
  }, []);

  return {
    fetchMetric,
    getCommonMetrics,
    checkPrometheusHealth
  };
};

// Health monitoring hook for real-time status
export const useHealthMonitoring = () => {
  const { addNotification } = useAppStore();

  const performHealthCheck = useCallback(async () => {
    console.log('🏥 Performing comprehensive health check...');
    
    const healthChecks = {
      prometheus: monitoringService.checkPrometheusHealth(),
      grafana: monitoringService.checkGrafanaHealth(),
      // Add more health checks as needed
    };

    const results = await Promise.allSettled(Object.entries(healthChecks).map(async ([name, check]) => {
      const isHealthy = await check;
      return { name, healthy: isHealthy };
    }));

    const healthStatus = results.map((result, index) => {
      const name = Object.keys(healthChecks)[index];
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        console.error(`❌ Health check failed for ${name}:`, result.reason);
        return { name, healthy: false };
      }
    });

    const unhealthyServices = healthStatus.filter(status => !status.healthy);
    
    if (unhealthyServices.length > 0) {
      addNotification({
        type: 'warning',
        title: 'Health Check Alert',
        message: `${unhealthyServices.length} monitoring service(s) are unhealthy`
      });
    }

    console.log('✅ Health check completed:', healthStatus);
    return healthStatus;
  }, [addNotification]);

  return {
    performHealthCheck
  };
};
