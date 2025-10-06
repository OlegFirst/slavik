"""
Platform Orchestrator Service
Центральный сервис для оркестрации ВСЕХ BCM сервисов
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

# Add workflow-intelligence to path
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/intelligent-core')

# Import routers
from platform_orchestrator import router as platform_router
from orchestrator import router as wi_orchestrator_router
from monitoring_api import router as monitoring_router

# Prometheus
from prometheus_client import make_asgi_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Platform Orchestrator starting...")
    logger.info("📊 Monitoring all BCM services")
    yield
    logger.info("👋 Platform Orchestrator shutting down")


app = FastAPI(
    title="BCM Platform Orchestrator",
    description="Central orchestration for all BCM platform services",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(platform_router)           # /api/v1/platform/*
app.include_router(wi_orchestrator_router)   # /api/v1/workflow-intelligence/*
app.include_router(monitoring_router)        # /api/v1/monitoring/*

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    return {
        "service": "BCM Platform Orchestrator",
        "version": "2.0.0",
        "description": "Central orchestration for all BCM services",
        "endpoints": {
            "platform_health": "/api/v1/platform/health",
            "workflow_intelligence": "/api/v1/workflow-intelligence/benchmarks/all",
            "monitoring": "/api/v1/monitoring/metrics",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "platform-orchestrator",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        reload=True
    )
