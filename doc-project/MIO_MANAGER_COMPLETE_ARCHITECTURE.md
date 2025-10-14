# MIO Manager - Полная архитектура (ГЛАЗА платформы)

**Дата**: 2025-10-10
**Port**: 8046
**Роль**: Observatory - ГЛАЗА платформы

---

## 🎯 Роль МиО Manager

> **МиО - это ГЛАЗА платформы**
>
> Наблюдает за всем, собирает данные, публикует observations.
> Помогает другим компонентам данными, но НЕ командует и НЕ принимает решения.

---

## 🏗️ Архитектура MIO Manager

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                    MIO MANAGER (Port 8046)                           │
│                    ГЛАЗА ПЛАТФОРМЫ / OBSERVATORY                     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. INFRASTRUCTURE STATE MONITOR                            │    │
│  │     (Observation Layer)                                     │    │
│  │                                                             │    │
│  │  Собирает состояние инфраструктуры из:                     │    │
│  │  ├─→ Project Manager                                       │    │
│  │  │   - Ports (used/available)                              │    │
│  │  │   - Databases (postgres, redis availability)            │    │
│  │  │   - Metrics coverage                                    │    │
│  │  │   - Database coverage                                   │    │
│  │  │                                                          │    │
│  │  ├─→ Prometheus (/infrastructure/observability/)           │    │
│  │  │   - Service metrics                                     │    │
│  │  │   - Response times                                      │    │
│  │  │   - Throughput                                          │    │
│  │  │   - Error rates                                         │    │
│  │  │                                                          │    │
│  │  ├─→ Resource Tracker (Phase 2 - internal)                 │    │
│  │  │   - CPU usage (real-time)                               │    │
│  │  │   - Memory usage (real-time)                            │    │
│  │  │   - Disk usage (real-time)                              │    │
│  │  │                                                          │    │
│  │  └─→ Service Discovery                                     │    │
│  │      - Health checks                                       │    │
│  │      - Service registry                                    │    │
│  │      - Availability status                                 │    │
│  │                                                             │    │
│  │  Публикует:                                                │    │
│  │  → platform.mio.state_observed (every 60s)                 │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  2. PERFORMANCE EVALUATOR                                   │    │
│  │     (Performance Observation Layer)                         │    │
│  │                                                             │    │
│  │  Наблюдает за производительностью:                         │    │
│  │  ├─→ Каждого сервиса:                                      │    │
│  │  │   - Response time p95                                   │    │
│  │  │   - Throughput (req/s)                                  │    │
│  │  │   - Error rate                                          │    │
│  │  │   - CPU efficiency (throughput/cpu)                     │    │
│  │  │   - Memory efficiency                                   │    │
│  │  │   - Health score (0-100)                                │    │
│  │  │   - Bottleneck detection                                │    │
│  │  │                                                          │    │
│  │  └─→ Всей системы:                                         │    │
│  │      - Overall health                                      │    │
│  │      - Total throughput                                    │    │
│  │      - System error rate                                   │    │
│  │      - Resource utilization                                │    │
│  │      - Efficiency score                                    │    │
│  │      - ROI score                                           │    │
│  │                                                             │    │
│  │  Публикует:                                                │    │
│  │  → platform.mio.performance_observed (every 60s)           │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  3. RESOURCE TRACKER (Phase 2 - ГЛАЗА для ресурсов)        │    │
│  │     (Real-time Resource Observation)                        │    │
│  │                                                             │    │
│  │  Отслеживает ресурсы в реальном времени:                   │    │
│  │  - CPU usage (каждые 10s)                                  │    │
│  │  - Memory usage (каждые 10s)                               │    │
│  │  - Disk I/O (каждые 10s)                                   │    │
│  │  - Network traffic (каждые 10s)                            │    │
│  │                                                             │    │
│  │  Публикует:                                                │    │
│  │  → platform.mio.resource_snapshot (every 10s)              │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  4. EVENT OBSERVER                                          │    │
│  │     (Platform Events Observation)                           │    │
│  │                                                             │    │
│  │  Подписывается на события от других координаторов:         │    │
│  │                                                             │    │
│  │  Подписан на:                                              │    │
│  │  ├─→ platform.events.* (от ai-event-manager)              │    │
│  │  │   - gap_detected                                        │    │
│  │  │   - pattern_recognized                                  │    │
│  │  │   - recommendation_ready                                │    │
│  │  │                                                          │    │
│  │  ├─→ platform.balancer.* (от balancer-service)            │    │
│  │  │   - imbalance_detected                                  │    │
│  │  │   - rebalancing_completed                               │    │
│  │  │   - metrics_updated                                     │    │
│  │  │                                                          │    │
│  │  ├─→ platform.analytics.* (от analytics-specialist)       │    │
│  │  │   - insights_ready                                      │    │
│  │  │   - bottleneck_detected                                 │    │
│  │  │   - health_check_completed                              │    │
│  │  │                                                          │    │
│  │  └─→ platform.brain.* (от Brain/Predictive)               │    │
│  │      - decision_made                                       │    │
│  │      - prediction_ready                                    │    │
│  │      - strategy_updated                                    │    │
│  │                                                             │    │
│  │  Хранит историю событий для корреляции                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  5. AI INTELLIGENCE LAYER                                   │    │
│  │     (Intelligent Observation Analysis)                      │    │
│  │                                                             │    │
│  │  ├─→ AI Coordinator                                        │    │
│  │  │   - Координирует AI-powered analysis                    │    │
│  │  │   - Интеграция с intelligent-core                       │    │
│  │  │                                                          │    │
│  │  ├─→ Decision Engine                                       │    │
│  │  │   - Анализирует observations                            │    │
│  │  │   - НЕ принимает решения (это Brain!)                  │    │
│  │  │   - Формирует рекомендации для Brain                   │    │
│  │  │                                                          │    │
│  │  └─→ Learning Tracker                                      │    │
│  │      - Отслеживает паттерны                                │    │
│  │      - Continuous learning                                 │    │
│  │      - Feedback loop                                       │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  6. AUTOMATION TOOLKIT MANAGER                              │    │
│  │     (Automated Observation Tools)                           │    │
│  │                                                             │    │
│  │  ├─→ Service Discovery Automation                          │    │
│  │  │   - Автоматическое обнаружение сервисов                │    │
│  │  │   - Service registry updates                            │    │
│  │  │                                                          │    │
│  │  ├─→ Health Check Automation                               │    │
│  │  │   - Автоматические health checks                       │    │
│  │  │   - Availability monitoring                             │    │
│  │  │                                                          │    │
│  │  └─→ Metrics Collection Automation                         │    │
│  │      - Автоматический сбор метрик                          │    │
│  │      - Coverage tracking                                   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  7. SMART SCHEDULER                                         │    │
│  │     (Scheduled Observations)                                │    │
│  │                                                             │    │
│  │  Периодические циклы наблюдения:                           │    │
│  │                                                             │    │
│  │  ├─→ Deep Analysis Cycle (каждые 5 мин)                    │    │
│  │  │   - Глубокий анализ состояния                          │    │
│  │  │   - Корреляция данных                                   │    │
│  │  │                                                          │    │
│  │  ├─→ Compliance Monitoring Cycle (каждые 15 мин)           │    │
│  │  │   - Проверка compliance                                 │    │
│  │  │   - Регуляторные требования                            │    │
│  │  │                                                          │    │
│  │  ├─→ Predictive Analysis Cycle (каждый час)                │    │
│  │  │   - Передача данных в Predictive для анализа           │    │
│  │  │                                                          │    │
│  │  └─→ Workflow Optimization Cycle (каждые 2 часа)           │    │
│  │      - Оптимизация workflow                                │    │
│  │      - Performance trends                                  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  8. INTEGRATION CLIENTS                                     │    │
│  │     (Connectors to other components)                        │    │
│  │                                                             │    │
│  │  ├─→ EventBus Client (критично!)                          │    │
│  │  │   - Публикация observations                             │    │
│  │  │   - Подписка на события                                 │    │
│  │  │                                                          │    │
│  │  ├─→ Workflow Intelligence Client (Brain)                  │    │
│  │  │   - Передача observations в Brain                       │    │
│  │  │                                                          │    │
│  │  ├─→ Predictive Client                                     │    │
│  │  │   - Передача данных для predictions                     │    │
│  │  │                                                          │    │
│  │  ├─→ Workflow Optimizer Client                             │    │
│  │  │   - Передача данных для оптимизации                    │    │
│  │  │                                                          │    │
│  │  ├─→ Coordination Center Client                            │    │
│  │  │   - Координация с центром                              │    │
│  │  │                                                          │    │
│  │  ├─→ Compliance Monitoring Client                          │    │
│  │  │   - Compliance observations                             │    │
│  │  │                                                          │    │
│  │  ├─→ AI Event Manager Client                               │    │
│  │  │   - Event intelligence integration                      │    │
│  │  │                                                          │    │
│  │  ├─→ DevOps Agent Client                                   │    │
│  │  │   - Infrastructure scanning                             │    │
│  │  │                                                          │    │
│  │  └─→ Analytics Specialist Client                           │    │
│  │      - Analytics insights consumption                      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  9. WEB UI DASHBOARD                                        │    │
│  │     (Visualization & Control)                               │    │
│  │                                                             │    │
│  │  - Real-time observations visualization                     │    │
│  │  - Infrastructure state dashboard                           │    │
│  │  - Performance metrics dashboard                            │    │
│  │  - Events timeline                                          │    │
│  │  - Alerts & notifications                                   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  10. API ENDPOINTS                                          │    │
│  │                                                             │    │
│  │  GET /health                    - Health check              │    │
│  │  GET /metrics                   - Prometheus metrics        │    │
│  │                                                             │    │
│  │  GET /api/v1/observations/state - Current infrastructure   │    │
│  │  GET /api/v1/observations/performance - Performance data   │    │
│  │  GET /api/v1/observations/resources - Resource snapshots   │    │
│  │  GET /api/v1/observations/history - Historical data        │    │
│  │  GET /api/v1/observations/events - Events timeline         │    │
│  │                                                             │    │
│  │  GET /ui                        - Web Dashboard            │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ EventBus - ПУБЛИКУЕТ OBSERVATIONS:
                           │
                           ▼
                  ┌─────────────────┐
                  │    EventBus     │
                  └────────┬────────┘
                           │
                           ├─→ platform.mio.state_observed
                           │   (Infrastructure state - every 60s)
                           │
                           ├─→ platform.mio.performance_observed
                           │   (Performance metrics - every 60s)
                           │
                           ├─→ platform.mio.resource_snapshot
                           │   (Resource usage - every 10s)
                           │
                           └─→ platform.mio.alert
                               (Critical observations - as needed)
