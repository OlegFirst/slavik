#!/usr/bin/env python3
"""
ПРИОРИТЕТ 6: Проверка Контроля Оркестратором

Проверяет, что каждый сервис:
1. Зарегистрирован в Service Registry
2. Управляется оркестратором (docker-compose/kubernetes)
3. Оркестратор знает о статусе сервиса
4. Настроены health checks
5. Настроена restart policy

Этот приоритет выполняется ПОСЛЕ всех предыдущих:
- Priority 1: Port Conflicts
- Priority 2: Metrics Integration
- Priority 3: Database Connections
- Priority 4: KPI Registration
- Priority 5: EventBus Events

Created: 2025-10-09
Status:  Implemented
"""

import sys
import logging
import subprocess
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrchestratorSeverity(Enum):
    """Серьезность проблемы с оркестратором"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ServiceOrchestratorStatus:
    """Статус контроля оркестратором"""
    service_name: str
    port: Optional[int] = None
    registered_in_registry: bool = False  # Зарегистрирован в Service Registry
    managed_by_orchestrator: bool = False  # Управляется оркестратором
    orchestrator_type: Optional[str] = None  # docker-compose, kubernetes, systemd
    container_id: Optional[str] = None  # ID контейнера/pod
    container_status: Optional[str] = None  # running, stopped, etc.
    has_health_check: bool = False  # Настроен health check
    health_check_status: Optional[str] = None  # healthy, unhealthy
    has_restart_policy: bool = False  # Настроена restart policy
    restart_policy: Optional[str] = None  # always, on-failure, unless-stopped
    restart_count: int = 0  # Количество перезапусков
    uptime: Optional[str] = None  # Время работы
    severity: OrchestratorSeverity = OrchestratorSeverity.INFO
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


# Ожидаемые сервисы и их порты
EXPECTED_SERVICES = {
    # Platform Services
    'planning-service': {'port': 8011, 'critical': True},
    'plans-service': {'port': 8023, 'critical': True},
    'bia-service': {'port': 8012, 'critical': True},
    'risk-service': {'port': 8013, 'critical': True},
    'response-service': {'port': 8014, 'critical': True},
    'compliance-service': {'port': 8015, 'critical': True},
    'governance-service': {'port': 8016, 'critical': True},
    'documents-service': {'port': 8017, 'critical': True},
    'validation-service': {'port': 8018, 'critical': True},
    'learning-service': {'port': 8019, 'critical': False},
    'community-service': {'port': 8020, 'critical': False},
    'bcm-coordination-service': {'port': 8021, 'critical': True},

    # Intelligent Core
    'workflow-intelligence': {'port': 9001, 'critical': True},
    'event-intelligence': {'port': 9002, 'critical': True},
    'expertise-center': {'port': 9003, 'critical': True},
    'community-intelligence': {'port': 9004, 'critical': False},
    'ai-workflow-optimizer': {'port': 9005, 'critical': False},

    # Infrastructure
    'eventbus': {'port': 8001, 'critical': True},
    'monitoring': {'port': 6002, 'critical': True},
    'notification-service': {'port': 6003, 'critical': False},
}


class OrchestratorControlChecker:
    """Проверка контроля оркестратором"""

    def __init__(self):
        self.registry_path = Path("/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-discovery")

    def check_service_registry_available(self) -> bool:
        """Проверить доступность Service Registry"""
        try:
            sys.path.insert(0, str(self.registry_path.parent.parent))
            from runtime.service_discovery import ServiceRegistry
            return True
        except Exception as e:
            logger.warning(f"Service Registry unavailable: {e}")
            return False

    def check_service_in_registry(self, service_name: str) -> Dict[str, Any]:
        """
        Проверить, зарегистрирован ли сервис в Service Registry

        В production здесь был бы реальный запрос к Registry через Redis/API
        """
        # Placeholder: В реальной системе здесь запрос к Service Registry
        return {
            'registered': False,
            'status': 'unknown',
            'orchestrator': None
        }

    def get_docker_containers(self) -> List[Dict[str, Any]]:
        """Получить список Docker контейнеров"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.warning("Docker not available or not running")
                return []

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container = json.loads(line)
                        containers.append(container)
                    except json.JSONDecodeError:
                        pass

            return containers

        except FileNotFoundError:
            logger.warning("Docker command not found")
            return []
        except Exception as e:
            logger.error(f"Failed to get Docker containers: {e}")
            return []

    def get_docker_container_info(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Получить детальную информацию о контейнере"""
        try:
            result = subprocess.run(
                ['docker', 'inspect', container_id],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data:
                    return data[0]

        except Exception as e:
            logger.debug(f"Failed to inspect container {container_id}: {e}")

        return None

    def find_service_container(self, service_name: str,
                              containers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Найти контейнер сервиса по имени"""
        # Try exact match first
        for container in containers:
            names = container.get('Names', '')
            if service_name in names:
                return container

        # Try fuzzy match
        service_key = service_name.replace('-', '_').replace('_', '')
        for container in containers:
            names = container.get('Names', '').replace('-', '').replace('_', '')
            if service_key in names.lower():
                return container

        return None

    def check_service_orchestrator_status(self, service_name: str,
                                         config: Dict[str, Any]) -> ServiceOrchestratorStatus:
        """Проверить статус контроля оркестратором для сервиса"""
        status = ServiceOrchestratorStatus(
            service_name=service_name,
            port=config.get('port')
        )

        # Check Service Registry
        registry_info = self.check_service_in_registry(service_name)
        status.registered_in_registry = registry_info.get('registered', False)

        # Check Docker containers
        containers = self.get_docker_containers()
        container = self.find_service_container(service_name, containers)

        if container:
            status.managed_by_orchestrator = True
            status.orchestrator_type = "docker"
            status.container_id = container.get('ID', '')[:12]
            status.container_status = container.get('State', 'unknown')
            status.uptime = container.get('Status', 'unknown')

            # Get detailed container info
            container_info = self.get_docker_container_info(status.container_id)
            if container_info:
                # Check health check
                health_config = container_info.get('Config', {}).get('Healthcheck')
                status.has_health_check = health_config is not None

                if status.has_health_check:
                    health = container_info.get('State', {}).get('Health', {})
                    status.health_check_status = health.get('Status', 'unknown')

                # Check restart policy
                restart_policy = container_info.get('HostConfig', {}).get('RestartPolicy', {})
                policy_name = restart_policy.get('Name', 'no')
                status.has_restart_policy = policy_name != 'no'
                status.restart_policy = policy_name

                # Get restart count
                status.restart_count = container_info.get('RestartCount', 0)
        else:
            status.managed_by_orchestrator = False
            status.orchestrator_type = None

        # Determine severity and message
        is_critical = config.get('critical', False)

        if not status.registered_in_registry and not status.managed_by_orchestrator:
            status.severity = OrchestratorSeverity.CRITICAL if is_critical else OrchestratorSeverity.ERROR
            status.message = " Не зарегистрирован И не управляется оркестратором!"
        elif not status.registered_in_registry:
            status.severity = OrchestratorSeverity.WARNING
            status.message = "️ Не зарегистрирован в Service Registry"
        elif not status.managed_by_orchestrator:
            status.severity = OrchestratorSeverity.WARNING
            status.message = "️ Не управляется оркестратором"
        elif not status.has_health_check:
            status.severity = OrchestratorSeverity.WARNING
            status.message = "️ Нет health check"
        elif not status.has_restart_policy:
            status.severity = OrchestratorSeverity.WARNING
            status.message = "️ Нет restart policy"
        elif status.container_status != 'running':
            status.severity = OrchestratorSeverity.ERROR
            status.message = f" Контейнер не running (статус: {status.container_status})"
        elif status.health_check_status == 'unhealthy':
            status.severity = OrchestratorSeverity.ERROR
            status.message = " Health check: unhealthy"
        elif status.restart_count > 10:
            status.severity = OrchestratorSeverity.WARNING
            status.message = f"️ Много перезапусков ({status.restart_count})"
        else:
            status.severity = OrchestratorSeverity.INFO
            status.message = " Полный контроль оркестратором"

        return status

    def check_all_services(self) -> Dict[str, ServiceOrchestratorStatus]:
        """Проверить все сервисы"""
        logger.info("Checking orchestrator control for all services...")

        results = {}

        for service_name, config in EXPECTED_SERVICES.items():
            status = self.check_service_orchestrator_status(service_name, config)
            results[service_name] = status

        return results

    def generate_summary(self, results: Dict[str, ServiceOrchestratorStatus]) -> Dict[str, Any]:
        """Сгенерировать сводку"""
        total_services = len(results)

        registered_services = sum(1 for s in results.values() if s.registered_in_registry)
        managed_services = sum(1 for s in results.values() if s.managed_by_orchestrator)
        with_health_check = sum(1 for s in results.values() if s.has_health_check)
        with_restart_policy = sum(1 for s in results.values() if s.has_restart_policy)

        fully_controlled = sum(
            1 for s in results.values()
            if s.managed_by_orchestrator and s.has_health_check and s.has_restart_policy
        )

        critical_issues = [
            s.service_name for s in results.values()
            if s.severity == OrchestratorSeverity.CRITICAL
        ]

        return {
            'total_services': total_services,
            'registered_services': registered_services,
            'managed_services': managed_services,
            'with_health_check': with_health_check,
            'with_restart_policy': with_restart_policy,
            'fully_controlled': fully_controlled,
            'control_rate': (fully_controlled / total_services * 100) if total_services > 0 else 0,
            'critical_issues': critical_issues,
            'critical_count': len(critical_issues)
        }

    def print_results(self, results: Dict[str, ServiceOrchestratorStatus]):
        """Вывести результаты проверки"""
        print("\n" + "="*80)
        print("ПРИОРИТЕТ 6: Проверка контроля оркестратором")
        print("="*80 + "\n")

        summary = self.generate_summary(results)

        print(f"Всего сервисов: {summary['total_services']}")
        print(f"Зарегистрировано в Registry: {summary['registered_services']}")
        print(f"Управляется оркестратором: {summary['managed_services']}")
        print(f"С health check: {summary['with_health_check']}")
        print(f"С restart policy: {summary['with_restart_policy']}")
        print(f"Полный контроль: {summary['fully_controlled']} ({summary['control_rate']:.1f}%)")
        print()

        # КРИТИЧНЫЕ ПРОБЛЕМЫ
        if summary['critical_count'] > 0:
            print(" КРИТИЧНЫЕ ПРОБЛЕМЫ ")
            print(f"Найдено {summary['critical_count']} критичных сервисов без контроля:")
            for service_name in summary['critical_issues']:
                print(f"   {service_name}")
            print()

        # Detailed results
        for service_name, status in sorted(results.items()):
            icon = "" if status.severity == OrchestratorSeverity.INFO else \
                   "️" if status.severity == OrchestratorSeverity.WARNING else \
                   "" if status.severity == OrchestratorSeverity.ERROR else ""

            print(f"{icon} {service_name}")
            print(f"   Зарегистрирован в Registry: {'' if status.registered_in_registry else ''}")
            print(f"   Управляется оркестратором: {'' if status.managed_by_orchestrator else ''}")

            if status.managed_by_orchestrator:
                print(f"   Тип: {status.orchestrator_type}")
                print(f"   Container ID: {status.container_id}")
                print(f"   Статус: {status.container_status}")
                print(f"   Health check: {'' if status.has_health_check else ''}")
                if status.has_health_check:
                    print(f"   Health status: {status.health_check_status}")
                print(f"   Restart policy: {'' if status.has_restart_policy else ''}")
                if status.has_restart_policy:
                    print(f"   Policy: {status.restart_policy}")
                print(f"   Restart count: {status.restart_count}")
                print(f"   Uptime: {status.uptime}")

            print(f"   {status.message}")
            print()

        # Final status
        print("="*80)
        if summary['critical_count'] > 0:
            print(" ПРИОРИТЕТ 6 CRITICAL: Критичные сервисы без контроля оркестратором!")
            passed = False
        elif summary['control_rate'] >= 80:
            print(" ПРИОРИТЕТ 6 PASSED: Контроль оркестратором в порядке")
            passed = True
        elif summary['control_rate'] >= 50:
            print("️ ПРИОРИТЕТ 6 WARNING: Неполный контроль оркестратором")
            passed = False
        else:
            print(" ПРИОРИТЕТ 6 FAILED: Недостаточный контроль оркестратором")
            passed = False
        print("="*80 + "\n")

        return passed


def main():
    """Main entry point"""
    checker = OrchestratorControlChecker()
    results = checker.check_all_services()
    passed = checker.print_results(results)

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
