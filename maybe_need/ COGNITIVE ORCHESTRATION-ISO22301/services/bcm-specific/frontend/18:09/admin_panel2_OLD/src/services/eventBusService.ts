/**
 * EventBus Integration Service for Digital Twin Lifecycle Events
 *
 * This service acts as the "information highway" connecting all BCM microservices
 * through the EventBus real-time messaging system.
 *
 * Features:
 * - Subscribe to Digital Twin lifecycle events
 * - Personal Twin creation/update/deletion events
 * - Data collection status changes
 * - Package management events
 * - System health alerts
 * - Multi-channel event routing
 * - Real-time cross-service communication
 */

import { getWebSocketService, WebSocketMessage } from './websocketService';
import type { PersonalTwin, DataCollectionService, TwinDataPackage, SystemHealth } from './digitalTwinAPI';

// Event Types
export interface DigitalTwinEvent {
  id: string;
  type: string;
  source: string;
  target?: string;
  timestamp: number;
  data: any;
  metadata?: Record<string, any>;
}

export interface PersonalTwinEvent extends DigitalTwinEvent {
  type: 'personal_twin.created' | 'personal_twin.updated' | 'personal_twin.deleted' | 'personal_twin.synced';
  data: {
    twinId: string;
    userId: string;
    twin?: Partial<PersonalTwin>;
    changes?: Record<string, any>;
  };
}

export interface DataCollectionEvent extends DigitalTwinEvent {
  type: 'data_collection.started' | 'data_collection.stopped' | 'data_collection.error' | 'data_collection.completed';
  data: {
    serviceId: string;
    service?: Partial<DataCollectionService>;
    metrics?: Record<string, number>;
    error?: string;
  };
}

export interface PackageManagementEvent extends DigitalTwinEvent {
  type: 'package.created' | 'package.updated' | 'package.deleted' | 'package.uploaded' | 'package.downloaded';
  data: {
    packageId: string;
    package?: Partial<TwinDataPackage>;
    progress?: number;
    error?: string;
  };
}

export interface SystemHealthEvent extends DigitalTwinEvent {
  type: 'system.health_changed' | 'system.service_status' | 'system.alert' | 'system.performance';
  data: {
    health?: Partial<SystemHealth>;
    serviceName?: string;
    alertLevel?: 'info' | 'warning' | 'error' | 'critical';
    message?: string;
    metrics?: Record<string, number>;
  };
}

export interface UserActivityEvent extends DigitalTwinEvent {
  type: 'user.login' | 'user.logout' | 'user.activity' | 'user.created' | 'user.updated';
  data: {
    userId: string;
    userName?: string;
    userEmail?: string;
    activity?: string;
    sessionId?: string;
  };
}

export interface ServiceCommunicationEvent extends DigitalTwinEvent {
  type: 'service.request' | 'service.response' | 'service.error' | 'service.notification';
  data: {
    fromService: string;
    toService: string;
    method?: string;
    endpoint?: string;
    status?: number;
    responseTime?: number;
    error?: string;
  };
}

// Event Channel Definitions
export const EVENTBUS_CHANNELS = {
  // Digital Twin Channels
  PERSONAL_TWINS: 'digital_twin.personal',
  ORGANIZATIONAL_TWINS: 'digital_twin.organizational',
  DATA_COLLECTION: 'digital_twin.data_collection',
  PACKAGE_MANAGEMENT: 'digital_twin.packages',

  // System Channels
  SYSTEM_HEALTH: 'system.health',
  SYSTEM_PERFORMANCE: 'system.performance',
  SYSTEM_ALERTS: 'system.alerts',

  // User & CRM Channels
  USER_LIFECYCLE: 'crm.users',
  USER_ACTIVITY: 'crm.activity',
  USER_SESSIONS: 'crm.sessions',

  // Service Communication
  SERVICE_MESH: 'services.mesh',
  SERVICE_DISCOVERY: 'services.discovery',
  SERVICE_MONITORING: 'services.monitoring',

  // BCM Module Channels
  BCM_CORE: 'bcm.core',
  BCM_COMPLIANCE: 'bcm.compliance',
  BCM_RISK: 'bcm.risk',
  BCM_GOVERNANCE: 'bcm.governance',
  BCM_AUDIT: 'bcm.audit',
  BCM_BIA: 'bcm.bia',
  BCM_INCIDENT: 'bcm.incident',
  BCM_REPORTING: 'bcm.reporting',

  // AI Services
  AI_ORCHESTRATOR: 'ai.orchestrator',
  AI_INSIGHTS: 'ai.insights',
  AI_ANALYSIS: 'ai.analysis',

  // Global/Broadcast Channel
  GLOBAL: 'global.*'
} as const;

export type EventBusChannel = typeof EVENTBUS_CHANNELS[keyof typeof EVENTBUS_CHANNELS];

