"""
Main AI Orchestrator
====================

The "brain" of the platform - autonomous decision-making system.

Responsibilities:
- Aggregate context from all sources
- Assess priority and select strategy
- Validate safety before execution
- Execute decisions or delegate
- Learn from outcomes (evolution)
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from intelligent_core.ai_orchestration.models import (
    Decision, Strategy, Priority, FullContext, ActionType,
    PriorityLevel, SafetyResult, SafetyConcern
)
from intelligent_core.ai_orchestration.decision_center.context_aggregator import ContextAggregator
from intelligent_core.ai_orchestration.decision_center.priority_engine import PriorityEngine
from intelligent_core.ai_orchestration.decision_center.strategy_selector import StrategySelector
from intelligent_core.ai_orchestration.decision_center.delegation_manager import DelegationManager
from intelligent_core.ai_orchestration.memory.distributed_memory import DistributedMemory
from intelligent_core.ai_orchestration.safety.safety_monitor import SafetyMonitor
from intelligent_core.ai_orchestration.evolution.evolution_engine import EvolutionEngine
from infrastructure.eventbus import create_eventbus, Event, EventPriority

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Main orchestrator - coordinates all decision-making.

    The orchestrator follows this flow:
    1. Aggregate full context from all sources
    2. Assess priority level
    3. Select best strategy (from memory or generate new)
    4. Validate safety (constitution, loops, hallucinations)
    5. Execute or delegate based on decision
    6. Store outcome in memory for learning

    Attributes:
        context_aggregator: Gathers context from platform
        priority_engine: Determines priority level
        strategy_selector: Selects best strategy
        delegation_manager: Delegates tasks to specialists
        memory: 4-layer distributed memory
        safety_monitor: Safety validation
        evolution_engine: Self-improvement system
        event_bus: Platform event bus

    Example:
        ```python
        orchestrator = AIOrchestrator()
        await orchestrator.initialize()

        # Situation: workflow stuck
        situation = {
            'workflow_stuck': True,
            'workflow_id': 'bia_001',
            'stuck_duration_minutes': 30
        }

        decision = await orchestrator.decide(situation)
        result = await orchestrator.execute(decision)
        ```
    """

    def __init__(
        self,
        event_bus_backend: str = 'redis',
        enable_evolution: bool = True,
        enable_safety: bool = True
    ):
        """
        Initialize AI Orchestrator.

        Args:
            event_bus_backend: EventBus backend ('memory', 'redis', 'rabbitmq')
            enable_evolution: Enable self-evolution features
            enable_safety: Enable safety monitoring
        """
        # Components
        self.context_aggregator = ContextAggregator()
        self.priority_engine = PriorityEngine()
        self.strategy_selector = StrategySelector()
        self.delegation_manager = DelegationManager()
        self.memory = DistributedMemory()
        self.safety_monitor = SafetyMonitor() if enable_safety else None
        self.evolution_engine = EvolutionEngine() if enable_evolution else None

        # Infrastructure
        self.event_bus = create_eventbus(event_bus_backend)

        # State
        self.initialized = False
        self.stats = {
            'decisions_made': 0,
            'auto_resolved': 0,
            'delegated': 0,
            'escalated_to_human': 0,
            'safety_blocks': 0,
            'evolution_cycles': 0
        }

        logger.info("AI Orchestrator created")

    async def initialize(self) -> None:
        """
        Initialize all components.

        Must be called before using orchestrator.
        """
        if self.initialized:
            logger.warning("Orchestrator already initialized")
            return

        try:
            # Initialize memory
            await self.memory.initialize()
            logger.info("✅ Memory initialized")

            # Initialize context aggregator
            await self.context_aggregator.initialize()
            logger.info("✅ Context aggregator initialized")

            # Initialize strategy selector
            await self.strategy_selector.initialize(self.memory)
            logger.info("✅ Strategy selector initialized")

            # Initialize delegation manager
            await self.delegation_manager.initialize(self.event_bus)
            logger.info("✅ Delegation manager initialized")

            # Initialize safety monitor
            if self.safety_monitor:
                await self.safety_monitor.initialize()
                logger.info("✅ Safety monitor initialized")

            # Initialize evolution engine
            if self.evolution_engine:
                await self.evolution_engine.initialize(self.memory)
                logger.info("✅ Evolution engine initialized")

                # Start evolution cycles
                asyncio.create_task(self._run_evolution_cycles())

            # Subscribe to platform events
            await self._subscribe_to_events()

            self.initialized = True
            logger.info("🚀 AI Orchestrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    async def decide(
        self,
        situation: Dict[str, Any],
        tenant_id: str = 'default'
    ) -> Decision:
        """
        Make decision for given situation.

        This is the main entry point for decision-making.

        Args:
            situation: Current situation data
            tenant_id: Tenant identifier

        Returns:
            Decision: The decision made

        Raises:
            RuntimeError: If orchestrator not initialized

        Example:
            ```python
            situation = {
                'workflow_stuck': True,
                'workflow_id': 'bia_001',
                'stuck_duration_minutes': 30,
                'error_message': 'Timeout waiting for user input'
            }

            decision = await orchestrator.decide(situation)
            print(f"Action: {decision.action}")
            print(f"Rationale: {decision.rationale}")
            ```
        """
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

        try:
            start_time = datetime.utcnow()
            logger.info(f"Making decision for situation: {situation.get('workflow_id', 'unknown')}")

            # Step 1: Aggregate full context
            context = await self.context_aggregator.aggregate(situation, tenant_id)
            logger.debug(f"Context aggregated: {len(context.recent_events)} recent events")

            # Step 2: Assess priority
            priority = await self.priority_engine.assess_priority(context)
            logger.info(f"Priority: {priority.level.name} (score: {priority.score:.1f})")

            # Step 3: Select strategy
            strategies = await self.strategy_selector.select_strategies(context, priority)
            logger.info(f"Generated {len(strategies)} candidate strategies")

            if not strategies:
                # Fallback: escalate if no strategies found
                return self._create_fallback_decision(
                    priority,
                    "No strategies found for situation"
                )

            # Select best strategy
            best_strategy = strategies[0]
            logger.info(f"Selected strategy: {best_strategy.action} (confidence: {best_strategy.confidence:.2f})")

            # Step 4: Create decision
            decision = Decision(
                action=self._map_strategy_to_action(best_strategy, priority),
                rationale=best_strategy.rationale,
                priority=priority.level,
                confidence=best_strategy.confidence,
                strategies_considered=strategies,
                learned_from=best_strategy.learned_from,
                metadata={
                    'situation': situation,
                    'tenant_id': tenant_id,
                    'decision_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            )

            # Step 5: Safety validation
            if self.safety_monitor:
                safety_result = await self.safety_monitor.validate(decision, context)
                decision.safety_approved = safety_result.safe

                if not safety_result.safe:
                    logger.warning(f"Safety check FAILED: {len(safety_result.concerns)} concerns")
                    decision.action = ActionType.ESCALATE_HUMAN
                    decision.rationale = f"Safety concerns: {', '.join([c.description for c in safety_result.get_blocking_concerns()])}"
                    self.stats['safety_blocks'] += 1
                else:
                    logger.info("✅ Safety check passed")

            # Step 6: Store in memory
            await self._store_decision(decision, context)

            # Update stats
            self.stats['decisions_made'] += 1

            # Publish event
            await self._publish_decision_event(decision, tenant_id)

            logger.info(f"Decision made: {decision.action.value}")
            return decision

        except Exception as e:
            logger.error(f"Error making decision: {e}", exc_info=True)
            # Return safe fallback decision
            return self._create_emergency_decision(str(e))

    async def execute(self, decision: Decision) -> Dict[str, Any]:
        """
        Execute a decision.

        Args:
            decision: The decision to execute

        Returns:
            dict: Execution result

        Example:
            ```python
            decision = await orchestrator.decide(situation)
            result = await orchestrator.execute(decision)

            if result['success']:
                print(f"Executed: {result['message']}")
            ```
        """
        logger.info(f"Executing decision: {decision.action.value}")

        try:
            if decision.action == ActionType.AUTO_RESOLVE:
                result = await self._auto_resolve(decision)
                self.stats['auto_resolved'] += 1

            elif decision.action == ActionType.DELEGATE:
                result = await self.delegation_manager.delegate(decision)
                self.stats['delegated'] += 1

            elif decision.action == ActionType.ESCALATE_HUMAN:
                result = await self._escalate_to_human(decision)
                self.stats['escalated_to_human'] += 1

            elif decision.action == ActionType.WAIT_AND_MONITOR:
                result = await self._wait_and_monitor(decision)

            elif decision.action == ActionType.EMERGENCY_STOP:
                result = await self._emergency_stop(decision)

            else:
                result = {
                    'success': False,
                    'error': f"Unknown action type: {decision.action}"
                }

            # Store execution result
            await self._store_execution_result(decision, result)

            return result

        except Exception as e:
            logger.error(f"Error executing decision: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def shutdown(self) -> None:
        """Shutdown orchestrator and cleanup resources."""
        logger.info("Shutting down AI Orchestrator...")

        try:
            # Stop evolution engine
            if self.evolution_engine:
                await self.evolution_engine.shutdown()

            # Close event bus
            await self.event_bus.close()

            # Close memory
            await self.memory.close()

            logger.info("✅ AI Orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self.stats,
            'memory_stats': self.memory.get_stats(),
            'initialized': self.initialized
        }

    # ============================================
    # Private Methods
    # ============================================

    async def _subscribe_to_events(self) -> None:
        """Subscribe to relevant platform events."""
        # Subscribe to workflow events
        await self.event_bus.subscribe(
            'workflow.*',
            self._handle_workflow_event,
            consumer_group='orchestrator'
        )

        # Subscribe to system events
        await self.event_bus.subscribe(
            'system.*',
            self._handle_system_event,
            consumer_group='orchestrator'
        )

        logger.info("Subscribed to platform events")

    async def _handle_workflow_event(self, event: Event) -> None:
        """Handle workflow-related events."""
        logger.debug(f"Received workflow event: {event.type}")
        # Store in working memory
        await self.memory.working_memory.store_event(event)

    async def _handle_system_event(self, event: Event) -> None:
        """Handle system-level events."""
        logger.debug(f"Received system event: {event.type}")
        # Store in working memory
        await self.memory.working_memory.store_event(event)

    def _map_strategy_to_action(
        self,
        strategy: Strategy,
        priority: Priority
    ) -> ActionType:
        """Map strategy recommendation to action type."""
        # Low confidence = escalate
        if strategy.confidence < 0.7:
            return ActionType.ESCALATE_HUMAN

        # Critical priority with high confidence = auto resolve
        if priority.level == PriorityLevel.CRITICAL and strategy.confidence >= 0.9:
            return ActionType.AUTO_RESOLVE

        # High confidence = auto resolve or delegate
        if strategy.confidence >= 0.9:
            # Check if strategy suggests delegation
            if 'delegate' in strategy.action.lower():
                return ActionType.DELEGATE
            return ActionType.AUTO_RESOLVE

        # Medium confidence = delegate to specialist
        if strategy.confidence >= 0.7:
            return ActionType.DELEGATE

        # Default: wait and monitor
        return ActionType.WAIT_AND_MONITOR

    def _create_fallback_decision(
        self,
        priority: Priority,
        reason: str
    ) -> Decision:
        """Create fallback decision when normal flow fails."""
        return Decision(
            action=ActionType.ESCALATE_HUMAN,
            rationale=f"Fallback decision: {reason}",
            priority=priority.level,
            confidence=0.0,
            safety_approved=True,
            metadata={'fallback': True}
        )

    def _create_emergency_decision(self, error: str) -> Decision:
        """Create emergency decision for critical errors."""
        return Decision(
            action=ActionType.EMERGENCY_STOP,
            rationale=f"Emergency: {error}",
            priority=PriorityLevel.CRITICAL,
            confidence=1.0,
            safety_approved=True,
            metadata={'emergency': True, 'error': error}
        )

    async def _store_decision(
        self,
        decision: Decision,
        context: FullContext
    ) -> None:
        """Store decision in memory for learning."""
        await self.memory.short_term_memory.store_decision(decision, context)

    async def _store_execution_result(
        self,
        decision: Decision,
        result: Dict[str, Any]
    ) -> None:
        """Store execution result for learning."""
        await self.memory.short_term_memory.store_execution_result(
            decision.metadata.get('situation', {}),
            decision,
            result
        )

    async def _publish_decision_event(
        self,
        decision: Decision,
        tenant_id: str
    ) -> None:
        """Publish decision event to platform."""
        event = Event.create(
            event_type='orchestrator.decision_made',
            data=decision.to_dict(),
            source='ai-orchestrator',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH if decision.priority == PriorityLevel.CRITICAL else EventPriority.NORMAL
        )
        await self.event_bus.publish(event)

    async def _auto_resolve(self, decision: Decision) -> Dict[str, Any]:
        """Auto-resolve the issue."""
        logger.info("Auto-resolving...")
        # TODO: Implement auto-resolution logic
        return {
            'success': True,
            'action': 'auto_resolve',
            'message': decision.rationale
        }

    async def _escalate_to_human(self, decision: Decision) -> Dict[str, Any]:
        """Escalate to human operator."""
        logger.warning("Escalating to human...")
        # TODO: Send notification to human operators
        return {
            'success': True,
            'action': 'escalate_to_human',
            'message': f"Escalated: {decision.rationale}",
            'requires_human_intervention': True
        }

    async def _wait_and_monitor(self, decision: Decision) -> Dict[str, Any]:
        """Wait and monitor situation."""
        logger.info("Waiting and monitoring...")
        # TODO: Set up monitoring
        return {
            'success': True,
            'action': 'wait_and_monitor',
            'message': 'Monitoring situation'
        }

    async def _emergency_stop(self, decision: Decision) -> Dict[str, Any]:
        """Emergency stop - halt all operations."""
        logger.critical("EMERGENCY STOP TRIGGERED!")
        # TODO: Implement emergency stop logic
        return {
            'success': True,
            'action': 'emergency_stop',
            'message': 'Emergency stop executed',
            'critical': True
        }

    async def _run_evolution_cycles(self) -> None:
        """Run periodic evolution cycles in background."""
        if not self.evolution_engine:
            return

        while True:
            try:
                # Wait 24 hours between cycles
                await asyncio.sleep(86400)

                logger.info("Starting evolution cycle...")
                await self.evolution_engine.run_evolution_cycle()
                self.stats['evolution_cycles'] += 1
                logger.info("Evolution cycle complete")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in evolution cycle: {e}")
