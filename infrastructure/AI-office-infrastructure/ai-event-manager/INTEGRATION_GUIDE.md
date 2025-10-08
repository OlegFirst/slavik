# AI Event Manager - Complete Integration Guide

## Overview

AI Event Manager v2.0 is now **fully integrated** with all major platform components, providing:

- **Event-Driven Architecture** via EventBus
- **AI-Powered Analysis** via Event Intelligence
- **Infrastructure Scanning** via DevOps Agent
- **Code Repository Integration** via GitHub Integration
- **Platform Coordination** via MIO Manager
- **Continuous Monitoring** with automatic gap detection

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  AI Event Manager v2.0                       │
│                 (Port 8055)                                  │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ Integration Manager
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   EventBus   │    │    Event     │    │   DevOps     │
│              │    │ Intelligence │    │    Agent     │
│ (Redis/Mem)  │    │ (Port 8039)  │    │ (Port 8050)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   GitHub     │    │     MIO      │    │ Continuous   │
│ Integration  │    │   Manager    │    │   Monitor    │
│ (Port 8051)  │    │ (Port 8046)  │    │ (Built-in)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Quick Start

### 1. Start AI Event Manager

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager

# Using start script (recommended)
./start.sh

# Or directly
python3 main.py
```

### 2. Verify Integration Status

```bash
# Check integration health
curl http://localhost:8055/integrations/status

# Response:
{
  "integrations": {
    "eventbus": "active",
    "event_intelligence": "active",
    "devops_agent": "active",
    "github": "active",
    "mio_manager": "active",
    "monitor": "active"
  },
  "statistics": {
    "integrations_active": 6,
    "events_published": 0,
    "ai_analyses": 0,
    ...
  },
  "health": "healthy"
}
```

---

## Integration Features

### 1. EventBus Integration

**Publish events when gaps are detected:**

```bash
POST /integrations/eventbus/publish
{
  "event_name": "event.gap.detected",
  "data": {
    "event_name": "bia.completed",
    "severity": "critical"
  },
  "priority": "critical"
}
```

**Features:**
- Real-time event propagation
- Priority-based routing
- Automatic subscription management
- Works with both memory and Redis backends

### 2. Event Intelligence Integration

**AI-powered analysis:**

```bash
POST /integrations/analyze/full

# Returns:
{
  "status": "success",
  "results": {
    "infrastructure_scan": {...},
    "ai_analysis": {...},
    "critical_findings_published": 3,
    "github_issues_created": ["https://..."]
  }
}
```

**Features:**
- Pattern detection
- Predictive recommendations
- Learning from feedback
- Historical analysis

### 3. DevOps Agent Integration

**Infrastructure scanning:**

```bash
POST /integrations/scan/trigger

# Triggers immediate scan and returns:
{
  "status": "success",
  "result": {
    "scans_completed": 15,
    "gaps_detected": 8,
    "critical_gaps": 2
  }
}
```

**Features:**
- Event architecture analysis
- Container scanning
- Deployment monitoring
- Auto-fix coordination

### 4. GitHub Integration

**Automatic issue creation:**

```bash
POST /integrations/github/issue
{
  "title": "Event Gap: bia.completed",
  "body": "Critical gap detected in event architecture",
  "labels": ["event-gap", "critical"]
}

# Returns:
{
  "status": "success",
  "issue_url": "https://github.com/..."
}
```

**Features:**
- Auto-create issues for gaps
- Priority-based labeling
- Integration with PR workflows
- Issue tracking

### 5. MIO Manager Integration

**Platform coordination:**

```bash
# MIO Manager receives automatic reports:
{
  "source": "ai-event-manager",
  "type": "full_analysis_cycle",
  "results": {...},
  "recommendations": [...]
}
```

**Features:**
- Central coordination
- Task delegation
- Context sharing
- Strategic decision support

### 6. Continuous Monitor

**Automated monitoring cycle:**

```bash
# Get monitor statistics
GET /monitor/stats

{
  "scans_completed": 15,
  "gaps_detected": 8,
  "critical_gaps": 2,
  "auto_fixes_triggered": 3,
  "alerts_sent": 2,
  "running": true,
  "interval_seconds": 300
}
```

**Features:**
- Periodic scanning (every 5 minutes)
- Automatic gap detection
- Critical alert triggering
- Auto-fix coordination

---

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Enable/disable integrations
integrations:
  eventbus:
    enabled: true
    backend: "redis"  # or "memory"

  event_intelligence:
    enabled: true
    url: "http://localhost:8039"

  # ... other integrations

# Monitoring settings
monitoring:
  enabled: true
  interval_seconds: 300  # 5 minutes
  auto_fix: false  # Set true for automatic fixes
  alert_on_critical: true

# Auto-fix settings
auto_fix:
  enabled: false  # Enable with caution
  safe_only: true
  require_approval: true
  max_fixes_per_cycle: 5
```

---

## API Endpoints

### Core Endpoints

- `GET /` - Service information and integration status
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### Integration Endpoints

