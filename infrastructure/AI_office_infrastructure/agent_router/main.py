"""
Agent Router - Routing requests to appropriate AI agents

Routes incoming requests to the most suitable AI agent based on request type,
context, and agent capabilities.

Port: 8057
"""

import sys
from pathlib import Path

# Add parent path for EventBusHelper
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn

# Import EventBus Helper
try:
    from _shared.eventbus_helper import EventBusHelper
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus Helper not available")

# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("AGENT_ROUTER_PORT", "8057"))
HOST = os.getenv("AGENT_ROUTER_HOST", "0.0.0.0")

# Global EventBus helper
eventbus_helper = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    global eventbus_helper

    logger.info("=" * 70)
    logger.info(" AGENT ROUTER STARTING...")
    logger.info("=" * 70)
    logger.info(f"   Service: Agent Router")
    logger.info(f"   Port: {PORT}")
    logger.info("=" * 70)

    # Initialize EventBus Helper
    if EVENTBUS_AVAILABLE:
        try:
            eventbus_helper = EventBusHelper(
                service_name="agent-router",
                port=PORT,
                orchestrator="ai-office",
                capabilities=[
                    "request_routing",
                    "agent_discovery",
                    "load_balancing",
                    "capability_matching"
                ],
                dependencies=["eventbus", "service-discovery"],
                service_type="infrastructure"
            )
            await eventbus_helper.startup()
            logger.info(" EventBus integration initialized")
        except Exception as e:
            logger.error(f" EventBus initialization failed: {e}")
            logger.warning("️  Running without EventBus integration")

    logger.info("=" * 70)
    logger.info(" AGENT ROUTER READY!")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info(" AGENT ROUTER SHUTTING DOWN...")
    logger.info("=" * 70)

    # Shutdown EventBus
    if eventbus_helper:
        await eventbus_helper.shutdown()
        logger.info(" EventBus integration stopped")

    logger.info(" Goodbye!")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Agent Router",
    description="Routes requests to appropriate AI agents",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class RouteRequest(BaseModel):
    request_type: str
    context: Dict
    priority: Optional[str] = "normal"

class RouteResponse(BaseModel):
    agent_id: str
    agent_url: str
    confidence: float

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agent-router",
        "version": "1.0.0"
    }

@app.post("/route", response_model=RouteResponse)
async def route_request(request: RouteRequest):
    """
    Route request to appropriate agent

    TODO: Implement intelligent routing logic based on:
    - Request type
    - Agent capabilities
    - Agent load
    - Request priority
    """
    # Placeholder routing logic
    return RouteResponse(
        agent_id="default-agent",
        agent_url="http://localhost:8000",
        confidence=0.8
    )

@app.get("/agents")
async def list_agents():
    """List available agents and their capabilities"""
    return {
        "agents": [
            {
                "id": "analytics-specialist",
                "url": "http://localhost:8056",
                "capabilities": ["analytics", "monitoring", "optimization"]
            },
            {
                "id": "mio-manager",
                "url": "http://localhost:8046",
                "capabilities": ["coordination", "resource-management"]
            }
        ]
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Agent Router on {HOST}:{PORT}")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
