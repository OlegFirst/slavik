# Infrastructure Coordination Events (Phase 1)
**Category:** Infrastructure Level
**Created:** 2025-10-09
**Component:** Infrastructure Coordination

---

## Infrastructure Health Events

### `infrastructure.health.healthy`
**Description:** Service health check passed - service is healthy

**Publishers:**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py` - Health Monitor

**Data Schema:**
```json
{
  "service_name": "string",
  "status": "healthy",
  "previous_status": "string|null",
  "response_time_ms": "float",
  "message": "string",
  "details": "object",
  "checked_at": "ISO8601 timestamp"
}
```

**Subscribers:**
- Auto-Recovery Service (monitors for recovery completion)
- Monitoring Dashboard
- Alert Manager

**Triggering Conditions:**
- Health check succeeds AND status changed from non-healthy state
- Response time within acceptable limits

---

### `infrastructure.health.unhealthy`
**Description:** Service health check failed - service is unhealthy

**Publishers:**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py` - Health Monitor

**Data Schema:**
```json
{
  "service_name": "string",
  "status": "unhealthy",
  "previous_status": "string|null",
  "response_time_ms": "float|null",
  "message": "string",
  "details": "object",
  "checked_at": "ISO8601 timestamp"
}
```

**Subscribers:**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery Service
- Notification Service (for critical alerts)
- Monitoring Dashboard
- Alert Manager

**Triggering Conditions:**
- Health check fails
- Service not responding
- Response time exceeds threshold
- Connection errors

**Recovery Actions:**
- Auto-Recovery initiates recovery strategy
- Alert sent to operations team
- Circuit breaker may be activated

---

### `infrastructure.health.degraded`
**Description:** Service health check shows degraded performance

