# Comprehensive Event Catalog
## BCM Platform - Event-Driven Architecture

**Version:** 2.0
**Last Updated:** 2025-10-09
**Total Events:** 217
**Event Format:** `domain.entity.action`

---

## Table of Contents

- [Workflow Events (35)](#workflow-events)
- [BIA Events (28)](#bia-events)
- [Risk Events (27)](#risk-events)
- [Planning Events (23)](#planning-events)
- [Compliance Events (22)](#compliance-events)
- [Governance Events (18)](#governance-events)
- [Documents Events (17)](#documents-events)
- [Exercises Events (16)](#exercises-events)
- [Learning Events (12)](#learning-events)
- [Infrastructure Events (16)](#infrastructure-events)
- [Crisis Events (13)](#crisis-events)
- [Response Events (10)](#response-events)

---

## Workflow Events

### workflow.instance.created
**Publishers:** workflow-engine, temporal-workflows
**Subscribers:** audit-service, notification-service
**Payload:**
```json
{
  "workflow_id": "string",
  "workflow_type": "string",
  "tenant_id": "string",
  "created_by": "string",
  "metadata": {}
}
```

### workflow.instance.started
**Publishers:** workflow-engine
**Subscribers:** monitoring-service, event-intelligence
**Payload:**
```json
{
  "workflow_id": "string",
  "execution_id": "string",
  "started_at": "timestamp"
}
```

### workflow.instance.completed
**Publishers:** workflow-engine
**Subscribers:** audit-service, metrics-service, community-service
**Payload:**
```json
{
  "workflow_id": "string",
  "execution_id": "string",
  "completed_at": "timestamp",
  "duration_seconds": "number",
  "status": "string"
}
```

### workflow.instance.failed
**Publishers:** workflow-engine
**Subscribers:** alert-service, monitoring-service
**Payload:**
```json
{
  "workflow_id": "string",
  "execution_id": "string",
  "error": "string",
  "failed_at": "timestamp"
}
```

### workflow.instance.cancelled
**Publishers:** workflow-engine
**Subscribers:** audit-service
**Payload:**
```json
{
  "workflow_id": "string",
  "execution_id": "string",
  "cancelled_by": "string",
  "reason": "string"
}
```

### workflow.stage.changed
**Publishers:** workflow-engine
**Subscribers:** notification-service, ui-service
**Payload:**
```json
{
  "workflow_id": "string",
  "from_stage": "string",
  "to_stage": "string",
  "changed_at": "timestamp"
}
```

### workflow.stage.completed
**Publishers:** workflow-engine
**Subscribers:** metrics-service
**Payload:**
```json
{
  "workflow_id": "string",
  "stage": "string",
  "completed_at": "timestamp"
}
```

### workflow.task.assigned
**Publishers:** workflow-engine
**Subscribers:** notification-service, user-service
**Payload:**
```json
{
  "task_id": "string",
  "workflow_id": "string",
  "assigned_to": "string",
  "assigned_by": "string",
  "due_date": "timestamp"
}
```

### workflow.task.completed
**Publishers:** workflow-engine
**Subscribers:** audit-service, metrics-service
**Payload:**
```json
{
  "task_id": "string",
  "workflow_id": "string",
  "completed_by": "string",
  "completed_at": "timestamp"
}
```

### workflow.task.overdue
**Publishers:** scheduler-service
**Subscribers:** notification-service, escalation-service
**Payload:**
```json
{
  "task_id": "string",
  "workflow_id": "string",
  "assigned_to": "string",
  "overdue_by_hours": "number"
}
```

### workflow.task.escalated
**Publishers:** escalation-service
**Subscribers:** notification-service, management-dashboard
**Payload:**
```json
{
  "task_id": "string",
  "workflow_id": "string",
  "escalated_to": "string",
  "reason": "string"
}
```

### workflow.approval.requested
**Publishers:** workflow-engine
**Subscribers:** notification-service, approval-service
**Payload:**
```json
{
  "approval_id": "string",
  "workflow_id": "string",
  "approvers": ["string"],
  "requested_at": "timestamp"
}
```

### workflow.approval.granted
**Publishers:** approval-service
**Subscribers:** workflow-engine, audit-service
**Payload:**
```json
{
  "approval_id": "string",
  "workflow_id": "string",
  "approved_by": "string",
  "approved_at": "timestamp"
}
```

### workflow.approval.rejected
**Publishers:** approval-service
**Subscribers:** workflow-engine, notification-service
**Payload:**
```json
{
  "approval_id": "string",
  "workflow_id": "string",
  "rejected_by": "string",
  "reason": "string"
}
```

### workflow.milestone.reached
**Publishers:** workflow-engine
**Subscribers:** metrics-service, notification-service
**Payload:**
```json
{
  "workflow_id": "string",
  "milestone": "string",
  "reached_at": "timestamp"
}
```

### workflow.sla.warning
**Publishers:** monitoring-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "workflow_id": "string",
  "sla_threshold": "number",
  "current_duration": "number"
}
```

### workflow.sla.breached
**Publishers:** monitoring-service
**Subscribers:** alert-service, management-dashboard
**Payload:**
```json
{
  "workflow_id": "string",
  "sla_threshold": "number",
  "actual_duration": "number"
}
```

### workflow.data.updated
**Publishers:** workflow-engine
**Subscribers:** analytics-service
**Payload:**
```json
{
  "workflow_id": "string",
  "field": "string",
  "old_value": "any",
  "new_value": "any"
}
```

### workflow.comment.added
**Publishers:** collaboration-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "workflow_id": "string",
  "comment_id": "string",
  "author": "string",
  "content": "string"
}
```

### workflow.attachment.uploaded
**Publishers:** document-service
**Subscribers:** workflow-engine, virus-scanner
**Payload:**
```json
{
  "workflow_id": "string",
  "attachment_id": "string",
  "filename": "string",
  "size_bytes": "number"
}
```

### workflow.template.created
**Publishers:** template-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "template_id": "string",
  "name": "string",
  "created_by": "string"
}
```

### workflow.template.updated
**Publishers:** template-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "template_id": "string",
  "updated_by": "string",
  "version": "number"
}
```

### workflow.template.published
**Publishers:** template-service
**Subscribers:** notification-service, workflow-engine
**Payload:**
```json
{
  "template_id": "string",
  "published_by": "string",
  "version": "number"
}
```

### workflow.validation.failed
**Publishers:** validation-service
**Subscribers:** workflow-engine, notification-service
**Payload:**
```json
{
  "workflow_id": "string",
  "validation_errors": ["string"],
  "failed_at": "timestamp"
}
```

### workflow.validation.passed
**Publishers:** validation-service
**Subscribers:** workflow-engine
**Payload:**
```json
{
  "workflow_id": "string",
  "validated_at": "timestamp"
}
```

### workflow.parallel.branch.started
**Publishers:** workflow-engine
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "workflow_id": "string",
  "branch_id": "string",
  "branch_name": "string"
}
```

### workflow.parallel.branch.completed
**Publishers:** workflow-engine
**Subscribers:** workflow-engine, monitoring-service
**Payload:**
```json
{
  "workflow_id": "string",
  "branch_id": "string",
  "completed_at": "timestamp"
}
```

### workflow.parallel.join.ready
**Publishers:** workflow-engine
**Subscribers:** workflow-engine
**Payload:**
```json
{
  "workflow_id": "string",
  "branches_completed": ["string"]
}
```

### workflow.retry.initiated
**Publishers:** workflow-engine
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "workflow_id": "string",
  "retry_count": "number",
  "reason": "string"
}
```

### workflow.retry.exhausted
**Publishers:** workflow-engine
**Subscribers:** alert-service
**Payload:**
```json
{
  "workflow_id": "string",
  "max_retries": "number",
  "last_error": "string"
}
```

### workflow.compensation.started
**Publishers:** workflow-engine
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "workflow_id": "string",
  "compensation_reason": "string"
}
```

### workflow.compensation.completed
**Publishers:** workflow-engine
**Subscribers:** audit-service
**Payload:**
```json
{
  "workflow_id": "string",
  "compensated_at": "timestamp"
}
```

### workflow.timer.expired
**Publishers:** scheduler-service
**Subscribers:** workflow-engine
**Payload:**
```json
{
  "workflow_id": "string",
  "timer_id": "string",
  "expired_at": "timestamp"
}
```

### workflow.signal.received
**Publishers:** workflow-engine
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "workflow_id": "string",
  "signal_name": "string",
  "signal_data": {}
}
```

### workflow.query.executed
**Publishers:** workflow-engine
**Subscribers:** analytics-service
**Payload:**
```json
{
  "workflow_id": "string",
  "query_type": "string",
  "result": {}
}
```

---

## BIA Events

### bia.assessment.created
**Publishers:** bia-service
**Subscribers:** audit-service, workflow-engine
**Payload:**
```json
{
  "assessment_id": "string",
  "name": "string",
  "created_by": "string",
  "tenant_id": "string"
}
```

### bia.assessment.started
**Publishers:** bia-service
**Subscribers:** notification-service, metrics-service
**Payload:**
```json
{
  "assessment_id": "string",
  "started_by": "string",
  "started_at": "timestamp"
}
```

### bia.assessment.completed
**Publishers:** bia-service
**Subscribers:** risk-service, planning-service, audit-service
**Payload:**
```json
{
  "assessment_id": "string",
  "completed_at": "timestamp",
  "processes": [{
    "process_id": "string",
    "name": "string",
    "criticality": "string",
    "rto": "number",
    "rpo": "number",
    "mtpd": "number"
  }],
  "critical_process_count": "number",
  "total_processes": "number"
}
```

### bia.assessment.updated
**Publishers:** bia-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "assessment_id": "string",
  "updated_by": "string",
  "changes": {}
}
```

### bia.assessment.approved
**Publishers:** bia-service
**Subscribers:** planning-service, governance-service
**Payload:**
```json
{
  "assessment_id": "string",
  "approved_by": "string",
  "approved_at": "timestamp"
}
```

### bia.assessment.rejected
**Publishers:** bia-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "assessment_id": "string",
  "rejected_by": "string",
  "reason": "string"
}
```

### bia.process.created
**Publishers:** bia-service
**Subscribers:** dependency-service, audit-service
**Payload:**
```json
{
  "process_id": "string",
  "assessment_id": "string",
  "name": "string",
  "owner": "string"
}
```

### bia.process.updated
**Publishers:** bia-service
**Subscribers:** audit-service, analytics-service
**Payload:**
```json
{
  "process_id": "string",
  "updated_fields": {}
}
```

### bia.process.deleted
**Publishers:** bia-service
**Subscribers:** dependency-service, audit-service
**Payload:**
```json
{
  "process_id": "string",
  "deleted_by": "string"
}
```

### bia.criticality.assigned
**Publishers:** bia-service
**Subscribers:** risk-service, planning-service
**Payload:**
```json
{
  "process_id": "string",
  "criticality": "string",
  "score": "number"
}
```

### bia.criticality.changed
**Publishers:** bia-service
**Subscribers:** risk-service, planning-service, notification-service
**Payload:**
```json
{
  "process_id": "string",
  "old_criticality": "string",
  "new_criticality": "string",
  "changed_by": "string"
}
```

### bia.rto.set
**Publishers:** bia-service
**Subscribers:** planning-service, validation-service
**Payload:**
```json
{
  "process_id": "string",
  "rto_hours": "number",
  "set_by": "string"
}
```

### bia.rpo.set
**Publishers:** bia-service
**Subscribers:** planning-service, validation-service
**Payload:**
```json
{
  "process_id": "string",
  "rpo_hours": "number",
  "set_by": "string"
}
```

### bia.mtpd.set
**Publishers:** bia-service
**Subscribers:** planning-service
**Payload:**
```json
{
  "process_id": "string",
  "mtpd_hours": "number",
  "set_by": "string"
}
```

### bia.dependency.added
**Publishers:** bia-service
**Subscribers:** dependency-service, analytics-service
**Payload:**
```json
{
  "process_id": "string",
  "dependency_type": "string",
  "dependency_id": "string",
  "criticality": "string"
}
```

### bia.dependency.removed
**Publishers:** bia-service
**Subscribers:** dependency-service
**Payload:**
```json
{
  "process_id": "string",
  "dependency_id": "string"
}
```

### bia.dependency.updated
**Publishers:** bia-service
**Subscribers:** dependency-service, analytics-service
**Payload:**
```json
{
  "dependency_id": "string",
  "updated_fields": {}
}
```

### bia.impact.assessed
**Publishers:** bia-service
**Subscribers:** risk-service, reporting-service
**Payload:**
```json
{
  "process_id": "string",
  "financial_impact": "number",
  "operational_impact": "string",
  "reputational_impact": "string"
}
```

### bia.resource.identified
**Publishers:** bia-service
**Subscribers:** planning-service, resource-service
**Payload:**
```json
{
  "process_id": "string",
  "resource_type": "string",
  "resource_id": "string",
  "criticality": "string"
}
```

### bia.recovery.strategy.proposed
**Publishers:** bia-service
**Subscribers:** planning-service
**Payload:**
```json
{
  "process_id": "string",
  "strategy": "string",
  "estimated_cost": "number"
}
```

### bia.validation.completed
**Publishers:** validation-service
**Subscribers:** bia-service, audit-service
**Payload:**
```json
{
  "assessment_id": "string",
  "validation_result": "string",
  "issues": ["string"]
}
```

### bia.report.generated
**Publishers:** reporting-service
**Subscribers:** document-service, notification-service
**Payload:**
```json
{
  "assessment_id": "string",
  "report_id": "string",
  "format": "string"
}
```

### bia.review.scheduled
**Publishers:** scheduler-service
**Subscribers:** notification-service, bia-service
**Payload:**
```json
{
  "assessment_id": "string",
  "review_date": "timestamp",
  "reviewers": ["string"]
}
```

### bia.review.completed
**Publishers:** bia-service
**Subscribers:** audit-service, metrics-service
**Payload:**
```json
{
  "assessment_id": "string",
  "review_date": "timestamp",
  "changes_required": "boolean"
}
```

### bia.critical.process.identified
**Publishers:** bia-service
**Subscribers:** risk-service, planning-service, alert-service
**Payload:**
```json
{
  "process_id": "string",
  "name": "string",
  "criticality_score": "number",
  "requires_immediate_attention": "boolean"
}
```

### bia.threshold.exceeded
**Publishers:** bia-service
**Subscribers:** alert-service, management-dashboard
**Payload:**
```json
{
  "process_id": "string",
  "threshold_type": "string",
  "threshold_value": "number",
  "actual_value": "number"
}
```

### bia.gap.identified
**Publishers:** bia-service
**Subscribers:** planning-service, risk-service
**Payload:**
```json
{
  "process_id": "string",
  "gap_type": "string",
  "severity": "string",
  "description": "string"
}
```

### bia.scenario.analyzed
**Publishers:** bia-service
**Subscribers:** risk-service, planning-service
**Payload:**
```json
{
  "assessment_id": "string",
  "scenario_type": "string",
  "affected_processes": ["string"],
  "estimated_impact": {}
}
```

---

## Risk Events

### risk.assessment.created
**Publishers:** risk-service
**Subscribers:** audit-service, workflow-engine
**Payload:**
```json
{
  "assessment_id": "string",
  "name": "string",
  "created_by": "string"
}
```

### risk.assessment.started
**Publishers:** risk-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "assessment_id": "string",
  "started_at": "timestamp"
}
```

### risk.assessment.completed
**Publishers:** risk-service
**Subscribers:** planning-service, governance-service, audit-service
**Payload:**
```json
{
  "assessment_id": "string",
  "completed_at": "timestamp",
  "risks": [{
    "risk_id": "string",
    "severity": "string",
    "likelihood": "string",
    "impact": "string"
  }],
  "high_risk_count": "number",
  "total_risks": "number"
}
```

### risk.identified
**Publishers:** risk-service, bia-service, ai-advisor
**Subscribers:** planning-service, notification-service
**Payload:**
```json
{
  "risk_id": "string",
  "title": "string",
  "source": "string",
  "category": "string",
  "initial_severity": "string"
}
```

### risk.analyzed
**Publishers:** risk-service
**Subscribers:** planning-service, reporting-service
**Payload:**
```json
{
  "risk_id": "string",
  "likelihood": "string",
  "impact": "string",
  "risk_score": "number",
  "analyzed_by": "string"
}
```

### risk.severity.changed
**Publishers:** risk-service
**Subscribers:** planning-service, alert-service, notification-service
**Payload:**
```json
{
  "risk_id": "string",
  "old_severity": "string",
  "new_severity": "string",
  "changed_by": "string",
  "reason": "string"
}
```

### risk.mitigation.proposed
**Publishers:** risk-service, ai-advisor
**Subscribers:** planning-service, approval-service
**Payload:**
```json
{
  "risk_id": "string",
  "mitigation_id": "string",
  "strategy": "string",
  "estimated_cost": "number",
  "estimated_risk_reduction": "number"
}
```

### risk.mitigation.approved
**Publishers:** approval-service
**Subscribers:** planning-service, implementation-service
**Payload:**
```json
{
  "mitigation_id": "string",
  "risk_id": "string",
  "approved_by": "string",
  "budget_allocated": "number"
}
```

### risk.mitigation.implemented
**Publishers:** implementation-service
**Subscribers:** risk-service, audit-service
**Payload:**
```json
{
  "mitigation_id": "string",
  "risk_id": "string",
  "implemented_at": "timestamp",
  "actual_cost": "number"
}
```

### risk.mitigation.verified
**Publishers:** validation-service
**Subscribers:** risk-service, reporting-service
**Payload:**
```json
{
  "mitigation_id": "string",
  "risk_id": "string",
  "effectiveness": "string",
  "residual_risk_score": "number"
}
```

### risk.residual.calculated
**Publishers:** risk-service
**Subscribers:** reporting-service, governance-service
**Payload:**
```json
{
  "risk_id": "string",
  "inherent_risk": "number",
  "control_effectiveness": "number",
  "residual_risk": "number"
}
```

### risk.threshold.exceeded
**Publishers:** risk-service
**Subscribers:** alert-service, management-dashboard
**Payload:**
```json
{
  "risk_id": "string",
  "threshold_type": "string",
  "threshold_value": "number",
  "actual_value": "number"
}
```

### risk.control.created
**Publishers:** risk-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "control_id": "string",
  "risk_id": "string",
  "control_type": "string",
  "owner": "string"
}
```

### risk.control.tested
**Publishers:** testing-service
**Subscribers:** risk-service, audit-service
**Payload:**
```json
{
  "control_id": "string",
  "test_date": "timestamp",
  "result": "string",
  "effectiveness": "number"
}
```

### risk.control.failed
**Publishers:** testing-service
**Subscribers:** alert-service, risk-service
**Payload:**
```json
{
  "control_id": "string",
  "risk_id": "string",
  "failure_reason": "string",
  "impact": "string"
}
```

### risk.owner.assigned
**Publishers:** risk-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "risk_id": "string",
  "owner": "string",
  "assigned_by": "string"
}
```

### risk.owner.changed
**Publishers:** risk-service
**Subscribers:** notification-service, audit-service
**Payload:**
```json
{
  "risk_id": "string",
  "old_owner": "string",
  "new_owner": "string"
}
```

### risk.review.scheduled
**Publishers:** scheduler-service
**Subscribers:** notification-service, risk-service
**Payload:**
```json
{
  "risk_id": "string",
  "review_date": "timestamp",
  "reviewer": "string"
}
```

### risk.review.completed
**Publishers:** risk-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "risk_id": "string",
  "reviewed_at": "timestamp",
  "changes_required": "boolean"
}
```

### risk.accepted
**Publishers:** risk-service
**Subscribers:** audit-service, governance-service
**Payload:**
```json
{
  "risk_id": "string",
  "accepted_by": "string",
  "acceptance_rationale": "string"
}
```

### risk.transferred
**Publishers:** risk-service
**Subscribers:** insurance-service, audit-service
**Payload:**
```json
{
  "risk_id": "string",
  "transfer_method": "string",
  "transfer_to": "string",
  "transfer_cost": "number"
}
```

### risk.closed
**Publishers:** risk-service
**Subscribers:** audit-service, reporting-service
**Payload:**
```json
{
  "risk_id": "string",
  "closed_by": "string",
  "closure_reason": "string",
  "closed_at": "timestamp"
}
```

### risk.reopened
**Publishers:** risk-service
**Subscribers:** notification-service, audit-service
**Payload:**
```json
{
  "risk_id": "string",
  "reopened_by": "string",
  "reason": "string"
}
```

### risk.escalated
**Publishers:** risk-service
**Subscribers:** alert-service, management-dashboard
**Payload:**
```json
{
  "risk_id": "string",
  "escalated_to": "string",
  "reason": "string"
}
```

### risk.trend.analyzed
**Publishers:** analytics-service
**Subscribers:** reporting-service, management-dashboard
**Payload:**
```json
{
  "period": "string",
  "trend_direction": "string",
  "risk_categories": {},
  "recommendations": ["string"]
}
```

### risk.correlation.detected
**Publishers:** ai-advisor
**Subscribers:** risk-service, alert-service
**Payload:**
```json
{
  "risk_ids": ["string"],
  "correlation_type": "string",
  "correlation_strength": "number",
  "recommended_action": "string"
}
```

### risk.suggestion.generated
**Publishers:** ai-advisor
**Subscribers:** risk-service, notification-service
**Payload:**
```json
{
  "source": "string",
  "suggested_risks": [{
    "title": "string",
    "category": "string",
    "estimated_severity": "string",
    "rationale": "string"
  }],
  "confidence": "number"
}
```

---

## Planning Events

### plan.created
**Publishers:** planning-service
**Subscribers:** audit-service, workflow-engine
**Payload:**
```json
{
  "plan_id": "string",
  "plan_type": "string",
  "name": "string",
  "created_by": "string"
}
```

### plan.updated
**Publishers:** planning-service
**Subscribers:** audit-service, version-control
**Payload:**
```json
{
  "plan_id": "string",
  "updated_by": "string",
  "version": "number",
  "changes": {}
}
```

### plan.approved
**Publishers:** planning-service
**Subscribers:** governance-service, notification-service
**Payload:**
```json
{
  "plan_id": "string",
  "approved_by": "string",
  "approved_at": "timestamp",
  "version": "number"
}
```

### plan.rejected
**Publishers:** planning-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "plan_id": "string",
  "rejected_by": "string",
  "reason": "string"
}
```

### plan.published
**Publishers:** planning-service
**Subscribers:** notification-service, training-service
**Payload:**
```json
{
  "plan_id": "string",
  "published_at": "timestamp",
  "stakeholders": ["string"]
}
```

### plan.activated
**Publishers:** planning-service, response-service
**Subscribers:** notification-service, coordination-service
**Payload:**
```json
{
  "plan_id": "string",
  "activated_by": "string",
  "activated_at": "timestamp",
  "trigger_event": "string"
}
```

### plan.deactivated
**Publishers:** planning-service, response-service
**Subscribers:** notification-service, audit-service
**Payload:**
```json
{
  "plan_id": "string",
  "deactivated_by": "string",
  "deactivated_at": "timestamp",
  "duration": "number"
}
```

### plan.tested
**Publishers:** exercise-service
**Subscribers:** planning-service, reporting-service
**Payload:**
```json
{
  "plan_id": "string",
  "exercise_id": "string",
  "test_date": "timestamp",
  "result": "string",
  "effectiveness_score": "number"
}
```

### plan.review.scheduled
**Publishers:** scheduler-service
**Subscribers:** notification-service, planning-service
**Payload:**
```json
{
  "plan_id": "string",
  "review_date": "timestamp",
  "reviewers": ["string"]
}
```

### plan.review.completed
**Publishers:** planning-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "plan_id": "string",
  "reviewed_at": "timestamp",
  "updates_required": "boolean",
  "findings": ["string"]
}
```

### plan.version.created
**Publishers:** version-control
**Subscribers:** audit-service, document-service
**Payload:**
```json
{
  "plan_id": "string",
  "version": "number",
  "created_by": "string",
  "change_summary": "string"
}
```

### plan.archived
**Publishers:** planning-service
**Subscribers:** document-service, audit-service
**Payload:**
```json
{
  "plan_id": "string",
  "archived_by": "string",
  "archived_at": "timestamp",
  "reason": "string"
}
```

### plan.restored
**Publishers:** planning-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "plan_id": "string",
  "restored_by": "string",
  "restored_at": "timestamp"
}
```

### plan.gap.identified
**Publishers:** validation-service, exercise-service
**Subscribers:** planning-service, alert-service
**Payload:**
```json
{
  "plan_id": "string",
  "gap_type": "string",
  "severity": "string",
  "description": "string"
}
```

### plan.strategy.proposed
**Publishers:** ai-advisor, planning-service
**Subscribers:** approval-service
**Payload:**
```json
{
  "plan_id": "string",
  "strategy_type": "string",
  "description": "string",
  "estimated_cost": "number"
}
```

### plan.resource.allocated
**Publishers:** resource-service
**Subscribers:** planning-service, notification-service
**Payload:**
```json
{
  "plan_id": "string",
  "resource_type": "string",
  "quantity": "number",
  "allocated_by": "string"
}
```

### plan.team.assigned
**Publishers:** planning-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "plan_id": "string",
  "team_members": ["string"],
  "roles": {}
}
```

### plan.training.required
**Publishers:** planning-service
**Subscribers:** training-service, notification-service
**Payload:**
```json
{
  "plan_id": "string",
  "required_training": ["string"],
  "target_audience": ["string"],
  "deadline": "timestamp"
}
```

### plan.dependency.identified
**Publishers:** planning-service
**Subscribers:** dependency-service
**Payload:**
```json
{
  "plan_id": "string",
  "dependency_type": "string",
  "dependency_id": "string"
}
```

### plan.objective.set
**Publishers:** planning-service
**Subscribers:** metrics-service
**Payload:**
```json
{
  "plan_id": "string",
  "objective_id": "string",
  "objective": "string",
  "target_value": "number"
}
```

### plan.objective.achieved
**Publishers:** metrics-service
**Subscribers:** planning-service, notification-service
**Payload:**
```json
{
  "plan_id": "string",
  "objective_id": "string",
  "achieved_at": "timestamp",
  "actual_value": "number"
}
```

### plan.effectiveness.measured
**Publishers:** metrics-service
**Subscribers:** reporting-service, planning-service
**Payload:**
```json
{
  "plan_id": "string",
  "effectiveness_score": "number",
  "measurement_date": "timestamp",
  "metrics": {}
}
```

### plan.template.applied
**Publishers:** planning-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "plan_id": "string",
  "template_id": "string",
  "applied_by": "string"
}
```

---

## Compliance Events

### compliance.standard.added
**Publishers:** compliance-service
**Subscribers:** audit-service, gap-analysis-service
**Payload:**
```json
{
  "standard_id": "string",
  "standard_name": "string",
  "version": "string",
  "added_by": "string"
}
```

### compliance.requirement.created
**Publishers:** compliance-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "requirement_id": "string",
  "standard_id": "string",
  "requirement_text": "string",
  "clause": "string"
}
```

### compliance.assessment.started
**Publishers:** compliance-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "assessment_id": "string",
  "standard_id": "string",
  "started_by": "string"
}
```

### compliance.assessment.completed
**Publishers:** compliance-service
**Subscribers:** audit-service, reporting-service
**Payload:**
```json
{
  "assessment_id": "string",
  "standard_id": "string",
  "compliance_score": "number",
  "compliant_count": "number",
  "non_compliant_count": "number"
}
```

### compliance.gap.identified
**Publishers:** compliance-service, gap-analysis-service
**Subscribers:** planning-service, alert-service
**Payload:**
```json
{
  "gap_id": "string",
  "requirement_id": "string",
  "severity": "string",
  "description": "string"
}
```

### compliance.gap.closed
**Publishers:** compliance-service
**Subscribers:** audit-service, reporting-service
**Payload:**
```json
{
  "gap_id": "string",
  "closed_by": "string",
  "closed_at": "timestamp",
  "evidence_id": "string"
}
```

### compliance.evidence.uploaded
**Publishers:** compliance-service
**Subscribers:** audit-service, validation-service
**Payload:**
```json
{
  "evidence_id": "string",
  "requirement_id": "string",
  "file_name": "string",
  "uploaded_by": "string"
}
```

### compliance.evidence.verified
**Publishers:** validation-service
**Subscribers:** compliance-service, audit-service
**Payload:**
```json
{
  "evidence_id": "string",
  "verified_by": "string",
  "verification_status": "string",
  "comments": "string"
}
```

### compliance.evidence.rejected
**Publishers:** validation-service
**Subscribers:** compliance-service, notification-service
**Payload:**
```json
{
  "evidence_id": "string",
  "rejected_by": "string",
  "reason": "string"
}
```

### compliance.control.implemented
**Publishers:** compliance-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "control_id": "string",
  "requirement_id": "string",
  "implemented_by": "string",
  "implementation_date": "timestamp"
}
```

### compliance.control.tested
**Publishers:** testing-service
**Subscribers:** compliance-service, audit-service
**Payload:**
```json
{
  "control_id": "string",
  "test_date": "timestamp",
  "result": "string",
  "tester": "string"
}
```

### compliance.audit.scheduled
**Publishers:** scheduler-service
**Subscribers:** notification-service, compliance-service
**Payload:**
```json
{
  "audit_id": "string",
  "standard_id": "string",
  "audit_date": "timestamp",
  "auditors": ["string"]
}
```

### compliance.audit.completed
**Publishers:** compliance-service
**Subscribers:** reporting-service, governance-service
**Payload:**
```json
{
  "audit_id": "string",
  "completion_date": "timestamp",
  "findings_count": "number",
  "non_conformities": "number"
}
```

### compliance.finding.created
**Publishers:** compliance-service
**Subscribers:** planning-service, notification-service
**Payload:**
```json
{
  "finding_id": "string",
  "audit_id": "string",
  "severity": "string",
  "description": "string"
}
```

### compliance.finding.resolved
**Publishers:** compliance-service
**Subscribers:** audit-service, reporting-service
**Payload:**
```json
{
  "finding_id": "string",
  "resolved_by": "string",
  "resolution": "string",
  "resolved_at": "timestamp"
}
```

### compliance.certificate.issued
**Publishers:** compliance-service
**Subscribers:** document-service, notification-service
**Payload:**
```json
{
  "certificate_id": "string",
  "standard_id": "string",
  "issued_date": "timestamp",
  "expiry_date": "timestamp"
}
```

### compliance.certificate.expiring
**Publishers:** scheduler-service
**Subscribers:** alert-service, compliance-service
**Payload:**
```json
{
  "certificate_id": "string",
  "standard_id": "string",
  "expiry_date": "timestamp",
  "days_remaining": "number"
}
```

### compliance.certificate.expired
**Publishers:** scheduler-service
**Subscribers:** alert-service, management-dashboard
**Payload:**
```json
{
  "certificate_id": "string",
  "standard_id": "string",
  "expired_at": "timestamp"
}
```

### compliance.improvement.planned
**Publishers:** compliance-service
**Subscribers:** planning-service
**Payload:**
```json
{
  "improvement_id": "string",
  "description": "string",
  "target_date": "timestamp"
}
```

### compliance.improvement.completed
**Publishers:** compliance-service
**Subscribers:** audit-service, reporting-service
**Payload:**
```json
{
  "improvement_id": "string",
  "completed_at": "timestamp",
  "effectiveness": "string"
}
```

### compliance.report.generated
**Publishers:** reporting-service
**Subscribers:** document-service, notification-service
**Payload:**
```json
{
  "report_id": "string",
  "report_type": "string",
  "generated_at": "timestamp",
  "format": "string"
}
```

### compliance.violation.detected
**Publishers:** compliance-service, monitoring-service
**Subscribers:** alert-service, governance-service
**Payload:**
```json
{
  "violation_id": "string",
  "requirement_id": "string",
  "severity": "string",
  "detected_at": "timestamp"
}
```

---

## Governance Events

### governance.policy.created
**Publishers:** governance-service
**Subscribers:** audit-service, notification-service
**Payload:**
```json
{
  "policy_id": "string",
  "name": "string",
  "category": "string",
  "created_by": "string"
}
```

### governance.policy.updated
**Publishers:** governance-service
**Subscribers:** audit-service, version-control
**Payload:**
```json
{
  "policy_id": "string",
  "version": "number",
  "updated_by": "string",
  "changes": {}
}
```

### governance.policy.approved
**Publishers:** governance-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "policy_id": "string",
  "approved_by": "string",
  "approved_at": "timestamp"
}
```

### governance.policy.published
**Publishers:** governance-service
**Subscribers:** notification-service, training-service
**Payload:**
```json
{
  "policy_id": "string",
  "published_at": "timestamp",
  "effective_date": "timestamp"
}
```

### governance.policy.reviewed
**Publishers:** governance-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "policy_id": "string",
  "reviewed_at": "timestamp",
  "reviewer": "string",
  "update_required": "boolean"
}
```

