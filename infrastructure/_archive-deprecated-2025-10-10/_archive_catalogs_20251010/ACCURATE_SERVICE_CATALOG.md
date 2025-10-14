# AI-Platform-ISO Accurate Service Catalog

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')
**Based on:** Real running services + Documentation

---

## 📊 Executive Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Documented Services** | 21+ | 100% |
| **Currently Running (Documented)** | 4 | 19.0% |
| **Currently Running (Undocumented)** | 17 | - |
| **Not Running** | 17 | 81.0% |
| **Prometheus Monitored** | 2/6 | 33.3% |

---

## 🎯 Intelligent Core (11 Modules)

### Running ✅

| Module | Port | Status | Metrics | Business Process |
|--------|------|--------|---------|------------------|
| **collective** | 8032 | ✅ RUNNING | ❌ Not configured | Core Platform Services |
| **predictive** | 8031 | ✅ RUNNING | ❌ Not configured | Predictive Analytics |
| **community_intelligence** | 8038 | ✅ RUNNING | ❌ Not configured | AI Intelligence & Decision Support |
| **system-bcm-service** | 8050 | ✅ RUNNING | ⚠️ Conflict (shared with monitoring-backend) | Core Platform Services |

### Not Running ❌

| Module | Port | Status | Reason |
|--------|------|--------|--------|
| **ai-foundation** | ? | ❌ NOT RUNNING | Not started |
| **workflow_intelligence** | 8037 | ❌ NOT RUNNING | Not started |
| **expertise-center** | 8036 | ❌ NOT RUNNING | Not started |
| **event_intelligence** | 8039 | ❌ NOT RUNNING | Not started |
| **workflow-engine** | 8041 | ❌ NOT RUNNING | Not started |
| **ai_workflow_optimizer** | ? | ❌ NOT RUNNING | Not started |
| **orchestration** | ? | ❌ NOT RUNNING | Not started |

---

## 🏢 Platform Services (12 Services)

### All NOT Running ❌

| Service | Port | ISO 22301 Clause | Status |
|---------|------|------------------|--------|
| **bia-service** | 8001 | 8.2 | ❌ NOT RUNNING |
| **risk-service** | 8002 | 8.3 | ❌ NOT RUNNING |
| **compliance-service** | 8003 | 9.1 | ❌ NOT RUNNING |
| **planning-service** | 8004 | 8.4 | ❌ NOT RUNNING |
| **response-service** | 8005 | 8.4 | ❌ NOT RUNNING |
| **documents-service** | 8006 | 7.5 | ❌ NOT RUNNING |
| **governance-service** | 8007 | 5.0 | ❌ NOT RUNNING |
| **validation-service** | 8008 | 8.5 | ❌ NOT RUNNING |
| **learning-service** | 8009 | 7.3 | ❌ NOT RUNNING |
| **bcm-coordination-service** | 8010 | - | ❌ NOT RUNNING |
| **community-service** | 8011 | - | ❌ NOT RUNNING |
| **monitoring** | 8012 | 9.0 | ❌ NOT RUNNING |

---

## 🏗️ Infrastructure

### Running ✅

| Component | Port | Status | Metrics |
|-----------|------|--------|---------|
| **monitoring-backend** | 8050 | ✅ RUNNING | ✅ http://localhost:8050/metrics |
| **prometheus** | 9090 | ⚠️ Should be running | ✅ Configured |

### Undocumented (Running) ⚠️

| Port | Process | Suspected Service |
|------|---------|-------------------|
| 8888 | Python | _deprecated_unified_database_gateway |
| 8020 | Python | Unknown backend service |
| 8030 | Python | Unknown backend service |
| 8033 | Python | learning-system (not documented) |
| 8034 | Python | Unknown backend service |
| 8055 | Python | Unknown backend service |
| 5555 | Python | Unknown backend service |

---

## 🖥️ Interface (Frontend)

### Running ✅

| Port | Suspected Service | Framework |
|------|-------------------|-----------|
| 3003 | admin-control-center | React + Vite |
| 3000-3007 | Various frontend services | React + Vite |
| 3333 | Unknown frontend | React + Vite |
| 4000 | Unknown frontend | React + Vite |

**Note:** Frontend ports are dynamic (Vite auto-assigns if port busy)

---

## 📈 Monitoring Status

### Prometheus Targets

| Job | Target | Health | Last Error |
|-----|--------|--------|------------|
| prometheus | localhost:9090 | ✅ UP | - |
| monitoring_backend | localhost:8050 | ✅ UP | - |
| ai_orchestrator | localhost:8000 | ❌ DOWN | Connection refused |
| workflow_intelligence | localhost:8003 | ❌ DOWN | Connection refused |
| community_intelligence | localhost:8004 | ❌ DOWN | Connection refused |
| admin_control_center | localhost:3008 | ❌ DOWN | Wrong port (runs on 3003) |

### Dashboard Data Quality

**Current:** ❌ **100% MOCK DATA**

```json
{
  "total_services": 12,        // ← MOCK (documented: 21+, running: 21)
  "healthy_services": 10,      // ← MOCK (real: 4 documented, 17 undocumented)
  "cpu_usage": 45.3,          // ← MOCK
  "memory_usage": 62.8,       // ← MOCK
  "active_pdca_cycles": 3,    // ← MOCK
  "active_alerts": 2          // ← MOCK
}
```

---

## ⚠️ Critical Issues

### 1. Port Conflicts
- **8050:** Used by both `monitoring-backend` AND `system-bcm-service`

### 2. Missing Metrics Endpoints
17 out of 21 services have NO /metrics endpoint:
- All intelligent-core services (except if monitoring-backend counted)
- All platform-services
- Undocumented services

### 3. Service Discovery Gap
17 undocumented services running - need identification and cataloging

### 4. Platform Services Coverage
**0% of platform services running** - Critical for ISO 22301 compliance

---

## 🎯 Recommendations

### Priority 1: Start Critical Platform Services

**ISO 22301 Compliance depends on these:**

```bash
# Business Continuity Planning
./start-service.sh bia-service 8001
./start-service.sh planning-service 8004

# Risk & Compliance
./start-service.sh risk-service 8002
./start-service.sh compliance-service 8003

# Governance
./start-service.sh governance-service 8007
```

### Priority 2: Fix Monitoring Data

1. **Install node_exporter**
   ```bash
   brew install node_exporter
   node_exporter &
   ```

2. **Fix dashboard.py error handling**
   - Remove list index out of range error
   - Use real Prometheus data

3. **Update Prometheus config**
   - Add all 21+ documented services
   - Fix admin-control-center port (3003 not 3008)

### Priority 3: Add /metrics Endpoints

Template for adding to each service:

```python
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
from fastapi.responses import Response

# Define metrics
requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
active_connections = Gauge('active_connections', 'Active connections')

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )
```

### Priority 4: Identify Unknown Services

Investigate and document the 17 undocumented services:
- Ports 5555, 8020, 8030, 8033, 8034, 8055, 8888
- Frontend ports 3000-3007, 3333, 4000

---

## 📋 Service Catalog Files

This directory contains:

1. **ACCURATE_SERVICE_CATALOG.md** (this file) - Real status
2. **service-catalog.json** - Programmatic access
3. **service-catalog.yaml** - Human-readable format
4. **SERVICE_CATALOG_SUMMARY.md** - Quick reference
5. **LIVE_STATUS_REPORT.md** - Runtime status
6. **README.md** - Usage instructions

---

**Last Updated:** $(date '+%Y-%m-%d %H:%M:%S')
