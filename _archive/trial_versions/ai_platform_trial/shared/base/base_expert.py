"""
Base Expert Class

Unified base for all AI experts in the platform
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseExpert(ABC):
    """
    Base class for all AI Experts

    Experts are user-facing consultants that provide advice and guidance.
    They use Tools and Organs to accomplish their tasks.

    Hierarchy:
    - TOP Manager delegates to Expert
    - Expert uses Tools for structured operations
    - Expert uses Organs for heavy computations
    """

    def __init__(
        self,
        name: str,
        segment: str,  # 'governance', 'platform', or 'domain'
        specialization: str,
        description: str,
        tools: Optional[List[Any]] = None,
        organs: Optional[List[Any]] = None,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize Expert

        Args:
            name: Expert name (e.g., "BIA Specialist")
            segment: Segment this expert belongs to
            specialization: What this expert specializes in
            description: Detailed description of capabilities
            tools: List of Tool instances this expert can use
            organs: List of Organ instances this expert can delegate to
            llm_client: AI client for reasoning
        """
        self.name = name
        self.segment = segment
        self.specialization = specialization
        self.description = description
        self.tools = tools or []
        self.organs = organs or []
        self.llm_client = llm_client
        self.logger = logger

        # Metrics
        self.requests_handled = 0
        self.avg_response_time = 0.0
        self.success_rate = 1.0

    @abstractmethod
    async def handle_request(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle user request

        Args:
            user_query: User's question or request
            context: Context information (user_id, organization, history, etc.)

        Returns:
            Response with advice, recommendations, and actions taken
        """
        pass

    @abstractmethod
    def can_handle(self, user_query: str, context: Dict[str, Any]) -> float:
        """
        Determine if this expert can handle the request

        Args:
            user_query: User's question
            context: Context information

        Returns:
            Confidence score (0.0 - 1.0)
        """
        pass

    async def use_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use a tool by name

        Args:
            tool_name: Name of the tool to use
            parameters: Parameters for the tool

        Returns:
            Tool execution result
        """
        for tool in self.tools:
            if tool.name == tool_name:
                self.logger.info(f"{self.name} using tool: {tool_name}")
                return await tool.execute(parameters)

        raise ValueError(f"Tool '{tool_name}' not available to {self.name}")

    async def delegate_to_organ(
        self,
        organ_name: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Delegate heavy computation to an organ

        Args:
            organ_name: Name of the organ
            task: Task specification

        Returns:
            Organ execution result
        """
        for organ in self.organs:
            if organ.name == organ_name:
                self.logger.info(f"{self.name} delegating to organ: {organ_name}")
                return await organ.process(task)

        raise ValueError(f"Organ '{organ_name}' not available to {self.name}")

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM"""
        return f"""You are {self.name}, an AI expert in {self.specialization}.

Segment: {self.segment.upper()}

Description:
{self.description}

Your role:
- Provide expert advice and guidance
- Use available tools when appropriate
- Delegate heavy computations to organs
- Be practical and actionable
- Consider regulatory and compliance requirements
- Base recommendations on real-world patterns

Available tools:
{chr(10).join([f"- {tool.name}: {tool.description}" for tool in self.tools])}

Available organs:
{chr(10).join([f"- {organ.name}: {organ.description}" for organ in self.organs])}
"""

    async def _query_llm(
        self,
        user_prompt: str,
        context: Dict[str, Any],
        temperature: float = 0.3
    ) -> str:
        """
        Query LLM for reasoning

        Args:
            user_prompt: User's question
            context: Context information
            temperature: LLM temperature

        Returns:
            LLM response
        """
        if not self.llm_client:
            return f"[MOCK] {self.name} response to: {user_prompt}"

        system_prompt = self._build_system_prompt()

        # Add context to user prompt
        full_prompt = f"""Context:
{context}

User query:
{user_prompt}
"""

        try:
            response = await self.llm_client.query(
                system_prompt=system_prompt,
                user_prompt=full_prompt,
                temperature=temperature
            )
            return response
        except Exception as e:
            self.logger.error(f"LLM query failed: {e}")
            return f"Error: Unable to process request"

    def get_info(self) -> Dict[str, Any]:
        """Get expert information"""
        return {
            "name": self.name,
            "segment": self.segment,
            "specialization": self.specialization,
            "description": self.description,
            "tools": [tool.name for tool in self.tools],
            "organs": [organ.name for organ in self.organs],
            "metrics": {
                "requests_handled": self.requests_handled,
                "avg_response_time": self.avg_response_time,
                "success_rate": self.success_rate
            }
        }

    def _track_request(self, success: bool, response_time: float):
        """Track request metrics"""
        self.requests_handled += 1

        # Update average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (
                self.avg_response_time * 0.9 + response_time * 0.1
            )

        # Update success rate
        if success:
            self.success_rate = (
                self.success_rate * 0.95 + 1.0 * 0.05
            )
        else:
            self.success_rate = (
                self.success_rate * 0.95 + 0.0 * 0.05
            )
