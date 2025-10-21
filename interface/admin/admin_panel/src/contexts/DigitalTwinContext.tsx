import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';

// ===== WebSocket Connection Types =====
interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  source: string;
}

interface ConnectionStatus {
  connected: boolean;
  lastConnected?: Date;
  reconnectAttempts: number;
  latency?: number;
}

interface EventSubscription {
  event: string;
  callback: (data: any) => void;
  id: string;
}

// ===== Digital Twin Context Types =====
interface DigitalTwinContextValue {
  // Connection Status
  connectionStatus: ConnectionStatus;
  isLive: boolean;

  // Data Streams
  overview: any;
  personalTwins: any[];
  services: any[];
  packages: any[];
  systemHealth: any;

  // Event Management
  subscribe: (event: string, callback: (data: any) => void) => string;
  unsubscribe: (subscriptionId: string) => void;

  // Connection Control
  connect: () => void;
  disconnect: () => void;
  toggleLive: () => void;

  // Data Actions
  refreshData: () => Promise<void>;

  // Error Handling
  lastError?: string;
  clearError: () => void;
}

// ===== Context Creation =====
const DigitalTwinContext = createContext<DigitalTwinContextValue | undefined>(undefined);

// ===== WebSocket URL Configuration =====
const WS_URL = import.meta.env.VITE_DIGITAL_TWIN_WS_URL || 'ws://localhost:8000/ws/digital-twin';
const RECONNECT_INTERVAL = 5000;
const MAX_RECONNECT_ATTEMPTS = 10;
const HEARTBEAT_INTERVAL = 30000;

// ===== Provider Component =====
export const DigitalTwinProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Connection State
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
    reconnectAttempts: 0
  });
  const [isLive, setIsLive] = useState(true);
  const [lastError, setLastError] = useState<string>();

  // Data State
  const [overview, setOverview] = useState<any>(null);
  const [personalTwins, setPersonalTwins] = useState<any[]>([]);
  const [services, setServices] = useState<any[]>([]);
  const [packages, setPackages] = useState<any[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);

  // WebSocket and Subscription Management
  const wsRef = useRef<WebSocket | null>(null);
  const subscriptionsRef = useRef<Map<string, EventSubscription>>(new Map());
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();
  const lastHeartbeatRef = useRef<Date>();

  // ===== Event Subscription Management =====
  const subscribe = useCallback((event: string, callback: (data: any) => void): string => {
    const subscriptionId = `${event}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    subscriptionsRef.current.set(subscriptionId, {
      event,
      callback,
      id: subscriptionId
    });

    // If connected, send subscription to server
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        event,
        subscriptionId
      }));
    }

    return subscriptionId;
  }, []);

  const unsubscribe = useCallback((subscriptionId: string) => {
    const subscription = subscriptionsRef.current.get(subscriptionId);
    if (subscription && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        subscriptionId
      }));
    }
    subscriptionsRef.current.delete(subscriptionId);
  }, []);

  // ===== WebSocket Message Handler =====
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      // Update latency if this is a heartbeat response
      if (message.type === 'heartbeat_response') {
        const latency = Date.now() - new Date(message.timestamp).getTime();
        setConnectionStatus(prev => ({ ...prev, latency }));
        lastHeartbeatRef.current = new Date();
        return;
      }

      // Handle data updates
      switch (message.type) {
        case 'overview_update':
          setOverview(message.data);
          break;

        case 'personal_twins_update':
          setPersonalTwins(message.data);
          break;

        case 'services_update':
          setServices(message.data);
          break;

        case 'packages_update':
          setPackages(message.data);
          break;

        case 'system_health_update':
          setSystemHealth(message.data);
          break;

        case 'real_time_metric':
          // Dispatch to subscribers
          subscriptionsRef.current.forEach(subscription => {
            if (subscription.event === message.data.metric || subscription.event === 'all') {
              subscription.callback(message.data);
            }
          });
          break;

        case 'error':
          setLastError(message.data.message);
          console.error('Digital Twin WebSocket Error:', message.data);
          break;

        default:
          // Handle custom events
          subscriptionsRef.current.forEach(subscription => {
            if (subscription.event === message.type) {
              subscription.callback(message.data);
            }
          });
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      setLastError('Failed to parse real-time message');
    }
  }, []);

  // ===== Connection Management =====
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(' Digital Twin WebSocket Connected');
        setConnectionStatus({
          connected: true,
          lastConnected: new Date(),
          reconnectAttempts: 0
        });
        setLastError(undefined);

        // Re-establish subscriptions
        subscriptionsRef.current.forEach(subscription => {
          ws.send(JSON.stringify({
            type: 'subscribe',
            event: subscription.event,
            subscriptionId: subscription.id
          }));
        });

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              type: 'heartbeat',
              timestamp: new Date().toISOString()
            }));
          }
        }, HEARTBEAT_INTERVAL);

        // Request initial data
        ws.send(JSON.stringify({ type: 'get_initial_data' }));
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error(' Digital Twin WebSocket Error:', error);
        setLastError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log(' Digital Twin WebSocket Disconnected:', event.code, event.reason);
        setConnectionStatus(prev => ({
          ...prev,
          connected: false
        }));

        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Attempt reconnection if not manually disconnected
        if (event.code !== 1000 && isLive && connectionStatus.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          const newAttempts = connectionStatus.reconnectAttempts + 1;
          setConnectionStatus(prev => ({
            ...prev,
            reconnectAttempts: newAttempts
          }));

          console.log(` Attempting to reconnect (${newAttempts}/${MAX_RECONNECT_ATTEMPTS}) in ${RECONNECT_INTERVAL}ms...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_INTERVAL);
        }
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setLastError(`Connection failed: ${error.message}`);
    }
  }, [handleMessage, isLive, connectionStatus.reconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setConnectionStatus({
      connected: false,
      reconnectAttempts: 0
    });
  }, []);

  const toggleLive = useCallback(() => {
    const newLiveState = !isLive;
    setIsLive(newLiveState);

    if (newLiveState) {
      connect();
    } else {
      disconnect();
    }
  }, [isLive, connect, disconnect]);

  // ===== Data Refresh =====
  const refreshData = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'refresh_all_data' }));
    } else {
      // Fallback to REST API if WebSocket not available
      try {
        const { digitalTwinAPI } = await import('../services/digitalTwinAPI');

        const [overviewData, twinsData, servicesData, packagesData, healthData] = await Promise.all([
          digitalTwinAPI.getOverview(),
          digitalTwinAPI.getPersonalTwins(),
          digitalTwinAPI.getDataCollectionServices(),
          digitalTwinAPI.getTwinDataPackages(),
          digitalTwinAPI.getSystemHealth()
        ]);

        setOverview(overviewData);
        setPersonalTwins(twinsData);
        setServices(servicesData);
        setPackages(packagesData);
        setSystemHealth(healthData);
      } catch (error) {
        console.error('Failed to refresh data via REST API:', error);
        setLastError('Failed to refresh data');
      }
    }
  }, []);

  // ===== Error Management =====
  const clearError = useCallback(() => {
    setLastError(undefined);
  }, []);

  // ===== Effect: Auto-connect =====
  useEffect(() => {
    if (isLive) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [isLive]);

  // ===== Effect: Connection Health Monitoring =====
  useEffect(() => {
    if (!connectionStatus.connected) return;

    const healthCheckInterval = setInterval(() => {
      // Check if we've received a heartbeat recently
      if (lastHeartbeatRef.current) {
        const timeSinceLastHeartbeat = Date.now() - lastHeartbeatRef.current.getTime();
        if (timeSinceLastHeartbeat > HEARTBEAT_INTERVAL * 2) {
          console.warn(' Heartbeat timeout detected, attempting reconnection');
          disconnect();
          if (isLive) {
            setTimeout(connect, 1000);
          }
        }
      }
    }, HEARTBEAT_INTERVAL);

    return () => clearInterval(healthCheckInterval);
  }, [connectionStatus.connected, isLive, connect, disconnect]);

  // ===== Context Value =====
  const contextValue: DigitalTwinContextValue = {
    // Connection Status
    connectionStatus,
    isLive,

    // Data Streams
    overview,
    personalTwins,
    services,
    packages,
    systemHealth,

    // Event Management
    subscribe,
    unsubscribe,

    // Connection Control
    connect,
    disconnect,
    toggleLive,

    // Data Actions
    refreshData,

    // Error Handling
    lastError,
    clearError
  };

  return (
    <DigitalTwinContext.Provider value={contextValue}>
      {children}
    </DigitalTwinContext.Provider>
  );
};

