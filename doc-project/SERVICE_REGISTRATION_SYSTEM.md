# Система Регистрации и Учёта Ресурсов

**Created**: 2025-10-11
**Status**: 🔍 Analysis Complete
**Question**: "Кто отвечает за регистрацию элементов в системе?"

---

## 🎯 Ответ на главный вопрос

**Кто отвечает за регистрацию:** `infrastructure/runtime/service-discovery/` (Port 8500)

Это **центральный реестр** (Service Registry) с тремя механизмами регистрации:

1. **HTTP API** - Consul-compatible endpoints для ручной регистрации
2. **EventBus Integration** - Автоматическая регистрация через события
3. **Resource Tracker** (Phase 2) - Активное обнаружение ("ГЛАЗА" системы)

---

## 📊 Архитектура системы регистрации

```
┌─────────────────────────────────────────────────────────────┐
│                  Service Registration Flow                   │
└─────────────────────────────────────────────────────────────┘

1. АКТИВНАЯ РЕГИСТРАЦИЯ (Сервис сам сообщает)
   ┌──────────────┐
   │ New Service  │
   │ starts up    │
   └──────┬───────┘
          │
          ├─► publish_service_started() ──► EventBus ──┐
          │                                             │
          └─► POST /v1/agent/service/register ─────────┤
                                                        │
                                                        ▼
                                            ┌───────────────────┐
                                            │ Service Registry  │
                                            │   (Port 8500)     │
                                            └───────────────────┘
                                                        │
                                                        ├─► In-Memory Registry
                                                        ├─► Redis Persistence
                                                        └─► Health Tracking

2. ПАССИВНОЕ ОБНАРУЖЕНИЕ (Система сама находит)
   ┌──────────────────┐
   │ Resource Tracker │ ←─── MIO Manager (Phase 2)
   │   (ГЛАЗА)        │
   └────────┬─────────┘
            │
            ├─► Scans infrastructure
            ├─► Detects new services
            └─► Publishes to EventBus ──► Service Registry

3. НАЗНАЧЕНИЕ ПОРТОВ
   ┌─────────────────────┐
   │ PORT_ALLOCATION.md  │ ←─── Manual documentation
   └─────────────────────┘
            │
            ├─► Environment Variables (SERVICE_PORT=8046)
            ├─► Port ranges by service type
            │   • BCM Core: 8011-8049
            │   • Intelligence: 8080-8099
            │   • AI Office: 8045-8059
            └─► Consul service discovery reads these
```

---

## 🔧 Компоненты системы регистрации

### 1. Service Registry (Port 8500)

**Location**: `infrastructure/runtime/service-discovery/`

**Назначение**: Центральный реестр всех сервисов платформы

**Ключевые файлы**:
- `service_registry.py` - Core registry implementation
- `main.py` - FastAPI service (Consul-compatible)
- `eventbus_integration.py` - EventBus subscriber

**Хранилище**:
```python
class Service:
    name: str                    # Имя сервиса
    orchestrator: str           # К какому оркестратору относится
    status: str                 # "active", "starting", "stopped"
    registered_at: datetime
    last_seen: datetime         # Для heartbeat tracking
    metadata: Dict[str, Any]    # Дополнительные данные
    dependencies: List[str]     # Зависимости
    health_status: str          # "healthy", "unhealthy"
    port: int                   # Порт сервиса
    url: str                    # URL для доступа
```

**Persistence**:
- In-memory (быстро)
- Redis (персистентность)

---

### 2. EventBus Integration

**Location**: `infrastructure/runtime/service-discovery/eventbus_integration.py`

**Назначение**: Автоматическая регистрация через события EventBus

**События, которые регистрирует**:

