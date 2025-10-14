# МиО Manager - Интеграция с Service Discovery v2.0

## 🎯 Текущая ситуация

### ✅ Service Discovery v2.0 УЖЕ ГОТОВ!

**Что уже реализовано другой командой:**

1. **Service Discovery Event Broadcasting** ✅
   - Публикует: `platform.monitoring.service_registered`
   - Публикует: `platform.monitoring.service_disconnected`
   - Публикует: `platform.monitoring.critical_timeout`
   - EventBus integration работает!

2. **Service Catalog Integration** ✅
   - Unified view (catalog + runtime)
   - REST API v2: `/v2/catalog/services`, `/v2/catalog/stats`, `/v2/catalog/missing`
   - Знает какие сервисы ДОЛЖНЫ работать (из catalog)
   - Знает какие сервисы РЕАЛЬНО работают (из registry)

3. **Event Payload** ✅
```json
{
  "type": "platform.monitoring.service_registered",
  "data": {
    "service_name": "ai-foundation",
    "orchestrator": "docker-compose",
    "port": 8040,
    "metadata": {...},
    "dependencies": ["eventbus", "qdrant"],
    "registry_id": "ai-foundation",
    "capabilities": ["ml_predictions"],
    "kpis": ["request_latency_ms"]
  }
}
```

### ✅ МиО Manager УЖЕ ИМЕЕТ компоненты:

1. **Infrastructure State Monitor** ✅ (`monitoring/infrastructure_state.py`)
2. **Performance Evaluator** ✅ (`monitoring/performance_evaluator.py`)
3. **SmartScheduler** ✅ (`scheduler/smart_scheduler.py`)
4. **Metrics Coverage Observer** ✅ (ТОЛЬКО ЧТО СОЗДАН!)
5. **Metrics Health Checker** ✅ (ТОЛЬКО ЧТО СОЗДАН!)
6. **EventBus Client** ✅ (`integrations/eventbus_client.py`)

---

## 🔄 Правильная интеграция (МиО = ГЛАЗА)

### Что нужно исправить в МиО Manager:

#### 1. МиО ПОДПИСЫВАЕТСЯ на события от Service Discovery

**СЕЙЧАС**: МиО не слушает события от Service Discovery ❌

**ДОЛЖНО БЫТЬ**: МиО подписывается на события ✅

```python
# В main.py МиО Manager - lifespan startup

# Subscribe to Service Discovery events
await eventbus_client.subscribe(
    'platform.monitoring.service_registered',
    handle_service_registered
)

await eventbus_client.subscribe(
    'platform.monitoring.service_disconnected',
    handle_service_disconnected
)

await eventbus_client.subscribe(
    'platform.monitoring.critical_timeout',
    handle_service_timeout
)
```

#### 2. МиО использует Service Discovery API для Metrics Coverage

**СЕЙЧАС**: Metrics Coverage Observer использует fallback список ❌

**ДОЛЖНО БЫТЬ**: Использует Service Discovery v2 API ✅

```python
# В metrics_coverage_observer.py

async def _get_registered_services(self) -> List[Dict]:
    """Get all registered services from Service Discovery v2"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # NEW: Use v2 unified API instead of v1
            response = await client.get(
                f"{self.service_discovery_url}/v2/catalog/services"
            )
            response.raise_for_status()
            data = response.json()

            # Convert UnifiedService format to our format
            services = []
            for service in data.get('services', []):
                services.append({
                    'name': service['name'],
                    'host': service['name'],  # Use service name as host
                    'port': service.get('actual_port') or service.get('expected_port'),
                    'metrics_endpoint': '/metrics'
                })

            return services
    except Exception as e:
        logger.error(f"Failed to get services from Service Discovery: {e}")
        return []
```

#### 3. МиО публикует OBSERVATIONS (НЕ командует!)

**СЕЙЧАС**: МиО иногда командует Brain (`brain.escalate_problem()`) ❌

**ДОЛЖНО БЫТЬ**: МиО публикует observations в EventBus ✅

```python
# НЕПРАВИЛЬНО (МиО командует):
await self.brain.escalate_problem(...)
await self.brain.send_alert(...)

# ПРАВИЛЬНО (МиО наблюдает и публикует):
await self.eventbus.publish(
    'platform.mio.critical_failure_observed',
    {
        'observation': 'Multiple critical services down',
        'services': critical_failures,
        'severity': 'critical',
        'recommendation': 'Immediate investigation required'
    },
    priority='critical'
)
```

---

