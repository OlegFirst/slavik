# Phase 1.1 Governance Layer - Deployment Checklist

## Overview
This checklist ensures proper deployment of the Phase 1.1 Governance Layer (Decision Center) into the running Infrastructure Coordinator.

**Deployment Date:** _____________
**Deployed By:** _____________
**Environment:** _____________

---

## Pre-Deployment Checks

### 1. Code Verification
- [ ] **Auto-Recovery Integration** (`/infrastructure/eventbus/coordination/auto_recovery.py`)
  - [ ] Decision Center parameter added to `__init__()`
  - [ ] Decision Center check added in `_execute_recovery()` before recovery attempts
  - [ ] Proper error handling for blocked recoveries
  - [ ] Backward compatibility maintained (works without Decision Center)

- [ ] **Resource Optimizer Integration** (`/infrastructure/eventbus/coordination/resource_optimizer.py`)
  - [ ] Decision Center parameter added to `__init__()`
  - [ ] `_apply_recommendations()` method checks decisions
  - [ ] `_apply_optimization()` helper method implemented
  - [ ] Backward compatibility maintained (works without Decision Center)

- [ ] **Infrastructure Coordinator Integration** (`/infrastructure/eventbus/coordination/infrastructure_coordinator.py`)
  - [ ] `enable_governance` parameter added
  - [ ] Policy engine initialization in `__init__()`
  - [ ] Decision Center, Escalation Manager, Notification Service created
  - [ ] Startup logging enhanced with governance status
  - [ ] Status endpoint includes Decision Center stats
  - [ ] All components receive Decision Center instance

### 2. Decision Center Components
- [ ] **Policy Engine** (`/infrastructure/decision-center/policy_engine.py`)
  - [ ] Exists and functional
  - [ ] Can load policies from YAML
  - [ ] Provides query interface

- [ ] **Decision Center** (`/infrastructure/decision-center/decision_center.py`)
  - [ ] Exists and functional
  - [ ] `decide_recovery_action()` implemented
  - [ ] `decide_optimization_action()` implemented
  - [ ] Audit logging functional
  - [ ] Escalation integration working

- [ ] **Audit Logger** (`/infrastructure/decision-center/audit_logger.py`)
  - [ ] Exists and functional
  - [ ] Logs decisions to file
  - [ ] Creates audit directory if needed
  - [ ] JSONL format validated

- [ ] **Policy YAML** (`/infrastructure/decision-center/policies.yaml`)
  - [ ] File exists
  - [ ] Contains recovery policies
  - [ ] Contains optimization policies
  - [ ] Contains compliance policies
  - [ ] Contains notification policies
  - [ ] Valid YAML syntax

### 3. Dependencies
- [ ] **Python Packages**
  - [ ] `pyyaml` installed (for policy loading)
  - [ ] `pydantic` installed (for models)
  - [ ] All existing dependencies satisfied

- [ ] **File System**
  - [ ] Audit log directory exists or can be created
  - [ ] Write permissions for audit logs
  - [ ] Read permissions for policy files

### 4. Testing
- [ ] **Unit Tests**
  - [ ] Policy Engine tests pass
  - [ ] Decision Center tests pass
  - [ ] Audit Logger tests pass

- [ ] **Integration Tests**
  - [ ] Run `/tests/phase1_1/test_integration.py`
  - [ ] All test scenarios pass
  - [ ] No errors in logs
  - [ ] Decisions are logged correctly
  - [ ] Escalations are created as expected

---

## Deployment Steps

### Step 1: Backup Current System
- [ ] Backup current codebase
  - [ ] Location: `_________________`
  - [ ] Verified backup integrity

- [ ] Backup configuration files
  - [ ] EventBus configuration
  - [ ] Coordinator configuration

- [ ] Document current state
  - [ ] Services running: `_________________`
  - [ ] Version: `_________________`

### Step 2: Deploy Code Changes
- [ ] Deploy updated `auto_recovery.py`
  - [ ] Code reviewed
  - [ ] Deployed successfully
  - [ ] No syntax errors

- [ ] Deploy updated `resource_optimizer.py`
  - [ ] Code reviewed
  - [ ] Deployed successfully
  - [ ] No syntax errors

- [ ] Deploy updated `infrastructure_coordinator.py`
  - [ ] Code reviewed
  - [ ] Deployed successfully
  - [ ] No syntax errors

- [ ] Deploy Decision Center components
  - [ ] All files in `/infrastructure/decision-center/` deployed
  - [ ] `__init__.py` updated with all exports
  - [ ] File permissions correct

### Step 3: Deploy Configuration
- [ ] Deploy `policies.yaml`
  - [ ] File placed in `/infrastructure/decision-center/policies.yaml`
  - [ ] Read permissions verified
  - [ ] YAML syntax validated

- [ ] Create audit log directory
  - [ ] Directory: `/infrastructure/decision-center/audit_logs/`
  - [ ] Write permissions verified
  - [ ] Created: `_________________` (date/time)

