# Event Bus Integration Guide

## 🎯 Quick Start - 5 минут до запуска

### Шаг 1: Импорт в вашем main.py

```python
from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to, Event
```

### Шаг 2: Инициализация в lifespan

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_event_bus(
        service_name="your-service-name",  # Уникальное имя вашего сервиса
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
    )

    logger.info("✅ Service started with EventBus")
    yield

    # Shutdown
    bus = get_event_bus()
    if bus:
        await bus.close()

app = FastAPI(lifespan=lifespan, title="Your Service")
```

### Шаг 3: Публикация событий

```python
from shared.event_bus import publish_event

@app.post("/workflows/{workflow_id}/complete")
async def complete_workflow(workflow_id: str):
    # Ваша бизнес-логика
    workflow = update_workflow_status(workflow_id, "completed")

    # Публикация события
    await publish_event(
        event_type="workflow.completed",
        data={
            "workflow_id": workflow_id,
            "completed_at": datetime.utcnow().isoformat(),
            "duration_seconds": workflow.duration
        },
        source="workflow-service",
        tenant_id=workflow.tenant_id
    )

    return {"status": "completed"}
```

### Шаг 4: Подписка на события

```python
from shared.event_bus import subscribe_to, Event

# Подписка на конкретное событие
@subscribe_to("workflow.completed")
async def on_workflow_completed(event: Event):
    logger.info(f"Workflow {event.data['workflow_id']} completed!")

    # Ваша логика обработки
    await send_notification(event.data)


# Подписка на все события workflow
@subscribe_to("workflow.*")
async def on_any_workflow_event(event: Event):
    logger.debug(f"Workflow event: {event.type}")


# Подписка на все события
@subscribe_to("*")
async def log_all_events(event: Event):
    logger.debug(f"Event received: {event.type} from {event.source}")
```

Готово! Ваш сервис теперь интегрирован с EventBus.

---

## 📚 Полное руководство

### Event Naming Convention

Используйте формат: `<domain>.<entity>.<action>`

**Примеры:**
```
workflow.process.started
workflow.process.completed
workflow.stage.changed

bia.risk.identified
bia.risk.assessed
bia.mitigation.planned

incident.alert.detected
incident.response.activated
incident.resolution.completed

compliance.audit.scheduled
compliance.gap.identified

governance.policy.updated
governance.stakeholder.added
```

### Wildcard Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `workflow.completed` | Точное совпадение | `workflow.completed` |
| `workflow.*` | Все workflow события | `workflow.started`, `workflow.completed` |
| `workflow.*.completed` | Workflow с любой сущностью | `workflow.process.completed`, `workflow.stage.completed` |
| `*` | Все события | Любое событие |

### Event Structure

```python
@dataclass
class Event:
    id: str                    # Уникальный UUID
    type: str                  # Тип события (workflow.completed)
    data: Dict[str, Any]       # Полезная нагрузка
    source: str                # Имя сервиса-источника
    timestamp: str             # ISO 8601 timestamp
    tenant_id: Optional[str]   # Идентификатор tenant
    correlation_id: str        # ID для трейсинга связанных событий
    metadata: Dict[str, Any]   # Дополнительные метаданные
```

### Advanced: Consumer Groups

Для load balancing между несколькими экземплярами сервиса:

```python
@subscribe_to("workflow.completed", consumer_group="workflow-processors")
async def process_workflow(event: Event):
    # Только один экземпляр из группы обработает событие
    pass
```

### Advanced: Transactional Events (Outbox Pattern)

Для гарантированной доставки событий:

```python
from shared.event_bus.outbox import save_to_outbox, OutboxPublisher
from sqlalchemy.orm import Session

# В вашем endpoint
@app.post("/workflows")
async def create_workflow(workflow_data: dict, db: Session = Depends(get_db)):
    # Бизнес-логика
    workflow = Workflow(**workflow_data)
    db.add(workflow)

    # Сохранить событие в outbox (в той же транзакции!)
    await save_to_outbox(
        event_type="workflow.created",
        data={"workflow_id": str(workflow.id)},
        source="workflow-service",
        db=db,
        tenant_id=workflow.tenant_id,
        aggregate_type="workflow",
        aggregate_id=str(workflow.id)
    )

    # Коммит - и workflow, и событие сохраняются атомарно
    db.commit()

    return {"id": workflow.id}


# В вашем lifespan - запустить publisher
from shared.event_bus.outbox import OutboxPublisher

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ...инициализация EventBus...

    # Запустить outbox publisher
    publisher = OutboxPublisher(
        db_session_factory=lambda: SessionLocal(),
        poll_interval_seconds=5
    )
    await publisher.start()

    yield

    await publisher.stop()
