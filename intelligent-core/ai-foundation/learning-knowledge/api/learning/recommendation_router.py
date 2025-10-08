"""
Recommendation API Router

AI-powered recommendations based on learning
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import get_db

# Import models
models_path = Path(__file__).parent.parent / "models"
sys.path.insert(0, str(models_path))

from learning_models import ExerciseResult, Pattern, ScenarioLearning

router = APIRouter()


# Pydantic schemas
class RecommendationResponse(BaseModel):
    """Recommendation response"""
    model_config = ConfigDict(from_attributes=True)

    recommendation_type: str
    priority: str
    title: str
    description: str
    rationale: str
    actions: List[str]
    confidence: float


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    twin_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered recommendations based on learning

    Combines:
    - Detected patterns
    - Exercise performance
    - Scenario learning

    Returns prioritized actionable recommendations
    """
    recommendations = []

    # Get active high-severity patterns
    critical_patterns = db.query(Pattern).filter(
        Pattern.is_active == True,
        Pattern.severity.in_(['critical', 'high']),
        Pattern.is_acknowledged == False
    ).order_by(desc(Pattern.confidence)).limit(5).all()

    for pattern in critical_patterns:
        recommendations.append(RecommendationResponse(
            recommendation_type="pattern_based",
            priority=pattern.severity,
            title=f"Address {pattern.pattern_type}: {pattern.pattern_name}",
            description=pattern.description,
            rationale=f"Detected in {pattern.occurrence_count} occurrences with {pattern.confidence*100:.0f}% confidence",
            actions=pattern.recommended_actions or [],
            confidence=pattern.confidence
        ))

    # Get recent poor-performing exercises
    recent_date = datetime.utcnow() - timedelta(days=30)
    poor_exercises = db.query(ExerciseResult).filter(
        ExerciseResult.conducted_at >= recent_date,
        ExerciseResult.overall_score < 70
    )

    if twin_id:
        poor_exercises = poor_exercises.filter(ExerciseResult.twin_id == twin_id)

    poor_exercises = poor_exercises.order_by(desc(ExerciseResult.conducted_at)).limit(3).all()

    for exercise in poor_exercises:
        if exercise.key_issues:
            recommendations.append(RecommendationResponse(
                recommendation_type="performance_based",
                priority="high",
                title=f"Improve {exercise.scenario_type} scenario performance",
                description=f"Recent exercise '{exercise.exercise_name}' scored {exercise.overall_score}/100",
                rationale=f"Score below acceptable threshold. Key issues: {', '.join(exercise.key_issues[:2])}",
                actions=[
                    f"Focus training on {exercise.scenario_type} scenarios",
                    f"Address issue: {exercise.key_issues[0]}" if exercise.key_issues else "Review exercise debrief",
                    "Schedule follow-up exercise"
                ],
                confidence=0.8
            ))

    # Get scenario-specific recommendations
    scenarios_with_learning = db.query(ScenarioLearning).filter(
        ScenarioLearning.success_rate < 75
    ).order_by(ScenarioLearning.avg_score).limit(3).all()

    for scenario in scenarios_with_learning:
        if scenario.recommended_improvements:
            recommendations.append(RecommendationResponse(
                recommendation_type="scenario_based",
                priority="medium",
                title=f"Improve {scenario.scenario_type} scenario readiness",
                description=f"Success rate: {scenario.success_rate:.1f}% (avg score: {scenario.avg_score:.1f})",
                rationale=f"Based on {scenario.execution_count} executions, performance needs improvement",
                actions=scenario.recommended_improvements,
                confidence=0.75
            ))

    # Sort by priority and confidence
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    recommendations.sort(
        key=lambda x: (priority_order.get(x.priority, 4), -x.confidence)
    )

    return recommendations[:limit]


@router.get("/training")
async def get_training_recommendations(
    twin_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get training-specific recommendations

    Analyzes skill gaps and recommends training priorities
    """
    training_needs = []

    # Analyze common issues across exercises
    recent_date = datetime.utcnow() - timedelta(days=90)
    recent_exercises = db.query(ExerciseResult).filter(
        ExerciseResult.conducted_at >= recent_date
    )

    if twin_id:
        recent_exercises = recent_exercises.filter(ExerciseResult.twin_id == twin_id)

    recent_exercises = recent_exercises.all()

    # Count issue frequency
    from collections import Counter
    all_issues = []
    for ex in recent_exercises:
        if ex.key_issues:
            all_issues.extend(ex.key_issues)

    issue_counts = Counter(all_issues)

    # Generate training recommendations
    for issue, count in issue_counts.most_common(5):
        training_needs.append({
            "topic": issue,
            "priority": "high" if count >= len(recent_exercises) * 0.5 else "medium",
            "frequency": count,
            "total_exercises": len(recent_exercises),
            "occurrence_rate": (count / len(recent_exercises)) * 100 if recent_exercises else 0,
            "suggested_format": "Workshop" if count >= 5 else "E-learning module"
        })

    return {
        "training_needs": training_needs,
        "analysis_period": "last_90_days",
        "exercises_analyzed": len(recent_exercises)
    }


@router.get("/next-exercise")
async def recommend_next_exercise(
    twin_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Recommend next exercise based on learning gaps

    Suggests scenario type and complexity based on:
    - Recent performance
    - Identified weaknesses
    - Time since last exercise
    """

    # Analyze recent exercise history
    recent_exercises = db.query(ExerciseResult).filter(
        ExerciseResult.conducted_at >= datetime.utcnow() - timedelta(days=180)
    )

    if twin_id:
        recent_exercises = recent_exercises.filter(ExerciseResult.twin_id == twin_id)

    recent_exercises = recent_exercises.all()

    if not recent_exercises:
        return {
            "recommended_scenario": "cyber_incident",
            "recommended_complexity": "Beginner",
            "rationale": "No exercise history - starting with common scenario",
            "objectives": [
                "Establish baseline competency",
                "Familiarize team with exercise format",
                "Identify initial training needs"
            ]
        }

    # Find scenario types with poor performance
    from collections import defaultdict
    scenario_scores = defaultdict(list)

    for ex in recent_exercises:
        scenario_scores[ex.scenario_type].append(ex.overall_score)

    # Calculate average scores
    scenario_avg = {
        st: sum(scores) / len(scores)
        for st, scores in scenario_scores.items()
    }

    # Find weakest scenario
    weakest_scenario = min(scenario_avg.items(), key=lambda x: x[1])

    # Determine complexity based on performance
    avg_score = weakest_scenario[1]
    if avg_score < 60:
        complexity = "Beginner"
    elif avg_score < 75:
        complexity = "Intermediate"
    else:
        complexity = "Advanced"

    return {
        "recommended_scenario": weakest_scenario[0],
        "recommended_complexity": complexity,
        "rationale": f"Current avg score for {weakest_scenario[0]}: {avg_score:.1f} - needs improvement",
        "objectives": [
            f"Improve {weakest_scenario[0]} response capability",
            "Address identified weaknesses",
            "Validate improvements since last exercise"
        ],
        "recent_performance": {
            "scenario": weakest_scenario[0],
            "avg_score": round(avg_score, 1),
            "exercise_count": len(scenario_scores[weakest_scenario[0]])
        }
    }
