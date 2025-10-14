# BCM Platform Workflows

## Overview

This document describes the key workflows across BCM Platform services, showing how they integrate to provide end-to-end ISO 22301:2019 compliance.

---

## 1. BIA → Strategy → Plan Workflow

### Overview
Complete business continuity lifecycle from impact analysis to executable plans.

### Sequence Diagram

```
User          BIA Service    EventBus       Planning        Plans Service
 |                |             |           Service              |
 |--Create BIA--->|             |              |                |
 |                |--Process--->|              |                |
 |<--BIA Created--|             |              |                |
 |                |             |              |                |
 |--Complete BIA->|             |              |                |
 |                |--Validate-->|              |                |
 |                |             |              |                |
 |                |--Publish Event------------>|                |
 |                |    "bia.analysis.completed"|                |
 |                |             |              |                |
 |                |             |    <--Listen Event             |
 |                |             |              |                |
 |--Create Strategy------------>|              |                |
 |                |             |<--Strategy-->|                |
 |<--Strategy Created-----------|              |                |
 |                |             |              |                |
 |--Approve Strategy----------->|              |                |
 |                |             |--Validate-->|                |
 |                |             |              |                |
 |                |             |--Publish Event--------------->|
 |                |       "planning.strategy.approved"         |
 |                |             |              |                |
 |                |             |              |    <--Listen Event
 |                |             |              |                |
 |--Create Plan-------------------------------------------------|
 |                |             |              |    <--Plan---->|
 |<--Plan Created----------------------------------------------|
```

### Steps

#### Step 1: Business Impact Analysis (Port 8012)
**ISO 22301 Clause 8.2.2**

```bash
# Create BIA Process
POST /api/bia/processes
{
  "name": "Payment Processing",
  "criticality": "CRITICAL",
  "rto_hours": 2,
  "rpo_hours": 1,
  "mtpd_hours": 4,
  "financial_impact": {...},
  "dependencies": [...]
}

# Complete BIA
POST /api/bia/processes/1/complete
→ Triggers event: "bia.analysis.completed"
```

#### Step 2: Strategy Development (Port 8011)
**ISO 22301 Clause 8.3**

Planning Service listens for `bia.analysis.completed` event.

```bash
# Create Strategy based on BIA results
POST /api/strategies
{
  "name": "Payment System Recovery",
  "strategy_type": "FAST_RECOVERY",
  "target_rto_hours": 2,
  "estimated_cost": 500000
}

# Cost-Benefit Analysis
POST /api/strategies/{id}/cost-benefit
{
  "analysis_period_years": 3,
  "discount_rate": 0.08,
  ...
}
→ Returns NPV, ROI, Payback Period

# Approve Strategy
POST /api/strategies/{id}/approve
→ Triggers event: "planning.strategy.approved"
```

#### Step 3: Plan Creation (Port 8023)
**ISO 22301 Clause 8.4**

Plans Service listens for `planning.strategy.approved` event.

```bash
# Create BC Plan
POST /api/plans/plans
{
  "name": "Payment System Recovery Plan",
  "plan_type": "IT_RECOVERY",
  "strategy_id": "...",
  ...
}

# Add Procedures with Dependencies
POST /api/plans/plans/1/procedures
{
  "title": "Restore Database",
  "dependencies": [1, 2],  # Must complete proc 1 & 2 first
  ...
}

# Approve and Activate Plan
POST /api/plans/plans/1/approve
POST /api/plans/plans/1/activate
```

### Integration Points

| Event | Publisher | Subscriber | Action |
|-------|-----------|------------|--------|
| `bia.analysis.completed` | BIA Service | Planning Service | Suggest strategy creation |
| `planning.strategy.approved` | Planning Service | Plans Service | Enable plan creation |
| `plans.plan.activated` | Plans Service | All Services | Plan ready for use |

---

## 2. Audit → Gap → NC → CAPA → Improvement Workflow

### Overview
Complete compliance improvement cycle from audit to verified corrective actions.

### Sequence Diagram

```
Auditor    Compliance Service    NC Manager    CAPA Owner
  |               |                   |              |
  |--Create Audit->|                   |              |
  |               |--Audit Created---->|              |
  |               |                   |              |
  |--Add Finding-->|                   |              |
  |               |--Finding Logged-->|              |
  |               |                   |              |
  |--Create NC------------------->|   |              |
  |               |<--NC Created-------|              |
  |               |                   |              |
  |               |        State: IDENTIFIED         |
  |               |                   |              |
  |--Start RCA------------------>|    |              |
  |               |<--RCA Template-----|              |
  |               |                   |              |
  |               |        State: RCA_IN_PROGRESS    |
  |               |                   |              |
  |--Complete RCA--------------->|    |              |
  |               |<--Root Causes------|              |
  |               |                   |              |
  |               |    State: CORRECTIVE_ACTION      |
  |               |                   |              |
  |--Create CAPA--------------------------------->|   |
  |               |<--CAPA Plan--------------------|   |
  |               |                   |              |
  |--Implement Actions-------------------------->|   |
  |               |<--Implementation Complete-----|   |
  |               |                   |              |
  |               |        State: VERIFICATION       |
  |               |                   |              |
  |--Verify Effectiveness----------->|              |
  |               |<--Verified---------|              |
  |               |                   |              |
  |               |           State: CLOSED          |
```

