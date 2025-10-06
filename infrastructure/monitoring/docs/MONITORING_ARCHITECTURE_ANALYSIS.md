# 🏗️ Monitoring Architecture - Deep Analysis & Professional Specification

**Date:** 2025-10-03
**Analysis Type:** Code-First (не Docker-First)
**Status:** COMPREHENSIVE AUDIT

---

## 🎯 Правильный Подход: Анализ КОДА, а не Docker

### ❌ Ошибочный подход:
- Смотреть на docker-compose.yml (может быть устаревшим)
- Смотреть на Dockerfile (может не соответствовать коду)
- Предполагать что "если есть файл, значит используется"

### ✅ Правильный подход:
- Анализировать **реальный код сервисов** (`main.py`)
- Смотреть **что импортируют** сервисы
- Проверять **что реально работает** в runtime
- Строить архитектуру **от потребностей кода**

---

## 📊 Part 1: Реальное Состояние Кода (Code Reality)

### 1.1 Что РЕАЛЬНО Импортируют Сервисы

**Анализ всех `main.py` файлов:**

| Service | prometheus_client | shared.monitoring | Both | None |
|---------|------------------|-------------------|------|------|
| bia-service | ✅ make_asgi_app | ❌ | ❌ | ❌ |
| compliance-service | ✅ make_asgi_app | ❌ | ❌ | ❌ |
| documents-service | ✅ make_asgi_app + Counter/Histogram/Gauge | ❌ | ❌ | ❌ |
| planning_service | ✅ make_asgi_app | ❌ | ❌ | ❌ |
| plans_service | ✅ make_asgi_app | ❌ | ❌ | ❌ |
| risk-service | ✅ make_asgi_app | ❌ | ❌ | ❌ |
| response-service | ✅ make_asgi_app | ❌ | ❌ | ❌ |
| **governance-service** | ✅ make_asgi_app | ✅ PrometheusMiddleware | **✅ ДВА PATTERN** | ❌ |
| **learning-service** | ✅ make_asgi_app | ✅ PrometheusMiddleware | **✅ ДВА PATTERN** | ❌ |
| **portal** | ✅ make_asgi_app + Counter/Histogram | ✅ PrometheusMiddleware | **✅ ДВА PATTERN** | ❌ |
| **marketplace** | ✅ make_asgi_app + Counter/Histogram | ✅ PrometheusMiddleware | **✅ ДВА PATTERN** | ❌ |
| validation-service | ❌ | ❌ | ❌ | **✅ НЕТ МОНИТОРИНГА** |

### 1.2 Критическая Находка: СМЕШАННЫЕ PATTERN!

**Проблема:** 4 сервиса (governance, learning, portal, marketplace) используют **ОБА pattern одновременно**:

```python
# Pattern A - shared.monitoring
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint
app.add_middleware(PrometheusMiddleware, service_name="service-name")

# Pattern B - prometheus_client (в ТОМ ЖЕ ФАЙЛЕ!)
from prometheus_client import make_asgi_app
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Это ПРОБЛЕМА потому что:**
1. ❌ Дублирование метрик
2. ❌ Конфликт на `/metrics` endpoint
3. ❌ Неопределенность - какие метрики реально собираются?
4. ❌ Путаница для разработчиков

---

## 🗂️ Part 2: Структура Monitoring Директорий (По НАЗНАЧЕНИЮ)

### 2.1 `/infrastructure/monitoring/` - Centralized Monitoring Service

**Тип:** FastAPI Standalone Service (Port 8045)
**Назначение:** Централизованный сервис для агрегации логов/метрик/алертов

**Содержимое:**
```
/infrastructure/monitoring/
├── main.py (729 lines, 26KB)          # FastAPI service
├── prometheus_integration.py (13KB)   # Prometheus scraper
├── Dockerfile                          # Container build
├── requirements.txt                    # Dependencies
├── dashboards/
│   └── workflow-intelligence.json      # Grafana dashboard
└── prometheus/
    └── rules/
        └── workflow-intelligence.yml   # Alert rules
