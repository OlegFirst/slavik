# Service Discovery & Health Monitoring

## Overview
Complete service discovery, registry, health monitoring, and ISO 22301 mapping system for the BCM Platform.

## Extracted From
- **Service Registry**: `/intelligent-core/orchestrator_обьединенный/core/service_registry.py`
- **Health Monitor**: `/intelligent-core/orchestrator_обьединенный/core/health_monitor.py`
- **ISO Mapping**: `/intelligent-core/platform-orchestrator/platform_orchestrator.py` (SERVICES dict)
- **Date**: 2025-10-04
- **Total Lines**: ~1000

## What This Module Does
1. **Service Registry** - Track all services, dependencies, status
2. **Health Monitoring** - Docker, HTTP, and custom health checks
3. **ISO 22301 Mapping** - Map services to ISO clauses
4. **Dependency Management** - Ensure services start in correct order

## Status
**Production-Ready**

## Components

### 1. Service Registry (`service_registry.py`)
Maintains in-memory (with Redis persistence) registry of all platform services.

**Features**:
- Register/unregister services
- Track service status and health
- Dependency tracking
- Query by orchestrator, status, dependencies

**Usage**:
```python
from infrastructure.service_discovery import ServiceRegistry

registry = ServiceRegistry()
await registry.connect_redis(redis_client)

# Register service
service = await registry.register(
    service_name="api_service",
    orchestrator="PlatformOrchestrator",
    metadata={"port": 8000},
    dependencies=["postgres", "redis"]
)

# Check if dependencies ready
ready = await registry.is_dependencies_ready("api_service")

# Update status
await registry.update_status("api_service", "running")
await registry.update_health("api_service", "healthy")
```

### 2. Health Monitor (`health_monitor.py`)
Multi-mode health checking system with continuous monitoring.

**Check Types**:
- **Docker**: Container status and health
- **HTTP**: HTTP endpoint checks (GET/POST)
- **Custom**: Custom check functions

**Usage**:
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

**Health Statuses**:
- `HEALTHY` - Service operational
- `UNHEALTHY` - Service down
- `DEGRADED` - Service running but issues
- `UNKNOWN` - Unable to determine

### 3. ISO Service Map (`iso_service_map.py`)
Complete mapping of all 12 BCM Platform services to ISO 22301 clauses.

**Registry Structure**:
```python
{
    "service_key": {
        "name": "Human Readable Name",
        "url": "http://localhost:PORT",
        "module": "module_name",
        "iso_clause": "8.3",
        "component": "bcm-strategy",
        "has_workflow_intelligence": True,
        "description": "What it does"
    }
}
```

**Usage**:
```python
from infrastructure.service_discovery import ISO_SERVICE_REGISTRY
from infrastructure.service_discovery.iso_service_map import (
    get_services_by_component,
    get_services_with_workflow_intelligence,
    get_services_by_iso_clause
)

# Get all services
all_services = ISO_SERVICE_REGISTRY

# Get services by component
bcm_services = get_services_by_component("bcm-strategy")

# Get workflow intelligence services
wi_services = get_services_with_workflow_intelligence()  # Returns 10 services

# Get services implementing ISO 8.2.2
bia_services = get_services_by_iso_clause("8.2.2")
```

**Service Breakdown**:
- **Total Services**: 12
- **Core BCM**: 10 (with Workflow Intelligence)
- **Community**: 2 (portal, marketplace)
- **Storage**: 1 (file service)

**ISO Clause Coverage**:
- 5.3 (Governance)
- 7.1 (Resources)
- 7.2 (Competence)
- 7.3 (Communication)
- 7.4 (Knowledge)
- 7.5 (Documentation)
- 8.2.2 (BIA)
- 8.2.3 (Risk)
- 8.3 (Strategy)
- 8.4 (Plans)
- 8.4.5 (Response)
- 8.4.6 (Testing)
- 9.2 (Audit)
- 10.1, 10.2 (Improvement)

## Dependencies
- `redis.asyncio` - Service registry persistence
- `httpx` - HTTP health checks
- `docker-py` (optional) - Docker health checks

## Integration Points
- **AI DevOps Engine**: Uses for deployment orchestration
- **Docker Manager**: Container lifecycle
- **Platform Orchestrator**: Service coordination
- **Monitoring Service**: Exports health metrics

## Production Features
1. **Redis Persistence**: Services survive restarts
2. **Continuous Monitoring**: Background health checks
3. **Retry Logic**: 3 retries on HTTP checks
4. **Dependency Awareness**: Smart startup ordering
5. **Multi-mode Checks**: Docker, HTTP, Custom

## Next Steps
1. Add Consul integration for true service discovery
2. Implement circuit breaker pattern
3. Add service mesh support (Istio/Linkerd)
4. Integrate with Prometheus for metrics
5. Add gRPC health check support