// Event Handlers
export type EventHandler<T = DigitalTwinEvent> = (event: T) => void | Promise<void>;

class EventBusService {
  private wsService = getWebSocketService();
  private eventHandlers = new Map<string, Set<EventHandler>>();
  private channelSubscriptions = new Map<string, number>();
  private isInitialized = false;

  /**
   * Initialize EventBus service
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      // Ensure WebSocket connection
      await this.wsService.connect();

      // Set up global message handler
      this.wsService.onMessage('*', this.handleWebSocketMessage.bind(this));

      // Subscribe to essential channels
      await this.subscribeToEssentialChannels();

      this.isInitialized = true;
      console.log('✅ EventBus service initialized successfully');

    } catch (error) {
      console.error('🚨 Failed to initialize EventBus service:', error);
      throw error;
    }
  }

  /**
   * Subscribe to Digital Twin lifecycle events
   */
  public subscribeToDigitalTwinEvents(handler: EventHandler<PersonalTwinEvent>): () => void {
    return this.subscribe(EVENTBUS_CHANNELS.PERSONAL_TWINS, handler);
  }

  /**
   * Subscribe to data collection events
   */
  public subscribeToDataCollectionEvents(handler: EventHandler<DataCollectionEvent>): () => void {
    return this.subscribe(EVENTBUS_CHANNELS.DATA_COLLECTION, handler);
  }

  /**
   * Subscribe to package management events
   */
  public subscribeToPackageEvents(handler: EventHandler<PackageManagementEvent>): () => void {
    return this.subscribe(EVENTBUS_CHANNELS.PACKAGE_MANAGEMENT, handler);
  }

  /**
   * Subscribe to system health events
   */
  public subscribeToSystemHealthEvents(handler: EventHandler<SystemHealthEvent>): () => void {
    return this.subscribe(EVENTBUS_CHANNELS.SYSTEM_HEALTH, handler);
  }

  /**
   * Subscribe to user activity events
   */
  public subscribeToUserActivityEvents(handler: EventHandler<UserActivityEvent>): () => void {
    return this.subscribe(EVENTBUS_CHANNELS.USER_ACTIVITY, handler);
  }

  /**
   * Subscribe to service communication events
   */
  public subscribeToServiceMeshEvents(handler: EventHandler<ServiceCommunicationEvent>): () => void {
    return this.subscribe(EVENTBUS_CHANNELS.SERVICE_MESH, handler);
  }

  /**
   * Subscribe to specific channel with event handler
   */
  public subscribe<T = DigitalTwinEvent>(channel: string, handler: EventHandler<T>): () => void {
    // Add handler to the set
    if (!this.eventHandlers.has(channel)) {
      this.eventHandlers.set(channel, new Set());
    }
    this.eventHandlers.get(channel)!.add(handler as EventHandler);

    // Track channel subscription count
    const currentCount = this.channelSubscriptions.get(channel) || 0;
    this.channelSubscriptions.set(channel, currentCount + 1);

    // Subscribe to WebSocket channel if first subscription
    if (currentCount === 0) {
      this.wsService.subscribeToChannel(channel);
      console.log(`📡 Subscribed to EventBus channel: ${channel}`);
    }

    // Return unsubscribe function
    return () => {
      const handlers = this.eventHandlers.get(channel);
      if (handlers) {
        handlers.delete(handler as EventHandler);

        const newCount = this.channelSubscriptions.get(channel)! - 1;
        this.channelSubscriptions.set(channel, newCount);

        // Unsubscribe from WebSocket channel if no more handlers
        if (newCount === 0 && handlers.size === 0) {
          this.eventHandlers.delete(channel);
          this.channelSubscriptions.delete(channel);
          this.wsService.unsubscribeFromChannel(channel);
          console.log(`📡 Unsubscribed from EventBus channel: ${channel}`);
        }
      }
    };
  }

  /**
   * Publish event to specific channel
   */
  public async publishEvent(channel: string, event: Omit<DigitalTwinEvent, 'id' | 'timestamp'>): Promise<void> {
    const fullEvent: DigitalTwinEvent = {
      id: this.generateEventId(),
      timestamp: Date.now(),
      ...event
    };

    try {
      this.wsService.sendMessage({
        type: 'publish',
        channel: channel,
        data: fullEvent,
        timestamp: Date.now(),
        id: this.generateEventId()
      });

      console.log(`📤 Published event to ${channel}:`, fullEvent.type);
    } catch (error) {
      console.error('🚨 Failed to publish event:', error);
      throw error;
    }
  }

