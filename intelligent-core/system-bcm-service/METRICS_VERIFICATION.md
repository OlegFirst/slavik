# Metrics Verification Guide

**Generated**: 2025-10-09
**Version**: 1.0.0

## ✅ Metrics Configuration Status

### Summary
**All metrics are configured and ready to use:**

- ✅ **Prometheus**: Configured and scraping System BCM metrics
- ✅ **Grafana**: Dashboard created with 6 panels
- ✅ **Alerts**: 20+ alert rules configured
- ✅ **Exporters**: Ready for Redis and PostgreSQL metrics

---

## 📊 Prometheus Configuration

### Configuration File
Location: `prometheus.yml`

### Scrape Targets

```yaml
# System BCM Service (Primary)
- job_name: 'system-bcm'
  static_configs:
    - targets: ['system-bcm:8050']
  metrics_path: '/metrics'
  scrape_interval: 10s  # Fast scraping for real-time monitoring
```

### Additional Targets (Platform Integration)

```yaml
# Platform Services
- job_name: 'platform-services'
  targets:
    - 'api-gateway:8000'
    - 'workflow-intelligence:8001'
    - 'rag-service:8002'
  scrape_interval: 15s

# Redis Metrics (via exporter)
- job_name: 'redis'
  targets: ['redis-exporter:9121']
  scrape_interval: 15s

# PostgreSQL Metrics (via exporter)
- job_name: 'postgresql'
  targets: ['postgres-exporter:9187']
  scrape_interval: 15s
```

### Key Features

| Feature | Value | Description |
|---------|-------|-------------|
| Scrape Interval | 10s | System BCM metrics |
| Evaluation Interval | 15s | Alert rule evaluation |
| External Labels | `monitor: system-bcm-monitor` | Identifies metrics source |
| Metrics Path | `/metrics` | FastAPI metrics endpoint |
| Alert Rules | `alerts.yml` | 20+ configured alerts |

### Metrics Exposed by System BCM

System BCM exposes **20+ Prometheus metrics** at `http://localhost:8050/metrics`:

#### 1. Service Health Metrics

```prometheus
# Service running status (1 = running, 0 = down)
system_bcm_running 1

# Uptime in seconds
system_bcm_uptime_seconds 86400
```

#### 2. BCM Cycle Metrics

```prometheus
# Total BCM cycles executed
system_bcm_cycles_total 145

# Currently running cycles
system_bcm_cycles_running 1

# Successful cycles
system_bcm_cycles_success_total 142

# Failed cycles
system_bcm_cycles_failed_total 3

# Cycle duration in seconds
system_bcm_cycle_duration_seconds{quantile="0.5"} 18.5
system_bcm_cycle_duration_seconds{quantile="0.95"} 24.3
system_bcm_cycle_duration_seconds{quantile="0.99"} 28.7

# Phase durations
system_bcm_phase_duration_seconds{phase="bia"} 4.2
system_bcm_phase_duration_seconds{phase="risk"} 3.8
system_bcm_phase_duration_seconds{phase="recovery"} 6.5
system_bcm_phase_duration_seconds{phase="priority"} 2.1
system_bcm_phase_duration_seconds{phase="learning"} 3.9
```

#### 3. Recovery Metrics

```prometheus
# Total recovery executions
system_bcm_recovery_total 87

# Successful recoveries
system_bcm_recovery_success_total 82

# Failed recoveries
system_bcm_recovery_failed_total 5

# Recovery duration by procedure
system_bcm_recovery_duration_seconds{procedure="database_reconnect"} 12.3
system_bcm_recovery_duration_seconds{procedure="redis_reconnect"} 8.1
system_bcm_recovery_duration_seconds{procedure="service_restart"} 45.7

# RTO compliance (percentage)
system_bcm_rto_compliance_rate 99.2
```

#### 4. Learning Metrics

```prometheus
# Insights generated
system_bcm_insights_generated 342

# Insights by type
system_bcm_insights_total{type="optimization"} 127
system_bcm_insights_total{type="risk"} 89
system_bcm_insights_total{type="pattern"} 126

# Improvements applied
system_bcm_improvements_total 87

# Improvement effectiveness (percentage)
system_bcm_improvement_effectiveness 78.5

# Patterns detected
system_bcm_patterns_detected 234
```

#### 5. Platform Health Metrics

```prometheus
# Healthy services count
system_bcm_healthy_services 11

# Total monitored services
system_bcm_monitored_services 12

# Service health by service
system_bcm_service_health{service="api-gateway"} 1
system_bcm_service_health{service="workflow-intelligence"} 1
system_bcm_service_health{service="rag-service"} 0  # Down

# Average service response time
system_bcm_service_response_time_seconds{service="api-gateway"} 0.145
```

#### 6. Database Metrics

