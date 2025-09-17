# Digital Office Integration Guide

## Огляд

Digital Office підтримує інтеграцію з популярними календарями та системами управління завданнями через Model Context Protocol (MCP). Це дозволяє агентам автоматично створювати події, завдання та нагадування.

## Підтримувані інтеграції

### Календарі
- **Google Calendar** - повна інтеграція через Google API
- **Outlook Calendar** - через Microsoft Graph API
- **Apple Calendar** - через CalDAV
- **CalDAV** - універсальний протокол для різних календарів

### Системи управління завданнями
- **Asana** - повна інтеграція з проектами та завданнями
- **Notion** - робота з базами даних та сторінками
- **Jira** - створення та управління задачами
- **Todoist** - простий менеджер завдань
- **GitHub Issues** - інтеграція з розробкою

### Комунікації
- **Slack** - відправка повідомлень та сповіщень
- **Email** - автоматичні email-повідомлення

## Швидкий старт

### Крок 1: Увімкнення інтеграцій для агента

```typescript
// При створенні агента
const agentConfig: AgentConfig = {
  enabled: true,
  name: 'MySmartAgent',
  enableIntegrations: true, // Увімкнути інтеграції
  integrationConfig: {
    calendar: {
      provider: 'google',
      defaultCalendar: 'primary'
    },
    taskManagement: {
      provider: 'asana',
      defaultProject: 'My Project',
      defaultAssignee: 'team@company.com'
    }
  }
};
```

### Крок 2: Використання в агенті

```typescript
export class MySmartAgent extends BaseAgent {
  async executeAutonomously(): Promise<void> {
    // Створити подію в календарі
    await this.scheduleCalendarEvent({
      title: 'Огляд результатів аналізу',
      description: 'Автоматично згенеровано агентом',
      startTime: new Date('2024-01-20T14:00:00'),
      endTime: new Date('2024-01-20T15:00:00'),
      attendees: ['team@company.com'],
      reminders: [15, 60] // 15 хв та 1 година
    });

    // Створити завдання в Asana
    await this.createAsanaTask({
      name: 'Підготувати звіт за результатами',
      notes: 'На основі аналізу від ' + new Date().toLocaleDateString(),
      dueDate: new Date('2024-01-25'),
      priority: 'high',
      tags: ['автоматизація', 'звіти']
    });

    // Або використати універсальний метод
    await this.createTask(
      'Перевірити результати',
      'Необхідно перевірити автоматично згенеровані дані',
      'medium',
      new Date('2024-01-22')
    );
  }
}
```

## Налаштування зовнішніх MCP сервісів

### Google Calendar

1. Встановіть MCP сервіс:
```bash
npm install -g @modelcontextprotocol/server-google-calendar
```

