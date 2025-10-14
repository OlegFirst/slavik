# Port Conflicts - Решения

**Дата:** 2025-10-11
**Статус:** ⚠️ КРИТИЧНО - требует немедленного решения

---

## 🔴 Обнаруженные конфликты

### Конфликт 1: Port 8050

**Конфликтующие сервисы:**
1. **DB Intelligence** (AI-office-infrastructure)
   - Файл: `/infrastructure/AI-office-infrastructure/db-intelligence/main.py`
   - Строка 234: `port = int(os.getenv("DB_INTELLIGENCE_PORT", 8051))`
   - Строка 13: комментарий `uvicorn main:app --host 0.0.0.0 --port 8050`
   - EventBusHelper: `port=8051` (строка 181)

2. **Real-time WebSocket** (вне AI Office)
   - Файл: `/infrastructure/runtime/realtime-websocket/main.py`
   - Default port: 8050

**Проблема:**
- В коде DB Intelligence есть несоответствие:
  - main.py по умолчанию: 8051
  - Комментарий в main.py: 8050
  - EventBusHelper: 8051
  - Документация FULL_COMPONENT_CATALOG.md: 8050

**Решение:**

**Вариант A (Рекомендуемый):**
```bash
# DB Intelligence оставить на 8050 (как в документации)
# Real-time WebSocket переместить на 8053

# 1. Исправить DB Intelligence main.py:
DB_INTELLIGENCE_PORT=8050 (по умолчанию)

# 2. Исправить EventBusHelper в db-intelligence/main.py:
port = int(os.getenv("DB_INTELLIGENCE_PORT", 8050))  # было 8051

# 3. Переместить Real-time WebSocket:
REALTIME_WEBSOCKET_PORT=8053
```

**Файлы для изменения:**
1. `/infrastructure/AI-office-infrastructure/db-intelligence/main.py`
   - Строка 181: `port=int(os.getenv("DB_INTELLIGENCE_PORT", 8050))`
   - Строка 234: `port = int(os.getenv("DB_INTELLIGENCE_PORT", 8050))`

2. `/infrastructure/runtime/realtime-websocket/main.py`
   - Изменить default port с 8050 на 8053

3. Создать `.env.example`:
```bash
# DB Intelligence
DB_INTELLIGENCE_PORT=8050
DB_INTELLIGENCE_HOST=0.0.0.0

# Real-time WebSocket
REALTIME_WEBSOCKET_PORT=8053
```

---

### Конфликт 2: Port 8060

**Конфликтующие сервисы:**
1. **Project & Code Quality Agent** (main service)
   - Файл: `/infrastructure/AI-office-infrastructure/project-agent/main.py`
   - Строка 44: `PORT = int(os.getenv("PROJECT_AGENT_PORT", "8060"))`
   - Основной сервис, должен быть на 8060

2. **DevOps Agent API** (вспомогательный API)
   - Файл: `/infrastructure/AI-office-infrastructure/devops-agent/api/main.py`
   - Строка 168: `uvicorn.run(app, host="0.0.0.0", port=8060)`
   - Вспомогательный API, можно переместить

**Проблема:**
- DevOps Agent имеет два файла:
  - `devops-agent/main.py` - основной service (port 8058) ✅
  - `devops-agent/api/main.py` - вспомогательный API (port 8060) ❌ конфликт!

**Решение:**

**Вариант A (Рекомендуемый):**
```bash
# Project Agent оставить на 8060 (основной сервис)
# DevOps Agent API переместить на 8061

# Изменить devops-agent/api/main.py:
DEVOPS_AGENT_API_PORT=8061
```

**Файлы для изменения:**
1. `/infrastructure/AI-office-infrastructure/devops-agent/api/main.py`
   - Строка 168: изменить с `port=8060` на `port=int(os.getenv("DEVOPS_AGENT_API_PORT", 8061))`

