"""
Expertise Center Public API

Предоставляет доступ к:
- Tactical Assistants (12 BCM экспертов)
- Strategic Analyzers
- Domain Knowledge
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Main router
router = APIRouter(prefix="/expertise", tags=["Expertise Center"])

# Sub-routers - import after router creation to avoid circular imports
try:
    from service.api.tactical import router as tactical_router
    from service.api.analyzers import router as analyzers_router

    router.include_router(tactical_router)
    router.include_router(analyzers_router)
except ImportError as e:
    logger.warning(f"Could not import sub-routers: {e}")
    tactical_router = None
    analyzers_router = None


# ==================== Models ====================

class ExpertInfo(BaseModel):
    id: str
    name: str
    specialty: str
    domain: str
    capabilities: List[str]


class ExpertQueryRequest(BaseModel):
    expert_type: str  # "bia_specialist", "risk_analyst", etc.
    query: str
    context: Optional[Dict[str, Any]] = None
    organization_id: Optional[str] = None


class ExpertQueryResponse(BaseModel):
    expert: str
    response: str
    confidence: float
    sources: List[str]
    metadata: Dict[str, Any]


# ==================== Health & Info ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "expertise-center",
        "version": "1.0.0"
    }


@router.get("/info")
async def get_info():
    """Get available experts and capabilities"""
    return {
        "tactical_assistants": [
            {
                "id": "bia_specialist",
                "name": "BIA Specialist AI",
                "specialty": "Business Impact Analysis & RTO/RPO Determination",
                "domain": "bcm"
            },
            {
                "id": "risk_analyst",
                "name": "Risk Analyst AI",
                "specialty": "Risk Assessment & Treatment Planning",
                "domain": "bcm"
            },
            {
                "id": "compliance_copilot",
                "name": "Compliance Copilot AI",
                "specialty": "ISO 22301 Compliance & Gap Analysis",
                "domain": "bcm"
            },
            {
                "id": "incident_advisor",
                "name": "Incident Advisor AI",
                "specialty": "Incident Response & Crisis Management",
                "domain": "bcm"
            },
            {
                "id": "plan_generator",
                "name": "Plan Generator AI",
                "specialty": "BCM Plan Development & Maintenance",
                "domain": "bcm"
            },
            {
                "id": "exercise_designer",
                "name": "Exercise Designer AI",
                "specialty": "BCM Exercise & Testing Design",
                "domain": "bcm"
            },
            {
                "id": "project_manager",
                "name": "Project Manager AI",
                "specialty": "BCM Program Management",
                "domain": "bcm"
            },
            {
                "id": "documents_specialist",
                "name": "Documents Specialist AI",
                "specialty": "BCM Documentation & Templates",
                "domain": "bcm"
            },
            {
                "id": "governance_specialist",
                "name": "Governance Specialist AI",
                "specialty": "BCM Governance & Leadership",
                "domain": "bcm"
            },
            {
                "id": "learning_specialist",
                "name": "Learning Specialist AI",
                "specialty": "BCM Training & Awareness",
                "domain": "bcm"
            },
            {
                "id": "validation_specialist",
                "name": "Validation Specialist AI",
                "specialty": "BCM Validation & Verification",
                "domain": "bcm"
            },
            {
                "id": "community_specialist",
                "name": "Community Specialist AI",
                "specialty": "BCM Community Building & Collaboration",
                "domain": "bcm"
            }
        ],
        "analyzers": [
            {
                "id": "compliance_analyzer",
                "name": "Compliance Analyzer",
                "specialty": "ISO 22301 Compliance Analysis",
                "domain": "bcm"
            },
            {
                "id": "risk_analyzer",
                "name": "Risk Analyzer",
                "specialty": "Risk Impact Analysis",
                "domain": "bcm"
            },
            {
                "id": "governance_analyzer",
                "name": "Governance Analyzer",
                "specialty": "BCM Governance Analysis",
                "domain": "bcm"
            },
            {
                "id": "lifecycle_analyzer",
                "name": "Lifecycle Analyzer",
                "specialty": "BCM Lifecycle Analysis",
                "domain": "bcm"
            },
            {
                "id": "learning_analyzer",
                "name": "Learning Analyzer",
                "specialty": "Learning & Training Analysis",
                "domain": "bcm"
            },
            {
                "id": "performance_analyzer",
                "name": "Performance Analyzer",
                "specialty": "BCM Performance Analysis",
                "domain": "bcm"
            },
            {
                "id": "emergency_analyzer",
                "name": "Emergency Analyzer",
                "specialty": "Emergency Response Analysis",
                "domain": "bcm"
            },
            {
                "id": "impact_analyzer",
                "name": "Impact Analyzer",
                "specialty": "Business Impact Analysis",
                "domain": "bcm"
            },
            {
                "id": "plan_analyzer",
                "name": "Plan Analyzer",
                "specialty": "BCM Plan Analysis",
                "domain": "bcm"
            },
            {
                "id": "scenario_analyzer",
                "name": "Scenario Analyzer",
                "specialty": "BCM Scenario Analysis",
                "domain": "bcm"
            }
        ],
        "domains": ["bcm", "iso22301"],
        "total_experts": 12,
        "total_analyzers": 10
    }


@router.get("/experts", response_model=List[ExpertInfo])
async def list_experts():
    """List all available experts"""
    info = await get_info()

    experts = []
    for ta in info["tactical_assistants"]:
        experts.append(ExpertInfo(
            id=ta["id"],
            name=ta["name"],
            specialty=ta["specialty"],
            domain=ta["domain"],
            capabilities=[]  # TODO: Add from expert metadata
        ))

    return experts


@router.get("/experts/{expert_id}")
async def get_expert_info(expert_id: str):
    """Get detailed information about specific expert"""
    info = await get_info()

    # Search in tactical assistants
    for ta in info["tactical_assistants"]:
        if ta["id"] == expert_id:
            return {
                **ta,
                "type": "tactical_assistant",
                "status": "available"
            }

    # Search in analyzers
    for analyzer in info["analyzers"]:
        if analyzer["id"] == expert_id:
            return {
                **analyzer,
                "type": "analyzer",
                "status": "available"
            }

    raise HTTPException(status_code=404, detail=f"Expert '{expert_id}' not found")


# ==================== Generic Expert Query ====================

@router.post("/query", response_model=ExpertQueryResponse)
async def query_expert(request: ExpertQueryRequest):
    """
    Query any expert with natural language

    Example:
    ```json
    {
      "expert_type": "bia_specialist",
      "query": "What are critical processes for healthcare?",
      "context": {"industry": "healthcare"}
    }
    ```
    """
    # Import tactical router's dispatch function
    from .tactical import dispatch_to_expert

    try:
        result = await dispatch_to_expert(
            expert_type=request.expert_type,
            query=request.query,
            context=request.context or {},
            organization_id=request.organization_id
        )

        return ExpertQueryResponse(
            expert=request.expert_type,
            response=result["response"],
            confidence=result.get("confidence", 0.8),
            sources=result.get("sources", []),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Expert query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query to {request.expert_type} failed: {str(e)}"
        )
