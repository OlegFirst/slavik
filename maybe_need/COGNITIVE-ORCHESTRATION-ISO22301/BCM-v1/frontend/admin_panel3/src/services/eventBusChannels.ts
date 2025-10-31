/**
 * EventBus Channel Manager for Multi-Channel Event Routing
 *
 * This service manages all EventBus channels, provides event type definitions,
 * and handles cross-service event routing for the Digital Twin system.
 *
 * Features:
 * - Define all Digital Twin event channels
 * - Channel subscription management
 * - Event type definitions and handlers
 * - Cross-service event routing
 * - Message priority and queuing
 * - Channel health monitoring
 */

import type {
  PersonalTwinEvent,
  DataCollectionEvent,
  PackageManagementEvent,
  SystemHealthEvent,
  UserActivityEvent,
  ServiceCommunicationEvent,
  DigitalTwinEvent
} from './eventBusService';

// Channel Categories
export const CHANNEL_CATEGORIES = {
  DIGITAL_TWIN: 'digital_twin',
  SYSTEM: 'system',
  USER: 'user',
  SERVICE: 'service',
  BCM: 'bcm',
  AI: 'ai',
  GLOBAL: 'global'
} as const;

// Complete Channel Registry with Descriptions and Metadata
export const CHANNEL_REGISTRY = {
  // ===== Digital Twin Channels =====
  'digital_twin.personal': {
    category: CHANNEL_CATEGORIES.DIGITAL_TWIN,
    description: 'Personal Digital Twin lifecycle events',
    priority: 'high',
    retention: '7d',
    eventTypes: [
      'personal_twin.created',
      'personal_twin.updated',
      'personal_twin.deleted',
      'personal_twin.synced',
      'personal_twin.analyzed',
      'personal_twin.privacy_updated'
    ],
    subscribers: ['admin_panel', 'bcm_core', 'bcm_portal', 'ai_orchestrator']
  },

  'digital_twin.organizational': {
    category: CHANNEL_CATEGORIES.DIGITAL_TWIN,
    description: 'Organizational Digital Twin events',
    priority: 'high',
    retention: '30d',
    eventTypes: [
      'org_twin.created',
      'org_twin.updated',
      'org_twin.health_changed',
      'org_twin.compliance_status'
    ],
    subscribers: ['admin_panel', 'bcm_core', 'bcm_governance', 'bcm_reporting']
  },

  'digital_twin.data_collection': {
    category: CHANNEL_CATEGORIES.DIGITAL_TWIN,
    description: 'Data collection service events',
    priority: 'medium',
    retention: '3d',
    eventTypes: [
      'data_collection.started',
      'data_collection.stopped',
      'data_collection.error',
      'data_collection.completed',
      'data_collection.metrics_updated'
    ],
    subscribers: ['admin_panel', 'bcm_core', 'data_collector', 'monitoring']
  },

  'digital_twin.packages': {
    category: CHANNEL_CATEGORIES.DIGITAL_TWIN,
    description: 'Twin data package management events',
    priority: 'medium',
    retention: '14d',
    eventTypes: [
      'package.created',
      'package.updated',
      'package.deleted',
      'package.uploaded',
      'package.downloaded',
      'package.verified',
      'package.archived'
    ],
    subscribers: ['admin_panel', 'package_manager', 'bcm_portal', 'storage']
  },

  // ===== System Channels =====
  'system.health': {
    category: CHANNEL_CATEGORIES.SYSTEM,
    description: 'System health and monitoring events',
    priority: 'critical',
    retention: '30d',
    eventTypes: [
      'system.health_changed',
      'system.service_status',
      'system.performance_alert',
      'system.resource_warning'
    ],
    subscribers: ['admin_panel', 'monitoring', 'alerting', 'all_services']
  },

  'system.alerts': {
    category: CHANNEL_CATEGORIES.SYSTEM,
    description: 'Critical system alerts and notifications',
    priority: 'critical',
    retention: '90d',
    eventTypes: [
      'system.alert',
      'system.error',
      'system.warning',
      'system.critical_failure'
    ],
    subscribers: ['admin_panel', 'alerting', 'notification', 'ops_team']
  },

  'system.performance': {
    category: CHANNEL_CATEGORIES.SYSTEM,
    description: 'System performance metrics and trends',
    priority: 'low',
    retention: '7d',
    eventTypes: [
      'system.performance',
      'system.metrics_update',
      'system.load_alert',
      'system.capacity_warning'
    ],
    subscribers: ['admin_panel', 'monitoring', 'analytics', 'capacity_planning']
  },

  // ===== User & CRM Channels =====
  'crm.users': {
    category: CHANNEL_CATEGORIES.USER,
    description: 'User lifecycle management through CRM',
    priority: 'high',
    retention: '365d',
    eventTypes: [
      'user.created',
      'user.updated',
      'user.deleted',
      'user.activated',
      'user.deactivated',
      'user.role_changed'
    ],
    subscribers: ['admin_panel', 'bcm_core', 'bcm_portal', 'auth_service']
  },

  'crm.activity': {
    category: CHANNEL_CATEGORIES.USER,
    description: 'User activity tracking and analytics',
    priority: 'medium',
    retention: '30d',
    eventTypes: [
      'user.login',
      'user.logout',
      'user.activity',
      'user.interaction',
      'user.session_timeout'
    ],
    subscribers: ['admin_panel', 'analytics', 'security', 'digital_twin']
  },

  'crm.sessions': {
    category: CHANNEL_CATEGORIES.USER,
    description: 'User session management and tracking',
    priority: 'medium',
    retention: '7d',
    eventTypes: [
      'session.started',
      'session.ended',
      'session.expired',
      'session.renewed'
    ],
    subscribers: ['admin_panel', 'auth_service', 'security', 'analytics']
  },

  // ===== Service Communication Channels =====
  'services.mesh': {
    category: CHANNEL_CATEGORIES.SERVICE,
    description: 'Inter-service communication and requests',
    priority: 'high',
    retention: '3d',
    eventTypes: [
      'service.request',
      'service.response',
      'service.error',
      'service.timeout'
    ],
    subscribers: ['all_services', 'service_mesh', 'monitoring']
  },

  'services.discovery': {
    category: CHANNEL_CATEGORIES.SERVICE,
    description: 'Service discovery and registration',
    priority: 'high',
    retention: '7d',
    eventTypes: [
      'service.registered',
      'service.deregistered',
      'service.health_check',
      'service.updated'
    ],
    subscribers: ['service_registry', 'load_balancer', 'monitoring']
  },

  'services.monitoring': {
    category: CHANNEL_CATEGORIES.SERVICE,
    description: 'Service health and performance monitoring',
    priority: 'medium',
    retention: '14d',
    eventTypes: [
      'service.health_update',
      'service.performance_metrics',
      'service.warning',
      'service.recovery'
    ],
    subscribers: ['monitoring', 'alerting', 'admin_panel', 'ops_team']
  },

  // ===== BCM Module Channels =====
  'bcm.core': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'BCM Core module events and operations',
    priority: 'high',
    retention: '30d',
    eventTypes: [
      'bcm.plan_updated',
      'bcm.incident_created',
      'bcm.process_changed',
      'bcm.workflow_completed'
    ],
    subscribers: ['admin_panel', 'bcm_modules', 'reporting', 'compliance']
  },

  'bcm.compliance': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'Compliance monitoring and audit events',
    priority: 'critical',
    retention: '2555d', // 7 years for compliance
    eventTypes: [
      'compliance.check_completed',
      'compliance.violation_detected',
      'compliance.audit_started',
      'compliance.report_generated'
    ],
    subscribers: ['admin_panel', 'bcm_governance', 'bcm_audit', 'reporting']
  },

  'bcm.risk': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'Risk management and assessment events',
    priority: 'high',
    retention: '365d',
    eventTypes: [
      'risk.assessment_completed',
      'risk.level_changed',
      'risk.mitigation_applied',
      'risk.alert_triggered'
    ],
    subscribers: ['admin_panel', 'bcm_risk', 'bcm_governance', 'alerting']
  },

  'bcm.governance': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'Governance and policy management events',
    priority: 'high',
    retention: '365d',
    eventTypes: [
      'governance.policy_updated',
      'governance.approval_required',
      'governance.workflow_started',
      'governance.compliance_checked'
    ],
    subscribers: ['admin_panel', 'bcm_governance', 'bcm_compliance', 'workflow']
  },

  'bcm.audit': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'Audit trail and logging events',
    priority: 'critical',
    retention: '2555d', // 7 years for audit
    eventTypes: [
      'audit.action_logged',
      'audit.trail_created',
      'audit.report_generated',
      'audit.anomaly_detected'
    ],
    subscribers: ['admin_panel', 'bcm_audit', 'compliance', 'security']
  },

  'bcm.bia': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'Business Impact Analysis events',
    priority: 'high',
    retention: '365d',
    eventTypes: [
      'bia.analysis_completed',
      'bia.dependency_updated',
      'bia.impact_calculated',
      'bia.critical_process_identified'
    ],
    subscribers: ['admin_panel', 'bcm_bia', 'bcm_risk', 'reporting']
  },

  'bcm.incident': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'Incident management and response events',
    priority: 'critical',
    retention: '365d',
    eventTypes: [
      'incident.created',
      'incident.updated',
      'incident.resolved',
      'incident.escalated',
      'incident.response_activated'
    ],
    subscribers: ['admin_panel', 'bcm_incident', 'alerting', 'response_team']
  },

  'bcm.reporting': {
    category: CHANNEL_CATEGORIES.BCM,
    description: 'BCM reporting and analytics events',
    priority: 'medium',
    retention: '365d',
    eventTypes: [
      'report.generated',
      'report.scheduled',
      'analytics.completed',
      'dashboard.updated'
    ],
    subscribers: ['admin_panel', 'bcm_reporting', 'analytics', 'executives']
  },

  // ===== AI Services Channels =====
  'ai.orchestrator': {
    category: CHANNEL_CATEGORIES.AI,
    description: 'AI Orchestrator coordination events',
    priority: 'high',
    retention: '14d',
    eventTypes: [
      'ai.analysis_started',
      'ai.analysis_completed',
      'ai.model_updated',
      'ai.prediction_generated'
    ],
    subscribers: ['admin_panel', 'ai_services', 'digital_twin', 'analytics']
  },

  'ai.insights': {
    category: CHANNEL_CATEGORIES.AI,
    description: 'AI-generated insights and recommendations',
    priority: 'medium',
    retention: '30d',
    eventTypes: [
      'ai.insight_generated',
      'ai.recommendation_created',
      'ai.pattern_detected',
      'ai.anomaly_found'
    ],
    subscribers: ['admin_panel', 'decision_support', 'reporting', 'users']
  },

  'ai.analysis': {
    category: CHANNEL_CATEGORIES.AI,
    description: 'AI analysis and processing events',
    priority: 'medium',
    retention: '7d',
    eventTypes: [
      'ai.analysis_queued',
      'ai.processing_started',
      'ai.processing_completed',
      'ai.error_occurred'
    ],
    subscribers: ['admin_panel', 'ai_services', 'monitoring', 'digital_twin']
  },

  // ===== Global Channels =====
  'global.notifications': {
    category: CHANNEL_CATEGORIES.GLOBAL,
    description: 'System-wide notifications and broadcasts',
    priority: 'medium',
    retention: '30d',
    eventTypes: [
      'notification.broadcast',
      'notification.user_specific',
      'notification.system_message',
      'notification.alert'
    ],
    subscribers: ['all_users', 'notification_service', 'admin_panel']
  },

  'global.announcements': {
    category: CHANNEL_CATEGORIES.GLOBAL,
    description: 'System announcements and maintenance notices',
    priority: 'high',
    retention: '90d',
    eventTypes: [
      'announcement.created',
      'maintenance.scheduled',
      'maintenance.started',
      'maintenance.completed',
      'system.upgrade_available'
    ],
    subscribers: ['all_users', 'admin_panel', 'ops_team']
  }
} as const;