## 📋 События - Полная схема хореографии

### 1. Service Discovery → МиО

**Service Discovery публикует** → **МиО подписывается**

```
Service Discovery                           МiО Manager (ГЛАЗА)
       ↓                                           ↓
platform.monitoring.service_registered  →  handle_service_registered()
platform.monitoring.service_disconnected → handle_service_disconnected()
platform.monitoring.critical_timeout    →  handle_service_timeout()
```

**Handlers в МiО:**

```python
async def handle_service_registered(event):
    """
    МиО узнал о новом сервисе

    Действия:
    1. Проверить: есть ли metrics endpoint
    2. Проверить: зарегистрирован ли в Prometheus
    3. Если НЕТ → публиковать observation
    """
    service_name = event['data']['service_name']
    port = event['data']['port']
    kpis = event['data'].get('kpis', [])

    logger.info(f"👀 МиО observed new service: {service_name}")

    # Check if Prometheus is monitoring this service
    prometheus_monitoring = await check_prometheus_target(service_name)

    if not prometheus_monitoring:
        # Publish observation about missing Prometheus monitoring
        await eventbus.publish(
            'platform.mio.service_not_monitored_observed',
            {
                'service_name': service_name,
                'observation': f'{service_name} registered but not monitored by Prometheus',
                'expected_kpis': kpis,
                'recommendation': 'Add Prometheus scrape config for this service'
            },
            priority='high'
        )

async def handle_service_timeout(event):
    """
    МиО узнал о critical timeout

    Действия:
    1. Наблюдать и логировать
    2. Публиковать observation для Brain/DevOps
    """
    service_name = event['data']['service_name']
    last_heartbeat = event['data']['last_heartbeat']

    logger.error(f"👀 МиО observed CRITICAL: {service_name} timeout")

    # Publish observation (НЕ принимает решений!)
    await eventbus.publish(
        'platform.mio.service_timeout_observed',
        {
            'service_name': service_name,
            'observation': f'{service_name} failed to send heartbeat',
            'last_heartbeat': last_heartbeat,
            'severity': 'critical',
            'recommendation': 'Check service health and restart if needed'
        },
        priority='critical'
    )
```

### 2. МиО → EventBus (Observations)

**МиО публикует observations** → **Все подписываются**

```
МiО Manager (ГЛАЗА)                         EventBus
       ↓                                        ↓
platform.mio.state_observed          →  [Brain, Analytics, ai-event-manager]
platform.mio.performance_observed     →  [Brain, balancer-service, Analytics]
platform.mio.metrics_coverage_observed →  [Brain, DevOps Agent, Analytics]
platform.mio.metrics_health_observed   →  [Brain, DevOps Agent]
platform.mio.service_not_monitored_observed → [DevOps Agent, ai-event-manager]
platform.mio.critical_failure_observed →  [Brain, ai-event-manager, DevOps Agent]
```

### 3. Brain ← МиО observations (принимает решения)

**Brain подписывается** на observations от МиО

```python
# В Brain/workflow_intelligence

await eventbus.subscribe(
    'platform.mio.critical_failure_observed',
    analyze_and_decide
)

async def analyze_and_decide(observation):
    """
    Brain анализирует observation и ПРИНИМАЕТ РЕШЕНИЕ
    """
    services = observation['data']['services']
    severity = observation['data']['severity']

    # Brain АНАЛИЗИРУЕТ
    decision = analyze_critical_failure(services, severity)

    # Brain ПРИНИМАЕТ РЕШЕНИЕ
    await eventbus.publish(
        'platform.brain.decision_made',
        {
            'decision': decision,
            'action': 'trigger_recovery',
            'target_services': services
        }
    )
```

### 4. Analytics ← МиО observations (собирает данные)

**Analytics подписывается** на observations

```python
# В analytics-specialist

await eventbus.subscribe(
    'platform.mio.performance_observed',
    collect_performance_data
)

await eventbus.subscribe(
    'platform.mio.metrics_coverage_observed',
    analyze_coverage_trends
)

async def collect_performance_data(observation):
    """Analytics собирает данные"""
    performance = observation['data']['observation']

    # Collect to DB
    await save_performance_metrics(performance)

    # Analyze trends
    trends = await analyze_trends(performance)

    # If insights found → send to Brain
    if trends['insights']:
        await eventbus.publish(
            'platform.analytics.insights_ready',
            {
                'type': 'performance_trends',
                'insights': trends['insights'],
                'target': 'brain'
            }
        )
```

