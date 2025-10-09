# 🧠 AI MIO Manager - Intelligent Monitoring & Observability Manager

**Port:** 8046
**Version:** 1.0.0

---

## 🎯 Что это?

**AI MIO Manager** - это **управляющий центр платформы**, который:

1. **Запускает Automation Toolkit** для анализа кода и системы
2. **Управляет API Gateway** и координирует сервисы
3. **Формирует задачи** для улучшений и исправлений
4. **Делегирует задачи Orchestrator** для выполнения
5. **Отчитывается в систему мониторинга** (Prometheus/Grafana)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                   AI MIO MANAGER (Port 8046)                         │
│              Управляющий центр + Action Executor                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Обнаруживает проблему (Prometheus metrics)                      │
│  2. Анализирует через Automation Toolkit                            │
│  3. Формирует задачу (Task)                                         │
│  4. Выполняет действие или делегирует Orchestrator                  │
│  5. Отчитывается в Monitoring                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
         │                          │                         │
         ▼                          ▼                         ▼
   AUTOMATION            API GATEWAY/               ORCHESTRATOR
     TOOLKIT           INTELLIGENT GATEWAY          (координация)
   (инструменты)        (управление)              (делегирование)
```

---

## 📦 Компоненты

### 1. Automation Toolkit Manager
**Файл:** `integrations/automation_toolkit.py`

Запускает инструменты из `/tools`:
- **AST Analyzer** - auto-discovery сервисов
- **Dependency Mapper** - root cause analysis
- **Security Scanner** (Bandit) - OWASP сканирование
- **Complexity Analyzer** (Radon) - code quality
- **Test Generator** - synthetic monitoring

### 2. Orchestrator Client
**Файл:** `integrations/orchestrator_client.py`

Делегирует задачи AI Orchestrator:
- Service restart
- Config updates
- Task delegation
- Task status tracking

### 3. Gateway Manager
**Файл:** `integrations/gateway_manager.py`

Управляет API Gateway:
- Service registration
- Routing updates
- Health checks
- Circuit breaker control

### 4. Automation Scheduler
**Файл:** `scheduler/automation_jobs.py`

**6 автоматических задач:**

| Задача | Расписание | Действие |
|--------|-----------|----------|
| Service Discovery | Каждые 5 мин | Auto-discovery новых сервисов |
| Security Scan | Каждый час | Bandit security scan |
| Dependency Analysis | Каждые 15 мин | Root cause analysis |
| Code Complexity | Ежедневно 2:00 | Radon complexity analysis |
| Test Generation | Воскресенье 3:00 | Synthetic tests generation |
| Health Check | Каждые 2 мин | Health check всех сервисов |

---

## 🚀 Запуск

### 1. Установить зависимости

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/mio-manager
pip3 install -r requirements.txt
```

### 2. Запустить MIO Manager

```bash
python3 main.py
```

**Или с uvicorn:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8046 --reload
```

---

## 📊 API Endpoints

### Service Discovery

```bash
POST /api/discover
{
  "force_rescan": false
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_services": 12,
    "monitored_services": 12,
    "coverage": {
      "percentage": 100.0,
      "monitored": 12,
      "total": 12
    }
  }
}
```

### Dependency Analysis

```bash
POST /api/analyze/dependencies
{
  "service_name": "governance"  # optional
}
```

### Security Scan

```bash
POST /api/security/scan
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "clean",
    "high_severity": 0,
    "medium_severity": 2,
    "low_severity": 5
  }
}
```

### Code Complexity

```bash
POST /api/analyze/complexity
{
  "service_name": "validation"
}
```

### Delegate Task

```bash
POST /api/tasks/delegate
{
  "task_type": "security",
  "details": {
    "severity": "high",
    "count": 3
  },
  "priority": "critical"
}
```

### Gateway Registration

```bash
POST /api/gateway/register
{
  "name": "new-service",
  "endpoints": [...]
}
```

### MIO Status

```bash
GET /api/status
```

---

## 📈 Prometheus Metrics

MIO Manager экспортирует метрики на `/metrics`:

```
# Service Discovery
mio_service_coverage_percentage 100.0
mio_services_total 12
mio_unmonitored_services 0

# Security
mio_security_high_issues 0
mio_security_medium_issues 2

# Code Complexity
mio_code_complexity_avg{service="validation"} 7.2
mio_code_complexity_max{service="validation"} 15

# Dependencies
mio_dependency_graph_nodes 45
mio_circular_dependencies 0

