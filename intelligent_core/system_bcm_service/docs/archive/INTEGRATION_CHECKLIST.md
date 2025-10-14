# 🔌 System BCM - Platform Integration Checklist

**Цель:** Полная интеграция System BCM Service с живой платформой AI-Platform-ISO

---

## 📋 Pre-Integration Assessment

### Step 1: Inventory Platform Services

```bash
# Найти все запущенные сервисы платформы
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

# Или для Kubernetes
kubectl get pods -n platform -o wide
```

**Заполнить:**
- [ ] API Gateway: `_____:____` (обычно 8000)
- [ ] Workflow Intelligence: `_____:____` (обычно 8001)
- [ ] PostgreSQL: `_____:____` (обычно 5432)
- [ ] Redis (EventBus): `_____:____` (обычно 6379)
- [ ] RAG Service: `_____:____` (обычно 8002)
- [ ] Qdrant: `_____:____` (обычно 6333)
- [ ] Analytics Specialist: `_____:____`
- [ ] Monitoring Stack: `_____:____` (Prometheus 9090, Grafana 3000)

### Step 2: Check Network Configuration

```bash
# Проверить существование platform_network
docker network ls | grep platform_network

# Если нет - создать
docker network create platform_network

# Проверить какие контейнеры в сети
docker network inspect platform_network
```

**Status:**
- [ ] `platform_network` exists
- [ ] All platform services are in `platform_network`

### Step 3: Verify EventBus (Redis)

```bash
# Проверить Redis
docker exec -it <redis-container> redis-cli ping

# Проверить streams
docker exec -it <redis-container> redis-cli XINFO GROUPS platform.health.degraded

# Проверить consumers
docker exec -it <redis-container> redis-cli XINFO CONSUMERS platform.health.degraded system-bcm-group
```

**Status:**
- [ ] Redis is running
- [ ] Redis Streams enabled
- [ ] Event streams exist: `platform.health.*`, `platform.service.*`

---

## 🔧 Integration Steps

### Phase 1: Network Integration

#### 1.1 Connect System BCM to Platform Network

**Edit docker-compose.yml:**
```yaml
networks:
  platform_network:
    external: true  # ✅ Already configured
```

**Verify:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service
docker-compose up -d
docker network inspect platform_network | grep system-bcm
```

**Checklist:**
- [ ] System BCM Service connected to `platform_network`
- [ ] Can ping other services from System BCM container

---

### Phase 2: EventBus Integration

#### 2.1 Configure Redis Connection

**Edit .env:**
```bash
cp .env.example .env
vi .env

# Set Redis host
REDIS_HOST=<actual-redis-container-name>
REDIS_PORT=6379
REDIS_PASSWORD=<if-any>
```

#### 2.2 Verify EventBus Connection

```bash
# Start System BCM
docker-compose up -d system-bcm

# Check logs
docker-compose logs -f system-bcm | grep EventBus

# Expected: "✅ EventBus connected (Redis Streams)"
```

**Checklist:**
- [ ] Redis connection successful
- [ ] Subscribed to platform events
- [ ] Can publish events

#### 2.3 Test Event Flow

**Terminal 1 - Subscribe:**
```bash
docker exec -it <redis-container> redis-cli XREAD BLOCK 0 STREAMS platform.bcm.cycle.completed $
```

**Terminal 2 - Trigger Cycle:**
```bash
curl -X POST http://localhost:8050/cycle/trigger
```

**Terminal 1 - Should see event!**

**Checklist:**
- [ ] Events published successfully
- [ ] Events received by subscribers
- [ ] Event data structure correct

---

### Phase 3: Service Discovery Integration

#### 3.1 Update Service URLs in .env

```bash
# Find actual service URLs
docker ps --format "{{.Names}}: {{.Ports}}"

