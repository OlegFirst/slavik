# Service Discovery v2.0 - Unified Catalog + Registry + Event Broadcasting

## Overview
Complete service discovery, registry, health monitoring, ISO 22301 mapping, **and Service Catalog integration** for the AI Platform.

**Version**: 2.0 (with Service Catalog Integration)
**Date**: October 11, 2025
**Status**: ✅ Production Ready with Event Broadcasting

## Extracted From
- **Service Registry**: `/intelligent-core/orchestrator_обьединенный/core/service_registry.py`
- **Health Monitor**: `/intelligent-core/orchestrator_обьединенный/core/health_monitor.py`
- **ISO Mapping**: `/intelligent-core/platform-orchestrator/platform_orchestrator.py` (SERVICES dict)
- **Date**: 2025-10-04
- **Total Lines**: ~1000

## What This Module Does
1. **Service Catalog Integration** - Static service templates from `service-catalog.yaml`
2. **Service Registry** - Track all services, dependencies, runtime status
3. **Unified View** - Combine catalog (static) + registry (dynamic) data
4. **Health Monitoring** - Docker, HTTP, and custom health checks
5. **ISO 22301 Mapping** - Map services to ISO clauses
6. **Dependency Management** - Ensure services start in correct order
7. **Event Broadcasting** - Publish service lifecycle events to EventBus

## Key Features (v2.0)

### 🆕 Service Catalog Integration (`catalog_integration.py`)
- Loads service templates from `service-catalog.yaml`
- Combines static catalog with dynamic runtime data
- Detects **missing services** (in catalog but not running)
- Detects **unknown services** (running but not in catalog)
- Provides unified API: `/v2/catalog/*`

### 🆕 Event Broadcasting (`eventbus_integration.py`)
- Publishes to EventBus on service lifecycle events
- **Events**: `service_registered`, `service_disconnected`, `critical_timeout`
- MIO Manager (EYES) subscribes for observation
- Enables event-driven choreography

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

## v2.0 Unified Catalog API

### Catalog Endpoints

```python
# Get all services (catalog + runtime unified view)
GET /v2/catalog/services
Response: {
    "services": [
        {
            "name": "mio-manager",
            "type": "infrastructure/AI-office-infrastructure",
            "business_process": "Monitoring & Observability Management",
            "kpis": ["coverage_percentage", "alert_response_time"],
            "expected_port": 8046,
            "actual_port": 8046,
            "runtime_status": "running",
            "registration_status": "registered",
            "health_status": "healthy",
            ...
        }
    ]
}

# Get missing services (in catalog but not running)
GET /v2/catalog/missing
Response: {
    "missing_services": [...],
    "count": 5
}

# Get unknown services (running but not in catalog)
GET /v2/catalog/unknown
Response: {
    "unknown_services": [...],
    "count": 2
}

# Get catalog statistics
GET /v2/catalog/stats
Response: {
    "totals": {
        "total_services": 50,
        "registered_services": 43,
        "missing_services": 5,
        "unknown_services": 2,
        "healthy_services": 41,
        "coverage_percent": 86.0
    },
    "by_type": {...},
    "by_business_process": {...}
}
```

### Event Broadcasting

Service Discovery v2.0 publishes events to EventBus:

```python
# When service registers
Event: platform.monitoring.service_registered
Payload: {
    "service_name": "mio-manager",
    "port": 8046,
    "orchestrator": "unified_orchestrator",
    "kpis": ["coverage_percentage"],
    "timestamp": "2025-10-11T01:00:00Z"
}

# When service disconnects
Event: platform.monitoring.service_disconnected
Payload: {
    "service_name": "api-gateway",
    "reason": "shutdown",
    "timestamp": "2025-10-11T01:05:00Z"
}

# When heartbeat timeout (>60s)
Event: platform.monitoring.critical_timeout
Payload: {
    "service_name": "db-intelligence",
    "last_heartbeat": "2025-10-11T00:58:00Z",
    "timeout_seconds": 60,
    "timestamp": "2025-10-11T01:00:00Z"
}
```

### Integration with MIO Manager (EYES)

MIO Manager subscribes to Service Discovery events and:
1. **Observes** new service registrations
2. **Checks** if service is monitored by Prometheus
3. **Verifies** metrics endpoint accessibility
4. **Publishes** observations to EventBus (not commands!)

Example observation flow:
```
1. Service Discovery: service_registered → EventBus
2. MIO Manager: Receives event → Checks Prometheus → Checks metrics endpoint
3. MIO Manager: Publishes observation → EventBus
   - platform.mio.service_not_monitored_observed (if missing)
   - platform.mio.metrics_endpoint_unreachable_observed (if down)
4. Brain/DevOps Agent: Receives observation → Makes decision → Takes action
```

## Service Catalog Location

The `service-catalog.yaml` file is located at:
```
/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-catalog/service-catalog.yaml
```

**Note**: `/infrastructure/runtime/service-catalog/` is now a symlink to the archived catalog for backward compatibility.

## Migration from v1 to v2

**v1 (old)**: Service Discovery only tracked runtime services
**v2 (new)**: Service Discovery integrates catalog + runtime + event broadcasting

**Breaking Changes**: None! v1 endpoints still work.
**New Endpoints**: `/v2/catalog/*` for unified catalog view

## Next Steps
1. ✅ Service Catalog Integration (DONE)
2. ✅ Event Broadcasting to EventBus (DONE)
3. ✅ MIO Manager Integration (DONE)
4. Integrate with Prometheus for metrics export
5. Add gRPC health check support
6. Implement circuit breaker pattern
7. Add service mesh support (Istio/Linkerd)
