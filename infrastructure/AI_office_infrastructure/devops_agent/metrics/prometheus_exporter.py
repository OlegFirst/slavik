#!/usr/bin/env python3
"""
Prometheus Metrics Exporter for DevOps Agent

Exports infrastructure metrics to Prometheus Pushgateway:
- Event architecture gaps
- Container status
- Deployment health
- Port conflicts
- Auto-fix statistics
"""

import logging
from typing import Dict, Any
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    push_to_gateway,
    delete_from_gateway
)
import os

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """
    Prometheus metrics exporter for DevOps Agent

    Pushes metrics to Prometheus Pushgateway
    """

    def __init__(self, pushgateway_url: str = None):
        """
        Initialize Prometheus exporter

        Args:
            pushgateway_url: Pushgateway URL (default from env or localhost:9091)
        """
        self.pushgateway_url = pushgateway_url or os.getenv(
            'PROMETHEUS_PUSHGATEWAY',
            'localhost:9091'
        )
        self.job_name = 'devops_agent'

        # Create dedicated registry
        self.registry = CollectorRegistry()

        # ===== COUNTERS (monotonically increasing) =====

        self.scans_total = Counter(
            'devops_scans_total',
            'Total infrastructure scans performed',
            ['scan_type'],
            registry=self.registry
        )

        self.fixes_applied_total = Counter(
            'devops_fixes_applied_total',
            'Total fixes applied',
            ['category', 'success'],
            registry=self.registry
        )

        self.dockerfiles_generated_total = Counter(
            'devops_dockerfiles_generated_total',
            'Total Dockerfiles generated',
            ['language', 'success'],
            registry=self.registry
        )

        # ===== GAUGES (current values) =====

        self.issues_detected = Gauge(
            'devops_issues_detected',
            'Current infrastructure issues detected',
            ['category', 'severity'],
            registry=self.registry
        )

        self.event_gaps = Gauge(
            'devops_event_gaps_total',
            'Total event architecture gaps',
            ['severity'],
            registry=self.registry
        )

        self.port_conflicts = Gauge(
            'devops_port_conflicts',
            'Number of port conflicts',
            registry=self.registry
        )

        self.services_without_dockerfile = Gauge(
            'devops_services_without_dockerfile',
            'Number of services missing Dockerfile',
            registry=self.registry
        )

        self.service_health = Gauge(
            'devops_service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service_name'],
            registry=self.registry
        )

        # ===== HISTOGRAMS (distributions) =====

        self.scan_duration_seconds = Histogram(
            'devops_scan_duration_seconds',
            'Time spent scanning infrastructure',
            ['scan_type'],
            registry=self.registry
        )

        self.fix_duration_seconds = Histogram(
            'devops_fix_duration_seconds',
            'Time spent applying fixes',
            ['category'],
            registry=self.registry
        )

        logger.info(f" Prometheus exporter initialized: {self.pushgateway_url}")

    def export_scan_metrics(self, scan_results: Dict[str, Any]):
        """
        Export scan results to Prometheus

        Args:
            scan_results: Scan results from DevOps Agent
        """
        try:
            scan_type = scan_results.get('scan_type', 'unknown')

            # Increment scan counter
            self.scans_total.labels(scan_type=scan_type).inc()

            # Event metrics
            if 'events' in scan_results:
                events = scan_results['events']

                # Event gaps by severity
                critical_gaps = events.get('critical_gaps', 0)
                total_gaps = events.get('gaps_found', 0)

                self.event_gaps.labels(severity='critical').set(critical_gaps)
                self.event_gaps.labels(severity='all').set(total_gaps)

                # Issues
                self.issues_detected.labels(
                    category='event_architecture',
                    severity='critical'
                ).set(critical_gaps)

            # Container metrics
            if 'containers' in scan_results:
                containers = scan_results['containers']

                missing_dockerfiles = containers.get('missing_dockerfiles', 0)
                self.services_without_dockerfile.set(missing_dockerfiles)

                self.issues_detected.labels(
                    category='missing_dockerfile',
                    severity='medium'
                ).set(missing_dockerfiles)

            # Deployment metrics
            if 'deployments' in scan_results:
                deployments = scan_results['deployments']

                # Port conflicts
                port_conflicts_count = deployments.get('port_conflicts', 0)
                self.port_conflicts.set(port_conflicts_count)

                # Service health
                total_services = deployments.get('total_services', 0)
                healthy_services = deployments.get('healthy_services', 0)

                if total_services > 0:
                    # Could expand with per-service metrics if needed
                    pass

            # Push to gateway
            push_to_gateway(
                self.pushgateway_url,
                job=self.job_name,
                registry=self.registry
            )

            logger.info(f" Metrics pushed to Prometheus: {self.pushgateway_url}")

        except Exception as e:
            logger.error(f" Failed to export scan metrics: {e}")

    def export_fix_metrics(self, fix_results: Dict[str, Any]):
        """
        Export fix results to Prometheus

        Args:
            fix_results: Fix results from DevOps Agent
        """
        try:
            # Fixes applied
            successful = fix_results.get('fixes_successful', 0)
            failed = fix_results.get('fixes_failed', 0)

            # Track by category if available
            for feedback in fix_results.get('feedbacks', []):
                category = feedback.get('category', 'unknown')
                success = feedback.get('success', False)

                self.fixes_applied_total.labels(
                    category=category,
                    success='true' if success else 'false'
                ).inc()

            # Push to gateway
            push_to_gateway(
                self.pushgateway_url,
                job=self.job_name,
                registry=self.registry
            )

            logger.info(f" Fix metrics pushed: {successful} successful, {failed} failed")

        except Exception as e:
            logger.error(f" Failed to export fix metrics: {e}")

    def export_dockerfile_metrics(self, generation_results: Dict[str, Any]):
        """
        Export Dockerfile generation metrics

        Args:
            generation_results: Dockerfile generation results
        """
        try:
            generated = generation_results.get('generated', [])
            failed = generation_results.get('failed', [])

            # Count by language if available
            for service in generated:
                language = service.get('language', 'unknown')
                self.dockerfiles_generated_total.labels(
                    language=language,
                    success='true'
                ).inc()

            for service in failed:
                language = service.get('language', 'unknown')
                self.dockerfiles_generated_total.labels(
                    language=language,
                    success='false'
                ).inc()

            # Push to gateway
            push_to_gateway(
                self.pushgateway_url,
                job=self.job_name,
                registry=self.registry
            )

            logger.info(f" Dockerfile metrics pushed: {len(generated)} generated")

        except Exception as e:
            logger.error(f" Failed to export Dockerfile metrics: {e}")

    def export_agent_statistics(self, statistics: Dict[str, Any]):
        """
        Export general agent statistics

        Args:
            statistics: Agent statistics (scans_completed, issues_detected, fixes_applied)
        """
        try:
            # These are cumulative metrics
            # For now, just push current state
            # In production, these would be tracked as Counters

            push_to_gateway(
                self.pushgateway_url,
                job=self.job_name,
                registry=self.registry
            )

            logger.info(" Agent statistics pushed to Prometheus")

        except Exception as e:
            logger.error(f" Failed to export agent statistics: {e}")

    def delete_metrics(self):
        """Delete all metrics from Pushgateway (cleanup)"""
        try:
            delete_from_gateway(
                self.pushgateway_url,
                job=self.job_name
            )
            logger.info(f"️ Metrics deleted from Pushgateway: {self.job_name}")

        except Exception as e:
            logger.error(f" Failed to delete metrics: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================

# Global exporter instance
_exporter: PrometheusExporter = None


def get_exporter() -> PrometheusExporter:
    """Get or create global Prometheus exporter"""
    global _exporter
    if _exporter is None:
        _exporter = PrometheusExporter()
    return _exporter


def export_scan_metrics(scan_results: Dict[str, Any]):
    """Export scan metrics (convenience function)"""
    get_exporter().export_scan_metrics(scan_results)


def export_fix_metrics(fix_results: Dict[str, Any]):
    """Export fix metrics (convenience function)"""
    get_exporter().export_fix_metrics(fix_results)


def export_dockerfile_metrics(generation_results: Dict[str, Any]):
    """Export Dockerfile generation metrics (convenience function)"""
    get_exporter().export_dockerfile_metrics(generation_results)


# ============================================================================
# Grafana Dashboard Config (JSON export)
# ============================================================================

GRAFANA_DASHBOARD = {
    "title": "DevOps Agent - Infrastructure Monitoring",
    "panels": [
        {
            "title": "Event Architecture Gaps",
            "targets": [
                {
                    "expr": "devops_event_gaps_total{severity='critical'}",
                    "legendFormat": "Critical Gaps"
                },
                {
                    "expr": "devops_event_gaps_total{severity='all'}",
                    "legendFormat": "Total Gaps"
                }
            ]
        },
        {
            "title": "Services Without Dockerfile",
            "targets": [
                {
                    "expr": "devops_services_without_dockerfile",
                    "legendFormat": "Missing Dockerfiles"
                }
            ]
        },
        {
            "title": "Port Conflicts",
            "targets": [
                {
                    "expr": "devops_port_conflicts",
                    "legendFormat": "Port Conflicts"
                }
            ]
        },
        {
            "title": "Fixes Applied (Success Rate)",
            "targets": [
                {
                    "expr": "rate(devops_fixes_applied_total{success='true'}[5m])",
                    "legendFormat": "Successful"
                },
                {
                    "expr": "rate(devops_fixes_applied_total{success='false'}[5m])",
                    "legendFormat": "Failed"
                }
            ]
        },
        {
            "title": "Scan Duration",
            "targets": [
                {
                    "expr": "devops_scan_duration_seconds",
                    "legendFormat": "{{scan_type}}"
                }
            ]
        }
    ]
}


if __name__ == "__main__":
    # Test exporter
    import asyncio

    async def test():
        exporter = PrometheusExporter()

        # Test scan metrics
        test_scan = {
            "scan_type": "full",
            "events": {
                "critical_gaps": 5,
                "gaps_found": 12
            },
            "containers": {
                "missing_dockerfiles": 3
            },
            "deployments": {
                "port_conflicts": 1,
                "total_services": 10,
                "healthy_services": 9
            }
        }

        exporter.export_scan_metrics(test_scan)
        print(" Test metrics exported!")

    asyncio.run(test())
