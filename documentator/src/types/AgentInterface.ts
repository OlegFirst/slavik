import { ServiceStatus } from './ServiceInterface';

export interface AgentConfig {
  enabled: boolean;
  name?: string;
  priority?: number;
  maxRetries?: number;
  retryDelayMs?: number;
  timeoutMs?: number;
  metadata?: Record<string, any>;
  enableIntegrations?: boolean;
  integrationConfig?: {
    calendar?: {
      provider?: 'google' | 'outlook' | 'apple' | 'caldav';
      defaultCalendar?: string;
    };
    taskManagement?: {
      provider?: 'asana' | 'todoist' | 'notion' | 'jira' | 'trello';
      defaultProject?: string;
      defaultAssignee?: string;
    };
  };
}

export enum ScheduleType {
  INTERVAL = 'interval',
  CRON = 'cron',
  ONCE = 'once',
  EVENT_DRIVEN = 'event_driven'
}

export interface ScheduleConfig {
  type: ScheduleType;
  enabled: boolean;
  intervalMs?: number; // Для INTERVAL
  cronExpression?: string; // Для CRON
  delayMs?: number; // Для ONCE
  events?: string[]; // Для EVENT_DRIVEN
  stopOnError?: boolean;
  maxExecutions?: number;
}

export interface AgentStatus extends ServiceStatus {
  isRunning: boolean;
  lastExecution?: Date;
  nextExecution?: Date;
  executionCount: number;
  recentErrors: string[];
  schedule: ScheduleConfig;
  config: AgentConfig;
}

export interface AgentExecutionResult {
  success: boolean;
  executionTime: number;
  result?: any;
  error?: string;
  logs?: string[];
}

export interface AutonomousAgent {
  getScheduleConfig(): ScheduleConfig;
  executeAutonomously(): Promise<void>;
  startAutonomousExecution(): Promise<void>;
  stopAutonomousExecution(): Promise<void>;
  isAutonomousRunning(): boolean;
  getAgentStatus(): AgentStatus;
}

export interface AgentEventPayload {
  agentName: string;
  eventType: 'execution_start' | 'execution_success' | 'execution_error' | 'status_change';
  timestamp: Date;
  data?: any;
  error?: string;
}

export interface AgentEvent {
  id: string;
  payload: AgentEventPayload;
}

export interface AgentHealthCheck {
  agentName: string;
  healthy: boolean;
  lastCheck: Date;
  details?: {
    memoryUsage?: number;
    cpuUsage?: number;
    diskSpace?: number;
    customMetrics?: Record<string, any>;
  };
}