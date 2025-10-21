"""
BIA Service - Main Application

ISO 22301 Clause 8.2.2 - Business Impact Analysis

FastAPI entry point with lifespan management and unified architecture.
All original functionality preserved from 695_line monolithic main.py.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import router as bia_router
from api.workflow_ai import router as workflow_ai_router
from database.connection import init_db, close_db
from shared.utils import setup_logging
from shared.eventbus import init_eventbus, get_eventbus
from shared.middleware.error_handler import setup_error_handlers
from shared.auth import init_jwt
from shared.cache import init_cache, get_cache

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# BIA Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None

# Setup logging
setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup/shutdown with database and EventBus integration.
    """
    # Startup
    logger.info(f" Starting {settings.SERVICE_TITLE}")
    logger.info(f" Port: {settings.SERVICE_PORT}")
    logger.info(f" ISO 22301 Clause: 8.2.2 - Business Impact Analysis")

    # Initialize JWT
    init_jwt(settings.JWT_SECRET)
    logger.info(" JWT authentication initialized")

    # Initialize Database
    await init_db(
        database_url=settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        echo=settings.DB_ECHO
    )
    logger.info(f" Database initialized: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'SQLite'}")

    # Initialize Workflow Intelligence
    global workflow_storage, workflow_engine, ai_advisor, case_collector
    global audit_logger, iso_checker, security_middleware
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="bia",
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

        logger.info(" Workflow Intelligence initialized (BIA module)")
    except Exception as e:
        logger.warning(f"Workflow Intelligence initialization failed: {e}")

    # Initialize Redis Cache
    redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
    init_cache(redis_url)
    cache = get_cache()
    if await cache.ping():
        logger.info(f" Redis cache connected: {redis_url}")
    else:
        logger.warning("️ Redis cache connection failed - caching disabled")

    # Initialize EventBus
    if settings.FEATURE_EVENTBUS:
        eventbus_client = init_eventbus(settings.EVENTBUS_URL)
        await eventbus_client.connect()
        logger.info(f" EventBus connected to RabbitMQ: {settings.EVENTBUS_URL}")

        # Setup event choreography subscriptions
        await setup_event_subscriptions()

        # Subscribe to relevant events (legacy)
        if settings.SUBSCRIBE_TOPICS:
            for topic in settings.SUBSCRIBE_TOPICS:
                await eventbus_client.subscribe(topic, handle_event)
            logger.info(f" EventBus subscribed to: {settings.SUBSCRIBE_TOPICS}")

    logger.info(" BIA Service started successfully - Data will persist across restarts")

    yield

    # Shutdown
    logger.info(f" Shutting down {settings.SERVICE_TITLE}")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    await close_db()
    logger.info(" Database connections closed")

    # Close Redis cache
    try:
        cache = get_cache()
        await cache.close()
        logger.info(" Redis cache closed")
    except Exception as e:
        logger.warning(f"Error closing Redis cache: {e}")


