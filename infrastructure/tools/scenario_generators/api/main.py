"""
Scenario Orchestrator - REST API for Scenario Generators

REST API service for managing scenario generation across all levels.
Part of Infrastructure Tools, not AI Office.

Location: infrastructure/tools/scenario-generators/api/
Role: Provides HTTP API interface for Generation Manager
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.generation_routes import router as generation_router
from api.monitoring_routes import router as monitoring_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("="*70)
    logger.info("SCENARIO ORCHESTRATOR - REST API")
    logger.info("="*70)
    logger.info("Location: infrastructure/tools/scenario-generators/api/")
    logger.info(f"Port: {os.getenv('PORT', 8060)}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # TODO: Initialize Generation Manager
    # TODO: Initialize EventBus connection (optional)

    logger.info(" Scenario Orchestrator API ready")
    logger.info("="*70)

    yield

    # Shutdown
    logger.info("Shutting down Scenario Orchestrator...")
    # TODO: Cleanup resources


# Create FastAPI app
app = FastAPI(
    title="Scenario Orchestrator API",
    description="REST API for scenario generation tools (Infrastructure Tool)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generation_router)
app.include_router(monitoring_router)


@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "scenario-orchestrator",
        "version": "1.0.0",
        "location": "infrastructure/tools/scenario-generators/api",
        "type": "infrastructure_tool",
        "description": "REST API for scenario generation",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "api": "/api/v1"
        }
    }


@app.get("/info")
async def service_info():
    """
    Detailed service information.
    """
    return {
        "service": {
            "name": "scenario-orchestrator",
            "version": "1.0.0",
            "port": int(os.getenv("PORT", 8060)),
            "location": "infrastructure/tools/scenario-generators/api",
            "type": "infrastructure_tool"
        },
        "capabilities": {
            "generation_levels": ["l1_platform", "l1_applications", "l2", "l3", "l4"],
            "async_generation": True,
            "progress_tracking": True
        },
        "dependencies": {
            "intelligent_core": "templates, storage (required)",
            "generators": "L1, L2, L3, L4 (required)",
            "generation_manager": "orchestration (required)"
        },
        "endpoints": {
            "start_generation": "POST /api/v1/generate/start",
            "get_progress": "GET /api/v1/generate/progress/{job_id}",
            "get_status": "GET /api/v1/generate/status",
            "stop_generation": "POST /api/v1/generate/stop",
            "health": "GET /health",
            "metrics": "GET /metrics",
            "statistics": "GET /api/v1/statistics"
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8060))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Development mode
        log_level="info"
    )
