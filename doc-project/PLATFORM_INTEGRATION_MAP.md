# 🗺️ PLATFORM INTEGRATION MAP
## Как все компоненты взаимодействуют друг с другом

**Дата:** 2025-10-13
**Версия:** 1.0.0
**Статус:** ✅ Complete Integration Architecture

---

## 🎯 ПРОБЛЕМА

Все решения создавались параллельно:
- ✅ **scenario-intelligence** (Intelligent Core)
- ✅ **simulation-service** (Platform Services)
- ✅ **7 integration adapters**
- ✅ **ai-orchestration**
- ✅ **workflow-intelligence**
- ✅ и т.д...

**Вопрос:** Как организовать правильно, чтобы они могли использовать друг друга и взаимодействовать?

---

## 🏗️ АРХИТЕКТУРНЫЕ СЛОИ

### Layer 0: Infrastructure 🔧
```
┌─────────────────────────────────────────────────┐
│  Infrastructure Layer                            │
├─────────────────────────────────────────────────┤
│  - PostgreSQL (Port 5432) - Primary Database    │
│  - Redis (Port 6379) - Cache & Message Queue    │
│  - EventBus (Port 8055) - Event Choreography    │
│  - Service Discovery (Port 8500) - Consul       │
│  - Secrets Manager (Port 8200) - Vault          │
│  - API Gateway (Port 8000) - Entry Point        │
└─────────────────────────────────────────────────┘
```

**Правило:** Все сервисы ОБЯЗАНЫ использовать Infrastructure Layer.

---

### Layer 1: AI Office 🤖
```
┌─────────────────────────────────────────────────┐
│  AI Office Layer (Координация агентов)          │
├─────────────────────────────────────────────────┤
│  - Agent Router (8033) - Маршрутизация задач    │
│  - Orchestrator (8026) - Координация агентов    │
│  - Project Agent (8034) - Управление проектами  │
│  - DevOps Agent (8035) - CI/CD & Infrastructure │
│  - Analytics Specialist (8036) - Аналитика      │
└─────────────────────────────────────────────────┘
```

**Правило:** AI Office используют только Infrastructure Layer.

---

### Layer 2: Intelligent Core 🧠
```
┌─────────────────────────────────────────────────┐
│  Intelligent Core (Интеллект платформы)         │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │ 🎭 scenario-intelligence (Port 8060)      │  │
│  │ - 652 сценария (4 уровня)                │  │
│  │ - 7 integration adapters                  │  │
│  │ - Auto-Generator                          │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │ 🔮 predictive-intelligence (8030)         │  │
│  │ 🤝 community-intelligence (8040)          │  │
│  │ 🎼 ai-orchestration (8026)                │  │
│  │ 📊 event-intelligence (8035)              │  │
│  │ 🏥 system-bcm-service (8050)              │  │
│  │ 🔄 workflow-intelligence (8037)           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Правило:** Intelligent Core может использовать:
- ✅ Infrastructure Layer
- ✅ AI Office Layer (через orchestrator)
- ✅ Друг друга (через adapters)

---

### Layer 3: Platform Services 🚀
```
┌─────────────────────────────────────────────────┐
│  Platform Services (Бизнес-сервисы)             │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │ 🎬 simulation-service (Port 8095)         │  │
│  │ - 4 simulation engines                    │  │
│  │ - TheHive integration                     │  │
│  │ - BCM exercises                           │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │ 📱 Admin Control Center (3000)            │  │
│  │ 🖥️  Admin Panel (3001)                    │  │
│  │ 👥 User Dashboard (3002)                  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Правило:** Platform Services могут использовать:
- ✅ Infrastructure Layer
- ✅ Intelligent Core (через API)
- ✅ Друг друга (через API)

---

## 🔗 INTEGRATION PATTERNS

### Pattern 1: EventBus Choreography (Асинхронная связь)

**Используют:** ВСЕ сервисы

