# Phase 1 Infrastructure - Quick Start Guide 🚀

**Status:** ✅ All code complete - Ready to deploy!
**Time to Deploy:** ~10 minutes

---

## What's Been Built

Your complete **Infrastructure Coordination System (Phase 1)** is ready:

✅ **Health Monitoring** - Checks services every 30 seconds, publishes events on changes
✅ **Auto-Recovery** - Automatically restarts failed services with exponential backoff
✅ **Resource Optimizer** - Analyzes CPU/Memory/Disk every 5 minutes, recommends scaling
✅ **Metrics API** - Exposes all metrics on port 9091 for Prometheus
✅ **Prometheus & Grafana** - Already configured, just needs to start
✅ **EventBus Catalog** - Updated with 7 new infrastructure events

---

## Quick Deploy (3 Commands)

### 1. Start Monitoring Stack
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability
docker-compose -f docker-compose.monitoring.yml up -d
```
**Starts:** Prometheus, Grafana, AlertManager, Node Exporter, cAdvisor

### 2. Start Metrics API
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/api
python3 metrics_api.py &
```
**Runs on:** http://localhost:9091

### 3. Start Infrastructure Coordinator
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus/coordination
python3 infrastructure_coordinator.py
```
**Coordinates:** Health Monitor + Auto-Recovery + Resource Optimizer

---

## Verify It's Working

### Check Prometheus
```bash
open http://localhost:9090
# Search for: infrastructure_health_status
```

### Check Grafana
```bash
open http://localhost:3000
# Login: admin / admin123
# Navigate to: Dashboards → Infrastructure Health
```

### Check Metrics API
```bash
curl http://localhost:9091/health
# Expected: {"status":"healthy","service":"metrics_api","port":9091}
```

### Watch Health Events
```bash
cd /Users/MD/AI-Platform-ISO
python3 << 'EOF'
import asyncio
from infrastructure.eventbus import create_eventbus

async def watch():
    bus = create_eventbus('redis')
    async def handler(event):
        print(f"📤 {event.type} - {event.data.get('service_name')}: {event.data.get('status')}")
    await bus.subscribe('infrastructure.health.*', handler)
    await asyncio.sleep(300)

asyncio.run(watch())
EOF
```

---

## What You'll See

When running, Infrastructure Coordinator shows:

```
======================================================================
Starting Infrastructure Coordinator (Phase 1)
======================================================================
Step 1: Connecting Health Monitor to EventBus...
✅ Health Monitor connected to EventBus

Step 2: Registering critical services...
  ✅ eventbus (interval: 30s)
  ✅ api_gateway (interval: 30s)
  ✅ database (interval: 60s)
  ✅ redis (interval: 30s)
  ✅ rag_pipeline (interval: 60s)
✅ Registered 5 health checks

Step 3: Registering recovery strategies...
  ✅ eventbus: restart (max 3 attempts)
  ✅ api_gateway: restart (max 3 attempts)
  ✅ database: circuit_breaker (max 1 attempts)
  ✅ redis: restart (max 3 attempts)
  ✅ rag_pipeline: restart (max 2 attempts)
✅ Registered 5 recovery strategies

Step 4: Starting coordination services...
======================================================================
✅ Infrastructure Coordinator STARTED
======================================================================
Services running:
  🏥 Health Monitor: Running (30 sec intervals)
  🔧 Auto-Recovery: Listening for health events
  📊 Resource Optimizer: Running (5 min intervals)
======================================================================
```

Every 30 seconds, health checks run.
Every 5 minutes, resource optimization completes.
When a service fails, auto-recovery kicks in automatically.

---

## Architecture

```
Health Monitor (30s) → EventBus → Auto-Recovery
                          ↓
                     Resource Optimizer (5min)
                          ↓
                     Metrics API (9091) → Prometheus → Grafana
```

---

## Event Flow Example

```
1. Service Fails
   Health Monitor detects → Publishes infrastructure.health.unhealthy

2. Auto-Recovery Activates
   Receives event → Starts recovery → Publishes infrastructure.recovery.started

3. Recovery Executes
   Restarts service → Waits → Checks health

4. Service Recovers
   Health Monitor detects → Publishes infrastructure.health.healthy
   Auto-Recovery → Publishes infrastructure.recovery.completed

Total Time: ~10-30 seconds
```

---

## Full Documentation

📖 **Complete Guide:** [PHASE1_DEPLOYMENT_GUIDE.md](infrastructure/observability/PHASE1_DEPLOYMENT_GUIDE.md)
📊 **Complete Summary:** [PHASE_1_COMPLETE_SUMMARY.md](doc-project/PHASE_1_COMPLETE_SUMMARY.md)
📝 **Infrastructure Events:** [INFRASTRUCTURE_EVENTS.md](infrastructure/eventbus/events/INFRASTRUCTURE_EVENTS.md)
🗺️ **Phase 1 Plan:** [PHASE_1_INTEGRATION_PLAN.md](doc-project/PHASE_1_INTEGRATION_PLAN.md)

---

## Files Created

**Core Services:**
- `/infrastructure/eventbus/coordination/auto_recovery.py`
- `/infrastructure/eventbus/coordination/resource_optimizer.py`
- `/infrastructure/eventbus/coordination/infrastructure_coordinator.py`
- `/intelligent-core/orchestration/api/metrics_api.py`

**Modified:**
- `/intelligent-core/orchestration/ai-orchestration/core/health_monitor.py`
- `/infrastructure/observability/config/prometheus/prometheus.yml`

**Documentation:**
- `/infrastructure/observability/PHASE1_DEPLOYMENT_GUIDE.md`
- `/infrastructure/eventbus/events/INFRASTRUCTURE_EVENTS.md`
- `/doc-project/PHASE_1_COMPLETE_SUMMARY.md`

---

## Support

**Issues?** Check troubleshooting in [PHASE1_DEPLOYMENT_GUIDE.md](infrastructure/observability/PHASE1_DEPLOYMENT_GUIDE.md)

**Questions?** All documentation is in `/doc-project/` and `/infrastructure/observability/`

---

**Status:** ✅ READY TO GO - All code complete, documented, and tested!
**Next:** Deploy with 3 commands above, then verify with checks
**After:** Start Phase 2 - Core Level Coordination

🎉 **Let's deploy, partner!**
