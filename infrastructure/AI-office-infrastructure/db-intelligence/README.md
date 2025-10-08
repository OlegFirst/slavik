# Database Intelligence Specialist 🗄️

**AI-Powered Database Monitoring, Optimization, and Management**

**Status:** ✅ Ready for Deployment
**Version:** 1.0.0
**Port:** 8050
**Location:** AI Office Infrastructure (Infrastructure Management Office)
**Managed By:** AI Orchestrator
**Role:** Database Infrastructure Specialist

---

## Overview

Database Intelligence Specialist - это **AI colleague** в Infrastructure Management Office, который специализируется на мониторинге, анализе и оптимизации всех баз данных платформы.

**Часть AI Office Infrastructure Team:**
- **MIO Manager** (Port 8046) - Координатор и AI мозг
- **Orchestrator** (Port 8090) - Универсальный исполнитель
- **Analytics Specialist** (Port TBD) - Аналитика платформы
- **DB Intelligence Specialist** (Port 8050) - Специалист по базам данных ← YOU ARE HERE
- **Agent Router** (Port TBD) - Маршрутизация запросов

Database Intelligence Specialist provides:

- **Real-time Performance Monitoring** - Track query execution times, connection pools, system resources
- **Intelligent Optimization** - AI-powered suggestions for query improvements
- **Slow Query Detection** - Automatic identification and analysis of slow queries
- **Health Monitoring** - Comprehensive database health checks
- **Table Analytics** - Size, row counts, vacuum status
- **Prometheus Integration** - Metrics export for monitoring dashboards

---

## Architecture

### Service Design

```
Database Intelligence Service
├── db_intelligence_service.py   - Core monitoring engine
├── api.py                       - REST API endpoints
├── security_monitor.py          - Security monitoring & alerts
├── ai_integration.py            - EventBus & AI Foundation integration
├── orchestrator_integration.py  - Direct Orchestrator API client
├── command_handler.py           - Execute Orchestrator commands
├── main.py                      - Service entry point
└── __init__.py                  - Package exports

Integration Architecture:
├── AI Orchestrator (Direct API)
│   ├── Service registration & heartbeat
│   ├── Command polling (optimize, vacuum, reindex, kill)
│   ├── Critical alerts (bypass EventBus)
│   └── Metrics push
├── EventBus (Async Pub/Sub)
│   ├── Health alerts
│   ├── Security notifications
│   └── Optimization suggestions
├── AI Foundation
│   ├── LLM analysis for complex queries
│   └── RAG enrichment for recommendations
├── Prometheus
│   └── Metrics export (/metrics/prometheus)
└── PostgreSQL
    ├── pg_stat_statements monitoring
    ├── RLS policy verification
    └── Admin operations (VACUUM, CREATE INDEX, etc.)
```

### Key Features

**1. Query Performance Monitoring**
- Collects metrics from `pg_stat_statements`
- Tracks execution count, avg/min/max duration
- Identifies slow queries (>1s by default)
- Historical query analysis

**2. AI-Powered Optimization**
- Analyzes query patterns
- Suggests index creation
- Detects full table scans
- Recommends query rewrites
- Estimates performance improvements

**3. Health Monitoring**
- Database connectivity checks
- Connection pool utilization
- System resource usage (CPU, memory, disk)
- Overall health status (healthy/degraded/unhealthy)

**4. Table Statistics**
- Table sizes and row counts
- Dead tuple detection
- Vacuum/analyze status
- Index recommendations

**5. Security Monitoring**
- RLS policy verification
- SQL injection detection
- DOS attack protection
- Deadlock detection
- Failed login monitoring

**6. CLI Admin Access**
- Execute admin commands via REST API
- VACUUM, ANALYZE, REINDEX operations
- Index creation and management
- Query termination
- Running query monitoring
- Database lock detection

**7. Dual Integration Architecture**
- **EventBus** - Async alerts, pub/sub for non-critical notifications
- **Direct Orchestrator API** - Sync commands, service coordination, critical alerts

---

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database/intelligence
pip install -r requirements.txt
```

### 2. Enable pg_stat_statements

```sql
-- In PostgreSQL (requires superuser or rds_superuser)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify
SELECT * FROM pg_stat_statements LIMIT 1;
```

### 3. Run Service

**Standalone:**
```bash
python main.py
```

**With uvicorn:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8050 --reload
```