```python
# Пример: scenario-intelligence публикует событие
from integration.eventbus_integration import EventBusClient

eventbus = EventBusClient()
await eventbus.publish(
    event_type="scenario.execution.completed",
    payload={
        "scenario_id": "scenario-123",
        "result": "success",
        "duration_ms": 1234
    },
    priority="normal"
)

# simulation-service подписывается на событие
async def handle_scenario_completed(event):
    """Создать симуляцию на основе сценария"""
    scenario_id = event["payload"]["scenario_id"]
    # Create simulation based on scenario result
    ...

await eventbus.subscribe(
    event_type="scenario.execution.completed",
    handler=handle_scenario_completed
)
```

**Когда использовать:**
- ✅ Асинхронная связь (fire-and-forget)
- ✅ Один источник → Много подписчиков
- ✅ Не требуется немедленный ответ
- ✅ Event-driven workflows

---

### Pattern 2: Direct API Calls (Синхронная связь)

**Используют:** Сервисы с прямыми зависимостями

```python
# scenario-intelligence вызывает predictive-intelligence
from integration import get_predictive_adapter

adapter = get_predictive_adapter()
prediction = await adapter.predict_scenario_failure(
    scenario_id="scenario-123",
    historical_data={...}
)

# Returns: {probability: 0.15, confidence: 0.85, factors: [...]}
```

**Когда использовать:**
- ✅ Синхронная связь (request-response)
- ✅ Требуется немедленный ответ
- ✅ Прямая зависимость между сервисами
- ✅ Простые запросы (GET, POST)

---

### Pattern 3: Workflow Orchestration (Temporal)

**Используют:** Long-running processes

```python
# scenario-intelligence запускает workflow в Temporal
from integration import get_workflow_adapter

adapter = get_workflow_adapter()
result = await adapter.execute_scenario_as_workflow(
    scenario_id="scenario-123",
    context={...}
)

# Temporal обеспечивает:
# - Durable execution (переживает рестарты)
# - Automatic retries
# - Saga pattern (compensation)
# - Versioning
```

**Когда использовать:**
- ✅ Long-running workflows (>1 минута)
- ✅ Требуется durable execution
- ✅ Нужны retries и compensation
- ✅ Multi-step processes

---

### Pattern 4: Database Integration (Shared Database)

**Используют:** Все сервисы для персистентности

```python
# scenario-intelligence сохраняет сценарий
from integration.database_integration import get_database_manager

db = get_database_manager()
async with db.session() as session:
    scenario = Scenario(
        scenario_id="scenario-123",
        name="BIA Analysis Test",
        level=1
    )
    await db.create(session, scenario)
    await session.commit()

# simulation-service читает сценарий
async with db.session() as session:
    scenario = await db.get_by_id(session, Scenario, "scenario-123")
    # Create simulation based on scenario
```

**Когда использовать:**
- ✅ Персистентность данных
- ✅ Транзакционные операции
- ✅ Сложные запросы (JOINs, aggregations)
- ✅ Shared state между сервисами

**⚠️ Осторожно:** Не создавать tight coupling через shared database!

---

## 🔄 КОНКРЕТНЫЕ ИНТЕГРАЦИИ

### 1. scenario-intelligence ↔ simulation-service

**Направление 1:** scenario-intelligence → simulation-service

```python
# Scenario Intelligence генерирует L3 сценарий
scenario = {
    "level": 3,
    "type": "functional",
    "name": "BIA Process Test",
    "steps": [...]
}

# Публикует событие
await eventbus.publish(
    event_type="scenario.generated.l3",
    payload={
        "scenario_id": scenario["id"],
        "scenario_data": scenario
    }
)

# simulation-service подписывается
async def convert_scenario_to_exercise(event):
    scenario_data = event["payload"]["scenario_data"]

    # Создать BCM exercise из сценария
    exercise = await simulation_service.create_exercise(
        scenario_id=scenario_data["id"],
        exercise_type="bcm_drill",
        duration_minutes=240
    )

    # Опубликовать обратно
    await eventbus.publish(
        event_type="exercise.created",
        payload={"exercise_id": exercise["id"]}
    )
```

**Направление 2:** simulation-service → scenario-intelligence

