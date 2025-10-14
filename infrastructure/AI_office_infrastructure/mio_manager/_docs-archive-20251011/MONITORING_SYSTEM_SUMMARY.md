# Monitoring System - Complete Summary

**Date**: October 11, 2025
**Version**: 2.0 (MIO EYES Phase 2.1 Complete)

## Ответы на ваши вопросы

### Вопрос 1: Показать организованную систему мониторинга

✅ **Система мониторинга полностью организована и задокументирована**

#### Документация создана:

1. **MONITORING_SYSTEM_ARCHITECTURE.md** (этот каталог)
   - Полная архитектура
   - Все компоненты и их роли
   - API endpoints
   - Event flows
   - Technology stack

2. **MONITORING_ARCHITECTURE_DIAGRAM.md** (этот каталог)
   - Mermaid диаграммы
   - Sequence diagrams
   - Component interaction matrix
   - Configuration examples

3. **MONITORING_CLEANUP_PLAN.md** (`/infrastructure/`)
   - Обнаруженные дубликаты
   - План очистки
   - Миграция конфигураций

---

### Вопрос 2: Проблемы с компонентами - старая версия или дубликаты?

✅ **Обнаружена проблема: дублирование каталогов**

#### Найденные дубликаты:

```
/infrastructure/observability/     # ✅ АКТУАЛЬНАЯ - полная система
/infrastructure/monitoring/        # ❌ СТАРАЯ ВЕРСИЯ - дубликат
```

#### Статус компонентов:

| Компонент | Статус | Расположение | Комментарий |
|-----------|--------|--------------|-------------|
| **Prometheus** | ✅ OK | `/observability/prometheus/` | Актуальная конфигурация |
| **Prometheus OLD** | ❌ Дубликат | `/monitoring/prometheus/` | Старая версия, нужно удалить |
| **Service Discovery v2** | ✅ OK | `/runtime/service-discovery/` | Production ready |
| **MIO Manager (EYES)** | ✅ OK | `/AI-office-infrastructure/mio-manager/` | Phase 2.1 complete |
| **Monitoring Backend** | ✅ OK | `/observability/monitoring-backend/` | FastAPI backend |
| **Grafana** | ✅ OK | `/observability/grafana/` | Visualization |

#### Различия между версиями:

**`/observability/prometheus/prometheus.yml`** (NEWER):
- Использует Docker service names
- Интегрирован с EventBus, Service Discovery
- Современная структура

**`/monitoring/prometheus/prometheus.yml`** (OLDER):
- Использует localhost:ports
- Старые сервисы (orchestrator без event manager)
- Устаревшая структура

**Рекомендация**: Удалить `/infrastructure/monitoring/` и заархивировать

---

## Архитектура системы мониторинга (визуализация)

### Компоненты и их роли

```
┌─────────────────────────────────────────────────────────┐
│                 OBSERVABILITY STACK                     │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │Prometheus│◄──│ Service  │◄──│ Services │           │
│  │  :9090   │   │Discovery │   │ (27)     │           │
│  └────┬─────┘   │  :8500   │   └──────────┘           │
│       │         └─────┬────┘                            │
│       │scrape         │events                           │
│       ▼               ▼                                 │
│  ┌──────────────────────────────┐                      │
│  │  MIO Manager (EYES)          │                      │
│  │  Port: 8046                  │                      │
│  │  ─────────────────           │                      │
│  │  Phase 2.1 (READY):          │                      │
│  │  • MetricsCoverageObserver   │                      │
│  │  • MetricsHealthChecker      │                      │
│  │  • Event Handlers (SD v2)    │                      │
│  │                               │                      │
│  │  Phase 2.2 (FUTURE):         │                      │
│  │  • EventGapDetector          │                      │
│  │  • MLModelPerformanceMonitor │                      │
│  │  • StuckOrganizationDetector │                      │
│  │  ... и другие                │                      │
│  └───────────┬──────────────────┘                      │
│              │observations                              │
│              ▼                                          │
│  ┌──────────────────────────────┐                      │
│  │       EventBus               │                      │
│  │  platform.monitoring.*       │                      │
│  │  platform.mio.*              │                      │
│  └────────┬─────────────────────┘                      │
│           │                                             │
│  ┌────────┴─────────────────────────────┐              │
│  │  Decision & Action Layer             │              │
│  │  • Brain (AI Event Manager) :8043    │              │
│  │  • DevOps Agent (auto-fixes)         │              │
│  │  • Analytics Specialist :8041        │              │
│  └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### Event Flow Example

```
1. New service starts
   │
   ▼
