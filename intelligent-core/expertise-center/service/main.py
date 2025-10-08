"""
Expertise Center Service

Standalone FastAPI service providing access to:
- 12 Tactical Assistants (BCM Experts)
- 10 Strategic Analyzers
- Domain Knowledge

Port: 8035
"""

import logging
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from service.api.routes import router
from service import config

# Import EventBus
from shared.event_bus import init_event_bus, get_event_bus, publish_event

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Expertise Center Service",
    description="""
    BCM Expertise Center - AI Experts and Analyzers

    ## Tactical Assistants (12)
    - BIA Specialist
    - Risk Analyst
    - Compliance Copilot
    - Incident Advisor
    - Plan Generator
    - Exercise Designer
    - Project Manager
    - Documents Specialist
    - Governance Specialist
    - Learning Specialist
    - Validation Specialist
    - Community Specialist

    ## Strategic Analyzers (10)
    - Compliance Analyzer
    - Risk Analyzer
    - Governance Analyzer
    - Lifecycle Analyzer
    - Learning Analyzer
    - Performance Analyzer
    - Emergency Analyzer
    - Impact Analyzer
    - Plan Analyzer
    - Scenario Analyzer
    """,
    version=config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info(f"🚀 Starting {config.SERVICE_NAME} v{config.VERSION}")
    logger.info(f"📍 Port: {config.PORT}")
    logger.info(f"🔧 AI Foundation: {config.AI_FOUNDATION_URL}")
    logger.info(f"📚 Knowledge Base: {config.KNOWLEDGE_BASE_URL}")

    # Initialize EventBus
    try:
        await init_event_bus(
            service_name="expertise-center",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        logger.info("✅ EventBus initialized")
    except Exception as e:
        logger.warning(f"⚠️ EventBus init failed: {e}")

    # Log available experts
    logger.info("👥 Available Tactical Assistants: 12")
    logger.info("📊 Available Analyzers: 10")

    logger.info("✅ Expertise Center Service ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("👋 Shutting down Expertise Center Service")
    bus = get_event_bus()
    if bus:
        await bus.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": config.SERVICE_NAME,
        "version": config.VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/expertise/health",
        "info": "/expertise/info"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": config.SERVICE_NAME,
        "version": config.VERSION
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        workers=config.WORKERS
    )