```python
# simulation-service завершил симуляцию
simulation_result = {
    "simulation_id": "sim-123",
    "scenario_id": "scenario-123",
    "success": True,
    "metrics": {
        "effectiveness": 0.85,
        "duration_ms": 12000
    }
}

# Публикует событие
await eventbus.publish(
    event_type="simulation.completed",
    payload=simulation_result
)

# scenario-intelligence подписывается для обучения
async def learn_from_simulation(event):
    result = event["payload"]

    # Обновить паттерны на основе результата
    await pattern_detector.update_patterns(
        scenario_id=result["scenario_id"],
        effectiveness=result["metrics"]["effectiveness"]
    )

    # Улучшить Auto-Generator
    await auto_generator.learn_from_result(result)
```

---

### 2. scenario-intelligence ↔ predictive-intelligence

**Используется:** Direct API calls через adapter

```python
# scenario-intelligence/integration/predictive_adapter.py
class ScenarioPredictiveAdapter:
    def __init__(self):
        self.predictive_url = "http://predictive-intelligence:8030"

    async def predict_scenario_failure(self, scenario_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.predictive_url}/api/v1/predict",
                json={
                    "scenario_id": scenario_id,
                    "prediction_type": "failure"
                }
            )
            return response.json()

# Usage в scenario-intelligence
from integration import get_predictive_adapter

adapter = get_predictive_adapter()
prediction = await adapter.predict_scenario_failure("scenario-123")

if prediction["probability"] > 0.5:
    # Сценарий вероятно упадет, нужна оптимизация
    optimization = await adapter.get_optimization_suggestions("scenario-123")
```

---

### 3. scenario-intelligence ↔ workflow-intelligence

**Используется:** Temporal workflows + Direct API

```python
# Вариант 1: Через Temporal (для long-running)
from integration import get_workflow_adapter

adapter = get_workflow_adapter()
result = await adapter.execute_scenario_as_workflow(
    scenario_id="scenario-123",
    context={"timeout_seconds": 3600}
)

# Вариант 2: Через API (для analytics)
from integration import get_workflow_intel_adapter

adapter = get_workflow_intel_adapter()

# Process mining
flow = await adapter.analyze_execution_flow(
    scenario_id="scenario-123",
    time_window="7d"
)

# Найти bottlenecks
for bottleneck in flow["bottlenecks"]:
    print(f"Узкое место: {bottleneck['step_id']}, "
          f"avg_duration={bottleneck['avg_duration_ms']}ms")

# Оптимизация
optimizations = await adapter.optimize_scenario("scenario-123")
```

---

### 4. scenario-intelligence ↔ ai-orchestration

**Используется:** Task delegation через adapter

```python
# scenario-intelligence делегирует AI задачу
from integration import get_orchestration_adapter

adapter = get_orchestration_adapter()

# Делегировать BIA analysis AI агенту
task = await adapter.delegate_to_ai(
    task_type="bia_analysis",
    scenario_context={
        "scenario_id": "scenario-123",
        "organization_type": "hospital",
        "business_processes": [...]
    },
    priority="high"
)

# Ждать результата (с таймаутом)
result = await adapter.wait_for_result(
    task_id=task["task_id"],
    timeout=300  # 5 минут
)

if result["completed"]:
    # Использовать AI результат в сценарии
    ai_recommendations = result["result"]["recommendations"]
```

---

### 5. scenario-intelligence ↔ system-bcm-service

**Используется:** Framework-specific scenarios

```python
# scenario-intelligence загружает ISO 22301 сценарии
from integration import get_bcm_adapter

adapter = get_bcm_adapter()

# Загрузить все сценарии для ISO 22301
iso_scenarios = await adapter.load_framework_scenarios("ISO_22301")

# Зарегистрировать их в scenario-intelligence
for scenario in iso_scenarios:
    await scenario_registry.register(scenario)

# Валидация compliance
compliance = await adapter.validate_bcm_compliance(
    scenario_id="scenario-123",
    iso_clause="8.2.2"  # Business Continuity Strategy
)

if not compliance["compliant"]:
    # Показать пробелы
    for gap in compliance["gaps"]:
        print(f"Gap: {gap}")
```

---

### 6. scenario-intelligence ↔ community-intelligence

**Используется:** Collective recommendations