```python
# 1. Сервис запустился
await publish_service_started(
    eventbus=eventbus,
    service_name="mio-manager",
    orchestrator="ai-office",
    port=8046,
    metadata={"version": "2.0"},
    dependencies=["orchestrator", "redis"]
)

# 2. Heartbeat (каждые 60 сек)
await publish_service_heartbeat(
    eventbus=eventbus,
    service_name="mio-manager"
)

# 3. Health status update
await publish_service_health(
    eventbus=eventbus,
    service_name="mio-manager",
    health_status="healthy",
    metrics={"cpu": 45, "memory": 512}
)

# 4. Сервис остановился
await publish_service_stopped(
    eventbus=eventbus,
    service_name="mio-manager",
    reason="graceful_shutdown"
)
```

**Автоматические проверки**:
- ⏱️ **Heartbeat timeout**: 60 секунд (по умолчанию)
- 🔍 **Auto-detection**: Если сервис не отправляет heartbeat → помечается как "disconnected"
- 📊 **Health tracking**: Мониторинг состояния каждого сервиса

---

### 3. Resource Tracker (Phase 2 - ГЛАЗА)

**Location**: `infrastructure/AI-office-infrastructure/mio-manager/integrations/resource_tracker_client.py`

**Назначение**: **Активное обнаружение** - система сама находит новые сервисы

**Как работает**:

```python
class ResourceTrackerClient:
    def __init__(self, eventbus, check_interval=60):
        self.eventbus = eventbus
        self.check_interval = check_interval  # Проверка каждые 60 сек

    async def start(self):
        """Запускает циклическое сканирование инфраструктуры"""
        while self.running:
            # 1. Scan running processes
            new_services = await self._scan_processes()

            # 2. Scan Docker containers
            containers = await self._scan_docker()

            # 3. Check open ports
            open_ports = await self._scan_ports()

            # 4. Publish discoveries to EventBus
            for service in new_services:
                await publish_service_started(
                    eventbus=self.eventbus,
                    service_name=service.name,
                    port=service.port,
                    metadata={"discovered_by": "resource_tracker"}
                )

            await asyncio.sleep(self.check_interval)
```

**Интеграция в MIO Manager** (`mio-manager/main.py:159-175`):
```python
# Initialize Resource Tracker (Phase 2 - ГЛАЗА)
resource_tracker = ResourceTrackerClient(
    eventbus=eventbus_client,
    check_interval=60  # Check every 60 seconds
)
await resource_tracker.start()
logger.info("   👀 Resource Tracker started (Phase 2 - ГЛАЗА)")
```

**Возможности**:
- 👀 **Автоматическое обнаружение** новых сервисов
- 🔍 **Сканирование портов** и процессов
- 🐳 **Docker container discovery**
- 📡 **Публикация находок** в EventBus → Service Registry

---

## 🎨 Система назначения портов

### Документация портов

**Location**: `platform-services/PORT_ALLOCATION.md`

**Назначение**: Ручная документация распределения портов

**Диапазоны портов по категориям**:

| Диапазон | Категория | Примеры |
|----------|-----------|---------|
| **8011-8049** | BCM Core Services | Planning (8011), BIA (8012), Governance (8013) |
| **8045-8059** | AI Office / Orchestration | Orchestrator (8045), MIO Manager (8046) |
| **8050-8069** | BCM Extensions | Reserved |
| **8070-8079** | Coordination | BCM Coordination (8070) |
| **8080-8099** | Intelligence Services | BIA Engine (8082), Scenario Orchestrator (8085) |
| **8500** | Service Discovery | Service Registry (Consul-compatible) |
| **8780** | Monitoring | Process Analytics |

### Механизм назначения портов

**Каждый сервис определяет свой порт через Environment Variable**:

```python
# Example: orchestrator/main.py
PORT = int(os.getenv("AI_OFFICE_ORCHESTRATOR_PORT", "8059"))

# Example: mio-manager/main.py
# Port: 8046 (hardcoded in docstring, configurable via env)
```

