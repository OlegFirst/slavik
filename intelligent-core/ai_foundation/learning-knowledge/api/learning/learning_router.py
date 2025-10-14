"""
Learning API Router

Exercise results and scenario learning
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import get_db

# Add engines to path
engines_path = Path(__file__).parent.parent / "engines"
sys.path.insert(0, str(engines_path))

from pattern_detector import ScenarioAnalyzer

# Import models
models_path = Path(__file__).parent.parent / "models"
sys.path.insert(0, str(models_path))

from learning_models import ExerciseResult, ScenarioLearning

router = APIRouter()


# Pydantic schemas
class ExerciseResultCreate(BaseModel):
    """Create exercise result"""
    model_config = ConfigDict(from_attributes=True)

    tenant_id: Optional[str] = None
    twin_id: Optional[int] = None
    scenario_id: Optional[int] = None
    exercise_name: str
    exercise_type: str
    scenario_type: str
    overall_score: float
    response_time_minutes: Optional[int] = None
    communication_score: Optional[float] = None
    decision_quality_score: Optional[float] = None
    coordination_score: Optional[float] = None
    objectives_met: Optional[List[str]] = None
    objectives_missed: Optional[List[str]] = None
    key_issues: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    participant_count: Optional[int] = None
    roles_involved: Optional[List[str]] = None
    conducted_at: str


class ExerciseResultResponse(BaseModel):
    """Exercise result response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_name: str
    exercise_type: str
    scenario_type: str
    overall_score: float
    response_time_minutes: Optional[int]
    key_issues: Optional[List[str]]
    strengths: Optional[List[str]]
    conducted_at: str


class ScenarioLearningResponse(BaseModel):
    """Scenario learning response"""
    model_config = ConfigDict(from_attributes=True)

    scenario_type: str
    execution_count: int
    avg_score: Optional[float]
    avg_response_time: Optional[float]
    success_rate: Optional[float]
    common_failures: Optional[List[Dict[str, Any]]]
    common_strengths: Optional[List[Dict[str, Any]]]
    improvement_trend: Optional[float]
    recommended_improvements: Optional[List[str]]


# Scenario analyzer instance
analyzer = ScenarioAnalyzer()


@router.post("/results", response_model=ExerciseResultResponse, status_code=201)
async def create_exercise_result(
    result: ExerciseResultCreate,
    db: Session = Depends(get_db)
):
    """
    Record exercise result

    This feeds the learning system with new data
    """
    db_result = ExerciseResult(
        tenant_id=result.tenant_id,
        twin_id=result.twin_id,
        scenario_id=result.scenario_id,
        exercise_name=result.exercise_name,
        exercise_type=result.exercise_type,
        scenario_type=result.scenario_type,
        overall_score=result.overall_score,
        response_time_minutes=result.response_time_minutes,
        communication_score=result.communication_score,
        decision_quality_score=result.decision_quality_score,
        coordination_score=result.coordination_score,
        objectives_met=result.objectives_met,
        objectives_missed=result.objectives_missed,
        key_issues=result.key_issues,
        strengths=result.strengths,
        participant_count=result.participant_count,
        roles_involved=result.roles_involved,
        conducted_at=datetime.fromisoformat(result.conducted_at)
    )

    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return ExerciseResultResponse(
        id=db_result.id,
        exercise_name=db_result.exercise_name,
        exercise_type=db_result.exercise_type,
        scenario_type=db_result.scenario_type,
        overall_score=db_result.overall_score,
        response_time_minutes=db_result.response_time_minutes,
        key_issues=db_result.key_issues,
        strengths=db_result.strengths,
        conducted_at=db_result.conducted_at.isoformat()
    )


