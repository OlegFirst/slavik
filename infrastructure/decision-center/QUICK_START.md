# Phase 1.1 Decision Center - Quick Start Guide

## TL;DR - Get Started in 5 Minutes

### 1. Start Infrastructure Coordinator with Governance
```python
from infrastructure.eventbus.coordination import InfrastructureCoordinator

# Create coordinator with governance enabled
coordinator = InfrastructureCoordinator(
    event_bus_backend='redis',  # or 'memory' for testing
    enable_governance=True      # Enable Decision Center
)

# Start all services
await coordinator.start()
```

### 2. Check Decision Center Status
```python
# Get overall status
status = await coordinator.get_status()

# Decision Center statistics
dc_stats = status['decision_center']
print(f"Total decisions: {dc_stats['total_decisions']}")
print(f"Approval rate: {dc_stats['approval_rate']:.1f}%")
print(f"Active escalations: {dc_stats['active_escalations']}")
```

### 3. View Audit Logs
```bash
# Today's audit log
tail -f /Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/audit_$(date +%Y-%m-%d).jsonl

# Pretty print last 10 decisions
tail -10 /Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/audit_$(date +%Y-%m-%d).jsonl | jq .
```

### 4. Run Integration Tests
```bash
cd /Users/MD/AI-Platform-ISO
python3 tests/phase1_1/test_integration.py
```

---

## What Happens Automatically

### When a Service Fails:
1. **Health Monitor** detects failure
2. **Auto-Recovery** receives event
3. **Decision Center** is consulted (NEW!)
4. **Policy Engine** checks policies
5. **Decision** is made (approve/reject)
6. **Audit Log** entry created
7. **Recovery** executes (if approved) or blocked (if rejected)
8. **Escalation** created (if needed)

### When Optimization Runs:
1. **Resource Optimizer** generates recommendations (every 5 min)
2. **Decision Center** is consulted for each recommendation (NEW!)
3. **Policy Engine** checks policies
4. **Decision** is made (approve/reject)
5. **Audit Log** entry created
6. **Optimization** applied (if approved) or blocked (if rejected)

---

## Key Configuration Files

### 1. Policy Configuration
**File:** `/infrastructure/decision-center/policies.yaml`

**What it contains:**
- Recovery policies (max attempts, escalation thresholds)
- Optimization policies (allowed actions, thresholds)
- Compliance policies (approval requirements)
- Notification policies (channels, recipients)

**Example policy snippet:**
```yaml
recovery:
  critical_services:
    database:
      max_auto_attempts: 1        # Only 1 attempt before escalation
      escalate_after_seconds: 60  # Escalate if not recovered in 60s
      auto_create_incident: true

    api_gateway:
      max_auto_attempts: 2
      escalate_after_seconds: 180
      auto_create_incident: true
```

### 2. Audit Logs
**Location:** `/infrastructure/decision-center/audit_logs/`

**Format:** JSONL (JSON Lines - one JSON object per line)

**Example entry:**
```json
{
  "timestamp": "2025-10-09T14:30:45.123Z",
  "decision_id": "dec_abc123",
  "decision_type": "recovery",
  "service_name": "database",
  "action_type": "restart",
  "outcome": "approved",
  "reasoning": "Within policy limits (attempt 1/1)",
  "policy_reference": "recovery/database",
  "confidence_score": 1.0
}
```

---

## Common Use Cases

### Use Case 1: Check if Recovery Would Be Approved
```python
# Check policy compliance before attempting recovery
compliance = await coordinator.decision_center.check_policy_compliance(
    service_name='database',
    action_type='restart',
    current_attempt=1
)

if compliance['compliant']:
    print("✅ Recovery would be approved")
else:
    print(f"❌ Recovery would be rejected: {compliance['reason']}")
```

### Use Case 2: View Active Escalations
```python
# Get list of services currently escalated
escalations = await coordinator.decision_center.get_active_escalations()

for esc in escalations:
    print(f"Service: {esc.service_name}")
    print(f"  Reason: {esc.reason}")
    print(f"  Severity: {esc.severity}")
    print(f"  Assigned to: {esc.assigned_team}")
```

### Use Case 3: View Pending Approvals
```python
# Get list of actions awaiting manual approval
approvals = await coordinator.decision_center.get_pending_approvals()

for app in approvals:
    print(f"Action: {app.requested_action}")
    print(f"  Service: {app.service_name}")
    print(f"  Justification: {app.justification}")
    print(f"  Expires: {app.expires_at}")
```

