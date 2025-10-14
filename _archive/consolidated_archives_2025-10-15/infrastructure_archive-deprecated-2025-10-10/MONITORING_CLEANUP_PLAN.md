# Monitoring Infrastructure Cleanup Plan

**Date**: October 11, 2025
**Issue**: Duplicate monitoring directories detected
**Status**: 🔄 Requires action

## Problem: Duplicate Directories

### Current State

```
/infrastructure/
├── observability/              # ✅ PRIMARY - полный набор
│   ├── monitoring-backend/     # FastAPI backend (port 8050)
│   ├── notification-service/   # Notification system
│   ├── exporters/              # Metrics exporters
│   ├── scripts/                # Utility scripts
│   ├── prometheus/             # Prometheus configs (NEWER)
│   │   └── prometheus.yml      # Configured for: node, postgres, odoo, eventbus
│   ├── grafana/                # Grafana configs
│   └── prometheus-local.yml    # Local dev config
│
└── monitoring/                 # ❌ DUPLICATE - старая версия
    ├── prometheus/             # Prometheus configs (OLDER)
    │   ├── prometheus.yml      # Configured for: monitoring_backend, orchestrator, workflow
    │   ├── alerts/
    │   │   └── orchestrator-alerts.yml
    │   └── data/               # Prometheus data directory
    └── grafana/                # Grafana configs (older)
```

### Comparison

| Aspect | `/observability/` | `/monitoring/` |
|--------|-------------------|----------------|
| **Status** | ✅ Current | ❌ Old |
| **Prometheus config** | node, postgres, odoo, eventbus | monitoring_backend, orchestrator, workflow |
| **Last modified** | Oct 11, 2025 | Oct 9, 2025 |
| **Additional components** | exporters/, scripts/, monitoring-backend/ | Only prometheus + grafana |
| **Purpose** | Full observability stack | Basic prometheus setup |
| **Integration** | Service Discovery v2.0, MIO Manager | Old orchestrator |

### Key Differences in prometheus.yml

#### `/observability/prometheus/prometheus.yml` (NEWER):
```yaml
scrape_configs:
  - job_name: 'node'              # System metrics
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres'          # Database metrics
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'odoo'              # Odoo ERP metrics
    static_configs:
      - targets: ['odoo:8069']

  - job_name: 'eventbus'          # EventBus metrics
    static_configs:
      - targets: ['eventbus:3001']
```

#### `/monitoring/prometheus/prometheus.yml` (OLDER):
```yaml
scrape_configs:
  - job_name: 'monitoring_backend'
    static_configs:
      - targets: ['localhost:8050']

  - job_name: 'ai_orchestrator'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'workflow_intelligence'
    static_configs:
      - targets: ['localhost:8003']

  - job_name: 'community_intelligence'
    static_configs:
      - targets: ['localhost:8004']

  - job_name: 'admin_control_center'
    static_configs:
      - targets: ['localhost:3000']
```

**Analysis**:
- `/monitoring/` = старая конфигурация с прямыми localhost портами
- `/observability/` = новая конфигурация с Docker service names

---

## Recommended Action Plan

### Option 1: Merge and Archive (RECOMMENDED) ✅

**Important**: `/infrastructure/monitoring/` contains **valuable alert rules** and **dashboards**!

#### Valuable Assets Found:
- ✅ `orchestrator-alerts.yml` (208 lines) - Critical, Warning, Info alerts
- ✅ `orchestrator-overview.json` - Grafana dashboard
- ✅ `orchestrator-efficiency.json` - Grafana dashboard

**Steps**:

1. **Create directories in `/observability/`**
```bash
mkdir -p /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/alerts/
mkdir -p /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
```

2. **Copy alert rules**
```bash
cp /Users/MD/AI-Platform-ISO/infrastructure/monitoring/prometheus/alerts/orchestrator-alerts.yml \
   /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/alerts/
```

3. **Copy Grafana dashboards**
```bash
cp /Users/MD/AI-Platform-ISO/infrastructure/monitoring/grafana/dashboards/*.json \
   /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
```

4. **Update `/observability/prometheus/prometheus.yml`**
```yaml
# Add after global section:
rule_files:
  - 'alerts/orchestrator-alerts.yml'
```

