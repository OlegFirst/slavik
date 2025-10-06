# 📍 WHERE EVERYTHING GOES - Quick Reference

**Updated:** 2025-10-03

---

## 🎯 TL;DR - Quick Answers

| What | Where |
|------|-------|
| **Automation Toolkit Reports** | `/Users/MD/AI-Platform-ISO/tools/reports/` |
| **Compliance Data** | `/Users/MD/AI-Platform-ISO/data/compliance/` |
| **Prometheus Metrics** | Docker volume `prometheus_data` |
| **Grafana Dashboards** | Docker volume `grafana_data` |
| **Service Discovery Configs** | `/Users/MD/AI-Platform-ISO/infrastructure/observability/config/prometheus/sd_configs/` |
| **Logs (Loki)** | Docker volume `loki_data` |
| **Docker Container Logs** | `docker logs <container-name>` |
| **Job Results** | `/Users/MD/AI-Platform-ISO/data/compliance/automation/` |

---

## 📊 1. Automation Toolkit Reports

### Path
```
/Users/MD/AI-Platform-ISO/tools/reports/
```

### Files
- `ast_analysis.json` - All functions, classes, endpoints
- `dependencies.json` - Dependency graph
- `security_scan.json` - Bandit OWASP security issues
- `dashboard.html` - Interactive Plotly dashboard
- `endpoint_map.html` - Sunburst visualization
- `dependency_network.html` - Interactive dependency graph

### How to Generate
```bash
cd /Users/MD/AI-Platform-ISO
./tools/run_analysis.sh
```

### How to View
```bash
# Open dashboard
open tools/reports/dashboard.html

# Parse JSON
cat tools/reports/ast_analysis.json | jq '.endpoints | length'
```

---

## 📁 2. Compliance Data (NEW!)

### Path
```
/Users/MD/AI-Platform-ISO/data/compliance/
```

### Structure
```
data/compliance/
├── alerts/                 # Compliance alerts snapshots
├── nonconformities/        # ISO 10.1 nonconformity records
├── audits/                 # ISO 9.2 audit tracking
├── metrics/                # RTO/RPO/MTPD business metrics
├── backups/                # Daily compliance snapshots
│   ├── compliance_snapshot_2025-10-03_15-00.json
│   └── latest.json         # Always points to latest
└── automation/             # Automated job results
    ├── service_discovery_2025-10-03_15-35.json
    ├── security_scan_2025-10-03_16-00.json
    └── complexity_analysis_2025-10-04_02-00.json
```

### Persistence
- **Format:** JSON files
- **Backup:** Daily at 3:00 AM
- **Loading:** Automatic on startup from `latest.json`
- **Retention:** 90 days for backups

### Access
```bash
# View latest snapshot
cat /Users/MD/AI-Platform-ISO/data/compliance/backups/latest.json | jq '.alerts | length'

# View automation job results
ls -lh /Users/MD/AI-Platform-ISO/data/compliance/automation/

# Parse security scan
cat /Users/MD/AI-Platform-ISO/data/compliance/automation/security_scan_*.json | jq '.high_severity'
```

---

## 📝 3. Prometheus Service Discovery

### Path
```
/Users/MD/AI-Platform-ISO/infrastructure/observability/config/prometheus/sd_configs/
```

### Files
- `validation-service.json` - Auto-created when service registers
- `documents-service.json`
- `governance-service.json`
- etc.

### Created By
- `POST /register-service` API endpoint
- Automation Toolkit auto-discovery (every 5 min)

### Format
```json
[{
  "targets": ["validation-service:8022"],
  "labels": {
    "job": "validation-service",
    "service_type": "bcm",
    "iso_clauses": "8.5",
    "compliance_critical": "true"
  }
}]
```

---

## 📊 4. Prometheus Metrics (TSDB)

### Path
```
Docker volume: prometheus_data
Physical: /var/lib/docker/volumes/prometheus_data/_data/
```

### What's Stored
- All scraped metrics from all services
- Time-series data
- Retention: 30 days

### Query
```bash
# Latest metrics
curl 'http://localhost:9090/api/v1/query?query=up' | jq

# Automation metrics
curl 'http://localhost:9090/api/v1/query?query=automation_service_coverage' | jq
```

