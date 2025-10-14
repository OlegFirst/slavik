# Monitoring Directories Status

**Date**: October 11, 2025
**Status**: ⚠️ Requires merge before archival

## TL;DR

❌ **НЕ УДАЛЯЙТЕ** `/infrastructure/monitoring/` сразу!
✅ **СНАЧАЛА** скопируйте ценные alert rules и dashboards в `/observability/`

---

## Directory Comparison

### `/infrastructure/observability/` ✅ MAIN

**Purpose**: Primary observability stack
**Last Modified**: Oct 11, 2025
**Status**: ✅ Active, production

**Contents**:
```
/observability/
├── prometheus/
│   ├── prometheus.yml               # ✅ MODERN (Docker service names)
│   └── alerts/                       # ⚠️ EMPTY - needs orchestrator-alerts.yml
├── grafana/
│   ├── provisioning/
│   └── dashboards/                   # ⚠️ EMPTY - needs orchestrator dashboards
├── monitoring-backend/              # FastAPI backend (port 8050)
├── notification-service/            # Notifications
├── exporters/                       # Custom exporters
└── scripts/                         # Utility scripts
```

**Prometheus Config**: Modern (node, postgres, odoo, eventbus)

---

### `/infrastructure/monitoring/` ⚠️ OLD BUT HAS VALUABLE CONTENT

**Purpose**: Old monitoring setup
**Last Modified**: Oct 10, 2025
**Status**: ⚠️ **Contains valuable alert rules!**

**Contents**:
```
/monitoring/
├── prometheus/
│   ├── prometheus.yml               # ❌ OLD (localhost:ports)
│   ├── alerts/
│   │   └── orchestrator-alerts.yml  # ✅ VALUABLE! 208 lines
│   └── data/                         # ❌ Runtime data (can delete)
└── grafana/
    └── dashboards/
        ├── orchestrator-overview.json      # ✅ VALUABLE! Dashboard
        └── orchestrator-efficiency.json    # ✅ VALUABLE! Dashboard
```

**Prometheus Config**: Old (orchestrator, workflow_intelligence, localhost)

---

## Valuable Assets in `/monitoring/` 🔥

### 1. Alert Rules (CRITICAL - DO NOT LOSE!)

**File**: `/monitoring/prometheus/alerts/orchestrator-alerts.yml`
**Size**: 208 lines
**Contents**:
- 6 Critical alerts (latency, failures, escalations, safety, circuit breakers)
- 5 Warning alerts (slow calls, cache, retries, PDCA, memory)
- 3 Info alerts (learning, crisis, prevention)

**Example alerts**:
```yaml
- OrchestratorHighLatency            # P95 > 100ms
- OrchestratorAutoResolveFailures    # > 5% failure rate
- OrchestratorHighEscalationRate     # > 30% escalations
- OrchestratorCircuitBreakersOpen    # Circuit breaker trips
- OrchestratorCrisisCoordinatorDown  # API down
```

**Status**: ✅ **MUST PRESERVE**

---

### 2. Grafana Dashboards (VALUABLE)

**Files**:
1. `/monitoring/grafana/dashboards/orchestrator-overview.json`
2. `/monitoring/grafana/dashboards/orchestrator-efficiency.json`

**Status**: ✅ **SHOULD PRESERVE**

---

## Merge Instructions (EXECUTE BEFORE ARCHIVAL)

### Step 1: Create directories

```bash
mkdir -p /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/alerts/
mkdir -p /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
```

### Step 2: Copy alert rules

```bash
cp /Users/MD/AI-Platform-ISO/infrastructure/monitoring/prometheus/alerts/orchestrator-alerts.yml \
   /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/alerts/
```

**Verify**:
```bash
cat /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/alerts/orchestrator-alerts.yml | wc -l
# Expected: 208
```

### Step 3: Copy dashboards

```bash
cp /Users/MD/AI-Platform-ISO/infrastructure/monitoring/grafana/dashboards/*.json \
   /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
```