2. Отримайте credentials:
- Перейдіть на [Google Cloud Console](https://console.cloud.google.com/)
- Створіть новий проект або виберіть існуючий
- Увімкніть Google Calendar API
- Створіть OAuth 2.0 credentials
- Завантажте credentials.json

3. Додайте в Claude Desktop config:
```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-calendar"],
      "env": {
        "GOOGLE_CALENDAR_CLIENT_ID": "your-client-id",
        "GOOGLE_CALENDAR_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Asana

1. Встановіть MCP сервіс:
```bash
npm install -g @modelcontextprotocol/server-asana
```

2. Отримайте Personal Access Token:
- Перейдіть в [Asana Developer Console](https://app.asana.com/0/my-apps)
- Створіть Personal Access Token
- Збережіть токен

3. Додайте в Claude Desktop config:
```json
{
  "mcpServers": {
    "asana": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-asana"],
      "env": {
        "ASANA_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

### Notion

1. Встановіть MCP сервіс:
```bash
npm install -g @modelcontextprotocol/server-notion
```

2. Налаштуйте інтеграцію:
- Перейдіть на [Notion Integrations](https://www.notion.so/my-integrations)
- Створіть нову інтеграцію
- Отримайте API key
- Надайте доступ інтеграції до потрібних сторінок

3. Додайте в Claude Desktop config:
```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": {
        "NOTION_API_KEY": "your-api-key"
      }
    }
  }
}
```

## API для агентів

### Календар

```typescript
// Створити подію
await this.scheduleCalendarEvent({
  title: string,
  description?: string,
  startTime: Date | string,
  endTime?: Date | string,
  location?: string,
  attendees?: string[],
  reminders?: number[], // хвилини до події
  recurrence?: 'daily' | 'weekly' | 'monthly' | 'yearly',
  timezone?: string
});

// Запланувати зустріч
await this.scheduleMeeting(
  title: string,
  participants: string[],
  duration: number, // хвилини
  description?: string
);

// Створити кілька подій
await this.scheduleMultipleEvents(events: CalendarEvent[]);
```

### Завдання

```typescript
// Універсальний метод
await this.createTask(
  title: string,
  description: string,
  priority: 'low' | 'medium' | 'high' | 'urgent',
  dueDate?: Date
);

// Asana
await this.createAsanaTask({
  name: string,
  notes?: string,
  dueDate?: Date | string,
  assignee?: string,
  project?: string,
  tags?: string[],
  priority?: 'low' | 'medium' | 'high' | 'urgent'
});

// Notion
await this.createNotionTask({
  title: string,
  content?: string,
  status?: 'To Do' | 'In Progress' | 'Done',
  dueDate?: Date | string,
  tags?: string[],
  database?: string
});

// Jira
await this.createJiraIssue({
  summary: string,
  description?: string,
  issueType: 'Task' | 'Bug' | 'Story' | 'Epic',
  project: string,
  priority?: 'Lowest' | 'Low' | 'Medium' | 'High' | 'Highest',
  labels?: string[]
});

// Todoist
await this.createTodoistTask({
  content: string,
  description?: string,
  dueDate?: string,
  priority?: 1 | 2 | 3 | 4, // 1=normal, 4=urgent
  labels?: string[]
});
```

### Допоміжні методи

```typescript
// Запланувати оглядову зустріч
await this.scheduleReviewMeeting(
  topic: string,
  participants?: string[]
);

// Створити follow-up завдання
await this.createFollowUpTask(
  originalTask: string,
  followUpAction: string,
  daysTillDue: number
);

// Перевірити статус інтеграцій
const status = await this.getIntegrationStatus();
```

## Локальне сховище

Якщо зовнішні MCP сервіси недоступні, система автоматично зберігає всі події та завдання локально в папці `data/integrations/`. Коли з'єднання відновиться, дані можуть бути синхронізовані.

### Структура локального сховища

```
data/integrations/
├── calendar/          # Події календаря
│   └── event_*.json
├── tasks/             # Завдання
│   └── {provider}_*.json
├── logs/              # Журнал активності
│   └── YYYY-MM-DD.json
├── config.json        # Конфігурація
└── pending_*.json     # Черга на синхронізацію
```

## Приклади використання

### Приклад 1: Агент планувальник

```typescript
export class PlannerAgent extends BaseAgent {
  async planWeeklyTasks(projects: Project[]): Promise<void> {
    const tasks = [];

    for (const project of projects) {
      // Створити завдання для кожного проекту
      tasks.push({
        name: `Weekly review: ${project.name}`,
        notes: `Review progress and plan next steps`,
        dueDate: this.getNextMonday(),
        priority: project.priority as any,
        project: project.name
      });
    }

    // Створити всі завдання одночасно
    await this.createMultipleTasks(tasks, 'asana');

    // Запланувати зустріч для огляду
    await this.scheduleMeeting(
      'Weekly Planning Session',
      ['team@company.com'],
      60,
      'Review all project tasks for the week'
    );
  }

  private getNextMonday(): Date {
    const d = new Date();
    d.setDate(d.getDate() + (1 + 7 - d.getDay()) % 7);
    return d;
  }
}
```

### Приклад 2: Агент звітності

```typescript
export class ReportingAgent extends BaseAgent {
  async generateAndScheduleReport(data: any): Promise<void> {
    // Генеруємо звіт
    const report = await this.analyzeData(data);

    // Створюємо завдання для review
    await this.createTask(
      'Review automated report',
      `Report generated on ${new Date().toLocaleDateString()}\n\n${report.summary}`,
      report.critical ? 'urgent' : 'medium'
    );

    // Якщо є критичні проблеми - плануємо терміновий дзвінок
    if (report.critical) {
      await this.scheduleCalendarEvent({
        title: '🚨 URGENT: Critical issues found',
        description: report.details,
        startTime: new Date(Date.now() + 3600000), // через годину
        attendees: ['manager@company.com', 'team@company.com'],
        reminders: [5, 15]
      });
    }
  }
}
```

### Приклад 3: Агент моніторингу

```typescript
export class MonitoringAgent extends BaseAgent {
  async checkSystemHealth(): Promise<void> {
    const health = await this.performHealthCheck();

    if (!health.allGreen) {
      // Створити Jira ticket для проблеми
      await this.createJiraIssue({
        summary: `System health issue: ${health.issue}`,
        description: health.details,
        issueType: 'Bug',
        project: 'INFRA',
        priority: health.severity === 'critical' ? 'Highest' : 'High',
        labels: ['monitoring', 'automated']
      });

      // Відправити повідомлення в Slack (якщо підключено)
      // await this.sendSlackMessage('#alerts', health.summary);
    }

    // Записати в календар наступну перевірку
    await this.scheduleCalendarEvent({
      title: 'System Health Check',
      description: 'Automated health check',
      startTime: new Date(Date.now() + 86400000), // через 24 години
      recurrence: 'daily'
    });
  }
}
```

## Troubleshooting

### Проблема: Події не з'являються в календарі

1. Перевірте чи правильно налаштовано MCP сервіс в Claude Desktop
2. Перевірте логи в `data/integrations/logs/`
3. Переконайтеся що у вас є доступ до API календаря

### Проблема: Завдання створюються локально, але не в Asana

1. Перевірте валідність Access Token
2. Переконайтеся що проект існує в Asana
3. Перевірте права доступу токена

### Проблема: Помилка "Integration service not enabled"

Додайте `enableIntegrations: true` в конфігурацію агента:

```typescript
const config: AgentConfig = {
  enabled: true,
  enableIntegrations: true // <- Додати це
};
```

## Безпека

- **Ніколи** не зберігайте credentials в коді
- Використовуйте змінні середовища для токенів
- Регулярно ротуйте API ключі
- Обмежуйте scope доступу до мінімально необхідного
- Логуйте всі операції для аудиту

## Додаткові ресурси

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google Calendar API](https://developers.google.com/calendar)
- [Asana API](https://developers.asana.com/)
- [Notion API](https://developers.notion.com/)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Todoist API](https://developer.todoist.com/)

## Підтримка

Для питань та проблем створюйте issue на GitHub або звертайтеся до команди розробки.