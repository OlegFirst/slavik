# Senior Project Manager Agent

## Роль та Відповідальності

**Senior Project Manager Agent** - автономний агент для управління проектами, планування, трекінгу прогресу та координації між командами.

## Основний функціонал

### 1. **Планування та управління задачами**
- Створення та оновлення project roadmap
- Розбиття епіків на задачі та підзадачі
- Планування спринтів та releases
- Управління backlog'ом

### 2. **Трекінг прогресу та звітність**
- Моніторинг виконання задач
- Burndown charts та velocity tracking
- Статус репорти для стейкхолдерів
- Risk assessment та мітігація

### 3. **Координація команди**
- Планування зустрічей та standups
- Розподіл ресурсів та навантаження
- Конфлікт резолюшн
- Performance tracking

### 4. **Інтеграція з проектними інструментами**
- Jira/Azure DevOps синхронізація
- GitHub issues та milestones
- Calendar management
- Slack/Teams координація

## Технічні можливості

### Проектне планування
- Gantt charts генерація
- Critical path analysis
- Resource allocation optimization
- Timeline prediction

### Аналітика та звітність
- Velocity analysis
- Team performance metrics
- Budget tracking
- Stakeholder reporting

### Автоматизація процесів
- Automated task creation
- Status updates
- Notification management
- Meeting scheduling

## MCP Команди

### `project-manager:create_project`
Створює новий проект з планом

**Параметри:**
```json
{
  "projectName": "New Feature Development",
  "description": "Implementation of user authentication",
  "startDate": "2024-01-15",
  "estimatedDuration": "8 weeks",
  "team": ["dev1", "dev2", "qa1"],
  "priority": "high|medium|low"
}
```

### `project-manager:update_task_status`
Оновлює статус задачі

**Параметри:**
```json
{
  "taskId": "PROJ-123",
  "status": "todo|in_progress|review|done",
  "assignee": "developer1",
  "estimatedHours": 16,
  "actualHours": 12
}
```

### `project-manager:generate_report`
Генерує звіт по проекту

**Параметри:**
```json
{
  "projectId": "project-123",
  "reportType": "status|progress|velocity|budget",
  "timeRange": "sprint|month|quarter",
  "recipients": ["stakeholder@company.com"]
}
```

### `project-manager:plan_sprint`
Планує новий спринт

**Параметри:**
```json
{
  "sprintName": "Sprint 15",
  "startDate": "2024-01-15",
  "duration": "2 weeks",
  "capacity": 80,
  "tasks": ["PROJ-123", "PROJ-124"]
}
```

### `project-manager:assess_risks`
Оцінює ризики проекту

**Параметри:**
```json
{
  "projectId": "project-123",
  "riskCategories": ["technical", "resource", "timeline"],
  "includeRecommendations": true
}
```

### `project-manager:optimize_resources`
Оптимізує розподіл ресурсів

**Параметри:**
```json
{
  "timeframe": "next_sprint|next_month",
  "constraints": ["budget", "availability"],
  "priorities": ["critical_bugs", "new_features"]
}
```

## Події EventBus

### Публікує
- `project.created` - Новий проект створено
- `task.updated` - Задача оновлена
- `sprint.started` - Спринт розпочато
- `milestone.reached` - Досягнуто milestone
- `risk.identified` - Виявлено ризик
- `report.generated` - Звіт створено

### Слухає
- `git.commit` - Коміти по задачах
- `ci.build` - Статус збірок
- `qa.test.completed` - Результати тестування
- `deployment.completed` - Завершення деплою
- `team.availability` - Зміни в доступності команди

## Структура даних

### Проектні дані зберігаються в:
```
data/projects/
├── active/
│   ├── project-123/
│   │   ├── plan.json           # Проектний план
│   │   ├── tasks.json          # Задачі та статуси
│   │   ├── sprints/            # Інформація по спринтах
│   │   ├── reports/            # Згенеровані звіти
│   │   └── risks.json          # Ризики та мітігація
├── completed/                  # Завершені проекти
├── templates/                  # Шаблони проектів
└── analytics/
    ├── velocity.json           # Velocity метрики
    ├── team-performance.json   # Перформанс команди
    └── historical-data.json    # Історичні дані
```

## Конфігурація

