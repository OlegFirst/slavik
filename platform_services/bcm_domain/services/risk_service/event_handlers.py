"""
Risk Service Event Handlers
============================

Event-driven choreography for Risk service.
Subscribes to BIA events and publishes risk-related events.

Event Flow:
  BIA Assessment Completed → Auto-suggest Risks → Risk Assessment Created
  Risk Assessment Completed → Auto-create BC Plans
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

# Import eventbus from infrastructure
import sys
sys.path.append('/Users/MD/AI-Platform-ISO/infrastructure')
from eventbus import Event, EventPriority, create_eventbus

logger = logging.getLogger(__name__)


class RiskEventHandlers:
    """
    Event handlers for Risk service.

    Subscribes to:
    - bia.assessment.completed: Auto-generate risk suggestions
    - bia.criticality.changed: Re-assess related risks
    - bia.critical.process.identified: Create high-priority risk assessment

    Publishes:
    - risk.suggestion.generated: When AI suggests risks based on BIA
    - risk.assessment.created: When risk assessment is created
    - risk.assessment.completed: When risk assessment is done
    - risk.severity.changed: When risk severity changes
    """

    def __init__(self, eventbus=None, risk_service=None):
        self.eventbus = eventbus or create_eventbus('redis')
        self.risk_service = risk_service  # Injected risk service for business logic

    # ==================== SUBSCRIBERS ====================

    async def on_bia_completed(self, event: Event) -> None:
        """
        React to BIA assessment completion by auto-suggesting risks.

        This is a KEY choreography handler that implements the BIA → Risk flow.

        Args:
            event: bia.assessment.completed event
        """
        try:
            assessment_id = event.data.get('assessment_id')
            tenant_id = event.tenant_id
            processes = event.data.get('processes', [])
            critical_count = event.data.get('critical_process_count', 0)

            logger.info(
                f"Received bia.assessment.completed for assessment {assessment_id}, "
                f"analyzing {len(processes)} processes ({critical_count} critical)"
            )

            # Generate risk suggestions based on BIA data
            risk_suggestions = await self._generate_risk_suggestions_from_bia(
                processes=processes,
                tenant_id=tenant_id
            )

            if risk_suggestions:
                # Publish risk suggestions event
                await self._publish_risk_suggestions(
                    suggestions=risk_suggestions,
                    source=f"bia-assessment-{assessment_id}",
                    tenant_id=tenant_id
                )

                logger.info(
                    f"Generated {len(risk_suggestions)} risk suggestions "
                    f"from BIA assessment {assessment_id}"
                )
            else:
                logger.info(f"No risk suggestions generated from BIA assessment {assessment_id}")

        except Exception as e:
            logger.error(f"Error processing bia.assessment.completed: {e}", exc_info=True)
            # Don't re-raise - we don't want to break the event bus

    async def on_criticality_changed(self, event: Event) -> None:
        """
        React to process criticality change by re-assessing related risks.

        Args:
            event: bia.criticality.changed event
        """
        try:
            process_id = event.data.get('process_id')
            old_criticality = event.data.get('old_criticality')
            new_criticality = event.data.get('new_criticality')
            tenant_id = event.tenant_id

            logger.info(
                f"Process {process_id} criticality changed: {old_criticality} -> {new_criticality}"
            )

            # If criticality increased to critical/high, suggest immediate risk assessment
            if new_criticality in ['critical', 'high'] and old_criticality not in ['critical', 'high']:
                await self._publish_risk_suggestion_for_process(
                    process_id=process_id,
                    reason=f"Criticality escalated to {new_criticality}",
                    priority='high',
                    tenant_id=tenant_id
                )

        except Exception as e:
            logger.error(f"Error processing bia.criticality.changed: {e}", exc_info=True)

    async def on_critical_process_identified(self, event: Event) -> None:
        """
        React to critical process identification by creating risk assessment.

        Args:
            event: bia.critical.process.identified event
        """
        try:
            process_id = event.data.get('process_id')
            process_name = event.data.get('name')
            criticality_score = event.data.get('criticality_score')
            urgent = event.data.get('requires_immediate_attention', False)
            tenant_id = event.tenant_id

            logger.warning(
                f"Critical process identified: {process_name} (score: {criticality_score}, urgent: {urgent})"
            )

            # Auto-create risk suggestion with high priority
            await self._publish_risk_suggestion_for_process(
                process_id=process_id,
                process_name=process_name,
                reason=f"Critical process identified with score {criticality_score}",
                priority='critical' if urgent else 'high',
                tenant_id=tenant_id
            )

        except Exception as e:
            logger.error(f"Error processing bia.critical.process.identified: {e}", exc_info=True)

    # ==================== PUBLISHERS ====================

    async def publish_risk_assessment_created(
        self,
        assessment_id: str,
        tenant_id: str,
        name: str,
        created_by: str
    ) -> None:
        """
        Publish event when risk assessment is created.

        Args:
            assessment_id: Risk assessment identifier
            tenant_id: Tenant ID
            name: Assessment name
            created_by: User who created the assessment
        """
        event = Event.create(
            event_type='risk.assessment.created',
            data={
                'assessment_id': assessment_id,
                'name': name,
                'created_by': created_by,
                'created_at': datetime.utcnow().isoformat()
            },
            source='risk-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published risk.assessment.created for assessment {assessment_id}")

    async def publish_risk_assessment_completed(
        self,
        assessment_id: str,
        tenant_id: str,
        risks: List[Dict[str, Any]],
        high_risk_count: int,
        total_risks: int
    ) -> None:
        """
        Publish event when risk assessment is completed.

        KEY choreography event that triggers:
        - Planning service: Auto-create BC plans for high risks
        - Governance service: Update risk posture
        - Notification service: Alert stakeholders

        Args:
            assessment_id: Risk assessment identifier
            tenant_id: Tenant ID
            risks: List of identified risks with severity data
            high_risk_count: Number of high/critical risks
            total_risks: Total number of risks
        """
        # Transform risks to essential data
        risk_data = []
        for risk in risks:
            risk_data.append({
                'risk_id': str(risk.get('id', risk.get('risk_id', ''))),
                'title': risk.get('title', ''),
                'severity': risk.get('severity', ''),
                'likelihood': risk.get('likelihood', ''),
                'impact': risk.get('impact', ''),
                'risk_score': risk.get('risk_score', 0),
                'category': risk.get('category', ''),
                'related_process_id': risk.get('related_process_id', '')
            })

        event = Event.create(
            event_type='risk.assessment.completed',
            data={
                'assessment_id': assessment_id,
                'completed_at': datetime.utcnow().isoformat(),
                'risks': risk_data,
                'high_risk_count': high_risk_count,
                'total_risks': total_risks,
                'summary': {
                    'critical': sum(1 for r in risks if r.get('severity') == 'critical'),
                    'high': sum(1 for r in risks if r.get('severity') == 'high'),
                    'medium': sum(1 for r in risks if r.get('severity') == 'medium'),
                    'low': sum(1 for r in risks if r.get('severity') == 'low')
                }
            },
            source='risk-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH  # High priority for choreography
        )

        await self.eventbus.publish(event)
        logger.info(
            f"Published risk.assessment.completed for assessment {assessment_id} "
            f"with {high_risk_count} high risks"
        )

    async def publish_risk_severity_changed(
        self,
        risk_id: str,
        tenant_id: str,
        old_severity: str,
        new_severity: str,
        changed_by: str,
        reason: str = None
    ) -> None:
        """
        Publish event when risk severity changes.

        Triggers:
        - Planning service: Update BC plan priority
        - Notification service: Alert risk owner
        - Alert service: Escalate if severity increased

        Args:
            risk_id: Risk identifier
            tenant_id: Tenant ID
            old_severity: Previous severity level
            new_severity: New severity level
            changed_by: User who made the change
            reason: Optional reason for change
        """
        event = Event.create(
            event_type='risk.severity.changed',
            data={
                'risk_id': risk_id,
                'old_severity': old_severity,
                'new_severity': new_severity,
                'changed_by': changed_by,
                'changed_at': datetime.utcnow().isoformat(),
                'reason': reason,
                'escalated': self._is_escalation(old_severity, new_severity),
                'requires_plan_update': new_severity in ['critical', 'high']
            },
            source='risk-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH if new_severity in ['critical', 'high'] else EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f"Published risk.severity.changed for risk {risk_id}: "
            f"{old_severity} -> {new_severity}"
        )

    async def publish_risk_mitigation_proposed(
        self,
        risk_id: str,
        mitigation_id: str,
        tenant_id: str,
        strategy: str,
        estimated_cost: float,
        estimated_risk_reduction: float
    ) -> None:
        """
        Publish event when risk mitigation is proposed.

        Triggers:
        - Planning service: Integrate mitigation into BC plans
        - Approval service: Route for approval
        """
        event = Event.create(
            event_type='risk.mitigation.proposed',
            data={
                'risk_id': risk_id,
                'mitigation_id': mitigation_id,
                'strategy': strategy,
                'estimated_cost': estimated_cost,
                'estimated_risk_reduction': estimated_risk_reduction,
                'proposed_at': datetime.utcnow().isoformat()
            },
            source='risk-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published risk.mitigation.proposed for risk {risk_id}")

    # ==================== PRIVATE HELPERS ====================

    async def _generate_risk_suggestions_from_bia(
        self,
        processes: List[Dict[str, Any]],
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate risk suggestions based on BIA process data.

        Business logic for AI-driven risk identification from BIA.

        Args:
            processes: List of BIA processes with criticality data
            tenant_id: Tenant ID

        Returns:
            List of risk suggestions
        """
        suggestions = []

        for process in processes:
            process_id = process.get('process_id')
            process_name = process.get('name')
            criticality = process.get('criticality', '')
            rto = process.get('rto', 0)
            rpo = process.get('rpo', 0)
            dependencies = process.get('dependencies', [])

            # Suggest risks based on criticality
            if criticality in ['critical', 'high']:
                suggestions.append({
                    'title': f"Disruption risk for critical process: {process_name}",
                    'category': 'operational',
                    'estimated_severity': 'high' if criticality == 'critical' else 'medium',
                    'rationale': f"Process has {criticality} criticality with RTO of {rto}h",
                    'related_process_id': process_id,
                    'recommended_mitigation': 'Implement redundancy and backup procedures'
                })

            # Suggest risks based on tight RTO
            if rto > 0 and rto < 4:
                suggestions.append({
                    'title': f"RTO breach risk for {process_name}",
                    'category': 'continuity',
                    'estimated_severity': 'high',
                    'rationale': f"Very tight RTO of {rto}h may be difficult to achieve",
                    'related_process_id': process_id,
                    'recommended_mitigation': 'Validate recovery capabilities through testing'
                })

            # Suggest risks based on dependencies
            if len(dependencies) > 5:
                suggestions.append({
                    'title': f"Dependency risk for {process_name}",
                    'category': 'operational',
                    'estimated_severity': 'medium',
                    'rationale': f"Process has {len(dependencies)} dependencies, increasing complexity",
                    'related_process_id': process_id,
                    'recommended_mitigation': 'Map and document all dependencies'
                })

            # Suggest data loss risk based on RPO
            if rpo > 0 and rpo < 1:
                suggestions.append({
                    'title': f"Data loss risk for {process_name}",
                    'category': 'data',
                    'estimated_severity': 'high',
                    'rationale': f"Tight RPO of {rpo}h requires continuous data protection",
                    'related_process_id': process_id,
                    'recommended_mitigation': 'Implement real-time data replication'
                })

        return suggestions

    async def _publish_risk_suggestions(
        self,
        suggestions: List[Dict[str, Any]],
        source: str,
        tenant_id: str
    ) -> None:
        """
        Publish risk suggestions event.

        Args:
            suggestions: List of risk suggestions
            source: Source identifier (e.g., BIA assessment ID)
            tenant_id: Tenant ID
        """
        event = Event.create(
            event_type='risk.suggestion.generated',
            data={
                'source': source,
                'suggested_risks': suggestions,
                'confidence': 0.85,  # AI confidence score
                'generated_at': datetime.utcnow().isoformat(),
                'count': len(suggestions)
            },
            source='risk-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published {len(suggestions)} risk suggestions from {source}")

    async def _publish_risk_suggestion_for_process(
        self,
        process_id: str,
        reason: str,
        priority: str,
        tenant_id: str,
        process_name: str = None
    ) -> None:
        """
        Publish risk suggestion for a specific process.

        Args:
            process_id: Process identifier
            reason: Reason for suggestion
            priority: Priority level
            tenant_id: Tenant ID
            process_name: Optional process name
        """
        suggestion = {
            'title': f"Risk assessment required for process {process_name or process_id}",
            'category': 'continuity',
            'estimated_severity': priority,
            'rationale': reason,
            'related_process_id': process_id,
            'recommended_action': 'Conduct immediate risk assessment'
        }

        await self._publish_risk_suggestions(
            suggestions=[suggestion],
            source=f"process-{process_id}",
            tenant_id=tenant_id
        )

    def _is_escalation(self, old_severity: str, new_severity: str) -> bool:
        """
        Check if severity change is an escalation.

        Args:
            old_severity: Previous severity
            new_severity: New severity

        Returns:
            True if escalated, False otherwise
        """
        severity_order = ['low', 'medium', 'high', 'critical']
        try:
            old_idx = severity_order.index(old_severity.lower())
            new_idx = severity_order.index(new_severity.lower())
            return new_idx > old_idx
        except (ValueError, AttributeError):
            return False


# Global event handlers instance
_handlers = None


def get_risk_event_handlers(eventbus=None, risk_service=None) -> RiskEventHandlers:
    """
    Get or create global Risk event handlers instance.

    Args:
        eventbus: Optional eventbus instance
        risk_service: Optional risk service for business logic

    Returns:
        RiskEventHandlers: Global event handlers instance
    """
    global _handlers
    if _handlers is None:
        _handlers = RiskEventHandlers(eventbus, risk_service)
    return _handlers