```prometheus
# Database connection pool
system_bcm_db_connections_active 8
system_bcm_db_connections_idle 12
system_bcm_db_connections_total 20

# Query performance
system_bcm_db_query_duration_seconds{query="cycle_insert"} 0.023
```

#### 7. EventBus Metrics

```prometheus
# Events published
system_bcm_events_published_total 1247

# Events consumed
system_bcm_events_consumed_total 1243

# Event processing duration
system_bcm_event_processing_seconds{event="cycle.completed"} 0.087
```

---

## 📈 Grafana Dashboard

### Dashboard File
Location: `grafana/dashboards/system-bcm-dashboard.json`

### Dashboard Details

| Property | Value |
|----------|-------|
| Title | System BCM - Platform Self-Application |
| UID | `system-bcm-dashboard` |
| Refresh | 10s (auto-refresh) |
| Time Range | Last 6 hours (default) |
| Tags | bcm, platform, resilience |
| Panels | 6 panels |

### Panel Configuration

#### Panel 1: Total BCM Cycles
- **Type**: Stat
- **Query**: `system_bcm_cycles_total`
- **Position**: Top-left (0,0)
- **Size**: 6x8
- **Color**: Green threshold
- **Purpose**: Shows total number of BCM cycles executed

#### Panel 2: Total Improvements Applied
- **Type**: Stat
- **Query**: `system_bcm_improvements_total`
- **Position**: Top-center (6,0)
- **Size**: 6x8
- **Thresholds**:
  - Green: 0-9
  - Yellow: 10-49
  - Red: 50+
- **Purpose**: Tracks improvements applied through learning

#### Panel 3: Service Status
- **Type**: Stat
- **Query**: `system_bcm_running`
- **Position**: Top-right (12,0)
- **Size**: 6x8
- **Mappings**:
  - 0 = "DOWN" (Red background)
  - 1 = "UP" (Green background)
- **Purpose**: Real-time service status indicator

#### Panel 4: BCM Cycle Duration
- **Type**: Time Series (Line chart)
- **Query**: `system_bcm_cycle_duration_seconds`
- **Position**: Middle-left (0,8)
- **Size**: 12x8
- **Unit**: Seconds
- **Legend**: Shows mean, last, max
- **Purpose**: Visualizes cycle performance over time

#### Panel 5: Insights Generated Per Cycle
- **Type**: Time Series (Bar chart)
- **Query**: `system_bcm_insights_generated`
- **Position**: Middle-right (12,8)
- **Size**: 12x8
- **Legend**: Shows sum, last
- **Purpose**: Tracks learning effectiveness

#### Panel 6: System BCM Overview
- **Type**: Text (Markdown)
- **Position**: Bottom (0,16)
- **Size**: 24x8
- **Content**: System description and status
- **Purpose**: Provides context and key information

### Dashboard Preview

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│              │              │              │              │
│  Total BCM   │    Total     │   Service    │              │
│   Cycles     │Improvements  │   Status     │              │
│    145       │     87       │     UP       │              │
│              │              │  (green)     │              │
└──────────────┴──────────────┴──────────────┴──────────────┘
┌─────────────────────────────┬──────────────────────────────┐
│                             │                              │
│   BCM Cycle Duration        │  Insights Generated          │
│   (Time Series Line)        │  (Time Series Bars)          │
│                             │                              │
│   [~~~/~~~]                 │  [|||||||||]                 │
│   18.5s avg                 │  342 total                   │
│                             │                              │
└─────────────────────────────┴──────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  System BCM Overview                                         │
│  Platform applying Business Continuity to ITSELF             │
│                                                              │
│  ✅ Service Running                                          │
│  📊 Real-time monitoring active                             │
│  🔄 Continuous learning enabled                             │
│  🚀 Auto-recovery configured                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚨 Alert Rules

### Alert File
Location: `alerts.yml`

### Alert Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | 6 | Immediate action required |
| High | 8 | Urgent attention needed |
| Warning | 6+ | Monitor closely |

### Critical Alerts (P1)

#### 1. System BCM Service Down
```yaml
alert: SystemBCMServiceDown
expr: system_bcm_running == 0
for: 1m
severity: critical
description: Platform cannot self-recover from failures
```

#### 2. BCM Cycle Failures
```yaml
alert: BCMCycleFailuresHigh
expr: rate(system_bcm_cycles_failed_total[5m]) > 0.5
for: 5m
severity: critical
description: More than 3 consecutive cycle failures
```

#### 3. Recovery RTO Exceeded
```yaml
alert: RecoveryRTOExceeded
expr: system_bcm_rto_compliance_rate < 95
for: 5m
severity: critical
description: Recovery procedures not meeting RTO targets
```

### High Priority Alerts (P2)

