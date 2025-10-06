"""
Audit Logger - Generalized from governance service
Logs all operations for compliance and auditing
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def log_audit_event(
    db: AsyncSession,
    event_type: str,
    service_name: str,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    action: Optional[str] = None,
    event_data: Optional[Dict[str, Any]] = None,
    http_method: Optional[str] = None,
    http_path: Optional[str] = None,
    http_status: Optional[int] = None,
    response_time_ms: Optional[int] = None,
    ip_address: Optional[str] = None
):
    """
    Log audit event to database

    Args:
        db: Database session
        event_type: Type of event
        service_name: Name of service generating event
        tenant_id: Tenant identifier
        user_id: User who performed action
        resource_type: Type of resource
        resource_id: ID of resource
        action: Action performed ('create', 'read', 'update', 'delete')
        event_data: Additional event data (JSONB)
        http_method: HTTP method
        http_path: API path
        http_status: HTTP status code
        response_time_ms: Response time in milliseconds
        ip_address: Client IP address
    """

    try:
        stmt = text("""
            INSERT INTO audit_log (
                event_type, service_name, tenant_id, user_id, resource_type, resource_id,
                action, event_data, http_method, http_path, http_status,
                response_time_ms, ip_address, created_at
            ) VALUES (
                :event_type, :service_name, :tenant_id, :user_id, :resource_type, :resource_id,
                :action, :event_data::jsonb, :http_method, :http_path, :http_status,
                :response_time_ms, :ip_address, :created_at
            )
        """)

        await db.execute(stmt, {
            "event_type": event_type,
            "service_name": service_name,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "event_data": event_data or {},
            "http_method": http_method,
            "http_path": http_path,
            "http_status": http_status,
            "response_time_ms": response_time_ms,
            "ip_address": ip_address,
            "created_at": datetime.utcnow()
        })

        await db.commit()

    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        # Don't raise - audit logging should never break the main flow
