import { bcmAPI } from './api';
import { getEventBusService, publishPersonalTwinEvent, publishDataCollectionEvent, publishPackageEvent } from './eventBusService';

// ===== Type Definitions =====

export interface DigitalTwinOverview {
  personalTwins: {
    total: number;
    active: number;
    inactive: number;
  };
  organizationalTwins: {
    total: number;
    healthy: number;
    warning: number;
    error: number;
  };
  dataCollection: {
    totalServices: number;
    activeServices: number;
    collectionsPerHour: number;
  };
  recentActivity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
}

export interface PersonalTwin {
  id: string;
  userId: string;
  userName: string;
  userEmail: string;
  status: 'active' | 'inactive' | 'syncing' | 'error';
  healthScore: number;
  lastSync: string;
  dataPoints: number;
  privacySettings: {
    behaviorTracking: boolean;
    performanceMonitoring: boolean;
    aiInsights: boolean;
  };
  createdAt: string;
  updatedAt: string;
}

export interface TwinHealthScore {
  dataQuality: number;
  completeness: number;
  accuracy: number;
  freshness: number;
  overall: number;
}

export interface TwinActivity {
  id: string;
  action: string;
  timestamp: string;
  type: string;
  description: string;
}

export interface DataCollectionService {
  id: string;
  name: string;
  endpoint: string;
  category: string;
  status: 'active' | 'inactive' | 'error' | 'warning';
  collectionsPerMinute: number;
  responseTime: number;
  errorRate: number;
  lastCollection: string;
  configuration: {
    interval: number;
    timeout: number;
    retries: number;
  };
}

export interface ServiceMetrics {
  requestsPerSecond: number;
  avgResponseTime: number;
  successRate: number;
  dataPointsCollected: number;
  recentErrors: Array<{
    message: string;
    timestamp: string;
  }>;
  collectionInterval: number;
  timeout: number;
  retryCount: number;
  bufferSize: number;
}

export interface CollectionStats {
  totalDataPoints: number;
  collectionsPerHour: number;
  avgResponseTime: number;
  successRate: number;
  hourlyTrend: number;
  responseTrend: number;
  successTrend: number;
}

export interface TwinDataPackage {
  id: string;
  name: string;
  description: string;
  type: 'personal' | 'organizational' | 'backup' | 'export';
  status: 'ready' | 'processing' | 'archived' | 'error' | 'uploading';
  size: number;
  compressionRatio: number;
  owner: string;
  createdAt: string;
  encrypted: boolean;
  contents: Array<{
    name: string;
    size: number;
    type: string;
  }>;
  metadata: Record<string, any>;
}

export interface PackageStats {
  totalSize: number;
  avgCompressionRatio: number;
  totalPackages: number;
  packagesByType: Record<string, number>;
}

export interface TransportLog {
  id: string;
  packageName: string;
  action: string;
  status: string;
  size: number;
  timestamp: string;
  duration: string;
}

export interface SystemHealth {
  overallScore: number;
  status: 'healthy' | 'warning' | 'error';
  connectedServices: number;
  dataIntegrity: number;
  dataCollection: number;
  personalTwins: number;
  performance: number;
  aiServices: number;
  packageManagement: number;
  services: Array<{
    name: string;
    status: string;
    responseTime: number;
  }>;
}

export interface ServiceHealth {
  name: string;
  endpoint: string;
  status: 'healthy' | 'warning' | 'error';
  uptime: string;
  responseTime: number;
  memoryUsage: number;
  cpuUsage: number;
  lastCheck: string;
}

export interface PerformanceMetrics {
  avgResponseTime: number;
  requestsPerSecond: number;
  errorRate: number;
  activeConnections: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  systemLoad: number;
  availableMemory: number;
  availableDisk: number;
  networkIn: number;
  networkOut: number;
}

export interface HealthAlert {
  id: string;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error';
  timestamp: string;
  service: string;
}

// ===== API Endpoints =====

const DIGITAL_TWIN_API_BASE = '/api/digital-twin';
const ODOO_BCM_API_BASE = 'http://localhost:8069/api';
const AI_ORCHESTRATOR_API_BASE = 'http://localhost:8000/api/v1';
const EVENTBUS_API_BASE = 'http://localhost:8001/api';
const BIA_ENGINE_API_BASE = 'http://localhost:8082/api';

// ===== API Service =====

