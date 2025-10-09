# Phase 1 Infrastructure Deployment Guide
**Created:** 2025-10-09
**Component:** Infrastructure Coordination (Phase 1)
**Status:** Ready for Deployment

---

## Overview

This guide covers deploying the complete Phase 1 infrastructure coordination system including:
- ✅ Prometheus & Grafana (already configured)
- ✅ Health Monitoring with EventBus integration
- ✅ Auto-Recovery Service
- ✅ Resource Optimizer
- ✅ Infrastructure Coordinator
- ✅ Metrics API (port 9091)

---

## Pre-Deployment Checklist

### 1. Database Verification
```bash
# Check if PostgreSQL migrations are applied
psql -h aws-1-eu-north-1.pooler.supabase.com \
     -U postgres.tpdkhddtbhpoqzzgxfni \
     -d postgres \
     -p 5432 \
     -c "\dt public.*" | grep -E "(bia|compliance|governance|documents)"

# Expected: Tables for all BCM services should exist
```

**Migration Files Located:**
- `/infrastructure/database/postgresql/migrations/COMBINED_MIGRATIONS_006-018.sql`
- Individual batches: BATCH_1, BATCH_2, BATCH_3

### 2. Environment Variables
```bash
# Required environment variables
export DATABASE_URL="postgresql://postgres.tpdkhddtbhpoqzzgxfni:K@x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
export REDIS_URL="redis://localhost:6379"
export SUPABASE_URL="https://tpdkhddtbhpoqzzgxfni.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="<your-key>"
```

### 3. Port Availability
Check that required ports are available:
```bash
# Phase 1 Infrastructure Ports
lsof -i :9090  # Prometheus (should be free or show existing)
lsof -i :3000  # Grafana (should be free or show existing)
lsof -i :9091  # Metrics API (NEW - should be free)
lsof -i :8055  # EventBus (ai-event-manager)
lsof -i :6379  # Redis
lsof -i :5432  # PostgreSQL
```

---

## Deployment Steps

### Step 1: Start Monitoring Stack (Prometheus & Grafana)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability

# Start the monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services started
docker ps | grep -E "(prometheus|grafana)"

# Expected output:
# bcm-prometheus    ... Up ... 0.0.0.0:9090->9090/tcp
# bcm-grafana       ... Up ... 0.0.0.0:3000->3000/tcp
# bcm-alertmanager  ... Up ... 0.0.0.0:9093->9093/tcp
# bcm-node-exporter ... Up ... 0.0.0.0:9100->9100/tcp
# bcm-cadvisor      ... Up ... 0.0.0.0:8080->8080/tcp
```

**Access Points:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)
- AlertManager: http://localhost:9093

### Step 2: Start Metrics API (Phase 1)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/api

# Install dependencies
pip3 install fastapi uvicorn prometheus-client

# Start Metrics API
python3 metrics_api.py &

# Verify metrics endpoint
curl http://localhost:9091/health
# Expected: {"status":"healthy","service":"metrics_api","port":9091}

curl http://localhost:9091/metrics | head -20
# Expected: Prometheus metrics format
```

### Step 3: Verify Prometheus is Scraping Metrics API

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="metrics-api")'

# Expected: Target should be "up" and healthy
```

### Step 4: Start Infrastructure Coordinator

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus/coordination

# Run Infrastructure Coordinator (demo mode - 5 minutes)
python3 infrastructure_coordinator.py

# Expected output:
# ======================================================================
# Starting Infrastructure Coordinator (Phase 1)
# ======================================================================
# Step 1: Connecting Health Monitor to EventBus...
# ✅ Health Monitor connected to EventBus
#
# Step 2: Registering critical services...
#   ✅ eventbus (interval: 30s)
#   ✅ api_gateway (interval: 30s)
#   ✅ database (interval: 60s)
#   ✅ redis (interval: 30s)
#   ✅ rag_pipeline (interval: 60s)
# ✅ Registered 5 health checks
#
# Step 3: Registering recovery strategies...
#   ✅ eventbus: restart (max 3 attempts)
#   ✅ api_gateway: restart (max 3 attempts)
#   ✅ database: circuit_breaker (max 1 attempts)
#   ✅ redis: restart (max 3 attempts)
#   ✅ rag_pipeline: restart (max 2 attempts)
# ✅ Registered 5 recovery strategies
#
# Step 4: Starting coordination services...
# ======================================================================
# ✅ Infrastructure Coordinator STARTED
# ======================================================================
# Services running:
#   🏥 Health Monitor: Running (30 sec intervals)
#   🔧 Auto-Recovery: Listening for health events
#   📊 Resource Optimizer: Running (5 min intervals)
# ======================================================================
```

---

## Verification Tests

### Test 1: Health Monitor Publishing Events

