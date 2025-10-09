# Central Brain Testing System

**Система тестирования от имени центрального мозга**

## Overview / Обзор

This testing system implements the requirement:

> "можно создать тесты от имени центрального мозга где все источники правды зафиксированы"

(Create tests from the central brain perspective where all sources of truth are fixed)

### Key Features / Ключевые возможности

1. **Fixed Sources of Truth** - Фиксированные источники правды:
   - Service Registry (`infrastructure/runtime/service-discovery/service_registry.py`)
   - EventBus (`infrastructure/eventbus`)
   - Expected service configurations (ports, dependencies)
   - Running process list (lsof/netstat)

2. **Critical Compliance Tests** - Критические тесты на соответствие:
   - Services running but NOT registered (в системе но не участие)
   - Services registered but NOT responding
   - Services NOT connected to EventBus (не подротсетность)
   - Services with missing dependencies
   - Port conflicts

3. **Immediate Detection** - Немедленное обнаружение:
   - Real-time EventBus integration
   - Automatic heartbeat monitoring
   - Health check automation
   - Instant alerts when services disconnect

## Architecture / Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                     CENTRAL BRAIN                            │
│                    (Центральный мозг)                        │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Service    │  │   EventBus   │  │  Process     │
    │   Registry   │  │              │  │  List        │
    │ (SOURCE OF   │  │ (SOURCE OF   │  │ (SOURCE OF   │
    │   TRUTH)     │  │   TRUTH)     │  │   TRUTH)     │
    └──────────────┘  └──────────────┘  └──────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Critical Tests   │
                    │                  │
                    │ 1. Unregistered  │
                    │ 2. Non-responding│
                    │ 3. Disconnected  │
                    │ 4. Dependencies  │
                    │ 5. Port conflicts│
                    └──────────────────┘
```

## Components / Компоненты

### 1. Central Brain Test Suite
**File**: `infrastructure/tests/central_brain_tests.py`

Comprehensive test suite that validates system health from a global perspective.

**Tests**:
- ✅ `test_detect_unregistered_services` - **CRITICAL**: Detect services running but not in registry
- ✅ `test_detect_non_responding_services` - **CRITICAL**: Detect registered services that don't respond
- ✅ `test_detect_eventbus_disconnected_services` - **CRITICAL**: Detect services not connected to EventBus
- ✅ `test_detect_missing_dependencies` - **CRITICAL**: Detect missing dependencies
- ✅ `test_detect_port_conflicts` - **CRITICAL**: Detect port conflicts
- ✅ `test_system_health_summary` - Overall system health report

### 2. EventBus Integration
**File**: `infrastructure/runtime/service-discovery/eventbus_integration.py`

Integrates Service Registry with EventBus for real-time monitoring.

**Features**:
- Automatic service registration when services connect
- Heartbeat monitoring (60-second timeout by default)
- Immediate detection of disconnected services
- Health status updates via EventBus
- Configurable callbacks for alerts

**Events**:
- `platform.service.started` - Service has started
- `platform.service.stopped` - Service has stopped
- `platform.service.heartbeat` - Service heartbeat (every 30s)
- `platform.service.health` - Health status update
- `platform.service_discovery.service_connected` - Service connected (alert)
- `platform.service_discovery.service_disconnected` - Service disconnected (alert)
- `platform.service_discovery.heartbeat_timeout` - Heartbeat timeout (alert)

### 3. Automated Health Checker
**File**: `infrastructure/runtime/service-discovery/automated_health_checker.py`

Continuous health monitoring system.

**Features**:
- Automatic port checks (TCP connect)
- HTTP health endpoint checks
- Configurable check interval (default 30s)
- Configurable failure threshold (default 3 consecutive failures)
- Automatic recovery detection
- EventBus integration for alerts

## Usage / Использование

### Running Tests / Запуск тестов

```bash
# Run all critical tests
cd /Users/MD/AI-Platform-ISO
python -m pytest infrastructure/tests/central_brain_tests.py -v -s

# Run specific test
python -m pytest infrastructure/tests/central_brain_tests.py::TestCentralBrain::test_detect_unregistered_services -v -s

