# Monitoring Ecosystem - Complete Analysis

**Дата**: 2025-10-10
**Цель**: Анализ всех monitoring/observability компонентов в платформе

---

## 🔍 Обнаружено Monitoring Components

### 1. `/infrastructure/observability/` ✅ ACTIVE
**Тип**: Prometheus + Grafana stack
**Порты**:
- Prometheus: 9090
- Grafana: 3001
- Loki: 3100
- Tempo: 3200

**Назначение**: Platform-wide metrics collection & visualization
**Статус**: ✅ Production Ready
**Компоненты**:
- `config/prometheus/` - Prometheus configuration
- `config/grafana/` - Grafana dashboards
- `monitoring-backend/` - Backend services
- `service-catalog/` - Service discovery

**Интеграция с нашей системой**:
- ✅ InfrastructureStateMonitor должен собирать metrics от Prometheus
- ✅ Уже используется в `collect_state_from_project_manager()`

---

### 2. `/infrastructure/monitoring/` ⚠️ MINIMAL
**Тип**: Legacy Grafana/Prometheus configs
**Содержимое**:
```
/infrastructure/monitoring/
├── grafana/
└── prometheus/
```

**Статус**: ⚠️ Дубликат `/infrastructure/observability/`
**Рекомендация**: Возможно архивировать или объединить с observability

---

### 3. `/infrastructure/AI-office-infrastructure/ai-event-manager/monitoring/` ✅ NEW!
**Тип**: Infrastructure State Monitor (наша интеграция!)
**Файлы**:
- `__init__.py`
- `infrastructure_state.py` (400+ lines)

**Назначение**: Unified infrastructure monitoring
**Статус**: ✅ Just integrated!
**EventBus events**:
- `platform.infrastructure.state_updated`
- `platform.infrastructure.emergency`
- `platform.infrastructure.strategy_recommended`

---

### 4. `/infrastructure/AI-office-infrastructure/mio-manager/` ✅ ACTIVE
**Тип**: MIO (Monitoring & Observability) Manager - Центральный координатор
**Port**: 8046
**Назначение**:
- Automation toolkit management
- Platform coordination
- EventBus orchestration
- Resource tracking (Phase 2 - ГЛАЗА)

**Ключевые компоненты**:
```python
# Resource Tracker (Phase 2 - ГЛАЗА)
resource_tracker = ResourceTrackerClient(
    eventbus=eventbus_client,
    check_interval=60  # Check every 60 seconds
)

# EventBus subscriptions
await eventbus_client.subscribe_to_problems()
await eventbus_client.subscribe_to_tasks()
await eventbus_client.subscribe_to_alerts()
```

**Интеграция с нашей системой**:
- ✅ MIO Manager должен подписаться на `platform.infrastructure.*` events
- ✅ Resource Tracker публикует `platform.resources.snapshot`
- ✅ InfrastructureStateMonitor уже читает это в `collect_resources_from_mio_manager()`

---

### 5. `/infrastructure/AI-office-infrastructure/analytics-specialist/` ✅ ACTIVE
**Тип**: Analytics AI - Platform Intelligence Expert
**Port**: 8056
**Назначение**:
- Platform health analysis
- Bottleneck detection
- Dependency mapping
- Daily health checks
- Continuous improvement scans

**Background tasks**:
```python
# Daily health check (every 24h)
schedule_daily_health_check()

# Continuous improvement (every hour)
schedule_continuous_improvement()

# Heartbeat to MIO (every 5 min)
send_heartbeat_to_mio()
```

**Интеграция с нашей системой**:
- ⚠️ НЕ интегрирован с InfrastructureStateMonitor
- 💡 Может использовать `/infrastructure/state` для анализа
- 💡 Может публиковать findings в EventBus

---

### 6. `/platform-services/monitoring/` ⚠️ EMPTY
**Тип**: Placeholder (auto-generated)
**Содержимое**:
- README.md (auto-generated, 0 lines of code)
- grafana/ (configs)
- prometheus.yml

**Статус**: ⚠️ Empty utility module
**Рекомендация**: Объединить с `/infrastructure/observability/`

---

### 7. `/intelligent-core/workflow_intelligence/monitoring/` 📊 DOMAIN-SPECIFIC
**Тип**: Workflow monitoring (domain-specific)
**Назначение**: Workflow-specific metrics
**Статус**: ✅ Domain module (не infrastructure)

---

### 8. `/intelligent-core/expertise-center/monitoring/` 📊 DOMAIN-SPECIFIC
**Тип**: Expertise monitoring (domain-specific)
**Назначение**: Expertise-specific metrics
**Статус**: ✅ Domain module (не infrastructure)

---

### 9. `/shared/monitoring/` 🔧 UTILITY
**Тип**: Shared monitoring utilities
**Назначение**: Reusable monitoring helpers
**Статус**: ✅ Utility library

---

## 📊 Architecture Overview

