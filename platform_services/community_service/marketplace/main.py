"""
Marketplace Service - Main Application
Professional Marketplace для BCM консультантов

Port: 8032
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
import logging

from database.connection import init_db, close_db
from shared.eventbus import init_eventbus, get_eventbus
from integrations.portal_client import portal_client
from api import specialists, projects, proposals, reviews

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Service-specific metrics
requests_total = Counter(
    'marketplace_service_requests_total',
    'Total requests',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'marketplace_service_request_duration_seconds',
    'Request duration',
    ['endpoint']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Marketplace Service starting...")
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize EventBus
    eventbus_url = os.getenv('EVENTBUS_URL', 'http://localhost:8001')
    await init_eventbus(eventbus_url, service_name="marketplace-service")
    logger.info(f"✅ EventBus initialized ({eventbus_url})")

    # Register event subscribers
    try:
        from events.subscribers import setup_subscriptions
        await setup_subscriptions()
        logger.info("✅ Event subscribers registered")
    except Exception as e:
        logger.warning(f"⚠️  Failed to register event subscribers: {e}")
        # Don't fail startup if event subscriptions fail

    # Log integration endpoints
    logger.info(f"📡 Portal URL: {os.getenv('PORTAL_URL', 'http://localhost:8031')}")

    yield

    # Shutdown
    logger.info("🛑 Marketplace Service shutting down...")

    # Close EventBus
    eventbus = get_eventbus()
    if eventbus:
        await eventbus.disconnect()
    logger.info("✅ EventBus disconnected")

    await close_db()
    await portal_client.close()
    logger.info("✅ All connections closed")


# Create FastAPI app
app = FastAPI(
    title="Marketplace Service",
    description="BCM Platform - Professional Marketplace (Uber for BCM Consultants)",
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
app.include_router(specialists.router)
app.include_router(projects.router)
app.include_router(proposals.router)
app.include_router(reviews.router)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

logger.info("✅ All API routers registered")
logger.info("   - Specialists: /api/marketplace/specialists")
logger.info("   - Projects: /api/marketplace/projects")
logger.info("   - Proposals: /api/marketplace/proposals")
logger.info("   - Reviews: /api/marketplace/reviews")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "marketplace",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Marketplace Service",
        "description": "Professional Marketplace для BCM консультантов",
        "version": "1.0.0",
        "based_on": "BCM_1 Odoo modules",
        "endpoints": {
            "specialists": "/api/marketplace/specialists",
            "projects": "/api/marketplace/projects",
            "proposals": "/api/marketplace/proposals",
            "reviews": "/api/marketplace/reviews",
            "documentation": "/docs",
            "health": "/health"
        },
        "integrations": {
            "portal": {
                "url": os.getenv("PORTAL_URL", "http://localhost:8031"),
                "features": [
                    "Knowledge article recommendations",
                    "BCM scenario linking",
                    "Forum integration",
                    "Community reputation display"
                ]
            },
            "eventbus": {
                "url": os.getenv("EVENTBUS_URL", "http://localhost:8001"),
                "events": 11
            },
            "clients": {
                "url": os.getenv("CLIENTS_SERVICE_URL", "http://localhost:8030"),
                "features": ["Authentication", "User profiles"]
            }
        },
        "status": "development"
    }


# ============================================================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8032 --reload
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8032")),
        reload=True if os.getenv("DEBUG") == "true" else False
    )
