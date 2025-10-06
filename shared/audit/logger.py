"""
Audit Logger Service
Centralized audit logging for ISO 22301 compliance
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from .models import AuditLogModel, AuditLogEntry, AuditAction, AuditCategory

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logger service for tracking all critical operations.

    Supports:
    - CRUD operations tracking
    - State transition logging
    - Permission changes
    - Authentication events
    - Forensic analysis requirements
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        user_id: str,
        tenant_id: str,
        action: AuditAction,
        category: AuditCategory,
        entity_type: str,
        entity_id: Optional[str] = None,
        description: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        user_email: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log audit event.

        Args:
            user_id: User performing action
            tenant_id: Tenant context
            action: Action type (CREATE, UPDATE, etc.)
            category: Event category (BIA, COMPLIANCE, etc.)
            entity_type: Type of entity (BIAProcess, Evidence, etc.)
            entity_id: Entity identifier
            description: Human-readable description
            changes: Before/after values for updates
            metadata: Additional context
            request: FastAPI request (for IP/user-agent)
            user_email: User email address
            success: Whether action succeeded
            error_message: Error details if failed

        Returns:
            AuditLogEntry: Created audit log entry
        """
        # Extract request metadata
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # Create log entry
        log_entry = AuditLogModel(
            user_id=user_id,
            user_email=user_email,
            tenant_id=tenant_id,
            action=action.value,
            category=category.value,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            changes=changes,
            metadata=metadata,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )

        try:
            self.db.add(log_entry)
            await self.db.commit()
            await self.db.refresh(log_entry)

            # Also log to application logger
            level = logging.INFO if success else logging.WARNING
            logger.log(
                level,
                f"AUDIT: {action.value} {entity_type}:{entity_id} by {user_id} - {'SUCCESS' if success else 'FAILED'}",
                extra={
                    "audit_category": category.value,
                    "tenant_id": tenant_id,
                    "user_id": user_id
                }
            )

            return AuditLogEntry.model_validate(log_entry)

        except Exception as e:
            # Never fail the actual operation due to audit logging
            # But log the failure prominently
            logger.error(
                f"CRITICAL: Failed to create audit log entry: {e}",
                extra={
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "action": action.value,
                    "entity_type": entity_type,
                    "entity_id": entity_id
                }
            )
            # Re-raise if this is a critical audit requirement
            # For now, we'll allow the operation to proceed
            raise

    async def log_create(
        self,
        user_id: str,
        tenant_id: str,
        category: AuditCategory,
        entity_type: str,
        entity_id: str,
        entity_data: Dict[str, Any],
        request: Optional[Request] = None,
        user_email: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log entity creation.

        Args:
            user_id: User who created the entity
            tenant_id: Tenant context
            category: Audit category
            entity_type: Type of entity created
            entity_id: ID of created entity
            entity_data: Entity data (sanitized)
            request: FastAPI request
            user_email: User email
        """
        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditAction.CREATE,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Created {entity_type} {entity_id}",
            metadata={"created_data": entity_data},
            request=request,
            user_email=user_email
        )

    async def log_update(
        self,
        user_id: str,
        tenant_id: str,
        category: AuditCategory,
        entity_type: str,
        entity_id: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        request: Optional[Request] = None,
        user_email: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log entity update with before/after comparison.

        Args:
            user_id: User who updated the entity
            tenant_id: Tenant context
            category: Audit category
            entity_type: Type of entity updated
            entity_id: ID of updated entity
            before: State before update
            after: State after update
            request: FastAPI request
            user_email: User email
        """
        # Calculate changed fields
        changed_fields = []
        for key in set(list(before.keys()) + list(after.keys())):
            if before.get(key) != after.get(key):
                changed_fields.append(key)

        changes = {
            "before": before,
            "after": after,
            "changed_fields": changed_fields
        }

        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditAction.UPDATE,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Updated {entity_type} {entity_id} ({len(changed_fields)} fields changed)",
            changes=changes,
            request=request,
            user_email=user_email
        )

    async def log_delete(
        self,
        user_id: str,
        tenant_id: str,
        category: AuditCategory,
        entity_type: str,
        entity_id: str,
        request: Optional[Request] = None,
        user_email: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log entity deletion.

        Args:
            user_id: User who deleted the entity
            tenant_id: Tenant context
            category: Audit category
            entity_type: Type of entity deleted
            entity_id: ID of deleted entity
            request: FastAPI request
            user_email: User email
        """
        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditAction.DELETE,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Deleted {entity_type} {entity_id}",
            request=request,
            user_email=user_email
        )

    async def log_state_transition(
        self,
        user_id: str,
        tenant_id: str,
        category: AuditCategory,
        entity_type: str,
        entity_id: str,
        from_state: str,
        to_state: str,
        request: Optional[Request] = None,
        user_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLogEntry:
        """
        Log workflow state transition.

        Args:
            user_id: User who triggered the transition
            tenant_id: Tenant context
            category: Audit category
            entity_type: Type of entity
            entity_id: ID of entity
            from_state: Previous state
            to_state: New state
            request: FastAPI request
            user_email: User email
            metadata: Additional transition metadata
        """
        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditAction.STATE_TRANSITION,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"{entity_type} {entity_id} transitioned from {from_state} to {to_state}",
            changes={"from_state": from_state, "to_state": to_state},
            metadata=metadata,
            request=request,
            user_email=user_email
        )

    async def log_permission_change(
        self,
        user_id: str,
        tenant_id: str,
        target_user_id: str,
        permission: str,
        granted: bool,
        request: Optional[Request] = None,
        user_email: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log permission grant or revocation.

        Args:
            user_id: User making the permission change
            tenant_id: Tenant context
            target_user_id: User receiving/losing permission
            permission: Permission identifier
            granted: True if granted, False if revoked
            request: FastAPI request
            user_email: User email
        """
        action = AuditAction.PERMISSION_GRANTED if granted else AuditAction.PERMISSION_REVOKED

        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            category=AuditCategory.AUTHORIZATION,
            entity_type="Permission",
            entity_id=permission,
            description=f"{'Granted' if granted else 'Revoked'} permission '{permission}' to/from user {target_user_id}",
            metadata={"target_user_id": target_user_id, "permission": permission},
            request=request,
            user_email=user_email
        )

    async def log_authentication(
        self,
        user_id: str,
        tenant_id: str,
        success: bool,
        request: Optional[Request] = None,
        user_email: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log authentication attempt.

        Args:
            user_id: User attempting to authenticate
            tenant_id: Tenant context
            success: Whether authentication succeeded
            request: FastAPI request
            user_email: User email
            error_message: Error message if failed
        """
        action = AuditAction.LOGIN if success else AuditAction.LOGIN

        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            category=AuditCategory.AUTHENTICATION,
            entity_type="Session",
            description=f"Authentication {'successful' if success else 'failed'} for user {user_id}",
            request=request,
            user_email=user_email,
            success=success,
            error_message=error_message
        )

    async def log_export(
        self,
        user_id: str,
        tenant_id: str,
        entity_type: str,
        export_format: str,
        filter_criteria: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        user_email: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log data export operation.

        Args:
            user_id: User exporting data
            tenant_id: Tenant context
            entity_type: Type of data exported
            export_format: Export format (CSV, PDF, etc.)
            filter_criteria: Filters applied to export
            request: FastAPI request
            user_email: User email
        """
        return await self.log(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditAction.EXPORT,
            category=AuditCategory.SYSTEM,
            entity_type=entity_type,
            description=f"Exported {entity_type} data in {export_format} format",
            metadata={
                "export_format": export_format,
                "filter_criteria": filter_criteria
            },
            request=request,
            user_email=user_email
        )
