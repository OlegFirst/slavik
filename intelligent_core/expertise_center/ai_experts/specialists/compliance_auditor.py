"""
Compliance Auditor - AI Expert for ISO 22301 Compliance

Specializes in:
- Clause-by-clause compliance checking
- Gap analysis
- Audit preparation
"""

from ..base.expert_agent import ExpertAgent

class ComplianceAuditor(ExpertAgent):
    """
    Compliance Auditor - проверяет соответствие стандартам

    Example:
        >>> auditor = ComplianceAuditor(knowledge_graph)
        >>> compliance = await auditor.advise(
        ...     "Check my BIA compliance with ISO 22301",
        ...     context={'workflow_id': 'bia_123'}
        ... )
    """

    def __init__(self, knowledge_graph):
        """
        Initialize Compliance Auditor

        Args:
            knowledge_graph: Knowledge graph with ISO 22301 clauses
        """

        # Import tools
        try:
            from ..tools.compliance_tools import (
                ComplianceCheckTool,
                GapAnalysisTool,
                EvidenceValidatorTool
            )

            tools = [
                ComplianceCheckTool(knowledge_graph, workflow_engine=None),
                GapAnalysisTool(knowledge_graph),
                EvidenceValidatorTool()
            ]
        except ImportError:
            tools = []

        super().__init__(
            name="Compliance Auditor",
            role_description="ISO 22301 compliance expert and certification auditor",
            knowledge_sources=[knowledge_graph],
            tools=tools,
            temperature=0.2  # Very factual for compliance
        )

    def _specialization(self) -> str:
        return """ISO 22301 compliance and audit preparation.

You excel at:
- Clause-by-clause compliance checking (citing specific clauses)
- Gap analysis and remediation planning
- Audit evidence validation
- Certification readiness assessment
- Regulatory alignment

Your approach:
- Be precise about requirements (SHALL vs SHOULD)
- Cite specific clause numbers (e.g., "8.2.2 requires...")
- Provide evidence examples
- Give realistic timeframes for remediation
- Consider audit perspectives
"""
