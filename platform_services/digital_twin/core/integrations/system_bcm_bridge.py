"""
System BCM Bridge
Integration with System BCM Service (Port 8050)

Provides:
- BCM cycle monitoring
- Recovery triggering
- Platform health tracking
- Improvement tracking
"""

import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemBCMBridge:
    """
    System BCM Bridge

    Integration bridge to System BCM Service for business continuity management.
    Monitors BCM cycles, recovery procedures, and platform improvements.

    Features:
    - BCM cycle monitoring and triggering
    - Recovery procedure execution
    - Platform health tracking
    - Improvement tracking
    - EventBus integration
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8050",
        timeout: float = 30.0,
        api_key: Optional[str] = None
    ):
        """
        Initialize System BCM bridge

        Args:
            base_url: Base URL of System BCM service
            timeout: HTTP request timeout
            api_key: API key for authentication (if required)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DigitalTwin-SystemBCMBridge/1.0.0"
        }

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.client = httpx.AsyncClient(timeout=timeout, headers=headers)
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Connect to System BCM service and verify availability

        Returns:
            True if connected successfully
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")

            if response.status_code == 200:
                health_data = response.json()
                logger.info(
                    f"✅ Connected to System BCM Service "
                    f"(running={health_data.get('running', False)})"
                )
                self.is_connected = True
                return True

        except Exception as error:
            logger.error(f"Failed to connect to System BCM Service: {error}")
            self.is_connected = False

        return False

    async def get_health(self) -> Dict[str, Any]:
        """
        Get System BCM Service health

        Returns:
            Health status
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

        except Exception as error:
            logger.error(f"Failed to get health: {error}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed System BCM status

        Returns:
            Detailed status including:
            - running: bool
            - cycle_count: int
            - last_cycle_at: str
            - last_cycle_result: dict
            - total_improvements_applied: int
        """
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()

        except Exception as error:
            logger.error(f"Failed to get status: {error}")
            raise

    async def trigger_cycle(self) -> Dict[str, Any]:
        """
        Manually trigger a BCM cycle

        BCM cycle includes:
        1. Health Check - Check all services
        2. Analyze - Identify issues
        3. Improve - Apply improvements
        4. Verify - Verify improvements worked

        Returns:
            Cycle execution results
        """
        try:
            logger.info("🔄 Triggering BCM cycle...")
            response = await self.client.post(f"{self.base_url}/cycle/trigger")
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ BCM cycle completed: {result.get('status')}")
            return result

        except Exception as error:
            logger.error(f"Failed to trigger cycle: {error}")
            raise

    async def trigger_recovery(
        self,
        service: str,
        incident_type: str
    ) -> Dict[str, Any]:
        """
        Manually trigger recovery for a service

        Args:
            service: Service name (e.g., "api-gateway", "simulation-service")
            incident_type: Type of incident
                - "failure": Complete service failure
                - "degradation": Performance degradation
                - "connection_error": Connection issues
                - "timeout": Timeout issues
                - "resource_exhaustion": Resource issues

        Returns:
            Recovery trigger response
        """
        try:
            logger.info(f"🚨 Triggering recovery for {service} ({incident_type})...")

            response = await self.client.post(
                f"{self.base_url}/recovery/trigger",
                params={
                    "service": service,
                    "incident_type": incident_type
                }
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Recovery triggered: {result.get('status')}")
            return result

        except Exception as error:
            logger.error(f"Failed to trigger recovery: {error}")
            raise

    async def get_metrics(self) -> str:
        """
        Get Prometheus metrics from System BCM

        Returns:
            Metrics in Prometheus format
        """
        try:
            response = await self.client.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            return response.text

        except Exception as error:
            logger.error(f"Failed to get metrics: {error}")
            raise

    async def get_last_cycle_result(self) -> Optional[Dict[str, Any]]:
        """
        Get results from last BCM cycle

        Returns:
            Last cycle results or None if no cycles run yet
        """
        try:
            status = await self.get_status()
            return status.get("last_cycle_result")

        except Exception as error:
            logger.error(f"Failed to get last cycle result: {error}")
            return None

    async def get_cycle_count(self) -> int:
        """
        Get total number of BCM cycles executed

        Returns:
            Cycle count
        """
        try:
            status = await self.get_status()
            return status.get("cycle_count", 0)

        except Exception as error:
            logger.error(f"Failed to get cycle count: {error}")
            return 0

    async def get_improvements_applied(self) -> int:
        """
        Get total number of improvements applied

        Returns:
            Total improvements count
        """
        try:
            status = await self.get_status()
            return status.get("total_improvements_applied", 0)

        except Exception as error:
            logger.error(f"Failed to get improvements count: {error}")
            return 0

    async def is_healthy(self) -> bool:
        """
        Quick health check (boolean)

        Returns:
            True if System BCM is healthy and running
        """
        try:
            health = await self.get_health()
            return health.get("status") == "healthy" and health.get("running") == True

        except:
            return False

    async def get_platform_continuity_status(self) -> Dict[str, Any]:
        """
        Get overall platform business continuity status

        Returns:
            Continuity status including:
            - bcm_running: bool
            - last_cycle: dict
            - cycle_count: int
            - improvements_applied: int
            - platform_health: str
        """
        try:
            status = await self.get_status()
            health = await self.get_health()

            return {
                "bcm_running": status.get("running", False),
                "bcm_healthy": health.get("status") == "healthy",
                "last_cycle": {
                    "timestamp": status.get("last_cycle_at"),
                    "result": status.get("last_cycle_result")
                },
                "cycle_count": status.get("cycle_count", 0),
                "improvements_applied": status.get("total_improvements_applied", 0),
                "retrieved_at": datetime.utcnow().isoformat()
            }

        except Exception as error:
            logger.error(f"Failed to get platform continuity status: {error}")
            return {
                "bcm_running": False,
                "bcm_healthy": False,
                "error": str(error)
            }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
