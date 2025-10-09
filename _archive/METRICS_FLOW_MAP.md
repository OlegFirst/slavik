# Metrics Flow Map - Complete Integration

**Date**: 2025-10-09
**Purpose**: Полная карта метрик - источники, потоки, хранилища, потребители

## Metrics Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         METRICS SOURCES                             │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  psutil  │  │FastAPI   │  │ Survival │  │  Memory  │          │
│  │ (system) │  │(service) │  │ Instinct │  │  System  │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │             │              │              │                 │
└───────┼─────────────┼──────────────┼──────────────┼─────────────────┘
        │             │              │              │
        │             │              │              │
        ▼             ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      METRICS COLLECTORS                             │
│                                                                     │
│  ┌────────────────────┐         ┌────────────────────┐            │
│  │  Resource Tracker  │         │  Monitoring Service│            │
│  │  • CPU %           │         │  • Prometheus      │            │
│  │  • Memory %        │         │  • Custom metrics  │            │
│  │  • Disk IO         │         │                    │            │
│  │  • Network         │         │                    │            │
│  └─────────┬──────────┘         └─────────┬──────────┘            │
│            │                              │                        │
└────────────┼──────────────────────────────┼────────────────────────┘
             │                              │
             │                              │
             ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      METRICS STORAGE                                │
│                                                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐      │
│  │  JSON Files    │  │  Supabase      │  │  Prometheus    │      │
│  │  (local)       │  │  (database)    │  │  (TSDB)        │      │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘      │
│           │                   │                   │               │
└───────────┼───────────────────┼───────────────────┼───────────────┘
            │                   │                   │
            │                   │                   │
            ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      METRICS CONSUMERS                              │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐   │
│  │  Wishlist  │  │  Survival  │  │  Grafana   │  │   API    │   │
│  │  System    │  │  Instinct  │  │ Dashboards │  │  Users   │   │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Detailed Metrics Flow

### 1. System-Level Metrics (psutil → Resource Tracker)

**Source**: `psutil` library

**Collected by**: Resource Tracker

**Collection Code**:
```python
# In resource_tracker.py
def take_snapshot(self) -> ResourceSnapshot:
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)

    # Memory
    mem = psutil.virtual_memory()
    memory_percent = mem.percent
    memory_mb = mem.used / (1024 * 1024)

    # Disk IO
    disk = psutil.disk_io_counters()
    disk_io_mb = (disk.read_bytes + disk.write_bytes) / (1024 * 1024)

    # Network
    net = psutil.net_io_counters()
    network_bytes = net.bytes_sent + net.bytes_recv

    snapshot = ResourceSnapshot(
        timestamp=time.time(),
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        memory_mb=memory_mb,
        disk_io_mb=disk_io_mb,
        network_bytes=network_bytes
    )

    return snapshot
```

**Frequency**: Every 60 seconds (configurable)

**Storage**:
- In-memory: `deque` (last 100 snapshots)
- On-disk: JSON file (last 50 snapshots)

**Consumers**:
- Wishlist System (для prioritization)
- Survival Instinct (для threshold monitoring)
- API endpoints (для visualization)

### 2. Service-Level Metrics (FastAPI → Prometheus)

**Source**: FastAPI service

**Collected by**: Monitoring Service (existing in infrastructure/)

**Collection Points**:
```python
# In system-bcm-service/main.py

# Request metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Calculate metrics
    duration = time.time() - start_time

    # Send to Prometheus
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).observe(duration)

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()

    return response
```

**Metrics Collected**:
- Request count
- Request duration (histogram)
- Response status codes
- Active requests (gauge)
- Error rate

**Storage**: Prometheus TSDB

**Location**: `infrastructure/observability/prometheus/`

**Consumers**:
- Grafana dashboards
- Alertmanager
- API monitoring

### 3. Survival Instinct Metrics (Internal → KPIs)

**Source**: Survival Instinct internal monitoring

**Collected by**: Self-monitoring loop