```

**Функциональность (из кода):**
- ✅ Health checks (автоматически каждые 30s)
- ✅ Log aggregation (10,000 entries in-memory)
- ✅ Metrics collection (24h retention)
- ✅ Alert system (critical/high/medium severity)
- ✅ WebSocket real-time streaming (`/ws/realtime`)
- ✅ HTML dashboard (`/dashboard`)
- ✅ REST API для логов/метрик/алертов

**Monitored Services (из main.py:51-136):**
- intelligent_gateway (8000)
- eventbus (8001)
- ai_orchestration (8002)
- bpmn_workflow (8003)
- coordination_center (8004)
- project_intelligence (8025)
- ai_intelligence (8032)
- notification_service (8035)
- process_mining (8040)
- **planning_service (8011)** ✅
- **plans_service (8023)** ✅
- **bia_service (8012)** ✅
- **compliance_service (8014)** ✅

**Отсутствуют:**
- ❌ learning-service (8021)
- ❌ governance-service (8022)
- ❌ community-portal (8031)
- ❌ community-marketplace (8032)
- ❌ risk-service (8040) - конфликт с process_mining
- ❌ response-service (8041)
- ❌ validation-service (8022) - конфликт с governance
- ❌ documents-service (8024)

**Storage:** In-memory (данные теряются при рестарте)

**Когда использовать:**
- ✅ Development/debugging
- ✅ Real-time monitoring dashboard
- ✅ Quick health overview
- ❌ Production long-term storage (используй observability)

---

### 2.2 `/infrastructure/monitoring-service/` - УСТАРЕВШАЯ ВЕРСИЯ

**Тип:** Old version of monitoring service
**Статус:** ❌ **DUPLICATE - УДАЛИТЬ**

**Доказательства:**
- `main.py`: 666 lines (Oct 2) vs 729 lines (Oct 3) в `/monitoring/`
- Отсутствует `prometheus_integration.py` module
- Отсутствует Dockerfile
- Отсутствуют dashboards и alert rules
- Не содержит 4 BCM сервисов (planning, plans, bia, compliance)

**Вывод:** Это старая версия, полностью вытесненная `/infrastructure/monitoring/`

---

### 2.3 `/infrastructure/observability/` - Production Observability Stack

**Тип:** Docker Compose Stack (Prometheus/Grafana/Loki/Tempo/Exporters)
**Назначение:** Production-grade долгосрочный мониторинг/логирование/трейсинг

**Содержимое:**
```
/infrastructure/observability/
├── docker-compose.monitoring.yml (275 lines) # Full stack
├── prometheus.yml (37 lines)                  # OLD CONFIG (только 4 сервиса!)
├── prometheus/                                # Prometheus configs
├── grafana/                                   # Dashboards + provisioning
├── loki/                                      # Log aggregation
└── config/
    ├── prometheus/                            # Rules, alerts
    ├── grafana/                               # Provisioning configs
    ├── loki/                                  # Loki config
    ├── promtail/                              # Log collection
    ├── alertmanager/                          # Alert routing
    └── blackbox/                              # Endpoint monitoring
```

**Docker Services (11 containers):**
1. **prometheus** (9090) - Metrics storage & PromQL queries
2. **grafana** (3000) - Dashboards & visualization
3. **grafana-postgres** (5432) - Grafana metadata storage
4. **alertmanager** (9093) - Alert routing & notifications
5. **node-exporter** (9100) - System metrics (CPU, mem, disk)
6. **cadvisor** (8080) - Container metrics
7. **blackbox-exporter** (9115) - Endpoint probing
8. **postgres-exporter** (9187) - PostgreSQL metrics
9. **redis-exporter** (9121) - Redis cache metrics
10. **loki** (3100) - Log aggregation
11. **promtail** - Log collection from files & containers

**prometheus.yml проблема:**
```yaml
# ❌ УСТАРЕЛО - только 4 сервиса!
scrape_configs:
  - job_name: 'eventbus'
    targets: ['eventbus:3001']    # ❌ WRONG PORT (should be 8001)

  - job_name: 'ai_orchestrator'
    targets: ['ai_orchestrator:8000']

  - job_name: 'postgres'
    targets: ['postgres-exporter:9187']

  - job_name: 'odoo'
    targets: ['odoo:8069']
