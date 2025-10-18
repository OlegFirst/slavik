# Quick Start Guide - Self-Aware Services

Get started with self-aware services in 5 minutes.

## 1. Basic Service (Minimal Setup)

```python
from _shared import SelfAwareService, EventPriority, HandlingDecision

class MyService(SelfAwareService):
    def __init__(self):
        super().__init__(
            service_name="my_service",
            capabilities=["my_service.action"]
        )

        # Register handler
        self.register_handler("my_service.*", self.handle_event)

    async def handle_event(self, ctx):
        print(f"Handling {ctx.event_type}")
        return {"status": "success"}

# Usage
service = MyService()

# Handle an event
result = await service.on_event(
    "my_service.action",
    {"data": "test"},
    priority=EventPriority.NORMAL
)

if result.decision == HandlingDecision.HANDLE:
    await result.handler(ctx)
```

## 2. With Health Monitoring

```python
from _shared import SelfAwareService, check_database_health

class MyService(SelfAwareService):
    def __init__(self, db):
        super().__init__(
            service_name="my_service",
            capabilities=["my_service.action"]
        )
        self.db = db

        # Setup health monitoring
        self.health_monitor.register_check(
            "database",
            lambda: check_database_health(self.db)
        )

    async def start(self):
        await self.health_monitor.start()

service = MyService(db)
await service.start()

# Check health
status = await service.health_monitor.get_status()
print(f"Health: {status.status.value}")
```

## 3. With Load Management

```python
from _shared import SelfAwareService, LoadPolicy

class MyService(SelfAwareService):
    def __init__(self):
        super().__init__(
            service_name="my_service",
            capabilities=["my_service.action"],
            load_policy=LoadPolicy(
                degradation_threshold=0.85,
                enable_auto_degradation=True
            )
        )

        # Set degradation callback
        self.load_manager.set_degradation_callback(
            self.degrade_gracefully
        )

    async def start(self):
        await self.load_manager.start()

service = MyService()
await service.start()

# Handle with load awareness
if await service.load_manager.can_accept("normal"):
    await service.load_manager.track_request_start()
    # Process request
    await service.load_manager.track_request_end()
```

## 4. With Collaboration

```python
from _shared import SelfAwareService, Vote, VoteType

class MyService(SelfAwareService):
    def __init__(self, eventbus):
        super().__init__(
            service_name="my_service",
            capabilities=["my_service.action"],
            enable_collaboration=True
        )
        self.collaboration.eventbus = eventbus

        # Register vote handler
        self.collaboration.register_vote_handler(
            "approval",
            self.vote_on_approval
        )

    async def vote_on_approval(self, context):
        # Make decision
        return Vote(
            service=self.service_name,
            vote=VoteType.APPROVE,
            confidence=0.9,
            reasoning="Looks good"
        )

# Request consensus
decision = await service.collaboration.request_consensus(
    participants=["other_service"],
    context={"type": "approval", "item_id": 123}
)

print(f"Consensus: {decision.decision}")
```

## 5. Complete Integration

```python
from _shared import (
    SelfAwareService,
    EventPriority,
    HandlingDecision,
    LoadPolicy,
    check_database_health,
    Vote,
    VoteType
)

class BIAService(SelfAwareService):
    def __init__(self, db, redis, eventbus):
        super().__init__(
            service_name="bia",
            capabilities=[
                "bia.assessment.create",
                "bia.assessment.complete"
            ],
            load_policy=LoadPolicy(
                degradation_threshold=0.85,
                enable_auto_degradation=True
            ),
            enable_collaboration=True
        )

        self.db = db
        self.redis = redis
        self.eventbus = eventbus

        # Mark essential capabilities
        self.mark_essential("bia.assessment.create")

        # Register handlers
        self.register_handler("bia.assessment.*", self.handle_assessment)

        # Setup health checks
        self.health_monitor.register_check(
            "database",
            lambda: check_database_health(self.db)
        )

        # Setup collaboration
        self.collaboration.eventbus = eventbus
        self.collaboration.register_vote_handler(
            "plan_approval",
            self.vote_on_plan
        )

    async def handle_assessment(self, ctx):
        # Track load
        await self.load_manager.track_request_start()

        try:
            # Business logic
            result = await self.create_assessment(ctx.event_data)

            # Record metrics
            self.health_monitor.record_request(100.0, error=False)

            return result

        finally:
            await self.load_manager.track_request_end()

    async def vote_on_plan(self, context):
        # Voting logic
        return Vote(
            service=self.service_name,
            vote=VoteType.APPROVE,
            confidence=0.95
        )

    async def start(self):
        await self.health_monitor.start()
        await self.load_manager.start()

# Usage
service = BIAService(db, redis, eventbus)
await service.start()

# Handle events intelligently
result = await service.on_event(
    "bia.assessment.create",
    {"name": "Test"},
    priority=EventPriority.HIGH
)
```

