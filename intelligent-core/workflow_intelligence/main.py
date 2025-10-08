"""
Workflow Intelligence Service

Standalone FastAPI service providing:
- Case Library API
- Workflow Analysis
- ML-powered recommendations

Port: 8037
"""

import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Add shared event_bus to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = 8037
HOST = "0.0.0.0"

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Workflow Intelligence Service")
    logger.info(f"📍 Port: {PORT}")

    # Initialize EventBus
    try:
        await init_event_bus(
            service_name="workflow-intelligence",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        logger.info("✅ EventBus initialized")
    except Exception as e:
        logger.warning(f"⚠️ EventBus init failed: {e}")

    logger.info("✅ Service ready!")
    yield

    # Shutdown
    logger.info("👋 Shutting down Workflow Intelligence Service")
    bus = get_event_bus()
    if bus:
        await bus.close()

# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Workflow Intelligence Service",
    description="Workflow Intelligence, Case Library & ML Analysis",
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
router = APIRouter(tags=["Workflow Intelligence"])


# ==================== Models ====================

class CaseAddRequest(BaseModel):
    """Add case to library"""
    case_data: Dict[str, Any]
    module: str
    source: str = "community"
    metadata: Optional[Dict[str, Any]] = None


class CaseResponse(BaseModel):
    """Case response"""
    case_id: str
    status: str
    message: str


class WorkflowAnalysisRequest(BaseModel):
    """Workflow analysis request"""
    workflow_id: str
    workflow_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class WorkflowAnalysisResponse(BaseModel):
    """Workflow analysis response"""
    workflow_id: str
    analysis: Dict[str, Any]
    recommendations: List[str]
    confidence: float


# ==================== Core Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "workflow-intelligence",
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/info")
async def get_info():
    """Service information"""
    return {
        "service": "workflow-intelligence",
        "version": "1.0.0",
        "features": [
            "Case Library Management",
            "Workflow Analysis",
            "ML Recommendations",
            "Community Integration"
        ],
        "endpoints": {
            "cases": [
                "/cases/add",
                "/cases/{case_id}",
                "/cases/search"
            ],
            "analysis": [
                "/analyze",
                "/recommend"
            ]
        },
        "status": "available"
    }


# ==================== Case Library Endpoints ====================

@router.post("/cases/add", response_model=CaseResponse)
async def add_case(request: CaseAddRequest):
    """
    Add case to workflow intelligence library

    Used by community_intelligence to sync approved cases
    """
    try:
        # TODO: Full implementation with case_library
        # For now, accept and return success
        import uuid
        case_id = str(uuid.uuid4())

        logger.info(
            f"📚 Case added to library: {case_id} "
            f"(module: {request.module}, source: {request.source})"
        )

        # Publish event
        await publish_event(
            event_type="workflow.case.added",
            data={
                "case_id": case_id,
                "module": request.module,
                "source": request.source,
                "metadata": request.metadata or {}
            }
        )

        return CaseResponse(
            case_id=case_id,
            status="success",
            message=f"Case added to library successfully"
        )

    except Exception as e:
        logger.error(f"Failed to add case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get case by ID"""
    # TODO: Full implementation
    return {
        "case_id": case_id,
        "status": "found",
        "data": {
            "module": "example",
            "title": "Example Case",
            "description": "Case description here"
        },
        "note": "Full implementation coming soon"
    }


@router.post("/cases/search")
async def search_cases(query: Dict[str, Any]):
    """Search cases in library"""
    # TODO: Full implementation
    return {
        "results": [],
        "total": 0,
        "note": "Full implementation coming soon"
    }


@router.post("/cases/bulk")
async def bulk_operations(operations: List[Dict[str, Any]]):
    """Bulk case operations"""
    # TODO: Full implementation
    return {
        "processed": len(operations),
        "status": "success",
        "note": "Full implementation coming soon"
    }


# ==================== Workflow Analysis Endpoints ====================

@router.post("/analyze", response_model=WorkflowAnalysisResponse)
async def analyze_workflow(request: WorkflowAnalysisRequest):
    """
    Analyze workflow with ML

    Returns insights and recommendations
    """
    try:
        # TODO: Full ML implementation
        # For now, return simple analysis

        logger.info(f"🔍 Analyzing workflow: {request.workflow_id}")

        return WorkflowAnalysisResponse(
            workflow_id=request.workflow_id,
            analysis={
                "complexity": "medium",
                "estimated_duration": "10 minutes",
                "risk_level": "low",
                "optimization_potential": "moderate"
            },
            recommendations=[
                "Consider parallel execution for independent tasks",
                "Add error handling for critical steps",
                "Cache frequently accessed data"
            ],
            confidence=0.75
        )

    except Exception as e:
        logger.error(f"Workflow analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def get_recommendations(workflow_data: Dict[str, Any]):
    """Get ML-powered recommendations for workflow"""
    # TODO: Full ML implementation
    return {
        "recommendations": [
            {
                "type": "optimization",
                "priority": "high",
                "description": "Optimize data loading",
                "expected_impact": "30% faster execution"
            },
            {
                "type": "reliability",
                "priority": "medium",
                "description": "Add retry logic",
                "expected_impact": "95% success rate"
            }
        ],
        "note": "Full ML implementation coming soon"
    }


# Include router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "workflow-intelligence",
        "version": "1.0.0",
        "status": "running",
        "mode": "api_gateway",
        "docs": "/docs",
        "health": "/health",
        "info": "/info"
    }


@app.get("/health")
async def app_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "workflow-intelligence",
        "version": "1.0.0"
    }




if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False
    )
