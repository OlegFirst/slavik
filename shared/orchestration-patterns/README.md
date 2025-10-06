# Orchestration Patterns - Shared Base Classes

## Overview
Reusable orchestration pattern (Abstract Base Class) providing common functionality for all platform orchestrators.

## Extracted From
- **Source**: `/intelligent-core/orchestrator_обьединенный/core/base_orchestrator.py`
- **Date**: 2025-10-04
- **Original Size**: 213 lines

## What This Module Does
Provides abstract base class `BaseOrchestrator` that all orchestrators extend:
- Platform Orchestrator
- AI Orchestrator
- Scenario Orchestrator
- Workflow Orchestrator

## Status
**Production-Ready** - Refactored for dependency injection

## Key Features

### 1. Dependency Injection
All dependencies are injected (not hardcoded):
```python
from shared.orchestration_patterns import BaseOrchestrator

class MyOrchestrator(BaseOrchestrator):
    def __init__(self, service_registry, event_coordinator,
                 health_monitor, docker_manager):
        super().__init__(
            service_registry=service_registry,
            event_coordinator=event_coordinator,
            health_monitor=health_monitor,
            docker_manager=docker_manager
        )
```

### 2. Common Methods Provided

**Service Registry Integration**:
- `register_service(service_name, metadata)` - Register service
- Dependencies resolved via injected `service_registry`

**Event Bus Integration**:
- `publish_event(event_type, data, tenant_id)` - Publish events
- `subscribe_to_events(pattern, handler)` - Subscribe to events
- Dependencies resolved via injected `event_coordinator`

**Health Monitoring**:
- `monitor_service_health(service_name)` - Check service health
- Dependencies resolved via injected `health_monitor`

**Docker Lifecycle**:
- `start_docker_service(service_name, timeout)` - Start with health wait
- `stop_docker_service(service_name)` - Stop service
- `restart_docker_service(service_name)` - Restart with health check
- Dependencies resolved via injected `docker_manager`

### 3. Abstract Methods (Must Implement)
```python
@abstractmethod
async def start() -> None:
    """Start the orchestrator"""
    pass

@abstractmethod
async def stop() -> None:
    """Stop the orchestrator"""
    pass

@abstractmethod
async def get_status() -> Dict[str, Any]:
    """Get orchestrator status"""
    pass
```

## Usage Example

### Minimal Implementation
```python
from shared.orchestration_patterns import BaseOrchestrator

class MyOrchestrator(BaseOrchestrator):
    async def start(self):
        self.running = True
        logger.info(f"{self.name} started")

        # Register this orchestrator's services
        await self.register_service("my_service")

        # Subscribe to events
        await self.subscribe_to_events("platform.*", self._handle_event)

    async def stop(self):
        self.running = False
        logger.info(f"{self.name} stopped")

    async def get_status(self):
        return {
            "name": self.name,
            "running": self.running,
            "services": []
        }

    async def _handle_event(self, event):
        logger.info(f"Received event: {event['type']}")
```

### Full Implementation with Services
```python
from shared.orchestration_patterns import BaseOrchestrator

class PlatformOrchestrator(BaseOrchestrator):
    async def start(self):
        self.running = True

        # Start infrastructure services
        await self.start_docker_service("postgres", timeout=60)
        await self.start_docker_service("redis", timeout=60)

        # Register services
        await self.register_service("postgres", {"type": "database"})
        await self.register_service("redis", {"type": "cache"})

        # Publish platform ready event
        await self.publish_event("platform.ready", {
            "services": ["postgres", "redis"]
        })

    async def stop(self):
        # Stop services in reverse order
        await self.stop_docker_service("redis")
        await self.stop_docker_service("postgres")

        self.running = False

    async def get_status(self):
        postgres_healthy = await self.monitor_service_health("postgres")
        redis_healthy = await self.monitor_service_health("redis")

        return {
            "name": self.name,
            "running": self.running,
            "services": {
                "postgres": "healthy" if postgres_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy"
            }
        }
```

## Composition over Inheritance

This design uses **dependency injection** instead of creating dependencies internally:

**Old (hardcoded)**:
```python
def __init__(self):
    self.service_registry = ServiceRegistry()  # ❌ Hardcoded
    self.docker_manager = DockerManager()      # ❌ Hardcoded
```

**New (injected)**:
```python
def __init__(self, service_registry, docker_manager):
    self.service_registry = service_registry  # ✅ Injected
    self.docker_manager = docker_manager      # ✅ Injected
```

**Benefits**:
- Easy to test (inject mocks)
- Flexible configuration
- No circular dependencies
- Can swap implementations

## Integration Points
- **Service Registry**: Register/discover services
- **Event Coordinator**: Pub/sub messaging
- **Health Monitor**: Service health checks
- **Docker Manager**: Container lifecycle

## Real-World Orchestrators

### 1. Platform Orchestrator
Manages infrastructure services (postgres, redis, rabbitmq)

### 2. AI Orchestrator
Manages AI services (claude, local models, vector DB)

### 3. Scenario Orchestrator
Manages BCM scenarios (exercises, drills, tests)

### 4. Workflow Orchestrator
Manages BPMN workflows (process execution)

## Next Steps
1. Add metrics collection hooks
2. Add lifecycle event hooks (pre-start, post-start, etc.)
3. Add circuit breaker pattern support
4. Add automatic restart on failure
