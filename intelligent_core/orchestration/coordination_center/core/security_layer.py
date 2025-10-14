"""Security Layer - permissions, rate limiting, audit logging."""
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class Permission(str, Enum):
    """Permission types."""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"


class AIPermissions:
    """AI permission system."""

    # Default permissions for AI agent
    DEFAULT_PERMISSIONS = {
        Permission.READ: ["all"],  # AI can read everything
        Permission.CREATE: [
            "bia", "risk", "simulation", "digital_twin",
            "scenario", "assessment", "plan"
        ],
        Permission.UPDATE: [
            "bia", "risk", "simulation", "assessment"
        ],
        Permission.DELETE: [],  # AI cannot delete without approval
        Permission.EXECUTE: [
            "simulation", "scenario", "assessment", "analysis"
        ],
    }

    # Critical actions that require human approval
    CRITICAL_ACTIONS = [
        "delete",
        "activate_plan",  # Activating BC/DR plan
        "escalate_incident",  # Escalating incident
        "approve_document",  # Document approval
    ]

    @classmethod
    def check_permission(
        cls,
        action: str,
        entity: Optional[str] = None,
        user_id: str = "ai_agent"
    ) -> tuple[bool, Optional[str]]:
        """
        Check if AI has permission to perform action.

        Returns:
            (has_permission, reason_if_denied)
        """
        # Determine permission type from action
        perm_type = cls._get_permission_type(action)

        # Check if action requires approval
        if action in cls.CRITICAL_ACTIONS:
            return False, f"Action '{action}' requires human approval"

        # Check if entity is allowed for this permission type
        allowed_entities = cls.DEFAULT_PERMISSIONS.get(perm_type, [])

        if "all" in allowed_entities:
            return True, None

        if entity and entity in allowed_entities:
            return True, None

        return False, f"AI does not have '{perm_type}' permission for '{entity}'"

    @staticmethod
    def _get_permission_type(action: str) -> Permission:
        """Map action to permission type."""
        action_lower = action.lower()

        if any(x in action_lower for x in ["create", "add", "new"]):
            return Permission.CREATE
        elif any(x in action_lower for x in ["read", "get", "list", "view"]):
            return Permission.READ
        elif any(x in action_lower for x in ["update", "modify", "edit", "change"]):
            return Permission.UPDATE
        elif any(x in action_lower for x in ["delete", "remove", "destroy"]):
            return Permission.DELETE
        elif any(x in action_lower for x in ["execute", "run", "simulate", "analyze"]):
            return Permission.EXECUTE
        else:
            return Permission.READ  # Default to most restrictive


class RateLimiter:
    """Rate limiter using sliding window algorithm."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Storage: {user_id: [(timestamp, action), ...]}
        self.requests: Dict[str, List[tuple[float, str]]] = {}

    def check_rate_limit(
        self,
        user_id: str,
        action: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request is within rate limit.

        Returns:
            (is_allowed, reason_if_denied)
        """
        now = time.time()

        # Get user's request history
        if user_id not in self.requests:
            self.requests[user_id] = []

        user_requests = self.requests[user_id]

        # Remove old requests outside window
        cutoff = now - self.window_seconds
        user_requests = [(ts, act) for ts, act in user_requests if ts > cutoff]
        self.requests[user_id] = user_requests

        # Check if limit exceeded
        if len(user_requests) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"

        # Add current request
        user_requests.append((now, action))

        return True, None

    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests for user."""
        if user_id not in self.requests:
            return self.max_requests

        now = time.time()
        cutoff = now - self.window_seconds
        user_requests = [(ts, act) for ts, act in self.requests[user_id] if ts > cutoff]

        return max(0, self.max_requests - len(user_requests))


class AuditLogger:
    """Audit logger for all AI actions."""

    def __init__(self):
        # In-memory storage (в продакшене будет PostgreSQL)
        self.logs: List[Dict[str, Any]] = []

    def log_action(
        self,
        execution_id: str,
        action: str,
        user_id: str,
        tenant_id: str,
        details: Dict[str, Any],
        status: str = "initiated"
    ):
        """Log an action."""
        log_entry = {
            "id": len(self.logs) + 1,
            "execution_id": execution_id,
            "action": action,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "details": details,
            "status": status,
            "timestamp": datetime.utcnow(),
        }

        self.logs.append(log_entry)

    def get_logs(
        self,
        execution_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filters."""
        logs = self.logs

        if execution_id:
            logs = [log for log in logs if log["execution_id"] == execution_id]

        if user_id:
            logs = [log for log in logs if log["user_id"] == user_id]

        if tenant_id:
            logs = [log for log in logs if log["tenant_id"] == tenant_id]

        # Sort by timestamp desc
        logs.sort(key=lambda x: x["timestamp"], reverse=True)

        return logs[:limit]


class SecurityLayer:
    """Main security layer combining permissions, rate limiting, and audit."""

    def __init__(
        self,
        max_requests_per_minute: int = 100,
        require_approval_for: Optional[List[str]] = None
    ):
        self.permissions = AIPermissions()
        self.rate_limiter = RateLimiter(max_requests=max_requests_per_minute, window_seconds=60)
        self.audit_logger = AuditLogger()

        # Custom actions requiring approval
        if require_approval_for:
            self.permissions.CRITICAL_ACTIONS.extend(require_approval_for)

    async def authorize_request(
        self,
        execution_id: str,
        action: str,
        entity: Optional[str],
        user_id: str,
        tenant_id: str,
        details: Dict[str, Any]
    ) -> tuple[bool, Optional[str], bool]:
        """
        Authorize request.

        Returns:
            (is_authorized, reason_if_denied, requires_approval)
        """
        # 1. Check permissions
        has_permission, perm_reason = self.permissions.check_permission(action, entity, user_id)

        if not has_permission:
            # Log denial
            self.audit_logger.log_action(
                execution_id, action, user_id, tenant_id,
                details, status="permission_denied"
            )
            return False, perm_reason, False

        # 2. Check rate limit
        is_allowed, rate_reason = self.rate_limiter.check_rate_limit(user_id, action)

        if not is_allowed:
            # Log rate limit
            self.audit_logger.log_action(
                execution_id, action, user_id, tenant_id,
                details, status="rate_limited"
            )
            return False, rate_reason, False

        # 3. Check if requires approval
        requires_approval = action in self.permissions.CRITICAL_ACTIONS

        # Log authorization
        status = "authorized_pending_approval" if requires_approval else "authorized"
        self.audit_logger.log_action(
            execution_id, action, user_id, tenant_id,
            details, status=status
        )

        return True, None, requires_approval

    def log_execution(
        self,
        execution_id: str,
        action: str,
        user_id: str,
        tenant_id: str,
        details: Dict[str, Any],
        status: str
    ):
        """Log execution result."""
        self.audit_logger.log_action(
            execution_id, action, user_id, tenant_id,
            details, status=status
        )


# Global security layer instance
security_layer = SecurityLayer(
    max_requests_per_minute=100,
    require_approval_for=["delete", "critical_update"]
)
