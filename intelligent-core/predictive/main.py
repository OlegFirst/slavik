"""
Predictive Journey Service

Platform predicts what organizations need before they ask.

Port: 8031

Integrations:
- Supabase PostgreSQL (predictions storage)
- Case Library (workflow_intelligence)
- Notification Service (email digests)
- APScheduler (daily cron jobs)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Predictive Service starting...")

    # Initialize dependencies
    from .integration.dependencies import get_dependencies

    try:
        deps = await get_dependencies()
        app.state.deps = deps
        logger.info("✅ Dependencies initialized (Case Library, Notification Service, Database)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize dependencies: {e}")
        logger.warning("⚠️  Service will run with limited functionality")

    # Start scheduler for daily digests
    if os.getenv("ENABLE_DAILY_DIGESTS", "true").lower() == "true":
        try:
            from .scheduler.daily_digests import DailyDigestScheduler

            async def run_daily_digest_job():
                """Wrapper for daily digest job"""
                try:
                    if hasattr(app.state, 'deps'):
                        digest_scheduler = DailyDigestScheduler(app.state.deps)
                        await digest_scheduler.run_daily_digests()
                except Exception as e:
                    logger.error(f"Daily digest job error: {e}")

            # Schedule daily at 8 AM
            scheduler.add_job(
                run_daily_digest_job,
                CronTrigger(hour=8, minute=0),
                id='daily_proactive_digests',
                name='Daily Proactive Recommendations Digest',
                replace_existing=True
            )

            scheduler.start()
            logger.info("✅ Scheduler started: Daily digests at 8:00 AM")

        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")

    logger.info(f"✅ Predictive Service ready on port 8031")

    yield

    # Cleanup
    logger.info("👋 Predictive Service shutting down...")

    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Scheduler stopped")

    from .integration.dependencies import cleanup_dependencies
    await cleanup_dependencies()
    logger.info("✅ Dependencies cleaned up")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Predictive Journey Service",
    description="🔮 Magic predictions for BCM journeys",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .api import predictions

app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["predictions"]
)


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "predictive-journey",
        "version": "1.0.0",
        "magic_level": "🔮🔮🔮🔮🔮"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Predictive Journey Service",
        "tagline": "Platform predicts what you need before you ask",
        "version": "1.0.0",
        "endpoints": {
            "journey_prediction": "/api/v1/predictions/journey/{org_id}",
            "certification_timeline": "/api/v1/predictions/certification/{org_id}",
            "recommendations": "/api/v1/predictions/recommendations/{org_id}",
            "expert_demand": "/api/v1/predictions/expert-demand",
            "docs": "/docs"
        },
        "magic_features": [
            "90-day journey timeline",
            "Certification date prediction",
            "Proactive recommendations",
            "Expert demand forecasting",
            "Challenge prediction"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8031, reload=True)
