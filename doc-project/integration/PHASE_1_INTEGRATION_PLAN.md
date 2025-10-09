# Phase 1: Infrastructure Integration (Week 1)

**Date:** 2025-10-09
**Priority:** 🔥 CRITICAL - Foundation
**Duration:** 5-7 days
**Goal:** Интегрировать Infrastructure уровень через EventBus

---

## 🎯 ЦЕЛЬ PHASE 1

**Запустить Infrastructure Coordination:**
1. Health Monitoring Cycle (30 sec)
2. Auto-Recovery на failures
3. Resource Optimization (5 min)

**Критерий успеха:**
- ✅ Все инфраструктурные сервисы мониторятся
- ✅ Auto-recovery срабатывает при сбоях
- ✅ Metrics экспортируются в Prometheus

---

## 📋 TASKS (Приоритизированные)

### Task 1.1: EventBus Integration в Health Monitor ⭐⭐⭐

**Цель:** Health Monitor публикует события в EventBus

**Файл:** `/intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`

**Changes:**
```python
# ADD: Import EventBus
from infrastructure.eventbus import create_eventbus, Event

class HealthMonitor:
    def __init__(self):
        # ... existing code ...
        self.eventbus = None  # ADD
        logger.info("HealthMonitor initialized")

    async def connect_eventbus(self, eventbus) -> None:
        """Connect to EventBus for event publishing"""
        self.eventbus = eventbus
        logger.info("HealthMonitor connected to EventBus")

    async def monitor_continuously(self) -> None:
        """Modified: Publish events on status changes"""
        self.monitoring = True
        logger.info("Starting continuous health monitoring")

        next_checks: Dict[str, datetime] = {}
        previous_status: Dict[str, HealthStatus] = {}  # ADD: Track status changes

        while self.monitoring:
            current_time = datetime.utcnow()

            for service_name, check in self.checks.items():
                if service_name not in next_checks or current_time >= next_checks[service_name]:
                    # Run check
                    result = await self.check_service(service_name)

                    # ADD: Publish event on status change
                    prev_status = previous_status.get(service_name)
                    if prev_status != result.status:
                        await self._publish_health_event(service_name, result, prev_status)
                        previous_status[service_name] = result.status

                    # Log if unhealthy
                    if result.status == HealthStatus.UNHEALTHY:
                        logger.warning(f"Service {service_name} unhealthy: {result.message}")
                    elif result.status == HealthStatus.DEGRADED:
                        logger.info(f"Service {service_name} degraded: {result.message}")

                    next_checks[service_name] = current_time + timedelta(seconds=check.interval)

            await asyncio.sleep(5)

        logger.info("Stopped continuous health monitoring")

    async def _publish_health_event(
        self,
        service_name: str,
        result: HealthCheckResult,
        previous_status: Optional[HealthStatus]
    ) -> None:
        """Publish health status change event"""
        if not self.eventbus:
            return

        event = Event.create(
            event_type=f'infrastructure.health.{result.status.value}',
            data={
                'service_name': service_name,
                'status': result.status.value,
                'previous_status': previous_status.value if previous_status else None,
                'response_time_ms': result.response_time_ms,
                'message': result.message,
                'details': result.details,
                'checked_at': result.checked_at.isoformat()
            },
            source='health_monitor',
            tenant_id='system'  # System-level event
        )

        await self.eventbus.publish(event)
        logger.info(f"Published health event: {service_name} → {result.status.value}")
```

**Test:**
```python
# Test health monitor with EventBus
bus = create_eventbus('memory')
monitor = HealthMonitor()
await monitor.connect_eventbus(bus)

# Subscribe to health events
received_events = []
async def handler(event):
    received_events.append(event)

await bus.subscribe('infrastructure.health.*', handler)

# Register check and run
await monitor.register_check(HealthCheck(
    service_name='test_service',
    check_type='http',
    interval=5,
    config={'url': 'http://localhost:8000/health'}
))

# Monitor will publish events on status changes
asyncio.create_task(monitor.monitor_continuously())
```

