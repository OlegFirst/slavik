import { secureApiClient } from '../../security/api/SecureApiClient';

interface RealSystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  timestamp: string;
}

interface RealAIOrgan {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'error';
  health: number;
  location: string;
  tokenUsage: number;
  lastActivity: string;
}

export class RealBCMService {
  // Заменяем getMockMetricValue на реальные данные
  async getSystemMetrics(): Promise<RealSystemMetrics> {
    try {
      const response = await secureApiClient.get('/metrics/system');
      return response.data;
    } catch (error) {
      // Fallback к кешированным данным
      const cached = this.getCachedMetrics();
      if (cached) return cached;

      throw new Error('System metrics unavailable');
    }
  }

  // Заменяем getEnhancedMockOrgans на реальные AI органы
  async getAIOrgans(): Promise<RealAIOrgan[]> {
    try {
      const response = await secureApiClient.get('/ai/organs');
      return response.data.organs;
    } catch (error) {
      console.error('Failed to fetch AI organs:', error);
      return [];
    }
  }

  // Реальные логи вместо моков
  async getServiceLogs(serviceId: string): Promise<string[]> {
    try {
      const response = await secureApiClient.get(`/logs/${serviceId}`);
      return response.data.logs;
    } catch (error) {
      return [`[${new Date().toISOString()}] Service logs unavailable`];
    }
  }

  // Реальная аналитика
  async getAnalytics(): Promise<any> {
    try {
      const [
        complianceData,
        kpiData,
        performanceData
      ] = await Promise.all([
        secureApiClient.get('/analytics/compliance'),
        secureApiClient.get('/analytics/kpi'),
        secureApiClient.get('/analytics/performance')
      ]);

      return {
        compliance: complianceData.data,
        kpi: kpiData.data,
        performance: performanceData.data
      };
    } catch (error) {
      throw new Error('Analytics data unavailable');
    }
  }

  // Реальная проверка здоровья сервисов
  async getServiceHealth(): Promise<Record<string, boolean>> {
    try {
      const response = await secureApiClient.get('/health/services');
      return response.data.services;
    } catch (error) {
      return {};
    }
  }

  // Кеширование для fallback
  private getCachedMetrics(): RealSystemMetrics | null {
    const cached = localStorage.getItem('bcm_metrics_cache');
    const cacheTime = localStorage.getItem('bcm_metrics_cache_time');

    if (cached && cacheTime) {
      const age = Date.now() - parseInt(cacheTime);
      const fiveMinutes = 5 * 60 * 1000;

      if (age < fiveMinutes) {
        return JSON.parse(cached);
      }
    }

    return null;
  }

  private setCachedMetrics(metrics: RealSystemMetrics): void {
    localStorage.setItem('bcm_metrics_cache', JSON.stringify(metrics));
    localStorage.setItem('bcm_metrics_cache_time', Date.now().toString());
  }
}