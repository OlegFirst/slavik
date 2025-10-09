# System BCM - Observability Integration

**Integration Date**: 2025-10-09
**Status**: ✅ **INTEGRATED**

---

## 📊 Overview

System BCM is fully integrated into the platform's observability infrastructure, providing comprehensive monitoring, alerting, and visualization for the BCM self-application service.

---

## 🔗 Integration Points

### Prometheus Integration

**Scrape Target**: `system-bcm-service:8050/metrics`
**Scrape Interval**: 15 seconds
**Retention**: 15 days

**Metrics Exported** (20+ metrics):
```
# Service Health
system_bcm_running{version="1.0.0"}
system_bcm_cycle_total
system_bcm_cycle_duration_seconds
system_bcm_cycle_last_success_timestamp

# Recovery Metrics
system_bcm_recovery_total{service,procedure}
system_bcm_recovery_success_total{service}
system_bcm_recovery_duration_seconds{service}
system_bcm_rto_met_total{service}

# Platform Health
system_bcm_service_available{service}
system_bcm_service_response_time{service}
system_bcm_service_error_rate{service}

# Learning Metrics
system_bcm_insights_generated_total
system_bcm_patterns_detected_total
system_bcm_improvements_applied_total
system_bcm_learning_effectiveness
```

### Grafana Dashboard

**Location**: `/infrastructure/observability/dashboards/system-bcm-dashboard.json`

**Panels** (6 panels):
1. Service Status - Running, EventBus connected, last cycle
2. BCM Cycle Performance - Duration over time, target tracking
3. Platform Health Matrix - All services health, RTO, last check
4. Recovery Statistics - Total recoveries, success rate, avg time
5. Learning Insights - Insights by type (patterns, metrics, optimizations)
6. Recent Events Timeline - BCM events in last 24 hours

**Refresh**: 5 seconds
**Time Range**: Last 24 hours (default)

### Alert Manager

**Alert Rules**: 20+ rules in `/infrastructure/observability/alerts/system-bcm.yml`

**Critical Alerts**:
- SystemBCMServiceDown (for: 1m)
- BCMCycleFailing (for: 5m)
- CriticalServiceDown (for: 1m)
- CascadeFailureDetected (for: 30s)

**High Priority Alerts**:
- RecoveryProcedureFailing (for: 3m)
- RTOTargetMissed (for: 1m)
- HighPriorityRiskDetected (for: 5m)
- ResourceContentionCritical (for: 2m)

**Warning Alerts**:
- BCMCycleSlow (for: 10m)
- LearningEffectivenessLow (for: 30m)
- InsightsNotGenerated (for: 1h)

---

## 📁 File Structure

```
infrastructure/observability/services/system-bcm/
├── README.md                          # This file
├── prometheus-config.yml              # Prometheus scrape config
├── alerts.yml                         # Alert rules
├── dashboards/
│   └── system-bcm-overview.json       # Grafana dashboard
└── queries/
    ├── performance-queries.promql     # Performance queries
    ├── health-queries.promql          # Health check queries
    └── recovery-queries.promql        # Recovery metrics queries
```

---

## 🚀 Deployment

### Add to Prometheus

Add to `/infrastructure/observability/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'system-bcm'
    scrape_interval: 15s
    static_configs:
      - targets: ['system-bcm-service:8050']
    metrics_path: '/metrics'
```

### Import Grafana Dashboard

```bash
# Import dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/system-bcm-overview.json \
  -u admin:admin
```

### Load Alert Rules

```bash
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload
```

---

## 📈 Key Metrics Queries

### Cycle Performance

```promql
# Average cycle duration (last hour)
avg_over_time(system_bcm_cycle_duration_seconds[1h])

# Cycle success rate
rate(system_bcm_cycle_total[5m])

# Time since last successful cycle
time() - system_bcm_cycle_last_success_timestamp
```

### Recovery Performance

```promql
# Recovery success rate by service
sum by (service) (system_bcm_recovery_success_total) /
sum by (service) (system_bcm_recovery_total)

# Average recovery duration
avg by (service) (system_bcm_recovery_duration_seconds)

# RTO compliance rate
sum(system_bcm_rto_met_total) / sum(system_bcm_recovery_total)
```

### Platform Health

```promql
# Services availability
system_bcm_service_available

# Average response time by service
avg_over_time(system_bcm_service_response_time[5m])

# Error rate by service
rate(system_bcm_service_error_rate[5m])
```

### Learning Effectiveness

```promql
# Total insights generated
sum(increase(system_bcm_insights_generated_total[24h]))

# Patterns detected
sum(increase(system_bcm_patterns_detected_total[24h]))

# Learning effectiveness trend
system_bcm_learning_effectiveness
```

---

## 🔔 Alert Configuration

### Configure Alert Routing

Add to `/infrastructure/observability/alertmanager/config.yml`:

```yaml
route:
  routes:
    - match:
        service: system-bcm
      receiver: system-bcm-alerts
      group_by: ['alertname', 'service']
      group_wait: 10s
      group_interval: 5m
      repeat_interval: 4h

receivers:
  - name: system-bcm-alerts
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#bcm-alerts'
        title: 'System BCM Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## 🎯 SLOs (Service Level Objectives)

### Availability SLO

**Target**: 99.9% uptime

```promql
# Availability SLO (30 days)
avg_over_time(system_bcm_running[30d]) * 100
```

### Performance SLO

**Target**: 95% of cycles complete in <30s

```promql
# Performance SLO
histogram_quantile(0.95,
  rate(system_bcm_cycle_duration_seconds_bucket[24h])
) < 30
```

### Recovery SLO

**Target**: 90% of recoveries meet RTO

```promql
# Recovery SLO
(sum(system_bcm_rto_met_total) /
 sum(system_bcm_recovery_total)) > 0.9
```

---

## 🔍 Troubleshooting

### No Metrics Appearing

```bash
# 1. Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="system-bcm")'

# 2. Test metrics endpoint
curl http://localhost:8050/metrics | grep system_bcm

# 3. Check Prometheus logs
docker logs prometheus | grep system-bcm
```

### Dashboard Not Loading

```bash
# 1. Check Grafana datasource
curl -u admin:admin http://localhost:3000/api/datasources | jq

# 2. Test Prometheus connection from Grafana
curl -u admin:admin http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up

# 3. Re-import dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/system-bcm-overview.json \
  -u admin:admin
```

### Alerts Not Firing

```bash
# 1. Check alert rules
curl http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name=="system-bcm")'

# 2. Check alert status
curl http://localhost:9090/api/v1/alerts | jq

# 3. Reload Prometheus config
curl -X POST http://localhost:9090/-/reload
```

---

## 📚 Related Documentation

- [Platform Observability README](../../README.md)
- [Prometheus Configuration](../../prometheus/)
- [Grafana Dashboards](../../grafana/)
- [Alert Manager Configuration](../../alertmanager/)
- [System BCM Integration Guide](/intelligent-core/system-bcm-service/PLATFORM_INTEGRATION.md)

---

**Integration Status**: ✅ **COMPLETE**
**Last Updated**: 2025-10-09
