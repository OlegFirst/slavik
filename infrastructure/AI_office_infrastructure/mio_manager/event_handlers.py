"""
Event Handlers для МиО Manager

МиО Manager = ГЛАЗА (Observatory)
- Наблюдает события от других сервисов
- Публикует observations в EventBus
- НЕ принимает решений, НЕ командует

Choreography:
- Подписывается на: platform.monitoring.* (от Service Discovery)
- Публикует observations: platform.mio.* (для Brain, DevOps, Analytics)
"""

import logging
from typing import Dict, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class MioEventHandlers:
    """
    Event Handlers для МиО Manager

    Обрабатывает события от:
    - Service Discovery (регистрация, отключение, timeout)
    - Других сервисов платформы

    Публикует observations для:
    - Brain (принятие решений)
    - DevOps Agent (автоматическое исправление)
    - Analytics (сбор данных)
    - ai-event-manager (координация)
    """

    def __init__(
        self,
        eventbus,
        prometheus_url: str = "http://prometheus:9090",
        service_discovery_url: str = "http://service-discovery:8500"
    ):
        """
        Args:
            eventbus: EventBus client для публикаций
            prometheus_url: URL Prometheus для проверки мониторинга
            service_discovery_url: URL Service Discovery для проверок
        """
        self.eventbus = eventbus
        self.prometheus_url = prometheus_url
        self.service_discovery_url = service_discovery_url

        # Statistics
        self.stats = {
            'services_registered': 0,
            'services_disconnected': 0,
            'critical_timeouts': 0,
            'observations_published': 0,
            'last_event_time': None
        }

    # ========================================================================
    # Service Discovery Event Handlers
    # ========================================================================

    async def handle_service_registered(self, event: Dict):
        """
        Handle: platform.monitoring.service_registered

        Когда новый сервис регистрируется в Service Discovery,
        МиО проверяет:
        1. Зарегистрирован ли в Prometheus?
        2. Доступен ли metrics endpoint?
        3. Публикует observation если что-то не так
        """
        service_name = event['data']['service_name']
        port = event['data']['port']
        kpis = event['data'].get('kpis', [])
        orchestrator = event['data'].get('orchestrator', 'unknown')

        logger.info(f" МиО observed service registered: {service_name} (port: {port})")

        self.stats['services_registered'] += 1
        self.stats['last_event_time'] = datetime.utcnow().isoformat()

        # Check if Prometheus is monitoring this service
        is_monitored = await self._check_prometheus_monitoring(service_name)

        if not is_monitored:
            # Service not monitored by Prometheus - publish observation
            await self._publish_observation(
                'platform.mio.service_not_monitored_observed',
                {
                    'service_name': service_name,
                    'port': port,
                    'orchestrator': orchestrator,
                    'expected_kpis': kpis,
                    'observation': f'{service_name} is registered but not monitored by Prometheus',
                    'recommendation': 'Add service to Prometheus scrape targets',
                    'severity': 'medium'
                },
                priority='high'
            )

            logger.warning(f"   ️  {service_name} not monitored by Prometheus")
        else:
            logger.info(f"    {service_name} is monitored by Prometheus")

        # Check if metrics endpoint is accessible
        metrics_accessible = await self._check_metrics_endpoint(service_name, port)

        if not metrics_accessible:
            # Metrics endpoint not accessible - publish observation
            await self._publish_observation(
                'platform.mio.metrics_endpoint_unreachable_observed',
                {
                    'service_name': service_name,
                    'port': port,
                    'endpoint': f'http://{service_name}:{port}/metrics',
                    'observation': f'{service_name} metrics endpoint is unreachable',
                    'recommendation': 'Check if service exposes /metrics endpoint',
                    'severity': 'high'
                },
                priority='high'
            )

            logger.warning(f"   ️  {service_name} metrics endpoint unreachable")

    async def handle_service_disconnected(self, event: Dict):
        """
        Handle: platform.monitoring.service_disconnected

        Когда сервис отключается (gracefully или падает),
        МиО наблюдает и логирует.

        Другие сервисы (balancer, policy engine) уже получили это событие,
        так что МиО просто наблюдает.
        """
        service_name = event['data']['service_name']
        reason = event['data'].get('reason', 'unknown')

        logger.info(f" МиО observed service disconnected: {service_name} (reason: {reason})")

        self.stats['services_disconnected'] += 1
        self.stats['last_event_time'] = datetime.utcnow().isoformat()

        # Just observe - не нужно ничего публиковать, т.к. другие сервисы уже получили
        # Но можем обновить internal state если нужно

    async def handle_service_timeout(self, event: Dict):
        """
        Handle: platform.monitoring.critical_timeout

        CRITICAL EVENT: Сервис не отправил heartbeat > 60 секунд

        МиО наблюдает критический timeout и публикует observation
        для Brain и DevOps Agent.
        """
        service_name = event['data']['service_name']
        last_heartbeat = event['data']['last_heartbeat']
        timeout_seconds = event['data'].get('timeout_seconds', 60)

        logger.error(f" МиО observed CRITICAL TIMEOUT: {service_name}")
        logger.error(f"   Last heartbeat: {last_heartbeat}")
        logger.error(f"   Timeout: {timeout_seconds}s")

        self.stats['critical_timeouts'] += 1
        self.stats['last_event_time'] = datetime.utcnow().isoformat()

        # Publish critical observation для Brain/DevOps
        await self._publish_observation(
            'platform.mio.service_timeout_observed',
            {
                'service_name': service_name,
                'observation': f'{service_name} critical heartbeat timeout',
                'last_heartbeat': last_heartbeat,
                'timeout_seconds': timeout_seconds,
                'severity': 'critical',
                'recommendation': 'Immediate investigation and recovery required',
                'possible_causes': [
                    'Service crashed',
                    'Network connectivity issues',
                    'High load preventing heartbeat',
                    'Service hanging'
                ]
            },
            priority='critical'
        )

        logger.error(f"    Published critical timeout observation")

    # ========================================================================
    # Helper Methods - Checks
    # ========================================================================

    async def _check_prometheus_monitoring(self, service_name: str) -> bool:
        """
        Проверить, мониторится ли сервис Prometheus

        Args:
            service_name: Название сервиса

        Returns:
            True если сервис есть в Prometheus targets, False иначе
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.prometheus_url}/api/v1/targets")
                response.raise_for_status()
                data = response.json()

                if data.get('status') == 'success':
                    active_targets = data.get('data', {}).get('activeTargets', [])

                    for target in active_targets:
                        job_name = target.get('labels', {}).get('job', '')
                        if job_name == service_name:
                            return True

                return False

        except httpx.HTTPError as e:
            logger.warning(f"Failed to check Prometheus monitoring: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking Prometheus: {e}")
            return False

    async def _check_metrics_endpoint(self, service_name: str, port: int) -> bool:
        """
        Проверить доступность metrics endpoint

        Args:
            service_name: Название сервиса
            port: Порт сервиса

        Returns:
            True если endpoint доступен, False иначе
        """
        try:
            metrics_url = f"http://{service_name}:{port}/metrics"

            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(metrics_url)
                response.raise_for_status()

                # Check if response looks like Prometheus metrics
                text = response.text
                if '# TYPE' in text or '# HELP' in text:
                    return True

                # Accept any 200 response
                return True

        except httpx.HTTPError:
            return False
        except Exception as e:
            logger.debug(f"Metrics endpoint check failed for {service_name}: {e}")
            return False

    # ========================================================================
    # Helper Methods - Publishing
    # ========================================================================

    async def _publish_observation(
        self,
        event_type: str,
        data: Dict,
        priority: str = 'normal'
    ):
        """
        Публикация observation в EventBus

        Args:
            event_type: Тип события (platform.mio.*)
            data: Payload события
            priority: Приоритет (normal, high, critical)
        """
        try:
            # Add timestamp and source
            observation_data = {
                **data,
                'source': 'mio-manager',
                'observed_at': datetime.utcnow().isoformat()
            }

            await self.eventbus.publish(
                event_type,
                observation_data,
                priority=priority
            )

            self.stats['observations_published'] += 1

            logger.info(f" Published observation: {event_type} (priority: {priority})")

        except Exception as e:
            logger.error(f" Failed to publish observation {event_type}: {e}")

    # ========================================================================
    # Public API - Statistics
    # ========================================================================

    def get_stats(self) -> Dict:
        """
        Получить статистику event handlers

        Returns:
            Dict с метриками обработки событий
        """
        return {
            **self.stats,
            'uptime': 'running'  # TODO: Calculate actual uptime
        }

    def reset_stats(self):
        """Сбросить статистику"""
        self.stats = {
            'services_registered': 0,
            'services_disconnected': 0,
            'critical_timeouts': 0,
            'observations_published': 0,
            'last_event_time': None
        }
        logger.info(" Event handler statistics reset")


# ========================================================================
# Legacy Event Handlers (для обратной совместимости)
# ========================================================================

# TODO: Эти handlers нужно переместить в MioEventHandlers когда будем
# рефакторить остальные части кода

async def handle_problem_detected(event: Dict):
    """
    Legacy handler для platform.problem_detected

    TODO: Refactor to use MioEventHandlers
    """
    logger.info(f" МиО observed problem: {event.get('data', {}).get('problem_type', 'unknown')}")
    # Currently handled by EscalationManager


async def handle_task_completed(event: Dict):
    """
    Legacy handler для platform.task_completed

    TODO: Refactor to use MioEventHandlers
    """
    logger.info(f" МиО observed task completed: {event.get('data', {}).get('task_type', 'unknown')}")
    # Currently handled by ActionExecutor


async def handle_directive_issued(event: Dict):
    """
    Legacy handler для platform.directive_issued

    TODO: Refactor to use MioEventHandlers
    """
    logger.info(f" МиО observed directive: {event.get('data', {}).get('directive_type', 'unknown')}")
    # Currently handled by reaction layer


async def handle_service_deployed(event: Dict):
    """
    Legacy handler для platform.service_deployed

    TODO: Refactor to use MioEventHandlers
    """
    logger.info(f" МиО observed deployment: {event.get('data', {}).get('service_name', 'unknown')}")
    # Currently handled by reaction layer


async def handle_alert_triggered(event: Dict):
    """
    Legacy handler для platform.alert_triggered

    TODO: Refactor to use MioEventHandlers
    """
    logger.info(f" МиО observed alert: {event.get('data', {}).get('alert_type', 'unknown')}")
    # Currently handled by EscalationManager