**Publishers:**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py` - Health Monitor

**Data Schema:**
```json
{
  "service_name": "string",
  "status": "degraded",
  "previous_status": "string|null",
  "response_time_ms": "float",
  "message": "string",
  "details": "object",
  "checked_at": "ISO8601 timestamp"
}
```

**Subscribers:**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery Service
- Resource Optimizer (for capacity planning)
- Monitoring Dashboard

**Triggering Conditions:**
- Response time higher than normal but below failure threshold
- Partial functionality available
- Warning indicators present

**Recovery Actions:**
- Auto-Recovery may initiate optimization
- Resource Optimizer analyzes capacity needs
- Warning alerts sent

---

### `infrastructure.health.unknown`
**Description:** Service health status cannot be determined

**Publishers:**
- `intelligent-core/orchestration/ai-orchestration/core/health_monitor.py` - Health Monitor

**Data Schema:**
```json
{
  "service_name": "string",
  "status": "unknown",
  "previous_status": "string|null",
  "response_time_ms": "null",
  "message": "string",
  "details": "object",
  "checked_at": "ISO8601 timestamp"
}
```

**Subscribers:**
- Monitoring Dashboard
- Alert Manager

**Triggering Conditions:**
- Health check endpoint not configured
- Network issues preventing checks
- Service discovery failure

---

## Infrastructure Recovery Events

### `infrastructure.recovery.started`
**Description:** Automatic recovery process initiated for unhealthy service

**Publishers:**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery Service

**Data Schema:**
```json
{
  "service_name": "string",
  "strategy_type": "restart|failover|circuit_breaker",
  "attempt": "integer",
  "max_attempts": "integer",
  "timestamp": "ISO8601 timestamp",
  "reason": "string",
  "previous_health_status": "string"
}
```

**Subscribers:**
- Health Monitor (for status tracking)
- Monitoring Dashboard
- Alert Manager
- Notification Service

**Triggering Conditions:**
- infrastructure.health.unhealthy received
- infrastructure.health.degraded received (if critical)
- Recovery strategy registered for service

**Actions:**
- Execute recovery function (restart, failover, etc.)
- Log recovery attempt
- Publish status updates

---

### `infrastructure.recovery.completed`
**Description:** Automatic recovery successfully completed

**Publishers:**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery Service

**Data Schema:**
```json
{
  "service_name": "string",
  "strategy_type": "restart|failover|circuit_breaker",
  "attempt": "integer",
  "duration_seconds": "float",
  "timestamp": "ISO8601 timestamp",
  "new_health_status": "string"
}
```

**Subscribers:**
- Monitoring Dashboard
- Metrics Collector (for recovery time tracking)
- Alert Manager (for notification closure)

**Success Criteria:**
- Recovery function executed without errors
- Service returns to healthy state
- Health checks pass

---

### `infrastructure.recovery.failed`
**Description:** Automatic recovery failed after all retry attempts

**Publishers:**
- `infrastructure/eventbus/coordination/auto_recovery.py` - Auto-Recovery Service

**Data Schema:**
```json
{
  "service_name": "string",
  "strategy_type": "restart|failover|circuit_breaker",
  "attempts_made": "integer",
  "max_attempts": "integer",
  "duration_seconds": "float",
  "timestamp": "ISO8601 timestamp",
  "error_message": "string",
  "requires_manual_intervention": "boolean"
}
```

**Subscribers:**
- Notification Service (CRITICAL alerts)
- Incident Management System
- Monitoring Dashboard
- On-call Team

**Failure Scenarios:**
- All retry attempts exhausted
- Recovery function errors
- Service remains unhealthy after recovery
- Dependencies unavailable

**Escalation:**
- Critical alert to operations team
- Incident ticket created
- Manual intervention required
- Possible system-wide impact assessment

---

## Infrastructure Optimization Events

### `infrastructure.optimization.completed`
**Description:** Resource optimization cycle completed

**Publishers:**
- `infrastructure/eventbus/coordination/resource_optimizer.py` - Resource Optimizer

**Data Schema:**
```json
{
  "cycle": "integer",
  "timestamp": "ISO8601 timestamp",
  "metrics": {
    "cpu": {"service_name": "float (percentage)"},
    "memory": {"service_name": "float (percentage)"},
    "disk": {"service_name": "float (percentage)"}
  },
  "analysis": {
    "overutilized": [
      {
        "service": "string",
        "resource": "cpu|memory|disk",
        "utilization": "float"
      }
    ],
    "underutilized": [
      {
        "service": "string",
        "resource": "cpu|memory|disk",
        "utilization": "float"
      }
    ],
    "optimal": [
      {
        "service": "string",
        "resource": "cpu|memory|disk",
        "utilization": "float"
      }
    ]
  },
  "recommendations": [
    {
      "service": "string",
      "resource": "string",
      "action": "scale_up|scale_down|optimize",
      "priority": "high|medium|low",
      "current_utilization": "float",
      "reason": "string"
    }
  ],
  "efficiency_score": "float (0-100)"
}
```

**Subscribers:**
- Capacity Planning Service
- Auto-Scaler (if implemented)
- Monitoring Dashboard
- Cost Optimization Service

**Optimization Cycle:**
- Runs every 5 minutes
- Collects resource metrics from all services
- Analyzes utilization patterns
- Generates recommendations
- Calculates efficiency score

**Thresholds:**
- Overutilized: > 80%
- Underutilized: < 30%
- Optimal: 30-80%

**Recommendation Actions:**
- `scale_up`: Add resources (utilization > 90%)
- `optimize`: Tune configuration (utilization 80-90%)
- `scale_down`: Reduce resources (utilization < 20%)

**Priority Levels:**
- `high`: Immediate action required (> 90% or < 10%)
- `medium`: Action recommended (80-90% or 10-20%)
- `low`: Monitor only (< 80% and > 20%)

---

## Event Flow Diagrams

### Health Monitoring Flow
```
┌─────────────────┐
│ Health Monitor  │
│ (30s intervals) │
└────────┬────────┘
         │
         ├─► [Check Service Health]
         │
         ├─► [Compare with Previous Status]
         │
         ├─► If Changed:
         │   └─► Publish infrastructure.health.{status}
         │       └─► Event Data: {
         │           service_name,
         │           status,
         │           previous_status,
         │           response_time_ms,
         │           details
         │         }
         │
         └─► Wait 30 seconds → Repeat
```

### Auto-Recovery Flow
```
┌───────────────────────────────────────┐
│ infrastructure.health.unhealthy       │
│ OR infrastructure.health.degraded     │
└──────────────┬────────────────────────┘
               │
               ▼
┌──────────────────────────┐
│ Auto-Recovery Service    │
│ _handle_unhealthy()      │
└──────────┬───────────────┘
           │
           ├─► Check if recovery in progress? → Skip if yes
           │
           ├─► Get recovery strategy for service
           │
           ├─► Publish infrastructure.recovery.started
           │
           ├─► Execute recovery with retries:
           │   │
           │   ├─► Attempt 1 → Wait backoff_seconds
           │   ├─► Attempt 2 → Wait backoff_seconds * 2
           │   ├─► Attempt 3 → Wait backoff_seconds * 4
           │   └─► ... (exponential backoff)
           │
           ├─► Recovery Success?
           │   ├─► YES → Publish infrastructure.recovery.completed
           │   └─► NO  → Publish infrastructure.recovery.failed
           │
           └─► Clear recovery_in_progress flag
```

### Resource Optimization Flow
```
┌────────────────────────┐
│ Resource Optimizer     │
│ (5 minute cycles)      │
└───────────┬────────────┘
            │
            ├─► 1. Collect Metrics
            │   └─► CPU, Memory, Disk per service
            │
            ├─► 2. Analyze Utilization
            │   ├─► Overutilized (> 80%)
            │   ├─► Underutilized (< 30%)
            │   └─► Optimal (30-80%)
            │
            ├─► 3. Generate Recommendations
            │   ├─► scale_up (> 90%)
            │   ├─► optimize (80-90%)
            │   └─► scale_down (< 20%)
            │
            ├─► 4. Calculate Efficiency Score
            │   └─► 0-100 based on optimal ratio
            │
            ├─► 5. Publish infrastructure.optimization.completed
            │
            └─► Wait 5 minutes → Repeat
