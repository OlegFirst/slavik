"""PDCA Analytics Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class PDCACycle(BaseModel):
    id: str
    workflow_id: str
    module: str
    phase: str
    quality_score: float
    started_at: str
    completed_at: Optional[str]
    status: str

@router.get("/cycles")
async def get_pdca_cycles(limit: int = 10):
    """Get recent PDCA cycles"""
    # TODO: Connect to workflow_intelligence API
    # For now, return mock data
    return {
        "cycles": [
            {
                "id": "pdca_001",
                "workflow_id": "wf_bia_001",
                "module": "bia-service",
                "phase": "act",
                "quality_score": 0.92,
                "started_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "status": "completed"
            },
            {
                "id": "pdca_002",
                "workflow_id": "wf_risk_001",
                "module": "risk-service",
                "phase": "check",
                "quality_score": 0.85,
                "started_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "completed_at": None,
                "status": "in_progress"
            }
        ],
        "total": 2
    }

@router.get("/metrics")
async def get_pdca_metrics():
    """Get PDCA metrics from Prometheus"""
    try:
        async with httpx.AsyncClient() as client:
            # Get PDCA cycles total
            resp = await client.get(
                "http://localhost:9090/api/v1/query?query=pdca_cycles_total",
                timeout=5.0
            )
            data = resp.json()

            return {
                "pdca_cycles_total": data.get("data", {}).get("result", []),
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error fetching PDCA metrics: {e}")
        return {"pdca_cycles_total": [], "error": str(e)}
