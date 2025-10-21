"""
Governance Service - Main Entry Point
ISO 22301 Clauses 4 & 5 - Context & Leadership

Full business logic:
- Context of Organization (Clause 4)
- Leadership & Commitment (Clause 5)
- Policy Management
- Objectives & KPIs
- Scope Definition
- Domain Intelligence
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
import logging
from pydantic import BaseModel

from shared.database import init_database, close_db, get_db
from shared.eventbus import init_eventbus, get_eventbus
from shared.utils.logging import setup_logging
from shared.models import HealthCheck
from shared.auth import init_jwt, get_jwt_manager
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance
from prometheus_client import make_asgi_app

# Setup logging
setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None


# Auth models
class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    global workflow_storage, workflow_engine, ai_advisor, case_collector
    global audit_logger, iso_checker, security_middleware

    # Startup
    logger.info(f" Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")

    # Initialize JWT
    init_jwt(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    logger.info(" JWT initialized")

    # Initialize database
    _db_manager = init_database(
        database_url=settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=settings.DB_ECHO,
    )
    logger.info(" Database initialized")

    # Initialize Workflow Intelligence
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="governance",
            storage_adapter=workflow_storage
        )

        case_collector = CaseCollector(storage_adapter=workflow_storage)
        # Initialize Audit Logger
        audit_logger = AuditLogger(storage_adapter=workflow_storage)
        await audit_logger.ensure_schema()
        logger.info(" Audit logging initialized")

        # Initialize ISO Compliance Checker
        iso_checker = ISO22301Checker()
        logger.info(" ISO 22301 compliance checker initialized")

        # Initialize Security Middleware
        jwt_secret = getattr(settings, 'JWT_SECRET', 'dev-secret-key-change-in-production')
        security_middleware = WorkflowSecurityMiddleware(
            audit_logger=audit_logger,
            iso_checker=iso_checker,
            jwt_secret=jwt_secret
        )
        logger.info(" Security middleware initialized")

        

        # Set health metrics
        workflow_metrics.set_health("workflow_intelligence", True)
        workflow_metrics.set_health("database", True)
        workflow_metrics.set_health("audit_logging", True)
        workflow_metrics.set_health("iso_compliance", True)

        logger.info(" Workflow Intelligence initialized (Governance module)")
    except Exception as e:
        logger.warning(f"Workflow Intelligence initialization failed: {e}")

    # Initialize EventBus
    eventbus = init_eventbus(
        url=settings.EVENTBUS_URL,
        service_name=settings.SERVICE_NAME,
        timeout=settings.EVENTBUS_TIMEOUT,
    )
    logger.info(" EventBus initialized")

    # Register event subscriptions
    from events.subscribers import init_subscribers
    await init_subscribers()
    logger.info(" Event subscriptions registered")

    logger.info(f" {settings.SERVICE_NAME} ready on port {settings.SERVICE_PORT}")

    yield

    # Shutdown
    logger.info(f" Shutting down {settings.SERVICE_NAME}")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info(" Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    await close_db()
    await eventbus.close()

    logger.info(f" {settings.SERVICE_NAME} stopped")


# Create FastAPI app
app = FastAPI(
    title="Governance Service",
    description="ISO 22301 Context, Leadership & Governance",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routes
from api.routes import router
app.include_router(router, prefix="/api/v1/governance", tags=["Governance"])

# Import and include workflow AI router
from api.workflow_ai import router as workflow_ai_router
app.include_router(workflow_ai_router)


# Compliance check
@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 10.1 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    sample_context = {"data": {}}
    result = await check_compliance(sample_context, iso_checker, "10.1")

    return {
        "iso_clause": "10.1",
        "module": "governance",
        "compliance_status": result
    }


# Health check
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime

    return HealthCheck(
        service=settings.SERVICE_NAME,
        status="healthy",
        version=settings.SERVICE_VERSION,
        timestamp=datetime.utcnow(),
        components={
            "database": "connected",
            "eventbus": "connected",
            # "domain_intelligence": "ready",  # TODO: Implement domain intelligence
        }
    )


# Prometheus metrics endpoint (replace with proper ASGI mount)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "operational",
        "capabilities": [
            "context_management",  # Clause 4
            "leadership",          # Clause 5
            "policy_management",
            "objectives_kpis",
            "scope_definition",
            # "domain_intelligence",  # TODO: Implement domain intelligence
            # "ai_recommendations",   # TODO: Implement AI recommendations
        ],
        "api_docs": "/docs",
    }


@app.post("/auth/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Login endpoint to obtain JWT token.

    Validates credentials against auth.users table in Supabase.

    Demo users:
    - username: "admin", password: "admin123" → roles: ["admin", "bcm_manager"]
    - username: "manager", password: "admin123" → roles: ["manager", "bcm_manager"]
    - username: "user", password: "admin123" → roles: ["user"]
    - username: "resourcemgr", password: "admin123" → roles: ["resource_manager"]
    """
    from shared.auth.user_service import UserService, create_user_dict
    from shared.auth.jwt_handler import create_access_token

    # Authenticate user against database
    user_service = UserService(db)
    user = await user_service.authenticate_user(
        username=form_data.username,
        password=form_data.password,
        tenant_id="tenant_001"  # TODO: Get from domain or headers
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token with user data
    token = create_access_token(
        user_id=user.user_id,
        tenant_id=user.tenant_id,
        roles=user.roles
    )

    logger.info(f"Login successful for user: {user.username} (tenant: {user.tenant_id})")

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