```

### Correlation IDs для трейсинга

```python
# Первое событие создаёт correlation_id
await publish_event(
    event_type="workflow.started",
    data={"workflow_id": "123"},
    source="workflow-service"
)
# correlation_id автоматически генерируется

# Последующие события используют тот же correlation_id
@subscribe_to("workflow.started")
async def on_workflow_started(event: Event):
    # Используем correlation_id из входящего события
    await publish_event(
        event_type="workflow.validation.started",
        data={"workflow_id": event.data["workflow_id"]},
        source="validation-service",
        correlation_id=event.correlation_id  # Связываем события
    )
```

### Error Handling

```python
@subscribe_to("workflow.*")
async def handle_workflow_event(event: Event):
    try:
        # Ваша логика
        await process_workflow(event.data)

    except Exception as e:
        logger.error(f"Failed to process {event.type}: {e}")

        # Публикация события об ошибке
        await publish_event(
            event_type="workflow.processing.failed",
            data={
                "original_event_id": event.id,
                "error": str(e)
            },
            source="workflow-processor",
            correlation_id=event.correlation_id
        )

        # Не падайте! EventBus автоматически retry
        # Если нужен retry вашей логики - кидайте exception
        raise
```

### Idempotent Handlers

**ВАЖНО**: Обработчики событий должны быть идемпотентными (можно вызывать несколько раз безопасно).

```python
@subscribe_to("workflow.completed")
async def send_completion_email(event: Event):
    workflow_id = event.data["workflow_id"]

    # Проверка - уже отправляли?
    if await email_already_sent(workflow_id):
        logger.info(f"Email already sent for {workflow_id}, skipping")
        return

    # Отправка
    await send_email(workflow_id)

    # Сохранение факта отправки
    await mark_email_sent(workflow_id)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Redis connection
REDIS_URL=redis://localhost:6379

# Optional: Custom stream name
EVENT_STREAM_NAME=platform:events

# Optional: Service-specific consumer group
CONSUMER_GROUP=my-service-group
```

### Redis Setup

```bash
# Запустить Redis (если ещё не запущен)
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes
```

---

## 📊 Monitoring

### Get EventBus Statistics

```python
bus = get_event_bus()
stats = bus.get_stats()

print(f"Published: {stats['published']}")
print(f"Consumed: {stats['consumed']}")
print(f"Errors: {stats['errors']}")
```

### Outbox Statistics

```sql
-- В Postgres
SELECT * FROM get_outbox_stats();

-- Результат:
-- total_events | pending_events | published_events | failed_events | events_with_retries | oldest_pending_age
-- 1234         | 5              | 1200             | 29            | 15                  | 00:05:23
```

### Cleanup Old Events

```sql
-- Удалить события старше 30 дней
SELECT cleanup_outbox_events();
```

---

## 🧪 Testing

### Unit Tests

```python
import pytest
from shared.event_bus import Event, subscribe_to, publish_event

@pytest.mark.asyncio
async def test_event_handler():
    # Mock handler
    events_received = []

    @subscribe_to("test.event")
    async def test_handler(event: Event):
        events_received.append(event)

    # Publish test event
    await publish_event(
        event_type="test.event",
        data={"test": "data"},
        source="test-service"
    )

    # Wait for processing
    await asyncio.sleep(0.1)

    # Assert
    assert len(events_received) == 1
    assert events_received[0].data["test"] == "data"
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_outbox_publish():
    # Create DB session
    db = SessionLocal()

    # Save to outbox
    await save_to_outbox(
        event_type="test.created",
        data={"id": 123},
        source="test-service",
        db=db
    )
    db.commit()

    # Verify saved
    outbox_event = db.query(OutboxEvent).filter_by(event_type="test.created").first()
    assert outbox_event is not None
    assert outbox_event.status == "pending"

    # Publish
    await publish_outbox_events(lambda: SessionLocal())

    # Verify published
    db.refresh(outbox_event)
    assert outbox_event.status == "published"
```

---

## 🚨 Troubleshooting

### Events not being published

1. Check Redis connection:
   ```python
   bus = get_event_bus()
   if bus and bus._connected:
       print("✅ Connected to Redis")
   else:
       print("❌ Not connected to Redis")
   ```

2. Check logs for errors:
   ```bash
   tail -f /tmp/your-service.log | grep -i event
   ```

### Events not being consumed

1. Verify subscription registered:
   ```python
   bus = get_event_bus()
   print(f"Subscribers: {list(bus._subscribers.keys())}")
   ```

2. Check pattern matching:
   ```python
   # ❌ Wrong
   @subscribe_to("workflow.completed")  # Точное совпадение

   # ✅ Right для wildcard
   @subscribe_to("workflow.*")  # Все workflow события
   ```

### Outbox events stuck

1. Check outbox publisher is running:
   ```python
   # В lifespan должно быть:
   await publisher.start()
   ```

2. Check for errors:
   ```sql
   SELECT event_type, retry_count, error
   FROM outbox_events
   WHERE status = 'pending' AND retry_count > 0;
   ```

3. Manually trigger publish:
   ```python
   await publish_outbox_events(lambda: SessionLocal())
   ```

---

## 📖 Examples

### Example 1: Workflow Service

```python
# main.py
from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to, Event

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_event_bus(service_name="workflow-service")
    yield
    await get_event_bus().close()

