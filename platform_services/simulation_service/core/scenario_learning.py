"""
Scenario Learning System
========================

Experience accumulation and learning from BCM exercise results.

Features:
- Collect exercise results
- Accumulate learning data
- Generate improvement recommendations
- Track effectiveness trends
- Learning dashboard

Adapted from: /scenarios/scenario_orchestrator/main.py (learning endpoints)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import httpx

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================

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
    effectiveness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Overall effectiveness score (0-10)"
    )
    completed_at: Optional[str] = None


class ScenarioLearning(BaseModel):
    """Learning data accumulated for scenario improvement"""
    scenario_id: str
    total_uses: int = 0
    avg_effectiveness: float = 0.0
    effectiveness_scores: List[float] = Field(default_factory=list)
    exercise_results: List[str] = Field(default_factory=list)
    patterns: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            'successful_elements': [],
            'common_issues': [],
            'improvement_areas': []
        }
    )
    ai_recommendations: List[str] = Field(default_factory=list)
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())


class LearningInsights(BaseModel):
    """Insights from accumulated learning"""
    total_uses: int
    avg_effectiveness: float
    effectiveness_trend: List[float]
    successful_elements: List[str]
    common_issues: List[str]
    ai_recommendations: List[str]
    improvement_areas: List[str]


class LearningDashboard(BaseModel):
    """Dashboard data for all scenarios"""
    total_scenarios_with_data: int
    total_exercises_completed: int
    avg_platform_effectiveness: float
    recent_exercise_results: List[Dict[str, Any]]
    top_performing_scenarios: List[Dict[str, Any]]
    scenarios_needing_improvement: List[Dict[str, Any]]


# ============================================================================
# Scenario Learning Manager
# ============================================================================

class ScenarioLearningManager:
    """
    Manages scenario learning and experience accumulation

    Stores learning data in-memory (development) or external storage (production).
    Integrates with AI Orchestrator for improvement recommendations.
    """

    def __init__(
        self,
        ai_orchestrator_url: str = None,
        storage_backend: str = "memory"  # memory, redis, supabase
    ):
        self.ai_orchestrator_url = ai_orchestrator_url or "http://ai-orchestrator:8000"
        self.storage_backend = storage_backend

        # In-memory storage for development
        self.scenario_experience_db: Dict[str, Any] = {}

    async def collect_exercise_result(
        self,
        result: ExerciseResult
    ) -> Dict[str, Any]:
        """
        Collect exercise results for learning accumulation

        Args:
            result: Exercise result data

        Returns:
            Collection status with updated metrics
        """
        try:
            logger.info(f"Collecting exercise result: {result.exercise_id}")

            # Store exercise result
            result_key = f"exercise_result_{result.exercise_id}"
            self.scenario_experience_db[result_key] = result.dict()

            # Update scenario learning data
            scenario_key = f"scenario_learning_{result.scenario_id}"

            if scenario_key not in self.scenario_experience_db:
                self.scenario_experience_db[scenario_key] = ScenarioLearning(
                    scenario_id=result.scenario_id
                ).dict()

            # Accumulate learning data
            learning_data = self.scenario_experience_db[scenario_key]
            learning_data['total_uses'] += 1
            learning_data['effectiveness_scores'].append(result.effectiveness_score)
            learning_data['exercise_results'].append(result.exercise_id)

            # Extract patterns from feedback
            if result.participant_feedback:
                self._extract_feedback_patterns(
                    learning_data,
                    result.participant_feedback
                )

            # Add lessons learned
            learning_data['patterns']['improvement_areas'].extend(
                result.lessons_learned
            )

            # Calculate updated metrics
            avg_effectiveness = (
                sum(learning_data['effectiveness_scores']) /
                len(learning_data['effectiveness_scores'])
            )
            learning_data['avg_effectiveness'] = round(avg_effectiveness, 2)
            learning_data['last_updated'] = datetime.now().isoformat()

            # Generate AI-powered improvement recommendations
            if learning_data['total_uses'] >= 3:
                recommendations = await self._generate_scenario_improvements(
                    learning_data
                )
                learning_data['ai_recommendations'] = recommendations

            # Notify AI Orchestrator of new learning data
            await self._notify_ai_orchestrator_learning(result, learning_data)

            return {
                "status": "success",
                "exercise_id": result.exercise_id,
                "scenario_learning_updated": True,
                "total_scenario_uses": learning_data['total_uses'],
                "avg_effectiveness": learning_data['avg_effectiveness']
            }

        except Exception as e:
            logger.error(f"Error collecting exercise result: {e}")
            raise

    async def get_scenario_insights(
        self,
        scenario_id: str
    ) -> LearningInsights:
        """
        Get accumulated learning insights for scenario

        Args:
            scenario_id: Scenario identifier

        Returns:
            Learning insights with recommendations
        """
        try:
            scenario_key = f"scenario_learning_{scenario_id}"

            if scenario_key not in self.scenario_experience_db:
                return LearningInsights(
                    total_uses=0,
                    avg_effectiveness=0,
                    effectiveness_trend=[],
                    successful_elements=[],
                    common_issues=[],
                    ai_recommendations=[
                        "Not enough data - need at least 3 exercise completions"
                    ],
                    improvement_areas=[]
                )

            learning_data = self.scenario_experience_db[scenario_key]

            # Generate insights summary
            insights = LearningInsights(
                total_uses=learning_data['total_uses'],
                avg_effectiveness=learning_data.get('avg_effectiveness', 0),
                effectiveness_trend=learning_data['effectiveness_scores'][-5:],
                successful_elements=list(set(
                    learning_data['patterns']['successful_elements'][-10:]
                )),
                common_issues=list(set(
                    learning_data['patterns']['common_issues'][-10:]
                )),
                ai_recommendations=learning_data.get('ai_recommendations', []),
                improvement_areas=list(set(
                    learning_data['patterns']['improvement_areas'][-10:]
                ))
            )

            return insights

        except Exception as e:
            logger.error(f"Error getting scenario insights: {e}")
            raise

    async def get_learning_dashboard(self) -> LearningDashboard:
        """
        Get learning dashboard data for all scenarios

        Returns:
            Dashboard with aggregated metrics
        """
        try:
            # Aggregate all scenario learning data
            all_scenarios = []
            total_exercises = 0

            for key, data in self.scenario_experience_db.items():
                if key.startswith('scenario_learning_'):
                    all_scenarios.append(data)
                    total_exercises += data['total_uses']

            # Calculate average platform effectiveness
            avg_platform_effectiveness = 0.0
            if all_scenarios:
                effectiveness_scores = [
                    s.get('avg_effectiveness', 0)
                    for s in all_scenarios
                ]
                avg_platform_effectiveness = (
                    sum(effectiveness_scores) / len(effectiveness_scores)
                )

            # Get recent exercise results
            recent_results = []
            for key, data in self.scenario_experience_db.items():
                if key.startswith('exercise_result_'):
                    recent_results.append(data)

            # Sort by completion time
            recent_results.sort(
                key=lambda x: x.get('completed_at', ''),
                reverse=True
            )

            # Top performing scenarios
            top_performing = sorted(
                all_scenarios,
                key=lambda x: x.get('avg_effectiveness', 0),
                reverse=True
            )[:5]

            # Scenarios needing improvement
            needing_improvement = [
                s for s in all_scenarios
                if s.get('avg_effectiveness', 0) < 6.0
            ]

            dashboard = LearningDashboard(
                total_scenarios_with_data=len(all_scenarios),
                total_exercises_completed=total_exercises,
                avg_platform_effectiveness=round(avg_platform_effectiveness, 2),
                recent_exercise_results=recent_results[:10],
                top_performing_scenarios=top_performing,
                scenarios_needing_improvement=needing_improvement
            )

            return dashboard

        except Exception as e:
            logger.error(f"Error generating learning dashboard: {e}")
            raise

    def _extract_feedback_patterns(
        self,
        learning_data: Dict,
        feedback: List[Dict[str, Any]]
    ):
        """Extract patterns from participant feedback"""
        positive_feedback = [
            f for f in feedback
            if f.get('rating', 0) >= 7
        ]
        negative_feedback = [
            f for f in feedback
            if f.get('rating', 0) <= 4
        ]

        for fb in positive_feedback:
            if fb.get('comment'):
                learning_data['patterns']['successful_elements'].append(
                    fb['comment']
                )

        for fb in negative_feedback:
            if fb.get('comment'):
                learning_data['patterns']['common_issues'].append(
                    fb['comment']
                )

    async def _generate_scenario_improvements(
        self,
        learning_data: Dict
    ) -> List[str]:
        """Generate AI-powered scenario improvement recommendations"""
        try:
            # Build learning context for AI
            learning_prompt = f"""
