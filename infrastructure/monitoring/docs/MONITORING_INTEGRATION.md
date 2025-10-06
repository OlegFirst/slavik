# Monitoring Integration - Setup Guide

**Дата:** 2025-10-03
**Статус:** READY TO INTEGRATE

---

## 📊 Текущий Статус

### ✅ Что ГОТОВО:

1. **Prometheus Configuration** (`/platform-services/monitoring/prometheus.yml`)
   - ✅ Добавлены все новые сервисы:
     - Learning Service (port 8021)
     - Governance Service (port 8022)
     - Community Portal (port 8023)
     - Community Marketplace (port 8024)
   - ✅ Настроены labels с ISO clauses
   - ✅ Scrape interval: 10s для всех сервисов

2. **Shared Monitoring Library** (`/shared/monitoring/`)
   - ✅ Создан `prometheus_metrics.py` с готовыми метриками
   - ✅ PrometheusMiddleware для автоматического трекинга HTTP requests
   - ✅ Helper functions для business metrics
   - ✅ `/metrics` endpoint handler

3. **Requirements**
   - ✅ `prometheus-client>=0.18.0` уже в shared/requirements.txt

---

## ❌ Что НУЖНО СДЕЛАТЬ:

### Шаг 1: Интегрировать Prometheus в каждый сервис

Для каждого из сервисов нужно добавить в `main.py`:

#### Learning Service (`/platform-services/learning-service/main.py`):

```python
# Add imports
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

# Add middleware (ПОСЛЕ CORS, до других middleware)
app.add_middleware(PrometheusMiddleware, service_name="learning-service")

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    return get_metrics_endpoint()()
```

#### Governance Service (`/platform-services/governance-service/main.py`):

```python
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

app.add_middleware(PrometheusMiddleware, service_name="governance-service")

@app.get("/metrics")
async def metrics():
    return get_metrics_endpoint()()
```

#### Community Portal (`/platform-services/community-service/portal/main.py`):

```python
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

app.add_middleware(PrometheusMiddleware, service_name="community-portal")

@app.get("/metrics")
async def metrics():
    return get_metrics_endpoint()()
```

#### Community Marketplace (`/platform-services/community-service/marketplace/main.py`):

```python
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

app.add_middleware(PrometheusMiddleware, service_name="community-marketplace")

@app.get("/metrics")
async def metrics():
    return get_metrics_endpoint()()
```

---

### Шаг 2: Добавить Business Metrics (опционально)

В key endpoints можно добавить бизнес-метрики:

#### Learning Service - Track Enrollments:

```python
# In services/training_service.py
from shared.monitoring import track_business_metric

async def create_enrollment(...):
    # ... existing code ...

    # Track metric
    track_business_metric(
        "enrollment",
        "learning-service",
        program_type=enrollment.program_type,
        tenant_id=str(enrollment.tenant_id)
    )

    return enrollment
```

#### Learning Service - Track Certifications:

```python
# In services/training_service.py
from shared.monitoring import track_business_metric

async def issue_certification(...):
    # ... existing code ...

    track_business_metric(
        "certification",
        "learning-service",
        certification_type=program_type,
        tenant_id=str(tenant_id)
    )
```

#### Governance Service - Track Policies:

```python
# In services/governance_service.py
from shared.monitoring import track_business_metric

async def create_policy(...):
    # ... existing code ...

    track_business_metric(
        "policy",
        "governance-service",
        policy_type=policy.policy_type,
        tenant_id=str(policy.tenant_id)
    )
```

#### Marketplace - Track Specialist Verifications:

```python
# In api/specialists.py (verify-via-governance endpoint)
from shared.monitoring import track_business_metric

if verification_result.get('is_verified'):
    track_business_metric(
        "specialist_verified",
        "community-marketplace",
        verification_source=verification_result.get('verification_source'),
        tenant_id=str(specialist.tenant_id)
    )
```

#### Marketplace - Track Project Matches:

```python
# In api/projects.py (matching-specialists endpoint)
from shared.monitoring import track_business_metric

for specialist in matching_specialists:
    score_range = "high" if specialist["match_score"] >= 90 else "medium" if specialist["match_score"] >= 70 else "low"

    track_business_metric(
        "project_matched",
        "community-marketplace",
        match_score_range=score_range,
        tenant_id=str(project.tenant_id)
    )
```

---

### Шаг 3: Добавить EventBus Metrics (опционально)

В event handlers можно трекать обработку:

```python
# In portal/events/subscribers.py
from shared.monitoring import track_event_consumed
import time

async def on_training_completed(event_data: Dict[str, Any]):
    start_time = time.time()

    try:
        # ... existing handler code ...

        # Track success
        duration = time.time() - start_time
        track_event_consumed(
            "learning.training.completed",
            "community-portal",
            duration
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        # Track failure (duration = 0 indicates failure)
        track_event_consumed(
            "learning.training.completed",
            "community-portal",
            0
        )
        raise
```

---

## 📈 Доступные Метрики

### HTTP Metrics (автоматические через middleware):

```promql
# Total requests by service
http_requests_total{service="learning-service"}

# Request duration by endpoint
http_request_duration_seconds{service="learning-service",endpoint="/api/v1/learning/enrollments"}

# Requests in progress
http_requests_in_progress{service="learning-service"}
```

### Business Metrics (если добавить):

