# 🔗 Process Analytics - Integration & Reporting Guide

**Service:** Process Analytics
**Port:** 8780
**Database:** `process_analytics.*` schema in Supabase ✅ APPLIED
**Purpose:** Advanced process mining and bottleneck detection
**Type:** **STANDALONE ANALYTICS SERVICE** (не привязан к Grafana или Prometheus)

---

## 🎯 Purpose & Architecture

### What This Service Does

**Process Analytics** - это **автономный аналитический сервис** для глубокого анализа процессов:

1. **Process Discovery** - Обнаруживает фактические потоки процессов из логов
2. **Bottleneck Detection** - Находит узкие места и медленные шаги
3. **Pattern Mining** - Обнаруживает паттерны (последовательности, циклы, параллели)
4. **Deviation Analysis** - Детектирует отклонения от ожидаемого поведения
5. **Performance Analytics** - Вычисляет метрики производительности
6. **Predictive Insights** - Предсказывает проблемы и генерирует рекомендации

### Architecture Type

**НЕ Prometheus exporter!**
**НЕ Grafana dashboard!**

Это **STANDALONE REST API** с собственной базой данных и логикой анализа.

```
┌─────────────────┐
│ Process         │  Logs executions
│ Workflows       │───────────┐
│ (BIA, Risk, etc)│           │
└─────────────────┘           │
                              ▼
┌─────────────────┐     ┌──────────────────┐
│ workflow_       │────▶│ Process          │
│ intelligence    │ API │ Analytics        │
└─────────────────┘     │ Service :8780    │
                        └──────────────────┘
┌─────────────────┐            │
│ AI              │            │ Stores
│ Orchestrator    │            │ analysis
└─────────────────┘            ▼
        │            ┌──────────────────┐
        │            │ Supabase         │
        │            │ process_analytics│
        │            │ schema           │
        └───────────▶└──────────────────┘
           Queries insights
```

---

## 📊 Database Schema (Applied ✅)

### Schema: `process_analytics.*`

**6 Tables:**

1. **executions** - Process instances (workflow runs)
   - id, process_id, execution_id, start_time, end_time, status, duration

2. **events** - Individual steps within executions
   - id, execution_id, event_type, step_name, timestamp, actor, data

3. **patterns** - Discovered process patterns
   - id, process_id, pattern_type (sequence/parallel/loop/skip), frequency, confidence

4. **deviations** - Detected deviations
   - id, execution_id, deviation_type (timing/sequence/quality), severity, impact_score

5. **bottlenecks** - Identified bottlenecks
   - id, process_id, step_name, bottleneck_type, avg_duration, impact_score

6. **performance_snapshots** - Time-series aggregates
   - id, process_id, snapshot_time, period (hourly/daily), metrics

**3 Views:**
- `active_executions` - Currently running processes
- `recent_bottlenecks` - Last 7 days
- `process_health` - 30-day health metrics

---

## 🔌 Integration Points

### 1. Workflow Intelligence (Primary Consumer)

**Location:** `intelligent-core/workflow_intelligence/`

**Integration:**
```python
import httpx

# Log workflow execution
async def log_workflow_execution(process_id: str, execution_id: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8780/api/v1/process-mining/log-execution",
            json={
                "process_id": process_id,
                "execution_id": execution_id,
                "start_time": datetime.utcnow().isoformat(),
                "status": "running",
                "executed_by": "user@example.com"
            }
        )

# Log workflow event
async def log_workflow_event(execution_id: str, step_name: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8780/api/v1/process-mining/log-event",
            json={
                "execution_id": execution_id,
                "event_type": "checkpoint",
                "step_name": step_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

**When to log:**
- Journey start → `log-execution` (status="running")
- Each action completion → `log-event`
- Journey completion → update execution (status="completed")

---

### 2. AI Orchestrator (Consumer of Insights)

**Location:** `intelligent-core/orchestration/ai-orchestration/`

**Integration:**
```python
import httpx

# Get process insights for decision-making
async def get_process_insights(process_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8780/api/v1/process-mining/comprehensive-analysis",
            json={
                "process_id": process_id,
                "include_patterns": True,
                "include_deviations": True,
                "include_performance": True
            }
        )
        return response.json()

# Use insights for optimization
insights = await get_process_insights("bia_workflow")
if insights["bottlenecks"]:
    bottleneck = insights["bottlenecks"][0]
    # Adjust workflow based on bottleneck
    await orchestrator.optimize_step(bottleneck["step_name"])
