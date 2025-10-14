# ACE Service - KPI Dashboard

**Service:** ACE Service (Agentic Context Engineering)
**Port:** 8050
**Version:** 2.0.0
**Status:** Production Ready

---

## 📊 Key Performance Indicators (KPIs)

### 1. Business Impact KPIs

#### 🎯 Effectiveness Improvement
- **Metric:** `ace_avg_effectiveness`
- **Type:** Gauge (0.0 - 1.0)
- **Current:** Not yet measured (awaiting integration)
- **Baseline:** 0.70 - 0.75 (without ACE)
- **Target:** 0.78 - 0.85 (with ACE)
- **Improvement Goal:** **+8% to +15%**
- **Measurement:** `AVG(effectiveness) FROM ace_trajectory_log`
- **Query:**
  ```sql
  SELECT AVG(effectiveness) as avg_effectiveness
  FROM ace_trajectory_log
  WHERE created_at > NOW() - INTERVAL '30 days';
  ```

#### ✅ Success Rate
- **Metric:** `ace_success_rate`
- **Type:** Gauge (percentage)
- **Target:** > 90%
- **Measurement:** `AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)`
- **Query:**
  ```sql
  SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100 as success_rate
  FROM ace_trajectory_log
  WHERE created_at > NOW() - INTERVAL '30 days';
  ```

---

### 2. Learning & Growth KPIs

#### 📚 Total Playbooks
- **Metric:** `ace_playbooks_total`
- **Type:** Counter
- **Current:** 2 (sample data)
- **Target:** > 50 playbooks
- **Indicates:** Platform-wide ACE adoption
- **Query:**
  ```sql
  SELECT COUNT(DISTINCT task_type) as total_playbooks
  FROM ace_playbooks;
  ```

#### 🏢 Active Modules
- **Metric:** `ace_active_modules`
- **Type:** Gauge
- **Current:** 0 (ready for integration)
- **Target:** > 5 modules
- **Measurement:** Count of distinct modules using ACE
- **Query:**
  ```sql
  SELECT COUNT(DISTINCT module_name) as active_modules
  FROM ace_playbooks
  WHERE module_name IS NOT NULL;
  ```

#### 📈 Playbook Evolution
- **Metric:** `ace_playbook_versions_avg`
- **Type:** Gauge
- **Target:** > 3 versions per playbook
- **Indicates:** Active learning and improvement
- **Query:**
  ```sql
  SELECT AVG(max_version) as avg_versions
  FROM (
    SELECT task_type, MAX(version) as max_version
    FROM ace_playbooks
    GROUP BY task_type
  ) t;
  ```

#### 🧠 Knowledge Growth
- **Metric:** `ace_knowledge_growth`
- **Type:** Gauge
- **Calculation:** Average of (strategies + patterns + domain knowledge)
- **Target:** Continuous growth
- **Query:**
  ```sql
  SELECT AVG(
    jsonb_array_length(playbook->'strategies') +
    jsonb_array_length(playbook->'patterns') +
    jsonb_array_length(playbook->'domain_knowledge')
  ) as knowledge_growth
  FROM ace_playbooks
  WHERE version = (SELECT MAX(version) FROM ace_playbooks p2 WHERE p2.task_type = ace_playbooks.task_type);
  ```

---

### 3. Operational KPIs

#### 📝 Total Trajectories
- **Metric:** `ace_trajectories_total`
- **Type:** Counter
- **Current:** 0 (awaiting integration)
- **Target:** > 1,000 trajectories
- **Indicates:** System usage and data collection
- **Query:**
  ```sql
  SELECT COUNT(*) as total_trajectories
  FROM ace_trajectory_log;
  ```

#### ⚡ API Request Rate
- **Metric:** `ace_api_requests_total`
- **Type:** Counter
- **Labels:** endpoint, method, status
- **Target:** Varies by module adoption
- **Prometheus:** `rate(ace_api_requests_total[5m])`