### governance.policy.archived
**Publishers:** governance-service
**Subscribers:** audit-service, document-service
**Payload:**
```json
{
  "policy_id": "string",
  "archived_by": "string",
  "archived_at": "timestamp"
}
```

### governance.role.created
**Publishers:** governance-service
**Subscribers:** access-control-service
**Payload:**
```json
{
  "role_id": "string",
  "role_name": "string",
  "permissions": ["string"]
}
```

### governance.role.assigned
**Publishers:** governance-service
**Subscribers:** notification-service, access-control-service
**Payload:**
```json
{
  "user_id": "string",
  "role_id": "string",
  "assigned_by": "string",
  "assigned_at": "timestamp"
}
```

### governance.role.revoked
**Publishers:** governance-service
**Subscribers:** notification-service, access-control-service
**Payload:**
```json
{
  "user_id": "string",
  "role_id": "string",
  "revoked_by": "string",
  "reason": "string"
}
```

### governance.objective.created
**Publishers:** governance-service
**Subscribers:** metrics-service
**Payload:**
```json
{
  "objective_id": "string",
  "objective": "string",
  "target_date": "timestamp",
  "owner": "string"
}
```

### governance.objective.achieved
**Publishers:** metrics-service
**Subscribers:** governance-service, notification-service
**Payload:**
```json
{
  "objective_id": "string",
  "achieved_at": "timestamp",
  "actual_result": {}
}
```

