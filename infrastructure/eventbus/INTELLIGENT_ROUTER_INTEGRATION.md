# Intelligent EventBus Router - Integration Guide

## Overview

The **Intelligent EventBus Router** is an AI-powered event routing system that provides:

- **AI-powered event classification** - Automatic priority determination and complexity analysis
- **Semantic event matching** - Routes events to best-qualified subscribers using embeddings
- **Priority queues** - CRITICAL, HIGH, NORMAL, LOW with intelligent scheduling
- **Load-aware distribution** - Prevents subscriber overload with capacity management
- **Circuit breaker pattern** - Automatic failure detection and fallback routing
- **Comprehensive metrics** - Real-time monitoring and performance analytics

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Event Published                              │
└───────────────────────┬────────────────────────────────────────┘
                        │
        ┌───────────────▼───────────────┐
        │   AI Event Analyzer            │
        │   - Priority determination     │
        │   - Complexity scoring         │
        │   - Semantic embedding         │
        │   - Keyword extraction         │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │   Smart Subscriber Selector    │
        │   - Semantic matching          │
        │   - Load balancing             │
        │   - SLA awareness              │
        │   - Performance scoring        │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │    Priority Queue System       │
        │   ┌─────────────────────────┐ │
        │   │ CRITICAL (Prio 4)       │ │
        │   ├─────────────────────────┤ │
        │   │ HIGH (Prio 3)           │ │
        │   ├─────────────────────────┤ │
        │   │ NORMAL (Prio 2)         │ │
        │   ├─────────────────────────┤ │
        │   │ LOW (Prio 1)            │ │
        │   └─────────────────────────┘ │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │   Event Delivery               │
        │   - Concurrent processing      │
        │   - SLA monitoring             │
        │   - Circuit breaker            │
        │   - Retry logic                │
        └────────────────────────────────┘
```

## Quick Start

### 1. Basic Setup

```python
from infrastructure.eventbus.backends.memory import InMemoryEventBus
from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
from infrastructure.eventbus.core.events import Event, EventPriority

# Create base eventbus
eventbus = InMemoryEventBus()

# Create intelligent router
router = IntelligentEventRouter(
    base_eventbus=eventbus,
    enable_ai_analysis=True,
    enable_semantic_matching=True
)

# Initialize router
await router.initialize()
```

### 2. Register Subscribers with Capabilities

```python
# Define subscriber handler
async def handle_risk_event(event: Event):
    print(f"Processing risk event: {event.type}")
    # Your processing logic here
    await asyncio.sleep(0.5)  # Simulate work
    print(f"Completed: {event.id}")

# Register with capabilities
await router.register_subscriber(
    subscriber_id="risk_analyzer_1",
    event_pattern="risk.*",
    handler=handle_risk_event,
    capabilities={
        "domains": ["risk", "security", "threat_analysis"],
        "max_concurrent": 5,
        "avg_processing_time_ms": 300,
        "sla_ms": 1000,
        "semantic_tags": ["risk", "assessment", "vulnerability", "threat"]
    }
)
```

### 3. Publish Events

```python
# Create event
event = Event.create(
    event_type="risk.assessment_needed",
    data={
        "assessment_type": "cybersecurity",
        "urgency": "high",
        "description": "Critical vulnerability detected"
    },
    source="security-scanner",
    tenant_id="tenant_123",
    priority=EventPriority.HIGH
)

# Route event (AI will analyze and route intelligently)
decision = await router.route_event(event)

print(f"Routed to: {decision.selected_subscribers}")
print(f"Strategy: {decision.routing_strategy}")
print(f"Confidence: {decision.confidence_score:.2%}")
```

### 4. Monitor Metrics

```python
# Get routing metrics
metrics = router.get_metrics()

print(f"Total events: {metrics['total_events']}")
print(f"Routing efficiency: {metrics['routing_efficiency']:.2%}")
print(f"SLA compliance: {metrics['sla_compliance_rate']:.2%}")

