# Self-Aware Services - Shared Components

**Foundation for graceful event choreography in AI Platform ISO**

This package provides components that enable services to be self-aware, adaptive, and collaborative. Services can make intelligent decisions about event handling, manage their load gracefully, and collaborate with other services for distributed consensus.

## Components

### 1. SelfAwareService (Base Class)

The core class that makes services intelligent and adaptive.

**Features:**
- Automatic capability matching
- Load-aware event handling
- Health-based decisions
- Graceful degradation
- Service collaboration
- AI-powered decision making

**Example:**

```python
from _shared import SelfAwareService, EventPriority, EventContext

class BIAService(SelfAwareService):
    def __init__(self):
        super().__init__(
            service_name="bia",
            capabilities=[
                "bia.assessment.create",
                "bia.assessment.complete",
                "bia.process.analyze"
            ],
            enable_ai_decisions=True,
            enable_collaboration=True
        )

        # Register event handlers
        self.register_handler("bia.assessment.*", self.handle_assessment)
        self.register_handler("bia.process.*", self.handle_process)

        # Mark essential capabilities
        self.mark_essential("bia.assessment.create")

    async def handle_assessment(self, ctx: EventContext):
        """Handle BIA assessment events"""
        # Your business logic here
        pass

    async def handle_process(self, ctx: EventContext):
        """Handle BIA process events"""
        # Your business logic here
        pass

# Usage
service = BIAService()

# Handle an event
result = await service.on_event(
    "bia.assessment.completed",
    {"process_id": 123, "criticality": "HIGH"},
    tenant_id="tenant-1",
    priority=EventPriority.HIGH
)

if result.decision == HandlingDecision.HANDLE:
    await result.handler(EventContext(...))
elif result.decision == HandlingDecision.DEFER:
    # Queue for later
    pass
```

### 2. HealthMonitor

Self-monitoring component for tracking service health.

**Features:**
- Continuous health checks
- Dependency monitoring (DB, Redis, EventBus)
- Automatic degradation detection
- Health metrics collection
- Alert generation

**Example:**

```python
from _shared import HealthMonitor, check_database_health, check_redis_health

monitor = HealthMonitor("bia")
await monitor.start()

# Register dependency checks
monitor.register_check("database", lambda: check_database_health(db))
monitor.register_check("redis", lambda: check_redis_health(redis))

# Get current status
status = await monitor.get_status()
print(f"Health: {status.status.value}")
print(f"Uptime: {status.metadata['metrics']['uptime_seconds']}s")

# Record request metrics
monitor.record_request(duration_ms=150.5, error=False)

# Manually set status
await monitor.set_degraded("High error rate")
await monitor.set_healthy()
```

### 3. CapabilityRegistry

Tracks service capabilities and enables intelligent routing.

**Features:**
- Capability registration and discovery
- Pattern matching (wildcards)
- Tag-based matching
- Expertise-based ranking
- Version compatibility
- Enable/disable capabilities

**Example:**

```python
from _shared import CapabilityRegistry, Capability, ExpertiseLevel

registry = CapabilityRegistry()

# Register capabilities
registry.register(Capability(
    name="bia.assessment.create",
    service="bia",
    expertise=ExpertiseLevel.EXPERT,
    description="Create BIA assessments",
    tags={"bcm", "assessment", "critical"}
))

registry.register(Capability(
    name="bia.process.analyze",
    service="bia",
    expertise=ExpertiseLevel.PROFICIENT,
    tags={"bcm", "analysis"}
))

# Find capabilities
matches = registry.find_capabilities("bia.*")
for match in matches:
    print(f"{match.capability.name}: {match.score:.2f} ({match.reason})")

# Find by tag
assessment_caps = registry.find_by_tag("assessment")

# Disable capability (graceful degradation)
registry.disable_capability("bia.process.analyze", "bia")
```

### 4. LoadManager

Monitors and manages service load.

**Features:**
- Real-time load monitoring
- Capacity estimation
- Automatic degradation
- Load shedding
- Queue management
- Predictive load forecasting