### governance.committee.meeting.scheduled
**Publishers:** scheduler-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "meeting_id": "string",
  "committee": "string",
  "scheduled_date": "timestamp",
  "attendees": ["string"]
}
```

### governance.committee.decision.made
**Publishers:** governance-service
**Subscribers:** audit-service, implementation-service
**Payload:**
```json
{
  "decision_id": "string",
  "committee": "string",
  "decision": "string",
  "action_items": ["string"]
}
```

### governance.competence.gap.identified
**Publishers:** governance-service
**Subscribers:** training-service, planning-service
**Payload:**
```json
{
  "gap_id": "string",
  "competence_area": "string",
  "current_level": "string",
  "required_level": "string"
}
```

### governance.resource.allocated
**Publishers:** governance-service
**Subscribers:** resource-service, notification-service
**Payload:**
```json
{
  "resource_type": "string",
  "amount": "number",
  "allocated_to": "string",
  "purpose": "string"
}
```

### governance.budget.approved
**Publishers:** governance-service
**Subscribers:** finance-service, notification-service
**Payload:**
```json
{
  "budget_id": "string",
  "amount": "number",
  "fiscal_period": "string",
  "approved_by": "string"
}
```

### governance.kpi.defined
**Publishers:** governance-service
**Subscribers:** metrics-service
**Payload:**
```json
{
  "kpi_id": "string",
  "name": "string",
  "target_value": "number",
  "measurement_frequency": "string"
}
```

### governance.kpi.measured
**Publishers:** metrics-service
**Subscribers:** governance-service, reporting-service
**Payload:**
```json
{
  "kpi_id": "string",
  "measurement_date": "timestamp",
  "actual_value": "number",
  "target_value": "number"
}
```

---

## Documents Events

### document.created
**Publishers:** document-service
**Subscribers:** audit-service, version-control
**Payload:**
```json
{
  "document_id": "string",
  "title": "string",
  "document_type": "string",
  "created_by": "string"
}
```

### document.updated
**Publishers:** document-service
**Subscribers:** audit-service, version-control
**Payload:**
```json
{
  "document_id": "string",
  "version": "number",
  "updated_by": "string"
}
```

### document.approved
**Publishers:** document-service
**Subscribers:** notification-service, workflow-engine
**Payload:**
```json
{
  "document_id": "string",
  "approved_by": "string",
  "approved_at": "timestamp"
}
```

### document.published
**Publishers:** document-service
**Subscribers:** notification-service, search-indexer
**Payload:**
```json
{
  "document_id": "string",
  "published_at": "timestamp",
  "access_level": "string"
}
```

### document.reviewed
**Publishers:** document-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "document_id": "string",
  "reviewed_by": "string",
  "reviewed_at": "timestamp",
  "status": "string"
}
```