2. Service registers → Service Discovery v2.0
   │
   ▼
3. SD publishes → EventBus: service_registered
   │
   ▼
4. MIO EYES receives event (EventHandler)
   │
   ├─► Checks Prometheus targets
   ├─► Checks metrics endpoint
   └─► Service NOT monitored?
       │
       ▼
5. MIO publishes → EventBus: service_not_monitored_observed
   │
   ▼
6. Brain receives observation
   │
   ├─► AI analyzes (Claude)
   └─► Decision: "add to Prometheus"
       │
       ▼
7. Brain publishes → EventBus: decision_made
   │
   ▼
8. DevOps Agent receives decision
   │
   ├─► Updates prometheus.yml
   ├─► Reloads Prometheus
   └─► Publishes action_completed
```

---

## Файловая структура (правильная)

### Актуальная структура

```
/infrastructure/
│
├── observability/                           # ✅ MAIN observability directory
│   ├── prometheus/
│   │   ├── prometheus.yml                   # Unified config (all 27 services)
│   │   └── alerts/
│   ├── grafana/
│   ├── monitoring-backend/                  # FastAPI backend (port 8050)
│   ├── notification-service/
│   ├── exporters/
│   └── scripts/
│
├── monitoring/                              # ❌ DELETE - old duplicate
│   └── [to be archived]
│
├── AI-office-infrastructure/
│   ├── mio-manager/                         # ✅ MIO Manager (EYES)
│   │   ├── main.py                          # FastAPI app
│   │   ├── event_handlers.py                # ✅ Phase 2.1 - SD events
│   │   ├── monitoring/                      # ✅ Phase 2.1 observers
│   │   │   ├── metrics_coverage_observer.py # Coverage monitoring
│   │   │   └── metrics_health_checker.py    # Health monitoring
│   │   ├── intelligence/                    # 🔄 Phase 2.2 (future)
│   │   ├── scheduler/
│   │   │   └── smart_scheduler.py           # ✅ EventBus choreography
│   │   └── MONITORING_SYSTEM_ARCHITECTURE.md # 🆕 This documentation
│   │
│   ├── ai-event-manager/                    # ✅ Brain (decisions)
│   ├── devops-agent/                        # ✅ Auto-fixes
│   └── analytics-specialist/                # ✅ Analysis
│
└── runtime/
    ├── service-discovery/                   # ✅ Service Discovery v2.0
    │   ├── catalog_integration.py           # Catalog + Registry
    │   ├── eventbus_integration.py          # Event publishing
    │   ├── service_registry.py
    │   └── health_monitor.py
    └── service-catalog/                     # ✅ Symlink to archive
```

### Что нужно сделать (cleanup)

```bash
# 1. Создать archive
mkdir -p /_archive/monitoring-deprecated-20251011/

# 2. Переместить старую версию
mv /infrastructure/monitoring/ \
   /_archive/monitoring-deprecated-20251011/old-monitoring/

