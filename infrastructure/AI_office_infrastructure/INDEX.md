# AI-Office Infrastructure - Навигация

**Дата последнего обновления:** 2025-10-11
**Версия:** 1.0
**Статус:** Production Ready (требует исправления конфликтов портов)

---

## 📚 Основные документы

### 🎯 Начните отсюда
1. **[КРАТКАЯ_СВОДКА.md](КРАТКАЯ_СВОДКА.md)** ⭐
   - Быстрый обзор всех 8 компонентов
   - Статистика и статус
   - Критичные проблемы
   - Рекомендации

2. **[AI_OFFICE_DETAILED_ANALYSIS.md](AI_OFFICE_DETAILED_ANALYSIS.md)** 📊
   - Полный детальный анализ каждого компонента
   - Назначение, зависимости, интеграции
   - API endpoints, capabilities
   - Особенности и уникальные характеристики

3. **[PORT_CONFLICTS_SOLUTION.md](PORT_CONFLICTS_SOLUTION.md)** 🔧
   - Обнаруженные конфликты портов
   - Пошаговые решения
   - .env.example шаблоны
   - Checklist для выполнения

---

## 🗂️ Структура компонентов

### 1. MIO Manager (8046) - EYES 👁️
```
mio-manager/
├── main.py                          # FastAPI app, port 8046
├── config/                          # Configuration
├── api/                             # API routes
├── integrations/                    # Integration clients (17 файлов)
├── monitoring/                      # Observers & checkers (Phase 2.1)
├── scheduler/                       # SmartScheduler
├── intelligence/                    # AI Intelligence Layer
├── event_handlers.py                # MIO Event Handlers (Phase 2.1)
├── ui_routes.py                     # Web UI Dashboard
└── README.md
```
**Документация компонента:**
- [README.md](mio-manager/README.md)
- [START_HERE.md](mio-manager/START_HERE.md)
- [QUICK_MONITORING_OVERVIEW.md](mio-manager/QUICK_MONITORING_OVERVIEW.md)

---

### 2. DB Intelligence (8050)
```
db-intelligence/
├── main.py                          # FastAPI app, port 8050
├── api.py                           # API routes
├── db_intelligence_service.py       # Core service
├── command_handler.py               # Command handlers
└── README.md
```
**Документация компонента:**
- [README.md](db-intelligence/README.md)

---

### 3. AI Event Manager (8055)
```
ai-event-manager/
├── main.py                          # FastAPI app, port 8055
├── integrations/                    # IntegrationManager
│   ├── __init__.py
│   └── (integration modules)
└── README.md
```
**Документация компонента:**
- [README.md](ai-event-manager/README.md)

---

### 4. Analytics Specialist (8051)
```
analytics-specialist/
├── main.py                          # FastAPI app, port 8051
├── config/                          # Settings
├── api/                             # API routes + UI
│   ├── routes.py
│   └── tools_ui_routes.py          # Web UI для инструментов
├── clients/                         # Integration clients (7 файлов)
├── core/                            # Analytics core
├── tools/                           # Analysis tools (7 файлов)
└── workflows/                       # Background workflows
```
**Документация компонента:**
- [README.md](analytics-specialist/README.md)

---

### 5. DevOps Agent (8058/8061)
```
devops-agent/
├── main.py                          # FastAPI app, port 8058
├── api/
│   └── main.py                      # API service, port 8061
├── agent.py                         # DevOps Agent class
├── tools/                           # Compliance toolkit (NEW v2.0)
│   ├── compliance-checks/          # 6 priority checks
│   └── compliance_runner.py        # Unified interface
└── README.md
```
**Документация компонента:**
- [README.md](devops-agent/README.md)

---

### 6. Agent Router (8057)
```
agent-router/
├── main.py                          # FastAPI app, port 8057
├── router.py                        # Routing logic
├── metrics_server.py                # Metrics
├── docker-compose.yml
└── README.md
```
**Документация компонента:**
- [README.md](agent-router/README.md)

---

### 7. Project & Code Quality Agent (8060)
```
project-agent/
├── main.py                          # FastAPI app, port 8060
├── setup.py                         # Package setup
├── setup.cfg                        # Package config
├── test-project/                    # Demo project
└── README.md
```
**Документация компонента:**
- [README.md](project-agent/README.md)

---

### 8. Orchestrator (8059)
```
orchestrator/
├── main.py                          # FastAPI app, port 8059
├── unified_orchestrator.py          # Core logic
├── executors/                       # Task executors
└── README.md
```
**Документация компонента:**
- [README.md](orchestrator/README.md)

---

## 🔗 Общие модули

### _shared/
```
_shared/
└── eventbus_helper.py               # Universal EventBus integration
```
**Используется в:**
- MIO Manager ✅
- DB Intelligence ✅
- AI Event Manager ✅
- Analytics Specialist ✅
- DevOps Agent ✅
- Project Agent ✅
- Agent Router ❌ (нужно добавить)
- Orchestrator ❌ (нужно добавить)

---

## 📊 Быстрая справка

### Порты компонентов
```
8046  MIO Manager               ✅
8050  DB Intelligence           ✅ (был конфликт с Real-time WebSocket)
8051  Analytics Specialist      ✅
8055  AI Event Manager          ✅
8057  Agent Router              ⚠️ (минимальная реализация)
8058  DevOps Agent              ✅
8059  Orchestrator              ⚠️ (минимальная реализация)
8060  Project Agent             ✅ (был конфликт с DevOps API)
8061  DevOps Agent API          ✅ (перенесён с 8060)
```

