"""
BCM Advisor - AI Expert for Business Continuity Management

Specializes in:
- Business Impact Analysis (BIA)
- Recovery strategies
- BCM planning
"""

from ..base.expert_agent import ExpertAgent

class BCMAdvisor(ExpertAgent):
    """
    BCM Advisor - помогает с BIA, планированием, стратегией

    Example:
        >>> advisor = BCMAdvisor(case_library, knowledge_graph)
        >>> advice = await advisor.advise(
        ...     "How should I identify critical processes for healthcare?",
        ...     context={'industry': 'healthcare', 'size': 'medium'}
        ... )
    """

    def __init__(self, case_library, knowledge_graph):
        """
        Initialize BCM Advisor

        Args:
            case_library: Case library instance for searching similar cases
            knowledge_graph: Knowledge graph with ISO standards
        """

        # Import tools
        try:
            from ..tools.bia_tools import BIAAnalysisTool, DependencyMapperTool
            from ..tools.case_library_tool import CaseSearchTool

            tools = [
                BIAAnalysisTool(workflow_engine=None),  # Will be injected
                DependencyMapperTool(case_library),
                CaseSearchTool(case_library)
            ]
        except ImportError:
            tools = []  # Graceful fallback

        super().__init__(
            name="BCM Advisor",
            role_description="Business Continuity Management expert specializing in BIA and strategy development",
            knowledge_sources=[knowledge_graph, case_library],
            tools=tools,
            temperature=0.3  # Factual but helpful
        )

    def _specialization(self) -> str:
        return """business impact analysis, recovery strategies, and BCM planning.

You excel at:
- Identifying critical business processes
- Calculating recovery time objectives (RTOs)
- Designing recovery strategies
- Finding patterns in similar organizations' approaches
- Practical dependency mapping

Your approach:
- Start with business needs, not technology
- Consider regulatory and compliance requirements
- Use real-world examples when available
- Be realistic about resource constraints
"""