### document.archived
**Publishers:** document-service
**Subscribers:** audit-service, storage-service
**Payload:**
```json
{
  "document_id": "string",
  "archived_by": "string",
  "archived_at": "timestamp"
}
```

### document.deleted
**Publishers:** document-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "document_id": "string",
  "deleted_by": "string",
  "reason": "string"
}
```

### document.version.created
**Publishers:** version-control
**Subscribers:** audit-service
**Payload:**
```json
{
  "document_id": "string",
  "version": "number",
  "created_by": "string"
}
```

### document.shared
**Publishers:** document-service
**Subscribers:** notification-service, access-control-service
**Payload:**
```json
{
  "document_id": "string",
  "shared_with": ["string"],
  "shared_by": "string",
  "permissions": "string"
}
```

### document.accessed
**Publishers:** document-service
**Subscribers:** analytics-service
**Payload:**
```json
{
  "document_id": "string",
  "accessed_by": "string",
  "accessed_at": "timestamp"
}
```

### document.downloaded
**Publishers:** document-service
**Subscribers:** analytics-service, audit-service
**Payload:**
```json
{
  "document_id": "string",
  "downloaded_by": "string",
  "downloaded_at": "timestamp"
}
```

### document.expiring
**Publishers:** scheduler-service
**Subscribers:** notification-service, document-service
**Payload:**
```json
{
  "document_id": "string",
  "expiry_date": "timestamp",
  "days_remaining": "number"
}
```

### document.expired
**Publishers:** scheduler-service
**Subscribers:** alert-service, document-service
**Payload:**
```json
{
  "document_id": "string",
  "expired_at": "timestamp"
}
```

### document.template.created
**Publishers:** document-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "template_id": "string",
  "name": "string",
  "category": "string"
}
```

