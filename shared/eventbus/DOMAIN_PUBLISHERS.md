# Domain-Specific Event Publishers

Comprehensive guide to using domain-specific event publishers for BCM (Business Continuity Management) events.

## Overview

Domain publishers provide type-safe, domain-specific methods for publishing events across all BCM domains. These publishers ensure consistency, reduce errors, and provide clear APIs for event-driven communication.

## Available Publishers

| Publisher | Domain | Event Count |
|-----------|--------|-------------|
| `BIAEventPublisher` | Business Impact Analysis | 4 events |
| `WorkflowEventPublisher` | Workflow Management | 6 events |
| `RiskEventPublisher` | Risk Management | 4 events |
| `IncidentEventPublisher` | Incident Management | 4 events |
| `ComplianceEventPublisher` | Compliance & Audit | 4 events |
| `CommunityEventPublisher` | Community Intelligence | 4 events |

**Total: 6 publishers, 26 specialized methods**

---

## Installation & Setup

### 1. Initialize EventBus (Application Startup)

```python
from shared.eventbus import init_eventbus

# During FastAPI startup
@app.on_event("startup")
async def startup():
    eventbus = init_eventbus(settings.RABBITMQ_URL)
    await eventbus.connect()
```

### 2. Import Domain Publishers

```python
from shared.eventbus import (
    BIAEventPublisher,
    WorkflowEventPublisher,
    RiskEventPublisher,
    IncidentEventPublisher,
    ComplianceEventPublisher,
    CommunityEventPublisher,
)
```

---

## BIAEventPublisher

**Domain:** Business Impact Analysis

### Event Catalog

| Event Type | Description |
|------------|-------------|
| `bia.started` | BIA process initiated |
| `bia.completed` | BIA process completed with results |
| `bia.validated` | BIA validated by stakeholder |
| `bia.process_analyzed` | Business process impact analyzed |

### Usage Examples

#### Publish BIA Started

```python
from shared.eventbus import BIAEventPublisher

bia_publisher = BIAEventPublisher()

# Basic usage
await bia_publisher.publish_bia_started(
    bia_id=123,
    process_name="Payment Processing System",
    org_id="org-456",
    tenant_id="tenant-789"
)

# With additional data
await bia_publisher.publish_bia_started(
    bia_id=123,
    process_name="Payment Processing System",
    org_id="org-456",
    tenant_id="tenant-789",
    additional_data={
        "department": "Finance",
        "initiated_by": "user-001",
        "due_date": "2025-11-01"
    }
)
```

#### Publish BIA Completed

```python
# Complete BIA with full metrics
await bia_publisher.publish_bia_completed(
    bia_id=123,
    rto=4,  # 4 hours RTO
    rpo=1,  # 1 hour RPO
    criticality="CRITICAL",
    impact_score=9.5,
    tenant_id="tenant-789",
    additional_data={
        "financial_impact": 500000,
        "operational_impact": "SEVERE",
        "dependencies": ["payment-gateway", "database"]
    }
)
```

#### Publish BIA Validated

```python
# Approve BIA
await bia_publisher.publish_bia_validated(
    bia_id=123,
    validator_id="executive-456",
    validation_status="APPROVED",
    comments="All recovery metrics verified and approved",
    tenant_id="tenant-789"
)

# Reject BIA
await bia_publisher.publish_bia_validated(
    bia_id=123,
    validator_id="manager-789",
    validation_status="REJECTED",
    comments="RTO needs to be reduced to 2 hours",
    tenant_id="tenant-789"
)
```

#### Publish Process Analyzed

```python
await bia_publisher.publish_process_analyzed(
    process_id=456,
    impact_data={
        "financial_impact": 50000,
        "operational_impact": "HIGH",
        "reputational_impact": "MEDIUM",
        "regulatory_impact": "LOW"
    },
    dependencies=["payment-api", "user-service", "notification-service"],
    tenant_id="tenant-789"
)
```

---

## WorkflowEventPublisher

**Domain:** Workflow Management

### Event Catalog

