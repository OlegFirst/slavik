# Observability Service - BCM Platform

**Purpose:** Monitoring, logging, and metrics for all platform services

**Technology:** Prometheus + Grafana + Loki + Tempo

**Ports:**
- Prometheus: 9090
- Grafana: 3001
- Loki: 3100
- Tempo: 3200

---

## 🎯 Features

### Core Functionality
- ✅ **Metrics Collection** - Prometheus for metrics scraping
- ✅ **Visualization** - Grafana dashboards
- ✅ **Log Aggregation** - Loki for centralized logging
- ✅ **Distributed Tracing** - Tempo for request tracing
- ✅ **Alerting** - Alert manager for notifications
- ✅ **Service Health** - Real-time health monitoring

### Dashboards
- ✅ **BCM Platform Overview** - System-wide metrics
- ✅ **Service Performance** - Per-service performance
- ✅ **Event Analytics** - EventBus statistics
- ✅ **Gateway Metrics** - API Gateway performance
- ✅ **Database Performance** - PostgreSQL metrics

---

## 📊 Metrics Collected

### Platform Metrics
- `bcm_requests_total` - Total requests per service
- `bcm_request_duration_seconds` - Request latency
- `bcm_errors_total` - Total errors
- `bcm_active_connections` - Active connections

### Service-Specific Metrics
- `eventbus_events_published_total` - Events published
- `eventbus_events_consumed_total` - Events consumed
- `gateway_requests_per_service` - Requests routed per service
- `orchestration_ai_calls_total` - AI model invocations

### Infrastructure Metrics
- `postgres_connections_active` - Active DB connections
- `redis_memory_used_bytes` - Redis memory usage
- `cpu_usage_percent` - CPU utilization
- `memory_usage_bytes` - Memory usage

---

## 📈 Grafana Dashboards

### BCM Platform Overview
- System-wide health status
- Total requests/second
- Error rate
- Response time percentiles (p50, p95, p99)

### Service Performance
- Per-service request rates
- Service error rates
- Service response times
- Service health status

### Event Analytics
- Events published per type
- Event processing latency
- Event failure rate
- Top event producers/consumers

### Gateway Metrics
- Requests per endpoint
- Auth success/failure rate
- Rate limit triggers
- Proxy latency

---

## 🚀 Quick Start

### Start Monitoring Stack
```bash
cd services/PLATFORM/observability
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Dashboards
- **Grafana:** http://localhost:3001 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

---

## 🔧 Configuration

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bcm-gateway'
    static_configs:
      - targets: ['gateway:8000']

  - job_name: 'bcm-eventbus'
    static_configs:
      - targets: ['eventbus:8001']

  - job_name: 'bcm-orchestration'
    static_configs:
      - targets: ['orchestration:8002']
```

### Grafana Data Sources
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://loki:3100

  - name: Tempo
    type: tempo
    url: http://tempo:3200
```

---

## 🚨 Alerting

### Alert Rules
```yaml
groups:
  - name: bcm_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(bcm_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: ServiceDown
        expr: up{job=~"bcm-.*"} == 0
        for: 1m
        annotations:
          summary: "Service {{ $labels.job }} is down"

      - alert: HighLatency
        expr: bcm_request_duration_seconds{quantile="0.95"} > 1
        for: 5m
        annotations:
          summary: "High latency on {{ $labels.service }}"
```

---

## 📊 Logging

### Log Levels
- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

### Log Format
```json
{
  "timestamp": "2025-01-20T10:30:45Z",
  "level": "INFO",
  "service": "gateway",
  "message": "Request processed",
  "request_id": "req_123",
  "user_id": "user_456",
  "duration_ms": 45
}
```

---

## 🔍 Distributed Tracing

### Trace Flow
```
┌────────────┐
│  Gateway   │ [Trace Start: trace_id=abc123]
└─────┬──────┘
      │
      ▼
┌────────────┐
│ BIA Service│ [Span: bia_analysis]
└─────┬──────┘
      │
      ▼
┌────────────┐
│  EventBus  │ [Span: event_publish]
└────────────┘
```

### Viewing Traces
- Open Grafana → Explore → Tempo
- Search by trace_id or service name
- View full request flow with timing

---

## 📈 Performance Monitoring

### SLIs (Service Level Indicators)
- **Availability:** 99.9% uptime
- **Latency:** p95 < 200ms
- **Error Rate:** < 0.1%
- **Throughput:** > 100 req/s

### SLOs (Service Level Objectives)
- **Gateway:** 99.95% uptime, p95 latency < 100ms
- **EventBus:** 99.9% event delivery, < 50ms latency
- **Orchestration:** 99.5% uptime, p95 latency < 500ms

---

**Version:** 1.0
**Status:** ✅ Consolidated
**Ports:** 9090 (Prometheus), 3001 (Grafana), 3100 (Loki)
