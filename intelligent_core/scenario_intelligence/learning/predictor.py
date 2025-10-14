"""
Scenario Predictor
Предсказывает следующие сценарии, failures и приоритеты
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class ScenarioPredictor:
    """
    Предсказатель сценариев

    Использует:
    - Pattern Detector results
    - Execution history
    - External predictions (от Predictive Service)
    - Community votes (от Community Intelligence)

    Предсказывает:
    - Какие сценарии упадут (failure prediction)
    - Следующие сценарии для выполнения (next scenario prediction)
    - Приоритеты сценариев (priority calculation)
    - Оптимальное время выполнения (timing prediction)
    """

    def __init__(self):
        self.prediction_history: List[Dict[str, Any]] = []
        self.accuracy_stats: Dict[str, float] = {}

    async def predict_failures(
        self,
        scenarios: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        execution_history: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Predict which scenarios will fail

        Args:
            scenarios: List of scenarios
            patterns: Detected patterns from Pattern Detector
            execution_history: Historical executions

        Returns:
            {
                scenario_id: {
                    "failure_probability": 0.0-1.0,
                    "confidence": 0.0-1.0,
                    "reasons": [str],
                    "recommended_action": str
                }
            }
        """
        try:
            logger.info(f"Predicting failures for {len(scenarios)} scenarios")

            predictions = {}

            # Get failure patterns
            failure_patterns = [p for p in patterns if p.get("type") == "failure_pattern"]
            time_patterns = [p for p in patterns if p.get("type") == "time_pattern"]
            dependency_patterns = [p for p in patterns if p.get("type") == "dependency_pattern"]

            for scenario in scenarios:
                scenario_id = scenario["meta"]["id"]

                prediction = self._predict_scenario_failure(
                    scenario_id=scenario_id,
                    failure_patterns=failure_patterns,
                    time_patterns=time_patterns,
                    dependency_patterns=dependency_patterns,
                    execution_history=execution_history
                )

                predictions[scenario_id] = prediction

            logger.info(f"✅ Predicted failures for {len(predictions)} scenarios")

            return predictions

        except Exception as e:
            logger.error(f"Error predicting failures: {e}")
            return {}

    def _predict_scenario_failure(
        self,
        scenario_id: str,
        failure_patterns: List[Dict[str, Any]],
        time_patterns: List[Dict[str, Any]],
        dependency_patterns: List[Dict[str, Any]],
        execution_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict failure for single scenario"""

        failure_probability = 0.0
        confidence = 0.0
        reasons = []

        # Check failure patterns
        scenario_failure_pattern = next(
            (p for p in failure_patterns if p.get("scenario_id") == scenario_id),
            None
        )

        if scenario_failure_pattern:
            failure_rate = scenario_failure_pattern.get("failure_rate", 0)
            failure_probability = max(failure_probability, failure_rate)
            confidence = scenario_failure_pattern.get("confidence", 0)
            reasons.append(f"Historical failure rate: {failure_rate*100:.1f}%")

        # Check time patterns
        current_hour = datetime.now().hour
        hour_pattern = next(
            (p for p in time_patterns if p.get("hour") == current_hour),
            None
        )

        if hour_pattern:
            time_failure_rate = hour_pattern.get("failure_rate", 0)
            failure_probability = max(failure_probability, time_failure_rate * 0.5)  # Weight: 50%
            reasons.append(f"High failure rate during this hour ({current_hour}:00)")

        # Check dependency patterns
        for dep_pattern in dependency_patterns:
            if dep_pattern.get("scenario_a") == scenario_id or dep_pattern.get("scenario_b") == scenario_id:
                co_failure_rate = dep_pattern.get("co_failure_rate", 0)
                failure_probability = max(failure_probability, co_failure_rate * 0.4)  # Weight: 40%
                other_scenario = dep_pattern.get("scenario_b") if dep_pattern.get("scenario_a") == scenario_id else dep_pattern.get("scenario_a")
                reasons.append(f"Often fails together with {other_scenario}")

        # Calculate confidence
        if not confidence:
            # Base confidence on number of executions
            scenario_executions = [e for e in execution_history if e.get("scenario_id") == scenario_id]
            confidence = min(len(scenario_executions) / 10, 1.0)

        # Recommended action
        if failure_probability > 0.7:
            recommended_action = "SKIP - High failure probability"
        elif failure_probability > 0.4:
            recommended_action = "INVESTIGATE - Medium failure probability"
        elif failure_probability > 0.2:
            recommended_action = "MONITOR - Low failure probability"
        else:
            recommended_action = "EXECUTE - Low failure probability"

        return {
            "failure_probability": failure_probability,
            "confidence": confidence,
            "reasons": reasons if reasons else ["No failure patterns detected"],
            "recommended_action": recommended_action
        }

    async def predict_next_scenarios(
        self,
        current_scenario_id: str,
        patterns: List[Dict[str, Any]],
        execution_history: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Predict next scenarios to execute

        Args:
            current_scenario_id: Currently executing scenario
            patterns: Detected patterns
            execution_history: Historical executions
            limit: Max predictions

        Returns:
            [
                {
                    "scenario_id": str,
                    "probability": 0.0-1.0,
                    "reason": str
                }
            ]
        """
        try:
            logger.info(f"Predicting next scenarios after {current_scenario_id}")

            # Get sequence patterns
            sequence_patterns = [p for p in patterns if p.get("type") == "sequence_pattern"]

            # Find sequences containing current scenario
            relevant_sequences = []

            for pattern in sequence_patterns:
                sequence = pattern.get("sequence", [])
                if current_scenario_id in sequence:
                    idx = sequence.index(current_scenario_id)
                    if idx < len(sequence) - 1:
                        # Found next scenario
                        next_scenario = sequence[idx + 1]
                        frequency = pattern.get("frequency", 0)
                        relevant_sequences.append({
                            "scenario_id": next_scenario,
                            "probability": frequency,
                            "reason": f"Frequently follows {current_scenario_id} in sequence"
                        })

            # Sort by probability
            relevant_sequences.sort(key=lambda x: x["probability"], reverse=True)

            # Return top N
            return relevant_sequences[:limit]

        except Exception as e:
            logger.error(f"Error predicting next scenarios: {e}")
            return []

    async def calculate_priorities(
        self,
        scenarios: List[Dict[str, Any]],
        predictions: Optional[Dict[str, Any]] = None,
        community_votes: Optional[Dict[str, Any]] = None,
        optimizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate scenario priorities

        Combines:
        - Failure predictions
        - Community votes (от Community Intelligence)
        - Workflow optimizations (от Workflow Intelligence)
        - Business value (from scenario meta)

        Args:
            scenarios: List of scenarios
            predictions: Failure predictions
            community_votes: Community Intelligence votes
            optimizations: Workflow Intelligence optimizations

        Returns:
            {
                scenario_id: {
                    "priority": "CRITICAL|HIGH|MEDIUM|LOW",
                    "score": 0-100,
                    "confidence": 0.0-1.0,
                    "reasons": [str]
                }
            }
        """
        try:
            logger.info(f"Calculating priorities for {len(scenarios)} scenarios")

            priorities = {}

            for scenario in scenarios:
                scenario_id = scenario["meta"]["id"]

                priority_data = self._calculate_scenario_priority(
                    scenario=scenario,
                    predictions=predictions.get(scenario_id) if predictions else None,
                    community_vote=community_votes.get(scenario_id) if community_votes else None,
                    optimization=optimizations.get(scenario_id) if optimizations else None
                )

                priorities[scenario_id] = priority_data

            logger.info(f"✅ Calculated priorities for {len(priorities)} scenarios")

            return priorities

        except Exception as e:
            logger.error(f"Error calculating priorities: {e}")
            return {}

    def _calculate_scenario_priority(
        self,
        scenario: Dict[str, Any],
        predictions: Optional[Dict[str, Any]],
        community_vote: Optional[Dict[str, Any]],
        optimization: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate priority for single scenario"""

        score = 0
        reasons = []
        confidence_values = []

        # 1. Business value (from meta.tags)
        meta = scenario.get("meta", {})
        tags = meta.get("tags", [])

        if "critical" in tags or "high-priority" in tags:
            score += 40
            reasons.append("Tagged as critical/high-priority")

        pillar = meta.get("pillar", "")
        if pillar == "security":
            score += 30
            reasons.append("Security pillar (high importance)")
        elif pillar == "reliability":
            score += 25
            reasons.append("Reliability pillar")

        # 2. Failure prediction
        if predictions:
            failure_prob = predictions.get("failure_probability", 0)
            pred_confidence = predictions.get("confidence", 0)

            if failure_prob > 0.7:
                score += 30
                reasons.append(f"High failure probability ({failure_prob*100:.1f}%)")
            elif failure_prob > 0.4:
                score += 20
                reasons.append(f"Medium failure probability ({failure_prob*100:.1f}%)")
            elif failure_prob > 0.2:
                score += 10
                reasons.append(f"Low failure probability ({failure_prob*100:.1f}%)")

            confidence_values.append(pred_confidence)

        # 3. Community vote
        if community_vote:
            vote_score = community_vote.get("score", 0)  # 0-10
            vote_confidence = community_vote.get("confidence", 0)

            normalized_vote = (vote_score / 10) * 20  # Scale to 0-20
            score += normalized_vote
            reasons.append(f"Community vote: {vote_score}/10")

            confidence_values.append(vote_confidence)

        # 4. Workflow optimization
        if optimization:
            opt_priority = optimization.get("priority", 0)  # 0-10
            opt_confidence = optimization.get("confidence", 0)

            normalized_opt = (opt_priority / 10) * 10  # Scale to 0-10
            score += normalized_opt
            reasons.append(f"Workflow optimization priority: {opt_priority}/10")

            confidence_values.append(opt_confidence)

        # Calculate overall confidence
        if confidence_values:
            overall_confidence = statistics.mean(confidence_values)
        else:
            overall_confidence = 0.5  # Default

        # Determine priority level
        if score >= 80:
            priority_level = "CRITICAL"
        elif score >= 60:
            priority_level = "HIGH"
        elif score >= 40:
            priority_level = "MEDIUM"
        else:
            priority_level = "LOW"

        return {
            "priority": priority_level,
            "score": min(score, 100),
            "confidence": overall_confidence,
            "reasons": reasons if reasons else ["Default priority"]
        }

    async def predict_optimal_timing(
        self,
        scenario_id: str,
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict optimal time to execute scenario

        Args:
            scenario_id: Scenario ID
            patterns: Detected patterns

        Returns:
            {
                "recommended_hours": [int],  # Hours of day
                "avoid_hours": [int],
                "reason": str
            }
        """
        try:
            # Get time patterns
            time_patterns = [p for p in patterns if p.get("type") == "time_pattern"]

            # Find hours with high failure rates
            avoid_hours = []
            for pattern in time_patterns:
                if pattern.get("failure_rate", 0) > 0.3:
                    avoid_hours.append(pattern.get("hour"))

            # Recommend hours with low failure (inverse)
            all_hours = set(range(24))
            avoid_hours_set = set(avoid_hours)
            recommended_hours = list(all_hours - avoid_hours_set)

            # Prefer business hours (9-17) if not in avoid list
            business_hours = [h for h in range(9, 18) if h in recommended_hours]

            if business_hours:
                recommended_hours = business_hours
                reason = "Business hours with low failure rates"
            elif recommended_hours:
                reason = "Hours with historically low failure rates"
            else:
                recommended_hours = list(range(24))
                reason = "No specific timing recommendation"

            return {
                "recommended_hours": recommended_hours,
                "avoid_hours": avoid_hours,
                "reason": reason
            }

        except Exception as e:
            logger.error(f"Error predicting timing: {e}")
            return {
                "recommended_hours": list(range(24)),
                "avoid_hours": [],
                "reason": "Error in prediction"
            }

    def recalculate(
        self,
        execution_results: List[Dict[str, Any]],
        previous_priorities: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Recalculate priorities based on execution results

        Feedback loop - adjust predictions based on actual results

        Args:
            execution_results: Recent execution results
            previous_priorities: Previous priorities (to compare)

        Returns:
            Updated priorities
        """
        try:
            logger.info(f"Recalculating priorities based on {len(execution_results)} results")

            # Calculate prediction accuracy
            if previous_priorities:
                self._calculate_prediction_accuracy(execution_results, previous_priorities)

            # For now, return empty dict
            # Full implementation would re-run calculate_priorities with updated data
            return {}

        except Exception as e:
            logger.error(f"Error recalculating priorities: {e}")
            return {}

    def _calculate_prediction_accuracy(
        self,
        execution_results: List[Dict[str, Any]],
        previous_priorities: Dict[str, Dict[str, Any]]
    ):
        """Calculate how accurate our predictions were"""
        try:
            correct_predictions = 0
            total_predictions = 0

            for result in execution_results:
                scenario_id = result.get("scenario_id")
                actual_status = result.get("status")

                if scenario_id in previous_priorities:
                    priority_data = previous_priorities[scenario_id]
                    predicted_failure_prob = priority_data.get("failure_probability", 0)

                    # Check if prediction was correct
                    actually_failed = actual_status in ["failed", "error"]
                    predicted_to_fail = predicted_failure_prob > 0.5

                    total_predictions += 1
                    if actually_failed == predicted_to_fail:
                        correct_predictions += 1

            if total_predictions > 0:
                accuracy = correct_predictions / total_predictions
                self.accuracy_stats["overall"] = accuracy
                logger.info(f"Prediction accuracy: {accuracy*100:.1f}%")

        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")

    async def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        return {
            "total_predictions": len(self.prediction_history),
            "accuracy": self.accuracy_stats.get("overall", 0),
            "accuracy_by_type": self.accuracy_stats
        }


# Global instance
_predictor: Optional[ScenarioPredictor] = None


def get_predictor() -> ScenarioPredictor:
    """Get or create global predictor"""
    global _predictor

    if _predictor is None:
        _predictor = ScenarioPredictor()

    return _predictor
