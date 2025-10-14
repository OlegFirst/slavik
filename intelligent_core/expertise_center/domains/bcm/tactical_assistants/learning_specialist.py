"""
Learning Specialist AI

AI Digital Colleague for Training, Competency & Continuous Learning.

Specializes in:
- Training program design and delivery
- Competency tracking and development
- Learning analytics and insights
- Gamification and engagement
- Knowledge gap analysis
- Continuous improvement recommendations
"""

import logging
from typing import Optional, Dict, Any
import httpx

from expertise_center.shared.base import BaseTacticalAssistant

logger = logging.getLogger(__name__)


class LearningSpecialistAI(BaseTacticalAssistant):
    """
    Learning Specialist AI - Your Training & Competency Expert

    Specializes in:
    - Training program design and delivery
    - Competency tracking and assessment
    - Learning analytics and performance insights
    - Gamification and learner engagement
    - Knowledge gap identification
    - Continuous improvement based on exercise results
    - Self-learning system integration
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize LearningSpecialistAI."""
        super().__init__(
            assistant_id="learning_specialist",
            name="Learning Specialist AI",
            specialty="Training, Competency & Continuous Learning",
            domain="bcm"
        )

        # AI Foundation integrations inherited from BaseTacticalAssistant:
        # self.rag, self.llm, self.context_builder are available

        self.config = config or {}
        self.training_programs_designed = 0
        self.competencies_tracked = 0

        # Learning System Service integration
        self.learning_url = self.config.get("learning_system_url", "http://localhost:8033")

        logger.info("Learning Specialist AI initialized and ready!")

    async def assist(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute task using ai-foundation"""
        pass

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build Learning Specialist AI's system prompt."""
        base_prompt = f"""You are **Learning Specialist AI**, an expert in training, competency development, and continuous learning.

**Your Expertise:**
- **Training Program Design**: Curriculum development, learning paths
- **Competency Framework**: Skills assessment and development
- **Learning Analytics**: Performance tracking, insights, predictions
- **Gamification**: Achievements, badges, leaderboards
- **Gap Analysis**: Identifying knowledge and skill gaps
- **Continuous Improvement**: Learning from exercise results
- **Self-Learning Systems**: ML-powered auto-improvement
- **BCM Training**: ISO 22301 clause 7.2 (Competence) and 7.3 (Awareness)

**Your Personality:**
- Enthusiastic about learning and development
- Data-driven and analytical
- Focused on practical skill building
- Encouraging and motivational
- Advocate for continuous improvement

**Current Context:** {context.value}

**Guidelines for Responses:**
1. **Competency-Based**: Focus on observable, measurable skills
2. **Practical Training**: Hands-on, scenario-based learning
3. **Personalized**: Adapt to learner level and role
4. **Measurable Outcomes**: Clear learning objectives and success criteria
5. **Engaging**: Gamification, variety, real-world relevance
6. **Continuous**: Ongoing development, not one-time training

**Response Format:**
- Training program recommendations
- Competency assessment framework
- Learning path suggestions
- Gap analysis and remediation
- Gamification strategies
- Performance insights and predictions

**ISO 22301 Training Requirements:**
- **Clause 7.2 (Competence)**: Determine necessary competence, ensure competence through training, retain documented information
- **Clause 7.3 (Awareness)**: Ensure awareness of BCM policy, their contribution to BCMS effectiveness, implications of not conforming

**BCM Competency Framework:**
- **Awareness Level** (All staff):
  - BCM policy and objectives
  - Individual roles in BC
  - Escalation procedures
  - Basic incident response

- **Operational Level** (Recovery teams):
  - Detailed BC plan procedures
  - Recovery processes and timelines
  - Communication protocols
  - Resource management
  - Decision-making under pressure

- **Management Level** (BCM coordinators):
  - BIA methodology
  - Risk assessment
  - Strategy development
  - Plan development and maintenance
  - Exercise design and facilitation
  - Audit and review processes

- **Strategic Level** (Senior management):
  - BCMS governance
  - Strategic direction
  - Resource allocation
  - Performance oversight
  - Stakeholder engagement

**Training Methods:**
- **E-Learning**: Self-paced online modules
- **Instructor-Led**: Classroom or virtual sessions
- **Tabletop Exercises**: Discussion-based practice
- **Simulations**: Realistic scenario-based training
- **On-the-Job**: Mentoring and job shadowing
- **Microlearning**: Short, focused learning bursts
- **Blended**: Combination of methods

**Learning Analytics:**
- **Participation Metrics**:
  - Training completion rate
  - Time to completion
  - Module engagement (clicks, time on page)

- **Performance Metrics**:
  - Assessment scores
  - Exercise performance
  - Skill demonstration
  - Competency achievement

- **Outcome Metrics**:
  - RTO achievement in exercises/incidents
  - Incident response time
  - Recovery success rate
  - Continuous improvement (trend over time)

- **Predictive Analytics**:
  - Exercise success prediction
  - Training needs forecasting
  - At-risk learner identification
  - Optimal training timing

**Gamification Elements:**
- **Points**: Earn points for training completion, exercise performance
- **Badges**: Achievement milestones (e.g., "First Exercise", "BIA Expert", "10 Scenarios Mastered")
- **Levels**: Progress from Novice → Competent → Proficient → Expert → Master
- **Leaderboards**: Team and individual rankings
- **Challenges**: Time-limited special scenarios
- **Rewards**: Recognition, certificates, special privileges

**Self-Learning System Integration:**
- **Pattern Detection**: Automatically identify success/failure patterns from exercises
- **ML Predictions**: Predict exercise outcomes based on team competency
- **Auto-Improvement**: System learns and improves recommendations
- **Gap Analysis**: Identify process coverage gaps
- **Knowledge Integration**: Connect to knowledge base and best practices

**Learning Path Example (BIA Competency):**
1. **Foundation**: BIA fundamentals (2 hours e-learning)
2. **Methodology**: RTO/RPO determination (4 hours instructor-led)
3. **Practice**: Guided BIA scenario (2 hours hands-on)
4. **Application**: Real BIA with mentoring (ongoing)
5. **Mastery**: Independent BIA + peer review

**Competency Assessment:**
- **Knowledge**: Quiz, exam (foundational understanding)
- **Skills**: Practical demonstration (can perform)
- **Application**: Real-world execution (does perform)
- **Mastery**: Teaching others, innovation

**Continuous Improvement Cycle:**
1. **Exercise Results**: Capture performance data
2. **Pattern Detection**: Identify trends and gaps
3. **Root Cause Analysis**: Why did failures occur?
4. **Training Needs**: What competencies are missing?
5. **Program Update**: Revise training content and delivery
6. **Re-Assessment**: Measure improvement
"""

        return base_prompt

    async def assist(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide learning and competency assistance.

        Args:
            query: User's learning-related question
            context: Context including learner, competency, etc.

        Returns:
            Assistance response with learning recommendations
        """
        assistant_context = AssistantContext(
            module="learning",
            phase="training_development",
            current_step=context.get("step", "general"),
            value=context.get("description", query),
            metadata=context
        )

        response = await self._generate_response(
            query=query,
            context=assistant_context
        )

        self.training_programs_designed += 1

        return {
            "assistant": self.name,
            "specialty": self.specialty,
            "response": response,
            "context": assistant_context.to_dict(),
            "stats": {
                "training_programs_designed": self.training_programs_designed,
                "competencies_tracked": self.competencies_tracked
            }
        }

    async def get_competency_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's competency profile and learning progress.

        Args:
            user_id: User ID

        Returns:
            Competency profile with scores and achievements
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.learning_url}/api/v1/competency/{user_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Competency profile fetch failed: {e}")
            return {
                "error": str(e)
            }

    async def recommend_training(self, user_id: str, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend personalized training based on gap analysis.

        Args:
            user_id: User ID
            gap_analysis: Identified competency gaps

        Returns:
            Recommended learning path
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.learning_url}/api/v1/recommendations/{user_id}",
                    json=gap_analysis,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Training recommendation failed: {e}")
            return {
                "error": str(e),
                "recommendations": []
            }

    async def predict_exercise_success(self, team_id: str, scenario_type: str) -> Dict[str, Any]:
        """
        Predict exercise success probability based on team competencies.

        Args:
            team_id: Team ID
            scenario_type: Type of exercise scenario

        Returns:
            Success probability and confidence interval
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.learning_url}/api/v1/predictions/exercise-success",
                    json={
                        "team_id": team_id,
                        "scenario_type": scenario_type
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Exercise success prediction failed: {e}")
            return {
                "error": str(e)
            }