**Example:**

```python
from _shared import LoadManager, LoadPolicy, LoadLevel

# Custom policy
policy = LoadPolicy(
    degradation_threshold=0.85,
    enable_auto_degradation=True,
    enable_load_shedding=True
)

load_manager = LoadManager(
    "bia",
    policy=policy,
    max_concurrent_requests=100
)
await load_manager.start()

# Set callbacks
load_manager.set_degradation_callback(service.degrade_gracefully)
load_manager.set_recovery_callback(service.recover_from_degradation)

# Check if can accept
if await load_manager.can_accept(priority="high"):
    await load_manager.track_request_start()
    # Process request
    await load_manager.track_request_end(duration_ms=150.0)

# Get load level
level = await load_manager.get_load_level()
if level == LoadLevel.HIGH:
    print("Service under high load")

# Predict future load
predicted = await load_manager.predict_load(seconds_ahead=60)
print(f"Predicted load in 1min: {predicted:.2%}")
```

### 5. CollaborationMixin

Enables service collaboration and consensus decisions.

**Features:**
- Consensus requests (UNANIMOUS, MAJORITY, QUORUM)
- Distributed voting
- Alternative handler discovery
- Status broadcasting
- Service coordination

**Example:**

```python
from _shared import CollaborationMixin, ConsensusStrategy, Vote, VoteType

collaboration = CollaborationMixin("bia", eventbus_client)

# Register vote handler
async def approve_plan(context):
    plan_id = context.get("plan_id")
    # Analyze plan...
    return Vote(
        service="bia",
        vote=VoteType.APPROVE,
        confidence=0.95,
        reasoning="BIA data supports this plan"
    )

collaboration.register_vote_handler("plan_approval", approve_plan)

# Request consensus
decision = await collaboration.request_consensus(
    participants=["risk", "compliance", "governance"],
    context={"type": "plan_approval", "plan_id": 123},
    strategy=ConsensusStrategy.MAJORITY,
    timeout_seconds=30
)

if decision.consensus_reached:
    print(f"Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Votes: {decision.participants_responded}/{decision.total_participants}")

# Find alternative handlers
alternatives = await collaboration.find_alternative_handlers("bia.assessment")
print(f"Can delegate to: {alternatives}")

# Broadcast status
await collaboration.broadcast_status("degraded", {"reason": "High load"})
```

## Integration Guide

### Step 1: Update Service Class

```python
# Before
class BIAServiceOld:
    def __init__(self):
        self.name = "bia"

    async def handle_event(self, event):
        # Always handles everything
        await self.process(event)

# After
from _shared import SelfAwareService, EventPriority

class BIAService(SelfAwareService):
    def __init__(self):
        super().__init__(
            service_name="bia",
            capabilities=["bia.assessment", "bia.process"]
        )
        self.register_handler("bia.*", self.handle_bia_event)

    async def handle_bia_event(self, ctx):
        # Intelligent handling with load awareness
        result = await self.on_event(
            ctx.event_type,
            ctx.event_data,
            priority=ctx.priority
        )

        if result.decision == HandlingDecision.HANDLE:
            await self.process(ctx)
        elif result.decision == HandlingDecision.DEFER:
            await self.queue_for_later(ctx)
```

### Step 2: Add Health Checks

```python
from _shared import HealthMonitor, check_database_health

# In your service initialization
self.health_monitor = HealthMonitor(self.service_name)
await self.health_monitor.start()

# Register checks
self.health_monitor.register_check(
    "database",
    lambda: check_database_health(self.db)
)
```

### Step 3: Enable Load Management

```python
from _shared import LoadManager, LoadPolicy

# In your service initialization
self.load_manager = LoadManager(
    self.service_name,
    policy=LoadPolicy(enable_auto_degradation=True),
    max_concurrent_requests=100
)
await self.load_manager.start()

# Set degradation callback
self.load_manager.set_degradation_callback(self.degrade_gracefully)
```