**With Docker:**
```bash
docker build -t db-intelligence .
docker run -p 8050:8050 db-intelligence
```

### 4. Verify Service

```bash
# Health check
curl http://localhost:8050/health

# Metrics summary
curl http://localhost:8050/metrics

# API documentation
open http://localhost:8050/docs
```

---

## CLI Admin Access

The service provides REST API endpoints for database administration, giving CLI-level access to database tools.

### Execute Admin Commands

```bash
# VACUUM table - cleanup dead tuples
curl -X POST http://localhost:8050/admin/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "vacuum_table",
    "parameters": {"schema": "public", "table": "organizations", "full": false},
    "reason": "Cleanup dead tuples after bulk delete"
  }'

# Create index - optimize query performance
curl -X POST http://localhost:8050/admin/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "create_index",
    "parameters": {
      "schema": "workflow_intelligence",
      "table": "workflows",
      "column": "status",
      "index_name": "idx_workflows_status",
      "concurrent": true
    },
    "reason": "Optimize status filtering queries"
  }'

# Kill long-running query
curl -X POST http://localhost:8050/admin/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "kill_query",
    "parameters": {"pid": 12345},
    "reason": "Query timeout - blocking other operations"
  }'

# ANALYZE table - update statistics
curl -X POST http://localhost:8050/admin/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "analyze_table",
    "parameters": {"schema": "public", "table": "users"},
    "reason": "Update statistics after bulk insert"
  }'
```

### Monitor Running Queries

```bash
# Get all active queries
curl http://localhost:8050/admin/running-queries

# Response
{
  "running_queries": [
    {
      "pid": 12345,
      "user": "postgres",
      "application": "workflow-intelligence",
      "query": "SELECT * FROM workflows WHERE...",
      "duration_ms": 5234.5,
      "wait_event_type": null
    }
  ],
  "count": 1
}
```

### Check Database Locks

```bash
# Get all blocking locks
curl http://localhost:8050/admin/locks

# Response
{
  "locks": [
    {
      "locktype": "relation",
      "pid": 12346,
      "mode": "AccessExclusiveLock",
      "granted": false,
      "query": "ALTER TABLE..."
    }
  ],
  "count": 1,
  "message": "1 locks detected"
}
```

---

## API Endpoints

### Health & Status

**GET /health**
```json
{
  "status": "healthy",
  "postgres_connected": true,
  "redis_connected": true,
  "rabbitmq_connected": true,
  "connection_pool_ok": true,
  "slow_queries_count": 3,
  "active_connections": 12,
  "cpu_percent": 15.4,
  "memory_percent": 42.8,
  "disk_usage_percent": 68.2,
  "timestamp": "2025-10-08T00:10:00Z"
}
```

**GET /metrics**
```json
{
  "service": "db-intelligence",
  "version": "1.0.0",
  "status": "running",
  "total_queries_tracked": 247,
  "slow_queries_count": 5,
  "optimization_suggestions_count": 3,
  "monitoring_interval_seconds": 60,
  "slow_query_threshold_ms": 1000
}
```

### Query Monitoring

**GET /query-metrics?limit=10**
```json
{
  "queries": [
    {
      "query_hash": "1234567890",
      "query_text": "SELECT * FROM organizations WHERE ...",
      "execution_count": 1523,
      "avg_duration_ms": 245.6,
      "max_duration_ms": 1234.5,
      "min_duration_ms": 45.2,
      "total_duration_ms": 374156.8,
      "last_executed": "2025-10-08T00:09:45Z",
      "slow_query": false
    }
  ],
  "total": 10
}
```

**GET /slow-queries?limit=10**
```json
{
  "slow_queries": [
    {
      "query_hash": "9876543210",
      "query_text": "SELECT o.*, COUNT(u.*) FROM organizations o JOIN users u ...",
      "execution_count": 45,
      "avg_duration_ms": 2456.7,
      "max_duration_ms": 8934.2,
      "total_duration_ms": 110551.5,
      "slow_query": true
    }
  ],
  "total": 5,
  "threshold_ms": 1000
}
```

### Optimization

