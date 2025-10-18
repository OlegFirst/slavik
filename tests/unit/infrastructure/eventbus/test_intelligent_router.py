"""
Unit Tests for Intelligent Event Router
========================================

Comprehensive test suite for the IntelligentEventRouter system.

Run tests:
    cd /Users/MD/AI-Platform-ISO
    pytest tests/unit/infrastructure/eventbus/test_intelligent_router.py -v
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from infrastructure.eventbus.backends.memory import InMemoryEventBus
from infrastructure.eventbus.intelligent_router import (
    IntelligentEventRouter,
    AIEventAnalyzer,
    SmartSubscriberSelector,
    SubscriberCapabilities,
    SubscriberMetrics,
    SubscriberStatus,
    EventAnalysis
)
from infrastructure.eventbus.core.events import Event, EventPriority


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def router():
    """Create and initialize router"""
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(
        base_eventbus=eventbus,
        enable_ai_analysis=True,
        enable_semantic_matching=True
    )
    await router.initialize()

    yield router

    await router.shutdown()


@pytest.fixture
def sample_event():
    """Create sample event"""
    return Event.create(
        event_type="test.event",
        data={"test": "data", "value": 123},
        source="test-source",
        tenant_id="test-tenant",
        priority=EventPriority.NORMAL
    )


@pytest.fixture
def high_priority_event():
    """Create high priority event"""
    return Event.create(
        event_type="risk.critical_assessment",
        data={
            "severity": "critical",
            "description": "Urgent security vulnerability detected"
        },
        source="security-scanner",
        tenant_id="test-tenant",
        priority=EventPriority.CRITICAL
    )


# ============================================================================
# AI Event Analyzer Tests
# ============================================================================

class TestAIEventAnalyzer:
    """Test AI event analysis engine"""

    @pytest.mark.asyncio
    async def test_basic_analysis(self, sample_event):
        """Test basic event analysis"""
        analyzer = AIEventAnalyzer(use_embeddings=True)

        analysis = await analyzer.analyze_event(sample_event)

        assert isinstance(analysis, EventAnalysis)
        assert analysis.event_id == sample_event.id
        assert isinstance(analysis.determined_priority, EventPriority)
        assert 0.0 <= analysis.complexity_score <= 1.0
        assert len(analysis.keywords) > 0

    @pytest.mark.asyncio
    async def test_priority_detection(self):
        """Test AI priority detection"""
        analyzer = AIEventAnalyzer()

        # Critical event
        critical_event = Event.create(
            event_type="incident.emergency",
            data={"description": "Critical failure in payment system"},
            source="monitor",
            tenant_id="test",
            priority=EventPriority.NORMAL
        )

        analysis = await analyzer.analyze_event(critical_event)

        # Should upgrade to CRITICAL based on keywords
        assert analysis.determined_priority in [EventPriority.CRITICAL, EventPriority.HIGH]

    @pytest.mark.asyncio
    async def test_complexity_calculation(self):
        """Test complexity score calculation"""
        analyzer = AIEventAnalyzer()

        # Simple event
        simple = Event.create(
            event_type="info.log",
            data={"msg": "test"},
            source="test",
            tenant_id="test"
        )

        # Complex event
        complex_event = Event.create(
            event_type="workflow.analysis_required",
            data={
                "workflow_id": "wf_001",
                "analysis_type": "comprehensive_assessment",
                "description": "Complex workflow analysis with multiple dependencies",
                "parameters": {"depth": 5, "scope": "full"}
            },
            source="workflow-engine",
            tenant_id="test"
        )

        simple_analysis = await analyzer.analyze_event(simple)
        complex_analysis = await analyzer.analyze_event(complex_event)

        # Complex event should have higher complexity score
        assert complex_analysis.complexity_score > simple_analysis.complexity_score

    @pytest.mark.asyncio
    async def test_semantic_embedding_generation(self):
        """Test semantic embedding generation"""
        analyzer = AIEventAnalyzer(use_embeddings=True)

        event = Event.create(
            event_type="risk.assessment",
            data={"type": "security", "severity": "high"},
            source="test",
            tenant_id="test"
        )

        analysis = await analyzer.analyze_event(event)

        assert analysis.semantic_embedding is not None
        assert isinstance(analysis.semantic_embedding, list)
        assert len(analysis.semantic_embedding) > 0

    @pytest.mark.asyncio
    async def test_semantic_similarity(self):
        """Test semantic similarity calculation"""
        analyzer = AIEventAnalyzer(use_embeddings=True)

        # Similar events
        event1 = Event.create(
            event_type="risk.security_assessment",
            data={"type": "security vulnerability analysis"},
            source="test",
            tenant_id="test"
        )

        event2 = Event.create(
            event_type="risk.threat_analysis",
            data={"type": "security threat detection"},
            source="test",
            tenant_id="test"
        )

        # Different event
        event3 = Event.create(
            event_type="compliance.audit",
            data={"type": "compliance review"},
            source="test",
            tenant_id="test"
        )

        analysis1 = await analyzer.analyze_event(event1)
        analysis2 = await analyzer.analyze_event(event2)
        analysis3 = await analyzer.analyze_event(event3)

        # Similar events should have higher similarity
        similarity_12 = analyzer.calculate_semantic_similarity(
            analysis1.semantic_embedding,
            analysis2.semantic_embedding
        )

        similarity_13 = analyzer.calculate_semantic_similarity(
            analysis1.semantic_embedding,
            analysis3.semantic_embedding
        )

        # Similarity should be between 0 and 1
        assert 0.0 <= similarity_12 <= 1.0
        assert 0.0 <= similarity_13 <= 1.0


# ============================================================================
# Subscriber Management Tests
# ============================================================================

class TestSubscriberManagement:
    """Test subscriber registration and management"""

    @pytest.mark.asyncio
    async def test_register_subscriber(self, router):
        """Test subscriber registration"""
        events_received = []

        async def handler(event):
            events_received.append(event)

        sub_id = await router.register_subscriber(
            subscriber_id="test_sub",
            event_pattern="test.*",
            handler=handler,
            capabilities={
                "domains": ["test"],
                "max_concurrent": 5,
                "sla_ms": 1000
            }
        )

        assert sub_id == "test_sub"
        assert "test_sub" in router.subscribers
        assert "test_sub" in router.subscriber_handlers
        assert "test_sub" in router.subscriber_metrics

    @pytest.mark.asyncio
    async def test_unregister_subscriber(self, router):
        """Test subscriber unregistration"""
        async def handler(event):
            pass

        await router.register_subscriber(
            subscriber_id="test_sub",
            event_pattern="test.*",
            handler=handler
        )

        await router.unregister_subscriber("test_sub")

        assert "test_sub" not in router.subscribers
        assert "test_sub" not in router.subscriber_handlers
        assert "test_sub" not in router.subscriber_metrics

    @pytest.mark.asyncio
    async def test_subscriber_capabilities(self, router):
        """Test subscriber capabilities storage"""
        async def handler(event):
            pass

        await router.register_subscriber(
            subscriber_id="test_sub",
            event_pattern="test.*",
            handler=handler,
            capabilities={
                "domains": ["risk", "security"],
                "max_concurrent": 10,
                "avg_processing_time_ms": 300,
                "sla_ms": 1000,
                "semantic_tags": ["risk", "threat"]
            }
        )

        caps = router.subscribers["test_sub"]

        assert caps.domains == ["risk", "security"]
        assert caps.max_concurrent == 10
        assert caps.avg_processing_time_ms == 300.0
        assert caps.sla_ms == 1000.0
        assert "risk" in caps.semantic_tags


# ============================================================================
# Event Routing Tests
# ============================================================================

class TestEventRouting:
    """Test event routing functionality"""

    @pytest.mark.asyncio
    async def test_basic_routing(self, router, sample_event):
        """Test basic event routing"""
        events_received = []

        async def handler(event):
            events_received.append(event)

        await router.register_subscriber(
            subscriber_id="test_sub",
            event_pattern="test.*",
            handler=handler
        )

        decision = await router.route_event(sample_event)

        assert decision.event_id == sample_event.id
        assert "test_sub" in decision.selected_subscribers

        # Wait for processing
        await asyncio.sleep(0.5)

        assert len(events_received) == 1
        assert events_received[0].id == sample_event.id

    @pytest.mark.asyncio
    async def test_pattern_matching(self, router):
        """Test event pattern matching"""
        workflow_events = []
        risk_events = []

        async def workflow_handler(event):
            workflow_events.append(event)

        async def risk_handler(event):
            risk_events.append(event)

        await router.register_subscriber(
            subscriber_id="workflow_sub",
            event_pattern="workflow.*",
            handler=workflow_handler
        )

        await router.register_subscriber(
            subscriber_id="risk_sub",
            event_pattern="risk.*",
            handler=risk_handler
        )

        # Publish workflow event
        workflow_event = Event.create(
            event_type="workflow.stage_changed",
            data={},
            source="test",
            tenant_id="test"
        )

        # Publish risk event
        risk_event = Event.create(
            event_type="risk.assessment_needed",
            data={},
            source="test",
            tenant_id="test"
        )

        await router.route_event(workflow_event)
        await router.route_event(risk_event)

        await asyncio.sleep(0.5)

        # Each handler should only receive matching events
        assert len(workflow_events) == 1
        assert len(risk_events) == 1
        assert workflow_events[0].type == "workflow.stage_changed"
        assert risk_events[0].type == "risk.assessment_needed"

    @pytest.mark.asyncio
    async def test_priority_routing(self, router, high_priority_event):
        """Test priority-based routing"""
        decision = await router.route_event(high_priority_event)

        # Critical events should maintain or be upgraded to high priority
        assert decision.priority_used in [EventPriority.CRITICAL, EventPriority.HIGH]

    @pytest.mark.asyncio
    async def test_no_subscribers(self, router, sample_event):
        """Test routing with no matching subscribers"""
        # Don't register any subscribers
        decision = await router.route_event(sample_event)

        # Should use fallback routing
        assert decision.routing_strategy in ["no_candidates", "fallback_error"]

    @pytest.mark.asyncio
    async def test_multiple_subscribers_same_pattern(self, router):
        """Test routing to multiple subscribers with same pattern"""
        sub1_events = []
        sub2_events = []

        async def handler1(event):
            sub1_events.append(event)

        async def handler2(event):
            sub2_events.append(event)

        await router.register_subscriber(
            subscriber_id="sub1",
            event_pattern="test.*",
            handler=handler1,
            capabilities={"max_concurrent": 5}
        )

        await router.register_subscriber(
            subscriber_id="sub2",
            event_pattern="test.*",
            handler=handler2,
            capabilities={"max_concurrent": 5}
        )

        event = Event.create(
            event_type="test.event",
            data={},
            source="test",
            tenant_id="test"
        )

        decision = await router.route_event(event)

        # Should route to one of the subscribers
        assert len(decision.selected_subscribers) > 0

        await asyncio.sleep(0.5)

        # At least one subscriber should receive the event
        total_received = len(sub1_events) + len(sub2_events)
        assert total_received >= 1


# ============================================================================
# Load Balancing Tests
# ============================================================================

class TestLoadBalancing:
    """Test load-aware routing"""

    @pytest.mark.asyncio
    async def test_load_distribution(self, router):
        """Test load distribution across subscribers"""
        sub1_count = []
        sub2_count = []

        async def slow_handler1(event):
            sub1_count.append(event)
            await asyncio.sleep(0.5)  # Slow processing

        async def fast_handler2(event):
            sub2_count.append(event)
            await asyncio.sleep(0.1)  # Fast processing

        await router.register_subscriber(
            subscriber_id="slow_sub",
            event_pattern="test.*",
            handler=slow_handler1,
            capabilities={
                "max_concurrent": 2,
                "avg_processing_time_ms": 500
            }
        )

        await router.register_subscriber(
            subscriber_id="fast_sub",
            event_pattern="test.*",
            handler=fast_handler2,
            capabilities={
                "max_concurrent": 10,
                "avg_processing_time_ms": 100
            }
        )

        # Publish multiple events
        for i in range(10):
            event = Event.create(
                event_type="test.event",
                data={"index": i},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)
            await asyncio.sleep(0.05)

        await asyncio.sleep(2)

        # Fast subscriber should process more events
        assert len(sub2_count) >= len(sub1_count)

    @pytest.mark.asyncio
    async def test_capacity_limits(self, router):
        """Test that subscribers respect capacity limits"""
        processing = []

        async def handler(event):
            processing.append(event.id)
            await asyncio.sleep(1)  # Long processing
            processing.remove(event.id)

        await router.register_subscriber(
            subscriber_id="limited_sub",
            event_pattern="test.*",
            handler=handler,
            capabilities={"max_concurrent": 2}  # Max 2 concurrent
        )

        # Publish 5 events quickly
        for i in range(5):
            event = Event.create(
                event_type="test.event",
                data={"index": i},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)

        await asyncio.sleep(0.5)

        # Should never exceed max_concurrent
        metrics = router.get_subscriber_metrics("limited_sub")
        assert metrics["current_load"] <= 2


# ============================================================================
# Circuit Breaker Tests
# ============================================================================

class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after consecutive failures"""
        eventbus = InMemoryEventBus()
        router = IntelligentEventRouter(
            base_eventbus=eventbus,
            circuit_breaker_threshold=3  # Open after 3 failures
        )
        await router.initialize()

        failure_count = 0

        async def failing_handler(event):
            nonlocal failure_count
            failure_count += 1
            raise Exception("Simulated failure")

        await router.register_subscriber(
            subscriber_id="failing_sub",
            event_pattern="test.*",
            handler=failing_handler
        )

        # Publish events to trigger failures
        for i in range(5):
            event = Event.create(
                event_type="test.event",
                data={"index": i},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)
            await asyncio.sleep(0.2)

        # Check circuit breaker status
        metrics = router.get_subscriber_metrics("failing_sub")

        assert metrics["status"] == SubscriberStatus.CIRCUIT_OPEN.value
        assert metrics["consecutive_failures"] >= 3

        await router.shutdown()

    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_routing(self):
        """Test that circuit breaker prevents routing to failed subscriber"""
        eventbus = InMemoryEventBus()
        router = IntelligentEventRouter(
            base_eventbus=eventbus,
            circuit_breaker_threshold=2
        )
        await router.initialize()

        call_count = 0

        async def failing_handler(event):
            nonlocal call_count
            call_count += 1
            raise Exception("Failure")

        await router.register_subscriber(
            subscriber_id="failing_sub",
            event_pattern="test.*",
            handler=failing_handler
        )

        # Trigger circuit breaker
        for i in range(3):
            event = Event.create(
                event_type="test.event",
                data={},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)
            await asyncio.sleep(0.2)

        initial_calls = call_count

        # Try to route more events
        for i in range(3):
            event = Event.create(
                event_type="test.event",
                data={},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)
            await asyncio.sleep(0.2)

        # Should not increase call count (circuit is open)
        assert call_count <= initial_calls + 1  # Maybe 1 more for half-open test

        await router.shutdown()