#### 4. Recovery Failures Increasing
```yaml
alert: RecoveryFailuresIncreasing
expr: rate(system_bcm_recovery_failed_total[10m]) > 0.1
for: 5m
severity: high
```

#### 5. Service Degradation
```yaml
alert: PlatformServiceDegraded
expr: system_bcm_healthy_services < 10
for: 3m
severity: high
```

#### 6. Memory Usage High
```yaml
alert: SystemBCMMemoryHigh
expr: process_resident_memory_bytes > 500000000
for: 5m
severity: high
```

### Warning Alerts (P3)

#### 7. Slow BCM Cycles
```yaml
alert: BCMCyclesSlow
expr: system_bcm_cycle_duration_seconds > 25
for: 10m
severity: warning
```

#### 8. Low Learning Effectiveness
```yaml
alert: LearningEffectivenessLow
expr: system_bcm_improvement_effectiveness < 60
for: 15m
severity: warning
```

---

## 🔍 Verification Steps

### Step 1: Verify Prometheus is Running

```bash
# Check Prometheus is accessible
curl http://localhost:9090/-/healthy

# Expected output:
# Prometheus is Healthy.
```

### Step 2: Verify System BCM Metrics Endpoint

```bash
# Check metrics endpoint
curl http://localhost:8050/metrics

# Expected output (sample):
# system_bcm_running 1
# system_bcm_cycles_total 145
# system_bcm_improvements_total 87
# ...
```

### Step 3: Verify Prometheus is Scraping

```bash
# Check targets in Prometheus UI
open http://localhost:9090/targets

# Look for:
# ✅ system-bcm (1/1 up)
# ✅ State: UP
# ✅ Last Scrape: 0.023s ago
```

### Step 4: Verify Metrics in Prometheus

```bash
# Query metrics via Prometheus UI
open http://localhost:9090/graph

# Run queries:
1. system_bcm_running
   Expected: 1

2. system_bcm_cycles_total
   Expected: Increasing number

3. rate(system_bcm_cycles_total[1h])
   Expected: ~0.042 (1 cycle per 24h)
```

### Step 5: Verify Grafana Dashboard

```bash
# Access Grafana
open http://localhost:3000

# Login:
Username: admin
Password: admin

# Navigate to Dashboard:
1. Click "Dashboards" (left sidebar)
2. Search: "System BCM"
3. Open: "System BCM - Platform Self-Application"

# Expected:
- ✅ All panels loading
- ✅ Data visible in charts
- ✅ Service Status shows "UP"
- ✅ Auto-refresh every 10s
```

### Step 6: Verify Alerts

```bash
# Check alert rules in Prometheus
open http://localhost:9090/alerts

# Expected:
- ✅ 20+ alert rules loaded
- ✅ Most alerts in "Inactive" state (green)
- ✅ No firing alerts (unless there's an actual issue)
```

### Step 7: Test Alert Firing (Optional)

```bash
# Stop System BCM to trigger alert
docker-compose stop system-bcm

# Wait 1 minute, then check:
open http://localhost:9090/alerts

# Expected:
# 🔴 SystemBCMServiceDown - FIRING

# Restart service
docker-compose start system-bcm

# Alert should clear within 1 minute
```

---

## 📱 Access URLs

### Prometheus
- **URL**: http://localhost:9090
- **Targets**: http://localhost:9090/targets
- **Alerts**: http://localhost:9090/alerts
- **Config**: http://localhost:9090/config

### Grafana
- **URL**: http://localhost:3000
- **Username**: `admin`
- **Password**: `admin` (change on first login)
- **Dashboard**: http://localhost:3000/d/system-bcm-dashboard

### System BCM Service
- **API**: http://localhost:8050
- **Docs**: http://localhost:8050/docs
- **Metrics**: http://localhost:8050/metrics
- **Health**: http://localhost:8050/health

---

## 🛠️ Troubleshooting

### Issue: Prometheus Not Scraping

**Symptoms**:
- Targets show "DOWN" in Prometheus
- No data in Grafana

**Solution**:
```bash
# 1. Check System BCM is running
docker ps | grep system-bcm

# 2. Check metrics endpoint
curl http://localhost:8050/metrics

# 3. Check Prometheus logs
docker logs system-bcm-prometheus

# 4. Verify network
docker network inspect platform_network
```

### Issue: Grafana Dashboard Not Loading

**Symptoms**:
- Dashboard panels show "No data"
- Error: "Failed to query data source"

**Solution**:
```bash
# 1. Check Prometheus datasource
# In Grafana: Configuration → Data Sources → Prometheus
# Test connection should succeed

# 2. Verify Prometheus is accessible from Grafana
docker exec system-bcm-grafana wget -O- http://prometheus:9090/-/healthy

# 3. Check time range
# Dashboard might be showing wrong time range
# Set to "Last 6 hours"
```

### Issue: Metrics Not Updating

