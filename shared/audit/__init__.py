"""
Audit Module
ISO 22301 compliant audit trail for BCMS activities

This module provides comprehensive audit logging for:
- CRUD operations
- State transitions
- Permission changes
- Authentication events
- Data exports/imports

Usage:
    from shared.audit import AuditLogger, AuditAction, AuditCategory

    # Create audit logger
    audit = AuditLogger(db_session)

    # Log creation
    await audit.log_create(
        user_id="user123",
        tenant_id="tenant456",
        category=AuditCategory.BIA,
        entity_type="BIAProcess",
        entity_id="process789",
        entity_data={"name": "Critical Process"}
    )

    # Log state transition
    await audit.log_state_transition(
        user_id="user123",
        tenant_id="tenant456",
        category=AuditCategory.EVIDENCE,
        entity_type="Evidence",
        entity_id="evidence001",
        from_state="draft",
        to_state="submitted"
    )
"""

from .models import (
    AuditAction,
    AuditCategory,
    AuditLogModel,
    AuditLogEntry
)

from .logger import AuditLogger

from .decorators import (
    audit_log,
    audit_state_transition,
    with_audit_context
)

__all__ = [
    # Models
    'AuditAction',
    'AuditCategory',
    'AuditLogModel',
    'AuditLogEntry',

    # Logger
    'AuditLogger',

    # Decorators
    'audit_log',
    'audit_state_transition',
    'with_audit_context'
]

__version__ = '1.0.0'
