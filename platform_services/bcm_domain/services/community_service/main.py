"""
Community Service - Main Application

ISO 22301 Clause 10.2 - Continual Improvement & Knowledge Sharing

FastAPI entry point with lifespan management and unified architecture.
Provides BCM specialist marketplace and knowledge sharing platform.
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / "_shared"))

from config import settings
from shared.utils import setup_logging
from shared.eventbus import init_eventbus, get_eventbus
from shared.middleware.error_handler import setup_error_handlers
from shared.auth import init_jwt
from shared.cache import init_cache, get_cache

# Database
from shared.database import init_db, close_db

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Community Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
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
    logger.info(f" ISO 22301 Clause: 10.2 - Continual Improvement")

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
    global workflow_storage, workflow_engine, case_collector
    global audit_logger, iso_checker, security_middleware
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="community",
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

        logger.info(" Workflow Intelligence initialized (Community module)")
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

        # Subscribe to relevant events
        if settings.SUBSCRIBE_TOPICS:
            for topic in settings.SUBSCRIBE_TOPICS:
                await eventbus_client.subscribe(topic, handle_event)
            logger.info(f" EventBus subscribed to: {settings.SUBSCRIBE_TOPICS}")

    logger.info(" Community Service started successfully - Data will persist across restarts")

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
    EventBus event handler for Community service.

    Handles events from other services (e.g., learning completions, plan creations).
    """
    try:
        event_type = event_data.get("event_type", "unknown")
        logger.info(f" Received event: {event_type} for tenant {tenant_id}")

        # Handle specific event types
        if event_type == "learning.training.completed":
            # Award points for training completion
            logger.info("Training completed - awarding points to specialist")
        elif event_type == "validation.exercise.completed":
            # Encourage knowledge sharing from exercise learnings
            logger.info("Exercise completed - prompting knowledge contribution")
        elif event_type == "planning.plan.created":
            # Record knowledge contribution
            logger.info("Plan created - recording knowledge contribution")
        else:
            logger.debug(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Error handling event: {e}")


# Import event handlers for choreography
from event_handlers import get_community_event_handlers

# Initialize event handlers after eventbus is ready
async def setup_event_subscriptions():
    """
    Setup event subscriptions for Community service choreography.

    Community Service PUBLISHES:
    - community.specialist.registered
    - community.knowledge.shared
    - community.collaboration.started
    - community.marketplace.listing.created
    """
    try:
        eventbus = get_eventbus()
        if not eventbus:
            logger.warning("EventBus not available - skipping event subscriptions")
            return

        # Get Community event handlers
        handlers = get_community_event_handlers(eventbus)

        logger.info(" Community event handlers initialized (publisher mode)")
        logger.info(" Ready to publish: community.specialist.registered, community.knowledge.shared, etc.")

    except Exception as e:
        logger.error(f"Failed to setup event subscriptions: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_TITLE,
    description="""
    **ISO 22301:2019 - Community Service**

    BCM Specialist Marketplace and Knowledge Sharing Platform aligned with ISO 22301:2019 Clause 10.2.

    ## Core Features
    - **Specialist Marketplace**: Connect with BCM professionals and consultants
    - **Knowledge Sharing**: Share best practices, templates, and learnings
    - **Collaboration Portal**: Team collaboration and peer support
    - **Gamification**: Points, badges, and leaderboards for engagement
    - **Community Support**: Q&A, forums, and expert consultation

    ## Capabilities
    - community.specialists - Specialist profiles and marketplace
    - community.marketplace - Service listings and bookings
    - community.collaboration - Team collaboration tools
    - community.knowledge_sharing - Knowledge base and best practices
    - community.support - Community forums and Q&A

    ## Integration
    - **EventBus**: RabbitMQ on port 8001
    - **AI Orchestration**: Port 8002
    - **API Gateway**: Port 8000
    - **Service Port**: 8022
    """,
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Community",
            "description": "BCM specialist community and marketplace - ISO 22301 Clause 10.2"
        },
        {
            "name": "Specialists",
            "description": "Specialist profiles and marketplace listings"
        },
        {
            "name": "Knowledge",
            "description": "Knowledge sharing and best practices"
        },
        {
            "name": "Collaboration",
            "description": "Team collaboration and peer support"
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

# Include routers (will be imported dynamically)
try:
    from marketplace.api import router as marketplace_router
    app.include_router(marketplace_router, prefix="/api/marketplace", tags=["Marketplace"])
    logger.info(" Marketplace router included")
except ImportError:
    logger.warning("Marketplace router not available")

try:
    from portal.api import router as portal_router
    app.include_router(portal_router, prefix="/api/portal", tags=["Portal"])
    logger.info(" Portal router included")
except ImportError:
    logger.warning("Portal router not available")

# Workflow Intelligence AI endpoints
try:
    from api.workflow_ai import router as workflow_ai_router
    app.include_router(workflow_ai_router)
    logger.info(" Workflow AI router included")
except ImportError:
    logger.warning("Workflow AI router not available")

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
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
        "iso_clause": "10.2",
        "port": settings.SERVICE_PORT,
        "features": {
            "marketplace": settings.MARKETPLACE_ENABLED,
            "portal": settings.PORTAL_ENABLED,
            "knowledge_sharing": settings.KNOWLEDGE_SHARING_ENABLED,
            "gamification": settings.ENABLE_GAMIFICATION,
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
    Check ISO 22301 Clause 10.2 compliance for Community Service

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {
        "data": {
            "continual_improvement": True,
            "knowledge_management": True,
            "lessons_learned": True,
            "best_practices_sharing": True
        }
    }

    result = await check_compliance(sample_context, iso_checker, "10.2")

    return {
        "iso_clause": "10.2",
        "module": "community",
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_TITLE,
        "version": settings.SERVICE_VERSION,
        "iso_clause": "10.2",
        "documentation": f"http://localhost:{settings.SERVICE_PORT}/docs",
        "health": f"http://localhost:{settings.SERVICE_PORT}/health"
    }


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn

    logger.info(f" Starting Community Service on port {settings.SERVICE_PORT}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
