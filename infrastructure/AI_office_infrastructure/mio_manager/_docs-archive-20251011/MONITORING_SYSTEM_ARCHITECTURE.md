# Архитектура системы мониторинга AI Platform ISO 22301

**Version**: 2.0 (MIO EYES Integration Complete)
**Date**: October 11, 2025
**Status**: ✅ Production Ready

## Обзор системы

Система мониторинга AI Platform построена по принципу **Event-Driven Choreography** с разделением на автономные компоненты.

```
┌─────────────────────────────────────────────────────────────────┐
│                    СИСТЕМА МОНИТОРИНГА                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Prometheus   │◄───│ Service      │◄───│ Services     │     │
│  │ (Metrics)    │    │ Discovery    │    │ (Exporters)  │     │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘     │
│         │                   │                                  │
│         │ scrape            │ events                          │
│         ▼                   ▼                                  │
│  ┌──────────────────────────────────────┐                     │
│  │   MIO Manager (EYES/Observatory)     │                     │
│  │   ================================    │                     │
│  │   Phase 1: Coverage & Health         │                     │
│  │   ├─ MetricsCoverageObserver         │                     │
│  │   ├─ MetricsHealthChecker            │                     │
│  │   └─ Event Handlers                  │                     │
│  │                                       │                     │
│  │   Phase 2: Intelligence (Future)     │                     │
│  │   ├─ EventGapDetector                │                     │
│  │   ├─ MLModelPerformanceMonitor       │                     │
│  │   ├─ StuckOrganizationDetector       │                     │
│  │   ├─ CoordinationConflictDetector    │                     │
│  │   └─ ExpertiseQualityMonitor         │                     │
│  └──────────────┬───────────────────────┘                     │
│                 │ observations                                 │
│                 ▼                                              │
│  ┌──────────────────────────────────────┐                     │
│  │           EventBus                   │                     │
│  │   platform.mio.* events              │                     │
│  └──────────────┬───────────────────────┘                     │
│                 │ subscribes                                   │
│                 ▼                                              │
│  ┌─────────────────────────────────────────────────┐          │
│  │  Decision & Action Layer                        │          │
│  │  ├─ Brain (AI Event Manager) - Decisions        │          │
│  │  ├─ DevOps Agent - Auto-fixes                   │          │
│  │  └─ Analytics Specialist - Analysis             │          │
│  └─────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Компоненты системы

### 1.1 Prometheus (Metrics Collection)

**Расположение**: `/infrastructure/monitoring/prometheus/`
**Порт**: 9090
**Тип**: Time-series database + scraper

**Функции**:
- Scraping metrics endpoints (`/metrics`) всех сервисов
- Хранение временных рядов метрик
- Alerts на основе правил
- Service Discovery integration (auto-configuration)

**Конфигурация**:
```yaml
# /infrastructure/observability/prometheus-local.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'service-discovery'
    static_configs:
      - targets: ['service-discovery:8500']

  - job_name: 'mio-manager'
    static_configs:
      - targets: ['mio-manager:8046']

  # ... 40+ других сервисов
```

**Проблема**: ❌ Все 40+ сервисов прописаны вручную (статически)
**Решение**: 🔄 Service Discovery v2.0 + MIO EYES автоматизируют обнаружение

---

### 1.2 Service Discovery v2.0 (Unified Catalog + Registry)

**Расположение**: `/infrastructure/runtime/service-discovery/`
**Порт**: 8500
**API Version**: v2.0

**Функции**:
- **Catalog Integration**: Загрузка `service-catalog.yaml` (27 сервисов)
- **Runtime Registry**: Отслеживание запущенных сервисов
- **Unified View**: Комбинирование catalog (static) + registry (dynamic)
- **Event Broadcasting**: Публикация lifecycle events в EventBus

**Компоненты**:
```python
# catalog_integration.py
class CatalogIntegration:
    - load_catalog()                    # Загружает service-catalog.yaml
    - get_all_unified_services()        # Catalog + Runtime
    - get_missing_services()            # В catalog но не running
    - get_unknown_services()            # Running но не в catalog
    - get_catalog_stats()               # Статистика

