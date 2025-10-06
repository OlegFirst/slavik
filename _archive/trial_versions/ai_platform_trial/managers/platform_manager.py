"""
Platform Manager

TOP Manager for Platform segment (Workflow, Architecture, Technical)
"""

from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.base import BaseManager
import logging

logger = logging.getLogger(__name__)


class PlatformManager(BaseManager):
    """
    Platform Manager

    Oversees platform segment experts:
    - Workflow Expert
    - MIO Expert (Multi-Instance Orchestration)
    - Deployment Expert
    - Performance Expert
    - Learning Expert

    Responsibilities:
    - Workflow automation and optimization
    - Service orchestration
    - Deployment and DevOps
    - Performance monitoring and tuning
    - Machine learning and continuous improvement
    """

    def __init__(self, experts=None, llm_client=None):
        super().__init__(
            name="Platform Manager",
            segment="platform",
            description="""Manages platform architecture and technical operations.

Oversees:
- Workflow automation and optimization
- Multi-instance orchestration (MIO)
- Deployment and DevOps pipelines
- Performance monitoring and optimization
- Machine learning and self-improvement
- Service reliability and scalability

Coordinates 5 experts:
1. Workflow Expert - Workflow automation and BPMN
2. MIO Expert - Multi-instance orchestration
3. Deployment Expert - CI/CD and deployment
4. Performance Expert - Performance optimization
5. Learning Expert - ML and continuous improvement
""",
            experts=experts,
            llm_client=llm_client
        )

    async def handle(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle platform request

        Args:
            user_query: User's question
            context: Context information

        Returns:
            Response from appropriate platform expert
        """
        try:
            # Select best expert for this request
            expert = await self.select_expert(user_query, context)

            if not expert:
                return {
                    "success": False,
                    "error": "No platform expert available to handle this request",
                    "manager": self.name,
                    "segment": self.segment,
                    "suggestion": "Try rephrasing your question with more specific platform/technical keywords"
                }

            # Delegate to expert
            result = await self.delegate(expert, user_query, context)

            # Add platform-specific metadata
            result["manager"] = self.name
            result["segment"] = self.segment

            return result

        except Exception as e:
            logger.error(f"Platform Manager failed: {e}")
            return {
                "success": False,
                "error": f"Platform request failed: {str(e)}",
                "manager": self.name,
                "segment": self.segment
            }