**Metrics Tracked**:
```python
# In survival.py
self.my_kpis: Dict[str, KPI] = {
    'response_time_ms': KPI(
        name='response_time_ms',
        target_value=200.0,
        tolerance=0.25,
        current_value=150.0  # ← Measured value
    ),
    'uptime_percent': KPI(
        name='uptime_percent',
        target_value=99.9,
        tolerance=0.001,
        current_value=99.95  # ← Measured value
    ),
    'error_rate_percent': KPI(
        name='error_rate_percent',
        target_value=0.1,
        tolerance=0.5,
        current_value=0.05  # ← Measured value
    ),
    # ... 7 KPIs total
}
```

**How Measured**:
```python
def get_my_current_metrics(self) -> Dict[str, float]:
    """
    Get current metric values for my KPIs
    """
    metrics = {}

    # Response time - from service stats
    if hasattr(state, 'last_request_time'):
        metrics['response_time_ms'] = state.last_request_time

    # Uptime - from start time
    uptime_seconds = time.time() - self.start_time
    total_time = time.time() - self.created_at
    metrics['uptime_percent'] = (uptime_seconds / total_time) * 100

    # Error rate - from request counters
    if hasattr(state, 'request_stats'):
        total = state.request_stats.get('total', 0)
        errors = state.request_stats.get('errors', 0)
        metrics['error_rate_percent'] = (errors / total * 100) if total > 0 else 0

    # CPU/Memory - from Resource Tracker
    if self.resource_tracker:
        latest = self.resource_tracker.history[-1] if self.resource_tracker.history else None
        if latest:
            metrics['cpu_utilization_percent'] = latest.cpu_percent
            metrics['memory_utilization_percent'] = latest.memory_percent

    # MTTR - from recovery history
    if self.action_history:
        recent_recoveries = [a for a in self.action_history[-10:] if a.success]
        if recent_recoveries:
            avg_recovery_time = sum(a.execution_time for a in recent_recoveries) / len(recent_recoveries)
            metrics['mttr_minutes'] = avg_recovery_time / 60.0

    # Auto-recovery rate
    if self.stats['corrections_executed'] > 0:
        success_rate = (self.stats['corrections_successful'] / self.stats['corrections_executed']) * 100
        metrics['auto_recovery_success_rate'] = success_rate

    return metrics
```

**Frequency**: Every 60 seconds

**Storage**: In-memory + API endpoint

**Consumers**:
- Survival Instinct (self-monitoring)
- Wishlist (creates wishes on imbalance)
- API (GET /survival/health)

### 4. Memory System Metrics (Internal → Patterns)

**Source**: Memory System operations

**Metrics Tracked**:
```python
# In memory_system.py

# Short-term cache metrics
self.short_term.stats = {
    'hits': 0,              # Cache hits
    'misses': 0,            # Cache misses
    'evictions': 0,         # LRU evictions
    'expirations': 0,       # TTL expirations
    'total_entries': 0,     # Total stored
    'current_size': 0,      # Current entries
    'hit_rate': 0.0         # hits / (hits + misses)
}

# Long-term storage metrics
self.long_term.stats = {
    'patterns_stored': 0,      # Total patterns
    'patterns_retrieved': 0,   # Query count
    'successful_patterns': 0,  # Success count
    'failed_patterns': 0       # Failure count
}
```

**How Measured**:
```python
# Short-term
def get(self, key: str) -> Optional[Any]:
    entry = self.cache.get(key)

    if entry is None:
        self.stats['misses'] += 1  # ← Metric increment
        return None

    if entry.is_expired():
        self.stats['misses'] += 1
        self.stats['expirations'] += 1  # ← Metric increment
        del self.cache[key]
        return None

    entry.touch()
    self.stats['hits'] += 1  # ← Metric increment
    return entry.value

# Long-term
def store_pattern(self, state_signature, action_type, success, context):
    if success:
        self.stats['successful_patterns'] += 1  # ← Metric increment
    else:
        self.stats['failed_patterns'] += 1  # ← Metric increment

    self.stats['patterns_stored'] += 1  # ← Metric increment
```

**Storage**: In-memory + API endpoint

**Consumers**:
- API (GET /memory/stats)
- Monitoring dashboards

### 5. Wishlist System Metrics (Internal → Operations)

