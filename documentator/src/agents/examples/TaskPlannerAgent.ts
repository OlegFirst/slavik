import { BaseAgent } from '../../core/BaseAgent';
import { AgentConfig, ScheduleConfig, ScheduleType } from '../../types/AgentInterface';
import { ServiceMetadata } from '../../types/ServiceInterface';

/**
 * Приклад агента, який демонструє використання інтеграцій
 * з календарями та системами управління завданнями
 */
export class TaskPlannerAgent extends BaseAgent {
  public metadata: ServiceMetadata = {
    name: 'task-planner',
    version: '1.0.0',
    description: 'Агент для автоматичного планування завдань та подій',
    author: 'Digital Office',
    category: 'automation',
    tags: ['planning', 'calendar', 'tasks', 'automation'],
    status: 'active',
    dependencies: []
  };

  constructor() {
    const config: AgentConfig = {
      enabled: true,
      name: 'TaskPlannerAgent',
      enableIntegrations: true, // Важливо: увімкнути інтеграції
      integrationConfig: {
        calendar: {
          provider: 'google',
          defaultCalendar: 'primary'
        },
        taskManagement: {
          provider: 'asana',
          defaultProject: 'Digital Office Tasks'
        }
      }
    };
    super(config);
  }

  public getScheduleConfig(): ScheduleConfig {
    return {
      type: ScheduleType.CRON,
      enabled: true,
      cronExpression: '0 9 * * 1', // Щопонеділка о 9:00
      stopOnError: false
    };
  }

  protected async onInitialize(): Promise<void> {
    this.log('Task Planner Agent ініціалізовано');

    // Ініціалізуємо інтеграції якщо потрібно
    if (this.integrationService) {
      await this.integrationService.initialize();
      this.log('Інтеграції підключено');
    }
  }

  protected async onShutdown(): Promise<void> {
    this.log('Task Planner Agent зупиняється');

    if (this.integrationService) {
      await this.integrationService.shutdown();
    }
  }

  protected async performHealthCheck(): Promise<boolean> {
    // Перевіряємо статус інтеграцій
    if (this.integrationService) {
      const status = await this.getIntegrationStatus();
      return status.calendar.connected || status.taskManagement.connected;
    }
    return true;
  }

  protected async executeAutonomously(): Promise<void> {
    this.log('Початок планування тижневих завдань...');

    try {
      // Отримуємо дані для планування
      const weekPlan = await this.generateWeekPlan();

      // Створюємо завдання на тиждень
      await this.createWeeklyTasks(weekPlan.tasks);

      // Плануємо зустрічі
      await this.scheduleWeeklyMeetings(weekPlan.meetings);

      // Створюємо нагадування
      await this.createReminders(weekPlan.reminders);

      // Генеруємо звіт про заплановані активності
      await this.generatePlanningReport(weekPlan);

      this.log('Планування завершено успішно');
    } catch (error) {
      this.log(`Помилка планування: ${error}`, 'error');
      throw error;
    }
  }

  private async generateWeekPlan(): Promise<any> {
    // Тут може бути логіка аналізу попереднього тижня,
    // пріоритетів, deadline'ів тощо
    return {
      tasks: [
        {
          title: 'Code Review',
          description: 'Review pending pull requests',
          priority: 'high',
          dueDate: this.getNextDate(1) // Вівторок
        },
        {
          title: 'Update Documentation',
          description: 'Update API documentation and guides',
          priority: 'medium',
          dueDate: this.getNextDate(3) // Четвер
        },
        {
          title: 'Performance Optimization',
          description: 'Analyze and optimize slow queries',
          priority: 'medium',
          dueDate: this.getNextDate(5) // Субота
        }
      ],
      meetings: [
        {
          title: 'Weekly Team Sync',
          participants: ['team@company.com'],
          duration: 60,
          day: 1 // Вівторок
        },
        {
          title: 'Sprint Planning',
          participants: ['team@company.com', 'pm@company.com'],
          duration: 120,
          day: 3 // Четвер
        }
      ],
      reminders: [
        {
          title: 'Prepare weekly report',
          dayBefore: 5 // П'ятниця
        },
        {
          title: 'Review sprint goals',
          dayBefore: 0 // Понеділок
        }
      ]
    };
  }

  private async createWeeklyTasks(tasks: any[]): Promise<void> {
    this.log(`Створення ${tasks.length} завдань на тиждень...`);

    for (const task of tasks) {
      try {
        // Використовуємо універсальний метод
        const result = await this.createTask(
          task.title,
          task.description,
          task.priority,
          task.dueDate
        );

        this.log(`✅ Завдання створено: ${task.title}`);

        // Додатково можемо створити в конкретній системі
        if (this.agentConfig.integrationConfig?.taskManagement?.provider === 'asana') {
          await this.createAsanaTask({
            name: `[Auto] ${task.title}`,
            notes: task.description,
            dueDate: task.dueDate,
            priority: task.priority,
            tags: ['automated', 'weekly-planning']
          });
        }
      } catch (error) {
        this.log(`❌ Помилка створення завдання ${task.title}: ${error}`, 'error');
      }
    }
  }

