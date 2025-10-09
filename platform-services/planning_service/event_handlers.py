"""
Planning Service Event Handlers
================================

Event-driven choreography for Planning service.
Subscribes to BIA and Risk events to auto-create and update BC plans.

Event Flow:
  BIA Assessment Completed → Analyze Requirements → Create BC Plan Templates
  Risk Assessment Completed → Auto-create BC Plans for High Risks
  Risk Severity Changed → Update Plan Priority
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

# Import eventbus from infrastructure
import sys
sys.path.append('/Users/MD/AI-Platform-ISO/infrastructure')
from eventbus import Event, EventPriority, create_eventbus

logger = logging.getLogger(__name__)


class PlanningEventHandlers:
    """
    Event handlers for Planning service.

    Subscribes to:
    - bia.assessment.completed: Analyze recovery requirements
    - bia.critical.process.identified: Create priority BC plan
    - risk.assessment.completed: Auto-create BC plans for high risks
    - risk.severity.changed: Update plan priority

    Publishes:
    - plan.created: When BC plan is created
    - plan.updated: When plan is updated
    - plan.approved: When plan is approved
    - plan.activated: When plan is activated during crisis
    """

    def __init__(self, eventbus=None, planning_service=None):
        self.eventbus = eventbus or create_eventbus('redis')
        self.planning_service = planning_service  # Injected planning service for business logic

    # ==================== SUBSCRIBERS ====================

    async def on_bia_completed(self, event: Event) -> None:
        """
        React to BIA assessment completion by analyzing recovery requirements.

        Creates BC plan templates for processes with critical recovery objectives.

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
                f"analyzing recovery requirements for {critical_count} critical processes"
            )

            # Analyze recovery requirements for critical processes
            plan_suggestions = await self._analyze_recovery_requirements(
                processes=processes,
                tenant_id=tenant_id
            )

            if plan_suggestions:
                logger.info(
                    f"Generated {len(plan_suggestions)} BC plan suggestions "
                    f"from BIA assessment {assessment_id}"
                )

                # Optionally auto-create plans (could also just publish suggestions)
                for suggestion in plan_suggestions:
                    await self._publish_plan_suggestion(
                        suggestion=suggestion,
                        source=f"bia-assessment-{assessment_id}",
                        tenant_id=tenant_id
                    )
            else:
                logger.info(f"No BC plan suggestions from BIA assessment {assessment_id}")

        except Exception as e:
            logger.error(f"Error processing bia.assessment.completed: {e}", exc_info=True)

    async def on_critical_process_identified(self, event: Event) -> None:
        """
        React to critical process identification by creating priority BC plan.

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
                f"Critical process identified: {process_name} (score: {criticality_score}), "
                f"creating priority BC plan"
            )

            # Auto-create BC plan for critical process
            plan_suggestion = {
                'process_id': process_id,
                'process_name': process_name,
                'plan_type': 'business_continuity',
                'priority': 'critical' if urgent else 'high',
                'reason': f"Critical process with score {criticality_score}",
                'recommended_strategies': [
                    'Identify alternate work locations',
                    'Define recovery team roles',
                    'Document recovery procedures',
                    'Test recovery capabilities'
                ]
            }

            await self._publish_plan_suggestion(
                suggestion=plan_suggestion,
                source=f"critical-process-{process_id}",
                tenant_id=tenant_id
            )

        except Exception as e:
            logger.error(f"Error processing bia.critical.process.identified: {e}", exc_info=True)

    async def on_risk_assessment_completed(self, event: Event) -> None:
        """
        React to risk assessment completion by auto-creating BC plans for high risks.

        This is a KEY choreography handler that implements the Risk → Planning flow.

        Args:
            event: risk.assessment.completed event
        """
        try:
            assessment_id = event.data.get('assessment_id')
            tenant_id = event.tenant_id
            risks = event.data.get('risks', [])
            high_risk_count = event.data.get('high_risk_count', 0)

            logger.info(
                f"Received risk.assessment.completed for assessment {assessment_id}, "
                f"analyzing {len(risks)} risks ({high_risk_count} high/critical)"
            )

            # Auto-create BC plans for high/critical risks
            plan_suggestions = await self._create_plans_for_high_risks(
                risks=risks,
                tenant_id=tenant_id
            )

            if plan_suggestions:
                logger.info(
                    f"Generated {len(plan_suggestions)} BC plan suggestions "
                    f"from risk assessment {assessment_id}"
                )

                for suggestion in plan_suggestions:
                    await self._publish_plan_suggestion(
                        suggestion=suggestion,
                        source=f"risk-assessment-{assessment_id}",
                        tenant_id=tenant_id
                    )
            else:
                logger.info(f"No BC plan suggestions from risk assessment {assessment_id}")

        except Exception as e:
            logger.error(f"Error processing risk.assessment.completed: {e}", exc_info=True)

    async def on_risk_severity_changed(self, event: Event) -> None:
        """
        React to risk severity change by updating related BC plan priority.

        Args:
            event: risk.severity.changed event
        """
        try:
            risk_id = event.data.get('risk_id')
            old_severity = event.data.get('old_severity')
            new_severity = event.data.get('new_severity')
            tenant_id = event.tenant_id

            logger.info(
                f"Risk {risk_id} severity changed: {old_severity} -> {new_severity}, "
                f"checking for plan updates"
            )

            # If risk escalated to high/critical, suggest creating/updating plan
            if new_severity in ['critical', 'high'] and old_severity not in ['critical', 'high']:
                await self._publish_plan_update_suggestion(
                    risk_id=risk_id,
                    reason=f"Risk severity escalated to {new_severity}",
                    priority=new_severity,
                    tenant_id=tenant_id
                )

        except Exception as e:
            logger.error(f"Error processing risk.severity.changed: {e}", exc_info=True)

    async def on_risk_mitigation_proposed(self, event: Event) -> None:
        """
        React to risk mitigation proposal by integrating into BC plans.

        Args:
            event: risk.mitigation.proposed event
        """
        try:
            risk_id = event.data.get('risk_id')
            mitigation_id = event.data.get('mitigation_id')
            strategy = event.data.get('strategy')
            tenant_id = event.tenant_id

            logger.info(
                f"Risk mitigation proposed for risk {risk_id}, "
                f"integrating into BC plans"
            )

            # Suggest updating related BC plans with mitigation strategy
            await self._publish_plan_update_suggestion(
                risk_id=risk_id,
                reason=f"Integrate mitigation strategy: {strategy}",
                priority='medium',
                tenant_id=tenant_id,
                mitigation_id=mitigation_id
            )

        except Exception as e:
            logger.error(f"Error processing risk.mitigation.proposed: {e}", exc_info=True)

    # ==================== PUBLISHERS ====================

    async def publish_plan_created(
        self,
        plan_id: str,
        tenant_id: str,
        plan_type: str,
        name: str,
        created_by: str
    ) -> None:
        """
        Publish event when BC plan is created.

        Args:
            plan_id: Plan identifier
            tenant_id: Tenant ID
            plan_type: Type of plan (business_continuity, disaster_recovery, etc.)
            name: Plan name
            created_by: User who created the plan
        """
        event = Event.create(
            event_type='plan.created',
            data={
                'plan_id': plan_id,
                'plan_type': plan_type,
                'name': name,
                'created_by': created_by,
                'created_at': datetime.utcnow().isoformat()
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published plan.created for plan {plan_id}")

    async def publish_plan_updated(
        self,
        plan_id: str,
        tenant_id: str,
        updated_by: str,
        version: int,
        changes: Dict[str, Any]
    ) -> None:
        """
        Publish event when BC plan is updated.

        Args:
            plan_id: Plan identifier
            tenant_id: Tenant ID
            updated_by: User who updated the plan
            version: New version number
            changes: Dictionary of changes made
        """
        event = Event.create(
            event_type='plan.updated',
            data={
                'plan_id': plan_id,
                'updated_by': updated_by,
                'version': version,
                'changes': changes,
                'updated_at': datetime.utcnow().isoformat()
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published plan.updated for plan {plan_id} (version {version})")

    async def publish_plan_approved(
        self,
        plan_id: str,
        tenant_id: str,
        approved_by: str,
        version: int
    ) -> None:
        """
        Publish event when BC plan is approved.

        Triggers:
        - Governance service: Update compliance status
        - Notification service: Inform stakeholders
        - Training service: Schedule plan training

        Args:
            plan_id: Plan identifier
            tenant_id: Tenant ID
            approved_by: User who approved the plan
            version: Approved version number
        """
        event = Event.create(
            event_type='plan.approved',
            data={
                'plan_id': plan_id,
                'approved_by': approved_by,
                'approved_at': datetime.utcnow().isoformat(),
                'version': version
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH
        )

        await self.eventbus.publish(event)
        logger.info(f"Published plan.approved for plan {plan_id}")

    async def publish_plan_activated(
        self,
        plan_id: str,
        tenant_id: str,
        activated_by: str,
        trigger_event: str
    ) -> None:
        """
        Publish event when BC plan is activated during crisis.

        Critical choreography event that triggers:
        - Response service: Mobilize response team
        - Notification service: Mass notification
        - Coordination service: Start crisis management

        Args:
            plan_id: Plan identifier
            tenant_id: Tenant ID
            activated_by: User who activated the plan
            trigger_event: Event that triggered activation
        """
        event = Event.create(
            event_type='plan.activated',
            data={
                'plan_id': plan_id,
                'activated_by': activated_by,
                'activated_at': datetime.utcnow().isoformat(),
                'trigger_event': trigger_event
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL  # Critical priority for plan activation
        )

        await self.eventbus.publish(event)
        logger.critical(f"Published plan.activated for plan {plan_id} (trigger: {trigger_event})")

    async def publish_plan_tested(
        self,
        plan_id: str,
        tenant_id: str,
        exercise_id: str,
        test_date: str,
        result: str,
        effectiveness_score: float
    ) -> None:
        """
        Publish event when BC plan is tested.

        Args:
            plan_id: Plan identifier
            tenant_id: Tenant ID
            exercise_id: Exercise identifier
            test_date: Test date
            result: Test result (passed, failed, partial)
            effectiveness_score: Effectiveness score (0-100)
        """
        event = Event.create(
            event_type='plan.tested',
            data={
                'plan_id': plan_id,
                'exercise_id': exercise_id,
                'test_date': test_date,
                'result': result,
                'effectiveness_score': effectiveness_score
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published plan.tested for plan {plan_id} (result: {result})")

    # ==================== PRIVATE HELPERS ====================

    async def _analyze_recovery_requirements(
        self,
        processes: List[Dict[str, Any]],
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze recovery requirements from BIA processes.

        Business logic for determining which processes need BC plans.

        Args:
            processes: List of BIA processes
            tenant_id: Tenant ID

        Returns:
            List of BC plan suggestions
        """
        suggestions = []

        for process in processes:
            process_id = process.get('process_id')
            process_name = process.get('name')
            criticality = process.get('criticality', '')
            rto = process.get('rto', 0)
            mtpd = process.get('mtpd', 0)

            # Suggest BC plan for critical/high processes
            if criticality in ['critical', 'high']:
                strategies = []

                # Suggest strategies based on RTO
                if rto <= 4:
                    strategies.append('Hot site or active-active failover')
                    strategies.append('Real-time data replication')
                elif rto <= 24:
                    strategies.append('Warm site with daily backups')
                    strategies.append('Recovery team on standby')
                else:
                    strategies.append('Cold site with documented procedures')
                    strategies.append('Regular backup and testing')

                suggestions.append({
                    'process_id': process_id,
                    'process_name': process_name,
                    'plan_type': 'business_continuity',
                    'priority': 'high' if criticality == 'critical' else 'medium',
                    'reason': f"Critical process with RTO {rto}h requires BC plan",
                    'recommended_strategies': strategies,
                    'target_rto': rto,
                    'target_mtpd': mtpd
                })

        return suggestions

    async def _create_plans_for_high_risks(
        self,
        risks: List[Dict[str, Any]],
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Create BC plan suggestions for high/critical risks.

        Business logic for auto-creating plans based on risk assessment.

        Args:
            risks: List of identified risks
            tenant_id: Tenant ID

        Returns:
            List of BC plan suggestions
        """
        suggestions = []

        for risk in risks:
            risk_id = risk.get('risk_id')
            title = risk.get('title')
            severity = risk.get('severity', '')
            category = risk.get('category', '')
            process_id = risk.get('related_process_id')

            # Create plan suggestions for high/critical risks
            if severity in ['critical', 'high']:
                plan_type = self._determine_plan_type(category)
                strategies = self._suggest_strategies_for_risk(risk)

                suggestions.append({
                    'risk_id': risk_id,
                    'process_id': process_id,
                    'plan_type': plan_type,
                    'name': f"BC Plan for {title}",
                    'priority': severity,
                    'reason': f"High-severity {category} risk requires mitigation plan",
                    'recommended_strategies': strategies
                })

        return suggestions

    async def _publish_plan_suggestion(
        self,
        suggestion: Dict[str, Any],
        source: str,
        tenant_id: str
    ) -> None:
        """
        Publish BC plan suggestion event.

        Args:
            suggestion: Plan suggestion data
            source: Source identifier
            tenant_id: Tenant ID
        """
        event = Event.create(
            event_type='plan.strategy.proposed',
            data={
                'source': source,
                'suggestion': suggestion,
                'proposed_at': datetime.utcnow().isoformat()
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published plan suggestion from {source}")

    async def _publish_plan_update_suggestion(
        self,
        risk_id: str,
        reason: str,
        priority: str,
        tenant_id: str,
        mitigation_id: str = None
    ) -> None:
        """
        Publish suggestion to update BC plan based on risk change.

        Args:
            risk_id: Risk identifier
            reason: Reason for update
            priority: Priority level
            tenant_id: Tenant ID
            mitigation_id: Optional mitigation ID
        """
        event = Event.create(
            event_type='plan.strategy.proposed',
            data={
                'source': f"risk-{risk_id}",
                'suggestion': {
                    'risk_id': risk_id,
                    'mitigation_id': mitigation_id,
                    'action': 'update_plan',
                    'reason': reason,
                    'priority': priority
                },
                'proposed_at': datetime.utcnow().isoformat()
            },
            source='planning-service',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH if priority in ['critical', 'high'] else EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published plan update suggestion for risk {risk_id}")

    def _determine_plan_type(self, risk_category: str) -> str:
        """
        Determine plan type based on risk category.

        Args:
            risk_category: Risk category

        Returns:
            Plan type
        """
        category_map = {
            'operational': 'business_continuity',
            'continuity': 'business_continuity',
            'data': 'disaster_recovery',
            'technology': 'disaster_recovery',
            'security': 'incident_response',
            'compliance': 'compliance_plan'
        }
        return category_map.get(risk_category.lower(), 'business_continuity')

    def _suggest_strategies_for_risk(self, risk: Dict[str, Any]) -> List[str]:
        """
        Suggest recovery strategies for a specific risk.

        Args:
            risk: Risk data

        Returns:
            List of suggested strategies
        """
        category = risk.get('category', '').lower()
        severity = risk.get('severity', '').lower()

        strategies = []

        if category == 'operational':
            strategies.extend([
                'Define alternate procedures',
                'Cross-train team members',
                'Document workarounds'
            ])
        elif category == 'data':
            strategies.extend([
                'Implement backup solution',
                'Test data restoration',
                'Define RPO and RTO'
            ])
        elif category == 'technology':
            strategies.extend([
                'Implement redundancy',
                'Define failover procedures',
                'Maintain vendor contacts'
            ])

        if severity in ['critical', 'high']:
            strategies.append('Conduct regular testing')
            strategies.append('Assign dedicated recovery team')

        return strategies


# Global event handlers instance
_handlers = None


def get_planning_event_handlers(eventbus=None, planning_service=None) -> PlanningEventHandlers:
    """
    Get or create global Planning event handlers instance.

    Args:
        eventbus: Optional eventbus instance
        planning_service: Optional planning service for business logic

    Returns:
        PlanningEventHandlers: Global event handlers instance
    """
    global _handlers
    if _handlers is None:
        _handlers = PlanningEventHandlers(eventbus, planning_service)
    return _handlers
