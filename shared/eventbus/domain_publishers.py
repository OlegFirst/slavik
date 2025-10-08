"""
Domain-Specific Event Publishers
=================================

Specialized event publishers for each BCM domain.
These provide type-safe, domain-specific event publishing methods.

Usage:
    ```python
    from shared.eventbus.domain_publishers import BIAEventPublisher

    bia_publisher = BIAEventPublisher()
    await bia_publisher.publish_bia_started(
        bia_id=123,
        process_name="Payment Processing",
        org_id="org-456",
        tenant_id="tenant-789"
    )
    ```
"""

from typing import Optional, Dict, Any, List
import logging
from shared.eventbus.client import get_eventbus

logger = logging.getLogger(__name__)


class BIAEventPublisher:
    """
    Business Impact Analysis (BIA) domain event publisher.

    Publishes events related to BIA processes, impact assessments,
    and process criticality analysis.
    """

    async def publish_bia_started(
        self,
        bia_id: int,
        process_name: str,
        org_id: str,
        tenant_id: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish BIA process started event.

        Args:
            bia_id: BIA identifier
            process_name: Business process name
            org_id: Organization identifier
            tenant_id: Tenant identifier
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await bia_publisher.publish_bia_started(
                bia_id=123,
                process_name="Payment Processing",
                org_id="org-456",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "bia_id": bia_id,
                "process_name": process_name,
                "org_id": org_id,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("bia.started", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish bia.started event: {e}", exc_info=True)
            return False

    async def publish_bia_completed(
        self,
        bia_id: int,
        rto: int,
        criticality: str,
        tenant_id: str,
        rpo: Optional[int] = None,
        impact_score: Optional[float] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish BIA process completed event.

        Args:
            bia_id: BIA identifier
            rto: Recovery Time Objective (hours)
            criticality: Criticality level (CRITICAL, HIGH, MEDIUM, LOW)
            tenant_id: Tenant identifier
            rpo: Recovery Point Objective (hours)
            impact_score: Calculated impact score
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await bia_publisher.publish_bia_completed(
                bia_id=123,
                rto=4,
                criticality="CRITICAL",
                rpo=1,
                impact_score=9.5,
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "bia_id": bia_id,
                "rto": rto,
                "rpo": rpo,
                "criticality": criticality,
                "impact_score": impact_score,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("bia.completed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish bia.completed event: {e}", exc_info=True)
            return False

    async def publish_bia_validated(
        self,
        bia_id: int,
        validator_id: str,
        tenant_id: str,
        validation_status: str = "APPROVED",
        comments: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish BIA validation event.

        Args:
            bia_id: BIA identifier
            validator_id: Validator user identifier
            tenant_id: Tenant identifier
            validation_status: Validation status (APPROVED, REJECTED, NEEDS_REVISION)
            comments: Validation comments
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await bia_publisher.publish_bia_validated(
                bia_id=123,
                validator_id="user-456",
                validation_status="APPROVED",
                comments="All metrics verified",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "bia_id": bia_id,
                "validator_id": validator_id,
                "validation_status": validation_status,
                "comments": comments,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("bia.validated", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish bia.validated event: {e}", exc_info=True)
            return False

    async def publish_process_analyzed(
        self,
        process_id: int,
        impact_data: Dict[str, Any],
        tenant_id: str,
        dependencies: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish process analysis completed event.

        Args:
            process_id: Business process identifier
            impact_data: Impact analysis results (financial, operational, reputational)
            tenant_id: Tenant identifier
            dependencies: List of dependent processes/systems
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await bia_publisher.publish_process_analyzed(
                process_id=456,
                impact_data={
                    "financial_impact": 50000,
                    "operational_impact": "HIGH",
                    "reputational_impact": "MEDIUM"
                },
                dependencies=["process-123", "system-789"],
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "process_id": process_id,
                "impact_data": impact_data,
                "dependencies": dependencies or [],
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("bia.process_analyzed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish bia.process_analyzed event: {e}", exc_info=True)
            return False


class WorkflowEventPublisher:
    """
    Workflow management domain event publisher.

    Publishes events related to workflow lifecycle, state transitions,
    milestones, and action execution.
    """

    async def publish_workflow_started(
        self,
        workflow_id: int,
        workflow_type: str,
        tenant_id: str,
        initiator_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish workflow started event.

        Args:
            workflow_id: Workflow identifier
            workflow_type: Type of workflow (BIA, RISK_ASSESSMENT, INCIDENT_RESPONSE, etc.)
            tenant_id: Tenant identifier
            initiator_id: User who initiated the workflow
            context: Workflow context data
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await workflow_publisher.publish_workflow_started(
                workflow_id=789,
                workflow_type="BIA",
                initiator_id="user-123",
                context={"department": "IT"},
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "initiator_id": initiator_id,
                "context": context or {},
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("workflow.started", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish workflow.started event: {e}", exc_info=True)
            return False

    async def publish_workflow_state_changed(
        self,
        workflow_id: int,
        from_state: str,
        to_state: str,
        tenant_id: str,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish workflow state transition event.

        Args:
            workflow_id: Workflow identifier
            from_state: Previous state
            to_state: New state
            tenant_id: Tenant identifier
            changed_by: User who triggered the state change
            reason: Reason for state change
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
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
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "workflow_id": workflow_id,
                "from_state": from_state,
                "to_state": to_state,
                "changed_by": changed_by,
                "reason": reason,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("workflow.state_changed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish workflow.state_changed event: {e}", exc_info=True)
            return False

    async def publish_workflow_completed(
        self,
        workflow_id: int,
        duration_days: float,
        outcome: str,
        tenant_id: str,
        completion_metrics: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish workflow completion event.

        Args:
            workflow_id: Workflow identifier
            duration_days: Workflow duration in days
            outcome: Workflow outcome (SUCCESS, PARTIAL, FAILED)
            tenant_id: Tenant identifier
            completion_metrics: Metrics about workflow completion
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await workflow_publisher.publish_workflow_completed(
                workflow_id=789,
                duration_days=5.5,
                outcome="SUCCESS",
                completion_metrics={
                    "tasks_completed": 15,
                    "quality_score": 9.2
                },
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "workflow_id": workflow_id,
                "duration_days": duration_days,
                "outcome": outcome,
                "completion_metrics": completion_metrics or {},
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("workflow.completed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish workflow.completed event: {e}", exc_info=True)
            return False

    async def publish_workflow_failed(
        self,
        workflow_id: int,
        error: str,
        tenant_id: str,
        error_details: Optional[Dict[str, Any]] = None,
        recovery_actions: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish workflow failure event.

        Args:
            workflow_id: Workflow identifier
            error: Error description
            tenant_id: Tenant identifier
            error_details: Detailed error information
            recovery_actions: Suggested recovery actions
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await workflow_publisher.publish_workflow_failed(
                workflow_id=789,
                error="Database connection timeout",
                error_details={"code": "DB_TIMEOUT", "retry_count": 3},
                recovery_actions=["Check database connectivity", "Retry workflow"],
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "workflow_id": workflow_id,
                "error": error,
                "error_details": error_details or {},
                "recovery_actions": recovery_actions or [],
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("workflow.failed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish workflow.failed event: {e}", exc_info=True)
            return False

    async def publish_milestone_reached(
        self,
        workflow_id: int,
        milestone: str,
        tenant_id: str,
        milestone_data: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish workflow milestone reached event.

        Args:
            workflow_id: Workflow identifier
            milestone: Milestone name
            tenant_id: Tenant identifier
            milestone_data: Data associated with milestone
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await workflow_publisher.publish_milestone_reached(
                workflow_id=789,
                milestone="IMPACT_ANALYSIS_COMPLETE",
                milestone_data={"completion_percentage": 50},
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "workflow_id": workflow_id,
                "milestone": milestone,
                "milestone_data": milestone_data or {},
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("workflow.milestone_reached", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish workflow.milestone_reached event: {e}", exc_info=True)
            return False

    async def publish_action_executed(
        self,
        workflow_id: int,
        action_type: str,
        result: str,
        tenant_id: str,
        action_details: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish workflow action execution event.

        Args:
            workflow_id: Workflow identifier
            action_type: Type of action executed
            result: Action execution result (SUCCESS, FAILED, PENDING)
            tenant_id: Tenant identifier
            action_details: Details about the action
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await workflow_publisher.publish_action_executed(
                workflow_id=789,
                action_type="SEND_NOTIFICATION",
                result="SUCCESS",
                action_details={"recipients": 5, "channel": "email"},
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "workflow_id": workflow_id,
                "action_type": action_type,
                "result": result,
                "action_details": action_details or {},
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("workflow.action_executed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish workflow.action_executed event: {e}", exc_info=True)
            return False


class RiskEventPublisher:
    """
    Risk management domain event publisher.

    Publishes events related to risk identification, assessment,
    scoring, and mitigation.
    """

    async def publish_risk_identified(
        self,
        risk_id: int,
        risk_type: str,
        severity: str,
        tenant_id: str,
        description: Optional[str] = None,
        impact_areas: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish risk identification event.

        Args:
            risk_id: Risk identifier
            risk_type: Type of risk (OPERATIONAL, STRATEGIC, FINANCIAL, COMPLIANCE, etc.)
            severity: Risk severity (CRITICAL, HIGH, MEDIUM, LOW)
            tenant_id: Tenant identifier
            description: Risk description
            impact_areas: Affected areas/departments
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await risk_publisher.publish_risk_identified(
                risk_id=123,
                risk_type="OPERATIONAL",
                severity="HIGH",
                description="Critical supplier dependency",
                impact_areas=["SUPPLY_CHAIN", "PRODUCTION"],
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "risk_id": risk_id,
                "risk_type": risk_type,
                "severity": severity,
                "description": description,
                "impact_areas": impact_areas or [],
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("risk.identified", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish risk.identified event: {e}", exc_info=True)
            return False

    async def publish_risk_score_changed(
        self,
        risk_id: int,
        old_score: float,
        new_score: float,
        tenant_id: str,
        reason: Optional[str] = None,
        changed_by: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish risk score change event.

        Args:
            risk_id: Risk identifier
            old_score: Previous risk score
            new_score: New risk score
            tenant_id: Tenant identifier
            reason: Reason for score change
            changed_by: User who changed the score
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await risk_publisher.publish_risk_score_changed(
                risk_id=123,
                old_score=7.5,
                new_score=5.0,
                reason="Mitigation controls implemented",
                changed_by="user-456",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "risk_id": risk_id,
                "old_score": old_score,
                "new_score": new_score,
                "score_delta": new_score - old_score,
                "reason": reason,
                "changed_by": changed_by,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("risk.score_changed", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish risk.score_changed event: {e}", exc_info=True)
            return False

    async def publish_risk_mitigated(
        self,
        risk_id: int,
        mitigation_strategy: str,
        tenant_id: str,
        mitigation_details: Optional[Dict[str, Any]] = None,
        residual_risk: Optional[float] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish risk mitigation event.

        Args:
            risk_id: Risk identifier
            mitigation_strategy: Mitigation strategy applied
            tenant_id: Tenant identifier
            mitigation_details: Details about mitigation measures
            residual_risk: Residual risk score after mitigation
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await risk_publisher.publish_risk_mitigated(
                risk_id=123,
                mitigation_strategy="DIVERSIFY_SUPPLIERS",
                mitigation_details={
                    "new_suppliers": 3,
                    "cost_increase": 5
                },
                residual_risk=2.5,
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "risk_id": risk_id,
                "mitigation_strategy": mitigation_strategy,
                "mitigation_details": mitigation_details or {},
                "residual_risk": residual_risk,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("risk.mitigated", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish risk.mitigated event: {e}", exc_info=True)
            return False

    async def publish_risk_accepted(
        self,
        risk_id: int,
        approver_id: str,
        tenant_id: str,
        acceptance_rationale: Optional[str] = None,
        review_date: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish risk acceptance event.

        Args:
            risk_id: Risk identifier
            approver_id: User who accepted the risk
            tenant_id: Tenant identifier
            acceptance_rationale: Reason for accepting the risk
            review_date: Next review date (ISO format)
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await risk_publisher.publish_risk_accepted(
                risk_id=123,
                approver_id="executive-456",
                acceptance_rationale="Cost of mitigation exceeds potential impact",
                review_date="2025-12-31",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "risk_id": risk_id,
                "approver_id": approver_id,
                "acceptance_rationale": acceptance_rationale,
                "review_date": review_date,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("risk.accepted", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish risk.accepted event: {e}", exc_info=True)
            return False


class IncidentEventPublisher:
    """
    Incident management domain event publisher.

    Publishes events related to incident lifecycle, escalation,
    resolution, and pattern detection.
    """

    async def publish_incident_opened(
        self,
        incident_id: int,
        incident_type: str,
        severity: str,
        tenant_id: str,
        description: Optional[str] = None,
        affected_services: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish incident opened event.

        Args:
            incident_id: Incident identifier
            incident_type: Type of incident (OUTAGE, BREACH, DISASTER, etc.)
            severity: Incident severity (SEV1, SEV2, SEV3, SEV4)
            tenant_id: Tenant identifier
            description: Incident description
            affected_services: List of affected services/systems
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await incident_publisher.publish_incident_opened(
                incident_id=789,
                incident_type="OUTAGE",
                severity="SEV1",
                description="Database primary node failure",
                affected_services=["payment-api", "user-service"],
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "incident_id": incident_id,
                "incident_type": incident_type,
                "severity": severity,
                "description": description,
                "affected_services": affected_services or [],
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("incident.opened", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish incident.opened event: {e}", exc_info=True)
            return False

    async def publish_incident_escalated(
        self,
        incident_id: int,
        from_level: str,
        to_level: str,
        tenant_id: str,
        escalation_reason: Optional[str] = None,
        escalated_by: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish incident escalation event.

        Args:
            incident_id: Incident identifier
            from_level: Previous escalation level
            to_level: New escalation level
            tenant_id: Tenant identifier
            escalation_reason: Reason for escalation
            escalated_by: User who escalated the incident
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await incident_publisher.publish_incident_escalated(
                incident_id=789,
                from_level="L1_SUPPORT",
                to_level="L2_ENGINEERING",
                escalation_reason="Requires database expertise",
                escalated_by="support-123",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "incident_id": incident_id,
                "from_level": from_level,
                "to_level": to_level,
                "escalation_reason": escalation_reason,
                "escalated_by": escalated_by,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("incident.escalated", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish incident.escalated event: {e}", exc_info=True)
            return False

    async def publish_incident_resolved(
        self,
        incident_id: int,
        resolution_time_hours: float,
        tenant_id: str,
        resolution_summary: Optional[str] = None,
        root_cause: Optional[str] = None,
        resolved_by: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish incident resolution event.

        Args:
            incident_id: Incident identifier
            resolution_time_hours: Time to resolve in hours
            tenant_id: Tenant identifier
            resolution_summary: Summary of resolution
            root_cause: Identified root cause
            resolved_by: User who resolved the incident
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await incident_publisher.publish_incident_resolved(
                incident_id=789,
                resolution_time_hours=2.5,
                resolution_summary="Failover to secondary database completed",
                root_cause="Hardware failure on primary node",
                resolved_by="engineer-456",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "incident_id": incident_id,
                "resolution_time_hours": resolution_time_hours,
                "resolution_summary": resolution_summary,
                "root_cause": root_cause,
                "resolved_by": resolved_by,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("incident.resolved", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish incident.resolved event: {e}", exc_info=True)
            return False

    async def publish_incident_pattern_detected(
        self,
        pattern_type: str,
        incidents_count: int,
        tenant_id: str,
        pattern_details: Optional[Dict[str, Any]] = None,
        recommendation: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish incident pattern detection event.

        Args:
            pattern_type: Type of pattern detected
            incidents_count: Number of incidents in pattern
            tenant_id: Tenant identifier
            pattern_details: Details about the pattern
            recommendation: Recommended action
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await incident_publisher.publish_incident_pattern_detected(
                pattern_type="RECURRING_OUTAGE",
                incidents_count=5,
                pattern_details={
                    "frequency": "every_monday",
                    "affected_component": "database",
                    "time_pattern": "06:00-07:00"
                },
                recommendation="Schedule maintenance outside peak hours",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "pattern_type": pattern_type,
                "incidents_count": incidents_count,
                "pattern_details": pattern_details or {},
                "recommendation": recommendation,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("incident.pattern_detected", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish incident.pattern_detected event: {e}", exc_info=True)
            return False


class ComplianceEventPublisher:
    """
    Compliance management domain event publisher.

    Publishes events related to audits, control validation,
    gap identification, and compliance certification.
    """

    async def publish_audit_started(
        self,
        audit_id: int,
        standard: str,
        scope: str,
        tenant_id: str,
        auditor_id: Optional[str] = None,
        planned_completion: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish audit started event.

        Args:
            audit_id: Audit identifier
            standard: Compliance standard (ISO22301, ISO27001, SOC2, etc.)
            scope: Audit scope description
            tenant_id: Tenant identifier
            auditor_id: Auditor identifier
            planned_completion: Planned completion date (ISO format)
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await compliance_publisher.publish_audit_started(
                audit_id=123,
                standard="ISO22301",
                scope="Business Continuity Management System",
                auditor_id="auditor-456",
                planned_completion="2025-12-31",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "audit_id": audit_id,
                "standard": standard,
                "scope": scope,
                "auditor_id": auditor_id,
                "planned_completion": planned_completion,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("compliance.audit_started", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish compliance.audit_started event: {e}", exc_info=True)
            return False

    async def publish_control_validated(
        self,
        control_id: int,
        validation_result: str,
        tenant_id: str,
        validator_id: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        findings: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish control validation event.

        Args:
            control_id: Control identifier
            validation_result: Validation result (PASSED, FAILED, PARTIAL, NOT_APPLICABLE)
            tenant_id: Tenant identifier
            validator_id: Validator identifier
            evidence: List of evidence documents/references
            findings: Validation findings
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await compliance_publisher.publish_control_validated(
                control_id=456,
                validation_result="PASSED",
                validator_id="auditor-123",
                evidence=["doc-789", "screenshot-012"],
                findings="Control is operating effectively",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "control_id": control_id,
                "validation_result": validation_result,
                "validator_id": validator_id,
                "evidence": evidence or [],
                "findings": findings,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("compliance.control_validated", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish compliance.control_validated event: {e}", exc_info=True)
            return False

    async def publish_gap_identified(
        self,
        gap_id: int,
        severity: str,
        requirement: str,
        tenant_id: str,
        gap_description: Optional[str] = None,
        remediation_plan: Optional[str] = None,
        target_date: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish compliance gap identification event.

        Args:
            gap_id: Gap identifier
            severity: Gap severity (CRITICAL, HIGH, MEDIUM, LOW)
            requirement: Compliance requirement not met
            tenant_id: Tenant identifier
            gap_description: Description of the gap
            remediation_plan: Plan to address the gap
            target_date: Target remediation date (ISO format)
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await compliance_publisher.publish_gap_identified(
                gap_id=789,
                severity="HIGH",
                requirement="ISO22301-8.4.1",
                gap_description="BIA documentation incomplete",
                remediation_plan="Complete BIA for all critical processes",
                target_date="2025-11-30",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "gap_id": gap_id,
                "severity": severity,
                "requirement": requirement,
                "gap_description": gap_description,
                "remediation_plan": remediation_plan,
                "target_date": target_date,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("compliance.gap_identified", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish compliance.gap_identified event: {e}", exc_info=True)
            return False

    async def publish_compliance_achieved(
        self,
        standard: str,
        certification_date: str,
        tenant_id: str,
        certification_body: Optional[str] = None,
        certificate_id: Optional[str] = None,
        expiry_date: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish compliance achievement event.

        Args:
            standard: Compliance standard achieved
            certification_date: Certification date (ISO format)
            tenant_id: Tenant identifier
            certification_body: Certifying organization
            certificate_id: Certificate identifier
            expiry_date: Certificate expiry date (ISO format)
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await compliance_publisher.publish_compliance_achieved(
                standard="ISO22301",
                certification_date="2025-10-07",
                certification_body="BSI Group",
                certificate_id="CERT-2025-123456",
                expiry_date="2028-10-07",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "standard": standard,
                "certification_date": certification_date,
                "certification_body": certification_body,
                "certificate_id": certificate_id,
                "expiry_date": expiry_date,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("compliance.achieved", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish compliance.achieved event: {e}", exc_info=True)
            return False


class CommunityEventPublisher:
    """
    Community intelligence domain event publisher.

    Publishes events related to case submissions, peer review,
    and knowledge sharing.
    """

    async def publish_case_submitted(
        self,
        case_id: int,
        contributor_id: str,
        module: str,
        tenant_id: str,
        case_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish case submission event.

        Args:
            case_id: Case identifier
            contributor_id: User who submitted the case
            module: BCM module (BIA, RISK, INCIDENT, COMPLIANCE, etc.)
            tenant_id: Tenant identifier
            case_type: Type of case (BEST_PRACTICE, LESSON_LEARNED, TEMPLATE, etc.)
            tags: Case tags for categorization
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await community_publisher.publish_case_submitted(
                case_id=123,
                contributor_id="user-456",
                module="BIA",
                case_type="BEST_PRACTICE",
                tags=["healthcare", "critical-processes"],
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "case_id": case_id,
                "contributor_id": contributor_id,
                "module": module,
                "case_type": case_type,
                "tags": tags or [],
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("community.case_submitted", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish community.case_submitted event: {e}", exc_info=True)
            return False

    async def publish_review_assigned(
        self,
        case_id: int,
        reviewer_id: str,
        tenant_id: str,
        assignment_reason: Optional[str] = None,
        due_date: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish review assignment event.

        Args:
            case_id: Case identifier
            reviewer_id: Assigned reviewer identifier
            tenant_id: Tenant identifier
            assignment_reason: Reason for assignment
            due_date: Review due date (ISO format)
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await community_publisher.publish_review_assigned(
                case_id=123,
                reviewer_id="expert-789",
                assignment_reason="Healthcare domain expertise",
                due_date="2025-10-14",
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "case_id": case_id,
                "reviewer_id": reviewer_id,
                "assignment_reason": assignment_reason,
                "due_date": due_date,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("community.review_assigned", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish community.review_assigned event: {e}", exc_info=True)
            return False

    async def publish_case_approved(
        self,
        case_id: int,
        final_score: float,
        tenant_id: str,
        approved_by: Optional[str] = None,
        review_comments: Optional[str] = None,
        quality_metrics: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish case approval event.

        Args:
            case_id: Case identifier
            final_score: Final quality score (0-10)
            tenant_id: Tenant identifier
            approved_by: Approver identifier
            review_comments: Review comments
            quality_metrics: Quality assessment metrics
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await community_publisher.publish_case_approved(
                case_id=123,
                final_score=8.5,
                approved_by="expert-789",
                review_comments="Excellent best practice documentation",
                quality_metrics={
                    "completeness": 9.0,
                    "clarity": 8.5,
                    "applicability": 8.0
                },
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "case_id": case_id,
                "final_score": final_score,
                "approved_by": approved_by,
                "review_comments": review_comments,
                "quality_metrics": quality_metrics or {},
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("community.case_approved", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish community.case_approved event: {e}", exc_info=True)
            return False

    async def publish_case_rejected(
        self,
        case_id: int,
        reasons: List[str],
        tenant_id: str,
        rejected_by: Optional[str] = None,
        feedback: Optional[str] = None,
        resubmission_allowed: bool = True,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish case rejection event.

        Args:
            case_id: Case identifier
            reasons: List of rejection reasons
            tenant_id: Tenant identifier
            rejected_by: Rejector identifier
            feedback: Detailed feedback for improvement
            resubmission_allowed: Whether resubmission is allowed
            additional_data: Additional event data

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await community_publisher.publish_case_rejected(
                case_id=123,
                reasons=["INCOMPLETE_DOCUMENTATION", "MISSING_EXAMPLES"],
                rejected_by="expert-789",
                feedback="Please add more detailed examples and references",
                resubmission_allowed=True,
                tenant_id="tenant-789"
            )
            ```
        """
        try:
            eventbus = get_eventbus()
            event_data = {
                "case_id": case_id,
                "reasons": reasons,
                "rejected_by": rejected_by,
                "feedback": feedback,
                "resubmission_allowed": resubmission_allowed,
                "tenant_id": tenant_id,
                **(additional_data or {})
            }
            return await eventbus.publish("community.case_rejected", event_data, tenant_id)
        except Exception as e:
            logger.error(f"Failed to publish community.case_rejected event: {e}", exc_info=True)
            return False