```

**Отсутствуют все BCM сервисы:**
- ❌ planning, plans, bia, compliance
- ❌ learning, governance
- ❌ community-portal, community-marketplace
- ❌ risk, response, validation, documents

**Вывод:** Docker stack ГОТОВ, но `prometheus.yml` полностью УСТАРЕЛ

---

### 2.4 `/platform-services/monitoring/` - Service-Level Prometheus Config

**Тип:** Prometheus scrape configuration
**Назначение:** Актуальная конфигурация для scraping метрик с сервисов

**Содержимое:**
```
/platform-services/monitoring/
├── prometheus.yml (191 lines) # ✅ САМЫЙ ПОЛНЫЙ!
└── grafana/
    ├── bcm-services-overview.json
    ├── bcm-platform-unified.json
    └── dashboard.yml
```

**prometheus.yml - САМАЯ ПОЛНАЯ КОНФИГУРАЦИЯ (14 сервисов):**
```yaml
scrape_configs:
  - job_name: 'prometheus' (9090)
  - job_name: 'planning-service' (8011) ✅ ISO 8.3
  - job_name: 'plans-service' (8023) ✅ ISO 8.4
  - job_name: 'bia-service' (8012) ✅ ISO 8.2.2
  - job_name: 'compliance-service' (8014) ✅ ISO 9.2, 10.1, 10.2
  - job_name: 'monitoring-service' (8045) ✅ Observability
  - job_name: 'eventbus' (8001) ✅ Messaging
  - job_name: 'learning-service' (8021) ✅ ISO 7.2
  - job_name: 'governance-service' (8022) ✅ ISO 5.3, 7.1, 7.3
  - job_name: 'community-portal' (8023) ✅ ISO 7.4
  - job_name: 'community-marketplace' (8024) ✅ ISO 7.1
```

**Отсутствуют (4 сервиса):**
- ❌ risk-service (8040)
- ❌ response-service (8041)
- ❌ validation-service (8022) - port conflict!
- ❌ documents-service (8024)

**Вывод:** Это ГЛАВНАЯ конфигурация для Prometheus scraping

---

## 🔍 Part 3: Назначение Каждого Компонента

### 3.1 Два РАЗНЫХ Типа Мониторинга

#### Type A: Service-Level Metrics (внутри каждого сервиса)

**Что:** Prometheus endpoint `/metrics` в каждом микросервисе
**Зачем:** Экспортировать метрики для scraping Prometheus

**Реализация (2 pattern):**

**Pattern 1 - prometheus_client (7 сервисов):**
```python
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Используют:** bia, compliance, documents, planning, plans, risk, response

**Pattern 2 - shared.monitoring (0 сервисов ЧИСТО):**
```python
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

app.add_middleware(PrometheusMiddleware, service_name="service-name")

@app.get("/metrics")
async def metrics():
    return get_metrics_endpoint()()
```

**Используют:** НИКТО чисто! (но 4 сервиса используют оба pattern)

**Pattern 3 - MIXED (4 сервиса - ПРОБЛЕМА!):**
```python
# Оба импорта одновременно
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint
from prometheus_client import make_asgi_app

app.add_middleware(PrometheusMiddleware, ...)  # Middleware
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)             # Mount ASGI app
```

**Используют:** governance, learning, portal, marketplace

---

#### Type B: Centralized Monitoring Service (Port 8045)

**Что:** Standalone FastAPI сервис (`/infrastructure/monitoring/`)
**Зачем:** Агрегация логов/метрик/алертов от всех сервисов

**Функции:**
1. **Health checks** - Опрашивает `/health` endpoint всех сервисов каждые 30s
2. **Log aggregation** - REST API для push логов: `POST /logs`
3. **Metrics collection** - REST API для push метрик: `POST /metrics`
4. **Alert management** - Автоматические алерты при сбоях
5. **Real-time streaming** - WebSocket `/ws/realtime`
6. **Dashboard** - HTML UI на `/dashboard`

**Storage:** In-memory (10k logs, 24h metrics)

**Взаимодействие с сервисами:**
```python
# Сервисы должны PUSH логи/метрики
import httpx

await httpx.post("http://monitoring-service:8045/logs", json={
    "service": "learning-service",
    "level": "ERROR",
    "message": "Something failed"
})
```

**Проблема:** Сервисы **НЕ** используют этот API! Нет push логов/метрик в код.

---

#### Type C: Observability Stack (Prometheus/Grafana/Loki)

**Что:** Docker compose stack с 11 контейнерами
**Зачем:** Production-grade сбор/хранение/визуализация метрик/логов

