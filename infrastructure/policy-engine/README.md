# Decision Center - Policy Engine

**Phase 1.1: Minimal Governance Layer for Infrastructure Coordination**

## Overview

The Policy Engine is the central authority for all infrastructure governance policies. Instead of hardcoding thresholds, limits, and rules throughout the codebase, everything is defined in a single `policies.yaml` file that can be:

- ✅ Updated without code changes
- ✅ Validated before deployment
- ✅ Hot-reloaded without service restart
- ✅ Version controlled
- ✅ Approved by stakeholders

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Policy Engine                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌────────────────┐              │
│  │ policies.yaml│────▶│ PolicyValidator│              │
│  └──────────────┘     └───────┬────────┘              │
│                               │                        │
│                               ▼                        │
│                    ┌──────────────────┐               │
│                    │  Pydantic Models │               │
│                    └─────────┬────────┘               │
│                              │                        │
│                              ▼                        │
│                   ┌────────────────────┐             │
│                   │   PolicyEngine     │             │
│                   │  - get_policy()    │             │
│                   │  - get_threshold() │             │
│                   │  - check_compliance│             │
│                   │  - reload()        │             │
│                   └────────────────────┘             │
│                                                       │
└───────────────────────────────────────────────────────┘
                          │
                          │ Used by:
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Auto-Recovery│  │ Health Monitor│  │  Optimizer   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Components

### 1. PolicyEngine (`policy_engine.py`)

Central policy management and query interface.

**Key Methods:**

- `load_policies(file)` - Load policies from YAML
- `reload_policies()` - Hot reload without restart
- `get_recovery_policy(service)` - Get recovery policy for a service
- `get_threshold(resource, level)` - Get optimization threshold
- `check_compliance(action, service)` - Check if action is allowed
- `get_service_priority(service)` - Get service priority
- `validate_action_context(action, service, context)` - Comprehensive validation

### 2. PolicyValidator (`policy_validator.py`)

Validates policy files before loading to ensure correctness.

**Checks:**
- ✅ Required fields present
- ✅ Value types correct
- ✅ Thresholds in ascending order (normal < high < critical)
- ✅ Service names valid
- ✅ No conflicts between auto_execute and manual_only
- ✅ RPO ≤ RTO
- ✅ Escalation delays increasing

### 3. Policy Models (`policy_models.py`)

Pydantic models for type safety and validation.

**Models:**
- `PolicyConfiguration` - Complete config
- `RecoveryPolicy` - Recovery policies
- `OptimizationPolicy` - Optimization policies
- `MonitoringPolicy` - Monitoring policies
- `CompliancePolicy` - Audit policies
- `NotificationPolicy` - Notification policies

### 4. policies.yaml

Human-readable YAML file with all policies.

**Sections:**
1. **Recovery** - How to recover failed services
2. **Optimization** - Resource thresholds and actions
3. **Monitoring** - Health check intervals
4. **Compliance** - Audit and regulatory requirements
5. **Notifications** - Alert channels and escalation

## Usage

### Initialization

```python
from infrastructure.decision_center import (
    initialize_policy_engine,
    get_policy_engine
)

# Initialize at application startup
engine = initialize_policy_engine("/path/to/policies.yaml")

# Or use default location
from infrastructure.decision_center import create_default_engine
engine = create_default_engine()
```

### Query Policies

```python
# Get recovery policy for a service
policy = engine.get_recovery_policy("database")
print(f"RTO: {policy.rto_seconds}s")
print(f"Max attempts: {policy.max_auto_attempts}")
print(f"Strategy: {policy.recovery_strategy}")

# Get optimization thresholds
cpu_critical = engine.get_threshold("cpu", "critical")  # Returns: 90
memory_high = engine.get_threshold("memory", "high")    # Returns: 85

# Check if action requires approval
compliance = engine.check_compliance("scale_up", "api_gateway")
if compliance["requires_approval"]:
    print("Need approval before scaling up")

# Get service priority
priority = engine.get_service_priority("database")  # Returns: 1 (critical)

# Get monitoring interval based on priority
interval = engine.get_monitoring_interval(priority)  # Returns: 30 seconds
```

