"""
Plugin Manager for Data Collectors

Manages dynamic loading, registration, and execution of data collectors
"""

import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
from enum import Enum

from core.models.base import DataSourceType, Organization

logger = logging.getLogger(__name__)


# ============================================
# COLLECTOR REGISTRY
# ============================================

class CollectorStatus(str, Enum):
    """Collector status"""
    AVAILABLE = "available"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class CollectorInfo:
    """Information about a collector"""

    def __init__(
        self,
        source_type: DataSourceType,
        collector_class: Type,
        name: str,
        description: str,
        version: str,
        capabilities: List[str],
        required_credentials: List[str]
    ):
        self.source_type = source_type
        self.collector_class = collector_class
        self.name = name
        self.description = description
        self.version = version
        self.capabilities = capabilities
        self.required_credentials = required_credentials
        self.status = CollectorStatus.AVAILABLE
        self.registered_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'source_type': self.source_type.value,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'capabilities': self.capabilities,
            'required_credentials': self.required_credentials,
            'status': self.status.value,
            'registered_at': self.registered_at.isoformat()
        }


# ============================================
# PLUGIN MANAGER
# ============================================

class CollectorManager:
    """
    Plugin Manager for Data Collectors

    Manages registration, discovery, and execution of data collectors
    """

    def __init__(self):
        """Initialize collector manager"""
        self._collectors: Dict[DataSourceType, CollectorInfo] = {}
        self._instances: Dict[str, Any] = {}  # Active collector instances

        logger.info("Collector Manager initialized")

    def register_collector(
        self,
        source_type: DataSourceType,
        collector_class: Type,
        name: str,
        description: str,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
        required_credentials: Optional[List[str]] = None
    ) -> None:
        """
        Register a collector

        Args:
            source_type: Data source type
            collector_class: Collector class
            name: Collector name
            description: Collector description
            version: Version string
            capabilities: List of capabilities
            required_credentials: Required credential fields
        """
        if source_type in self._collectors:
            logger.warning(f"Collector for {source_type.value} already registered, overwriting")

        collector_info = CollectorInfo(
            source_type=source_type,
            collector_class=collector_class,
            name=name,
            description=description,
            version=version,
            capabilities=capabilities or [],
            required_credentials=required_credentials or []
        )

        self._collectors[source_type] = collector_info

        logger.info(f"Registered collector: {name} ({source_type.value}) v{version}")

    def get_collector(
        self,
        source_type: DataSourceType,
        credentials: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Get collector instance

        Args:
            source_type: Data source type
            credentials: Collector credentials

        Returns:
            Collector instance

        Raises:
            ValueError: If collector not found or credentials invalid
        """
        if source_type not in self._collectors:
            raise ValueError(f"Collector not found for source type: {source_type.value}")

        collector_info = self._collectors[source_type]

        # Check credentials
        if credentials:
            missing = [
                cred for cred in collector_info.required_credentials
                if cred not in credentials
            ]
            if missing:
                raise ValueError(
                    f"Missing required credentials for {source_type.value}: {', '.join(missing)}"
                )

        # Create instance key
        instance_key = f"{source_type.value}_{id(credentials) if credentials else 'default'}"

        # Return existing instance or create new one
        if instance_key not in self._instances:
            logger.info(f"Creating new collector instance: {collector_info.name}")

            # Instantiate collector
            if credentials:
                instance = collector_info.collector_class(credentials=credentials)
            else:
                instance = collector_info.collector_class()

            self._instances[instance_key] = instance

        return self._instances[instance_key]

    def list_collectors(
        self,
        status: Optional[CollectorStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        List registered collectors

        Args:
            status: Optional filter by status

        Returns:
            List of collector information
        """
        collectors = []

        for collector_info in self._collectors.values():
            if status is None or collector_info.status == status:
                collectors.append(collector_info.to_dict())

        return collectors

    def get_collector_info(
        self,
        source_type: DataSourceType
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about specific collector

        Args:
            source_type: Data source type

        Returns:
            Collector information or None
        """
        if source_type in self._collectors:
            return self._collectors[source_type].to_dict()
        return None

    def is_collector_available(
        self,
        source_type: DataSourceType
    ) -> bool:
        """
        Check if collector is available

        Args:
            source_type: Data source type

        Returns:
            True if available
        """
        return (
            source_type in self._collectors and
            self._collectors[source_type].status == CollectorStatus.AVAILABLE
        )

    def disable_collector(
        self,
        source_type: DataSourceType
    ) -> None:
        """
        Disable a collector

        Args:
            source_type: Data source type
        """
        if source_type in self._collectors:
            self._collectors[source_type].status = CollectorStatus.DISABLED
            logger.info(f"Disabled collector: {source_type.value}")

    def enable_collector(
        self,
        source_type: DataSourceType
    ) -> None:
        """
        Enable a collector

        Args:
            source_type: Data source type
        """
        if source_type in self._collectors:
            self._collectors[source_type].status = CollectorStatus.AVAILABLE
            logger.info(f"Enabled collector: {source_type.value}")

    async def collect_from_source(
        self,
        source_type: DataSourceType,
        entity_types: List[str],
        credentials: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect data from source

        Args:
            source_type: Data source type
            entity_types: List of entity types to collect
            credentials: Collector credentials
            filters: Optional filters

        Returns:
            Dictionary of collected data by entity type
        """
        logger.info(f"Collecting from {source_type.value}: {entity_types}")

        # Get collector instance
        collector = self.get_collector(source_type, credentials)

        # Collect data
        results = {}

        for entity_type in entity_types:
            try:
                data = await collector.collect(entity_type, filters=filters)
                results[entity_type] = data
                logger.info(
                    f"Collected {len(data)} {entity_type} records from {source_type.value}"
                )
            except Exception as e:
                logger.error(
                    f"Error collecting {entity_type} from {source_type.value}: {e}",
                    exc_info=True
                )
                results[entity_type] = []

        return results

    async def collect_for_organization(
        self,
        organization: Organization,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Collect data for organization from all connected sources

        Args:
            organization: Organization digital twin
            entity_types: Optional list of entity types (default: all)

        Returns:
            Nested dictionary: {source_type: {entity_type: [data]}}
        """
        logger.info(
            f"Collecting data for organization: {organization.name} "
            f"({len(organization.sources)} sources)"
        )

        if entity_types is None:
            entity_types = [
                'companies', 'contacts', 'leads', 'opportunities',
                'accounts', 'invoices', 'projects', 'tasks'
            ]

        all_results = {}

        for source in organization.sources:
            source_type = source.source_type

            if not self.is_collector_available(source_type):
                logger.warning(f"Collector not available: {source_type.value}")
                continue

            try:
                # Get credentials from organization metadata or source metadata
                credentials = source.metadata.get('credentials', {})

                # Collect data
                results = await self.collect_from_source(
                    source_type,
                    entity_types,
                    credentials=credentials if credentials else None
                )

                all_results[source_type.value] = results

            except Exception as e:
                logger.error(
                    f"Error collecting from {source_type.value} for {organization.name}: {e}",
                    exc_info=True
                )
                all_results[source_type.value] = {}

        total_records = sum(
            len(records)
            for source_data in all_results.values()
            for records in source_data.values()
        )

        logger.info(
            f"Collection complete for {organization.name}: "
            f"{total_records} total records from {len(all_results)} sources"
        )

        return all_results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get manager statistics

        Returns:
            Statistics dictionary
        """
        return {
            'total_collectors': len(self._collectors),
            'available': sum(
                1 for c in self._collectors.values()
                if c.status == CollectorStatus.AVAILABLE
            ),
            'disabled': sum(
                1 for c in self._collectors.values()
                if c.status == CollectorStatus.DISABLED
            ),
            'active_instances': len(self._instances),
            'collectors_by_type': {
                source_type.value: info.name
                for source_type, info in self._collectors.items()
            }
        }

    def clear_instances(self) -> None:
        """Clear all collector instances (force re-instantiation)"""
        self._instances.clear()
        logger.info("Cleared all collector instances")


# ============================================
# GLOBAL MANAGER INSTANCE
# ============================================

# Global collector manager (singleton pattern)
_global_manager: Optional[CollectorManager] = None


def get_collector_manager() -> CollectorManager:
    """
    Get global collector manager instance

    Returns:
        CollectorManager instance
    """
    global _global_manager

    if _global_manager is None:
        _global_manager = CollectorManager()

    return _global_manager


def register_builtin_collectors() -> None:
    """
    Register all built-in collectors

    This should be called at application startup
    """
    manager = get_collector_manager()

    logger.info("Registering built-in collectors...")

    # Import and register collectors
    try:
        from collectors.builtin.odoo_collector import OdooCollector
        manager.register_collector(
            DataSourceType.ODOO,
            OdooCollector,
            "Odoo Collector",
            "Collects data from Odoo ERP system",
            version="1.0.0",
            capabilities=['companies', 'contacts', 'projects', 'invoices'],
            required_credentials=['url', 'db', 'username', 'password']
        )
    except ImportError:
        logger.warning("OdooCollector not available")

    try:
        from collectors.builtin.salesforce_collector import SalesforceCollector
        manager.register_collector(
            DataSourceType.SALESFORCE,
            SalesforceCollector,
            "Salesforce Collector",
            "Collects data from Salesforce CRM",
            version="1.0.0",
            capabilities=['accounts', 'contacts', 'leads', 'opportunities'],
            required_credentials=['username', 'password', 'security_token']
        )
    except ImportError:
        logger.warning("SalesforceCollector not available")

    try:
        from collectors.builtin.hubspot_collector import HubSpotCollector
        manager.register_collector(
            DataSourceType.HUBSPOT,
            HubSpotCollector,
            "HubSpot Collector",
            "Collects data from HubSpot CRM",
            version="1.0.0",
            capabilities=['companies', 'contacts', 'deals'],
            required_credentials=['api_key']
        )
    except ImportError:
        logger.warning("HubSpotCollector not available")

    try:
        from collectors.builtin.generic_rest_collector import GenericRESTCollector
        manager.register_collector(
            DataSourceType.CUSTOM,
            GenericRESTCollector,
            "Generic REST Collector",
            "Collects data from generic REST APIs",
            version="1.0.0",
            capabilities=['any'],
            required_credentials=['base_url']
        )
    except ImportError:
        logger.warning("GenericRESTCollector not available")

    logger.info(f"Registered {len(manager.list_collectors())} collectors")