export const digitalTwinAPI = {
  // ===== Overview & Dashboard =====

  async getOverview(): Promise<DigitalTwinOverview> {
    try {
      // Get real data from multiple sources
      const [personalTwinsResponse, orgTwinsResponse, dataCollectionResponse, activityResponse] = await Promise.allSettled([
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/personal-twins/overview`),
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/organizational-twins/overview`),
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/data-collection/stats`),
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/activity/recent`)
      ]);

      const overview: DigitalTwinOverview = {
        personalTwins: {
          total: personalTwinsResponse.status === 'fulfilled' ? personalTwinsResponse.value.data.total : 0,
          active: personalTwinsResponse.status === 'fulfilled' ? personalTwinsResponse.value.data.active : 0,
          inactive: personalTwinsResponse.status === 'fulfilled' ? personalTwinsResponse.value.data.inactive : 0
        },
        organizationalTwins: {
          total: orgTwinsResponse.status === 'fulfilled' ? orgTwinsResponse.value.data.total : 0,
          healthy: orgTwinsResponse.status === 'fulfilled' ? orgTwinsResponse.value.data.healthy : 0,
          warning: orgTwinsResponse.status === 'fulfilled' ? orgTwinsResponse.value.data.warning : 0,
          error: orgTwinsResponse.status === 'fulfilled' ? orgTwinsResponse.value.data.error : 0
        },
        dataCollection: {
          totalServices: dataCollectionResponse.status === 'fulfilled' ? dataCollectionResponse.value.data.totalServices : 0,
          activeServices: dataCollectionResponse.status === 'fulfilled' ? dataCollectionResponse.value.data.activeServices : 0,
          collectionsPerHour: dataCollectionResponse.status === 'fulfilled' ? dataCollectionResponse.value.data.collectionsPerHour : 0
        },
        recentActivity: activityResponse.status === 'fulfilled' ? activityResponse.value.data : []
      };

      return overview;
    } catch (error) {
      console.error('🚨 Failed to get Digital Twin overview:', error);
      throw new Error('Digital Twin API unavailable');
    }
  },


  // ===== Personal Twins Management =====

  async getPersonalTwins(): Promise<PersonalTwin[]> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/personal-twins`);
      return response.data.twins || [];
    } catch (error) {
      console.error('🚨 Failed to get Personal Twins:', error);
      throw new Error('Failed to load Personal Twins from backend');
    }
  },


  async getPersonalTwinDetails(twinId: string): Promise<any> {
    try {
      const [detailsResponse, healthResponse, activityResponse] = await Promise.allSettled([
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}`),
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}/health`),
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}/activity`)
      ]);

      return {
        id: twinId,
        details: detailsResponse.status === 'fulfilled' ? detailsResponse.value.data : null,
        health: healthResponse.status === 'fulfilled' ? healthResponse.value.data : null,
        activities: activityResponse.status === 'fulfilled' ? activityResponse.value.data : []
      };
    } catch (error) {
      console.error(`🚨 Failed to get Personal Twin details for ${twinId}:`, error);
      throw new Error(`Failed to load Personal Twin details: ${twinId}`);
    }
  },


  async syncPersonalTwin(twinId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}/sync`);

      // Publish sync event
      await publishPersonalTwinEvent({
        type: 'personal_twin.synced',
        data: {
          twinId: twinId,
          userId: '', // Will be filled by backend
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to sync Personal Twin ${twinId}:`, error);
      throw new Error(`Failed to sync Personal Twin: ${twinId}`);
    }
  },

  async resetPersonalTwin(twinId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}/reset`);
    } catch (error) {
      console.error(`🚨 Failed to reset Personal Twin ${twinId}:`, error);
      throw new Error(`Failed to reset Personal Twin: ${twinId}`);
    }
  },

  async analyzePersonalTwin(twinId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}/analyze`);
    } catch (error) {
      console.error(`🚨 Failed to analyze Personal Twin ${twinId}:`, error);
      throw new Error(`Failed to analyze Personal Twin: ${twinId}`);
    }
  },

  async deletePersonalTwin(twinId: string): Promise<void> {
    try {
      await bcmAPI.delete(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}`);

      // Publish deletion event
      await publishPersonalTwinEvent({
        type: 'personal_twin.deleted',
        data: {
          twinId: twinId,
          userId: '', // Will be filled by backend
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to delete Personal Twin ${twinId}:`, error);
      throw new Error(`Failed to delete Personal Twin: ${twinId}`);
    }
  },

  async updatePrivacySettings(twinId: string, settings: Partial<PersonalTwin['privacySettings']>): Promise<void> {
    try {
      await bcmAPI.put(`${DIGITAL_TWIN_API_BASE}/personal-twins/${twinId}/privacy`, settings);
    } catch (error) {
      console.error(`🚨 Failed to update privacy settings for Twin ${twinId}:`, error);
      throw new Error(`Failed to update privacy settings: ${twinId}`);
    }
  },

  // ===== Data Collection Services =====

  async getDataCollectionServices(): Promise<DataCollectionService[]> {
    try {
      // Get services from multiple endpoints
      const [bcmServicesResponse, aiServicesResponse, systemServicesResponse] = await Promise.allSettled([
        bcmAPI.get(`${ODOO_BCM_API_BASE}/bcm/services`),
        bcmAPI.get(`${AI_ORCHESTRATOR_API_BASE}/services`),
        bcmAPI.get(`${EVENTBUS_API_BASE}/services`)
      ]);

      const allServices: DataCollectionService[] = [];

      // Process BCM services
      if (bcmServicesResponse.status === 'fulfilled') {
        const bcmServices = bcmServicesResponse.value.data.services || [];
        allServices.push(...bcmServices);
      }

      // Process AI services
      if (aiServicesResponse.status === 'fulfilled') {
        const aiServices = aiServicesResponse.value.data.services || [];
        allServices.push(...aiServices);
      }

      // Process System services
      if (systemServicesResponse.status === 'fulfilled') {
        const systemServices = systemServicesResponse.value.data.services || [];
        allServices.push(...systemServices);
      }

      return allServices;
    } catch (error) {
      console.error('🚨 Failed to get data collection services:', error);
      throw new Error('Failed to load data collection services');
    }
  },


  async getCollectionStats(): Promise<CollectionStats> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/data-collection/stats`);
      return response.data;
    } catch (error) {
      console.error('🚨 Failed to get collection stats:', error);
      throw new Error('Failed to load collection statistics');
    }
  },

  async getServiceMetrics(serviceId: string): Promise<ServiceMetrics> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/data-collection/services/${serviceId}/metrics`);
      return response.data;
    } catch (error) {
      console.error(`🚨 Failed to get service metrics for ${serviceId}:`, error);
      throw new Error(`Failed to load service metrics: ${serviceId}`);
    }
  },


  async startDataCollection(serviceId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/data-collection/services/${serviceId}/start`);

      // Publish data collection started event
      await publishDataCollectionEvent({
        type: 'data_collection.started',
        data: {
          serviceId: serviceId
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to start data collection for ${serviceId}:`, error);
      throw new Error(`Failed to start data collection: ${serviceId}`);
    }
  },

  async stopDataCollection(serviceId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/data-collection/services/${serviceId}/stop`);

      // Publish data collection stopped event
      await publishDataCollectionEvent({
        type: 'data_collection.stopped',
        data: {
          serviceId: serviceId
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to stop data collection for ${serviceId}:`, error);
      throw new Error(`Failed to stop data collection: ${serviceId}`);
    }
  },

  async restartDataCollection(serviceId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/data-collection/services/${serviceId}/restart`);
    } catch (error) {
      console.error(`🚨 Failed to restart data collection for ${serviceId}:`, error);
      throw new Error(`Failed to restart data collection: ${serviceId}`);
    }
  },

  // ===== Package Management =====

  async getTwinDataPackages(): Promise<TwinDataPackage[]> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/packages`);
      return response.data.packages || [];
    } catch (error) {
      console.error('🚨 Failed to get twin data packages:', error);
      throw new Error('Failed to load twin data packages');
    }
  },


  async getPackageStats(): Promise<PackageStats> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/packages/stats`);
      return response.data;
    } catch (error) {
      console.error('🚨 Failed to get package stats:', error);
      throw new Error('Failed to load package statistics');
    }
  },

  async getTransportLogs(): Promise<TransportLog[]> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/packages/transport-logs`);
      return response.data.logs || [];
    } catch (error) {
      console.error('🚨 Failed to get transport logs:', error);
      throw new Error('Failed to load transport logs');
    }
  },


  async getPackageDetails(packageId: string): Promise<any> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/packages/${packageId}`);
      return response.data;
    } catch (error) {
      console.error(`🚨 Failed to get package details for ${packageId}:`, error);
      throw new Error(`Failed to load package details: ${packageId}`);
    }
  },


  async downloadPackage(packageId: string): Promise<void> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/packages/${packageId}/download`, {
        responseType: 'blob'
      });

      // Handle file download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `digital-twin-package-${packageId}.pkg`;
      link.click();
      window.URL.revokeObjectURL(url);

      // Publish download event
      await publishPackageEvent({
        type: 'package.downloaded',
        data: {
          packageId: packageId
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to download package ${packageId}:`, error);
      throw new Error(`Failed to download package: ${packageId}`);
    }
  },

  async uploadPackage(file: File): Promise<void> {
    try {
      const formData = new FormData();
      formData.append('package', file);
      const response = await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/packages/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Publish upload event
      await publishPackageEvent({
        type: 'package.uploaded',
        data: {
          packageId: response.data.packageId || 'unknown'
        }
      });
    } catch (error) {
      console.error('🚨 Failed to upload package:', error);
      throw new Error('Failed to upload package');
    }
  },

  async verifyPackage(packageId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/packages/${packageId}/verify`);
    } catch (error) {
      console.error(`🚨 Failed to verify package ${packageId}:`, error);
      throw new Error(`Failed to verify package: ${packageId}`);
    }
  },

  async archivePackage(packageId: string): Promise<void> {
    try {
      await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/packages/${packageId}/archive`);
    } catch (error) {
      console.error(`🚨 Failed to archive package ${packageId}:`, error);
      throw new Error(`Failed to archive package: ${packageId}`);
    }
  },

  async deletePackage(packageId: string): Promise<void> {
    try {
      await bcmAPI.delete(`${DIGITAL_TWIN_API_BASE}/packages/${packageId}`);

      // Publish deletion event
      await publishPackageEvent({
        type: 'package.deleted',
        data: {
          packageId: packageId
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to delete package ${packageId}:`, error);
      throw new Error(`Failed to delete package: ${packageId}`);
    }
  },

  async clonePackage(packageId: string): Promise<void> {
    try {
      const response = await bcmAPI.post(`${DIGITAL_TWIN_API_BASE}/packages/${packageId}/clone`);

      // Publish creation event for cloned package
      await publishPackageEvent({
        type: 'package.created',
        data: {
          packageId: response.data.newPackageId || 'unknown'
        }
      });
    } catch (error) {
      console.error(`🚨 Failed to clone package ${packageId}:`, error);
      throw new Error(`Failed to clone package: ${packageId}`);
    }
  },

  // ===== System Health =====

  async getSystemHealth(): Promise<SystemHealth> {
    try {
      // Get health from multiple sources
      const [digitalTwinHealth, eventBusHealth, aiOrchestratorHealth] = await Promise.allSettled([
        bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/health`),
        bcmAPI.get(`${EVENTBUS_API_BASE}/health`),
        bcmAPI.get(`${AI_ORCHESTRATOR_API_BASE}/health`)
      ]);

      // Aggregate health data
      const healthData = {
        digitalTwin: digitalTwinHealth.status === 'fulfilled' ? digitalTwinHealth.value.data : null,
        eventBus: eventBusHealth.status === 'fulfilled' ? eventBusHealth.value.data : null,
        aiOrchestrator: aiOrchestratorHealth.status === 'fulfilled' ? aiOrchestratorHealth.value.data : null
      };

      // Calculate overall health
      const healthyServices = Object.values(healthData).filter(h => h?.status === 'healthy').length;
      const totalServices = Object.values(healthData).filter(h => h !== null).length;
      const overallScore = totalServices > 0 ? Math.round((healthyServices / totalServices) * 100) : 0;

      return {
        overallScore,
        status: overallScore >= 80 ? 'healthy' : overallScore >= 60 ? 'warning' : 'error',
        connectedServices: totalServices,
        dataIntegrity: healthData.digitalTwin?.dataIntegrity || 0,
        dataCollection: healthData.digitalTwin?.dataCollection || 0,
        personalTwins: healthData.digitalTwin?.personalTwins || 0,
        performance: healthData.digitalTwin?.performance || 0,
        aiServices: healthData.aiOrchestrator?.performance || 0,
        packageManagement: healthData.digitalTwin?.packageManagement || 0,
        services: Object.entries(healthData)
          .filter(([_, data]) => data !== null)
          .map(([name, data]) => ({
            name: name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
            status: data?.status || 'unknown',
            responseTime: data?.responseTime || 0
          }))
      };
    } catch (error) {
      console.error('🚨 Failed to get system health:', error);
      throw new Error('Failed to load system health');
    }
  },


  async getServiceHealth(): Promise<ServiceHealth[]> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/health/services`);
      return response.data.services || [];
    } catch (error) {
      console.error('🚨 Failed to get service health:', error);
      throw new Error('Failed to load service health');
    }
  },


  async getPerformanceMetrics(timeRange: string): Promise<PerformanceMetrics> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/health/performance?range=${timeRange}`);
      return response.data;
    } catch (error) {
      console.error('🚨 Failed to get performance metrics:', error);
      throw new Error('Failed to load performance metrics');
    }
  },


  async getHealthAlerts(): Promise<HealthAlert[]> {
    try {
      const response = await bcmAPI.get(`${DIGITAL_TWIN_API_BASE}/health/alerts`);
      return response.data.alerts || [];
    } catch (error) {
      console.error('🚨 Failed to get health alerts:', error);
      throw new Error('Failed to load health alerts');
    }
  },


  // ===== Utility Methods =====

  /**
   * Format timestamp for display
   */
  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minutes ago`;

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
  },

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }
};

/**
 * Initialize Digital Twin API with EventBus integration
 */
export async function initializeDigitalTwinAPI(): Promise<void> {
  try {
    // Initialize EventBus service for real-time updates
    const eventBus = getEventBusService();
    await eventBus.initialize();

    console.log('✅ Digital Twin API initialized with real-time EventBus integration');
  } catch (error) {
    console.error('🚨 Failed to initialize Digital Twin API:', error);
    throw error;
  }
}

export default digitalTwinAPI;