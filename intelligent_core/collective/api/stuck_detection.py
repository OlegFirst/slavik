"""
Stuck Detection API Endpoints

Endpoints for detecting when organizations need help
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from ..services.stuck_detector_service import StuckDetectorService
from ..dependencies import get_current_user, get_stuck_detector

router = APIRouter(prefix="/stuck-detection", tags=["stuck-detection"])

# Response Models

class StuckSignals(BaseModel):
    """Signals indicating organization might be stuck"""
    days_no_progress: int
    validation_failures: int
    avg_confidence: float
    repeated_questions: int
    repeated_doc_reviews: int
    frustration_score: float

class Recommendation(BaseModel):
    """Recommendation for stuck organization"""
    type: str
    title: str
    description: str
    action: str
    problem_type: Optional[str] = None

class StuckCheckResponse(BaseModel):
    """Response from stuck check"""
    is_stuck: bool
    stuck_score: int
    threshold: int
    signals: StuckSignals
    recommendations: List[Recommendation]

    class Config:
        json_schema_extra = {
            "example": {
                "is_stuck": True,
                "stuck_score": 5,
                "threshold": 4,
                "signals": {
                    "days_no_progress": 10,
                    "validation_failures": 7,
                    "avg_confidence": 0.45,
                    "repeated_questions": 4,
                    "repeated_doc_reviews": 6,
                    "frustration_score": 0.65
                },
                "recommendations": [
                    {
                        "type": "collective_agent",
                        "title": "Get help from 7 organizations that solved this",
                        "description": "We found 7 similar organizations...",
                        "action": "create_collective_agent",
                        "problem_type": "supply_chain_complexity"
                    }
                ]
            }
        }

# Endpoints

@router.get("/check", response_model=StuckCheckResponse)
async def check_if_stuck(
    module: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    detector: StuckDetectorService = Depends(get_stuck_detector)
):
    """
    Check if your organization is stuck

    **What we check:**
    - Days without progress (threshold: 7)
    - Validation failure rate
    - AI confidence scores
    - Question repetition patterns
    - Document review patterns
    - Frustration indicators

    **Scoring:**
    - 0-3 points: On track 
    - 4-6 points: Stuck, need help 🆘
    - 7+ points: Seriously stuck 

    **If stuck:**
    We'll recommend creating a Collective Agent from organizations
    that successfully solved what you're working on.

    **Example:**
    ```
    You've been on "supply chain dependency mapping" for 10 days
    with multiple validation failures.

    Stuck Score: 5

    Recommendation: Create Collective Agent from 7 organizations
    that completed this successfully.
    ```
    """

    result = await detector.check_organization(
        org_id=current_user['org_id'],
        module=module
    )

    return StuckCheckResponse(
        is_stuck=result['is_stuck'],
        stuck_score=result['stuck_score'],
        threshold=result['threshold'],
        signals=StuckSignals(**result['signals']),
        recommendations=[
            Recommendation(**rec) for rec in result['recommendations']
        ]
    )

@router.post("/accept-help")
async def accept_collective_help(
    problem_type: str = Field(..., description="Problem type to get help with"),
    current_user: dict = Depends(get_current_user),
    detector: StuckDetectorService = Depends(get_stuck_detector)
):
    """
    Accept offer for collective help

    Creates a Collective Agent for the problem you're stuck on

    **Flow:**
    1. You're stuck on "supply chain complexity"
    2. Platform detects stuck (via `/check` endpoint)
    3. Platform recommends Collective Agent
    4. You accept help (this endpoint)
    5. Collective Agent created from similar orgs
    6. You can start chatting with it

    Returns:
        Redirect to create collective agent endpoint
    """

    offer_id = await detector.offer_collective_help(
        org_id=current_user['org_id'],
        problem_type=problem_type
    )

    return {
        "status": "accepted",
        "message": "Creating Collective Agent...",
        "next_action": f"POST /collective-agents/create with problem_type='{problem_type}'"
    }