@router.get("/results", response_model=List[ExerciseResultResponse])
async def list_exercise_results(
    scenario_type: Optional[str] = None,
    twin_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List exercise results"""
    query = db.query(ExerciseResult)

    if scenario_type:
        query = query.filter(ExerciseResult.scenario_type == scenario_type)

    if twin_id:
        query = query.filter(ExerciseResult.twin_id == twin_id)

    results = query.order_by(desc(ExerciseResult.conducted_at)).limit(limit).all()

    return [
        ExerciseResultResponse(
            id=r.id,
            exercise_name=r.exercise_name,
            exercise_type=r.exercise_type,
            scenario_type=r.scenario_type,
            overall_score=r.overall_score,
            response_time_minutes=r.response_time_minutes,
            key_issues=r.key_issues,
            strengths=r.strengths,
            conducted_at=r.conducted_at.isoformat()
        )
        for r in results
    ]


@router.get("/scenarios/{scenario_type}", response_model=ScenarioLearningResponse)
async def get_scenario_learning(
    scenario_type: str,
    db: Session = Depends(get_db)
):
    """
    Get aggregated learning for a scenario type

    Analyzes all executions of this scenario and returns:
    - Performance metrics
    - Common issues/strengths
    - Improvement trends
    - Recommendations
    """

    # Get all results for this scenario type
    results = db.query(ExerciseResult).filter(
        ExerciseResult.scenario_type == scenario_type
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for scenario type: {scenario_type}")

    # Convert to dict for analyzer
    results_data = [
        {
            'scenario_type': r.scenario_type,
            'overall_score': r.overall_score,
            'response_time_minutes': r.response_time_minutes,
            'key_issues': r.key_issues or [],
            'strengths': r.strengths or [],
            'conducted_at': r.conducted_at
        }
        for r in results
    ]

    # Analyze scenario
    analysis = analyzer.analyze_scenario(scenario_type, results_data)

    # Check if ScenarioLearning record exists
    scenario_learning = db.query(ScenarioLearning).filter(
        ScenarioLearning.scenario_type == scenario_type
    ).first()

    if scenario_learning:
        # Update existing record
        scenario_learning.execution_count = analysis['execution_count']
        scenario_learning.avg_score = analysis['avg_score']
        scenario_learning.avg_response_time = analysis['avg_response_time']
        scenario_learning.success_rate = analysis['success_rate']
        scenario_learning.common_failures = analysis['common_failures']
        scenario_learning.common_strengths = analysis['common_strengths']
        scenario_learning.improvement_trends = {'trend': analysis['improvement_trend']}
        scenario_learning.recommended_improvements = analysis['recommended_improvements']
        scenario_learning.last_execution = analysis['last_execution']
    else:
        # Create new record
        scenario_learning = ScenarioLearning(
            scenario_type=scenario_type,
            execution_count=analysis['execution_count'],
            avg_score=analysis['avg_score'],
            avg_response_time=analysis['avg_response_time'],
            success_rate=analysis['success_rate'],
            common_failures=analysis['common_failures'],
            common_strengths=analysis['common_strengths'],
            improvement_trends={'trend': analysis['improvement_trend']},
            recommended_improvements=analysis['recommended_improvements'],
            first_execution=analysis['first_execution'],
            last_execution=analysis['last_execution']
        )
        db.add(scenario_learning)

    db.commit()

    return ScenarioLearningResponse(
        scenario_type=scenario_type,
        execution_count=analysis['execution_count'],
        avg_score=analysis['avg_score'],
        avg_response_time=analysis['avg_response_time'],
        success_rate=analysis['success_rate'],
        common_failures=analysis['common_failures'],
        common_strengths=analysis['common_strengths'],
        improvement_trend=analysis['improvement_trend'],
        recommended_improvements=analysis['recommended_improvements']
    )


@router.get("/scenarios", response_model=List[str])
async def list_scenario_types(db: Session = Depends(get_db)):
    """List all scenario types with learning data"""
    scenario_types = db.query(ExerciseResult.scenario_type).distinct().all()

    return [st[0] for st in scenario_types]


@router.get("/stats")
async def get_learning_stats(db: Session = Depends(get_db)):
    """Get overall learning system statistics"""

    total_exercises = db.query(func.count(ExerciseResult.id)).scalar()
    total_scenarios = db.query(func.count(ScenarioLearning.id)).scalar()

    avg_score = db.query(func.avg(ExerciseResult.overall_score)).scalar()

    recent_exercises = db.query(ExerciseResult).filter(
        ExerciseResult.conducted_at >= datetime.utcnow() - timedelta(days=30)
    ).count()

    return {
        "total_exercises": total_exercises,
        "total_scenario_types": total_scenarios,
        "average_score": round(avg_score, 2) if avg_score else 0,
        "recent_exercises_30d": recent_exercises
    }
