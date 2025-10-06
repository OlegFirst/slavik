"""
Change Tracker Tests
Demonstrates and validates change tracking functionality
"""

import asyncio
from datetime import datetime
from shared.history import ChangeTracker


def test_detect_changes_simple():
    """Test simple field changes detection"""
    before = {
        "name": "Old Name",
        "rto_hours": 24,
        "status": "draft"
    }

    after = {
        "name": "New Name",
        "rto_hours": 12,
        "status": "draft"
    }

    # Mock DB for testing
    class MockDB:
        pass

    tracker = ChangeTracker(MockDB())
    changes = tracker.detect_changes(before, after)

    print("Simple Field Changes:")
    for change in changes:
        print(f"  {change.field}: {change.old_value} -> {change.new_value}")

    assert len(changes) == 2
    assert any(c.field == "name" for c in changes)
    assert any(c.field == "rto_hours" for c in changes)
    print("✓ Simple changes detected correctly\n")


def test_detect_changes_nested():
    """Test nested object changes detection"""
    before = {
        "name": "Process A",
        "financial_impact": {
            "hourly_revenue_loss": 1000,
            "daily_revenue_loss": 24000
        }
    }

    after = {
        "name": "Process A",
        "financial_impact": {
            "hourly_revenue_loss": 2000,
            "daily_revenue_loss": 24000
        }
    }

    class MockDB:
        pass

    tracker = ChangeTracker(MockDB())
    changes = tracker.detect_changes(before, after)

    print("Nested Object Changes:")
    for change in changes:
        print(f"  {change.field}: {change.old_value} -> {change.new_value}")

    assert len(changes) == 1
    assert "financial_impact" in changes[0].field
    print("✓ Nested changes detected correctly\n")


def test_detect_changes_with_additions():
    """Test field additions detection"""
    before = {
        "name": "Process A",
        "rto_hours": 24
    }

    after = {
        "name": "Process A",
        "rto_hours": 24,
        "rpo_hours": 12
    }

    class MockDB:
        pass

    tracker = ChangeTracker(MockDB())
    changes = tracker.detect_changes(before, after)

    print("Field Additions:")
    for change in changes:
        print(f"  {change.field}: {change.old_value} -> {change.new_value}")

    assert len(changes) == 1
    assert changes[0].old_value is None
    assert changes[0].new_value == 12
    print("✓ Field additions detected correctly\n")


def test_detect_changes_with_removals():
    """Test field removal detection"""
    before = {
        "name": "Process A",
        "rto_hours": 24,
        "rpo_hours": 12
    }

    after = {
        "name": "Process A",
        "rto_hours": 24
    }

    class MockDB:
        pass

    tracker = ChangeTracker(MockDB())
    changes = tracker.detect_changes(before, after)

    print("Field Removals:")
    for change in changes:
        print(f"  {change.field}: {change.old_value} -> {change.new_value}")

    assert len(changes) == 1
    assert changes[0].old_value == 12
    assert changes[0].new_value is None
    print("✓ Field removals detected correctly\n")


def test_ignore_fields():
    """Test ignore_fields functionality"""
    before = {
        "name": "Process A",
        "updated_at": "2025-10-01T10:00:00",
        "version": 1
    }

    after = {
        "name": "Process A",
        "updated_at": "2025-10-03T15:30:00",
        "version": 2
    }

    class MockDB:
        pass

    tracker = ChangeTracker(MockDB())
    changes = tracker.detect_changes(before, after, ignore_fields=["updated_at", "version"])

    print("Ignored Fields Test:")
    print(f"  Changes detected: {len(changes)}")

    assert len(changes) == 0
    print("✓ Ignored fields work correctly\n")


def test_serialization():
    """Test value serialization"""
    from enum import Enum

    class Status(str, Enum):
        DRAFT = "draft"
        ACTIVE = "active"

    class MockDB:
        pass

    tracker = ChangeTracker(MockDB())

    # Test datetime serialization
    dt = datetime(2025, 10, 3, 12, 0, 0)
    serialized = tracker._serialize_value(dt)
    print(f"Datetime serialization: {dt} -> {serialized}")
    assert isinstance(serialized, str)

    # Test enum serialization
    status = Status.ACTIVE
    serialized = tracker._serialize_value(status)
    print(f"Enum serialization: {status} -> {serialized}")
    assert serialized == "active"

    print("✓ Serialization works correctly\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Change Tracker Tests")
    print("=" * 60 + "\n")

    test_detect_changes_simple()
    test_detect_changes_nested()
    test_detect_changes_with_additions()
    test_detect_changes_with_removals()
    test_ignore_fields()
    test_serialization()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