2. Создать `.env.example`:
```bash
# Project & Code Quality Agent
PROJECT_AGENT_PORT=8060

# DevOps Agent (main)
DEVOPS_AGENT_PORT=8058

# DevOps Agent API (auxiliary)
DEVOPS_AGENT_API_PORT=8061
```

---

### Проблема 3: Analytics Specialist - несоответствие портов

**Проблема:**
- Код использует `settings.PORT`
- Документация упоминает 8056
- FULL_COMPONENT_CATALOG.md: 8051

**Решение:**

```bash
# Стандартизировать на 8051 (как в каталоге)
ANALYTICS_SPECIALIST_PORT=8051
```

**Файлы для изменения:**
1. `/infrastructure/AI-office-infrastructure/analytics-specialist/config/settings.py`
   - Проверить значение PORT по умолчанию

2. Обновить документацию:
   - `/infrastructure/FULL_COMPONENT_CATALOG.md` - строка 194: убрать упоминание 8056

3. Создать `.env.example`:
```bash
# Analytics Specialist
ANALYTICS_SPECIALIST_PORT=8051
ANALYTICS_SPECIALIST_HOST=0.0.0.0
```

---

## ✅ План действий

### Шаг 1: Создать .env.example для каждого компонента

**1.1. MIO Manager (.env.example):**
```bash
# MIO Manager Configuration
MIO_MANAGER_PORT=8046
MIO_MANAGER_HOST=0.0.0.0

# Integration URLs
SERVICE_DISCOVERY_URL=http://localhost:8500
PROMETHEUS_URL=http://prometheus:9090
REDIS_URL=redis://localhost:6379
ORCHESTRATOR_URL=http://localhost:8059
GATEWAY_URL=http://localhost:8000
WORKFLOW_INTELLIGENCE_URL=http://localhost:8020
PREDICTIVE_URL=http://localhost:8030
OPTIMIZER_URL=http://localhost:8031
COORDINATION_CENTER_URL=http://localhost:8004
COMPLIANCE_MONITORING_URL=http://localhost:8017
AI_EVENT_MANAGER_URL=http://localhost:8055
DEVOPS_AGENT_URL=http://localhost:8058

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Debug
DEBUG=false
```

**1.2. DB Intelligence (.env.example):**
```bash
# DB Intelligence Configuration
DB_INTELLIGENCE_PORT=8050
DB_INTELLIGENCE_HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# Orchestrator
ORCHESTRATOR_URL=http://localhost:8059

# Debug
DEBUG=false
```

**1.3. AI Event Manager (.env.example):**
```bash
# AI Event Manager Configuration
AI_EVENT_MANAGER_PORT=8055
AI_EVENT_MANAGER_HOST=0.0.0.0

# EventBus
EVENTBUS_BACKEND=redis
REDIS_URL=redis://localhost:6379

# Integration URLs
EVENT_INTELLIGENCE_URL=http://localhost:8039
DEVOPS_AGENT_URL=http://localhost:8050
GITHUB_INTEGRATION_URL=http://localhost:8051
MIO_MANAGER_URL=http://localhost:8046

# Project Root
PROJECT_ROOT=/Users/MD/AI-Platform-ISO

# Monitoring
MONITOR_INTERVAL=300

# Debug
DEBUG=false
```

**1.4. Analytics Specialist (.env.example):**
```bash
# Analytics Specialist Configuration
ANALYTICS_SPECIALIST_PORT=8051
ANALYTICS_SPECIALIST_HOST=0.0.0.0

# Competency
COMPETENCY_LEVEL=middle

# Integration URLs
MIO_MANAGER_URL=http://localhost:8046
PROCESS_ANALYTICS_URL=http://localhost:8xxx
AI_ORCHESTRATOR_URL=http://localhost:8059

# Background Tasks
DAILY_HEALTH_CHECK_ENABLED=true
DAILY_HEALTH_CHECK_TIME=09:00
CONTINUOUS_IMPROVEMENT_ENABLED=true
CONTINUOUS_IMPROVEMENT_INTERVAL=3600

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
REDIS_URL=redis://localhost:6379

# Debug
DEBUG=false
```

