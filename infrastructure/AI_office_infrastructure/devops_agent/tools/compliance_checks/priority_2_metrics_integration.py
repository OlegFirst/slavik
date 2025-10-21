"""
ПРИОРИТЕТ 2: Проверка интеграции с метриками (Grafana/Prometheus)

После проверки конфликтов портов, проверяем подключение к системе метрик.
Каждый сервис должен:
1. Экспортировать метрики в формате Prometheus
2. Быть зарегистрирован в Prometheus targets
3. Иметь dashboard в Grafana (опционально, но желательно)

Это инструмент для проектного менеджера.
"""

import asyncio
import logging
import subprocess
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


@dataclass
class MetricsIntegration:
    """Интеграция сервиса с метриками"""
    service_name: str
    port: int
    metrics_endpoint: str  # Обычно /metrics
    prometheus_registered: bool
    prometheus_scraping: bool  # Prometheus активно собирает метрики
    grafana_dashboard_exists: bool
    last_scrape_time: Optional[str] = None
    scrape_errors: int = 0


# ИСТОЧНИК ПРАВДЫ: Ожидаемые endpoints метрик
EXPECTED_METRICS_ENDPOINTS = {
    # Platform Services
    'planning-service': {'port': 8011, 'endpoint': '/metrics'},
    'plans-service': {'port': 8023, 'endpoint': '/metrics'},
    'governance-service': {'port': 8030, 'endpoint': '/metrics'},
    'risk-service': {'port': 8040, 'endpoint': '/metrics'},
    'response-service': {'port': 8050, 'endpoint': '/metrics'},
    'learning-service': {'port': 8060, 'endpoint': '/metrics'},

    # Intelligent Core Services
    'workflow-intelligence': {'port': 9001, 'endpoint': '/metrics'},
    'ai-workflow-optimizer': {'port': 9002, 'endpoint': '/metrics'},
    'expertise-center': {'port': 9003, 'endpoint': '/metrics'},

    # Phase 2 Services
    'balancer-service': {'port': 9091, 'endpoint': '/metrics'},
    'resource-tracker': {'port': 9092, 'endpoint': '/metrics'},

    # AI Office Infrastructure
    'mio-manager': {'port': 7001, 'endpoint': '/metrics'},
    'monitoring-service': {'port': 7002, 'endpoint': '/metrics'},
    'notification-service': {'port': 7003, 'endpoint': '/metrics'},

    # Infrastructure
    'postgres-exporter': {'port': 9187, 'endpoint': '/metrics'},
    'redis-exporter': {'port': 9121, 'endpoint': '/metrics'},
}

# Prometheus и Grafana
PROMETHEUS_URL = 'http://localhost:9090'
GRAFANA_URL = 'http://localhost:3000'