### document.generated.from.template
**Publishers:** document-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "document_id": "string",
  "template_id": "string",
  "generated_by": "string"
}
```

### document.comment.added
**Publishers:** collaboration-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "document_id": "string",
  "comment_id": "string",
  "author": "string",
  "comment": "string"
}
```

### document.tag.added
**Publishers:** document-service
**Subscribers:** search-indexer
**Payload:**
```json
{
  "document_id": "string",
  "tag": "string",
  "added_by": "string"
}
```

---

## Exercises Events

### exercise.created
**Publishers:** exercise-service
**Subscribers:** audit-service, notification-service
**Payload:**
```json
{
  "exercise_id": "string",
  "exercise_type": "string",
  "name": "string",
  "created_by": "string"
}
```

### exercise.scheduled
**Publishers:** exercise-service
**Subscribers:** notification-service, calendar-service
**Payload:**
```json
{
  "exercise_id": "string",
  "scheduled_date": "timestamp",
  "participants": ["string"]
}
```

### exercise.started
**Publishers:** exercise-service
**Subscribers:** notification-service, monitoring-service
**Payload:**
```json
{
  "exercise_id": "string",
  "started_at": "timestamp",
  "facilitator": "string"
}
```

### exercise.completed
**Publishers:** exercise-service
**Subscribers:** audit-service, reporting-service, planning-service
**Payload:**
```json
{
  "exercise_id": "string",
  "completed_at": "timestamp",
  "duration": "number",
  "success_rate": "number",
  "gaps_identified": ["string"]
}
```

