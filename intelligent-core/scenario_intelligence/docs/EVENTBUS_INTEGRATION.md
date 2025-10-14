# EventBus Integration for Scenario Intelligence

## Overview

The Scenario Intelligence system is fully integrated with the platform's EventBus to enable:
- **Event-driven scenario generation**: Automatically regenerate scenarios when services change
- **Real-time monitoring**: MIO Manager tracks all scenario activities
- **Choreography**: Coordinate with other platform services through events
- **Auto-regeneration**: Keep scenarios synchronized with the platform state

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        EventBus (Redis)                          │
│                   (infrastructure/eventbus)                      │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                   │
             │ Publishes                         │ Subscribes
             ▼                                   ▼
┌────────────────────────────┐    ┌─────────────────────────────┐
│  Scenario Intelligence     │    │      MIO Manager            │
│                            │    │                             │
│  - Generation Manager      │    │  - Monitors scenarios       │
│  - Scenario Engine         │    │  - Tracks metrics           │
│  - Auto-Regen Handler      │    │  - Alerts on failures       │
└────────────────────────────┘    └─────────────────────────────┘
             │
             │ Subscribes to
             ▼
┌────────────────────────────┐
│   Service Catalog          │
│                            │
│  - service.added           │
│  - service.updated         │
│  - service.removed         │
└────────────────────────────┘
```

## Components

### 1. Event Definitions
**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/events/scenario_events.py`

Defines all scenario-related events:

#### Published Events
- `scenario.generated` - When scenarios are generated
- `scenario.updated` - When scenario is modified
- `scenario.executed` - When scenario execution completes
- `scenario.deprecated` - When scenario is deprecated
- `scenario.regeneration.triggered` - When auto-regeneration starts
- `scenario.regeneration.completed` - When auto-regeneration finishes
- `scenario.pattern.detected` - When pattern is detected

#### Subscribed Events
- `service.catalog.updated` - Service catalog changes
- `service.added` - New service added
- `service.updated` - Service modified
- `service.removed` - Service removed
- `service.health.changed` - Service health changes

### 2. EventBus Client
**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/integrations/eventbus_client.py`

**Class**: `ScenarioEventBusClient`

**Features**:
- Publishes scenario lifecycle events
- Subscribes to service catalog events
- Handles event routing
- Manages connections

**Usage**:
```python
from integrations.eventbus_client import ScenarioEventBusClient
from events.scenario_events import create_scenario_generated_event

# Initialize
client = ScenarioEventBusClient(backend='redis')
await client.initialize()

# Publish event
event = create_scenario_generated_event(
    scenario_ids=["s1", "s2"],
    level="l1_platform",
    generator="l1_platform",
    trigger="manual"
)
await client.publish_scenario_generated(event)

# Subscribe to events
async def handle_service_added(event):
    print(f"Service added: {event.data}")

await client.subscribe_to_catalog_updates(handle_service_added)
```

### 3. Generation Manager Integration
**Location**: `/Users/MD/AI-Platform-ISO/infrastructure/tools/scenario-generators/managers/generation_manager.py`

**Integration Points**:
- Initializes EventBus client on startup
- Publishes `scenario.generated` event after each generation level
- Includes metadata (stats, timing, errors)

**Example**:
```python
from generation_manager import GenerationManager

# Create manager with EventBus
manager = GenerationManager(enable_eventbus=True)

# Generate scenarios - automatically publishes events
await manager.generate_all(levels=["l1_platform"])
```

**Events Published**:
- After L1 Platform generation
- After L1 Applications generation
- After L2 Subsystems generation
- After L3 Systems generation
- After L4 Workflows generation

### 4. Auto-Regeneration Handler
**Location**: `/Users/MD/AI-Platform-ISO/infrastructure/tools/scenario-generators/managers/auto_regeneration_handler.py`

**Class**: `AutoRegenerationHandler`

**Purpose**: Automatically regenerates scenarios when services change

**Features**:
- Listens to service catalog events
- Batches changes (30-second window)
- Determines affected scenario levels
- Triggers regeneration
- Publishes regeneration events

**Flow**:
```
1. Service Added Event
   ↓
2. AutoRegenerationHandler receives event
   ↓
3. Adds to pending changes batch
   ↓
4. After 30 seconds, processes batch
   ↓
5. Publishes regeneration.triggered event
   ↓
6. Calls GenerationManager for affected levels
   ↓
7. Publishes regeneration.completed event
```

**Usage**:
```python
from auto_regeneration_handler import AutoRegenerationHandler

# Initialize
handler = AutoRegenerationHandler(generation_manager)
await handler.initialize()

