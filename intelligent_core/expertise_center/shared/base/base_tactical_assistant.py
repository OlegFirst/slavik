"""
Base Tactical Assistant (BCM Expert) AI

Tactical Assistants = Operational level BCM experts (12)
- Specific task execution
- Quick answers
- Workflow support
- Domain-specific operations
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# AI Foundation integration
from intelligent_core.ai_foundation import RAGPipeline, LLMRouter, ContextBuilder


class BaseTacticalAssistant(ABC):
    """
    Base class for Tactical AI Assistants (BCM Experts)

    Used for:
    - BIA Specialist
    - Risk Analyst
    - Project Manager
    - Incident Advisor
    - Plan Generator
    - Compliance Copilot
    - Exercise Designer
    - Documents Specialist
    - Governance Specialist
    - Validation Specialist
    - Community Specialist
    - Learning Specialist

    Integrated with ai-foundation:
    - self.rag: RAGPipeline for knowledge retrieval
    - self.llm: LLMRouter for tactical AI operations
    - self.context_builder: ContextBuilder for context enrichment
    """

    def __init__(
        self,
        assistant_id: str,
        name: str,
        specialty: str,
        domain: str = "bcm"
    ):
        self.assistant_id = assistant_id
        self.name = name
        self.specialty = specialty
        self.domain = domain

        # AI Foundation integrations (available to all tactical assistants)
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()

    @abstractmethod
    async def assist(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide tactical assistance

        Args:
            task: Task description
            context: Task context

        Returns:
            Assistance result
        """
        pass

    @abstractmethod
    async def validate(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate task data

        Args:
            data: Data to validate

        Returns:
            Validation result
        """
        pass

    async def get_capabilities(self) -> List[str]:
        """Get assistant capabilities"""
        return []

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.assistant_id} specialty={self.specialty}>"