## 6. In FastAPI

```python
# main.py
from fastapi import FastAPI
from _shared import SelfAwareService, EventPriority, HandlingDecision

app = FastAPI()
service = None

@app.on_event("startup")
async def startup():
    global service
    service = BIAService(db, redis, eventbus)
    await service.start()

@app.on_event("shutdown")
async def shutdown():
    await service.health_monitor.stop()
    await service.load_manager.stop()

@app.post("/api/assessments")
async def create_assessment(data: dict):
    # Use self-aware handling
    result = await service.on_event(
        "bia.assessment.create",
        data,
        priority=EventPriority.HIGH
    )

    if result.decision == HandlingDecision.HANDLE:
        return await result.handler(EventContext(...))
    elif result.decision == HandlingDecision.DEFER:
        return {"status": "queued", "message": "Service busy"}
    else:
        return {"status": "error", "message": result.reasoning}

@app.get("/health")
async def health():
    status = await service.health_monitor.get_status()
    return {
        "status": status.status.value,
        "metrics": status.metadata
    }

@app.get("/metrics")
async def metrics():
    return service.get_metrics()
```

## 7. With Prometheus Metrics

```python
from _shared import get_metrics_collector
from prometheus_client import make_asgi_app

# In your service
metrics = get_metrics_collector("bia")

# Record events
metrics.record_event_received("bia.assessment.create", "high")
metrics.record_event_handled("bia.assessment.create", "handle", 0.150)

# Update health
metrics.update_health_status("healthy")
metrics.update_load(0.65)

# Mount Prometheus endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

## Common Patterns

### Pattern 1: Essential vs Non-Essential

```python
# Mark critical capabilities
service.mark_essential("bia.assessment.create")
service.mark_essential("bia.process.critical")

# Under load, only essential capabilities remain enabled
await service.degrade_gracefully("High load")
```

### Pattern 2: Event Priorities

```python
# Critical - Always handle
EventPriority.CRITICAL

# High - Handle if capacity available
EventPriority.HIGH

# Normal - Standard handling
EventPriority.NORMAL

# Low - Defer if under load
EventPriority.LOW

# Background - Only when idle
EventPriority.BACKGROUND
```

### Pattern 3: Graceful Degradation

```python
# Automatic degradation
service.load_manager.set_degradation_callback(
    service.degrade_gracefully
)

# Manual degradation
await service.degrade_gracefully("External trigger")

# Recovery
await service.recover_from_degradation()
```

### Pattern 4: Collaboration

```python
# Request consensus
decision = await service.collaboration.request_consensus(
    participants=["risk", "compliance"],
    context={"type": "plan_approval", "plan_id": 123},
    strategy=ConsensusStrategy.MAJORITY
)

# Cast vote
vote = await service.collaboration.cast_vote(
    request_id,
    context
)
```

## Testing

```python
import pytest

@pytest.mark.asyncio
async def test_service():
    service = MyService()

    result = await service.on_event(
        "my_service.action",
        {},
        priority=EventPriority.NORMAL
    )

    assert result.decision == HandlingDecision.HANDLE
```

## Monitoring

```bash
# Prometheus queries
selfaware_events_received_total{service="bia"}
selfaware_service_health_status{service="bia"}
selfaware_current_load_percentage{service="bia"}
```

## Troubleshooting

### Service not handling events?
```python
# Check capability registration
print(service.capability_registry.list_capabilities())

# Check health
status = await service.health_monitor.get_status()
print(status.status.value)

# Check load
level = await service.load_manager.get_load_level()
print(level.value)
```

### High load?
```python
# Get metrics
metrics = await service.load_manager.get_metrics()
print(f"Load: {metrics.current_load:.2%}")
print(f"Active: {metrics.active_requests}")
print(f"Queued: {metrics.queued_events}")

# Predict future load
predicted = await service.load_manager.predict_load(60)
print(f"Predicted (1min): {predicted:.2%}")
```

### Degraded mode?
```python
# Check if degraded
print(f"Degraded: {service._degraded_mode}")

# Get reason
print(f"Reason: {service.health_monitor._degraded_reason}")

# Force recovery
await service.recover_from_degradation()
```

## Next Steps

1. Read [README.md](README.md) for detailed documentation
2. Check [example_bia_integration.py](example_bia_integration.py) for complete example
3. Run tests: `pytest test_self_aware_services.py -v`
4. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture

## Support

- Documentation: See README.md
- Examples: See example_bia_integration.py
- Tests: See test_self_aware_services.py
- Issues: Contact platform team