### Steps

#### Step 1: Internal Audit (ISO 9.2)

```bash
# Create Internal Audit
POST /api/audit/audits
{
  "title": "Q1 2024 ISO 22301 Audit",
  "audit_type": "INTERNAL",
  "scope": "Clauses 8.4, 8.5",
  "audit_date": "2024-01-15",
  "lead_auditor": "sarah.jones@company.com"
}

# Add Findings
POST /api/audit/audits/{id}/findings
{
  "finding_number": "F-2024-001",
  "finding_type": "MAJOR",
  "clause_reference": "8.4.4",
  "description": "BC plan lacks procedure dependencies"
}
```

#### Step 2: Nonconformity Creation (ISO 10.1)

```bash
# Create NC from Finding
POST /api/nonconformities
{
  "nc_number": "NC-2024-001",
  "nc_type": "MAJOR",
  "source": "AUDIT",
  "description": "BC plan lacks procedure dependencies",
  "clause_affected": "8.4.4"
}
→ State: IDENTIFIED
```

#### Step 3: Root Cause Analysis

```bash
# Start RCA (5 Whys Method)
POST /api/nonconformities/{id}/rca/start?rca_method=5_whys&rca_lead=john.doe
→ Returns blank 5 Whys template
→ State: RCA_IN_PROGRESS

# Complete RCA
POST /api/nonconformities/{id}/rca/complete
{
  "completed_template": {
    "problem_statement": "BC plan lacks dependencies",
    "why_1": "No template requirement",
    "why_2": "Template design gap",
    "why_3": "Original implementation oversight",
    "why_4": "Training didn't emphasize Clause 8.4.4",
    "why_5": "Incomplete ISO training program",
    "root_cause": "Inadequate template and training"
  }
}
→ Extracts root causes
→ State: CORRECTIVE_ACTION
```

#### Step 4: Corrective Actions (CAPA)

```bash
# Create Corrective Actions
POST /api/nonconformities/{id}/corrective-actions
{
  "actions": [
    {
      "description": "Update BC plan template",
      "responsible": "bcm-team@company.com",
      "target_date": "2024-02-15"
    },
    {
      "description": "Provide supplemental training",
      "responsible": "training@company.com",
      "target_date": "2024-02-20"
    }
  ]
}

# Implement Actions
POST /api/corrective-actions/{id}/complete
→ State: VERIFICATION
```

#### Step 5: Verification & Closure

```bash
# Verify Effectiveness
POST /api/nonconformities/{id}/verify
{
  "verification_notes": "Template updated, training completed, all BC plans reviewed",
  "verified_by": "audit-manager@company.com",
  "is_effective": true
}
→ State: CLOSED

# Create Improvement Initiative (ISO 10.2)
POST /api/improvements
{
  "title": "Enhanced BC Plan Template",
  "description": "Improved template now includes dependency mapping",
  "benefits": "Reduced plan gaps, better ISO compliance"
}
```

### State Machine

```
IDENTIFIED → RCA_IN_PROGRESS → CORRECTIVE_ACTION → VERIFICATION → CLOSED
                                                  ↓
                                              REOPENED (if ineffective)
```

**Valid Transitions:**
- IDENTIFIED → RCA_IN_PROGRESS (start RCA)
- RCA_IN_PROGRESS → CORRECTIVE_ACTION (complete RCA)
- CORRECTIVE_ACTION → VERIFICATION (actions implemented)
- VERIFICATION → CLOSED (verified effective)
- VERIFICATION → REOPENED (verified ineffective)
- REOPENED → CORRECTIVE_ACTION (new actions needed)

---

## 3. Plan Activation Workflow

### Overview
Real incident response using activated BC plan.

### Sequence Diagram

```
Incident      Plans Service    Response Team    EventBus
Manager
  |                |                  |             |
  |--Activate Plan->|                  |             |
  |                |--Validate-------->|             |
  |                |                  |             |
  |                |--Publish Event--------------->|
  |                | "plans.activation.started"    |
  |                |                  |             |
  |<--Activation ID-|                  |             |
  |                |                  |             |
  |                |--Notify Team----------------->|
  |                |                  |             |
  |                |          <--Acknowledge--------|
  |                |                  |             |
  |--Execute Procedures-------------->|             |
  |                |          <--Progress Updates---|
  |                |                  |             |
  |--Log Progress->|                  |             |
  |                |--Update Status-->|             |
  |                |                  |             |
  |--Complete----->|                  |             |
  |                |--Publish Event--------------->|
  |                |  "plans.activation.completed" |
  |                |                  |             |
  |--Create Review->|                  |             |
  |<--Lessons Learned|                |             |
```

### Steps

#### Step 1: Activate Plan

```bash
# Activate for Real Incident
POST /api/plans/plans/{id}/activate-real
{
  "activation_type": "REAL_INCIDENT",
  "incident_description": "Payment gateway outage",
  "severity": "CRITICAL",
  "incident_start_time": "2024-01-15T10:30:00Z"
}
→ Returns activation_id
→ Triggers: "plans.activation.started" event
→ Notifies: Contact lists
```

