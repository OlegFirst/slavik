# BCM Platform Event Catalog
**Generated:** Automatically scanned from codebase  
**Total Events:** 133 (126 existing + 7 Phase 1 infrastructure)  
**Files Scanned:** 10220  
**Last Updated:** 2025-10-09 - Added Phase 1 Infrastructure Events

---

## 🆕 Infrastructure Events (Phase 1)

> **See:** [INFRASTRUCTURE_EVENTS.md](./INFRASTRUCTURE_EVENTS.md) for detailed documentation

### `infrastructure.health.healthy`
**Publishers (1):**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`

**Subscribers:**
- Auto-Recovery Service (monitoring)
- Monitoring Dashboard

---

### `infrastructure.health.unhealthy`
**Publishers (1):**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`

**Subscribers (1):**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery

---

### `infrastructure.health.degraded`
**Publishers (1):**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`

**Subscribers (2):**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery
- `infrastructure/eventbus/coordination/resource_optimizer.py` - Resource Optimizer

---

### `infrastructure.health.unknown`
**Publishers (1):**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`

**Subscribers:**
- Monitoring Dashboard

---

### `infrastructure.recovery.started`
**Publishers (1):**
- `infrastructure/eventbus/coordination/auto_recovery.py`

**Subscribers:**
- Health Monitor
- Monitoring Dashboard
- Notification Service

---

### `infrastructure.recovery.completed`
**Publishers (1):**
- `infrastructure/eventbus/coordination/auto_recovery.py`

**Subscribers:**
- Monitoring Dashboard
- Metrics Collector

---

### `infrastructure.recovery.failed`
**Publishers (1):**
- `infrastructure/eventbus/coordination/auto_recovery.py`

**Subscribers:**
- Notification Service (CRITICAL)
- Incident Management
- On-call Team

---

### `infrastructure.optimization.completed`
**Publishers (1):**
- `infrastructure/eventbus/coordination/resource_optimizer.py`

**Subscribers:**
- Capacity Planning Service
- Monitoring Dashboard

---