**Компоненты:**
- **Prometheus** - PULL метрики с `/metrics` endpoints сервисов (scraping)
- **Grafana** - Визуализация дашбордов
- **Loki** - Агрегация логов (альтернатива push-based)
- **Alertmanager** - Уведомления по алертам
- **Exporters** - Метрики инфраструктуры (postgres, redis, node, containers)

**Взаимодействие с сервисами:**
```yaml
# Prometheus scrapes /metrics endpoints
scrape_configs:
  - job_name: 'learning-service'
    targets: ['learning-service:8021']
    metrics_path: '/metrics'
```

**Проблема:** `prometheus.yml` устарел - отсутствуют BCM сервисы

---

## 🎯 Part 4: Реальные Потребности Сервисов

### 4.1 Что НУЖНО Сервисам?

**Минимальный набор (Production-ready):**

1. **Prometheus `/metrics` endpoint** - для scraping метрик Prometheus
2. **Health endpoint** `/health` - для health checks
3. **Structured logging** - JSON logs в stdout (для Loki/Promtail)

**Опциональные (Nice to have):**

4. **Business metrics** - Кастомные метрики (enrollments, certifications, etc.)
5. **EventBus metrics** - Метрики обработки событий
6. **Database metrics** - Query performance tracking

### 4.2 Что НЕ НУЖНО Сервисам?

❌ **Push логов в monitoring-service:8045** - устаревший подход
❌ **Два Prometheus pattern одновременно** - конфликт
❌ **Дубликаты метрик** - путаница

---

## 🏗️ Part 5: Профессиональная Архитектура (Specification)

### 5.1 Рекомендуемая Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                   BCM PLATFORM SERVICES                          │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐          │
│  │Learning  │ │Governance│ │Community │ │ Planning/ │ ...      │
│  │  :8021   │ │  :8022   │ │:8031/8032│ │  Plans/BIA│          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘          │
│       │            │            │             │                 │
│       ├─ /metrics (Prometheus format)                           │
│       ├─ /health (Health check)                                 │
│       └─ stdout logs (JSON format) ──────────────┐             │
└──────────────────────────────────────────────────│──────────────┘
                                                    │
        ┌───────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│            OBSERVABILITY STACK (Production)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Prometheus (9090) - PULL /metrics                       │   │
│  │  - Scrapes /metrics every 15s                            │   │
│  │  - Stores time-series data (30 days retention)           │   │
│  │  - Evaluates alert rules                                 │   │
│  │  - Config: /platform-services/monitoring/prometheus.yml  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Promtail + Loki (3100) - PULL stdout logs              │   │
│  │  - Collects logs from Docker containers                  │   │
│  │  - Stores in Loki                                        │   │
│  │  - Queryable via LogQL                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Grafana (3000) - Visualization                          │   │
│  │  - Dashboards for metrics (Prometheus datasource)        │   │
│  │  - Dashboards for logs (Loki datasource)                 │   │
│  │  - Dashboards for traces (Tempo datasource)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Exporters - Infrastructure Metrics                      │   │
│  │  - node-exporter (9100) - System metrics                 │   │
│  │  - postgres-exporter (9187) - Database metrics           │   │
│  │  - redis-exporter (9121) - Cache metrics                 │   │
│  │  - cadvisor (8080) - Container metrics                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Alertmanager (9093) - Alert Routing                     │   │
│  │  - Receives alerts from Prometheus                        │   │
│  │  - Routes to email/Slack/PagerDuty                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│   MONITORING SERVICE (Optional - Dev/Debug)                       │
│   Port: 8045 (/infrastructure/monitoring/)                        │
│   - Real-time dashboard                                          │
│   - WebSocket streaming                                          │
│   - In-memory logs/metrics (24h)                                 │
│   - Not for production long-term storage                         │
└──────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Роли Компонентов

| Компонент | Роль | Когда использовать |
|-----------|------|-------------------|
| **Service `/metrics`** | Экспорт метрик | ВСЕГДА (все сервисы) |
| **Service `/health`** | Health checks | ВСЕГДА (все сервисы) |
| **Service logs → stdout** | Логирование | ВСЕГДА (JSON format) |
| **Prometheus** | Scrape & store metrics | Production |
| **Grafana** | Визуализация | Production |
| **Loki + Promtail** | Log aggregation | Production |
| **Exporters** | Infrastructure metrics | Production |
| **Alertmanager** | Alert routing | Production |
| **Monitoring Service:8045** | Dev dashboard | Development only |