async def handle_event(event_data: dict, tenant_id: str = None):
    """
    EventBus event handler for BIA service.

    Handles events from other services (e.g., risk assessments, exercises).
    NOTE: This is kept for backward compatibility.
    New event handling is in event_handlers.py
    """
    try:
        event_type = event_data.get("event_type", "unknown")
        logger.info(f" Received event: {event_type} for tenant {tenant_id}")

        # Handle specific event types
        if event_type == "risk.assessment.completed":
            # Could trigger BIA review for high-risk processes
            logger.info("Risk assessment completed - may require BIA review")
        elif event_type == "exercise.completed":
            # Could update RTO/RPO based on exercise results
            logger.info("Exercise completed - may update recovery objectives")
        else:
            logger.debug(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Error handling event: {e}")


# Import event handlers for choreography
from event_handlers import get_bia_event_handlers

# Initialize event handlers after eventbus is ready
async def setup_event_subscriptions():
    """
    Setup event subscriptions for BIA service choreography.

    BIA Service PUBLISHES:
    - bia.assessment.completed
    - bia.process.created
    - bia.criticality.changed
    - bia.critical.process.identified

    No subscriptions needed - BIA is typically at the start of the flow.
    """
    try:
        eventbus = get_eventbus()
        if not eventbus:
            logger.warning("EventBus not available - skipping event subscriptions")
            return

        # Get BIA event handlers
        handlers = get_bia_event_handlers(eventbus)

        logger.info(" BIA event handlers initialized (publisher mode)")
        logger.info(" Ready to publish: bia.assessment.completed, bia.criticality.changed, etc.")

    except Exception as e:
        logger.error(f"Failed to setup event subscriptions: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_TITLE,
    description="""
    **ISO 22301:2019 - Business Impact Analysis Service**

    Comprehensive BIA capabilities aligned with ISO 22301:2019 Clause 8.2.2 requirements.

    ##  Core Features
    - **RTO/RPO/MTPD Calculations**: Recovery Time Objective, Recovery Point Objective, Maximum Tolerable Period of Disruption
    - **Financial Impact Assessment**: Multi-period financial impact analysis (1 hour to 1 month)
    - **Dependency Mapping**: Upstream/downstream process, technology, and supplier dependencies
    - **Critical Process Identification**: Automated criticality scoring and WHO tier classification
    - **AI-Powered Analysis**: Intelligent RTO/RPO suggestions and dependency discovery
    - **Multi-Industry Support**: Healthcare (WHO tiers), Financial Services, Manufacturing, IT, Retail, and more
    - **Supply Chain BCM**: Critical supplier management and supply chain risk assessment

    ##  API Endpoints (16 total)

    ### Process Management
    - `POST /api/bia/processes` - Create BIA process
    - `GET /api/bia/processes` - List processes (with filters)
    - `GET /api/bia/processes/{id}` - Get process details
    - `PUT /api/bia/processes/{id}` - Update process
    - `DELETE /api/bia/processes/{id}` - Delete process
    - `POST /api/bia/processes/{id}/complete` - Mark as completed

    ### AI-Powered Analysis
    - `POST /api/bia/processes/{id}/suggest-rto` - AI RTO/RPO/MTPD suggestions
    - `POST /api/bia/processes/{id}/discover-dependencies` - AI dependency discovery

    ### Bulk Operations
    - `POST /api/bia/processes/bulk` - Bulk create processes
    - `PATCH /api/bia/processes/bulk` - Bulk update processes
    - `DELETE /api/bia/processes/bulk` - Bulk delete processes
    - `POST /api/bia/processes/bulk/validate` - Validate before import

    ### Reporting
    - `GET /api/bia/reports/summary` - Executive summary report
    - `GET /api/bia/reports/critical-processes` - Critical processes report
    - `GET /api/bia/reports/dependencies` - Dependencies mapping report

    ### Supply Chain (Optional)
    - 8 additional endpoints for supply chain BCM management

    ##  Authentication & Authorization
    - **JWT Bearer Token** required for all endpoints
    - **Tenant Isolation**: Automatic filtering by tenant_id from JWT
    - **RBAC Permissions**: BIA_CREATE, BIA_VIEW, BIA_UPDATE, BIA_DELETE, BIA_COMPLETE, BIA_AI_SUGGEST
    - **Dev Mode**: Use `X-Dev-User` header with JSON user context

    ## ️ ISO 22301:2019 Compliance (Clause 8.2.2)

    ### Required Analysis Components
     **Criticality Assessment**: CriticalityLevel enum (CRITICAL, HIGH, MEDIUM, LOW)
     **Recovery Objectives**: RTO, RPO, MTPD in hours
     **Resource Requirements**: Personnel, facilities, technology, information, materials
     **Dependency Identification**: Upstream/downstream processes, suppliers, technologies
     **Impact Analysis**: Financial, operational, reputational, regulatory, patient safety

    ### Healthcare-Specific Features (ISO 22301 + WHO Guidelines)
    - WHO Essential Services Tier Classification (Tier 1-4)
    - Patient Safety Impact Assessment
    - Healthcare-specific compliance objectives

    ### Advanced Features
    - **Peak Period Analysis**: Different RTOs for peak vs normal periods
    - **Minimum Resource Levels**: Define minimum staff, facilities, tech for continuity
    - **Alternative Procedures**: Document workarounds and manual procedures
    - **Legal/Regulatory Tracking**: Map to HIPAA, GDPR, SOX, etc.
    - **Recovery Strategies**: Document recovery approach per process

    ##  Data Persistence
    - **PostgreSQL Database**: Full persistence across service restarts
    - **Redis Caching**: High-performance caching with hit/miss metrics
    - **Event-Driven**: EventBus integration for cross-service workflows

    ##  Integration
    - **EventBus**: RabbitMQ on port 8001
    - **AI Orchestration**: Port 8002
    - **API Gateway**: Port 8000
    - **Service Port**: 8012

    ##  Response Examples

    ### BIA Process Response
    ```json
    {
      "id": 1,
      "tenant_id": "tenant-123",
      "name": "Payment Processing",
      "criticality": "CRITICAL",
      "rto_hours": 2,
      "rpo_hours": 1,
      "mtpd_hours": 4,
      "financial_impact": {
        "1_hour": 50000,
        "4_hours": 200000,
        "24_hours": 1200000
      },
      "dependencies": [
        {"type": "technology", "name": "Payment Gateway", "criticality": 5}
      ]
    }
    ```

    ### AI RTO Suggestion Response
    ```json
    {
      "suggested_rto_hours": 2,
      "suggested_rpo_hours": 1,
      "suggested_mtpd_hours": 4,
      "confidence_score": 0.92,
      "reasoning": "Based on CRITICAL criticality and financial impact of $200K at 4 hours",
      "industry_benchmark": "Financial services typical RTO: 1-4 hours"
    }
    ```

    ##  Error Codes
    - `400` - Validation error (invalid input)
    - `401` - Unauthorized (missing/invalid JWT)
    - `403` - Forbidden (tenant mismatch, insufficient permissions)
    - `404` - Resource not found
    - `422` - Business rule violation
    - `500` - Internal server error

    ##  Documentation
    - **Swagger UI**: /docs
    - **ReDoc**: /redoc
    - **OpenAPI Spec**: /openapi.json
    - **Health Check**: /health
    - **Cache Metrics**: /metrics/cache
    """,
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "BIA",
            "description": "Business Impact Analysis process management - ISO 22301 Clause 8.2.2"
        },
        {
            "name": "AI Analysis",
            "description": "AI-powered RTO suggestions and dependency discovery"
        },
        {
            "name": "Bulk Operations",
            "description": "High-performance bulk create/update/delete operations with partial success support"
        },
        {
            "name": "Reporting",
            "description": "Executive reports, critical processes, and dependency mapping"
        },
        {
            "name": "Supply Chain",
            "description": "Supply Chain BCM and critical supplier management (optional module)"
        }
    ]
)