**Completion Criteria:**
- ✅ Health Monitor imports EventBus
- ✅ Publishes events on status changes
- ✅ Events have proper structure (service_name, status, details)
- ✅ Test passes

---

### Task 1.2: Auto-Recovery Service ⭐⭐⭐

**Цель:** Создать Auto-Recovery который слушает health events и восстанавливает сервисы

**Файл:** `/infrastructure/eventbus/coordination/auto_recovery.py` (CREATE)

**Code:**
```python
"""
Auto-Recovery Service
Listens to health events and recovers failed services
"""

import logging
import asyncio
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timedelta

from infrastructure.eventbus import IEventBus, Event
from intelligent_core.orchestration.ai_orchestration.core.health_monitor import HealthStatus

logger = logging.getLogger(__name__)


class RecoveryStrategy:
    """Recovery strategy for a service"""
    def __init__(
        self,
        service_name: str,
        strategy_type: str,  # restart, failover, circuit_breaker
        max_attempts: int = 3,
        backoff_seconds: int = 5,
        recovery_function: Optional[Callable] = None
    ):
        self.service_name = service_name
        self.strategy_type = strategy_type
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.recovery_function = recovery_function


class AutoRecovery:
    """
    Auto-Recovery Service

    Subscribes to: infrastructure.health.unhealthy, infrastructure.health.degraded
    Publishes: infrastructure.recovery.started, infrastructure.recovery.completed, infrastructure.recovery.failed
    """

    def __init__(self, eventbus: IEventBus):
        self.eventbus = eventbus
        self.strategies: Dict[str, RecoveryStrategy] = {}
        self.recovery_in_progress: Dict[str, bool] = {}
        self.recovery_history: Dict[str, list] = {}
        logger.info("AutoRecovery initialized")

    async def start(self):
        """Start auto-recovery service"""
        # Subscribe to health events
        await self.eventbus.subscribe('infrastructure.health.unhealthy', self._handle_unhealthy)
        await self.eventbus.subscribe('infrastructure.health.degraded', self._handle_degraded)
        logger.info("AutoRecovery started - listening for health events")

    async def register_strategy(self, strategy: RecoveryStrategy):
        """Register recovery strategy for a service"""
        self.strategies[strategy.service_name] = strategy
        self.recovery_history[strategy.service_name] = []
        logger.info(f"Registered {strategy.strategy_type} recovery for {strategy.service_name}")

    async def _handle_unhealthy(self, event: Event):
        """Handle unhealthy service event"""
        service_name = event.data['service_name']
        logger.warning(f"Service {service_name} is unhealthy - triggering recovery")

        await self._trigger_recovery(service_name, event)

    async def _handle_degraded(self, event: Event):
        """Handle degraded service event"""
        service_name = event.data['service_name']
        logger.info(f"Service {service_name} is degraded - monitoring closely")

        # For degraded, wait and see if it becomes unhealthy
        # Only recover if degraded for > 60 seconds
        await asyncio.sleep(60)

        # Check if still degraded or became unhealthy
        # (In real implementation, would query current status from health monitor)

    async def _trigger_recovery(self, service_name: str, trigger_event: Event):
        """Trigger recovery for a service"""
        # Check if recovery already in progress
        if self.recovery_in_progress.get(service_name, False):
            logger.warning(f"Recovery already in progress for {service_name} - skipping")
            return

        # Get recovery strategy
        strategy = self.strategies.get(service_name)
        if not strategy:
            logger.error(f"No recovery strategy registered for {service_name}")
            return

        self.recovery_in_progress[service_name] = True

        # Publish recovery started event
        await self.eventbus.publish(Event.create(
            event_type='infrastructure.recovery.started',
            data={
                'service_name': service_name,
                'strategy': strategy.strategy_type,
                'trigger': trigger_event.data
            },
            source='auto_recovery',
            tenant_id='system',
            correlation_id=trigger_event.id
        ))

        # Execute recovery with retries
        success = await self._execute_recovery(strategy)

        # Record history
        self.recovery_history[service_name].append({
            'timestamp': datetime.utcnow().isoformat(),
            'strategy': strategy.strategy_type,
            'success': success,
            'trigger': trigger_event.data
        })

        # Publish recovery result
        if success:
            await self.eventbus.publish(Event.create(
                event_type='infrastructure.recovery.completed',
                data={
                    'service_name': service_name,
                    'strategy': strategy.strategy_type
                },
                source='auto_recovery',
                tenant_id='system',
                correlation_id=trigger_event.id
            ))
            logger.info(f"✅ Recovery successful for {service_name}")
        else:
            await self.eventbus.publish(Event.create(
                event_type='infrastructure.recovery.failed',
                data={
                    'service_name': service_name,
                    'strategy': strategy.strategy_type,
                    'attempts': strategy.max_attempts
                },
                source='auto_recovery',
                tenant_id='system',
                correlation_id=trigger_event.id
            ))
            logger.error(f"❌ Recovery failed for {service_name} after {strategy.max_attempts} attempts")

        self.recovery_in_progress[service_name] = False

    async def _execute_recovery(self, strategy: RecoveryStrategy) -> bool:
        """Execute recovery with retries"""
        for attempt in range(1, strategy.max_attempts + 1):
            logger.info(f"Recovery attempt {attempt}/{strategy.max_attempts} for {strategy.service_name}")

            try:
                if strategy.recovery_function:
                    # Execute custom recovery function
                    await strategy.recovery_function(strategy.service_name)
                else:
                    # Default recovery based on type
                    await self._default_recovery(strategy)

                # Wait for service to come back up
                await asyncio.sleep(strategy.backoff_seconds)

                # TODO: Check if service is healthy now
                # For now, assume success
                return True

            except Exception as e:
                logger.error(f"Recovery attempt {attempt} failed: {e}")

                if attempt < strategy.max_attempts:
                    # Exponential backoff
                    wait_time = strategy.backoff_seconds * (2 ** (attempt - 1))
                    logger.info(f"Waiting {wait_time}s before next attempt...")
                    await asyncio.sleep(wait_time)

        return False

    async def _default_recovery(self, strategy: RecoveryStrategy):
        """Default recovery actions by strategy type"""
        if strategy.strategy_type == 'restart':
            logger.info(f"Restarting {strategy.service_name}...")
            # TODO: Call Docker restart or systemctl restart
            # For now, just log
            await asyncio.sleep(1)

        elif strategy.strategy_type == 'failover':
            logger.info(f"Failing over {strategy.service_name}...")
            # TODO: Redirect traffic to backup instance
            await asyncio.sleep(1)

        elif strategy.strategy_type == 'circuit_breaker':
            logger.info(f"Opening circuit breaker for {strategy.service_name}...")
            # TODO: Stop sending traffic, use fallback
            await asyncio.sleep(1)

    async def get_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        return {
            'registered_strategies': len(self.strategies),
            'recovery_in_progress': sum(self.recovery_in_progress.values()),
            'total_recoveries': sum(len(h) for h in self.recovery_history.values()),
            'history': self.recovery_history
        }
```

