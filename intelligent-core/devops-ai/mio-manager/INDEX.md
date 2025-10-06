# 📚 MIO Manager - Навигация по документации

**Версия:** 1.0.0
**Дата:** 2025-10-03
**Статус:** ✅ Production Ready

---

## 🚀 Быстрый старт

1. **[README.md](README.md)** - Краткий обзор сервиса
2. **[docs/SERVICE_DOCUMENTATION.md](docs/SERVICE_DOCUMENTATION.md)** - **⭐ ГЛАВНАЯ ТЕХНИЧЕСКАЯ ДОКУМЕНТАЦИЯ**

---

## 📖 Документация

### Основная документация

| Документ | Описание | Статус |
|----------|----------|--------|
| **[docs/SERVICE_DOCUMENTATION.md](docs/SERVICE_DOCUMENTATION.md)** | Полная техническая документация | ✅ Актуально |
| [README.md](README.md) | Краткий обзор и quick start | ✅ Актуально |
| [requirements.txt](requirements.txt) | Зависимости | ✅ Актуально |

### Специализированная документация

| Документ | Описание | Статус |
|----------|----------|--------|
| [docs/DATABASE_INTEGRATION.md](docs/DATABASE_INTEGRATION.md) | База данных (9 таблиц) | ✅ Актуально |
| [docs/WORKFLOW_INTEGRATION.md](docs/WORKFLOW_INTEGRATION.md) | Workflow Intelligence интеграция | ✅ Актуально |
| [docs/INTEGRATION_COMPLETE.md](docs/INTEGRATION_COMPLETE.md) | Сводка интеграции | ✅ Актуально |

### Тестирование

| Документ | Описание | Статус |
|----------|----------|--------|
| [tests/README.md](tests/README.md) | Инструкции по тестированию | ✅ Актуально |
| [tests/test_database.py](tests/test_database.py) | Database tests | ✅ Готово |
| [tests/test_api.py](tests/test_api.py) | API tests | 🚧 TODO |
| [tests/test_workflows.py](tests/test_workflows.py) | Workflow tests | 🚧 TODO |

---

## 🗂️ Структура проекта

```
intelligent-core/mio-manager/
├── INDEX.md                         # 📚 Этот файл (навигация)
├── README.md                        # 📖 Краткий обзор
├── main.py                          # 🚀 FastAPI application
├── config.py                        # ⚙️ Configuration
├── database.py                      # 💾 Database initialization
├── requirements.txt                 # 📦 Dependencies
│
├── api/                            # 🌐 API Endpoints
│   ├── __init__.py
│   └── routes.py                   # 10 endpoints
│
├── integrations/                   # 🔗 External integrations
│   ├── __init__.py
│   ├── automation_toolkit.py       # Automation Toolkit Manager
│   ├── orchestrator_client.py      # Orchestrator Client
│   ├── gateway_manager.py          # Gateway Manager
│   ├── workflow_intelligence_client.py  # Workflow Intelligence
│   └── workflow_optimizer_client.py     # AI Optimizer
│
├── workflows/                      # 🔄 Automated workflows
│   ├── __init__.py
│   └── automated_response_engine.py # Response Engine
│
├── models/                         # 📊 Database models
│   ├── __init__.py
│   └── database.py                 # 9 SQLAlchemy models
│
├── repositories/                   # 💾 Data access layer
│   ├── __init__.py
│   ├── reports_repository.py       # Reports CRUD
│   └── actions_repository.py       # Actions CRUD
│
├── scheduler/                      # ⏰ Scheduled jobs
│   ├── __init__.py
│   └── automation_jobs.py          # 6 cron jobs
│
├── tests/                          # 🧪 Tests
│   ├── __init__.py
│   ├── README.md
│   └── test_database.py            # Database tests
│
├── docs/                           # 📚 Documentation
│   ├── SERVICE_DOCUMENTATION.md    # ⭐ ГЛАВНАЯ ДОКУМЕНТАЦИЯ
│   ├── DATABASE_INTEGRATION.md
│   ├── WORKFLOW_INTEGRATION.md
│   └── INTEGRATION_COMPLETE.md
│
└── _archive/                       # 🗄️ Архив старых документов
    └── TOOLS_INTEGRATION_OLD.md
```

---

## 🎯 Основные функции

### 1. Automation Toolkit
- Service Discovery (AST Analyzer)
- Security Scanning (Bandit)
- Dependency Analysis
- Code Complexity (Radon)
- Test Generation

### 2. Automated Response
- Security Incident Workflow
- Service Down Workflow
- Managed Autonomy