### Use Case 4: Approve a Pending Action
```python
# Manually approve a pending action
await coordinator.decision_center.approve_action(
    approval_id='app_abc123',
    approved_by='ops_engineer',
    approved=True,
    comment='Approved after reviewing logs'
)
```

### Use Case 5: Query Audit Logs
```python
# Read and filter audit logs
import json
from datetime import datetime

log_file = f"audit_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
log_path = f"/Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/{log_file}"

with open(log_path) as f:
    for line in f:
        entry = json.loads(line)

        # Filter for rejected decisions
        if entry['outcome'] == 'rejected':
            print(f"{entry['timestamp']}: {entry['service_name']} - {entry['reasoning']}")
```

---

## Decision Center API Quick Reference

### Core Decision Methods

#### decide_recovery_action()
Decides whether to allow auto-recovery action.

```python
decision, can_proceed = await decision_center.decide_recovery_action(
    service_name='database',
    action_type='restart',
    current_attempt=1,
    trigger_event_id='evt_123',  # Optional
    trigger_data={'error': 'connection_refused'}  # Optional
)

if can_proceed:
    # Execute recovery
    pass
else:
    # Block recovery
    print(f"Blocked: {decision.reasoning}")
```

**Returns:**
- `decision`: Decision object with full details
- `can_proceed`: Boolean (True = execute, False = block)

#### decide_optimization_action()
Decides whether to apply optimization recommendation.

```python
decision, can_proceed = await decision_center.decide_optimization_action(
    service_name='api_gateway',
    action_type='scale_up',
    recommendation={
        'resource': 'cpu',
        'current_utilization': 85.0,
        'priority': 'medium'
    }
)
```

#### check_policy_compliance()
Checks if an action complies with policy (without creating decision).

```python
compliance = await decision_center.check_policy_compliance(
    service_name='database',
    action_type='restart',
    current_attempt=1
)

print(compliance['compliant'])          # True/False
print(compliance['reason'])             # Human-readable reason
print(compliance['requires_approval'])  # True if manual approval needed
print(compliance['requires_escalation']) # True if should escalate
```

### Escalation Methods

#### escalate()
Manually escalate an issue to human operators.

```python
escalation = await decision_center.escalate(
    service_name='database',
    reason='Multiple recovery failures',
    severity='critical',  # low, medium, high, critical
    context_data={
        'failure_count': 3,
        'last_error': 'Connection timeout'
    }
)
```

#### get_active_escalations()
Get list of currently active escalations.

```python
escalations = await decision_center.get_active_escalations()
# Returns: List[EscalationRequest]
```

### Approval Methods

#### approve_action()
Process manual approval for pending action.

```python
success = await decision_center.approve_action(
    approval_id='app_abc123',
    approved_by='john.doe',
    approved=True,  # True=approve, False=reject
    comment='Reviewed and approved'
)
```

#### get_pending_approvals()
Get list of actions awaiting approval.

```python
approvals = await decision_center.get_pending_approvals()
# Returns: List[ApprovalRequest]
```

### Statistics Methods

#### get_stats()
Get Decision Center statistics.

```python
stats = await decision_center.get_stats()

print(stats['total_decisions'])      # Total decisions made
print(stats['approved_decisions'])   # Number approved
print(stats['rejected_decisions'])   # Number rejected
print(stats['approval_rate'])        # Approval rate %
print(stats['automation_rate'])      # Auto-approval rate %
print(stats['active_escalations'])   # Current escalations
print(stats['pending_approvals'])    # Pending approvals
```

---

## Policy Configuration Quick Reference

### Recovery Policy Structure
```yaml
recovery:
  critical_services:
    service_name:
      max_auto_attempts: 2              # Max attempts before escalation
      escalate_after_seconds: 180       # Escalate if not recovered in time
      auto_create_incident: true        # Create incident on escalation
      allow_outside_business_hours: true # Allow recovery outside business hours

  default:
    max_auto_attempts: 3
    escalate_after_seconds: 300
```

### Optimization Policy Structure
```yaml
optimization:
  thresholds:
    cpu:
      critical: 90    # Critical threshold %
      warning: 75     # Warning threshold %
      optimal_min: 30 # Optimal range min %
      optimal_max: 70 # Optimal range max %

  actions:
    scale_up:
      requires_approval: false
      allowed_services: ['api_gateway', 'rag_pipeline']

    scale_down:
      requires_approval: true
      allowed_services: ['api_gateway']
```

### Compliance Policy Structure
```yaml
compliance:
  approval_required:
    - action: scale_down
      reason: "Cost impact"

    - action: database_restart
      reason: "Data safety"

  business_hours:
    start: "09:00"
    end: "17:00"
    timezone: "America/New_York"
```