# service_registry.py
class ServiceRegistry:
    - register()                        # Регистрация сервиса
    - update_health()                   # Обновление health
    - list_services()                   # Список runtime services

# health_monitor.py
class HealthMonitor:
    - check_service()                   # HTTP health check
    - monitor_continuously()            # Background checks

# eventbus_integration.py
class EventBusIntegration:
    - on_service_registered()           # → platform.monitoring.service_registered
    - on_service_disconnected()         # → platform.monitoring.service_disconnected
    - on_critical_timeout()             # → platform.monitoring.critical_timeout
```

**API Endpoints**:
```http
# v1 (legacy)
GET  /services                  # Runtime services only
POST /register                  # Register service
GET  /health/{service_name}     # Health check

# v2 (new - unified catalog)
GET /v2/catalog/services        # All services (catalog + runtime)
GET /v2/catalog/missing         # Missing services
GET /v2/catalog/unknown         # Unknown services
GET /v2/catalog/stats           # Statistics
```

**Events Published**:
```yaml
platform.monitoring.service_registered:
  service_name: "mio-manager"
  port: 8046
  orchestrator: "unified_orchestrator"
  kpis: ["coverage_percentage", "alert_response_time"]
  timestamp: "2025-10-11T01:00:00Z"

platform.monitoring.service_disconnected:
  service_name: "api-gateway"
  reason: "shutdown"
  timestamp: "2025-10-11T01:05:00Z"

platform.monitoring.critical_timeout:
  service_name: "db-intelligence"
  last_heartbeat: "2025-10-11T00:58:00Z"
  timeout_seconds: 60
  timestamp: "2025-10-11T01:00:00Z"
```

---

### 1.3 MIO Manager (EYES / Observatory)

**Расположение**: `/infrastructure/AI-office-infrastructure/mio-manager/`
**Порт**: 8046
**Роль**: **Observatory (ГЛАЗА) - только наблюдает, НЕ командует!**

**Архитектурный принцип**: Event-Driven Choreography
- ✅ Наблюдает события
- ✅ Проверяет состояния
- ✅ Публикует observations
- ❌ НЕ принимает решений
- ❌ НЕ отдает команды
- ❌ НЕ исправляет проблемы

#### 1.3.1 Структура MIO Manager

```
/mio-manager/
├── main.py                          # FastAPI app + lifecycle
├── config.py                        # Settings
├── database.py                      # SQLite persistence
│
├── event_handlers.py                # 🆕 Phase 2.1 - Service Discovery events
│   └── MioEventHandlers
│       ├── handle_service_registered()
│       ├── handle_service_disconnected()
│       └── handle_critical_timeout()
│
├── monitoring/                      # 🆕 Phase 2.1 - EYES components
│   ├── metrics_coverage_observer.py # Coverage: SD v2 vs Prometheus
│   └── metrics_health_checker.py    # Health: Scrape errors, staleness
│
├── intelligence/                    # Phase 2.2 (Future)
│   ├── event_gap_detector.py
│   ├── ml_model_performance_monitor.py
│   ├── stuck_organization_detector.py
│   ├── coordination_conflict_detector.py
│   └── expertise_quality_monitor.py
│
├── scheduler/
│   ├── smart_scheduler.py           # ✅ Updated - EventBus choreography
│   └── cycles registration
│
├── api/                             # REST API endpoints
├── models/                          # Data models
├── repositories/                    # Data persistence
└── workflows/                       # Temporal workflows (future)
```

#### 1.3.2 Phase 2.1 Components (READY)

##### A. MetricsCoverageObserver

**Файл**: `/monitoring/metrics_coverage_observer.py`
**Цель**: Обнаружение сервисов без мониторинга

**Алгоритм**:
```python
1. Получить все сервисы из Service Discovery v2.0
   → GET /v2/catalog/services

2. Получить все targets из Prometheus
   → GET /api/v1/targets

3. Сравнить списки:
   - Monitored: Есть в SD + есть в Prometheus
   - Not Monitored: Есть в SD + НЕТ в Prometheus ⚠️
   - Unknown: НЕТ в SD + есть в Prometheus

