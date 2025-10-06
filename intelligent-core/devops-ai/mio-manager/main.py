#!/usr/bin/env python3
"""
AI MIO Manager - Intelligent Monitoring & Observability Manager
Port: 8046

Управляющий центр платформы:
- Запускает Automation Toolkit для анализа
- Управляет API Gateway
- Формирует задачи для исправлений
- Отчитывается в систему мониторинга
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from config import settings
from integrations.automation_toolkit import AutomationToolkitManager
from integrations.orchestrator_client import OrchestratorClient
from integrations.gateway_manager import GatewayManager
from scheduler.automation_jobs import start_scheduler, stop_scheduler
from api import routes
from database import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
toolkit_manager = None
orchestrator_client = None
gateway_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    global toolkit_manager, orchestrator_client, gateway_manager

    logger.info("🚀 AI MIO Manager starting...")

    # Initialize database
    init_database()
    logger.info("   ✅ Database initialized")

    # Initialize Automation Toolkit Manager
    toolkit_manager = AutomationToolkitManager()
    logger.info("   ✅ Automation Toolkit Manager initialized")

    # Initialize Orchestrator Client
    orchestrator_client = OrchestratorClient(
        orchestrator_url=settings.ORCHESTRATOR_URL
    )
    logger.info("   ✅ Orchestrator Client initialized")

    # Initialize Gateway Manager
    gateway_manager = GatewayManager(
        gateway_url=settings.GATEWAY_URL
    )
    logger.info("   ✅ Gateway Manager initialized")

    # Start automation scheduler
    start_scheduler(
        toolkit_manager=toolkit_manager,
        orchestrator_client=orchestrator_client,
        gateway_manager=gateway_manager
    )
    logger.info("   ✅ Automation scheduler started")

    # Initial service discovery
    discovery_result = await toolkit_manager.discover_services()
    logger.info(f"   📊 Discovered {discovery_result['total_services']} services")
    logger.info(f"   📈 Coverage: {discovery_result['coverage']['percentage']:.1f}%")

    logger.info("✅ AI MIO Manager ready on port 8046")

    yield

    # Shutdown
    logger.info("👋 AI MIO Manager shutting down...")
    stop_scheduler()
    logger.info("   ✅ Scheduler stopped")


# FastAPI app
app = FastAPI(
    title="AI MIO Manager",
    description="Intelligent Monitoring & Observability Manager - Управляющий центр платформы",
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

# Include routes
app.include_router(routes.router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "mio-manager",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8046,
        reload=True
    )
