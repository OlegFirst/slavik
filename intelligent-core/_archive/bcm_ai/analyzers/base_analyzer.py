"""
Base Analyzer Class
Fast LLM analysis layer for BCM AI system
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import json


class BaseAnalyzer(ABC):
    """
    Base class for all BCM AI Analyzers

    Responsibilities:
    - LLM prompt building
    - Claude/GPT invocation
    - Structured output parsing
    - Stateless analysis
    """

    def __init__(self, llm_router=None, temperature: float = 0.7):
        """
        Initialize Analyzer

        Args:
            llm_router: LLM router for Claude/GPT
            temperature: LLM temperature (0.0-1.0)
        """
        self.llm_router = llm_router
        self.temperature = temperature

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method

        Args:
            context: Analysis context (data, params, etc.)

        Returns:
            {
                'insights': List[str],
                'recommendations': List[str],
                'confidence': float,
                'raw_response': str
            }
        """
        # 1. Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        # 2. Query LLM
        llm_response = await self._query_llm(system_prompt, user_prompt)

        # 3. Parse response
        parsed = self._parse_response(llm_response)

        # 4. Calculate confidence
        confidence = self._calculate_confidence(parsed, context)

        return {
            'insights': parsed.get('insights', []),
            'recommendations': parsed.get('recommendations', []),
            'confidence': confidence,
            'raw_response': llm_response
        }

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """
        Build system prompt for this analyzer

        Must be implemented by subclass
        Defines analyzer's role and capabilities
        """
        pass

    @abstractmethod
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build user prompt from context

        Must be implemented by subclass
        Converts context data into LLM query
        """
        pass

    async def _query_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Query LLM with prompts

        Args:
            system_prompt: System prompt
            user_prompt: User prompt

        Returns:
            LLM response text
        """
        if not self.llm_router:
            raise ValueError("LLM Router not configured")

        try:
            response = await self.llm_router.generate(
                system=system_prompt,
                user=user_prompt,
                temperature=self.temperature
            )
            return response
        except Exception as e:
            print(f"LLM query error: {e}")
            raise

    def _parse_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured output

        Tries JSON first, then fallback to text parsing
        """
        # Try JSON parsing
        try:
            # Look for JSON block in response
            if '```json' in llm_response:
                json_start = llm_response.find('```json') + 7
                json_end = llm_response.find('```', json_start)
                json_str = llm_response[json_start:json_end].strip()
                return json.loads(json_str)
            elif llm_response.strip().startswith('{'):
                return json.loads(llm_response)
        except json.JSONDecodeError:
            pass

        # Fallback: text parsing
        return self._parse_text_response(llm_response)

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """
        Fallback text parser

        Extracts insights and recommendations from plain text
        """
        insights = []
        recommendations = []

        lines = text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if 'insights' in line.lower() or 'анализ' in line.lower():
                current_section = 'insights'
                continue
            elif 'recommendation' in line.lower() or 'рекомендаци' in line.lower():
                current_section = 'recommendations'
                continue

            # Extract content
            if current_section == 'insights':
                if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                    insights.append(line.lstrip('•-*123. '))
            elif current_section == 'recommendations':
                if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                    recommendations.append(line.lstrip('•-*123. '))

        # If no sections found, treat entire response as insight
        if not insights and not recommendations:
            insights = [text]

        return {
            'insights': insights,
            'recommendations': recommendations
        }

    def _calculate_confidence(
        self,
        parsed: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score

        Override in subclass for specific confidence calculation
        Default: based on content completeness
        """
        score = 0.5  # baseline

        # Has insights
        if parsed.get('insights'):
            score += 0.2

        # Has recommendations
        if parsed.get('recommendations'):
            score += 0.2

        # Has data in context
        if context.get('data'):
            score += 0.1

        return min(score, 1.0)

    def _format_insights(self, insights: list) -> str:
        """Format insights for display"""
        if not insights:
            return ""
        return "\n".join([f"• {insight}" for insight in insights])

    def _format_recommendations(self, recommendations: list) -> str:
        """Format recommendations for display"""
        if not recommendations:
            return ""
        return "\n".join([f"• {rec}" for rec in recommendations])