4. Вычислить coverage:
   coverage_pct = (monitored / total_registered) * 100

5. Публиковать observation:
   → platform.mio.metrics_coverage_observed
```

**Observation Events**:
```yaml
# Every 5 minutes
platform.mio.metrics_coverage_observed:
  coverage_percentage: 85.5
  total_services: 27
  monitored_services: 23
  not_monitored_services: 4
  unknown_services: 2
  not_monitored_list: ["api-gateway", "bia-service", ...]
  recommendation: "4 services not monitored by Prometheus"

# Если найден service без мониторинга
platform.mio.service_not_monitored_observed:
  service_name: "api-gateway"
  port: 8080
  expected_metrics_endpoint: "http://localhost:8080/metrics"
  severity: "high"
```

##### B. MetricsHealthChecker

**Файл**: `/monitoring/metrics_health_checker.py`
**Цель**: Проверка здоровья metrics endpoints

**Алгоритм**:
```python
1. Получить все Prometheus targets
   → GET /api/v1/targets

2. Для каждого target проверить:
   - Endpoint reachable? (health == 'up')
   - Last scrape fresh? (< 120 seconds old)
   - Scrape errors? (lastError)
   - Scrape duration OK? (< 5 seconds)

3. Классифицировать:
   - healthy: Всё OK
   - warning: Stale metrics или slow scrape
   - critical: Unreachable или scrape error

4. Публиковать observation:
   → platform.mio.metrics_health_observed
```

**Observation Events**:
```yaml
# Every 1 minute
platform.mio.metrics_health_observed:
  overall_health: "degraded"
  total_services: 23
  healthy_services: 20
  warning_services: 2
  critical_services: 1
  unreachable_services: 1
  critical_issues:
    - "api-gateway: Endpoint unreachable"
    - "bia-service: Stale metrics (150s ago)"
  recommendation: "1 unreachable service, investigate"

# Если критичная проблема
platform.mio.metrics_health_issue_observed:
  overall_health: "critical"
  critical_services: 3
  unreachable_services: 2
  severity: "critical"
  recommendation: "CRITICAL: Immediate investigation required"
```

##### C. Event Handlers (Service Discovery Integration)

**Файл**: `/event_handlers.py`
**Цель**: Реагировать на lifecycle events от Service Discovery

**Подписки**:
```python
# При старте MIO Manager подписывается:
await eventbus.subscribe(
    'platform.monitoring.service_registered',
    mio_event_handlers.handle_service_registered
)

await eventbus.subscribe(
    'platform.monitoring.service_disconnected',
    mio_event_handlers.handle_service_disconnected
)

await eventbus.subscribe(
    'platform.monitoring.critical_timeout',
    mio_event_handlers.handle_critical_timeout
)
```

**Обработчики**:
```python
async def handle_service_registered(event):
    """Новый сервис зарегистрировался"""
    service_name = event['data']['service_name']
    port = event['data'].get('port')

    # 1. Проверить: мониторится ли Prometheus?
    is_monitored = await check_prometheus_monitoring(service_name)
    if not is_monitored:
        # Публикуем observation (НЕ команду!)
        await eventbus.publish(
            'platform.mio.service_not_monitored_observed',
            {...}
        )

    # 2. Проверить: доступен ли metrics endpoint?
    if port:
        metrics_accessible = await check_metrics_endpoint(
            f"http://localhost:{port}/metrics"
        )
        if not metrics_accessible:
            await eventbus.publish(
                'platform.mio.metrics_endpoint_unreachable_observed',
                {...}
            )

async def handle_service_disconnected(event):
    """Сервис отключился"""
    service_name = event['data']['service_name']

    # Публикуем observation о disconnection
    await eventbus.publish(
        'platform.mio.service_disconnection_observed',
        {...}
    )

async def handle_critical_timeout(event):
    """Критический timeout (heartbeat > 60s)"""
    service_name = event['data']['service_name']

    # Публикуем critical observation
    await eventbus.publish(
        'platform.mio.service_timeout_observed',
        {...},
        priority='high'
    )
