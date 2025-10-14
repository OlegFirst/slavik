# Service Discovery Event Broadcasting

**Дата**: 2025-10-11
**Статус**: ✅ Реализовано
**Версия**: Service Discovery v2.0

---

## 🎯 Что реализовано

**Service Discovery** теперь **автоматически уведомляет** несколько заинтересованных сервисов при регистрации/отключении любого сервиса через **Event Broadcasting**.

### Принцип работы:

Когда сервис регистрируется в Service Discovery:
1. ✅ Сервис регистрируется в ServiceRegistry
2. ✅ Создается UnifiedService (catalog + runtime)
3. ✅ **НОВОЕ**: Публикуется **6 разных events** для заинтересованных сервисов
4. ✅ Каждый сервис получает событие на своём топике

---

## 📡 Event Broadcasting Architecture

```
┌────────────────────────────────────────────────────────┐
│          Service Discovery (Port 8500)                 │
│                                                         │
│  1. Регистрирует сервис                               │
│  2. Определяет KPIs, capabilities, dependencies       │
│  3. Присваивает registry_id                           │
│  4. BROADCASTS события на 5+ топиков                  │
└────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┼────────────────┬───────────────┐
        ↓                ↓                ↓               ↓
┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────────┐
│ MIO Manager  │  │  Analytics   │  │   Policy   │  │   Balancer   │
│              │  │  Specialist  │  │   Engine   │  │   Service    │
├──────────────┤  ├──────────────┤  ├────────────┤  ├──────────────┤
│ Топик:       │  │ Топик:       │  │ Топик:     │  │ Топик:       │
│ monitoring.  │  │ analytics.   │  │ policy.    │  │ balancer.    │
│ service_     │  │ new_service  │  │ service_   │  │ service_     │
│ registered   │  │              │  │ registered │  │ available    │
└──────────────┘  └──────────────┘  └────────────┘  └──────────────┘
        ↓                ↓                ↓               ↓
   Starts           Analyzes         Applies         Adds to
  monitoring       dependencies      policies      load balancer
                                                        pool
```

---

## 🔔 Event Types

### 1. **Service Registration** (Новый сервис зарегистрирован)

**Когда**: Сервис подключается и регистрируется

**Главное событие**:
```json
{
  "type": "platform.service_discovery.service_connected",
  "data": {
    "service_name": "ai-foundation",
    "orchestrator": "docker-compose",
    "port": 8040,
    "metadata": {
      "version": "1.0.0",
      "capabilities": ["ml_predictions", "knowledge_graph"],
      "type": "intelligent-core"
    },
    "dependencies": ["eventbus", "qdrant", "redis"],
    "timestamp": "2025-10-11T12:00:00.123456",
    "registry_id": "ai-foundation",
    "capabilities": ["ml_predictions", "knowledge_graph"],
    "kpis": ["request_latency_ms", "ai_decisions_total"]
  }
}
```

**Дополнительные топики** (broadcast):

1. **`platform.monitoring.service_registered`**
   → **MIO Manager** получает и начинает мониторинг

2. **`platform.analytics.new_service`**
   → **Analytics Specialist** анализирует dependencies и capabilities

3. **`platform.policy.service_registered`**
   → **Policy Engine** применяет policies для этого сервиса

4. **`platform.balancer.service_available`**
   → **Balancer Service** добавляет в пул балансировки

5. **`platform.ai_events.service_registered`**
   → **AI Event Manager** учитывает при принятии решений

---

### 2. **Service Disconnection** (Сервис отключился)

**Когда**: Сервис gracefully shutdown или упал

**Главное событие**:
```json
{
  "type": "platform.service_discovery.service_disconnected",
  "data": {
    "service_name": "ai-foundation",
    "reason": "graceful_shutdown",
    "timestamp": "2025-10-11T13:00:00.123456",
    "registry_id": "ai-foundation"
  }
}
```

**Broadcast топики**:

1. **`platform.monitoring.service_disconnected`**
   → **MIO Manager** логирует disconnect

2. **`platform.analytics.service_down`**
   → **Analytics** обновляет статистику downtime

3. **`platform.policy.service_failed`**
   → **Policy Engine** запускает recovery процедуры!

4. **`platform.balancer.service_unavailable`**
   → **Balancer** убирает из load balancer pool

