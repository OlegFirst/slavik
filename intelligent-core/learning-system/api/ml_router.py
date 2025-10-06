"""
ML Predictions API Router

Endpoints for success prediction, difficulty adjustment, personalized recommendations
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from engines.ml_predictor import (
    ExerciseSuccessPredictor,
    DifficultyAdjuster,
    PersonalizedPathRecommender,
    AnomalyDetector
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines
success_predictor = ExerciseSuccessPredictor()
difficulty_adjuster = DifficultyAdjuster()
path_recommender = PersonalizedPathRecommender()
anomaly_detector = AnomalyDetector()


# =====================================================
# Request/Response Models
# =====================================================

class HistoricalResult(BaseModel):
    """Historical exercise result"""
    scenario_type: str
    overall_score: float
    conducted_at: datetime


class SuccessPredictionRequest(BaseModel):
    """Request for exercise success prediction"""
    scenario_type: str
    team_competency: float
    preparation_days: int
    historical_results: List[HistoricalResult]


class DifficultyAdjustmentRequest(BaseModel):
    """Request for difficulty adjustment"""
    current_difficulty: float
    recent_scores: List[float]
    target_score: Optional[float] = 72.5


class PathRecommendationRequest(BaseModel):
    """Request for personalized path recommendation"""
    user_id: str
    competencies: dict
    avg_score: float
    completed_paths: List[dict] = []


class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection"""
    exercise_results: List[dict]


# =====================================================
# Endpoints
# =====================================================

@router.post("/predict/success")
async def predict_exercise_success(request: SuccessPredictionRequest):
    """
    Predict exercise success probability

    Features:
    - Team competency
    - Preparation time
    - Historical performance
    - Scenario complexity

    Returns:
    - Predicted score
    - Success probability
    - Confidence interval
    - Recommendations
    """
    try:
        # Convert to dict
        historical_dict = [r.dict() for r in request.historical_results]

        # Predict
        prediction = success_predictor.predict_success(
            scenario_type=request.scenario_type,
            team_competency=request.team_competency,
            preparation_days=request.preparation_days,
            historical_results=historical_dict
        )

        return prediction

    except Exception as e:
        logger.error(f"Error predicting exercise success: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/difficulty/adjust")
async def adjust_scenario_difficulty(request: DifficultyAdjustmentRequest):
    """
    Adjust scenario difficulty based on performance

    Uses RL-inspired approach:
    - Optimal zone: 65-80% score
    - Auto-adjusts to maintain challenge
    """
    try:
        adjustment = difficulty_adjuster.adjust_difficulty(
            current_difficulty=request.current_difficulty,
            recent_scores=request.recent_scores,
            target_score=request.target_score
        )

        return adjustment

    except Exception as e:
        logger.error(f"Error adjusting difficulty: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/learning-path")
async def recommend_learning_path(request: PathRecommendationRequest):
    """
    Recommend personalized learning paths

    Uses collaborative filtering:
    - Finds similar users
    - Recommends paths that worked for them
    """
    try:
        # TODO: Fetch all user profiles and available paths from database
        all_users = []  # Fetch from DB
        available_paths = []  # Fetch from DB

        recommendations = path_recommender.recommend_learning_path(
            user_profile={
                'user_id': request.user_id,
                'competencies': request.competencies,
                'avg_score': request.avg_score,
                'completed_paths': request.completed_paths
            },
            all_user_profiles=all_users,
            available_paths=available_paths
        )

        return {
            'user_id': request.user_id,
            'recommendations': recommendations,
            'note': 'Using limited dataset - full implementation pending'
        }

    except Exception as e:
        logger.error(f"Error recommending learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect/anomalies")
async def detect_anomalies(request: AnomalyDetectionRequest):
    """
    Detect anomalies in exercise performance

    Identifies:
    - Unusually high/low scores
    - Unexpected patterns
    - Outliers requiring investigation
    """
    try:
        anomalies = anomaly_detector.detect_anomalies(
            exercise_results=request.exercise_results
        )

        return {
            'total_exercises': len(request.exercise_results),
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies
        }

    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimal-challenge")
async def get_optimal_challenge_zone():
    """
    Get optimal challenge zone definition

    Target score range for maximum learning
    """
    return {
        'optimal_range': difficulty_adjuster.optimal_range,
        'target_score': 72.5,
        'description': 'Scores in this range indicate optimal challenge level',
        'too_easy': {'range': '> 80%', 'action': 'Increase difficulty'},
        'optimal': {'range': '65-80%', 'action': 'Maintain difficulty'},
        'too_hard': {'range': '< 65%', 'action': 'Decrease difficulty'}
    }


@router.get("/scenario-complexity")
async def get_scenario_complexity():
    """Get complexity ratings for all scenarios"""
    return {
        'complexity_ratings': success_predictor.scenario_complexity,
        'scale': '0.0 (easiest) to 1.0 (hardest)',
        'note': 'Complexity affects success prediction'
    }


@router.post("/simulate/performance")
async def simulate_performance(
    scenario_type: str,
    team_competency: float,
    preparation_days: int,
    simulations: int = Query(100, description="Number of Monte Carlo simulations")
):
    """
    Monte Carlo simulation of exercise performance

    Runs multiple simulations to estimate performance distribution
    """
    try:
        # Simple Monte Carlo simulation
        import random

        results = []

        for _ in range(simulations):
            # Add random variation
            comp_variation = team_competency + random.gauss(0, 5)
            comp_variation = max(0, min(comp_variation, 100))

            # Predict with variation
            prediction = success_predictor.predict_success(
                scenario_type=scenario_type,
                team_competency=comp_variation,
                preparation_days=preparation_days,
                historical_results=[]
            )

            results.append(prediction['predicted_score'])

        # Aggregate results
        import statistics

        return {
            'scenario_type': scenario_type,
            'simulations_run': simulations,
            'mean_predicted_score': round(statistics.mean(results), 2),
            'median_predicted_score': round(statistics.median(results), 2),
            'stdev_predicted_score': round(statistics.stdev(results), 2) if len(results) > 1 else 0,
            'min_score': round(min(results), 2),
            'max_score': round(max(results), 2),
            'success_rate': round(sum(1 for s in results if s >= 70) / len(results) * 100, 2),
            'confidence': '95%'
        }

    except Exception as e:
        logger.error(f"Error simulating performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml/model-info")
async def get_ml_model_info():
    """Get information about ML models used"""
    return {
        'success_predictor': {
            'type': 'Weighted Feature Model',
            'features': list(success_predictor.model_weights.keys()),
            'weights': success_predictor.model_weights,
            'note': 'Production version would use RandomForest or XGBoost'
        },
        'difficulty_adjuster': {
            'type': 'Reinforcement Learning inspired',
            'optimal_range': difficulty_adjuster.optimal_range,
            'adjustment_step': difficulty_adjuster.adjustment_step,
            'note': 'Auto-adjusts to maintain optimal challenge'
        },
        'path_recommender': {
            'type': 'Collaborative Filtering',
            'similarity_metric': 'Cosine Similarity',
            'threshold': path_recommender.user_similarity_threshold,
            'note': 'Recommends based on similar user success'
        },
        'anomaly_detector': {
            'type': 'Statistical Outlier Detection',
            'method': 'Z-score (2+ standard deviations)',
            'contamination': anomaly_detector.contamination,
            'note': 'Production version would use Isolation Forest'
        }
    }
