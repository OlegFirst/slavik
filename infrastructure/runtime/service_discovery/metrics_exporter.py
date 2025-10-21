"""
Service Catalog Metrics Exporter for Prometheus

Exports service catalog statistics and health metrics to Prometheus.
"""

from prometheus_client import Gauge, Counter, Info, Histogram
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


# ============================================
# CATALOG STATISTICS METRICS
# ============================================

catalog_total_services = Gauge(
    'service_catalog_total_services',
    'Total number of services in catalog'
)

catalog_registered_services = Gauge(
    'service_catalog_registered_services',
    'Number of registered (running) services'
)

catalog_missing_services = Gauge(
    'service_catalog_missing_services',
    'Number of missing services (in catalog but not running)'
)

catalog_unknown_services = Gauge(
    'service_catalog_unknown_services',
    'Number of unknown services (running but not in catalog)'
)

catalog_coverage_percent = Gauge(
    'service_catalog_coverage_percent',
    'Percentage of catalog services that are running'
)

catalog_healthy_services = Gauge(
    'service_catalog_healthy_services',
    'Number of healthy services'
)

# ============================================
# SERVICES BY CATEGORY METRICS
# ============================================

catalog_services_by_type = Gauge(
    'service_catalog_services_by_type',
    'Number of services by type',
    ['type']
)

catalog_services_by_status = Gauge(
    'service_catalog_services_by_status',
    'Number of services by status (active/configured/deprecated/archived)',
    ['status']
)

catalog_services_by_business_process = Gauge(
    'service_catalog_services_by_business_process',
    'Number of services by business process',
    ['business_process']
)

# ============================================
# SERVICE HEALTH METRICS
# ============================================

service_health_status = Gauge(
    'service_health_status',
    'Health status of each service (1=healthy, 0.5=degraded, 0=unhealthy)',
    ['service_name', 'type', 'port']
)

service_registration_status = Gauge(
    'service_registration_status',
    'Registration status of service (1=registered, 0=not_registered)',
    ['service_name', 'type']
)

service_uptime_seconds = Gauge(
    'service_uptime_seconds',
    'Service uptime in seconds',
    ['service_name']
)

# ============================================
# CATALOG METADATA
# ============================================

catalog_info = Info(
    'service_catalog_info',
    'Service catalog metadata'
)

catalog_version_info = Info(
    'service_catalog_version',
    'Service catalog version information'
)

# ============================================
# OPERATIONS METRICS
# ============================================

catalog_export_total = Counter(
    'service_catalog_export_total',
    'Total number of catalog exports to Prometheus'
)

catalog_export_errors = Counter(
    'service_catalog_export_errors',
    'Total number of catalog export errors'
)