### exercise.cancelled
**Publishers:** exercise-service
**Subscribers:** notification-service, audit-service
**Payload:**
```json
{
  "exercise_id": "string",
  "cancelled_by": "string",
  "reason": "string"
}
```

### exercise.inject.created
**Publishers:** exercise-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "inject_id": "string",
  "exercise_id": "string",
  "inject_type": "string",
  "scheduled_time": "timestamp"
}
```

### exercise.inject.delivered
**Publishers:** exercise-service
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "inject_id": "string",
  "exercise_id": "string",
  "delivered_at": "timestamp"
}
```

### exercise.response.submitted
**Publishers:** exercise-service
**Subscribers:** evaluation-service
**Payload:**
```json
{
  "exercise_id": "string",
  "inject_id": "string",
  "participant": "string",
  "response": "string",
  "response_time": "number"
}
```

### exercise.participant.joined
**Publishers:** exercise-service
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "exercise_id": "string",
  "participant": "string",
  "joined_at": "timestamp"
}
```

### exercise.gap.identified
**Publishers:** evaluation-service
**Subscribers:** planning-service, alert-service
**Payload:**
```json
{
  "exercise_id": "string",
  "gap_type": "string",
  "severity": "string",
  "description": "string"
}
```

### exercise.report.generated
**Publishers:** reporting-service
**Subscribers:** document-service, notification-service
**Payload:**
```json
{
  "exercise_id": "string",
  "report_id": "string",
  "generated_at": "timestamp"
}
```

### exercise.improvement.identified
**Publishers:** evaluation-service
**Subscribers:** planning-service
**Payload:**
```json
{
  "exercise_id": "string",
  "improvement_area": "string",
  "recommendation": "string",
  "priority": "string"
}
```

### exercise.objective.achieved
**Publishers:** evaluation-service
**Subscribers:** metrics-service
**Payload:**
```json
{
  "exercise_id": "string",
  "objective_id": "string",
  "achieved": "boolean"
}
```

### exercise.scenario.created
**Publishers:** exercise-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "scenario_id": "string",
  "name": "string",
  "scenario_type": "string"
}
```

