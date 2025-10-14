"""
Audit event definitions
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class AuditEventType(str, Enum):
    """Base audit event types"""
    SECURITY = "security"
    WORKFLOW = "workflow"
    DATA_ACCESS = "data_access"
    SYSTEM = "system"


class SecurityEventType(str, Enum):
    """Security-specific event types"""

    # Authentication events
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILED = "auth.failed"
    AUTH_LOGOUT = "auth.logout"

    # Authorization events
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_DENIED = "permission.denied"
    TENANT_ISOLATION_VIOLATED = "tenant.isolation.violated"

    # Data access events
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"

    # RLS events
    RLS_BYPASS_ATTEMPT = "rls.bypass.attempt"
    RLS_POLICY_VIOLATION = "rls.policy.violation"


class WorkflowEventType(str, Enum):
    """Workflow-specific event types"""

    # Workflow lifecycle
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Workflow actions
    ACTION_EXECUTED = "workflow.action.executed"
    ACTION_FAILED = "workflow.action.failed"

    # Context changes
    CONTEXT_CREATED = "workflow.context.created"
    CONTEXT_UPDATED = "workflow.context.updated"
    CONTEXT_DELETED = "workflow.context.deleted"

    # Case library
    CASE_SAVED = "workflow.case.saved"
    CASE_ACCESSED = "workflow.case.accessed"


@dataclass
class AuditEvent:
    """
    Comprehensive audit event

    Contains all necessary information for security audit, compliance, and forensics.
    """

    # Event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = None
    event_category: str = None

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Actor (who)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None

    # Action (what)
    action: str = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    # Metadata (additional context)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Security flags
    is_security_event: bool = False
    is_compliance_relevant: bool = False
    severity: str = "info"  # info, warning, error, critical

    # ISO 22301 compliance
    iso_clause: Optional[str] = None  # e.g., "8.2.2" for BIA

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "event_category": self.event_category,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "success": self.success,
            "error_message": self.error_message,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "is_security_event": self.is_security_event,
            "is_compliance_relevant": self.is_compliance_relevant,
            "severity": self.severity,
            "iso_clause": self.iso_clause,
        }

    @classmethod
    def security_event(
        cls,
        event_type: str,
        user_id: str,
        tenant_id: str,
        action: str,
        success: bool = True,
        **kwargs
    ) -> "AuditEvent":
        """
        Create security audit event

        Args:
            event_type: Type of security event (from SecurityEventType)
            user_id: User who performed action
            tenant_id: Tenant context
            action: Description of action
            success: Whether action succeeded
            **kwargs: Additional fields
        """
        return cls(
            event_type=event_type,
            event_category=AuditEventType.SECURITY,
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            success=success,
            is_security_event=True,
            is_compliance_relevant=True,
            severity="warning" if not success else "info",
            **kwargs
        )

    @classmethod
    def workflow_event(
        cls,
        event_type: str,
        user_id: str,
        tenant_id: str,
        workflow_id: str,
        action: str,
        **kwargs
    ) -> "AuditEvent":
        """
        Create workflow audit event

        Args:
            event_type: Type of workflow event (from WorkflowEventType)
            user_id: User who performed action
            tenant_id: Tenant context
            workflow_id: Workflow identifier
            action: Description of action
            **kwargs: Additional fields
        """
        return cls(
            event_type=event_type,
            event_category=AuditEventType.WORKFLOW,
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type="workflow",
            resource_id=workflow_id,
            is_compliance_relevant=True,
            **kwargs
        )

    @classmethod
    def data_access_event(
        cls,
        operation: str,  # read, create, update, delete
        user_id: str,
        tenant_id: str,
        resource_type: str,
        resource_id: str,
        **kwargs
    ) -> "AuditEvent":
        """
        Create data access audit event

        Args:
            operation: Type of data operation
            user_id: User who accessed data
            tenant_id: Tenant context
            resource_type: Type of resource accessed
            resource_id: ID of resource
            **kwargs: Additional fields
        """
        return cls(
            event_type=f"data.{operation}",
            event_category=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            tenant_id=tenant_id,
            action=f"{operation} {resource_type}",
            resource_type=resource_type,
            resource_id=resource_id,
            is_security_event=True,
            **kwargs
        )

# Alias for backward compatibility
SecurityAuditEvent = AuditEvent
