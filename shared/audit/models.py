"""
Audit Log Models
ISO 22301 compliant audit trail
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuditAction(str, Enum):
    """Audit action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    STATE_TRANSITION = "state_transition"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    EXPORT = "export"
    IMPORT = "import"


class AuditCategory(str, Enum):
    """Audit event categories"""
    BIA = "bia"
    COMPLIANCE = "compliance"
    EVIDENCE = "evidence"
    ASSESSMENT = "assessment"
    GAP = "gap"
    NONCONFORMITY = "nonconformity"
    AUDIT = "audit"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM = "system"


class AuditLogModel(Base):
    """Audit log database model"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Who
    user_id = Column(String(255), nullable=False)  # indexed in composite
    user_email = Column(String(255), nullable=True)
    tenant_id = Column(String(255), nullable=False)  # indexed in composite

    # What
    action = Column(String(50), nullable=False)  # indexed in composite
    category = Column(String(50), nullable=False)  # indexed in composite
    entity_type = Column(String(100), nullable=False)  # indexed in composite
    entity_id = Column(String(255), nullable=True)  # indexed in composite

    # Details
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # before/after values
    extra_metadata = Column('metadata', JSON, nullable=True)  # additional context

    # When/Where
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)  # indexed in composite
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)

    # Result
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        # Tenant isolation + timestamp (descending) for audit trail
        Index('idx_audit_tenant_time_desc', 'tenant_id', 'timestamp'),
        # User activity tracking
        Index('idx_audit_user_time_desc', 'user_id', 'timestamp'),
        # Entity lookup
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        # Category + timestamp for filtered queries
        Index('idx_audit_category_time', 'category', 'timestamp'),
        # Tenant + action filtering
        Index('idx_audit_tenant_action', 'tenant_id', 'action'),
        # Tenant + category + action for detailed filtering
        Index('idx_audit_tenant_cat_action', 'tenant_id', 'category', 'action'),
        # Success/failure tracking
        Index('idx_audit_tenant_success', 'tenant_id', 'success', 'timestamp'),
        # Entity + action for specific entity audits
        Index('idx_audit_entity_action', 'entity_type', 'entity_id', 'action'),
    )


class AuditLogEntry(BaseModel):
    """Pydantic model for audit log"""
    id: Optional[int] = None
    user_id: str
    user_email: Optional[str] = None
    tenant_id: str
    action: AuditAction
    category: AuditCategory
    entity_type: str
    entity_id: Optional[str] = None
    description: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
