"""
Metrics Health Checker - Проверка здоровья метрик

МиО Manager (ГЛАЗА) использует этот модуль для:
- Проверки доступности metrics endpoints
- Проверки актуальности метрик (last scrape time)
- Проверки scrape errors в Prometheus
- Публикации health observations в EventBus
- НЕ принимает решений, НЕ командует - только наблюдает!

Choreography:
- Публикует observations: platform.mio.metrics_health_observed
- Brain/DevOps Agent реагируют на observations
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import asyncio
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ServiceMetricsHealth:
    """Здоровье метрик одного сервиса"""
    service_name: str
    endpoint_url: str
    endpoint_reachable: bool
    last_scrape_time: Optional[datetime]
    scrape_duration_seconds: Optional[float]
    scrape_error: Optional[str]
    metrics_count: Optional[int]  # Количество метрик
    health_status: str  # 'healthy', 'warning', 'critical', 'unknown'
    issues: List[str]  # List of detected issues


@dataclass
class MetricsHealthObservation:
    """Наблюдение о здоровье метрик системы"""
    timestamp: datetime
    total_services: int
    healthy_services: int
    warning_services: int
    critical_services: int
    unreachable_services: int
    service_healths: List[ServiceMetricsHealth]
    overall_health: str  # 'healthy', 'degraded', 'critical'
    critical_issues: List[str]
    recommendation: str


class MetricsHealthChecker:
    """
    Проверяет здоровье метрик системы

    МиО Manager (ГЛАЗА) - только наблюдает и публикует!
    НЕ принимает решений, НЕ командует, НЕ исправляет.

    Хореография:
    - Проверяет health всех metrics endpoints
    - Публикует observations в EventBus
    - Brain анализирует observations и принимает решения
    - DevOps Agent исправляет проблемы
    """

    def __init__(
        self,
        eventbus,
        prometheus_url: str = "http://prometheus:9090",
        scrape_freshness_threshold_seconds: int = 120  # Alert if metrics older than 2min
    ):
        self.eventbus = eventbus
        self.prometheus_url = prometheus_url
        self.scrape_freshness_threshold = scrape_freshness_threshold_seconds
        self.last_observation: Optional[MetricsHealthObservation] = None

    # ========================================================================
    # Main Health Check Methods
    # ========================================================================

    async def check_all_endpoints(self) -> MetricsHealthObservation:
        """
        Проверить здоровье всех metrics endpoints

        Returns:
            MetricsHealthObservation с полным snapshot здоровья
        """
        logger.info("👀 МиО checking metrics health...")

        try:
            # Get all Prometheus targets
            prometheus_targets = await self._get_prometheus_targets()
            logger.info(f"   Found {len(prometheus_targets)} Prometheus targets")

            # Check health for each target
            service_healths = []
            for target in prometheus_targets:
                health = await self._check_target_health(target)
                service_healths.append(health)

            # Categorize by health status
            healthy = [s for s in service_healths if s.health_status == 'healthy']
            warning = [s for s in service_healths if s.health_status == 'warning']
            critical = [s for s in service_healths if s.health_status == 'critical']
            unreachable = [s for s in service_healths if not s.endpoint_reachable]

            # Determine overall health
            overall_health = self._determine_overall_health(len(healthy), len(warning), len(critical), len(service_healths))

            # Collect critical issues
            critical_issues = []
            for service in critical + unreachable:
                if service.issues:
                    critical_issues.extend([
                        f"{service.service_name}: {issue}" for issue in service.issues
                    ])

            # Generate recommendation
            recommendation = self._generate_recommendation(overall_health, len(critical_issues), len(unreachable))

            observation = MetricsHealthObservation(
                timestamp=datetime.utcnow(),
                total_services=len(service_healths),
                healthy_services=len(healthy),
                warning_services=len(warning),
                critical_services=len(critical),
                unreachable_services=len(unreachable),
                service_healths=service_healths,
                overall_health=overall_health,
                critical_issues=critical_issues,
                recommendation=recommendation
            )

            self.last_observation = observation

            logger.info(
                f"   ✅ Metrics health observed: "
                f"{len(healthy)}/{len(service_healths)} healthy, "
                f"{len(warning)} warnings, "
                f"{len(critical)} critical"
            )

            if critical_issues:
                logger.warning(f"   ⚠️  {len(critical_issues)} critical issues detected")

            return observation

        except Exception as e:
            logger.error(f"❌ Failed to check metrics health: {e}")
            # Return minimal observation on error
            return MetricsHealthObservation(
                timestamp=datetime.utcnow(),
                total_services=0,
                healthy_services=0,
                warning_services=0,
                critical_services=0,
                unreachable_services=0,
                service_healths=[],
                overall_health='unknown',
                critical_issues=[f"Health check failed: {str(e)}"],
                recommendation="Unable to check metrics health - investigate monitoring system"
            )

    async def publish_health_observation(self, observation: MetricsHealthObservation):
        """
        Публикует health observation в EventBus

        Хореография:
        - МиО публикует observation
        - Brain может проанализировать и принять решение
        - DevOps Agent может отреагировать на проблемы
        - Analytics может собрать статистику
        """
        try:
            await self.eventbus.publish(
                'platform.mio.metrics_health_observed',
                {
                    'observation': asdict(observation),
                    'timestamp': observation.timestamp.isoformat(),
                    'summary': {
                        'overall_health': observation.overall_health,
                        'healthy_services': observation.healthy_services,
                        'total_services': observation.total_services,
                        'critical_issues_count': len(observation.critical_issues)
                    }
                },
                priority='normal'
            )
            logger.info(f"📡 Published metrics health observation: {observation.overall_health}")

            # If critical health, publish separate issue observation
            if observation.overall_health == 'critical' or observation.critical_services > 0:
                await self._publish_health_issue(observation)

        except Exception as e:
            logger.error(f"❌ Failed to publish health observation: {e}")

    async def _publish_health_issue(self, observation: MetricsHealthObservation):
        """Публикует observation о критичной проблеме со здоровьем метрик"""
        severity = 'critical' if observation.overall_health == 'critical' else 'high'

        await self.eventbus.publish(
            'platform.mio.metrics_health_issue_observed',
            {
                'overall_health': observation.overall_health,
                'critical_services': observation.critical_services,
                'unreachable_services': observation.unreachable_services,
                'critical_issues': observation.critical_issues,
                'severity': severity,
                'recommendation': observation.recommendation,
                'timestamp': observation.timestamp.isoformat()
            },
            priority='high'
        )
        logger.warning(f"⚠️  Published health issue: {observation.overall_health} (severity: {severity})")

    # ========================================================================
    # Prometheus Integration
    # ========================================================================

    async def _get_prometheus_targets(self) -> List[Dict]:
        """
        Get all targets from Prometheus

        Returns:
            List of target dicts with health, labels, scrape info
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

    async def _check_target_health(self, target: Dict) -> ServiceMetricsHealth:
        """
        Проверить здоровье одного Prometheus target

        Args:
            target: Prometheus target dict

        Returns:
            ServiceMetricsHealth with detailed health info
        """
        service_name = target.get('labels', {}).get('job', 'unknown')
        scrape_url = target.get('scrapeUrl', '')

        # Get basic info from Prometheus
        health = target.get('health', 'unknown')
        last_scrape = target.get('lastScrape')
        scrape_duration = target.get('scrapeDuration', 0)
        last_error = target.get('lastError', '')

        # Parse last scrape time
        last_scrape_time = None
        if last_scrape:
            try:
                last_scrape_time = datetime.fromisoformat(last_scrape.replace('Z', '+00:00'))
            except:
                pass

        # Check endpoint reachability (basic check from Prometheus health)
        endpoint_reachable = (health == 'up')

        # Detect issues
        issues = []
        health_status = 'healthy'

        # Issue 1: Endpoint unreachable
        if not endpoint_reachable:
            issues.append('Endpoint unreachable')
            health_status = 'critical'

        # Issue 2: Scrape error
        if last_error:
            issues.append(f'Scrape error: {last_error}')
            health_status = 'critical'

        # Issue 3: Stale metrics (last scrape too old)
        if last_scrape_time:
            age_seconds = (datetime.utcnow().replace(tzinfo=None) - last_scrape_time.replace(tzinfo=None)).total_seconds()
            if age_seconds > self.scrape_freshness_threshold:
                issues.append(f'Stale metrics (last scrape {age_seconds:.0f}s ago)')
                if health_status == 'healthy':
                    health_status = 'warning'

        # Issue 4: Slow scrape duration
        if scrape_duration > 5.0:  # > 5 seconds is concerning
            issues.append(f'Slow scrape duration ({scrape_duration:.2f}s)')
            if health_status == 'healthy':
                health_status = 'warning'

        # Try to get metrics count (additional check)
        metrics_count = None
        try:
            metrics_count = await self._get_metrics_count(scrape_url)
        except:
            pass

        return ServiceMetricsHealth(
            service_name=service_name,
            endpoint_url=scrape_url,
            endpoint_reachable=endpoint_reachable,
            last_scrape_time=last_scrape_time,
            scrape_duration_seconds=scrape_duration,
            scrape_error=last_error if last_error else None,
            metrics_count=metrics_count,
            health_status=health_status,
            issues=issues
        )

    async def _get_metrics_count(self, scrape_url: str) -> int:
        """
        Попытаться получить количество метрик из endpoint

        Returns:
            Count of metrics, or None if unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(scrape_url)
                response.raise_for_status()

                # Count non-comment lines (rough estimate)
                lines = response.text.split('\n')
                metrics_lines = [l for l in lines if l and not l.startswith('#')]
                return len(metrics_lines)

        except:
            return None

    # ========================================================================
    # Analysis Methods
    # ========================================================================

    def _determine_overall_health(
        self,
        healthy_count: int,
        warning_count: int,
        critical_count: int,
        total_count: int
    ) -> str:
        """
        Определить общее здоровье системы метрик

        Returns:
            'healthy', 'degraded', 'critical', or 'unknown'
        """
        if total_count == 0:
            return 'unknown'

        healthy_pct = (healthy_count / total_count) * 100

        if critical_count > 0:
            # Any critical service = overall critical
            if critical_count >= total_count * 0.2:  # >= 20% critical
                return 'critical'
            else:
                return 'degraded'

        if warning_count > 0:
            if healthy_pct < 80:
                return 'degraded'
            else:
                return 'healthy'

        return 'healthy'

    def _generate_recommendation(
        self,
        overall_health: str,
        critical_issues_count: int,
        unreachable_count: int
    ) -> str:
        """
        Генерация recommendation (observation, not decision!)

        МиО только наблюдает и рекомендует, НЕ принимает решений!
        """
        if overall_health == 'healthy':
            return "All metrics endpoints are healthy and responding"

        recommendations = []

        if overall_health == 'critical':
            recommendations.append(
                f"CRITICAL: Metrics system health is critical. "
                f"{critical_issues_count} issues detected. "
                "Immediate investigation required."
            )

        if unreachable_count > 0:
            recommendations.append(
                f"{unreachable_count} services have unreachable metrics endpoints. "
                "Recommendation: Check service health and network connectivity."
            )

        if overall_health == 'degraded':
            recommendations.append(
                "Metrics system health is degraded. "
                "Recommendation: Review warnings and scrape errors."
            )

        return " ".join(recommendations) if recommendations else "Review metrics health warnings"

    # ========================================================================
    # Public API (for dashboard/API endpoints)
    # ========================================================================

    def get_last_observation(self) -> Optional[MetricsHealthObservation]:
        """Get the last health observation (for dashboard)"""
        return self.last_observation

    async def get_service_health(self, service_name: str) -> Optional[ServiceMetricsHealth]:
        """
        Get health for specific service

        Args:
            service_name: Service name to check

        Returns:
            ServiceMetricsHealth or None if not found
        """
        if not self.last_observation:
            return None

        for service_health in self.last_observation.service_healths:
            if service_health.service_name == service_name:
                return service_health

        return None

    async def get_unhealthy_services(self) -> List[ServiceMetricsHealth]:
        """
        Get list of all unhealthy services

        Returns:
            List of ServiceMetricsHealth with health_status != 'healthy'
        """
        if not self.last_observation:
            return []

        return [
            s for s in self.last_observation.service_healths
            if s.health_status != 'healthy'
        ]
