/**
 * Real-time Dashboard Hook for Digital Twin Data
 *
 * Custom React hook for real-time Digital Twin data management with WebSocket integration.
 *
 * Features:
 * - WebSocket event handling for real-time updates
 * - State management for live data synchronization
 * - Connection status and health monitoring
 * - Automatic data refresh on connection restore
 * - Memory leak prevention and cleanup
 * - Error handling and recovery
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getWebSocketService, getEventBusService } from '../services/eventBusService';
import { digitalTwinAPI, initializeDigitalTwinAPI } from '../services/digitalTwinAPI';
import { getCRMLifecycleService } from '../services/crmLifecycleService';
import type {
  DigitalTwinOverview,
  PersonalTwin,
  DataCollectionService,
  TwinDataPackage,
  SystemHealth,
  ServiceHealth,
  PerformanceMetrics,
  HealthAlert
} from '../services/digitalTwinAPI';
import type {
  PersonalTwinEvent,
  DataCollectionEvent,
  PackageManagementEvent,
  SystemHealthEvent,
  UserActivityEvent
} from '../services/eventBusService';

// Hook State Types
export interface RealTimeDigitalTwinState {
  // Data
  overview: DigitalTwinOverview | null;
  personalTwins: PersonalTwin[];
  dataCollectionServices: DataCollectionService[];
  twinDataPackages: TwinDataPackage[];
  systemHealth: SystemHealth | null;
  serviceHealth: ServiceHealth[];
  performanceMetrics: PerformanceMetrics | null;
  healthAlerts: HealthAlert[];

  // Loading States
  loading: {
    overview: boolean;
    personalTwins: boolean;
    services: boolean;
    packages: boolean;
    health: boolean;
  };

  // Error States
  errors: {
    overview: string | null;
    personalTwins: string | null;
    services: string | null;
    packages: string | null;
    health: string | null;
  };

  // Connection Status
  connectionStatus: {
    websocket: boolean;
    eventbus: boolean;
    backend: boolean;
    lastUpdate: Date | null;
    latency: number;
  };

  // Real-time Activity
  recentEvents: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: Date;
    severity: 'info' | 'warning' | 'error' | 'success';
  }>;
}

export interface RealTimeDigitalTwinActions {
  // Data Refresh
  refreshOverview: () => Promise<void>;
  refreshPersonalTwins: () => Promise<void>;
  refreshServices: () => Promise<void>;
  refreshPackages: () => Promise<void>;
  refreshHealth: () => Promise<void>;
  refreshAll: () => Promise<void>;

  // Personal Twin Actions
  syncPersonalTwin: (twinId: string) => Promise<void>;
  deletePersonalTwin: (twinId: string) => Promise<void>;
  updatePrivacySettings: (twinId: string, settings: any) => Promise<void>;

  // Service Actions
  startDataCollection: (serviceId: string) => Promise<void>;
  stopDataCollection: (serviceId: string) => Promise<void>;
  restartDataCollection: (serviceId: string) => Promise<void>;

  // Package Actions
  downloadPackage: (packageId: string) => Promise<void>;
  deletePackage: (packageId: string) => Promise<void>;
  uploadPackage: (file: File) => Promise<void>;

  // Event Management
  clearEvents: () => void;
  acknowledgeAlert: (alertId: string) => void;

  // Connection Management
  reconnect: () => Promise<void>;
  disconnect: () => void;
}

export type UseRealTimeDigitalTwinReturn = RealTimeDigitalTwinState & RealTimeDigitalTwinActions;

/**
 * Real-time Digital Twin Hook
 */
