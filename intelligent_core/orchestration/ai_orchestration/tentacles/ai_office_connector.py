"""
AI Office Connector

Connects Super-Orchestrator to AI Office (7 AI Colleagues)

Architecture:
- Super-Orchestrator (this) orchestrates AI Office
- AI Office provides 7 specialized AI Colleagues:
  1. Compliance Copilot
  2. Project Manager AI
  3. Risk Analyst AI
  4. BIA Specialist AI
  5. Plan Generator AI
  6. Incident Advisor AI
  7. Exercise Designer AI

Each colleague provides:
- PDCA framework (Plan-Do-Check-Act)
- RAG capabilities (Retrieval-Augmented Generation)
- Conversation tracking
- Context-aware responses
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AIColleague(str, Enum):
    """Available AI Colleagues in AI Office"""
    COMPLIANCE_COPILOT = "compliance_copilot"
    PROJECT_MANAGER = "project_manager"
    RISK_ANALYST = "risk_analyst"
    BIA_SPECIALIST = "bia_specialist"
    PLAN_GENERATOR = "plan_generator"
    INCIDENT_ADVISOR = "incident_advisor"
    EXERCISE_DESIGNER = "exercise_designer"


class PDCAPhase(str, Enum):
    """PDCA phases"""
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


class AssistantContext(str, Enum):
    """BCM contexts"""
    OVERVIEW = "overview"
    RISK = "risk"
    BIA = "bia"
    PLANNING = "planning"
    COMPLIANCE = "compliance"
    RESPONSE = "response"
    EXERCISES = "exercises"
    GOVERNANCE = "governance"


class AIOfficeConnector:
    """
    Connector to AI Office service.

    Enables Super-Orchestrator to delegate tasks to specialized AI Colleagues.
    """

    def __init__(self, ai_office_url: str = "http://localhost:8032"):
        """
        Initialize AI Office connector.

        Args:
            ai_office_url: Base URL of AI Office service
        """
        self.base_url = ai_office_url
        self.client = httpx.AsyncClient(timeout=60.0)
        logger.info(f"AI Office Connector initialized: {ai_office_url}")

    async def consult_colleague(
        self,
        colleague: AIColleague,
        message: str,
        context: AssistantContext = AssistantContext.OVERVIEW,
        tenant_id: str = "demo",
        phase: Optional[PDCAPhase] = None
    ) -> Dict[str, Any]:
        """
        Consult an AI Colleague.

        Args:
            colleague: Which colleague to consult
            message: User message/query
            context: BCM context
            tenant_id: Tenant identifier
            phase: Optional PDCA phase

        Returns:
            Colleague response with answer and suggested actions
        """
        try:
            endpoint = f"{self.base_url}/api/colleagues/{colleague.value}/message"

            payload = {
                "message": message,
                "context": context.value,
                "tenant_id": tenant_id
            }

            if phase:
                payload["phase"] = phase.value

            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()

            result = response.json()

            logger.info(
                f"Consulted {colleague.value}: "
                f"confidence={result.get('confidence', 0):.2f}, "
                f"actions={len(result.get('actions', []))}"
            )

            return result

        except httpx.HTTPError as e:
            logger.error(f"Failed to consult {colleague.value}: {e}")
            return {
                "error": str(e),
                "colleague": colleague.value,
                "content": "Failed to reach AI colleague"
            }

    async def get_colleague_stats(self, colleague: AIColleague) -> Dict[str, Any]:
        """
        Get statistics for an AI Colleague.

        Args:
            colleague: Which colleague

        Returns:
            Statistics dict
        """
        try:
            endpoint = f"{self.base_url}/api/colleagues/{colleague.value}/stats"
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get stats for {colleague.value}: {e}")
            return {"error": str(e)}

    async def list_colleagues(self) -> List[Dict[str, Any]]:
        """
        List all available AI Colleagues.

        Returns:
            List of colleague info
        """
        try:
            endpoint = f"{self.base_url}/api/colleagues"
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to list colleagues: {e}")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if AI Office is healthy.

        Returns:
            Health status
        """
        try:
            endpoint = f"{self.base_url}/health"
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"AI Office health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # Convenience methods for specific colleagues

    async def consult_compliance(
        self,
        message: str,
        context: AssistantContext = AssistantContext.COMPLIANCE,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """Consult Compliance Copilot"""
        return await self.consult_colleague(
            AIColleague.COMPLIANCE_COPILOT,
            message,
            context,
            tenant_id
        )

    async def consult_project_manager(
        self,
        message: str,
        context: AssistantContext = AssistantContext.PLANNING,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """Consult Project Manager AI"""
        return await self.consult_colleague(
            AIColleague.PROJECT_MANAGER,
            message,
            context,
            tenant_id
        )

    async def consult_risk_analyst(
        self,
        message: str,
        context: AssistantContext = AssistantContext.RISK,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """Consult Risk Analyst AI"""
        return await self.consult_colleague(
            AIColleague.RISK_ANALYST,
            message,
            context,
            tenant_id
        )

    async def consult_bia_specialist(
        self,
        message: str,
        context: AssistantContext = AssistantContext.BIA,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """Consult BIA Specialist AI"""
        return await self.consult_colleague(
            AIColleague.BIA_SPECIALIST,
            message,
            context,
            tenant_id
        )

    async def consult_incident_advisor(
        self,
        message: str,
        context: AssistantContext = AssistantContext.RESPONSE,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """Consult Incident Advisor AI"""
        return await self.consult_colleague(
            AIColleague.INCIDENT_ADVISOR,
            message,
            context,
            tenant_id
        )

    async def consult_exercise_designer(
        self,
        message: str,
        context: AssistantContext = AssistantContext.EXERCISES,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """Consult Exercise Designer AI"""
        return await self.consult_colleague(
            AIColleague.EXERCISE_DESIGNER,
            message,
            context,
            tenant_id
        )


# Singleton instance
_ai_office_connector: Optional[AIOfficeConnector] = None


def get_ai_office_connector(url: str = "http://localhost:8032") -> AIOfficeConnector:
    """
    Get singleton AI Office connector instance.

    Args:
        url: AI Office base URL

    Returns:
        AIOfficeConnector instance
    """
    global _ai_office_connector

    if _ai_office_connector is None:
        _ai_office_connector = AIOfficeConnector(url)

    return _ai_office_connector
