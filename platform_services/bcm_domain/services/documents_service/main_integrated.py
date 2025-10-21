"""
Documents Service - Integrated with Graceful Choreography
==========================================================

Enhanced Documents Service with:
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
import os

from config import settings
from api.routes import router as service_router
from api.workflow_ai import router as workflow_ai_router

# Platform Integration - THE NEW WAY
from infrastructure.platform_integration import init_platform, get_platform, shutdown_platform

# Self-Aware Service Base - THE NEW WAY
try:
    from platform_services.bcm_domain.services._shared import SelfAwareService, EventPriority
    SELF_AWARE_AVAILABLE = True
except ImportError:
    SELF_AWARE_AVAILABLE = False
    print("WARNING: Self-Aware Services not available")

# Database
import sys
from pathlib import Path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

from database.connection import init_db, close_db

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

from workflow_integration import WorkflowSecurityMiddleware, check_compliance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
platform = None
service_self_aware = None
workflow_storage = None
workflow_engine = None
audit_logger = None
iso_checker = None
security_middleware = None


class DocumentsServiceSelfAware(SelfAwareService if SELF_AWARE_AVAILABLE else object):
    """
    Documents Service with Self-Aware capabilities

    Provides intelligent event handling with:
    - Automatic capability matching
    - Load-aware processing
    - Graceful degradation
    - Service collaboration
    """

    def __init__(self):
        if SELF_AWARE_AVAILABLE:
            super().__init__(
                service_name="documents_service",
                capabilities=[
                    "documents.create",
                    "documents.version_control",
                    "documents.approval",
                    "documents.distribution"
                ]
            )
            logger.info(" Documents Service initialized as Self-Aware")
        else:
            logger.warning("️  Documents Service running in basic mode (Self-Aware not available)")

    async def initialize(self):
        """Initialize Documents Service-specific capabilities"""
        if SELF_AWARE_AVAILABLE:
            # Register event handlers with priorities
            self.register_handler("documents.create.*", self.handle_create_event, priority=EventPriority.HIGH)
            self.register_handler("documents.version_control.*", self.handle_version_control_event, priority=EventPriority.HIGH)
            self.register_handler("documents.approval.*", self.handle_approval_event, priority=EventPriority.NORMAL)
            self.register_handler("documents.distribution.*", self.handle_distribution_event, priority=EventPriority.NORMAL)

            logger.info(" Documents Service event handlers registered")

    async def handle_create_event(self, event):
        """Handle documents.create events"""
        logger.info(f"Handling documents.create event: {event.type}")
        # TODO: Implement actual create handling
        return {"status": "processed", "event_type": event.type}
    async def handle_version_control_event(self, event):
        """Handle documents.version_control events"""
        logger.info(f"Handling documents.version_control event: {event.type}")
        # TODO: Implement actual version_control handling
        return {"status": "processed", "event_type": event.type}
    async def handle_approval_event(self, event):
        """Handle documents.approval events"""
        logger.info(f"Handling documents.approval event: {event.type}")
        # TODO: Implement actual approval handling
        return {"status": "processed", "event_type": event.type}
    async def handle_distribution_event(self, event):
        """Handle documents.distribution events"""
        logger.info(f"Handling documents.distribution event: {event.type}")
        # TODO: Implement actual distribution handling
        return {"status": "processed", "event_type": event.type}

    async def handle_completion_event(self, event):
        """Handle completion events (triggers next steps)"""
        logger.info(f"Documents Service completion event: {event.type}")

        # If platform available, can trigger saga
        if platform and platform.saga_orchestrator:
            logger.info("  → Considering saga orchestration for next steps")
            # TODO: Trigger appropriate saga

        return {"status": "completion_processed"}


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
    global platform, service_self_aware, workflow_storage, workflow_engine
    global audit_logger, iso_checker, security_middleware

    # === STARTUP ===
    logger.info("=" * 60)
    logger.info(" Starting Documents Service (Integrated with Graceful Choreography)")
    logger.info("=" * 60)
    logger.info(f" Port: 8090")
    logger.info(f" ISO 22301 Clause: 7.5")

    try:
        # === 1. Initialize Platform Integration ===
        logger.info("\n1️⃣  Initializing Platform Integration...")
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

        platform = await init_platform(
            database_url=settings.DATABASE_URL,
            redis_url=redis_url,
            enable_intelligent_routing=True,
            enable_saga_engine=True,
            enable_self_aware=True,
            enable_cqrs=False
        )

        platform_status = platform.get_status()
        logger.info(f"   Platform Status: {platform_status}")

        # === 2. Initialize Database ===
        logger.info("\n2️⃣  Initializing Database...")
        await init_db()
        logger.info(f"    Database initialized")

        # === 3. Initialize Self-Aware Service ===
        if SELF_AWARE_AVAILABLE:
            logger.info("\n3️⃣  Initializing Self-Aware Service...")
            service_self_aware = DocumentsServiceSelfAware()
            await service_self_aware.initialize()

            # Subscribe to events via platform EventBus
            if platform.intelligent_router:
                logger.info("    Registering with Intelligent EventBus...")
                # Register service capabilities with router
                await platform.intelligent_router.register_subscriber(
                    subscriber_id="documents_service",
                    event_pattern="documents.*",
                    handler=service_self_aware.on_event,
                    capabilities={
                        "domains": ["documents", "bcm"],
                        "max_concurrent": 10,
                        "avg_processing_time_ms": 500,
                        "sla_ms": 3000,
                        "semantic_tags": ["documents", "version", "approval", "distribution"]
                    }
                )
                logger.info("    Self-Aware Service registered with Intelligent Router")
            elif platform.eventbus:
                logger.info("    Registering with Basic EventBus...")
                await platform.eventbus.subscribe("documents.*", service_self_aware.on_event)
                logger.info("    Self-Aware Service registered with EventBus")
        else:
            logger.warning("\n3️⃣  ️  Self-Aware Services not available (basic mode)")

        # === 4. Initialize Workflow Intelligence ===
        logger.info("\n4️⃣  Initializing Workflow Intelligence...")
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="documents",
            storage_adapter=workflow_storage
        )

        audit_logger = AuditLogger(storage_adapter=workflow_storage)
        await audit_logger.ensure_schema()

        iso_checker = ISO22301Checker()

        jwt_secret = getattr(settings, 'JWT_SECRET_KEY', None) or "dev-secret-key-change-in-production"
        security_middleware = WorkflowSecurityMiddleware(
            audit_logger=audit_logger,
            iso_checker=iso_checker,
            jwt_secret=jwt_secret
        )

        # Set health metrics
        workflow_metrics.set_health("workflow_intelligence", True)
        workflow_metrics.set_health("database", True)
        workflow_metrics.set_health("audit_logging", True)
        workflow_metrics.set_health("iso_compliance", True)

        logger.info("    Workflow Intelligence initialized")

        # === 5. Register Sagas (if saga engine available) ===
        if platform.saga_orchestrator:
            logger.info("\n5️⃣  Registering Sagas...")
            try:
                from intelligent_core.orchestration.saga_engine.example_sagas import (
                    create_bcm_program_saga,
                    create_incident_response_saga
                )

                platform.saga_orchestrator.register_saga(create_bcm_program_saga())
                platform.saga_orchestrator.register_saga(create_incident_response_saga())

                logger.info("    Sagas registered")
            except ImportError:
                logger.warning("   ️  Saga definitions not found")

        logger.info("\n" + "=" * 60)
        logger.info(" Documents Service ready (with Graceful Choreography)")
        logger.info("=" * 60)
        logger.info(f"    Docs: http://localhost:8090/docs")
        logger.info(f"    Metrics: http://localhost:8090/metrics")
        logger.info(f"   ️  Health: http://localhost:8090/health")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        logger.error(f" Failed to start Documents Service: {e}", exc_info=True)
        raise

    yield  # Application running

    # === SHUTDOWN ===
    logger.info("\n" + "=" * 60)
    logger.info(" Shutting down Documents Service...")
    logger.info("=" * 60)

    if workflow_storage:
        await workflow_storage.close()
        logger.info("    Workflow storage closed")

    await close_db()
    logger.info("    Database closed")

    await shutdown_platform()
    logger.info("    Platform integration shutdown")

    logger.info("=" * 60)
    logger.info(" Documents Service shutdown complete")
    logger.info("=" * 60)


# Create FastAPI app with enhanced lifespan
app = FastAPI(
    title=getattr(settings, 'SERVICE_NAME', 'Documents Service'),
    description=f"""
    Document Management - ISO 22301 Clause 7.5

    **Enhanced with Graceful Choreography:**
    - Intelligent EventBus
    - Saga Pattern
    - Self-Aware capabilities
    - CQRS (optional)
    """,
    version=getattr(settings, 'SERVICE_VERSION', '1.0.0'),
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(service_router)
app.include_router(workflow_ai_router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# === ENHANCED HEALTH CHECK ===
@app.get("/health")
async def health_check():
    """Enhanced health check with platform status"""
    health = {
        "status": "healthy",
        "service": "documents_service",
        "version": getattr(settings, 'SERVICE_VERSION', '1.0.0'),
        "iso_clause": "7.5"
    }

    if platform:
        health["platform"] = platform.get_status()

    if service_self_aware and SELF_AWARE_AVAILABLE:
        health_status = await service_self_aware.health_monitor.check_health()
        health["self_aware"] = {
            "status": health_status.status.value,
            "load": await service_self_aware.load_manager.get_load_percentage()
        }

    return health


# === PLATFORM STATUS ENDPOINT ===
@app.get("/api/platform/status")
async def get_platform_status():
    """Get detailed platform integration status"""
    if not platform:
        return {"error": "Platform not initialized"}

    status = platform.get_status()

    if platform.intelligent_router:
        status["intelligent_router"] = platform.intelligent_router.get_metrics()

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
        port=8090,
        reload=True,
        log_level="info"
    )
