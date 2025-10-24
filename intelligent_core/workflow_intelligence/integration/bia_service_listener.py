"""
BIA Service Event Listener for workflow_intelligence

Listens to BIA Service events and:
1. Collects cases for learning
2. Triggers PDCA cycles
3. Updates benchmarks
4. Publishes recommendations back to BIA Service

This completes the feedback loop:
BIA Service → EventBus → workflow_intelligence → Learn → Recommend → BIA Service
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BIAServiceListener:
    """
    Listens to BIA Service events and integrates with workflow_intelligence

    Events from BIA Service (Port 8001):
    - bia.assessment.completed
    - bia.process.created
    - bia.criticality.changed
    - bia.critical.process.identified
    """

    def __init__(
        self,
        workflow_engine,
        case_collector,
        pdca_engine=None,
        context_advisor=None
    ):
        """
        Initialize BIA Service listener

        Args:
            workflow_engine: WorkflowEngine instance
            case_collector: CaseCollector for learning
            pdca_engine: PDCA Engine (optional)
            context_advisor: ContextAdvisor (optional)
        """
        self.workflow_engine = workflow_engine
        self.case_collector = case_collector
        self.pdca_engine = pdca_engine
        self.context_advisor = context_advisor

        logger.info("BIA Service listener initialized")

    async def handle_bia_assessment_completed(
        self,
        event_data: Dict[str, Any],
        tenant_id: str
    ):
        """
        Handle BIA assessment completion

        Flow:
        1. Collect case for learning
        2. Trigger PDCA Act phase (learn from execution)
        3. Update benchmarks
        4. Generate recommendations for next BIA
        """
        try:
            assessment_id = event_data.get('assessment_id')
            processes = event_data.get('processes', [])
            duration_hours = event_data.get('duration_hours')
            quality_score = event_data.get('quality_score')

            logger.info(
                f"BIA assessment completed: {assessment_id} "
                f"({len(processes)} processes, {duration_hours}h, quality: {quality_score})"
            )

            # 1. Collect case for learning
            case_data = {
                "workflow_id": assessment_id,
                "module": "bia",
                "org_context": {
                    "industry": event_data.get('industry', 'unknown'),
                    "size": event_data.get('org_size', 'medium'),
                    "maturity_level": event_data.get('maturity_level', 'basic')
                },
                "journey": self._build_journey(event_data),
                "metrics": {
                    "total_duration_days": duration_hours / 24 if duration_hours else None,
                    "total_duration_hours": duration_hours,
                    "total_steps": len(processes),
                    "completed_successfully": True,
                    "quality_score": quality_score,
                    "user_satisfaction": event_data.get('user_satisfaction')
                },
                "success_patterns": self._extract_success_patterns(event_data),
                "lessons_learned": self._extract_lessons(event_data)
            }

            await self.case_collector.collect_case(
                case_data=case_data,
                tenant_id=tenant_id
            )

            logger.info(f"Case collected for BIA: {assessment_id}")

            # 2. Trigger PDCA Act phase (if PDCA engine available)
            if self.pdca_engine:
                await self.pdca_engine.act_phase(
                    workflow_id=assessment_id,
                    actual_metrics=case_data['metrics'],
                    tenant_id=tenant_id
                )
                logger.info(f"PDCA Act phase completed for: {assessment_id}")

            # 3. Update benchmarks (done automatically by case collector)

            # 4. Generate recommendations for next BIA (if context advisor available)
            if self.context_advisor:
                recommendations = await self.context_advisor.get_recommendations(
                    module="bia",
                    org_context=case_data['org_context']
                )
                logger.info(f"Generated recommendations based on {assessment_id}")

        except Exception as e:
            logger.error(f"Error handling BIA assessment completed: {e}", exc_info=True)

    async def handle_bia_process_created(
        self,
        event_data: Dict[str, Any],
        tenant_id: str
    ):
        """
        Handle BIA process creation

        Opportunity to provide proactive recommendations
        """
        try:
            process_id = event_data.get('process_id')
            process_name = event_data.get('process_name')
            criticality = event_data.get('criticality')

            logger.info(
                f"BIA process created: {process_name} "
                f"(ID: {process_id}, criticality: {criticality})"
            )

            # Proactive: Suggest RTO/RPO based on similar processes
            if self.context_advisor and criticality:
                similar_cases = await self.case_collector.find_similar(
                    module="bia",
                    query={
                        "criticality": criticality,
                        "process_type": event_data.get('process_type')
                    },
                    tenant_id=None  # Cross-tenant benchmarking (anonymized)
                )

                if similar_cases:
                    logger.info(
                        f"Found {len(similar_cases)} similar processes "
                        f"for proactive recommendations"
                    )

        except Exception as e:
            logger.error(f"Error handling BIA process created: {e}", exc_info=True)

    async def handle_bia_criticality_changed(
        self,
        event_data: Dict[str, Any],
        tenant_id: str
    ):
        """
        Handle BIA criticality change

        May trigger governance validation (RTO alignment)
        """
        try:
            process_id = event_data.get('process_id')
            old_criticality = event_data.get('old_criticality')
            new_criticality = event_data.get('new_criticality')

            logger.info(
                f"BIA criticality changed: {process_id} "
                f"({old_criticality} → {new_criticality})"
            )

            # Governance: Validate if RTO aligns with new criticality
            if self.workflow_engine.governance:
                validation = await self.workflow_engine.validate_governance(
                    workflow_data={
                        "process_id": process_id,
                        "criticality": new_criticality,
                        "rto_hours": event_data.get('rto_hours')
                    },
                    current_stage="assess_impact",
                    tenant_id=tenant_id
                )

                if validation.decision_type == "warn":
                    logger.warning(
                        f"Governance warning for {process_id}: {validation.rationale}"
                    )

        except Exception as e:
            logger.error(f"Error handling BIA criticality changed: {e}", exc_info=True)

    async def handle_bia_critical_process_identified(
        self,
        event_data: Dict[str, Any],
        tenant_id: str
    ):
        """
        Handle critical process identification

        May trigger cross-service workflows (Risk Assessment, BC Planning)
        """
        try:
            process_id = event_data.get('process_id')
            process_name = event_data.get('process_name')
            rto_hours = event_data.get('rto_hours')

            logger.info(
                f"Critical process identified: {process_name} "
                f"(RTO: {rto_hours}h)"
            )

            # Opportunity: Trigger multi-service workflow
            # BIA (complete) → Risk Assessment (auto-create) → BC Plan (auto-create)

            # This would use Temporal workflows for durability
            # (Implementation in Phase 3)

        except Exception as e:
            logger.error(f"Error handling critical process identified: {e}", exc_info=True)

    def _build_journey(self, event_data: Dict[str, Any]) -> list:
        """
        Build workflow journey from event data

        Returns:
            List of journey steps with timestamps, actions, outcomes
        """
        # Extract journey if provided, otherwise create minimal journey
        journey = event_data.get('journey', [])

        if not journey:
            # Create minimal journey from event data
            journey = [
                {
                    "stage": "identify_processes",
                    "completed_at": event_data.get('started_at'),
                    "duration_seconds": 0
                },
                {
                    "stage": "assess_impact",
                    "completed_at": event_data.get('completed_at'),
                    "duration_seconds": event_data.get('duration_hours', 0) * 3600
                }
            ]

        return journey

    def _extract_success_patterns(self, event_data: Dict[str, Any]) -> list:
        """
        Extract success patterns from completed BIA

        Returns:
            List of patterns that contributed to success
        """
        patterns = []

        # Pattern: Used AI recommendations
        if event_data.get('ai_suggestions_used'):
            patterns.append("Used AI RTO/RPO recommendations")

        # Pattern: Early stakeholder approval
        if event_data.get('stakeholder_approved'):
            patterns.append("Early stakeholder approval obtained")

        # Pattern: Complete dependency mapping
        if event_data.get('dependencies_complete'):
            patterns.append("Complete dependency mapping")

        # Pattern: Fast completion
        duration_hours = event_data.get('duration_hours', 0)
        if duration_hours > 0 and duration_hours < 24:
            patterns.append(f"Fast completion ({duration_hours}h)")

        return patterns

    def _extract_lessons(self, event_data: Dict[str, Any]) -> list:
        """
        Extract lessons learned from BIA execution

        Returns:
            List of lessons learned
        """
        lessons = []

        # Extract challenges if provided
        challenges = event_data.get('challenges', [])
        for challenge in challenges:
            lesson = {
                "challenge": challenge.get('description'),
                "resolution": challenge.get('resolution'),
                "impact": challenge.get('impact')
            }
            lessons.append(lesson)

        return lessons


def register_bia_listener(eventbus, listener: BIAServiceListener):
    """
    Register BIA Service event listeners with EventBus

    Args:
        eventbus: EventBus instance
        listener: BIAServiceListener instance

    Usage:
        eventbus = get_eventbus()
        listener = BIAServiceListener(
            workflow_engine=workflow_engine,
            case_collector=case_collector,
            pdca_engine=pdca_engine,
            context_advisor=context_advisor
        )
        register_bia_listener(eventbus, listener)
    """
    try:
        # Subscribe to BIA events
        eventbus.subscribe(
            "bia.assessment.completed",
            listener.handle_bia_assessment_completed
        )

        eventbus.subscribe(
            "bia.process.created",
            listener.handle_bia_process_created
        )

        eventbus.subscribe(
            "bia.criticality.changed",
            listener.handle_bia_criticality_changed
        )

        eventbus.subscribe(
            "bia.critical.process.identified",
            listener.handle_bia_critical_process_identified
        )

        logger.info(
            "BIA Service listeners registered: "
            "4 event types (assessment.completed, process.created, "
            "criticality.changed, critical.process.identified)"
        )

    except Exception as e:
        logger.error(f"Failed to register BIA listeners: {e}", exc_info=True)
        raise
