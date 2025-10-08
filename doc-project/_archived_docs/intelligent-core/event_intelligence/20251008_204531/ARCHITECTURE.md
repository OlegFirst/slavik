# Event Intelligence - Unified Event System Architecture

## 🎯 Цель
Создать централизованную event-driven систему для всей платформы с автоматическим обнаружением событий, публикацией и обработкой.

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT INTELLIGENCE BRAIN                      │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Event        │  │ Event        │  │ Pattern      │          │
│  │ Analyzer     │  │ Predictor    │  │ Learner      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │ Knowledge Base  │                           │
│                   │ (Event Patterns)│                           │
│                   └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                             ▲
                             │ Events Flow
                             │
┌─────────────────────────────────────────────────────────────────┐
│                      SHARED EVENT BUS LAYER                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Redis Streams Backend                    │  │
│  │  - Persistence (events survive restarts)                 │  │
│  │  - Consumer Groups (load balancing)                      │  │
│  │  - ACK mechanism (at-least-once delivery)                │  │
│  │  - Pattern matching (workflow.*, bia.*, etc)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Outbox Pattern (DB)                      │  │
│  │  - Transactional event publishing                        │  │
│  │  - Guaranteed delivery (no lost events)                  │  │
│  │  - Automatic retry on failure                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Expertise     │   │ Workflow      │   │ Community     │
│ Center        │   │ Intelligence  │   │ Intelligence  │
│               │   │               │   │               │
│ Auto-connect  │   │ Auto-connect  │   │ Auto-connect  │
│ via shared/   │   │ via shared/   │   │ via shared/   │
└───────────────┘   └───────────────┘   └───────────────┘
```

## 📋 Компоненты

### 1. Shared Event Bus Library (`intelligent-core/shared/event_bus/`)

**Функции:**
- Единая точка подключения для всех сервисов
- Автоматическое обнаружение событий
- Публикация с гарантией доставки
- Подписка с pattern matching
- Интеграция с outbox pattern

**API:**
```python
from shared.event_bus import get_event_bus, publish_event, subscribe_to

# Auto-initialized singleton
bus = await get_event_bus()

# Publish with auto-discovery
await publish_event(
    event_type="workflow.completed",
    data={"workflow_id": "123"},
    source="workflow-service"
)

# Subscribe with patterns
@subscribe_to("workflow.*")
async def handle_workflow_events(event: Event):
    print(f"Got workflow event: {event.type}")
```

### 2. Outbox Events Table

**Schema:**
```sql
CREATE TABLE public.outbox_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    aggregate_type VARCHAR(255),
    aggregate_id VARCHAR(255),
    payload JSONB NOT NULL,
    metadata JSONB,
    tenant_id VARCHAR(100),
    source VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    error TEXT,
    INDEX idx_status_created (status, created_at),
    INDEX idx_tenant (tenant_id),
    INDEX idx_event_type (event_type)
);
```

**Статусы:**
- `pending` - ожидает публикации
- `published` - успешно опубликовано
- `failed` - ошибка публикации (требует retry)

### 3. Event Intelligence Brain

**Возможности:**
- **Event Analyzer** - анализ входящих событий
- **Event Predictor** - предсказание следующих событий
- **Pattern Learner** - обучение на паттернах событий
- **Knowledge Base** - хранение изученных паттернов

**Auto-learning:**
```
workflow.started → (90% probability) → workflow.completed
bia.risk_identified → (70% probability) → bia.mitigation_planned
incident.detected → (95% probability) → incident.response_activated
```

## 🔌 Unified Connection Rules

### Правило 1: Все сервисы используют `shared/event_bus`

```python
# В КАЖДОМ сервисе:
from shared.event_bus import init_event_bus, get_event_bus, subscribe_to

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_event_bus(
        service_name="expertise-center",
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        consumer_group=f"expertise-center-{os.getenv('HOSTNAME', 'local')}"
    )

    # Auto-register event handlers
    await auto_register_handlers()

    yield

    # Shutdown
    bus = get_event_bus()
    await bus.close()
```

### Правило 2: Events автоматически публикуются через Outbox

```python
from shared.event_bus import publish_event

