"""
Learning Engine - Exercise result learning and scenario improvement

From /services/scenario_orchestrator/main.py (learning system)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from models import ExerciseResult, ScenarioLearning

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Exercise learning and scenario improvement engine

    Collects exercise results and learns patterns for improvement
    """

    def __init__(self):
        self.scenario_learning = {}  # scenario_id -> learning data
        logger.info("LearningEngine initialized")

    async def collect_exercise_result(self, result: ExerciseResult) -> Dict[str, Any]:
        """
        Collect exercise result for learning

        Args:
            result: Exercise completion result

        Returns:
            Updated learning summary
        """
        logger.info(f"Collecting exercise result: {result.exercise_id}")

        scenario_id = result.scenario_id

        # Initialize if first use
        if scenario_id not in self.scenario_learning:
            self.scenario_learning[scenario_id] = {
                'scenario_id': scenario_id,
                'total_uses': 0,
                'effectiveness_scores': [],
                'patterns': {
                    'successful_elements': [],
                    'common_issues': [],
                    'improvement_areas': []
                }
            }

        learning_data = self.scenario_learning[scenario_id]

        # Update metrics
        learning_data['total_uses'] += 1
        learning_data['effectiveness_scores'].append(result.effectiveness_score)

        # Extract patterns from feedback
        self._extract_patterns(result, learning_data)

        # Calculate average effectiveness
        avg_effectiveness = sum(learning_data['effectiveness_scores']) / len(learning_data['effectiveness_scores'])
        learning_data['avg_effectiveness'] = round(avg_effectiveness, 2)

        # Generate improvements if enough data
        if learning_data['total_uses'] >= 3:
            improvements = self._generate_improvements(learning_data)
            learning_data['improvements'] = improvements

        logger.info(f"Learning data updated for scenario {scenario_id}")

        return {
            'scenario_id': scenario_id,
            'total_uses': learning_data['total_uses'],
            'avg_effectiveness': learning_data.get('avg_effectiveness', 0)
        }

    def _extract_patterns(self, result: ExerciseResult, learning_data: Dict) -> None:
        """Extract patterns from exercise feedback"""
        # Extract successful elements from positive feedback
        positive_feedback = [f for f in result.participant_feedback if f.get('rating', 0) >= 7]
        for feedback in positive_feedback:
            comment = feedback.get('comment', '')
            if comment:
                learning_data['patterns']['successful_elements'].append(comment)

        # Extract issues from negative feedback
        negative_feedback = [f for f in result.participant_feedback if f.get('rating', 0) <= 4]
        for feedback in negative_feedback:
            comment = feedback.get('comment', '')
            if comment:
                learning_data['patterns']['common_issues'].append(comment)

        # Add lessons learned
        learning_data['patterns']['improvement_areas'].extend(result.lessons_learned)

    def _generate_improvements(self, learning_data: Dict) -> List[str]:
        """Generate improvement recommendations based on patterns"""
        improvements = []

        # Check effectiveness trend
        scores = learning_data['effectiveness_scores']
        avg = learning_data.get('avg_effectiveness', 0)

        if avg < 6.0:
            improvements.append("Scenario effectiveness below target - consider major revisions")

        if len(scores) >= 3 and scores[-1] < scores[-3]:
            improvements.append("Effectiveness declining - review recent changes")

        # Check common issues
        issues = learning_data['patterns']['common_issues']
        if len(set(issues)) > 3:
            improvements.append("Multiple recurring issues - prioritize resolution")

        # Default improvements
        if not improvements:
            improvements.append("Continue monitoring - scenario performing well")

        return improvements

    async def get_scenario_learning(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get learning insights for a scenario

        Args:
            scenario_id: Scenario identifier

        Returns:
            Learning insights dictionary
        """
        if scenario_id not in self.scenario_learning:
            return None

        learning_data = self.scenario_learning[scenario_id]

        return {
            'scenario_id': scenario_id,
            'total_uses': learning_data['total_uses'],
            'avg_effectiveness': learning_data.get('avg_effectiveness', 0),
            'effectiveness_trend': learning_data['effectiveness_scores'][-5:],
            'successful_elements': list(set(learning_data['patterns']['successful_elements'][-10:])),
            'common_issues': list(set(learning_data['patterns']['common_issues'][-10:])),
            'improvements': learning_data.get('improvements', [])
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Get overall learning statistics"""
        if not self.scenario_learning:
            return {
                'total_scenarios': 0,
                'total_exercises': 0,
                'avg_platform_effectiveness': 0.0
            }

        total_exercises = sum(data['total_uses'] for data in self.scenario_learning.values())
        all_scores = []
        for data in self.scenario_learning.values():
            all_scores.extend(data['effectiveness_scores'])

        avg_effectiveness = sum(all_scores) / len(all_scores) if all_scores else 0.0

        return {
            'total_scenarios': len(self.scenario_learning),
            'total_exercises': total_exercises,
            'avg_platform_effectiveness': round(avg_effectiveness, 2)
        }