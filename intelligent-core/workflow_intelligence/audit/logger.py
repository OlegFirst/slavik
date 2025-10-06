"""
Audit logger - main interface for recording audit events
"""

from typing import Optional, Dict, Any
from datetime import datetime
import structlog

from .events import AuditEvent, SecurityEventType, WorkflowEventType
from .storage import AuditStorage


logger = structlog.get_logger(__name__)


class AuditLogger:
    """
    Main audit logger interface

    Usage:
        audit_logger = AuditLogger(storage)

        # Log security event
        await audit_logger.log_security_event(
            event_type=SecurityEventType.PERMISSION_DENIED,
            user_id="user_123",
            tenant_id="tenant_001",
            action="read_workflow_context",
            success=False
        )

        # Log workflow event
        await audit_logger.log_workflow_event(
            event_type=WorkflowEventType.CONTEXT_UPDATED,
            user_id="user_123",
            tenant_id="tenant_001",
            workflow_id="wf_456",
            action="update context"
        )
    """

    def __init__(self, storage: AuditStorage):
        """
        Initialize audit logger

        Args:
            storage: Audit storage backend
        """
        self.storage = storage

    async def log_event(self, event: AuditEvent) -> None:
        """
        Log generic audit event

        Args:
            event: AuditEvent to log
        """
        try:
            await self.storage.save_event(event)

            # Also log to structlog for immediate visibility
            logger.info(
                "audit.event",
                event_id=event.event_id,
                event_type=event.event_type,
                user_id=event.user_id,
                tenant_id=event.tenant_id,
                action=event.action,
                success=event.success,
                is_security=event.is_security_event
            )

        except Exception as e:
            # Audit logging should NEVER break the application
            # Log error but continue
            logger.error(
                "audit.log.failed",
                error=str(e),
                event_type=event.event_type,
                user_id=event.user_id
            )

    async def log_security_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        action: str,
        success: bool = True,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log security event

        Args:
            event_type: Type of security event
            user_id: User who performed action
            tenant_id: Tenant context
            action: Description of action
            success: Whether action succeeded
            resource_type: Type of resource accessed
            resource_id: ID of resource
            error_message: Error message if failed
            ip_address: User's IP address
            user_agent: User's user agent
            metadata: Additional metadata
        """
        event = AuditEvent.security_event(
            event_type=event_type,
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            success=success,
            resource_type=resource_type,
            resource_id=resource_id,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )

        await self.log_event(event)

    async def log_workflow_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        workflow_id: str,
        action: str,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        iso_clause: Optional[str] = None
    ) -> None:
        """
        Log workflow event

        Args:
            event_type: Type of workflow event
            user_id: User who performed action
            tenant_id: Tenant context
            workflow_id: Workflow identifier
            action: Description of action
            success: Whether action succeeded
            metadata: Additional metadata
            iso_clause: Related ISO 22301 clause
        """
        event = AuditEvent.workflow_event(
            event_type=event_type,
            user_id=user_id,
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            action=action,
            success=success,
            metadata=metadata or {},
            iso_clause=iso_clause
        )

        await self.log_event(event)

    async def log_data_access(
        self,
        operation: str,  # read, create, update, delete
        user_id: str,
        tenant_id: str,
        resource_type: str,
        resource_id: str,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log data access event

        Args:
            operation: Type of operation (read, create, update, delete)
            user_id: User who accessed data
            tenant_id: Tenant context
            resource_type: Type of resource
            resource_id: ID of resource
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        event = AuditEvent.data_access_event(
            operation=operation,
            user_id=user_id,
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            metadata=metadata or {}
        )

        await self.log_event(event)

    async def log_permission_denied(
        self,
        user_id: str,
        tenant_id: str,
        action: str,
        required_permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log permission denied event

        Args:
            user_id: User who was denied
            tenant_id: Tenant context
            action: Action that was denied
            required_permission: Permission that was required
            resource_type: Type of resource
            resource_id: ID of resource
            ip_address: User's IP
        """
        await self.log_security_event(
            event_type=SecurityEventType.PERMISSION_DENIED,
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            success=False,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            metadata={
                "required_permission": required_permission
            }
        )

    async def log_tenant_violation(
        self,
        user_id: str,
        user_tenant: str,
        attempted_tenant: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log tenant isolation violation attempt

        Args:
            user_id: User who attempted violation
            user_tenant: User's tenant
            attempted_tenant: Tenant user tried to access
            action: Action that was attempted
            resource_type: Type of resource
            resource_id: ID of resource
            ip_address: User's IP
        """
        await self.log_security_event(
            event_type=SecurityEventType.TENANT_ISOLATION_VIOLATED,
            user_id=user_id,
            tenant_id=user_tenant,
            action=action,
            success=False,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            metadata={
                "user_tenant": user_tenant,
                "attempted_tenant": attempted_tenant
            }
        )


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> Optional[AuditLogger]:
    """
    Get global audit logger instance

    Returns:
        AuditLogger if initialized, None otherwise

    Usage:
        audit_logger = get_audit_logger()
        if audit_logger:
            await audit_logger.log_security_event(...)
    """
    return _audit_logger


def set_audit_logger(logger: AuditLogger) -> None:
    """
    Set global audit logger instance

    Args:
        logger: AuditLogger instance

    Usage:
        storage = PostgresAuditStorage(pool)
        audit_logger = AuditLogger(storage)
        set_audit_logger(audit_logger)
    """
    global _audit_logger
    _audit_logger = logger
