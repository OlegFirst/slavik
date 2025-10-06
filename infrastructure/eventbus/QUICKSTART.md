# EventBus Quick Start

## Installation

```bash
cd /Users/MD/AI-Platform-ISO

# For memory backend (no dependencies)
# Already ready to use!

# For Redis backend
pip install redis
```

## 5-Minute Tutorial

### 1. Basic Example (In-Memory)

```python
import asyncio
from infrastructure.eventbus import create_eventbus, Event, EventPriority

async def main():
    # Create bus
    bus = create_eventbus('memory')

    # Subscribe
    async def my_handler(event: Event):
        print(f"Got event: {event.type} - {event.data}")

    await bus.subscribe('workflow.*', my_handler)

    # Publish
    event = Event.create(
        event_type='workflow.started',
        data={'workflow_id': 'bia_001'},
        source='my-service',
        tenant_id='tenant_123'
    )
    await bus.publish(event)

    # Wait for processing
    await asyncio.sleep(0.1)

    # Cleanup
    await bus.close()

asyncio.run(main())
```

### 2. Run Example

```bash
cd /Users/MD/AI-Platform-ISO

# Run basic example
PYTHONPATH=. python3 infrastructure/eventbus/examples/basic_usage.py

# Output:
# 📨 Received: workflow.started
#    Data: {'workflow_id': 'bia_001', 'stage': 'identify_processes'}
#    ...
```

### 3. Use in Service

```python
# In your FastAPI service
from fastapi import FastAPI
from infrastructure.eventbus import create_eventbus, Event

app = FastAPI()
bus = None

@app.on_event("startup")
async def startup():
    global bus
    bus = create_eventbus('memory')  # or 'redis'

@app.on_event("shutdown")
async def shutdown():
    await bus.close()

@app.post("/api/process")
async def create_process():
    # Create process...

    # Publish event
    event = Event.create(
        event_type='bia.process_created',
        data={'process_id': 123},
        source='bia-service',
        tenant_id='tenant_456'
    )
    await bus.publish(event)

    return {"status": "created"}
```

### 4. Subscribe in Another Service

```python
# In workflow-intelligence service
from infrastructure.eventbus import create_eventbus

bus = create_eventbus('memory')

async def handle_process_created(event: Event):
    process_id = event.data['process_id']
    print(f"New process: {process_id}")

    # Update workflow state...

await bus.subscribe('bia.process_created', handle_process_created)
```

## Common Patterns

### Pattern 1: Workflow Events

```python
# Publish workflow state changes
events = [
    Event.create('workflow.started', {...}, 'workflow-engine', 'tenant_123'),
    Event.create('workflow.stage_changed', {...}, 'workflow-engine', 'tenant_123'),
    Event.create('workflow.completed', {...}, 'workflow-engine', 'tenant_123'),
]

for event in events:
    await bus.publish(event)
```

### Pattern 2: Subscribe to All Service Events

```python
# Listen to all BIA service events
await bus.subscribe('bia.*', handle_bia_event)

# Listen to all events
await bus.subscribe('*', handle_any_event)
```

### Pattern 3: Priority Events

```python
# High priority event
event = Event.create(
    event_type='alert.system_failure',
    data={'service': 'database'},
    source='monitoring',
    tenant_id='tenant_123',
    priority=EventPriority.CRITICAL
)
await bus.publish(event)
```

## Switching to Redis (Production)

### 1. Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Or use existing Upstash Redis
```

### 2. Change One Line

```python
# Before (MVP)
bus = create_eventbus('memory')

# After (Production)
bus = create_eventbus('redis', redis_url='redis://localhost:6379')

# Or from environment
bus = create_eventbus_from_env()
```

### 3. Set Environment

```bash
# .env
EVENTBUS_BACKEND=redis
REDIS_URL=redis://localhost:6379
```

**That's it!** Same code, different backend.

## Testing

```bash
# Run tests
PYTHONPATH=. pytest infrastructure/eventbus/tests/ -v

# Run specific test
PYTHONPATH=. pytest infrastructure/eventbus/tests/test_memory_backend.py -v
```

## Next Steps

- Read full [README.md](README.md)
- Check [examples/](examples/) directory
- Integrate into your service
- Set up Redis for production

## Common Issues

### ImportError: No module named 'infrastructure'

**Solution:** Set PYTHONPATH

```bash
export PYTHONPATH=/Users/MD/AI-Platform-ISO
# or
PYTHONPATH=. python3 your_script.py
```

### Redis connection failed

**Solution:** Check Redis is running

```bash
redis-cli ping
# Should return: PONG
```

## Support

Questions? Check:
- [README.md](README.md) - Full documentation
- [examples/](examples/) - Working examples
- [tests/](tests/) - Test cases