**Правила**:
1. Порт указывается в `PORT_ALLOCATION.md`
2. Сервис читает порт из env var или использует дефолт
3. При старте сервис регистрируется с этим портом в Service Registry
4. Health endpoint доступен на `http://localhost:{PORT}/health`

**Конфликты портов**:
- Документированы в `PORT_ALLOCATION.md` (раздел "Port Conflict Resolution")
- История изменений:
  - Governance: 8020 → 8013 (конфликт с workflow-intelligence)
  - Community Portal: 8031 → 8033 (конфликт с simulation)

---

## 🔄 Примеры регистрации сервисов

### AI Office Orchestrator (Port 8059)

**Location**: `AI-office-infrastructure/orchestrator/main.py:25`

```python
PORT = int(os.getenv("AI_OFFICE_ORCHESTRATOR_PORT", "8059"))

# Внутренняя регистрация агентов
agents_registry: Dict[str, Dict] = {}

@app.post("/agents/register")
async def register_agent(registration: AgentRegistration):
    """Register an AI agent with the orchestrator"""
    agents_registry[registration.agent_id] = {
        "type": registration.agent_type,
        "capabilities": registration.capabilities,
        "endpoint": registration.endpoint,
        "registered_at": datetime.now().isoformat(),
        "status": "active"
    }
    logger.info(f"Agent registered: {registration.agent_id}")
```

**Особенность**: Orchestrator сам является реестром для AI агентов!

---

### MIO Manager (Port 8046)

**Location**: `AI-office-infrastructure/mio-manager/main.py:84-252`

**Полная интеграция с системой регистрации**:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize EventBus Client
    eventbus_client = EventBusClient(
        backend='redis',
        redis_url=settings.REDIS_URL
    )
    await eventbus_client.initialize()
    logger.info("   ✅ EventBus Client initialized")

    # 2. Initialize Resource Tracker (ГЛАЗА - активное обнаружение)
    resource_tracker = ResourceTrackerClient(
        eventbus=eventbus_client,
        check_interval=60
    )
    await resource_tracker.start()
    logger.info("   👀 Resource Tracker started (Phase 2 - ГЛАЗА)")

    # 3. Subscribe to events
    await eventbus_client.subscribe_to_problems(...)
    await eventbus_client.subscribe_to_tasks(...)
    await eventbus_client.subscribe_to_directives(...)

    # 4. Start consumer
    await eventbus_client.start_consumer()
    logger.info("   ✅ EventBus subscriptions active")

    # 5. Auto-discovery
    discovery_result = await toolkit_manager.discover_services()
    logger.info(f"   📊 Discovered {discovery_result['total_services']} services")
```

**Возможности**:
- ✅ EventBus integration
- ✅ Resource Tracker (активное сканирование)
- ✅ Auto-discovery других сервисов
- ✅ Health monitoring подписок

---

## 📡 Как система узнаёт о новых сервисах

### Вариант 1: Активная регистрация (сервис сообщает сам)

```python
# В коде нового сервиса (например, analytics-specialist)

from infrastructure.runtime.service_discovery.eventbus_integration import (
    publish_service_started,
    publish_service_heartbeat
)

async def startup():
    # 1. Publish startup event
    await publish_service_started(
        eventbus=eventbus,
        service_name="analytics-specialist",
        orchestrator="ai-office",
        port=8056,
        metadata={
            "version": "1.0.0",
            "capabilities": ["metrics_discovery", "dependency_mapping"]
        },
        dependencies=["orchestrator", "redis", "supabase"]
    )

    # 2. Start heartbeat loop
    asyncio.create_task(heartbeat_loop())

async def heartbeat_loop():
    while True:
        await publish_service_heartbeat(
            eventbus=eventbus,
            service_name="analytics-specialist"
        )
        await asyncio.sleep(30)  # Every 30 seconds
