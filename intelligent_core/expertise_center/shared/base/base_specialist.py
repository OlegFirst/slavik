"""
Base Specialist - Strategic Expert AI

Specialists = Strategic level experts (3)
- Deep analysis
- Strategic recommendations
- Complex decision support
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# AI Foundation integration
from intelligent_core.ai_foundation import RAGPipeline, LLMRouter, ContextBuilder


class BaseSpecialist(ABC):
    """
    Base class for Strategic AI Specialists

    Used for:
    - BCM Advisor (strategic BCM guidance)
    - Compliance Auditor (compliance analysis)
    - Strategic Planner (strategic planning)

    Integrated with ai-foundation:
    - self.rag: RAGPipeline for knowledge retrieval
    - self.llm: LLMRouter for strategic analysis
    - self.context_builder: ContextBuilder for context enrichment
    """

    def __init__(
        self,
        specialist_id: str,
        name: str,
        specialty: str,
        domain: str = "bcm"
    ):
        self.specialist_id = specialist_id
        self.name = name
        self.specialty = specialty
        self.domain = domain

        # AI Foundation integrations (available to all specialists)
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()

    @abstractmethod
    async def analyze(
        self,
        context: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Strategic analysis

        Args:
            context: Analysis context
            query: Strategic question

        Returns:
            Strategic analysis result
        """
        pass

    @abstractmethod
    async def recommend(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations

        Args:
            analysis: Analysis results

        Returns:
            List of strategic recommendations
        """
        pass

    async def get_capabilities(self) -> List[str]:
        """Get specialist capabilities"""
        return []

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.specialist_id} name={self.name}>"
