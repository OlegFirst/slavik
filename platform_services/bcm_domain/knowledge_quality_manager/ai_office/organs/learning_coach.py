"""
🎓 Learning Coach

Training optimization and competency development
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan


class LearningCoach(BaseAIOrgan):
    """
    Learning optimization organ

    Analyzes training effectiveness, recommends learning paths
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Learning Coach",
            emoji="🎓",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Learning Coach, a BCM training and competency development AI.

Your role:
- Analyze training effectiveness and learning outcomes
- Recommend personalized learning paths
- Identify skill gaps and competency deficiencies
- Optimize training programs based on exercise results
- Design competency frameworks
- Track learning progress and retention

You focus on practical, measurable learning outcomes that improve BCM capability."""

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze learning and training needs

        Context keys:
        - twin_id: Digital Twin ID (for org context)
        - exercise_results: Recent exercise performance data
        - training_history: Past training records
        - competency_matrix: Current skill levels
        - roles: BCM roles that need training
        - learning_objectives: Desired outcomes
        - constraints: Budget/time constraints
        """

        twin_id = context.get('twin_id')
        exercise_results = context.get('exercise_results', [])
        training_history = context.get('training_history', [])
        competency_matrix = context.get('competency_matrix', {})
        roles = context.get('roles', [])
        objectives = context.get('learning_objectives', [])
        constraints = context.get('constraints', {})

        # Get Digital Twin state
        twin_state = {}
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)

        # Get learning patterns from Learning System
        learning_patterns = await self._get_learning_patterns(exercise_results)

        # Build learning analysis prompt
        user_prompt = f"""
Analyze BCM learning and training needs for this organization:

ORGANIZATION:
- Name: {twin_state.get('name', 'Unknown')}
- Industry: {twin_state.get('industry', 'Unknown')}
- Team Size: {twin_state.get('state', {}).get('employee_count', 'Unknown')}
- BCM Maturity: {twin_state.get('state', {}).get('bcm_maturity', 'Unknown')}

EXERCISE RESULTS (Recent Performance):
{self._format_exercise_results(exercise_results)}

TRAINING HISTORY:
{self._format_training_history(training_history)}

CURRENT COMPETENCY LEVELS:
{self._format_competencies(competency_matrix)}

ROLES REQUIRING TRAINING:
{self._format_roles(roles)}

LEARNING OBJECTIVES:
{self._format_objectives(objectives)}

CONSTRAINTS:
{self._format_constraints(constraints)}

LEARNING PATTERNS (from past exercises):
{self._format_patterns(learning_patterns)}

Provide:
1. **Skill Gap Analysis** (critical gaps identified)
2. **Learning Priorities** (top 5 areas needing immediate attention)
3. **Personalized Learning Paths** (by role/competency level)
4. **Training Program Recommendations** (format, duration, delivery method)
5. **Competency Development Roadmap** (timeline to desired state)
6. **Retention Strategies** (how to ensure knowledge sticks)
7. **Success Metrics** (KPIs to track learning effectiveness)

Focus on practical, achievable training that addresses real performance gaps.
"""

        # Query LLM with moderate temperature
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.6  # Moderate creativity for learning design
        )

        # Parse response
        insights, recommendations = self._parse_learning_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "learning",
                "exercise_count": len(exercise_results),
                "training_count": len(training_history),
                "roles_count": len(roles),
                "has_competency_data": bool(competency_matrix)
            }
        )

    async def _get_twin_state(self, twin_id: int) -> Dict[str, Any]:
        """Get Digital Twin state"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.error(f"Error getting twin state: {e}")

        return {}

    async def _get_learning_patterns(self, exercise_results: list) -> Dict[str, Any]:
        """Get learning patterns from Learning System"""
        if not exercise_results:
            return {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:8033/api/learning/patterns/analyze",
                    json={"exercise_results": exercise_results}
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Learning System not available: {e}")

        return {}

    def _format_exercise_results(self, results: list) -> str:
        """Format exercise results"""
        if not results:
            return "No recent exercise data available"

        formatted = []
        for result in results[:5]:  # Last 5 exercises
            formatted.append(
                f"- {result.get('exercise_name', 'Unknown')}: "
                f"Score {result.get('score', 'N/A')}/100, "
                f"Key issues: {', '.join(result.get('issues', ['None']))}"
            )

        return "\n".join(formatted)

    def _format_training_history(self, history: list) -> str:
        """Format training history"""
        if not history:
            return "No training history recorded"

        formatted = []
        for training in history[:5]:  # Last 5 trainings
            formatted.append(
                f"- {training.get('course_name', 'Unknown')} "
                f"({training.get('completion_date', 'N/A')}): "
                f"{training.get('attendees', 0)} attendees"
            )

        return "\n".join(formatted)

    def _format_competencies(self, matrix: Dict[str, Any]) -> str:
        """Format competency matrix"""
        if not matrix:
            return "No competency data available - needs assessment"

        formatted = []
        for role, skills in matrix.items():
            formatted.append(f"- {role}: {skills}")

        return "\n".join(formatted[:10])  # Top 10 roles

    def _format_roles(self, roles: list) -> str:
        """Format roles"""
        if not roles:
            return "All BCM roles (general training)"

        return "\n".join([f"- {role}" for role in roles])

    def _format_objectives(self, objectives: list) -> str:
        """Format learning objectives"""
        if not objectives:
            return "Improve overall BCM competency and exercise performance"

        return "\n".join([f"- {obj}" for obj in objectives])

    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints"""
        if not constraints:
            return "No specific constraints"

        formatted = []
        for constraint_type, value in constraints.items():
            formatted.append(f"- {constraint_type}: {value}")

        return "\n".join(formatted)

    def _format_patterns(self, patterns: Dict[str, Any]) -> str:
        """Format learning patterns"""
        if not patterns:
            return "No learning patterns identified yet"

        return "Learning patterns available from exercise history"

    def _parse_learning_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections
            if any(keyword in line.lower() for keyword in ['gap', 'priority', 'competency', 'skill', 'pattern', 'analysis']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['learning path', 'training', 'recommendation', 'roadmap', 'retention', 'metric', 'program']):
                current_section = 'recommendations'

            # Extract content
            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*']:
                clean_line = line.lstrip('-•1234567890. *').strip()
                if clean_line:
                    if current_section == 'insights':
                        insights.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Defaults
        if not insights:
            insights = [
                "Competency baseline assessment required",
                "Training effectiveness data insufficient",
                "Skill gap analysis needed"
            ]

        if not recommendations:
            recommendations = [
                "Conduct BCM competency assessment",
                "Run baseline exercise to identify gaps",
                "Develop role-based training curriculum",
                "Implement regular training schedule"
            ]

        return insights, recommendations