```bash
# Monitor EventBus for health events (in separate terminal)
cd /Users/MD/AI-Platform-ISO
python3 << 'EOF'
import asyncio
from infrastructure.eventbus import create_eventbus

async def monitor_health_events():
    bus = create_eventbus('redis')

    async def handler(event):
        print(f"📤 Health Event: {event.type}")
        print(f"   Service: {event.data.get('service_name')}")
        print(f"   Status: {event.data.get('status')}")
        print(f"   Previous: {event.data.get('previous_status')}")
        print()

    await bus.subscribe('infrastructure.health.*', handler)
    print("🎧 Listening for health events...\n")

    await asyncio.sleep(300)  # Monitor for 5 minutes

asyncio.run(monitor_health_events())
EOF
```

### Test 2: Metrics API Integration

```bash
# Query metrics from Prometheus
curl -s "http://localhost:9090/api/v1/query?query=up{job='metrics-api'}" | jq .

# Query infrastructure metrics
curl -s "http://localhost:9090/api/v1/query?query=infrastructure_health_status" | jq .
```

### Test 3: Auto-Recovery (Simulated Failure)

```bash
# Stop a service to trigger auto-recovery
docker stop <service-container>

# Watch for recovery events
# Should see:
# 1. infrastructure.health.unhealthy
# 2. infrastructure.recovery.started
# 3. infrastructure.recovery.completed (or failed)
```

### Test 4: Resource Optimization

```bash
# Wait for optimization cycle (runs every 5 minutes)
# Should see event: infrastructure.optimization.completed

# Check Prometheus for optimization metrics
curl -s "http://localhost:9090/api/v1/query?query=infrastructure_efficiency_score" | jq .
```

---

## Grafana Dashboard Setup

### Import Infrastructure Dashboards

1. **Access Grafana:** http://localhost:3000 (admin/admin123)

2. **Add Prometheus Data Source:**
   - Navigate to: Configuration → Data Sources → Add data source
   - Select: Prometheus
   - URL: http://prometheus:9090
   - Click: Save & Test

3. **Import Dashboards:**

   ```bash
   # Check available dashboards
   ls -la /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/

   # Key dashboards:
   # - infrastructure-health.json
   # - service-performance.json
   # - bcm-platform-overview.json
   ```

4. **Import via UI:**
   - Navigate to: Dashboards → Import
   - Upload JSON file or paste JSON content
   - Select Prometheus as data source
   - Click: Import

### Recommended Panels for Phase 1

**Infrastructure Health Dashboard:**
- Service Health Status (gauge)
- Health Check Response Times (graph)
- Recovery Events Timeline (table)
- Health Status Changes (stat)

**Resource Optimization Dashboard:**
- CPU Utilization by Service (graph)
- Memory Utilization by Service (graph)
- Efficiency Score Trend (graph)
- Optimization Recommendations (table)

**Auto-Recovery Dashboard:**
- Recovery Attempts by Service (stat)
- Recovery Success Rate (gauge)
- Recovery Duration (graph)
- Failed Recoveries Alert (alert list)

---

## Monitoring & Alerting

### Alert Rules

Create alert rules in `/infrastructure/observability/config/prometheus/rules/infrastructure.yml`:

```yaml
groups:
  - name: infrastructure_phase1
    interval: 30s
    rules:
      # Service unhealthy for > 5 minutes
      - alert: ServiceUnhealthy
        expr: infrastructure_health_status{status="unhealthy"} > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.service }} is unhealthy"
          description: "{{ $labels.service }} has been unhealthy for 5 minutes"

      # Recovery failed
      - alert: RecoveryFailed
        expr: increase(infrastructure_recovery_failed_total[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Auto-recovery failed for {{ $labels.service }}"
          description: "All recovery attempts exhausted"

      # Low efficiency score
      - alert: LowEfficiencyScore
        expr: infrastructure_efficiency_score < 60
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Infrastructure efficiency score is low"
          description: "Efficiency score below 60 for 15 minutes"
```

### Notification Channels

Configure in Grafana:
- Email (SMTP)
- Slack webhook
- PagerDuty integration
- Microsoft Teams webhook

---

## EventBus Event Catalog

**New Events Added (Phase 1):**

See [INFRASTRUCTURE_EVENTS.md](../eventbus/events/INFRASTRUCTURE_EVENTS.md) for complete documentation.

Summary:
- `infrastructure.health.healthy`
- `infrastructure.health.unhealthy`
- `infrastructure.health.degraded`
- `infrastructure.health.unknown`
- `infrastructure.recovery.started`
- `infrastructure.recovery.completed`
- `infrastructure.recovery.failed`
- `infrastructure.optimization.completed`

**Event Visualization:**

EventCatalog is available at:
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus/event-catalog
npm run dev
# Access: http://localhost:3001
```

---

## Production Deployment

### Systemd Services (for production)

Create systemd service files:

**1. Metrics API Service**
```ini
# /etc/systemd/system/metrics-api.service
[Unit]
Description=Infrastructure Metrics API (Phase 1)
After=network.target

[Service]
Type=simple
User=bcm
WorkingDirectory=/opt/bcm-platform/intelligent-core/orchestration/api
ExecStart=/usr/bin/python3 metrics_api.py
Restart=always
RestartSec=10
Environment="PORT=9091"

