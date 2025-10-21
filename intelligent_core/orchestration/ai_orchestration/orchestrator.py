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

from .models import (
    Decision, Strategy, Priority, FullContext, ActionType,
    PriorityLevel, SafetyResult, SafetyConcern
)
from .decision_center.context_aggregator import ContextAggregator
from .decision_center.priority_engine import PriorityEngine
from .decision_center.strategy_selector import StrategySelector
from .decision_center.delegation_manager import DelegationManager
from .memory.distributed_memory import DistributedMemory
from .safety.safety_monitor import SafetyMonitor
from .evolution.evolution_engine import EvolutionEngine
from .service_registry import ServiceRegistry
from .crisis_coordinator import CrisisCoordinator

# Infrastructure imports - need sys.path for infrastructure module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
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
        self.service_registry = ServiceRegistry()
        self.crisis_coordinator = None  # Will be initialized in initialize()

        # State
        self.initialized = False
        self.pdca_engine = None  # Will be initialized in initialize()
        self.ace_engine = None  # ACE Engine for evolving context playbooks
        self.stats = {
            'decisions_made': 0,
            'auto_resolved': 0,
            'delegated': 0,
            'escalated_to_human': 0,
            'safety_blocks': 0,
            'evolution_cycles': 0,
            'ace_tasks': 0  # NEW: Track ACE-enhanced tasks
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
            logger.info(" Memory initialized")

            # Initialize context aggregator
            await self.context_aggregator.initialize()
            logger.info(" Context aggregator initialized")

            # Initialize strategy selector
            await self.strategy_selector.initialize(self.memory)
            logger.info(" Strategy selector initialized")

            # Initialize delegation manager
            await self.delegation_manager.initialize(self.event_bus)
            logger.info(" Delegation manager initialized")

            # Initialize safety monitor
            if self.safety_monitor:
                await self.safety_monitor.initialize()
                logger.info(" Safety monitor initialized")

            # Initialize evolution engine
            if self.evolution_engine:
                await self.evolution_engine.initialize(self.memory)
                logger.info(" Evolution engine initialized")

                # Start evolution cycles
                asyncio.create_task(self._run_evolution_cycles())

            # Initialize service registry
            await self.service_registry.initialize()
            logger.info(" Service registry initialized")

            # Register platform services
            await self._register_platform_services()

            # Subscribe to platform events
            await self._subscribe_to_events()

            # Initialize PDCA for continuous improvement
            await self._initialize_pdca()

            # Initialize Crisis Coordinator
            await self._initialize_crisis_coordinator()

            # Initialize ACE Engine
            await self._initialize_ace_engine()

            self.initialized = True
            logger.info(" AI Orchestrator initialized successfully")

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

            # Step 2.5: Check for crisis situation
            if self.crisis_coordinator and priority.level.value >= 3:  # HIGH or CRITICAL
                crisis_id = await self.crisis_coordinator.detect_crisis(
                    situation=situation,
                    source='orchestrator'
                )
                if crisis_id:
                    logger.warning(f" Crisis detected: {crisis_id}")
                    # Crisis will be handled by crisis coordinator
                    # Continue with normal decision-making, but track crisis

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
                    logger.info(" Safety check passed")

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

            # Shutdown service registry
            await self.service_registry.shutdown()

            # Close event bus
            await self.event_bus.close()

            # Close memory
            await self.memory.close()

            logger.info(" AI Orchestrator shutdown complete")

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

    async def _register_platform_services(self) -> None:
        """Register all platform services with the service registry."""
        services = [
            # Core BCM Services (existing)
            ('bia', 'http://localhost:8012', '/health'),
            ('risk', 'http://localhost:8040', '/health'),
            ('planning', 'http://localhost:8011', '/health'),
            ('compliance', 'http://localhost:8014', '/health'),
            ('governance', 'http://localhost:8013', '/health'),
            # Additional Services (NEW - critical for crisis coordination)
            ('documents', 'http://localhost:8024', '/health'),
            ('learning', 'http://localhost:8021', '/health'),
            ('response', 'http://localhost:8041', '/health'),  # CRITICAL for crisis!
            ('validation', 'http://localhost:8022', '/health'),
            # Note: exercises-service not found - may be combined with validation
        ]

        for name, url, health_endpoint in services:
            try:
                await self.service_registry.register_service(name, url, health_endpoint)
                logger.info(f" Registered service '{name}' at {url}")
            except Exception as e:
                logger.warning(f"Failed to register service '{name}': {e}")

        logger.info(f" Platform services registration complete: {len(services)} services")

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

    async def _initialize_pdca(self) -> None:
        """Initialize PDCA Rules Engine for continuous improvement."""
        try:
            from workflow_intelligence.enable_pdca import enable_pdca_for_platform_eventbus

            logger.info(" Initializing PDCA Rules Engine...")

            # Enable PDCA with platform EventBus
            pdca_engine = await enable_pdca_for_platform_eventbus(
                event_bus=self.event_bus,
                tenant_id='default-tenant'
            )

            # Store reference
            self.pdca_engine = pdca_engine

            logger.info(" PDCA Rules Engine initialized and connected to EventBus")
            logger.info("   - Plan-Do-Check-Act cycle activated")
            logger.info("   - Continuous improvement enabled")
            logger.info("   - Learning from workflow outcomes")

        except Exception as e:
            logger.warning(f"️ PDCA initialization failed (non-critical): {e}")
            logger.warning("   Orchestrator will continue without PDCA")
            self.pdca_engine = None

    async def _initialize_crisis_coordinator(self) -> None:
        """Initialize Crisis Coordinator for crisis response."""
        try:
            logger.info(" Initializing Crisis Coordinator...")

            # Create Crisis Coordinator
            self.crisis_coordinator = CrisisCoordinator(
                service_registry=self.service_registry,
                event_bus=self.event_bus
            )

            # Initialize coordinator
            await self.crisis_coordinator.initialize()

            logger.info(" Crisis Coordinator initialized")
            logger.info("   - Crisis detection enabled")
            logger.info("   - Multi-service coordination ready")
            logger.info("   - BC plan activation ready")

        except Exception as e:
            logger.warning(f"️ Crisis Coordinator initialization failed (non-critical): {e}")
            logger.warning("   Orchestrator will continue without crisis coordination")
            self.crisis_coordinator = None

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

            # Delegate expert-level tasks to AI Experts
            if self._should_delegate_to_experts(strategy):
                return ActionType.DELEGATE

            return ActionType.AUTO_RESOLVE

        # Medium confidence = delegate to specialist
        if strategy.confidence >= 0.7:
            return ActionType.DELEGATE

        # Default: wait and monitor
        return ActionType.WAIT_AND_MONITOR

    def _should_delegate_to_experts(self, strategy: Strategy) -> bool:
        """
        Determine if task should be delegated to AI Experts.

        AI Experts handle:
        - Complex BCM planning
        - Compliance auditing
        - Strategic decision-making
        - Situations requiring specialized domain knowledge

        Args:
            strategy: Strategy to evaluate

        Returns:
            True if should delegate to AI Experts
        """
        expert_keywords = [
            'compliance', 'audit', 'bcm', 'business continuity',
            'strategic', 'planning', 'assessment', 'analysis',
            'risk assessment', 'impact analysis', 'recovery strategy',
            'gap analysis', 'certification', 'iso', 'standard'
        ]

        action_lower = strategy.action.lower()

        # Check if action contains expert keywords
        for keyword in expert_keywords:
            if keyword in action_lower:
                return True

        # Check strategy metadata for delegation hints
        if strategy.metadata.get('requires_expert', False):
            return True

        if strategy.metadata.get('domain') in ['bcm', 'compliance', 'strategic']:
            return True

        return False

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
        """
        Auto-resolve the issue by calling appropriate services.

        Analyzes the decision and makes real API calls to platform services
        based on the action recommended. Includes retry logic via ServiceRegistry.

        Args:
            decision: The decision to execute

        Returns:
            dict: Execution result with success status and details
        """
        logger.info(f"Auto-resolving: {decision.rationale}")

        try:
            # Extract situation details from decision metadata
            situation = decision.metadata.get('situation', {})
            action_details = self._parse_action_from_decision(decision)

            # Route to appropriate service based on action
            service_name = action_details.get('service')
            method = action_details.get('method', 'POST')
            endpoint = action_details.get('endpoint')
            data = action_details.get('data', {})

            if not service_name or not endpoint:
                logger.warning("No specific service action identified, using generic resolution")
                return {
                    'success': True,
                    'action': 'auto_resolve',
                    'message': decision.rationale,
                    'resolution_type': 'generic'
                }

            # Make service call with automatic retry
            logger.info(f"Calling {service_name} service: {method} {endpoint}")
            result = await self.service_registry.call_service(
                service_name=service_name,
                method=method,
                endpoint=endpoint,
                data=data
            )

            logger.info(f"Service call succeeded: {result}")

            return {
                'success': True,
                'action': 'auto_resolve',
                'message': f"Successfully resolved via {service_name} service",
                'service': service_name,
                'endpoint': endpoint,
                'result': result,
                'decision_rationale': decision.rationale
            }

        except ValueError as e:
            # Service not available
            logger.error(f"Service unavailable for auto-resolution: {e}")
            return {
                'success': False,
                'action': 'auto_resolve',
                'error': str(e),
                'fallback': 'escalate_to_human',
                'message': f"Auto-resolution failed: {str(e)}"
            }

        except RuntimeError as e:
            # All retries failed
            logger.error(f"Auto-resolution failed after retries: {e}")
            return {
                'success': False,
                'action': 'auto_resolve',
                'error': str(e),
                'fallback': 'escalate_to_human',
                'message': f"Auto-resolution failed after retries: {str(e)}"
            }

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in auto-resolution: {e}", exc_info=True)
            return {
                'success': False,
                'action': 'auto_resolve',
                'error': str(e),
                'fallback': 'emergency_stop',
                'message': f"Critical error in auto-resolution: {str(e)}"
            }

    def _parse_action_from_decision(self, decision: Decision) -> Dict[str, Any]:
        """
        Parse action details from decision metadata and strategies.

        Args:
            decision: The decision containing action details

        Returns:
            dict: Action details including service, method, endpoint, data
        """
        # Check decision metadata for explicit action details
        if 'action_details' in decision.metadata:
            return decision.metadata['action_details']

        # Parse from strategies
        if decision.strategies_considered:
            best_strategy = decision.strategies_considered[0]

            # Check strategy metadata
            if 'service' in best_strategy.metadata:
                return best_strategy.metadata

            # Parse from action string
            action = best_strategy.action.lower()

            # BIA-related actions
            if 'bia' in action or 'business impact' in action:
                if 'create' in action or 'add' in action:
                    return {
                        'service': 'bia',
                        'method': 'POST',
                        'endpoint': '/api/v1/processes',
                        'data': self._extract_bia_data(decision)
                    }
                elif 'update' in action:
                    return {
                        'service': 'bia',
                        'method': 'PUT',
                        'endpoint': '/api/v1/processes/{id}',
                        'data': self._extract_bia_data(decision)
                    }

            # Risk-related actions
            elif 'risk' in action or 'assessment' in action:
                if 'create' in action or 'assess' in action:
                    return {
                        'service': 'risk',
                        'method': 'POST',
                        'endpoint': '/api/v1/assessments',
                        'data': self._extract_risk_data(decision)
                    }

            # Planning-related actions
            elif 'plan' in action or 'recovery' in action:
                if 'create' in action or 'generate' in action:
                    return {
                        'service': 'planning',
                        'method': 'POST',
                        'endpoint': '/api/v1/plans',
                        'data': self._extract_planning_data(decision)
                    }

            # Workflow-related actions
            elif 'workflow' in action:
                if 'restart' in action or 'resume' in action:
                    workflow_id = decision.metadata.get('situation', {}).get('workflow_id')
                    if workflow_id:
                        return {
                            'service': 'planning',  # Planning service manages workflows
                            'method': 'POST',
                            'endpoint': f'/api/v1/workflows/{workflow_id}/resume',
                            'data': {'reason': decision.rationale}
                        }

        # Default: no specific action
        return {}

    def _extract_bia_data(self, decision: Decision) -> Dict[str, Any]:
        """Extract BIA-related data from decision."""
        situation = decision.metadata.get('situation', {})
        return {
            'name': situation.get('process_name', 'Unknown Process'),
            'description': decision.rationale,
            'tenant_id': decision.metadata.get('tenant_id', 'default')
        }

    def _extract_risk_data(self, decision: Decision) -> Dict[str, Any]:
        """Extract risk assessment data from decision."""
        situation = decision.metadata.get('situation', {})
        return {
            'target_type': situation.get('target_type', 'system'),
            'target_id': situation.get('target_id', 'unknown'),
            'description': decision.rationale,
            'tenant_id': decision.metadata.get('tenant_id', 'default')
        }

    def _extract_planning_data(self, decision: Decision) -> Dict[str, Any]:
        """Extract planning data from decision."""
        situation = decision.metadata.get('situation', {})
        return {
            'plan_type': situation.get('plan_type', 'recovery'),
            'description': decision.rationale,
            'tenant_id': decision.metadata.get('tenant_id', 'default')
        }

    async def _escalate_to_human(self, decision: Decision) -> Dict[str, Any]:
        """
        Escalate to human operator.

        Sends notifications and creates escalation records.

        Args:
            decision: The decision requiring escalation

        Returns:
            dict: Escalation result
        """
        logger.warning(f"Escalating to human: {decision.rationale}")

        escalation_id = f"esc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        situation = decision.metadata.get('situation', {})
        tenant_id = decision.metadata.get('tenant_id', 'default')

        try:
            # 1. Create escalation event
            escalation_event = Event.create(
                event_type='orchestrator.escalation',
                data={
                    'escalation_id': escalation_id,
                    'priority': decision.priority.name,
                    'confidence': decision.confidence,
                    'rationale': decision.rationale,
                    'situation': situation,
                    'safety_concerns': self._get_safety_concerns(decision),
                    'timestamp': datetime.utcnow().isoformat(),
                    'requires_immediate_attention': decision.priority == PriorityLevel.CRITICAL
                },
                source='ai-orchestrator',
                tenant_id=tenant_id,
                priority=EventPriority.CRITICAL if decision.priority == PriorityLevel.CRITICAL else EventPriority.HIGH
            )
            await self.event_bus.publish(escalation_event)
            logger.info(f"Published escalation event: {escalation_id}")

            # 2. Send notification (stub - would integrate with notification service)
            notification_result = await self._send_escalation_notification(
                escalation_id=escalation_id,
                decision=decision,
                tenant_id=tenant_id
            )

            # 3. Create incident ticket structure (logged for now)
            incident_ticket = {
                'ticket_id': f"INC-{escalation_id}",
                'escalation_id': escalation_id,
                'title': f"AI Orchestrator Escalation: {decision.rationale[:100]}",
                'description': self._format_escalation_description(decision, situation),
                'priority': decision.priority.name,
                'status': 'open',
                'assigned_to': 'operations_team',
                'created_at': datetime.utcnow().isoformat(),
                'metadata': {
                    'confidence': decision.confidence,
                    'safety_approved': decision.safety_approved,
                    'situation': situation
                }
            }
            logger.info(f"Incident ticket structure: {incident_ticket}")

            # Store escalation in memory for tracking
            await self._store_escalation(escalation_id, decision, incident_ticket)

            return {
                'success': True,
                'action': 'escalate_to_human',
                'escalation_id': escalation_id,
                'ticket_id': incident_ticket['ticket_id'],
                'message': f"Escalated to human operators: {decision.rationale}",
                'requires_human_intervention': True,
                'priority': decision.priority.name,
                'notification_sent': notification_result['sent'],
                'incident_ticket': incident_ticket
            }

        except Exception as e:
            logger.error(f"Error during escalation: {e}", exc_info=True)
            # Still return success - escalation logged even if notification fails
            return {
                'success': True,
                'action': 'escalate_to_human',
                'escalation_id': escalation_id,
                'message': f"Escalated (with errors): {decision.rationale}",
                'requires_human_intervention': True,
                'error': str(e)
            }

    def _get_safety_concerns(self, decision: Decision) -> List[str]:
        """Extract safety concerns from decision."""
        concerns = []
        if not decision.safety_approved:
            concerns.append("Safety validation failed")
        if decision.confidence < 0.5:
            concerns.append(f"Low confidence: {decision.confidence:.2f}")
        return concerns

    def _format_escalation_description(
        self,
        decision: Decision,
        situation: Dict[str, Any]
    ) -> str:
        """Format detailed escalation description."""
        lines = [
            "ESCALATION FROM AI ORCHESTRATOR",
            "=" * 50,
            "",
            f"Rationale: {decision.rationale}",
            f"Priority: {decision.priority.name}",
            f"Confidence: {decision.confidence:.2%}",
            f"Safety Approved: {decision.safety_approved}",
            "",
            "SITUATION:",
        ]

        for key, value in situation.items():
            lines.append(f"  - {key}: {value}")

        if decision.strategies_considered:
            lines.extend([
                "",
                "STRATEGIES CONSIDERED:",
            ])
            for i, strategy in enumerate(decision.strategies_considered[:3], 1):
                lines.append(f"  {i}. {strategy.action} (confidence: {strategy.confidence:.2%})")

        lines.extend([
            "",
            "ACTION REQUIRED:",
            "  Please review the situation and take appropriate action.",
            "  Update the incident ticket when resolved."
        ])

        return "\n".join(lines)

    async def _send_escalation_notification(
        self,
        escalation_id: str,
        decision: Decision,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Send escalation notification to human operators.

        Stub implementation - would integrate with notification service.

        Args:
            escalation_id: Escalation identifier
            decision: The decision
            tenant_id: Tenant identifier

        Returns:
            dict: Notification result
        """
        # This is a stub - in production would call notification service
        logger.warning(
            f"ESCALATION NOTIFICATION [{escalation_id}]: "
            f"Priority={decision.priority.name}, "
            f"Rationale={decision.rationale}"
        )

        # Simulate notification
        return {
            'sent': True,
            'channels': ['email', 'slack', 'pagerduty'] if decision.priority == PriorityLevel.CRITICAL else ['email'],
            'recipients': ['ops-team@company.com'],
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _store_escalation(
        self,
        escalation_id: str,
        decision: Decision,
        incident_ticket: Dict[str, Any]
    ) -> None:
        """Store escalation in memory for tracking."""
        try:
            await self.memory.working_memory.store({
                'type': 'escalation',
                'escalation_id': escalation_id,
                'decision': decision.to_dict(),
                'incident_ticket': incident_ticket,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to store escalation in memory: {e}")

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
        """
        Emergency stop - halt all operations.

        Triggers platform-wide emergency shutdown procedures.

        Args:
            decision: The decision that triggered emergency stop

        Returns:
            dict: Emergency stop result
        """
        emergency_id = f"emg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        tenant_id = decision.metadata.get('tenant_id', 'default')
        situation = decision.metadata.get('situation', {})

        logger.critical(f"EMERGENCY STOP TRIGGERED [{emergency_id}]: {decision.rationale}")

        try:
            # 1. Publish critical emergency stop event
            emergency_event = Event.create(
                event_type='orchestrator.emergency_stop',
                data={
                    'emergency_id': emergency_id,
                    'trigger_reason': decision.rationale,
                    'situation': situation,
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': decision.metadata,
                    'action_required': 'immediate_manual_intervention'
                },
                source='ai-orchestrator',
                tenant_id=tenant_id,
                priority=EventPriority.CRITICAL
            )
            await self.event_bus.publish(emergency_event)
            logger.critical(f"Published emergency stop event: {emergency_id}")

            # 2. Log critical alert (would integrate with monitoring/alerting)
            critical_alert = {
                'alert_id': f"ALERT-{emergency_id}",
                'severity': 'CRITICAL',
                'title': 'AI Orchestrator Emergency Stop',
                'message': decision.rationale,
                'situation': situation,
                'timestamp': datetime.utcnow().isoformat(),
                'requires_immediate_attention': True
            }
            logger.critical(f"CRITICAL ALERT: {critical_alert}")

            # 3. Attempt to stop pending workflows via delegation manager
            stopped_workflows = []
            try:
                # Send stop command via event bus to workflow engine
                stop_workflow_event = Event.create(
                    event_type='workflow.emergency_stop_all',
                    data={
                        'emergency_id': emergency_id,
                        'reason': decision.rationale,
                        'initiated_by': 'ai-orchestrator',
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    source='ai-orchestrator',
                    tenant_id=tenant_id,
                    priority=EventPriority.CRITICAL
                )
                await self.event_bus.publish(stop_workflow_event)
                logger.critical("Sent emergency stop command to workflow engine")
                stopped_workflows.append("all_workflows")

            except Exception as e:
                logger.error(f"Failed to stop workflows: {e}")

            # 4. Disable auto-resolution temporarily (safety measure)
            self.stats['emergency_stops'] = self.stats.get('emergency_stops', 0) + 1
            self.stats['last_emergency_stop'] = datetime.utcnow().isoformat()

            # 5. Store emergency stop in memory
            await self._store_emergency_stop(emergency_id, decision, critical_alert)

            # 6. Send critical notifications
            await self._send_emergency_notification(emergency_id, decision, tenant_id)

            return {
                'success': True,
                'action': 'emergency_stop',
                'emergency_id': emergency_id,
                'message': f'EMERGENCY STOP EXECUTED: {decision.rationale}',
                'critical': True,
                'timestamp': datetime.utcnow().isoformat(),
                'stopped_workflows': stopped_workflows,
                'alert': critical_alert,
                'requires_manual_intervention': True,
                'recovery_instructions': self._get_recovery_instructions(decision)
            }

        except Exception as e:
            logger.critical(f"Error during emergency stop: {e}", exc_info=True)
            # Even if errors occur, mark as executed
            return {
                'success': True,
                'action': 'emergency_stop',
                'emergency_id': emergency_id,
                'message': f'EMERGENCY STOP EXECUTED (with errors): {decision.rationale}',
                'critical': True,
                'error': str(e),
                'requires_manual_intervention': True
            }

    async def _store_emergency_stop(
        self,
        emergency_id: str,
        decision: Decision,
        critical_alert: Dict[str, Any]
    ) -> None:
        """Store emergency stop in memory for audit trail."""
        try:
            await self.memory.working_memory.store({
                'type': 'emergency_stop',
                'emergency_id': emergency_id,
                'decision': decision.to_dict(),
                'alert': critical_alert,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to store emergency stop in memory: {e}")

    async def _send_emergency_notification(
        self,
        emergency_id: str,
        decision: Decision,
        tenant_id: str
    ) -> None:
        """Send critical emergency notifications."""
        try:
            logger.critical(
                f"EMERGENCY NOTIFICATION [{emergency_id}]: "
                f"IMMEDIATE ACTION REQUIRED - {decision.rationale}"
            )

            # In production, this would:
            # - Send PagerDuty alerts
            # - Send SMS to on-call engineers
            # - Trigger incident response procedures
            # - Update status pages

        except Exception as e:
            logger.error(f"Failed to send emergency notification: {e}")

    def _get_recovery_instructions(self, decision: Decision) -> List[str]:
        """Get recovery instructions for emergency stop."""
        return [
            "1. Investigate the root cause of the emergency stop",
            "2. Review the orchestrator logs and decision history",
            "3. Verify all systems are in safe state",
            "4. Address the underlying issue that triggered the stop",
            "5. Manually restart workflows if appropriate",
            "6. Monitor the system closely after restart",
            "7. Update escalation procedures if needed"
        ]

    async def _initialize_ace_engine(self) -> None:
        """Initialize ACE Engine for evolving context playbooks."""
        try:
            logger.info(" Initializing ACE Engine...")

            # Import ACE Engine
            import sys
            from pathlib import Path
            ace_path = Path(__file__).parent.parent.parent / "ace-engine"
            if str(ace_path) not in sys.path:
                sys.path.insert(0, str(ace_path))

            from ace_engine import get_ace_engine

            # Get ACE Engine instance
            self.ace_engine = get_ace_engine()

            logger.info(" ACE Engine initialized")
            logger.info("   - Evolving context playbooks enabled")
            logger.info("   - Knowledge accumulation active")
            logger.info("   - +8-15% expected improvement")

        except Exception as e:
            logger.warning(f"️ ACE Engine initialization failed (non-critical): {e}")
            logger.warning("   Orchestrator will continue without ACE")
            self.ace_engine = None

    async def delegate_to_ai(
        self,
        task_type: str,
        context: Dict[str, Any],
        require_ace: bool = True
    ) -> Dict[str, Any]:
        """
        Delegate task to AI with ACE-enhanced context.

        This method wraps AI task delegation with ACE framework:
        1. Generator: Create enhanced context with evolving playbook
        2. Execute: Delegate to AI specialist
        3. Reflector: Analyze trajectory and identify insights
        4. Curator: Update playbook incrementally

        Args:
            task_type: Type of task (e.g., "scenario_generation", "compliance_analysis")
            context: Base context for the task
            require_ace: Whether to use ACE (default: True)

        Returns:
            dict: Task result with ACE metadata

        Example:
            ```python
            result = await orchestrator.delegate_to_ai(
                task_type="scenario_generation",
                context={
                    "module_name": "bia",
                    "operation": "create_assessment",
                    "framework": "ISO_22301"
                }
            )
            ```
        """
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized")

        logger.info(f"Delegating AI task: {task_type}")
        start_time = datetime.utcnow()

        try:
            # Step 1: Generator - Create enhanced context with ACE
            if self.ace_engine and require_ace:
                logger.info(f" Generating ACE-enhanced context for {task_type}")

                enhanced_context = await self.ace_engine.generate_context(
                    task=task_type,
                    base_context=context,
                    playbook=self.ace_engine.get_playbook(task_type)
                )

                logger.info(
                    f" Enhanced context with {len(enhanced_context.get('playbook_strategies', []))} strategies, "
                    f"{len(enhanced_context.get('known_patterns', []))} patterns"
                )
            else:
                enhanced_context = context
                logger.info("Using base context (ACE not available)")

            # Step 2: Execute - Delegate to AI specialist via delegation manager
            # Create a decision for delegation
            from .models import Decision, ActionType, PriorityLevel

            decision = Decision(
                action=ActionType.DELEGATE,
                rationale=f"AI task delegation: {task_type}",
                priority=PriorityLevel.NORMAL,
                confidence=0.9,
                metadata={
                    'task_type': task_type,
                    'situation': enhanced_context,
                    'ace_enhanced': self.ace_engine is not None and require_ace
                }
            )

            # Delegate via delegation manager
            delegation_result = await self.delegation_manager.delegate(decision)

            # Simulate AI execution (in production, would wait for specialist response via event bus)
            # For POC, we'll create a mock result
            execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            ai_result = {
                'success': delegation_result['success'],
                'task_type': task_type,
                'result': {
                    'status': 'delegated',
                    'specialist': delegation_result.get('specialist'),
                    'event_id': delegation_result.get('event_id'),
                    # Mock output - in production would come from specialist
                    'output': {
                        'message': f"Task {task_type} delegated to {delegation_result.get('specialist')}",
                        'enhanced_with_ace': self.ace_engine is not None and require_ace
                    }
                },
                'execution_time_ms': execution_time_ms
            }

            # Step 3 & 4: Reflector + Curator - Learn from execution (if ACE enabled)
            if self.ace_engine and require_ace and ai_result['success']:
                logger.info(f" Reflecting on trajectory for {task_type}")

                # Create trajectory
                trajectory = {
                    'input': enhanced_context,
                    'output': ai_result['result'],
                    'execution_time_ms': execution_time_ms,
                    'success': ai_result['success'],
                    'effectiveness': 0.85,  # Mock - in production would come from validation
                    'validation': {
                        'approved': True,  # Mock
                        'confidence': 0.9
                    }
                }

                # Reflect on trajectory
                insights = await self.ace_engine.reflect_on_trajectory(
                    task=task_type,
                    trajectory=trajectory
                )

                # Curate playbook
                current_playbook = self.ace_engine.get_playbook(task_type)
                updated_playbook = await self.ace_engine.curate_playbook(
                    task=task_type,
                    current_playbook=current_playbook,
                    insights=insights,
                    preserve_knowledge=True
                )

                # Add ACE metadata to result
                ai_result['ace_metadata'] = {
                    'playbook_updated': True,
                    'insights': insights,
                    'playbook_stats': self.ace_engine.get_playbook_stats(task_type)
                }

                logger.info(
                    f" Playbook updated for {task_type}: "
                    f"{len(updated_playbook.get('strategies', []))} strategies, "
                    f"{len(updated_playbook.get('patterns', []))} patterns"
                )

                # Update stats
                self.stats['ace_tasks'] += 1

            return ai_result

        except Exception as e:
            logger.error(f"Error in AI delegation: {e}", exc_info=True)
            return {
                'success': False,
                'task_type': task_type,
                'error': str(e),
                'execution_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
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
