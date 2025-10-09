# Port Map для Phase 1: Infrastructure Integration

**Date:** 2025-10-09
**Purpose:** Карта портов для Phase 1 интеграции
**Source:** [PORT_ALLOCATION.md](../platform-services/PORT_ALLOCATION.md)

---

## 🎯 CRITICAL INFRASTRUCTURE PORTS (Phase 1)

### Infrastructure Layer (Always Running)

| Port | Service | Purpose | Health Check | Metrics | Status |
|------|---------|---------|--------------|---------|--------|
| **5432** | PostgreSQL | Primary Database | - | - | ✅ External (RDS/Supabase) |
| **6379** | Redis | Cache & EventBus backend | - | - | ✅ External (ElastiCache) |
| **6333** | Qdrant | Vector Database (RAG) | http://localhost:6333/health | - | ✅ External (Qdrant Cloud) |
| **9090** | Prometheus | Metrics Collection | http://localhost:9090/-/healthy | http://localhost:9090/metrics | ⏳ To Deploy |
| **3000** | Grafana | Metrics Visualization | http://localhost:3000/api/health | - | ⏳ To Deploy |

### EventBus & Coordination (NEW - Phase 1)

| Port | Service | Purpose | Health Check | Metrics | Status |
|------|---------|---------|--------------|---------|--------|
| **8055** | ai-event-manager | Event Management API | http://localhost:8055/health | http://localhost:8055/metrics | ✅ Exists |
| **8090** | Unified Orchestrator | Infrastructure Orchestration | http://localhost:8090/health | http://localhost:8090/metrics | ⚠️ Exists (Raw) |
| **9091** | Metrics API | Prometheus Metrics Endpoint | http://localhost:9091/health | http://localhost:9091/metrics | ⏳ To Create (Phase 1 Task 1.5) |

---

## 📊 PLATFORM SERVICES (BCM Core)

### BCM Core Services (Active)

| Port | Service | ISO Clause | Health Check | Metrics | Status |
|------|---------|------------|--------------|---------|--------|
| **8011** | Planning Service | 8.3 | http://localhost:8011/health | http://localhost:8011/metrics | ✅ Active |
| **8012** | BIA Service | 8.2.2 | http://localhost:8012/health | http://localhost:8012/metrics | ✅ Active |
| **8013** | Governance Service | 4, 5 | http://localhost:8013/health | http://localhost:8013/metrics | ✅ Active |
| **8014** | Compliance Service | 9.2, 10.1, 10.2 | http://localhost:8014/health | http://localhost:8014/metrics | ✅ Active |
| **8021** | Learning Service | 7.2, 7.3 | http://localhost:8021/health | http://localhost:8021/metrics | ✅ Active |
| **8022** | Validation Service | 8.5, 9.1-9.3, 10 | http://localhost:8022/health | http://localhost:8022/metrics | ✅ Active |
| **8023** | Plans Service | 8.4 | http://localhost:8023/health | http://localhost:8023/metrics | ✅ Active |
| **8024** | Documents Service | 7.5 | http://localhost:8024/health | http://localhost:8024/metrics | ✅ Active |
| **8040** | Risk Service | 8.2.3 | http://localhost:8040/health | http://localhost:8040/metrics | ✅ Active |
| **8041** | Response Service | 8.4.5 | http://localhost:8041/health | http://localhost:8041/metrics | ✅ Active |
| **8070** | BCM Coordination | - | http://localhost:8070/health | http://localhost:8070/metrics | ✅ Active |

---

## 🧠 INTELLIGENT CORE (AI Services)

### Intelligence Services

| Port | Service | Purpose | Health Check | Metrics | Status |
|------|---------|---------|--------------|---------|--------|
| **8020** | AI Foundation (RAG/ML) | RAG, LLM, ML Models | http://localhost:8020/health | http://localhost:8020/metrics | ✅ Active |
| **8030** | AI Orchestrator | 6-step cognitive loop | http://localhost:8030/health | http://localhost:8030/metrics | ⏳ Phase 2 (интеграция через EventBus) |
| **8031** | Simulation Main | Scenario simulation | http://localhost:8031/health | http://localhost:8031/metrics | ✅ Active |
| **8034** | Living Docs | Dynamic documentation | http://localhost:8034/health | http://localhost:8034/metrics | ✅ Active |
| **8035** | Expertise Center | Expert agents | http://localhost:8035/health | http://localhost:8035/metrics | ⏳ Phase 3 |
| **8036** | Workflow Engine | Workflow execution | http://localhost:8036/health | http://localhost:8036/metrics | ✅ Active |
| **8037** | Workflow Intelligence | Workflow analytics | http://localhost:8037/health | http://localhost:8037/metrics | ⏳ Phase 2 |
| **8082** | BIA Engine (Simulation) | BIA simulation | http://localhost:8082/health | http://localhost:8082/metrics | ✅ Active |
| **8085** | Scenario Orchestrator | Scenario management | http://localhost:8085/health | http://localhost:8085/metrics | ✅ Active |