### Validate Actions

```python
# Comprehensive validation
context = {
    "attempts": 3,
    "metrics": {
        "cpu": 95,
        "memory": 88
    }
}

result = engine.validate_action_context(
    action="restart",
    service_name="database",
    context=context
)

if result["allowed"]:
    print(f"Action allowed: {result['recovery_strategy']}")
else:
    print(f"Action blocked: {result['violations']}")
```

### Hot Reload

```python
# Reload policies without restarting service
success = engine.reload_policies()

if success:
    print("Policies reloaded successfully")
else:
    print("Reload failed, using existing policies")
```

## Migration from Hardcoded Values

### Before (Hardcoded)

```python
# In auto_recovery.py
MAX_RETRY_ATTEMPTS = 3
DATABASE_RTO = 120
ESCALATION_TIMEOUT = 300

# In optimizer.py
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 85

# In health_monitor.py
CHECK_INTERVAL = 60
```

### After (Policy-Driven)

```python
from infrastructure.decision_center import get_policy_engine

engine = get_policy_engine()

# In auto_recovery.py
policy = engine.get_recovery_policy(service_name)
max_attempts = policy.max_auto_attempts
rto = policy.rto_seconds
default_policy = engine.get_default_recovery_policy()
escalation_timeout = default_policy.escalation_timeout_seconds

# In optimizer.py
cpu_threshold = engine.get_threshold("cpu", "critical")
memory_threshold = engine.get_threshold("memory", "high")

# In health_monitor.py
priority = engine.get_service_priority(service_name)
check_interval = engine.get_monitoring_interval(priority)
```

## Validation

### Validate Before Loading

```python
from infrastructure.decision_center import validate_policy_file

is_valid, errors, warnings = validate_policy_file("policies.yaml")

if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Validation passed!")
    for warning in warnings:
        print(f"  ⚠ {warning}")
```

### Validation Rules

The validator checks:

1. **Structure**: All required sections present
2. **Types**: Values match expected types
3. **Thresholds**: Ascending order (normal < high < critical)
4. **Policies**: RPO ≤ RTO for all services
5. **Actions**: No conflicts between auto_execute and manual_only
6. **Escalations**: Delays increase with each level
7. **Services**: Service names are recognized (warning only)
8. **Teams**: Team names are recognized (warning only)

## Policy File Structure

```yaml
version: "1.0"
updated: "2025-10-09"
approved_by: "system_architect"

infrastructure_policies:
  recovery:
    default:
      max_auto_attempts: 3
      escalation_timeout_seconds: 300
      backoff_seconds: 5
      require_approval_after_attempts: 2

    by_service:
      database:
        priority: 1
        rto_seconds: 120
        rpo_seconds: 300
        max_auto_attempts: 2
        recovery_strategy: "circuit_breaker"
        notify_teams: ["ops", "dba"]

  optimization:
    thresholds:
      cpu:
        normal: 70
        high: 80
        critical: 90

    actions:
      require_approval:
        scale_up: true
        restart: false
      auto_execute:
        - "optimize"
        - "restart"

  monitoring:
    intervals:
      critical_services: 30
      normal_services: 60
      low_priority: 120

  compliance:
    audit_enabled: true
    iso_22301_compliance: true
    log_retention_days: 90

  notifications:
    channels:
      email:
        enabled: true
        recipients: ["ops@example.com"]

    escalation_levels:
      - level: 1
        delay_seconds: 0
        notify: ["ops_team"]
```

## Examples

### Example 1: Auto-Recovery Integration

