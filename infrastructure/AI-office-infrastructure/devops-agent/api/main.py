#!/usr/bin/env python3
"""
DevOps Agent REST API

FastAPI service for DevOps Agent
Port: 8060
"""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import uvicorn

# Add project root to path
project_root = Path(__file__).parents[4]
sys.path.append(str(project_root))

# Add DevOps Agent directory to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from agent import DevOpsAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="DevOps Agent API",
    description="REST API for DevOps Agent - AI Digital Colleague",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[DevOpsAgent] = None


# Models
class ScanRequest(BaseModel):
    scan_type: str = "full"  # 'full', 'events', 'containers', 'deployments'


# Endpoints
@app.on_event("startup")
async def startup():
    """Initialize DevOps Agent on startup"""
    global agent
    agent = DevOpsAgent("/Users/MD/AI-Platform-ISO")
    await agent.initialize()
    logger.info("✅ DevOps Agent API ready")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "DevOps Agent API",
        "version": "1.0.0",
        "status": "operational",
        "port": 8060
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "devops-agent",
        "statistics": {
            "scans_completed": agent.scans_completed if agent else 0,
            "issues_detected": agent.issues_detected if agent else 0,
            "fixes_applied": agent.fixes_applied if agent else 0
        }
    }


@app.post("/scan")
async def trigger_scan(request: ScanRequest):
    """Trigger infrastructure scan"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    logger.info(f"🔍 Triggering {request.scan_type} scan...")

    result = await agent.run_full_cycle()

    return {
        "status": "success",
        "scan_type": request.scan_type,
        "result": result
    }


@app.get("/reports/latest")
async def get_latest_report():
    """Get latest report"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    latest = agent.report_manager.get_latest()

    if not latest:
        raise HTTPException(status_code=404, detail="No reports found")

    return latest


@app.get("/reports/history")
async def get_report_history(limit: int = 10):
    """Get report history"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    history = agent.report_manager.get_history(limit=limit)

    return {
        "total": len(history),
        "reports": history
    }


@app.get("/status")
async def get_status():
    """Get DevOps Agent status"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return {
        "agent_id": agent.agent_id,
        "agent_name": agent.name,
        "status": "operational",
        "statistics": {
            "scans_completed": agent.scans_completed,
            "issues_detected": agent.issues_detected,
            "fixes_applied": agent.fixes_applied
        },
        "integrations": {
            "rag": agent.rag is not None,
            "llm": agent.llm is not None,
            "eventbus": agent.eventbus is not None,
            "workflow_intelligence": agent.workflow_intelligence is not None
        }
    }


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if agent and agent.workflow_intelligence:
        await agent.workflow_intelligence.close()
    logger.info("👋 DevOps Agent API shutdown")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8060)