| Event Type | Description |
|------------|-------------|
| `workflow.started` | Workflow initiated |
| `workflow.state_changed` | Workflow state transition |
| `workflow.completed` | Workflow completed successfully |
| `workflow.failed` | Workflow failed |
| `workflow.milestone_reached` | Workflow milestone achieved |
| `workflow.action_executed` | Workflow action executed |

### Usage Examples

#### Publish Workflow Started

```python
from shared.eventbus import WorkflowEventPublisher

workflow_publisher = WorkflowEventPublisher()

await workflow_publisher.publish_workflow_started(
    workflow_id=789,
    workflow_type="BIA",
    initiator_id="user-123",
    context={
        "department": "IT",
        "priority": "HIGH",
        "estimated_duration_days": 7
    },
    tenant_id="tenant-789"
)
```

#### Publish Workflow State Changed

```python
await workflow_publisher.publish_workflow_state_changed(
    workflow_id=789,
    from_state="DRAFT",
    to_state="IN_PROGRESS",
    changed_by="user-123",
    reason="All prerequisites completed",
    tenant_id="tenant-789"
)
```

#### Publish Workflow Completed

```python
await workflow_publisher.publish_workflow_completed(
    workflow_id=789,
    duration_days=5.5,
    outcome="SUCCESS",
    completion_metrics={
        "tasks_completed": 15,
        "quality_score": 9.2,
        "on_time": True,
        "stakeholder_satisfaction": 4.8
    },
    tenant_id="tenant-789"
)
```

#### Publish Workflow Failed

```python
await workflow_publisher.publish_workflow_failed(
    workflow_id=789,
    error="Database connection timeout",
    error_details={
        "code": "DB_TIMEOUT",
        "retry_count": 3,
        "last_attempt": "2025-10-07T10:30:00Z"
    },
    recovery_actions=[
        "Check database connectivity",
        "Review connection pool settings",
        "Retry workflow"
    ],
    tenant_id="tenant-789"
)
```

#### Publish Milestone Reached

```python
await workflow_publisher.publish_milestone_reached(
    workflow_id=789,
    milestone="IMPACT_ANALYSIS_COMPLETE",
    milestone_data={
        "completion_percentage": 50,
        "duration_days": 3,
        "quality_check_passed": True
    },
    tenant_id="tenant-789"
)
```

#### Publish Action Executed

```python
await workflow_publisher.publish_action_executed(
    workflow_id=789,
    action_type="SEND_NOTIFICATION",
    result="SUCCESS",
    action_details={
        "recipients": 5,
        "channel": "email",
        "delivery_time_ms": 234
    },
    tenant_id="tenant-789"
)
```

---

## RiskEventPublisher

**Domain:** Risk Management

### Event Catalog

| Event Type | Description |
|------------|-------------|
| `risk.identified` | New risk identified |
| `risk.score_changed` | Risk score updated |
| `risk.mitigated` | Risk mitigation implemented |
| `risk.accepted` | Risk formally accepted |

### Usage Examples

#### Publish Risk Identified

```python
from shared.eventbus import RiskEventPublisher

risk_publisher = RiskEventPublisher()

await risk_publisher.publish_risk_identified(
    risk_id=123,
    risk_type="OPERATIONAL",
    severity="HIGH",
    description="Critical supplier single point of failure",
    impact_areas=["SUPPLY_CHAIN", "PRODUCTION", "REVENUE"],
    tenant_id="tenant-789",
    additional_data={
        "likelihood": 0.4,
        "impact": 9,
        "initial_score": 7.5
    }
)
```

#### Publish Risk Score Changed

```python
await risk_publisher.publish_risk_score_changed(
    risk_id=123,
    old_score=7.5,
    new_score=5.0,
    reason="Implemented supplier diversification strategy",
    changed_by="risk-manager-456",
    tenant_id="tenant-789"
)
```

#### Publish Risk Mitigated

```python
await risk_publisher.publish_risk_mitigated(
    risk_id=123,
    mitigation_strategy="DIVERSIFY_SUPPLIERS",
    mitigation_details={
        "new_suppliers": 3,
        "geographic_distribution": ["US", "EU", "APAC"],
        "cost_increase_percent": 5,
        "implementation_date": "2025-10-01"
    },
    residual_risk=2.5,
    tenant_id="tenant-789"
)
```

