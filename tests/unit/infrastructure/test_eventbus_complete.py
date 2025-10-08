"""
Complete real tests for EventBus infrastructure
Tests Memory and Redis backends with real event scenarios
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
class TestEventBusMemoryBackend:
    """Test EventBus with Memory backend (fast, no external deps)"""

    async def test_eventbus_publishes_workflow_events(self):
        """Test EventBus publishes workflow state transition events"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")
        events_received = []

        async def event_handler(event: Event):
            events_received.append(event)

        await bus.subscribe("workflow.state_transition", event_handler)

        # Create realistic workflow event
        workflow_event = Event(
            topic="workflow.state_transition",
            payload={
                "workflow_id": "bia-workflow-2024-001",
                "tenant_id": "tenant-healthcare-001",
                "from_state": "initialized",
                "to_state": "analyzing",
                "timestamp": datetime.now().isoformat(),
                "module": "bia",
                "metadata": {
                    "organization_id": "org-healthcare-001",
                    "user_id": "user-bcm-officer-001"
                }
            }
        )

        # ACT
        await bus.publish(workflow_event)
        await asyncio.sleep(0.1)  # Allow event processing

        # ASSERT
        assert len(events_received) == 1
        received_event = events_received[0]
        assert received_event.topic == "workflow.state_transition"
        assert received_event.payload["workflow_id"] == "bia-workflow-2024-001"
        assert received_event.payload["from_state"] == "initialized"
        assert received_event.payload["to_state"] == "analyzing"


    async def test_eventbus_wildcard_subscription(self):
        """Test wildcard subscriptions work correctly"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")
        all_workflow_events = []

        async def wildcard_handler(event: Event):
            all_workflow_events.append(event)

        await bus.subscribe("workflow.*", wildcard_handler)

        # Publish different workflow events
        events_to_publish = [
            Event(topic="workflow.started", payload={"workflow_id": "wf-001"}),
            Event(topic="workflow.completed", payload={"workflow_id": "wf-001"}),
            Event(topic="workflow.failed", payload={"workflow_id": "wf-002"}),
            Event(topic="bia.analysis_complete", payload={"bia_id": "bia-001"}),  # Should not match
        ]

        # ACT
        for event in events_to_publish:
            await bus.publish(event)

        await asyncio.sleep(0.1)

        # ASSERT
        assert len(all_workflow_events) == 3  # Only workflow.* events
        assert all(e.topic.startswith("workflow.") for e in all_workflow_events)
        assert not any(e.topic.startswith("bia.") for e in all_workflow_events)


    async def test_eventbus_multiple_subscribers_same_topic(self):
        """Test multiple subscribers receive same event"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")

        subscriber1_events = []
        subscriber2_events = []
        subscriber3_events = []

        async def handler1(event): subscriber1_events.append(event)
        async def handler2(event): subscriber2_events.append(event)
        async def handler3(event): subscriber3_events.append(event)

        await bus.subscribe("bia.process_identified", handler1)
        await bus.subscribe("bia.process_identified", handler2)
        await bus.subscribe("bia.process_identified", handler3)

        event = Event(
            topic="bia.process_identified",
            payload={
                "bia_id": "bia-2024-001",
                "processes_count": 25,
                "critical_count": 8
            }
        )

        # ACT
        await bus.publish(event)
        await asyncio.sleep(0.1)

        # ASSERT
        assert len(subscriber1_events) == 1
        assert len(subscriber2_events) == 1
        assert len(subscriber3_events) == 1

        # All subscribers received same event
        assert subscriber1_events[0].payload == event.payload
        assert subscriber2_events[0].payload == event.payload
        assert subscriber3_events[0].payload == event.payload


    async def test_eventbus_event_ordering_preserved(self):
        """Test events are delivered in order"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")
        received_sequence = []

        async def sequence_handler(event: Event):
            received_sequence.append(event.payload["sequence"])

        await bus.subscribe("test.sequence", sequence_handler)

        # ACT - Publish 10 events in order
        for i in range(10):
            event = Event(topic="test.sequence", payload={"sequence": i})
            await bus.publish(event)

        await asyncio.sleep(0.2)

        # ASSERT
        assert received_sequence == list(range(10))  # [0,1,2,3,4,5,6,7,8,9]


@pytest.mark.asyncio
class TestEventBusRealScenarios:
    """Test EventBus with real application scenarios"""

    async def test_bia_workflow_event_flow(self):
        """Test complete BIA workflow event flow"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")
        workflow_history = []

        async def workflow_tracker(event: Event):
            workflow_history.append({
                "timestamp": datetime.now(),
                "event": event.topic,
                "payload": event.payload
            })

        await bus.subscribe("workflow.*", workflow_tracker)
        await bus.subscribe("bia.*", workflow_tracker)

        # ACT - Simulate complete BIA workflow
        workflow_id = "bia-workflow-2024-q1"

        # 1. Workflow started
        await bus.publish(Event(
            topic="workflow.started",
            payload={"workflow_id": workflow_id, "type": "bia"}
        ))

        # 2. BIA process identification
        await bus.publish(Event(
            topic="bia.process_identification.started",
            payload={"workflow_id": workflow_id}
        ))

        await bus.publish(Event(
            topic="bia.process_identification.completed",
            payload={"workflow_id": workflow_id, "processes_found": 25}
        ))

        # 3. Dependency analysis
        await bus.publish(Event(
            topic="bia.dependency_analysis.started",
            payload={"workflow_id": workflow_id}
        ))

        await bus.publish(Event(
            topic="bia.dependency_analysis.completed",
            payload={"workflow_id": workflow_id, "dependencies_mapped": 150}
        ))

        # 4. Impact assessment
        await bus.publish(Event(
            topic="bia.impact_assessment.completed",
            payload={
                "workflow_id": workflow_id,
                "total_risk_exposure": "$25M"
            }
        ))

        # 5. Workflow completed
        await bus.publish(Event(
            topic="workflow.completed",
            payload={
                "workflow_id": workflow_id,
                "duration_seconds": 1200,
                "status": "success"
            }
        ))

        await asyncio.sleep(0.2)

        # ASSERT
        assert len(workflow_history) == 7

        # Verify workflow phases
        topics = [h["event"] for h in workflow_history]
        assert "workflow.started" in topics
        assert "bia.process_identification.completed" in topics
        assert "bia.dependency_analysis.completed" in topics
        assert "bia.impact_assessment.completed" in topics
        assert "workflow.completed" in topics

        # Verify final status
        final_event = workflow_history[-1]
        assert final_event["payload"]["status"] == "success"


    async def test_risk_assessment_event_flow(self):
        """Test risk assessment workflow events"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")
        risk_events = []

        async def risk_tracker(event: Event):
            risk_events.append(event)

        await bus.subscribe("risk.*", risk_tracker)

        # ACT - Risk assessment workflow
        workflow_id = "risk-2024-q1"

        await bus.publish(Event(
            topic="risk.threat_identification.completed",
            payload={
                "workflow_id": workflow_id,
                "threats_identified": 15,
                "high_risk_count": 5
            }
        ))

        await bus.publish(Event(
            topic="risk.fair_analysis.completed",
            payload={
                "workflow_id": workflow_id,
                "ale_calculated": "$3M",
                "scenarios_analyzed": 5
            }
        ))

        await bus.publish(Event(
            topic="risk.mitigation_recommendations.generated",
            payload={
                "workflow_id": workflow_id,
                "recommendations_count": 12
            }
        ))

        await asyncio.sleep(0.1)

        # ASSERT
        assert len(risk_events) == 3
        assert risk_events[0].payload["threats_identified"] == 15
        assert risk_events[1].payload["ale_calculated"] == "$3M"
        assert risk_events[2].payload["recommendations_count"] == 12


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.requires_redis
class TestEventBusRedisBackend:
    """Test EventBus with Redis backend (requires Redis running)"""

    async def test_redis_eventbus_persistence(self):
        """Test Redis backend persists events"""
        # ARRANGE
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="redis", redis_url=redis_url)
        events_received = []

        async def handler(event: Event):
            events_received.append(event)

        await bus.subscribe("test.redis", handler)

        # ACT
        event = Event(topic="test.redis", payload={"test": "redis persistence"})
        await bus.publish(event)
        await asyncio.sleep(0.2)

        # ASSERT
        assert len(events_received) == 1
        assert events_received[0].payload["test"] == "redis persistence"

        # Cleanup
        await bus.close()


@pytest.mark.asyncio
class TestEventBusErrorHandling:
    """Test EventBus error handling"""

    async def test_eventbus_handles_subscriber_exception(self):
        """Test EventBus continues working when subscriber raises exception"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")

        good_events = []

        async def failing_handler(event: Event):
            raise Exception("Subscriber error!")

        async def good_handler(event: Event):
            good_events.append(event)

        await bus.subscribe("test.error", failing_handler)
        await bus.subscribe("test.error", good_handler)

        # ACT
        event = Event(topic="test.error", payload={"test": "error handling"})
        await bus.publish(event)
        await asyncio.sleep(0.1)

        # ASSERT
        # Good handler should still receive event despite other handler failing
        assert len(good_events) == 1


    async def test_eventbus_validates_event_structure(self):
        """Test EventBus validates event structure"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus

        bus = create_event_bus(backend="memory")

        # ACT & ASSERT - Invalid event (no topic)
        with pytest.raises((ValueError, TypeError, AttributeError)):
            await bus.publish({"invalid": "event"})  # Not an Event object


@pytest.mark.asyncio
class TestEventBusPerformance:
    """Test EventBus performance characteristics"""

    async def test_eventbus_handles_high_volume(self):
        """Test EventBus handles high volume of events"""
        # ARRANGE
        from infrastructure.runtime.eventbus.factory import create_event_bus
        from infrastructure.runtime.eventbus.core.events import Event

        bus = create_event_bus(backend="memory")
        events_received = []

        async def counter_handler(event: Event):
            events_received.append(event)

        await bus.subscribe("test.volume", counter_handler)

        # ACT - Publish 1000 events
        start_time = datetime.now()

        for i in range(1000):
            event = Event(topic="test.volume", payload={"sequence": i})
            await bus.publish(event)

        await asyncio.sleep(0.5)  # Wait for processing

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # ASSERT
        assert len(events_received) == 1000
        assert duration < 2.0  # Should process 1000 events in < 2 seconds
        print(f"Processed 1000 events in {duration:.3f} seconds ({1000/duration:.0f} events/sec)")