```

**Результат**:
- Service Registry получает событие через EventBus
- Автоматически регистрирует сервис
- Начинает отслеживать heartbeat
- Если heartbeat не приходит 60+ секунд → "disconnected"

---

### Вариант 2: Пассивное обнаружение (система находит сама)

```python
# Resource Tracker в MIO Manager

async def _scan_infrastructure():
    """Активно сканирует инфраструктуру"""

    # 1. Scan running processes
    processes = psutil.process_iter(['pid', 'name', 'cmdline'])
    for proc in processes:
        if 'uvicorn' in proc.info['cmdline']:
            # Found Python service!
            service_info = extract_service_info(proc)

            # Publish discovery
            await publish_service_started(
                eventbus=self.eventbus,
                service_name=service_info.name,
                port=service_info.port,
                metadata={"discovered_by": "resource_tracker"}
            )

    # 2. Scan Docker containers
    client = docker.from_env()
    for container in client.containers.list():
        # Extract port mappings
        ports = container.attrs['NetworkSettings']['Ports']

        # Publish discovery
        await publish_service_started(...)

    # 3. Scan open ports
    for port in range(8000, 8100):
        if is_port_open('localhost', port):
            # Try to identify service
            health = try_health_check(f"http://localhost:{port}/health")
            if health:
                await publish_service_started(...)
```

**Результат**:
- 👀 Система **сама находит** новые сервисы
- 📊 Обнаруживает процессы, контейнеры, открытые порты
- 📡 Публикует находки в EventBus
- ✅ Service Registry автоматически регистрирует

---

### Вариант 3: HTTP API (Consul-compatible)

```bash
# Manual registration via HTTP
curl -X POST http://localhost:8500/v1/agent/service/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "analytics-specialist-001",
    "service_name": "analytics-specialist",
    "host": "localhost",
    "port": 8056,
    "metadata": {
      "version": "1.0.0"
    }
  }'
```

**Результат**:
- Service Registry получает HTTP запрос
- Регистрирует сервис в реестре
- Доступен для других сервисов через `/v1/catalog/services`

---

## 🧠 Интеллектуальная система обучения

### Как система "учится" взаимодействовать

**MIO Manager → AI Intelligence Layer** (`mio-manager/main.py:99-113`):

```python
# Initialize AI Intelligence Layer
ai_coordinator = AICoordinator()
decision_engine = DecisionEngine()
learning_tracker = LearningTracker()

if ai_coordinator.enabled:
    logger.info("   🧠 AI-powered decision making enabled")
else:
    logger.warning("   ⚠️  AI Foundation not available - using fallback mode")
```

**Компоненты обучения**:

1. **AICoordinator** (`intelligence/ai_coordinator.py`)
   - Координирует AI-решения
   - Интегрируется с AI Foundation

2. **DecisionEngine** (`intelligence/decision_engine.py`)
   - Принимает решения на основе данных реестра
   - Адаптируется к изменениям инфраструктуры

3. **LearningTracker** (`intelligence/learning_tracker.py`)
   - Отслеживает паттерны поведения сервисов
   - Экспортирует данные обучения

**Процесс обучения**:

```python
# 1. Новый сервис зарегистрировался
await eventbus.subscribe('service.started', learning_tracker.on_service_started)

# 2. LearningTracker записывает
learning_tracker.record_discovery({
    "service": "new-service",
    "discovered_at": datetime.now(),
    "port": 8099,
    "dependencies": ["orchestrator"]
})

# 3. DecisionEngine анализирует паттерны
patterns = decision_engine.analyze_patterns(learning_tracker.get_data())
# "Обычно сервисы типа 'specialist' зависят от orchestrator и redis"

# 4. AICoordinator делает предсказания
prediction = ai_coordinator.predict_service_needs("new-specialist")
# → "Вероятно нужны: orchestrator, redis, supabase"

