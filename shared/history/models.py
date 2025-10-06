"""
Change History Models
Field-level change tracking
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChangeType(str, Enum):
    """Type of change"""
    FIELD_UPDATE = "field_update"
    FIELD_ADD = "field_add"
    FIELD_REMOVE = "field_remove"
    RECORD_CREATE = "record_create"
    RECORD_DELETE = "record_delete"
    STATE_CHANGE = "state_change"


class ChangeHistoryModel(Base):
    """Change history database model"""
    __tablename__ = "change_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # What entity
    entity_type = Column(String(100), nullable=False)  # indexed in composite
    entity_id = Column(String(255), nullable=False)  # indexed in composite
    tenant_id = Column(String(255), nullable=False)  # indexed in composite

    # What changed
    change_type = Column(String(50), nullable=False)  # indexed in composite
    field_name = Column(String(255), nullable=True)  # indexed in composite
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)

    # Who/When
    changed_by = Column(String(255), nullable=False)  # indexed in composite
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # indexed in composite

    # Context
    change_reason = Column(Text, nullable=True)
    version_number = Column(Integer, nullable=True)  # indexed in composite
    snapshot = Column(JSON, nullable=True)  # Full entity snapshot
    change_metadata = Column(JSON, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        # Entity history lookup
        Index('idx_history_entity', 'entity_type', 'entity_id'),
        # Entity + field for field-level history
        Index('idx_history_entity_field', 'entity_type', 'entity_id', 'field_name'),
        # Tenant + timestamp for audit trail
        Index('idx_history_tenant_time_desc', 'tenant_id', 'changed_at'),
        # User activity tracking
        Index('idx_history_user_time', 'changed_by', 'changed_at'),
        # Entity + timestamp for change timeline
        Index('idx_history_entity_time', 'entity_type', 'entity_id', 'changed_at'),
        # Tenant + entity type filtering
        Index('idx_history_tenant_entity_type', 'tenant_id', 'entity_type'),
        # Version tracking
        Index('idx_history_entity_version', 'entity_type', 'entity_id', 'version_number'),
        # Change type analysis
        Index('idx_history_change_type', 'change_type', 'tenant_id'),
    )


class ChangeHistoryEntry(BaseModel):
    """Pydantic model for change history"""
    id: Optional[int] = None
    entity_type: str
    entity_id: str
    tenant_id: str
    change_type: ChangeType
    field_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None
    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    change_reason: Optional[str] = None
    version_number: Optional[int] = None
    snapshot: Optional[Dict[str, Any]] = None
    change_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class FieldChange(BaseModel):
    """Single field change"""
    field: str
    old_value: Any
    new_value: Any
    changed_at: datetime
    changed_by: str


class EntityHistory(BaseModel):
    """Complete history for an entity"""
    entity_type: str
    entity_id: str
    tenant_id: str
    current_version: int
    created_at: datetime
    created_by: str
    last_modified_at: datetime
    last_modified_by: str
    total_changes: int
    changes: List[ChangeHistoryEntry]
