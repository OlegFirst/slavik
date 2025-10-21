"""
AI Office Orchestrator - Coordinates AI Office agents

Central coordination service for AI Office infrastructure agents.
Manages agent lifecycle, routing, and inter-agent communication.

Port: 8059
"""

import logging
import os
import sys
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

# Add paths for EventBus
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# EventBus imports
try:
    from infrastructure.eventbus import create_eventbus
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus not available - running without service discovery integration")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("AI_OFFICE_ORCHESTRATOR_PORT", "8059"))
HOST = os.getenv("AI_OFFICE_ORCHESTRATOR_HOST", "0.0.0.0")

app = FastAPI(
    title="AI Office Orchestrator",
    description="Coordinates AI Office agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent registry
agents_registry: Dict[str, Dict] = {}

# EventBus instance (global)
eventbus = None
heartbeat_task = None

class AgentRegistration(BaseModel):
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str

class TaskRequest(BaseModel):
    task_type: str
    parameters: Dict
    priority: Optional[str] = "normal"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-office-orchestrator",
        "version": "1.0.0",
        "registered_agents": len(agents_registry)
    }

@app.post("/agents/register")
async def register_agent(registration: AgentRegistration):
    """Register an AI agent with the orchestrator"""
    agents_registry[registration.agent_id] = {
        "type": registration.agent_type,
        "capabilities": registration.capabilities,
        "endpoint": registration.endpoint,
        "registered_at": datetime.now().isoformat(),
        "status": "active"
    }

    logger.info(f"Agent registered: {registration.agent_id}")

    return {
        "status": "registered",
        "agent_id": registration.agent_id
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "agents": agents_registry,
        "count": len(agents_registry)
    }

@app.post("/tasks/execute")
async def execute_task(task: TaskRequest):
    """Execute a task by routing it to appropriate agent"""
    logger.info(f"Executing task: {task.task_type}")

    # Find suitable agent
    # TODO: Implement intelligent agent selection

    return {
        "task_id": "task-001",
        "status": "queued",
        "assigned_agent": "pending"
    }

@app.get("/status")
async def get_orchestrator_status():
    """Get orchestrator status and statistics"""
    return {
        "orchestrator": "healthy",
        "registered_agents": len(agents_registry),
        "active_agents": sum(1 for a in agents_registry.values() if a["status"] == "active"),
        "uptime": "running",
        "eventbus_connected": eventbus is not None
    }

# ============================================================================
# EventBus Integration
# ============================================================================

async def publish_service_started():
    """Publish service started event to EventBus"""
    if not EVENTBUS_AVAILABLE or not eventbus:
        return

    try:
        await eventbus.publish(
            'platform.service.started',
            {
                'service_name': 'orchestrator',
                'orchestrator': 'ai-office',
                'port': PORT,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'version': '1.0.0',
                    'capabilities': ['agent_registration', 'task_routing', 'agent_coordination'],
                    'type': 'coordinator'
                },
                'dependencies': ['eventbus']
            }
        )
        logger.info(" Published service started event to EventBus")
    except Exception as e:
        logger.error(f"Failed to publish service started event: {e}")

async def publish_service_heartbeat():
    """Publish heartbeat events periodically"""
    if not EVENTBUS_AVAILABLE or not eventbus:
        return

    while True:
        try:
            await eventbus.publish(
                'platform.service.heartbeat',
                {
                    'service_name': 'orchestrator',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'active',
                    'metrics': {
                        'registered_agents': len(agents_registry),
                        'active_agents': sum(1 for a in agents_registry.values() if a["status"] == "active")
                    }
                }
            )
            logger.debug(" Heartbeat sent to EventBus")
            await asyncio.sleep(30)  # Every 30 seconds
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            await asyncio.sleep(5)

async def publish_service_health():
    """Publish health status"""
    if not EVENTBUS_AVAILABLE or not eventbus:
        return

    try:
        await eventbus.publish(
            'platform.service.health',
            {
                'service_name': 'orchestrator',
                'health_status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'registered_agents': len(agents_registry),
                    'active_agents': sum(1 for a in agents_registry.values() if a["status"] == "active")
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to publish health: {e}")

@app.on_event("startup")
async def startup_event():
    """Application startup - initialize EventBus"""
    global eventbus, heartbeat_task

    logger.info(" AI Office Orchestrator starting...")

    if EVENTBUS_AVAILABLE:
        try:
            # Create EventBus connection
            logger.info("Connecting to EventBus...")
            eventbus = create_eventbus('redis')
            await eventbus.connect()
            logger.info(" EventBus connected")

            # Publish service started
            await publish_service_started()

            # Start heartbeat task
            heartbeat_task = asyncio.create_task(publish_service_heartbeat())
            logger.info(" Heartbeat task started")

        except Exception as e:
            logger.error(f"EventBus initialization failed: {e}")
            logger.warning("️  Running without EventBus integration")
            eventbus = None
    else:
        logger.warning("️  EventBus not available - service discovery disabled")

    logger.info(f" AI Office Orchestrator ready on port {PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown - cleanup EventBus"""
    global eventbus, heartbeat_task

    logger.info(" AI Office Orchestrator shutting down...")

    # Stop heartbeat
    if heartbeat_task:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

    # Publish service stopped
    if eventbus:
        try:
            await eventbus.publish(
                'platform.service.stopped',
                {
                    'service_name': 'orchestrator',
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'graceful_shutdown'
                }
            )
            logger.info(" Published service stopped event")
        except Exception as e:
            logger.error(f"Failed to publish shutdown event: {e}")

        # Disconnect EventBus
        try:
            await eventbus.disconnect()
            logger.info(" EventBus disconnected")
        except Exception as e:
            logger.error(f"EventBus disconnect error: {e}")

    logger.info(" Shutdown complete")

if __name__ == "__main__":
    logger.info(f"Starting AI Office Orchestrator on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
