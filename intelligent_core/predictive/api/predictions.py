"""
Predictions API

Endpoints for journey predictions and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()


# --- Pydantic Models ---

class MilestoneResponse(BaseModel):
    """Predicted milestone"""
    milestone: str
    predicted_start_date: datetime
    predicted_duration_days: int
    confidence: float
    reasoning: str
    recommended_experts: List[dict]
    estimated_cost: dict
    challenges: List[dict]


class JourneyPredictionResponse(BaseModel):
    """Journey prediction response"""
    org_id: UUID
    prediction_date: datetime
    horizon_days: int
    milestones: List[MilestoneResponse]
    similar_orgs_count: int


class CertificationPredictionResponse(BaseModel):
    """Certification timeline prediction"""
    predicted_certification_date: datetime
    months_remaining: float
    success_probability: float
    confidence: float
    based_on_orgs_count: int
    key_factors: List[str]


class DemandForecastResponse(BaseModel):
    """Expert demand forecast"""
    forecast_date: datetime
    horizon_days: int
    total_predicted_projects: int
    by_specialty: dict
    by_industry: dict


class RecommendationResponse(BaseModel):
    """Proactive recommendation"""
    type: str
    priority: str
    milestone: str
    days_until: int
    confidence: float
    actions: List[str]
    resources: List[dict]


# --- Endpoints ---

@router.get("/journey/{org_id}", response_model=JourneyPredictionResponse)
async def get_journey_prediction(
    org_id: UUID,
    horizon_days: int = Query(default=90, ge=7, le=365)
):
    """
    Get predicted journey timeline for organization

    Returns next milestones with confidence scores
    """

    # Would use actual journey_predictor service
    # For now, mock response

    return JourneyPredictionResponse(
        org_id=org_id,
        prediction_date=datetime.utcnow(),
        horizon_days=horizon_days,
        milestones=[
            MilestoneResponse(
                milestone="risk_assessment",
                predicted_start_date=datetime.utcnow() + timedelta(days=14),
                predicted_duration_days=34,
                confidence=0.87,
                reasoning="83% of similar organizations started risk 14±3 days after BIA",
                recommended_experts=[
                    {
                        "specialty": "risk_assessment",
                        "usage_count": 47,
                        "helpful_rate": 0.92
                    }
                ],
                estimated_cost={
                    "estimated_min": 6800,
                    "estimated_max": 10200,
                    "currency": "USD"
                },
                challenges=[
                    {
                        "challenge_type": "data_availability",
                        "probability": 0.45,
                        "mitigation_strategies": [
                            "Start with available data",
                            "Use templates"
                        ]
                    }
                ]
            )
        ],
        similar_orgs_count=83
    )


@router.get("/certification/{org_id}", response_model=CertificationPredictionResponse)
async def get_certification_prediction(org_id: UUID):
    """
    Predict when organization will achieve certification

    Based on similar successful organizations
    """

    # Mock response
    from datetime import datetime, timedelta

    return CertificationPredictionResponse(
        predicted_certification_date=datetime.utcnow() + timedelta(days=240),
        months_remaining=8.0,
        success_probability=0.82,
        confidence=0.76,
        based_on_orgs_count=47,
        key_factors=[
            "Dedicated BCM team",
            "Executive sponsorship",
            "Regular progress reviews",
            "External expert guidance",
            "Compliance culture"
        ]
    )


@router.get("/recommendations/{org_id}", response_model=List[RecommendationResponse])
async def get_recommendations(
    org_id: UUID,
    days_ahead: int = Query(default=14, ge=7, le=30)
):
    """
    Get proactive recommendations for organization

    Returns upcoming milestones and suggested actions
    """

    # Mock response
    return [
        RecommendationResponse(
            type="milestone_approaching",
            priority="high",
            milestone="risk_assessment",
            days_until=7,
            confidence=0.87,
            actions=[
                "Review critical processes from BIA",
                "Gather historical incident data",
                "Schedule team kickoff meeting"
            ],
            resources=[
                {
                    "type": "template",
                    "name": "Risk Register Template",
                    "url": "/templates/risk"
                },
                {
                    "type": "video",
                    "name": "Risk Assessment Guide",
                    "url": "/learn/risk"
                }
            ]
        )
    ]


@router.get("/expert-demand", response_model=DemandForecastResponse)
async def get_expert_demand_forecast(
    horizon_days: int = Query(default=30, ge=7, le=90),
    specialty: Optional[str] = None
):
    """
    Get forecast of expert demand

    Used by specialists to see upcoming opportunities
    """

    # Mock response
    return DemandForecastResponse(
        forecast_date=datetime.utcnow(),
        horizon_days=horizon_days,
        total_predicted_projects=47,
        by_specialty={
            "bia": {
                "expected_projects": 12,
                "peak_week": "2025-10-18",
                "confidence": 0.84
            },
            "risk": {
                "expected_projects": 18,
                "peak_week": "2025-10-25",
                "confidence": 0.78
            },
            "planning": {
                "expected_projects": 17,
                "peak_week": "2025-11-01",
                "confidence": 0.72
            }
        },
        by_industry={
            "healthcare": 28,
            "finance": 12,
            "technology": 7
        }
    )


@router.get("/similar-organizations/{org_id}")
async def get_similar_organizations(
    org_id: UUID,
    limit: int = Query(default=10, le=50)
):
    """
    Get similar organizations (anonymized)

    Shows success stories from similar contexts
    """

    # Mock response
    return {
        "org_id": org_id,
        "similar_organizations": [
            {
                "industry": "healthcare",
                "size_category": "medium_200-500",
                "similarity_score": 0.89,
                "time_to_cert_months": 7.5,
                "success_rate": 0.95,
                "key_success_factors": [
                    "Phased implementation",
                    "Early expert engagement",
                    "Cross-functional team"
                ]
            }
        ],
        "count": 1,
        "avg_time_to_cert": 7.5,
        "avg_success_rate": 0.95
    }
