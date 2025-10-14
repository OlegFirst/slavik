"""
ML Predictor - Integrated Version

Uses shared ML Platform for predictions
Extends with Learning System specific logic
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics

# Add shared to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from integrations.ml_platform_client import (
    MLPlatformClient,
    FeatureBuilder,
    ModelPerformanceTracker
)

logger = logging.getLogger(__name__)


class IntegratedMLPredictor:
    """
    Learning System's ML predictor using shared ML Platform

    Provides:
    - Exercise success prediction
    - Difficulty scoring
    - Time estimation
    - Performance forecasting

    All using shared ML Platform models
    """

    def __init__(self, ml_service_url: str = "http://localhost:8060"):
        self.ml_client = MLPlatformClient(ml_service_url)
        self.performance_tracker = ModelPerformanceTracker()

        # Model names in ML Platform
        self.models = {
            'exercise_success': 'exercise_success_predictor',
            'difficulty_scorer': 'exercise_difficulty_scorer',
            'time_estimator': 'exercise_time_estimator'
        }

    async def predict_exercise_success(
        self,
        scenario_type: str,
        team_composition: Dict[str, Any],
        historical_performance: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict exercise success probability and expected score

        Uses shared ML Platform model

        Args:
            scenario_type: Type of scenario
            team_composition: Team data (size, competencies, etc.)
            historical_performance: Past exercise results
            context: Additional context

        Returns:
            Prediction with confidence and recommendations
        """
        # Build features using FeatureBuilder
        features = self._build_exercise_features(
            scenario_type,
            team_composition,
            historical_performance
        )

        # Get prediction from ML Platform
        prediction = await self.ml_client.predict(
            model_name=self.models['exercise_success'],
            features=features.build(),
            context=context or {},
            return_explanation=True
        )

        # Track prediction
        self.performance_tracker.record_prediction(
            prediction_id=prediction.get('prediction_id'),
            prediction=prediction.get('prediction')
        )

        # Enhance with Learning System insights
        enhanced_prediction = self._enhance_prediction_with_insights(
            prediction,
            historical_performance
        )

        logger.info(f"Predicted success: {enhanced_prediction.get('predicted_score'):.1f} "
                   f"(confidence: {enhanced_prediction.get('confidence'):.2f})")

        return enhanced_prediction

    async def predict_difficulty_score(
        self,
        scenario_definition: Dict[str, Any],
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict difficulty score for scenario

        Args:
            scenario_definition: Scenario parameters
            target_audience: Team competency data

        Returns:
            Difficulty score (0-100) and recommendations
        """
        features = FeatureBuilder()

        # Scenario features
        features.add_categorical('scenario_type', scenario_definition.get('type', 'unknown'))
        features.add_numeric('scenario_complexity', scenario_definition.get('complexity', 50))
        features.add_numeric('objectives_count', len(scenario_definition.get('objectives', [])))

        # Audience features
        features.add_numeric('team_avg_competency', target_audience.get('avg_competency', 0.5))
        features.add_numeric('team_experience_months', target_audience.get('avg_experience_months', 12))

        prediction = await self.ml_client.predict(
            model_name=self.models['difficulty_scorer'],
            features=features.build(),
            return_explanation=False
        )

        return {
            'difficulty_score': prediction.get('prediction'),
            'confidence': prediction.get('confidence'),
            'prediction_id': prediction.get('prediction_id'),
            'difficulty_level': self._score_to_level(prediction.get('prediction')),
            'recommended_preparation_hours': self._difficulty_to_prep_time(prediction.get('prediction'))
        }

    async def predict_exercise_duration(
        self,
        scenario_type: str,
        team_size: int,
        complexity: int
    ) -> Dict[str, Any]:
        """
        Predict exercise duration

        Args:
            scenario_type: Type of scenario
            team_size: Number of participants
            complexity: Complexity score (0-100)

        Returns:
            Predicted duration in minutes
        """
        features = FeatureBuilder()
        features.add_categorical('scenario_type', scenario_type)
        features.add_numeric('team_size', team_size)
        features.add_numeric('complexity', complexity)

        prediction = await self.ml_client.predict(
            model_name=self.models['time_estimator'],
            features=features.build()
        )

        return {
            'predicted_duration_minutes': prediction.get('prediction'),
            'confidence': prediction.get('confidence'),
            'prediction_id': prediction.get('prediction_id'),
            'duration_range': {
                'min': prediction.get('prediction') * 0.8,
                'max': prediction.get('prediction') * 1.2
            }
        }

    async def submit_actual_result(
        self,
        prediction_id: str,
        actual_score: float,
        exercise_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Submit actual exercise result (closes feedback loop)

        Args:
            prediction_id: ID from prediction
            actual_score: Real exercise score
            exercise_metadata: Additional data
        """
        # Submit to ML Platform (triggers model learning)
        success = await self.ml_client.submit_feedback(
            prediction_id=prediction_id,
            actual_outcome=actual_score,
            metadata=exercise_metadata
        )

        # Track locally
        self.performance_tracker.record_prediction(
            prediction_id=prediction_id,
            prediction=0,  # Don't have original prediction here
            actual=actual_score
        )

        if success:
            logger.info(f"Feedback submitted for {prediction_id}, actual: {actual_score}")
        else:
            logger.warning(f"Failed to submit feedback for {prediction_id}")

    async def get_model_performance(self) -> Dict[str, Any]:
        """
        Get performance metrics for all Learning System models

        Returns:
            Performance data from ML Platform
        """
        performance = {}

        for model_key, model_name in self.models.items():
            model_perf = await self.ml_client.get_model_performance(
                model_name=model_name,
                time_window_days=30
            )
            if model_perf:
                performance[model_key] = model_perf

        # Add local tracking
        performance['local_tracking'] = self.performance_tracker.get_recent_performance()

        return performance

    async def get_feature_importance(
        self,
        model_type: str = 'exercise_success'
    ) -> Optional[Dict[str, float]]:
        """
        Get feature importance for model

        Args:
            model_type: Model type (exercise_success, difficulty_scorer, etc.)

        Returns:
            Feature importance dict
        """
        model_name = self.models.get(model_type)
        if not model_name:
            return None

        return await self.ml_client.get_feature_importance(model_name)

    def _build_exercise_features(
        self,
        scenario_type: str,
        team_composition: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> FeatureBuilder:
        """Build features for exercise prediction"""
        builder = FeatureBuilder()

        # Scenario features
        builder.add_categorical('scenario_type', scenario_type)

        # Team features
        builder.add_numeric('team_size', team_composition.get('size', 0))
        builder.add_numeric('avg_competency', team_composition.get('avg_competency', 0.5))
        builder.add_numeric('competency_variance', team_composition.get('competency_variance', 0.1))

        # Historical features
        if historical_performance:
            scores = [p.get('overall_score', 0) for p in historical_performance]
            builder.add_list_aggregates('historical_scores', scores)

            # Days since last exercise
            if historical_performance:
                last_date = max(p.get('conducted_at', datetime.min) for p in historical_performance)
                if isinstance(last_date, datetime):
                    days_since = (datetime.utcnow() - last_date).days
                    builder.add_numeric('days_since_last_exercise', days_since)

            # Success rate
            successes = sum(1 for p in historical_performance if p.get('overall_score', 0) >= 70)
            builder.add_numeric('historical_success_rate', successes / len(historical_performance))

        return builder

    def _enhance_prediction_with_insights(
        self,
        prediction: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add Learning System insights to prediction"""
        enhanced = prediction.copy()

        predicted_score = prediction.get('prediction', 0)

        # Add success probability
        enhanced['success_probability'] = self._score_to_probability(predicted_score)

        # Add risk level
        enhanced['risk_level'] = self._score_to_risk(predicted_score)

        # Add recommendations based on prediction
        enhanced['recommendations'] = self._generate_recommendations(
            predicted_score,
            historical_performance
        )

        # Add confidence level category
        confidence = prediction.get('confidence', 0)
        enhanced['confidence_level'] = self._confidence_category(confidence)

        return enhanced

    def _score_to_probability(self, score: float) -> float:
        """Convert predicted score to success probability"""
        # Success threshold: 70
        if score >= 90:
            return 0.95
        elif score >= 70:
            return 0.8
        elif score >= 60:
            return 0.6
        elif score >= 50:
            return 0.4
        else:
            return 0.2

    def _score_to_risk(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return 'low'
        elif score >= 60:
            return 'medium'
        else:
            return 'high'

    def _generate_recommendations(
        self,
        predicted_score: float,
        historical_performance: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on prediction"""
        recommendations = []

        if predicted_score < 60:
            recommendations.append("Consider additional preparation time")
            recommendations.append("Review team competencies and provide targeted training")

        if predicted_score < 70:
            recommendations.append("Simplify scenario or extend timeline")

        if historical_performance:
            recent_scores = [p.get('overall_score', 0) for p in historical_performance[-3:]]
            if recent_scores and statistics.mean(recent_scores) < predicted_score - 10:
                recommendations.append("Team showing improvement - maintain momentum")

        if not recommendations:
            recommendations.append("Team well-prepared for this scenario")

        return recommendations

    def _score_to_level(self, score: float) -> str:
        """Convert difficulty score to level"""
        if score >= 80:
            return 'advanced'
        elif score >= 60:
            return 'intermediate'
        else:
            return 'beginner'

    def _difficulty_to_prep_time(self, difficulty: float) -> int:
        """Convert difficulty to recommended prep hours"""
        if difficulty >= 80:
            return 8
        elif difficulty >= 60:
            return 4
        else:
            return 2

    def _confidence_category(self, confidence: float) -> str:
        """Categorize confidence level"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        else:
            return 'low'

    async def close(self):
        """Close connections"""
        await self.ml_client.close()