### Step 4: Add Collaboration

```python
from _shared import CollaborationMixin

# In your service initialization
self.collaboration = CollaborationMixin(
    self.service_name,
    eventbus_client=self.eventbus
)

# Register vote handlers
self.collaboration.register_vote_handler(
    "plan_approval",
    self.vote_on_plan
)
```

## Complete Example: BIA Service Integration

```python
# File: bia_service/self_aware_bia.py

from _shared import (
    SelfAwareService,
    EventPriority,
    EventContext,
    HandlingDecision,
    LoadPolicy
)

class SelfAwareBIAService(SelfAwareService):
    """
    Self-aware BIA service with graceful choreography.
    """

    def __init__(self, db, redis, eventbus):
        super().__init__(
            service_name="bia",
            capabilities=[
                "bia.assessment.create",
                "bia.assessment.update",
                "bia.assessment.complete",
                "bia.process.analyze",
                "bia.criticality.assess",
                "bia.dependencies.map"
            ],
            load_policy=LoadPolicy(
                degradation_threshold=0.85,
                enable_auto_degradation=True
            ),
            enable_ai_decisions=True,
            enable_collaboration=True
        )

        self.db = db
        self.redis = redis
        self.eventbus = eventbus

        # Mark essential capabilities
        self.mark_essential("bia.assessment.create")
        self.mark_essential("bia.assessment.complete")

        # Register handlers
        self.register_handler("bia.assessment.*", self.handle_assessment)
        self.register_handler("bia.process.*", self.handle_process)

        # Setup health monitoring
        self._setup_health_monitoring()

        # Setup collaboration
        self._setup_collaboration()

    def _setup_health_monitoring(self):
        """Setup health checks"""
        from _shared import check_database_health, check_redis_health

        self.health_monitor.register_check(
            "database",
            lambda: check_database_health(self.db)
        )
        self.health_monitor.register_check(
            "redis",
            lambda: check_redis_health(self.redis)
        )

    def _setup_collaboration(self):
        """Setup collaboration handlers"""
        self.collaboration.register_vote_handler(
            "plan_approval",
            self.vote_on_plan
        )

    async def handle_assessment(self, ctx: EventContext):
        """Handle BIA assessment events"""
        event_type = ctx.event_type
        data = ctx.event_data

        # Track request
        await self.load_manager.track_request_start()

        try:
            if event_type == "bia.assessment.create":
                result = await self._create_assessment(data)
            elif event_type == "bia.assessment.complete":
                result = await self._complete_assessment(data)
            else:
                result = None

            # Record success
            self.health_monitor.record_request(
                duration_ms=100.0,
                error=False
            )

            return result

        except Exception as e:
            # Record error
            self.health_monitor.record_request(
                duration_ms=100.0,
                error=True
            )
            raise
        finally:
            await self.load_manager.track_request_end()

    async def handle_process(self, ctx: EventContext):
        """Handle BIA process events"""
        # Similar to handle_assessment
        pass

    async def vote_on_plan(self, context):
        """Vote on plan approval"""
        from _shared import Vote, VoteType

        plan_id = context.get("plan_id")

        # Check if BIA data supports this plan
        bia_data = await self._get_bia_data_for_plan(plan_id)

        if bia_data and bia_data.get("criticality") == "HIGH":
            return Vote(
                service=self.service_name,
                vote=VoteType.APPROVE,
                confidence=0.95,
                reasoning="High criticality processes covered"
            )
        else:
            return Vote(
                service=self.service_name,
                vote=VoteType.ABSTAIN,
                confidence=0.5,
                reasoning="Insufficient BIA data"
            )

    async def _create_assessment(self, data):
        """Create BIA assessment"""
        # Your business logic
        pass

    async def _complete_assessment(self, data):
        """Complete BIA assessment"""
        # Your business logic
        pass

    async def _get_bia_data_for_plan(self, plan_id):
        """Get BIA data for plan"""
        # Query database
        pass

# Usage in main.py
service = SelfAwareBIAService(db, redis, eventbus)
await service.health_monitor.start()
await service.load_manager.start()

# Handle events
result = await service.on_event(
    "bia.assessment.completed",
    {"process_id": 123},
    priority=EventPriority.HIGH
)
```

