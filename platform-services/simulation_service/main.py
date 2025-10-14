"""
Simulation & Modeling Service - Main Application

FastAPI application with full platform integration.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import get_settings, Settings
from storage.database import DatabaseManager, get_db_session
from integration.eventbus_client import SimulationEventBusClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
db_manager: DatabaseManager = None
eventbus_client: SimulationEventBusClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager

    Handles startup and shutdown events
    """
    global db_manager, eventbus_client

    settings = get_settings()
    logger.info("=" * 80)
    logger.info(f"Starting Simulation Service")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Port: {settings.port}")
    logger.info("=" * 80)

    # ========================================================================
    # STARTUP
    # ========================================================================

    try:
        # 1. Initialize Database
        logger.info("Initializing database...")
        db_manager = DatabaseManager(settings)
        await db_manager.init_db()

        health = await db_manager.health_check()
        if health["postgres"]:
            logger.info("✅ PostgreSQL connected")
        else:
            logger.error("❌ PostgreSQL connection failed")
            raise Exception("PostgreSQL connection failed")

        if health["redis"]:
            logger.info("✅ Redis connected")
        else:
            logger.warning("⚠️  Redis not available (caching disabled)")

        # 2. Initialize EventBus
        logger.info("Initializing EventBus...")
        eventbus_client = SimulationEventBusClient(settings)
        await eventbus_client.connect()

        eventbus_health = await eventbus_client.health_check()
        if eventbus_health.get("connected"):
            logger.info("✅ EventBus connected")
        else:
            logger.warning("⚠️  EventBus not available")

        logger.info("=" * 80)
        logger.info("🚀 Simulation Service started successfully!")
        logger.info(f"📚 API Documentation: http://localhost:{settings.port}/docs")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

    yield

    # ========================================================================
    # SHUTDOWN
    # ========================================================================

    logger.info("Shutting down Simulation Service...")

    try:
        if eventbus_client:
            await eventbus_client.disconnect()
            logger.info("✅ EventBus disconnected")

        if db_manager:
            await db_manager.close()
            logger.info("✅ Database connections closed")

        logger.info("👋 Simulation Service shut down gracefully")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ============================================================================
# CREATE APP
# ============================================================================

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    settings = get_settings()

    app = FastAPI(
        title="Simulation & Modeling Service",
        description="BCM simulation service with AI-powered scenario generation and multi-engine support",
        version="1.0.0",
        docs_url="/docs" if settings.enable_api_docs else None,
        redoc_url="/redoc" if settings.enable_api_docs else None,
        lifespan=lifespan
    )

    # ========================================================================
    # MIDDLEWARE
    # ========================================================================

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # ========================================================================
    # ROUTES
    # ========================================================================

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "simulation-service",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint

        Checks:
        - Database connection (PostgreSQL + Redis)
        - EventBus connection
        """
        health_status = {
            "service": "simulation-service",
            "status": "healthy",
            "database": {},
            "eventbus": {},
            "version": "1.0.0"
        }

        try:
            # Check database
            if db_manager:
                db_health = await db_manager.health_check()
                health_status["database"] = db_health

                if not db_health.get("postgres"):
                    health_status["status"] = "unhealthy"

            # Check EventBus
            if eventbus_client:
                eventbus_health = await eventbus_client.health_check()
                health_status["eventbus"] = eventbus_health

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)

    @app.get("/health/live")
    async def liveness():
        """Kubernetes liveness probe"""
        return {"status": "alive"}

    @app.get("/health/ready")
    async def readiness():
        """Kubernetes readiness probe"""
        try:
            # Check critical dependencies
            if db_manager:
                db_health = await db_manager.health_check()
                if not db_health.get("postgres"):
                    return JSONResponse(
                        content={"status": "not_ready", "reason": "database"},
                        status_code=503
                    )

            return {"status": "ready"}

        except Exception as e:
            return JSONResponse(
                content={"status": "not_ready", "error": str(e)},
                status_code=503
            )

    @app.get("/info")
    async def service_info():
        """Service information"""
        settings = get_settings()

        return {
            "service": "simulation-service",
            "version": "1.0.0",
            "environment": settings.environment,
            "features": {
                "eventbus": settings.eventbus_enabled,
                "orchestrator": settings.ai_orchestrator_enabled,
                "workflow": settings.workflow_intelligence_enabled,
                "knowledge": settings.knowledge_center_enabled,
                "community": settings.community_intelligence_enabled,
                "predictive": settings.predictive_journey_enabled,
                "digital_twin": settings.digital_twin_enabled,
            },
            "engines": {
                "jaamsim": settings.jaamsim_enabled,
                "simpy": settings.simpy_enabled,
            },
            "integrations": {
                "eventbus_url": settings.eventbus_url,
                "orchestrator_url": settings.ai_orchestrator_url,
                "workflow_url": settings.workflow_intelligence_url,
            }
        }

    # ========================================================================
    # API ROUTERS
    # ========================================================================

    from api import bridge_router, scenario_advanced_router

    # Bridge Router - Integration orchestration
    app.include_router(
        bridge_router,
        tags=["Bridge Integration"]
    )

    # Scenario Advanced Router - AI-powered scenario operations
    app.include_router(
        scenario_advanced_router,
        tags=["Scenarios Advanced"]
    )

    return app


# ============================================================================
# CREATE APP INSTANCE
# ============================================================================

app = create_app()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
