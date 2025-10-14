"""
Tests for InMemoryEventBus
===========================

Unit tests for in-memory event bus backend.
"""

import pytest
import asyncio
from infrastructure.eventbus import create_eventbus, Event, EventPriority


@pytest.mark.asyncio
async def test_create_memory_bus():
    """Test creating in-memory event bus."""
    bus = create_eventbus('memory')
    assert bus is not None
    await bus.close()


@pytest.mark.asyncio
async def test_publish_and_subscribe():
    """Test basic publish/subscribe flow."""
    bus = create_eventbus('memory')

    # Track received events
    received_events = []

    async def handler(event: Event):
        received_events.append(event)

    # Subscribe
    sub_id = await bus.subscribe('test.event', handler)

    # Publish
    event = Event.create(
        event_type='test.event',
        data={'message': 'hello'},
        source='test',
        tenant_id='tenant_123'
    )
    await bus.publish(event)

    # Give handler time to process
    await asyncio.sleep(0.1)

    # Check event received
    assert len(received_events) == 1
    assert received_events[0].type == 'test.event'
    assert received_events[0].data['message'] == 'hello'

    # Cleanup
    await bus.unsubscribe(sub_id)
    await bus.close()


@pytest.mark.asyncio
async def test_wildcard_subscription():
    """Test wildcard pattern matching."""
    bus = create_eventbus('memory')

    received_events = []

    async def handler(event: Event):
        received_events.append(event)

    # Subscribe to wildcard pattern
    await bus.subscribe('workflow.*', handler)

    # Publish multiple events
    events = [
        Event.create('workflow.started', {}, 'test', 'tenant_123'),
        Event.create('workflow.completed', {}, 'test', 'tenant_123'),
        Event.create('bia.created', {}, 'test', 'tenant_123'),  # Won't match
    ]

    for event in events:
        await bus.publish(event)

    await asyncio.sleep(0.1)

    # Should receive only workflow events
    assert len(received_events) == 2
    assert all(e.type.startswith('workflow.') for e in received_events)

    await bus.close()


@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test multiple subscribers to same event."""
    bus = create_eventbus('memory')

    received_1 = []
    received_2 = []

    async def handler1(event: Event):
        received_1.append(event)

    async def handler2(event: Event):
        received_2.append(event)

    # Both subscribe to same event
    await bus.subscribe('test.event', handler1)
    await bus.subscribe('test.event', handler2)

    # Publish once
    event = Event.create('test.event', {}, 'test', 'tenant_123')
    await bus.publish(event)

    await asyncio.sleep(0.1)

    # Both should receive
    assert len(received_1) == 1
    assert len(received_2) == 1

    await bus.close()


@pytest.mark.asyncio
async def test_unsubscribe():
    """Test unsubscribing from events."""
    bus = create_eventbus('memory')

    received = []

    async def handler(event: Event):
        received.append(event)

    # Subscribe
    sub_id = await bus.subscribe('test.event', handler)

    # Publish - should receive
    await bus.publish(Event.create('test.event', {}, 'test', 'tenant_123'))
    await asyncio.sleep(0.1)
    assert len(received) == 1

    # Unsubscribe
    await bus.unsubscribe(sub_id)

    # Publish again - should NOT receive
    await bus.publish(Event.create('test.event', {}, 'test', 'tenant_123'))
    await asyncio.sleep(0.1)
    assert len(received) == 1  # Still 1 (not 2)

    await bus.close()


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in event handlers."""
    bus = create_eventbus('memory')

    call_count = 0

    async def failing_handler(event: Event):
        nonlocal call_count
        call_count += 1
        raise Exception("Handler error")

    await bus.subscribe('test.event', failing_handler)

    # Publish event
    event = Event.create('test.event', {}, 'test', 'tenant_123')
    event.max_retries = 2
    await bus.publish(event)

    # Wait for retries
    await asyncio.sleep(5)

    # Should be called multiple times (original + retries)
    assert call_count > 1

    await bus.close()


@pytest.mark.asyncio
async def test_event_priority():
    """Test event with different priorities."""
    bus = create_eventbus('memory')

    received = []

    async def handler(event: Event):
        received.append(event)

    await bus.subscribe('test.*', handler)

    # Publish events with different priorities
    priorities = [EventPriority.LOW, EventPriority.HIGH, EventPriority.CRITICAL]

    for priority in priorities:
        event = Event.create(
            'test.priority',
            {'priority': priority.name},
            'test',
            'tenant_123',
            priority=priority
        )
        await bus.publish(event)

    await asyncio.sleep(0.1)

    # All should be received
    assert len(received) == 3

    # Check priorities preserved
    assert received[0].priority == EventPriority.LOW
    assert received[1].priority == EventPriority.HIGH
    assert received[2].priority == EventPriority.CRITICAL

    await bus.close()


@pytest.mark.asyncio
async def test_stats():
    """Test bus statistics."""
    bus = create_eventbus('memory')

    async def handler(event: Event):
        pass

    await bus.subscribe('test.event', handler)

    # Publish events
    for i in range(5):
        event = Event.create('test.event', {'i': i}, 'test', 'tenant_123')
        await bus.publish(event)

    await asyncio.sleep(0.2)

    # Check stats
    stats = await bus.get_stats()
    assert stats['published'] == 5
    assert stats['consumed'] == 5

    await bus.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