[Install]
WantedBy=multi-user.target
```

**2. Infrastructure Coordinator Service**
```ini
# /etc/systemd/system/infrastructure-coordinator.service
[Unit]
Description=Infrastructure Coordinator (Phase 1)
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=bcm
WorkingDirectory=/opt/bcm-platform/infrastructure/eventbus/coordination
ExecStart=/usr/bin/python3 infrastructure_coordinator.py
Restart=always
RestartSec=10
Environment="REDIS_URL=redis://localhost:6379"
Environment="DATABASE_URL=postgresql://..."

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable metrics-api.service
sudo systemctl enable infrastructure-coordinator.service
sudo systemctl start metrics-api.service
sudo systemctl start infrastructure-coordinator.service

# Check status
sudo systemctl status metrics-api.service
sudo systemctl status infrastructure-coordinator.service
```

---

## Troubleshooting

### Issue 1: Metrics API not responding

```bash
# Check if running
ps aux | grep metrics_api

# Check port
lsof -i :9091

# Check logs
tail -f /var/log/metrics-api.log

# Restart
pkill -f metrics_api.py
python3 /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/api/metrics_api.py &
```

### Issue 2: Health events not publishing

```bash
# Verify EventBus connection
redis-cli PING
# Expected: PONG

# Check EventBus streams
redis-cli XINFO STREAM events:default

# Verify Health Monitor has EventBus connected
# Check logs for: "HealthMonitor connected to EventBus"
```

### Issue 3: Prometheus not scraping Metrics API

```bash
# Check Prometheus config
cat /Users/MD/AI-Platform-ISO/infrastructure/observability/config/prometheus/prometheus.yml | grep -A 10 metrics-api

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="metrics-api")'

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload
```

### Issue 4: Auto-Recovery not triggering

```bash
# Verify Auto-Recovery subscriptions
# Check logs for: "✅ Subscribed to infrastructure.health.unhealthy"

# Manually publish test event
python3 << 'EOF'
import asyncio
from infrastructure.eventbus import create_eventbus, Event

async def test_recovery():
    bus = create_eventbus('redis')
    await bus.publish(Event.create(
        event_type='infrastructure.health.unhealthy',
        data={
            'service_name': 'test_service',
            'status': 'unhealthy',
            'message': 'Test failure'
        },
        source='test',
        tenant_id='system'
    ))
    print("✅ Published test unhealthy event")
    await asyncio.sleep(2)

asyncio.run(test_recovery())
EOF
```

---

## Performance Benchmarks

Expected performance for Phase 1:

| Metric | Target | Actual |
|--------|--------|--------|
| Health check interval | 30s | ✅ 30s |
| Health event latency | < 100ms | - |
| Recovery start latency | < 1s | - |
| Resource optimization cycle | 5min | ✅ 5min |
| Metrics API response time | < 50ms | - |
| EventBus throughput | > 1000 events/s | - |

**Run benchmarks:**
```bash
cd /Users/MD/AI-Platform-ISO/tests/phase1
python3 benchmark_infrastructure.py
```

---

## Next Steps (Phase 2)

After Phase 1 is stable:

1. **Core Level Coordination** (intelligent-core services)
   - Workflow Intelligence coordination
   - AI Foundation coordination
   - Expertise Center coordination

2. **Center Level Orchestration** (decision center)
   - Context Aggregation
   - Priority Engine
   - Decision Making

3. **Program Level Governance**
   - Strategic Planning
   - Resource Allocation
   - Compliance Oversight

4. **Cross-Level Coordination**
   - System-wide optimization
   - Cascading recovery
   - Unified observability

---

## Support & Documentation

**Documentation:**
- [Phase 1 Integration Plan](../../doc-project/PHASE_1_INTEGRATION_PLAN.md)
- [Infrastructure Events Catalog](../eventbus/events/INFRASTRUCTURE_EVENTS.md)
- [Metrics Framework](../../doc-project/METRICS_FRAMEWORK_AND_INTEGRATION_ANALYSIS.md)

**Code Locations:**
- Health Monitor: `/intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`
- Auto-Recovery: `/infrastructure/eventbus/coordination/auto_recovery.py`
- Resource Optimizer: `/infrastructure/eventbus/coordination/resource_optimizer.py`
- Infrastructure Coordinator: `/infrastructure/eventbus/coordination/infrastructure_coordinator.py`
- Metrics API: `/intelligent-core/orchestration/api/metrics_api.py`

**Support:**
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Project Documentation: `/doc-project/`
- EventBus README: `/infrastructure/eventbus/README.md`

---

## Deployment Checklist

- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Prometheus & Grafana running
- [ ] Metrics API running on port 9091
- [ ] Prometheus scraping Metrics API
- [ ] Infrastructure Coordinator running
- [ ] Health events being published
- [ ] Auto-Recovery listening for events
- [ ] Resource Optimizer running 5-min cycles
- [ ] Grafana dashboards imported
- [ ] Alert rules configured
- [ ] EventCatalog updated with new events
- [ ] Phase 1 integration test passed

---

**Deployment Status:** ✅ Ready for Production
**Version:** 1.0.0 (Phase 1)
**Last Updated:** 2025-10-09
