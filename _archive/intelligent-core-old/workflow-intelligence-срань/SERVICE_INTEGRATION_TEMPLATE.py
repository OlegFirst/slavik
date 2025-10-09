"""
Workflow Intelligence Integration Template
Copy this to any BCM service for quick integration

USAGE:
1. Copy workflow_integration.py to service directory
2. Add imports to main.py
3. Initialize in lifespan
4. Add middleware to app
5. Update module name and ISO clause

MODULES:
- bia-service: module="bia", iso_clause="8.2.2"
- risk-service: module="risk", iso_clause="8.2.3"
- planning_service: module="planning", iso_clause="8.3"
- plans_service: module="plans", iso_clause="8.4"
- response-service: module="response", iso_clause="8.4.5"
- validation-service: module="validation", iso_clause="8.4.6"
- compliance-service: module="compliance", iso_clause="9.2"
- governance-service: module="governance", iso_clause="10.1"
- documents-service: module="documents", iso_clause="7.5"
- learning-service: module="learning", iso_clause="10.2"
"""

# =============================================================================
# STEP 1: Create workflow_integration.py (same for all services)
# =============================================================================

WORKFLOW_INTEGRATION_PY = '''"""
Workflow Intelligence Integration for {SERVICE_NAME}
Adds: Auth, Audit Logging, Authorization, ISO Compliance
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Import workflow intelligence security features
from workflow_intelligence.auth import AuthContext, PermissionSet
from workflow_intelligence.auth.middleware import auth_context_var
from workflow_intelligence.audit import AuditLogger, SecurityAuditEvent
from workflow_intelligence.compliance import ISO22301Checker

logger = logging.getLogger(__name__)

# JWT Security
security = HTTPBearer()


class WorkflowSecurityMiddleware:
    """Security middleware for {SERVICE_NAME}"""

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
                metadata={{"error": str(e)}}
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
            action=f"{{request.method}} {{request.url.path}}",
            resource_type="api_endpoint",
            resource_id=request.url.path,
            success=success,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            metadata=metadata or {{}}
        )

        await self.audit_logger.log_event(event)


async def check_compliance(
    workflow_context: Dict[str, Any],
    iso_checker: ISO22301Checker,
    iso_clause: str
) -> Dict[str, Any]:
    """
    Check ISO 22301 compliance for module

    Args:
        workflow_context: Current workflow context
        iso_checker: ISO compliance checker
        iso_clause: ISO clause to check

    Returns:
        Compliance check results
    """

    result = await iso_checker.check_compliance(
        workflow_context=workflow_context,
        iso_clause=iso_clause
    )

    logger.info(
        f"ISO 22301 Clause {{iso_clause}} compliance: {{result['compliance_percentage']:.1f}}%"
    )

    if not result['compliant']:
        logger.warning(
            f"Compliance gaps found: {{len(result['gaps'])}} issues"
        )
        for gap in result['gaps']:
            logger.warning(f"  - {{gap['description']}}: {{gap['recommendation']}}")

    return result
'''

# =============================================================================
# STEP 2: Add imports to main.py
# =============================================================================

IMPORTS_TO_ADD = '''
# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker

# Service workflow integration
from .workflow_integration import WorkflowSecurityMiddleware, check_compliance
'''

# =============================================================================
# STEP 3: Add global variables to main.py
# =============================================================================

GLOBAL_VARS = '''
# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
audit_logger = None
iso_checker = None
security_middleware = None
'''

# =============================================================================
# STEP 4: Initialize in lifespan function
# =============================================================================

LIFESPAN_INIT = '''
        # Initialize Workflow Intelligence
        global workflow_storage, workflow_engine, audit_logger, iso_checker, security_middleware
        try:
            workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
            await workflow_storage.connect()

            workflow_engine = WorkflowEngine(
                module="{MODULE_NAME}",  # CHANGE THIS
                storage_adapter=workflow_storage
            )

            # Initialize Audit Logger
            audit_logger = AuditLogger(storage_adapter=workflow_storage)
            await audit_logger.ensure_schema()
            logger.info("✅ Audit logging initialized")

            # Initialize ISO Compliance Checker
            iso_checker = ISO22301Checker()
            logger.info("✅ ISO 22301 compliance checker initialized")

            # Initialize Security Middleware
            jwt_secret = getattr(settings, 'JWT_SECRET', 'dev-secret-key-change-in-production')
            security_middleware = WorkflowSecurityMiddleware(
                audit_logger=audit_logger,
                iso_checker=iso_checker,
                jwt_secret=jwt_secret
            )
            logger.info("✅ Security middleware initialized")

            logger.info("✅ Workflow Intelligence initialized ({MODULE_NAME} module)")
        except Exception as e:
            logger.warning(f"Workflow Intelligence initialization failed: {{e}}")
'''

# =============================================================================
# STEP 5: Add middleware to FastAPI app
# =============================================================================

MIDDLEWARE_CODE = '''
# Security middleware (Auth + Audit)
if security_middleware:
    app.middleware("http")(security_middleware)
'''

# =============================================================================
# STEP 6: Add compliance endpoint
# =============================================================================

COMPLIANCE_ENDPOINT = '''
@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause {ISO_CLAUSE} compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {{"error": "ISO compliance checker not initialized"}}

    # Example context - in production this would come from actual workflow
    sample_context = {{
        "data": {{
            # Add module-specific fields here
        }}
    }}

    result = await check_compliance(sample_context, iso_checker, "{ISO_CLAUSE}")

    return {{
        "iso_clause": "{ISO_CLAUSE}",
        "module": "{MODULE_NAME}",
        "compliance_status": result
    }}
'''

# =============================================================================
# Quick Reference: Module Mappings
# =============================================================================

SERVICE_MAPPINGS = {
    'bia-service': {
        'module': 'bia',
        'iso_clause': '8.2.2',
        'port': 8010,
        'description': 'Business Impact Analysis'
    },
    'risk-service': {
        'module': 'risk',
        'iso_clause': '8.2.3',
        'port': 8012,
        'description': 'Risk Assessment'
    },
    'planning_service': {
        'module': 'planning',
        'iso_clause': '8.3',
        'port': 8011,
        'description': 'Business Continuity Planning'
    },
    'plans_service': {
        'module': 'plans',
        'iso_clause': '8.4',
        'port': 8013,
        'description': 'BC Plans Management'
    },
    'response-service': {
        'module': 'response',
        'iso_clause': '8.4.5',
        'port': 8014,
        'description': 'Incident Response'
    },
    'validation-service': {
        'module': 'validation',
        'iso_clause': '8.4.6',
        'port': 8015,
        'description': 'Testing and Exercising'
    },
    'compliance-service': {
        'module': 'compliance',
        'iso_clause': '9.2',
        'port': 8016,
        'description': 'Internal Audit'
    },
    'governance-service': {
        'module': 'governance',
        'iso_clause': '10.1',
        'port': 8017,
        'description': 'Management Review'
    },
    'documents-service': {
        'module': 'documents',
        'iso_clause': '7.5',
        'port': 8018,
        'description': 'Document Control'
    },
    'learning-service': {
        'module': 'learning',
        'iso_clause': '10.2',
        'port': 8019,
        'description': 'Continual Improvement'
    },
}


if __name__ == "__main__":
    print("Workflow Intelligence Integration Template")
    print("=" * 60)
    print("\nService Mappings:")
    for service, config in SERVICE_MAPPINGS.items():
        print(f"\n{service}:")
        print(f"  Module: {config['module']}")
        print(f"  ISO Clause: {config['iso_clause']}")
        print(f"  Port: {config['port']}")
        print(f"  Description: {config['description']}")
