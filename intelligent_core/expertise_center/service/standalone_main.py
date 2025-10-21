"""
Expertise Center Service - Standalone Main

Simple service providing API gateway to BCM experts and analyzers
Port: 8035
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = 8035
HOST = "0.0.0.0"

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(" Starting Expertise Center Service")
    logger.info(f" Port: {PORT}")
    logger.info(" 12 Tactical Assistants available")
    logger.info(" 10 Analyzers available")
    logger.info(" Service ready!")
    yield
    # Shutdown
    logger.info(" Shutting down Expertise Center Service")

# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Expertise Center Service",
    description="BCM Expertise Center - 12 AI Experts + 10 Analyzers",
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

# Router
router = APIRouter(prefix="/expertise", tags=["Expertise Center"])


# ==================== Models ====================

class ExpertQueryRequest(BaseModel):
    expert_type: str
    query: str
    context: Optional[Dict[str, Any]] = None
    organization_id: Optional[str] = None


class ExpertQueryResponse(BaseModel):
    expert: str
    response: str
    confidence: float = 0.8
    sources: List[str] = []
    metadata: Dict[str, Any] = {}


# ==================== Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "expertise-center",
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/info")
async def get_info():
    """Get available experts"""
    return {
        "tactical_assistants": [
            {"id": "bia_specialist", "name": "BIA Specialist AI", "specialty": "Business Impact Analysis"},
            {"id": "risk_analyst", "name": "Risk Analyst AI", "specialty": "Risk Assessment"},
            {"id": "compliance_copilot", "name": "Compliance Copilot AI", "specialty": "ISO 22301 Compliance"},
            {"id": "incident_advisor", "name": "Incident Advisor AI", "specialty": "Incident Response"},
            {"id": "plan_generator", "name": "Plan Generator AI", "specialty": "BCM Plan Development"},
            {"id": "exercise_designer", "name": "Exercise Designer AI", "specialty": "BCM Exercise Design"},
            {"id": "project_manager", "name": "Project Manager AI", "specialty": "BCM Program Management"},
            {"id": "documents_specialist", "name": "Documents Specialist AI", "specialty": "BCM Documentation"},
            {"id": "governance_specialist", "name": "Governance Specialist AI", "specialty": "BCM Governance"},
            {"id": "learning_specialist", "name": "Learning Specialist AI", "specialty": "BCM Training"},
            {"id": "validation_specialist", "name": "Validation Specialist AI", "specialty": "BCM Validation"},
            {"id": "community_specialist", "name": "Community Specialist AI", "specialty": "BCM Community"}
        ],
        "analyzers": [
            {"id": "compliance", "name": "Compliance Analyzer"},
            {"id": "risk", "name": "Risk Analyzer"},
            {"id": "governance", "name": "Governance Analyzer"},
            {"id": "lifecycle", "name": "Lifecycle Analyzer"},
            {"id": "learning", "name": "Learning Analyzer"},
            {"id": "performance", "name": "Performance Analyzer"},
            {"id": "emergency", "name": "Emergency Analyzer"},
            {"id": "impact", "name": "Impact Analyzer"},
            {"id": "plan", "name": "Plan Analyzer"},
            {"id": "scenario", "name": "Scenario Analyzer"}
        ],
        "total_experts": 12,
        "total_analyzers": 10,
        "status": "available"
    }


@router.post("/query", response_model=ExpertQueryResponse)
async def query_expert(request: ExpertQueryRequest):
    """
    Query any expert (simplified for now)

    Full implementation will be added after fixing imports
    """
    return ExpertQueryResponse(
        expert=request.expert_type,
        response=f"Expert '{request.expert_type}' received query: {request.query}. Full implementation coming soon.",
        confidence=0.8,
        sources=[],
        metadata={
            "expert_type": request.expert_type,
            "status": "gateway_mode",
            "note": "Full expert integration in progress"
        }
    )


# Tactical endpoints (simplified)
tactical_router = APIRouter(prefix="/tactical", tags=["Tactical Assistants"])

@tactical_router.post("/bia/analyze")
async def analyze_business_impact(request: Dict[str, Any]):
    """BIA Analysis (simplified)"""
    return {"status": "gateway_mode", "message": "BIA Specialist API ready, full integration coming soon"}

@tactical_router.post("/risk/assess")
async def assess_risk(request: Dict[str, Any]):
    """Risk Assessment (simplified)"""
    return {"status": "gateway_mode", "message": "Risk Analyst API ready, full integration coming soon"}

@tactical_router.post("/compliance/check")
async def check_compliance(request: Dict[str, Any]):
    """Compliance Check (simplified)"""
    return {"status": "gateway_mode", "message": "Compliance Copilot API ready, full integration coming soon"}

router.include_router(tactical_router)


# Analyzers endpoints (simplified)
analyzers_router = APIRouter(prefix="/analyzers", tags=["Analyzers"])

@analyzers_router.post("/compliance/analyze")
async def analyze_compliance(request: Dict[str, Any]):
    """Compliance Analysis (simplified)"""
    return {"status": "gateway_mode", "message": "Compliance Analyzer API ready, full integration coming soon"}

@analyzers_router.post("/risk/analyze")
async def analyze_risk(request: Dict[str, Any]):
    """Risk Analysis (simplified)"""
    return {"status": "gateway_mode", "message": "Risk Analyzer API ready, full integration coming soon"}

router.include_router(analyzers_router)


# Include main router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "expertise-center-service",
        "version": "1.0.0",
        "status": "running",
        "mode": "gateway",
        "docs": "/docs",
        "health": "/expertise/health",
        "info": "/expertise/info",
        "note": "Full expert integration coming soon"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "expertise-center-service", "version": "1.0.0"}


# Startup moved to lifespan context manager above


if __name__ == "__main__":
    uvicorn.run(
        "standalone_main:app",
        host=HOST,
        port=PORT,
        reload=False
    )
