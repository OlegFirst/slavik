"""
🔍 Analytics Specialist AI - Main Service
==========================================

The 6th AI Colleague in AI Office - Platform Intelligence Expert.

**Responsibilities:**
- Analyze platform health (processes, metrics, dependencies)
- Detect bottlenecks, conflicts, and anomalies
- Generate insights and recommendations
- Report to MIO Manager for coordination
- Provide context to AI Orchestrator for decision-making

**Port:** 8051
**Competency Levels:** junior → middle → senior → expert
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .api import health_router, analysis_router, workflow_router
from .api.tools_ui_routes import ui_router
from .workflows import daily_health_check, continuous_improvement_scan
from .clients import MIOManagerClient

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

# Background task handles
background_tasks = []


async def schedule_daily_health_check():
    """
    Scheduled daily health check

    Runs every day at configured time (default: 09:00)
    """
    if not settings.DAILY_HEALTH_CHECK_ENABLED:
        logger.info("Daily health check is disabled")
        return

    logger.info(f"Scheduling daily health check for {settings.DAILY_HEALTH_CHECK_TIME}")

    while True:
        try:
            # Calculate time until next execution
            # For now, run every 24 hours (simplified)
            # TODO: Use proper cron scheduling

            logger.info("Executing daily health check...")
            result = await daily_health_check()

            logger.info(f"Daily health check result: {result.get('status')}")

            # Sleep 24 hours
            await asyncio.sleep(86400)  # 24 hours

        except Exception as e:
            logger.error(f"Daily health check error: {e}", exc_info=True)
            # Sleep and retry
            await asyncio.sleep(3600)  # 1 hour


async def schedule_continuous_improvement():
    """
    Scheduled continuous improvement scan

    Runs every hour (configurable)
    """
    if not settings.CONTINUOUS_IMPROVEMENT_ENABLED:
        logger.info("Continuous improvement is disabled")
        return

    interval = settings.CONTINUOUS_IMPROVEMENT_INTERVAL
    logger.info(f"Scheduling continuous improvement every {interval}s")

    while True:
        try:
            logger.info("Executing continuous improvement scan...")
            result = await continuous_improvement_scan()

            logger.info(f"Continuous improvement result: {result.get('status')}")

            # Sleep for configured interval
            await asyncio.sleep(interval)

        except Exception as e:
            logger.error(f"Continuous improvement error: {e}", exc_info=True)
            # Sleep and retry
            await asyncio.sleep(600)  # 10 minutes


async def send_heartbeat_to_mio():
    """
    Send periodic heartbeat to MIO Manager

    Let МиО know Analytics Specialist is alive.
    Runs every 5 minutes.
    """
    mio_client = MIOManagerClient()

    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes

            result = await mio_client.heartbeat()
            logger.debug(f"Heartbeat sent to MIO Manager: {result.get('status')}")

        except Exception as e:
            logger.warning(f"Heartbeat failed: {e}")


# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager

    Startup:
    - Initialize background tasks (health check, continuous improvement)
    - Send initial heartbeat to MIO Manager

    Shutdown:
    - Cancel background tasks
    - Send goodbye to MIO Manager
    """
    logger.info("=" * 70)
    logger.info("🔍 ANALYTICS SPECIALIST AI STARTING...")
    logger.info("=" * 70)
    logger.info(f"   Service: Analytics Specialist")
    logger.info(f"   Port: {settings.PORT}")
    logger.info(f"   Competency Level: {settings.COMPETENCY_LEVEL}")
    logger.info(f"   Tools: metrics_discovery, dependency_mapper")
    logger.info(f"   MIO Manager: {settings.MIO_MANAGER_URL}")
    logger.info(f"   Process Analytics: {settings.PROCESS_ANALYTICS_URL}")
    logger.info("=" * 70)

    # Start background tasks
    global background_tasks

    # Daily health check
    if settings.DAILY_HEALTH_CHECK_ENABLED:
        task1 = asyncio.create_task(schedule_daily_health_check())
        background_tasks.append(task1)
        logger.info("✅ Daily health check scheduled")

    # Continuous improvement
    if settings.CONTINUOUS_IMPROVEMENT_ENABLED:
        task2 = asyncio.create_task(schedule_continuous_improvement())
        background_tasks.append(task2)
        logger.info("✅ Continuous improvement scheduled")

    # Heartbeat to MIO
    task3 = asyncio.create_task(send_heartbeat_to_mio())
    background_tasks.append(task3)
    logger.info("✅ Heartbeat to MIO Manager started")

    logger.info("=" * 70)
    logger.info("🚀 ANALYTICS SPECIALIST AI READY!")
    logger.info("=" * 70)

    # Yield to application
    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info("🛑 ANALYTICS SPECIALIST AI SHUTTING DOWN...")
    logger.info("=" * 70)

    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    logger.info("✅ Background tasks stopped")
    logger.info("👋 Goodbye!")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Analytics Specialist AI",
    description=(
        "Platform Intelligence Expert - 6th AI Colleague in AI Office. "
        "Analyzes platform health, detects issues, and provides intelligent insights."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(workflow_router)
app.include_router(ui_router)  # Web UI for tools management


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - Service information

    Returns:
        Service metadata
    """
    return {
        "service": "analytics-specialist",
        "description": "Platform Intelligence Expert - AI Colleague #6",
        "version": "1.0.0",
        "competency_level": settings.COMPETENCY_LEVEL,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analytics/analyze",
            "insights": "/api/v1/analytics/insights",
            "status": "/api/v1/analytics/status",
            "daily_health_check": "/api/v1/workflows/daily-health-check",
            "investigate": "/api/v1/workflows/investigate-incident",
            "ui": "/ui",  # 🎨 Web UI for tools management
            "docs": "/docs"
        },
        "ai_office": {
            "colleague_number": 6,
            "reports_to": "MIO Manager (port 8046)",
            "coordinates_with": [
                "AI Event Manager (port 8050)",
                "Orchestrator",
                "Agent Router",
                "Project Agent"
            ]
        }
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    TODO: Implement prometheus_client metrics
    """
    return JSONResponse(
        content={
            "message": "Metrics endpoint - TODO: Implement prometheus_client",
            "note": "Will export service metrics for Prometheus"
        }
    )


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