app = FastAPI(lifespan=lifespan)

@app.post("/workflows/{id}/start")
async def start_workflow(id: str):
    # Start workflow
    workflow = start_workflow_logic(id)

    # Publish event
    await publish_event(
        event_type="workflow.started",
        data={"workflow_id": id, "started_at": datetime.utcnow().isoformat()},
        source="workflow-service"
    )

    return {"status": "started"}

@subscribe_to("workflow.stage.completed")
async def on_stage_completed(event: Event):
    # Auto-start next stage
    workflow_id = event.data["workflow_id"]
    next_stage = event.data.get("next_stage")

    if next_stage:
        await start_next_stage(workflow_id, next_stage)
```

### Example 2: Notification Service

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_event_bus(service_name="notification-service")
    yield
    await get_event_bus().close()

app = FastAPI(lifespan=lifespan)

# Subscribe to all completion events
@subscribe_to("*.completed")
async def send_completion_notification(event: Event):
    entity_type = event.type.split(".")[0]  # workflow, bia, etc
    entity_id = event.data.get(f"{entity_type}_id")

    await send_notification(
        title=f"{entity_type.title()} Completed",
        message=f"{entity_type} {entity_id} has been completed",
        tenant_id=event.tenant_id
    )
```

### Example 3: Audit Service

```python
@subscribe_to("*")  # All events
async def audit_event(event: Event):
    # Log all platform events for compliance
    await save_audit_log(
        event_type=event.type,
        source=event.source,
        data=event.data,
        tenant_id=event.tenant_id,
        timestamp=event.timestamp
    )
```

---

## 🎓 Best Practices

### 1. Event Naming

✅ **DO:**
- Use domain-driven naming: `bia.risk.identified`
- Use past tense for completed actions: `workflow.completed`, not `workflow.complete`
- Be specific: `workflow.validation.failed` not `workflow.error`

❌ **DON'T:**
- Use generic names: `event.happened`
- Mix tenses: `workflow.completing`
- Use verbs: `createWorkflow`

### 2. Event Data

✅ **DO:**
- Include entity ID: `{"workflow_id": "123"}`
- Include timestamps: `{"completed_at": "2025-10-08T10:30:00Z"}`
- Keep data small (< 1KB if possible)
- Include tenant_id for multi-tenancy

❌ **DON'T:**
- Include sensitive data (passwords, tokens)
- Include large blobs (use references instead)
- Include redundant data

### 3. Handlers

✅ **DO:**
- Make handlers idempotent
- Handle errors gracefully
- Log processing
- Use correlation_id for tracing

❌ **DON'T:**
- Do long-running work in handlers (use background tasks)
- Throw exceptions without reason (EventBus will retry)
- Modify event data

### 4. Testing

✅ **DO:**
- Test event handlers in isolation
- Mock EventBus for unit tests
- Use real Redis for integration tests
- Test idempotency

❌ **DON'T:**
- Depend on event ordering
- Test with production data

---

## 🔐 Security

### Tenant Isolation

```python
# Events автоматически изолируются по tenant_id
await publish_event(
    event_type="workflow.completed",
    data={"workflow_id": "123"},
    source="workflow-service",
    tenant_id="tenant_456"  # ✅ Always include for multi-tenancy
)

# В обработчике проверяйте tenant
@subscribe_to("workflow.*")
async def handle_workflow(event: Event):
    if event.tenant_id != current_user_tenant_id:
        logger.warning("Unauthorized access attempt")
        return
```

### Event Validation

```python
from pydantic import BaseModel

class WorkflowCompletedData(BaseModel):
    workflow_id: str
    completed_at: str

@subscribe_to("workflow.completed")
async def validated_handler(event: Event):
    # Validate event data
    try:
        data = WorkflowCompletedData(**event.data)
    except ValidationError as e:
        logger.error(f"Invalid event data: {e}")
        return

    # Process validated data
    await process_workflow(data.workflow_id)
```

---

## 📞 Support

Вопросы? Проблемы?

1. Проверьте логи: `tail -f /tmp/your-service.log`
2. Проверьте Redis: `redis-cli PING`
3. Проверьте outbox: `SELECT * FROM outbox_events WHERE status = 'failed'`
4. Создайте issue в репозитории

---

**Готово!** Ваш сервис теперь полностью интегрирован с платформенной event-driven архитектурой. 🎉
