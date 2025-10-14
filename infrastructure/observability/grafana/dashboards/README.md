# Platform Services Grafana Dashboards

**Production-ready monitoring dashboards for all 6 platform services**

## Overview

This directory contains comprehensive Grafana dashboard configurations for monitoring the entire platform-services ecosystem. All dashboards are designed with dark theme, auto-refresh (30s), and production-grade alerting.

## Dashboard Files

### 1. **platform-services-overview.json** - Main Unified Dashboard
The master dashboard providing a bird's-eye view of all platform services.

**Key Features:**
- Total requests across all services
- Overall success rate and error tracking
- Average response time (p95)
- Active services gauge (6/6)
- Individual service health sections

**Panels:**
- **Overview Row**: Total requests/sec, Success rate, Response time, Active services
- **Process Analytics Row**: Patterns discovered, Deviations detected, Performance analyses, Processing time
- **Compliance Monitoring Row**: ISO 22301 score, Active alerts, Services discovered, Auto-fixes
- **Living Docs Row**: AI generations, Quality scores, Personalization requests, Search queries
- **Community Services Row**: Portal users, Marketplace transactions, Specialists, Projects
- **Digital Twin Row**: Sync status, Entity count, Data quality, CRM/ERP connections
- **ML Pipeline Row**: Predictions, Model accuracy, Training jobs, Inference time

**Dashboard UID:** `platform-services-overview`

---

### 2. **process-analytics.json** - Process Mining Detailed Dashboard
Deep-dive monitoring for process analytics and mining service.

**Key Metrics:**
- Service status and health
- Pattern discovery by type (sequence, parallel, loop, skip, timing)
- Deviation detection by severity (critical, high, medium, low)
- Process executions analyzed by status
- Analysis performance metrics

**Dashboard UID:** `process-analytics-detailed`

**Port:** 8780

**Key Prometheus Metrics:**
```
process_analytics_requests_total
process_analytics_patterns_discovered
process_analytics_deviations_detected
process_analytics_executions_analyzed
process_analytics_analysis_duration_seconds
process_analytics_active_analyses
```

---

### 3. **compliance-monitoring.json** - ISO 22301 Compliance Dashboard
Real-time compliance monitoring and automated fixes tracking.

**Key Metrics:**
- ISO 22301 compliance score (0-100%)
- Active compliance alerts
- Services discovered
- Auto-fixes applied
- Compliance violations by type
- Compliance score trends

**Dashboard UID:** `compliance-monitoring-detailed`

**Port:** 8779

**Key Prometheus Metrics:**
```
compliance_monitoring_iso22301_score
compliance_monitoring_active_alerts
compliance_monitoring_services_discovered
compliance_monitoring_auto_fixes_applied
compliance_monitoring_violations_total
```

---

### 4. **living-docs.json** - Living Documentation Dashboard
AI-powered documentation generation and quality monitoring.

**Key Metrics:**
- AI generations (24h)
- Average quality score
- Personalization requests
- Search queries
- Generation duration by type
- Cache hit/miss ratio
- Page views and engagement
- Knowledge gaps and improvements queued

**Dashboard UID:** `living-docs-detailed`

**Port:** 8034

**Key Prometheus Metrics:**
```
living_docs_ai_generations
living_docs_quality_score
living_docs_personalized_requests
living_docs_searches_total
living_docs_personalization_cache_hits
living_docs_page_views
living_docs_gaps_detected
```

---

### 5. **community-services.json** - Community Portal & Marketplace Dashboard
Combined monitoring for community portal and marketplace services.

**Community Portal Metrics:**
- Active users
- Specialists registered
- Projects active
- Portal engagement score
- Portal activity trends

**Marketplace Metrics:**
- Transactions (24h)
- Active listings
- Total revenue
- Marketplace health score
- Transaction rate by type

**Dashboard UID:** `community-services-detailed`

**Ports:** 8031 (Portal), 8032 (Marketplace)

**Key Prometheus Metrics:**
```
community_portal_active_users
community_portal_specialists_registered
community_portal_projects_active
community_marketplace_transactions_total
community_marketplace_active_listings
community_marketplace_revenue_total
```

---

### 6. **digital-twin.json** - Digital Twin Synchronization Dashboard
Monitoring for CRM/ERP synchronization and data quality.

**Key Metrics:**
- Sync status (Synced/Pending)
- Entity count
- Data quality score (0-100%)
- Pending sync operations
- CRM connection (Salesforce)
- ERP connection (Odoo)
- Marketing connection (HubSpot)
- Sync operations rate
- Entity resolution and matching
- Match accuracy and conflicts

**Dashboard UID:** `digital-twin-detailed`

**Port:** 8090

