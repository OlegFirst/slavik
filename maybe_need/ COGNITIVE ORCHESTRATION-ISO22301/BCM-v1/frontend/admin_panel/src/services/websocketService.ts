/**
 * Production-ready WebSocket Service for Digital Twin Real-time Communication
 *
 * Features:
 * - Real WebSocket connection to EventBus (ws://localhost:8001/ws)
 * - Automatic reconnection with exponential backoff
 * - Channel subscription management for Digital Twin updates
 * - Message queuing during disconnection
 * - Connection status monitoring
 * - Memory leak prevention
 * - Performance optimization for high-frequency updates
 */

export interface WebSocketMessage {
  type: string;
  channel: string;
  data: any;
  timestamp: number;
  id: string;
}

export interface ConnectionStatus {
  connected: boolean;
  reconnecting: boolean;
  lastConnected: Date | null;
  connectionAttempts: number;
  latency: number;
  queuedMessages: number;
}

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  maxReconnectAttempts?: number;
  reconnectBaseDelay?: number;
  maxReconnectDelay?: number;
  heartbeatInterval?: number;
  messageQueueLimit?: number;
  enableMessageQueue?: boolean;
}

export type MessageHandler = (message: WebSocketMessage) => void;
export type StatusHandler = (status: ConnectionStatus) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private messageHandlers = new Map<string, Set<MessageHandler>>();
  private statusHandlers = new Set<StatusHandler>();
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private heartbeatIntervalId: NodeJS.Timeout | null = null;
  private connectionAttempts = 0;
  private messageQueue: WebSocketMessage[] = [];
  private subscribedChannels = new Set<string>();
  private lastPingTime = 0;
  private latency = 0;
  private isReconnecting = false;
  private shouldReconnect = true;

  constructor(config: WebSocketConfig) {
    this.config = {
      protocols: [],
      maxReconnectAttempts: 10,
      reconnectBaseDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000,
      messageQueueLimit: 1000,
      enableMessageQueue: true,
      ...config
    };
  }

  /**
   * Connect to WebSocket server with automatic reconnection
   */
  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.shouldReconnect = true;
      this._connect()
        .then(() => resolve())
        .catch((error) => reject(error));
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    this.shouldReconnect = false;
    this._clearTimers();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this._updateStatus();
  }

  /**
   * Subscribe to message handlers for specific channels
   */
  public onMessage(channel: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(channel)) {
      this.messageHandlers.set(channel, new Set());
    }

    this.messageHandlers.get(channel)!.add(handler);

    // Auto-subscribe to channel if connected
    if (this.isConnected()) {
      this.subscribeToChannel(channel);
    }

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(channel);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(channel);
          this.unsubscribeFromChannel(channel);
        }
      }
    };
  }

  /**
   * Subscribe to connection status updates
   */
  public onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);

    // Send current status immediately
    handler(this.getStatus());

    return () => {
      this.statusHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to specific EventBus channel
   */
  public subscribeToChannel(channel: string): void {
    if (!this.subscribedChannels.has(channel)) {
      this.subscribedChannels.add(channel);

      if (this.isConnected()) {
        this._sendMessage({
          type: 'subscribe',
          channel: channel,
          data: {},
          timestamp: Date.now(),
          id: this._generateId()
        });
      }
    }
  }

  /**
   * Unsubscribe from specific EventBus channel
   */
  public unsubscribeFromChannel(channel: string): void {
    if (this.subscribedChannels.has(channel)) {
      this.subscribedChannels.delete(channel);

      if (this.isConnected()) {
        this._sendMessage({
          type: 'unsubscribe',
          channel: channel,
          data: {},
          timestamp: Date.now(),
          id: this._generateId()
        });
      }
    }
  }

  /**
   * Send message to WebSocket server
   */
  public sendMessage(message: Omit<WebSocketMessage, 'timestamp' | 'id'>): void {
    const fullMessage: WebSocketMessage = {
      ...message,
      timestamp: Date.now(),
      id: this._generateId()
    };

    this._sendMessage(fullMessage);
  }

  /**
   * Get current connection status
   */
  public getStatus(): ConnectionStatus {
    return {
      connected: this.isConnected(),
      reconnecting: this.isReconnecting,
      lastConnected: this.ws && this.ws.readyState === WebSocket.OPEN ? new Date() : null,
      connectionAttempts: this.connectionAttempts,
      latency: this.latency,
      queuedMessages: this.messageQueue.length
    };
  }

  /**
   * Check if WebSocket is connected
   */
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get list of subscribed channels
   */
  public getSubscribedChannels(): string[] {
    return Array.from(this.subscribedChannels);
  }

  /**
   * Clear message queue
   */
  public clearMessageQueue(): void {
    this.messageQueue = [];
    this._updateStatus();
  }

  // Private methods

  private async _connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.isReconnecting = this.connectionAttempts > 0;
        this.connectionAttempts++;

        // Production logging conditional on environment
        if (import.meta.env.NODE_ENV !== 'production') {
          console.log(`🔗 Attempting to connect to EventBus WebSocket: ${this.config.url} (attempt ${this.connectionAttempts})`);
        }

        this.ws = new WebSocket(this.config.url, this.config.protocols);

        this.ws.onopen = () => {
          if (import.meta.env.NODE_ENV !== 'production') {
            console.log('✅ WebSocket connected to EventBus');
          }
          this.connectionAttempts = 0;
          this.isReconnecting = false;

          this._startHeartbeat();
          this._resubscribeToChannels();
          this._processMessageQueue();
          this._updateStatus();

          resolve();
        };

        this.ws.onmessage = (event) => {
          this._handleMessage(event);
        };

        this.ws.onclose = (event) => {
          if (import.meta.env.NODE_ENV !== 'production') {
            console.log(`❌ WebSocket connection closed: ${event.code} - ${event.reason}`);
          }
          this._clearTimers();
          this._handleDisconnection();
        };

        this.ws.onerror = (error) => {
          console.error('🚨 WebSocket error:', error);
          reject(new Error('WebSocket connection failed'));
        };

        // Connection timeout
        const timeoutId = setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            this.ws.close();
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);

        this.ws.addEventListener('open', () => clearTimeout(timeoutId));

      } catch (error) {
        console.error('🚨 Failed to create WebSocket connection:', error);
        reject(error);
      }
    });
  }

  private _handleMessage(event: MessageEvent): void {
    try {
      // Input validation for WebSocket messages
      const rawMessage = JSON.parse(event.data);
      if (!rawMessage || typeof rawMessage !== 'object' || !rawMessage.type) {
        if (import.meta.env.NODE_ENV !== 'production') {
          console.warn('Invalid WebSocket message format:', rawMessage);
        }
        return;
      }

      const message: WebSocketMessage = rawMessage;

      // Handle pong response for latency calculation
      if (message.type === 'pong') {
        this.latency = Date.now() - this.lastPingTime;
        this._updateStatus();
        return;
      }

      // Route message to appropriate handlers
      const handlers = this.messageHandlers.get(message.channel);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error('🚨 Error in message handler:', error);
          }
        });
      }

      // Route to global handlers (channel '*')
      const globalHandlers = this.messageHandlers.get('*');
      if (globalHandlers) {
        globalHandlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error('🚨 Error in global message handler:', error);
          }
        });
      }

    } catch (error) {
      console.error('🚨 Failed to parse WebSocket message:', error);
    }
  }

  private _handleDisconnection(): void {
    this._clearTimers();
    this._updateStatus();

    if (this.shouldReconnect && this.connectionAttempts < this.config.maxReconnectAttempts) {
      this._scheduleReconnection();
    } else if (this.connectionAttempts >= this.config.maxReconnectAttempts) {
      console.error('🚨 Max reconnection attempts reached. Giving up.');
      this.shouldReconnect = false;
    }
  }

  private _scheduleReconnection(): void {
    const delay = Math.min(
      this.config.reconnectBaseDelay * Math.pow(2, this.connectionAttempts - 1),
      this.config.maxReconnectDelay
    );

    console.log(`🔄 Scheduling reconnection in ${delay}ms...`);

    this.reconnectTimeoutId = setTimeout(() => {
      if (this.shouldReconnect) {
        this._connect().catch(error => {
          console.error('🚨 Reconnection failed:', error);
        });
      }
    }, delay);
  }

  private _sendMessage(message: WebSocketMessage): void {
    if (this.isConnected()) {
      try {
        this.ws!.send(JSON.stringify(message));
      } catch (error) {
        console.error('🚨 Failed to send WebSocket message:', error);
        this._queueMessage(message);
      }
    } else if (this.config.enableMessageQueue) {
      this._queueMessage(message);
    }
  }

  private _queueMessage(message: WebSocketMessage): void {
    if (this.messageQueue.length >= this.config.messageQueueLimit) {
      // Remove oldest message to make room
      this.messageQueue.shift();
    }

    this.messageQueue.push(message);
    this._updateStatus();
  }

  private _processMessageQueue(): void {
    if (this.messageQueue.length > 0 && this.isConnected()) {
      console.log(`📤 Processing ${this.messageQueue.length} queued messages...`);

      const messages = [...this.messageQueue];
      this.messageQueue = [];

      messages.forEach(message => {
        this._sendMessage(message);
      });

      this._updateStatus();
    }
  }

  private _resubscribeToChannels(): void {
    if (this.subscribedChannels.size > 0) {
      console.log(`🔄 Re-subscribing to ${this.subscribedChannels.size} channels...`);

      this.subscribedChannels.forEach(channel => {
        this._sendMessage({
          type: 'subscribe',
          channel: channel,
          data: {},
          timestamp: Date.now(),
          id: this._generateId()
        });
      });
    }
  }

  private _startHeartbeat(): void {
    if (this.config.heartbeatInterval > 0) {
      this.heartbeatIntervalId = setInterval(() => {
        if (this.isConnected()) {
          this.lastPingTime = Date.now();
          this._sendMessage({
            type: 'ping',
            channel: 'system',
            data: { timestamp: this.lastPingTime },
            timestamp: this.lastPingTime,
            id: this._generateId()
          });
        }
      }, this.config.heartbeatInterval);
    }
  }

  private _clearTimers(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }

    if (this.heartbeatIntervalId) {
      clearInterval(this.heartbeatIntervalId);
      this.heartbeatIntervalId = null;
    }
  }

  private _updateStatus(): void {
    const status = this.getStatus();
    this.statusHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        console.error('🚨 Error in status handler:', error);
      }
    });
  }

  private _generateId(): string {
    return `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Global WebSocket service instance
let webSocketService: WebSocketService | null = null;

/**
 * Get or create the global WebSocket service instance
 */
export function getWebSocketService(): WebSocketService {
  if (!webSocketService) {
    const config: WebSocketConfig = {
      url: import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws',
      protocols: ['eventbus-v1'],
      maxReconnectAttempts: 15,
      reconnectBaseDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000,
      messageQueueLimit: 2000,
      enableMessageQueue: true
    };

    webSocketService = new WebSocketService(config);
  }

  return webSocketService;
}

/**
 * Initialize WebSocket connection
 */
export async function initializeWebSocket(): Promise<WebSocketService> {
  const service = getWebSocketService();
  await service.connect();
  return service;
}

/**
 * Cleanup WebSocket connection
 */
export function cleanupWebSocket(): void {
  if (webSocketService) {
    webSocketService.disconnect();
    webSocketService = null;
  }
}

export default WebSocketService;