```

---

## 📊 Data Sources (что МиО наблюдает)

### 1. Infrastructure State Monitor собирает из:

#### Project Manager
```
Location: /infrastructure/tools/project-manager
Data:
  - ports_used / ports_available
  - prometheus_available
  - grafana_available
  - postgres_available
  - redis_available
  - services_with_metrics
  - services_with_db
  - total_services
  - monitoring_coverage
  - database_coverage
```

#### Prometheus (Observability)
```
Location: /infrastructure/observability/ (Port 9090)
Data:
  - Service metrics (response time, throughput, errors)
  - Resource metrics (CPU, memory, disk)
  - Application metrics (custom metrics per service)
  - Scrape targets health
```

#### Resource Tracker (Phase 2 - internal)
```
Location: MIO Manager internal component
Data:
  - CPU usage (real-time, every 10s)
  - Memory usage (real-time, every 10s)
  - Disk I/O (real-time, every 10s)
  - Network traffic (real-time, every 10s)
```

#### Service Discovery
```
Location: /infrastructure/runtime/service-discovery
Data:
  - Service registry
  - Health check status
  - Service availability
  - Service endpoints
```

### 2. Performance Evaluator собирает из:

#### Prometheus API (detailed metrics)
```
Queries:
  - http_request_duration_seconds{quantile="0.95"} → Response time p95
  - rate(http_requests_total[5m]) → Throughput
  - rate(http_requests_errors_total[5m]) → Error rate
  - process_cpu_seconds_total → CPU usage per service
  - process_resident_memory_bytes → Memory usage per service