---

## 🔧 Part 6: Проблемы и Решения

### Проблема 1: Смешанные Prometheus Patterns

**Сервисы:** governance, learning, portal, marketplace

**Проблема:**
```python
# Оба pattern одновременно!
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint
from prometheus_client import make_asgi_app

app.add_middleware(PrometheusMiddleware, service_name="learning-service")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Последствия:**
- ❌ Конфликт на `/metrics` endpoint (кто отвечает?)
- ❌ Дублирование метрик
- ❌ Неопределенность какие метрики собираются

**Решение: Выбрать ОДИН pattern**

**Option A: Только prometheus_client (рекомендуется для совместимости)**
```python
from prometheus_client import make_asgi_app

# Remove PrometheusMiddleware

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Плюсы:**
- ✅ Стандартный Prometheus client
- ✅ Совместимость с другими 7 сервисами
- ✅ Полный контроль над метриками

**Минусы:**
- ❌ Нет автоматического HTTP request tracking
- ❌ Надо вручную инструментировать код

**Option B: Только shared.monitoring (если добавить функциональность)**
```python
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

app.add_middleware(PrometheusMiddleware, service_name="learning-service")

@app.get("/metrics")
async def metrics():
    return get_metrics_endpoint()()

# Remove prometheus_client
```

**Плюсы:**
- ✅ Автоматический HTTP request tracking
- ✅ Business metrics helpers
- ✅ EventBus metrics integration

**Минусы:**
- ❌ Нужно мигрировать другие 7 сервисов
- ❌ Кастомная реализация (не стандартная)

**Рекомендация:** **Option A** - использовать `prometheus_client` везде

---

### Проблема 2: Port Conflicts

**Конфликты:**
- governance-service (8022) vs validation-service (8022) ❌
- plans-service (8023) vs community-portal (8023) ❌
- documents-service (8024) vs community-marketplace (8024) ❌
- risk-service (8040) vs process-mining (8040) ❌

**Решение:**
```python
# Reassign ports
validation-service: 8022 → 8025
community-portal: 8023 → 8031 (уже изменено)
community-marketplace: 8024 → 8032 (уже изменено)
# risk-service and process-mining need resolution
```

---

### Проблема 3: Устаревшая Конфигурация Observability

**Файл:** `/infrastructure/observability/prometheus.yml`

**Проблема:** Только 4 сервиса, неправильные порты

**Решение:** Заменить на `/platform-services/monitoring/prometheus.yml`
```bash
cp /Users/MD/AI-Platform-ISO/platform-services/monitoring/prometheus.yml \
   /Users/MD/AI-Platform-ISO/infrastructure/observability/config/prometheus/prometheus.yml
```

---

### Проблема 4: Monitoring Service Не Используется

**Сервис:** `/infrastructure/monitoring/main.py` (Port 8045)

**Проблема:** Сервисы НЕ push логи/метрики через API

**Доказательство:** Ни один `main.py` не содержит:
```python
httpx.post("http://monitoring-service:8045/logs", ...)
```

**Решение:**

**Option A:** Добавить push логов в сервисы (не рекомендуется)
**Option B:** Использовать ТОЛЬКО для dev/debug dashboard (рекомендуется)
**Option C:** Удалить (если не нужно)

**Рекомендация:** **Option B** - оставить для development, не для production

---

### Проблема 5: Duplicate `/infrastructure/monitoring-service/`

**Решение:** Удалить полностью
```bash
rm -rf /Users/MD/AI-Platform-ISO/infrastructure/monitoring-service/
```

---

## 📋 Part 7: Комплексное ТЗ (Technical Specification)

### 7.1 Цель

Построить **единую, согласованную, профессиональную** систему мониторинга для BCM Platform, основанную на industry best practices (Prometheus/Grafana/Loki).

---

### 7.2 Требования

#### R1: Service-Level Metrics (ОБЯЗАТЕЛЬНО для всех сервисов)

**Каждый сервис ДОЛЖЕН:**

1. **Экспортировать Prometheus метрики** на `/metrics`
   - Format: Prometheus exposition format
   - Implementation: `prometheus_client.make_asgi_app()`
   - Metrics: default Python metrics + custom business metrics

2. **Иметь health endpoint** на `/health`
   - Return: JSON `{"status": "healthy", "service": "name", "version": "1.0", "components": {...}}`
   - Status codes: 200 (healthy), 503 (unhealthy)

