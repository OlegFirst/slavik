"""
AI Intelligence Service - Main Entry Point

10 Specialized AI Organs for BCM Intelligence

Port: 8032
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
    title="AI Intelligence Service",
    description="10 Specialized AI Organs for BCM Intelligence",
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
    logger.info("🚀 Starting AI Intelligence Service...")
    logger.info("🧠 Initializing 10 AI Organs...")

    # Initialize database
    init_db()
    create_tables()

    # Initialize Redis
    init_redis()

    logger.info("✅ AI Intelligence Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Intelligence Service...")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-intelligence",
        "version": "2.0.0",
        "organs": 10
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Intelligence Service",
        "version": "2.0.0",
        "description": "10 Specialized AI Organs for BCM Intelligence",
        "organs": [
            "🧠 Governance Brain",
            "🚨 Emergency Response",
            "🔮 Impact Oracle",
            "📝 Scenario Creator",
            "⚡ Risk Advisor",
            "🛡️ Compliance Guardian",
            "📊 Performance Analyst",
            "🎓 Learning Coach",
            "📋 Plan Generator",
            "💓 Lifecycle Monitor"
        ],
        "docs": "/docs"
    }


# Import models (so they're registered with SQLAlchemy)
from models import ai_models

# Import routers
from api import ai_router, organ_router, insight_router

app.include_router(ai_router.router, prefix="/api/ai", tags=["AI Analysis"])
app.include_router(organ_router.router, prefix="/api/ai/organs", tags=["AI Organs"])
app.include_router(insight_router.router, prefix="/api/ai/insights", tags=["AI Insights"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8032,
        reload=True,
        log_level="info"
    )
