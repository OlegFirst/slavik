import { useState, useEffect } from 'react';
import { realtimeService } from '@/services/realtime';

interface MetricsData {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  activeUsers: number;
  requestsPerSecond: number;
  timestamp: string;
}

interface OrganismHealth {
  id: string;
  name: string;
  status: 'healthy' | 'warning' | 'error';
  health_score: number;
  endpoint?: string;
  last_check?: string;
}

interface UseRealtimeReturn {
  isConnected: boolean;
  metrics: MetricsData | null;
  organisms: OrganismHealth[];
  notifications: any[];
  healthStatus: Record<string, any>;
}

export const useRealtime = (): UseRealtimeReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [organisms, setOrganisms] = useState<OrganismHealth[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [healthStatus, setHealthStatus] = useState<Record<string, any>>({});

  useEffect(() => {
    // Connect to realtime service
    realtimeService.connect();

    // Connection status listeners
    realtimeService.onConnect(() => {
      console.log(' Realtime service connected');
      setIsConnected(true);
    });

    realtimeService.onDisconnect(() => {
      console.log(' Realtime service disconnected');
      setIsConnected(false);
    });

    // Data listeners
    realtimeService.onMetrics((data: MetricsData) => {
      console.log(' Metrics update:', data);
      setMetrics(data);
    });

    realtimeService.onOrganisms((data: OrganismHealth[]) => {
      console.log(' Organisms update:', data);
      setOrganisms(data);
    });

    realtimeService.onNotification((data: any) => {
      console.log(' Notification:', data);
      setNotifications(prev => [data, ...prev.slice(0, 49)]); // Keep last 50
    });

    realtimeService.onHealth((data: Record<string, any>) => {
      console.log('️ Health update:', data);
      setHealthStatus(data);
    });

    // Subscribe to topics
    realtimeService.subscribe('metrics');
    realtimeService.subscribe('organisms');
    realtimeService.subscribe('notifications');
    realtimeService.subscribe('health');

    // Cleanup on unmount
    return () => {
      realtimeService.disconnect();
    };
  }, []);

  return {
    isConnected,
    metrics,
    organisms,
    notifications,
    healthStatus
  };
};