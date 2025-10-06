"""
Validation Service
ISO 22301 Clauses 8.5, 9.1, 9.2, 9.3, 10

FastAPI microservice for:
- Exercise Management (ISO 8.5)
- Performance Monitoring & KPIs (ISO 9.1)
- Internal Audits (ISO 9.2)
- Management Reviews (ISO 9.3)
- CAPA & Continuous Improvement (ISO 10)
"""

import logging
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import httpx

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from shared.database import init_database, get_db
from config import settings
from models.database import Base
from api import routes
from events.subscribers import event_subscriber

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
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Workflow Intelligence global instances
workflow_storage = None
workflow_engine = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None


# ==================== DATABASE SETUP ====================

# Database manager will be initialized in lifespan
db_manager = None


async def init_db():
    """Initialize database (create all tables)"""
    from sqlalchemy.ext.asyncio import create_async_engine

    # Create engine temporarily just for table creation
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    await engine.dispose()


# ==================== ORCHESTRATOR REGISTRATION ====================

async def register_with_orchestrator(service_name: str, port: int, health_endpoint: str):
    """Register service with orchestrator"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ORCHESTRATOR_URL}/api/services/register",
                json={
                    "service_name": service_name,
                    "service_url": f"http://localhost:{port}",
                    "health_endpoint": health_endpoint,
                    "version": settings.SERVICE_VERSION,
                },
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info(f"Registered with orchestrator: {service_name}")
            else:
                logger.warning(f"Failed to register with orchestrator: {response.status_code}")
    except Exception as e:
        logger.error(f"Error registering with orchestrator: {e}")


async def unregister_from_orchestrator(service_name: str):
    """Unregister service from orchestrator"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.ORCHESTRATOR_URL}/api/services/unregister",
                json={"service_name": service_name},
                timeout=5.0
            )
            logger.info(f"Unregistered from orchestrator: {service_name}")
    except Exception as e:
        logger.error(f"Error unregistering from orchestrator: {e}")


# ==================== EVENT BUS SUBSCRIPTION ====================

async def subscribe_to_events(event_patterns: list):
    """Subscribe to events from event bus"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.EVENTBUS_URL}/api/subscriptions",
                json={
                    "service_name": settings.SERVICE_NAME,
                    "event_patterns": event_patterns,
                    "callback_url": f"http://localhost:{settings.SERVICE_PORT}/api/events/webhook",
                },
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info(f"Subscribed to events: {event_patterns}")
            else:
                logger.warning(f"Failed to subscribe to events: {response.status_code}")
    except Exception as e:
        logger.error(f"Error subscribing to events: {e}")


# ==================== FASTAPI LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager
    Handles startup and shutdown logic
    """
    global db_manager, workflow_storage, workflow_engine, case_collector

    # STARTUP
    logger.info(f"Starting {settings.SERVICE_NAME} service...")

    # Initialize database with connection pooling
    try:
        db_manager = init_database(
            database_url=settings.DATABASE_URL,
            pool_size=20,           # ✅ 20 connections
            max_overflow=10,        # ✅ +10 overflow
            pool_recycle=3600       # ✅ Recycle every hour
        )
        logger.info("Database connection pool initialized (pool_size=20)")

        # Create tables
        await init_db()
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize Workflow Intelligence
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="validation",
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

        logger.info("✅ Workflow Intelligence initialized (validation module)")
    except Exception as e:
        logger.warning(f"Workflow Intelligence initialization failed: {e}")

    # Register with orchestrator
    await register_with_orchestrator(
        service_name=settings.SERVICE_NAME,
        port=settings.SERVICE_PORT,
        health_endpoint="/health"
    )

    # Subscribe to events
    await subscribe_to_events([
        "governance.*",
        "plans.*",
        "incidents.*",
    ])

    logger.info(f"{settings.SERVICE_NAME} service started successfully")

    yield

    # SHUTDOWN
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    # Unregister from orchestrator
    await unregister_from_orchestrator(settings.SERVICE_NAME)

    # Close database connections
    if db_manager:
        await db_manager.dispose()
        logger.info("Database connections closed")

    logger.info(f"{settings.SERVICE_NAME} service shut down complete")


# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Validation Service",
    description="ISO 22301 Validation Module - Clauses 8.5, 9.1, 9.2, 9.3, 10 | BCI GPG PP6",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router)

# Include Workflow AI router
from api.workflow_ai import router as workflow_ai_router
app.include_router(workflow_ai_router)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ==================== HEALTH CHECK ====================


@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.4.6 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {"data": {}}

    result = await check_compliance(sample_context, iso_checker, "8.4.6")

    return {
        "iso_clause": "8.4.6",
        "module": "validation",
        "compliance_status": result
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "timestamp": "2025-10-03T00:00:00Z"
    }


# ==================== EVENT WEBHOOK ====================

@app.post("/api/events/webhook")
async def event_webhook(event: dict):
    """
    Webhook endpoint for receiving events from event bus
    """
    try:
        await event_subscriber.handle_event(
            event_type=event.get("event_type"),
            event_data=event.get("event_data"),
            tenant_id=event.get("tenant_id")
        )
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error handling webhook event: {e}")
        return {"status": "error", "message": str(e)}


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,  # Set to False in production
        log_level=settings.LOG_LEVEL.lower()
    )