5. **`platform.ai_events.service_disconnected`**
   → **AI Event Manager** adjusts strategies

---

### 3. **Heartbeat Timeout** (CRITICAL - Сервис не отвечает)

**Когда**: Сервис не отправил heartbeat > 60 секунд

**Главное событие**:
```json
{
  "type": "platform.service_discovery.heartbeat_timeout",
  "data": {
    "service_name": "ai-foundation",
    "last_heartbeat": "2025-10-11T12:58:00.123456",
    "timeout_seconds": 60,
    "timestamp": "2025-10-11T13:00:00.123456",
    "registry_id": "ai-foundation",
    "severity": "critical"
  }
}
```

**CRITICAL Broadcast топики**:

1. **`platform.monitoring.critical_timeout`**
   → **MIO Manager** немедленно реагирует

2. **`platform.analytics.service_timeout`**
   → **Analytics** логирует для RCA

3. **`platform.policy.service_timeout`**
   → **Policy Engine** TRIGGERS AUTO-RECOVERY!

4. **`platform.balancer.service_timeout`**
   → **Balancer** немедленно убирает из pool

5. **`platform.ai_events.critical_timeout`**
   → **AI Event Manager** критическое событие

6. **`platform.alerts.critical`**
   → **Alert System** отправляет уведомления команде

---

## 🔄 Event Flow Examples

### Example 1: Новый сервис регистрируется

```
1. ai-foundation запускается
   ↓
2. EventBus Helper публикует: platform.service.started
   ↓
3. Service Discovery получает событие
   ↓
4. ServiceRegistry.register("ai-foundation")
   ↓
5. CatalogIntegration обогащает данными (KPIs, business process)
   ↓
6. 📢 BROADCAST на 5 топиков:
   - platform.monitoring.service_registered
   - platform.analytics.new_service
   - platform.policy.service_registered
   - platform.balancer.service_available
   - platform.ai_events.service_registered
   ↓
7. Каждый сервис реагирует:
   - MIO Manager: Начинает мониторинг
   - Analytics: Анализирует зависимости
   - Policy Engine: Применяет policies
   - Balancer: Добавляет в pool
   - AI Event Manager: Обновляет состояние платформы
```

### Example 2: Сервис падает без heartbeat

```
1. ai-foundation упал (без graceful shutdown)
   ↓
2. Service Discovery не получает heartbeat 60 секунд
   ↓
3. Heartbeat monitor обнаруживает timeout
   ↓
4. ServiceRegistry.update_status("ai-foundation", "failed")
   ↓
5. 📢 CRITICAL BROADCAST на 6 топиков:
   - platform.monitoring.critical_timeout
   - platform.analytics.service_timeout
   - platform.policy.service_timeout      ← TRIGGERS RECOVERY!
   - platform.balancer.service_timeout
   - platform.ai_events.critical_timeout
   - platform.alerts.critical
   ↓
6. Policy Engine получает событие:
   ↓
7. PolicyAwareOrchestrator запускает recovery:
   - Проверяет policy для ai-foundation
   - RTO = 120 секунд
   - Strategy = auto-restart
   - Max attempts = 3
   ↓
8. Пытается перезапустить ai-foundation
   ↓
9. Если успешно → публикует platform.service.started
   ↓
10. Цикл повторяется (регистрация)
```

---

## 📊 Данные в событиях

### Обязательные поля (все события):

| Поле | Тип | Описание |
|------|-----|----------|
| `type` | string | Тип события |
| `data` | object | Payload события |
| `data.service_name` | string | Имя сервиса |
| `data.timestamp` | string | ISO 8601 timestamp |
| `data.registry_id` | string | ID в Service Registry |

### Дополнительные поля (registration):

| Поле | Тип | Описание |
|------|-----|----------|
| `data.orchestrator` | string | Кто управляет (docker-compose, k8s, etc) |
| `data.port` | int | Порт сервиса |
| `data.metadata` | object | Метаданные сервиса |
| `data.metadata.capabilities` | array | Возможности сервиса |
| `data.metadata.type` | string | Тип сервиса |
| `data.dependencies` | array | Зависимости |
| `data.kpis` | array | KPIs для мониторинга |

### Дополнительные поля (timeout):

| Поле | Тип | Описание |
|------|-----|----------|
| `data.last_heartbeat` | string | Время последнего heartbeat |
| `data.timeout_seconds` | int | Таймаут (60s) |
| `data.severity` | string | "critical" |