# Run only critical tests
python -m pytest infrastructure/tests/central_brain_tests.py -m critical -v -s
```

### Expected Services / Ожидаемые сервисы

The test suite validates these services:

**Platform Services** (Ports 8000-8099):
- `planning-service` - Port 8011 ⚠️ **CRITICAL**
- `plans-service` - Port 8023 ⚠️ **CRITICAL**
- `governance-service` - Port 8030 ⚠️ **CRITICAL**
- `risk-service` - Port 8040 ⚠️ **CRITICAL**
- `response-service` - Port 8050 ⚠️ **CRITICAL**
- `learning-service` - Port 8060 ⚠️ **CRITICAL**
- `validation-service` - Port 8070
- `documents-service` - Port 8080

**Intelligent Core Services** (Ports 9000-9099):
- `workflow-intelligence` - Port 9001 ⚠️ **CRITICAL**
- `ai-workflow-optimizer` - Port 9002 ⚠️ **CRITICAL**
- `expertise-center` - Port 9003
- `orchestration` - Port 9004
- `event-intelligence` - Port 9005
- `predictive` - Port 9006
- `balancer-service` - Port 9091 ⚠️ **CRITICAL** (Phase 2)

**Infrastructure Services** (Ports 6000-6999):
- `redis` - Port 6379 ⚠️ **CRITICAL**
- `postgres` - Port 5432 ⚠️ **CRITICAL**
- `eventbus` - Port 8001 ⚠️ **CRITICAL**

**AI Office Infrastructure** (Ports 7000-7999):
- `mio-manager` - Port 7001
- `monitoring-service` - Port 7002
- `notification-service` - Port 7003

### Service Integration / Интеграция сервиса

Services should integrate with the system by publishing events:

```python
from infrastructure.eventbus import create_eventbus
from infrastructure.runtime.service_discovery.eventbus_integration import (
    publish_service_started,
    publish_service_heartbeat,
    publish_service_health,
    publish_service_stopped
)

# On service startup
eventbus = create_eventbus('redis')
await eventbus.connect()

await publish_service_started(
    eventbus,
    service_name='my-service',
    orchestrator='docker-compose',
    port=8011,
    metadata={'version': '1.0.0'},
    dependencies=['postgres', 'redis', 'eventbus']
)

# Send heartbeat every 30 seconds
async def heartbeat_loop():
    while True:
        await publish_service_heartbeat(eventbus, 'my-service')
        await asyncio.sleep(30)

# Update health status
await publish_service_health(eventbus, 'my-service', 'healthy')

# On shutdown
await publish_service_stopped(eventbus, 'my-service', reason='shutdown')
```

### Setting up Service Discovery / Настройка Service Discovery

```python
from infrastructure.eventbus import create_eventbus
from infrastructure.runtime.service_discovery import ServiceRegistry
from infrastructure.runtime.service_discovery.eventbus_integration import (
    ServiceDiscoveryEventBusIntegration
)
from infrastructure.runtime.service_discovery.automated_health_checker import (
    AutomatedHealthChecker,
    HealthCheckConfig
)

# 1. Create components
eventbus = create_eventbus('redis')
await eventbus.connect()

service_registry = ServiceRegistry()
await service_registry.connect_redis(redis_client)

# 2. Setup EventBus integration
eventbus_integration = ServiceDiscoveryEventBusIntegration(
    service_registry=service_registry,
    eventbus=eventbus,
    heartbeat_timeout=60  # 60 seconds
)

# Optional: Set callbacks
eventbus_integration.on_service_connect = my_connect_handler
eventbus_integration.on_service_disconnect = my_disconnect_handler
eventbus_integration.on_service_unhealthy = my_unhealthy_handler

await eventbus_integration.start()

# 3. Setup automated health checker
health_config = HealthCheckConfig(
    interval_seconds=30,
    timeout_seconds=5,
    max_failures=3,
    check_port=True,
    check_endpoint=True
)

health_checker = AutomatedHealthChecker(
    service_registry=service_registry,
    eventbus=eventbus,
    config=health_config
)

await health_checker.start()