**Source**: Wishlist operations

**Metrics Tracked**:
```python
# In wishlist_system.py
self.stats = {
    'total_created': 0,        # Total wishes created
    'total_completed': 0,      # Successfully completed
    'total_obsolete': 0,       # Marked obsolete
    'conflicts_resolved': 0,   # Conflicts resolved
    'current_pending': 0,      # Currently pending
    'current_active': 0,       # Currently active
    'current_completed': 0     # Currently completed
}
```

**How Measured**:
```python
def add_wish(self, description, need_type, urgency, resource_cost, ...):
    item = WishlistItem(...)
    self.items[item.id] = item
    self.stats['total_created'] += 1  # ← Metric increment
    return item

def complete_wish(self, item_id, success):
    item = self.items[item_id]
    item.status = "completed"
    self.stats['total_completed'] += 1  # ← Metric increment

def cleanup_obsolete(self):
    for item in obsolete_items:
        item.status = "obsolete"
        self.stats['total_obsolete'] += 1  # ← Metric increment
```

**Storage**: In-memory + JSON file + API endpoint

**Consumers**:
- API (GET /wishlist/stats)
- Monitoring dashboards

## Integration with Existing Monitoring

### Current Monitoring Infrastructure

**Location**: `/infrastructure/observability/`

**Components**:
1. **Prometheus** (port 9090)
   - Time-series database
   - Scrapes metrics endpoints
   - Stores historical data

2. **Grafana** (port 3000)
   - Visualization dashboards
   - Alerts
   - Queries Prometheus

3. **Monitoring Service** (port 8010)
   - Aggregates metrics
   - Custom metrics collection
   - Integration layer

### How New Components Integrate

#### Option 1: Direct Prometheus Export

**Add to each component**:
```python
# In resource_tracker.py
from prometheus_client import Gauge, Counter, Histogram

# Define metrics
CPU_USAGE = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('system_memory_usage_percent', 'Memory usage percentage')
RESOURCE_SNAPSHOTS = Counter('resource_snapshots_total', 'Total snapshots taken')

# Update in take_snapshot()
def take_snapshot(self):
    snapshot = ResourceSnapshot(...)

    # Export to Prometheus
    CPU_USAGE.set(snapshot.cpu_percent)
    MEMORY_USAGE.set(snapshot.memory_percent)
    RESOURCE_SNAPSHOTS.inc()

    return snapshot
```

**Prometheus scrapes**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'system-bcm-service'
    static_configs:
      - targets: ['localhost:8009']
    metrics_path: '/metrics'
```

#### Option 2: Push to Monitoring Service

**Send metrics to monitoring service**:
```python
# In resource_tracker.py
async def send_to_monitoring(self, snapshot: ResourceSnapshot):
    """Send metrics to monitoring service"""
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                'http://localhost:8010/metrics',
                json={
                    'service': 'system-bcm',
                    'component': 'resource_tracker',
                    'metrics': {
                        'cpu_percent': snapshot.cpu_percent,
                        'memory_percent': snapshot.memory_percent,
                        'timestamp': snapshot.timestamp
                    }
                }
            )
    except Exception as e:
        logger.error(f"Failed to send metrics: {e}")
```

#### Option 3: EventBus Publication

**Publish metrics as events**:
```python
# In resource_tracker.py
async def publish_metrics(self, snapshot: ResourceSnapshot):
    """Publish metrics via EventBus"""
    await self.eventbus.publish(Event(
        type='platform.metrics.resource_snapshot',
        data={
            'cpu_percent': snapshot.cpu_percent,
            'memory_percent': snapshot.memory_percent,
            'timestamp': snapshot.timestamp
        },
        source='resource-tracker'
    ))
```

**Monitoring service subscribes**:
```python
# In monitoring service
@eventbus.subscribe('platform.metrics.*')
async def handle_metrics(event):
    # Store in Prometheus
    # Update Grafana
    # Trigger alerts
