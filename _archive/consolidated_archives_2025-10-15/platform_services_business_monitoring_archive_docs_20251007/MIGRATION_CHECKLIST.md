# 🔍 Monitoring Service - Migration Checklist

**Service:** monitoring_service
**Lines:** 553
**Status:** STEP 1 - ANALYZE ✅

---

## 📊 SERVICE ANALYSIS

### Purpose:
Centralized monitoring and logging service that:
- Health checks for all BCM services
- Log aggregation and storage
- Metrics collection and storage
- Real-time alerts and notifications
- WebSocket streaming for live monitoring
- Built-in HTML dashboard

### Technology Stack:
- **Framework:** FastAPI
- **Storage:** In-memory (deque) + File-based logs
- **Real-time:** WebSocket
- **Health Checks:** httpx async HTTP client + socket connections
- **System Metrics:** psutil
- **Features:**
  - Automatic health monitoring (every 30s)
  - Real-time log/alert broadcasting via WebSocket
  - Simple HTML dashboard with auto-refresh
  - Alert system with severity levels

### Key Components:
1. **MonitoringStorage:** In-memory storage (10k logs, 24h metrics)
2. **HealthChecker:** Continuous health monitoring background task
3. **WebSocket:** Real-time streaming to dashboard
4. **File Logging:** Persistent logs to disk

---

## 🔧 REQUIRED CHANGES

### 1. **Port Configuration** ⚠️ CRITICAL
- **Current:** Port 8779 (hardcoded in line 554)
- **Change to:** Port 8045
- **Action:** Make port configurable via environment variable

### 2. **Monitored Services Configuration** ⚠️ CRITICAL
- **Current:** Hardcoded old service list (lines 49-56):
  - odoo:8069
  - unified_database_gateway:8888
  - unified_api_gateway:8777
  - crm_bridge:8778
  - postgres:5432
  - redis:6379
- **Problem:** These services don't exist in new architecture!
- **Change to:** New production services:
  - intelligent-gateway:8000
  - eventbus:8001
  - ai-orchestration:8002
  - bpmn-workflow:8003
  - coordination-center:8004
  - project-intelligence:8025
  - ai-intelligence:8032
  - notification-service:8035
  - process-mining:8040

### 3. **Log Directory**
- **Current:** `/tmp/bcm_logs` (line 44)
- **Change to:** Configurable path with better default
- **Recommendation:** `/var/log/bcm/` or env-based

### 4. **Environment Variables**
- **Add:**
  - `PORT=8045`
  - `LOG_DIR=/var/log/bcm/`
  - `METRICS_RETENTION_HOURS=24`
  - `CHECK_INTERVAL_SECONDS=30`
  - `ALERT_WEBHOOK_URL` (optional)

### 5. **Storage Backend** 🤔
- **Current:** In-memory only (deque)
- **Issue:** Data lost on restart
- **Recommendation:** Consider Redis or PostgreSQL for persistence
- **For now:** Keep in-memory, document limitation

### 6. **Alert Webhook Integration**
- **Current:** Stub (line 46)
- **Action:** Integrate with notification-service (Port 8035)
- **Benefit:** Send alerts via email/SMS/push

### 7. **Health Check Endpoints**
- **Current:** Assumes `/health` or `/web/health`
- **Action:** Standardize to `/health` for all services
- **Note:** Most services already have `/health`

### 8. **System Metrics**
- **Current:** Uses psutil for CPU/memory
- **Issue:** Monitors monitoring service itself, not target services
- **Action:** Remove or document this limitation
- **Alternative:** Services should report their own metrics

### 9. **WebSocket Security**
- **Current:** No authentication
- **Action:** Add optional JWT authentication
- **Note:** Dashboard is currently public

### 10. **Integration with Observability**
- **Current:** Standalone service
- **Opportunity:** Integrate with existing Prometheus/Grafana stack
- **Action:** Document integration path

---

## 📝 MIGRATION STEPS

### STEP 1: ANALYZE ✅ (CURRENT)
- [x] Read main.py (553 lines)
- [x] Read requirements.txt
- [x] Identify dependencies
- [x] Identify required changes
- [x] Create migration checklist

### STEP 2: ADAPT (NEXT)
- [ ] Create BCM_1_MIGRATED/monitoring_service/
- [ ] Copy main.py and requirements.txt
- [ ] Fix port configuration (8779 → 8045)
- [ ] Update MONITORED_SERVICES to new architecture
- [ ] Make LOG_DIR configurable
- [ ] Add notification-service integration for alerts
- [ ] Create .env.example with all required variables
- [ ] Update HTML dashboard title/branding
- [ ] Create README.md with:
  - API documentation
  - Setup instructions
  - Integration guide
  - Architecture diagram
- [ ] Test health checks
- [ ] Test WebSocket connection

### STEP 3: TRANSFER
- [ ] Copy to /Users/MD/AI-Platform-ISO/infrastructure/monitoring-service/
- [ ] Update Tool Registry with 8 actions:
  - ingest_log
  - ingest_metrics
  - get_status
  - get_services
  - get_logs
  - get_metrics
  - get_alerts
  - acknowledge_alert
  - resolve_alert