```python
from infrastructure.decision_center import get_policy_engine

class AutoRecovery:
    def __init__(self):
        self.policy_engine = get_policy_engine()

    def attempt_recovery(self, service_name: str, attempt: int):
        # Get policy for service
        policy = self.policy_engine.get_recovery_policy(service_name)

        # Check if max attempts reached
        if attempt >= policy.max_auto_attempts:
            self.escalate(
                service_name,
                reason=f"Max attempts ({policy.max_auto_attempts}) exceeded"
            )
            return False

        # Check if within RTO
        if self.time_since_failure > policy.rto_seconds:
            self.escalate(
                service_name,
                reason=f"RTO ({policy.rto_seconds}s) exceeded"
            )
            return False

        # Execute recovery with configured strategy
        return self.execute_strategy(policy.recovery_strategy)
```

### Example 2: Health Monitor Integration

```python
from infrastructure.decision_center import get_policy_engine

class HealthMonitor:
    def __init__(self):
        self.policy_engine = get_policy_engine()

    def get_check_interval(self, service_name: str) -> int:
        # Get service priority from policy
        priority = self.policy_engine.get_service_priority(service_name)

        # Get monitoring interval based on priority
        return self.policy_engine.get_monitoring_interval(priority)

    async def monitor_service(self, service_name: str):
        interval = self.get_check_interval(service_name)

        while True:
            await asyncio.sleep(interval)
            health = await self.check_health(service_name)

            if health.status == "unhealthy":
                self.trigger_recovery(service_name)
```

### Example 3: Optimizer Integration

```python
from infrastructure.decision_center import get_policy_engine

class Optimizer:
    def __init__(self):
        self.policy_engine = get_policy_engine()

    def analyze_metrics(self, service_name: str, metrics: dict):
        # Get thresholds from policy
        cpu_critical = self.policy_engine.get_threshold("cpu", "critical")
        memory_high = self.policy_engine.get_threshold("memory", "high")

        actions = []

        # Check CPU
        if metrics["cpu"] >= cpu_critical:
            actions.append(("scale_up", "CPU critical"))

        # Check Memory
        if metrics["memory"] >= memory_high:
            actions.append(("optimize", "Memory high"))

        # Execute allowed actions
        for action, reason in actions:
            self.execute_if_allowed(action, service_name, reason)

    def execute_if_allowed(self, action: str, service: str, reason: str):
        # Check compliance
        compliance = self.policy_engine.check_compliance(action, service)

        if not compliance["allowed"]:
            print(f"Action blocked: {compliance['reason']}")
            return

        if compliance["requires_approval"]:
            self.request_approval(action, service, reason)
        elif compliance["auto_execute"]:
            self.execute_action(action, service)
```

## Testing

```python
import pytest
from pathlib import Path
from infrastructure.decision_center import PolicyEngine

def test_policy_loading():
    engine = PolicyEngine()
    engine.load_policies("policies.yaml")

    assert engine.get_service_priority("database") == 1
    assert engine.get_threshold("cpu", "critical") == 90

def test_recovery_policy():
    engine = PolicyEngine("policies.yaml")
    policy = engine.get_recovery_policy("database")

    assert policy.priority == 1
    assert policy.rto_seconds == 120
    assert policy.recovery_strategy == "circuit_breaker"

def test_compliance_check():
    engine = PolicyEngine("policies.yaml")

    # Scale up requires approval
    result = engine.check_compliance("scale_up")
    assert result["requires_approval"] == True

    # Restart is auto-execute
    result = engine.check_compliance("restart")
    assert result["auto_execute"] == True
```

## API Reference

See docstrings in:
- `policy_engine.py` - Main engine API
- `policy_validator.py` - Validation API
- `policy_models.py` - Pydantic models

## Benefits

1. **Centralized Governance** - All policies in one place
2. **No Code Changes** - Update policies via YAML
3. **Hot Reload** - No service restarts required
4. **Type Safety** - Pydantic validation
5. **Auditability** - Version control for policies
6. **Compliance** - ISO 22301 aligned
7. **Flexibility** - Easy to add new services/thresholds

## Next Steps

Phase 1.2 will add:
- Policy versioning and rollback
- Policy A/B testing
- Policy analytics
- Integration with existing EscalationManager
- Policy recommendation engine