# Handler automatically listens for service changes
# and triggers regeneration as needed
```

**Service-to-Level Mapping**:
```python
{
    # L1 Platform Services
    "gateway": "l1_platform",
    "eventbus": "l1_platform",
    "database-gateway": "l1_platform",

    # L1 Applications
    "scenario-intelligence": "l1_application",
    "simulation-service": "l1_application",

    # L2 Subsystems
    "ai-office": "l2",
    "expertise-center": "l2",
}
```

### 5. Execution Engine Integration
**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/engines/scenario_engine.py`

**Class**: `ScenarioEngine`

**Integration Points**:
- Accepts EventBus client in constructor
- Publishes `scenario.executed` event after execution
- Includes execution metrics (duration, steps, status)

**Events Published**:
- `scenario.executed` (status: success)
- `scenario.executed` (status: failed)

**Usage**:
```python
from engines.scenario_engine import ScenarioEngine

# Create engine with EventBus
engine = ScenarioEngine(eventbus_client=client)

# Execute scenario - automatically publishes event
result = await engine.execute_scenario(scenario, context)
```

### 6. MIO Manager Integration
**Location**: `/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager/integrations/scenario_intelligence_client.py`

**Class**: `ScenarioIntelligenceClient`

**Purpose**: Monitor scenario health and track metrics

**Features**:
- Subscribes to all scenario events
- Tracks metrics:
  - Scenarios generated
  - Scenarios executed
  - Scenarios failed
  - Regenerations triggered/completed
- Alerts on:
  - Failed executions
  - Slow executions (>30s)
  - Large batches (>100 scenarios)
  - Failed regenerations
- Provides health status endpoint

**Metrics Tracked**:
```python
{
    "scenarios_generated": 150,
    "scenarios_executed": 45,
    "scenarios_failed": 2,
    "regenerations_triggered": 5,
    "regenerations_completed": 5,
    "last_generation": {...},
    "last_execution": {...},
    "last_regeneration": {...}
}
```

**Usage**:
```python
# In MIO Manager main.py
scenario_intelligence_client = ScenarioIntelligenceClient(eventbus_client)
await scenario_intelligence_client.subscribe_to_events()

# Get metrics
metrics = scenario_intelligence_client.get_metrics()

# Get health status
health = await scenario_intelligence_client.get_health_status()
```

## Event Flows

### Flow 1: Scenario Generation
```
┌──────────────────┐
│ User/Scheduler   │
└────────┬─────────┘
         │
         │ generate_all()
         ▼
┌──────────────────────┐
│ Generation Manager   │
│                      │
│ 1. Generate L1       │
│ 2. Publish event     │───────┐
└──────────────────────┘       │
                               │
                               ▼
                    ┌──────────────────┐
                    │    EventBus      │
                    └────────┬─────────┘
                             │
                             │ scenario.generated
                             ▼
                    ┌──────────────────┐
                    │  MIO Manager     │
                    │                  │
                    │ • Logs event     │
                    │ • Updates metrics│
                    │ • Checks health  │
                    └──────────────────┘
```

### Flow 2: Auto-Regeneration
```
┌──────────────────┐
│ Service Catalog  │
│                  │
│ service.added    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│      EventBus            │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ AutoRegenerationHandler  │
│                          │
│ 1. Receive event         │
│ 2. Add to batch          │
│ 3. Wait 30s              │
│ 4. Process batch         │
│ 5. Publish triggered     │───────┐
│ 6. Call GenManager       │       │
│ 7. Publish completed     │───────┤
└──────────────────────────┘       │
                                   │
                                   ▼
                        ┌──────────────────┐
                        │  MIO Manager     │
                        │                  │
                        │ • Tracks regen   │
                        │ • Monitors status│
                        └──────────────────┘
```

### Flow 3: Scenario Execution
```
┌──────────────────┐
│ User/API         │
└────────┬─────────┘
         │
         │ execute_scenario()
         ▼
┌──────────────────────┐
│ Scenario Engine      │
│                      │
│ 1. Execute steps     │
│ 2. Collect metrics   │
│ 3. Publish event     │───────┐
└──────────────────────┘       │
                               │
                               ▼
                    ┌──────────────────┐
                    │    EventBus      │
                    └────────┬─────────┘
                             │
                             │ scenario.executed
                             ▼
                    ┌──────────────────┐
                    │  MIO Manager     │
                    │                  │
                    │ • Tracks exec    │
                    │ • Checks failures│
                    │ • Alerts if slow │
                    └──────────────────┘
```

## Configuration

### EventBus Backend
The EventBus supports multiple backends:
- **memory**: In-memory (testing only)
- **redis**: Production (recommended)
- **rabbitmq**: Alternative

Configuration:
```python
# In scenario-intelligence
client = ScenarioEventBusClient(
    backend='redis',
    redis_url='redis://localhost:6379'
)

# In MIO Manager (uses existing EventBus)
eventbus_client = EventBusClient(
    backend='redis',
    redis_url=settings.REDIS_URL
)
```

