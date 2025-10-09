# System BCM - Platform Integration Guide

**Generated**: 2025-10-09
**Platform Version**: 2.0.0
**System BCM Version**: 1.0.0
**Status**: ✅ Ready for Integration

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Platform Architecture](#platform-architecture)
3. [Integration Points](#integration-points)
4. [Quick Start](#quick-start)
5. [Configuration](#configuration)
6. [EventBus Integration](#eventbus-integration)
7. [Service Discovery](#service-discovery)
8. [Health Monitoring](#health-monitoring)
9. [Recovery Procedures](#recovery-procedures)
10. [Validation](#validation)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

System BCM is a **self-application BCM service** that applies Business Continuity Management to the AI-Platform-ISO itself. It learns through practice by:

1. **Applying BCM to Platform** - Executes BIA, Risk Assessment, Recovery Setup for platform infrastructure
2. **Learning from Practice** - Measures real RTO/RPO, effectiveness metrics
3. **Auto-Recovery** - Triggers recovery procedures when platform services fail
4. **Pattern Detection** - Learns from behavioral patterns and improves over time

### Key Capabilities

- ✅ **Platform BIA** - Analyzes 7 critical processes (EventBus, DB, Gateway, Workflows, etc.)
- ✅ **Risk Assessment** - Monitors 12 platform risks (memory leaks, cascade failures, etc.)
- ✅ **Auto-Recovery** - 7 automated recovery procedures (30s - 15m RTO)
- ✅ **Resource Priorities** - 3-tier resource allocation (critical/important/optional)
- ✅ **Practice Learning** - Learns from actual execution, not theory
- ✅ **EventBus Integration** - Subscribes to platform events, publishes BCM events
- ✅ **Prometheus Metrics** - 20+ metrics for monitoring
- ✅ **Grafana Dashboard** - Real-time visualization

---

## 🏗 Platform Architecture

### Platform Layers

```
┌─────────────────────────────────────────────────────────┐
│ 4. Integration Layer                                    │
│ • API Gateway (8000)                                    │
│ • EventBus (Redis 6379, RabbitMQ 5672)                 │
│ • WebSocket                                             │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ 3. Platform Services Layer (12 services: 8001-8012)    │
│ • BIA, Risk, Compliance, Planning, Response, etc.      │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ 2. Intelligent Core Layer (11 modules: 8031-8050)      │
│ • AI Foundation, Workflow Intelligence, Expertise, etc. │
│ • SYSTEM BCM SERVICE (8050) ← YOU ARE HERE              │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ 1. Infrastructure Layer                                 │
│ • PostgreSQL (5432), Redis (6379), Qdrant (6333)       │
│ • Prometheus (9090), Grafana (3000), Vault (8200)      │
└─────────────────────────────────────────────────────────┘
```

### System BCM Position

System BCM sits in the **Intelligent Core Layer** and:

- **Monitors** all layers (Infrastructure → Integration)
- **Subscribes** to platform events (health degraded, service failed, etc.)
- **Publishes** BCM events (cycle completed, recovery triggered, insights generated)
- **Coordinates** with other intelligent modules (Workflow Intelligence, Expertise Center)
- **Learns** from real platform behavior

---

## 🔗 Integration Points

### Infrastructure Dependencies

| Component | Port | URL | Purpose |
|-----------|------|-----|---------|
| **Redis EventBus** | 6379 | `redis:6379` | Event streaming (CRITICAL - Tier 1) |
| **PostgreSQL** | 5432 | `postgresql:5432` | Data persistence (CRITICAL - Tier 1) |
| **API Gateway** | 8000 | `gateway:8000` | Unified API routing (CRITICAL - Tier 1) |
| **Prometheus** | 9090 | `prometheus:9090` | Metrics collection |
| **Grafana** | 3000 | `grafana:3000` | Dashboards |
| **Qdrant** | 6333 | `qdrant:6333` | Vector DB for RAG |
| **RabbitMQ** | 5672 | `rabbitmq:5672` | Message queue |
| **Vault** | 8200 | `vault:8200` | Secrets management |

### Platform Services (8001-8012)

| Service | Port | ISO Clause | Integration |
|---------|------|------------|-------------|
| BIA Service | 8001 | 8.2 | EventBus subscriber |
| Risk Service | 8002 | 8.3 | EventBus subscriber |
| Compliance Service | 8003 | 9.1 | EventBus subscriber |
| Planning Service | 8004 | 8.4 | EventBus subscriber |
| Response Service | 8005 | 8.4 | EventBus subscriber |
| Documents Service | 8006 | 7.5 | EventBus subscriber |
| Governance Service | 8007 | 5.0 | EventBus subscriber |
| Validation Service | 8008 | 8.5 | EventBus subscriber |
| Learning Service | 8009 | 7.3 | EventBus subscriber |
| BCM Coordination | 8010 | - | EventBus subscriber |
| Community Service | 8011 | - | EventBus subscriber |
| Monitoring Service | 8012 | 9.0 | EventBus subscriber |

### Intelligent Modules (8031-8050)

| Module | Port | Integration |
|--------|------|-------------|
| Predictive | 8031 | EventBus subscriber |
| Collective | 8032 | EventBus subscriber |
| Expertise Center | 8036 | EventBus subscriber + AI Foundation |
| Workflow Intelligence | 8037 | EventBus subscriber + Temporal Cloud |
| Community Intelligence | 8038 | EventBus subscriber |
| Event Intelligence | 8039 | EventBus subscriber |
| Workflow Engine | 8041 | EventBus subscriber |
| **System BCM** | **8050** | **EventBus publisher + subscriber** |

---

## 🚀 Quick Start

### Option 1: Automated Integration

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service

# Run integration script
./integrate-with-platform.sh
```

This script will:
1. Check Docker and platform_network
2. Discover running platform services
3. Build and deploy System BCM
4. Verify integration
5. Trigger first BCM cycle

### Option 2: Manual Integration

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service

# 1. Create platform_network (if not exists)
docker network create platform_network

# 2. Check configuration
cat .env

# 3. Build and start
docker-compose up -d

# 4. Verify health
curl http://localhost:8050/health

# 5. Trigger first cycle
curl -X POST http://localhost:8050/cycle/trigger
```

### Option 3: Development Mode

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export REDIS_HOST=localhost
export LOG_LEVEL=DEBUG

# 3. Run directly
python3 main.py
```

---

## ⚙️ Configuration

### Environment Variables

The `.env` file contains 100+ configuration parameters. Key sections:

#### Critical Settings

```bash
# Service
SERVICE_PORT=8050

# EventBus (CRITICAL)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_STREAM_PREFIX=platform

# Scheduler
CYCLE_INTERVAL_HOURS=24
RUN_FIRST_CYCLE_ON_STARTUP=true

# Auto-Recovery
AUTO_RECOVERY_ENABLED=true
MAX_RECOVERY_ATTEMPTS=3
RECOVERY_TIMEOUT=300
```

#### Platform Services URLs

All 12 platform services are configured:

```bash
BIA_SERVICE_URL=http://bia-service:8001
RISK_SERVICE_URL=http://risk-service:8002
COMPLIANCE_SERVICE_URL=http://compliance-service:8003
# ... (see .env for full list)
```

#### Intelligent Modules URLs

All intelligent core modules:

```bash
PREDICTIVE_SERVICE_URL=http://predictive:8031
COLLECTIVE_SERVICE_URL=http://collective:8032
EXPERTISE_CENTER_URL=http://expertise-center:8036
WORKFLOW_INTELLIGENCE_URL=http://workflow-intelligence:8037
# ... (see .env for full list)
```

#### Monitored Services

System BCM monitors these services:

```bash
MONITORED_SERVICES=bia-service,risk-service,compliance-service,planning-service,response-service,documents-service,governance-service,validation-service,learning-service,bcm-coordination-service,community-service,monitoring,predictive,collective,expertise-center,workflow-intelligence,community-intelligence,event-intelligence,workflow-engine
```

#### Critical Services (Tier 1)

These services are critical for platform survival:

```bash
CRITICAL_SERVICES=redis,postgresql,eventbus,gateway,workflow-intelligence
CRITICAL_SERVICE_RTO=30  # seconds
CRITICAL_SERVICE_RPO=0   # seconds
```

---

## 📡 EventBus Integration

### Event Subscriptions (System BCM listens to)

System BCM subscribes to these platform events:

```python
# Health Degradation
@eventbus.subscribe("platform.health.degraded")
async def on_health_degraded(event):
    # Trigger health check and recovery if needed
    await trigger_recovery_check(event.data)

# Service Failure
@eventbus.subscribe("platform.service.failed")
async def on_service_failed(event):
    # Trigger emergency recovery
    await trigger_emergency_recovery(event.data)

# Resource Contention
@eventbus.subscribe("platform.resource.contention")
async def on_resource_contention(event):
    # Apply resource priorities
    await apply_resource_priorities(event.data)

# Cascade Risk
@eventbus.subscribe("platform.cascade.risk")
async def on_cascade_risk(event):
    # Trigger cascade failure prevention
    await prevent_cascade_failure(event.data)
```

### Event Publications (System BCM publishes)

System BCM publishes these events:

```python
# BCM Cycle Events
await eventbus.publish("platform.bcm.cycle.started", {
    "cycle_id": "cycle_001",
    "timestamp": "2025-10-09T12:00:00Z"
})

await eventbus.publish("platform.bcm.cycle.completed", {
    "cycle_id": "cycle_001",
    "phases": ["bia", "risk_assessment", "recovery_setup", "priority_application"],
    "insights_generated": 5,
    "improvements_applied": 2
})

# Recovery Events
await eventbus.publish("platform.bcm.recovery.triggered", {
    "service": "redis",
    "incident_type": "connection_pool_exhausted",
    "procedure": "restart_with_pool_increase"
})

await eventbus.publish("platform.bcm.recovery.completed", {
    "service": "redis",
    "duration_seconds": 25,
    "rto_met": true
})

# Learning Events
await eventbus.publish("platform.bcm.insight.generated", {
    "insight_type": "pattern_detected",
    "description": "Memory usage spikes every 6 hours",
    "confidence": 0.85,
    "recommended_action": "increase_memory_limit"
})
```

### Event Schema

All events follow this schema:

```json
{
  "event_type": "platform.bcm.cycle.completed",
  "timestamp": "2025-10-09T12:00:00Z",
  "source": "system-bcm-service",
  "data": {
    "cycle_id": "cycle_001",
    "phases": ["bia", "risk_assessment", "recovery_setup", "priority_application"],
    "insights_generated": 5
  },
  "metadata": {
    "platform_version": "2.0.0",
    "system_bcm_version": "1.0.0"
  }
}
```

---

## 🔍 Service Discovery

System BCM automatically discovers platform services:

### Discovery Methods

1. **Docker Network Discovery**
   ```python
   # Discovers all containers in platform_network
   services = discover_services_in_network("platform_network")
   ```

2. **Port-Based Discovery**
   ```python
   # Scans known ports (8001-8012, 8031-8050)
   services = scan_platform_ports()
   ```

3. **Health Endpoint Polling**
   ```python
   # Polls /health endpoints
   healthy_services = poll_health_endpoints(services)
   ```

### Service Registry

System BCM maintains a service registry:

```json
{
  "bia-service": {
    "url": "http://bia-service:8001",
    "health": "healthy",
    "last_check": "2025-10-09T12:00:00Z",
    "tier": "important",
    "rto": "5m",
    "rpo": "1h"
  },
  "redis": {
    "url": "redis:6379",
    "health": "healthy",
    "last_check": "2025-10-09T12:00:00Z",
    "tier": "critical",
    "rto": "30s",
    "rpo": "0s"
  }
}
```

---

## 💚 Health Monitoring

### Health Check Strategy

System BCM monitors platform health at 3 levels:

#### 1. Infrastructure Health (Tier 1 - Critical)

```python
# Redis EventBus
health_checks["redis"] = {
    "method": "ping",
    "interval": 30,  # seconds
    "timeout": 5,
    "threshold": 3  # failures before alert
}

# PostgreSQL
health_checks["postgresql"] = {
    "method": "query",
    "query": "SELECT 1",
    "interval": 30,
    "timeout": 5
}
```

#### 2. Service Health (Tier 2 - Important)

```python
# Platform Services
for service in platform_services:
    health_checks[service] = {
        "method": "http_get",
        "endpoint": f"http://{service}:port/health",
        "interval": 60,
        "timeout": 10
    }
```

#### 3. Module Health (Tier 2/3 - Important/Optional)

```python
# Intelligent Modules
for module in intelligent_modules:
    health_checks[module] = {
        "method": "http_get",
        "endpoint": f"http://{module}:port/health",
        "interval": 120,
        "timeout": 15
    }
```

### Health Metrics

System BCM tracks these health metrics:

```python
# Availability
system_bcm_service_available{service="redis"} 1.0
system_bcm_service_available{service="postgresql"} 1.0

# Response Time
system_bcm_service_response_time{service="bia-service"} 0.250

# Error Rate
system_bcm_service_error_rate{service="risk-service"} 0.01

# Resource Usage
system_bcm_service_cpu_percent{service="workflow-intelligence"} 45.2
system_bcm_service_memory_percent{service="expertise-center"} 38.7
```

---

## 🔧 Recovery Procedures

### Auto-Recovery Triggers

System BCM triggers recovery when:

1. **Service Failed** - Service health check fails 3 times
2. **Health Degraded** - Service response time > 2x normal
3. **Resource Contention** - CPU/Memory > threshold
4. **Cascade Risk Detected** - Dependencies failing

### Recovery Procedures (7 Total)

#### 1. EventBus Recovery (RTO: 30s)

```yaml
procedure: eventbus_recovery
trigger: Redis connection failed
steps:
  1. Clear connection pool
  2. Reinitialize Redis client
  3. Restore stream subscriptions
  4. Verify event flow
expected_rto: 30s
```

#### 2. Database Pool Recovery (RTO: 2m)

```yaml
procedure: db_pool_recovery
trigger: PostgreSQL connection pool exhausted
steps:
  1. Close idle connections
  2. Increase pool size (+50%)
  3. Restart connection pool
  4. Verify queries working
expected_rto: 2m
```

#### 3. Service Restart (RTO: 5m)

```yaml
procedure: service_restart
trigger: Service health check failed 3x
steps:
  1. Log failure details
  2. Execute graceful shutdown
  3. Wait 10s cooldown
  4. Start service
  5. Verify health endpoint
expected_rto: 5m
```

#### 4. Memory Leak Mitigation (RTO: 10m)

```yaml
procedure: memory_leak_mitigation
trigger: Memory usage > 90%
steps:
  1. Trigger garbage collection
  2. Clear caches
  3. If still high: rolling restart
  4. Monitor memory trend
expected_rto: 10m
```

#### 5. Cascade Failure Prevention (RTO: 15m)

```yaml
procedure: cascade_prevention
trigger: 2+ dependent services failing
steps:
  1. Identify dependency chain
  2. Isolate failing service (circuit breaker)
  3. Route traffic to healthy replicas
  4. Restart failed service
  5. Gradually restore traffic
expected_rto: 15m
```

#### 6. Connection Pool Exhaustion (RTO: 3m)

```yaml
procedure: connection_pool_recovery
trigger: "Too many connections" error
steps:
  1. Kill long-running queries
  2. Close idle connections
  3. Increase max connections
  4. Verify new connections work
expected_rto: 3m
```

#### 7. Disk Space Recovery (RTO: 10m)

```yaml
procedure: disk_space_recovery
trigger: Disk usage > 85%
steps:
  1. Identify large log files
  2. Rotate logs
  3. Clear old backups
  4. Compress archives
  5. Verify space available
expected_rto: 10m
```

### Recovery Execution Flow

```python
async def execute_recovery(service: str, incident_type: str):
    """Executes recovery procedure"""

    # 1. Select procedure
    procedure = select_recovery_procedure(service, incident_type)

    # 2. Notify observers
    await eventbus.publish("platform.bcm.recovery.triggered", {
        "service": service,
        "incident_type": incident_type,
        "procedure": procedure.name
    })

    # 3. Execute steps
    start_time = time.time()
    for step in procedure.steps:
        await execute_step(step)

    duration = time.time() - start_time

    # 4. Verify success
    success = await verify_service_health(service)

    # 5. Notify completion
    await eventbus.publish("platform.bcm.recovery.completed", {
        "service": service,
        "duration_seconds": duration,
        "rto_met": duration <= procedure.rto,
        "success": success
    })

    # 6. Learn from execution
    await practice_learning.learn_from_recovery(
        service=service,
        procedure=procedure,
        duration=duration,
        success=success
    )

    return success
```

---

## ✅ Validation

### Deployment Validation

Run comprehensive validation:

```bash
./validate-deployment.sh
```

This runs 40+ automated tests:

- **Phase 1**: Infrastructure (Docker, network, dependencies)
- **Phase 2**: Service Availability (ports, containers)
- **Phase 3**: API Endpoints (health, status, metrics)
- **Phase 4**: Scenarios (JSON validation)
- **Phase 5**: Functional Tests (cycle execution)
- **Phase 6**: EventBus Integration
- **Phase 7**: Monitoring Stack (Prometheus, Grafana)
- **Phase 8**: Performance (cycle time, resource usage)

Expected output:

```
Tests run:    42
Tests passed: 42
Tests failed: 0

Success rate: 100%

╔═══════════════════════════════════════════════════════╗
║  ✅ DEPLOYMENT VALIDATION SUCCESSFUL                  ║
║  System BCM Service is fully operational!            ║
╚═══════════════════════════════════════════════════════╝
```

### Health Check

Quick health check:

```bash
./health-check.sh
```

Checks:
- Docker daemon
- System BCM service (5 checks)
- EventBus (3 checks)
- Monitoring (4 checks)
- Platform services
- Functionality (4 checks)
- Resources

---

## 🐛 Troubleshooting

### Issue 1: Service Won't Start

**Symptoms:**
- `docker-compose up -d` fails
- Container exits immediately

**Diagnosis:**
```bash
# Check logs
docker-compose logs system-bcm

# Check container status
docker ps -a | grep system-bcm

# Check resource usage
docker stats --no-stream
```

**Solutions:**
1. Check `.env` configuration
2. Verify platform_network exists: `docker network ls`
3. Check Redis is running: `docker ps | grep redis`
4. Verify scenarios directory: `ls -la scenarios/`
5. Check port 8050 not in use: `lsof -i :8050`

---

### Issue 2: EventBus Not Connected

**Symptoms:**
- Service running but no events
- Errors in logs: "Redis connection failed"

**Diagnosis:**
```bash
# Test Redis connection
docker exec system-bcm-service redis-cli -h redis ping

# Check Redis container
docker ps | grep redis

# Check network
docker network inspect platform_network
```

**Solutions:**
1. Verify REDIS_HOST in `.env` (should be `redis`)
2. Ensure Redis container is on platform_network
3. Check Redis port: `docker port <redis_container>`
4. Restart System BCM: `docker-compose restart system-bcm`

---

### Issue 3: BCM Cycle Fails

**Symptoms:**
- Cycle trigger returns error
- Cycle never completes

**Diagnosis:**
```bash
# Trigger cycle manually
curl -X POST http://localhost:8050/cycle/trigger

# Check service logs
docker-compose logs -f system-bcm

# Check scenarios
ls -la scenarios/
jq empty scenarios/platform_bia.json
```

**Solutions:**
1. Verify all 4 scenario files exist and are valid JSON
2. Check service has read access to scenarios/
3. Increase timeout: `RECOVERY_TIMEOUT=600` in .env
4. Run in debug mode: `LOG_LEVEL=DEBUG`

---

### Issue 4: Metrics Not Appearing

**Symptoms:**
- Prometheus not scraping metrics
- Grafana dashboard empty

**Diagnosis:**
```bash
# Check metrics endpoint
curl http://localhost:8050/metrics | grep system_bcm

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq

# Check Prometheus config
docker exec system-bcm-prometheus cat /etc/prometheus/prometheus.yml
```

**Solutions:**
1. Verify `prometheus.yml` has system-bcm job
2. Check port 8050 accessible from Prometheus container
3. Restart Prometheus: `docker-compose restart prometheus`
4. Wait 1 minute for first scrape

---

### Issue 5: Auto-Recovery Not Triggering

**Symptoms:**
- Service fails but no recovery
- No recovery events in logs

**Diagnosis:**
```bash
# Check auto-recovery setting
grep AUTO_RECOVERY_ENABLED .env

# Check event subscriptions
docker-compose logs system-bcm | grep "Subscribed to"

# Trigger test event
redis-cli XADD platform.service.failed * service test error "test failure"
```

**Solutions:**
1. Enable auto-recovery: `AUTO_RECOVERY_ENABLED=true`
2. Verify EventBus connection (see Issue 2)
3. Check recovery timeout not too short
4. Review recovery procedure logs

---

## 📚 Additional Resources

### Documentation

- [SYSTEM_BCM_LAUNCH.md](SYSTEM_BCM_LAUNCH.md) - Quick start guide
- [INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md) - Detailed integration steps
- [SYSTEM_BCM_FINAL_SUMMARY.md](SYSTEM_BCM_FINAL_SUMMARY.md) - Complete summary

### Scripts

- `integrate-with-platform.sh` - Automated integration
- `validate-deployment.sh` - Full validation (40+ tests)
- `health-check.sh` - Quick health check

### Platform Documentation

- [Platform Architecture Map](../../docs/PLATFORM_ARCHITECTURE_MAP.md)
- [Platform Map JSON](../../docs/platform-map.json)
- [Comprehensive Platform Docs](../../doc-project/comprehensive-platform-docs/)

### API Reference

- **Health**: `GET /health`
- **Status**: `GET /status`
- **Metrics**: `GET /metrics`
- **Trigger Cycle**: `POST /cycle/trigger`
- **Trigger Recovery**: `POST /recovery/trigger`
- **Get Insights**: `GET /insights`

---

## 🎉 Success Criteria

System BCM is successfully integrated when:

✅ Service is running on port 8050
✅ Health endpoint returns "healthy"
✅ Connected to Redis EventBus
✅ Subscribed to platform events
✅ First BCM cycle completed
✅ Metrics exported to Prometheus
✅ Grafana dashboard showing data
✅ Auto-recovery procedures ready
✅ All 40+ validation tests pass

---

**Integration Guide Complete! 🚀**

Run `./integrate-with-platform.sh` to start integrating!