- [ ] Update SERVICES_INVENTORY.md (14th service)
- [ ] Create integration documentation

---

## 🎯 UNIQUE FEATURES

This is a **USEFUL but OVERLAPPING** service:

✅ **Real-time Monitoring:** WebSocket streaming
✅ **Built-in Dashboard:** HTML UI with auto-refresh
✅ **Log Aggregation:** Centralized logging
✅ **Alert System:** Automated alerts with severity levels
✅ **Health Checks:** Automatic 30s interval checks
✅ **In-memory Storage:** Fast access to recent data

⚠️ **Overlap with Observability:**
- We already have Prometheus + Grafana + Loki
- monitoring_service provides simpler, lightweight alternative
- Good for quick checks and development
- Prometheus better for production metrics

**Decision:** Transfer, but document as complementary to Observability stack

---

## ⚠️ CRITICAL CHANGES NEEDED

### Change 1: Update Monitored Services List
**Lines:** 49-56

**Current (WRONG):**
```python
MONITORED_SERVICES = {
    "odoo": {"url": "http://odoo:8069", "health": "/web/health", "type": "core"},
    "database_gateway": {"url": "http://unified_database_gateway:8888", "health": "/health", "type": "gateway"},
    # ... old services
}
```

**Fix (CORRECT):**
```python
MONITORED_SERVICES = {
    "intelligent_gateway": {"url": "http://localhost:8000", "health": "/health", "type": "gateway"},
    "eventbus": {"url": "http://localhost:8001", "health": "/health", "type": "platform"},
    "ai_orchestration": {"url": "http://localhost:8002", "health": "/health", "type": "platform"},
    "bpmn_workflow": {"url": "http://localhost:8003", "health": "/health", "type": "platform"},
    "coordination_center": {"url": "http://localhost:8004", "health": "/health", "type": "platform"},
    "project_intelligence": {"url": "http://localhost:8025", "health": "/health", "type": "intelligence"},
    "ai_intelligence": {"url": "http://localhost:8032", "health": "/health", "type": "intelligence"},
    "notification_service": {"url": "http://localhost:8035", "health": "/health", "type": "platform"},
    "process_mining": {"url": "http://localhost:8040", "health": "/api/v1/process-mining/health", "type": "analytics"},
}
```

### Change 2: Port Configuration
**Line:** 554

**Current:**
```python
uvicorn.run(app, host="0.0.0.0", port=8779, log_level="info")
```

**Fix:**
```python
port = int(os.getenv("PORT", 8045))
uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
```

### Change 3: Integrate with Notification Service
**New function to add:**
```python
async def send_alert_notification(alert: Alert):
    """Send alert via notification service"""
    if not Config.NOTIFICATION_SERVICE_URL:
        return

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{Config.NOTIFICATION_SERVICE_URL}/email/send",
                json={
                    "to": [Config.ALERT_EMAIL],
                    "subject": f"[{alert.severity.upper()}] {alert.title}",
                    "body": alert.description
                }
            )
    except Exception as e:
        logger.error(f"Failed to send alert notification: {e}")
```

---

## 📊 API ENDPOINTS (9 ACTIONS)

### Read Operations:
1. `GET /health` - Health check
2. `GET /status` - Overall system status
3. `GET /services` - All services status
4. `GET /logs` - Get logs with filtering
5. `GET /metrics/{service}` - Get metrics for service
6. `GET /alerts` - Get alerts
7. `GET /dashboard` - HTML dashboard

### Write Operations:
8. `POST /logs` - Ingest log entry
9. `POST /metrics` - Ingest metrics
10. `PUT /alerts/{alert_id}/acknowledge` - Acknowledge alert
11. `PUT /alerts/{alert_id}/resolve` - Resolve alert

### Real-time:
12. `WS /ws/realtime` - WebSocket for live updates

---

## 🔗 INTEGRATION WITH EXISTING SERVICES

### 1. Notification Service (Port 8035)
Send alerts via email/SMS when critical events occur.

### 2. Coordination Center (Port 8004)
Register as monitoring tool for health checks.

### 3. EventBus (Port 8001)
Publish monitoring events:
- `service.health_changed`
- `alert.created`
- `alert.resolved`

### 4. All Services
Services should push logs/metrics to monitoring service.

### 5. Observability Stack
Complement Prometheus/Grafana with simple dashboard.

---

## ⚖️ DECISION: TRANSFER OR SKIP?

**Recommendation:** ✅ TRANSFER

**Reasons:**
1. Provides simple, lightweight monitoring
2. Built-in dashboard useful for quick checks
3. Real-time WebSocket streaming
4. Complements Prometheus/Grafana (not replaces)
5. Good for development/debugging
6. Small codebase (553 lines)

**Use Cases:**
- Development: Quick service health checks
- Debugging: Real-time log streaming
- Demos: Simple HTML dashboard
- Alerts: Integration with notification service

**Note:** Document as complementary to Observability stack, not replacement.

---

**STATUS: READY FOR STEP 2 (ADAPT)** 🚀
