# Runtime Infrastructure - Service Specification

**Last Updated:** 2025-10-07
**Status:** Production Ready
**Version:** 1.0.0

---

## Назначение

Runtime инфраструктура для event-driven архитектуры и service coordination:
- **EventBus** - Pluggable event system (Memory, Redis Streams, RabbitMQ)
- **Message Queue** - RabbitMQ для асинхронных задач
- **Realtime WebSocket** - Real-time двусторонняя коммуникация
- **Service Discovery** - Регистрация и обнаружение сервисов

---

## Технологии

### EventBus
- **Language:** Python 3.11+
- **Backends:** Memory (MVP), Redis Streams (Production), RabbitMQ (Future)
- **Pattern:** Publisher/Subscriber
- **Features:** Wildcard subscriptions, Consumer groups, Retry logic

### Message Queue
- **Technology:** RabbitMQ 3.12+
- **Client:** aio-pika (async Python)
- **Patterns:** Pub/Sub, Work Queues, Topic Routing
- **Features:** DLQ, Priority, Persistence

### Realtime WebSocket
- **Framework:** FastAPI WebSocket
- **Protocol:** WebSocket (RFC 6455)
- **Features:** Rooms, Broadcasting, Authentication

### Service Discovery
- **Pattern:** Service Registry + Health Monitor
- **Storage:** Redis (persistence)
- **Health Checks:** Docker, HTTP, Custom
- **ISO Mapping:** 12 services mapped to ISO 22301 clauses

---

## Структура

```
runtime/
├── eventbus/                       # Pluggable Event System
│   ├── core/
│   │   ├── events.py                   # Event model
│   │   └── interface.py                # IEventBus interface
│   ├── backends/
│   │   ├── memory.py                   # In-memory backend
│   │   └── redis_streams.py            # Redis Streams backend
│   ├── subscribers/
│   │   └── base.py                     # Subscriber base class
│   ├── examples/
│   │   ├── basic_usage.py
│   │   ├── redis_example.py
│   │   └── subscriber_example.py
│   ├── tests/
│   │   ├── test_events.py
│   │   └── test_memory_backend.py
│   ├── config.py
│   ├── factory.py                      # EventBus factory
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── README.md
│   ├── QUICKSTART.md
│   └── ARCHITECTURE.md
│
├── message-queue/                  # RabbitMQ Manager
│   ├── rabbitmq_manager.py             # Main manager class
│   ├── requirements.txt
│   └── README.md
│
├── realtime-websocket/             # WebSocket Service
│   ├── main.py                         # FastAPI WebSocket server
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── service-discovery/              # Service Registry
    ├── service_registry.py             # Service registration
    ├── health_monitor.py               # Health monitoring
    ├── iso_service_map.py              # ISO 22301 mapping
    └── README.md
```

---

## EventBus

### Purpose
Clean architecture event bus для decoupling сервисов через events.

### Event Model

```python
from infrastructure.eventbus import Event, EventPriority

# Create event
event = Event.create(
    event_type='bia.process_created',
    data={'process_id': 123, 'name': 'IT Systems'},
    source='bia-service',
    tenant_id='tenant_456',
    priority=EventPriority.NORMAL
)

# Event fields
event.id            # UUID
event.event_type    # 'bia.process_created'
event.data          # Payload
event.source        # Service that published
event.tenant_id     # Tenant isolation
event.timestamp     # When created
event.correlation_id # For tracing
event.priority      # LOW, NORMAL, HIGH, CRITICAL
```

### Backends

**1. Memory (MVP, Testing)**
```python
from infrastructure.eventbus import create_eventbus

bus = create_eventbus('memory')

# Pros: Zero dependencies, instant startup
# Cons: Events don't survive restart, single process only
```

**2. Redis Streams (Production)**
```python
bus = create_eventbus('redis', redis_url='redis://localhost:6379')

# Pros: Persistence, consumer groups, multi-process
# Cons: Requires Redis 5.0+
```

**3. RabbitMQ (Future)**
```python
bus = create_eventbus('rabbitmq', rabbitmq_url='amqp://localhost')

# Pros: Advanced routing, mature, scalable
# Cons: More complex setup
```

### Usage