# Actions
mio_actions_executed_total{action_type="service_discovery"} 120
mio_actions_executed_total{action_type="security_scan"} 24
```

---

## 🔄 Workflow Example

**Scenario: HIGH security issue обнаружена**

1. **Hourly Security Scan запускается** (scheduler)
2. **Bandit находит 3 HIGH issues**
3. **MIO Manager создаёт задачу:**
   ```python
   {
     'type': 'security',
     'priority': 'critical',
     'details': {'high_severity': 3}
   }
   ```
4. **Делегирует Orchestrator:**
   ```python
   await orchestrator_client.delegate_task(task)
   ```
5. **Orchestrator назначает AI Agent** для исправления
6. **MIO отчитывается в Prometheus:**
   ```python
   security_high_issues.set(3)
   actions_executed.inc()
   ```
7. **Grafana показывает алерт**
8. **После исправления:** новый scan → 0 issues → алерт закрыт

---

## 🛠️ Конфигурация

**Файл:** `config.py`

```python
# Service config
SERVICE_PORT = 8046

# Orchestrator
ORCHESTRATOR_URL = "http://localhost:8001"

# Gateway
GATEWAY_URL = "http://localhost:8000"

# Prometheus
PROMETHEUS_URL = "http://localhost:9090"

# Grafana
GRAFANA_URL = "http://localhost:3000"
```

---

## 📁 Структура

```
intelligent-core/mio-manager/
├── main.py                          # FastAPI app
├── config.py                        # Configuration
├── database.py                      # ✅ Database initialization
├── README.md                        # This file
├── DATABASE_INTEGRATION.md          # ✅ Database documentation
├── requirements.txt                 # Dependencies
│
├── api/
│   ├── __init__.py
│   └── routes.py                    # API endpoints
│
├── integrations/
│   ├── __init__.py
│   ├── automation_toolkit.py        # ✅ Automation Toolkit Manager + DB persistence
│   ├── orchestrator_client.py       # ✅ Orchestrator Client
│   └── gateway_manager.py           # ✅ Gateway Manager
│
├── models/
│   ├── __init__.py
│   └── database.py                  # ✅ SQLAlchemy models (9 tables)
│
├── repositories/
│   ├── __init__.py
│   ├── reports_repository.py        # ✅ Save/retrieve reports
│   └── actions_repository.py        # ✅ Save/retrieve actions
│
└── scheduler/
    ├── __init__.py
    └── automation_jobs.py           # ✅ 6 cron jobs + DB persistence
```

---

## ✅ Что интегрировано

| Компонент | Статус | Функция |
|-----------|--------|---------|
| **Automation Toolkit** | ✅ | Запуск инструментов анализа |
| **Orchestrator Client** | ✅ | Делегирование задач |
| **Gateway Manager** | ✅ | Управление API Gateway |
| **Database Persistence** | ✅ | SQLite БД для отчётов и действий (9 таблиц) |
| **Auto-discovery** | ✅ | Каждые 5 минут + сохранение в БД |
| **Security Scan** | ✅ | Каждый час + сохранение в БД |
| **Dependency Analysis** | ✅ | Каждые 15 минут + сохранение в БД |
| **Complexity Analysis** | ✅ | Ежедневно + сохранение в БД |
| **Test Generation** | ✅ | Еженедельно |
| **Health Checks** | ✅ | Каждые 2 минуты |
| **Prometheus Export** | ✅ | `/metrics` endpoint |

---

## 🚀 Готово к работе!

MIO Manager полностью интегрирован с Automation Toolkit и готов:
- ✅ Автоматически обнаруживать сервисы
- ✅ Анализировать код и безопасность
- ✅ Формировать задачи для исправлений
- ✅ Делегировать Orchestrator
- ✅ Управлять Gateway
- ✅ Отчитываться в Monitoring
- ✅ **Сохранять все отчёты и действия в БД** (9 таблиц)

---

## 💾 Database Integration

MIO Manager сохраняет **все отчёты и действия** в SQLite базу данных (`mio_manager.db`).

**9 таблиц:**
- `analysis_reports` - Все отчёты анализа
- `service_discoveries` - История service discovery
- `security_scan_results` - Результаты Bandit сканов
- `code_complexity_results` - Анализ сложности кода
- `dependency_analysis_results` - Анализ зависимостей
- `mio_actions` - Все действия MIO Manager
- `task_delegations` - Задачи делегированные Orchestrator
- `issue_tracking` - Отслеживание проблем (open → resolved)
- `metrics_snapshots` - Snapshots метрик для трендов

**Подробнее:** См. [DATABASE_INTEGRATION.md](DATABASE_INTEGRATION.md)