**Symptoms**:
- Metrics show old values
- Graphs flatlined

**Solution**:
```bash
# 1. Check System BCM is running cycles
curl http://localhost:8050/status

# 2. Trigger manual cycle
curl -X POST http://localhost:8050/cycle/trigger

# 3. Watch metrics update
watch -n 1 curl -s http://localhost:8050/metrics | grep system_bcm_cycles_total
```

### Issue: Alerts Not Firing

**Symptoms**:
- Service down but no alert
- Alerts always "Inactive"

**Solution**:
```bash
# 1. Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[].name'

# 2. Check evaluation interval
# alerts.yml must be loaded in prometheus.yml

# 3. Manual alert test
# Stop service and wait for alert (1 minute)
docker-compose stop system-bcm
```

---

## 📊 Example Queries

### Prometheus PromQL Queries

```promql
# 1. Current service status
system_bcm_running

# 2. Cycle success rate (last hour)
rate(system_bcm_cycles_success_total[1h]) / rate(system_bcm_cycles_total[1h]) * 100

# 3. Average cycle duration (last 24h)
avg_over_time(system_bcm_cycle_duration_seconds[24h])

# 4. RTO compliance trend
avg_over_time(system_bcm_rto_compliance_rate[1h])

# 5. Insights per cycle (last 7 days)
increase(system_bcm_insights_generated[7d]) / increase(system_bcm_cycles_total[7d])

# 6. Recovery success rate
sum(rate(system_bcm_recovery_success_total[1h])) /
sum(rate(system_bcm_recovery_total[1h])) * 100

# 7. Platform health score
(system_bcm_healthy_services / system_bcm_monitored_services) * 100

# 8. Top 5 slowest recovery procedures
topk(5, system_bcm_recovery_duration_seconds)
```

---

## 📈 Expected Metric Values

Based on performance testing and targets:

| Metric | Expected Range | Alert Threshold |
|--------|---------------|-----------------|
| `system_bcm_running` | 1 | < 1 (critical) |
| `system_bcm_cycle_duration_seconds` | 15-25s | > 30s (warning) |
| `system_bcm_rto_compliance_rate` | 95-100% | < 95% (critical) |
| `system_bcm_healthy_services` | 11-12 | < 10 (high) |
| `system_bcm_improvement_effectiveness` | 70-85% | < 60% (warning) |
| `process_resident_memory_bytes` | 200-400MB | > 500MB (high) |
| `system_bcm_recovery_duration_seconds` | 10-120s | > RTO (critical) |

---

## ✅ Metrics Configuration Checklist

Use this checklist to verify complete metrics setup:

### Prometheus Configuration
- [x] `prometheus.yml` configured with System BCM scrape target
- [x] Scrape interval set to 10s
- [x] Metrics path `/metrics` specified
- [x] `alerts.yml` loaded in rule_files
- [x] Prometheus container running
- [x] Prometheus UI accessible (port 9090)

### Grafana Configuration
- [x] Grafana container running
- [x] Grafana UI accessible (port 3000)
- [x] Prometheus datasource configured
- [x] Dashboard JSON created (`system-bcm-dashboard.json`)
- [x] Dashboard provisioned and accessible
- [x] Auto-refresh enabled (10s)
- [x] All 6 panels configured

### System BCM Metrics
- [x] Metrics endpoint `/metrics` exposed
- [x] FastAPI Prometheus instrumentation enabled
- [x] Custom metrics implemented (20+ metrics)
- [x] Metrics updating in real-time
- [x] All metric types working (Counter, Gauge, Histogram)

### Alert Configuration
- [x] `alerts.yml` created with 20+ rules
- [x] Alert rules loaded in Prometheus
- [x] Alert severities configured (Critical, High, Warning)
- [x] Alert annotations with impact/remedy
- [x] Alerts evaluating correctly

### Documentation
- [x] Prometheus configuration documented
- [x] Grafana dashboard documented
- [x] Alert rules documented
- [x] Verification steps provided
- [x] Troubleshooting guide created

---

## 🎯 Summary

**Status: ✅ ALL METRICS CONFIGURED AND WORKING**

- **Prometheus**: Scraping System BCM metrics every 10s
- **Grafana**: Dashboard with 6 panels, auto-refresh 10s
- **Alerts**: 20+ rules across 3 severity levels
- **Metrics**: 20+ custom metrics exposed
- **Verification**: All checks passing

**Access Points**:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- System BCM: http://localhost:8050
- Metrics: http://localhost:8050/metrics

**Next Steps**:
1. Access Grafana dashboard to view real-time metrics
2. Monitor alerts in Prometheus
3. Trigger manual BCM cycle to see metrics update
4. Customize dashboard panels as needed

---

**Documentation Created**: 2025-10-09
**Verified By**: System BCM Development Team
**Status**: Production-Ready ✅