```

##### D. SmartScheduler (Observation Cycles)

**Файл**: `/scheduler/smart_scheduler.py`
**Цель**: Запуск observation cycles по расписанию

**Cycles (Phase 2.1)**:
```python
# Metrics Coverage - каждые 5 минут
scheduler.add_job(
    _observe_metrics_coverage,
    IntervalTrigger(minutes=5),
    id='observe_metrics_coverage'
)

# Metrics Health - каждую минуту
scheduler.add_job(
    _check_metrics_health,
    IntervalTrigger(minutes=1),
    id='check_metrics_health'
)
```

**Cycles (Phase 2.2 - Future)**:
```python
# Event Gap Detection - каждые 10 минут
# ML Model Performance - каждые 30 минут
# Stuck Organizations - каждые 15 минут
# Coordination Conflicts - каждые 5 минут
# Expertise Quality - каждые 30 минут
```

**Choreography Fix** ✅:
```python
# ❌ БЫЛО (orchestration):
await self.brain.send_alert({...})
await self.brain.escalate_problem({...})

# ✅ СТАЛО (choreography):
if self.eventbus:
    await self.eventbus.publish(
        'platform.mio.critical_event_gaps_observed',
        {...},
        priority='high'
    )
```

#### 1.3.3 MIO Manager Events Published

**Phase 2.1 (Implemented)**:
```yaml
# Coverage
platform.mio.metrics_coverage_observed          # Every 5 min
platform.mio.service_not_monitored_observed     # When service not in Prometheus
platform.mio.metrics_endpoint_unreachable_observed  # When /metrics unreachable

# Health
platform.mio.metrics_health_observed            # Every 1 min
platform.mio.metrics_health_issue_observed      # When critical health detected

# Lifecycle
platform.mio.service_disconnection_observed     # When service disconnects
platform.mio.service_timeout_observed           # When heartbeat timeout
```

**Phase 2.2 (Future)**:
```yaml
platform.mio.critical_event_gaps_observed
platform.mio.model_accuracy_degraded_observed
platform.mio.stuck_organizations_observed
platform.mio.high_coordination_conflicts_observed
platform.mio.low_expertise_quality_observed
```

---

### 1.4 Brain (AI Event Manager) - Decision Layer

**Расположение**: `/infrastructure/AI-office-infrastructure/ai-event-manager/`
**Порт**: 8043
**Роль**: **Принятие решений на основе observations**

**Функции**:
- Подписка на `platform.mio.*` events
- Анализ observations с помощью AI (Claude/Anthropic)
- Принятие решений (escalate, ignore, delegate)
- Публикация decisions: `platform.brain.decision_made`

**Integration с MIO**:
```python
# Brain подписывается на MIO observations
await eventbus.subscribe(
    'platform.mio.service_not_monitored_observed',
    brain.analyze_monitoring_gap
)

async def analyze_monitoring_gap(event):
    """Brain анализирует observation от MIO"""
    service_name = event['data']['service_name']

    # AI анализ
    decision = await anthropic_client.analyze(
        observation=event,
        context="Service not monitored"
    )

    if decision['action'] == 'auto_fix':
        # Публикуем decision для DevOps Agent
        await eventbus.publish(
            'platform.brain.decision_made',
            {
                'decision': 'add_to_prometheus',
                'service_name': service_name,
                'assigned_to': 'devops-agent'
            }
        )
```

---

### 1.5 DevOps Agent - Action Layer

**Расположение**: `/infrastructure/AI-office-infrastructure/devops-agent/`
**Роль**: **Автоматизация исправлений**

**Функции**:
- Подписка на `platform.brain.decision_made` events
- Автоматическое исправление проблем
- Обновление конфигураций (Prometheus, Docker, etc.)
- Публикация результатов: `platform.devops.action_completed`

**Integration с Brain**:
```python
await eventbus.subscribe(
    'platform.brain.decision_made',
    devops_agent.execute_action
)