```

**Use cases:**
- Identify slow steps before delegating tasks
- Detect frequently failing processes
- Optimize task allocation based on historical performance

---

### 3. MIO Manager (❌ NO INTEGRATION)

**Location:** `infrastructure/AI-office-infrastructure/mio-manager/`

**Status:** ❌ **НЕТ ИНТЕГРАЦИИ**

**Why:**
- MIO Manager - это monitoring orchestrator (Grafana/Prometheus)
- Process Analytics - это process mining service (отдельный домен)
- Разные области ответственности

**If integration needed (future):**
- MIO Manager could **query** Process Analytics for reports
- Example: "Show me bottlenecks in last 7 days" → display in MIO dashboard

---

### 4. Compliance Monitoring (Potential Consumer)

**Location:** `infrastructure/observability/services/compliance-monitoring/`

**Potential integration:**
```python
# Query process deviations for compliance checks
async def check_process_compliance(process_id: str):
    response = await client.get(
        f"http://localhost:8780/api/v1/process-mining/processes/{process_id}/summary"
    )
    summary = response.json()

    # Check if process meets compliance thresholds
    if summary["success_rate"] < 95:
        await create_compliance_alert("Low process success rate")
```

---

## 📈 Reporting & Publishing

### Where Reports Go

**Process Analytics does NOT push to:**
- ❌ Prometheus (not a metrics exporter)
- ❌ Grafana (not a data source - yet)
- ❌ External systems automatically

**Process Analytics provides:**
- ✅ REST API for querying insights
- ✅ Database tables for SQL queries
- ✅ JSON responses with analysis results

### How to Access Reports

#### 1. Via REST API

```bash
# Get process summary
curl http://localhost:8780/api/v1/process-mining/processes/bia_workflow/summary

# Get comprehensive analysis
curl -X POST http://localhost:8780/api/v1/process-mining/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "process_id": "bia_workflow",
    "include_patterns": true,
    "include_deviations": true
  }'

# Health check
curl http://localhost:8780/api/v1/process-mining/health
```

#### 2. Via Database Queries

```sql
-- Get active processes
SELECT * FROM process_analytics.active_executions;

-- Get recent bottlenecks
SELECT * FROM process_analytics.recent_bottlenecks
WHERE impact_score > 7;

-- Get process health
SELECT * FROM process_analytics.process_health
WHERE success_rate < 80;

-- Get process summary (via function)
SELECT * FROM process_analytics.get_process_summary('bia_workflow', 30);
```

#### 3. Via Grafana (Future Integration)

**Not implemented yet, but possible:**

1. Add PostgreSQL data source in Grafana pointing to Supabase
2. Create dashboard with SQL queries to `process_analytics.*` tables
3. Visualize bottlenecks, patterns, performance over time

**Example dashboard panels:**
- Process success rate over time
- Top 5 bottlenecks by impact
- Deviation count trend
- Average execution duration

---

## 🔄 Data Flow

### 1. Logging Flow (Ingestion)

```
Workflow Execution
        │
        ├─ Start → POST /log-execution (status=running)
        │
        ├─ Step 1 → POST /log-event (event_type=checkpoint)
        │
        ├─ Step 2 → POST /log-event
        │
        └─ Complete → POST /log-execution (status=completed)
                            │
                            ▼
                    process_analytics.executions
                    process_analytics.events
```

### 2. Analysis Flow (Processing)

```
On Request
    │
    └─ POST /comprehensive-analysis
            │
            ├─ Query executions & events from DB
            │
            ├─ Run ProcessMiningEngine:
            │   ├─ analyze_process_performance()
            │   ├─ discover_patterns()
            │   └─ detect_deviations()
            │
            ├─ Store discovered patterns
            ├─ Store detected bottlenecks
            │
            └─ Return JSON response with insights
```

### 3. Consumption Flow (Reporting)

```
Consumer Service
    │
    ├─ AI Orchestrator
    │   └─ GET /processes/{id}/summary → Use for task optimization
    │
    ├─ Compliance Monitoring
    │   └─ Query deviations → Create compliance alerts
    │
    └─ External Dashboard (future)
        └─ SQL queries → Visualize trends
```

---

## 🎯 API Endpoints Reference

### Logging Endpoints

```
POST /api/v1/process-mining/log-execution
  Body: {process_id, execution_id, start_time, status, ...}
  Purpose: Log workflow execution start/completion

POST /api/v1/process-mining/log-event
  Body: {execution_id, event_type, step_name, timestamp, ...}
  Purpose: Log individual workflow steps/events
```

### Analysis Endpoints

```
POST /api/v1/process-mining/analyze-performance/{process_id}
  Purpose: Get performance metrics (duration, success rate, etc.)

POST /api/v1/process-mining/discover-patterns/{process_id}
  Purpose: Discover process patterns (sequences, loops, parallels)