### Step 4: Configuration
- [ ] Configure Policy Engine
  - [ ] Policy file path correct
  - [ ] Policies load successfully
  - [ ] No validation errors

- [ ] Configure Decision Center
  - [ ] EventBus connection configured
  - [ ] Audit logger path configured
  - [ ] Database session factory configured (if using DB)

- [ ] Configure Notification Service
  - [ ] SMTP settings (if using email)
  - [ ] Slack webhook (if using Slack)
  - [ ] Recipient lists verified

### Step 5: Testing in Staging/Development
- [ ] Start Infrastructure Coordinator
  - [ ] With `enable_governance=True`
  - [ ] Verify startup logs show governance components
  - [ ] No errors during initialization

- [ ] Test Auto-Recovery with Decision Center
  - [ ] Simulate service failure
  - [ ] Verify Decision Center consulted
  - [ ] Verify decision logged
  - [ ] Verify recovery proceeds if approved

- [ ] Test Resource Optimizer with Decision Center
  - [ ] Wait for optimization cycle
  - [ ] Verify Decision Center consulted for recommendations
  - [ ] Verify decisions logged

- [ ] Test Escalation Flow
  - [ ] Simulate repeated failures
  - [ ] Verify escalation created
  - [ ] Verify notifications sent
  - [ ] Verify recovery blocked after escalation

- [ ] Test Audit Logs
  - [ ] Verify audit log file created
  - [ ] Verify JSONL format
  - [ ] Verify all decisions logged
  - [ ] Verify log rotation (if configured)

- [ ] Run Integration Test Suite
  ```bash
  cd /Users/MD/AI-Platform-ISO
  python tests/phase1_1/test_integration.py
  ```
  - [ ] All tests pass
  - [ ] Expected output verified
  - [ ] Statistics look correct

### Step 6: Smoke Tests
- [ ] Health Monitor still functional
  - [ ] Health checks running
  - [ ] Events published
  - [ ] No errors

- [ ] Auto-Recovery still functional
  - [ ] Listens to events
  - [ ] Executes recovery (when approved)
  - [ ] Respects Decision Center blocks

- [ ] Resource Optimizer still functional
  - [ ] Cycles running
  - [ ] Recommendations generated
  - [ ] Respects Decision Center decisions

- [ ] EventBus still functional
  - [ ] Events published
  - [ ] Events subscribed
  - [ ] No connection issues

### Step 7: Monitor Performance
- [ ] Check latency
  - [ ] Decision Center adds < 100ms to recovery path
  - [ ] Audit logging is async
  - [ ] No blocking operations

- [ ] Check resource usage
  - [ ] CPU usage acceptable
  - [ ] Memory usage acceptable
  - [ ] Disk I/O acceptable (for audit logs)

- [ ] Check log files
  - [ ] No error messages
  - [ ] No warnings (except expected)
  - [ ] Audit log format correct

---

## Post-Deployment Verification

### 1. Operational Checks (First 24 Hours)
- [ ] **Hour 1**: Check logs for errors
- [ ] **Hour 4**: Verify decisions are being made
- [ ] **Hour 8**: Verify audit logs accumulating
- [ ] **Hour 12**: Check escalation functionality
- [ ] **Hour 24**: Review statistics and metrics

### 2. Metrics to Monitor
- [ ] **Decision Center Statistics**
  - [ ] Total decisions: `_________________`
  - [ ] Approval rate: `_________________`%
  - [ ] Rejection rate: `_________________`%
  - [ ] Escalation rate: `_________________`%
  - [ ] Automation rate: `_________________`%

- [ ] **Auto-Recovery Statistics**
  - [ ] Total recoveries: `_________________`
  - [ ] Success rate: `_________________`%
  - [ ] Blocked recoveries: `_________________`

- [ ] **Resource Optimizer Statistics**
  - [ ] Cycles completed: `_________________`
  - [ ] Optimizations applied: `_________________`
  - [ ] Optimizations blocked: `_________________`

### 3. Audit Trail Verification
- [ ] Audit logs are being created daily
- [ ] Log entries contain all required fields
- [ ] Logs are queryable for compliance
- [ ] Log retention policy defined

### 4. Policy Verification
- [ ] Policies are being enforced correctly
- [ ] Critical services have correct policies
- [ ] Escalation thresholds are appropriate
- [ ] Approval workflows functioning

---

## Rollback Plan

### If Issues Detected:
1. **Stop Infrastructure Coordinator**
   ```bash
   # Stop coordinator process
   ```

2. **Restore Backup**
   ```bash
   # Restore backed up files
   cp -r backup_location/* /Users/MD/AI-Platform-ISO/infrastructure/
   ```

3. **Restart with Governance Disabled**
   ```python
   coordinator = InfrastructureCoordinator(
       event_bus_backend='redis',
       enable_governance=False  # Disable governance
   )
   ```

4. **Verify System Operational**
   - [ ] Health Monitor running
   - [ ] Auto-Recovery running
   - [ ] Resource Optimizer running
   - [ ] No errors in logs

