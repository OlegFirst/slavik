# Оставшиеся задачи - AI Office Infrastructure Integration

**Created**: 2025-10-11
**Status**: 📋 Roadmap
**Priority**: Medium (опционально, но рекомендуется)

---

## ✅ Что уже сделано (ОСНОВНОЕ)

### 1. Policy Engine ✅
- ✅ Добавлены policies для всех 7 AI Office сервисов
- ✅ Version: 1.1
- ✅ Все сервисы имеют RTO, recovery strategy, escalation teams

### 2. EventBus Helper ✅
- ✅ Создан универсальный `eventbus_helper.py`
- ✅ 278 lines, полностью готов к использованию
- ✅ Документирован с примерами

### 3. Orchestrator ✅
- ✅ Полная интеграция EventBus
- ✅ Auto-registration, heartbeat, graceful shutdown
- ✅ Публикует события в Service Discovery

### 4. Существующие интеграции ✅
- ✅ **ai-event-manager** - уже имеет EventBus
- ✅ **mio-manager** - уже имеет EventBus

---

## 📋 Что осталось (ОПЦИОНАЛЬНО)

### Приоритет 1: EventBus интеграция (5 сервисов)

| Сервис | main.py | EventBus | Handlers | Приоритет | Сложность |
|--------|---------|----------|----------|-----------|-----------|
| **analytics-specialist** | ✅ | ❌ | ✅ | High | Easy |
| **db-intelligence** | ✅ | ❌ | ✅ | High | Easy |
| **devops-agent** | ✅ | ❌ | ❌ | Medium | Medium |
| **agent-router** | ✅ | ❌ | ❌ | Medium | Medium |
| **project-agent** | ✅ | ❌ | ❌ | Low | Easy |

**Время**: ~30-40 минут (все 5 сервисов)

**Почему опционально**:
- Основная функциональность работает без этого
- Сервисы запускаются и работают
- **НО**: Service Discovery не видит эти сервисы
- **НО**: Policy Engine не может их восстанавливать автоматически

**Польза от добавления**:
- ✅ Автоматическая регистрация в Service Discovery
- ✅ Видимость в Unified Catalog
- ✅ Health monitoring через heartbeat
- ✅ Policy-based recovery
- ✅ Видимость в Admin Panel

---

### Приоритет 2: Порты и конфигурация

#### A. Port Conflicts (критично для db-intelligence)

**Проблема**: `db-intelligence` хочет порт 8050, но он занят `monitoring-backend`

**Решение**:
```bash
# В db-intelligence/main.py или через env
export DB_INTELLIGENCE_PORT=8051
```

**Файл**: `infrastructure/AI-office-infrastructure/db-intelligence/main.py`

**Изменение**:
```python
# Было:
PORT = int(os.getenv("DB_INTELLIGENCE_PORT", "8050"))

# Стало:
PORT = int(os.getenv("DB_INTELLIGENCE_PORT", "8051"))  # Avoid conflict with monitoring-backend
```

**Время**: 2 минуты

---

#### B. Analytics Specialist - Missing Port

**Проблема**: `analytics-specialist` не имеет порта в main.py

**Проверить**:
```bash
grep -n "PORT\|port\|uvicorn" /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/analytics-specialist/main.py | head -5
```

**Решение**: Добавить порт (если нет)
```python
PORT = int(os.getenv("ANALYTICS_SPECIALIST_PORT", "8056"))
```

**Время**: 2 минуты

---

### Приоритет 3: Startup Handlers (для 3 сервисов)

Сервисы **без** startup handlers:
- devops-agent
- agent-router
- project-agent

**Почему нужно**:
- EventBus helper требует `@app.on_event("startup")` и `"shutdown"`
- Без handlers невозможно добавить EventBus интеграцию

**Решение**: Добавить базовые handlers
```python
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {SERVICE_NAME} starting...")
    # EventBus integration here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"👋 {SERVICE_NAME} shutting down...")
    # EventBus cleanup here
```

**Время**: 5 минут на каждый сервис = 15 минут

---

## 🎯 Детальный план для каждого сервиса

### 1. analytics-specialist (Priority: High, Time: 10 мин)

**Статус**: ✅ main.py, ✅ handlers, ❌ EventBus

**План**:
1. Проверить порт (если нет, добавить PORT=8056)
2. Добавить EventBus helper (copy-paste из orchestrator)
3. Обновить startup/shutdown handlers