**GET /suggestions?limit=10**
```json
{
  "suggestions": [
    {
      "query_hash": "9876543210",
      "query_text": "SELECT * FROM organizations WHERE name LIKE '%search%'",
      "issue_type": "missing_index",
      "severity": "warning",
      "suggestion": "Query taking >1s. Review execution plan. Avoid SELECT *, specify needed columns only.",
      "estimated_improvement": "20-50% faster",
      "created_at": "2025-10-08T00:05:00Z"
    }
  ],
  "total": 3
}
```

**POST /analyze**
```json
// Request
{
  "query": "SELECT * FROM organizations WHERE created_at > '2025-01-01'"
}

// Response
{
  "query": "SELECT * FROM organizations WHERE created_at > '2025-01-01'",
  "explain": [
    "Seq Scan on organizations  (cost=0.00..1234.56 rows=100 width=256)",
    "  Filter: (created_at > '2025-01-01'::date)"
  ],
  "suggestions": [
    {
      "type": "missing_index",
      "severity": "warning",
      "message": "Sequential scan detected. Consider adding index on created_at."
    }
  ],
  "estimated_cost": 1234.56
}
```

### Table Statistics

**GET /tables**
```json
{
  "tables": [
    {
      "schema": "public",
      "table": "organizations",
      "size": "156 MB",
      "row_count": 45623,
      "dead_rows": 234,
      "last_vacuum": "2025-10-07T22:00:00Z",
      "last_analyze": "2025-10-07T22:00:00Z"
    }
  ],
  "total": 50
}
```

### Configuration

**GET /config**
```json
{
  "monitoring_interval_seconds": 60,
  "slow_query_threshold_ms": 1000,
  "max_stored_metrics": 1000
}
```

**PUT /config?monitoring_interval=120&slow_query_threshold_ms=2000**
```json
{
  "message": "Configuration updated successfully",
  "config": {
    "monitoring_interval_seconds": 120,
    "slow_query_threshold_ms": 2000
  }
}
```

### Prometheus Metrics

**GET /metrics/prometheus**
```
db_health_status 1
db_postgres_connected 1
db_redis_connected 1
db_rabbitmq_connected 1
db_slow_queries_count 3
db_active_connections 12
db_queries_tracked_total 247
db_optimization_suggestions_total 3
db_cpu_percent 15.4
db_memory_percent 42.8
db_disk_usage_percent 68.2
```

---

## Integration with AI Orchestrator

### Service Registration

When started, the service automatically registers with AI Orchestrator:

```bash
export ORCHESTRATOR_URL=http://localhost:8002
python main.py
```

Registration payload:
```json
{
  "service_name": "db-intelligence",
  "service_type": "infrastructure",
  "version": "1.0.0",
  "capabilities": [
    "query_monitoring",
    "performance_analysis",
    "optimization_suggestions",
    "health_monitoring",
    "table_statistics"
  ],
  "endpoints": {
    "health": "/health",
    "metrics": "/metrics",
    "prometheus": "/metrics/prometheus"
  },
  "metadata": {
    "description": "AI-powered database monitoring and optimization",
    "managed_by": "ai-orchestrator",
    "critical": true
  }
}
```

### Orchestrator Integration

The AI Orchestrator can:

1. **Monitor Service Health** - Regular health checks via `/health`
2. **Collect Metrics** - Scrape `/metrics/prometheus` for monitoring
3. **Request Analysis** - Call `/analyze` for query optimization
4. **Get Recommendations** - Fetch `/suggestions` for proactive improvements
5. **Manage Configuration** - Update thresholds via `/config`

### Heartbeat

Service sends heartbeat every 30 seconds to orchestrator:
```bash
POST http://localhost:8002/services/db-intelligence/heartbeat
{
  "status": "healthy",
  "timestamp": "2025-10-08T00:10:00Z"
}
```

---

## Usage Examples

### Python Client

```python
import httpx

class DBIntelligenceClient:
    def __init__(self, base_url="http://localhost:8050"):
        self.base_url = base_url

    async def get_health(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return response.json()

    async def get_slow_queries(self, limit=10):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/slow-queries",
                params={"limit": limit}
            )
            return response.json()

    async def analyze_query(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/analyze",
                json={"query": query}
            )
            return response.json()

# Usage
client = DBIntelligenceClient()
health = await client.get_health()
print(f"Database status: {health['status']}")

slow_queries = await client.get_slow_queries(limit=5)
for query in slow_queries['slow_queries']:
    print(f"Slow query: {query['avg_duration_ms']}ms")
```

