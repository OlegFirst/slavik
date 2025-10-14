/**
 * Real-time System Initializer
 *
 * Main initialization and orchestration file for the complete real-time
 * WebSocket + EventBus integration system.
 *
 * This file coordinates the startup of all real-time services and ensures
 * proper initialization order and error handling.
 */

import { initializeWebSocket, cleanupWebSocket } from './websocketService';
import { initializeEventBus, getEventBusService } from './eventBusService';
import { initializeCRMLifecycle, getCRMLifecycleService } from './crmLifecycleService';
import { initializeDigitalTwinAPI } from './digitalTwinAPI';
import { getChannelManager } from './eventBusChannels';
import { validateRealTimeIntegration } from './realTimeIntegrationValidator';
import type { IntegrationValidationReport } from './realTimeIntegrationValidator';

// Initialization Status
export interface RealTimeSystemStatus {
  initialized: boolean;
  initializationTime: number;
  components: {
    websocket: boolean;
    eventBus: boolean;
    crmLifecycle: boolean;
    digitalTwinAPI: boolean;
    channelManager: boolean;
  };
  errors: string[];
  validationReport?: IntegrationValidationReport;
}

// System Events
export type SystemEventType =
  | 'initialization_started'
  | 'initialization_completed'
  | 'initialization_failed'
  | 'component_ready'
  | 'component_failed'
  | 'validation_completed'
  | 'system_ready';

export interface SystemEvent {
  type: SystemEventType;
  component?: string;
  message: string;
  timestamp: Date;
  error?: string;
}

// Event Listeners
type SystemEventListener = (event: SystemEvent) => void;

class RealTimeSystemInitializer {
  private status: RealTimeSystemStatus = {
    initialized: false,
    initializationTime: 0,
    components: {
      websocket: false,
      eventBus: false,
      crmLifecycle: false,
      digitalTwinAPI: false,
      channelManager: false
    },
    errors: []
  };

  private eventListeners: SystemEventListener[] = [];
  private startTime = 0;