5. **Verify files copied**
```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/alerts/
ls -la /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
```

6. **Archive old directory** (only after verification)
```bash
mkdir -p /Users/MD/AI-Platform-ISO/_archive/monitoring-deprecated-20251011/
mv /Users/MD/AI-Platform-ISO/infrastructure/monitoring/ \
   /Users/MD/AI-Platform-ISO/_archive/monitoring-deprecated-20251011/
```

7. **Create migration doc** in archive explaining what was preserved

**Benefits**:
- ✅ Single source of truth
- ✅ No confusion
- ✅ Clean structure
- ✅ Preserve history in archive

---

### Option 2: Rename for Clarity

**If both are needed** (unlikely):

```bash
mv /infrastructure/monitoring/ /infrastructure/monitoring-legacy/
```

Add README in `/infrastructure/monitoring-legacy/`:
```markdown
# DEPRECATED - Monitoring Legacy

This directory contains old monitoring configs.

**DO NOT USE** - Use `/infrastructure/observability/` instead.

**Migration**: Oct 11, 2025
**Archive**: This will be removed in v3.0
```

---

## Merged Configuration Recommendations

### Unified Prometheus Config

After cleanup, `/infrastructure/observability/prometheus/prometheus.yml` should contain:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    platform: 'AI-Platform-ISO'
    environment: 'production'

# Alert rules
rule_files:
  - 'alerts/*.yml'

scrape_configs:
  # ========================================
  # Infrastructure
  # ========================================

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # ========================================
  # Platform Services - Runtime
  # ========================================

  - job_name: 'service-discovery'
    static_configs:
      - targets: ['service-discovery:8500']
    metrics_path: '/metrics'

  - job_name: 'eventbus'
    static_configs:
      - targets: ['eventbus:3001']
    metrics_path: '/metrics'

  - job_name: 'mio-manager'
    static_configs:
      - targets: ['mio-manager:8046']
    metrics_path: '/metrics'

  - job_name: 'ai-event-manager'
    static_configs:
      - targets: ['ai-event-manager:8043']
    metrics_path: '/metrics'

  # ========================================
  # Platform Services - Observability
  # ========================================

  - job_name: 'monitoring-backend'
    static_configs:
      - targets: ['monitoring-backend:8050']
    metrics_path: '/metrics'

  # ========================================
  # Intelligent Core
  # ========================================

  - job_name: 'workflow_intelligence'
    static_configs:
      - targets: ['workflow-intelligence:8037']
    metrics_path: '/metrics'

  - job_name: 'ai-foundation'
    static_configs:
      - targets: ['ai-foundation:8040']
    metrics_path: '/metrics'

  - job_name: 'event_intelligence'
    static_configs:
      - targets: ['event-intelligence:8039']
    metrics_path: '/metrics'

  - job_name: 'learning-system'
    static_configs:
      - targets: ['learning-system:8033']
    metrics_path: '/metrics'

  - job_name: 'predictive'
    static_configs:
      - targets: ['predictive:8032']
    metrics_path: '/metrics'

  - job_name: 'workflow-engine'
    static_configs:
      - targets: ['workflow-engine:8036']
    metrics_path: '/metrics'

  # ========================================
  # External Integrations
  # ========================================

  - job_name: 'odoo'
    static_configs:
      - targets: ['odoo:8069']
    metrics_path: '/web/database/manager'

  # ========================================
  # AI Office Infrastructure
  # ========================================

  - job_name: 'orchestrator'
    static_configs:
      - targets: ['orchestrator:8045']
    metrics_path: '/metrics'

  - job_name: 'analytics-specialist'
    static_configs:
      - targets: ['analytics-specialist:8041']
    metrics_path: '/metrics'

  - job_name: 'db-intelligence'
    static_configs:
      - targets: ['db-intelligence:8042']
    metrics_path: '/metrics'

  - job_name: 'project-agent'
    static_configs:
      - targets: ['project-agent:8044']
    metrics_path: '/metrics'

  # ========================================
  # FUTURE: Service Discovery Auto-Config
  # ========================================
  # TODO: Replace static configs with Service Discovery integration
  # - job_name: 'service-discovery-auto'
  #   consul_sd_configs:
  #     - server: 'service-discovery:8500'