#### Publish Risk Accepted

```python
await risk_publisher.publish_risk_accepted(
    risk_id=456,
    approver_id="executive-789",
    acceptance_rationale="Cost of mitigation ($500K) exceeds potential annual impact ($200K)",
    review_date="2025-12-31",
    tenant_id="tenant-789"
)
```

---

## IncidentEventPublisher

**Domain:** Incident Management

### Event Catalog

| Event Type | Description |
|------------|-------------|
| `incident.opened` | New incident opened |
| `incident.escalated` | Incident escalated |
| `incident.resolved` | Incident resolved |
| `incident.pattern_detected` | Recurring incident pattern detected |

### Usage Examples

#### Publish Incident Opened

```python
from shared.eventbus import IncidentEventPublisher

incident_publisher = IncidentEventPublisher()

await incident_publisher.publish_incident_opened(
    incident_id=789,
    incident_type="OUTAGE",
    severity="SEV1",
    description="Database primary node failure",
    affected_services=["payment-api", "user-service", "reporting"],
    tenant_id="tenant-789",
    additional_data={
        "detected_at": "2025-10-07T08:15:00Z",
        "detection_method": "automated_monitoring",
        "affected_users": 5000
    }
)
```

#### Publish Incident Escalated

```python
await incident_publisher.publish_incident_escalated(
    incident_id=789,
    from_level="L1_SUPPORT",
    to_level="L2_ENGINEERING",
    escalation_reason="Requires database cluster expertise",
    escalated_by="support-123",
    tenant_id="tenant-789"
)
```

#### Publish Incident Resolved

```python
await incident_publisher.publish_incident_resolved(
    incident_id=789,
    resolution_time_hours=2.5,
    resolution_summary="Failover to secondary database node completed successfully",
    root_cause="Hardware failure on primary database server",
    resolved_by="engineer-456",
    tenant_id="tenant-789",
    additional_data={
        "downtime_minutes": 15,
        "users_affected": 5000,
        "data_loss": False,
        "permanent_fix_eta": "2025-10-08"
    }
)
```

#### Publish Incident Pattern Detected

```python
await incident_publisher.publish_incident_pattern_detected(
    pattern_type="RECURRING_OUTAGE",
    incidents_count=5,
    pattern_details={
        "frequency": "every_monday",
        "affected_component": "database",
        "time_pattern": "06:00-07:00 UTC",
        "common_root_cause": "automated_backup_process"
    },
    recommendation="Schedule backup maintenance outside peak hours",
    tenant_id="tenant-789"
)
```

---

## ComplianceEventPublisher

**Domain:** Compliance & Audit Management

### Event Catalog

| Event Type | Description |
|------------|-------------|
| `compliance.audit_started` | Compliance audit initiated |
| `compliance.control_validated` | Control validation completed |
| `compliance.gap_identified` | Compliance gap identified |
| `compliance.achieved` | Compliance certification achieved |

### Usage Examples

#### Publish Audit Started

```python
from shared.eventbus import ComplianceEventPublisher

compliance_publisher = ComplianceEventPublisher()

await compliance_publisher.publish_audit_started(
    audit_id=123,
    standard="ISO22301",
    scope="Business Continuity Management System - Full scope",
    auditor_id="auditor-456",
    planned_completion="2025-12-31",
    tenant_id="tenant-789",
    additional_data={
        "audit_type": "CERTIFICATION",
        "certification_body": "BSI Group",
        "preparation_weeks": 8
    }
)
```

#### Publish Control Validated

```python
# Control passed
await compliance_publisher.publish_control_validated(
    control_id=456,
    validation_result="PASSED",
    validator_id="auditor-123",
    evidence=["doc-789", "screenshot-012", "config-snapshot-345"],
    findings="Control is operating effectively. Documentation is complete.",
    tenant_id="tenant-789"
)

# Control failed
await compliance_publisher.publish_control_validated(
    control_id=457,
    validation_result="FAILED",
    validator_id="auditor-123",
    evidence=["incomplete-doc-001"],
    findings="BIA documentation is incomplete. Missing RTO/RPO for 5 critical processes.",
    tenant_id="tenant-789"
)
```