- `GET /integrations/status` - Integration health status
- `POST /integrations/scan/trigger` - Trigger immediate scan
- `POST /integrations/analyze/full` - Run full analysis cycle
- `POST /integrations/eventbus/publish` - Publish event to EventBus
- `POST /integrations/github/issue` - Create GitHub issue
- `GET /monitor/stats` - Monitor statistics

### Legacy Endpoints (backward compatible)

- `POST /analyze/event` - Analyze single event
- `GET /recommendations` - Get AI recommendations
- `POST /feedback` - Record feedback
- `GET /predictions/future` - Future predictions
- `GET /learning/stats` - Learning statistics

---

## Monitoring & Alerts

### Prometheus Metrics

Available at `/metrics`:

- `ai_event_manager_requests_total` - Total requests
- `ai_event_manager_request_duration_seconds` - Request duration
- `ai_event_manager_recommendations_total` - Recommendations count
- `ai_event_manager_learning_accuracy` - Learning accuracy
- `ai_event_manager_feedback_total` - Feedback count

### Alert Flow

```
1. Continuous Monitor detects critical gap
2. Publishes to EventBus (priority: critical)
3. Creates GitHub issue
4. Reports to MIO Manager
5. Triggers auto-fix (if enabled and safe)
```

---

## Deployment Options

### Option 1: Standalone

```bash
./start.sh
```

### Option 2: Docker Compose

```bash
docker-compose up -d
```

### Option 3: With Full Platform

```bash
# Start all services
cd /Users/MD/AI-Platform-ISO
docker-compose -f docker-compose.full-platform.yml up -d
```

---

## Integration Examples

### Example 1: Full Analysis Cycle

```python
import httpx

async def run_full_analysis():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8055/integrations/analyze/full"
        )
        results = response.json()

        print(f"Scan completed: {results['results']['steps_completed']}")
        print(f"Critical findings: {results['results']['critical_findings_published']}")
        print(f"GitHub issues: {results['results']['github_issues_created']}")
```

### Example 2: Subscribe to Events

```python
from infrastructure.eventbus import create_eventbus, Event

async def main():
    bus = create_eventbus('redis', redis_url='redis://localhost:6379')

    async def handle_gap(event: Event):
        print(f"Gap detected: {event.data['event_name']}")
        print(f"Severity: {event.data['severity']}")

    await bus.subscribe('event.gap.detected', handle_gap)

    # Keep listening
    await asyncio.sleep(3600)
```

### Example 3: Trigger Immediate Scan

```bash
curl -X POST http://localhost:8055/integrations/scan/trigger
```

---

## Troubleshooting

### Integration Not Available

If an integration shows as "inactive":

1. Check if the service is running:
   ```bash
   curl http://localhost:8039/health  # Event Intelligence
   curl http://localhost:8050/health  # DevOps Agent
   curl http://localhost:8051/health  # GitHub Integration
   curl http://localhost:8046/health  # MIO Manager
   ```

2. Check logs:
   ```bash
   # AI Event Manager logs show initialization status
   tail -f /var/log/ai-event-manager.log
   ```

3. Service will run in degraded mode with available integrations

### EventBus Issues

If EventBus backend fails:

1. Check Redis:
   ```bash
   redis-cli ping
   ```

2. Fallback to memory backend:
   ```yaml
   # config.yaml
   integrations:
     eventbus:
       backend: "memory"
   ```

### Monitor Not Running

If continuous monitor is not active:

```bash
# Check monitor stats
curl http://localhost:8055/monitor/stats

# Restart service
./start.sh
```

---

## Best Practices

### 1. Start with Memory Backend

For development and testing:

```yaml
integrations:
  eventbus:
    backend: "memory"
```

### 2. Enable Auto-Fix Gradually

Start with disabled, then enable for safe fixes only:

```yaml
auto_fix:
  enabled: true
  safe_only: true
  require_approval: true
  max_fixes_per_cycle: 3
```

### 3. Monitor Statistics

Regularly check integration health:

```bash
curl http://localhost:8055/integrations/status
```

### 4. Adjust Scan Interval

For active development, use shorter intervals:

```yaml
monitoring:
  interval_seconds: 60  # 1 minute
```

For production, use longer intervals:

```yaml
monitoring:
  interval_seconds: 600  # 10 minutes
```

---

## What's Next

1. **Enable Auto-Fix** (after testing):
   - Set `auto_fix.enabled: true`
   - Monitor results
   - Adjust safety settings

2. **Switch to Redis Backend** (for production):
   - Set `eventbus.backend: "redis"`
   - Ensure Redis is running
   - Restart service

3. **Integrate with CI/CD**:
   - Add to pipeline
   - Trigger scans on commits
   - Block PRs with critical gaps

4. **Custom Alerts**:
   - Configure Slack/Teams webhooks
   - Add custom alert channels
   - Customize thresholds

---

## Support

For issues or questions:

1. Check logs at `/var/log/ai-event-manager.log`
2. Review integration status at `/integrations/status`
3. Consult individual service documentation

---

**AI Event Manager v2.0 - Maximally Integrated**

All components working together for intelligent event management.
