import { BaseService } from '../../core/BaseService';
import { ServiceMetadata } from '../../types/ServiceInterface';
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import * as fs from 'fs-extra';
import * as path from 'path';

export interface CalendarEvent {
  title: string;
  description?: string;
  startTime: Date | string;
  endTime?: Date | string;
  location?: string;
  attendees?: string[];
  reminders?: number[]; // минуты до события
  recurrence?: 'daily' | 'weekly' | 'monthly' | 'yearly';
  timezone?: string;
}

export interface AsanaTask {
  name: string;
  notes?: string;
  dueDate?: Date | string;
  assignee?: string;
  project?: string;
  section?: string;
  tags?: string[];
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  followers?: string[];
  customFields?: Record<string, any>;
}

export interface TodoistTask {
  content: string;
  description?: string;
  due?: {
    date: string;
    datetime?: string;
    timezone?: string;
  };
  priority?: 1 | 2 | 3 | 4; // 1 = normal, 4 = urgent
  project?: string;
  labels?: string[];
  sectionId?: string;
}

export interface NotionTask {
  title: string;
  content?: string;
  status?: 'To Do' | 'In Progress' | 'Done';
  dueDate?: Date | string;
  assignee?: string;
  tags?: string[];
  priority?: 'Low' | 'Medium' | 'High';
  database?: string;
  properties?: Record<string, any>;
}

export interface JiraIssue {
  summary: string;
  description?: string;
  issueType: 'Task' | 'Bug' | 'Story' | 'Epic';
  project: string;
  assignee?: string;
  priority?: 'Lowest' | 'Low' | 'Medium' | 'High' | 'Highest';
  dueDate?: Date | string;
  labels?: string[];
  components?: string[];
  fixVersion?: string;
  epicLink?: string;
  storyPoints?: number;
}

export interface IntegrationConfig {
  calendar?: {
    provider: 'google' | 'outlook' | 'apple' | 'caldav';
    defaultCalendar?: string;
    defaultReminders?: number[];
  };
  taskManagement?: {
    provider: 'asana' | 'todoist' | 'notion' | 'jira' | 'trello';
    defaultProject?: string;
    defaultAssignee?: string;
  };
  notifications?: {
    enabled: boolean;
    channels?: ('email' | 'slack' | 'teams' | 'discord')[];
  };
}

export class IntegrationService extends BaseService {
  public metadata: ServiceMetadata = {
    name: 'integration',
    version: '1.0.0',
    description: 'Сервіс інтеграції з календарями та системами управління завданнями',
    author: 'Digital Office',
    category: 'integration',
    tags: ['calendar', 'tasks', 'asana', 'google', 'notion', 'jira'],
    status: 'active',
    dependencies: []
  };

  private config: IntegrationConfig;
  private eventsQueue: CalendarEvent[] = [];
  private tasksQueue: any[] = [];
  private dataPath: string;

  constructor(config?: IntegrationConfig) {
    super();
    this.config = config || this.loadDefaultConfig();
    this.dataPath = path.join(process.cwd(), 'data', 'integrations');
  }

  private loadDefaultConfig(): IntegrationConfig {
    return {
      calendar: {
        provider: 'google',
        defaultReminders: [15, 60] // 15 минут и 1 час
      },
      taskManagement: {
        provider: 'asana'
      },
      notifications: {
        enabled: true,
        channels: ['email']
      }
    };
  }

  protected async onInitialize(): Promise<void> {
    await fs.ensureDir(this.dataPath);
    await fs.ensureDir(path.join(this.dataPath, 'calendar'));
    await fs.ensureDir(path.join(this.dataPath, 'tasks'));
    await fs.ensureDir(path.join(this.dataPath, 'logs'));

    // Загружаем конфигурацию из файла если есть
    const configPath = path.join(this.dataPath, 'config.json');
    if (await fs.pathExists(configPath)) {
      const savedConfig = await fs.readJson(configPath);
      this.config = { ...this.config, ...savedConfig };
    } else {
      await fs.writeJson(configPath, this.config, { spaces: 2 });
    }
  }

