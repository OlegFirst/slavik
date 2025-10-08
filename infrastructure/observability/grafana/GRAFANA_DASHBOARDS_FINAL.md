# Grafana Dashboards - Final Configuration

**Date**: 2025-10-07
**Status**: ✅ CLEANED UP & CONFIGURED FOR REAL INFRASTRUCTURE

## Summary

Cleaned up Grafana dashboards structure from **10+ scattered files** to **5 organized dashboards**.

---

## Final Dashboard Structure

```
grafana/
├── dashboards/
│   ├── bcm-platform-overview.json           ← BCM Platform overview
│   ├── infrastructure-health.json           ← Infrastructure metrics
│   ├── intelligent-core-overview.json       ← AI/ML services metrics
│   ├── iso-22301-compliance.json            ← ISO compliance tracking
│   ├── service-performance.json             ← Service performance
│   └── dashboards.backup.20251003/          ← Old backups (archived)
│
config/grafana/
└── provisioning/
    ├── dashboards/
    │   └── dashboards.yml                   ← Single provisioning config
    └── datasources/
        └── datasources.yml                  ← Prometheus datasource
```

---

## Dashboard Details

### 1. **BCM Platform Overview** (`bcm-platform-overview.json`)
**Size**: 14 KB | **Panels**: 12

**Purpose**: High-level platform health and BCM-specific KPIs

**Metrics Required** (each service must export):
```prometheus
# Service Health
up{job="service-name"}

# HTTP Metrics
http_requests_total{job="service-name", method="GET|POST", status="200|500"}
http_request_duration_seconds{job="service-name"}

# BCM-Specific Metrics
bcm_bia_total                          # Total BIA processes
bcm_bia_coverage_percentage            # BIA coverage %
bcm_plans_up_to_date_percentage        # Plans up-to-date %
bcm_incidents_total                    # Total incidents
bcm_training_completion_rate           # Training completion %
bcm_risk_score                         # Risk assessment score
```

**Services Expected**:
- BCM services (planning, bia, compliance, governance, etc.)

---

### 2. **Intelligent Core Overview** (`intelligent-core-overview.json`)
**Size**: 9 KB | **Panels**: 10+

**Purpose**: AI/ML services monitoring - LLM costs, RAG performance, embeddings

**Metrics Required** (ai-foundation and other AI services):
```prometheus
# LLM Metrics
ai_foundation_llm_cost_usd_total{provider="anthropic|openai"}
llm_requests_total{provider="anthropic|openai", model="..."}
llm_request_duration_seconds{provider="...", model="..."}
llm_tokens_used_total{type="prompt|completion", provider="...", model="..."}

# RAG Metrics
rag_search_duration_seconds{collection="...", query_type="hybrid|vector|text"}
rag_search_duration_seconds_bucket{...}  # for histogram
rag_search_duration_seconds_count{...}

# Embeddings Metrics
embeddings_created_total{model="..."}
embeddings_duration_seconds{model="..."}

# Expertise Center
expertise_center_analyzer_calls_total{analyzer_name="..."}
```

**Services Expected**:
- ai-foundation (8030)
- ai-orchestration (8002)
- expertise-center services

**Status**: ⚠️ **REQUIRES** services to implement Prometheus metrics exporters

---

### 3. **Infrastructure Health** (`infrastructure-health.json`)
**Size**: 16 KB | **Panels**: 17

**Purpose**: System-level monitoring (CPU, memory, disk, Docker containers)

**Metrics Source**:
- **Node Exporter** - System metrics (CPU, RAM, disk)
- **cAdvisor** - Container metrics
- **Postgres Exporter** - Database metrics (if installed)
- **Redis Exporter** - Redis metrics (if installed)

**Metrics Used**:
```prometheus
# Node Exporter (system metrics)
node_cpu_seconds_total
node_memory_MemAvailable_bytes
node_memory_MemTotal_bytes
node_filesystem_avail_bytes
node_filesystem_size_bytes
node_network_receive_bytes_total
node_network_transmit_bytes_total
node_load1
node_boot_time_seconds

# cAdvisor (container metrics)
container_cpu_usage_seconds_total
container_memory_usage_bytes
container_up

# Postgres Exporter
pg_stat_database_numbackends
pg_stat_database_xact_commit
pg_stat_database_xact_rollback
pg_stat_database_blks_hit
pg_stat_database_blks_read

# Redis Exporter
redis_memory_used_bytes
redis_memory_max_bytes
redis_commands_processed_total
```

**Status**: ⚠️ **REQUIRES** Node Exporter, cAdvisor, and database exporters to be deployed

---

### 4. **ISO 22301 Compliance** (`iso-22301-compliance.json`)
**Size**: 16 KB | **Panels**: 12

**Purpose**: ISO 22301 compliance tracking per clause

**Metrics Required** (compliance-monitoring service exports these):
```prometheus
# Overall Compliance
bcm_compliance_score                   # Overall score (0-100)

# Clause-Specific Compliance
bcm_compliance_by_clause{clause="8.2"}  # BIA compliance
bcm_compliance_by_clause{clause="8.3"}  # Strategy compliance
bcm_compliance_by_clause{clause="8.4"}  # Plans compliance
bcm_compliance_by_clause{clause="9.2"}  # Audit compliance
bcm_compliance_by_clause{clause="10.1"} # Nonconformity
bcm_compliance_by_clause{clause="10.2"} # Improvement

# RTO/RPO Compliance
bcm_rto_adherence_percentage           # % meeting RTO
bcm_rpo_adherence_percentage           # % meeting RPO
bcm_bia_rto_average_hours             # Average RTO
bcm_bia_rpo_average_hours             # Average RPO

# Audit Metrics
bcm_audit_events_total                 # Total audit events
bcm_nonconformity_total{status="open|resolved"}  # Nonconformities
```