**Код** (добавить в main.py):
```python
# Top of file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _shared.eventbus_helper import EventBusHelper

# After app creation
helper = EventBusHelper(
    service_name="analytics-specialist",
    port=8056,
    capabilities=["metrics_discovery", "dependency_mapping",
                  "bottleneck_detection", "health_analysis"],
    service_type="specialist"
)

# In startup handler (already exists)
@app.on_event("startup")
async def startup_event():
    # Existing code...
    await helper.startup()  # Add this

# In shutdown handler (already exists)
@app.on_event("shutdown")
async def shutdown_event():
    await helper.shutdown()  # Add this
    # Existing code...
```

**Проверка**:
```bash
python main.py
curl http://localhost:8500/v1/catalog/services | jq '.services[] | select(.name=="analytics-specialist")'
```

---

### 2. db-intelligence (Priority: High, Time: 10 мин)

**Статус**: ✅ main.py, ✅ handlers, ❌ EventBus, ⚠️ Port conflict

**План**:
1. **Сначала**: Исправить порт 8050 → 8051
2. Добавить EventBus helper
3. Обновить handlers

**Код**:
```python
# Fix port first
PORT = int(os.getenv("DB_INTELLIGENCE_PORT", "8051"))  # Changed from 8050

# Add EventBus
from _shared.eventbus_helper import EventBusHelper

helper = EventBusHelper(
    service_name="db-intelligence",
    port=8051,  # Updated port
    capabilities=["query_monitoring", "performance_analysis",
                  "optimization_suggestions"],
    dependencies=["eventbus", "postgres", "supabase"],
    service_type="specialist"
)

# In startup
await helper.startup()

# In shutdown
await helper.shutdown()
```

---

### 3. devops-agent (Priority: Medium, Time: 15 мин)

**Статус**: ✅ main.py, ❌ handlers, ❌ EventBus

**План**:
1. Создать startup/shutdown handlers
2. Добавить EventBus helper
3. Определить порт (если нет)

**Код**:
```python
# Define port (check if exists)
PORT = int(os.getenv("DEVOPS_AGENT_PORT", "8058"))

# Add EventBus
from _shared.eventbus_helper import EventBusHelper

helper = EventBusHelper(
    service_name="devops-agent",
    port=8058,
    capabilities=["deployment_automation", "infrastructure_management"],
    service_type="agent"
)

# Create handlers
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 DevOps Agent starting...")
    await helper.startup()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 DevOps Agent shutting down...")
    await helper.shutdown()
```

---

### 4. agent-router (Priority: Medium, Time: 15 мин)

**Статус**: ✅ main.py, ❌ handlers, ❌ EventBus

**План**: Same as devops-agent

**Код**:
```python
PORT = int(os.getenv("AGENT_ROUTER_PORT", "8057"))

from _shared.eventbus_helper import EventBusHelper

helper = EventBusHelper(
    service_name="agent-router",
    port=8057,
    capabilities=["request_routing", "agent_selection", "load_balancing"],
    service_type="router"
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Agent Router starting...")
    await helper.startup()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Agent Router shutting down...")
    await helper.shutdown()
```

---

### 5. project-agent (Priority: Low, Time: 10 мин)

**Статус**: ✅ main.py, ❌ handlers, ❌ EventBus

**План**: Same as devops-agent

**Код**:
```python
PORT = int(os.getenv("PROJECT_AGENT_PORT", "8048"))

from _shared.eventbus_helper import EventBusHelper

helper = EventBusHelper(
    service_name="project-agent",
    port=8048,
    capabilities=["project_tracking", "task_management", "status_reporting"],
    service_type="agent"
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Project Agent starting...")
    await helper.startup()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Project Agent shutting down...")
    await helper.shutdown()
```

---

## ⏱️ Временная оценка

| Задача | Сервисов | Время | Сложность |
|--------|----------|-------|-----------|
| analytics-specialist | 1 | 10 мин | Easy |
| db-intelligence | 1 | 10 мин | Easy |
| devops-agent | 1 | 15 мин | Medium |
| agent-router | 1 | 15 мин | Medium |
| project-agent | 1 | 10 мин | Easy |
| **Total** | **5** | **60 мин** | - |

**Реальное время** (с тестированием): ~1.5 часа

---

## 🧪 План тестирования

### 1. Unit Test (для каждого сервиса)

```bash
# Start service
python main.py

# Check EventBus connection
curl http://localhost:PORT/status
# Should show: "eventbus_connected": true

# Check health
curl http://localhost:PORT/health
```

### 2. Integration Test (Service Discovery)

