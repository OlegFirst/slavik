"""
MIO Manager Client
==================

Client for communicating with MIO Manager (port 8046).

MIO Manager is the coordinator of AI Office - all colleagues report to МиО.
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..config import settings
from ..models import MIOEventInsight, MIOTaskDelegation, SeverityLevel

logger = logging.getLogger(__name__)


class MIOManagerClient:
    """
    Client for MIO Manager service

    MIO Manager coordinates all AI Office colleagues. Analytics Specialist
    reports insights and requests task delegation through this client.

    Example:
        ```python
        mio = MIOManagerClient()

        # Report insights
        await mio.report_insights({
            "severity": "high",
            "critical_issues": [...],
            "recommendations": [...]
        })

        # Request task delegation
        await mio.delegate_task({
            "title": "Fix bottlenecks",
            "priority": "high"
        })
        ```
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize MIO Manager client

        Args:
            base_url: Base URL of MIO Manager service.
                     If None, uses settings.MIO_MANAGER_URL
        """
        self.base_url = base_url or settings.MIO_MANAGER_URL
        self.timeout = 30.0
        logger.info(f"MIOManagerClient initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if MIO Manager is healthy

        Returns:
            Health status dict

        Example:
            ```python
            health = await mio.health_check()
            if health["status"] == "healthy":
                print("MIO Manager is up!")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"MIO Manager health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def report_insights(
        self,
        event_insight: MIOEventInsight
    ) -> Dict[str, Any]:
        """
        Report analytics insights to MIO Manager

        This is the main communication channel from Analytics Specialist to МиО.
        МиО will decide what actions to take based on severity and recommendations.

        Args:
            event_insight: Event insight to report

        Returns:
            Response from MIO Manager

        Example:
            ```python
            insight = MIOEventInsight(
                event_type="daily_health_check",
                severity=SeverityLevel.HIGH,
                critical_issues=[
                    {"title": "3 bottlenecks detected"}
                ],
                recommendations=[
                    {"action": "allocate_resources"}
                ],
                summary="Platform health: 78.5/100"
            )

            response = await mio.report_insights(insight)
            print(f"MIO response: {response['status']}")
            ```
        """
        try:
            payload = event_insight.model_dump()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/insights/report",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()

                logger.info(
                    f"Reported insights to MIO Manager: "
                    f"severity={event_insight.severity}, "
                    f"issues={len(event_insight.critical_issues)}"
                )

                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to report insights (HTTP {e.response.status_code}): {e}")
            # Return graceful failure
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}",
                "message": "Failed to report to MIO Manager"
            }
        except Exception as e:
            logger.error(f"Failed to report insights: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to report to MIO Manager"
            }

    async def delegate_task(
        self,
        task: MIOTaskDelegation
    ) -> Dict[str, Any]:
        """
        Request МиО to delegate a task to Orchestrator

        For critical issues that require immediate action, Analytics Specialist
        can request МиО to delegate task to Orchestrator for execution.

        Args:
            task: Task delegation request

        Returns:
            Response from MIO Manager

        Example:
            ```python
            task = MIOTaskDelegation(
                title="Fix critical bottlenecks",
                priority="high",
                actions=[
                    {
                        "type": "allocate_resources",
                        "target": "approval_step",
                        "count": 2
                    }
                ]
            )

            response = await mio.delegate_task(task)
            print(f"Task delegated: {response['task_id']}")
            ```
        """
        try:
            payload = task.model_dump()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/tasks/delegate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()

                logger.info(
                    f"Delegated task to MIO Manager: "
                    f"title={task.title}, priority={task.priority}"
                )

                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to delegate task (HTTP {e.response.status_code}): {e}")
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}",
                "message": "Failed to delegate task"
            }
        except Exception as e:
            logger.error(f"Failed to delegate task: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to delegate task"
            }

    async def get_colleague_status(self, colleague_name: str) -> Dict[str, Any]:
        """
        Get status of another AI Office colleague

        Args:
            colleague_name: Name of colleague (e.g., "ai-event-manager")

        Returns:
            Colleague status

        Example:
            ```python
            status = await mio.get_colleague_status("ai-event-manager")
            print(f"Event Manager health: {status['health']}")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/colleagues/{colleague_name}/status"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get colleague status for {colleague_name}: {e}")
            return {"status": "unknown", "error": str(e)}

    async def request_coordination(
        self,
        coordination_type: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Request coordination from МиО

        For complex tasks that require coordination between multiple colleagues,
        Analytics Specialist can request МиО's coordination.

        Args:
            coordination_type: Type of coordination needed
            details: Coordination details

        Returns:
            Coordination response

        Example:
            ```python
            response = await mio.request_coordination(
                coordination_type="multi_colleague_analysis",
                details={
                    "incident_id": "inc_001",
                    "colleagues_needed": ["ai-event-manager", "project-agent"],
                    "reason": "Complex incident requiring multiple perspectives"
                }
            )
            ```
        """
        try:
            payload = {
                "requester": "analytics-specialist",
                "coordination_type": coordination_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/coordination/request",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to request coordination: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to request coordination"
            }

    async def heartbeat(self) -> Dict[str, Any]:
        """
        Send heartbeat to МиО Manager

        Let МиО know Analytics Specialist is alive and healthy.
        Should be called periodically (e.g., every 5 minutes).

        Returns:
            Heartbeat acknowledgment

        Example:
            ```python
            @scheduled(interval="5min")
            async def send_heartbeat():
                await mio.heartbeat()
            ```
        """
        try:
            payload = {
                "colleague": "analytics-specialist",
                "status": "healthy",
                "competency_level": settings.COMPETENCY_LEVEL,
                "timestamp": datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/heartbeat",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.warning(f"Heartbeat failed: {e}")
            return {"status": "failed", "error": str(e)}


# Convenience functions for common patterns

async def report_daily_health_check(
    mio_client: MIOManagerClient,
    health_score: float,
    critical_issues: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to report daily health check

    Args:
        mio_client: MIO Manager client instance
        health_score: Overall health score (0-100)
        critical_issues: List of critical issues
        recommendations: List of recommendations
        metadata: Additional metadata

    Returns:
        MIO Manager response

    Example:
        ```python
        await report_daily_health_check(
            mio_client=mio,
            health_score=78.5,
            critical_issues=[...],
            recommendations=[...]
        )
        ```
    """
    # Determine severity based on health score
    if health_score < 50:
        severity = SeverityLevel.CRITICAL
    elif health_score < 70:
        severity = SeverityLevel.HIGH
    elif health_score < 85:
        severity = SeverityLevel.MEDIUM
    else:
        severity = SeverityLevel.LOW

    insight = MIOEventInsight(
        event_type="daily_health_check",
        severity=severity,
        critical_issues=critical_issues,
        recommendations=recommendations,
        summary=f"Platform health score: {health_score:.1f}/100. "
                f"{len(critical_issues)} critical issues, "
                f"{len(recommendations)} recommendations.",
        metadata=metadata or {}
    )

    return await mio_client.report_insights(insight)


async def report_incident_investigation(
    mio_client: MIOManagerClient,
    incident_id: str,
    root_cause: Dict[str, Any],
    prevention_plan: List[Dict[str, Any]],
    severity: SeverityLevel = SeverityLevel.HIGH
) -> Dict[str, Any]:
    """
    Convenience function to report incident investigation results

    Args:
        mio_client: MIO Manager client instance
        incident_id: Incident identifier
        root_cause: Root cause analysis
        prevention_plan: Prevention recommendations
        severity: Severity level

    Returns:
        MIO Manager response

    Example:
        ```python
        await report_incident_investigation(
            mio_client=mio,
            incident_id="inc_001",
            root_cause={"cause": "memory leak", "component": "service_x"},
            prevention_plan=[...]
        )
        ```
    """
    insight = MIOEventInsight(
        event_type="incident_investigation",
        severity=severity,
        critical_issues=[root_cause],
        recommendations=prevention_plan,
        summary=f"Incident {incident_id} investigation complete. "
                f"Root cause: {root_cause.get('cause', 'unknown')}.",
        metadata={"incident_id": incident_id}
    )

    return await mio_client.report_insights(insight)