  /**
   * Request specific data from services
   */
  public async requestData(service: string, request: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const requestId = this.generateEventId();
      const timeoutId = setTimeout(() => {
        reject(new Error(`Request timeout for service: ${service}`));
      }, 30000);

      // Set up response handler
      const unsubscribe = this.subscribe('service.response', (event: ServiceCommunicationEvent) => {
        if (event.metadata?.requestId === requestId) {
          clearTimeout(timeoutId);
          unsubscribe();

          if (event.data.error) {
            reject(new Error(event.data.error));
          } else {
            resolve(event.data);
          }
        }
      });

      // Send request
      this.publishEvent(EVENTBUS_CHANNELS.SERVICE_MESH, {
        type: 'service.request',
        source: 'admin_panel',
        target: service,
        data: request,
        metadata: { requestId }
      });
    });
  }

  /**
   * Broadcast system-wide notification
   */
  public async broadcastNotification(notification: {
    title: string;
    message: string;
    severity: 'info' | 'warning' | 'error' | 'success';
    targetUsers?: string[];
    persistent?: boolean;
  }): Promise<void> {
    await this.publishEvent(EVENTBUS_CHANNELS.GLOBAL, {
      type: 'system.notification',
      source: 'admin_panel',
      data: notification
    });
  }

  /**
   * Get active channel subscriptions
   */
  public getActiveChannels(): string[] {
    return Array.from(this.channelSubscriptions.keys());
  }

  /**
   * Get subscription count for channel
   */
  public getChannelSubscriptionCount(channel: string): number {
    return this.channelSubscriptions.get(channel) || 0;
  }

  /**
   * Check if EventBus is connected
   */
  public isConnected(): boolean {
    return this.wsService.isConnected();
  }

  /**
   * Get connection status
   */
  public getConnectionStatus() {
    return this.wsService.getStatus();
  }

  // Private methods

  private async subscribeToEssentialChannels(): Promise<void> {
    const essentialChannels = [
      EVENTBUS_CHANNELS.SYSTEM_HEALTH,
      EVENTBUS_CHANNELS.SYSTEM_ALERTS,
      EVENTBUS_CHANNELS.PERSONAL_TWINS,
      EVENTBUS_CHANNELS.DATA_COLLECTION,
      EVENTBUS_CHANNELS.USER_ACTIVITY,
      EVENTBUS_CHANNELS.SERVICE_MESH
    ];

    for (const channel of essentialChannels) {
      this.wsService.subscribeToChannel(channel);
    }

    console.log(`📡 Subscribed to ${essentialChannels.length} essential EventBus channels`);
  }

  private handleWebSocketMessage(message: WebSocketMessage): void {
    try {
      // Parse event from message data
      const event: DigitalTwinEvent = message.data;

      // Route to appropriate handlers
      const handlers = this.eventHandlers.get(message.channel);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(event);
          } catch (error) {
            console.error(`🚨 Error in EventBus handler for ${message.channel}:`, error);
          }
        });
      }

      // Log important events
      if (this.shouldLogEvent(event)) {
        console.log(`📨 EventBus event [${message.channel}]:`, event.type, event.data);
      }

    } catch (error) {
      console.error('🚨 Failed to handle EventBus message:', error);
    }
  }

  private shouldLogEvent(event: DigitalTwinEvent): boolean {
    // Log important event types
    const importantTypes = [
      'personal_twin.created',
      'personal_twin.deleted',
      'system.alert',
      'data_collection.error',
      'package.created',
      'user.login',
      'user.logout',
      'service.error'
    ];

    return importantTypes.includes(event.type);
  }

  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Global EventBus service instance
let eventBusService: EventBusService | null = null;

/**
 * Get or create the global EventBus service instance
 */
export function getEventBusService(): EventBusService {
  if (!eventBusService) {
    eventBusService = new EventBusService();
  }
  return eventBusService;
}

/**
 * Initialize EventBus service
 */
export async function initializeEventBus(): Promise<EventBusService> {
  const service = getEventBusService();
  await service.initialize();
  return service;
}

/**
 * Helper function to create typed event publishers
 */
export function createEventPublisher<T extends DigitalTwinEvent>(
  channel: string,
  source: string
) {
  const eventBus = getEventBusService();

  return async (event: Omit<T, 'id' | 'timestamp' | 'source'>): Promise<void> => {
    await eventBus.publishEvent(channel, {
      ...event,
      source
    });
  };
}

// Pre-configured event publishers
export const publishPersonalTwinEvent = createEventPublisher<PersonalTwinEvent>(
  EVENTBUS_CHANNELS.PERSONAL_TWINS,
  'admin_panel'
);

export const publishDataCollectionEvent = createEventPublisher<DataCollectionEvent>(
  EVENTBUS_CHANNELS.DATA_COLLECTION,
  'admin_panel'
);

export const publishPackageEvent = createEventPublisher<PackageManagementEvent>(
  EVENTBUS_CHANNELS.PACKAGE_MANAGEMENT,
  'admin_panel'
);

export const publishSystemHealthEvent = createEventPublisher<SystemHealthEvent>(
  EVENTBUS_CHANNELS.SYSTEM_HEALTH,
  'admin_panel'
);

export default EventBusService;