```python
# scenario-intelligence запрашивает community рекомендацию
from integration import get_community_adapter

adapter = get_community_adapter()

# Коллективное решение
recommendation = await adapter.get_community_recommendation(
    scenario_id="scenario-123",
    context={"organization": "hospital", "size": "large"},
    agents=["all"]  # Все агенты участвуют
)

if recommendation["consensus"] == "approve":
    # Community одобрило сценарий
    print(f"Confidence: {recommendation['confidence']}")
    print(f"Votes: {recommendation['votes']}")

# Валидация сценария через community
validation = await adapter.validate_scenario(
    scenario_yaml=scenario_yaml_string,
    validators=["all"]
)

if not validation["approved"]:
    # Применить feedback
    for feedback in validation["feedback"]:
        print(f"Feedback: {feedback}")
```

---

### 7. scenario-intelligence ↔ event-intelligence

**Используется:** Event analysis & anomaly detection

```python
# scenario-intelligence анализирует события выполнения
from integration import get_event_intelligence_adapter

adapter = get_event_intelligence_adapter()

# Анализ событий за последние 24 часа
analysis = await adapter.analyze_scenario_events(
    scenario_id="scenario-123",
    time_window="24h"
)

print(f"Events: {analysis['events_count']}")
print(f"Patterns: {analysis['patterns']}")
print(f"Anomalies: {len(analysis['anomalies'])}")

# Обнаружение аномалий
anomalies = await adapter.detect_anomalies(
    scenario_ids=["scenario-123", "scenario-124", "scenario-125"],
    time_window="24h"
)

for anomaly in anomalies:
    if anomaly["severity"] == "critical":
        # Критическая аномалия - нужно действовать
        print(f"Critical anomaly: {anomaly['description']}")
```

---

## 📊 SERVICE DEPENDENCY MAP

```
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (Port 8000)                      │
│                    ✅ Entry point для всех                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Frontend   │  │  Frontend   │  │  Frontend   │
│  (Admin)    │  │  (Control)  │  │  (User)     │
│  Port 3001  │  │  Port 3000  │  │  Port 3002  │
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────────┐       ┌──────────────────────┐
│ scenario-intelligence│       │  simulation-service  │
│    Port 8060         │◄─────►│    Port 8095         │
└──────────┬───────────┘       └──────────┬───────────┘
           │                              │
           │    ┌──────────┬─────────┐    │
           ├───►│predictive│8030     │    │
           │    └──────────┘         │    │
           │    ┌──────────┬─────────┐    │
           ├───►│community │8040     │    │
           │    └──────────┘         │    │
           │    ┌──────────┬─────────┐    │
           ├───►│orchestr. │8026     │◄───┤
           │    └──────────┘         │    │
           │    ┌──────────┬─────────┐    │
           ├───►│event-int.│8035     │◄───┤
           │    └──────────┘         │    │
           │    ┌──────────┬─────────┐    │
           ├───►│bcm-serv. │8050     │    │
           │    └──────────┘         │    │
           │    ┌──────────┬─────────┐    │
           └───►│workflow  │8037     │◄───┘
                └──────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌──────────┐         ┌──────────┐
    │PostgreSQL│         │  Redis   │
    │Port 5432 │         │Port 6379 │
    └──────────┘         └──────────┘
```

**Легенда:**
- `◄────►` : Двунаправленная связь (API calls + EventBus)
- `──────►` : Однонаправленная связь
- `│` : Зависимость (uses)

---

## 🚦 COMMUNICATION RULES

### Rule 1: EventBus First
**Всегда предпочитать EventBus для асинхронной связи**

✅ **Правильно:**
```python
# Publish event
await eventbus.publish("scenario.completed", payload)

# Subscribe to event
await eventbus.subscribe("scenario.completed", handler)
```

❌ **Неправильно:**
```python
# Direct HTTP call для event notification
await http_client.post("http://service/notify", payload)
```

### Rule 2: Adapters for Direct Calls
**Использовать adapters для прямых API вызовов**

✅ **Правильно:**
```python
from integration import get_predictive_adapter

adapter = get_predictive_adapter()
result = await adapter.predict_scenario_failure(scenario_id)
```