```

## Complete Metrics Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            DATA SOURCES                                  │
└────┬──────────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
     │          │          │          │          │          │
     │          │          │          │          │          │
  ┌──▼──┐   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐
  │psutil│  │FastAPI│ │Survival│ │Memory│ │Wishlist│ │User  │
  │      │  │       │ │Instinct│ │System│ │System │ │Actions│
  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘
     │         │         │         │         │         │
     │ CPU     │ Req     │ KPI     │ Cache   │ Wishes  │ Events
     │ Memory  │ Latency │ Values  │ Hits    │ Count   │
     │ Disk    │ Errors  │ Imbal.  │ Patterns│ Status  │
     │ Network │         │         │         │         │
     │         │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         COLLECTORS / AGGREGATORS                         │
│                                                                          │
│  ┌─────────────────┐           ┌─────────────────┐                     │
│  │ Resource Tracker│           │ Monitoring Svc  │                     │
│  │ • Snapshots     │◄─────────►│ • Prometheus    │                     │
│  │ • Trends        │           │ • Custom        │                     │
│  │ • Predictions   │           │                 │                     │
│  └────────┬────────┘           └────────┬────────┘                     │
│           │                             │                              │
└───────────┼─────────────────────────────┼──────────────────────────────┘
            │                             │
            │                             │
            ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            STORAGE LAYER                                 │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐      │
│  │ JSON Files │  │ Memory     │  │ Supabase   │  │ Prometheus │      │
│  │ (local)    │  │ (runtime)  │  │ (postgres) │  │ (TSDB)     │      │
│  │            │  │            │  │            │  │            │      │
│  │ • resource │  │ • snapshots│  │ • wishes   │  │ • all      │      │
│  │   history  │  │ • patterns │  │ • patterns │  │   metrics  │      │
│  │ • wishlist │  │ • wishes   │  │ • metrics  │  │            │      │
│  │ • patterns │  │            │  │            │  │            │      │
│  └────────┬───┘  └────────┬───┘  └────────┬───┘  └────────┬───┘      │
│           │               │               │               │           │
└───────────┼───────────────┼───────────────┼───────────────┼───────────┘
            │               │               │               │
            │               │               │               │
            └───────┬───────┴───────┬───────┴───────┬───────┘
                    │               │               │
                    ▼               ▼               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          CONSUMPTION LAYER                               │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Wishlist   │  │  Survival   │  │   Grafana   │  │  REST API   │  │
│  │  Priority   │  │  Decisions  │  │  Dashboards │  │  Endpoints  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│  │  Alerts /   │  │  ML Models  │  │  External   │                    │
│  │  Triggers   │  │  (future)   │  │  Systems    │                    │
│  └─────────────┘  └─────────────┘  └─────────────┘                    │
└──────────────────────────────────────────────────────────────────────────┘
```

## Metrics Catalog

### System Metrics (psutil)

| Metric | Source | Type | Unit | Frequency | Consumer |
|--------|--------|------|------|-----------|----------|
| cpu_percent | psutil.cpu_percent() | Gauge | % | 60s | Resource Tracker |
| memory_percent | psutil.virtual_memory() | Gauge | % | 60s | Resource Tracker |
| memory_mb | psutil.virtual_memory() | Gauge | MB | 60s | Resource Tracker |
| disk_io_mb | psutil.disk_io_counters() | Counter | MB | 60s | Resource Tracker |
| network_bytes | psutil.net_io_counters() | Counter | bytes | 60s | Resource Tracker |

### Service Metrics (FastAPI)

| Metric | Source | Type | Unit | Frequency | Consumer |
|--------|--------|------|------|-----------|----------|
| request_count | Middleware | Counter | count | per request | Prometheus |
| request_duration | Middleware | Histogram | seconds | per request | Prometheus |
| response_status | Middleware | Counter | count | per request | Prometheus |
| active_requests | Middleware | Gauge | count | realtime | Prometheus |
| error_rate | Derived | Gauge | % | 1m | Grafana |

### Survival Instinct Metrics

