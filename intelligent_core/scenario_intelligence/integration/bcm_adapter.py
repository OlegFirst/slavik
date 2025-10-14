"""
BCM Service Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с System BCM Service для:
- Загрузки framework-specific сценариев (ISO 22301, NIST, WHO)
- Валидации BCM compliance
- Domain expertise для BCM сценариев
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioBCMAdapter:
    """
    Адаптер для интеграции с System BCM Service модулем

    Provides:
    - Framework-specific scenario loading
    - BCM compliance validation
    - Domain expertise integration
    """

    def __init__(self, bcm_url: str = "http://bcm-service:8050"):
        """
        Initialize BCM adapter

        Args:
            bcm_url: URL system BCM service
        """
        self.bcm_url = bcm_url
        logger.info(f"Initialized ScenarioBCMAdapter: {bcm_url}")

    async def load_framework_scenarios(
        self,
        framework: str
    ) -> List[Dict[str, Any]]:
        """
        Загрузить сценарии для фреймворка

        Args:
            framework: Название фреймворка (ISO_22301, NIST, WHO_Healthcare, etc.)

        Returns:
            List of scenarios ready to register
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.bcm_url}/api/v1/frameworks/{framework}/scenarios",
                    timeout=60.0
                )

                if response.status_code == 200:
                    scenarios = response.json()
                    logger.info(
                        f"Loaded {len(scenarios)} scenarios "
                        f"for framework {framework}"
                    )
                    return scenarios
                else:
                    logger.error(
                        f"BCM Service error: {response.status_code}"
                    )
                    return []

        except Exception as e:
            logger.error(f"Failed to load framework scenarios: {e}")
            return []

    async def validate_bcm_compliance(
        self,
        scenario_id: str,
        iso_clause: str = None
    ) -> Dict[str, Any]:
        """
        Валидировать BCM compliance сценария

        Args:
            scenario_id: ID сценария
            iso_clause: ISO 22301 clause (опционально, например "8.2.2")

        Returns:
            Dict with:
                - compliant: bool соответствует ли
                - score: float (0-1) оценка соответствия
                - clause_coverage: Dict[str, bool] покрытие по пунктам
                - gaps: List[str] найденные пробелы
                - recommendations: List[str] рекомендации
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                params = {"scenario_id": scenario_id}
                if iso_clause:
                    params["iso_clause"] = iso_clause

                response = await client.post(
                    f"{self.bcm_url}/api/v1/validate",
                    json=params,
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"BCM compliance for {scenario_id}: "
                        f"compliant={result.get('compliant', False)}, "
                        f"score={result.get('score', 0):.2f}"
                    )
                    return result
                else:
                    return {
                        "compliant": False,
                        "score": 0.0,
                        "clause_coverage": {},
                        "gaps": ["Validation service unavailable"],
                        "recommendations": []
                    }

        except Exception as e:
            logger.error(f"Failed to validate BCM compliance: {e}")
            return {
                "compliant": False,
                "score": 0.0,
                "clause_coverage": {},
                "gaps": [f"Validation error: {str(e)}"],
                "recommendations": []
            }

    async def get_framework_info(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """
        Получить информацию о фреймворке для domain expertise

        Args:
            framework: Название фреймворка

        Returns:
            Dict with:
                - framework_name: str
                - version: str версия фреймворка
                - clauses: List[Dict] список пунктов
                - best_practices: List[str] best practices
                - requirements: Dict требования
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.bcm_url}/api/v1/frameworks/{framework}/info",
                    timeout=30.0
                )

                if response.status_code == 200:
                    info = response.json()
                    logger.info(
                        f"Got framework info for {framework}: "
                        f"version={info.get('version', 'N/A')}"
                    )
                    return info
                else:
                    return {
                        "framework_name": framework,
                        "version": "unknown",
                        "clauses": [],
                        "best_practices": [],
                        "requirements": {}
                    }

        except Exception as e:
            logger.error(f"Failed to get framework info: {e}")
            return {
                "framework_name": framework,
                "version": "unknown",
                "clauses": [],
                "best_practices": [],
                "requirements": {}
            }

    async def generate_compliance_evidence(
        self,
        scenario_id: str,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерировать compliance evidence на основе выполнения сценария

        Args:
            scenario_id: ID сценария
            execution_result: Результат выполнения

        Returns:
            Dict with:
                - evidence_id: str ID evidence
                - evidence_type: str тип evidence
                - iso_clauses: List[str] покрытые пункты ISO
                - artifact_url: str URL артефакта
                - timestamp: str когда создано
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bcm_url}/api/v1/evidence/generate",
                    json={
                        "scenario_id": scenario_id,
                        "execution_result": execution_result,
                        "evidence_type": "scenario_execution"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    evidence = response.json()
                    logger.info(
                        f"Generated compliance evidence for {scenario_id}: "
                        f"evidence_id={evidence.get('evidence_id', 'N/A')}"
                    )
                    return evidence
                else:
                    return {
                        "evidence_id": None,
                        "evidence_type": "scenario_execution",
                        "iso_clauses": [],
                        "artifact_url": None,
                        "timestamp": None
                    }

        except Exception as e:
            logger.error(f"Failed to generate compliance evidence: {e}")
            return {
                "evidence_id": None,
                "evidence_type": "scenario_execution",
                "iso_clauses": [],
                "artifact_url": None,
                "timestamp": None
            }

    async def get_healthcare_scenarios(self) -> List[Dict[str, Any]]:
        """
        Получить Healthcare-specific BCM сценарии (WHO guidelines)

        Returns:
            List of Healthcare BCM scenarios
        """
        return await self.load_framework_scenarios("WHO_Healthcare")

    async def get_nist_scenarios(self) -> List[Dict[str, Any]]:
        """
        Получить NIST framework сценарии

        Returns:
            List of NIST framework scenarios
        """
        return await self.load_framework_scenarios("NIST")


# Global instance
_adapter: Optional[ScenarioBCMAdapter] = None


def get_bcm_adapter() -> ScenarioBCMAdapter:
    """Get global BCM adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioBCMAdapter()
    return _adapter