### Notification Policy Structure
```yaml
notifications:
  escalation:
    critical:
      channels: ['slack_alerts', 'email', 'pagerduty']
      teams: ['ops_team', 'platform_team']

    high:
      channels: ['slack_alerts', 'email']
      teams: ['ops_team']
```

---

## Troubleshooting Quick Guide

### Issue: Decision Center not making decisions

**Check 1:** Is governance enabled?
```python
print(coordinator.enable_governance)  # Should be True
```

**Check 2:** Is Decision Center initialized?
```python
print(coordinator.decision_center)  # Should not be None
```

**Check 3:** Are services receiving Decision Center?
```python
print(coordinator.auto_recovery.decision_center)  # Should not be None
```

### Issue: All decisions rejected

**Check policies:**
```bash
cat /Users/MD/AI-Platform-ISO/infrastructure/decision-center/policies.yaml
```

**Check policy compliance:**
```python
compliance = await coordinator.decision_center.check_policy_compliance(
    service_name='YOUR_SERVICE',
    action_type='restart',
    current_attempt=1
)
print(compliance)
```

### Issue: Audit logs not created

**Check directory:**
```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/
```

**Check permissions:**
```bash
# Directory should be writable
touch /Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/test.txt
```

### Issue: Policies not loading

**Validate YAML:**
```bash
python3 -c "import yaml; yaml.safe_load(open('/Users/MD/AI-Platform-ISO/infrastructure/decision-center/policies.yaml'))"
```

**Check file exists:**
```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/decision-center/policies.yaml
```

---

## Performance Tuning

### Latency Optimization
```python
# Decision Center is already optimized for low latency:
# - In-memory policy engine
# - Async audit logging
# - Fast policy lookups
#
# Typical latency: < 50ms per decision
```

### Audit Log Performance
```python
# Audit logs use async buffered writes
# No performance impact on decision path
#
# For high-volume deployments:
# - Consider log rotation
# - Use SSD for audit logs
# - Archive old logs to S3/GCS
```

---

## Best Practices

### 1. Policy Management
- ✅ Version control `policies.yaml`
- ✅ Test policy changes in staging first
- ✅ Use policy validation before deployment
- ✅ Document policy changes in git commit messages

### 2. Audit Log Management
- ✅ Rotate logs regularly (e.g., keep 90 days)
- ✅ Archive old logs for compliance
- ✅ Monitor log disk usage
- ✅ Set up log analysis/search (e.g., ELK stack)

### 3. Escalation Management
- ✅ Review active escalations daily
- ✅ Document resolution steps
- ✅ Update policies based on escalation patterns
- ✅ Train team on escalation procedures

### 4. Monitoring
- ✅ Monitor approval rate (should be > 80%)
- ✅ Monitor automation rate (should be > 90%)
- ✅ Monitor escalation count (should be low)
- ✅ Set up alerts for anomalies

### 5. Testing
- ✅ Run integration tests after policy changes
- ✅ Test escalation flow monthly
- ✅ Test approval workflow monthly
- ✅ Verify audit logs are complete

---

## Next Steps

### For Development:
1. Read `/infrastructure/decision-center/PHASE_1_1_INTEGRATION_SUMMARY.md`
2. Run integration tests: `python3 tests/phase1_1/test_integration.py`
3. Experiment with policy changes
4. Test approval workflows

### For Deployment:
1. Follow `/infrastructure/decision-center/DEPLOYMENT_CHECKLIST.md`
2. Test in staging environment first
3. Monitor closely after production deployment
4. Have rollback plan ready

### For Operations:
1. Set up log monitoring/alerts
2. Create escalation runbooks
3. Train team on approval workflows
4. Schedule regular policy reviews

---

## Support

### Documentation
- **Integration Summary:** `PHASE_1_1_INTEGRATION_SUMMARY.md`
- **Deployment Checklist:** `DEPLOYMENT_CHECKLIST.md`
- **This Guide:** `QUICK_START.md`

### Code Locations
- **Decision Center:** `/infrastructure/decision-center/`
- **Auto-Recovery:** `/infrastructure/eventbus/coordination/auto_recovery.py`
- **Resource Optimizer:** `/infrastructure/eventbus/coordination/resource_optimizer.py`
- **Coordinator:** `/infrastructure/eventbus/coordination/infrastructure_coordinator.py`

### Test Locations
- **Integration Tests:** `/tests/phase1_1/test_integration.py`

---

**Last Updated:** October 9, 2025
**Version:** 1.0
