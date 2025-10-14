"""
Process Analytics Client
=========================

Client for communicating with Process Analytics service (port 8780).
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import settings
from models import ProcessMiningMetrics

logger = logging.getLogger(__name__)


class ProcessAnalyticsClient:
    """
    Client for Process Analytics service

    Provides methods to query process mining insights from process_analytics service.

    Example:
        ```python
        client = ProcessAnalyticsClient()
        summary = await client.get_summary("bia_workflow")
        print(f"Average duration: {summary['avg_duration_minutes']} minutes")
        ```
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Process Analytics client

        Args:
            base_url: Base URL of process-analytics service.
                     If None, uses settings.PROCESS_ANALYTICS_URL
        """
        self.base_url = base_url or settings.PROCESS_ANALYTICS_URL
        self.timeout = 30.0
        logger.info(f"ProcessAnalyticsClient initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if process-analytics service is healthy

        Returns:
            Health status dict

        Example:
            ```python
            health = await client.health_check()
            if health["status"] == "healthy":
                print("Service is up!")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Process Analytics health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def get_summary(self, process_id: str) -> Dict[str, Any]:
        """
        Get summary for a specific process

        Args:
            process_id: Process identifier (e.g., "bia_workflow")

        Returns:
            Process summary with metrics

        Example:
            ```python
            summary = await client.get_summary("bia_workflow")
            print(f"Executions: {summary['total_executions']}")
            print(f"Avg duration: {summary['avg_duration_minutes']} min")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/process-mining/processes/{process_id}/summary"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Process {process_id} not found")
                return {"error": "Process not found", "process_id": process_id}
            logger.error(f"Failed to get summary for {process_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get summary for {process_id}: {e}")
            raise

    async def discover_patterns(self, process_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Discover patterns in process execution

        Args:
            process_id: Process identifier
            days_back: Number of days to analyze (default: 30)

        Returns:
            List of discovered patterns

        Example:
            ```python
            patterns = await client.discover_patterns("bia_workflow")
            for pattern in patterns:
                print(f"Found pattern: {pattern['pattern_type']}")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/process-mining/discover-patterns/{process_id}",
                    params={"days_back": days_back}
                )
                response.raise_for_status()
                return response.json().get("patterns", [])
        except Exception as e:
            logger.error(f"Failed to discover patterns for {process_id}: {e}")
            return []

    async def detect_bottlenecks(self, process_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Detect bottlenecks in process

        Args:
            process_id: Process identifier
            days_back: Number of days to analyze (default: 30)

        Returns:
            List of bottlenecks found

        Example:
            ```python
            bottlenecks = await client.detect_bottlenecks("bia_workflow")
            for b in bottlenecks:
                print(f"Bottleneck: {b['step_name']} ({b['avg_duration_minutes']} min)")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/process-mining/analyze-performance/{process_id}",
                    params={"days_back": days_back}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("bottlenecks", [])
        except Exception as e:
            logger.error(f"Failed to detect bottlenecks for {process_id}: {e}")
            return []

    async def detect_deviations(self, process_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Detect deviations from expected process flow

        Args:
            process_id: Process identifier
            days_back: Number of days to analyze (default: 30)

        Returns:
            List of deviations found

        Example:
            ```python
            deviations = await client.detect_deviations("bia_workflow")
            for d in deviations:
                print(f"Deviation: {d['type']} in {d['step_name']}")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/process-mining/detect-deviations/{process_id}",
                    params={"days_back": days_back}
                )
                response.raise_for_status()
                return response.json().get("deviations", [])
        except Exception as e:
            logger.error(f"Failed to detect deviations for {process_id}: {e}")
            return []

    async def comprehensive_analysis(self, process_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a process

        Combines summary, patterns, bottlenecks, and deviations.

        Args:
            process_id: Process identifier

        Returns:
            Complete analysis report

        Example:
            ```python
            analysis = await client.comprehensive_analysis("bia_workflow")
            print(f"Health score: {analysis['health_score']}")
            print(f"Bottlenecks: {len(analysis['bottlenecks'])}")
            ```
        """
        try:
            # Gather all data
            summary = await self.get_summary(process_id)
            patterns = await self.discover_patterns(process_id)
            bottlenecks = await self.detect_bottlenecks(process_id)
            deviations = await self.detect_deviations(process_id)

            # Calculate health score
            health_score = self._calculate_health_score(
                summary, bottlenecks, deviations
            )

            return {
                "process_id": process_id,
                "summary": summary,
                "patterns": patterns,
                "bottlenecks": bottlenecks,
                "deviations": deviations,
                "health_score": health_score,
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {process_id}: {e}")
            return {
                "process_id": process_id,
                "error": str(e),
                "health_score": 0,
                "analyzed_at": datetime.now().isoformat()
            }

    async def get_all_processes(self) -> List[str]:
        """
        Get list of all tracked processes

        Returns:
            List of process IDs

        Example:
            ```python
            processes = await client.get_all_processes()
            print(f"Tracking {len(processes)} processes")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/process-mining/processes"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("processes", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Endpoint doesn't exist yet, return common BCM processes
                logger.warning("Processes list endpoint not available, using default BCM processes")
                return [
                    "bia_workflow",
                    "risk_assessment",
                    "incident_response",
                    "compliance_audit",
                    "plan_generation",
                    "exercise_design"
                ]
            logger.error(f"Failed to get processes: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get all processes: {e}")
            return []

    async def log_execution(
        self,
        process_id: str,
        execution_id: str,
        start_time: datetime,
        status: str = "running",
        executed_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a process execution (for testing/integration)

        Args:
            process_id: Process identifier
            execution_id: Unique execution ID
            start_time: When execution started
            status: Execution status (running, completed, failed)
            executed_by: Who/what executed it
            metadata: Additional metadata

        Returns:
            Created execution record

        Example:
            ```python
            await client.log_execution(
                process_id="bia_workflow",
                execution_id="exec_001",
                start_time=datetime.now(),
                executed_by="user_123"
            )
            ```
        """
        try:
            payload = {
                "process_id": process_id,
                "execution_id": execution_id,
                "start_time": start_time.isoformat(),
                "status": status,
                "executed_by": executed_by,
                "execution_metadata": metadata or {}
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/process-mining/log-execution",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
            raise

    def _calculate_health_score(
        self,
        summary: Dict[str, Any],
        bottlenecks: List[Dict[str, Any]],
        deviations: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate process health score (0-100)

        Factors:
        - Success rate (40 points)
        - Bottlenecks (30 points penalty)
        - Deviations (30 points penalty)

        Args:
            summary: Process summary
            bottlenecks: Bottlenecks found
            deviations: Deviations found

        Returns:
            Health score 0-100
        """
        score = 100.0

        # Success rate impact (up to -40 points)
        success_rate = summary.get("success_rate", 1.0)
        score -= (1 - success_rate) * 40

        # Bottlenecks impact (up to -30 points)
        bottleneck_count = len(bottlenecks)
        score -= min(bottleneck_count * 10, 30)

        # Deviations impact (up to -30 points)
        deviation_count = len(deviations)
        score -= min(deviation_count * 10, 30)

        return max(0, min(100, score))