POST /api/v1/process-mining/detect-deviations/{process_id}
  Purpose: Detect deviations from expected behavior

POST /api/v1/process-mining/comprehensive-analysis
  Body: {process_id, include_patterns, include_deviations, ...}
  Purpose: Full analysis with all insights
```

### Query Endpoints

```
GET /api/v1/process-mining/processes/{process_id}/summary
  Purpose: Get summary for specific process (30 days)

GET /api/v1/process-mining/health
  Purpose: Service health check
```

---

## 🚀 Deployment

### Docker Compose (in observability stack)

```yaml
# infrastructure/observability/docker-compose.monitoring.yml
process-analytics:
  build:
    context: ./services/process-analytics
    dockerfile: Dockerfile
  container_name: bcm-process-analytics
  ports:
    - "8780:8780"
  environment:
    - DATABASE_URL=postgresql://...  # Supabase connection
    - PORT=8780
  restart: unless-stopped
  networks:
    - monitoring
```

### Standalone Run

```bash
cd infrastructure/observability/services/process-analytics
python3 main.py

# Service starts on http://localhost:8780
# Health check: curl http://localhost:8780/api/v1/process-mining/health
```

---

## 📊 Monitoring Process Analytics Itself

**Meta question:** How do we monitor the monitoring service?

### Option 1: Add /metrics endpoint (Future)

```python
from prometheus_client import Counter, Histogram, generate_latest

analysis_requests = Counter('process_analytics_requests_total', 'Total analysis requests')
analysis_duration = Histogram('process_analytics_duration_seconds', 'Analysis duration')

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

Then Prometheus can scrape it.

### Option 2: Use observability schema (Current)

Process Analytics already logs to Supabase, so:
- Compliance-monitoring can monitor it
- Query `process_analytics.executions` for service health

---

## 🔗 Coordination with Other Systems

### vs MIO Manager

| Aspect | Process Analytics | MIO Manager |
|--------|-------------------|-------------|
| **Purpose** | Process mining & analysis | Monitoring orchestration |
| **Domain** | Workflow optimization | Infrastructure monitoring |
| **Input** | Workflow execution logs | Prometheus metrics |
| **Output** | Process insights (API) | Grafana dashboards, alerts |
| **Integration** | ❌ None currently | Could query PA for reports |

**Relationship:** SEPARATE DOMAINS
**Future:** MIO Manager could display Process Analytics reports in dashboards

### vs Workflow Intelligence

| Aspect | Process Analytics | Workflow Intelligence |
|--------|-------------------|----------------------|
| **Purpose** | Analyze past executions | Execute workflows |
| **Role** | Analytics (passive) | Orchestration (active) |
| **Integration** | ✅ Receives logs from WI | ✅ Logs executions to PA |

**Relationship:** PRODUCER-CONSUMER
Workflow Intelligence **produces** execution data → Process Analytics **consumes** and analyzes

### vs AI Orchestrator

| Aspect | Process Analytics | AI Orchestrator |
|--------|-------------------|-----------------|
| **Purpose** | Identify patterns & bottlenecks | Decide task delegation |
| **Role** | Insights provider | Decision maker |
| **Integration** | ✅ Provides insights via API | ✅ Queries PA for optimization |

**Relationship:** ADVISOR-DECISION MAKER
Process Analytics **advises** → AI Orchestrator **acts**

---

## 📝 Summary

### Key Points

1. **Standalone Service** - Not a Prometheus exporter or Grafana dashboard
2. **REST API** - Provides insights via HTTP endpoints
3. **Database Storage** - Stores analysis in `process_analytics.*` schema ✅
4. **Async Analysis** - Analyzes on request, not real-time streaming
5. **Multiple Consumers** - Workflow Intelligence logs, AI Orchestrator queries

### Current Integrations

- ✅ **Supabase** - Database storage (schema applied)
- ✅ **Workflow Intelligence** - Can log executions (implementation needed)
- ✅ **AI Orchestrator** - Can query insights (implementation needed)
- ❌ **MIO Manager** - No integration (different domain)
- ❌ **Prometheus** - Not an exporter (could add /metrics)
- ❌ **Grafana** - Not a data source (could connect to Supabase)

### Reporting Channels

1. **REST API** - Primary method (GET/POST endpoints)
2. **SQL Queries** - Direct database access
3. **Future: Grafana** - Visualize via Supabase data source
4. **Future: Scheduled Reports** - Email/Slack summaries

---

**Schema:** ✅ Applied to Supabase
**Service:** Ready to deploy
**Integrations:** Need implementation in consumers
**Next:** Update workflow_intelligence to log executions