# Get subscriber-specific metrics
sub_metrics = router.get_subscriber_metrics("risk_analyzer_1")
print(f"Success rate: {sub_metrics['success_rate']:.2%}")
print(f"Avg latency: {sub_metrics['avg_latency_ms']:.2f}ms")
print(f"Status: {sub_metrics['status']}")
```

## Advanced Features

### Subscriber Capabilities

Subscribers declare their capabilities to enable intelligent routing:

```python
capabilities = {
    # Domain expertise
    "domains": ["risk", "compliance", "security"],

    # Event patterns this subscriber handles
    # (event_pattern parameter also sets this)

    # Performance characteristics
    "max_concurrent": 10,  # Max concurrent events
    "avg_processing_time_ms": 500.0,  # Average processing time
    "sla_ms": 2000.0,  # SLA commitment

    # Priority preference (optional)
    "priority_preference": EventPriority.HIGH,

    # Semantic tags for matching
    "semantic_tags": [
        "risk", "threat", "vulnerability",
        "assessment", "mitigation"
    ]
}
```

### AI Event Analysis

The router automatically analyzes events to determine:

- **Priority**: Upgraded/downgraded based on content analysis
- **Complexity**: Score from 0.0-1.0 indicating processing difficulty
- **Category**: Extracted from event type and keywords
- **Semantic embedding**: Vector representation for semantic matching
- **Keywords**: Important terms extracted from event
- **SLA requirements**: Determined from priority and complexity

Example analysis output:

```python
EventAnalysis(
    event_id="abc123",
    determined_priority=EventPriority.CRITICAL,  # Upgraded from HIGH
    complexity_score=0.75,
    semantic_embedding=[0.23, -0.45, ...],  # 384-dim vector
    keywords=["critical", "vulnerability", "payment", "system"],
    category="risk",
    estimated_processing_time_ms=1500.0,
    sla_requirement_ms=500.0
)
```

### Smart Subscriber Selection

The router selects subscribers using a scoring algorithm:

```
score = (semantic_match × 0.4) +
        (load_level × 0.2) +
        (performance_history × 0.25) +
        (sla_compliance × 0.15)
```

Where:
- **Semantic match**: Cosine similarity between event and subscriber embeddings
- **Load level**: Current load vs. max capacity (prefer less loaded)
- **Performance history**: Success rate and average latency
- **SLA compliance**: Whether subscriber can meet SLA requirements

### Priority Queues

Events are queued by priority:

| Priority | SLA Target | Use Case |
|----------|-----------|----------|
| CRITICAL | 500ms | System failures, security breaches, data loss |
| HIGH | 2s | Important events, warnings, escalations |
| NORMAL | 5s | Standard events, routine operations |
| LOW | 30s | Background tasks, logging, analytics |

Priority is determined by:
1. Event's declared priority
2. AI analysis of content (can upgrade/downgrade)
3. Keywords in event type and data
4. Historical patterns

### Circuit Breaker

Automatic failure protection:

```python
router = IntelligentEventRouter(
    base_eventbus=eventbus,
    circuit_breaker_threshold=5,  # Open after 5 consecutive failures
    circuit_breaker_timeout_seconds=60  # Retry after 60 seconds
)
```

States:
- **HEALTHY**: Normal operation
- **DEGRADED**: Some failures (warning state)
- **FAILED**: Too many errors
- **CIRCUIT_OPEN**: Temporarily disabled, will retry after timeout

### Load-Aware Routing

The router tracks real-time subscriber load:

```python
# Subscriber metrics tracked automatically
SubscriberMetrics(
    subscriber_id="risk_analyzer_1",
    current_load=3,  # Currently processing 3 events
    total_processed=1247,
    total_errors=5,
    total_timeouts=2,
    avg_latency_ms=342.5,
    sla_violations=8,
    success_rate=0.996,  # 99.6% success
    status=SubscriberStatus.HEALTHY
)
```

The router won't route to subscribers at max capacity.

## Integration Patterns

### Pattern 1: Microservice Integration

```python
# In each microservice's startup

from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
from infrastructure.eventbus.backends.redis_streams import RedisStreamEventBus

# Create router with Redis backend
redis_bus = RedisStreamEventBus(redis_url="redis://localhost:6379")
router = IntelligentEventRouter(base_eventbus=redis_bus)
await router.initialize()

# Register service's capabilities
await router.register_subscriber(
    subscriber_id=f"{SERVICE_NAME}_instance_{INSTANCE_ID}",
    event_pattern=f"{SERVICE_DOMAIN}.*",
    handler=handle_domain_event,
    capabilities={
        "domains": [SERVICE_DOMAIN],
        "max_concurrent": config.MAX_CONCURRENT,
        "avg_processing_time_ms": config.AVG_PROCESSING_TIME,
        "sla_ms": config.SLA_MS,
        "semantic_tags": SERVICE_TAGS
    }
)

# Publish events through router
await router.route_event(event)
```

### Pattern 2: Multi-Tenant Routing

```python
# Route based on tenant capabilities

