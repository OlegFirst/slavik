# EventBus - Pluggable Event System

Clean architecture event bus for the BCM Platform with multiple backend support.

## Features

- ✅ Clean interface (`IEventBus`) - backend-agnostic
- ✅ Multiple backends: memory, Redis Streams, (RabbitMQ coming)
- ✅ Type-safe events with `Event` class
- ✅ Wildcard subscriptions (`workflow.*`, `*`)
- ✅ Consumer groups (load balancing)
- ✅ Automatic retry logic
- ✅ Zero vendor lock-in

## Quick Start

### 1. Install

```bash
# No dependencies for in-memory backend
pip install -e .

# For Redis backend
pip install redis
```

### 2. Basic Usage

```python
from infrastructure.eventbus import create_eventbus, Event, EventPriority

# Create bus
bus = create_eventbus('memory')  # or 'redis'

# Publish event
event = Event.create(
    event_type='workflow.stage_changed',
    data={'workflow_id': 'bia_001', 'stage': 'analysis'},
    source='workflow-engine',
    tenant_id='tenant_123'
)
await bus.publish(event)

# Subscribe to events
async def handle_workflow_event(event: Event):
    print(f"Workflow event: {event.data}")

await bus.subscribe('workflow.*', handle_workflow_event)

# Cleanup
await bus.close()
```

## Backends

### In-Memory (MVP, Testing)

```python
bus = create_eventbus('memory')
```

**Advantages:**
- Zero dependencies
- Instant startup
- Perfect for unit tests

**Limitations:**
- Events don't survive restart
- Single process only

### Redis Streams (Production)

```python
bus = create_eventbus('redis', redis_url='redis://localhost:6379')
```

**Advantages:**
- Persistence
- Consumer groups (load balancing)
- ACK mechanism
- Works across processes

**Requirements:**
- Redis 5.0+
- `pip install redis`

## Event Model

### Creating Events

```python
from infrastructure.eventbus import Event, EventPriority

# Basic event
event = Event.create(
    event_type='bia.process_created',
    data={'process_id': 123, 'name': 'IT Systems'},
    source='bia-service',
    tenant_id='tenant_456'
)

# With priority
event = Event.create(
    event_type='alert.critical',
    data={'message': 'System down'},
    source='monitoring',
    tenant_id='tenant_123',
    priority=EventPriority.CRITICAL
)

# With correlation ID (for tracing)
event = Event.create(
    event_type='workflow.completed',
    data={'workflow_id': 'bia_001'},
    source='workflow-engine',
    tenant_id='tenant_123',
    correlation_id='request_789'
)
```

### Event Types (Convention)

Use dot-separated naming:

```
{domain}.{action}
```

Examples:
- `bia.process_created`
- `bia.process_updated`
- `workflow.stage_changed`
- `workflow.completed`
- `risk.assessment_started`
- `document.approved`

### Event Priorities

```python
from infrastructure.eventbus import EventPriority

EventPriority.LOW       # Background tasks
EventPriority.NORMAL    # Default
EventPriority.HIGH      # Important events
EventPriority.CRITICAL  # Alerts, failures
```

## Subscriptions

### Exact Match

```python
await bus.subscribe('workflow.completed', handler)
```

### Wildcard Patterns

```python
# All workflow events
await bus.subscribe('workflow.*', handler)

# All events
await bus.subscribe('*', handler)
```

### Consumer Groups (Load Balancing)

```python
# Multiple instances share load
await bus.subscribe(
    'workflow.stage_changed',
    handler,
    consumer_group='workflow-processors'
)
```

When using consumer groups, only ONE instance receives each event (round-robin).

### Unsubscribe

```python
sub_id = await bus.subscribe('workflow.*', handler)

# Later...
await bus.unsubscribe(sub_id)
```

## Configuration

### From Environment

```python
from infrastructure.eventbus import create_eventbus_from_env

# Reads EVENTBUS_BACKEND and REDIS_URL
bus = create_eventbus_from_env()
```

**Environment Variables:**

```bash
# .env
EVENTBUS_BACKEND=redis  # or 'memory'
REDIS_URL=redis://localhost:6379
```

### In Services

```python
# FastAPI example
from fastapi import FastAPI
from infrastructure.eventbus import create_eventbus_from_env

app = FastAPI()
bus = None

@app.on_event("startup")
async def startup():
    global bus
    bus = create_eventbus_from_env()

@app.on_event("shutdown")
async def shutdown():
    await bus.close()
```

## Advanced Usage

### Error Handling

Events automatically retry on handler errors:

```python
event.max_retries = 5  # Default: 3

await bus.publish(event)
```

Exponential backoff: 2s, 4s, 8s, ...

### Statistics

```python
stats = await bus.get_stats()
print(stats)
# {'published': 150, 'consumed': 148, 'errors': 2}
```

### Event Serialization

```python
# To dict
event_dict = event.to_dict()

# From dict
event = Event.from_dict(event_dict)
```

Useful for:
- Storing events in database
- Sending via HTTP
- Event replay

## Testing

### Unit Tests

```python
import pytest
from infrastructure.eventbus import create_eventbus, Event

@pytest.mark.asyncio
async def test_event_flow():
    bus = create_eventbus('memory')

    received = []

    async def handler(event: Event):
        received.append(event)

    await bus.subscribe('test.event', handler)

    event = Event.create('test.event', {}, 'test', 'tenant_123')
    await bus.publish(event)

    await asyncio.sleep(0.1)

    assert len(received) == 1
    await bus.close()
```