**Publish Event:**
```python
from infrastructure.eventbus import create_eventbus, Event

bus = create_eventbus('redis')

event = Event.create(
    event_type='workflow.stage_changed',
    data={'workflow_id': 'bia_001', 'stage': 'analysis'},
    source='workflow-engine',
    tenant_id='tenant_123'
)

await bus.publish(event)
```

**Subscribe to Events:**
```python
# Handler function
async def handle_workflow_event(event: Event):
    print(f"Workflow event: {event.data}")
    # Process event
    workflow_id = event.data['workflow_id']
    # ...

# Subscribe (wildcard support)
await bus.subscribe('workflow.*', handle_workflow_event)

# Subscribe to all events
await bus.subscribe('*', handle_all_events)

# Cleanup
await bus.close()
```

**Event Types Convention:**
```
{domain}.{action}

Examples:
- bia.process_created
- bia.process_updated
- workflow.stage_changed
- workflow.completed
- risk.assessment_started
- document.approved
```

---

## Message Queue (RabbitMQ)

### Purpose
Асинхронная очередь сообщений для long-running tasks и event distribution.

### Setup

```bash
# Docker
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management-alpine

# Management UI: http://localhost:15672
# Username: guest, Password: guest
```

### Usage

**Publisher:**
```python
from rabbitmq_manager import get_rabbitmq_manager

mq = await get_rabbitmq_manager("amqp://guest:guest@localhost/")

# Publish event
await mq.publish(
    routing_key="user.created",
    message={
        "user_id": "123",
        "email": "user@example.com"
    },
    priority=5  # 0-9
)

# Publish with TTL
await mq.publish(
    routing_key="notification.email",
    message={"to": "user@example.com", "subject": "Welcome!"},
    ttl=60000  # 60 seconds
)
```

**Consumer:**
```python
# Handler
async def handle_user_events(message: dict):
    data = message["data"]
    print(f"User event: {data}")
    # Process event

# Subscribe
await mq.subscribe(
    routing_key="user.*",  # user.created, user.updated, etc.
    callback=handle_user_events,
    queue_name="user_events_queue",
    durable=True
)
```

**Work Queue:**
```python
# Create work queue
async def process_email_task(task: dict):
    data = task["data"]
    await send_email(data["to"], data["subject"], data["body"])

await mq.create_work_queue(
    queue_name="email_tasks",
    callback=process_email_task,
    max_priority=10
)

# Add task to queue
await mq.publish_task(
    queue_name="email_tasks",
    task={
        "to": "user@example.com",
        "subject": "Welcome!",
        "body": "Thank you!"
    },
    priority=5
)
```

### Patterns

**Routing Patterns:**
- `user.*` → user.created, user.updated, user.deleted
- `*.important` → user.important, order.important
- `#` → all messages

**Dead Letter Queue:**
- Failed tasks automatically go to DLQ
- Format: `{queue_name}.dlq`
- Monitor: `await mq.get_queue_stats("email_tasks.dlq")`

---

## Realtime WebSocket

### Purpose
Real-time двусторонняя коммуникация между backend и frontend.

### Features
- WebSocket connections
- Room-based broadcasting
- JWT authentication
- Auto-reconnection support

### Setup

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/realtime-websocket

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
python main.py
```

### Usage

**Server (FastAPI):**
```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            # Process message
            await websocket.send_json({"response": "ok"})
    except:
        pass
```

**Client (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8050/ws/client123');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({type: 'subscribe', room: 'incidents'}));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onerror = (error) => console.error('Error:', error);
ws.onclose = () => console.log('Disconnected');
```

### Use Cases

**1. Real-time Notifications:**
```python
# Backend sends notification
await websocket_manager.broadcast_to_user(
    user_id="123",
    message={"type": "notification", "text": "New incident"}
)
```

**2. Live Dashboard Updates:**
```python
# Broadcast metrics update
await websocket_manager.broadcast_to_room(
    room="dashboard",
    message={"type": "metrics", "data": metrics}
)
```

**3. Collaborative Editing:**
```python
# Send document change to all editors
await websocket_manager.broadcast_to_room(
    room=f"document_{doc_id}",
    message={"type": "change", "delta": delta}
)
```

---

## Service Discovery

### Purpose
Service registry + health monitoring + ISO 22301 mapping.

### Components

**1. Service Registry**
- Track all services, dependencies, status
- Redis persistence
- Query by orchestrator, status, dependencies