# Update .env
API_GATEWAY_URL=http://<actual-gateway-container>:8000
WORKFLOW_INTELLIGENCE_URL=http://<actual-workflow-container>:8001
RAG_SERVICE_URL=http://<actual-rag-container>:8002
POSTGRES_HOST=<actual-postgres-container>
QDRANT_URL=http://<actual-qdrant-container>:6333
```

#### 3.2 Verify Service Connectivity

```bash
# Test from System BCM container
docker exec system-bcm-service curl http://api-gateway:8000/health
docker exec system-bcm-service curl http://workflow-intelligence:8001/health
docker exec system-bcm-service curl http://rag-service:8002/health
```

**Checklist:**
- [ ] Can reach API Gateway
- [ ] Can reach Workflow Intelligence
- [ ] Can reach RAG Service
- [ ] Can reach PostgreSQL
- [ ] Can reach Qdrant

---

### Phase 4: Monitoring Integration

#### 4.1 Configure Prometheus

**Edit prometheus.yml to scrape platform services:**

```yaml
scrape_configs:
  - job_name: 'platform-services'
    static_configs:
      - targets:
          - '<actual-api-gateway>:8000'
          - '<actual-workflow>:8001'
          - '<actual-rag>:8002'
```

**Reload Prometheus:**
```bash
docker-compose restart prometheus
```

**Verify targets in Prometheus:**
- Open: http://localhost:9090/targets
- Check all services are "UP"

**Checklist:**
- [ ] Prometheus scraping System BCM Service
- [ ] Prometheus scraping all platform services
- [ ] All targets status: UP
- [ ] Metrics appearing in Prometheus

#### 4.2 Configure Grafana Datasource

```bash
# Open Grafana
open http://localhost:3000

# Login: admin/admin
# Navigate to Configuration → Data Sources
# Add Prometheus datasource: http://prometheus:9090
```

**Import Dashboard:**
- Dashboard → Import
- Upload: `grafana/dashboards/system-bcm-dashboard.json`

**Checklist:**
- [ ] Prometheus datasource configured
- [ ] System BCM dashboard imported
- [ ] Dashboards showing data

---

### Phase 5: Recovery Integration

#### 5.1 Enable Docker Socket Access

**For Docker recovery actions:**

```yaml
# Add to docker-compose.yml system-bcm service
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

**Restart:**
```bash
docker-compose up -d system-bcm
```

#### 5.2 Test Recovery Actions

**Simulate failure:**
```bash
# Trigger test recovery
curl -X POST "http://localhost:8050/recovery/trigger?service=test&incident_type=failure"

# Check logs
docker-compose logs -f system-bcm | grep recovery
```

**Checklist:**
- [ ] Docker socket accessible
- [ ] Can list containers
- [ ] Can execute docker commands
- [ ] Recovery procedures execute

---

### Phase 6: Platform Services Event Publishing

#### 6.1 Configure Services to Publish Events

**Each platform service needs to publish:**

```python
# Example for any platform service
from infrastructure.eventbus import create_eventbus, Event

eventbus = create_eventbus('redis')

# On health degradation
await eventbus.publish(Event(
    type="platform.health.degraded",
    data={
        "service": "api-gateway",
        "severity": "warning",
        "metric": "response_time",
        "value": 500,
        "threshold": 200
    }
))

# On service failure
await eventbus.publish(Event(
    type="platform.service.failed",
    data={
        "service": "rag-service",
        "type": "connection_error",
        "error": "Cannot connect to Qdrant"
    }
))

# On resource contention
await eventbus.publish(Event(
    type="platform.resources.contention",
    data={
        "resource_type": "cpu",
        "utilization": 95,
        "threshold": 80
    }
))
```

**Update each service:**
- [ ] API Gateway
- [ ] Workflow Intelligence
- [ ] RAG Service
- [ ] PostgreSQL (via exporter)
- [ ] Analytics Specialist

#### 6.2 Verify Event Flow

```bash
# Monitor all events
docker exec <redis-container> redis-cli MONITOR | grep platform

# Trigger event from service
# Should see event in monitor
```

**Checklist:**
- [ ] Services publishing health events
- [ ] Services publishing failure events
- [ ] Services publishing resource events
- [ ] System BCM receiving events
- [ ] System BCM reacting to events

---

### Phase 7: Database Integration

#### 7.1 Create BCM Metrics Tables