❌ **Неправильно:**
```python
# Direct HTTP call без adapter
response = await http_client.post(
    "http://predictive:8030/api/v1/predict",
    json={"scenario_id": scenario_id}
)
```

### Rule 3: Database Through Manager
**Всегда использовать DatabaseManager для БД**

✅ **Правильно:**
```python
from integration.database_integration import get_database_manager

db = get_database_manager()
async with db.session() as session:
    scenario = await db.get_by_id(session, Scenario, scenario_id)
```

❌ **Неправильно:**
```python
# Direct SQLAlchemy session
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM scenarios")
```

### Rule 4: Temporal for Long-Running
**Использовать Temporal для long-running процессов**

✅ **Правильно:**
```python
from integration import get_workflow_adapter

adapter = get_workflow_adapter()
result = await adapter.execute_scenario_as_workflow(scenario_id)
```

❌ **Неправильно:**
```python
# Long-running task без Temporal (потеряется при рестарте)
async def long_task():
    await asyncio.sleep(3600)  # 1 hour
    return result
```

---

## 📝 INTEGRATION CHECKLIST

Для каждого нового сервиса:

### 1. Infrastructure Layer ✅
- [ ] PostgreSQL connection через DatabaseManager
- [ ] Redis connection для кеширования
- [ ] EventBus subscription/publishing
- [ ] Service Discovery registration (Consul)
- [ ] Secrets Manager integration (Vault)
- [ ] Health checks (/health, /health/live, /health/ready)
- [ ] Metrics endpoint (/metrics - Prometheus)

### 2. Integration Adapters ✅
- [ ] Создать adapters для зависимых сервисов
- [ ] Использовать global instances pattern
- [ ] Graceful error handling с fallback
- [ ] Async/await везде
- [ ] Logging для каждого вызова

### 3. EventBus Events ✅
- [ ] Определить события, которые публикует сервис
- [ ] Определить события, на которые подписывается
- [ ] Документировать event schemas
- [ ] Использовать priority (low/normal/high/critical)
- [ ] Включить correlation_id для tracing

### 4. API Design ✅
- [ ] REST API с FastAPI
- [ ] OpenAPI/Swagger documentation
- [ ] Versioning (/api/v1/...)
- [ ] Authentication (JWT через API Gateway)
- [ ] Rate limiting
- [ ] Input validation (Pydantic)

### 5. Testing ✅
- [ ] Unit tests (pytest)
- [ ] Integration tests (с mock services)
- [ ] E2E tests (real services)
- [ ] Load tests (locust/k6)
- [ ] Contract tests (для API)

### 6. Documentation ✅
- [ ] README.md
- [ ] API documentation
- [ ] Integration guide
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## 🔧 IMPLEMENTATION GUIDE

### Step 1: Setup Infrastructure Clients

**В каждом сервисе создать `/integration/` папку:**

```python
# integration/__init__.py
from .database_integration import get_database_manager
from .eventbus_integration import EventBusClient
from .redis_client import get_redis_client

__all__ = [
    "get_database_manager",
    "EventBusClient",
    "get_redis_client",
]
```

### Step 2: Create Service Adapters

**Пример: scenario-intelligence создает adapter для simulation-service:**

```python
# integration/simulation_adapter.py
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ScenarioSimulationAdapter:
    """Adapter для интеграции с Simulation Service"""

    def __init__(self, simulation_url: str = "http://simulation-service:8095"):
        self.simulation_url = simulation_url
        logger.info(f"Initialized ScenarioSimulationAdapter: {simulation_url}")

    async def convert_scenario_to_exercise(
        self,
        scenario_id: str,
        exercise_type: str = "bcm_drill"
    ) -> Dict[str, Any]:
        """
        Конвертировать L3 сценарий в BCM exercise

        Args:
            scenario_id: ID сценария
            exercise_type: Тип упражнения

        Returns:
            Dict with exercise details
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.simulation_url}/api/v1/exercises/from-scenario",
                    json={
                        "scenario_id": scenario_id,
                        "exercise_type": exercise_type
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Converted scenario {scenario_id} to exercise: "
                        f"exercise_id={result.get('exercise_id', 'N/A')}"
                    )
                    return result
                else:
                    logger.error(
                        f"Simulation Service error: {response.status_code}"
                    )
                    return {"exercise_id": None, "success": False}

        except Exception as e:
            logger.error(f"Failed to convert scenario to exercise: {e}")
            return {"exercise_id": None, "success": False, "error": str(e)}


# Global instance
_adapter: Optional[ScenarioSimulationAdapter] = None


def get_simulation_adapter() -> ScenarioSimulationAdapter:
    """Get global Simulation adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioSimulationAdapter()
    return _adapter
```