class MetricsIntegrationChecker:
    """
    Проверка интеграции с системой метрик

    ПРИОРИТЕТ 2: Запускается после проверки портов
    """

    def __init__(self):
        self.integrations: Dict[str, MetricsIntegration] = {}
        self.prometheus_available = False
        self.grafana_available = False

    def check_prometheus_available(self) -> bool:
        """Проверить доступность Prometheus"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        try:
            result = sock.connect_ex(('localhost', 9090))
            self.prometheus_available = (result == 0)
            return self.prometheus_available
        except socket.error:
            self.prometheus_available = False
            return False
        finally:
            sock.close()

    def check_grafana_available(self) -> bool:
        """Проверить доступность Grafana"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        try:
            result = sock.connect_ex(('localhost', 3000))
            self.grafana_available = (result == 0)
            return self.grafana_available
        except socket.error:
            self.grafana_available = False
            return False
        finally:
            sock.close()

    def check_metrics_endpoint(self, host: str, port: int, endpoint: str) -> bool:
        """
        Проверить наличие endpoint метрик

        Args:
            host: Хост
            port: Порт
            endpoint: Путь к endpoint (обычно /metrics)

        Returns:
            True если endpoint доступен
        """
        try:
            # Попробуем подключиться
            import subprocess

            result = subprocess.run(
                ['curl', '-f', '-s', '-m', '2', f'http://{host}:{port}{endpoint}'],
                capture_output=True,
                timeout=3
            )

            # Проверяем, что ответ содержит метрики Prometheus
            if result.returncode == 0:
                output = result.stdout.decode('utf-8', errors='ignore')
                # Метрики Prometheus обычно содержат '# HELP' или '# TYPE'
                return '# HELP' in output or '# TYPE' in output

            return False

        except Exception as e:
            logger.debug(f"Не удалось проверить {host}:{port}{endpoint}: {e}")
            return False

    def get_prometheus_targets(self) -> Dict[str, Dict]:
        """
        Получить список targets из Prometheus

        Returns:
            Dict[target_url -> target_info]
        """
        if not self.prometheus_available:
            return {}

        try:
            result = subprocess.run(
                ['curl', '-s', f'{PROMETHEUS_URL}/api/v1/targets'],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)

                if data.get('status') == 'success':
                    targets = {}

                    for target in data.get('data', {}).get('activeTargets', []):
                        url = target.get('scrapeUrl', '')
                        targets[url] = {
                            'health': target.get('health', 'unknown'),
                            'lastScrape': target.get('lastScrape', ''),
                            'lastError': target.get('lastError', ''),
                            'labels': target.get('labels', {})
                        }

                    return targets

        except Exception as e:
            logger.error(f"Не удалось получить targets из Prometheus: {e}")

        return {}

    def check_integrations(self) -> List[MetricsIntegration]:
        """
        Проверить интеграцию всех сервисов с метриками

        Returns:
            Список интеграций
        """
        logger.info("=" * 80)
        logger.info("ПРИОРИТЕТ 2: Проверка интеграции с метриками")
        logger.info("=" * 80)

        # Проверяем доступность Prometheus и Grafana
        prom_available = self.check_prometheus_available()
        grafana_available = self.check_grafana_available()

        logger.info(f"Prometheus: {' доступен' if prom_available else ' недоступен'}")
        logger.info(f"Grafana: {' доступен' if grafana_available else ' недоступен'}")
        logger.info("")

        if not prom_available:
            logger.warning("️  Prometheus недоступен - невозможно проверить scraping")

        # Получаем targets из Prometheus
        prometheus_targets = self.get_prometheus_targets() if prom_available else {}

        logger.info(f"Prometheus targets: {len(prometheus_targets)}")
        logger.info("")

        # Проверяем каждый сервис
        integrations = []

        for service_name, config in EXPECTED_METRICS_ENDPOINTS.items():
            port = config['port']
            endpoint = config['endpoint']

            # Проверяем endpoint метрик
            has_metrics = self.check_metrics_endpoint('localhost', port, endpoint)

            # Проверяем регистрацию в Prometheus
            target_url = f'http://localhost:{port}{endpoint}'
            prometheus_registered = target_url in prometheus_targets
            prometheus_scraping = False
            last_scrape = None
            scrape_errors = 0

            if prometheus_registered:
                target_info = prometheus_targets[target_url]
                prometheus_scraping = (target_info['health'] == 'up')
                last_scrape = target_info.get('lastScrape')

                if target_info.get('lastError'):
                    scrape_errors = 1  # Есть ошибка

            # TODO: Проверить наличие dashboard в Grafana
            # (требует API Grafana или проверку конфигурации)
            grafana_dashboard = False

            integration = MetricsIntegration(
                service_name=service_name,
                port=port,
                metrics_endpoint=endpoint,
                prometheus_registered=prometheus_registered,
                prometheus_scraping=prometheus_scraping,
                grafana_dashboard_exists=grafana_dashboard,
                last_scrape_time=last_scrape,
                scrape_errors=scrape_errors
            )

            integrations.append(integration)
            self.integrations[service_name] = integration

            # Логирование результата
            status_icon = "" if has_metrics and prometheus_scraping else ""
            logger.info(f"{status_icon} {service_name}:")
            logger.info(f"   Metrics endpoint: {'' if has_metrics else ''} (http://localhost:{port}{endpoint})")
            logger.info(f"   Prometheus зарегистрирован: {'' if prometheus_registered else ''}")
            logger.info(f"   Prometheus собирает: {'' if prometheus_scraping else ''}")

            if last_scrape:
                logger.info(f"   Последний сбор: {last_scrape}")

            logger.info("")

        # Итоговый отчет
        total = len(integrations)
        with_metrics = sum(1 for i in integrations if i.prometheus_scraping)

        logger.info(f"Итого: {with_metrics}/{total} сервисов полностью интегрированы")

        return integrations

    def get_metrics_state_for_central_brain(self) -> Dict[str, any]:
        """
        Получить состояние метрик для Центрального Мозга

        Центральный мозг получает только ФАКТИЧЕСКОЕ состояние.

        Returns:
            Фактическое состояние системы метрик
        """
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'prometheus_available': self.prometheus_available,
            'grafana_available': self.grafana_available,
            'services_with_metrics': sum(
                1 for i in self.integrations.values()
                if i.prometheus_scraping
            ),
            'total_services': len(self.integrations)
        }

    def generate_report(self) -> str:
        """
        Сгенерировать отчет

        Returns:
            Текстовый отчет
        """
        report = []
        report.append("=" * 80)
        report.append("ПРИОРИТЕТ 2: Отчет об интеграции с метриками")
        report.append("=" * 80)
        report.append(f"Дата проверки: {datetime.utcnow().isoformat()}")
        report.append("")

        report.append("Инфраструктура метрик:")
        report.append(f"  Prometheus: {' доступен' if self.prometheus_available else ' недоступен'}")
        report.append(f"  Grafana: {' доступен' if self.grafana_available else ' недоступен'}")
        report.append("")

        # Статистика
        total = len(self.integrations)
        fully_integrated = sum(
            1 for i in self.integrations.values()
            if i.prometheus_scraping
        )

        report.append("Статистика интеграции:")
        report.append(f"  Всего сервисов: {total}")
        report.append(f"  Полностью интегрированных: {fully_integrated}")
        report.append(f"  Процент покрытия: {(fully_integrated / total * 100) if total > 0 else 0:.1f}%")
        report.append("")

        # Проблемные сервисы
        problems = [
            i for i in self.integrations.values()
            if not i.prometheus_scraping
        ]

        if problems:
            report.append(f" Сервисы БЕЗ метрик ({len(problems)}):")
            for integration in problems:
                report.append(f"  - {integration.service_name} (порт {integration.port})")

                if not integration.prometheus_registered:
                    report.append(f"    Причина: не зарегистрирован в Prometheus")
                elif integration.scrape_errors > 0:
                    report.append(f"    Причина: ошибки при сборе метрик")

            report.append("")
        else:
            report.append(" Все сервисы интегрированы с метриками")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def check_metrics_integration() -> bool:
    """
    Проверить интеграцию с метриками (основная функция)

    Returns:
        True если все OK
    """
    checker = MetricsIntegrationChecker()
    integrations = checker.check_integrations()

    print(checker.generate_report())

    # Проверяем, что хотя бы Prometheus доступен
    if not checker.prometheus_available:
        logger.error(" Prometheus недоступен - система метрик не работает")
        return False

    # Проверяем, что большинство сервисов интегрированы
    fully_integrated = sum(1 for i in integrations if i.prometheus_scraping)
    total = len(integrations)

    if fully_integrated / total < 0.5:  # Менее 50% интегрированы
        logger.error(
            f" Недостаточно сервисов интегрированы: "
            f"{fully_integrated}/{total} ({fully_integrated / total * 100:.0f}%)"
        )
        return False

    return True


if __name__ == '__main__':
    """Запуск проверки"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    success = check_metrics_integration()

    exit(0 if success else 1)