3. **Логировать в stdout** в JSON format
   - Format: `{"timestamp": "...", "level": "INFO", "service": "...", "message": "...", "context": {...}}`
   - Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Library: Python `logging` module

**Стандартный pattern (для ВСЕХ сервисов):**
```python
# main.py
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge
import logging
import json

# Setup JSON logging
logging.basicConfig(
    format='%(message)s',  # JSON serialized below
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Custom metrics
requests_total = Counter(
    'service_requests_total',
    'Total requests',
    ['endpoint', 'method', 'status']
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "service-name",
        "version": "1.0.0",
        "components": {
            "database": "connected",
            "eventbus": "connected"
        }
    }

# JSON logging
logger.info(json.dumps({
    "timestamp": datetime.utcnow().isoformat(),
    "level": "INFO",
    "service": "service-name",
    "message": "Service started",
    "context": {"port": 8021}
}))
```

---

#### R2: Centralized Scraping (Prometheus)

**Prometheus ДОЛЖЕН:**

1. **Scrape `/metrics`** from all services every 15s
2. **Store time-series data** with 30 days retention
3. **Evaluate alert rules** for SLOs (latency, error rate, uptime)
4. **Use config:** `/platform-services/monitoring/prometheus.yml` (MASTER CONFIG)

**Все сервисы в config:**
- ✅ planning (8011), plans (8023), bia (8012), compliance (8014)
- ✅ learning (8021), governance (8022)
- ✅ community-portal (8031), community-marketplace (8032)
- ⚠️ risk (8040 → reassign port), response (8041)
- ⚠️ validation (8022 → reassign to 8025), documents (8024 → reassign port)

---

#### R3: Visualization (Grafana)

**Grafana ДОЛЖЕН:**

1. **Connect to Prometheus** as datasource
2. **Connect to Loki** as datasource
3. **Provision dashboards:**
   - BCM Services Overview (all services status, request rates, errors)
   - Per-Service Performance (latency, throughput, error rate)
   - Business KPIs (enrollments, certifications, policies, etc.)
   - Infrastructure (database, redis, system resources)

**Dashboard sources:**
- `/platform-services/monitoring/grafana/`
- `/infrastructure/observability/config/grafana/dashboards/`

---

#### R4: Log Aggregation (Loki + Promtail)

**Loki ДОЛЖЕН:**

1. **Collect logs** from Docker container stdout via Promtail
2. **Store logs** with 14 days retention
3. **Queryable via LogQL** in Grafana

**Promtail ДОЛЖЕН:**
1. **Tail logs** from `/var/lib/docker/containers`
2. **Parse JSON logs** and extract labels (service, level, etc.)
3. **Push to Loki** on port 3100

---

#### R5: Alerting (Alertmanager)

**Alertmanager ДОЛЖЕН:**

1. **Receive alerts** from Prometheus
2. **Route alerts** based on severity:
   - Critical → PagerDuty + Email + Slack
   - High → Email + Slack
   - Medium → Slack

**Alert rules:**
- Service Down (up == 0 for 1m)
- High Error Rate (error_rate > 5% for 5m)
- High Latency (p95 latency > 1s for 5m)
- Low Disk Space (disk_usage > 90%)

---

#### R6: Infrastructure Metrics (Exporters)

**Exporters ДОЛЖНЫ работать:**

1. **node-exporter** (9100) - CPU, memory, disk, network
2. **postgres-exporter** (9187) - Database connections, queries, locks
3. **redis-exporter** (9121) - Cache hit rate, memory usage
4. **cadvisor** (8080) - Container CPU, memory, network

---

### 7.3 Что УДАЛИТЬ

1. ❌ `/infrastructure/monitoring-service/` - полностью удалить (дубликат)
2. ❌ `shared.monitoring.PrometheusMiddleware` usage - заменить на `prometheus_client`
3. ❌ Устаревший `/infrastructure/observability/prometheus.yml` - заменить

---

### 7.4 Что ОСТАВИТЬ

1. ✅ `/infrastructure/monitoring/` - для dev dashboard (опционально)
2. ✅ `/infrastructure/observability/` - Docker stack (ОБНОВИТЬ configs)
3. ✅ `/platform-services/monitoring/prometheus.yml` - MASTER CONFIG

---