async def execute_action(event):
    """DevOps Agent выполняет action из decision"""
    decision = event['data']['decision']

    if decision == 'add_to_prometheus':
        service_name = event['data']['service_name']

        # 1. Получить service info из Service Discovery
        service = await service_discovery.get_service(service_name)

        # 2. Обновить prometheus.yml
        await update_prometheus_config(
            service_name=service_name,
            port=service['port'],
            metrics_endpoint=service['metrics_endpoint']
        )

        # 3. Reload Prometheus
        await reload_prometheus()

        # 4. Публикуем result
        await eventbus.publish(
            'platform.devops.action_completed',
            {
                'action': 'add_to_prometheus',
                'service_name': service_name,
                'status': 'success'
            }
        )
```

---

## 2. Event Flow (Choreography)

### 2.1 Scenario: Новый сервис запущен

```
1. Service starts
   └─► Service registers with Service Discovery
       └─► Service Discovery publishes:
           platform.monitoring.service_registered

2. MIO Manager receives event (EventHandler)
   └─► Checks Prometheus targets
   └─► Service NOT found in Prometheus
   └─► MIO publishes observation:
       platform.mio.service_not_monitored_observed

3. Brain receives observation
   └─► AI analyzes (Claude)
   └─► Decision: "auto_fix - add to Prometheus"
   └─► Brain publishes:
       platform.brain.decision_made

4. DevOps Agent receives decision
   └─► Updates prometheus.yml
   └─► Reloads Prometheus
   └─► DevOps publishes:
       platform.devops.action_completed

5. Analytics Specialist receives all events
   └─► Records to database
   └─► Updates dashboard
```

### 2.2 Scenario: Metrics endpoint недоступен

```
1. MIO Manager observation cycle (every 1 min)
   └─► MetricsHealthChecker checks all Prometheus targets
   └─► Detects: api-gateway endpoint unreachable
   └─► MIO publishes:
       platform.mio.metrics_health_issue_observed
       (severity: critical)

2. Brain receives observation
   └─► AI analyzes
   └─► Decision: "escalate - notify on-call engineer"
   └─► Brain publishes:
       platform.brain.decision_made

3. Notification Service receives decision
   └─► Sends Slack alert to #on-call
   └─► Creates PagerDuty incident
```

---

## 3. Service Catalog Integration

### 3.1 Service Catalog v2.0

**Расположение**: `/infrastructure/runtime/service-catalog/service-catalog.yaml`
**Версия**: 2.0.0
**Сервисов**: 27

**Структура**:
```yaml
metadata:
  platform_name: AI-Platform-ISO
  version: 2.0.0
  total_services: 27
  generated_at: '2025-10-11T02:00:00'

services:
  - name: mio-manager
    type: infrastructure/AI-office-infrastructure
    business_process: "Monitoring & Observability Management"
    port: 8046
    status: active
    path: infrastructure/AI-office-infrastructure/mio-manager

    kpis:
      - request_latency_ms
      - requests_per_second
      - error_rate_percent
      - availability_percent
      - coverage_percentage           # 🆕 MIO-specific
      - alert_response_time           # 🆕 MIO-specific
      - services_monitored            # 🆕 MIO-specific
      - observations_published        # 🆕 MIO-specific

    dependencies:
      - fastapi
      - uvicorn[standard]
      - pydantic
      - redis
      - httpx
      - prometheus-client

    metrics_endpoint: http://localhost:8046/metrics
    health_endpoint: http://localhost:8046/health
```

**Integration Flow**:
```
Service Catalog YAML
       │
       ▼
Service Discovery v2.0
(catalog_integration.py)
       │
       ├─► Loads templates
       ├─► Combines with runtime data
       ├─► Provides unified view
       │
       ▼
MIO Manager
(MetricsCoverageObserver)
       │
       ├─► Gets all services from SD v2
       ├─► Compares with Prometheus
       ├─► Detects missing services
       │
       ▼
