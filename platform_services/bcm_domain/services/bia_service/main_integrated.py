"""
BIA Service - Integrated with Graceful Choreography
=====================================================

Enhanced BIA Service with:
1. Intelligent EventBus (AI-powered routing)
2. Saga Pattern support
3. Self-Aware service capabilities
4. CQRS pattern (optional)

This is the NEW main.py that integrates all architectural patterns.
Replace main.py with this file once tested.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import router as bia_router
from api.workflow_ai import router as workflow_ai_router
from database.connection import init_db, close_db

# Platform Integration - THE NEW WAY
from infrastructure.platform_integration import init_platform, get_platform, shutdown_platform

# Self-Aware Service Base - THE NEW WAY
try:
    from platform_services.bcm_domain.services._shared import SelfAwareService, EventPriority
    SELF_AWARE_AVAILABLE = True
except ImportError:
    SELF_AWARE_AVAILABLE = False
    logger.warning("Self-Aware Services not available")

# Original dependencies (kept for compatibility)
from shared.utils import setup_logging
from shared.middleware.error_handler import setup_error_handlers
from shared.auth import init_jwt
from shared.cache import init_cache

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

from workflow_integration import WorkflowSecurityMiddleware, check_compliance

# Setup logging
setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Global instances
platform = None
bia_self_aware_service = None
workflow_storage = None
workflow_engine = None
audit_logger = None
iso_checker = None
security_middleware = None


class BIASelfAwareService(SelfAwareService if SELF_AWARE_AVAILABLE else object):
    """
    BIA Service with Self-Aware capabilities

    Provides intelligent event handling with:
    - Automatic capability matching
    - Load-aware processing
    - Graceful degradation
    - Service collaboration
    """

    def __init__(self):
        if SELF_AWARE_AVAILABLE:
            super().__init__(
                service_name="bia_service",
                capabilities=[
                    "bia.assessment",
                    "bia.process.create",
                    "bia.process.update",
                    "bia.analysis",
                    "bia.reporting",
                ]
            )
            logger.info("✅ BIA Service initialized as Self-Aware")
        else:
            logger.warning("⚠️  BIA Service running in basic mode (Self-Aware not available)")

    async def initialize(self):
        """Initialize BIA-specific capabilities"""
        if SELF_AWARE_AVAILABLE:
            # Register event handlers with priorities
            self.register_handler("bia.process.*", self.handle_process_event, priority=EventPriority.HIGH)
            self.register_handler("bia.assessment.*", self.handle_assessment_event, priority=EventPriority.HIGH)
            self.register_handler("bia.*.completed", self.handle_completion_event, priority=EventPriority.NORMAL)
            self.register_handler("bia.analyze", self.handle_analysis_request, priority=EventPriority.NORMAL)

            logger.info("✅ BIA event handlers registered")

    async def handle_process_event(self, event):
        """Handle BIA process events"""
        logger.info(f"Handling BIA process event: {event.type}")
        # TODO: Implement actual BIA process handling
        return {"status": "processed", "event_type": event.type}

    async def handle_assessment_event(self, event):
        """Handle BIA assessment events"""
        logger.info(f"Handling BIA assessment event: {event.type}")
        # TODO: Implement actual assessment handling
        return {"status": "processed", "event_type": event.type}

    async def handle_completion_event(self, event):
        """Handle completion events (triggers next steps)"""
        logger.info(f"BIA completion event: {event.type}")

        # If platform available, can trigger saga
        if platform and platform.saga_orchestrator:
            logger.info("  → Considering saga orchestration for next steps")
            # TODO: Trigger appropriate saga (e.g., BCP generation)

        return {"status": "completion_processed"}

    async def handle_analysis_request(self, event):
        """Handle analysis requests"""
        logger.info(f"BIA analysis request: {event.type}")
        # TODO: Implement analysis logic
        return {"status": "analysis_completed"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced application lifespan with Platform Integration

    Startup sequence:
    1. Initialize Platform Integration (EventBus, Saga, CQRS)
    2. Initialize Database
    3. Initialize Self-Aware Service
    4. Initialize Workflow Intelligence
    5. Register with Platform
    """
    global platform, bia_self_aware_service, workflow_storage, workflow_engine
    global audit_logger, iso_checker, security_middleware

    # === STARTUP ===
    logger.info("=" * 60)
    logger.info("🚀 Starting BIA Service (Integrated with Graceful Choreography)")
    logger.info("=" * 60)
    logger.info(f"📍 Port: {settings.SERVICE_PORT}")
    logger.info(f"📋 ISO 22301 Clause: 8.2.2 - Business Impact Analysis")

    try:
        # === 1. Initialize Platform Integration ===
        logger.info("\n1️⃣  Initializing Platform Integration...")
        platform = await init_platform(
            database_url=settings.DATABASE_URL,
            redis_url=getattr(settings, 'REDIS_URL', 'redis://localhost:6379'),
            enable_intelligent_routing=True,
            enable_saga_engine=True,
            enable_self_aware=True,
            enable_cqrs=getattr(settings, 'ENABLE_CQRS', False)
        )

        platform_status = platform.get_status()
        logger.info(f"   Platform Status: {platform_status}")

        # === 2. Initialize JWT ===
        logger.info("\n2️⃣  Initializing Authentication...")
        init_jwt(settings.JWT_SECRET_KEY)
        logger.info("   ✅ JWT authentication initialized")

        # === 3. Initialize Database ===
        logger.info("\n3️⃣  Initializing Database...")
        await init_db(
            database_url=settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            echo=settings.DB_ECHO
        )
        logger.info(f"   ✅ Database initialized")

        # === 4. Initialize Cache ===
        logger.info("\n4️⃣  Initializing Cache...")
        await init_cache(getattr(settings, 'REDIS_URL', 'redis://localhost:6379'))
        logger.info("   ✅ Cache initialized")

        # === 5. Initialize Self-Aware Service ===
        if SELF_AWARE_AVAILABLE:
            logger.info("\n5️⃣  Initializing Self-Aware Service...")
            bia_self_aware_service = BIASelfAwareService()
            await bia_self_aware_service.initialize()

            # Subscribe to events via platform EventBus
            if platform.intelligent_router:
                logger.info("   📡 Registering with Intelligent EventBus...")
                # Register service capabilities with router
                await platform.intelligent_router.register_subscriber(
                    subscriber_id="bia_service",
                    event_pattern="bia.*",
                    handler=bia_self_aware_service.on_event,
                    capabilities={
                        "domains": ["bia", "business_impact", "continuity"],
                        "max_concurrent": 10,
                        "avg_processing_time_ms": 500,
                        "sla_ms": 2000,
                        "semantic_tags": ["bia", "impact", "assessment", "rto", "rpo"]
                    }
                )
                logger.info("   ✅ Self-Aware Service registered with Intelligent Router")
            elif platform.eventbus:
                logger.info("   📡 Registering with Basic EventBus...")
                await platform.eventbus.subscribe("bia.*", bia_self_aware_service.on_event)
                logger.info("   ✅ Self-Aware Service registered with EventBus")
        else:
            logger.warning("\n5️⃣  ⚠️  Self-Aware Services not available (basic mode)")

        # === 6. Initialize Workflow Intelligence ===
        logger.info("\n6️⃣  Initializing Workflow Intelligence...")
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="bia",
            storage_adapter=workflow_storage
        )

        audit_logger = AuditLogger(storage_adapter=workflow_storage)
        await audit_logger.ensure_schema()

        iso_checker = ISO22301Checker()

        security_middleware = WorkflowSecurityMiddleware(
            audit_logger=audit_logger,
            iso_checker=iso_checker,
            jwt_secret=settings.JWT_SECRET_KEY
        )

        logger.info("   ✅ Workflow Intelligence initialized")

        # === 7. Register BIA Sagas (if saga engine available) ===
        if platform.saga_orchestrator:
            logger.info("\n7️⃣  Registering BIA Sagas...")
            # Import saga definitions
            try:
                from intelligent_core.orchestration.saga_engine.example_sagas import (
                    create_bcm_program_saga,
                    create_incident_response_saga
                )

                # Register sagas
                platform.saga_orchestrator.register_saga(create_bcm_program_saga())
                platform.saga_orchestrator.register_saga(create_incident_response_saga())

                logger.info("   ✅ BIA Sagas registered")
            except ImportError:
                logger.warning("   ⚠️  Saga definitions not found")

        logger.info("\n" + "=" * 60)
        logger.info("✅ BIA Service ready (with Graceful Choreography)")
        logger.info("=" * 60)
        logger.info(f"   🌐 Docs: http://localhost:{settings.SERVICE_PORT}/docs")
        logger.info(f"   📊 Metrics: http://localhost:{settings.SERVICE_PORT}/metrics")
        logger.info(f"   ❤️  Health: http://localhost:{settings.SERVICE_PORT}/health")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"❌ Failed to start BIA Service: {e}", exc_info=True)
        raise

    yield  # Application running

    # === SHUTDOWN ===
    logger.info("\n" + "=" * 60)
    logger.info("🛑 Shutting down BIA Service...")
    logger.info("=" * 60)

    # Close workflow storage
    if workflow_storage:
        await workflow_storage.close()
        logger.info("   ✅ Workflow storage closed")

    # Close database
    await close_db()
    logger.info("   ✅ Database closed")

    # Shutdown platform
    await shutdown_platform()
    logger.info("   ✅ Platform integration shutdown")

    logger.info("=" * 60)
    logger.info("✅ BIA Service shutdown complete")
    logger.info("=" * 60)


