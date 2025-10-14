# 🔍 Monitoring Service

**Port:** 8779
**Version:** 1.0.0
**Status:** ✅ Adapted for production

Centralized monitoring and logging service for BCM platform with real-time dashboard.

---

## 🎯 Features

### Core Capabilities:
1. **🏥 Health Checks** - Automatic monitoring every 30s
2. **📝 Log Aggregation** - Centralized logging from all services
3. **📊 Metrics Collection** - Performance metrics storage
4. **🚨 Alert System** - Automated alerts with severity levels
5. **📡 Real-time Streaming** - WebSocket for live updates
6. **🖥️ Built-in Dashboard** - HTML UI with auto-refresh

### Monitored Services:
- intelligent-gateway (8000)
- eventbus (8001)
- ai-orchestration (8002)
- bpmn-workflow (8003)
- coordination-center (8004)
- project-intelligence (8025)
- ai-intelligence (8032)
- notification-service (8035)
- process-mining (8040)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Service

```bash
python main.py
```

Service will start on **http://localhost:8779**

---

## 📊 Storage Architecture

### In-Memory Storage:
- **Logs:** Last 10,000 entries (deque)
- **Metrics:** 1,440 data points per service (24h, minute-by-minute)
- **Alerts:** All active/acknowledged/resolved alerts
- **WebSockets:** Connected clients for real-time streaming

### File-Based Logs:
- Location: `/var/log/bcm/` (configurable)
- Format: `{service}_{YYYYMMDD}.log`
- Rotation: Daily

⚠️ **Note:** Metrics are in-memory only. Data is lost on restart.

---

## 📡 API Endpoints

### Health & Status

#### Get Health
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "monitoring_service",
  "timestamp": "2025-10-02T12:00:00",
  "uptime_seconds": 3600
}
```

#### Get System Status
```bash
GET /status

Response:
{
  "overall_status": "healthy",
  "services_count": 9,
  "healthy_services": 8,
  "degraded_services": 1,
  "unhealthy_services": 0,
  "active_alerts": 2,
  "last_updated": "2025-10-02T12:00:00"
}
```

#### Get All Services Status
```bash
GET /services

Response:
{
  "intelligent_gateway": {
    "service": "intelligent_gateway",
    "status": "healthy",
    "response_time_ms": 45.2,
    "timestamp": "2025-10-02T12:00:00"
  },
  "eventbus": {
    "service": "eventbus",
    "status": "healthy",
    "response_time_ms": 32.1,
    "timestamp": "2025-10-02T12:00:00"
  }
}
```

### Logs

#### Ingest Log Entry
```bash
POST /logs
Content-Type: application/json

{
  "service": "coordination_center",
  "level": "ERROR",
  "message": "Failed to connect to database",
  "context": {"error_code": "DB_001"},
  "trace_id": "abc-123"
}

Response:
{
  "status": "logged"
}
```

#### Get Logs
```bash
GET /logs?service=coordination_center&level=ERROR&limit=50

Response:
[
  {
    "timestamp": "2025-10-02T12:00:00",
    "service": "coordination_center",
    "level": "ERROR",
    "message": "Failed to connect to database",
    "context": {"error_code": "DB_001"},
    "trace_id": "abc-123"
  }
]
```

### Metrics

#### Ingest Metrics
```bash
POST /metrics
Content-Type: application/json

{
  "service": "coordination_center",
  "status": "healthy",
  "response_time_ms": 125.5,
  "cpu_usage": 45.2,
  "memory_usage": 62.1,
  "active_connections": 10
}

Response:
{
  "status": "recorded"
}
```

#### Get Service Metrics
```bash
GET /metrics/coordination_center?hours=1

Response:
[
  {
    "service": "coordination_center",
    "timestamp": "2025-10-02T12:00:00",
    "status": "healthy",
    "response_time_ms": 125.5,
    "cpu_usage": 45.2,
    "memory_usage": 62.1
  }
]
```

### Alerts

#### Get Alerts
```bash
GET /alerts?status=active

Response:
[
  {
    "id": "eventbus_slow_response_1696248000",
    "service": "eventbus",
    "severity": "high",
    "title": "Slow response from eventbus",
    "description": "Response time: 5200.5ms",
    "timestamp": "2025-10-02T12:00:00",
    "status": "active",
    "resolved_at": null
  }
]
```

#### Acknowledge Alert
```bash
PUT /alerts/{alert_id}/acknowledge

Response:
{
  "status": "acknowledged"
}
```

#### Resolve Alert
```bash
PUT /alerts/{alert_id}/resolve

Response:
{
  "status": "resolved"
}
```

### Real-time WebSocket

#### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8779/ws/realtime');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'log') {
    console.log('New log:', data.data);
  } else if (data.type === 'alert') {
    console.log('New alert:', data.data);
  }
};
```

### Dashboard

#### View HTML Dashboard
```bash
GET /dashboard
```

Opens interactive dashboard with:
- Overall system status
- All services status cards
- Auto-refresh every 30 seconds
- Quick links to API endpoints

---

## 🔧 Configuration

### Required Environment Variables:

```bash
PORT=8779
LOG_DIR=/var/log/bcm
```

### Optional:

```bash
METRICS_RETENTION_HOURS=24           # Default: 24
CHECK_INTERVAL_SECONDS=30            # Default: 30
ALERT_EMAIL=alerts@bcm.example.com   # For email notifications
NOTIFICATION_SERVICE_URL=http://localhost:8035
EVENTBUS_URL=http://localhost:8001   # For event publishing
LOG_LEVEL=INFO
```

