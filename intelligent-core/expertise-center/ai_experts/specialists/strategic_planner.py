"""
Strategic Planner - AI Expert for BCM Program Strategy

Specializes in:
- Long-term BCM roadmap development
- Resource planning
- Maturity advancement
"""

from ..base.expert_agent import ExpertAgent

class StrategicPlanner(ExpertAgent):
    """
    Strategic Planner - долгосрочное планирование BCM

    Example:
        >>> planner = StrategicPlanner(case_library, ml_predictor)
        >>> roadmap = await planner.advise(
        ...     "Create 12-month BCM roadmap for our organization",
        ...     context={'industry': 'finance', 'current_maturity': 'initial'}
        ... )
    """

    def __init__(self, case_library, ml_predictor):
        """
        Initialize Strategic Planner

        Args:
            case_library: Case library for benchmarking
            ml_predictor: ML predictor for timeline forecasting
        """

        # Import tools
        try:
            from ..tools.strategic_tools import (
                TimelinePredictorTool,
                ResourcePlannerTool,
                MaturityAssessmentTool
            )

            tools = [
                TimelinePredictorTool(ml_predictor),
                ResourcePlannerTool(case_library),
                MaturityAssessmentTool()
            ]
        except ImportError:
            tools = []

        super().__init__(
            name="Strategic Planner",
            role_description="BCM strategic advisor for long-term resilience planning",
            knowledge_sources=[case_library],
            tools=tools,
            temperature=0.4  # Strategic thinking
        )

    def _specialization(self) -> str:
        return """strategic BCM program development and maturity advancement.

You excel at:
- Multi-year BCM roadmap development
- Resource planning and budgeting
- Maturity model assessment (using ML predictions)
- Executive communication and buy-in
- Phased implementation planning

Your approach:
- Think long-term (12-24 months minimum)
- Balance quick wins with strategic goals
- Consider budget and resource constraints realistically
- Provide executive-level communication tips
- Use industry benchmarks for planning
"""
