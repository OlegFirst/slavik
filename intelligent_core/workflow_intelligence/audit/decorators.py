"""
Audit logging decorators
"""

from functools import wraps
from typing import Callable, Optional
import inspect

from ..auth import get_auth_context
from .logger import get_audit_logger
from .events import WorkflowEventType, SecurityEventType


def audit_log(
    event_type: str,
    action: str,
    resource_type: Optional[str] = None,
    resource_id_param: Optional[str] = None,
    iso_clause: Optional[str] = None
) -> Callable:
    """
    Decorator: Automatically log audit event when function is called

    Args:
        event_type: Type of event to log
        action: Description of action
        resource_type: Type of resource
        resource_id_param: Name of parameter containing resource ID
        iso_clause: Related ISO 22301 clause

    Usage:
        @audit_log(
            event_type=WorkflowEventType.CONTEXT_UPDATED,
            action="update workflow context",
            resource_type="workflow",
            resource_id_param="workflow_id",
            iso_clause="8.2.2"
        )
        async def update_workflow_context(workflow_id: str, context: dict, tenant_id: str):
            # Function will be audited automatically
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get auth context
            auth_ctx = get_auth_context()
            audit_logger = get_audit_logger()

            # Extract resource_id if specified
            resource_id = None
            if resource_id_param:
                # Try kwargs first
                resource_id = kwargs.get(resource_id_param)

                # Try positional args
                if resource_id is None:
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())

                    if resource_id_param in param_names:
                        param_index = param_names.index(resource_id_param)

                        # Account for 'self' in methods
                        if param_names[0] == 'self' and len(args) > param_index + 1:
                            resource_id = args[param_index + 1]
                        elif len(args) > param_index:
                            resource_id = args[param_index]

            # Execute function
            success = True
            error_message = None

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                success = False
                error_message = str(e)
                raise

            finally:
                # Log audit event (even if function failed)
                if audit_logger and auth_ctx:
                    try:
                        await audit_logger.log_workflow_event(
                            event_type=event_type,
                            user_id=auth_ctx.user_id,
                            tenant_id=auth_ctx.tenant_id,
                            workflow_id=resource_id or "unknown",
                            action=action,
                            success=success,
                            iso_clause=iso_clause,
                            metadata={
                                "function": func.__name__,
                                "error": error_message
                            }
                        )
                    except Exception as audit_error:
                        # Audit logging should never break the application
                        import structlog
                        log = structlog.get_logger(__name__)
                        log.error(
                            "audit.decorator.failed",
                            error=str(audit_error),
                            function=func.__name__
                        )

        return wrapper
    return decorator


def audit_security_event(
    event_type: str,
    action: str,
    resource_type: Optional[str] = None
) -> Callable:
    """
    Decorator: Log security event

    Args:
        event_type: Type of security event
        action: Description of action
        resource_type: Type of resource

    Usage:
        @audit_security_event(
            event_type=SecurityEventType.DATA_READ,
            action="read sensitive data",
            resource_type="workflow_context"
        )
        async def get_workflow_context(workflow_id: str):
            # Security event will be logged
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            auth_ctx = get_auth_context()
            audit_logger = get_audit_logger()

            success = True
            error_message = None

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                success = False
                error_message = str(e)
                raise

            finally:
                # Log security event
                if audit_logger and auth_ctx:
                    try:
                        await audit_logger.log_security_event(
                            event_type=event_type,
                            user_id=auth_ctx.user_id,
                            tenant_id=auth_ctx.tenant_id,
                            action=action,
                            success=success,
                            resource_type=resource_type,
                            error_message=error_message,
                            metadata={
                                "function": func.__name__
                            }
                        )
                    except Exception:
                        # Silent fail - audit logging should not break app
                        pass

        return wrapper
    return decorator
