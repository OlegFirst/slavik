"""
Documents Service - Main Application Entry Point
ISO 22301 Clause 7.5 - Documented Information

Production-ready 4-tier architecture with:
- Document lifecycle management
- AI/NLP processing (extraction, classification, analysis)
- Approval workflows
- Retention policies
- Version control
- Event-driven integration

Port: 8024
Database Schema: documents
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add shared library to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge

from config import settings
from shared.database import init_database, get_db, close_db
from models.database import Base
from api.routes import router
from events.eventbus import initialize_eventbus, get_eventbus
from events.handlers import EVENT_HANDLERS

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Service-specific metrics
requests_total = Counter(
    'documents_service_requests_total',
    'Total requests',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'documents_service_request_duration_seconds',
    'Request duration',
    ['endpoint']
)


# ============================================================================
# DATABASE SETUP
# ============================================================================

# Database manager will be initialized in lifespan
db_manager = None

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown tasks
    """
    global db_manager, workflow_storage, workflow_engine, ai_advisor, case_collector

    print(f"🚀 Documents Service starting...")

    # Create storage directories
    storage_path = Path(settings.STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Storage directory: {storage_path}")

    # Initialize database with connection pooling
    try:
        db_manager = init_database(
            database_url=settings.DATABASE_URL,
            pool_size=20,
            max_overflow=10
        )
        print(f"   ✅ Database connection pool initialized (pool_size=20)")

        # Create database schema
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"   ✅ Database schema initialized")
        await engine.dispose()
    except Exception as e:
        print(f"   ⚠️  Database initialization warning: {e}")

    # Initialize Workflow Intelligence
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="documents",
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

        print(f"   ✅ Workflow Intelligence initialized (Documents module)")
    except Exception as e:
        print(f"   ⚠️  Workflow Intelligence initialization warning: {e}")

    # Initialize EventBus
    try:
        print(f"📡 Connecting to EventBus: {settings.EVENTBUS_URL}")
        eventbus = initialize_eventbus(rabbitmq_url=settings.EVENTBUS_URL)
        await eventbus.connect()

        # Subscribe to events from other modules
        for event_type, handler in EVENT_HANDLERS.items():
            await eventbus.subscribe(event_type, handler)
            print(f"   ✅ Subscribed: {event_type}")

    except Exception as e:
        print(f"   ⚠️  EventBus connection warning: {e}")
        print(f"   ℹ️  Service will continue without EventBus")

    # Register with Orchestrator
    if settings.REGISTER_WITH_ORCHESTRATOR:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.ORCHESTRATOR_URL}/register",
                    json={
                        "service_name": settings.SERVICE_NAME,
                        "service_port": settings.SERVICE_PORT,
                        "health_endpoint": "/health",
                        "capabilities": [
                            "document_management",
                            "ai_processing",
                            "version_control",
                            "approval_workflow",
                            "retention_policy"
                        ]
                    },
                    timeout=5.0
                )
                if response.status_code == 200:
                    print(f"   ✅ Registered with Orchestrator")
        except Exception as e:
            print(f"   ⚠️  Orchestrator registration warning: {e}")

    print(f"✅ Documents Service ready on port {settings.SERVICE_PORT}")
    print(f"📚 API Documentation: http://localhost:{settings.SERVICE_PORT}/docs")

    yield

    # Shutdown
    print("👋 Documents Service shutting down...")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            print("   ✅ Workflow Intelligence connection closed")
        except Exception as e:
            print(f"   ⚠️  Error closing Workflow Intelligence: {e}")

    # Disconnect EventBus
    try:
        eventbus = get_eventbus()
        if eventbus and eventbus.is_connected:
            await eventbus.disconnect()
            print("   ✅ EventBus disconnected")
    except:
        pass

    # Unregister from Orchestrator
    if settings.REGISTER_WITH_ORCHESTRATOR:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.ORCHESTRATOR_URL}/unregister",
                    json={"service_name": settings.SERVICE_NAME},
                    timeout=5.0
                )
                print("   ✅ Unregistered from Orchestrator")
        except:
            pass

    # Close database connections
    await close_db()
    print("   ✅ Database connections closed")

    print("✅ Shutdown complete")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Documents Service",
    description="ISO 22301 Documented Information Management - Production",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Include API routes
app.include_router(router)

# Import and include workflow AI router
from api.workflow_ai import router as workflow_ai_router
app.include_router(workflow_ai_router)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ============================================================================
# HEALTH CHECK
# ============================================================================


@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 7.5 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {"data": {}}

    result = await check_compliance(sample_context, iso_checker, "7.5")

    return {
        "iso_clause": "7.5",
        "module": "documents",
        "compliance_status": result
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    eventbus_status = "disconnected"
    try:
        eventbus = get_eventbus()
        eventbus_status = "connected" if eventbus and eventbus.is_connected else "disconnected"
    except:
        pass

    db_status = "connected"
    try:
        async for session in get_db():
            await session.execute("SELECT 1")
            break
    except:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "port": settings.SERVICE_PORT,
        "eventbus": eventbus_status,
        "database": db_status
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Documents Service",
        "version": settings.SERVICE_VERSION,
        "description": "ISO 22301 Documented Information Management",
        "documentation": f"http://localhost:{settings.SERVICE_PORT}/docs",
        "health": f"http://localhost:{settings.SERVICE_PORT}/health"
    }


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