# Security middleware (Auth + Audit)
if security_middleware:
    app.middleware("http")(security_middleware)
    logger.info(" Security middleware enabled (Auth + Audit)")

# CORS Configuration
if settings.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f" CORS enabled for: {settings.CORS_ORIGINS}")

# Setup error handlers
setup_error_handlers(app)
logger.info(" Error handlers configured")

# Include BIA router
app.include_router(bia_router)
logger.info(" BIA router included")

# Include Workflow Intelligence router
app.include_router(workflow_ai_router)  # Workflow Intelligence AI endpoints

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include Supply Chain router (optional)
if settings.SUPPLY_CHAIN_ENABLED:
    try:
        from supply_chain_api import router as supply_chain_router
        app.include_router(supply_chain_router)
        logger.info(" Supply Chain BCM module loaded (8 endpoints)")
    except ImportError as e:
        logger.warning(f"️ Supply Chain BCM module not available: {e}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Original functionality from main.py preserved.
    """
    # Check Redis health
    cache_healthy = False
    try:
        cache = get_cache()
        cache_healthy = await cache.ping()
    except Exception:
        pass

    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "iso_clause": "8.2.2",
        "port": settings.SERVICE_PORT,
        "features": {
            "ai_enabled": settings.AI_ENABLED,
            "who_tier": settings.WHO_TIER_ENABLED,
            "supply_chain": settings.SUPPLY_CHAIN_ENABLED,
            "eventbus": settings.FEATURE_EVENTBUS
        },
        "cache": {
            "enabled": cache_healthy,
            "type": "redis"
        }
    }


@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.2.2 compliance for BIA

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {
        "data": {
            "critical_activities_list": True,
            "resource_inventory": True,
            "impact_analysis": True,
            "rto_rpo_defined": True,
            "priority_matrix": True,
            "mtpd_defined": True
        }
    }

    result = await check_compliance(sample_context, iso_checker, "8.2.2")

    return {
        "iso_clause": "8.2.2",
        "module": "bia",
        "compliance_status": result
    }


@app.get("/metrics/cache")
async def cache_metrics():
    """
    Get cache metrics endpoint.

    Returns cache hit/miss statistics.
    """
    try:
        cache = get_cache()
        return cache.get_metrics()
    except Exception as e:
        return {
            "error": str(e),
            "message": "Cache not initialized"
        }


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn

    logger.info(f" Starting BIA Service on port {settings.SERVICE_PORT}")
    logger.info(" Supply Chain BCM: EY research shows 20% faster recovery with ISO 22301")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
