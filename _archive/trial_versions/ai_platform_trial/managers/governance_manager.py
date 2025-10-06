"""
Governance Manager

TOP Manager for Governance segment (Compliance, Audit, Governance)
"""

from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.base import BaseManager
import logging

logger = logging.getLogger(__name__)


class GovernanceManager(BaseManager):
    """
    Governance Manager

    Oversees governance segment experts:
    - Compliance Auditor
    - Governance Expert
    - Audit Manager

    Responsibilities:
    - ISO 22301, ISO 27001 compliance
    - Audit preparation and management
    - Policy and governance framework
    - Regulatory requirements
    """

    def __init__(self, experts=None, llm_client=None):
        super().__init__(
            name="Governance Manager",
            segment="governance",
            description="""Manages compliance, audit, and governance operations.

Oversees:
- ISO 22301, ISO 27001 compliance
- Internal and external audits
- Governance frameworks and policies
- Regulatory compliance (GDPR, SOX, etc.)
- Control frameworks

Coordinates 3 experts:
1. Compliance Auditor - ISO/regulatory compliance
2. Governance Expert - Policies and frameworks
3. Audit Manager - Audit preparation and execution
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
        Handle governance request

        Args:
            user_query: User's question
            context: Context information

        Returns:
            Response from appropriate governance expert
        """
        try:
            # Select best expert for this request
            expert = await self.select_expert(user_query, context)

            if not expert:
                return {
                    "success": False,
                    "error": "No governance expert available to handle this request",
                    "manager": self.name,
                    "segment": self.segment,
                    "suggestion": "Try rephrasing your question with more specific governance/compliance keywords"
                }

            # Delegate to expert
            result = await self.delegate(expert, user_query, context)

            # Add governance-specific metadata
            result["manager"] = self.name
            result["segment"] = self.segment

            return result

        except Exception as e:
            logger.error(f"Governance Manager failed: {e}")
            return {
                "success": False,
                "error": f"Governance request failed: {str(e)}",
                "manager": self.name,
                "segment": self.segment
            }