```json
{
  "reportingInterval": 1440,        // Звіти (хвилини) - щодня
  "statusCheckInterval": 60,        // Перевірка статусу (хвилини)
  "defaultSprintDuration": 14,      // Тривалість спринту (дні)
  "workingHoursPerDay": 8,
  "integrations": {
    "jira": {
      "enabled": true,
      "url": "${JIRA_URL}",
      "token": "${JIRA_TOKEN}",
      "syncInterval": 30
    },
    "github": {
      "enabled": true,
      "token": "${GITHUB_TOKEN}",
      "repositories": ["repo1", "repo2"]
    },
    "slack": {
      "enabled": true,
      "webhook": "${SLACK_WEBHOOK}",
      "channel": "#project-updates"
    },
    "calendar": {
      "enabled": true,
      "provider": "google|outlook",
      "autoScheduleMeetings": true
    }
  },
  "notifications": {
    "dailyStandup": "09:00",
    "sprintReview": "friday:15:00",
    "weeklyReport": "friday:17:00"
  },
  "riskThresholds": {
    "budgetOverrun": 10,             // %
    "timelineDelay": 3,              // дні
    "velocityDrop": 20               // %
  }
}
```

## Типи проектів та шаблони

### 1. **Software Development Project**
```json
{
  "phases": ["planning", "development", "testing", "deployment"],
  "defaultTasks": [
    "requirements_analysis",
    "architecture_design",
    "implementation",
    "code_review",
    "testing",
    "deployment"
  ],
  "estimationMethod": "story_points"
}
```

### 2. **Bug Fix Project**
```json
{
  "phases": ["investigation", "fix", "testing", "deployment"],
  "priority": "high",
  "estimationMethod": "hours",
  "autoAssignQA": true
}
```

### 3. **Research Project**
```json
{
  "phases": ["research", "poc", "documentation", "presentation"],
  "deliverables": ["research_report", "prototype", "recommendations"],
  "estimationMethod": "time_based"
}
```

## Інтеграція з іншими агентами

- **Data Analyst** - отримує метрики та аналітику проектів
- **DevOps Engineer** - координує releases та деплої
- **QA Engineer** - планує тестування та отримує результати
- **Development Team** - розподіляє задачі та отримує статуси

## Алгоритми та автоматизація

### 1. **Smart Task Assignment**
```typescript
// Алгоритм розподілу задач на основі:
// - навичок розробника
// - поточного навантаження
// - пріоритету задачі
// - історичної продуктивності
```

### 2. **Risk Prediction**
```typescript
// Прогнозування ризиків на основі:
// - velocity trends
// - бюджетних трат
// - якості коду
// - доступності команди
```

### 3. **Timeline Optimization**
```typescript
// Оптимізація часових рамок:
// - critical path analysis
// - resource leveling
// - dependency management
```

## Приклади використання

### Створення нового проекту
```bash
project-manager:create_project {
  "projectName": "User Authentication System",
  "description": "Implement OAuth2 authentication",
  "startDate": "2024-01-15",
  "estimatedDuration": "6 weeks",
  "team": ["john.doe", "jane.smith", "alex.qa"],
  "priority": "high"
}
```

### Планування спринту
```bash
project-manager:plan_sprint {
  "sprintName": "Sprint 16 - Auth Implementation",
  "startDate": "2024-01-15",
  "duration": "2 weeks",
  "capacity": 120,
  "tasks": ["AUTH-001", "AUTH-002", "AUTH-003"]
}
```

### Генерація тижневого звіту
```bash
project-manager:generate_report {
  "projectId": "auth-project",
  "reportType": "progress",
  "timeRange": "sprint",
  "recipients": ["cto@company.com", "stakeholder@company.com"]
}
```

## Автоматичні сценарії

### 1. **Daily Standups**
- Збирає статуси задач
- Ідентифікує блокери
- Генерує agenda для standup
- Відправляє нагадування команді

### 2. **Sprint Planning**
- Аналізує velocity попереднього спринту
- Рекомендує задачі для наступного спринту
- Оптимізує навантаження команди
- Створює sprint backlog

### 3. **Risk Management**
- Постійно моніторить проектні метрики
- Виявляє потенційні ризики
- Генерує алерти для критичних ситуацій
- Пропонує мітігацію ризиків