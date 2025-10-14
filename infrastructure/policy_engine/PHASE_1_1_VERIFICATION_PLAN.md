# Phase 1.1 Governance Layer - Verification Testing Plan

**Date:** 2025-10-14
**Status:** Ready for Execution
**Version:** 1.0.0
**Duration:** 1-2 дня

---

## 🎯 Цели Verification Testing

### Основная Цель
Подтвердить, что Phase 1.1 Governance Layer (Decision Center, Escalation Manager, Policy Engine, Audit Logger, Notification Service) работает end-to-end и готова к production.

### Специфические Цели

1. **Functional Verification**: Каждый компонент работает согласно спецификации
2. **Integration Verification**: Компоненты взаимодействуют корректно
3. **Scenario Verification**: Реальные healthcare BCM сценарии выполняются успешно
4. **Standards Compliance**: Соответствие ISO 22301 и WHO требованиям

---

## 📚 Связь с Библиотекой Знаний

### Knowledge Base Integration

Все тестовые сценарии основаны на:

1. **ISO 22301:2019 Business Flows**
   - Источник: `/data/knowledge/standards/iso/iso-22301/ISO_22301_FLOWS_INDEX.md`
   - 58 задокументированных flows
   - 7 критических flows для сертификации

2. **WHO Healthcare BCM Flows**
   - Источник: `/data/knowledge/standards/who/WHO_HEALTHCARE_BCM_FLOWS.md`
   - 10+ healthcare-specific flows
   - Healthcare emergency scenarios

3. **Case Library (347+ cases)**
   - Источник: `/intelligent-core/collective/services/case_library.py`
   - Real-world BCM cases
   - Anonymized approaches and patterns

### Scenario Selection Criteria

**Базовые сценарии (ISO 22301):**
- Flow 8.6: Incident Activation and Response
- Flow 8.2.3: Operational Risk Assessment
- Flow 9.1.1: Performance Monitoring

**Доменные сценарии (WHO Healthcare):**
- Flow 3.3: Health Workforce continuity
- Flow 5: Pandemic/Epidemic Response
- Flow 9: Healthcare Supply Chain Resilience

**Кейсы из практики (Case Library):**
- Problem Type: "service_continuity_under_staff_shortage"
- Problem Type: "critical_supply_disruption"
- Problem Type: "infrastructure_failure_recovery"

---

## 🧪 Test Scenarios

### Tier 1: Component Functional Tests

#### Test 1.1: Policy Engine Loading
**Source:** Core infrastructure functionality

**Objective:** Verify Policy Engine loads policies.yaml correctly

**Steps:**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus/coordination

# Start infrastructure coordinator
python infrastructure_coordinator.py

# Expected output:
# ✅ Policy Engine initialized from policies.yaml
# ✅ Loaded policies for 20+ services
# ✅ Policy validation passed
```

**Success Criteria:**
- ✅ No errors during initialization
- ✅ All 20+ service policies loaded
- ✅ Policy validation passes
- ✅ Policy Engine singleton accessible

**Evidence:**
- Policy Engine initialization logs
- Loaded policies count
- Validation report

---

#### Test 1.2: Decision Center Initialization
**Source:** Core infrastructure functionality

**Objective:** Verify Decision Center connects to Policy Engine

**Steps:**
```python
from infrastructure.policy_engine import (
    get_policy_engine,
    InfrastructureDecisionCenter
)

# Get Policy Engine
engine = get_policy_engine()
print(f"Policy Engine loaded at: {engine.loaded_at}")

# Get policy for database
db_policy = engine.get_recovery_policy('database')
print(f"Database RTO: {db_policy['rto']}s")
print(f"Max attempts: {db_policy['max_auto_attempts']}")

