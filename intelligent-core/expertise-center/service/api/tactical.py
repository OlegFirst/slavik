"""
Tactical Assistants Endpoints

12 BCM Experts:
1. BIA Specialist
2. Risk Analyst
3. Compliance Copilot
4. Incident Advisor
5. Plan Generator
6. Exercise Designer
7. Project Manager
8. Documents Specialist
9. Governance Specialist
10. Learning Specialist
11. Validation Specialist
12. Community Specialist
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tactical", tags=["Tactical Assistants"])

# Import tactical assistants
try:
    from expertise_center.domains.bcm.tactical_assistants.bia_specialist import BIASpecialistAI
    from expertise_center.domains.bcm.tactical_assistants.risk_analyst import RiskAnalystAI
    from expertise_center.domains.bcm.tactical_assistants.compliance_copilot import ComplianceCopilotAI
    from expertise_center.domains.bcm.tactical_assistants.incident_advisor import IncidentAdvisorAI
    from expertise_center.domains.bcm.tactical_assistants.plan_generator import PlanGeneratorAI
    from expertise_center.domains.bcm.tactical_assistants.exercise_designer import ExerciseDesignerAI
    from expertise_center.domains.bcm.tactical_assistants.project_manager import ProjectManagerAI
    from expertise_center.domains.bcm.tactical_assistants.documents_specialist import DocumentsSpecialistAI
    from expertise_center.domains.bcm.tactical_assistants.governance_specialist import GovernanceSpecialistAI
    from expertise_center.domains.bcm.tactical_assistants.learning_specialist import LearningSpecialistAI
    from expertise_center.domains.bcm.tactical_assistants.validation_specialist import ValidationSpecialistAI
    from expertise_center.domains.bcm.tactical_assistants.community_specialist import CommunitySpecialistAI
except ImportError as e:
    logger.error(f"Failed to import tactical assistants: {e}")
    # Graceful degradation
    BIASpecialistAI = None
    RiskAnalystAI = None
    ComplianceCopilotAI = None
    IncidentAdvisorAI = None
    PlanGeneratorAI = None
    ExerciseDesignerAI = None
    ProjectManagerAI = None
    DocumentsSpecialistAI = None
    GovernanceSpecialistAI = None
    LearningSpecialistAI = None
    ValidationSpecialistAI = None
    CommunitySpecialistAI = None

from expertise_center.shared.base.assistant_context import AssistantContext


# ==================== Models ====================

class ExpertRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    organization_id: Optional[str] = None


class ExpertResponse(BaseModel):
    expert: str
    response: str
    confidence: float = 0.8
    sources: List[str] = []
    metadata: Dict[str, Any] = {}


# ==================== Expert Registry ====================

EXPERTS = {}


def get_expert(expert_type: str):
    """Get or create expert instance"""
    if expert_type not in EXPERTS:
        expert_class = {
            "bia_specialist": BIASpecialistAI,
            "risk_analyst": RiskAnalystAI,
            "compliance_copilot": ComplianceCopilotAI,
            "incident_advisor": IncidentAdvisorAI,
            "plan_generator": PlanGeneratorAI,
            "exercise_designer": ExerciseDesignerAI,
            "project_manager": ProjectManagerAI,
            "documents_specialist": DocumentsSpecialistAI,
            "governance_specialist": GovernanceSpecialistAI,
            "learning_specialist": LearningSpecialistAI,
            "validation_specialist": ValidationSpecialistAI,
            "community_specialist": CommunitySpecialistAI,
        }.get(expert_type)

        if not expert_class:
            raise HTTPException(status_code=404, detail=f"Expert '{expert_type}' not found")

        if expert_class is None:
            raise HTTPException(
                status_code=503,
                detail=f"Expert '{expert_type}' not available (import failed)"
            )

        EXPERTS[expert_type] = expert_class()

    return EXPERTS[expert_type]


async def dispatch_to_expert(
    expert_type: str,
    query: str,
    context: Dict[str, Any],
    organization_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dispatch query to appropriate expert

    Returns:
        Dict with response, confidence, sources, metadata
    """
    expert = get_expert(expert_type)

    # Build context
    assistant_context = AssistantContext(
        value=context or {},
        organization_id=organization_id or "default"
    )

    # Process query
    try:
        response = await expert.process(query, assistant_context)

        return {
            "response": response,
            "confidence": 0.8,  # TODO: Get from expert
            "sources": [],  # TODO: Get from RAG
            "metadata": {
                "expert_id": expert.assistant_id,
                "expert_name": expert.name,
                "specialty": expert.specialty,
                "domain": expert.domain
            }
        }
    except Exception as e:
        logger.error(f"Expert {expert_type} processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Expert processing failed: {str(e)}"
        )


# ==================== BIA Specialist ====================

