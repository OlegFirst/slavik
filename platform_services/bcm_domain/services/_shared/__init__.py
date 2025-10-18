"""
Self-Aware Services - Shared Components

This package provides the foundation for self-aware, adaptive services
that can gracefully handle event choreography in distributed systems.

Core Components:
- SelfAwareService: Base class for intelligent services
- HealthMonitor: Self-monitoring and health tracking
- CapabilityRegistry: Capability tracking and matching
- LoadManager: Load awareness and management
- CollaborationMixin: Service collaboration and consensus

Usage:
    from _shared import SelfAwareService, EventPriority

    class BIAService(SelfAwareService):
        def __init__(self):
            super().__init__(
                service_name="bia",
                capabilities=["bia.assessment", "bia.analysis"]
            )

        async def handle_assessment(self, ctx):
            # Your logic here
            pass
"""

from .self_aware_base import (
    SelfAwareService,
    EventPriority,
    HandlingDecision,
    EventContext,
    HandlingResult
)

from .health_monitor import (
    HealthMonitor,
    HealthStatus,
    HealthCheck,
    HealthMetrics,
    check_database_health,
    check_redis_health,
    check_eventbus_health
)

from .capability_registry import (
    CapabilityRegistry,
    Capability,
    CapabilityMatch,
    ExpertiseLevel,
    BCM_CAPABILITIES
)

from .load_manager import (
    LoadManager,
    LoadLevel,
    LoadPolicy,
    LoadMetrics
)

from .collaboration_mixin import (
    CollaborationMixin,
    CollaborationDecision,
    ConsensusStrategy,
    VoteType,
    Vote,
    ConsensusRequest
)

from .metrics import (
    MetricsCollector,
    get_metrics_collector
)

__all__ = [
    # Main class
    "SelfAwareService",

    # Event handling
    "EventPriority",
    "HandlingDecision",
    "EventContext",
    "HandlingResult",

    # Health monitoring
    "HealthMonitor",
    "HealthStatus",
    "HealthCheck",
    "HealthMetrics",
    "check_database_health",
    "check_redis_health",
    "check_eventbus_health",

    # Capability registry
    "CapabilityRegistry",
    "Capability",
    "CapabilityMatch",
    "ExpertiseLevel",
    "BCM_CAPABILITIES",

    # Load management
    "LoadManager",
    "LoadLevel",
    "LoadPolicy",
    "LoadMetrics",

    # Collaboration
    "CollaborationMixin",
    "CollaborationDecision",
    "ConsensusStrategy",
    "VoteType",
    "Vote",
    "ConsensusRequest",

    # Metrics
    "MetricsCollector",
    "get_metrics_collector",
]

__version__ = "1.0.0"