# Create Decision Center
decision_center = InfrastructureDecisionCenter()
print("Decision Center ready!")
```

**Success Criteria:**
- ✅ Policy Engine returns valid policies
- ✅ Decision Center initializes without errors
- ✅ Can query policies for all services

**Evidence:**
- Policy query results
- Decision Center initialization log

---

#### Test 1.3: Escalation Manager Setup
**Source:** Core infrastructure functionality

**Objective:** Verify Escalation Manager initializes with notification service

**Steps:**
```python
from infrastructure.policy_engine import (
    EscalationManager,
    NotificationService,
    NotificationConfig
)

# Create Notification Service
notification_config = NotificationConfig(
    slack_webhook="https://hooks.slack.com/test",
    smtp_host="localhost",
    smtp_port=587
)
notification_service = NotificationService(notification_config)

# Create Escalation Manager
escalation_manager = EscalationManager(
    notification_service=notification_service
)

print("Escalation Manager ready!")
print(f"Levels configured: {len(escalation_manager.escalation_levels)}")
```

**Success Criteria:**
- ✅ Notification Service initializes
- ✅ Escalation Manager initializes
- ✅ 4 escalation levels configured
- ✅ Notification channels configured

**Evidence:**
- Escalation levels configuration
- Notification channels list

---

### Tier 2: Integration Tests

#### Test 2.1: Auto-Recovery with Decision Center
**Source:** Infrastructure integration

**Objective:** Verify Auto-Recovery consults Decision Center before recovery action

**Steps:**
```python
# Simulate database failure
service_name = "database"
failure_count = 1

# Auto-Recovery should:
# 1. Consult Decision Center
# 2. Get policy for database
# 3. Check max_auto_attempts (should be 2)
# 4. Approve recovery action
# 5. Attempt restart
```

**Success Criteria:**
- ✅ Decision Center consulted
- ✅ Policy retrieved (RTO: 120s, max_attempts: 2)
- ✅ Recovery decision made
- ✅ Audit log recorded

**Evidence:**
- Decision Center decision log
- Policy Engine query log
- Audit trail entry

---

#### Test 2.2: Escalation Flow (End-to-End)
**Source:** ISO 22301 Flow 8.6 (Incident Activation and Response)

**Objective:** Verify full escalation from failure to notification

**Scenario:** Database fails repeatedly, exceeds max attempts

**Steps:**
1. **Failure 1**: Auto-recovery attempts restart
2. **Failure 2**: Auto-recovery attempts restart again (max_attempts=2 reached)
3. **Escalation Level 1**: Escalation Manager escalates to Ops Team
4. **Notification**: Slack + Email sent to ops team
5. **Timeout (15 min)**: No response
6. **Escalation Level 2**: Escalate to Senior Ops, PagerDuty alert

**Success Criteria:**
- ✅ Escalation triggered after max_attempts
- ✅ Level 1 notification sent (Slack + Email)
- ✅ Level 2 escalation after timeout
- ✅ All decisions logged in audit trail

**Evidence:**
- Escalation Manager log
- Notification delivery confirmations
- Audit log with full escalation trail

---

### Tier 3: Healthcare BCM Scenarios (WHO-Based)

#### Test 3.1: Pandemic Response - Staff Shortage Scenario
**Source:** WHO Flow 5 (Pandemic/Epidemic Response Continuity) + Flow 3.3 (Health Workforce)

**Scenario:** COVID-19 pandemic, 30% staff absenteeism

**Healthcare Context:**
- **Problem**: Infectious disease outbreak → staff illness/fear → service disruption
- **Critical Services**: Emergency care, ICU, Maternity, HIV ART, TB treatment
- **Policy Requirement**: Maintain essential services, activate surge capacity

**Test Steps:**

1. **Trigger Event**: Staff absenteeism exceeds 25% (policy threshold)

2. **Decision Center Actions:**
   ```python
   # Policy check for workforce shortage
   policy = engine.get_workforce_policy('healthcare_facility')

   # Should return:
   {
       "absenteeism_threshold": 0.25,
       "essential_services": ["emergency", "icu", "maternity", "hiv_art"],
       "surge_capacity_activation": "immediate",
       "service_modification_allowed": true,
       "escalation_required": true
   }
   ```

3. **Expected Decisions:**
   - ✅ Activate surge capacity roster
   - ✅ Modify non-essential services (defer elective surgeries)
   - ✅ Maintain critical services (ART, emergency, maternity)
   - ✅ Escalate to management for additional staff

4. **Notification Flow:**
   - Level 1: Ops team (activate surge roster)
   - Level 2: Senior management (approve service modifications)
   - Level 3: Health authority notification (if >50% absenteeism)

**Success Criteria:**
- ✅ Policy correctly identifies essential services
- ✅ Decision Center approves service modifications
- ✅ Escalation flow triggers correctly
- ✅ All decisions logged with healthcare context

**Evidence:**
- Decision Center decision log with healthcare rationale
- Service modification approval trail
- Escalation notifications sent
- Audit log with ISO 22301 compliance markers

**Link to Case Library:**
```python
# Query similar cases
cases = await case_library.find_cases(
    problem_type="service_continuity_under_staff_shortage",
    min_success_rate=0.8
)