**Test:**
```python
# Test auto-recovery
bus = create_eventbus('memory')
recovery = AutoRecovery(bus)

# Register recovery strategy
await recovery.register_strategy(RecoveryStrategy(
    service_name='api_gateway',
    strategy_type='restart',
    max_attempts=3,
    backoff_seconds=5
))

# Start service
await recovery.start()

# Simulate health event
await bus.publish(Event.create(
    event_type='infrastructure.health.unhealthy',
    data={
        'service_name': 'api_gateway',
        'status': 'unhealthy',
        'message': 'Service not responding'
    },
    source='health_monitor',
    tenant_id='system'
))

# Should trigger recovery
await asyncio.sleep(10)

stats = await recovery.get_stats()
print(stats)  # Should show recovery attempt
```

**Completion Criteria:**
- ✅ AutoRecovery class created
- ✅ Subscribes to health events
- ✅ Executes recovery with retries
- ✅ Publishes recovery events
- ✅ Test passes

---

### Task 1.3: Resource Optimizer ⭐⭐

**Цель:** Оптимизация ресурсов каждые 5 минут

**Файл:** `/infrastructure/eventbus/coordination/resource_optimizer.py` (CREATE)

**Code:**
```python
"""
Resource Optimizer
Optimizes resource allocation every 5 minutes
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

from infrastructure.eventbus import IEventBus, Event

logger = logging.getLogger(__name__)


class ResourceOptimizer:
    """
    Resource Optimizer Service

    Runs every 5 minutes:
    1. Collect resource metrics
    2. Analyze utilization
    3. Optimize allocation
    4. Publish recommendations
    """

    def __init__(self, eventbus: IEventBus):
        self.eventbus = eventbus
        self.optimization_interval = 300  # 5 minutes
        self.running = False
        logger.info("ResourceOptimizer initialized")

    async def start(self):
        """Start optimization cycle"""
        self.running = True
        logger.info("ResourceOptimizer started - running every 5 minutes")

        while self.running:
            try:
                await self._run_optimization_cycle()
            except Exception as e:
                logger.error(f"Optimization cycle error: {e}")

            await asyncio.sleep(self.optimization_interval)

    async def stop(self):
        """Stop optimization cycle"""
        self.running = False
        logger.info("ResourceOptimizer stopped")

    async def _run_optimization_cycle(self):
        """Run single optimization cycle"""
        logger.info("Running resource optimization cycle...")

        # 1. Collect metrics
        metrics = await self._collect_metrics()

        # 2. Analyze
        analysis = await self._analyze_utilization(metrics)

        # 3. Generate recommendations
        recommendations = await self._generate_recommendations(analysis)

        # 4. Publish
        await self.eventbus.publish(Event.create(
            event_type='infrastructure.optimization.completed',
            data={
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics,
                'analysis': analysis,
                'recommendations': recommendations
            },
            source='resource_optimizer',
            tenant_id='system'
        ))

        logger.info(f"Optimization complete - {len(recommendations)} recommendations")

    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect resource metrics"""
        # TODO: Collect from Prometheus or system metrics
        # For now, stub data
        return {
            'cpu': {
                'eventbus': 45.0,
                'database': 72.0,
                'api_gateway': 58.0,
                'rag_pipeline': 35.0
            },
            'memory': {
                'eventbus': 65.0,
                'database': 88.0,
                'api_gateway': 55.0,
                'rag_pipeline': 42.0
            },
            'disk': {
                'database': 78.0
            }
        }

    async def _analyze_utilization(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource utilization"""
        analysis = {
            'overutilized': [],
            'underutilized': [],
            'optimal': []
        }

        for resource_type, services in metrics.items():
            for service, utilization in services.items():
                if utilization > 80:
                    analysis['overutilized'].append({
                        'service': service,
                        'resource': resource_type,
                        'utilization': utilization
                    })
                elif utilization < 30:
                    analysis['underutilized'].append({
                        'service': service,
                        'resource': resource_type,
                        'utilization': utilization
                    })
                else:
                    analysis['optimal'].append({
                        'service': service,
                        'resource': resource_type,
                        'utilization': utilization
                    })

        return analysis

    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> list:
        """Generate optimization recommendations"""
        recommendations = []

        for item in analysis['overutilized']:
            recommendations.append({
                'service': item['service'],
                'resource': item['resource'],
                'action': 'scale_up' if item['utilization'] > 90 else 'optimize',
                'priority': 'high' if item['utilization'] > 90 else 'medium',
                'reason': f"{item['resource']} utilization at {item['utilization']}%"
            })

        for item in analysis['underutilized']:
            if item['utilization'] < 20:
                recommendations.append({
                    'service': item['service'],
                    'resource': item['resource'],
                    'action': 'scale_down',
                    'priority': 'low',
                    'reason': f"{item['resource']} utilization at {item['utilization']}%"
                })

        return recommendations
```