### Community & Collective

| Port | Service | Purpose | Health Check | Metrics | Status |
|------|---------|---------|--------------|---------|--------|
| **8032** | Collective Intelligence | k-anonymity intelligence | http://localhost:8032/health | http://localhost:8032/metrics | ⏳ Phase 3 |
| **8033** | Community Portal | Community collaboration | http://localhost:8033/health | http://localhost:8033/metrics | ✅ Active |

---

## 📈 MONITORING & OBSERVABILITY

### Monitoring Services

| Port | Service | Purpose | Health Check | Metrics | Status |
|------|---------|---------|--------------|---------|--------|
| **8045** | Compliance Monitoring | Compliance metrics | http://localhost:8045/health | http://localhost:8045/metrics | ✅ Active |
| **8780** | Process Analytics | Process mining | http://localhost:8780/health | http://localhost:8780/metrics | ✅ Active |

---

## 🔧 PHASE 1 SPECIFIC CONFIGURATION

### Services to Monitor in Phase 1

**Critical Infrastructure (RTO = 30 sec):**
```python
critical_services = {
    'eventbus': {
        'port': 8055,  # ai-event-manager
        'check_type': 'http',
        'interval': 30,
        'rto': 30,
        'rpo': 0
    },
    'database': {
        'port': 5432,
        'check_type': 'custom',  # PostgreSQL check
        'interval': 60,
        'rto': 300,
        'rpo': 60
    },
    'redis': {
        'port': 6379,
        'check_type': 'custom',  # Redis PING
        'interval': 30,
        'rto': 60,
        'rpo': 0
    },
    'api_gateway': {
        'port': 8000,
        'check_type': 'http',
        'interval': 30,
        'rto': 60,
        'rpo': 5
    },
    'rag_pipeline': {
        'port': 8020,  # AI Foundation
        'check_type': 'http',
        'interval': 60,
        'rto': 600,
        'rpo': 300
    }
}
```

### Auto-Recovery Strategies

```python
recovery_strategies = {
    'eventbus': {
        'strategy_type': 'restart',
        'max_attempts': 3,
        'backoff_seconds': 5
    },
    'database': {
        'strategy_type': 'circuit_breaker',  # Don't restart DB!
        'max_attempts': 1,
        'backoff_seconds': 30
    },
    'redis': {
        'strategy_type': 'restart',
        'max_attempts': 3,
        'backoff_seconds': 5
    },
    'api_gateway': {
        'strategy_type': 'restart',
        'max_attempts': 3,
        'backoff_seconds': 10
    },
    'rag_pipeline': {
        'strategy_type': 'restart',
        'max_attempts': 2,
        'backoff_seconds': 15
    }
}
```

---

## 🌐 NETWORK CONFIGURATION

### Docker Network (Development)

```yaml
networks:
  bcm-platform:
    driver: bridge
    name: bcm-platform
```

### Internal Service Communication

```bash
# Services communicate via container names:
http://ai-event-manager:8055
http://bcm-bia-service:8012
http://bcm-planning-service:8011
http://postgres:5432
http://redis:6379
```

### External Access (from host)

```bash
# All services accessible via localhost:
http://localhost:8055  # ai-event-manager
http://localhost:8012  # BIA Service
http://localhost:8011  # Planning Service
```

---

## 🧪 HEALTH CHECK COMMANDS (Phase 1)

### Test Infrastructure

```bash
# EventBus (ai-event-manager)
curl http://localhost:8055/health

# Database (via custom check)
psql -h localhost -U postgres -d ai_platform_prod -c "SELECT 1"

# Redis
redis-cli -h localhost -p 6379 PING

# Qdrant
curl http://localhost:6333/health
```

### Test All Critical Services

```bash
#!/bin/bash
# test_phase1_infrastructure.sh

services=(
    "8055:ai-event-manager"
    "8012:bia-service"
    "8020:ai-foundation"
    "8011:planning-service"
)

for service in "${services[@]}"; do
    port="${service%%:*}"
    name="${service##*:}"

    echo -n "Testing $name ($port): "
    if curl -s -f http://localhost:$port/health > /dev/null; then
        echo "✅ HEALTHY"
    else
        echo "❌ UNHEALTHY"
    fi
done
```

---

## 📊 PROMETHEUS SCRAPE CONFIGURATION

### prometheus.yml для Phase 1

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'ai-platform-dev'
    environment: 'development'

