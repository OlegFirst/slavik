"""
Metrics Coverage Observer - Наблюдает за покрытием метрик

МиО Manager (ГЛАЗА) использует этот модуль для:
- Наблюдения: все ли сервисы мониторятся?
- Сравнения Service Discovery vs Prometheus targets
- Публикации observations в EventBus
- НЕ принимает решений, НЕ командует - только наблюдает!

Choreography:
- Использует Service Discovery v2 API для получения списка сервисов
- Публикует observations: platform.mio.metrics_coverage_observed
- Brain/DevOps Agent реагируют на observations
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import asyncio
import httpx

logger = logging.getLogger(__name__)


@dataclass
class MetricsCoverageObservation:
    """Наблюдение о покрытии метрик"""
    timestamp: datetime
    total_services: int
    monitored_services: int
    missing_services: List[str]
    coverage_percentage: float
    prometheus_targets_total: int
    prometheus_targets_healthy: int
    prometheus_targets_unhealthy: int
    unhealthy_targets: List[str]
    recommendation: str


@dataclass
class ServiceMetricsStatus:
    """Статус метрик одного сервиса"""
    service_name: str
    registered_in_discovery: bool
    monitored_by_prometheus: bool
    prometheus_health: Optional[str]  # 'up', 'down', None
    last_scrape_time: Optional[datetime]
    scrape_error: Optional[str]
    metrics_endpoint: str


class MetricsCoverageObserver:
    """
    Наблюдает за покрытием метрик системы

    МиО Manager (ГЛАЗА) - только наблюдает и публикует!
    НЕ принимает решений, НЕ командует, НЕ исправляет.

    Хореография:
    - Наблюдает Service Discovery v2 + Prometheus
    - Публикует observations в EventBus
    - Brain анализирует observations и принимает решения
    - DevOps Agent исправляет проблемы
    """

    def __init__(
        self,
        eventbus,
        service_discovery_url: str = "http://service-discovery:8500",
        prometheus_url: str = "http://prometheus:9090"
    ):
        self.eventbus = eventbus
        self.service_discovery_url = service_discovery_url
        self.prometheus_url = prometheus_url
        self.last_observation: Optional[MetricsCoverageObservation] = None

    # ========================================================================
    # Main Observation Methods
    # ========================================================================

    async def observe_coverage(self) -> MetricsCoverageObservation:
        """
        Основной метод наблюдения за coverage

        Returns:
            MetricsCoverageObservation с полным snapshot состояния
        """
        logger.info(" МиО observing metrics coverage...")

        try:
            # Get all registered services from Service Discovery v2
            registered_services = await self._get_registered_services()
            logger.info(f"   Found {len(registered_services)} registered services")

            # Get all Prometheus targets
            prometheus_targets = await self._get_prometheus_targets()
            logger.info(f"   Found {len(prometheus_targets)} Prometheus targets")

            # Analyze coverage
            service_statuses = self._analyze_service_statuses(
                registered_services,
                prometheus_targets
            )

            # Calculate metrics
            monitored = [s for s in service_statuses if s.monitored_by_prometheus]
            missing = [s.service_name for s in service_statuses if not s.monitored_by_prometheus]

            healthy_targets = [t for t in prometheus_targets if t.get('health') == 'up']
            unhealthy_targets = [
                t.get('labels', {}).get('job', 'unknown')
                for t in prometheus_targets
                if t.get('health') != 'up'
            ]

            coverage_pct = (len(monitored) / len(registered_services) * 100) if registered_services else 100.0

            # Generate recommendation (observation, not decision!)
            recommendation = self._generate_recommendation(coverage_pct, len(missing), len(unhealthy_targets))

            observation = MetricsCoverageObservation(
                timestamp=datetime.utcnow(),
                total_services=len(registered_services),
                monitored_services=len(monitored),
                missing_services=missing,
                coverage_percentage=coverage_pct,
                prometheus_targets_total=len(prometheus_targets),
                prometheus_targets_healthy=len(healthy_targets),
                prometheus_targets_unhealthy=len(unhealthy_targets),
                unhealthy_targets=unhealthy_targets,
                recommendation=recommendation
            )

            self.last_observation = observation

            logger.info(f"    Coverage observed: {coverage_pct:.1f}% ({len(monitored)}/{len(registered_services)})")
            if missing:
                logger.warning(f"   ️  Missing {len(missing)} services: {', '.join(missing[:5])}")
            if unhealthy_targets:
                logger.warning(f"   ️  {len(unhealthy_targets)} unhealthy targets: {', '.join(unhealthy_targets[:5])}")

            return observation

        except Exception as e:
            logger.error(f" Failed to observe metrics coverage: {e}")
            # Return minimal observation on error
            return MetricsCoverageObservation(
                timestamp=datetime.utcnow(),
                total_services=0,
                monitored_services=0,
                missing_services=[],
                coverage_percentage=0.0,
                prometheus_targets_total=0,
                prometheus_targets_healthy=0,
                prometheus_targets_unhealthy=0,
                unhealthy_targets=[],
                recommendation="Unable to observe - error occurred"
            )

    async def publish_observation(self, observation: MetricsCoverageObservation):
        """
        Публикует observation в EventBus

        Хореография:
        - МиО публикует observation
        - Brain может проанализировать и принять решение
        - DevOps Agent может отреагировать на проблемы
        - Analytics может собрать статистику
        """
        try:
            await self.eventbus.publish(
                'platform.mio.metrics_coverage_observed',
                {
                    'observation': asdict(observation),
                    'timestamp': observation.timestamp.isoformat(),
                    'summary': {
                        'coverage_percentage': observation.coverage_percentage,
                        'monitored_services': observation.monitored_services,
                        'total_services': observation.total_services,
                        'missing_count': len(observation.missing_services),
                        'unhealthy_count': observation.prometheus_targets_unhealthy
                    }
                },
                priority='normal'
            )
            logger.info(f" Published metrics coverage observation: {observation.coverage_percentage:.1f}% coverage")

            # If coverage is low, publish issue observation
            if observation.coverage_percentage < 90:
                await self._publish_coverage_issue(observation)

        except Exception as e:
            logger.error(f" Failed to publish observation: {e}")

    async def _publish_coverage_issue(self, observation: MetricsCoverageObservation):
        """Публикует observation о проблеме с coverage (для Brain/DevOps)"""
        severity = 'critical' if observation.coverage_percentage < 80 else 'high'

        await self.eventbus.publish(
            'platform.mio.metrics_coverage_issue_observed',
            {
                'coverage_percentage': observation.coverage_percentage,
                'missing_count': len(observation.missing_services),
                'missing_services': observation.missing_services,
                'unhealthy_count': observation.prometheus_targets_unhealthy,
                'unhealthy_targets': observation.unhealthy_targets,
                'severity': severity,
                'recommendation': observation.recommendation,
                'timestamp': observation.timestamp.isoformat()
            },
            priority='high'
        )
        logger.warning(f"️  Published coverage issue: {observation.coverage_percentage:.1f}% (severity: {severity})")

    # ========================================================================
    # Service Discovery v2 Integration
    # ========================================================================

    async def _get_registered_services(self) -> List[Dict]:
        """
        Get all registered services from Service Discovery v2

        ОБНОВЛЕНО: Использует v2 unified API вместо v1

        Returns:
            List of service dicts with name, host, port, metrics_endpoint
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Use Service Discovery v2 unified API
                response = await client.get(
                    f"{self.service_discovery_url}/v2/catalog/services"
                )
                response.raise_for_status()
                data = response.json()

                # Convert UnifiedService format to our format
                services = []
                for service in data.get('services', []):
                    # Only include registered services (not missing/unknown)
                    if service.get('registration_status') == 'registered':
                        services.append({
                            'name': service['name'],
                            'host': service['name'],  # Use service name as host
                            'port': service.get('actual_port') or service.get('expected_port'),
                            'metrics_endpoint': '/metrics'
                        })

                logger.debug(f"Retrieved {len(services)} registered services from Service Discovery v2")
                return services

        except httpx.HTTPError as e:
            logger.warning(f"Failed to get registered services from Service Discovery v2: {e}")
            # Fallback: try legacy v1 API
            return await self._get_registered_services_v1_fallback()
        except Exception as e:
            logger.error(f"Error getting registered services: {e}")
            return []

    async def _get_registered_services_v1_fallback(self) -> List[Dict]:
        """
        Fallback to v1 Consul-compatible API if v2 is unavailable

        Returns:
            List of services from v1 API
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.service_discovery_url}/v1/catalog/services"
                )
                response.raise_for_status()
                data = response.json()

                # v1 returns dict of {service_name: [tags]}
                services = []
                for service_name in data.keys():
                    services.append({
                        'name': service_name,
                        'host': service_name,
                        'port': None,  # Unknown in v1 catalog endpoint
                        'metrics_endpoint': '/metrics'
                    })

                logger.debug(f"Retrieved {len(services)} services from Service Discovery v1 (fallback)")
                return services

        except Exception as e:
            logger.error(f"v1 fallback also failed: {e}")
            return []

    # ========================================================================
    # Prometheus Integration
    # ========================================================================

    async def _get_prometheus_targets(self) -> List[Dict]:
        """
        Get all targets from Prometheus

        Returns:
            List of target dicts with health status, labels, etc.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.prometheus_url}/api/v1/targets")
                response.raise_for_status()
                data = response.json()

                if data.get('status') == 'success':
                    active_targets = data.get('data', {}).get('activeTargets', [])
                    return active_targets
                else:
                    logger.warning(f"Prometheus returned non-success status: {data.get('status')}")
                    return []

        except httpx.HTTPError as e:
            logger.warning(f"Failed to get Prometheus targets: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting Prometheus targets: {e}")
            return []

    # ========================================================================
    # Analysis Methods
    # ========================================================================

    def _analyze_service_statuses(
        self,
        registered_services: List[Dict],
        prometheus_targets: List[Dict]
    ) -> List[ServiceMetricsStatus]:
        """
        Анализирует статус метрик для каждого сервиса

        Сравнивает:
        - Зарегистрирован ли в Service Discovery?
        - Мониторится ли Prometheus?
        - Какой health status?
        """
        # Build index of Prometheus targets by job name
        prometheus_index = {}
        for target in prometheus_targets:
            job_name = target.get('labels', {}).get('job', '')
            if job_name:
                prometheus_index[job_name] = target

        # Analyze each registered service
        statuses = []
        for service in registered_services:
            service_name = service.get('name', '')
            prometheus_target = prometheus_index.get(service_name)

            if prometheus_target:
                # Service is monitored by Prometheus
                health = prometheus_target.get('health', 'unknown')
                last_scrape = prometheus_target.get('lastScrape')
                scrape_error = prometheus_target.get('lastError', '')

                last_scrape_time = None
                if last_scrape:
                    try:
                        last_scrape_time = datetime.fromisoformat(last_scrape.replace('Z', '+00:00'))
                    except:
                        pass

                status = ServiceMetricsStatus(
                    service_name=service_name,
                    registered_in_discovery=True,
                    monitored_by_prometheus=True,
                    prometheus_health=health,
                    last_scrape_time=last_scrape_time,
                    scrape_error=scrape_error if scrape_error else None,
                    metrics_endpoint=service.get('metrics_endpoint', '/metrics')
                )
            else:
                # Service is registered but NOT monitored by Prometheus
                status = ServiceMetricsStatus(
                    service_name=service_name,
                    registered_in_discovery=True,
                    monitored_by_prometheus=False,
                    prometheus_health=None,
                    last_scrape_time=None,
                    scrape_error=None,
                    metrics_endpoint=service.get('metrics_endpoint', '/metrics')
                )

            statuses.append(status)

        return statuses

    def _generate_recommendation(self, coverage_pct: float, missing_count: int, unhealthy_count: int) -> str:
        """
        Генерирует recommendation (observation, not decision!)

        МиО только наблюдает и рекомендует, НЕ принимает решений!
        """
        if coverage_pct >= 95 and unhealthy_count == 0:
            return "Excellent metrics coverage - all services monitored and healthy"

        recommendations = []

        if coverage_pct < 90:
            recommendations.append(
                f"Low coverage detected ({coverage_pct:.1f}%) - {missing_count} services not monitored. "
                "Recommendation: Check Prometheus configuration and service registration."
            )

        if unhealthy_count > 0:
            recommendations.append(
                f"{unhealthy_count} unhealthy Prometheus targets detected. "
                "Recommendation: Investigate scrape errors and service health."
            )

        if coverage_pct >= 90 and unhealthy_count > 0:
            recommendations.append(
                "Good coverage but some targets unhealthy. "
                "Recommendation: Monitor for service issues."
            )

        return " ".join(recommendations) if recommendations else "Monitoring coverage is acceptable"

    # ========================================================================
    # Public API (for dashboard/API endpoints)
    # ========================================================================

    def get_last_observation(self) -> Optional[MetricsCoverageObservation]:
        """Get the last observation (for dashboard)"""
        return self.last_observation

    async def get_service_statuses(self) -> List[ServiceMetricsStatus]:
        """
        Get detailed status for each service

        Returns:
            List of ServiceMetricsStatus
        """
        try:
            registered_services = await self._get_registered_services()
            prometheus_targets = await self._get_prometheus_targets()
            return self._analyze_service_statuses(registered_services, prometheus_targets)
        except Exception as e:
            logger.error(f"Failed to get service statuses: {e}")
            return []