### Batch Window
Control how long to wait before processing batch of changes:
```python
handler = AutoRegenerationHandler(
    generation_manager,
    batch_window_seconds=30  # Default: 30 seconds
)
```

## Testing

### Unit Tests
Test individual components:
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
pytest tests/integration/test_eventbus_integration.py -v
```

### Integration Tests
Test complete flows:
```python
# Test generation with EventBus
manager = GenerationManager(enable_eventbus=True)
await manager.generate_all(levels=["l1_platform"])

# Verify events were published
# Check MIO Manager received events
```

### Manual Testing
1. Start EventBus (Redis)
2. Start MIO Manager (subscribes to events)
3. Run scenario generation (publishes events)
4. Check MIO Manager logs for received events

## Monitoring

### MIO Manager Dashboard
Access at: `http://localhost:8046/ui`

**Scenario Intelligence Section**:
- Scenarios generated today
- Scenarios executed today
- Failure rate
- Recent regenerations
- Event timeline

### Metrics Endpoint
```bash
curl http://localhost:8046/api/scenario-intelligence/metrics
```

Response:
```json
{
  "scenarios_generated": 150,
  "scenarios_executed": 45,
  "scenarios_failed": 2,
  "failure_rate_percent": 4.4,
  "regenerations_triggered": 5,
  "regenerations_completed": 5
}
```

### Health Endpoint
```bash
curl http://localhost:8046/api/scenario-intelligence/health
```

Response:
```json
{
  "status": "healthy",
  "metrics": {...},
  "failure_rate_percent": 4.4,
  "subscriptions_active": true
}
```

## Troubleshooting

### Events Not Being Published
1. Check EventBus client is initialized:
   ```python
   assert client.is_connected()
   ```
2. Check EventBus is running (Redis)
3. Check logs for errors

### Auto-Regeneration Not Triggering
1. Check AutoRegenerationHandler is running
2. Check it subscribed to catalog events
3. Verify service-to-level mapping includes your service
4. Check batch window hasn't been exceeded

### MIO Manager Not Receiving Events
1. Check MIO Manager is running
2. Check ScenarioIntelligenceClient subscribed
3. Verify EventBus connection
4. Check MIO Manager logs

## Best Practices

1. **Always enable EventBus in production**:
   ```python
   manager = GenerationManager(enable_eventbus=True)
   ```

2. **Use appropriate batch windows**:
   - Short window (10s): Fast response, more events
   - Long window (60s): Better batching, fewer events

3. **Monitor failure rates**:
   - Alert if >10% scenarios fail
   - Investigate patterns in failures

4. **Test auto-regeneration**:
   - Add test service to catalog
   - Verify scenarios are regenerated
   - Check timing and batch processing

5. **Include metadata in events**:
   ```python
   event = create_scenario_generated_event(
       ...,
       metadata={
           "stats": gen_stats,
           "user_id": user_id,
           "reason": "scheduled"
       }
   )
   ```

## Future Enhancements

1. **Dead Letter Queue**: Handle failed event processing
2. **Event Replay**: Replay events for debugging
3. **Event Versioning**: Support multiple event schema versions
4. **Event Filtering**: Filter events by level, service, etc.
5. **Event Analytics**: Analyze event patterns and trends
6. **Smart Regeneration**: Use AI to determine when to regenerate

## Files Created/Modified

### New Files
1. `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/events/scenario_events.py`
2. `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/integrations/eventbus_client.py`
3. `/Users/MD/AI-Platform-ISO/infrastructure/tools/scenario-generators/managers/auto_regeneration_handler.py`
4. `/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager/integrations/scenario_intelligence_client.py`
5. `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/tests/integration/test_eventbus_integration.py`

### Modified Files
1. `/Users/MD/AI-Platform-ISO/infrastructure/tools/scenario-generators/managers/generation_manager.py`
   - Added EventBus client parameter
   - Added event publishing after generation
   - Added initialize/close methods

2. `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/engines/scenario_engine.py`
   - Added EventBus client parameter
   - Added event publishing after execution
   - Added _publish_execution_event method

3. `/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager/main.py`
   - Added ScenarioIntelligenceClient import
   - Added client initialization
   - Added event subscriptions

## Summary

The Scenario Intelligence EventBus integration provides:
- ✅ **Event-driven architecture** for scenario management
- ✅ **Auto-regeneration** when services change
- ✅ **Real-time monitoring** through MIO Manager
- ✅ **Platform choreography** through events
- ✅ **Comprehensive testing** with integration tests
- ✅ **Production-ready** with Redis backend

All components are now connected and communicating through the EventBus, enabling a truly intelligent and self-managing scenario system.