```

---

## Integration with Existing Systems

### Prometheus Metrics
All infrastructure events are exposed via Metrics API on port 9091:
- `infrastructure_health_status{service="X", status="Y"}`
- `infrastructure_recovery_attempts_total{service="X", strategy="Y"}`
- `infrastructure_resource_utilization{service="X", resource="Y"}`
- `infrastructure_efficiency_score`

### Grafana Dashboards
Recommended dashboards:
- Infrastructure Health Overview
- Service Recovery Timeline
- Resource Utilization Trends
- Efficiency Score History

### Alert Manager Rules
Critical alerts:
- Service unhealthy for > 5 minutes
- Recovery failed after all attempts
- Efficiency score < 60 for > 15 minutes
- Critical service (database, eventbus) degraded

---

## Event Catalog Statistics

**Total Infrastructure Events:** 7
- Health Events: 4
- Recovery Events: 3
- Optimization Events: 1

**Event Categories:**
- Monitoring: 4 events
- Resilience: 3 events
- Performance: 1 event

**Critical Services Monitored:**
1. eventbus (port 8055)
2. api_gateway (port 8000)
3. database (port 5432)
4. redis (port 6379)
5. rag_pipeline (port 8020)

---

## Usage Examples

### Example 1: Health Check Failure → Auto-Recovery

```python
# 1. Health Monitor detects failure
Event: infrastructure.health.unhealthy
{
  "service_name": "api_gateway",
  "status": "unhealthy",
  "previous_status": "healthy",
  "response_time_ms": null,
  "message": "Connection refused",
  "checked_at": "2025-10-09T10:30:00Z"
}

# 2. Auto-Recovery initiates
Event: infrastructure.recovery.started
{
  "service_name": "api_gateway",
  "strategy_type": "restart",
  "attempt": 1,
  "max_attempts": 3,
  "timestamp": "2025-10-09T10:30:05Z"
}

# 3. Recovery succeeds
Event: infrastructure.recovery.completed
{
  "service_name": "api_gateway",
  "strategy_type": "restart",
  "attempt": 1,
  "duration_seconds": 12.5,
  "timestamp": "2025-10-09T10:30:17Z",
  "new_health_status": "healthy"
}
```

### Example 2: Resource Optimization Recommendations

```python
Event: infrastructure.optimization.completed
{
  "cycle": 42,
  "timestamp": "2025-10-09T10:35:00Z",
  "metrics": {
    "cpu": {
      "database": 88.0,
      "api_gateway": 45.0,
      "rag_pipeline": 25.0
    },
    "memory": {
      "database": 92.0,
      "eventbus": 55.0
    }
  },
  "analysis": {
    "overutilized": [
      {"service": "database", "resource": "cpu", "utilization": 88.0},
      {"service": "database", "resource": "memory", "utilization": 92.0}
    ],
    "underutilized": [
      {"service": "rag_pipeline", "resource": "cpu", "utilization": 25.0}
    ],
    "optimal": [
      {"service": "api_gateway", "resource": "cpu", "utilization": 45.0},
      {"service": "eventbus", "resource": "memory", "utilization": 55.0}
    ]
  },
  "recommendations": [
    {
      "service": "database",
      "resource": "memory",
      "action": "scale_up",
      "priority": "high",
      "current_utilization": 92.0,
      "reason": "memory utilization at 92.0%"
    },
    {
      "service": "database",
      "resource": "cpu",
      "action": "optimize",
      "priority": "medium",
      "current_utilization": 88.0,
      "reason": "cpu utilization at 88.0%"
    }
  ],
  "efficiency_score": 72.5
}
```

---

## Version History

**v1.0.0 (2025-10-09)** - Initial Phase 1 Release
- Added infrastructure health events (healthy, unhealthy, degraded, unknown)
- Added infrastructure recovery events (started, completed, failed)
- Added infrastructure optimization events (completed)
- Integrated with Health Monitor, Auto-Recovery, Resource Optimizer
- Connected to Prometheus metrics (port 9091)

---

## References

- [Phase 1 Integration Plan](../../../doc-project/PHASE_1_INTEGRATION_PLAN.md)
- [Health Monitor](../../../intelligent-core/orchestration/ai-orchestration/core/health_monitor.py)
- [Auto-Recovery](../coordination/auto_recovery.py)
- [Resource Optimizer](../coordination/resource_optimizer.py)
- [Infrastructure Coordinator](../coordination/infrastructure_coordinator.py)
- [Metrics API](../../../intelligent-core/orchestration/api/metrics_api.py)
