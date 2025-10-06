"""
Community Intelligence Service

Transforms passive case collection into active community-driven knowledge creation.

Port: 8030
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .api import contributions, reviews, reputation, cases
from .events.subscribers import setup_event_subscribers
from shared.database import get_db
from shared.eventbus import get_eventbus_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Community Intelligence Service starting...")

    # Setup event subscribers
    try:
        eventbus = get_eventbus_client()
        await setup_event_subscribers(eventbus)
        logger.info("✅ EventBus subscribers registered")
    except Exception as e:
        logger.error(f"❌ Failed to setup event subscribers: {e}")

    logger.info(f"✅ Community Intelligence Service ready on port {settings.PORT}")

    yield

    # Cleanup
    logger.info("👋 Community Intelligence Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Community Intelligence Service",
    description="Community-driven knowledge creation through peer review and reputation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .api import routes

# Unified API router (includes all endpoints)
app.include_router(
    routes.router,
    tags=["community"]
)

# Individual module routers (for backwards compatibility)
app.include_router(
    contributions.router,
    prefix="/api/v1/community/contributions",
    tags=["contributions"]
)

app.include_router(
    reviews.router,
    prefix="/api/v1/community/reviews",
    tags=["peer-reviews"]
)

app.include_router(
    reputation.router,
    prefix="/api/v1/community/reputation",
    tags=["reputation"]
)

app.include_router(
    cases.router,
    prefix="/api/v1/community/cases",
    tags=["case-library"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "community-intelligence",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Community Intelligence Service",
        "version": "1.0.0",
        "description": "Community-driven knowledge creation through peer review",
        "endpoints": {
            "contributions": "/api/v1/community/contributions",
            "reviews": "/api/v1/community/reviews",
            "reputation": "/api/v1/community/reputation",
            "leaderboard": "/api/v1/community/reputation/leaderboard",
            "annotations": "/api/v1/community/annotations",
            "guidance": "/api/v1/community/guidance/{clause_id}",
            "timeline": "/api/v1/community/timeline/predict",
            "next_steps": "/api/v1/community/timeline/{org_id}/next-steps",
            "search": "/api/v1/community/clauses/search",
            "demand_forecast": "/api/v1/community/marketplace/demand-forecast",
            "stats": "/api/v1/community/stats/community",
            "cases": "/api/v1/community/cases",
            "docs": "/docs",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