```promql
# Total enrollments
enrollments_total{service="learning-service",program_type="bcm",tenant_id="tenant_1"}

# Certifications issued
certifications_issued_total{service="learning-service"}

# Policies created
policies_created_total{service="governance-service",policy_type="procedure"}

# Specialists verified
specialists_verified_total{service="community-marketplace",verification_source="governance_role"}

# Project matches
projects_matched_total{service="community-marketplace",match_score_range="high"}
```

### EventBus Metrics (если добавить):

```promql
# Messages published
eventbus_messages_published_total{event_type="learning.training.completed",service="learning-service"}

# Messages consumed
eventbus_messages_consumed_total{event_type="learning.training.completed",service="community-portal"}

# Event processing duration
eventbus_processing_duration_seconds{event_type="learning.training.completed"}
```

---

## 🚀 Как запустить мониторинг

### Option 1: Docker Compose (рекомендуется)

```bash
cd /Users/MD/AI-Platform-ISO/platform-services/monitoring

# Start Prometheus
docker-compose up -d prometheus

# Start Grafana (if available)
docker-compose up -d grafana
```

### Option 2: Standalone Prometheus

```bash
cd /Users/MD/AI-Platform-ISO/platform-services/monitoring

# Run Prometheus
prometheus --config.file=prometheus.yml --web.listen-address=:9090
```

### Проверка:

1. **Prometheus UI:** http://localhost:9090
2. **Targets:** http://localhost:9090/targets (должны быть все сервисы UP)
3. **Metrics:** http://localhost:9090/graph (можно строить графики)

### Проверка метрик сервиса:

```bash
# Learning Service
curl http://localhost:8021/metrics

# Governance Service
curl http://localhost:8022/metrics

# Community Portal
curl http://localhost:8023/metrics

# Community Marketplace
curl http://localhost:8024/metrics
```

Должны видеть Prometheus metrics в формате:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/api/v1/learning/enrollments",method="POST",service="learning-service",status="200"} 15.0
...
```

---

## 📊 Grafana Dashboards (опционально)

Если есть Grafana, можно создать дашборды:

### Dashboard 1: Service Overview

**Panels:**
- Request Rate (по сервисам)
- Response Time (P50, P95, P99)
- Error Rate
- Requests In Progress

**PromQL Examples:**
```promql
# Request rate
rate(http_requests_total[5m])

# P95 response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

### Dashboard 2: Business Metrics

**Panels:**
- Enrollments Created (по программам)
- Certifications Issued (по типам)
- Policies Created (по типам)
- Specialists Verified (по источникам)
- Project Matches (по score ranges)

**PromQL Examples:**
```promql
# Enrollments per program type
sum(enrollments_total) by (program_type)

# Certifications issued today
increase(certifications_issued_total[1d])

# Specialist verification sources
sum(specialists_verified_total) by (verification_source)
```

### Dashboard 3: EventBus Health

**Panels:**
- Messages Published/Consumed
- Event Processing Duration
- Event Processing Errors

**PromQL Examples:**
```promql
# Message throughput
rate(eventbus_messages_published_total[5m])

# Average processing time
rate(eventbus_processing_duration_seconds_sum[5m]) / rate(eventbus_processing_duration_seconds_count[5m])
```

---

## 🔍 Troubleshooting

### Метрики не собираются:

1. **Проверить middleware добавлен:**
   ```bash
   grep -r "PrometheusMiddleware" /Users/MD/AI-Platform-ISO/platform-services/*/main.py
   ```

2. **Проверить /metrics endpoint:**
   ```bash
   curl http://localhost:8021/metrics
   ```

3. **Проверить Prometheus targets:**
   - Открыть http://localhost:9090/targets
   - Все сервисы должны быть "UP"
   - Если "DOWN", проверить порты и доступность

### Prometheus не находит сервисы:

1. **Проверить docker network** (если через Docker):
   ```bash
   docker network inspect bcm-platform-network
   ```

2. **Проверить service names в prometheus.yml:**
   - Должны совпадать с именами контейнеров
   - Или использовать `localhost:PORT` для local development

3. **Local development config:**
   ```yaml
   # For local development (без Docker)
   - job_name: 'learning-service'
     static_configs:
       - targets: ['localhost:8021']  # Instead of 'learning-service:8021'
   ```

---

## ✅ Checklist

### Интеграция (минимум):
- [ ] Добавить PrometheusMiddleware в Learning Service main.py
- [ ] Добавить PrometheusMiddleware в Governance Service main.py
- [ ] Добавить PrometheusMiddleware в Community Portal main.py
- [ ] Добавить PrometheusMiddleware в Community Marketplace main.py
- [ ] Добавить `/metrics` endpoints во все 4 сервиса
- [ ] Запустить Prometheus
- [ ] Проверить targets в Prometheus UI (все UP)

### Опциональные улучшения:
- [ ] Добавить business metrics в key endpoints
- [ ] Добавить EventBus metrics в event handlers
- [ ] Настроить Grafana dashboards
- [ ] Настроить alerting rules
- [ ] Добавить Database query metrics

---

## 📝 Summary

**Готово к интеграции:**
- ✅ Prometheus config обновлен (4 новых сервиса)
- ✅ Shared monitoring library создана
- ✅ Метрики определены (HTTP, Business, EventBus)
- ✅ Helper functions готовы

**Нужно сделать:**
- ❌ Добавить middleware в main.py каждого сервиса (4 файла)
- ❌ Добавить /metrics endpoints (4 файла)
- ❌ Опционально: добавить business metrics

**Время на интеграцию:** ~15-20 минут

**Дата:** 2025-10-03