**1.5. DevOps Agent (.env.example):**
```bash
# DevOps Agent Configuration
DEVOPS_AGENT_PORT=8058
DEVOPS_AGENT_HOST=0.0.0.0

# DevOps Agent API (auxiliary)
DEVOPS_AGENT_API_PORT=8061

# Integration URLs
MIO_MANAGER_URL=http://localhost:8046
WORKFLOW_INTELLIGENCE_URL=http://localhost:8020

# Debug
DEBUG=false
```

**1.6. Agent Router (.env.example):**
```bash
# Agent Router Configuration
AGENT_ROUTER_PORT=8057
AGENT_ROUTER_HOST=0.0.0.0

# Orchestrator
AI_ORCHESTRATOR_URL=http://localhost:8059

# Debug
DEBUG=false
```

**1.7. Project & Code Quality Agent (.env.example):**
```bash
# Project & Code Quality Agent Configuration
PROJECT_AGENT_PORT=8060
PROJECT_AGENT_HOST=0.0.0.0

# Integration URLs
MIO_MANAGER_URL=http://localhost:8046

# Debug
DEBUG=false
```

**1.8. Orchestrator (.env.example):**
```bash
# AI Office Orchestrator Configuration
AI_OFFICE_ORCHESTRATOR_PORT=8059
AI_OFFICE_ORCHESTRATOR_HOST=0.0.0.0

# Integration URLs
MIO_MANAGER_URL=http://localhost:8046

# Debug
DEBUG=false
```

---

### Шаг 2: Исправить код

**2.1. DB Intelligence - исправить порт:**
```python
# Файл: /infrastructure/AI-office-infrastructure/db-intelligence/main.py

# Строка 181 (БЫЛО):
eventbus_helper = EventBusHelper(
    service_name="db-intelligence",
    port=int(os.getenv("DB_INTELLIGENCE_PORT", 8051)),  # ❌ Было 8051
    ...
)

# СТАЛО:
eventbus_helper = EventBusHelper(
    service_name="db-intelligence",
    port=int(os.getenv("DB_INTELLIGENCE_PORT", 8050)),  # ✅ Теперь 8050
    ...
)

# Строка 234 (уже правильно):
port = int(os.getenv("DB_INTELLIGENCE_PORT", 8051))  # ⚠️ Изменить на 8050!
```

**2.2. DevOps Agent API - изменить порт:**
```python
# Файл: /infrastructure/AI-office-infrastructure/devops-agent/api/main.py

# Строка 168 (БЫЛО):
uvicorn.run(app, host="0.0.0.0", port=8060)  # ❌ Конфликт!

# СТАЛО:
port = int(os.getenv("DEVOPS_AGENT_API_PORT", 8061))
uvicorn.run(app, host="0.0.0.0", port=port)  # ✅ Теперь 8061
```

**2.3. Real-time WebSocket - изменить порт:**
```python
# Файл: /infrastructure/runtime/realtime-websocket/main.py

# БЫЛО:
# Default port: 8050

# СТАЛО:
# Default port: 8053
PORT = int(os.getenv("REALTIME_WEBSOCKET_PORT", 8053))
```

---

### Шаг 3: Обновить документацию

**3.1. Обновить FULL_COMPONENT_CATALOG.md:**
```markdown
# Строка 119 (DB Intelligence):
- **Port:** 8050 ✅ (исправлен конфликт с Real-time WebSocket)

# Строка 194 (Analytics Specialist):
- **Port:** 8051 (стандартизировано)

# Строка 236 (DevOps Agent):
- **Port:** 8058 (main), 8061 (API) ✅ (исправлен конфликт)

# Добавить в Summary Tables:
### Port Conflicts Resolved
- **8050:** DB Intelligence (8050), Real-time WebSocket moved to 8053 ✅
- **8060:** Project Agent (8060), DevOps Agent API moved to 8061 ✅
- **Analytics:** Standardized to 8051 ✅
```