  protected async onShutdown(): Promise<void> {
    // Сохраняем незавершенные задачи
    if (this.eventsQueue.length > 0) {
      await fs.writeJson(
        path.join(this.dataPath, 'pending_events.json'),
        this.eventsQueue,
        { spaces: 2 }
      );
    }

    if (this.tasksQueue.length > 0) {
      await fs.writeJson(
        path.join(this.dataPath, 'pending_tasks.json'),
        this.tasksQueue,
        { spaces: 2 }
      );
    }
  }

  protected async performHealthCheck(): Promise<boolean> {
    // Проверяем доступность конфигурации
    return this.config !== null;
  }

  public async handleToolCall(toolName: string, args: any): Promise<any> {
    switch (toolName) {
      case 'calendar_create_event':
        return await this.createCalendarEvent(args);
      case 'asana_create_task':
        return await this.createAsanaTask(args);
      case 'notion_create_task':
        return await this.createNotionTask(args);
      case 'jira_create_issue':
        return await this.createJiraIssue(args);
      case 'todoist_create_task':
        return await this.createTodoistTask(args);
      case 'integration_get_status':
        return await this.getIntegrationStatus();
      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  }

  public getTools(): Tool[] {
    return [
      {
        name: 'calendar_create_event',
        description: 'Створити подію в календарі',
        inputSchema: {
          type: 'object',
          properties: {
            title: { type: 'string', description: 'Назва події' },
            description: { type: 'string', description: 'Опис події' },
            startTime: { type: 'string', description: 'Час початку (ISO формат)' },
            endTime: { type: 'string', description: 'Час завершення (ISO формат)' },
            location: { type: 'string', description: 'Місце проведення' },
            attendees: {
              type: 'array',
              items: { type: 'string' },
              description: 'Email учасників'
            },
            reminders: {
              type: 'array',
              items: { type: 'number' },
              description: 'Нагадування (хвилини до події)'
            }
          },
          required: ['title', 'startTime']
        }
      },
      {
        name: 'asana_create_task',
        description: 'Створити завдання в Asana',
        inputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string', description: 'Назва завдання' },
            notes: { type: 'string', description: 'Опис завдання' },
            dueDate: { type: 'string', description: 'Термін виконання' },
            project: { type: 'string', description: 'ID або назва проекту' },
            assignee: { type: 'string', description: 'Email виконавця' },
            priority: {
              type: 'string',
              enum: ['low', 'medium', 'high', 'urgent'],
              description: 'Пріоритет'
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Теги'
            }
          },
          required: ['name']
        }
      },
      {
        name: 'notion_create_task',
        description: 'Створити завдання в Notion',
        inputSchema: {
          type: 'object',
          properties: {
            title: { type: 'string', description: 'Назва завдання' },
            content: { type: 'string', description: 'Опис завдання' },
            status: {
              type: 'string',
              enum: ['To Do', 'In Progress', 'Done'],
              description: 'Статус'
            },
            dueDate: { type: 'string', description: 'Термін виконання' },
            priority: {
              type: 'string',
              enum: ['Low', 'Medium', 'High'],
              description: 'Пріоритет'
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Теги'
            },
            database: { type: 'string', description: 'ID бази даних Notion' }
          },
          required: ['title']
        }
      },
      {
        name: 'jira_create_issue',
        description: 'Створити задачу в Jira',
        inputSchema: {
          type: 'object',
          properties: {
            summary: { type: 'string', description: 'Короткий опис' },
            description: { type: 'string', description: 'Детальний опис' },
            issueType: {
              type: 'string',
              enum: ['Task', 'Bug', 'Story', 'Epic'],
              description: 'Тип задачі'
            },
            project: { type: 'string', description: 'Ключ проекту' },
            assignee: { type: 'string', description: 'Username виконавця' },
            priority: {
              type: 'string',
              enum: ['Lowest', 'Low', 'Medium', 'High', 'Highest'],
              description: 'Пріоритет'
            },
            dueDate: { type: 'string', description: 'Термін виконання' },
            labels: {
              type: 'array',
              items: { type: 'string' },
              description: 'Мітки'
            },
            storyPoints: { type: 'number', description: 'Story points' }
          },
          required: ['summary', 'project', 'issueType']
        }
      },
      {
        name: 'todoist_create_task',
        description: 'Створити завдання в Todoist',
        inputSchema: {
          type: 'object',
          properties: {
            content: { type: 'string', description: 'Текст завдання' },
            description: { type: 'string', description: 'Опис' },
            dueDate: { type: 'string', description: 'Дата виконання' },
            priority: {
              type: 'number',
              minimum: 1,
              maximum: 4,
              description: 'Пріоритет (1-4, де 4 найвищий)'
            },
            project: { type: 'string', description: 'Назва проекту' },
            labels: {
              type: 'array',
              items: { type: 'string' },
              description: 'Мітки'
            }
          },
          required: ['content']
        }
      },
      {
        name: 'integration_get_status',
        description: 'Отримати статус інтеграцій',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ];
  }

