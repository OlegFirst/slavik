"""
Workflow Intelligence Integration
Adds: Auth, Audit Logging, Authorization, ISO Compliance
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

from workflow_intelligence.auth import AuthContext
from workflow_intelligence.auth.middleware import auth_context_var
from workflow_intelligence.audit import AuditLogger, SecurityAuditEvent
from workflow_intelligence.compliance import ISO22301Checker

logger = logging.getLogger(__name__)
security = HTTPBearer()


class WorkflowSecurityMiddleware:
    """Security middleware with Auth + Audit logging"""

    def __init__(
        self,
        audit_logger: AuditLogger,
        iso_checker: ISO22301Checker,
        jwt_secret: str,
        jwt_algorithm: str = "HS256"
    ):
        self.audit_logger = audit_logger
        self.iso_checker = iso_checker
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm

    async def __call__(self, request: Request, call_next):
        """Process request with security checks"""

        # Skip auth for public endpoints
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Extract and validate JWT
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            await self._log_security_event(
                event_type="auth.missing",
                request=request,
                success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )

        token = auth_header.replace("Bearer ", "")

        try:
            # Decode JWT
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )

            # Create auth context
            auth_ctx = AuthContext.from_jwt(payload)

            # Set context for request
            token = auth_context_var.set(auth_ctx)

            try:
                # Log successful authentication
                await self._log_security_event(
                    event_type="auth.success",
                    request=request,
                    success=True,
                    user_id=auth_ctx.user_id,
                    tenant_id=auth_ctx.tenant_id
                )

                # Process request
                response = await call_next(request)

                return response

            finally:
                # Reset context
                auth_context_var.reset(token)

        except jwt.ExpiredSignatureError:
            await self._log_security_event(
                event_type="auth.expired",
                request=request,
                success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )

        except jwt.InvalidTokenError as e:
            await self._log_security_event(
                event_type="auth.invalid",
                request=request,
                success=False,
                metadata={"error": str(e)}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def _log_security_event(
        self,
        event_type: str,
        request: Request,
        success: bool,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log security event"""

        event = SecurityAuditEvent(
            event_type=event_type,
            user_id=user_id or "anonymous",
            tenant_id=tenant_id or "unknown",
            action=f"{request.method} {request.url.path}",
            resource_type="api_endpoint",
            resource_id=request.url.path,
            success=success,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            metadata=metadata or {}
        )

        await self.audit_logger.log_event(event)


async def check_compliance(
    workflow_context: Dict[str, Any],
    iso_checker: ISO22301Checker,
    iso_clause: str
) -> Dict[str, Any]:
    """Check ISO 22301 compliance"""

    result = await iso_checker.check_compliance(
        workflow_context=workflow_context,
        iso_clause=iso_clause
    )

    logger.info(
        f"ISO 22301 Clause {iso_clause} compliance: {result['compliance_percentage']:.1f}%"
    )

    if not result['compliant']:
        logger.warning(
            f"Compliance gaps found: {len(result['gaps'])} issues"
        )

    return result