**Services Expected**:
- compliance-monitoring (8779) - THIS SERVICE MUST EXPORT THESE METRICS

**Status**: ⚠️ **REQUIRES** compliance-monitoring to implement metrics exporter

---

### 5. **Service Performance** (`service-performance.json`)
**Size**: 21 KB | **Panels**: 21

**Purpose**: HTTP performance, latency, error rates per service

**Metrics Required** (ALL services must export):
```prometheus
# Standard HTTP Instrumentation
http_requests_total{job="service", method="GET|POST", status="200|404|500"}
http_request_duration_seconds{job="service", method="GET|POST", endpoint="/api/..."}
http_request_duration_seconds_bucket{...}  # for histogram (P95, P99)

# Service Health
up{job="service"}

# Database Connection Pool (if service uses DB)
database_connections_active{job="service"}
database_connections_idle{job="service"}

# Service-Specific Metrics
planning_strategies_created_total
planning_strategies_approved_total
plans_created_total
plans_approved_total
bia_processes_total
```

**Services Expected**:
- All 11 intelligent-core services
- All observability services

**Status**: ⚠️ **REQUIRES** ALL services to implement `prometheus_client` metrics

---

## How Prometheus Works

### Architecture:
```
┌──────────────────┐
│  Service A       │
│  (port 9000)     │──┐
│  /metrics        │  │
└──────────────────┘  │
                      │
┌──────────────────┐  │
│  Service B       │  │     ┌────────────────┐      ┌──────────────┐
│  (port 8030)     │──┼────→│  Prometheus    │─────→│  Grafana     │
│  /metrics        │  │     │  (scraper)     │      │  (dashboards)│
└──────────────────┘  │     │  Port 9090     │      │  Port 3000   │
                      │     └────────────────┘      └──────────────┘
┌──────────────────┐  │              ↑
│  Service C       │  │              │
│  (port 8031)     │──┘              │
│  /metrics        │                 │
└──────────────────┘          Reads metrics
                              every 15-30s
```

### Prometheus Config (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'intelligent-core'
    static_configs:
      - targets:
        - 'intelligent-core:9000'
        - 'ai-foundation:8030'
        - 'community-intelligence:8031'
        # ... all services
```

### Each Service Must:
1. **Import** `prometheus_client` (Python) or equivalent
2. **Create** metrics (Counter, Histogram, Gauge)
3. **Export** at `/metrics` endpoint
4. **Update** metrics during requests

**Example** (Python with FastAPI):
```python
from prometheus_client import Counter, Histogram, make_asgi_app
from fastapi import FastAPI

app = FastAPI()

# Define metrics
http_requests = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Update metrics in middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    with http_duration.labels(request.method, request.url.path).time():
        response = await call_next(request)
    http_requests.labels(request.method, request.url.path, response.status_code).inc()
    return response

# Mount Prometheus /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## Current Status - Metrics Implementation

### ✅ Services WITH Prometheus Metrics:
1. **Compliance Monitoring** (8779) - ⚠️ Has `/metrics` but needs custom BCM metrics
2. **Process Analytics** (8780) - ⚠️ Has `/metrics` but needs process mining metrics
3. **Notification Service** (8035) - ⚠️ Has basic metrics, needs enhancement

### ❌ Services WITHOUT Prometheus Metrics:
1. **intelligent-core main** (9000) - ❌ NO METRICS
2. **ai-foundation** (8030) - ❌ NO METRICS (LLM cost, RAG needed!)
3. **community-intelligence** (8031) - ❌ NO METRICS
4. **collective** (8032) - ❌ NO METRICS
5. **ai-orchestration** (8002) - ❌ NO METRICS
6. **coordination-center** (8004) - ❌ NO METRICS
7. **predictive** (8033) - ❌ NO METRICS
8. **ai-workflow-optimizer** (8006) - ❌ NO METRICS

---

## Next Steps

### Immediate (for dashboards to work):

1. **Add Prometheus metrics to ALL intelligent-core services**:
   ```bash
   # For each service's main.py:
   pip install prometheus-client
   # Add metrics middleware
   # Export /metrics endpoint
   ```

2. **Implement custom metrics in key services**:
   - **ai-foundation**: LLM cost, RAG latency, tokens used
   - **compliance-monitoring**: ISO clause scores, RTO/RPO adherence
   - **process-analytics**: Process deviations, bottlenecks

3. **Update Prometheus scrape config** to include all 11 services

4. **Deploy exporters** (optional but recommended):
   - Node Exporter (system metrics)
   - cAdvisor (container metrics)
   - Postgres Exporter (database metrics)

### Optional Enhancements:

- Add custom BCM metrics to dashboards
- Create alert rules based on thresholds
- Set up Grafana notifications (email, Slack)
- Implement service auto-discovery in Prometheus

---

## Testing Dashboards

### After implementing metrics:

```bash
# 1. Check service exports metrics
curl http://localhost:9000/metrics
curl http://localhost:8030/metrics

# 2. Check Prometheus scrapes them
curl http://localhost:9090/api/v1/targets

# 3. Check Grafana loads dashboards
open http://localhost:3000

# 4. Verify each dashboard displays data
```

---

## Dashboard URLs (after deployment)

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Prometheus Targets**: http://localhost:9090/targets

---

**Status**: ✅ DASHBOARDS CLEANED & CONFIGURED
**Next**: 🔨 IMPLEMENT METRICS IN SERVICES

See also:
- [REAL_INFRASTRUCTURE_CONFIGURATION.md](REAL_INFRASTRUCTURE_CONFIGURATION.md)
- [CONFIGURATION_COMPLETE.md](CONFIGURATION_COMPLETE.md)
