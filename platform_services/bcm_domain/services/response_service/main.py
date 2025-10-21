"""
Response Module - Main Application
ISO 22301:2019 Clause 8.4 - Incident Response

Complete FastAPI application for incident response management
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Add shared database to path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

from database import init_db, close_db, check_db_health

from config import settings
from api.routes import router
from events.publishers import ResponseEventPublisher
from events.subscribers import ResponseEventSubscriber

# Workflow Intelligence imports
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance
from prometheus_client import make_asgi_app

# Configure logging
logger = logging.getLogger(__name__)

# Workflow Intelligence global instances
workflow_storage = None
workflow_engine = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None


# ============================================================================
# Lifespan Manager
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown events
    """
    global workflow_storage, workflow_engine, case_collector
    global audit_logger, iso_checker, security_middleware

    # ========================================================================
    # STARTUP
    # ========================================================================
    logger.info("=" * 80)
    logger.info(f"Starting {settings.SERVICE_NAME} service v{settings.SERVICE_VERSION}")
    logger.info(f"ISO Standard: {settings.ISO_STANDARD} Clause {settings.ISO_CLAUSE}")
    logger.info("=" * 80)

    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        await init_db()

        # Check if response schema exists
        logger.info("Checking database schema...")
        db_health = await check_db_health()
        if db_health.get("status") == "healthy":
            logger.info(f" Database connection healthy (latency: {db_health.get('latency_ms')}ms)")
        else:
            logger.error(f" Database unhealthy: {db_health.get('error')}")

        # Initialize Workflow Intelligence
        try:
            workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
            await workflow_storage.connect()

            workflow_engine = WorkflowEngine(
                module="response",
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

            logger.info(" Workflow Intelligence initialized (response module)")
        except Exception as e:
            logger.warning(f"Workflow Intelligence initialization failed: {e}")

        # Initialize event publishers
        if settings.EVENT_BUS_ENABLED:
            logger.info("Initializing event publishers...")
            app.state.event_publisher = ResponseEventPublisher()
            await app.state.event_publisher.connect()
            logger.info(" Event publisher initialized")

            # Initialize event subscribers
            logger.info("Initializing event subscribers...")
            app.state.event_subscriber = ResponseEventSubscriber()
            await app.state.event_subscriber.start()
            logger.info(" Event subscriber initialized")
        else:
            logger.info("Event bus disabled - running in standalone mode")

        logger.info("=" * 80)
        logger.info(f" {settings.SERVICE_NAME} service started successfully")
        logger.info(f" Listening on http://{settings.HOST}:{settings.PORT}")
        logger.info(f" API Docs: http://{settings.HOST}:{settings.PORT}/docs")
        logger.info(f" Health Check: http://{settings.HOST}:{settings.PORT}/health")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f" Failed to start service: {e}")
        raise

    yield

    # ========================================================================
    # SHUTDOWN
    # ========================================================================
    logger.info("=" * 80)
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")
    logger.info("=" * 80)

    try:
        # Close Workflow Intelligence
        if workflow_storage:
            try:
                await workflow_storage.close()
                logger.info("Workflow Intelligence connection closed")
            except Exception as e:
                logger.error(f"Error closing Workflow Intelligence: {e}")

        # Close event connections
        if settings.EVENT_BUS_ENABLED and hasattr(app.state, "event_publisher"):
            logger.info("Closing event publisher...")
            await app.state.event_publisher.disconnect()

        if settings.EVENT_BUS_ENABLED and hasattr(app.state, "event_subscriber"):
            logger.info("Closing event subscriber...")
            await app.state.event_subscriber.stop()

        # Close database connection
        logger.info("Closing database connection...")
        await close_db()

        logger.info("=" * 80)
        logger.info(f" {settings.SERVICE_NAME} service stopped successfully")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f" Error during shutdown: {e}")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.SERVICE_NAME.upper() + " Service",
    description=settings.SERVICE_DESCRIPTION,
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============================================================================
# Middleware
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.debug(f" {request.method} {request.url.path}")

    response = await call_next(request)

    logger.debug(f" {request.method} {request.url.path} - {response.status_code}")

    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Error {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation Error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "status_code": 422,
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.is_production:
        message = "Internal Server Error"
    else:
        message = str(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": message,
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


# ============================================================================
# Routes
# ============================================================================

# Include API router
app.include_router(router)

# Include Workflow AI router
from api.workflow_ai import router as workflow_ai_router
app.include_router(workflow_ai_router)

# Prometheus metrics endpoint (replace existing /metrics endpoint)
metrics_app = make_asgi_app()
app.mount("/_metrics", metrics_app)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Service information
    """
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "description": settings.SERVICE_DESCRIPTION,
        "iso_standard": settings.ISO_STANDARD,
        "iso_clause": settings.ISO_CLAUSE,
        "status": "running",
        "docs": f"http://{settings.HOST}:{settings.PORT}/docs",
        "health": f"http://{settings.HOST}:{settings.PORT}/health"
    }


# Compliance check endpoint
@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.4.5 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    sample_context = {"data": {}}
    result = await check_compliance(sample_context, iso_checker, "8.4.5")

    return {
        "iso_clause": "8.4.5",
        "module": "response",
        "compliance_status": result
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns service health status including database connectivity
    """
    try:
        # Check database health
        db_health = await check_db_health()

        # Check event bus health
        event_bus_health = {
            "enabled": settings.EVENT_BUS_ENABLED,
            "status": "healthy" if settings.EVENT_BUS_ENABLED else "disabled"
        }

        if settings.EVENT_BUS_ENABLED and hasattr(app.state, "event_publisher"):
            event_bus_health["publisher_connected"] = app.state.event_publisher.broker_connected

        if settings.EVENT_BUS_ENABLED and hasattr(app.state, "event_subscriber"):
            event_bus_health["subscriber_connected"] = app.state.event_subscriber.broker_connected

        # Overall health
        overall_healthy = (
            db_health.get("status") == "healthy" and
            (not settings.EVENT_BUS_ENABLED or event_bus_health.get("status") == "healthy")
        )

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "service": settings.SERVICE_NAME,
            "version": settings.SERVICE_VERSION,
            "iso_standard": settings.ISO_STANDARD,
            "iso_clause": settings.ISO_CLAUSE,
            "timestamp": db_health.get("timestamp"),
            "components": {
                "database": db_health,
                "event_bus": event_bus_health
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": settings.SERVICE_NAME,
                "error": str(e)
            }
        )


# Readiness probe
@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness probe for Kubernetes

    Returns 200 if service is ready to accept traffic
    """
    try:
        db_health = await check_db_health()

        if db_health.get("status") == "healthy":
            return {"status": "ready", "service": settings.SERVICE_NAME}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": "database_unhealthy"}
            )

    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )


# Liveness probe
@app.get("/live", tags=["Health"])
async def liveness_check():
    """
    Liveness probe for Kubernetes

    Returns 200 if service is alive
    """
    return {"status": "alive", "service": settings.SERVICE_NAME}


# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Metrics endpoint

    Returns service metrics in Prometheus format (if enabled)
    """
    if not settings.METRICS_ENABLED:
        return {"error": "Metrics disabled"}

    # TODO: Implement Prometheus metrics
    return {
        "service": settings.SERVICE_NAME,
        "metrics_enabled": settings.METRICS_ENABLED,
        "note": "Prometheus metrics endpoint - implementation needed"
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.SERVICE_NAME} service...")
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"Debug: {settings.DEBUG}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