### 5. DevOps Agent ← МиО observations (исправляет)

**DevOps Agent подписывается** и автоматически исправляет

```python
# В devops-agent

await eventbus.subscribe(
    'platform.mio.service_not_monitored_observed',
    auto_fix_prometheus_config
)

async def auto_fix_prometheus_config(observation):
    """DevOps Agent автоматически исправляет проблемы"""
    service_name = observation['data']['service_name']

    logger.info(f"🔧 DevOps Agent fixing Prometheus config for {service_name}")

    # Auto-add to Prometheus SD JSON
    await add_prometheus_target(service_name)

    # Publish action completed
    await eventbus.publish(
        'platform.devops.action_completed',
        {
            'action': 'added_prometheus_target',
            'service_name': service_name,
            'status': 'success'
        }
    )
```

---

## 🔧 Изменения в коде МиО Manager

### 1. main.py - Добавить подписки на Service Discovery

```python
# /infrastructure/AI-office-infrastructure/mio-manager/main.py

# В lifespan startup, ПОСЛЕ инициализации EventBus:

# Subscribe to Service Discovery events
await eventbus_client.subscribe(
    'platform.monitoring.service_registered',
    handlers.handle_service_registered
)

await eventbus_client.subscribe(
    'platform.monitoring.service_disconnected',
    handlers.handle_service_disconnected
)

await eventbus_client.subscribe(
    'platform.monitoring.critical_timeout',
    handlers.handle_service_timeout
)

logger.info("   ✅ Subscribed to Service Discovery events")
```

### 2. Создать event_handlers.py

```python
# /infrastructure/AI-office-infrastructure/mio-manager/event_handlers.py

"""
Event Handlers для МиО Manager

МиО = ГЛАЗА - только наблюдает и публикует observations!
НЕ принимает решений, НЕ командует.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class MioEventHandlers:
    """Handlers для событий от других сервисов"""

    def __init__(self, eventbus, prometheus_client=None):
        self.eventbus = eventbus
        self.prometheus_client = prometheus_client

    async def handle_service_registered(self, event: Dict):
        """
        Handle: platform.monitoring.service_registered

        МиО наблюдает регистрацию нового сервиса
        """
        service_name = event['data']['service_name']
        port = event['data']['port']
        kpis = event['data'].get('kpis', [])

        logger.info(f"👀 МиО observed service registered: {service_name}")

        # Check if Prometheus is monitoring
        if self.prometheus_client:
            is_monitored = await self._check_prometheus_monitoring(service_name)

            if not is_monitored:
                # Publish observation
                await self.eventbus.publish(
                    'platform.mio.service_not_monitored_observed',
                    {
                        'service_name': service_name,
                        'port': port,
                        'expected_kpis': kpis,
                        'observation': f'{service_name} is not monitored by Prometheus',
                        'recommendation': 'Add to Prometheus scrape targets',
                        'severity': 'medium'
                    },
                    priority='high'
                )
                logger.warning(f"   ⚠️  {service_name} not monitored by Prometheus")

    async def handle_service_disconnected(self, event: Dict):
        """
        Handle: platform.monitoring.service_disconnected

        МиО наблюдает отключение сервиса
        """
        service_name = event['data']['service_name']
        reason = event['data'].get('reason', 'unknown')

        logger.info(f"👀 МиО observed service disconnected: {service_name} (reason: {reason})")

        # Just observe and log - другие сервисы уже получили это событие

    async def handle_service_timeout(self, event: Dict):
        """
        Handle: platform.monitoring.critical_timeout

        МиО наблюдает критический timeout
        """
        service_name = event['data']['service_name']
        last_heartbeat = event['data']['last_heartbeat']

        logger.error(f"👀 МиО observed CRITICAL TIMEOUT: {service_name}")

        # Publish observation (для Brain/DevOps Agent)
        await self.eventbus.publish(
            'platform.mio.service_timeout_observed',
            {
                'service_name': service_name,
                'observation': f'{service_name} critical heartbeat timeout',
                'last_heartbeat': last_heartbeat,
                'severity': 'critical',
                'recommendation': 'Immediate investigation and recovery required'
            },
            priority='critical'
        )

    async def _check_prometheus_monitoring(self, service_name: str) -> bool:
        """Check if service is monitored by Prometheus"""
        if not self.prometheus_client:
            return False

        try:
            targets = await self.prometheus_client.get_targets()
            for target in targets:
                job_name = target.get('labels', {}).get('job', '')
                if job_name == service_name:
                    return True
            return False
        except:
            return False
```