#### Step 2: Execute Procedures

```bash
# Get Procedures with Dependencies
GET /api/plans/plans/{id}/procedures
→ Returns procedures in dependency order

# Log Procedure Execution
POST /api/plans/activations/{activation_id}/procedure-log
{
  "procedure_id": 1,
  "status": "COMPLETED",
  "actual_duration_minutes": 35,
  "notes": "Database restored from backup"
}
```

#### Step 3: Track Progress

```bash
# Update Activation Status
PATCH /api/plans/activations/{activation_id}
{
  "status": "IN_PROGRESS",
  "progress_percentage": 60,
  "notes": "Database restored, application restart in progress"
}
```

#### Step 4: Complete & Review

```bash
# Complete Activation
POST /api/plans/activations/{activation_id}/complete
{
  "incident_end_time": "2024-01-15T12:15:00Z",
  "outcome": "SUCCESSFUL",
  "notes": "All systems restored within RTO"
}
→ Triggers: "plans.activation.completed" event

# Create Post-Incident Review
POST /api/plans/plans/{id}/reviews
{
  "review_type": "POST_INCIDENT",
  "activation_id": "...",
  "findings": ["RTO met", "Communication protocol worked well"],
  "improvements": ["Update contact list", "Add automation for Step 3"],
  "plan_updates_required": true
}
```

---

## 4. Testing & Exercise Workflow

### Overview
Scheduled BC plan testing and exercise execution.

### Steps

#### Step 1: Schedule Exercise

```bash
# Create Exercise Schedule
POST /api/plans/exercises
{
  "plan_id": 1,
  "exercise_type": "TABLETOP",
  "scheduled_date": "2024-02-15T09:00:00Z",
  "participants": ["team@company.com"],
  "objectives": ["Test RTO", "Validate procedures"]
}
```

#### Step 2: Execute Exercise

```bash
# Start Exercise
POST /api/plans/exercises/{id}/start
{
  "scenario": "Payment gateway failure simulation"
}

# Log Exercise Activities
POST /api/plans/exercises/{id}/activities
{
  "activity": "Executed Step 3 - Database Restore",
  "outcome": "PASS",
  "duration_minutes": 42,
  "observations": "Took longer than estimated 30 minutes"
}
```

#### Step 3: Complete & Debrief

```bash
# Complete Exercise
POST /api/plans/exercises/{id}/complete
{
  "overall_result": "PARTIAL_SUCCESS",
  "rto_achieved": false,  # Took 2.5hr instead of 2hr
  "lessons_learned": [
    "Database restore slower than expected",
    "Communication protocol needs improvement"
  ],
  "improvement_actions": [
    "Upgrade backup storage for faster restore",
    "Revise communication templates"
  ]
}
→ Triggers: "exercise.completed" event
→ May create: Improvement initiatives
→ May create: Plan update tasks
```

---

## 5. Cross-Service Integration Patterns

### Event-Driven Communication

**Events Published:**

| Service | Event | Payload | Purpose |
|---------|-------|---------|---------|
| BIA | `bia.analysis.completed` | `{process_id, rto_hours, criticality}` | Trigger strategy creation |
| Planning | `planning.strategy.approved` | `{strategy_id, target_rto, cost}` | Enable plan creation |
| Plans | `plans.plan.activated` | `{plan_id, activation_id}` | Start incident response |
| Plans | `plans.activation.completed` | `{activation_id, outcome, duration}` | Post-incident review |
| Compliance | `compliance.audit.completed` | `{audit_id, findings_count}` | Trigger gap analysis |
| Compliance | `compliance.nc.closed` | `{nc_id, root_causes, actions}` | Lessons learned |

### Synchronous API Calls

**When to Use:**
- Real-time data validation
- Transaction coordination
- Immediate response required

**Example:**
```bash
# Planning Service validates BIA exists before creating strategy
GET http://bia-service:8012/api/bia/processes/{id}
→ If exists and completed: Allow strategy creation
→ If not exists/incomplete: Return 400 error
```

---

## 6. Best Practices

### Workflow Design

1. **Idempotency**: All POST/PUT operations should be idempotent
2. **Error Handling**: Include retry logic for external service calls
3. **State Validation**: Validate state transitions before allowing actions
4. **Audit Trail**: Log all state changes with timestamp and actor

### Event-Driven Architecture

1. **Event Schema**: Use consistent event structure
2. **Versioning**: Version events for backward compatibility
3. **Dead Letter Queue**: Handle failed event processing
4. **Event Replay**: Support event replay for debugging

### Performance

1. **Async Operations**: Use async for long-running tasks
2. **Pagination**: Paginate large result sets
3. **Caching**: Cache frequently accessed data
4. **Bulk Operations**: Support bulk updates where possible

---

## Next Steps

- [API Reference](api_reference.md) - Detailed API documentation
- [Integration Guide](integration_guide.md) - Integration patterns
- [Authentication](authentication.md) - Auth and RBAC
- [Error Handling](error_handling.md) - Error codes and handling
