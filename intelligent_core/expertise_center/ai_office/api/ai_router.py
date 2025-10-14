"""
AI Analysis Router

Full AI analysis coordinating multiple organs
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import asyncio
from datetime import datetime

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import get_db

# Import organ router to reuse organ instances
from .organ_router import get_organ

router = APIRouter()


# Pydantic schemas
class FullAnalysisRequest(BaseModel):
    """Request for full AI analysis"""
    model_config = ConfigDict(from_attributes=True)

    twin_id: Optional[int] = Field(None, description="Digital Twin ID")
    analysis_type: str = Field(..., description="Type of analysis: comprehensive/risk/compliance/planning/emergency")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    organs_to_invoke: Optional[List[str]] = Field(None, description="Specific organs to invoke (default: auto-select based on analysis_type)")
    tenant_id: Optional[str] = Field(None, description="Tenant ID")


class FullAnalysisResponse(BaseModel):
    """Response from full AI analysis"""
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    analysis_type: str
    organs_invoked: List[str]
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    started_at: str
    completed_at: Optional[str] = None


# Analysis type to organs mapping
ANALYSIS_ORGAN_MAP = {
    "comprehensive": [
        "governance_brain",
        "risk_advisor",
        "compliance_guardian",
        "performance_analyst",
        "lifecycle_monitor"
    ],
    "risk": [
        "risk_advisor",
        "impact_oracle",
        "scenario_creator"
    ],
    "compliance": [
        "compliance_guardian",
        "governance_brain"
    ],
    "planning": [
        "plan_generator",
        "scenario_creator",
        "risk_advisor"
    ],
    "emergency": [
        "emergency_response",
        "impact_oracle",
        "risk_advisor"
    ],
    "training": [
        "learning_coach",
        "scenario_creator",
        "performance_analyst"
    ]
}


@router.post("/analyze", response_model=FullAnalysisResponse)
async def full_analysis(
    request: FullAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> FullAnalysisResponse:
    """
    Perform full AI analysis using multiple organs

    Analysis types:
    - comprehensive: Full BCM analysis (5 organs)
    - risk: Risk-focused analysis (3 organs)
    - compliance: Compliance assessment (2 organs)
    - planning: Planning and preparation (3 organs)
    - emergency: Emergency response (3 organs)
    - training: Learning and development (3 organs)

    Custom organ selection:
    - Specify organs_to_invoke to override defaults
    """

    # Determine which organs to invoke
    if request.organs_to_invoke:
        organs_to_invoke = request.organs_to_invoke
    elif request.analysis_type in ANALYSIS_ORGAN_MAP:
        organs_to_invoke = ANALYSIS_ORGAN_MAP[request.analysis_type]
    else:
        # Default to comprehensive
        organs_to_invoke = ANALYSIS_ORGAN_MAP["comprehensive"]

    # Build context for organs
    organ_context = {
        "twin_id": request.twin_id,
        **request.context
    }

    # Generate session ID
    session_id = f"ai_{request.analysis_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    started_at = datetime.utcnow().isoformat()

    # Invoke all organs in parallel
    tasks = []
    for organ_name in organs_to_invoke:
        try:
            organ = get_organ(organ_name)
            tasks.append(organ.analyze(organ_context))
        except Exception as e:
            # Log error but continue with other organs
            print(f"Error loading organ {organ_name}: {e}")

    # Execute all organs concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and format results
    valid_results = []
    for i, result in enumerate(results):
        if not isinstance(result, Exception):
            valid_results.append(result)
        else:
            print(f"Organ {organs_to_invoke[i]} failed: {result}")

    # Generate summary
    summary = _generate_summary(valid_results, request.analysis_type)

    completed_at = datetime.utcnow().isoformat()

    # TODO: Save to database (AnalysisSession model)

    return FullAnalysisResponse(
        session_id=session_id,
        analysis_type=request.analysis_type,
        organs_invoked=organs_to_invoke,
        results=valid_results,
        summary=summary,
        started_at=started_at,
        completed_at=completed_at
    )


def _generate_summary(results: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
    """Generate summary from multiple organ results"""

    # Aggregate insights and recommendations
    all_insights = []
    all_recommendations = []
    avg_confidence = 0.0

    for result in results:
        all_insights.extend(result.get("insights", []))
        all_recommendations.extend(result.get("recommendations", []))
        avg_confidence += result.get("confidence", 0.0)

    if results:
        avg_confidence /= len(results)

    # Deduplicate and prioritize
    # (Simple version - in production would use more sophisticated prioritization)
    unique_insights = list(dict.fromkeys(all_insights))[:10]  # Top 10
    unique_recommendations = list(dict.fromkeys(all_recommendations))[:10]  # Top 10

    return {
        "analysis_type": analysis_type,
        "organs_consulted": len(results),
        "total_insights": len(unique_insights),
        "total_recommendations": len(unique_recommendations),
        "average_confidence": round(avg_confidence, 2),
        "top_insights": unique_insights[:5],
        "top_recommendations": unique_recommendations[:5]
    }


@router.get("/analysis-types")
async def list_analysis_types():
    """List available analysis types"""
    return {
        "analysis_types": [
            {
                "type": "comprehensive",
                "description": "Full BCM analysis across all dimensions",
                "organs": ANALYSIS_ORGAN_MAP["comprehensive"]
            },
            {
                "type": "risk",
                "description": "Risk-focused analysis",
                "organs": ANALYSIS_ORGAN_MAP["risk"]
            },
            {
                "type": "compliance",
                "description": "Compliance and governance assessment",
                "organs": ANALYSIS_ORGAN_MAP["compliance"]
            },
            {
                "type": "planning",
                "description": "Planning and preparation analysis",
                "organs": ANALYSIS_ORGAN_MAP["planning"]
            },
            {
                "type": "emergency",
                "description": "Emergency response guidance",
                "organs": ANALYSIS_ORGAN_MAP["emergency"]
            },
            {
                "type": "training",
                "description": "Learning and development analysis",
                "organs": ANALYSIS_ORGAN_MAP["training"]
            }
        ]
    }