# 4. Get health summary
summary = await health_checker.get_health_summary()
print(f"System health: {summary['health_percentage']:.1f}%")
print(f"Healthy: {summary['healthy']}/{summary['total_services']}")
```

## Test Results / Результаты тестов

### Example Output / Пример вывода

```
==================== CRITICAL TEST 1: Detecting unregistered services ====================
Found 15 listening ports: [5432, 6379, 8001, 8011, 8023, 8030, ...]
Registered services: 8
Registered ports: {8011, 8023, 8030, 8040}
❌ CRITICAL: Found unregistered services!
  [CRITICAL] planning-service on port 8011
  [WARNING] validation-service on port 8070
FAILED: Found 1 critical unregistered services: ['planning-service']

==================== CRITICAL TEST 2: Detecting non-responding services ====================
❌ Found 3 non-responding services!
  [CRITICAL] planning-service on port 8011: Port not listening
  [WARNING] validation-service on port 8070: Health check failed: HTTP 503
FAILED: Found 1 critical non-responding services: ['planning-service']

==================== CRITICAL TEST 3: Detecting EventBus-disconnected services ====================
⚠️  Found 2 EventBus-disconnected services!
  [CRITICAL] planning-service - last seen 0:05:23 ago
  [WARNING] validation-service - last seen 0:03:45 ago

==================== CRITICAL TEST 4: Detecting missing dependencies ====================
✅ All service dependencies are registered

==================== CRITICAL TEST 5: Detecting port conflicts ====================
✅ No port conflicts detected

==================== SYSTEM HEALTH SUMMARY ====================
Total services: 24
Services by status: {'running': 18, 'stopped': 3, 'failed': 3}
Services by orchestrator: {'docker-compose': 20, 'kubernetes': 4}
Expected services: 24
Running services: 18/24
Critical services running: 8/9
❌ SYSTEM STATUS: DEGRADED - 1 critical services not running
```

## Critical Scenarios / Критические сценарии

### Scenario 1: Service Running but Not Registered
**В системе но не участие** (In system but not participating)

**Problem**: Service is running (port listening) but not registered in Service Registry.

**Detection**:
```python
# Test detects this automatically
test_detect_unregistered_services()
```

**Alert**: EventBus event `platform.service_discovery.unregistered_service_detected`

**Fix**:
```python
# Service should call on startup:
await publish_service_started(eventbus, 'my-service', ...)
```

### Scenario 2: Service Registered but Not Responding
**Зарегистрирован но не отвечает** (Registered but not responding)

**Problem**: Service is in registry but port is not listening or health check fails.

**Detection**:
```python
# Test detects this automatically
test_detect_non_responding_services()

# Automated health checker also detects this
health_checker = AutomatedHealthChecker(...)
await health_checker.start()
```

**Alert**: EventBus event `platform.service_discovery.service_unhealthy`

**Fix**: Restart service or investigate crash

### Scenario 3: Service Not Connected to EventBus
**Не подключен** (Not connected)

**Problem**: Service should be connected to EventBus but hasn't sent heartbeat.

**Detection**:
```python
# Test detects this
test_detect_eventbus_disconnected_services()

# EventBus integration monitors heartbeats
eventbus_integration = ServiceDiscoveryEventBusIntegration(heartbeat_timeout=60)
await eventbus_integration.start()
```

**Alert**: EventBus event `platform.service_discovery.heartbeat_timeout`

**Fix**:
```python
# Service should send heartbeat every 30s:
async def heartbeat_loop():
    while True:
        await publish_service_heartbeat(eventbus, 'my-service')
        await asyncio.sleep(30)
```

### Scenario 4: Missing Dependencies
**Отсутствуют зависимости** (Missing dependencies)

**Problem**: Service depends on another service that is not registered.

**Detection**:
```python
test_detect_missing_dependencies()
```

**Fix**: Ensure all dependencies are started and registered before dependent service

## Metrics & Monitoring / Метрики и мониторинг

### Available Metrics / Доступные метрики

```python
# Get health summary
summary = await health_checker.get_health_summary()
# Returns:
{
    'total_services': 24,
    'healthy': 18,
    'degraded': 3,
    'unhealthy': 3,
    'unknown': 0,
    'health_percentage': 75.0,
    'services': [...]
}