**Добавить в `__init__.py`:**

```python
# integration/__init__.py
from .simulation_adapter import ScenarioSimulationAdapter, get_simulation_adapter

__all__ = [
    # ... existing ...
    "ScenarioSimulationAdapter",
    "get_simulation_adapter",
]
```

### Step 3: Subscribe to EventBus Events

**Пример: simulation-service подписывается на scenario события:**

```python
# main.py or event_handlers.py
from integration.eventbus_client import SimulationEventBusClient

eventbus = SimulationEventBusClient()

async def handle_scenario_generated_l3(event: Dict[str, Any]):
    """
    Handle scenario.generated.l3 event

    Когда scenario-intelligence создает L3 сценарий,
    автоматически создаем BCM exercise.
    """
    logger.info(f"Received scenario.generated.l3 event: {event['event_id']}")

    scenario_data = event["payload"]["scenario_data"]
    scenario_id = scenario_data["id"]

    # Создать BCM exercise
    exercise = await create_exercise_from_scenario(
        scenario_id=scenario_id,
        scenario_data=scenario_data
    )

    # Опубликовать событие обратно
    await eventbus.publish(
        event_type="exercise.created",
        payload={
            "exercise_id": exercise["id"],
            "scenario_id": scenario_id,
            "exercise_type": "bcm_drill"
        },
        priority="normal"
    )

    logger.info(f"Created exercise {exercise['id']} from scenario {scenario_id}")


# Subscribe during startup
async def startup():
    await eventbus.connect()

    # Subscribe to scenario events
    await eventbus.subscribe(
        event_type="scenario.generated.l3",
        handler=handle_scenario_generated_l3
    )

    logger.info("✅ Subscribed to scenario.generated.l3 events")
```

### Step 4: Publish Events

**Пример: scenario-intelligence публикует события:**

```python
# execution_engine.py
from integration.eventbus_integration import EventBusClient

eventbus = EventBusClient()

async def execute_scenario(scenario_id: str):
    """Execute scenario and publish events"""

    # Publish start event
    await eventbus.publish(
        event_type="scenario.execution.started",
        payload={
            "scenario_id": scenario_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        priority="normal"
    )

    try:
        # Execute scenario
        result = await _execute_scenario_steps(scenario_id)

        # Publish success event
        await eventbus.publish(
            event_type="scenario.execution.completed",
            payload={
                "scenario_id": scenario_id,
                "result": "success",
                "duration_ms": result["duration_ms"],
                "metrics": result["metrics"]
            },
            priority="normal"
        )

        return result

    except Exception as e:
        # Publish failure event
        await eventbus.publish(
            event_type="scenario.execution.failed",
            payload={
                "scenario_id": scenario_id,
                "error": str(e),
                "error_type": type(e).__name__
            },
            priority="high"  # High priority for failures
        )

        raise
```

---

## 🎯 BEST PRACTICES

### 1. Use Adapters for ALL External Calls

**Never** call external services directly. **Always** use adapters.

### 2. EventBus for Asynchronous Communication

Use EventBus for:
- Event notifications
- Status updates
- Metrics publishing
- Audit logging

### 3. API Calls for Synchronous Communication

Use direct API calls (через adapters) for:
- Request-response patterns
- Data retrieval
- Immediate results needed

### 4. Temporal for Long-Running Workflows

Use Temporal for:
- Processes > 1 minute
- Need durable execution
- Multi-step workflows
- Saga patterns

### 5. Database Manager for All DB Access

Use DatabaseManager for:
- All database operations
- Connection pooling
- Transaction management
- Query optimization

### 6. Graceful Degradation