**Key Prometheus Metrics:**
```
digital_twin_sync_status
digital_twin_entity_count
digital_twin_data_quality_score
digital_twin_crm_connection_status
digital_twin_erp_connection_status
digital_twin_entities_matched_total
digital_twin_match_accuracy
```

---

### 7. **ml-pipeline.json** - ML Pipeline & Predictions Dashboard
Machine learning model monitoring and prediction tracking.

**Key Metrics:**
- Predictions generated (24h)
- Model accuracy (0-100%)
- Prediction rate
- Inference time (p95)
- Training jobs status
- Active training jobs
- Model precision, recall, F1 score
- Model drift detection
- Accuracy trends by model type

**Dashboard UID:** `ml-pipeline-detailed`

**Port:** TBD (new service)

**Key Prometheus Metrics:**
```
ml_pipeline_predictions_generated
ml_pipeline_model_accuracy
ml_pipeline_inference_duration_seconds
ml_pipeline_training_jobs_total
ml_pipeline_active_training_jobs
ml_pipeline_model_precision
ml_pipeline_model_recall
ml_pipeline_model_drift_detected
```

---

## Installation & Import Instructions

### Method 1: Grafana UI Import

1. **Login to Grafana**
   ```
   http://localhost:3000
   Default credentials: admin/admin
   ```

2. **Import Dashboard**
   - Click **+ → Import** in the left sidebar
   - Click **Upload JSON file**
   - Select one of the dashboard JSON files
   - Choose **Prometheus** as the datasource
   - Click **Import**

3. **Verify Dashboard**
   - Dashboard should appear immediately
   - Check that all panels are loading data
   - Verify auto-refresh is set to 30s

### Method 2: Provisioning (Automated)

For production deployments, use Grafana provisioning to automatically load dashboards.

1. **Copy dashboards to Grafana provisioning directory**
   ```bash
   # Docker deployment
   cp *.json /var/lib/grafana/dashboards/

   # Kubernetes deployment
   kubectl create configmap grafana-dashboards \
     --from-file=./dashboards/ \
     -n monitoring
   ```

2. **Configure Grafana provisioning** (`/etc/grafana/provisioning/dashboards/default.yaml`):
   ```yaml
   apiVersion: 1

   providers:
     - name: 'Platform Services'
       orgId: 1
       folder: 'Platform Services'
       type: file
       disableDeletion: false
       updateIntervalSeconds: 10
       allowUiUpdates: true
       options:
         path: /var/lib/grafana/dashboards
   ```

3. **Restart Grafana**
   ```bash
   # Docker
   docker restart grafana

   # Systemd
   sudo systemctl restart grafana-server
   ```

### Method 3: API Import (Scripted)

Use this bash script to import all dashboards via Grafana API:

```bash
#!/bin/bash
# import-dashboards.sh

GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"

for dashboard in *.json; do
  echo "Importing $dashboard..."

  curl -X POST \
    -H "Content-Type: application/json" \
    -u "$GRAFANA_USER:$GRAFANA_PASS" \
    "$GRAFANA_URL/api/dashboards/db" \
    -d @"$dashboard"

  echo ""
done

echo "All dashboards imported!"
```

Run it:
```bash
chmod +x import-dashboards.sh
./import-dashboards.sh
```

---

## Datasource Configuration

### Configure Prometheus Datasource

**Option 1: Via Grafana UI**

1. Go to **Configuration → Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   - **Name:** Prometheus
   - **URL:** `http://prometheus:9090` (or your Prometheus URL)
   - **Scrape interval:** 15s
   - **Query timeout:** 60s
5. Click **Save & Test**

**Option 2: Via Provisioning**

Use the provided datasource configuration file:

```bash
cp ../datasources/prometheus.yaml /etc/grafana/provisioning/datasources/
```

File location: `/infrastructure/observability/grafana/datasources/prometheus.yaml`

---

## Dashboard Features

### Common Features Across All Dashboards

✅ **Auto-refresh**: 30 seconds (configurable: 30s, 1m, 5m, 15m, 30m, 1h)
✅ **Time range selector**: Last 1h, 6h, 24h, 7d, 30d, custom
✅ **Service filter**: Filter by specific service (where applicable)
✅ **Dark theme**: Production-ready dark theme
✅ **Links**: Quick navigation between related dashboards
✅ **Responsive**: Works on desktop, tablet, and mobile
✅ **Alerts**: Pre-configured thresholds for alerting

### Panel Types Used

- **Stat**: Single value metrics with thresholds
- **Gauge**: Visual indicators for scores and percentages
- **Timeseries**: Line/area charts for trends
- **Piechart**: Distribution visualizations
- **Table**: Detailed data views
- **Bargraph**: Comparative metrics

---

## Alerting Configuration

Dashboards include pre-configured threshold-based alerts:

### Critical Alerts (Red)