# Should return cases from healthcare organizations
# that successfully maintained services during pandemics
```

---

#### Test 3.2: Supply Chain Disruption - Critical Medication Shortage
**Source:** WHO Flow 9 (Healthcare Supply Chain Resilience)

**Scenario:** Antiretroviral (ARV) drug supply disruption

**Healthcare Context:**
- **Problem**: War/conflict disrupts ARV supply chain
- **Critical Impact**: HIV patients, treatment interruption = death/resistance
- **WHO Guidance**: 3-6 month buffer stocks, multi-month dispensing (MMD), alternative suppliers

**Test Steps:**

1. **Trigger Event**: ARV stock level drops below 30-day supply

2. **Policy Check:**
   ```python
   policy = engine.get_supply_chain_policy('critical_medications')

   # Should return:
   {
       "medication_type": "life_sustaining",
       "minimum_stock_days": 90,
       "critical_threshold_days": 30,
       "emergency_procurement_required": true,
       "alternative_delivery_models": ["mmд", "community_distribution"],
       "escalation_immediate": true
   }
   ```

3. **Expected Decisions:**
   - ✅ Activate emergency procurement
   - ✅ Switch to Multi-Month Dispensing (3-month supplies to stable patients)
   - ✅ Activate community distribution points
   - ✅ Escalate to Global Fund for emergency supplies

4. **Notification Flow:**
   - Level 1: Pharmacy team (implement MMD immediately)
   - Level 2: Facility management (approve emergency procurement)
   - Level 3: National health authority + Global Fund (emergency request)

**Success Criteria:**
- ✅ Critical threshold detection
- ✅ Emergency procurement decision
- ✅ Alternative delivery model activation
- ✅ Multi-level escalation to external partners

**Evidence:**
- Supply chain monitoring alerts
- Emergency procurement approval
- MMD activation decision
- External escalation notifications (Global Fund, WHO)

**Link to Case Library:**
```python
cases = await case_library.find_cases(
    problem_type="critical_supply_disruption",
    min_success_rate=0.8
)