**Test:**
```python
# Test resource optimizer
bus = create_eventbus('memory')
optimizer = ResourceOptimizer(bus)

# Subscribe to optimization events
received = []
async def handler(event):
    received.append(event)
    print("Optimization:", event.data['recommendations'])

await bus.subscribe('infrastructure.optimization.completed', handler)

# Run one cycle (don't wait 5 min)
await optimizer._run_optimization_cycle()

assert len(received) > 0
```

**Completion Criteria:**
- ✅ ResourceOptimizer created
- ✅ Runs every 5 minutes
- ✅ Analyzes utilization
- ✅ Publishes recommendations
- ✅ Test passes

---

### Task 1.4: Infrastructure Coordinator (Main) ⭐⭐⭐

**Цель:** Главный координатор Infrastructure уровня

**Файл:** `/infrastructure/eventbus/coordination/infrastructure_coordinator.py` (CREATE)

**Code:**
```python
"""
Infrastructure Coordinator
Main coordinator for Infrastructure level (Level 1)
"""

import logging
import asyncio

from infrastructure.eventbus import create_eventbus, IEventBus
from intelligent_core.orchestration.ai_orchestration.core.health_monitor import HealthMonitor, HealthCheck
from infrastructure.eventbus.coordination.auto_recovery import AutoRecovery, RecoveryStrategy
from infrastructure.eventbus.coordination.resource_optimizer import ResourceOptimizer

logger = logging.getLogger(__name__)


class InfrastructureCoordinator:
    """
    Infrastructure Level Coordinator

    Coordinates:
    - Health Monitoring (30 sec)
    - Auto-Recovery (event-driven)
    - Resource Optimization (5 min)
    """

    def __init__(self, event_bus_backend='redis', redis_url=None):
        # Create EventBus
        self.eventbus = create_eventbus(event_bus_backend, redis_url=redis_url)

        # Create services
        self.health_monitor = HealthMonitor()
        self.auto_recovery = AutoRecovery(self.eventbus)
        self.resource_optimizer = ResourceOptimizer(self.eventbus)

        logger.info("InfrastructureCoordinator initialized")

    async def start(self):
        """Start all infrastructure services"""
        logger.info("Starting Infrastructure Coordinator...")

        # Connect health monitor to EventBus
        await self.health_monitor.connect_eventbus(self.eventbus)

        # Register critical services for health monitoring
        await self._register_critical_services()

        # Register recovery strategies
        await self._register_recovery_strategies()

        # Start services
        await self.auto_recovery.start()
        asyncio.create_task(self.health_monitor.monitor_continuously())
        asyncio.create_task(self.resource_optimizer.start())

        logger.info("✅ Infrastructure Coordinator started")
        logger.info("  - Health Monitor: Running (30 sec intervals)")
        logger.info("  - Auto-Recovery: Listening for health events")
        logger.info("  - Resource Optimizer: Running (5 min intervals)")

    async def _register_critical_services(self):
        """Register critical services for health monitoring"""
        services = [
            {
                'name': 'eventbus',
                'type': 'http',
                'interval': 30,
                'url': 'http://localhost:8055/health'  # ai-event-manager
            },
            {
                'name': 'api_gateway',
                'type': 'http',
                'interval': 30,
                'url': 'http://localhost:8000/health'
            },
            {
                'name': 'database',
                'type': 'custom',
                'interval': 60,
                'checker': self._check_database
            },
            {
                'name': 'rag_pipeline',
                'type': 'http',
                'interval': 60,
                'url': 'http://localhost:8001/health'
            }
        ]

        for service in services:
            check = HealthCheck(
                service_name=service['name'],
                check_type=service['type'],
                interval=service['interval'],
                config={'url': service.get('url')} if service['type'] == 'http' else {},
                custom_checker=service.get('checker')
            )
            await self.health_monitor.register_check(check)
            logger.info(f"Registered health check: {service['name']}")

    async def _check_database(self, service_name: str, config: dict):
        """Custom database health check"""
        # TODO: Check database connectivity
        # For now, always return healthy
        return True

    async def _register_recovery_strategies(self):
        """Register recovery strategies for critical services"""
        strategies = [
            RecoveryStrategy(
                service_name='eventbus',
                strategy_type='restart',
                max_attempts=3,
                backoff_seconds=5
            ),
            RecoveryStrategy(
                service_name='api_gateway',
                strategy_type='restart',
                max_attempts=3,
                backoff_seconds=10
            ),
            RecoveryStrategy(
                service_name='database',
                strategy_type='circuit_breaker',  # Don't restart DB, use circuit breaker
                max_attempts=1,
                backoff_seconds=30
            ),
            RecoveryStrategy(
                service_name='rag_pipeline',
                strategy_type='restart',
                max_attempts=2,
                backoff_seconds=15
            )
        ]

        for strategy in strategies:
            await self.auto_recovery.register_strategy(strategy)

        logger.info(f"Registered {len(strategies)} recovery strategies")

    async def stop(self):
        """Stop all infrastructure services"""
        logger.info("Stopping Infrastructure Coordinator...")

        await self.health_monitor.stop_monitoring()
        await self.resource_optimizer.stop()
        await self.eventbus.close()

        logger.info("Infrastructure Coordinator stopped")

    async def get_status(self):
        """Get status of all infrastructure services"""
        return {
            'health_monitor': {
                'monitoring': self.health_monitor.monitoring,
                'checks_registered': len(self.health_monitor.checks),
                'results': await self.health_monitor.get_all_results()
            },
            'auto_recovery': await self.auto_recovery.get_stats(),
            'resource_optimizer': {
                'running': self.resource_optimizer.running,
                'interval_seconds': self.resource_optimizer.optimization_interval
            }
        }
```