#### Publish Gap Identified

```python
await compliance_publisher.publish_gap_identified(
    gap_id=789,
    severity="HIGH",
    requirement="ISO22301-8.4.1",
    gap_description="Business Impact Analysis documentation incomplete for 5 critical processes",
    remediation_plan="Complete BIA for payment processing, customer service, inventory management, order fulfillment, and reporting systems",
    target_date="2025-11-30",
    tenant_id="tenant-789",
    additional_data={
        "identified_by": "auditor-456",
        "affected_processes": 5,
        "estimated_effort_days": 10
    }
)
```

#### Publish Compliance Achieved

```python
await compliance_publisher.publish_compliance_achieved(
    standard="ISO22301",
    certification_date="2025-10-07",
    certification_body="BSI Group",
    certificate_id="CERT-2025-123456",
    expiry_date="2028-10-07",
    tenant_id="tenant-789",
    additional_data={
        "scope": "Full organizational BCMS",
        "surveillance_dates": ["2026-10-07", "2027-10-07"],
        "achievement_duration_months": 12
    }
)
```

---

## CommunityEventPublisher

**Domain:** Community Intelligence & Knowledge Sharing

### Event Catalog

| Event Type | Description |
|------------|-------------|
| `community.case_submitted` | Knowledge case submitted |
| `community.review_assigned` | Case review assigned |
| `community.case_approved` | Case approved for publication |
| `community.case_rejected` | Case rejected |

### Usage Examples

#### Publish Case Submitted

```python
from shared.eventbus import CommunityEventPublisher

community_publisher = CommunityEventPublisher()

await community_publisher.publish_case_submitted(
    case_id=123,
    contributor_id="user-456",
    module="BIA",
    case_type="BEST_PRACTICE",
    tags=["healthcare", "critical-processes", "pandemic-response"],
    tenant_id="tenant-789",
    additional_data={
        "title": "Healthcare BIA During Pandemic",
        "industry": "healthcare",
        "organization_size": "large"
    }
)
```

#### Publish Review Assigned

```python
await community_publisher.publish_review_assigned(
    case_id=123,
    reviewer_id="expert-789",
    assignment_reason="Healthcare domain expertise and ISO22301 certification",
    due_date="2025-10-14",
    tenant_id="tenant-789"
)
```

#### Publish Case Approved

```python
await community_publisher.publish_case_approved(
    case_id=123,
    final_score=8.5,
    approved_by="expert-789",
    review_comments="Excellent best practice documentation with clear examples",
    quality_metrics={
        "completeness": 9.0,
        "clarity": 8.5,
        "applicability": 8.0,
        "innovation": 8.5,
        "documentation_quality": 9.0
    },
    tenant_id="tenant-789"
)
```

#### Publish Case Rejected

```python
await community_publisher.publish_case_rejected(
    case_id=124,
    reasons=["INCOMPLETE_DOCUMENTATION", "MISSING_EXAMPLES", "LACKS_CONTEXT"],
    rejected_by="expert-789",
    feedback="Please add more detailed examples, provide context about organization size and industry, and include lessons learned section.",
    resubmission_allowed=True,
    tenant_id="tenant-789"
)
```

---

## Integration Guide

### Service Integration Pattern

#### 1. BIA Service Integration

```python
# intelligent-core/bia-engine/api/routes.py
from fastapi import APIRouter, Depends
from shared.eventbus import BIAEventPublisher

router = APIRouter()
bia_publisher = BIAEventPublisher()

@router.post("/bia/")
async def create_bia(bia_data: BIACreate):
    # Create BIA in database
    bia = await create_bia_record(bia_data)

    # Publish event
    await bia_publisher.publish_bia_started(
        bia_id=bia.id,
        process_name=bia.process_name,
        org_id=bia.org_id,
        tenant_id=bia.tenant_id
    )

    return bia

@router.put("/bia/{bia_id}/complete")
async def complete_bia(bia_id: int, completion_data: BIACompletion):
    # Update BIA
    bia = await update_bia_status(bia_id, "COMPLETED")

    # Publish completion event
    await bia_publisher.publish_bia_completed(
        bia_id=bia.id,
        rto=bia.rto,
        rpo=bia.rpo,
        criticality=bia.criticality,
        impact_score=bia.impact_score,
        tenant_id=bia.tenant_id
    )

    return bia
```

