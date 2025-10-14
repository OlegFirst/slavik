"""
Plans Service - Main Application
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures

Port: 8023
Endpoints: 25+
Models: 8
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import httpx

from .config import settings
from .database import init_db, close_db
from .api.routes import router as plans_router
from .api.health import router as health_router
from .api.metrics import router as metrics_router
from .api.workflow_ai import router as workflow_ai_router
from .api.error_handlers import (
    validation_exception_handler,
    generic_exception_handler,
    value_error_handler
)
from .api.rate_limit import rate_limit_middleware
from shared.cache import init_cache, get_cache

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance
from prometheus_client import make_asgi_app

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Plans Service starting up...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Initialize Workflow Intelligence
        global workflow_storage, workflow_engine, ai_advisor, case_collector
        global audit_logger, iso_checker, security_middleware
        try:
            workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
            await workflow_storage.connect()

            workflow_engine = WorkflowEngine(
                module="plans",
                storage_adapter=workflow_storage
            )

            case_collector = CaseCollector(storage_adapter=workflow_storage)

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

            # Set health metrics
            workflow_metrics.set_health("workflow_intelligence", True)
            workflow_metrics.set_health("database", True)
            workflow_metrics.set_health("audit_logging", True)
            workflow_metrics.set_health("iso_compliance", True)

            logger.info("✅ Workflow Intelligence initialized (Plans module)")
        except Exception as e:
            logger.warning(f"Workflow Intelligence initialization failed: {e}")

        # Initialize Redis Cache
        redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/1')
        try:
            init_cache(redis_url)
            cache = get_cache()
            if await cache.ping():
                logger.info(f"Redis cache connected: {redis_url}")
            else:
                logger.warning("Redis cache connection failed - caching disabled")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")

        # Register with orchestrator
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.ORCHESTRATOR_URL}/services/register",
                    json={
                        "name": settings.SERVICE_NAME,
                        "port": settings.SERVICE_PORT,
                        "health_endpoint": "/health",
                        "iso_clauses": ["8.4"],
                        "bci_practices": ["PP5"],
                    },
                    timeout=5.0
                )
            logger.info("Registered with orchestrator")
        except Exception as e:
            logger.warning(f"Could not register with orchestrator: {e}")

        # Subscribe to events via EventBus
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.EVENTBUS_URL}/subscribe",
                    json={
                        "service": settings.SERVICE_NAME,
                        "topics": [
                            "planning.strategy.approved",  # Listen for approved strategies
                            "bia.analysis.completed",  # Listen for BIA completions
                            "exercise.completed",  # Listen for exercise completions
                        ]
                    },
                    timeout=5.0
                )
            logger.info("Subscribed to EventBus topics")
        except Exception as e:
            logger.warning(f"Could not subscribe to EventBus: {e}")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Plans Service shutting down...")

    try:
        # Unregister from orchestrator
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.ORCHESTRATOR_URL}/services/unregister",
                json={"name": settings.SERVICE_NAME},
                timeout=5.0
            )
        logger.info("Unregistered from orchestrator")
    except Exception as e:
        logger.warning(f"Could not unregister from orchestrator: {e}")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    # Close database
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="BCM Plans Service",
    description="""
    **Business Continuity Plans and Procedures Service - ISO 22301:2019 Clause 8.4**

    Comprehensive BC plan management aligned with ISO 22301:2019 Clause 8.4 requirements.

    ## 🎯 Core Features
    - **Plan Management**: Create, version, and maintain BC plans
    - **Procedure Tracking**: Step-by-step recovery procedures with dependencies
    - **Resource Management**: Track personnel, facilities, technology, supplies
    - **Contact Lists**: Emergency contacts and communication cascades (ISO 8.4.3)
    - **Plan Activation**: Real incident activation tracking
    - **Testing & Exercises**: Schedule and track plan tests
    - **Review Workflow**: Draft → Under Review → Approved → Active

    ## 📊 API Endpoints (25+)

    ### Plan Management
    - `POST /api/plans/plans` - Create BC plan
    - `GET /api/plans/plans` - List plans (with filters)
    - `GET /api/plans/plans/{id}` - Get plan details
    - `PUT /api/plans/plans/{id}` - Update plan (draft only)
    - `DELETE /api/plans/plans/{id}` - Archive plan

    ### Plan Workflow
    - `POST /api/plans/plans/{id}/submit-review` - Submit for review (Draft → Under Review)
    - `POST /api/plans/plans/{id}/approve` - Approve plan (Under Review → Approved)
    - `POST /api/plans/plans/{id}/activate` - Activate plan (Approved → Active)
    - `GET /api/plans/plans/{id}/workflow` - Get workflow status and available actions

    ### Procedures (ISO 8.4.4)
    - `POST /api/plans/plans/{id}/procedures` - Add procedure to plan
    - `GET /api/plans/plans/{id}/procedures` - List plan procedures
    - `PUT /api/plans/plans/{id}/procedures/{proc_id}` - Update procedure
    - `DELETE /api/plans/plans/{id}/procedures/{proc_id}` - Delete procedure
    - **Dependency Tracking**: Define procedure execution order and prerequisites

    ### Resources (ISO 8.4.4)
    - `POST /api/plans/plans/{id}/resources` - Add resource to plan
    - `GET /api/plans/plans/{id}/resources` - List plan resources
    - **Resource Types**: PERSONNEL, FACILITY, TECHNOLOGY, SUPPLIES, THIRD_PARTY

    ### Contact Lists (ISO 8.4.3)
    - `POST /api/plans/contact-lists` - Create contact list
    - `GET /api/plans/contact-lists?plan_id={id}` - List contact lists
    - **Contact Roles**: INCIDENT_MANAGER, TEAM_LEAD, TECHNICAL_LEAD, STAKEHOLDER, VENDOR

    ### Plan Activation (ISO 8.4.2)
    - `POST /api/plans/plans/{id}/activate-real` - Activate for real incident
    - `GET /api/plans/activations?plan_id={id}` - List plan activations
    - **Activation Types**: REAL_INCIDENT, TEST_EXERCISE, DRILL

    ### Reviews & Maintenance
    - `POST /api/plans/plans/{id}/reviews` - Create plan review
    - `GET /api/plans/plans/{id}/reviews` - List plan reviews
    - **Review Triggers**: SCHEDULED, POST_INCIDENT, POST_EXERCISE, REGULATORY

    ## 🔐 Authentication
    - **JWT Bearer Token** required
    - **Tenant Isolation**: Automatic filtering by tenant_id
    - **RBAC**: PLAN_CREATE, PLAN_VIEW, PLAN_APPROVE, PLAN_ACTIVATE permissions

    ## 🏗️ ISO 22301:2019 Clause 8.4 Compliance

    ### Clause 8.4.1 - General
    ✅ Documented BC plans and procedures
    ✅ Plan scope and objectives
    ✅ Version control and change management
    ✅ Review and update schedules

    ### Clause 8.4.2 - Incident Response Structure
    ✅ Incident response team roles
    ✅ Decision-making authority
    ✅ Escalation procedures
    ✅ Command and control structure

    ### Clause 8.4.3 - Warning and Communication
    ✅ Contact lists (internal/external)
    ✅ Communication methods
    ✅ Message templates
    ✅ Communication cascades

    ### Clause 8.4.4 - BC Plans and Procedures Content
    ✅ Step-by-step procedures
    ✅ Resource requirements
    ✅ Dependencies and prerequisites
    ✅ Recovery priorities
    ✅ Roles and responsibilities

    ## 📚 Request/Response Examples

    ### Create Plan
    ```json
    {
      "tenant_id": "tenant-123",
      "name": "Payment System Recovery Plan",
      "plan_type": "IT_RECOVERY",
      "description": "Recovery procedures for payment processing system",
      "scope": "Payment processing infrastructure and applications",
      "objectives": "Restore payment processing within 2 hours RTO",
      "owner_id": "user-456",
      "priority": "CRITICAL"
    }
    ```

    ### Add Procedure with Dependencies
    ```json
    {
      "title": "Restore Database Server",
      "description": "Restore primary database from backup",
      "step_number": 3,
      "estimated_duration_minutes": 45,
      "responsible_role": "DBA",
      "instructions": "1. Mount backup volume\n2. Run restore script\n3. Verify data integrity",
      "dependencies": [2],
      "required_resources": ["backup_storage", "dba_team"]
    }
    ```

    ### Plan Activation
    ```json
    {
      "activation_type": "REAL_INCIDENT",
      "incident_description": "Payment gateway outage - unable to process transactions",
      "severity": "CRITICAL",
      "activated_by": "user-789",
      "incident_start_time": "2024-01-15T10:30:00Z"
    }
    ```

    ## 🔄 Plan Lifecycle Workflow

    ```
    DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → RETIRED
              ↓                           ↓
           REJECTED                    SUSPENDED
    ```

    **Valid Transitions:**
    - DRAFT → UNDER_REVIEW (submit for review)
    - UNDER_REVIEW → APPROVED (approve)
    - UNDER_REVIEW → REJECTED (reject)
    - APPROVED → ACTIVE (activate)
    - ACTIVE → SUSPENDED (suspend temporarily)
    - ACTIVE/SUSPENDED → RETIRED (retire/archive)

    ## 🔍 Error Codes
    - `400` - Validation error
    - `401` - Unauthorized
    - `403` - Forbidden
    - `404` - Plan/procedure/resource not found
    - `409` - Invalid state transition
    - `422` - Business rule violation (e.g., circular dependencies)

    ## 📖 Documentation
    - **Swagger UI**: /docs
    - **ReDoc**: /redoc
    - **Health Check**: /health

    ## 🚀 Integration
    - **Service Port**: 8023
    - **EventBus**: Port 8001
    - **Listens to**: planning.strategy.approved, bia.analysis.completed, exercise.completed
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "plans",
            "description": "BC Plan management - ISO 22301 Clause 8.4"
        },
        {
            "name": "procedures",
            "description": "Plan procedures with dependency tracking - ISO 22301 Clause 8.4.4"
        },
        {
            "name": "resources",
            "description": "Plan resource management - ISO 22301 Clause 8.4.4"
        },
        {
            "name": "contacts",
            "description": "Contact lists and communication - ISO 22301 Clause 8.4.3"
        },
        {
            "name": "activation",
            "description": "Plan activation and incident response - ISO 22301 Clause 8.4.2"
        },
        {
            "name": "reviews",
            "description": "Plan reviews and maintenance - ISO 22301 Clause 8.4"
        },
        {
            "name": "health",
            "description": "Service health and metrics"
        }
    ]
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# CORS middleware - Secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(plans_router)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(workflow_ai_router)  # Workflow Intelligence AI endpoints

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Health check endpoint