**3.2. Обновить КРАТКАЯ_СВОДКА.md:**
```markdown
# Убрать из секции "Конфликты портов":
**✅ Конфликты портов РЕШЕНЫ:**
- 8050: DB Intelligence (8050) ✅, Real-time WebSocket → 8053 ✅
- 8060: Project Agent (8060) ✅, DevOps Agent API → 8061 ✅
- Analytics Specialist: Стандартизирован на 8051 ✅
```

---

### Шаг 4: Создать единый PORT_MAP.md

```markdown
# AI-Office Infrastructure - Port Map

## Официальная карта портов

| Порт | Сервис | Файл | Статус |
|------|--------|------|--------|
| 8046 | MIO Manager | mio-manager/main.py | ✅ |
| 8050 | DB Intelligence | db-intelligence/main.py | ✅ |
| 8051 | Analytics Specialist | analytics-specialist/main.py | ✅ |
| 8055 | AI Event Manager | ai-event-manager/main.py | ✅ |
| 8057 | Agent Router | agent-router/main.py | ✅ |
| 8058 | DevOps Agent | devops-agent/main.py | ✅ |
| 8059 | Orchestrator | orchestrator/main.py | ✅ |
| 8060 | Project & Code Quality Agent | project-agent/main.py | ✅ |
| 8061 | DevOps Agent API | devops-agent/api/main.py | ✅ |

## Порты вне AI Office (для справки)

| Порт | Сервис | Расположение | Примечание |
|------|--------|-------------|-----------|
| 8053 | Real-time WebSocket | runtime/realtime-websocket | Перемещён с 8050 |
| 8000 | API Gateway | gateway/api-gateway | Production gateway |
| 8001 | Auth Service | security/auth | Authentication |
| 8020 | Workflow Intelligence | intelligent-core/workflow_intelligence | Core service |
| 8500 | Service Discovery | runtime/service-discovery | v2.0 |
| 9090 | Prometheus | observability/prometheus | Metrics |
| 3000 | Grafana | observability/grafana | Dashboards |
| 6379 | Redis | Docker | Cache + EventBus |
| 5432 | PostgreSQL | Supabase | Database |
| 6333 | Qdrant | Cloud | Vector DB |

## Environment Variables

Каждый компонент AI Office должен иметь `.env.example` с:
- `{SERVICE}_PORT` - порт сервиса
- `{SERVICE}_HOST` - хост сервиса (default: 0.0.0.0)
- Integration URLs
- Database URLs
- DEBUG flag
```

---

## 🎯 Checklist для выполнения

### Критично (сегодня)
- [ ] Создать `.env.example` для всех 8 компонентов
- [ ] Исправить DB Intelligence port (8051 → 8050)
- [ ] Исправить DevOps Agent API port (8060 → 8061)
- [ ] Исправить Real-time WebSocket port (8050 → 8053)
- [ ] Создать PORT_MAP.md
- [ ] Обновить FULL_COMPONENT_CATALOG.md
- [ ] Обновить КРАТКАЯ_СВОДКА.md

### Важно (эта неделя)
- [ ] Протестировать запуск каждого сервиса
- [ ] Проверить отсутствие конфликтов портов
- [ ] Обновить docker-compose.yml (если есть)
- [ ] Создать unified .env для всего AI Office

### Желательно
- [ ] Автоматизировать проверку конфликтов портов
- [ ] Создать скрипт для валидации портов
- [ ] Добавить в CI/CD проверку портов

---

**Дата создания:** 2025-10-11
**Статус:** ⚠️ В процессе исправления
**Следующий обзор:** После применения всех изменений