### EventBus интеграция
```
✅  MIO Manager
✅  DB Intelligence
✅  AI Event Manager
✅  Analytics Specialist
✅  DevOps Agent
✅  Project Agent
❌  Agent Router         (нужно добавить)
❌  Orchestrator         (нужно добавить)
```

### Prometheus метрики
```
✅  MIO Manager          /metrics
✅  DB Intelligence      /metrics/prometheus
✅  AI Event Manager     /metrics
⚠️  Analytics Specialist /metrics (TODO)
❌  DevOps Agent
❌  Agent Router
❌  Project Agent
❌  Orchestrator
```

### Статус сервисов
```
⏸️  MIO Manager          (stopped)
⏸️  DB Intelligence      (stopped)
⏸️  AI Event Manager     (stopped)
⏸️  Analytics Specialist (stopped)
⏸️  DevOps Agent         (stopped)
⏸️  Agent Router         (stopped)
⏸️  Project Agent        (stopped)
⏸️  Orchestrator         (stopped)
```

---

## 🚀 Быстрый старт

### Запуск одного компонента

```bash
# Пример: MIO Manager
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager
python main.py

# Или через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8046 --reload
```

### Запуск всех компонентов (TODO)

```bash
# В разработке: docker-compose для всего AI Office
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure
docker-compose up -d
```

---

## 🔧 Конфигурация

### Environment Variables

Каждый компонент должен иметь файл `.env` (или использовать `.env.example` как шаблон):

**Общие переменные:**
```bash
# Service Configuration
{SERVICE}_PORT=8xxx
{SERVICE}_HOST=0.0.0.0
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

# Integration URLs
MIO_MANAGER_URL=http://localhost:8046
SERVICE_DISCOVERY_URL=http://localhost:8500
PROMETHEUS_URL=http://prometheus:9090
```

**См. также:**
- [PORT_CONFLICTS_SOLUTION.md](PORT_CONFLICTS_SOLUTION.md) - полные примеры .env.example

---

## 📖 Документация проекта

### Основная документация платформы
- [/infrastructure/FULL_COMPONENT_CATALOG.md](/Users/MD/AI-Platform-ISO/infrastructure/FULL_COMPONENT_CATALOG.md)
  - Каталог ВСЕХ компонентов платформы (40+)
  - Включает AI Office (9), Database (5), Gateway (3), Runtime (4), и др.

### Документация по развертыванию
- [/doc-project/DEPLOYMENT_PORT_MAP.md](/Users/MD/AI-Platform-ISO/doc-project/DEPLOYMENT_PORT_MAP.md)
  - Карта всех портов платформы
  - Deployment стратегия

### Архитектурная документация
- [/intelligent-core/ARCHITECTURE.md](/Users/MD/AI-Platform-ISO/intelligent-core/ARCHITECTURE.md)
  - Архитектура Intelligent Core
- EventBus: `/infrastructure/eventbus/README.md`
- Service Discovery v2.0: `/infrastructure/runtime/service-discovery/README.md`

---

## 🔍 Полезные команды

### Поиск конфликтов портов
```bash
# Найти все используемые порты
grep -r "port.*=.*[0-9]" --include="*.py" .

# Проверить запущенные порты
lsof -i :8046  # MIO Manager
lsof -i :8050  # DB Intelligence
lsof -i :8051  # Analytics Specialist
```

### Проверка EventBus интеграции
```bash
# Найти использование EventBusHelper
grep -r "EventBusHelper" --include="*.py" .

# Найти публикации событий
grep -r "eventbus.publish" --include="*.py" .
```

### Проверка Prometheus метрик
```bash
# Найти endpoints с метриками
grep -r "/metrics" --include="*.py" .

# Проверить prometheus-client
grep -r "prometheus_client" --include="*.py" .
```

---

## 📋 TODO

### Критично (Priority 1)
- [ ] Исправить конфликты портов (см. PORT_CONFLICTS_SOLUTION.md)
- [ ] Создать .env.example для всех компонентов
- [ ] Запустить core сервисы (MIO, DB Intel, AI Event, Analytics, DevOps)

### Важно (Priority 2)
- [ ] Добавить Prometheus метрики (4 компонента)
- [ ] Завершить EventBus интеграцию (Agent Router, Orchestrator)
- [ ] Написать интеграционные тесты

### Желательно (Priority 3)
- [ ] Создать unified docker-compose.yml
- [ ] Создать Grafana dashboard для AI Office
- [ ] Настроить CI/CD
- [ ] Написать Migration Guide

---

## 🆘 Поддержка

### Контакты
- **Проект:** AI Platform ISO
- **Репозиторий:** /Users/MD/AI-Platform-ISO
- **Документация:** Этот файл и связанные документы

### Полезные ссылки
- MIO Manager EYES: [mio-manager/START_HERE.md](mio-manager/START_HERE.md)
- EventBus: `/infrastructure/eventbus/README.md`
- Service Discovery v2.0: `/infrastructure/runtime/service-discovery/README.md`
- Service Catalog v2.0: `/infrastructure/runtime/service-catalog/README.md`

---

## 📝 Changelog

### 2025-10-11 - Первоначальный анализ
- ✅ Создан детальный анализ всех компонентов
- ✅ Обнаружены конфликты портов
- ✅ Проверена EventBus интеграция
- ✅ Проверено Prometheus покрытие
- ✅ Созданы рекомендации по исправлению

---

**Последнее обновление:** 2025-10-11
**Версия документации:** 1.0
**Статус:** ⚠️ Требует исправления конфликтов портов