**Usage:**
```python
# Start Infrastructure Coordinator
coordinator = InfrastructureCoordinator(event_bus_backend='redis')
await coordinator.start()

# Get status
status = await coordinator.get_status()
print(status)

# Runs continuously:
# - Health checks every 30s
# - Auto-recovery on failures
# - Resource optimization every 5min
```

**Completion Criteria:**
- ✅ InfrastructureCoordinator created
- ✅ Starts all 3 services
- ✅ Registers critical services
- ✅ Coordinates via EventBus
- ✅ Can get status
- ✅ Test passes

---

### Task 1.5: Metrics Endpoint ⭐⭐

**Цель:** Expose metrics для Prometheus

**Файл:** `/intelligent-core/orchestration/api/metrics_api.py` (CREATE)

**Code:**
```python
"""
Metrics API
Exposes Prometheus metrics via HTTP
"""

from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Metrics API")


@app.get("/metrics")
def prometheus_metrics():
    """
    Prometheus scrape endpoint

    Returns metrics in Prometheus format
    """
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "service": "metrics_api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)
```

**Run:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration
python -m api.metrics_api
# Runs on port 9090
# Prometheus scrapes http://localhost:9090/metrics
```

**Completion Criteria:**
- ✅ Metrics API created
- ✅ `/metrics` endpoint works
- ✅ Returns Prometheus format
- ✅ Can run on port 9090

---

## 📊 PHASE 1 SUCCESS METRICS

### Health Monitoring
- `infrastructure_health_check_interval_seconds` = 30
- `infrastructure_service_uptime_percent` > 99% (for critical services)
- Events published: `infrastructure.health.unhealthy`, `infrastructure.health.degraded`, `infrastructure.health.healthy`

### Auto-Recovery
- `infrastructure_recovery_triggered_total` > 0 (when failures occur)
- `infrastructure_recovery_success_rate` > 90%
- `infrastructure_time_to_recovery_seconds` P95 < 30s
- Events published: `infrastructure.recovery.started`, `infrastructure.recovery.completed`, `infrastructure.recovery.failed`

### Resource Optimization
- `infrastructure_resource_efficiency_score` > 80
- `infrastructure_optimization_actions_total` > 0 (per cycle)
- Events published: `infrastructure.optimization.completed`

### Integration
- All 3 services communicate via EventBus ✅
- Events flow correctly ✅
- Metrics exported to Prometheus ✅

---

## 🧪 INTEGRATION TEST

**File:** `/tests/integration/test_phase1_infrastructure.py` (CREATE)

```python
import pytest
import asyncio
from infrastructure.eventbus.coordination.infrastructure_coordinator import InfrastructureCoordinator