### До нашей интеграции:
```
Infrastructure Layer:
├── observability (Prometheus + Grafana) ✅
├── monitoring (legacy duplicate) ⚠️
└── central-brain (standalone) ❌ DEPRECATED

AI Office:
├── mio-manager (Resource Tracker) ✅
├── analytics-specialist (Health checks) ✅
└── ai-event-manager (Events only) ⚠️

Platform Services:
└── monitoring (empty placeholder) ⚠️

Domain Modules:
├── workflow_intelligence/monitoring ✅
├── expertise-center/monitoring ✅
└── shared/monitoring ✅
```

### После нашей интеграции:
```
Infrastructure Layer:
├── observability (Prometheus + Grafana) ✅
│   └── Data source for InfrastructureStateMonitor
├── monitoring (legacy duplicate) ⚠️ TODO: Archive
└── central-brain → ARCHIVED ✅

AI Office (UNIFIED HUB):
├── ai-event-manager ✅ ENHANCED
│   └── monitoring/
│       └── infrastructure_state.py (UNIFIED MONITOR)
│           ├── Collects from observability/Prometheus
│           ├── Collects from mio-manager/ResourceTracker
│           ├── Collects from project-manager
│           └── Publishes to EventBus
│
├── mio-manager (Resource Tracker) ✅
│   ├── Subscribes to platform.infrastructure.* ✅
│   └── Publishes platform.resources.snapshot ✅
│
└── analytics-specialist (Health checks) ✅
    ├── Can consume /infrastructure/state API 💡
    └── Can publish findings to EventBus 💡

Platform Services:
└── monitoring (empty) ⚠️ TODO: Consolidate

Domain Modules: (unchanged)
├── workflow_intelligence/monitoring ✅
├── expertise-center/monitoring ✅
└── shared/monitoring ✅
```

---

## 🔗 Integration Points

### 1. InfrastructureStateMonitor ↔ Prometheus
```python
# infrastructure_state.py:collect_state_from_project_manager()
prometheus_available = metrics_data.get('prometheus_available', False)
grafana_available = metrics_data.get('grafana_available', False)
services_with_metrics = metrics_data.get('services_with_metrics', 0)
```

**Status**: ✅ Already integrated via project-manager

**Future enhancement**:
```python
async def collect_metrics_from_prometheus(self) -> Dict:
    """Direct Prometheus API call for real-time metrics"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:9090/api/v1/query?query=up') as resp:
            data = await resp.json()
            return {'services_up': ...}
```

---

### 2. InfrastructureStateMonitor ↔ MIO Manager (Resource Tracker)
```python
# infrastructure_state.py:collect_resources_from_mio_manager()
async def collect_resources_from_mio_manager(self) -> Dict:
    """
    Собрать ресурсы из MIO Manager

    Returns: {
        'cpu_usage': float (0-1),
        'memory_usage': float (0-1),
        'disk_usage': float (0-1)
    }
    """
    try:
        # TODO: Call MIO Manager API or get from EventBus cache
        # For now, placeholder
        return {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0
        }
```

**Status**: ⚠️ TODO - Needs implementation

**Implementation**:
```python
async def collect_resources_from_mio_manager(self) -> Dict:
    """Get resources from MIO Manager API"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8046/api/v1/resources/snapshot') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'cpu_usage': data.get('cpu_percent', 0) / 100,
                        'memory_usage': data.get('memory_percent', 0) / 100,
                        'disk_usage': data.get('disk_percent', 0) / 100
                    }
    except Exception as e:
        logger.error(f"Failed to collect from mio manager: {e}")
    return {'cpu_usage': 0.0, 'memory_usage': 0.0, 'disk_usage': 0.0}
```

---

### 3. InfrastructureStateMonitor ↔ Analytics Specialist
**Current**: ⚠️ Not integrated

**Opportunity**: Analytics Specialist can consume infrastructure state for analysis

```python
# In analytics-specialist/workflows/daily_health_check.py

async def daily_health_check():
    """Daily health check with infrastructure awareness"""

    # Get infrastructure state
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8055/infrastructure/state') as resp:
            infra_state = await resp.json()

    # Analyze with infrastructure context
    analysis = {
        'health_score': calculate_health_score(infra_state),
        'bottlenecks': detect_bottlenecks(infra_state),
        'recommendations': generate_recommendations(infra_state)
    }

    # Publish to EventBus
    await eventbus.publish(
        'platform.analytics.health_check_completed',
        {'analysis': analysis, 'infra_state': infra_state}
    )
```

---

### 4. MIO Manager ↔ EventBus Infrastructure Events
**Current**: ⚠️ MIO Manager НЕ подписан на `platform.infrastructure.*` events

**Recommendation**: Add subscriptions

