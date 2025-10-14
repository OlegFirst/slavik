"""
Service Catalog Adapter
Парсинг SERVICE_CATALOG_DETAILED.yaml для генерации сценариев
"""

import yaml
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration
CATALOG_PATH = "/Users/MD/AI-Platform-ISO/infrastructure/SERVICE_CATALOG_DETAILED.yaml"


class CatalogAdapter:
    """
    Adapter для чтения и парсинга SERVICE_CATALOG_DETAILED.yaml

    Извлекает информацию о сервисах для автогенерации L1-L3 сценариев
    """

    def __init__(self, catalog_path: str = CATALOG_PATH):
        self.catalog_path = catalog_path
        self.catalog_data: Optional[Dict[str, Any]] = None
        self.services: List[Dict[str, Any]] = []
        self.subsystems: Dict[str, List[str]] = {}

    async def load_catalog(self) -> Dict[str, Any]:
        """
        Load and parse service catalog

        Returns:
            Parsed catalog data
        """
        try:
            logger.info(f"Loading service catalog from: {self.catalog_path}")

            with open(self.catalog_path, 'r') as f:
                self.catalog_data = yaml.safe_load(f)

            logger.info(f"✅ Catalog loaded: {self.catalog_data.get('total_services', 0)} services")

            # Parse services
            self._parse_services()

            # Parse subsystems
            self._parse_subsystems()

            return self.catalog_data

        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            raise

    def _parse_services(self):
        """Parse all services from catalog"""
        self.services = []

        if not self.catalog_data:
            return

        # Parse different sections
        sections = [
            'database_infrastructure',
            'cache_infrastructure',
            'message_infrastructure',
            'gateway_services',
            'platform_services',
            'intelligent_core',
            'ai_office_infrastructure',
            'infrastructure_services'
        ]

        for section in sections:
            section_data = self.catalog_data.get(section, {})

            if isinstance(section_data, dict):
                for service_name, service_data in section_data.items():
                    if isinstance(service_data, dict):
                        service = self._normalize_service(service_name, service_data, section)
                        self.services.append(service)

        logger.info(f"✅ Parsed {len(self.services)} services")

    def _normalize_service(self, name: str, data: Dict[str, Any], section: str) -> Dict[str, Any]:
        """Normalize service data to consistent format"""
        return {
            "name": name,
            "display_name": data.get("display_name", name),
            "section": section,
            "description": data.get("description", ""),
            "capabilities": data.get("capabilities", []),
            "features": data.get("features", []),
            "port": data.get("runtime", {}).get("port"),
            "protocol": data.get("runtime", {}).get("protocol", "HTTP"),
            "dependencies": data.get("dependencies", {}).get("required", []),
            "optional_dependencies": data.get("dependencies", {}).get("optional", []),
            "integrations": data.get("integrations", []),
            "kpis": data.get("kpis", []),
            "eventbus": data.get("eventbus", {}),
            "status": data.get("registration", {}).get("status", "active"),
            "environment": data.get("registration", {}).get("environment", "development"),
            "known_issues": data.get("known_issues", {}),
            "limitations": data.get("limitations", [])
        }

    def _parse_subsystems(self):
        """Parse subsystems (groups of related services)"""
        self.subsystems = {}

        # Group by section
        for service in self.services:
            section = service["section"]
            if section not in self.subsystems:
                self.subsystems[section] = []

            self.subsystems[section].append(service["name"])

        logger.info(f"✅ Identified {len(self.subsystems)} subsystems")

    async def load_services(self) -> List[Dict[str, Any]]:
        """
        Load all services

        Returns:
            List of normalized service dicts
        """
        if not self.services:
            await self.load_catalog()

        return self.services

    async def get_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific service by name"""
        if not self.services:
            await self.load_catalog()

        for service in self.services:
            if service["name"] == name:
                return service

        return None

    async def get_services_by_subsystem(self, subsystem: str) -> List[Dict[str, Any]]:
        """Get all services in a subsystem"""
        if not self.services:
            await self.load_catalog()

        return [s for s in self.services if s["section"] == subsystem]

    async def get_subsystems(self) -> Dict[str, List[str]]:
        """Get all subsystems with their services"""
        if not self.subsystems:
            await self.load_catalog()

        return self.subsystems

    async def get_service_dependencies(self, service_name: str) -> Dict[str, List[str]]:
        """
        Get dependencies for a service

        Returns:
            {
                "required": ["service1", "service2"],
                "optional": ["service3"]
            }
        """
        service = await self.get_service(service_name)

        if not service:
            return {"required": [], "optional": []}

        return {
            "required": service.get("dependencies", []),
            "optional": service.get("optional_dependencies", [])
        }

    async def get_dependent_services(self, service_name: str) -> List[str]:
        """
        Get services that depend on this service

        Args:
            service_name: Service to check

        Returns:
            List of service names that depend on this service
        """
        if not self.services:
            await self.load_catalog()

        dependents = []

        for service in self.services:
            all_deps = service.get("dependencies", []) + service.get("optional_dependencies", [])

            if service_name in all_deps:
                dependents.append(service["name"])

        return dependents

    async def get_integration_pairs(self) -> List[Dict[str, str]]:
        """
        Get all service integration pairs

        Returns:
            [
                {"service_a": "bia-service", "service_b": "audit-service"},
                ...
            ]
        """
        if not self.services:
            await self.load_catalog()

        pairs = []

        for service in self.services:
            service_name = service["name"]

            # Get dependencies
            deps = service.get("dependencies", [])

            for dep in deps:
                pairs.append({
                    "service_a": service_name,
                    "service_b": dep,
                    "type": "dependency"
                })

            # Get integrations
            integrations = service.get("integrations", [])

            for integration in integrations:
                if isinstance(integration, dict):
                    integrated_service = integration.get("service")
                    if integrated_service:
                        pairs.append({
                            "service_a": service_name,
                            "service_b": integrated_service,
                            "type": integration.get("integration_type", "integration")
                        })

        return pairs

    async def get_catalog_stats(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        if not self.catalog_data:
            await self.load_catalog()

        return {
            "total_services": len(self.services),
            "subsystems": len(self.subsystems),
            "active_services": len([s for s in self.services if s["status"] == "active"]),
            "deprecated_services": len([s for s in self.services if s["status"] == "deprecated"]),
            "services_with_kpis": len([s for s in self.services if s.get("kpis")]),
            "services_with_eventbus": len([s for s in self.services if s.get("eventbus")]),
            "subsystem_breakdown": {
                name: len(services) for name, services in self.subsystems.items()
            }
        }


# Global instance
_catalog_adapter: Optional[CatalogAdapter] = None


def get_catalog_adapter() -> CatalogAdapter:
    """Get or create global catalog adapter"""
    global _catalog_adapter

    if _catalog_adapter is None:
        _catalog_adapter = CatalogAdapter()

    return _catalog_adapter