### Backup
```bash
docker run --rm -v prometheus_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/prometheus_backup_$(date +%Y%m%d).tar.gz /data
```

---

## 📈 5. Grafana Dashboards

### Path
```
Docker volume: grafana_data
Physical: /var/lib/docker/volumes/grafana_data/_data/
```

### Dashboard Files
```
/Users/MD/AI-Platform-ISO/infrastructure/observability/grafana/dashboards/
├── bcm-platform-overview.json
├── iso-22301-compliance.json
├── infrastructure-health.json
└── service-performance.json
```

### Access
- **UI:** http://localhost:3000
- **Login:** admin / admin123

---

## 📜 6. Loki Logs

### Path
```
Docker volume: loki_data
```

### Query
```bash
# Recent logs from service
curl 'http://localhost:3100/loki/api/v1/query_range?query={job="validation-service"}&limit=100'

# Error logs
curl 'http://localhost:3100/loki/api/v1/query_range?query={job="validation-service"}|~"ERROR"'
```

---

## 🐳 7. Docker Container Logs

### View Logs
```bash
# Real-time logs
docker logs -f iso22301-compliance

# Last 100 lines
docker logs --tail 100 bcm-prometheus

# Logs since 1 hour
docker logs --since 1h bcm-grafana

# Export to file
docker logs bcm-prometheus > prometheus_logs.txt
```

### Where They're Stored
```
/var/lib/docker/containers/[container-id]/[container-id]-json.log
```

---

## 🤖 8. Automated Job Results

### Path
```
/Users/MD/AI-Platform-ISO/data/compliance/automation/
```

### Files Created

#### Every 5 minutes (Service Discovery)
```
service_discovery_2025-10-03_15-35.json
service_discovery_2025-10-03_15-40.json
service_discovery_2025-10-03_15-45.json
...
```

**Content:**
```json
{
  "total_services": 12,
  "coverage": {
    "percentage": 100.0,
    "with_metrics": 12
  },
  "monitoring_endpoints": [...]
}
```

#### Every hour (Security Scan)
```
security_scan_2025-10-03_16-00.json
security_scan_2025-10-03_17-00.json
...
```

**Content:**
```json
{
  "status": "issues_found",
  "high_severity": 0,
  "medium_severity": 3,
  "issues": [...]
}
```

#### Daily at 2 AM (Code Complexity)
```
complexity_analysis_2025-10-04_02-00.json
complexity_analysis_2025-10-05_02-00.json
...
```

**Content:**
```json
{
  "avg_complexity": 7.2,
  "max_complexity": 15,
  "high_complexity_functions": [...]
}
```

### Query Examples
```bash
# Count service discoveries
ls -1 /Users/MD/AI-Platform-ISO/data/compliance/automation/service_discovery_*.json | wc -l

# Latest security scan
ls -t /Users/MD/AI-Platform-ISO/data/compliance/automation/security_scan_*.json | head -1 | xargs cat | jq '.high_severity'

# Latest complexity
ls -t /Users/MD/AI-Platform-ISO/data/compliance/automation/complexity_*.json | head -1 | xargs cat | jq '.avg_complexity'

# All security scans today
ls /Users/MD/AI-Platform-ISO/data/compliance/automation/security_scan_$(date +%Y-%m-%d)_*.json

# Trend analysis (complexity over last 7 days)
for file in $(ls -t /Users/MD/AI-Platform-ISO/data/compliance/automation/complexity_*.json | head -7); do
  echo "$(basename $file): $(cat $file | jq -r '.avg_complexity')"
done
```

---

## 📊 9. Process Tracking Logs

### Compliance API Logs
```bash
# If running in terminal
python3 infrastructure/monitoring/main.py

# If running via Docker
docker logs iso22301-compliance -f

# Filter by job type
docker logs iso22301-compliance 2>&1 | grep "🔍 Running automated service discovery"
docker logs iso22301-compliance 2>&1 | grep "🔒 Running hourly security scan"
docker logs iso22301-compliance 2>&1 | grep "📊 Running daily code complexity"
docker logs iso22301-compliance 2>&1 | grep "💾 Running daily compliance data backup"
```