# 3. Проверить, что все работает
curl http://localhost:9090/api/v1/targets
curl http://localhost:8046/api/coverage
```

---

## Компоненты системы (детально)

### 1. Prometheus (Metrics Storage)

**Расположение**: `/infrastructure/observability/prometheus/`
**Порт**: 9090
**Функция**: Time-series database + scraper

**Что делает**:
- Scrapes `/metrics` endpoints всех сервисов каждые 15 секунд
- Хранит временные ряды метрик
- Предоставляет API для запросов (PromQL)
- Генерирует alerts на основе rules

**Интеграция с MIO**:
- MIO читает `/api/v1/targets` для проверки coverage
- MIO проверяет health каждого target
- MIO публикует observations если проблемы

---

### 2. Service Discovery v2.0 (Unified Catalog + Registry)

**Расположение**: `/infrastructure/runtime/service-discovery/`
**Порт**: 8500
**Функция**: Service registry + lifecycle events

**Что делает**:
- Загружает `service-catalog.yaml` (27 сервисов)
- Регистрирует runtime services
- Объединяет catalog (static) + registry (dynamic)
- Публикует lifecycle events в EventBus

**API Endpoints**:
```http
GET /v2/catalog/services    # All services (unified view)
GET /v2/catalog/missing     # In catalog but not running
GET /v2/catalog/unknown     # Running but not in catalog
GET /v2/catalog/stats       # Statistics
```

**Events Published**:
- `platform.monitoring.service_registered`
- `platform.monitoring.service_disconnected`
- `platform.monitoring.critical_timeout`

---

### 3. MIO Manager (EYES / Observatory)

**Расположение**: `/infrastructure/AI-office-infrastructure/mio-manager/`
**Порт**: 8046
**Функция**: **Observatory - только наблюдает, НЕ командует!**

#### Архитектурный принцип: Event-Driven Choreography

- ✅ **Наблюдает** состояния
- ✅ **Проверяет** метрики
- ✅ **Публикует** observations
- ❌ **НЕ принимает** решений
- ❌ **НЕ отдает** команды
- ❌ **НЕ исправляет** проблемы

#### Phase 2.1 Components (IMPLEMENTED)

##### A. MetricsCoverageObserver

**Файл**: `/monitoring/metrics_coverage_observer.py`

**Что делает**:
```python
1. GET /v2/catalog/services from Service Discovery
   → Получает все зарегистрированные сервисы

2. GET /api/v1/targets from Prometheus
   → Получает все мониторимые targets

3. Сравнивает списки:
   • Monitored: В SD + В Prometheus ✅
   • Not Monitored: В SD + НЕТ в Prometheus ⚠️
   • Unknown: НЕТ в SD + В Prometheus ❓

4. Вычисляет coverage:
   coverage_pct = (monitored / total) * 100

5. Публикует observations:
   • platform.mio.metrics_coverage_observed (every 5 min)
   • platform.mio.service_not_monitored_observed (per service)
```

**Cycle**: Каждые 5 минут (SmartScheduler)

##### B. MetricsHealthChecker

**Файл**: `/monitoring/metrics_health_checker.py`

**Что делает**:
```python
1. GET /api/v1/targets from Prometheus

2. Для каждого target проверяет:
   • endpoint_reachable? (health == 'up')
   • last_scrape fresh? (< 120 seconds ago)
   • scrape_error present?
   • scrape_duration OK? (< 5 seconds)

3. Классифицирует:
   • healthy: Всё OK ✅
   • warning: Stale или slow ⚠️
   • critical: Unreachable или error ❌

4. Публикует observations:
   • platform.mio.metrics_health_observed (every 1 min)
   • platform.mio.metrics_health_issue_observed (if critical)
```

**Cycle**: Каждую минуту (SmartScheduler)

##### C. Event Handlers (Service Discovery Integration)

**Файл**: `/event_handlers.py`

**Что делает**:
```python
# Подписки на Service Discovery events
await eventbus.subscribe(
    'platform.monitoring.service_registered',
    handle_service_registered
)

# Обработчик
async def handle_service_registered(event):
    service_name = event['data']['service_name']
    port = event['data']['port']

    # 1. Проверить: мониторится ли Prometheus?
    if not await check_prometheus_monitoring(service_name):
        await publish('platform.mio.service_not_monitored_observed')

    # 2. Проверить: доступен ли /metrics endpoint?
    if not await check_metrics_endpoint(f"http://...:{port}/metrics"):
        await publish('platform.mio.metrics_endpoint_unreachable_observed')
```

**Triggers**: Reactive - при событиях от Service Discovery

##### D. SmartScheduler (Observation Cycles)

**Файл**: `/scheduler/smart_scheduler.py`

**Что делает**:
```python
# Phase 2.1 cycles (READY)
scheduler.add_job(
    _observe_metrics_coverage,
    IntervalTrigger(minutes=5),
    id='observe_metrics_coverage'
)

scheduler.add_job(
    _check_metrics_health,
    IntervalTrigger(minutes=1),
    id='check_metrics_health'
)

# Phase 2.2 cycles (FUTURE)
# Event gaps, ML performance, stuck orgs, conflicts, expertise
```

**Important Fix** ✅:
```python
# ❌ БЫЛО (orchestration - прямые команды):
await self.brain.send_alert({...})
await self.brain.escalate_problem({...})

# ✅ СТАЛО (choreography - публикация events):
if self.eventbus:
    await self.eventbus.publish(
        'platform.mio.critical_event_gaps_observed',
        {...},
        priority='high'
    )
