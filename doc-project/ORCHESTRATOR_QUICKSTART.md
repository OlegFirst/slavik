# AI Orchestrator - Quick Start Guide 🚀

## Prerequisites

- Python 3.9+
- Node.js 18+
- Redis (для EventBus)
- PostgreSQL (опционально, для Production)

## 1. Start Orchestrator API

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/ai-orchestration

# Install dependencies (if needed)
pip install -r requirements.txt

# Start API server
python api.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8050
INFO:     Application startup complete
```

**Test:**
```bash
curl http://localhost:8050/health
```

## 2. Start Admin Panel

```bash
cd /Users/MD/AI-Platform-ISO/interface/admin_panel

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev
```

**Expected output:**
```
  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.x:3000/
```

## 3. Access Control Panel

Open browser:
```
http://localhost:3000/orchestrator
```

## What You'll See

### Header
- **Status Badge:** Operational / Degraded / Unhealthy
- **Last Updated:** Timestamp

### Performance Metrics (4 Cards)
- Decision Latency: XXms (Target: < 50ms)
- Auto-Resolution Rate: XX% (Target: > 70%)
- Escalation Rate: XX% (Target: < 20%)
- Safety Approval: XX% (Target: > 95%)

### System Components
- ✅ Event Bus
- ✅ Service Registry
- ✅ Decision Center
- ✅ Crisis Coordinator
- ✅ PDCA Engine

### Active Crises
- Count by level (MINOR/MAJOR/CRITICAL/CATASTROPHIC)
- Crisis IDs

### AI Experts Delegation
- BCM Advisor: XX delegations
- Compliance Auditor: XX delegations
- Strategic Planner: XX delegations

### Recent Decisions
- Total decisions
- Breakdown by action type

### Service Health Grid
- 9/9 services healthy
- BIA, Risk, Compliance, Planning, etc.

### Quick Actions
- 🔄 **Trigger Evolution** - Start evolution cycle
- 🗑️ **Clear Cache** - Clear strategy cache

## Troubleshooting

### Orchestrator API не запускается
```bash
# Check port 8050
lsof -i :8050

# Kill if occupied
kill -9 <PID>
```

### Admin Panel не подключается
```bash
# Check orchestrator API is running
curl http://localhost:8050/health

# Check browser console for errors
```

### Services показывают Unhealthy
```bash
# Start required services
cd /Users/MD/AI-Platform-ISO/platform-services

# Start BIA service
cd bia-service && python main.py &

# Start Risk service
cd risk-service && python main.py &

# etc...
```

## Testing Orchestrator

### Make a test decision
```bash
curl -X POST http://localhost:8050/api/v1/decide \
  -H "Content-Type: application/json" \
  -d '{
    "situation": {
      "workflow_stuck": true,
      "workflow_id": "test_001"
    },
    "tenant_id": "default"
  }'
```

### Detect a crisis
```bash
curl -X POST http://localhost:8050/api/v1/crisis/detect \
  -H "Content-Type: application/json" \
  -d '{
    "situation": {
      "critical_services_affected": ["bia", "risk"],
      "error_rate": 0.35
    },
    "tenant_id": "default"
  }'
```

### Trigger evolution
```bash
curl -X POST http://localhost:8050/admin/evolve
```

### Clear cache
```bash
curl -X POST http://localhost:8050/admin/cache/clear
```

## Monitoring

### Prometheus Metrics
```bash
curl http://localhost:8050/metrics
```

### Grafana Dashboards
1. Start Grafana: `docker-compose up -d grafana`
2. Import dashboards from `/infrastructure/monitoring/grafana/dashboards/`
   - `orchestrator-overview.json`
   - `orchestrator-efficiency.json`

### View Alerts
Check Prometheus alerts at: `http://localhost:9090/alerts`

## Production Deployment

### 1. Environment Variables
```bash
export EVENT_BUS_BACKEND=redis
export REDIS_URL=redis://localhost:6379
export DATABASE_URL=postgresql://user:pass@host:5432/db
export ENABLE_EVOLUTION=true
export ENABLE_SAFETY=true
```

### 2. Docker Deployment
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/ai-orchestration

# Build image
docker build -t ai-orchestrator:latest .

# Run container
docker run -p 8050:8050 \
  -e EVENT_BUS_BACKEND=redis \
  -e REDIS_URL=redis://redis:6379 \
  ai-orchestrator:latest
```

### 3. Kubernetes Deployment
```bash
kubectl apply -f k8s/orchestrator-deployment.yaml
kubectl apply -f k8s/orchestrator-service.yaml
```

## Support

For issues, check:
- Logs: `/var/log/orchestrator/`
- Documentation: `/docs/ORCHESTRATOR_FINAL_DELIVERY.md`
- Tests: `pytest tests/test_e2e.py -v`

## Summary

✅ Orchestrator API running on port 8050
✅ Admin Panel running on port 3000
✅ Control Panel at /orchestrator route
✅ Real-time monitoring every 5-10 seconds
✅ Quick actions for management

🎉 Ready to use!