### 7.5 Что ОБНОВИТЬ

1. ⚠️ **Все сервисы с mixed patterns** (governance, learning, portal, marketplace)
   - Удалить `shared.monitoring` imports
   - Оставить только `prometheus_client.make_asgi_app()`

2. ⚠️ **Сервисы без мониторинга** (validation)
   - Добавить `prometheus_client.make_asgi_app()`
   - Добавить `/health` endpoint

3. ⚠️ **Port conflicts**
   - validation: 8022 → 8025
   - documents: 8024 → reassign
   - risk: 8040 → reassign

4. ⚠️ **Observability configs:**
   - Replace `/infrastructure/observability/prometheus.yml` with updated version
   - Update Grafana dashboards with new services

5. ⚠️ **Monitoring service:8045**
   - Update MONITORED_SERVICES list with all current services
   - Document as "development only"

---

## 🚀 Part 8: Implementation Plan

### Phase 1: Cleanup (30 minutes)

**Priority: CRITICAL**

1. **Delete duplicate directory**
   ```bash
   rm -rf /Users/MD/AI-Platform-ISO/infrastructure/monitoring-service/
   ```

2. **Fix mixed Prometheus patterns** (4 сервиса)
   - governance-service
   - learning-service
   - portal
   - marketplace

   **For each:**
   ```python
   # REMOVE:
   from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint
   app.add_middleware(PrometheusMiddleware, ...)

   # KEEP:
   from prometheus_client import make_asgi_app
   metrics_app = make_asgi_app()
   app.mount("/metrics", metrics_app)
   ```

3. **Fix port conflicts**
   ```python
   # validation-service/config.py
   SERVICE_PORT = 8025  # was 8022
   ```

---

### Phase 2: Add Missing Metrics (20 minutes)

**Priority: HIGH**

1. **validation-service** - add Prometheus
   ```python
   from prometheus_client import make_asgi_app

   metrics_app = make_asgi_app()
   app.mount("/metrics", metrics_app)
   ```

---

### Phase 3: Update Configs (15 minutes)

**Priority: HIGH**

1. **Update Observability Prometheus config**
   ```bash
   cp /Users/MD/AI-Platform-ISO/platform-services/monitoring/prometheus.yml \
      /Users/MD/AI-Platform-ISO/infrastructure/observability/config/prometheus/prometheus.yml
   ```

2. **Update Monitoring Service list**
   - Add: learning (8021), governance (8022), portal (8031), marketplace (8032)
   - Add: risk (reassign port), response (8041), validation (8025), documents (reassign)

3. **Update platform-services prometheus.yml**
   - Add: risk-service (new port)
   - Add: response-service (8041)
   - Add: validation-service (8025)
   - Add: documents-service (new port)

---

### Phase 4: Test & Verify (30 minutes)

**Priority: MEDIUM**

1. **Start Prometheus**
   ```bash
   cd /Users/MD/AI-Platform-ISO/infrastructure/observability
   docker-compose -f docker-compose.monitoring.yml up -d prometheus
   ```

2. **Verify all `/metrics` endpoints**
   ```bash
   curl http://localhost:8021/metrics  # learning
   curl http://localhost:8022/metrics  # governance
   # ... etc
   ```

3. **Check Prometheus targets**
   - Open http://localhost:9090/targets
   - All services should be UP

4. **Start Grafana & verify dashboards**
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d grafana
   ```
   - Open http://localhost:3000
   - Login: admin/admin123
   - Verify dashboards load with data

---

### Phase 5: Documentation (15 minutes)

**Priority: LOW**

1. **Create MONITORING.md** - single source of truth
2. **Update README files** in monitoring directories
3. **Document port allocations** and resolution of conflicts

---

## ✅ Success Criteria

1. ✅ **All services** have `/metrics` endpoint (12/12)
2. ✅ **All services** have `/health` endpoint (12/12)
3. ✅ **One Prometheus pattern** (no mixed implementations)
4. ✅ **No port conflicts** (all unique ports)
5. ✅ **Prometheus scrapes** all services successfully
6. ✅ **Grafana dashboards** show data from all services
7. ✅ **No duplicate directories** (monitoring-service deleted)
8. ✅ **Configs synchronized** (observability = platform-services)

---

**Version:** 1.0
**Status:** READY TO IMPLEMENT
**Estimated Time:** 2 hours total