# Get registry stats
stats = await service_registry.get_registry_stats()
# Returns:
{
    'total_services': 24,
    'by_status': {'running': 18, 'stopped': 3, 'failed': 3},
    'by_orchestrator': {'docker-compose': 20, 'kubernetes': 4},
    'services': ['planning-service', 'plans-service', ...]
}

# Check specific service
result = await health_checker.check_service_now('planning-service')
# Returns:
{
    'service_name': 'planning-service',
    'exists': True,
    'healthy': True,
    'health_status': 'healthy',
    'checks': {
        'port': {'listening': True, 'port': 8011},
        'endpoint': {'healthy': True, 'url': 'http://localhost:8011/health'}
    },
    'consecutive_failures': 0,
    'timestamp': '2025-10-09T12:00:00'
}
```

### Prometheus Metrics / Метрики Prometheus

Health checker can export Prometheus metrics (if prometheus_client installed):

```python
# service_registry_total - Total services in registry
# service_registry_by_status - Services by status
# service_health_status - Service health (0=unknown, 1=healthy, 2=degraded, 3=unhealthy)
# service_health_check_failures_total - Total health check failures
```

## Configuration / Конфигурация

### Environment Variables / Переменные окружения

```bash
# Service Discovery
SERVICE_REGISTRY_HEARTBEAT_TIMEOUT=60  # Heartbeat timeout in seconds
SERVICE_REGISTRY_HEALTH_CHECK_INTERVAL=30  # Health check interval
SERVICE_REGISTRY_MAX_FAILURES=3  # Max consecutive failures

# EventBus
EVENTBUS_URL=redis://localhost:6379

# Redis (for Service Registry persistence)
REDIS_URL=redis://localhost:6379
```

### Configuration File / Файл конфигурации

`config/service_discovery.yaml`:
```yaml
service_discovery:
  heartbeat_timeout: 60
  health_check:
    interval_seconds: 30
    timeout_seconds: 5
    max_failures: 3
    check_port: true
    check_endpoint: true

  alerts:
    on_service_disconnect: true
    on_service_unhealthy: true
    on_heartbeat_timeout: true
```

## Troubleshooting / Устранение неполадок

### Issue: Test fails with "No listening ports detected"

**Cause**: lsof and netstat not available

**Fix**: Install lsof or netstat, or run tests in Docker

### Issue: All services marked as unregistered

**Cause**: Service Registry not initialized

**Fix**:
```python
# Initialize registry and register expected services
service_registry = ServiceRegistry()
for service_name, config in EXPECTED_SERVICES.items():
    await service_registry.register(service_name, 'docker-compose', ...)
```

### Issue: EventBus integration not detecting disconnects

**Cause**: Services not sending heartbeats

**Fix**: Ensure all services call `publish_service_heartbeat` every 30s

### Issue: Health checks always fail

**Cause**: Health endpoint not implemented or wrong URL

**Fix**: Implement `/health` endpoint in all services:
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Next Steps / Следующие шаги

1. ✅ Central Brain Test Suite created
2. ✅ EventBus Integration implemented
3. ✅ Automated Health Checker implemented
4. ⏳ TODO: Integrate into CI/CD pipeline
5. ⏳ TODO: Add Prometheus metrics
6. ⏳ TODO: Create alerting dashboard
7. ⏳ TODO: Add test coverage for all services

## References / Ссылки

- [Service Registry](../../infrastructure/runtime/service-discovery/service_registry.py)
- [EventBus Integration](../../infrastructure/runtime/service-discovery/eventbus_integration.py)
- [Automated Health Checker](../../infrastructure/runtime/service-discovery/automated_health_checker.py)
- [Central Brain Tests](./central_brain_tests.py)
- [EventBus Core](../../infrastructure/eventbus/)
- [Phase 2 Documentation](../../docs/PHASE2_MVP_COMPLETE.md)

---

**Created**: 2025-10-09
**Author**: Central Brain (Центральный мозг)
**Status**: ✅ Complete and operational
