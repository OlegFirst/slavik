"""
Audit Decorators
Automatic audit logging for functions
"""

import logging
from functools import wraps
from typing import Optional, Callable, Dict, Any
from inspect import signature

from .models import AuditAction, AuditCategory

logger = logging.getLogger(__name__)


def audit_log(
    action: AuditAction,
    category: AuditCategory,
    entity_type: str,
    extract_entity_id: Optional[Callable] = None,
    extract_user_id: Optional[Callable] = None,
    extract_tenant_id: Optional[Callable] = None,
    extract_changes: Optional[Callable] = None
):
    """
    Decorator for automatic audit logging.

    Usage:
        @audit_log(
            action=AuditAction.CREATE,
            category=AuditCategory.BIA,
            entity_type="BIAProcess",
            extract_entity_id=lambda result: str(result.id)
        )
        async def create_process(...):
            ...

    Args:
        action: Audit action type
        category: Audit category
        entity_type: Entity type being audited
        extract_entity_id: Function to extract entity ID from result
        extract_user_id: Function to extract user ID from args/kwargs
        extract_tenant_id: Function to extract tenant ID from args/kwargs
        extract_changes: Function to extract before/after changes
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function first
            result = None
            success = True
            error_message = None

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                # Log audit event (fire-and-forget, don't block)
                try:
                    await _log_audit_event(
                        action=action,
                        category=category,
                        entity_type=entity_type,
                        result=result,
                        success=success,
                        error_message=error_message,
                        args=args,
                        kwargs=kwargs,
                        extract_entity_id=extract_entity_id,
                        extract_user_id=extract_user_id,
                        extract_tenant_id=extract_tenant_id,
                        extract_changes=extract_changes
                    )
                except Exception as audit_error:
                    # Never fail the actual operation due to audit logging
                    logger.error(f"Audit logging failed: {audit_error}")

            return result
        return wrapper
    return decorator


async def _log_audit_event(
    action: AuditAction,
    category: AuditCategory,
    entity_type: str,
    result: Any,
    success: bool,
    error_message: Optional[str],
    args: tuple,
    kwargs: dict,
    extract_entity_id: Optional[Callable],
    extract_user_id: Optional[Callable],
    extract_tenant_id: Optional[Callable],
    extract_changes: Optional[Callable]
):
    """Internal helper to log audit event"""

    # Extract context
    user_id = "system"
    tenant_id = "unknown"
    entity_id = None
    changes = None

    # Try to extract user_id
    if extract_user_id:
        try:
            user_id = extract_user_id(args, kwargs)
        except Exception:
            pass
    elif "user_id" in kwargs:
        user_id = kwargs["user_id"]
    elif "actor_id" in kwargs:
        user_id = kwargs["actor_id"]

    # Try to extract tenant_id
    if extract_tenant_id:
        try:
            tenant_id = extract_tenant_id(args, kwargs)
        except Exception:
            pass
    elif "tenant_id" in kwargs:
        tenant_id = kwargs["tenant_id"]

    # Try to extract entity_id
    if extract_entity_id and result:
        try:
            entity_id = extract_entity_id(result)
        except Exception:
            pass

    # Try to extract changes
    if extract_changes:
        try:
            changes = extract_changes(args, kwargs, result)
        except Exception:
            pass

    # Log to application logger (since we don't have direct DB access in decorator)
    logger.info(
        f"AUDIT: {action.value} {entity_type}:{entity_id} by {user_id} - {'SUCCESS' if success else 'FAILED'}",
        extra={
            "audit_action": action.value,
            "audit_category": category.value,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "success": success,
            "error_message": error_message,
            "changes": changes
        }
    )


def audit_state_transition(
    category: AuditCategory,
    entity_type: str
):
    """
    Decorator specifically for state transitions.

    Usage:
        @audit_state_transition(
            category=AuditCategory.EVIDENCE,
            entity_type="Evidence"
        )
        async def transition(entity_id, from_state, to_state, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get from_state and to_state from kwargs
            from_state = kwargs.get("from_state")
            to_state = kwargs.get("to_state")
            entity_id = kwargs.get("entity_id")
            user_id = kwargs.get("actor_id", "system")
            tenant_id = kwargs.get("tenant_id", "unknown")

            # Execute function
            success = True
            error_message = None
            result = None

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                # Log state transition
                try:
                    logger.info(
                        f"AUDIT: STATE_TRANSITION {entity_type}:{entity_id} "
                        f"{from_state.value if hasattr(from_state, 'value') else from_state} -> "
                        f"{to_state.value if hasattr(to_state, 'value') else to_state} "
                        f"by {user_id} - {'SUCCESS' if success else 'FAILED'}",
                        extra={
                            "audit_action": AuditAction.STATE_TRANSITION.value,
                            "audit_category": category.value,
                            "tenant_id": tenant_id,
                            "user_id": user_id,
                            "entity_type": entity_type,
                            "entity_id": entity_id,
                            "from_state": from_state.value if hasattr(from_state, "value") else from_state,
                            "to_state": to_state.value if hasattr(to_state, "value") else to_state,
                            "success": success,
                            "error_message": error_message
                        }
                    )
                except Exception as audit_error:
                    logger.error(f"Audit logging failed for state transition: {audit_error}")

            return result
        return wrapper
    return decorator


def with_audit_context(audit_logger):
    """
    Decorator that injects audit logger into function context.

    Usage:
        @with_audit_context(audit_logger)
        async def create_process(data, audit=None):
            # Use audit logger
            if audit:
                await audit.log_create(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Inject audit logger into kwargs
            kwargs['audit'] = audit_logger
            return await func(*args, **kwargs)
        return wrapper
    return decorator