  // Календар
  public async createCalendarEvent(event: CalendarEvent): Promise<any> {
    try {
      // Нормалізуємо дані події
      const normalizedEvent = {
        ...event,
        startTime: new Date(event.startTime),
        endTime: event.endTime ? new Date(event.endTime) : this.calculateEndTime(new Date(event.startTime)),
        reminders: event.reminders || this.config.calendar?.defaultReminders || [15],
        timezone: event.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone
      };

      // Додаємо в чергу
      this.eventsQueue.push(normalizedEvent);

      // Зберігаємо локально
      const eventId = `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const eventPath = path.join(this.dataPath, 'calendar', `${eventId}.json`);
      await fs.writeJson(eventPath, normalizedEvent, { spaces: 2 });

      // Логування
      await this.logActivity('calendar_event_created', normalizedEvent);

      // Якщо є зовнішній MCP календар, відправляємо туди
      if (this.isExternalMCPAvailable('calendar')) {
        return await this.sendToExternalMCP('calendar', 'create_event', normalizedEvent);
      }

      return {
        success: true,
        eventId,
        message: `Подія "${event.title}" створена локально`,
        data: normalizedEvent
      };
    } catch (error) {
      console.error('Помилка створення події:', error);
      throw error;
    }
  }

  // Asana
  public async createAsanaTask(task: AsanaTask): Promise<any> {
    try {
      const normalizedTask = {
        ...task,
        project: task.project || this.config.taskManagement?.defaultProject,
        assignee: task.assignee || this.config.taskManagement?.defaultAssignee,
        createdAt: new Date()
      };

      this.tasksQueue.push({ type: 'asana', data: normalizedTask });

      const taskId = `asana_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const taskPath = path.join(this.dataPath, 'tasks', `${taskId}.json`);
      await fs.writeJson(taskPath, normalizedTask, { spaces: 2 });

      await this.logActivity('asana_task_created', normalizedTask);

      if (this.isExternalMCPAvailable('asana')) {
        return await this.sendToExternalMCP('asana', 'create_task', normalizedTask);
      }

      return {
        success: true,
        taskId,
        message: `Завдання "${task.name}" створено локально`,
        data: normalizedTask
      };
    } catch (error) {
      console.error('Помилка створення Asana завдання:', error);
      throw error;
    }
  }

