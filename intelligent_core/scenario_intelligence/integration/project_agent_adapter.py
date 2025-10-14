"""
Project Agent Adapter
Интеграция с Project Agent для управления генерацией сценариев
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
PROJECT_AGENT_URL = "http://project-agent:8060"


class ProjectAgentAdapter:
    """
    Adapter для интеграции с Project Agent

    Project Agent управляет:
    - Запуск генерации сценариев
    - Создание задач на основе сценариев
    - Отслеживание прогресса выполнения
    - Обновление приоритетов на основе результатов
    """

    def __init__(self, project_agent_url: str = PROJECT_AGENT_URL):
        self.project_agent_url = project_agent_url

    async def trigger_generation(self, generation_type: str = "full") -> Dict[str, Any]:
        """
        Trigger scenario generation

        Args:
            generation_type: "full", "l1_only", "l2_only", etc.

        Returns:
            Generation task details
        """
        try:
            logger.info(f"Triggering generation: {generation_type}")

            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.project_agent_url}/tasks/create",
                    json={
                        "title": f"Generate {generation_type} scenarios",
                        "description": f"Auto-generate scenarios from service catalog",
                        "task_type": "scenario_generation",
                        "priority": "high",
                        "metadata": {
                            "generation_type": generation_type,
                            "triggered_by": "scenario-intelligence",
                            "triggered_at": datetime.now().isoformat()
                        }
                    }
                )

                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"✅ Generation task created: {result.get('task_id')}")
                    return result
                else:
                    logger.error(f"Failed to trigger generation: {response.status_code}")
                    return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Error triggering generation: {e}")
            return {"error": str(e)}

    async def create_tasks_from_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        priorities: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create execution tasks from scenarios

        Args:
            scenarios: List of scenario dicts
            priorities: Dict of {scenario_id: {priority, confidence, reasons}}

        Returns:
            List of created tasks
        """
        try:
            logger.info(f"Creating tasks for {len(scenarios)} scenarios")

            created_tasks = []

            for scenario in scenarios:
                scenario_id = scenario["meta"]["id"]
                priority_data = priorities.get(scenario_id, {})

                # Determine task priority
                priority_level = priority_data.get("priority", "MEDIUM")
                task_priority = self._map_priority(priority_level)

                # Create task
                task = await self._create_scenario_execution_task(
                    scenario=scenario,
                    priority=task_priority,
                    priority_data=priority_data
                )

                if task:
                    created_tasks.append(task)

            logger.info(f"✅ Created {len(created_tasks)} tasks")
            return created_tasks

        except Exception as e:
            logger.error(f"Error creating tasks: {e}")
            return []

    async def _create_scenario_execution_task(
        self,
        scenario: Dict[str, Any],
        priority: str,
        priority_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create individual scenario execution task"""
        try:
            meta = scenario["meta"]
            description_text = scenario.get("description", {})

            # Build task description
            reasons = priority_data.get("reasons", [])
            reasons_text = "\n".join(f"- {r}" for r in reasons) if reasons else "Standard execution"

            task_data = {
                "title": f"Execute Scenario: {description_text.get('title', meta['id'])}",
                "description": f"""
**Scenario**: {meta['id']}
**Level**: L{meta['level']}
**Type**: {meta['type']}

**Description**: {description_text.get('summary', 'No description')}

**Priority Reasons**:
{reasons_text}

**Confidence**: {priority_data.get('confidence', 0):.2f}
                """,
                "task_type": "scenario_execution",
                "priority": priority,
                "metadata": {
                    "scenario_id": meta["id"],
                    "scenario_level": meta["level"],
                    "scenario_type": meta["type"],
                    "priority_score": priority_data.get("priority"),
                    "confidence": priority_data.get("confidence"),
                    "assigned_to": "scenario-intelligence",
                    "created_at": datetime.now().isoformat()
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.project_agent_url}/tasks/create",
                    json=task_data
                )

                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.warning(f"Failed to create task for {meta['id']}: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    def _map_priority(self, priority_level: str) -> str:
        """Map priority level to Project Agent priority"""
        mapping = {
            "CRITICAL": "critical",
            "HIGH": "high",
            "MEDIUM": "normal",
            "LOW": "low"
        }
        return mapping.get(priority_level, "normal")

    async def update_task_priorities(
        self,
        priorities: Dict[str, Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Update task priorities based on new predictions

        Args:
            priorities: Updated priorities dict

        Returns:
            {"updated": count, "failed": count}
        """
        try:
            logger.info(f"Updating priorities for {len(priorities)} scenarios")

            updated = 0
            failed = 0

            for scenario_id, priority_data in priorities.items():
                success = await self._update_scenario_task_priority(scenario_id, priority_data)

                if success:
                    updated += 1
                else:
                    failed += 1

            logger.info(f"✅ Updated {updated} priorities, {failed} failed")

            return {"updated": updated, "failed": failed}

        except Exception as e:
            logger.error(f"Error updating priorities: {e}")
            return {"updated": 0, "failed": len(priorities)}

    async def _update_scenario_task_priority(
        self,
        scenario_id: str,
        priority_data: Dict[str, Any]
    ) -> bool:
        """Update priority for specific scenario task"""
        try:
            # Find task by scenario_id
            task = await self._find_task_by_scenario(scenario_id)

            if not task:
                logger.warning(f"Task not found for scenario: {scenario_id}")
                return False

            task_id = task["task_id"]
            new_priority = self._map_priority(priority_data.get("priority", "MEDIUM"))

            # Update task
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.project_agent_url}/tasks/{task_id}",
                    json={
                        "priority": new_priority,
                        "metadata": {
                            **task.get("metadata", {}),
                            "priority_updated_at": datetime.now().isoformat(),
                            "priority_confidence": priority_data.get("confidence"),
                            "priority_reasons": priority_data.get("reasons", [])
                        }
                    }
                )

                return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"Error updating task priority for {scenario_id}: {e}")
            return False

    async def _find_task_by_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Find task by scenario_id"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.project_agent_url}/tasks",
                    params={"task_type": "scenario_execution"}
                )

                if response.status_code == 200:
                    tasks = response.json().get("tasks", [])

                    for task in tasks:
                        if task.get("metadata", {}).get("scenario_id") == scenario_id:
                            return task

            return None

        except Exception as e:
            logger.error(f"Error finding task: {e}")
            return None

    async def track_scenario_execution(self) -> Dict[str, Any]:
        """
        Track progress of scenario execution tasks

        Returns:
            {
                "total_tasks": int,
                "pending": int,
                "in_progress": int,
                "completed": int,
                "failed": int
            }
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.project_agent_url}/tasks",
                    params={"task_type": "scenario_execution"}
                )

                if response.status_code == 200:
                    tasks = response.json().get("tasks", [])

                    stats = {
                        "total_tasks": len(tasks),
                        "pending": 0,
                        "in_progress": 0,
                        "completed": 0,
                        "failed": 0
                    }

                    for task in tasks:
                        status = task.get("status", "unknown")
                        if status in stats:
                            stats[status] += 1

                    return stats
                else:
                    return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Error tracking execution: {e}")
            return {"error": str(e)}

    async def report_generation_complete(
        self,
        results: Dict[str, Any]
    ) -> bool:
        """
        Report generation cycle completion to Project Agent

        Args:
            results: Generation results

        Returns:
            Success status
        """
        try:
            logger.info("Reporting generation completion to Project Agent")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.project_agent_url}/events/generation_complete",
                    json={
                        "event_type": "scenario_generation_complete",
                        "timestamp": datetime.now().isoformat(),
                        "results": results
                    }
                )

                success = response.status_code in [200, 201]

                if success:
                    logger.info("✅ Generation completion reported")
                else:
                    logger.warning(f"Failed to report completion: {response.status_code}")

                return success

        except Exception as e:
            logger.error(f"Error reporting completion: {e}")
            return False

    async def health_check(self) -> bool:
        """Check if Project Agent is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.project_agent_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Global instance
_project_agent_adapter: Optional[ProjectAgentAdapter] = None


def get_project_agent_adapter() -> ProjectAgentAdapter:
    """Get or create global Project Agent adapter"""
    global _project_agent_adapter

    if _project_agent_adapter is None:
        _project_agent_adapter = ProjectAgentAdapter()

    return _project_agent_adapter