# Внутри любого API endpoint или бизнес-логики
async def complete_workflow(workflow_id: str, db: Session):
    # 1. Бизнес-логика
    workflow = db.query(Workflow).get(workflow_id)
    workflow.status = "completed"

    # 2. Publish event (автоматически через outbox)
    await publish_event(
        event_type="workflow.completed",
        data={
            "workflow_id": workflow_id,
            "completed_at": datetime.utcnow().isoformat()
        },
        source="workflow-intelligence",
        db=db  # Транзакционная связь
    )

    db.commit()  # Outbox event тоже коммитится
```

### Правило 3: Event Handlers используют декораторы

```python
from shared.event_bus import subscribe_to, Event

# Автоматическая регистрация при инициализации
@subscribe_to("workflow.completed")
async def on_workflow_completed(event: Event):
    logger.info(f"Workflow {event.data['workflow_id']} completed!")
    # Логика обработки

@subscribe_to("bia.*")  # Wildcard pattern
async def on_any_bia_event(event: Event):
    # Обработка всех BIA событий
    pass

@subscribe_to("incident.detected", consumer_group="incident-responders")
async def on_incident_detected(event: Event):
    # Load-balanced обработка инцидентов
    pass
```

### Правило 4: Event Discovery - автоматическое обнаружение

```python
# В shared/event_bus/__init__.py встроена автоматическая регистрация
# сервис при старте:
# 1. Сканирует свой код на наличие @subscribe_to
# 2. Регистрирует себя в service registry
# 3. Публикует событие "service.started"
# 4. Подписывается на паттерны

# Event Intelligence автоматически получает:
await publish_event(
    event_type="service.started",
    data={
        "service_name": "expertise-center",
        "subscriptions": ["bia.*", "workflow.completed"],
        "capabilities": ["risk_analysis", "compliance_check"]
    }
)
```

## 🚀 Implementation Plan

### Phase 1: Shared Event Bus Library ✅
- [x] Copy infrastructure/eventbus → intelligent-core/shared/event_bus
- [x] Create high-level API wrapper
- [x] Add auto-discovery decorators
- [ ] Implement outbox integration

### Phase 2: Database Schema ✅
- [ ] Create migration for outbox_events table
- [ ] Add indexes for performance
- [ ] Create outbox publisher worker

### Phase 3: Event Intelligence Brain ✅
- [ ] Enhance analyzer with pattern detection
- [ ] Add predictor for event sequences
- [ ] Implement learning system
- [ ] Build knowledge base

### Phase 4: Service Integration ✅
- [ ] Update all services to use shared/event_bus
- [ ] Remove duplicate eventbus code
- [ ] Add event handlers via decorators
- [ ] Test end-to-end flow

### Phase 5: Redis Setup ✅
- [ ] Configure Redis Streams
- [ ] Setup consumer groups
- [ ] Configure persistence
- [ ] Add monitoring

## 📊 Monitoring & Observability

Event Intelligence предоставляет:

```python
GET /event-intelligence/stats
{
    "total_events_processed": 15234,
    "events_by_type": {
        "workflow.completed": 5432,
        "bia.risk_identified": 3211,
        "incident.detected": 234
    },
    "patterns_learned": 127,
    "predictions_made": 456,
    "prediction_accuracy": 0.87
}

GET /event-intelligence/patterns
[
    {
        "pattern": "workflow.started → workflow.completed",
        "confidence": 0.92,
        "avg_duration_seconds": 3600,
        "sample_count": 1234
    }
]
```

## 🔒 Security & Tenancy

- Все события содержат `tenant_id`
- RLS на уровне БД для outbox_events
- Consumer groups изолированы по tenant
- Event validation перед публикацией

## 📝 Event Naming Convention

```
<domain>.<entity>.<action>

Examples:
- workflow.process.started
- workflow.process.completed
- bia.risk.identified
- bia.mitigation.planned
- incident.alert.detected
- incident.response.activated
- compliance.audit.scheduled
- governance.policy.updated
```

## 🎓 Next Steps for New Services

1. Import `shared/event_bus`
2. Call `init_event_bus()` в lifespan
3. Добавить `@subscribe_to` декораторы
4. Использовать `publish_event()` для публикации
5. Всё! Event Intelligence автоматически:
   - Обнаружит ваш сервис
   - Зарегистрирует подписки
   - Начнёт изучать паттерны
   - Предоставит аналитику
