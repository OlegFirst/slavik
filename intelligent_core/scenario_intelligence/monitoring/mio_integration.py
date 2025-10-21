"""
MIO Manager Integration for Scenario Intelligence

Sends KPIs and alerts to MIO Manager for centralized monitoring.
"""

import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class KPIUpdate:
    """KPI update for MIO Manager"""
    service_name: str
    kpi_name: str
    value: float
    unit: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Alert:
    """Alert for MIO Manager"""
    service_name: str
    alert_type: str  # 'warning', 'error', 'critical'
    message: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class MIOManagerClient:
    """
    Client for sending metrics and alerts to MIO Manager

    MIO Manager aggregates KPIs from all services and provides:
    - Centralized monitoring dashboard
    - Alert management
    - Performance tracking
    - Service health checks
    """

    def __init__(self, host: str = 'localhost', port: int = 8020, enabled: bool = True):
        self.host = host
        self.port = port
        self.enabled = enabled
        self.base_url = f"http://{host}:{port}"
        self.service_name = "scenario-intelligence"

        if not enabled:
            logger.info("MIO Manager integration disabled")

    async def send_kpi(self, kpi_name: str, value: float, unit: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Send KPI update to MIO Manager

        Args:
            kpi_name: Name of the KPI (e.g., 'scenarios_generated', 'execution_success_rate')
            value: Numeric value
            unit: Unit of measurement (e.g., 'count', 'percent', 'seconds')
            metadata: Additional context
        """
        if not self.enabled:
            return

        kpi = KPIUpdate(
            service_name=self.service_name,
            kpi_name=kpi_name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/kpis",
                    json=asdict(kpi),
                    timeout=5.0
                )
                response.raise_for_status()
                logger.debug(f"KPI sent to MIO Manager: {kpi_name}={value}")
        except Exception as e:
            logger.warning(f"Failed to send KPI to MIO Manager: {e}")

    async def send_alert(self, alert_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Send alert to MIO Manager

        Args:
            alert_type: 'warning', 'error', or 'critical'
            message: Alert message
            metadata: Additional context
        """
        if not self.enabled:
            return

        alert = Alert(
            service_name=self.service_name,
            alert_type=alert_type,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/alerts",
                    json=asdict(alert),
                    timeout=5.0
                )
                response.raise_for_status()
                logger.info(f"Alert sent to MIO Manager: [{alert_type}] {message}")
        except Exception as e:
            logger.warning(f"Failed to send alert to MIO Manager: {e}")

    async def report_health(self, status: str, details: Optional[Dict[str, Any]] = None):
        """
        Report service health to MIO Manager

        Args:
            status: 'healthy', 'degraded', 'unhealthy'
            details: Health check details
        """
        if not self.enabled:
            return

        health_data = {
            'service_name': self.service_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/health",
                    json=health_data,
                    timeout=5.0
                )
                response.raise_for_status()
                logger.debug(f"Health status sent to MIO Manager: {status}")
        except Exception as e:
            logger.warning(f"Failed to send health status to MIO Manager: {e}")

    # ===================================================
    # CONVENIENCE METHODS FOR SCENARIO INTELLIGENCE KPIs
    # ===================================================

    async def report_scenarios_generated(self, level: str, count: int, generator: str):
        """Report scenario generation"""
        await self.send_kpi(
            kpi_name='scenarios_generated',
            value=count,
            unit='count',
            metadata={'level': level, 'generator': generator}
        )

    async def report_scenarios_executed(self, level: str, count: int, success_rate: float):
        """Report scenario execution"""
        await self.send_kpi(
            kpi_name='scenarios_executed',
            value=count,
            unit='count',
            metadata={'level': level}
        )

        await self.send_kpi(
            kpi_name='execution_success_rate',
            value=success_rate,
            unit='percent',
            metadata={'level': level}
        )

    async def report_generation_duration(self, level: str, duration_seconds: float):
        """Report generation duration"""
        await self.send_kpi(
            kpi_name='generation_duration',
            value=duration_seconds,
            unit='seconds',
            metadata={'level': level}
        )

    async def report_execution_duration(self, level: str, duration_seconds: float):
        """Report execution duration"""
        await self.send_kpi(
            kpi_name='execution_duration',
            value=duration_seconds,
            unit='seconds',
            metadata={'level': level}
        )

    async def report_storage_count(self, backend: str, total_count: int, by_level: Dict[str, int]):
        """Report storage state"""
        await self.send_kpi(
            kpi_name='scenarios_in_storage',
            value=total_count,
            unit='count',
            metadata={'backend': backend, 'by_level': by_level}
        )

    async def alert_generation_failure(self, level: str, error: str):
        """Alert on generation failure"""
        await self.send_alert(
            alert_type='error',
            message=f"Scenario generation failed for {level}",
            metadata={'level': level, 'error': error}
        )

    async def alert_execution_failure(self, scenario_id: str, error: str):
        """Alert on execution failure"""
        await self.send_alert(
            alert_type='error',
            message=f"Scenario execution failed: {scenario_id}",
            metadata={'scenario_id': scenario_id, 'error': error}
        )

    async def alert_storage_error(self, backend: str, operation: str, error: str):
        """Alert on storage error"""
        await self.send_alert(
            alert_type='warning',
            message=f"Storage operation failed: {backend}.{operation}",
            metadata={'backend': backend, 'operation': operation, 'error': error}
        )

    async def alert_eventbus_error(self, event_type: str, error: str):
        """Alert on EventBus error"""
        await self.send_alert(
            alert_type='warning',
            message=f"EventBus error: {event_type}",
            metadata={'event_type': event_type, 'error': error}
        )


# Global MIO Manager client
_mio_client: Optional[MIOManagerClient] = None


def get_mio_client() -> MIOManagerClient:
    """Get global MIO Manager client"""
    global _mio_client
    if _mio_client is None:
        import os
        _mio_client = MIOManagerClient(
            host=os.getenv('MIO_MANAGER_HOST', 'localhost'),
            port=int(os.getenv('MIO_MANAGER_PORT', '8020')),
            enabled=os.getenv('MIO_MANAGER_ENABLED', 'true').lower() == 'true'
        )
    return _mio_client


if __name__ == "__main__":
    import asyncio

    async def test():
        """Test MIO Manager integration"""
        client = MIOManagerClient(enabled=False)  # Test mode

        # Test KPIs
        await client.report_scenarios_generated('l1', 10, 'l1_platform')
        await client.report_scenarios_executed('l1', 5, 100.0)
        await client.report_generation_duration('l1', 2.5)

        # Test alerts
        await client.alert_generation_failure('l4', 'LLM timeout')

        # Test health
        await client.report_health('healthy', {'version': '1.0.0'})

        print(" MIO Manager integration test complete")

    asyncio.run(test())