---

## 🛠️ Реализация для подписчиков

### MIO Manager - Подписка на события

```python
# В MIO Manager main.py

from integrations.eventbus_client import EventBusClient

# Startup
eventbus = EventBusClient()
await eventbus.connect()

# Subscribe to registration events
await eventbus.subscribe(
    'platform.monitoring.service_registered',
    handle_new_service
)

# Subscribe to critical timeouts
await eventbus.subscribe(
    'platform.monitoring.critical_timeout',
    handle_critical_timeout
)

# Handler
async def handle_new_service(event):
    service_name = event['data']['service_name']
    port = event['data']['port']
    kpis = event['data']['kpis']

    # Start monitoring this service
    logger.info(f"📊 Starting monitoring for {service_name}")
    await start_monitoring(service_name, port, kpis)

async def handle_critical_timeout(event):
    service_name = event['data']['service_name']

    # IMMEDIATE ACTION
    logger.error(f"🚨 CRITICAL: {service_name} timeout!")
    await send_alert_to_ops_team(service_name)
    await trigger_incident_response(service_name)
```

### Analytics Specialist - Подписка

```python
# В Analytics Specialist

await eventbus.subscribe(
    'platform.analytics.new_service',
    analyze_new_service
)

async def analyze_new_service(event):
    service_name = event['data']['service_name']
    dependencies = event['data']['dependencies']
    capabilities = event['data']['capabilities']

    # Analyze dependencies
    logger.info(f"🔍 Analyzing {service_name}")
    await analyze_dependencies(service_name, dependencies)
    await map_capabilities(service_name, capabilities)

    # Update dependency graph
    await update_dependency_graph(service_name)
```

### Policy Engine - Подписка (ВАЖНО!)

```python
# В Policy Engine или PolicyAwareOrchestrator

await eventbus.subscribe(
    'platform.policy.service_registered',
    apply_policies
)

await eventbus.subscribe(
    'platform.policy.service_timeout',
    trigger_recovery  # ← КРИТИЧНО!
)

async def apply_policies(event):
    service_name = event['data']['service_name']

    # Load policies for this service
    policy = load_policy(service_name)

    if policy:
        logger.info(f"📋 Applying policy for {service_name}")
        await configure_monitoring(service_name, policy)
        await setup_recovery_rules(service_name, policy)

async def trigger_recovery(event):
    service_name = event['data']['service_name']
    severity = event['data']['severity']

    if severity == 'critical':
        logger.error(f"🔴 CRITICAL: Triggering recovery for {service_name}")

        # Load recovery policy
        policy = load_policy(service_name)

        # Execute recovery
        await execute_recovery(
            service_name=service_name,
            strategy=policy['recovery_strategy'],
            rto=policy['rto_seconds'],
            max_attempts=policy['max_auto_attempts']
        )
```

---

## 🎯 Use Cases

### Use Case 1: New Service Auto-Configuration

**Scenario**: Разработчик деплоит новый сервис `risk-analyzer`

**Flow**:
```
1. Developer: docker-compose up risk-analyzer
   ↓
2. risk-analyzer.py запускается с EventBusHelper
   ↓
3. EventBusHelper публикует: platform.service.started
   ↓
4. Service Discovery регистрирует + BROADCASTS
   ↓
5. MIO Manager получает event → начинает мониторинг
   ↓
6. Analytics получает event → анализирует dependencies
   ↓
7. Policy Engine получает event → применяет policies
   ↓
8. Balancer получает event → добавляет в pool
   ↓
9. Admin Panel обновляется → показывает новый сервис
```

**Результат**: Сервис автоматически интегрируется в платформу без ручной конфигурации!

---

### Use Case 2: Service Failure Auto-Recovery

**Scenario**: Сервис `ai-foundation` упал

**Flow**:
```
1. ai-foundation процесс убит
   ↓
2. Heartbeat останавливается
   ↓
3. Service Discovery: 60 секунд без heartbeat
   ↓
4. CRITICAL BROADCAST на 6 топиков
   ↓
5. Policy Engine получает: platform.policy.service_timeout
   ↓
6. PolicyAwareOrchestrator:
   - Загружает policy для ai-foundation
   - RTO = 120s, strategy = auto-restart
   ↓
7. Запускает recovery:
   docker-compose restart ai-foundation
   ↓
8. ai-foundation перезапускается
   ↓
9. EventBusHelper публикует: platform.service.started
   ↓
10. Service Discovery: BROADCAST registration
   ↓
11. Все сервисы получают уведомление о восстановлении
```

