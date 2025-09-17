import { BaseService } from './BaseService';
import { AgentConfig, ScheduleConfig, AgentStatus } from '../types/AgentInterface';
import { EventBus } from './EventBus';
import { DataStore } from './DataStore';
import { ResourceManager } from './ResourceManager';
import {
  IntegrationService,
  CalendarEvent,
  AsanaTask,
  NotionTask,
  JiraIssue,
  TodoistTask
} from '../services/integration/IntegrationService';

export abstract class BaseAgent extends BaseService {
  protected agentConfig: AgentConfig;
  protected eventBus: EventBus;
  protected dataStore: DataStore;
  protected resourceManager: ResourceManager;
  protected agentName: string;
  protected integrationService?: IntegrationService;

  private isRunning: boolean = false;
  private lastExecution?: Date;
  private nextExecution?: Date;
  private executionCount: number = 0;
  private errors: string[] = [];

  constructor(config: AgentConfig) {
    super();
    this.agentConfig = config;
    this.eventBus = EventBus.getInstance();
    this.dataStore = DataStore.getInstance();
    this.resourceManager = ResourceManager.getInstance();
    this.agentName = config.name || 'BaseAgent';

    // Ініціалізуємо сервіс інтеграції якщо потрібно
    if (config.enableIntegrations) {
      this.integrationService = new IntegrationService();
    }
  }

  public abstract getScheduleConfig(): ScheduleConfig;

  protected abstract executeAutonomously(): Promise<void>;

  async startAutonomousExecution(): Promise<void> {
    if (this.isRunning) {
      console.log(`Агент ${this.agentName} вже запущено`);
      return;
    }

    if (!this.agentConfig.enabled) {
      console.log(`Агент ${this.agentName} відключено`);
      return;
    }

    this.isRunning = true;
    console.log(`Агент ${this.agentName} запущено в автономному режимі`);
  }

