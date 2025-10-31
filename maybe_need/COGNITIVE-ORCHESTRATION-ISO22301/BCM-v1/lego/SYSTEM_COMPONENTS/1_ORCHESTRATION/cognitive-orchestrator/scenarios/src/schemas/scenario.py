# -*- coding: utf-8 -*-
"""Scenario schemas for AI Orchestrator"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ScenarioGenerateRequest(BaseModel):
    """Request model for scenario generation"""
    company_id: str
    scenario_type: str = Field(..., description="Type of scenario to generate")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class ScenarioGenerateResponse(BaseModel):
    """Response model for scenario generation"""
    scenario_id: str
    title: str
    description: str
    scenario_data: Dict[str, Any]
    generation_time: datetime
    confidence_score: float

class ScenarioAnalyzeRequest(BaseModel):
    """Request model for scenario analysis"""
    scenario_id: str
    company_context: Dict[str, Any]
    analysis_depth: str = Field(default="standard", description="deep, standard, or quick")
    focus_areas: List[str] = Field(default_factory=list)
    
class ScenarioAnalyzeResponse(BaseModel):
    """Response model for scenario analysis"""
    scenario_id: str
    effectiveness_scores: Dict[str, float]
    identified_gaps: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    analysis_timestamp: datetime
    next_review_date: datetime

class ScenarioOptimizeRequest(BaseModel):
    """Request model for scenario optimization"""
    scenario_id: str
    test_results: Dict[str, Any]
    feedback: List[Dict[str, Any]]
    optimization_goals: List[str]
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class ScenarioOptimizeResponse(BaseModel):
    """Response model for scenario optimization"""
    scenario_id: str
    optimized_scenario: Dict[str, Any]
    improvement_metrics: Dict[str, float]
    optimization_timestamp: datetime
    version: int

class ScenarioRecommendRequest(BaseModel):
    """Request model for scenario recommendations"""
    company_id: str
    industry: str
    company_size: str
    risk_profile: Dict[str, Any]
    existing_scenarios: List[str] = Field(default_factory=list)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class ScenarioRecommendResponse(BaseModel):
    """Response model for scenario recommendations"""
    company_id: str
    recommended_scenarios: List[Dict[str, Any]]
    recommendation_basis: List[str]
    timestamp: datetime
