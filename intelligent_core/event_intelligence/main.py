"""
Event Intelligence Service

AI-powered event analysis, learning, and prediction
Port: 8039
"""

import logging
import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import uvicorn
from contextlib import asynccontextmanager

# Import shared event bus
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.event_bus import init_event_bus, get_event_bus

try:
    from .api import router as event_intelligence_router, initialize_event_intelligence
    from .auto_discovery import init_auto_discovery, get_discovery_engine
    from . import event_subscribers  # Import to register @subscribe_to decorators
except ImportError:
    # Fallback for when running as script
    from event_intelligence.api import router as event_intelligence_router, initialize_event_intelligence
    from event_intelligence.auto_discovery import init_auto_discovery, get_discovery_engine
    import event_intelligence.event_subscribers as event_subscribers

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = 8039
HOST = "0.0.0.0"

# Create FastAPI app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Event Intelligence Service...")

    # Initialize EventBus
    try:
        await init_event_bus(
            service_name="event-intelligence",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        logger.info("✅ EventBus initialized")
    except Exception as e:
        logger.warning(f"⚠️ EventBus init failed: {e}")

    # Initialize Auto-Discovery Engine
    try:
        await init_auto_discovery()
        logger.info("✅ Auto-Discovery Engine started")
    except Exception as e:
        logger.warning(f"⚠️ Auto-Discovery init failed: {e}")

    # Initialize event intelligence components
    try:
        await initialize_event_intelligence()
        logger.info("✅ Event Intelligence components ready")
    except Exception as e:
        logger.warning(f"⚠️ Component init warning: {e}")

    logger.info("✅ Event Intelligence Service fully operational")
    yield

    # Shutdown
    logger.info("🛑 Shutting down Event Intelligence Service...")
    bus = get_event_bus()
    if bus:
        await bus.close()
    logger.info("✅ Shutdown complete")

app = FastAPI(
    lifespan=lifespan,
    title="Event Intelligence Service",
    description="AI-powered event analysis, learning, and prediction",
    version="1.0.0",
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


# ==================== Lifecycle Events ====================




# ==================== Core Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "event-intelligence",
        "version": "1.0.0",
        "port": PORT
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Event Intelligence",
        "tagline": "AI-powered event analysis, learning, and prediction",
        "version": "1.0.0",
        "port": PORT,
        "capabilities": [
            "event_analysis",
            "ml_learning",
            "gap_prediction",
            "knowledge_base",
            "pattern_detection",
            "ai_recommendations"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "metrics": "/metrics",
            "api": "/api/v1/event-intelligence/*"
        },
        "integration": {
            "temporal_workflows": "event_intelligence_workflow.py",
            "mio_manager": "automated_event_analysis"
        }
    }


# Include API router
app.include_router(event_intelligence_router)


# ==================== Auto-Discovery Endpoints ====================

@app.get("/discovery/services")
async def get_services():
    """Get all discovered services."""
    engine = get_discovery_engine()
    if not engine:
        return {"error": "Auto-discovery not initialized"}

    return {
        "services": engine.registry.get_all_services(),
        "stats": engine.registry.get_stats()
    }


@app.get("/discovery/patterns")
async def get_patterns(min_confidence: float = 0.5):
    """Get learned event patterns."""
    engine = get_discovery_engine()
    if not engine:
        return {"error": "Auto-discovery not initialized"}

    patterns = engine.pattern_learner.get_patterns(min_confidence=min_confidence)

    return {
        "patterns": patterns,
        "total": len(patterns),
        "min_confidence": min_confidence
    }


@app.get("/discovery/predict/{event_type}")
async def predict_next_event(event_type: str, min_confidence: float = 0.5):
    """Predict the next event after given event type."""
    engine = get_discovery_engine()
    if not engine:
        return {"error": "Auto-discovery not initialized"}

    prediction = engine.pattern_learner.predict_next_event(
        event_type,
        min_confidence=min_confidence
    )

    if not prediction:
        return {
            "event_type": event_type,
            "prediction": None,
            "message": f"No patterns found with confidence >= {min_confidence}"
        }

    return {
        "event_type": event_type,
        "prediction": prediction
    }


@app.get("/discovery/stats")
async def get_discovery_stats():
    """Get comprehensive auto-discovery statistics."""
    engine = get_discovery_engine()
    if not engine:
        return {"error": "Auto-discovery not initialized"}

    bus = get_event_bus()
    bus_stats = bus.get_stats() if bus else {}

    return {
        "discovery": engine.get_stats(),
        "event_bus": bus_stats,
        "timestamp": "2025-10-08T14:00:00Z"
    }


@app.get("/discovery/graph")
async def get_event_graph():
    """Get event flow graph (for visualization)."""
    engine = get_discovery_engine()
    if not engine:
        return {"error": "Auto-discovery not initialized"}

    patterns = engine.pattern_learner.get_patterns(min_confidence=0.3)

    # Build graph structure
    nodes = set()
    edges = []

    for pattern in patterns:
        nodes.add(pattern["from"])
        nodes.add(pattern["to"])
        edges.append({
            "from": pattern["from"],
            "to": pattern["to"],
            "weight": pattern["confidence"],
            "avg_time": pattern["avg_time_seconds"],
            "occurrences": pattern["occurrences"]
        })

    return {
        "nodes": [{"id": node, "label": node} for node in nodes],
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }


if __name__ == "__main__":
    uvicorn.run(
        "event_intelligence.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