```sql
-- Connect to PostgreSQL
psql -h localhost -U postgres -d platform

-- Create tables for BCM metrics
CREATE TABLE IF NOT EXISTS system_bcm_cycles (
    id SERIAL PRIMARY KEY,
    cycle_number INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds FLOAT,
    status VARCHAR(20),
    insights_count INTEGER,
    improvements_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_bcm_insights (
    id SERIAL PRIMARY KEY,
    cycle_id INTEGER REFERENCES system_bcm_cycles(id),
    category VARCHAR(50),
    observation TEXT,
    recommendation TEXT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_bcm_improvements (
    id SERIAL PRIMARY KEY,
    cycle_id INTEGER REFERENCES system_bcm_cycles(id),
    improvement_id VARCHAR(100) UNIQUE,
    category VARCHAR(50),
    description TEXT,
    priority VARCHAR(20),
    status VARCHAR(20),
    applied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_bcm_recoveries (
    id SERIAL PRIMARY KEY,
    service VARCHAR(100),
    procedure_id VARCHAR(50),
    incident_type VARCHAR(50),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds FLOAT,
    status VARCHAR(20),
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 7.2 Configure Database Connection

**Update .env:**
```bash
POSTGRES_HOST=<actual-postgres-host>
POSTGRES_PORT=5432
POSTGRES_DB=platform
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<actual-password>
```

**Checklist:**
- [ ] Database tables created
- [ ] Connection configured
- [ ] Can write metrics
- [ ] Can read historical data

---

### Phase 8: End-to-End Testing

#### 8.1 Full Cycle Test

```bash
# 1. Start all services
docker-compose up -d

# 2. Verify all healthy
curl http://localhost:8050/health

# 3. Trigger manual cycle
curl -X POST http://localhost:8050/cycle/trigger

# 4. Monitor execution
docker-compose logs -f system-bcm | grep -E "PHASE|✅|❌"

# 5. Verify results
curl http://localhost:8050/status | jq '.last_cycle_result'

# 6. Check Grafana
open http://localhost:3000
```

**Expected output:**
```
✅ BIA executed for 7 critical processes
✅ 8 high-priority risks identified
✅ 7 recovery procedures configured
✅ 10 services prioritized
✅ 3 insights generated
✅ 2 improvements applied
```

**Checklist:**
- [ ] Full cycle completes successfully
- [ ] All 4 BCM phases execute
- [ ] Learning generates insights
- [ ] Improvements applied
- [ ] Metrics in Prometheus
- [ ] Dashboard shows data

#### 8.2 Recovery Test

```bash
# Simulate API Gateway failure
curl -X POST "http://localhost:8050/recovery/trigger?service=api-gateway&incident_type=failure"

# Monitor recovery
docker-compose logs -f system-bcm | grep recovery

# Check recovery was published
docker exec <redis-container> redis-cli XREAD COUNT 1 STREAMS platform.bcm.recovery.completed $
```

**Expected:**
```
🚨 EMERGENCY: api-gateway failed
🔧 Executing recovery for api-gateway
✅ Recovery completed in X.Xs
```

**Checklist:**
- [ ] Recovery triggered
- [ ] Recovery procedure executed
- [ ] Recovery completed successfully
- [ ] Event published
- [ ] Metrics recorded

#### 8.3 Learning Test

```bash
# Run cycle
curl -X POST http://localhost:8050/cycle/trigger

# Get learning results
curl http://localhost:8050/status | jq '.last_cycle_result.learning_results'

# Verify insights
curl http://localhost:8050/status | jq '.last_cycle_result.learning_results.insights_generated'