// ===== Hook for using the context =====
export const useDigitalTwin = (): DigitalTwinContextValue => {
  const context = useContext(DigitalTwinContext);
  if (context === undefined) {
    throw new Error('useDigitalTwin must be used within a DigitalTwinProvider');
  }
  return context;
};

// ===== Specific hooks for different data streams =====
export const useDigitalTwinOverview = () => {
  const { overview, connectionStatus, refreshData } = useDigitalTwin();
  return { overview, connected: connectionStatus.connected, refreshData };
};

export const usePersonalTwins = () => {
  const { personalTwins, connectionStatus, subscribe, unsubscribe } = useDigitalTwin();

  useEffect(() => {
    const subscriptionId = subscribe('personal_twins_update', (data) => {
      // Additional processing if needed
    });

    return () => unsubscribe(subscriptionId);
  }, [subscribe, unsubscribe]);

  return { personalTwins, connected: connectionStatus.connected };
};

export const useDataCollectionServices = () => {
  const { services, connectionStatus, subscribe, unsubscribe } = useDigitalTwin();

  useEffect(() => {
    const subscriptionId = subscribe('services_update', (data) => {
      // Additional processing if needed
    });

    return () => unsubscribe(subscriptionId);
  }, [subscribe, unsubscribe]);

  return { services, connected: connectionStatus.connected };
};

export const useSystemHealth = () => {
  const { systemHealth, connectionStatus, subscribe, unsubscribe } = useDigitalTwin();

  useEffect(() => {
    const subscriptionId = subscribe('system_health_update', (data) => {
      // Additional processing if needed
    });

    return () => unsubscribe(subscriptionId);
  }, [subscribe, unsubscribe]);

  return { systemHealth, connected: connectionStatus.connected };
};

export const useDataPackages = () => {
  const { packages, connectionStatus, subscribe, unsubscribe } = useDigitalTwin();

  useEffect(() => {
    const subscriptionId = subscribe('packages_update', (data) => {
      // Additional processing if needed
    });

    return () => unsubscribe(subscriptionId);
  }, [subscribe, unsubscribe]);

  return { packages, connected: connectionStatus.connected };
};

// ===== Real-time metrics hook =====
export const useRealTimeMetrics = (metric: string, callback: (data: any) => void) => {
  const { subscribe, unsubscribe, connectionStatus } = useDigitalTwin();

  useEffect(() => {
    const subscriptionId = subscribe(`metric:${metric}`, callback);
    return () => unsubscribe(subscriptionId);
  }, [metric, callback, subscribe, unsubscribe]);

  return { connected: connectionStatus.connected, latency: connectionStatus.latency };
};

export default DigitalTwinContext;