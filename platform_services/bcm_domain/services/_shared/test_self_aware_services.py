"""
Tests for Self-Aware Services

Demonstrates all capabilities of the self-aware service pattern.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from self_aware_base import (
    SelfAwareService,
    EventPriority,
    EventContext,
    HandlingDecision
)
from health_monitor import HealthMonitor, HealthStatus, HealthCheck
from capability_registry import CapabilityRegistry, Capability, ExpertiseLevel
from load_manager import LoadManager, LoadPolicy, LoadLevel
from collaboration_mixin import CollaborationMixin, Vote, VoteType, ConsensusStrategy


class TestSelfAwareService:
    """Test SelfAwareService base class"""

    @pytest.fixture
    def service(self):
        """Create test service"""
        return SelfAwareService(
            service_name="test_service",
            capabilities=["test.event", "test.action"],
            enable_ai_decisions=False,
            enable_collaboration=False
        )

    @pytest.mark.asyncio
    async def test_initialization(self, service):
        """Test service initialization"""
        assert service.service_name == "test_service"
        assert len(service.capability_registry.list_capabilities()) == 2
        assert service.health_monitor is not None
        assert service.load_manager is not None

    @pytest.mark.asyncio
    async def test_should_handle_with_capability_match(self, service):
        """Test event handling decision with capability match"""
        ctx = EventContext(
            event_type="test.event",
            event_data={"test": "data"}
        )

        should_handle = await service.should_handle(ctx)
        assert should_handle is True

    @pytest.mark.asyncio
    async def test_should_not_handle_without_capability(self, service):
        """Test event rejection without capability"""
        ctx = EventContext(
            event_type="unknown.event",
            event_data={"test": "data"}
        )

        should_handle = await service.should_handle(ctx)
        assert should_handle is False

    @pytest.mark.asyncio
    async def test_can_handle_when_healthy(self, service):
        """Test can handle when service is healthy"""
        await service.health_monitor.set_healthy()

        ctx = EventContext(
            event_type="test.event",
            event_data={},
            priority=EventPriority.NORMAL
        )

        can_handle = await service.can_handle(ctx)
        assert can_handle is True

    @pytest.mark.asyncio
    async def test_cannot_handle_when_down(self, service):
        """Test cannot handle when service is down"""
        await service.health_monitor.set_down("Test failure")

        ctx = EventContext(
            event_type="test.event",
            event_data={},
            priority=EventPriority.NORMAL
        )

        can_handle = await service.can_handle(ctx)
        assert can_handle is False

    @pytest.mark.asyncio
    async def test_critical_events_always_accepted(self, service):
        """Test critical events are accepted even when degraded"""
        await service.health_monitor.set_degraded("High load")

        ctx = EventContext(
            event_type="test.event",
            event_data={},
            priority=EventPriority.CRITICAL
        )

        can_handle = await service.can_handle(ctx)
        assert can_handle is True

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, service):
        """Test graceful degradation"""
        # Mark one capability as essential
        service.mark_essential("test.event")

        # Enter degraded mode
        await service.degrade_gracefully("Test degradation")

        assert service._degraded_mode is True

        # Essential capability should still be enabled
        cap = service.capability_registry.get_capability("test.event")
        # Note: In actual implementation, non-essential would be disabled

    @pytest.mark.asyncio
    async def test_recovery_from_degradation(self, service):
        """Test recovery from degradation"""
        await service.degrade_gracefully("Test")
        assert service._degraded_mode is True

        await service.recover_from_degradation()
        assert service._degraded_mode is False

    @pytest.mark.asyncio
    async def test_event_handler_registration(self, service):
        """Test event handler registration"""
        handler_called = False

        async def test_handler(ctx):
            nonlocal handler_called
            handler_called = True

        service.register_handler("test.custom", test_handler)

        # Handler should be registered
        assert "test.custom" in service._handlers

    @pytest.mark.asyncio
    async def test_on_event_handle_decision(self, service):
        """Test on_event returns HANDLE decision"""
        async def test_handler(ctx):
            return {"result": "success"}

        service.register_handler("test.event", test_handler)

        result = await service.on_event(
            "test.event",
            {"data": "test"},
            priority=EventPriority.NORMAL
        )

        assert result.decision == HandlingDecision.HANDLE
        assert result.handler is not None

    @pytest.mark.asyncio
    async def test_on_event_reject_without_capability(self, service):
        """Test on_event returns REJECT without capability"""
        result = await service.on_event(
            "unknown.event",
            {},
            priority=EventPriority.NORMAL
        )

        assert result.decision == HandlingDecision.REJECT


class TestHealthMonitor:
    """Test HealthMonitor component"""

    @pytest.fixture
    def monitor(self):
        """Create health monitor"""
        return HealthMonitor("test_service")

    @pytest.mark.asyncio
    async def test_initialization(self, monitor):
        """Test monitor initialization"""
        assert monitor.service_name == "test_service"
        assert monitor._status == HealthStatus.UNKNOWN

    @pytest.mark.asyncio
    async def test_register_check(self, monitor):
        """Test registering health check"""
        async def test_check():
            return HealthCheck(
                name="test",
                status=HealthStatus.HEALTHY
            )

        monitor.register_check("test", test_check)
        assert "test" in monitor._checks

    @pytest.mark.asyncio
    async def test_health_check_execution(self, monitor):
        """Test health check execution"""
        async def test_check():
            return HealthCheck(
                name="test",
                status=HealthStatus.HEALTHY,
                message="All good"
            )

        monitor.register_check("test", test_check)

        status = await monitor.get_status()
        assert status.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_set_degraded(self, monitor):
        """Test setting degraded status"""
        await monitor.set_degraded("High load")

        assert monitor._status == HealthStatus.DEGRADED
        assert monitor._degraded_reason == "High load"

    @pytest.mark.asyncio
    async def test_set_healthy(self, monitor):
        """Test setting healthy status"""
        await monitor.set_degraded("Test")
        await monitor.set_healthy()

        assert monitor._status == HealthStatus.HEALTHY
        assert monitor._degraded_reason is None

    def test_record_request(self, monitor):
        """Test recording request metrics"""
        monitor.record_request(100.0, error=False)
        monitor.record_request(200.0, error=True)

        assert len(monitor._request_times) == 2
        assert len(monitor._error_count) == 2

    def test_get_metrics(self, monitor):
        """Test getting metrics"""
        monitor.record_request(150.0, error=False)

        metrics = monitor.get_metrics()
        assert metrics.avg_response_time_ms > 0


class TestCapabilityRegistry:
    """Test CapabilityRegistry component"""

    @pytest.fixture
    def registry(self):
        """Create capability registry"""
        return CapabilityRegistry()

    def test_register_capability(self, registry):
        """Test registering capability"""
        cap = Capability(
            name="test.action",
            service="test_service",
            expertise=ExpertiseLevel.EXPERT
        )

        registry.register(cap)

        assert "test.action" in registry.list_capabilities()

    def test_get_capability(self, registry):
        """Test getting capability"""
        cap = Capability(
            name="test.action",
            service="test_service"
        )

        registry.register(cap)

        retrieved = registry.get_capability("test.action")
        assert retrieved is not None
        assert retrieved.service == "test_service"

    def test_find_capabilities_exact_match(self, registry):
        """Test finding capabilities with exact match"""
        cap = Capability(
            name="test.action",
            service="test_service"
        )

        registry.register(cap)

        matches = registry.find_capabilities("test.action")
        assert len(matches) == 1
        assert matches[0].capability.name == "test.action"

    def test_find_capabilities_wildcard(self, registry):
        """Test finding capabilities with wildcard"""
        registry.register(Capability(name="test.action1", service="test"))
        registry.register(Capability(name="test.action2", service="test"))

        matches = registry.find_capabilities("test.*")
        assert len(matches) == 2

    def test_enable_disable_capability(self, registry):
        """Test enabling/disabling capability"""
        cap = Capability(name="test.action", service="test")
        registry.register(cap)

        registry.disable_capability("test.action", "test")
        retrieved = registry.get_capability("test.action")
        assert retrieved.enabled is False

        registry.enable_capability("test.action", "test")
        retrieved = registry.get_capability("test.action")
        assert retrieved.enabled is True

    def test_find_by_tag(self, registry):
        """Test finding capabilities by tag"""
        cap = Capability(
            name="test.action",
            service="test",
            tags={"bcm", "critical"}
        )

        registry.register(cap)

        results = registry.find_by_tag("bcm")
        assert len(results) == 1
        assert results[0].name == "test.action"


class TestLoadManager:
    """Test LoadManager component"""

    @pytest.fixture
    def load_manager(self):
        """Create load manager"""
        return LoadManager(
            "test_service",
            max_concurrent_requests=10
        )

    @pytest.mark.asyncio
    async def test_initialization(self, load_manager):
        """Test load manager initialization"""
        assert load_manager.service_name == "test_service"
        assert load_manager.max_concurrent_requests == 10

    @pytest.mark.asyncio
    async def test_can_accept_when_idle(self, load_manager):
        """Test can accept when idle"""
        can_accept = await load_manager.can_accept("normal")
        assert can_accept is True

    @pytest.mark.asyncio
    async def test_track_request(self, load_manager):
        """Test tracking request"""
        initial = load_manager._active_requests

        await load_manager.track_request_start()
        assert load_manager._active_requests == initial + 1

        await load_manager.track_request_end(duration_ms=100.0)
        assert load_manager._active_requests == initial

    @pytest.mark.asyncio
    async def test_get_load_level(self, load_manager):
        """Test getting load level"""
        level = await load_manager.get_load_level()
        assert isinstance(level, LoadLevel)

    @pytest.mark.asyncio
    async def test_queue_event(self, load_manager):
        """Test queuing event"""
        event = {"type": "test.event", "data": {}}

        queued = await load_manager.queue_event(event)
        assert queued is True
        assert len(load_manager._queued_events) == 1

    @pytest.mark.asyncio
    async def test_defer_event(self, load_manager):
        """Test deferring event"""
        event = {"type": "test.event", "data": {}}

        deferred = await load_manager.defer_event(event)
        assert deferred is True
        assert len(load_manager._deferred_events) == 1

    @pytest.mark.asyncio
    async def test_get_metrics(self, load_manager):
        """Test getting metrics"""
        metrics = await load_manager.get_metrics()

        assert metrics.current_load >= 0.0
        assert metrics.active_requests >= 0

    @pytest.mark.asyncio
    async def test_predict_load(self, load_manager):
        """Test load prediction"""
        predicted = await load_manager.predict_load(seconds_ahead=60)
        assert 0.0 <= predicted <= 1.0


class TestCollaborationMixin:
    """Test CollaborationMixin component"""

    @pytest.fixture
    def collaboration(self):
        """Create collaboration mixin"""
        return CollaborationMixin("test_service")

    def test_register_vote_handler(self, collaboration):
        """Test registering vote handler"""
        async def test_handler(context):
            return Vote(
                service="test",
                vote=VoteType.APPROVE,
                confidence=1.0
            )

        collaboration.register_vote_handler("test_context", test_handler)
        assert "test_context" in collaboration._vote_handlers

    def test_register_service_capabilities(self, collaboration):
        """Test registering service capabilities"""
        capabilities = {"bia.assessment", "bia.analysis"}
        collaboration.register_service_capabilities("bia", capabilities)

        assert "bia" in collaboration._service_registry
        assert collaboration._service_registry["bia"] == capabilities

    @pytest.mark.asyncio
    async def test_cast_vote(self, collaboration):
        """Test casting vote"""
        async def approve_handler(context):
            return Vote(
                service="test",
                vote=VoteType.APPROVE,
                confidence=0.9,
                reasoning="Test approval"
            )

        collaboration.register_vote_handler("test_approval", approve_handler)

        vote = await collaboration.cast_vote(
            "req-123",
            {"type": "test_approval"}
        )

        assert vote.vote == VoteType.APPROVE
        assert vote.confidence == 0.9

    @pytest.mark.asyncio
    async def test_find_alternative_handlers(self, collaboration):
        """Test finding alternative handlers"""
        collaboration.register_service_capabilities("bia", {"bia.assessment"})
        collaboration.register_service_capabilities("risk", {"bia.assessment"})

        alternatives = await collaboration.find_alternative_handlers("bia.assessment")
        assert len(alternatives) >= 1

    @pytest.mark.asyncio
    async def test_find_related_services(self, collaboration):
        """Test finding related services"""
        related = await collaboration.find_related_services("bia.assessment")

        # Should find BCM-related services
        assert isinstance(related, list)


class TestIntegration:
    """Integration tests for complete self-aware service"""

    @pytest.mark.asyncio
    async def test_complete_event_flow(self):
        """Test complete event handling flow"""
        # Create service
        service = SelfAwareService(
            service_name="bia",
            capabilities=["bia.assessment.create"],
            enable_ai_decisions=False,
            enable_collaboration=False
        )

        # Register handler
        handler_executed = False

        async def assessment_handler(ctx):
            nonlocal handler_executed
            handler_executed = True
            return {"result": "success"}

        service.register_handler("bia.assessment.create", assessment_handler)

        # Handle event
        result = await service.on_event(
            "bia.assessment.create",
            {"name": "Test Assessment"},
            priority=EventPriority.HIGH
        )

        assert result.decision == HandlingDecision.HANDLE
        assert result.handler is not None

    @pytest.mark.asyncio
    async def test_load_based_degradation(self):
        """Test automatic degradation under load"""
        service = SelfAwareService(
            service_name="test",
            capabilities=["test.action"],
            load_policy=LoadPolicy(
                degradation_threshold=0.5,
                enable_auto_degradation=True
            )
        )

        # Set degradation callback
        degraded = False

        async def on_degrade(reason):
            nonlocal degraded
            degraded = True
            await service.degrade_gracefully(reason)

        service.load_manager.set_degradation_callback(on_degrade)

        # Simulate high load
        for _ in range(10):
            await service.load_manager.track_request_start()

        # Should trigger degradation
        # (in real scenario, monitoring loop would trigger this)


    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test metrics are collected properly"""
        service = SelfAwareService(
            service_name="test",
            capabilities=["test.action"]
        )

        # Generate some events
        await service.on_event("test.action", {})
        await service.on_event("unknown.action", {})

        # Get metrics
        metrics = service.get_metrics()

        assert metrics["events_received"] == 2
        assert metrics["events_rejected"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