**Verify**:
```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
# Expected: orchestrator-overview.json, orchestrator-efficiency.json
```

### Step 4: Update Prometheus config

Edit `/infrastructure/observability/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# ADD THIS SECTION:
rule_files:
  - 'alerts/orchestrator-alerts.yml'

scrape_configs:
  # ... existing configs
```

**Verify**:
```bash
grep -A1 "rule_files:" /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/prometheus.yml
```

### Step 5: Test Prometheus config

```bash
# If Prometheus is running:
curl -X POST http://localhost:9090/-/reload

# Check rules loaded:
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].name'
# Expected: orchestrator_critical, orchestrator_warning, orchestrator_info
```

### Step 6: Archive old directory (ONLY AFTER STEPS 1-5)

```bash
# Create archive directory
mkdir -p /Users/MD/AI-Platform-ISO/_archive/monitoring-deprecated-20251011/

# Move old monitoring
mv /Users/MD/AI-Platform-ISO/infrastructure/monitoring/ \
   /Users/MD/AI-Platform-ISO/_archive/monitoring-deprecated-20251011/

# Create README in archive
cat > /Users/MD/AI-Platform-ISO/_archive/monitoring-deprecated-20251011/README.md << 'EOF'
# Old Monitoring Directory (Archived Oct 11, 2025)

## Why archived?

Old monitoring setup with localhost-based Prometheus config.

## What was preserved?

✅ **Preserved in /infrastructure/observability/**:
- `orchestrator-alerts.yml` → `/observability/prometheus/alerts/`
- `orchestrator-overview.json` → `/observability/grafana/dashboards/`
- `orchestrator-efficiency.json` → `/observability/grafana/dashboards/`

❌ **Not preserved** (obsolete):
- Old prometheus.yml (localhost configs)
- Prometheus runtime data

## Migration Date

October 11, 2025

## New Location

Primary observability stack: `/infrastructure/observability/`
EOF
```

---

## Checklist Before Archival

- [ ] Created `/observability/prometheus/alerts/` directory
- [ ] Created `/observability/grafana/dashboards/` directory
- [ ] Copied `orchestrator-alerts.yml` to new location
- [ ] Copied dashboard JSONs to new location
- [ ] Updated Prometheus config with `rule_files`
- [ ] Tested Prometheus config (if running)
- [ ] Verified alert rules loaded
- [ ] Verified dashboards accessible in Grafana
- [ ] Created archive directory
- [ ] Moved `/monitoring/` to archive
- [ ] Created README in archive

**Only check this when ALL above are done**: [ ] Migration complete

---

## Documentation Locations

**Monitoring System Docs**:
```
/infrastructure/AI-office-infrastructure/mio-manager/
├── MONITORING_DOCS_INDEX.md
├── MONITORING_SYSTEM_SUMMARY.md
├── MONITORING_SYSTEM_ARCHITECTURE.md
└── MONITORING_ARCHITECTURE_DIAGRAM.md
```

**Cleanup Plan**:
```
/infrastructure/
├── MONITORING_CLEANUP_PLAN.md           # Detailed plan
└── MONITORING_DIRECTORIES_STATUS.md     # This file
```

---

## Summary

**Current State**:
- ✅ `/observability/` = Main stack (but missing alerts)
- ⚠️ `/monitoring/` = Old (but has valuable alerts)

**Action Required**:
1. **COPY** valuable assets from `/monitoring/` to `/observability/`
2. **VERIFY** all assets copied
3. **ARCHIVE** `/monitoring/` directory

**Do NOT**:
- ❌ Delete `/monitoring/` before copying assets
- ❌ Ignore orchestrator-alerts.yml (critical!)

---

**Status**: ⚠️ Ready for merge
**Risk Level**: 🟡 Medium (valuable data must be preserved)
**Estimated Time**: 10 minutes

**Last Updated**: October 11, 2025