- **Success Rate** < 95%
- **ISO 22301 Compliance** < 70%
- **Model Accuracy** < 70%
- **Data Quality Score** < 70%

### Warning Alerts (Yellow/Orange)

- **Success Rate** 95-99%
- **Compliance Score** 70-90%
- **Active Alerts** > 5
- **Deviations** > 10

### Healthy (Green)

- **Success Rate** > 99%
- **Compliance Score** > 90%
- **Model Accuracy** > 85%
- **All services UP**

---

## Prometheus Metrics Reference

### General Metrics (All Services)

```promql
# Request metrics
{service}_requests_total{method, endpoint, status}
{service}_request_duration_seconds{method, endpoint}
{service}_active_tasks

# Error tracking
{service}_errors_total{type}
```

### Service-Specific Metrics

See individual dashboard sections above for service-specific metrics.

---

## Accessing Dashboards

After import, dashboards are available at:

- **Main Overview**: http://localhost:3000/d/platform-services-overview
- **Process Analytics**: http://localhost:3000/d/process-analytics-detailed
- **Compliance**: http://localhost:3000/d/compliance-monitoring-detailed
- **Living Docs**: http://localhost:3000/d/living-docs-detailed
- **Community**: http://localhost:3000/d/community-services-detailed
- **Digital Twin**: http://localhost:3000/d/digital-twin-detailed
- **ML Pipeline**: http://localhost:3000/d/ml-pipeline-detailed

---

## Troubleshooting

### No Data Displayed

1. **Check Prometheus datasource**:
   - Go to Configuration → Data Sources → Prometheus
   - Click "Save & Test"
   - Ensure it shows "Data source is working"

2. **Verify Prometheus is scraping services**:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```
   Check that all platform services are listed and UP.

3. **Check service /metrics endpoints**:
   ```bash
   # Process Analytics
   curl http://localhost:8780/metrics

   # Living Docs
   curl http://localhost:8034/metrics

   # Compliance Monitoring
   curl http://localhost:8779/metrics
   ```

4. **Verify Prometheus configuration** (`prometheus.yml`):
   ```yaml
   scrape_configs:
     - job_name: 'process_analytics'
       static_configs:
         - targets: ['process-analytics:8780']

     - job_name: 'living_docs'
       static_configs:
         - targets: ['living-docs:8034']

     # ... other services
   ```

### Dashboard Shows "N/A" or Empty Panels

- **Time Range**: Ensure time range includes data (try "Last 24h")
- **Metrics Exist**: Run Prometheus query directly to verify metric exists
- **Query Syntax**: Check browser console for PromQL errors

### Performance Issues

- **Reduce Time Range**: Use shorter ranges (6h instead of 7d)
- **Increase Refresh Interval**: Change from 30s to 5m
- **Optimize Queries**: Use recording rules in Prometheus for complex queries

---

## Customization

### Modifying Dashboards

1. Open dashboard in Grafana
2. Click **Dashboard settings** (⚙️ icon)
3. Edit panels, add new rows, customize thresholds
4. Click **Save dashboard**
5. **Export JSON** to save your changes

### Adding Custom Panels

```json
{
  "id": <unique_id>,
  "type": "timeseries",
  "title": "My Custom Panel",
  "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
  "targets": [
    {
      "expr": "your_prometheus_query",
      "legendFormat": "{{label}}",
      "refId": "A"
    }
  ]
}
```

### Creating New Dashboards

Use existing dashboards as templates. Copy structure and modify:
- Change `uid` to unique value
- Update `title`
- Modify `targets[].expr` with your metrics
- Adjust thresholds and colors

---

## Production Deployment Checklist

- [ ] All 7 dashboards imported successfully
- [ ] Prometheus datasource configured and tested
- [ ] All panels showing data (not "N/A")
- [ ] Alert thresholds configured appropriately
- [ ] Auto-refresh enabled (30s)
- [ ] Dashboard links working correctly
- [ ] Access controls configured (if using auth)
- [ ] Dashboards added to Grafana provisioning (for GitOps)
- [ ] Backup exported JSON files
- [ ] Team trained on dashboard usage

---

## Support & Documentation

**Related Documentation:**
- `/infrastructure/observability/prometheus/prometheus.yml` - Prometheus config
- `/platform-services/PLATFORM_SERVICES_ANALYSIS.md` - Service architecture
- `/CURRENT_STATE_MEMO.md` - Priority 3.2 requirements

**Grafana Resources:**
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/)
- [Prometheus Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)

**Issues & Questions:**
- Check `/infrastructure/observability/grafana/dashboards/` for updates
- Review Prometheus targets: http://localhost:9090/targets
- Check service health endpoints

---

**Last Updated:** 2025-10-11
**Version:** 1.0
**Status:** Production Ready ✅