Analyze the following BCM scenario learning data and provide improvement recommendations:

SCENARIO USAGE DATA:
- Total uses: {learning_data['total_uses']}
- Average effectiveness: {learning_data['avg_effectiveness']}/10
- Effectiveness trend: {learning_data['effectiveness_scores'][-5:]}

SUCCESSFUL ELEMENTS:
{self._format_list(learning_data['patterns']['successful_elements'][-5:])}

COMMON ISSUES:
{self._format_list(learning_data['patterns']['common_issues'][-5:])}

IMPROVEMENT AREAS:
{self._format_list(learning_data['patterns']['improvement_areas'][-5:])}

Provide 3-5 specific, actionable recommendations for improving this scenario's effectiveness.
"""

            # Query AI Orchestrator for improvement suggestions
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ai_orchestrator_url}/nlp/query",
                    json={
                        "query": learning_prompt,
                        "context": {
                            "type": "scenario_improvement",
                            "scenario_id": learning_data['scenario_id'],
                            "learning_data": learning_data
                        },
                        "user_role": "scenario_optimizer"
                    }
                )

                if response.status_code == 200:
                    ai_result = response.json()
                    ai_response = ai_result.get("response", "")

                    # Extract recommendations from AI response
                    recommendations = self._extract_recommendations(ai_response)
                    return recommendations[:5]

        except Exception as e:
            logger.error(f"Error generating scenario improvements: {e}")

        # Fallback recommendations
        return [
            "Increase scenario complexity gradually based on participant feedback",
            "Add more realistic time constraints based on actual exercise duration",
            "Enhance participant briefing based on common confusion points",
            "Consider additional stakeholder roles based on lessons learned"
        ]

    def _format_list(self, items: List[str]) -> str:
        """Format list items for prompt"""
        if not items:
            return "- None"
        return '\n'.join(f'- {item}' for item in items)

    def _extract_recommendations(self, ai_response: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = ai_response.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
                clean_line = line.lstrip('-•123456789. ').strip()
                if clean_line:
                    recommendations.append(clean_line)

        return recommendations

    async def _notify_ai_orchestrator_learning(
        self,
        exercise_result: ExerciseResult,
        learning_data: Dict
    ):
        """Notify AI Orchestrator of new learning data"""
        try:
            learning_notification = {
                "type": "exercise_learning",
                "exercise_result": exercise_result.dict(),
                "accumulated_learning": {
                    "scenario_id": learning_data['scenario_id'],
                    "total_uses": learning_data['total_uses'],
                    "avg_effectiveness": learning_data.get('avg_effectiveness', 0),
                    "patterns": learning_data['patterns']
                }
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self.ai_orchestrator_url}/learning/update",
                    json=learning_notification
                )

            logger.info(
                f"Notified AI Orchestrator of learning data for "
                f"scenario {learning_data['scenario_id']}"
            )

        except Exception as e:
            logger.error(f"Failed to notify AI Orchestrator: {e}")
