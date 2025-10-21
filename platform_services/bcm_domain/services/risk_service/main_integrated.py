"""
Risk Service - Integrated with Graceful Choreography
====================================================

Enhanced Risk Service with:
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
from api.routes import router as risk_router
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
risk_self_aware_service = None
workflow_storage = None
workflow_engine = None
audit_logger = None
iso_checker = None
security_middleware = None


class RiskSelfAwareService(SelfAwareService if SELF_AWARE_AVAILABLE else object):
    """
    Risk Service with Self-Aware capabilities

    Provides intelligent event handling with:
    - Automatic capability matching
    - Load-aware processing
    - Graceful degradation
    - Service collaboration
    """

    def __init__(self):
        if SELF_AWARE_AVAILABLE:
            super().__init__(
                service_name="risk_service",
                capabilities=[
                    "risk.assessment",
                    "risk.analysis",
                    "risk.fair",
                    "risk.monte_carlo",
                    "risk.treatment",
                    "risk.reporting",
                ]
            )
            logger.info(" Risk Service initialized as Self-Aware")
        else:
            logger.warning("️  Risk Service running in basic mode (Self-Aware not available)")

    async def initialize(self):
        """Initialize Risk-specific capabilities"""
        if SELF_AWARE_AVAILABLE:
            # Register event handlers with priorities
            self.register_handler("risk.assessment.*", self.handle_assessment_event, priority=EventPriority.HIGH)
            self.register_handler("risk.analysis.*", self.handle_analysis_event, priority=EventPriority.HIGH)
            self.register_handler("risk.treatment.*", self.handle_treatment_event, priority=EventPriority.NORMAL)
            self.register_handler("risk.*.completed", self.handle_completion_event, priority=EventPriority.NORMAL)

            logger.info(" Risk event handlers registered")

    async def handle_assessment_event(self, event):
        """Handle risk assessment events"""
        logger.info(f"Handling risk assessment event: {event.type}")
        # TODO: Implement actual risk assessment handling
        return {"status": "processed", "event_type": event.type}

    async def handle_analysis_event(self, event):
        """Handle risk analysis events (FAIR, Monte Carlo)"""
        logger.info(f"Handling risk analysis event: {event.type}")
        # TODO: Implement actual analysis handling
        return {"status": "processed", "event_type": event.type}

    async def handle_treatment_event(self, event):
        """Handle risk treatment events"""
        logger.info(f"Handling risk treatment event: {event.type}")
        # TODO: Implement actual treatment handling
        return {"status": "processed", "event_type": event.type}

    async def handle_completion_event(self, event):
        """Handle completion events (triggers next steps)"""
        logger.info(f"Risk completion event: {event.type}")

        # If platform available, can trigger saga
        if platform and platform.saga_orchestrator:
            logger.info("  → Considering saga orchestration for next steps")
            # TODO: Trigger appropriate saga (e.g., risk mitigation workflow)

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
    global platform, risk_self_aware_service, workflow_storage, workflow_engine
    global audit_logger, iso_checker, security_middleware

    # === STARTUP ===
    logger.info("=" * 60)
    logger.info(" Starting Risk Service (Integrated with Graceful Choreography)")
    logger.info("=" * 60)
    logger.info(f" Port: {settings.PORT}")
    logger.info(f" ISO 22301 Clause: 8.2.3 - Risk Assessment")

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
            risk_self_aware_service = RiskSelfAwareService()
            await risk_self_aware_service.initialize()

            # Subscribe to events via platform EventBus
            if platform.intelligent_router:
                logger.info("    Registering with Intelligent EventBus...")
                # Register service capabilities with router
                await platform.intelligent_router.register_subscriber(
                    subscriber_id="risk_service",
                    event_pattern="risk.*",
                    handler=risk_self_aware_service.on_event,
                    capabilities={
                        "domains": ["risk", "risk_assessment", "compliance"],
                        "max_concurrent": 10,
                        "avg_processing_time_ms": 600,
                        "sla_ms": 3000,
                        "semantic_tags": ["risk", "assessment", "fair", "monte_carlo", "treatment"]
                    }
                )
                logger.info("    Self-Aware Service registered with Intelligent Router")
            elif platform.eventbus:
                logger.info("    Registering with Basic EventBus...")
                await platform.eventbus.subscribe("risk.*", risk_self_aware_service.on_event)
                logger.info("    Self-Aware Service registered with EventBus")
        else:
            logger.warning("\n3️⃣  ️  Self-Aware Services not available (basic mode)")

        # === 4. Initialize Workflow Intelligence ===
        logger.info("\n4️⃣  Initializing Workflow Intelligence...")
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="risk",
            storage_adapter=workflow_storage
        )

        audit_logger = AuditLogger(storage_adapter=workflow_storage)
        await audit_logger.ensure_schema()

        iso_checker = ISO22301Checker()

        jwt_secret = settings.JWT_SECRET_KEY if settings.JWT_SECRET_KEY else "dev-secret-key-change-in-production"
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

        # === 5. Register Risk Sagas (if saga engine available) ===
        if platform.saga_orchestrator:
            logger.info("\n5️⃣  Registering Risk Sagas...")
            # Import saga definitions
            try:
                from intelligent_core.orchestration.saga_engine.example_sagas import (
                    create_bcm_program_saga,
                    create_incident_response_saga
                )

                # Register sagas
                platform.saga_orchestrator.register_saga(create_bcm_program_saga())
                platform.saga_orchestrator.register_saga(create_incident_response_saga())

                logger.info("    Risk Sagas registered")
            except ImportError:
                logger.warning("   ️  Saga definitions not found")

        logger.info("\n" + "=" * 60)
        logger.info(" Risk Service ready (with Graceful Choreography)")
        logger.info("=" * 60)
        logger.info(f"    Docs: http://localhost:{settings.PORT}/docs")
        logger.info(f"    Metrics: http://localhost:{settings.PORT}/metrics")
        logger.info(f"   ️  Health: http://localhost:{settings.PORT}/health")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        logger.error(f" Failed to start Risk Service: {e}", exc_info=True)
        raise

    yield  # Application running

    # === SHUTDOWN ===
    logger.info("\n" + "=" * 60)
    logger.info(" Shutting down Risk Service...")
    logger.info("=" * 60)

    # Close workflow storage
    if workflow_storage:
        await workflow_storage.close()
        logger.info("    Workflow storage closed")

    # Close database
    await close_db()
    logger.info("    Database closed")

    # Shutdown platform
    await shutdown_platform()
    logger.info("    Platform integration shutdown")

    logger.info("=" * 60)
    logger.info(" Risk Service shutdown complete")
    logger.info("=" * 60)


# Create FastAPI app with enhanced lifespan
app = FastAPI(
    title=settings.SERVICE_NAME,
    description=f"""
    Risk Management Capability - ISO 22301:2019 Clause 8.2.3

    **Enhanced with Graceful Choreography:**
    - Intelligent EventBus
    - Saga Pattern
    - Self-Aware capabilities
    - CQRS (optional)

    **Features:**
    - Risk Assessment (Likelihood × Impact)
    - FAIR Quantitative Analysis
    - Monte Carlo Simulation
    - Risk Treatment Plans
    - Risk Heat Maps & Reports
    """,
    version=settings.SERVICE_VERSION,
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
app.include_router(risk_router)
app.include_router(workflow_ai_router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# === ENHANCED HEALTH CHECK ===
@app.get("/health")
async def health_check():
    """
    Enhanced health check with platform status
    """
    health = {
        "status": "healthy",
        "service": "risk_service",
        "version": settings.SERVICE_VERSION,
        "iso_clause": "8.2.3"
    }

    # Add platform status
    if platform:
        health["platform"] = platform.get_status()

    # Add self-aware status
    if risk_self_aware_service and SELF_AWARE_AVAILABLE:
        health_status = await risk_self_aware_service.health_monitor.check_health()
        health["self_aware"] = {
            "status": health_status.status.value,
            "load": await risk_self_aware_service.load_manager.get_load_percentage()
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
        status["intelligent_router"] = platform.intelligent_router.get_metrics()

    if platform.saga_orchestrator:
        status["saga_engine"] = {
            "registered_sagas": list(platform.saga_orchestrator._sagas.keys())
        }

    return status


# === COMPLIANCE CHECK ENDPOINT ===
@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.2.3 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {"data": {}}

    result = await check_compliance(sample_context, iso_checker, "8.2.3")

    return {
        "iso_clause": "8.2.3",
        "module": "risk",
        "compliance_status": result
    }


# === ROOT ENDPOINT ===
@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": settings.SERVICE_NAME,
        "description": "Risk Management Capability for BCM Platform (Enhanced with Graceful Choreography)",
        "version": settings.SERVICE_VERSION,
        "iso_compliance": "ISO 22301:2019 Clause 8.2.3",
        "capabilities": {
            "risk_assessment": "5×5 Risk Matrix (Likelihood × Impact)",
            "fair_analysis": "Factor Analysis of Information Risk (Quantitative)",
            "monte_carlo": "Monte Carlo Simulation (Probability Distribution)",
            "treatment_planning": "Risk Treatment & Mitigation Plans",
            "reporting": "Risk Heat Maps, Reports & Analytics"
        },
        "platform_integration": {
            "intelligent_eventbus": platform.intelligent_router is not None if platform else False,
            "saga_engine": platform.saga_orchestrator is not None if platform else False,
            "self_aware": SELF_AWARE_AVAILABLE
        },
        "endpoints": {
            "api": settings.API_PREFIX,
            "documentation": "/docs",
            "health": "/health",
            "platform_status": "/api/platform/status",
            "compliance": "/api/compliance/check"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_integrated:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
