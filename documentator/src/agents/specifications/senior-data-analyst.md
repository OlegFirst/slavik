# Senior Data Analyst Agent

## Роль та Відповідальності

**Senior Data Analyst Agent** - автономний агент для аналізу даних, генерації звітів та надання інсайтів на основі зібраної інформації.

## Основний функціонал

### 1. **Аналіз даних проектів**
- Аналіз структури проектів та кодової бази
- Метрики якості коду (складність, покриття тестами, технічний борг)
- Статистика коммітів, розробників, активності
- Аналіз залежностей та архітектури

### 2. **Моніторинг та звітність**
- Генерація щоденних/тижневих звітів
- KPI дашборди та метрики
- Тренди розробки та продуктивності
- Аналіз проблем та вузьких місць

### 3. **Інтеграція з зовнішніми джерелами**
- GitHub/GitLab статистика
- CI/CD метрики
- Логи застосунків
- Метрики продуктивності

### 4. **Прогнозування та рекомендації**
- Прогнозування термінів виконання задач
- Рекомендації по оптимізації процесів
- Ідентифікація ризиків проектів
- Планування ресурсів

## Технічні можливості

### Аналіз коду
- Статичний аналіз якості коду
- Виявлення code smells та антипатернів
- Аналіз покриття тестами
- Метрики складності (cyclomatic, cognitive)

### Робота з даними
- Парсинг логів та метрик
- Агрегація та кореляція даних
- Статистичний аналіз
- Візуалізація результатів

### Звітність
- Автоматичні звіти у форматі JSON/CSV/HTML
- Інтерактивні дашборди
- Email нотифікації
- Інтеграція з Slack/Teams

## MCP Команди

### `data-analyst:analyze_project`
Аналізує вказаний проект та генерує звіт

**Параметри:**
```json
{
  "projectPath": "./path/to/project",
  "analysisType": "full|quick|custom",
  "outputFormat": "json|html|csv"
}
```

### `data-analyst:generate_report`
Генерує звіт на основі зібраних даних

**Параметри:**
```json
{
  "reportType": "daily|weekly|monthly|custom",
  "includeSections": ["metrics", "trends", "recommendations"],
  "recipients": ["email@example.com"]
}
```

### `data-analyst:get_metrics`
Повертає поточні метрики проектів

**Параметри:**
```json
{
  "projects": ["project1", "project2"],
  "timeRange": "1d|7d|30d|custom",
  "metrics": ["commits", "quality", "coverage"]
}
```

### `data-analyst:predict_timeline`
Прогнозує терміни виконання на основі історичних даних

**Параметри:**
```json
{
  "projectName": "project-name",
  "remainingTasks": 50,
  "confidence": "low|medium|high"
}
```

## Події EventBus

### Публікує
- `analysis.completed` - Аналіз завершено
- `report.generated` - Звіт створено
- `metrics.updated` - Метрики оновлено
- `alert.threshold` - Перевищено поріг метрики

### Слухає
- `project.updated` - Оновлення проекту
- `git.commit` - Новий коміт
- `ci.build` - Результат збірки
- `qa.test` - Результати тестування

## Структура даних

### Аналітичні дані зберігаються в:
```
data/analytics/
├── projects/
│   ├── project-name/
│   │   ├── metrics.json     # Поточні метрики
│   │   ├── history.json     # Історія змін
│   │   └── analysis/        # Детальні аналізи
├── reports/
│   ├── daily/              # Щоденні звіти
│   ├── weekly/             # Тижневі звіти
│   └── custom/             # Користувацькі звіти
└── dashboards/             # Дані для дашбордів
```

## Конфігурація

```json
{
  "analysisInterval": 360,      // Інтервал аналізу (хвилини)
  "reportSchedule": {
    "daily": "08:00",
    "weekly": "monday:09:00"
  },
  "thresholds": {
    "codeQuality": 70,
    "testCoverage": 80,
    "techDebt": 30
  },
  "integrations": {
    "github": {
      "enabled": true,
      "token": "${GITHUB_TOKEN}"
    },
    "slack": {
      "enabled": true,
      "webhook": "${SLACK_WEBHOOK}"
    }
  }
}
```

## Інтеграція з іншими агентами

- **QA Engineer** - отримує метрики тестів
- **DevOps Engineer** - аналізує метрики деплоїв
- **Project Manager** - надає прогнози та звіти
- **WebScraper** - використовує зібрані дані

## Приклади використання

### Щоденний аналіз проекту
```bash
# Через Claude
data-analyst:analyze_project {
  "projectPath": "./projects/my-app",
  "analysisType": "daily",
  "outputFormat": "html"
}
```

### Генерація тижневого звіту
```bash
data-analyst:generate_report {
  "reportType": "weekly",
  "includeSections": ["metrics", "trends", "recommendations"]
}
```

### Прогнозування релізу
```bash
data-analyst:predict_timeline {
  "projectName": "my-app",
  "remainingTasks": 25,
  "confidence": "high"
}
```