**2. Health Monitor**
- Multi-mode health checks (Docker, HTTP, Custom)
- Continuous monitoring (background tasks)
- Retry logic (3 retries)

**3. ISO Service Map**
- 12 BCM services mapped to ISO 22301 clauses
- Component grouping (bcm-strategy, community, etc.)
- Workflow intelligence tracking

### Service Registry Usage

```python
from infrastructure.service_discovery import ServiceRegistry

registry = ServiceRegistry()
await registry.connect_redis(redis_client)

# Register service
service = await registry.register(
    service_name="api_service",
    orchestrator="PlatformOrchestrator",
    metadata={"port": 8000, "version": "1.0.0"},
    dependencies=["postgres", "redis"]
)

# Check dependencies
ready = await registry.is_dependencies_ready("api_service")

# Update status
await registry.update_status("api_service", "running")
await registry.update_health("api_service", "healthy")

# Query services
all_services = await registry.get_all_services()
by_orch = await registry.get_services_by_orchestrator("PlatformOrchestrator")
```

### Health Monitor Usage

```python
from infrastructure.service_discovery import HealthMonitor, HealthCheck

monitor = HealthMonitor()
await monitor.connect_docker(docker_client)

# Register HTTP health check
await monitor.register_check(HealthCheck(
    service_name="api_service",
    check_type="http",
    interval=30,
    timeout=10,
    retries=3,
    config={
        "url": "http://localhost:8000/health",
        "expected_status": 200
    }
))

# Run check
result = await monitor.check_service("api_service")
print(f"Healthy: {result.is_healthy()}")

# Continuous monitoring
await monitor.monitor_continuously()
```

### ISO Service Map

```python
from infrastructure.service_discovery.iso_service_map import (
    ISO_SERVICE_REGISTRY,
    get_services_by_component,
    get_services_with_workflow_intelligence,
    get_services_by_iso_clause
)

# Get all services
all_services = ISO_SERVICE_REGISTRY

# Get BCM strategy services
bcm_services = get_services_by_component("bcm-strategy")

# Get services with workflow intelligence (10 services)
wi_services = get_services_with_workflow_intelligence()

# Get services implementing ISO 8.2.2 (BIA)
bia_services = get_services_by_iso_clause("8.2.2")
```

---

## Configuration

### EventBus Environment Variables

```bash
# Backend type
EVENTBUS_BACKEND=redis  # memory, redis, rabbitmq

# Redis (if using redis backend)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=<if-required>

# Event retention
EVENT_RETENTION_DAYS=7

# Consumer group (for Redis Streams)
CONSUMER_GROUP=default
```

### RabbitMQ Environment Variables

```bash
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_PREFETCH_COUNT=10
RABBITMQ_HEARTBEAT=600
RABBITMQ_CONNECTION_TIMEOUT=30
```

### WebSocket Environment Variables

```bash
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8050
WEBSOCKET_MAX_CONNECTIONS=1000

# Auth
JWT_SECRET=<secret>
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Service Discovery Environment Variables

```bash
# Redis (for registry persistence)
REDIS_URL=redis://localhost:6379

# Health check intervals
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3

# Docker (if using Docker health checks)
DOCKER_HOST=unix:///var/run/docker.sock
```

---

## Развертывание

### Docker Compose

```yaml
version: '3.8'

services:
  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    healthcheck:
      test: rabbitmq-diagnostics -q ping
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis (for EventBus + Service Registry)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  # WebSocket Service
  websocket:
    build: ./realtime-websocket
    ports:
      - "8050:8050"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

volumes:
  rabbitmq-data:
  redis-data:
```

### Standalone Services

```bash
# EventBus (library, no service)
pip install -e infrastructure/runtime/eventbus

# RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management

# WebSocket
cd infrastructure/runtime/realtime-websocket
pip install -r requirements.txt
python main.py
```

---

## Мониторинг

### RabbitMQ Monitoring

**Management UI:**
```bash
open http://localhost:15672
# Username: guest, Password: guest
```

**Metrics:**
```python
# Queue stats
stats = await mq.get_queue_stats("user_events_queue")
print(f"Messages: {stats['message_count']}")
print(f"Consumers: {stats['consumer_count']}")
```

**Prometheus Exporter:**
```yaml
# docker-compose.yml
rabbitmq-exporter:
  image: kbudde/rabbitmq-exporter
  ports:
    - "9419:9419"
  environment:
    - RABBIT_URL=http://rabbitmq:15672