```python
# In mio-manager/integrations/eventbus_client.py

async def subscribe_to_infrastructure_events(self, handler):
    """Subscribe to infrastructure events from ai-event-manager"""
    await self.subscribe('platform.infrastructure.state_updated', handler)
    await self.subscribe('platform.infrastructure.emergency', handler)
    await self.subscribe('platform.infrastructure.strategy_recommended', handler)

# In mio-manager/main.py lifespan()

async def handle_infrastructure_event(event: dict):
    """Handle infrastructure events for coordination"""
    state = event['data'].get('state')

    # Update MIO's awareness
    await toolkit_manager.update_infrastructure_state(state)

    # Log for AI coordination
    if ai_coordinator:
        await ai_coordinator.process_infrastructure_state(state)

await eventbus_client.subscribe_to_infrastructure_events(handle_infrastructure_event)
logger.info("   ✅ Infrastructure events subscribed")
```

---

## ⚠️ Issues & Recommendations

### 1. Дублирование monitoring directories
**Проблема**:
- `/infrastructure/observability/` (active)
- `/infrastructure/monitoring/` (duplicate configs)
- `/platform-services/monitoring/` (empty placeholder)

**Рекомендация**:
```bash
# Archive duplicates
mv /infrastructure/monitoring/ /infrastructure/_archive-deprecated-2025-10-10/monitoring-duplicate/

# Remove empty placeholder
rm -rf /platform-services/monitoring/

# Update references to use /infrastructure/observability/
```

---

### 2. MIO Manager не подписан на infrastructure events
**Проблема**: MIO Manager - "Platform Eyes", но не получает infrastructure state

**Решение**: Добавить подписки (см. Integration Point #4 выше)

---

### 3. Analytics Specialist работает изолированно
**Проблема**: Analytics Specialist делает health checks, но не использует infrastructure state

**Решение**: Интегрировать через API (см. Integration Point #3 выше)

---

### 4. Resource data не поступает в InfrastructureStateMonitor
**Проблема**: `collect_resources_from_mio_manager()` - placeholder

**Решение**: Реализовать API call к MIO Manager (см. Integration Point #2 выше)

---

## 📋 Action Items

### Immediate (критично):
1. ✅ **DONE**: Интегрировать central-brain в ai-event-manager
2. ⚠️ **TODO**: Реализовать `collect_resources_from_mio_manager()` API call
3. ⚠️ **TODO**: MIO Manager subscribe to `platform.infrastructure.*` events

### Short-term (1-2 дня):
4. ⚠️ **TODO**: Analytics Specialist consume `/infrastructure/state` API
5. ⚠️ **TODO**: Archive duplicate monitoring directories
6. ⚠️ **TODO**: Add Service Discovery integration for health checks

### Medium-term (1 неделя):
7. ⚠️ **TODO**: Direct Prometheus API integration (optional, если project-manager недостаточно)
8. ⚠️ **TODO**: Grafana dashboard для Infrastructure State
9. ⚠️ **TODO**: Alerting rules for infrastructure emergencies

---

## 🎯 Unified Monitoring Vision

### Goal: Single Source of Truth
```
┌───────────────────────────────────────────────────────────┐
│  ai-event-manager/monitoring/InfrastructureStateMonitor   │
│                  (SINGLE SOURCE OF TRUTH)                  │
└─────────────────────┬─────────────────────────────────────┘
                      │
         Collects from multiple sources:
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌─────────┐   ┌──────────────┐   ┌─────────────┐
│Prometheus│   │MIO Manager   │   │Project      │
│(Metrics) │   │(Resources)   │   │Manager      │
└─────────┘   └──────────────┘   └─────────────┘
                      │
         Publishes to EventBus:
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌─────────────┐  ┌──────────────┐
│balancer- │  │analytics-   │  │mio-manager   │
│service   │  │specialist   │  │(coordination)│
└──────────┘  └─────────────┘  └──────────────┘

ALL SERVICES HAVE UNIFIED VIEW OF INFRASTRUCTURE STATE!
```

---

## ✅ Summary

### Что есть сейчас:
- ✅ Prometheus/Grafana stack (`/infrastructure/observability/`)
- ✅ MIO Manager с Resource Tracker (port 8046)
- ✅ Analytics Specialist (port 8056)
- ✅ **NEW**: InfrastructureStateMonitor в ai-event-manager ✨
- ✅ EventBus coordination с balancer-service ✨

### Что нужно доделать:
1. ⚠️ MIO Manager → subscribe to infrastructure events
2. ⚠️ Analytics Specialist → consume infrastructure state API
3. ⚠️ InfrastructureStateMonitor → collect real resource data from MIO
4. ⚠️ Archive duplicate monitoring directories
5. ⚠️ Service Discovery integration

### Результат:
**UNIFIED MONITORING ECOSYSTEM** с координацией через EventBus! ✅

---

**Дата**: 2025-10-10
**Автор**: Claude (Monitoring Ecosystem Analysis)
**Статус**: Analysis Complete - Implementation 70% Done