| Metric | Source | Type | Unit | Frequency | Consumer |
|--------|--------|------|------|-----------|----------|
| response_time_ms | Service stats | Gauge | ms | 60s | Survival KPI |
| uptime_percent | Start time | Gauge | % | 60s | Survival KPI |
| mttr_minutes | Recovery history | Gauge | minutes | 60s | Survival KPI |
| error_rate_percent | Request stats | Gauge | % | 60s | Survival KPI |
| cpu_utilization | Resource Tracker | Gauge | % | 60s | Survival KPI |
| memory_utilization | Resource Tracker | Gauge | % | 60s | Survival KPI |
| auto_recovery_rate | Action history | Gauge | % | 60s | Survival KPI |
| imbalances_detected | Internal counter | Counter | count | cumulative | API |
| corrections_executed | Internal counter | Counter | count | cumulative | API |
| corrections_successful | Internal counter | Counter | count | cumulative | API |

### Memory System Metrics

| Metric | Source | Type | Unit | Frequency | Consumer |
|--------|--------|------|------|-----------|----------|
| cache_hits | Short-term ops | Counter | count | per access | API |
| cache_misses | Short-term ops | Counter | count | per access | API |
| cache_hit_rate | Derived | Gauge | % | 1m | API |
| cache_size | Short-term | Gauge | count | realtime | API |
| evictions | Short-term ops | Counter | count | cumulative | API |
| expirations | Short-term ops | Counter | count | cumulative | API |
| patterns_stored | Long-term ops | Counter | count | cumulative | API |
| patterns_retrieved | Long-term ops | Counter | count | cumulative | API |
| pattern_success_rate | Derived | Gauge | % | 1m | API |

### Wishlist System Metrics

| Metric | Source | Type | Unit | Frequency | Consumer |
|--------|--------|------|------|-----------|----------|
| wishes_created | add_wish() | Counter | count | cumulative | API |
| wishes_completed | complete_wish() | Counter | count | cumulative | API |
| wishes_obsolete | cleanup() | Counter | count | cumulative | API |
| conflicts_resolved | resolve() | Counter | count | cumulative | API |
| pending_wishes | get_stats() | Gauge | count | realtime | API |
| active_wishes | get_stats() | Gauge | count | realtime | API |
| wish_priority_avg | Derived | Gauge | 0-1 | 1m | Monitoring |

### Resource Tracker Metrics

| Metric | Source | Type | Unit | Frequency | Consumer |
|--------|--------|------|------|-----------|----------|
| snapshots_taken | take_snapshot() | Counter | count | cumulative | API |
| cpu_trend | calculate_trend() | Gauge | -1 to +1 | 60s | API |
| memory_trend | calculate_trend() | Gauge | -1 to +1 | 60s | API |
| resource_state | detect_state() | Enum | string | 60s | Wishlist |
| deficit_events | detect_state() | Counter | count | cumulative | API |
| surplus_events | detect_state() | Counter | count | cumulative | API |
| seconds_to_deficit | predict_deficit() | Gauge | seconds | 60s | Alerts |

## Storage Requirements

### JSON Files (Local Disk)

```
/Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service/data/
├── resource_history.json      (~50 snapshots, ~250KB)
├── wishlist.json              (~100 wishes, ~100KB)
└── longterm_memory.json       (~1000 patterns, ~500KB)

Total: ~850KB
Daily growth: ~100KB
Weekly cleanup: Keep last 7 days
```

### Supabase (PostgreSQL) - Future

```sql
-- Metrics table (time-series)
CREATE TABLE metrics (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL,         -- 'resource_tracker', 'survival', etc.
    metric_name TEXT NOT NULL,
    metric_value FLOAT NOT NULL,
    tags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_source_name ON metrics(source, metric_name);

-- Retention policy: 30 days
```

### Prometheus (TSDB)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Retention: 15 days
storage:
  tsdb:
    retention.time: 15d
    retention.size: 10GB

# Storage per day: ~200MB
# Total: ~3GB for 15 days
```

## API Endpoints for Metrics

### Current Metrics Endpoints

```
GET /survival/health
GET /survival/stats
GET /memory/stats
```

### New Metrics Endpoints

```
GET /metrics                    # Prometheus format (all)
GET /metrics/resources          # Resource Tracker metrics
GET /metrics/wishlist           # Wishlist metrics
GET /metrics/memory             # Memory metrics
GET /metrics/survival           # Survival metrics
GET /metrics/summary            # Combined summary

