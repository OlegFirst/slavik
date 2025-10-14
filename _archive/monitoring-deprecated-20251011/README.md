# Old Monitoring Directory (Archived Oct 11, 2025)

## Why archived?

Old monitoring setup with localhost-based Prometheus configuration.
Modern observability stack is now in `/infrastructure/observability/`.

## What was preserved?

✅ **Preserved in `/infrastructure/observability/`**:

### Alert Rules
- `orchestrator-alerts.yml` (208 lines)
  - Location: `/infrastructure/observability/prometheus/alerts/orchestrator-alerts.yml`
  - Contains: 6 Critical, 5 Warning, 3 Info alerts for AI Orchestrator
  - Added to Prometheus via `rule_files` in prometheus.yml

### Grafana Dashboards
- `orchestrator-overview.json`
  - Location: `/infrastructure/observability/grafana/dashboards/orchestrator-overview.json`
  - Purpose: AI Orchestrator overview dashboard

- `orchestrator-efficiency.json`
  - Location: `/infrastructure/observability/grafana/dashboards/orchestrator-efficiency.json`
  - Purpose: Orchestrator efficiency metrics

## What was NOT preserved (obsolete)

❌ **Old prometheus.yml**:
- Used localhost:port configs
- Replaced by modern Docker service names in `/observability/prometheus/prometheus.yml`

❌ **Prometheus runtime data** (`/prometheus/data/`):
- Temporary runtime data
- Not needed (new Prometheus instance has fresh data)

## Migration Details

**Date**: October 11, 2025
**Performed by**: AI Platform Architecture Team
**Verified**: ✅ All valuable assets copied and verified

### Files Copied
```bash
# Alert rules
/monitoring/prometheus/alerts/orchestrator-alerts.yml
  → /observability/prometheus/alerts/orchestrator-alerts.yml

# Dashboards
/monitoring/grafana/dashboards/orchestrator-overview.json
  → /observability/grafana/dashboards/orchestrator-overview.json

/monitoring/grafana/dashboards/orchestrator-efficiency.json
  → /observability/grafana/dashboards/orchestrator-efficiency.json
```

### Prometheus Config Updated
```yaml
# /infrastructure/observability/prometheus/prometheus.yml
rule_files:
  - 'alerts/orchestrator-alerts.yml'  # Added
```

## New Location

**Primary observability stack**: `/infrastructure/observability/`

**Structure**:
```
/infrastructure/observability/
├── prometheus/
│   ├── prometheus.yml              # Modern config
│   └── alerts/
│       └── orchestrator-alerts.yml # Migrated
├── grafana/
│   ├── provisioning/
│   └── dashboards/
│       ├── orchestrator-overview.json    # Migrated
│       └── orchestrator-efficiency.json  # Migrated
├── monitoring-backend/
├── notification-service/
├── exporters/
└── scripts/
```

## Restoration (if needed)

If you need to restore anything:

```bash
# Restore alert rules
cp /_archive/monitoring-deprecated-20251011/monitoring/prometheus/alerts/orchestrator-alerts.yml \
   /infrastructure/observability/prometheus/alerts/

# Restore dashboards
cp /_archive/monitoring-deprecated-20251011/monitoring/grafana/dashboards/*.json \
   /infrastructure/observability/grafana/dashboards/
```

## References

- **Migration Plan**: `/infrastructure/MONITORING_CLEANUP_PLAN.md`
- **Directories Status**: `/infrastructure/MONITORING_DIRECTORIES_STATUS.md`
- **MIO Manager Docs**: `/infrastructure/AI-office-infrastructure/mio-manager/MONITORING_DOCS_INDEX.md`

---

**Archive Status**: ✅ Complete
**Safe to Delete**: No - keep as backup
**Retention**: Recommended 6-12 months