```

#### Events Published by MIO

**Phase 2.1 (Implemented)**:
```yaml
# Coverage observations
platform.mio.metrics_coverage_observed:
  coverage_percentage: 85.5
  monitored_services: 23
  not_monitored_services: 4
  recommendation: "..."

platform.mio.service_not_monitored_observed:
  service_name: "api-gateway"
  port: 8080
  severity: "high"

# Health observations
platform.mio.metrics_health_observed:
  overall_health: "degraded"
  healthy_services: 20
  critical_services: 1
  recommendation: "..."

platform.mio.metrics_health_issue_observed:
  severity: "critical"
  critical_issues: [...]
  recommendation: "..."

# Lifecycle observations
platform.mio.service_disconnection_observed:
  service_name: "..."
  reason: "shutdown"

platform.mio.service_timeout_observed:
  service_name: "..."
  timeout_seconds: 60
```

---

### 4. Brain (AI Event Manager) - Decision Layer

**Расположение**: `/infrastructure/AI-office-infrastructure/ai-event-manager/`
**Порт**: 8043
**Функция**: **Принятие решений на основе AI**

**Что делает**:
- Подписывается на `platform.mio.*` events
- Анализирует observations через Claude AI
- Принимает решения (auto-fix, escalate, ignore)
- Публикует `platform.brain.decision_made`

**Integration Flow**:
```
MIO observation → EventBus → Brain receives
                                  ↓
                             AI analyzes
                                  ↓
                             Makes decision
                                  ↓
                    Publishes decision → EventBus
                                          ↓
                                   DevOps Agent/
                                   Notification Service
```

---

### 5. DevOps Agent - Action Layer

**Расположение**: `/infrastructure/AI-office-infrastructure/devops-agent/`
**Функция**: **Автоматизация исправлений**

**Что делает**:
- Подписывается на `platform.brain.decision_made`
- Выполняет auto-fixes
- Обновляет конфигурации (Prometheus, Docker, etc.)
- Публикует `platform.devops.action_completed`

**Example Actions**:
- Add service to Prometheus
- Restart service
- Update configuration
- Deploy hotfix

---

## Service Catalog Integration

### Service Catalog v2.0

**Файл**: `/infrastructure/runtime/service-catalog/service-catalog.yaml`
**Версия**: 2.0.0
**Сервисов**: 27

**Основные секции**:
```yaml
metadata:
  platform_name: AI-Platform-ISO
  version: 2.0.0
  total_services: 27

services:
  - name: mio-manager
    type: infrastructure/AI-office-infrastructure
    business_process: "Monitoring & Observability Management"
    port: 8046
    kpis:
      - coverage_percentage          # MIO-specific
      - alert_response_time          # MIO-specific
      - services_monitored           # MIO-specific
      - observations_published       # MIO-specific
    metrics_endpoint: http://localhost:8046/metrics
    health_endpoint: http://localhost:8046/health
```

**Документация**:
- `CATALOG_SCHEMA.md` - Official specification (13 sections)
- `QUICK_REFERENCE.md` - Developer quick guide
- `README.md` - Overview and integration

**Integration with MIO**:
```
Service Catalog YAML
       ↓
Service Discovery v2.0 (catalog_integration.py)
       ↓ GET /v2/catalog/services
MIO MetricsCoverageObserver
       ↓ Compare with Prometheus
Observations published → EventBus
```

---

## Verification Steps

### 1. Проверить Service Discovery v2.0

```bash
# All services
curl http://localhost:8500/v2/catalog/services | jq '.services | length'
# Expected: 27

# Missing services
curl http://localhost:8500/v2/catalog/missing | jq '.missing_services'

# Coverage stats
curl http://localhost:8500/v2/catalog/stats | jq '.totals.coverage_percent'
```

### 2. Проверить MIO Manager

```bash
# Coverage observation
curl http://localhost:8046/api/coverage | jq

# Health check
curl http://localhost:8046/health | jq

# Metrics
curl http://localhost:8046/metrics | grep mio_
```

### 3. Проверить Prometheus

```bash
# Targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
# Expected: 27+