  /**
   * Initialize the complete real-time system
   */
  public async initialize(options: {
    runValidation?: boolean;
    enableLogging?: boolean;
    skipOptionalComponents?: boolean;
  } = {}): Promise<RealTimeSystemStatus> {

    const {
      runValidation = true,
      enableLogging = true,
      skipOptionalComponents = false
    } = options;

    this.startTime = Date.now();
    this.status.errors = [];

    if (enableLogging) {
      console.log('🚀 Initializing Real-time Digital Twin System...');
    }

    this.emitEvent({
      type: 'initialization_started',
      message: 'Real-time system initialization started',
      timestamp: new Date()
    });

    try {
      // Step 1: Initialize Channel Manager (no dependencies)
      await this.initializeComponent('channelManager', async () => {
        const channelManager = getChannelManager();
        // Channel manager is always ready (no async initialization needed)
        return true;
      }, enableLogging);

      // Step 2: Initialize WebSocket Service
      await this.initializeComponent('websocket', async () => {
        const wsService = await initializeWebSocket();
        return wsService.isConnected();
      }, enableLogging);

      // Step 3: Initialize EventBus Service (depends on WebSocket)
      await this.initializeComponent('eventBus', async () => {
        const eventBusService = await initializeEventBus();
        return eventBusService.isConnected();
      }, enableLogging);

      // Step 4: Initialize Digital Twin API (depends on EventBus)
      await this.initializeComponent('digitalTwinAPI', async () => {
        await initializeDigitalTwinAPI();
        return true; // API is considered ready if no errors thrown
      }, enableLogging);

      // Step 5: Initialize CRM Lifecycle Service (optional, depends on EventBus)
      if (!skipOptionalComponents) {
        await this.initializeComponent('crmLifecycle', async () => {
          const crmService = await initializeCRMLifecycle();
          return true; // Service is considered ready if no errors thrown
        }, enableLogging, true); // Mark as optional
      }

      // Calculate initialization time
      this.status.initializationTime = Date.now() - this.startTime;
      this.status.initialized = this.isSystemReady();

      if (enableLogging) {
        if (this.status.initialized) {
          console.log(`✅ Real-time system initialized successfully in ${this.status.initializationTime}ms`);
        } else {
          console.log(`⚠️ Real-time system partially initialized in ${this.status.initializationTime}ms`);
        }
      }

      // Step 6: Run validation if requested
      if (runValidation) {
        if (enableLogging) {
          console.log('🔍 Running system validation...');
        }

        try {
          this.status.validationReport = await validateRealTimeIntegration();

          this.emitEvent({
            type: 'validation_completed',
            message: `Validation completed: ${this.status.validationReport.overallResult}`,
            timestamp: new Date()
          });

          if (enableLogging) {
            console.log(`📊 Validation completed: ${this.status.validationReport.overallResult.toUpperCase()}`);
          }
        } catch (validationError) {
          const errorMsg = `Validation failed: ${validationError.message}`;
          this.status.errors.push(errorMsg);

          if (enableLogging) {
            console.warn('⚠️ System validation failed:', validationError);
          }
        }
      }

      // Emit final status
      if (this.status.initialized) {
        this.emitEvent({
          type: 'system_ready',
          message: 'Real-time system is ready for use',
          timestamp: new Date()
        });
      }

      this.emitEvent({
        type: this.status.initialized ? 'initialization_completed' : 'initialization_failed',
        message: this.status.initialized
          ? 'System initialization completed successfully'
          : 'System initialization completed with errors',
        timestamp: new Date()
      });

    } catch (error) {
      const errorMsg = `System initialization failed: ${error.message}`;
      this.status.errors.push(errorMsg);
      this.status.initializationTime = Date.now() - this.startTime;

      this.emitEvent({
        type: 'initialization_failed',
        message: errorMsg,
        timestamp: new Date(),
        error: error.message
      });

      if (enableLogging) {
        console.error('🚨 Real-time system initialization failed:', error);
      }
    }

    return this.status;
  }

  /**
   * Initialize individual component with error handling
   */
  private async initializeComponent(
    componentName: keyof RealTimeSystemStatus['components'],
    initializeFunc: () => Promise<boolean>,
    enableLogging: boolean,
    optional: boolean = false
  ): Promise<void> {
    try {
      if (enableLogging) {
        console.log(`🔧 Initializing ${componentName}...`);
      }

      const success = await initializeFunc();
      this.status.components[componentName] = success;

      const message = success
        ? `${componentName} initialized successfully`
        : `${componentName} initialization completed with warnings`;

      this.emitEvent({
        type: success ? 'component_ready' : 'component_failed',
        component: componentName,
        message,
        timestamp: new Date()
      });

      if (enableLogging) {
        console.log(`${success ? '✅' : '⚠️'} ${message}`);
      }

      if (!success && !optional) {
        throw new Error(`Critical component ${componentName} failed to initialize`);
      }

    } catch (error) {
      const errorMsg = `${componentName} initialization failed: ${error.message}`;
      this.status.errors.push(errorMsg);
      this.status.components[componentName] = false;

      this.emitEvent({
        type: 'component_failed',
        component: componentName,
        message: errorMsg,
        timestamp: new Date(),
        error: error.message
      });

      if (enableLogging) {
        console.error(`❌ ${errorMsg}`);
      }

      if (!optional) {
        throw error; // Re-throw for critical components
      }
    }
  }

  /**
   * Check if core system components are ready
   */
  private isSystemReady(): boolean {
    // Core required components
    const coreComponents = ['websocket', 'eventBus', 'digitalTwinAPI', 'channelManager'];
    return coreComponents.every(component =>
      this.status.components[component as keyof RealTimeSystemStatus['components']]
    );
  }

