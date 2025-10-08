# EventBus Architecture

## Design Philosophy

**Goal:** Clean, pluggable event system with zero vendor lock-in

**Principles:**
1. **Interface segregation** - Code depends on `IEventBus`, not concrete backend
2. **Pluggable backends** - Switch from memory → Redis → RabbitMQ without code changes
3. **Type safety** - Strongly typed `Event` class
4. **Simplicity** - Easy to use, hard to misuse

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                   Services Layer                     │
│  (BIA, Risk, Workflow Intelligence, etc.)           │
└────────────────────┬────────────────────────────────┘
                     │ Depends on interface only
                     ↓
┌─────────────────────────────────────────────────────┐
│              Core Interface Layer                    │
│  - IEventBus (abstract interface)                   │
│  - Event (data model)                               │
│  - EventPriority (enum)                             │
└────────────────────┬────────────────────────────────┘
                     │ Implemented by
                     ↓
┌─────────────────────────────────────────────────────┐
│              Backend Layer                           │
│  - InMemoryEventBus (MVP, tests)                    │
│  - RedisStreamEventBus (production)                 │
│  - RabbitMQEventBus (future)                        │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. Event Model

**File:** `core/events.py`

**Purpose:** Type-safe event representation

**Key Features:**
- Immutable event ID
- JSON-serializable data
- Built-in metadata (timestamp, source, tenant)
- Priority levels
- Retry logic

**Example:**
```python
event = Event.create(
    event_type='workflow.stage_changed',
    data={'workflow_id': 'bia_001'},
    source='workflow-engine',
    tenant_id='tenant_123'
)
```

### 2. Interface

**File:** `core/interface.py`

**Purpose:** Abstract contract for all backends

**Key Methods:**
- `publish(event)` - Send event
- `subscribe(pattern, handler, group)` - Receive events
- `unsubscribe(sub_id)` - Cancel subscription
- `close()` - Cleanup

**Guarantees:**
- At-least-once delivery
- Async operations
- Pattern matching support

### 3. Backends

#### InMemoryEventBus

**File:** `backends/memory.py`

**Use Cases:**
- Unit testing
- Local development
- MVP validation
- Single-process apps

**Implementation:**
- Dictionary-based handlers
- Asyncio tasks for delivery
- Regex pattern matching
- No external dependencies

**Limitations:**
- No persistence
- Single process only
- Lost on restart

#### RedisStreamEventBus

**File:** `backends/redis_streams.py`

**Use Cases:**
- Production deployments
- Multi-instance services
- Event replay
- Reliable delivery

**Implementation:**
- Redis Streams (XADD, XREADGROUP)
- Consumer groups
- ACK mechanism
- Persistent storage

**Features:**
- Survives restarts
- Load balancing across instances
- Event history

### 4. Factory

**File:** `factory.py`

**Purpose:** Create EventBus instances

**Usage:**
```python
# Memory
bus = create_eventbus('memory')

# Redis
bus = create_eventbus('redis', redis_url='redis://...')

# From environment
bus = create_eventbus_from_env()
```

## Event Flow

### Publish Flow

```
Service
  │
  ├─> Event.create()
  │
  ├─> bus.publish(event)
  │
  └─> Backend
       ├─> Serialize event
       ├─> Store/Send via transport
       └─> Return (async)
```

### Subscribe Flow

```
Service
  │
  ├─> Define handler function
  │
  ├─> bus.subscribe(pattern, handler)
  │
  └─> Backend
       ├─> Register pattern
       ├─> Start consumer task
       └─> On event:
            ├─> Match pattern
            ├─> Deserialize event
            ├─> Call handler
            └─> ACK (if supported)
```

## Pattern Matching

### Syntax

- `workflow.started` - Exact match
- `workflow.*` - Single level wildcard
- `*` or `#` - Match all

### Examples

```python
# Specific event
await bus.subscribe('bia.process_created', handler)

# All BIA events
await bus.subscribe('bia.*', handler)

# All workflow events
await bus.subscribe('workflow.*', handler)

# Everything
await bus.subscribe('*', handler)
```