Always handle failures gracefully:

```python
try:
    result = await external_service.call()
except Exception as e:
    logger.error(f"External service failed: {e}")
    # Return fallback/default value
    result = {"status": "unavailable", "fallback": True}
```

### 7. Correlation IDs for Tracing

Always include correlation_id:

```python
await eventbus.publish(
    event_type="scenario.completed",
    payload={...},
    correlation_id=request.correlation_id  # Pass through
)
```

### 8. Health Checks Everywhere

Every service MUST implement:
- `/health` - Overall health
- `/health/live` - Kubernetes liveness
- `/health/ready` - Kubernetes readiness

---

## 📊 MONITORING & OBSERVABILITY

### Metrics to Collect

**Every service:**
```python
# Request metrics
http_requests_total
http_request_duration_seconds
http_requests_in_progress

# EventBus metrics
eventbus_events_published_total
eventbus_events_consumed_total
eventbus_event_processing_duration_seconds

# Database metrics
db_connections_active
db_query_duration_seconds
db_transactions_total

# Business metrics (custom per service)
scenarios_executed_total
simulations_running
predictions_made_total
```

### Distributed Tracing

Use OpenTelemetry:

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

@app.post("/api/v1/scenarios/execute")
async def execute_scenario(scenario_id: str):
    with tracer.start_as_current_span("execute_scenario"):
        # Your code here
        result = await _execute_scenario(scenario_id)
        return result
```

---

## ✅ SUCCESS CRITERIA

Integration считается успешной когда:

1. ✅ Все сервисы используют Infrastructure Layer
2. ✅ Все сервисы регистрируются в Service Discovery
3. ✅ Все сервисы публикуют/подписываются на EventBus
4. ✅ Все внешние вызовы через adapters
5. ✅ Все health checks работают
6. ✅ Distributed tracing настроен
7. ✅ Metrics собираются в Prometheus
8. ✅ Logs централизованы
9. ✅ E2E тесты проходят
10. ✅ Documentation актуальна

---

## 🚀 NEXT STEPS

### Phase 1: scenario-intelligence ↔ simulation-service (Week 1)

1. ✅ Создать `simulation_adapter.py` в scenario-intelligence
2. 📋 Создать `scenario_client.py` в simulation-service
3. 📋 Настроить EventBus события:
   - `scenario.generated.l3` → `exercise.created`
   - `simulation.completed` → `scenario.learned`
4. 📋 E2E тест полного цикла
5. 📋 Documentation

### Phase 2: Full Intelligent Core Integration (Week 2)

1. 📋 Протестировать все 7 adapters scenario-intelligence
2. 📋 Создать reverse adapters в каждом сервисе
3. 📋 Настроить все EventBus subscriptions
4. 📋 E2E тесты для каждой интеграции
5. 📋 Performance testing

### Phase 3: Platform Services Integration (Week 3)

1. 📋 Frontend → Backend интеграция
2. 📋 API Gateway routing
3. 📋 Authentication flow
4. 📋 Rate limiting
5. 📋 Load testing

### Phase 4: Production Ready (Week 4)

1. 📋 Distributed tracing setup
2. 📋 Centralized logging
3. 📋 Alerting rules
4. 📋 Runbooks
5. 📋 Deployment automation

---

## 📚 REFERENCES

### Documentation
- [EventBus Integration Guide](/infrastructure/runtime/message-queue/README.md)
- [Service Discovery Guide](/infrastructure/runtime/service-discovery/README.md)
- [Database Manager Guide](/infrastructure/database/README.md)
- [API Gateway Guide](/infrastructure/security/api-gateway/README.md)

### Code Examples
- [scenario-intelligence adapters](/intelligent-core/scenario-intelligence/integration/)
- [simulation-service clients](/platform-services/simulation/simulation-service/integration/)

### Architecture Diagrams
- [Platform Architecture](/doc/architecture/PLATFORM_ARCHITECTURE_MAP.md)
- [Service Catalog](/catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml)

---

**Версия:** 1.0.0
**Дата:** 2025-10-13
**Автор:** Claude + MD collaboration
**Статус:** ✅ **COMPLETE - Ready for Implementation**