# Specific target health
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="mio-manager")'
```

### 4. Проверить EventBus

```bash
# Recent events (если есть API)
curl http://localhost:3001/api/events?channel=platform.mio.* | jq
```

---

## Next Steps

### Immediate (Cleanup)

1. ✅ **Удалить дубликат `/infrastructure/monitoring/`**
   - Выполнить plan из `MONITORING_CLEANUP_PLAN.md`
   - Заархивировать старую версию
   - Обновить все references

2. ✅ **Создать unified Prometheus config**
   - Объединить все 27 сервисов
   - Добавить alert rules
   - Протестировать

### Short-term (Phase 2.2)

3. 🔄 **Implement remaining MIO intelligence modules**
   - EventGapDetector
   - MLModelPerformanceMonitor
   - StuckOrganizationDetector
   - CoordinationConflictDetector
   - ExpertiseQualityMonitor

### Mid-term (Auto-Configuration)

4. 🔄 **DevOps Agent auto-fixes**
   - Auto-add services to Prometheus
   - Auto-restart unhealthy services
   - Auto-update configurations

5. 🔄 **Service Discovery → Prometheus integration**
   - Replace static configs with dynamic discovery
   - Prometheus auto-reload on service changes

---

## Summary

### Что готово ✅

| Component | Status | Phase |
|-----------|--------|-------|
| Service Discovery v2.0 | ✅ Production | Complete |
| Service Catalog v2.0 | ✅ Production | Complete |
| MIO Manager (EYES) | ✅ Phase 2.1 | Coverage + Health |
| Event Handlers | ✅ Ready | SD integration |
| SmartScheduler | ✅ Fixed | Choreography |
| Prometheus | ✅ Running | Manual config |
| EventBus | ✅ Running | Event routing |
| Brain integration | ✅ Ready | Event subscriptions |
| Documentation | ✅ Complete | Architecture + Diagrams |

### Что нужно сделать 🔄

| Task | Priority | Complexity |
|------|----------|------------|
| Cleanup `/infrastructure/monitoring/` | 🔴 High | Low |
| Unified Prometheus config | 🔴 High | Medium |
| Phase 2.2 Intelligence modules | 🟡 Medium | High |
| DevOps Agent auto-fixes | 🟡 Medium | Medium |
| Prometheus auto-configuration | 🟢 Low | High |

### Архитектурные принципы ✅

- ✅ **Event-Driven Choreography** (не orchestration)
- ✅ **Separation of Concerns** (EYES observe, Brain decides, DevOps acts)
- ✅ **Unified View** (Catalog + Registry)
- ✅ **Observable System** (все lifecycle events tracked)
- ✅ **Autonomous Components** (no direct coupling)

---

## Ответ на вопросы (итог)

### 1. Система мониторинга организована?

**✅ ДА**, полностью организована и задокументирована:

- Архитектура описана в `MONITORING_SYSTEM_ARCHITECTURE.md`
- Диаграммы в `MONITORING_ARCHITECTURE_DIAGRAM.md`
- Все компоненты идентифицированы и распределены правильно
- Event flows задокументированы
- Integration points описаны

### 2. Проблемы с компонентами?

**✅ НАЙДЕНА ПРОБЛЕМА**: Дублирование директорий

**Решение**: План очистки в `MONITORING_CLEANUP_PLAN.md`

**Статус компонентов**:
- ✅ `/observability/` - актуальная, полная
- ❌ `/monitoring/` - старая, дубликат → удалить
- ✅ Все основные компоненты правильно распределены

### 3. Это представляет собой систему?

**✅ ДА**, это полноценная **Event-Driven Monitoring System**:

**Компоненты взаимодействуют**:
- Services → Prometheus (metrics)
- Services → Service Discovery (registration)
- Service Discovery → EventBus (lifecycle events)
- MIO → Prometheus + SD (observations)
- MIO → EventBus (observations)
- Brain → EventBus (decisions)
- DevOps Agent → Infrastructure (actions)

**Система автономна**:
- Choreography pattern (не orchestration)
- Каждый компонент независим
- Communication через events
- Decoupled architecture

**Система наблюдаема**:
- Все lifecycle events tracked
- Metrics coverage monitored
- Health continuously checked
- Observations published to EventBus

---

**Conclusion**: Система мониторинга полностью организована, правильно распределена по компонентам, и представляет собой целостную Event-Driven архитектуру. Найден один дубликат, который нужно удалить.

**Last Updated**: October 11, 2025
**Status**: ✅ Documented & Production Ready (Phase 2.1)