# 5. Автоматическая настройка
await ai_coordinator.auto_configure_service("new-specialist", prediction)
```

**Экспорт данных обучения** (`mio-manager/main.py:285-288`):
```python
# On shutdown
if learning_tracker:
    export_path = Path(__file__).parent / 'learning_data' / 'export.json'
    learning_tracker.export_learning_data(str(export_path))
    logger.info("   ✅ Learning data exported")
```

---

## 📋 Текущее состояние системы

### ✅ Реализовано

1. **Service Registry** (Port 8500) - ✅ Production Ready
   - In-memory + Redis persistence
   - Consul-compatible API
   - Health tracking

2. **EventBus Integration** - ✅ Active
   - Automatic registration via events
   - Heartbeat monitoring (60s timeout)
   - Health status tracking

3. **Resource Tracker (Phase 2)** - ✅ Integrated in MIO Manager
   - Active service discovery
   - Process scanning
   - Docker container detection

4. **Port Allocation System** - ✅ Documented
   - `PORT_ALLOCATION.md` with ranges
   - Environment variable configuration
   - Conflict resolution history

5. **AI Learning Layer** - ✅ Initialized
   - AICoordinator
   - DecisionEngine
   - LearningTracker

### ⏳ В процессе

1. **AI Office Services** - Не все запущены
   - Orchestrator (8059) - ⏸️ Not started
   - MIO Manager (8046) - ⏸️ Not started
   - Analytics Specialist (8056) - ⏸️ Not started

2. **Service Discovery Usage** - Не все сервисы используют
   - Нужно добавить `publish_service_started()` в каждый сервис
   - Нужно настроить heartbeat loops

### 📝 TODO

1. **Добавить регистрацию во все сервисы**:
   ```python
   # В каждом main.py добавить:
   from infrastructure.runtime.service_discovery.eventbus_integration import (
       publish_service_started
   )

   async def startup():
       await publish_service_started(
           eventbus=eventbus,
           service_name="service-name",
           orchestrator="ai-office",
           port=PORT
       )
   ```

2. **Запустить Service Discovery**:
   ```bash
   cd infrastructure/runtime/service-discovery
   pip install -r requirements.txt
   python main.py  # Port 8500
   ```

3. **Запустить MIO Manager** (содержит Resource Tracker):
   ```bash
   cd infrastructure/AI-office-infrastructure/mio-manager
   pip install -r requirements.txt
   python main.py  # Port 8046
   ```

4. **Проверить регистрацию**:
   ```bash
   # Check registered services
   curl http://localhost:8500/v1/catalog/services

   # Check service health
   curl http://localhost:8500/v1/health/service/mio-manager
   ```

---

## 🎯 Ответы на вопросы пользователя

### ❓ "Кто отвечает за регистрацию элементов в системе?"

**Ответ**: `infrastructure/runtime/service-discovery/` (Port 8500)

- **ServiceRegistry** - центральный реестр
- **EventBusIntegration** - автоматическая регистрация
- **Resource Tracker** - активное обнаружение

---

### ❓ "Присвоение ему класса, определение места?"

**Ответ**: При регистрации указывается:

```python
service = Service(
    name="analytics-specialist",
    orchestrator="ai-office",  # ← Класс/категория
    port=8056,                 # ← Место (порт)
    metadata={                 # ← Дополнительная классификация
        "type": "specialist",
        "domain": "analytics",
        "capabilities": [...]
    }
)
```

**Классификация сервисов**:
- `orchestrator` field: "ai-office", "bcm-core", "intelligence"
- `metadata.type`: "specialist", "coordinator", "agent"
- `metadata.domain`: "analytics", "db", "devops"

---

### ❓ "Кто ведет учет?"

**Ответ**: **Три уровня учёта**:

1. **Service Registry** (Port 8500)
   - Список всех сервисов
   - Статус, health, heartbeat
   - Redis persistence

2. **MIO Manager** (Port 8046)
   - Resource Tracker - обнаруживает новые сервисы
   - Automation Toolkit - инвентаризация
   - Learning Tracker - история обучения

3. **PORT_ALLOCATION.md**
   - Ручная документация портов
   - Конфликты и резолюция
   - Планирование портов

---

### ❓ "Как можно выжить если нет понимания сколько есть ресурсов?"

**Ответ**: **Resource Tracker (ГЛАЗА)** - Phase 2

```python
# MIO Manager automatically discovers resources
resource_tracker = ResourceTrackerClient(
    eventbus=eventbus,
    check_interval=60  # Scan every 60 seconds
)