**Результат**: Автоматическое восстановление без участия человека!

---

## 📈 Metrics & Monitoring

### Service Discovery Metrics:

```python
from prometheus_client import Counter, Histogram

# Metrics
service_registrations_total = Counter(
    'service_discovery_registrations_total',
    'Total service registrations',
    ['service_name', 'orchestrator']
)

service_disconnections_total = Counter(
    'service_discovery_disconnections_total',
    'Total service disconnections',
    ['service_name', 'reason']
)

heartbeat_timeouts_total = Counter(
    'service_discovery_heartbeat_timeouts_total',
    'Total heartbeat timeouts',
    ['service_name']
)

broadcast_events_total = Counter(
    'service_discovery_broadcast_events_total',
    'Total broadcast events sent',
    ['event_type', 'topic']
)

broadcast_duration_seconds = Histogram(
    'service_discovery_broadcast_duration_seconds',
    'Time to broadcast all events',
    ['event_type']
)
```

---

## 🔧 Configuration

### EventBus Heartbeat Timeout:

```python
# В Service Discovery main.py

eventbus_integration = ServiceDiscoveryEventBusIntegration(
    service_registry=service_registry,
    eventbus=eventbus,
    heartbeat_timeout=60  # ← Configurable (default 60s)
)
```

### Broadcast Topics (расширяемые):

```python
# В eventbus_integration.py

# При регистрации
interested_services = [
    'platform.monitoring.service_registered',
    'platform.analytics.new_service',
    'platform.policy.service_registered',
    'platform.balancer.service_available',
    'platform.ai_events.service_registered',
    # Можно добавлять новые топики
]

# При critical timeout
critical_topics = [
    'platform.monitoring.critical_timeout',
    'platform.analytics.service_timeout',
    'platform.policy.service_timeout',
    'platform.balancer.service_timeout',
    'platform.ai_events.critical_timeout',
    'platform.alerts.critical',
    # Можно добавлять
]
```

---

## 🎉 Benefits

### ✅ До Event Broadcasting:

- ❌ Сервисы регистрируются, но никто не знает
- ❌ MIO Manager должен сам опрашивать Service Discovery
- ❌ Policy Engine не знает о новых сервисах
- ❌ Balancer не обновляется автоматически
- ❌ Нет автоматического recovery

### ✅ После Event Broadcasting:

- ✅ **Immediate notification** всех заинтересованных сервисов
- ✅ **Автоматический мониторинг** (MIO Manager)
- ✅ **Автоматический анализ** (Analytics)
- ✅ **Автоматическое recovery** (Policy Engine)
- ✅ **Автоматическая балансировка** (Balancer)
- ✅ **Распределение ответственности** между сервисами
- ✅ **Event-driven architecture** - loose coupling

---

## 📊 Event Statistics

После реализации можно мониторить:

```bash
# Prometheus query
curl http://localhost:9090/api/v1/query?query=service_discovery_broadcast_events_total

# Example response:
{
  "service_discovery_broadcast_events_total{event_type='registration', topic='platform.monitoring.service_registered'}": 127,
  "service_discovery_broadcast_events_total{event_type='registration', topic='platform.policy.service_registered'}": 127,
  "service_discovery_broadcast_events_total{event_type='timeout', topic='platform.alerts.critical'}": 3,
  ...
}
```

---

## ✅ Summary

**Реализован полный Event Broadcasting в Service Discovery:**

- ✅ **Registration events** → 5 заинтересованных сервисов
- ✅ **Disconnection events** → 5 заинтересованных сервисов
- ✅ **Critical timeout events** → 6 заинтересованных сервисов (включая alerts)
- ✅ **Rich event payload** с registry_id, capabilities, KPIs, dependencies
- ✅ **Автоматическое распределение** информации
- ✅ **Event-driven recovery** через Policy Engine
- ✅ **Loose coupling** - сервисы не знают друг о друге напрямую

**Теперь Service Discovery = Event Broadcasting Hub!**

---

**Status**: ✅ COMPLETE
**Version**: Service Discovery v2.0
**Date**: 2025-10-11
