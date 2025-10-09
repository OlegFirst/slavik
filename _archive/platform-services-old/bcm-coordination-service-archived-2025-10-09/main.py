"""
BCM Coordination Service - Main Application
============================================

Координирует 10 специализированных BCM анализаторов:
1. Compliance Analyzer (ISO 22301)
2. Risk Analyzer (FAIR)
3. Impact Analyzer (BIA)
4. Governance Analyzer
5. Emergency Analyzer
6. Performance Analyzer
7. Learning Analyzer
8. Lifecycle Analyzer
9. Plan Analyzer
10. Scenario Analyzer

ISO 22301: Полная координация всех аспектов BCM
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import BCM Orchestrator
try:
    import sys
    from pathlib import Path
    INTELLIGENT_CORE = Path(__file__).parent.parent.parent / 'intelligent-core'
    BCM_ORCHESTRATOR_PATH = INTELLIGENT_CORE / 'orchestration' / 'bcm-services-orchestrator'
    sys.path.insert(0, str(BCM_ORCHESTRATOR_PATH))

    from analyzer_coordinator import (
        AnalyzerCoordinator,
        AnalyzerType
    )
    BCM_ORCHESTRATOR_AVAILABLE = True
    logger.info("✅ BCM Orchestrator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️  BCM Orchestrator not available: {e}")
    BCM_ORCHESTRATOR_AVAILABLE = False
    AnalyzerType = None


# Global instances
analyzer_coordinator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global analyzer_coordinator

    logger.info("🚀 Starting BCM Coordination Service")
    logger.info("📍 Port: 8070")
    logger.info("📋 ISO 22301: Full BCM Coordination")

    # Initialize Analyzer Coordinator
    if BCM_ORCHESTRATOR_AVAILABLE:
        try:
            # Initialize analyzers (placeholder - will be connected to actual analyzers)
            analyzers = {
                "compliance_analyzer": None,  # Will be initialized
                "risk_analyzer": None,
                "impact_analyzer": None,
                "governance_analyzer": None,
                "emergency_analyzer": None,
                "performance_analyzer": None,
                "learning_analyzer": None,
                "lifecycle_analyzer": None,
                "plan_analyzer": None,
                "scenario_analyzer": None,
            }

            analyzer_coordinator = AnalyzerCoordinator(analyzers)
            logger.info("✅ Analyzer Coordinator initialized")
            logger.info(f"   10 BCM Analyzers ready for coordination")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Analyzer Coordinator: {e}")
    else:
        logger.warning("⚠️  Running in fallback mode - BCM Orchestrator not available")

    logger.info("✅ BCM Coordination Service ready")

    yield

    # Shutdown
    logger.info("👋 Shutting down BCM Coordination Service")


# Create FastAPI app
app = FastAPI(
    title="BCM Coordination Service",
    description="Coordinates 10 specialized BCM analyzers for comprehensive BCM analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request Models
# ============================================================================

class AnalysisRequest(BaseModel):
    """Analysis request model"""
    analyzer_type: str  # 'compliance', 'risk', 'impact', 'auto', etc.
    input_data: Dict[str, Any]
    tenant_id: str
    metadata: Optional[Dict[str, Any]] = None


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request model"""
    analyzer_sequence: List[str]  # ['risk', 'impact', 'plan']
    input_data: Dict[str, Any]
    tenant_id: str


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bcm-coordination-service",
        "port": 8070,
        "bcm_orchestrator_available": BCM_ORCHESTRATOR_AVAILABLE,
        "coordinator_initialized": analyzer_coordinator is not None
    }


