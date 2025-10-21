/**
 * useRealtime Hook
 *
 * Real-time data updates via WebSocket connection to Monitoring Backend
 */

import { useState, useEffect, useCallback } from 'react';

interface RealtimeData {
  type: string;
  timestamp: string;
  data: any;
}

export const useRealtime = (url: string = 'ws://localhost:8050/ws') => {
  const [data, setData] = useState<RealtimeData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        ws = new WebSocket(url);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setError(null);
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            setData(message);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
          }
        };

        ws.onerror = (event) => {
          console.error('WebSocket error:', event);
          setError('WebSocket connection error');
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);

          // Reconnect after 5 seconds
          reconnectTimeout = setTimeout(() => {
            console.log('Reconnecting...');
            connect();
          }, 5000);
        };
      } catch (err) {
        console.error('Failed to create WebSocket:', err);
        setError('Failed to create WebSocket connection');
      }
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [url]);

  const send = useCallback((message: any) => {
    // WebSocket send functionality (if needed)
    console.log('Send message:', message);
  }, []);

  return {
    data,
    metrics: data?.data, // Alias for compatibility with Analytics.tsx
    isConnected,
    error,
    send
  };
};