# Verify improvements
curl http://localhost:8050/status | jq '.last_cycle_result.learning_results.improvements_identified'
```

**Expected:**
- Insights about auto-recovery gaps
- Insights about risk mitigation
- Improvements generated
- High-confidence improvements applied

**Checklist:**
- [ ] Insights generated
- [ ] Improvements identified
- [ ] Critical improvements auto-applied
- [ ] Learning metrics recorded

---

## 🎯 Integration Validation

### Final Checklist

#### Infrastructure
- [ ] All services in same Docker network
- [ ] All services can communicate
- [ ] Redis EventBus operational
- [ ] PostgreSQL accessible
- [ ] Prometheus scraping all targets
- [ ] Grafana dashboards working

#### EventBus
- [ ] System BCM subscribed to platform events
- [ ] System BCM publishes BCM events
- [ ] Platform services publish health events
- [ ] Event flow end-to-end verified

#### Functionality
- [ ] Full BCM cycle works (BIA, Risk, Recovery, Priorities)
- [ ] Learning generates insights
- [ ] Improvements applied automatically
- [ ] Recovery procedures execute
- [ ] Metrics collected

#### Monitoring
- [ ] Prometheus collecting metrics
- [ ] Grafana showing dashboards
- [ ] Alerts configured
- [ ] Health checks passing

#### Production Readiness
- [ ] Logs configured and rotating
- [ ] Error handling tested
- [ ] Graceful shutdown works
- [ ] Auto-restart configured
- [ ] Backup procedures defined

---

## 🚀 Go-Live Checklist

### Pre-Launch
- [ ] All integration tests passing
- [ ] Load testing completed
- [ ] Failover testing completed
- [ ] Documentation updated
- [ ] Team trained

### Launch
- [ ] Deploy to production environment
- [ ] Verify health checks
- [ ] Monitor first cycle execution
- [ ] Verify EventBus integration
- [ ] Check monitoring dashboards

### Post-Launch (First 24 hours)
- [ ] Monitor logs continuously
- [ ] Verify automatic cycles running
- [ ] Check recovery procedures work
- [ ] Validate learning insights
- [ ] Monitor resource usage
- [ ] Check for errors/warnings

### Post-Launch (First Week)
- [ ] Review cycle performance
- [ ] Analyze learning effectiveness
- [ ] Tune alert thresholds
- [ ] Optimize resource allocation
- [ ] Document any issues/resolutions

---

## 📊 Success Metrics

### Week 1
- [ ] 7 successful BCM cycles
- [ ] >10 insights generated
- [ ] >5 improvements applied
- [ ] 0 critical failures
- [ ] >99% service uptime

### Month 1
- [ ] 30 successful BCM cycles
- [ ] >50 insights generated
- [ ] >20 improvements applied
- [ ] Measurable platform resilience improvement
- [ ] Auto-recovery success rate >90%

### Month 3
- [ ] 90 successful BCM cycles
- [ ] Platform RTO reduced by >20%
- [ ] Auto-recovery success rate >95%
- [ ] Zero manual interventions needed
- [ ] Platform availability >99.9%

---

## 🛠️ Troubleshooting Guide

### EventBus Not Connecting
```bash
# Check Redis
docker exec <redis-container> redis-cli ping

# Check network
docker exec system-bcm-service ping redis

# Check logs
docker-compose logs system-bcm | grep EventBus
```

### Recovery Not Triggering
```bash
# Verify event subscription
docker-compose logs system-bcm | grep subscribe

# Test manual trigger
curl -X POST "http://localhost:8050/recovery/trigger?service=test&incident_type=failure"

# Check event flow
docker exec <redis-container> redis-cli MONITOR
```

### Metrics Not Appearing
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check metrics endpoint
curl http://localhost:8050/metrics

# Verify Prometheus config
cat prometheus.yml
```

### Learning Not Generating Insights
```bash
# Check cycle results
curl http://localhost:8050/status | jq '.last_cycle_result'

# Review logs
docker-compose logs system-bcm | grep Learning

# Verify scenarios loaded
docker-compose logs system-bcm | grep "Loaded.*scenario"
```

---

## 📞 Support

**Documentation:**
- Main README: `/intelligent-core/system-bcm-service/README.md`
- Technical Docs: `/intelligent-core/ai-foundation/learning-knowledge/SYSTEM_BCM_README.md`
- Deployment Guide: `/doc-project/SYSTEM_BCM_PRODUCTION_DEPLOYMENT.md`

**Logs:**
- Service: `docker-compose logs -f system-bcm`
- EventBus: `docker exec <redis> redis-cli MONITOR`
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Health Checks:**
- Service: `curl http://localhost:8050/health`
- Status: `curl http://localhost:8050/status`
- Metrics: `curl http://localhost:8050/metrics`

---

**Integration Status:** ⏳ Pending Platform Map
**Last Updated:** 2025-10-09
**Version:** 1.0.0
