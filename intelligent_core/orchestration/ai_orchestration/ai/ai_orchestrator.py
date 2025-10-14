"""
AI Orchestrator - Main AI coordination and intelligence

Consolidates from:
- /services/ai_orchestrator/main.py (BCMIntelligenceEngine, AIDevOpsEngine, ClaudeProEngine)
- /backend/orchestrator_service/main.py (event processing, auto-triggers)
- /backend/orchestrator/ai_orchestrator.py (rule engine, decision making)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from core import BaseOrchestrator
from models import AIDecision, OrchestratorRule, ActionType
from .intelligence_engine import IntelligenceEngine
from .devops_engine import DevOpsEngine

logger = logging.getLogger(__name__)


class AIOrchestrator(BaseOrchestrator):
    """
    AI Orchestration and Intelligence

    Responsibilities:
    - Process BCM events and make intelligent decisions
    - Auto-generate plans (BCP, DRP) from BIA
    - Classify incidents and suggest responses
    - AI-powered deployment orchestration
    - Learning from experience
    - Rule-based automation
    """

    def __init__(self):
        super().__init__()

        # AI Engines
        self.intelligence = IntelligenceEngine()
        self.devops = DevOpsEngine(
            docker_manager=self.docker_manager,
            service_registry=self.service_registry
        )

        # Decision tracking
        self.rules: List[OrchestratorRule] = []
        self.decisions: List[AIDecision] = []
        self.pending_decisions: Dict[str, AIDecision] = {}

        logger.info("AIOrchestrator initialized")

    async def start(self) -> None:
        """
        Start AI orchestrator

        Initialize:
        - Orchestration rules
        - Event subscriptions
        - AI engines
        """
        if self.running:
            logger.warning("AI Orchestrator already running")
            return

        logger.info("Starting AI Orchestrator...")

        # Initialize rules
        await self._initialize_rules()

        # Subscribe to BCM events
        await self._subscribe_to_events()

        self.running = True
        logger.info("AI Orchestrator started")

        # Publish startup event
        await self.publish_event(
            event_type='ai.orchestrator.ready',
            data={'rules_count': len(self.rules)}
        )

    async def stop(self) -> None:
        """Stop AI orchestrator"""
        self.running = False
        logger.info("AI Orchestrator stopped")

    async def get_status(self) -> Dict[str, Any]:
        """Get AI orchestrator status"""
        return {
            'running': self.running,
            'rules_active': len([r for r in self.rules if r.enabled]),
            'total_decisions': len(self.decisions),
            'pending_approvals': len(self.pending_decisions),
            'engines': {
                'intelligence': 'active',
                'devops': 'active'
            },
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _initialize_rules(self) -> None:
        """
        Initialize orchestration rules

        Rules define: when event X happens → take action Y
        """
        self.rules = [
            # Rule 1: Auto-generate BCP after BIA completion
            OrchestratorRule(
                name="auto_generate_bcp",
                event_type="bcm.bia.completed",
                conditions={"has_critical_processes": True},
                actions=[ActionType.GENERATE_PLAN, ActionType.SEND_NOTIFICATION],
                priority=1,
                enabled=True
            ),

            # Rule 2: Incident response for critical incidents
            OrchestratorRule(
                name="incident_response",
                event_type="bcm.incident.opened",
                conditions={"severity": ["high", "critical"]},
                actions=[ActionType.SUGGEST_RESPONSE, ActionType.TRIGGER_WORKFLOW],
                priority=1,
                enabled=True
            ),

            # Rule 3: Schedule training after plan approval
            OrchestratorRule(
                name="schedule_training",
                event_type="bcm.plan.approved",
                conditions={"plan_type": ["BCP", "DRP"]},
                actions=[ActionType.SCHEDULE_TRAINING, ActionType.SEND_NOTIFICATION],
                priority=2,
                enabled=True
            ),

            # Rule 4: Compliance analysis after audit
            OrchestratorRule(
                name="compliance_analysis",
                event_type="bcm.audit.completed",
                conditions={},
                actions=[ActionType.ANALYZE_COMPLIANCE],
                priority=1,
                enabled=True
            ),

            # Rule 5: KPI-based recommendations
            OrchestratorRule(
                name="kpi_recommendations",
                event_type="bcm.kpi.calculated",
                conditions={},
                actions=[ActionType.CREATE_TASK],
                priority=2,
                enabled=True
            ),
        ]

        logger.info(f"Initialized {len(self.rules)} orchestration rules")

    async def _subscribe_to_events(self) -> None:
        """Subscribe to BCM events"""
        # Subscribe to all BCM events
        await self.subscribe_to_events("bcm.*", self._handle_event)
        logger.info("Subscribed to bcm.* events")

    async def _handle_event(self, event) -> None:
        """
        Handle incoming BCM event

        Process through rule engine and execute actions
        """
        event_type = event.get('type', '')
        tenant_id = event.get('tenant_id')
        data = event.get('data', {})

        logger.info(f"Processing event: {event_type}")

        # Find matching rules
        matching_rules = [
            rule for rule in self.rules
            if rule.enabled and rule.event_type == event_type
        ]

        if not matching_rules:
            logger.debug(f"No rules match event: {event_type}")
            return

        # Process each matching rule
        for rule in matching_rules:
            if await self._check_conditions(data, rule.conditions):
                await self._execute_rule(rule, event)

    async def _check_conditions(self, event_data: Dict[str, Any],
                                conditions: Dict[str, Any]) -> bool:
        """
        Check if event data meets rule conditions

        Args:
            event_data: Event data dictionary
            conditions: Rule conditions

        Returns:
            True if all conditions met
        """
        for key, expected in conditions.items():
            actual = event_data.get(key)

            if isinstance(expected, list):
                # Check if actual in list
                if actual not in expected:
                    return False
            elif isinstance(expected, bool):
                # Boolean check
                if bool(actual) != expected:
                    return False
            else:
                # Exact match
                if actual != expected:
                    return False

        return True

    async def _execute_rule(self, rule: OrchestratorRule, event: Dict[str, Any]) -> None:
        """
        Execute rule actions

        Args:
            rule: Orchestration rule
            event: Event that triggered the rule
        """
        logger.info(f"Executing rule: {rule.name}")

        # Create decision record
        decision = AIDecision(
            id=str(uuid.uuid4()),
            type=rule.name,
            title=f"Auto-action: {rule.name}",
            description=f"Triggered by {event.get('type')}",
            recommendation="Execute configured actions",
            confidence=0.90,
            status="pending",
            created_at=datetime.utcnow(),
            tenant_id=event.get('tenant_id', 'system'),
            data=event.get('data', {})
        )

        # Store decision
        self.decisions.append(decision)
        self.pending_decisions[decision.id] = decision

        # Execute actions
        for action in rule.actions:
            try:
                await self._execute_action(action, event, decision)
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")

    async def _execute_action(self, action: ActionType, event: Dict[str, Any],
                             decision: AIDecision) -> None:
        """
        Execute specific action

        Args:
            action: Action type to execute
            event: Event data
            decision: Decision record
        """
        if action == ActionType.GENERATE_PLAN:
            await self._action_generate_plan(event, decision)

        elif action == ActionType.SUGGEST_RESPONSE:
            await self._action_suggest_response(event, decision)

        elif action == ActionType.SCHEDULE_TRAINING:
            await self._action_schedule_training(event, decision)

        elif action == ActionType.ANALYZE_COMPLIANCE:
            await self._action_analyze_compliance(event, decision)

        elif action == ActionType.CREATE_TASK:
            await self._action_create_task(event, decision)

        elif action == ActionType.SEND_NOTIFICATION:
            await self._action_send_notification(event, decision)

        elif action == ActionType.TRIGGER_WORKFLOW:
            await self._action_trigger_workflow(event, decision)

        else:
            logger.warning(f"Unknown action type: {action}")

    async def _action_generate_plan(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Generate BCP/DRP plan from BIA data"""
        logger.info("Generating plan from BIA data")

        # Use intelligence engine
        plan = await self.intelligence.generate_plan_from_bia(event.get('data', {}))

        # Publish plan generated event
        await self.publish_event(
            event_type='bcm.plan.generated',
            data=plan,
            tenant_id=event.get('tenant_id')
        )

        logger.info(f"Plan generated: {plan.get('id')}")

    async def _action_suggest_response(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Suggest incident response actions"""
        logger.info("Generating incident response suggestions")

        incident_data = event.get('data', {})
        suggestions = await self.intelligence.suggest_incident_response(incident_data)

        # Publish suggestions
        await self.publish_event(
            event_type='bcm.incident.response_suggested',
            data=suggestions,
            tenant_id=event.get('tenant_id')
        )

    async def _action_schedule_training(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Schedule training sessions"""
        logger.info("Scheduling training")

        # Publish training schedule event
        await self.publish_event(
            event_type='bcm.training.scheduled',
            data={'plan_id': event.get('data', {}).get('plan_id')},
            tenant_id=event.get('tenant_id')
        )

    async def _action_analyze_compliance(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Analyze compliance gaps"""
        logger.info("Analyzing compliance")

        audit_data = event.get('data', {})
        analysis = await self.intelligence.analyze_compliance(audit_data)

        await self.publish_event(
            event_type='bcm.compliance.analyzed',
            data=analysis,
            tenant_id=event.get('tenant_id')
        )

    async def _action_create_task(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Create follow-up task"""
        logger.info("Creating task")

        task = {
            'title': f"Follow-up: {event.get('type')}",
            'description': decision.description,
            'priority': 'medium'
        }

        await self.publish_event(
            event_type='bcm.task.created',
            data=task,
            tenant_id=event.get('tenant_id')
        )

    async def _action_send_notification(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Send notification"""
        logger.info("Sending notification")

        notification = {
            'subject': decision.title,
            'message': decision.description
        }

        await self.publish_event(
            event_type='bcm.notification.sent',
            data=notification,
            tenant_id=event.get('tenant_id')
        )

    async def _action_trigger_workflow(self, event: Dict[str, Any], decision: AIDecision) -> None:
        """Trigger workflow"""
        logger.info("Triggering workflow")

        await self.publish_event(
            event_type='bcm.workflow.triggered',
            data={'trigger': event.get('type')},
            tenant_id=event.get('tenant_id')
        )

    async def approve_decision(self, decision_id: str, approved_by: str) -> None:
        """Approve pending decision"""
        if decision_id in self.pending_decisions:
            decision = self.pending_decisions[decision_id]
            decision.status = "approved"

            logger.info(f"Decision {decision_id} approved by {approved_by}")

            # Remove from pending
            del self.pending_decisions[decision_id]

            # Publish approval event
            await self.publish_event(
                event_type='ai.decision.approved',
                data={'decision_id': decision_id}
            )

    async def reject_decision(self, decision_id: str, rejected_by: str) -> None:
        """Reject pending decision"""
        if decision_id in self.pending_decisions:
            decision = self.pending_decisions[decision_id]
            decision.status = "rejected"

            logger.info(f"Decision {decision_id} rejected by {rejected_by}")

            # Remove from pending
            del self.pending_decisions[decision_id]

            # Publish rejection event
            await self.publish_event(
                event_type='ai.decision.rejected',
                data={'decision_id': decision_id}
            )