// Channel Management Types
export interface ChannelInfo {
  category: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  retention: string;
  eventTypes: string[];
  subscribers: string[];
}

export interface ChannelMetrics {
  messageCount: number;
  subscriberCount: number;
  avgMessageSize: number;
  lastActivity: Date;
  errorRate: number;
}

export interface ChannelHealth {
  status: 'healthy' | 'warning' | 'error';
  latency: number;
  throughput: number;
  errorCount: number;
  lastCheck: Date;
}

// Channel Manager Class
class EventBusChannelManager {
  private channelMetrics = new Map<string, ChannelMetrics>();
  private channelHealth = new Map<string, ChannelHealth>();
  private activeSubscriptions = new Map<string, Set<string>>();

  /**
   * Get all available channels
   */
  public getAllChannels(): Record<string, ChannelInfo> {
    return CHANNEL_REGISTRY;
  }

  /**
   * Get channels by category
   */
  public getChannelsByCategory(category: string): Record<string, ChannelInfo> {
    const channels: Record<string, ChannelInfo> = {};

    Object.entries(CHANNEL_REGISTRY).forEach(([channel, info]) => {
      if (info.category === category) {
        channels[channel] = info;
      }
    });

    return channels;
  }

  /**
   * Get channels by priority
   */
  public getChannelsByPriority(priority: string): Record<string, ChannelInfo> {
    const channels: Record<string, ChannelInfo> = {};

    Object.entries(CHANNEL_REGISTRY).forEach(([channel, info]) => {
      if (info.priority === priority) {
        channels[channel] = info;
      }
    });

    return channels;
  }