class TenantAwareRouter(IntelligentEventRouter):
    def __init__(self, *args, tenant_registry, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_registry = tenant_registry

    async def route_event(self, event: Event):
        # Check tenant subscription level
        tenant = await self.tenant_registry.get_tenant(event.tenant_id)

        # Adjust routing based on subscription
        if tenant.subscription_tier == "premium":
            # Premium tenants get priority
            if event.priority == EventPriority.NORMAL:
                event.priority = EventPriority.HIGH

        return await super().route_event(event)
```

### Pattern 3: Hybrid Routing

```python
# Combine intelligent routing with simple routing

class HybridRouter:
    def __init__(self, intelligent_router, simple_eventbus):
        self.intelligent = intelligent_router
        self.simple = simple_eventbus

    async def route_event(self, event: Event):
        # Complex events → intelligent routing
        if self._is_complex(event):
            return await self.intelligent.route_event(event)

        # Simple events → direct routing (faster)
        else:
            await self.simple.publish(event)
            return None

    def _is_complex(self, event: Event) -> bool:
        # Determine if event needs intelligent routing
        return (
            event.priority in [EventPriority.CRITICAL, EventPriority.HIGH] or
            "analysis" in event.type or
            "assessment" in event.type or
            len(str(event.data)) > 1000
        )
```

### Pattern 4: A/B Testing Routing

```python
# Compare intelligent vs. simple routing

class ABTestingRouter:
    def __init__(self, intelligent_router, simple_eventbus):
        self.intelligent = intelligent_router
        self.simple = simple_eventbus
        self.ab_ratio = 0.5  # 50/50 split

    async def route_event(self, event: Event):
        import random

        # Randomly choose routing method
        use_intelligent = random.random() < self.ab_ratio

        # Tag event for analytics
        event.data["_routing_method"] = (
            "intelligent" if use_intelligent else "simple"
        )

        if use_intelligent:
            return await self.intelligent.route_event(event)
        else:
            await self.simple.publish(event)
            return None
```

## Production Deployment

### Configuration

```python
# production_config.py

from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
from infrastructure.eventbus.backends.redis_streams import RedisStreamEventBus
import os

def create_production_router():
    # Use Redis for production
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_bus = RedisStreamEventBus(redis_url=redis_url)

    # Create router with production settings
    router = IntelligentEventRouter(
        base_eventbus=redis_bus,
        enable_ai_analysis=True,
        enable_semantic_matching=True,
        circuit_breaker_threshold=5,
        circuit_breaker_timeout_seconds=60
    )

    return router

# In main.py
router = create_production_router()
await router.initialize()
```

### Monitoring

```python
# Export metrics to Prometheus

from prometheus_client import Counter, Histogram, Gauge

# Define metrics
events_total = Counter('eventbus_events_total', 'Total events routed')
routing_duration = Histogram('eventbus_routing_duration_seconds', 'Event routing duration')
subscriber_load = Gauge('eventbus_subscriber_load', 'Current subscriber load', ['subscriber_id'])

# Update metrics
async def route_with_metrics(router, event):
    events_total.inc()

    with routing_duration.time():
        decision = await router.route_event(event)

    # Update subscriber load
    metrics = router.get_metrics()
    for sub_id, sub_metrics in metrics['subscriber_metrics'].items():
        subscriber_load.labels(subscriber_id=sub_id).set(
            sub_metrics['current_load']
        )

    return decision
```

### Health Checks

```python
# Health check endpoint

from fastapi import FastAPI

app = FastAPI()

@app.get("/health/eventbus")
async def eventbus_health():
    metrics = router.get_metrics()

    # Check if router is healthy
    healthy_ratio = (
        metrics['healthy_subscribers'] /
        max(metrics['registered_subscribers'], 1)
    )

    is_healthy = (
        healthy_ratio >= 0.5 and  # At least 50% subscribers healthy
        metrics['routing_efficiency'] >= 0.9  # At least 90% routing success
    )

    return {
        "status": "healthy" if is_healthy else "degraded",
        "metrics": {
            "total_events": metrics['total_events'],
            "routing_efficiency": metrics['routing_efficiency'],
            "sla_compliance": metrics['sla_compliance_rate'],
            "healthy_subscribers": metrics['healthy_subscribers'],
            "total_subscribers": metrics['registered_subscribers']
        }
    }
```

### Graceful Shutdown

```python
# Shutdown handler

import signal
import asyncio

async def shutdown_handler(router):
    """Gracefully shutdown router"""
    print("Shutting down intelligent router...")

    # Stop accepting new events
    router.running = False

    # Wait for queue to drain (max 30s)
    for _ in range(30):
        metrics = router.get_metrics()
        total_queued = sum(metrics['queue_depths'].values())

        if total_queued == 0:
            break

        print(f"Waiting for {total_queued} events to process...")
        await asyncio.sleep(1)

    # Shutdown router
    await router.shutdown()
    print("Router shutdown complete")

# Register signal handlers
def setup_shutdown_handlers(router):
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown_handler(router))
        )
```

## Performance Tuning

### Optimize for Throughput

```python
# High throughput configuration