### Run Tests

```bash
pytest infrastructure/eventbus/tests/
```

## Architecture

```
infrastructure/eventbus/
├── __init__.py           # Public API
├── core/
│   ├── events.py         # Event model
│   └── interface.py      # IEventBus interface
├── backends/
│   ├── memory.py         # In-memory backend
│   └── redis_streams.py  # Redis Streams backend
├── factory.py            # create_eventbus()
├── config.py             # Configuration
└── tests/
    ├── test_events.py
    └── test_memory_backend.py
```

## Migration Path

### Phase 1: MVP (Now)

```python
bus = create_eventbus('memory')
```

### Phase 2: Production

```python
bus = create_eventbus('redis', redis_url=REDIS_URL)
```

**Code doesn't change!** Only configuration.

### Phase 3: Advanced (Future)

```python
bus = create_eventbus('rabbitmq', rabbitmq_url=RABBITMQ_URL)
```

## Best Practices

### 1. Event Naming

✅ Good:
```python
'bia.process_created'
'workflow.stage_changed'
'document.approved'
```

❌ Bad:
```python
'processCreated'  # Use dots
'BIA_PROCESS'     # Lowercase
'created'         # Too generic
```

### 2. Event Data

✅ Good:
```python
data = {
    'process_id': 123,
    'name': 'IT Systems',
    'created_by': 'user_456'
}
```

❌ Bad:
```python
data = {
    'process': ProcessObject()  # Not JSON-serializable
}
```

### 3. Idempotent Handlers

Events may be delivered multiple times. Make handlers idempotent:

```python
async def handle_process_created(event: Event):
    process_id = event.data['process_id']

    # Check if already processed
    if await db.exists('process', process_id):
        return  # Already handled

    # Process event
    await db.create('process', process_id, ...)
```

### 4. Correlation IDs

Use correlation IDs for tracing:

```python
# In request handler
request_id = generate_request_id()

event = Event.create(
    event_type='bia.process_created',
    data={...},
    source='bia-service',
    tenant_id='tenant_123',
    correlation_id=request_id  # Link to original request
)
```

### 5. Error Handling

Don't swallow errors - let retry mechanism work:

```python
async def handler(event: Event):
    try:
        await process_event(event)
    except TemporaryError:
        raise  # Will retry
    except PermanentError as e:
        logger.error(f"Permanent error: {e}")
        # Don't raise - prevents infinite retries
```

## FAQ

### Q: Which backend should I use?

- **Development/Testing:** `memory`
- **Production (single instance):** `redis`
- **Production (multiple instances):** `redis` with consumer groups

### Q: How do wildcard subscriptions work?

- `workflow.*` → matches `workflow.started`, `workflow.completed`
- `*` → matches everything

Redis Streams: Wildcards implemented by subscribing to multiple streams.

### Q: Can I use both backends simultaneously?

No. Choose one backend per application instance.

### Q: What happens if Redis is down?

Events will fail to publish. Implement fallback or queue locally.

### Q: How do I migrate from memory to Redis?

Change one line:

```python
# Before
bus = create_eventbus('memory')

# After
bus = create_eventbus('redis', redis_url='...')
```

## Event Subscribers

### Building Event Subscribers

Use `BaseSubscriber` to create event subscribers:

```python
from infrastructure.eventbus.subscribers import BaseSubscriber

class CaseCollectorSubscriber(BaseSubscriber):
    async def setup_subscriptions(self, eventbus):
        await self.subscribe(
            eventbus,
            'workflow.state_changed',
            self.handle_state_changed
        )

    async def handle_state_changed(self, event: Event):
        # Record state transition
        pass
```

### Event-Driven Architecture

```
State Machine (Publisher)
    │
    └─→ EventBus
         ├─→ Case Collector (records history)
         ├─→ AI Advisor (prepares context)
         ├─→ Analytics Service (metrics)
         ├─→ Notification Service (alerts)
         └─→ Audit Logger (compliance)
```

### Examples

See [examples/subscriber_example.py](examples/subscriber_example.py) for complete subscriber examples.

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from infrastructure.eventbus import create_eventbus, IEventBus

app = FastAPI()

@app.on_event("startup")
async def startup():
    bus = create_eventbus('memory')

    # Setup subscribers
    subscribers = [
        WorkflowSubscriber(),
        NotificationSubscriber(),
        AuditSubscriber()
    ]

    for subscriber in subscribers:
        await subscriber.setup_subscriptions(bus)

    app.state.eventbus = bus
    app.state.subscribers = subscribers

@app.on_event("shutdown")
async def shutdown():
    for subscriber in app.state.subscribers:
        await subscriber.cleanup(app.state.eventbus)
    await app.state.eventbus.close()

# Use in endpoints
def get_eventbus() -> IEventBus:
    return app.state.eventbus

@app.post("/workflows")
async def create_workflow(bus: IEventBus = Depends(get_eventbus)):
    event = Event.create(...)
    await bus.publish(event)
```

See [examples/fastapi_integration.py](examples/fastapi_integration.py) for complete integration example.

## Roadmap

- [x] Event Subscribers base class
- [x] FastAPI integration example
- [ ] RabbitMQ backend (advanced routing)
- [ ] Dead letter queue
- [ ] Event replay
- [ ] Metrics/monitoring integration
- [ ] Event schema validation

## License

MIT
