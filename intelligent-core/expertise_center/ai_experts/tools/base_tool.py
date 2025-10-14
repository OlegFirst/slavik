"""
Base Tool Class

Foundation for all AI expert tools. Provides:
- Anthropic tool format conversion
- Execution interface
- Event publishing
- Error handling
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Base class for AI expert tools

    All tools must:
    1. Define name, description, and parameters
    2. Implement execute() method
    3. Return structured results

    Example:
        >>> class MyTool(BaseTool):
        ...     def __init__(self):
        ...         super().__init__(
        ...             name="my_tool",
        ...             description="Does something useful",
        ...             parameters={
        ...                 "input": {"type": "string", "description": "Input data"}
        ...             }
        ...         )
        ...
        ...     async def execute(self, input: str) -> Dict[str, Any]:
        ...         return {"result": f"Processed: {input}"}
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required_params: Optional[list] = None
    ):
        """
        Initialize tool

        Args:
            name: Tool name (snake_case)
            description: Clear description for LLM
            parameters: Parameter schema (JSON Schema format)
            required_params: List of required parameter names
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.required_params = required_params or list(parameters.keys())

        # Optional: EventBus integration
        self.eventbus = None
        try:
            from infrastructure.eventbus import create_eventbus
            self.eventbus = create_eventbus('redis')
        except ImportError:
            logger.warning(f"EventBus not available for tool {name}")

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute tool logic

        Args:
            **kwargs: Tool parameters

        Returns:
            Structured result dictionary

        Raises:
            ValueError: Invalid parameters
            Exception: Execution error
        """
        pass

    def to_anthropic_tool(self) -> dict:
        """
        Convert to Anthropic Claude tool format

        Returns:
            Tool definition for Claude API
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required_params
            }
        }

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """
        Publish tool execution event

        Args:
            event_type: Event type (e.g., 'ai.tool.executed')
            data: Event data
        """
        if not self.eventbus:
            return

        try:
            from infrastructure.eventbus import Event
            event = Event.create(
                event_type=event_type,
                data=data,
                source='ai-experts'
            )
            await self.eventbus.publish(event)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    async def safe_execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute with error handling and event publishing

        Args:
            **kwargs: Tool parameters

        Returns:
            Result with success/error status
        """
        try:
            # Validate required params
            missing = [p for p in self.required_params if p not in kwargs]
            if missing:
                raise ValueError(f"Missing required parameters: {missing}")

            # Execute
            result = await self.execute(**kwargs)

            # Publish success event
            await self._publish_event('ai.tool.executed', {
                'tool': self.name,
                'status': 'success',
                'result': result
            })

            return {
                'success': True,
                'data': result
            }

        except Exception as e:
            logger.error(f"Tool {self.name} execution failed: {e}")

            # Publish error event
            await self._publish_event('ai.tool.failed', {
                'tool': self.name,
                'error': str(e)
            })

            return {
                'success': False,
                'error': str(e)
            }

    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate parameters against schema

        Args:
            **kwargs: Parameters to validate

        Returns:
            True if valid

        Raises:
            ValueError: Invalid parameters
        """
        # Check required params
        missing = [p for p in self.required_params if p not in kwargs]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        # Check types (basic validation)
        for param_name, param_value in kwargs.items():
            if param_name not in self.parameters:
                raise ValueError(f"Unknown parameter: {param_name}")

            expected_type = self.parameters[param_name].get('type')
            if expected_type == 'string' and not isinstance(param_value, str):
                raise ValueError(f"Parameter {param_name} must be string")
            elif expected_type == 'integer' and not isinstance(param_value, int):
                raise ValueError(f"Parameter {param_name} must be integer")
            elif expected_type == 'number' and not isinstance(param_value, (int, float)):
                raise ValueError(f"Parameter {param_name} must be number")
            elif expected_type == 'boolean' and not isinstance(param_value, bool):
                raise ValueError(f"Parameter {param_name} must be boolean")

        return True