#### 2. Workflow Service Integration

```python
# intelligent-core/orchestration/workflow-intelligence/services/workflow_service.py
from shared.eventbus import WorkflowEventPublisher

class WorkflowService:
    def __init__(self):
        self.workflow_publisher = WorkflowEventPublisher()

    async def start_workflow(self, workflow_data: WorkflowCreate):
        # Create workflow
        workflow = await self.create_workflow(workflow_data)

        # Publish started event
        await self.workflow_publisher.publish_workflow_started(
            workflow_id=workflow.id,
            workflow_type=workflow.workflow_type,
            initiator_id=workflow.initiator_id,
            tenant_id=workflow.tenant_id
        )

        return workflow

    async def transition_state(self, workflow_id: int, new_state: str):
        # Get current state
        workflow = await self.get_workflow(workflow_id)
        old_state = workflow.state

        # Update state
        workflow.state = new_state
        await self.update_workflow(workflow)

        # Publish state change event
        await self.workflow_publisher.publish_workflow_state_changed(
            workflow_id=workflow.id,
            from_state=old_state,
            to_state=new_state,
            tenant_id=workflow.tenant_id
        )
```

#### 3. Risk Service Integration

```python
# intelligent-core/risk-management/api/routes.py
from shared.eventbus import RiskEventPublisher

router = APIRouter()
risk_publisher = RiskEventPublisher()

@router.post("/risks/")
async def identify_risk(risk_data: RiskCreate):
    # Create risk record
    risk = await create_risk(risk_data)

    # Publish identification event
    await risk_publisher.publish_risk_identified(
        risk_id=risk.id,
        risk_type=risk.risk_type,
        severity=risk.severity,
        description=risk.description,
        impact_areas=risk.impact_areas,
        tenant_id=risk.tenant_id
    )

    return risk
```

### Error Handling Pattern

```python
from shared.eventbus import WorkflowEventPublisher
import logging

logger = logging.getLogger(__name__)

async def execute_workflow_action(workflow_id: int, action_type: str):
    workflow_publisher = WorkflowEventPublisher()

    try:
        # Execute action
        result = await perform_action(workflow_id, action_type)

        # Publish success event
        success = await workflow_publisher.publish_action_executed(
            workflow_id=workflow_id,
            action_type=action_type,
            result="SUCCESS",
            action_details=result,
            tenant_id=get_tenant_id()
        )

        if not success:
            logger.warning(f"Failed to publish action_executed event for workflow {workflow_id}")

        return result

    except Exception as e:
        logger.error(f"Action execution failed: {e}")

        # Publish failure event
        await workflow_publisher.publish_workflow_failed(
            workflow_id=workflow_id,
            error=str(e),
            error_details={"action_type": action_type},
            tenant_id=get_tenant_id()
        )

        raise
```

### Testing Pattern

```python
import pytest
from shared.eventbus import init_eventbus, BIAEventPublisher

@pytest.mark.asyncio
async def test_bia_event_publishing(rabbitmq_url):
    # Initialize eventbus
    eventbus = init_eventbus(rabbitmq_url)
    await eventbus.connect()

    # Create publisher
    bia_publisher = BIAEventPublisher()

    # Publish event
    success = await bia_publisher.publish_bia_started(
        bia_id=123,
        process_name="Test Process",
        org_id="org-test",
        tenant_id="tenant-test"
    )

    assert success is True

    # Cleanup
    await eventbus.disconnect()
```

---

## Event Naming Conventions

### Pattern

```
{domain}.{action}
```

### Examples

- `bia.started` - BIA domain, started action
- `workflow.state_changed` - Workflow domain, state changed action
- `risk.identified` - Risk domain, identified action
- `incident.opened` - Incident domain, opened action
- `compliance.audit_started` - Compliance domain, audit started action
- `community.case_submitted` - Community domain, case submitted action

---

## Best Practices

