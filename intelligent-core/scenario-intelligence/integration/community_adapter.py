"""
Community Intelligence Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с Community Intelligence для:
- Коллективных рекомендаций по сценариям
- Валидации сценариев через consensus
- Обучения на коллективном опыте
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioCommunityAdapter:
    """
    Адаптер для интеграции с Community Intelligence модулем

    Provides:
    - Collective scenario recommendations
    - Community-based validation
    - Shared knowledge learning
    """

    def __init__(self, community_url: str = "http://community-intelligence:8040"):
        """
        Initialize Community adapter

        Args:
            community_url: URL community intelligence service
        """
        self.community_url = community_url
        logger.info(f"Initialized ScenarioCommunityAdapter: {community_url}")

    async def get_community_recommendation(
        self,
        scenario_id: str,
        context: Dict[str, Any],
        agents: List[str] = None
    ) -> Dict[str, Any]:
        """
        Получить коллективную рекомендацию по выполнению сценария

        Args:
            scenario_id: ID сценария
            context: Контекст выполнения
            agents: Список агентов (или ["all"] для всех)

        Returns:
            Dict with:
                - consensus: str коллективное решение
                - confidence: float (0-1) уверенность
                - votes: Dict[str, int] голоса агентов
                - reasoning: str обоснование
        """
        try:
            import httpx

            if agents is None:
                agents = ["all"]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.community_url}/api/v1/ask",
                    json={
                        "question": f"Best execution strategy for scenario: {scenario_id}",
                        "context": context,
                        "agents": agents,
                        "require_consensus": True
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Got community recommendation for {scenario_id}: "
                        f"consensus={result.get('consensus', 'N/A')}, "
                        f"confidence={result.get('confidence', 0):.2f}"
                    )
                    return result
                else:
                    logger.error(
                        f"Community service error: {response.status_code}"
                    )
                    return {
                        "consensus": "proceed",
                        "confidence": 0.0,
                        "votes": {},
                        "reasoning": "Service unavailable, using default"
                    }

        except Exception as e:
            logger.error(f"Failed to get community recommendation: {e}")
            return {
                "consensus": "proceed",
                "confidence": 0.0,
                "votes": {},
                "reasoning": f"Error: {str(e)}"
            }

    async def validate_scenario(
        self,
        scenario_yaml: str,
        validators: List[str] = None
    ) -> Dict[str, Any]:
        """
        Валидировать сценарий через community consensus

        Args:
            scenario_yaml: YAML сценария
            validators: Список валидаторов (агентов)

        Returns:
            Dict with:
                - approved: bool принят ли сценарий
                - score: float (0-1) оценка
                - feedback: List[str] комментарии
                - improvements: List[str] рекомендации по улучшению
        """
        try:
            import httpx

            if validators is None:
                validators = ["all"]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.community_url}/api/v1/validate",
                    json={
                        "type": "scenario",
                        "content": scenario_yaml,
                        "validators": validators,
                        "threshold": 0.7  # 70% approval required
                    },
                    timeout=120.0  # Validation can take time
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Scenario validation: "
                        f"approved={result.get('approved', False)}, "
                        f"score={result.get('score', 0):.2f}"
                    )
                    return result
                else:
                    return {
                        "approved": False,
                        "score": 0.0,
                        "feedback": ["Validation service unavailable"],
                        "improvements": []
                    }

        except Exception as e:
            logger.error(f"Failed to validate scenario: {e}")
            return {
                "approved": False,
                "score": 0.0,
                "feedback": [f"Validation error: {str(e)}"],
                "improvements": []
            }

    async def get_common_flows(
        self,
        user_persona: str
    ) -> List[Dict[str, Any]]:
        """
        Получить типичные flow для user persona

        Args:
            user_persona: Роль пользователя (e.g., "Risk Manager")

        Returns:
            List of common flows:
                - scenarios: List[str] ID сценариев
                - frequency: int как часто используется
                - success_rate: float успешность
                - description: str описание flow
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.community_url}/api/v1/flows/{user_persona}",
                    timeout=30.0
                )

                if response.status_code == 200:
                    flows = response.json()
                    logger.info(
                        f"Got {len(flows)} common flows for {user_persona}"
                    )
                    return flows
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to get common flows: {e}")
            return []

    async def share_execution_result(
        self,
        scenario_id: str,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Поделиться результатом выполнения с community

        Args:
            scenario_id: ID сценария
            result: Результат выполнения
            context: Контекст (environment, load, etc.)

        Returns:
            Dict with:
                - shared: bool успешно ли расшарено
                - contribution_id: str ID вклада
                - impact: str влияние на community knowledge
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.community_url}/api/v1/share",
                    json={
                        "type": "scenario_execution",
                        "scenario_id": scenario_id,
                        "result": result,
                        "context": context
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Shared execution result for {scenario_id}: "
                        f"contribution_id={result.get('contribution_id', 'N/A')}"
                    )
                    return result
                else:
                    return {
                        "shared": False,
                        "contribution_id": None,
                        "impact": "none"
                    }

        except Exception as e:
            logger.error(f"Failed to share execution result: {e}")
            return {
                "shared": False,
                "contribution_id": None,
                "impact": "error"
            }

    async def get_best_practices(
        self,
        scenario_type: str,
        level: int = None
    ) -> List[Dict[str, Any]]:
        """
        Получить best practices от community для типа сценария

        Args:
            scenario_type: Тип сценария (functional, integration, e2e, etc.)
            level: Level сценария (1-4) или None для всех

        Returns:
            List of best practices:
                - practice: str название практики
                - description: str описание
                - examples: List[str] примеры
                - adoption_rate: float насколько широко используется
        """
        try:
            import httpx

            params = {"type": scenario_type}
            if level is not None:
                params["level"] = level

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.community_url}/api/v1/best-practices",
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    practices = response.json()
                    logger.info(
                        f"Got {len(practices)} best practices "
                        f"for {scenario_type}"
                    )
                    return practices
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to get best practices: {e}")
            return []


# Global instance
_adapter: Optional[ScenarioCommunityAdapter] = None


def get_community_adapter() -> ScenarioCommunityAdapter:
    """Get global Community adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioCommunityAdapter()
    return _adapter
