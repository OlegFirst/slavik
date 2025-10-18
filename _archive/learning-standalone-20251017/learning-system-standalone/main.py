"""
Learning System Service - Main Entry Point

Learns from exercises, simulations, and AI analyses

Port: 8033
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
    title="Learning System Service",
    description="Machine learning from BCM exercises and simulations",
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
    logger.info("🎓 Starting Learning System Service...")

    # Initialize database
    init_db()
    create_tables()

    # Initialize Redis
    init_redis()

    logger.info("✅ Learning System Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Learning System Service...")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "learning-system",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Learning System Service",
        "version": "2.0.0",
        "description": "Machine learning from BCM exercises, simulations, and AI analyses",
        "capabilities": [
            "📚 Pattern detection from exercise history",
            "🎯 Performance trend analysis",
            "🧠 AI model improvement recommendations",
            "📈 Predictive success scoring",
            "🔄 Continuous learning loop",
            "👤 Competency tracking & team analysis",
            "📊 Process gap analysis & coverage matrix",
            "🎮 Gamification with badges & leaderboards",
            "📖 Knowledge base integration & learning paths",
            "🤖 ML-powered predictions & difficulty adjustment",
            "📈 Advanced analytics dashboard",
            "🔄 Self-learning ML models (auto-improvement)",
            "🎓 Automated learning needs collection",
            "📚 Auto-creation of knowledge from patterns",
            "🌐 External knowledge sync (ISO, threats, best practices)",
            "🔗 Platform integration (RAG, ML Platform, shared TOOLS)",
            "🎯 Unified semantic search across all knowledge",
            "🤝 Shared ML models with cross-service learning"
        ],
        "docs": "/docs"
    }


# Import models (so they're registered with SQLAlchemy)
from models import learning_models

# Import routers
from api import (
    pattern_router,
    learning_router,
    recommendation_router,
    competency_router,
    process_gap_router,
    gamification_router,
    knowledge_router,
    ml_router,
    analytics_router,
    self_learning_router,
    platform_integration_router
)

# Core routers
app.include_router(pattern_router.router, prefix="/api/learning/patterns", tags=["Patterns"])
app.include_router(learning_router.router, prefix="/api/learning", tags=["Learning"])
app.include_router(recommendation_router.router, prefix="/api/learning/recommendations", tags=["Recommendations"])

# Enhancement routers
app.include_router(competency_router.router, prefix="/api/learning/competency", tags=["Competency Tracking"])
app.include_router(process_gap_router.router, prefix="/api/learning/process-gaps", tags=["Process Gap Analysis"])
app.include_router(gamification_router.router, prefix="/api/learning/gamification", tags=["Gamification"])
app.include_router(knowledge_router.router, prefix="/api/learning/knowledge", tags=["Knowledge Integration"])
app.include_router(ml_router.router, prefix="/api/learning/ml", tags=["ML Predictions"])
app.include_router(analytics_router.router, prefix="/api/learning/analytics", tags=["Analytics Dashboard"])

# Phase 2: Self-Learning & Automation routers
app.include_router(self_learning_router.router, prefix="/api/learning/auto", tags=["Self-Learning & Automation"])

# Phase 3: Platform Integration routers (TOOLS, RAG, ML Platform)
app.include_router(platform_integration_router.router, prefix="/api/learning/platform", tags=["Platform Integration"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8033,
        reload=True,
        log_level="info"
    )