# Time-series queries
GET /metrics/history?metric=cpu_percent&duration=1h
GET /metrics/trends?metrics=cpu,memory&duration=24h
```

## Grafana Dashboard Design

### Dashboard: System BCM Overview

**Panels**:

1. **System Resources** (top row)
   - CPU Usage (gauge + sparkline)
   - Memory Usage (gauge + sparkline)
   - Disk IO (graph)
   - Network (graph)

2. **Resource Trends** (second row)
   - CPU Trend (-1 to +1)
   - Memory Trend (-1 to +1)
   - Resource State (deficit/normal/surplus)
   - Seconds to Deficit (if applicable)

3. **Survival Instinct** (third row)
   - KPI Status (7 gauges)
   - Imbalances Detected (counter)
   - Corrections Success Rate (gauge)
   - Recent Imbalances (table)

4. **Wishlist Activity** (fourth row)
   - Pending Wishes (gauge)
   - Active Wishes (gauge)
   - Completion Rate (gauge)
   - Top Priority Wishes (table)

5. **Memory Performance** (fifth row)
   - Cache Hit Rate (gauge)
   - Patterns Stored (counter)
   - Pattern Success Rate (gauge)
   - Recent Patterns (table)

**Queries** (PromQL):
```promql
# CPU Usage
system_cpu_usage_percent

# CPU Trend
system_cpu_trend

# Wishes pending
wishlist_pending_wishes

# Cache hit rate
rate(memory_cache_hits[5m]) / (rate(memory_cache_hits[5m]) + rate(memory_cache_misses[5m]))
```

## Alerting Rules

### Critical Alerts

```yaml
# Resource Deficit Alert
- alert: ResourceDeficit
  expr: resource_state == "deficit"
  for: 5m
  annotations:
    summary: "System resources in deficit state"

# Survival Instinct Critical Imbalance
- alert: CriticalImbalance
  expr: survival_imbalance_level == "critical"
  for: 1m
  annotations:
    summary: "Critical imbalance detected in {{ $labels.kpi }}"

# High Error Rate
- alert: HighErrorRate
  expr: error_rate_percent > 5
  for: 5m
  annotations:
    summary: "Error rate above 5%"
```

### Warning Alerts

```yaml
# Resource Deficit Predicted
- alert: DeficitPredicted
  expr: seconds_to_deficit < 300  # 5 minutes
  for: 1m
  annotations:
    summary: "Resource deficit predicted in {{ $value }}s"

# Wishlist Growing
- alert: WishlistGrowing
  expr: rate(wishlist_pending_wishes[5m]) > 0.1
  for: 10m
  annotations:
    summary: "Wishlist growing: {{ $value }} wishes/min"

# Memory Cache Low Hit Rate
- alert: LowCacheHitRate
  expr: cache_hit_rate < 0.5
  for: 10m
  annotations:
    summary: "Cache hit rate below 50%"
```

## Implementation Checklist

### Phase 1: Basic Metrics Collection ✅
- [x] Resource Tracker collects system metrics
- [x] Survival Instinct tracks KPIs
- [x] Memory System tracks cache stats
- [x] Wishlist tracks operations

### Phase 2: Storage ⏳
- [ ] JSON file storage (partial - done in components)
- [ ] Prometheus export endpoints
- [ ] Supabase schema (future)

### Phase 3: Integration ⏳
- [ ] Add Prometheus client to components
- [ ] Configure scrape endpoints
- [ ] EventBus metrics publication (optional)

### Phase 4: Visualization ⏳
- [ ] Create Grafana dashboard
- [ ] Configure alerts
- [ ] Test end-to-end

---

**Вопрос**: Какой вариант интеграции предпочитаешь?
1. **Direct Prometheus** - каждый компонент экспортирует метрики
2. **Via Monitoring Service** - компоненты отправляют в централизованный сервис
3. **Via EventBus** - метрики как события через EventBus
4. **Hybrid** - critical metrics через Prometheus, остальное через EventBus