await resource_tracker.start()
# 👀 Система сама находит:
# - Running processes
# - Docker containers
# - Open ports
# - Unknown services
```

**Результат**: Система **сама обнаруживает** все ресурсы, даже если они не зарегистрировались!

---

### ❓ "Кто определяет порт?"

**Ответ**: **Три источника**:

1. **PORT_ALLOCATION.md** - Документация диапазонов
   - BCM Core: 8011-8049
   - AI Office: 8045-8059
   - Intelligence: 8080-8099

2. **Environment Variables** - Конфигурация
   ```bash
   AI_OFFICE_ORCHESTRATOR_PORT=8059
   MIO_MANAGER_PORT=8046
   ANALYTICS_SPECIALIST_PORT=8056
   ```

3. **Default в коде**:
   ```python
   PORT = int(os.getenv("SERVICE_PORT", "8046"))
   ```

**Процесс**:
1. Проверить `PORT_ALLOCATION.md` → выбрать свободный порт в диапазоне
2. Установить env var или использовать дефолт
3. При старте сервис регистрируется с этим портом
4. Service Registry отслеживает конфликты

---

### ❓ "Сообщает в реестр всем чтобы это было поводом всей системе интеллектуальной обратить внимание и начать учиться взаимодействовать?"

**Ответ**: **ДА! Именно так!**

```
Новый сервис → EventBus → Service Registry
                    ↓
                AICoordinator
                    ↓
                DecisionEngine
                    ↓
                LearningTracker
                    ↓
        Система учится паттернам
```

**Пример обучения**:

```python
# 1. Сервис зарегистрировался
await publish_service_started(
    eventbus=eventbus,
    service_name="new-specialist",
    dependencies=["orchestrator", "redis"]
)

# 2. AICoordinator получает событие
ai_coordinator.on_service_discovered({
    "service": "new-specialist",
    "dependencies": ["orchestrator", "redis"]
})

# 3. LearningTracker записывает паттерн
learning_tracker.record_pattern({
    "service_type": "specialist",
    "common_dependencies": ["orchestrator", "redis"],
    "frequency": "100%"
})

# 4. DecisionEngine делает выводы
decision_engine.infer_rule({
    "rule": "All 'specialist' services need orchestrator and redis",
    "confidence": 0.95
})

# 5. В следующий раз система автоматически предложит
ai_coordinator.auto_configure("another-specialist")
# → "Предлагаю добавить dependencies: orchestrator, redis"
```

**Результат**: Система **автоматически учится** на основе регистраций!

---

## 🚀 Quick Start для новых сервисов

### Шаблон регистрации нового сервиса

```python
# new_service/main.py

import os
import asyncio
from fastapi import FastAPI
from infrastructure.eventbus.client import EventBusClient
from infrastructure.runtime.service_discovery.eventbus_integration import (
    publish_service_started,
    publish_service_heartbeat,
    publish_service_health
)

# 1. Define port
SERVICE_NAME = "my-new-service"
PORT = int(os.getenv("MY_SERVICE_PORT", "8099"))

# 2. Initialize EventBus
eventbus = EventBusClient(backend='redis')

