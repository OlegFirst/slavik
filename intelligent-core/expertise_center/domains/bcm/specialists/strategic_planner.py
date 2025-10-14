"""
Strategic Planner - AI Expert for BCM Program Strategy

Specializes in:
- Long-term BCM roadmap development
- Resource planning
- Maturity advancement
"""

from typing import Dict, Any, Optional, List
from expertise_center.shared.base import BaseSpecialist

class StrategicPlanner(BaseSpecialist):
    """
    Strategic Planner - долгосрочное планирование BCM

    Example:
        >>> planner = StrategicPlanner(case_library, ml_predictor)
        >>> roadmap = await planner.advise(
        ...     "Create 12-month BCM roadmap for our organization",
        ...     context={'industry': 'finance', 'current_maturity': 'initial'}
        ... )
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize StrategicPlanner."""
        super().__init__(
            specialist_id="strategic_planner",
            name="StrategicPlanner",
            specialty="Strategic BCM Analysis",
            domain="bcm"
        )

        # AI Foundation integrations inherited from BaseSpecialist:
        # self.rag, self.llm, self.context_builder are available

        self.config = config or {}

    async def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Strategic analysis using ai-foundation

        Args:
            context: Analysis context
            query: Analysis query

        Returns:
            Analysis results with recommendations
        """
        # Build context using ai-foundation
        enriched_context = await self.context_builder.build(context, query)

        # Use RAG to find relevant knowledge
        rag_results = await self.rag.search(query, context)

        # Use LLM for strategic analysis
        analysis = await self.llm.generate(
            task_type="strategic_analysis",
            messages=[
                {"role": "system", "content": f"You are {self.name}, a {self.specialty} expert."},
                {"role": "user", "content": f"Context: {enriched_context}\n\nQuery: {query}"}
            ]
        )

        return {
            "analysis": analysis,
            "context": enriched_context,
            "knowledge": rag_results,
            "specialist": self.name
        }

    async def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations

        Args:
            analysis: Analysis results

        Returns:
            List of recommendations
        """
        recommendations_prompt = f"""
        Based on this analysis:
        {analysis.get('analysis', '')}

        Generate strategic recommendations.
        """

        recommendations = await self.llm.generate(
            task_type="content_generation",
            messages=[
                {"role": "system", "content": f"You are {self.name}, generating strategic recommendations."},
                {"role": "user", "content": recommendations_prompt}
            ]
        )

        return [
            {
                "recommendation": recommendations,
                "priority": "high",
                "specialist": self.name
            }
        ]