  // Notion
  public async createNotionTask(task: NotionTask): Promise<any> {
    try {
      const normalizedTask = {
        ...task,
        status: task.status || 'To Do',
        createdAt: new Date()
      };

      this.tasksQueue.push({ type: 'notion', data: normalizedTask });

      const taskId = `notion_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const taskPath = path.join(this.dataPath, 'tasks', `${taskId}.json`);
      await fs.writeJson(taskPath, normalizedTask, { spaces: 2 });

      await this.logActivity('notion_task_created', normalizedTask);

      if (this.isExternalMCPAvailable('notion')) {
        return await this.sendToExternalMCP('notion', 'create_task', normalizedTask);
      }

      return {
        success: true,
        taskId,
        message: `Завдання "${task.title}" створено локально`,
        data: normalizedTask
      };
    } catch (error) {
      console.error('Помилка створення Notion завдання:', error);
      throw error;
    }
  }

  // Jira
  public async createJiraIssue(issue: JiraIssue): Promise<any> {
    try {
      const normalizedIssue = {
        ...issue,
        priority: issue.priority || 'Medium',
        createdAt: new Date()
      };

      this.tasksQueue.push({ type: 'jira', data: normalizedIssue });

      const issueId = `jira_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const issuePath = path.join(this.dataPath, 'tasks', `${issueId}.json`);
      await fs.writeJson(issuePath, normalizedIssue, { spaces: 2 });

      await this.logActivity('jira_issue_created', normalizedIssue);

      if (this.isExternalMCPAvailable('jira')) {
        return await this.sendToExternalMCP('jira', 'create_issue', normalizedIssue);
      }

      return {
        success: true,
        issueId,
        message: `Задача "${issue.summary}" створена локально`,
        data: normalizedIssue
      };
    } catch (error) {
      console.error('Помилка створення Jira задачі:', error);
      throw error;
    }
  }

