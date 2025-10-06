"""
Change Tracker Service
Field-level change detection and recording
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from deepdiff import DeepDiff

from .models import (
    ChangeHistoryModel,
    ChangeHistoryEntry,
    ChangeType,
    FieldChange,
    EntityHistory
)

logger = logging.getLogger(__name__)


class ChangeTracker:
    """Change tracking service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def detect_changes(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
        ignore_fields: List[str] = None
    ) -> List[FieldChange]:
        """
        Detect field-level changes between two entity states.

        Args:
            before: Entity state before change
            after: Entity state after change
            ignore_fields: Fields to ignore (e.g., updated_at, version)

        Returns:
            List of field changes
        """
        ignore_fields = ignore_fields or ["updated_at", "version"]

        # Use DeepDiff for nested change detection
        diff = DeepDiff(before, after, ignore_order=True, view='tree')

        changes = []

        # Values changed
        if 'values_changed' in diff:
            for change in diff['values_changed']:
                path_list = change.path(output_format='list')
                field = '.'.join(str(p) for p in path_list)
                if path_list[0] not in ignore_fields:
                    changes.append(FieldChange(
                        field=field,
                        old_value=change.t1,
                        new_value=change.t2,
                        changed_at=datetime.utcnow(),
                        changed_by="system"
                    ))

        # Items added
        if 'dictionary_item_added' in diff:
            for change in diff['dictionary_item_added']:
                path_list = change.path(output_format='list')
                field = '.'.join(str(p) for p in path_list)
                if path_list[0] not in ignore_fields:
                    changes.append(FieldChange(
                        field=field,
                        old_value=None,
                        new_value=change.t2,
                        changed_at=datetime.utcnow(),
                        changed_by="system"
                    ))

        # Items removed
        if 'dictionary_item_removed' in diff:
            for change in diff['dictionary_item_removed']:
                path_list = change.path(output_format='list')
                field = '.'.join(str(p) for p in path_list)
                if path_list[0] not in ignore_fields:
                    changes.append(FieldChange(
                        field=field,
                        old_value=change.t1,
                        new_value=None,
                        changed_at=datetime.utcnow(),
                        changed_by="system"
                    ))

        return changes

    async def track_changes(
        self,
        entity_type: str,
        entity_id: str,
        tenant_id: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        changed_by: str,
        change_reason: Optional[str] = None,
        version_number: Optional[int] = None,
        save_snapshot: bool = True
    ) -> List[ChangeHistoryEntry]:
        """
        Track and persist field-level changes.

        Args:
            entity_type: Type of entity (BIAProcess, Evidence, etc.)
            entity_id: Entity identifier
            tenant_id: Tenant context
            before: Entity state before change
            after: Entity state after change
            changed_by: User who made the change
            change_reason: Optional reason for change
            version_number: Entity version number
            save_snapshot: Whether to save full entity snapshot
        """
        # Detect changes
        field_changes = self.detect_changes(before, after)

        history_entries = []

        for change in field_changes:
            entry = ChangeHistoryModel(
                entity_type=entity_type,
                entity_id=entity_id,
                tenant_id=tenant_id,
                change_type=ChangeType.FIELD_UPDATE.value,
                field_name=change.field,
                old_value=self._serialize_value(change.old_value),
                new_value=self._serialize_value(change.new_value),
                changed_by=changed_by,
                changed_at=datetime.utcnow(),
                change_reason=change_reason,
                version_number=version_number,
                snapshot=after if save_snapshot else None
            )

            self.db.add(entry)
            history_entries.append(
                ChangeHistoryEntry.model_validate(entry)
            )

        await self.db.commit()

        logger.info(
            f"Tracked {len(field_changes)} field changes for {entity_type}:{entity_id}",
            extra={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "tenant_id": tenant_id,
                "changes_count": len(field_changes)
            }
        )

        return history_entries

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        tenant_id: str,
        limit: int = 100
    ) -> EntityHistory:
        """Get complete change history for an entity"""

        # Get all changes
        stmt = (
            select(ChangeHistoryModel)
            .where(ChangeHistoryModel.entity_type == entity_type)
            .where(ChangeHistoryModel.entity_id == entity_id)
            .where(ChangeHistoryModel.tenant_id == tenant_id)
            .order_by(ChangeHistoryModel.changed_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        changes = result.scalars().all()

        if not changes:
            raise ValueError(f"No history found for {entity_type}:{entity_id}")

        # Build history summary
        return EntityHistory(
            entity_type=entity_type,
            entity_id=entity_id,
            tenant_id=tenant_id,
            current_version=changes[0].version_number or 0,
            created_at=changes[-1].changed_at,
            created_by=changes[-1].changed_by,
            last_modified_at=changes[0].changed_at,
            last_modified_by=changes[0].changed_by,
            total_changes=len(changes),
            changes=[ChangeHistoryEntry.model_validate(c) for c in changes]
        )

    async def get_field_history(
        self,
        entity_type: str,
        entity_id: str,
        field_name: str,
        tenant_id: str
    ) -> List[FieldChange]:
        """Get change history for a specific field"""

        stmt = (
            select(ChangeHistoryModel)
            .where(ChangeHistoryModel.entity_type == entity_type)
            .where(ChangeHistoryModel.entity_id == entity_id)
            .where(ChangeHistoryModel.field_name == field_name)
            .where(ChangeHistoryModel.tenant_id == tenant_id)
            .order_by(ChangeHistoryModel.changed_at.desc())
        )

        result = await self.db.execute(stmt)
        changes = result.scalars().all()

        return [
            FieldChange(
                field=c.field_name,
                old_value=c.old_value,
                new_value=c.new_value,
                changed_at=c.changed_at,
                changed_by=c.changed_by
            )
            for c in changes
        ]

    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON storage"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, Enum):
            return value.value
        elif hasattr(value, 'model_dump'):
            return value.model_dump()
        elif hasattr(value, 'dict'):
            return value.dict()
        return value