@pytest.mark.asyncio
async def test_phase1_integration():
    """Test Phase 1: Infrastructure Integration"""

    # Start coordinator
    coordinator = InfrastructureCoordinator(event_bus_backend='memory')
    await coordinator.start()

    # Wait for first health check cycle (30 sec)
    await asyncio.sleep(35)

    # Get status
    status = await coordinator.get_status()

    # Verify health monitoring
    assert status['health_monitor']['monitoring'] == True
    assert status['health_monitor']['checks_registered'] >= 4

    # Verify auto-recovery ready
    assert 'registered_strategies' in status['auto_recovery']
    assert status['auto_recovery']['registered_strategies'] >= 4

    # Verify resource optimizer running
    assert status['resource_optimizer']['running'] == True
    assert status['resource_optimizer']['interval_seconds'] == 300

    # Cleanup
    await coordinator.stop()

    print("✅ Phase 1 Integration Test PASSED")


@pytest.mark.asyncio
async def test_auto_recovery_flow():
    """Test auto-recovery flow"""

    coordinator = InfrastructureCoordinator(event_bus_backend='memory')
    await coordinator.start()

    # Track recovery events
    recovery_events = []
    async def track_recovery(event):
        recovery_events.append(event)

    await coordinator.eventbus.subscribe('infrastructure.recovery.*', track_recovery)

    # Simulate service failure
    await coordinator.eventbus.publish(Event.create(
        event_type='infrastructure.health.unhealthy',
        data={'service_name': 'api_gateway', 'status': 'unhealthy'},
        source='test',
        tenant_id='system'
    ))

    # Wait for recovery
    await asyncio.sleep(10)

    # Should have triggered recovery
    assert len(recovery_events) >= 1
    assert any('recovery.started' in e.event_type for e in recovery_events)

    await coordinator.stop()

    print("✅ Auto-Recovery Flow Test PASSED")
```

---

## 📅 TIMELINE

```
Day 1: Task 1.1 (EventBus in Health Monitor)
Day 2: Task 1.2 (Auto-Recovery)
Day 3: Task 1.3 (Resource Optimizer)
Day 4: Task 1.4 (Infrastructure Coordinator)
Day 5: Task 1.5 (Metrics Endpoint) + Integration Testing
Day 6-7: Buffer + Documentation
```

---

## 🎯 NEXT: PHASE 2

После завершения Phase 1 → переходим к **Phase 2: Core Integration**
- Core Coordinator для event_intelligence
- Learning Cycle (24h)
- Pattern Detection
- Model Training

**Prerequisites от Phase 1:**
- ✅ EventBus работает
- ✅ Infrastructure координация работает
- ✅ Metrics экспортируются

---

**Status:** Ready to Start 🚀
**Approval Needed:** Да, от пользователя перед началом
