"""
FastAPI Application

Main FastAPI application factory for Digital Twin service
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from storage import PostgreSQLStorage, RedisCache

logger = logging.getLogger(__name__)


# ============================================
# APPLICATION STATE
# ============================================

class AppState:
    """Application state container"""

    def __init__(self):
        self.storage: PostgreSQLStorage = None
        self.cache: RedisCache = None
        self.config: Dict[str, Any] = {}


# ============================================
# LIFESPAN MANAGEMENT
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Digital Twin API...")

    state: AppState = app.state.app_state

    try:
        # Initialize storage
        logger.info("Initializing PostgreSQL storage...")
        await state.storage.initialize()

        # Initialize cache
        logger.info("Initializing Redis cache...")
        await state.cache.initialize()

        # Health checks
        storage_healthy = await state.storage.health_check()
        cache_healthy = await state.cache.health_check()

        if not storage_healthy:
            logger.error("PostgreSQL health check failed!")
        if not cache_healthy:
            logger.error("Redis health check failed!")

        logger.info("Digital Twin API started successfully")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down Digital Twin API...")

        try:
            await state.cache.close()
        except Exception as e:
            logger.error(f"Error closing cache: {e}")

        try:
            await state.storage.close()
        except Exception as e:
            logger.error(f"Error closing storage: {e}")

        logger.info("Digital Twin API shut down")


# ============================================
# APPLICATION FACTORY
# ============================================

def create_app(config: Dict[str, Any] = None) -> FastAPI:
    """
    Create FastAPI application

    Args:
        config: Application configuration

    Returns:
        FastAPI application instance
    """
    config = config or {}

    # Create FastAPI app
    app = FastAPI(
        title="Digital Twin Universal Service",
        description="Universal Digital Twin API for BCM Platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Initialize app state
    state = AppState()
    state.config = config

    # Initialize storage and cache (will be connected in lifespan)
    pg_config = config.get('postgres', {
        'host': 'localhost',
        'port': 5432,
        'database': 'digital_twin',
        'username': 'postgres',
        'password': 'postgres'
    })

    redis_config = config.get('redis', {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'prefix': 'dt:'
    })

    state.storage = PostgreSQLStorage(pg_config)
    state.cache = RedisCache(redis_config)

    app.state.app_state = state

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get('cors_origins', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from .routers import (
        organizations, simulations, metrics, health, bridges,
        import_data, visualize, integrations, auth,
        scenarios, exercises, predictions, bia,  # Simulation Hub routers
        topology, system_clone, platform_bridges, data_collector  # NEW: System Clone & Integration routers
    )

    # Auth router (FIRST - no /api/v1 prefix, just /auth)
    app.include_router(
        auth.router,
        prefix="/api/v1",
        tags=["authentication"]
    )

    app.include_router(
        organizations.router,
        prefix="/api/v1/organizations",
        tags=["organizations"]
    )

    app.include_router(
        simulations.router,
        prefix="/api/v1/simulations",
        tags=["simulations"]
    )

    app.include_router(
        metrics.router,
        prefix="/api/v1/metrics",
        tags=["metrics"]
    )

    app.include_router(
        bridges.router,
        prefix="/api/v1/bridges",
        tags=["bridges"]
    )

    app.include_router(
        import_data.router,
        prefix="/api/v1/import",
        tags=["import"]
    )

    app.include_router(
        integrations.router,
        prefix="/api/v1",
        tags=["integrations"]
    )

    app.include_router(
        visualize.router,
        prefix="/api/v1/visualize",
        tags=["visualization"]
    )

    # Simulation Hub routers (NEW)
    app.include_router(
        scenarios.router,
        prefix="/api/v1/scenarios",
        tags=["simulation-hub", "scenarios"]
    )

    app.include_router(
        exercises.router,
        prefix="/api/v1/exercises",
        tags=["simulation-hub", "exercises"]
    )

    app.include_router(
        predictions.router,
        prefix="/api/v1/predictions",
        tags=["simulation-hub", "predictions"]
    )

    app.include_router(
        bia.router,
        prefix="/api/v1/bia",
        tags=["simulation-hub", "bia"]
    )

    app.include_router(
        health.router,
        prefix="/api/v1",
        tags=["health"]
    )

    # System Clone & Integration routers (NEW - Multi-tenant platform integration)
    app.include_router(
        topology.router,
        prefix="/api/v1/topology",
        tags=["system-clone", "topology"]
    )

    app.include_router(
        system_clone.router,
        prefix="/api/v1/system-clone",
        tags=["system-clone", "mirror"]
    )

    app.include_router(
        platform_bridges.router,
        prefix="/api/v1/platform-bridges",
        tags=["integrations", "bridges"]
    )

    app.include_router(
        data_collector.router,
        prefix="/api/v1/data-collection",
        tags=["data-collection", "organization"]
    )

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "Digital Twin Universal Service",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs"
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc)
            }
        )

    logger.info("FastAPI application created")

    return app


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(app: FastAPI) -> PostgreSQLStorage:
    """Get storage dependency"""
    return app.state.app_state.storage


def get_cache(app: FastAPI) -> RedisCache:
    """Get cache dependency"""
    return app.state.app_state.cache