### 1. Always Include tenant_id

```python
# Good
await publisher.publish_event(
    ...,
    tenant_id=current_tenant_id
)

# Bad - Missing tenant_id
await publisher.publish_event(...)
```

### 2. Use additional_data for Custom Fields

```python
# Good - Extensible
await bia_publisher.publish_bia_started(
    bia_id=123,
    process_name="Payment Processing",
    org_id="org-456",
    tenant_id="tenant-789",
    additional_data={
        "custom_field_1": "value1",
        "integration_source": "salesforce"
    }
)
```

### 3. Handle Publishing Failures

```python
# Good - Check return value
success = await publisher.publish_event(...)
if not success:
    logger.warning("Failed to publish event, continuing operation")

# Bad - Ignoring failures
await publisher.publish_event(...)
```

### 4. Log Important Events

```python
# Good - Log before publishing
logger.info(f"Publishing BIA completion for BIA {bia_id}")
success = await bia_publisher.publish_bia_completed(...)
if success:
    logger.info(f"Successfully published BIA completion event")
```

### 5. Use Type Hints

```python
from typing import Optional, Dict, Any

async def process_bia(
    bia_id: int,
    tenant_id: str,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    return await bia_publisher.publish_bia_started(
        bia_id=bia_id,
        tenant_id=tenant_id,
        additional_data=context
    )
```

---

## Event Subscribers

Subscribe to these events using EventSubscriber:

```python
from shared.eventbus import get_eventbus

async def handle_bia_completed(event_data: dict, tenant_id: str):
    bia_id = event_data["bia_id"]
    print(f"BIA {bia_id} completed for tenant {tenant_id}")

# Subscribe to specific event
eventbus = get_eventbus()
await eventbus.subscribe("bia.completed", handle_bia_completed)

# Subscribe to all BIA events
await eventbus.subscribe("bia.*", handle_all_bia_events)

# Subscribe to all events
await eventbus.subscribe("#", handle_all_events)
```

---

## Migration from Generic Publisher

### Before (Generic EventPublisher)

```python
from shared.eventbus import EventPublisher

publisher = EventPublisher(service_name="bia")
await publisher.publish(
    entity="bia",
    action="started",
    entity_id=123,
    data={
        "process_name": "Payment Processing",
        "org_id": "org-456"
    },
    tenant_id="tenant-789"
)
```

### After (Domain-Specific Publisher)

```python
from shared.eventbus import BIAEventPublisher

bia_publisher = BIAEventPublisher()
await bia_publisher.publish_bia_started(
    bia_id=123,
    process_name="Payment Processing",
    org_id="org-456",
    tenant_id="tenant-789"
)
```

**Benefits:**
- Type safety
- Clear API
- IDE autocomplete
- Better documentation
- Reduced errors

---

## Troubleshooting

### Event Not Being Published

1. **Check EventBus initialization:**
   ```python
   from shared.eventbus import get_eventbus

   eventbus = get_eventbus()
   if not eventbus.is_connected():
       await eventbus.connect()
   ```

2. **Check RabbitMQ connectivity:**
   ```bash
   # Test RabbitMQ connection
   curl http://localhost:15672/api/overview
   ```

3. **Enable debug logging:**
   ```python
   import logging
   logging.getLogger("shared.eventbus").setLevel(logging.DEBUG)
   ```

### Event Not Being Received

1. **Verify subscription:**
   ```python
   await eventbus.subscribe("bia.started", handler)
   ```

2. **Check routing key:**
   - Use `bia.*` to match all BIA events
   - Use `#` to match all events

3. **Verify tenant_id filtering** in subscriber

---

## Performance Considerations

- Event publishing is async and non-blocking
- Failed publishes return `False` but don't raise exceptions
- Use `additional_data` sparingly (keep events small)
- Consider batching events for high-volume scenarios

---

## Summary

- **6 domain publishers** covering all BCM domains
- **26 specialized methods** for type-safe event publishing
- **Consistent API** across all domains
- **Full error handling** with logging
- **Extensible** via `additional_data` parameter
- **Production-ready** with comprehensive examples

For questions or issues, refer to the EventBus documentation or contact the platform team.