# Cases should show:
# - Emergency procurement strategies
# - Alternative supplier activation
# - MMD implementation success stories
# - Cross-border supply coordination
```

---

#### Test 3.3: Infrastructure Failure - Database Outage During Patient Surge
**Source:** ISO 22301 Flow 8.2.3 (Operational Risk Assessment) + WHO Service Continuity

**Scenario:** Database server failure during emergency surge (earthquake response)

**Healthcare Context:**
- **Problem**: Mass casualty event → patient surge + infrastructure failure
- **Critical Impact**: Patient records inaccessible, treatment delays
- **BCM Requirement**: Manual backup systems, paper-based procedures

**Test Steps:**

1. **Trigger Event**: Database health check fails, concurrent patient surge

2. **Policy Check:**
   ```python
   policy = engine.get_recovery_policy('database')

   # Should return:
   {
       "priority": 1,  # Critical
       "rto_seconds": 120,
       "max_auto_attempts": 2,
       "recovery_strategy": "circuit_breaker",
       "manual_fallback_required": true,
       "service_continuity_procedures": ["paper_based_triage", "verbal_handoffs"]
   }
   ```

3. **Expected Decisions:**
   - ✅ Attempt auto-recovery (max 2 attempts)
   - ✅ Activate manual/paper-based procedures immediately
   - ✅ Escalate to infrastructure team
   - ✅ Notify clinical staff of manual procedures

4. **Escalation Flow:**
   - Level 1: Infrastructure team (database recovery)
   - Level 2: Clinical leadership (activate manual procedures)
   - Level 3: Incident command (if RTO exceeded)

**Success Criteria:**
- ✅ Auto-recovery attempts (2 max)
- ✅ Manual fallback activation decision
- ✅ Clinical staff notification
- ✅ RTO monitoring and escalation

**Evidence:**
- Recovery attempts log
- Manual fallback activation timestamp
- Clinical staff notification confirmations
- RTO compliance tracking

**Link to Case Library:**
```python
cases = await case_library.find_cases(
    problem_type="infrastructure_failure_recovery",
    min_success_rate=0.8
)

