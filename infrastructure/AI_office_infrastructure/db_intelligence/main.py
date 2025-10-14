"""
Database Intelligence Service - Main Entry Point

Standalone service that can be run as:
1. Standalone FastAPI application
2. Integrated with AI Orchestrator

Usage:
    # Standalone
    python main.py

    # With uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8050

Environment Variables:
    DB_INTELLIGENCE_PORT: Port to run on (default: 8051)
    DB_INTELLIGENCE_HOST: Host to bind to (default: 0.0.0.0)
    ORCHESTRATOR_URL: URL of AI Orchestrator for registration
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add current directory to path for imports (CRITICAL for relative imports)
sys.path.insert(0, str(Path(__file__).parent))

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add parent path for EventBusHelper
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastAPI app
from api import app

# Import service
from db_intelligence_service import (
    start_db_intelligence,
    stop_db_intelligence
)

# Import EventBus Helper
try:
    from _shared.eventbus_helper import EventBusHelper
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logger.warning("EventBus Helper not available")

# Global EventBus helper
eventbus_helper = None


# =============================================================================
# ORCHESTRATOR INTEGRATION
# =============================================================================

async def register_with_orchestrator():
    """
    Register this service with AI Orchestrator

    Sends service metadata and capabilities to orchestrator
    """
    orchestrator_url = os.getenv("ORCHESTRATOR_URL")

    if not orchestrator_url:
        logger.info("ORCHESTRATOR_URL not set, skipping registration")
        return

    try:
        import httpx

        service_info = {
            "service_name": "db-intelligence",
            "service_type": "infrastructure",
            "version": "1.0.0",
            "host": os.getenv("DB_INTELLIGENCE_HOST", "0.0.0.0"),
            "port": int(os.getenv("DB_INTELLIGENCE_PORT", 8051)),
            "capabilities": [
                "query_monitoring",
                "performance_analysis",
                "optimization_suggestions",
                "health_monitoring",
                "table_statistics"
            ],
            "endpoints": {
                "health": "/health",
                "metrics": "/metrics",
                "prometheus": "/metrics/prometheus"
            },
            "metadata": {
                "description": "AI-powered database monitoring and optimization",
                "managed_by": "ai-orchestrator",
                "critical": True
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{orchestrator_url}/services/register",
                json=service_info,
                timeout=10.0
            )

            if response.status_code == 200:
                logger.info(f"✅ Registered with orchestrator at {orchestrator_url}")
            else:
                logger.warning(f"⚠️  Registration failed: {response.status_code}")

    except Exception as e:
        logger.error(f"Failed to register with orchestrator: {e}")


async def send_heartbeat():
    """
    Send periodic heartbeat to orchestrator

    Keeps the orchestrator informed that this service is alive
    """
    orchestrator_url = os.getenv("ORCHESTRATOR_URL")

    if not orchestrator_url:
        return

    while True:
        try:
            import httpx
            from infrastructure.database.intelligence.db_intelligence_service import get_db_intelligence

            service = get_db_intelligence()
            health = await service.get_health()

            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{orchestrator_url}/services/db-intelligence/heartbeat",
                    json={
                        "status": health["status"],
                        "timestamp": health["timestamp"].isoformat()
                    },
                    timeout=5.0
                )

            await asyncio.sleep(30)  # Every 30 seconds

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")
            await asyncio.sleep(30)


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup():
    """Extended startup with orchestrator integration and EventBus"""
    global eventbus_helper

    logger.info("🧠 Database Intelligence Service starting...")

    # Start the intelligence service
    await start_db_intelligence()

    # Initialize EventBus Helper
    if EVENTBUS_AVAILABLE:
        try:
            port = int(os.getenv("DB_INTELLIGENCE_PORT", 8051))
            eventbus_helper = EventBusHelper(
                service_name="db-intelligence",
                port=port,
                orchestrator="ai-office",
                capabilities=[
                    "query_monitoring",
                    "performance_analysis",
                    "optimization_suggestions",
                    "health_monitoring",
                    "table_statistics"
                ],
                dependencies=["eventbus", "postgres", "supabase"],
                service_type="specialist"
            )
            await eventbus_helper.startup()
            logger.info("   ✅ EventBus integration initialized")
        except Exception as e:
            logger.error(f"   ❌ EventBus initialization failed: {e}")
            logger.warning("   ⚠️  Running without EventBus integration")

    # Register with orchestrator
    await register_with_orchestrator()

    # Start heartbeat task
    asyncio.create_task(send_heartbeat())

    logger.info("✅ Database Intelligence Service ready")
    logger.info(f"   API: http://{os.getenv('DB_INTELLIGENCE_HOST', '0.0.0.0')}:{os.getenv('DB_INTELLIGENCE_PORT', 8051)}")
    logger.info(f"   Docs: http://{os.getenv('DB_INTELLIGENCE_HOST', '0.0.0.0')}:{os.getenv('DB_INTELLIGENCE_PORT', 8051)}/docs")


@app.on_event("shutdown")
async def shutdown():
    """Extended shutdown with EventBus cleanup"""
    global eventbus_helper

    logger.info("🛑 Database Intelligence Service shutting down...")

    # Shutdown EventBus
    if eventbus_helper:
        await eventbus_helper.shutdown()

    await stop_db_intelligence()
    logger.info("✅ Shutdown complete")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("DB_INTELLIGENCE_PORT", 8051))
    host = os.getenv("DB_INTELLIGENCE_HOST", "0.0.0.0")

    logger.info(f"Starting Database Intelligence Service on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