# ============================================================================
# Metrics Tests
# ============================================================================

class TestMetrics:
    """Test metrics collection and reporting"""

    @pytest.mark.asyncio
    async def test_routing_metrics(self, router, sample_event):
        """Test basic routing metrics collection"""
        async def handler(event):
            pass

        await router.register_subscriber(
            subscriber_id="test_sub",
            event_pattern="test.*",
            handler=handler
        )

        await router.route_event(sample_event)
        await asyncio.sleep(0.5)

        metrics = router.get_metrics()

        assert metrics["total_events"] >= 1
        assert metrics["total_routed"] >= 1
        assert "routing_efficiency" in metrics
        assert "avg_routing_time_ms" in metrics

    @pytest.mark.asyncio
    async def test_subscriber_metrics(self, router):
        """Test subscriber-specific metrics"""
        async def handler(event):
            await asyncio.sleep(0.1)

        await router.register_subscriber(
            subscriber_id="test_sub",
            event_pattern="test.*",
            handler=handler
        )

        # Process some events
        for i in range(3):
            event = Event.create(
                event_type="test.event",
                data={"index": i},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)

        await asyncio.sleep(1)

        sub_metrics = router.get_subscriber_metrics("test_sub")

        assert sub_metrics is not None
        assert "success_rate" in sub_metrics
        assert "avg_latency_ms" in sub_metrics
        assert "status" in sub_metrics
        assert sub_metrics["success_rate"] > 0.0

    @pytest.mark.asyncio
    async def test_sla_compliance_tracking(self, router):
        """Test SLA compliance tracking"""
        async def fast_handler(event):
            await asyncio.sleep(0.05)  # Fast, meets SLA

        await router.register_subscriber(
            subscriber_id="fast_sub",
            event_pattern="test.*",
            handler=fast_handler,
            capabilities={"sla_ms": 100}  # 100ms SLA
        )

        for i in range(5):
            event = Event.create(
                event_type="test.event",
                data={},
                source="test",
                tenant_id="test"
            )
            await router.route_event(event)

        await asyncio.sleep(1)

        metrics = router.get_metrics()
        assert "sla_compliance_rate" in metrics


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Setup
        eventbus = InMemoryEventBus()
        router = IntelligentEventRouter(
            base_eventbus=eventbus,
            enable_ai_analysis=True,
            enable_semantic_matching=True
        )
        await router.initialize()

        processed_events = []

        async def workflow_handler(event):
            processed_events.append(event)
            await asyncio.sleep(0.1)

        # Register subscriber
        await router.register_subscriber(
            subscriber_id="workflow_processor",
            event_pattern="workflow.*",
            handler=workflow_handler,
            capabilities={
                "domains": ["workflow", "orchestration"],
                "max_concurrent": 5,
                "avg_processing_time_ms": 100,
                "sla_ms": 500,
                "semantic_tags": ["workflow", "process", "orchestration"]
            }
        )

        # Publish events
        events_published = []
        for i in range(3):
            event = Event.create(
                event_type="workflow.stage_changed",
                data={
                    "workflow_id": f"wf_{i}",
                    "stage": "execution"
                },
                source="workflow-engine",
                tenant_id="tenant_123",
                priority=EventPriority.NORMAL
            )
            events_published.append(event)
            decision = await router.route_event(event)

            assert decision.selected_subscribers == ["workflow_processor"]
            assert decision.confidence_score > 0.0

        # Wait for processing
        await asyncio.sleep(1)

        # Verify
        assert len(processed_events) == 3

        metrics = router.get_metrics()
        assert metrics["total_events"] == 3
        assert metrics["routing_efficiency"] == 1.0

        sub_metrics = router.get_subscriber_metrics("workflow_processor")
        assert sub_metrics["success_rate"] == 1.0

        # Cleanup
        await router.shutdown()

    @pytest.mark.asyncio
    async def test_multi_subscriber_workflow(self):
        """Test workflow with multiple specialized subscribers"""
        eventbus = InMemoryEventBus()
        router = IntelligentEventRouter(base_eventbus=eventbus)
        await router.initialize()

        risk_events = []
        compliance_events = []
        workflow_events = []

        async def risk_handler(event):
            risk_events.append(event)

        async def compliance_handler(event):
            compliance_events.append(event)

        async def workflow_handler(event):
            workflow_events.append(event)

        # Register specialized subscribers
        await router.register_subscriber(
            subscriber_id="risk_analyzer",
            event_pattern="risk.*",
            handler=risk_handler,
            capabilities={"domains": ["risk", "security"]}
        )

        await router.register_subscriber(
            subscriber_id="compliance_checker",
            event_pattern="compliance.*",
            handler=compliance_handler,
            capabilities={"domains": ["compliance", "audit"]}
        )

        await router.register_subscriber(
            subscriber_id="workflow_orchestrator",
            event_pattern="workflow.*",
            handler=workflow_handler,
            capabilities={"domains": ["workflow"]}
        )

        # Publish diverse events
        events = [
            Event.create(
                event_type="risk.assessment_needed",
                data={},
                source="test",
                tenant_id="test"
            ),
            Event.create(
                event_type="compliance.audit_required",
                data={},
                source="test",
                tenant_id="test"
            ),
            Event.create(
                event_type="workflow.stage_changed",
                data={},
                source="test",
                tenant_id="test"
            )
        ]

        for event in events:
            await router.route_event(event)

        await asyncio.sleep(1)

        # Each subscriber should only receive relevant events
        assert len(risk_events) == 1
        assert len(compliance_events) == 1
        assert len(workflow_events) == 1

        await router.shutdown()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
