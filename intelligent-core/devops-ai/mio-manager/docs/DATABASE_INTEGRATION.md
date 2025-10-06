# 💾 Database Integration - MIO Manager

**Статус:** ✅ Полностью интегрировано

---

## 🎯 Что сделано

MIO Manager теперь **сохраняет все отчёты и действия** в SQLite базу данных для:
- Исторического анализа
- Трендов
- Отслеживания исправлений
- Метрик и статистики

---

## 📊 Структура базы данных

### База данных: `mio_manager.db` (SQLite)

**9 таблиц:**

| Таблица | Назначение | Ключевые поля |
|---------|-----------|---------------|
| `analysis_reports` | Все отчёты анализа | report_id, analysis_type, results, issues_found |
| `service_discoveries` | История service discovery | total_services, coverage_percentage, services_list |
| `security_scan_results` | Результаты Bandit сканов | high/medium/low_severity_count, all_issues |
| `code_complexity_results` | Анализ сложности кода | service_name, avg/max_complexity, high_complexity_functions |
| `dependency_analysis_results` | Анализ зависимостей | circular_dependencies, dependency_graph |
| `mio_actions` | Все действия MIO Manager | action_type, target_service, status, success |
| `task_delegations` | Задачи → Orchestrator | task_type, priority, orchestrator_response, assigned_to |
| `issue_tracking` | Отслеживание проблем | issue_type, severity, status (open/resolved) |
| `metrics_snapshots` | Snapshots метрик | service_coverage, high_security_issues, avg_complexity |

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│              AUTOMATION TOOLKIT MANAGER                  │
│         (integrations/automation_toolkit.py)             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  discover_services()        →  ReportsRepository        │
│  run_security_scan()        →  .save_service_discovery()│
│  analyze_dependencies()     →  .save_security_scan()    │
│  analyze_code_complexity()  →  .save_dependency_analysis│
│                                .save_complexity_analysis │
│                                                          │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                REPOSITORIES LAYER                        │
│            (repositories/*.py)                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ReportsRepository:                                      │
│  - save_service_discovery()                              │
│  - save_security_scan()                                  │
│  - save_complexity_analysis()                            │
│  - save_dependency_analysis()                            │
│  - get_latest_reports()                                  │
│                                                          │
│  ActionsRepository:                                      │
│  - create_action()                                       │
│  - update_action_status()                                │
│  - save_task_delegation()                                │
│  - create_issue()                                        │
│  - resolve_issue()                                       │
│  - save_metrics_snapshot()                               │
│                                                          │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│               DATABASE LAYER                             │
│              (database.py)                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  init_database()  - Create all tables                    │
│  get_db()        - Context manager for sessions          │
│  SessionLocal    - SQLAlchemy session factory            │
│                                                          │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                DATABASE MODELS                           │
│           (models/database.py)                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  SQLAlchemy ORM Models:                                  │
│  - AnalysisReport                                        │
│  - ServiceDiscovery                                      │
│  - SecurityScanResult                                    │
│  - CodeComplexityResult                                  │
│  - DependencyAnalysisResult                              │
│  - MIOAction                                             │
│  - TaskDelegation                                        │
│  - IssueTracking                                         │
│  - MetricsSnapshot                                       │
│                                                          │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
              mio_manager.db
              (SQLite database)
```

---

## 📁 Файлы

### 1. Database Layer

**`database.py`** (65 lines)
```python
# Инициализация базы данных
init_database()  # Создать все таблицы

# Context manager для сессий
with get_db() as db:
    db.add(record)
    # Автоматический commit/rollback
```

**`models/database.py`** (400+ lines)
- 9 SQLAlchemy ORM моделей
- 4 Enum типа (AnalysisType, ActionType, ActionStatus, IssueSeverity)
- JSON columns для гибких данных
- Indexes для быстрых запросов

### 2. Repository Layer

**`repositories/reports_repository.py`** (200+ lines)

Методы:
```python
# Сохранение
save_analysis_report(...)
save_service_discovery(...)
save_security_scan(...)
save_complexity_analysis(...)
save_dependency_analysis(...)

# Получение
get_latest_reports(analysis_type, limit)
get_security_trend(days)
```

**`repositories/actions_repository.py`** (220+ lines)

Методы:
```python
# Действия
create_action(action_type, target_service, ...)
update_action_status(action_id, status, ...)

# Делегирование
save_task_delegation(task_type, ...)
update_task_delegation(task_id, status, ...)

# Проблемы
create_issue(issue_type, severity, ...)
resolve_issue(issue_id, resolved_by_action_id)

# Метрики
save_metrics_snapshot(...)

# Статистика
get_pending_actions(limit)
get_open_issues(severity)
get_action_stats()
```

### 3. Integration

**`integrations/automation_toolkit.py`** (обновлено)

Каждый метод анализа теперь сохраняет результаты:

```python
async def discover_services():
    # ... анализ ...

    # Save to database
    ReportsRepository.save_service_discovery(
        total_services=total,
        monitored_services=monitored,
        ...
    )

async def run_security_scan():
    # ... сканирование ...

    # Save to database
    ReportsRepository.save_security_scan(
        high_count=len(high),
        ...
    )
```

---

## 🚀 Использование

### При запуске MIO Manager

```python
# main.py
from database import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    init_database()  # ✅ Создаёт все таблицы

    # ... остальная инициализация ...
```

### Автоматическое сохранение

Все scheduled jobs автоматически сохраняют данные:

```python
# scheduler/automation_jobs.py

# JOB 1: Service Discovery (каждые 5 мин)
@scheduler.scheduled_job(IntervalTrigger(minutes=5))
async def auto_discover_services():
    result = await toolkit_manager.discover_services()
    # ✅ Автоматически сохраняется в service_discoveries таблицу

# JOB 2: Security Scan (каждый час)
@scheduler.scheduled_job(IntervalTrigger(hours=1))
async def hourly_security_scan():
    result = await toolkit_manager.run_security_scan()
    # ✅ Автоматически сохраняется в security_scan_results таблицу
```

### Получение данных

```python
from repositories import ReportsRepository, ActionsRepository

# Последние отчёты
reports = ReportsRepository.get_latest_reports(
    analysis_type=AnalysisType.SECURITY_SCAN,
    limit=10
)

# Security тренд
trend = ReportsRepository.get_security_trend(days=7)

# Открытые проблемы
issues = ActionsRepository.get_open_issues(
    severity=IssueSeverity.HIGH
)

# Статистика действий
stats = ActionsRepository.get_action_stats()
# {
#   "total": 150,
#   "completed": 120,
#   "failed": 10,
#   "pending": 20,
#   "success_rate": 80.0
# }
```

---

## 📊 Примеры данных

### Service Discovery
```json
{
  "discovery_id": "uuid-123",
  "total_services": 12,
  "monitored_services": 12,
  "coverage_percentage": 100.0,
  "services_list": [
    {
      "name": "validation",
      "has_health": true,
      "has_metrics": true
    }
  ],
  "discovered_at": "2025-10-03T10:00:00"
}
```

### Security Scan
```json
{
  "scan_id": "uuid-456",
  "high_severity_count": 3,
  "medium_severity_count": 5,
  "low_severity_count": 2,
  "scan_status": "issues_found",
  "high_issues": [
    {
      "issue_text": "SQL injection risk",
      "filename": "service.py",
      "line_number": 42
    }
  ],
  "scanned_at": "2025-10-03T11:00:00"
}
```

### MIO Action
```json
{
  "action_id": "uuid-789",
  "action_type": "service_restart",
  "target_service": "validation",
  "status": "completed",
  "success": true,
  "started_at": "2025-10-03T12:00:00",
  "completed_at": "2025-10-03T12:00:30",
  "duration_seconds": 30.5
}
```

### Issue Tracking
```json
{
  "issue_id": "uuid-999",
  "issue_type": "security",
  "severity": "high",
  "description": "SQL injection vulnerability in validation service",
  "affected_service": "validation",
  "status": "open",
  "discovered_by_report_id": "uuid-456",
  "created_at": "2025-10-03T11:00:00"
}
```

---

## ✅ Что работает

| Компонент | Статус | Описание |
|-----------|--------|----------|
| **Database Init** | ✅ | Автоматическое создание таблиц при запуске |
| **Service Discovery** | ✅ | Сохранение результатов каждого скана |
| **Security Scan** | ✅ | История всех Bandit сканов |
| **Dependency Analysis** | ✅ | Граф зависимостей и циклы |
| **Complexity Analysis** | ✅ | Метрики сложности по сервисам |
| **Actions Tracking** | ✅ | Все действия MIO Manager |
| **Issue Tracking** | ✅ | Проблемы: открытые → в работе → решены |
| **Metrics Snapshots** | ✅ | Hourly snapshots для трендов |

---

## 🔍 Запросы для анализа

### 1. Service Coverage Trend
```sql
SELECT
    date(discovered_at) as date,
    AVG(coverage_percentage) as avg_coverage,
    MAX(total_services) as max_services
FROM service_discoveries
GROUP BY date(discovered_at)
ORDER BY date DESC
LIMIT 30;
```

### 2. Security Issues Trend
```sql
SELECT
    date(scanned_at) as date,
    SUM(high_severity_count) as high_issues,
    SUM(medium_severity_count) as medium_issues
FROM security_scan_results
GROUP BY date(scanned_at)
ORDER BY date DESC
LIMIT 30;
```

### 3. Actions Success Rate
```sql
SELECT
    action_type,
    COUNT(*) as total,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
    ROUND(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM mio_actions
WHERE status = 'completed'
GROUP BY action_type;
```

### 4. Open Issues by Severity
```sql
SELECT
    severity,
    COUNT(*) as count
FROM issue_tracking
WHERE status = 'open'
GROUP BY severity
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;
```

---

## 🚀 Следующие шаги

### Уже готово:
- ✅ Создана база данных
- ✅ Определены 9 таблиц
- ✅ Repositories слой
- ✅ Интеграция с AutomationToolkitManager
- ✅ Автоматическое сохранение при запуске jobs

### Можно добавить:
- [ ] API endpoints для получения исторических данных
- [ ] Dashboard для визуализации трендов
- [ ] Alarms на основе трендов
- [ ] Экспорт в Grafana для отображения

---

## 📝 Примечания

- **База данных:** SQLite (`mio_manager.db`) создаётся автоматически при первом запуске
- **Миграции:** SQLAlchemy `Base.metadata.create_all()` создаёт/обновляет схему
- **Производительность:** Indexes на часто используемых полях (created_at, status, severity)
- **Размер:** JSON columns для гибкости, но могут увеличить размер БД

---

**Статус:** ✅ База данных полностью интегрирована и готова к использованию!
