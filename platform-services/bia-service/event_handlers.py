"""
BIA Service Event Handlers
===========================

Event-driven choreography for BIA service.
Publishes events when BIA assessments complete, allowing downstream services
to react automatically (e.g., Risk service, Planning service).
"""

import logging
from typing import Dict, Any
from datetime import datetime

# Import eventbus from infrastructure
import sys
sys.path.append('/Users/MD/AI-Platform-ISO/infrastructure')
from eventbus import Event, EventPriority, create_eventbus

logger = logging.getLogger(__name__)


class BIAEventHandlers:
    """
    Event handlers for BIA service.

    Publishes events when:
    - BIA assessment is completed
    - Critical processes are identified
    - Dependencies are mapped
    - Recovery objectives are set
    """

    def __init__(self, eventbus=None):
        self.eventbus = eventbus or create_eventbus('redis')

    async def on_assessment_created(
        self,
        assessment_id: str,
        tenant_id: str,
        name: str,
        created_by: str
    ) -> None:
        """
        Publish event when BIA assessment is created.

        Triggers:
        - Audit logging
        - Workflow initialization
        """
        event = Event.create(
            event_type='bia.assessment.created',
            data={
                'assessment_id': assessment_id,
                'name': name,
                'created_by': created_by,
                'created_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.assessment.created for assessment {assessment_id}")

    async def on_assessment_completed(
        self,
        assessment_id: str,
        tenant_id: str,
        processes: list,
        critical_process_count: int,
        total_processes: int
    ) -> None:
        """
        Publish event when BIA assessment is completed.

        This is a KEY choreography event that triggers:
        - Risk service: Auto-generate risk suggestions based on critical processes
        - Planning service: Create BC plan templates for high-criticality processes
        - Governance service: Update compliance posture
        - Notification service: Alert stakeholders

        Args:
            assessment_id: Unique assessment identifier
            tenant_id: Tenant ID
            processes: List of analyzed processes with criticality data
            critical_process_count: Number of critical processes identified
            total_processes: Total processes analyzed
        """
        # Transform processes to include only essential data
        process_data = []
        for process in processes:
            process_data.append({
                'process_id': str(process.get('id', process.get('process_id', ''))),
                'name': process.get('name', ''),
                'criticality': process.get('criticality', ''),
                'criticality_score': process.get('criticality_score', 0),
                'rto': process.get('rto_hours', 0),
                'rpo': process.get('rpo_hours', 0),
                'mtpd': process.get('mtpd_hours', 0),
                'financial_impact': process.get('financial_impact', 0),
                'operational_impact': process.get('operational_impact', ''),
                'reputational_impact': process.get('reputational_impact', ''),
                'dependencies': process.get('dependencies', [])
            })

        event = Event.create(
            event_type='bia.assessment.completed',
            data={
                'assessment_id': assessment_id,
                'completed_at': datetime.utcnow().isoformat(),
                'processes': process_data,
                'critical_process_count': critical_process_count,
                'total_processes': total_processes,
                'completion_percentage': 100,
                'summary': {
                    'critical': critical_process_count,
                    'high': sum(1 for p in processes if p.get('criticality') == 'high'),
                    'medium': sum(1 for p in processes if p.get('criticality') == 'medium'),
                    'low': sum(1 for p in processes if p.get('criticality') == 'low')
                }
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH  # High priority for choreography
        )

        await self.eventbus.publish(event)
        logger.info(
            f"Published bia.assessment.completed for assessment {assessment_id} "
            f"with {critical_process_count} critical processes"
        )

    async def on_process_created(
        self,
        process_id: str,
        assessment_id: str,
        tenant_id: str,
        name: str,
        owner: str,
        criticality: str
    ) -> None:
        """
        Publish event when individual BIA process is created.

        Triggers:
        - Dependency mapping
        - Resource identification
        """
        event = Event.create(
            event_type='bia.process.created',
            data={
                'process_id': process_id,
                'assessment_id': assessment_id,
                'name': name,
                'owner': owner,
                'criticality': criticality,
                'created_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.process.created for process {process_id}")

    async def on_criticality_changed(
        self,
        process_id: str,
        tenant_id: str,
        old_criticality: str,
        new_criticality: str,
        changed_by: str,
        reason: str = None
    ) -> None:
        """
        Publish event when process criticality changes.

        Critical choreography event that triggers:
        - Risk service: Re-assess risks for this process
        - Planning service: Update BC plan priority
        - Notification service: Alert process owner

        Args:
            process_id: Process identifier
            tenant_id: Tenant ID
            old_criticality: Previous criticality level
            new_criticality: New criticality level
            changed_by: User who made the change
            reason: Optional reason for change
        """
        event = Event.create(
            event_type='bia.criticality.changed',
            data={
                'process_id': process_id,
                'old_criticality': old_criticality,
                'new_criticality': new_criticality,
                'changed_by': changed_by,
                'changed_at': datetime.utcnow().isoformat(),
                'reason': reason,
                'requires_plan_update': new_criticality in ['critical', 'high']
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH if new_criticality in ['critical', 'high'] else EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f"Published bia.criticality.changed for process {process_id}: "
            f"{old_criticality} -> {new_criticality}"
        )

    async def on_rto_set(
        self,
        process_id: str,
        tenant_id: str,
        rto_hours: int,
        set_by: str
    ) -> None:
        """
        Publish event when Recovery Time Objective is set.

        Triggers:
        - Planning service: Validate BC plan feasibility
        - Validation service: Check RTO vs MTPD
        """
        event = Event.create(
            event_type='bia.rto.set',
            data={
                'process_id': process_id,
                'rto_hours': rto_hours,
                'set_by': set_by,
                'set_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.rto.set for process {process_id}: {rto_hours}h")

    async def on_rpo_set(
        self,
        process_id: str,
        tenant_id: str,
        rpo_hours: int,
        set_by: str
    ) -> None:
        """
        Publish event when Recovery Point Objective is set.

        Triggers:
        - Planning service: Update backup strategy
        - Validation service: Check RPO vs RTO
        """
        event = Event.create(
            event_type='bia.rpo.set',
            data={
                'process_id': process_id,
                'rpo_hours': rpo_hours,
                'set_by': set_by,
                'set_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.rpo.set for process {process_id}: {rpo_hours}h")

    async def on_dependency_added(
        self,
        process_id: str,
        tenant_id: str,
        dependency_type: str,
        dependency_id: str,
        criticality: str
    ) -> None:
        """
        Publish event when dependency is added to process.

        Triggers:
        - Dependency service: Map dependency graph
        - Analytics service: Update impact analysis
        """
        event = Event.create(
            event_type='bia.dependency.added',
            data={
                'process_id': process_id,
                'dependency_type': dependency_type,
                'dependency_id': dependency_id,
                'criticality': criticality,
                'added_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.dependency.added for process {process_id}")

    async def on_impact_assessed(
        self,
        process_id: str,
        tenant_id: str,
        financial_impact: float,
        operational_impact: str,
        reputational_impact: str
    ) -> None:
        """
        Publish event when impact assessment is completed.

        Triggers:
        - Risk service: Calculate risk exposure
        - Reporting service: Generate impact reports
        """
        event = Event.create(
            event_type='bia.impact.assessed',
            data={
                'process_id': process_id,
                'financial_impact': financial_impact,
                'operational_impact': operational_impact,
                'reputational_impact': reputational_impact,
                'assessed_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.impact.assessed for process {process_id}")

    async def on_critical_process_identified(
        self,
        process_id: str,
        tenant_id: str,
        name: str,
        criticality_score: float,
        requires_immediate_attention: bool = False
    ) -> None:
        """
        Publish event when critical process is identified.

        High-priority choreography event that triggers:
        - Risk service: Immediate risk assessment
        - Planning service: Priority BC plan creation
        - Alert service: Notify management

        Args:
            process_id: Process identifier
            tenant_id: Tenant ID
            name: Process name
            criticality_score: Numerical criticality score
            requires_immediate_attention: Flag for urgent processes
        """
        event = Event.create(
            event_type='bia.critical.process.identified',
            data={
                'process_id': process_id,
                'name': name,
                'criticality_score': criticality_score,
                'requires_immediate_attention': requires_immediate_attention,
                'identified_at': datetime.utcnow().isoformat(),
                'recommended_actions': [
                    'Conduct immediate risk assessment',
                    'Create or update BC plan',
                    'Identify recovery resources',
                    'Define backup strategy'
                ]
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL if requires_immediate_attention else EventPriority.HIGH
        )

        await self.eventbus.publish(event)
        logger.warning(
            f"Published bia.critical.process.identified for process {process_id} "
            f"(score: {criticality_score}, urgent: {requires_immediate_attention})"
        )

    async def on_gap_identified(
        self,
        process_id: str,
        tenant_id: str,
        gap_type: str,
        severity: str,
        description: str
    ) -> None:
        """
        Publish event when gap is identified in BIA.

        Triggers:
        - Planning service: Create remediation plan
        - Risk service: Assess gap risk
        """
        event = Event.create(
            event_type='bia.gap.identified',
            data={
                'process_id': process_id,
                'gap_type': gap_type,
                'severity': severity,
                'description': description,
                'identified_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH if severity in ['critical', 'high'] else EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.gap.identified for process {process_id}")

    async def on_recovery_strategy_proposed(
        self,
        process_id: str,
        tenant_id: str,
        strategy: str,
        estimated_cost: float
    ) -> None:
        """
        Publish event when recovery strategy is proposed.

        Triggers:
        - Planning service: Evaluate and integrate strategy
        """
        event = Event.create(
            event_type='bia.recovery.strategy.proposed',
            data={
                'process_id': process_id,
                'strategy': strategy,
                'estimated_cost': estimated_cost,
                'proposed_at': datetime.utcnow().isoformat()
            },
            source='bia-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published bia.recovery.strategy.proposed for process {process_id}")


# Global event handlers instance
_handlers = None


def get_bia_event_handlers(eventbus=None) -> BIAEventHandlers:
    """
    Get or create global BIA event handlers instance.

    Args:
        eventbus: Optional eventbus instance (creates default if None)

    Returns:
        BIAEventHandlers: Global event handlers instance
    """
    global _handlers
    if _handlers is None:
        _handlers = BIAEventHandlers(eventbus)
    return _handlers