### 3. Integrations
- Workflow Intelligence Engine
- AI Workflow Optimizer
- AI Orchestrator
- API Gateway

### 4. Data Persistence
- 9 SQLite tables
- Reports, Actions, Issues, Tasks
- Metrics Snapshots

### 5. Scheduled Jobs
- Service Discovery (5 min)
- Security Scan (1 hour)
- Dependency Analysis (15 min)
- Complexity Analysis (daily)
- Test Generation (weekly)
- Health Check (2 min)

---

## 🔗 API Endpoints

**Base URL:** `http://localhost:8046`

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/discover` | POST | Service discovery |
| `/api/security/scan` | POST | Security scan |
| `/api/analyze/dependencies` | POST | Dependency analysis |
| `/api/analyze/complexity` | POST | Code complexity |
| `/api/tasks/delegate` | POST | Delegate task |
| `/api/status` | GET | MIO status |
| `/metrics` | GET | Prometheus metrics |
| `/health` | GET | Health check |

**Подробнее:** [docs/SERVICE_DOCUMENTATION.md#api-endpoints](docs/SERVICE_DOCUMENTATION.md#api-endpoints)

---

## 📊 База данных

**9 таблиц:**

1. `analysis_reports` - Все отчёты анализа
2. `service_discoveries` - История service discovery
3. `security_scan_results` - Security scans
4. `code_complexity_results` - Complexity analysis
5. `dependency_analysis_results` - Dependency analysis
6. `mio_actions` - Все действия MIO Manager
7. `task_delegations` - Задачи → Orchestrator
8. `issue_tracking` - Отслеживание проблем
9. `metrics_snapshots` - Snapshots для трендов

**Подробнее:** [docs/DATABASE_INTEGRATION.md](docs/DATABASE_INTEGRATION.md)

---

## 🔄 Workflows

### Security Incident Workflow

**States:** `detected → analyzing → task_created → delegated → in_progress → resolved → closed`

**Actions by severity:**
- **CRITICAL:** Circuit Breaker + Emergency task
- **HIGH:** Create task + Delegate
- **MEDIUM:** Normal delegation
- **LOW:** Log only

**Подробнее:** [docs/WORKFLOW_INTEGRATION.md](docs/WORKFLOW_INTEGRATION.md)

---

## 🚀 Запуск

```bash
# 1. Установить зависимости
cd /Users/MD/AI-Platform-ISO/intelligent-core/mio-manager
pip3 install -r requirements.txt

# 2. Запустить
python3 main.py

# Или с uvicorn:
uvicorn main:app --host 0.0.0.0 --port 8046 --reload
```

**Подробнее:** [docs/SERVICE_DOCUMENTATION.md#запуск-и-развёртывание](docs/SERVICE_DOCUMENTATION.md#запуск-и-развёртывание)

---

## 🧪 Тестирование

```bash
# Все тесты
pytest tests/ -v

# С coverage
pytest --cov=. --cov-report=html tests/
```

**Подробнее:** [tests/README.md](tests/README.md)

---

## 📈 Мониторинг

**Prometheus:** `http://localhost:8046/metrics`

**Метрики:**
- `mio_service_coverage_percentage`
- `mio_security_high_issues`
- `mio_code_complexity_avg`
- `mio_actions_executed_total`

**Подробнее:** [docs/SERVICE_DOCUMENTATION.md#мониторинг](docs/SERVICE_DOCUMENTATION.md#мониторинг)

---

## ✅ Status

| Компонент | Статус |
|-----------|--------|
| **Core Application** | ✅ Production Ready |
| **Database** | ✅ 9 tables integrated |
| **Automation Toolkit** | ✅ Fully integrated |
| **Workflow Intelligence** | ✅ Integrated |
| **AI Optimizer** | ✅ Integrated |
| **Automated Response** | ✅ Security workflow ready |
| **Scheduled Jobs** | ✅ 6 jobs running |
| **API** | ✅ 10 endpoints |
| **Documentation** | ✅ Complete |
| **Tests** | 🚧 Basic tests (80% TODO) |
| **Docker** | 🚧 TODO |

---

## 🎯 TODO

- [ ] Дополнительные unit tests
- [ ] Integration tests
- [ ] Docker image
- [ ] Grafana dashboard
- [ ] Service down workflow (полная реализация)
- [ ] Complexity workflow
- [ ] Dependency workflow

---

## 📞 Контакты

**Сервис:** MIO Manager
**Port:** 8046
**Версия:** 1.0.0
**Статус:** ✅ Production Ready

---

**Начните изучение с:** [docs/SERVICE_DOCUMENTATION.md](docs/SERVICE_DOCUMENTATION.md) ⭐
