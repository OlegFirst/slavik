# EventBus Integration - Quick Reference

## Quick Start

### 1. Initialize EventBus in Generation Manager
```python
from generation_manager import GenerationManager

# Enable EventBus (default: True)
manager = GenerationManager(enable_eventbus=True)

# Generate scenarios - automatically publishes events
await manager.generate_all(levels=["l1_platform"])
```

### 2. Initialize EventBus in Scenario Engine
```python
from engines.scenario_engine import ScenarioEngine
from integrations.eventbus_client import get_eventbus_client

# Get global EventBus client
client = get_eventbus_client()
await client.initialize()

# Create engine with EventBus
engine = ScenarioEngine(eventbus_client=client)

# Execute scenario - automatically publishes events
result = await engine.execute_scenario(scenario, context)
```

### 3. Setup Auto-Regeneration
```python
from auto_regeneration_handler import AutoRegenerationHandler

# Create handler
handler = AutoRegenerationHandler(
    generation_manager=manager,
    batch_window_seconds=30  # Wait 30s before processing batch
)

# Initialize and subscribe to catalog events
await handler.initialize()

# Handler now automatically regenerates scenarios when services change
```

### 4. Monitor in MIO Manager
```python
# In MIO Manager - automatically initialized at startup
scenario_intelligence_client = ScenarioIntelligenceClient(eventbus_client)
await scenario_intelligence_client.subscribe_to_events()

# Get metrics
metrics = scenario_intelligence_client.get_metrics()

# Get health status
health = await scenario_intelligence_client.get_health_status()
```

## Event Types Reference

### Published Events

| Event Type | Published By | Data |
|------------|-------------|------|
| `scenario.generated` | GenerationManager | scenario_ids, level, generator, count, trigger |
| `scenario.updated` | Manual/System | scenario_id, old_version, new_version, changes |
| `scenario.executed` | ScenarioEngine | scenario_id, execution_id, status, duration_ms, steps |
| `scenario.deprecated` | AutoRegenerationHandler | scenario_id, reason, replaced_by |
| `scenario.regeneration.triggered` | AutoRegenerationHandler | regeneration_id, affected_services, affected_levels |
| `scenario.regeneration.completed` | AutoRegenerationHandler | regeneration_id, scenarios_generated, status, duration_ms |
| `scenario.pattern.detected` | PatternDetector | pattern_type, scenario_ids, confidence |

### Subscribed Events

| Event Type | Subscribed By | Purpose |
|------------|---------------|---------|
| `service.catalog.updated` | AutoRegenerationHandler | Trigger regeneration |
| `service.added` | AutoRegenerationHandler | Generate scenarios for new service |
| `service.removed` | AutoRegenerationHandler | Deprecate scenarios for removed service |
| `service.updated` | AutoRegenerationHandler | Update affected scenarios |
| `service.health.changed` | AutoRegenerationHandler | React to service health changes |

## Code Snippets

### Publish Scenario Generated Event
```python
from events.scenario_events import create_scenario_generated_event, ScenarioLevel

event = create_scenario_generated_event(
    scenario_ids=["s1", "s2", "s3"],
    level=ScenarioLevel.L1_PLATFORM,
    generator="l1_platform",
    trigger="manual",
    metadata={"user_id": "user123"}
)

await eventbus_client.publish_scenario_generated(event)
```

### Publish Scenario Executed Event
```python
from events.scenario_events import create_scenario_executed_event

event = create_scenario_executed_event(
    scenario_id="test-scenario-1",
    execution_id="exec-123",
    status="success",
    duration_ms=1500.0,
    steps_executed=5,
    steps_failed=0
)

await eventbus_client.publish_scenario_executed(event)
```

### Subscribe to Catalog Updates
```python
async def handle_service_added(event):
    service_name = event.data.get('service_name')
    print(f"Service added: {service_name}")
    # Trigger regeneration...

await eventbus_client.subscribe_to_catalog_updates(handle_service_added)
```

### Handle Regeneration
```python
# In AutoRegenerationHandler
async def handle_service_added(self, service_name: str, service_data: dict):
    level = self.get_level_for_service(service_name)
    regeneration_id = f"add-{uuid.uuid4()}"
    result = await self._regenerate_for_levels([level], regeneration_id)
    return result
```

## API Endpoints