@router.post("/bia/analyze", response_model=ExpertResponse)
async def analyze_business_impact(request: ExpertRequest):
    """
    Perform Business Impact Analysis

    Example:
    ```json
    {
      "query": "Analyze impact of email system outage",
      "context": {
        "industry": "finance",
        "organization_size": "medium"
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="bia_specialist",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="bia_specialist",
        **result
    )


# ==================== Risk Analyst ====================

@router.post("/risk/assess", response_model=ExpertResponse)
async def assess_risk(request: ExpertRequest):
    """
    Assess risks for given scenario

    Example:
    ```json
    {
      "query": "Assess ransomware risk for our organization",
      "context": {
        "industry": "healthcare",
        "security_maturity": "medium"
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="risk_analyst",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="risk_analyst",
        **result
    )


# ==================== Compliance Copilot ====================

@router.post("/compliance/check", response_model=ExpertResponse)
async def check_compliance(request: ExpertRequest):
    """
    Check compliance against standards

    Example:
    ```json
    {
      "query": "Check compliance with ISO 22301 clause 8.2",
      "context": {
        "standard": "iso22301",
        "current_practices": ["BIA conducted", "Plans documented"]
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="compliance_copilot",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="compliance_copilot",
        **result
    )


# ==================== Incident Advisor ====================

@router.post("/incident/advise", response_model=ExpertResponse)
async def advise_on_incident(request: ExpertRequest):
    """
    Get incident response advice

    Example:
    ```json
    {
      "query": "Data center fire - immediate actions?",
      "context": {
        "incident_type": "fire",
        "severity": "critical",
        "affected_systems": ["primary_datacenter"]
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="incident_advisor",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="incident_advisor",
        **result
    )


# ==================== Plan Generator ====================

@router.post("/plan/generate", response_model=ExpertResponse)
async def generate_plan(request: ExpertRequest):
    """
    Generate BCM plan

    Example:
    ```json
    {
      "query": "Generate IT disaster recovery plan",
      "context": {
        "plan_type": "IT_DR",
        "scope": "all_it_systems",
        "rto": "4_hours"
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="plan_generator",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="plan_generator",
        **result
    )


# ==================== Exercise Designer ====================

@router.post("/exercise/design", response_model=ExpertResponse)
async def design_exercise(request: ExpertRequest):
    """
    Design BCM exercise

    Example:
    ```json
    {
      "query": "Design tabletop exercise for ransomware",
      "context": {
        "exercise_type": "tabletop",
        "scenario": "ransomware",
        "participants": ["IT", "Security", "Management"]
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="exercise_designer",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="exercise_designer",
        **result
    )


# ==================== Project Manager ====================

@router.post("/project/manage", response_model=ExpertResponse)
async def manage_project(request: ExpertRequest):
    """
    BCM project management advice

    Example:
    ```json
    {
      "query": "Create BCM implementation roadmap",
      "context": {
        "organization_maturity": "initial",
        "timeline": "12_months",
        "resources": ["1_bcm_manager", "budget_100k"]
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="project_manager",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="project_manager",
        **result
    )


# ==================== Documents Specialist ====================

@router.post("/documents/create", response_model=ExpertResponse)
async def create_document(request: ExpertRequest):
    """
    Create BCM document

    Example:
    ```json
    {
      "query": "Create BCM policy template",
      "context": {
        "document_type": "policy",
        "industry": "finance",
        "regulations": ["ISO22301", "PCI_DSS"]
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="documents_specialist",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="documents_specialist",
        **result
    )


# ==================== Governance Specialist ====================

@router.post("/governance/analyze", response_model=ExpertResponse)
async def analyze_governance(request: ExpertRequest):
    """
    Analyze BCM governance

    Example:
    ```json
    {
      "query": "Assess BCM governance structure",
      "context": {
        "organization_type": "corporate",
        "size": "large",
        "current_structure": "..."
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="governance_specialist",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="governance_specialist",
        **result
    )


# ==================== Learning Specialist ====================

@router.post("/learning/design", response_model=ExpertResponse)
async def design_learning(request: ExpertRequest):
    """
    Design BCM training

    Example:
    ```json
    {
      "query": "Design awareness training for all staff",
      "context": {
        "audience": "all_staff",
        "delivery": "online",
        "duration": "30_minutes"
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="learning_specialist",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="learning_specialist",
        **result
    )


# ==================== Validation Specialist ====================

@router.post("/validation/validate", response_model=ExpertResponse)
async def validate_bcm(request: ExpertRequest):
    """
    Validate BCM capabilities

    Example:
    ```json
    {
      "query": "Validate our BCM program readiness",
      "context": {
        "validation_scope": "full_program",
        "standards": ["ISO22301"]
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="validation_specialist",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="validation_specialist",
        **result
    )


# ==================== Community Specialist ====================

@router.post("/community/engage", response_model=ExpertResponse)
async def engage_community(request: ExpertRequest):
    """
    BCM community engagement

    Example:
    ```json
    {
      "query": "Build BCM community of practice",
      "context": {
        "organization_size": "large",
        "distributed": true,
        "current_engagement": "low"
      }
    }
    ```
    """
    result = await dispatch_to_expert(
        expert_type="community_specialist",
        query=request.query,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return ExpertResponse(
        expert="community_specialist",
        **result
    )