```

### EventBus Monitoring

```python
# Health check
from infrastructure.eventbus import create_eventbus

bus = create_eventbus('redis')
health = await bus.health_check()

print(f"Backend: {health['backend']}")
print(f"Connected: {health['connected']}")
print(f"Events published: {health['events_published']}")
```

### WebSocket Monitoring

```python
# Connection count
from main import connection_manager

active_connections = connection_manager.get_active_count()
print(f"Active WebSocket connections: {active_connections}")
```

### Service Registry Monitoring

```python
# Service health
from infrastructure.service_discovery import ServiceRegistry

registry = ServiceRegistry()
services = await registry.get_all_services()

for service in services:
    print(f"{service.name}: {service.status} ({service.health})")
```

---

## Проблемы/TODO

### Critical Issues
- None currently

### Improvements Needed

1. **EventBus:**
   - [ ] Implement RabbitMQ backend
   - [ ] Add event replay functionality
   - [ ] Implement event versioning
   - [ ] Add event schema validation
   - [ ] Create event auditing

2. **Message Queue:**
   - [ ] Add RabbitMQ Shovel для multi-region
   - [ ] Implement message deduplication
   - [ ] Add message tracing
   - [ ] Create monitoring dashboards
   - [ ] Add auto-scaling workers

3. **WebSocket:**
   - [ ] Add horizontal scaling (Redis pub/sub)
   - [ ] Implement reconnection strategy
   - [ ] Add message persistence
   - [ ] Create connection pooling
   - [ ] Add rate limiting per connection

4. **Service Discovery:**
   - [ ] Add Consul integration
   - [ ] Implement circuit breaker pattern
   - [ ] Add service mesh support (Istio)
   - [ ] Create gRPC health checks
   - [ ] Add service versioning

5. **General:**
   - [ ] Add distributed tracing
   - [ ] Implement saga pattern для distributed transactions
   - [ ] Add event sourcing support
   - [ ] Create CQRS implementation
   - [ ] Add GraphQL subscription support

---

## Integration Examples

### BIA Service → Notification

```python
# BIA Service publishes event
from infrastructure.eventbus import create_eventbus, Event

bus = create_eventbus('redis')

await bus.publish(Event.create(
    event_type='bia.analysis.completed',
    data={'bia_id': 'bia_001', 'organization_id': 'org_123'},
    source='bia-service',
    tenant_id='tenant_456'
))

# Notification Service subscribes
async def send_completion_notification(event: Event):
    data = event.data
    await notification_service.send_email(
        to=get_stakeholders(data['organization_id']),
        subject="BIA Analysis Completed",
        body=f"BIA {data['bia_id']} completed successfully"
    )

await bus.subscribe('bia.*.completed', send_completion_notification)
```

### Real-time Dashboard Updates

```python
# Backend: Publish metrics update
from infrastructure.runtime.realtime_websocket import websocket_manager

await websocket_manager.broadcast_to_room(
    room="dashboard",
    message={
        "type": "metrics_update",
        "data": {
            "active_incidents": 5,
            "training_compliance": 87.5,
            "rto_compliance": 92.3
        }
    }
)

# Frontend: Receive and update
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'metrics_update') {
        updateDashboard(data.data);
    }
};
```

---

## Quick Reference

### Publish Event (EventBus)

```python
from infrastructure.eventbus import create_eventbus, Event

bus = create_eventbus('redis')
await bus.publish(Event.create(
    event_type='bia.process_created',
    data={'process_id': 123},
    source='bia-service',
    tenant_id='tenant_123'
))
```

### Subscribe to Events

```python
async def handler(event: Event):
    print(event.data)

await bus.subscribe('bia.*', handler)
```

### Send Task to Queue

```python
from rabbitmq_manager import get_rabbitmq_manager

mq = await get_rabbitmq_manager()
await mq.publish_task('email_tasks', {'to': 'user@example.com'})
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8050/ws/client123');
ws.send(JSON.stringify({type: 'message', data: 'Hello'}));
```

---

**STATUS:** Production Ready
**READY FOR:** Full deployment
**BLOCKERS:** None
