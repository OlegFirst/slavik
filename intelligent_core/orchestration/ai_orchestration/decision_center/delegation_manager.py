"""
Delegation Manager (with ACE learning!)
==================

Delegates tasks to specialist agents:
- Workflow Specialist
- BIA Specialist
- Risk Specialist
- Compliance Specialist
- Integration Specialist

Uses EventBus to send delegation events.
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add platform root for ACE integration
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

from ..models import Decision
from infrastructure.eventbus import IEventBus, Event, EventPriority
from shared.ace_integration import ACEIntegration

logger = logging.getLogger(__name__)


class DelegationManager:
    """
    Manages delegation to specialist agents.

    Determines which specialist to delegate to based on:
    - Task type
    - Priority level
    - Specialist availability
    - Domain expertise required

    Example:
        ```python
        manager = DelegationManager()
        await manager.initialize(event_bus)

        result = await manager.delegate(decision)
        if result['success']:
            print(f"Delegated to: {result['specialist']}")
        ```
    """

    # Specialist types
    SPECIALISTS = {
        'workflow': 'workflow-specialist',
        'bia': 'bia-specialist',
        'risk': 'risk-specialist',
        'compliance': 'compliance-specialist',
        'integration': 'integration-specialist',
        'general': 'general-specialist',
        # AI Experts (high-level consultants)
        'bcm_advisor': 'ai-expert-bcm-advisor',
        'compliance_auditor': 'ai-expert-compliance-auditor',
        'strategic_planner': 'ai-expert-strategic-planner'
    }

    def __init__(self):
        # ACE Integration for continuous learning
        self.ace = ACEIntegration(module_name="ai_orchestration")

        self.event_bus: Optional[IEventBus] = None
        self.initialized = False
        self.delegation_stats = {specialist: 0 for specialist in self.SPECIALISTS.values()}

    async def initialize(self, event_bus: IEventBus) -> None:
        """
        Initialize delegation manager.

        Args:
            event_bus: EventBus instance for communication
        """
        self.event_bus = event_bus
        self.initialized = True
        logger.info("DelegationManager initialized")

    async def delegate(
        self,
        decision: Decision,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Delegate task to appropriate specialist (with ACE learning!).

        Args:
            decision: Decision to delegate
            timeout_seconds: Delegation timeout

        Returns:
            dict: Delegation result

        Example:
            ```python
            result = await manager.delegate(decision)
            if result['success']:
                print(f"Task delegated to {result['specialist']}")
            ```
        """
        if not self.initialized:
            raise RuntimeError("DelegationManager not initialized")

        logger.info(f"Delegating decision: {decision.action.value}")

        # Use ACE for continuous learning of delegation patterns!
        result = await self.ace.execute_with_learning(
            task_type="ai_task_delegation",
            base_context={
                "decision": decision.to_dict(),
                "timeout": timeout_seconds
            },
            execute_fn=self._delegate_impl
        )

        return result

    async def _delegate_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal delegation implementation (called by ACE)"""
        # Get decision dict from context
        decision_dict = context["decision"]

        # ACE provides enhanced context with learned strategies!
        strategies = context.get('playbook_strategies', [])
        patterns = context.get('known_patterns', [])

        if strategies:
            logger.info(f"🎯 ACE enhanced: {len(strategies)} strategies, {len(patterns)} patterns")

        # Reconstruct Decision object from dict
        from ..models import DecisionAction, DecisionPriority
        decision = Decision(
            action=DecisionAction(decision_dict['action']),
            priority=DecisionPriority(decision_dict['priority']),
            metadata=decision_dict.get('metadata', {})
        )

        try:
            # Determine specialist (ACE learns which specialist is best!)
            specialist = self._select_specialist(decision)
            logger.info(f"Selected specialist: {specialist}")

            # Create delegation event
            event = self._create_delegation_event(decision, specialist)

            # Publish to event bus
            await self.event_bus.publish(event)

            # Update stats
            self.delegation_stats[specialist] += 1

            logger.info(f"✅ Delegated to {specialist}")

            return {
                'success': True,
                'specialist': specialist,
                'event_id': event.id,
                'delegated_at': datetime.utcnow().isoformat(),
                'effectiveness': 0.85  # ACE will track and improve!
            }

        except Exception as e:
            logger.error(f"Delegation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'effectiveness': 0.0
            }

    def _select_specialist(self, decision: Decision) -> str:
        """
        Select appropriate specialist for decision.

        Selection logic:
        1. Check for AI Expert requirements (high-level expertise)
        2. Fall back to domain specialists
        3. Default to general specialist

        AI Experts (Consultants):
        - BCM Advisor: BCM planning, strategy, BIA design
        - Compliance Auditor: ISO compliance, gap analysis, certification
        - Strategic Planner: Long-term planning, roadmaps, strategic decisions

        Domain Specialists (Execution):
        - BIA Specialist: Execute BIA assessments
        - Risk Specialist: Execute risk assessments
        - Compliance Specialist: Execute compliance checks
        """
        # Get situation and strategy from metadata
        situation = decision.metadata.get('situation', {})
        strategy = decision.metadata.get('strategy', {})
        situation_str = str(situation).lower()
        strategy_action = strategy.get('action', '').lower() if isinstance(strategy, dict) else ''

        # AI EXPERT SELECTION (high-level consulting)

        # BCM Advisor - for complex BCM planning and strategy
        bcm_advisor_keywords = ['bcm planning', 'recovery strategy', 'continuity strategy',
                                'bia design', 'business continuity', 'strategic bcm']
        if any(keyword in situation_str or keyword in strategy_action for keyword in bcm_advisor_keywords):
            logger.info("🎯 Delegating to AI Expert: BCM Advisor")
            return self.SPECIALISTS['bcm_advisor']

        # Compliance Auditor - for compliance and certification
        compliance_auditor_keywords = ['iso compliance', 'gap analysis', 'certification',
                                       'audit preparation', 'compliance assessment', 'iso 22301']
        if any(keyword in situation_str or keyword in strategy_action for keyword in compliance_auditor_keywords):
            logger.info("🎯 Delegating to AI Expert: Compliance Auditor")
            return self.SPECIALISTS['compliance_auditor']

        # Strategic Planner - for strategic planning
        strategic_keywords = ['strategic plan', 'roadmap', 'strategic decision',
                             'long-term planning', 'strategic direction']
        if any(keyword in situation_str or keyword in strategy_action for keyword in strategic_keywords):
            logger.info("🎯 Delegating to AI Expert: Strategic Planner")
            return self.SPECIALISTS['strategic_planner']

        # DOMAIN SPECIALIST SELECTION (execution)

        # Workflow specialist
        if 'workflow' in situation_str:
            return self.SPECIALISTS['workflow']

        # BIA specialist (execution)
        if 'bia' in situation_str or 'business_impact' in situation_str or 'business impact analysis' in situation_str:
            return self.SPECIALISTS['bia']

        # Risk specialist (execution)
        if 'risk' in situation_str or 'threat' in situation_str or 'risk assessment' in situation_str:
            return self.SPECIALISTS['risk']

        # Compliance specialist (execution)
        if 'compliance' in situation_str or 'audit' in situation_str:
            return self.SPECIALISTS['compliance']

        # Integration specialist
        if 'integration' in situation_str or 'api' in situation_str:
            return self.SPECIALISTS['integration']

        # Default to general specialist
        return self.SPECIALISTS['general']

    def _create_delegation_event(
        self,
        decision: Decision,
        specialist: str
    ) -> Event:
        """Create delegation event for specialist."""
        # Determine event priority
        event_priority = EventPriority.NORMAL
        if decision.priority.value >= 3:  # HIGH or CRITICAL
            event_priority = EventPriority.HIGH
        if decision.priority.value >= 4:  # CRITICAL
            event_priority = EventPriority.CRITICAL

        # Create event
        event = Event.create(
            event_type=f'orchestrator.delegate.{specialist}',
            data={
                'decision': decision.to_dict(),
                'specialist': specialist,
                'delegation_time': datetime.utcnow().isoformat()
            },
            source='ai-orchestrator',
            tenant_id=decision.metadata.get('tenant_id', 'default'),
            priority=event_priority
        )

        return event

    def get_stats(self) -> Dict[str, Any]:
        """Get delegation statistics."""
        total = sum(self.delegation_stats.values())
        return {
            'total_delegations': total,
            'by_specialist': self.delegation_stats,
            'initialized': self.initialized
        }