EventBus → Brain → DevOps Agent
```

---

## 4. Directories Structure

### 4.1 Правильная структура (после очистки)

```
/infrastructure/
│
├── observability/                  # ✅ ГЛАВНЫЙ каталог
│   ├── monitoring-backend/         # Grafana backend (port 8050)
│   ├── notification-service/       # Notifications
│   ├── exporters/                  # Metrics exporters
│   ├── scripts/                    # Utility scripts
│   ├── prometheus/                 # Prometheus configs
│   └── prometheus-local.yml        # Prometheus config
│
├── monitoring/                     # ❓ ДУБЛИКАТ - нужно проверить
│   ├── grafana/
│   └── prometheus/
│
├── AI-office-infrastructure/
│   ├── mio-manager/                # ✅ MIO Manager (EYES)
│   │   ├── monitoring/             # ✅ Phase 2.1 observers
│   │   ├── intelligence/           # 🔄 Phase 2.2 detectors
│   │   ├── scheduler/              # ✅ SmartScheduler
│   │   └── event_handlers.py       # ✅ SD integration
│   │
│   ├── ai-event-manager/           # ✅ Brain (decisions)
│   │   └── monitoring/             # Infrastructure state
│   │
│   └── devops-agent/               # ✅ Actions
│       └── monitoring/             # Module reports
│
└── runtime/
    ├── service-discovery/          # ✅ SD v2.0 + Catalog
    └── service-catalog/            # ✅ Symlink to archive
```

### 4.2 Что нужно проверить

Давайте проверим содержимое `/infrastructure/monitoring/`:
```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/monitoring/
```

**Возможные сценарии**:
1. **Дубликат** → Удалить/объединить с `/observability/`
2. **Старая версия** → Переместить в `_archive/`
3. **Разные компоненты** → Документировать различия

---

## 5. Next Steps (Рекомендации)

### 5.1 Immediate Actions

1. ✅ **Проверить `/infrastructure/monitoring/` vs `/observability/`**
   - Выяснить различия
   - Удалить дубликаты
   - Создать единую структуру

2. ✅ **Создать architecture diagram**
   - Mermaid диаграмма
   - Component interaction
   - Event flows

3. ✅ **Документировать все MIO events**
   - Complete event catalog
   - Event schemas
   - Event consumers

### 5.2 Phase 2.2 (Intelligence Layer)

Реализовать остальные MIO intelligence modules:
- EventGapDetector
- MLModelPerformanceMonitor
- StuckOrganizationDetector
- CoordinationConflictDetector
- ExpertiseQualityMonitor

### 5.3 Auto-Configuration

Реализовать автоматическое добавление сервисов в Prometheus:
- DevOps Agent слушает `platform.brain.decision_made`
- Автоматически обновляет `prometheus.yml`
- Reload Prometheus через HTTP API

---

## 6. Summary

### Компоненты системы мониторинга:

| Компонент | Порт | Роль | Status |
|-----------|------|------|--------|
| **Prometheus** | 9090 | Metrics storage + scraper | ✅ Production |
| **Service Discovery v2.0** | 8500 | Catalog + Registry + Events | ✅ Production |
| **MIO Manager (EYES)** | 8046 | Observatory + Observations | ✅ Phase 2.1 Complete |
| **Brain (AI Event Manager)** | 8043 | Decision making | ✅ Integrated |
| **DevOps Agent** | - | Auto-fixes | 🔄 Integration ready |
| **Grafana** | 3000 | Visualization | ✅ Production |
| **Monitoring Backend** | 8050 | API + Dashboards | ✅ Production |

### Event Flow:

```
Services → Prometheus ─┐
                        ├─► MIO Manager (EYES) ─► Observations
Services → SD v2.0 ─────┘        │
                                 ▼
                            EventBus
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
                  Brain      Analytics    DevOps
              (Decisions)   (Analysis)   (Actions)
```

### Phase Status:

- ✅ **Phase 1**: Basic monitoring (Prometheus + Grafana)
- ✅ **Phase 2.1**: MIO EYES (Coverage + Health observers)
- 🔄 **Phase 2.2**: MIO Intelligence (Event gaps, ML performance, etc.)
- 🔄 **Phase 3**: Full automation (DevOps Agent auto-fixes)

---

**Last Updated**: October 11, 2025
**Architecture Status**: ✅ Complete and documented
**Next Review**: After `/infrastructure/monitoring/` analysis
