"""
AI Learning Coach - Adaptive Training Intelligence

Extracted and adapted from bcm_training/models/ai_learning_coach.py
Provides personalized coaching, competency gap analysis, and adaptive learning paths
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import aiohttp

logger = logging.getLogger(__name__)


class CoachingStyle(str, Enum):
    """Coaching style options"""
    ADAPTIVE = "adaptive"  # 🎯 Personalized Learning
    INTENSIVE = "intensive"  # 🔥 Accelerated Training
    SUPPORTIVE = "supportive"  # 🤝 Guided Learning
    CHALLENGING = "challenging"  # 💪 Advanced Training


class AILearningCoach:
    """
    AI Learning Coach - Adaptive Training Intelligence

    Features:
    - Competency gap analysis
    - Exercise-based learning integration
    - Personalized learning pathways
    - Performance prediction
    - Adaptive coaching recommendations
    """

    def __init__(
        self,
        coaching_style: CoachingStyle = CoachingStyle.ADAPTIVE,
        ai_orchestrator_url: str = "http://localhost:8000"
    ):
        self.coaching_style = coaching_style
        self.ai_orchestrator_url = ai_orchestrator_url

        # Coach Configuration
        self.exercise_learning_integration = True
        self.performance_tracking = True
        self.adaptive_pathways = True

        # Coach Metrics
        self.learners_coached = 0
        self.competency_improvements = 0.0
        self.learning_acceleration = 0.0

        # Coach Memory
        self.learning_patterns = {}
        self.coaching_effectiveness = {}
        self.learner_preferences = {}

    async def analyze_competency_gaps(
        self,
        organization_id: str,
        learning_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered competency gap analysis

        Args:
            organization_id: Organization identifier
            learning_data: Learning performance data

        Returns:
            {
                'analysis': str,
                'gaps': List[Dict],
                'recommendations': List[Dict],
                'optimization': Dict,
                'personalized_plans': List[Dict]
            }
        """
        try:
            logger.info(f"Starting competency analysis for org {organization_id}")

            # Build analysis prompt
            coaching_prompt = self._build_coaching_prompt(
                organization_id=organization_id,
                learning_data=learning_data
            )

            # Call AI orchestrator for analysis
            result = await self._call_learning_coach_ai(coaching_prompt, learning_data)

            if result:
                # Generate personalized learning plans
                personalized_plans = self._generate_personalized_learning_plans(result)
                result['personalized_plans'] = personalized_plans

                # Update coach metrics
                self.learners_coached += len(learning_data.get('learners', []))
                self.competency_improvements = result.get('predicted_improvement', 0.0)

                logger.info(f"Competency analysis complete: {len(personalized_plans)} plans generated")

                return result
            else:
                logger.warning("AI analysis returned no result")
                return self._fallback_analysis(learning_data)

        except Exception as e:
            logger.error(f"Competency analysis failed: {e}")
            return self._fallback_analysis(learning_data)

    def _build_coaching_prompt(
        self,
        organization_id: str,
        learning_data: Dict[str, Any]
    ) -> str:
        """Build AI coaching prompt"""
        return f"""
AI LEARNING COACH ANALYSIS

COMPETENCY ANALYSIS REQUEST:
Organization: {organization_id}
Coaching Style: {self.coaching_style}
Timestamp: {datetime.utcnow().isoformat()}

LEARNING PERFORMANCE DATA:
{json.dumps(learning_data, indent=2)}

LEARNING COACH INTELLIGENCE REQUIRED:

1. COMPETENCY GAP ANALYSIS:
   - Individual competency assessment
   - Role-based skill gap identification
   - Critical training needs prioritization
   - Learning pathway recommendations

2. EXERCISE-BASED LEARNING:
   - Exercise performance correlation
   - Skill development opportunities
   - Training reinforcement needs
   - Practical application gaps

3. ADAPTIVE LEARNING DESIGN:
   - Personalized learning paths
   - Learning style adaptation
   - Pace optimization recommendations
   - Engagement enhancement strategies

4. PERFORMANCE PREDICTION:
   - Learning outcome forecasting
   - Training effectiveness prediction
   - Competency development timeline
   - ROI optimization opportunities

5. COACHING RECOMMENDATIONS:
   - Individual coaching strategies
   - Group training optimizations
   - Learning reinforcement methods
   - Continuous improvement approaches

Provide ADAPTIVE LEARNING INTELLIGENCE with personalized coaching recommendations.
"""

    async def _call_learning_coach_ai(
        self,
        prompt: str,
        learning_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Call AI Orchestrator for learning analysis"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ai_orchestrator_url}/nlp/query",
                    json={
                        'query': prompt,
                        'context': {
                            'learning_data': learning_data,
                            'ai_organ': 'learning_coach',
                            'coaching_style': self.coaching_style
                        },
                        'user_role': 'learning_coach'
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"AI orchestrator returned status {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Learning coach AI call failed: {e}")
            return None

    def _generate_personalized_learning_plans(
        self,
        ai_analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized learning plans based on AI analysis

        Args:
            ai_analysis_result: AI analysis output

        Returns:
            List of personalized learning plans
        """
        try:
            if not ai_analysis_result:
                logger.warning("No AI analysis result provided for learning plan generation")
                return []

            # Extract competency gaps from AI analysis
            competency_gaps = ai_analysis_result.get('competency_gaps', [])
            learning_style = ai_analysis_result.get('recommended_style', self.coaching_style)

            # Generate learning path recommendations
            learning_plans = []
            for gap in competency_gaps:
                plan = {
                    'competency_area': gap.get('area'),
                    'current_level': gap.get('current_level', 0),
                    'target_level': gap.get('target_level', 5),
                    'learning_modules': gap.get('suggested_modules', []),
                    'estimated_duration': gap.get('duration_hours', 8),
                    'learning_style': learning_style,
                    'priority': gap.get('priority', 'medium'),
                    'created_at': datetime.utcnow().isoformat()
                }
                learning_plans.append(plan)

            logger.info(f"Generated {len(learning_plans)} personalized learning plans")
            return learning_plans

        except Exception as e:
            logger.error(f"Failed to generate personalized learning plans: {e}")
            return []

    def _fallback_analysis(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable"""
        return {
            'analysis': 'Fallback analysis - AI orchestrator unavailable',
            'gaps': self._identify_basic_gaps(learning_data),
            'recommendations': [
                {
                    'area': 'General Training',
                    'recommendation': 'Continue with regular training schedule',
                    'priority': 'medium'
                }
            ],
            'optimization': {
                'message': 'AI-powered optimization unavailable, using basic rules'
            },
            'personalized_plans': []
        }

    def _identify_basic_gaps(self, learning_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Basic gap identification without AI"""
        gaps = []

        # Check exercise performance
        avg_performance = learning_data.get('avg_exercise_performance', 0.0)
        if avg_performance < 0.7:
            gaps.append({
                'area': 'Exercise Performance',
                'current_level': int(avg_performance * 5),
                'target_level': 4,
                'priority': 'high'
            })

        # Check competency areas
        for area in learning_data.get('competency_areas', []):
            gaps.append({
                'area': area,
                'current_level': 3,
                'target_level': 5,
                'priority': 'medium',
                'suggested_modules': [f"{area} training module"]
            })

        return gaps

    async def track_learning_progress(
        self,
        learner_id: str,
        completed_activity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track learner progress and update coaching strategy

        Args:
            learner_id: Learner identifier
            completed_activity: Completed learning activity data

        Returns:
            Updated progress and next recommendations
        """
        try:
            # Update learner preferences
            if learner_id not in self.learner_preferences:
                self.learner_preferences[learner_id] = {
                    'activities_completed': 0,
                    'preferred_style': None,
                    'performance_trend': []
                }

            learner_pref = self.learner_preferences[learner_id]
            learner_pref['activities_completed'] += 1
            learner_pref['performance_trend'].append(
                completed_activity.get('score', 0.0)
            )

            # Analyze progress
            avg_performance = sum(learner_pref['performance_trend']) / len(learner_pref['performance_trend'])

            return {
                'learner_id': learner_id,
                'activities_completed': learner_pref['activities_completed'],
                'avg_performance': avg_performance,
                'recommended_next_steps': self._recommend_next_steps(avg_performance),
                'coaching_adjustment': self._adjust_coaching_style(avg_performance)
            }

        except Exception as e:
            logger.error(f"Progress tracking failed: {e}")
            return {'error': str(e)}

    def _recommend_next_steps(self, avg_performance: float) -> List[str]:
        """Recommend next learning steps based on performance"""
        if avg_performance >= 0.85:
            return [
                "Advance to challenging scenarios",
                "Mentor other learners",
                "Explore advanced topics"
            ]
        elif avg_performance >= 0.70:
            return [
                "Continue current learning path",
                "Practice key scenarios",
                "Review difficult concepts"
            ]
        else:
            return [
                "Review foundational concepts",
                "Schedule coaching session",
                "Complete remedial exercises"
            ]

    def _adjust_coaching_style(self, avg_performance: float) -> str:
        """Adjust coaching style based on performance"""
        if avg_performance >= 0.85:
            return CoachingStyle.CHALLENGING
        elif avg_performance >= 0.70:
            return CoachingStyle.ADAPTIVE
        else:
            return CoachingStyle.SUPPORTIVE

    def format_learning_plans_html(self, plans: List[Dict[str, Any]]) -> str:
        """Format learning plans as HTML for display"""
        html_content = "<h3>🎯 Personalized Learning Plans</h3>"

        for i, plan in enumerate(plans, 1):
            html_content += f"""
            <div class="learning-plan">
                <h4>{i}. {plan['competency_area']}</h4>
                <p><strong>Current Level:</strong> {plan['current_level']}/5</p>
                <p><strong>Target Level:</strong> {plan['target_level']}/5</p>
                <p><strong>Learning Style:</strong> {plan['learning_style']}</p>
                <p><strong>Estimated Duration:</strong> {plan['estimated_duration']} hours</p>
                <p><strong>Priority:</strong> {plan['priority']}</p>
                <ul>
                    {''.join(f"<li>{module}</li>" for module in plan.get('learning_modules', []))}
                </ul>
            </div>
            """

        return html_content

    def get_coaching_effectiveness_report(self) -> Dict[str, Any]:
        """Get coaching effectiveness metrics"""
        return {
            'learners_coached': self.learners_coached,
            'competency_improvements': self.competency_improvements,
            'learning_acceleration': self.learning_acceleration,
            'coaching_style': self.coaching_style,
            'total_learning_patterns': len(self.learning_patterns),
            'learner_preferences_tracked': len(self.learner_preferences)
        }
