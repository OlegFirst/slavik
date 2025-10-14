"""
Infrastructure Decision Center (Phase 1.1)
==========================================

Governance layer for infrastructure coordination.

Provides:
- Decision authority for auto-recovery and optimization
- Policy-based decision making
- Escalation to human operators
- Manual approval workflows
- Full audit trail for ISO 22301 compliance

Features:
- decide_recovery_action() - decides whether to allow auto-recovery
- decide_optimization_action() - decides whether to apply optimization
- escalate() - escalates to human operators
- approve_action() - manual approval workflow
- check_policy_compliance() - validates against policies
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from infrastructure.policy_engine.decision_models import (
    Decision,
    DecisionType,
    DecisionOutcome,
    EscalationRequest,
    EscalationStatus,
    ApprovalRequest,
    ApprovalStatus
)
from infrastructure.policy_engine.policy_engine import PolicyEngine
from infrastructure.policy_engine.audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class InfrastructureDecisionCenter:
    """
    Infrastructure Decision Center

    Central governance layer for infrastructure decisions.
    Enforces policies, manages approvals, and maintains audit trail.
    """

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        audit_logger: Optional[AuditLogger] = None,
        eventbus=None,
        db_session_factory=None
    ):
        """
        Initialize Decision Center

        Args:
            policy_engine: PolicyEngine instance (creates if None)
            audit_logger: AuditLogger instance (creates if None)
            eventbus: EventBus instance for notifications
            db_session_factory: Database session factory
        """
        self.policy_engine = policy_engine or PolicyEngine()
        self.audit_logger = audit_logger or AuditLogger(db_session_factory=db_session_factory)
        self.eventbus = eventbus
        self.db_session_factory = db_session_factory

        # Load policies only if policy_engine was not provided or not loaded
        if policy_engine is None or policy_engine._config is None:
            if self.policy_engine.policy_file:
                self.policy_engine.load_policies()
            else:
                logger.warning("Decision Center initialized without policies - provide policy_engine or policy_file")

        # In-memory stores
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.active_escalations: Dict[str, EscalationRequest] = {}
        self.decision_history: List[Decision] = []

        # Statistics
        self.stats = {
            'total_decisions': 0,
            'approved_decisions': 0,
            'rejected_decisions': 0,
            'escalated_decisions': 0,
            'auto_approved': 0,
            'manual_approved': 0
        }

        logger.info("✅ InfrastructureDecisionCenter initialized")

    async def decide_recovery_action(
        self,
        service_name: str,
        action_type: str,
        trigger_event_id: Optional[str] = None,
        trigger_data: Optional[Dict[str, Any]] = None,
        current_attempt: int = 1
    ) -> Tuple[Decision, bool]:
        """
        Decide whether to allow auto-recovery action

        Args:
            service_name: Name of the service
            action_type: Type of recovery action (restart, failover, etc.)
            trigger_event_id: ID of the triggering event
            trigger_data: Data from the triggering event
            current_attempt: Current recovery attempt number

        Returns:
            Tuple of (Decision, can_proceed: bool)
        """
        self.stats['total_decisions'] += 1

        # Create decision record
        decision = Decision(
            decision_type=DecisionType.RECOVERY,
            service_name=service_name,
            action_type=action_type,
            trigger_event_id=trigger_event_id,
            trigger_data=trigger_data or {},
            parameters={'attempt': current_attempt}
        )

        logger.info(f"🔍 Deciding recovery action: {service_name} - {action_type} (attempt {current_attempt})")

        try:
            # Check business hours
            is_business_hours = self.policy_engine.is_business_hours()

            # Create policy context (as dict)
            context = {
                'service_name': service_name,
                'action_type': action_type,
                'current_attempt': current_attempt,
                'is_business_hours': is_business_hours
            }

            # Check policy compliance
            compliance_result = self.policy_engine.check_policy_compliance(context)

            decision.policy_reference = compliance_result.get('policy_reference')
            decision.reasoning = compliance_result['reason']

            # Decision logic
            if not compliance_result['compliant']:
                # Policy violation - reject
                decision.outcome = DecisionOutcome.REJECTED
                decision.decided_at = datetime.utcnow()
                self.stats['rejected_decisions'] += 1

                logger.warning(f"❌ Recovery REJECTED for {service_name}: {decision.reasoning}")

                # Check if should escalate
                if compliance_result.get('requires_escalation', False):
                    await self._create_escalation(decision, "policy_violation")

            elif compliance_result.get('requires_approval', False):
                # Requires manual approval
                decision.outcome = DecisionOutcome.PENDING
                decision.requires_approval = True
                self.stats['manual_approved'] += 1

                logger.info(f"⏸️  Recovery PENDING for {service_name}: requires approval")

                # Create approval request
                await self._create_approval_request(decision)

                # Escalate for visibility
                if compliance_result.get('requires_escalation', False):
                    await self._create_escalation(decision, "approval_required")

            elif compliance_result.get('requires_escalation', False):
                # Escalate but allow action
                decision.outcome = DecisionOutcome.APPROVED
                decision.decided_at = datetime.utcnow()
                decision.confidence_score = 0.7  # Lower confidence due to escalation
                self.stats['approved_decisions'] += 1
                self.stats['auto_approved'] += 1

                logger.info(f"✅ Recovery APPROVED for {service_name} with escalation: {decision.reasoning}")

                # Create escalation for monitoring
                await self._create_escalation(decision, "critical_service_alert")

            else:
                # Approve action
                decision.outcome = DecisionOutcome.APPROVED
                decision.decided_at = datetime.utcnow()
                decision.confidence_score = 1.0
                self.stats['approved_decisions'] += 1
                self.stats['auto_approved'] += 1

                logger.info(f"✅ Recovery APPROVED for {service_name}: {decision.reasoning}")

        except Exception as e:
            logger.error(f"❌ Error deciding recovery action: {e}")
            decision.outcome = DecisionOutcome.REJECTED
            decision.reasoning = f"Decision error: {str(e)}"
            decision.decided_at = datetime.utcnow()
            self.stats['rejected_decisions'] += 1

        # Audit log
        await self.audit_logger.log_decision(decision)

        # Store in history
        self.decision_history.append(decision)

        # Publish decision event
        await self._publish_decision_event(decision)

        # Return decision and whether can proceed
        can_proceed = decision.outcome == DecisionOutcome.APPROVED
        return decision, can_proceed

    async def decide_optimization_action(
        self,
        service_name: str,
        action_type: str,
        recommendation: Dict[str, Any],
        trigger_event_id: Optional[str] = None
    ) -> Tuple[Decision, bool]:
        """
        Decide whether to apply optimization recommendation

        Args:
            service_name: Name of the service
            action_type: Type of optimization (scale_up, scale_down, optimize)
            recommendation: Optimization recommendation details
            trigger_event_id: ID of the triggering event

        Returns:
            Tuple of (Decision, can_proceed: bool)
        """
        self.stats['total_decisions'] += 1

        # Create decision record
        decision = Decision(
            decision_type=DecisionType.OPTIMIZATION,
            service_name=service_name,
            action_type=action_type,
            trigger_event_id=trigger_event_id,
            trigger_data=recommendation,
            parameters=recommendation
        )

        logger.info(f"🔍 Deciding optimization action: {service_name} - {action_type}")

        try:
            # Get optimization policy
            opt_policy = self.policy_engine.get_optimization_policy(service_name)

            # Check if action requires approval
            approval_policy = self.policy_engine.get_approval_policy(action_type)
            requires_approval = approval_policy.get('requires_approval', False)

            # Check utilization vs thresholds
            thresholds = self.policy_engine.get_thresholds()
            current_utilization = recommendation.get('current_utilization', 0)

            # Decision reasoning
            reasoning_parts = []

            # Check if service allows auto-optimization
            service_config = opt_policy.get('services', {}).get(service_name, {})
            allow_auto_optimize = service_config.get('allow_optimization', True)

            if not allow_auto_optimize:
                decision.outcome = DecisionOutcome.REJECTED
                decision.reasoning = f"Service {service_name} does not allow automatic optimization"
                self.stats['rejected_decisions'] += 1

            elif requires_approval:
                decision.outcome = DecisionOutcome.PENDING
                decision.requires_approval = True
                decision.reasoning = f"Action {action_type} requires manual approval per policy"
                self.stats['manual_approved'] += 1

                # Create approval request
                await self._create_approval_request(decision)

            else:
                # Auto-approve optimization
                decision.outcome = DecisionOutcome.APPROVED
                decision.reasoning = f"Optimization approved: {action_type} for {service_name}"
                decision.confidence_score = 0.9
                self.stats['approved_decisions'] += 1
                self.stats['auto_approved'] += 1

            decision.decided_at = datetime.utcnow()
            decision.policy_reference = f"optimization/{service_name}/{action_type}"

            logger.info(f"{'✅' if decision.outcome == DecisionOutcome.APPROVED else '❌'} Optimization {decision.outcome.value.upper()} for {service_name}: {decision.reasoning}")

        except Exception as e:
            logger.error(f"❌ Error deciding optimization action: {e}")
            decision.outcome = DecisionOutcome.REJECTED
            decision.reasoning = f"Decision error: {str(e)}"
            decision.decided_at = datetime.utcnow()
            self.stats['rejected_decisions'] += 1

        # Audit log
        await self.audit_logger.log_decision(decision)

        # Store in history
        self.decision_history.append(decision)

        # Publish decision event
        await self._publish_decision_event(decision)

        # Return decision and whether can proceed
        can_proceed = decision.outcome == DecisionOutcome.APPROVED
        return decision, can_proceed

    async def escalate(
        self,
        service_name: str,
        reason: str,
        decision_id: Optional[str] = None,
        severity: str = "medium",
        context_data: Optional[Dict[str, Any]] = None
    ) -> EscalationRequest:
        """
        Escalate issue to human operators

        Args:
            service_name: Name of the service
            reason: Reason for escalation
            decision_id: Related decision ID
            severity: Severity level (low, medium, high, critical)
            context_data: Additional context

        Returns:
            EscalationRequest
        """
        self.stats['escalated_decisions'] += 1

        # Create escalation request
        escalation = EscalationRequest(
            decision_id=decision_id or "",
            service_name=service_name,
            escalation_type="infrastructure_issue",
            reason=reason,
            severity=severity,
            context_data=context_data or {},
            status=EscalationStatus.PENDING
        )

        # Get escalation policy
        policy = self.policy_engine.get_escalation_policy(severity)

        # Assign to teams
        teams = policy.get('teams', ['ops_team'])
        escalation.assigned_team = teams[0] if teams else 'ops_team'

        # Store escalation
        self.active_escalations[escalation.escalation_id] = escalation

        logger.warning(f"🚨 ESCALATION created for {service_name}: {reason} (severity: {severity})")

        # Audit log
        await self.audit_logger.log_escalation(escalation)

        # Send notifications
        await self._send_escalation_notifications(escalation, policy)

        # Publish escalation event
        await self._publish_escalation_event(escalation)

        return escalation

    async def approve_action(
        self,
        approval_id: str,
        approved_by: str,
        approved: bool,
        comment: Optional[str] = None
    ) -> bool:
        """
        Process manual approval for a pending action

        Args:
            approval_id: ID of the approval request
            approved_by: User who approved/rejected
            approved: Whether approved or rejected
            comment: Optional comment

        Returns:
            bool: True if action can now proceed
        """
        approval = self.pending_approvals.get(approval_id)
        if not approval:
            logger.error(f"Approval request {approval_id} not found")
            return False

        # Add approver decision
        approval.add_approver_decision(approved_by, approved, comment)

        # Check if approved
        if approved and approval.is_approved():
            approval.status = ApprovalStatus.APPROVED
            approval.approved_at = datetime.utcnow()
            approval.final_decision = "approved"
            approval.decision_by = approved_by
            approval.decision_comment = comment

            logger.info(f"✅ Approval {approval_id} APPROVED by {approved_by}")

            # Update related decision
            for decision in self.decision_history:
                if decision.decision_id == approval.decision_id:
                    decision.outcome = DecisionOutcome.APPROVED
                    decision.approved_by = approved_by
                    decision.approval_timestamp = datetime.utcnow()
                    break

            # Audit log
            await self.audit_logger.log_approval(approval, "approval_granted")

            return True

        elif not approved:
            approval.status = ApprovalStatus.REJECTED
            approval.rejected_at = datetime.utcnow()
            approval.final_decision = "rejected"
            approval.decision_by = approved_by
            approval.decision_comment = comment

            logger.info(f"❌ Approval {approval_id} REJECTED by {approved_by}")

            # Update related decision
            for decision in self.decision_history:
                if decision.decision_id == approval.decision_id:
                    decision.outcome = DecisionOutcome.REJECTED
                    break

            # Audit log
            await self.audit_logger.log_approval(approval, "approval_rejected")

            return False

        else:
            logger.info(f"⏸️  Approval {approval_id} pending additional approvers")
            return False

    async def check_policy_compliance(
        self,
        service_name: str,
        action_type: str,
        current_attempt: int = 1
    ) -> Dict[str, Any]:
        """
        Check if an action complies with policy

        Args:
            service_name: Name of the service
            action_type: Type of action
            current_attempt: Current attempt number

        Returns:
            Dict with compliance result
        """
        context = {
            'service_name': service_name,
            'action_type': action_type,
            'current_attempt': current_attempt,
            'is_business_hours': self.policy_engine.is_business_hours()
        }

        return self.policy_engine.check_policy_compliance(context)

    async def _create_escalation(
        self,
        decision: Decision,
        escalation_type: str
    ) -> None:
        """Create escalation for a decision"""
        # Determine severity based on service
        policy = self.policy_engine.get_recovery_policy(decision.service_name)
        is_critical = policy.get('critical_service', False)
        severity = "critical" if is_critical else "high"

        await self.escalate(
            service_name=decision.service_name,
            reason=decision.reasoning,
            decision_id=decision.decision_id,
            severity=severity,
            context_data={
                'decision_type': decision.decision_type.value,
                'action_type': decision.action_type,
                'trigger_data': decision.trigger_data
            }
        )

    async def _create_approval_request(
        self,
        decision: Decision
    ) -> None:
        """Create approval request for a decision"""
        approval = ApprovalRequest(
            decision_id=decision.decision_id,
            service_name=decision.service_name,
            action_type=decision.action_type or "",
            requested_action=f"{decision.action_type} for {decision.service_name}",
            justification=decision.reasoning,
            impact_assessment="Service recovery action requires approval",
            rollback_plan="Auto-recovery will stop if action fails",
            status=ApprovalStatus.PENDING
        )

        # Get approval policy
        approval_policy = self.policy_engine.get_approval_policy(decision.action_type or "")
        approval.required_approvers = approval_policy.get('allowed_approvers', [])
        expires_in = approval_policy.get('expires_in', 3600)
        approval.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Store approval request
        self.pending_approvals[approval.approval_id] = approval

        logger.info(f"📋 Approval request created: {approval.approval_id} for {decision.service_name}")

        # Audit log
        await self.audit_logger.log_approval(approval, "approval_requested")

    async def _send_escalation_notifications(
        self,
        escalation: EscalationRequest,
        policy: Dict[str, Any]
    ) -> None:
        """Send notifications for escalation"""
        if not self.eventbus:
            logger.warning("EventBus not configured - skipping notifications")
            return

        # Get notification channels
        channels = policy.get('channels', ['slack_alerts'])

        # Publish notification event
        from infrastructure.eventbus import Event
        await self.eventbus.publish(Event.create(
            event_type='infrastructure.escalation.notification',
            data={
                'escalation_id': escalation.escalation_id,
                'service_name': escalation.service_name,
                'severity': escalation.severity,
                'reason': escalation.reason,
                'assigned_team': escalation.assigned_team,
                'channels': channels
            },
            source='decision_center',
            tenant_id='system',
            correlation_id=escalation.correlation_id
        ))

    async def _publish_decision_event(self, decision: Decision) -> None:
        """Publish decision event to EventBus"""
        if not self.eventbus:
            return

        from infrastructure.eventbus import Event
        await self.eventbus.publish(Event.create(
            event_type=f'infrastructure.decision.{decision.outcome.value}',
            data=decision.to_dict(),
            source='decision_center',
            tenant_id='system',
            correlation_id=decision.correlation_id
        ))

    async def _publish_escalation_event(self, escalation: EscalationRequest) -> None:
        """Publish escalation event to EventBus"""
        if not self.eventbus:
            return

        from infrastructure.eventbus import Event
        await self.eventbus.publish(Event.create(
            event_type='infrastructure.escalation.created',
            data=escalation.to_dict(),
            source='decision_center',
            tenant_id='system',
            correlation_id=escalation.correlation_id
        ))

    async def get_stats(self) -> Dict[str, Any]:
        """Get Decision Center statistics"""
        return {
            **self.stats,
            'pending_approvals': len(self.pending_approvals),
            'active_escalations': len(self.active_escalations),
            'decision_history_size': len(self.decision_history),
            'approval_rate': (self.stats['approved_decisions'] / self.stats['total_decisions'] * 100)
                if self.stats['total_decisions'] > 0 else 0,
            'automation_rate': (self.stats['auto_approved'] / self.stats['approved_decisions'] * 100)
                if self.stats['approved_decisions'] > 0 else 0
        }

    async def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get list of pending approvals"""
        return [
            approval for approval in self.pending_approvals.values()
            if approval.status == ApprovalStatus.PENDING
        ]

    async def get_active_escalations(self) -> List[EscalationRequest]:
        """Get list of active escalations"""
        return [
            escalation for escalation in self.active_escalations.values()
            if escalation.status == EscalationStatus.PENDING
        ]