catalog_export_duration_seconds = Histogram(
    'service_catalog_export_duration_seconds',
    'Duration of catalog export in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)


# ============================================
# EXPORT FUNCTION
# ============================================

async def export_catalog_metrics(
    catalog_integration: Any,
    service_registry: Any = None
) -> None:
    """
    Export service catalog metrics to Prometheus.

    Args:
        catalog_integration: CatalogIntegration instance
        service_registry: ServiceRegistry instance (optional)
    """
    import time
    start_time = time.time()

    try:
        # Get catalog statistics
        stats = await catalog_integration.get_stats()
        totals = stats.get('totals', {})
        by_type = stats.get('by_type', {})
        by_status = stats.get('by_status', {})
        by_business_process = stats.get('by_business_process', {})
        metadata = stats.get('metadata', {})

        # ============================================
        # UPDATE CATALOG TOTALS
        # ============================================

        catalog_total_services.set(totals.get('total_services', 0))
        catalog_registered_services.set(totals.get('registered_services', 0))
        catalog_missing_services.set(totals.get('missing_services', 0))
        catalog_unknown_services.set(totals.get('unknown_services', 0))
        catalog_coverage_percent.set(totals.get('coverage_percent', 0))
        catalog_healthy_services.set(totals.get('healthy_services', 0))

        logger.debug(
            f"Exported catalog totals: {totals.get('total_services')} total, "
            f"{totals.get('registered_services')} registered, "
            f"{totals.get('coverage_percent')}% coverage"
        )

        # ============================================
        # UPDATE BY TYPE METRICS
        # ============================================

        for type_name, count in by_type.items():
            catalog_services_by_type.labels(type=type_name).set(count)

        # ============================================
        # UPDATE BY STATUS METRICS
        # ============================================

        for status, count in by_status.items():
            catalog_services_by_status.labels(status=status).set(count)

        # ============================================
        # UPDATE BY BUSINESS PROCESS METRICS
        # ============================================

        for business_process, count in by_business_process.items():
            # Truncate long business process names for label
            bp_label = business_process[:50] if len(business_process) > 50 else business_process
            catalog_services_by_business_process.labels(
                business_process=bp_label
            ).set(count)

        # ============================================
        # UPDATE SERVICE HEALTH METRICS
        # ============================================

        services = await catalog_integration.get_unified_services()

        for service in services:
            service_name = service.get('name', 'unknown')
            service_type = service.get('type', 'unknown')
            service_port = service.get('expected_port') or service.get('actual_port') or 0

            # Health status (1=healthy, 0.5=degraded, 0=unhealthy)
            health = service.get('health_status', 'unknown')
            health_value = {
                'healthy': 1.0,
                'degraded': 0.5,
                'unhealthy': 0.0,
                'unknown': -1.0
            }.get(health, -1.0)

            service_health_status.labels(
                service_name=service_name,
                type=service_type,
                port=str(service_port)
            ).set(health_value)

            # Registration status (1=registered, 0=not_registered)
            registration = service.get('registration_status', 'not_registered')
            registration_value = 1.0 if registration == 'registered' else 0.0

            service_registration_status.labels(
                service_name=service_name,
                type=service_type
            ).set(registration_value)

            # Uptime (if available from service registry)
            if service_registry and registration == 'registered':
                try:
                    service_data = await service_registry.get_service(service_name)
                    if service_data:
                        uptime = service_data.get('uptime_seconds', 0)
                        service_uptime_seconds.labels(
                            service_name=service_name
                        ).set(uptime)
                except Exception as e:
                    logger.debug(f"Could not get uptime for {service_name}: {e}")

        # ============================================
        # UPDATE CATALOG METADATA
        # ============================================

        catalog_info.info({
            'platform_name': metadata.get('platform_name', 'AI-Platform-ISO'),
            'schema_version': metadata.get('schema_version', '1.0.0'),
            'auto_generated': str(metadata.get('auto_generated', False)),
            'last_updated': metadata.get('generated_at', 'unknown')
        })

        catalog_version_info.info({
            'version': metadata.get('version', '2.0.0'),
            'total_services': str(metadata.get('total_services', 0))
        })

        # ============================================
        # RECORD SUCCESS
        # ============================================

        duration = time.time() - start_time
        catalog_export_duration_seconds.observe(duration)
        catalog_export_total.inc()

        logger.info(
            f" Successfully exported catalog metrics to Prometheus "
            f"({totals.get('total_services')} services, {duration:.2f}s)"
        )

    except Exception as e:
        catalog_export_errors.inc()
        logger.error(f" Failed to export catalog metrics: {e}", exc_info=True)
        raise


async def export_catalog_events_metrics(eventbus_integration: Any) -> None:
    """
    Export event broadcasting metrics (if needed).

    Args:
        eventbus_integration: EventBusIntegration instance
    """
    # TODO: Add event-specific metrics if needed
    # For example: events published, events consumed, etc.
    pass


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_all_metrics() -> Dict[str, Any]:
    """Get all current metric values for debugging."""
    from prometheus_client import REGISTRY

    metrics = {}
    for collector in REGISTRY._collector_to_names:
        for name in REGISTRY._collector_to_names[collector]:
            try:
                metric = REGISTRY._names_to_collectors[name]
                metrics[name] = metric
            except Exception:
                pass

    return metrics


def reset_all_metrics() -> None:
    """Reset all catalog metrics (for testing)."""
    # Note: Prometheus metrics can't be truly reset,
    # but we can set them to 0 or remove labels

    catalog_total_services.set(0)
    catalog_registered_services.set(0)
    catalog_missing_services.set(0)
    catalog_unknown_services.set(0)
    catalog_coverage_percent.set(0)
    catalog_healthy_services.set(0)

    logger.info("Reset all catalog metrics to 0")


if __name__ == "__main__":
    # Test metrics export
    import asyncio

    async def test_metrics():
        """Test metrics export with mock data."""
        from unittest.mock import AsyncMock, MagicMock

        # Mock catalog integration
        mock_catalog = AsyncMock()
        mock_catalog.get_stats.return_value = {
            'totals': {
                'total_services': 27,
                'registered_services': 20,
                'missing_services': 7,
                'unknown_services': 2,
                'coverage_percent': 74.07,
                'healthy_services': 18
            },
            'by_type': {
                'infrastructure/AI-office-infrastructure': 9,
                'intelligent-core': 8,
                'platform-services': 6,
                'interface': 4
            },
            'by_status': {
                'active': 25,
                'configured': 2
            },
            'by_business_process': {
                'Monitoring & Observability': 3,
                'Workflow Orchestration': 5,
                'Business Continuity Planning': 6
            },
            'metadata': {
                'platform_name': 'AI-Platform-ISO',
                'version': '2.0.0',
                'total_services': 27,
                'schema_version': '1.0.0',
                'generated_at': '2025-10-11T03:00:00Z',
                'auto_generated': True
            }
        }

        mock_catalog.get_unified_services.return_value = [
            {
                'name': 'mio-manager',
                'type': 'infrastructure/AI-office-infrastructure',
                'expected_port': 8046,
                'health_status': 'healthy',
                'registration_status': 'registered'
            },
            {
                'name': 'service-discovery',
                'type': 'infrastructure/runtime',
                'expected_port': 8500,
                'health_status': 'healthy',
                'registration_status': 'registered'
            }
        ]

        # Export metrics
        await export_catalog_metrics(mock_catalog)

        print(" Test metrics export complete")
        print("\nMetrics that would be exposed:")
        print(f"  service_catalog_total_services = 27")
        print(f"  service_catalog_registered_services = 20")
        print(f"  service_catalog_coverage_percent = 74.07")
        print(f"  service_catalog_services_by_type{{type='infrastructure/AI-office-infrastructure'}} = 9")
        print(f"  service_health_status{{service_name='mio-manager', type='infrastructure/AI-office-infrastructure', port='8046'}} = 1.0")

    asyncio.run(test_metrics())
