"""
Workflow Intelligence Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с Workflow Intelligence для:
- Регистрации сценариев как бизнес-процессов
- Process mining сценариев
- Оптимизации на основе workflow analytics
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioWorkflowIntelAdapter:
    """
    Адаптер для интеграции с Workflow Intelligence модулем

    Provides:
    - Scenario as business process registration
    - Process mining integration
    - Workflow optimization
    """

    def __init__(self, workflow_intel_url: str = "http://workflow-intelligence:8037"):
        """
        Initialize Workflow Intelligence adapter

        Args:
            workflow_intel_url: URL workflow intelligence service
        """
        self.workflow_intel_url = workflow_intel_url
        logger.info(f"Initialized ScenarioWorkflowIntelAdapter: {workflow_intel_url}")

    async def register_as_workflow(
        self,
        scenario_id: str,
        workflow_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Зарегистрировать сценарий как бизнес-процесс

        Args:
            scenario_id: ID сценария
            workflow_definition: Определение workflow из сценария

        Returns:
            Dict with:
                - workflow_id: str ID зарегистрированного workflow
                - registered: bool успешно ли зарегистрирован
                - process_type: str тип процесса
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.workflow_intel_url}/api/v1/workflows/register",
                    json={
                        "scenario_id": scenario_id,
                        "workflow_definition": workflow_definition,
                        "source": "scenario-intelligence"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Registered scenario {scenario_id} as workflow: "
                        f"workflow_id={result.get('workflow_id', 'N/A')}"
                    )
                    return result
                else:
                    logger.error(
                        f"Workflow Intelligence service error: {response.status_code}"
                    )
                    return {
                        "workflow_id": None,
                        "registered": False,
                        "process_type": None
                    }

        except Exception as e:
            logger.error(f"Failed to register as workflow: {e}")
            return {
                "workflow_id": None,
                "registered": False,
                "process_type": None
            }

    async def analyze_execution_flow(
        self,
        scenario_id: str,
        time_window: str = "7d"
    ) -> Dict[str, Any]:
        """
        Анализировать execution flow сценария (process mining)

        Args:
            scenario_id: ID сценария
            time_window: Временное окно

        Returns:
            Dict with:
                - bottlenecks: List[Dict] узкие места
                - average_duration_ms: int среднее время
                - happy_path: List[str] наиболее частый путь
                - variations: int количество вариаций выполнения
                - optimization_opportunities: List[Dict] возможности оптимизации
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.workflow_intel_url}/api/v1/analyze/flow",
                    json={
                        "scenario_id": scenario_id,
                        "time_window": time_window,
                        "include_bottlenecks": True,
                        "include_variations": True
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Analyzed flow for {scenario_id}: "
                        f"{len(result.get('bottlenecks', []))} bottlenecks found, "
                        f"avg_duration={result.get('average_duration_ms', 0)}ms"
                    )
                    return result
                else:
                    return {
                        "bottlenecks": [],
                        "average_duration_ms": 0,
                        "happy_path": [],
                        "variations": 0,
                        "optimization_opportunities": []
                    }

        except Exception as e:
            logger.error(f"Failed to analyze execution flow: {e}")
            return {
                "bottlenecks": [],
                "average_duration_ms": 0,
                "happy_path": [],
                "variations": 0,
                "optimization_opportunities": []
            }

    async def optimize_scenario(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Получить рекомендации по оптимизации сценария на основе process mining

        Args:
            scenario_id: ID сценария

        Returns:
            Dict with:
                - optimizations: List[Dict] рекомендации
                - expected_improvement: Dict ожидаемые улучшения
                - priority: str приоритет оптимизации
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.workflow_intel_url}/api/v1/optimize",
                    json={
                        "scenario_id": scenario_id,
                        "optimization_types": [
                            "reduce_duration",
                            "remove_redundant_steps",
                            "parallelize_steps",
                            "improve_error_handling"
                        ]
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Got {len(result.get('optimizations', []))} "
                        f"optimization recommendations for {scenario_id}"
                    )
                    return result
                else:
                    return {
                        "optimizations": [],
                        "expected_improvement": {},
                        "priority": "low"
                    }

        except Exception as e:
            logger.error(f"Failed to optimize scenario: {e}")
            return {
                "optimizations": [],
                "expected_improvement": {},
                "priority": "low"
            }

    async def get_process_metrics(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Получить метрики процесса для сценария

        Args:
            scenario_id: ID сценария

        Returns:
            Dict with:
                - total_executions: int всего выполнений
                - success_rate: float (0-1) успешность
                - avg_duration_ms: int среднее время
                - p50_duration_ms: int медиана
                - p95_duration_ms: int 95 перцентиль
                - p99_duration_ms: int 99 перцентиль
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.workflow_intel_url}/api/v1/metrics/{scenario_id}",
                    timeout=30.0
                )

                if response.status_code == 200:
                    metrics = response.json()
                    logger.info(
                        f"Got process metrics for {scenario_id}: "
                        f"executions={metrics.get('total_executions', 0)}, "
                        f"success_rate={metrics.get('success_rate', 0):.2f}"
                    )
                    return metrics
                else:
                    return {
                        "total_executions": 0,
                        "success_rate": 0.0,
                        "avg_duration_ms": 0,
                        "p50_duration_ms": 0,
                        "p95_duration_ms": 0,
                        "p99_duration_ms": 0
                    }

        except Exception as e:
            logger.error(f"Failed to get process metrics: {e}")
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0,
                "p50_duration_ms": 0,
                "p95_duration_ms": 0,
                "p99_duration_ms": 0
            }

    async def apply_pdca_cycle(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Применить PDCA цикл к сценарию

        Args:
            scenario_id: ID сценария

        Returns:
            Dict with:
                - plan: Dict что запланировано
                - do: Dict что сделано
                - check: Dict результаты проверки
                - act: Dict действия по улучшению
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.workflow_intel_url}/api/v1/pdca",
                    json={
                        "scenario_id": scenario_id,
                        "cycle_type": "scenario_improvement"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Applied PDCA cycle to {scenario_id}"
                    )
                    return result
                else:
                    return {
                        "plan": {},
                        "do": {},
                        "check": {},
                        "act": {}
                    }

        except Exception as e:
            logger.error(f"Failed to apply PDCA cycle: {e}")
            return {
                "plan": {},
                "do": {},
                "check": {},
                "act": {}
            }


# Global instance
_adapter: Optional[ScenarioWorkflowIntelAdapter] = None


def get_workflow_intel_adapter() -> ScenarioWorkflowIntelAdapter:
    """Get global Workflow Intelligence adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioWorkflowIntelAdapter()
    return _adapter