### Expected Log Output
```
2025-10-03 15:35:00 - 🔍 Running automated service discovery...
2025-10-03 15:35:05 - ✅ Service discovery complete: 100.0% coverage
2025-10-03 15:35:05 - 💾 Compliance data saved to /Users/MD/AI-Platform-ISO/data/compliance/automation/service_discovery_2025-10-03_15-35.json

2025-10-03 16:00:00 - 🔒 Running hourly security scan...
2025-10-03 16:00:15 - ⚠️  Security issues: HIGH=0, MEDIUM=3
2025-10-03 16:00:15 - 💾 Compliance data saved to /Users/MD/AI-Platform-ISO/data/compliance/automation/security_scan_2025-10-03_16-00.json

2025-10-04 02:00:00 - 📊 Running daily code complexity analysis...
2025-10-04 02:00:30 - 📈 Complexity: avg=7.2, high_complexity_functions=2
2025-10-04 02:00:30 - 💾 Compliance data saved to /Users/MD/AI-Platform-ISO/data/compliance/automation/complexity_analysis_2025-10-04_02-00.json

2025-10-04 03:00:00 - 💾 Running daily compliance data backup...
2025-10-04 03:00:01 - 💾 Compliance data saved to /Users/MD/AI-Platform-ISO/data/compliance/backups/compliance_snapshot_2025-10-04_03-00.json
2025-10-04 03:00:01 - ✅ Daily backup complete
```

---

## 🗂️ Complete Directory Tree

```
/Users/MD/AI-Platform-ISO/
│
├── data/                                    # ✅ NEW - Persistent data
│   └── compliance/
│       ├── alerts/
│       ├── nonconformities/
│       ├── audits/
│       ├── metrics/
│       ├── backups/
│       │   ├── compliance_snapshot_*.json
│       │   └── latest.json
│       └── automation/
│           ├── service_discovery_*.json
│           ├── security_scan_*.json
│           └── complexity_analysis_*.json
│
├── tools/
│   └── reports/                             # ✅ Automation Toolkit reports
│       ├── ast_analysis.json
│       ├── dependencies.json
│       ├── security_scan.json
│       └── dashboard.html
│
├── infrastructure/
│   └── observability/
│       ├── config/
│       │   └── prometheus/
│       │       └── sd_configs/              # ✅ Service discovery configs
│       │           ├── validation-service.json
│       │           └── documents-service.json
│       └── grafana/
│           └── dashboards/                  # ✅ Grafana dashboard JSON
│               ├── bcm-platform-overview.json
│               └── iso-22301-compliance.json
│
└── Docker Volumes (via docker volume inspect):
    ├── prometheus_data                      # ✅ Metrics TSDB
    ├── grafana_data                         # ✅ Dashboards, users
    ├── loki_data                            # ✅ Centralized logs
    └── alertmanager_data                    # ✅ Alert state
```

---

## 🛠️ Cleanup Commands

```bash
# Clean old automation results (keep last 30 days)
find /Users/MD/AI-Platform-ISO/data/compliance/automation/ -name "*.json" -mtime +30 -delete

# Clean old compliance backups (keep last 90 days)
find /Users/MD/AI-Platform-ISO/data/compliance/backups/ -name "compliance_snapshot_*.json" -mtime +90 -delete

# Check disk usage
du -sh /Users/MD/AI-Platform-ISO/data/compliance/*

# Clean Automation Toolkit reports (manual)
rm /Users/MD/AI-Platform-ISO/tools/reports/*.json
rm /Users/MD/AI-Platform-ISO/tools/reports/*.html
```

---

## ✅ Summary

| Data Type | Primary Location | Backup/Archive | Retention |
|-----------|------------------|----------------|-----------|
| **Automation Reports** | `tools/reports/` | Git | Forever |
| **Compliance Data** | `data/compliance/backups/` | Daily snapshots | 90 days |
| **Job Results** | `data/compliance/automation/` | None | 30 days |
| **Prometheus Metrics** | Docker volume | Manual backup | 30 days |
| **Grafana Dashboards** | Docker volume | Git (JSON) | Forever |
| **Logs (Loki)** | Docker volume | None | 30 days |
| **Service Discovery** | `sd_configs/` | Git | Forever |
| **Docker Logs** | `/var/lib/docker/` | Rotated | Last 30 MB |

---

**All process tracking is now persistent!** 🎉

- Compliance data survives restarts ✅
- Job results saved to disk ✅
- Automated backups every day ✅