  // Todoist
  public async createTodoistTask(task: TodoistTask): Promise<any> {
    try {
      const normalizedTask = {
        ...task,
        priority: task.priority || 1,
        createdAt: new Date()
      };

      this.tasksQueue.push({ type: 'todoist', data: normalizedTask });

      const taskId = `todoist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const taskPath = path.join(this.dataPath, 'tasks', `${taskId}.json`);
      await fs.writeJson(taskPath, normalizedTask, { spaces: 2 });

      await this.logActivity('todoist_task_created', normalizedTask);

      if (this.isExternalMCPAvailable('todoist')) {
        return await this.sendToExternalMCP('todoist', 'create_task', normalizedTask);
      }

      return {
        success: true,
        taskId,
        message: `Завдання "${task.content}" створено локально`,
        data: normalizedTask
      };
    } catch (error) {
      console.error('Помилка створення Todoist завдання:', error);
      throw error;
    }
  }

  // Отримання статусу
  public async getIntegrationStatus(): Promise<any> {
    const status = {
      calendar: {
        provider: this.config.calendar?.provider,
        pendingEvents: this.eventsQueue.length,
        connected: this.isExternalMCPAvailable('calendar')
      },
      taskManagement: {
        provider: this.config.taskManagement?.provider,
        pendingTasks: this.tasksQueue.length,
        connected: this.isExternalMCPAvailable(this.config.taskManagement?.provider || 'asana')
      },
      localStorage: {
        eventsStored: await this.countStoredItems('calendar'),
        tasksStored: await this.countStoredItems('tasks')
      }
    };

    return status;
  }

  // Допоміжні методи
  private calculateEndTime(startTime: Date): Date {
    const endTime = new Date(startTime);
    endTime.setHours(endTime.getHours() + 1); // За замовчуванням 1 година
    return endTime;
  }

  private isExternalMCPAvailable(service: string): boolean {
    // Перевіряємо чи є зовнішній MCP сервіс для інтеграції
    // В реальності тут буде перевірка доступності зовнішнього MCP
    return false; // Поки що завжди false
  }

  private async sendToExternalMCP(service: string, action: string, data: any): Promise<any> {
    // Тут буде відправка до зовнішнього MCP сервісу
    console.log(`Would send to MCP ${service}: ${action}`, data);
    return { success: true, external: true };
  }

  private async logActivity(action: string, data: any): Promise<void> {
    const logEntry = {
      timestamp: new Date(),
      action,
      data
    };

    const logPath = path.join(
      this.dataPath,
      'logs',
      `${new Date().toISOString().split('T')[0]}.json`
    );

    let logs = [];
    if (await fs.pathExists(logPath)) {
      logs = await fs.readJson(logPath);
    }

    logs.push(logEntry);
    await fs.writeJson(logPath, logs, { spaces: 2 });
  }

  private async countStoredItems(type: 'calendar' | 'tasks'): Promise<number> {
    const dir = path.join(this.dataPath, type);
    if (await fs.pathExists(dir)) {
      const files = await fs.readdir(dir);
      return files.filter(f => f.endsWith('.json')).length;
    }
    return 0;
  }

  // Batch операції
  public async createMultipleEvents(events: CalendarEvent[]): Promise<any[]> {
    const results = [];
    for (const event of events) {
      results.push(await this.createCalendarEvent(event));
    }
    return results;
  }

  public async createMultipleTasks(tasks: Array<AsanaTask | NotionTask | JiraIssue | TodoistTask>, provider: string): Promise<any[]> {
    const results = [];
    for (const task of tasks) {
      switch (provider) {
        case 'asana':
          results.push(await this.createAsanaTask(task as AsanaTask));
          break;
        case 'notion':
          results.push(await this.createNotionTask(task as NotionTask));
          break;
        case 'jira':
          results.push(await this.createJiraIssue(task as JiraIssue));
          break;
        case 'todoist':
          results.push(await this.createTodoistTask(task as TodoistTask));
          break;
      }
    }
    return results;
  }

  // Методи для агентів
  public async scheduleAgentMeeting(
    title: string,
    participants: string[],
    duration: number = 60,
    description?: string
  ): Promise<any> {
    const startTime = this.findNextAvailableSlot(duration);
    const endTime = new Date(startTime.getTime() + duration * 60000);

    return this.createCalendarEvent({
      title: `[Agent Meeting] ${title}`,
      description: description || 'Автоматично заплановано агентом',
      startTime,
      endTime,
      attendees: participants,
      reminders: [15, 60]
    });
  }

  public async createAgentTask(
    title: string,
    description: string,
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'medium',
    dueDate?: Date
  ): Promise<any> {
    const provider = this.config.taskManagement?.provider || 'asana';

    switch (provider) {
      case 'asana':
        return this.createAsanaTask({
          name: `[Agent] ${title}`,
          notes: description,
          priority,
          dueDate: dueDate || this.getDefaultDueDate()
        });

      case 'notion':
        return this.createNotionTask({
          title: `[Agent] ${title}`,
          content: description,
          priority: priority === 'urgent' ? 'High' : priority === 'high' ? 'High' : 'Medium',
          dueDate: dueDate || this.getDefaultDueDate()
        });

      case 'jira':
        return this.createJiraIssue({
          summary: `[Agent] ${title}`,
          description,
          issueType: 'Task',
          project: this.config.taskManagement?.defaultProject || 'DEFAULT',
          priority: this.mapPriorityToJira(priority),
          dueDate: dueDate || this.getDefaultDueDate()
        });

      default:
        return this.createAsanaTask({
          name: `[Agent] ${title}`,
          notes: description,
          priority,
          dueDate: dueDate || this.getDefaultDueDate()
        });
    }
  }

  private findNextAvailableSlot(duration: number): Date {
    // Знаходимо наступний доступний слот в календарі
    const now = new Date();
    const slot = new Date(now);

    // Округлюємо до наступної години
    slot.setHours(slot.getHours() + 1, 0, 0, 0);

    // Перевіряємо робочі години (9:00 - 18:00)
    if (slot.getHours() < 9) {
      slot.setHours(9, 0, 0, 0);
    } else if (slot.getHours() >= 18) {
      slot.setDate(slot.getDate() + 1);
      slot.setHours(9, 0, 0, 0);
    }

    // Пропускаємо вихідні
    while (slot.getDay() === 0 || slot.getDay() === 6) {
      slot.setDate(slot.getDate() + 1);
    }

    return slot;
  }

  private getDefaultDueDate(): Date {
    const date = new Date();
    date.setDate(date.getDate() + 7); // За замовчуванням через тиждень
    return date;
  }

  private mapPriorityToJira(priority: 'low' | 'medium' | 'high' | 'urgent'): 'Lowest' | 'Low' | 'Medium' | 'High' | 'Highest' {
    switch (priority) {
      case 'urgent': return 'Highest';
      case 'high': return 'High';
      case 'medium': return 'Medium';
      case 'low': return 'Low';
      default: return 'Medium';
    }
  }
}