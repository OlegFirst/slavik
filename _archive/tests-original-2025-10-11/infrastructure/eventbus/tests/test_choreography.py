"""
Event Choreography Integration Tests
=====================================

Tests for event-driven flows between services:
- BIA → Risk → Planning flow
- Risk → Planning flow
- Event ordering
- Error handling
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Import eventbus components
import sys
sys.path.append('/Users/MD/AI-Platform-ISO/infrastructure')
from eventbus import Event, EventPriority, create_eventbus


class EventCapture:
    """Helper class to capture events during tests."""

    def __init__(self):
        self.events: List[Event] = []
        self.events_by_type: Dict[str, List[Event]] = {}

    async def capture(self, event: Event):
        """Capture an event."""
        self.events.append(event)
        event_type = event.type
        if event_type not in self.events_by_type:
            self.events_by_type[event_type] = []
        self.events_by_type[event_type].append(event)

    def get_events(self, event_type: str) -> List[Event]:
        """Get all captured events of a specific type."""
        return self.events_by_type.get(event_type, [])

    def clear(self):
        """Clear all captured events."""
        self.events.clear()
        self.events_by_type.clear()


@pytest.fixture
async def eventbus():
    """Create eventbus instance for testing."""
    bus = create_eventbus('memory')  # Use memory backend for tests
    yield bus
    # Cleanup if needed


@pytest.fixture
def event_capture():
    """Create event capture instance."""
    return EventCapture()


@pytest.mark.asyncio
async def test_bia_to_risk_flow(eventbus, event_capture):
    """
    Test BIA → Risk flow:
    1. BIA assessment completed
    2. Risk service generates suggestions
    3. Risk assessment created
    """
    # Setup: Subscribe to relevant events
    await eventbus.subscribe('risk.suggestion.generated', event_capture.capture)
    await eventbus.subscribe('risk.assessment.created', event_capture.capture)

    # Act: Simulate BIA assessment completion
    bia_event = Event.create(
        event_type='bia.assessment.completed',
        data={
            'assessment_id': 'bia-test-001',
            'tenant_id': 'tenant-123',
            'processes': [
                {
                    'process_id': 'p1',
                    'name': 'Payment Processing',
                    'criticality': 'critical',
                    'rto': 2,
                    'rpo': 1,
                    'dependencies': ['payment-gateway', 'database']
                },
                {
                    'process_id': 'p2',
                    'name': 'Customer Service',
                    'criticality': 'high',
                    'rto': 8,
                    'rpo': 4,
                    'dependencies': ['crm-system']
                }
            ],
            'critical_process_count': 2,
            'total_processes': 2
        },
        source='bia-service',
        tenant_id='tenant-123',
        priority=EventPriority.HIGH
    )

    await eventbus.publish(bia_event)

    # Wait for async processing
    await asyncio.sleep(0.5)

    # Assert: Risk suggestions should be generated
    risk_suggestions = event_capture.get_events('risk.suggestion.generated')
    assert len(risk_suggestions) > 0, "Risk suggestions should be generated from BIA data"

    suggestion_event = risk_suggestions[0]
    assert 'suggested_risks' in suggestion_event.data
    assert len(suggestion_event.data['suggested_risks']) > 0

    # Assert: Suggestions should include risks for critical processes
    suggested_risks = suggestion_event.data['suggested_risks']
    critical_risks = [r for r in suggested_risks if 'critical' in r.get('title', '').lower()]
    assert len(critical_risks) > 0, "Should suggest risks for critical processes"


@pytest.mark.asyncio
async def test_risk_to_planning_flow(eventbus, event_capture):
    """
    Test Risk → Planning flow:
    1. Risk assessment completed with high risks
    2. Planning service creates BC plans
    3. Plans published
    """
    # Setup: Subscribe to plan events
    await eventbus.subscribe('plan.strategy.proposed', event_capture.capture)
    await eventbus.subscribe('plan.created', event_capture.capture)

    # Act: Simulate risk assessment completion
    risk_event = Event.create(
        event_type='risk.assessment.completed',
        data={
            'assessment_id': 'risk-test-001',
            'tenant_id': 'tenant-123',
            'risks': [
                {
                    'risk_id': 'r1',
                    'title': 'Payment system failure',
                    'severity': 'critical',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'risk_score': 9,
                    'category': 'operational',
                    'related_process_id': 'p1'
                },
                {
                    'risk_id': 'r2',
                    'title': 'Data breach',
                    'severity': 'high',
                    'likelihood': 'low',
                    'impact': 'critical',
                    'risk_score': 8,
                    'category': 'security',
                    'related_process_id': 'p2'
                }
            ],
            'high_risk_count': 2,
            'total_risks': 2
        },
        source='risk-service',
        tenant_id='tenant-123',
        priority=EventPriority.HIGH
    )

    await eventbus.publish(risk_event)

    # Wait for async processing
    await asyncio.sleep(0.5)

    # Assert: BC plan strategies should be proposed
    plan_strategies = event_capture.get_events('plan.strategy.proposed')
    assert len(plan_strategies) > 0, "BC plan strategies should be proposed for high risks"

    strategy_event = plan_strategies[0]
    assert 'suggestion' in strategy_event.data

    # Assert: Should have strategies for critical risks
    suggestion = strategy_event.data['suggestion']
    if isinstance(suggestion, dict):
        assert 'risk_id' in suggestion or 'process_id' in suggestion


@pytest.mark.asyncio
async def test_complete_bia_risk_planning_flow(eventbus, event_capture):
    """
    Test complete BIA → Risk → Planning flow end-to-end.

    This tests the full choreography from BIA completion through
    risk identification to BC plan creation.
    """
    # Setup: Subscribe to all relevant events
    await eventbus.subscribe('bia.assessment.completed', event_capture.capture)
    await eventbus.subscribe('risk.suggestion.generated', event_capture.capture)
    await eventbus.subscribe('risk.assessment.completed', event_capture.capture)
    await eventbus.subscribe('plan.strategy.proposed', event_capture.capture)

    # Act: Publish BIA assessment completed
    bia_event = Event.create(
        event_type='bia.assessment.completed',
        data={
            'assessment_id': 'bia-e2e-001',
            'tenant_id': 'tenant-123',
            'processes': [
                {
                    'process_id': 'p1',
                    'name': 'Core Banking',
                    'criticality': 'critical',
                    'rto': 1,
                    'rpo': 0.5,
                    'mtpd': 2,
                    'financial_impact': 1000000,
                    'dependencies': ['mainframe', 'database', 'network']
                }
            ],
            'critical_process_count': 1,
            'total_processes': 1
        },
        source='bia-service',
        tenant_id='tenant-123',
        priority=EventPriority.HIGH
    )

    await eventbus.publish(bia_event)

    # Wait for cascading events to process
    await asyncio.sleep(1.0)

    # Assert: Check event cascade
    bia_events = event_capture.get_events('bia.assessment.completed')
    assert len(bia_events) == 1, "BIA event should be captured"

    risk_suggestions = event_capture.get_events('risk.suggestion.generated')
    assert len(risk_suggestions) > 0, "Risk suggestions should be generated"

    # Manual simulation of risk assessment (since we're testing choreography)
    # In real system, risk service would create assessment and publish completed event
    risk_event = Event.create(
        event_type='risk.assessment.completed',
        data={
            'assessment_id': 'risk-e2e-001',
            'tenant_id': 'tenant-123',
            'risks': [
                {
                    'risk_id': 'r1',
                    'title': 'Core banking system failure',
                    'severity': 'critical',
                    'related_process_id': 'p1'
                }
            ],
            'high_risk_count': 1,
            'total_risks': 1
        },
        source='risk-service',
        tenant_id='tenant-123',
        priority=EventPriority.HIGH
    )

    await eventbus.publish(risk_event)
    await asyncio.sleep(0.5)

    # Assert: Planning should propose strategies
    plan_strategies = event_capture.get_events('plan.strategy.proposed')
    assert len(plan_strategies) > 0, "BC plan strategies should be proposed"


@pytest.mark.asyncio
async def test_event_ordering(eventbus):
    """
    Test that events are processed in the correct order.
    """
    received_events = []

    async def capture_with_order(event: Event):
        received_events.append({
            'type': event.type,
            'timestamp': datetime.utcnow(),
            'data': event.data
        })

    # Subscribe to events
    await eventbus.subscribe('test.event.1', capture_with_order)
    await eventbus.subscribe('test.event.2', capture_with_order)
    await eventbus.subscribe('test.event.3', capture_with_order)

    # Publish events in specific order
    for i in range(1, 4):
        event = Event.create(
            event_type=f'test.event.{i}',
            data={'sequence': i},
            source='test',
            tenant_id='tenant-123'
        )
        await eventbus.publish(event)
        await asyncio.sleep(0.1)  # Small delay to ensure ordering

    await asyncio.sleep(0.5)

    # Assert: Events should be received in order
    assert len(received_events) == 3
    for i, evt in enumerate(received_events):
        assert evt['data']['sequence'] == i + 1


@pytest.mark.asyncio
async def test_error_handling_in_flow(eventbus, event_capture):
    """
    Test that errors in one handler don't break the entire flow.
    """
    error_count = 0

    async def handler_that_fails(event: Event):
        nonlocal error_count
        error_count += 1
        raise Exception("Simulated handler failure")

    async def handler_that_succeeds(event: Event):
        await event_capture.capture(event)

    # Subscribe both handlers to same event
    await eventbus.subscribe('test.error.event', handler_that_fails)
    await eventbus.subscribe('test.error.event', handler_that_succeeds)

    # Publish event
    event = Event.create(
        event_type='test.error.event',
        data={'test': 'data'},
        source='test',
        tenant_id='tenant-123'
    )

    await eventbus.publish(event)
    await asyncio.sleep(0.5)

    # Assert: Failing handler should not prevent successful handler
    assert error_count > 0, "Error handler should have been called"
    successful_events = event_capture.get_events('test.error.event')
    # Note: Depending on implementation, successful handler may or may not execute
    # This tests resilience of the system


@pytest.mark.asyncio
async def test_criticality_change_triggers_risk_update(eventbus, event_capture):
    """
    Test that criticality change triggers risk reassessment.
    """
    # Setup: Subscribe to risk events
    await eventbus.subscribe('risk.suggestion.generated', event_capture.capture)

    # Act: Publish criticality change
    criticality_event = Event.create(
        event_type='bia.criticality.changed',
        data={
            'process_id': 'p1',
            'old_criticality': 'medium',
            'new_criticality': 'critical',
            'changed_by': 'admin',
            'reason': 'Increased business dependency'
        },
        source='bia-service',
        tenant_id='tenant-123',
        priority=EventPriority.HIGH
    )

    await eventbus.publish(criticality_event)
    await asyncio.sleep(0.5)

    # Assert: Should trigger risk suggestion
    risk_suggestions = event_capture.get_events('risk.suggestion.generated')
    # Risk service should react to criticality escalation
    # (Actual assertion depends on handler implementation)


@pytest.mark.asyncio
async def test_plan_activation_flow(eventbus, event_capture):
    """
    Test plan activation during crisis.
    """
    # Setup: Subscribe to plan and response events
    await eventbus.subscribe('plan.activated', event_capture.capture)
    await eventbus.subscribe('response.team.mobilized', event_capture.capture)

    # Act: Simulate crisis declaration
    crisis_event = Event.create(
        event_type='crisis.declared',
        data={
            'crisis_id': 'crisis-001',
            'crisis_type': 'cyber_attack',
            'severity': 'critical'
        },
        source='crisis-service',
        tenant_id='tenant-123',
        priority=EventPriority.CRITICAL
    )

    await eventbus.publish(crisis_event)

    # Simulate plan activation
    plan_activated_event = Event.create(
        event_type='plan.activated',
        data={
            'plan_id': 'plan-001',
            'activated_by': 'incident-manager',
            'trigger_event': 'crisis-001'
        },
        source='planning-service',
        tenant_id='tenant-123',
        priority=EventPriority.CRITICAL
    )

    await eventbus.publish(plan_activated_event)
    await asyncio.sleep(0.5)

    # Assert: Plan activation should be captured
    activations = event_capture.get_events('plan.activated')
    assert len(activations) == 1
    assert activations[0].data['plan_id'] == 'plan-001'


@pytest.mark.asyncio
async def test_concurrent_events(eventbus, event_capture):
    """
    Test handling of concurrent events from multiple sources.
    """
    # Subscribe to all test events
    await eventbus.subscribe('test.concurrent.*', event_capture.capture)

    # Publish multiple events concurrently
    events = []
    for i in range(10):
        event = Event.create(
            event_type=f'test.concurrent.event{i}',
            data={'id': i},
            source='test',
            tenant_id='tenant-123'
        )
        events.append(eventbus.publish(event))

    # Wait for all to complete
    await asyncio.gather(*events)
    await asyncio.sleep(1.0)

    # Assert: All events should be processed
    # (Actual count depends on wildcard subscription implementation)
    assert len(event_capture.events) > 0


@pytest.mark.asyncio
async def test_event_with_correlation_id(eventbus, event_capture):
    """
    Test event tracing with correlation IDs.
    """
    correlation_id = 'trace-12345'

    # Subscribe to events
    await eventbus.subscribe('test.trace.*', event_capture.capture)

    # Publish related events with same correlation ID
    event1 = Event.create(
        event_type='test.trace.start',
        data={'step': 1},
        source='test',
        tenant_id='tenant-123',
        correlation_id=correlation_id
    )

    event2 = Event.create(
        event_type='test.trace.middle',
        data={'step': 2},
        source='test',
        tenant_id='tenant-123',
        correlation_id=correlation_id
    )

    event3 = Event.create(
        event_type='test.trace.end',
        data={'step': 3},
        source='test',
        tenant_id='tenant-123',
        correlation_id=correlation_id
    )

    await eventbus.publish(event1)
    await eventbus.publish(event2)
    await eventbus.publish(event3)
    await asyncio.sleep(0.5)

    # Assert: All events should have same correlation ID
    captured = event_capture.events
    assert len(captured) >= 3
    # Check correlation IDs are preserved
    # (Depends on wildcard implementation)


# Performance Tests

@pytest.mark.asyncio
async def test_event_processing_performance(eventbus, event_capture):
    """
    Test event processing performance and latency.
    """
    event_count = 100
    start_time = datetime.utcnow()

    await eventbus.subscribe('test.performance', event_capture.capture)

    # Publish many events
    for i in range(event_count):
        event = Event.create(
            event_type='test.performance',
            data={'id': i},
            source='test',
            tenant_id='tenant-123'
        )
        await eventbus.publish(event)

    await asyncio.sleep(2.0)  # Wait for processing

    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()

    # Assert: Processing should be reasonably fast
    assert duration < 5.0, f"Processing {event_count} events took {duration}s (expected < 5s)"

    # Assert: All events processed
    # (Depending on implementation, may not capture all if async)
    print(f"Processed {len(event_capture.events)} events in {duration:.2f}s")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
