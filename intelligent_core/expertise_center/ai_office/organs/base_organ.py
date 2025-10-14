"""
Base AI Organ

Abstract class for all AI organs
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)


class BaseAIOrgan(ABC):
    """Base class for all AI organs"""

    def __init__(self, organ_name: str, emoji: str, llm_router=None):
        self.organ_name = organ_name
        self.emoji = emoji
        self.llm_router = llm_router
        self.logger = logger

    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze input and generate insights

        Args:
            context: Analysis context (varies by organ)

        Returns:
            Analysis results with insights and recommendations
        """
        pass

    def _build_system_prompt(self) -> str:
        """Build system prompt for this organ"""
        return f"You are the {self.organ_name}, a specialized AI for BCM."

    async def _query_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Query LLM via router

        Args:
            system_prompt: System instruction
            user_prompt: User query
            temperature: LLM temperature (0.0 - 1.0)

        Returns:
            LLM response text
        """
        start_time = time.time()

        if self.llm_router:
            response = await self.llm_router.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature
            )
        else:
            # Mock response if no LLM router
            response = f"[MOCK] Analysis from {self.organ_name}:\n\n{user_prompt[:200]}..."

        execution_time = (time.time() - start_time) * 1000  # ms

        self.logger.info(f"{self.emoji} {self.organ_name} completed in {execution_time:.0f}ms")

        return response

    def _calculate_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for analysis

        Override in subclasses for specific logic
        """
        # Default confidence based on presence of insights
        if analysis_result.get('insights'):
            return 0.85
        elif analysis_result.get('recommendations'):
            return 0.75
        else:
            return 0.50

    def format_response(self, insights: list, recommendations: list, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format organ response"""
        result = {
            "organ": self.organ_name,
            "emoji": self.emoji,
            "insights": insights,
            "recommendations": recommendations,
            "metadata": metadata or {}
        }

        result["confidence"] = self._calculate_confidence(result)

        return result