## Metrics and Observability

All components provide metrics that can be exposed via Prometheus:

```python
# Get metrics from all components
metrics = {
    "service": service.get_metrics(),
    "health": service.health_monitor.get_metrics(),
    "load": await service.load_manager.get_metrics(),
    "collaboration": service.collaboration.get_metrics()
}

# Example output:
{
    "service": {
        "events_received": 1543,
        "events_handled": 1520,
        "events_deferred": 15,
        "events_delegated": 5,
        "events_rejected": 3,
        "degraded_mode": false
    },
    "health": {
        "uptime_seconds": 3600,
        "error_rate": 0.002,
        "avg_response_time_ms": 45.3
    },
    "load": {
        "current_load": 0.65,
        "active_requests": 32,
        "queued_events": 8
    },
    "collaboration": {
        "consensus_requests": 12,
        "consensus_approved": 10,
        "votes_cast": 45
    }
}
```

## Graceful Degradation Example

```python
# Service automatically degrades under load
service = SelfAwareBIAService(...)

# When load exceeds threshold, non-essential capabilities are disabled
await service.degrade_gracefully("High load detected")

# Now only essential events are handled
result = await service.on_event(
    "bia.process.analyze",  # Non-essential
    {},
    priority=EventPriority.NORMAL
)
# Result: DEFER or DELEGATE

result = await service.on_event(
    "bia.assessment.create",  # Essential
    {},
    priority=EventPriority.HIGH
)
# Result: HANDLE

# Recovery when load decreases
await service.recover_from_degradation()
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SelfAwareService                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Health       │  │ Capability   │  │ Load         │      │
│  │ Monitor      │  │ Registry     │  │ Manager      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Event Decision Engine                    │       │
│  │  1. Should I handle? (Capability match)         │       │
│  │  2. Can I handle? (Health + Load)               │       │
│  │  3. How to handle? (Priority + Policy)          │       │
│  │  4. Collaborate? (Consensus needed)             │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Collaboration Mixin                      │       │
│  │  - Consensus requests                            │       │
│  │  - Distributed voting                            │       │
│  │  - Alternative handlers                          │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │      EventBus          │
              │   (RabbitMQ)           │
              └────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │   BIA   │       │  Risk   │       │ Plans   │
   │ Service │       │ Service │       │ Service │
   └─────────┘       └─────────┘       └─────────┘
```

## Best Practices

1. **Always register essential capabilities**
   ```python
   self.mark_essential("bia.assessment.create")
   ```

2. **Use appropriate priorities**
   ```python
   EventPriority.CRITICAL  # Must handle
   EventPriority.HIGH      # Handle if capacity
   EventPriority.NORMAL    # Standard handling
   EventPriority.LOW       # Defer if load
   EventPriority.BACKGROUND # Only when idle
   ```

3. **Handle all decision types**
   ```python
   result = await service.on_event(...)

   if result.decision == HandlingDecision.HANDLE:
       await result.handler(ctx)
   elif result.decision == HandlingDecision.DEFER:
       await queue_event(ctx)
   elif result.decision == HandlingDecision.DELEGATE:
       await delegate_to(result.delegate_to, ctx)
   ```

4. **Monitor metrics**
   ```python
   metrics = service.get_metrics()
   if metrics["degraded_mode"]:
       alert("Service degraded!")
   ```

5. **Test degradation scenarios**
   ```python
   # Simulate high load
   for i in range(200):
       await service.on_event(...)

   # Should auto-degrade
   assert service._degraded_mode
   ```

## Testing

See `tests/test_self_aware_services.py` for comprehensive test examples.

## License

MIT License - AI Platform ISO

## Support

For questions or issues, contact the platform team or consult the main documentation.
