"""
Scenario Models - Data models for scenario orchestration
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ScenarioGenerationRequest(BaseModel):
    """Request to generate BCM scenario"""
    category: str = Field(..., description="Scenario category: epidemic, blackout, cyber, supply, natural, terrorism")
    complexity: int = Field(default=3, ge=1, le=5, description="Complexity level 1-5")
    duration_hours: int = Field(default=4, description="Exercise duration in hours")
    participants: int = Field(default=10, description="Number of participants")
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems")
    custom_objectives: List[str] = Field(default_factory=list, description="Custom objectives")
    organization_context: Optional[str] = Field(None, description="Organization context")


class Scenario(BaseModel):
    """Generated BCM scenario"""
    id: str
    title: str
    category: str
    level: str  # tabletop, full
    meta_duration: int
    meta_participants: int
    content_md: str
    is_ai_generated: bool = Field(default=False)
    ai_generation_params: Optional[Dict[str, Any]] = None
    jaamsim_config: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExerciseResult(BaseModel):
    """Exercise completion result for learning"""
    exercise_id: str
    scenario_id: str
    template_id: str
    exercise_type: str
    duration_actual_hours: float
    participants_count: int
    success_metrics: Dict[str, Any] = Field(default_factory=dict)
    participant_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    simulation_metrics: Optional[Dict[str, Any]] = None
    lessons_learned: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    effectiveness_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Effectiveness score 0-10")
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class ScenarioLearning(BaseModel):
    """Learning data accumulated for scenario improvement"""
    scenario_id: str
    total_uses: int
    avg_effectiveness: float
    common_issues: List[str] = Field(default_factory=list)
    success_patterns: List[str] = Field(default_factory=list)
    improvement_recommendations: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)