### exercise.debrief.scheduled
**Publishers:** exercise-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "exercise_id": "string",
  "debrief_date": "timestamp",
  "participants": ["string"]
}
```

### exercise.debrief.completed
**Publishers:** exercise-service
**Subscribers:** reporting-service
**Payload:**
```json
{
  "exercise_id": "string",
  "debrief_date": "timestamp",
  "action_items": ["string"]
}
```

---

## Learning Events

### learning.program.created
**Publishers:** learning-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "program_id": "string",
  "name": "string",
  "category": "string",
  "created_by": "string"
}
```

### learning.program.published
**Publishers:** learning-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "program_id": "string",
  "published_at": "timestamp"
}
```

### learning.enrollment.created
**Publishers:** learning-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "enrollment_id": "string",
  "program_id": "string",
  "user_id": "string"
}
```

### learning.training.started
**Publishers:** learning-service
**Subscribers:** metrics-service
**Payload:**
```json
{
  "enrollment_id": "string",
  "program_id": "string",
  "user_id": "string",
  "started_at": "timestamp"
}
```

### learning.training.completed
**Publishers:** learning-service
**Subscribers:** governance-service, metrics-service, notification-service
**Payload:**
```json
{
  "enrollment_id": "string",
  "program_id": "string",
  "user_id": "string",
  "completed_at": "timestamp",
  "score": "number"
}
```

### learning.assessment.passed
**Publishers:** learning-service
**Subscribers:** certification-service, notification-service
**Payload:**
```json
{
  "assessment_id": "string",
  "user_id": "string",
  "score": "number",
  "passing_score": "number"
}
```

### learning.assessment.failed
**Publishers:** learning-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "assessment_id": "string",
  "user_id": "string",
  "score": "number",
  "passing_score": "number"
}
```

### learning.certification.issued
**Publishers:** certification-service
**Subscribers:** governance-service, notification-service, document-service
**Payload:**
```json
{
  "certificate_id": "string",
  "user_id": "string",
  "program_id": "string",
  "issued_at": "timestamp",
  "expiry_date": "timestamp"
}
```

### learning.certification.expiring
**Publishers:** scheduler-service
**Subscribers:** notification-service, learning-service
**Payload:**
```json
{
  "certificate_id": "string",
  "user_id": "string",
  "expiry_date": "timestamp",
  "days_remaining": "number"
}
```

### learning.certification.expired
**Publishers:** scheduler-service
**Subscribers:** alert-service, governance-service
**Payload:**
```json
{
  "certificate_id": "string",
  "user_id": "string",
  "expired_at": "timestamp"
}
```

### learning.progress.updated
**Publishers:** learning-service
**Subscribers:** metrics-service
**Payload:**
```json
{
  "enrollment_id": "string",
  "user_id": "string",
  "progress_percentage": "number"
}
```

### learning.content.accessed
**Publishers:** learning-service
**Subscribers:** analytics-service
**Payload:**
```json
{
  "content_id": "string",
  "user_id": "string",
  "accessed_at": "timestamp"
}
```

---

## Infrastructure Events

### infrastructure.service.started
**Publishers:** all-services
**Subscribers:** monitoring-service, service-registry
**Payload:**
```json
{
  "service_name": "string",
  "version": "string",
  "instance_id": "string",
  "started_at": "timestamp"
}
```

### infrastructure.service.stopped
**Publishers:** all-services
**Subscribers:** monitoring-service, service-registry
**Payload:**
```json
{
  "service_name": "string",
  "instance_id": "string",
  "stopped_at": "timestamp"
}
```

### infrastructure.service.health.degraded
**Publishers:** monitoring-service
**Subscribers:** alert-service
**Payload:**
```json
{
  "service_name": "string",
  "health_status": "string",
  "metrics": {}
}
```

### infrastructure.service.health.recovered
**Publishers:** monitoring-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "service_name": "string",
  "recovered_at": "timestamp"
}
```

### infrastructure.database.connection.lost
**Publishers:** database-monitor
**Subscribers:** alert-service, ops-team
**Payload:**
```json
{
  "database": "string",
  "service": "string",
  "lost_at": "timestamp"
}
```

### infrastructure.database.connection.restored
**Publishers:** database-monitor
**Subscribers:** notification-service
**Payload:**
```json
{
  "database": "string",
  "service": "string",
  "restored_at": "timestamp"
}
```

### infrastructure.cache.cleared
**Publishers:** cache-service
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "cache_name": "string",
  "cleared_by": "string",
  "cleared_at": "timestamp"
}
```

### infrastructure.backup.started
**Publishers:** backup-service
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "backup_id": "string",
  "backup_type": "string",
  "started_at": "timestamp"
}
```

### infrastructure.backup.completed
**Publishers:** backup-service
**Subscribers:** notification-service, audit-service
**Payload:**
```json
{
  "backup_id": "string",
  "completed_at": "timestamp",
  "size_bytes": "number",
  "status": "string"
}
```

### infrastructure.backup.failed
**Publishers:** backup-service
**Subscribers:** alert-service
**Payload:**
```json
{
  "backup_id": "string",
  "failed_at": "timestamp",
  "error": "string"
}
```

### infrastructure.deployment.started
**Publishers:** deployment-service
**Subscribers:** monitoring-service, notification-service
**Payload:**
```json
{
  "deployment_id": "string",
  "service_name": "string",
  "version": "string",
  "started_by": "string"
}
```

### infrastructure.deployment.completed
**Publishers:** deployment-service
**Subscribers:** audit-service, notification-service
**Payload:**
```json
{
  "deployment_id": "string",
  "service_name": "string",
  "version": "string",
  "completed_at": "timestamp"
}
```

### infrastructure.deployment.failed
**Publishers:** deployment-service
**Subscribers:** alert-service, ops-team
**Payload:**
```json
{
  "deployment_id": "string",
  "service_name": "string",
  "error": "string",
  "failed_at": "timestamp"
}
```

### infrastructure.scaling.triggered
**Publishers:** autoscaler-service
**Subscribers:** monitoring-service
**Payload:**
```json
{
  "service_name": "string",
  "current_instances": "number",
  "target_instances": "number",
  "trigger_reason": "string"
}
```

### infrastructure.resource.threshold.exceeded
**Publishers:** monitoring-service
**Subscribers:** alert-service, autoscaler-service
**Payload:**
```json
{
  "resource_type": "string",
  "service_name": "string",
  "threshold": "number",
  "current_value": "number"
}
```

### infrastructure.security.scan.completed
**Publishers:** security-scanner
**Subscribers:** security-team, audit-service
**Payload:**
```json
{
  "scan_id": "string",
  "scan_type": "string",
  "vulnerabilities_found": "number",
  "severity_breakdown": {}
}
```

---

## Crisis Events

### crisis.declared
**Publishers:** crisis-service, response-service
**Subscribers:** notification-service, planning-service, alert-service
**Payload:**
```json
{
  "crisis_id": "string",
  "crisis_type": "string",
  "severity": "string",
  "declared_by": "string",
  "declared_at": "timestamp"
}
```

### crisis.escalated
**Publishers:** crisis-service
**Subscribers:** notification-service, management-dashboard
**Payload:**
```json
{
  "crisis_id": "string",
  "from_level": "string",
  "to_level": "string",
  "escalated_by": "string"
}
```

