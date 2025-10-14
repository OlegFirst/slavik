"""
Workflow Engine Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с Workflow Engine (Temporal) для:
- Запуска сценариев как durable workflows
- Интеграции с Temporal activities
- Long-running scenario executions
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioWorkflowAdapter:
    """
    Адаптер для интеграции с Workflow Engine (Temporal)

    Provides:
    - Scenario as Temporal workflow execution
    - Durable scenario execution
    - Long-running process support
    """

    def __init__(self, workflow_url: str = "http://workflow-engine:8020"):
        """
        Initialize Workflow adapter

        Args:
            workflow_url: URL workflow engine service
        """
        self.workflow_url = workflow_url
        logger.info(f"Initialized ScenarioWorkflowAdapter: {workflow_url}")

    async def execute_scenario_as_workflow(
        self,
        scenario_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Запустить сценарий как Temporal workflow

        Args:
            scenario_id: ID сценария
            context: Контекст выполнения

        Returns:
            Dict with:
                - workflow_id: str ID workflow
                - status: str статус (running, completed, failed)
                - result: Optional[Dict] результат (если completed)
        """
        try:
            import httpx

            # Start workflow
            async with httpx.AsyncClient() as client:
                start_response = await client.post(
                    f"{self.workflow_url}/api/v1/workflows/start",
                    json={
                        "workflow_type": "scenario_execution",
                        "input": {
                            "scenario_id": scenario_id,
                            "context": context
                        }
                    },
                    timeout=30.0
                )

                if start_response.status_code == 200:
                    workflow_data = start_response.json()
                    workflow_id = workflow_data.get("workflow_id")

                    logger.info(
                        f"Started workflow for scenario {scenario_id}: "
                        f"workflow_id={workflow_id}"
                    )

                    # Wait for completion (with timeout)
                    status_response = await client.get(
                        f"{self.workflow_url}/api/v1/workflows/{workflow_id}/status",
                        timeout=300.0  # 5 min max
                    )

                    if status_response.status_code == 200:
                        result = status_response.json()
                        logger.info(
                            f"Workflow {workflow_id} status: "
                            f"{result.get('status', 'unknown')}"
                        )
                        return result
                    else:
                        return {
                            "workflow_id": workflow_id,
                            "status": "unknown",
                            "result": None
                        }
                else:
                    logger.error(
                        f"Failed to start workflow: {start_response.status_code}"
                    )
                    return {
                        "workflow_id": None,
                        "status": "failed",
                        "result": {"error": "Failed to start workflow"}
                    }

        except Exception as e:
            logger.error(f"Failed to execute scenario as workflow: {e}")
            return {
                "workflow_id": None,
                "status": "error",
                "result": {"error": str(e)}
            }

    async def register_scenario_as_activity(
        self,
        scenario_id: str,
        activity_name: str
    ) -> Dict[str, Any]:
        """
        Зарегистрировать сценарий как Temporal activity

        Args:
            scenario_id: ID сценария
            activity_name: Имя activity

        Returns:
            Dict with:
                - registered: bool успешно ли зарегистрировано
                - activity_id: str ID activity
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.workflow_url}/api/v1/activities/register",
                    json={
                        "activity_name": activity_name,
                        "handler_type": "scenario",
                        "handler_id": scenario_id
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Registered scenario {scenario_id} as activity "
                        f"{activity_name}"
                    )
                    return result
                else:
                    return {
                        "registered": False,
                        "activity_id": None
                    }

        except Exception as e:
            logger.error(f"Failed to register scenario as activity: {e}")
            return {
                "registered": False,
                "activity_id": None
            }

    async def get_workflow_status(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Получить статус workflow

        Args:
            workflow_id: ID workflow

        Returns:
            Dict with:
                - status: str (running, completed, failed, cancelled)
                - progress: float (0-1) прогресс выполнения
                - current_step: str текущий шаг
                - result: Optional[Dict] результат
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.workflow_url}/api/v1/workflows/{workflow_id}/status",
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "status": "unknown",
                        "progress": 0.0,
                        "current_step": None,
                        "result": None
                    }

        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return {
                "status": "error",
                "progress": 0.0,
                "current_step": None,
                "result": None
            }

    async def cancel_workflow(
        self,
        workflow_id: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Отменить workflow

        Args:
            workflow_id: ID workflow
            reason: Причина отмены

        Returns:
            Dict with:
                - cancelled: bool успешно ли отменено
                - final_state: Dict финальное состояние
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.workflow_url}/api/v1/workflows/{workflow_id}/cancel",
                    json={"reason": reason or "User requested cancellation"},
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Cancelled workflow {workflow_id}")
                    return result
                else:
                    return {
                        "cancelled": False,
                        "final_state": None
                    }

        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            return {
                "cancelled": False,
                "final_state": None
            }


# Global instance
_adapter: Optional[ScenarioWorkflowAdapter] = None


def get_workflow_adapter() -> ScenarioWorkflowAdapter:
    """Get global Workflow adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioWorkflowAdapter()
    return _adapter