#### ⏱️ API Response Time
- **Metric:** `ace_api_duration_seconds`
- **Type:** Histogram
- **Targets:**
  - P50: < 100ms
  - P95: < 500ms
  - P99: < 1s
- **Prometheus:** `histogram_quantile(0.95, ace_api_duration_seconds)`

#### 🔌 Database Connections
- **Metric:** `ace_database_connections`
- **Type:** Gauge
- **Current:** N/A (service not started)
- **Warning:** 15 connections
- **Critical:** 19 connections
- **Max:** 20 connections (configured)
- **Query:**
  ```sql
  SELECT count(*) as active_connections
  FROM pg_stat_activity
  WHERE datname = 'postgres'
    AND application_name LIKE '%ace%';
  ```

---

## 📈 Performance Targets

### Baseline (Without ACE)
```
Task Effectiveness:    0.70 - 0.75  (70-75%)
Success Rate:          75% - 80%
Learning:              None (static)
Knowledge Sharing:     None
```

### Target (With ACE)
```
Task Effectiveness:    0.78 - 0.85  (78-85%)  ← +8-15% improvement
Success Rate:          85% - 90%              ← +10-15% improvement
Learning:              Continuous
Knowledge Sharing:     Cross-module
```

### Learning Timeline
```
Executions      Expected Behavior
──────────────────────────────────────────────────────
1-10            Initial learning, playbook v1-2
10-50           Patterns emerging, effectiveness rising
50-100          Stable improvement, +8-15% achieved
100+            Continuous refinement, high performance
```

---

## 🔍 Real-Time Monitoring

### Via Service API

```bash
# Overall statistics
curl http://localhost:8050/stats
{
  "total_playbooks": 5,
  "total_trajectories": 123,
  "avg_effectiveness": 0.87,
  "success_rate": 0.92,
  "uptime_seconds": 86400
}

# Full analytics
curl http://localhost:8050/api/v1/ace/analytics
{
  "total_playbooks": 5,
  "active_modules": ["scenario_intelligence", "ai_orchestration"],
  "total_trajectories": 123,
  "success_rate": 0.92,
  "avg_effectiveness": 0.87,
  "top_performers": [
    {"task_type": "scenario_L1_BIA", "effectiveness": 0.95},
    {"task_type": "ai_task_delegation", "effectiveness": 0.90}
  ]
}
```

### Via Supabase Queries

```sql
-- Dashboard: Overall Performance
SELECT
  COUNT(DISTINCT task_type) as total_playbooks,
  COUNT(DISTINCT module_name) as active_modules,
  (SELECT COUNT(*) FROM ace_trajectory_log) as total_trajectories,
  AVG(success_rate) as avg_success_rate,
  AVG(avg_effectiveness) as avg_effectiveness
FROM ace_playbooks;

-- Dashboard: Top Performers
SELECT
  task_type,
  module_name,
  version,
  usage_count,
  success_rate,
  avg_effectiveness
FROM ace_playbooks
WHERE version = (SELECT MAX(version) FROM ace_playbooks p2 WHERE p2.task_type = ace_playbooks.task_type)
ORDER BY avg_effectiveness DESC
LIMIT 10;

-- Dashboard: Recent Activity
SELECT
  task_type,
  success,
  effectiveness,
  created_at
FROM ace_trajectory_log
ORDER BY created_at DESC
LIMIT 20;

-- Dashboard: Learning Progress
SELECT
  task_type,
  version,
  usage_count,
  success_rate,
  avg_effectiveness,
  created_at
FROM ace_playbooks
ORDER BY task_type, version;
```

---

## 🎯 KPI Targets Summary

