"""
Catalog Integration for Service Discovery

Integrates static Service Catalog with dynamic Service Registry
to provide unified view of all services (template + runtime).

Features:
- Load service templates from catalog
- Enrich runtime services with catalog metadata
- Detect missing services (in catalog but not running)
- Detect unknown services (running but not in catalog)
- Store unified data in PostgreSQL database
"""

import logging
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service runtime status"""
    UNKNOWN = "unknown"
    REGISTERED = "registered"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class RegistrationStatus(str, Enum):
    """Service registration status"""
    NOT_REGISTERED = "not_registered"  # In catalog but not in discovery
    REGISTERED = "registered"  # In both catalog and discovery
    UNKNOWN_SERVICE = "unknown_service"  # In discovery but not in catalog


@dataclass
class ServiceTemplate:
    """
    Service template from Service Catalog
    Static definition of what service should be
    """
    name: str
    type: str  # intelligent-core, platform-services, infrastructure/*
    business_process: str
    kpis: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    port: Optional[int] = None
    metrics_endpoint: Optional[str] = None
    health_endpoint: Optional[str] = None
    path: Optional[str] = None
    framework: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UnifiedService:
    """
    Unified service representation combining catalog template + runtime data

    This is what Admin Panel and other consumers see
    """
    # From catalog (static)
    name: str
    type: str
    business_process: str
    kpis: List[str]
    template_dependencies: List[str]
    expected_port: Optional[int]
    metrics_endpoint: Optional[str]
    health_endpoint: Optional[str]
    path: Optional[str]
    framework: Optional[str]

    # From runtime (dynamic)
    runtime_status: ServiceStatus = ServiceStatus.UNKNOWN
    registration_status: RegistrationStatus = RegistrationStatus.NOT_REGISTERED
    orchestrator: Optional[str] = None
    actual_port: Optional[int] = None
    health_status: Optional[str] = None
    last_seen: Optional[datetime] = None
    registered_at: Optional[datetime] = None
    runtime_dependencies: List[str] = field(default_factory=list)
    runtime_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)

        # Convert enums to strings
        data['runtime_status'] = self.runtime_status.value
        data['registration_status'] = self.registration_status.value

        # Convert datetime to ISO string
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        if self.registered_at:
            data['registered_at'] = self.registered_at.isoformat()

        return data

    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return (
            self.runtime_status == ServiceStatus.RUNNING and
            self.health_status == "healthy" and
            self.registration_status == RegistrationStatus.REGISTERED
        )

    def is_missing(self) -> bool:
        """Check if service is missing (should be running but isn't)"""
        return self.registration_status == RegistrationStatus.NOT_REGISTERED


class CatalogIntegration:
    """
    Integrates Service Catalog with Service Registry

    Provides unified view combining:
    - Static templates from catalog YAML
    - Runtime data from service registry
    - Historical data from database
    """

    def __init__(self, catalog_path: Optional[str] = None):
        """
        Initialize catalog integration

        Args:
            catalog_path: Path to service-catalog.yaml
        """
        self.catalog_path = catalog_path or self._find_catalog()
        self.templates: Dict[str, ServiceTemplate] = {}
        self.db_pool = None  # PostgreSQL connection pool

        logger.info(f"CatalogIntegration initialized with catalog: {self.catalog_path}")

    def _find_catalog(self) -> str:
        """Find service-catalog.yaml in standard locations"""
        possible_paths = [
            # Prefer DETAILED catalog (47 services)
            "/Users/MD/AI-Platform-ISO/infrastructure/SERVICE_CATALOG_DETAILED.yaml",
            # Fallback to compact catalog (13 services)
            "/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-catalog/service-catalog.yaml",
            Path(__file__).parent.parent / "service-catalog" / "service-catalog.yaml",
            Path(__file__).parent.parent.parent / "runtime" / "service-catalog" / "service-catalog.yaml"
        ]

        for path in possible_paths:
            if Path(path).exists():
                return str(path)

        raise FileNotFoundError("service-catalog.yaml not found in standard locations")

    async def initialize(self) -> None:
        """Initialize catalog integration"""
        logger.info("Initializing CatalogIntegration...")

        # Load catalog templates
        await self.load_catalog()

        logger.info(f"CatalogIntegration ready with {len(self.templates)} service templates")

    async def connect_database(self, db_pool) -> None:
        """
        Connect to PostgreSQL database for persistence

        Args:
            db_pool: asyncpg connection pool
        """
        self.db_pool = db_pool
        logger.info("CatalogIntegration connected to database")

        # Create tables if not exist
        await self._create_tables()

    async def load_catalog(self) -> None:
        """Load service catalog from YAML file"""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = yaml.safe_load(f)

            # Support both old and new catalog formats
            services = []

            # DETAILED format: category-based structure (47 services)
            if 'database_infrastructure' in catalog_data or 'intelligent_core' in catalog_data:
                logger.info("Loading DETAILED catalog (47 services)")

                # Process all category sections
                categories = [
                    'database_infrastructure',
                    'runtime_services',
                    'gateway_layer',
                    'observability',
                    'eventbus_core',
                    'security',
                    'ai_office',
                    'platform_services',
                    'intelligent_core'
                ]

                for category in categories:
                    if category in catalog_data:
                        category_data = catalog_data[category]
                        if isinstance(category_data, dict):
                            for name, service_data in category_data.items():
                                if isinstance(service_data, dict) and 'name' in service_data:
                                    services.append(service_data)

            # New format: platform_services + intelligent_core (13 services)
            elif 'platform_services' in catalog_data:
                logger.info("Loading compact catalog (new format with categories)")

                # Load platform services
                platform_services = catalog_data.get('platform_services', {}).get('services', [])
                services.extend(platform_services)

                # Load intelligent core services
                intelligent_core_services = catalog_data.get('intelligent_core', {}).get('services', [])
                services.extend(intelligent_core_services)

            # Old format: services array
            elif 'services' in catalog_data:
                logger.info("Loading catalog (legacy format)")
                services = catalog_data.get('services', [])

            # Process all services
            for service_data in services:
                # Extract runtime info
                runtime = service_data.get('runtime', {})
                endpoints = service_data.get('endpoints', {})
                registration = service_data.get('registration', {})

                # Extract KPI names from kpis array
                kpis_list = service_data.get('kpis', [])
                kpi_names = [kpi.get('name', '') for kpi in kpis_list if isinstance(kpi, dict)]

                # Extract dependencies
                deps = service_data.get('dependencies', {})
                dep_services = deps.get('services', []) if isinstance(deps, dict) else []
                dep_names = [dep.get('name', '') for dep in dep_services if isinstance(dep, dict)]

                # Get port from multiple possible locations
                port = None
                if isinstance(runtime, dict):
                    port = runtime.get('port')
                if port is None:
                    port = service_data.get('port')

                # Get type from registration or direct
                service_type = registration.get('type') if isinstance(registration, dict) else service_data.get('type', 'unknown')

                template = ServiceTemplate(
                    name=service_data.get('name', 'unknown'),
                    type=service_type,
                    business_process=service_data.get('business_process', 'Unknown'),
                    kpis=kpi_names,
                    dependencies=dep_names,
                    port=port,
                    metrics_endpoint=endpoints.get('metrics', '/metrics') if isinstance(endpoints, dict) else '/metrics',
                    health_endpoint=endpoints.get('health', '/health') if isinstance(endpoints, dict) else '/health',
                    path=service_data.get('_source_file'),
                    framework=runtime.get('framework', 'FastAPI') if isinstance(runtime, dict) else 'FastAPI'
                )

                self.templates[template.name] = template

            logger.info(f"Loaded {len(self.templates)} service templates from catalog")

        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            raise

    async def get_unified_service(self, service_name: str,
                                  runtime_service=None) -> Optional[UnifiedService]:
        """
        Get unified service combining catalog + runtime data

        Args:
            service_name: Name of the service
            runtime_service: Service object from ServiceRegistry (optional)

        Returns:
            UnifiedService or None
        """
        template = self.templates.get(service_name)

        # If not in catalog and not in runtime, return None
        if not template and not runtime_service:
            return None

        # If in catalog but not in runtime
        if template and not runtime_service:
            return UnifiedService(
                name=template.name,
                type=template.type,
                business_process=template.business_process,
                kpis=template.kpis,
                template_dependencies=template.dependencies,
                expected_port=template.port,
                metrics_endpoint=template.metrics_endpoint,
                health_endpoint=template.health_endpoint,
                path=template.path,
                framework=template.framework,
                runtime_status=ServiceStatus.UNKNOWN,
                registration_status=RegistrationStatus.NOT_REGISTERED
            )

        # If in runtime but not in catalog
        if runtime_service and not template:
            return UnifiedService(
                name=runtime_service.name,
                type="unknown",
                business_process="Unknown",
                kpis=[],
                template_dependencies=[],
                expected_port=None,
                metrics_endpoint=None,
                health_endpoint=None,
                path=None,
                framework=None,
                runtime_status=ServiceStatus(runtime_service.status),
                registration_status=RegistrationStatus.UNKNOWN_SERVICE,
                orchestrator=runtime_service.orchestrator,
                actual_port=runtime_service.port,
                health_status=runtime_service.health_status,
                last_seen=runtime_service.last_seen,
                registered_at=runtime_service.registered_at,
                runtime_dependencies=runtime_service.dependencies,
                runtime_metadata=runtime_service.metadata
            )

        # Both in catalog and runtime - merge data
        return UnifiedService(
            name=template.name,
            type=template.type,
            business_process=template.business_process,
            kpis=template.kpis,
            template_dependencies=template.dependencies,
            expected_port=template.port,
            metrics_endpoint=template.metrics_endpoint,
            health_endpoint=template.health_endpoint,
            path=template.path,
            framework=template.framework,
            runtime_status=ServiceStatus(runtime_service.status),
            registration_status=RegistrationStatus.REGISTERED,
            orchestrator=runtime_service.orchestrator,
            actual_port=runtime_service.port,
            health_status=runtime_service.health_status,
            last_seen=runtime_service.last_seen,
            registered_at=runtime_service.registered_at,
            runtime_dependencies=runtime_service.dependencies,
            runtime_metadata=runtime_service.metadata
        )

    async def get_all_unified_services(self, service_registry) -> List[UnifiedService]:
        """
        Get all unified services combining catalog + registry

        Args:
            service_registry: ServiceRegistry instance

        Returns:
            List of UnifiedService objects
        """
        unified_services = []

        # Track which services we've processed
        processed_names = set()

        # 1. Process all services from catalog
        for template_name in self.templates:
            runtime_service = await service_registry.get_service(template_name)
            unified = await self.get_unified_service(template_name, runtime_service)
            if unified:
                unified_services.append(unified)
                processed_names.add(template_name)

        # 2. Process runtime services not in catalog
        runtime_services = await service_registry.list_services()
        for runtime_service in runtime_services:
            if runtime_service.name not in processed_names:
                unified = await self.get_unified_service(
                    runtime_service.name,
                    runtime_service
                )
                if unified:
                    unified_services.append(unified)

        return unified_services

    async def get_missing_services(self, service_registry) -> List[UnifiedService]:
        """
        Get services that are in catalog but not registered in discovery

        Returns:
            List of missing UnifiedService objects
        """
        all_services = await self.get_all_unified_services(service_registry)
        return [s for s in all_services if s.is_missing()]

    async def get_unknown_services(self, service_registry) -> List[UnifiedService]:
        """
        Get services that are registered but not in catalog

        Returns:
            List of unknown UnifiedService objects
        """
        all_services = await self.get_all_unified_services(service_registry)
        return [
            s for s in all_services
            if s.registration_status == RegistrationStatus.UNKNOWN_SERVICE
        ]

    async def get_healthy_services(self, service_registry) -> List[UnifiedService]:
        """Get all healthy services"""
        all_services = await self.get_all_unified_services(service_registry)
        return [s for s in all_services if s.is_healthy()]

    async def get_catalog_stats(self, service_registry) -> Dict[str, Any]:
        """
        Get catalog statistics

        Returns:
            Dictionary with stats
        """
        all_services = await self.get_all_unified_services(service_registry)

        total = len(self.templates)
        registered = len([s for s in all_services if s.registration_status == RegistrationStatus.REGISTERED])
        missing = len([s for s in all_services if s.is_missing()])
        unknown = len([s for s in all_services if s.registration_status == RegistrationStatus.UNKNOWN_SERVICE])
        healthy = len([s for s in all_services if s.is_healthy()])

        # Group by type
        by_type = {}
        for service in all_services:
            by_type[service.type] = by_type.get(service.type, 0) + 1

        # Group by business process
        by_process = {}
        for service in all_services:
            by_process[service.business_process] = by_process.get(service.business_process, 0) + 1

        return {
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'catalog_version': '1.0.0'
            },
            'totals': {
                'total_services': total,
                'registered_services': registered,
                'missing_services': missing,
                'unknown_services': unknown,
                'healthy_services': healthy,
                'coverage_percent': round((registered / total * 100) if total > 0 else 0, 1)
            },
            'by_type': by_type,
            'by_business_process': by_process,
            'services': {
                'registered': [s.name for s in all_services if s.registration_status == RegistrationStatus.REGISTERED],
                'missing': [s.name for s in all_services if s.is_missing()],
                'unknown': [s.name for s in all_services if s.registration_status == RegistrationStatus.UNKNOWN_SERVICE]
            }
        }

    async def _create_tables(self) -> None:
        """Create database tables for unified registry"""
        if not self.db_pool:
            return

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS unified_service_registry (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(255) UNIQUE NOT NULL,

            -- From catalog (static)
            service_type VARCHAR(100),
            business_process VARCHAR(255),
            kpis JSONB,
            template_dependencies JSONB,
            expected_port INTEGER,
            metrics_endpoint TEXT,
            health_endpoint TEXT,
            service_path TEXT,
            framework VARCHAR(100),

            -- From runtime (dynamic)
            runtime_status VARCHAR(50),
            registration_status VARCHAR(50),
            orchestrator VARCHAR(100),
            actual_port INTEGER,
            health_status VARCHAR(50),
            last_seen TIMESTAMP,
            registered_at TIMESTAMP,
            runtime_dependencies JSONB,
            runtime_metadata JSONB,

            -- Audit
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_service_name ON unified_service_registry(service_name);
        CREATE INDEX IF NOT EXISTS idx_runtime_status ON unified_service_registry(runtime_status);
        CREATE INDEX IF NOT EXISTS idx_registration_status ON unified_service_registry(registration_status);
        CREATE INDEX IF NOT EXISTS idx_business_process ON unified_service_registry(business_process);
        """

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(create_table_sql)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")

    async def save_to_database(self, unified_service: UnifiedService) -> None:
        """
        Save unified service to database

        Args:
            unified_service: UnifiedService to save
        """
        if not self.db_pool:
            return

        upsert_sql = """
        INSERT INTO unified_service_registry (
            service_name, service_type, business_process, kpis,
            template_dependencies, expected_port, metrics_endpoint, health_endpoint,
            service_path, framework, runtime_status, registration_status,
            orchestrator, actual_port, health_status, last_seen, registered_at,
            runtime_dependencies, runtime_metadata, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, NOW()
        )
        ON CONFLICT (service_name) DO UPDATE SET
            service_type = EXCLUDED.service_type,
            business_process = EXCLUDED.business_process,
            runtime_status = EXCLUDED.runtime_status,
            registration_status = EXCLUDED.registration_status,
            orchestrator = EXCLUDED.orchestrator,
            actual_port = EXCLUDED.actual_port,
            health_status = EXCLUDED.health_status,
            last_seen = EXCLUDED.last_seen,
            runtime_dependencies = EXCLUDED.runtime_dependencies,
            runtime_metadata = EXCLUDED.runtime_metadata,
            updated_at = NOW()
        """

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    upsert_sql,
                    unified_service.name,
                    unified_service.type,
                    unified_service.business_process,
                    json.dumps(unified_service.kpis),
                    json.dumps(unified_service.template_dependencies),
                    unified_service.expected_port,
                    unified_service.metrics_endpoint,
                    unified_service.health_endpoint,
                    unified_service.path,
                    unified_service.framework,
                    unified_service.runtime_status.value,
                    unified_service.registration_status.value,
                    unified_service.orchestrator,
                    unified_service.actual_port,
                    unified_service.health_status,
                    unified_service.last_seen,
                    unified_service.registered_at,
                    json.dumps(unified_service.runtime_dependencies),
                    json.dumps(unified_service.runtime_metadata)
                )
            logger.debug(f"Saved {unified_service.name} to database")
        except Exception as e:
            logger.error(f"Failed to save {unified_service.name} to database: {e}")

    async def load_from_database(self, service_name: str) -> Optional[UnifiedService]:
        """
        Load unified service from database

        Args:
            service_name: Name of service to load

        Returns:
            UnifiedService or None
        """
        if not self.db_pool:
            return None

        select_sql = """
        SELECT * FROM unified_service_registry WHERE service_name = $1
        """

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(select_sql, service_name)

                if not row:
                    return None

                return UnifiedService(
                    name=row['service_name'],
                    type=row['service_type'],
                    business_process=row['business_process'],
                    kpis=json.loads(row['kpis']) if row['kpis'] else [],
                    template_dependencies=json.loads(row['template_dependencies']) if row['template_dependencies'] else [],
                    expected_port=row['expected_port'],
                    metrics_endpoint=row['metrics_endpoint'],
                    health_endpoint=row['health_endpoint'],
                    path=row['service_path'],
                    framework=row['framework'],
                    runtime_status=ServiceStatus(row['runtime_status']),
                    registration_status=RegistrationStatus(row['registration_status']),
                    orchestrator=row['orchestrator'],
                    actual_port=row['actual_port'],
                    health_status=row['health_status'],
                    last_seen=row['last_seen'],
                    registered_at=row['registered_at'],
                    runtime_dependencies=json.loads(row['runtime_dependencies']) if row['runtime_dependencies'] else [],
                    runtime_metadata=json.loads(row['runtime_metadata']) if row['runtime_metadata'] else {}
                )
        except Exception as e:
            logger.error(f"Failed to load {service_name} from database: {e}")
            return None
