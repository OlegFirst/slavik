"""
Self-Aware Service Base Class

Enables services to make intelligent decisions about event handling,
load management, and collaboration with other services.

This is the foundation for graceful event choreography in AI Platform ISO.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

from .health_monitor import HealthMonitor, HealthStatus
from .capability_registry import CapabilityRegistry, Capability, CapabilityMatch
from .load_manager import LoadManager, LoadLevel, LoadPolicy
from .collaboration_mixin import CollaborationMixin, CollaborationDecision
from .metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for handling decisions"""
    CRITICAL = "critical"      # Must handle regardless of load
    HIGH = "high"              # Handle if capacity available
    NORMAL = "normal"          # Handle based on load policy
    LOW = "low"                # Defer if under load
    BACKGROUND = "background"  # Only when idle


class HandlingDecision(Enum):
    """Decision on how to handle an event"""
    HANDLE = "handle"                    # Process immediately
    DEFER = "defer"                      # Queue for later
    DELEGATE = "delegate"                # Pass to another service
    COLLABORATE = "collaborate"          # Handle with consensus
    REJECT = "reject"                    # Cannot handle
    DEGRADE = "degrade"                  # Handle with reduced quality


@dataclass
class EventContext:
    """Context for event handling decision"""
    event_type: str
    event_data: Dict[str, Any]
    tenant_id: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HandlingResult:
    """Result of event handling decision"""
    decision: HandlingDecision
    handler: Optional[Callable] = None
    delegate_to: Optional[str] = None
    collaborate_with: Optional[List[str]] = None
    defer_until: Optional[datetime] = None
    reasoning: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SelfAwareService:
    """
    Self-aware service base class.

    Provides:
    - Health monitoring
    - Capability tracking
    - Load management
    - Intelligent event handling decisions
    - Service collaboration
    - Graceful degradation

    Usage:
        class BIAService(SelfAwareService):
            def __init__(self):
                super().__init__(
                    service_name="bia",
                    capabilities=["bia.assessment", "bia.analysis"]
                )

            async def handle_assessment_event(self, ctx: EventContext):
                # Custom handling logic
                pass
    """

    def __init__(
        self,
        service_name: str,
        capabilities: List[str],
        load_policy: Optional[LoadPolicy] = None,
        enable_ai_decisions: bool = True,
        enable_collaboration: bool = True
    ):
        """
        Initialize self-aware service.

        Args:
            service_name: Unique service identifier
            capabilities: List of capabilities this service provides
            load_policy: Custom load management policy
            enable_ai_decisions: Use AI for decision making
            enable_collaboration: Enable service collaboration
        """
        self.service_name = service_name
        self.enable_ai_decisions = enable_ai_decisions
        self.enable_collaboration = enable_collaboration

        # Initialize components
        self.health_monitor = HealthMonitor(service_name)
        self.capability_registry = CapabilityRegistry()
        self.load_manager = LoadManager(service_name, load_policy)
        self.collaboration = CollaborationMixin(service_name) if enable_collaboration else None

        # Register capabilities
        for cap in capabilities:
            self.capability_registry.register(
                Capability(
                    name=cap,
                    service=service_name,
                    enabled=True
                )
            )

        # Event handlers registry
        self._handlers: Dict[str, Callable] = {}
        self._pattern_handlers: List[tuple[str, Callable]] = []  # For regex patterns

        # Metrics
        self._metrics = {
            "events_received": 0,
            "events_handled": 0,
            "events_deferred": 0,
            "events_delegated": 0,
            "events_rejected": 0,
            "collaborations": 0,
            "degradations": 0
        }

        # State
        self._degraded_mode = False
        self._essential_capabilities: Set[str] = set()

        # Metrics
        self.metrics_collector = get_metrics_collector(service_name)

        logger.info(f"SelfAwareService initialized: {service_name} with {len(capabilities)} capabilities")

    def register_handler(self, event_type: str, handler: Callable, priority: EventPriority = EventPriority.NORMAL):
        """
        Register an event handler.

        Args:
            event_type: Event type to handle (supports wildcards: "bia.*")
            handler: Async function to handle the event
            priority: Default priority for this event type
        """
        if "*" in event_type:
            self._pattern_handlers.append((event_type, handler))
        else:
            self._handlers[event_type] = handler

        logger.debug(f"Registered handler for {event_type} with priority {priority.value}")

    def mark_essential(self, capability: str):
        """Mark a capability as essential (cannot be degraded)"""
        self._essential_capabilities.add(capability)

    async def on_event(self, event_type: str, event_data: Dict[str, Any], **kwargs) -> HandlingResult:
        """
        Main event handler - makes intelligent decision about event handling.

        This is the core self-awareness logic:
        1. Should I handle this? (capability match)
        2. Can I handle this? (health + load)
        3. How should I handle this? (priority + policy)
        4. Should I collaborate? (consensus needed)

        Args:
            event_type: Type of event
            event_data: Event payload
            **kwargs: Additional context (tenant_id, priority, etc.)

        Returns:
            HandlingResult with decision and reasoning
        """
        self._metrics["events_received"] += 1

        # Record metrics
        priority = kwargs.get("priority", EventPriority.NORMAL)
        self.metrics_collector.record_event_received(event_type, priority.value)

        # Build event context
        ctx = EventContext(
            event_type=event_type,
            event_data=event_data,
            tenant_id=kwargs.get("tenant_id"),
            priority=kwargs.get("priority", EventPriority.NORMAL),
            correlation_id=kwargs.get("correlation_id", str(uuid.uuid4())),
            retry_count=kwargs.get("retry_count", 0),
            metadata=kwargs.get("metadata", {})
        )

        try:
            # Step 1: Should I handle this? (Capability check)
            should_handle = await self.should_handle(ctx)
            if not should_handle:
                self._metrics["events_rejected"] += 1
                return HandlingResult(
                    decision=HandlingDecision.REJECT,
                    reasoning=f"Service {self.service_name} does not have capability for {event_type}"
                )

            # Step 2: Can I handle this? (Health + Load check)
            can_handle = await self.can_handle(ctx)
            if not can_handle:
                # Try to delegate or defer
                return await self._handle_overload(ctx)

            # Step 3: Should I collaborate? (For complex/critical events)
            if self.enable_collaboration and await self._should_collaborate(ctx):
                return await self._initiate_collaboration(ctx)

            # Step 4: Get handler and execute
            handler = self._find_handler(event_type)
            if not handler:
                return HandlingResult(
                    decision=HandlingDecision.REJECT,
                    reasoning=f"No handler registered for {event_type}"
                )

            self._metrics["events_handled"] += 1
            return HandlingResult(
                decision=HandlingDecision.HANDLE,
                handler=handler,
                reasoning=f"Service {self.service_name} handling {event_type}",
                confidence=1.0
            )

        except Exception as e:
            logger.error(f"Error in event decision for {event_type}: {e}", exc_info=True)
            return HandlingResult(
                decision=HandlingDecision.REJECT,
                reasoning=f"Error: {str(e)}",
                confidence=0.0
            )

    async def should_handle(self, ctx: EventContext) -> bool:
        """
        Determine if this service should handle the event.

        Uses:
        - Capability matching
        - AI-based pattern recognition (if enabled)
        - Business rules

        Args:
            ctx: Event context

        Returns:
            True if service should handle this event
        """
        # Check capability match
        matches = self.capability_registry.find_capabilities(ctx.event_type)
        if not matches:
            return False

        # Check if any match is for this service
        for match in matches:
            if match.capability.service == self.service_name and match.capability.enabled:
                return True

        # AI-based decision (if enabled)
        if self.enable_ai_decisions:
            ai_decision = await self._ai_should_handle(ctx)
            if ai_decision is not None:
                return ai_decision

        return False

    async def can_handle(self, ctx: EventContext) -> bool:
        """
        Determine if this service CAN handle the event right now.

        Considers:
        - Current health status
        - Current load level
        - Event priority vs load policy

        Args:
            ctx: Event context

        Returns:
            True if service has capacity to handle
        """
        # Check health
        health_status = await self.health_monitor.get_status()
        if health_status.status == HealthStatus.DOWN:
            logger.warning(f"{self.service_name} is DOWN - cannot handle events")
            return False

        # Critical events always accepted (if healthy)
        if ctx.priority == EventPriority.CRITICAL:
            return True

        # Check load
        load_level = await self.load_manager.get_load_level()

        # Degraded status - only essential
        if health_status.status == HealthStatus.DEGRADED:
            return ctx.priority in [EventPriority.CRITICAL, EventPriority.HIGH]

        # Load-based decision
        if load_level == LoadLevel.CRITICAL:
            return ctx.priority == EventPriority.CRITICAL
        elif load_level == LoadLevel.HIGH:
            return ctx.priority in [EventPriority.CRITICAL, EventPriority.HIGH]
        elif load_level == LoadLevel.MEDIUM:
            return ctx.priority != EventPriority.BACKGROUND

        return True

    async def degrade_gracefully(self, reason: str = "High load"):
        """
        Enter graceful degradation mode.

        - Disable non-essential capabilities
        - Queue non-critical events
        - Notify other services

        Args:
            reason: Reason for degradation
        """
        if self._degraded_mode:
            return

        logger.warning(f"⚠️ {self.service_name} entering degraded mode: {reason}")
        self._degraded_mode = True
        self._metrics["degradations"] += 1

        # Disable non-essential capabilities
        for cap_name in self.capability_registry.list_capabilities():
            if cap_name not in self._essential_capabilities:
                cap = self.capability_registry.get_capability(cap_name)
                if cap:
                    cap.enabled = False
                    logger.info(f"Disabled non-essential capability: {cap_name}")

        # Update health status
        await self.health_monitor.set_degraded(reason)

        # Notify collaboration partners
        if self.collaboration:
            await self.collaboration.broadcast_status("degraded", {"reason": reason})

    async def recover_from_degradation(self):
        """
        Exit graceful degradation mode.

        - Re-enable capabilities
        - Process deferred events
        - Notify other services
        """
        if not self._degraded_mode:
            return

        logger.info(f"✅ {self.service_name} recovering from degraded mode")
        self._degraded_mode = False

        # Re-enable all capabilities
        for cap_name in self.capability_registry.list_capabilities():
            cap = self.capability_registry.get_capability(cap_name)
            if cap:
                cap.enabled = True

        # Update health status
        await self.health_monitor.set_healthy()

        # Notify collaboration partners
        if self.collaboration:
            await self.collaboration.broadcast_status("healthy", {})

    async def collaborate_with(
        self,
        other_services: List[str],
        decision_context: Dict[str, Any]
    ) -> CollaborationDecision:
        """
        Collaborate with other services for consensus decision.

        Args:
            other_services: List of service names to collaborate with
            decision_context: Context for the decision

        Returns:
            CollaborationDecision with consensus result
        """
        if not self.collaboration:
            raise RuntimeError("Collaboration not enabled for this service")

        self._metrics["collaborations"] += 1

        return await self.collaboration.request_consensus(
            other_services,
            decision_context
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            **self._metrics,
            "service_name": self.service_name,
            "degraded_mode": self._degraded_mode,
            "health": self.health_monitor.get_status_sync(),
            "load": self.load_manager.get_load_level_sync(),
            "capabilities": len(self.capability_registry.list_capabilities())
        }

    # Private methods

    async def _handle_overload(self, ctx: EventContext) -> HandlingResult:
        """Handle overload situation - delegate or defer"""
        # Try to find another service to delegate to
        if self.collaboration:
            alternatives = await self.collaboration.find_alternative_handlers(ctx.event_type)
            if alternatives:
                self._metrics["events_delegated"] += 1
                return HandlingResult(
                    decision=HandlingDecision.DELEGATE,
                    delegate_to=alternatives[0],
                    reasoning=f"Service overloaded, delegating to {alternatives[0]}"
                )

        # Otherwise defer
        self._metrics["events_deferred"] += 1
        return HandlingResult(
            decision=HandlingDecision.DEFER,
            defer_until=datetime.utcnow(),  # TODO: Calculate based on load
            reasoning="Service overloaded, deferring event"
        )

    async def _should_collaborate(self, ctx: EventContext) -> bool:
        """Determine if event needs collaboration"""
        # Critical events may need consensus
        if ctx.priority == EventPriority.CRITICAL:
            return True

        # Events with specific metadata
        if ctx.metadata.get("requires_consensus"):
            return True

        return False

    async def _initiate_collaboration(self, ctx: EventContext) -> HandlingResult:
        """Initiate collaboration for event handling"""
        # Find related services
        related = await self.collaboration.find_related_services(ctx.event_type)

        if not related:
            # No collaboration needed, handle alone
            return HandlingResult(
                decision=HandlingDecision.HANDLE,
                handler=self._find_handler(ctx.event_type),
                reasoning="No collaboration partners found"
            )

        self._metrics["collaborations"] += 1
        return HandlingResult(
            decision=HandlingDecision.COLLABORATE,
            collaborate_with=related,
            reasoning=f"Collaborating with {len(related)} services"
        )

    def _find_handler(self, event_type: str) -> Optional[Callable]:
        """Find handler for event type (supports wildcards)"""
        # Exact match first
        if event_type in self._handlers:
            return self._handlers[event_type]

        # Pattern matching
        for pattern, handler in self._pattern_handlers:
            if self._match_pattern(event_type, pattern):
                return handler

        return None

    def _match_pattern(self, event_type: str, pattern: str) -> bool:
        """Simple wildcard matching (e.g., "bia.*" matches "bia.assessment.completed")"""
        import re
        regex = pattern.replace(".", r"\.").replace("*", ".*")
        return bool(re.match(f"^{regex}$", event_type))

    async def _ai_should_handle(self, ctx: EventContext) -> Optional[bool]:
        """
        AI-based decision on whether to handle event.

        This would call AI Orchestrator for intelligent pattern matching.
        For now, returns None to defer to capability matching.
        """
        # TODO: Integrate with AI Orchestrator
        # - Analyze event patterns
        # - Learn from past decisions
        # - Predict handling success
        return None