```

#### Calculations:
```
- CPU Efficiency = throughput / cpu_usage
- Memory Efficiency = throughput / memory_usage
- Health Score = weighted(response_time, error_rate, resource_usage)
- Bottleneck Detection = analyze(cpu, memory, io, errors)
```

### 3. Event Observer подписан на:

```
platform.events.* (ai-event-manager):
  - gap_detected
  - pattern_recognized
  - recommendation_ready

platform.balancer.* (balancer-service):
  - imbalance_detected
  - rebalancing_completed
  - metrics_updated

platform.analytics.* (analytics-specialist):
  - insights_ready ← ВАЖНО! Выжатый сок для Brain
  - bottleneck_detected
  - trend_observed
  - health_check_completed

platform.brain.* (Brain/Predictive):
  - decision_made
  - prediction_ready
  - strategy_updated
```

---

## 📡 Publications (что МиО публикует)

### 1. platform.mio.state_observed (every 60s)
```json
{
  "event": "platform.mio.state_observed",
  "data": {
    "observation_id": "obs_2025101012001",
    "timestamp": "2025-10-10T12:00:00",
    "infrastructure": {
      "ports_available": 50,
      "ports_used": 30,
      "prometheus_available": true,
      "grafana_available": true,
      "postgres_available": true,
      "redis_available": true,
      "total_services": 24,
      "healthy_services": 22,
      "unhealthy_services": 2,
      "monitoring_coverage": 0.75,
      "database_coverage": 0.83,
      "health_check_coverage": 0.92
    },
    "resources": {
      "cpu_usage": 0.45,
      "memory_usage": 0.62,
      "disk_usage": 0.35,
      "network_rx_mbps": 12.5,
      "network_tx_mbps": 8.3
    },
    "status": "healthy",
    "capacity_remaining": 0.55
  },
  "priority": "normal"
}
```

### 2. platform.mio.performance_observed (every 60s)
```json
{
  "event": "platform.mio.performance_observed",
  "data": {
    "observation_id": "obs_perf_2025101012001",
    "timestamp": "2025-10-10T12:00:00",
    "system_performance": {
      "overall_health": 85.5,
      "total_throughput": 1250.0,
      "avg_response_time": 95.0,
      "system_error_rate": 0.015,
      "efficiency_score": 78.5,
      "roi_score": 82.0
    },
    "service_observations": [
      {
        "service_name": "ai-event-manager",
        "health_score": 92.0,
        "response_time_p95": 85.0,
        "throughput": 350.0,
        "error_rate": 0.005,
        "cpu_efficiency": 85.0,
        "bottleneck_detected": false
      },
      {
        "service_name": "analytics-specialist",
        "health_score": 68.0,
        "response_time_p95": 250.0,
        "throughput": 120.0,
        "error_rate": 0.02,
        "cpu_efficiency": 45.0,
        "bottleneck_detected": true,
        "bottleneck_type": "cpu"
      }
    ],
    "bottlenecks": ["analytics-specialist"],
    "recommendations": [
      {
        "service": "analytics-specialist",
        "type": "performance_degradation",
        "recommendation": "CPU bottleneck detected - investigate heavy processes"
      }
    ]
  },
  "priority": "normal"
}
```

### 3. platform.mio.resource_snapshot (every 10s)
```json
{
  "event": "platform.mio.resource_snapshot",
  "data": {
    "timestamp": "2025-10-10T12:00:00",
    "cpu_percent": 45.0,
    "memory_percent": 62.0,
    "disk_percent": 35.0,
    "disk_io_read_mbps": 15.2,
    "disk_io_write_mbps": 8.3,
    "network_rx_mbps": 12.5,
    "network_tx_mbps": 8.3
  },
  "priority": "low"
}
```

### 4. platform.mio.alert (critical observations)
```json
{
  "event": "platform.mio.alert",
  "data": {
    "alert_id": "alert_2025101012001",
    "timestamp": "2025-10-10T12:00:00",
    "alert_type": "critical_observation",
    "severity": "critical",
    "observation": "postgres_unavailable",
    "details": {
      "resource": "postgres",
      "status": "unavailable",
      "last_seen": "2025-10-10T11:55:00",
      "affected_services": ["bia-service", "planning-service"]
    },
    "context": {
      "infrastructure_state": {...},
      "recent_events": [...]
    }
  },
  "priority": "critical"
}
```

---

## 🔄 Data Flow Examples

### Пример 1: Periodic State Observation
```
Every 60 seconds:

