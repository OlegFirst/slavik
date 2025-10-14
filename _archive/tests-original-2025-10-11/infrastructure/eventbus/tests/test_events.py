"""
Tests for Event Model
=====================

Unit tests for Event class.
"""

import pytest
from datetime import datetime
from infrastructure.eventbus import Event, EventPriority


def test_event_create():
    """Test event creation via factory method."""
    event = Event.create(
        event_type='bia.process_created',
        data={'process_id': 123},
        source='bia-service',
        tenant_id='tenant_456'
    )

    assert event.id is not None
    assert event.type == 'bia.process_created'
    assert event.data['process_id'] == 123
    assert event.source == 'bia-service'
    assert event.tenant_id == 'tenant_456'
    assert event.priority == EventPriority.NORMAL
    assert isinstance(event.timestamp, datetime)


def test_event_with_priority():
    """Test creating event with custom priority."""
    event = Event.create(
        event_type='alert.critical',
        data={},
        source='monitoring',
        tenant_id='tenant_123',
        priority=EventPriority.CRITICAL
    )

    assert event.priority == EventPriority.CRITICAL


def test_event_serialization():
    """Test event to_dict and from_dict."""
    original = Event.create(
        event_type='test.event',
        data={'key': 'value'},
        source='test-service',
        tenant_id='tenant_789',
        correlation_id='corr_123'
    )

    # Serialize
    event_dict = original.to_dict()

    # Deserialize
    restored = Event.from_dict(event_dict)

    # Compare
    assert restored.id == original.id
    assert restored.type == original.type
    assert restored.data == original.data
    assert restored.source == original.source
    assert restored.tenant_id == original.tenant_id
    assert restored.correlation_id == original.correlation_id
    assert restored.priority == original.priority


def test_event_priorities():
    """Test all priority levels."""
    priorities = [
        EventPriority.LOW,
        EventPriority.NORMAL,
        EventPriority.HIGH,
        EventPriority.CRITICAL
    ]

    for priority in priorities:
        event = Event.create(
            event_type='test.priority',
            data={},
            source='test',
            tenant_id='tenant_123',
            priority=priority
        )
        assert event.priority == priority


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