  private async scheduleWeeklyMeetings(meetings: any[]): Promise<void> {
    this.log(`Планування ${meetings.length} зустрічей...`);

    for (const meeting of meetings) {
      try {
        const meetingDate = this.getNextDate(meeting.day);
        meetingDate.setHours(10, 0, 0, 0); // 10:00 AM

        const result = await this.scheduleMeeting(
          meeting.title,
          meeting.participants,
          meeting.duration,
          'Щотижнева зустріч, заплановано автоматично'
        );

        this.log(`📅 Зустріч заплановано: ${meeting.title}`);

        // Додатково створюємо подію в календарі з деталями
        await this.scheduleCalendarEvent({
          title: meeting.title,
          description: 'Автоматично заплановано Task Planner Agent',
          startTime: meetingDate,
          endTime: new Date(meetingDate.getTime() + meeting.duration * 60000),
          attendees: meeting.participants,
          reminders: [15, 60], // 15 хв та 1 година
          location: 'Conference Room / Zoom'
        });

        // Створюємо завдання для підготовки до зустрічі
        const prepDate = new Date(meetingDate);
        prepDate.setDate(prepDate.getDate() - 1);

        await this.createFollowUpTask(
          meeting.title,
          'Підготувати agenda та матеріали для зустрічі',
          1
        );
      } catch (error) {
        this.log(`❌ Помилка планування зустрічі ${meeting.title}: ${error}`, 'error');
      }
    }
  }

  private async createReminders(reminders: any[]): Promise<void> {
    this.log(`Створення ${reminders.length} нагадувань...`);

    for (const reminder of reminders) {
      try {
        const reminderDate = this.getNextDate(reminder.dayBefore);
        reminderDate.setHours(9, 0, 0, 0); // 9:00 AM

        await this.scheduleCalendarEvent({
          title: `⏰ Нагадування: ${reminder.title}`,
          description: 'Автоматичне нагадування від Task Planner',
          startTime: reminderDate,
          endTime: new Date(reminderDate.getTime() + 900000), // 15 хвилин
          reminders: [0, 15] // Одразу та за 15 хвилин
        });

        this.log(`⏰ Нагадування створено: ${reminder.title}`);
      } catch (error) {
        this.log(`❌ Помилка створення нагадування ${reminder.title}: ${error}`, 'error');
      }
    }
  }

  private async generatePlanningReport(weekPlan: any): Promise<void> {
    const report = {
      weekStarting: this.getNextMonday(),
      tasksCreated: weekPlan.tasks.length,
      meetingsScheduled: weekPlan.meetings.length,
      remindersSet: weekPlan.reminders.length,
      summary: `Заплановано ${weekPlan.tasks.length} завдань, ${weekPlan.meetings.length} зустрічей та ${weekPlan.reminders.length} нагадувань на наступний тиждень.`,
      details: {
        tasks: weekPlan.tasks.map((t: any) => ({
          title: t.title,
          priority: t.priority,
          due: t.dueDate.toLocaleDateString()
        })),
        meetings: weekPlan.meetings.map((m: any) => ({
          title: m.title,
          duration: `${m.duration} хв`,
          day: this.getDayName(m.day)
        }))
      }
    };

    // Зберігаємо звіт
    await this.saveData('weekly-plan-report', report);

    // Створюємо завдання для review плану
    await this.createTask(
      'Review Weekly Plan',
      `Переглянути автоматично створений план на тиждень:\n\n${report.summary}`,
      'low',
      this.getNextMonday()
    );

    // Публікуємо подію
    await this.emit('planning.completed', report);

    this.log('Звіт про планування згенеровано та збережено');
  }

  // Допоміжні методи
  private getNextMonday(): Date {
    const d = new Date();
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1) + 7;
    const monday = new Date(d.setDate(diff));
    monday.setHours(0, 0, 0, 0);
    return monday;
  }

  private getNextDate(daysFromMonday: number): Date {
    const monday = this.getNextMonday();
    const targetDate = new Date(monday);
    targetDate.setDate(targetDate.getDate() + daysFromMonday);
    return targetDate;
  }

  private getDayName(dayIndex: number): string {
    const days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця', 'Субота', 'Неділя'];
    return days[dayIndex] || days[0];
  }

  protected log(message: string, level: 'info' | 'error' | 'warn' = 'info'): void {
    const prefix = `[TaskPlanner]`;
    switch (level) {
      case 'error':
        console.error(`${prefix} ❌ ${message}`);
        break;
      case 'warn':
        console.warn(`${prefix} ⚠️ ${message}`);
        break;
      default:
        console.log(`${prefix} ${message}`);
    }
  }
}

// Експортуємо для використання
export default TaskPlannerAgent;