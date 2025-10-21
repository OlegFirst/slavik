"""
DevOps Agent - Infrastructure and deployment automation

Manages deployment, CI/CD, infrastructure provisioning, and monitoring.

Port: 8058
"""

import sys
from pathlib import Path

# Add parent path for EventBusHelper
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn

# Import EventBus Helper
try:
    from _shared.eventbus_helper import EventBusHelper
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus Helper not available")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("DEVOPS_AGENT_PORT", "8058"))
HOST = os.getenv("DEVOPS_AGENT_HOST", "0.0.0.0")

# Global EventBus helper
eventbus_helper = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    global eventbus_helper

    logger.info("=" * 70)
    logger.info(" DEVOPS AGENT STARTING...")
    logger.info("=" * 70)
    logger.info(f"   Service: DevOps Agent")
    logger.info(f"   Port: {PORT}")
    logger.info("=" * 70)

    # Initialize EventBus Helper
    if EVENTBUS_AVAILABLE:
        try:
            eventbus_helper = EventBusHelper(
                service_name="devops-agent",
                port=PORT,
                orchestrator="ai-office",
                capabilities=[
                    "deployment_automation",
                    "ci_cd_management",
                    "infrastructure_provisioning",
                    "monitoring_setup",
                    "rollback_management"
                ],
                dependencies=["eventbus", "mio-manager"],
                service_type="specialist"
            )
            await eventbus_helper.startup()
            logger.info(" EventBus integration initialized")
        except Exception as e:
            logger.error(f" EventBus initialization failed: {e}")
            logger.warning("️  Running without EventBus integration")

    logger.info("=" * 70)
    logger.info(" DEVOPS AGENT READY!")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info(" DEVOPS AGENT SHUTTING DOWN...")
    logger.info("=" * 70)

    # Shutdown EventBus
    if eventbus_helper:
        await eventbus_helper.shutdown()
        logger.info(" EventBus integration stopped")

    logger.info(" Goodbye!")


app = FastAPI(
    title="DevOps Agent",
    description="Infrastructure and deployment automation",
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

class DeploymentRequest(BaseModel):
    service: str
    environment: str
    config: Optional[Dict] = None

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "devops-agent",
        "version": "1.0.0"
    }

@app.post("/deploy")
async def deploy_service(request: DeploymentRequest):
    """Deploy service to specified environment"""
    logger.info(f"Deploying {request.service} to {request.environment}")
    return {
        "status": "success",
        "service": request.service,
        "environment": request.environment,
        "deployment_id": "deploy-001"
    }

@app.get("/status")
async def get_deployment_status():
    """Get current deployment status"""
    return {
        "active_deployments": 0,
        "pending_deployments": 0,
        "infrastructure_health": "healthy"
    }

if __name__ == "__main__":
    logger.info(f"Starting DevOps Agent on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