@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.4 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {"data": {}}

    result = await check_compliance(sample_context, iso_checker, "8.4")

    return {
        "iso_clause": "8.4",
        "module": "plans",
        "compliance_status": result
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "iso_clauses": ["8.4", "8.4.1", "8.4.2", "8.4.3", "8.4.4"],
        "bci_practices": ["PP5"],
        "port": settings.SERVICE_PORT,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "BCM Plans Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "Business Continuity Plans and Procedures - ISO 22301 Clause 8.4",
        "port": settings.SERVICE_PORT,
        "docs": "/docs",
        "health": "/health",
        "iso_compliance": {
            "clause_8_4": "Business Continuity Plans and Procedures",
            "clause_8_4_1": "General",
            "clause_8_4_2": "Incident Response Structure",
            "clause_8_4_3": "Warning and Communication",
            "clause_8_4_4": "BC Plans and Procedures Content"
        },
        "api_endpoints": {
            "plans": "/api/plans/plans - Plan management",
            "procedures": "/api/plans/plans/{id}/procedures - Procedure management",
            "resources": "/api/plans/plans/{id}/resources - Resource management",
            "contacts": "/api/plans/contact-lists - Contact list management",
            "activations": "/api/plans/activations - Plan activation tracking",
            "reviews": "/api/plans/plans/{id}/reviews - Plan review management"
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Plans Service on port {settings.SERVICE_PORT}")
    logger.info("ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures")
    logger.info("BCI PP5 - Enabling Solutions")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level="info"
    )
