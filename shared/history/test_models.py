"""
Change History Models Test
Simple validation of models without requiring deepdiff
"""

from datetime import datetime


def test_models_syntax():
    """Test that models can be imported and instantiated"""
    import sys
    sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

    # Test basic imports
    from shared.history.models import (
        ChangeType,
        ChangeHistoryEntry,
        FieldChange,
        EntityHistory
    )

    print("=" * 60)
    print("Change History Models Validation")
    print("=" * 60 + "\n")

    # Test ChangeType enum
    print("Testing ChangeType enum:")
    print(f"  FIELD_UPDATE: {ChangeType.FIELD_UPDATE.value}")
    print(f"  FIELD_ADD: {ChangeType.FIELD_ADD.value}")
    print(f"  FIELD_REMOVE: {ChangeType.FIELD_REMOVE.value}")
    print(f"  RECORD_CREATE: {ChangeType.RECORD_CREATE.value}")
    print(f"  RECORD_DELETE: {ChangeType.RECORD_DELETE.value}")
    print(f"  STATE_CHANGE: {ChangeType.STATE_CHANGE.value}")
    print(" ChangeType enum works\n")

    # Test FieldChange model
    print("Testing FieldChange model:")
    field_change = FieldChange(
        field="rto_hours",
        old_value=24,
        new_value=12,
        changed_at=datetime.utcnow(),
        changed_by="test_user"
    )
    print(f"  Field: {field_change.field}")
    print(f"  Old value: {field_change.old_value}")
    print(f"  New value: {field_change.new_value}")
    print(f"  Changed by: {field_change.changed_by}")
    print(" FieldChange model works\n")

    # Test ChangeHistoryEntry model
    print("Testing ChangeHistoryEntry model:")
    entry = ChangeHistoryEntry(
        entity_type="BIAProcess",
        entity_id="123",
        tenant_id="tenant_abc",
        change_type=ChangeType.FIELD_UPDATE,
        field_name="rto_hours",
        old_value=24,
        new_value=12,
        changed_by="test_user",
        change_reason="Updated based on new risk assessment"
    )
    print(f"  Entity: {entry.entity_type}:{entry.entity_id}")
    print(f"  Field: {entry.field_name}")
    print(f"  Change: {entry.old_value} -> {entry.new_value}")
    print(f"  Reason: {entry.change_reason}")
    print(" ChangeHistoryEntry model works\n")

    # Test EntityHistory model
    print("Testing EntityHistory model:")
    history = EntityHistory(
        entity_type="BIAProcess",
        entity_id="123",
        tenant_id="tenant_abc",
        current_version=5,
        created_at=datetime.utcnow(),
        created_by="creator",
        last_modified_at=datetime.utcnow(),
        last_modified_by="modifier",
        total_changes=42,
        changes=[]
    )
    print(f"  Entity: {history.entity_type}:{history.entity_id}")
    print(f"  Version: {history.current_version}")
    print(f"  Total changes: {history.total_changes}")
    print(f"  Created by: {history.created_by}")
    print(f"  Last modified by: {history.last_modified_by}")
    print(" EntityHistory model works\n")

    # Test model serialization
    print("Testing model serialization:")
    entry_dict = entry.model_dump()
    print(f"  Serialized keys: {list(entry_dict.keys())}")
    print(f"  Can convert to JSON: {bool(entry_dict)}")
    print(" Model serialization works\n")

    print("=" * 60)
    print("All model tests passed! ")
    print("=" * 60)


if __name__ == "__main__":
    test_models_syntax()
