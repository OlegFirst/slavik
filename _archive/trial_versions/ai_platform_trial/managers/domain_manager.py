"""
Domain Manager (BCM Manager)

TOP Manager for Domain segment (Business Continuity Management)
"""

from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.base import BaseManager
import logging

logger = logging.getLogger(__name__)


class DomainManager(BaseManager):
    """
    Domain Manager (BCM Manager)

    Oversees domain/BCM segment experts:
    - BIA Specialist
    - Risk Analyst
    - Planning Specialist
    - Incident Expert
    - Exercise Designer
    - Supply Chain Expert
    - Collective Expert
    - Documentation Expert
    - Knowledge Manager
    - Predictive Analyst

    Responsibilities:
    - Business impact analysis
    - Risk assessment and management
    - Continuity planning
    - Incident response
    - Testing and exercises
    - Supply chain continuity
    - Collective intelligence
    - Documentation management
    - Knowledge graphs
    - Predictive analytics
    """

    def __init__(self, experts=None, llm_client=None):
        super().__init__(
            name="Domain Manager (BCM)",
            segment="domain",
            description="""Manages all Business Continuity Management (BCM) operations.

Oversees:
- Business Impact Analysis (BIA)
- Risk assessment and mitigation
- Business continuity planning
- Incident and crisis management
- Testing and exercises
- Supply chain continuity
- Collective intelligence and peer learning
- Documentation and knowledge management
- Predictive analytics

Coordinates 10 experts:
1. BIA Specialist - Business impact analysis
2. Risk Analyst - Risk assessment and management
3. Planning Specialist - Continuity planning
4. Incident Expert - Incident/crisis response
5. Exercise Designer - Testing and exercises
6. Supply Chain Expert - Supply chain continuity
7. Collective Expert - Peer learning and collective intelligence
8. Documentation Expert - Living documentation
9. Knowledge Manager - Knowledge graphs
10. Predictive Analyst - Predictive analytics and ML
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
        Handle BCM/domain request

        Args:
            user_query: User's question
            context: Context information

        Returns:
            Response from appropriate BCM expert
        """
        try:
            # Select best expert for this request
            expert = await self.select_expert(user_query, context)

            if not expert:
                return {
                    "success": False,
                    "error": "No BCM expert available to handle this request",
                    "manager": self.name,
                    "segment": self.segment,
                    "suggestion": "Try rephrasing your question with more specific BCM keywords (BIA, risk, recovery, etc.)"
                }

            # Delegate to expert
            result = await self.delegate(expert, user_query, context)

            # Add domain-specific metadata
            result["manager"] = self.name
            result["segment"] = self.segment

            return result

        except Exception as e:
            logger.error(f"Domain Manager failed: {e}")
            return {
                "success": False,
                "error": f"Domain request failed: {str(e)}",
                "manager": self.name,
                "segment": self.segment
            }