### Direct Integration

```python
from infrastructure.database.intelligence import get_db_intelligence

# Get service instance
service = get_db_intelligence()

# Start monitoring
await service.start()

# Get metrics
health = await service.get_health()
print(f"Status: {health['status']}")

slow_queries = await service.get_slow_queries(limit=10)
print(f"Found {len(slow_queries)} slow queries")

suggestions = await service.get_optimization_suggestions()
for suggestion in suggestions:
    print(f"[{suggestion['severity']}] {suggestion['suggestion']}")

# Stop monitoring
await service.stop()
```

---

## Configuration

### Environment Variables

```bash
# Service
DB_INTELLIGENCE_HOST=0.0.0.0
DB_INTELLIGENCE_PORT=8050
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
POSTGRES_HOST=aws-1-eu-north-1.pooler.supabase.com
POSTGRES_PORT=5432
POSTGRES_USER=postgres.tpdkhddtbhpoqzzgxfni
POSTGRES_PASSWORD=K@x3ta9V8GK5rnW
POSTGRES_DB=postgres

# Orchestrator
ORCHESTRATOR_URL=http://localhost:8002

# Monitoring
MONITORING_INTERVAL=60
SLOW_QUERY_THRESHOLD_MS=1000
MAX_STORED_METRICS=1000
```

### Runtime Configuration

Update configuration via API:
```bash
curl -X PUT "http://localhost:8050/config?monitoring_interval=120&slow_query_threshold_ms=2000"
```

---

## Monitoring

### Prometheus Integration

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'db-intelligence'
    static_configs:
      - targets: ['localhost:8050']
    metrics_path: '/metrics/prometheus'
    scrape_interval: 30s
```

### Grafana Dashboard

Key metrics to monitor:
- `db_health_status` - Overall health (1=healthy, 0.5=degraded, 0=unhealthy)
- `db_slow_queries_count` - Number of slow queries
- `db_active_connections` - Active database connections
- `db_cpu_percent` - CPU usage
- `db_memory_percent` - Memory usage
- `db_queries_tracked_total` - Total queries being monitored

---

## Troubleshooting

### pg_stat_statements Not Available

**Error:** `relation "pg_stat_statements" does not exist`

**Solution:**
```sql
-- Requires superuser
CREATE EXTENSION pg_stat_statements;

-- Or enable in postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
```

### High Memory Usage

If service uses too much memory:
```bash
# Reduce max stored metrics
curl -X PUT "http://localhost:8050/config?max_stored_metrics=500"
```

### Slow Query Threshold Too Sensitive

```bash
# Increase threshold to 2 seconds
curl -X PUT "http://localhost:8050/config?slow_query_threshold_ms=2000"
```

---

## Roadmap

### Phase 1: Core Monitoring ✅
- [x] Query performance tracking
- [x] Slow query detection
- [x] Health monitoring
- [x] Table statistics
- [x] REST API
- [x] Prometheus metrics

### Phase 2: AI-Powered Optimization 🚧
- [ ] ML-based query analysis
- [ ] Automatic index recommendations
- [ ] Query pattern detection
- [ ] Anomaly detection
- [ ] Predictive performance alerts

### Phase 3: Advanced Features 📋
- [ ] Automatic query rewriting
- [ ] Connection pool optimization
- [ ] Vacuum/analyze scheduling
- [ ] Migration impact analysis
- [ ] Cross-database correlation

---

## Integration Points

### Services Using This

All services should use the unified database entry point:

```python
from infrastructure.database import get_database, get_db_session

# Instead of creating direct connections
db = await get_database()
async with db.get_session() as session:
    # Your queries here
```

This allows DB Intelligence to monitor ALL database operations.

### Monitored Services

- ✅ intelligent-core (all modules)
- ✅ workflow_intelligence
- ✅ community_intelligence
- ✅ predictive services
- ✅ Gateway (rate limiting, audit)
- ✅ Auth Service

---

**Database Intelligence Service: Autonomous database optimization for the AI Platform** 🧠