# Cases should show:
# - Manual fallback effectiveness
# - Staff training on paper procedures
# - RTO achievement strategies
# - Patient safety during outage
```

---

### Tier 4: Audit & Compliance Tests

#### Test 4.1: ISO 22301 Audit Trail Verification
**Source:** ISO 22301 Flow 9.2.2 (Internal Audit Execution)

**Objective:** Verify all governance decisions produce compliant audit trails

**Test Steps:**
1. Execute Test 3.1 (Pandemic scenario)
2. Query audit logs for that scenario
3. Verify ISO 22301 compliance elements

**Required Audit Elements (ISO 22301:2019, Clause 7.5.2):**
- ✅ Timestamp (when decision made)
- ✅ Decision type (recovery, escalation, approval)
- ✅ Service/system affected
- ✅ Decision made
- ✅ Justification (which policy, clause, rationale)
- ✅ Outcome (success/failure)
- ✅ Decision maker (user_id or system)
- ✅ Policy version used

**Success Criteria:**
- ✅ All required elements present
- ✅ Audit trail is chronological
- ✅ Tamper-proof (append-only)
- ✅ 90-day retention policy configured

**Evidence:**
- Sample audit log entries
- Audit log integrity verification
- Retention policy configuration

---

#### Test 4.2: Notification Delivery Verification
**Source:** ISO 22301 Flow 8.4.3 (Warning and Communication Procedures)

**Objective:** Verify multi-channel notifications are delivered

**Test Channels:**
- Slack webhook
- Email (SMTP)
- PagerDuty API
- (Optional) TheHive incident creation

**Test Steps:**
1. Configure test notification endpoints
2. Trigger escalation (Test 2.2)
3. Verify delivery on each channel

**Success Criteria:**
- ✅ Slack message delivered (webhook 200 OK)
- ✅ Email sent (SMTP success)
- ✅ PagerDuty incident created
- ✅ Retry logic works (simulate failure)

**Evidence:**
- Notification delivery logs
- Channel-specific confirmations
- Retry attempt logs

---

### Tier 5: Performance & Edge Cases

#### Test 5.1: Policy Hot-Reload
**Source:** Operational requirement

**Objective:** Verify policies can be updated without restart

**Steps:**
1. Start Infrastructure Coordinator
2. Modify policies.yaml (change database RTO from 120s to 180s)
3. Trigger policy reload
4. Verify new policy active

**Success Criteria:**
- ✅ Policy reload without service restart
- ✅ New policy values active
- ✅ No disruption to running operations

---

#### Test 5.2: Concurrent Escalations
**Source:** Real-world scenario (multiple simultaneous failures)

**Objective:** Handle multiple service failures concurrently

**Scenario:** Database + Redis + EventBus all fail simultaneously

**Expected Behavior:**
- ✅ Each service escalates independently
- ✅ Escalation Manager handles concurrent flows
- ✅ Notifications are batched appropriately
- ✅ No race conditions or deadlocks

---

## 📋 Test Execution Plan

### Day 1: Component & Integration Tests

**Morning (9:00-12:00):**
- ✅ Test 1.1: Policy Engine Loading
- ✅ Test 1.2: Decision Center Initialization
- ✅ Test 1.3: Escalation Manager Setup
- ✅ Test 2.1: Auto-Recovery with Decision Center

**Afternoon (13:00-17:00):**
- ✅ Test 2.2: Escalation Flow (End-to-End)
- ✅ Test 4.1: Audit Trail Verification
- ✅ Test 4.2: Notification Delivery

**Evening (17:00-18:00):**
- Document Day 1 results
- Identify any issues
- Prepare Day 2 scenarios

---

### Day 2: Healthcare BCM Scenarios

**Morning (9:00-12:00):**
- ✅ Test 3.1: Pandemic Response - Staff Shortage
  - Execute scenario
  - Query Case Library for similar cases
  - Verify decisions match WHO guidance
  - Document healthcare-specific compliance

**Afternoon (13:00-15:00):**
- ✅ Test 3.2: Supply Chain Disruption - ARV Shortage
  - Execute scenario
  - Query Case Library for supply chain cases
  - Verify WHO BCM Flow 9 compliance
  - Document Global Fund escalation

**Late Afternoon (15:00-17:00):**
- ✅ Test 3.3: Infrastructure Failure During Surge
  - Execute scenario
  - Verify manual fallback activation
  - Query Case Library for infrastructure cases
  - Document ISO + WHO compliance

**Evening (17:00-18:00):**
- ✅ Test 5.1: Policy Hot-Reload
- ✅ Test 5.2: Concurrent Escalations
- Final documentation and reporting

---

## 📊 Success Metrics

### Coverage Metrics

| Category | Target | Measurement |
|----------|--------|-------------|
| Component Tests | 100% | 3/3 components tested |
| Integration Tests | 100% | 2/2 integration flows tested |
| Healthcare Scenarios | 100% | 3/3 WHO scenarios tested |
| ISO 22301 Compliance | 100% | Audit trail + notifications verified |
| Case Library Integration | 100% | 3/3 scenarios linked to cases |

### Quality Metrics

| Metric | Target | Threshold |
|--------|--------|-----------|
| Test Pass Rate | 100% | >95% acceptable |
| Audit Trail Completeness | 100% | All required ISO fields |
| Notification Delivery | 100% | >98% acceptable |
| RTO Compliance | 100% | Within policy limits |
| Policy Accuracy | 100% | Correct policy applied |

---

## 🔗 Knowledge Base Integration

### Scenario Catalog Creation

**Location:** `/data/knowledge/scenarios/governance/`

**Structure:**
```
governance/
├── README.md (Scenario catalog index)
├── iso-22301/
│   ├── incident_response.md (Flow 8.6)
│   ├── risk_assessment.md (Flow 8.2.3)
│   └── audit_execution.md (Flow 9.2.2)
├── who-healthcare/
│   ├── pandemic_staff_shortage.md (Flow 5 + Flow 3.3)
│   ├── supply_chain_disruption.md (Flow 9)
│   └── infrastructure_failure.md (Custom)
└── case-library-links/
    ├── staff_shortage_cases.md
    ├── supply_disruption_cases.md
    └── infrastructure_failure_cases.md
