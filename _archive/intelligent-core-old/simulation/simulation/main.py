"""
Simulation Service - Main Entry Point

Runs simulations: what-if analysis, Monte Carlo, scenarios, optimization

Port: 8031
"""

import sys
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared libs to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import init_db, create_tables
from cache.redis_client import init_redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simulation Service",
    description="Scenario simulation, what-if analysis, and predictive modeling",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Starting Simulation Service...")

    # Initialize database
    init_db()
    create_tables()

    # Initialize Redis
    init_redis()

    logger.info("✅ Simulation Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Simulation Service...")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "simulation",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Simulation Service",
        "version": "2.0.0",
        "description": "Scenario simulation, what-if analysis, and predictive modeling",
        "docs": "/docs"
    }


# Import routers
from api import simulation_router, scenario_router, execution_router, scenario_library_router

app.include_router(simulation_router.router, prefix="/api/simulation", tags=["Simulations"])
app.include_router(scenario_router.router, prefix="/api/simulation", tags=["Scenarios"])
app.include_router(execution_router.router, prefix="/api/simulation", tags=["Execution"])
app.include_router(scenario_library_router.router, prefix="/api/simulation", tags=["Scenario Library"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8031,
        reload=True,
        log_level="info"
    )