router = IntelligentEventRouter(
    base_eventbus=redis_bus,
    enable_ai_analysis=False,  # Disable for speed
    enable_semantic_matching=False  # Use simple pattern matching
)

# Register with higher capacities
await router.register_subscriber(
    subscriber_id="high_throughput_worker",
    event_pattern="events.*",
    handler=fast_handler,
    capabilities={
        "max_concurrent": 50,  # Higher concurrency
        "avg_processing_time_ms": 50,  # Fast processing
        "sla_ms": 100
    }
)
```

### Optimize for Quality

```python
# High quality configuration (best routing decisions)

router = IntelligentEventRouter(
    base_eventbus=redis_bus,
    enable_ai_analysis=True,  # Full AI analysis
    enable_semantic_matching=True  # Semantic matching
)

# Register with detailed capabilities
await router.register_subscriber(
    subscriber_id="quality_analyzer",
    event_pattern="analysis.*",
    handler=detailed_handler,
    capabilities={
        "domains": ["risk", "compliance", "security", "audit"],
        "max_concurrent": 3,  # Lower concurrency for quality
        "avg_processing_time_ms": 2000,  # Allow more time
        "sla_ms": 5000,
        "semantic_tags": [
            "risk", "assessment", "vulnerability", "threat",
            "compliance", "audit", "standard", "regulation"
        ]
    }
)
```

## Testing

### Unit Tests

```python
import pytest
from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
from infrastructure.eventbus.backends.memory import InMemoryEventBus

@pytest.mark.asyncio
async def test_basic_routing():
    # Setup
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(base_eventbus=eventbus)
    await router.initialize()

    # Register subscriber
    events_received = []

    async def handler(event):
        events_received.append(event)

    await router.register_subscriber(
        subscriber_id="test_sub",
        event_pattern="test.*",
        handler=handler
    )

    # Publish event
    event = Event.create(
        event_type="test.event",
        data={"test": "data"},
        source="test",
        tenant_id="test"
    )

    decision = await router.route_event(event)

    # Wait for processing
    await asyncio.sleep(0.5)

    # Assert
    assert len(events_received) == 1
    assert decision.selected_subscribers == ["test_sub"]

    # Cleanup
    await router.shutdown()
```

### Integration Tests

See `/infrastructure/eventbus/examples/intelligent_routing_example.py` for comprehensive integration test scenarios.

## Troubleshooting

### Events Not Being Routed

Check:
1. Is router initialized? `await router.initialize()`
2. Are there registered subscribers? `router.get_metrics()['registered_subscribers']`
3. Do event patterns match? Check pattern matching logic
4. Are subscribers available? Check circuit breaker status

### High Latency

Check:
1. Subscriber processing times: `sub_metrics['avg_latency_ms']`
2. Queue depths: `metrics['queue_depths']`
3. Subscriber load: `sub_metrics['current_load']`
4. Enable/disable AI analysis based on needs

### Circuit Breakers Opening

Check:
1. Subscriber error logs
2. Consecutive failure count: `sub_metrics['consecutive_failures']`
3. Adjust threshold if needed: `circuit_breaker_threshold`
4. Review subscriber SLA settings

## API Reference

### IntelligentEventRouter

Main router class.

**Constructor:**
```python
IntelligentEventRouter(
    base_eventbus: IEventBus,
    enable_ai_analysis: bool = True,
    enable_semantic_matching: bool = True,
    circuit_breaker_threshold: int = 5,
    circuit_breaker_timeout_seconds: int = 60
)
```

**Methods:**

- `async initialize()` - Initialize and start router
- `async shutdown()` - Gracefully shutdown router
- `async register_subscriber(...)` - Register intelligent subscriber
- `async unregister_subscriber(subscriber_id)` - Unregister subscriber
- `async route_event(event)` - Route event intelligently
- `get_metrics()` - Get comprehensive routing metrics
- `get_subscriber_metrics(subscriber_id)` - Get subscriber-specific metrics

## Examples

Full working examples available in:
- `/infrastructure/eventbus/examples/intelligent_routing_example.py`

Run examples:
```bash
cd /Users/MD/AI-Platform-ISO
python -m infrastructure.eventbus.examples.intelligent_routing_example
```

## Support

For issues or questions:
1. Check logs for error messages
2. Review metrics for performance insights
3. Consult examples for usage patterns
4. Check circuit breaker states for subscriber health

## Future Enhancements

Planned features:
- [ ] Machine learning-based routing optimization
- [ ] Event pattern learning and suggestion
- [ ] Automatic subscriber capability discovery
- [ ] Advanced SLA prediction
- [ ] Multi-region routing
- [ ] Event replay capabilities
- [ ] A/B testing framework
- [ ] Cost-based routing optimization