### MIO Manager Endpoints
```bash
# Get scenario metrics
GET http://localhost:8046/api/scenario-intelligence/metrics

# Get health status
GET http://localhost:8046/api/scenario-intelligence/health

# Get recent events (if implemented)
GET http://localhost:8046/api/scenario-intelligence/events?limit=20
```

## Configuration

### EventBus Backend
```python
# Memory (testing only)
client = ScenarioEventBusClient(backend='memory')

# Redis (production)
client = ScenarioEventBusClient(
    backend='redis',
    redis_url='redis://localhost:6379'
)

# RabbitMQ (alternative)
client = ScenarioEventBusClient(
    backend='rabbitmq',
    rabbitmq_url='amqp://guest:guest@localhost/'
)
```

### Batch Processing
```python
handler = AutoRegenerationHandler(
    generation_manager,
    batch_window_seconds=30  # Wait 30s before processing
)
```

### Service-to-Level Mapping
```python
# In AutoRegenerationHandler
service_level_map = {
    "gateway": "l1_platform",
    "eventbus": "l1_platform",
    "scenario-intelligence": "l1_application",
    "ai-office": "l2",
}
```

## Monitoring Commands

### Check EventBus Status
```bash
# Redis
redis-cli ping

# Check EventBus logs
docker logs eventbus-service
```

### Check MIO Manager Status
```bash
# Health check
curl http://localhost:8046/health

# Scenario metrics
curl http://localhost:8046/api/scenario-intelligence/metrics

# Full status
curl http://localhost:8046/api/status
```

### Check Scenario Intelligence Status
```bash
# Check if scenarios are being generated
ls -lh /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/generated/

# Check logs
tail -f /var/log/scenario-intelligence.log
```

## Common Patterns

### Pattern 1: Generate and Monitor
```python
# Generate scenarios
manager = GenerationManager(enable_eventbus=True)
report = await manager.generate_all(levels=["l1_platform"])

# Events are automatically published
# MIO Manager automatically receives and tracks them
```

### Pattern 2: Execute and Track
```python
# Execute scenario
engine = ScenarioEngine(eventbus_client=client)
result = await engine.execute_scenario(scenario, context)

# Event is automatically published
# MIO Manager tracks execution metrics
```

### Pattern 3: Auto-Regeneration on Service Change
```python
# Setup handler (once at startup)
handler = AutoRegenerationHandler(manager)
await handler.initialize()

# When service.added event is published:
# 1. Handler receives event
# 2. Adds to batch queue
# 3. After 30s, processes batch
# 4. Triggers regeneration
# 5. Publishes events
# 6. MIO Manager monitors progress
```

## Troubleshooting

### Problem: Events not being published
**Solution**:
```python
# Check EventBus is initialized
assert client.is_connected()

# Check EventBus is enabled
manager = GenerationManager(enable_eventbus=True)  # Not False!

# Check logs
logger.info("Publishing event...")
```

### Problem: Auto-regeneration not triggering
**Solution**:
```python
# Check handler is running
assert handler._running

# Check subscriptions
print(handler.eventbus_client.get_subscriptions())

# Verify service mapping
level = handler.get_level_for_service("my-service")
print(f"Service maps to level: {level}")
```

### Problem: MIO Manager not receiving events
**Solution**:
```bash
# Check MIO Manager is running
curl http://localhost:8046/health

# Check subscriptions are active
curl http://localhost:8046/api/scenario-intelligence/health
# Should show: "subscriptions_active": true

# Check EventBus connection
# In MIO Manager logs, look for:
# "✅ Subscribed to Scenario Intelligence events"
```

## Performance Tips

1. **Batch service changes**: Use 30-60 second batch window
2. **Enable EventBus only in production**: Use `enable_eventbus=False` for testing
3. **Monitor metrics**: Track failure rates and slow executions
4. **Use Redis for EventBus**: Memory backend is for testing only
5. **Set appropriate timeouts**: Don't block on slow event handlers

## Links

- [Full Documentation](./EVENTBUS_INTEGRATION.md)
- [Event Definitions](../events/scenario_events.py)
- [EventBus Client](../integrations/eventbus_client.py)
- [Auto-Regeneration Handler](../../infrastructure/tools/scenario-generators/managers/auto_regeneration_handler.py)
- [MIO Manager Client](../../infrastructure/AI-office-infrastructure/mio-manager/integrations/scenario_intelligence_client.py)
- [Integration Tests](../tests/integration/test_eventbus_integration.py)