### crisis.team.activated
**Publishers:** crisis-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "crisis_id": "string",
  "team_members": ["string"],
  "activated_at": "timestamp"
}
```

### crisis.update.posted
**Publishers:** crisis-service
**Subscribers:** notification-service, stakeholder-service
**Payload:**
```json
{
  "crisis_id": "string",
  "update_id": "string",
  "update_text": "string",
  "posted_by": "string"
}
```

### crisis.action.created
**Publishers:** crisis-service
**Subscribers:** task-service, notification-service
**Payload:**
```json
{
  "crisis_id": "string",
  "action_id": "string",
  "action": "string",
  "assigned_to": "string",
  "priority": "string"
}
```

### crisis.action.completed
**Publishers:** task-service
**Subscribers:** crisis-service, metrics-service
**Payload:**
```json
{
  "crisis_id": "string",
  "action_id": "string",
  "completed_by": "string",
  "completed_at": "timestamp"
}
```

### crisis.resource.requested
**Publishers:** crisis-service
**Subscribers:** resource-service
**Payload:**
```json
{
  "crisis_id": "string",
  "resource_type": "string",
  "quantity": "number",
  "urgency": "string"
}
```

### crisis.resource.deployed
**Publishers:** resource-service
**Subscribers:** crisis-service, notification-service
**Payload:**
```json
{
  "crisis_id": "string",
  "resource_type": "string",
  "quantity": "number",
  "deployed_at": "timestamp"
}
```

### crisis.resolved
**Publishers:** crisis-service
**Subscribers:** audit-service, reporting-service, notification-service
**Payload:**
```json
{
  "crisis_id": "string",
  "resolved_by": "string",
  "resolved_at": "timestamp",
  "duration": "number",
  "summary": "string"
}
```

### crisis.debrief.scheduled
**Publishers:** crisis-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "crisis_id": "string",
  "debrief_date": "timestamp",
  "participants": ["string"]
}
```

### crisis.lesson.learned
**Publishers:** crisis-service
**Subscribers:** knowledge-base, planning-service
**Payload:**
```json
{
  "crisis_id": "string",
  "lesson": "string",
  "category": "string",
  "recommendations": ["string"]
}
```

### crisis.communication.sent
**Publishers:** communication-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "crisis_id": "string",
  "communication_id": "string",
  "recipients": ["string"],
  "channel": "string",
  "sent_at": "timestamp"
}
```

### crisis.status.changed
**Publishers:** crisis-service
**Subscribers:** notification-service, monitoring-service
**Payload:**
```json
{
  "crisis_id": "string",
  "from_status": "string",
  "to_status": "string",
  "changed_at": "timestamp"
}
```

---

## Response Events

### response.incident.created
**Publishers:** response-service
**Subscribers:** notification-service, workflow-engine
**Payload:**
```json
{
  "incident_id": "string",
  "incident_type": "string",
  "severity": "string",
  "created_by": "string"
}
```

### response.incident.updated
**Publishers:** response-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "incident_id": "string",
  "updated_fields": {},
  "updated_by": "string"
}
```

### response.incident.status.changed
**Publishers:** response-service
**Subscribers:** notification-service, monitoring-service
**Payload:**
```json
{
  "incident_id": "string",
  "from_status": "string",
  "to_status": "string"
}
```

### response.incident.escalated
**Publishers:** response-service
**Subscribers:** alert-service, notification-service
**Payload:**
```json
{
  "incident_id": "string",
  "escalated_to": "string",
  "reason": "string"
}
```

### response.incident.resolved
**Publishers:** response-service
**Subscribers:** audit-service, metrics-service
**Payload:**
```json
{
  "incident_id": "string",
  "resolved_by": "string",
  "resolved_at": "timestamp",
  "resolution": "string"
}
```

### response.incident.closed
**Publishers:** response-service
**Subscribers:** audit-service, reporting-service
**Payload:**
```json
{
  "incident_id": "string",
  "closed_by": "string",
  "closed_at": "timestamp"
}
```

### response.team.mobilized
**Publishers:** response-service
**Subscribers:** notification-service
**Payload:**
```json
{
  "incident_id": "string",
  "team_members": ["string"],
  "mobilized_at": "timestamp"
}
```

### response.communication.issued
**Publishers:** communication-service
**Subscribers:** audit-service
**Payload:**
```json
{
  "incident_id": "string",
  "communication_type": "string",
  "recipients": ["string"],
  "issued_at": "timestamp"
}
```

### response.metrics.updated
**Publishers:** metrics-service
**Subscribers:** reporting-service, monitoring-service
**Payload:**
```json
{
  "incident_id": "string",
  "metrics": {},
  "updated_at": "timestamp"
}
```

### response.recovery.completed
**Publishers:** response-service
**Subscribers:** audit-service, notification-service
**Payload:**
```json
{
  "incident_id": "string",
  "recovery_time": "number",
  "completed_at": "timestamp"
}
```

---

## Event Choreography Patterns

### Pattern 1: BIA → Risk → Planning Flow

```
bia.assessment.completed
  ├─→ risk-service: Generate risk suggestions
  │   └─→ risk.suggestion.generated
  │       └─→ risk-service: Create risk assessments
  │           └─→ risk.assessment.completed
  │               └─→ planning-service: Auto-create BC plans
  │                   └─→ plan.created
  └─→ planning-service: Analyze recovery requirements
```

### Pattern 2: Compliance Gap → Remediation Flow

```
compliance.gap.identified
  ├─→ planning-service: Create remediation plan
  │   └─→ plan.created
  └─→ risk-service: Assess compliance risk
      └─→ risk.identified
```

### Pattern 3: Exercise → Improvement Flow

```
exercise.completed
  └─→ exercise.gap.identified
      ├─→ planning-service: Update plans
      │   └─→ plan.updated
      └─→ training-service: Create training
          └─→ learning.program.created
```

### Pattern 4: Crisis → Response → Recovery Flow

```
crisis.declared
  ├─→ plan.activated
  ├─→ response.team.mobilized
  └─→ crisis.team.activated
      └─→ crisis.action.created
          └─→ crisis.action.completed
              └─→ crisis.resolved
```

---

## Event Naming Conventions

1. **Format**: `domain.entity.action`
   - domain: Service or business area
   - entity: Resource being acted upon
   - action: Past tense verb

2. **Examples**:
   - ✅ `bia.assessment.completed`
   - ✅ `risk.mitigation.approved`
   - ❌ `bia-assessment-complete`
   - ❌ `BIA_ASSESSMENT_COMPLETED`

3. **Wildcard Subscriptions**:
   - `bia.*` - All BIA events
   - `*.assessment.*` - All assessment events
   - `risk.*.changed` - All risk change events

---

## Event Priority Guidelines

- **CRITICAL**: System failures, security incidents, crisis events
- **HIGH**: Compliance violations, high-severity risks, SLA breaches
- **NORMAL**: Standard workflow events, updates, completions
- **LOW**: Analytics, metrics, non-urgent notifications

---

**Generated by:** Agent 3 - Choreography Implementation Specialist
**Last Updated:** 2025-10-09