### Implementation

**In-Memory:** Regex conversion (`workflow.*` → `^workflow\..*$`)

**Redis Streams:** Multiple stream subscriptions (limited wildcard support)

## Reliability

### At-Least-Once Delivery

**Guarantee:** Events will be delivered at least once (may be duplicates)

**Recommendation:** Make handlers idempotent

**Example:**
```python
async def idempotent_handler(event: Event):
    process_id = event.data['process_id']

    # Check if already processed
    if await db.exists('processed_events', event.id):
        return  # Skip duplicate

    # Process event
    await create_process(process_id)

    # Mark as processed
    await db.save('processed_events', event.id)
```

### Retry Logic

**Built-in:** Automatic retry on handler failure

**Configuration:**
```python
event.max_retries = 5  # Default: 3
```

**Backoff:** Exponential (2s, 4s, 8s, 16s, ...)

**Failure:** After max retries, event is logged and dropped

## Multi-Tenancy

### Tenant Isolation

Events carry `tenant_id`:

```python
event = Event.create(
    event_type='bia.process_created',
    data={...},
    tenant_id='tenant_healthcare_123'
)
```

### Handler Filtering

```python
async def handler(event: Event):
    # Filter by tenant
    if event.tenant_id != 'my_tenant':
        return

    # Process...
```

## Consumer Groups (Redis)

### Purpose

Load balancing across multiple service instances

### Usage

```python
# Instance 1
await bus.subscribe(
    'workflow.stage_changed',
    handler,
    consumer_group='workflow-processors'
)

# Instance 2 (same group)
await bus.subscribe(
    'workflow.stage_changed',
    handler,
    consumer_group='workflow-processors'
)
```

**Behavior:** Each event delivered to ONE instance (round-robin)

### No Consumer Group

```python
await bus.subscribe('workflow.*', handler)
# No consumer_group = ALL instances receive ALL events
```

## Event Priorities

### Levels

```python
EventPriority.LOW       # Background tasks
EventPriority.NORMAL    # Default
EventPriority.HIGH      # Important events
EventPriority.CRITICAL  # Alerts, failures
```

### Current Implementation

Priorities stored in event metadata but **not** used for delivery order (all backends deliver FIFO).

### Future

- Priority queues
- Critical events bypass queue
- Throttling low priority

## Correlation IDs

### Purpose

Trace related events across services

### Usage

```python
# Request arrives
request_id = generate_request_id()

# Publish event with correlation ID
event = Event.create(
    event_type='bia.process_created',
    data={...},
    correlation_id=request_id
)

# Later, in another service
async def handler(event: Event):
    logger.info(
        f"Processing event",
        correlation_id=event.correlation_id
    )
```

### Observability

Link logs, traces, and events using correlation ID.

## Performance

### In-Memory

- **Publish:** < 1ms (dict append)
- **Deliver:** < 1ms (asyncio task)
- **Throughput:** 10K+ events/sec (single process)

### Redis Streams

- **Publish:** < 5ms (Redis XADD)
- **Deliver:** < 10ms (XREADGROUP + handler)
- **Throughput:** 1K+ events/sec (depends on Redis)

### Optimization

- Batch publishes (`XADD` pipeline)
- Consumer prefetch (read multiple events)
- Handler parallelism (multiple workers)

## Error Handling

### Handler Errors

```python
async def handler(event: Event):
    try:
        await process(event)
    except TemporaryError:
        raise  # Retry
    except PermanentError:
        logger.error("Permanent failure")
        # Don't raise - prevents infinite retries
```

### Backend Errors

**Memory:** No external dependencies = no network errors

**Redis:** Auto-reconnect via `redis.asyncio` (robust connection)

### Dead Letter Queue (Future)

Events exceeding max retries → Dead letter queue for manual inspection

## Testing

### Unit Tests

Use in-memory backend:

