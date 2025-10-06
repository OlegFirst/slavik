"""
Base Tool Class

Unified base for all AI tools in the platform
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str
    type: str  # 'string', 'number', 'boolean', 'object', 'array'
    description: str
    required: bool = True
    default: Any = None


class BaseTool(ABC):
    """
    Base class for all AI Tools

    Tools provide structured interfaces for specific operations.
    They are used by Experts to accomplish tasks.

    Tools follow Anthropic's tool calling format.
    """

    def __init__(
        self,
        name: str,
        segment: str,  # 'governance', 'platform', or 'domain'
        description: str,
        parameters: List[ToolParameter]
    ):
        """
        Initialize Tool

        Args:
            name: Tool name (e.g., "bia_analysis_tool")
            segment: Segment this tool belongs to
            description: What this tool does
            parameters: List of parameters this tool accepts
        """
        self.name = name
        self.segment = segment
        self.description = description
        self.parameters = parameters
        self.logger = logger

        # Metrics
        self.executions = 0
        self.avg_execution_time = 0.0
        self.success_rate = 1.0

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with given parameters

        Args:
            parameters: Tool parameters

        Returns:
            Execution result
        """
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters against tool schema

        Args:
            parameters: Parameters to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        for param in self.parameters:
            if param.required and param.name not in parameters:
                raise ValueError(
                    f"Required parameter '{param.name}' missing for tool '{self.name}'"
                )

            if param.name in parameters:
                # Type checking
                value = parameters[param.name]
                expected_type = param.type

                if expected_type == 'string' and not isinstance(value, str):
                    raise ValueError(
                        f"Parameter '{param.name}' must be string, got {type(value).__name__}"
                    )
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Parameter '{param.name}' must be number, got {type(value).__name__}"
                    )
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    raise ValueError(
                        f"Parameter '{param.name}' must be boolean, got {type(value).__name__}"
                    )
                elif expected_type == 'object' and not isinstance(value, dict):
                    raise ValueError(
                        f"Parameter '{param.name}' must be object, got {type(value).__name__}"
                    )
                elif expected_type == 'array' and not isinstance(value, list):
                    raise ValueError(
                        f"Parameter '{param.name}' must be array, got {type(value).__name__}"
                    )

        return True

    def to_anthropic_format(self) -> Dict[str, Any]:
        """
        Convert tool to Anthropic tool calling format

        Returns:
            Tool definition in Anthropic format
        """
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }

            if param.default is not None:
                properties[param.name]["default"] = param.default

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    async def safe_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with validation and error handling

        Args:
            parameters: Tool parameters

        Returns:
            Execution result with success/error status
        """
        import time

        start_time = time.time()

        try:
            # Validate parameters
            self.validate_parameters(parameters)

            # Execute
            self.logger.info(f"Executing tool: {self.name}")
            result = await self.execute(parameters)

            # Track success
            execution_time = time.time() - start_time
            self._track_execution(success=True, execution_time=execution_time)

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }

        except Exception as e:
            # Track failure
            execution_time = time.time() - start_time
            self._track_execution(success=False, execution_time=execution_time)

            self.logger.error(f"Tool '{self.name}' execution failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }

    def _track_execution(self, success: bool, execution_time: float):
        """Track execution metrics"""
        self.executions += 1

        # Update average execution time
        if self.avg_execution_time == 0:
            self.avg_execution_time = execution_time
        else:
            self.avg_execution_time = (
                self.avg_execution_time * 0.9 + execution_time * 0.1
            )

        # Update success rate
        if success:
            self.success_rate = self.success_rate * 0.95 + 1.0 * 0.05
        else:
            self.success_rate = self.success_rate * 0.95 + 0.0 * 0.05

    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.name,
            "segment": self.segment,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in self.parameters
            ],
            "metrics": {
                "executions": self.executions,
                "avg_execution_time": self.avg_execution_time,
                "success_rate": self.success_rate
            }
        }