export function useRealTimeDigitalTwin(): UseRealTimeDigitalTwinReturn {
  // State Management
  const [state, setState] = useState<RealTimeDigitalTwinState>({
    // Data
    overview: null,
    personalTwins: [],
    dataCollectionServices: [],
    twinDataPackages: [],
    systemHealth: null,
    serviceHealth: [],
    performanceMetrics: null,
    healthAlerts: [],

    // Loading States
    loading: {
      overview: false,
      personalTwins: false,
      services: false,
      packages: false,
      health: false
    },

    // Error States
    errors: {
      overview: null,
      personalTwins: null,
      services: null,
      packages: null,
      health: null
    },

    // Connection Status
    connectionStatus: {
      websocket: false,
      eventbus: false,
      backend: false,
      lastUpdate: null,
      latency: 0
    },

    // Real-time Activity
    recentEvents: []
  });

  // Refs for cleanup
  const eventUnsubscribers = useRef<Array<() => void>>([]);
  const wsService = useRef(getWebSocketService());
  const eventBusService = useRef(getEventBusService());
  const crmService = useRef(getCRMLifecycleService());
  const isInitialized = useRef(false);

  // Update State Helper
  const updateState = useCallback((updates: Partial<RealTimeDigitalTwinState>) => {
    setState(prev => ({
      ...prev,
      ...updates,
      connectionStatus: {
        ...prev.connectionStatus,
        lastUpdate: new Date(),
        ...updates.connectionStatus
      }
    }));
  }, []);

  // Add Event Helper
  const addEvent = useCallback((event: {
    type: string;
    message: string;
    severity: 'info' | 'warning' | 'error' | 'success';
  }) => {
    const newEvent = {
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      ...event
    };

    setState(prev => ({
      ...prev,
      recentEvents: [newEvent, ...prev.recentEvents.slice(0, 49)] // Keep last 50 events
    }));
  }, []);

  // Error Handler
  const handleError = useCallback((section: keyof RealTimeDigitalTwinState['errors'], error: any) => {
    const errorMessage = error?.message || error?.toString() || 'Unknown error occurred';
    console.error(` Real-time Digital Twin error [${section}]:`, error);

    updateState({
      errors: {
        ...state.errors,
        [section]: errorMessage
      }
    });

    addEvent({
      type: 'error',
      message: `${section}: ${errorMessage}`,
      severity: 'error'
    });
  }, [state.errors, updateState, addEvent]);

  // Data Refresh Functions
  const refreshOverview = useCallback(async () => {
    updateState({ loading: { ...state.loading, overview: true } });
    try {
      const overview = await digitalTwinAPI.getOverview();
      updateState({
        overview,
        loading: { ...state.loading, overview: false },
        errors: { ...state.errors, overview: null }
      });
    } catch (error) {
      handleError('overview', error);
      updateState({ loading: { ...state.loading, overview: false } });
    }
  }, [state.loading, state.errors, updateState, handleError]);

  const refreshPersonalTwins = useCallback(async () => {
    updateState({ loading: { ...state.loading, personalTwins: true } });
    try {
      const personalTwins = await digitalTwinAPI.getPersonalTwins();
      updateState({
        personalTwins,
        loading: { ...state.loading, personalTwins: false },
        errors: { ...state.errors, personalTwins: null }
      });
    } catch (error) {
      handleError('personalTwins', error);
      updateState({ loading: { ...state.loading, personalTwins: false } });
    }
  }, [state.loading, state.errors, updateState, handleError]);

  const refreshServices = useCallback(async () => {
    updateState({ loading: { ...state.loading, services: true } });
    try {
      const dataCollectionServices = await digitalTwinAPI.getDataCollectionServices();
      updateState({
        dataCollectionServices,
        loading: { ...state.loading, services: false },
        errors: { ...state.errors, services: null }
      });
    } catch (error) {
      handleError('services', error);
      updateState({ loading: { ...state.loading, services: false } });
    }
  }, [state.loading, state.errors, updateState, handleError]);

  const refreshPackages = useCallback(async () => {
    updateState({ loading: { ...state.loading, packages: true } });
    try {
      const twinDataPackages = await digitalTwinAPI.getTwinDataPackages();
      updateState({
        twinDataPackages,
        loading: { ...state.loading, packages: false },
        errors: { ...state.errors, packages: null }
      });
    } catch (error) {
      handleError('packages', error);
      updateState({ loading: { ...state.loading, packages: false } });
    }
  }, [state.loading, state.errors, updateState, handleError]);

  const refreshHealth = useCallback(async () => {
    updateState({ loading: { ...state.loading, health: true } });
    try {
      const [systemHealth, serviceHealth, healthAlerts] = await Promise.all([
        digitalTwinAPI.getSystemHealth(),
        digitalTwinAPI.getServiceHealth(),
        digitalTwinAPI.getHealthAlerts()
      ]);

      updateState({
        systemHealth,
        serviceHealth,
        healthAlerts,
        loading: { ...state.loading, health: false },
        errors: { ...state.errors, health: null }
      });
    } catch (error) {
      handleError('health', error);
      updateState({ loading: { ...state.loading, health: false } });
    }
  }, [state.loading, state.errors, updateState, handleError]);

  const refreshAll = useCallback(async () => {
    await Promise.all([
      refreshOverview(),
      refreshPersonalTwins(),
      refreshServices(),
      refreshPackages(),
      refreshHealth()
    ]);
  }, [refreshOverview, refreshPersonalTwins, refreshServices, refreshPackages, refreshHealth]);

  // Personal Twin Actions
  const syncPersonalTwin = useCallback(async (twinId: string) => {
    try {
      await digitalTwinAPI.syncPersonalTwin(twinId);
      addEvent({
        type: 'sync',
        message: `Personal Twin ${twinId} sync initiated`,
        severity: 'info'
      });
      await refreshPersonalTwins();
    } catch (error) {
      handleError('personalTwins', error);
    }
  }, [addEvent, refreshPersonalTwins, handleError]);

  const deletePersonalTwin = useCallback(async (twinId: string) => {
    try {
      await digitalTwinAPI.deletePersonalTwin(twinId);
      addEvent({
        type: 'delete',
        message: `Personal Twin ${twinId} deleted`,
        severity: 'success'
      });
      await refreshPersonalTwins();
    } catch (error) {
      handleError('personalTwins', error);
    }
  }, [addEvent, refreshPersonalTwins, handleError]);

  const updatePrivacySettings = useCallback(async (twinId: string, settings: any) => {
    try {
      await digitalTwinAPI.updatePrivacySettings(twinId, settings);
      addEvent({
        type: 'privacy',
        message: `Privacy settings updated for Twin ${twinId}`,
        severity: 'success'
      });
      await refreshPersonalTwins();
    } catch (error) {
      handleError('personalTwins', error);
    }
  }, [addEvent, refreshPersonalTwins, handleError]);

  // Service Actions
  const startDataCollection = useCallback(async (serviceId: string) => {
    try {
      await digitalTwinAPI.startDataCollection(serviceId);
      addEvent({
        type: 'service_start',
        message: `Data collection started for service ${serviceId}`,
        severity: 'success'
      });
      await refreshServices();
    } catch (error) {
      handleError('services', error);
    }
  }, [addEvent, refreshServices, handleError]);

  const stopDataCollection = useCallback(async (serviceId: string) => {
    try {
      await digitalTwinAPI.stopDataCollection(serviceId);
      addEvent({
        type: 'service_stop',
        message: `Data collection stopped for service ${serviceId}`,
        severity: 'warning'
      });
      await refreshServices();
    } catch (error) {
      handleError('services', error);
    }
  }, [addEvent, refreshServices, handleError]);

  const restartDataCollection = useCallback(async (serviceId: string) => {
    try {
      await digitalTwinAPI.restartDataCollection(serviceId);
      addEvent({
        type: 'service_restart',
        message: `Data collection restarted for service ${serviceId}`,
        severity: 'info'
      });
      await refreshServices();
    } catch (error) {
      handleError('services', error);
    }
  }, [addEvent, refreshServices, handleError]);

  // Package Actions
  const downloadPackage = useCallback(async (packageId: string) => {
    try {
      await digitalTwinAPI.downloadPackage(packageId);
      addEvent({
        type: 'package_download',
        message: `Package ${packageId} download started`,
        severity: 'info'
      });
    } catch (error) {
      handleError('packages', error);
    }
  }, [addEvent, handleError]);

  const deletePackage = useCallback(async (packageId: string) => {
    try {
      await digitalTwinAPI.deletePackage(packageId);
      addEvent({
        type: 'package_delete',
        message: `Package ${packageId} deleted`,
        severity: 'success'
      });
      await refreshPackages();
    } catch (error) {
      handleError('packages', error);
    }
  }, [addEvent, refreshPackages, handleError]);

  const uploadPackage = useCallback(async (file: File) => {
    try {
      await digitalTwinAPI.uploadPackage(file);
      addEvent({
        type: 'package_upload',
        message: `Package ${file.name} upload completed`,
        severity: 'success'
      });
      await refreshPackages();
    } catch (error) {
      handleError('packages', error);
    }
  }, [addEvent, refreshPackages, handleError]);

  // Event Management
  const clearEvents = useCallback(() => {
    updateState({ recentEvents: [] });
  }, [updateState]);

  const acknowledgeAlert = useCallback((alertId: string) => {
    updateState({
      healthAlerts: state.healthAlerts.filter(alert => alert.id !== alertId)
    });
  }, [state.healthAlerts, updateState]);

  // Connection Management
  const reconnect = useCallback(async () => {
    try {
      addEvent({
        type: 'reconnect',
        message: 'Reconnecting to real-time services...',
        severity: 'info'
      });

      await wsService.current.connect();
      await eventBusService.current.initialize();

      updateState({
        connectionStatus: {
          ...state.connectionStatus,
          websocket: wsService.current.isConnected(),
          eventbus: eventBusService.current.isConnected(),
          backend: true
        }
      });

      addEvent({
        type: 'reconnect_success',
        message: 'Successfully reconnected to real-time services',
        severity: 'success'
      });

      // Refresh all data after reconnection
      await refreshAll();

    } catch (error) {
      handleError('health', error);
      addEvent({
        type: 'reconnect_error',
        message: 'Failed to reconnect to real-time services',
        severity: 'error'
      });
    }
  }, [state.connectionStatus, updateState, addEvent, handleError, refreshAll]);

  const disconnect = useCallback(() => {
    wsService.current.disconnect();

    updateState({
      connectionStatus: {
        ...state.connectionStatus,
        websocket: false,
        eventbus: false
      }
    });

    addEvent({
      type: 'disconnect',
      message: 'Disconnected from real-time services',
      severity: 'warning'
    });
  }, [state.connectionStatus, updateState, addEvent]);

  // Event Handlers
  const handlePersonalTwinEvent = useCallback((event: PersonalTwinEvent) => {
    addEvent({
      type: event.type,
      message: `Personal Twin ${event.type}: ${event.data.twinId}`,
      severity: event.type.includes('error') ? 'error' : 'info'
    });

    // Update data if relevant
    if (['personal_twin.created', 'personal_twin.updated', 'personal_twin.deleted'].includes(event.type)) {
      refreshPersonalTwins();
    }
  }, [addEvent, refreshPersonalTwins]);

  const handleDataCollectionEvent = useCallback((event: DataCollectionEvent) => {
    addEvent({
      type: event.type,
      message: `Data Collection ${event.type}: ${event.data.serviceId}`,
      severity: event.type.includes('error') ? 'error' : 'info'
    });

    // Update services data
    refreshServices();
  }, [addEvent, refreshServices]);

  const handlePackageEvent = useCallback((event: PackageManagementEvent) => {
    addEvent({
      type: event.type,
      message: `Package ${event.type}: ${event.data.packageId}`,
      severity: event.type.includes('error') ? 'error' : 'success'
    });

    // Update packages data
    refreshPackages();
  }, [addEvent, refreshPackages]);

  const handleSystemHealthEvent = useCallback((event: SystemHealthEvent) => {
    addEvent({
      type: event.type,
      message: event.data.message || `System ${event.type}`,
      severity: event.data.alertLevel || 'info'
    });

    // Update health data
    refreshHealth();
  }, [addEvent, refreshHealth]);

  const handleUserActivityEvent = useCallback((event: UserActivityEvent) => {
    addEvent({
      type: event.type,
      message: `User Activity: ${event.data.activity || event.type}`,
      severity: 'info'
    });
  }, [addEvent]);

  // Connection Status Monitor
  const updateConnectionStatus = useCallback(() => {
    const wsStatus = wsService.current.getStatus();

    updateState({
      connectionStatus: {
        websocket: wsStatus.connected,
        eventbus: eventBusService.current.isConnected(),
        backend: !state.errors.overview && !state.errors.personalTwins,
        lastUpdate: new Date(),
        latency: wsStatus.latency
      }
    });
  }, [state.errors, updateState]);

  // Initialize Services and Event Listeners
  useEffect(() => {
    if (isInitialized.current) return;

    const initializeServices = async () => {
      try {
        // Initialize all services
        await initializeDigitalTwinAPI();
        await eventBusService.current.initialize();
        await crmService.current.initialize();

        // Set up event subscriptions
        const unsubscribers = [
          eventBusService.current.subscribeToDigitalTwinEvents(handlePersonalTwinEvent),
          eventBusService.current.subscribeToDataCollectionEvents(handleDataCollectionEvent),
          eventBusService.current.subscribeToPackageEvents(handlePackageEvent),
          eventBusService.current.subscribeToSystemHealthEvents(handleSystemHealthEvent),
          eventBusService.current.subscribeToUserActivityEvents(handleUserActivityEvent),
          wsService.current.onStatusChange(updateConnectionStatus)
        ];

        eventUnsubscribers.current = unsubscribers;

        // Initial data load
        await refreshAll();

        updateConnectionStatus();
        isInitialized.current = true;

        addEvent({
          type: 'initialization',
          message: 'Real-time Digital Twin system initialized successfully',
          severity: 'success'
        });

      } catch (error) {
        console.error(' Failed to initialize real-time Digital Twin system:', error);
        addEvent({
          type: 'initialization_error',
          message: 'Failed to initialize real-time system',
          severity: 'error'
        });
      }
    };

    initializeServices();

    // Set up periodic connection status updates
    const statusInterval = setInterval(updateConnectionStatus, 30000); // Every 30 seconds

    // Cleanup function
    return () => {
      clearInterval(statusInterval);
      eventUnsubscribers.current.forEach(unsubscribe => unsubscribe());
      wsService.current.disconnect();
    };
  }, [
    handlePersonalTwinEvent,
    handleDataCollectionEvent,
    handlePackageEvent,
    handleSystemHealthEvent,
    handleUserActivityEvent,
    updateConnectionStatus,
    refreshAll,
    addEvent
  ]);

  // Return the complete state and actions
  return {
    ...state,
    refreshOverview,
    refreshPersonalTwins,
    refreshServices,
    refreshPackages,
    refreshHealth,
    refreshAll,
    syncPersonalTwin,
    deletePersonalTwin,
    updatePrivacySettings,
    startDataCollection,
    stopDataCollection,
    restartDataCollection,
    downloadPackage,
    deletePackage,
    uploadPackage,
    clearEvents,
    acknowledgeAlert,
    reconnect,
    disconnect
  };
}

export default useRealTimeDigitalTwin;