```python
@pytest.mark.asyncio
async def test_workflow_event():
    bus = create_eventbus('memory')

    received = []

    async def handler(event: Event):
        received.append(event)

    await bus.subscribe('workflow.*', handler)

    event = Event.create('workflow.started', {}, 'test', 'tenant_123')
    await bus.publish(event)

    await asyncio.sleep(0.1)

    assert len(received) == 1
    await bus.close()
```

### Integration Tests

Use Redis (requires running Redis):

```python
@pytest.mark.integration
async def test_redis_eventbus():
    bus = create_eventbus('redis', redis_url='redis://localhost:6379')
    # ... same test logic
```

## Migration Path

### Phase 1: MVP (Current)

```python
bus = create_eventbus('memory')
```

All services use in-memory bus.

### Phase 2: Production

```python
bus = create_eventbus('redis', redis_url=REDIS_URL)
```

Change configuration, code stays same.

### Phase 3: Scale (Future)

```python
bus = create_eventbus('rabbitmq', rabbitmq_url=RABBITMQ_URL)
```

Add RabbitMQ backend, change config.

**Code never changes!**

## Extension Points

### Add New Backend

1. Implement `IEventBus` interface
2. Add to `factory.py`
3. Done!

**Example:**
```python
# backends/rabbitmq.py
class RabbitMQEventBus(IEventBus):
    async def publish(self, event: Event): ...
    async def subscribe(self, event_type, handler, group): ...
    async def unsubscribe(self, sub_id): ...
    async def close(self): ...

# factory.py
elif backend == 'rabbitmq':
    return RabbitMQEventBus(config['rabbitmq_url'])
```

### Add Event Validation

```python
# core/validation.py
def validate_event(event: Event):
    assert event.tenant_id, "tenant_id required"
    assert event.source, "source required"
    # ...

# Integrate in publish()
async def publish(self, event: Event):
    validate_event(event)
    # ... continue
```

### Add Event Schema

```python
# Use Pydantic or similar
from pydantic import BaseModel

class BIAProcessCreatedData(BaseModel):
    process_id: int
    name: str

event = Event.create(
    'bia.process_created',
    BIAProcessCreatedData(process_id=123, name='IT').dict(),
    'bia-service',
    'tenant_123'
)
```

## Design Decisions

### Why not use existing library?

**Considered:**
- Celery (too heavy, requires broker)
- NATS (another dependency)
- Kafka (overkill for MVP)

**Decision:** Build minimal, clean abstraction that fits our needs.

### Why pluggable backends?

**Reason:** Start simple (memory), scale later (Redis/RabbitMQ) without code changes.

### Why Event class vs dict?

**Reason:**
- Type safety
- IDE autocomplete
- Validation
- Serialization logic in one place

### Why at-least-once vs exactly-once?

**Reason:**
- Exactly-once is complex (2-phase commit)
- At-least-once + idempotent handlers = simpler
- Good enough for our use cases

## Future Enhancements

- [ ] Event schema validation (Pydantic)
- [ ] Dead letter queue
- [ ] Event replay (from timestamp)
- [ ] Metrics/monitoring (Prometheus)
- [ ] Event versioning
- [ ] Circuit breaker (stop consuming if handler fails repeatedly)
- [ ] Rate limiting (per tenant, per event type)
- [ ] Event filtering (server-side)

## Related Components

**Workflow Intelligence:** Consumes workflow events to track state

**Case Library:** Stores successful workflows as events

**AI Services:** Publish recommendations as events

**Notification Service:** Subscribes to alert events

## References

**Code:**
- [core/events.py](core/events.py) - Event model
- [core/interface.py](core/interface.py) - IEventBus interface
- [backends/memory.py](backends/memory.py) - In-memory backend
- [backends/redis_streams.py](backends/redis_streams.py) - Redis backend

**Docs:**
- [README.md](README.md) - User guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start
- [examples/](examples/) - Working examples

**Tests:**
- [tests/test_events.py](tests/test_events.py) - Event model tests
- [tests/test_memory_backend.py](tests/test_memory_backend.py) - Backend tests
