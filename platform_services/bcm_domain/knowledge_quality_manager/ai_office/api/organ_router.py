"""
AI Organ Router

Individual organ invocation endpoints
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import get_db

# Add organs to path
organs_path = Path(__file__).parent.parent / "organs"
sys.path.insert(0, str(organs_path))

# Import all organs
from governance_brain import GovernanceBrain
from emergency_response import EmergencyResponse
from impact_oracle import ImpactOracle
from scenario_creator import ScenarioCreator
from risk_advisor import RiskAdvisor
from compliance_guardian import ComplianceGuardian
from performance_analyst import PerformanceAnalyst
from learning_coach import LearningCoach
from plan_generator import PlanGenerator
from lifecycle_monitor import LifecycleMonitor

# Import LLM router (will be None if not configured)
try:
    llm_path = Path(__file__).parent.parent / "llm"
    sys.path.insert(0, str(llm_path))
    from llm_router import LLMRouter
    llm_router = LLMRouter()
except:
    llm_router = None

router = APIRouter()


# Pydantic schemas
class OrganAnalysisRequest(BaseModel):
    """Request for organ analysis"""
    model_config = ConfigDict(from_attributes=True)

    context: Dict[str, Any] = Field(..., description="Analysis context (varies by organ)")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenancy")


class OrganAnalysisResponse(BaseModel):
    """Response from organ analysis"""
    model_config = ConfigDict(from_attributes=True)

    organ: str
    emoji: str
    insights: List[str]
    recommendations: List[str]
    confidence: float
    metadata: Dict[str, Any]


# Organ instances (lazy initialization)
_organs = {}


def get_organ(organ_name: str):
    """Get or create organ instance"""
    if organ_name not in _organs:
        organ_classes = {
            "governance_brain": GovernanceBrain,
            "emergency_response": EmergencyResponse,
            "impact_oracle": ImpactOracle,
            "scenario_creator": ScenarioCreator,
            "risk_advisor": RiskAdvisor,
            "compliance_guardian": ComplianceGuardian,
            "performance_analyst": PerformanceAnalyst,
            "learning_coach": LearningCoach,
            "plan_generator": PlanGenerator,
            "lifecycle_monitor": LifecycleMonitor
        }

        if organ_name not in organ_classes:
            raise ValueError(f"Unknown organ: {organ_name}")

        _organs[organ_name] = organ_classes[organ_name](llm_router=llm_router)

    return _organs[organ_name]


# Organ endpoints
@router.post("/governance-brain", response_model=OrganAnalysisResponse)
async def analyze_governance(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Analyze governance and strategic alignment

    Required context keys:
    - organization_state: Current org state
    - policies: List of policies (optional)
    - strategic_objectives: Strategic goals (optional)
    - compliance_requirements: Regulatory requirements (optional)
    """
    organ = get_organ("governance_brain")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/emergency-response", response_model=OrganAnalysisResponse)
async def analyze_emergency(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Analyze emergency situation and provide response guidance

    Required context keys:
    - incident_type: Type of incident
    - incident_description: Detailed description
    - twin_id: Digital Twin ID (optional)
    - severity: Initial severity (optional)
    - affected_systems: List of affected systems (optional)
    """
    organ = get_organ("emergency_response")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/impact-oracle", response_model=OrganAnalysisResponse)
async def predict_impact(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Predict business impact and recommend RTO/RPO

    Required context keys:
    - disruption_scenario: What's being disrupted
    - twin_id: Digital Twin ID (optional)
    - process_data: Process information (optional)
    """
    organ = get_organ("impact_oracle")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/scenario-creator", response_model=OrganAnalysisResponse)
async def create_scenario(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Generate BCM exercise scenario

    Required context keys:
    - scenario_type: Type (exercise/simulation/tabletop)
    - threat_type: Primary threat
    - twin_id: Digital Twin ID (optional)
    - complexity_level: Beginner/Intermediate/Advanced (optional)
    """
    organ = get_organ("scenario_creator")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/risk-advisor", response_model=OrganAnalysisResponse)
async def analyze_risks(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Analyze risks and recommend mitigations

    Required context keys:
    - organization_state: Current state
    - twin_id: Digital Twin ID (optional)
    - known_risks: List of known risks (optional)
    - scenario: Risk scenario (optional)
    """
    organ = get_organ("risk_advisor")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/compliance-guardian", response_model=OrganAnalysisResponse)
async def check_compliance(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Assess compliance with BCM standards

    Required context keys:
    - standards: List of standards (e.g., ['ISO_22301'])
    - twin_id: Digital Twin ID (optional)
    - current_controls: List of controls (optional)
    - policies: List of policies (optional)
    """
    organ = get_organ("compliance_guardian")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/performance-analyst", response_model=OrganAnalysisResponse)
async def analyze_performance(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Analyze BCM performance metrics

    Required context keys:
    - kpi_data: Current KPI values
    - twin_id: Digital Twin ID (optional)
    - historical_data: Time-series data (optional)
    - time_period: Analysis period (optional)
    """
    organ = get_organ("performance_analyst")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/learning-coach", response_model=OrganAnalysisResponse)
async def analyze_learning(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Analyze learning needs and recommend training

    Required context keys:
    - twin_id: Digital Twin ID (optional)
    - exercise_results: Recent performance (optional)
    - training_history: Past training (optional)
    - competency_matrix: Current skills (optional)
    """
    organ = get_organ("learning_coach")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/plan-generator", response_model=OrganAnalysisResponse)
async def generate_plan(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Generate BCM plan

    Required context keys:
    - plan_type: Type of plan (BCP/DRP/IRP/etc.)
    - twin_id: Digital Twin ID (optional)
    - process_data: Critical process info (optional)
    - rto_rpo: Recovery objectives (optional)
    """
    organ = get_organ("plan_generator")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.post("/lifecycle-monitor", response_model=OrganAnalysisResponse)
async def monitor_lifecycle(
    request: OrganAnalysisRequest,
    db: Session = Depends(get_db)
) -> OrganAnalysisResponse:
    """
    Monitor BCM lifecycle health

    Required context keys:
    - twin_id: Digital Twin ID (optional)
    - time_period: Monitoring period (optional)
    - lifecycle_stage: Current stage (optional)
    - activity_log: Recent activities (optional)
    """
    organ = get_organ("lifecycle_monitor")
    result = await organ.analyze(request.context)
    return OrganAnalysisResponse(**result)


@router.get("/organs")
async def list_organs():
    """List all available AI organs"""
    return {
        "organs": [
            {"name": "governance_brain", "emoji": "", "description": "Strategic intelligence and policy guidance"},
            {"name": "emergency_response", "emoji": "", "description": "Crisis management and incident response"},
            {"name": "impact_oracle", "emoji": "", "description": "Predictive business impact analysis"},
            {"name": "scenario_creator", "emoji": "", "description": "AI-powered scenario generation"},
            {"name": "risk_advisor", "emoji": "", "description": "Risk analysis and mitigation"},
            {"name": "compliance_guardian", "emoji": "️", "description": "Standards compliance monitoring"},
            {"name": "performance_analyst", "emoji": "", "description": "BCM KPI intelligence"},
            {"name": "learning_coach", "emoji": "", "description": "Training optimization"},
            {"name": "plan_generator", "emoji": "", "description": "BCM plan creation"},
            {"name": "lifecycle_monitor", "emoji": "", "description": "Lifecycle health monitoring"}
        ]
    }