1. Infrastructure State Monitor:
   ├─→ Collects from Project Manager
   ├─→ Collects from Prometheus
   ├─→ Collects from Resource Tracker
   └─→ Collects from Service Discovery

2. Performance Evaluator:
   ├─→ Queries Prometheus for detailed metrics
   ├─→ Calculates service performance
   └─→ Calculates system efficiency

3. Combines and publishes:
   ├─→ platform.mio.state_observed
   └─→ platform.mio.performance_observed
```

### Пример 2: Event Correlation
```
МиО наблюдает:

1. Получает: platform.balancer.imbalance_detected
   - Source: balancer-service
   - Data: High CPU on analytics-specialist

2. Коррелирует с собственными observations:
   - Infrastructure state: analytics-specialist CPU = 85%
   - Performance: CPU efficiency = 45% (low)
   - Resource snapshot: System CPU = 45% (ok)

3. Обогащает контекст и сохраняет:
   - Event correlation stored
   - Available for Brain analysis

4. НЕ принимает решения:
   - Это задача Brain!
   - МиО только наблюдает и информирует
```

### Пример 3: Critical Observation Alert
```
МиО обнаруживает критическое состояние:

1. Infrastructure State Monitor:
   ├─→ postgres_available = false
   └─→ Критическое наблюдение!

