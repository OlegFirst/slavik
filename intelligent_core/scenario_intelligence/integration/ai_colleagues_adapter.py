"""
AI Colleagues Adapter
Распределение сценариев на всех AI коллег для изучения
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# AI Colleagues configuration
AI_COLLEAGUES = {
    "mio-manager": {
        "url": "http://mio-manager:8053",
        "capabilities": ["task_coordination", "agent_orchestration", "priority_management"]
    },
    "analytics-specialist": {
        "url": "http://analytics-specialist:8054",
        "capabilities": ["system_analysis", "metrics_analysis", "performance_monitoring"]
    },
    "devops-agent": {
        "url": "http://devops-agent:8061",
        "capabilities": ["infrastructure_management", "deployment", "monitoring"]
    },
    "project-agent": {
        "url": "http://project-agent:8060",
        "capabilities": ["project_management", "task_tracking", "code_quality"]
    },
    "agent-router": {
        "url": "http://agent-router:8052",
        "capabilities": ["routing", "delegation", "load_balancing"]
    },
    "ai-event-manager": {
        "url": "http://ai-event-manager:8055",
        "capabilities": ["event_management", "workflow_orchestration", "state_management"]
    }
}


class AIColleaguesAdapter:
    """
    Adapter для распределения сценариев всем AI коллегам

    После генерации сценарии отправляются всем AI агентам для:
    - Изучения системного поведения
    - Обновления knowledge base
    - Координации работы
    - Предсказания failures
    """

    def __init__(self):
        self.colleagues = AI_COLLEAGUES

    async def distribute_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        targets: Optional[List[str]] = None
    ) -> List[str]:
        """
        Distribute scenarios to AI colleagues

        Args:
            scenarios: List of scenario dicts
            targets: Specific colleagues (None = all)

        Returns:
            List of notified colleague names
        """
        try:
            logger.info(f"Distributing {len(scenarios)} scenarios to AI colleagues")

            # Determine targets
            colleagues_to_notify = targets if targets else list(self.colleagues.keys())

            notified = []

            for colleague_name in colleagues_to_notify:
                if colleague_name not in self.colleagues:
                    logger.warning(f"Unknown colleague: {colleague_name}")
                    continue

                colleague = self.colleagues[colleague_name]

                success = await self._notify_colleague(
                    colleague_name=colleague_name,
                    colleague_url=colleague["url"],
                    scenarios=scenarios
                )

                if success:
                    notified.append(colleague_name)
                    logger.info(f" {colleague_name} notified")
                else:
                    logger.warning(f" {colleague_name} failed")

            logger.info(f" Notified {len(notified)}/{len(colleagues_to_notify)} colleagues")

            return notified

        except Exception as e:
            logger.error(f"Error distributing scenarios: {e}")
            return []

    async def _notify_colleague(
        self,
        colleague_name: str,
        colleague_url: str,
        scenarios: List[Dict[str, Any]]
    ) -> bool:
        """Notify individual colleague"""
        try:
            # Prepare notification payload
            payload = {
                "event_type": "scenarios_generated",
                "source": "scenario-intelligence",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "total_scenarios": len(scenarios),
                    "scenarios_by_level": self._group_by_level(scenarios),
                    "scenarios_by_type": self._group_by_type(scenarios),
                    "scenarios": self._prepare_scenarios_for_colleague(scenarios, colleague_name)
                }
            }

            # Send notification
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try /events/scenario_update endpoint
                response = await client.post(
                    f"{colleague_url}/events/scenario_update",
                    json=payload
                )

                if response.status_code in [200, 201, 404]:
                    # 404 = endpoint doesn't exist, but colleague is alive
                    if response.status_code == 404:
                        # Try alternative endpoint
                        response = await client.post(
                            f"{colleague_url}/knowledge/update",
                            json=payload
                        )

                    return response.status_code in [200, 201]

                return False

        except httpx.TimeoutException:
            logger.warning(f"Timeout notifying {colleague_name}")
            return False
        except Exception as e:
            logger.error(f"Error notifying {colleague_name}: {e}")
            return False

    def _group_by_level(self, scenarios: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group scenarios by level"""
        groups = {}
        for scenario in scenarios:
            level = f"L{scenario['meta']['level']}"
            groups[level] = groups.get(level, 0) + 1
        return groups

    def _group_by_type(self, scenarios: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group scenarios by type"""
        groups = {}
        for scenario in scenarios:
            scenario_type = scenario['meta']['type']
            groups[scenario_type] = groups.get(scenario_type, 0) + 1
        return groups

    def _prepare_scenarios_for_colleague(
        self,
        scenarios: List[Dict[str, Any]],
        colleague_name: str
    ) -> List[Dict[str, Any]]:
        """
        Prepare scenarios for specific colleague

        Filter and customize based on colleague's capabilities
        """
        colleague_capabilities = self.colleagues[colleague_name]["capabilities"]

        # All colleagues get summary
        prepared = []

        for scenario in scenarios:
            # Create summary version
            summary = {
                "scenario_id": scenario["meta"]["id"],
                "level": scenario["meta"]["level"],
                "type": scenario["meta"]["type"],
                "title": scenario.get("description", {}).get("title", ""),
                "summary": scenario.get("description", {}).get("summary", ""),
                "module": scenario["meta"].get("module"),
                "subsystem": scenario["meta"].get("subsystem"),
                "tags": scenario["meta"].get("tags", [])
            }

            # Add capability-specific data
            if "system_analysis" in colleague_capabilities:
                # Analytics Specialist gets metrics
                summary["observability"] = scenario.get("observability", {})
                summary["sla"] = scenario.get("sla", {})

            if "infrastructure_management" in colleague_capabilities:
                # DevOps Agent gets infrastructure details
                summary["execution"] = scenario.get("execution", {})
                summary["chaos"] = scenario.get("chaos", {})

            if "task_coordination" in colleague_capabilities:
                # MIO Manager gets integration details
                summary["integration"] = scenario.get("integration", {})

            prepared.append(summary)

        return prepared

    async def notify_execution_started(
        self,
        scenario_id: str,
        execution_id: str
    ) -> int:
        """
        Notify AI colleagues that scenario execution started

        Args:
            scenario_id: Scenario ID
            execution_id: Execution ID

        Returns:
            Number of notified colleagues
        """
        try:
            payload = {
                "event_type": "scenario_execution_started",
                "source": "scenario-intelligence",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "scenario_id": scenario_id,
                    "execution_id": execution_id
                }
            }

            notified = 0

            for colleague_name, colleague in self.colleagues.items():
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.post(
                            f"{colleague['url']}/events/execution_started",
                            json=payload
                        )

                        if response.status_code in [200, 201]:
                            notified += 1

                except Exception:
                    pass  # Silent fail for notifications

            return notified

        except Exception as e:
            logger.error(f"Error notifying execution start: {e}")
            return 0

    async def notify_execution_completed(
        self,
        scenario_id: str,
        execution_id: str,
        result: Dict[str, Any]
    ) -> int:
        """
        Notify AI colleagues that scenario execution completed

        Args:
            scenario_id: Scenario ID
            execution_id: Execution ID
            result: Execution result

        Returns:
            Number of notified colleagues
        """
        try:
            payload = {
                "event_type": "scenario_execution_completed",
                "source": "scenario-intelligence",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "scenario_id": scenario_id,
                    "execution_id": execution_id,
                    "status": result.get("status"),
                    "duration_ms": result.get("duration_ms"),
                    "success": result.get("success", False)
                }
            }

            notified = 0

            for colleague_name, colleague in self.colleagues.items():
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.post(
                            f"{colleague['url']}/events/execution_completed",
                            json=payload
                        )

                        if response.status_code in [200, 201]:
                            notified += 1

                except Exception:
                    pass  # Silent fail for notifications

            return notified

        except Exception as e:
            logger.error(f"Error notifying execution completion: {e}")
            return 0

    async def check_colleagues_health(self) -> Dict[str, bool]:
        """
        Check health of all AI colleagues

        Returns:
            {colleague_name: is_healthy}
        """
        health_status = {}

        for colleague_name, colleague in self.colleagues.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{colleague['url']}/health")
                    health_status[colleague_name] = response.status_code == 200

            except Exception:
                health_status[colleague_name] = False

        return health_status


# Global instance
_ai_colleagues_adapter: Optional[AIColleaguesAdapter] = None


def get_ai_colleagues_adapter() -> AIColleaguesAdapter:
    """Get or create global AI Colleagues adapter"""
    global _ai_colleagues_adapter

    if _ai_colleagues_adapter is None:
        _ai_colleagues_adapter = AIColleaguesAdapter()

    return _ai_colleagues_adapter