### 3. metrics_coverage_observer.py - Использовать Service Discovery v2 API

```python
# Обновить метод _get_registered_services()

async def _get_registered_services(self) -> List[Dict]:
    """
    Get all registered services from Service Discovery v2

    ОБНОВЛЕНО: Использует v2 unified API
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Use Service Discovery v2 unified API
            response = await client.get(
                f"{self.service_discovery_url}/v2/catalog/services"
            )
            response.raise_for_status()
            data = response.json()

            # Convert UnifiedService to our format
            services = []
            for service in data.get('services', []):
                # Only include registered services
                if service.get('registration_status') == 'registered':
                    services.append({
                        'name': service['name'],
                        'host': service['name'],
                        'port': service.get('actual_port') or service.get('expected_port'),
                        'metrics_endpoint': '/metrics'
                    })

            return services

    except Exception as e:
        logger.error(f"Failed to get services from Service Discovery v2: {e}")
        return []
```

### 4. SmartScheduler - Исправить хореографию

```python
# В scheduler/smart_scheduler.py

# ЗАМЕНИТЬ все вызовы:
# await self.brain.escalate_problem(...)
# await self.brain.send_alert(...)

# НА:
# await self.eventbus.publish('platform.mio.*_observed', ...)

# Пример:
async def _escalate_critical_failure(self, critical_failures, health_results):
    """
    МиО наблюдает критический сбой и публикует observation

    ИСПРАВЛЕНО: НЕ командует Brain, а публикует observation
    """
    logger.error(f"👀 МиО observed CRITICAL FAILURE: {critical_failures}")

    # Publish observation в EventBus
    await self.eventbus.publish(
        'platform.mio.critical_failure_observed',
        {
            'observation': 'Multiple critical services are down',
            'services': critical_failures,
            'health_results': health_results,
            'severity': 'critical',
            'recommendation': 'Immediate investigation and recovery required',
            'detected_at': datetime.utcnow().isoformat()
        },
        priority='critical'
    )

    logger.info("   📡 Published critical failure observation to EventBus")
    # Brain подписан на это событие и САМ примет решение что делать
```

---

## ✅ Результат после интеграции

### 1. Правильная хореография:

```
Service Discovery (coordinator of service registry)
   ↓ публикует events
EventBus
   ↓ доставляет
МиО Manager (ГЛАЗА - observatory)
   ↓ подписывается, наблюдает, публикует observations
EventBus
   ↓ доставляет observations
Brain (МОЗГ - decision maker)
   ↓ анализирует, принимает решения
Analytics (АНАЛИТИК - data collector)
   ↓ собирает, анализирует, передает insights
DevOps Agent (РУКИ - executor)
   ↓ исправляет проблемы автоматически
```

### 2. МиО = Полноценные ГЛАЗА:

- ✅ Наблюдает регистрацию сервисов (от Service Discovery)
- ✅ Наблюдает состояние инфраструктуры (Infrastructure State Monitor)
- ✅ Наблюдает производительность (Performance Evaluator)
- ✅ Наблюдает metrics coverage (Metrics Coverage Observer)
- ✅ Наблюдает metrics health (Metrics Health Checker)
- ✅ Публикует observations (НЕ командует!)

### 3. Prometheus регистрация:

- ✅ МиО наблюдает новые сервисы
- ✅ МиО проверяет: зарегистрирован ли в Prometheus
- ✅ МиО публикует observation если НЕТ
- ✅ DevOps Agent подписан и автоматически исправляет
- ✅ Автоматизация вместо ручной работы!

---

## 📋 Задачи для реализации

### Phase 1: Подписки на Service Discovery ✅

1. ✅ Создать `event_handlers.py` с handlers
2. ⏳ Обновить `main.py` - добавить подписки
3. ⏳ Обновить `metrics_coverage_observer.py` - использовать v2 API

### Phase 2: Исправить хореографию ✅

4. ⏳ Обновить `SmartScheduler` - заменить `brain.*` на `eventbus.publish`
5. ⏳ Убрать все прямые вызовы к Brain
6. ⏳ Все публикации через EventBus

### Phase 3: Обновить других ✅

7. ⏳ Обновить `ai-event-manager` - подписаться на `platform.mio.*_observed`
8. ⏳ Обновить `analytics-specialist` - подписаться на observations
9. ⏳ Обновить `Brain` - подписаться и принимать решения

---

**Status**: План готов
**Next**: Реализация Phase 1