2. Event Observer проверяет корреляцию:
   ├─→ Нет recent events о postgres
   └─→ Это новое наблюдение

3. Публикует alert:
   └─→ platform.mio.alert
       - Type: critical_observation
       - Details: postgres unavailable
       - Context: infrastructure state + recent events

4. Другие компоненты реагируют:
   - Brain получает alert и принимает решение
   - Orchestrator может запустить emergency workflow
   - balancer-service входит в conservative mode
```

---

## 🎯 Responsibilities (что МиО ДЕЛАЕТ и НЕ ДЕЛАЕТ)

### ✅ МиО ДЕЛАЕТ (Observatory):

1. **Наблюдает**:
   - Собирает данные из всех источников
   - Мониторит infrastructure state
   - Отслеживает performance
   - Следит за ресурсами

2. **Анализирует observations**:
   - Вычисляет метрики (health scores, efficiency, ROI)
   - Выявляет bottlenecks
   - Детектирует аномалии
   - Коррелирует события

3. **Публикует observations**:
   - Infrastructure state
   - Performance observations
   - Resource snapshots
   - Critical alerts

4. **Помогает другим**:
   - Предоставляет данные через API
   - Публикует observations в EventBus
   - Обогащает контекст событий
   - Хранит историю

5. **Координирует сбор данных**:
   - Автоматизация через Automation Toolkit
   - Scheduled cycles через Smart Scheduler
   - Integration с множеством источников

### ❌ МиО НЕ ДЕЛАЕТ:

1. **НЕ принимает решения**:
   - Это задача Brain/Predictive
   - МиО только наблюдает и информирует

2. **НЕ командует**:
   - Не дает директивы другим сервисам
   - Работает через хореографию

3. **НЕ исполняет задачи**:
   - Не балансирует (это balancer-service)
   - Не анализирует детально (это analytics-specialist)
   - Не управляет событиями (это ai-event-manager)

4. **НЕ собирает аналитику**:
   - Собирает сырые данные
   - Аналитику собирает analytics-specialist
   - Analytics выжимает сок и передает в Brain

---

## 🔌 Integration Points

### С observability инфраструктурой:
```
/infrastructure/observability/
├── Prometheus (9090) → МиО собирает metrics
├── Grafana (3001) → Визуализация МиО observations
└── Loki/Tempo → Logs/Traces correlation
```

### С platform-services:
```
МиО подписывается на события от:
- ai-event-manager (events)
- balancer-service (balancing)
- analytics-specialist (insights)
- Brain/Predictive (decisions)

МиО публикует observations для всех
```

### С intelligent-core:
```
- AI Intelligence Layer использует AI Foundation
- Decision Engine интегрирован с workflow_intelligence
- Learning Tracker для continuous improvement
```

---

## ✅ Summary

### МиО Manager как ГЛАЗА:
```
✅ Наблюдает за ВСЕМ
✅ Собирает данные из ВСЕХ источников
✅ Публикует observations в EventBus
✅ Помогает всем компонентам данными
✅ Коррелирует события
✅ Обогащает контекст
✅ Хранит историю

❌ НЕ командует
❌ НЕ принимает решения (это Brain)
❌ НЕ исполняет задачи
```

### Ключевые компоненты:
1. Infrastructure State Monitor - наблюдение за инфраструктурой
2. Performance Evaluator - наблюдение за производительностью
3. Resource Tracker - наблюдение за ресурсами
4. Event Observer - наблюдение за событиями
5. AI Intelligence Layer - intelligent observations
6. Automation Toolkit - автоматизация сбора
7. Smart Scheduler - периодические циклы
8. Integration Clients - коннекторы
9. Web UI Dashboard - визуализация
10. API Endpoints - доступ к observations

---

**Статус**: ✅ Complete Architecture
**Роль**: ГЛАЗА платформы / Observatory
**Принцип**: Наблюдает и информирует, НЕ командует
**Port**: 8046
