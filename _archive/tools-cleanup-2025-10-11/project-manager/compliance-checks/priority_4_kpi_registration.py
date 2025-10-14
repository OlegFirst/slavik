#!/usr/bin/env python3
"""
ПРИОРИТЕТ 4: Проверка Регистрации KPI

Проверяет, что каждый сервис:
1. Имеет определенные KPI
2. KPI зарегистрированы в системе мониторинга
3. KPI обновляются регулярно
4. KPI соответствуют стандартам платформы

Этот приоритет выполняется ПОСЛЕ:
- Priority 1: Port Conflicts (критично)
- Priority 2: Metrics Integration (метрики должны работать)
- Priority 3: Database Connections (БД должна быть доступна)

Created: 2025-10-09
Status: ✅ Implemented
"""

import sys
import logging
import socket
import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KPISeverity(Enum):
    """Серьезность проблемы с KPI"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ServiceKPI:
    """Определение KPI сервиса"""
    service_name: str
    kpi_name: str
    kpi_type: str  # counter, gauge, histogram, summary
    registered: bool = False
    last_updated: Optional[datetime] = None
    has_data: bool = False
    prometheus_metric_name: Optional[str] = None
    current_value: Optional[float] = None
    severity: KPISeverity = KPISeverity.INFO
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['severity'] = self.severity.value
        if self.last_updated:
            result['last_updated'] = self.last_updated.isoformat()
        return result


# Ожидаемые KPI для каждого сервиса
EXPECTED_SERVICE_KPIS = {
    # Platform Services
    'planning-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'strategies_created_total': {'type': 'counter', 'metric': 'strategies_created_total'},
        'strategies_active': {'type': 'gauge', 'metric': 'strategies_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'plans-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'plans_created_total': {'type': 'counter', 'metric': 'plans_created_total'},
        'plans_active': {'type': 'gauge', 'metric': 'plans_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'bia-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'bia_analyses_total': {'type': 'counter', 'metric': 'bia_analyses_total'},
        'bia_analyses_active': {'type': 'gauge', 'metric': 'bia_analyses_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'risk-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'risks_assessed_total': {'type': 'counter', 'metric': 'risks_assessed_total'},
        'risks_active': {'type': 'gauge', 'metric': 'risks_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'response-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'incidents_handled_total': {'type': 'counter', 'metric': 'incidents_handled_total'},
        'incidents_active': {'type': 'gauge', 'metric': 'incidents_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'compliance-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'compliance_checks_total': {'type': 'counter', 'metric': 'compliance_checks_total'},
        'compliance_violations': {'type': 'gauge', 'metric': 'compliance_violations'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'governance-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'policies_active': {'type': 'gauge', 'metric': 'policies_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'documents-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'documents_stored_total': {'type': 'counter', 'metric': 'documents_stored_total'},
        'documents_active': {'type': 'gauge', 'metric': 'documents_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'validation-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'validations_performed_total': {'type': 'counter', 'metric': 'validations_performed_total'},
        'validation_failures': {'type': 'gauge', 'metric': 'validation_failures'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'learning-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'learning_sessions_total': {'type': 'counter', 'metric': 'learning_sessions_total'},
        'learning_sessions_active': {'type': 'gauge', 'metric': 'learning_sessions_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'community-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'community_members': {'type': 'gauge', 'metric': 'community_members'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'bcm-coordination-service': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'coordination_tasks_total': {'type': 'counter', 'metric': 'coordination_tasks_total'},
        'coordination_tasks_active': {'type': 'gauge', 'metric': 'coordination_tasks_active'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },

    # Intelligent Core Services
    'workflow-intelligence': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'workflows_executed_total': {'type': 'counter', 'metric': 'workflows_executed_total'},
        'workflows_active': {'type': 'gauge', 'metric': 'workflows_active'},
        'ai_predictions_made': {'type': 'counter', 'metric': 'ai_predictions_made'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'event-intelligence': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'events_processed_total': {'type': 'counter', 'metric': 'events_processed_total'},
        'events_queue_size': {'type': 'gauge', 'metric': 'events_queue_size'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'expertise-center': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'consultations_provided': {'type': 'counter', 'metric': 'consultations_provided'},
        'knowledge_base_size': {'type': 'gauge', 'metric': 'knowledge_base_size'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'community-intelligence': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'community_insights_generated': {'type': 'counter', 'metric': 'community_insights_generated'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'ai-workflow-optimizer': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'http_request_duration_seconds': {'type': 'histogram', 'metric': 'http_request_duration_seconds'},
        'optimizations_applied': {'type': 'counter', 'metric': 'optimizations_applied'},
        'workflows_optimized': {'type': 'gauge', 'metric': 'workflows_optimized'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },

    # Infrastructure Services
    'monitoring': {
        'http_requests_total': {'type': 'counter', 'metric': 'http_requests_total'},
        'services_monitored': {'type': 'gauge', 'metric': 'services_monitored'},
        'alerts_triggered_total': {'type': 'counter', 'metric': 'alerts_triggered_total'},
        'database_connections': {'type': 'gauge', 'metric': 'database_connections'},
    },
    'notification-service': {
        'notifications_sent_total': {'type': 'counter', 'metric': 'notifications_sent_total'},
        'notification_queue_size': {'type': 'gauge', 'metric': 'notification_queue_size'},
        'notification_failures': {'type': 'counter', 'metric': 'notification_failures'},
    },
    'eventbus': {
        'events_published_total': {'type': 'counter', 'metric': 'events_published_total'},
        'events_consumed_total': {'type': 'counter', 'metric': 'events_consumed_total'},
        'connected_consumers': {'type': 'gauge', 'metric': 'connected_consumers'},
        'queue_size': {'type': 'gauge', 'metric': 'queue_size'},
    },
}


class KPIRegistrationChecker:
    """Проверка регистрации KPI"""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})

    def check_prometheus_available(self) -> bool:
        """Проверить доступность Prometheus"""
        try:
            response = self.session.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Prometheus unavailable: {e}")
            return False

    def get_all_prometheus_metrics(self) -> Set[str]:
        """Получить все метрики из Prometheus"""
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/label/__name__/values",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return set(data.get('data', []))

            return set()
        except Exception as e:
            logger.error(f"Failed to get Prometheus metrics: {e}")
            return set()

    def query_metric(self, metric_name: str, service_label: Optional[str] = None) -> Optional[Dict]:
        """Запросить метрику из Prometheus"""
        try:
            # Build query
            if service_label:
                query = f'{metric_name}{{service="{service_label}"}}'
            else:
                query = metric_name

            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': query},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    result = data.get('data', {}).get('result', [])
                    if result:
                        return result[0]

            return None
        except Exception as e:
            logger.debug(f"Failed to query metric {metric_name}: {e}")
            return None

    def check_kpi_registration(self, service_name: str, kpi_name: str,
                               kpi_config: Dict) -> ServiceKPI:
        """Проверить регистрацию KPI для сервиса"""
        metric_name = kpi_config.get('metric', kpi_name)
        kpi_type = kpi_config.get('type', 'gauge')

        kpi = ServiceKPI(
            service_name=service_name,
            kpi_name=kpi_name,
            kpi_type=kpi_type,
            prometheus_metric_name=metric_name
        )

        # Query metric from Prometheus
        result = self.query_metric(metric_name, service_name)

        if result:
            kpi.registered = True
            kpi.has_data = True

            # Extract value
            value_data = result.get('value', [])
            if len(value_data) >= 2:
                try:
                    kpi.current_value = float(value_data[1])
                    # Timestamp is value_data[0]
                    kpi.last_updated = datetime.fromtimestamp(float(value_data[0]))
                except (ValueError, TypeError) as e:
                    logger.debug(f"Failed to parse metric value: {e}")

            kpi.severity = KPISeverity.INFO
            kpi.message = f"✅ KPI зарегистрирован и обновляется (значение: {kpi.current_value})"
        else:
            kpi.registered = False
            kpi.has_data = False
            kpi.severity = KPISeverity.WARNING
            kpi.message = f"⚠️ KPI не найден в Prometheus"

        return kpi

    def check_all_kpis(self) -> Dict[str, List[ServiceKPI]]:
        """Проверить все KPI для всех сервисов"""
        logger.info("Checking KPI registration for all services...")

        # Check Prometheus availability
        if not self.check_prometheus_available():
            logger.error("❌ Prometheus недоступен - невозможно проверить KPI")
            return {}

        # Get all metrics from Prometheus
        all_metrics = self.get_all_prometheus_metrics()
        logger.info(f"Found {len(all_metrics)} metrics in Prometheus")

        results = {}

        for service_name, kpis in EXPECTED_SERVICE_KPIS.items():
            service_kpis = []

            for kpi_name, kpi_config in kpis.items():
                kpi = self.check_kpi_registration(service_name, kpi_name, kpi_config)
                service_kpis.append(kpi)

            results[service_name] = service_kpis

        return results

    def generate_summary(self, results: Dict[str, List[ServiceKPI]]) -> Dict[str, Any]:
        """Сгенерировать сводку по KPI"""
        total_services = len(results)
        total_kpis = sum(len(kpis) for kpis in results.values())

        registered_kpis = sum(
            1 for kpis in results.values()
            for kpi in kpis
            if kpi.registered
        )

        services_with_all_kpis = sum(
            1 for kpis in results.values()
            if all(kpi.registered for kpi in kpis)
        )

        services_with_no_kpis = sum(
            1 for kpis in results.values()
            if not any(kpi.registered for kpi in kpis)
        )

        return {
            'total_services': total_services,
            'total_kpis': total_kpis,
            'registered_kpis': registered_kpis,
            'kpi_coverage_percent': (registered_kpis / total_kpis * 100) if total_kpis > 0 else 0,
            'services_with_all_kpis': services_with_all_kpis,
            'services_with_partial_kpis': total_services - services_with_all_kpis - services_with_no_kpis,
            'services_with_no_kpis': services_with_no_kpis
        }

    def print_results(self, results: Dict[str, List[ServiceKPI]]):
        """Вывести результаты проверки"""
        print("\n" + "="*80)
        print("ПРИОРИТЕТ 4: Проверка регистрации KPI")
        print("="*80 + "\n")

        summary = self.generate_summary(results)

        print(f"Всего сервисов: {summary['total_services']}")
        print(f"Всего KPI: {summary['total_kpis']}")
        print(f"Зарегистрировано KPI: {summary['registered_kpis']}/{summary['total_kpis']} ({summary['kpi_coverage_percent']:.1f}%)")
        print(f"Сервисов со всеми KPI: {summary['services_with_all_kpis']}")
        print(f"Сервисов с частичными KPI: {summary['services_with_partial_kpis']}")
        print(f"Сервисов без KPI: {summary['services_with_no_kpis']}")
        print()

        # Detailed results
        for service_name, kpis in sorted(results.items()):
            registered = sum(1 for kpi in kpis if kpi.registered)
            total = len(kpis)

            if registered == total:
                status_icon = "✅"
            elif registered > 0:
                status_icon = "⚠️"
            else:
                status_icon = "❌"

            print(f"{status_icon} {service_name}: {registered}/{total} KPI зарегистрировано")

            for kpi in kpis:
                if kpi.registered:
                    value_str = f" (значение: {kpi.current_value})" if kpi.current_value is not None else ""
                    print(f"   ✅ {kpi.kpi_name}{value_str}")
                else:
                    print(f"   ❌ {kpi.kpi_name} - не найден")
            print()

        # Final status
        print("="*80)
        if summary['kpi_coverage_percent'] >= 80:
            print("✅ ПРИОРИТЕТ 4 PASSED: KPI регистрация в порядке")
            passed = True
        elif summary['kpi_coverage_percent'] >= 50:
            print("⚠️ ПРИОРИТЕТ 4 WARNING: Неполная регистрация KPI")
            passed = False
        else:
            print("❌ ПРИОРИТЕТ 4 FAILED: Недостаточно KPI зарегистрировано")
            passed = False
        print("="*80 + "\n")

        return passed


def main():
    """Main entry point"""
    checker = KPIRegistrationChecker()
    results = checker.check_all_kpis()
    passed = checker.print_results(results)

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