  async stopAutonomousExecution(): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;
    console.log(`Агент ${this.agentName} зупинено`);
  }

  async executeOnce(): Promise<void> {
    if (!(this as any).initialized) {
      throw new Error(`Агент ${this.agentName} не ініціалізовано`);
    }

    try {
      this.lastExecution = new Date();

      // Публікуємо подію про початок виконання
      await this.eventBus.publish('agent.execution.start', this.agentName, {
        executionCount: this.executionCount + 1,
        timestamp: this.lastExecution
      });

      // Виконуємо основну логіку агента
      await this.executeAutonomously();

      this.executionCount++;

      // Зберігаємо статистику виконання
      await this.dataStore.create(`agent_executions_${this.agentName}`, {
        executionNumber: this.executionCount,
        startTime: this.lastExecution,
        endTime: new Date(),
        success: true
      });

      // Публікуємо подію про успішне виконання
      await this.eventBus.publish('agent.execution.success', this.agentName, {
        executionCount: this.executionCount,
        duration: Date.now() - this.lastExecution.getTime()
      });

      console.log(`Агент ${this.agentName} виконано успішно (виконання #${this.executionCount})`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
      this.errors.push(`${new Date().toISOString()}: ${errorMessage}`);

      // Зберігаємо інформацію про помилку
      await this.dataStore.create(`agent_errors_${this.agentName}`, {
        executionCount: this.executionCount,
        error: errorMessage,
        timestamp: new Date()
      });

      // Публікуємо подію про помилку
      await this.eventBus.publish('agent.execution.error', this.agentName, {
        error: errorMessage,
        executionCount: this.executionCount
      });

      console.error(`Помилка виконання агента ${this.agentName}:`, error);
      throw error;
    }
  }

  getAgentStatus(): AgentStatus {
    return {
      ...this.getStatus(),
      isRunning: this.isRunning,
      lastExecution: this.lastExecution,
      nextExecution: this.nextExecution,
      executionCount: this.executionCount,
      recentErrors: this.errors.slice(-5),
      schedule: this.getScheduleConfig(),
      config: this.agentConfig
    };
  }

  updateNextExecution(nextExecution: Date): void {
    this.nextExecution = nextExecution;
  }

  isAutonomousRunning(): boolean {
    return this.isRunning;
  }

  clearErrors(): void {
    this.errors = [];
  }

  updateConfig(newConfig: Partial<AgentConfig>): void {
    this.agentConfig = { ...this.agentConfig, ...newConfig };
  }

  protected log(message: string, level: 'info' | 'warn' | 'error' = 'info'): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${this.agentName}] ${message}`;

    switch (level) {
      case 'error':
        console.error(logMessage);
        break;
      case 'warn':
        console.warn(logMessage);
        break;
      default:
        console.log(logMessage);
    }
  }

  // Допоміжні методи для роботи з інфраструктурою
  protected async emit(event: string, data: any): Promise<void> {
    await this.eventBus.publish(event, this.agentName, data);
  }

  protected async on(event: string, handler: (data: any) => void | Promise<void>): Promise<string> {
    return this.eventBus.subscribe(event, async (payload) => {
      await handler(payload.data);
    });
  }

  protected async saveData(key: string, data: any): Promise<void> {
    await this.dataStore.set(`agent_${this.agentName}`, key, data);
  }

  protected async loadData(key: string): Promise<any> {
    return await this.dataStore.get(`agent_${this.agentName}`, key);
  }

  protected async queryData(filter: any, options?: any): Promise<any[]> {
    return await this.dataStore.query({
      collection: `agent_${this.agentName}`,
      filter,
      ...options
    });
  }

  protected async readFile(path: string): Promise<string | null> {
    return await this.resourceManager.readFile(path);
  }

  protected async writeFile(path: string, content: string): Promise<boolean> {
    return await this.resourceManager.writeFile(path, content);
  }

  protected async getSystemResources(): Promise<any> {
    return await this.resourceManager.getSystemResources();
  }

  protected async fetchApi(apiName: string, endpoint: string, options?: RequestInit): Promise<any> {
    return await this.resourceManager.fetchApiResource(apiName, endpoint, options);
  }

  protected async executeCommand(command: string): Promise<{ stdout: string; stderr: string }> {
    return await this.resourceManager.executeCommand(command);
  }

  protected getService(serviceName: string): any {
    return this.resourceManager.getService(serviceName);
  }

  // Data persistence methods
  protected async persistentStore(key: string, data: any): Promise<void> {
    return await this.saveData(key, data);
  }

  protected async persistentLoad(key: string): Promise<any> {
    return await this.loadData(key);
  }

  // Integration methods
  protected async scheduleCalendarEvent(event: CalendarEvent): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled. Set enableIntegrations: true in agent config');
    }
    return await this.integrationService.createCalendarEvent(event);
  }

  protected async scheduleMeeting(
    title: string,
    participants: string[],
    duration: number = 60,
    description?: string
  ): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.scheduleAgentMeeting(title, participants, duration, description);
  }

  protected async createTask(
    title: string,
    description: string,
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'medium',
    dueDate?: Date
  ): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createAgentTask(title, description, priority, dueDate);
  }

  protected async createAsanaTask(task: AsanaTask): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createAsanaTask(task);
  }

  protected async createNotionTask(task: NotionTask): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createNotionTask(task);
  }

  protected async createJiraIssue(issue: JiraIssue): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createJiraIssue(issue);
  }

  protected async createTodoistTask(task: TodoistTask): Promise<any> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createTodoistTask(task);
  }

  protected async getIntegrationStatus(): Promise<any> {
    if (!this.integrationService) {
      return { enabled: false };
    }
    return await this.integrationService.getIntegrationStatus();
  }

  // Batch operations
  protected async scheduleMultipleEvents(events: CalendarEvent[]): Promise<any[]> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createMultipleEvents(events);
  }

  protected async createMultipleTasks(
    tasks: Array<AsanaTask | NotionTask | JiraIssue | TodoistTask>,
    provider: 'asana' | 'notion' | 'jira' | 'todoist'
  ): Promise<any[]> {
    if (!this.integrationService) {
      throw new Error('Integration service not enabled');
    }
    return await this.integrationService.createMultipleTasks(tasks, provider);
  }

  // Helper method for agents to schedule their own review meetings
  protected async scheduleReviewMeeting(topic: string, participants?: string[]): Promise<any> {
    const defaultParticipants = participants || ['team@company.com'];
    return await this.scheduleMeeting(
      `Agent Review: ${topic}`,
      defaultParticipants,
      30,
      `Автоматичний огляд від агента ${this.agentName}: ${topic}`
    );
  }

  // Helper method to create follow-up tasks
  protected async createFollowUpTask(
    originalTask: string,
    followUpAction: string,
    daysTillDue: number = 7
  ): Promise<any> {
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + daysTillDue);

    return await this.createTask(
      `Follow-up: ${originalTask}`,
      `Необхідно виконати: ${followUpAction}\n\nПов'язано з: ${originalTask}`,
      'medium',
      dueDate
    );
  }
}