---

## 🚨 Alert System

### Alert Triggers:

1. **Service Unhealthy** (Critical)
   - When health check fails
   - Severity: critical
   - Notification: Email sent

2. **Slow Response** (High)
   - Response time > 5 seconds
   - Severity: high
   - Notification: Email sent

3. **High CPU** (Medium)
   - CPU usage > 90%
   - Severity: medium
   - Notification: None (logged only)

### Alert Lifecycle:
```
active → acknowledged → resolved
```

### Notification Integration:
Alerts with severity `high` or `critical` are automatically sent via notification-service (Port 8035) to configured email.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│      Services (9 monitored)             │
│  ├─ intelligent-gateway:8000            │
│  ├─ eventbus:8001                       │
│  ├─ ai-orchestration:8002               │
│  └─ ... (6 more)                        │
└────────────┬────────────────────────────┘
             ↓ Health checks every 30s
             ↓ Push logs/metrics
┌────────────────────────────────────────┐
│    Monitoring Service:8779              │
│  ┌─────────────────────────────────┐   │
│  │  In-Memory Storage              │   │
│  │  ├─ Logs (10k)                  │   │
│  │  ├─ Metrics (24h)               │   │
│  │  └─ Alerts                      │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Health Checker (Background)    │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  WebSocket Broadcaster          │   │
│  └─────────────────────────────────┘   │
└────┬───────────┬──────────────────┬────┘
     ↓           ↓                  ↓
┌─────────┐ ┌──────────┐  ┌──────────────┐
│ File    │ │WebSocket │  │Notification  │
│ Logs    │ │ Clients  │  │Service:8035  │
└─────────┘ └──────────┘  └──────────────┘
```

---

## 🔗 Integration

### With Services:
Services should push logs and metrics to monitoring service:

```python
import httpx

# Push log
await httpx.post("http://localhost:8779/logs", json={
    "service": "my_service",
    "level": "ERROR",
    "message": "Something went wrong"
})

# Push metrics
await httpx.post("http://localhost:8779/metrics", json={
    "service": "my_service",
    "status": "healthy",
    "response_time_ms": 125.5
})
```

### With Notification Service (8035):
Alerts are automatically sent via email for high/critical severity.

### With Coordination Center (8004):
Register as monitoring tool for health checks.

### With EventBus (8001):
TODO: Publish monitoring events:
- `service.health_changed`
- `alert.created`
- `alert.resolved`

---

## 🧪 Testing

### Test Health Check:
```bash
curl http://localhost:8779/health
```

### Test Log Ingestion:
```bash
curl -X POST http://localhost:8779/logs \
  -H "Content-Type: application/json" \
  -d '{
    "service": "test_service",
    "level": "INFO",
    "message": "Test log message"
  }'
```

### Test System Status:
```bash
curl http://localhost:8779/status
```

### View Dashboard:
```bash
open http://localhost:8779/dashboard
```

---

## 📊 Monitoring Best Practices

### For Services:
1. **Push logs regularly** - Use appropriate log levels
2. **Report metrics** - Send metrics every minute
3. **Standardize health endpoint** - Use `/health`
4. **Include context** - Add trace_id for correlation

### For Operations:
1. **Monitor dashboard** - Check every hour
2. **Review alerts** - Acknowledge and resolve promptly
3. **Analyze logs** - Look for patterns
4. **Track trends** - Use metrics for capacity planning

---

## 🆚 Monitoring vs Observability

### monitoring_service (Port 8779):
- ✅ Lightweight, simple dashboard
- ✅ Real-time WebSocket streaming
- ✅ Good for development/debugging
- ✅ Quick health checks
- ⚠️ In-memory storage (data loss on restart)
- ⚠️ Limited retention (24h)

### observability (Prometheus/Grafana/Loki):
- ✅ Production-grade metrics storage
- ✅ Advanced dashboards (6 Grafana dashboards)
- ✅ Long-term retention
- ✅ Powerful query language (PromQL)
- ⚠️ More complex setup
- ⚠️ Higher resource usage

**Recommendation:** Use both!
- **monitoring_service** - Quick checks, real-time streaming, development
- **observability** - Production metrics, long-term storage, alerting

---

## 🐳 Docker

```bash
docker build -t monitoring-service .
docker run -p 8779:8779 --env-file .env monitoring-service
```

---

## 📝 TODO

### High Priority:
- [ ] Add Redis/PostgreSQL for persistent storage
- [ ] Integrate with EventBus for event publishing
- [ ] Add JWT authentication for WebSocket
- [ ] Create Prometheus exporter endpoint

### Medium Priority:
- [ ] Add log parsing and analysis
- [ ] Implement log retention policies
- [ ] Add custom alert rules configuration
- [ ] Create API for dynamic service registration

### Low Priority:
- [ ] Add machine learning for anomaly detection
- [ ] Implement distributed tracing support
- [ ] Add performance profiling
- [ ] Create mobile dashboard

---

## 🎓 Use Cases

### 1. Development Environment
Quick service health checks during development.

### 2. Debugging
Real-time log streaming to identify issues.

### 3. Demos
Simple dashboard for presentations.

### 4. Incident Response
Fast overview of system health during incidents.

### 5. Capacity Planning
Historical metrics for resource planning.

---

**Ready for production!** ✅

**Note:** Complementary to Observability stack (Prometheus/Grafana), not a replacement.