  /**
   * Validate if channel exists
   */
  public isValidChannel(channel: string): boolean {
    return channel in CHANNEL_REGISTRY;
  }

  /**
   * Get channel information
   */
  public getChannelInfo(channel: string): ChannelInfo | null {
    return CHANNEL_REGISTRY[channel as keyof typeof CHANNEL_REGISTRY] || null;
  }

  /**
   * Get event types for channel
   */
  public getEventTypesForChannel(channel: string): string[] {
    const info = this.getChannelInfo(channel);
    return info?.eventTypes || [];
  }

  /**
   * Validate event type for channel
   */
  public isValidEventType(channel: string, eventType: string): boolean {
    const eventTypes = this.getEventTypesForChannel(channel);
    return eventTypes.includes(eventType);
  }

  /**
   * Get subscribers for channel
   */
  public getChannelSubscribers(channel: string): string[] {
    const info = this.getChannelInfo(channel);
    return info?.subscribers || [];
  }

  /**
   * Update channel metrics
   */
  public updateChannelMetrics(channel: string, metrics: Partial<ChannelMetrics>): void {
    const current = this.channelMetrics.get(channel) || {
      messageCount: 0,
      subscriberCount: 0,
      avgMessageSize: 0,
      lastActivity: new Date(),
      errorRate: 0
    };

    this.channelMetrics.set(channel, { ...current, ...metrics });
  }

