"""
Scenario Orchestrator Request/Response Schemas
===============================================

Schemas for integration with Scenario Orchestrator service.
Extracted from: /scenarios/scenario_orchestrator/src/schemas/scenario.py

These schemas define the contracts for:
- Scenario generation
- Scenario analysis
- Scenario optimization
- Scenario recommendations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ========================================================================
# SCENARIO GENERATION
# ========================================================================

class ScenarioGenerateRequest(BaseModel):
    """
    Request model for AI-powered scenario generation

    Used to request scenario generation from Scenario Orchestrator service.
    """
    company_id: str = Field(..., description="Company/Organization ID")
    scenario_type: str = Field(..., description="Type of scenario to generate")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context for generation"
    )

    # Extended fields for Simulation Service
    complexity: Optional[int] = Field(
        default=3,
        ge=1,
        le=5,
        description="Complexity level (1-5)"
    )
    duration_hours: Optional[int] = Field(
        default=4,
        description="Exercise duration in hours"
    )
    participants: Optional[int] = Field(
        default=10,
        description="Number of participants"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "org_456",
                "scenario_type": "cyber",
                "context": {
                    "industry": "healthcare",
                    "size": "large",
                    "existing_plans": ["DR_PLAN_01"]
                },
                "complexity": 4,
                "duration_hours": 6,
                "participants": 20
            }
        }


class ScenarioGenerateResponse(BaseModel):
    """
    Response model for scenario generation

    Contains the generated scenario data and metadata.
    """
    scenario_id: str = Field(..., description="Generated scenario ID")
    title: str = Field(..., description="Scenario title")
    description: str = Field(..., description="Scenario description")
    scenario_data: Dict[str, Any] = Field(
        ...,
        description="Complete scenario data"
    )
    generation_time: datetime = Field(
        ...,
        description="When scenario was generated"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence in generated scenario"
    )

    # Optional fields
    jaamsim_config: Optional[str] = Field(
        default=None,
        description="JaamSim configuration (if complexity >= 4)"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Path to saved scenario file"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scen_abc123",
                "title": "Hospital Ransomware Attack",
                "description": "Critical systems encrypted...",
                "scenario_data": {
                    "category": "cyber",
                    "complexity": 4,
                    "incidents": [...]
                },
                "generation_time": "2025-10-13T10:00:00Z",
                "confidence_score": 0.92,
                "jaamsim_config": "RecordEdits\n..."
            }
        }


# ========================================================================
# SCENARIO ANALYSIS
# ========================================================================

class ScenarioAnalyzeRequest(BaseModel):
    """
    Request model for scenario analysis

    Used to analyze scenario effectiveness and identify gaps.
    """
    scenario_id: str = Field(..., description="Scenario ID to analyze")
    company_context: Dict[str, Any] = Field(
        ...,
        description="Company context for analysis"
    )
    analysis_depth: str = Field(
        default="standard",
        description="Analysis depth: quick, standard, or deep"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Specific areas to focus analysis on"
    )

    # Optional simulation results for post-exercise analysis
    simulation_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Simulation results to include in analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scen_abc123",
                "company_context": {
                    "industry": "healthcare",
                    "size": "large",
                    "risk_profile": "high"
                },
                "analysis_depth": "deep",
                "focus_areas": ["rto_compliance", "communication", "decision_making"]
            }
        }


class ScenarioAnalyzeResponse(BaseModel):
    """
    Response model for scenario analysis

    Contains analysis results, gaps, and recommendations.
    """
    scenario_id: str = Field(..., description="Analyzed scenario ID")
    effectiveness_scores: Dict[str, float] = Field(
        ...,
        description="Effectiveness scores by area"
    )
    identified_gaps: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Identified gaps and weaknesses"
    )
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="AI-generated recommendations"
    )
    analysis_timestamp: datetime = Field(
        ...,
        description="When analysis was performed"
    )
    next_review_date: datetime = Field(
        ...,
        description="Recommended next review date"
    )

    # Additional analysis metadata
    analysis_depth_used: Optional[str] = Field(
        default=None,
        description="Actual analysis depth used"
    )
    confidence_level: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in analysis results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scen_abc123",
                "effectiveness_scores": {
                    "rto_compliance": 0.85,
                    "communication": 0.72,
                    "decision_making": 0.90
                },
                "identified_gaps": [
                    {
                        "area": "communication",
                        "severity": "medium",
                        "description": "Delayed notifications to stakeholders"
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Implement automated notification system",
                        "expected_impact": "Reduce notification time by 60%"
                    }
                ],
                "analysis_timestamp": "2025-10-13T10:30:00Z",
                "next_review_date": "2025-11-13T10:30:00Z"
            }
        }


# ========================================================================
# SCENARIO OPTIMIZATION
# ========================================================================

class ScenarioOptimizeRequest(BaseModel):
    """
    Request model for scenario optimization

    Used to optimize scenario based on test results and feedback.
    """
    scenario_id: str = Field(..., description="Scenario ID to optimize")
    test_results: Dict[str, Any] = Field(
        ...,
        description="Test/simulation results"
    )
    feedback: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Participant and observer feedback"
    )
    optimization_goals: List[str] = Field(
        ...,
        description="Optimization goals (e.g., 'improve_realism', 'reduce_duration')"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Constraints for optimization"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scen_abc123",
                "test_results": {
                    "effectiveness_score": 7.5,
                    "participant_satisfaction": 8.2,
                    "duration_actual": 4.5,
                    "issues_encountered": ["timing_too_fast", "unclear_objectives"]
                },
                "feedback": [
                    {
                        "participant_id": "user_123",
                        "rating": 8,
                        "comments": "Good scenario but timing was too fast"
                    }
                ],
                "optimization_goals": [
                    "improve_timing",
                    "clarify_objectives",
                    "increase_realism"
                ],
                "constraints": {
                    "max_duration": 6,
                    "min_participants": 8
                }
            }
        }


class ScenarioOptimizeResponse(BaseModel):
    """
    Response model for scenario optimization

    Contains optimized scenario and improvement metrics.
    """
    scenario_id: str = Field(..., description="Optimized scenario ID")
    optimized_scenario: Dict[str, Any] = Field(
        ...,
        description="Optimized scenario data"
    )
    improvement_metrics: Dict[str, float] = Field(
        ...,
        description="Improvement metrics (before vs after)"
    )
    optimization_timestamp: datetime = Field(
        ...,
        description="When optimization was performed"
    )
    version: int = Field(
        ...,
        description="Scenario version number"
    )

    # Changes made
    changes_summary: Optional[List[str]] = Field(
        default_factory=list,
        description="Summary of changes made"
    )
    expected_improvements: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Expected improvements from changes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scen_abc123",
                "optimized_scenario": {
                    "version": 2,
                    "duration_minutes": 300,
                    "objectives": ["Improved objective 1", "Improved objective 2"]
                },
                "improvement_metrics": {
                    "timing_improvement": 0.25,
                    "clarity_improvement": 0.40,
                    "realism_improvement": 0.15
                },
                "optimization_timestamp": "2025-10-13T11:00:00Z",
                "version": 2,
                "changes_summary": [
                    "Extended duration by 60 minutes",
                    "Clarified objectives",
                    "Added intermediate checkpoints"
                ]
            }
        }


# ========================================================================
# SCENARIO RECOMMENDATIONS
# ========================================================================

class ScenarioRecommendRequest(BaseModel):
    """
    Request model for scenario recommendations

    Used to get AI recommendations for suitable scenarios.
    """
    company_id: str = Field(..., description="Company/Organization ID")
    industry: str = Field(..., description="Company industry")
    company_size: str = Field(..., description="Company size (small/medium/large)")
    risk_profile: Dict[str, Any] = Field(
        ...,
        description="Company risk profile"
    )
    existing_scenarios: List[str] = Field(
        default_factory=list,
        description="IDs of scenarios already used"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Company preferences for scenarios"
    )

    # Additional context
    compliance_requirements: Optional[List[str]] = Field(
        default_factory=list,
        description="Compliance standards to meet (e.g., ISO 22301)"
    )
    focus_areas: Optional[List[str]] = Field(
        default_factory=list,
        description="Areas of focus (e.g., 'cyber', 'supply_chain')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "org_456",
                "industry": "healthcare",
                "company_size": "large",
                "risk_profile": {
                    "cyber_risk": "high",
                    "operational_risk": "medium",
                    "natural_disaster_risk": "low"
                },
                "existing_scenarios": ["scen_001", "scen_002"],
                "compliance_requirements": ["ISO_22301", "HIPAA"],
                "focus_areas": ["cyber", "pandemic"]
            }
        }


class ScenarioRecommendResponse(BaseModel):
    """
    Response model for scenario recommendations

    Contains recommended scenarios with rationale.
    """
    company_id: str = Field(..., description="Company ID")
    recommended_scenarios: List[Dict[str, Any]] = Field(
        ...,
        description="List of recommended scenarios with details"
    )
    recommendation_basis: List[str] = Field(
        ...,
        description="Basis for recommendations"
    )
    timestamp: datetime = Field(
        ...,
        description="When recommendations were generated"
    )

    # Additional metadata
    confidence_scores: Optional[Dict[str, float]] = Field(
        default_factory=dict,
        description="Confidence scores for each recommendation"
    )
    priority_order: Optional[List[str]] = Field(
        default_factory=list,
        description="Recommended order of execution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "org_456",
                "recommended_scenarios": [
                    {
                        "scenario_id": "scen_ransomware_01",
                        "title": "Hospital Ransomware Attack",
                        "category": "cyber",
                        "complexity": 4,
                        "estimated_duration": 6,
                        "rationale": "High cyber risk, healthcare industry focus"
                    },
                    {
                        "scenario_id": "scen_pandemic_01",
                        "title": "Pandemic Response Exercise",
                        "category": "pandemic",
                        "complexity": 3,
                        "estimated_duration": 4,
                        "rationale": "Healthcare relevance, current risk landscape"
                    }
                ],
                "recommendation_basis": [
                    "Industry-specific risks",
                    "Current threat landscape",
                    "Compliance requirements",
                    "Gap analysis results"
                ],
                "timestamp": "2025-10-13T12:00:00Z",
                "confidence_scores": {
                    "scen_ransomware_01": 0.92,
                    "scen_pandemic_01": 0.88
                },
                "priority_order": ["scen_ransomware_01", "scen_pandemic_01"]
            }
        }