```bash
# 1. Start Service Discovery
cd infrastructure/runtime/service-discovery
python main.py  # Port 8500

# 2. Start Redis (if not running)
docker run -d -p 6379:6379 redis:7-alpine

# 3. Start a service
cd ../AI-office-infrastructure/analytics-specialist
python main.py

# 4. Check registration
curl http://localhost:8500/v1/catalog/services | jq '.services[] | select(.name=="analytics-specialist")'

# Expected:
{
  "name": "analytics-specialist",
  "runtime_status": "active",
  "health": "healthy",
  "port": 8056,
  "last_seen": "2025-10-11T..."
}

# 5. Wait 30 seconds and check heartbeat
sleep 35
curl http://localhost:8500/v1/catalog/services | jq '.services[] | select(.name=="analytics-specialist") | .last_seen'
# Should be updated (within last 30s)
```

### 3. End-to-End Test

```bash
# Start all services and verify all registered
curl http://localhost:8500/v1/catalog/services | jq '.metadata'

# Expected:
{
  "total_services": 27,
  "registered_services": 8,  # orchestrator + ai-event-manager + mio-manager + 5 new
  "running_services": 8
}
```

---

## 📊 Impact Analysis

### Без EventBus интеграции (текущее состояние):

**Работает**:
- ✅ Сервисы запускаются
- ✅ HTTP endpoints работают
- ✅ Policy Engine имеет правила (но не может применять)

**Не работает**:
- ❌ Service Discovery не видит сервисы
- ❌ Unified Catalog показывает "not_registered"
- ❌ Нет heartbeat monitoring
- ❌ Policy-based recovery не работает
- ❌ Admin Panel не видит статус
- ❌ Balancer Service не получает события

---

### С EventBus интеграцией (после завершения):

**Дополнительно работает**:
- ✅ Auto-registration в Service Discovery
- ✅ Real-time status в Unified Catalog
- ✅ Heartbeat monitoring (60s timeout detection)
- ✅ Policy-based auto-recovery
- ✅ Admin Panel показывает live status
- ✅ Balancer Service получает infrastructure events
- ✅ AI Event Manager видит все сервисы

---

## 🎯 Рекомендация

### Минимально необходимо:
1. **db-intelligence port fix** (8050 → 8051) - 2 минуты
   - Критично, иначе конфликт с monitoring-backend

### Желательно (High Priority):
2. **analytics-specialist** EventBus - 10 минут
3. **db-intelligence** EventBus - 10 минут

**Итого**: 22 минуты для минимально работающей системы

### Опционально (для полноты):
4. **devops-agent** - 15 минут
5. **agent-router** - 15 минут
6. **project-agent** - 10 минут

**Итого**: +40 минут для 100% coverage

---

## 🚀 Quick Start (минимальная версия)

### Шаг 1: Fix db-intelligence port (2 мин)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/db-intelligence

# Edit main.py, change line with PORT:
# FROM: PORT = int(os.getenv("DB_INTELLIGENCE_PORT", "8050"))
# TO:   PORT = int(os.getenv("DB_INTELLIGENCE_PORT", "8051"))
```

### Шаг 2: Add EventBus to analytics-specialist (10 мин)

```bash
cd ../analytics-specialist

# Add to main.py (see detailed code above)
# 1. Import helper
# 2. Create helper instance
# 3. Add to startup/shutdown handlers
```

### Шаг 3: Test (5 мин)

```bash
# Start Service Discovery
cd ../../runtime/service-discovery
python main.py &

# Start analytics
cd ../../AI-office-infrastructure/analytics-specialist
python main.py

# Check
curl http://localhost:8500/v1/catalog/services | jq
```

---

## 📝 Checklist

### Must Do (критично):
- [ ] Fix db-intelligence port conflict (8050 → 8051)

### Should Do (high priority):
- [ ] Add EventBus to analytics-specialist
- [ ] Add EventBus to db-intelligence
- [ ] Test registration in Service Discovery

### Could Do (опционально):
- [ ] Add EventBus to devops-agent
- [ ] Add EventBus to agent-router
- [ ] Add EventBus to project-agent
- [ ] Full integration test
- [ ] Admin Panel visualization test

---

## 💡 Summary

**Основное сделано** ✅:
- Policy Engine готов (v1.1)
- EventBus Helper готов
- Orchestrator интегрирован
- ai-event-manager работает
- mio-manager работает

**Осталось** (опционально):
- 5 сервисов без EventBus (работают, но не в Service Discovery)
- 1 port conflict (критично исправить)
- ~1 час работы для 100% coverage

**Решение**: Можете остановиться сейчас (основное готово) или потратить ~1 час на полную интеграцию.

**Рекомендация**: Исправить port conflict (2 мин) + добавить EventBus в analytics и db-intelligence (20 мин) = 22 минуты для 80% пользы.

---

**Status**: 📋 Roadmap ready
**Decision**: Ваше решение - продолжать или остановиться