```

### Alert Rules to Preserve

From `/monitoring/prometheus/alerts/orchestrator-alerts.yml`:

```yaml
# Check if these are still relevant and merge to:
# /infrastructure/observability/prometheus/alerts/platform-alerts.yml

groups:
  - name: orchestrator
    rules:
      - alert: OrchestratorDown
        expr: up{job="orchestrator"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Orchestrator is down"

      # ... other orchestrator alerts
```

**Action**: Review and merge into unified alerts structure.

---

## Final Structure (After Cleanup)

```
/infrastructure/
│
├── observability/                        # ✅ ONLY observability directory
│   ├── README.md                         # Documentation
│   ├── monitoring-README.md              # Monitoring guide
│   │
│   ├── prometheus/                       # Prometheus configs
│   │   ├── prometheus.yml                # UNIFIED config (all 27 services)
│   │   ├── alerts/                       # Alert rules
│   │   │   ├── platform-alerts.yml       # Platform-wide alerts
│   │   │   ├── service-alerts.yml        # Service-specific alerts
│   │   │   └── coverage-alerts.yml       # MIO coverage alerts
│   │   └── data/                         # Prometheus data (gitignored)
│   │
│   ├── grafana/                          # Grafana configs
│   │   ├── provisioning/
│   │   └── dashboards/
│   │
│   ├── monitoring-backend/               # Monitoring API (port 8050)
│   ├── notification-service/             # Notifications
│   ├── exporters/                        # Custom exporters
│   └── scripts/                          # Utility scripts
│
├── AI-office-infrastructure/
│   └── mio-manager/                      # MIO Manager (EYES)
│       ├── MONITORING_SYSTEM_ARCHITECTURE.md    # 🆕 Architecture doc
│       ├── MONITORING_ARCHITECTURE_DIAGRAM.md   # 🆕 Diagrams
│       └── monitoring/                   # MIO observers
│
└── runtime/
    └── service-discovery/                # Service Discovery v2.0
        └── catalog_integration.py        # Catalog integration

/_archive/
└── monitoring-deprecated-20251011/       # 🆕 Archived old configs
    ├── README.md                         # Migration explanation
    └── old-monitoring/                   # Old /infrastructure/monitoring/
```

---

## Migration Checklist

### Pre-Migration
- [ ] Backup `/infrastructure/monitoring/` to archive
- [ ] Review `orchestrator-alerts.yml` - still needed?
- [ ] Check if any scripts reference old location
- [ ] Verify `/infrastructure/observability/` has all needed configs

### Migration
- [ ] Create archive directory
- [ ] Copy old configs to archive
- [ ] Extract useful alert rules
- [ ] Merge alert rules to `/observability/prometheus/alerts/`
- [ ] Update prometheus.yml with all services
- [ ] Delete old `/infrastructure/monitoring/`

### Post-Migration
- [ ] Update documentation references
- [ ] Test Prometheus with new config
- [ ] Verify all 27 services are scraped
- [ ] Update docker-compose.yml if needed
- [ ] Update MIO Manager to use unified Prometheus config

### Verification
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
# Should return: 27+ targets

# Check MIO coverage
curl http://localhost:8046/api/coverage | jq '.coverage_percentage'
# Should return: ~100%
```

---

## References

- **Service Catalog**: `/infrastructure/runtime/service-catalog/service-catalog.yaml`
- **Service Discovery v2**: `/infrastructure/runtime/service-discovery/`
- **MIO Manager**: `/infrastructure/AI-office-infrastructure/mio-manager/`
- **Observability**: `/infrastructure/observability/`

---

## Decision Required

**Question for team**:
1. ✅ Merge and archive `/infrastructure/monitoring/`? (RECOMMENDED)
2. ⏸️ Rename to `/infrastructure/monitoring-legacy/`?
3. ❌ Keep both? (NOT recommended - causes confusion)

**Recommended**: **Option 1 - Merge and Archive**

---

**Status**: 🔄 Awaiting approval to execute cleanup
**Impact**: Low (old directory not actively used)
**Risk**: Low (backup to archive)
**Benefit**: High (clean structure, no confusion)

**Last Updated**: October 11, 2025