@app.get("/api/v1/analyzers")
async def get_available_analyzers():
    """Get list of available BCM analyzers"""
    if not analyzer_coordinator:
        return {
            "success": False,
            "error": "Analyzer Coordinator not initialized"
        }

    return {
        "success": True,
        "analyzers": [
            {
                "type": "compliance_analyzer",
                "name": "Compliance Analyzer",
                "description": "ISO 22301 gap analysis and compliance checking",
                "iso_clauses": "All clauses"
            },
            {
                "type": "risk_analyzer",
                "name": "Risk Analyzer",
                "description": "FAIR-based risk quantification and assessment",
                "iso_clauses": "Clause 6 (Risk Assessment)"
            },
            {
                "type": "impact_analyzer",
                "name": "Impact Analyzer",
                "description": "Business Impact Analysis (BIA) with RTO/RPO",
                "iso_clauses": "Clause 8.2.2 (BIA)"
            },
            {
                "type": "governance_analyzer",
                "name": "Governance Analyzer",
                "description": "Policy adherence and governance framework",
                "iso_clauses": "Clauses 4, 5, 7 (Context, Leadership, Support)"
            },
            {
                "type": "emergency_analyzer",
                "name": "Emergency Analyzer",
                "description": "Crisis response and incident severity analysis",
                "iso_clauses": "Clause 8.4 (Incident Response)"
            },
            {
                "type": "performance_analyzer",
                "name": "Performance Analyzer",
                "description": "KPI analysis and performance metrics",
                "iso_clauses": "Clause 9 (Performance Evaluation)"
            },
            {
                "type": "learning_analyzer",
                "name": "Learning Analyzer",
                "description": "Pattern extraction and lessons learned",
                "iso_clauses": "Clause 10 (Improvement)"
            },
            {
                "type": "lifecycle_analyzer",
                "name": "Lifecycle Analyzer",
                "description": "BCM maturity assessment and lifecycle stage",
                "iso_clauses": "All clauses (maturity)"
            },
            {
                "type": "plan_analyzer",
                "name": "Plan Analyzer",
                "description": "Recovery plan quality and completeness",
                "iso_clauses": "Clause 8.4 (Recovery Plans)"
            },
            {
                "type": "scenario_analyzer",
                "name": "Scenario Analyzer",
                "description": "Exercise design and scenario planning",
                "iso_clauses": "Clause 8.5 (Exercising and Testing)"
            }
        ]
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get coordinator statistics"""
    if not analyzer_coordinator:
        return {
            "success": False,
            "error": "Analyzer Coordinator not initialized"
        }

    return {
        "success": True,
        "stats": analyzer_coordinator.get_stats()
    }


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.post("/api/v1/analyze")
async def analyze(request: AnalysisRequest):
    """
    Route analysis to appropriate analyzer.

    Supports:
    - Specific analyzer: analyzer_type='compliance_analyzer'
    - Auto-routing: analyzer_type='auto'
    """
    if not analyzer_coordinator:
        raise HTTPException(
            status_code=503,
            detail="Analyzer Coordinator not initialized"
        )

    try:
        # Map string to AnalyzerType enum
        if request.analyzer_type == 'auto':
            analyzer_type = AnalyzerType.AUTO
        else:
            analyzer_type = AnalyzerType(request.analyzer_type)

        result = await analyzer_coordinator.route_analysis(
            analysis_type=analyzer_type,
            input_data=request.input_data,
            tenant_id=request.tenant_id,
            metadata=request.metadata
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid analyzer type: {request.analyzer_type}"
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/api/v1/analyze/batch")
async def batch_analyze(request: BatchAnalysisRequest):
    """
    Execute batch analysis (multiple analyzers in sequence).

    Example: Risk → Impact → Plan pipeline
    """
    if not analyzer_coordinator:
        raise HTTPException(
            status_code=503,
            detail="Analyzer Coordinator not initialized"
        )

    try:
        # Map strings to AnalyzerType enums
        analyzer_sequence = [
            AnalyzerType(analyzer_type)
            for analyzer_type in request.analyzer_sequence
        ]

        result = await analyzer_coordinator.batch_analysis(
            analyzer_sequence=analyzer_sequence,
            input_data=request.input_data,
            tenant_id=request.tenant_id
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid analyzer type in sequence: {e}"
        )
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================================
# Convenience Endpoints (Specific Analyses)
# ============================================================================

@app.post("/api/v1/analyze/compliance")
async def analyze_compliance(
    tenant_id: str,
    standard: str = "ISO_22301",
    clauses: Optional[List[str]] = None
):
    """Execute ISO compliance check"""
    request = AnalysisRequest(
        analyzer_type="compliance_analyzer",
        input_data={
            "type": "compliance_gap",
            "standard": standard,
            "clauses": clauses or []
        },
        tenant_id=tenant_id
    )
    return await analyze(request)


@app.post("/api/v1/analyze/risk")
async def analyze_risk(
    tenant_id: str,
    scenario: str,
    assets: List[Dict]
):
    """Execute FAIR-based risk assessment"""
    request = AnalysisRequest(
        analyzer_type="risk_analyzer",
        input_data={
            "type": "risk_assessment",
            "scenario": scenario,
            "assets": assets
        },
        tenant_id=tenant_id
    )
    return await analyze(request)


@app.post("/api/v1/analyze/impact")
async def analyze_impact(
    tenant_id: str,
    processes: List[Dict],
    scope: str = "full"
):
    """Execute Business Impact Analysis"""
    request = AnalysisRequest(
        analyzer_type="impact_analyzer",
        input_data={
            "type": "bia_analysis",
            "processes": processes,
            "scope": scope
        },
        tenant_id=tenant_id
    )
    return await analyze(request)


@app.post("/api/v1/analyze/iso_clause")
async def analyze_by_iso_clause(
    tenant_id: str,
    clause: str
):
    """
    Analyze specific ISO 22301 clause.

    Auto-routes to appropriate analyzer based on clause:
    - 4.x → Governance
    - 6.x → Risk
    - 8.x → Impact
    - 9.x → Performance
    """
    request = AnalysisRequest(
        analyzer_type="auto",
        input_data={
            "type": "iso_audit",
            "clause": clause,
            "standard": "ISO_22301"
        },
        tenant_id=tenant_id
    )
    return await analyze(request)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8070,
        reload=True,
        log_level="info"
    )