# Create FastAPI app with enhanced lifespan
app = FastAPI(
    title=settings.SERVICE_TITLE,
    description=f"{settings.SERVICE_DESCRIPTION}\n\n**Enhanced with Graceful Choreography:**\n- Intelligent EventBus\n- Saga Pattern\n- Self-Aware capabilities\n- CQRS (optional)",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bia_router, prefix="/api", tags=["BIA"])
app.include_router(workflow_ai_router, prefix="/api/workflow-ai", tags=["Workflow AI"])

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Setup error handlers
setup_error_handlers(app)


# === ENHANCED HEALTH CHECK ===
@app.get("/health")
async def health_check():
    """
    Enhanced health check with platform status
    """
    health = {
        "status": "healthy",
        "service": "bia_service",
        "version": settings.SERVICE_VERSION,
        "iso_clause": "8.2.2"
    }

    # Add platform status
    if platform:
        health["platform"] = platform.get_status()

    # Add self-aware status
    if bia_self_aware_service and SELF_AWARE_AVAILABLE:
        health_status = await bia_self_aware_service.health_monitor.check_health()
        health["self_aware"] = {
            "status": health_status.status.value,
            "load": await bia_self_aware_service.load_manager.get_load_percentage()
        }

    return health


# === PLATFORM STATUS ENDPOINT ===
@app.get("/api/platform/status")
async def get_platform_status():
    """
    Get detailed platform integration status
    """
    if not platform:
        return {"error": "Platform not initialized"}

    status = platform.get_status()

    # Add component-specific details
    if platform.intelligent_router:
        status["intelligent_router"] = await platform.intelligent_router.get_metrics()

    if platform.saga_orchestrator:
        status["saga_engine"] = {
            "registered_sagas": list(platform.saga_orchestrator._sagas.keys())
        }

    return status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_integrated:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
