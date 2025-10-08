"""
Service Health Monitoring
"""

import logging
from typing import Dict, Any
from datetime import datetime
import httpx

from .config import ServiceConfig

logger = logging.getLogger(__name__)


class ServiceHealthMonitor:
    """
    Health monitoring for microservices

    Tracks service availability and health status
    """

    def __init__(self):
        self.health_status: Dict[str, Dict[str, Any]] = {}

    async def check_health(self, config: ServiceConfig) -> bool:
        """
        Check if service is healthy

        Args:
            config: Service configuration

        Returns:
            True if healthy, False otherwise
        """
        try:
            health_url = f"{config.get_full_url()}{config.health_endpoint}"

            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, timeout=config.timeout)

                is_healthy = response.status_code == 200

                self.health_status[config.service_type] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'last_check': datetime.now().isoformat(),
                    'response_code': response.status_code,
                    'service_name': config.name
                }

                if is_healthy:
                    logger.info(f"✅ {config.name} is healthy")
                else:
                    logger.warning(f"⚠️  {config.name} unhealthy (status: {response.status_code})")

                return is_healthy

        except Exception as e:
            logger.error(f"❌ Health check failed for {config.name}: {e}")
            self.health_status[config.service_type] = {
                'status': 'unhealthy',
                'last_check': datetime.now().isoformat(),
                'error': str(e),
                'service_name': config.name
            }
            return False

    async def check_all_services(self, configs: list[ServiceConfig]) -> Dict[str, bool]:
        """
        Check health of all configured services

        Args:
            configs: List of service configurations

        Returns:
            Dict mapping service_type to health status
        """
        results = {}
        for config in configs:
            results[config.service_type] = await self.check_health(config)
        return results

    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current health status of all services"""
        return self.health_status.copy()

    def get_unhealthy_services(self) -> list[str]:
        """Get list of unhealthy service types"""
        return [
            service_type
            for service_type, status in self.health_status.items()
            if status.get('status') != 'healthy'
        ]