  /**
   * Get current system status
   */
  public getStatus(): RealTimeSystemStatus {
    return { ...this.status };
  }

  /**
   * Check if system is ready
   */
  public isReady(): boolean {
    return this.status.initialized;
  }

  /**
   * Get initialization errors
   */
  public getErrors(): string[] {
    return [...this.status.errors];
  }

  /**
   * Add event listener
   */
  public addEventListener(listener: SystemEventListener): () => void {
    this.eventListeners.push(listener);

    // Return unsubscribe function
    return () => {
      const index = this.eventListeners.indexOf(listener);
      if (index >= 0) {
        this.eventListeners.splice(index, 1);
      }
    };
  }

  /**
   * Emit system event
   */
  private emitEvent(event: SystemEvent): void {
    this.eventListeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in system event listener:', error);
      }
    });
  }

  /**
   * Shutdown the real-time system
   */
  public async shutdown(): Promise<void> {
    console.log('🛑 Shutting down real-time system...');

    try {
      // Cleanup WebSocket connections
      cleanupWebSocket();

      // Reset status
      this.status = {
        initialized: false,
        initializationTime: 0,
        components: {
          websocket: false,
          eventBus: false,
          crmLifecycle: false,
          digitalTwinAPI: false,
          channelManager: false
        },
        errors: []
      };

      // Clear event listeners
      this.eventListeners = [];

      console.log('✅ Real-time system shutdown completed');

    } catch (error) {
      console.error('🚨 Error during system shutdown:', error);
    }
  }

  /**
   * Restart the real-time system
   */
  public async restart(options?: {
    runValidation?: boolean;
    enableLogging?: boolean;
    skipOptionalComponents?: boolean;
  }): Promise<RealTimeSystemStatus> {
    await this.shutdown();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    return await this.initialize(options);
  }

  /**
   * Get system health summary
   */
  public getHealthSummary(): {
    status: 'healthy' | 'degraded' | 'unhealthy';
    readyComponents: number;
    totalComponents: number;
    errors: number;
    uptime: number;
  } {
    const components = Object.values(this.status.components);
    const readyComponents = components.filter(Boolean).length;
    const totalComponents = components.length;
    const errors = this.status.errors.length;

    let status: 'healthy' | 'degraded' | 'unhealthy';
    if (readyComponents === totalComponents && errors === 0) {
      status = 'healthy';
    } else if (readyComponents >= totalComponents * 0.7) {
      status = 'degraded';
    } else {
      status = 'unhealthy';
    }

    return {
      status,
      readyComponents,
      totalComponents,
      errors,
      uptime: this.status.initialized ? Date.now() - this.startTime : 0
    };
  }
}

// Global system initializer instance
let systemInitializer: RealTimeSystemInitializer | null = null;

/**
 * Get the global system initializer instance
 */
export function getSystemInitializer(): RealTimeSystemInitializer {
  if (!systemInitializer) {
    systemInitializer = new RealTimeSystemInitializer();
  }
  return systemInitializer;
}

/**
 * Initialize the complete real-time system
 */
export async function initializeRealTimeSystem(options?: {
  runValidation?: boolean;
  enableLogging?: boolean;
  skipOptionalComponents?: boolean;
}): Promise<RealTimeSystemStatus> {
  const initializer = getSystemInitializer();
  return await initializer.initialize(options);
}

/**
 * Quick system health check
 */
export function getSystemHealth(): {
  status: 'healthy' | 'degraded' | 'unhealthy';
  readyComponents: number;
  totalComponents: number;
  errors: number;
  uptime: number;
} {
  const initializer = getSystemInitializer();
  return initializer.getHealthSummary();
}

/**
 * Shutdown the real-time system
 */
export async function shutdownRealTimeSystem(): Promise<void> {
  const initializer = getSystemInitializer();
  await initializer.shutdown();
}

export default RealTimeSystemInitializer;