# -*- coding: utf-8 -*-
"""Scenario AI Orchestrator Endpoints"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
import json
import asyncio
from uuid import uuid4

from app.core.security import get_current_user
from app.core.ai_engine import AIEngine
from app.core.database import get_db
from app.models import Scenario
from app.schemas.scenario import (
    ScenarioGenerateRequest,
    ScenarioGenerateResponse,
    ScenarioAnalyzeRequest,
    ScenarioAnalyzeResponse,
    ScenarioOptimizeRequest,
    ScenarioOptimizeResponse,
    ScenarioRecommendRequest,
    ScenarioRecommendResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

ai_engine = AIEngine()

class ScenarioGenerationConfig(BaseModel):
    """Configuration for scenario generation"""
    industry: str
    company_size: str
    risk_level: str
    complexity: str = Field(default="medium", description="Scenario complexity level")
    use_historical_data: bool = Field(default=True)
    include_mitigation: bool = Field(default=True)
    language: str = Field(default="en")
    
class ScenarioTestConfig(BaseModel):
    """Configuration for scenario testing"""
    test_type: str = Field(..., description="Type of test: simulation, tabletop, full")
    duration_hours: int = Field(default=2)
    participants: List[str] = Field(default_factory=list)
    objectives: List[str] = Field(default_factory=list)
    evaluation_criteria: Dict[str, Any] = Field(default_factory=dict)

@router.post("/generate", response_model=ScenarioGenerateResponse)
async def generate_scenario(
    request: ScenarioGenerateRequest,
    config: ScenarioGenerationConfig = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Generate BCM scenarios using AI based on company profile and risk assessment
    """
    try:
        # Prepare context for AI generation
        context = {
            "company_id": request.company_id,
            "industry": config.industry,
            "company_size": config.company_size,
            "risk_level": config.risk_level,
            "complexity": config.complexity,
            "scenario_type": request.scenario_type,
            "historical_incidents": [],
            "regulatory_requirements": []
        }
        
        # Fetch historical data if requested
        if config.use_historical_data:
            context["historical_incidents"] = await _fetch_historical_incidents(
                db, request.company_id
            )
            
        # Generate scenario using AI
        scenario_data = await ai_engine.generate_bcm_scenario(context)
        
        # Add mitigation strategies if requested
        if config.include_mitigation:
            mitigation_data = await ai_engine.generate_mitigation_strategies(
                scenario_data
            )
            scenario_data["mitigation_strategies"] = mitigation_data
            
        # Save to database
        scenario = Scenario(
            id=str(uuid4()),
            company_id=request.company_id,
            title=scenario_data["title"],
            description=scenario_data["description"],
            scenario_type=request.scenario_type,
            risk_level=config.risk_level,
            data=scenario_data,
            created_by=current_user["user_id"],
            created_at=datetime.utcnow()
        )
        
        await db.save(scenario)
        
        return ScenarioGenerateResponse(
            scenario_id=scenario.id,
            title=scenario.title,
            description=scenario.description,
            scenario_data=scenario_data,
            generation_time=datetime.utcnow(),
            confidence_score=scenario_data.get("confidence_score", 0.85)
        )
        
    except Exception as e:
        logger.error(f"Error generating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=ScenarioAnalyzeResponse)
async def analyze_scenario(
    request: ScenarioAnalyzeRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analyze existing BCM scenario for effectiveness and gaps
    """
    try:
        # Fetch scenario from database
        scenario = await db.get(Scenario, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
            
        # Perform AI analysis
        analysis_result = await ai_engine.analyze_bcm_scenario({
            "scenario": scenario.data,
            "company_context": request.company_context,
            "analysis_depth": request.analysis_depth,
            "focus_areas": request.focus_areas
        })
        
        # Calculate effectiveness scores
        effectiveness_scores = {
            "overall": analysis_result.get("overall_score", 0),
            "response_readiness": analysis_result.get("response_readiness", 0),
            "recovery_capability": analysis_result.get("recovery_capability", 0),
            "communication_clarity": analysis_result.get("communication_clarity", 0),
            "resource_adequacy": analysis_result.get("resource_adequacy", 0)
        }
        
        # Identify gaps and recommendations
        gaps = analysis_result.get("identified_gaps", [])
        recommendations = analysis_result.get("recommendations", [])
        
        return ScenarioAnalyzeResponse(
            scenario_id=request.scenario_id,
            effectiveness_scores=effectiveness_scores,
            identified_gaps=gaps,
            recommendations=recommendations,
            analysis_timestamp=datetime.utcnow(),
            next_review_date=datetime.utcnow() + timedelta(days=90)
        )
        
    except Exception as e:
        logger.error(f"Error analyzing scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize", response_model=ScenarioOptimizeResponse)
async def optimize_scenario(
    request: ScenarioOptimizeRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Optimize BCM scenario based on test results and feedback
    """
    try:
        # Fetch scenario
        scenario = await db.get(Scenario, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
            
        # Prepare optimization context
        optimization_context = {
            "scenario": scenario.data,
            "test_results": request.test_results,
            "feedback": request.feedback,
            "optimization_goals": request.optimization_goals,
            "constraints": request.constraints
        }
        
        # Perform AI optimization
        optimized_scenario = await ai_engine.optimize_bcm_scenario(
            optimization_context
        )
        
        # Calculate improvement metrics
        improvement_metrics = {
            "response_time_reduction": optimized_scenario.get("response_time_reduction", 0),
            "recovery_time_improvement": optimized_scenario.get("recovery_time_improvement", 0),
            "cost_optimization": optimized_scenario.get("cost_optimization", 0),
            "resource_efficiency": optimized_scenario.get("resource_efficiency", 0)
        }
        
        # Update scenario in database
        scenario.data = optimized_scenario["scenario_data"]
        scenario.updated_at = datetime.utcnow()
        scenario.version += 1
        await db.save(scenario)
        
        return ScenarioOptimizeResponse(
            scenario_id=request.scenario_id,
            optimized_scenario=optimized_scenario["scenario_data"],
            improvement_metrics=improvement_metrics,
            optimization_timestamp=datetime.utcnow(),
            version=scenario.version
        )
        
    except Exception as e:
        logger.error(f"Error optimizing scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend", response_model=ScenarioRecommendResponse)
async def recommend_scenarios(
    request: ScenarioRecommendRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Recommend relevant BCM scenarios from the hub based on company profile
    """
    try:
        # Prepare recommendation context
        context = {
            "company_id": request.company_id,
            "industry": request.industry,
            "company_size": request.company_size,
            "risk_profile": request.risk_profile,
            "existing_scenarios": request.existing_scenarios,
            "preferences": request.preferences
        }
        
        # Get AI recommendations
        recommendations = await ai_engine.recommend_bcm_scenarios(context)
        
        # Fetch recommended scenarios from hub
        recommended_scenarios = []
        for rec in recommendations["scenarios"]:
            scenario = await db.get(Scenario, rec["scenario_id"])
            if scenario:
                recommended_scenarios.append({
                    "scenario_id": scenario.id,
                    "title": scenario.title,
                    "description": scenario.description,
                    "relevance_score": rec["relevance_score"],
                    "reason": rec["recommendation_reason"],
                    "adaptation_required": rec.get("adaptation_required", False),
                    "estimated_implementation_time": rec.get("implementation_time", "2-4 weeks")
                })
                
        return ScenarioRecommendResponse(
            company_id=request.company_id,
            recommended_scenarios=recommended_scenarios,
            recommendation_basis=recommendations.get("basis", []),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error recommending scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/simulate")
async def simulate_scenario_test(
    scenario_id: str,
    test_config: ScenarioTestConfig,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Simulate BCM scenario test execution
    """
    try:
        # Fetch scenario
        scenario = await db.get(Scenario, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
            
        # Prepare simulation context
        simulation_context = {
            "scenario": scenario.data,
            "test_type": test_config.test_type,
            "duration": test_config.duration_hours,
            "participants": test_config.participants,
            "objectives": test_config.objectives,
            "evaluation_criteria": test_config.evaluation_criteria
        }
        
        # Run AI simulation
        simulation_result = await ai_engine.simulate_scenario_test(
            simulation_context
        )
        
        # Generate test report
        test_report = {
            "scenario_id": scenario_id,
            "test_id": str(uuid4()),
            "test_type": test_config.test_type,
            "execution_date": datetime.utcnow(),
            "duration_hours": test_config.duration_hours,
            "participants": test_config.participants,
            "results": simulation_result["results"],
            "performance_metrics": simulation_result["metrics"],
            "identified_issues": simulation_result.get("issues", []),
            "lessons_learned": simulation_result.get("lessons_learned", []),
            "recommendations": simulation_result.get("recommendations", []),
            "overall_score": simulation_result.get("overall_score", 0)
        }
        
        # Save test report
        await db.save_test_report(test_report)
        
        return {
            "test_id": test_report["test_id"],
            "scenario_id": scenario_id,
            "test_report": test_report,
            "status": "completed",
            "next_steps": simulation_result.get("next_steps", [])
        }
        
    except Exception as e:
        logger.error(f"Error simulating scenario test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hub/catalog")
async def get_scenario_catalog(
    industry: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    scenario_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get catalog of available scenarios from the hub
    """
    try:
        # Build filter criteria
        filters = {}
        if industry:
            filters["industry"] = industry
        if risk_level:
            filters["risk_level"] = risk_level
        if scenario_type:
            filters["scenario_type"] = scenario_type
            
        # Fetch scenarios from hub
        scenarios = await db.get_hub_scenarios(
            filters=filters,
            page=page,
            page_size=page_size
        )
        
        # Format response
        catalog = []
        for scenario in scenarios["items"]:
            catalog.append({
                "scenario_id": scenario.id,
                "title": scenario.title,
                "description": scenario.description,
                "industry": scenario.industry,
                "risk_level": scenario.risk_level,
                "scenario_type": scenario.scenario_type,
                "rating": scenario.rating,
                "usage_count": scenario.usage_count,
                "last_updated": scenario.updated_at,
                "tags": scenario.tags,
                "is_certified": scenario.is_certified
            })
            
        return {
            "catalog": catalog,
            "total": scenarios["total"],
            "page": page,
            "page_size": page_size,
            "total_pages": (scenarios["total"] + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"Error fetching scenario catalog: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hub/submit")
async def submit_scenario_to_hub(
    scenario_id: str,
    title: str = Body(...),
    description: str = Body(...),
    tags: List[str] = Body(default=[]),
    is_public: bool = Body(default=False),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Submit a scenario to the BCM hub for sharing
    """
    try:
        # Fetch scenario
        scenario = await db.get(Scenario, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
            
        # Validate scenario quality
        validation_result = await ai_engine.validate_scenario_quality(
            scenario.data
        )
        
        if validation_result["quality_score"] < 0.7:
            raise HTTPException(
                status_code=400,
                detail=f"Scenario quality too low: {validation_result['issues']}"
            )
            
        # Submit to hub
        hub_submission = {
            "scenario_id": scenario_id,
            "title": title,
            "description": description,
            "scenario_data": scenario.data,
            "tags": tags,
            "is_public": is_public,
            "submitted_by": current_user["user_id"],
            "submission_date": datetime.utcnow(),
            "quality_score": validation_result["quality_score"],
            "status": "pending_review"
        }
        
        await db.submit_to_hub(hub_submission)
        
        return {
            "submission_id": str(uuid4()),
            "scenario_id": scenario_id,
            "status": "pending_review",
            "quality_score": validation_result["quality_score"],
            "estimated_review_time": "24-48 hours"
        }
        
    except Exception as e:
        logger.error(f"Error submitting scenario to hub: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _fetch_historical_incidents(db, company_id: str) -> List[Dict]:
    """Fetch historical incidents for context"""
    try:
        incidents = await db.get_company_incidents(company_id, limit=10)
        return [
            {
                "type": inc.incident_type,
                "severity": inc.severity,
                "impact": inc.impact,
                "resolution_time": inc.resolution_time,
                "lessons_learned": inc.lessons_learned
            }
            for inc in incidents
        ]
    except Exception:
        return []
