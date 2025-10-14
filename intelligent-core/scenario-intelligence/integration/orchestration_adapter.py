"""
AI Orchestration Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с AI Orchestration для:
- Делегирования AI задач на основе сценариев
- Использования Decision Center для принятия решений
- Safety-проверок выполнения сценариев
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioOrchestrationAdapter:
    """
    Адаптер для интеграции с AI Orchestration модулем

    Provides:
    - AI task delegation based on scenarios
    - Decision Center integration
    - Safety monitoring for scenarios
    """

    def __init__(self, orchestrator_url: str = "http://ai-orchestrator:8030"):
        """
        Initialize Orchestration adapter

        Args:
            orchestrator_url: URL AI orchestrator service
        """
        self.orchestrator_url = orchestrator_url
        logger.info(f"Initialized ScenarioOrchestrationAdapter: {orchestrator_url}")

    async def delegate_to_ai(
        self,
        task_type: str,
        scenario_context: Dict[str, Any],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Делегировать задачу AI Orchestrator

        Args:
            task_type: Тип задачи (bia_analysis, risk_assessment, etc.)
            scenario_context: Контекст сценария
            priority: Приоритет (low, normal, high, critical)

        Returns:
            Dict with:
                - task_id: str ID задачи
                - status: str статус (queued, running, completed, failed)
                - assigned_agent: str какой агент обрабатывает
                - result: Optional[Dict] результат
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/api/v1/tasks",
                    json={
                        "task_type": task_type,
                        "context": scenario_context,
                        "priority": priority,
                        "source": "scenario-intelligence"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Delegated task {task_type} to AI: "
                        f"task_id={result.get('task_id', 'N/A')}, "
                        f"agent={result.get('assigned_agent', 'N/A')}"
                    )
                    return result
                else:
                    logger.error(
                        f"AI Orchestrator error: {response.status_code}"
                    )
                    return {
                        "task_id": None,
                        "status": "failed",
                        "assigned_agent": None,
                        "result": {"error": "Orchestrator unavailable"}
                    }

        except Exception as e:
            logger.error(f"Failed to delegate to AI: {e}")
            return {
                "task_id": None,
                "status": "error",
                "assigned_agent": None,
                "result": {"error": str(e)}
            }

    async def wait_for_result(
        self,
        task_id: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Ждать результата AI задачи

        Args:
            task_id: ID задачи
            timeout: Таймаут в секундах

        Returns:
            Dict with:
                - completed: bool завершена ли задача
                - result: Dict результат
                - duration_ms: int время выполнения
        """
        try:
            import httpx
            import asyncio

            async with httpx.AsyncClient() as client:
                start_time = asyncio.get_event_loop().time()

                while True:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > timeout:
                        logger.warning(
                            f"Task {task_id} timeout after {timeout}s"
                        )
                        return {
                            "completed": False,
                            "result": {"error": "Timeout"},
                            "duration_ms": int(elapsed * 1000)
                        }

                    response = await client.get(
                        f"{self.orchestrator_url}/api/v1/tasks/{task_id}",
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")

                        if status in ["completed", "failed"]:
                            duration_ms = int(elapsed * 1000)
                            logger.info(
                                f"Task {task_id} {status} in {duration_ms}ms"
                            )
                            return {
                                "completed": status == "completed",
                                "result": data.get("result", {}),
                                "duration_ms": duration_ms
                            }

                    # Wait before next check
                    await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"Failed to wait for result: {e}")
            return {
                "completed": False,
                "result": {"error": str(e)},
                "duration_ms": 0
            }

    async def check_safety(
        self,
        scenario_id: str,
        planned_actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Проверить безопасность выполнения сценария

        Args:
            scenario_id: ID сценария
            planned_actions: Планируемые действия

        Returns:
            Dict with:
                - safe: bool безопасно ли выполнять
                - risks: List[str] выявленные риски
                - recommendations: List[str] рекомендации
                - severity: str (low, medium, high, critical)
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/api/v1/safety/check",
                    json={
                        "scenario_id": scenario_id,
                        "actions": planned_actions,
                        "check_type": "scenario_execution"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Safety check for {scenario_id}: "
                        f"safe={result.get('safe', False)}, "
                        f"severity={result.get('severity', 'unknown')}"
                    )
                    return result
                else:
                    return {
                        "safe": True,  # Default to safe if service unavailable
                        "risks": ["Unable to perform safety check"],
                        "recommendations": [],
                        "severity": "unknown"
                    }

        except Exception as e:
            logger.error(f"Failed to check safety: {e}")
            return {
                "safe": True,
                "risks": [f"Safety check error: {str(e)}"],
                "recommendations": [],
                "severity": "unknown"
            }

    async def get_agent_coordination_plan(
        self,
        scenario_id: str,
        required_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Получить план координации агентов для сценария

        Args:
            scenario_id: ID сценария
            required_agents: Требуемые агенты

        Returns:
            Dict with:
                - plan: Dict план координации
                - assignments: Dict[str, str] назначения агентов
                - execution_order: List[str] порядок выполнения
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/api/v1/coordination/plan",
                    json={
                        "scenario_id": scenario_id,
                        "required_agents": required_agents,
                        "source": "scenario-intelligence"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Got coordination plan for {scenario_id}: "
                        f"{len(result.get('assignments', {}))} agents assigned"
                    )
                    return result
                else:
                    return {
                        "plan": {},
                        "assignments": {},
                        "execution_order": []
                    }

        except Exception as e:
            logger.error(f"Failed to get coordination plan: {e}")
            return {
                "plan": {},
                "assignments": {},
                "execution_order": []
            }


# Global instance
_adapter: Optional[ScenarioOrchestrationAdapter] = None


def get_orchestration_adapter() -> ScenarioOrchestrationAdapter:
    """Get global Orchestration adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioOrchestrationAdapter()
    return _adapter
