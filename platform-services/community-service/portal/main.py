"""
Portal Service - Main Application
Knowledge Hub + Scenario Marketplace + Client Dashboard

Port: 8031
"""

import sys
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge

from database.connection import init_db, close_db
from shared.eventbus import init_eventbus, get_eventbus
from api.knowledge import router as knowledge_router
from api.scenarios import router as scenarios_router
from api.forum import router as forum_router
from api.simulation_router import router as simulation_router
from api.execution_router import router as execution_router
from api.organizations import router as organizations_router
# from api.scenario_library_router import router as scenario_library_router


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Service-specific metrics
requests_total = Counter(
    'portal_service_requests_total',
    'Total requests',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'portal_service_request_duration_seconds',
    'Request duration',
    ['endpoint']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Portal Service starting...")
    await init_db()
    print("✅ Database initialized")

    # Initialize EventBus
    eventbus_url = os.getenv("EVENTBUS_URL", "http://localhost:8001")
    await init_eventbus(eventbus_url, service_name="portal-service")
    print(f"✅ EventBus initialized ({eventbus_url})")

    # Register event subscribers
    try:
        from events.subscribers import setup_subscriptions
        await setup_subscriptions()
        print("✅ Event subscribers registered")
    except Exception as e:
        print(f"⚠️  Failed to register event subscribers: {e}")
        # Don't fail startup if event subscriptions fail

    yield

    # Shutdown
    print("🛑 Portal Service shutting down...")

    # Close EventBus
    eventbus = get_eventbus()
    if eventbus:
        await eventbus.disconnect()
    print("✅ EventBus disconnected")

    await close_db()
    print("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Portal Service",
    description="BCM Platform - Knowledge Hub, Scenario Marketplace & Community Forum",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
app.include_router(knowledge_router)
app.include_router(scenarios_router)
app.include_router(forum_router)
app.include_router(organizations_router)
# Simulation routers
app.include_router(simulation_router, prefix="/api/portal/simulations", tags=["Simulations"])
app.include_router(execution_router, prefix="/api/portal/simulations", tags=["Simulation Execution"])
# app.include_router(scenario_library_router, prefix="/api/portal/scenario-library", tags=["Scenario Library"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "portal",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Portal Service",
        "description": "Knowledge Hub, Scenario Marketplace & Community Forum for BCM Platform",
        "version": "1.0.0",
        "endpoints": {
            "knowledge_hub": "/api/portal/knowledge",
            "scenario_marketplace": "/api/portal/scenarios",
            "forum": "/api/portal/forum",
            "documentation": "/docs",
            "health": "/health"
        }
    }


# ============================================================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8031 --reload
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8031")),
        reload=True if os.getenv("DEBUG") == "true" else False
    )