```

**Each scenario file includes:**
- Scenario description
- Source (ISO flow or WHO flow)
- Healthcare context
- Test steps
- Expected decisions
- Success criteria
- Link to Case Library query
- Real-world examples (anonymized)

---

## 📝 Test Report Template

### Test Execution Report

**Test ID:** Test 3.1 (Pandemic Staff Shortage)
**Date:** 2025-10-14
**Tester:** [Name]
**Status:** ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

**Test Summary:**
- Scenario: COVID-19 pandemic, 30% staff absenteeism
- Source: WHO Flow 5 + Flow 3.3
- Duration: 45 minutes

**Results:**

| Test Step | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Policy check | Essential services identified | ✅ Emergency, ICU, Maternity, HIV ART | ✅ PASS |
| Decision Center | Service modifications approved | ✅ Defer elective surgeries | ✅ PASS |
| Escalation | Management notified | ✅ Level 2 escalation sent | ✅ PASS |
| Audit log | ISO 22301 compliant | ✅ All required fields | ✅ PASS |

**Case Library Query:**
```python
cases = await case_library.find_cases(
    problem_type="service_continuity_under_staff_shortage",
    min_success_rate=0.8
)

# Results: 12 cases found
# Top approach: Surge capacity activation + service prioritization
# Success rate: 91%
```

**Evidence:**
- [Decision Center log screenshot]
- [Escalation notification screenshot]
- [Audit trail excerpt]

**Issues Found:** None

**Recommendations:** None

---

## 🎯 Definition of Done

Phase 1.1 Verification Testing is COMPLETE when:

### Functional Completion
- ✅ All Tier 1 tests pass (3/3)
- ✅ All Tier 2 tests pass (2/2)
- ✅ All Tier 3 tests pass (3/3 healthcare scenarios)
- ✅ All Tier 4 tests pass (2/2 compliance)
- ✅ All Tier 5 tests pass (2/2 performance)

### Compliance Completion
- ✅ ISO 22301 audit trail verified
- ✅ WHO BCM guidance compliance verified
- ✅ All decisions logged correctly
- ✅ Notifications delivered reliably

### Documentation Completion
- ✅ Test execution report created
- ✅ All scenarios documented
- ✅ Case Library links established
- ✅ Knowledge Base updated with scenarios

### Integration Completion
- ✅ Infrastructure Coordinator running with governance
- ✅ All 5 governance components active
- ✅ No critical issues identified
- ✅ Performance acceptable

---

## 🚀 Next Steps After Verification

### If All Tests Pass ✅

1. **Update Documentation:**
   - Mark Phase 1.1 as "Production Ready"
   - Update platform maturity to 75% (confirmed)
   - Document verified scenarios

2. **Create Quick Start Guide:**
   - How to run Infrastructure Coordinator with governance
   - Common scenarios and expected behavior
   - Troubleshooting guide

3. **Prepare for Phase 1.5:**
   - AI Orchestrator integration
   - Workflow Intelligence integration
   - Predictive Intelligence for proactive decisions

### If Issues Found ⚠️

1. **Document Issues:**
   - Issue description
   - Severity (critical/high/medium/low)
   - Steps to reproduce
   - Expected vs actual behavior

2. **Fix Critical Issues:**
   - Address blockers immediately
   - Re-run affected tests
   - Update documentation

3. **Re-Test:**
   - Run full test suite again
   - Verify fixes
   - Update test report

---

## 📚 Appendix: Test Data

### Sample policies.yaml

```yaml
version: "1.1"

infrastructure_policies:
  recovery:
    by_service:
      database:
        priority: 1
        rto_seconds: 120
        max_auto_attempts: 2
        recovery_strategy: "circuit_breaker"
        escalate_after_attempts: 2
        notification_teams: ["ops", "database-admins"]

  workforce:
    absenteeism_threshold: 0.25
    essential_services: ["emergency", "icu", "maternity", "hiv_art"]
    surge_capacity_activation: "immediate"

  supply_chain:
    critical_medications:
      minimum_stock_days: 90
      critical_threshold_days: 30
      emergency_procurement_required: true
      alternative_delivery_models: ["mmd", "community_distribution"]
```

---

**Created:** 2025-10-14
**Author:** AI Platform Integration Team
**Status:** Ready for Execution
**Next Action:** Execute Day 1 tests

---

**🎯 Ready to verify Phase 1.1 Governance Layer with real-world healthcare BCM scenarios!**