| KPI | Current | Target | Status |
|-----|---------|--------|--------|
| **Effectiveness** | N/A | 0.78-0.85 | ⏳ Awaiting integration |
| **Success Rate** | N/A | > 90% | ⏳ Awaiting integration |
| **Total Playbooks** | 2 | > 50 | 🟡 4% of target |
| **Active Modules** | 0 | > 5 | 🟡 Ready for integration |
| **Trajectories** | 0 | > 1,000 | 🟡 Ready to collect |
| **Playbook Versions** | 1.0 | > 3.0 | 🟡 Initial state |
| **API P95 Latency** | N/A | < 500ms | ⏳ Will measure |
| **DB Connections** | N/A | < 15 | ⏳ Will monitor |

**Legend:**
- 🟢 Green: Meeting target
- 🟡 Yellow: In progress / Ready
- 🔴 Red: Below target
- ⏳ Pending: Awaiting data

---

## 📊 Grafana Dashboard (Future)

### Recommended Panels

1. **Effectiveness Over Time**
   - Line chart
   - Metric: `ace_avg_effectiveness`
   - Group by: `task_type`, `module_name`

2. **Success Rate by Module**
   - Bar chart
   - Metric: `ace_success_rate`
   - Group by: `module_name`

3. **Playbook Evolution**
   - Line chart
   - Metric: `ace_playbook_versions_avg`
   - Shows learning progress

4. **API Performance**
   - Histogram
   - Metric: `ace_api_duration_seconds`
   - P50, P95, P99 quantiles

5. **Active Modules**
   - Gauge
   - Metric: `ace_active_modules`
   - Target: > 5

6. **Knowledge Growth**
   - Area chart
   - Metric: `ace_knowledge_growth`
   - Cumulative strategies + patterns + knowledge

7. **Recent Trajectories**
   - Table
   - Source: `ace_trajectory_log`
   - Columns: task_type, success, effectiveness, timestamp

---

## 🚦 Alerting Rules

### Critical Alerts

```yaml
# Success rate drops below 80%
- alert: ACESuccessRateLow
  expr: ace_success_rate < 0.80
  for: 5m
  severity: critical
  description: ACE success rate is {{ $value | humanizePercentage }}

# Database connection pool exhausted
- alert: ACEDatabaseConnectionsHigh
  expr: ace_database_connections > 18
  for: 1m
  severity: critical
  description: ACE using {{ $value }} of 20 database connections
```

### Warning Alerts

```yaml
# Effectiveness below target
- alert: ACEEffectivenessLow
  expr: ace_avg_effectiveness < 0.75
  for: 10m
  severity: warning
  description: ACE effectiveness is {{ $value | humanize }}

# API latency high
- alert: ACEAPILatencyHigh
  expr: histogram_quantile(0.95, ace_api_duration_seconds) > 0.5
  for: 5m
  severity: warning
  description: ACE API P95 latency is {{ $value }}s
```

---

## 📋 KPI Checklist for Integration

When integrating a new module with ACE:

- [ ] Module registers with unique `module_name`
- [ ] Tasks use descriptive `task_type` names
- [ ] Effectiveness scores (0-1) are returned
- [ ] Success/failure is tracked
- [ ] Check playbook creation in Supabase
- [ ] Monitor first 10 executions
- [ ] Verify playbook evolution (version increases)
- [ ] Track effectiveness improvement over time
- [ ] Measure baseline vs ACE performance
- [ ] Document results in module's README

---

## 🎯 Success Criteria

ACE Service is considered successful when:

1. ✅ **5+ modules** are actively using ACE
2. ✅ **Average effectiveness** reaches 0.80+
3. ✅ **Success rate** stays above 90%
4. ✅ **Playbooks evolve** to version 3+ on average
5. ✅ **Measurable improvement** of +8-15% is demonstrated
6. ✅ **API performance** meets SLA (P95 < 500ms)
7. ✅ **Knowledge sharing** across modules is observed
8. ✅ **Continuous learning** is evident in metrics

---

**Created:** 2025-10-15
**Status:** Production Ready
**Next:** Start service and integrate modules
