"""
Service Registry for Service Discovery
"""

import logging
from typing import Dict, Optional
import os

from .config import ServiceConfig

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Service registry for microservice discovery

    Manages service configurations and provides service lookup
    """

    def __init__(self, custom_configs: Optional[list[ServiceConfig]] = None):
        """
        Initialize service registry

        Args:
            custom_configs: Optional custom service configurations.
                          If not provided, loads from environment or defaults.
        """
        self.configs: Dict[str, ServiceConfig] = {}

        if custom_configs:
            for config in custom_configs:
                self.register_service(config)
        else:
            self._load_default_configs()

    def _load_default_configs(self):
        """Load default service configurations from environment"""

        # Platform services from intelligent-core
        default_services = [
            ServiceConfig(
                name='Predictive Journey',
                service_type='predictive',
                base_url=os.getenv('PREDICTIVE_URL', 'http://localhost'),
                port=int(os.getenv('PREDICTIVE_PORT', '8031'))
            ),
            ServiceConfig(
                name='Collective Agents',
                service_type='collective',
                base_url=os.getenv('COLLECTIVE_URL', 'http://localhost'),
                port=int(os.getenv('COLLECTIVE_PORT', '8032'))
            ),
            ServiceConfig(
                name='Community Intelligence',
                service_type='community_intelligence',
                base_url=os.getenv('COMMUNITY_URL', 'http://localhost'),
                port=int(os.getenv('COMMUNITY_PORT', '8030'))
            ),
            ServiceConfig(
                name='Living Documentation',
                service_type='living_docs',
                base_url=os.getenv('LIVING_DOCS_URL', 'http://localhost'),
                port=int(os.getenv('LIVING_DOCS_PORT', '8034'))
            ),
            ServiceConfig(
                name='Simulation Service',
                service_type='simulation',
                base_url=os.getenv('SIMULATION_URL', 'http://localhost'),
                port=int(os.getenv('SIMULATION_PORT', '8031'))
            ),
        ]

        for config in default_services:
            self.register_service(config)

    def register_service(self, config: ServiceConfig):
        """
        Register a service configuration

        Args:
            config: Service configuration to register
        """
        self.configs[config.service_type] = config
        logger.info(
            f" Registered service: {config.name} "
            f"({config.service_type}) at {config.get_full_url()}"
        )

    def get_service(self, service_type: str) -> ServiceConfig:
        """
        Get service configuration by type

        Args:
            service_type: Service type identifier

        Returns:
            Service configuration

        Raises:
            ValueError: If service not registered
        """
        if service_type not in self.configs:
            raise ValueError(
                f"Service '{service_type}' not registered. "
                f"Available services: {list(self.configs.keys())}"
            )
        return self.configs[service_type]

    def get_service_url(self, service_type: str) -> str:
        """
        Get full service URL

        Args:
            service_type: Service type identifier

        Returns:
            Full URL (base_url:port)
        """
        config = self.get_service(service_type)
        return config.get_full_url()

    def list_services(self) -> list[str]:
        """Get list of registered service types"""
        return list(self.configs.keys())

    def get_all_configs(self) -> list[ServiceConfig]:
        """Get all service configurations"""
        return list(self.configs.values())