5. **Document Rollback Reason**
   - Issue: `_________________`
   - Timestamp: `_________________`
   - Action taken: `_________________`

---

## Production Deployment

### Pre-Production Checklist
- [ ] All staging tests passed
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Operations team trained
- [ ] Rollback plan tested
- [ ] Monitoring alerts configured

### Production Deployment Steps
- [ ] Schedule maintenance window
  - [ ] Date/Time: `_________________`
  - [ ] Duration: `_________________`
  - [ ] Stakeholders notified

- [ ] Deploy to production
  - [ ] Follow deployment steps above
  - [ ] Double-check configuration
  - [ ] Verify policy file

- [ ] Monitor closely
  - [ ] First hour: Every 5 minutes
  - [ ] First 24 hours: Every hour
  - [ ] First week: Daily checks

### Post-Production Verification
- [ ] All services healthy
- [ ] Decision Center making decisions
- [ ] Audit logs accumulating
- [ ] No performance degradation
- [ ] Metrics within expected ranges

---

## Success Criteria

### Phase 1.1 is considered successfully deployed when:
1. ✅ **Integration Complete**
   - Auto-Recovery consults Decision Center before all recovery actions
   - Resource Optimizer consults Decision Center before optimizations
   - Infrastructure Coordinator starts with governance enabled

2. ✅ **Functionality Verified**
   - Decisions are made according to policies
   - Escalations created when appropriate
   - Approvals workflow functional
   - Audit logs complete and queryable

3. ✅ **Performance Acceptable**
   - < 100ms latency added to decision path
   - No resource exhaustion
   - System stability maintained

4. ✅ **Compliance Requirements Met**
   - All decisions audited (ISO 22301 requirement)
   - Audit logs immutable and timestamped
   - Audit logs retained per policy
   - Escalation chain documented

5. ✅ **Operational Readiness**
   - Operations team trained
   - Monitoring dashboards updated
   - Alerts configured
   - Runbooks updated

---

## Sign-Off

### Development Team
- [ ] Code changes reviewed and approved
  - Reviewed by: `_________________`
  - Date: `_________________`

### QA Team
- [ ] All tests passed
  - Tested by: `_________________`
  - Date: `_________________`

### Operations Team
- [ ] Deployment successful
  - Deployed by: `_________________`
  - Date: `_________________`

### Security Team
- [ ] Security review completed
  - Reviewed by: `_________________`
  - Date: `_________________`

### Project Manager
- [ ] Phase 1.1 deployment approved
  - Approved by: `_________________`
  - Date: `_________________`

---

## Notes and Issues

### Issues Encountered:
```
(Document any issues found during deployment)

Issue 1:
  Description: _________________
  Severity: _________________
  Resolution: _________________
  Resolved by: _________________
  Date: _________________

Issue 2:
  Description: _________________
  Severity: _________________
  Resolution: _________________
  Resolved by: _________________
  Date: _________________
```

### Lessons Learned:
```
(Document lessons learned for future deployments)

1. _________________
2. _________________
3. _________________
```

---

## Appendix

### A. Key Files Modified
```
/infrastructure/eventbus/coordination/auto_recovery.py
/infrastructure/eventbus/coordination/resource_optimizer.py
/infrastructure/eventbus/coordination/infrastructure_coordinator.py
```

### B. Key Files Added
```
/infrastructure/decision-center/__init__.py
/infrastructure/decision-center/decision_center.py
/infrastructure/decision-center/policy_engine.py
/infrastructure/decision-center/audit_logger.py
/infrastructure/decision-center/decision_models.py
/infrastructure/decision-center/policy_models.py
/infrastructure/decision-center/policies.yaml
/tests/phase1_1/test_integration.py
```

### C. Configuration Files
```
/infrastructure/decision-center/policies.yaml - Main policy configuration
```

### D. Important Directories
```
/infrastructure/decision-center/audit_logs/ - Audit log storage (created automatically)
```

### E. Quick Reference Commands

**Start with governance:**
```python
from infrastructure.eventbus.coordination import InfrastructureCoordinator
coordinator = InfrastructureCoordinator(enable_governance=True)
await coordinator.start()
```

**Start without governance (fallback):**
```python
coordinator = InfrastructureCoordinator(enable_governance=False)
await coordinator.start()
```

**Check Decision Center stats:**
```python
stats = await coordinator.decision_center.get_stats()
print(stats)
```

**Run integration tests:**
```bash
cd /Users/MD/AI-Platform-ISO
python tests/phase1_1/test_integration.py
```

**Check audit logs:**
```bash
tail -f /Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/audit_$(date +%Y-%m-%d).jsonl
```

---

**Deployment Status:** ☐ Not Started | ☐ In Progress | ☐ Complete
**Deployment Environment:** ☐ Development | ☐ Staging | ☐ Production
**Deployment Result:** ☐ Success | ☐ Partial Success | ☐ Failed | ☐ Rolled Back