scrape_configs:
  # Infrastructure
  - job_name: 'ai-event-manager'
    static_configs:
      - targets: ['ai-event-manager:8055']
    metrics_path: '/metrics'

  # Metrics API (new in Phase 1)
  - job_name: 'metrics-api'
    static_configs:
      - targets: ['localhost:9091']
    metrics_path: '/metrics'

  # BCM Core Services
  - job_name: 'bia-service'
    static_configs:
      - targets: ['bia-service:8012']

  - job_name: 'planning-service'
    static_configs:
      - targets: ['planning-service:8011']

  - job_name: 'ai-foundation'
    static_configs:
      - targets: ['ai-foundation:8020']

  # Database (via exporter)
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis (via exporter)
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

---

## 🚀 PHASE 1 DEPLOYMENT SEQUENCE

### 1. Infrastructure (External Services)

```bash
# Already running (external):
# - PostgreSQL (Supabase) - port 5432
# - Redis (ElastiCache or local) - port 6379
# - Qdrant (Qdrant Cloud) - port 6333

# Verify connectivity:
psql -h <supabase-host> -U postgres -d postgres -c "SELECT version();"
redis-cli -h <redis-host> PING
curl http://localhost:6333/health
```

### 2. EventBus & Coordination

```bash
# Start ai-event-manager (если ещё не запущен)
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
docker-compose up -d

# Verify
curl http://localhost:8055/health
```

### 3. Deploy Infrastructure Coordinator (NEW - Phase 1)

```bash
# Deploy Infrastructure Coordinator
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus/coordination
python -m infrastructure_coordinator

# Starts:
# - Health Monitor (30 sec cycle)
# - Auto-Recovery (event-driven)
# - Resource Optimizer (5 min cycle)
```

### 4. Deploy Metrics API (NEW - Phase 1)

```bash
# Start Metrics API
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration
python -m api.metrics_api

# Runs on port 9091
# Prometheus scrapes http://localhost:9091/metrics
```

### 5. Deploy Prometheus & Grafana

```bash
# Start Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Start Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

### 6. Verify Phase 1 Integration

```bash
# Run integration test
cd /Users/MD/AI-Platform-ISO
pytest tests/integration/test_phase1_infrastructure.py

# Expected output:
# ✅ Health Monitor running
# ✅ Auto-Recovery ready
# ✅ Resource Optimizer running
# ✅ Metrics exported
```

---

## 🔍 TROUBLESHOOTING

### Port Conflicts

```bash
# Check if port is in use
lsof -i :8055
lsof -i :9091

# Kill process on port
kill -9 $(lsof -ti :8055)
```

### Service Not Responding

```bash
# Check Docker logs
docker logs ai-event-manager
docker logs bcm-bia-service

# Check service is running
docker ps | grep ai-event-manager

# Test health endpoint
curl -v http://localhost:8055/health
```

### EventBus Issues

```bash
# Check Redis connectivity
redis-cli -h localhost -p 6379 PING

# Check EventBus events
redis-cli -h localhost -p 6379 MONITOR

# Subscribe to events
redis-cli -h localhost -p 6379 PSUBSCRIBE "infrastructure.*"
```

---

## 📈 SUCCESS METRICS (Phase 1)

### Infrastructure Health

```bash
# All services should return healthy:
curl http://localhost:8055/health  # ai-event-manager
curl http://localhost:8012/health  # BIA Service
curl http://localhost:8020/health  # AI Foundation

# Prometheus should scrape all targets:
curl http://localhost:9090/api/v1/targets

# Metrics API should expose metrics:
curl http://localhost:9091/metrics
```

### Auto-Recovery Test

```bash
# Simulate failure (stop a service)
docker stop bcm-bia-service

# Should see in logs:
# - Health Monitor detects unhealthy
# - Auto-Recovery triggered
# - Service restarted
# - Health Monitor confirms healthy

# Check recovery stats
curl http://localhost:8055/api/recovery/stats
```

---

## 🎯 NEXT STEPS (After Phase 1)

### Phase 2: Core Integration (Week 2)
- Integrate AI Orchestrator (port 8030) with EventBus
- Add Core Coordinator for event_intelligence (port 8037)
- Learning Cycle (24h) implementation

### Phase 3: Center Integration (Week 3)
- Expert Coordinator (port 8035)
- Collective Intelligence (port 8032) with k=5
- Community Learning

### Phase 4: Program Integration (Week 4)
- Program Coordinator
- Virtuous Cycle (7 days)
- System BCM Self-Application

---

**Document Version:** 1.0.0
**Phase:** Phase 1 - Infrastructure Integration
**Related:**
- [PHASE_1_INTEGRATION_PLAN.md](PHASE_1_INTEGRATION_PLAN.md)
- [METRICS_FRAMEWORK_AND_INTEGRATION_ANALYSIS.md](METRICS_FRAMEWORK_AND_INTEGRATION_ANALYSIS.md)
- [PORT_ALLOCATION.md](../platform-services/PORT_ALLOCATION.md)