  /**
   * Get channel metrics
   */
  public getChannelMetrics(channel: string): ChannelMetrics | null {
    return this.channelMetrics.get(channel) || null;
  }

  /**
   * Update channel health
   */
  public updateChannelHealth(channel: string, health: Partial<ChannelHealth>): void {
    const current = this.channelHealth.get(channel) || {
      status: 'healthy' as const,
      latency: 0,
      throughput: 0,
      errorCount: 0,
      lastCheck: new Date()
    };

    this.channelHealth.set(channel, { ...current, ...health });
  }

  /**
   * Get channel health
   */
  public getChannelHealth(channel: string): ChannelHealth | null {
    return this.channelHealth.get(channel) || null;
  }

  /**
   * Get all channels health overview
   */
  public getHealthOverview(): Record<string, ChannelHealth> {
    const overview: Record<string, ChannelHealth> = {};

    this.channelHealth.forEach((health, channel) => {
      overview[channel] = health;
    });

    return overview;
  }

  /**
   * Add active subscription
   */
  public addSubscription(channel: string, subscriber: string): void {
    if (!this.activeSubscriptions.has(channel)) {
      this.activeSubscriptions.set(channel, new Set());
    }
    this.activeSubscriptions.get(channel)!.add(subscriber);
  }

  /**
   * Remove active subscription
   */
  public removeSubscription(channel: string, subscriber: string): void {
    const subscribers = this.activeSubscriptions.get(channel);
    if (subscribers) {
      subscribers.delete(subscriber);
      if (subscribers.size === 0) {
        this.activeSubscriptions.delete(channel);
      }
    }
  }

  /**
   * Get active subscriptions for channel
   */
  public getActiveSubscriptions(channel: string): string[] {
    return Array.from(this.activeSubscriptions.get(channel) || []);
  }

  /**
   * Get channels with critical status
   */
  public getCriticalChannels(): string[] {
    const critical: string[] = [];

    this.channelHealth.forEach((health, channel) => {
      if (health.status === 'error' || health.errorCount > 10) {
        critical.push(channel);
      }
    });

    return critical;
  }

  /**
   * Get high-priority channels
   */
  public getHighPriorityChannels(): string[] {
    return Object.entries(CHANNEL_REGISTRY)
      .filter(([_, info]) => info.priority === 'critical' || info.priority === 'high')
      .map(([channel, _]) => channel);
  }

  /**
   * Generate channel routing rules
   */
  public generateRoutingRules(): Record<string, string[]> {
    const rules: Record<string, string[]> = {};

    Object.entries(CHANNEL_REGISTRY).forEach(([channel, info]) => {
      rules[channel] = info.subscribers;
    });

    return rules;
  }
}

// Global channel manager instance
let channelManager: EventBusChannelManager | null = null;

/**
 * Get the global channel manager instance
 */
export function getChannelManager(): EventBusChannelManager {
  if (!channelManager) {
    channelManager = new EventBusChannelManager();
  }
  return channelManager;
}

/**
 * Helper function to get channel for event type
 */
export function getChannelForEventType(eventType: string): string | null {
  for (const [channel, info] of Object.entries(CHANNEL_REGISTRY)) {
    if (info.eventTypes.includes(eventType)) {
      return channel;
    }
  }
  return null;
}

/**
 * Helper function to route event to appropriate channels
 */
export function routeEvent(event: DigitalTwinEvent): string[] {
  const channels: string[] = [];

  // Find primary channel for event type
  const primaryChannel = getChannelForEventType(event.type);
  if (primaryChannel) {
    channels.push(primaryChannel);
  }

  // Add global channels for important events
  if (event.type.includes('error') || event.type.includes('alert')) {
    channels.push('system.alerts');
  }

  // Add service mesh for inter-service communication
  if (event.source && event.target) {
    channels.push('services.mesh');
  }

  return [...new Set(channels)]; // Remove duplicates
}

export default EventBusChannelManager;