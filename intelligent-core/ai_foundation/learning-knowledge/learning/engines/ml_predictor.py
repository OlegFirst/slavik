"""
ML-Powered Predictions Engine

Exercise success prediction, difficulty adjustment, anomaly detection
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import statistics
from collections import defaultdict
import random

logger = logging.getLogger(__name__)


class ExerciseSuccessPredictor:
    """
    Predicts exercise success probability

    Features:
    - Team competency scores
    - Preparation time
    - Historical scenario performance
    - Scenario complexity
    """

    def __init__(self):
        # Simplified ML model (would use sklearn RandomForest in production)
        self.model_weights = {
            'team_competency': 0.35,
            'preparation_days': 0.20,
            'historical_performance': 0.25,
            'scenario_complexity': 0.20
        }

        self.scenario_complexity = {
            'cyber': 0.8,
            'supply_chain': 0.7,
            'natural_disaster': 0.6,
            'pandemic': 0.75,
            'physical': 0.5,
            'operational': 0.65
        }

    def predict_success(
        self,
        scenario_type: str,
        team_competency: float,
        preparation_days: int,
        historical_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict exercise success probability

        Returns:
            Prediction with confidence interval
        """
        # Extract features
        features = self._extract_features(
            scenario_type=scenario_type,
            team_competency=team_competency,
            preparation_days=preparation_days,
            historical_results=historical_results
        )

        # Calculate predicted score
        predicted_score = self._calculate_prediction(features)

        # Calculate success probability (score >= 70)
        success_threshold = 70
        success_probability = self._calculate_success_probability(
            predicted_score,
            success_threshold
        )

        # Confidence interval
        confidence_interval = self._calculate_confidence_interval(
            predicted_score,
            features
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            predicted_score,
            success_probability,
            features
        )

        return {
            'scenario_type': scenario_type,
            'predicted_score': round(predicted_score, 2),
            'success_probability': round(success_probability, 3),
            'confidence_interval': {
                'lower': round(confidence_interval[0], 2),
                'upper': round(confidence_interval[1], 2)
            },
            'factors': features,
            'recommendations': recommendations
        }

    def _extract_features(
        self,
        scenario_type: str,
        team_competency: float,
        preparation_days: int,
        historical_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract and normalize features"""
        # Normalize team competency (0-1)
        team_comp_norm = min(team_competency / 100, 1.0)

        # Normalize preparation (assume 14 days optimal)
        prep_norm = min(preparation_days / 14, 1.0)

        # Historical performance in this scenario
        scenario_results = [
            r for r in historical_results
            if r.get('scenario_type') == scenario_type
        ]

        if scenario_results:
            hist_avg = statistics.mean([r.get('overall_score', 0) for r in scenario_results])
            hist_norm = hist_avg / 100
        else:
            hist_norm = 0.5  # Neutral if no history

        # Scenario complexity (inverse - easier = higher score)
        complexity = self.scenario_complexity.get(scenario_type, 0.6)
        complexity_factor = 1 - complexity  # Invert so easier = higher value

        return {
            'team_competency': team_comp_norm,
            'preparation': prep_norm,
            'historical_performance': hist_norm,
            'scenario_complexity': complexity_factor
        }

    def _calculate_prediction(self, features: Dict[str, float]) -> float:
        """Calculate weighted prediction"""
        prediction = sum(
            features[key] * self.model_weights[key]
            for key in features.keys()
        )

        # Scale to 0-100
        return prediction * 100

    def _calculate_success_probability(
        self,
        predicted_score: float,
        threshold: float
    ) -> float:
        """Calculate probability of success (sigmoid-like)"""
        # Simple probability based on distance from threshold
        distance = predicted_score - threshold

        if distance >= 20:
            return 0.95
        elif distance >= 10:
            return 0.85
        elif distance >= 0:
            return 0.70
        elif distance >= -10:
            return 0.45
        elif distance >= -20:
            return 0.25
        else:
            return 0.10

    def _calculate_confidence_interval(
        self,
        predicted_score: float,
        features: Dict[str, float]
    ) -> Tuple[float, float]:
        """Calculate 95% confidence interval"""
        # Confidence based on data quality
        data_quality = features.get('historical_performance', 0.5)

        # Lower data quality = wider interval
        interval_width = 10 * (1 - data_quality)

        lower = max(predicted_score - interval_width, 0)
        upper = min(predicted_score + interval_width, 100)

        return (lower, upper)

    def _generate_recommendations(
        self,
        predicted_score: float,
        success_probability: float,
        features: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations to improve success probability"""
        recommendations = []

        if predicted_score < 70:
            # Low prediction - suggest improvements
            if features['team_competency'] < 0.7:
                recommendations.append(
                    "Team competency below threshold - conduct refresher training"
                )

            if features['preparation'] < 0.7:
                recommendations.append(
                    "Insufficient preparation time - schedule additional prep sessions"
                )

            if features['historical_performance'] < 0.6:
                recommendations.append(
                    "Low historical performance in this scenario - review past learnings"
                )

            if features['scenario_complexity'] < 0.4:
                recommendations.append(
                    "High scenario complexity - consider simplifying or increasing support"
                )
        else:
            recommendations.append(
                "Team is well-prepared - proceed with confidence"
            )

        return recommendations


class DifficultyAdjuster:
    """
    Adjusts scenario difficulty using Reinforcement Learning principles

    Optimal challenge zone: 65-80% score
    """

    def __init__(self):
        self.optimal_range = (65, 80)
        self.adjustment_step = 0.1  # 10% difficulty adjustment

    def adjust_difficulty(
        self,
        current_difficulty: float,
        recent_scores: List[float],
        target_score: float = 72.5  # Middle of optimal range
    ) -> Dict[str, Any]:
        """
        Adjust scenario difficulty based on performance

        Uses RL-inspired approach:
        - Reward = staying in optimal zone
        - Penalty = too easy or too hard
        """
        if not recent_scores:
            return {
                'current_difficulty': current_difficulty,
                'adjusted_difficulty': current_difficulty,
                'adjustment': 0,
                'reason': 'No performance data'
            }

        avg_score = statistics.mean(recent_scores)

        # Determine adjustment
        if avg_score < self.optimal_range[0]:
            # Too hard - decrease difficulty
            adjustment = -self.adjustment_step
            reason = f"Scores too low (avg {avg_score:.1f}%) - reducing difficulty"

        elif avg_score > self.optimal_range[1]:
            # Too easy - increase difficulty
            adjustment = self.adjustment_step
            reason = f"Scores too high (avg {avg_score:.1f}%) - increasing difficulty"

        else:
            # In optimal zone - no change
            adjustment = 0
            reason = f"Performance in optimal zone ({avg_score:.1f}%) - maintaining difficulty"

        new_difficulty = max(0.1, min(current_difficulty + adjustment, 1.0))

        return {
            'current_difficulty': current_difficulty,
            'adjusted_difficulty': round(new_difficulty, 2),
            'adjustment': round(adjustment, 2),
            'avg_recent_score': round(avg_score, 2),
            'optimal_range': self.optimal_range,
            'reason': reason,
            'recommendation': self._get_difficulty_recommendation(new_difficulty)
        }

    def _get_difficulty_recommendation(self, difficulty: float) -> str:
        """Get difficulty level description"""
        if difficulty <= 0.3:
            return "Basic scenario - suitable for beginners"
        elif difficulty <= 0.5:
            return "Intermediate scenario - standard challenge"
        elif difficulty <= 0.7:
            return "Advanced scenario - experienced teams"
        else:
            return "Expert scenario - maximum challenge"


class PersonalizedPathRecommender:
    """
    Recommends personalized learning paths using collaborative filtering
    """

    def __init__(self):
        self.user_similarity_threshold = 0.7

    def recommend_learning_path(
        self,
        user_profile: Dict[str, Any],
        all_user_profiles: List[Dict[str, Any]],
        available_paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recommend learning paths using collaborative filtering

        Finds similar users and recommends paths that worked for them
        """
        # Find similar users
        similar_users = self._find_similar_users(
            user_profile,
            all_user_profiles
        )

        if not similar_users:
            # No similar users - recommend based on competency level
            return self._recommend_by_competency(user_profile, available_paths)

        # Aggregate successful paths from similar users
        path_scores = defaultdict(float)

        for similar_user in similar_users:
            similarity = similar_user['similarity']

            for path in similar_user.get('completed_paths', []):
                if path.get('improvement', 0) > 0:
                    # Weight by similarity and improvement
                    path_scores[path['path_id']] += similarity * path['improvement']

        # Rank paths
        ranked_paths = sorted(
            path_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top recommendations
        recommendations = []

        for path_id, score in ranked_paths[:5]:
            path = next((p for p in available_paths if p.get('id') == path_id), None)

            if path:
                recommendations.append({
                    'path_id': path_id,
                    'path_name': path.get('name'),
                    'recommendation_score': round(score, 2),
                    'reason': 'Successful for similar users',
                    'estimated_improvement': path.get('avg_improvement', 0)
                })

        return recommendations

    def _find_similar_users(
        self,
        target_user: Dict[str, Any],
        all_users: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find users with similar competency profiles"""
        similar_users = []

        target_competencies = target_user.get('competencies', {})

        for user in all_users:
            if user.get('user_id') == target_user.get('user_id'):
                continue  # Skip self

            user_competencies = user.get('competencies', {})

            # Calculate similarity (cosine similarity)
            similarity = self._calculate_similarity(
                target_competencies,
                user_competencies
            )

            if similarity >= self.user_similarity_threshold:
                similar_users.append({
                    'user_id': user.get('user_id'),
                    'similarity': similarity,
                    'completed_paths': user.get('completed_paths', [])
                })

        return similar_users

    def _calculate_similarity(
        self,
        comp1: Dict[str, float],
        comp2: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity between competency vectors"""
        # Simplified similarity calculation
        common_keys = set(comp1.keys()) & set(comp2.keys())

        if not common_keys:
            return 0

        # Normalized dot product
        dot_product = sum(comp1[k] * comp2[k] for k in common_keys)
        norm1 = sum(v**2 for v in comp1.values()) ** 0.5
        norm2 = sum(v**2 for v in comp2.values()) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot_product / (norm1 * norm2)

    def _recommend_by_competency(
        self,
        user_profile: Dict[str, Any],
        available_paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recommend paths based on competency level"""
        user_score = user_profile.get('avg_score', 50)

        # Match paths to competency level
        recommendations = []

        for path in available_paths:
            target_range = path.get('target_score_range', '50-75')
            low, high = map(int, target_range.split('-'))

            if low <= user_score <= high:
                recommendations.append({
                    'path_id': path.get('id'),
                    'path_name': path.get('name'),
                    'recommendation_score': 0.7,
                    'reason': f'Matches competency level ({user_score})',
                    'estimated_improvement': path.get('avg_improvement', 0)
                })

        return recommendations[:5]


class AnomalyDetector:
    """
    Detects anomalies in exercise performance using Isolation Forest principles
    """

    def __init__(self):
        self.contamination = 0.1  # Expect 10% anomalies

    def detect_anomalies(
        self,
        exercise_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous exercise results

        Anomalies:
        - Unusually high/low scores
        - Unexpected performance patterns
        """
        if len(exercise_results) < 5:
            return []

        anomalies = []

        # Extract scores
        scores = [r.get('overall_score', 0) for r in exercise_results]
        mean_score = statistics.mean(scores)
        stdev_score = statistics.stdev(scores) if len(scores) > 1 else 0

        # Detect score anomalies
        for result in exercise_results:
            score = result.get('overall_score', 0)

            if stdev_score > 0:
                z_score = (score - mean_score) / stdev_score

                if abs(z_score) > 2:  # 2 standard deviations
                    anomalies.append({
                        'exercise_id': result.get('id'),
                        'exercise_name': result.get('exercise_name'),
                        'anomaly_type': 'score',
                        'score': score,
                        'expected_range': (
                            round(mean_score - 2*stdev_score, 2),
                            round(mean_score + 2*stdev_score, 2)
                        ),
                        'z_score': round(z_score, 2),
                        'severity': 'high' if abs(z_score) > 3 else 'medium',
                        'investigation_needed': True,
                        'conducted_at': result.get('conducted_at')
                    })

        return anomalies