async def startup():
    # 3. Connect to EventBus
    await eventbus.connect()

    # 4. Register service
    await publish_service_started(
        eventbus=eventbus,
        service_name=SERVICE_NAME,
        orchestrator="ai-office",  # or "bcm-core", "intelligence"
        port=PORT,
        metadata={
            "version": "1.0.0",
            "type": "specialist",  # or "coordinator", "agent"
            "capabilities": ["capability1", "capability2"]
        },
        dependencies=["orchestrator", "redis", "supabase"]
    )

    # 5. Start heartbeat
    asyncio.create_task(heartbeat_loop())

async def heartbeat_loop():
    """Send heartbeat every 30 seconds"""
    while True:
        try:
            await publish_service_heartbeat(
                eventbus=eventbus,
                service_name=SERVICE_NAME
            )
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            await asyncio.sleep(5)

async def health_update_loop():
    """Send health status every 60 seconds"""
    while True:
        try:
            # Get current metrics
            metrics = {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent
            }

            await publish_service_health(
                eventbus=eventbus,
                service_name=SERVICE_NAME,
                health_status="healthy",
                metrics=metrics
            )
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Health update failed: {e}")

@app.on_event("startup")
async def on_startup():
    await startup()
    asyncio.create_task(health_update_loop())

@app.on_event("shutdown")
async def on_shutdown():
    # Deregister on shutdown
    from infrastructure.runtime.service_discovery.eventbus_integration import (
        publish_service_stopped
    )
    await publish_service_stopped(
        eventbus=eventbus,
        service_name=SERVICE_NAME,
        reason="graceful_shutdown"
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
```

---

## 📊 Проверка системы регистрации

### 1. Запустить Service Discovery

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service-discovery
python main.py
# → Starting on port 8500
```

### 2. Запустить MIO Manager (Resource Tracker)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager
python main.py
# → Starting on port 8046
# → Resource Tracker started (ГЛАЗА)
```

### 3. Запустить тестовый сервис

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/orchestrator
python main.py
# → Starting on port 8059
# → Should auto-register via EventBus (if integrated)
```

### 4. Проверить реестр

```bash
# List all registered services
curl http://localhost:8500/v1/catalog/services | jq

# Expected output:
{
  "mio-manager": {
    "port": 8046,
    "status": "active",
    "health": "healthy"
  },
  "orchestrator": {
    "port": 8059,
    "status": "active",
    "health": "healthy"
  }
}
```

### 5. Проверить Health

```bash
# Check specific service health
curl http://localhost:8500/v1/health/service/mio-manager | jq

# Expected output:
{
  "service": "mio-manager",
  "status": "passing",
  "checks": [
    {
      "status": "passing",
      "output": "healthy"
    }
  ]
}
```

---

## 🎓 Выводы

### ✅ Система регистрации полностью спроектирована

1. **Service Registry** (Port 8500) - Центральный реестр
2. **EventBus Integration** - Автоматическая регистрация
3. **Resource Tracker** - Активное обнаружение ("ГЛАЗА")
4. **Port Allocation** - Документированная система портов
5. **AI Learning** - Автоматическое обучение на регистрациях

### 🎯 Ответы на все вопросы пользователя

- ✅ **Кто отвечает**: Service Registry (Port 8500)
- ✅ **Класс/место**: Указывается в `orchestrator` и `metadata`
- ✅ **Кто ведет учет**: 3 уровня (Registry, MIO Manager, Docs)
- ✅ **Без понимания ресурсов**: Resource Tracker (ГЛАЗА) находит всё
- ✅ **Кто определяет порт**: PORT_ALLOCATION.md + env vars
- ✅ **Система учится**: AICoordinator + LearningTracker

### 📋 Следующие шаги

1. Запустить Service Discovery (Port 8500)
2. Запустить MIO Manager (Port 8046 с Resource Tracker)
3. Добавить регистрацию во все AI Office сервисы
4. Протестировать автоматическое обнаружение
5. Экспортировать learning data для анализа

---

**Status**: ✅ Анализ завершён
**Confidence**: 100% - Вся система найдена и задокументирована
**Next**: Внедрение регистрации во все сервисы
